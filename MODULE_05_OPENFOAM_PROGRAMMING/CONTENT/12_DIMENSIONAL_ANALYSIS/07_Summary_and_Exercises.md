# Summary & Exercises

```mermaid
mindmap
  root((Dimensional Analysis))
    dimensionSet
      SI Units (7 Dimensions)
      Exponent Storage
      isDimensionless()
    Arithmetic
      Add/Sub (Match required)
      Mul/Div (Exponent Sum/Diff)
      Pow/Sqrt
    Non-Dimensionalization
      Reference Scales
      Similarity (Re, Fr, Pr)
      Numerical Stability
    Advanced
      Multi-physics Coupling
      Custom Units
      Safety Net Mechanism
```

---

## 12.9. Summary: The Dimensional Safety Net

The OpenFOAM dimensional analysis system represents a foundational advancement in computational fluid dynamics safety and reliability, catching dimensional inconsistencies from the earliest stages of compilation or runtime initialization.

### Core Benefits of the Dimensional System

1. **Automatic Consistency Checking**: Prevents physically meaningless operations such as adding pressure to velocity
2. **Type-Level Physical Safety**: Embeds physical dimensions directly into the C++ type system to verify conservation laws in governing equations
3. **Non-Dimensionalization Support**: Facilitates improved numerical stability and enables similarity analysis
4. **Multi-Physics Integration**: Manages interactions between disparate physical domains (e.g., FSI, MHD) rigorously

> [!INFO] Key Principle
> The dimensional analysis system operates at **both compile-time and runtime** to automatically verify that all mathematical operations are dimensionally consistent, preventing unit conversion errors and physically invalid calculations.

### Fundamental Dimensional Algebra Rules

| Operation | Dimensional Requirement | Example |
|-----------|------------------------|---------|
| Addition/Subtraction | Identical dimensions in all 7 positions | `p + p` |
| Multiplication/Division | Exponents add/subtract algebraically | `velocity * time = length` |
| Power Operations | Exponent multiplied by power value | `length^2 = area` |
| Intrinsic Functions | Arguments must be **dimensionless** | `sin(angle)`, `exp(T/Tref)` |

### Conservation Law Verification

The dimensional system helps verify that conservation laws are correctly implemented by ensuring each term in a conservation equation has identical dimensions.

**Mass Conservation:**
$$\frac{\partial \rho}{\partial t} + \nabla \cdot (\rho \mathbf{u}) = 0$$

**Dimensional Check:**
- $\frac{\partial \rho}{\partial t}$: $[M \, L^{-3} \, T^{-1}]$
- $\nabla \cdot (\rho \mathbf{u})$: $[M \, L^{-3} \, T^{-1}]$

**Momentum Conservation:**
$$\rho \frac{\partial \mathbf{u}}{\partial t} + \rho (\mathbf{u} \cdot \nabla) \mathbf{u} = -\nabla p + \mu \nabla^2 \mathbf{u} + \mathbf{f}$$

**Dimensional Check:**
- All terms: $[M \, L^{-2} \, T^{-2}]$ (force per volume)

### Multi-Physics Integration Benefits

In complex multi-physics simulations, the dimensional safety net becomes even more valuable as it manages interactions between different physical domains:

```cpp
// Multi-physics coupling with automatic dimensional checking
// Heat transfer affects fluid properties through temperature-dependent viscosity
volScalarField muEff(mu(T));          // Temperature-dependent viscosity
volScalarField alpha(k/(rho*cp));     // Thermal diffusivity

// Buoyancy force with correct dimensions
volVectorField gBuoyancy(rhok * g * T); // [kg/(m²·s²)]
```

### Practical Impact on CFD Work

**Development Efficiency:**
| Benefit | Description | Impact |
|---------|-------------|--------|
| **Early Error Detection** | Problems caught during compilation | Reduces wasted computation time |
| **Precise Error Identification** | Exact location of dimensional inconsistency | Accelerates problem resolution |
| **Reduced Trial and Error** | Systematic checking instead of guessing unit conversions | Increases code reliability |

