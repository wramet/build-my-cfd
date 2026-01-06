import re
import os
import sys

def polish_content(content):
    # 1. Regex replacements (Global)
    
    # Backticks around math `$...$` -> $...$
    # We use a loop to handle multiple occurrences on one line safely? 
    # Actually regex handles it.
    content = re.sub(r'`(\$[^`\n]+\$)`', r'\1', content)

    # Vector Notation: \vec{X} -> \mathbf{X}
    vectors = ['U', 'g', 'n', 'S', 'r', 'x', 'V', 'A', 'd', 'b', 'p', 'z', 'q']
    for v in vectors:
        content = re.sub(r'\\vec\{' + v + r'\}', r'\\mathbf{' + v + '}', content)
        content = re.sub(r'\\vec\s+' + v + r'(?![a-zA-Z])', r'\\mathbf{' + v + '}', content)

    # Text Subscripts
    common_subs = ['liquid', 'gas', 'vapor', 'sat', 'interface', 'wall', 'inlet', 'outlet', 'total', 'eff', 'visc', 'lam', 'turb', 'owner', 'neighbour', 'neigh']
    for sub in common_subs:
        content = re.sub(r'_\{' + sub + r'\}', r'_{\\text{' + sub + '}}', content)
        content = re.sub(r'_' + sub + r'(?![a-zA-Z])', r'_{\\text{' + sub + '}}', content)

    # Internal Links
    day_map = {
        "01": "Day 01: Governing Equations",
        "02": "Day 02: Finite Volume Method Basics",
        "03": "Day 03: Spatial Discretization Schemes",
        "04": "Day 04: Temporal Discretization",
        "05": "Day 05: Mesh Topology",
        "06": "Day 06: Boundary Conditions Theory",
        "07": "Day 07: Linear Algebra (LDU)",
        "08": "Day 08: Iterative Solvers (PCG & PBiCGStab)",
        "09": "Day 09: Pressure-Velocity Coupling (SIMPLE, PISO, Rhie-Chow)",
        "10": "Day 10: Two-Phase Fundamentals (VOF & MULES)",
        "11": "Day 11: Phase Change Theory (Lee Model & Linearization)",
        "12": "Day 12: Phase 1 Review & Integration"
    }
    for num, title in day_map.items():
        content = content.replace(f"(Day {num})", f"([[{title}|Day {num}]])")
        content = content.replace(f"from Day {num}", f"from [[{title}|Day {num}]]")
        content = content.replace(f"จาก Day {num}", f"จาก [[{title}|Day {num}]]")
        content = content.replace(f"ใน Day {num}", f"ใน [[{title}|Day {num}]]")

    # 2. Stateful Line Processing (Callouts & Indentation)
    lines = content.splitlines()
    new_lines = []
    in_concept_check = False
    
    for line in lines:
        # Check start of Concept Check
        # Trigger: ### ... Concept Check ...
        # Exclude ## Headers (which are section headers)
        # Allow optional emojis, bold, whitespace
        if re.match(r'^###\s*.*?(Concept Check|คำถาม|\d+\.\d+\s*คำถาม)', line, re.IGNORECASE):
            in_concept_check = True
            
            # Extract Title
            title_text = line.replace('###', '').strip()
            # Clean up "6.1 คำถาม:" to just "Concept Check 6.1:" if possible, or keep as is.
            # User example: "> [!QUESTION] Concept Check 1: ..."
            # We'll use the raw text but wrap it.
            
            # If line has "คำถาม", let's make it look like "Concept Check"
            if "คำถาม" in title_text:
                # Try to preserve numbering
                num_match = re.search(r'(\d+(\.\d+)?)', title_text)
                num = num_match.group(1) if num_match else ""
                clean_title = title_text
            else:
                clean_title = title_text

            new_lines.append(f"> [!QUESTION] {clean_title}")
            new_lines.append(">")
            new_lines.append("> > [!SUCCESS]- เฉลย (คลิกเพื่ออ่านคำตอบ)")
            continue
            
        # Check end of Concept Check (Any next Header)
        if in_concept_check and re.match(r'^#+\s', line):
            in_concept_check = False
            # proceed to process this line normally
        
        # Process Content
        if in_concept_check:
            if line.strip() == "":
                new_lines.append("> >")
            else:
                new_lines.append(f"> > {line}")
        else:
            new_lines.append(line)

    return "\n".join(new_lines)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python polish_obsidian.py <file_path>")
        sys.exit(1)
        
    file_path = sys.argv[1]
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    new_content = polish_content(content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
