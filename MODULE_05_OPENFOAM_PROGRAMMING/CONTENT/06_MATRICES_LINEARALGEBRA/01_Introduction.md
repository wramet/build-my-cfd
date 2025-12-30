# Matrices & Linear Algebra - Introduction

บทนำ Matrices และ Linear Algebra ใน OpenFOAM — PDE → Ax = b

> **ทำไมต้องเรียนบทนี้?**
> - เข้าใจว่า **PDE กลายเป็น matrix** อย่างไร
> - รู้ความแตกต่าง **fvm:: vs fvc::**
> - เตรียมพร้อมสำหรับ custom solver development

---

## 📋 Learning Objectives

หลังจากอ่านบทนี้ คุณจะสามารถ:

- **อธิบาย** กระบวนการแปลง PDE ให้เป็นรูปแบบ Matrix (Ax = b)
- **แยกแยะ** ความแตกต่างระหว่าง `fvm::` (implicit) และ `fvc::` (explicit)
- **ระบุ** โครงสร้าง lduMatrix และ fvMatrix ใน OpenFOAM
- **เขียน** discretized equation ด้วย fvm operators อย่างถูกต้อง
- **เลือก** ใช้ linear solver ที่เหมาะสมกับปัญหาที่แก้

---

## Prerequisites

ความรู้ที่ต้องมีก่อนเรียนบทนี้:

- [Module 01] CFD Fundamentals - Governing Equations
- [Module 05.02] Dimensioned Types - การจัดการ units
- [Module 05.04] Mesh Classes - fvMesh และ geometric fields
- **C++ Fundamentals:** Templates, smart pointers, OOP

---

## Overview

> **💡 fvMatrix = Discretized PDE**
>
> `fvm::ddt(T) + fvm::div(phi, T) == fvm::laplacian(alpha, T)`
> แปลงเป็น `Ax = b` ที่ linear solver แก้

---

## 1. From PDE to Matrix

### 1.1 Continuous Equation (PDE)

$$\frac{\partial T}{\partial t} + \nabla \cdot (\mathbf{U} T) = \nabla \cdot (\alpha \nabla T)$$

**หมายเหตุ:** นี่คือ PDE ที่ต่อเนื่อง (continuous) ซึ่งยังไม่สามารถแก้ด้วย computer ได้โดยตรง

### 1.2 Discretized Form (Matrix)

$$\mathbf{A} \cdot \mathbf{T} = \mathbf{b}$$

Where:
- **A**: Coefficient matrix (เก็บ coefficients จาก discretization)
- **T**: Solution vector (ค่า T ที่แต่ละ cell)
- **b**: Source vector (boundary conditions, source terms)

### 1.3 Visual Pattern: Dense vs Sparse Matrix

```
Dense Matrix (Full storage):          Sparse Matrix (LDU storage):
[[a₁₁ a₁₂ a₁₃ a₁₄]                   [0  0  a₁₃  0 ]  → only store non-zero
 [a₂₁ a₂₂ a₂₃ a₂₄]       →           [0  a₂₂  0   a₂₄]
 [a₃₁ a₃₂ a₃₃ a₃₄]                   [a₃₁ 0   a₃₃  0 ]
 [a₄₁ a₄₂ a₄₃ a₄₄]]                  [0  a₄₂  0   a₄₄]

Stored: ALL n² elements              Stored: lower[], diag[], upper[]
```

**OpenFOAM Context:** FV method produces sparse matrices because each cell only connects to neighbors through faces.

---

## 2. OpenFOAM Approach

### 2.1 fvMatrix Construction

```cpp
fvScalarMatrix TEqn
(
    fvm::ddt(T)           // Time derivative → diagonal
  + fvm::div(phi, T)      // Convection → off-diagonal
  ==
    fvm::laplacian(alpha, T)  // Diffusion → off-diagonal
);

TEqn.solve();  // Call linear solver
```

**OpenFOAM Implementation Detail:**
- `fvm::ddt` adds to diagonal coefficients (aₚ)
- `fvm::div` adds to off-diagonal (aₙᵦ) based on face flux
- `fvm::laplacian` adds to both diagonal and neighbors

### 2.2 Matrix Assembly Process

