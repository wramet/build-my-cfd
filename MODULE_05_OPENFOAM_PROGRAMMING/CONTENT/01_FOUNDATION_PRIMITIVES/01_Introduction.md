# Foundation Primitives - Introduction

บทนำ OpenFOAM Primitives — ทำไม OpenFOAM ถึงสร้าง types ใหม่?

---

## 🎯 Learning Objectives

หลังจากอ่านบทนี้ คุณจะสามารถ:

1. **อธิบาย** ทำไม OpenFOAM ไม่ใช้ C++ standard types ตรงๆ และข้อดีของ custom types
2. **แยกแยะ** ประเภทต่างๆ ของ OpenFOAM primitives (Basic, Mathematical, Dimensioned, Smart Pointers)
3. **เลือกใช้** type ที่เหมาะสมกับงาน CFD ที่ต้องการ
4. **ทำความเข้าใจ** หลักการของ operator overloading และ dimension checking
5. **ประเมิน** ความสำคัญของ memory management ใน CFD simulations

---

## Overview

### What: OpenFOAM's Custom Type System

OpenFOAM สร้าง type system ขึ้นมาใหม่ทั้งหมดแทนการใช้ C++ standard types:

- **Basic types:** `label`, `scalar`, `word` แทน `int`, `double`, `string`
- **Mathematical types:** `vector`, `tensor`, `symmTensor` สำหรับ CFD operations
- **Dimensioned types:** `dimensionedScalar`, `dimensionedVector` สำหรับ unit checking
- **Smart pointers:** `autoPtr`, `tmp` สำหรับ automatic memory management

### Why: Limitations of Standard C++ for CFD

> **💡 ปัญหาของ C++ ดั้งเดิมสำหรับ CFD:**
> - `double` ไม่รู้จักหน่วย (meter? Pascal? Kelvin?) → **Physics errors**
> - `std::vector` ไม่มี dot product, cross product → **Manual implementation**
> - Manual memory management → **Memory leaks**
> - No tensor operations → **Complex mathematical code**
> - No built-in field operations → **Inefficient computations**

**Why Custom Types Matter in CFD:**

1. **Dimension Consistency:** การบวก pressure กับ velocity ไม่ควร compile ผ่าน
   - เกิด bug: `p + U` → ผลลัพธ์ผิดทาง physics แต่โปรแกรมทำงานต่อ
   - OpenFOAM: จะ catch ตอน compile-time

2. **Mathematical Clarity:** Navier-Stokes equations ต้องการ vector/tensor operations
   - Stress tensor: `τ = μ(∇U + ∇Uᵀ)` ต้องการ tensor operations
   - Vorticity: `ω = ∇ × U` ต้องการ cross product
   - ถ้าใช้ arrays → โค้ดอ่านยาก และ error-prone

3. **Memory Safety:** Large meshes → millions of cells
   - Field operations สร้าง temporary objects จำนวนมาก
   - Manual cleanup → ลืม delete → memory leaks
   - OpenFOAM smart pointers → automatic garbage collection

4. **Performance Optimization:** Built-in operations
   - `sum(field)`, `max(field)`, `average(field)` optimized for OpenFOAM
   - Loop unrolling, SIMD instructions ใน built-in methods

**Real-World Consequences:**

```cpp
// ❌ Without dimension checking (standard C++)
double p = 1000;      // Pa
double rho = 1.2;     // kg/m³
double U = 10;        // m/s
double result = p + U;  // Compiles! But physics nonsense

// ✅ With dimension checking (OpenFOAM)
dimensionedScalar p("p", dimPressure, 1000);
dimensionedScalar rho("rho", dimDensity, 1.2);
dimensionedScalar U("U", dimVelocity, 10);
dimensionedScalar result = p + U;  // COMPILER ERROR!
```

### How: OpenFOAM's Solution Architecture

OpenFOAM แก้ปัญหาโดยการสร้าง **layered type system**:

```
Layer 1: Basic Primitives (label, scalar, word)
    ↓
Layer 2: Mathematical Types (vector, tensor, symmTensor)
    ↓
Layer 3: Dimensioned Types (dimensionedScalar, dimensionedVector)
    ↓
Layer 4: Field Types (volScalarField, volVectorField)
```

