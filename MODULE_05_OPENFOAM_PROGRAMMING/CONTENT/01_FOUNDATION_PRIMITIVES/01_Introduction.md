# Foundation Primitives - Introduction

บทนำ OpenFOAM Primitives

---

## Overview

> **OpenFOAM Primitives** = พื้นฐาน C++ types ที่ออกแบบสำหรับ CFD

---

## 1. Why Custom Types?

| Need | Solution |
|------|----------|
| Physical units | `dimensionedScalar` |
| 3D vectors | `vector` class |
| Tensors | `tensor`, `symmTensor` |
| Memory safety | `autoPtr`, `tmp` |
| CFD operations | Built-in methods |

---

## 2. Type Categories

### Basic Types

| Type | C++ Equivalent | Use |
|------|----------------|-----|
| `label` | int/long | Indices |
| `scalar` | double | Values |
| `word` | string | Names |
| `fileName` | string | Paths |
| `Switch` | bool | Flags |

### Mathematical Types

| Type | Components | Use |
|------|------------|-----|
| `vector` | 3 | Velocity, force |
| `tensor` | 9 | Stress, gradient |
| `symmTensor` | 6 | Symmetric tensors |
| `sphericalTensor` | 1 | Isotropic tensors |

### Dimensioned Types

| Type | Purpose |
|------|---------|
| `dimensionedScalar` | Scalar with units |
| `dimensionedVector` | Vector with units |
| `dimensionedTensor` | Tensor with units |

---

## 3. Quick Examples

### Basic

```cpp
label cellI = 0;
scalar T = 300.0;
word fieldName = "p";
```

### Vector

```cpp
vector U(1.0, 0.0, 0.0);
scalar speed = mag(U);
vector normalized = U / mag(U);
```

### Dimensioned

```cpp
dimensionedScalar rho("rho", dimDensity, 1000);
dimensionedVector g("g", dimAcceleration, vector(0, 0, -9.81));
```

---

## 4. Key Features

### Operator Overloading

```cpp
// Vector operations
vector a(1, 2, 3);
vector b(4, 5, 6);

scalar dot = a & b;      // Dot product
vector cross = a ^ b;    // Cross product
vector sum = a + b;      // Addition
```

### Dimension Checking

```cpp
// Automatic unit checking
dimensionedScalar p("p", dimPressure, 1000);
dimensionedScalar rho("rho", dimDensity, 1.2);

// Valid
dimensionedScalar dynP = 0.5 * rho * sqr(U);

// Invalid (compile/runtime error)
// p + U;  // Dimension mismatch!
```

---

## 5. Module Contents

| File | Topic |
|------|-------|
| 02_Basic_Primitives | scalar, vector, tensor |
| 03_Dimensioned_Types_Intro | dimensionedScalar/Vector |
| 04_Smart_Pointers | autoPtr, tmp, PtrList |
| 05_Containers | List, HashTable, Field |
| 06_Summary | Quick reference |
| 07_Exercises | Practice problems |

---

## Quick Reference

| Need | Type |
|------|------|
| Index | `label` |
| Value | `scalar` |
| Velocity | `vector` |
| Stress | `tensor` |
| With units | `dimensioned*` |
| Memory managed | `autoPtr`, `tmp` |

---

## Concept Check

<details>
<summary><b>1. ทำไมใช้ label แทน int?</b></summary>

**Portability** — label สามารถเป็น 32-bit หรือ 64-bit ตาม platform
</details>

<details>
<summary><b>2. scalar กับ double ต่างกันอย่างไร?</b></summary>

**scalar** คือ typedef ของ double ที่มี CFD-specific functions เช่น `mag()`, `sqr()`
</details>

<details>
<summary><b>3. dimensionedScalar ดีกว่า scalar อย่างไร?</b></summary>

มี **unit tracking** — ป้องกัน errors จาก mismatched units
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Basic Primitives:** [02_Basic_Primitives.md](02_Basic_Primitives.md)