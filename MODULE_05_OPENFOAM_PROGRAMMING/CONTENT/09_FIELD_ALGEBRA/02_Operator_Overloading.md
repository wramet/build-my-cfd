# Operator Overloading in Field Algebra

## Learning Objectives

**What will you learn?**
- Understand how C++ operators are overloaded for field operations
- Master element-wise comparison operators (pos, neg)
- Learn special boundary assignment syntax (== operator)
- Apply compound assignment operators (+=, -=, *=, /=)
- Recognize dimensional checking in operator overloading
- Distinguish between field operators and standard C++ operators

**Prerequisites:**
- Basic C++ operator overloading concepts
- Understanding of OpenFOAM field types (volScalarField, volVectorField)
- Knowledge of field algebra fundamentals from [[00_Overview.md]]

---

## Why Operator Overloading Matters

> [!TIP] **ทำไม Operator Overloading สำคัญใน OpenFOAM?**
> **Operator Overloading** คือเทคนิคที่ทำให้การเขียนสมการทางฟิสิกส์ใน OpenFOAM ดูเหมือนสมการคณิตศาสตร์:
> - **Natural Syntax:** เขียน `a + b` แทนที่จะเป็น `add(a, b)` → โค้ดอ่านง่ายและใกล้เคียงสมการจริง
> - **Element-wise Operations:** การดำเนินการกับ field ทั้งหมดพร้อมกัน → ไม่ต้องเขียน loop
> - **Type Safety:** Dimensional checking ผ่าน operators → error ตั้งแต่ compile-time
> - **Performance:** Compiler สามารถ optimize operators ได้ดีกว่า function calls
>
> 💡 **ถ้าคุณจะเขียน custom solver หรือ boundary condition:** การเข้าใจ operators พวกนี้จะช่วยให้คุณเขียนโค้ดที่กระชับ ถูกต้อง และมีประสิทธิภาพ

---

## Core Concept

> Operator Overloading = Using C++ syntax for field-wide mathematical operations

```mermaid
flowchart LR
    A[Standard C++ Operators] --> B[OpenFOAM Overloaded]
    B --> C[Natural Field Syntax]
    C --> D[Element-wise Operations]
    D --> E[Dimension Checking]
```

---

## 1. Comparison Operators (pos/neg)

> [!NOTE] **📂 OpenFOAM Context: Conditional Field Operations**
> ส่วนนี้เกี่ยวข้องกับ **การสร้าง conditional fields** สำหรับการคำนวณแบบมีเงื่อนไข
> - **Conditional Operations:** ใช้ในการกำหนด source terms ที่ขึ้นกับตำแหน่งหรือเวลา
> - **Mask Creation:** สร้าง mask fields สำหรับ operations บางส่วนของ domain
> - **Source Term Switching:** เปิด/ปิด source terms ตามเงื่อนไข (เช่น การเผาไหม้เมื่อ T > T_ignition)
> - **Multi-phase Models:** ใช้ในการกำหนด phase interaction regions
> - **Turbulence Models:** ใช้ใน wall damping functions (เช่น ยกเลิก turbulence production ใกล้ผนัง)
>
> 💡 **ตัวอย่างการใช้งานจริง:** ใน combustion solver, ใช้ `pos(T - T_ignition)` เพื่อเปิด reaction source term เฉพาะบริเวณที่มีอุณหภูมิสูงพอ

### How pos() and neg() Work

```cpp
volScalarField T = ...;      // Temperature field
scalar Tcrit = 1000.0;       // Critical temperature

// Positive where condition is true (> 0)
volScalarField highT = pos(T - Tcrit);
// Result: 1.0 where T > Tcrit, 0.0 elsewhere

// Negative where condition is true (< 0)
volScalarField lowT = neg(T - Tcrit);
// Result: 1.0 where T < Tcrit, 0.0 elsewhere
```

