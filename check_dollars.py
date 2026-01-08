
import re

def check_balance(file_path):
    with open(file_path, 'r') as f:
        lines_orig = f.readlines()
    
    content = "".join(lines_orig)
    
    # Identify code blocks to exclude them
    code_block_ranges = []
    for m in re.finditer(r'```.*?```', content, flags=re.DOTALL):
        code_block_ranges.append(m.span())
    
    def is_in_code_block(pos):
        for start, end in code_block_ranges:
            if start <= pos < end:
                return True
        return False

    total_dollars = 0
    unbalanced_lines = []
    
    current_pos = 0
    for line_num, line in enumerate(lines_orig, 1):
        line_dollars = 0
        for i, char in enumerate(line):
            if char == '$' and not is_in_code_block(current_pos + i):
                line_dollars += 1
                total_dollars += 1
        
        # Note: this check per line is only valid for inline math or 
        # single-line block math. Multi-line block math will flag 2 lines.
        # But if total is odd, we have a problem.
        current_pos += len(line)

    print(f"Total $ outside code blocks: {total_dollars}")
    if total_dollars % 2 != 0:
        print("RESULT: UNBALANCED")
    else:
        print("RESULT: BALANCED")

check_balance('daily_learning/2026-01-12.md')