**Simulation Reliability:**
- **Physical Correctness**: Results guaranteed to be dimensionally consistent
- **Reproducibility**: Eliminates unit-related sources of variation between simulations
- **Verification Support**: Provides mathematical foundation for code verification procedures

---

## Exercises

### Part 1: Basic Dimensional Analysis

Write the 7-position exponent array (`M L T Theta N I J`) for the following quantities:

1. **Force**: $F = m \cdot a$
2. **Energy**: $E = F \cdot d$
3. **Kinematic Viscosity ($\nu$)**: Units are $m^2/s$
4. **Mass Flow Rate**: Units are $kg/s$

<details>
<summary>💡 Solution - Part 1</summary>

1. **Force**: `[1 1 -2 0 0 0 0]` (Newton: $kg \cdot m/s^2$)
2. **Energy**: `[1 2 -2 0 0 0 0]` (Joule: $kg \cdot m^2/s^2$)
3. **Kinematic Viscosity**: `[0 2 -1 0 0 0 0]` ($m^2/s$)
4. **Mass Flow Rate**: `[1 0 -1 0 0 0 0]` ($kg/s$)

</details>

---

### Part 2: Consistency Verification

A simplified momentum equation is:
$$\frac{\mathbf{U}}{\Delta t} + \mathbf{U} \cdot \nabla \mathbf{U} = -\frac{\nabla p}{\rho}$$

**Question**: Prove whether the units of the leftmost term ($\mathbf{U}/\Delta t$) and the rightmost term ($\nabla p / \rho$) are equal. (Show the exponents)

<details>
<summary>💡 Solution - Part 2</summary>

**Leftmost term analysis ($\mathbf{U}/\Delta t$):**
- $\mathbf{U}$: $[L \, T^{-1}]$ (velocity)
- $\Delta t$: $[T]$ (time)
- **Result**: $[L \, T^{-1}] / [T] = [L \, T^{-2}]$ (Acceleration)

**Rightmost term analysis ($\nabla p / \rho$):**
- $\nabla p$: $[M \, L^{-1} \, T^{-2}] / [L] = [M \, L^{-2} \, T^{-2}]$
- $\rho$: $[M \, L^{-3}]$
- **Result**: $[M \, L^{-2} \, T^{-2}] / [M \, L^{-3}] = [L \, T^{-2}]$ (Acceleration)

**Conclusion**: ✓ Both terms have identical dimensions $[L \, T^{-2}]$

</details>

---

### Part 3: Application Scenario

You are solving flow around a cylinder and find that results from coarse and fine grids give vastly different pressure values:

- If you switch to comparing in terms of the **pressure coefficient ($C_p$)**, which is dimensionless, what trend would you see?
- Write OpenFOAM code to calculate `Cp` from `p`, `p_inf`, `rho`, and `U_inf`

<details>
<summary>💡 Solution - Part 3</summary>

**Trend Observation:**
- You would see that $C_p$ **converges to the same value** even though raw pressures differ (grid independence study)
- Non-dimensional coefficients eliminate scaling differences and reveal the underlying physics

**OpenFOAM Code Implementation:**

```cpp
// Read reference quantities
dimensionedScalar p_inf("p_inf", dimPressure, readScalar(transportProperties.lookup("p_inf")));
dimensionedScalar rho("rho", dimDensity, readScalar(transportProperties.lookup("rho")));
dimensionedScalar U_inf("U_inf", dimVelocity, readScalar(transportProperties.lookup("U_inf")));

// Calculate pressure coefficient
volScalarField Cp
(
    IOobject("Cp", runTime.timeName(), mesh),
    (p - p_inf) / (0.5 * rho * sqr(U_inf))
);

Cp.write();
```

**Dimensional Verification:**
- Numerator: $(p - p_\infty)$ → $[M \, L^{-1} \, T^{-2}]$
- Denominator: $0.5 \cdot \rho \cdot U_\infty^2$ → $[M \, L^{-3}] \cdot [L^2 \, T^{-2}] = [M \, L^{-1} \, T^{-2}]$
- **Result**: $C_p$ is dimensionless as required

