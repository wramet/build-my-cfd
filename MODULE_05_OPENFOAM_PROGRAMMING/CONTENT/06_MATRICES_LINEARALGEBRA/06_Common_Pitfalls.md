# Matrices & Linear Algebra - Common Pitfalls

ปัญหาที่พบบ่อยใน Linear Algebra — เรียนจากความผิดพลาดของคนอื่น

> **ทำไมบทนี้สำคัญ?**
> - **Solver issues = #1 cause of divergence** — ปัญหา linear solver เป็นสาเหตุอันดับ 1 ที่ทำให้ simulation แตก (diverge)
> - รู้ traps ที่พบบ่อย → หลีกเลี่ยงได้ → ประหยัดเวลา debug ได้หลายชั่วโมง
> - Debug convergence problems ได้เร็ว — รู้ว่าต้องแก้ที่ solver, preconditioner, หรือ relaxation
> - เชื่อมโยงกับ practical consequences: **stability, convergence speed, solution accuracy**

---

## 🎯 Learning Objectives

หลังจบบทนี้ คุณควรจะสามารถ:
1. **Identify** ปัญหาที่พบบ่อยในการเลือก solver และ preconditioner สำหรับ matrix ประเภทต่างๆ
2. **Diagnose** สาเหตุของ convergence problems จาก residual behavior
3. **Choose** ค่า relaxation factors ที่เหมาะสมสำหรับแต่ละ field
4. **Distinguish** ความแตกต่างระหว่าง `tolerance` และ `relTol` และใช้งานได้อย่างถูกต้อง
5. **Avoid** common pitfalls ในการใช้ implicit vs explicit terms
6. **Troubleshoot** ปัญหา solver divergence ได้อย่างมีระบบ

---

## 1. Solver Selection Errors

### Problem: Wrong Solver for Matrix Type

**🔍 Why This Matters**
- Symmetric matrices (pressure) ต้องใช้ solver ที่ optimize สำหรับ symmetric structure
- Non-symmetric matrices (velocity) ต้องการ solver ที่รองรับ general matrices
- ใช้ solver ผิดประเภท → **convergence ช้า** หรือ **ไม่ converge เลย**

```cpp
// ❌ BAD: Using PCG for non-symmetric matrix
// velocity matrix มักเป็น non-symmetric เพราะ convection terms
U 
{
    solver          PCG;  // ผิด! PCG สำหรับ symmetric เท่านั้น
    preconditioner  DIC;
    tolerance       1e-06;
    relTol          0.01;
}

// ✅ GOOD: Use appropriate solver for matrix type
U
{
    solver          PBiCGStab;  // ถูก! สำหรับ non-symmetric
    preconditioner  DILU;
    tolerance       1e-05;
    relTol          0.1;
}
```

**💡 CFD Insight:**
- **Pressure equation** (Poisson-type) → symmetric → PCG/GAMG เร็วกว่า 2-5×
- **Velocity equation** (convection-diffusion) → non-symmetric → PBiCGStab จำเป็น
- ผิด solver → แก้ด้วยการ **increase iterations** แต่ก็ยังช้า/ไม่ converge → เสียเวลาคำนวณ

### Quick Guide

| Matrix Type | Equation Example | Solver | Preconditioner | Why? |
|-------------|------------------|--------|----------------|------|
| Pressure (symmetric) | ∇²p = source | PCG, GAMG | DIC, FDIC | Symmetric matrix → efficient |
| Velocity (non-symmetric) | ∂U/∂t + U·∇U = ... | PBiCGStab | DILU | Convection breaks symmetry |
| Scalars (often symmetric) | ∂T/∂t = α∇²T | smoothSolver, PCG | DIC | Diffusion-dominated → symmetric |
| Turbulence (mixed) | k-ε equations | PBiCGStab, smoothSolver | DILU, DIC | Depends on convection/diffusion |

---

## 2. Convergence Issues

### Problem: Not Converging

