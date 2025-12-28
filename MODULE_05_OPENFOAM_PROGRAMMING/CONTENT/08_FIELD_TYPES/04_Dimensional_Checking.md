# Dimensional Checking in Fields

การตรวจสอบมิติใน Fields

---

## Overview

> Fields have **attached dimensions** that are checked automatically

---

## 1. Dimension in Field Creation

```cpp
volScalarField T
(
    IOobject("T", runTime.timeName(), mesh, IOobject::NO_READ),
    mesh,
    dimensionedScalar("T", dimTemperature, 300)  // [0 0 0 1 0 0 0]
);
```

---

## 2. Automatic Checking

### Valid Operations

```cpp
volScalarField p;   // [M L^-1 T^-2]
volScalarField rho; // [M L^-3]
volVectorField U;   // [L T^-1]

// OK: dimensions combine correctly
volScalarField dynP = 0.5 * rho * magSqr(U);
// [M L^-3] * [L^2 T^-2] = [M L^-1 T^-2] ✓
```

### Invalid Operations

```cpp
// ERROR: Cannot add pressure + velocity
// volScalarField bad = p + U;
```

---

## 3. Checking in Equations

```cpp
// All terms must have same dimensions
fvScalarMatrix TEqn
(
    fvm::ddt(T)           // [T/s] = [Θ T^-1]
  + fvm::div(phi, T)      // Same
  ==
    fvm::laplacian(alpha, T)  // Same
);
```

---

## 4. Common Dimension Sets

| Field | dimensionSet |
|-------|--------------|
| Pressure | `[1 -1 -2 0 0 0 0]` |
| Velocity | `[0 1 -1 0 0 0 0]` |
| Temperature | `[0 0 0 1 0 0 0]` |
| Density | `[1 -3 0 0 0 0 0]` |
| Flux (phi) | `[1 0 -1 0 0 0 0]` |

---

## 5. Accessing Dimensions

```cpp
const dimensionSet& dims = T.dimensions();

// Check dimensionless
if (dims.dimensionless())
{
    // Field is dimensionless
}
```

---

## 6. Dimension Errors

### Error Message

```
--> FOAM FATAL ERROR:
Inconsistent dimensions for +
   Left operand: [1 -1 -2 0 0 0 0]
   Right operand: [0 1 -1 0 0 0 0]
```

### Debugging

1. Check equation physics
2. Verify all field dimensions
3. Check operators (fvm vs fvc)

---

## Quick Reference

| Need | Code |
|------|------|
| Get dimensions | `field.dimensions()` |
| Check dimless | `field.dimensions().dimensionless()` |
| Set dimensions | In constructor |

---

## 🧠 Concept Check

<details>
<summary><b>1. ทำไม dimension checking สำคัญ?</b></summary>

**ป้องกัน physics errors** — จับ mistakes ตอน compile/runtime
</details>

<details>
<summary><b>2. Equation terms ต้องมี dimension เดียวกันไหม?</b></summary>

**ใช่** — ทุก term ต้องมี same dimensions
</details>

<details>
<summary><b>3. flux (phi) มี dimension อะไร?</b></summary>

**[M T^-1]** หรือ **[L^3 T^-1]** (mass or volume flux)
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Dimensioned Fields:** [06_Dimensioned_Fields.md](06_Dimensioned_Fields.md)