import re
import sys

def check_file(filepath):
    issues = []
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')

    # 1. Backtick-wrapped LaTeX
    # Checking for `$$ or $$`
    if re.search(r'`\$\$', content) or re.search(r'\$\$`', content):
        issues.append("Backtick-wrapped Block Math")
    
    # 2. Malformed Callouts
    # Looking for > [!TYPE]Title (no space)
    if re.search(r'>\s*\[![A-Z]+\][^ \n]', content):
        issues.append("Malformed Callout (Missing space after type)")

    # 3. Unclosed Code Blocks
    # Count ``` occurrences
    code_block_markers = len(re.findall(r'^```', content, re.MULTILINE))
    if code_block_markers % 2 != 0:
        issues.append(f"Unbalanced Code Blocks ({code_block_markers})")

    # 5. Header Hierarchy
    # Find all headers
    headers = []
    for line in lines:
        match = re.match(r'^(#+)\s', line)
        if match:
            headers.append(len(match.group(1)))
    
    if headers:
        prev_level = 0 # H1 is level 1
        for h in headers:
            # Allow H1 as start. 
            # If prev is 0, h can be 1.
            # If prev is 1, h can be 1, 2.
            # If prev is 2, h can be 1, 2, 3.
            # Jump limit: h cannot be > prev_level + 1
            
            # Special case: sometimes we restart sections, so h < prev_level is fine.
            # We only care about h > prev_level + 1
            
            if prev_level == 0:
                if h != 1:
                     # Allow starting with H1 only
                     issues.append(f"Document starts with H{h} (Should be H1)")
            else:
                if h > prev_level + 1:
                    issues.append(f"Header Jump: H{prev_level} -> H{h}")
            
            prev_level = h

    return issues

files = [
    "daily_learning/2026-01-04.md",
    "daily_learning/2026-01-05.md",
    "daily_learning/2026-01-06.md",
    "daily_learning/2026-01-07.md",
    "daily_learning/2026-01-10.md",
    "daily_learning/2026-01-12.md"
]

for fpath in files:
    file_issues = check_file(fpath)
    if not file_issues:
        print(f"PASS: {fpath}")
    else:
        print(f"FAIL: {fpath} - {file_issues}")