**🔍 Why This Matters**
- Residuals plateau → **solution ไม่ถูกต้อง** → CFD results ไว้ไม่ได้
- Residuals oscillate → **instability** → อาจ diverge ใน timestep ต่อๆ ไป
- เสียเวลาคำนวณหลายชั่วโมงแต่ได้ผลลัพธ์ผิด

**Symptoms & Diagnosis:**

| Residual Pattern | Cause | Practical Impact |
|------------------|-------|------------------|
| **Plateau** (ลาบช้าๆ) | Solver ไม่แรงพอ / tolerance หลวม | ใช้เวลานาน → **ไม่คุ้มค่า** |
| **Oscillation** (สั่น) | Relaxation มากเกินไป / coupling แรง | **Instability** → อาจ diverge |
| **Spike** (แล้วลด) | Initial guess แย่ / transient change | อาจโอK ถ้าลงที่เดิม |
| **Diverge** (พุ่ง) | BC ผิด / mesh แย่ / relaxation น้อยไป | **Simulation fail** → เสียเวลา |

**Solutions (in `system/fvSolution`):**

```cpp
// Solution 1: Reduce relaxation factors
// → เพิ่ม stability แต่ลด convergence speed
relaxationFactors
{
    fields
    {
        p       0.3;    // Default: 0.3 → ลดเป็น 0.2 ถ้า oscillate
        p_rgh   0.3;
    }
    equations
    {
        U       0.5;    // Default: 0.5 → ลดเป็น 0.3 ถ้า diverge
        "(k|epsilon|omega)" 0.5;
    }
}

// Solution 2: Increase solver iterations
// → Allow more iterations ต่อ timestep
solvers
{
    p
    {
        solver          GAMG;
        tolerance       1e-06;
        relTol          0.01;
        maxIter         1000;  // Default: 1000 → เพิ่มถ้า plateau
    }
}

// Solution 3: Use tighter tolerance for final correction
// → บังคับ converge จริงใน final iteration
pFinal
{
    $p;                    // Inherit settings from p
    relTol          0;     // ไม่ใช้ relTol → converge จนถึง tolerance
    tolerance       1e-06; // Absolute convergence
}
```

**💡 CFD Insight:**
- **Tight relaxation** (0.2-0.3) → **stable แต่ช้า** → ใช้ใน transient หรือ complex physics
- **Loose relaxation** (0.7-0.9) → **เร็วแต่เสี่ยง** → ใช้ใน steady-state หรือ well-initialized cases
- Trade-off: **stability vs speed** → ปรับตาม case และ convergence behavior

---

## 3. Preconditioner Mismatch

### Problem: Wrong Preconditioner

**🔍 Why This Matters**
- Preconditioner → **scale matrix** ให้ solver ทำงานเร็วขึ้น 2-10×
- ใช้ผิดประเภท → **preconditioning ไม่มีประสิทธิภาพ** หรือ **unstable**
- Good preconditioning → ลด iterations ได้ถึง 80%

```cpp
// ❌ BAD: DIC for non-symmetric solver
// DIC = Diagonal Incomplete Cholesky → สำหรับ symmetric ONLY
U
{
    solver          PBiCGStab;  // Non-symmetric
    preconditioner  DIC;        // ❌ ผิด! DIC สำหรับ symmetric
}

// ✅ GOOD: DILU for non-symmetric
// DILU = Diagonal Incomplete LU → สำหรับ general matrices
U
{
    solver          PBiCGStab;  // Non-symmetric
    preconditioner  DILU;       // ✅ ถูก! เข้าคู่กัน
}
```

### Preconditioner Guide

| Solver | Matrix Type | Preconditioner | Best For | Avoid |
|--------|-------------|----------------|----------|-------|
| **PCG** | Symmetric | DIC, FDIC, GAMG | Pressure, diffusion | Heavy convection |
| **PBiCGStab** | Non-symmetric | DILU, none | Velocity, turbulence | - |
| **GAMG** | Symmetric | GaussSeidel | Large pressure problems | Small problems |
| **smoothSolver** | Any | none | Smoothing, bad conditioned | Final convergence |

