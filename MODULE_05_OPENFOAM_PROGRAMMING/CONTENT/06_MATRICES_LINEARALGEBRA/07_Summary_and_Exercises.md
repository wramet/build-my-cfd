# Learning Objectives

By the end of this section, you will be able to:
1. **Select appropriate linear solvers** for different equation types in OpenFOAM based on matrix properties (symmetric vs. non-symmetric, SPD)
2. **Configure solver parameters** in `system/fvSolution` including tolerance, relative tolerance, and preconditioners to balance convergence speed and stability
3. **Distinguish between fvm and fvc operators** and their effects on matrix assembly (diagonal vs. off-diagonal vs. source terms)
4. **Apply under-relaxation strategies** to stabilize non-linear iterations in coupled problems
5. **Diagnose and fix convergence issues** by adjusting solver settings and relaxation factors

---

# Prerequisites

> [!IMPORTANT] **Before starting this section, ensure you have completed:**
> - **[03_fvMatrix_Architecture.md](03_fvMatrix_Architecture.md)** - Understanding of fvMatrix internal structure, LDU addressing, and coefficient storage
> - **[02_Dense_vs_Sparse_Matrices.md](02_Dense_vs_Sparse_Matrices.md)** - Knowledge of sparse matrix formats and OpenFOAM's lduMatrix implementation
> - **[04_Linear_Solvers_Hierarchy.md](04_Linear_Solvers_Hierarchy.md)** - Familiarity with Krylov subspace methods, preconditioners, and multigrid techniques

**Key Concepts You Should Know:**
- Matrix properties: Symmetric Positive Definite (SPD), non-symmetric, diagonally dominant
- Krylov methods: Conjugate Gradient (CG), BiCGStab, GMRES
- Preconditioning: Jacobi, DIC, DILU, GAMG
- Discretization: implicit (fvm) vs. explicit (fvc) operators

---

# Matrices & Linear Algebra - Summary and Exercises

สรุปและแบบฝึกหัด Linear Algebra ใน OpenFOAM

> [!TIP] **ทำไม Linear Algebra สำคัญใน OpenFOAM?**
> **Linear Algebra** เป็นหัวใจของการแก้สมการพาร์เทียลดิฟเฟอเรนเชียล (PDE) ใน CFD ทุกประเภท ไม่ว่าจะเป็น การไหลของไหล (fluid flow), การถ่ายเทความร้อน (heat transfer), หรือการละลายของไอเสีย (turbulence) เมื่อเรา **discretize** สมการบน mesh จะได้รับ **system of linear equations** ในรูปแบบ $[A][x] = [b]$
>
> **การเลือก solver ที่เหมาะสม** และ **การตั้งค่า tolerance** ส่งผลโดยตรงต่อ:
> - **Stability:** การทำงานที่เสถียรของ simulation (ไม่ explode)
> - **Convergence speed:** เวลาที่ใช้ในการคำนวณ (fast vs slow)
> - **Accuracy:** ความแม่นยำของคำตอบ
>
> > [!NOTE] **📂 OpenFOAM Context**
> > ส่วนนี้เกี่ยวข้องกับ **Linear Solver Configuration** ใน OpenFOAM case
> > - **File:** `system/fvSolution`
> > - **Keywords:** `solvers`, `solver`, `preconditioner`, `tolerance`, `relTol`
> > - **Purpose:** กำหนดว่าแต่ละ field (p, U, T, etc.) จะใช้ solver แบบไหนในการแก้ system of linear equations
>
> **ตัวอย่างการใช้งาน:**
> - `PCG` → สำหรับสมการ symmetric (pressure)
> - `PBiCGStab` → สำหรับสมการ non-symmetric (velocity)
> - `GAMG` → สำหรับ large-scale problems (เร็วกว่า PCG ในกรณี mesh ใหญ่)

---

## Summary

### fvMatrix Structure

> [!NOTE] **📂 OpenFOAM Context**
> โครงสร้าง `fvMatrix` เป็นฐานข้อมูลหลักที่เก็บ coefficients ของ linear system ที่เกิดจาก discretization
> - **Source:** `src/finiteVolume/fvMatrices/fvMatrix/fvMatrix.H`
> - **Storage:** LDU format (Lower-Diagonal-Upper) เพื่อประหยัดหน่วยความจำ
> - **Access:** `source()`, `diag()`, `lower()`, `upper()` methods สำหรับ debugging
>
> **การใช้งานจริง:**
> - เมื่อเขียน custom solver → ตรวจสอบ `matrix.source()` เพื่อดู RHS terms
> - เมื่อมีปัญหา convergence → ตรวจสอบ `matrix.diag()` เพื่อดู diagonal dominance

```cpp
template<class Type>
class fvMatrix
{
    GeometricField<Type, fvPatchField, volMesh>& psi_;  // Solution field
    scalarField& diag_;   // Diagonal coefficients
    scalarField& upper_;  // Upper triangle
    scalarField& lower_;  // Lower triangle
    Field<Type> source_;  // RHS
};
```

### Key Classes

| Class | Purpose | Use Case |
|-------|---------|----------|
| `fvScalarMatrix` | Matrix for scalar equations | Temperature (T), pressure (p), turbulence (k, ε) |
| `fvVectorMatrix` | Matrix for vector equations | Velocity (U), displacement (U in solid mechanics) |
| `lduMatrix` | Lower-diagonal-upper storage | Base class for all sparse matrices in OpenFOAM |

---

## Linear Solvers

> [!NOTE] **📂 OpenFOAM Context**
> ส่วนนี้เกี่ยวข้องกับ **Linear Solver Configuration** ใน OpenFOAM case
> - **File:** `system/fvSolution`
> - **Keywords:** `solvers`, `solver`, `preconditioner`, `tolerance`, `relTol`
> - **Purpose:** กำหนดว่าแต่ละ field (p, U, T, etc.) จะใช้ solver แบบไหนในการแก้ system of linear equations
>
> **ตัวอย่างการใช้งาน:**
> - `PCG` → สำหรับสมการ symmetric (pressure)
> - `PBiCGStab` → สำหรับสมการ non-symmetric (velocity)
> - `GAMG` → สำหรับ large-scale problems (เร็วกว่า PCG ในกรณี mesh ใหญ่)

