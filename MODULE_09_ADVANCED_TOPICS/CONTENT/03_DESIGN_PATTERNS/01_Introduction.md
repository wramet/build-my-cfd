# Design Patterns - Introduction

บทนำ Design Patterns

---

## Overview

> **Design Patterns** = Reusable solutions to common design problems

---

## 1. Why Patterns?

| Benefit | Description |
|---------|-------------|
| **Proven** | Tested in real systems |
| **Communication** | Common vocabulary |
| **Maintainability** | Easier to modify |
| **Flexibility** | Easier to extend |

---

## 2. Pattern Categories

| Category | Examples |
|----------|----------|
| **Creational** | Factory, Singleton |
| **Structural** | Adapter, Composite |
| **Behavioral** | Strategy, Observer, Template Method |

---

## 3. OpenFOAM Patterns

### Creational

```cpp
// Factory: Create from dictionary
autoPtr<turbulenceModel> turb = turbulenceModel::New(dict);
```

### Behavioral

```cpp
// Strategy: Interchangeable schemes
fvc::div(phi, U);  // Uses scheme from fvSchemes
```

---

## 4. When to Use

| Pattern | When |
|---------|------|
| Factory | Object creation from config |
| Strategy | Multiple algorithms |
| Observer | React to events |
| Template Method | Algorithm skeleton |

---

## 5. Module Contents

| File | Topic |
|------|-------|
| 02_Factory | Factory pattern |
| 03_Strategy | Strategy pattern |
| 04_Synergy | Combinations |
| 05_Performance | Analysis |
| 06_Exercise | Practice |

---

## Quick Reference

| Pattern | OpenFOAM Example |
|---------|------------------|
| Factory | `Model::New(dict)` |
| Strategy | fvSchemes |
| Observer | functionObjects |
| Template | solver::run() |

---

## Concept Check

<details>
<summary><b>1. Pattern คืออะไร?</b></summary>

**Reusable solution** to common design problem
</details>

<details>
<summary><b>2. OpenFOAM ใช้ patterns อะไรมากที่สุด?</b></summary>

**Factory** (RTS) และ **Strategy** (schemes, models)
</details>

<details>
<summary><b>3. Patterns guarantee ประสิทธิภาพไหม?</b></summary>

**ไม่** — patterns are about **structure**, not performance
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Factory:** [02_Factory_Pattern.md](02_Factory_Pattern.md)