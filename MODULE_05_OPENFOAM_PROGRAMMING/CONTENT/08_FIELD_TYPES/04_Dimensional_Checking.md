# Dimensional Checking in Fields

การตรวจสอบมิติใน Fields

---

## Learning Objectives

By the end of this section, you will be able to:
- **Understand** how OpenFOAM enforces dimensional consistency at compile-time and runtime
- **Specify** dimensions correctly using `dimensionSet` notation and predefined constants
- **Apply** dimensional checking to catch physics errors before simulation execution
- **Debug** dimensional inconsistencies systematically using error messages and field inspection
- **Validate** equation consistency by verifying all terms have matching dimensions

**Prerequisites:** Basic C++ knowledge, understanding of field types (from 02_Volume_Fields.md)

**Estimated Reading Time:** 15 minutes

**Difficulty Level:** Intermediate

---

## Key Takeaways

- ✓ **Automatic enforcement** - OpenFOAM checks dimensions at compile-time and runtime with zero overhead
- ✓ **Type-safe operations** - Only dimensionally-consistent operations compile successfully  
- ✓ **Early error detection** - Dimension mismatches caught before simulation produces invalid results
- ✓ **Physical consistency** - All terms in equations must have identical dimensions (homogeneous equations)
- ✓ **Systematic debugging** - Error messages explicitly show dimension mismatches for rapid troubleshooting

---

## 1. What is Dimensional Checking?

### Definition

**Dimensional checking** is OpenFOAM's type-safety feature that ensures mathematical operations respect physical units by automatically validating that field dimensions are compatible before operations execute.

### Why It Matters

> **Dimensional analysis is the first check of any physics calculation** — If the dimensions don't match, the physics is wrong

**Benefits:**
- **Prevents physics errors** - Catches unit conversion mistakes and algebraic errors
- **Ensures equation consistency** - Validates all terms in PDEs have matching dimensions
- **Improves code reliability** - Compiler catches what would otherwise be runtime bugs
- **Self-documenting code** - Dimensions explicitly encoded in field types

### How It Works

OpenFOAM uses **compile-time template metaprogramming** and **runtime validation** to check dimensions:

```
Field Creation → Dimension Specification → Operation Validation → Error or Execution
     ↓                    ↓                         ↓
dimensionSet         Template checks            Runtime checks
```

**See 05_Mathematical_Type_Theory.md** for implementation details

---

## 2. Specifying Dimensions in Fields

### Method 1: Predefined Dimension Constants

```cpp
volScalarField T
(
    IOobject("T", runTime.timeName(), mesh, IOobject::NO_READ),
    mesh,
    dimensionedScalar("T", dimTemperature, 300)
);
```

**Common predefined constants:**
- `dimPressure` - Pressure [M L^-1 T^-2]
- `dimVelocity` - Velocity [L T^-1]
- `dimDensity` - Density [M L^-3]
- `dimTemperature` - Temperature [Θ]
- `dimKinematicViscosity` - Kinematic viscosity [L^2 T^-1]

**For complete reference table, see Section 8: Dimension Reference**

### Method 2: Explicit dimensionSet Constructor

```cpp
dimensionSet(1, -1, -2, 0, 0, 0, 0)  // Pressure: [M L^-1 T^-2]
dimensionSet(0, 1, -1, 0, 0, 0, 0)   // Velocity: [L T^-1]
dimensionSet(0, 0, 0, 1, 0, 0, 0)    // Temperature: [Θ]
```

**dimensionSet parameters:** `(mass, length, time, temperature, moles, current, luminous_intensity)`

### Method 3: Reading from Dictionaries

```cpp
// In field file (e.g., 0/T)
dimensions      [0 0 0 1 0 0 0];  // Temperature

// Automatically read and validated
volScalarField T
(
    IOobject("T", runTime.timeName(), mesh, IOobject::MUST_READ),
    mesh
);
```

**Dictionary validation:** Dimensions checked when file is read; mismatch causes immediate error

---

## 3. Automatic Validation in Action

### Valid Operations ✓

```cpp
volScalarField p;   // Pressure: [M L^-1 T^-2]
volScalarField rho; // Density: [M L^-3]
volVectorField U;   // Velocity: [L T^-1]

// Dynamic pressure - dimensions combine correctly
volScalarField dynP = 0.5 * rho * magSqr(U);
// [M L^-3] × [L^2 T^-2] = [M L^-1 T^-2] ✓
```

