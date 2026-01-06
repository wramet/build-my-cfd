import argparse
import re
import sys
from pathlib import Path

def parse_arguments():
    parser = argparse.ArgumentParser(description='Validate Markdown daily learning files.')
    parser.add_argument('files', metavar='FILE', type=str, nargs='*', help='Specific files to validate')
    parser.add_argument('--day', nargs=2, type=int, metavar=('START', 'END'), help='Validate range of days (e.g. 1 12)')
    return parser.parse_args()

def get_target_files(args):
    files = []
    base_path = Path('daily_learning')
    
    if args.day:
        start, end = args.day
        for i in range(start, end + 1):
            # Try both naming conventions if necessary, but standard is YYYY-MM-DD.md
            # Assuming 2026-01-XX for now based on context
            filename = f"2026-01-{i:02d}.md"
            file_path = base_path / filename
            if file_path.exists():
                files.append(file_path)
            else:
                print(f"Warning: File {file_path} not found.")
    
    if args.files:
        for f in args.files:
            path = Path(f)
            if path.exists():
                files.append(path)
            else:
                print(f"Error: File {f} not found.")

    return sorted(list(set(files)))

def check_backtick_latex(content, filename):
    errors = []
    lines = content.splitlines()
    for i, line in enumerate(lines):
        if re.search(r'`\$\$', line) or re.search(r'\$\$`', line):
             errors.append(f"❌ Backtick-wrapped Block LaTeX detected (`$$...$$`) at Line {i+1}: {line.strip()[:50]}...")
    return errors

def check_code_blocks(content):
    errors = []
    # Count strict ``` occurrences (start of line or after space, but typically start of line in these docs)
    # We look for lines that contain only ``` or ```language
    
    # Simple count of triple backticks
    matches = re.findall(r'```', content)
    if len(matches) % 2 != 0:
        errors.append(f"❌ Unclosed Code Blocks: Found {len(matches)} triple backticks (odd number).")
    
    return errors

def check_truncation(content):
    errors = []
    lines = content.strip().splitlines()
    if not lines:
        return ["❌ Empty file"]
    
    last_line = lines[-1].strip()
    
    # Truncation heuristics
    if last_line.endswith('**') and not last_line.startswith('**'): # dangling bold
        errors.append(f"❌ Possible Truncation: Ends with '**'")
    if last_line.endswith('\\'):
        errors.append(f"❌ Possible Truncation: Ends with backslash")
    if last_line.endswith('```'): # Could be ok, but if it's opening... actually closing is fine.
        pass 
    
    # Check if last line looks like a sentence cut off
    # Heuristic: Ends with no punctuation, and is not a header, and not a code block fence
    if len(last_line) > 0 and last_line[-1] not in ['.', '!', '?', ']', '}', '`', '"', "'", ')', '>']:
        # Exclude headers
        if not last_line.startswith('#'):
            errors.append(f"⚠️  Possible Truncation: Last line does not end with punctuation: '{last_line[-20:]}...'")

    return errors

def check_forbidden_terms(content):
    errors = []
    forbidden = [
        "English from V3",
        "Generate daily CFD lesson", 
        "Translate specific comments",
        "Here is the translation"
    ]
    for term in forbidden:
        if term in content:
            errors.append(f"❌ Forbidden Term Found: '{term}'")
    return errors

def validate_file(file_path):
    print(f"🔍 Checking {file_path}...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

    all_errors = []
    all_errors.extend(check_backtick_latex(content, file_path))
    all_errors.extend(check_code_blocks(content))
    all_errors.extend(check_truncation(content))
    all_errors.extend(check_forbidden_terms(content))

    if all_errors:
        for err in all_errors:
            print(f"  {err}")
        return False
    else:
        print(f"  ✅ Passed")
        return True

def main():
    args = parse_arguments()
    files = get_target_files(args)
    
    if not files:
        print("No files to validate. Usage: python3 validate_markdown.py --day 1 12")
        sys.exit(0)

    failed_count = 0
    for f in files:
        if not validate_file(f):
            failed_count += 1
    
    print("-" * 40)
    if failed_count > 0:
        print(f"🚨 Validation FAILED: {failed_count} files have issues.")
        sys.exit(1)
    else:
        print("✅ All files Passed Validation.")
        sys.exit(0)

if __name__ == "__main__":
    main()
