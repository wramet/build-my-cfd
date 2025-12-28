# Coupled Physics - Overview

ภาพรวม Coupled Physics

---

## Overview

> **Coupled physics** = Multiple physics domains interacting

---

## 1. Types

| Coupling | Example |
|----------|---------|
| CHT | Fluid + Solid heat |
| FSI | Fluid + Structure |
| MHD | Fluid + EM |

---

## 2. Solver

```bash
chtMultiRegionFoam  # CHT
```

---

## 3. Regions

```cpp
// constant/regionProperties
regions (fluid (fluid) solid (heater));
```

---

## 4. Module Contents

| File | Topic |
|------|-------|
| 01_Fundamentals | Basics |
| 02_CHT | Heat transfer |
| 04_Registry | Multi-region |
| 05_Advanced | Topics |

---

## Quick Reference

| Need | Solver |
|------|--------|
| CHT | chtMultiRegionFoam |

## 🧠 Concept Check

<details>
<summary><b>1. Multi-region simulation คืออะไร?</b></summary>

**Multi-region** คือการจำลองที่มี **หลาย mesh แยกกัน** แต่ coupled กันที่ interfaces

**ตัวอย่าง:**
- **CHT:** Fluid region + Solid region → แลกเปลี่ยนความร้อนที่ผนัง
- **FSI:** Fluid region + Structural solver → แลกเปลี่ยนแรงและการเสียรูป

```cpp
regions (fluid (fluid) solid (heater));
```

</details>

<details>
<summary><b>2. CHT (Conjugate Heat Transfer) ใช้เมื่อไหร่?</b></summary>

ใช้เมื่อต้องการจำลอง **การถ่ายเทความร้อนระหว่างของไหลและของแข็ง:**

**ตัวอย่าง:**
- Heat sink ระบายความร้อนจาก CPU
- เครื่องแลกเปลี่ยนความร้อน (Heat exchanger)
- การระบายความร้อนของ Electronic components

**Solver:** `chtMultiRegionFoam`

</details>

<details>
<summary><b>3. ความแตกต่างระหว่าง Weak และ Strong Coupling?</b></summary>

| Aspect | Weak Coupling | Strong Coupling |
|--------|---------------|-----------------|
| **วิธี** | แก้แต่ละ region ทีละครั้ง | วนซ้ำจนลู่เข้า |
| **ความเสถียร** | ดีสำหรับ loose coupling | ดีสำหรับ tight coupling |
| **ต้นทุน** | ต่ำกว่า | สูงกว่า |
| **ตัวอย่าง** | CHT ง่ายๆ | FSI ในน้ำ |

</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **บทถัดไป:** [01_Coupled_Physics_Fundamentals.md](01_Coupled_Physics_Fundamentals.md) — พื้นฐาน Coupled Physics
- **CHT:** [02_Conjugate_Heat_Transfer.md](02_Conjugate_Heat_Transfer.md) — การถ่ายเทความร้อนแบบ Conjugate
- **FSI:** [03_Fluid_Structure_Interaction.md](03_Fluid_Structure_Interaction.md) — ปฏิสัมพันธ์ของไหล-โครงสร้าง
- **Advanced:** [05_Advanced_Coupling_Topics.md](05_Advanced_Coupling_Topics.md) — หัวข้อขั้นสูง