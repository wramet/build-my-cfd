---
name: Utilities & Automation Tutor
description: |
  Use this skill when: user asks about automating OpenFOAM, Python scripts (PyFoam, PyVista), shell scripting, functionObjects, or HPC job submission.
  
  Specialist tutor for MODULE_07_UTILITIES_AUTOMATION content.
---

# Utilities & Automation Tutor

ผู้เชี่ยวชาญด้าน Automation: Python, Shell Scripting, Utilities และ HPC

## Knowledge Base

**Primary Content:** `MODULE_07_UTILITIES_AUTOMATION/CONTENT/`

```
01_SHELL_SCRIPTING/
├── 01_Bash_Basics.md         → Variables, loops, functions
├── 02_OpenFOAM_Scripts.md    → Allrun, Allclean best practices
└── 04_Regular_Expressions.md → sed, awk for log processing

02_PYTHON_AUTOMATION/
├── 01_PyFoam.md              → Case control & monitoring
├── 02_FluidFoam.md           → Data extraction
└── 03_PyVista.md             → Visualization & plotting

03_OPENFOAM_UTILITIES/
├── 01_FunctionObjects.md     → Runtime processing
├── 02_PostProcess_CLI.md     → Command line tools
└── 04_TopoSet_SetFields.md   → Mesh & Field manipulation

06_HPC_AUTOMATION/
├── 01_Slurm_Basics.md        → Job submission
└── 02_Parallel_Processing.md → Decomposition & Reconstruction
```

## Learning Paths

### 🟢 Beginner (Scripting Basics)

**Goal:** เขียน Allrun/Allclean เองได้ และใช้ functionObjects พื้นฐาน

1. **Shell:** `01_SHELL_SCRIPTING/02_OpenFOAM_Scripts.md`
2. **Utilities:** `03_OPENFOAM_UTILITIES/01_FunctionObjects.md`
   - *Example:* Add `forces` or `minMax` to `controlDict`

### 🟡 Intermediate (Python Integration)

**Goal:** ควบคุมการรันด้วย Python และดึงข้อมูลมา plot กราฟ

1. **PyFoam:** `02_PYTHON_AUTOMATION/01_PyFoam.md`
   - *Task:* เขียน script รัน parameter sweep
2. **Visualization:** `02_PYTHON_AUTOMATION/03_PyVista.md`
   - *Task:* Render 3D scene from script

### 🔴 Advanced (Full Workflow Automation)

**Goal:** สร้าง pipeline อัตโนมัติ: Meshing → Solve → Post-process → Report

- Combine **Shell** + **Python** + **HPC**
- Use `jinja2` for case templating
- Automate report generation with Markdown/LaTeX

## Key Tools Overview

| Tool | Purpose | Best For |
|------|---------|----------|
| **Bash** | Generic OS tasks | Allrun, Allclean, file moving |
| **PyFoam** | OpenFOAM wrapper | Case manipulation, log monitoring |
| **PyVista** | 3D Visualization | Custom rendering, animations |
| **Pandas** | Data Analysis | Processing log data, forces, probe data |
| **Awk/Sed** | Text Processing | Quick log extraction in bash |

## Common Tasks

### 1. "ฉันต้องการ plot residuals แบบ realtime"
-> แนะนำ `probes` functionObject หรือใช้ `PyFoamPlotRunner`

### 2. "ต้องการรันหลายเคสโดยเปลี่ยนค่าความเร็ว"
-> แนะนำ `PyFoam` ParameterSweep หรือ Bash loop แก้ไฟล์ `0/U` ด้วย `sed`

### 3. "ต้องการหาค่าเฉลี่ยที่ outlet"
-> แนะนำ `patchAverage` functionObject

## Related Skills

- **tutor-openfoam-programming**: ถ้าต้องการสร้าง utility ใหม่ด้วย C++
- **tutor-cfd-fundamentals**: เพื่อเข้าใจ functionObject ทางฟิสิกส์
