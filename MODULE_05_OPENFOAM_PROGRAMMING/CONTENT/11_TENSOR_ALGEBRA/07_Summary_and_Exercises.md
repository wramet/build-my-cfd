# Tensor Algebra - Summary and Exercises

สรุปและแบบฝึกหัด Tensor Algebra

---

## Summary

### Tensor Types

| Type | Components | Use |
|------|------------|-----|
| `scalar` | 1 | Temperature, pressure |
| `vector` | 3 | Velocity |
| `tensor` | 9 | Stress, gradient |
| `symmTensor` | 6 | Symmetric stress |

### Operations

| Operation | Syntax |
|-----------|--------|
| Dot product | `a & b` |
| Outer product | `a * b` |
| Double contraction | `A && B` |
| Transpose | `T.T()` |

---

## Exercise 1: Basic Tensor

```cpp
// Create tensor
tensor T(1, 0, 0, 0, 2, 0, 0, 0, 3);

// Operations
scalar trace_T = tr(T);      // 6
tensor T_symm = symm(T);     // Symmetric part
tensor T_skew = skew(T);     // Skew part
```

---

## Exercise 2: Velocity Gradient

```cpp
volTensorField gradU = fvc::grad(U);

// Strain rate
volSymmTensorField S = symm(gradU);

// Vorticity
volTensorField W = skew(gradU);

// Magnitude
volScalarField magS = mag(S);
```

---

## Exercise 3: Stress Tensor

```cpp
// Viscous stress
volSymmTensorField tau = -2 * mu * dev(symm(gradU));

// Reynolds stress
volSymmTensorField R = 2.0/3.0 * k * I - nuEff * 2 * symm(gradU);
```

---

## Exercise 4: Eigen Decomposition

```cpp
// Get eigenvalues
vector eigenValues = eigenValues(T);

// Get eigenvectors
tensor eigenVectors = eigenVectors(T);
```

---

## Quick Reference

| Need | Code |
|------|------|
| Trace | `tr(T)` |
| Symmetric | `symm(T)` |
| Deviatoric | `dev(T)` |
| Magnitude | `mag(T)` |
| Eigenvalues | `eigenValues(T)` |

---

## Concept Check

<details>
<summary><b>1. symm(gradU) คืออะไร?</b></summary>

**Strain rate tensor** = ½(∇U + ∇Uᵀ)
</details>

<details>
<summary><b>2. tr(T) คืออะไร?</b></summary>

**Trace** = T₁₁ + T₂₂ + T₃₃
</details>

<details>
<summary><b>3. dev(T) ทำอะไร?</b></summary>

**Deviatoric part** = T - ⅓ tr(T) I
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Operations:** [04_Tensor_Operations.md](04_Tensor_Operations.md)