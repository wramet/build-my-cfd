#!/usr/bin/env python3
"""
Enhanced Obsidian QC Script

Validates markdown files for Obsidian-specific rendering requirements.
- Code block structure validation
- Non-breaking space detection
- Mermaid syntax checking
- C++ syntax validation

Usage:
    python3 enhanced_obsidian_qc.py --file daily_learning/Phase_01_Foundation_Theory/Day_01.md
    python3 enhanced_obsidian_qc.py --file Day_01.md --fix  # Auto-fix non-breaking spaces
    python3 enhanced_obsidian_qc.py --file Day_01.md --verbose
"""

import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple


class EnhancedObsidianQC:
    """Enhanced validator for Obsidian markdown rendering"""

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.fixes = []

    def validate_code_blocks(self, content: str) -> List[Dict]:
        """
        Validate code block structure and language tags.

        Checks:
        - Every code block has opening ``` with language tag
        - Every code block has closing ```
        - No orphaned code snippets
        """
        issues = []
        lines = content.split('\n')

        in_code_block = False
        block_start_line = 0
        lang_tag = None

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # Check for code block delimiter
            # Must be exactly ``` or ``` followed by language, not ```xyz inside a word
            if re.match(r'^```[a-zA-Z0-9]*\s*$', stripped):
                if not in_code_block:
                    # Opening code block
                    in_code_block = True
                    block_start_line = i
                    lang_tag = stripped[3:].strip()

                    # Check for language tag
                    if not lang_tag or lang_tag == '':
                        issues.append({
                            'line': i,
                            'type': 'missing_language_tag',
                            'message': f"Code block at line {i} missing language tag (e.g., ```cpp)",
                            'severity': 'warning'
                        })
                else:
                    # Closing code block
                    in_code_block = False
                    lang_tag = None

        # Check for unclosed block at end
        if in_code_block:
            issues.append({
                'line': block_start_line,
                'type': 'unclosed_code_block',
                'message': f"Code block starting at line {block_start_line} never closed (missing ``` at end)",
                'severity': 'error'
            })

        return issues

    def detect_non_breaking_spaces(self, content: str) -> List[Dict]:
        """
        Detect non-breaking spaces (U+00A0) that break Obsidian rendering.

        Non-breaking spaces cause:
        - Mermaid diagram parsing failures
        - Inconsistent indentation
        - Display issues in Obsidian
        """
        issues = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            # Find all U+00A0 occurrences
            if '\u00a0' in line:
                positions = [j for j, c in enumerate(line) if c == '\u00a0']
                issues.append({
                    'line': i,
                    'type': 'non_breaking_space',
                    'message': f"Line {i}: Found {len(positions)} non-breaking space(s) at positions {positions}",
                    'auto_fix': 'replace_with_standard_space',
                    'severity': 'error'
                })

        return issues

    def validate_mermaid_syntax(self, content: str) -> List[Dict]:
        """
        Validate Mermaid diagram syntax for Obsidian rendering.

        Checks:
        - Non-breaking spaces (U+00A0)
        - Pipe characters | in node text (breaks edge label parsing)
        - Unquoted edge labels with special characters
        - Unquoted flowchart nodes with special characters
        - Basic Mermaid keyword validation
        """
        issues = []

        # Extract mermaid blocks
        pattern = r'```mermaid\n(.*?)```'
        for match in re.finditer(pattern, content, re.DOTALL):
            start_line = content[:match.start()].count('\n') + 1
            mmd_code = match.group(1)

            # Check 1: Non-breaking spaces in Mermaid
            if '\u00a0' in mmd_code:
                issues.append({
                    'line': start_line,
                    'type': 'mermaid_non_breaking_space',
                    'message': f"Mermaid block at line {start_line} contains non-breaking spaces (breaks parsing in Obsidian)",
                    'severity': 'error'
                })

            # Check 2: Pipe character | in node text (graph TD, graph LR)
            # Find lines like: Node[Text with | inside]
            # The pipe character has special meaning in Mermaid (edge labels)
            for line_num, line in enumerate(mmd_code.split('\n'), start_line):
                if '[' in line and ']' in line:
                    # Match node definitions with unescaped pipe in text
                    # Pattern: Node[...|...] - pipe inside brackets breaks rendering
                    # Skip already-quoted nodes: Node["...|..."]
                    for match in re.finditer(r'\["([^"]*\|)', line):
                        # This is a quoted node with pipe, check if properly closed
                        pass  # Already quoted, skip
                    # Now find unquoted nodes with pipes
                    for match in re.finditer(r'\[(?!"[^"]*\|)([^"\]]*\|)', line):
                        if match:  # Found | inside unquoted brackets
                            node_text = match.group(1)
                            issues.append({
                                'line': start_line + line_num,
                                'type': 'mermaid_pipe_in_node',
                                'message': f"Line {start_line + line_num}: Pipe character | in node text - wrap in quotes: Node[\"{node_text}\"]",
                                'severity': 'error'
                            })

            # Check 3: Unquoted edge labels with special characters
            # Pattern: -->|label with special chars|
            # Edge labels with ()·φ{}[] must be quoted
            for line_num, line in enumerate(mmd_code.split('\n'), start_line):
                # Match all edge labels: -->|label|
                for match in re.finditer(r'-->?\|([^\|]+)\|', line):
                    label_text = match.group(1)
                    # Skip already quoted labels (starts with ")
                    if label_text.startswith('"'):
                        continue
                    # Check if label contains special characters that need quoting
                    if re.search(r'[(){}\[\]·φ]', label_text):
                        issues.append({
                            'line': start_line + line_num,
                            'type': 'mermaid_unquoted_label',
                            'message': f"Line {start_line + line_num}: Edge label contains special characters - wrap in quotes: -->|\"{label_text}\"|",
                            'severity': 'warning'
                        })

            # Check 4: flowchart nodes with unquoted special chars
            # flowchart TD is stricter than graph TD - requires quotes
            if mmd_code.strip().startswith('flowchart'):
                for line_num, line in enumerate(mmd_code.split('\n'), start_line):
                    # Match: [text] or [text<br>more]
                    # Skip if already has quotes ["text"]
                    for match in re.finditer(r'\[([^\]]+)\]', line):
                        node_text = match.group(1)
                        # Skip if already quoted or doesn't contain special chars
                        if node_text.startswith('"'):
                            continue
                        # Check if contains special characters that break flowchart parser
                        if re.search(r'[(){}\[\]·φ]', node_text):
                            issues.append({
                                'line': start_line + line_num,
                                'type': 'mermaid_flowchart_node',
                                'message': f"Line {start_line + line_num}: flowchart node with special chars - wrap in quotes: [\"{node_text}\"]",
                                'severity': 'error'
                            })

            # Check 5: Basic diagram type validation
            first_line = mmd_code.strip().split('\n')[0].strip() if mmd_code.strip() else ''
            valid_diagram_types = [
                'graph', 'flowchart', 'sequenceDiagram', 'classDiagram',
                'stateDiagram', 'erDiagram', 'gantt', 'pie', 'journey'
            ]

            if first_line and not any(first_line.startswith(t) for t in valid_diagram_types):
                issues.append({
                    'line': start_line,
                    'type': 'mermaid_invalid_diagram_type',
                    'message': f"Mermaid block at line {start_line}: Unrecognized diagram type '{first_line}'",
                    'severity': 'warning'
                })

        return issues

    def validate_cpp_syntax(self, content: str) -> List[Dict]:
        """
        Basic C++ syntax validation.

        Checks:
        - Balanced braces { }
        - Balanced parentheses ( )
        - Common syntax errors
        """
        issues = []

        # Extract cpp blocks
        pattern = r'```cpp\n(.*?)```'
        for match in re.finditer(pattern, content, re.DOTALL):
            start_line = content[:match.start()].count('\n') + 1
            cpp_code = match.group(1)

            # Check for balanced braces
            open_braces = cpp_code.count('{')
            close_braces = cpp_code.count('}')
            if open_braces != close_braces:
                issues.append({
                    'line': start_line,
                    'type': 'unbalanced_braces',
                    'message': f"C++ block at line {start_line}: {open_braces} {{ vs {close_braces} }} (unbalanced)",
                    'severity': 'error'
                })

            # Check for balanced parentheses in each line (basic check)
            lines = cpp_code.split('\n')
            for line_offset, line in enumerate(lines):
                # Skip comments and strings
                if '//' in line:
                    line = line[:line.index('//')]

                open_parens = line.count('(')
                close_parens = line.count(')')
                # Allow slight imbalance within a line (might span multiple lines)
                if abs(open_parens - close_parens) > 5:
                    issues.append({
                        'line': start_line + line_offset,
                        'type': 'unbalanced_parentheses',
                        'message': f"C++ line {start_line + line_offset}: Possible unbalanced parentheses ({open_parens} ( vs {close_parens} ))",
                        'severity': 'warning'
                    })

        return issues

    def validate_latex_syntax(self, content: str) -> List[Dict]:
        """
        Validate LaTeX math syntax for Obsidian MathJax compatibility.

        Checks:
        - Balanced $$ delimiters
        - Balanced $ delimiters
        - No nested $$ containing $
        - NO invalid \\bfS, \\bfF, \\bfU, \\bf n patterns (breaks MathJax)
        """
        issues = []
        lines = content.split('\n')

        # Remove code blocks before checking LaTeX
        prose_content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)

        # Check for balanced display math ($$)
        display_matches = prose_content.count('$$')
        if display_matches % 2 != 0:
            issues.append({
                'type': 'latex_unmatched_delimiter',
                'message': f"Unmatched $$ delimiters (found {display_matches} occurrences, expected even)",
                'severity': 'error'
            })

        # Check for nested delimiters ($$ containing $)
        for match in re.finditer(r'\$\$.*?\$\$', prose_content, re.DOTALL):
            if '$' in match.group(0)[2:-2]:  # Check inside the $$ blocks
                line_num = content[:match.start()].count('\n') + 1
                issues.append({
                    'line': line_num,
                    'type': 'latex_nested_delimiter',
                    'message': f"Line {line_num}: Nested $ delimiter inside $$ block (not allowed)",
                    'severity': 'error'
                })

        # 🔒 CRITICAL: Check for invalid \\bfS, \\bfF, \\bfU, \\bf n patterns
        # These break Obsidian's MathJax renderer
        invalid_patterns = [
            (r'\\bfS', r'\mathbf{S}', 'surface vector S'),
            (r'\\bfF', r'\mathbf{F}', 'force/flux vector F'),
            (r'\\bfU', r'\mathbf{U}', 'velocity vector U'),
            (r'\\bf n_f', r'\mathbf{n}_f', 'unit normal n_f'),
            (r'\\bf n(?![a-z_])', r'\mathbf{n}', 'unit normal n'),  # n followed by non-letter
        ]

        for i, line in enumerate(lines, 1):
            # Skip code blocks
            if line.strip().startswith('```'):
                continue

            for pattern, replacement, description in invalid_patterns:
                if re.search(pattern, line):
                    # Find occurrences for better error message
                    matches = re.findall(pattern, line)
                    issues.append({
                        'line': i,
                        'type': 'latex_invalid_bold_syntax',
                        'message': f"Line {i}: Invalid \\bf syntax detected ({description}): {pattern} → {replacement}. Use \\mathbf{{}} for MathJax compatibility.",
                        'severity': 'error',
                        'auto_fix': replacement
                    })

        return issues

    def validate_headers(self, content: str) -> List[Dict]:
        """
        Validate header hierarchy.

        Checks:
        - No skipped levels (e.g., H1 -> H3)
        - Proper markdown header format
        """
        issues = []
        lines = content.split('\n')
        prev_level = 0
        in_code_block = False

        for i, line in enumerate(lines, 1):
            # Track code blocks
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue

            # Skip checks inside code blocks
            if in_code_block:
                continue

            if line.startswith('#'):
                # Count # symbols to get level
                level = 0
                for char in line:
                    if char == '#':
                        level += 1
                    else:
                        break

                # Check for skipped levels
                if prev_level > 0 and level > prev_level + 1:
                    issues.append({
                        'line': i,
                        'type': 'header_skipped_level',
                        'message': f"Header skipped level: H{prev_level} -> H{level} (should be H{prev_level + 1})",
                        'severity': 'warning'
                    })

                prev_level = level

        return issues

    def auto_fix_non_breaking_spaces(self, content: str) -> Tuple[str, int]:
        """
        Auto-fix: Replace all U+00A0 with U+0020.

        Returns:
            (fixed_content, count_of_fixes)
        """
        fixed_content = content.replace('\u00a0', ' ')
        count = content.count('\u00a0')
        return fixed_content, count

    def auto_fix_mermaid(self, content: str) -> Tuple[str, int]:
        """
        Auto-fix common Mermaid syntax issues.

        Fixes:
        1. Pipe characters in node text → wrap in quotes
        2. Edge labels with special chars → wrap in quotes
        3. Flowchart nodes with special chars → wrap in quotes

        Returns:
            (fixed_content, fix_count)
        """
        fix_count = [0]  # Use list for mutability in nested function
        lines = content.split('\n')
        in_mermaid = False
        is_flowchart = False

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Track mermaid blocks
            if stripped.startswith('```'):
                if not in_mermaid:
                    if 'mermaid' in stripped.lower():
                        in_mermaid = True
                        is_flowchart = False
                else:
                    in_mermaid = False
                    is_flowchart = False

            # Only process lines inside mermaid blocks
            if in_mermaid:
                # Check if this is a flowchart diagram
                if 'flowchart' in stripped:
                    is_flowchart = True

                # Fix 1: Pipe in node text
                # Pattern: Node[...|...] or Node[...|...|...]
                # Fix: Node["...|..."]
                if '[' in line:
                    # Fix nodes with unescaped pipes
                    def fix_pipes_in_nodes(match):
                        node_text = match.group(1)
                        # If contains | but not already quoted, quote it
                        if '|' in node_text and not node_text.startswith('"'):
                            fix_count[0] += 1
                            return match.group(0).replace(node_text, f'"{node_text}"')
                        return match.group(0)

                    lines[i] = re.sub(r'\[([^\]]*\|)\]', fix_pipes_in_nodes, lines[i])

                # Fix 2: Edge labels with special chars
                # Pattern: -->|label with ()·φ{}[]|
                # Fix: -->|"label with ()·φ{}[]"|
                def fix_edge_labels(match):
                    label = match.group(1)
                    # If contains special chars and not quoted, quote it
                    if re.search(r'[(){}\[\]·φ]', label) and not label.startswith('"'):
                        fix_count[0] += 1
                        return match.group(0).replace(label, f'"{label}"')
                    return match.group(0)

                lines[i] = re.sub(r'-->?\|([^\|]+)\|', fix_edge_labels, lines[i])

                # Fix 3: Flowchart nodes with special chars (only in flowchart)
                if is_flowchart:
                    def fix_flowchart_nodes(match):
                        node_text = match.group(1)
                        # If contains special chars, quote it
                        if re.search(r'[(){}\[\]·φ]', node_text) and not node_text.startswith('"'):
                            fix_count[0] += 1
                            return match.group(0).replace(node_text, f'"{node_text}"')
                        return match.group(0)

                    lines[i] = re.sub(r'\[([^\]]+)\]', fix_flowchart_nodes, lines[i])

        return '\n'.join(lines), fix_count[0]

    def auto_fix_latex_syntax(self, content: str) -> Tuple[str, int]:
        """
        Auto-fix invalid LaTeX bold vector syntax for Obsidian MathJax.

        Fixes:
        - \\bfS → \\mathbf{S}
        - \\bfF → \\mathbf{F}
        - \\bfU → \\mathbf{U}
        - \\bf n_f → \\mathbf{n}_f
        - \\bf n → \\mathbf{n}

        Returns:
            (fixed_content, fix_count)
        """
        # Don't fix code blocks
        lines = content.split('\n')
        in_code_block = False
        fix_count = [0]  # Use list for mutability

        for i, line in enumerate(lines):
            # Track code blocks
            if line.strip().startswith('```'):
                if not in_code_block:
                    in_code_block = True
                else:
                    in_code_block = False
                continue

            # Skip LaTeX fixes inside code blocks
            if in_code_block:
                continue

            original_line = line

            # Fix patterns in order (more specific first)
            line = re.sub(r'\\bf n_f', r'\mathbf{n}_f', line)
            line = re.sub(r'\\bf n(?![a-z_])', r'\mathbf{n}', line)  # n followed by non-letter
            line = re.sub(r'\\bfU', r'\mathbf{U}', line)
            line = re.sub(r'\\bfF', r'\mathbf{F}', line)
            line = re.sub(r'\\bfS', r'\mathbf{S}', line)

            if line != original_line:
                fix_count[0] += 1

            lines[i] = line

        return '\n'.join(lines), fix_count[0]

    def validate_file(self, file_path: Path) -> Dict:
        """
        Run all validations on a file.

        Returns:
            Validation result dictionary with all issues found
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {
                'file': str(file_path),
                'error': f"Could not read file: {str(e)}",
                'passed': False,
                'total_issues': 1
            }

        result = {
            'file': str(file_path),
            'code_block_issues': self.validate_code_blocks(content),
            'non_breaking_space_issues': self.detect_non_breaking_spaces(content),
            'mermaid_issues': self.validate_mermaid_syntax(content),
            'cpp_syntax_issues': self.validate_cpp_syntax(content),
            'latex_issues': self.validate_latex_syntax(content),
            'header_issues': self.validate_headers(content),
            'total_issues': 0,
            'passed': True
        }

        # Count total issues
        result['total_issues'] = (
            len(result['code_block_issues']) +
            len(result['non_breaking_space_issues']) +
            len(result['mermaid_issues']) +
            len(result['cpp_syntax_issues']) +
            len(result['latex_issues']) +
            len(result['header_issues'])
        )

        # Count errors vs warnings
        all_issues = (
            result['code_block_issues'] +
            result['non_breaking_space_issues'] +
            result['mermaid_issues'] +
            result['cpp_syntax_issues'] +
            result['latex_issues'] +
            result['header_issues']
        )

        error_count = sum(1 for i in all_issues if i.get('severity') == 'error')
        result['passed'] = error_count == 0
        result['error_count'] = error_count
        result['warning_count'] = len(all_issues) - error_count

        return result

    def print_report(self, result: Dict, verbose: bool = True):
        """Print validation report."""
        print(f"\n{'='*60}")
        print(f"Enhanced Obsidian QC Report")
        print(f"{'='*60}")
        print(f"File: {result['file']}")

        if 'error' in result:
            print(f"Status: ❌ ERROR - {result['error']}")
            print(f"{'='*60}\n")
            return

        print(f"Status: {'✅ PASSED' if result['passed'] else '❌ FAILED'}")
        print(f"Errors: {result.get('error_count', 0)}")
        print(f"Warnings: {result.get('warning_count', 0)}")
        print(f"Total Issues: {result['total_issues']}")
        print(f"{'='*60}\n")

        # Always show errors
        if not result['passed'] or verbose:
            issue_categories = [
                ('code_block_issues', '📦 Code Block Issues'),
                ('non_breaking_space_issues', '🔤 Non-Breaking Space Issues'),
                ('mermaid_issues', '📊 Mermaid Issues'),
                ('cpp_syntax_issues', '⚙️ C++ Syntax Issues'),
                ('latex_issues', '📐 LaTeX Issues'),
                ('header_issues', '📝 Header Issues'),
            ]

            for category_key, category_name in issue_categories:
                issues = result.get(category_key, [])
                if issues:
                    # Filter for errors first, then warnings
                    errors = [i for i in issues if i.get('severity') == 'error']
                    warnings = [i for i in issues if i.get('severity') == 'warning']

                    if errors:
                        print(f"{category_name} - ERRORS ({len(errors)}):")
                        for issue in errors:
                            line_info = f"Line {issue['line']}:" if 'line' in issue else ""
                            print(f"   {line_info} {issue['message']}")
                        print()

                    if warnings and (verbose or not errors):
                        print(f"{category_name} - WARNINGS ({len(warnings)}):")
                        for issue in warnings[:10]:  # Limit warnings
                            line_info = f"Line {issue['line']}:" if 'line' in issue else ""
                            print(f"   {line_info} {issue['message']}")
                        if len(warnings) > 10:
                            print(f"   ... and {len(warnings) - 10} more warnings")
                        print()


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Enhanced Obsidian QC - Validate markdown for Obsidian rendering",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate a file
  python3 enhanced_obsidian_qc.py --file Day_01.md

  # Auto-fix non-breaking spaces and Mermaid syntax issues
  python3 enhanced_obsidian_qc.py --file Day_01.md --fix

  # Verbose output (show warnings too)
  python3 enhanced_obsidian_qc.py --file Day_01.md --verbose
        """
    )
    parser.add_argument("--file", required=True, type=Path, help="Path to markdown file")
    parser.add_argument("--fix", action="store_true", help="Auto-fix non-breaking spaces and Mermaid syntax issues (creates .backup)")
    parser.add_argument("--verbose", action="store_true", help="Show warnings in addition to errors")
    args = parser.parse_args()

    qc = EnhancedObsidianQC()
    file_path = args.file

    if not file_path.exists():
        print(f"❌ Error: File not found: {file_path}")
        sys.exit(1)

    if args.fix:
        # Auto-fix mode
        print(f"🔧 Auto-fixing syntax issues in: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Fix non-breaking spaces
        fixed_content, nb_count = qc.auto_fix_non_breaking_spaces(content)

        # Fix Mermaid syntax issues
        fixed_content, mermaid_count = qc.auto_fix_mermaid(fixed_content)

        # Fix LaTeX syntax issues (NEW)
        fixed_content, latex_count = qc.auto_fix_latex_syntax(fixed_content)

        total_fixes = nb_count + mermaid_count + latex_count

        if total_fixes > 0:
            # Backup original
            backup_path = file_path.with_suffix('.md.backup')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)

            # Write fixed
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)

            print(f"✅ Fixed {total_fixes} issue(s):")
            if nb_count > 0:
                print(f"   - {nb_count} non-breaking space(s)")
            if mermaid_count > 0:
                print(f"   - {mermaid_count} Mermaid syntax issue(s)")
            if latex_count > 0:
                print(f"   - {latex_count} LaTeX bold syntax issue(s) (\\bfS → \\mathbf{{S}})")
            print(f"   Original backed up to: {backup_path}")

            # Run validation again to check remaining issues
            result = qc.validate_file(file_path)
            qc.print_report(result, verbose=args.verbose)

            sys.exit(0 if result['passed'] else 1)
        else:
            print("✅ No fixable issues found. File is clean.")

            # Run validation to show other issues
            result = qc.validate_file(file_path)
            qc.print_report(result, verbose=args.verbose)

            sys.exit(0 if result['passed'] else 1)
    else:
        # Validation mode
        result = qc.validate_file(file_path)
        qc.print_report(result, verbose=args.verbose)

        if not result['passed']:
            print("\n💡 Tip: Run with --fix to auto-fix non-breaking spaces and Mermaid syntax issues")
            print("   Example: python3 enhanced_obsidian_qc.py --file Day_01.md --fix")

        sys.exit(0 if result['passed'] else 1)


if __name__ == "__main__":
    main()
