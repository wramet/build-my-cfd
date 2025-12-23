# พื้นฐานทางฟิสิกส์และความคณิตศาสตร์ของความปั่นป่วน

## 🌊 1. ปรากฏการณ์ความปั่นป่วน (Turbulence Phenomenon)

ความปั่นป่วนเป็นสถานะการไหลที่เกิดขึ้นเมื่อแรงเฉื่อย (Inertial forces) มีอิทธิพลเหนือแรงหนืด (Viscous forces) ซึ่งมักเกิดขึ้นที่ค่า **Reynolds Number ($Re$)** สูง

### 1.1 ลักษณะเด่นของความปั่นป่วน:
- **Irregularity**: มีลักษณะสุ่มและวุ่นวาย
- **Diffusivity**: เพิ่มการผสม (Mixing) ของมวล โมเมนตัม และความร้อนอย่างมหาศาล
- **Dissipative**: พลังงานจลน์ถูกถ่ายโอนจากโครงสร้างใหญ่ไปเล็กและเปลี่ยนเป็นความร้อน (Energy Cascade)
- **Three-dimensional**: ความปั่นป่วนมีความเป็นสามมิติโดยธรรมชาติเสมอ

---

## 📐 2. การหาค่าเฉลี่ยแบบ Reynolds (Reynolds Averaging) 

ในการจำลอง RANS เราไม่ได้แก้ความผันผวนชั่วขณะ แต่จะแก้สมการสำหรับค่าเฉลี่ยตามเวลา ผ่านการแยกตัวแปรแบบ **Reynolds Decomposition**:

$$\phi(\mathbf{x}, t) = \overline{\phi}(\mathbf{x}, t) + \phi'(\mathbf{x}, t)$$

โดยที่:
- $\overline{\phi}$: ส่วนเฉลี่ยตามเวลา (Time-averaged component)
- $\phi'$: ส่วนผันผวน (Fluctuating component) โดยมีเงื่อนไข $\overline{\phi'} = 0$

---

## ⚖️ 3. สมการ RANS (Reynolds-Averaged Navier-Stokes)

เมื่อนำการแยกส่วนเข้าไปแทนในสมการ Navier-Stokes และทำการเฉลี่ย จะได้สมการควบคุมสำหรับการไหลแบบอัดตัวไม่ได้:

**สมการความต่อเนื่องเฉลี่ย:**
$$\nabla \cdot \overline{\mathbf{u}} = 0$$

**สมการโมเมนตัมเฉลี่ย:**
$$\rho \frac{\partial \overline{\mathbf{u}}}{\partial t} + \rho (\overline{\mathbf{u}} \cdot \nabla) \overline{\mathbf{u}} = -\nabla \overline{p} + \mu \nabla^2 \overline{\mathbf{u}} + \nabla \cdot \boldsymbol{\tau}_{R}$$

เทอมใหม่ที่เกิดขึ้นคือ **Reynolds Stress Tensor ($oldsymbol{	au}_{R}$)**:
$$\boldsymbol{\tau}_{R} = -\rho \overline{\mathbf{u}' \otimes \mathbf{u}'}$$
เทอมนี้แสดงถึงผลกระทบของความปั่นป่วนที่มีต่อการไหลเฉลี่ย และเป็นจุดเริ่มต้นของปัญหา **Closure Problem** (ความต้องการสมการเพิ่มเพื่อแก้หาตัวแปรที่ไม่ทราบค่า)

---

## 🔧 4. สมมติฐานความหนืดไหลวน (Boussinesq Hypothesis)

เพื่อปิดสมการ RANS วิธีที่นิยมที่สุดคือการสมมติว่าความเค้นปั่นป่วนเป็นสัดส่วนกับอัตราการเปลี่ยนแปลงรูปเฉลี่ย (Mean strain rate):

$$\boldsymbol{\tau}_{R} = \mu_t \left( \nabla \overline{\mathbf{u}} + (\nabla \overline{\mathbf{u}})^T \right) - \frac{2}{3} \rho k \mathbf{I}$$

โดยที่:
- $\mu_t$: **Eddy Viscosity** (ความหนืดปั่นป่วน) - ไม่ใช่คุณสมบัติของของไหลแต่เป็นคุณสมบัติของการไหล
- $k$: **Turbulent Kinetic Energy** (พลังงานจลน์ปั่นป่วน)

---

## 📊 5. สถาปัตยกรรมใน OpenFOAM

OpenFOAM จัดการความหนืดปั่นป่วนผ่านฟังก์ชัน `divDevTau` (หรือ `divDevReff`) ซึ่งฉีดความเค้นเข้าไปในสมการโมเมนตัม:

```cpp
// ภายใน UEqn.H
tmp<fvVectorMatrix> tUEqn
(
    fvm::ddt(rho, U) + fvm::div(phi, U)
  + turbulence->divDevRhoReff(U) // เพิ่มผลของ Turbulence
 ==
    fvOptions(rho, U)
);
```

ฟังก์ชันนี้จะคำนวณ $\nu_{eff} = \nu + \nu_t$ โดยอัตโนมัติตามโมเดลที่ผู้ใช้เลือกในรันไทม์

---
**หัวข้อถัดไป**: [แบบจำลอง RANS เชิงรายละเอียด](./02_RANS_Models.md)
