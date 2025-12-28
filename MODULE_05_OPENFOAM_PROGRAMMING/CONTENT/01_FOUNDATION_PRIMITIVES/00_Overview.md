# Foundation Primitives - Overview

ภาพรวม OpenFOAM Primitives — Building blocks สำหรับ CFD programming

> **ทำไม Primitives สำคัญ?**
> - **ทุกอย่างใน OpenFOAM สร้างจาก primitives เหล่านี้** — Fields, Matrices, BCs
> - เข้าใจ primitives = อ่าน/แก้ไข OpenFOAM source code ได้
> - ใช้ผิด type = bugs ที่หายาก (แม้ compile ผ่าน)

---

## Overview

> **💡 คิดแบบนี้:**
> OpenFOAM Primitives = **LEGO blocks สำหรับ CFD**
> 
> - `scalar`, `vector`, `tensor` = รูปทรงพื้นฐาน
> - `dimensionedScalar` = LEGO ที่มี label บอกขนาด
> - `autoPtr`, `tmp` = กล่องเก็บ LEGO อัตโนมัติ

```mermaid
flowchart TD
    A[Primitives] --> B[Basic Types]
    A --> C[Mathematical Types]
    A --> D[Dimensioned Types]
    A --> E[Smart Pointers]
    A --> F[Containers]
    
    B --> B1[label, scalar, word]
    C --> C1[vector, tensor]
    D --> D1[dimensionedScalar]
    E --> E1[autoPtr, tmp]
    F --> F1[List, Field]
```

---

## 1. Basic Types

| Type | ใช้เมื่อ | ทำไมไม่ใช้ C++ ตรงๆ |
|------|---------|-------------------|
| `label` | Cell/face indices | Portable 32/64-bit |
| `scalar` | Temperature, pressure | มี CFD functions (mag, sqr) |
| `word` | Field names | มี validation + operations |
| `fileName` | File paths | Path operations built-in |
| `Switch` | Solver options | รองรับ "yes/no/on/off" |

**ตัวอย่าง:**
```cpp
label cellI = 0;       // Cell index
scalar T = 300.0;      // Temperature
word fieldName = "p";  // Field name
```

---

## 2. Mathematical Types

| Type | Rank | Components | ใช้สำหรับ | Physics |
|------|------|------------|----------|---------|
| `scalar` | 0 | 1 | p, T, k | ค่าเดี่ยว |
| `vector` | 1 | 3 | U, F | ทิศทาง + magnitude |
| `tensor` | 2 | 9 | σ, ∇U | Transformation |
| `symmTensor` | 2 | 6 | R (Reynolds stress) | Symmetric ประหยัด memory |
| `sphericalTensor` | 2 | 1 | pI | Isotropic part |

> **ทำไมมีหลาย tensor types?**
> - `tensor` (9) → เก็บครบ เช่น velocity gradient
> - `symmTensor` (6) → ประหยัด 33% เมื่อ symmetric
> - `sphericalTensor` (1) → pressure part เท่านั้น

---

## 3. Dimensioned Types

> **ทำไม dimensioned types สำคัญมาก?**
> - **ป้องกัน physics errors ที่ compiler จับไม่ได้**
> - บวก pressure + velocity → Error! (ไม่ใช่ bug ที่ซ่อน)

```cpp
// Scalar with units
dimensionedScalar rho("rho", dimDensity, 1000);  // 1000 kg/m³

// Vector with units
dimensionedVector g("g", dimAcceleration, vector(0, 0, -9.81));
```

### Dimension Checking

```cpp
// ✅ Valid: dimensions match
volScalarField dynP = 0.5 * rho * magSqr(U);  // [M L^-1 T^-2]

// ❌ Invalid: dimension error (won't compile/run)
// p + U;  // Error! Cannot add pressure + velocity
```

---

## 4. Smart Pointers

> **ทำไมต้องใช้ smart pointers?**
> - **ป้องกัน memory leaks** — delete อัตโนมัติ
> - CFD ใช้ memory มาก → leak = crash