> [!TIP] **ทำไมต้องใช้ pos/neg แทน if-statement?**
> **`pos()` และ `neg()`** ทำงานบนทุก cell พร้อมกัน (vectorized) → เร็วกว่าการใช้ loop กับ if-statement มาก
> - **Performance:** Compiler สามารถ optimize ให้เป็น SIMD operations
> - **Readability:** โค้ดกระชับและใกล้เคียงสมการคณิตศาสตร์
> - **Field-based:** ไม่ต้องเขียน loop เอง → OpenFOAM จัดการให้หมด
>
> 💡 **Best Practice:** ใช้ `pos()` และ `neg()` สำรอง conditional field operations ใน solver

### pos vs neg Comparison

| Function | Returns 1.0 where | Returns 0.0 where | Example |
|----------|-------------------|-------------------|---------|
| `pos(x)` | `x > 0` | `x <= 0` | `pos(T - 1000)` → 1.0 at T > 1000 K |
| `neg(x)` | `x < 0` | `x >= 0` | `neg(T - 1000)` → 1.0 at T < 1000 K |

💡 **Important:** `pos(x) + neg(x)` does NOT equal 1.0 everywhere (at x = 0, both return 0.0)

### Practical Examples

#### Example 1: Temperature-Dependent Source Term

```cpp
// Heat source only active above ignition temperature
volScalarField T = ...;
dimensionedScalar Tignition("Tignition", dimTemperature, 1000.0);
dimensionedScalar Qmax("Qmax", dimPower/dimVol, 1e6);

// Source term: Q = Qmax * pos(T - Tignition)
volScalarField heatSource = Qmax * pos(T - Tignition);
```

#### Example 2: Multi-Phase Interface Masking

```cpp
// Interface region (where alpha is between 0.01 and 0.99)
volScalarField alpha = ...;  // Volume fraction field
volScalarField interface = pos(alpha - 0.01) * pos(0.99 - alpha);
// Result: 1.0 in interface region, 0.0 elsewhere

// Surface tension force only at interface
volVectorField Fst = sigma * fvc::grad(alpha) * interface;
```

#### Example 3: Wall Damping Function

```cpp
// Turbulence damping near walls
volScalarField y = mesh.mag().dist();  // Distance to nearest wall
dimensionedScalar yPlusCrit("yPlusCrit", dimLength, 11.0);

// Damping factor: 1.0 away from wall, 0.0 in viscous sublayer
volScalarField wallDamping = neg(yPlusCrit - y);

// Apply to turbulence production
volScalarField P = neg(yPlusCrit - y) * productionTerm;
```

#### Example 4: Multi-Zone Source Term

```cpp
// Three-zone heat transfer problem
volScalarField T = ...;
volScalarField x = mesh.C().component(0);  // x-coordinate

// Zone 1: x < 0.3
volScalarField zone1 = neg(x - 0.3);

// Zone 2: 0.3 <= x <= 0.7
volScalarField zone2 = pos(x - 0.3) * pos(0.7 - x);

// Zone 3: x > 0.7
volScalarField zone3 = pos(x - 0.7);

// Apply different source terms
volScalarField source = zone1 * Q1 + zone2 * Q2 + zone3 * Q3;
```

#### Example 5: Time-Dependent Switching

```cpp
// Activate source term only during certain time window
scalar tStart = 1.0;
scalar tEnd = 3.0;
scalar t = runTime.timeOutputValue();

// Time window mask
volScalarField timeWindow = pos(t - tStart) * pos(tEnd - t);

// Apply source term
volScalarField Q = timeWindow * Qmax;
```

---

## 2. Boundary Assignment Operator (==)

> [!NOTE] **📂 OpenFOAM Context: Boundary Condition Assignment**
> ส่วนนี้เกี่ยวข้องกับ **การกำหนดค่าที่ boundary patches** ซึ่งเป็น syntax พิเศษของ OpenFOAM
> - **Special Syntax:** `==` สำหรับ boundary assignment → ต่างจาก standard C++ assignment
> - **Patch Identification:** ใช้ `mesh.boundaryMesh().findPatchID("patchName")`
> - **Boundary Field Access:** `.boundaryFieldRef()[patchI]` → reference ถึง boundary field
> - **FixedValue BC:** ใช้ `==` กับ patches ที่เป็น `fixedValue` type
> - **Time-Varying BC:** สามารถใช้ loop กับ `==` เพื่อสร้าง spatially/temporally varying profiles
>
> 💡 **ตัวอย่างการใช้งานจริง:** ใช้ใน custom function objects หรือ boundary conditions ที่ต้องการกำหนดค่าแบบ dynamic

