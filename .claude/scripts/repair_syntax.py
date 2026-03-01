#!/usr/bin/env python3
"""
repair_syntax.py - Markdown Syntax Repair

Detects and fixes common Markdown syntax issues:
- Unclosed code blocks (odd number of ```)
- Unclosed bold (**)
- Unclosed italic (*)
- Hanging code block state detection

Usage:
    python3 repair_syntax.py <input_file> <output_file>
"""

import sys
import re
from pathlib import Path


class SyntaxRepairer:
    def __init__(self, input_path):
        self.input_path = Path(input_path)
        self.content = ""
        self.issues = []

    def read_file(self):
        """Read input file"""
        with open(self.input_path, 'r', encoding='utf-8') as f:
            self.content = f.read()
        return self.content

    def detect_code_block_state(self, content):
        """Analyze content to find code block state at each line"""
        lines = content.split('\n')
        states = []

        in_code_block = False
        current_lang = None

        for i, line in enumerate(lines):
            # Check for code block markers
            if line.strip().startswith('```'):
                backtick_count = line.count('`')
                if backtick_count >= 3:
                    in_code_block = not in_code_block
                    if in_code_block:
                        # Extract language tag
                        current_lang = line.strip()[3:].strip() or 'unknown'
                    else:
                        current_lang = None

            states.append({
                'line_num': i + 1,
                'in_code_block': in_code_block,
                'language': current_lang
            })

        return states

    def find_unclosed_blocks(self, content):
        """Find unclosed code blocks, bold, italic"""
        issues = []

        # Count code block markers
        code_markers = re.findall(r'```[a-z]*', content)
        if len(code_markers) % 2 != 0:
            issues.append({
                'type': 'UNCLOSED_CODE_BLOCK',
                'severity': 'CRITICAL',
                'count': len(code_markers),
                'message': f"Odd number of code block markers: {len(code_markers)}"
            })

        # Count bold markers
        bold_markers = re.findall(r'\*\*', content)
        if len(bold_markers) % 2 != 0:
            issues.append({
                'type': 'UNCLOSED_BOLD',
                'severity': 'WARNING',
                'count': len(bold_markers),
                'message': f"Odd number of bold markers: {len(bold_markers)}"
            })

        # Count italic markers (not part of bold)
        # Remove bold markers first
        content_no_bold = re.sub(r'\*\*', '', content)
        italic_markers = re.findall(r'\*', content_no_bold)
        if len(italic_markers) % 2 != 0:
            issues.append({
                'type': 'UNCLOSED_ITALIC',
                'severity': 'WARNING',
                'count': len(italic_markers),
                'message': f"Odd number of italic markers: {len(italic_markers)}"
            })

        return issues

    def detect_hanging_code_at_end(self, content):
        """Check if file ends inside a code block"""
        lines = content.split('\n')

        # Count backticks in entire file
        backtick_count = content.count('```')

        if backtick_count % 2 != 0:
            # Find the last code block start
            for i in range(len(lines) - 1, -1, -1):
                if '```' in lines[i]:
                    return {
                        'line': i + 1,
                        'language': lines[i].strip()[3:].strip() or 'unknown',
                        'last_lines': '\n'.join(lines[max(0, i-2):])
                    }

        return None

    def fix_unclosed_code_block(self, content):
        """Attempt to fix unclosed code block at end"""
        hanging = self.detect_hanging_code_at_end(content)
        if hanging:
            lang = hanging['language']
            # Add closing backticks
            content += f"\n```\n"
            self.issues.append({
                'type': 'FIXED_CODE_BLOCK',
                'action': 'Added closing ```',
                'language': lang
            })
        return content

    def validate_mermaid_syntax(self, content):
        """Basic Mermaid syntax validation"""
        issues = []

        # Find all Mermaid blocks
        mermaid_blocks = re.findall(r'```mermaid\n(.*?)\n```', content, re.DOTALL)

        for i, block in enumerate(mermaid_blocks, 1):
            lines = block.split('\n')

            # Check for common issues
            for j, line in enumerate(lines):
                # Check for non-breaking spaces (U+00A0)
                if '\u00a0' in line:
                    issues.append({
                        'block': i,
                        'line': j,
                        'issue': 'NON_BREAKING_SPACE',
                        'message': f"Non-breaking space detected: {line[:50]}"
                    })

                # Check for unquoted special characters in node text
                if '[' in line and ']' in line:
                    # Extract node content
                    match = re.search(r'\[([^\]]*)\]', line)
                    if match:
                        node_content = match.group(1)
                        # Check for problematic characters
                        if any(char in node_content for char in ['|', '(', ')', '{', '}', '·', 'φ']):
                            if '"' not in line:  # Not already quoted
                                issues.append({
                                    'block': i,
                                    'line': j,
                                    'issue': 'UNQUOTED_SPECIAL_CHAR',
                                    'message': f"Unquoted special chars: {line[:50]}"
                                })

        return issues

    def repair(self):
        """Main repair workflow"""
        print(f"🔧 Repairing syntax in: {self.input_path}")

        # Read content
        self.read_file()

        # Detect issues
        print("\n🔍 Detecting issues...")
        issues = self.find_unclosed_blocks(self.content)

        for issue in issues:
            self.issues.append(issue)
            print(f"  {issue['severity']}: {issue['message']}")

        # Fix unclosed code blocks
        if any(i['type'] == 'UNCLOSED_CODE_BLOCK' for i in issues):
            print("\n🔨 Fixing unclosed code block...")
            self.content = self.fix_unclosed_code_block(self.content)

        # Validate Mermaid
        print("\n🔍 Validating Mermaid diagrams...")
        mermaid_issues = self.validate_mermaid_syntax(self.content)
        for issue in mermaid_issues:
            self.issues.append(issue)
            print(f"  ⚠️  Block {issue['block']}, Line {issue['line']}: {issue['issue']}")

        # Generate report
        print(f"\n📊 Repair Summary:")
        print(f"  Total issues found: {len(self.issues)}")
        print(f"  Critical: {sum(1 for i in self.issues if i.get('severity') == 'CRITICAL')}")
        print(f"  Warnings: {sum(1 for i in self.issues if i.get('severity') == 'WARNING')}")

        return self.content

    def save(self, output_path):
        """Save repaired content"""
        output_path = Path(output_path)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(self.content)
        print(f"\n✅ Saved repaired content to: {output_path}")

    def get_state_report(self):
        """Generate state report for next stage"""
        hanging = self.detect_hanging_code_at_end(self.content)

        report = {
            'file': str(self.input_path),
            'line_count': len(self.content.split('\n')),
            'ends_in_code_block': hanging is not None,
            'hanging_info': hanging,
            'issues': self.issues
        }

        return report


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 repair_syntax.py <input_file> <output_file>")
        print("\nThis script:")
        print("  - Detects unclosed code blocks, bold, italic")
        print("  - Fixes unclosed code blocks at end of file")
        print("  - Validates Mermaid diagram syntax")
        print("  - Generates state report for seam healing")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    repairer = SyntaxRepairer(input_path)
    repaired_content = repairer.repair()
    repairer.save(output_path)

    # Save state report
    report_path = Path(output_path).with_suffix('.state.json')
    import json
    with open(report_path, 'w') as f:
        json.dump(repairer.get_state_report(), f, indent=2)
    print(f"📊 State report saved to: {report_path}")


if __name__ == "__main__":
    main()
