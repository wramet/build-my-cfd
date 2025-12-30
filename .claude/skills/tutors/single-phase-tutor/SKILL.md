---
name: Single Phase Flow Tutor
description: |
  Use this skill when: user wants to learn pressure-velocity coupling, SIMPLE/PISO/PIMPLE algorithms, turbulence modeling, heat transfer, or incompressible flow simulation.
  
  Specialist tutor for MODULE_03_SINGLE_PHASE_FLOW content.
---

# Single Phase Flow Tutor

ผู้เชี่ยวชาญด้าน Single-Phase Flow: P-V Coupling, Turbulence, Heat Transfer

## Knowledge Base

**Primary Content:** `MODULE_03_SINGLE_PHASE_FLOW/CONTENT/`

```
01_INCOMPRESSIBLE_FLOW_SOLVERS/
├── 00_Overview.md              → Solver selection
├── 02_Standard_Solvers.md      → simpleFoam, pisoFoam, pimpleFoam
└── 03_Simulation_Control.md    → controlDict, fvSchemes, fvSolution

02_PRESSURE_VELOCITY_COUPLING/
├── 00_Overview.md              → P-V coupling problem
├── 01_Mathematical_Foundation.md → Pressure Poisson
├── 02_SIMPLE_Algorithm.md      → SIMPLE details
├── 03_PISO_and_PIMPLE.md       → Transient algorithms
├── 04_Rhie_Chow.md             → Collocated grid
└── 05_Algorithm_Comparison.md  → Selection guide

03_TURBULENCE_MODELING/
├── 00_Overview.md              → Turbulence basics
├── 01_Turbulence_Fundamentals.md → Energy cascade
├── 02_RANS_Models.md           → k-ε, k-ω, SST
├── 03_Wall_Treatment.md        → y+ guidelines
└── 04_LES_Fundamentals.md      → Large Eddy Simulation

04_HEAT_TRANSFER/
├── 00_Overview.md              → Heat transfer overview
├── 01_Energy_Equation.md       → Energy equation
├── 03_Buoyancy_Driven.md       → Natural convection
└── 04_Conjugate_Heat.md        → CHT

05_PRACTICAL_APPLICATIONS/
├── 01_External_Aerodynamics.md → Ahmed body, airfoils
├── 02_Internal_Flow.md         → Pipe flow
└── 03_Heat_Exchangers.md       → STHE design

06_VALIDATION_AND_VERIFICATION/
├── 01_V_and_V_Principles.md    → V&V framework
├── 02_Mesh_Independence.md     → GCI, Richardson
└── 03_Experimental_Validation.md → Comparison

07_ADVANCED_TOPICS/
├── 01_HPC.md                   → Parallel computing
├── 02_Advanced_Turbulence.md   → Hybrid RANS-LES
└── 03_Numerical_Methods.md     → Schemes, stability
```

## Learning Paths

### 🟢 Beginner: "ทำไม simulation ถึง diverge?"

**Goal:** เข้าใจ P-V coupling และตั้งค่า solver ได้

| Step | File | Time | Focus |
|------|------|------|-------|
| 1 | `02_PRESSURE_VELOCITY_COUPLING/00_Overview.md` | 30 min | The coupling problem |
| 2 | `01_INCOMPRESSIBLE_FLOW_SOLVERS/02_Standard_Solvers.md` | 30 min | Solver selection |
| 3 | `01_INCOMPRESSIBLE_FLOW_SOLVERS/03_Simulation_Control.md` | 30 min | fvSolution settings |
| 4 | **Hands-on** | 30 min | Fix diverging case |

**Tutorial:**
```bash
cd $FOAM_TUTORIALS/incompressible/simpleFoam/pitzDaily
# Try reducing relaxation factors if diverging
# Edit system/fvSolution
```

**Concept Checks:**
1. ทำไม incompressible flow ไม่มี pressure equation โดยตรง?
2. SIMPLE vs PISO ต่างกันอย่างไร?
3. relaxation factor ทำหน้าที่อะไร?

---

### 🟡 Intermediate: "ฉันอยากเข้าใจ turbulence modeling"

**Goal:** เลือก turbulence model และ wall treatment ได้ถูกต้อง

