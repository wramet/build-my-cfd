#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import sys
from pathlib import Path
import datetime
import re
from collections import Counter

# ==========================================
# ⚙️ CONFIGURATION
# ==========================================

TARGET_ROOT = "/Users/woramet/Documents/th_new"
SOURCE_REF_PATH = "/Users/woramet/Documents/th_new/.applications"

# CLI Command
CLI_COMMAND = "claude"
CLI_FLAGS = ["--dangerously-skip-permissions", "-p"]

# Safety Thresholds
SIZE_THRESHOLD_RATIO = 0.90
LOG_FILE = "refactor_success.log"
ERROR_LOG = "refactor_errors.log"

# Limits for Context Injection
MAX_CONTEXT_FILES = 5        
MAX_CONTENT_INJECTION = 1    
MAX_LINES_PER_FILE = 150     

# ==========================================
# 🧠 CONTEXT RETRIEVER
# ==========================================

def extract_cpp_keywords(text: str) -> set:
    """Extracts relevant C++ identifiers from code blocks in the markdown."""
    keywords = set()
    code_blocks = re.findall(r'```cpp(.*?)```', text, re.DOTALL)
    
    for block in code_blocks:
        tokens = re.findall(r'\b[a-zA-Z_]\w{3,}\b', block)
        for token in tokens:
            if token not in {
                'return', 'void', 'const', 'include', 'using', 'namespace', 
                'class', 'public', 'private', 'template', 'typedef', 'virtual',
                'if', 'else', 'for', 'while', 'switch', 'case', 'break'
            }:
                keywords.add(token)
    return keywords

def search_relevant_files(keywords: set, search_root: str) -> str:
    """Greps the search_root for the keywords and returns best matching file paths."""
    if not keywords or not os.path.exists(search_root):
        return "No relevant source code found."

    search_terms = sorted(list(keywords), key=len, reverse=True)[:10]

    print(f"     🔍 Searching for: {', '.join(search_terms)} ...")

    pattern = "|".join([re.escape(t) for t in search_terms])
    cmd = ["grep", "-r", "-c", "-E", pattern, search_root]

    try:
        # Run with a 15s timeout to prevent hanging on massive directories
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        
        matches = []
        for line in result.stdout.splitlines():
            if ":" in line:
                parts = line.rsplit(":", 1)
                fname = parts[0]
                try:
                    count = int(parts[1])
                except ValueError:
                    count = 0
                
                if count > 0:
                    matches.append((fname, count))
        
        matches.sort(key=lambda x: x[1], reverse=True)
        top_matches = matches[:MAX_CONTEXT_FILES]

        context_str = "\n--- REFERENCE SOURCE FILES FOUND IN DATABASE ---\n"
        context_str += "The following files contain matching OpenFOAM logic:\n"
        
        for path, count in top_matches:
            rel_path = path.replace(search_root, ".applications")
            context_str += f"- {rel_path} (Matches: {count})\n"
            
        if top_matches and MAX_CONTENT_INJECTION > 0:
            best_file = top_matches[0][0]
            rel_path = best_file.replace(search_root, ".applications")
            context_str += f"\n--- CONTENT OF BEST MATCH: {rel_path} ---\n"
            try:
                with open(best_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    snippet = "".join(lines[:MAX_LINES_PER_FILE])
                    if len(lines) > MAX_LINES_PER_FILE:
                        snippet += "\n... (File truncated) ..."
                    context_str += f"```cpp\n{snippet}\n```\n"
            except Exception as e:
                context_str += f"[Error reading file: {e}]\n"

        return context_str

    except subprocess.TimeoutExpired:
        return "Reference search timed out."
    except Exception as e:
        return f"Error during grep search: {e}"

# ==========================================
# PROMPT GENERATOR
# ==========================================

def get_refactor_prompt(filename: str, file_content: str, reference_context: str) -> str:
    return f"""
**Role:** Senior OpenFOAM Developer & Technical Educator.
**Task:** Refactor the Markdown content below.

**INPUT FILE (`{filename}`):**
```markdown
{file_content}
```

**REFERENCE CONTEXT:**
{reference_context}

**INSTRUCTIONS:**
1. Refactor C++ Blocks: Fix indentation and add `// English comments`.
2. Add Thai Explanations: Insert the specific Thai explanation block (Source/Explanation/Key Concepts) immediately after every C++ block.
3. Source Finding: Use the reference context above to identify the correct 📂 Source: path.

**CRITICAL OUTPUT PROTOCOL:**
Wrap your FULL markdown content strictly inside these tags:

<FILE_CONTENT_START>
[Insert transformed markdown here]
<FILE_CONTENT_END>

Do NOT output conversational text. Do NOT wrap the content inside the tags with markdown code blocks.
"""

# ==========================================
# HELPERS
# ==========================================

def load_processed_files(log_path: str) -> set:
    processed = set()
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                processed.add(line.strip())
    return processed

def log_success(log_path: str, file_path: str) -> None:
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(file_path + "\n")

def log_error(log_path: str, file_path: str, error_msg: str) -> None:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] Failed: {file_path}\nError: {error_msg}\n{'-' * 50}\n")

