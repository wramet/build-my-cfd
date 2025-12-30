# Matrices & Linear Algebra - Overview

## Learning Objectives

By the end of this module, you will be able to:

- **Identify** the core matrix classes in OpenFOAM's linear algebra hierarchy (`lduMatrix`, `fvMatrix`, `fvScalarMatrix`, `fvVectorMatrix`)
- **Explain** why sparse matrix storage (LDU format) is essential for CFD efficiency
- **Assemble** discretized equations using `fvm::` operators and understand their transformation to linear systems
- **Select** appropriate linear solvers and preconditioners for different equation types (symmetric vs non-symmetric)
- **Configure** solver parameters in `system/fvSolution` for optimal performance and stability
- **Diagnose** common convergence issues related to solver selection and matrix conditioning

---

## Overview

> **💡 CFD = Solving Linear Systems Repeatedly**
>
> Every time step, every equation: **PDE → Discretize (fvm::) → fvMatrix → lduMatrix → Solver → Solution**

This transformation happens **thousands of times per simulation**. Understanding OpenFOAM's linear algebra backbone is not optional—it's the difference between:
- ✅ Simulation converging in hours vs days
- ✅ Stable solution vs divergence
- ✅ Efficient memory usage vs crashes

### Why Linear Algebra Matters in Practice

| Impact | Consequence |
|--------|-------------|
| **90% of compute time** | Poor solver choice = 10x slower simulation |
| **Matrix conditioning** | Ill-conditioned matrices = convergence stalls or divergence |
| **Memory efficiency** | Dense matrices = impossible for industrial cases (>1M cells) |
| **Parallel scalability** | Inefficient operations = poor strong scaling |

### OpenFOAM's Matrix Pipeline

```mermaid
flowchart TD
    A[PDE<br/>∂φ/∂t + ∇·(uφ) = ∇·(Γ∇φ)] --> B[fvm:: Discretization<br/>Finite Volume Operators]
    B --> C[fvMatrix<br/>Coefficients + Source]
    C --> D[lduMatrix<br/>LDU Sparse Storage]
    D --> E[Linear Solver<br/>PCG/PBiCGStab/GAMG]
    E --> F[solution Field]
    
    style A fill:#e3f2fd
    style B fill:#fff3e0
    style C fill:#f3e5f5
    style D fill:#ffebee
    style E fill:#e8f5e9
    style F fill:#e0f2f1
```

<!-- IMAGE: IMG_05_005 -->
<!-- 
Purpose: To explain that OpenFOAM doesn't store full dense matrices but uses LDU addressing (Lower-Diagonal-Upper). This image must connect mesh topology (cell P connected to neighbors) to the resulting sparse matrix structure.
Prompt: "Data Structure Diagram of LDU Matrix Storage. **Components:** 1. A small 5x5 Matrix grid with only diagonal and a few off-diagonal cells filled (others blank). 2. Three 1D Arrays labeled 'Diagonal', 'Lower', 'Upper'. 3. Arrows connecting the non-zero matrix cells to their corresponding slots in the arrays. **Labeling:** Show that 'Lower' stores lower-triangle neighbors, 'Upper' stores upper-triangle neighbors. **Style:** Computer Science infographic, flat 2D, white background, distinct array blocks."
-->
![[IMG_05_005.jpg]]

**Key Insight:** For a typical 3D mesh with 20 neighbors per cell, the matrix is **95% empty**. LDU storage ignores zeros, storing only:
- **L**ower coefficients (neighbors with higher index)
- **D**iagonal coefficients (cell center)
- **U**pper coefficients (neighbors with lower index)

---

## 1. Core Classes

### Why This Hierarchy?

OpenFOAM separates **physics** (fvMatrix) from **numerics** (lduMatrix):

```cpp
// PHYSICS LAYER: What equation are we solving?
fvScalarMatrix TEqn(fvm::ddt(T) + fvm::div(phi, T) == fvm::laplacian(DT, T));

// NUMERICS LAYER: How do we store and solve it?
lduMatrix& ldu = TEqn;  // Automatic conversion for solving
```

| Class | Purpose | Memory Pattern | Key Operations |
|-------|---------|----------------|----------------|
| `lduMatrix` | **Sparse storage** base class | 3 arrays (L, D, U) | Matrix-vector multiply, solver interface |
| `fvMatrix<Type>` | **Discretized equation** wrapper | Coeffs + boundary | `fvm::` operator assembly, relaxation |
| `fvScalarMatrix` | Scalar field equations | `fvMatrix<scalar>` | Temperature, pressure, k, ε, ω |
| `fvVectorMatrix` | Vector field equations | `fvMatrix<vector>` | Velocity U, displacement D |

