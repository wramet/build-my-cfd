# Reacting Flows - Overview

ภาพรวม Reacting Flows

---

## Overview

> **Reacting flows** = Fluid flow with chemical reactions

---

## 1. Key Concepts

| Concept | Description |
|---------|-------------|
| **Species** | Chemical components |
| **Reactions** | รสาร → ผลผลิต |
| **Heat release** | Energy from reaction |
| **Combustion** | Fuel + oxidizer → products |

---

## 2. OpenFOAM Solvers

| Solver | Use |
|--------|-----|
| `reactingFoam` | General reacting |
| `XiFoam` | Premixed combustion |
| `sprayFoam` | Spray + combustion |
| `fireFoam` | Fire simulation |

---

## 3. Governing Equations

```
∂ρYᵢ/∂t + ∇·(ρUYᵢ) = ∇·(ρDᵢ∇Yᵢ) + ωᵢ

Yᵢ = mass fraction of species i
ωᵢ = reaction rate
```

---

## 4. Chemistry Models

| Model | Speed | Accuracy |
|-------|-------|----------|
| Finite rate | Slow | High |
| EDC | Medium | Medium |
| PaSR | Fast | Medium |
| Flamelet | Fast | Good |

---

## 5. Module Contents

| File | Topic |
|------|-------|
| 01_Fundamentals | Basics |
| 04_Combustion | Models |
| 05_Chemkin | Parsing |
| 06_Workflow | Practice |

---

## Quick Reference

| Need | Solver |
|------|--------|
| Multi-species | reactingFoam |
| Premixed flame | XiFoam |
| Spray combustion | sprayFoam |
| Fire | fireFoam |

---

## 🧠 Concept Check

<details>
<summary><b>1. Species transport equation?</b></summary>

**Convection + Diffusion + Reaction** ของ mass fraction
</details>

<details>
<summary><b>2. EDC คืออะไร?</b></summary>

**Eddy Dissipation Concept** — turbulence-chemistry interaction
</details>

<details>
<summary><b>3. Chemkin ใช้ทำอะไร?</b></summary>

**Define reactions** และ thermodynamic properties
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **Fundamentals:** [01_Reacting_Flow_Fundamentals.md](01_Reacting_Flow_Fundamentals.md)
- **Combustion:** [04_Combustion_Models.md](04_Combustion_Models.md)
