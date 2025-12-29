# Spatial Discretization

การแปลง Spatial Derivatives เป็นสมการพีชคณิตโดยใช้ค่าที่ Cell Centers และ Faces

> **ทำไมต้อง discretize?**
> คอมพิวเตอร์ไม่เข้าใจ $\nabla$ หรือ $\partial/\partial x$ แต่เข้าใจ "ลบ" กับ "หาร"
> 
> Discretization = แปลงอนุพันธ์เป็นผลต่างของค่าที่จุดต่างๆ

---

## Mesh Structure

### Cell-Centered Approach

**ปัญหาพื้นฐาน:** เก็บค่าที่ Cell Centers แต่ต้องคำนวณ Flux ที่ Face

```
     Cell P          Face f         Cell N
       ●───────────────■───────────────●
      φ_P             φ_f            φ_N
    (stored)      (ต้องเดา!)       (stored)
```

**วิธีแก้:** ใช้ Interpolation Scheme เพื่อ "เดา" ค่า $\phi_f$ จาก $\phi_P$ และ $\phi_N$

### Orthogonality: ทำไมสำคัญ?

<!-- IMAGE: IMG_01_003 -->
<!-- 
Purpose: เพื่ออธิบายว่าทำไม "Orthogonality" ถึงสำคัญมากใน FVM โดยเปรียบเทียบกรณี "อุดมคติ" (Orthogonal) ที่เวกเตอร์เชื่อมศูนย์กลาง (d) ขนานกับเวกเตอร์พื้นที่หน้าตัด (Sf) ทำให้คำนวณ Gradient ได้แม่นยำ กับกรณี "ความเป็นจริง" (Non-Orthogonal) ที่มีมุมเบี่ยงเบน (theta) ทำให้ต้องแตกแรงและบวกเทอมแก้ (Non-orthogonal correction) ซึ่งเพิ่ม cost และลด stability
Prompt: "Detailed technical comparison diagram of Finite Volume Mesh Geometry. **Left Panel (Ideal):** 'Orthogonal Mesh' - Two rectangular cells perfectly aligned. The vector connecting centers ($\mathbf{d}$) is PERFECTLY PARALLEL to the face area vector ($\mathbf{S}_f$). Green checkmark indicating 'Simple & Accurate'. **Right Panel (Reality):** 'Non-Orthogonal Mesh' - Two skewed/rhomboid cells. The vector $\mathbf{d}$ intersects $\mathbf{S}_f$ at a significant angle $\theta$. Show vector decomposition: $\mathbf{S}_f = \mathbf{\Delta} \text{ (Orthogonal part)} + \mathbf{k} \text{ (Correction part)}$. Red alert icon indicating 'Correction Required'. STYLE: Precision engineering blueprint style, blue and black ink on white paper, very sharp thin lines. Mathematical notations in LaTeX font."
-->
![[IMG_01_003.jpg]]

| Mesh Type | ลักษณะ | ผลกระทบ |
|-----------|--------|---------|
| **Orthogonal** | $d_{PN} \perp S_f$ | Gradient คำนวณถูกต้องทันที |
| **Non-orthogonal** | $d_{PN} \angle S_f$ | Gradient ผิด → ต้อง correction |

> **💡 คิดแบบนี้:**
> ถ้า mesh เบี้ยว เหมือนเดินทแยง — ระยะทางที่วัดได้ไม่ใช่ระยะจริง ต้องแก้ไข

**ตรวจสอบ:** `checkMesh` → ดู `Max non-orthogonality`
- < 40°: ดี ไม่ต้อง correction
- 40-70°: ต้อง correction
- > 70°: อันตราย อาจ diverge

---

## Convective Term: การพาพาสาร

$$\nabla \cdot (\phi \mathbf{u}) \rightarrow \sum_f \phi_f \Phi_f$$

โดย $\Phi_f = \mathbf{u}_f \cdot \mathbf{S}_f$ = Volumetric Flux (m³/s)

