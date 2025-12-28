# Spatial Discretization

การแปลง Spatial Derivatives เป็นสมการพีชคณิตโดยใช้ค่าที่ Cell Centers และ Faces

---

## Mesh Structure

### Cell-Centered Approach

ค่าตัวแปรเก็บที่ **Cell Centers** (P, N) แต่ต้อง Interpolate ไปที่ **Face** (f) เพื่อคำนวณ Flux

```
     Cell P          Face f         Cell N
       ●───────────────■───────────────●
      φ_P             φ_f            φ_N
    (stored)      (interpolate)    (stored)
```

| Mesh Type | ลักษณะ | ผลกระทบ |
|-----------|--------|---------|
| **Orthogonal** | d_PN ⊥ S_f | Gradient คำนวณง่าย |
| **Non-orthogonal** | d_PN ∠ S_f | ต้องใช้ correction |

**ตรวจสอบ:** `checkMesh` → ดู `Max non-orthogonality` (ควร < 70°)

---

## Convective Term

$$\nabla \cdot (\phi \mathbf{u}) \rightarrow \sum_f \phi_f \Phi_f$$

โดย $\Phi_f = \mathbf{u}_f \cdot \mathbf{S}_f$ = Volumetric Flux

### Interpolation Schemes

| Scheme | สูตร $\phi_f$ | Order | เสถียร | Applied |
|--------|--------------|-------|--------|---------|
| **Upwind** | $\phi_P$ (if $\Phi_f > 0$) | 1 | ✅ | เริ่มต้น, High Pe |
| **Linear** | $\frac{1}{2}(\phi_P + \phi_N)$ | 2 | ❌ | Laminar |
| **Linear Upwind** | Upwind + Gradient correction | 2 | ✅ | ทั่วไป |
| **Van Leer** | TVD limiter | 2 | ✅ | Compressible |

**ตั้งค่าใน `system/fvSchemes`:**

```cpp
divSchemes
{
    div(phi,U)      Gauss linearUpwind grad(U);  // แนะนำ
    div(phi,k)      Gauss upwind;                // เสถียร
    div(phi,T)      Gauss limitedLinear 1;       // TVD
}
```

### เลือก Scheme อย่างไร?

```
Upwind ←──────────────────────────→ Linear
(Stable, Diffusive)          (Accurate, Oscillatory)
         ↑
    LinearUpwind / TVD
    (Best of both)
```

---

## Diffusive Term

$$\nabla \cdot (D \nabla \phi) \rightarrow \sum_f D_f \frac{\phi_N - \phi_P}{|d_{PN}|} |S_f|$$

### Orthogonal Mesh

$$(D \nabla \phi)_f \cdot \mathbf{S}_f = D_f \frac{\phi_N - \phi_P}{|d_{PN}|} |S_f|$$

### Non-Orthogonal Mesh

ต้องเพิ่ม correction:

$$(D \nabla \phi)_f \cdot \mathbf{S}_f = D_f \frac{\phi_N - \phi_P}{|d_{PN}|} |S_f| + \underbrace{D_f (\nabla \phi)_f \cdot \mathbf{k}}_{\text{correction}}$$

**ตั้งค่าใน `system/fvSchemes`:**

```cpp
laplacianSchemes
{
    default         Gauss linear corrected;   // มี correction
    // หรือ
    default         Gauss linear uncorrected; // ไม่มี (เร็วกว่า)
}
```

**เพิ่ม iterations ใน `system/fvSolution`:**

```cpp
SIMPLE
{
    nNonOrthogonalCorrectors 2;  // สำหรับ non-ortho mesh
}
```

---

## Gradient Calculation

$$\nabla \phi_P \approx \frac{1}{V_P} \sum_f \phi_f \mathbf{S}_f$$

**Schemes:**

| Scheme | ข้อดี | ใช้เมื่อ |
|--------|------|---------|
| `Gauss linear` | Standard, เร็ว | Orthogonal mesh |
| `leastSquares` | แม่นยำ | Non-orthogonal mesh |

```cpp
gradSchemes
{
    default         Gauss linear;
    grad(U)         cellLimited Gauss linear 1;  // Limited
}
```

---

## Matrix Assembly

หลัง discretize ได้สมการสำหรับ Cell P:

$$a_P \phi_P + \sum_N a_N \phi_N = b_P$$

โดย:
- $a_P$ = Diagonal coefficient (จาก Cell P)
- $a_N$ = Off-diagonal coefficients (จาก Neighbors)
- $b_P$ = Source term

**คุณสมบัติ:**
- **Diagonal Dominance**: $|a_P| \geq \sum|a_N|$ → เสถียร
- **Sparse**: ส่วนใหญ่เป็น 0

---

## Boundary Conditions

| Type | คำอธิบาย | OpenFOAM | ผลต่อ Matrix |
|------|---------|----------|-------------|
| **Dirichlet** | Fixed value | `fixedValue` | แก้ไข $a_P$, $b_P$ |
| **Neumann** | Fixed gradient | `zeroGradient` | แก้ไข $b_P$ |
| **Mixed** | Value + Gradient | `mixed` | แก้ไขทั้งคู่ |

**ตัวอย่าง `0/U`:**

```cpp
boundaryField
{
    inlet  { type fixedValue; value uniform (10 0 0); }
    outlet { type zeroGradient; }
    walls  { type noSlip; }
}
```

---

## Linear Solvers

ระบบ $[A][\phi] = [b]$ ถูกแก้โดย:

| Solver | ใช้กับ | ข้อดี |
|--------|-------|------|
| `GAMG` | p (pressure) | เร็วมาก |
| `PCG` | Symmetric | เสถียร |
| `PBiCGStab` | Asymmetric | ทั่วไป |
| `smoothSolver` | ง่ายๆ | เร็ว |

**ตั้งค่าใน `system/fvSolution`:**

```cpp
solvers
{
    p
    {
        solver      GAMG;
        tolerance   1e-6;
        relTol      0.01;
        smoother    GaussSeidel;
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

---

## สรุป Scheme Recommendations

| Term | Scheme แนะนำ | เหตุผล |
|------|-------------|--------|
| Convection U | `linearUpwind grad(U)` | 2nd order + stable |
| Convection k, ε | `upwind` | Turbulence sensitive |
| Diffusion | `linear corrected` | Standard |
| Gradient | `Gauss linear` | Standard |
| Time | `backward` (2nd) หรือ `Euler` (1st) | ตามความต้องการ |

---

## Concept Check

<details>
<summary><b>1. Upwind vs Linear ต่างกันอย่างไร?</b></summary>

- **Upwind**: ใช้ค่าจาก upstream → เสถียรแต่ diffusive (smear sharp gradients)
- **Linear**: เฉลี่ยทั้งสอง → แม่นยำแต่อาจ oscillate
</details>

<details>
<summary><b>2. เมื่อไหร่ต้องใช้ Non-orthogonal Correction?</b></summary>

เมื่อ mesh มี non-orthogonality > 40° เพื่อให้ gradient ที่ face ถูกต้อง ตั้ง `nNonOrthogonalCorrectors > 0`
</details>

<details>
<summary><b>3. ทำไม Turbulence fields (k, ε) มักใช้ Upwind?</b></summary>

เพราะ k, ε มีค่าเป็นบวกเสมอ (physical constraint) Higher-order schemes อาจทำให้เกิดค่าลบ → diverge
</details>

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [02_Fundamental_Concepts.md](02_Fundamental_Concepts.md) — แนวคิดพื้นฐาน
- **บทถัดไป:** [04_Temporal_Discretization.md](04_Temporal_Discretization.md) — Temporal Discretization