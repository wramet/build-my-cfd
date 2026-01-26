#!/usr/bin/env python3
import sys
import re
import os

def check_file(filepath):
    """
    Validates a single markdown file against strict QC rules.
    Returns a list of error messages.
    """
    errors = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        return [f"Could not read file: {e}"]

    # State variables
    in_code_block = False
    code_block_lang = None
    line_num = 0
    header_level = 0
    
    # Global counters
    backtick_count = 0
    
    for line in lines:
        line_num += 1
        stripped = line.strip()
        
        # 1. Check for Code Blocks
        if line.lstrip().startswith("```"):
            backtick_count += 1
            if in_code_block:
                in_code_block = False
                code_block_lang = None
            else:
                in_code_block = True
                # Check for language specification
                if len(stripped) > 3:
                    code_block_lang = stripped[3:].strip()
                else:
                    errors.append(f"Line {line_num}: Code block starts without language specification (e.g., ```cpp)")

        # 2. Checks inside Code Blocks
        if in_code_block:
            # Check for Shebang indentation
            if "bin/bash" in line or "bin/sh" in line:
                if line.startswith(" ") or line.startswith("\t"):
                   errors.append(f"Line {line_num}: Indented shebang found. Remove indentation for scripts to work.")
            
            # Check for LaTeX in code comments (C++ double slash)
            if "//" in line and "$$" in line:
                errors.append(f"Line {line_num}: LaTeX '$$' delimiter found inside code comment. Use plain text or single '$' with care.")

        if not in_code_block:
            # 3. Headers
            if line.startswith("#"):
                # Header attributes check
                if re.search(r'\{#.*\}', line):
                    errors.append(f"Line {line_num}: Header contains ID attribute {{#...}}. Remove it for Obsidian compatibility.")
                
                # Hierarchy check (simple)
                current_level = len(line.split(' ')[0])
                if current_level > 6: # Markdown only supports up to h6
                     pass 
                # (Can add logic to check for skipped levels if needed)

            # 4. LaTeX Checks
            # Backtick-wrapped LaTeX
            if re.search(r'`\$\$', line) or re.search(r'\$\$`', line):
                 errors.append(f"Line {line_num}: Backticks found around Display Math ($$). Remove backticks.")
            if re.search(r'`\$[^\n`]+\$`', line):
                 # This is tricky because `$var` in code is fine.
                 # We assume inline math starts with $ and has no spaces immediately after.
                 pass 

            # Mismatched delimiters in a single line (heuristic)
            # Count $ but ignore \$
            # This is hard to do perfectly with regex line-by-line due to multi-line math.
            
            # Check for specific bad patterns
            if "\\alpha$_" in line:
                errors.append(f"Line {line_num}: Incorrect LaTeX subscript format '\\alpha$_'. Should be '$\\alpha_'.")
            if "T_sat" in line and "$" not in line:
                # Heuristic: T_sat outside math mode
                # errors.append(f"Line {line_num}: 'T_sat' found without math delimiters. Use '$T_{{sat}}$'.")
                pass

            # 5. Image/Link Checks
            if "![" in line and "](" in line:
                 if "http" in line or "/abs/" in line:
                     errors.append(f"Line {line_num}: External or absolute image link path found. Use Obsidian '![[image.png]]' syntax.")

    # Final File-Level Checks
    if backtick_count % 2 != 0:
        errors.append(f"File Error: Unbalanced code blocks (found {backtick_count} delimiters).")

    return errors

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 qc_validator.py <file1.md> [file2.md ...]")
        sys.exit(1)

    has_errors = False
    print("--------------------------------------------------")
    print("  OpenFOAM Content QC Validator")
    print("--------------------------------------------------")

    for filepath in sys.argv[1:]:
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            continue
            
        print(f"Checking: {os.path.basename(filepath)}...")
        errors = check_file(filepath)
        
        if errors:
            has_errors = True
            print(f"  FAILED ({len(errors)} errors):")
            for err in errors:
                print(f"    - {err}")
        else:
            print("  PASSED")
    
    print("--------------------------------------------------")
    if has_errors:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
