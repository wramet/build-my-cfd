import os
import re

directories = [
    'daily_learning/Phase_01_Foundation_Theory/',
    'daily_learning/Phase_02_Geometry_Mesh/'
]

for directory in directories:
    files = sorted([f for f in os.listdir(directory) if f.endswith('.md') and not f.startswith('phase_') and not f.startswith('backup_')])
    for filename in files:
        filepath = os.path.join(directory, filename)
        with open(filepath, 'r') as f:
            content = f.read(1000)
            if content.startswith('---'):
                end_index = content.find('---', 3)
                if end_index != -1:
                    frontmatter = content[3:end_index]
                    print(f"FILE: {filepath}\n{frontmatter}\n{'-'*20}")
                else:
                    print(f"FILE: {filepath}\nNO CLOSING ---\n{'-'*20}")
            else:
                print(f"FILE: {filepath}\nNO FRONTMATTER\n{'-'*20}")
