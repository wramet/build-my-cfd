# DimensionSet Advanced

---

## Learning Objectives

After studying this section, you will be able to:
- Define custom `dimensionSet` objects for any physical quantity
- Perform dimension arithmetic to derive new dimensions
- Check and compare field dimensions in code
- Modify dimensions of existing fields safely
- Create dimensions for thermal and mass transfer applications

---

## Overview

> **dimensionSet** = 7 exponents representing fundamental dimensions: **M** (mass), **L** (length), **T** (time), **Θ** (temperature), **mol** (amount), **A** (current), **cd** (luminous intensity)

This system enables OpenFOAM to perform automatic dimensional consistency checking at compile-time, preventing unit errors in your simulations.

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

### Thermal Applications

```cpp
// Thermal conductivity [W/(m·K)] = kg·m/(s³·K)
dimensionSet dimThermalConductivity
(
    1,   // M: kg
    1,   // L: m
   -3,   // T: s
   -1,   // Θ: K
    0, 0, 0  // mol, A, cd
);

// Heat transfer coefficient [W/(m²·K)] = kg/(s³·K)
dimensionSet dimHeatTransferCoeff
(
    1,   // M: kg
    0,   // L: m
   -3,   // T: s
   -1,   // Θ: K
    0, 0, 0
);
```

### Mass Transfer Applications

```cpp
// Mass diffusivity [m²/s]
dimensionSet dimMassDiffusivity
(
    0,   // M: kg
    2,   // L: m
   -1,   // T: s
    0,   // Θ: K
    0, 0, 0
);

// Molar flux [mol/(m²·s)]
dimensionSet dimMolarFlux
(
    0,   // M: kg
   -2,   // L: m
   -1,   // T: s
    0,   // Θ: K
    1,   // mol: mol
    0, 0  // A, cd
);
```

### Using Algebraic Operations

```cpp
// Thermal conductivity using algebra
dimensionSet dimThermalConductivity = dimPower / dimLength / dimTemperature;

// Specific heat [J/(kg·K)]
dimensionSet dimSpecificHeat = dimEnergy / dimMass / dimTemperature;
```

---

## 4. Dimension Arithmetic

```cpp
// Multiplication combines exponents (add)
dimensionSet force = dimMass * dimLength / sqr(dimTime);
// = [1 1 -2 0 0 0 0] = [N] (Newton)

// Division (subtract exponents)
dimensionSet accel = dimVelocity / dimTime;
// = [0 1 -2 0 0 0 0] = [m/s²]

// Power operations
dimensionSet area = pow(dimLength, 2);
// = [0 2 0 0 0 0 0] = [m²]
```

---

## 5. Access and Check Dimensions

```cpp
// Get dimensions from a field
const dimensionSet& dims = field.dimensions();

// Check if dimensionless
if (dims.dimensionless())
{
    Info << "Field is dimensionless" << endl;
}

// Compare with predefined dimensions
if (dims == dimVelocity)
{
    Info << "Field has velocity dimensions" << endl;
}

// Print dimensions
Info << "Dimensions: " << dims << endl;
// Output: Dimensions: [0 1 -1 0 0 0 0]
```

---

## 6. Modify Dimensions

```cpp
// Reset dimensions (use carefully!)
field.dimensions().reset(dimVelocity);

// Set dimensions at construction
volScalarField T
(
    IOobject("T", runTime.timeName(), mesh),
    mesh,
    dimensionedScalar("T", dimTemperature, 300)
);

// Dimensions in GeometricFields
volVectorField U
(
    IOobject("U", runTime.timeName(), mesh),
    mesh,
    dimensionedVector("U", dimVelocity, vector::zero)
);
```

---

## Quick Reference

| Need | Code |
|------|------|
| Create custom dimension | `dimensionSet(M,L,T,Θ,mol,A,cd)` |
| Check dimensionless | `.dimensionless()` |
| Access dimensions | `.dimensions()` |
| Compare dimensions | `== dimVelocity` |
| Reset dimensions | `.reset(dimSet)` |
| Print dimensions | `Info << dims << endl;` |

---

## Key Takeaways

- **7 Fundamental Dimensions**: Mass, Length, Time, Temperature, Amount, Current, Luminous Intensity
- **Custom Dimensions**: Define manually using exponents or derive through algebraic operations
- **Dimension Arithmetic**: Multiplication = add exponents, Division = subtract exponents
- **Type Safety**: OpenFOAM checks dimensional consistency at compile-time
- **Thermal/Mass Transfer**: Create custom dimensions for any derived quantity using the same 7-component system

---

## 🧠 Concept Check

<details>
<summary><b>1. How many fundamental dimensions exist in OpenFOAM?</b></summary>

**7**: M (mass), L (length), T (time), Θ (temperature), mol (amount), A (current), cd (luminous intensity)
</details>

<details>
<summary><b>2. How do you multiply two dimensionSets?</b></summary>

**Add exponents component-wise** — [1 0 0] × [0 1 0] = [1 1 0]
</details>

<details>
<summary><b>3. What does dimensionless mean?</b></summary>

**All exponents = 0** — [0 0 0 0 0 0 0] (no physical dimensions)
</details>

<details>
<summary><b>4. How would you create dimensions for thermal conductivity?</b></summary>

```cpp
dimensionSet dimThermalConductivity(1, 1, -3, -1, 0, 0, 0);
// or
dimensionSet dimThermalConductivity = dimPower / dimLength / dimTemperature;
```
</details>

---

## 📖 Related Documentation

- **Overview:** [00_Overview.md](00_Overview.md)
- **Arithmetic:** [03_Dimension_Arithmetic.md](03_Dimension_Arithmetic.md)
- **Validation:** [04_Non_Dimensionalization.md](04_Non_Dimensionalization.md)