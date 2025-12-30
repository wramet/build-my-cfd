# Dimensioned Types - Introduction

> **ทำไมต้องเรียนบทนี้?**
> - เข้าใจวิธีสร้าง dimensioned values
> - รู้วิธีอ่านจาก dictionary
> - ป้องกัน common errors

---

## Learning Objectives

By the end of this lesson, you will be able to:

1. **Create** dimensioned types with proper units and names
2. **Read** dimensioned values from dictionary files
3. **Perform** dimensional arithmetic and understand automatic unit checking
4. **Apply** dimensioned types in common CFD scenarios (Reynolds number, time scales)
5. **Debug** common dimension-related errors

---

## Overview

> **💡 Dimensioned Types = ตัวเลข + หน่วย + ชื่อ**
>
> ไม่ใช่แค่ `1000` แต่คือ `rho = 1000 kg/m³`

```cpp
dimensionedScalar rho("rho", dimDensity, 1000);
// Name: "rho"           → ใช้ใน output/debug
// Dimensions: [M L^-3]  → ตรวจสอบ physics
// Value: 1000           → ค่าจริง
```

**Key Concept:** OpenFOAM tracks physical units throughout your simulation, preventing costly mistakes like adding velocity to pressure or using wrong viscosity units.

**See Also:** Complete SI dimensions reference table in [00_Overview.md](00_Overview.md#si-dimensions-reference)

---

## 1. Why Dimensioned Types?

| Benefit | Description | Example |
|---------|-------------|---------|
| **Type Safety** | Prevents unit mismatches | Cannot add `m/s` to `Pa` |
| **Self-documenting** | Units visible in code | `nu` clearly shows `[L²/T]` |
| **Error Detection** | Catches physics errors early | Compile-time dimension check |
| **Automatic Checking** | Both compile and runtime | Runtime verification in solvers |
| **Debugging Aid** | Meaningful names in output | "rho" vs "1000" in logs |

---

## 2. Core Classes

### dimensionedScalar

```cpp
dimensionedScalar nu("nu", dimKinematicViscosity, 1e-6);

// Access components
word name = nu.name();           // "nu"
dimensionSet dims = nu.dimensions();  // [0 2 -1 0 0 0 0]
scalar value = nu.value();       // 1e-6
```

### dimensionedVector

```cpp
dimensionedVector g("g", dimAcceleration, vector(0, 0, -9.81));
// Gravity vector with proper acceleration units [L/T²]
```

### dimensionedTensor

```cpp
dimensionedTensor I("I", dimless, tensor::I);
// Identity tensor (dimensionless)
```

### dimensionedSymmTensor

```cpp
dimensionedSymmTensor tau("tau", dimPressure, symmTensor(0));
// Symmetric stress tensor [M/LT²]
```

---

## 3. Understanding dimensionSet

```cpp
// 7 SI base dimensions: [M, L, T, Θ, I, N, J]
dimensionSet(M, L, T, Θ, I, N, J)
```

**Common Predefined Sets:**

| Name | Dimensions | Physical Quantity |
|------|------------|-------------------|
| `dimless` | [0 0 0 0 0 0 0] | Dimensionless |
| `dimLength` | [0 1 0 0 0 0 0] | Length |
| `dimTime` | [0 0 1 0 0 0 0] | Time |
| `dimMass` | [1 0 0 0 0 0 0] | Mass |
| `dimTemperature` | [0 0 0 1 0 0 0] | Temperature |
| `dimVelocity` | [0 1 -1 0 0 0 0] | Velocity [L/T] |
| `dimAcceleration` | [0 1 -2 0 0 0 0] | Acceleration [L/T²] |
| `dimDensity` | [1 -3 0 0 0 0 0] | Density [M/L³] |
| `dimPressure` | [1 -1 -2 0 0 0 0] | Pressure [M/LT²] |
| `dimKinematicViscosity` | [0 2 -1 0 0 0 0] | Kinematic viscosity [L²/T] |
| `dimDynamicViscosity` | [1 -1 -1 0 0 0 0] | Dynamic viscosity [M/LT] |

> **📚 Complete Reference:** See [00_Overview.md](00_Overview.md#si-dimensions-reference) for full dimensions table

---

## 4. Creating Dimensioned Values

### From Literals

```cpp
dimensionedScalar T0("T0", dimTemperature, 300.0);  // 300 K
dimensionedScalar p0("p0", dimPressure, 101325);    // 101325 Pa
dimensionedVector U0("U0", dimVelocity, vector(1, 0, 0));  // 1 m/s in x
```

### From Dictionary

```cpp
// In constant/transportProperties:
// nu              nu [0 2 -1 0 0 0 0] 1e-6;

IOdictionary transProp(IOobject(
    "transportProperties",
    runTime.constant(),
    mesh,
    IOobject::MUST_READ
));

dimensionedScalar nu(
    "nu", 
    dimKinematicViscosity, 
    transProp
);

// Alternative:
auto nu = transProp.get<dimensionedScalar>("nu");
```

### Manual Construction

```cpp
// Full specification
dimensionedScalar value(
    "name",              // Identifier
    dimensionSet(1, -3, 0, 0, 0, 0, 0),  // [M L^-3]
    1000                 // Value
);
```

---

## 5. Dimensional Arithmetic

### Basic Operations

```cpp
dimensionedScalar a("a", dimLength, 2.0);
dimensionedScalar b("b", dimLength, 3.0);
dimensionedScalar c("c", dimTime, 5.0);

dimensionedScalar d = a + b;    // OK: same dims [L]
dimensionedScalar e = a * b;    // Result: dimArea [L²]
dimensionedScalar f = a / c;    // Result: dimVelocity [L/T]

// Compile ERROR: dimension mismatch
// dimensionedScalar g = a + c;  // Cannot add [L] + [T]
```

### Powers and Roots

```cpp
dimensionedScalar L("L", dimLength, 2.0);

dimensionedScalar area = sqr(L);      // [L²] = L²
dimensionedScalar volume = pow3(L);   // [L³] = L³
dimensionedScalar root = sqrt(L);     // [L^0.5]
dimensionedScalar cube_root = pow(L, 1.0/3.0);  // [L^(1/3)]
```

### Vector/Tensor Operations

```cpp
dimensionedVector v("v", dimVelocity, vector(1, 2, 3));
dimensionedScalar mag_v = mag(v);     // [L/T] - magnitude
dimensionedScalar sqr_v = sqr(v);     // [L²/T²] - squared magnitude

dimensionedTensor tau("tau", dimPressure, tensor(...));
dimensionedScalar tr_tau = tr(tau);  // Trace (same dims)
```

---

## 6. Common Patterns in CFD

### Characteristic Length Scale

```cpp
dimensionedScalar L(
    "L", 
    dimLength, 
    mesh.bounds().span().x()
);
```

### Reynolds Number Calculation

```cpp
dimensionedScalar rho("rho", dimDensity, 1000);
dimensionedScalar U("U", dimVelocity, 1.0);
dimensionedScalar L("L", dimLength, 0.1);
dimensionedScalar mu("mu", dimDynamicViscosity, 0.001);

dimensionedScalar Re = rho * U * L / mu;
// [M L^-3][L T^-1][L][M^-1 L T] = [1] (dimensionless)
Info << "Reynolds number: " << Re.value() << endl;
```

### Time Scale Estimation

```cpp
// Convection time scale
dimensionedScalar tau_conv = L / Uref;  // [L]/[L T^-1] = [T]

// Diffusion time scale
dimensionedScalar tau_diff = sqr(L) / nu;  // [L²]/[L²/T] = [T]
```

### Dimensionless Numbers

```cpp
// Courant number (local)
dimensionedScalar Co = mag(U) * runTime.deltaT() / mesh.deltaCoeffs();

// Froude number
dimensionedScalar Fr = mag(U) / sqrt(dimAcceleration * g.length());
```

---

## 7. Integration with Fields

### Initializing Fields

```cpp
// Initialize uniform field
volScalarField T
(
    IOobject("T", runTime.timeName(), mesh),
    mesh,
    dimensionedScalar("T", dimTemperature, 300)
);

// Initialize from dimensioned value
volVectorField U
(
    IOobject("U", runTime.timeName(), mesh),
    dimensionedVector("U", dimVelocity, vector::zero)
);
```

### Field Operations

```cpp
// Multiply field by dimensioned scalar
volScalarField p2 = p * dimensionedScalar("one", dimless, 2.0);

// Add dimensioned offset
T += dimensionedScalar("dT", dimTemperature, 10);

// Boundary conditions with dimensioned values
fixedValueFvPatchScalarField::typeValue = 
    dimensionedScalar("Twall", dimTemperature, 350);
```

### Time-dependent Scaling

```cpp
// Linear ramp
dimensionedScalar tFactor("tFactor", dimless, 0);
tFactor.value() = runTime.value() / runTime.endTime().value();

U *= (1.0 - tFactor) + 0.5 * tFactor;  // Ramp from 1.0 to 0.5
```

---

## Quick Reference: Essential Methods

| Method | Returns | Description |
|--------|---------|-------------|
| **Accessors** |
| `.name()` | `word` | Identifier for output/debug |
| `.value()` | `scalar` | Numeric value |
| `.dimensions()` | `dimensionSet` | Dimension specification |
| **Component Access** |
| `.component(i)` | `scalar` | Vector component (0-2) |
| `.x()`, `.y()`, `.z()` | `scalar` | Vector components |
| **Conversions** |
| `.value() * ...` | `scalar` | Extract raw value |
| `mag(...)` | dimensioned | Magnitude (same dims) |
| `sqr(...)` | dimensioned | Squared (dims²) |
| `sqrt(...)` | dimensioned | Square root (dims^0.5) |
| **Utilities** |
| `operator<<()` | - | Stream output (with units) |
| `read(Istream&)` | - | Parse from input stream |

---

## 🧠 Concept Check

<details>
<summary><b>1. ทำไมต้องใช้ dimensionedScalar แทน scalar?</b></summary>

เพื่อ **track physical units** — ป้องกัน errors จาก unit mismatches และช่วย debug ด้วย meaningful names

</details>

<details>
<summary><b>2. dimensionSet 7 ตัวคืออะไร?</b></summary>

**SI base units**: Mass [M], Length [L], Time [T], Temperature [Θ], Current [I], Moles [N], Luminous Intensity [J]

</details>

<details>
<summary><b>3. อ่าน dimensions จาก dictionary อย่างไร?</b></summary>

```cpp
// Method 1: Constructor
dimensionedScalar nu("nu", dimKinematicViscosity, dict);

// Method 2: Direct lookup
auto nu = dict.get<dimensionedScalar>("nu");

// Method 3: Template lookup
dimensionedScalar value;
dict.readEntry("nu", value);
```

</details>

<details>
<summary><b>4. เกิด compile error ตอนบวก velocity กับ pressure ได้ไหม?</b></summary>

**ใช่** — OpenFOAM checks dimensions at compile-time:
```cpp
dimensionedScalar v("v", dimVelocity, 1.0);      // [0 1 -1 0 0 0 0]
dimensionedScalar p("p", dimPressure, 1.0);      // [1 -1 -2 0 0 0 0]
auto result = v + p;  // COMPILE ERROR!
// Error: dimensions given [0 1 -1 0 0 0 0] but expected [1 -1 -2 0 0 0 0]
```

</details>

<details>
<summary><b>5. คำนวณ Reynolds number อย่างไรให้ถูกต้อง?</b></summary>

```cpp
dimensionedScalar Re = rho * U * L / mu;
// Check dimensions:
// [M L^-3] × [L T^-1] × [L] / [M L^-1 T^-1]
// = [M^0 L^0 T^0] ✓ (dimensionless)
```

</details>

---

## 📖 Related Documentation

- **Overview:** [00_Overview.md](00_Overview.md) — Complete SI dimensions reference
- **Mathematical Formulations:** [07_Mathematical_Formulations.md](07_Mathematical_Formulations.md) — Dimension algebra
- **Type System:** [03_Type_System.md](03_Type_System.md) — Template metaprogramming
- **Runtime Checking:** [04_Runtime_Checking.md](04_Runtime_Checking.md) — Debugging dimensions