**💡 CFD Insight:**
- **GAMG preconditioning** → **O(N) complexity** → ดีสุดสำหรับ large meshes (>1M cells)
- **DIC/DILU** → **cheap แต่จำกัดประสิทธิภาพ** → ดีสำหรับ small/medium problems
- **No preconditioner** → ช้าลง 3-5× แต่ **stable** → ใช้เมื่อ preconditioning ทำให้ diverge

---

## 4. relTol vs tolerance

### Problem: Confusion Between Convergence Criteria

**🔍 Why This Matters**
- `tolerance` = **absolute convergence** → ความแม่นยำของ solution
- `relTol` = **relative convergence** → **speed** ของการคำนวณ
- ตั้งค่าผิด → **convergence ช้าเกินไป** (เสียเวลา) หรือ **convergence ไม่พอ** (solution ผิด)

```cpp
// tolerance: absolute convergence criterion
// → หยุดเมื่อ residual < tolerance (absolute)
tolerance 1e-06;  // Stop when: ||r|| < 1e-06

// relTol: relative convergence criterion
// → หยุดเมื่อ residual ลดลงจากค่าเริ่มต้น
relTol 0.01;      // Stop when: ||r||/||r0|| < 0.01 (1% of initial)
```

**🎯 How They Work Together:**

```cpp
p
{
    solver          GAMG;
    tolerance       1e-06;   // Absolute floor (ต้องการ)
    relTol          0.01;    // Relative reduction (speed)
    
    // Solver หยุดเมื่อ:
    // 1. residual < 1e-06 (absolute) → MUST meet
    // 2. OR residual < 1% of initial (relative) → EARLY exit
    // → ใช้ relTol เพื่อ speed up ใน timestep แรกๆ
}

pFinal
{
    $p;                    // Inherit tolerance 1e-06
    relTol          0;      // ❌ No relative criterion
    
    // pFinal หยุดเมื่อ:
    // residual < 1e-06 ONLY → MUST converge to absolute tolerance
    // → ใช้ใน final iteration ของ timestep เพื่อความแม่นยำ
}
```

### Best Practice

| Application | tolerance | relTol | Why? |
|-------------|-----------|-------|------|
| **Transient** (initial) | 1e-5 | 0.01 | Speed สำคัญ → relTol ช่วย |
| **Transient** (final timestep) | 1e-6 | 0 | Accuracy สำคัญ → absolute only |
| **Steady-state** | 1e-8 | 0.001 | Tight tolerance → final accuracy |
| **Debugging** | 1e-4 | 0.1 | Loose → fast iterations |

**💡 CFD Insight:**
- **relTol > 0** → **speed up 2-5×** แต่ solution อาจไม่ fully converged
- **relTol = 0** → **guarantee convergence** แต่ **slow down 3-10×**
- Strategy: ใช้ **loose relTol** ใน transient iterations → **tight relTol=0** ใน final

---

## 5. Matrix Singularity

### Problem: Singular Matrix

**🔍 Why This Matters**
- Singular matrix → **no unique solution** → solver **crash** หรือ **produce garbage**
- เป็นปัญหา **#1** สำหรับ pressure equation (pure Neumann BCs)
- เกิดจาก **mathematical inconsistency** → ต้องแก้ที่ source, ไม่ใช่ solver settings

**Symptoms:**
```
--> FOAM FATAL ERROR:
request for singular field.

From function fvMatrix<Type>::solve()
in file fvMatrix.C at line XXX
```

**Root Causes:**

| Cause | Mathematical Reason | Practical Example |
|-------|---------------------|-------------------|
| **No reference pressure** | Pure Neumann → infinite solutions | All walls (zeroGradient) |
| **All Neumann BCs** | Matrix singular → det = 0 | No fixed value BC |
| **Poorly conditioned mesh** | Near-singular → high condition number | High skewness/non-orthogonality |
| **Zero equation coefficients** | Empty rows in matrix | transportProperties ผิด |

**Solutions:**

