# Matrices & Linear Algebra - Common Pitfalls

ปัญหาที่พบบ่อยใน Linear Algebra

---

## 1. Solver Selection Errors

### Problem: Wrong Solver for Matrix Type

```cpp
// BAD: Using PCG for non-symmetric matrix
U { solver PCG; }  // Error or slow convergence

// GOOD: Use appropriate solver
U { solver PBiCGStab; preconditioner DILU; }
```

### Quick Guide

| Matrix | Solver |
|--------|--------|
| Pressure (symmetric) | PCG, GAMG |
| Velocity (non-symmetric) | PBiCGStab |
| Scalars | smoothSolver, PCG |

---

## 2. Convergence Issues

### Problem: Not Converging

**Symptoms:**
- Residuals plateau or oscillate
- Solution diverges

**Solutions:**

```cpp
// 1. Reduce relaxation
relaxationFactors
{
    fields { p 0.3; }
    equations { U 0.5; }
}

// 2. Increase iterations
p { maxIter 1000; }

// 3. Use tighter tolerance for final correction
pFinal { $p; relTol 0; }
```

---

## 3. Preconditioner Mismatch

### Problem: Wrong Preconditioner

```cpp
// BAD: DIC for non-symmetric
U { solver PBiCGStab; preconditioner DIC; }

// GOOD: DILU for non-symmetric
U { solver PBiCGStab; preconditioner DILU; }
```

### Preconditioner Guide

| Solver | Preconditioner |
|--------|----------------|
| PCG | DIC, FDIC, GAMG |
| PBiCGStab | DILU, none |
| GAMG | GaussSeidel |

---

## 4. relTol vs tolerance

### Problem: Confusion Between Criteria

```cpp
// tolerance: absolute target
tolerance 1e-6;  // Stop when residual < 1e-6

// relTol: relative reduction
relTol 0.01;  // Stop when residual < 1% of initial
```

### Best Practice

```cpp
p
{
    tolerance   1e-6;   // Absolute floor
    relTol      0.01;   // 100× reduction
}
pFinal
{
    $p;
    relTol      0;      // Force to tolerance
}
```

---

## 5. Matrix Singularity

### Problem: Singular Matrix

**Symptoms:**
```
--> FOAM FATAL ERROR:
request for singular field.
```

**Causes:**
- No reference pressure
- All Neumann BCs
- Poorly conditioned mesh

**Solutions:**

```cpp
// Set reference cell
pRefCell 0;
pRefValue 0;

// In code
p.correctBoundaryConditions();
fvOptions.correct(p);
```

---

## 6. Under-Relaxation Issues

### Problem: Too Much/Little Relaxation

| Symptom | Cause | Fix |
|---------|-------|-----|
| Oscillating | Too little relaxation | Decrease factor |
| Very slow | Too much relaxation | Increase factor |
| Diverging | Unstable | Decrease factor significantly |

### Typical Values

| Field | Relaxation |
|-------|------------|
| p | 0.3-0.5 |
| U | 0.5-0.7 |
| k, ε | 0.5-0.7 |
| T | 0.7-0.9 |

---

## 7. Implicit vs Explicit

### Problem: Instability from Explicit Terms

```cpp
// BAD: Large explicit source (unstable)
fvScalarMatrix TEqn = ... + fvc::Su(largeSource, T);

// GOOD: Use implicit if possible
fvScalarMatrix TEqn = ... + fvm::Sp(coeff, T);
```

### Rule

- **fvm (implicit)**: Stable, goes to matrix diagonal
- **fvc (explicit)**: Can destabilize, use small values

---

## 8. Boundary Contributions

### Problem: Forgetting Boundary Update

```cpp
// BAD: Missing boundary correction
TEqn.solve();
// T boundary may be inconsistent

// GOOD: Correct boundaries
TEqn.solve();
T.correctBoundaryConditions();
```

---

## Quick Troubleshooting

| Problem | Check |
|---------|-------|
| Not converging | Relaxation, solver, BCs |
| Diverging | CFL, mesh quality, BCs |
| Slow | GAMG, mesh, equations |
| Singular | Reference cell, BCs |

---

## Concept Check

<details>
<summary><b>1. PCG ใช้กับ velocity ได้ไหม?</b></summary>

**ไม่ควร** — velocity matrix มักเป็น non-symmetric → ใช้ PBiCGStab
</details>

<details>
<summary><b>2. relTol = 0 หมายความว่าอะไร?</b></summary>

**ไม่ใช้ relative criterion** → converge เมื่อ absolute tolerance เท่านั้น
</details>

<details>
<summary><b>3. ทำไม GAMG ดีสำหรับ large problems?</b></summary>

เพราะ **O(N) complexity** — PCG เป็น O(N²) สำหรับ poorly conditioned
</details>

---

## Related Documents

- **Linear Solvers:** [04_Linear_Solvers_Hierarchy.md](04_Linear_Solvers_Hierarchy.md)
- **fvMatrix:** [03_fvMatrix_Architecture.md](03_fvMatrix_Architecture.md)