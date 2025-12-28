# Practical Workflow

การใช้งาน Reacting Flow ในทางปฏิบัติ

---

## Overview

> Step-by-step workflow for reacting flow cases

---

## 1. Case Setup

```
case/
├── 0/
│   ├── U, p, T
│   ├── CH4, O2, CO2, H2O, N2
│   └── Ydefault
├── constant/
│   ├── chemistryProperties
│   ├── combustionProperties
│   ├── reactions
│   └── thermo.compressibleGas
└── system/
    └── controlDict, fvSchemes, fvSolution
```

---

## 2. Define Species

```cpp
// constant/reactions
species
(
    CH4
    O2
    CO2
    H2O
    N2
);
```

---

## 3. Define Reactions

```cpp
// constant/reactions
reactions
(
    // CH4 + 2O2 -> CO2 + 2H2O
    methaneReaction
    {
        type    irreversibleArrheniusReaction;
        reaction    "CH4 + 2O2 = CO2 + 2H2O";
        A           1.5e11;
        Ta          24370;
    }
);
```

---

## 4. Combustion Model

```cpp
// constant/combustionProperties
combustionModel  laminar;
// or
combustionModel  EDC;
combustionModel  PaSR;
```

---

## 5. Run Simulation

```bash
# Mesh
blockMesh

# Initialize
setFields

# Run
reactingFoam

# Post-process
paraFoam
```

---

## 6. Monitor

```bash
# Check species
grep 'O2' log.reactingFoam | tail -5

# Check temperature
grep 'T max' log.reactingFoam | tail -5

# Check heat release
postProcess -func 'Qdot'
```

---

## Quick Reference

| Step | Action |
|------|--------|
| 1 | Define species in reactions |
| 2 | Write reaction mechanisms |
| 3 | Set thermo properties |
| 4 | Choose combustion model |
| 5 | Run reactingFoam |

---

## Concept Check

<details>
<summary><b>1. Ydefault ใช้ทำอะไร?</b></summary>

**Template** สำหรับ species BCs
</details>

<details>
<summary><b>2. EDC vs laminar?</b></summary>

- **laminar**: Direct chemistry
- **EDC**: Turbulence-chemistry interaction
</details>

<details>
<summary><b>3. ตรวจ convergence อย่างไร?</b></summary>

**Monitor species, T, residuals**
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Chemkin:** [05_Chemkin_Parsing.md](05_Chemkin_Parsing.md)