```cpp
// Solution 1: Set reference cell (MOST COMMON)
// → บังคับ solution uniqueness สำหรับ pure Neumann
// In system/fvSolution:
PIMPLE
{
    pRefCell        0;       // Cell index สำหรับ reference
    pRefValue       0;       // Reference value (gauge pressure)
}

// Solution 2: Fix one boundary (if applicable)
// → ใช้ fixedValue แทน zeroGradient ที่บาง boundary
p
{
    type            fixedValue;
    value           uniform 0;  // Reference pressure
}

// Solution 3: Improve mesh quality
// → ลด condition number
// In system/controlDict:
application     topoSetDesigner;  // Remove bad cells
meshQualityDict
{
    maxNonOrthogonality 70;
    maxSkewness          0.5;
}

// Solution 4: Check equation formulation
// In solver code / boundary conditions:
p.correctBoundaryConditions();  // Update BCs before solve
fvOptions.correct(p);            // Apply source terms
```

**💡 CFD Insight:**
- **Pure Neumann BCs** → **pressure defined up to constant** → ต้องมี reference
- **Singular matrix** → **solver crash** → **ไม่ใช่** convergence problem
- Prevention: **always set `pRefCell`** ถ้ามี zeroGradient BCs ทุกที่

---

## 6. Under-Relaxation Issues

### Problem: Too Much/Little Relaxation

**🔍 Why This Matters**
- Under-relaxation → **stability** ใน **coupled equations** (pressure-velocity)
- ค่าผิด → **oscillation** (ไม่น้อยไป) หรือ **stagnation** (ไม่มากไป)
- Trade-off โดยตรงระหว่าง **stability** และ **convergence speed**

**Symptoms & Diagnosis:**

| Symptom | Residual Plot | Cause | Fix |
|---------|---------------|-------|-----|
| **Oscillating residuals** | 📈📉📈📉 (regular pattern) | Too little relaxation → unstable coupling | **Decrease** factor |
| **Very slow convergence** | 📈___ (flat line) | Too much relaxation → over-damped | **Increase** factor |
| **Diverging residuals** | 📈↑↑↑ (spike up) | Highly unstable | **Decrease** factor significantly |
| **Stable plateau** | 📈→ (flat) | Under-relaxed but stable | OK ถ้าช้าๆ |

### Typical Relaxation Values

| Field | Physics | Typical Range | Aggressive | Conservative |
|-------|---------|---------------|------------|--------------|
| **p** (pressure) | Highly coupled | 0.3-0.5 | 0.5 | 0.2 |
| **p_rgh** | Buoyancy coupled | 0.3-0.5 | 0.5 | 0.2 |
| **U** (velocity) | Convection-dominated | 0.5-0.7 | 0.7 | 0.3 |
| **k, ε, ω** (turbulence) | Non-linear source | 0.5-0.7 | 0.7 | 0.3 |
| **T** (temperature) | Scalar transport | 0.7-0.9 | 0.9 | 0.5 |

**💡 CFD Insight:**
- **Low relaxation** (0.2-0.3) → **stable แต่ slow** → ใช้ใน **complex physics** (multiphase, combustion)
- **High relaxation** (0.7-0.9) → **fast แต่ risky** → ใช้ใน **well-initialized** หรือ **simple physics**
- **Strategy:** Start **conservative** → ค่อยๆ increase ถ้า stable

---

## 7. Implicit vs Explicit

### Problem: Instability from Explicit Terms

**🔍 Why This Matters**
- **Implicit (fvm)** → **unconditionally stable** → contribution ไป matrix diagonal
- **Explicit (fvc)** → **conditionally stable** → source term เป็น external force
- ใช้ explicit terms ใหญ่ๆ → **instability** → **divergence**

```cpp
// ❌ BAD: Large explicit source (unstable)
// fvc::Su = explicit source → ไม่ขึ้นกับ T → สามารถ explode
fvScalarMatrix TEqn = 
    fvm::ddt(T)
  + fvm::div(phi, T)
  - fvm::laplacian(DT, T)
  + fvc::Su(largeSource, T);  // ❌ Explicit → อาจ unstable

// ✅ GOOD: Use implicit if possible
// fvm::Sp = implicit source → ขึ้นกับ T → matrix diagonal แข็งขึ้น
fvScalarMatrix TEqn = 
    fvm::ddt(T)
  + fvm::div(phi, T)
  - fvm::laplacian(DT, T)
  + fvm::Sp(coeff, T);  // ✅ Implicit → stable
```

