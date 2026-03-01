#!/usr/bin/env python3
"""
Verify Code Blocks — Extract and compile C++ code from markdown files.

Extracts fenced ```cpp blocks from .md files, groups them into compilable
units based on filename hints, and verifies compilation using g++.

Usage:
    python3 verify_code_blocks.py --file Day_01.md
    python3 verify_code_blocks.py --dir Phase_01_CppThroughOpenFOAM/
    python3 verify_code_blocks.py --file Day_01.md --verbose
    python3 verify_code_blocks.py --dir Phase_01/ --json
"""

import re
import os
import sys
import json
import shutil
import tempfile
import subprocess
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field, asdict


# ── Data structures ──────────────────────────────────────────────────────

@dataclass
class CodeBlock:
    """A single fenced code block extracted from markdown."""
    content: str
    language: str
    start_line: int
    end_line: int
    filename_hint: Optional[str] = None
    is_example_only: bool = False  # Blocks not meant to compile


@dataclass
class CompilableUnit:
    """A group of related code blocks forming a compilable program."""
    name: str
    headers: Dict[str, CodeBlock] = field(default_factory=dict)
    sources: Dict[str, CodeBlock] = field(default_factory=dict)
    snippets: List[CodeBlock] = field(default_factory=list)


@dataclass
class CompileResult:
    """Result of compiling a single unit."""
    unit_name: str
    filename: str
    passed: bool
    md_start_line: int
    md_end_line: int
    compiler_output: str = ""
    error_summary: str = ""


# ── Extraction ───────────────────────────────────────────────────────────

# Patterns that identify STUDENT code (should compile)
STUDENT_CODE_PATTERNS = [
    # "Create file `my_field.H`:" or "Create file my_field.H:"
    re.compile(r'[Cc]reate\s+file\s+[`"]?([^\s`":]+\.[HCh])[`"]?\s*:', re.IGNORECASE),
    # "Add to file `mini_field/expressions.H`:"
    re.compile(r'[Aa]dd\s+to\s+file\s+[`"]?([^\s`":]+\.[HCh])[`"]?\s*:', re.IGNORECASE),
    # "### my_field.H" or "### test_field.C" (standalone section titles)
    re.compile(r'^###\s+([\w]+\.[HCh])\s*$', re.MULTILINE),
]

# Patterns that identify OpenFOAM SOURCE SNIPPETS (skip — not compilable)
OPENFOAM_SOURCE_PATTERNS = [
    # "// File: src/OpenFOAM/.../Field.H" — OpenFOAM internal source
    re.compile(r'//\s*[Ff]ile:\s*(src/[^\s]+\.[HCh])'),
    # "// File: src/.../limitedSchemes/..." — OpenFOAM path with directories
    re.compile(r'//\s*[Ff]ile:\s*([^\s]+/[^\s]+/[^\s]+\.[HCh])'),
]

# Markers inside code that indicate the block is an example/not compilable
SKIP_MARKERS = [
    '// ❌',       # Intentional bad example
    '// BAD:',     # Intentional bad example
    '❌ BAD',      # Bad example in comment
    '(simplified)',  # Simplified OpenFOAM source
]

# Strong indicators: any one of these means it's definitely OpenFOAM source
OPENFOAM_STRONG_INDICATORS = [
    'Foam::label', 'Foam::',
    'tmp<Field<Type>>::refCount',
    'volScalarField', 'volVectorField', 'surfaceVectorField',
    'fvMesh', 'fvc::', 'fvm::',
    'typeOfSum<',
]

# Weak indicators: only count if multiple present (student code may define one)
OPENFOAM_WEAK_INDICATORS = [
    'forAll(',       # Student code may #define forAll
    'label ',        # Might be used as variable name in student code
    'scalar ',       # Might appear in comments
]


def is_openfoam_snippet(block_content: str, filename_hint: str = None) -> bool:
    """Detect if a code block is an OpenFOAM source reading snippet."""
    # Check for strong indicators — any one match is enough
    for indicator in OPENFOAM_STRONG_INDICATORS:
        if indicator in block_content:
            return True

    # Check for weak indicators — need 2+ to classify as OpenFOAM
    # BUT: if forAll appears as #define, it's student code reimplementing it
    weak_count = 0
    for indicator in OPENFOAM_WEAK_INDICATORS:
        if indicator in block_content:
            # Special case: #define forAll is student code, not OpenFOAM usage
            if indicator == 'forAll(' and '#define forAll' in block_content:
                continue
            weak_count += 1
    if weak_count >= 2:
        return True

    # Check for OpenFOAM source path in first 3 lines
    first_lines = '\n'.join(block_content.split('\n')[:3])
    for pattern in OPENFOAM_SOURCE_PATTERNS:
        if pattern.search(first_lines):
            return True

    # Check for '(simplified)' annotation
    if '(simplified)' in first_lines.lower():
        return True

    # If the filename hint looks like an OpenFOAM path (has src/ or deep nesting)
    if filename_hint and ('/' in filename_hint and filename_hint.count('/') >= 2):
        return True

    return False


