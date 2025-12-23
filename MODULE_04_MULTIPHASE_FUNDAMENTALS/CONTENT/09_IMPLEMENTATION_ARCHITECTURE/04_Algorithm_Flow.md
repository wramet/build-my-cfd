# ขั้นตอนการทำงานของอัลกอริทึม (Algorithm Flow)

## 1. บทนำ (Overview)

`multiphaseEulerFoam` ใช้อัลกอริทึม **PIMPLE** (ซึ่งเป็นการผสมผสานระหว่าง PISO และ SIMPLE) เพื่อจัดการความเชื่อมโยงระหว่างความดันและความเร็ว (Pressure-Velocity Coupling) ในการจำลองการไหลหลายเฟสแบบ Transient อัลกอริทึมนี้รวมข้อดีของ PISO (ความแม่นยำในสภาวะไม่คงตัว) และ SIMPLE (ความเสถียรผ่าน Outer loops และ Under-relaxation) เข้าด้วยกัน

---

## 2. โครงสร้างวงจรคำนวณหลัก (Main Time Loop Structure)

ในแต่ละขั้นตอนเวลา (Time step) อัลกอริทึมจะทำงานตามลำดับดังนี้:

```cpp
while (runTime.loop())
{
    // 1. ปรับก้าวเวลา (Time step) ตามเลข Courant
    #include "compressibleMultiphaseCourantNo.H"

    // PIMPLE Loop (Outer Correctors)
    while (pimple.loop())
    {
        // 2. แก้สมการสัดส่วนเฟส (alphaEqns.H)
        #include "alphaEqns.H"

        // 3. แก้สมการโมเมนตัมของแต่ละเฟส (UEqns.H)
        #include "UEqns.H"

        // 4. แก้สมการความดันร่วม (pEqn.H)
        #include "pEqn.H"

        // 5. แก้สมการพลังงาน (EEqns.H)
        #include "EEqns.H"

        // 6. แก้ไขโมเดลความปั่นป่วน (Turbulence correction)
        forAll(phases, phasei)
        {
            phases[phasei].turbulence().correct();
        }
    }

    // 7. บันทึกผลลัพธ์
    runTime.write();
}
```

---

## 3. สมการสัดส่วนเฟส (Phase Fraction Equations - `alphaEqns.H`)

ใช้ติดตามการกระจายตัวของแต่ละเฟสในปริภูมิและเวลา:

$$\frac{\partial (\alpha_k \rho_k)}{\partial t} + \nabla \cdot (\alpha_k \rho_k \mathbf{u}_k) = \sum_{l=1}^{N} \dot{m}_{lk}$$ 

โดยมีเงื่อนไขบังคับคือ $\sum_{k=1}^{N} \alpha_k = 1$

**การนำไปใช้งานในโค้ด:**
```cpp
forAll(phases, phasei)
{
    phaseModel& phase = phases[phasei];
    volScalarField& alpha = phase;

    fvScalarMatrix alphaEqn
    (
        fvm::ddt(alpha, phase.rho())
      + fvm::div(alphaPhi, phase.rho())
     ==
        phase.massTransferSource()
    );

    alphaEqn.relax();
    alphaEqn.solve();
    alpha.maxMin(1.0, 0.0); // บังคับให้อยู่ในช่วง [0, 1]
}
```

---

## 4. สมการโมเมนตัม (Momentum Equations - `UEqns.H`)

แต่ละเฟสจะมีสมการโมเมนตัมของตัวเองที่เชื่อมโยงกันผ่านแรงระหว่างเฟส (Interphase forces):

$$\frac{\partial (\alpha_k \rho_k \mathbf{u}_k)}{\partial t} + \nabla \cdot (\alpha_k \rho_k \mathbf{u}_k \mathbf{u}_k) = -\alpha_k \nabla p + \nabla \cdot \boldsymbol{\tau}_k + \alpha_k \rho_k \mathbf{g} + \mathbf{M}_k$$ 

