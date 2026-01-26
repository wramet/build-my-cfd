
import os
import re

def split_day19():
    source_file = "daily_learning/Phase_02_Geometry_Mesh/19.md"
    output_dir = "daily_learning/temp_qc"
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Clear existing files
    for f in os.listdir(output_dir):
        os.remove(os.path.join(output_dir, f))
        
    with open(source_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    current_section = 0
    current_content = []
    
    # Section breakpoints (Regex patterns)
    section_patterns = [
        (r"^## Section 1: Theory", 1),
        (r"^# 3. Section 2: OpenFOAM Reference", 2),
        (r"^# 4. Section 3: Class Design", 3),
        (r"^# 5. Section 4: Implementation", 4),
        (r"^## 6.1 CMake Build System", 5) # Treating this as Section 5 start
    ]
    
    def get_section_id(line):
        for pattern, sec_id in section_patterns:
            if re.match(pattern, line):
                return sec_id
        return None

    for line in lines:
        sec_id = get_section_id(line)
        if sec_id is not None:
            # Write current buffer to file
            filename = f"section_{current_section:02d}.md"
            with open(os.path.join(output_dir, filename), 'w', encoding='utf-8') as out:
                out.writelines(current_content)
            
            # Reset for next section
            current_section = sec_id
            current_content = []
        
        current_content.append(line)
        
    # Write last section
    filename = f"section_{current_section:02d}.md"
    with open(os.path.join(output_dir, filename), 'w', encoding='utf-8') as out:
        out.writelines(current_content)
        
    print(f"Split Day 19 into {current_section + 1} sections.")

if __name__ == "__main__":
    split_day19()
