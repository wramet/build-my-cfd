import os
import subprocess
import sys
import re
from pathlib import Path

# ==========================================
# ⚙️ CONFIGURATION
# ==========================================

# 1. Point to the PARENT directory containing all modules
PARENT_ROOT = "/Users/woramet/Documents/th_new"

STYLE_GUIDE_PATH = "/Users/woramet/Documents/th_new/Obsidian_rule.md" 
LOG_FILE = "obsidian_recursive.log"

# CLI Configuration
CLI_COMMAND = "claude"
CLI_FLAGS = ["--dangerously-skip-permissions", "-p"]

# Limit context size to avoid token overflow
MAX_CONTEXT_CHARS = 300000 

# ==========================================

def load_style_guide():
    """Reads the style guide from the external markdown file."""
    path = Path(STYLE_GUIDE_PATH)
    if not path.exists():
        print(f"⚠️ Warning: Style guide not found at {path}. Using default minimal rules.")
        return "Use standard Markdown."
    
    try:
        return path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"⚠️ Error reading style guide: {e}")
        return "Use standard Markdown."

def get_restoration_prompt(target_filename, relevant_files_list, style_guide_text):
    """
    BRANCH A: RESTORATION MODE
    Used when .bak files ARE available. Focuses on merging lost data.
    """
    files_str = ", ".join(relevant_files_list)
    
    return f"""
**Role:** Senior Technical Editor & OpenFOAM Subject Matter Expert.

**Context:**
- **TARGET TO EDIT:** `{target_filename}` (This is the ONLY file you will change).
- **READ-ONLY REFERENCE:** `{files_str}` (Use these .bak files to find content).

**Task:** Refactor and Enrich `{target_filename}` by restoring details from backups.

**Instructions:**
1. **Source Analysis:** Read the provided `.bak` files to find technical details, equations, and code snippets that belong in `{target_filename}`.
2. **Content Restoration:** Rewrite `{target_filename}` to be a complete, high-quality technical note.
   - You MUST transfer valid OpenFOAM code and Math from the backups to the target.
   - **Language:** Explain in **Thai**. Keep technical terms in **English**.
   - Do NOT edit, output, or mention the `.bak` files in your final response. Focus 100% on the `.md` file.

**FORMATTING RULES (STRICT):**
---
{style_guide_text}
---

**Output Requirement:**
Produce the FULL, final content for `{target_filename}`.
"""

def get_synthesis_prompt(target_filename, style_guide_text):
    """
    BRANCH B: SYNTHESIS MODE
    Used when NO .bak files are available. Focuses on Theory & Best Practices.
    """
    return f"""
**Role:** Senior Technical Editor & OpenFOAM Subject Matter Expert.

**Context:**
- **TARGET TO EDIT:** `{target_filename}`
- **STATUS:** No source backup files are available. You must synthesize the technical content.

**Task:** Reconstruct and Expand `{target_filename}` using Standard Theory and Best Practices.

**Instructions:**
1. **Topic Analysis:** Analyze the existing headers and text in `{target_filename}` to understand the physics or solver (e.g., if "VOF" is mentioned, assume `interFoam`).
2. **Theoretical Reconstruction:**
   - If physics concepts are mentioned but lack math, **generate standard governing equations** (LaTeX).
   - **Language:** Explain concepts in **Thai**.
   - **Terminology:** Keep variable names and OpenFOAM terms in **English**.
3. **Code Reconstruction (Standard Only):**
   - Generate **standard OpenFOAM dictionary snippets** (e.g., `fvSchemes`, `boundary conditions`) relevant to the topic.
   - **ANNOTATION:** Mark all AI-generated code with `// NOTE: Synthesized by AI - Verify parameters`.
4. **Data Safety (CRITICAL):**
   - **DO NOT** invent simulation results, residuals, or specific values.
   - If results are needed, use this placeholder: `> **[MISSING DATA]**: Insert specific simulation results/graphs for this section.`

**FORMATTING RULES (STRICT):**
---
{style_guide_text}
---

**Output Requirement:**
Produce the FULL, final content for `{target_filename}`, THAI LANGUAGE ONLY.
"""

def extract_keywords(text):
    """Extract words to compare similarity."""
    words = re.findall(r'\w+', text.lower())
    return set(w for w in words if len(w) > 3)

