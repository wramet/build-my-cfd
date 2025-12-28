# Eigen Decomposition

Eigen Decomposition ใน OpenFOAM

---

## Overview

> **Eigenvalues/vectors** = Principal directions and magnitudes of tensor

---

## 1. Eigenvalue Problem

$$\mathbf{T} \cdot \mathbf{v} = \lambda \mathbf{v}$$

- λ = eigenvalue (scalar)
- v = eigenvector (direction)

---

## 2. OpenFOAM Functions

```cpp
// Get eigenvalues
vector eigenVals = eigenValues(T);

// Get eigenvectors (columns of tensor)
tensor eigenVecs = eigenVectors(T);

// Principal values (sorted)
vector principal = eigenValues(T);
```

---

## 3. Symmetric Tensor

```cpp
// For symmetric tensors (stress, strain)
symmTensor stress(...);

// Eigenvalues are real
vector sigmaP = eigenValues(stress);

// Principal stresses: σ₁ > σ₂ > σ₃
```

---

## 4. Applications

### Principal Stress

```cpp
// Stress tensor
symmTensor sigma = ...;

// Principal stresses
vector sigmaPrincipal = eigenValues(sigma);

// Maximum principal
scalar sigma1 = sigmaPrincipal.x();
```

### Turbulence Anisotropy

```cpp
// Reynolds stress anisotropy
symmTensor b = R / (2*k) - I/3;

// Anisotropy eigenvalues
vector bEigen = eigenValues(b);
```

---

## 5. Example

```cpp
tensor T(1, 0, 0,
         0, 2, 0,
         0, 0, 3);

vector lambdas = eigenValues(T);
// lambdas = (1, 2, 3)

tensor V = eigenVectors(T);
// V columns are eigenvectors
```

---

## Quick Reference

| Function | Returns |
|----------|---------|
| `eigenValues(T)` | vector of λ |
| `eigenVectors(T)` | tensor (columns = v) |

---

## Concept Check

<details>
<summary><b>1. Eigenvalue คืออะไร?</b></summary>

**Scaling factor** ตาม eigenvector direction
</details>

<details>
<summary><b>2. Symmetric tensor eigenvalues เป็นอะไร?</b></summary>

**Real numbers** เสมอ
</details>

<details>
<summary><b>3. Principal stress ใช้ทำอะไร?</b></summary>

**Maximum/minimum stress** ในวัสดุ
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Operations:** [04_Tensor_Operations.md](04_Tensor_Operations.md)
