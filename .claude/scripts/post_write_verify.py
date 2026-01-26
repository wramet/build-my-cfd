#!/usr/bin/env python3
"""
Post-write verification hook for Claude Code.

Verifies content after Write operations to catch common issues.
"""

import argparse
import json
import sys
from pathlib import Path


def verify_write_after(file_path: str) -> bool:
    """
    Verify file state after writing.

    Args:
        file_path: Path to file that was written

    Returns:
        True if verification passes
    """
    # Check if this is a content file
    content_extensions = ['.md']
    if not any(file_path.endswith(ext) for ext in content_extensions):
        return True  # Not a markdown file

    issues = []

    # Read the file
    try:
        with open(file_path) as f:
            content = f.read()
    except Exception as e:
        with open('/tmp/write_verification.log', 'w') as f:
            f.write(f"Failed to read file: {e}\n")
        return True  # Don't fail on read errors

    # Check for common issues

    # 1. Unclosed code blocks
    code_block_count = content.count('```')
    if code_block_count % 2 != 0:
        issues.append("Unclosed code block (odd count of ```)")

    # 2. Nested LaTeX (simplified check)
    if '$$' in content:
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if '$$' in line and '$' in line and line.count('$') > 2:
                issues.append(f"Line {i}: Possible nested LaTeX")

    # 3. Write results
    with open('/tmp/write_verification.log', 'w') as f:
        f.write(f"Write verification: {file_path}\n")
        if issues:
            f.write(f"Issues found: {len(issues)}\n")
            for issue in issues:
                f.write(f"  - {issue}\n")
        else:
            f.write("No issues found\n")

    return len(issues) == 0


def main():
    parser = argparse.ArgumentParser(description='Verify after write')
    parser.add_argument('--file', required=True, help='File that was written')
    parser.add_argument('--output', required=True, help='Output log file')

    args = parser.parse_args()

    result = verify_write_after(args.file)

    with open(args.output, 'a') as f:
        f.write(f"Post-write verification: {'PASSED' if result else 'WARNING'}\n")

    return 0  # Don't block writes, just warn


if __name__ == '__main__':
    sys.exit(main())
