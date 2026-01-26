# Mathematical Formulations

Advanced Dimensional Analysis in OpenFOAM — Buckingham π Theorem and Non-Dimensionalization

---

## Learning Objectives

By the end of this section, you will be able to:
- Apply **Buckingham π theorem** to derive dimensionless groups
- Understand the mathematical foundation of **non-dimensionalization** 
- Perform dimensional analysis on tensor equations
- Implement dimension-aware computations in OpenFOAM

---

## Overview

> **💡 Dimensional Analysis = Discovering Physics Invariants**
>
> Every physical law must be dimensionally consistent. Dimensionless groups (Re, Fr, Nu) capture essential physics while reducing parameter space.

**Why This Matters:**
- **Theory Foundation:** Understand the mathematics behind dimensional consistency
- **Derivation Tool:** Buckingham π theorem systematically finds dimensionless groups
- **Numerical Stability:** Non-dimensionalization improves computational accuracy
- **Similarity Analysis:** Scale experimental results to prototype conditions

**Key Topics:**
1. Buckingham π theorem for systematic dimensional analysis
2. dimensionSet class implementation details
3. Non-dimensionalization of governing equations
4. Similarity and scaling laws
5. Tensor dimensional analysis
6. OpenFOAM implementation techniques

---

## 1. Buckingham π Theorem

### 1.1 Mathematical Principle

For a physical relationship involving1$n1variables with1$k1fundamental dimensions:

$$f(Q_1, Q_2, ..., Q_n) = 0$$

The theorem guarantees we can form1$n - k1independent dimensionless π-groups:

$$\Pi_m = \prod_{i=1}^n Q_i^{b_{im}} \quad \text{for} \quad m = 1, 2, ..., n-k$$

### 1.2 Systematic Procedure

