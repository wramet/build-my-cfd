import os
import subprocess
import sys
from pathlib import Path

# ==========================================
# ⚙️ CONFIGURATION
# ==========================================

# 1. โฟลเดอร์หลักที่มีไฟล์ Notes ของคุณ
PARENT_ROOT = "/Users/woramet/Documents/th_new"

# 2. ไฟล์ Style Guide (ถ้าไม่มีจะใช้ค่า Default)
STYLE_GUIDE_PATH = "/Users/woramet/Documents/th_new/Obsidian_rule.md" 

# 3. ไฟล์ Log เพื่อกันไม่ให้รันซ้ำโฟลเดอร์เดิม
LOG_FILE = "obsidian_context_bridge.log"

# 4. การตั้งค่า CLI
# ตรวจสอบว่าคุณใช้ tool ตัวไหน (claude, llm, ฯลฯ)
# flag --dangerously-skip-permissions บอกให้ Agent แก้ไขไฟล์ได้เลยโดยไม่ต้องถามยืนยัน
CLI_COMMAND = "claude"
CLI_FLAGS = ["--dangerously-skip-permissions", "-p"]

# ==========================================

def load_style_guide():
    """อ่านกฎการเขียนจากไฟล์ภายนอก"""
    path = Path(STYLE_GUIDE_PATH)
    if not path.exists():
        return "Use standard Markdown with Obsidian Callouts."
    try:
        return path.read_text(encoding='utf-8')
    except Exception:
        return "Use standard Markdown with Obsidian Callouts."

def get_context_bridge_prompt(target_filename, style_guide_text):
    """
    สร้าง Prompt ที่ฉลาดพอจะแยกแยะเนื้อหา (Physics, Code, Math) 
    และเชื่อมโยงไปยังไฟล์ OpenFOAM ที่ถูกต้องได้เอง
    """
    return f"""
**Role:** Senior OpenFOAM Engineer & Technical Instructor.

**Objective:** Edit `{target_filename}` to bridge the gap between "Theory/Concept" and "OpenFOAM Implementation".

**THE CHALLENGE:**
This file could be about ANYTHING (Math, Physics, Meshing, C++ Coding, or Post-processing).
You must analyze the content and figure out **"Where does this live in an OpenFOAM case?"**

**TASK INSTRUCTIONS:**

1.  **Analyze Content & Categorize:**
    Read the content and determine which "OpenFOAM Domain" it belongs to:
    * **Domain A: Physics & Fields** (e.g., Viscosity, Density, U, p, k-epsilon) -> Map to `0/` directory, `constant/transportProperties`, or `constant/turbulenceProperties`.
    * **Domain B: Numerics & Linear Algebra** (e.g., Gradient schemes, Matrix solvers, Residuals) -> Map to `system/fvSchemes` or `system/fvSolution`.
    * **Domain C: Simulation Control** (e.g., Time step, Write interval, Courant No.) -> Map to `system/controlDict`.
    * **Domain D: Meshing** (e.g., Cell types, Refinement, Layers) -> Map to `system/blockMeshDict` or `system/snappyHexMeshDict`.
    * **Domain E: Coding/Customization** (e.g., creating a new boundary condition, editing a solver) -> Map to the `src/` directory structure (e.g., `src/finiteVolume/...`) or compilation files (`Make/files`, `Make/options`).

2.  **INSERTION TYPE A: File Header (The Big Picture)**
    - Insert a `> [!TIP]` block at the very top of the file.
    - **Concept:** Explain simply *why* this topic matters for a successful simulation (e.g., stability, accuracy).
    - **Language:** Explain in **Thai**.

3.  **INSERTION TYPE B: Section Anchors (The Connection)**
    - Scan for H2 Headers (`##`).
    - Immediately after the header, insert a `> [!NOTE]` block titled `**📂 OpenFOAM Context**`.
    - **CRITICAL:** Based on your domain analysis in Step 1, explicitly name the **File (`dict`)** and **Keywords** related to that specific section.
    - **Language:** Explain in **Thai**, but keep technical terms/filenames in **English**.
    
    *Example logic for diverse topics:*
    - If the section explains "Discretization of Convection", YOU MUST mention `divSchemes` in `system/fvSchemes`.
    - If the section explains "Adding Layers to a Mesh", YOU MUST mention `addLayersControls` in `snappyHexMeshDict`.
    - If the section explains "Standard Deviation of Field", YOU MUST mention `functionObjects` in `controlDict`.

**NON-DESTRUCTIVE RULE:**
- **DO NOT DELETE** or rewrite original text, equations, or code blocks.
- **ONLY INSERT** the Callout blocks at the designated spots.

**FORMATTING:**
---
{style_guide_text}
---

**Output Requirement:**
Apply the changes directly to `{target_filename}`. The final file must contain all original content PLUS the new context bridges.
"""

