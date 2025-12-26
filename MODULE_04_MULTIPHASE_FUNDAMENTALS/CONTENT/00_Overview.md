# MODULE 04: MULTIPHASE FUNDAMENTALS AND VOF

> "When one fluid is not enough." (เมื่อของไหลชนิดเดียวไม่เพียงพอ)

โมดูลนี้จะนำคุณเข้าสู่โลกของ **Multiphase Flow** ที่ซับซ้อนและน่าตื่นเต้น เราได้ปรับโครงสร้างใหม่ให้เน้น **"การใช้งานจริง" (VOF Method)** เป็นอันดับแรก ก่อนที่จะพาคุณดำดิ่งสู่ทฤษฎี **Eulerian-Eulerian** ขั้นสูง

## 🎯 เส้นทางการเรียนรู้ (Learning Path)

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
