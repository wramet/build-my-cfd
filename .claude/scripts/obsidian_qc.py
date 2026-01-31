#!/usr/bin/env python3
"""
Obsidian Rendering QC Script

Validates markdown files for Obsidian-specific syntax requirements.
Uses Mermaid CLI for authoritative Mermaid validation.

Usage:
    python3 obsidian_qc.py --file daily_learning/Phase_01_Foundation_Theory/01.md
    python3 obsidian_qc.py --directory daily_learning/ --report obsidian_report.md
"""

import argparse
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class ObsidianQC:
    """Validator for Obsidian markdown rendering"""

    def __init__(self, mermaid_cli: str = "mmdc"):
        self.mermaid_cli = mermaid_cli
        self.mermaid_available = self._check_mermaid_cli()

    def _check_mermaid_cli(self) -> bool:
        """Check if Mermaid CLI is available"""
        try:
            result = subprocess.run(
                [self.mermaid_cli, "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def extract_mermaid_blocks(self, content: str) -> List[Tuple[int, int, str]]:
        """
        Extract mermaid blocks with line numbers.

        Returns: List of (start_line, end_line, mermaid_code)
        """
        blocks = []
        pattern = r'```mermaid\n(.*?)```'

        for match in re.finditer(pattern, content, re.DOTALL):
            start_line = content[:match.start()].count('\n') + 1
            end_line = content[:match.end()].count('\n') + 1
            mmd_code = match.group(1).strip()
            blocks.append((start_line, end_line, mmd_code))

        return blocks

    def validate_mermaid_with_cli(self, mmd_code: str) -> Tuple[bool, str]:
        """
        Validate Mermaid using official CLI.

        Returns: (is_valid, error_message)
        """
        if not self.mermaid_available:
            return False, "Mermaid CLI not installed. Run: npm install -g @mermaid-js/mermaid-cli"

        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as f:
                f.write(mmd_code)
                f.flush()
                temp_path = f.name

            result = subprocess.run(
                [self.mermaid_cli, '-i', temp_path, '-o', '/tmp/obsidian_qc_temp.png'],
                capture_output=True,
                text=True,
                timeout=10
            )

            Path(temp_path).unlink()

            if result.returncode != 0:
                # Extract useful error message
                error_msg = result.stderr.strip()
                if not error_msg:
                    error_msg = result.stdout.strip()
                return False, error_msg
            return True, "OK"

        except subprocess.TimeoutExpired:
            return False, "Validation timeout (possible infinite loop)"
        except Exception as e:
            return False, f"Validation error: {str(e)}"

    def validate_mermaid(self, content: str) -> List[Dict]:
        """
        Validate all Mermaid diagrams in content.

        Returns: List of issues found
        """
        issues = []
        blocks = self.extract_mermaid_blocks(content)

        for start_line, end_line, mmd_code in blocks:
            is_valid, error_msg = self.validate_mermaid_with_cli(mmd_code)
            if not is_valid:
                issues.append({
                    'line': start_line,
                    'end_line': end_line,
                    'type': 'mermaid_syntax_error',
                    'message': error_msg[:200]  # Truncate long errors
                })

        return issues

    def validate_latex(self, content: str) -> List[Dict]:
        """
        Validate LaTeX math syntax.

        Checks:
        - Balanced $$ delimiters
        - Balanced $ delimiters
        - No nested $$ containing $
        - Only checks prose, skips code blocks
        """
        issues = []

        # Remove code blocks from content before checking LaTeX
        # This prevents false positives from code containing $ (e.g., CMake, shell)
        prose_content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)

        # Check for balanced display math ($$)
        display_matches = prose_content.count('$$')
        if display_matches % 2 != 0:
            issues.append({
                'type': 'latex_unmatched_delimiter',
                'message': f"Unmatched $$ delimiters (found {display_matches} occurrences, expected even)"
            })

        # Check for nested delimiters ($$ containing $)
        for match in re.finditer(r'\$\$.*?\$\$', prose_content, re.DOTALL):
            if '$' in match.group(0)[2:-2]:  # Check inside the $$ blocks
                # Find line number in original content
                line_num = content[:match.start()].count('\n') + 1
                issues.append({
                    'line': line_num,
                    'type': 'latex_nested_delimiter',
                    'message': "Nested $ delimiter inside $$ block (not allowed)"
                })

        # Check for balanced inline math ($) in prose only
        # Skip lines with $$
        lines = prose_content.split('\n')
        for i, line in enumerate(lines, 1):
            # Skip lines that are part of $$
            if '$$' in line:
                continue

            # Count single $ delimiters
            single_dollar_count = line.count('$')
            if single_dollar_count % 2 != 0:
                issues.append({
                    'line': i,
                    'type': 'latex_unmatched_inline',
                    'message': f"Possible unmatched $ delimiter on line {i}"
                })

        return issues

    def validate_code_blocks(self, content: str) -> List[Dict]:
        """
        Validate code block syntax.

        Checks:
        - Balanced backticks
        - Language tags present
        """
        issues = []

        # Count code block delimiters
        tick_count = content.count('```')
        if tick_count % 2 != 0:
            issues.append({
                'type': 'code_block_unmatched',
                'message': f"Unmatched code block delimiters (found {tick_count} ``` markers, expected even)"
            })

        # Check for code blocks without language tags
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if line.startswith('```'):
                # Extract language tag
                lang_tag = line[3:].strip()
                if not lang_tag or lang_tag == '':
                    issues.append({
                        'line': i,
                        'type': 'code_block_no_language',
                        'message': f"Code block at line {i} missing language tag"
                    })

        return issues

    def validate_headers(self, content: str) -> List[Dict]:
        """
        Validate header hierarchy.

        Checks:
        - No skipped levels (e.g., H1 -> H3)
        """
        issues = []
        lines = content.split('\n')
        prev_level = 0

        for i, line in enumerate(lines, 1):
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
                        'message': f"Header skipped level: H{prev_level} -> H{level} (should be H{prev_level + 1})"
                    })

                prev_level = level

        return issues

    def validate_file(self, file_path: Path) -> Dict:
        """
        Validate a single markdown file.

        Returns: Validation result dictionary
        """
        try:
            content = file_path.read_text()
        except Exception as e:
            return {
                'file': str(file_path),
                'error': f"Could not read file: {str(e)}",
                'passed': False
            }

        result = {
            'file': str(file_path),
            'mermaid_issues': self.validate_mermaid(content),
            'latex_issues': self.validate_latex(content),
            'code_block_issues': self.validate_code_blocks(content),
            'header_issues': self.validate_headers(content),
            'passed': True
        }

        # Check if any issues found
        total_issues = (
            len(result['mermaid_issues']) +
            len(result['latex_issues']) +
            len(result['code_block_issues']) +
            len(result['header_issues'])
        )

        result['passed'] = total_issues == 0
        result['total_issues'] = total_issues

        return result

    def validate_directory(self, directory: Path, pattern: str = "*.md") -> List[Dict]:
        """
        Validate all markdown files in directory.

        Returns: List of validation results
        """
        results = []
        for md_file in directory.rglob(pattern):
            results.append(self.validate_file(md_file))
        return results

    def generate_report(self, results: List[Dict], output_path: Path):
        """Generate markdown validation report"""
        with open(output_path, 'w') as f:
            f.write("# Obsidian QC Report\n\n")

            # Summary
            passed = sum(1 for r in results if r.get('passed', False))
            failed = len(results) - passed
            total_issues = sum(r.get('total_issues', 0) for r in results)

            f.write(f"## Summary\n\n")
            f.write(f"- **Files checked**: {len(results)}\n")
            f.write(f"- ✅ **Passed**: {passed}\n")
            f.write(f"- ❌ **Failed**: {failed}\n")
            f.write(f"- **Total issues**: {total_issues}\n\n")

            # Failed files
            failed_results = [r for r in results if not r.get('passed', False)]
            if failed_results:
                f.write("## Files with Issues\n\n")

                for result in failed_results:
                    f.write(f"### {result['file']}\n\n")

                    # Mermaid issues
                    if result.get('mermaid_issues'):
                        f.write(f"#### Mermaid Issues ({len(result['mermaid_issues'])})\n\n")
                        for issue in result['mermaid_issues']:
                            f.write(f"- **Line {issue.get('line', '?')}**: {issue['message']}\n")

                    # LaTeX issues
                    if result.get('latex_issues'):
                        f.write(f"#### LaTeX Issues ({len(result['latex_issues'])})\n\n")
                        for issue in result['latex_issues']:
                            line_info = f"Line {issue.get('line', '?')}: " if 'line' in issue else ""
                            f.write(f"- {line_info}{issue['message']}\n")

                    # Code block issues
                    if result.get('code_block_issues'):
                        f.write(f"#### Code Block Issues ({len(result['code_block_issues'])})\n\n")
                        for issue in result['code_block_issues']:
                            line_info = f"Line {issue.get('line', '?')}: " if 'line' in issue else ""
                            f.write(f"- {line_info}{issue['message']}\n")

                    # Header issues
                    if result.get('header_issues'):
                        f.write(f"#### Header Issues ({len(result['header_issues'])})\n\n")
                        for issue in result['header_issues']:
                            f.write(f"- **Line {issue['line']}**: {issue['message']}\n")

                    f.write("\n---\n\n")

            # Passed files
            passed_results = [r for r in results if r.get('passed', False)]
            if passed_results:
                f.write("## Files Passed ✅\n\n")
                for result in passed_results:
                    f.write(f"- {result['file']}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Validate markdown files for Obsidian rendering"
    )
    parser.add_argument('--file', type=Path, help='Validate single file')
    parser.add_argument('--directory', type=Path, help='Validate all .md files in directory')
    parser.add_argument('--report', type=Path, help='Output report file')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    qc = ObsidianQC()

    if args.file:
        result = qc.validate_file(args.file)
        results = [result]

        if args.verbose or not result['passed']:
            print(f"\n{'='*60}")
            print(f"File: {result['file']}")
            print(f"Status: {'✅ PASSED' if result['passed'] else '❌ FAILED'}")
            print(f"Total Issues: {result.get('total_issues', 0)}")

            if result.get('mermaid_issues'):
                print(f"\nMermaid Issues: {len(result['mermaid_issues'])}")
                for issue in result['mermaid_issues']:
                    print(f"  Line {issue['line']}: {issue['message'][:80]}")

            if result.get('latex_issues'):
                print(f"\nLaTeX Issues: {len(result['latex_issues'])}")
                for issue in result['latex_issues']:
                    line_info = f"Line {issue.get('line', '?')}: " if 'line' in issue else ""
                    print(f"  {line_info}{issue['message']}")

            if result.get('code_block_issues'):
                print(f"\nCode Block Issues: {len(result['code_block_issues'])}")
                for issue in result['code_block_issues']:
                    line_info = f"Line {issue.get('line', '?')}: " if 'line' in issue else ""
                    print(f"  {line_info}{issue['message']}")

            if result.get('header_issues'):
                print(f"\nHeader Issues: {len(result['header_issues'])}")
                for issue in result['header_issues']:
                    print(f"  Line {issue['line']}: {issue['message']}")

    elif args.directory:
        results = qc.validate_directory(args.directory)

        # Print summary
        passed = sum(1 for r in results if r.get('passed', False))
        failed = len(results) - passed
        total_issues = sum(r.get('total_issues', 0) for r in results)

        print(f"\n{'='*60}")
        print(f"Obsidian QC Results for {args.directory}")
        print(f"{'='*60}")
        print(f"Files checked: {len(results)}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Total Issues: {total_issues}")
        print(f"{'='*60}\n")

        # Show failed files
        for result in results:
            if not result.get('passed', False):
                print(f"❌ {result['file']}")
                print(f"   Issues: {result.get('total_issues', 0)}")
                if result.get('mermaid_issues'):
                    print(f"   Mermaid: {len(result['mermaid_issues'])} errors")
                if result.get('latex_issues'):
                    print(f"   LaTeX: {len(result['latex_issues'])} errors")
                if result.get('code_block_issues'):
                    print(f"   Code blocks: {len(result['code_block_issues'])} errors")
                if result.get('header_issues'):
                    print(f"   Headers: {len(result['header_issues'])} errors")
                print()

    if args.report:
        qc.generate_report(results, args.report)
        print(f"Report saved to: {args.report}")


if __name__ == '__main__':
    main()
