import sys
import re

def fix_thai_spacing(text):
    # Fix Left: English -> Thai
    # Example: wordภาษา -> word ภาษา
    text = re.sub(r'([a-zA-Z0-9])([\u0E00-\u0E7F])', r'\1 \2', text)
    
    # Fix Right: Thai -> English
    # Example: ภาษาword -> ภาษา word
    text = re.sub(r'([\u0E00-\u0E7F])([a-zA-Z0-9])', r'\1 \2', text)
    
    return text

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 auto_fix.py <file>")
        sys.exit(1)
        
    filepath = sys.argv[1]
    
    with open(filepath, 'r') as f:
        content = f.read()
        
    fixed = fix_thai_spacing(content)
    
    with open(filepath, 'w') as f:
        f.write(fixed)
        
    print(f"✅ Fixed spacing in {filepath}")

if __name__ == "__main__":
    main()