| Solver | Algorithm | Matrix Type | Best For | Complexity |
|--------|-----------|-------------|----------|------------|
| `PCG` | Preconditioned Conjugate Gradient | Symmetric (SPD) | Pressure, scalar transport | O(N√κ) |
| `PBiCGStab` | Preconditioned Bi-Conjugate Gradient Stabilized | Non-symmetric | Velocity, momentum equations | O(N²) worst case |
| `GAMG` | Geometric-Algebraic Multigrid | Both (best for SPD) | Large problems (>1M cells) | O(N) |
| `smoothSolver` | Jacobi/Gauss-Seidel smoothing | Both | Preconditioning, simple problems | O(N) per iteration |

**Key:**
- **SPD** = Symmetric Positive Definite
- **κ** = Condition number (ratio of largest to smallest eigenvalue)
- **N** = Number of unknowns

### Configuration Example

```cpp
// system/fvSolution
solvers
{
    p
    {
        solver          PCG;            // Preconditioned Conjugate Gradient
        preconditioner  DIC;            // Diagonal Incomplete Cholesky
        tolerance       1e-06;          // Absolute residual tolerance
        relTol          0.01;           // Relative tolerance (1% reduction)
        minIter         0;              // Minimum iterations
        maxIter         1000;           // Maximum iterations
    }

    U
    {
        solver          PBiCGStab;      // For non-symmetric systems
        preconditioner  DILU;           // Diagonal Incomplete LU
        tolerance       1e-05;
        relTol          0.1;            // Higher for momentum (10%)
        minIter         0;
        maxIter         1000;
    }

    T
    {
        solver          GAMG;           // Multigrid for large meshes
        preconditioner  DICGaussSeidel;
        tolerance       1e-06;
        relTol          0.05;
        nCellsInCoarsestLevel  10;      // Coarsening parameters
        nPreSweeps      0;
        nPostSweeps     2;
        cacheAgglomeration on;
    }
}
```

**Practical Guidelines:**
- **Pressure (p):** Always SPD → Use `PCG` or `GAMG` for large meshes
- **Velocity (U):** Advection makes it non-symmetric → Use `PBiCGStab`
- **Scalars (T, k, ε):** Usually symmetric → Use `PCG` unless strong convection → `PBiCGStab`
- **relTol:** 0.01 for tight convergence, 0.1 for loose (faster but less accurate)
- **tolerance:** Should be 1-2 orders of magnitude smaller than final convergence target

---

## Exercise 1: Matrix Assembly - Understanding fvm vs fvc

> [!NOTE] **📂 OpenFOAM Context**
> ส่วนนี้เกี่ยวข้องกับ **Matrix Assembly** ซึ่งเป็นกระบวนการสร้าง matrix จาก discretized PDE
> - **Files:**
>   - `src/finiteVolume/fvMatrices/` → โค้ดต้นฉบับของ `fvm::` และ `fvc::`
>   - `system/fvSchemes` → กำหนด discretization schemes (`divSchemes`, `laplacianSchemes`)
> - **Keywords:** `fvm::div`, `fvm::laplacian`, `fvm::ddt`, `fvc::grad`, `fvc::Su`
> - **Purpose:** เข้าใจว่าแต่ละ operator ใส่ค่าใน matrix ตรงไหน (diagonal vs off-diagonal)
>
> **ความสำคัญ:** การเข้าใจ matrix assembly ช่วยให้เขียน custom solver หรือปรับแต่ง equation ได้ถูกต้อง

### Task

วิเคราะห์การประกอบ matrix จาก energy equation ต่อไปนี้:

```cpp
// Energy equation: dT/dt + div(phi, T) = div(alpha*grad(T)) + S
fvScalarMatrix TEqn
(
    fvm::ddt(T)                    // Time derivative: implicit
  + fvm::div(phi, T)               // Convection: implicit
 ==
    fvm::laplacian(alpha, T)       // Diffusion: implicit
  + fvc::Su(source, T)             // Source term: explicit
);
```

### Questions

1. **`fvm::ddt(T)` ใส่ค่าใน matrix ตรงไหน?**
   - Diagonal หรือ off-diagonal?
   - เพราะอะไร?
   - **Hint:** ดูรูปแบบ backward Euler: $\frac{T^{n+1}_P - T^n_P}{\Delta t}$

2. **`fvm::div(phi, T)` สร้าง off-diagonal terms อย่างไร?**
   - Upwind scheme ใส่ค่าอะไรใน upper/lower?
   - ทำไม convection เป็น off-diagonal?
   - **Hint:** Flux ระหว่าง neighbor cells

3. **`fvc::Su(source, T)` ต่างจาก `fvm::Sp(source, T)` อย่างไร?**
   - `Su` = explicit source → ไปที่ RHS (source_)
   - `Sp` = implicit source → ไปที่ diagonal (เพื่อ stability)
   - เมื่อไหร่ควรใช้อันไหน?

4. **ถ้าเปลี่ยน `fvm::div(phi, T)` เป็น `fvc::div(phi, T)` จะเกิดอะไรขึ้น?**
   - Matrix structure เปลี่ยนอย่างไร?
   - Stability ลดลงหรือไม่?
   - **Hint:** Explicit vs. Implicit treatment

### Advanced Challenge

เขียน code snippet ที่ print ค่า diagonal และ source ของ TEqn หลังจาก assembly:

```cpp
TEqn.solve();

Info << "Diagonal range: " 
     << min(TEqn.diag()) << " to " 
     << max(TEqn.diag()) << endl;

Info << "Source range: "
     << min(TEqn.source()) << " to "
     << max(TEqn.source()) << endl;
```

---

## Exercise 2: Solver Selection Strategy

> [!NOTE] **📂 OpenFOAM Context**
> ส่วนนี้เกี่ยวข้องกับ **Solver Selection Strategy** ในการตั้งค่า case
> - **File:** `system/fvSolution`
> - **Keywords:** `solvers`, `solver` (PCG, PBiCGStab, GAMG), `preconditioner` (DIC, DILU)
> - **Purpose:** เลือก solver ที่เหมาะสมกับประเภทของ matrix (SPD, non-symmetric, etc.)
>
> **กฎพื้นฐาน:**
> - **Pressure equation (SPD matrix)** → `PCG` หรือ `GAMG`
> - **Momentum/Velocity equation (non-symmetric)** → `PBiCGStab`
> - **Scalar transport (T, k, epsilon)** → `PCG` หาก symmetric, `PBiCGStab` หาก non-symmetric

### Task

เลือก solver ที่เหมาะสมสำหรับแต่ละ equation และอธิบายเหตุผล:

