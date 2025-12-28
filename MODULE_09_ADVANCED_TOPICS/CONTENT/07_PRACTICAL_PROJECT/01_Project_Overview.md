# Project Overview

ภาพรวมโปรเจค

---

## Overview

> Build a complete OpenFOAM model from scratch

---

## 1. Project Goal

สร้าง model/solver ที่:
- Compiles with wmake
- Uses RTS for selection
- Follows OpenFOAM patterns
- Works in real simulations

---

## 2. Project Structure

```
myProject/
├── Make/
│   ├── files
│   └── options
├── myModel.H
├── myModel.C
└── testCase/
    └── ...
```

---

## 3. Development Steps

| Step | Task |
|------|------|
| 1 | Design class hierarchy |
| 2 | Write header file |
| 3 | Implement methods |
| 4 | Add RTS |
| 5 | Configure Make |
| 6 | Compile and test |

---

## 4. Learning Objectives

- Understand OpenFOAM architecture
- Apply design patterns
- Use RTS system
- Debug common issues

---

## 5. Module Contents

| File | Topic |
|------|-------|
| 01_Project_Overview | This file |
| 02_Development | Model design |
| 03_Organization | File structure |
| 04_Compilation | wmake |
| 05_Inheritance | Virtual functions |
| 06_Patterns | Design patterns |
| 07_Errors | Debugging |
| 08_Challenge | Final exercise |

---

## Quick Reference

| Phase | Deliverable |
|-------|-------------|
| Design | Class diagram |
| Implementation | .H and .C files |
| Build | Compiled library |
| Test | Working case |

---

## Concept Check

<details>
<summary><b>1. โปรเจคต้องมีอะไรบ้าง?</b></summary>

**Make/, source files, RTS registration, test case**
</details>

<details>
<summary><b>2. ลำดับการพัฒนา?</b></summary>

**Design → Header → Implement → RTS → Compile → Test**
</details>

<details>
<summary><b>3. ทดสอบอย่างไร?</b></summary>

**Run solver** กับ dictionary ที่เลือก model
</details>

---

## Related Documents

- **Next:** [02_Model_Development_Rationale.md](02_Model_Development_Rationale.md)