**Practical Impact:** When debugging convergence issues, you need to know which layer is causing problems:
- Assembly error? → Check `fvMatrix` coefficients (wrong physics discretization)
- Solver error? → Check `lduMatrix` properties (poor matrix conditioning)

---

## 2. Matrix Assembly Process

### From PDE to Linear System

Every term in your PDE becomes matrix coefficients:

```cpp
// GOVERNING EQUATION:
// ∂T/∂t + ∇·(uT) = ∇·(α∇T) + Q
//
// DISCRETIZED (OpenFOAM):
fvScalarMatrix TEqn
(
    fvm::ddt(T)              // Unsteady term → diagonal + source
  + fvm::div(phi, T)         // Convection → off-diagonal (upwind/QUICK/etc.)
  ==
    fvm::laplacian(alpha, T) // Diffusion → diagonal + off-diagonal
  + Q                        // Source term → source array
);
```

**What Happens Under the Hood:**

| Operation | Matrix Effect | Why It Matters |
|-----------|---------------|----------------|
| `fvm::ddt(T)` | Adds to diagonal + source | Larger diagonal = more stable (diagonal dominance) |
| `fvm::div(phi, T)` | Off-diagonal from neighbors | Upwind scheme = stable but diffusive; Central differencing = accurate but unstable |
| `fvm::laplacian(k, T)` | Symmetric L+U contributions | Diffusion always improves conditioning |
| Explicit source | Source array only | Can break diagonal dominance if too large |

**Consequence for Solver Choice:**
- **Pressure equation** (`fvm::laplacian` dominated) → Symmetric, well-conditioned → Use PCG
- **Velocity equation** (`fvm::div` dominated, upwind) → Non-symmetric, poorer conditioning → Use PBiCGStab

---

## 3. Matrix Operations & Solution Control

### Essential Operations

```cpp
// 1. SOLVE: Main call (config via system/fvSolution)
solverPerformance perf = TEqn.solve();
// Access residuals: perf.initialResidual(), perf.finalResidual()

// 2. RELAXATION: Prevent divergence in coupled solvers
TEqn.relax(0.7);  // Blend: A_new = 0.7*A_new + 0.3*A_old
// Critical for: Simple algorithms, transient schemes

// 3. RESIDUAL CALCULATION: Check convergence
scalar res = TEqn.solve().initialResidual();
// Use in: Custom convergence criteria, adaptive time stepping

// 4. COEFFICIENT ACCESS: Debugging matrix properties
const scalarField& diag = TEqn.diag();    // Diagonal coefficients
const scalarField& lower = TEqn.lower();  // Lower triangle
const scalarField& upper = TEqn.upper();  // Upper triangle
const scalarField& source = TEqn.source(); // RHS vector

// 5. MATRIX CONDITIONING: Diagonal dominance check
scalar DiagDom = sum(mag(diag)) / (sum(mag(lower + upper)) + SMALL);
// DiagDom > 1 = Good; DiagDom < 1 = Potentially unstable
```

### Quick Reference: Common Tasks

| Task | Code | Use Case |
|------|------|----------|
| Create equation | `fvScalarMatrix TEqn(fvm::ddt(T) + fvm::div(phi, T) == fvm::laplacian(DT, T));` | Assemble discretized PDE |
| Solve | `TEqn.solve();` | Execute linear solver (configured in `fvSolution`) |
| Relax | `TEqn.relax(0.7);` | Under-relaxation for stability |
| Get diagonal | `const scalarField& d = TEqn.diag();` | Check diagonal dominance |
| Get source | `const scalarField& s = TEqn.source();` | Inspect RHS values |
| Get residual | `scalar r = TEqn.solve().initialResidual();` | Monitor convergence |
| Access LDU | `TEqn.lower()`, `TEqn.upper()` | Debug matrix sparsity pattern |

---

## 4. Solver Selection Fundamentals

> **⚠️ Important:** Detailed solver comparison is in **04_Linear_Solvers_Hierarchy.md**. This section provides only essential context for understanding the matrix classes.

### Solver Families

| Solver | Matrix Type | When to Use | Example |
|--------|-------------|-------------|---------|
| `PCG` | **Symmetric** | Pressure, diffusion-dominated cases | `p`, `pd` in incompressible flow |
| `PBiCGStab` | **Non-symmetric** | Velocity, convection-dominated cases | `U`, `T` with high convection |
| `GAMG` | Either | **Large problems** (>500k cells) | Any field in industrial cases |
| `smoothSolver` | Either | Simple cases, bad initial guesses | Poor mesh quality scenarios |

