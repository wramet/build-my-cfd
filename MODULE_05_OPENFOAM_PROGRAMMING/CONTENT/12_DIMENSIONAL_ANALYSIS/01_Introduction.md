# Introduction to Dimensional Analysis

## Learning Objectives

By the end of this section, you will be able to:
- Understand what dimensional analysis is and why OpenFOAM implements it
- Explain how OpenFOAM's dimension system prevents unit mismatch errors
- Apply dimensional analysis correctly when writing CFD code
- Avoid common pitfalls when working with dimensionless quantities

## What is Dimensional Analysis?

Dimensional analysis is a systematic method for verifying the consistency of physical equations by checking that all terms have compatible units. OpenFOAM implements this as a compile-time and runtime checking system that acts as a safety net for CFD simulations.

The core principle, first formalized by Fourier in 1822, states that all terms in a physically meaningful equation must have identical dimensions. Only quantities with matching dimensions can be meaningfully compared, added, or equated.

## Why Does OpenFOAM Need It?

In complex CFD calculations, we handle transport equations with multiple terms:
- Convection terms (m/s²)
- Diffusion terms (m/s²)
- Source terms (m/s²)

If you forget to divide by area or multiply by time in any term, the units change immediately. In other CFD software, you might not realize this until results diverge. In OpenFOAM, **the program stops immediately and reports the error**.

This provides several critical benefits:

1. **Physical Consistency**: Ensures all equations remain dimensionally balanced
2. **Error Prevention**: Detects unit-related bugs before they corrupt results
3. **Verification**: Additional checks for numerical schemes
4. **Debugging**: Helps identify sources of numerical instability

## How OpenFOAM Implements It

OpenFOAM enforces dimensional consistency through several key components:

### dimensionSet Class

The core data structure representing physical dimensions using SI base units:

| Base Unit | Symbol | Description |
|-----------|--------|-------------|
| Mass | M | kg |
| Length | L | m |
| Time | T | s |
| Temperature | Θ | K |
| Amount | N | mol |
| Current | I | A |
| Luminosity | J | cd |

### Dimensioned Types

Template classes that combine values with their dimensions:

```cpp
// Pressure field with dimensions (M·L⁻¹·T⁻²)
dimensionedScalar p("p", dimPressure, 101325.0);

// Velocity vector field with dimensions (L·T⁻¹)
dimensionedVector U("U", dimVelocity, vector(1.0, 0, 0));
```

### Compile-Time Checking

```cpp
// This will fail to compile - dimension mismatch error
// Velocity (L/T) cannot be added to Pressure (M·L⁻¹·T⁻²)
dimensionedScalar invalidSum = U + p;  // Error!

// Correct approach: only add quantities with same dimensions
dimensionedScalar velocitySum = U + U;  // OK
```

### Automatic Dimension Assignment

Fields automatically carry physical meaning through database lookup:

```cpp
// Temperature field - automatically has dimTemperature
volScalarField T(io, "T", mesh);

// Velocity field - automatically has dimVelocity
volVectorField U(io, "U", mesh);

// Pressure field - automatically has dimPressure
volScalarField p(io, "p", mesh);
```

## Examples

### Navier-Stokes Dimensional Analysis

For incompressible flow:
$$\rho \frac{\partial \mathbf{u}}{\partial t} + \rho (\mathbf{u} \cdot \nabla) \mathbf{u} = -\nabla p + \mu \nabla^2 \mathbf{u} + \mathbf{f}$$

| Term | Dimensions |
|------|------------|
| Transient: $\rho \frac{\partial \mathbf{u}}{\partial t}$ | M/(L²·T²) |
| Convection: $\rho (\mathbf{u} \cdot \nabla) \mathbf{u}$ | M/(L²·T²) |
| Pressure gradient: $-\nabla p$ | M/(L²·T²) |

All terms have identical dimensions, confirming dimensional consistency.

### Multiphase Flow

Volume fraction transport:
$$\frac{\partial \alpha}{\partial t} + \mathbf{u} \cdot \nabla \alpha = 0$$

```cpp
// Volume fraction field (dimensionless: 0 to 1)
volScalarField alpha
(
    IOobject("alpha", runTime.timeName(), mesh),
    mesh,
    dimensionedScalar("alpha", dimless, 0.0)
);

// Dilatation error field (T⁻¹)
volScalarField dilatationError
(
    IOobject("dilatationError", runTime.timeName(), mesh),
    mesh,
    dimensionedScalar(inv(dimTime), 0)
);
```

## Common Pitfalls

### Dimensionless Numbers

