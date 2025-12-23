# การเชื่อมโยงความดัน-ความเร็ว (Pressure-Velocity Coupling)

## 🔍 ภาพรวม (Overview)

**การเชื่อมโยงความดัน-ความเร็ว (Pressure-velocity coupling)** เป็นความท้าทายเชิงตัวเลขที่สำคัญที่สุดใน Computational Fluid Dynamics (CFD) สำหรับการไหลที่อัดตัวไม่ได้ (incompressible flows) เนื่องจากสมการความต่อเนื่อง (continuity equation) ไม่มีพจน์ความดันที่ชัดเจน ความดันจึงทำหน้าที่เป็น "Lagrange multiplier" เพื่อบังคับให้สนามความเร็วเป็นไปตามเงื่อนไข Divergence-free

---


## 📐 1. รากฐานทางคณิตศาสตร์ (Mathematical Foundation)

### 1.1 ปัญหาการเชื่อมโยง (The Coupling Problem)
สมการ Navier-Stokes สำหรับ incompressible flow:
- **สมการความต่อเนื่อง**: $\nabla \cdot \mathbf{u} = 0$
- **สมการโมเมนตัม**: $\rho \left( \frac{\partial \mathbf{u}}{\partial t} + \mathbf{u} \cdot \nabla \mathbf{u} \right) = -\nabla p + \mu \nabla^2 \mathbf{u} + \mathbf{f}$

**ความท้าทาย:**
1. ความดันปรากฏเฉพาะในสมการโมเมนตัมในรูปของเกรเดียนต์ ($-\nabla p$)
2. สมการความต่อเนื่องเป็นข้อจำกัดเชิงจลนศาสตร์ของความเร็ว ไม่ใช่สมการวิวัฒนาการของความดัน
3. บน Collocated Grid หากไม่จัดการอย่างเหมาะสมจะเกิดปัญหา **Checkerboard oscillations**

### 1.2 รูปแบบดิสครีต (Discretized Form)
ใน OpenFOAM สมการโมเมนตัมถูกทำให้เป็นดิสครีตในรูปแบบ:
$$a_P \mathbf{u}_P + \sum_N a_N \mathbf{u}_N = \mathbf{b}_P - (\nabla p)_P$$
ซึ่งสามารถจัดรูปใหม่ได้เป็น:
$$\mathbf{u}_P = \frac{\mathbf{H}(\mathbf{u})}{a_P} - \frac{1}{a_P} \nabla p$$
โดยที่ $\mathbf{H}(\mathbf{u})$ บรรจุเทอมเพื่อนบ้านและเทอมแหล่งกำเนิด

---


## ⚙️ 2. อัลกอริทึมหลักใน OpenFOAM

OpenFOAM นำเสนอสามอัลกอริทึมหลักเพื่อแก้ปัญหาการเชื่อมโยงนี้:

### 2.1 SIMPLE (Semi-Implicit Method for Pressure-Linked Equations)
- **วัตถุประสงค์**: สำหรับสภาวะคงที่ (Steady-state)
- **กลไก**: ใช้การทำนายโมเมนตัมตามด้วยการแก้ไขความดัน (Pressure Correction)
- **ความเสถียร**: จำเป็นต้องใช้ **Under-relaxation** ($\alpha_p \approx 0.3, \alpha_U \approx 0.7$)

### 2.2 PISO (Pressure-Implicit with Splitting of Operators)
- **วัตถุประสงค์**: สำหรับสภาวะชั่วคร่าว (Transient) ที่ต้องการความแม่นยำเชิงเวลาสูง
- **กลไก**: ใช้ขั้นตอน Corrector หลายรอบภายในหนึ่ง Time-step เพื่อรักษา Temporal Accuracy
- **ข้อจำกัด**: มักต้องการ $Co < 1$ เพื่อความเสถียร

### 2.3 PIMPLE (PISO + SIMPLE Hybrid)
- **วัตถุประสงค์**: สำหรับสภาวะชั่วคร่าวที่ต้องการความแข็งแกร่ง (Robustness) สูง
- **กลไก**: รวมลูปภายนอก (Outer loops) แบบ SIMPLE เข้ากับลูปภายในแบบ PISO
- **จุดเด่น**: สามารถรันด้วย Time-step ขนาดใหญ่ได้ ($Co > 1$)

---


## 🛠️ 3. เทคนิคพิเศษใน OpenFOAM

### 3.1 Rhie-Chow Interpolation
เพื่อป้องกันปัญหาสนามความดันแบบตารางหมากรุกบน Collocated Grid OpenFOAM ใช้การประมาณค่าความเร็วที่หน้าเซลล์ ($\\mathbf{u}_f$) แบบพิเศษ:
$$\\mathbf{u}_f = \overline{\\mathbf{u}}_f - \mathbf{D}_f (\nabla p_f - \overline{\nabla p}_f)$$
เทอมที่เพิ่มเข้ามาทำหน้าที่เป็น Numerical Diffusion ที่ช่วยเชื่อมโยงความดันและความเร็วในระดับเซลล์

### 3.2 Non-Orthogonal Correction
สำหรับ Mesh ที่ไม่ตั้งฉาก ($\theta > 0$) OpenFOAM จะทำการวนซ้ำเพื่อแก้ไขความคลาดเคลื่อนของ Laplacian operator:
```cpp
while (pimple.correctNonOrthogonal())
{
    fvScalarMatrix pEqn(fvm::laplacian(rAU, p) == fvc::div(phiHbyA));
    pEqn.solve();
}
```

---


## 📋 4. สรุปพารามิเตอร์ที่แนะนำ (Recommended Parameters)

| อัลกอริทึม | Pressure Relaxation | Velocity Relaxation | nCorrectors |
|------------|---------------------|---------------------|-------------|
| **SIMPLE** | 0.2 - 0.3 | 0.5 - 0.7 | 1 |
| **PISO** | 1.0 (No relax) | 1.0 (No relax) | 2 - 3 |
| **PIMPLE** | 0.3 - 0.7 (Outer) | 0.6 - 0.9 (Outer) | Inner: 2, Outer: 2-5 |

---
**หัวข้อถัดไป**: [รากฐานทางคณิตศาสตร์อย่างละเอียด](./01_Mathematical_Foundation.md)
