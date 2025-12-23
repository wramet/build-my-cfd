# รากฐานทางคณิตศาสต์ของการเชื่อมโยงความดัน-ความเร็ว

## 📖 บทนำ (Introduction)

การจำลอง **Incompressible Flow** ใน OpenFOAM อาศัยการแก้สมการอนุรักษ์มวลและโมเมนตัม ปัญหาพื้นฐานอยู่ที่ความดัน ($p$) ไม่มีสมการควบคุมที่ชัดเจนในระบบของไหลอัดตัวไม่ได้

ความดันทำหน้าที่เป็น **Lagrange Multiplier** เพื่อรักษาเงื่อนไข $\nabla \cdot \mathbf{u} = 0$ ซึ่งสร้างความท้าทายทางคณิตศาสตร์ที่เรียกว่า **Saddle-Point Problem** เอกสารนี้จะอธิบายวิธีการอนุพัทธ์สมการความดันจากเงื่อนไขทางกายภาพ

---

## 📐 1. สมการควบคุมในรูปแบบต่อเนื่อง (Continuous Governing Equations)

### 1.1 สมการพื้นฐานสำหรับ Incompressible Newtonian Fluid

สำหรับของไหล Newtonian ที่ความหนาแน่นคงที่ เรามีสมการควบคุมสองสมการหลัก:

**สมการความต่อเนื่อง (Continuity Equation) - การอนุรักษ์มวล:**
$$\nabla \cdot \mathbf{u} = 0 \tag{1.1}$$

**สมการโมเมนตัม (Momentum Equation) - การอนุรักษ์โมเมนตัม:**
$$\rho \frac{\partial \mathbf{u}}{\partial t} + \rho (\mathbf{u} \cdot \nabla) \mathbf{u} = -\nabla p + \mu \nabla^2 \mathbf{u} + \mathbf{f} \tag{1.2}$$

**นิยามตัวแปร:**
- $\mathbf{u}$ = เวกเตอร์สนามความเร็ว (velocity vector field) [m/s]
- $p$ = สนามความดัน (pressure field) [Pa]
- $\rho$ = ความหนาแน่นของไหลคงที่ (constant fluid density) [kg/m³]
- $\mu$ = ความหนืดพลวัต (dynamic viscosity) [Pa·s]
- $\mathbf{f}$ = แรงภายนอกต่อหน่วยปริมาตร (body forces) [N/m³]

### 1.2 ปัญหาการเชื่อมโยง (The Coupling Problem)

> [!INFO] ปัญหาพื้นฐานของ Incompressible Flow
> ความท้าทายหลักเกิดขึ้นเนื่องจาก:
> 1. **ความดันปรากฏเฉพาะในรูปของ Gradient** ในสมการโมเมนตัม
> 2. **ไม่มีสมการความดันโดยตรง** ที่มาจากกฎการอนุรักษ์ทางกายภาพ
> 3. **ความดันถูกกำหนดได้ถึงค่าคงที่บวก** (additive constant)
> 4. **สนามความเร็วต้องเป็นไปตาม** $\nabla \cdot \mathbf{u} = 0$ **ในขณะที่ตอบสนองต่อ Gradient ความดัน**

สิ่งนี้สร้าง **ปัญหาจุดอานม้า (saddle-point problem)** ซึ่งความดันทำหน้าที่เป็น Lagrange multiplier ที่บังคับใช้ข้อจำกัด divergence-free กับความเร็ว

---

## 🔢 2. การทำให้เป็นดิสครีตด้วย Finite Volume Method (Discretization)

### 2.1 รูปแบบ Semi-Discretized ของสมการโมเมนตัม

เมื่อใช้ **Finite Volume Method (FVM)** กับสมการโมเมนตัมที่จุดศูนย์กลางเซลล์ $P$:

```mermaid
flowchart LR
    A[Cell P] --> B[Neighbor N]
    A --> C[Face f]
    B --> C
    C --> D[Flux Calculation]
```
> **Figure 1:** ความสัมพันธ์ระหว่างเซลล์ควบคุม (Cell P) กับเซลล์ข้างเคียง (Neighbor N) ผ่านหน้าสัมผัส (Face f) ซึ่งเป็นตำแหน่งหลักในการคำนวณฟลักซ์ (Flux Calculation) โดยใช้วิธี Finite Volume เพื่อเปลี่ยนสมการอนุพันธ์เชิงพื้นที่ให้เป็นรูปแบบพีชคณิตที่สามารถแก้ปัญหาได้

$$a_P \mathbf{u}_P + \sum_{N} a_N \mathbf{u}_N = \mathbf{b}_P - (\nabla p)_P \tag{2.1}$$

**ความหมายของสัมประสิทธิ์:**

