# ความปั่นป่วนขั้นสูง (Advanced Turbulence)

## 📋 1. Large Eddy Simulation (LES)

LES ก้าวข้ามข้อจำกัดของ RANS โดยการจำลองโครงสร้างการไหลวนขนาดใหญ่ (Large Eddies) โดยตรง และใช้โมเดลสำหรับสเกลขนาดเล็กเท่านั้น

### 1.1 การกรองเชิงพื้นที่ (Spatial Filtering)
สมการ Navier-Stokes จะถูกกรองเพื่อแยกส่วนที่ต้องการแก้:
$$\frac{\partial \bar{u}_i}{\partial t} + \bar{u}_j \frac{\partial \bar{u}_i}{\partial x_j} = -\frac{1}{\rho} \frac{\partial \bar{p}}{\partial x_i} + \nu \frac{\partial^2 \bar{u}_i}{\partial x_j^2} - \frac{\partial \tau_{ij}}{\partial x_j}$$
โดยที่ $\tau_{ij}$ คือ **SGS (Subgrid-scale) stress tensor**

### 1.2 แบบจำลอง SGS ที่นิยม
- **Smagorinsky**: ใช้ค่าสัมประสิทธิ์คงที่ เรียบง่ายและเสถียร
- **WALE**: เหมาะสมมากสำหรับการไหลติดผนัง เนื่องจากค่าความหนืด Eddy จะลดลงสู่ศูนย์ที่ผนังโดยธรรมชาติ

---

## 🔀 2. Hybrid RANS-LES (DES)

**Detached Eddy Simulation (DES)** รวมประสิทธิภาพของ RANS ใกล้ผนังเข้ากับความแม่นยำของ LES ในบริเวณที่การไหลแยกตัว (Separated flow)

### 2.1 กลไกการสลับ (Switching Mechanism)
ใช้ระยะห่างจากผนัง ($y$) และขนาดของ Mesh ($\Delta$) เป็นตัวตัดสิน:
$$l_{DES} = \min(l_{RANS}, C_{DES} \Delta)$$

---

## 🏔️ 3. การทำนายการเปลี่ยนสภาพ (Transition Modeling)

ในงานวิศวกรรมบางประเภท (เช่น กังหันแก๊ส) การเปลี่ยนสภาพจาก Laminar ไปเป็น Turbulent เป็นจุดตัดสินประสิทธิภาพ

### 3.1 แบบจำลอง γ-Reθ
ใช้สมการขนส่งเพิ่มอีก 2 สมการเพื่อระบุ:
- **Intermittency ($\gamma$)**: สัดส่วนเวลาที่เป็นความปั่นป่วน
- **$Re_{\theta}$**: ระบุจุดเริ่มต้นของการเปลี่ยนสภาพ

---

## 🛠️ 4. ข้อควรระวังเชิงเทคนิค

- **Mesh Resolution**: LES ต้องการ Mesh ที่ละเอียดมากและมีความเป็น Isotropic สูง (Aspect ratio ใกล้ 1)
- **Time Step**: ค่า CFL มักต้องคุมให้อยู่ในช่วง 0.3 - 0.5 เพื่อความแม่นยำเชิงสถิติ

---
**หัวข้อถัดไป**: [วิธีการเชิงตัวเลขขั้นสูง (AMR & Adjoint)](./03_Numerical_Methods.md)
