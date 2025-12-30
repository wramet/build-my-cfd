# Dimensional Analysis - Overview

## Learning Objectives

By the end of this module, you will be able to:
- Understand how OpenFOAM's dimension system prevents physics errors
- Use `dimensionSet` to define physical dimensions correctly
- Apply `dimensionedScalar` for dimension-aware quantities
- Leverage automatic dimension checking to catch bugs early

---

## What is Dimensional Analysis?

> **💡 Dimensional Analysis = Physics Safety Net**
>
> Dimensional analysis in OpenFOAM provides compile-time and runtime checking of physical dimensions, preventing you from adding pressure to velocity or making other physics mistakes.

**Core Concept:** Every physical quantity in OpenFOAM carries its dimensions (mass, length, time, etc.), and operations are automatically validated for dimensional consistency.

---

## Why Use Dimensional Analysis?

| Problem | Solution |
|---------|----------|
| Physics errors are hard to debug | OpenFOAM catches them at runtime |
| Unit conversions cause bugs | Dimensions are tracked consistently |
| Code reviews miss dimension mistakes | Automatic checking prevents them |
| Complex equations hide errors | DimensionSet validates every operation |

**Key Insight:** If you try to add pressure [Pa] to velocity [m/s], OpenFOAM will error immediately - saving you hours of debugging.

---

## How It Works

### 1. dimensionSet - 7 Base Dimensions

```cpp
// Format: dimensionSet(M, L, T, Θ, mol, A, cd)
dimensionSet dimVelocity(0, 1, -1, 0, 0, 0, 0);     // m/s
dimensionSet dimPressure(1, -1, -2, 0, 0, 0, 0);    // Pa = kg/(m·s²)
dimensionSet dimDensity(1, -3, 0, 0, 0, 0, 0);      // kg/m³
```

**Base Dimensions:** Mass [M], Length [L], Time [T], Temperature [Θ], Amount [mol], Current [A], Luminous [cd]

### 2. dimensionedScalar - Dimension-Aware Values

```cpp
dimensionedScalar rho
(
    "rho",              // Name
    dimDensity,         // Dimensions: [kg/m³]
    1000                // Value: 1000 kg/m³
);

dimensionedScalar nu
(
    "nu",
    dimensionSet(0, 2, -1, 0, 0, 0, 0),  // m²/s
    1e-6
);
```

### 3. Automatic Dimension Checking

```cpp
// Valid operations - dimensions match
volScalarField dynamicPressure = rho * sqr(U);     // [kg/m³]·[m²/s²] = [Pa] ✓

// Invalid operations - compile/runtime error
// volScalarField nonsense = p + U;  // [Pa] + [m/s] = ERROR!
```

---

## Common dimensionSet Values

| Quantity | dimensionSet | SI Unit |
|----------|--------------|---------|
| Length | `[0 1 0 0 0 0 0]` | m |
| Area | `[0 2 0 0 0 0 0]` | m² |
| Volume | `[0 3 0 0 0 0 0]` | m³ |
| Velocity | `[0 1 -1 0 0 0 0]` | m/s |
| Acceleration | `[0 1 -2 0 0 0 0]` | m/s² |
| Density | `[1 -3 0 0 0 0 0]` | kg/m³ |
| Pressure | `[1 -1 -2 0 0 0 0]` | Pa |
| Dynamic Viscosity | `[1 -1 -1 0 0 0 0]` | Pa·s |
| Kinematic Viscosity | `[0 2 -1 0 0 0 0]` | m²/s |
| Temperature | `[0 0 0 1 0 0 0]` | K |
| Energy | `[1 2 -2 0 0 0 0]` | J |
| Power | `[1 2 -3 0 0 0 0]` | W |
| Dimensionless | `[0 0 0 0 0 0 0]` | - |

---

## Module Structure

| File | Content | Focus |
|------|---------|-------|
| 01_Introduction | What & Why | Motivation and basic concepts |
| 02_DimensionSet | Technical Details | Advanced dimensionSet operations |
| 03_Arithmetic | Operations | Dimension-aware arithmetic |
| 04_Non_Dim | Scaling | Non-dimensionalization techniques |
| 05_Advanced | Applications | Real-world use cases |
| 06_Pitfalls | Debugging | Common errors and solutions |
| 07_Summary | Practice | Exercises and review |

---

## Quick Reference

| Need | Syntax | Example |
|------|--------|---------|
| Standard velocity | `dimVelocity` | `dimensionedScalar U("U", dimVelocity, 1.0);` |
| Standard pressure | `dimPressure` | `dimensionedScalar p("p", dimPressure, 101325);` |
| Standard density | `dimDensity` | `dimensionedScalar rho("rho", dimDensity, 1000);` |
| Dimensionless | `dimless` | `dimensionedScalar Re("Re", dimless, 1000);` |
| Custom dimension | `dimensionSet(M,L,T,Θ,mol,A,cd)` | `dimensionSet(0, 1, -1, 0, 0, 0, 0)` |
| Volume | `dimVolume` | `[0 3 0 0 0 0 0]` |
| Area | `dimArea` | `[0 2 0 0 0 0 0]` |
| Time | `dimTime` | `[0 0 1 0 0 0 0]` |
| Mass | `dimMass` | `[1 0 0 0 0 0 0]` |
| Temperature | `dimTemperature` | `[0 0 0 1 0 0 0]` |

---

## Key Takeaways

✓ **dimensionSet** uses 7 base dimensions: M, L, T, Θ, mol, A, cd

✓ **dimensionedScalar** combines name, dimensions, and value

✓ **Automatic checking** prevents physics errors at runtime

✓ **Operations** must be dimensionally consistent or code will fail

✓ **Use predefined dimensions** (`dimVelocity`, `dimPressure`) for common cases

---

## Concept Check

<details>
<summary><b>1. How many base dimensions does dimensionSet use?</b></summary>

**7**: Mass [M], Length [L], Time [T], Temperature [Θ], Amount [mol], Current [A], Luminous [cd]
</details>

<details>
<summary><b>2. What happens if you add pressure [Pa] to velocity [m/s]?</b></summary>

**Runtime error** - OpenFOAM's dimension checking prevents operations with incompatible dimensions
</details>

<details>
<summary><b>3. How do you create a dimensionedScalar for density?</b></summary>

```cpp
dimensionedScalar rho
(
    "rho",              // name
    dimDensity,         // [kg/m³]
    1000                // value
);
```
</details>

<details>
<summary><b>4. What is the dimensionSet for kinematic viscosity (m²/s)?</b></summary>

`dimensionSet(0, 2, -1, 0, 0, 0, 0)` - Length² / Time
</details>

---

## Related Documentation

- **Introduction:** [01_Introduction.md](01_Introduction.md)
- **DimensionSet Advanced:** [02_DimensionSet_Advanced.md](02_DimensionSet_Advanced.md)
- **Arithmetic Operations:** [03_Arithmetic_Operations.md](03_Arithmetic_Operations.md)