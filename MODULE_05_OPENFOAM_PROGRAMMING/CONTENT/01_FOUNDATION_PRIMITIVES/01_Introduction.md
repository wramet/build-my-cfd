# Foundation Primitives - Introduction

บทนำ OpenFOAM Primitives — ทำไม OpenFOAM ถึงสร้าง types ใหม่?

> **ทำไมต้องเรียนบทนี้?**
> - เข้าใจว่า **ทำไม OpenFOAM ไม่ใช้ C++ types ตรงๆ**
> - รู้จัก type categories ก่อนลงรายละเอียด
> - พร้อมสำหรับบทถัดไป

---

## Overview

> **💡 ปัญหาของ C++ ดั้งเดิมสำหรับ CFD:**
> - `double` ไม่รู้จักหน่วย (meter? Pascal? Kelvin?)
> - `std::vector` ไม่มี dot product, cross product
> - Manual memory management → memory leaks

**OpenFOAM แก้ปัญหาโดย:**
- สร้าง types ที่ **"รู้จัก CFD"**
- ใส่ dimension checking
- จัดการ memory อัตโนมัติ

---

## 1. Why Custom Types?

| ปัญหา C++ | Solution ใน OpenFOAM | ประโยชน์ |
|-----------|---------------------|---------|
| Units confusion | `dimensionedScalar` | ป้องกัน physics errors |
| No 3D vectors | `vector` class | Built-in dot, cross, mag |
| No tensors | `tensor`, `symmTensor` | Stress, strain operations |
| Memory leaks | `autoPtr`, `tmp` | Automatic cleanup |
| No CFD operations | Built-in methods | max, sum, average |

---

## 2. Type Categories

### Basic Types

| Type | C++ Equivalent | ทำไมสร้างใหม่ |
|------|----------------|--------------|
| `label` | int/long | Portable 32/64-bit |
| `scalar` | double | มี sqr, mag, sign |
| `word` | string | Validated names |
| `fileName` | string | Path operations |
| `Switch` | bool | Parse "yes/no/on/off" |

**ตัวอย่างว่าทำไม `word` ดีกว่า `string`:**
```cpp
word fieldName = "p";     // OK
word badName = "p q";     // ERROR: spaces not allowed
// std::string wouldn't catch this
```

### Mathematical Types

| Type | Components | ทำไมต้องมี |
|------|------------|----------|
| `vector` | 3 | Velocity, force — ต้องการ dot/cross |
| `tensor` | 9 | Stress, gradient — 3x3 matrix |
| `symmTensor` | 6 | Symmetric → ประหยัด 33% memory |
| `sphericalTensor` | 1 | pI — isotropic part |

### Dimensioned Types

| Type | ประกอบด้วย | Purpose |
|------|-----------|---------|
| `dimensionedScalar` | name + units + value | Unit checking |
| `dimensionedVector` | name + units + vector | Unit checking |
| `dimensionedTensor` | name + units + tensor | Unit checking |

---

## 3. Quick Examples

### Basic Types
```cpp
label cellI = 0;          // Index (integer)
scalar T = 300.0;         // Temperature (double)
word fieldName = "p";     // Name (validated string)
Switch active("yes");     // Boolean from string
```

### Vector Operations
```cpp
vector U(1.0, 0.0, 0.0);           // Create
scalar speed = mag(U);             // Magnitude: 1.0
vector normalized = U / mag(U);    // Unit vector
```

### Dimensioned Types
```cpp
dimensionedScalar rho("rho", dimDensity, 1000);
dimensionedVector g("g", dimAcceleration, vector(0, 0, -9.81));

// Dimension checking
dimensionedScalar F = rho * g;  // [M L^-3] * [L T^-2] = [M L^-2 T^-2]
```

---

## 4. Key Features

### Operator Overloading

> **ทำไมสำคัญ?**
> เขียน math equations ได้ตรง ๆ ไม่ต้องเรียก functions

```cpp
vector a(1, 2, 3);
vector b(4, 5, 6);

scalar dot = a & b;      // Dot product = 32
vector cross = a ^ b;    // Cross product = (-3, 6, -3)
vector sum = a + b;      // (5, 7, 9)
scalar mag_a = mag(a);   // √14
```

**⚠️ ระวัง: Operators ไม่เหมือน C++ ปกติ**
- `&` = dot product (ไม่ใช่ bitwise AND)
- `^` = cross product (ไม่ใช่ XOR)

### Dimension Checking

```cpp
dimensionedScalar p("p", dimPressure, 1000);   // Pa
dimensionedScalar rho("rho", dimDensity, 1.2); // kg/m³
dimensionedScalar U("U", dimVelocity, 10);     // m/s

// ✅ Valid: dimensions work out
dimensionedScalar dynP = 0.5 * rho * sqr(U);  // [Pa]

// ❌ Invalid: dimension mismatch
// p + U;  // Error at compile/runtime!
```

---

## 5. Module Contents

| File | Topic | ทำไมต้องอ่าน |
|------|-------|-------------|
| 02_Basic_Primitives | scalar, vector, tensor | Foundation for everything |
| 03_Dimensioned_Types_Intro | dimensionedScalar/Vector | ป้องกัน unit errors |
| 04_Smart_Pointers | autoPtr, tmp, PtrList | ป้องกัน memory leaks |
| 05_Containers | List, HashTable, Field | Data structures |
| 06_Summary | Quick reference | Review |
| 07_Exercises | Practice problems | Solidify knowledge |

---

## Quick Reference

| Need | Type | Example |
|------|------|---------|
| Index | `label` | `cellI = 0` |
| Value | `scalar` | `T = 300.0` |
| Velocity | `vector` | `U(1, 0, 0)` |
| Stress | `tensor` | `tau(...)` |
| With units | `dimensioned*` | `dimDensity` |
| Memory managed | `autoPtr`, `tmp` | `fvc::grad(p)` |

---

## 🧠 Concept Check

<details>
<summary><b>1. ทำไมใช้ label แทน int?</b></summary>

**Portability:**
- `label` = typedef ที่ compile เป็น 32 หรือ 64 bit
- Large meshes (>2B cells) ต้องการ 64-bit
- OpenFOAM จัดการให้อัตโนมัติ
</details>

<details>
<summary><b>2. scalar กับ double ต่างกันอย่างไร?</b></summary>

**scalar = double + CFD functions:**
```cpp
scalar x = 4.0;
scalar y = sqr(x);      // 16 (OpenFOAM function)
scalar z = sign(x);     // 1 (OpenFOAM function)
scalar m = mag(x);      // 4 (works on scalar too)
```

double ไม่มี functions เหล่านี้โดยตรง
</details>

<details>
<summary><b>3. dimensionedScalar ดีกว่า scalar อย่างไร?</b></summary>

**Unit tracking ป้องกัน errors:**
```cpp
dimensionedScalar p("p", dimPressure, 1000);
dimensionedScalar L("L", dimLength, 1);

// p / L → [Pa/m] = [M L^-2 T^-2]
// OpenFOAM tracks this automatically

// p + L → ERROR! Cannot add pressure + length
```

Scalar ไม่รู้จักหน่วย → bugs ที่ซ่อน
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **บทถัดไป:** [02_Basic_Primitives.md](02_Basic_Primitives.md) — scalar, vector, tensor
- **Dimensioned Types:** [03_Dimensioned_Types_Intro.md](03_Dimensioned_Types_Intro.md)