# รากฐานทฤษฎี Finite Volume Method

## 🎯 Learning Objectives

หลังจากอ่านบทนี้ คุณจะสามารถ:
- อธิบาย **หลักการอนุรักษ์** ที่เป็นหัวใจของ FVM
- เข้าใจการแปลง **PDE → Algebraic Equations**
- จำแนก **ข้อดีของ FVM** ที่เหมาะกับ CFD
- ทำความเข้าใจ **Control Volume Approach** และ Flux Balance
- เรียนรู้ **Discretization พื้นฐาน** ของแต่ละ term
- เข้าใจ **Matrix Concept** เบื้องต้น

## 📋 Prerequisites

- ✅ เข้าใจ **Calculus** พื้นฐาน (derivative, integral)
- ✅ คุ้นเคยกับ **PDE** (Partial Differential Equations)
- ✅ รู้จัก **Gauss Divergence Theorem**

---

## ทำไมต้อง Finite Volume Method?

> **คำถามกลาง: เลือก Discretization Method อย่างไรให้เหมาะกับ CFD?**

### เปรียบเทียบวิธีหลัก 3 แบบ

| วิธี | หลักการ | ข้อดี | ข้อเสีย | เหมาะกับ |
|------|----------|--------|---------|-----------|
| **FDM** | ใช้จุดตาข่าย (Grid Points) | เขียนง่าย | ไม่รองรับ complex geometry | Simple domains |
| **FVM** | ใช้ Control Volumes | **Conservation** โดยธรรมชาติ | Implementation ซับซ้อน | **CFD** ✅ |
| **FEM** | ใช้ Basis Functions | แม่นยำสูง | ช้า, ซับซ้อน | Structural analysis |

### ข้อดีของ FVM สำหรับ CFD

| ข้อดี | เหตุผลทางฟิสิกส์ | ผลใน OpenFOAM |
|--------|---------------------|----------------|
| **Conservation** | Flux ที่ออกจาก Cell A = Flux ที่เข้า Cell B | มวล/โมเมนตัม/พลังงานไม่หาย |
| **Flexibility** | รองรับ **Unstructured, Polyhedral Mesh** | จัดการ complex geometry ได้ |
| **Physical Intuition** | มาจากการ **balance flux** จริงๆ | Debug และวิเคราะห์ได้ง่าย |
| **Robustness** | จัดการ **discontinuous solutions** ได้ดี | เหมาะกับ shock, turbulence |

---

## หลักการพื้นฐาน: จาก PDE สู่ Algebraic Equations

### สมการอนุรักษ์ทั่วไป

$$\frac{\partial \phi}{\partial t} + \nabla \cdot \mathbf{F}(\phi) = S(\phi)$$

โดยที่:
- $\phi$ = ตัวแปรใดๆ (เช่น อุณหภูมิ $T$, ความเร็ว $\mathbf{u}$, ความดัน $p$)
- $\mathbf{F}(\phi)$ = Flux vector
- $S(\phi)$ = Source term

### 4 ขั้นตอน FVM

```mermaid
graph LR
    A[สมการ PDE] --> B[1. แบ่งโดเมน<br/>เป็น Control Volumes]
    B --> C[2. Integrate<br/>เหนือแต่ละ Cell]
    C --> D[3. Gauss Theorem<br/>Volume → Surface]
    D --> E[4. สร้างสมการ<br/>พีชคณิต]
    
    style A fill:#ffe1e1
    style B fill:#fff4e1
    style C fill:#e1f5ff
    style D fill:#e1ffe1
    style E fill:#e1ffff
```

#### ขั้นตอนที่ 1: แบ่งโดเมนเป็น Control Volumes

```
┌─────────────────────────────────────────────────────────────┐
│                    Computational Domain                      │
│  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐      │
│  │Cell1│  │Cell2│  │Cell3│  │Cell4│  │Cell5│  │Cell6│ ... │
│  └─────┘  └─────┘  └─────┘  └─────┘  └─────┘  └─────┘      │
└─────────────────────────────────────────────────────────────┘
```

