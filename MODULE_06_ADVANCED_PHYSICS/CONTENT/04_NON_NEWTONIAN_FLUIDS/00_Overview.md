# Non-Newtonian Fluids - Overview

ภาพรวม Non-Newtonian Fluids

---

## Overview

> **Non-Newtonian** = Viscosity depends on shear rate

---

## 1. Newtonian vs Non-Newtonian

| Type | Viscosity |
|------|-----------|
| Newtonian | Constant |
| Shear-thinning | η ↓ as γ̇ ↑ |
| Shear-thickening | η ↑ as γ̇ ↑ |
| Yield stress | η = ∞ until τ > τy |

---

## 2. Common Models

| Model | Behavior |
|-------|----------|
| Power Law | η = k γ̇^(n-1) |
| Cross | Plateau + shear thin |
| Carreau | Smooth transition |
| Bingham | Yield stress |
| Herschel-Bulkley | Yield + power law |

---

## 3. OpenFOAM Setup

```cpp
// constant/transportProperties
transportModel  CrossPowerLaw;

CrossPowerLawCoeffs
{
    nu0     0.01;
    nuInf   0.0001;
    m       0.1;
    n       0.5;
}
```

---

## 4. Solvers

| Solver | Use |
|--------|-----|
| simpleFoam | Steady |
| pimpleFoam | Transient |
| viscoelasticFluidFoam | Elastic |

---

## 5. Module Contents

| File | Topic |
|------|-------|
| 02_Viscosity_Models | Model equations |
| 03_OpenFOAM_Architecture | Implementation |
| 04_Numerical | Numerics |
| 05_Practical | Usage |

---

## Quick Reference

| Parameter | Meaning |
|-----------|---------|
| n < 1 | Shear thinning |
| n > 1 | Shear thickening |
| τy | Yield stress |

---

## 🧠 Concept Check

<details>
<summary><b>1. Blood เป็น non-Newtonian ไหม?</b></summary>

**ใช่** — shear-thinning behavior
</details>

<details>
<summary><b>2. Power law n = 1?</b></summary>

**Newtonian** — constant viscosity
</details>

<details>
<summary><b>3. Yield stress คืออะไร?</b></summary>

**Minimum stress** to initiate flow
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **Viscosity Models:** [02_Viscosity_Models.md](02_Viscosity_Models.md)
- **Implementation:** [04_Numerical_Implementation.md](04_Numerical_Implementation.md)