| Equation | Matrix Properties | Recommended Solver | Preconditioner | Justification |
|----------|-------------------|-------------------|----------------|----------------|
| Pressure (p) | SPD, diagonal dominance | ? | ? | ? |
| Velocity (U) | Non-symmetric (advection) | ? | ? | ? |
| Temperature (T) | Symmetric (diffusion-dominated) | ? | ? | ? |
| Turbulent kinetic energy (k) | Non-symmetric (strong advection) | ? | ? | ? |
| Volume fraction (alpha) | Bounded (0-1), sharp gradients | ? | ? | ? |

### Additional Questions

1. **เมื่อไหร่ควรใช้ GAMG แทน PCG?**
   - Mesh size threshold?
   - Memory considerations?
   - Parallel scaling?

2. **Preconditioner เลือกอย่างไร?**
   - DIC vs. DILU vs. none?
   - ความสำคัญของ preconditioning?

3. **ถ้า solver ไม่ converge (maxIter reached) ทำอย่างไร?**
   - ลด relTol หรือเพิ่ม tolerance?
   - เปลี่ยน solver หรือ preconditioner?
   - เพิ่ม under-relaxation?

---

## Exercise 3: Under-Relaxation for Stability

> [!NOTE] **📂 OpenFOAM Context**
> ส่วนนี้เกี่ยวข้องกับ **Convergence Control** ผ่าน under-relaxation factors
> - **File:** `system/fvSolution`
> - **Keywords:** `relaxationFactors`, `fields`, `equations`
> - **Purpose:** ควบคุมความเสถียรของ nonlinear iterations (เช่นใน SIMPLE/PISO algorithm)
>
> **การใช้งานจริง:**
> - **Field relaxation** (เช่น pressure `p 0.3`) → ใช้กับ field values โดยตรง
> - **Equation relaxation** (เช่น velocity `U 0.7`) → แก้ไข diagonal coefficients ใน matrix
> - ค่า **ต่ำ (0.1-0.3)** → เสถียรแต่ converge ช้า
> - ค่า **สูง (0.7-0.9)** → converge เร็วแต่อาจไม่เสถียร

### Task

ตั้งค่า relaxation factors สำหรับ case ที่มีปัญหา convergence:

**Scenario:** ใช้ SIMPLE algorithm สำหรับ steady-state incompressible flow
- Pressure residuals oscillate
- Velocity residuals decrease slowly
- Solution diverges หลังจาก 100 iterations

```cpp
// system/fvSolution
relaxationFactors
{
    fields
    {
        p       0.3;    // Field relaxation: direct value update
    }
    equations
    {
        U       0.7;    // Equation relaxation: modifies matrix diagonal
        T       0.8;    // For energy equation
        k       0.7;    // For turbulence
        epsilon 0.7;    // For turbulence
    }
}
```

### Questions

1. **Relaxation ต่ำ (0.1-0.3) ใช้เมื่อไหร่?**
   - Case ที่ highly nonlinear?
   - Initial iterations?
   - ข้อดี-ข้อเสีย?

2. **Field vs. Equation relaxation ต่างกันอย่างไร?**
   - Field: $\phi^{new} = \phi^{old} + \alpha(\phi^{calc} - \phi^{old})$
   - Equation: modifies diagonal coefficients: $A_{PP} = A_{PP} / \alpha$
   - เมื่อไหร่ใช้อันไหน?

3. **ถ้าลด p relaxation จาก 0.3 เป็น 0.1 จะเกิดอะไรขึ้น?**
   - Stability เพิ่มขึ้นหรือไม่?
   - Convergence rate เปลี่ยนอย่างไร?
   - Computational cost?

### Advanced Scenario

**Case:** High Reynolds number flow (Re = 10⁶) ใน complex geometry
- ปัญหา: residuals oscillate และ divergence บางครั้ง
- Mesh: 5M cells, boundary layers

**Task:** ออกแบบ relaxation strategy:
1. เริ่มต้นด้วย conservative factors
2. จากนั้น ออกแบบ strategy สำหรับ gradual increase
3. อธิบายว่าทำไมแต่ละค่าถูกเลือก

---

## Exercise 4: Troubleshooting Convergence Issues (Coding)

> [!NOTE] **📂 OpenFOAM Context**
> ส่วนนี้เกี่ยวข้องกับ **Diagnostic Tools** สำหรับแก้ปัญหา convergence
> - **Files:**
>   - `system/fvSolution` → solver settings
>   - `log.simpleFoam` / `log.pimpleFoam` → convergence history
> - **Tools:**
>   - `foamListTimes` → check time directories
>   - `sample` / `probe` → monitor field evolution
> - **Purpose:** วินิจฉัยปัญหา solver และแก้ไข settings

### Task

เขียน function ใน custom solver ที่ monitor convergence และ auto-adjust relaxation:

```cpp
// Pseudo-code for adaptive relaxation
scalar pResidual = 0.0;
scalar UResidual = 0.0;
scalar pRelax = 0.3;
scalar URelax = 0.7;

for (int i = 0; i < maxIter; i++)
{
    // Solve pressure
    pResidual = solve(pEqn).initialResidual();
    
    // Solve momentum
    UResidual = solve(UEqn).initialResidual();
    
    // Adaptive relaxation based on residuals
    if (pResidual > 1.0)  // Diverging
    {
        pRelax = max(0.1, pRelax * 0.8);
        Info << "Reducing p relaxation to " << pRelax << endl;
    }
    else if (pResidual < 0.01 && pRelax < 0.5)  // Converging well
    {
        pRelax = min(0.5, pRelax * 1.1);
    }
}
```

### Questions

1. **ทำไม initialResidual() สำคัญ?**
   - แตกต่างจาก final residual อย่างไร?
   - relTol คำนวณจากอะไร?

2. **Strategy นี้ใช้ได้กับ algorithm ไหนบ้าง?**
   - SIMPLE (steady)?
   - PISO (transient)?
   - PIMPLE (hybrid)?

3. **ข้อควรระวังของ adaptive relaxation?**
   - Stability risks?
   - Oscillation?

---

## Exercise 5: Custom Equation Assembly (Advanced Coding)

> [!NOTE] **📂 OpenFOAM Context**
> ส่วนนี้เกี่ยวข้องกับ **Custom Solver Development**
> - **Source:** `src/finiteVolume/fvMatrices/fvMatrix/`
> - **Application:** ใช้ใน custom solver ที่ต้องการ implement physics เพิ่มเติม
> - **Keywords:** `fvm::Sp`, `fvm::SuSp`, `fvm::laplacian`, `fvm::div`
>
> **Prerequisites:**
> - ความเข้าใจเรื่อง boundary conditions และ source term linearization
> - ความรู้เรื่อง implicit vs. explicit treatment

