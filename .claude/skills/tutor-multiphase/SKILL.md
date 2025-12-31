---
name: Multiphase Flow Tutor
description: |
  Use this skill when: user wants to learn multiphase flow, VOF method, Euler-Euler method, interphase forces, interFoam, multiphaseEulerFoam, or bubble/droplet simulations.
  
  Specialist tutor for MODULE_04_MULTIPHASE_FUNDAMENTALS content.
---

# Multiphase Flow Tutor

ผู้เชี่ยวชาญด้าน Multiphase Flow: VOF, Euler-Euler, Interphase Forces

## Knowledge Base

**Primary Content:** `MODULE_04_MULTIPHASE_FUNDAMENTALS/CONTENT/`

```
01_FUNDAMENTAL_CONCEPTS/
├── 00_Overview.md              → Classification, α, solver selection
├── 01_Flow_Regimes.md          → Bubbly, slug, annular
└── 02_Interfacial_Phenomena.md → Surface tension, contact angle

02_VOF_METHOD/
├── 00_Overview.md              → VOF concept
├── 01_The_VOF_Concept.md       → α equation
├── 02_Interface_Compression.md → MULES, Cα
├── 03_Setting_Up_InterFoam.md  → Case setup
└── 04_Adaptive_Time.md         → maxAlphaCo

03_EULER_EULER_METHOD/
├── 00_Overview.md              → Two-fluid model
├── 02_Mathematical_Framework.md → Conservation equations
└── 03_Implementation.md        → phaseProperties

04_INTERPHASE_FORCES/
├── 01_DRAG/                    → Drag models
├── 02_LIFT/                    → Lift models
├── 03_VIRTUAL_MASS/            → Added mass
└── 04_TURBULENT_DISPERSION/    → TD models

05_MODEL_SELECTION/
├── 01_Decision_Framework.md    → How to choose
├── 02_Gas_Liquid_Systems.md    → Bubbly, free surface
└── 04_Gas_Solid_Systems.md     → Fluidized beds

07_VALIDATION/
├── 02_Benchmark_Problems.md    → Standard cases
└── 03_Grid_Convergence.md      → GCI for multiphase
```

## Learning Paths

### 🟢 Beginner: "ฉันอยากจำลอง free surface flow"

**Goal:** ตั้งค่า VOF simulation ได้

| Step | File | Time | Focus |
|------|------|------|-------|
| 1 | `01_FUNDAMENTAL.../00_Overview.md` | 30 min | α concept, solver types |
| 2 | `02_VOF_METHOD/00_Overview.md` | 30 min | VOF basics |
| 3 | `02_VOF_METHOD/03_Setting_Up_InterFoam.md` | 45 min | Case setup |
| 4 | **Hands-on** | 45 min | damBreak tutorial |

**Tutorial:**
```bash
cd $FOAM_TUTORIALS/multiphase/interFoam/laminar/damBreak
./Allrun
paraFoam  # Look at alpha.water field
```

**Key Files to Understand:**
```
constant/
├── transportProperties    → sigma, rho, nu per phase
├── g                      → gravity vector
└── turbulenceProperties   → laminar or RAS

0/
├── alpha.water            → Initial phase distribution
├── U                      → Velocity BC
└── p_rgh                  → Dynamic pressure
```

**Concept Checks:**
1. α = 0.5 หมายความว่าอย่างไร?
2. MULES algorithm ทำหน้าที่อะไร?
3. ทำไมต้องใช้ p_rgh แทน p?

---

### 🟡 Intermediate: "ฉันอยากจำลอง bubbly flow"

**Goal:** เข้าใจ Euler-Euler method และ interphase forces

| Step | File | Time | Focus |
|------|------|------|-------|
| 1 | `01_FUNDAMENTAL.../01_Flow_Regimes.md` | 30 min | When to use Euler-Euler |
| 2 | `03_EULER_EULER/00_Overview.md` | 30 min | Two-fluid concept |
| 3 | `04_INTERPHASE.../01_DRAG/00_Overview.md` | 30 min | Drag models |
| 4 | `05_MODEL_SELECTION/01_Decision.md` | 30 min | Solver selection |
| 5 | **Hands-on** | 60 min | bubbleColumn tutorial |

**Tutorial:**
```bash
cd $FOAM_TUTORIALS/multiphase/twoPhaseEulerFoam/RAS/bubbleColumn
./Allrun
```

**phaseProperties Key Settings:**
```cpp
phases (air water);

air
{
    diameterModel constant;
    d             3e-3;        // Bubble diameter
}

drag (air in water)
{
    type            SchillerNaumann;
}

virtualMass (air in water)
{
    type            constantCoefficient;
    Cvm             0.5;
}
```

---

### 🔴 Advanced: "ฉันต้องการ custom drag model"

**Goal:** เข้าใจ interphase force implementation และ coding

| Step | File | Time | Focus |
|------|------|------|-------|
| 1 | `04_INTERPHASE.../01_DRAG/03_OpenFOAM_Implementation.md` | 45 min | Drag code |
| 2 | `04_INTERPHASE.../02_LIFT/03_OpenFOAM_Implementation.md` | 45 min | Lift code |
| 3 | `03_EULER_EULER/03_Implementation.md` | 45 min | phaseSystem architecture |
| 4 | **Code Study** | 2 hrs | Source code analysis |

**Source Code Locations:**
```
$FOAM_SOLVERS/multiphase/
├── interFoam/                    → VOF solver
└── multiphaseEulerFoam/
    └── phaseSystems/
        └── interfacialModels/
            ├── dragModels/       → Drag implementations
            ├── liftModels/       → Lift implementations
            └── virtualMassModels/
```

---

## Solver Selection Guide

| Flow Type | Solver | When to Use |
|-----------|--------|-------------|
| Free surface | `interFoam` | Dam break, sloshing, waves |
| Bubbly flow | `twoPhaseEulerFoam` | Bubble columns, dense dispersions |
| Multiple liquids | `multiphaseInterFoam` | Oil-water, 3+ phases |
| Particles | `DPMFoam` | Dilute suspensions |
| Phase change | `compressibleInterFoam` | Boiling, cavitation |

## Key Parameters

### VOF Settings (interFoam)

| Parameter | Location | Typical Value |
|-----------|----------|---------------|
| `maxAlphaCo` | controlDict | 0.3-0.5 |
| `nAlphaSubCycles` | fvSolution | 1-4 |
| `Cα` | fvSchemes | 0-1 (interface compression) |
| `sigma` | transportProperties | surface tension |

### Euler-Euler Settings

| Parameter | Location | Typical Value |
|-----------|----------|---------------|
| `d` | phaseProperties | bubble/particle diameter |
| `drag type` | phaseProperties | SchillerNaumann, IshiiZuber |
| `Cvm` | phaseProperties | 0.5 (spheres) |

## Common Mistakes

| Mistake | Consequence | Fix |
|---------|-------------|-----|
| Wrong phase order | Inverted α | Check `phases (a b)` order |
| Large time step | Interface smearing | Reduce maxAlphaCo |
| No gravity | No buoyancy | Add g file |
| Wrong BC for α | Non-physical | Use `inletOutlet` at outlets |

## Related Topics

- **CFD Fundamentals** → `cfd-fundamentals` tutor
- **Single-Phase Turbulence** → `single-phase-tutor`
- **OpenFOAM Programming** → `openfoam-programming-tutor`
