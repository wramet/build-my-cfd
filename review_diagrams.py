import json
import os
import subprocess
import math
import re

# ==========================================
# ⚙️ CONFIGURATION
# ==========================================

MAPPING_FILE = "mapping.json"
OUTPUT_FILE = "staging_reviewed.md"
BATCH_SIZE = 10 # Reduced batch size for safety

# CLI Configuration
CLI_COMMAND = "claude"
CLI_FLAGS = ["--dangerously-skip-permissions", "-p"]

# ==========================================

def load_mapping():
    if not os.path.exists(MAPPING_FILE):
        print(f"❌ Error: {MAPPING_FILE} not found. Run extract_with_context.py first.")
        return None
    with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_existing_ids():
    """Reads the output file to find IDs that are already processed."""
    if not os.path.exists(OUTPUT_FILE):
        return set()
    
    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all IDs
    ids = re.findall(r'<<<< ID: (.*?) >>>>', content)
    return set(ids)

def generate_prompt_with_data(batch_items):
    """
    Constructs the prompt instructions AND the data in one single string.
    """
    prompt_header = """
**Role:** Mermaid Diagram Expert & OpenFOAM Technical Editor.

**Task:** 
Review the following batch of Mermaid diagrams.

**Instructions:**
1. **Syntax Check:** Ensure the Mermaid code is valid. Fix any syntax errors.
2. **Logic Review:** Use the provided *Context* (Header/Caption) to verify if the diagram makes sense. 
3. **Styling:** Improve the layout (e.g., use subgraphs, adjust direction LR/TD) if it improves clarity.
4. **Consistency:** Keep classDefs if they seem standard, or improve them.

**Output Format (STRICT):**
Return ALL diagrams in the batch using this EXACT format:

<<<< ID: DIA_xxxxxx >>>>
[Your Improved Mermaid Code Here]
<<<< END >>>>

NO conversational text. NO markdown fences around the blocks. Just the blocks.

**DATA TO PROCESS:**
"""
    data_str = ""
    for item in batch_items:
        dia_id = item['id']
        content = item['content']
        instances = item['instances']
        
        # Context summary
        context_str = ""
        for idx, inst in enumerate(instances):
            context_str += f"  - Location {idx+1}:\n"
            context_str += f"    File: {inst['file']}\n"
            context_str += f"    Header: {inst['header']}\n"
            context_str += f"    Caption: {inst['caption']}\n"

        data_str += f"--- START ITEM: {dia_id} ---\n"
        data_str += f"CONTEXT:\n{context_str}\n"
        data_str += f"CURRENT MERMAID CODE:\n{content}\n"
        data_str += f"--- END ITEM ---\n\n"
    
    return prompt_header + "\n" + data_str

def clean_ai_response(response_text):
    """
    Extracts only the valid blocks from the AI response.
    Ignores chatty introductions.
    """
    pattern = re.compile(r'(<<<< ID: .*? >>>>\n.*?<<<< END >>>>)', re.DOTALL)
    matches = pattern.findall(response_text)
    return "\n\n".join(matches)

def process_batch(batch_items, batch_index):
    # Embed data directly into the prompt string
    full_prompt = generate_prompt_with_data(batch_items)
    
    cmd = [CLI_COMMAND] + CLI_FLAGS + [full_prompt]
    
    print(f"  🤖 Sending Batch {batch_index} ({len(batch_items)} items) to AI...")
    
    try:
        # Run the command
        result = subprocess.run(cmd, text=True, capture_output=True)
        
        if result.returncode != 0:
            print(f"  ❌ Batch {batch_index} Failed: {result.stderr}")
            return None
        
        # Clean the output immediately
        cleaned_output = clean_ai_response(result.stdout)
        
        if not cleaned_output:
            print(f"  ⚠️ Warning: Batch {batch_index} returned no valid blocks. Raw output length: {len(result.stdout)}")
            # print(f"DEBUG RAW: {result.stdout[:200]}...")
            return None

        return cleaned_output

    except Exception as e:
        print(f"  ❌ Error running CLI: {e}")
        return None

def main():
    print("🚀 Starting Diagram Review Process (Resumable Mode)...")
    
    data = load_mapping()
    if not data:
        return

    # Filter out already processed diagrams
    existing_ids = get_existing_ids()
    print(f"ℹ️  Found {len(existing_ids)} already processed diagrams.")

    all_diagrams = list(data.values())
    
    # Only process diagrams that are NOT in the existing set
    pending_diagrams = [d for d in all_diagrams if d['id'] not in existing_ids]
    
    if not pending_diagrams:
        print("✅ All diagrams have been processed! No new work needed.")
        return

    total_diagrams = len(pending_diagrams)
    total_batches = math.ceil(total_diagrams / BATCH_SIZE)
    
    print(f"📋 Processing {total_diagrams} remaining diagrams in {total_batches} batches.")

    success_count = 0
    
    for i in range(total_batches):
        start_idx = i * BATCH_SIZE
        end_idx = min((i + 1) * BATCH_SIZE, total_diagrams)
        batch = pending_diagrams[start_idx:end_idx]
        
        print(f"\nProcessing Batch {i+1}/{total_batches}...")
        
        output = process_batch(batch, i+1)
        
        if output:
            # Append to staging file immediately
            with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
                f.write(output)
                f.write("\n\n") # Ensure separation
            success_count += 1
            print(f"  ✅ Batch {i+1} saved to {OUTPUT_FILE}")
        else:
            print(f"  ⚠️ Batch {i+1} failed or returned empty.")

    print("\n" + "="*30)
    print(f"🏁 Process Complete.")
    print(f"Successful Batches: {success_count}/{total_batches}")
    print(f"Output saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
