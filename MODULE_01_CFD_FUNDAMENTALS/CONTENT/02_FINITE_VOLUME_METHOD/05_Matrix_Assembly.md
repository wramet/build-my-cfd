# Matrix Assembly

กระบวนการแปลง PDE → ระบบสมการเชิงเส้น $[A][\phi] = [b]$

> **ทำไมต้องสนใจ Matrix Assembly?**
> - เข้าใจ matrix = เข้าใจว่า discretization scheme ทำงานอย่างไร
> - Debug divergence ได้ถูกจุด (เช่น diagonal dominance หาย)
> - เลือก linear solver ได้เหมาะสม

---

## ภาพรวม

หลัง Discretization ทุก Cell จะได้สมการ:

$$a_P \phi_P + \sum_N a_N \phi_N = b_P$$

> **💡 คิดแบบนี้:**
> แต่ละ cell มี "สมการตัวเอง" ที่บอกว่า:
> "ค่าที่ฉัน ($\phi_P$) ขึ้นกับค่าที่เพื่อนบ้าน ($\phi_N$) และ sources ($b_P$)"

เมื่อรวมทุก Cell → ได้ระบบ:

$$[A][\phi] = [b]$$

| Component | มาจาก | ทำไมสำคัญ |
|-----------|-------|----------|
| $a_P$ (Diagonal) | ddt, diffusion, convection ที่ Cell P | ต้องใหญ่พอ → stability |
| $a_N$ (Off-diagonal) | diffusion, convection ที่ Neighbors | เชื่อม cells เข้าด้วยกัน |
| $b_P$ (Source) | Explicit terms, BCs, old time values | "ข้อมูลที่รู้แล้ว" |

---

## Coefficients จากแต่ละ Term

### Diffusion Term (ช่วย Stability!)

$$\nabla \cdot (D \nabla \phi) \rightarrow a_N = -\frac{D_f A_f}{d_{PN}}$$

$$a_P = -\sum_N a_N$$

**ทำไม Diffusion ดีสำหรับ Stability?**
- $a_N < 0$ เสมอ (ติดลบ)
- $a_P = -\sum a_N > 0$ (เป็นบวก)
- → **Diagonal Dominant** → Stable!

### Convection Term (อาจลด Stability!)

$$\nabla \cdot (\phi \mathbf{u}) \rightarrow a_N = \max(-\Phi_f, 0)$$

โดย $\Phi_f = \mathbf{u}_f \cdot \mathbf{S}_f$ (face flux)

**ทำไม Convection อาจเป็นปัญหา?**
- Upwind: $a_N$ มาจากด้าน upstream เท่านั้น → ยังคง diagonal dominant
- Central: $a_N$ มาจากทั้งสองด้าน → อาจทำให้ **diagonal dominance ลดลง** → unstable

### Temporal Term (เพิ่ม Stability!)

$$\frac{\partial \phi}{\partial t} \rightarrow a_P += \frac{\rho V}{\Delta t}, \quad b_P += \frac{\rho V}{\Delta t} \phi^n$$

**ทำไมช่วย Stability?**
- เพิ่ม $\frac{\rho V}{\Delta t}$ เข้า diagonal → diagonal ใหญ่ขึ้น
- $\Delta t$ เล็ก → contribution มาก → stable มากขึ้น
- นี่คือเหตุผลว่าทำไม **ลด $\Delta t$ ช่วยแก้ divergence**

---

## OpenFOAM Implementation

### fvm vs fvc: ความแตกต่างที่สำคัญมาก

| Prefix | ชื่อเต็ม | ผลลัพธ์ | ใช้เมื่อ |
|--------|---------|---------|---------|
| `fvm::` | Finite Volume Method | → Matrix ($a_P$, $a_N$) | Unknown (กำลังหา) |
| `fvc::` | Finite Volume Calculus | → Field (ตัวเลขทันที) | Known (รู้ค่าแล้ว) |

> **ทำไมต้องแยก?**
> - **fvm:** $\phi$ ยังไม่รู้ → ต้องเก็บเป็น coefficient ใน matrix
> - **fvc:** $\phi$ รู้แล้ว → คำนวณเป็นตัวเลขได้เลย → ใส่ source

**ตัวอย่าง:**

```cpp
fvVectorMatrix UEqn
(
    fvm::ddt(rho, U)              // U ไม่รู้ → เข้า Diagonal
  + fvm::div(phi, U)              // U ไม่รู้ → เข้า Diagonal + Off-diagonal
  - fvm::laplacian(mu, U)         // U ไม่รู้ → เข้า Diagonal + Off-diagonal
 ==
    -fvc::grad(p)                 // p รู้แล้ว → คำนวณเป็น Source vector
);
```

