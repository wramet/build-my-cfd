import sys
import re

def polish_callouts(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    title = "Concept Check"
    
    # 1. Extract Title
    if len(lines) > 0 and lines[0].strip().startswith("##"):
        # ex: ## 6.1 คำถาม: Title
        header_match = re.search(r'##\s*\d+\.(\d+)\s*(.*)', lines[0])
        if header_match:
            num = header_match.group(1)
            raw_title = header_match.group(2).replace('คำถาม:', '').strip()
            title = f"Concept Check {num}: {raw_title}"
        else:
             # Try simple match
             title = lines[0].replace('#', '').strip()
        
        # Add Question Block
        new_lines.append(f"> [!QUESTION] {title}\n")
        new_lines.append(">\n")
        new_lines.append("> > [!SUCCESS]- เฉลย (คลิกเพื่ออ่านคำตอบ)\n")
    
    # 2. Indent Content
    for line in lines[1:]:
        if line.strip() == "":
            new_lines.append("> >\n")
        else:
            new_lines.append(f"> > {line}")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python polish_callouts.py <file>")
        sys.exit(1)
    polish_callouts(sys.argv[1])