def extract_code_blocks(content: str) -> List[CodeBlock]:
    """Extract all fenced code blocks from markdown content."""
    blocks = []
    lines = content.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]
        # Match opening fence: ```cpp, ```c++, ```C++
        match = re.match(r'^```(cpp|c\+\+|C\+\+)\s*$', line.strip())
        if match:
            lang = match.group(1)
            start = i + 1  # 0-indexed line after the opening fence
            md_start = i + 1  # 1-indexed for reporting

            # Find closing fence
            j = i + 1
            block_lines = []
            while j < len(lines):
                if lines[j].strip() == '```':
                    break
                block_lines.append(lines[j])
                j += 1

            md_end = j + 1  # 1-indexed
            block_content = '\n'.join(block_lines)

            # Check if this is an example-only block
            is_example = False
            for marker in SKIP_MARKERS:
                if marker in block_content:
                    is_example = True
                    break

            # Check if inside a blockquote
            if i > 0 and lines[i-1].strip().startswith('>'):
                is_example = True

            # Look for filename hint in preceding lines (up to 5 lines before)
            filename_hint = None
            for lookback in range(1, min(6, i + 1)):
                prev_line = lines[i - lookback]
                for pattern in STUDENT_CODE_PATTERNS:
                    hint_match = pattern.search(prev_line)
                    if hint_match:
                        filename_hint = hint_match.group(1)
                        # Normalize: take just the basename
                        filename_hint = os.path.basename(filename_hint)
                        break
                if filename_hint:
                    break

            # Also check first line of the code block for OpenFOAM source hints
            if not filename_hint and block_lines:
                for pattern in OPENFOAM_SOURCE_PATTERNS:
                    hint_match = pattern.search(block_lines[0])
                    if hint_match:
                        # This is an OpenFOAM source snippet — mark as example
                        is_example = True
                        break

            # Detect OpenFOAM snippets by content analysis
            if not is_example and is_openfoam_snippet(block_content, filename_hint):
                is_example = True

            blocks.append(CodeBlock(
                content=block_content,
                language=lang,
                start_line=md_start,
                end_line=md_end,
                filename_hint=filename_hint,
                is_example_only=is_example,
            ))
            i = j + 1
        else:
            i += 1

    return blocks


def group_into_units(blocks: List[CodeBlock]) -> List[CompilableUnit]:
    """Group code blocks into compilable units based on filename hints."""
    # Separate into named files and unnamed snippets
    named_blocks: Dict[str, CodeBlock] = {}
    unnamed_blocks: List[CodeBlock] = []

    for block in blocks:
        if block.is_example_only:
            continue

        if block.filename_hint:
            # Use last occurrence if duplicate filename
            named_blocks[block.filename_hint] = block
        else:
            unnamed_blocks.append(block)

    # Build compilable units from named blocks
    # Each .C file + its #include'd .H files = one unit
    units = []
    headers = {}
    sources = {}

    for name, block in named_blocks.items():
        if name.endswith('.H') or name.endswith('.h'):
            headers[name] = block
        elif name.endswith('.C') or name.endswith('.c') or name.endswith('.cpp'):
            sources[name] = block

    # For each source file, create a unit with its dependencies
    for src_name, src_block in sources.items():
        unit = CompilableUnit(name=src_name)
        unit.sources[src_name] = src_block

        # Find #include'd local headers
        for inc_match in re.finditer(r'#include\s+"([^"]+)"', src_block.content):
            inc_name = os.path.basename(inc_match.group(1))
            if inc_name in headers:
                unit.headers[inc_name] = headers[inc_name]

        units.append(unit)

    # Headers without a source file — compile with -fsyntax-only
    standalone_headers = {
        name: block for name, block in headers.items()
        if not any(name in u.headers for u in units)
    }
    if standalone_headers:
        unit = CompilableUnit(name="standalone_headers")
        unit.headers = standalone_headers
        units.append(unit)

    return units