### = vs == for Boundaries

```cpp
// Standard C++ assignment (=)
volScalarField T = ...;
T = 300.0;  // Assigns to internal field

// OpenFOAM boundary assignment (==)
label inletPatchI = mesh.boundaryMesh().findPatchID("inlet");
T.boundaryFieldRef()[inletPatchI] == 300.0;
// Assigns to boundary patch
```

> [!WARNING] **⚠️ Critical: Always use == for Boundaries**
> - **`field.boundaryFieldRef()[patchI] = value`**: ❌ **WRONG** → May cause runtime errors
> - **`field.boundaryFieldRef()[patchI] == value`**: ✓ **CORRECT** → OpenFOAM boundary assignment
>
> 💡 **เหตุผล:** `==` ถูก overload ให้เรียก `operator==()` ซึ่งจัดการ boundary assignment อย่างถูกต้อง รวมถึงการตรวจสอบประเภทของ BC

### Boundary Assignment Workflow

```mermaid
flowchart LR
    A[Find Patch ID] --> B[Get Boundary Field Reference]
    B --> C[Use == Operator]
    C --> D[Value Assigned to Patch]
    
    A --> A1["mesh.boundaryMesh()<br/>.findPatchID<br/>(\"name\")"]
    B --> B1["field.boundaryFieldRef()<br/>[patchI]"]
    C --> C1["== value"]
```

### Practical Examples

#### Example 1: Uniform Boundary Value

```cpp
// Set inlet temperature
label inletPatchI = mesh.boundaryMesh().findPatchID("inlet");
dimensionedScalar Tinlet("Tinlet", dimTemperature, 300.0);

T.boundaryFieldRef()[inletPatchI] == Tinlet;
```

#### Example 2: Parabolic Velocity Profile

```cpp
// Parabolic velocity profile at inlet
label inletPatchI = mesh.boundaryMesh().findPatchID("inlet");
const fvPatchVectorField& inletPatch = U.boundaryField()[inletPatchI];
const vectorField& faceCentres = mesh.Cf().boundaryField()[inletPatchI];

vectorField& Uinlet = U.boundaryFieldRef()[inletPatchI];

// Calculate parabolic profile based on y-coordinate
forAll(inletPatch, faceI)
{
    scalar y = faceCentres[faceI].y();
    scalar yMax = 0.1;  // Channel half-height
    scalar Umax = 1.0;  // Centerline velocity

    Uinlet[faceI] == vector(Umax * (1.0 - sqr(y/yMax)), 0, 0);
}
```

#### Example 3: Oscillating Boundary Condition

```cpp
// Oscillating inlet velocity
label inletPatchI = mesh.boundaryMesh().findPatchID("inlet");
vectorField& Uinlet = U.boundaryFieldRef()[inletPatchI];

dimensionedScalar omega("omega", dimless/dimTime, 2.0 * pi * 0.5);  // 0.5 Hz
dimensionedScalar Uamplitude("Uamplitude", dimVelocity, 1.0);

scalar t = runTime.timeOutputValue();

forAll(Uinlet, faceI)
{
    Uinlet[faceI] == vector(
        Uamplitude.value() * Foam::sin(omega.value() * t), 
        0, 
        0
    );
}
```

#### Example 4: Radial Profile

```cpp
// Radial velocity profile at inlet
label inletPatchI = mesh.boundaryMesh().findPatchID("inlet");
vectorField& Uinlet = U.boundaryFieldRef()[inletPatchI];
const vectorField& Cf = mesh.Cf().boundaryField()[inletPatchI];

forAll(Uinlet, faceI)
{
    scalar r = Foam::sqrt(sqr(Cf[faceI].x()) + sqr(Cf[faceI].y()));
    scalar R = 0.05;  // Pipe radius
    scalar Umax = 2.0;
    
    // Parabolic profile: U = Umax * (1 - r^2/R^2)
    scalar Ur = Umax * (1.0 - sqr(r/R));
    
    Uinlet[faceI] == vector(0, 0, Ur);  // Assuming flow in z-direction
}
```

