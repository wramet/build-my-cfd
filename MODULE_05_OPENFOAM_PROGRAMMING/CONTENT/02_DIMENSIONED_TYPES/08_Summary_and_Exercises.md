# Summary and Exercises

สรุปและแบบฝึกหัด — ฝึกทำเพื่อเข้าใจจริง

> **ทำไมต้องทำ Exercises?**
> - อ่านอย่างเดียวไม่พอ — **ต้องเขียน code เอง**
> - ฝึก dimension calculations จนคล่อง
> - เตรียมพร้อมสำหรับ real-world usage

---

## Learning Objectives

หลังจากผ่านบทนี้ คุณควรจะสามารถ:
- สร้างและใช้งาน `dimensionedScalar` และ `dimensionedVector` ได้อย่างถูกต้อง
- ตรวจสอบและคำนวณ dimensions สำหรับสมการทางฟิสิกส์
- อ่านและเขียน dimensioned values จาก dictionary files
- สร้าง fields พร้อม dimensions สำหรับ OpenFOAM solvers
- คำนวณ dimensionless numbers และ verify ความถูกต้อง
- Debug dimension mismatches อย่างเป็นระบบ

---

## Summary

### Core Concepts Review

| Concept | Description |
|---------|-------------|
| `dimensionSet` | 7 SI exponents: [M L T Θ I N J] |
| `dimensionedScalar` | Scalar value + dimensions + name |
| `dimensionedVector` | Vector value + dimensions + name |
| `dimless` | Special dimension set for dimensionless quantities |
| Checking | Compile-time (templates) + runtime (dimensionSet) |

### Key Dimension Operations

| Operation | Dimension Math |
|-----------|----------------|
| Addition/Subtraction | Requires identical dimensions |
| Multiplication | Add exponents element-wise |
| Division | Subtract exponents element-wise |
| Powers | Multiply exponents by scalar |

### Common Dimension Aliases

> **📋 Full SI dimensions reference:** Available in [00_Overview.md](00_Overview.md)

| Alias | Physical Quantity | Dimension Set |
|-------|-------------------|---------------|
| `dimless` | Dimensionless | `[0 0 0 0 0 0 0]` |
| `dimLength` | Length | `[0 1 0 0 0 0 0]` |
| `dimTime` | Time | `[0 0 1 0 0 0 0]` |
| `dimMass` | Mass | `[1 0 0 0 0 0 0]` |
| `dimVelocity` | Velocity | `[0 1 -1 0 0 0 0]` |
| `dimAcceleration` | Acceleration | `[0 1 -2 0 0 0 0]` |
| `dimPressure` | Pressure | `[1 -1 -2 0 0 0 0]` |
| `dimDensity` | Density | `[1 -3 0 0 0 0 0]` |
| `dimDynamicViscosity` | Dynamic Viscosity | `[1 -1 -1 0 0 0 0]` |
| `dimKinematicViscosity` | Kinematic Viscosity | `[0 2 -1 0 0 0 0]` |
| `dimTemperature` | Temperature | `[0 0 0 1 0 0 0]` |
| `dimSurfaceTension` | Surface Tension | `[1 0 -2 0 0 0 0]` |

---

## Exercises

### Exercise 1: Create Dimensioned Values [Beginner]

**Task:** Create the following physical quantities with correct dimensions.

```cpp
// TODO: Create these dimensioned scalars
// 1. Water density: 1000 kg/m³
// 2. Kinematic viscosity of water: 1e-6 m²/s
// 3. Dynamic viscosity of water: 1e-3 Pa·s
// 4. Gravity acceleration: 9.81 m/s² in z-direction

// Your code here:


```

<details>
<summary><b>💡 Hint 1</b></summary>

Use `dimDensity`, `dimKinematicViscosity`, `dimDynamicViscosity`, `dimAcceleration`
</details>

<details>
<summary><b>💡 Hint 2</b></summary>

For vectors, use `vector(x, y, z)` constructor
</details>

<details>
<summary><b>🔍 Inline Hint: Constructor Pattern</b></summary>

```cpp
// Pattern: dimensionedScalar("name", dimensions, value)
dimensionedScalar example("example", dimLength, 1.0);
```
</details>

<details>
<summary><b>✓ Solution</b></summary>