# ── Compilation ──────────────────────────────────────────────────────────

def compile_unit(unit: CompilableUnit, verbose: bool = False) -> List[CompileResult]:
    """Compile a unit and return results."""
    results = []
    tmpdir = tempfile.mkdtemp(prefix="verify_cpp_")

    try:
        # Write all headers to tmpdir
        for name, block in unit.headers.items():
            filepath = os.path.join(tmpdir, name)
            with open(filepath, 'w') as f:
                f.write(block.content + '\n')

        # Compile each source file
        for name, block in unit.sources.items():
            filepath = os.path.join(tmpdir, name)
            with open(filepath, 'w') as f:
                f.write(block.content + '\n')

            # Check if it has main() — full compile, otherwise syntax-only
            has_main = 'int main(' in block.content or 'int main ()' in block.content
            cmd = ['g++', '-std=c++11', '-Wall', '-Wextra']

            if has_main:
                # Full compile + link
                output_path = os.path.join(tmpdir, name.replace('.C', '').replace('.cpp', ''))
                cmd += [filepath, '-o', output_path]
            else:
                cmd += ['-fsyntax-only', filepath]

            # Add include path
            cmd += ['-I', tmpdir]

            if verbose:
                print(f"  $ {' '.join(cmd)}")

            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            passed = proc.returncode == 0
            error_output = proc.stderr.strip()

            # Clean up error paths for readability
            error_output = error_output.replace(tmpdir + '/', '')

            # Extract first error line for summary
            error_summary = ""
            if not passed and error_output:
                first_error = next(
                    (l for l in error_output.split('\n') if 'error:' in l),
                    error_output.split('\n')[0]
                )
                error_summary = first_error.strip()

            results.append(CompileResult(
                unit_name=unit.name,
                filename=name,
                passed=passed,
                md_start_line=block.start_line,
                md_end_line=block.end_line,
                compiler_output=error_output,
                error_summary=error_summary,
            ))

        # For standalone headers, syntax-check each one
        if not unit.sources and unit.headers:
            for name, block in unit.headers.items():
                filepath = os.path.join(tmpdir, name)

                # Create a trivial .C that includes the header
                test_src = f'#include "{name}"\n'
                test_path = os.path.join(tmpdir, f'_test_{name}.C')
                with open(test_path, 'w') as f:
                    f.write(test_src)

                cmd = ['g++', '-std=c++11', '-Wall', '-Wextra',
                       '-fsyntax-only', test_path, '-I', tmpdir]

                if verbose:
                    print(f"  $ {' '.join(cmd)}")

                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

                passed = proc.returncode == 0
                error_output = proc.stderr.strip().replace(tmpdir + '/', '')

                error_summary = ""
                if not passed and error_output:
                    first_error = next(
                        (l for l in error_output.split('\n') if 'error:' in l),
                        error_output.split('\n')[0]
                    )
                    error_summary = first_error.strip()

                results.append(CompileResult(
                    unit_name=unit.name,
                    filename=name,
                    passed=passed,
                    md_start_line=block.start_line,
                    md_end_line=block.end_line,
                    compiler_output=error_output,
                    error_summary=error_summary,
                ))
    except subprocess.TimeoutExpired:
        results.append(CompileResult(
            unit_name=unit.name,
            filename="(timeout)",
            passed=False,
            md_start_line=0,
            md_end_line=0,
            error_summary="Compilation timed out (30s)",
        ))
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    return results


# ── Reporting ────────────────────────────────────────────────────────────