### สมการโมเมนตัม

$$\rho\frac{\partial \mathbf{u}}{\partial t} + \nabla \cdot (\rho \mathbf{u} \mathbf{u}) = -\nabla p + \nabla \cdot (\mu \nabla \mathbf{u})$$

```cpp
fvVectorMatrix UEqn
(
    fvm::ddt(rho, U)           // Temporal
  + fvm::div(phi, U)           // Convection
  - fvm::laplacian(mu, U)      // Diffusion
);

// Pressure coupling: solve พร้อม pressure gradient
solve(UEqn == -fvc::grad(p));
```

**ทำไม `fvc::grad(p)`?**
- p มาจาก pressure correction (SIMPLE/PISO) = รู้ค่าแล้ว
- ใส่เป็น explicit source ใน RHS

### สมการ Energy

```cpp
fvScalarMatrix TEqn
(
    rho*cp*fvm::ddt(T)
  + rho*cp*fvm::div(phi, T)
  - fvm::laplacian(k, T)
 ==
    Q   // Heat source (explicit)
);
TEqn.solve();
```

---

## Boundary Conditions

| BC Type | ผลต่อ Matrix | ทำไม |
|---------|-------------|------|
| `fixedValue` | แก้ไข $a_P$, $b_P$ | ค่าที่ขอบถูกกำหนด → ใส่เป็น constraint |
| `zeroGradient` | ไม่มี off-diagonal ที่ boundary | $\phi_{boundary} = \phi_P$ → ไม่มี neighbor |
| `mixed` | แก้ไขทั้งคู่ | ผสม Dirichlet + Neumann |

**ตัวอย่าง fixedValue:**

```cpp
// 0/U
inlet
{
    type    fixedValue;
    value   uniform (10 0 0);  // → เพิ่มเข้า source b_P
}
```

---

## Sparse Matrix Structure

Matrix $[A]$ มีโครงสร้าง **Sparse** เพราะ:
- แต่ละ Cell เชื่อมต่อกับ **Neighbors เท่านั้น** (ไม่ใช่ทุก Cell)
- Non-zero entries ≈ 6-20 ต่อแถว (3D hexahedral)

```
         Cell 0   1   2   3   4   5   6  ...
Cell 0: [a_P  a_N  0   a_N  0   0   0  ...]
Cell 1: [a_N  a_P  a_N  0   a_N  0   0  ...]
...
```

**ทำไม Sparse สำคัญ?**
- ไม่ต้องเก็บ zeros → ประหยัด memory O(N) แทน O(N²)
- Iterative solvers ใช้ sparse format → เร็วมาก

---

## Linear Solvers

### Solver Selection

| Solver | Matrix Type | ใช้กับ | ทำไม |
|--------|-------------|--------|------|
| **GAMG** | Symmetric | p (pressure) | Multigrid → ลด error ทุกระดับพร้อมกัน |
| **PCG** | Symmetric PD | p (alternative) | Conjugate Gradient |
| **PBiCGStab** | Asymmetric | U, k, ε | Convection ทำให้ asymmetric |
| **smoothSolver** | Any | เล็ก/ง่าย | Simple Gauss-Seidel |

### ตั้งค่าใน `system/fvSolution`

```cpp
solvers
{
    p
    {
        solver      GAMG;           // Multigrid for Laplacian
        smoother    GaussSeidel;    // Pre/post-smoothing
        tolerance   1e-6;           // Absolute convergence
        relTol      0.01;           // Relative (stop after 100x reduction)
    }
    pFinal
    {
        $p;                         // Copy settings from p
        relTol      0;              // ต้อง converge ถึง tolerance
    }
    U
    {
        solver      PBiCGStab;      // For asymmetric matrix
        preconditioner DILU;        // Incomplete LU (สำหรับ asymmetric)
        tolerance   1e-5;
        relTol      0.1;
    }
}
```

### Relaxation: ทำไมต้องใช้?

**ปัญหา:** SIMPLE algorithm ไม่ stable ถ้าใช้ค่าใหม่ทั้งหมด

**ทางออก:** ผสมค่าเก่ากับค่าใหม่

$$\phi_{new} = \alpha \cdot \phi_{calculated} + (1-\alpha) \cdot \phi_{old}$$

```cpp
relaxationFactors
{
    fields
    {
        p       0.3;    // Pressure: ค่อยๆ เปลี่ยน (sensitive)
    }
    equations
    {
        U       0.7;    // Velocity: เปลี่ยนเร็วกว่าได้
        k       0.7;
        epsilon 0.7;
    }
}
```