### Rule of Thumb

| Term | Type | Stability | When to Use |
|------|------|-----------|-------------|
| **fvm::Sp(coef, T)** | Implicit | ✅ Unconditionally stable | Linear source (∝ T) |
| **fvc::Su(source, T)** | Explicit | ⚠️ Conditionally stable | Constant source (indepedent of T) |
| **fvm::SuSp(coef, T)** | Hybrid | ✅ Stable (auto-switch) | coef อาจเป็นบวก/ลบ |

**💡 CFD Insight:**
- **Implicit terms** → **matrix dominance** → **better conditioning** → **faster convergence**
- **Explicit terms** → **CFL constraint** → **smaller timesteps** → **slower simulation**
- Rule: **Always use `fvm`** ถ้า term ขึ้นกับ unknown variable

---

## 8. Boundary Contributions

### Problem: Forgetting Boundary Update

**🔍 Why This Matters**
- Solver solve → **internal field only** → **boundary conditions ไม่ update**
- ลืม update → **boundary inconsistent** กับ internal field → **wrong fluxes**
- Impact: **mass conservation violation**, **wrong gradients**, **instability**

```cpp
// ❌ BAD: Missing boundary correction
TEqn.solve();  // Solve internal field ONLY
// T.boundaryField() ยังเก่า → inconsistent กับ internal T

// ✅ GOOD: Correct boundaries after solve
TEqn.solve();
T.correctBoundaryConditions();  // Update BCs → consistent fluxes

// ✅ ALSO GOOD: Use in loop
while (simple.loop())
{
    // Solve equations
    while (simple.correctNonOrthogonal())
    {
        TEqn.solve();
    }
    
    // Update ALL boundaries
    T.correctBoundaryConditions();
    U.correctBoundaryConditions();
    p.correctBoundaryConditions();
}
```

**💡 CFD Insight:**
- **Boundary update** → **gradient BCs** (zeroGradient, fixedGradient) ต้องใช้ internal field
- **Forgotten update** → **wrong wall heat flux**, **wrong velocity gradients**, **mass leak**
- Rule: **always call `correctBoundaryConditions()`** หลังจาก `.solve()` ถ้ามี gradient BCs

---

## Quick Troubleshooting

**🔍 Diagnostic Flowchart:**

| Problem | Residual Sign | Check First | Then Check |
|---------|---------------|-------------|------------|
| **Not converging** | Plateau at 1e-4 | relaxation factors (lower) | solver settings (increase iterations) |
| **Diverging** | Spike to 1e+2 | CFL number (reduce dt) | mesh quality (check skewness) |
| **Very slow** | Linear decrease | GAMG solver (faster) | mesh resolution (maybe too fine) |
| **Oscillating** | Regular 📈📉 pattern | relaxation (lower) | BC consistency |
| **Singular matrix** | Crash with error | reference cell (pRefCell) | BC types (need fixedValue) |
| **Wrong results** | Converged but unphysical | boundary update (forgot?) | source terms (check signs) |

---

## 🎯 Key Takeaways

1. **Solver Selection Matters**
   - Symmetric matrices (pressure) → **PCG/GAMG**
   - Non-symmetric matrices (velocity) → **PBiCGStab**
   - Wrong solver → convergence ช้า หรือไม่ converge เลย

2. **Convergence Diagnostics**
   - **Residual plot** บอกทุกอย่าง: oscillate → relaxation issues, plateau → solver weakness
   - ตั้งค่า `tolerance` (accuracy) และ `relTol` (speed) อย่างรู้ความ

3. **Preconditioning = Speed**
   - Good preconditioner → **reduce iterations 2-10×**
   - Match preconditioner กับ solver type (DIC→PCG, DILU→PBiCGStab)

4. **Relaxation = Stability**
   - **Low relaxation (0.2-0.3)** → stable แต่ช้า → ใช้ใน complex physics
   - **High relaxation (0.7-0.9)** → เร็วแต่เสี่ยง → ใช้ใน well-initialized cases
   - Trade-off โดยตรง: stability vs speed

