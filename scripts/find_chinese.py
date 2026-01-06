
import os
import re

def find_chinese_chars(directory):
    # Regex for CJK characters and common CJK punctuation
    # \u4e00-\u9fff: CJK Unified Ideographs
    # \u3000-\u303f: CJK Symbols and Punctuation
    # \uff00-\uffef: Halfwidth and Fullwidth Forms
    chinese_pattern = re.compile(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]')
    
    found_issues = False

    print(f"Scanning {directory} for Chinese characters...")
    print("-" * 50)

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".md"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines):
                            if chinese_pattern.search(line):
                                print(f"File: {filepath}")
                                print(f"Line {i+1}: {line.strip()}")
                                print("-" * 20)
                                found_issues = True
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")

    if not found_issues:
        print("No Chinese characters found.")
    else:
        print("Scan complete. Please review the findings above.")

if __name__ == "__main__":
    find_chinese_chars("daily_learning")
