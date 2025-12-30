# สูตรทางคณิตศาสตร์ของ Boundary Conditions

Mathematical Formulation and FVM Discretization of Boundary Conditions

## Learning Objectives

หลังจากอ่านบทนี้ คุณควรจะสามารถ:

- **ระบุและเปรียบเทียบ** สมการคณิตศาสตร์ของ BC ทั้ง 3 ประเภท (Dirichlet, Neumann, Robin)
- **อธิบาย** แต่ละประเภทของ BC ส่งผลต่อโครงสร้างของเมทริกซ์ในระบบ linear equation อย่างไร
- **นำไปใช้** สูตร discretization สำหรับการ implement BC ใน Finite Volume Method
- **วิเคราะห์** ความสัมพันธ์ระหว่าง U และ p BC ใน incompressible flow และปัญหาที่เกิดจาก over-constrained BC
- **ประเมิน** well-posedness ของปัญหา BC ตามหลัก Hadamard

**Prerequisites:** พื้นฐาน Calculus (partial derivatives), Linear Algebra (matrix systems), พื้นฐาน PDE classifications

---

## What: ประเภทของ BC และสมการคณิตศาสตร์

### 1. Dirichlet Boundary Condition (First Kind)

**Mathematical Definition:**
$$\phi|_{\partial\Omega} = \phi_0(\mathbf{x}, t)$$

กำหนดค่าของตัวแปร $\phi$ โดยตรงที่ขอบเขต $\partial\Omega$

**Physical Examples:**

| ตัวอย่าง | สมการ | สถานการณ์จริง |
|---------|-------|----------------|
| Inlet velocity | $\mathbf{u} = \mathbf{u}_{\text{inlet}}$ | กำหนดความเร็วลมเข้าช่องทาง |
| Wall temperature | $T = T_{\text{wall}}$ | ผนังคงที่อุณหภูมิ |
| Outlet pressure | $p = p_{\text{atm}}$ | ทางออกเปิดสู่บรรยากาศ |

### 2. Neumann Boundary Condition (Second Kind)

**Mathematical Definition:**
$$\frac{\partial\phi}{\partial n}\bigg|_{\partial\Omega} = g(\mathbf{x}, t)$$

กำหนด normal derivative (gradient/flux) ของ $\phi$ ที่ขอบเขต โดยที่ $n$ คือ unit normal vector

**Physical Examples:**

| ตัวอย่าง | สมการ | ความหมายทางฟิสิกส์ |
|---------|-------|---------------------|
| Adiabatic wall | $\frac{\partial T}{\partial n} = 0$ | ไม่มีการถ่ายเทความร้อน |
| Heat flux | $-k\frac{\partial T}{\partial n} = q''$ | กำหนดอัตราการไหลของความร้อน |
| Fully developed | $\frac{\partial \mathbf{u}}{\partial n} = 0$ | โปรไฟล์ความเร็วไม่เปลี่ยนตามระยะทาง |

### 3. Robin Boundary Condition (Third Kind / Mixed)

**Mathematical Definition:**
$$a\phi + b\frac{\partial\phi}{\partial n} = c$$

ผสมกันระหว่างค่าของตัวแปรและ gradient ที่ขอบเขต

**Physical Examples:**

| ตัวอย่าง | สมการ | ปรากฏการณ์ |
|---------|-------|------------|
| Convection | $-k\frac{\partial T}{\partial n} = h(T - T_\infty)$ | การถ่ายเทความร้อนแบบทับซ้อน (convective cooling) |
| Radiation | $-k\frac{\partial T}{\partial n} = \varepsilon\sigma(T^4 - T^4_\infty)$ | การแผ่รังสีความร้อน |

---

## Why: ทำไมคณิตศาสตร์ของ BC สำคัญต่อการแก้ปัญหา CFD?

### 1. ผลต่อ Matrix Structure

การ discretize BC แต่ละประเภทส่งผลต่อระบบสมการเชิงเส้น $A\mathbf{x} = \mathbf{b}$ ที่แตกต่างกัน:

- **Dirichlet:** แก้ไข diagonal และ source term → แก้ปัญหา singularity ของเมทริกซ์
- **Neumann:** เพิ่ม flux เข้า source term → รักษา sparsity structure
- **Robin:** แก้ไขทั้ง diagonal และ off-diagonal → ต้อง careful ในการ implement