> **ทำไม Convection ยากที่สุด?**
> 1. **Nonlinear:** $u$ คูณ $\phi$ (ถ้า $\phi = u$ ก็ยิ่งซับซ้อน)
> 2. **Information travels:** ข้อมูลไหลไปทิศทางเดียว → ต้องรู้ว่า "upstream" อยู่ไหน
> 3. **Unbounded:** ค่าอาจพุ่งสูงมาก → oscillation → blow up

### Interpolation Schemes

**ทางเลือกหลักมี 2 ขั้ว:**

<!-- IMAGE: IMG_01_004 -->
<!-- 
Purpose: เพื่อเปรียบเทียบพฤติกรรมของ Interpolation Schemes หลัก 3 ตัว (Upwind, Linear, Central) เมื่อเจอการเปลี่ยนแปลงค่าแบบ "กระทันหัน" (Step Change). ภาพนี้ต้องสื่อว่า Upwind "เบลอ" (Diffusion), Linear "แกว่ง" (Dispersion), และ Limiters (TVD) คือทางสายกลางที่ "คมและไม่แกว่ง"
Prompt: "Scientific data plot comparing CFD convection schemes on a 1D step problem. **X-axis:** Space, **Y-axis:** Value $\phi$. **Key Elements:** 1. **True Solution (Black Dashed):** A square wave / sharp step function. 2. **Upwind (Blue Curve):** Smooth, smeared slope showing 'Numerical Diffusion' (Safe but blurry). 3. **Central/Linear (Red Curve):** Sharp slope but with wavy 'Oscillations' near the step showing numerical dispersion (Unstable). 4. **TVD/Limited (Green Curve):** Matches the step closely without oscillations (Accurate & Stable). STYLE: Clean Matplotlib/Python-style scientific plot, with a legend, grid lines, and clear annotations pointing to 'Diffusion' vs 'Oscillation'. High contrast colors."
-->
![[IMG_01_004.jpg]]

| Scheme | วิธีคำนวณ $\phi_f$ | Accuracy | Stability |
|--------|-------------------|----------|-----------|
| **Upwind** | ใช้ค่า upstream เท่านั้น | 1st | ✅ สูงมาก |
| **Linear** | เฉลี่ย $\frac{1}{2}(\phi_P + \phi_N)$ | 2nd | ❌ อาจสั่น |
| **Linear Upwind** | Upwind + gradient correction | 2nd | ✅ ดี |
| **TVD (limitedLinear)** | ใช้ limiter ป้องกัน overshoot | 2nd | ✅ ดีมาก |

**ตั้งค่าใน `system/fvSchemes`:**

```cpp
divSchemes
{
    // Velocity - ต้องการทั้งความแม่นยำและเสถียรภาพ
    div(phi,U)      Gauss linearUpwind grad(U);
    
    // Turbulence - ต้องการเสถียรภาพ (k,ε ต้อง > 0 เสมอ)
    div(phi,k)      Gauss upwind;
    div(phi,epsilon) Gauss upwind;
    
    // Scalar - TVD ป้องกัน overshoots
    div(phi,T)      Gauss limitedLinear 1;
}
```

---

## Diffusive Term: การแพร่กระจาย

$$\nabla \cdot (D \nabla \phi) \rightarrow \sum_f D_f \frac{\phi_N - \phi_P}{|d_{PN}|} |S_f|$$

> **ทำไม Diffusion ง่ายกว่า Convection?**
> - Diffusion เป็น **self-stabilizing:** ค่าสูงแพร่ไปหาค่าต่ำ → ทำให้เรียบ
> - ไม่มี "ทิศทาง" → ใช้ central difference ได้

### Orthogonal vs Non-Orthogonal Mesh

**Orthogonal Mesh:** ใช้สูตรตรงๆ ได้เลย

$$(D \nabla \phi)_f \cdot \mathbf{S}_f = D_f \frac{\phi_N - \phi_P}{|d_{PN}|} |S_f|$$

**Non-Orthogonal Mesh:** ต้องเพิ่ม correction

