# 04 Interphase Forces (แรงระหว่างเฟส)

> [!TIP]
> **ทำไม Interphase Forces ถึงสำคัญใน Multiphase Flow?**
>
> แรงระหว่างเฟส (Interphase Forces) เป็นศูนย์กลางของการจำลอง Multiphase Flow ที่แท้จริง เพราะ:
> - **การโต้ตอบระหว่างเฟส**: บอบบาง (Droplets/Bubbles) มีพฤติกรรมที่แตกต่างจากเฟสต่อเนื่อง (Continuous Phase)
> - **การกระจายตัว**: แรง Drag, Lift, Virtual Mass ส่งผลต่อวิถีการเคลื่อนที่ของ Particle/Droplet
> - **การระเหย**: ใน R410A Evaporation, Surface Tension ส่งผลต่อประสิทธิภาพการระเหย
> - **การทำนาย Flow Regime**: การเข้าใจ Interphase Forces ช่วยในการทำนายและจำแนก Flow Regime ได้ถูกต้อง

---

## 🎯 Learning Objectives

หลังจากผ่านส่วนนี้ คุณจะสามารถ:

- **ระบุและคำนวณ** Interphase Forces ต่างๆ (Drag, Lift, Virtual Mass, Surface Tension)
- **เลือกโมเดล Interphase Forces** ที่เหมาะสมสำหรับ Flow Regime ที่ต้องการ
- **นำไปใช้ใน OpenFOAM** ได้อย่างถูกต้องใส่ source terms ใน solver
- **วิเคราะห์ผลกระทบ** ของแรงเหล่านี้ต่อประสิทธิภาพ Heat Exchanger
- **ตั้งค่า Boundary Conditions** สำหรับแรงที่เกี่ยวข้องกับ R410A

---

## 🎯 Module Structure

| Section | Title | Focus | R410A Relevance |
|---------|-------|-------|-----------------|
| **01_DRAG** | Drag Forces | แรงต้านออกซีเจนที่เฟส | ⭐️⭐️⭐️⭐️⭐️ สำคัญที่สุดสำหรับ Pressure Drop |
| **02_LIFT** | Lift Forces | แรงยกซึ่งตั้งฉากกับการไหล | ⭐️⭐️⭐️ สำคัญสำหรับ Bubble Migration |
| **03_VIRTUAL_MASS** | Virtual Mass | แรงเสริมมวลสมมาตร | ⭐️⭐️ สำคัญในการเปลี่ยนเฟสเร็ว |
| **04_TURBULENT_DISPERSION** | Turbulent Dispersion | การกระจายตัวจาก Turbulence | ⭐️⭐️ สำคัญในของไหลชุมนุม |
| **05_SURFACE_TENSION** | Surface Tension | แรงตัวผิวผิว | ⭐️⭐️⭐️⭐️⭐️ สำคัญสำหรับ Microchannel |

---

## 🎯 Learning Path

### Path A: Drag Forces First
**สำหรับใครที่เริ่มต้นจาก Zero**

1. **01_DRAG/01_Drag_Forces.md** - แรง Drag พื้นฐาน
2. **02_LIFT/01_Lift_Forces.md** - แรง Lift และ Saffman Force
3. **03_VIRTUAL_MASS/01_Virtual_Mass.md** - แรงเสริมมวล
4. **04_TURBULENT_DISPERSION/01_Turbulent_Dispersion.md** - การกระจายตัว
5. **05_SURFACE_TENSION/01_Surface_Tension_R410A.md** - แรงตัวผิวผิว

### Path B: Special Focus on R410A
**สำหรับใครที่สนใจ Heat Exchanger และ Evaporation**

1. **05_SURFACE_TENSION/01_Surface_Tension_R410A.md** - Surface Tension (สำคัญสุด)
2. **01_DRAG/01_Drag_Forces.md** - Drag Forces (สำคัญสำหรับ Pressure Drop)
3. **02_LIFT/01_Lift_Forces.md** - Lift Forces (สำคัญสำหรับ Bubble behavior)

> [!NOTE]
> **🔥 สำคัญมากสำหรับ R410A**: Surface Tension ส่งผลต่อ **Bubble Formation**, **Film Stability**, และ **Pressure Drop** ใน Microchannel Evaporator อย่างมาก

---

## 🧠 Concept Check

**1. แรงใดที่ส่งผลต่อ Pressure Drop ใน Pipe Flow มากที่สุด?**

<details>
<summary>เฉลย</summary>
**Drag Force** - เพราะมันส่งผลต่อความต้านทานของของไหล (Skin Friction) และ Pressure Drop โดยตรง
</details>

**2. Surface Tension ส่งผลต่อ Flow Regime อย่างไรใน Microchannel?**

<details>
<summary>เฉลย</summary>
Surface Tension ส่งผลต่อ **Capillary Forces** ซึ่งสร้าง Pressure Gradient ในแนวตั้ง เป็นตัวกำหนด Bubble Size, Film Thickness และ Flow Pattern (Slug vs Annular)
</details>

**3. Virtual Mass Force สำคัญในเวลาใด?**

<details>
<summary>เฉลย</summary**
เมื่อเกิด **Rapid Phase Change** เช่น การระเหยที่เกิดขึ้นเร็วๆ เช่นใน Flash Evaporation หรือ Supercritical Conditions
</details>

---

## 📝 Key Takeaways

✅ **Drag Force** - ส่งผลต่อ Pressure Drop มากที่สุดใน Tube Flow

✅ **Surface Tension** - สำคัญสำหรับ Microchannel และ Bubble Formation

✅ **Lift Force** - ส่งผลต่อ Bubble Migration ใน Tube

✅ **Virtual Mass** - สำคัญสำหรับ Flow Acceleration

✅ **Turbulent Dispersion** - ส่งผลต่อ Particle Distribution ใข่ขวดหนา

---

## 🔗 Prerequisites

- ความเข้าใจพื้นฐาน **Multiphase Concepts** (../01_FUNDAMENTAL_CONCEPTS/)
- ความเข้าใจ **VOF Method** พื้นฐาน (../02_VOF_METHOD/)
- ความเข้าใจ **Eulerian-Eulerian Method** (../03_EULER_EULER_METHOD/)

---

## ➡️ Next Steps

เริ่มต้นจาก: **[01_DRAG/00_Overview.md](01_DRAG/00_Overview.md)** หรือ **[05_SURFACE_TENSION/00_Overview.md](05_SURFACE_TENSION/00_Overview.md)**

---

## 📖 Related Documents

- **บทก่อนหน้า**: [../03_EULER_EULER_METHOD/00_Overview.md](../03_EULER_EULER_METHOD/00_Overview.md)
- **บทถัดไป**: [../05_MODEL_SELECTION/00_Overview.md](../05_MODEL_SELECTION/00_Overview.md)