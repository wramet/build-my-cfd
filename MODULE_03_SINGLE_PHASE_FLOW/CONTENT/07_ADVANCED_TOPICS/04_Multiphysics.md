# Multiphysics Coupling

การเชื่อมโยงหลายฟิสิกส์ใน OpenFOAM

---

## Overview

| Coupling Type | Physics | Solver |
|---------------|---------|--------|
| FSI | Fluid + Structure | `pimpleFoam` + `solidDisplacementFoam` |
| CHT | Fluid + Solid heat | `chtMultiRegionFoam` |
| Reacting | Flow + Chemistry | `reactingFoam` |

---

## 1. Fluid-Structure Interaction (FSI)

### Interface Conditions

**Kinematic:** ความเร็ว fluid = ความเร็ว solid
$$\mathbf{u}_f = \frac{\partial \mathbf{d}_s}{\partial t}$$

**Dynamic:** แรงสมดุลที่ interface
$$\boldsymbol{\sigma}_f \cdot \mathbf{n} = \boldsymbol{\sigma}_s \cdot \mathbf{n}$$

### Coupling Strategies

| Approach | Method | Pros | Cons |
|----------|--------|------|------|
| **Weak** | Solve sequentially | Simple | May be unstable |
| **Strong** | Iterate to convergence | Stable | More expensive |
| **Monolithic** | Single system | Most stable | Complex |

### Coupling Schemes Visualization

```
┌─────────────────────────────────────────────────────────────────────┐
│                        WEAK COUPLING                                 │
│                        (One-way or loose)                            │
│                                                                     │
│  Fluid Domain                Solid Domain                           │
│  ┌─────────────┐            ┌─────────────┐                        │
│  │  Solve      │───────────►│  Solve      │  Single pass per    │
│  │  Fluid Eq.  │            │  Solid Eq.  │  time step           │
│  └─────────────┘            └─────────────┘                        │
│         ▲                         │                                │
│         │                         ▼                                │
│    Load data              No iteration                           │
│    (from previous)         (may be unstable)                      │
│                                                                     │
│    ✓ Simple  ✗ May diverge  ✗ Lower accuracy                      │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                        STRONG COUPLING                                │
│                        (Two-way with iteration)                      │
│                                                                     │
│  Fluid Domain                Solid Domain                           │
│  ┌─────────────┐            ┌─────────────┐                        │
│  │  Solve      │◄───────────│  Solve      │                        │
│  │  Fluid Eq.  │            │  Solid Eq.  │                        │
│  └─────────────┘            └─────────────┘                        │
│         ▲                         │                                │
│         │                         ▼                                │
│    Transfer data           Exchange data                          │
│    (loads, disp)           at interface                           │
│         │                         │                                │
│         └───────► ◄───────────────┘                                │
│                   Iterate                                         │
│         │                                                         │
│         ▼                                                         │
│    Converged?  ──No──►  Repeat                                   │
│         │                                                         │
│        Yes                                                        │
│         │                                                         │
│         ▼                                                         │
│    Next time step                                                 │
│                                                                     │
│    ✓ Stable  ✓ Higher accuracy  ✗ More expensive                  │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                        MONOLITHIC COUPLING                           │
│                        (Single matrix system)                       │
│                                                                     │
│           ┌───────────────────────────────────┐                    │
│           │                                   │                    │
│           │   [A_ff   A_fs] [U_f]   = [R_f]   │                    │
│           │   [A_sf   A_ss] [U_s]     [R_s]   │                    │
│           │                                   │                    │
│           │   Single coupled matrix solve     │                    │
│           │                                   │                    │
│           └───────────────────────────────────┘                    │
│                                                                     │
│    ✓ Most stable  ✓ Exact coupling  ✗ Very complex  ✗ Memory     │
└─────────────────────────────────────────────────────────────────────┘
```

### OpenFOAM Setup

```cpp
// constant/regionProperties
regions (fluid solid);

// 0/fluid/interface
type regionCoupledWall;
```

---

## 2. Conjugate Heat Transfer (CHT)

### Interface Conditions