### 2. Well-Posedness ของปัญหา (Hadamard's Conditions)

ปัญหาทางคณิตศาสตร์จะมีคำตอบที่ถูกต้องได้ต้องเป็น **well-posed** ตามเงื่อนไข 3 ข้อ:

1. **Existence** — ต้องมีคำตอบ
2. **Uniqueness** — คำตอบต้องเป็นเอกลักษณ์
3. **Stability** — คำตอบต้องเปลี่ยนต่อเนื่องเมื่อ BC เปลี่ยนเล็กน้อย

### 3. Conservation Properties

BC ที่ถูกต้องจะรักษา conservation laws ของ FVM:
- Mass conservation: $\sum F_f = 0$
- Momentum conservation: ไม่มี source/sink ที่ boundary (เว้นแต่กำหนดไว้)
- Energy conservation: flux balance ที่ boundary

---

## How: การ Discretize BC ใน Finite Volume Method

### Dirichlet BC Implementation

สำหรับ cell $P$ ที่ติดกับ boundary face $f$:

**General FVM Equation:**
$$a_P\phi_P = \sum_N a_N\phi_N + b_P$$

**Matrix Modification:**
```
Diagonal coefficient:    a_P → a_P + a_f
Source term:             b_P → b_P + a_f × φ_boundary
Off-diagonal (neighbor): ลบ a_f ออกจาก summation
```

**ผลลัพธ์:** Boundary value $\phi_{\text{boundary}}$ ถูก "imposed" ผ่าน diagonal dominance

**OpenFOAM Implementation:**
```cpp
// Dirichlet contributes to diagonal and source
// internalCoeffs: contribution to diagonal matrix coefficient
// boundaryCoeffs: contribution to source term
internalCoeffs = patchInternalCoeffs;      // → a_f
boundaryCoeffs = patchField * patchInternalCoeffs;  // → a_f × φ_boundary
```

### Neumann BC Implementation

**Mathematical Form:**
$$\frac{\partial\phi}{\partial n}\bigg|_f = g_f$$

**Discretization:**
```
Flux calculation:  F_f = -Γ × g_f × A_f
Source modification: b_P → b_P + F_f
```

สำหรับกรณีพิเศษ `zeroGradient` ($g_f = 0$):
```
φ_f = φ_P  (extrapolate จาก cell center ถึง face)
Flux: F_f = 0
```

**ผลลัพธ์:** Gradient BC ไม่แก้ไข matrix coefficients → เพิ่ม flux เข้า source term เท่านั้น

### Robin (Mixed) BC Implementation

**General Form:**
$$a\phi_f + b\frac{\partial\phi}{\partial n}\bigg|_f = c$$

**Discretization Strategy:**
```
ใช้ linear interpolation:
φ_f = α × φ_boundary + (1-α) × extrapolated_value

α = valueFraction  (ช่วง 0 ถึง 1)
```

**Mathematical Formulation:**
$$\phi_f = \text{valueFraction} \times \phi_{\text{specified}} + (1 - \text{valueFraction}) \times \phi_{\text{extrapolated}}$$

**ValueFraction Interpretation:**

| valueFraction | ประเภท BC | ผลลัพธ์ |
|--------------|----------|---------|
| $1$ | Dirichlet | $\phi_f = \phi_{\text{specified}}$ |
| $0$ | Neumann | $\phi_f = \phi_{\text{extrapolated}}$ |
| $(0,1)$ | Mixed | ผสมกันระหว่าง value และ gradient |

**OpenFOAM Implementation:**
```cpp
// Mixed BC ใช้ valueFraction
valueFraction = h / (h + k/δ);  // ตัวอย่างสำหรับ convection
// h = heat transfer coefficient
// k = thermal conductivity
// δ = cell size at boundary
```

---

## Special Considerations in OpenFOAM

### Velocity-Pressure Coupling in Incompressible Flow

**Governing Equations:**

**Continuity:**
$$\nabla \cdot \mathbf{u} = 0$$

**Momentum:**
$$\frac{\partial\mathbf{u}}{\partial t} + (\mathbf{u}\cdot\nabla)\mathbf{u} = -\frac{1}{\rho}\nabla p + \nu\nabla^2\mathbf{u}$$

**Critical Coupling Rule:**