**Dimension propagation:**
- Multiplication: Exponents add
- Division: Exponents subtract
- Powers: Exponents multiply

### Invalid Operations ✗

```cpp
// ERROR: Cannot add pressure + velocity
volScalarField bad = p + U;  
// [M L^-1 T^-2] + [L T^-1] = DIMENSION ERROR
```

**Compiler/Runtime output:**
```
--> FOAM FATAL ERROR:
Inconsistent dimensions for +
   Left operand: [1 -1 -2 0 0 0 0]
   Right operand: [0 1 -1 0 0 0 0]

    From function operator+(const dimensioned&, const dimensioned&)
    in file dimensionedType.C at line 123
```

**Key diagnostic information:**
- Operation that failed (+, -, *, /)
- Left and right operand dimensions
- File and line number for debugging

---

## 4. Equation Consistency Requirements

### The Homogeneity Principle

> **All terms in a valid physical equation must have identical dimensions**

### Matrix Equation Example

```cpp
solve
(
    fvm::ddt(T)           // [Θ T^-1] - Rate of change
  + fvm::div(phi, T)      // [Θ T^-1] - Convection
  ==
    fvm::laplacian(DT, T) // [Θ T^-1] - Diffusion
);
```

**Term-by-term dimension analysis:**

| Operator | Dimension | Physical Meaning |
|----------|-----------|------------------|
| `fvm::ddt(T)` | [Θ T^-1] | ∂T/∂t - Temperature rate of change |
| `fvm::div(phi, T)` | [Θ T^-1] | ∇·(φT) - Convective transport |
| `fvm::laplacian(DT, T)` | [Θ T^-1] | ∇·(DT∇T) - Diffusive transport |

**Why this matters:** If any term has different dimensions, OpenFOAM rejects the entire equation before solving

### Checking Equation Dimensions

```cpp
// Debug: Print dimensions of each term
Info << "ddt(T): " << fvm::ddt(T).dimensions() << endl;
Info << "div(phi,T): " << fvm::div(phi, T).dimensions() << endl;
Info << "laplacian(DT,T): " << fvm::laplacian(DT, T).dimensions() << endl;
```

---

## 5. Inspecting and Manipulating Dimensions

### Reading Field Dimensions

```cpp
const dimensionSet& dims = T.dimensions();

Info << "Temperature dimensions: " << dims << endl;
// Output: [0 0 0 1 0 0 0]

// Check individual exponents
Info << "Mass exponent: " << dims[0] << endl;     // 0
Info << "Length exponent: " << dims[1] << endl;   // 0
Info << "Time exponent: " << dims[2] << endl;     // 0
Info << "Temperature exponent: " << dims[3] << endl; // 1
```

### Checking Dimensionless Fields

```cpp
if (dims.dimensionless())
{
    Info << "Field has no dimensions (dimensionless)" << endl;
}
else
{
    Info << "Field has physical dimensions" << endl;
}
```

### Comparing Field Dimensions

```cpp
volScalarField field1, field2;

if (field1.dimensions() == field2.dimensions())
{
    // Safe to perform operations
    volScalarField result = field1 + field2;
}
else
{
    FatalError << "Dimension mismatch: " 
               << field1.dimensions() << " vs " 
               << field2.dimensions() << abort(FatalError);
}
```

### Setting Dimensions Programmatically

```cpp
// Create dimensionless field
volScalarField alpha
(
    IOobject("alpha", runTime.timeName(), mesh, IOobject::NO_READ),
    mesh,
    dimensionedScalar("alpha", dimensionSet(0,0,0,0,0,0,0), 0.0)
);

// Or use predefined
dimensionSet dimless;  // Default: all zeros
```

---

## 6. Debugging Dimensional Errors

### Systematic Debugging Workflow

```
1. READ ERROR → Identify operation and operands
2. VERIFY PHYSICS → Manually calculate expected dimensions
3. PRINT DIMENSIONS → Output field dimensions to console
4. CHECK OPERATORS → Verify fvm:: vs fvc:: usage
5. REVIEW BOUNDARY CONDITIONS → BC dimensions must match field dimensions
6. FIX AND VALIDATE → Ensure fix maintains dimensional consistency
```

