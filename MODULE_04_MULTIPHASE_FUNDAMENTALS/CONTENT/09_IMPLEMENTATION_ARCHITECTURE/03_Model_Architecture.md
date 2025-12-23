# สถาปัตยกรรมโมเดลและรายละเอียดการนำไปใช้งาน (Model Architecture & Implementation)

## 1. บทนำ (Introduction)

OpenFOAM ใช้สถาปัตยกรรมที่ยืดหยุ่นและขยายได้สูง (Modular & Extensible) สำหรับการจัดการโมเดลหลายเฟส โดยเฉพาะใน `multiphaseEulerFoam` ซึ่งใช้ระบบ **Run-time Selection** ช่วยให้ผู้ใช้สามารถเลือกหรือเปลี่ยนโมเดลฟิสิกส์ต่างๆ ได้ผ่านไฟล์การตั้งค่าโดยไม่ต้องคอมไพล์โค้ดใหม่

---

## 2. หลักการออกแบบหลัก (Core Design Principles)

- **Runtime Selection**: โมเดลถูกเลือกแบบไดนามิกผ่านพจนานุกรม `phaseProperties` โดยใช้กลไก `TypeName` และ `New`
- **Polymorphism**: ใช้คลาสฐาน (Base class) กำหนดอินเตอร์เฟซมาตรฐาน (เช่น `dragModel`) และให้คลาสลูก (Derived class) นำไปใช้งานจริง (เช่น `SchillerNaumannDrag`)
- **Phase-pair Specificity**: โมเดลส่วนใหญ่ทำงานบนออบเจ็กต์ `phasePair` ซึ่งเก็บข้อมูลการปฏิสัมพันธ์ระหว่างคู่เฟสที่เฉพาะเจาะจง

---

## 3. โมเดลการถ่ายโอนโมเมนตัมระหว่างเฟส (Interfacial Momentum Transfer)

เทอม $\mathbf{M}_k$ ในสมการโมเมนตัมคือผลรวมของแรงต่างๆ ที่เกิดขึ้นที่อินเตอร์เฟซ:
$$\mathbf{M}_k = \sum_{l=1}^{N} (\mathbf{F}^{D}_{kl} + \mathbf{F}^{L}_{kl} + \mathbf{F}^{VM}_{kl} + \mathbf{F}^{TD}_{kl})$$

### 3.1 โมเดลแรงลาก (Drag Model - `dragModel`)
ใช้คำนวณแรงต้านการเคลื่อนที่ระหว่างเฟส คลาสฐานกำหนดเมธอดหลักดังนี้:
```cpp
virtual tmp<volVectorField> F(const phaseModel& p1, const phaseModel& p2) const = 0;
virtual tmp<volScalarField> Cd() const = 0; // Drag coefficient
virtual tmp<volScalarField> K() const = 0;  // Momentum exchange coefficient
```

**ตัวอย่าง: Schiller-Naumann Drag**
เหมาะสำหรับฟองอากาศหรืออนุภาคทรงกลม:
$$C_D = \begin{cases} 24(1 + 0.15 Re^{0.687}) / Re & \text{if } Re < 1000 \\ 0.44 & \text{if } Re \geq 1000 \end{cases}$$
โดยที่ $Re = \rho_p |\mathbf{u}_p - \mathbf{u}_c| d_p / \mu_c$

### 3.2 แรงอื่นๆ (Lift, Virtual Mass, Turbulent Dispersion)
- **Lift Force**: $\mathbf{F}^{L}_{kl} = C_L \rho_k \alpha_l (\mathbf{u}_l - \mathbf{u}_k) \times (\nabla \times \mathbf{u}_k)$
- **Virtual Mass**: $\mathbf{F}^{VM}_{kl} = C_{VM} \rho_k \alpha_l \left(\frac{D\mathbf{u}_l}{Dt} - \frac{D\mathbf{u}_k}{Dt}\right)$
- **Turbulent Dispersion**: $\mathbf{F}^{TD}_{kl} = C_{TD} \rho_k \frac{\mu_{t,k}}{\sigma_{t,k}} (\nabla \alpha_l - \nabla \alpha_k)$

