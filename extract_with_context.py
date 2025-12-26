import os
import re
import hashlib
import json

def get_context(content, start_index, end_index):
    # Search backwards for Header (up to 2000 chars)
    search_start = max(0, start_index - 2000)
    pre_text = content[search_start:start_index]
    
    # Find all headers in pre_text
    # (?m)^#+\s+(.*)$ matches headers at start of lines
    headers = list(re.finditer(r'(?m)^#+\s+(.*)$', pre_text))
    
    header = "No Header Found"
    if headers:
        # Take the last one found (nearest to the diagram)
        header = headers[-1].group(1).strip()

    # Search forwards for Caption (up to 500 chars)
    post_text = content[end_index:min(len(content), end_index + 500)]
    caption_match = re.search(r'(?m)^>\s*\*\*Figure.*$', post_text)
    caption = "No Caption Found"
    if caption_match:
        caption = caption_match.group(0).strip()
    
    return header, caption

def process_files():
    root_dir = "."
    diagrams = {} # Map hash -> {id: str, content: str, instances: list}
    
    # Regex for finding mermaid blocks
    # Captures: 0: Full match, 1: Content
    mermaid_pattern = re.compile(r'^```mermaid\n(.*?)```', re.MULTILINE | re.DOTALL)

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Filter directories
        dirnames[:] = [d for d in dirnames if d.startswith("MODULE_") or (dirpath == root_dir and d.startswith("MODULE_")) or (dirpath != root_dir)]
        
        # Determine if we are in a valid path (start with MODULE_ or inside one)
        rel_path = os.path.relpath(dirpath, root_dir)
        if rel_path != "." and not rel_path.startswith("MODULE_") and not any(part.startswith("MODULE_") for part in rel_path.split(os.sep)):
             continue

        for filename in filenames:
            if filename.endswith(".bak"):
                continue
            
            if not filename.endswith(".md"): # Assuming we only look at md files, though prompt implies 'Read each file' usually implies markdown in this context
                continue

            file_path = os.path.join(dirpath, filename)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                print(f"Skipping {file_path}: {e}")
                continue

            new_content = []
            last_pos = 0
            modified = False
            
            # Use finditer to process matches
            matches = list(mermaid_pattern.finditer(content))
            
            if not matches:
                continue

            print(f"Processing {file_path}...")

            for match in matches:
                start, end = match.span()
                diagram_code = match.group(1)
                
                # Deduplicate
                content_hash = hashlib.md5(diagram_code.encode('utf-8')).hexdigest()
                dia_id = f"DIA_{content_hash[:8]}" # Short hash
                
                header, caption = get_context(content, start, end)
                
                if dia_id not in diagrams:
                    diagrams[dia_id] = {
                        "id": dia_id,
                        "content": diagram_code,
                        "instances": []
                    }
                
                diagrams[dia_id]["instances"].append({
                    "file": file_path,
                    "header": header,
                    "caption": caption
                })

                # Append text before match
                new_content.append(content[last_pos:start])
                # Append placeholder
                new_content.append(f"<!-- MERMAID_PLACEHOLDER: {dia_id} -->")
                last_pos = end
                modified = True

            new_content.append(content[last_pos:])
            
            if modified:
                final_content = "".join(new_content)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(final_content)

    # Write staging.md
    with open("staging.md", "w", encoding='utf-8') as f:
        for dia_id, data in diagrams.items():
                        f.write(f"<<<< ID: {dia_id} >>>>\n")
                        f.write(data['content']) 
                        f.write("\n<<<< END >>>>\n\n")
    # Write mapping.json
    with open("mapping.json", "w", encoding='utf-8') as f:
        json.dump(diagrams, f, indent=2)

    print("Extraction complete. staging.md and mapping.json created.")

if __name__ == "__main__":
    process_files()