def verify_file(file_path: Path, verbose: bool = False) -> Dict:
    """Verify all C++ code blocks in a markdown file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    blocks = extract_code_blocks(content)
    compilable = [b for b in blocks if not b.is_example_only]
    units = group_into_units(blocks)

    all_results = []
    for unit in units:
        results = compile_unit(unit, verbose=verbose)
        all_results.extend(results)

    passed = all(r.passed for r in all_results) if all_results else True
    failures = [r for r in all_results if not r.passed]

    return {
        'file': str(file_path),
        'total_blocks': len(blocks),
        'compilable_blocks': len(compilable),
        'example_only_blocks': len(blocks) - len(compilable),
        'units': len(units),
        'results': all_results,
        'passed': passed,
        'failures': failures,
    }


def print_file_report(report: Dict, verbose: bool = False):
    """Print a human-readable report for a single file."""
    filename = os.path.basename(report['file'])
    status = "✅ PASS" if report['passed'] else "❌ FAIL"

    print(f"\n{'='*60}")
    print(f"  {status}  {filename}")
    print(f"  Blocks: {report['total_blocks']} total, "
          f"{report['compilable_blocks']} compilable, "
          f"{report['example_only_blocks']} skipped")
    print(f"  Units: {report['units']}")
    print(f"{'='*60}")

    if verbose or not report['passed']:
        for result in report['results']:
            icon = "✅" if result.passed else "❌"
            print(f"  {icon} {result.filename} (md lines {result.md_start_line}-{result.md_end_line})")

            if not result.passed and result.compiler_output:
                for line in result.compiler_output.split('\n')[:5]:
                    print(f"     {line}")
                total_lines = len(result.compiler_output.split('\n'))
                if total_lines > 5:
                    print(f"     ... ({total_lines - 5} more lines)")

    if report['failures']:
        print(f"\n  ⚠️  {len(report['failures'])} compilation failure(s):")
        for f in report['failures']:
            print(f"     • {f.filename} (line {f.md_start_line}): {f.error_summary}")


def print_summary(reports: List[Dict]):
    """Print overall summary for multiple files."""
    total = len(reports)
    passed = sum(1 for r in reports if r['passed'])
    failed = total - passed

    print(f"\n{'='*60}")
    print(f"  SUMMARY: {passed}/{total} files passed")
    if failed > 0:
        print(f"  ❌ {failed} file(s) with compilation errors:")
        for r in reports:
            if not r['passed']:
                fname = os.path.basename(r['file'])
                errors = len(r['failures'])
                print(f"     • {fname}: {errors} error(s)")
    else:
        print(f"  ✅ All files compile successfully!")
    print(f"{'='*60}\n")


# ── Main ─────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Verify C++ code blocks in markdown files compile correctly",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Verify a single file
  python3 verify_code_blocks.py --file daily_learning/Phase_01/01.md

  # Verify all .md files in a directory
  python3 verify_code_blocks.py --dir daily_learning/Phase_01/

  # Verbose output (show compiler commands)
  python3 verify_code_blocks.py --file 01.md --verbose

  # JSON output for machine consumption
  python3 verify_code_blocks.py --dir Phase_01/ --json
        """
    )
    parser.add_argument("--file", type=Path, help="Path to a single markdown file")
    parser.add_argument("--dir", type=Path, help="Path to a directory of markdown files")
    parser.add_argument("--verbose", action="store_true", help="Show compiler commands and all results")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    if not args.file and not args.dir:
        parser.error("Either --file or --dir is required")

    # Check g++ is available
    try:
        subprocess.run(['g++', '--version'], capture_output=True, timeout=5)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print("❌ Error: g++ not found. Please install a C++ compiler.")
        sys.exit(1)

    # Collect files
    files = []
    if args.file:
        if not args.file.exists():
            print(f"❌ Error: File not found: {args.file}")
            sys.exit(1)
        files.append(args.file)
    elif args.dir:
        if not args.dir.exists():
            print(f"❌ Error: Directory not found: {args.dir}")
            sys.exit(1)
        files = sorted(args.dir.glob("*.md"))
        if not files:
            print(f"⚠️ No .md files found in: {args.dir}")
            sys.exit(0)

    print(f"🔍 Verifying C++ code blocks in {len(files)} file(s)...\n")

    reports = []
    for file_path in files:
        if args.verbose:
            print(f"Processing: {file_path}")

        report = verify_file(file_path, verbose=args.verbose)
        reports.append(report)

        if not args.json:
            print_file_report(report, verbose=args.verbose)

    if args.json:
        # JSON output
        json_output = []
        for r in reports:
            json_report = {
                'file': r['file'],
                'passed': r['passed'],
                'total_blocks': r['total_blocks'],
                'compilable_blocks': r['compilable_blocks'],
                'units': r['units'],
                'failures': [
                    {
                        'filename': f.filename,
                        'md_line': f.md_start_line,
                        'error': f.error_summary,
                    }
                    for f in r['failures']
                ]
            }
            json_output.append(json_report)
        print(json.dumps(json_output, indent=2))
    else:
        if len(reports) > 1:
            print_summary(reports)

    # Exit with failure if any file failed
    all_passed = all(r['passed'] for r in reports)
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
