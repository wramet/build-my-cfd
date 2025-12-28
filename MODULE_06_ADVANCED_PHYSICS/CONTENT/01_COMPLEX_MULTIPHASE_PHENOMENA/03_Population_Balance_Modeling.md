# Population Balance Modeling

การจำลอง Population Balance

---

## Overview

> **PBM** = Track particle size distribution evolution

---

## 1. Population Balance Equation

```
∂n/∂t + ∇·(Un) = Birth - Death + Breakup - Coalescence

n(d) = number density at size d
```

---

## 2. OpenFOAM Implementation

```cpp
// constant/phaseProperties
populationBalanceCoeffs
{
    populationBalance bubbles;

    coalescenceModels
    (
        LehrMilliesMewes{}
    );

    breakupModels
    (
        LehrMilliesMewes{}
    );
}
```

---

## 3. Size Classes

```cpp
// constant/phaseProperties
diameterModel velocityGroup;

velocityGroupCoeffs
{
    populationBalance bubbles;
    shapeModel spherical;

    sizeGroups
    (
        f0 { d 1e-4; }
        f1 { d 2e-4; }
        f2 { d 4e-4; }
        // ...
    );
}
```

---

## 4. Coalescence Models

| Model | Use |
|-------|-----|
| LehrMilliesMewes | Bubble coalescence |
| CoulaloglouTavlarides | Liquid drops |
| constant | Simple testing |

---

## 5. Breakup Models

| Model | Use |
|-------|-----|
| LehrMilliesMewes | Turbulent breakup |
| LuoSvendsen | Energy-based |
| Laakkonen | High shear |

---

## 6. Solver

```bash
# Use multiphase solver
multiphaseEulerFoam

# With population balance enabled in phaseProperties
```

---

## Quick Reference

| Process | Models |
|---------|--------|
| Coalescence | LehrMillies, Coulaloglou |
| Breakup | Luo, Laakkonen |
| Size groups | velocityGroup |

---

## Concept Check

<details>
<summary><b>1. PBM ใช้เมื่อไหร่?</b></summary>

**Track size distribution** — เช่น bubbles, drops
</details>

<details>
<summary><b>2. Coalescence คืออะไร?</b></summary>

**Particles merge** → larger size
</details>

<details>
<summary><b>3. Size groups คืออะไร?</b></summary>

**Discrete sizes** สำหรับ represent distribution
</details>

---

## Related Documents

- **ภาพรวม:** [../01_COMPLEX_MULTIPHASE_PHENOMENA/00_Overview.md](../01_COMPLEX_MULTIPHASE_PHENOMENA/00_Overview.md)
- **Cavitation:** [02_Cavitation_Modeling.md](02_Cavitation_Modeling.md)