def clean_output(raw_output: str) -> str:
    """Extracts content between tags and cleans up unwanted markdown fences."""
    pattern = re.compile(r"<FILE_CONTENT_START>(.*?)<FILE_CONTENT_END>", re.DOTALL)
    match = pattern.search(raw_output)
    if not match:
        return ""
    
    content = match.group(1).strip()
    
    # Strip double markdown fences if the AI ignored instructions
    lines = content.splitlines()
    if len(lines) >= 2 and lines[0].strip().startswith("```") and lines[-1].strip() == "```":
        content = "\n".join(lines[1:-1]).strip()
        
    return content

def safety_check(original_content: str, new_content: str):
    lo = len(original_content)
    ln = len(new_content)
    if lo == 0: return True, "Original was empty"
    if ln == 0: return False, "Extraction failed (Tags missing)"
    if ln < lo * SIZE_THRESHOLD_RATIO:
        return False, f"New content too short ({ln}/{lo})"
    return True, "OK"

# ==========================================
# MAIN PROCESS
# ==========================================

def process_all_files(root_dir: str) -> None:
    root_path = Path(root_dir)
    if not root_path.exists():
        print(f"❌ Error: Directory not found: {root_path}")
        return

    completed = load_processed_files(LOG_FILE)
    print(f"🚀 Starting Refactoring in: {root_path}")
    print(f"📚 Reference DB: {SOURCE_REF_PATH}")

    for current_root, dirs, files in os.walk(root_path, topdown=True):
        current_root_path = Path(current_root)
        
        # Filter folders
        if current_root_path.resolve() == root_path.resolve():
            dirs[:] = [d for d in dirs if d.startswith("MODULE")]
        else:
            if "TBD" in dirs: dirs.remove("TBD")
            dirs[:] = [d for d in dirs if not d.startswith(".")]
        
        dirs.sort()
        files.sort()
        md_files = [f for f in files if f.endswith(".md")]

        if not md_files: continue
        
        print(f"\n📂 Entering: {current_root_path.name}")

        for md_file in md_files:
            file_path = current_root_path / md_file
            str_path = str(file_path)

            if str_path in completed: continue

            print(f"  👉 Refactoring: {md_file} ...")

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    original = f.read()

                if not original.strip(): continue

                # Context Retrieval
                keywords = extract_cpp_keywords(original)
                reference_context = search_relevant_files(keywords, SOURCE_REF_PATH)

                # CLI Execution
                prompt = get_refactor_prompt(md_file, original, reference_context)
                cmd = [CLI_COMMAND] + CLI_FLAGS + [prompt]
                result = subprocess.run(cmd, text=True, capture_output=True, encoding="utf-8")

                if result.returncode == 0 and result.stdout:
                    new_content = clean_output(result.stdout)
                    is_safe, reason = safety_check(original, new_content)

                    if is_safe:
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(new_content)
                        log_success(LOG_FILE, str_path)
                        print("     ✅ Done.")
                    else:
                        print(f"     ❌ Rejected: {reason}")
                        log_error(ERROR_LOG, str_path, reason)
                else:
                    print("     ❌ Failed (CLI Error).")
                    log_error(ERROR_LOG, str_path, result.stderr or "No output")

            except Exception as e:
                print(f"     ❌ Error: {e}")
                log_error(ERROR_LOG, str_path, str(e))

def main() -> None:
    process_all_files(TARGET_ROOT)
    print("\n🏁 Refactoring Process Finished.")

if __name__ == "__main__":
    main()