**Core Design Principles:**

1. **Operator Overloading:** เขียน math equations ตรงๆ ไม่ต้องเรียก functions
   ```cpp
   vector a(1, 2, 3);
   vector b(4, 5, 6);
   scalar dot = a & b;      // Dot product
   vector cross = a ^ b;    // Cross product
   ```

2. **Compile-Time Dimension Checking:** Validate units ตั้งแต่ compile
   ```cpp
   dimensionedScalar F = rho * sqr(U);  // Check: [M L^-3][L² T⁻²] = [M L⁻¹ T⁻²]
   ```

3. **Automatic Memory Management:** Smart pointers จัดการ lifetime
   ```cpp
   tmp<volScalarField> tgradP = fvc::grad(p);  // Auto-cleanup when done
   ```

---

## 1. Type Categories Overview

### Summary Table: OpenFOAM Type System

| Category | Types | Primary Purpose | Key Benefit |
|----------|-------|----------------|-------------|
| **Basic** | `label`, `scalar`, `word`, `Switch` | Foundational data types | Portability, validation |
| **Mathematical** | `vector`, `tensor`, `symmTensor`, `sphericalTensor` | 3D physics operations | Built-in vector/tensor math |
| **Dimensioned** | `dimensionedScalar`, `dimensionedVector` | Unit-aware quantities | Prevent physics errors |
| **Smart Pointers** | `autoPtr`, `tmp`, `refPtr` | Memory management | Prevent memory leaks |
| **Containers** | `List`, `Field`, `HashTable`, `PtrList` | Data structures | Efficient storage/access |
| **Fields** | `volScalarField`, `volVectorField`, `surfaceScalarField` | Mesh data | Mesh-aware operations |

---

### Basic Types

| Type | C++ Equivalent | Physics Purpose | ทำไมสร้างใหม่ |
|------|----------------|----------------|--------------|
| `label` | int/long | Cell indices, face indices | Portable 32/64-bit for large meshes |
| `scalar` | double | Temperature, pressure, density | Built-in CFD functions (sqr, mag, sign) |
| `word` | string | Field names, boundary names | Validated identifiers (no spaces) |
| `fileName` | string | File paths, case directories | Path operations, validation |
| `Switch` | bool | Solver control flags | Parse "yes/no/on/off/true/false" |

**Why `word` is Better than `string`:**

```cpp
word fieldName = "p";           // ✅ Valid
word badName = "p q";           // ❌ ERROR: spaces not allowed
word withSlash = "p/r";         // ❌ ERROR: slashes not allowed

// std::string wouldn't catch these → runtime bugs in dictionary parsing
```

### Mathematical Types

| Type | Components | Storage | Physics Applications | ทำไมต้องมี |
|------|------------|---------|---------------------|----------|
| `vector` | 3 (x, y, z) | 3 scalars | Velocity, force, position | Built-in dot, cross, mag |
| `tensor` | 9 (3×3) | 9 scalars | Stress, velocity gradient | Full matrix operations |
| `symmTensor` | 6 (unique) | 6 scalars | Symmetric stress, strain | 33% memory savings |
| `sphericalTensor` | 1 (diagonal) | 1 scalar | Isropic stress (pI) | Maximum compression |

**Physics Examples:**

```cpp
// Velocity field
vector U(10, 0, 0);           // m/s in x-direction

// Stress tensor (anisotropic)
tensor tau(1e5, 0, 0,         // Pa
           0, 5e4, 0,
           0, 0, 8e4);

// Symmetric stress (common in fluids)
symmTensor sigma(1e5, 0, 0,   // Only 6 unique components
                 5e4, 0, 
                 8e4);

// Isropic pressure
sphericalTensor pI(1e5);      // p on diagonal only
```

### Dimensioned Types

| Type | Components | Purpose | Example Application |
|------|-----------|---------|---------------------|
| `dimensionedScalar` | name + dimensions + value | Unit-aware scalars | Density, viscosity, pressure |
| `dimensionedVector` | name + dimensions + vector | Unit-aware vectors | Gravity, velocity |
| `dimensionedTensor` | name + dimensions + tensor | Unit-aware tensors | Permeability, conductivity |

