# 🚀 Module 06: Advanced Physics (ฟิสิกส์ขั้นสูง)

ยินดีต้อนรับสู่โมดูลฟิสิกส์ขั้นสูง! ในโมดูลนี้ เราจะก้าวข้ามขีดจำกัดของการจำลอง CFD พื้นฐาน ไปสู่การจำลองปรากฏการณ์ที่ซับซ้อนและสมจริงยิ่งขึ้น ซึ่งเป็นหัวใจสำคัญของวิศวกรรมขั้นสูงในปัจจุบัน

---

## 📚 โครงสร้างเนื้อหา (Content Structure)

เนื้อหาถูกแบ่งออกเป็น 4 หัวข้อหลัก ตามประเภทของปรากฏการณ์ทางฟิสิกส์:

### 1. 🌊 Complex Multiphase Phenomena (ปรากฏการณ์หลายเฟสที่ซับซ้อน)
เจาะลึกฟิสิกส์ของการเปลี่ยนสถานะและการกระจายตัวของอนุภาค
*   **บทเรียน:** [00_Overview.md](CONTENT/01_COMPLEX_MULTIPHASE_PHENOMENA/00_Overview.md)
*   **หัวข้อหลัก:** Phase Change (Boiling/Condensation), Cavitation, Population Balance Modeling (PBM)
*   **ห้องปฏิบัติการ:** `LABS/01_PBM/` (กำลังพัฒนา)

### 2. 🔗 Coupled Physics (ฟิสิกส์แบบคู่ควบ)
เรียนรู้การเชื่อมต่อระหว่างสมการฟิสิกส์ที่แตกต่างกัน
*   **บทเรียน:** [00_Overview.md](CONTENT/02_COUPLED_PHYSICS/00_Overview.md)
*   **หัวข้อหลัก:** Conjugate Heat Transfer (CHT), Fluid-Structure Interaction (FSI), Object Registry
*   **ห้องปฏิบัติการ:** `LABS/02_COUPLED_PHYSICS/`
    *   **Exercise 2.1:** Simple CHT Case (การถ่ายเทความร้อนระหว่างของไหลและของแข็ง)

### 3. 🔥 Reacting Flows (การไหลแบบมีปฏิกิริยา)
จำลองการเผาไหม้และปฏิกิริยาเคมีที่มีความซับซ้อน
*   **บทเรียน:** [00_Overview.md](CONTENT/03_REACTING_FLOWS/00_Overview.md)
*   **หัวข้อหลัก:** Combustion Models, Species Transport, Chemistry Integration
*   **ห้องปฏิบัติการ:** `LABS/03_REACTING/` (กำลังพัฒนา)

### 4. 🍯 Non-Newtonian Fluids (ของไหลนอนนิวตัน)
เข้าใจและจำลองของไหลที่มีความหนืดไม่คงที่
*   **บทเรียน:** [00_Overview.md](CONTENT/04_NON_NEWTONIAN_FLUIDS/00_Overview.md)
*   **หัวข้อหลัก:** Viscosity Models (Bird-Carreau, Herschel-Bulkley), Rheology
*   **ห้องปฏิบัติการ:** `LABS/04_NON_NEWTONIAN/` (กำลังพัฒนา)

---

## 🛠️ วิธีการใช้งาน (How to Use)

1.  **ศึกษาทฤษฎี:** เริ่มต้นจากการอ่านไฟล์ในโฟลเดอร์ `CONTENT/` เพื่อทำความเข้าใจหลักการพื้นฐานและสมการควบคุม
2.  **ลงมือปฏิบัติ:** ไปที่โฟลเดอร์ `LABS/` เพื่อทำแบบฝึกหัดที่เตรียมไว้
    *   แต่ละ Lab จะมีโจทย์และไฟล์ตั้งต้น (Case Setup) ให้
    *   ทำตามคำแนะนำในคู่มือการฝึกปฏิบัติ (Exercise Guide) ในโฟลเดอร์ `CONTENT/.../Exercises.md`
3.  **วิเคราะห์ผล:** ใช้ ParaView เพื่อดูผลลัพธ์และเปรียบเทียบกับทฤษฎี

---

> [!TIP]
> **Learning by Doing:** วิธีที่ดีที่สุดในการเรียนรู้ฟิสิกส์ขั้นสูงคือการ "ลองผิดลองถูก" กับการตั้งค่า Solver และสังเกตผลกระทบที่เกิดขึ้นในผลลัพธ์การจำลอง

---
*Created by Antigravity for Advanced Agentic Coding*
