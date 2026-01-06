import os
import re

def split_markdown(file_path, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    current_file = None
    file_counter = 1
    
    # Pre-read to catch frontmatter
    if lines[0].strip() == '---':
        section_name = "00_frontmatter"
        current_path = os.path.join(output_dir, f"{section_name}.md")
        current_file = open(current_path, 'w', encoding='utf-8')
    else:
        section_name = "01_intro"
        current_path = os.path.join(output_dir, f"{section_name}.md")
        current_file = open(current_path, 'w', encoding='utf-8')

    for line in lines:
        if re.match(r'^#\s|^##\s', line):
            if current_file:
                current_file.close()
            header_text = line.strip().replace('#', '').strip()
            safe_text = re.sub(r'[^\w\s-]', '', header_text).strip().lower()
            safe_text = re.sub(r'[-\s]+', '_', safe_text)
            filename = f"{file_counter:02d}_{safe_text}.md"
            current_path = os.path.join(output_dir, filename)
            current_file = open(current_path, 'w', encoding='utf-8')
            file_counter += 1
            
        if current_file:
            current_file.write(line)
            
    if current_file:
        current_file.close()
    print(f"Split completed into {file_counter-1} files")

split_markdown('daily_learning/2026-01-12.md', 'daily_learning/temp_qc/day12')