```
Step 1: Discretization
├─ fvm::ddt(T)      → Add to diagonal
├─ fvm::div(phi,T)  → Add to upper/lower
└─ fvm::laplacian   → Add to diagonal + upper/lower

Step 2: Boundary Conditions
└─ Modify matrix rows for boundary cells

Step 3: Solve
└─ Call linear solver (PCG, GAMG, etc.)
```

---

## 3. Matrix Structure

### 3.1 lduMatrix (Lower-Diagonal-Upper)

**Concept:** Sparse matrix storage optimized for FV meshes

```
For face f connecting cells Owner (O) and Neighbor (N):

Matrix row for cell P:  aₚTₚ + Σ aₙᵦTₙᵦ = bₚ
                       ↗     ↖
                      /       \
                  upper[f]  lower[f]
                    (O→N)     (N→O)

Storage arrays:
- diag[owner], diag[neighbor]  : Diagonal coefficients
- upper[face]                   : Owner→Neighbor coefficient  
- lower[face]                   : Neighbor→Owner coefficient
```

**Why LDU?** FV meshes are "locally connected" - each cell only interacts with immediate neighbors, resulting in sparse pattern.

### 3.2 fvMatrix Components

| Component | Type | Purpose | Example Use |
|-----------|------|---------|-------------|
| `diag_` | Field<scalar> | Diagonal coefficients | Time derivative, central part of laplacian |
| `upper_` | Field<scalar> | Upper triangle (owner→neighbor) | Convection, diffusion to neighbors |
| `lower_` | Field<scalar> | Lower triangle (neighbor→owner) | Reverse direction (symmetric if needed) |
| `source_` | Field<scalar> | RHS vector (b) | Source terms, explicit contributions |
| `psi_` | GeometricField | Solution field (T, p, U, etc.) | Where solution is stored |

---

## 4. fvm vs fvc

### 4.1 Fundamental Difference

| Prefix | Type | Mathematical Effect | Code Location |
|--------|------|---------------------|---------------|
| `fvm::` | Implicit | → Matrix coefficients (LHS) | Adds to A matrix |
| `fvc::` | Explicit | → Source vector (RHS) | Adds to b vector |

### 4.2 When to Use Which

```cpp
// fvm: Implicit → Matrix (LHS)
// Use when: Variable is being solved for
fvm::ddt(T)           // ∂T/∂t: Time derivative of solution
fvm::div(phi, T)      // ∇·(UT): Convection of T
fvm::laplacian(alpha, T)  // ∇·(α∇T): Diffusion of T
fvm::Sp(S, T)         // S×T: Implicit source term

// fvc: Explicit → Source (RHS)  
// Use when: Variable is known or from previous iteration
fvc::grad(p)          // ∇p: Pressure gradient (known)
fvc::div(phi)         // ∇·U: Velocity divergence (known)
fvc::laplacian(alpha, T)  // Explicit diffusion (rare)
fvc::Su(S, T)         // S×T: Explicit source term
```

**OpenFOAM Context:**
- **Implicit** = More stable, requires matrix solve, unconditionally stable (for dt)
- **Explicit** = Faster per iteration, but stability limit (CFL condition)

### 4.3 Example: Complete Equation

```cpp
// Transient convection-diffusion with source
fvScalarMatrix TEqn
(
    fvm::ddt(T)              // Implicit: ∂T/∂t
  + fvm::div(phi, T)         // Implicit: ∇·(UT)
  - fvm::laplacian(DT, T)    // Implicit: ∇·(D∇T)
  ==
    fvc::Sp(Q, T)            // Explicit: Heat source Q
  + fvc::ddt(T0)             // Explicit: Initial T₀ contribution
);
```

---

## 5. Solving

### 5.1 Basic Solve

```cpp
// Solve and get performance data
solverPerformance perf = TEqn.solve();

// Check convergence
scalar initialResidual = perf.initialResidual();
scalar finalResidual = perf.finalResidual();
int nIterations = perf.nIterations();

Info << "Solved in " << nIterations 
     << " iterations, final residual = " << finalResidual << endl;
```

### 5.2 Relaxation

**Why?** Improve convergence for highly coupled/nonlinear problems

```cpp
// Under-relaxation (stabilize iterative solution)
TEqn.relax(0.7);  // 70% new, 30% old
TEqn.solve();

// Equivalent to: T_new = 0.7 × T_solution + 0.3 × T_old
```

