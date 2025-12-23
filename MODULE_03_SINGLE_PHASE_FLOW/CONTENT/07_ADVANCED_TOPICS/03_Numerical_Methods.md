# วิธีการเชิงตัวเลขขั้นสูง (Advanced Numerical Methods)

## 📐 1. Adaptive Mesh Refinement (AMR)

**AMR** เป็นเทคนิคที่อนุญาตให้ OpenFOAM ปรับปรุง Mesh ให้ละเอียดขึ้นเฉพาะในบริเวณที่จำเป็นในระหว่างการรันจำลอง (Runtime) เช่น บริเวณที่มีความชัน (Gradient) ของตัวแปรสูง

### 1.1 เกณฑ์การปรับปรุง (Refinement Criteria)
- **Gradient Magnitude**: ปรับ Mesh เมื่อ $|
abla \phi| > \text{threshold}$
- **Vorticity**: ปรับรอบๆ โครงสร้างกระแสน้ำวน

### 1.2 ตัวอย่างการตั้งค่า (`system/controlDict`)
```cpp
dynamicFvMesh   dynamicRefineFvMesh;
dynamicRefineFvMeshCoeffs
{
    field           alpha.water; // หรือ U
    lowerRefineLevel 0.01;
    upperRefineLevel 0.99;
    maxRefinementLevel 2;
}
```

---

## 🏗️ 2. วิธีการ Adjoint (Adjoint Method)

ใช้สำหรับ **การปรับปรุงรูปร่างให้เหมาะสม (Shape Optimization)** และการวิเคราะห์ความไว (Sensitivity Analysis) โดยมีต้นทุนการคำนวณที่ไม่ขึ้นกับจำนวนตัวแปรการออกแบบ

### 2.1 หลักการ
หาเกรเดียนต์ของฟังก์ชันวัตถุประสงค์ ($J$) เช่น แรงต้าน เทียบกับการเปลี่ยนแปลงรูปร่างพื้นผิว ($\alpha$):
$$\frac{\mathrm{d}J}{\mathrm{d}\alpha} = \frac{\partial J}{\partial \alpha} + \boldsymbol{\lambda}^T \frac{\partial \mathbf{R}}{\partial \alpha}$$ 
โดยที่ $\boldsymbol{\lambda}$ คือสนาม Adjoint ที่ต้องแก้หา

---

## 👻 3. Immersed Boundary Method (IBM)

จัดการกับรูปทรงเรขาคณิตที่ซับซ้อนโดยไม่ต้องสร้าง Mesh ที่สอดคล้องกับขอบเขต (Non-conformal mesh) แต่ใช้การปรับแต่ง Source term ในสมการโมเมนตัมแทน เหมาะสำหรับปัญหาที่มีการเคลื่อนที่ของวัตถุขนาดใหญ่หรือซับซ้อนมาก

---

## 🤖 4. บูรณาการ Machine Learning

- **PINNs (Physics-Informed Neural Networks)**: ฝังสมการ Navier-Stokes ลงใน Loss function ของโครงข่ายประสาทเทียม เพื่อเร่งการหาผลเฉลยหรือสร้างแบบจำลองแทน (Surrogates)
- **ROM (Reduced Order Modeling)**: ใช้เทคนิค POD หรือ DMD เพื่อลดมิติของปัญหาขนาดใหญ่ให้เหลือเพียงไม่กี่โหมดที่สำคัญ

---
**หัวข้อถัดไป**: [การเชื่อมโยงหลายฟิสิกส์ (Multiphysics)](./04_Multiphysics.md)