5. **Avoid Explicit Terms**
   - **fvm (implicit)** → stable, ใช้ได้เสมอ สำหรับ linear terms
   - **fvc (explicit)** → เสี่ยง instability, ใช้เฉพาะ constant sources
   - Rule: **prefer `fvm` over `fvc`** ถ้าเป็นไปได้

6. **Boundary Consistency**
   - Solver solve → **internal field only**
   - **Always call** `correctBoundaryConditions()` หลังจาก `.solve()`
   - ลืม → wrong fluxes → mass conservation violation

7. **Singular Matrix Prevention**
   - **Pure Neumann BCs** → **must set `pRefCell`**
   - **Matrix singularity** → **solver crash** (not convergence issue)
   - Prevention: check BCs และ mesh quality ก่อน run

---

## 🧠 Concept Check

<details>
<summary><b>1. PCG ใช้กับ velocity ได้ไหม? ทำไม?</b></summary>

**ไม่ควร** — velocity matrix มักเป็น **non-symmetric** เพราะ convection terms (∂U/∂t + U·∇U) → ใช้ **PBiCGStab** แทน

**Impact:** ถ้าใช้ PCG → convergence ช้ามาก หรือไม่ converge เลย เพราะ PCG optimize สำหรับ symmetric matrices (เช่น pressure Poisson equation)
</details>

<details>
<summary><b>2. relTol = 0 หมายความว่าอะไร? ใช้เมื่อไร?</b></summary>

**ไม่ใช้ relative criterion** → converge เมื่อ **absolute tolerance เท่านั้น**

**ใช้เมื่อ:** ต้องการ **guaranteed convergence** ถึงความแม่นยำที่ตั้งไว้ เช่น:
- **Final timestep** ใน transient simulation (ด้วย `pFinal`)
- **Steady-state** ที่ต้องการ final accuracy

**Trade-off:** ช้าลง 3-10× แต่มั่นใจว่า converged จริง
</details>

<details>
<summary><b>3. ทำไม GAMG ดีสำหรับ large problems?</b></summary>

เพราะ **O(N) complexity** แทนที่จะเป็น O(N²) เหมือน PCG สำหรับ poorly conditioned matrices

**Mechanism:** GAMG ใช้ **multigrid** → solve บน coarse grids → **fast convergence** สำหรับ large systems

**Impact:** สำหรับ meshes >1M cells → GAMG เร็วกว่า PCG **5-20×** สำหรับ pressure equation
</details>

<details>
<summary><b>4. ทำไมต้อง correctBoundaryConditions() หลังจาก solve()?</b></summary>

เพราะ `.solve()` **updates internal field ONLY** → boundary conditions ยังคงค่าเดิม

**Consequences:**
- **Gradient BCs** (zeroGradient, fixedGradient) ใช้ internal field คำนวณ → ถ้า internal เปลี่ยน แต่ boundary ไม่ update → **inconsistent**
- **Wrong fluxes** → **mass conservation violation** → **instability**

**Example:** wall heat flux คำนวณจาก `dT/dn` ที่ boundary → ถ้า T ภายในเปลี่ยน แต่ BC ไม่ update → flux ผิด
</details>

<details>
<summary><b>5. Implicit vs Explicit terms: อะไรคือ trade-off?</b></summary>

| Aspect | Implicit (fvm) | Explicit (fvc) |
|--------|----------------|----------------|
| **Stability** | ✅ Unconditionally stable | ⚠️ Conditionally stable (CFL-limited) |
| **Speed** | ช้าขึ้น per iteration (matrix solve) | เร็วขึ้น per iteration (no matrix) |
| **Convergence** | เร็วขึ้น (better conditioning) | ช้าลง (smaller timesteps) |
| **When to use** | Linear terms (∝ variable) | Constant sources (independent) |

**Rule:** **Prefer `fvm`** ถ้า term ขึ้นกับ unknown variable → **stable** และ **faster convergence**
</details>

