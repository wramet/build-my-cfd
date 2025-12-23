# Common Pitfalls & Debugging

![[index_labyrinth_tensor.png]]

---

## Overview

Working with tensors in OpenFOAM presents unique challenges that can lead to subtle bugs, performance issues, and numerical instabilities. This section identifies the most common pitfalls and provides practical strategies for avoiding and debugging them.

---

## 1. Tensor Contraction Errors

The ==most common source of errors== is incorrect tensor contraction - confusing single (`&`) and double (`&&`) contractions.

### Single vs Double Contraction

| Operation | Operator | Result Type | Mathematical Form | Description |
|-----------|----------|-------------|-------------------|-------------|
| **Double Contraction** | `&&` | `scalar` | $$s = \mathbf{A} : \mathbf{B} = \sum_{i,j=1}^{3} A_{ij}B_{ij}$$ | Full index contraction (Frobenius inner product) |
| **Single Contraction** | `&` | `vector` or `tensor` | $$w_i = \sum_{j=1}^{3} A_{ij}v_j$$ (tensor-vector) | Partial index contraction |

### Common Mistakes

```cpp
// ❌ ERROR: Double contraction yields scalar, not vector
vector v = A && B;

// ❌ ERROR: Type mismatch in assignment
tensor T = A && B;  // A && B returns scalar

// ✅ CORRECT: Proper contractions
scalar s = A && B;      // Double contraction → scalar
vector w = A & v;       // Single contraction → vector
tensor C = A & B;       // Single contraction → tensor
```

> [!WARNING] Type Safety
> OpenFOAM's tensor operations are type-safe at compile-time. Always check the expected return type before using contraction operators.

---

## 2. Symmetric Tensor Misconceptions

### Memory Layout Differences

Understanding the ==memory layout differences== between `tensor` and `symmTensor` is crucial:

**General Tensor (`tensor`):**
```
[XX][XY][XZ][YX][YY][YZ][ZX][ZY][ZZ]
  0   1   2   3   4   5   6   7   8
```

**Symmetric Tensor (`symmTensor`):**
```
[XX][XY][XZ][YY][YZ][ZZ]
  0   1   2   3   4   5
```

### Implicit Symmetry Access

```cpp
symmTensor S(1, 2, 3, 4, 5, 6);

// Stored components (direct access)
scalar s1 = S.xx();  // Returns 1
scalar s2 = S.xy();  // Returns 2

// Implicit components (computed via symmetry)
scalar s3 = S.yx();  // Returns S.xy() = 2
scalar s4 = S.zx();  // Returns S.xz() = 3
```

> [!TIP] Performance Optimization
> Using `symmTensor` instead of `tensor` for symmetric quantities reduces memory usage by ==33%== and improves cache efficiency.

---

## 3. Numerical Stability Issues

### Singular Tensors and Inversion

```cpp
// ❌ DANGEROUS: Inversion without checking
tensor invT = inv(T);  // May fail or produce NaN if det(T) ≈ 0

// ✅ SAFE: Check determinant first
scalar detT = det(T);
if (mag(detT) > SMALL) {
    tensor invT = inv(T);
} else {
    Warning << "Singular tensor detected: det(T) = " << detT << endl;
}
```

### Eigenvalue Computation Pitfalls

```cpp
symmTensor stressTensor;

// ❌ PROBLEMATIC: Eigenvalues may be numerically unstable
vector eigenvals = eigenValues(stressTensor);

// ✅ ROBUST: Validate physicality
vector eigenvals = eigenValues(stressTensor);
scalar minEigen = min(eigenvals);

if (minEigen < 0) {
    Warning << "Non-physical negative eigenvalue detected: "
            << minEigen << endl;
    // Apply regularization or check input
}
```

### Von Mises Stress Calculation

