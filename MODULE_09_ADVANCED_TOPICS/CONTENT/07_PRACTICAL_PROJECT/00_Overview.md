# Practical Project - Overview

ภาพรวม Practical Project

---

## Overview

> สร้าง OpenFOAM model แบบครบวงจร

---

## 1. Project Scope

| Component | Deliverable |
|-----------|-------------|
| Design | Class diagram |
| Code | .H, .C files |
| Build | Make system |
| Test | Working case |

---

## 2. Development Flow

```mermaid
flowchart LR
    A[Design] --> B[Code]
    B --> C[Compile]
    C --> D[Test]
    D --> E[Debug]
    E --> B
```

---

## 3. Required Knowledge

- C++ inheritance
- Templates
- RTS system
- wmake

---

## 4. Module Contents

| File | Topic |
|------|-------|
| 01_Project | Overview |
| 02_Development | Design |
| 03_Organization | Structure |
| 04_Compilation | Build |
| 05_Inheritance | Virtual |
| 06_Patterns | Design |
| 07_Errors | Debug |
| 08_Challenge | Final |

---

## Quick Reference

| Step | Action |
|------|--------|
| 1 | Design class |
| 2 | Write code |
| 3 | Setup Make |
| 4 | Compile |
| 5 | Test |
| 6 | Debug |

---

## Concept Check

<details>
<summary><b>1. โปรเจคต้องมีอะไร?</b></summary>

**Code + Make + RTS + Test case**
</details>

<details>
<summary><b>2. Development loop คืออะไร?</b></summary>

**Code → Compile → Test → Debug → repeat**
</details>

<details>
<summary><b>3. เริ่มจากอะไร?</b></summary>

**Design** — understand base class first
</details>

---

## Related Documents

- **Project Overview:** [01_Project_Overview.md](01_Project_Overview.md)
- **Development:** [02_Model_Development_Rationale.md](02_Model_Development_Rationale.md)