# MODULE 04: MULTIPHASE FUNDAMENTALS AND VOF

> [!TIP]
> **ทำไมการทำความเข้าใจ Multiphase Flow ถึงสำคัญใน OpenFOAM?**
>
> การจำลองการไหลแบบหลายเฟส (Multiphase Flow) เป็นการเพิ่มความซับซ้อนของปัญหาจาก Single Phase ไปสู่ระดับที่สูงขึ้น ซึ่งส่งผลโดยตรงต่อ:
> - **เสถียรภาพของการคำนวณ (Numerical Stability)**: การมีหลายเฟสที่มีคุณสมบัติต่างกัน (Density/Viscosity ratios) ทำให้เกิดปัญหา Convergence ยากขึ้น
> - **การเลือก Solver ที่เหมาะสม**: แต่ละ Approach (VOF vs Eulerian-Eulerian) ถูกออกแบบมาสำหรับ Flow Regime ที่แตกต่างกัน การเลือกผิดจะทำให้ผลลัพธ์ไม่ถูกต้องหรือใช้เวลาคำนวณนานเกินไป
> - **ความถูกต้องของผลลัพธ์ (Physical Accuracy)**: การจำลองผิวต่อ (Interface) และแรงระหว่างเฟส (Interfacial forces) ต้องมีความแม่นยำสูง เพื่อให้ได้ผลลัพธ์ที่เชื่อถือได้
>
> การเข้าใจหลักการของแต่ละวิธีจะช่วยให้คุณ:
> - ตั้งค่า `constant/phaseProperties` หรือ `constant/transportProperties` ได้อย่างถูกต้อง
> - เลือก Solver ที่เหมาะสม เช่น `interFoam`, `multiphaseInterFoam`, หรือ `twoPhaseEulerFoam`
> - ตั้งค่า Numerical Schemes ใน `system/fvSchemes` สำหรับการจำลอง Interface
> - ควบคุมเวลาคำนวณ (Time stepping) ให้เหมาะสมกับปัญหา Multiphase
>
> **หัวใจสำคัญ**: Multiphase Flow ไม่ใช่แค่ "เพิ่มของไหลอีกชนิด" แต่เป็นการเปลี่ยนแนวทางการคิดจาก "ของไหลเดียว" ไปเป็น "ระบบของเฟสที่โต้ตอบกัน" ซึ่งต้องการความเข้าใจทั้งด้านฟิสิกส์และ Numerical Methods

> "When one fluid is not enough." (เมื่อของไหลชนิดเดียวไม่เพียงพอ)

โมดูลนี้จะนำคุณเข้าสู่โลกของ **Multiphase Flow** ที่ซับซ้อนและน่าตื่นเต้น เราได้ปรับโครงสร้างใหม่ให้เน้น **"การใช้งานจริง" (VOF Method)** เป็นอันดับแรก ก่อนที่จะพาคุณดำดิ่งสู่ทฤษฎี **Eulerian-Eulerian** ขั้นสูง

## 🎯 เส้นทางการเรียนรู้ (Learning Path)

> [!NOTE]
> **📂 OpenFOAM Context**
>
> ใน OpenFOAM การเลือกเส้นทางการเรียนรู้ (VOF vs Eulerian-Eulerian) มีผลโดยตรงต่อ:
> - **Solver Selection**: การเลือก Solver ที่เหมาะสมกับปัญหา เช่น:
>   - `interFoam` สำหรับ 2 เฟสใช้ VOF method
>   - `multiphaseInterFoam` สำหรับหลายเฟส (หลายกว่า 2 เฟส)
>   - `twoPhaseEulerFoam` สำหรับ 2 เฟสใช้ Eulerian-Eulerian approach
>   - `multiphaseEulerFoam` สำหรับหลายเฟสแบบ Eulerian
>
> - **Property Files**: แต่ละ Solver จะมีการตั้งค่าที่แตกต่างกัน:
>   - VOF: ตั้งค่าใน `constant/transportProperties` หรือ `constant/phaseProperties` (สำหรับ multiphaseInterFoam)
>   - Eulerian: ตั้งค่าใน `constant/phaseProperties` พร้อมรายละเอียดของแต่ละเฟส
>
> - **Initial Conditions**: การกำหนดค่าเริ่มต้นของ Volume fraction (`alpha.water`, `alpha.air`) ในไดเรกทอรี `0/`
>
> การเข้าใจเส้นทางการเรียนรู้จะช่วยให้คุณเลือก Solver และตั้งค่า Case ได้อย่างถูกต้องตั้งแต่เริ่มต้น

### 🌊 Level 1: Volume of Fluid (VOF) Basics
เหมาะสำหรับงาน: Free surface flows, Dam breaks, Tank sloshing, Ship hulls
*   **01_MULTIPHASE_CONCEPTS**: รู้จัก Flow Regimes (Dispersed vs Separated)
*   **02_VOF_METHOD**: เจาะลึก `interFoam`, การจับผิว (Surface Capturing), และการตั้งค่า `setFields`

### 🏭 Level 2: Eulerian-Eulerian (Two-Fluid Model)
เหมาะสำหรับงาน: Bubble columns, Fluidized beds, Sedimentation
*   **03_EULER_EULER_METHOD**: ทฤษฎี Interpenetrating Continua (เมื่อน้ำและอากาศอยู่ทับที่กันได้)
*   **04_INTERPHASE_FORCES**: รวมมิตรแรงกระทำ (Drag, Lift, Virtual Mass)
*   **05_MODEL_SELECTION**: วิธีเลือกโมเดลให้เหมาะกับงาน

