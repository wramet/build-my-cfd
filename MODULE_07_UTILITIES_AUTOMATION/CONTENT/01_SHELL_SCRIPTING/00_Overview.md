# Shell Scripting - Overview

ภาพรวม Shell Scripting

---

## Overview

> **Shell scripts** = Automate OpenFOAM workflows

---

## 1. Allrun Pattern

```bash
#!/bin/bash
cd ${0%/*} || exit 1
. $WM_PROJECT_DIR/bin/tools/RunFunctions

runApplication blockMesh
runApplication simpleFoam
```

---

## 2. Allclean Pattern

```bash
#!/bin/bash
cd ${0%/*} || exit 1

rm -rf 0.[0-9]* [1-9]* log.* postProcessing
cp -r 0.orig 0
```

---

## 3. Module Contents

| File | Topic |
|------|-------|
| 01_Strategy | Planning |
| 02_Framework | Templates |

---

## Quick Reference

| Script | Purpose |
|--------|---------|
| Allrun | Run case |
| Allclean | Clean case |
| Allrun.pre | Pre-process |
| Allrun.post | Post-process |

---

## 🧠 Concept Check

<details>
<summary><b>1. runApplication ทำอะไร?</b></summary>

**Run with logging** — รันคำสั่งและบันทึก output ไปยังไฟล์ log.* โดยอัตโนมัติ
</details>

<details>
<summary><b>2. ทำไมต้องใช้ Allrun และ Allclean?</b></summary>

**คำตอบ:**
- **Allrun:** สคริปต์มาตรฐานสำหรับรันทุกขั้นตอน (mesh → solver → postProcess) ช่วยให้ workflow repeatable
- **Allclean:** ลบไฟล์ผลลัพธ์ทั้งหมดเพื่อเริ่มใหม่ได้สะอาด
- ทำให้ case ใดๆ สามารถรันได้โดยไม่ต้องจำลำดับคำสั่ง
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **Strategy:** [01_Automation_Strategy.md](01_Automation_Strategy.md) — กลยุทธ์ Automation
- **Framework:** [02_Automation_Framework.md](02_Automation_Framework.md) — Framework Templates