### Task

เขียน custom equation สำหรับ reacting flow โดยมี heat release dependent on temperature:

```cpp
// Reaction-diffusion equation: dT/dt + div(phi, T) = div(alpha*grad(T)) + S(T)
// where S(T) = -A * exp(-E/RT) * T (Arrhenius source term)

// Temperature-dependent source rate
volScalarField reactionRate
(
    A * exp(-E/(R*T)) * T
);

// Linearize source: S = S_explicit + S_implicit * T_P
// S_implicit = -dS/dT = -(A*exp(-E/RT) * (1 + E/(R*T)))
// S_explicit = S(T_old) - S_implicit * T_old

volScalarField SImplicit = -reactionRate * (1.0 + E/(R*T));
volScalarField SExplicit = reactionRate.oldTime() - SImplicit * T.oldTime();

fvScalarMatrix TEqn
(
    fvm::ddt(T)
  + fvm::div(phi, T)
 ==
    fvm::laplacian(alpha, T)
  + fvm::Sp(SImplicit, T)      // Implicit part → diagonal
  + fvc::Su(SExplicit, T)      // Explicit part → source
);

TEqn.relax(0.7);  // Under-relaxation for stability
TEqn.solve();
```

### Questions

1. **ทำไมต้อง linearize source term?**
   - Stability considerations?
   - Convergence implications?

2. **`fvm::Sp` vs `fvm::SuSp` ต่างกันอย่างไร?**
   - Sp: always implicit
   - SuSp: sign-dependent implicit/explicit

3. **การเลือก implicit vs. explicit ส่งผลต่อ matrix conditioning อย่างไร?**
   - Diagonal dominance?
   - Condition number?

---

## Solutions

### Exercise 1: Matrix Assembly

1. **`fvm::ddt` → Diagonal**
   - เพราะ backward Euler: $\frac{T^{n+1}_P - T^n_P}{\Delta t}$
   - เฉพาะ cell P มีค่า T^{n+1} → diagonal only
   - Source term: $-T^n_P/\Delta t$ → RHS

2. **`fvm::div` → Off-diagonal**
   - Upwind scheme: $F_f \max(\phi_f, 0)$ for upper, $F_f \min(-\phi_f, 0)$ for lower
   - Flux ระหว่าง neighbor cells → coupling ใน matrix
   - Explicit `fvc::div` → ทุกค่าไป RHS (no matrix coupling)

3. **`Su` vs. `Sp`**
   - `Su(source, T)` = explicit → source_ only (RHS)
   - `Sp(source, T)` = implicit → diagonal += source*V, source_ -= source*V*T
   - ใช้ `Sp` เมื่อ source dependent on solution variable (เพื่อ stability)

4. **`fvc::div` vs `fvm::div`**
   - `fvc::div`: Explicit, no matrix terms, ไป RHS ทั้งหมด
   - **ข้อดี:** เร็ว (ไม่ต้อง assemble matrix)
   - **ข้อเสีย:** Stability limited by CFL condition, timestep ต้องเล็ก
   - `fvm::div`: Implicit, matrix coupling, stable for large timestep

### Exercise 2: Solver Selection

| Equation | Matrix Properties | Solver | Preconditioner | Justification |
|----------|-------------------|--------|----------------|----------------|
| Pressure (p) | SPD, diagonal dominance | GAMG (or PCG) | DICGaussSeidel | SPD → CG/MG converge fast; DIC preserves SPD |
| Velocity (U) | Non-symmetric | PBiCGStab | DILU | Advection breaks symmetry; DILU handles non-symmetric |
| Temperature (T) | Symmetric | PCG (or GAMG) | DIC | Diffusion-dominated → SPD; DIC cheap and effective |
| k (turbulent kinetic energy) | Non-symmetric | PBiCGStab | DILU | Strong advection → non-symmetric |
| alpha (VOF) | Bounded, sharp gradients | MULES (special) | N/A | Not a linear system; uses special boundedness algorithm |

**Additional Questions:**

1. **GAMG vs. PCG:**
   - Use GAMG when: mesh > 1M cells, memory available, good parallel scaling needed
   - Use PCG when: mesh small (< 500k), memory limited, single-core
   - GAMG has O(N) complexity vs. O(N√κ) for PCG

2. **Preconditioner selection:**
   - **DIC** (Diagonal Incomplete Cholesky): For SPD (PCG/GAMG), cheap, good for diagonal dominance
   - **DILU** (Diagonal Incomplete LU): For non-symmetric (PBiCGStab), handles off-diagonals
   - **None:** Only for very well-conditioned problems (rare in CFD)

3. **Solver not converging:**
   - Check: relTol too low? → Increase (e.g., 0.01 → 0.1)
   - Check: tolerance too tight? → Loosen (e.g., 1e-7 → 1e-5)
   - Check: preconditioner weak? → Try stronger (e.g., DIC → DILU or GAMG)
   - Check: Matrix ill-conditioned? → Improve mesh quality, adjust discretization schemes
   - Last resort: Increase under-relaxation factors

### Exercise 3: Under-Relaxation

1. **Low relaxation (0.1-0.3):**
   - Use when: High nonlinearity (initial iterations), strong source terms, complex physics
   - **Pros:** Very stable, robust
   - **Cons:** Slow convergence, more iterations
   - **Strategy:** Start low (0.2), increase gradually as residuals drop

2. **Field vs. Equation:**
   - **Field relaxation:** Direct update: $\phi^{new} = \phi^{old} + \alpha(\phi^{calc} - \phi^{old})$
     - Use for: pressure in SIMPLE (field coupling is key)
   - **Equation relaxation:** Matrix modification: diagonal /= α
     - Use for: momentum, scalars, where equation stiffness matters
   
3. **Reducing p from 0.3 to 0.1:**
   - **Stability:** Increases significantly (slower updates)
   - **Convergence:** Decreases 2-3x slower (more iterations)
   - **Cost:** Higher computational time, but avoids divergence
   - **Trade-off:** 10-20% slower vs. 100% restart cost from divergence

**Advanced Scenario (High Re flow):**

```cpp
relaxationFactors
{
    fields
    {
        p       0.15;   // Very conservative (highly nonlinear)
    }
    equations
    {
        U       0.5;    // Moderate (advection-dominated)
        T       0.6;    // Higher (diffusion helps)
        k       0.5;    // Conservative (turbulence source)
        epsilon 0.5;    // Conservative (stiff source)
    }
}
```

