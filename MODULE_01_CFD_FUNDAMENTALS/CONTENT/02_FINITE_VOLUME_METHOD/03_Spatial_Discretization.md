# Spatial Discretization

การแปลง Spatial Derivatives เป็นสมการพีชคณิตโดยใช้ค่าที่ Cell Centers และ Faces

> **ทำไมต้อง discretize?**
> คอมพิวเตอร์ไม่เข้าใจ $\nabla$ หรือ $\partial/\partial x$ แต่เข้าใจ "ลบ" กับ "หาร"
> 
> Discretization = แปลงอนุพันธ์เป็นผลต่างของค่าที่จุดต่างๆ

## Prerequisites

⚠️ **ควรอ่านก่อน:** [02_Fundamental_Concepts.md](02_Fundamental_Concepts.md) เพื่อความเข้าใจเรื่อง:
- Finite Volume Method basics
- Conservation laws in FVM
- Mesh structure terminology

## Learning Objectives

หลังจากอ่านบทนี้ คุณจะสามารถ:
- **อธิบาย** ความแตกต่างระหว่าง convection และ diffusion schemes
- **เลือก** interpolation scheme ที่เหมาะสมกับปัญหาที่แก้
- **คำนวณ** non-orthogonal correction สำหรับ mesh ที่ไม่สมมาตร
- **แก้ปัญหา** numerical instability จากการเลือก scheme ที่ไม่เหมาะสม

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

### ตัวอย่างการคำนาณ Non-Orthogonal Correction

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

> **📖 ดูเพิ่มเติม:** รายละเอียด boundary conditions ที่ [06_OpenFOAM_Implementation.md](06_OpenFOAM_Implementation.md)

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

> **📖 ดูเพิ่มเติม:** รายละเอียด solver algorithms และ parameter tuning ที่ [05_Linear_Solvers_Matrix_Assembly.md](05_Linear_Solvers_Matrix_Assembly.md)

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

## Scheme Recommendations Summary

| Term | Scheme แนะนำ | เหตุผล |
|------|-------------|--------|
| Convection U | `linearUpwind grad(U)` | 2nd order + stable |
| Convection k, ε | `upwind` | ค่าต้อง > 0 เสมอ |
| Diffusion | `linear corrected` | Standard + non-ortho safe |
| Gradient | `Gauss linear` | เร็ว standard |
| Time | `backward` (transient accurate) หรือ `Euler` (simple) | ตามความต้องการ |

---

## Troubleshooting: Common Spatial Scheme Errors

| Error Message | สาเหตุที่เป็นไปได้ | วิธีแก้ |
|--------------|------------------|---------|
| `--> FOAM FATAL ERROR: Maximum number of iterations exceeded` | Scheme ไม่ converge หรือ tolerance เข้มไป | ลอง: (1) เปลี่ยนเป็น upwind, (2) เพิ่ม tolerance, (3) ลด under-relaxation |
| `Negative value found in XXX field` | Undershoot จาก high-order scheme | เปลี่ยนเป็น upwind หรือ limitedLinear |
| `Unbounded value in turbulence field` | k หรือ ε ติดลบ | ใช้ upwind สำหรับ turbulence fields |
| `checkMesh: non-orthogonality > 70 degrees` | Mesh เบี้ยวมากเกินไป | (1) เพิ่ม nNonOrthogonalCorrectors, (2) สร้าง mesh ใหม่ |
| `Solution diverges after first iteration` | Convection scheme ไม่เสถียร | เปลี่ยนจาก linear เป็น upwind หรือ linearUpwind |
| `Oscillations near sharp gradients` | Scheme ไม่มี limiter | ใช้ limitedLinear หรือ TVD scheme |

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

---

## 10. Cylindrical Coordinate FVM for R410A Tube Flow
## 10. การแบ่งส่วน FVM ในพิกัดทรงกระบอกสำหรับการไหล R410A ในท่อ

> **🔧 R410A Evaporator Focus**
>
> สำหรับเครื่องระเหย R410A การไหลของสารทำความเย็นอยู่ในท่อวงกลม (รัศมี ~5mm, ความยาว ~1-10m) พิกัดทรงกระบอก $(r, \theta, z)$ เป็นพิกัดธรรมชาติ:

### 10.1 ตัวดำเนินการเชิงอนุพันธ์ในพิกัดทรงกระบอก

**Gradient:**
$$
\nabla \phi = \frac{\partial \phi}{\partial r}\hat{\mathbf{r}} + \frac{1}{r}\frac{\partial \phi}{\partial \theta}\hat{\boldsymbol{\theta}} + \frac{\partial \phi}{\partial z}\hat{\mathbf{z}}
$$

**Divergence:**
$$
\nabla \cdot \mathbf{U} = \frac{1}{r}\frac{\partial}{\partial r}(r U_r) + \frac{1}{r}\frac{\partial U_\theta}{\partial \theta} + \frac{\partial U_z}{\partial z}
$$

**Laplacian:**
$$
\nabla^2 \phi = \frac{1}{r}\frac{\partial}{\partial r}\left(r\frac{\partial \phi}{\partial r}\right) + \frac{1}{r^2}\frac{\partial^2 \phi}{\partial \theta^2} + \frac{\partial^2 \phi}{\partial z^2}
$$

### 10.2 การลดรูปแบบสมมาตรแนวแกน (Axisymmetric)

สำหรับเครื่องระเหย R410A ส่วนใหญ่ flow เป็น **axisymmetric** ($\partial/\partial\theta = 0$, $U_\theta = 0$):

