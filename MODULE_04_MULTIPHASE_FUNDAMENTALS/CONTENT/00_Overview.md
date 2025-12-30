# MODULE 04: MULTIPHASE FUNDAMENTALS AND VOF

> [!TIP]
> **ทำไมการทำความเข้าใจ Multiphase Flow ถึงสำคัญใน OpenFOAM?**
>
> การจำลองการไหลแบบหลายเฟส (Multiphase Flow) เพิ่มความซับซ้อนจาก Single Phase ระดับที่สูงขึ้น ซึ่งส่งผลโดยตรงต่อ:
> - **เสถียรภาพของการคำนวณ (Numerical Stability)**: การมีหลายเฟสที่มีคุณสมบัติต่างกัน (Density/Viscosity ratios) ทำให้เกิดปัญหา Convergence ยากขึ้น
> - **การเลือก Solver ที่เหมาะสม**: แต่ละ Approach (VOF vs Eulerian-Eulerian) ถูกออกแบบมาสำหรับ Flow Regime ที่แตกต่างกัน
> - **ความถูกต้องของผลลัพธ์ (Physical Accuracy)**: การจำลองผิวต่อ (Interface) และแรงระหว่างเฟส (Interfacial forces) ต้องมีความแม่นยำสูง
>
> **หัวใจสำคัญ**: Multiphase Flow ไม่ใช่แค่ "เพิ่มของไหลอีกชนิด" แต่เป็นการเปลี่ยนแนวทางการคิดจาก "ของไหลเดียว" ไปเป็น "ระบบของเฟสที่โต้ตอบกัน"

> "When one fluid is not enough."

---

## 🎯 Learning Objectives

หลังจากผ่านโมดูลนี้ คุณจะสามารถ:

- **แยกแยะ Flow Regimes** ได้อย่างถูกต้องว่าควรใช้ VOF หรือ Eulerian-Eulerian Approach
- **เลือก Solver ที่เหมาะสม** จาก OpenFOAM Solver family (`interFoam`, `multiphaseInterFoam`, `twoPhaseEulerFoam`, etc.)
- **ตั้งค่า Property Files** ได้อย่างถูกต้อง (`constant/transportProperties`, `constant/phaseProperties`)
- **กำหนด Initial Conditions** สำหรับ Volume fraction fields (`alpha.water`, `alpha.air`) ในไดเรกทอรี `0/`
- **เลือก Numerical Schemes** ที่เหมาะสมสำหรับการจำลอง Interface ใน `system/fvSchemes`
- **ตั้งค่า Solver Controls** สำหรับเสถียรภาพการคำนวณ Multiphase ใน `system/fvSolution`

---

## 🎯 เส้นทางการเรียนรู้ (Learning Path)

> [!NOTE]
> **📂 OpenFOAM Solver Selection Guide**
>
> การเลือกเส้นทางการเรียนรู้ (VOF vs Eulerian-Eulerian) มีผลโดยตรงต่อ:
> - **Solver Selection**: `interFoam` (2-phase VOF), `multiphaseInterFoam` (multi-phase VOF), `twoPhaseEulerFoam` (2-phase Eulerian), `multiphaseEulerFoam` (multi-phase Eulerian)
> - **Property Files**: VOF ใช้ `constant/transportProperties` หรือ `constant/phaseProperties`; Eulerian ใช้ `constant/phaseProperties` พร้อมรายละเอียดแต่ละเฟส
> - **Initial Conditions**: กำหนด Volume fraction (`alpha.water`, `alpha.air`) ในไดเรกทอรี `0/`

### 🌊 Level 1: Volume of Fluid (VOF) Basics

เหมาะสำหรับงาน: Free surface flows, Dam breaks, Tank sloshing, Ship hulls

- **01_MULTIPHASE_CONCEPTS**: รู้จัก Flow Regimes (Dispersed vs Separated)
- **02_VOF_METHOD**: เจาะลึก `interFoam`, การจับผิว (Surface Capturing), และการตั้งค่า `setFields`

### 🏭 Level 2: Eulerian-Eulerian (Two-Fluid Model)

เหมาะสำหรับงาน: Bubble columns, Fluidized beds, Sedimentation

- **03_EULER_EULER_METHOD**: ทฤษฎี Interpenetrating Continua (เมื่อน้ำและอากาศอยู่ทับที่กันได้)
- **04_INTERPHASE_FORCES**: รวมมิตรแรงกระทำ (Drag, Lift, Virtual Mass)
- **05_MODEL_SELECTION**: วิธีเลือกโมเดลให้เหมาะกับงาน

### 🛠 Level 3: Advanced Topics

- **06_IMPLEMENTATION**: โครงสร้างโค้ด OpenFOAM สำหรับ Multiphase
- **07_VALIDATION**: เคสตัวอย่างเพื่อตรวจสอบความถูกต้อง

