# Matrices & Linear Algebra - Introduction

บทนำ Matrices และ Linear Algebra ใน OpenFOAM — PDE → Ax = b

> **ทำไมต้องเรียนบทนี้?**
> - เข้าใจว่า **PDE กลายเป็น matrix** อย่างไร
> - รู้ความแตกต่าง **fvm:: vs fvc::**
> - เตรียมพร้อมสำหรับ custom solver development

---

## Overview

> **💡 fvMatrix = Discretized PDE**
>
> `fvm::ddt(T) + fvm::div(phi, T) == fvm::laplacian(alpha, T)`
> แปลงเป็น `Ax = b` ที่ linear solver แก้

---

## 1. From PDE to Matrix

### Continuous Equation

$$\frac{\partial T}{\partial t} + \nabla \cdot (\mathbf{U} T) = \nabla \cdot (\alpha \nabla T)$$

### Discretized Form

$$\mathbf{A} \cdot \mathbf{T} = \mathbf{b}$$

Where:
- **A**: Coefficient matrix
- **T**: Solution vector
- **b**: Source vector

---

## 2. OpenFOAM Approach

```cpp
fvScalarMatrix TEqn
(
    fvm::ddt(T)           // Time derivative → diagonal
  + fvm::div(phi, T)      // Convection → off-diagonal
  ==
    fvm::laplacian(alpha, T)  // Diffusion → off-diagonal
);

TEqn.solve();
```

---

## 3. Matrix Structure

### lduMatrix (Lower-Diagonal-Upper)

```
For face f connecting cells O and N:
- diag[O], diag[N]     : Diagonal coefficients
- upper[f]             : O→N coefficient
- lower[f]             : N→O coefficient
```

### fvMatrix

| Component | Purpose |
|-----------|---------|
| `diag_` | Diagonal coefficients |
| `upper_` | Upper triangle |
| `lower_` | Lower triangle |
| `source_` | RHS vector |
| `psi_` | Solution field |

---

## 4. fvm vs fvc

| Prefix | Type | Effect |
|--------|------|--------|
| `fvm::` | Implicit | → Matrix coefficients |
| `fvc::` | Explicit | → Source vector |

```cpp
// fvm: adds to matrix
fvm::ddt(T)
fvm::div(phi, T)
fvm::laplacian(alpha, T)

// fvc: adds to source
fvc::grad(p)
fvc::div(phi)
```

---

## 5. Solving

```cpp
// Solve and get residual
solverPerformance perf = TEqn.solve();

// With relaxation
TEqn.relax();
TEqn.solve();

// Check convergence
scalar residual = perf.initialResidual();
```

---

## 6. Module Contents

| File | Topic |
|------|-------|
| 02_Dense_vs_Sparse | Matrix types |
| 03_fvMatrix | Architecture |
| 04_Linear_Solvers | PCG, GAMG, etc. |
| 05_Parallel | Parallel solving |
| 06_Pitfalls | Common errors |
| 07_Summary | Exercises |

---

## Quick Reference

| Operator | fvm/fvc | Matrix Effect |
|----------|---------|---------------|
| `ddt` | fvm | Diagonal |
| `div` | fvm | Off-diagonal |
| `laplacian` | fvm | Off-diagonal |
| `grad` | fvc | Source |
| `Sp` | fvm | Diagonal (implicit) |
| `Su` | fvc | Source (explicit) |

---

## 🧠 Concept Check

<details>
<summary><b>1. fvm vs fvc ต่างกันอย่างไร?</b></summary>

- **fvm**: Implicit → matrix coefficients (LHS)
- **fvc**: Explicit → source vector (RHS)
</details>

<details>
<summary><b>2. lduMatrix คืออะไร?</b></summary>

**Lower-Diagonal-Upper** storage — sparse matrix format สำหรับ FV
</details>

<details>
<summary><b>3. ทำไมต้อง relax()?</b></summary>

**Improve convergence** — ลด oscillation ระหว่าง iterations
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **fvMatrix:** [03_fvMatrix_Architecture.md](03_fvMatrix_Architecture.md)