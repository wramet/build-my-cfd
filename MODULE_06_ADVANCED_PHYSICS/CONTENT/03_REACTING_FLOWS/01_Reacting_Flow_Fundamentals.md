# Reacting Flow Fundamentals

พื้นฐาน Reacting Flows

---

## Overview

> Chemical reactions in flowing fluids

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