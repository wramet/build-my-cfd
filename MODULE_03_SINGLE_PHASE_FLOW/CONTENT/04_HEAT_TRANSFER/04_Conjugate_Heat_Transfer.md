# การถ่ายเทความร้อนแบบควบคู่ (Conjugate Heat Transfer - CHT)

## 📐 1. แนวคิดพื้นฐาน

**CHT** คือการจำลองการถ่ายเทความร้อนที่มีการโต้ตอบกันระหว่างโดเมน **ของไหล (Fluid)** และ **ของแข็ง (Solid)** โดยความร้อนจะถูกพาโดยการไหลและนำผ่านโครงสร้างของแข็ง

---

## 🔗 2. เงื่อนไขที่อินเทอร์เฟซ (Interface Conditions)

ที่รอยต่อระหว่างของแข็งและของไหล จะต้องรักษาความต่อเนื่องสองประการ:

1. **Temperature Continuity**: $T_{fluid} = T_{solid}$
2. **Heat Flux Continuity**: $k_f \frac{\partial T_f}{\partial n} = k_s \frac{\partial T_s}{\partial n}$

ใน OpenFOAM ใช้ Boundary Condition พิเศษคือ **`turbulentTemperatureCoupledBaffleMixed`** เพื่อบังคับเงื่อนไขเหล่านี้

---

## 🏗️ 3. การนำไปใช้ใน OpenFOAM (Multi-Region)

OpenFOAM ใช้แนวทาง **Multi-region** โดยแบ่งโดเมนออกเป็นส่วนๆ และใช้ Solver **`chtMultiRegionFoam`**

### 3.1 โครงสร้างไฟล์
```bash
case/
├── 0/
│   ├── fluid/ (U, p, T, ...)
│   └── solid/ (T)
├── constant/
│   ├── fluid/ (thermophysicalProperties)
│   ├── solid/ (thermophysicalProperties)
│   └── regionProperties # กำหนดว่าภูมิภาคใดเป็น fluid หรือ solid
└── system/
    ├── fluid/
    └── solid/
```

### 3.2 ตัวอย่าง Boundary Condition ที่ Interface
```cpp
// ภายใน 0/fluid/T
interface_patch
{
    type            compressible::turbulentTemperatureCoupledBaffleMixed;
    Tnbr            T;
    kappaMethod     fluidThermo;
    value           $internalField;
}
```

---

## 📊 4. การประเมินประสิทธิภาพ (Performance Metrics)

- **Overall Heat Transfer Coefficient ($U$)**:
  $$\frac{1}{U} = \frac{1}{h_h} + \frac{t_w}{k_w} + \frac{1}{h_c}$$
- **Effectiveness ($\varepsilon$)**: อัตราส่วนความร้อนที่ถ่ายเทได้จริงต่อค่าสูงสุดทางทฤษฎี

---

## ✅ 5. แนวทางปฏิบัติที่ดีที่สุด (Best Practices)

1. **Consistent Mesh**: แม้ OpenFOAM จะรองรับ Mesh ที่ไม่ตรงกันที่ Interface (AMI) แต่การใช้ Mesh ที่มีจุดตรงกัน (Conformal mesh) จะให้ความแม่นยำและความเสถียรที่สูงกว่า
2. **Thermal Inertia**: พึงระลึกว่าของแข็งมีสเกลเวลาการเปลี่ยนแปลงอุณหภูมิที่ช้ากว่าของไหลมาก ซึ่งอาจส่งผลต่อการลู่เข้าของผลเฉลย

---
**จบเนื้อหาโมดูลการถ่ายเทความร้อน**