### 🛠 Level 3: Advanced Topics
*   **06_IMPLEMENTATION**: โครงสร้างโค้ด OpenFOAM สำหรับ Multiphase
*   **07_VALIDATION**: เคสตัวอย่างเพื่อตรวจสอบความถูกต้อง

---

> [!NOTE]
> เราแนะนำให้คุณเริ่มจาก **02_VOF_METHOD** หากคุณเพิ่งเริ่มทำ Multiphase เพราะเข้าใจง่ายกว่าและเห็นภาพชัดเจน (Visual) มากกว่า Eulerian Model ที่เป็นเชิงสถิติ

---

## 🧠 Concept Check: ทดสอบความเข้าใจ

> [!NOTE]
> **📂 OpenFOAM Context**
>
> แนวคิดที่คุณทำความเข้าใจในส่วนนี้จะถูกนำไปใช้ในการตั้งค่า OpenFOAM Case ดังนี้:
>
> - **Question 1: VOF สำหรับ Free Surface**:
>   - ใช้ Solver: `interFoam`, `multiphaseInterFoam`
>   - ตั้งค่า Interface properties ใน `constant/transportProperties` (เช่น `sigma` - Surface tension coefficient)
>   - กำหนดค่าเริ่มต้นของ `alpha` (Volume fraction) ในไดเรกทอรี `0/` โดยใช้ `setFields` หรือ `funkySetFields`
>
> - **Question 2: Eulerian-Eulerian vs VOF**:
>   - VOF: ใช้ Field เดียว (`alpha`) แทนการแยกเฟส, Interface ถูก Capture โดย MULES scheme
>   - Eulerian: ใช้ Multiple Fields (หนึ่ง Field ต่อหนึ่งเฟส) และตั้งค่า Interphase forces ใน `constant/phaseProperties`
>
> - **Question 3: ความยากของ Multiphase**:
>   - ตั้งค่า Numerical Schemes ใน `system/fvSchemes`:
>     - `divSchemes`: ใช้ `Gauss vanLeer` หรือ `Gauss linearUpwind` สำหรับ convection ของ `alpha`
>     - `laplacianSchemes`: ต้องระมัดระวังเมื่อ Density/Viscosity แตกต่างกันมาก
>   - ตั้งค่า Solver controls ใน `system/fvSolution`:
>     - ใช้ `MULES` สำหรับการจำลอง Interface ของ `alpha`
>     - ปรับค่า `nAlphaSubCycles` สำหรับเสถียรภาพ
>
> การทำความเข้าใจแนวคิดเหล่านี้จะช่วยให้คุณตั้งค่า OpenFOAM Case ได้อย่างถูกต้องและเข้าใจว่าทำไมต้องตั้งค่าแต่ละอย่าง

1.  **VOF (Volume of Fluid) เหมาะกับงานประเภทไหนมากที่สุด?**
    <details>
    <summary>เฉลย</summary>
    เหมาะสำหรับงานที่ต้องการติดตาม **รอยต่อระหว่างเฟส (Interface) ที่ชัดเจน** เช่น น้ำกับอากาศ ในกรณี Free surface, Dam break, หรือการไหลในรางเปิด
    </details>

2.  **Eulerian-Eulerian Approach แตกต่างจาก VOF อย่างไร?**
    <details>
    <summary>เฉลย</summary>
    VOF ใช้กริดเดียวแก้สมการชุดเดียว (One-fluid formulation) และใช้ตัวแปร $\alpha$ แยกเฟสเหมาะกับเฟสแยกตัวชัดเจน ส่วน Eulerian-Eulerian (Two-fluid model) มองว่าทุกเฟสเป็นของไหลต่อเนื่องที่ซ้อนทับกัน (Interpenetrating continua) แก้สมการแยกแต่ละเฟส เหมาะกับเฟสผสม เช่น ฟองอากาศในน้ำ (Dispersed flow)
    </details>

3.  **ทำไมการจำลอง Multiphase ถึงยากกว่า Single Phase?**
    <details>
    <summary>เฉลย</summary>
    เพราะมีความซับซ้อนเพิ่มขึ้นจาก **Interfacial Interactions** (แรงระหว่างผิวสัมผัส) ต้องแก้สมการเพิ่มเพื่อติดตามสัดส่วนของเฟส ($\alpha$) และต้องจัดการกับความไม่ต่อเนื่องของคุณสมบัติ (Density/Viscosity jump) ที่รอยต่อ
    </details>

---

## 📖 เอกสารที่เกี่ยวข้อง

*   **บทก่อนหน้า**: [../../MODULE_03_SINGLE_PHASE_FLOW/CONTENT/07_ADVANCED_TOPICS/04_Multiphysics.md](../../MODULE_03_SINGLE_PHASE_FLOW/CONTENT/07_ADVANCED_TOPICS/04_Multiphysics.md)
*   **บทถัดไป**: [01_FUNDAMENTAL_CONCEPTS/00_Overview.md](01_FUNDAMENTAL_CONCEPTS/00_Overview.md)
