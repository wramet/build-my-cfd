# DimensionSet Advanced

การใช้งาน DimensionSet ขั้นสูง

---

## Overview

> **dimensionSet** = 7 exponents for M, L, T, Θ, mol, A, cd

---

## 1. Dimension System

```cpp
// [M L T Θ mol A cd]
// [kg m s K mol A cd]

dimensionSet dimMass(1, 0, 0, 0, 0, 0, 0);
dimensionSet dimLength(0, 1, 0, 0, 0, 0, 0);
dimensionSet dimTime(0, 0, 1, 0, 0, 0, 0);
dimensionSet dimTemperature(0, 0, 0, 1, 0, 0, 0);
```

---

## 2. Predefined Dimensions

| Name | Symbol | dimensionSet |
|------|--------|--------------|
| `dimVelocity` | m/s | [0 1 -1 0 0 0 0] |
| `dimPressure` | Pa | [1 -1 -2 0 0 0 0] |
| `dimDensity` | kg/m³ | [1 -3 0 0 0 0 0] |
| `dimViscosity` | Pa·s | [1 -1 -1 0 0 0 0] |
| `dimEnergy` | J | [1 2 -2 0 0 0 0] |

---

## 3. Creating Custom Dimensions

```cpp
// Thermal conductivity [W/(m·K)]
dimensionSet dimThermalConductivity
(
    1,   // kg
    1,   // m
   -3,   // s
   -1,   // K
    0, 0, 0
);

// Or use algebra
dimensionSet dimK = dimPower / dimLength / dimTemperature;
```

---

## 4. Dimension Arithmetic

```cpp
// Multiplication combines exponents (add)
dimensionSet force = dimMass * dimLength / sqr(dimTime);
// = [1 1 -2 0 0 0 0] = [N]

// Division (subtract exponents)
dimensionSet accel = dimVelocity / dimTime;
// = [0 1 -2 0 0 0 0] = [m/s²]
```

---

## 5. Access and Check

```cpp
// Get dimensions
const dimensionSet& dims = field.dimensions();

// Check dimensionless
if (dims.dimensionless())
{
    // Field is dimensionless
}

// Compare
if (dims == dimVelocity)
{
    // Field is velocity
}
```

---

## 6. Modify Dimensions

```cpp
// Reset dimensions (use carefully!)
field.dimensions().reset(dimVelocity);

// Or in construction
volScalarField T
(
    IOobject(...),
    mesh,
    dimensionedScalar("T", dimTemperature, 300)
);
```

---

## Quick Reference

| Need | Code |
|------|------|
| Create | `dimensionSet(M,L,T,Θ,...)` |
| Check | `.dimensionless()` |
| Access | `.dimensions()` |
| Compare | `== dimVelocity` |

---

## Concept Check

<details>
<summary><b>1. dimensions ใน OpenFOAM มีกี่ตัว?</b></summary>

**7**: M, L, T, Θ, mol, A, cd
</details>

<details>
<summary><b>2. multiply dimensions ทำอย่างไร?</b></summary>

**Add exponents** — [1 0 0] * [0 1 0] = [1 1 0]
</details>

<details>
<summary><b>3. dimless คืออะไร?</b></summary>

**All exponents = 0** — [0 0 0 0 0 0 0]
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Arithmetic:** [03_Dimension_Arithmetic.md](03_Dimension_Arithmetic.md)