#### Example 5: Copying Between Fields

```cpp
// Copy boundary values from one field to another
label inletPatchI = mesh.boundaryMesh().findPatchID("inlet");

// Copy velocity boundary field
volVectorField Unew("Unew", U);
Unew.boundaryFieldRef()[inletPatchI] == U.boundaryField()[inletPatchI];
```

#### Example 6: Temperature Profile from Function

```cpp
// Temperature profile following a function
label inletPatchI = mesh.boundaryMesh().findPatchID("inlet");
scalarField& Tinlet = T.boundaryFieldRef()[inletPatchI];
const vectorField& Cf = mesh.Cf().boundaryField()[inletPatchI];

forAll(Tinlet, faceI)
{
    scalar y = Cf[faceI].y();
    
    // Exponential temperature profile
    Tinlet[faceI] == 300.0 + 100.0 * Foam::exp(-y/0.05);
}
```

---

## 3. Compound Assignment Operators

> [!NOTE] **📂 OpenFOAM Context: In-Place Field Modifications**
> ส่วนนี้เกี่ยวข้องกับ **การปรับปรุงค่า field แบบ in-place** ซึ่งมีประสิทธิภาพสูงกว่าการสร้าง field ใหม่
> - **Memory Efficiency:** ไม่ต้องสร้าง temporary fields → ประหยัด memory
> - **Performance:** Compiler สามารถ optimize ให้ดีกว่าการแยก operations
> - **Solver Usage:** ใช้ในการสะสม source terms หรือ corrections
> - **Matrix Assembly:** ใช้ในการรวม contributions จากหลาย sources
> - **Time Stepping:** ใช้ในการ update fields ระหว่าง time steps
>
> 💡 **ตัวอย่างการใช้งานจริง:** ใน iterative solvers, ใช้ `+=` เพื่อสะสม corrections จากแต่ละ iteration

### Available Compound Operators

```cpp
volScalarField T = ...;
volScalarField source = ...;
dimensionedScalar factor("factor", dimless, 2.0);

// Addition assignment
T += source;  // T = T + source

// Subtraction assignment
T -= sink;    // T = T - sink

// Multiplication assignment
T *= factor;  // T = T * factor

// Division assignment
T /= divisor; // T = T / divisor
```

> [!TIP] **ทำไม += ดีกว่า T = T + source?**
> **`+=`** (compound assignment) มีประสิทธิภาพดีกว่า **`T = T + source`** เพราะ:
> - **No Temporary:** ไม่สร้าง temporary field สำหรับ `T + source`
> - **In-Place Operation:** แก้ไขค่าโดยตรงใน memory เดิม
> - **Better Cache Locality:** ใช้ cache ได้ดีกว่า
> - **Cleaner Syntax:** โค้ดกระชับและอ่านง่ายกว่า
>
> 💡 **Best Practice:** ใช้ compound operators (`+=`, `-=`, `*=`, `/=`) สำหรับ in-place modifications ใน solver loops

### Performance Comparison

```cpp
// Less efficient: Creates temporary field
volScalarField temp = T + source;
T = temp;

// More efficient: In-place modification
T += source;
```

### Practical Examples

#### Example 1: Accumulating Multiple Source Terms

```cpp
// Multiple source contributions
volScalarField T = ...;
volScalarField heatSource = ...;
volScalarField reactionSource = ...;
volScalarField viscousDissipation = ...;
volScalarField radiationSource = ...;

// Accumulate all sources efficiently
T += heatSource;
T += reactionSource;
T += viscousDissipation;
T += radiationSource;
```

#### Example 2: Explicit Time Integration

```cpp
// Explicit Euler time stepping: T_new = T_old + dt * dTdt
volScalarField T = ...;
volScalarField dTdt = fvc::div(phi, T) - fvc::laplacian(alpha, T);
scalar dt = runTime.deltaTValue();

T += dt * dTdt;
```

#### Example 3: Field Normalization

