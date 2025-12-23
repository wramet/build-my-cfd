# รากฐานทางคณิตศาสตร์ของการเชื่อมโยงความดัน-ความเร็ว

## 📖 บทนำ (Introduction)

การจำลอง incompressible flow ใน OpenFOAM อาศัยการแก้สมการอนุรักษ์มวลและโมเมนตัม ปัญหาพื้นฐานอยู่ที่ความดัน ($p$) ไม่มีสมการควบคุมที่ชัดเจนในระบบของไหลอัดตัวไม่ได้ เอกสารนี้จะอธิบายวิธีการอนุพัทธ์สมการความดันจากเงื่อนไขทางกายภาพ

---

## 📐 1. สมการควบคุมในรูปแบบต่อเนื่อง (Continuous Equations)

สำหรับของไหล Newtonian ที่ความหนาแน่นคงที่:

**1. สมการความต่อเนื่อง (Continuity Equation):**
$$\nabla \cdot \mathbf{u} = 0 \tag{1.1}$$ 

**2. สมการโมเมนตัม (Momentum Equation):**
$$\rho \frac{\partial \mathbf{u}}{\partial t} + \rho (\mathbf{u} \cdot \nabla) \mathbf{u} = -\nabla p + \mu \nabla^2 \mathbf{u} + \mathbf{f} \tag{1.2}$$ 

ความดัน $p$ ทำหน้าที่เป็น Lagrange multiplier เพื่อรักษาเงื่อนไข $\nabla \cdot \mathbf{u} = 0$

---

## 🔢 2. การทำให้เป็นดิสครีต (Discretization)

เมื่อใช้ Finite Volume Method (FVM) กับสมการโมเมนตัมที่จุดศูนย์กลางเซลล์ $P$:

$$a_P \mathbf{u}_P + \sum_{N} a_N \mathbf{u}_N = \mathbf{b}_P - (\nabla p)_P \tag{2.1}$$ 

**สัมประสิทธิ์หลัก:**
- $a_P$: Diagonal coefficient (รวมพจน์เวลา, การพา, และการแพร่)
- $a_N$: Neighbor coefficients
- $\mathbf{b}_P$: Source terms (ไม่รวมพจน์ความดัน)

จัดรูปสมการใหม่ในรูปแบบ **Semi-discretized form**:
$$\mathbf{u}_P = \frac{\mathbf{H}(\mathbf{u})}{a_P} - \frac{1}{a_P} \nabla p \tag{2.2}$$ 

โดยที่ **H-operator** นิยามเป็น:
$$\mathbf{H}(\mathbf{u}) = \mathbf{b}_P - \sum_{N} a_N \mathbf{u}_N \tag{2.3}$$ 

ในซอร์สโค้ดของ OpenFOAM:
- `rAU` คือ $\frac{1}{a_P}$
- `HbyA` คือ $\frac{\mathbf{H}(\mathbf{u})}{a_P}$

---

## 🔄 3. การสร้างสมการความดัน (Pressure Equation Derivation)

เพื่อให้แน่ใจว่าความเร็วที่ได้จากสมการโมเมนตัมสอดคล้องกับสมการความต่อเนื่อง เรานำ Divergence ($\nabla \cdot$) มาใช้กับสมการ (2.2):

$$\nabla \cdot \mathbf{u}_P = \nabla \cdot \left( \frac{\mathbf{H}(\mathbf{u})}{a_P} \right) - \nabla \cdot \left( \frac{1}{a_P} \nabla p \right) = 0$$ 

จัดรูปจะได้ **Pressure Poisson Equation**:
$$\nabla \cdot \left( \frac{1}{a_P} \nabla p \right) = \nabla \cdot \left( \frac{\mathbf{H}(\mathbf{u})}{a_P} \right) \tag{3.1}$$ 

**ความสำคัญ:**
- สมการนี้ช่วยให้เราคำนวณสนามความดัน $p$ ที่สอดคล้องกับสนามความเร็ว $\mathbf{u}$
- ด้านขวาของสมการ (RHS) คือ Divergence ของ `HbyA` ซึ่งแสดงถึงความไม่สมดุลของมวลชั่วคราว

---

## 💻 4. OpenFOAM Implementation

ตัวอย่างการประกอบเมทริกซ์ใน OpenFOAM (`pEqn.H`):

```cpp
// 1. สร้าง HbyA และ rAU
volScalarField rAU(1.0/UEqn.A());
volVectorField HbyA(constrainHbyA(rAU*UEqn.H(), U, p));

// 2. สร้าง Flux ที่หน้าเซลล์โดยไม่รวมผลของความดัน
surfaceScalarField phiHbyA
(
    "phiHbyA",
    fvc::flux(HbyA)
  + fvc::interpolate(rAU)*fvc::ddtCorr(U, phi)
);

// 3. แก้สมการ Poisson สำหรับความดัน
fvScalarMatrix pEqn
(
    fvm::laplacian(rAU, p) == fvc::div(phiHbyA)
);
pEqn.solve();

// 4. แก้ไขความเร็ว (Velocity Correction)
U = HbyA - rAU*fvc::grad(p);
U.correctBoundaryConditions();
```

---

## 🧱 5. Rhie-Chow Interpolation

บน Collocated Grid ความเร็วที่หน้าเซลล์ ($\\mathbf{u}_f$) หากใช้การเฉลี่ยแบบ Linear ปกติ จะเกิดปัญหา **Checkerboard Decoupling** OpenFOAM จึงใช้สูตร:
$$\\mathbf{u}_f = \overline{\\mathbf{u}}_f - \overline{\\left(\\frac{1}{a_P}\\right)}_f (\\nabla p_f - \overline{\\nabla p}_f)$$
เทอมที่เพิ่มเข้ามาช่วยรับประกันว่าสนามความดันที่คำนวณได้จะเรียบและไม่มีความผันผวนเชิงตัวเลขที่ผิดปกติ

---
**หัวข้อถัดไป**: [อัลกอริทึม SIMPLE สำหรับ Steady-state](./02_SIMPLE_Algorithm.md)