#!/usr/bin/env python3
"""
Fix code blocks without language tags

Detects language from content and adds appropriate Obsidian/Prism.js tags:
- cpp: C++/OpenFOAM code
- python: Python scripts
- bash: Shell commands
- cmake: CMake files
- text: Default (diagrams, tables, etc.)

Usage:
    python3 .claude/scripts/fix_code_blocks.py --file daily_learning/Phase_01_Foundation_Theory/01.md
    python3 .claude/scripts/fix_code_blocks.py --directory daily_learning/ --dry-run
"""

import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple


class CodeBlockFixer:
    """Fix code blocks without language tags"""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.fixes_made = 0
        self.files_modified = 0

    def detect_language(self, content: str) -> str:
        """
        Detect language from code content.

        Returns: language identifier for Obsidian/Prism.js
        """
        content_stripped = content.strip()

        # Check for empty or very short content
        if not content_stripped or len(content_stripped) < 20:
            return None

        # Skip if it's mostly text/prose (has lots of spaces, Thai/Unicode text)
        # Check if it looks like prose (lots of words without code-like patterns)
        words = content_stripped.split()
        if len(words) < 3:
            return None  # Too short to be code

        # Check for Thai characters (prose)
        if re.search(r'[\u0E00-\u0E7F]', content_stripped):
            # Has Thai text - likely prose, not code
            # Unless it has clear code patterns
            if not any(pattern in content_stripped for pattern in ['{', '}', ';', '()', '==', '->']):
                return None

        # Skip if it's markdown formatting (headers, lists, etc)
        if content_stripped.startswith('#') or content_stripped.startswith('|') or content_stripped.startswith('-'):
            return None

        # C++ / OpenFOAM patterns (must have multiple indicators)
        cpp_indicators = 0
        cpp_patterns = [
            (r'\b(fvScalarMatrix|volScalarField|volVectorField|surfaceScalarField)\b', 2),
            (r'\b(fvc::|fvm::|fvm::ddt|fvc::div|fvc::grad)\b', 2),
            (r'\bInfo\s*<<\s*endl\b', 1),
            (r'#include\s*[<"]\w+', 1),
            (r'\{\s*\n', 1),  # Opening brace on newline
            (r'\n\s*\}\s*;', 2),  # Closing brace with semicolon
            (r'//.*$', 1),  # C++ comments
            (r'for\s*\([^)]*\)', 1),  # for loops
        ]

        for pattern, weight in cpp_patterns:
            if re.search(pattern, content_stripped, re.MULTILINE):
                cpp_indicators += weight

        if cpp_indicators >= 3:
            return 'cpp'

        # Python patterns (must have multiple indicators)
        python_indicators = 0
        python_patterns = [
            (r'\bdef\s+\w+\s*\([^)]*\)\s*:', 2),  # Function definition
            (r'\bclass\s+\w+\s*:', 1),  # Class definition
            (r'\bimport\s+\w+', 1),
            (r'\bfrom\s+\w+\s+import', 1),
            (r'\bprint\s*\(', 1),
            (r'#!/usr/bin/env python', 3),
            (r'\w+\s*=\s*\w+\s*\(.*\)', 1),  # Assignment with function call
        ]

        for pattern, weight in python_patterns:
            if re.search(pattern, content_stripped):
                python_indicators += weight

        if python_indicators >= 2:
            return 'python'

        # Bash patterns (must have multiple indicators)
        bash_indicators = 0
        bash_patterns = [
            (r'\bnpm\s+(install|update|run)\b', 2),
            (r'\bgit\s+(clone|checkout|commit|add|push)\b', 2),
            (r'\bpip\s+install\b', 1),
            (r'\b(cpio|mkdir|cp|mv|ls|cd|rm)\s+-', 1),
            (r'#!/bin/(bash|sh)', 3),
            (r'\$\{?\w+\}?', 1),  # Variables
            (r'^\s*\w+\s+=', 1),  # Assignment
        ]

        for pattern, weight in bash_patterns:
            if re.search(pattern, content_stripped, re.MULTILINE):
                bash_indicators += weight

        if bash_indicators >= 2:
            return 'bash'

        # CMake patterns
        cmake_indicators = 0
        cmake_patterns = [
            (r'\badd_library\b', 2),
            (r'\badd_executable\b', 2),
            (r'\btarget_link_libraries\b', 1),
            (r'\btarget_include_directories\b', 1),
            (r'CMakeLists\.txt', 2),
            (r'project\s*\(', 1),
        ]

        for pattern, weight in cmake_patterns:
            if re.search(pattern, content_stripped, re.MULTILINE):
                cmake_indicators += weight

        if cmake_indicators >= 2:
            return 'cmake'

        # Default: don't tag (text/diagrams/tables)
        return None

    def fix_file(self, file_path: Path) -> int:
        """Fix code blocks in a single file.

        Returns: number of fixes made
        """
        try:
            content = file_path.read_text()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return 0

        lines = content.split('\n')
        fixed_lines = []
        fixes = 0
        i = 0

        while i < len(lines):
            line = lines[i]

            # Check for code block opening with no language
            if line.strip() == '```' and (i == 0 or not lines[i-1].strip().startswith('```')):
                # Get the content
                content_lines = []
                j = i + 1
                while j < len(lines) and not lines[j].strip().startswith('```'):
                    content_lines.append(lines[j])
                    j += 1

                block_content = '\n'.join(content_lines).strip()

                # Detect language
                detected_lang = self.detect_language(block_content)

                if detected_lang and detected_lang != 'text':
                    # Add language tag
                    fixed_lines.append(f'```{detected_lang}')
                    fixes += 1
                    if self.dry_run:
                        print(f"  Would fix line {i+1}: ``` → ```{detected_lang}")
                        print(f"    Preview: {block_content[:60]}...")
                else:
                    # Keep as-is (empty block or text/diagram)
                    fixed_lines.append(line)

                # Add content
                fixed_lines.extend(content_lines)

                # Find closing ```
                if j < len(lines):
                    fixed_lines.append(lines[j])
                    i = j + 1
                else:
                    i = j
            else:
                fixed_lines.append(line)
                i += 1

        if fixes > 0 and not self.dry_run:
            file_path.write_text('\n'.join(fixed_lines))
            self.files_modified += 1

        return fixes

    def fix_directory(self, directory: Path, pattern: str = "*.md") -> Dict:
        """Fix all markdown files in directory.

        Returns: summary dict
        """
        results = {
            'files_checked': 0,
            'files_modified': 0,
            'total_fixes': 0,
            'by_language': {}
        }

        for md_file in directory.rglob(pattern):
            results['files_checked'] += 1
            fixes = self.fix_file(md_file)
            results['total_fixes'] += fixes

        results['files_modified'] = self.files_modified

        return results


def main():
    parser = argparse.ArgumentParser(
        description="Fix code blocks without language tags for Obsidian"
    )
    parser.add_argument('--file', type=Path, help='Fix single file')
    parser.add_argument('--directory', type=Path, help='Fix all .md files in directory')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be fixed without making changes')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    fixer = CodeBlockFixer(dry_run=args.dry_run)

    if args.file:
        print(f"Fixing {args.file}")
        fixes = fixer.fix_file(args.file)
        print(f"Made {fixes} fixes")

        if not args.dry_run and fixes > 0:
            print(f"✅ Fixed {args.file}")

    elif args.directory:
        print(f"Scanning {args.directory}...")
        results = fixer.fix_directory(args.directory)

        print(f"\n{'='*60}")
        print(f"Files checked: {results['files_checked']}")
        if args.dry_run:
            print(f"Would modify: {results['files_modified']} files")
        else:
            print(f"Files modified: {results['files_modified']}")
        print(f"Total fixes: {results['total_fixes']}")
        print(f"{'='*60}")

        if not args.dry_run and results['total_fixes'] > 0:
            print(f"\n✅ Fixed {results['files_modified']} files")


if __name__ == '__main__':
    main()
