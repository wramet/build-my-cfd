# พื้นฐานสมการพลังงานใน OpenFOAM

## 📖 บทนำ (Introduction)

**สมการการอนุรักษ์พลังงาน** เป็นหัวใจสำคัญของการวิเคราะห์ความร้อน ซึ่งเชื่อมโยงการไหลของของไหลเข้ากับการถ่ายเทพลังงาน โดยพิจารณาสมดุลระหว่างการพาความร้อน การนำความร้อน และแหล่งกำเนิดความร้อนอื่นๆ

---

## 📐 1. สมการพลังงานในรูปแบบทางคณิตศาสตร์

สำหรับการจำลองใน OpenFOAM สมการมักจะถูกเขียนในรูปของเอนทาลปีสัมผัส (Sensible Enthalpy, $h$):

$$\frac{\partial (\rho h)}{\partial t} + \nabla  \cdot (\rho \mathbf{u} h) = \nabla  \cdot (k \nabla T) + \frac{Dp}{Dt} + Q$$

**ความหมายของแต่ละเทอม:**
- $\frac{\partial (\rho h)}{\partial t}$: อัตราการเปลี่ยนแปลงพลังงานตามเวลา
- $\nabla  \cdot (\rho \mathbf{u} h)$: การขนส่งพลังงานโดยการไหล (Convection)
- $\nabla  \cdot (k \nabla T)$: การถ่ายเทความร้อนโดยการนำ (Conduction)
- $\frac{Dp}{Dt}$: งานที่เกิดจากการเปลี่ยนแปลงความดัน (Pressure work)
- $Q$: แหล่งกำเนิดความร้อนภายนอก (Heat sources)

---

## 💻 2. การนำไปใช้ใน OpenFOAM (EEqn.H)

ในระดับซอร์สโค้ด สมการพลังงานถูกประกอบขึ้นโดยใช้ Finite Volume Method (FVM):

```cpp
fvScalarMatrix EEqn
(
    fvm::ddt(rho, he) + fvm::div(phi, he)
  - fvm::laplacian(turbulence->alphaEff(), he)
 ==
    reaction->Qdot() + fvOptions(rho, he)
);

EEqn.relax();
EEqn.solve();
```

**ตัวแปรที่สำคัญ:**
- `he`: อาจเป็นพลังงานภายใน ($e$) หรือเอนทาลปี ($h$) ขึ้นอยู่กับการเลือกใน `thermophysicalProperties`
- `alphaEff()`: สัมประสิทธิ์การแพร่ความร้อนที่มีประสิทธิผล ($\alpha_{eff} = \alpha_{molecular} + \alpha_{turbulent}$)

---

## 🌡️ 3. การเชื่อมโยงความร้อนและการไหล

ใน Incompressible Flow (ความหนาแน่นคงที่) สมการพลังงานจะลดรูปเหลือรูปแบบอุณหภูมิที่ง่ายขึ้น:

$$\rho c_p \left( \frac{\partial T}{\partial t} + \mathbf{u} \cdot \nabla T \right) = k \nabla^2 T + Q$$

**ข้อสังเกตเชิงตัวเลข:**
- ความหนืดปั่นป่วน ($\nu_t$) จากโมเดลความปั่นป่วนจะช่วยเพิ่มการแพร่ความร้อนผ่าน **Turbulent Prandtl Number** ($Pr_t$):
  $$\alpha_t = \frac{\nu_t}{Pr_t}$$
- โดยทั่วไป $Pr_t$ สำหรับอากาศมีค่าประมาณ 0.85 - 0.9

---

## 📊 4. จำนวนไร้มิติที่เกี่ยวข้อง (Dimensionless Numbers)

| จำนวน | สูตร | ความหมาย |
|-------|------|----------|
| **Prandtl (Pr)** | $Pr = \frac{\nu}{\alpha} = \frac{\mu c_p}{k}$ | อัตราส่วนการแพร่โมเมนตัมต่อความร้อน |
| **Peclet (Pe)** | $Pe = Re \cdot Pr = \frac{u L}{\alpha}$ | อัตราส่วนการพาความร้อนต่อการนำความร้อน |

---
**หัวข้อถัดไป**: [กลไกการถ่ายเทความร้อน: การนำ การพา และการแผ่รังสี](./02_Heat_Transfer_Mechanisms.md)