**Bad Practice**: Losing dimensional information

```cpp
// ❌ BAD - loses traceability
dimensionedScalar Re("Re", dimless, 1000.0);
```

**Better Approach**: Calculate from dimensional quantities

```cpp
// ✅ BETTER - preserves dimensional form
dimensionedScalar U_ref("U_ref", dimVelocity, 1.0);
dimensionedScalar L_ref("L_ref", dimLength, 1.0);
dimensionedScalar nu_ref("nu_ref", dimKinematicViscosity, 1e-6);

// Calculate dimensionless number from dimensional quantities
dimensionedScalar Re = U_ref * L_ref / nu_ref;
```

### Custom Boundary Conditions

When creating custom BCs, specify dimensions correctly:

```cpp
class MyBoundaryCondition : public fvPatchField<scalar>
{
    MyBoundaryCondition
    (
        const fvPatch& p,
        const DimensionedField<scalar, volMesh>& iF,
        const dictionary& dict
    )
    :
        // Must specify correct dimensions
        fvPatchField<scalar>(p, iF, dict, dimless)
    {}
};
```

## Quick Reference

| Concept | Key Point |
|---------|-----------|
| Principle | All terms in an equation must have identical dimensions |
| dimensionSet | Stores 7 exponents of SI base units [M, L, T, Θ, N, I, J] |
| dimensionedScalar | Scalar value + dimensions |
| dimensionedVector | Vector value + dimensions |
| dimPressure | M·L⁻¹·T⁻² (Pascal) |
| dimVelocity | L·T⁻¹ (m/s) |
| dimless | No dimensions (dimensionless) |
| Compile-time check | Catches dimension errors during compilation |
| Runtime check | Validates field operations during simulation |

## Key Takeaways

1. **Safety First**: OpenFOAM's dimensional system acts as a compile-time safety net that catches unit mismatches before runtime

2. **Self-Documenting**: Dimensions serve as embedded documentation—code automatically carries physical meaning

3. **Best Practice**: Preserve dimensional form for reference values, then calculate dimensionless numbers from them

4. **Multiphysics Safety**: The system prevents mixing incompatible physical quantities in complex simulations

5. **Minimal Overhead**: Dimension checking has negligible performance cost—compile-time checks are optimized away, runtime checks occur only during initialization

## Concept Check

<details>
<summary><b>1. Why does `dimensionedScalar invalidSum = U + p;` cause a compile error?</b></summary>

Because **dimensions don't match:**
- `U` has dimensions **L/T** (velocity)
- `p` has dimensions **M/(L·T²)** (pressure)

**Rule**: Only quantities with **identical dimensions** can be added/subtracted.

**Correct example:**
```cpp
dimensionedScalar validSum = U1 + U2;  // velocity + velocity = OK
```

</details>

<details>
<summary><b>2. What does dimensionSet store in OpenFOAM?</b></summary>

Stores **7 exponents** of SI base units:

| Index | Unit | Symbol | Example |
|-------|------|--------|---------|
| 0 | Mass | M | kg |
| 1 | Length | L | m |
| 2 | Time | T | s |
| 3 | Temperature | Θ | K |
| 4 | Moles | N | mol |
| 5 | Current | I | A |
| 6 | Luminosity | J | cd |

**Example:**
- Pressure: `[1 -1 -2 0 0 0 0]` = M·L⁻¹·T⁻² = Pa

</details>

<details>
<summary><b>3. How should Reynolds number be calculated in OpenFOAM?</b></summary>

**Correct way**: Calculate from dimensional quantities

```cpp
// Preserve dimensional reference values
dimensionedScalar U_ref("U_ref", dimVelocity, 1.0);  // m/s
dimensionedScalar L_ref("L_ref", dimLength, 1.0);    // m
dimensionedScalar nu("nu", dimKinematicViscosity, 1e-6); // m²/s

// Calculate Re (automatically dimensionless)
dimensionedScalar Re = U_ref * L_ref / nu;
```

**Benefit**: Maintains traceability and enables validation

</details>

## Related Documentation

- **Overview**: [00_Overview.md](00_Overview.md) — Dimensional Analysis overview
- **Next**: [02_dimensionSet.md](02_dimensionSet.md) — The dimensionSet class
- **Field Types**: [../08_FIELD_TYPES/00_Overview.md](../08_FIELD_TYPES/00_Overview.md) — Field types
- **Tensor Algebra**: [../11_TENSOR_ALGEBRA/00_Overview.md](../11_TENSOR_ALGEBRA/00_Overview.md) — Previous module