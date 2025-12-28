# Phase Change Modeling

การจำลอง Phase Change

---

## Overview

> **Phase change** = Transition between liquid/vapor/solid

---

## 1. Types

| Type | Example |
|------|---------|
| Boiling | Water → Steam |
| Condensation | Steam → Water |
| Cavitation | Liquid → Vapor (low p) |
| Solidification | Liquid → Solid |

---

## 2. Solver

```bash
interPhaseChangeFoam  # Cavitation
interCondensatingEvaporatingFoam  # Boiling
```

---

## 3. Mass Transfer

```cpp
// Source in VOF equation
∂α/∂t + ∇·(Uα) = Γ_evap - Γ_cond
```

---

## 4. Setup

```cpp
// constant/phaseProperties
model SchnerrSauer;
pSat 2300;  // Saturation pressure
```

---

## Quick Reference

| Solver | Use |
|--------|-----|
| interPhaseChangeFoam | Cavitation |
| interCondensating... | Boiling |

---

## Concept Check

<details>
<summary><b>1. Phase change เกิดเมื่อไหร่?</b></summary>

At **saturation conditions** (p or T)
</details>

---

## Related Documents

- **Cavitation:** [02_Cavitation_Modeling.md](02_Cavitation_Modeling.md)
