# Mathematical Type Theory

ทฤษฎีประเภททางคณิตศาสตร์ใน OpenFOAM

---

## Overview

> OpenFOAM types = Mathematical entities with proper algebra

---

## 1. Tensor Rank Hierarchy

| Rank | Type | Components | Example |
|------|------|------------|---------|
| 0 | `scalar` | 1 | p, T, k |
| 1 | `vector` | 3 | U, F |
| 2 | `tensor` | 9 | σ, ∇U |
| 2 (symm) | `symmTensor` | 6 | R |
| 2 (spher) | `sphericalTensor` | 1 | pI |

---

## 2. Transformation Rules

Under coordinate rotation R:

| Type | Transformation |
|------|----------------|
| `scalar` | φ' = φ (invariant) |
| `vector` | v' = R·v |
| `tensor` | T' = R·T·Rᵀ |

---

## 3. Invariants

### Tensor Invariants

| Invariant | Formula | Code |
|-----------|---------|------|
| I₁ | tr(T) | `tr(T)` |
| I₂ | ½(tr²(T) - tr(T²)) | `invariantII(T)` |
| I₃ | det(T) | `det(T)` |

### Application

```cpp
symmTensor S = symm(gradU);
scalar I2 = invariantII(S);
scalar strainRate = sqrt(2.0 * I2);
```

---

## 4. Decomposition

### Tensor Decomposition

$$T = \frac{1}{3}tr(T)I + dev(T)$$

| Part | Code | Meaning |
|------|------|---------|
| Spherical | `sph(T)` | Isotropic |
| Deviatoric | `dev(T)` | Anisotropic |

### Velocity Gradient

$$\nabla U = S + \Omega$$

```cpp
tensor gradU = fvc::grad(U);
symmTensor S = symm(gradU);    // Strain rate
tensor Omega = skew(gradU);     // Rotation
```

---

## 5. Products

| Operation | Syntax | Result |
|-----------|--------|--------|
| Dot | `a & b` | Rank reduced |
| Outer | `a * b` | Rank increased |
| Double dot | `A && B` | Scalar |

### Examples

```cpp
// Vector dot
scalar s = v1 & v2;  // v1·v2

// Tensor-vector
vector Tv = T & v;   // T·v

// Double contraction
scalar s = A && B;   // A:B = Σᵢⱼ Aᵢⱼ Bᵢⱼ
```

---

## 6. Eigenvalue Problems

```cpp
// Symmetric tensor eigenvalues
symmTensor S = ...;
vector eigenVals = eigenValues(S);
tensor eigenVecs = eigenVectors(S);

// Principal stresses
scalar sigma1 = eigenVals.x();
scalar sigma2 = eigenVals.y();
scalar sigma3 = eigenVals.z();
```

---

## 7. Common Operations

### Strain Rate

$$S = \frac{1}{2}(\nabla U + (\nabla U)^T)$$

```cpp
symmTensor S = 0.5 * (gradU + gradU.T());
// or
symmTensor S = symm(gradU);
```

### Vorticity

$$\omega = \nabla \times U$$

```cpp
volVectorField omega = fvc::curl(U);
```

---

## Quick Reference

| Function | Description |
|----------|-------------|
| `tr(T)` | Trace |
| `det(T)` | Determinant |
| `dev(T)` | Deviatoric |
| `sph(T)` | Spherical |
| `symm(T)` | Symmetric part |
| `skew(T)` | Skew-symmetric part |
| `inv(T)` | Inverse |
| `eigenValues(S)` | Eigenvalues |

---

## Concept Check

<details>
<summary><b>1. dev(T) คืออะไร?</b></summary>

**Deviatoric part**: $T - \frac{1}{3}tr(T)I$ = ส่วนที่ traceless (no volume change)
</details>

<details>
<summary><b>2. ทำไม strain rate ใช้ symm(gradU)?</b></summary>

เพราะ **strain rate ต้อง symmetric** — skew part คือ rotation ไม่ใช่ deformation
</details>

<details>
<summary><b>3. Double contraction ใช้เมื่อไหร่?</b></summary>

เมื่อต้องการ **scalar จาก 2 tensors** เช่น stress power: σ:ε̇
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Design Philosophy:** [02_Design_Philosophy.md](02_Design_Philosophy.md)