```cpp
// ✅ CORRECT: Von Mises stress from deviatoric stress
volSymmTensorField sigma = ...;
volSymmTensorField devSigma = dev(sigma);  // σ' = σ - (1/3)tr(σ)I
volScalarField vonMises = sqrt(1.5) * mag(devSigma);
```

**Mathematical Foundation:**
$$\sigma_{vm} = \sqrt{\frac{3}{2}\mathbf{S}:\mathbf{S}}$$

where $\mathbf{S} = \boldsymbol{\sigma} - \frac{1}{3}\text{tr}(\boldsymbol{\sigma})\mathbf{I}$ is the deviatoric stress tensor.

---

## 4. Dimensional Consistency Errors

OpenFOAM's dimensional analysis system catches many errors, but tensor operations require special attention.

```cpp
// ❌ ERROR: Dimensional mismatch
dimensionedSymmTensor stress("stress", dimPressure, symmTensor::zero);
dimensionedSymmTensor rate("rate", dimless/dimTime, symmTensor::zero);
auto result = stress + rate;  // Compile-time error!

// ✅ CORRECT: Ensure dimensional consistency
dimensionedSymmTensor stress("stress", dimPressure, symmTensor::zero);
dimensionedSymmTensor strain("strain", dimless, symmTensor::zero);
auto result = stress && strain;  // Scalar with dimensions [M L⁻¹ T⁻²]
```

> [!INFO] Dimensional Propagation
> Tensor operations automatically propagate dimensions:
> - **Double contraction**: `[A] × [B]`
> - **Single contraction**: `[A] × [B]`
> - **Gradient**: `[A] / [L]`

---

## 5. Tensor Field Boundary Conditions

### Incorrect Boundary Types

```cpp
// ❌ PROBLEMATIC: Fixed value on all patches
volSymmTensorField R
(
    IOobject("R", runTime.timeName(), mesh),
    mesh,
    dimensionedSymmTensor("zero", dimVelocity*dimVelocity, symmTensor::zero),
    calculatedFvPatchField<symmTensor>::typeName
);

// ✅ CORRECT: Appropriate boundary conditions
volSymmTensorField R
(
    IOobject("R", runTime.timeName(), mesh),
    mesh,
    dimensionedSymmTensor("zero", dimVelocity*dimVelocity, symmTensor::zero),
    boundaryConditions  // Specify appropriate BCs per patch
);
```

### Symmetry Enforcement

```cpp
// Ensure numerical symmetry for physical correctness
symmTensor T = ...;
scalar symmetryError = mag(T - T.T());

if (symmetryError > 1e-10) {
    Warning << "Tensor asymmetry detected: " << symmetryError << endl;
    T = symm(T);  // Enforce symmetry
}
```

---

## 6. Performance Pitfalls

### Memory Inefficiency

```cpp
// ❌ INEFFICIENT: Full tensor for symmetric quantities
volTensorField stress(...);  // Uses 9 components per cell

// ✅ EFFICIENT: Symmetric tensor
volSymmTensorField stress(...);  // Uses 6 components per cell
```

### Unnecessary Temporary Objects

```cpp
// ❌ INEFFICIENT: Creates temporaries
tensor result = A + B + C + D;

// ✅ EFFICIENT: Uses expression templates (lazy evaluation)
auto result = A + B + C + D;  // Single pass computation
```

### Pre-computation Strategies

```cpp
// ✅ OPTIMIZED: Pre-compute invariants
symmTensor S = ...;

scalar trS = tr(S);        // Compute once
scalar detS = det(S);      // Compute once
scalar magS = mag(S);      // Frobenius norm

// Reuse invariants in subsequent calculations
scalar pressure = trS / 3.0;
scalar invariant2 = 0.5 * (trS*trS - magS*magS);
```

---

## 7. Debugging Checklist

Use this systematic approach to debug tensor-related issues:

### Step 1: Type Verification
```cpp
// Check tensor ranks and types
static_assert(std::is_same_v<decltype(A && B), scalar>, "Type mismatch!");
```

