# การอนุรักษ์โมเมนตัมในระบบหลายเฟส (Momentum Conservation Equations)

## 📐 สมการโมเมนตัมเฉพาะเฟส (Phase-Specific Momentum Equation)

ในกรอบงานแบบ Eulerian-Eulerian แต่ละเฟส $k$ จะถูกควบคุมด้วยสมการโมเมนตัมของตนเอง ซึ่งรวมถึงแรงดัน แรงหนืด แรงโน้มถ่วง และแรงปฏิสัมพันธ์ระหว่างเฟส

### สมการทั่วไป
สำหรับเฟส $k$ ในระบบหลายเฟส:

$$\frac{\partial}{\partial t}(\alpha_k \rho_k \mathbf{u}_k) + \nabla \cdot (\alpha_k \rho_k \mathbf{u}_k \mathbf{u}_k) = -\alpha_k \nabla p + \nabla \cdot (\alpha_k \boldsymbol{\tau}_k) + \alpha_k \rho_k \mathbf{g} + \mathbf{M}_k \tag{2.1}$$

**นิยามตัวแปร:**
- $\alpha_k$ = สัดส่วนปริมาตรของเฟส $k$ (volume fraction)
- $\rho_k$ = ความหนาแน่นของเฟส $k$ (\text{kg/m}^3)
- $\mathbf{u}_k$ = เวกเตอร์ความเร็วของเฟส $k$ (\text{m/s})
- $p$ = ความดันร่วมระหว่างเฟส (\text{Pa})
- $\boldsymbol{\tau}_k$ = เทนเซอร์ความเค้น (stress tensor) ของเฟส $k$
- $\mathbf{g}$ = เวกเตอร์ความเร่งโน้มถ่วง (\text{m/s}^2)
- $\mathbf{M}_k$ = การถ่ายเทโมเมนตัมระหว่างเฟส (interfacial momentum transfer) (\text{N/m}^3)

---

## 🔍 การวิเคราะห์แต่ละเทอมในสมการ

### 1. ความเร่งตามเวลา (Temporal Acceleration)
$$\frac{\partial}{\partial t}(\alpha_k \rho_k \mathbf{u}_k)$$
แสดงถึงอัตราการเปลี่ยนแปลงโมเมนตัมเฉพาะที่ของเฟส $k$ ซึ่งรวมถึงการเปลี่ยนแปลงทั้งความเร็วและสัดส่วนปริมาตร

### 2. ความเร่งแบบพา (Convective Acceleration)
$$\nabla \cdot (\alpha_k \rho_k \mathbf{u}_k \mathbf{u}_k)$$
แสดงถึงฟลักซ์โมเมนตัมเนื่องจากการเคลื่อนที่ของเฟส $k$ ผ่านขอบเขตของปริมาตรควบคุม

### 3. แรงดัน (Pressure Force)
$$-\alpha_k \nabla p$$
แรงเนื่องจากความชันของสนามความดันร่วม (shared pressure field) โดยถูกถ่วงน้ำหนักด้วยสัดส่วนปริมาตรของเฟสนั้นๆ

### 4. แรงหนืด (Viscous Force)
$$\nabla \cdot (\alpha_k \boldsymbol{\tau}_k)$$
สำหรับของไหลนิวตัน เทนเซอร์ความเค้นหนืดคือ:
$$\boldsymbol{\tau}_k = \mu_k \left( \nabla \mathbf{u}_k + (\nabla \mathbf{u}_k)^T \right) - \frac{2}{3}\mu_k (\nabla \cdot \mathbf{u}_k)\mathbf{I}$$

### 5. การถ่ายเทโมเมนตัมระหว่างเฟส ($\mathbf{M}_k$)
เป็นเทอมที่สำคัญที่สุดซึ่งเชื่อมโยงพลศาสตร์ของแต่ละเฟสเข้าด้วยกัน โดยมีเงื่อนไขการอนุรักษ์คือ $\sum \mathbf{M}_k = \mathbf{0}$