| Step | File | Time | Focus |
|------|------|------|-------|
| 1 | `03_TURBULENCE_MODELING/01_Turbulence_Fundamentals.md` | 45 min | Energy cascade, RANS |
| 2 | `03_TURBULENCE_MODELING/02_RANS_Models.md` | 45 min | k-ε, k-ω, SST |
| 3 | `03_TURBULENCE_MODELING/03_Wall_Treatment.md` | 45 min | y+ guidelines |
| 4 | `02_PRESSURE_VELOCITY_COUPLING/03_PISO_and_PIMPLE.md` | 30 min | Transient simulation |
| 5 | **Hands-on** | 60 min | Compare models |

**Tutorial:**
```bash
cd $FOAM_TUTORIALS/incompressible/simpleFoam/motorBike
# Compare kEpsilon vs kOmegaSST
# Check y+ values with yPlus utility
```

**y+ Guidelines:**
| Model | Wall Function | Resolved |
|-------|---------------|----------|
| k-ε standard | 30 < y+ < 300 | Not recommended |
| k-ω SST | 1 < y+ < 5 | y+ < 1 |
| Spalart-Allmaras | 1 < y+ < 5 | y+ < 1 |

---

### 🔴 Advanced: "ฉันต้องการ validate simulation"

**Goal:** ทำ mesh independence study และ compare กับ experimental data

| Step | File | Time | Focus |
|------|------|------|-------|
| 1 | `06_VALIDATION.../01_V_and_V_Principles.md` | 45 min | V&V framework |
| 2 | `06_VALIDATION.../02_Mesh_Independence.md` | 60 min | GCI, Richardson |
| 3 | `05_PRACTICAL.../01_External_Aerodynamics.md` | 45 min | Ahmed body validation |
| 4 | `07_ADVANCED.../02_Advanced_Turbulence.md` | 60 min | Hybrid RANS-LES |
| 5 | **Project** | 3+ hrs | Full validation study |

**GCI Calculation Steps:**
1. Run 3 mesh levels (coarse, medium, fine)
2. Compute refinement ratio r = h_coarse / h_fine
3. Calculate order of convergence p
4. Compute GCI = F_s * |ε| / (r^p - 1)

---

## Algorithm Quick Reference

### SIMPLE vs PISO vs PIMPLE

| Feature | SIMPLE | PISO | PIMPLE |
|---------|--------|------|--------|
| Type | Steady | Transient | Transient |
| Under-relaxation | Required | Not needed | Optional |
| Max Co | ∞ | < 1 | > 1 OK |
| Typical solver | simpleFoam | pisoFoam | pimpleFoam |

### fvSolution Template

```cpp
// For SIMPLE
SIMPLE
{
    nNonOrthogonalCorrectors 1;
    residualControl
    {
        p       1e-5;
        U       1e-5;
    }
}
relaxationFactors
{
    fields { p 0.3; }
    equations { U 0.7; }
}

// For PIMPLE
PIMPLE
{
    nOuterCorrectors    3;
    nCorrectors         2;
    nNonOrthogonalCorrectors 1;
}
```

## Troubleshooting

| Problem | Common Cause | Solution |
|---------|--------------|----------|
| Divergence at start | Bad initialization | Use potentialFoam first |
| Oscillating residuals | Mesh non-orthogonality | Increase nNonOrthCorr |
| Slow convergence | Relaxation too low | Gradually increase α |
| Wrong Cd/Cl | y+ out of range | Re-mesh near walls |

## OpenFOAM Solvers

| Solver | Physics | Use Case |
|--------|---------|----------|
| `simpleFoam` | Steady incompressible | RANS aerodynamics |
| `pisoFoam` | Transient incompressible | LES, DNS |
| `pimpleFoam` | Transient incompressible | Large Δt, moving mesh |
| `buoyantSimpleFoam` | Steady + buoyancy | Natural convection |
| `chtMultiRegionFoam` | Conjugate heat transfer | CHT problems |

## Related Topics

When ready to advance:
- **Multiphase Flow** → `multiphase-tutor`
- **OpenFOAM C++ Programming** → `openfoam-programming-tutor`
- **Mesh Quality** → see MODULE_02
