# Automation Strategy

กลยุทธ์การ Automate

---

## Overview

> **Strategy** สำหรับ effective automation

---

## 1. Principles

| Principle | Description |
|-----------|-------------|
| Reproducible | Same results every time |
| Documented | Know what it does |
| Error handling | Handle failures |
| Modular | Reusable parts |

---

## 2. Workflow Phases

```mermaid
flowchart LR
    A[Pre] --> B[Solve]
    B --> C[Post]
    C --> D[Analyze]
```

<!-- IMAGE: IMG_07_003 -->
<!-- 
Purpose: เพื่อแสดงวงจร "CFD Automation Pipeline" ที่สมบูรณ์. การ Automate ไม่ใช่แค่การรัน Solver แต่ต้องครอบคลุมตั้งแต่การสร้าง Mesh ($\rightarrow$ Pre) ไปจนถึงการสรุปผลกราฟ ($\rightarrow$ Post) เพื่อให้มั่นใจในความ "Reproducible"
Prompt: "Sequential CFD Automation Pipeline. **Stage 1 (Pre-processing):** Icons for 'CAD Import' and 'Meshing (blockMesh)'. **Stage 2 (Solving):** Icon for 'CPU/Server Rack' running calculations. **Stage 3 (Post-processing):** Icons for 'Sampling' and 'Visualization (ParaView)'. **Integration:** A conveyor belt connecting all stages, driven by a 'Script/Bot'. Label: 'Fully Automated Workflow'. STYLE: Industrial process diagram, clean and efficient looking."
-->
[[IMG_07_003.jpg]]

---

## 3. Script Structure

```bash
#!/bin/bash
# Phase 1: Pre-processing
./Allrun.pre

# Phase 2: Solve
./Allrun.solve

# Phase 3: Post-processing
./Allrun.post
```

---

## 4. Allrun.pre

```bash
#!/bin/bash
blockMesh
setFields
decomposePar
```

---

## Quick Reference

| Phase | Scripts |
|-------|---------|
| Pre | Mesh, initialize |
| Solve | Run solver |
| Post | Process, plot |

---

## 🧠 Concept Check

<details>
<summary><b>1. ทำไมแยก phases?</b></summary>

**Debug easily**, rerun specific phase
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)