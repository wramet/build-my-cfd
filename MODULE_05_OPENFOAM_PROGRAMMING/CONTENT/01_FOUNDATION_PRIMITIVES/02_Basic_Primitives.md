# Basic Primitives

ประเภทข้อมูลพื้นฐานใน OpenFOAM

---

## Overview

> OpenFOAM primitives = Mathematical types with CFD operations

---

## 1. Scalar Types

| Type | Definition | Use |
|------|------------|-----|
| `label` | int/long | Indices |
| `scalar` | double | Values |

```cpp
label cellI = 0;
scalar T = 300.0;
```

---

## 2. Vector

```cpp
// Create
vector v1(1.0, 2.0, 3.0);
vector v2 = vector::zero;
vector v3 = vector::one;

// Access components
scalar x = v1.x();  // or v1[0]
scalar y = v1.y();  // or v1[1]
scalar z = v1.z();  // or v1[2]
```

### Vector Operations

| Operation | Syntax | Result |
|-----------|--------|--------|
| Dot product | `v1 & v2` | scalar |
| Cross product | `v1 ^ v2` | vector |
| Magnitude | `mag(v1)` | scalar |
| Normalize | `v1 / mag(v1)` | vector |
| Component-wise | `cmptMultiply(v1, v2)` | vector |

---

## 3. Tensor

```cpp
// Create 3x3 tensor
tensor T
(
    1, 2, 3,    // row 1
    4, 5, 6,    // row 2
    7, 8, 9     // row 3
);

// Special tensors
tensor I = tensor::I;    // Identity
tensor Z = tensor::zero; // Zero
```

### Tensor Operations

| Operation | Syntax | Result |
|-----------|--------|--------|
| Trace | `tr(T)` | scalar |
| Determinant | `det(T)` | scalar |
| Transpose | `T.T()` | tensor |
| Inverse | `inv(T)` | tensor |
| Tensor-vector | `T & v` | vector |

---

## 4. Symmetric Tensor

```cpp
// 6 components (symmetric)
symmTensor S
(
    1, 2, 3,    // xx, xy, xz
       4, 5,    //     yy, yz
          6     //         zz
);

// Operations
scalar I1 = tr(S);         // First invariant
symmTensor dev_S = dev(S); // Deviatoric
symmTensor sph_S = sph(S); // Spherical
```

---

## 5. Vector Calculus (Fields)

```cpp
// Gradient
volVectorField gradT = fvc::grad(T);

// Divergence
volScalarField divU = fvc::div(U);

// Curl
volVectorField curlU = fvc::curl(U);

// Laplacian
volScalarField lapT = fvc::laplacian(alpha, T);
```

---

## 6. Mathematical Functions

| Function | Description |
|----------|-------------|
| `sqr(x)` | x² |
| `sqrt(x)` | √x |
| `mag(v)` | |v| |
| `magSqr(v)` | |v|² |
| `sin/cos/tan(x)` | Trig |
| `exp/log(x)` | Exp/Log |
| `pow(x, n)` | xⁿ |
| `sign(x)` | ±1 |
| `pos/neg(x)` | 1 if positive/negative |

---

## 7. Special Values

```cpp
// Vector constants
vector::zero     // (0, 0, 0)
vector::one      // (1, 1, 1)
vector::max      // (VGREAT, VGREAT, VGREAT)

// Directions
vector::x_       // (1, 0, 0)
vector::y_       // (0, 1, 0)
vector::z_       // (0, 0, 1)
```

---

## Quick Reference

| Type | Components | Example |
|------|------------|---------|
| `scalar` | 1 | T, p, k |
| `vector` | 3 | U, F |
| `tensor` | 9 | σ, ε |
| `symmTensor` | 6 | Reynolds stress |
| `sphericalTensor` | 1 | pI |

---

## Concept Check

<details>
<summary><b>1. & กับ ^ ใน vector ต่างกันอย่างไร?</b></summary>

- **&**: Dot product → scalar
- **^**: Cross product → vector
</details>

<details>
<summary><b>2. symmTensor มีกี่ components?</b></summary>

**6** components เพราะ symmetric: xx, xy, xz, yy, yz, zz
</details>

<details>
<summary><b>3. dev(T) คืออะไร?</b></summary>

**Deviatoric part**: $T - \frac{1}{3}tr(T)I$ (ลบส่วน isotropic ออก)
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Containers:** [05_Containers.md](05_Containers.md)
- **Exercises:** [07_Exercises.md](07_Exercises.md)
