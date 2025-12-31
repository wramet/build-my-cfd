---
name: Advanced Physics Tutor
description: |
  Use this skill when: user asks about complex physics models, phase change, cavitation, population balance, or advanced thermodynamics in OpenFOAM.
  
  Specialist tutor for MODULE_06_ADVANCED_PHYSICS content.
---

# Advanced Physics Tutor

ผู้เชี่ยวชาญด้าน Advanced Physics: Phase Change, Cavitation, Population Balance Model (PBM)

## Knowledge Base

**Primary Content:** `MODULE_06_ADVANCED_PHYSICS/CONTENT/`

```
01_PHASE_CHANGE_MODELING/
├── 00_Overview.md            → Thermophysical models
├── 01_Boiling_Models.md      → Lee, Merte-Hughes
├── 02_Condensation.md        → Kinetic theory
└── 04_Solver_InterCondensingEvaporatingFoam.md

02_CAVITATION_MODELING/
├── 00_Overview.md            → Physics of cavitation
├── 01_Mass_Transfer.md       → Kunz, Merkle, Schnerr-Sauer
└── 03_InterPhaseChangeFoam.md

03_POPULATION_BALANCE_MODELING/
├── 00_Overview.md            → Polydispersed flows
├── 01_PBE_Equation.md        → Breakup & Coalescence
└── 04_DriftFluxFoam.md
```

## Learning Paths

### 🟢 Beginner (Understanding Concepts)

**Goal:** เข้าใจกลไกฟิสิกส์ของการเปลี่ยนสถานะและ cavitation

| Topic | File | Focus |
|-------|------|-------|
| **Boiling** | `01_PHASE_CHANGE/01_Boiling.md` | Lee model parameter ($C$) |
| **Cavitation** | `02_CAVITATION/00_Overview.md` | Vapor pressure, nucleation |
| **PBM** | `03_PBM/00_Overview.md` | Classes vs Moments |

**Concept Check:**
1. ทำไม $C$ ใน Lee model ถึงเป็น fitting parameter?
2. Cavitation ต่างจาก Boiling อย่างไร?

### 🟡 Intermediate (Solver Usage)

**Goal:** ใช้งาน solver และเลือก model ที่เหมาะสม

- **interPhaseChangeFoam**: สำหรับ Cavitation (isothermal)
- **interCondensingEvaporatingFoam**: สำหรับ Boiling/Condensation (thermal driven)
- **reactingTwoPhaseEulerFoam**: สำหรับ complex thermodynamics

**Key Config:** `phaseProperties`, `thermophysicalProperties`

### 🔴 Advanced (Model Implementation)

**Goal:** เขียน phase change model ใหม่ หรือแก้ไข source code

**Source Code Focus:**
- `$FOAM_SRC/phaseChangeModels/`
- `$FOAM_SRC/lagrangian/intermediate/submodels/Reacting/PhaseChangeModel/`

## Common Pitfalls

1. **Time Step:** Phase change เร็วมาก ต้องใช้ CFL < 0.5 หรือน้อยกว่า
2. **Stability:** Mass source term มักทำให้สมการ pressure ไม่เสถียร (Boundedness issue)
3. **Mismatched Thermodynamics:** เลือก Equation of State ไม่ตรงกับ physics (เช่น incompressible vs perfectGas)

## Related Skills

- **tutor-multiphase**: พื้นฐาน VOF/Euler-Euler ที่จำเป็นก่อนเรียนเรื่องนี้
- **tutor-openfoam-programming**: หากต้องการแก้ไข source code
