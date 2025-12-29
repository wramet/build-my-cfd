# Reacting Flow Fundamentals

พื้นฐาน Reacting Flows

---

## Overview

> Chemical reactions in flowing fluids

<!-- IMAGE: IMG_06_003 -->
<!-- 
Purpose: เพื่อแสดงโครงสร้างของ "เปลวไฟ" (Flame Structure) ในเชิง CFD. ภาพนี้ต้องโชว์การเปลี่ยนแปลงของ 3 ตัวแปรหลักเมื่อผ่านเปลวไฟ: 1. เชื้อเพลิง ($Y_{Fuel}$) ลดลง 2. ผลิตภัณฑ์ ($Y_{Product}$) เพิ่มขึ้น 3. อุณหภูมิ ($T$) พุ่งสูงขึ้น และจุดที่กราฟตัดกันคือตำแหน่งของ "Reaction Zone"
Prompt: "Combustion Physics Profile Diagram (Pre-mixed Flame). **X-axis:** Distance through flame. **Y-axis:** Normalized Value (0 to 1). **Curves:** 1. **Fuel Mass Fraction (Blue):** Starts at 1, drops sharply to 0 at the flame front. 2. **Oxidizer Mass Fraction (Green):** Follows Fuel curve. 3. **Product Mass Fraction (Purple):** Starts at 0, rises sharply to 1. 4. **Temperature (Red):** S-Curve starting low (Unburnt) and rising to high (Burnt). **Highlight:** A vertical zone labeled 'Reaction Zone $\dot{\omega}$' where the gradients are steepest. STYLE: Textbook scientific plot, clear lines, distinct zones."
-->
![[IMG_06_003.jpg]]

---

## 1. Species Transport

```
∂(ρYᵢ)/∂t + ∇·(ρUYᵢ) = ∇·(ρDᵢ∇Yᵢ) + ωᵢ

Yᵢ = mass fraction of species i
ωᵢ = reaction source term
```

---

## 2. Reaction Rate

```cpp
// Arrhenius form
k = A * T^n * exp(-Ea / RT)

// Example
reactionRate
{
    type    ArrheniusReaction;
    A       1e10;
    Ea      1e5;
    n       0;
}
```

---

## 3. Energy Equation

```cpp
// With heat release
fvScalarMatrix TEqn
(
    fvm::ddt(rho, he)
  + fvm::div(phi, he)
  - fvm::laplacian(alphaEff, he)
  ==
    Qdot  // Heat release from reactions
);
```

---

## 4. OpenFOAM Setup

```cpp
// constant/chemistryProperties
chemistryType
{
    chemistrySolver ode;
    chemistryThermo psi;
}

chemistry       on;
initialChemicalTimeStep 1e-7;
```

---

## 5. Solver Selection

| Solver | Use |
|--------|-----|
| reactingFoam | General reacting |
| chemFoam | OD reactor |
| XiFoam | Premixed flame |

---

## 6. ODE Solver

```cpp
// constant/chemistryProperties
odeCoeffs
{
    solver  seulex;
    absTol  1e-8;
    relTol  1e-4;
}
```

---

## Quick Reference

| Term | Meaning |
|------|---------|
| Yᵢ | Mass fraction |
| ωᵢ | Reaction rate |
| Qdot | Heat release |
| Ea | Activation energy |

---

## 🧠 Concept Check

<details>
<summary><b>1. Mass fraction sum?</b></summary>

**ΣYᵢ = 1** — all species
</details>

<details>
<summary><b>2. Arrhenius คืออะไร?</b></summary>

**Temperature-dependent** reaction rate
</details>

<details>
<summary><b>3. ODE solver ใช้ทำไม?</b></summary>

**Stiff chemistry** — fast reactions need special solver
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Combustion:** [04_Combustion_Models.md](04_Combustion_Models.md)