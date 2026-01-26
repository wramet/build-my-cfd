import os
import re

def split_markdown(file_path, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Split by ## headers, keeping the headers in the sections
    sections = re.split(r'(?m)^(?=## )', content)
    
    for i, section in enumerate(sections):
        output_file = os.path.join(output_dir, f'section_{i:02d}.md')
        with open(output_file, 'w') as f:
            f.write(section)
            if not section.endswith('\n'):
                f.write('\n')
        print(f"Created {output_file}")

split_markdown('daily_learning/Phase_02_Geometry_Mesh/15.md', 'daily_learning/temp_qc/')
