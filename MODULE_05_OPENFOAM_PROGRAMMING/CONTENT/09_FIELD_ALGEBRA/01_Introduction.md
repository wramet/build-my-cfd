# Field Algebra - Introduction

บทนำ Field Algebra

---

## Overview

> **Field Algebra** = Mathematical operations on entire fields at once

---

## 1. What is Field Algebra?

Operations that work on **all cells simultaneously**:

```cpp
// Instead of:
forAll(T, cellI) { result[cellI] = a[cellI] + b[cellI]; }

// Use:
volScalarField result = a + b;
```

---

## 2. Operation Types

| Category | Examples |
|----------|----------|
| Arithmetic | `+`, `-`, `*`, `/` |
| Mathematical | `sqr`, `sqrt`, `mag` |
| Vector | `&`, `^` |
| Calculus | `grad`, `div`, `laplacian` |

---

## 3. fvc vs fvm

| Prefix | Type | Result |
|--------|------|--------|
| `fvc::` | Explicit | Field |
| `fvm::` | Implicit | Matrix |

```cpp
// Explicit: evaluate now
volVectorField gradP = fvc::grad(p);

// Implicit: add to matrix
fvm::laplacian(alpha, T)
```

---

## 4. Key Operations

### Calculus (fvc)

```cpp
fvc::grad(p)         // Gradient
fvc::div(phi)        // Divergence
fvc::div(phi, T)     // Convection
fvc::laplacian(k, T) // Diffusion
fvc::curl(U)         // Curl
```

### Interpolation

```cpp
fvc::interpolate(T)  // Cell → face
fvc::average(Tf)     // Face → cell
```

---

## 5. Building Equations

```cpp
fvScalarMatrix TEqn
(
    fvm::ddt(T)
  + fvm::div(phi, T)
  ==
    fvm::laplacian(alpha, T)
  + fvc::div(source)
);

TEqn.solve();
```

---

## Quick Reference

| Need | Code |
|------|------|
| Gradient | `fvc::grad(p)` |
| Divergence | `fvc::div(U)` |
| Laplacian | `fvc::laplacian(k, T)` |
| Interpolate | `fvc::interpolate(T)` |
| Flux | `fvc::flux(U)` |

---

## Concept Check

<details>
<summary><b>1. fvc vs fvm?</b></summary>

- **fvc**: Explicit → evaluated now
- **fvm**: Implicit → matrix coefficients
</details>

<details>
<summary><b>2. ทำไมใช้ field algebra?</b></summary>

**Cleaner code** และ potential **vectorization**
</details>

<details>
<summary><b>3. interpolate ทำอะไร?</b></summary>

**Cell values → face values** สำหรับ flux calculation
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Arithmetic:** [02_Arithmetic_Operations.md](02_Arithmetic_Operations.md)