### Real-World Error Messages from Solver Logs

> [!NOTE] **📂 OpenFOAM Context**
> **ตำแหน่งไฟล์ที่พบ error:**
> - **Solver logs**: `log.simpleFoam`, `log.interFoam`, `log.customSolver`
> - **Error traces**: ระบุ file และ line number ใน OpenFOAM source
> - **Runtime errors**: เกิดเมื่อ solver ประมวลผลสมการ
>
> **Keywords ที่ค้นหาใน log:**
> - "Inconsistent dimensions"
> - "LHS and RHS"
> - "dimension mismatch"
> - "Dimensions of"
>
> **การ decode error:**
> - ตัวเลขในวงเล็บ `[...]` คือ exponent ของ [M L T Θ I N J]
> - อ่านจากซ้ายไปขวา: Mass, Length, Time, Temperature, Moles, Current, Luminous

#### Error Type 1: Addition/Subtraction Mismatch

**Scenario**: Adding pressure and velocity (common physics error)

```
--> FOAM FATAL ERROR:
LHS and RHS of + have different dimensions
    LHS: [0 2 -2 0 0 0 0]
    RHS: [1 -1 -2 0 0 0 0]

    From function operator+(const dimensionedField<Type>&, const dimensionedField<Type>&)
    in file fields/DimensionedField/DimensionedField.C at line 845

FOAM aborting
```

**Diagnosis**:
- **LHS** (Left Hand Side): `[0 2 -2]` = Kinetic energy (m²/s²)
- **RHS** (Right Hand Side): `[1 -1 -2]` = Pressure (Pa = kg/(m·s²))
- **Root cause**: Attempting `TKE + p` which is physically invalid

**Fix**:
```cpp
// WRONG: Direct addition
volScalarField bad = TKE + p;

// CORRECT: Convert units first
volScalarField dynamicPressure = rho * TKE;  // [kg/m³] × [m²/s²] = [Pa]
volScalarField totalPressure = p + dynamicPressure;  // Now both have [M L^-1 T^-2]
```

#### Error Type 2: Flux Dimension Mismatch

**Scenario**: Wrong flux type (mass flux vs volume flux)

```
--> FOAM FATAL ERROR:
Dimensions of operands for div are not consistent
    dimensions: [0 3 -1 0 0 0 0]
    required: [1 0 -1 0 0 0 0]

    From function fvm::div(...)
    in file finiteVolume/ddtSchemes/divScheme.C at line 124

FOAM aborting
```

**Diagnosis**:
- **Actual phi**: `[0 3 -1]` = Volume flux (m³/s)
- **Required**: `[1 0 -1]` = Mass flux (kg/s)
- **Root cause**: Solver expects mass flux but received volume flux (common in compressible solvers)

**Fix**:
```cpp
// WRONG: Using volume flux in compressible solver
surfaceScalarField phi = fvc::flux(U);  // Volume flux [L^3/T]

// CORRECT: Include density
surfaceScalarField phi = fvc::flux(rho * U);  // Mass flux [M/T]
```

#### Error Type 3: Laplacian Diffusivity Error

**Scenario**: Using wrong viscosity type (kinematic vs dynamic)

```
--> FOAM FATAL ERROR:
Dimensions of operands for laplacian are not consistent
    field: [0 1 -1 0 0 0 0]
    diffusivity: [1 -1 -1 0 0 0 0]
    result: [1 0 -2 0 0 0 0]
    expected: [0 1 -2 0 0 0 0]

    From function fvm::laplacian(...)
    in file finiteVolume/lnSchemes/laplacianScheme.C at line 201

FOAM aborting
```

**Diagnosis**:
- **Field (U)**: `[0 1 -1]` = Velocity (m/s)
- **Diffusivity (mu)**: `[1 -1 -1]` = Dynamic viscosity (Pa·s)
- **Result**: `[1 0 -2]` = Wrong dimension for momentum equation
- **Expected**: `[0 1 -2]` = Acceleration (m/s²)

**Fix**:
```cpp
// WRONG: Using dynamic viscosity in incompressible solver
fvm::laplacian(mu, U)  // mu = dynamic viscosity [M/(L·T)]

// CORRECT: Use kinematic viscosity
fvm::laplacian(nu, U)  // nu = kinematic viscosity [L^2/T]
```