| สัมประสิทธิ์ | นิยาม | คำอธิบาย |
|:------------:|:------:|:----------|
| $a_P$ | $\frac{\rho_P V_P}{\Delta t} + \sum_{f} \Gamma_f S_f$ | สัมประสิทธิ์แนวทแยง (Diagonal coefficient) |
| $a_N$ | $-\Gamma_f S_f$ | สัมประสิทธิ์เพื่อนบ้าน (Neighbor coefficient) |
| $\mathbf{b}_P$ | $\frac{\rho_P V_P}{\Delta t} \mathbf{u}_P^n + \mathbf{f}_{b,P} V_P$ | เทอมแหล่งกำเนิด (Source term) |

**โดยที่:**
- $V_P$ = ปริมาตรของเซลล์ $P$ [m³]
- $S_f$ = พื้นที่ผิวหน้า $f$ [m²]
- $\Gamma_f$ = ค่าสัมประสิทธิ์การนำที่หน้า $f$

### 2.2 การจัดรูปใหม่เป็นรูปแบบ H-Operator

จัดรูปสมการ (2.1) ใหม่ในรูปแบบ **Semi-discretized form**:

$$\mathbf{u}_P = \frac{\mathbf{H}(\mathbf{u})}{a_P} - \frac{1}{a_P} \nabla p \tag{2.2}$$

โดยที่ **H-operator** นิยามเป็น:

$$\mathbf{H}(\mathbf{u}) = \mathbf{b}_P - \sum_{N} a_N \mathbf{u}_N \tag{2.3}$$

### 2.3 การแทนค่าใน OpenFOAM

ในซอร์สโค้ดของ OpenFOAM มีการแทนค่าดังนี้:

```cpp
// การแทนค่าใน OpenFOAM
volScalarField rAU(1.0/UEqn.A());      // rAU = 1/a_P
volVectorField HbyA(constrainHbyA(rAU*UEqn.H(), U, p));  // HbyA = H(u)/a_P
```

**ความสัมพันธ์:**
- `rAU` ใน OpenFOAM = $\frac{1}{a_P}$
- `HbyA` ใน OpenFOAM = $\frac{\mathbf{H}(\mathbf{u})}{a_P}$

---

## 🔄 3. การสร้างสมการความดัน (Pressure Equation Derivation)

### 3.1 หลักการพื้นฐาน

เพื่อให้แน่ใจว่าความเร็วที่ได้จากสมการโมเมนตัมสอดคล้องกับสมการความต่อเนื่อง เรานำ **Divergence ($\nabla \cdot$)** มาใช้กับสมการ (2.2):

$$\nabla \cdot \mathbf{u}_P = \nabla \cdot \left( \frac{\mathbf{H}(\mathbf{u})}{a_P} \right) - \nabla \cdot \left( \frac{1}{a_P} \nabla p \right) = 0$$

### 3.2 สมการ Pressure Poisson

จัดรูปจะได้ **Pressure Poisson Equation**:

$$\nabla \cdot \left( \frac{1}{a_P} \nabla p \right) = \nabla \cdot \left( \frac{\mathbf{H}(\mathbf{u})}{a_P} \right) \tag{3.1}$$

> [!TIP] ความสำคัญของ Pressure Poisson Equation
> - สมการนี้ช่วยให้เราคำนวณสนามความดัน $p$ ที่สอดคล้องกับสนามความเร็ว $\mathbf{u}$
> - ด้านขวาของสมการ (RHS) คือ Divergence ของ `HbyA` ซึ่งแสดงถึงความไม่สมดุลของมวลชั่วคราว
> - การแก้สมการนี้จะทำให้ความเร็วเป็นไปตามเงื่อนไข divergence-free

### 3.3 รูปแบบเมทริกซ์ใน OpenFOAM

สมการความดันสามารถเขียนในรูปแบบเมทริกซ์:

$$\mathbf{A}_p \mathbf{p}' = \mathbf{r}_p$$

**โดยที่:**
- $\mathbf{A}_p$ = เมทริกซ์สัมประสิทธิ์ความดัน
- $\mathbf{r}_p$ = เวกเตอร์ Residual

---

## 💻 4. การนำไปใช้ใน OpenFOAM (OpenFOAM Implementation)

### 4.1 ตัวอย่างการประกอบเมทริกซ์ใน `pEqn.H`

