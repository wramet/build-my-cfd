# Phase Change Modeling (การจำลองการเปลี่ยนสถานะ)

> **Phase change** = Transition between liquid/vapor/solid

---

## 1. ประเภทของการเปลี่ยนสถานะ (Types of Phase Change)

| Type | ชนิด | ตัวอย่าง | Driving Force |
|------|------|---------|---------------|
| **Boiling** | การเดือด | Water → Steam | Temperature (T > T_sat) |
| **Condensation** | การควบแน่น | Steam → Water | Temperature (T < T_sat) |
| **Cavitation** | การเกิดโพรง | Liquid → Vapor (low p) | Pressure (p < p_sat) |
| **Solidification** | การแข็งตัว | Liquid → Solid | Temperature (T < T_melt) |
| **Evaporation** | การระเหย | Liquid → Vapor (surface) | Concentration gradient |

---

## 2. Solvers ใน OpenFOAM

```bash
# Cavitation (การเกิดโพรง)
interPhaseChangeFoam

# Boiling/Condensation (การเดือด/ควบแน่น)
interCondensatingEvaporatingFoam

# Multiphase with phase change
reactingTwoPhaseEulerFoam
multiphaseEulerFoam
```

---

## 3. สมการการถ่ายเทมวล (Mass Transfer Equation)

```cpp
// Source term in VOF equation
∂α/∂t + ∇·(Uα) = Γ_evap - Γ_cond

α  = Volume fraction
Γ  = Mass transfer rate [kg/(m³·s)]
```

### 3.1 แบบจำลองการถ่ายเทมวล (Mass Transfer Models)

#### แบบจำลอง Lee (Lee Model)

อัตราการถ่ายเทมวลอิงจากความแตกต่างของอุณหภูมิ:

$$\Gamma = r \cdot \alpha \cdot \rho \cdot \frac{|T - T_{sat}|}{T_{sat}}$$

โดยที่:
- $r$ = ค่าสัมประสิทธิ์การผ่อนถ่าย [1/s]
- $\alpha$ = volume fraction ของเฟส
- $\rho$ = ความหนาแน่น [kg/m³]
- $T$ = อุณหภูมิ [K]
- $T_{sat}$ = อุณหภูมิอิ่มตัว [K]

#### แบบจำลอง Hertz-Knudsen

อิงจากจลนพลศาสตร์โมเลกุล:

$$\Gamma = \frac{2\sigma}{2-\sigma} \sqrt{\frac{M}{2\pi R}} \left(\frac{p_{sat}}{\sqrt{T_{sat}}} - \frac{p}{\sqrt{T}}\right)$$

---

## 4. การตั้งค่าใน OpenFOAM (Setup)

### 4.1 สำหรับ Cavitation (SchnerrSauer Model)

```cpp
// constant/phaseProperties
phases (water vapor);

water
{
    transportModel  Newtonian;
    nu              1e-06;
    rho             1000;
}

vapor
{
    transportModel  Newtonian;
    nu              4.273e-04;
    rho             0.023;
}

phaseChangeModel SchnerrSauer;

SchnerrSauerCoeffs
{
    nBubbles     1e13;      // จำนวนฟองต่อลูกบาศก์เมตร
    pSat         2300;      // ความดันอิ่มตัว [Pa]
    dNucleation  1e-06;     // ขนาดเริ่มต้นของฟอง [m]
}
```

### 4.2 สำหรับ Boiling/Condensation

```cpp
// constant/phaseProperties
phaseChangeModel thermalPhaseChange;

thermalPhaseChangeCoeffs
{
    hLv     2.26e6;      // Latent heat of vaporization [J/kg]
    Tsat    373.15;      // Saturation temperature [K]

    // Mass transfer coefficient
    r       100;         // Relaxation factor [1/s]

    // Temperature limits
    Tmin    300;         // Minimum temperature [K]
    Tmax    400;         // Maximum temperature [K]
}
```

### 4.3 Boundary Conditions

```cpp
// 0/T (Temperature)
dimensions      [0 0 0 1 0 0 0];

internalField   uniform 300;

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 300;
    }

    heatedWall
    {
        type            fixedValue;
        value           uniform 380;  // เหนือ T_sat ทำให้เกิดการเดือด
    }

    outlet
    {
        type            zeroGradient;
    }
}
```

---

## 5. ข้อควรระวังและปัญหาที่พบบ่อย

| ปัญหา | สาเหตุ | วิธีแก้ |
|--------|---------|---------|
| **Divergence** | Timestep ใหญ่เกินไป | ลด Δt หรือใช้ MaxCo < 0.3 |
| **Unrealistic Temperature** | BC ผิด หรือ Cp ผิด | ตรวจสอบ BC และ thermophysical properties |
| **Pressure Oscillations** | การเปลี่ยนความหนาแน่นอย่างรุนแรง | เพิ่ม nCorrectors ใน PIMPLE (3-5 ครั้ง) |
| **Mass Imbalance** | Mass transfer rate ไม่สมดุล | ตรวจสอบ Γ_evap และ Γ_cond |

---

## Quick Reference

| Solver | การใช้งาน | Phase Change |
|--------|-------------|--------------|
| interPhaseChangeFoam | Cavitation | Pressure-driven |
| interCondensating... | Boiling/Condensation | Temperature-driven |
| reactingTwoPhaseEulerFoam | Multiphase reacting | Both |

---

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
