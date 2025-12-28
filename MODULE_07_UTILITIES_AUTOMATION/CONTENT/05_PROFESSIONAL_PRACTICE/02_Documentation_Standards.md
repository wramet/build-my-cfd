# Documentation Standards

มาตรฐานการเขียนเอกสาร

---

## Overview

> **Good documentation** = Reproducible research

---

## 1. Case Documentation

```markdown
# Project: Flow over Cylinder
## Objective
- Validate against NASA data
- Study Re = 100-1000

## Setup
- Solver: pimpleFoam
- Mesh: 500k cells
- BC: velocity inlet, pressure outlet
```

---

## 2. README Template

```markdown
# Case Name
## Description
## Requirements
- OpenFOAM v2312
## Run
./Allrun
## Results
See postProcessing/
```

---

## 3. Code Comments

```cpp
// Calculate turbulent kinetic energy
// k = 0.5 * (u'^2 + v'^2 + w'^2)
volScalarField k = 0.5 * magSqr(UPrime);
```

---

## 4. Validation Report

| Section | Content |
|---------|---------|
| Objective | What validated |
| Method | How compared |
| Results | Error metrics |
| Conclusion | Pass/fail |

---

## Quick Reference

| Doc Type | Purpose |
|----------|---------|
| README | Quick start |
| Report | Detailed results |
| Comments | Code explanation |

---

## 🧠 Concept Check

<details>
<summary><b>1. ทำไมต้อง document?</b></summary>

**Reproducibility** — others can repeat work
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Version Control:** [04_Version_Control_Git.md](04_Version_Control_Git.md)