---

## 4. โมเดลการถ่ายโอนความร้อนและมวล (Heat & Mass Transfer)

- **Heat Transfer**: $Q_k = \sum_{l=1}^{N} h_{kl} A_{kl} (T_l - T_k)$ โดย $h_{kl}$ คือสัมประสิทธิ์การถ่ายโอนความร้อน และ $A_{kl}$ คือความหนาแน่นพื้นที่ผิวอินเตอร์เฟซ
- **Mass Transfer**: ควบคุมการเปลี่ยนเฟส โดยต้องเป็นไปตามเงื่อนไขการอนุรักษ์มวลรวม: $\sum_k \sum_l \dot{m}_{lk} = 0$

---

## 5. การบูรณาการโมเดลความปั่นป่วน (Turbulence Modeling)

คลาส `phaseCompressibleTurbulenceModel` ขยายความสามารถของโมเดลเฟสเดียวให้รองรับหลายเฟส:
- แต่ละเฟสมีสนามความปั่นป่วน ($k, \epsilon, \omega$) เป็นของตัวเอง
- มีการคำนวณ **Reynolds Stress**: $\mathbf{R}_k = -\rho_k \overline{\mathbf{u}'_k \mathbf{u}'_k}$
- คำนวณ **Turbulent Viscosity**: $\mu_{t,k} = \rho_k C_\mu \frac{k_k^2}{\epsilon_k}$

---

## 6. รายละเอียดการนำสมการไปใช้งาน (Code Implementation)

### 6.1 สมการสัดส่วนเฟส (`alphaEqns.H`)
ใช้ติดตามการกระจายตัวของเฟส:
```cpp
fvScalarMatrix alphaEqn
(
    fvm::ddt(alpha, phase.rho())
  + fvm::div(alphaPhi, phase.rho())
 ==
    phase.massTransferSource()
);
alphaEqn.solve();
alpha.maxMin(1.0, 0.0); // Bounding เพื่อความเสถียร
```

### 6.2 สมการโมเมนตัม (`UEqns.H`)
แก้สมการสำหรับแต่ละเฟสพร้อมเทอมการถ่ายโอนระหว่างเฟส:
```cpp
fvVectorMatrix UEqn
(
    fvm::ddt(alpha, phase.rho(), U)
  + fvm::div(alphaPhi, phase.rho(), U)
 ==
    - alpha*fvc::grad(p)
  + fvc::div(alpha*phase.R())
  + alpha*rho*g
  + phase.interfacialMomentumTransfer()
);
```

### 6.3 สมการความดัน (`pEqn.H`)
ใช้รักษาความต่อเนื่องของมวลรวม โดยอิงจากอัลกอริทึม **PISO/PIMPLE**:
1. **Predictor Step**: ทำนายความเร็วเบื้องต้น
2. **Pressure Solution**: แก้สมการ Poisson สำหรับความดันร่วม
3. **Correctors**: แก้ไขความเร็วและ Flux ให้สอดคล้องกับความดันใหม่

---

## 7. แนวทางการขยายโมเดล (Extensibility)

หากต้องการเพิ่มโมเดลแรง Drag ใหม่:
1. สร้างคลาสใหม่ที่สืบทอดจาก `dragModel`
2. นำฟังก์ชัน `F()`, `Cd()`, `K()` ไปใช้งานตามสูตรคณิตศาสตร์ที่ต้องการ
3. ลงทะเบียนโมเดลด้วยมาโคร `defineTypeName` และ `addToRunTimeSelectionTable`
4. เรียกใช้งานในไฟล์ `constant/phaseProperties` ของเคสที่ต้องการ

สถาปัตยกรรมนี้ช่วยให้ OpenFOAM สามารถรองรับงานวิจัยและการใช้งานในอุตสาหกรรมที่ต้องการความละเอียดและความซับซ้อนของฟิสิกส์ในระดับสูงได้

*อ้างอิง: วิเคราะห์ตามซอร์สโค้ด OpenFOAM-10, dragModel.H และกลไก interfacialMomentumTransfer ของ multiphaseEulerFoam*