</details>

---

### Part 4: Advanced Multi-Physics Challenge

For a magnetohydrodynamics (MHD) simulation, you need to verify dimensional consistency for the Lorentz force term:

$$\mathbf{F}_L = \mathbf{J} \times \mathbf{B}$$

Where:
- $\mathbf{J}$ = current density ($A/m^2$)
- $\mathbf{B}$ = magnetic field (Tesla)

**Tasks:**
1. Determine the dimensions of the Lorentz force per unit volume
2. Write OpenFOAM code to declare these fields with proper dimensions
3. Show how the dimensional system prevents mixing electric and magnetic fields incorrectly

<details>
<summary>💡 Solution - Part 4</summary>

**1. Dimensional Analysis:**

| Quantity | Symbol | Dimensions | SI Unit |
|----------|--------|------------|---------|
| Current Density | $\mathbf{J}$ | $[I \, L^{-2}]$ | $A/m^2$ |
| Magnetic Field | $\mathbf{B}$ | $[M \, T^{-2} \, I^{-1}]$ | Tesla |
| Lorentz Force Density | $\mathbf{F}_L$ | $[M \, L^{-2} \, T^{-2}]$ | $N/m^3$ |

**Verification:**
$$[\mathbf{J} \times \mathbf{B}] = [I \, L^{-2}] \cdot [M \, T^{-2} \, I^{-1}] = [M \, L^{-2} \, T^{-2}]$$

**2. OpenFOAM Implementation:**

```cpp
// Custom electromagnetic dimensions
dimensionSet dimCurrentDensity(0, -2, 0, 0, 0, 1, 0);      // [A/m²]
dimensionSet dimMagneticField(1, 0, -2, 0, 0, -1, 0);      // [T]
dimensionSet dimForceDensity(1, -2, -2, 0, 0, 0, 0);       // [N/m³]

// Field declarations
volVectorField J
(
    IOobject("J", runTime.timeName(), mesh, IOobject::MUST_READ),
    mesh,
    dimCurrentDensity
);

volVectorField B
(
    IOobject("B", runTime.timeName(), mesh, IOobject::MUST_READ),
    mesh,
    dimMagneticField
);

// Lorentz force calculation with dimensional safety
volVectorField F_L("F_L", J ^ B);  // Cross product operator

// Verify dimensions match force density
if (!F_L.dimensions().matches(dimForceDensity))
{
    FatalErrorIn("calculateLorentzForce")
        << "Lorentz force has incorrect dimensions: " << F_L.dimensions()
        << "Expected: " << dimForceDensity
        << exit(FatalError);
}
```

**3. Error Prevention:**

The dimensional system prevents these common errors:

```cpp
// ❌ ERROR: Caught by compiler or runtime
// volScalarField invalid = J + B;  // Cannot add current density to magnetic field

// ❌ ERROR: Dimension mismatch detected
// volVectorField wrongForce = J * B;  // Wrong operator - should be cross product

// ✓ CORRECT: Proper cross product with automatic dimensional validation
volVectorField lorentzForce = J ^ B;  // Dimensions automatically verified
```

</details>

---

### Part 5: Non-Dimensional Solver Implementation

Create a non-dimensional form of the incompressible Navier-Stokes equations for flow around an obstacle.

**Reference quantities:**
- $L_{ref} = 1.0$ m (characteristic length)
- $U_{ref} = 10.0$ m/s (characteristic velocity)
- $\nu = 1.5 \times 10^{-5}$ m²/s (kinematic viscosity)

**Tasks:**
1. Calculate the Reynolds number
2. Write the non-dimensional momentum equation
3. Implement boundary conditions in non-dimensional form

<details>
<summary>💡 Solution - Part 5</summary>

**1. Reynolds Number Calculation:**

$$Re = \frac{U_{ref} \cdot L_{ref}}{\nu} = \frac{10.0 \times 1.0}{1.5 \times 10^{-5}} \approx 666,667$$

