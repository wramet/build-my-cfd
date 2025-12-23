# การอนุรักษ์พลังงานในระบบหลายเฟส (Energy Conservation Equations)

## 📐 สมการพลังงานเฉพาะเฟส (Phase-Specific Energy Equation)

ในระบบหลายเฟส แต่ละเฟส $k$ มีการอนุรักษ์พลังงานที่รวมถึงการพาความร้อน การนำความร้อน งานจากความดัน และการแลกเปลี่ยนพลังงานที่รอยต่อ

### สมการในรูปของเอนทัลปีจำเพาะ ($h_k$)
สำหรับเฟส $k$:

$$\frac{\partial}{\partial t}(\alpha_k \rho_k h_k) + \nabla \cdot (\alpha_k \rho_k \mathbf{u}_k h_k) = \alpha_k \frac{\partial p}{\partial t} + \nabla \cdot (\alpha_k \kappa_k \nabla T_k) + \Phi_k + \dot{q}_k + \dot{m}_k h_{k,int} + \mathbf{M}_k \cdot \mathbf{u}_k \tag{3.1}$$

**นิยามตัวแปร**:
- $\alpha_k$ = สัดส่วนปริมาตรของเฟส $k$
- $\rho_k$ = ความหนาแน่นของเฟส $k$ ($\text{kg/m}^3$)
- $h_k$ = เอนทัลปีจำเพาะของเฟส $k$ ($\text{J/kg}$)
- $\mathbf{u}_k$ = ความเร็วของเฟส $k$ ($\text{m/s}$)
- $p$ = ความดัน ($\text{Pa}$)
- $\kappa_k$ = สภาพนำความร้อนของเฟส $k$ ($\text{W/(m·K)}$)
- $T_k$ = อุณหภูมิของเฟส $k$ ($\text{K}$)
- $\Phi_k$ = การกระจายความหนืด (Viscous Dissipation) ($\text{W/m}^3$)
- $\dot{q}_k$ = อัตราการถ่ายเทความร้อนระหว่างเฟส ($\text{W/m}^3$)
- $\dot{m}_k$ = อัตราการถ่ายเทมวล ($\text{kg/(m}^3\cdot\text{s)}$)
- $h_{k,int}$ = เอนทัลปีที่พื้นผิวรอยต่อ ($\text{J/kg}$)
- $\mathbf{M}_k$ = แรงที่รอยต่อ (Interfacial Force) ($\text{N/m}^3$)

---

## 🔍 การวิเคราะห์แต่ละเทอมในสมการ

### 1. งานจากความดัน (Pressure Work)
$$\alpha_k \frac{\partial p}{\partial t}$$
แสดงถึงงานที่ทำโดยการเปลี่ยนแปลงความดันตามเวลา สำคัญมากสำหรับระบบที่อัดตัวได้ (Compressible flows)

### 2. การนำความร้อน (Heat Conduction)
$$\nabla \cdot (\alpha_k \kappa_k \nabla T_k)$$
การนำความร้อนภายในเฟสตามกฎของฟูเรียร์ (Fourier's Law)

### 3. การกระจายความหนืด (Viscous Dissipation)
$$\Phi_k = \boldsymbol{\tau}_k : \nabla \mathbf{u}_k$$
การแปลงพลังงานกลเป็นความร้อนผ่านแรงเสียดทานหนืดภายในเฟส

### 4. การถ่ายเทความร้อนระหว่างเฟส ($\dot{q}_k$)
$$\dot{q}_{kl} = h_{kl} A_{kl} (T_l - T_k)$$
โดยที่ $h_{kl}$ คือสัมประสิทธิ์การถ่ายเทความร้อน และ $A_{kl}$ คือความหนาแน่นพื้นที่รอยต่อ

---

## 🌡️ อุณหพลศาสตร์ของการเปลี่ยนเฟส (Phase Change)

ระหว่างการเปลี่ยนเฟส (เช่น การระเหยหรือควบแน่น) สมดุลพลังงานต้องพิจารณาความร้อนแฝง (Latent Heat):

$$\dot{m}_{kl} L + \dot{q}_{kl} = 0 \tag{3.2}$$

โดยที่ $L = h_{vapor}^{sat} - h_{liquid}^{sat}$ คือความร้อนแฝงของการกลายเป็นไอ

---

## 💻 การนำไปใช้ใน OpenFOAM (C++ Implementation)

ใน Solver เช่น `reactingTwoPhaseEulerFoam`, สมการพลังงานถูกสร้างดังนี้:

```cpp
// Energy equation construction for phase k
 fvScalarMatrix hEqn
 (
 fvm::ddt(alpha, rho, h) + fvm::div(alphaRhoPhi, h)
 ==
 alpha*rho*(dpdt)            // Pressure work
 + fvc::div(alpha*kappa*grad(T)) // Conduction
 + interfacialHeatTransfer     // Heat transfer between phases
 + massTransfer*InterfaceEnthalpy // Latent heat / phase change
 + interfacialMomentumTransfer & U  // Interfacial work
 );
```

### การตั้งค่าเทอร์โมฟิสิกส์
OpenFOAM ต้องการไฟล์ `constant/thermophysicalProperties.phaseName` เพื่อกำหนดโมเดลพลังงาน เช่น:
- `hConstThermo`: เอนทัลปีคงที่
- `janafThermo`: เอนทัลปีแปรผันตามอุณหภูมิ (JANAF tables)


---

## 📊 ตารางสรุปกลไกการแลกเปลี่ยนพลังงาน

| กลไก | สมการปิด (Closure) | ความสำคัญ |
|-----|-------------------|-----------|
| **Interphase Heat** | Nusselt Correlations (Ranz-Marshall) | สูง (ระบบที่มีความต่างอุณหภูมิ) |
| **Latent Heat** | Clausius-Clapeyron | สูงมาก (Boiling, Condensation) |
| **Viscous Work** | Viscous Dissipation Model | ต่ำ (ยกเว้น High-speed/High-viscosity) |

การเลือกโมเดลการถ่ายเทความร้อนที่ถูกต้อง ($Nu$ correlation) มีผลอย่างยิ่งต่อความแม่นยำในการทำนายอุณหภูมิของแต่ละเฟสในระบบ