$$T_{fluid} = T_{solid}$$
$$-k_f \frac{\partial T_f}{\partial n} = -k_s \frac{\partial T_s}{\partial n}$$

### Solver: `chtMultiRegionFoam`

```cpp
// constant/fluid/thermophysicalProperties
thermoType
{
    type    heRhoThermo;
    mixture pureMixture;
    transport const;
    thermo  hConst;
    equationOfState perfectGas;
    energy  sensibleEnthalpy;
}
```

### Interface BC

```cpp
// 0/fluid/T at interface
type    compressible::turbulentTemperatureCoupledBaffleMixed;
Tnbr    T;
kappaMethod fluidThermo;
```

---

## 3. Reacting Flows

### Species Transport

$$\frac{\partial (\rho Y_i)}{\partial t} + \nabla \cdot (\rho Y_i \mathbf{u}) = -\nabla \cdot \mathbf{J}_i + R_i$$

### Arrhenius Kinetics

$$k = A T^\beta \exp\left(-\frac{E_a}{RT}\right)$$

### Solver: `reactingFoam`

```cpp
// constant/reactions
reaction
{
    type    irreversible;
    reaction "H2 + 0.5 O2 => H2O";
    A       1.8e8;
    beta    0;
    Ta      4680;
}
```

---

## 4. Coupling Techniques

### Aitken Relaxation

เร่ง convergence สำหรับ partitioned coupling:

$$\omega^{n+1} = \omega^n \frac{\langle \mathbf{r}^{n-1} - \mathbf{r}^n, \mathbf{r}^n \rangle}{\|\mathbf{r}^{n-1} - \mathbf{r}^n\|^2}$$

### Data Transfer

| Method | Conservation | Accuracy |
|--------|--------------|----------|
| Nearest neighbor | Poor | Low |
| Linear interpolation | Moderate | Good |
| Mortar | Exact | Best |

---

## 5. Applications

| Application | Coupling | Solver |
|-------------|----------|--------|
| Heat exchanger | CHT | `chtMultiRegionFoam` |
| Flexible propeller | FSI | `pimpleFoam` + structural |
| Combustor | Reacting | `reactingFoam` |
| Electronics cooling | CHT | `chtMultiRegionFoam` |
| Wind turbine blade | FSI | External coupling (preCICE) |

---

## 6. Multi-Region Case Structure

```
case/
├── 0/
│   ├── fluid/
│   │   ├── U, p, T
│   └── solid/
│       └── T
├── constant/
│   ├── regionProperties
│   ├── fluid/
│   │   └── thermophysicalProperties
│   └── solid/
│       └── thermophysicalProperties
└── system/
    ├── fluid/
    │   └── fvSchemes, fvSolution
    └── solid/
        └── fvSchemes, fvSolution
```

---

## Concept Check

<details>
<summary><b>1. One-way vs Two-way FSI ต่างกันอย่างไร?</b></summary>

- **One-way**: Fluid affects structure แต่ structure ไม่ affect fluid กลับ (เช่น ลมปะทะป้ายแข็ง)
- **Two-way**: ทั้งสองฝั่งมีผลต่อกัน (เช่น ใบพัดที่โค้งงอ) — ต้อง iterate จน convergence
</details>

<details>
<summary><b>2. CHT interface conditions มีอะไรบ้าง?</b></summary>

1. **Temperature continuity**: $T_f = T_s$
2. **Heat flux continuity**: $q_f = q_s$ — พลังงานที่ออกจาก fluid = พลังงานที่เข้า solid
</details>

<details>
<summary><b>3. Partitioned vs Monolithic coupling ต่างกันอย่างไร?</b></summary>

- **Partitioned**: แยก solver (เช่น OpenFOAM + CalculiX) ส่งข้อมูลหากัน — ง่ายแต่อาจไม่เสถียร
- **Monolithic**: รวมทุกสมการใน matrix เดียว — เสถียรแต่ซับซ้อนมาก
</details>

---

## Related Documents

- **บทก่อนหน้า:** [03_Numerical_Methods.md](03_Numerical_Methods.md)
- **ภาพรวม:** [00_Overview.md](00_Overview.md)