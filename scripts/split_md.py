import os
import re
import sys

def split_markdown(file_path, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    current_file = None
    file_counter = 0
    
    # Pre-read to catch frontmatter
    if len(lines) > 0 and lines[0].strip() == '---':
        section_name = "00_frontmatter"
        current_path = os.path.join(output_dir, f"{section_name}.md")
        current_file = open(current_path, 'w', encoding='utf-8')
    else:
        file_counter = 1
        section_name = "01_intro"
        current_path = os.path.join(output_dir, f"{section_name}.md")
        current_file = open(current_path, 'w', encoding='utf-8')

    for line in lines:
        if re.match(r'^#\s|^##\s', line):
            if current_file:
                current_file.close()
            
            # If we were in frontmatter (counter 0), next is 1. If we were in 1, next is 2.
            if file_counter == 0:
                file_counter = 1
            else:
                file_counter += 1
                
            header_text = line.strip().replace('#', '').strip()
            safe_text = re.sub(r'[^\w\s-]', '', header_text).strip().lower()
            safe_text = re.sub(r'[-\s]+', '_', safe_text)
            filename = f"{file_counter:02d}_{safe_text}.md"
            current_path = os.path.join(output_dir, filename)
            current_file = open(current_path, 'w', encoding='utf-8')
            
        if current_file:
            current_file.write(line)
            
    if current_file:
        current_file.close()
    print(f"Split {file_path} into {output_dir}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python split_md.py <input_file> <output_dir>")
        sys.exit(1)
    split_markdown(sys.argv[1], sys.argv[2])
