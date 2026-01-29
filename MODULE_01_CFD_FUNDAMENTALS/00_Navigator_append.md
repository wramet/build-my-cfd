
---

## 5. OpenFOAM Implementation (การนำไปใช้ OpenFOAM) ⭐ NEW

> [!NOTE] 📂 OpenFOAM Context
> **Domain:** Coding/Customization + Solver Architecture
>
> หัวข้อนี้เป็น **สะพานเชื่อม** ระหว่างทฤษฎี CFD และการ implement ใน OpenFOAM:
> - **Solver Anatomy:** โครงสร้างภายในของ OpenFOAM solver
> - **Source Code Mapping:** การแปลงสมการให้เป็น C++ code
> - **Code Tracing:** การติดตามการทำงานของ solver ทีละขั้นตอน

### 📖 Content → 🔧 Source Code Mapping

| 📖 เนื้อหา | 📝 คำอธิบาย | 🔧 Source Code ที่เกี่ยวข้อง |
|-----------|------------|---------------------------|
| [[03_OPENFOAM_IMPLEMENTATION/01_Solver_Anatomy]] | กายวิภาค solver | `src/incompressible/simpleFoam/simpleFoam.C` |
| [[03_OPENFOAM_IMPLEMENTATION/02_Source_Code_Mapping]] | แม็พสมการไปยังโค้ด | `src/finiteVolume/` |
| [[03_OPENFOAM_IMPLEMENTATION/03_First_Simulation]] | ติดตามการทำงาน | `tutorials/incompressible/icoFoam/cavity/` |

### 🎯 Study Guide

| ขั้นตอน | กิจกรรม | เวลาโดยประมาณ |
|--------|---------|--------------|
| 1 | อ่าน `01_Solver_Anatomy` | 45 นาที |
| 2 | ศึกษา `simpleFoam.C` | 30 นาที |
| 3 | ทำความเข้าใจ code-to-math | 60 นาที |
| 4 | รัน cavity tutorial | 45 นาที |

---

## 6. Design Principles (หลักการออกแบบ) ⭐ NEW

> [!NOTE] 📂 OpenFOAM Context
> **Domain:** Software Architecture + Modern C++
>
> หัวข้อนี้สอน **หลักการออกแบบซอฟต์แวร์** สำหรับ CFD codes:
> - **Class Design:** Encapsulation, SRP สำหรับ CFD objects
> - **Modern C++:** Smart pointers, RAII, const correctness
> - **Architecture:** Layered architecture สำหรับ CFD solvers
> - **R410A Application:** ออกแบบ custom solver สำหรับ R410A

### 📖 Content → 🔧 Source Code Mapping

| 📖 เนื้อหา | 📝 คำอธิบาย | 🔧 Source Code ที่เกี่ยวข้อง |
|-----------|------------|---------------------------|
| [[04_DESIGN_PRINCIPLES/01_Class_Design_Basics]] | OOP สำหรับ CFD | `src/OpenFOAM/fields/GeometricFields/` |
| [[04_DESIGN_PRINCIPLES/02_Modern_CPP_Intro]] | Modern C++ features | `src/OpenFOAM/memory/autoPtr.H` |
| [[04_DESIGN_PRINCIPLES/03_Architecture_Overview]] | Solver architecture | `src/finiteVolume/` |

### 🎯 Study Guide

| ขั้นตอน | กิจกรรม | เวลาโดยประมาณ |
|--------|---------|--------------|
| 1 | อ่าน `01_Class_Design_Basics` | 45 นาที |
| 2 | ศึกษา smart pointers | 30 นาที |
| 3 | วิเคราะห์ R410A architecture | 60 นาที |
| 4 | ออกแบบ custom class | 45 นาที |

