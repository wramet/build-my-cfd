# อัลกอริทึม PISO และ PIMPLE: อัลกอริทึมสำหรับการไหลแบบชั่วคร่าว (Transient)

## 📖 บทนำ (Introduction)

สำหรับการไหลที่ขึ้นกับเวลา (**Transient flow**) OpenFOAM นำเสนอสองอัลกอริทึมหลัก ได้แก่ **PISO** สำหรับความแม่นยำสูงเมื่อก้าวเวลาเล็ก และ **PIMPLE** สำหรับความแข็งแกร่งเมื่อก้าวเวลาใหญ่

---

## 🎯 1. อัลกอริทึม PISO (Pressure-Implicit with Splitting of Operators)

PISO ถูกพัฒนาโดย Issa (1986) เพื่อรักษาความแม่นยำเชิงเวลา (Temporal Accuracy) โดยไม่ต้องใช้ Under-relaxation

### 1.1 ขั้นตอนการทำงาน (PISO Workflow)
1. **Momentum Predictor**: แก้สมการโมเมนตัมด้วยความดันจาก Time-step ก่อนหน้า ($p^n$)
2. **PISO Corrector Loop** (ทำซ้ำ $n$ รอบตาม `nCorrectors`):
   - แก้สมการความดัน (Pressure Equation)
   - อัปเดตสนามความเร็วและ Flux
   - รักษาความต่อเนื่อง (Mass conservation)

### 1.2 OpenFOAM Configuration (`system/fvSolution`)
```cpp
PISO
{
    nCorrectors          2;    // จำนวนรอบการแก้ไขความดัน (แนะนำ 2-3)
    nNonOrthogonalCorrectors 0; // รอบการแก้สำหรับ mesh ที่ไม่ตั้งฉาก
    pRefCell             0;
    pRefValue            0;
}
```

---

## 🔀 2. อัลกอริทึม PIMPLE (Merged PISO-SIMPLE)

PIMPLE รวมความสามารถของ **SIMPLE** (สำหรับการวนซ้ำภายนอกพร้อม Relaxation) และ **PISO** (สำหรับการวนซ้ำภายในเพื่อความแม่นยำ)

### 2.1 จุดเด่นของ PIMPLE
- **Large Time Steps**: สามารถรันที่ค่า Courant number ($Co$) มากกว่า 1 ได้อย่างเสถียร
- **Robustness**: เหมาะกับปัญหาที่มีความไม่เป็นเชิงเส้นสูง (High non-linearity) เช่น Mesh เคลื่อนที่ หรือ Multiphase flow

### 2.2 โครงสร้างลูปของ PIMPLE
```cpp
while (runTime.loop())
{
    // Outer Correctors (SIMPLE loops)
    for (int oCorr=0; oCorr<nOuterCorr; oCorr++)
    {
        // 1. Solve Momentum (UEqn.H)
        // 2. Solve Pressure Inner Loop (pEqn.H)
        for (int corr=0; corr<nCorr; corr++)
        {
            // Solve p equation
        }
    }
}
```

### 2.3 Configuration ใน OpenFOAM
```cpp
PIMPLE
{
    nOuterCorrectors    2;     // จำนวนรอบ SIMPLE (Outer loop)
    nCorrectors         2;     // จำนวนรอบ PISO (Inner loop)
    nNonOrthogonalCorrectors 0;
    adjustTimeStep      yes;   // ปรับก้าวเวลาอัตโนมัติอิงตาม maxCo
    maxCo               2.0;   // อนุญาตให้ Co > 1
}
```

---

## 📊 3. ตารางเปรียบเทียบ PISO vs PIMPLE

| คุณสมบัติ | PISO | PIMPLE |
|-----------|------|--------|
| **ก้าวเวลา ($\Delta t$)** | ต้องเล็ก ($Co < 1$) | ใหญ่ได้ ($Co > 1$) |
| **Relaxation** | ไม่แนะนำ | จำเป็นใน Outer loop |
| **ต้นทุนการคำนวณ** | ต่ำต่อ Time-step | สูงต่อ Time-step (แต่ก้าวเวลาใหญ่กว่า) |
| **ความเหมาะสม** | LES, DNS, Aeroacoustics | อุตสาหกรรม, Moving Mesh, VOF |

---

## 🛠️ 4. แนวทางปฏิบัติที่ดีที่สุด (Best Practices)

1. **สำหรับ PISO**: ต้องระวังไม่ให้ค่า $Co$ เกิน 1.0 เสมอ มิฉะนั้นความคลาดเคลื่อนเชิงเวลาจะเพิ่มขึ้นอย่างรวดเร็ว
2. **สำหรับ PIMPLE**: หากต้องการผลเฉลยที่แม่นยำเชิงเวลาสูง (เช่น Vortex Shedding) ให้ลด `nOuterCorrectors` เหลือ 1 และรักษา $Co < 1$ (ซึ่งจะทำให้มันทำงานเหมือน PISO)
3. **Residual Control**: ใน PIMPLE สามารถใช้ `residualControl` ในลูปภายนอกเพื่อหยุดการวนซ้ำเมื่อคำตอบลู่เข้าก่อนถึงจำนวน `nOuterCorrectors` ที่ตั้งไว้

---
**หัวข้อถัดไป**: [การประมาณค่าแบบ Rhie-Chow Interpolation](./04_Rhie_Chow_Interpolation.md)