def create_ignore_file(folder_path):
    """สร้าง .claudeignore เพื่อกัน AI อ่านไฟล์ขยะ"""
    ignore_path = Path(folder_path) / ".claudeignore"
    content = "*.png\n*.jpg\n*.jpeg\n*.pdf\n*.zip\n.DS_Store\n.git\n"
    try:
        with open(ignore_path, "w") as f:
            f.write(content)
    except Exception:
        pass 

def process_module(module_path, log_path, completed_paths, style_guide_content):
    """
    วนลูปในแต่ละ Module เพื่อประมวลผลไฟล์ .md
    """
    print(f"\n🚀 Entering Module: {module_path.name}")
    
    # ⚠️ เพิ่ม topdown=True (ค่า default) เพื่อให้เราจัดลำดับ folders ได้
    for current_root, dirs, files in os.walk(module_path, topdown=True):
        
        # ✅ บรรทัดนี้สำคัญ! สั่งให้เรียงโฟลเดอร์ย่อย ก-ฮ ก่อนจะเดินเข้าไปหา
        dirs.sort() 
        
        # ค้นหาเฉพาะไฟล์ Markdown และเรียงลำดับ
        md_files = sorted([f for f in files if f.endswith('.md')])

        if not md_files:
            continue

        abs_current_path = str(Path(current_root).resolve())
        folder_name = Path(current_root).name

        # ข้าม Folder ที่เคยทำไปแล้ว
        if abs_current_path in completed_paths:
            # print(f"  ⏭️  Skipping completed folder: {folder_name}")
            continue

        print(f"  🔨 Processing Sub-folder: {folder_name}")
        create_ignore_file(abs_current_path)

        all_success = True
        
        for md_file in md_files:
            print(f"     👉 Injecting Context into: {md_file}")
            
            # สร้าง Prompt อัจฉริยะ
            final_prompt = get_context_bridge_prompt(md_file, style_guide_content)
            
            # ส่งคำสั่งให้ CLI (claude -p "PROMPT" filename.md)
            # เราโยนชื่อไฟล์ไปให้ CLI เพื่อให้มันอ่านและแก้ไขไฟล์นั้นโดยตรง
            cmd = [CLI_COMMAND] + CLI_FLAGS + [final_prompt] + [md_file]

            try:
                # รันคำสั่ง
                result = subprocess.run(cmd, text=True, cwd=abs_current_path, capture_output=True)
                
                if result.returncode == 0:
                    print(f"        ✅ Success: {md_file} updated.")
                else:
                    print(f"        ❌ Failed: {result.stderr}")
                    all_success = False
            except Exception as e:
                print(f"        ❌ Error: {e}")
                all_success = False

        # ถ้าทำสำเร็จครบทุกไฟล์ใน Folder นั้น ให้บันทึก Log
        if all_success:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(abs_current_path + "\n")
            completed_paths.add(abs_current_path)

def main():
    try:
        parent_root = Path(PARENT_ROOT).resolve()
        log_path = Path(LOG_FILE).resolve()
    except Exception:
        print("❌ Error resolving paths.")
        sys.exit(1)

    print(f"🌟 Starting OpenFOAM Context Injection (Universal Bridge Mode)")
    print(f"📂 Parent Root: {parent_root}")
    
    if not parent_root.exists():
        print("❌ Parent root directory does not exist.")
        sys.exit(1)
        
    if not log_path.exists():
        log_path.touch()

    print("📜 Loading Style Guide...")
    style_guide_content = load_style_guide()

    # โหลด Log เก่า
    with open(log_path, 'r', encoding='utf-8') as f:
        completed_paths = set(line.strip() for line in f if line.strip())

    # หา Folder ทั้งหมดใน Parent Root
    all_items = sorted(os.listdir(parent_root))
    module_folders = []
    for item in all_items:
        full_path = parent_root / item
        if full_path.is_dir():
            if "TBD" in item or item.startswith("."):
                continue 
            else:
                module_folders.append(full_path)

    print(f"📋 Found {len(module_folders)} modules to process.")

    # เริ่มวนลูปทำงาน
    for module_path in module_folders:
        process_module(module_path, log_path, completed_paths, style_guide_content)

    print("\n🏁 Context Injection Finished. Your notes are now connected to OpenFOAM!")

if __name__ == "__main__":
    main()