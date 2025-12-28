# Project Organization

การจัดระเบียบโปรเจค

---

## Overview

> **Good organization** = Efficient workflow

---

## 1. Directory Structure

```
project/
├── cases/
│   ├── baseline/
│   └── parametric/
├── mesh/
├── scripts/
├── results/
└── docs/
```

---

## 2. Naming Convention

| Type | Convention |
|------|------------|
| Cases | descriptive_name |
| Scripts | action_target.sh |
| Results | case_metric.csv |

---

## 3. Case Template

```
template/
├── 0/
├── constant/
├── system/
├── Allrun
├── Allclean
└── README.md
```

---

## 4. Scripts Location

```
scripts/
├── run/
│   └── runSimulation.sh
├── post/
│   └── extractData.py
└── utils/
    └── cleanAll.sh
```

---

## Quick Reference

| Folder | Content |
|--------|---------|
| cases/ | Simulations |
| mesh/ | Mesh files |
| scripts/ | Automation |
| results/ | Output |
| docs/ | Documentation |

---

## 🧠 Concept Check

<details>
<summary><b>1. Template case ดีอย่างไร?</b></summary>

**Reuse settings** — copy and modify
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)