```cpp
// Normalize field by maximum value
volScalarField T = ...;
scalar maxT = max(T).value();
scalar minT = min(T).value();

// Normalize to [0, 1]
T -= minT;      // Shift to start from 0
T /= (maxT - minT);  // Scale to [0, 1]
```

#### Example 4: Velocity Correction

```cpp
// Apply pressure correction to velocity field
volVectorField U = ...;
volScalarField p = ...;
scalar dt = runTime.deltaTValue();

// Correct velocity with pressure gradient
U -= fvc::grad(p) * dt;

// Add additional correction
volVectorField Ucorr = ...;
U += Ucorr;
```

#### Example 5: Relaxation in Iterative Solvers

```cpp
// Under-relaxation for stability
volScalarField T = ...;
volScalarField Tnew = ...;
scalar alpha = 0.7;  // Relaxation factor

// T = alpha * Tnew + (1 - alpha) * T
T *= (1.0 - alpha);
T += alpha * Tnew;
```

#### Example 6: Scale Field Values

```cpp
// Convert units: Kelvin to Celsius
volScalarField T_K = ...;
volScalarField T_C(T_K);

T_C -= 273.15;  // Subtract offset

// Scale velocity from m/s to km/h
volVectorField U_ms = ...;
volVectorField U_kmh(U_ms);

U_kmh *= 3.6;  // Multiply by conversion factor
```

#### Example 7: Apply Damping Factor

```cpp
// Apply time-dependent damping
volScalarField field = ...;
scalar t = runTime.timeOutputValue();

// Damping factor: decays exponentially
dimensionedScalar damping("damping", dimless, Foam::exp(-t));

field *= damping;
```

#### Example 8: Accumulate Corrections from Multiple Iterations

```cpp
// Iterative solver with multiple corrections
volScalarField p = ...;
volScalarField pCorr = ...;

for (int iter = 0; iter < maxIter; iter++)
{
    // Solve for correction
    pCorr = solve(fvm::laplacian(pCorr) == fvc::div(phi)).initialResidual();

    // Accumulate correction
    p += pCorr;

    // Check convergence
    if (max(pCorr) < tolerance) break;
}
```

---

## 4. Dimensional Checking in Operators

> [!NOTE] **📂 OpenFOAM Context: Dimensional Consistency Enforcement**
> ส่วนนี้เกี่ยวข้องกับ **การตรวจสอบความสอดคล้องของ units** ผ่าน operator overloading
> - **Compile-Time Checking:** Operators ตรวจสอบ dimensions ตั้งแต่ compile-time
> - **Dimensioned Types:** ทุก field มี dimensions attached → ดูรายละเอียดใน [[../02_DIMENSIONED_TYPES/00_Overview.md]]
> - **DimensionSet:** ตัวอย่างเช่น `[kg m^2 s^-2]` สำหรับ energy
> - **Automatic Reduction:** การคูณ/หาร fields จะคำนวณ dimensions ให้อัตโนมัติ
> - **Error Prevention:** ป้องกันการเขียนสมการที่ dimensionally inconsistent
>
> 💡 **ตัวอย่างการใช้งานจริง:** ในการเขียน solver, การตรวจสอบ dimensions ช่วยหา bugs ตั้งแต่ early stage

### How Dimensional Checking Works

```cpp
volScalarField p(dimPressure, mesh);      // [kg m^-1 s^-2]
volVectorField U(dimVelocity, mesh);      // [m s^-1]
volScalarField rho(dimDensity, mesh);     // [kg m^-3]
dimensionedScalar alpha(dimKinematicViscosity, 1e-5);  // [m^2 s^-1]

// ✓ Correct: pressure + pressure (dimensions match)
volScalarField totalP = p + dynP;

// ✓ Correct: dynamic pressure = 0.5 * rho * |U|^2 ([kg m^-1 s^-2])
volScalarField dynP = 0.5 * rho * magSqr(U);

// ❌ Error: pressure + velocity (dimension mismatch)
// volScalarField bad = p + U;  // COMPILER ERROR!

// ✓ Correct: kinematic viscosity = mu / rho ([m^2 s^-1])
volScalarField nu = mu / rho;

// ✓ Correct: diffusion = laplacian(alpha, T) ([K s^-1])
volScalarField diffusion = fvc::laplacian(alpha, T);

// ❌ Error: adding temperature to heat flux (dimension mismatch)
// volScalarField bad = T + heatFlux;  // COMPILER ERROR!
```