**ทำไม p ใช้ค่าต่ำ (0.3)?**
- Pressure correction โดนเกินไป (over-correction) → oscillate
- ค่าต่ำ = "ค่อยๆ เชื่อ" → stable แต่ช้าหน่อย

---

## Source Terms

### Explicit Source

```cpp
fvScalarMatrix TEqn(...)
 == Q;  // Q เป็น volScalarField → เข้า source vector b
```

### Semi-Implicit Source (แนะนำ!)

$$S = S_u + S_p \cdot \phi$$

```cpp
fvScalarMatrix TEqn
(
    ...
 ==
    Su                       // Explicit part → b_P
  + fvm::Sp(Sp, T)          // Implicit part → a_P
);
```

**ทำไม Semi-Implicit ดีกว่า?**
- ถ้า $S_p < 0$ → เพิ่ม diagonal → **stable ขึ้น**
- ตัวอย่าง: Linearized reaction $S = -k\phi$ → ใส่ $-k$ เป็น Sp

---

## Debugging Tips

### 1. Divergence

```
--> FOAM FATAL ERROR: Maximum number of iterations exceeded
```

**สาเหตุ:** Matrix ไม่ stable พอ

**ลองทำ:**
- ลด `deltaT` → เพิ่ม temporal contribution ใน diagonal
- ลด `relTol` (0.1 → 0.01) → converge แน่นขึ้น
- ลด relaxation (0.7 → 0.5) → เปลี่ยนช้าลง

### 2. ช้ามาก

**ลองทำ:**
- เปลี่ยน solver (smoothSolver → GAMG สำหรับ p)
- เพิ่ม `relTol` (0.01 → 0.1) สำหรับ intermediate iterations

### 3. Check Residuals

```bash
foamLog log.simpleFoam
gnuplot residuals
```

**Residual ที่ดี:**
- ลดลงอย่างต่อเนื่อง (monotonic decrease)
- ลดได้ 4-6 orders of magnitude

---

## Concept Check

<details>
<summary><b>1. fvm กับ fvc ต่างกันอย่างไร? ใช้เมื่อไหร่?</b></summary>

| | fvm | fvc |
|-|-----|-----|
| Output | Matrix coefficients | Field values |
| ใช้กับ | Unknown (กำลังจะหา) | Known (รู้แล้ว) |
| ตัวอย่าง | `fvm::ddt(U)` | `fvc::grad(p)` |

**Rule:** ถ้าตัวแปรอยู่ใน LHS ของสมการที่กำลัง solve → ใช้ fvm
</details>

<details>
<summary><b>2. ทำไม GAMG เร็วกว่า PCG สำหรับ pressure?</b></summary>

**GAMG** = Geometric Algebraic Multigrid

- **PCG:** ลด error ทีละ frequency → ต้อง iterate มาก
- **GAMG:** ลด error ทุก frequency พร้อมกัน (coarse grid จัดการ low frequency)

Pressure = Laplacian equation → information ต้องเดินทางไกล (elliptic)
GAMG "เห็น" ทั้งโดเมนจาก coarse grid → converge เร็วมาก
</details>

<details>
<summary><b>3. relaxation 0.3 กับ 0.7 ต่างกันอย่างไร?</b></summary>

$$\phi_{new} = \alpha \cdot \phi_{calculated} + (1-\alpha) \cdot \phi_{old}$$

| α | การเปลี่ยนแปลง | Stability | Speed |
|---|---------------|-----------|-------|
| 0.3 | เปลี่ยน 30% | สูง | ช้า |
| 0.7 | เปลี่ยน 70% | ต่ำ | เร็ว |

- **Pressure (α=0.3):** sensitive → ต้องค่อยๆ เปลี่ยน
- **Velocity (α=0.7):** stable กว่า → เปลี่ยนเร็วได้
</details>

<details>
<summary><b>4. ทำไมลด Δt ช่วยแก้ divergence?</b></summary>

Temporal term เพิ่ม diagonal:
$$a_P += \frac{\rho V}{\Delta t}$$

$\Delta t$ เล็ก → $\frac{\rho V}{\Delta t}$ ใหญ่ → diagonal dominant มากขึ้น → stable
</details>

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [04_Temporal_Discretization.md](04_Temporal_Discretization.md) — Temporal Discretization
- **บทถัดไป:** [06_OpenFOAM_Implementation.md](06_OpenFOAM_Implementation.md) — OpenFOAM Implementation
- **Troubleshooting:** [07_Best_Practices.md](07_Best_Practices.md) — Best Practices