**2. Non-Dimensional Momentum Equation:**

$$\frac{\partial \mathbf{u}^*}{\partial t^*} + (\mathbf{u}^* \cdot \nabla^*) \mathbf{u}^* = -\nabla^* p^* + \frac{1}{Re} \nabla^{*2} \mathbf{u}^*$$

Where:
- $\mathbf{u}^* = \mathbf{u} / U_{ref}$ (dimensionless velocity)
- $p^* = p / (\rho U_{ref}^2)$ (dimensionless pressure)
- $t^* = t \cdot U_{ref} / L_{ref}$ (dimensionless time)
- $\nabla^* = L_{ref} \cdot \nabla$ (dimensionless gradient)

**3. OpenFOAM Implementation:**

```cpp
// createNonDimensionalFields.H
// Reference quantities
dimensionedScalar LRef("LRef", dimLength, 1.0);
dimensionedScalar URef("URef", dimVelocity, 10.0);
dimensionedScalar nuRef("nuRef", dimKinematicViscosity, 1.5e-5);

// Calculate Reynolds number (dimensionless)
dimensionedScalar Re("Re", dimless, URef * LRef / nuRef);

Info << "Reynolds number: " << Re.value() << endl;

// Non-dimensional velocity field
volVectorField Ustar
(
    IOobject("Ustar", runTime.timeName(), mesh),
    U / URef  // Automatically dimensionless
);

// Non-dimensional pressure field
volScalarField pstar
(
    IOobject("pstar", runTime.timeName(), mesh),
    p / (rho * sqr(URef))  // Automatically dimensionless
);
```

**Non-Dimensional Boundary Conditions (`0/Ustar`):**

```cpp
dimensions      [0 0 0 0 0 0 0];  // Dimensionless

internalField   uniform (1 0 0);  // U/U_ref = 1 at inlet

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform (1 0 0);  // Non-dimensional inlet velocity
    }
    outlet
    {
        type            zeroGradient;
    }
    walls
    {
        type            fixedValue;
        value           uniform (0 0 0);  // No-slip condition
    }
}
```

**Non-Dimensional Momentum Equation (`UEqn.H`):**

```cpp
// UEqn.H - Non-dimensional form
{
    // Non-dimensional momentum equation
    // ∂u*/∂t* + (u*·∇*)u* = -∇*p* + (1/Re)∇*²u*
    fvVectorMatrix UstarEqn
    (
        fvm::ddt(Ustar)                      // ∂u*/∂t*
      + fvm::div(phiStar, Ustar)             // u*·∇*u*
      - fvm::laplacian(dimensionedScalar("invRe", dimless, 1.0/Re), Ustar)  // (1/Re)∇*²u*
    );

    UstarEqn.relax();

    if (pimple.momentumPredictor())
    {
        solve(UstarEqn == -fvc::grad(pstar));  // -∇*p*
    }
}
```

**Advantages of Non-Dimensional Form:**
- Single parameter ($Re$) controls the physics
- Results scale to any geometrically similar problem
- Improved numerical conditioning
- Direct comparison with experimental data

</details>

---

## Key Takeaways

> [!TIP] Best Practices
> 1. **Always declare dimensions explicitly** when creating fields or constants
> 2. **Use `dimensionSet::matches()`** for runtime dimensional validation
> 3. **Document reference scales** when using non-dimensional formulations
> 4. **Let OpenFOAM handle unit conversions** automatically through the dimensional system
> 5. **Test with known units** to verify solver implementations

> [!WARNING] Common Pitfalls
> - Mixing dimensionless volume fractions ($\alpha$) with dimensional densities ($\rho$)
> - Forgetting that `sin()`, `exp()`, `log()` require dimensionless arguments
> - Losing dimensional information when implementing non-dimensional solvers
> - Incorrect boundary condition dimensions in case files

The dimensional analysis system in OpenFOAM provides a **mathematical foundation for reliable CFD simulations**, ensuring that both numerical accuracy and physical meaning are maintained throughout the computational process.