**OpenFOAM Context:** Typical relaxation factors:
- `p`: 0.3-0.7 (pressure)
- `U`: 0.7-0.9 (velocity)
- `T`: 0.8-1.0 (scalar)

### 5.3 Solver Selection (in fvSolution)

```cpp
// system/fvSolution
solvers
{
    T
    {
        solver          PCG;        // Conjugate Gradient
        preconditioner  DIC;        // Diagonal Incomplete Cholesky
        tolerance       1e-06;
        relTol          0.1;
    }
    
    p
    {
        solver          GAMG;       // Geometric Algebraic Multigrid
        smoother        DICGaussSeidel;
        tolerance       1e-07;
        relTol          0.01;
    }
}
```

---

## 6. Module Contents

| File | Topic | Key Concepts |
|------|-------|--------------|
| [02_Dense_vs_Sparse.md](02_Dense_vs_Sparse.md) | Matrix types | Dense vs Sparse, LDU storage |
| [03_fvMatrix_Architecture.md](03_fvMatrix_Architecture.md) | Architecture | fvMatrix internals, boundaries |
| [04_Linear_Solvers.md](04_Linear_Solvers.md) | Linear Solvers | PCG, GAMG, BiCGStab |
| [05_Parallel.md](05_Parallel.md) | Parallel solving | Domain decomposition |
| [06_Pitfalls.md](06_Pitfalls.md) | Common errors | Convergence, stability |
| [07_Summary_and_Exercises.md](07_Summary_and_Exercises.md) | Summary | Comprehensive exercises |

---

## Quick Reference

### fvm/fvc Operators

| Operator | fvm/fvc | Matrix Effect | When to Use |
|----------|---------|---------------|-------------|
| `ddt(field)` | fvm | Diagonal | Time derivative of solution |
| `div(phi, field)` | fvm | Off-diagonal | Convection of solution |
| `laplacian(gamma, field)` | fvm | Off-diagonal | Diffusion of solution |
| `grad(field)` | fvc | Source | Gradient of known field |
| `div(phi)` | fvc | Source | Divergence of known field |
| `Sp(S, field)` | fvm | Diagonal | Implicit source |
| `Su(S, field)` | fvc | Source | Explicit source |

### Matrix Structure

```
fvScalarMatrix TEqn(...)
  ├── diag_    : Field<scalar>  // Diagonal (nCells)
  ├── upper_   : Field<scalar>  // Upper triangle (nInternalFaces)
  ├── lower_   : Field<scalar>  // Lower triangle (nInternalFaces)
  ├── source_  : Field<scalar>  // RHS (nCells)
  └── psi_     : GeometricField // Solution field (T, p, U, ...)
```

---

## 🧠 Concept Check

<details>
<summary><b>1. fvm vs fvc ต่างกันอย่างไร?</b></summary>

- **fvm** (finite volume method, implicit): Adds to **matrix coefficients** (LHS)
  - ใช้เมื่อ: Variable ถูกแก้ (being solved for)
  - ตัวอย่าง: `fvm::ddt(T)`, `fvm::div(phi, T)`
  
- **fvc** (finite volume calculus, explicit): Adds to **source vector** (RHS)
  - ใช้เมื่อ: Variable รู้ค่าแล้ว (known from previous iteration)
  - ตัวอย่าง: `fvc::grad(p)`, `fvc::div(phi)`

**ความสำคัญ:** fvm มั่นคงกว่า (unconditionally stable) แต่ช้ากว่าต่อ iteration
</details>

<details>
<summary><b>2. lduMatrix คืออะไร และทำไม OpenFOAM ใช้รูปแบบนี้?</b></summary>

**lduMatrix** = **Lower-Diagonal-Upper** sparse matrix format

**โครงสร้าง:**
```
for each internal face f:
  upper[f] → coefficient from owner to neighbor
  lower[f] → coefficient from neighbor to owner
for each cell:
  diag[cell] → diagonal coefficient
```

**ทำไมใช้ LDU:**
- FV meshes produce **sparse matrices** (each cell connects only to neighbors)
- **Memory efficient:** Store only non-zero elements (not n² elements)
- **Computationally efficient:** Matrix operations scale with faces, not cells²

