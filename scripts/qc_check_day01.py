import glob
import re
import os

files = sorted(glob.glob("daily_learning/temp_qc/section_*.md"))

print(f"Checking {len(files)} files...")

for fpath in files:
    fname = os.path.basename(fpath)
    with open(fpath, 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # 1. Balanced Code Blocks
    backticks = content.count('```')
    if backticks % 2 != 0:
        print(f"[{fname}] UNBALANCED CODE BLOCKS: {backticks}")

    # 2. Nested LaTeX ($ inside $$)
    # Simple check: line acts weird?
    # We look for $$ ... $ ... $$ on a single line
    for i, line in enumerate(lines):
        # Regex: $$ followed by something, then $ not at end?
        # A line with '$$' and more than 2 '$' might be suspicious?
        dollar_count = line.count('$')
        if '$$' in line:
            # If line is exactly '$$', it's fine.
            if line.strip() == '$$':
                continue
            # If line is '$$ math $$', count is 4.
            # If line is '$$ math $ math $$', count is 5?
            # If line is '$$ \text{...} $$', count is 4.
            pass
        
    # 3. Text Underscores
    in_code_block = False
    for i, line in enumerate(lines):
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            continue
        
        if in_code_block:
            continue

        if '_' in line:
            # Skip if URL
            if 'http' in line: continue
            # Skip if line has $ (assume math)
            if '$' in line: continue
            # Skip if line has ` (assume inline code)
            if '`' in line: continue
            # Skip if escaped \_
            # Check for unescaped _ [a-zA-Z]_[a-zA-Z]
            if re.search(r'[a-zA-Z]_[a-zA-Z]', line):
                print(f"[{fname}] L{i+1}: Suspicious Underscore: {line.strip()}")

    # 4. Mermaid Syntax
    # Check for < > in ClassDiagram
    in_mermaid = False
    for i, line in enumerate(lines):
        if 'classDiagram' in line:
            in_mermaid = True
        if in_mermaid and '```' in line and 'mermaid' not in line:
            in_mermaid = False
        
        if in_mermaid:
            if '<' in line or '>' in line:
                # exclude inheritance <|-- 
                # exclude composition *--
                # check for generic <Type>
                clean_line = line.replace('<|--', '').replace('*--', '').replace('o--', '').replace('<|..', '')
                if '<' in clean_line or '>' in clean_line:
                     print(f"[{fname}] L{i+1}: Mermaid Generics? : {line.strip()}")
