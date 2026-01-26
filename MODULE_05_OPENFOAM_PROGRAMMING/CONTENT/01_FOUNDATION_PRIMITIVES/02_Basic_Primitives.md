# 02_Basic_Primitives.md

---

## Learning Objectives

หลังจากอ่านบทนี้ คุณจะสามารถ:
- เลือกใช้ primitive types (`scalar`, `vector`, `tensor`) ได้อย่างถูกต้องตาม context
- ใช้ vector operators (`&`, `^`, `mag`) และเข้าใจความแตกต่าง
- คำนวณ tensor operations (trace, determinant, deviatoric)
- ใช้ fvc functions สำหรับ vector calculus บน mesh
- หลีกเลี่ยง common pitfalls ในการคำนวณ CFD

---

# Basic Primitives

ประเภทข้อมูลพื้นฐานใน OpenFOAM

---

## Overview

> **💡 คิดแบบนี้:**
> OpenFOAM primitives = **Mathematical types ที่รู้จัก CFD operations**
> 
> เปรียบเทียบ: C++ `double` รู้แค่ +, -, *, /
> แต่ OpenFOAM `vector` รู้ dot product, cross product, magnitude

> **ทำไมต้องรู้เรื่อง Primitives?**
> - **ทุกอย่างใน OpenFOAM สร้างจาก primitives เหล่านี้** — Fields, Equations, BCs
> - ใช้ operators ผิด (เช่น `&` vs `^`) = ผลลัพธ์ผิดโดยไม่ error
> - การเข้าใจ vector/tensor ช่วยให้ debug ปัญหาได้เร็ว

---

## 1. Scalar Types

### What
ประเภทข้อมูลพื้นฐานที่เก็บค่าตัวเลขแบบ integer และ floating-point

| Type | Definition | ใช้เมื่อ | ทำไม |
|------|------------|---------|------|
| `label` | int/long | Indices (cell, face IDs) | Integer เพราะ index ไม่มีทศนิยม |
| `scalar` | double | Physical values (T, p, k) | ต้องการ precision สูง |

```cpp
label cellI = 0;       // Cell index (integer)
scalar T = 300.0;      // Temperature (double)
```

### Why These Matter for CFD
- **label:** ใช้ reference cells/faces ในการ loop ผ่าน mesh
- **scalar:** เก็บค่า physics — pressure, temperature, density, turbulent kinetic energy

### How
```cpp
// Type aliasing allows precision change across program
label nCells = mesh.nCells();        // Mesh size
scalar rho = 1.225;                  // Air density
scalar p = 101325;                   // Pressure [Pa]
```

> **⚠️ Common Pitfall:** อย่าสับสน `label` กับ `scalar` — indices ต้องเป็น integer เสมอ

**ทำไม OpenFOAM ไม่ใช้ `int` และ `double` ตรงๆ?**
- Type aliasing ช่วยให้เปลี่ยน precision ได้ทั้งโปรแกรม (เช่น compile เป็น float)

---

## 2. Vector

### What
3D vector with x, y, z components ที่รองรับ vector operations พื้นฐาน

```cpp
// Create
vector v1(1.0, 2.0, 3.0);    // Explicit
vector v2 = vector::zero;     // (0, 0, 0)
vector v3 = vector::one;      // (1, 1, 1)

// Access components
scalar x = v1.x();  // หรือ v1[0]
scalar y = v1.y();  // หรือ v1[1]
scalar z = v1.z();  // หรือ v1[2]
```

### Why These Matter for CFD
- **Velocity, Force, Gradient** ล้วนเป็น vectors
- การคูณ vector ผิดวิธี = คำตอบผิดด้าน หรือผิด dimension

### How - Vector Operations

| Operation | Syntax | Result | ใช้เมื่อ |
|-----------|--------|--------|---------|
| **Dot product** | `v1 & v2` | scalar | หา projection, work done |
| **Cross product** | `v1 ^ v2` | vector | หา normal, torque |
| **Magnitude** | `mag(v1)` | scalar | หา speed จาก velocity |
| **Normalize** | `v1 / mag(v1)` | vector | หา unit direction |
| **Component-wise** | `cmptMultiply(v1, v2)` | vector | Scale แต่ละ component |