**Dimension Checking in Action:**

```cpp
dimensionedScalar rho("rho", dimDensity, 1000);          // kg/m³
dimensionedVector g("g", dimAcceleration, vector(0,0,-9.81)); // m/s²

dimensionedVector bodyForce = rho * g;  // [M L⁻³][L T⁻²] = [M L⁻² T⁻²] ✅

// Cannot add incompatible dimensions:
// rho + g;  // COMPILER ERROR!
```

### Smart Pointers

| Type | Ownership Model | Use Case | Benefit |
|------|----------------|----------|---------|
| `autoPtr<T>` | Unique ownership | Created objects, factory returns | Automatic deletion |
| `tmp<T>`` | Reference counting | Temporary field expressions | Optimized evaluation |
| `refPtr<T>`` | Optional reference | Cached computations | Lazy evaluation |

**Why Smart Matters in CFD:**

```cpp
// Without smart pointers (C-style)
volScalarField* gradP = fvc::grad(p);
// ... use gradP
delete gradP;  // Easy to forget! → memory leak

// With autoPtr (OpenFOAM style)
autoPtr<volScalarField> gradPPtr = fvc::grad(p);
// ... use gradPPtr()
// Automatic deletion when gradPPtr goes out of scope
```

---

## 2. Quick Examples

### Basic Types in Practice

```cpp
label cellI = 0;              // Cell index (mesh can have millions)
scalar T = 300.0;             // Temperature in Kelvin
word fieldName = "p";         // Pressure field name
fileName casePath = "~/cases/airFoil";  // Case directory
Switch turbulence("yes");     // Read from dictionary
```

### Vector Operations for CFD

```cpp
vector U(1.0, 0.0, 0.0);           // Velocity vector [m/s]
vector n(0, 1.0, 0);               // Normal vector

scalar speed = mag(U);             // Magnitude: 1.0 m/s
vector normalized = U / mag(U);    // Unit vector (direction only)

scalar kineticEnergy = 0.5 * magSqr(U);  // |U|² = 1.0 m²/s²

// Cross product: vorticity calculation
vector omega = U ^ n;              // ω = U × n
```

### Dimensioned Types with Unit Checking

```cpp
// Define properties with dimensions
dimensionedScalar rho("rho", dimDensity, 1000);         // kg/m³
dimensionedScalar nu("nu", dimKinematicViscosity, 1e-6); // m²/s
dimensionedVector g("g", dimAcceleration, vector(0, 0, -9.81)); // m/s²

// Dimensionally consistent operations
dimensionedScalar Re = mag(U) * length / nu;  // Reynolds number [L T⁻¹][L]/[L² T⁻¹] = [-] ✅

dimensionedVector F = rho * sqr(U) * area;     // Force [M L⁻³][L² T⁻²][L²] = [M L T⁻²] ✅

// Dimension mismatch caught at compile time
// rho + nu;  // ERROR: Cannot add density + viscosity
```

### Smart Pointers in Action

```cpp
// Factory function returns autoPtr
autoPtr<boundaryCondition> bc = boundaryCondition::New("fixedValue");

// Temporary field expression (tmp optimizes evaluation)
tmp<volScalarField> tgradP = fvc::grad(p);
volScalarField& gradP = tgradP.ref();  // Use reference

// Automatic cleanup when out of scope
```

---

## 3. Key Features

### Operator Overloading

> **Why It Matters:** เขียน math equations ได้ตรง ๆ ไม่ต้องเรียก functions → โค้ดอ่านง่าย และ in-line กับสมการ physics

```cpp
vector a(1, 2, 3);
vector b(4, 5, 6);

scalar dot = a & b;      // Dot product: 32
vector cross = a ^ b;    // Cross product: (-3, 6, -3)
vector sum = a + b;      // Element-wise: (5, 7, 9)
vector diff = a - b;     // Element-wise: (-3, -3, -3)
scalar mag_a = mag(a);   // Magnitude: √14 ≈ 3.74
```