### Preconditioner Impact

Preconditioners transform the matrix to improve convergence:

| Preconditioner | Cost | Benefit | Best For |
|----------------|------|---------|----------|
| `none` | Lowest | Baseline | Small test cases |
| `DIC` (Diagonal Incomplete Cholesky) | Low | Good for symmetric | Pressure with PCG |
| `DILU` (Diagonal ILU) | Low | Moderate for non-symmetric | Velocity with PBiCGStab |
| `GAMG` | High | Excellent for large | All cases on >1M cells |

**Rule of Thumb:** Poor preconditioner = 10x more iterations. Always tune this before tweaking other parameters.

---

## 5. Configuration: system/fvSolution

### Practical Example

```cpp
// File: system/fvSolution
solvers
{
    // PRESSURE: Symmetric matrix → PCG + DIC
    p
    {
        solver          PCG;           // Conjugate Gradient (requires symmetry)
        preconditioner  DIC;           // Diagonal Incomplete Cholesky
        tolerance       1e-06;         // Absolute convergence
        relTol          0.01;          // Relative tolerance (1% of initial)
        minIter         0;             // Minimum iterations
        maxIter         1000;          // Safety limit
    }

    // VELOCITY: Non-symmetric (convection) → PBiCGStab + DILU
    U
    {
        solver          PBiCGStab;     // Stabilized BiCG (handles non-symmetry)
        preconditioner  DILU;          // Diagonal Incomplete LU
        tolerance       1e-05;         // Slightly looser than pressure
        relTol          0.1;           // 10% reduction sufficient
        minIter         0;
        maxIter         1000;
    }

    // TEMPERATURE: Highly convective → Aggressive tolerance
    T
    {
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-04;          // Loose: temperature errors smooth out
        relTol          0.1;            // Don't waste iterations
        minIter         0;
        maxIter         500;
    }

    // TURBULENCE: Often poorly conditioned → Conservative
    k
    {
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-05;          // Must be tight: k affects viscosity
        relTol          0.01;           // More accurate than U/T
        minIter         1;              // At least 1 iteration
        maxIter         1000;
    }
}
```

### Tuning Strategy

1. **Start default:** Use `tutorials/heatTransfer/` settings as baseline
2. **Monitor residuals:** If `initialResidual` doesn't drop 10x in 10 iterations → Change preconditioner
3. **Adjust `relTol`:** 
   - Tight (0.01) for pressure, turbulence
   - Loose (0.1) for velocity, temperature
4. **Check `maxIter`:** Hitting this limit = diverging or poor preconditioning

---

## 6. Module Structure

| File | Focus | Key Questions Answered |
|------|-------|----------------------|
| **01_Introduction** | Linear algebra in CFD context | Why is 90% of compute time here? |
| **02_Dense_vs_Sparse** | Storage formats (dense, CSR, LDU) | How does OpenFOAM save 95% memory? |
| **03_fvMatrix_Architecture** | Matrix assembly pipeline | How do `fvm::` operators become matrix coeffs? |
| **04_Linear_Solvers_Hierarchy** | **Solver/preconditioner selection** | Which solver for my equation? |
| **05_Parallel_Linear_Algebra** | Domain decomposition | How do solvers work across processors? |
| **06_Common_Pitfalls** | Convergence debugging | Why is my residual stalling at 1e-3? |
| **07_Summary_and_Exercises** | Practice problems | Apply concepts to real cases |

---

## 7. Key Takeaways

### ✓ Core Concepts

- **Every CFD solve = Ax = b**: Discretization converts PDEs to linear systems solved iteratively
- **Sparse storage is mandatory**: LDU format uses only 5% memory of dense storage for typical 3D meshes
- **Matrix type dictates solver**: Symmetric (pressure/diffusion) → PCG; Non-symmetric (velocity/convection) → PBiCGStab
- **Preconditioners matter more than solvers**: Poor preconditioning can increase iterations by 10x
- **90% of runtime is linear algebra**: Optimizing solver config = faster simulations without code changes

### ⚠️ Common Mistakes

| Mistake | Consequence | Fix |
|---------|-------------|-----|
| Using PCG for velocity | Slow convergence or divergence | Switch to PBiCGStab |
| Neglecting preconditioner | 10x more iterations | Add DIC/DILU or GAMG |
| `relTol` too loose on pressure | Outer loop iterations stall | Tighten to 0.01 |
| `relTol` too tight on temperature | Wasted CPU time | Loosen to 0.1 |