> [!WARNING] **⚠️ Common Dimensional Mistakes**
> - **Forgetting `dimensionedScalar`:** ไม่สามารถใช้ `double` โดยตรงกับ field ได้
> - **Wrong Dimensions:** ใช้ `dimPressure` แทน `dimDynamicPressure`
> - **Mixed Units:** บวกกัน fields ที่มี units ต่างกัน (เช่น `p [Pa] + T [K]`)
>
> 💡 **เคล็ดลับ:** ถ้า compiler แจ้ง error เกี่ยวกับ dimensions ให้ตรวจสอบ:
> 1. ใช้ `dimensionedScalar` สำหรับ constants หรือไม่?
> 2. Units ของทั้งสอง fields สอดคล้องกันหรือไม่?
> 3. ผลลัพธ์ของ operation มี dimensions ที่ถูกต้องหรือไม่?

### Creating Dimensioned Scalars

```cpp
// Method 1: Direct constructor
dimensionedScalar rho
(
    "rho",                 // Name
    dimDensity,            // Dimensions [kg m^-3]
    1.225                  // Value
);

// Method 2: From dictionary
dimensionedScalar rho
(
    transportProperties.lookup("rho")
);

// Method 3: With name, dimensions, and value separately
dimensionedScalar pRef
(
    "pRef",
    dimPressure,
    101325.0
);
```

### Dimension Rules for Operators

| Operation | Dimension Rule | Example |
|-----------|---------------|---------|
| **Addition (+)** | Dimensions must match | `p + p` ✓, `p + T` ✗ |
| **Subtraction (-)** | Dimensions must match | `T1 - T2` ✓, `U - p` ✗ |
| **Multiplication (*)** | Dimensions multiply | `rho * U` → `[kg m^-3][m s^-1]` |
| **Division (/)** | Dimensions divide | `mu / rho` → `[Pa s]/[kg m^-3]` |
| **Power (^)** | Dimension raises to power | `U^2` → `[m s^-1]^2` |

---

## Quick Reference

### Comparison Operators

| Need | Code | Result |
|------|------|--------|
| Positive mask | `pos(T - Tcrit)` | 1.0 where T > Tcrit, 0.0 elsewhere |
| Negative mask | `neg(T - Tcrit)` | 1.0 where T < Tcrit, 0.0 elsewhere |
| Combined mask | `pos(x - 0.3) * pos(0.7 - x)` | 1.0 in interval [0.3, 0.7] |

### Boundary Assignment

| Need | Code | Notes |
|------|------|-------|
| Find patch ID | `mesh.boundaryMesh().findPatchID("name")` | Returns label |
| Uniform value | `field.boundaryFieldRef()[patchI] == value` | Use `==` not `=` |
| Loop over faces | `forAll(patch, faceI) { ... }` | Iterate over boundary faces |
| Get face centers | `mesh.Cf().boundaryField()[patchI]` | For spatial profiles |

### Compound Assignment

| Operator | Operation | Equivalent | Notes |
|----------|-----------|------------|-------|
| `+=` | Add in-place | `T = T + source` | No temporary field |
| `-=` | Subtract in-place | `T = T - sink` | More efficient |
| `*=` | Multiply in-place | `T = T * factor` | Good for scaling |
| `/=` | Divide in-place | `T = T / divisor` | Good for normalization |

### Dimensional Checking

| Need | Code | Notes |
|------|------|-------|
| Define scalar | `dimensionedScalar("name", dims, value)` | Always specify dimensions |
| Get dimensions | `field.dimensions()` | Returns DimensionSet |
| Check consistency | Compiler enforces at compile-time | Catches dimensional errors |
| Common dimensions | `dimPressure`, `dimVelocity`, `dimDensity`, etc. | See `dimensions.H` |

---

## Key Takeaways

