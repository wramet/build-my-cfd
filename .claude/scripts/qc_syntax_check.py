#!/usr/bin/env python3
import sys
import argparse
import re
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from scripts.workflow_logger import get_logger
    _logger = get_logger("/tmp/workflow_debug.log")
    _logger_enabled = True
except Exception:
    _logger_enabled = False

def log_phase(msg):
    """Log phase if logger is available."""
    if _logger_enabled:
        _logger.log_phase(0, msg)

def check_balanced_backticks(content):
    count = content.count("```")
    if count % 2 != 0:
        return f"❌ Unbalanced code blocks (found {count} instances of ```)"
    return None

def check_nested_latex(content):
    # Check for $$ containing $ inside
    # This regex looks for $$ ... $ ... $$ which is often a mistake
    # It's a simple heuristic
    pattern = re.compile(r'\$\$(.*?)\$\$', re.DOTALL)
    for match in pattern.finditer(content):
        inside = match.group(1)
        if '$' in inside:
             # Make sure it's not just an escaped \$
            if re.search(r'(?<!\\)\$', inside):
                return "❌ Nested LaTeX delimiters found (usage of $ inside $$)"
    return None

def check_header_hierarchy(content):
    lines = content.split('\n')
    last_level = 0
    in_code_block = False

    for i, line in enumerate(lines):
        # Track code blocks
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            continue

        # Skip checks inside code blocks
        if in_code_block:
            continue

        # Check header hierarchy only outside code blocks
        if line.strip().startswith('#'):
            # Skip C preprocessor directives that look like headers
            if re.match(r'^\s*#(include|define|pragma|if|ifdef|ifndef|else|elif|endif|error|warning)', line):
                continue

            level = len(line.split()[0])
            if level > last_level + 1:
                return f"❌ Skipped header level on line {i+1} (H{last_level} -> H{level})"
            last_level = level
    return None

def main():
    parser = argparse.ArgumentParser(description="QC Syntax Checker")
    parser.add_argument("--file", required=True, help="Path to markdown file")
    parser.add_argument("--silent", action="store_true", help="Suppress output on success")
    args = parser.parse_args()

    log_phase(f"Gate 4: Syntax QC - {args.file}")

    try:
        with open(args.file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    errors = []
    
    # 1. Code Block Balance
    err = check_balanced_backticks(content)
    if err: errors.append(err)

    # 2. Nested LaTeX
    err = check_nested_latex(content)
    if err: errors.append(err)
    
    # 3. Header Hierarchy
    err = check_header_hierarchy(content)
    if err: errors.append(err)

    if errors:
        print(f"\n⚠️ Auto-QC Syntax Issues in {args.file}:")
        for e in errors:
            print(e)
        print("Please correct these before proceeding.\n")
        if _logger_enabled:
            _logger.log_task_complete(f"Gate 4: Syntax QC - {args.file}", f"FAILED: {len(errors)} errors")
        # Ensure non-zero exit code so the hook alerts the user/agent
        sys.exit(1)
    
    if not args.silent:
        print("✅ Syntax Check Passed")

    if _logger_enabled:
        _logger.log_task_complete(f"Gate 4: Syntax QC - {args.file}", "PASSED: All checks")

    sys.exit(0)

if __name__ == "__main__":
    main()