---

## 🔄 แรงระหว่างเฟส (Interfacial Forces)

เทอม $\mathbf{M}_k$ ประกอบด้วยแรงย่อยต่างๆ ดังนี้:

$$\mathbf{M}_k = \sum_{j \neq k} \left[ \mathbf{M}_{kj}^{drag} + \mathbf{M}_{kj}^{lift} + \mathbf{M}_{kj}^{vm} + \mathbf{M}_{kj}^{td} \right] \tag{2.2}$$

### 1. แรงฉุด (Drag Force)
เกิดจากความเร็วสัมพัทธ์ระหว่างเฟส:
$$\mathbf{M}_{kj}^{drag} = K_{kj}(\mathbf{u}_j - \mathbf{u}_k)$$
โดยที่ $K_{kj}$ คือสัมประสิทธิ์การแลกเปลี่ยนโมเมนตัม ซึ่งคำนวณจาก Drag Model เช่น Schiller-Naumann

### 2. แรงยก (Lift Force)
เกิดจากการไล่ระดับความเร็ว (velocity gradient) ในเฟสต่อเนื่อง:
$$\mathbf{M}_{kj}^{lift} = C_L \rho_c \alpha_k \alpha_j (\mathbf{u}_j - \mathbf{u}_k) \times (\nabla \times \mathbf{u}_c)$$

### 3. แรงมวลเสมือน (Virtual Mass Force)
เกิดจากการเร่งความเร็วของของไหลรอบข้างเมื่ออนุภาคเร่งความเร็ว:
$$\mathbf{M}_{kj}^{vm} = C_{vm} \rho_c \alpha_k \alpha_j \left( \frac{\mathrm{D}\mathbf{u}_j}{\mathrm{D}t} - \frac{\mathrm{D}\mathbf{u}_k}{\mathrm{D}t} \right)$$

---

## 💻 การนำไปใช้ใน OpenFOAM (C++ Implementation)

ในไฟล์ `UEqn.H` ของ Solver `multiphaseEulerFoam`, สมการโมเมนตัมถูกสร้างดังนี้:

```cpp
// Momentum equation assembly for phase k
fvVectorMatrix UEqn
(
    fvm::ddt(alpha, rho, U) + fvm::div(alphaRhoPhi, U)
  - fvm::Sp(fvc::ddt(alpha, rho) + fvc::div(alphaRhoPhi), U)
  + turbulence->divDevReff(RhoEff)
 ==
    - alpha*fvc::grad(p)
    + alpha*rho*g
    + phase.Kd()*(U.otherPhase() - U) // Drag coupling
    + interfacialForces // Lift, virtual mass, etc.
);
```

### การเชื่อมโยงความดัน-ความเร็ว
OpenFOAM ใช้เทคนิค **Partial Elimination Algorithm (PEA)** เพื่อจัดการกับเทอม Drag ที่มีความแข็ง (stiffness) สูง โดยการย้ายเทอมความเร็วของเฟสอื่นมาไว้ในด้าน implicit เพื่อเพิ่มความเสถียรในการคำนวณ

---

## 📊 ตารางสรุปพฤติกรรมทางฟิสิกส์

| แรง | กลไกหลัก | ความสำคัญ |
|-----|----------|-----------|
| **Drag** | ความเร็วสัมพัทธ์ | สูงมาก (ทุกระบบ) |
| **Lift** | การเฉือน (Shear) | สูง (การไหลในท่อ, ฟองอากาศ) |
| **Virtual Mass** | การเร่งความเร็ว (Acceleration) | สูง (Unsteady flows, Gas-Liquid) |
| **Turbulent Dispersion** | ความปั่นป่วน (Turbulence) | ปานกลาง (การผสมเฟส) |

การจำลองที่แม่นยำต้องอาศัยการเลือกโมเดลแรงระหว่างเฟสที่สอดคล้องกับพฤติกรรมจริงของของไหลในแต่ละระบอบการไหล (flow regime)
