#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import sys
import json
import time
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

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2

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

def execute_file_refactor(file_path: Path, instruction: str, global_strategy: str) -> bool:
    """Refactor a single file using skill-aware prompt. Returns True if successful.
    
    Includes retry logic with exponential backoff for handling transient failures.
    """
    original_content = read_file(file_path)
    
    # Skill-aware prompt: "Refactor this OpenFOAM documentation" triggers openfoam-doc-refactor skill
    prompt = f"""Refactor this OpenFOAM documentation file: {file_path.name}

GLOBAL STRATEGY: {global_strategy}
SPECIFIC INSTRUCTION: {instruction}

INPUT FILE:
{original_content}

OUTPUT RULES:
1. Output the complete refactored markdown content ONLY
2. Do NOT wrap output in ```markdown``` code blocks
3. Do NOT include any explanations before or after the content
4. Start directly with the first line of the markdown (e.g., # Title)"""
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            cmd = [CLI_COMMAND] + CLI_FLAGS + [prompt]
            result = subprocess.run(cmd, text=True, capture_output=True, encoding="utf-8")
            
            # Log stderr if present for debugging
            if result.stderr:
                log_message(f"   ⚠️ CLI stderr: {result.stderr[:300]}")
            
            if result.returncode == 0 and result.stdout:
                new_content = result.stdout.strip()
                
                # Post-process: Remove markdown code block wrappers if present
                if new_content.startswith("```markdown"):
                    new_content = new_content[len("```markdown"):].strip()
                    if new_content.endswith("```"):
                        new_content = new_content[:-3].strip()
                    log_message(f"   🔧 Stripped markdown wrapper from output")
                elif new_content.startswith("```"):
                    # Handle generic ``` wrapper
                    lines = new_content.split('\n')
                    if lines[0].strip() == '```' or lines[0].startswith('```'):
                        lines = lines[1:]
                    if lines and lines[-1].strip() == '```':
                        lines = lines[:-1]
                    new_content = '\n'.join(lines).strip()
                    log_message(f"   🔧 Stripped code block wrapper from output")
                
                orig_len = len(original_content)
                new_len = len(new_content)
                
                # Basic validation
                if new_len > orig_len * 0.5:
                    write_file(file_path, new_content)
                    log_message(f"   ✅ Refactored: {file_path.name} ({orig_len} → {new_len} chars)")
                    return True
                else:
                    # Content too short - this might be a transient issue, retry
                    if attempt < MAX_RETRIES:
                        delay = RETRY_DELAY_SECONDS * (2 ** (attempt - 1))  # Exponential backoff
                        log_message(f"   ⚠️ Content too short ({new_len} vs {orig_len}). Retry {attempt}/{MAX_RETRIES} in {delay}s...")
                        time.sleep(delay)
                        continue
                    else:
                        log_message(f"   ⚠️ Skipped {file_path.name}: Content too short after {MAX_RETRIES} retries ({new_len} vs {orig_len} original).")
                        # DEBUG: Show what Claude actually returned
                        log_message(f"   📋 DEBUG Output preview:")
                        log_message(f"   {new_content[:500]!r}...")
                        # Save full output to debug file
                        debug_file = file_path.parent / f".debug_{file_path.name}.txt"
                        write_file(debug_file, new_content)
                        log_message(f"   📄 Full output saved to: {debug_file.name}")
                        return False
            else:
                # CLI failed - retry
                if attempt < MAX_RETRIES:
                    delay = RETRY_DELAY_SECONDS * (2 ** (attempt - 1))
                    log_message(f"   ❌ CLI Failed (returncode={result.returncode}). Retry {attempt}/{MAX_RETRIES} in {delay}s...")
                    time.sleep(delay)
                    continue
                else:
                    log_message(f"   ❌ CLI Failed for {file_path.name} after {MAX_RETRIES} retries (returncode={result.returncode})")
                    if result.stdout:
                        log_message(f"   📋 DEBUG stdout: {result.stdout[:300]!r}")
                    return False

        except Exception as e:
            if attempt < MAX_RETRIES:
                delay = RETRY_DELAY_SECONDS * (2 ** (attempt - 1))
                log_message(f"   ❌ Error: {e}. Retry {attempt}/{MAX_RETRIES} in {delay}s...")
                time.sleep(delay)
                continue
            else:
                log_message(f"   ❌ Error executing refactor after {MAX_RETRIES} retries: {e}")
                return False
    
    return False  # Should not reach here

# ==========================================
# 🚀 MAIN LOOP
# ==========================================

