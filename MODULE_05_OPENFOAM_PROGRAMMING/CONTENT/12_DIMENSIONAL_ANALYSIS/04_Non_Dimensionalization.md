# Non-Dimensionalization

---

## Learning Objectives

By the end of this section, you will be able to:

- **Understand** the purpose and benefits of non-dimensionalization in CFD
- **Apply** scaling techniques to variables in OpenFOAM
- **Calculate** common non-dimensional numbers (Re, Pr, Ma, Nu)
- **Implement** non-dimensional forms of governing equations
- **Recognize** when non-dimensionalization is necessary in practical CFD workflows

---

## Overview

**Non-dimensionalization** scales quantities to be dimensionless, reducing the number of parameters while improving numerical stability and enabling comparison across different physical scales.

---

## 1. What is Non-Dimensionalization?

Non-dimensionalization transforms physical quantities into dimensionless form by dividing by appropriate reference scales:

```cpp
// Dimensional → Non-dimensional
U* = U / Uref      // velocity scale
p* = p / pref      // pressure scale
x* = x / Lref      // length scale
t* = t * Uref / L  // time scale
```

---

## 2. Why Non-Dimensionalize?

| Benefit | Description | Impact |
|---------|-------------|--------|
| **Simplify** | Reduce number of parameters | Fewer simulations needed |
| **Compare** | Different scales/flows | Universal similarity |
| **Stability** | Values near O(1) | Better convergence |
| **Generalize** | Universal solutions | Applicable to multiple cases |

---

## 3. When to Use Non-Dimensionalization

### Practical CFD Workflow Scenarios:

**1. Validation Studies**
- Compare with experimental data at different scales
- Match non-dimensional numbers (Re, Ma) instead of absolute values

**2. Parametric Studies**
- Sweep Reynolds number from 1e3 to 1e6
- Single non-dimensional parameter replaces multiple dimensional combinations

**3. Turbulence Modeling**
- y+ calculation for wall functions
- Near-wall mesh sizing based on Re_tau

**4. Convergence Issues**
- Variables span orders of magnitude (e.g., pressure in Pa vs mmHg)
- Scaling improves solver stability

**5. Multi-Physics Problems**
- Identify dominant dimensionless groups
- Reduce parameter space for optimization

```cpp
// Example: Turbulent pipe flow validation
// Instead of: U=[1,10,100] m/s, D=[0.01,0.1,1] m, ν=1e-5 m²/s
// Use: Re=[1000, 10000, 100000]
dimensionedScalar Re_target("Re", dimless, 10000);
dimensionedScalar U_calc = Re_target * nu / D;
```

---

## 4. Reference Quantities in OpenFOAM

```cpp
// Define reference values in transportProperties
dimensionedScalar Uref
(
    "Uref",
    dimVelocity,
    dict.subDict("referenceValues").lookup("U")
);

dimensionedScalar Lref
(
    "Lref",
    dimLength,
    dict.subDict("referenceValues").lookup("L")
);

dimensionedScalar pref
(
    "pref",
    dimPressure,
    dict.subDict("referenceValues").lookup("p")
);
```

---

## 5. Non-Dimensional Variables

```cpp
// Non-dimensional velocity field
volVectorField Ustar
(
    IOobject("Ustar", runTime.timeName(), mesh),
    U / Uref
);

// Non-dimensional pressure (dynamic pressure scaling)
volScalarField pstar
(
    IOobject("pstar", runTime.timeName(), mesh),
    p / (rho * sqr(Uref))
);

// Non-dimensional coordinates
volVectorField xstar
(
    IOobject("xstar", runTime.timeName(), mesh),
    mesh.C() / Lref
);
```

---

## 6. Common Non-Dimensional Numbers

```cpp
// Reynolds number: inertia/viscous forces
dimensionedScalar Re = Uref * Lref / nu;

// Prandtl number: momentum/thermal diffusivity
dimensionedScalar Pr = nu / alpha;

// Mach number: compressibility
volScalarField Ma = mag(U) / c;

// Nusselt number: convection/conduction
volScalarField Nu = h * Lref / k;

// Strouhal number: vortex shedding frequency
dimensionedScalar St = f * Lref / Uref;

// Froude number: inertia/gravity
dimensionedScalar Fr = Uref / sqrt(g * Lref);
```

---

## 7. Scaling in Governing Equations