**⚠️ Common Pitfall: Operators ไม่เหมือน C++ ปกติ**
- `&` = dot product (ไม่ใช่ bitwise AND)
- `^` = cross product (ไม่ใช่ XOR)
- `*` = scalar multiplication or tensor inner product (context-dependent)

```cpp
// Confusing example
vector c = a & b;  // ERROR: & returns scalar, cannot assign to vector
scalar d = a ^ b;  // ERROR: ^ returns vector, cannot assign to scalar
```

### Dimension Checking

> **Why It Matters:** Prevent physics errors ที่ compiler จะ catch ได้

```cpp
dimensionedScalar p("p", dimPressure, 1000);   // Pa [M L⁻¹ T⁻²]
dimensionedScalar rho("rho", dimDensity, 1.2); // kg/m³ [M L⁻³]
dimensionedScalar U("U", dimVelocity, 10);     // m/s [L T⁻¹]

// ✅ Valid: Dynamic pressure calculation
dimensionedScalar dynP = 0.5 * rho * sqr(U);  
// Dimensions: [M L⁻³] × [L² T⁻²] = [M L⁻¹ T⁻²] = Pressure ✅

// ❌ Invalid: Cannot add pressure + velocity
// dimensionedScalar wrong = p + U;  
// COMPILER ERROR: Cannot add [M L⁻¹ T⁻²] + [L T⁻¹]
```

**Dimension Set Reference:**

| Quantity | Symbol | Dimension |
|----------|--------|-----------|
| Mass | M | [M] |
| Length | L | [L] |
| Time | T | [T] |
| Temperature | Θ | [Θ] |
| Pressure | p | [M L⁻¹ T⁻²] |
| Density | ρ | [M L⁻³] |
| Velocity | U | [L T⁻¹] |
| Kinematic Viscosity | ν | [L² T⁻¹] |
| Dynamic Viscosity | μ | [M L⁻¹ T⁻¹] |

### Automatic Memory Management

```cpp
// Problem: Manual memory management
volScalarField* gradP = new volScalarField(fvc::grad(p));
// ... complex code ...
delete gradP;  // Easy to forget or skip on exception

// Solution: Smart pointers
autoPtr<volScalarField> gradPPtr(fvc::grad(p).ptr());
// Automatic deletion when gradPPtr goes out of scope
```

---

## 4. Type Selection Guide

### Decision Tree: Which Type Should I Use?

```
Need to store a value?
│
├─ Is it a mesh index (cell, face, point)?
│  └─ Use → label
│
├─ Is it a physical quantity with units?
│  ├─ Scalar value (pressure, temperature)?
│  │  └─ Use → dimensionedScalar
│  │
│  └─ Vector/tensor (velocity, stress)?
│     └─ Use → dimensionedVector / dimensionedTensor
│
├─ Is it a name/identifier?
│  └─ Use → word
│
├─ Is it a boolean flag read from dictionary?
│  └─ Use → Switch
│
└─ Is it a temporary calculation result?
   └─ Use → tmp<T>
```

### Quick Reference Table

| Need | Type | Example |
|------|------|---------|
| Cell/face index | `label` | `label cellI = 0;` |
| Physical value (no units) | `scalar` | `scalar pi = 3.14159;` |
| Physical value (with units) | `dimensionedScalar` | `dimensionedScalar rho("rho", dimDensity, 1000);` |
| Velocity/force vector | `vector` | `vector U(10, 0, 0);` |
| Velocity with units | `dimensionedVector` | `dimensionedVector g("g", dimAcceleration, vector(0,0,-9.81));` |
| Stress/strain tensor | `symmTensor` | `symmTensor tau(...);` |
| Field name | `word` | `word fieldName = "p";` |
| File path | `fileName` | `fileName meshPath = "constant/polyMesh";` |
| Yes/No from dict | `Switch` | `Switch debug("on");` |
| Owned pointer | `autoPtr<T>` | `autoPtr<initialConditions> icPtr;` |
| Temporary field | `tmp<volScalarField>` | `tmp<volScalarField> tgradP = fvc::grad(p);` |
| List of values | `List<scalar>` | `List<scalar> xCoords(nCells);` |
| Field on mesh | `volScalarField` | `volScalarField p(mesh);` |