$$
\nabla \phi = \frac{\partial \phi}{\partial r}\hat{\mathbf{r}} + \frac{\partial \phi}{\partial z}\hat{\mathbf{z}}
$$

$$
\nabla \cdot \mathbf{U} = \frac{1}{r}\frac{\partial}{\partial r}(r U_r) + \frac{\partial U_z}{\partial z}
$$

$$
\nabla^2 \phi = \frac{1}{r}\frac{\partial}{\partial r}\left(r\frac{\partial \phi}{\partial r}\right) + \frac{\partial^2 \phi}{\partial z^2}
$$

### 10.3 เรขาคณิตของปริมาตรควบคุม

สำหรับ cell ที่จุด $(r_c, z_c)$ พร้อมขนาด $\Delta r$ และ $\Delta z$:

**ปริมาตร:**
$$
V_{cell} = \int_{r_c-\Delta r/2}^{r_c+\Delta r/2} \int_0^{2\pi} \int_{z_c-\Delta z/2}^{z_c+\Delta z/2} r \, dr \, d\theta \, dz = 2\pi r_c \Delta r \Delta z
$$

**พื้นที่ผิว:**
- หน้ารัศมี ($r = r_f$): $A_r = 2\pi r_f \Delta z$
- หน้าแนวแกน ($z = z_f$): $A_z = \pi(r_{\text{outer}}^2 - r_{\text{inner}}^2)$

### 10.4 การแบ่งส่วนเทอมการแพร่กระจายในแนวรัศมี

$$
\int_V \nabla \cdot (\mu \nabla \phi) \, dV = \oint_S \mu \nabla \phi \cdot d\mathbf{S}
$$

รูปแบบที่แบ่งส่วนแล้ว:
$$
\mu_e A_e \left(\frac{\phi_E - \phi_P}{\Delta r_e}\right) - \mu_w A_w \left(\frac{\phi_P - \phi_W}{\Delta r_w}\right) + \mu_n A_n \left(\frac{\phi_N - \phi_P}{\Delta z_n}\right) - \mu_s A_s \left(\frac{\phi_P - \phi_S}{\Delta z_s}\right)
$$

> **⚠️ สังเกต:** พื้นที่หน้ารัศมี $A_r = 2\pi r \Delta z$ แปรผันตรงกับ $r$ นี่คือความแตกต่างหลักจาก Cartesian!

### 10.5 C++ Implementation สำหรับ Cylindrical FVM

```cpp
// Cylindrical mesh for R410A evaporator tube
class CylindricalFVMesh {
    double R_tube;      // Tube radius [m] (typically ~0.005 m)
    double L_tube;      // Tube length [m] (typically 1-10 m)
    int nr, nz;         // Grid points in r, z
    double dr, dz;      // Cell sizes

public:
    CylindricalFVMesh(double R, double L, int n_r, int n_z)
        : R_tube(R), L_tube(L), nr(n_r), nz(n_z) {
        dr = R / nr;
        dz = L / nz;
    }

    // Cell volume at (i, j)
    double cellVolume(int i, int j) {
        double r_center = (i + 0.5) * dr;
        return 2.0 * M_PI * r_center * dr * dz;
    }

    // Radial face area
    double radialFaceArea(int i) {
        double r_face = i * dr;
        return 2.0 * M_PI * r_face * dz;
    }

    // Axial face area (annulus)
    double axialFaceArea(int i) {
        double r_inner = i * dr;
        double r_outer = (i + 1) * dr;
        return M_PI * (r_outer*r_outer - r_inner*r_inner);
    }
};

// Diffusion term in cylindrical coordinates
double radialDiffusion(int i, int j, const Field& phi, double mu, const CylindricalFVMesh& mesh) {
    // r * dphi/dr at faces
    double r_e = (i + 1) * mesh.dr;
    double dphi_dr_e = (phi(i+1, j) - phi(i, j)) / mesh.dr;

    double r_w = i * mesh.dr;
    double dphi_dr_w = (phi(i, j) - phi(i-1, j)) / mesh.dr;

    // Integral of div(r * grad(phi))
    return mu * (r_e * dphi_dr_e - r_w * dphi_dr_w) * mesh.dz;
}
```

### 10.6 R410A Evaporator Specific Considerations

| ประเด็น | คำอธิบาย | ผลกระทบ |
|---------|-----------|---------|
| **รัศมีท่อเล็ก** | $R \approx 5$ mm | ต้อง mesh ละเอียดในแนวรัศมี |
| **สัดส่วน aspect สูง** | $L/R \approx 1000$ | ใช้ non-uniform mesh |
| **Heat flux จากผนัง** | Constant q หรือ T | BC ที่ผนังสำคัญมาก |
| **Two-phase interface** | Void fraction $\alpha(r, z)$ | ติดตาม interface ใน $(r, z)$ |

> **🔗 See Also:** Day 04 for complete R410A evaporator simulation example with cylindrical mesh

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [02_Fundamental_Concepts.md](02_Fundamental_Concepts.md) — แนวคิดพื้นฐาน
- **บทถัดไป:** [04_Temporal_Discretization.md](04_Temporal_Discretization.md) — Temporal Discretization
- **ดู Matrix Assembly:** [05_Linear_Solvers_Matrix_Assembly.md](05_Linear_Solvers_Matrix_Assembly.md) — ระบบสมการเชิงเส้น
- **ประยุกต์:** [06_OpenFOAM_Implementation.md](06_OpenFOAM_Implementation.md) — การ implement ใน OpenFOAM
- **แก้ปัญหา:** [07_Troubleshooting.md](07_Troubleshooting.md) — Debugging และ solving issues