$$(D \nabla \phi)_f \cdot \mathbf{S}_f = \underbrace{D_f \frac{\phi_N - \phi_P}{|d_{PN}|} |\mathbf{S}_f|}_{\text{orthogonal part}} + \underbrace{D_f (\nabla \phi)_f \cdot \mathbf{k}}_{\text{correction}}$$

> **⚠️ หมายเหตุ:** ในสูตรด้านบน:
> - $|\mathbf{S}_f|$ คือขนาด (magnitude) ของ face area vector
> - $\mathbf{k} = \mathbf{S}_f - \boldsymbol{\Delta}$ คือ non-orthogonal component (เศษที่เหลือหลังลบส่วนที่ขนานกับ $d_{PN}$)

### ตัวอย่างการคำนวณ Non-Orthogonal Correction

**Problem:** 2D mesh ที่ face เอียงมุม θ = 30° จากแนว perpendicular

```
       Cell N
          ●
         /|
        / |
    d   /  |
    P N/   |Δ  (orthogonal component, ขนานกับ d_PN)
     /     |
    / θ    |
  ●────────■
 Cell P   Face f

d_PN = distance ระหว่าง cell centers = 0.01 m
θ = 30° (non-orthogonality angle)
```

**Step 1: คำนวณส่วน orthogonal**
$$|\mathbf{S}_f| \approx 0.001 \text{ m}^2$$
$$\Delta = |\mathbf{S}_f| \cdot \cos(30°) = 0.001 \times 0.866 = 0.000866 \text{ m}$$

Orthogonal flux (ส่วนแรก):
$$\Phi_{\text{ortho}} = D \frac{\phi_N - \phi_P}{d_{PN}} |\mathbf{S}_f|$$
$$\Phi_{\text{ortho}} = 0.001 \times \frac{5 - 3}{0.01} \times 0.001 = 0.2$$

**Step 2: คำนวณ correction**
$$\mathbf{k} = \mathbf{S}_f - \boldsymbol{\Delta} = 0.000134 \text{ m}^2 \text{ (magnitude)}$$

Correction term:
$$\Phi_{\text{corr}} = D (\nabla \phi)_f \cdot \mathbf{k}$$

ถ้า $(\nabla \phi)_f = 200 \text{ m}^{-1}$:
$$\Phi_{\text{corr}} = 0.001 \times 200 \times 0.000134 = 0.0000268$$

**Step 3: รวมสองส่วน**
$$\Phi_{\text{total}} = 0.2 + 0.0000268 \approx 0.200027$$

ในกรณีนี้ correction มีค่าน้อยมาก (~0.01%) เพราะ θ = 30° ยังไม่มากนัก

**ถ้า θ = 70° (mesh เบี้ยวมาก):**
- Correction อาจถึง 20-30% ของ orthogonal part
- **ต้องใช้ `nNonOrthogonalCorrectors` หลายรอบ**

**ตั้งค่าใน `fvSchemes` และ `fvSolution`:**

```cpp
// fvSchemes
laplacianSchemes
{
    default    Gauss linear corrected;    // มี correction
}

// fvSolution - ต้องวน correction loop
SIMPLE
{
    nNonOrthogonalCorrectors 2;  // วน 2 รอบ
}
```

---

## Gradient Calculation

$$\nabla \phi_P \approx \frac{1}{V_P} \sum_f \phi_f \mathbf{S}_f$$

| Scheme | ใช้เมื่อ | ข้อดี |
|--------|---------|------|
| `Gauss linear` | Orthogonal mesh | เร็ว standard |
| `leastSquares` | Non-orthogonal mesh | แม่นยำกว่า |

```cpp
gradSchemes
{
    default         Gauss linear;
    grad(U)         cellLimited Gauss linear 1;  // จำกัดไม่ให้เกินค่าสูงสุด
}
```

---

## Boundary Conditions: ผลต่อ Matrix

| Type | กำหนด | OpenFOAM | ผลต่อ Matrix |
|------|-------|----------|--------------|
| **Dirichlet** | ค่าที่ขอบ | `fixedValue` | แก้ $a_P$, $b_P$ |
| **Neumann** | gradient ที่ขอบ | `zeroGradient` | แก้ $b_P$ เท่านั้น |