def process_folder(folder_path: Path):
    """Process a folder using skill-aware prompts with per-file tracking."""
    
    # Load or create status file for per-file tracking
    status_file = folder_path / ".refactor_status.json"
    if status_file.exists():
        try:
            with open(status_file, 'r', encoding='utf-8') as f:
                status = json.load(f)
        except json.JSONDecodeError:
            status = {"completed": [], "skipped": []}
    else:
        status = {"completed": [], "skipped": []}
    
    completed_files = set(status.get("completed", []))
    
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
    
    # Filter out already completed files
    pending_files = [f for f in md_files if f not in completed_files]
    
    if not pending_files:
        log_message(f"   ✅ All {len(md_files)} files already completed")
        return
    
    log_message(f"   📋 Status: {len(completed_files)}/{len(md_files)} completed, {len(pending_files)} pending")

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

    # 3. PHASE 2: Execute Plan (only for pending files)
    log_message("   👷 Executing Plan...")
    global_strat = plan.get("global_strategy", "")
    files_plan = plan.get("files", {})

    for fname, instruction in files_plan.items():
        if fname in pending_files:
            file_path = folder_path / fname
            success = execute_file_refactor(file_path, instruction, global_strat)
            
            # Track result
            if success:
                status["completed"].append(fname)
            else:
                if fname not in status.get("skipped", []):
                    status.setdefault("skipped", []).append(fname)
            
            # Save status after each file
            write_json(status_file, status)
        elif fname in completed_files:
            log_message(f"   ⏭️  Skipping {fname} (already completed)")
    
    # Summary
    total_completed = len(status.get("completed", []))
    total_skipped = len(status.get("skipped", []))
    log_message(f"   📊 Summary: {total_completed} completed, {total_skipped} skipped")

def verify_and_retry_all(root_path: Path) -> dict:
    """Final verification pass: check all subfolders and retry any incomplete files.
    
    Returns a summary dict with counts of completed, skipped, and retried files.
    """
    log_message("\n🔍 Final Verification Pass: Checking all subfolders...")
    
    summary = {
        "folders_checked": 0,
        "files_retried": 0,
        "files_succeeded": 0,
        "files_still_incomplete": 0
    }
    
    for current_root, dirs, files in os.walk(root_path):
        dirs.sort()
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith(".")]
        
        current_path = Path(current_root)
        
        # Target only CONTENT folders
        if "CONTENT" not in str(current_path) or not any(f.endswith(".md") for f in files):
            continue
        
        status_file = current_path / ".refactor_status.json"
        if not status_file.exists():
            continue
        
        summary["folders_checked"] += 1
        
        # Load status
        try:
            with open(status_file, 'r', encoding='utf-8') as f:
                status = json.load(f)
        except json.JSONDecodeError:
            continue
        
        # Get skipped files that need retry
        skipped_files = status.get("skipped", [])
        completed_files = set(status.get("completed", []))
        
        if not skipped_files:
            continue
        
        log_message(f"\n📂 Retrying in: {current_path.name}")
        log_message(f"   Found {len(skipped_files)} skipped files to retry")
        
        # Load plan if exists
        plan_path = current_path / PLAN_FILE_NAME
        if not plan_path.exists():
            log_message(f"   ⚠️ No plan found, skipping retry")
            continue
        
        try:
            with open(plan_path, 'r', encoding='utf-8') as f:
                plan = json.load(f)
        except json.JSONDecodeError:
            log_message(f"   ⚠️ Invalid plan, skipping retry")
            continue
        
        global_strat = plan.get("global_strategy", "")
        files_plan = plan.get("files", {})
        
        # Retry each skipped file
        for fname in list(skipped_files):  # Use list() to allow modification during iteration
            if fname not in files_plan:
                log_message(f"   ⚠️ {fname} not in plan, skipping")
                continue
            
            file_path = current_path / fname
            if not file_path.exists():
                log_message(f"   ⚠️ {fname} not found, skipping")
                continue
            
            summary["files_retried"] += 1
            instruction = files_plan[fname]
            
            log_message(f"   🔄 Retrying: {fname}")
            success = execute_file_refactor(file_path, instruction, global_strat)
            
            if success:
                summary["files_succeeded"] += 1
                # Move from skipped to completed
                skipped_files.remove(fname)
                status["completed"].append(fname)
                status["skipped"] = skipped_files
                write_json(status_file, status)
                log_message(f"   ✅ Successfully retried: {fname}")
            else:
                summary["files_still_incomplete"] += 1
                log_message(f"   ❌ Still failed: {fname}")
    
    return summary

def main():
    root_path = Path(TARGET_ROOT)
    
    log_message("🚀 Starting Skill-Aware Refactoring...")
    log_message("   Skills will be auto-triggered from .claude/skills/")
    log_message(f"   Retry config: max_retries={MAX_RETRIES}, delay={RETRY_DELAY_SECONDS}s")

    # PHASE 1: Initial pass through all folders
    for current_root, dirs, files in os.walk(root_path):
        # Sort to ensure order
        dirs.sort()
        
        # Filter unwanted dirs
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith(".")]

        current_path = Path(current_root)
        
        # Target only CONTENT folders
        if "CONTENT" in str(current_path) and any(f.endswith(".md") for f in files):
            process_folder(current_path)
    
    # PHASE 2: Final verification and retry pass
    summary = verify_and_retry_all(root_path)
    
    # Final summary
    log_message("\n" + "="*60)
    log_message("📊 FINAL SUMMARY")
    log_message("="*60)
    log_message(f"   Folders checked in retry pass: {summary['folders_checked']}")
    log_message(f"   Files retried: {summary['files_retried']}")
    log_message(f"   Files succeeded on retry: {summary['files_succeeded']}")
    log_message(f"   Files still incomplete: {summary['files_still_incomplete']}")
    
    if summary['files_still_incomplete'] > 0:
        log_message("\n⚠️ Some files could not be completed. Check the .debug_*.txt files for details.")
    else:
        log_message("\n✅ All files processed successfully!")

if __name__ == "__main__":
    main()