---

## 5. Module Structure

### Learning Path

| File | Topic | Prerequisites | Why Read This |
|------|-------|--------------|---------------|
| **02_Basic_Primitives** | `scalar`, `vector`, `tensor` detailed usage | This file | Foundation for all OpenFOAM code |
| **03_Dimensioned_Types_Intro** | `dimensionedScalar`, dimension checking | 02 | Prevent unit errors in simulations |
| **04_Smart_Pointers** | `autoPtr`, `tmp`, memory management | 02 | Write leak-free code |
| **05_Containers** | `List`, `HashTable`, `Field` | 02, 04 | Store and manipulate data efficiently |
| **06_Summary** | Quick reference | All | Review and lookup |
| **07_Exercises** | Practice problems | All | Solidify understanding |

### Cross-Module Connections

- **Governing Equations:** Dimensioned types enforce dimensional consistency in Navier-Stokes
- **Boundary Conditions:** Smart pointers manage BC lifetime
- **Turbulence Models:** Mathematical types essential for Reynolds stress modeling
- **Parallel Processing:** Containers (Field, List) handle distributed data

---

## 6. Common Pitfalls

### ⚠️ Pitfall 1: Using `double` Instead of `scalar`

```cpp
// ❌ Wrong
double value = 4.0;
double squared = sqr(value);  // May not work! sqr() is OpenFOAM function

// ✅ Correct
scalar value = 4.0;
scalar squared = sqr(value);  // Works: 16
```

**Why:** `scalar` has built-in CFD functions (`sqr`, `mag`, `sign`, `pos`, `neg`)

### ⚠️ Pitfall 2: Mixing C++ Arrays with OpenFOAM

```cpp
// ❌ Wrong: Manual vector math
double a[3] = {1, 2, 3};
double b[3] = {4, 5, 6};
double dot = a[0]*b[0] + a[1]*b[1] + a[2]*b[2];  // Error-prone

// ✅ Correct: Use OpenFOAM vector
vector a(1, 2, 3);
vector b(4, 5, 6);
scalar dot = a & b;  // Clear and correct
```

### ⚠️ Pitfall 3: Forgetting Dimension Checking

```cpp
// ❌ Wrong: Unit errors slip through
scalar p = 1000;  // Assume Pa (but not enforced!)
scalar U = 10;    // Assume m/s
scalar result = p + U;  // Compiles! But physics nonsense

// ✅ Correct: Enforce dimensions
dimensionedScalar p("p", dimPressure, 1000);
dimensionedScalar U("U", dimVelocity, 10);
// dimensionedScalar result = p + U;  // COMPILER ERROR ✅
```

### ⚠️ Pitfall 4: Operator Confusion

```cpp
vector a(1, 2, 3);
vector b(4, 5, 6);

// ❌ Wrong: C++ habits
scalar dot = a * b;        // ERROR: * is not dot product for vectors
vector cross = a % b;      // ERROR: % is not cross product

// ✅ Correct: OpenFOAM operators
scalar dot = a & b;        // Dot product
vector cross = a ^ b;      // Cross product
```

### ⚠️ Pitfall 5: Memory Leaks with Raw Pointers

```cpp
// ❌ Wrong: Manual management
volScalarField* gradP = new volScalarField(fvc::grad(p));
// ... if exception thrown before delete ...
delete gradP;  // Never reached → memory leak

// ✅ Correct: Smart pointer
autoPtr<volScalarField> gradPPtr(fvc::grad(p).ptr());
// Automatic cleanup even if exception thrown
```

---

## 🧠 Concept Check

<details>
<summary><b>1. ทำไม OpenFOAM ใช้ label แทน int?</b></summary>

**Portability Across Mesh Sizes:**

- `label` เป็น typedef ที่ compile เป็น 32-bit หรือ 64-bit ขึ้นกับ configuration
- Small meshes (<2 billion cells): `label` = 32-bit int → ประหยั� memory
- Large meshes (>2 billion cells): `label` = 64-bit long → รองรับ meshes ขนาดใหญ่
- Code ไม่ต้องเปลี่ยน: OpenFOAM จัดการให้อัตโนมัติ