| ถ้า U เป็น... | แล้ว p ต้องเป็น... | เหตุผล |
|---------------|---------------------|--------|
| `fixedValue` (Dirichlet) | `zeroGradient` (Neumann) | หลีกเลี่ยง over-constrained |
| `zeroGradient` (Neumann) | `fixedValue` (Dirichlet) | กำหนด reference pressure |

**⚠️ Common Mistake:** การกำหนด Dirichlet ทั้ง velocity และ pressure ที่ boundary เดียวกัน → **over-constrained** → solver ไม่สามารถหา solution ที่สอดคล้องกับ continuity equation → มักจะ diverge

### Reference Pressure for Incompressible Flow

**ทำไมต้องมี Reference Pressure?**

สมการ momentum สำหรับ incompressible flow มีเฉพาะ pressure gradient $\nabla p$ ไม่ใช้ค่าสัมบูรณ์:
- ค่า pressure สามารถเพิ่มลด constant ได้โดยไม่กระทบ velocity field
- ถ้าไม่กำหนด reference จะเกิดปัญหา **floating pressure** → solver ไม่ converge หรือได้คำตอบไม่จำกัด

**วิธีการกำหนดใน OpenFOAM:**

**Method 1: Using pRefCell (preferred)**
```cpp
// system/fvSolution
SIMPLE
{
    pRefCell    0;        // Cell index สำหรับ reference
    pRefValue   0;        // Reference pressure value (Pa)
}
```

**Method 2: Fixed value at boundary**
```
// 0/p
outlet
{
    type            fixedValue;
    value           uniform 0;  // Gauge pressure = 0
}
```

### Flux Conservation in FVM

ใน Finite Volume Method, flux ที่ face ถูกคำนวณครั้งเดียวและใช้ร่วมกัน:

**Flux Definition:**
$$F_f = \phi_f \cdot (\mathbf{u}_f \cdot \mathbf{S}_f)$$

โดยที่:
- $\phi_f$ = property ที่ face (e.g., mass fraction)
- $\mathbf{u}_f$ = velocity ที่ face
- $\mathbf{S}_f$ = face area vector

**ผลลัพธ์สำคัญ:**
- สิ่งที่ออกจาก cell A = สิ่งที่เข้า cell B (ที่ face เดียวกัน)
- Conservation โดยธรรมชาติ → ไม่ต้อง enforce แยก
- BC ต้องรักษา consistency ของ flux เข้า-ออก

---

## Well-Posedness by PDE Type

| PDE Type | ตัวอย่างสมการ | Boundary Condition Requirement |
|----------|------------------|-------------------------------|
| **Elliptic** | Laplace: $\nabla^2\phi = 0$ <br> Poisson: $\nabla^2\phi = f$ | BC ต้องกำหนดที่ **ทุกขอบ** ของ computational domain |
| **Parabolic** | Heat: $\frac{\partial T}{\partial t} = \alpha\nabla^2 T$ | ต้องมี **Initial Condition (IC)** + BC ทุกขอบ |
| **Hyperbolic** | Wave: $\frac{\partial^2 u}{\partial t^2} = c^2\nabla^2 u$ | BC แบบ **Characteristic-based** (inflow/outflow) |

**Practical Implication:** ถ้าไม่กำหนด BC ครบถ้วนตามประเภท PDE → solver อาจแก้ปัญหาไม่ได้ หรือได้คำตอบไม่ถูกต้อง

---

## Key Takeaways: Essential Formulas Cheat Sheet

### BC Mathematical Formulations

| BC Type | Mathematical Form | Matrix Impact | Physical Meaning |
|---------|------------------|---------------|------------------|
| **Dirichlet** | $\phi\|_{\partial\Omega} = \phi_0$ | Modify diagonal + source | Fixed value at boundary |
| **Neumann** | $\frac{\partial\phi}{\partial n}\|_{\partial\Omega} = g$ | Add to source term only | Fixed flux at boundary |
| **Robin** | $a\phi + b\frac{\partial\phi}{\partial n} = c$ | Modify diagonal + off-diagonal | Convective/radiative balance |

### FVM Discretization Rules

**Dirichlet BC:**
```
a_P → a_P + a_f
b_P → b_P + a_f × φ_boundary
```

**Neumann BC:**
```
b_P → b_P - Γ × g × A_f
(no matrix modification)
```