def select_relevant_backups(md_file_path, bak_files, folder_path):
    """
    Selects .bak files relevant to the .md file based on keyword matching.
    """
    try:
        with open(md_file_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
            md_keywords = extract_keywords(md_content)
    except Exception:
        return bak_files 

    scored_files = []
    
    for bak_file in bak_files:
        bak_path = Path(folder_path) / bak_file
        try:
            with open(bak_path, 'r', encoding='utf-8') as f:
                content = f.read()
                bak_keywords = extract_keywords(content)
                common_words = md_keywords.intersection(bak_keywords)
                score = len(common_words)
                size = len(content)
                scored_files.append({'name': bak_file, 'score': score, 'size': size})
        except Exception:
            continue

    # Sort by relevance score
    scored_files.sort(key=lambda x: x['score'], reverse=True)

    selected_files = []
    current_size = 0
    
    for file_data in scored_files:
        if current_size + file_data['size'] < MAX_CONTEXT_CHARS:
            selected_files.append(file_data['name'])
            current_size += file_data['size']
        else:
            break
            
    return selected_files

def create_ignore_file(folder_path):
    """Creates a .claudeignore to prevent AI from reading garbage files."""
    ignore_path = Path(folder_path) / ".claudeignore"
    content = "*.png\n*.jpg\n*.jpeg\n*.pdf\n*.zip\n.DS_Store\n.git\n"
    try:
        with open(ignore_path, "w") as f:
            f.write(content)
    except Exception:
        pass 

def process_module(module_path, log_path, completed_paths, style_guide_content):
    """
    Walks through a specific module folder and processes files.
    """
    print(f"\n🚀 Entering Module: {module_path.name}")
    
    for current_root, dirs, files in os.walk(module_path):
        
        # 1. Identify Target Files (.md)
        md_files = sorted([f for f in files if f.endswith('.md')])
        # 2. Identify Reference Files (.bak)
        bak_files = sorted([f for f in files if f.endswith('.bak')])

        if not md_files:
            continue

        abs_current_path = str(Path(current_root).resolve())
        folder_name = Path(current_root).name

        if abs_current_path in completed_paths:
            # print(f"  ⏭️  Skipping completed folder: {folder_name}")
            continue

        print(f"  🔨 Processing Sub-folder: {folder_name}")
        create_ignore_file(abs_current_path)

        all_success = True
        
        for md_file in md_files:
            # === LOGIC BRANCHING START ===
            
            # Try to find relevant backups
            relevant_bak_files = select_relevant_backups(
                Path(abs_current_path) / md_file, 
                bak_files, 
                abs_current_path
            )
            
            # DECISION: Restoration OR Synthesis?
            if relevant_bak_files:
                # BRANCH A: Backups Found
                print(f"     👉 Target: {md_file} | Mode: RESTORATION ({len(relevant_bak_files)} backups)")
                final_prompt = get_restoration_prompt(md_file, relevant_bak_files, style_guide_content)
                current_batch = [md_file] + relevant_bak_files
            else:
                # BRANCH B: No Backups (Synthesis)
                print(f"     👉 Target: {md_file} | Mode: SYNTHESIS (No backups found)")
                final_prompt = get_synthesis_prompt(md_file, style_guide_content)
                current_batch = [md_file] # Only send the MD file
            
            # Execute Command
            cmd = [CLI_COMMAND] + CLI_FLAGS + [final_prompt] + current_batch

            try:
                result = subprocess.run(cmd, text=True, cwd=abs_current_path, capture_output=True)
                if result.returncode == 0:
                    print(f"        ✅ Success: {md_file} updated.")
                else:
                    print(f"        ❌ Failed: {result.stderr}")
                    all_success = False
            except Exception as e:
                print(f"        ❌ Error: {e}")
                all_success = False

        if all_success:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(abs_current_path + "\n")
            completed_paths.add(abs_current_path)

def main():
    try:
        parent_root = Path(PARENT_ROOT).resolve()
        log_path = Path(LOG_FILE).resolve()
    except Exception:
        sys.exit(1)

    print(f"🌟 Starting Global Smart Refactoring (Hybrid Mode)")
    print(f"📂 Parent Root: {parent_root}")
    
    if not parent_root.exists():
        print("❌ Parent root directory does not exist.")
        sys.exit(1)
        
    if not log_path.exists():
        log_path.touch()

    print("📜 Loading Style Guide...")
    style_guide_content = load_style_guide()

    # Load existing logs
    with open(log_path, 'r', encoding='utf-8') as f:
        completed_paths = set(line.strip() for line in f if line.strip())

    # 1. Get all items in the parent directory
    all_items = sorted(os.listdir(parent_root))

    # 2. Filter for directories only, ignore 'TBD'
    module_folders = []
    for item in all_items:
        full_path = parent_root / item
        if full_path.is_dir():
            if "TBD" in item:
                print(f"⛔ Ignoring TBD Folder: {item}")
            elif item.startswith("."):
                continue 
            else:
                module_folders.append(full_path)

    print(f"📋 Found {len(module_folders)} modules to process.")

    # 3. Loop through modules sequentially
    for module_path in module_folders:
        process_module(module_path, log_path, completed_paths, style_guide_content)

    print("\n🏁 Global Script Finished.")

if __name__ == "__main__":
    main()