```cpp
// ========================================
// 1. สร้าง HbyA และ rAU
// ========================================
volScalarField rAU(1.0/UEqn.A());
volVectorField HbyA(constrainHbyA(rAU*UEqn.H(), U, p));

// ========================================
// 2. สร้าง Flux ที่หน้าเซลล์โดยไม่รวมผลของความดัน
// ========================================
surfaceScalarField phiHbyA
(
    "phiHbyA",
    fvc::flux(HbyA)
  + fvc::interpolate(rAU)*fvc::ddtCorr(U, phi)
);

// ========================================
// 3. แก้สมการ Poisson สำหรับความดัน
// ========================================
fvScalarMatrix pEqn
(
    fvm::laplacian(rAU, p) == fvc::div(phiHbyA)
);
pEqn.solve();

// ========================================
// 4. แก้ไขความเร็ว (Velocity Correction)
// ========================================
U = HbyA - rAU*fvc::grad(p);
U.correctBoundaryConditions();
```

### 4.2 การแปลงสมการเป็น Code

| สมการคณิตศาสตร์ | OpenFOAM Code |
|:------------------:|:-------------|
| $\nabla \cdot \mathbf{u}$ | `fvc::div(U)` |
| $\nabla p$ | `fvc::grad(p)` |
| $\nabla^2 p$ | `fvm::laplacian(p)` |
| $\frac{1}{a_P}$ | `1.0/UEqn.A()` |
| $\frac{\mathbf{H}(\mathbf{u})}{a_P}$ | `UEqn.H()/UEqn.A()` |

---

## 🧱 5. Rhie-Chow Interpolation

### 5.1 ปัญหา Checkerboard Decoupling

บน **Collocated Grid** ซึ่งความดันและความเร็วถูกเก็บไว้ที่จุดศูนย์กลางเซลล์เดียวกัน ความเร็วที่หน้าเซลล์ ($\mathbf{u}_f$) หากใช้การเฉลี่ยแบบ Linear ปกติ จะเกิดปัญหา **Checkerboard Decoupling**

```mermaid
flowchart LR
    A[Linear Interpolation] --> B[Decoupled Pressure Field]
    B --> C[Checkerboard Pattern]
    C --> D[Unphysical Oscillations]
```
> **Figure 2:** แผนภาพแสดงผลกระทบของการใช้การประมาณค่าแบบเชิงเส้น (Linear Interpolation) บนเมชแบบ Collocated ซึ่งนำไปสู่การแยกตัวของข้อมูลความดันและความเร็ว (Decoupling) ส่งผลให้เกิดรูปแบบความดันสลับฟันปลา (Checkerboard pattern) และการแกว่งทางตัวเลขที่ไม่มีความหมายทางกายภาพความปลอดภัยทางฟิสิกส์ไม่ส่งผลกระทบต่อความเร็วในการจำลอง ผ่านการใช้พลังของ C++ Template Metaprogramming ในการตรวจสอบความสอดคล้องทางมิติทั้งหมดที่ขั้นตอนการคอมไพล์โปรแกรมเพียงครั้งเดียว

### 5.2 สูตร Rhie-Chow Interpolation

OpenFOAM ใช้สูตร Rhie-Chow เพื่อป้องกันปัญหานี้:

$$\mathbf{u}_f = \overline{\mathbf{u}}_f - \overline{\left(\frac{1}{a_P}\right)}_f (\nabla p_f - \overline{\nabla p}_f) \tag{5.1}$$

**โดยที่:**
- $\overline{\mathbf{u}}_f$ = ความเร็วที่หน้าเซลล์จากการประมาณค่าเชิงเส้น
- $\overline{\left(\frac{1}{a_P}\right)}_f$ = ค่าสัมประสิทธิ์ที่ประมาณค่าที่หน้าเซลล์
- $\nabla p_f$ = เกรเดียนต์ความดันที่หน้าเซลล์
- $\overline{\nabla p}_f$ = เกรเดียนต์ความดันที่ประมาณค่า

> [!WARNING] ความสำคัญของ Rhie-Chow Interpolation
> เทอมที่เพิ่มเข้ามา $-\overline{\left(\frac{1}{a_P}\right)}_f (\nabla p_f - \overline{\nabla p}_f)$ ช่วย:
> - รับประกันว่าสนามความดันที่คำนวณได้จะเรียบ (smooth)
> - ไม่มีความผันผวนเชิงตัวเลขที่ผิดปกติ
> - รักษาการเชื่อมโยงความดัน-ความเร็วอย่างแท้จริง

### 5.3 การนำไปใช้ใน OpenFOAM

```cpp
// Rhie-Chow interpolation ใน OpenFOAM
surfaceScalarField rAUf
(
    "rAUf",
    fvc::interpolate(rAU)
);

surfaceScalarField phiHbyA
(
    "phiHbyA",
    (fvc::interpolate(HbyA) & mesh.Sf())
  - rAUf*fvc::snGrad(p)*mesh.magSf()
);
```

---

## 📊 6. สูตรการแก้ไขความดันและความเร็ว (Pressure-Velocity Correction)

### 6.1 สำหรับอัลกอริทึม SIMPLE (Steady-State)

