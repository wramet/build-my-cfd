# Advanced Applications

การประยุกต์ใช้ Dimensional Analysis ขั้นสูง

---

## Overview

> ใช้ dimensions เพื่อ **verify physics** และ **prevent errors**

---

## 1. Custom Dimensions

```cpp
// Define new dimension
dimensionedScalar specificHeat
(
    "Cp",
    dimEnergy / dimMass / dimTemperature,  // J/(kg·K)
    1005
);
```

---

## 2. Derived Quantities

```cpp
// Thermal diffusivity
dimensionedScalar alpha = k / (rho * Cp);
// Check: [W/(m·K)] / ([kg/m³] * [J/(kg·K)]) = [m²/s] ✓

// Reynolds number (dimensionless)
volScalarField Re = mag(U) * L / nu;
```

---

## 3. Source Terms

```cpp
// Heat source [W/m³]
dimensionedScalar Q
(
    "Q",
    dimPower / dimVolume,
    1e6
);

// Add to equation
fvScalarMatrix TEqn
(
    fvm::ddt(rho, Cp, T) == fvm::laplacian(k, T) + Q
);
```

---

## 4. Boundary Conditions

```cpp
// Heat flux [W/m²]
dimensionedScalar qw
(
    "qw",
    dimPower / dimArea,
    1000
);

// Fixed gradient BC
T.boundaryFieldRef()[patchI] == qw / k;
```

---

## 5. Turbulence Quantities

```cpp
// Turbulent kinetic energy [m²/s²]
dimensionedScalar k0("k", sqr(dimVelocity), 0.1);

// Dissipation rate [m²/s³]
dimensionedScalar eps0("epsilon", sqr(dimVelocity)/dimTime, 0.01);

// Specific dissipation [1/s]
dimensionedScalar omega0("omega", dimless/dimTime, 1);
```

---

## 6. Non-Dimensional Groups

```cpp
// Nusselt number
volScalarField Nu = h * L / k_thermal;  // dimless

// Prandtl number
dimensionedScalar Pr = nu / alpha;  // dimless

// Peclet number
volScalarField Pe = mag(U) * L / alpha;  // dimless
```

---

## Quick Reference

| Quantity | Dimension |
|----------|-----------|
| Heat flux | `dimPower/dimArea` |
| Thermal diffusivity | `sqr(dimLength)/dimTime` |
| Source | `dimPower/dimVolume` |
| k | `sqr(dimVelocity)` |
| ε | `sqr(dimVelocity)/dimTime` |

---

## Concept Check

<details>
<summary><b>1. Re คือ dimensionless ไหม?</b></summary>

**ใช่** — UL/ν = [m/s][m]/[m²/s] = dimless
</details>

<details>
<summary><b>2. k dimension คืออะไร?</b></summary>

**[m²/s²]** — kinetic energy per mass
</details>

<details>
<summary><b>3. Source term ใน energy equation?</b></summary>

**[W/m³]** = dimPower/dimVolume
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Non-Dim:** [04_Non_Dimensionalization.md](04_Non_Dimensionalization.md)