**เทอมการถ่ายโอนโมเมนตัมระหว่างเฟส ($\\mathbf{M}_k$):**
ประกอบด้วยแรง Drag, Lift, Virtual Mass และ Turbulent Dispersion:
$$\\mathbf{M}_k = \sum_{l=1}^{N} (\mathbf{F}^{D}_{kl} + \mathbf{F}^{L}_{kl} + \mathbf{F}^{VM}_{kl} + \mathbf{F}^{TD}_{kl})$$ 

---

## 5. สมการความดัน (Pressure Equation - `pEqn.H`)

สมการความดันทำหน้าที่รักษาการอนุรักษ์มวลโดยบังคับให้ฟิลด์ความเร็วของส่วนผสมเป็น Divergence-free:

$$\sum_{k=1}^{N} \nabla \cdot (\alpha_k \rho_k \mathbf{u}_k) = 0$$ 

**ขั้นตอนของอัลกอริทึม PISO:**
1. **Predictor Step**: แก้สมการโมเมนตัมด้วยความดันปัจจุบัน เพื่อหาความเร็วชั่วคราว ($\\mathbf{u}^*$)
2. **Pressure Solution**: แก้สมการ Poisson เพื่อหาค่าความดันใหม่
3. **Velocity Correction**: ปรับปรุงค่าความเร็วโดยใช้ Gradient ของความดันใหม่:
   $$\\mathbf{u}_k^{n+1} = \\mathbf{u}_k^* - \frac{1}{A_k} \nabla p$$ 

---

## 6. สมการพลังงาน (Energy Equations - `EEqns.H`)

คำนวณการถ่ายเทความร้อนจากการพา (Convection), การนำ (Conduction) และการแลกเปลี่ยนความร้อนระหว่างเฟส:

$$\frac{\partial (\alpha_k \rho_k h_k)}{\partial t} + \nabla \cdot (\alpha_k \rho_k h_k \mathbf{u}_k) = \alpha_k \frac{D p_k}{D t} + \nabla \cdot (\alpha_k k_k \nabla T_k) + Q_{k}$$ 

โดยที่ $Q_k$ คือการถ่ายเทความร้อนระหว่างเฟส: $Q_k = \sum_{l=1}^{N} h_{kl} A_{kl} (T_l - T_k)$ 

---

## 7. กลยุทธ์ความเสถียร (Stability Strategies)

### 7.1 การคำนวณเลข Courant (Courant Number)
$$\\text{Co} = \frac{\\Delta t \cdot |\mathbf{u}|}{\\Delta x}$$ 
ระบบจะปรับ $\\Delta t$ อัตโนมัติเพื่อให้ $\\text{Co}$ อยู่ในเกณฑ์ที่กำหนดเพื่อความเสถียร

### 7.2 การผ่อนคลาย (Under-Relaxation)
ใช้เพื่อป้องกันการแกว่งของค่าในการคำนวณแบบ Iterative:
$$\\phi^{new} = \\phi^{old} + \lambda_{relax}(\\phi^{calculated} - \\phi^{old})$$ 

| ฟิลด์ (Field) | ค่า $\\lambda$ ที่แนะนำ |
|-------|------------------|
| **Phase fractions** | 0.7 - 0.9 |
| **Momentum (U)** | 0.6 - 0.8 |
| **Pressure (p)** | 0.2 - 0.5 |
| **Energy (h/T)** | 0.8 - 0.95 |

---

## 8. สรุปขั้นตอนการทำงาน (Summary)

`multiphaseEulerFoam` ใช้แนวทางการแก้ปัญหาแบบ **Segregated Approach** (แก้ทีละสมการตามลำดับ) ซึ่งมีข้อดีคือใช้หน่วยความจำน้อยและมีความยืดหยุ่นสูงในการจัดการฟิสิกส์ที่ซับซ้อน โดยมีการใช้เทคนิค **Implicit Treatment** สำหรับเทอมแรงระหว่างเฟสเพื่อเพิ่มความเสถียรในระบบที่มีแรง Drag สูง

*อ้างอิง: วิเคราะห์ตามซอร์สโค้ด OpenFOAM-10 multiphaseEulerFoam.C, pEqn.H และ UEqns.H*