# Dimensional Analysis - Overview

ภาพรวม Dimensional Analysis

---

## Overview

> **Dimensional analysis** = Ensure physics correctness via unit checking

---

## 1. dimensionSet

```cpp
// 7 base dimensions: [M L T Θ mol A cd]
dimensionSet dimVelocity(0, 1, -1, 0, 0, 0, 0);  // m/s
dimensionSet dimPressure(1, -1, -2, 0, 0, 0, 0);  // Pa
```

---

## 2. dimensionedScalar

```cpp
dimensionedScalar rho
(
    "rho",
    dimDensity,    // [kg/m³]
    1000
);
```

---

## 3. Automatic Checking

```cpp
// Operations check dimensions
volScalarField result = rho * sqr(U);  // [Pa] ✓

// Error if mismatch
// bad = p + U;  // [Pa] + [m/s] = ERROR!
```

---

## 4. Common Dimensions

| Variable | dimensionSet |
|----------|--------------|
| Velocity | [0 1 -1 0 0 0 0] |
| Pressure | [1 -1 -2 0 0 0 0] |
| Density | [1 -3 0 0 0 0 0] |
| Temperature | [0 0 0 1 0 0 0] |
| Viscosity | [1 -1 -1 0 0 0 0] |

---

## 5. Module Contents

| File | Topic |
|------|-------|
| 01_Introduction | Basics |
| 02_DimensionSet | Advanced |
| 03_Arithmetic | Operations |
| 04_Non_Dim | Scaling |
| 05_Advanced | Applications |
| 06_Pitfalls | Common errors |
| 07_Summary | Exercises |

---

## Quick Reference

| Need | Use |
|------|-----|
| Velocity | `dimVelocity` |
| Pressure | `dimPressure` |
| Dimensionless | `dimless` |
| Custom | `dimensionSet(...)` |

---

## Concept Check

<details>
<summary><b>1. dimensionSet มีกี่ค่า?</b></summary>

**7**: M, L, T, Θ, mol, A, cd
</details>

<details>
<summary><b>2. ทำไมต้อง dimension checking?</b></summary>

**Catch physics errors** at compile/runtime
</details>

<details>
<summary><b>3. Add ต้องมี same dimensions ไหม?</b></summary>

**ใช่** — ไม่งั้น error
</details>

---

## Related Documents

- **Introduction:** [01_Introduction.md](01_Introduction.md)
- **DimensionSet:** [02_DimensionSet_Advanced.md](02_DimensionSet_Advanced.md)