# Matrix Assembly

กระบวนการแปลง PDE → ระบบสมการเชิงเส้น $[A][\phi] = [b]$

---

## ภาพรวม

หลัง Discretization ทุก Cell จะได้สมการ:

$$a_P \phi_P + \sum_N a_N \phi_N = b_P$$

เมื่อรวมทุก Cell → ได้ระบบ:

$$[A][\phi] = [b]$$

| Component | ความหมาย | มาจาก |
|-----------|---------|-------|
| $a_P$ | Diagonal | Cell P เอง (ddt, diffusion, convection) |
| $a_N$ | Off-diagonal | Neighbors (diffusion, convection) |
| $b_P$ | Source | Explicit terms, BCs, old time values |

---

## Coefficients จากแต่ละ Term

### Diffusion Term

$$\nabla \cdot (D \nabla \phi) \rightarrow a_N = -\frac{D_f A_f}{d_{PN}}$$

$$a_P = -\sum_N a_N$$

### Convection Term (Upwind)

$$\nabla \cdot (\phi \mathbf{u}) \rightarrow a_N = \max(-\Phi_f, 0)$$

โดย $\Phi_f = \mathbf{u}_f \cdot \mathbf{S}_f$ (face flux)

### Temporal Term

$$\frac{\partial \phi}{\partial t} \rightarrow a_P += \frac{\rho V}{\Delta t}, \quad b_P += \frac{\rho V}{\Delta t} \phi^n$$

---

## OpenFOAM Implementation

### fvm vs fvc

| Prefix | ชื่อเต็ม | ผลลัพธ์ | ใช้เมื่อ |
|--------|---------|---------|---------|
| `fvm::` | Finite Volume Method | → Matrix | Implicit terms |
| `fvc::` | Finite Volume Calculus | → Field | Explicit terms |

**ตัวอย่าง:**

```cpp
fvVectorMatrix UEqn
(
    fvm::ddt(rho, U)              // → Diagonal
  + fvm::div(phi, U)              // → Diagonal + Off-diagonal
  - fvm::laplacian(mu, U)         // → Diagonal + Off-diagonal
 ==
    -fvc::grad(p)                 // → Source vector
);
```

### สมการโมเมนตัม

$$\rho\frac{\partial \mathbf{u}}{\partial t} + \nabla \cdot (\rho \mathbf{u} \mathbf{u}) = -\nabla p + \nabla \cdot (\mu \nabla \mathbf{u})$$

```cpp
fvVectorMatrix UEqn
(
    fvm::ddt(rho, U)
  + fvm::div(phi, U)
  - fvm::laplacian(mu, U)
);

// Pressure coupling
solve(UEqn == -fvc::grad(p));
```

### สมการ Energy

$$\rho c_p \frac{\partial T}{\partial t} + \nabla \cdot (\rho c_p \mathbf{u} T) = \nabla \cdot (k \nabla T) + Q$$

```cpp
fvScalarMatrix TEqn
(
    rho*cp*fvm::ddt(T)
  + rho*cp*fvm::div(phi, T)
  - fvm::laplacian(k, T)
 ==
    Q
);
TEqn.solve();
```

---

## Boundary Conditions

| BC Type | ผลต่อ Matrix |
|---------|-------------|
| `fixedValue` | แก้ไข $a_P$, $b_P$ |
| `zeroGradient` | ไม่มี off-diagonal ที่ boundary |
| `mixed` | แก้ไขทั้งคู่ |

**ตัวอย่าง fixedValue:**

```cpp
// 0/U
inlet
{
    type    fixedValue;
    value   uniform (10 0 0);  // → เพิ่มเข้า source
}
```

---

## Sparse Matrix Structure

Matrix $[A]$ มีโครงสร้าง **Sparse** เพราะ:
- แต่ละ Cell เชื่อมต่อกับ **Neighbors เท่านั้น**
- Non-zero entries ≈ 6-20 ต่อแถว (3D)

