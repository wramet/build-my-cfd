# Automated Parametric Study

การทำ Parametric Study อัตโนมัติ

---

## Overview

> **Parametric study** = Run multiple cases varying parameters

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