**Gradual increase strategy:**
```cpp
// Pseudo-code in solver
scalar initialURelax = 0.5;
scalar targetURelax = 0.7;
scalar currentURelax = initialURelax;

if (runTime.timeIndex() % 100 == 0)
{
    scalar convergenceRatio = max(UResiduals.last(), 1e-3) / max(UResiduals.first(), 1e-3);
    
    if (convergenceRatio < 0.1 && currentURelax < targetURelax)
    {
        currentURelax = min(targetURelax, currentURelax * 1.1);
        Info << "Increasing U relaxation to " << currentURelax << endl;
    }
}
```

### Exercise 4: Troubleshooting (Conceptual)

1. **initialResidual() importance:**
   - initial = before first solver iteration (what matters for convergence)
   - final = after all iterations (should be << initial)
   - relTol = final / initial (target: e.g., 0.01 means 100x reduction)
   - **Why:** Only initial residual reflects equation nonlinearity; final just shows linear solver effectiveness

2. **Algorithm applicability:**
   - **SIMPLE:** Yes, highly beneficial (steady-state, needs heavy relaxation)
   - **PISO:** Limited benefit (transient, CFL-limited, less need)
   - **PIMPLE:** Moderate benefit (hybrid, can use outer correction loops)

3. **Adaptive relaxation risks:**
   - **Oscillation:** Rapid changes in relaxation can cause instability
   - **Hysteresis:** System may get stuck in suboptimal relaxation
   - **Mitigation:** Use gradual adjustments (max 10-20% change), add damping

### Exercise 5: Custom Equation (Conceptual)

1. **Source linearization necessity:**
   - **Stability:** Fully explicit source requires tiny timesteps (CFL-like constraint)
   - **Convergence:** Implicit treatment allows larger timesteps, faster convergence
   - **Newton-Raphson:** Linearization is first-order Taylor expansion

2. **`Sp` vs. `SuSp`:**
   - **`Sp(coeff, T)`:** Always adds coeff*V to diagonal (implicit)
     - Use when: coefficient sign is known and negative (stabilizing)
   - **`SuSp(coeff, T)`:** Sign-dependent
     - If coeff < 0: implicit (diagonal)
     - If coeff > 0: explicit (RHS)
     - Use when: coefficient may change sign (e.g., complex reactions)

3. **Matrix conditioning effects:**
   - **Implicit (Sp):** Increases diagonal dominance → better condition number (κ↓)
   - **Explicit (Su):** No diagonal modification → conditioning depends on other terms
   - **Trade-off:** Over-implicitization can slow convergence (excessive diagonal dominance → slow error propagation)

**Example linearization for Arrhenius:**
```cpp
// S(T) = -A * exp(-E/RT) * T = -k(T) * T
// dS/dT = -k(T) - T * dk/dT = -k(T) - T * k(T) * E/(R*T²)
//       = -k(T) * (1 + E/(R*T))

volScalarField k = A * exp(-E/(R*T));
volScalarField dSdT = -k * (1.0 + E/(R*T));

// Newton linearization around T_old:
// S(T) ≈ S(T_old) + dSdT|_old * (T - T_old)
//       = [S(T_old) - dSdT * T_old] + dSdT * T
//       = S_explicit + S_implicit * T

volScalarField SImplicit = dSdT;
volScalarField SExplicit = k.oldTime() * T.oldTime() - SImplicit * T.oldTime();
```

---

## Quick Reference

> [!NOTE] **📂 OpenFOAM Context**
> ตารางนี้เป็น **Quick Reference** สำหรับการเขียน discretized equations ใน custom solver
> - **Source Code:** `src/finiteVolume/fvMatrices/fvMatrix/`
> - **Application:** ใช้ใน solver source code (เช่น `UEqn.H`, `pEqn.H`)
> - **Key Concept:** `fvm` (implicit → matrix) vs `fvc` (explicit → source)
>
> **การนำไปใช้:**
> - เมื่อต้องการ **implicit treatment** (stable, แต่เพิ่ม matrix coupling) → ใช้ `fvm::`
> - เมื่อต้องการ **explicit treatment** (เร็ว, แต่อาจ unstable) → ใช้ `fvc::`

| Operation | fvm/fvc | Matrix Effect | Use Case | Stability |
|-----------|---------|---------------|----------|-----------|
| `ddt(phi)` | fvm | Diagonal only | Time derivatives (implicit) | Excellent (unconditionally stable) |
| `div(phi, psi)` | fvm | Off-diagonal | Convection (implicit) | Good (upwind bounded) |
| `div(phi, psi)` | fvc | Source only | Convection (explicit) | Poor (CFL-limited) |
| `laplacian(Gamma, psi)` | fvm | Diagonal + Off-diagonal | Diffusion (implicit) | Excellent |
| `grad(psi)` | fvc | Source only | Gradient reconstruction | N/A (post-processing) |
| `Sp(coeff, psi)` | fvm | Diagonal (implicit source) | Linearized source terms | Excellent (improves diagonal dominance) |
| `Su(coeff, psi)` | fvc | Source (explicit) | Fixed source terms | Good if small |
| `SuSp(coeff, psi)` | fvm/fvc | Diagonal or Source | Sign-dependent source | Adaptive (best of both) |

**Common Equation Templates:**

```cpp
// 1. Transient diffusion (e.g., heat conduction)
fvScalarMatrix TEqn
(
    fvm::ddt(T)
 ==
    fvm::laplacian(alpha, T)
);

// 2. Steady-state convection-diffusion
fvScalarMatrix TEqn
(
    fvm::div(phi, T)
 ==
    fvm::laplacian(alpha, T)
  + fvc::Su(source, T)
);

// 3. Momentum equation (incompressible)
fvVectorMatrix UEqn
(
    fvm::div(phi, U)
  - fvm::laplacian(nu, U)
 ==
    fvc::grad(p)
);

// 4. Pressure equation (Poisson)
fvScalarMatrix pEqn
(
    fvm::laplacian(1/AU, p) == fvc::div(phiHbyA)
);

// 5. Turbulence (k-epsilon)
fvScalarMatrix kEqn
(
    fvm::ddt(k)
  + fvm::div(phi, k)
 ==
    fvm::laplacian(DkEff, k)
  + fvm::Sp(Pk - epsilon, k)  // Implicit production/destruction
);

// 6. Energy with source
fvScalarMatrix TEqn
(
    fvm::ddt(T)
  + fvm::div(phi, T)
 ==
    fvm::laplacian(alpha, T)
  + fvm::Sp(hCoeff, T)        // Heat transfer (implicit)
  + fvc::Su(qSource, T)       // Volumetric heating (explicit)
);
```