> **⚠️ ระวัง Operator Symbols:**
> - `&` = **Dot product** (ไม่ใช่ bitwise AND!)
> - `^` = **Cross product** (ไม่ใช่ XOR!)
> - `*` = **Scalar multiply** (ไม่ใช่ vector multiply)

**ตัวอย่างการใช้ผิด:**
```cpp
vector U(1, 0, 0);
vector n(0, 1, 0);

// ผิด! ต้องการ dot product แต่ใช้ *
// scalar Un = U * n;  // Compile error!

// ถูก! ใช้ & สำหรับ dot product
scalar Un = U & n;  // = 0 (orthogonal)
```

### When to Use Decision Guide
```
ต้องการค่า direction? → vector
ต้องการ magnitude? → mag(vector)
ต้องการ projection? → vectorA & vectorB
ต้องการ normal vector? → vectorA ^ vectorB
```

---

## 3. Tensor

### What
3×3 matrix (9 components) ที่ represent linear transformations

```cpp
// Create 3x3 tensor (row-major)
tensor T
(
    1, 2, 3,    // row 1: Txx, Txy, Txz
    4, 5, 6,    // row 2: Tyx, Tyy, Tyz
    7, 8, 9     // row 3: Tzx, Tzy, Tzz
);

// Special tensors
tensor I = tensor::I;    // Identity (diagonal = 1)
tensor Z = tensor::zero; // Zero tensor
```

### Why These Matter for CFD
- **Stress, Strain, Velocity gradient** เป็น tensors
- เข้าใจ tensor = เข้าใจ turbulence modeling

### How - Tensor Operations

| Operation | Syntax | Result | ความหมายทางกายภาพ |
|-----------|--------|--------|------------------|
| **Trace** | `tr(T)` | scalar | Sum of diagonal (= 3p for stress) |
| **Determinant** | `det(T)` | scalar | Volume scaling factor |
| **Transpose** | `T.T()` | tensor | สลับ row-column |
| **Inverse** | `inv(T)` | tensor | Undo the transformation |
| **Tensor-vector** | `T & v` | vector | Apply transformation to vector |

**ตัวอย่าง: Strain Rate Tensor**
```cpp
// Velocity gradient
volTensorField gradU = fvc::grad(U);

// Strain rate = 0.5 * (gradU + gradU.T)
volSymmTensorField S = symm(gradU);
```

### When to Use Decision Guide
```
Quantity มีทิศทาง + transform? → tensor
Symmetric? → symmTensor (6 components)
Isotropic? → sphericalTensor (1 component)
```

> **⚠️ Common Pitfall:** ใช้ `tensor` ทุกอย่างแม้ quantity จะ symmetric — เสีย memory 33%!

---

## 4. Symmetric Tensor

### What
Tensor ที่มีความสมมาตร (Aij = Aji) เก็บแค่ 6 components

```cpp
// 6 components only (upper triangle + diagonal)
symmTensor S
(
    1, 2, 3,    // xx, xy, xz
       4, 5,    //     yy, yz
          6     //         zz
);

// Decomposition
scalar I1 = tr(S);         // First invariant (hydrostatic)
symmTensor dev_S = dev(S); // Deviatoric part (shear)
symmTensor sph_S = sph(S); // Spherical part (pressure)
```

### Why These Matter for CFD
- หลาย physical quantities สมมาตร (stress, strain)
- เก็บแค่ 6 components แทน 9 → **ประหยัด memory 33%**
- Turbulence models มักสนใจแค่ deviatoric part

### How - Decomposition
**Spherical (sph):** ส่วนที่ทำให้อัดตัว (pressure-like)
```cpp
symmTensor sph_S = sph(S);  // (1/3)*tr(S)*I
```

