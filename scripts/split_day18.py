import os
import re

def split_markdown_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    headers_map = [
        ("# Day 18: VTK Mesh Output - Section 1: Theory", "section_01.md"),
        ("## 3. Section 2: OpenFOAM Reference", "section_02.md"),
        ("# 4. Section 3: Class Design", "section_03.md"),
        ("# Section 4: Implementation", "section_04.md"),
        ("# 6. Section 5: Build & Test", "section_05.md"),
        ("# 7. Section 6: Concept Checks", "section_06.md"),
        ("# 8. References & Related Days", "section_07.md")
    ]
    
    section_dict = {
        "section_00.md": []
    }
    
    current_key = "section_00.md"
    
    for line in lines:
        matched = False
        for header, filename in headers_map:
            if line.strip().startswith(header):
                current_key = filename
                if current_key not in section_dict:
                    section_dict[current_key] = []
                matched = True
                break
        
        section_dict[current_key].append(line)

    output_dir = "/Users/woramet/Documents/th_new/daily_learning/temp_qc"
    os.makedirs(output_dir, exist_ok=True)

    for filename, content in section_dict.items():
        with open(os.path.join(output_dir, filename), 'w', encoding='utf-8') as f:
            f.writelines(content)
            print(f"Created {filename} with {len(content)} lines")

split_markdown_file("/Users/woramet/Documents/th_new/daily_learning/Phase_02_Geometry_Mesh/18.md")
