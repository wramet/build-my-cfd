# การถ่ายเทความร้อนใน OpenFOAM: คู่มือการจำลองความร้อนเบื้องต้นถึงขั้นสูง

## 🔍 ภาพรวม (Overview)

การถ่ายเทความร้อนเป็นหัวใจสำคัญของการประยุกต์ใช้งานทางวิศวกรรม ตั้งแต่การระบายความร้อนอิเล็กทรอนิกส์ไปจนถึงการออกแบบหม้อน้ำในโรงไฟฟ้า โมดูลนี้ครอบคลุมการนำสมการพลังงานไปใช้งานใน OpenFOAM เพื่อจำลองกลไกการนำ การพา และการแผ่รังสี

---

## 🎯 วัตถุประสงค์การเรียนรู้ (Learning Objectives)

เมื่อจบโมดูลนี้ คุณจะสามารถ:
1. **ตั้งค่าการจำลองความร้อน**: เข้าใจการนำสมการพลังงาน (Energy Equation) ไปใช้ใน OpenFOAM
2. **กำหนดคุณสมบัติทางเทอร์โมฟิสิกส์**: เลือกแบบจำลอง `thermophysicalProperties` ที่เหมาะสม (เช่น Constant, Sutherland, Polynomial)
3. **จัดการเงื่อนไขขอบเขต**: ใช้ Boundary Conditions สำหรับอุณหภูมิและฟลักซ์ความร้อนได้อย่างถูกต้อง
4. **จำลองแรงลอยตัว**: ใช้การประมาณแบบ Boussinesq สำหรับการพาความร้อนตามธรรมชาติ
5. **จำลองการถ่ายเทความร้อนแบบควบคู่ (CHT)**: เชื่อมโยงการไหลของของไหลกับการนำความร้อนในของแข็ง

---

## 🔥 1. กลไกการถ่ายเทความร้อน (Heat Transfer Mechanisms)

OpenFOAM จัดการกลไกพื้นฐานสามรูปแบบดังนี้:

| กลไก | กฎทางกายภาพ | การนำไปใช้ใน OpenFOAM |
|------|------------|-----------------------|
| **การนำ (Conduction)** | กฎของฟูเรียร์: $\mathbf{q} = -k \nabla T$ | ตัวดำเนินการ `fvm::laplacian` |
| **การพา (Convection)** | การพาพลังงาน: $\nabla \cdot (\rho \mathbf{u} h)$ | ตัวดำเนินการ `fvm::div` ในสมการเอนทาลปี |
| **การแผ่รังสี (Radiation)** | $q \propto T^4$ | แบบจำลอง P-1 หรือ fvDOM |

---

## 🏗️ 2. สมการพลังงาน (Energy Equation)

ใน OpenFOAM สมการพลังงานมักจะถูกแก้ในรูปของ **เอนทาลปี ($h$)** หรือ **พลังงานภายใน ($e$)**:

$$\frac{\partial (\rho h)}{\partial t} + \nabla \cdot (\rho \mathbf{u} h) = \nabla \cdot (\alpha_{eff} \nabla h) + \frac{Dp}{Dt} + Q$$ 

โดยที่ $\alpha_{eff}$ คือค่าการแพร่ความร้อนประสิทธิผล (Thermal Diffusivity) ที่รวมผลของความปั่นป่วน

---

## 🌡️ 3. แบบจำลองเทอร์โมฟิสิกส์ (Thermophysical Models)

ไฟล์ `constant/thermophysicalProperties` ควบคุมการคำนวณคุณสมบัติของของไหล:
```cpp
thermoType
{
    type            heRhoThermo;
    mixture         pureMixture;
    transport       sutherland;
    thermo          hConst;
    equationOfState perfectGas;
    specie          specie;
    energy          sensibleEnthalpy;
}
```

---

## 🚀 4. Solvers ที่สำคัญ

- **`buoyantBoussinesqSimpleFoam`**: สำหรับการไหลแบบอัดตัวไม่ได้ที่ขับเคลื่อนด้วยแรงลอยตัวเล็กน้อย
- **`buoyantSimpleFoam`**: สำหรับการไหลแบบอัดตัวได้สภาวะคงที่
- **`chtMultiRegionFoam`**: สำหรับปัญหาที่ต้องแก้ความร้อนในของไหลและของแข็งพร้อมกัน (Conjugate Heat Transfer)

---

## ⏱️ ระยะเวลาเรียนโดยประมาณ
- **ภาคทฤษฎี**: 2-3 ชั่วโมง (พื้นฐานสมการและการระบุคุณสมบัติ)
- **ภาคปฏิบัติ**: 2-3 ชั่วโมง (Case Setup: Cavity natural convection, CHT pipe)
- **รวม**: 4-6 ชั่วโมง

---
**หัวข้อถัดไป**: [พื้นฐานสมการพลังงาน](./01_Energy_Equation_Fundamentals.md)