```cpp
dimensionedScalar rho("rho", dimDensity, 1000);
dimensionedScalar nu("nu", dimKinematicViscosity, 1e-6);
dimensionedScalar mu("mu", dimDynamicViscosity, 1e-3);
dimensionedVector g("g", dimAcceleration, vector(0, 0, -9.81));
```
</details>

---

### Exercise 2: Dimension Checking [Beginner]

**Task:** Determine which operations are valid and calculate resulting dimensions.

```cpp
dimensionedScalar a("a", dimPressure, 100);        // [M L^-1 T^-2]
dimensionedScalar b("b", dimDensity, 1000);         // [M L^-3]
dimensionedScalar c("c", dimVelocity, 10);          // [L T^-1]

// TODO: Determine validity and resulting dimensions
dimensionedScalar d = a / b;   // What dimension?
dimensionedScalar e = a * b;   // What dimension?
// dimensionedScalar f = a + c;  // Valid or error?
```

<details>
<summary><b>💡 Hint</b></summary>

Division: subtract exponents | Multiplication: add exponents | Addition: must be identical
</details>

<details>
<summary><b>🔍 Inline Hint: Dimension Arithmetic</b></summary>

```cpp
// Division: [M L^-1 T^-2] / [M L^-3] = [M^(1-1) L^(-1+3) T^-2] = [L^2 T^-2]
// This equals velocity squared!
```
</details>

<details>
<summary><b>✓ Solution</b></summary>

- `a / b`: `[1 -1 -2] - [1 -3 0] = [0 2 -2]` → `[L² T⁻²]` (velocity squared) ✓
- `a * b`: `[1 -1 -2] + [1 -3 0] = [2 -4 -2]` → `[M² L⁻⁴ T⁻²]` ✓
- `a + c`: **Error** — pressure dimensions ≠ velocity dimensions
</details>

---

### Exercise 3: Reynolds Number Calculation [Intermediate]

**Task:** Calculate Reynolds number and verify it's dimensionless.

```cpp
// Flow properties
dimensionedScalar rho("rho", dimDensity, 1000);           // kg/m³
dimensionedScalar U("U", dimVelocity, 1.0);                // m/s
dimensionedScalar L("L", dimLength, 0.1);                  // m
dimensionedScalar mu("mu", dimDynamicViscosity, 1e-3);     // Pa·s

// TODO: Calculate Reynolds number: Re = (rho * U * L) / mu
// Verify the result is dimensionless


```

<details>
<summary><b>💡 Hint</b></summary>

Use `.dimensions().dimensionless()` to check if result is dimensionless
</details>

<details>
<summary><b>🔍 Inline Hint: Dimension Verification Strategy</b></summary>

```cpp
// Always verify dimensionless numbers:
// 1. Calculate the number
// 2. Check dimensions are [0 0 0 0 0 0 0]
// 3. Print result with .dimensionless() check
```
</details>

<details>
<summary><b>✓ Solution</b></summary>

```cpp
dimensionedScalar Re = rho * U * L / mu;

Info << "Re = " << Re << endl;
Info << "Dimensions: " << Re.dimensions() << endl;
Info << "Dimensionless? " << Re.dimensions().dimensionless() << endl;
```

**Dimension verification:**
```
Re = [M L⁻³][L T⁻¹][L][M⁻¹ L⁻¹ T] = [1] = dimless ✓
```
</details>

---

### Exercise 4: Create Fields with Dimensions [Intermediate]

**Task:** Create OpenFOAM fields with proper initial values and dimensions.

```cpp
// TODO: Create temperature field (initial: 300 K)
volScalarField T
(
    IOobject("T", runTime.timeName(), mesh, IOobject::NO_READ),
    mesh,
    // Your code here for dimensionedScalar initial value
);

// TODO: Create pressure field (initial: 0 Pa, reference pressure)
volScalarField p
(
    IOobject("p", runTime.timeName(), mesh, IOobject::NO_READ),
    mesh,
    // Your code here for dimensionedScalar initial value
);
```

<details>
<summary><b>💡 Hint</b></summary>

Use `dimensionedScalar("name", dimensions, value)` as the third argument
</details>

<details>
<summary><b>🔍 Inline Hint: Field Constructor Pattern</b></summary>

```cpp
// volScalarField pattern:
// volScalarField fieldName(
//     IOobject(...),
//     mesh,
//     dimensionedScalar("name", dimensions, initialValue)
// );
```
</details>

<details>
<summary><b>✓ Solution</b></summary>