**Deviatoric (dev):** ส่วนที่ทำให้บิดเบี้ยว (shear)
```cpp
symmTensor dev_S = dev(S);  // S - sph(S)
```

**ทำไม dev/sph สำคัญ?**
- **Spherical:** Pressure, volumetric deformation
- **Deviatoric:** Shear, shape change
- Turbulence models มักสนใจแค่ deviatoric part

### When to Use Decision Guide
```
Quantity symmetric? → symmTensor
- Stress tensor → symmTensor ✓
- Strain rate → symmTensor ✓
- Velocity gradient → tensor (asymmetric!)
```

---

## 5. Vector Calculus (Fields)

### What
Operations บน fields ที่ distributed ตาม mesh ใช้ `fvc` (finite volume calculus)

### Why These Matter for CFD
- fvc ใช้ mesh geometry ถูกต้อง (รวม non-orthogonality)
- fvc consistent กับ fvm → mass conservative

### How
```cpp
// Gradient: scalar → vector
volVectorField gradT = fvc::grad(T);

// Divergence: vector → scalar
volScalarField divU = fvc::div(U);

// Curl: vector → vector
volVectorField curlU = fvc::curl(U);

// Laplacian: scalar → scalar
volScalarField lapT = fvc::laplacian(alpha, T);
```

### When to Use Decision Guide
```
ต้องการ gradient? → fvc::grad(scalar)
ต้องการ divergence? → fvc::div(vector)
ต้องการ curl? → fvc::curl(vector)
ต้องการ Laplacian? → fvc::laplacian(diffusivity, field)
```

> **⚠️ Common Pitfall:** อย่าใช้ analytical derivatives — fvc รักษา conservation บน non-orthogonal meshes

---

## 6. Mathematical Functions

### What
Built-in functions สำหรับ scalar/vector operations ที่ optimize แล้ว

| Function | Description | ใช้เมื่อ |
|----------|-------------|---------|
| `sqr(x)` | x² | Kinetic energy: 0.5*sqr(U) |
| `sqrt(x)` | √x | Speed from kinetic energy |
| `mag(v)` | \|v\| | Velocity magnitude |
| `magSqr(v)` | \|v\|² | เร็วกว่า mag(v)*mag(v) |
| `sign(x)` | ±1 | Determine direction |
| `pos/neg(x)` | 1 if positive/negative | Conditional operations |

### Why These Matter for CFD
- Performance: `magSqr` หลีกเลี่ยง sqrt ที่ช้า
- Clarity: `sign(x)` ชัดเจนกว่า `x > 0 ? 1 : -1`

### How
```cpp
// Kinetic energy per unit mass
scalar ke = 0.5 * magSqr(U);  // Fast!

// Speed from velocity
scalar speed = mag(U);         // = sqrt(magSqr(U))

// Conditional flux
scalar flux = pos(p - pRef) * U;  // Zero if p <= pRef
```

**ทำไม magSqr ดีกว่า sqr(mag(v))?**
- `magSqr(v) = v.x()² + v.y()² + v.z()`  → 3 multiplications
- `sqr(mag(v)) = √(x² + y² + z²)²` → 3 mult + 1 sqrt + 1 sqr
- หลีกเลี่ยง sqrt ที่ไม่จำเป็น → **เร็วกว่า**

---

## 7. Special Values

### What
Predefined constants สำหรับ initialization และ direction vectors

```cpp
// Vector constants
vector::zero     // (0, 0, 0)    — Starting point
vector::one      // (1, 1, 1)    — Scaling
vector::max      // (VGREAT, VGREAT, VGREAT) — Bounding box init

// Directions (unit vectors)
vector::x_       // (1, 0, 0)    — x direction
vector::y_       // (0, 1, 0)    — y direction
vector::z_       // (0, 0, 1)    — z direction
```

### Why These Matter for CFD
- Initialization ที่ consistent ทั่ว codebase
- Direction vectors สำหรับ BCs, forces, projections