---

## Key Takeaways

### 1. Linear Solver Selection

| Criterion | Decision |
|-----------|----------|
| **Matrix symmetry** | SPD → PCG/GAMG; Non-symmetric → PBiCGStab |
| **Problem size** | Small (< 500k) → PCG; Large (> 1M) → GAMG |
| **Preconditioning** | SPD → DIC; Non-symmetric → DILU |
| **Parallel scaling** | GAMG > PCG > PBiCGStab |

### 2. Matrix Assembly Principles

- **Implicit (fvm):** Matrix terms → stable, larger timesteps
- **Explicit (fvc):** Source terms → faster per iteration, CFL-limited
- **Source linearization:** Use `fvm::Sp` for solution-dependent sources (stability)
- **Diagonal dominance:** Critical for iterative solver convergence

### 3. Convergence Strategies

| Strategy | When to Use | Effect |
|----------|-------------|--------|
| **Under-relaxation (0.1-0.3)** | Highly nonlinear, initial iterations | Improves stability, slows convergence |
| **Tight tolerance (1e-6)** | Final accuracy | Increases iterations, improves accuracy |
| **Loose relTol (0.1)** | Intermediate iterations | Faster per timestep, acceptable accuracy |
| **GAMG for large meshes** | > 1M cells | O(N) complexity, better parallel scaling |

### 4. Troubleshooting Checklist

1. **Solver diverges:**
   - ↓ relaxation factors (0.7 → 0.3)
   - ↓ relTol (0.1 → 0.01)
   - Change preconditioner (DILU → GAMG)
   - Check mesh quality (non-orthogonality, aspect ratio)

2. **Slow convergence:**
   - ↑ relTol (0.01 → 0.1) if intermediate iterations
   - Switch PCG → GAMG for large meshes
   - Check if tolerances too tight (1e-7 → 1e-5)

3. **Oscillating residuals:**
   - ↓ relaxation factors
   - Improve mesh quality
   - Check boundary condition consistency
   - Try different discretization schemes

### 5. Best Practices

- **Pressure:** Always use GAMG or PCG with DIC (SPD matrix)
- **Velocity:** PBiCGStab with DILU (non-symmetric from advection)
- **Scalars:** PCG if diffusion-dominated, PBiCGStab if advection-dominated
- **Sources:** Linearize and implicitize (`fvm::Sp`) when possible
- **Relaxation:** Start conservative (0.2-0.3), increase as residuals drop
- **Monitoring:** Track initial residuals, not just final

---

## 🧠 Concept Check

> [!NOTE] **📂 OpenFOAM Context**
> ส่วนนี้เป็น **Self-Assessment** สำหรับทบทวนความเข้าใจเกี่ยวกับ linear solver configuration
> - **Files ที่เกี่ยวข้อง:** `system/fvSolution`, `system/fvSchemes`
> - **Key Concepts:** Matrix properties (SPD, symmetric), Solver algorithms (CG, BiCGStab, Multigrid), Convergence criteria
> - **Practical Application:** การเลือก solver และ tolerance ที่เหมาะสมกับปัญหา
>
> **เป้าหมาย:** หลังจากทบทวนตัวเอง คุณควรสามารถอธิบายได้ว่าทำไม solver แต่ละตัวถูกเลือกใช้กับ equation ที่ต่างกัน

<details>
<summary><b>1. ทำไม pressure ใช้ PCG (ไม่ใช่ PBiCGStab)?</b></summary>

**เฉลย:** Pressure matrix จาก incompressible flow เป็น **Symmetric Positive Definite (SPD)** เพราะ:
- Discretization ของ Laplacian (∇²p) สร้าง symmetric coefficients
- ไม่มี advection term (divergence-free constraint)
- Boundary conditions ไม่ทำลาย symmetry

**PCG converge เร็วกว่า** PBiCGStab สำหรับ SPD matrices เพราะ:
- CG ได้รับประกัน convergence ใน N iterations (N = จำนวน unknowns)
- BiCGStab ออกแบบมาสำหรับ non-symmetric → ไม่มีประโยชน์พิเศษสำหรับ SPD
- Preconditioner DIC (Incomplete Cholesky) preserve SPD property

> [!NOTE] **📂 OpenFOAM Context**
> ใน practice:
> ```cpp
> solvers
> {
>     p
>     {
>         solver          PCG;          // Not PBiCGStab!
>         preconditioner  DIC;          // Preserves SPD
>         tolerance       1e-06;
>         relTol          0.01;
>     }
> }
> ```

</details>

<details>
<summary><b>2. GAMG ดีกว่า PCG อย่างไร (และเมื่อไหร่ควรใช้)?</b></summary>

**เฉลย:** **GAMG** (Geometric-Algebraic Multigrid) มีข้อดีเหนือ PCG ในด้าน **computational complexity**:

| Property | PCG | GAMG |
|----------|-----|------|
| **Complexity** | O(N√κ) | O(N) |
| **Scalability** | Moderate | Excellent |
| **Memory** | Lower | Higher |
| **Setup time** | Minimal | Significant |
| **Best for** | Small-medium meshes (< 500k) | Large meshes (> 1M cells) |

**Key:**
- **N** = Number of unknowns
- **κ** = Condition number (ratio of largest to smallest eigenvalue)

**ทำไม GAMG เร็วกว่า?**
1. **Multigrid hierarchy:** แก้ปัญหาบน multiple mesh levels (coarse → fine)
2. **Smooth low-frequency errors:** Coarse grids แก้ข้อผิดพลาด low-frequency ได้ดี
3. **Smooth high-frequency errors:** Fine grids แก้ high-frequency errors ได้ดี
4. **Result:** O(N) iterations ไม่ขึ้นกับ mesh size

**เมื่อไหร่ใช้ GAMG?**
- Mesh > 1M cells
- Parallel simulations (excellent scaling)
- Steady-state problems (setup cost amortized)
- Memory available (GAMG ใช้ memory มากกว่า)

**เมื่อไหร่ใช้ PCG?**
- Mesh < 500k cells
- Memory limited
- Transient problems (frequent rebuilds, GAMG setup expensive)
- Serial runs

