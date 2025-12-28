# Cavitation Modeling

การจำลอง Cavitation

---

## Overview

> **Cavitation** = Phase change from liquid to vapor at low pressure

---

## 1. Physics

```
p < pSat → liquid → vapor (evaporation)
p > pSat → vapor → liquid (condensation)
```

---

## 2. OpenFOAM Solver

```bash
# Use interPhaseChangeFoam
interPhaseChangeFoam
```

---

## 3. Cavitation Models

| Model | Use |
|-------|-----|
| SchnerrSauer | General purpose |
| Kunz | Marine propellers |
| Merkle | Industrial |

```cpp
// constant/phaseProperties
model   SchnerrSauer;

SchnerrSauerCoeffs
{
    n       1.6e13;  // Nucleation site density
    dNuc    2e-6;    // Nucleation diameter
    Cc      1;       // Condensation coefficient
    Cv      1;       // Vaporization coefficient
}
```

---

## 4. Properties

```cpp
// constant/transportProperties
phases (water vapor);

water
{
    transportModel  Newtonian;
    nu              1e-6;
    rho             1000;
}

vapor
{
    transportModel  Newtonian;
    nu              4.273e-4;
    rho             0.023;
}

pSat    2300;  // Saturation pressure [Pa]
```

---

## 5. Mass Transfer

```cpp
// Source term in VOF equation
∂α/∂t + ∇·(Uα) = Γₑ - Γc

Γₑ = evaporation rate
Γc = condensation rate
```

---

## 6. Numerical Settings

```cpp
// system/fvSchemes
divSchemes
{
    div(rhoPhi,U)   Gauss linearUpwind grad(U);
    div(phi,alpha)  Gauss vanLeer;
}
```

---

## Quick Reference

| Parameter | Typical Value |
|-----------|---------------|
| pSat (water) | 2300 Pa |
| Nuclei density | 1e13 1/m³ |
| Nuclei size | 2e-6 m |

---

## 🧠 Concept Check

<details>
<summary><b>1. Cavitation เกิดเมื่อไหร่?</b></summary>

**p < pSat** — pressure below saturation
</details>

<details>
<summary><b>2. SchnerrSauer model ทำอะไร?</b></summary>

**Mass transfer rate** based on bubble dynamics
</details>

<details>
<summary><b>3. ทำไม cavitation สำคัญ?</b></summary>

**Damage**, noise, performance loss in pumps/propellers
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [../01_COMPLEX_MULTIPHASE_PHENOMENA/00_Overview.md](../01_COMPLEX_MULTIPHASE_PHENOMENA/00_Overview.md)
- **Phase Change:** [01_Phase_Change_Modeling.md](01_Phase_Change_Modeling.md)