- แต่ละ Cell = **Control Volume** หนึ่งหน่วย
- ขนาด/รูปร่างไม่เท่ากันได้ → **Unstructured Mesh**

#### ขั้นตอนที่ 2: Integrate สมการเหนือแต่ละ Cell

$$\int_{V_P} \frac{\partial \phi}{\partial t} dV + \int_{V_P} \nabla \cdot \mathbf{F}\, dV = \int_{V_P} S\, dV$$

#### ขั้นตอนที่ 3: ใช้ Gauss Divergence Theorem

$$\oint_{S_P} \mathbf{F} \cdot \mathbf{n}\, dS = \sum_{f} \mathbf{F}_f \cdot \mathbf{S}_f$$

สมการกลายเป็น:

$$\int_{V_P} \frac{\partial \phi}{\partial t} dV + \sum_{f} \mathbf{F}_f \cdot \mathbf{S}_f = \int_{V_P} S\, dV$$

#### ขั้นตอนที่ 4: สร้างสมการพีชคณิต

หลังจาก discretization จะได้:

$$a_P \phi_P + \sum_{N} a_N \phi_N = b_P$$

---

## Control Volume Approach

### Cell-Centered Storage

ใน OpenFOAM ค่าตัวแปรเก็บที่ **Cell Center**:

```
     Cell P                 Cell N
  ┌─────────┐           ┌─────────┐
  │         │           │         │
  │    •    │───────────│    •    │
  │   φ_P   │   Face f  │   φ_N   │
  │         │           │         │
  └─────────┘           └─────────┘
      │                     │
      Owner                Neighbor
```

**คำศัพท์สำคัญ:**

| สัญลักษณ์ | ความหมาย |
|----------|----------|
| **P** | Owner Cell |
| **N** | Neighbor Cell |
| **f** | Face ระหว่าง P กับ N |
| **S_f** | Face Area Vector (ชี้จาก P → N) |
| **φ_P** | ค่าที่ Cell Center P (known) |
| **φ_f** | ค่าที่ Face f (interpolate) |
| **φ_N** | ค่าที่ Cell Center N (known) |

### Flux Balance

**สำหรับแต่ละ Cell:**

$$\sum_f \mathbf{F}_f \cdot \mathbf{S}_f = 0$$

> **สิ่งที่ไหลเข้า = สิ่งที่ไหลออก (+ Sources)**

### ทำไม FVM อนุรักษ์โดยอัตโนมัติ?

1. Flux ที่ Face คำนวณ **ครั้งเดียว**
2. ใช้ร่วมกันระหว่าง **2 Cells ที่ติดกัน**
3. สิ่งที่ออกจาก Cell P → เข้า Cell N พอดี
4. ไม่มีการสูญหายหรือสร้างใหม่

---

## Discretization พื้นฐาน

### 1. Temporal Term (เวลา)

$$\frac{\partial \phi}{\partial t} \rightarrow \frac{\phi^{n+1} - \phi^n}{\Delta t} V_P$$

**Temporal Schemes:**

| Scheme | Order | ความเสถียร | ความแม่นยำ | ใช้เมื่อ |
|--------|-------|-------------|-------------|-----------|
| **Euler** | 1 | สูงมาก | ต่ำ | Large Δt |
| **Backward** | 2 | สูง | กลาง | General purpose |
| **Crank-Nicolson** | 2 | กลาง | สูง | Small Δt, ต้องการ accuracy |

> **📖 เรียนต่อ:** [04_Temporal_Discretization.md](04_Temporal_Discretization.md) — รายละเอียด Time Schemes

### 2. Convective Term (การพา)

$$\nabla \cdot (\phi \mathbf{u}) \rightarrow \sum_f \phi_f \Phi_f$$

