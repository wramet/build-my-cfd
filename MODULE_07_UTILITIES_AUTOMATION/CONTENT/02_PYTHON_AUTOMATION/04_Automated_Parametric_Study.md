# Automated Parametric Study

การทำ Parametric Study อัตโนมัติ

---

## Overview

> **Parametric study** = Run multiple cases varying parameters

<!-- IMAGE: IMG_07_005 -->
<!-- 
Purpose: เพื่อแสดง Workflow การทำ "Parametric Study" อัตโนมัติ. เริ่มจาก 1 Template Case $\rightarrow$ Clone ออกมาเป็นหลาย Case โดยเปลี่ยนค่า Parameter (เช่น Re=100, 200, 300) $\rightarrow$ สั่ง Run ขนานกัน $\rightarrow$ รวมผลลัพธ์มาพล็อต
Prompt: "Automated Parametric Study Workflow Diagram. **Step 1: Template Case:** Folder icon labelled 'Template'. **Step 2: Variation:** Arrows branching out to 3 distinct Cases: 'Case A (Re=100)', 'Case B (Re=500)', 'Case C (Re=1000)'. **Step 3: Execution:** Gear icons spinning for each case (Running Solvers). **Step 4: Aggregation:** Results flowing back into a single 'Analysis Report' (Charts/Graphs). STYLE: Process flowchart, clean folder icons, branching logic."
-->
![[IMG_07_005.jpg]]

---

## 1. Shell Script

```bash
#!/bin/bash
for Re in 100 500 1000 5000; do
    case="Re_$Re"
    cp -r template $case
    sed -i "s/REYNOLDS/$Re/" $case/constant/transportProperties
    (cd $case && ./Allrun)
done
```

---

## 2. Python

```python
import os
import subprocess

for Re in [100, 500, 1000, 5000]:
    case = f"Re_{Re}"
    os.system(f"cp -r template {case}")
    # Modify files
    # Run
    subprocess.run(["./Allrun"], cwd=case)
```

---

## 3. PyFoam

```bash
pyFoamRunParameterVariation.py \
    --parameter-file=parameters.txt \
    --cases-directory=cases \
    template
```

---

## Quick Reference

| Tool | Use |
|------|-----|
| Bash | Simple variation |
| Python | Complex logic |
| PyFoam | Built-in support |

---

## 🧠 Concept Check

<details>
<summary><b>1. ทำไมต้อง parametric study?</b></summary>

**Understand sensitivity** ของ parameters
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [../02_PYTHON_AUTOMATION/00_Overview.md](../02_PYTHON_AUTOMATION/00_Overview.md)
