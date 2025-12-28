# Matrices & Linear Algebra - Summary and Exercises

สรุปและแบบฝึกหัด Linear Algebra ใน OpenFOAM

> [!TIP] ทำไม Linear Algebra สำคัญใน OpenFOAM?
> **Linear Algebra** เป็นหัวใจของการแก้สมการพาร์เทียลดิฟเฟอเรนเชียล (PDE) ใน CFD ทุกประเภท ไม่ว่าจะเป็น การไหลของไหล (fluid flow), การถ่ายเทความร้อน (heat transfer), หรือการละลายของไอเสีย (turbulence) เมื่อเรา **discretize** สมการบน mesh จะได้รับ **system of linear equations** ในรูปแบบ $[A][x] = [b]$
>
> **การเลือก solver ที่เหมาะสม** และ **การตั้งค่า tolerance** ส่งผลโดยตรงต่อ:
> - **Stability:** การทำงานที่เสถียรของ simulation (ไม่ explode)
> - **Convergence speed:** เวลาที่ใช้ในการคำนวณ (fast vs slow)
> - **Accuracy:** ความแม่นยำของคำตอบ
>
> ใน OpenFOAM การตั้งค่า linear solvers ทั้งหมดอยู่ใน **`system/fvSolution`**

---

## Summary

### fvMatrix Structure

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

| Class | Purpose |
|-------|---------|
| `fvScalarMatrix` | Matrix for scalar equations |
| `fvVectorMatrix` | Matrix for vector equations |
| `lduMatrix` | Lower-diagonal-upper storage |

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

| Solver | Best For |
|--------|----------|
| `PCG` | Symmetric (pressure) |
| `PBiCGStab` | Non-symmetric (velocity) |
| `GAMG` | Large problems |
| `smoothSolver` | Simple problems |

### Configuration

```cpp
// system/fvSolution
solvers
{
    p
    {
        solver      PCG;
        preconditioner DIC;
        tolerance   1e-6;
        relTol      0.01;
    }
    U
    {
        solver      PBiCGStab;
        preconditioner DILU;
        tolerance   1e-6;
        relTol      0.1;
    }
}
```

---

## Exercise 1: Matrix Assembly

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

เข้าใจการประกอบ matrix จาก equation

```cpp
fvScalarMatrix TEqn
(
    fvm::ddt(T)                    // Diagonal contribution
  + fvm::div(phi, T)               // Convection (off-diagonal)
 ==
    fvm::laplacian(alpha, T)       // Diffusion (off-diagonal)
  + fvc::Su(source, T)             // Source
);
```

### Questions

1. `fvm::ddt` ใส่ค่าใน matrix ตรงไหน?
2. `fvm::div` สร้าง off-diagonal terms อย่างไร?
3. `fvc::Su` ต่างจาก `fvm::Sp` อย่างไร?

---

## Exercise 2: Solver Selection

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

เลือก solver ที่เหมาะสม

| Equation | Matrix Type | Recommended Solver |
|----------|-------------|-------------------|
| Pressure | SPD | ? |
| Velocity | Non-symmetric | ? |
| Temperature | Symmetric | ? |

---

## Exercise 3: Under-Relaxation

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

แก้ปัญหา convergence ด้วย relaxation

```cpp
// system/fvSolution
relaxationFactors
{
    fields
    {
        p       0.3;    // Field relaxation
    }
    equations
    {
        U       0.7;    // Equation relaxation
    }
}
```

### Questions

1. ค่า relaxation ต่ำใช้เมื่อไหร่?
2. Field vs Equation relaxation ต่างกันอย่างไร?

---

## Solutions

### Exercise 1

1. **ddt** → diagonal เพราะ $\frac{T^{n+1}_P - T^n_P}{\Delta t}$
2. **div** → off-diagonal เพราะ flux ระหว่าง cells
3. **Su** = explicit source, **Sp** = implicit (linearized)

### Exercise 2

| Equation | Solver |
|----------|--------|
| Pressure | PCG + GAMG |
| Velocity | PBiCGStab |
| Temperature | PCG |

### Exercise 3

1. Relaxation ต่ำ → convergence ช้าแต่ stable
2. Field: $\phi^{new} = \phi^{old} + \alpha(\phi^{calc} - \phi^{old})$
   Equation: modifies matrix diagonal

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

| Operation | fvm/fvc | Matrix Effect |
|-----------|---------|---------------|
| `ddt` | fvm | Diagonal |
| `div` | fvm | Off-diagonal |
| `laplacian` | fvm | Off-diagonal |
| `grad` | fvc | Source only |
| `Sp` | fvm | Diagonal (implicit) |
| `Su` | fvc | Source (explicit) |

---

## Concept Check

> [!NOTE] **📂 OpenFOAM Context**
> ส่วนนี้เป็น **Self-Assessment** สำหรับทบทวนความเข้าใจเกี่ยวกับ linear solver configuration
> - **Files ที่เกี่ยวข้อง:** `system/fvSolution`, `system/fvSchemes`
> - **Key Concepts:** Matrix properties (SPD, symmetric), Solver algorithms (CG, BiCGStab, Multigrid), Convergence criteria
> - **Practical Application:** การเลือก solver และ tolerance ที่เหมาะสมกับปัญหา
>
> **เป้าหมาย:** หลังจากทบทวนตัวเอง คุณควรสามารถอธิบายได้ว่าทำไม solver แต่ละตัวถูกเลือกใช้กับ equation ที่ต่างกัน

<details>
<summary><b>1. ทำไม pressure ใช้ PCG?</b></summary>

เพราะ pressure matrix เป็น **Symmetric Positive Definite (SPD)** → PCG converge เร็ว
</details>

<details>
<summary><b>2. GAMG ดีกว่า PCG อย่างไร?</b></summary>

**GAMG** ใช้ multigrid → **O(N)** complexity แทน O(N²), ดีสำหรับ large problems
</details>

<details>
<summary><b>3. relTol vs tolerance ต่างกันอย่างไร?</b></summary>

- **tolerance**: Absolute residual target
- **relTol**: Relative reduction from initial
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **fvMatrix:** [03_fvMatrix_Architecture.md](03_fvMatrix_Architecture.md)