โดย $\Phi_f = \mathbf{u}_f \cdot \mathbf{S}_f$ คือ **volumetric flux**

**Interpolation Schemes:**

| Scheme | สูตร | Order | เสถียรภาพ | ความแม่นยำ | ใช้เมื่อ |
|--------|------|-------|-------------|-------------|-----------|
| **Upwind** | $\phi_f = \phi_P$ (ถ้า $\Phi_f > 0$) | 1 | สูง | ต่ำ (diffusive) | First guess |
| **Linear** | $\phi_f = \frac{1}{2}(\phi_P + \phi_N)$ | 2 | ต่ำ | สูง | Fine mesh |
| **LimitedLinear** | Linear + TVD limiter | 2 | กลาง | สูง | General use |

> **📖 เรียนต่อ:** [03_Spatial_Discretization.md](03_Spatial_Discretization.md) — รายละเอียด Convection Schemes

### 3. Diffusive Term (การกระจาย)

$$\nabla \cdot (D \nabla \phi) \rightarrow \sum_f D_f \frac{\phi_N - \phi_P}{d_{PN}} |\mathbf{S}_f|$$

**หมายเหตุ:**
- สูตรนี้ใช้ได้เฉพาะ **Orthogonal Mesh**
- Non-orthogonal mesh ต้องมี **Correction Term**

> **📖 เรียนต่อ:** [03_Spatial_Discretization.md](03_Spatial_Discretization.md) — รายละเอียด Diffusion Schemes

### 4. Source Term

$$S \rightarrow S_P V_P$$

---

## Matrix Assembly Concept

### จาก Cell หนึ่งไปสู่ระบบสมการ

หลังจาก discretize ทุก term สำหรับ Cell P:

$$a_P \phi_P + \sum_{N} a_N \phi_N = b_P$$

รวมทุก Cell → **ระบบสมการเชิงเส้น:**

$$[A][\phi] = [b]$$

| ส่วนประกอบ | ความหมาย | ลักษณะ |
|-----------|----------|--------|
| **A** | Coefficient Matrix | **Sparse** (ส่วนใหญ่เป็น 0) |
| **φ** | Unknown Values | ค่าที่ทุก Cell Center |
| **b** | Source Vector | Source + Boundary contributions |

### Sparse Matrix Structure

```
[A] =  [ a_P   a_N2   a_N3   0     0    ... ]   [φ_P]   [b_P]
       [ a_N1  a_P    0     a_N4   0    ... ] × [φ_N] = [b_N]
       [ a_N1  0      a_P    a_N3   0    ... ]   [•  ]   [•  ]
       [ 0     a_N2   a_N3   a_P    a_N5 ...]   [•  ]   [•  ]
       [ ...                                    ]   [•  ]   [•  ]
```

- แต่ละแถว = **1 Cell**
- ค่า nonzero = **Neighboring Cells** เท่านั้น
- ประหยัด memory → iterative solvers

> **📖 เรียนต่อ:** [05_Matrix_Assembly_Solvers.md](05_Matrix_Assembly_Solvers.md) — รายละเอียด Matrix & Solvers

---

## Files ที่เกี่ยวข้องใน OpenFOAM

| Directory/File | เนื้อหา | บทบาทใน FVM |
|----------------|----------|---------------|
| `constant/polyMesh/` | Mesh topology | กำหนด Control Volumes |
| `0/` | Initial & Boundary Conditions | ค่าเริ่มต้น + Flux ที่ขอบ |
| `system/fvSchemes` | Discretization Schemes | เลือก interpolation method |
| `system/fvSolution` | Linear Solvers Settings | กำหนด iterative algorithm |

---

## Concept Check

<details>
<summary><b>1. ทำไม FVM ถึง "อนุรักษ์" โดยธรรมชาติ?</b></summary>