> [!NOTE]
> เราแนะนำให้คุณเริ่มจาก **02_VOF_METHOD** หากคุณเพิ่มเริ่มทำ Multiphase เพราะเข้าใจง่ายกว่าและเห็นภาพชัดเจน (Visual) มากกว่า Eulerian Model ที่เป็นเชิงสถิติ

---

## 🧠 Concept Check: ทดสอบความเข้าใจ

> [!NOTE]
> **📂 OpenFOAM Implementation Context**
>
> แนวคิดที่คุณทำความเข้าใจในส่วนนี้จะถูกนำไปใช้ในการตั้งค่า OpenFOAM Case:
> - **VOF**: ใช้ `interFoam`, ตั้งค่า `sigma` ใน `constant/transportProperties`, กำหนด `alpha` ด้วย `setFields` ในไดเรกทอรี `0/`
> - **Numerical Schemes** (`system/fvSchemes`): ใช้ `Gauss vanLeer` หรือ `Gauss linearUpwind` สำหรับ convection ของ `alpha`
> - **Solver Controls** (`system/fvSolution`): ใช้ `MULES` สำหรับการจำลอง Interface และปรับ `nAlphaSubCycles` สำหรับเสถียรภาพ

**1. VOF (Volume of Fluid) เหมาะกับงานประเภทไหนมากที่สุด?**

<details>
<summary>เฉลย</summary>
เหมาะสำหรับงานที่ต้องการติดตาม **รอยต่อระหว่างเฟส (Interface) ที่ชัดเจน** เช่น น้ำกับอากาศ ในกรณี Free surface, Dam break, หรือการไหลในรางเปิด
</details>

**2. Eulerian-Eulerian Approach แตกต่างจาก VOF อย่างไร?**

<details>
<summary>เฉลย</summary>
VOF ใช้กริดเดียวแก้สมการชุดเดียว (One-fluid formulation) และใช้ตัวแปร $\alpha$ แยกเฟสเหมาะกับเฟสแยกตัวชัดเจน ส่วน Eulerian-Eulerian (Two-fluid model) มองว่าทุกเฟสเป็นของไหลต่อเนื่องที่ซ้อนทับกัน (Interpenetrating continua) แก้สมการแยกแต่ละเฟส เหมาะกับเฟสผสม เช่น ฟองอากาศในน้ำ (Dispersed flow)
</details>

**3. ทำไมการจำลอง Multiphase ถึงยากกว่า Single Phase?**

<details>
<summary>เฉลย</summary>
เพราะมีความซับซ้อนเพิ่มขึ้นจาก **Interfacial Interactions** (แรงระหว่างผิวสัมผัส) ต้องแก้สมการเพิ่มเพื่อติดตามสัดส่วนของเฟส ($\alpha$) และต้องจัดการกับความไม่ต่อเนื่องของคุณสมบัติ (Density/Viscosity jump) ที่รอยต่อ
</details>

---

## 📝 Key Takeaways

✅ **Multiphase Flow คือระบบของเฟสที่โต้ตอบกัน** ไม่ใช่แค่เพิ่มของไหลอีกชนิด

✅ **VOF Method** เหมาะสำหรับ Free surface flows ที่มี Interface ชัดเจน ใช้ `interFoam` และตั้งค่าใน `constant/transportProperties`

✅ **Eulerian-Eulerian Method** เหมาะสำหรับ Dispersed flows เช่น ฟองอากาศในน้ำ ใช้ `twoPhaseEulerFoam` และตั้งค่าใน `constant/phaseProperties`

✅ **Numerical Stability** เป็นความท้าทายหลัก เนื่องจาก Density/Viscosity ratios และ Interface tracking

✅ **การเลือก Solver ที่เหมาะสม** เริ่มจากการจำแนก Flow Regime ก่อนเสมอ

---

## 🔗 Prerequisites

- ความเข้าใจพื้นฐาน **CFD Fundamentals** (MODULE_01)
- ความเข้าใจ **Single Phase Flow Solvers** (MODULE_03)
- ความเข้าใจ **Meshing Fundamentals** (MODULE_02)

## ➡️ Next Steps

เริ่มต้นจาก: **[01_MULTIPHASE_CONCEPTS/00_Overview.md](01_FUNDAMENTAL_CONCEPTS/00_Overview.md)**

---

## 📖 เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า**: [../../MODULE_03_SINGLE_PHASE_FLOW/CONTENT/07_ADVANCED_TOPICS/04_Multiphysics.md](../../MODULE_03_SINGLE_PHASE_FLOW/CONTENT/07_ADVANCED_TOPICS/04_Multiphysics.md)
- **บทถัดไป**: [01_FUNDAMENTAL_CONCEPTS/00_Overview.md](01_FUNDAMENTAL_CONCEPTS/00_Overview.md)