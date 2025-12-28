# Non-Dimensionalization

การทำให้ไม่มีมิติ

---

## Overview

> **Non-dimensionalization** = Scale quantities to be dimensionless

---

## 1. Why Non-Dimensionalize?

| Benefit | Description |
|---------|-------------|
| **Simplify** | Reduce parameters |
| **Compare** | Different scales |
| **Stability** | Values near O(1) |

---

## 2. Reference Quantities

```cpp
// Define reference values
dimensionedScalar Uref("Uref", dimVelocity, 1.0);
dimensionedScalar Lref("Lref", dimLength, 1.0);
dimensionedScalar pref("pref", dimPressure, 101325);
```

---

## 3. Non-Dimensional Variables

```cpp
// Non-dimensional velocity
volVectorField Ustar = U / Uref;

// Non-dimensional pressure
volScalarField pstar = p / pref;

// Non-dimensional coordinates
volVectorField xstar = mesh.C() / Lref;
```

---

## 4. Non-Dimensional Numbers

```cpp
// Reynolds number
dimensionedScalar Re = Uref * Lref / nu;

// Prandtl number
dimensionedScalar Pr = nu / alpha;

// Mach number
volScalarField Ma = mag(U) / c;
```

---

## 5. Scaling in Equations

```cpp
// Original: ρ(∂U/∂t + U·∇U) = -∇p + μ∇²U
// Scaled:   ∂U*/∂t* + U*·∇*U* = -∇*p* + (1/Re)∇*²U*

// Non-dimensional equation
solve
(
    fvm::ddt(Ustar)
  + fvm::div(phi_star, Ustar)
 ==
    fvc::grad(pstar) / rho_star
  + fvm::laplacian(1/Re, Ustar)
);
```

---

## 6. Common Non-Dimensional Groups

| Number | Formula | Physics |
|--------|---------|---------|
| Re | UL/ν | Inertia/Viscous |
| Ma | U/c | Compressibility |
| Pr | ν/α | Momentum/Thermal |
| Nu | hL/k | Convection/Conduction |

---

## Quick Reference

| Variable | Scaling |
|----------|---------|
| U* | U/Uref |
| p* | p/(ρU²) |
| t* | t Uref/L |
| x* | x/L |

---

## Concept Check

<details>
<summary><b>1. ทำไมต้อง non-dimensionalize?</b></summary>

**Reduce parameters**, improve numerical stability
</details>

<details>
<summary><b>2. Re สูง หมายความว่าอะไร?</b></summary>

**Inertia dominates** over viscosity (turbulent)
</details>

<details>
<summary><b>3. Pressure scaling ใช้อะไร?</b></summary>

**ρU²** (dynamic pressure) หรือ reference pressure
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Arithmetic:** [03_Dimension_Arithmetic.md](03_Dimension_Arithmetic.md)