เพราะ Flux ที่ Face คำนวณ **ครั้งเดียว** และใช้ร่วมกันระหว่าง 2 Cells ดังนั้นสิ่งที่ออกจาก Cell หนึ่งจะเข้าอีก Cell หนึ่งพอดี ไม่มีการสูญหายหรือสร้างใหม่

**เปรียบเทียบ:** เหมือนระบบน้ำในท่อที่เชื่อมต่อกัน — น้ำที่ออกจากท่อ A ต้องเข้าท่อ B เสมอ
</details>

<details>
<summary><b>2. Gauss Divergence Theorem ทำอะไรให้ FVM?</b></summary>

แปลง **Volume Integral** → **Surface Integral** ทำให้เรา:
- ไม่ต้องคำนวณในปริมาตรทั้งหมด
- คำนวณเฉพาะที่ Face (ผิวสัมผัส) เท่านั้น
- ทำให้ flux ระหว่าง cells ถูกคำนวณครั้งเดียว → conservation
</details>

<details>
<summary><b>3. Upwind vs Linear ต่างกันอย่างไร?</b></summary>

| Scheme | หลักการ | ข้อดี | ข้อเสีย |
|--------|----------|--------|---------|
| **Upwind** | ใช้ค่าจาก upstream เท่านั้น | เสถียรมาก | Diffusive (ลดความแม่นยำ) |
| **Linear** | เฉลี่ยค่าทั้งสอง Cell | แม่นยำกว่า | อาจ oscillate ได้ |

**กฎง่ายๆ:** ลอง Upwind ก่อน → ถ้า stable แล้วค่อยเปลี่ยนเป็น Linear
</details>

<details>
<summary><b>4. ทำไม Matrix ที่ได้ถึง "Sparse"?</b></summary>

เพราะ discretization ของแต่ละ Cell **ขึ้นกับ Neighbors โดยรอมเท่านั้น** (ไม่ใช่ทุก Cell ในโดเมน)

ตัวอย่าง: ถ้า Cell P มี neighbor 6 คือ → แถวใน matrix มี nonzero เพียง 7 ค่า (P + 6 neighbors)
</details>

---

## เอกสารที่เกี่ยวข้อง

### ภายใน Module นี้
- **ถัดไป:** [02_Governing_Equations_FVM.md](02_Governing_Equations_FVM.md) — สมการควบคุมในรูป FVM (Continuity, Momentum, Energy, SIMPLE/PISO)
- **ต่อไป:** [03_Spatial_Discretization.md](03_Spatial_Discretization.md) — Gradient, Convection, Diffusion Schemes
- **ต่อไป:** [04_Temporal_Discretization.md](04_Temporal_Discretization.md) — Time Schemes & CFL
- **ต่อไป:** [05_Matrix_Assembly_Solvers.md](05_Matrix_Assembly_Solvers.md) — Linear Algebra & Solvers

### ภายนอก Module
- **บทก่อนหน้า:** [00_Overview.md](00_Overview.md) — ภาพรวมและเส้นทางการเรียนรู้
- **บทก่อนหน้า:** [../01_GOVERNING_EQUATIONS/00_Overview.md](../01_GOVERNING_EQUATIONS/00_Overview.md) — สมการ PDE พื้นฐาน

---

## Summary: Key Takeaways

| แนวคิด | สิ่งที่ต้องจำ |
|---------|--------------|
| **FVM = Control Volume + Conservation** | แบ่งโดเมน → Balance flux ที่แต่ละกล่อง |
| **Gauss Theorem = Volume → Surface** | ทำให้คำนวณที่ Face และ conservation โดยอัตโนมัติ |
| **Cell-Centered = Interpolate to Faces** | เก็บค่าที่ Cell Center → ประมาณค่าที่ Face |
| **PDE → Algebraic → Matrix** | Discretize ทุก term → รวมเป็น [A][φ]=[b] |
| **Sparse Matrix = Iterative Solvers** | Nonlinearity + ขนาดใหญ่ → วนซ้ำ |