> [!SUCCESS] **🎯 Key Takeaways**
>
> **1. Comparison Operators (pos/neg)**
> - **`pos(condition)`**: Returns 1.0 where condition > 0, 0.0 elsewhere
> - **`neg(condition)`**: Returns 1.0 where condition < 0, 0.0 elsewhere
> - **Element-wise operations**: Work on entire fields at once (no loops needed)
> - **Use cases**: Conditional source terms, masking, interface detection
> - **Performance**: Vectorized operations are faster than if-statements
>
> **2. Boundary Assignment (==)**
> - **Special syntax**: Use `==` for boundary assignment, NOT `=`
> - **Access pattern**: `field.boundaryFieldRef()[patchI] == value`
> - **Patch identification**: `mesh.boundaryMesh().findPatchID("patchName")`
> - **Dynamic profiles**: Use with loops to create spatially/temporally varying BCs
> - **Type safety**: `==` ensures proper boundary condition handling
>
> **3. Compound Assignment Operators**
> - **Available**: `+=`, `-=`, `*=`, `/=` (in-place modifications)
> - **Memory efficiency**: No temporary fields created
> - **Performance**: Better cache locality than separate operations
> - **Use cases**: Accumulating sources, time integration, corrections
> - **Clean syntax**: More readable than `T = T + source`
>
> **4. Dimensional Checking**
> - **Automatic**: All operators check dimensional consistency
> - **Compile-time errors**: Catches dimensional mistakes early
> - **DimensionedScalar**: Always use for constants (not plain doubles)
> - **DimensionSet**: Units like `[kg m^-1 s^-2]` attached to every field
> - **Safety**: Prevents physically incorrect equations
>
> **5. Practical Applications**
> - **Custom solver development**: Conditional source terms, boundary profiles
> - **Function objects**: Runtime field manipulations
> - **Post-processing**: Masking, conditional analysis
> - **Turbulence modeling**: Wall damping, production term switching
> - **Multi-phase flows**: Interface detection, surface tension masking
>
> **6. Best Practices**
> - Use `pos()`/`neg()` for conditional field operations (not loops)
> - Always use `==` for boundary assignment (never `=`)
> - Prefer compound operators for in-place modifications
> - Define dimensioned scalars properly with units
> - Leverage dimensional checking to catch bugs early

---

## Concept Check

<details>
<summary><b>1. pos(T - Tcrit) คืนค่าอะไร?</b></summary>

**Returns a volScalarField with:**
- `1.0` where `T > Tcrit` (condition is positive)
- `0.0` where `T <= Tcrit` (condition is zero or negative)

💡 **Use case:** สร้าง mask สำหรับ conditional operations
</details>

<details>
<summary><b>2. == ที่ boundary ต่างจาก = อย่างไร?</b></summary>

**`==` (boundary assignment):**
- Special OpenFOAM syntax for boundary patches
- Calls `operator==()` for proper BC handling
- **✓ CORRECT**: `field.boundaryFieldRef()[patchI] == value;`

**`=` (standard assignment):**
- Standard C++ assignment operator
- May cause runtime errors on boundaries
- **❌ WRONG**: `field.boundaryFieldRef()[patchI] = value;`
</details>

<details>
<summary><b>3. T += source ดีกว่า T = T + source ทำไม?</b></summary>

**`+=` (compound assignment) เป็นพิเศษ:**
- **No temporary**: ไม่สร้าง temporary field สำหรับ `T + source`
- **In-place operation**: แก้ไขค่าโดยตรงใน memory เดิม
- **Better performance**: Cache locality ดีกว่า
- **Cleaner syntax**: อ่านง่ายและกระชับกว่า
</details>

<details>
<summary><b>4. operators ตรวจสอบ dimensions ไหม?</b></summary>

**ใช่! ทุก operators ใน OpenFOAM ตรวจสอบ dimensions:**
- **Compile-time checking**: Error ตั้งแต่ compile-time
- **Automatic reduction**: คูณ/หาร fields อัตโนมัติคำนวณ dimensions
- **Type safety**: ป้องกันการบวกกัน fields ที่ dimension ไม่ตรงกัน
- **Example**: `p + U` → ❌ COMPILER ERROR (pressure + velocity)
</details>

<details>
<summary><b>5. สร้าง spatially varying boundary condition อย่างไร?</b></summary>