1. **List all variables** and their dimensions
2. **Count fundamental dimensions** ($k$)
3. **Choose repeating variables** ($k1variables that don't form dimensionless group)
4. **Form π-groups** by combining repeating variables with each remaining variable
5. **Solve exponent equations** for dimensional consistency

### 1.3 Example: Pipe Flow Pressure Drop

**Variables:**1$\Delta p, \rho, \mu, U, D$

| Variable | Symbol | Dimension | Role |
|----------|--------|-----------|------|
| Pressure drop |1$\Delta p1|1$[ML^{-1}T^{-2}]1| Dependent |
| Density |1$\rho1|1$[ML^{-3}]1| Repeating |
| Viscosity |1$\mu1|1$[ML^{-1}T^{-1}]1| Repeating |
| Velocity |1$U1|1$[LT^{-1}]1| Repeating |
| Diameter |1$D1|1$[L]1| Repeating |

$n = 51variables,1$k = 31dimensions (M, L, T) →1$5 - 3 = 21dimensionless groups

**π₁ (Euler number):**
$$\Pi_1 = \Delta p \cdot \rho^a \cdot \mu^b \cdot U^c \cdot D^d$$

Solving for dimensional consistency:
$$Eu = \frac{\Delta p}{\rho U^2}$$

**π₂ (Reynolds number):**
$$\Pi_2 = \mu \cdot \rho^a \cdot U^c \cdot D^d$$

$$Re = \frac{\rho U D}{\mu}$$

**Final relationship:**
$$Eu = f(Re)$$

---

## 2. dimensionSet Class Architecture

### 2.1 Seven Base Dimensions

OpenFOAM uses SI base units with 7 fundamental dimensions:

$$[M, L, T, \Theta, I, N, J]$$

| Position | Dimension | Symbol | Unit |
|----------|-----------|--------|------|
| 0 | Mass | M | kg |
| 1 | Length | L | m |
| 2 | Time | T | s |
| 3 | Temperature | Θ | K |
| 4 | Electric Current | I | A |
| 5 | Amount of Substance | N | mol |
| 6 | Luminous Intensity | J | cd |

### 2.2 Constructor Syntax

```cpp
// Full constructor: [M, L, T, Θ, I, N, J]
dimensionSet(1, -1, -2, 0, 0, 0, 0)  // Pressure [Pa]
dimensionSet(0, 1, -1, 0, 0, 0, 0)   // Velocity [m/s]
dimensionSet(1, -3, 0, 0, 0, 0, 0)   // Density [kg/m³]
dimensionSet(1, -1, -1, 0, 0, 0, 0)  // Dynamic viscosity [Pa·s]
dimensionSet(2, -1, -3, 0, 0, 0, 0)  // Power [W]
```

### 2.3 Predefined Dimension Aliases

> **📚 Reference:** See [03_Implementation_Mechanisms.md](03_Implementation_Mechanisms.md) for complete dimensionSet operations

| Alias | dimensionSet | Physical Quantity |
|-------|--------------|-------------------|
| `dimless` | `[0 0 0 0 0 0 0]` | Dimensionless |
| `dimMass` | `[1 0 0 0 0 0 0]` | Mass |
| `dimLength` | `[0 1 0 0 0 0 0]` | Length |
| `dimTime` | `[0 0 1 0 0 0 0]` | Time |
| `dimTemperature` | `[0 0 0 1 0 0 0]` | Temperature |
| `dimVelocity` | `[0 1 -1 0 0 0 0]` | Velocity |
| `dimAcceleration` | `[0 1 -2 0 0 0 0]` | Acceleration |
| `dimDensity` | `[1 -3 0 0 0 0 0]` | Density |
| `dimPressure` | `[1 -1 -2 0 0 0 0]` | Pressure |
| `dimViscosity` | `[1 -1 -1 0 0 0 0]` | Dynamic viscosity |
| `dimKinematicViscosity` | `[0 2 -1 0 0 0 0]` | Kinematic viscosity |

---

## 3. Non-Dimensionalization

### 3.1 Motivation

**Why Non-Dimensionalize?**
1. **Numerical Stability:** Dimensionless variables are O(1), improving solver convergence
2. **Parameter Reduction:** Fewer independent parameters to explore
3. **Generalization:** Results apply to geometrically similar systems
4. **Scaling Analysis:** Identify dominant physical mechanisms

### 3.2 Reference Scales

Choose characteristic scales for each variable:

| Quantity | Scale | Dimensional | Dimensionless |
|----------|-------|-------------|---------------|
| Length |1$L_{ref}1|1$\mathbf{x} = L_{ref} \tilde{\mathbf{x}}1|1$\tilde{\mathbf{x}} = \mathbf{x}/L_{ref}1|
| Velocity |1$U_{ref}1|1$\mathbf{u} = U_{ref} \tilde{\mathbf{u}}1|1$\tilde{\mathbf{u}} = \mathbf{u}/U_{ref}1|
| Time |1$L_{ref}/U_{ref}1|1$t = (L_{ref}/U_{ref}) \tilde{t}1|1$\tilde{t} = t U_{ref}/L_{ref}1|
| Pressure |1$\rho U_{ref}^21|1$p = \rho U_{ref}^2 \tilde{p}1|1$\tilde{p} = p/(\rho U_{ref}^2)1|

### 3.3 Navier-Stokes Transformation

**Dimensional Form:**
$$\rho \frac{\partial \mathbf{u}}{\partial t} + \nabla \cdot (\rho \mathbf{u} \mathbf{u}) = -\nabla p + \nabla \cdot (\mu \nabla \mathbf{u})$$

**Substitute Reference Scales:**
$$\rho \frac{U_{ref}}{L_{ref}/U_{ref}} \frac{\partial \tilde{\mathbf{u}}}{\partial \tilde{t}} + \frac{\rho U_{ref}^2}{L_{ref}} \tilde{\nabla} \cdot (\tilde{\mathbf{u}} \tilde{\mathbf{u}}) = -\frac{\rho U_{ref}^2}{L_{ref}} \tilde{\nabla} \tilde{p} + \frac{\mu U_{ref}}{L_{ref}^2} \tilde{\nabla}^2 \tilde{\mathbf{u}}$$

**Divide by1$\rho U_{ref}^2/L_{ref}$:**
$$\frac{\partial \tilde{\mathbf{u}}}{\partial \tilde{t}} + \tilde{\nabla} \cdot (\tilde{\mathbf{u}} \tilde{\mathbf{u}}) = -\tilde{\nabla} \tilde{p} + \frac{1}{Re} \tilde{\nabla}^2 \tilde{\mathbf{u}}$$

**Result:** Single dimensionless parameter ($Re$) governs the entire flow physics!

### 3.4 Energy Equation Non-Dimensionalization

**Dimensional:**
$$\rho c_p \frac{\partial T}{\partial t} + \rho c_p \mathbf{u} \cdot \nabla T = k \nabla^2 T$$

**Dimensionless:**
$$\frac{\partial \tilde{T}}{\partial \tilde{t}} + \tilde{\mathbf{u}} \cdot \tilde{\nabla} \tilde{T} = \frac{1}{Re Pr} \tilde{\nabla}^2 \tilde{T}$$

Where:
- **Prandtl number:**1$Pr = \frac{\mu c_p}{k} = \frac{\nu}{\alpha}$
- **Péclet number:**1$Pe = Re \cdot Pr$

---

## 4. Similarity and Scaling Laws

### 4.1 Reynolds Similarity

For dynamically similar flows:
$$Re_{model} = Re_{prototype}$$

$$\frac{\rho_m U_m L_m}{\mu_m} = \frac{\rho_p U_p L_p}{\mu_p}$$

**Scaling Example:**
- Model scale:1$1:101($L_m = 0.1 L_p$)
- Same fluid ($\rho_m = \rho_p, \mu_m = \mu_p$)
- Required velocity:1$U_m = 10 U_p$

### 4.2 Key Dimensionless Numbers

| Number | Formula | Physical Ratio | Application |
|--------|---------|----------------|-------------|
| **Reynolds** |1$Re = \frac{\rho U L}{\mu}1| Inertia/Viscosity | Viscous flows, turbulence |
| **Froude** |1$Fr = \frac{U}{\sqrt{gL}}1| Inertia/Gravity | Free surface flows, ships |
| **Euler** |1$Eu = \frac{\Delta p}{\rho U^2}1| Pressure/Inertia | Pressure drop, cavitation |
| **Weber** |1$We = \frac{\rho U^2 L}{\sigma}1| Inertia/Surface tension | Sprays, bubbles, droplets |
| **Mach** |1$Ma = \frac{U}{c}1| Velocity/Sound speed | Compressible flow |
| **Strouhal** |1$St = \frac{f L}{U}1| Frequency/Convection | Vortex shedding, acoustics |
| **Prandtl** |1$Pr = \frac{\nu}{\alpha}1| Momentum/Thermal diffusion | Heat transfer |
| **Nusselt** |1$Nu = \frac{h L}{k}1| Convective/Conductive heat transfer | Heat transfer coefficient |
| **Grashof** |1$Gr = \frac{g \beta \Delta T L^3}{\nu^2}1| Buoyancy/Viscous forces | Natural convection |

### 4.3 Incomplete Similarity

When multiple dimensionless groups are involved, **complete similarity** is impossible:

**Example:** Ship model testing
- Reynolds similarity requires:1$U_m = \frac{L_p}{L_m} U_p$
- Froude similarity requires:1$U_m = \sqrt{\frac{L_m}{L_p}} U_p$

**Solution:** Match1$Fr1for wave effects, apply empirical corrections for1$Re1effects.

---

## 5. Tensor Dimensional Analysis

### 5.1 Stress Tensor Dimensional Consistency

**Newtonian Constitutive Law:**
$$\boldsymbol{\tau} = \mu \dot{\boldsymbol{\gamma}}$$

**Dimension Check:**

| Tensor | Dimension | dimensionSet |
|--------|-----------|--------------|
| Stress1$\boldsymbol{\tau}1|1$[ML^{-1}T^{-2}]1| `[1 -1 -2 0 0 0 0]` |
| Strain rate1$\dot{\boldsymbol{\gamma}}1|1$[T^{-1}]1| `[0 0 -1 0 0 0 0]` |
| Viscosity1$\mu1|1$[ML^{-1}T^{-1}]1| `[1 -1 -1 0 0 0 0]` |

**Verification:**
$$[\mu][\dot{\gamma}] = [ML^{-1}T^{-1}][T^{-1}] = [ML^{-1}T^{-2}] = [\boldsymbol{\tau}] \quad \checkmark$$

### 5.2 Convective Term Dimensional Analysis

**Term:**1$\nabla \cdot (\rho \mathbf{u} \mathbf{u})$

| Component | Dimension |
|-----------|-----------|
|1$\rho1|1$[ML^{-3}]1|
|1$\mathbf{u}1|1$[LT^{-1}]1|
|1$\mathbf{u} \mathbf{u}1|1$[L^2T^{-2}]1|
|1$\rho \mathbf{u} \mathbf{u}1|1$[ML^{-1}T^{-2}]1|
|1$\nabla \cdot (\cdot)1|1$[L^{-1}]1|
| **Result** |1$[MT^{-2}]1(momentum flux per volume) |

### 5.3 Reynolds Stress Tensor

**RANS closure:**1$-\rho \overline{\mathbf{u}' \mathbf{u}'}$

| Quantity | Dimension | Physical Meaning |
|----------|-----------|------------------|
| Velocity fluctuation1$\mathbf{u}'1|1$[LT^{-1}]1| Turbulent velocity |
|1$\mathbf{u}' \mathbf{u}'1|1$[L^2T^{-2}]1| Turbulent kinetic energy correlation |
|1$-\rho \overline{\mathbf{u}' \mathbf{u}'}1|1$[ML^{-1}T^{-2}]1| Turbulent momentum flux (stress) |

**Dimensional consistency:** Same dimensions as viscous stress1$\boldsymbol{\tau}$, allowing turbulence modeling via eddy viscosity1$\mu_t$.

---

## 6. OpenFOAM Implementation

### 6.1 Creating Dimensioned Quantities

```cpp
// Method 1: Using predefined dimensions
dimensionedScalar rho
(
    "rho",                      // name
    dimDensity,                 // dimensions
    1000                        // value [kg/m³]
);

dimensionedScalar nu
(
    "nu",
    dimKinematicViscosity,      // [m²/s]
    1e-6
);

// Method 2: Using dimensionSet constructor
dimensionedScalar p
(
    "p",
    dimensionSet(1, -1, -2, 0, 0, 0, 0),  // [Pa]
    101325
);

// Dimensioned vectors
dimensionedVector g
(
    "g",
    dimAcceleration,
    vector(0, 0, -9.81)  // [m/s²]
);
```

### 6.2 Automatic Dimension Checking

```cpp
// Dimensionless Reynolds number calculation
dimensionedScalar U("U", dimVelocity, 1.0);
dimensionedScalar L("L", dimLength, 0.1);
dimensionedScalar nu("nu", dimKinematicViscosity, 1e-6);

// This automatically yields dimensionless result
dimensionedScalar Re = U * L / nu;
Info << "Re = " << Re.value() 
     << " (dimensions: " << Re.dimensions() << ")" << endl;
// Output: Re = 100000 (dimensions: [0 0 0 0 0 0 0])

// Compile-time error: dimension mismatch
// dimensionedScalar invalid = p + U;  
// Error: no match for 'operator+'

// Force dimensionless (use with caution)
dimensionedScalar Re2 = U.dimensions().resetNonConst();
Re2.value() = U.value() * L.value() / nu.value();
```

### 6.3 Checking Dimensions at Runtime

```cpp
// Check if field is dimensionless
if (!Re.dimensions().dimensionless())
{
    WarningIn("myFunction")
        << "Reynolds number should be dimensionless, but has dimensions: "
        << Re.dimensions() << endl;
}

// Compare dimensions
if (p.dimensions() == dimPressure)
{
    Info << "Pressure field has correct dimensions" << endl;
}

// Get specific dimension component
scalar massDim = p.dimensions()[dimensionSet::MASS];  // = 1
scalar lengthDim = p.dimensions()[dimensionSet::LENGTH];  // = -1
```

### 6.4 Dimensionless Field Operations

```cpp
// Create dimensionless field from dimensional field
volScalarField ReField
(
    IOobject("Re", runTime.timeName(), mesh),
    mesh,
    dimensionedScalar("zero", dimless, 0)
);

// Compute Reynolds number field
ReField = rho * mag(U) * L / (rho * nu);
// Result: automatically dimensionless ✓

// Non-dimensionalize velocity
volScalarField U_tilde = U / URef;
U_tilde.dimensions().reset(dimless);
```

### 6.5 Disabling Dimension Checking (Advanced)

> **⚠️ Warning:** Only use this for debugging or validated dimensionless formulations

```cpp
// Disable checking globally
dimensionSet::checking(false);

// Perform operations without checking
dimensionedScalar result = p + U;  // No error!

// Re-enable checking
dimensionSet::checking(true);
```

---

## Quick Reference

> **📚 See Also:** [03_Implementation_Mechanisms.md](03_Implementation_Mechanisms.md) for complete dimensionSet API

| Task | Code | Notes |
|------|------|-------|
| **Create dimensioned scalar** | `dimensionedScalar("name", dims, value)` | Use predefined `dim*` when possible |
| **Get field dimensions** | `field.dimensions()` | Returns `const dimensionSet&` |
| **Check dimensionless** | `dims.dimensionless()` | Returns `bool` |
| **Reset dimensions** | `dims.reset(dimless)` | Use with caution |
| **Compare dimensions** | `dims1 == dims2` | Exact match required |
| **Disable checking** | `dimensionSet::checking(false)` | Global switch, use sparingly |
| **Non-dimensionalize** | `field /= refValue; field.dimensions().reset(dimless)` | Two-step process |

---

## 🧠 Concept Check

<details>
<summary><b>1. Why does Buckingham π theorem produce exactly n-k dimensionless groups?</b></summary>

The theorem is based on **linear algebra**: We have a dimensional matrix where each row represents a fundamental dimension and each column represents a variable. The rank of this matrix is at most1$k1(number of fundamental dimensions). The null space (solutions to the homogeneous system) has dimension1$n - \text{rank} \geq n - k$. Each independent null space vector corresponds to one dimensionless π-group.

**Physical intuition:** With1$k1fundamental dimensions, we need exactly1$k1"repeating variables" to express all dimensions. The remaining1$n-k1variables must combine with these to form dimensionless groups.
</details>

<details>
<summary><b>2. How do we choose which variables are "repeating variables"?</b></summary>

**Criteria for selecting repeating variables:**
1. **Must be independent:** No combination should be dimensionless
2. **Must span the dimension space:** Together, they contain all1$k1fundamental dimensions
3. **Should be physically meaningful:** Choose variables you can control or measure
4. **Avoid the dependent variable:** If1$\Delta p1is what you're solving for, don't use it as repeating

**Typical choices:** Characteristic length ($L$), velocity ($U$), fluid property ($\rho1or1$\mu$)

**Example:** For pipe flow, use1$D, U, \rho1(not1$\Delta p1or1$\mu$)
</details>

<details>
<summary><b>3. Why is1$\rho U_{ref}^21the standard pressure scale instead of just1$U_{ref}^2$?</b></summary>

**Dimensional consistency:** Pressure has units1$[ML^{-1}T^{-2}]$. Velocity squared is1$[L^2T^{-2}]1— we're missing the mass dimension! Multiplying by density1$\rho1adds the required1$[ML^{-3]1to get proper pressure units.

**Physical meaning:**1$\rho U^21represents **dynamic pressure** — the pressure generated by fluid motion. This is the natural scale for:
- Momentum equation: pressure gradients appear alongside1$\rho \mathbf{u} \cdot \nabla \mathbf{u}$
- Bernoulli equation:1$p + \frac{1}{2}\rho U^2 = \text{constant}$
- Drag coefficients:1$C_d = \frac{F_d}{\frac{1}{2}\rho U^2 A}$

**Alternative scales:** For low Mach number flows, sometimes use1$\mu U / L1(viscous pressure scale), leading to the Euler number1$Eu = \frac{\Delta p}{\rho U^2}$.
</details>

<details>
<summary><b>4. When is complete similarity impossible, and how do we handle it?</b></summary>

**Problem:** When multiple dimensionless groups govern the physics (e.g.,1$Re1and1$Fr1for ship resistance), we cannot simultaneously match all groups in a scaled model.

**Example:** Ship model at 1:10 scale
- Match1$Fr$:1$U_m = \sqrt{L_m/L_p} U_p = 0.316 U_p$
- Resulting1$Re_m$:1$0.316 \times 0.1 Re_p = 0.0316 Re_p1(mismatch!)

**Solutions:**
1. **Match the dominant group:** Match1$Fr1for wave-making resistance
2. **Apply empirical corrections:** Use ITTC-1978 method for viscous correction
3. **Use different fluids:** Change1$\mu1or1$\rho1to match both (often impractical)
4. **Computational supplement:** Use CFD to extrapolate to full scale

**Key principle:** Match the group that governs the physics you're studying, and correct for the rest.
</details>

<details>
<summary><b>5. How does OpenFOAM catch dimension mismatches at compile time vs runtime?</b></summary>

**Compile-time checking:**
```cpp
dimensionedScalar p("p", dimPressure, 101325);
dimensionedScalar U("U", dimVelocity, 1.0);

// This fails to compile:
auto result = p + U;  // No matching operator+
```
The C++ type system uses template metaprogramming to prevent operations between mismatched `dimensioned` types.

**Runtime checking:**
```cpp
volScalarField p(mesh.lookupObject<volScalarField>("p"));
volScalarField U(mesh.lookupObject<volScalarField>("U"));

// This compiles but fails at runtime if dimensions don't match:
volScalarField result = p + U;  // Runtime error in dimensionSet::operator+
```
Fields can be read from files with unknown dimensions, so checking happens when arithmetic is performed.

**Debugging:** OpenFOAM reports the exact dimension mismatch:
```
--> FOAM FATAL ERROR:
    dimensionSet::operator= : dimensions differ
    LHS dimensions: [1 -1 -2 0 0 0 0]
    RHS dimensions: [0 1 -1 0 0 0 0]
```
</details>

---

## 📖 Related Documents

### Within This Module
- **Previous:** [03_Implementation_Mechanisms.md](03_Implementation_Mechanisms.md) - How dimensionSet checks dimensions at compile time
- **Next:** [05_Pitfalls_and_Solutions.md](05_Pitfalls_and_Solutions.md) - Common dimensional analysis errors and fixes
- **Overview:** [00_Overview.md](00_Overview.md) - Module roadmap and prerequisites

### Cross-Module References
- **Boundary Conditions:** [05_Common_Boundary_Conditions_in_OpenFOAM.md](../../MODULE_01_CFD_FUNDAMENTALS/CONTENT/03_BOUNDARY_CONDITIONS/05_Common_Boundary_Conditions_in_OpenFOAM.md) - Dimensional consistency in BC specifications
- **Solver Selection:** [02_Standard_Solvers.md](../../MODULE_03_SINGLE_PHASE_FLOW/CONTENT/01_INCOMPRESSIBLE_FLOW_SOLVERS/02_Standard_Solvers.md) - Dimensionless parameters in solver choice

---

## 📚 Further Reading

### Classical Dimensional Analysis
1. **Bridgman, P. W.** (1922). *Dimensional Analysis*. Yale University Press.
   - Foundation of modern dimensional analysis methods

2. **Sonin, A. A.** (2001). *"The Physical Basis of Dimensional Analysis"* (MIT Course Notes)
   - Excellent treatment of Buckingham π theorem derivation

### Engineering Applications
3. **Barenblatt, G. I.** (2003). *Scaling*. Cambridge University Press.
   - Advanced similarity analysis and intermediate asymptotics

4. **White, F. M.** (2019). *Fluid Mechanics* (8th ed.). McGraw-Hill. Chapter 5.
   - Standard textbook treatment with practical examples

### OpenFOAM Dimension System
5. **OpenFOAM Source Code:** `src/OpenFOAM/dimensionSet/dimensionSet.H`
   - Complete class definition and operator overloads

6. **OpenFOAM Programmer's Guide:** Chapter 3 - "Dimensions and Units"
   - Official documentation for dimensioned types