> [!NOTE] **📂 OpenFOAM Context**
> ```cpp
> // Large mesh: use GAMG
> solvers
> {
>     p
>     {
>         solver          GAMG;
>         preconditioner  DICGaussSeidel;
>         nCellsInCoarsestLevel  10;
>         cacheAgglomeration on;
>     }
> }
>
> // Small mesh: use PCG
> solvers
> {
>     p
>     {
>         solver          PCG;
>         preconditioner  DIC;
>     }
> }
> ```
</details>

<details>
<summary><b>3. relTol vs tolerance ต่างกันอย่างไร (และตั้งค่าอย่างไร)?</b></summary>

**เฉลย:**

| Parameter | Definition | Physical Meaning | Typical Value |
|-----------|------------|-------------------|---------------|
| **tolerance** | Absolute residual target | Residual must drop below this value | 1e-6 to 1e-5 |
| **relTol** | Relative reduction target | Residual must drop by this fraction | 0.01 to 0.1 |

**ความสำคัญ:**
- **tolerance (absolute):** `finalResidual < tolerance`
- **relTol (relative):** `finalResidual < relTol * initialResidual`

**Solver stops when:** `finalResidual < max(tolerance, relTol * initialResidual)`

**กฎพื้นฐาน:**
1. **tolerance:** ควรต่ำกว่า final convergence target ของ simulation อย่างน้อย 1 order of magnitude
   - ถ้าต้องการ final residuals ~ 1e-4 → ตั้ง tolerance = 1e-5 หรือ 1e-6
   - **ไม่ควร** ตั้ง tolerance สูงเกินไป (เช่น 1e-3) → จำกัดความแม่นยำ

2. **relTol:** ควรตั้งตาม iteration stage
   - **Initial iterations (far from solution):** ใช้ relTol สูง (0.1) → เร็ว
   - **Final iterations (close to solution):** ใช้ relTol ต่ำ (0.01) → แม่นยำ
   - **Transient simulations:** relTol 0.05-0.1 (ไม่ต้องแม่นยำทุก timestep)
   - **Steady-state:** relTol 0.01 (ต้องการ tight convergence)

**ตัวอย่าง:**

```cpp
// Steady-state, high accuracy
solvers
{
    p
    {
        solver      PCG;
        tolerance   1e-06;   // Tight absolute
        relTol      0.01;    // Tight relative (1%)
    }
}

// Transient, moderate accuracy
solvers
{
    p
    {
        solver      PCG;
        tolerance   1e-05;   // Looser absolute
        relTol      0.1;     // Loose relative (10%)
    }
}
```

**Common pitfalls:**
- ❌ **tolerance สูงเกินไป (1e-3):** Solver หยุดเร็วเกินไป → residuals plateau ไม่ลดต่อ
- ❌ **relTol ต่ำเกินไป (0.001):** Solver ทำงานหนักเกินไป → สิ้นเปลืองเวลาใน early iterations
- ❌ **tolerance ต่ำเกินไป (1e-9):** Numerical noise → solver ไม่สามารถลดไปถึงได้

> [!NOTE] **📂 OpenFOAM Context**
> **Debugging tip:** Monitor residuals ใน log file:
> ```
> // Good convergence pattern:
> Initial residual = 1.0, Final residual = 0.008, No Iterations 5
> Initial residual = 0.05, Final residual = 0.0004, No Iterations 6
> 
> // Bad pattern (tolerance too high):
> Initial residual = 1.0, Final residual = 0.001, No Iterations 2  // Stopped too early!
> 
> // Bad pattern (relTol too low):
> Initial residual = 0.01, Final residual = 0.0001, No Iterations 20  // Wasting time!
> ```
</details>

<details>
<summary><b>4. ทำไม velocity ใช้ PBiCGStab (ไม่ใช่ PCG)?</b></summary>

**เฉลย:** Velocity matrix เป็น **non-symmetric** เพราะ:

1. **Convection term (`div(phi, U)`)**
   - Upwind scheme สร้าง asymmetric weights
   - Flux ขาเข้า vs. ขาออก ไม่เท่ากัน
   - Example: `F * max(phi_f, 0)` for upper, `F * min(-phi_f, 0)` for lower

2. **Pressure gradient**
   - ถ้า pressure ไม่ symmetric → velocity ก็ไม่ symmetric

**PCG ไม่สามารถใช้กับ non-symmetric:**
- CG algorithms assume `A = A^T` (symmetric)
- Non-symmetric matrices: CG อาจ diverge หรือ converge ช้ามาก

**PBiCGStab ออกแบบมาสำหรับ non-symmetric:**
- Bi-Conjugate Gradient Stabilized
- Handles off-diagonal asymmetry
- More robust than standard BiCG

> [!NOTE] **📂 OpenFOAM Context**
> ```cpp
> solvers
> {
>     U
>     {
>         solver          PBiCGStab;    // Non-symmetric!
>         preconditioner  DILU;         // Handles non-symmetry
>         tolerance       1e-05;
>         relTol          0.1;
>     }
> }
> 
> // Note: DILU (Diagonal Incomplete LU) preserves non-symmetric structure
> // DIC would fail (assumes SPD)
> ```
</details>

<details>
<summary><b>5. fvm::Sp vs fvc::Su เลือกใช้อย่างไร?</b></summary>

**เฉลย:**

| Operator | Full Name | Matrix Effect | When to Use | Stability |
|----------|-----------|---------------|-------------|-----------|
| `fvm::Sp(coeff, psi)` | Source Implicit | Diagonal += coeff*V, Source -= coeff*V*psi | Source dependent on solution variable | Excellent (improves diagonal dominance) |
| `fvc::Su(coeff, psi)` | Source Explicit | Source += coeff*V | Fixed source (independent of solution) | Good if small |

**Guidelines:**

1. **ใช้ `fvm::Sp` เมื่อ:**
   - Source dependent on solution variable (e.g., reaction rate ~ T)
   - Want to improve stability (increase diagonal dominance)
   - **Example:** Turbulence equations (`fvm::Sp(Pk - epsilon, k)`)

2. **ใช้ `fvc::Su` เมื่อ:**
   - Source independent of solution (e.g., gravity, fixed heat source)
   - Explicit treatment ไม่ทำให้ unstable
   - **Example:** Volumetric heating (`fvc::Su(qVol, T)`)

3. **ใช้ `fvm::SuSp` เมื่อ:**
   - Source coefficient may change sign
   - Adaptive implicit/explicit treatment
   - **Example:** Complex reactions with reversible steps