```cpp
label nCells = mesh.nCells();  // Works for any mesh size
// If using int: fails on meshes with >2B cells
```

**Why Not Use `size_t`?**
- `size_t` ไม่มี signed/unsigned consistency
- `label` เป็น signed → ใช้เป็น index ได้ และ เช็ค negative values ได้
</details>

<details>
<summary><b>2. scalar กับ double ต่างกันอย่างไร?</b></summary>

**scalar = double + OpenFOAM CFD Functions:**

```cpp
scalar x = 4.0;
scalar y = sqr(x);      // 16 (OpenFOAM-specific function)
scalar z = sign(x);     // 1 (Returns -1, 0, or 1)
scalar m = mag(x);      // 4 (Magnitude: works on scalar too)
scalar p = pos(x);      // 1 (Positive part: max(0, x))
scalar n = neg(-2.0);   // 2 (Negative part: max(0, -x))

// double ไม่มี functions เหล่านี้โดยตรง
double dx = 4.0;
// double dy = sqr(dx);  // May not work unless sqr() in scope
```

**When to Use Each:**
- Use `scalar` for: CFD calculations, field data, physical quantities
- Use `double` for: Pure numeric algorithms, temporary intermediate values
</details>

<details>
<summary><b>3. dimensionedScalar ดีกว่า scalar อย่างไร?</b></summary>

**Unit Tracking ป้องกัน Physics Errors:**

```cpp
// Without dimensions (scalar)
scalar p = 1000;  // Assume Pa (but not enforced!)
scalar L = 1.0;   // Assume m (but not enforced!)
scalar result = p / L;  // 1000 (What are the units?)

// With dimensions (dimensionedScalar)
dimensionedScalar p("p", dimPressure, 1000);    // Pa
dimensionedScalar L("L", dimLength, 1.0);       // m
dimensionedScalar result = p / L;  // [Pa/m] = [M L⁻² T⁻²]
// result.name() = "p/L"
// result.dimensions() = [M L⁻² T⁻²]
// result.value() = 1000
```

**Compile-Time Protection:**

```cpp
dimensionedScalar p("p", dimPressure, 1000);
dimensionedScalar L("L", dimLength, 1.0);

// p + L;  // COMPILER ERROR!
// Cannot add [M L⁻¹ T⁻²] + [L]
// Catches bugs before simulation runs
```

**When to Use Each:**
- Use `dimensionedScalar` for: Physical properties, constants, dictionary inputs
- Use `scalar` for: Dimensionless numbers, intermediate calculations, mesh indices
</details>

<details>
<summary><b>4. ทำไมใช้ & และ ^ สำหรับ dot/cross product?</b></summary>

**Historical Reasons + Clarity:**

1. **C++ Operator Limitations:** `*` already used for scalar multiplication
2. **Visual Distinction:** `&` และ `^` ดูต่างจาก arithmetic operators
3. **Operator Precedence:** Works correctly in complex expressions

```cpp
vector a(1, 2, 3);
vector b(4, 5, 6);

// Dot product: &
scalar dot = a & b;  // 32

// Cross product: ^
vector cross = a ^ b;  // (-3, 6, -3)

// Complex expressions
scalar result = (a & b) + mag(cross);  // Works as expected
```

**Common Mistake:** Confusing with C++ bitwise operators
```cpp
// ❌ Not bitwise AND or XOR
scalar x = 5 & 3;      // In C++: bitwise AND = 1
scalar y = 5 ^ 3;      // In C++: bitwise XOR = 6

// ✅ In OpenFOAM (with vectors)
vector v1(5, 0, 0);
vector v2(3, 0, 0);
scalar z = v1 & v2;    // Dot product = 15
```

**Best Practice:** Always remember: for OpenFOAM vectors, `&` = dot, `^` = cross
</details>

<details>
<summary><b>5. symmTensor ประหยัด memory อย่างไร?</b></summary>

**Symmetry Property: τ_ij = τ_ji**