#### Error Type 4: Time Derivative Dimension Error

**Scenario**: Field without time dimension in time derivative

```
--> FOAM FATAL ERROR:
Dimensions of ddt term are not consistent
    field: [0 0 0 1 0 0 0]
    derivative: [0 0 -1 0 0 0 0]
    result: [0 0 -1 1 0 0 0]
    required: [0 0 -1 0 0 0 0]

    From function fvm::ddt(...)
    in file finiteVolume/ddtSchemes/ddtScheme.C at line 89

FOAM aborting
```

**Diagnosis**:
- **Field (T)**: `[0 0 0 1]` = Temperature (K)
- **Derivative**: `[0 0 -1]` = 1/time (s⁻¹)
- **Result**: `[0 0 -1 1]` = Temperature rate (K/s)
- **Required**: `[0 0 -1]` = This solver expects dimensionless rate

**Fix**:
```cpp
// Check if equation expects dimensionless form
// For energy equation, use:
fvm::ddt(T) + fvm::div(phi, T) == fvm::laplacian(alpha, T)

// Where alpha has correct dimensions [L^2/T]
```

#### Error Type 5: Source Term Dimension Mismatch

**Scenario**: Source term with wrong units in transport equation

```
--> FOAM FATAL ERROR:
Dimensions of terms in == are not consistent
    LHS dimensions: [0 2 -2 0 0 0 0]
    RHS dimensions: [0 0 -1 0 0 0 0]

    From function fvMatrix::operator==(...)
    in file finiteVolume/fvMatrices/fvMatrix.C at line 456

FOAM aborting

    In equation:
    fvm::ddt(TKE) + fvm::div(phi, TKE) == production - dissipation
```

**Diagnosis**:
- **LHS** (Transient + Convection): `[0 2 -2]` = TKE rate (m²/s³)
- **RHS** (Source terms): `[0 0 -1]` = 1/time (s⁻¹) - **WRONG**
- **Root cause**: Source term `production - dissipation` missing density factor

**Fix**:
```cpp
// WRONG: Source term has wrong dimensions
volScalarField production = ...;  // [1/T]
volScalarField dissipation = ...; // [1/T]

// CORRECT: Multiply by rho*dimension
volScalarField production = rho * P;  // [M/L³] × [L²/T³] = [M/(L·T³)]
volScalarField dissipation = rho * epsilon;
// Now both sides: [M/(L·T³)] / [M/L³] = [L²/T³] ✓
```

### Step 1: Analyze the Error Message

```
--> FOAM FATAL ERROR:
Inconsistent dimensions for +
   Left operand: [1 -1 -2 0 0 0 0]
   Right operand: [0 1 -1 0 0 0 0]
```

**Questions to answer:**
- What operation failed? (+, -, *, /)
- What are the dimensions of each operand?
- What should the dimensions be according to physics?

### Step 2: Verify Equation Physics

```cpp
// Write out expected dimensions manually
// Bernoulli equation: p + 0.5*rho*U^2 = constant
// p: [M L^-1 T^-2]
// rho: [M L^-3], U: [L T^-1]
// rho*U^2: [M L^-3] × [L^2 T^-2] = [M L^-1 T^-2] ✓

// If dimensions don't match, physics is wrong!
```

### Step 3: Print Field Dimensions

```cpp
Info << "=== Dimension Debug ===" << endl;
Info << "p: " << p.dimensions() << endl;
Info << "rho: " << rho.dimensions() << endl;
Info << "U: " << U.dimensions() << endl;
Info << "phi: " << phi.dimensions() << endl;
Info << "=====================" << endl;
```

### Step 4: Check Operator Types

**Implicit operators (fvm::):**
- `fvm::ddt(T)` - Creates matrix term for time derivative
- `fvm::div(phi, T)` - Creates matrix term for divergence
- `fvm::laplacian(DT, T)` - Creates matrix term for diffusion

**Explicit operators (fvc::):**
- `fvc::ddt(T)` - Calculates time derivative value
- `fvc::div(phi, T)` - Calculates divergence value
- `fvc::laplacian(DT, T)` - Calculates Laplacian value

**Common pitfall:** Mixing fvm:: and fvc:: incorrectly in equations

### Step 5: Verify Boundary Conditions