```cpp
volScalarField T
(
    IOobject("T", runTime.timeName(), mesh, IOobject::NO_READ),
    mesh,
    dimensionedScalar("T", dimTemperature, 300)
);

volScalarField p
(
    IOobject("p", runTime.timeName(), mesh, IOobject::NO_READ),
    mesh,
    dimensionedScalar("p", dimPressure, 0)
);
```
</details>

---

### Exercise 5: Read from Dictionary [Intermediate]

**Task:** Read dimensioned values from a dictionary file.

**Dictionary file (`transportProperties`):**
```cpp
nu              nu [0 2 -1 0 0 0 0] 1e-6;
rho             rho [1 -3 0 0 0 0 0] 1000;
mu              mu [1 -1 -1 0 0 0 0] 0.001;
```

```cpp
// TODO: Read and use these values
IOdictionary transportProperties
(
    IOobject
    (
        "transportProperties",
        runTime.constant(),
        mesh,
        IOobject::MUST_READ,
        IOobject::NO_WRITE
    )
);

// Your code to read nu, rho, mu


// TODO: Print values with dimensions
```

<details>
<summary><b>💡 Hint</b></summary>

Use `dimensionedScalar(name, dict.lookup("key"))`
</details>

<details>
<summary><b>🔍 Inline Hint: Dictionary Reading Pattern</b></summary>

```cpp
// Two-step pattern:
// 1. Create IOdictionary object
// 2. Use dimensionedScalar constructor with dict.lookup()
// Dimensions are automatically read from the dictionary entry
```
</details>

<details>
<summary><b>✓ Solution</b></summary>

```cpp
dimensionedScalar nu("nu", transportProperties.lookup("nu"));
dimensionedScalar rho("rho", transportProperties.lookup("rho"));
dimensionedScalar mu("mu", transportProperties.lookup("mu"));

Info << "nu = " << nu << " (dimensions: " << nu.dimensions() << ")" << endl;
Info << "rho = " << rho << " (dimensions: " << rho.dimensions() << ")" << endl;
Info << "mu = " << mu << " (dimensions: " << mu.dimensions() << ")" << endl;
```
</details>

---

### Exercise 6: Dimensionless Numbers [Advanced]

**Task:** Calculate common dimensionless numbers and verify they're truly dimensionless.

```cpp
// Given properties
dimensionedScalar rho("rho", dimDensity, 1000);
dimensionedScalar U("U", dimVelocity, 2.0);
dimensionedScalar L("L", dimLength, 0.5);
dimensionedScalar mu("mu", dimDynamicViscosity, 1e-3);
dimensionedScalar sigma("sigma", dimSurfaceTension, 0.072);  // N/m
dimensionedScalar g("g", dimAcceleration, 9.81);

// TODO: Calculate and verify:
// 1. Reynolds number: Re = rho * U * L / mu
// 2. Froude number: Fr = U / sqrt(g * L)
// 3. Weber number: We = rho * U^2 * L / sigma


// Verify all are dimensionless
```

<details>
<summary><b>💡 Hint</b></summary>

Use `Foam::sqrt()` for square root. Check dimensionless after each calculation.
</details>

<details>
<summary><b>🔍 Inline Hint: Dimensionless Number Validation</b></summary>

```cpp
// Best practice for dimensionless numbers:
// 1. Calculate using Foam::sqrt() for roots
// 2. Use sqr() for squares (not pow(2))
// 3. Always verify with .dimensionless()
// 4. Log verification for debugging
```
</details>

<details>
<summary><b>✓ Solution</b></summary>

```cpp
// Reynolds number
dimensionedScalar Re = rho * U * L / mu;
Info << "Re = " << Re << ", dimless? " << Re.dimensions().dimensionless() << endl;

// Froude number
dimensionedScalar Fr = U / Foam::sqrt(g * L);
Info << "Fr = " << Fr << ", dimless? " << Fr.dimensions().dimensionless() << endl;

// Weber number
dimensionedScalar We = rho * sqr(U) * L / sigma;
Info << "We = " << We << ", dimless? " << We.dimensions().dimensionless() << endl;
```

**Expected output:** All should return `true` for dimensionless check.
</details>

---

### Exercise 7: Custom Dimension [Advanced]

**Task:** Create a custom dimension for a specialized quantity.