Full tensor (9 components):
```
| τ_xx  τ_xy  τ_xz |
| τ_xy  τ_yy  τ_yz |  (6 unique + 3 redundant)
| τ_xz  τ_yz  τ_zz |
```

Symmetric tensor (6 components only):
```
| τ_xx  τ_xy  τ_xz |
| τ_xy  τ_yy  τ_yz |  (stored as: xx, xy, xz, yy, yz, zz)
| τ_xz  τ_yz  τ_zz |
```

**Memory Savings:**
- `tensor`: 9 scalars × 8 bytes = 72 bytes
- `symmTensor`: 6 scalars × 8 bytes = 48 bytes
- **Savings: 33% reduction**

**Physics Justification:**
Most fluid stress tensors are symmetric:
- Viscous stress: `τ = μ(∇U + ∇Uᵀ)` → symmetric by construction
- Reynolds stress: `R = ⟨u'u'⟩` → symmetric
- Strain rate: `S = ½(∇U + ∇Uᵀ)` → symmetric

**When to Use Each:**
```cpp
// Use symmTensor for: Stress, strain, Reynolds stress
symmTensor tau(1e5, 0, 0, 5e4, 0, 8e4);  // 6 components

// Use tensor for: Full velocity gradient, rotation matrices
tensor gradU(1, 2, 3, 4, 5, 6, 7, 8, 9);  // 9 components
```

**Performance Impact:**
- Less memory → better cache utilization
- Fewer operations (avoid redundant calculations)
- Typical OpenFOAM case: ~10-20% faster for symmetric operations
</details>

---

## 🎯 Key Takeaways

### Core Concepts

1. **OpenFOAM ไม่ใช้ C++ types ตรงๆ**
   - ปัญหา: `double` ไม่รู้จักหน่วย, `std::vector` ไม่มี vector operations
   - วิธีแก้: สร้าง type system ที่ "รู้จัก CFD"

2. **Type Categories**
   - **Basic:** `label`, `scalar`, `word` → portable และ validated
   - **Mathematical:** `vector`, `tensor`, `symmTensor` → built-in operations
   - **Dimensioned:** `dimensionedScalar` → unit checking
   - **Smart Pointers:** `autoPtr`, `tmp` → automatic memory management

3. **Dimension Checking ป้องกัน Physics Errors**
   - Catch bugs ตอน compile-time ไม่ใช่ runtime
   - Example: `p + U` จะ error ทันที (pressure + velocity ไม่ได้)

4. **Operator Overloading ทำให้โค้ดอ่านง่าย**
   - `&` = dot product, `^` = cross product
   - Math equations เขียนตรงๆ ไม่ต้องเรียก functions

5. **Memory Management อัตโนมัติ**
   - Smart pointers → ป้องกัน memory leaks
   - สำคัญสำหรับ large meshes (millions of cells)

### Selection Rules

| Need | Use |
|------|-----|
| Mesh index | `label` |
| Physical value (no units) | `scalar` |
| Physical value (with units) | `dimensionedScalar` |
| Vector quantity | `vector` / `dimensionedVector` |
| Stress/strain | `symmTensor` |
| Owned object | `autoPtr<T>` |
| Temporary calculation | `tmp<T>` |

### What's Next

- **Next:** [02_Basic_Primitives.md](02_Basic_Primitives.md) — Deep dive into `scalar`, `vector`, `tensor`
- **Then:** [03_Dimensioned_Types_Intro.md](03_Dimensioned_Types_Intro.md) — How unit checking works

---

## 📖 Related Documentation

- **Overview:** [00_Overview.md](00_Overview.md) — Module roadmap and prerequisites
- **Next:** [02_Basic_Primitives.md](02_Basic_Primitives.md) — Detailed coverage of basic types
- **Dimensioned Types:** [03_Dimensioned_Types_Intro.md](03_Dimensioned_Types_Intro.md) — Unit system and checking
- **Smart Pointers:** [04_Smart_Pointers.md](04_Smart_Pointers.md) — Memory management in depth
- **Reference:** [06_Summary.md](06_Summary.md) — Quick lookup guide
- **Practice:** [07_Exercises.md](07_Exercises.md) — Test your understanding