**OpenFOAM Context:** lduMatrix is base class; fvMatrix adds source terms and boundary handling
</details>

<details>
<summary><b>3. ทำไมต้อง relax()?</b></summary>

**Relaxation** = Under-relaxation เพื่อ improve convergence

**หลักการ:**
```
T_new = ω × T_solution + (1-ω) × T_old
where ω = relaxation factor (0 < ω ≤ 1)
```

**ทำต้องใช้:**
- **Nonlinear equations:** Coefficients depend on solution (e.g., convection with U-dependent phi)
- **Coupled equations:** p-U coupling in segregated solvers
- **Stability:** ลด oscillation ระหว่าง iterations

**Typical values:**
- Pressure: 0.3-0.7 (strongly coupled)
- Velocity: 0.7-0.9
- Scalars (T, k, ε): 0.8-1.0

**Trade-off:** ค่า ω ต่ำ = มั่นคงกว่า แต่ converge ช้ากว่า
</details>

<details>
<summary><b>4. PDE ถูกแปลงเป็น matrix อย่างไร?</b></summary>

**Process Flow:**

1. **Continuous PDE:**
   $$\frac{\partial T}{\partial t} + \nabla \cdot (\mathbf{U} T) = \nabla \cdot (\alpha \nabla T)$$

2. **Discretization (FVM):**
   $$\int_V \frac{\partial T}{\partial t} dV + \oint_A \mathbf{U} T \cdot d\mathbf{A} = \oint_A \alpha \nabla T \cdot d\mathbf{A}$$

3. **Discrete form per cell P:**
   $$a_P T_P + \sum_{NB} a_{NB} T_{NB} = b_P$$

4. **Matrix form (Ax = b):**
   $$\begin{bmatrix} a_1 & a_{12} & \cdots \\ a_{21} & a_2 & \cdots \\ \vdots & \vdots & \ddots \end{bmatrix} 
   \begin{bmatrix} T_1 \\ T_2 \\ \vdots \end{bmatrix} = 
   \begin{bmatrix} b_1 \\ b_2 \\ \vdots \end{bmatrix}$$

**OpenFOAM Context:** `fvm::` operators perform steps 2-3 automatically
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

### ภายใน Module นี้
- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Matrix Types:** [02_Dense_vs_Sparse.md](02_Dense_vs_Sparse.md) 
- **fvMatrix Architecture:** [03_fvMatrix_Architecture.md](03_fvMatrix_Architecture.md)
- **Linear Solvers:** [04_Linear_Solvers.md](04_Linear_Solvers.md)

### จาก Modules ก่อนหน้า
- **Mesh Classes:** [04_fvMesh.md](../04_MESH_CLASSES/05_fvMesh.md)
- **Geometric Fields:** [05_Fields_Introduction.md](../05_FIELDS_GEOMETRICFIELDS/01_Introduction.md)

### OpenFOAM Source Code
- `src/OpenFOAM/matrices/lduMatrix/`
- `src/finiteVolume/finiteVolume/fvMatrices/fvMatrix/`

---

## 🎯 Key Takeaways

1. **PDE → Matrix Transformation:** OpenFOAM แปลง PDE ให้เป็น `Ax = b` โดยอัตโนมัติผ่าน `fvm::` operators

2. **fvm vs fvc:**
   - `fvm::` = Implicit → Matrix (stable, slower per iteration)
   - `fvc::` = Explicit → Source (faster, stability limit)

3. **Sparse Matrix Storage:** lduMatrix (Lower-Diagonal-Upper) stores only non-zero elements เหมาะกับ FV meshes

4. **fvMatrix Structure:**
   - `diag_`, `upper_`, `lower_` → Matrix coefficients (A)
   - `source_` → RHS vector (b)
   - `psi_` → Solution field (x)

5. **Solving Process:** Build matrix → Apply BCs → Solve with linear solver (PCG/GAMG) → Check residuals

6. **Next Steps:** เรียนรู้ Dense vs Sparse matrices (02) เพื่อเข้าใจ storage efficiency และ solver selection

---

**Next:** [02_Dense_vs_Sparse.md](02_Dense_vs_Sparse.md) → เจาะลึกประเภท matrix และการเลือกใช้ solver