**ใช้ `==` กับ loop ผ่าน boundary faces:**

```cpp
label patchI = mesh.boundaryMesh().findPatchID("inlet");
vectorField& Upatch = U.boundaryFieldRef()[patchI];
const vectorField& Cf = mesh.Cf().boundaryField()[patchI];

forAll(Upatch, faceI)
{
    scalar y = Cf[faceI].y();
    Upatch[faceI] == vector(parabolicProfile(y), 0, 0);
}
```
</details>

<details>
<summary><b>6. ใช้ dimensionedScalar อย่างไร?</b></summary>

**Define dimensionedScalar properly:**

```cpp
// Method 1: Direct constructor
dimensionedScalar rho
(
    "rho",           // Name
    dimDensity,      // Dimensions [kg m^-3]
    1.225            // Value
);

// Method 2: From dictionary
dimensionedScalar rho
(
    transportProperties.lookup("rho")
);

// Now you can use in operations
volScalarField p = 0.5 * rho * magSqr(U);  // ✓ Correct
```

❌ **WRONG**: `volScalarField p = 0.5 * 1.225 * magSqr(U);` // No dimensions!
</details>

<details>
<summary><b>7. pos กับ neg ต่างกันอย่างไร?</b></summary>

**`pos(condition)`:**
- Returns `1.0` where `condition > 0`
- Returns `0.0` where `condition <= 0`
- Example: `pos(T - 1000)` → 1.0 ที่ T > 1000 K

**`neg(condition)`:**
- Returns `1.0` where `condition < 0`
- Returns `0.0` where `condition >= 0`
- Example: `neg(T - 1000)` → 1.0 ที่ T < 1000 K

💡 **Note**: `pos(x) + neg(x)` ไม่จำเป็นต้องเท่ากับ 1.0 (เพราะที่ x = 0 ทั้งคู่เป็น 0.0)
</details>

<details>
<summary><b>8. สร้าง interface mask สำหรับ multiphase flow อย่างไร?</b></summary>

**ใช้ pos() สองครั้งเพื่อสร้าง interval:**

```cpp
volScalarField alpha = ...;  // Volume fraction field

// Interface region: 0.01 < alpha < 0.99
volScalarField interface = pos(alpha - 0.01) * pos(0.99 - alpha);

// ใช้ mask สำหรับ surface tension force
volVectorField Fst = sigma * fvc::grad(alpha) * interface;
```
</details>

---

## Related Documentation

- **Field Algebra Overview:** [[00_Overview.md]]
- **Dimensioned Types:** [[../02_DIMENSIONED_TYPES/00_Overview.md]]
- **Field Types:** [[../08_FIELD_TYPES/00_Overview.md]]
- **Mesh Classes:** [[../04_MESH_CLASSES/05_fvMesh.md]]
- **Linear Algebra:** [[../06_MATRICES_LINEARALGEBRA/00_Overview.md]]

---

> [!INFO] **🎯 Operator Overloading in the Big Picture**
>
> **Operator Overloading** เป็นสะพานเชื่อมระหว่างคณิตศาสตร์และการเขียนโปรแกรม:
>
> 1. **Coding Domain:** ใช้ใน custom solver, BCs, function objects
> 2. **Mathematical Domain:** แทนสมการฟิสิกส์ในรูปแบบที่ใกล้เคียงกับ notation คณิตศาสตร์
> 3. **Safety Domain:** Dimensional checking ผ่าน operators → error ตั้งแต่ compile-time
>
> **เส้นทางการเรียนรู้:**
> - เริ่มจาก [[00_Overview.md]] → ต่อด้วย operator overloading → ประยุกต์ใช้ใน custom solver
>
> **ไฟล์ที่เกี่ยวข้องใน OpenFOAM Case:**
> - `0/*`: Boundary conditions ใช้ `==` operator
> - `src/*`: Custom solvers ใช้ operators สำหรับ field algebra
> - `system/controlDict`: Function objects ใช้ operators สำหรับ runtime calculations
> - `Make/files`: Compiler ตรวจสอบ dimensional consistency ตั้งแต่ compile-time