# Coupled Physics - Overview

ภาพรวม Coupled Physics

---

## Overview

> **Coupled physics** = Multiple physics domains interacting

---

## 1. Types

| Coupling | Example |
|----------|---------|
| CHT | Fluid + Solid heat |
| FSI | Fluid + Structure |
| MHD | Fluid + EM |

---

## 2. Solver

```bash
chtMultiRegionFoam  # CHT
```

---

## 3. Regions

```cpp
// constant/regionProperties
regions (fluid (fluid) solid (heater));
```

---

## 4. Module Contents

| File | Topic |
|------|-------|
| 01_Fundamentals | Basics |
| 02_CHT | Heat transfer |
| 04_Registry | Multi-region |
| 05_Advanced | Topics |

---

## Quick Reference

| Need | Solver |
|------|--------|
| CHT | chtMultiRegionFoam |

---

## Concept Check

<details>
<summary><b>1. Multi-region?</b></summary>

**Separate meshes** coupled at interfaces
</details>

---

## Related Documents

- **CHT:** [02_Conjugate_Heat_Transfer.md](02_Conjugate_Heat_Transfer.md)