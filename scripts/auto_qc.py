#!/usr/bin/env python3
import sys
import re

def auto_qc(file_path):
    print(f"🔍 Running Auto-QC on {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.readlines()
        
    fixed_content = []
    code_block_open = False
    
    # regex for H1 that should be H2 (exclude first line or Day title)
    # Assume first line is Title.
    
    for i, line in enumerate(content):
        # 1. Header Hierarchy Fix
        # Change "# Section X" inside body to "## Section X"
        # But keep "# Day XX" as is (usually at top)
        if line.strip().startswith("# Section") or (line.strip().startswith("# Day") and i > 5):
            # Downgrade to H2
            line = "#" + line
            print(f"  Fixed Header at line {i+1}: {line.strip()}")
            
        # 2. Track Code Blocks for Bleeding Check
        if line.strip().startswith("```"):
            code_block_open = not code_block_open
            
        fixed_content.append(line)

    # 3. Check for Bleeding Code Block at end
    if code_block_open:
        print("🚨 CRITICAL: Bleeding Code Block detected at end of file!")
        print("  Auto-fixing: Appending ```")
        fixed_content.append("\n```\n")
    
    # 4. Check for Truncation (EOF Marker) - Optional since generate_v3 does it
    # But we can verify.
    if "``" not in "".join(fixed_content[-5:]):
         print("⚠️  Warning: EOF Marker `` not found at very end.")
         
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(fixed_content)
        
    print("✅ Auto-QC Complete.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 auto_qc.py <file_path>")
        sys.exit(1)
    
    auto_qc(sys.argv[1])