**การแก้ไขความดัน:**
$$p^{k+1} = p^k + \alpha_p p' \tag{6.1}$$

**การแก้ไขความเร็ว:**
$$\mathbf{u}^{k+1} = \mathbf{u}^* - \frac{1}{a_P} \nabla p' \tag{6.2}$$

**โดยที่:**
- $p'$ = การแก้ไขความดัน (pressure correction)
- $\alpha_p$ = ตัวประกอบการผ่อนคลายความดัน (pressure relaxation factor)
- $k$ = ดรรชนีการวนซ้ำ

### 6.2 สำหรับอัลกอริทึม PISO (Transient)

**การแก้ไขความดัน (หลายครั้งต่อ Time Step):**
$$p^{n+1,i+1} = p^{n+1,i} + p'^{(i)} \tag{6.3}$$

**การแก้ไขความเร็ว:**
$$\mathbf{u}^{n+1,i+1} = \mathbf{u}^{n+1,i} - \frac{\Delta t}{a_P} \nabla p'^{(i)} \tag{6.4}$$

**โดยที่:**
- $n$ = ระดับเวลา (time level)
- $i$ = ดรรชนีการแก้ไข PISO
- $\Delta t$ = ขนาด Time Step

### 6.3 สูตรการ Under-Relaxation

เพื่อความเสถียรของการคำนวณ มีการใช้ **Under-Relaxation**:

**สำหรับความเร็ว:**
$$\mathbf{u}^{k+1} = \mathbf{u}^k + \alpha_u (\mathbf{u}^* - \mathbf{u}^k) \tag{6.5}$$

**สำหรับความดัน:**
$$p^{k+1} = p^k + \alpha_p p' \tag{6.6}$$

**ค่าที่แนะนำ:**

| ตัวแปร | ช่วงที่แนะนำ | ค่าที่พบบ่อย |
|:--------:|:--------------:|:---------------:|
| $\alpha_u$ (ความเร็ว) | 0.3 - 0.8 | 0.5 - 0.7 |
| $\alpha_p$ (ความดัน) | 0.1 - 0.5 | 0.2 - 0.4 |

---

## 🎯 7. สรุปสมการสำคัญ

### 7.1 ตารางสูตรที่ใช้บ่อย

| สมการ | สูตร | การใช้งาน |
|:------:|:-----:|:------------|
| **Discretized Momentum** | $a_P \mathbf{u}_P + \sum a_N \mathbf{u}_N = \mathbf{b}_P - \nabla p_P$ | การแก้สมการโมเมนตัม |
| **Pressure Correction (SIMPLE)** | $\nabla \cdot (\frac{1}{a_P} \nabla p') = \frac{\rho_P V_P}{\Delta t} \nabla \cdot \mathbf{u}^*$ | การแก้ไขความดัน steady-state |
| **Pressure Correction (PISO)** | $\nabla \cdot (\frac{1}{a_P} \nabla p') = \nabla \cdot \mathbf{u}^*$ | การแก้ไขความดัน transient |
| **Velocity Correction** | $\mathbf{u}^{n+1} = \mathbf{u}^* - \frac{1}{a_P} \nabla p'$ | การปรับความเร็ว |
| **Momentum Relaxation** | $\mathbf{u}^{k+1} = \mathbf{u}^k + \alpha_u (\mathbf{u}^* - \mathbf{u}^k)$ | การทำให้เสถียร steady-state |

### 7.2 การแมปกับ OpenFOAM Code

| คณิตศาสตร์ | OpenFOAM |
|:------------:|:--------:|
| $\frac{1}{a_P}$ | `rAU` หรือ `1.0/UEqn.A()` |
| $\frac{\mathbf{H}(\mathbf{u})}{a_P}$ | `HbyA` หรือ `UEqn.H()/UEqn.A()` |
| $\nabla p$ | `fvc::grad(p)` |
| $\nabla \cdot \mathbf{u}$ | `fvc::div(U)` |
| $\nabla^2 p$ | `fvm::laplacian(p)` |

---

## 📚 8. การอ้างอิงและบทความที่เกี่ยวข้อง

บทความนี้เป็นรากฐานทางคณิตศาสตร์สำหรับ:

- [[02_SIMPLE_Algorithm|อัลกอริทึม SIMPLE สำหรับ Steady-state]]
- [[03_PISO_Algorithm|อัลกอริทึม PISO สำหรับ Transient Flow]]
- [[04_PIMPLE_Algorithm|อัลกอริทึม PIMPLE แบบผสมผสาน]]

---

**หัวข้อถัดไป**: [[02_SIMPLE_Algorithm|อัลกอริทึม SIMPLE สำหรับการแก้ปัญหา Steady-state]]