### How
```cpp
// Initialize bounding box
vector minBox = vector::max;
vector maxBox = vector::zero;

// Gravity direction
vector g = mag(g) * vector::z_;  // Downward

// Face normal projection
scalar Un = U & (faceNormal / mag(faceNormal));
```

---

## Quick Reference

| Type | Components | Example Fields | ทำไมใช้ |
|------|------------|----------------|--------|
| `scalar` | 1 | T, p, k | ค่าเดี่ยว (temperature, pressure) |
| `vector` | 3 | U, F | ทิศทาง + magnitude (velocity, force) |
| `tensor` | 9 | σ, ∇U | Transformation, full stress |
| `symmTensor` | 6 | Reynolds stress | Symmetric saves memory |
| `sphericalTensor` | 1 | pI | Isotropic part only |

---

## 🧠 Concept Check

<details>
<summary><b>1. & กับ ^ ใน vector ต่างกันอย่างไร?</b></summary>

| Operator | Name | Result | Physics |
|----------|------|--------|---------|
| **&** | Dot product | scalar | Work = F & d |
| **^** | Cross product | vector | Torque = r ^ F |

**จำ:** `&` ให้ผลเป็นตัวเลข (scalar), `^` ให้ผลเป็นทิศทาง (vector)
</details>

<details>
<summary><b>2. symmTensor มีกี่ components? ทำไมไม่ใช้ tensor ธรรมดา?</b></summary>

**6** components: xx, xy, xz, yy, yz, zz

**ทำไมใช้:** 
- Symmetric tensor มี Aij = Aji → เก็บแค่ครึ่งเดียว
- ประหยัด memory 33% (6 vs 9)
- OpenFOAM optimize operations สำหรับ symmTensor
</details>

<details>
<summary><b>3. dev(T) คืออะไร? ใช้เมื่อไหร่?</b></summary>

**Deviatoric part**:1$T_{dev} = T - \frac{1}{3}tr(T)I$

**ความหมาย:** ลบส่วน isotropic (pressure-like) ออก เหลือแต่ส่วน shear

**ใช้เมื่อ:**
- Turbulence modeling (Reynolds stress → deviatoric)
- Viscous stress calculation
</details>

<details>
<summary><b>4. ทำไมใช้ magSqr แทน sqr(mag)?</b></summary>

**เร็วกว่า!**
- `magSqr(v)` = x² + y² + z²  (3 operations)
- `sqr(mag(v))` = (√(x² + y² + z²))² → sqrt ช้า!

**กฎ:** ถ้าต้องการ |v|² ใช้ `magSqr` เสมอ
</details>

---

## 📚 Key Takeaways

1. **Type Selection:** เลือก primitive types ตาม dimensionality ของ physical quantity
   - Scalar → pressure, temperature
   - Vector → velocity, force
   - Tensor → stress, gradient

2. **Operator Awareness:** OpenFOAM operators ต่างจาก C++!
   - `&` = dot product, `^` = cross product
   - ใช้ผิด → compile error หรือผลลัพธ์ผิด

3. **Memory Efficiency:** ใช้ `symmTensor` แทน `tensor` เมื่อ possible
   - ประหยัด 33% memory
   - Faster operations

4. **Performance:** ใช้ `magSqr` แทน `sqr(mag)` — avoid unnecessary sqrt

5. **fvc Functions:** ใช้ finite volume calculus แทน analytical derivatives
   - Conservation บน non-orthogonal meshes
   - Consistent กับ discretization

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md) — ดู architecture ภาพรวม
- **Smart Pointers:** [04_Smart_Pointers.md](04_Smart_Pointers.md) — memory management
- **Containers:** [05_Containers.md](05_Containers.md) — List, Field, PtrList
- **Exercises:** [07_Exercises.md](07_Exercises.md) — ฝึกปฏิบัติ

**บทถัดไป:** [03_Dimensions_Units.md](03_Dimensions_Units.md) — ระบบ units ใน OpenFOAM