```cpp
// Check boundary condition dimensions
forAll(T.boundaryField(), patchI)
{
    Info << "Patch " << patchI
         << " dimensions: " << T.boundaryField()[patchI].dimensions() << endl;
}
```

### Common Error Patterns and Solutions

| Error Pattern | Symptom | Root Cause | Solution |
|---------------|---------|------------|----------|
| Adding pressure + velocity | `Inconsistent dimensions for +` | Different base dimensions | Check physics equation - should these be added? |
| Flux dimension mismatch | `Inconsistent dimensions for div` | Wrong phi dimension | Verify phi calculation: `rho*U` (mass flux) vs `U` (volume flux) |
| Time derivative error | `Inconsistent dimensions for ddt` | Wrong time dimension | Ensure field has correct dimensions for time derivative |
| Laplacian coefficient | `Inconsistent dimensions for laplacian` | Diffusivity units wrong | Check diffusivity: kinematic [L^2/T] vs dynamic [M/(L·T)] |
| Source term mismatch | `Inconsistent dimensions for ==` | Source term dimensions don't match PDE | Scale source term to match equation dimensions |

**For more pitfalls and solutions, see 07_Common_Pitfalls.md**

---

## 7. Dimension Reference

### SI Base Dimensions

| Position | dimensionSet Parameter | Symbol | Unit |
|----------|------------------------|--------|------|
| 0 | mass | M | kilogram (kg) |
| 1 | length | L | meter (m) |
| 2 | time | T | second (s) |
| 3 | temperature | Θ | Kelvin (K) |
| 4 | moles | N | mole (mol) |
| 5 | current | I | ampere (A) |
| 6 | luminous intensity | J | candela (cd) |

### Common Physical Quantities

| Physical Quantity | dimensionSet | OpenFOAM Constant |
|-------------------|--------------|-------------------|
| **Pressure** | `[1 -1 -2 0 0 0 0]` | `dimPressure` |
| **Density** | `[1 -3 0 0 0 0 0]` | `dimDensity` |
| **Velocity** | `[0 1 -1 0 0 0 0]` | `dimVelocity` |
| **Temperature** | `[0 0 0 1 0 0 0]` | `dimTemperature` |
| **Mass Flux** | `[1 0 -1 0 0 0 0]` | `dimMassFlux` |
| **Volume Flux** | `[0 3 -1 0 0 0 0]` | - |
| **Kinematic Viscosity** | `[0 2 -1 0 0 0 0]` | `dimKinematicViscosity` |
| **Dynamic Viscosity** | `[1 -1 -1 0 0 0 0]` | `dimDynamicViscosity` |
| **Energy** | `[1 2 -2 0 0 0 0]` | `dimEnergy` |
| **Power** | `[1 2 -3 0 0 0 0]` | `dimPower` |
| **Force** | `[1 1 -2 0 0 0 0]` | `dimForce` |
| **Acceleration** | `[0 1 -2 0 0 0 0]` | `dimAcceleration` |
| **Dimensionless** | `[0 0 0 0 0 0 0]` | `dimless` |

### Derived Field Dimensions

| Field Type | Typical Dimensions | Example |
|------------|-------------------|---------|
| `volScalarField` | Varies by quantity | Pressure: [M L^-1 T^-2] |
| `volVectorField` | [L T^-1] + scalar dims | Velocity: [L T^-1] |
| `volTensorField` | [L T^-1] + scalar dims | Velocity gradient: [T^-1] |
| `surfaceScalarField` | Flux-related | Phi (mass flux): [M T^-1] |
| `pointScalarField` | Same as volScalarField | Point temperature: [Θ] |

**For comprehensive dimension reference, see 06_Dimensioned_Fields.md**

---

## 8. Best Practices

### DO ✓

**Always specify dimensions explicitly**
```cpp
// GOOD: Explicit dimension specification
dimensionedScalar("T", dimTemperature, 300)
```

**Use predefined constants when available**
```cpp
// GOOD: Uses predefined constant
dimensionedScalar("p", dimPressure, 101325)
```

**Add dimension checks in debug mode**
```cpp
// GOOD: Validate dimensions during development
#ifdef DEBUG
    Info << "Field dimensions: " << field.dimensions() << endl;
#endif
```

**Document custom dimensions**
```cpp
// GOOD: Clear comments explain physical meaning
// Reaction rate: [T^-1] - First-order Arrhenius reaction
dimensionSet(0, 0, -1, 0, 0, 0, 0)
```

