#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import sys
import json
from pathlib import Path
import datetime

# ==========================================
# ⚙️ CONFIGURATION
# ==========================================

TARGET_ROOT = "/Users/woramet/Documents/th_new"
CHECKLIST_PATH = "/Users/woramet/Documents/th_new/content_development_checklist.md"
PLAN_FILE_NAME = "refactor_plan.json"
LOG_FILE = "refactor_process.log"

# CLI Command
CLI_COMMAND = "claude"
CLI_FLAGS = ["--dangerously-skip-permissions", "-p"]

# Folders to ignore
IGNORE_DIRS = {".git", ".obsidian", ".claude", "__pycache__", "TBD", "images", "applications"}

# ==========================================
# 🛠️ HELPER FUNCTIONS
# ==========================================

def read_file(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return ""

def write_file(path: str, content: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def write_json(path: str, data: dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_checklist() -> str:
    if os.path.exists(CHECKLIST_PATH):
        return read_file(CHECKLIST_PATH)
    return "Ensure high quality documentation."

def log_message(message: str):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(message)

# ==========================================
# 🧠 PHASE 1: THE ARCHITECT (PLANNING)
# ==========================================

def generate_plan_prompt(folder_name: str, file_data: dict) -> str:
    """Generate a lean prompt that triggers content-quality-checker skill."""
    files_context = ""
    for fname, content in file_data.items():
        # Truncate for planning context (~50% of typical files)
        files_context += f"\n--- FILE: {fname} ---\n{content[:7000]}...\n(Truncated for planning)\n"

    # Skill-aware prompt: "check quality" and "refactor" trigger skills
    return f"""Check the quality of these OpenFOAM documentation files and create a refactoring plan.

FOLDER: `{folder_name}` — these files form a learning sequence.

ANALYZE:
1. Detect redundancy between files
2. Check if 3W Framework (What/Why/How) is applied
3. Identify missing sections (Learning Objectives, Key Takeaways, etc.)

OUTPUT: Respond with ONLY valid JSON in this structure:
{{
  "files": {{
    "01_intro.md": "Specific instruction for this file",
    "02_details.md": "Specific instruction for this file"
  }},
  "global_strategy": "Overall approach for the folder"
}}

FILES:
{files_context}
"""

def create_refactor_plan(folder_path: Path, file_data: dict) -> dict:
    """Create refactor plan using skill-aware prompt."""
    prompt = generate_plan_prompt(folder_path.name, file_data)
    
    try:
        cmd = [CLI_COMMAND] + CLI_FLAGS + [prompt]
        result = subprocess.run(cmd, text=True, capture_output=True, encoding="utf-8")
        
        # Log stderr if present for debugging
        if result.stderr:
            log_message(f"   ⚠️ CLI stderr: {result.stderr[:300]}")
        
        # Extract JSON from response with improved parsing
        output = result.stdout.strip()
        
        # Remove common LLM markdown wrappers
        if "```json" in output:
            output = output.split("```json")[-1].split("```")[0].strip()
        elif "```" in output:
            # Handle generic code blocks
            parts = output.split("```")
            for part in parts:
                if "{" in part and "}" in part:
                    output = part.strip()
                    break
        
        json_start = output.find('{')
        json_end = output.rfind('}') + 1
        
        if json_start != -1 and json_end != -1:
            json_str = output[json_start:json_end]
            plan = json.loads(json_str)
            return plan
        else:
            log_message(f"❌ Failed to parse JSON Plan for {folder_path.name}")
            log_message(f"   Debug: Output length: {len(output)}")
            log_message(f"   Debug: Output start: {output[:500]!r}...")
            return None
    
    except json.JSONDecodeError as e:
        log_message(f"❌ JSON parsing error: {e}")
        log_message(f"   Debug: Attempted to parse: {json_str[:300] if 'json_str' in dir() else 'N/A'}...")
        return None
    except Exception as e:
        log_message(f"❌ Error creating plan: {e}")
        return None

# ==========================================
# 👷 PHASE 2: THE BUILDER (EXECUTION)
# ==========================================

def execute_file_refactor(file_path: Path, instruction: str, global_strategy: str):
    """Refactor a single file using skill-aware prompt."""
    original_content = read_file(file_path)
    
    # Skill-aware prompt: "Refactor this OpenFOAM documentation" triggers openfoam-doc-refactor skill
    prompt = f"""Refactor this OpenFOAM documentation file: {file_path.name}

GLOBAL STRATEGY: {global_strategy}
SPECIFIC INSTRUCTION: {instruction}

INPUT FILE:
{original_content}

OUTPUT: The complete refactored markdown content only. No explanations."""
    try:
        cmd = [CLI_COMMAND] + CLI_FLAGS + [prompt]
        result = subprocess.run(cmd, text=True, capture_output=True, encoding="utf-8")
        
        # Log stderr if present for debugging
        if result.stderr:
            log_message(f"   ⚠️ CLI stderr: {result.stderr[:300]}")
        
        if result.returncode == 0 and result.stdout:
            new_content = result.stdout.strip()
            orig_len = len(original_content)
            new_len = len(new_content)
            
            # Basic validation
            if new_len > orig_len * 0.5:
                write_file(file_path, new_content)
                log_message(f"   ✅ Refactored: {file_path.name} ({orig_len} → {new_len} chars)")
            else:
                log_message(f"   ⚠️ Skipped {file_path.name}: Content too short ({new_len} vs {orig_len} original).")
                # DEBUG: Show what Claude actually returned
                log_message(f"   📋 DEBUG Output preview:")
                log_message(f"   {new_content[:500]!r}...")
                # Save full output to debug file
                debug_file = file_path.parent / f".debug_{file_path.name}.txt"
                write_file(debug_file, new_content)
                log_message(f"   📄 Full output saved to: {debug_file.name}")
        else:
            log_message(f"   ❌ CLI Failed for {file_path.name} (returncode={result.returncode})")
            if result.stdout:
                log_message(f"   📋 DEBUG stdout: {result.stdout[:300]!r}")

    except Exception as e:
        log_message(f"   ❌ Error executing refactor: {e}")

# ==========================================
# 🚀 MAIN LOOP
# ==========================================

def process_folder(folder_path: Path):
    """Process a folder using skill-aware prompts."""
    log_message(f"\n📂 Entering: {folder_path.name}")
    
    # 1. Identify Files (exclude .bak, .json, and other non-content files)
    md_files = sorted([
        f for f in os.listdir(folder_path) 
        if f.endswith(".md") 
        and not f.endswith(".bak") 
        and not f.endswith(".md.bak")
        and not f.startswith(".")
    ])
    if not md_files: return

    file_data = {f: read_file(folder_path / f) for f in md_files}
    
    # 2. PHASE 1: Generate Plan
    plan_path = folder_path / PLAN_FILE_NAME
    if plan_path.exists():
        log_message(f"   ℹ️  Using existing plan: {PLAN_FILE_NAME}")
        try:
            with open(plan_path, 'r', encoding='utf-8') as f:
                plan = json.load(f)
        except json.JSONDecodeError as e:
            log_message(f"   ⚠️ Failed to load existing plan: {e}")
            plan = None
    else:
        log_message("   🧠 Generating Refactoring Plan...")
        plan = create_refactor_plan(folder_path, file_data)
        if plan:
            write_json(plan_path, plan)
            log_message(f"   📄 Plan saved to {PLAN_FILE_NAME}")

    if not plan:
        log_message("   ❌ Skipping: No valid plan.")
        return

    # 3. PHASE 2: Execute Plan
    log_message("   👷 Executing Plan...")
    global_strat = plan.get("global_strategy", "")
    files_plan = plan.get("files", {})

    for fname, instruction in files_plan.items():
        if fname in md_files:
            file_path = folder_path / fname
            execute_file_refactor(file_path, instruction, global_strat)

def main():
    root_path = Path(TARGET_ROOT)
    
    log_message("🚀 Starting Skill-Aware Refactoring...")
    log_message("   Skills will be auto-triggered from .claude/skills/")

    for current_root, dirs, files in os.walk(root_path):
        # Sort to ensure order
        dirs.sort()
        
        # Filter unwanted dirs
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith(".")]

        current_path = Path(current_root)
        
        # Target only CONTENT folders
        if "CONTENT" in str(current_path) and any(f.endswith(".md") for f in files):
            process_folder(current_path)

if __name__ == "__main__":
    main()