### 🔧 Practical Checklist

Before running a production case:
- [ ] Verify solver type matches equation symmetry (pressure=PCG, velocity=PBiCGStab)
- [ ] Confirm preconditioner is set (never `none` for production)
- [ ] Check `relTol` values (0.01 for p/k/ε/ω, 0.1 for U/T)
- [ ] For >500k cells, consider GAMG for all fields
- [ ] Monitor initial residuals: should drop 10x within 5-10 iterations

---

## 8. Concept Check

<details>
<summary><b>Q1: Why does OpenFOAM use LDU storage instead of dense matrices?</b></summary>

**Answer:** LDU (Lower-Diagonal-Upper) format stores only non-zero coefficients. For a typical 3D finite volume mesh with ~20 neighbors per cell, the matrix is >95% zeros. LDU storage:
- Uses ~5% of the memory required for dense storage
- Enables matrix-vector multiplication in O(N) vs O(N²)
- Makes industrial-scale simulations (millions of cells) possible on workstations
</details>

<details>
<summary><b>Q2: When should you use PCG vs PBiCGStab?</b></summary>

**Answer:**
- **PCG (Preconditioned Conjugate Gradient):** Only for **symmetric matrices**
  - Pressure equation (Poisson-type: ∇²p = ω)
  - Diffusion-dominated transport
  - Why? Faster convergence (requires fewer iterations)
  
- **PBiCGStab (Preconditioned Bi-Conjugate Gradient Stabilized):** For **non-symmetric matrices**
  - Velocity (convection-dominated: ∇·(uU) = ...)
  - Temperature with strong convection
  - Why? Handles asymmetric off-diagonal coefficients from upwind/QUICK schemes
</details>

<details>
<summary><b>Q3: What are the three most common reasons for linear solver divergence?</b></summary>

**Answer:**
1. **Wrong solver type:** Using PCG for non-symmetric velocity equations → fails immediately
2. **No preconditioner:** Solver takes forever, residuals plateau → add DIC/DILU/GAMG
3. **Poor matrix conditioning:** Very high convection (>100:1 convection:diffusion ratio) → use upwind scheme or smaller timestep

**Diagnostic:** Check `solverPerformance` output. If `initialResidual` increases or iterations hit `maxIter`, matrix conditioning is the issue.
</details>

<details>
<summary><b>Q4: How does matrix relaxation work and when is it necessary?</b></summary>

**Answer:** 

**How it works:**
```cpp
TEqn.relax(0.7);  // A_new = 0.7*A_calculated + 0.3*A_old
```
Blends new matrix coefficients with old values to prevent large changes.

**When necessary:**
- **Coupled algorithms:** SIMPLE, PISO (pressure-velocity coupling)
- **High under-relaxation factors:** When `U` relaxation < 0.5
- **Transient simulations:** First few timesteps to stabilize initial conditions

**Why it matters:** Unrelaxed matrices can cause outer loop oscillations in segregated solvers, preventing convergence.
</details>

<details>
<summary><b>Q5: Where in the OpenFOAM case directory do you configure linear solvers?</b></summary>

**Answer:** `system/fvSolution`

**Structure:**
```cpp
solvers
{
    p { solver PCG; preconditioner DIC; ... }    // Pressure equation
    U { solver PBiCGStab; preconditioner DILU; ... }  // Momentum
    T { solver PBiCGStab; ... }                  // Energy
    k { ... }                                    // Turbulence
    epsilon { ... }                              // Turbulence
}
```

**Common tuning parameters:**
- `tolerance`: Absolute convergence (e.g., 1e-06)
- `relTol`: Relative to initial residual (0.01-0.1 typical)
- `maxIter`: Safety limit (hitting this = problem)
</details>

---

## 📖 Further Reading

- **Next:** [01_Introduction.md](01_Introduction.md) — Mathematical foundations of linear algebra in CFD
- **Solver Deep Dive:** [04_Linear_Solvers_Hierarchy.md](04_Linear_Solvers_Hierarchy.md) — Complete solver/preconditioner comparison
- **Practical Debugging:** [06_Common_Pitfalls.md](06_Common_Pitfalls.md) — Residual diagnosis and solver tuning
- **Related Modules:**
  - [Mesh Classes](../04_MESH_CLASSES/00_Overview.md) — How mesh topology creates matrix sparsity
  - [Fields & GeometricFields](../05_FIELDS_GEOMETRICFIELDS/00_Overview.md) — How fields become solution vectors