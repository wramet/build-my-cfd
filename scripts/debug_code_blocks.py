import sys

def find_unclosed_block(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()

    stack = []
    
    print(f"--- Analyzing {filename} ---")
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        
        # Check for code block fence
        # We need to handle ` ``` ` inside blockquotes ` > `
        # But our rule is strict: balanced ``` counts.
        # Let's just look for ``` sequences.
        
        # Simple heuristic matching the 'grep' logic which found odd numbers
        # The grep was `grep -c '^```'` mostly, or just searching generally.
        # Let's refine: A block starts with ``` and ends with ```
        
        # Simplest check: Just find the "odd" one.
        # This means we assume strict alternation.
        
        # We need to filter out inline code `code` (single backtick) - regex needed?
        # The issue is usually triple backticks.
        
        if "```" in line:
            # Check if it's potentially an inline code block misuse or a proper fence
            # If it's at the start of the line or after > 
            
            # Simple toggle logic
            if not stack:
                stack.append((i + 1, line.strip()))
            else:
                stack.pop()
    
    if stack:
        print(f"❌ Unclosed block potentially starting at:")
        for lineno, content in stack:
            print(f"  Line {lineno}: {content}")
    else:
        print("✅ Balanced blocks (by simple toggle count).")

if __name__ == "__main__":
    for f in sys.argv[1:]:
        find_unclosed_block(f)