### Dimensional Form:
```
ρ(∂U/∂t + U·∇U) = -∇p + μ∇²U
```

### Non-Dimensional Form:
```
∂U*/∂t* + U*·∇*U* = -∇*p* + (1/Re)∇*²U*
```

### OpenFOAM Implementation:

```cpp
// Non-dimensional momentum equation
tmp<fvVectorMatrix> tUEqn
(
    fvm::ddt(Ustar)
  + fvm::div(phi_star, Ustar)
 ==
    fvc::grad(pstar) / rho_star
  + fvm::laplacian(1.0/Re, Ustar)
);

// Non-dimensional energy equation
tmp<fvScalarMatrix> tTEqn
(
    fvm::ddt(Tstar)
  + fvm::div(phi_star, Tstar)
 ==
    fvm::laplacian(1.0/(Re*Pr), Tstar)
);
```

---

## 8. Non-Dimensional Groups Reference

| Number | Formula | Physical Meaning | Typical Use |
|--------|---------|------------------|-------------|
| **Re** | ρUL/μ | Inertia/Viscous | Turbulence, transition |
| **Ma** | U/c | Flow speed/sound | Compressibility effects |
| **Pr** | ν/α | Momentum/Thermal | Heat transfer correlation |
| **Nu** | hL/k | Convection/Conduction | Heat transfer coefficient |
| **Fr** | U/√(gL) | Inertia/Gravity | Free surface flows |
| **St** | fL/U | Unsteady/Convective | Vortex shedding |
| **Ec** | U²/cₚT | Kinetic/Enthalpy | Viscous dissipation |
| **y+** | u*y/ν | Wall distance | Turbulent boundary layers |

---

## Quick Reference

### Variable Scaling Table

| Variable | Dimensionless Form | Reference Scale |
|----------|-------------------|-----------------|
| Velocity | `U* = U/Uref` | Characteristic velocity |
| Pressure | `p* = p/(ρU²)` | Dynamic pressure |
| Time | `t* = t·Uref/L` | Convective time scale |
| Length | `x* = x/Lref` | Characteristic length |
| Temperature | `T* = (T-T₀)/(Tref-T₀)` | Temperature difference |

### Common Pressure Scales

| Application | Scaling |
|-------------|---------|
| Incompressible flow | `p* = p/(ρU²)` |
| External aerodynamics | `p* = (p-p∞)/(0.5ρU²)` |
| Low Mach number | `p* = p/pref` |

---

## Key Takeaways

✓ **Non-dimensionalization reduces complexity** - Fewer parameters, universal solutions

✓ **Improves numerical stability** - Values near O(1) enhance convergence

✓ **Enables similarity comparisons** - Different scales, same physics

✓ **Essential for validation** - Match experimental conditions via dimensionless groups

✓ **Standard practice in turbulence** - y+, Reτ for near-wall modeling

✓ **Choose reference scales carefully** - Physical meaningful values matter

✓ **Common in CFD workflows** - Parametric studies, optimization, validation

---

## 🧠 Concept Check

<details>
<summary><b>1. Why non-dimensionalize CFD problems?</b></summary>

**Reduces parameters**, improves numerical stability, enables comparison across different scales
</details>

<details>
<summary><b>2. What does high Reynolds number indicate?</b></summary>

**Inertia dominates** over viscous forces → turbulent flow regime
</details>

<details>
<summary><b>3. Which pressure scaling for incompressible flow?</b></summary>

**Dynamic pressure**: `p* = p/(ρU²)` or `p* = (p-p∞)/(0.5ρU²)` for external flows
</details>

<details>
<summary><b>4. When is non-dimensionalization most useful?</b></summary>

**Parametric studies**, validation against experiments, convergence issues with disparate scales, turbulence modeling (y+, Reτ)
</details>

<details>
<summary><b>5. How does y+ relate to non-dimensionalization?</b></summary>

**y+ = u*y/ν** scales wall distance by viscous length scale → determines mesh resolution requirements for wall functions
</details>

---

## 📖 Related Documentation

- **Mathematical Formulations:** [07_Mathematical_Formulations.md](07_Mathematical_Formulations.md)
- **Dimension Arithmetic:** [03_Dimension_Arithmetic.md](03_Dimension_Arithmetic.md)
- **Overview:** [00_Overview.md](00_Overview.md)