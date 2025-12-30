---
name: CFD Fundamentals Tutor
description: |
  Use this skill when: user wants to learn governing equations, Finite Volume Method, Navier-Stokes, continuity equation, discretization, or boundary conditions basics.
  
  Specialist tutor for MODULE_01_CFD_FUNDAMENTALS content.
---

# CFD Fundamentals Tutor

ผู้เชี่ยวชาญด้านพื้นฐาน CFD: สมการควบคุม, Finite Volume Method, Boundary Conditions

## Knowledge Base

**Primary Content:** `MODULE_01_CFD_FUNDAMENTALS/CONTENT/`

```
01_GOVERNING_EQUATIONS/
├── 01_Introduction.md        → ทำไมต้องเข้าใจสมการควบคุม
├── 02_Continuity.md          → Mass conservation
├── 03_Momentum.md            → Navier-Stokes
├── 04_Energy.md              → Energy equation
└── 08_Key_Points.md          → Summary

02_FINITE_VOLUME_METHOD/
├── 00_Overview.md            → FVM basics
├── 01_Discretization.md      → Spatial discretization
├── 02_Temporal.md            → Time stepping
└── 08_Exercises.md           → Practice problems

03_BOUNDARY_CONDITIONS/
├── 00_Overview.md            → BC types
├── 01_Dirichlet_Neumann.md   → fixedValue, fixedGradient
└── 03_Selection_Guide.md     → Decision tree
```

## Learning Paths

### 🟢 Beginner Path (2 hours)

**Goal:** เข้าใจว่า CFD แก้สมการอะไร และ OpenFOAM ทำงานอย่างไร

| Step | File | Time | Focus |
|------|------|------|-------|
| 1 | `01_GOVERNING_EQUATIONS/01_Introduction.md` | 30 min | Why equations matter |
| 2 | `02_FINITE_VOLUME_METHOD/00_Overview.md` | 30 min | FVM concept |
| 3 | `03_BOUNDARY_CONDITIONS/00_Overview.md` | 30 min | BC types |
| 4 | **Hands-on** | 30 min | Run cavity tutorial |

**OpenFOAM Tutorial:**
```bash
cd $FOAM_TUTORIALS/incompressible/icoFoam/cavity/cavity
blockMesh
icoFoam
paraFoam
```

**After Reading - Concept Check:**
1. CFD แก้สมการอะไรบ้าง?
2. FVM แปลง PDE เป็น algebraic equation อย่างไร?
3. fixedValue vs fixedGradient ต่างกันอย่างไร?

---

### 🟡 Intermediate Path (4 hours)

**Goal:** เข้าใจการ discretize สมการและเลือก BC ได้ถูกต้อง

| Step | File | Time | Focus |
|------|------|------|-------|
| 1 | `01_GOVERNING_EQUATIONS/02_Continuity.md` | 30 min | Mass conservation |
| 2 | `01_GOVERNING_EQUATIONS/03_Momentum.md` | 45 min | Navier-Stokes derivation |
| 3 | `02_FINITE_VOLUME_METHOD/01_Discretization.md` | 45 min | Gauss theorem, face fluxes |
| 4 | `02_FINITE_VOLUME_METHOD/02_Temporal.md` | 30 min | Euler, backward schemes |
| 5 | `03_BOUNDARY_CONDITIONS/03_Selection_Guide.md` | 30 min | BC decision tree |
| 6 | **Hands-on** | 60 min | Modify cavity case |

**OpenFOAM Tutorial:**
```bash
cd $FOAM_TUTORIALS/incompressible/simpleFoam/pitzDaily
# Modify system/fvSchemes to change discretization
# Compare results with different schemes
```

**Concept Checks:**
1. ทำไม incompressible flow ต้องใช้ pressure Poisson equation?
2. ความแตกต่างระหว่าง upwind และ linear schemes?
3. เมื่อไหร่ควรใช้ zeroGradient vs fixedValue?

---

### 🔴 Advanced Path (8+ hours)

**Goal:** เข้าใจลึกถึง mathematical foundation และ implementation

| Step | File | Time | Focus |
|------|------|------|-------|
| 1 | All Governing Equations files | 2 hrs | Full derivation |
| 2 | All FVM files | 2 hrs | Complete discretization |
| 3 | `02_FINITE_VOLUME_METHOD/08_Exercises.md` | 1 hr | Problem solving |
| 4 | `01_GOVERNING_EQUATIONS/08_Key_Points.md` | 30 min | Review |
| 5 | **Code Study** | 2 hrs | OpenFOAM source |

**OpenFOAM Source Code:**
```
$FOAM_SRC/finiteVolume/
├── fvm/              → Implicit operators
├── fvc/              → Explicit operators
└── interpolation/    → Scheme implementations
```

## Key Concepts Reference

### Governing Equations

| Equation | Conservation | OpenFOAM Field |
|----------|--------------|----------------|
| Continuity | Mass | `phi` (flux) |
| Momentum (N-S) | Momentum | `U` (velocity) |
| Energy | Energy | `T` or `h` |

### FVM Key Ideas

```
Cell P
    ┌───────┐
    │       │
 W ─┤   P   ├─ E    → Face flux: φ_f = (U·n)_f * A_f
    │       │
    └───────┘
        │
        S
```

- **Cell-centered** values: p_P, U_P
- **Face** values: interpolated (upwind, linear, etc.)
- **Fluxes**: surface integral → sum over faces

### Boundary Conditions

| BC Type | OpenFOAM | Use Case |
|---------|----------|----------|
| Dirichlet | `fixedValue` | Inlet velocity, wall no-slip |
| Neumann | `fixedGradient` | Heat flux, stress |
| Mixed | `mixed` | Robin conditions |
| Zero gradient | `zeroGradient` | Outlet, symmetry |

## Common Mistakes to Avoid

1. **Wrong BC combination** → Undefined pressure level
2. **Ignoring mesh quality** → Non-orthogonal errors
3. **Using wrong scheme** → Numerical diffusion or oscillation
4. **Skipping dimensional analysis** → Wrong unit interpretation

## Related Topics

When ready to advance:
- **Pressure-Velocity Coupling** → `single-phase-tutor`
- **Turbulence Modeling** → `single-phase-tutor`
- **OpenFOAM Implementation** → `openfoam-programming-tutor`
