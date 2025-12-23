import os
import subprocess
import sys
from pathlib import Path

# ==========================================
# ⚙️ CONFIGURATION
# ==========================================

# 1. โฟลเดอร์เป้าหมาย
TARGET_ROOT = "/Users/woramet/Documents/th_new"

# 2. คำสั่ง CLI
CLI_COMMAND = "claude"
CLI_FLAGS = ["--dangerously-skip-permissions", "-p"] 

# ==========================================

def get_annotation_prompt(filename):
    """
    สร้าง Prompt ที่โฟกัสเฉพาะ Code Block C++ และสั่งให้อธิบายเป็นภาษาไทย
    """
    return f"""
**Task:** Analyze the **C++ code blocks** in `{filename}` and append educational explanations.

**RULES:**
1. **Target:** Focus ONLY on `cpp` or `c++` code blocks. Ignore Mermaid or other types.
2. **Action:** Immediately after the closing triple backticks (```) of the code block, insert a blockquote explanation.
3. **Content Preservation:** DO NOT change any original text or the code itself. ONLY add the explanation.
4. **Language:** The explanation MUST be in **Thai Language (ภาษาไทย)**.

**FORMAT TO ADD:**

> **Code Analysis:** [อธิบายการทำงานของโค้ดส่วนนี้เป็นภาษาไทย โดยเน้นเรื่อง Syntax, การจัดการ Memory (เช่น Pointers), หรือความหมายทางฟิสิกส์ในบริบทของ OpenFOAM]

**Output Requirement:**
Return the **FULL, updated Markdown content** of the file.
"""

def process_all_files(root_dir):
    """
    Logic การวนลูปพร้อมตัวกรองโฟลเดอร์ (Filtered Recursive Loop)
    """
    root_path = Path(root_dir)
    
    if not root_path.exists():
        print(f"❌ Error: Directory not found: {root_path}")
        return

    print(f"🚀 Starting filtered scan in: {root_path}")

    for current_root, dirs, files in os.walk(root_path, topdown=True):
        
        # ---------------------------------------------------------
        # 🛡️ FILTERING LOGIC (ส่วนที่เพิ่มใหม่)
        # ---------------------------------------------------------
        
        # ตรวจสอบว่าตอนนี้เราอยู่ที่ Root Folder (TH_NEW) หรือไม่
        is_root_level = (Path(current_root).resolve() == root_path.resolve())
        
        if is_root_level:
            # กฎที่ 1: ถ้าอยู่หน้าบ้าน ให้เลือกเฉพาะโฟลเดอร์ที่ขึ้นต้นด้วย "MODULE" เท่านั้น
            # (วิธีนี้จะตัด TBD, img, Gemini_single_shot, .obsidian ออกไปเองโดยอัตโนมัติ)
            dirs[:] = [d for d in dirs if d.startswith("MODULE")]
        else:
            # กฎที่ 2: ถ้าเข้าไปในบ้านแล้ว (Sub-folders) ให้กันเหนียว ลบ TBD ทิ้งถ้ามันไปโผล่ข้างใน
            if "TBD" in dirs:
                dirs.remove("TBD")
            
            # กฎที่ 3: ลบ hidden folders (เช่น .git, .obsidian)
            dirs[:] = [d for d in dirs if not d.startswith(".")]

        # ---------------------------------------------------------

        # เรียงลำดับ A-Z เพื่อความสวยงามของ Log
        dirs.sort()
        files.sort()
        
        # กรองเฉพาะไฟล์ .md
        md_files = [f for f in files if f.endswith('.md')]

        if not md_files:
            continue
            
        print(f"\n📂 Entering: {Path(current_root).name}")

        for md_file in md_files:
            file_path = Path(current_root) / md_file
            
            print(f"  👉 Processing: {md_file} ...", end="", flush=True)
            
            # 1. สร้าง Prompt
            prompt = get_annotation_prompt(md_file)
            
            # 2. สร้างคำสั่ง CLI
            cmd = [CLI_COMMAND] + CLI_FLAGS + [prompt, str(file_path)]
            
            try:
                # 3. รันคำสั่ง
                result = subprocess.run(cmd, text=True, capture_output=True, encoding='utf-8')
                
                if result.returncode == 0 and result.stdout:
                    # 4. เขียนทับไฟล์เดิม
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(result.stdout)
                    print(" ✅ Done.")
                else:
                    print(f" ❌ Failed.")
                    if result.stderr:
                        # ปริ้น Error สั้นๆ
                        print(f"     Error: {result.stderr.strip()[:200]}...")
                        
            except Exception as e:
                print(f" ❌ Error executing script: {e}")

def main():
    process_all_files(TARGET_ROOT)
    print("\n🏁 All valid MODULE files processed.")

if __name__ == "__main__":
    main()