**ตัวอย่าง `0/U`:**

```cpp
boundaryField
{
    inlet  { type fixedValue; value uniform (10 0 0); }  // กำหนด U
    outlet { type zeroGradient; }                         // ปล่อยไหลอิสระ
    walls  { type noSlip; }                               // U = 0
}
```

---

## Linear Solvers

หลัง discretize ได้ระบบ $[A][\phi] = [b]$ ต้องใช้ iterative solver

| Solver | ใช้กับ | ทำไม |
|--------|-------|------|
| **GAMG** | Pressure | เร็วมาก สำหรับ Laplacian equation |
| **PCG** | Symmetric matrix | Conjugate Gradient |
| **PBiCGStab** | Asymmetric | ทั่วไป (U, k, ε) |

```cpp
solvers
{
    p
    {
        solver      GAMG;
        tolerance   1e-6;
        relTol      0.01;    // ยอมแค่ลด 100 เท่า ต่อ iteration
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
| Convection k, ε | `upwind` | ค่าต้อง > 0 เสมอ |
| Diffusion | `linear corrected` | Standard + non-ortho safe |
| Gradient | `Gauss linear` | เร็ว standard |
| Time | `backward` (transient accurate) หรือ `Euler` (simple) | ตามความต้องการ |

---

## Concept Check

<details>
<summary><b>1. Upwind vs Linear ต่างกันอย่างไร? ทำไมถึงสำคัญ?</b></summary>

- **Upwind**: ใช้ค่าจาก upstream เท่านั้น → เสถียรแต่ **diffusive** (เบลอ sharp fronts)
- **Linear**: เฉลี่ยทั้งสองฝั่ง → แม่นยำแต่อาจ **oscillate** (ค่าสั่นเกิน/ต่ำกว่าที่ควร)

**ทำไมสำคัญ:** เลือกผิดอาจทำให้:
- Upwind มากไป → ผลลัพธ์เบลอ ไม่เห็นรายละเอียด
- Linear เมื่อ flow แรง → oscillation → diverge
</details>

<details>
<summary><b>2. เมื่อไหร่ต้องใช้ Non-orthogonal Correction?</b></summary>

เมื่อ `checkMesh` แสดง non-orthogonality > 40°:

```
Max non-orthogonality = 55 degrees.
```

**วิธีแก้:** ตั้ง `nNonOrthogonalCorrectors` ใน `fvSolution`:
- 40-60°: ใช้ 1-2
- 60-70°: ใช้ 2-3
- > 70°: ควรปรับ mesh ใหม่
</details>

<details>
<summary><b>3. ทำไม Turbulence fields (k, ε) มักใช้ Upwind?</b></summary>

เพราะ physical constraint: **k, ε ต้อง > 0 เสมอ**

- Higher-order schemes อาจทำให้เกิด undershoots → **ค่าลบ**
- ค่าลบใน k หรือ ε → คำนวณ $\nu_t$ ไม่ได้ → **diverge**

Upwind = safe แม้ diffusive เล็กน้อย ก็ยังดีกว่า diverge
</details>

<details>
<summary><b>4. GAMG ทำไมเร็วสำหรับ Pressure?</b></summary>

**GAMG** = Geometric Algebraic MultiGrid

หลักการ: แก้สมการบน coarse mesh ก่อน → prolong ลงมา fine mesh

ทำไมเหมาะกับ p:
- Pressure equation = Laplacian (elliptic) → information travels globally
- GAMG "เห็น" ทั้งโดเมนจาก coarse level → converge เร็วมาก
</details>

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [02_Fundamental_Concepts.md](02_Fundamental_Concepts.md) — แนวคิดพื้นฐาน
- **บทถัดไป:** [04_Temporal_Discretization.md](04_Temporal_Discretization.md) — Temporal Discretization
- **ประยุกต์:** [06_OpenFOAM_Implementation.md](06_OpenFOAM_Implementation.md) — การ implement ใน OpenFOAM