<details>
<summary><b>6. Under-relaxation คืออะไร? ทำไมต้องใช้?</b></summary>

**Under-relaxation** = damping factor สำหรับ **coupled equations** (pressure-velocity coupling)

**Mechanism:**
```
φ_new = φ_old + α · Δφ
```
- **α = 1** → no relaxation (full update)
- **α < 1** → under-relaxed (partial update) → **more stable**

**Why needed:**
- **Pressure-velocity coupling** แรงมาก → full update อาจ **overshoot** → **oscillation** → **divergence**
- **Under-relaxation** → **damp oscillations** → **stable convergence**

**Trade-off:** ต่ำ → stable แต่ช้า | สูง → เร็ว แต่เสี่ยง
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

### Prerequisites
- **Linear Solvers:** [04_Linear_Solvers_Hierarchy.md](04_Linear_Solvers_Hierarchy.md) — ศึกษา solver types และ preconditioners แบบละเอียด
- **fvMatrix:** [03_fvMatrix_Architecture.md](03_fvMatrix_Architecture.md) — ทำความเข้าใจ matrix assembly และ lduMatrix

### Related Topics
- **Solver Configuration:** [04_Linear_Solvers_Hierarchy.md](04_Linear_Solvers_Hierarchy.md) — วิธีเลือก solver ที่เหมาะสม
- **Field Boundaries:** [05_Fields_GeometricFields.md](../05_FIELDS_GEOMETRICFIELDS/05_Field_Lifecycle.md) — boundary condition updates
- **Mesh Quality:** [04_mesh_Classes.md](../04_MESH_CLASSES/04_polyMesh.md) — mesh conditioning และ singular matrices

### Practical Resources
- **OpenFOAM User Guide:** Section 4.4 (Solution Schemes)
- **`$FOAM_TUTORIALS/incompressible/simpleFoam/`:** ตัวอย่าง fvSolution settings
- **`$FOAM_ETC/cfdTools/general/solvers/`:** source code สำหรับ solver implementations

---

## 🔧 Practical Exercise

**Task:** Debug ปัญหา convergence ใน case นี้

**Scenario:**
- Case: `simpleFoam` (steady-state, turbulent)
- Mesh: 500k cells, max skewness = 0.6 (OK)
- BCs: velocity inlet, pressure outlet (zeroGradient)
- Problem: **Initial residuals oscillate** between 1e-3 and 1e-4, never converge

**Current Settings:**
```cpp
// system/fvSolution
solvers
{
    p
    {
        solver          GAMG;
        tolerance       1e-06;
        relTol          0.1;
    }
    U
    {
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-05;
        relTol          0.1;
    }
}

relaxationFactors
{
    fields { p 0.3; }
    equations { U 0.7; }
}
```

**Questions:**
1. **Diagnose:** ทำไม residuals oscillate? (Hint: look at relaxation factors)
2. **Propose fix:** ปรับ settings อย่างไร? (Hint: try lower relaxation)
3. **Explain:** ทำไมการปรับนี้ช่วย? (Hint: stability vs speed)

<details>
<summary><b>Click for Solution</b></summary>

**Diagnosis:**
- **U relaxation = 0.7** → **too high** สำหรับ turbulent flow → coupling แรง → oscillation
- **p relaxation = 0.3** → OK แต่อาจต้องลดไปอีก ถ้า U ยัง oscillate

**Proposed Fix:**
```cpp
relaxationFactors
{
    fields { p 0.2; }      // Decrease from 0.3 → more stability
    equations { U 0.5; }   // Decrease from 0.7 → damp oscillations
}

solvers
{
    p
    {
        relTol          0.05;  // Decrease from 0.1 → tighter convergence
    }
    U
    {
        maxIter         500;   // Increase from default 100 → more iterations
    }
}
```

**Explanation:**
- **Lower relaxation** → **damp pressure-velocity coupling** → **reduce oscillations**
- **Tighter relTol** → **better convergence per timestep** → **fewer outer iterations**
- **More iterations** → **compensate for slower convergence per iteration**

**Expected Result:** Residuals converge smoothly ถึง 1e-5 within 100 iterations
</details>