```
Cell P:   [a_P  a_N1  a_N2  a_N3  a_N4  0  0  0  ...]
```

---

## Linear Solvers

### Solver Selection

| Solver | Matrix Type | ใช้กับ |
|--------|-------------|--------|
| `GAMG` | Symmetric | p (pressure) |
| `PCG` | Symmetric PD | p (alternative) |
| `PBiCGStab` | Asymmetric | U, k, ε |
| `smoothSolver` | Any | เล็ก/ง่าย |

### ตั้งค่าใน `system/fvSolution`

```cpp
solvers
{
    p
    {
        solver      GAMG;
        smoother    GaussSeidel;
        tolerance   1e-6;
        relTol      0.01;
    }
    pFinal
    {
        $p;
        relTol      0;
    }
    U
    {
        solver      PBiCGStab;
        preconditioner DILU;
        tolerance   1e-5;
        relTol      0.1;
    }
}
```

### Relaxation

```cpp
relaxationFactors
{
    fields
    {
        p       0.3;    // Pressure (ค่อยๆ เปลี่ยน)
    }
    equations
    {
        U       0.7;    // Velocity
        k       0.7;
        epsilon 0.7;
    }
}
```

---

## Source Terms

### Explicit Source

```cpp
fvScalarMatrix TEqn(...);
TEqn += Q;  // Q เป็น volScalarField → เข้า source vector
```

### Semi-Implicit Source

$$S = S_u + S_p \cdot \phi$$

```cpp
fvScalarMatrix TEqn
(
    ...
 ==
    Su                       // Explicit part → source
  + fvm::Sp(Sp, T)          // Implicit part → diagonal
);
```

**ข้อดี:** ถ้า $S_p < 0$ → เพิ่ม diagonal dominance → เสถียรขึ้น

---

## Debugging Tips

### 1. Divergence

```
--> FOAM FATAL ERROR: Maximum number of iterations exceeded
```

**ลองทำ:**
- ลด `relTol` (เช่น 0.1 → 0.01)
- เพิ่ม relaxation (เช่น 0.7 → 0.5)
- ลด `deltaT`

### 2. ช้ามาก

**ลองทำ:**
- เปลี่ยน solver (smoothSolver → GAMG)
- เพิ่ม `relTol` (0.01 → 0.1 สำหรับ intermediate iterations)

### 3. Check Residuals

```bash
foamLog log.simpleFoam
gnuplot residuals
```

---

## Concept Check

<details>
<summary><b>1. fvm กับ fvc ต่างกันอย่างไร?</b></summary>

- **fvm**: สร้าง Matrix coefficients (implicit) → ใช้กับ terms ที่ต้องการ solve
- **fvc**: คำนวณ Field โดยตรง (explicit) → ใช้กับ terms ที่รู้ค่าแล้ว (เช่น pressure gradient)
</details>

<details>
<summary><b>2. ทำไม GAMG เร็วกว่า PCG สำหรับ pressure?</b></summary>

เพราะ GAMG ใช้ Multigrid ซึ่งลด error ทุก frequency พร้อมกัน ในขณะที่ PCG ลดทีละ frequency → GAMG ต้องการ iterations น้อยกว่า
</details>

<details>
<summary><b>3. relaxation 0.3 กับ 0.7 ต่างกันอย่างไร?</b></summary>

- **0.3**: เปลี่ยน 30% ของค่าใหม่ → ช้าแต่เสถียร
- **0.7**: เปลี่ยน 70% ของค่าใหม่ → เร็วแต่อาจ oscillate
- Pressure มักใช้ค่าต่ำ (0.3), Velocity ใช้สูงกว่า (0.7)
</details>

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [04_Temporal_Discretization.md](04_Temporal_Discretization.md) — Temporal Discretization
- **บทถัดไป:** [06_OpenFOAM_Implementation.md](06_OpenFOAM_Implementation.md) — OpenFOAM Implementation