| Type | ใช้เมื่อ | ตัวอย่าง |
|------|---------|---------|
| `autoPtr` | Unique ownership (1 เจ้าของ) | Factory pattern |
| `tmp` | Temporary results | `fvc::grad(p)` |
| `PtrList` | List of pointers | Collection of BCs |

```cpp
// tmp example: fvc:: returns tmp
tmp<volVectorField> tGradP = fvc::grad(p);
volVectorField gradP = tGradP();  // Access value
// tGradP auto-deleted when out of scope
```

---

## 5. Containers

| Container | ใช้เมื่อ | ต่างจาก std::vector อย่างไร |
|-----------|---------|---------------------------|
| `List<T>` | Dynamic array | OpenFOAM I/O compatible |
| `Field<T>` | Arrays with CFD ops | มี max(), sum(), average() |
| `HashTable` | Key-value map | Case-insensitive keys |
| `DynamicList` | Growable list | Pre-allocated growth |

**Field vs List:**
```cpp
Field<scalar> T(100, 300.0);

// Field has CFD operations
scalar Tmax = max(T);
scalar Tavg = average(T);
scalar Tsum = sum(T);

// List doesn't have these
```

---

## 6. Learning Path

```mermaid
flowchart LR
    A[01_Introduction] --> B[02_Basic_Primitives]
    B --> C[03_Dimensioned_Types]
    C --> D[04_Smart_Pointers]
    D --> E[05_Containers]
    E --> F[07_Exercises]
```

**แนะนำ:** อ่านตามลำดับ เพราะแต่ละบทสร้างบนความรู้ก่อนหน้า

---

## Quick Reference

| Need | Use | ทำไม |
|------|-----|------|
| Index | `label` | Portable integer |
| Value | `scalar` | CFD math functions |
| 3D direction | `vector` | Built-in dot/cross |
| With units | `dimensionedScalar` | Dimension checking |
| Temporary result | `tmp<T>` | Auto memory management |
| Array with ops | `Field<T>` | max/sum/average |

---

## 🧠 Concept Check

<details>
<summary><b>1. ทำไมต้องใช้ dimensioned types?</b></summary>

**ตรวจสอบหน่วยอัตโนมัติ:**
- Compile-time: ตรวจบาง operations
- Run-time: ตรวจทุก operation

**ตัวอย่าง:**
```cpp
dimensionedScalar p("p", dimPressure, 1000);
dimensionedScalar U("U", dimVelocity, 10);
// p + U → ERROR! Dimension mismatch
```

ป้องกัน physics errors ที่ compiler จับไม่ได้
</details>

<details>
<summary><b>2. autoPtr vs tmp ใช้เมื่อไหร่?</b></summary>

| | autoPtr | tmp |
|-|---------|-----|
| Ownership | Unique (1 เจ้าของ) | Reference counted |
| ใช้กับ | Factory objects | Temporary calculations |
| ตัวอย่าง | `autoPtr<turbulenceModel>` | `tmp<volVectorField>` |

**กฎ:**
- Factory return → `autoPtr`
- `fvc::`/`fvm::` return → `tmp`
</details>

<details>
<summary><b>3. Field กับ List ต่างกันอย่างไร?</b></summary>

| | List | Field |
|-|------|-------|
| CFD operations | ❌ | ✅ max, sum, average |
| Math operations | ❌ | ✅ +, -, *, / |
| Memory | Same | Same |

**กฎ:** ถ้าต้องการ CFD math → ใช้ `Field`
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **บทถัดไป:** [01_Introduction.md](01_Introduction.md) — รายละเอียดเพิ่มเติม
- **Basic Primitives:** [02_Basic_Primitives.md](02_Basic_Primitives.md)
- **Dimensioned Types:** [03_Dimensioned_Types_Intro.md](03_Dimensioned_Types_Intro.md)
- **Smart Pointers:** [04_Smart_Pointers.md](04_Smart_Pointers.md)