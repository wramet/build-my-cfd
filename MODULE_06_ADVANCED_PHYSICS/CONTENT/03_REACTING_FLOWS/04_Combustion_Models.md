# Combustion Models

Combustion Models ใน OpenFOAM

---

## Overview

> Different models for turbulence-chemistry interaction

---

## 1. Model Comparison

| Model | Speed | Accuracy | Use |
|-------|-------|----------|-----|
| Laminar | Slow | High | Small flames |
| EDC | Medium | Medium | Industrial |
| PaSR | Fast | Medium | Large cases |
| Flamelet | Fast | Good | Premixed |

---

## 2. Laminar

```cpp
// constant/combustionProperties
combustionModel laminar;

// Solve chemistry directly
// Good for non-turbulent or DNS
```

---

## 3. Eddy Dissipation Concept (EDC)

```cpp
// constant/combustionProperties
combustionModel EDC;

EDCCoeffs
{
    version         v2016;
}

// Mixing-limited combustion
// Uses eddy dissipation rate
```

---

## 4. Partially Stirred Reactor (PaSR)

```cpp
// constant/combustionProperties
combustionModel PaSR;

PaSRCoeffs
{
    mixingModel     simple;
    Cmix            0.3;
}

// Good for mixed kinetic/mixing control
```

---

## 5. Premixed Flame (Xi)

```cpp
// Use XiFoam solver
combustionModel  Xi;

XiCoeffs
{
    XiShapeCoeff    0.8;
    XiModel         transport Xi0;
}

// Uses flame wrinkling factor Xi
```

---

## 6. Selection Guide

| Regime | Model |
|--------|-------|
| Diffusion flame | EDC |
| Premixed | Xi, flamelet |
| Mixed | PaSR |
| Slow chemistry | Finite rate |

---

## Quick Reference

| Model | Solver |
|-------|--------|
| Laminar | reactingFoam |
| EDC | reactingFoam |
| PaSR | reactingFoam |
| Xi | XiFoam |

---

## 🧠 Concept Check

<details>
<summary><b>1. EDC คืออะไร?</b></summary>

**Eddy Dissipation Concept** — mixing controls reaction
</details>

<details>
<summary><b>2. Premixed vs diffusion?</b></summary>

- **Premixed**: Fuel+air mixed beforehand
- **Diffusion**: Mix while burning
</details>

<details>
<summary><b>3. XiFoam ใช้เมื่อไหร่?</b></summary>

**Premixed turbulent flames** — เช่น gas engines
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Fundamentals:** [01_Reacting_Flow_Fundamentals.md](01_Reacting_Flow_Fundamentals.md)