**Validate equation consistency**
```cpp
// GOOD: Check all terms have matching dimensions
assert(fvm::ddt(T).dimensions() == fvm::div(phi, T).dimensions());
```

### DON'T ✗

**Don't rely on default dimensions**
```cpp
// BAD: Unspecified dimension behavior
volScalarField T(mesh, dimensionedScalar("T", 300));  // What dimension?
```

**Don't disable dimension checking**
```cpp
// BAD: Disables safety feature
// Unless absolutely necessary for dimensionless formulations
```

**Don't ignore dimension warnings**
```cpp
// BAD: Compiler warnings indicate physics errors
Warning: Inconsistent dimensions for +
```

**Don't assume fields are dimensionless**
```cpp
// BAD: Explicitly specify if dimensionless
dimensionSet()  // Clear intent: dimensionless
```

**Don't mix fvm:: and fvc:: without checking**
```cpp
// BAD: Can cause dimension mismatches
fvm::ddt(T) + fvc::div(phi, T)  // Verify dimensions first!
```

---

## 🧠 Concept Check

<details>
<summary><b>1. ทำไม dimension checking สำคัญ?<br>Why is dimensional checking important?</b></summary>

**ป้องกัน physics errors** — Dimensional checking **prevents physics errors** by catching unit conversion mistakes and algebraic errors during compilation/runtime before they produce invalid simulation results.

**Key benefits:**
- ✅ Catches unit conversion errors automatically (e.g., mixing Pa and psi)
- ✅ Ensures equation consistency before solving  
- ✅ Prevents impossible physical operations (e.g., adding pressure + velocity)
- ✅ Provides clear error messages showing exact dimension mismatch
- ✅ Zero runtime overhead - validation happens at compile time

**Real-world example:** A missing density factor (`rho`) in a momentum equation would be caught immediately instead of producing subtly wrong results.
</details>

<details>
<summary><b>2. Equation terms ทุกตัวต้องมี dimension เดียวกันหรือไม่?<br>Must all terms in an equation have the same dimensions?</b></summary>

**ใช่** — **Yes**, every term in a valid physical equation must have **identical dimensions**. This is called **dimensional homogeneity**.

**Example from heat equation:**
```cpp
fvm::ddt(T)              // [Θ T^-1] - Temperature rate of change
+ fvm::div(phi, T)       // [Θ T^-1] - Convection
== fvm::laplacian(DT, T) // [Θ T^-1] - Diffusion
```

All three terms have dimensions of **temperature per unit time** [Θ T^-1].

**Why this matters:**
- Physical law: You can only add quantities that represent the same physical concept
- Mathematical consistency: ∂T/∂t + ∇·(φT) = ∇·(DT∇T) must balance dimensionally
- OpenFOAM enforcement: If dimensions don't match, equation is rejected before solving

**Counter-example - INVALID:**
```cpp
fvm::ddt(T) + fvm::div(phi, U)  // Temperature rate + Velocity flux? 
// [Θ T^-1] + [L T^-1 × L T^-1] = [Θ T^-1] + [L^2 T^-2] ✗ ERROR
```
</details>

<details>
<summary><b>3. flux (phi) มี dimension อะไร?<br>What are the dimensions of flux (phi)?</b></summary>

**Two common forms - MUST verify which your solver uses:**

**Mass flux** (compressible solvers):
- Dimension: `[M T^-1]` or `[1 0 -1 0 0 0 0]`
- Calculation: `phi = rho * U * mesh.Sf()`
- Used in: `fvm::div(phi, T)` where phi contains density
- Physical meaning: Mass flow rate through each face

**Volume flux** (incompressible solvers):
- Dimension: `[L^3 T^-1]` or `[0 3 -1 0 0 0 0]`
- Calculation: `phi = U * mesh.Sf()`
- Used in: Incompressible flow solvers (e.g., simpleFoam, pimpleFoam)
- Physical meaning: Volume flow rate through each face

**How to check:**
```cpp
Info << "phi dimensions: " << phi.dimensions() << endl;
// Output shows which form you have
```

**Critical:** Using the wrong assumption leads to dimension errors!
</details>

<details>
<summary><b>4. จะ debug dimension errors ได้อย่างไร?<br>How do you debug dimension errors?</b></summary>

