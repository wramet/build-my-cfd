# Phase Change Modeling

การจำลอง Phase Change

---

## Overview

> **Phase change** = Transition between liquid/vapor/solid

---

## 1. Types

| Type | Example |
|------|---------|
| Boiling | Water → Steam |
| Condensation | Steam → Water |
| Cavitation | Liquid → Vapor (low p) |
| Solidification | Liquid → Solid |

---

## 2. Solver

```bash
interPhaseChangeFoam  # Cavitation
interCondensatingEvaporatingFoam  # Boiling
```

---

## 3. Mass Transfer

```cpp
// Source in VOF equation
∂α/∂t + ∇·(Uα) = Γ_evap - Γ_cond
```

---

## 4. Setup

```cpp
// constant/phaseProperties
model SchnerrSauer;
pSat 2300;  // Saturation pressure
```

---

## Quick Reference

| Solver | Use |
|--------|-----|
| interPhaseChangeFoam | Cavitation |
| interCondensating... | Boiling |

## 🧠 Concept Check

<details>
<summary><b>1. Phase change เกิดจากอะไรได้บ้าง?</b></summary>

**Phase change เกิดได้จาก 2 สาเหตุหลัก:**
- **Temperature-driven:** อุณหภูมิเปลี่ยน (เช่น Boiling, Condensation)
- **Pressure-driven:** ความดันเปลี่ยน (เช่น Cavitation)

**ตัวอย่าง:**
- น้ำเดือด ($T > T_{sat}$) → Steam
- ความดันต่ำในปั๊ม ($p < p_{sat}$) → ฟองอากาศ

</details>

<details>
<summary><b>2. ทำไมต้องใช้ Mass Transfer Source Term ($\Gamma$)?</b></summary>

เพราะ VOF equation ปกติไม่รองรับการเปลี่ยนสถานะ:

$$\frac{\partial \alpha}{\partial t} + \nabla \cdot (U\alpha) = \underbrace{\Gamma_{evap} - \Gamma_{cond}}_{\text{Mass Transfer}}$$

- **$\Gamma_{evap}$:** อัตราการระเหย (ของเหลว → ไอ)
- **$\Gamma_{cond}$:** อัตราการควบแน่น (ไอ → ของเหลว)
- ถ้าไม่มี → ปริมาตรสัดส่วน ($\alpha$) จะไม่เปลี่ยน

</details>

<details>
<summary><b>3. Saturation Pressure ($p_{sat}$) สำคัญอย่างไร?</b></summary>

**$p_{sat}$** คือความดันที่ของเหลวเริ่มเปลี่ยนสถานะที่อุณหภูมินั้นๆ

**ในโค้ด OpenFOAM:**
```cpp
pSat 2300;  // Pa (สำหรับน้ำที่ 20°C)
```

**การใช้งาน:**
- ถ้า $p < p_{sat}$ → **Cavitation** (เกิดฟอง)
- ถ้า $p > p_{sat}$ → **Condensation** (ฟองยุบ)

</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md) — ภาพรวม Complex Multiphase
- **บทถัดไป:** [02_Cavitation_Modeling.md](02_Cavitation_Modeling.md) — การจำลอง Cavitation
- **Population Balance:** [03_Population_Balance_Modeling.md](03_Population_Balance_Modeling.md) — สมดุลประชากร