**Example:**

```cpp
// Heat transfer to wall (depends on T - T_wall)
// Bad (unstable if coeff large):
volScalarField hCoeff = 1000;  // Heat transfer coefficient
fvScalarMatrix TEqn
(
    fvm::ddt(T)
  + fvm::div(phi, T)
 ==
    fvm::laplacian(alpha, T)
  + fvc::Su(hCoeff * (T - T_wall), T)  // Explicit → unstable!
);

// Good (implicit):
fvScalarMatrix TEqn
(
    fvm::ddt(T)
  + fvm::div(phi, T)
 ==
    fvm::laplacian(alpha, T)
  + fvm::Sp(hCoeff, T)        // Implicit on T
  - fvc::Su(hCoeff * T_wall, T)  // Explicit on T_wall (constant)
);
```

> [!NOTE] **📂 OpenFOAM Context**
> **Key principle:** Linearize source terms และใส่ส่วนที่ dependent on unknown ลง diagonal (implicit)
> 
> **Mathematical form:**
> - Explicit: `S = S(T_old)` → source_ only
> - Implicit: `S = S_implicit * T + S_explicit` → diagonal += S_implicit, source += S_explicit
> 
> **Newton linearization:**
> ```cpp
> // S(T) = -k(T) * T (Arrhenius)
> // dS/dT = -dk/dT * T - k = -k * (1 + E/(RT))
> volScalarField dSdT = -k * (1.0 + E/(R*T));
> TEqn += fvm::Sp(dSdT, T) + fvc::Su(k * T.oldTime() - dSdT * T.oldTime(), T);
> ```
</details>

<details>
<summary><b>6. Under-relaxation: Field vs. Equation (ต่างกันอย่างไร)?</b></summary>

**เฉลย:**

| Aspect | Field Relaxation | Equation Relaxation |
|--------|------------------|-------------------|
| **Application point** | After solution | Before/during solution |
| **Implementation** | $\phi^{new} = \phi^{old} + \alpha(\phi^{calc} - \phi^{old})$ | Modifies matrix diagonal: $A_{PP} = A_{PP} / \alpha$ |
| **Use case** | Pressure (SIMPLE) | Momentum, scalars |
| **Stability effect** | Decouples non-linear updates | Increases diagonal dominance |
| **Speed effect** | Minimal overhead | Slightly slower (matrix modification) |

**Field Relaxation:**
```cpp
// system/fvSolution
relaxationFactors
{
    fields
    {
        p    0.3;    // Applied after pEqn.solve()
    }
}

// Equivalent to:
// p = p.oldTime() + 0.3 * (p - p.oldTime());
```

**Equation Relaxation:**
```cpp
// system/fvSolution
relaxationFactors
{
    equations
    {
        U    0.7;    // Applied during UEqn assembly
    }
}

// Equivalent to:
// UEqn.relax(0.7);
// Which does: UEqn.diag() /= 0.7;
```

**เมื่อไหร่ใช้อันไหน?**
- **Field relaxation:** สำหรับ pressure ใน SIMPLE (pressure-velocity coupling ต้องการ conservative updates)
- **Equation relaxation:** สำหรับ momentum/scalars (matrix stiffness ต้องการ diagonal modification)

> [!NOTE] **📂 OpenFOAM Context**
> **SIMPLE algorithm relaxation strategy:**
> ```cpp
> relaxationFactors
> {
>     fields
>     {
>         p    0.3;    // Low (pressure-sensitive)
>     }
>     equations
>     {
>         U    0.7;    // Medium (momentum coupling)
>         T    0.8;    // Higher (diffusion stabilizes)
>     }
> }
> 
> // Lower values = more stable but slower convergence
> // Increase gradually as residuals decrease
> ```
</details>

---

## 📖 Related Documentation

### Within This Module

1. **[00_Overview.md](00_Overview.md)** - Module roadmap and learning path
2. **[02_Dense_vs_Sparse_Matrices.md](02_Dense_vs_Sparse_Matrices.md)** - Understanding lduMatrix and sparse storage
3. **[03_fvMatrix_Architecture.md](03_fvMatrix_Architecture.md)** - fvMatrix internal structure and LDU addressing
4. **[04_Linear_Solvers_Hierarchy.md](04_Linear_Solvers_Hierarchy.md)** - Krylov methods, preconditioners, multigrid

### Prerequisite Modules

1. **[01_FOUNDATION_PRIMITIVES/05_Containers.md](../../01_FOUNDATION_PRIMITIVES/05_Containers.md)** - List, UList, field storage
2. **[01_FOUNDATION_PRIMITIVES/06_Smart_Pointers.md](../../01_FOUNDATION_PRIMITIVES/06_Smart_Pointers.md)** - autoPtr, refPtr, tmp

### Cross-Module References

1. **[03_CONTAINERS_MEMORY/](../../03_CONTAINERS_MEMORY/)** - Memory management in field operations
2. **[04_MESH_CLASSES/05_fvMesh.md](../../04_MESH_CLASSES/05_fvMesh.md)** - Finite volume mesh and geometric fields

### External Resources

1. **OpenFOAM Source Code:**
   - `src/finiteVolume/fvMatrices/fvMatrix/` - fvMatrix implementation
   - `src/finiteVolume/fvMatrices/fvScalarMatrix/` - Scalar matrix specializations
   - `src/finiteVolume/fvMatrices/fvVectorMatrix/` - Vector matrix specializations
   - `src/matrixSolvers/` - Linear solver implementations (PCG, PBiCGStab, GAMG)
   - `src/OpenFOAM/matrices/lduMatrix/` - LDU storage and solvers

2. **User Guide:**
   - `$FOAM_DOC/Guides/A4UserGuide.pdf` - Section 4.5: Linear solver configuration

3. **Doxygen:**
   - [fvMatrix Class Documentation](https://www.openfoam.com/documentation/guide/latest/) - Official API reference

---

## Next Steps

After completing this section, you should be able to:

1. **Configure linear solvers** in `system/fvSolution` for different equation types
2. **Diagnose convergence issues** by analyzing residuals and matrix properties
3. **Write custom equations** with appropriate implicit/explicit treatments
4. **Apply under-relaxation strategies** for stability in coupled problems

**Recommended next topics:**
- **Custom Solver Development:** Implement your own solver with optimized linear algebra
- **Advanced Preconditioning:** Explore ILU, AMG, and custom preconditioners
- **Parallel Linear Algebra:** Understand domain decomposition and parallel solver scaling