**Systematic 6-step debugging workflow:**

**1. Read the error message carefully**
```
Inconsistent dimensions for +
   Left: [1 -1 -2 0 0 0 0]  (Pressure)
   Right: [0 1 -1 0 0 0 0]  (Velocity)
```

**2. Identify the operation and location**
- Which operator? (+, -, *, /)
- Which file and line number?
- What equation is being assembled?

**3. Print field dimensions**
```cpp
Info << "=== Dimension Debug ===" << endl;
Info << "p: " << p.dimensions() << endl;
Info << "U: " << U.dimensions() << endl;
Info << "phi: " << phi.dimensions() << endl;
```

**4. Verify equation physics manually**
```cpp
// Bernoulli: p + 0.5*rho*U^2
// p: [M L^-1 T^-2]
// rho*U^2: [M L^-3] × [L^2 T^-2] = [M L^-1 T^-2] ✓
```

**5. Check operator usage (fvm:: vs fvc::)**
- `fvm::` - Implicit operators (create matrix terms)
- `fvc::` - Explicit operators (calculate values)
- Mixing incorrectly can cause dimension issues

**6. Review boundary conditions**
```cpp
forAll(T.boundaryField(), patchI)
{
    Info << "Patch " << patchI 
         << " dims: " << T.boundaryField()[patchI].dimensions() << endl;
}
```

**Common fixes:**
- Missing density factor in flux calculation
- Using wrong flux type (mass vs volume)
- Incorrect diffusivity dimensions
- Source term needs scaling

**For more debugging techniques, see 07_Common_Pitfalls.md**
</details>

<details>
<summary><b>5. kinematic viscosity และ dynamic viscosity ต่างกันอย่างไร?<br>What's the difference between kinematic and dynamic viscosity?</b></summary>

**Critical distinction - dimensions differ by density:**

**Dynamic viscosity (μ):**
- Dimension: `[M L^-1 T^-1]` or `[1 -1 -1 0 0 0 0]`
- OpenFOAM constant: `dimDynamicViscosity`
- Units: Pa·s or kg/(m·s)
- Used in: **Compressible** solvers with density variations
- Laplacian term: `fvm::laplacian(mu, U)`

**Kinematic viscosity (ν):**
- Dimension: `[L^2 T^-1]` or `[0 2 -1 0 0 0 0]`
- OpenFOAM constant: `dimKinematicViscosity`
- Units: m²/s
- Relationship: ν = μ/ρ (dynamic viscosity ÷ density)
- Used in: **Incompressible** solvers (constant density)
- Laplacian term: `fvm::laplacian(nu, U)`

**Common mistake:** Using wrong viscosity type causes dimension errors!
```cpp
// WRONG in incompressible solver:
fvm::laplacian(mu, U)  // [M L^-1 T^-1] × [L T^-1] = [M T^-2] ✗

// CORRECT in incompressible solver:
fvm::laplacian(nu, U)  // [L^2 T^-1] × [L T^-1] = [L^2 T^-2] → /L = [L T^-2] ✓
```

**Check your solver's documentation!**
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง | Related Documentation

### Essential Reading
- **ภาพรวม:** [00_Overview.md](00_Overview.md) - Field type system overview
- **Dimensioned Fields:** [06_Dimensioned_Fields.md](06_Dimensioned_Fields.md) - Complete dimension sets reference with examples
- **Geometric Fields:** [02_Volume_Fields.md](02_Volume_Fields.md) - Field types and their typical dimensions

### Advanced Topics
- **Mathematical Formulations:** [05_Mathematical_Type_Theory.md](05_Mathematical_Type_Theory.md) - Dimension theory implementation using template metaprogramming
- **Common Pitfalls:** [07_Common_Pitfalls.md](07_Common_Pitfalls.md) - Dimension-related errors and debugging techniques

### Cross-Module References
- **Unit Systems:** MODULE_01/03_BOUNDARY_CONDITIONS - Dimensional consistency in BC specifications
- **Equation Verification:** MODULE_03/02_PRESSURE_VELOCITY_COUPLING - Dimension checking in PDE assembly

### Quick Reference
- **Dimension sets table:** See Section 8 in this document
- **Field creation patterns:** See 02_Volume_Fields.md:3.2
- **Error debugging:** See Section 6 in this document