### Step 2: Symmetry Validation
```cpp
// For symmetric tensors
template<class TensorType>
void checkSymmetry(const TensorType& T, const word& name) {
    scalar asymmetry = mag(T - T.T());
    Info << name << " asymmetry: " << asymmetry << endl;
}
```

### Step 3: Physical Consistency
```cpp
// Check tensor invariants for physical validity
bool isPhysical = (minEigenvalue > 0) && (det(T) > 0);
if (!isPhysical) {
    Warning << "Non-physical tensor detected!" << endl;
}
```

### Step 4: Dimensional Analysis
```cpp
// Verify dimensions at runtime
Info << "Tensor dimensions: " << T.dimensions() << endl;
```

### Step 5: Numerical Range Checks
```cpp
// Check for NaN or Inf
if (mag(T) > GREAT) {
    FatalError << "Tensor magnitude exceeds bounds!" << endl;
}
```

---

## 8. Common Error Messages and Solutions

| Error Message | Common Cause | Solution |
|---------------|--------------|----------|
| `Rank mismatch error` | Wrong contraction operator (`&` vs `&&`) | Check expected return type |
| `Tensor is singular` | `det(T) ≈ 0` when computing `inv(T)` | Add regularization or check determinant |
| `Dimensional inconsistency` | Adding tensors with different units | Verify `dimensionSet` compatibility |
| `Symmetry violation` | Numerical errors in symmetric operations | Apply `symm()` function to enforce |
| `NaN in tensor field` | Division by zero or invalid operations | Add checks for `SMALL` values |

---

## 9. Best Practices Summary

### ✅ DO

1. **Always check tensor ranks** before using contraction operators
2. **Use `symmTensor`** for physically symmetric quantities
3. **Validate determinants** before computing inverses
4. **Enforce dimensional consistency** using `dimensionSet`
5. **Pre-compute invariants** for repeated calculations
6. **Check eigenvalues** for physical validity
7. **Use `tmp<>` templates** for temporary field operations

### ❌ DON'T

1. **Don't mix contraction operators** without understanding return types
2. **Don't use `tensor`** when `symmTensor` suffices
3. **Don't compute `inv()`** without checking `det()`
4. **Don't ignore dimensional warnings** from the compiler
5. **Don't assume symmetry** without numerical verification
6. **Don't create unnecessary temporaries** in performance-critical code

---

## 10. Debugging Tools

### Tensor Visualization

```cpp
// Output tensor components for debugging
Info << "Tensor T = " << nl
    << "  xx: " << T.xx() << "  xy: " << T.xy() << "  xz: " << T.xz() << nl
    << "  yx: " << T.yx() << "  yy: " << T.yy() << "  yz: " << T.yz() << nl
    << "  zx: " << T.zx() << "  zy: " << T.zy() << "  zz: " << T.zz() << endl;
```

### Invariant Monitoring

```cpp
// Monitor tensor invariants during simulation
scalar I1 = tr(T);
scalar I2 = 0.5 * (I1*I1 - tr(T & T));
scalar I3 = det(T);

Info << "Tensor invariants: I1=" << I1 << ", I2=" << I2 << ", I3=" << I3 << endl;
```

### Eigenvalue Analysis

```cpp
// Principal stress/strain analysis
vector lambdas = eigenValues(T);
tensor vectors = eigenVectors(T);

Info << "Eigenvalues: " << lambdas << nl
    << "Eigenvectors (columns): " << vectors << endl;
```

---

## Conclusion

Understanding these common pitfalls and implementing robust debugging practices will significantly improve the reliability and performance of your OpenFOAM tensor operations. The key is to:

1. **Always verify types** before operations
2. **Check physical validity** during computation
3. **Use appropriate tensor types** for the physics
4. **Monitor numerical stability** throughout simulations

Following these guidelines will help you avoid the most frequent errors and develop efficient, correct CFD solvers.
