import sys
import os
import re

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 split_qc.py <file> <out_dir>")
        sys.exit(1)
        
    filepath = sys.argv[1]
    out_dir = sys.argv[2]
    
    if not os.path.exists(filepath):
        print(f"Error: File {filepath} not found")
        sys.exit(1)
        
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
        
    with open(filepath, 'r') as f:
        lines = f.readlines()
        
    current_section = []
    section_count = 0
    
    # Header for first section (before first ##)
    current_section = []
    
    for line in lines:
        if line.startswith("## "):
            # Save previous section if not empty (or even if empty, to maintain structure)
            if current_section or section_count == 0:
                out_name = os.path.join(out_dir, f"section_{section_count:02d}.md")
                with open(out_name, 'w') as out:
                    out.writelines(current_section)
                print(f"Saved {out_name} ({len(current_section)} lines)")
                section_count += 1
                current_section = []
            
            current_section.append(line)
        else:
            current_section.append(line)
            
    # Save last section
    if current_section:
        out_name = os.path.join(out_dir, f"section_{section_count:02d}.md")
        with open(out_name, 'w') as out:
            out.writelines(current_section)
        print(f"Saved {out_name} ({len(current_section)} lines)")

if __name__ == "__main__":
    main()
