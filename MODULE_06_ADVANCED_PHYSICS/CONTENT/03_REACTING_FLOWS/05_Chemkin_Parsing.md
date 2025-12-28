# Chemkin Parsing

การใช้งาน Chemkin Files

---

## Overview

> **Chemkin** = Standard format for chemistry

---

## 1. Files

| File | Content |
|------|---------|
| thermo.dat | Thermo properties |
| chem.inp | Reactions |
| tran.dat | Transport |

---

## 2. Convert to OpenFOAM

```bash
chemkinToFoam chem.inp thermo.dat constant/reactions constant/thermo
```

---

## 3. Reaction Format

```
CH4 + 2O2 => CO2 + 2H2O   1.5E11  0.0  24370
```

---

## 4. Usage

```cpp
// constant/chemistryProperties
chemistryReader chemkinReader;
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Convert | chemkinToFoam |
| Read | chemkinReader |

## 🧠 Concept Check

<details>
<summary><b>1. Chemkin format ใช้ทำไม?</b></summary>

**Chemkin** เป็น **standard format** สำหรับ chemistry mechanisms ที่ใช้กันทั่วโลก

**ประโยชน์:**
- ใช้ mechanisms จาก literature ได้โดยตรง
- มี database ขนาดใหญ่ (GRI-Mech, USC Mech II, etc.)
- ไม่ต้องเขียน reactions เอง

</details>

<details>
<summary><b>2. ไฟล์ Chemkin มีอะไรบ้าง?</b></summary>

| ไฟล์ | เนื้อหา | ตัวอย่าง |
|------|---------|----------|
| **thermo.dat** | คุณสมบัติ thermodynamic | Cp, H, S |
| **chem.inp** | ปฏิกิริยาเคมี | CH4 + 2O2 → CO2 + 2H2O |
| **tran.dat** | Transport properties | μ, k, D |

**การแปลง:**
```bash
chemkinToFoam chem.inp thermo.dat constant/reactions constant/thermo
```

</details>

<details>
<summary><b>3. Modified Arrhenius equation คืออะไร?</b></summary>

ใน Chemkin ทุกปฏิกิริยาใช้ Modified Arrhenius:

$$k = A \cdot T^n \cdot \exp\left(-\frac{E_a}{RT}\right)$$

**ตัวอย่างใน chem.inp:**
```
CH4 + 2O2 => CO2 + 2H2O   1.5E11  0.0  24370
                          ↑ A     ↑ n  ↑ Ea (cal/mol)
```

</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md) — ภาพรวม Reacting Flows
- **บทก่อนหน้า:** [04_Combustion_Models.md](04_Combustion_Models.md) — Combustion Models
- **บทถัดไป:** [06_Practical_Workflow.md](06_Practical_Workflow.md) — ขั้นตอนปฏิบัติ
- **Chemistry Models:** [03_Chemistry_Models.md](03_Chemistry_Models.md) — โมเดลเคมี