```cpp
// TODO: Create a dimension for heat transfer coefficient h
// Units: W/(m²·K) = [M T^-3 Θ^-1]

dimensionSet dimHeatTransferCoeff(1, 0, -3, 0, 0, -1, 0);

// TODO: Create a dimensionedScalar with this dimension
// h = 1000 W/(m²·K)

// TODO: Verify heat flux q = h * deltaT has correct dimensions [M T^-3]


```

<details>
<summary><b>💡 Hint</b></summary>

dimensionSet constructor: `dimensionSet(M, L, T, I, J, N, Θ)`
</details>

<details>
<summary><b>🔍 Inline Hint: Custom Dimension Strategy</b></summary>

```cpp
// dimensionSet parameter order:
// dimensionSet(M, L, T, I, J, N, Θ)
// M=mass, L=length, T=time, I=current
// J=luminous intensity, N=amount of substance, Θ=temperature
```
</details>

<details>
<summary><b>✓ Solution</b></summary>

```cpp
dimensionSet dimHeatTransferCoeff(1, 0, -3, 0, 0, -1, 0);
dimensionedScalar h("h", dimHeatTransferCoeff, 1000);

dimensionedScalar deltaT("deltaT", dimTemperature, 50);
dimensionedScalar q = h * deltaT;  // Heat flux: W/m²

Info << "h = " << h << endl;
Info << "q = " << q << " (should be [M T^-3])" << endl;
```
</details>

---

### Exercise 8: Debug Dimension Mismatch [Expert]

**Task:** Identify and fix dimension errors in the following code.

```cpp
// This code has dimension errors - find and fix them!
dimensionedScalar rho("rho", dimDensity, 1000);
dimensionedScalar U("U", dimVelocity, 1.0);
dimensionedScalar p("p", dimPressure, 101325);
dimensionedScalar T("T", dimTemperature, 300);

// Error 1: What's wrong with this?
dimensionedScalar speedOfSound = Foam::sqrt(p / rho);

// Error 2: Fix this calculation
dimensionedScalar kineticEnergy = 0.5 * rho * U;  // Missing something?

// Error 3: Correct this Bernoulli term
dimensionedScalar totalPressure = p + rho * U;  // Wrong!
```

<details>
<summary><b>💡 Hint 1</b></summary>

Check units: speed should be [L T^-1], energy should be [M L² T⁻²]
</details>

<details>
<summary><b>💡 Hint 2</b></summary>

Kinetic energy formula: ½ρU² (note the square!)
</details>

<details>
<summary><b>💡 Hint 3</b></summary>

Bernoulli: P + ½ρU² (dynamic pressure has velocity squared)
</details>

<details>
<summary><b>🔍 Inline Hint: Dimension Error Debugging Strategy</b></summary>

```cpp
// Systematic debugging approach:
// 1. Write expected units for each term
// 2. Check if addition/subtraction operands match
// 3. Verify powers (sqr, sqrt) are applied correctly
// 4. Use Info << var.dimensions() to debug
```
</details>

<details>
<summary><b>✓ Solution</b></summary>

```cpp
// Fixed Error 1: Speed of sound calculation
dimensionedScalar speedOfSound = Foam::sqrt(p / rho);  // ✓ Correct!

// Fixed Error 2: Kinetic energy per unit volume
dimensionedScalar kineticEnergy = 0.5 * rho * sqr(U);  // Need U²!

// Fixed Error 3: Total pressure (static + dynamic)
dimensionedScalar totalPressure = p + 0.5 * rho * sqr(U);  // Dynamic pressure

// Verification
Info << "c = " << speedOfSound << " [L T^-1]? " 
     << (speedOfSound.dimensions() == dimVelocity) << endl;
Info << "ke = " << kineticEnergy << " [M L^-1 T^-2]? " 
     << (kineticEnergy.dimensions() == dimPressure) << endl;
Info << "p_tot = " << totalPressure << " [M L^-1 T^-2]? " 
     << (totalPressure.dimensions() == dimPressure) << endl;
```
</details>

---

### Exercise 9: Field Operations with Dimensions [Expert]

**Task:** Perform field operations while maintaining dimensional consistency.

```cpp
// Given fields
volScalarField p(mesh, dimensionedScalar("p", dimPressure, 1e5));
volScalarField T(mesh, dimensionedScalar("T", dimTemperature, 300));
volVectorField U(mesh, dimensionedVector("U", dimVelocity, vector(1, 0, 0)));

// TODO: Create new fields with proper dimensions
// 1. Pressure coefficient: Cp = (p - pRef) / (0.5 * rho * U²)
// 2. Temperature difference normalized: (T - TRef) / TRef
// 3. Velocity magnitude: mag(U)


// Verify all operations are dimensionally consistent
```

