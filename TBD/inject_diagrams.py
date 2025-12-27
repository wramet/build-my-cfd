import os
import re
import argparse

# Configuration
TARGET_DIR_PREFIX = "MODULE_"
IGNORE_EXTENSIONS = (".bak", ".pre_prompt.bak")
STAGING_FILE = "staging_reviewed.md"

def get_files_to_process(root_dir):
    files_to_process = []
    try:
        entries = os.listdir(root_dir)
    except OSError as e:
        print(f"Error accessing root directory: {e}")
        return []

    for entry in entries:
        full_path = os.path.join(root_dir, entry)
        if os.path.isdir(full_path) and entry.startswith(TARGET_DIR_PREFIX):
            for root, _, files in os.walk(full_path):
                for file in files:
                    if file.endswith(".md") and not file.endswith(IGNORE_EXTENSIONS):
                        files_to_process.append(os.path.join(root, file))
    return files_to_process

def parse_staging_file(filepath):
    diagrams = {}
    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found.")
        return diagrams
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Regex to extract ID and Content
    # Format: <<<< ID: DIA_xxxxxx >>>>\nCONTENT\n<<<< END >>>>
    pattern = re.compile(r'<<<< ID: (.*?) >>>>\n(.*?)<<<< END >>>>', re.DOTALL)
    matches = pattern.finditer(content)
    
    for match in matches:
        uid = match.group(1).strip()
        code = match.group(2).strip()
        diagrams[uid] = code
        
    return diagrams

def inject_diagrams(dry_run=False):
    print(f"Reading diagrams from {STAGING_FILE}...")
    diagrams = parse_staging_file(STAGING_FILE)
    if not diagrams:
        print("No diagrams found in staging file or file is empty.")
        return
    print(f"Loaded {len(diagrams)} unique diagrams.")

    files = get_files_to_process(".")
    
    # Corrected Regex for the placeholders used by extract_with_context.py
    placeholder_pattern = re.compile(r'<!-- MERMAID_PLACEHOLDER: (.*?) -->')
    
    files_modified = 0
    placeholders_replaced = 0
    missing_ids = set()

    print(f"Scanning {len(files)} files...")

    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Skipping file due to read error: {file_path} ({e})")
            continue
            
        new_content = content
        matches = list(placeholder_pattern.finditer(content))
        
        if not matches:
            continue

        replacements = []
        file_has_changes = False
        
        for match in matches:
            uid = match.group(1).strip()
            
            if uid in diagrams:
                # Wrap content in mermaid block with triple backticks
                # Ensure we don't double wrap if the staging content already has backticks (unlikely but safe)
                dia_content = diagrams[uid]
                mermaid_block = f"```mermaid\n{dia_content}\n```"
                
                replacements.append((match.start(), match.end(), mermaid_block))
                placeholders_replaced += 1
                file_has_changes = True
            else:
                missing_ids.add(uid)
        
        if file_has_changes and not dry_run:
            # Apply replacements in reverse order to preserve indices
            replacements.sort(key=lambda x: x[0], reverse=True)
            for start, end, repl in replacements:
                new_content = new_content[:start] + repl + new_content[end:]
                
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            files_modified += 1
        elif file_has_changes and dry_run:
            files_modified += 1 # Count for report

    print("-" * 30)
    if dry_run:
        print("DRY RUN COMPLETE (No files changed)")
    else:
        print("INJECTION COMPLETE")
        
    print(f"Files to be modified: {files_modified}")
    print(f"Placeholders matched: {placeholders_replaced}")
    
    if missing_ids:
        print(f"WARNING: The following IDs were found in files but not in {STAGING_FILE}:")
        for mid in missing_ids:
            print(f"  - {mid}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inject processed diagrams back into Markdown files.")
    parser.add_argument("--dry-run", action="store_true", help="Scan files without making changes")
    args = parser.parse_args()
    
    inject_diagrams(dry_run=args.dry_run)