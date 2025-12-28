# Coupled Physics Fundamentals

พื้นฐาน Coupled Physics

---

## Overview

> Coupling = Multiple physics solved together

---

## 1. Coupling Types

| Type | Method |
|------|--------|
| Weak | Sequential |
| Strong | Iterate |
| Monolithic | Single matrix |

---

## 2. Interface

```cpp
// Heat flux continuity
q_fluid = q_solid
T_fluid = T_solid
```

---

## 3. Implementation

```cpp
forAll(fluidRegions, i) { solveFluid(); }
forAll(solidRegions, i) { solveSolid(); }
```

---

## Quick Reference

| Coupling | When |
|----------|------|
| Weak | Loose coupling |
| Strong | Tight coupling |

---

## Concept Check

<details>
<summary><b>1. Weak vs Strong?</b></summary>

- **Weak**: One solve per step
- **Strong**: Iterate to converge
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)