<details>
<summary><b>💡 Hint 1</b></summary>

Use `mag(U)` for velocity magnitude, returns dimensionedScalar
</details>

<details>
<summary><b>💡 Hint 2</b></summary>

Cp should be dimensionless (pressure ratio)
</details>

<details>
<summary><b>🔍 Inline Hint: Field Dimension Consistency</b></summary>

```cpp
// Field operations follow same rules as scalars:
// - mag(vectorField) → dimensionedScalarField
// - All arithmetic operations preserve dimensions
// - Result field automatically gets computed dimensions
```
</details>

<details>
<summary><b>✓ Solution</b></summary>

```cpp
dimensionedScalar rho("rho", dimDensity, 1.225);
dimensionedScalar pRef("pRef", dimPressure, 1e5);
dimensionedScalar TRef("TRef", dimTemperature, 300);

// Pressure coefficient (dimensionless)
volScalarField Cp = (p - pRef) / (0.5 * rho * sqr(mag(U)));

// Normalized temperature difference (dimensionless)
volScalarField Theta = (T - TRef) / TRef;

// Velocity magnitude field
volScalarField magU = mag(U);

// Verification
Info << "Cp dimensions: " << Cp.dimensions() << " (dimless? " 
     << Cp.dimensions().dimensionless() << ")" << endl;
Info << "Theta dimensions: " << Theta.dimensions() << " (dimless? " 
     << Theta.dimensions().dimensionless() << ")" << endl;
Info << "magU dimensions: " << magU.dimensions() << " (velocity? " 
     << (magU.dimensions() == dimVelocity) << ")" << endl;
```
</details>

---

## Quick Reference

### Common Methods

> **📋 Complete API reference:** Available in [03_Implementation_Mechanisms.md](03_Implementation_Mechanisms.md)

| Method | Returns | Description |
|--------|---------|-------------|
| `.name()` | `word` | Variable name |
| `.value()` | `scalar`/`vector` | Numerical value |
| `.dimensions()` | `dimensionSet` | Dimension set |
| `.dimensionless()` | `bool` | True if dimensionless |
| `.reset(T v)` | `void` | Reset value |

### Operators

| Operation | Valid When |
|-----------|------------|
| `+`, `-` | Identical dimensions |
| `*`, `/` | Any dimensions (result computed) |
| `pow(scalar)` | Result must be integer dimensions |

### Mathematical Functions

> **📐 Detailed formulations:** See [07_Mathematical_Formulations.md](07_Mathematical_Formulations.md)

| Function | Use Case | Dimension Behavior |
|----------|----------|-------------------|
| `sqr(x)` | Square of value | Dimensions × 2 |
| `Foam::sqrt(x)` | Square root | Dimensions ÷ 2 |
| `pow(x, n)` | Power function | Dimensions × n |
| `mag(x)` | Magnitude | Preserves dimensions |
| `dimless` | Dimensionless value | `[0 0 0 0 0 0 0]` |

---

## 🧠 Concept Check

<details>
<summary><b>1. ทำไม Reynolds number ต้องเป็น dimless?</b></summary>

เพราะ Re เป็น **ratio of inertial forces to viscous forces** → dimensions หักล้างกัน

```cpp
Re = [M L⁻³][L T⁻¹][L] / [M⁻¹ L⁻¹ T] = [M⁰ L⁰ T⁰] = dimless
```
</details>

<details>
<summary><b>2. อ่าน dimensioned value จาก dictionary อย่างไร?</b></summary>

```cpp
// Method 1: Constructor (recommended)
dimensionedScalar nu("nu", dict.lookup("nu"));

// Method 2: Read method
dimensionedScalar nu;
nu.read(dict.lookup("nu"));

// Dimensions automatically read from dictionary entry
// Format: name [M L T I J N Θ] value
```
</details>

<details>
<summary><b>3. สร้าง field พร้อม dimension อย่างไร?</b></summary>

ใช้ `dimensionedScalar("name", dims, value)` ใน field constructor

```cpp
volScalarField T
(
    IOobject("T", runTime.timeName(), mesh, IOobject::NO_READ),
    mesh,
    dimensionedScalar("T", dimTemperature, 300)
);

// Field inherits dimensions from initial value
```
</details>