**Robin BC:**
```
φ_f = valueFraction × φ_specified + (1-valueFraction) × φ_extrapolated
```

### Velocity-Pressure Coupling

| U BC | Required p BC | Reason |
|------|--------------|--------|
| `fixedValue` | `zeroGradient` | Avoid over-constrained |
| `zeroGradient` | `fixedValue` | Set pressure reference |

### Well-Posedness Checklist

- [ ] **Elliptic:** BC on ALL boundaries
- [ ] **Parabolic:** IC + BC on all boundaries  
- [ ] **Hyperbolic:** Characteristic-based BC
- [ ] **Incompressible flow:** Pressure reference specified
- [ ] **Coupling:** U and p BC follow coupling rule

---

## Concept Check

<details>
<summary><b>1. ทำไม incompressible flow ต้องมี reference pressure?</b></summary>

เพราะสมการ momentum มีเฉพาะ pressure gradient $\nabla p$ → ค่า pressure สัมบูรณ์ไม่ถูกกำหนดโดยสมการ → ถ้าไม่มี reference จะได้คำตอบไม่จำกัด (floating pressure) → solver ไม่ converge หรือได้คำตอบที่ไม่แน่นอน

**Cross-reference:** ดูการ implement reference pressure ใน [05_Common_Boundary_Conditions_in_OpenFOAM.md](05_Common_Boundary_Conditions_in_OpenFOAM.md)
</details>

<details>
<summary><b>2. Over-constrained boundary condition เกิดเมื่อไหร่ และมีผลอย่างไร?</b></summary>

เกิดเมื่อกำหนด Dirichlet BC ทั้ง velocity ($\mathbf{u}$) และ pressure ($p$) ที่ boundary เดียวกัน → ขัดแย้งกับ continuity equation $\nabla \cdot \mathbf{u} = 0$ → solver ไม่สามารถหา solution ที่สอดคล้องกันได้ → มักจะทำให้ simulation diverge หรือให้ผลลัพธ์ที่ไม่ถูกต้อง

**Solution:** ใช้ coupling rule: ถ้า U เป็น `fixedValue` แล้ว p ต้องเป็น `zeroGradient` และกลับกัน
</details>

<details>
<summary><b>3. Neumann BC ถูก discretize และใส่ใน matrix อย่างไร?</b></summary>

Neumann BC ไม่แก้ไข diagonal หรือ off-diagonal coefficients ของเมทริกซ์ แต่เพิ่ม flux เข้า source term โดยตรง:

$$b_P \leftarrow b_P - \Gamma \cdot g \cdot A_f$$

โดยที่:
- $\Gamma$ = diffusion coefficient
- $g$ = specified gradient at boundary
- $A_f$ = face area

สำหรับกรณีพิเศษ `zeroGradient` ($g=0$): flux = 0 → ไม่ต้องเพิ่ม source term
</details>

<details>
<summary><b>4. อธิบายความแตกต่างระหว่าง Elliptic, Parabolic และ Hyperbolic PDE ในบริบทของ BC?</b></summary>

- **Elliptic (e.g., steady-state diffusion):** ต้องการ BC ที่ทุกขอบเขต → ข้อมูล propagate ทันทีทุกทิศทาง → ไม่มี "time-like" direction
- **Parabolic (e.g., transient diffusion):** ต้องการ Initial Condition + BC ทุกขอบ → มีทิศทาง "time" ที่ information flow ได้ทางเดียว
- **Hyperbolic (e.g., wave propagation):** ต้องการ BC ที่ inflow boundaries เท่านั้น → information propagate ตาม characteristics → BC ที่ outflow จะถูกกำหนดโดย solution เอง

**Practical tip:** ใน CFD ส่วนใหญ่เป็น mixed PDE type ต้อง carefully consider BC สำหรับแต่ละ variable
</details>

---

## Navigation

- **บทก่อนหน้า:** [03_Selection_Guide_Which_BC_to_Use.md](03_Selection_Guide_Which_BC_to_Use.md) — คู่มือการเลือก BC ที่เหมาะสม
- **บทถัดไป:** [05_Common_Boundary_Conditions_in_OpenFOAM.md](05_Common_Boundary_Conditions_in_OpenFOAM.md) — BC ที่ใช้บ่อยใน OpenFOAM
- **กลับไป Overview:** [00_Overview.md](00_Overview.md) — ภาพรวม Boundary Conditions