<details>
<summary><b>4. Dimension checking เกิดขึ้นเมื่อไร?</b></summary>

- **Compile-time:** Template operations ตรวจสอบตอน compile
- **Runtime:** `dimensionSet` ตรวจสอบตอน run ถ้า operations ผิดจะ abort

```cpp
// Compile-time error (templates)
// dimensionedScalar a = b + c;  // Checked at compile-time if possible

// Runtime error (dimensionSet)
// dimensionedScalar d = e + f;  // Checked at runtime, aborts if mismatch
```
</details>

<details>
<summary><b>5. สร้าง custom dimension อย่างไร?</b></summary>

```cpp
// dimensionSet constructor: dimensionSet(M, L, T, I, J, N, Θ)
dimensionSet customDim(1, 0, -2, 0, 0, 0, 0);  // [M L^0 T^-2]

// Example: Heat transfer coefficient [M T^-3 Θ^-1]
dimensionSet dimHeatTransferCoeff(1, 0, -3, 0, 0, -1, 0);

// Use in dimensionedScalar
dimensionedScalar h("h", dimHeatTransferCoeff, 1000);
```
</details>

<details>
<summary><b>6. จะ debug dimension errors อย่างไร?</b></summary>

```cpp
// Strategy 1: Print dimensions
Info << "Variable dims: " << var.dimensions() << endl;

// Strategy 2: Check equality
if (var.dimensions() == dimVelocity) { /* ... */ }

// Strategy 3: Verify dimensionless
if (!result.dimensions().dimensionless()) {
    FatalError << "Result should be dimensionless!" << endl;
}

// Strategy 4: Use dimensional analysis on paper first
// Write expected units, then check if code matches

// See [05_Pitfalls_and_Solutions.md](05_Pitfalls_and_Solutions.md) for detailed debugging flow
```
</details>

---

## 📖 Related Documentation

### In This Module
- **Overview:** [00_Overview.md](00_Overview.md) — Module structure and consolidated SI dimensions reference
- **Introduction:** [01_Introduction.md](01_Introduction.md) — Full dimension alias reference
- **Implementation:** [03_Implementation_Mechanisms.md](03_Implementation_Mechanisms.md) — Detailed API reference
- **Pitfalls:** [05_Pitfalls_and_Solutions.md](05_Pitfalls_and_Solutions.md) — Common errors, debugging flow, and fixes
- **Mathematics:** [07_Mathematical_Formulations.md](07_Mathematical_Formulations.md) — Dimension algebra rules and Buckingham π theorem

### Cross-Module References
- **Foundation Primitives:** [../../01_FOUNDATION_PRIMITIVES/00_Overview.md](../../01_FOUNDATION_PRIMITIVES/00_Overview.md) — Basic types overview
- **Template Metaprogramming:** [04_Template_Metaprogramming.md](04_Template_Metaprogramming.md) — Compile-time checking mechanisms
- **Engineering Applications:** [06_Engineering_Benefits.md](06_Engineering_Benefits.md) — Real-world use cases and productivity gains

---

## 🎯 Next Steps

หลังจากผ่านบทนี้:
1. ✅ ลองเขียน custom solver ที่ใช้ dimensioned types
2. ✅ ศึกษา template metaprogramming ใน [04_Template_Metaprogramming.md](04_Template_Metaprogramming.md)
3. ✅ ดู engineering applications ใน [06_Engineering_Benefits.md](06_Engineering_Benefits.md)
4. ✅ ทดลองเขียน validation scripts สำหรับตรวจสอบ dimensions ของ case files
5. ✅ สร้าง custom dimensions สำหรับ specialized physics models

---

## 📝 Exercise Completion Checklist

Use this checklist to track your progress:

- [ ] Exercise 1: Basic dimensioned value creation [Beginner]
- [ ] Exercise 2: Dimension arithmetic operations [Beginner]
- [ ] Exercise 3: Reynolds number calculation [Intermediate]
- [ ] Exercise 4: Field initialization with dimensions [Intermediate]
- [ ] Exercise 5: Dictionary file reading [Intermediate]
- [ ] Exercise 6: Dimensionless numbers validation [Advanced]
- [ ] Exercise 7: Custom dimension creation [Advanced]
- [ ] Exercise 8: Debug dimension mismatches [Expert]
- [ ] Exercise 9: Field operations with dimensions [Expert]

**Completion:** ━━━━━━━━━━━━━━━━━ **Your Progress**