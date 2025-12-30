# ประเด็นสำคัญที่ควรจดจำ

> **📌 Learning Objectives**
> - เข้าใจความสัมพันธ์ระหว่างแนวคิดทางทฤษฎีกับการนำไปใช้ใน OpenFOAM
> - สามารถเลือก solver, algorithm, และ boundary conditions ที่เหมาะสมกับปัญหา
> - ใช้ checklist ตรวจสอบการตั้งค่าก่อนรัน simulation

> **ทำไมต้องอ่านบทสรุปนี้?**
> - **Quick reference** สำหรับทบทวนก่อนทำงานจริง
> - รวมทุกสิ่งที่ต้องรู้ใน **1 หน้า**
> - มี **checklist** พร้อมใช้งานพร้อมคำสั่ง OpenFOAM
> - **Concept map** เชื่อมโยงความสัมพันธ์ระหว่างหัวข้อ

---

## 🗺️ Concept Map: Flow Regime Decision Tree

```
                ┌─────────────────────────────────────┐
                │     คำนวณ Mach Number (Ma = U/c)     │
                └─────────────────┬───────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                Ma < 0.3                        Ma > 0.3
                    │                               │
            ┌───────┴────────┐            ┌─────────┴─────────┐
            │  Incompressible│            │   Compressible   │
            │                │            │                   │
    ┌───────┴────────┐      │    ┌───────┴────────┐   ┌─────┴──────┐
    │                │      │    │                │   │            │
ρ = constant    Ideal Gas   │    Ideal Gas      Real Gas     ...
    │                │      │    │                │   │            │
┌───┴────┐     ┌────┴────┐  │  ┌──┴──────┐   ┌────┴──┐ ┌──┴─────┐ ┌─┴──┐
│        │     │         │  │  │         │   │       │ │        │ │    │
simple  rho    buoyant  ... │  rhoCentral  rhoPimp|le  sonic ...
Foam   Simple  Simple    │  Foam       Foam     Foam
    │                │      │    │                │   │            │
    └───────┬────────┘      │    └────────────────┘   └────────────┘
            │               │
    ┌───────┴────────────────┴──────────────┐
    │     คำนวณ Reynolds Number (Re = ρUL/μ)   │
    └───────────────┬────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
    Re < 2300              Re > 4000
        │                       │
    ┌───┴────┐            ┌──────┴──────┐
    │        │            │             │
 Laminar  Transition   Turbulent
    │        │            │             │
 laminar   ...      kEpsilon  kOmegaSST  LES
                        │             │
                        └──────┬──────┘
                               │
                    ┌──────────┴──────────┐
                    │  ตรวจสอบ y+ ที่ผนัง  │
                    └──────────┬──────────┘
                               │
                  ┌────────────┴────────────┐
                  │                         │
            y+ < 5                  30 < y+ < 300
            (Low-Re)               (Wall Function)
                  │                         │
            Resolve all            Use wall functions
          boundary layers         for k, epsilon, omega
```

---

## 📚 Quick Equation Reference

### Conservation Laws (1-Line Summary)

| กฎการอนุรักษ์ | สมการ | OpenFOAM Implementation |
|---------------|---------|----------------------|
| **มวล (Mass)** | $\nabla \cdot \mathbf{u} = 0$ | Constraint (ไม่มี solver โดยตรง) |
| **โมเมนตัม (Momentum)** | $\rho \frac{D\mathbf{u}}{Dt} = -\nabla p + \mu \nabla^2 \mathbf{u} + \mathbf{f}$ | `UEqn.H`: `fvm::div(phi, U) - fvm::laplacian(nu, U)` |
| **พลังงาน (Energy)** | $\rho c_p \frac{DT}{Dt} = k \nabla^2 T + Q$ | `TEqn.H`: `fvm::div(phi, T) - fvm::laplacian(alpha, T)` |

### General Transport Equation (Template)

$$\boxed{\frac{\partial (\rho \phi)}{\partial t} + \nabla \cdot (\rho \phi \mathbf{u}) = \nabla \cdot (\Gamma \nabla \phi) + S_\phi}$$

**OpenFOAM Translation:**
```cpp
// รูปแบบมาตรฐานในทุก solver
solve
(
    fvm::ddt(phi)                  // ∂/∂t
  + fvm::div(phi, phi)             // ∇·(ϕu)
  - fvm::laplacian(Gamma, phi)    // ∇·(Γ∇ϕ)
 ==
    Su                              // Source term
);
```

---

## 🔗 Concept Flow: Reynolds Number → Turbulence → Wall Treatment → BCs

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    REYNOLDS NUMBER (Re = ρUL/μ)                        │
│                  ดูรายละเอียด: 04_Dimensionless_Numbers.md          │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
        Re < 2300                      Re > 4000
        (Laminar)                     (Turbulent)
              │                             │
              │                    ┌────────┴────────┐
              │                    │                 │
              │              k-Epsilon      k-Omega SST  LES
              │                    │                 │
              └────────────────────┼─────────────────┘
                                   │
┌──────────────────────────────────┴─────────────────────────────────────┐
│                      WALL TREATMENT (y+ Calculation)                  │
│             ดูรายละเอียด: 04_Dimensionless_Numbers.md#y-plus        │
│                  ดูรายละเอียด: 06_Boundary_Conditions.md#walls      │
└────────────────────────────┬──────────────────────────────────────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
          y+ < 5                 30 < y+ < 300
      (Viscous Sublayer)       (Log-Law Region)
                │                         │
    ┌───────────┴───────────┐   ┌─────────┴─────────┐
    │                       │   │                   │
 Resolve all              Use   Low-Re          Wall
boundary layers        Wall Functions  Models     Functions
 (y+ < 1)               (y+ ~ 30-100)     (y+ < 1)   (y+ ~ 30-300)
    │                       │   │                   │
    └───────────────────────┼───┼───────────────────┘
                            │   │
┌───────────────────────────┴───┴───────────────────────────────────────┐
│                   BOUNDARY CONDITIONS SELECTION                       │
│             ดูรายละเอียด: 06_Boundary_Conditions.md                │
└────────────────────────────┬──────────────────────────────────────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
           Low-Re Wall              High-Re Wall
            Treatment               Treatment
                │                         │
    ┌───────────┴───────────┐   ┌─────────┴─────────┐
    │                       │   │                   │
 U: noSlip              U: noSlip        U: noSlip
 k: zeroGradient        k: kqWallFunct   k: epsilonWallFunct
omega: fixedValue (small) omega: omegaWallFunct
epsilon: zeroGradient   epsilon: epsilonWallFunct
```

---

## 🎯 Pressure-Velocity Coupling: Visual Selection Guide

```
┌─────────────────────────────────────────────────────────────┐
│                  ปัญหาของ Incompressible Flow              │
│         "ความดันไม่มีสมการ - เป็น constraint"           │
│                                                             │
│  ความดันทำหน้าที่บังคับให้ ∇·u = 0 (continuity)       │
└────────────────────────┬────────────────────────────────────┘
                         │
            ┌────────────┴────────────┐
            │                         │
      Steady-State              Transient
            │                         │
    ┌───────┴───────┐       ┌────────┴────────┐
    │               │       │                 │
  SIMPLE          PIMPLE   PISO            PIMPLE
 (Standard)    (Hybrid) (Standard)      (Robust)
    │               │       │                 │
    │           สำหรับ      │         สำหรับ Δt
    │           Δt ใหญ่     │          ใหญ่ได้
    │                       │
    ▼                       ▼
┌─────────┐           ┌─────────┐
│  1 pass │           │ Outer   │
│  per IT │           │ loop    │
│         │           │ (PISO)  │
│         │           │ +       │
│         │           │ Under-  │
│         │           │ relax   │
└─────────┘           └─────────┘
```

**Algorithm Comparison Table:**

| Algorithm | Type | Under-Relaxation | Use Case | OpenFOAM Keyword |
|-----------|------|------------------|-----------|------------------|
| **SIMPLE** | Steady-state | Required | Fast steady-state solutions | `SIMPLE` in `fvSolution` |
| **PISO** | Transient | Not needed | Small time steps, accurate transients | `PISO` in `fvSolution` |
| **PIMPLE** | Transient | Optional | Large time steps, robust | `PIMPLE` in `fvSolution` |

---

## 📋 Learning Objectives Quick Reference

| ไฟล์ | Learning Objective | Link |
|------|-------------------|------|
| **01** | อธิบายความสำคัญของสมการควบคุมและการลดรูป | [01_Introduction.md](01_Introduction.md) |
| **02** | อนุมานสมการควบคุมจากหลักการอนุรักษ์ | [02_Conservation_Laws.md](02_Conservation_Laws.md) |
| **03** | เลือก EOS ที่เหมาะสมกับปัญหา | [03_Equation_of_State.md](03_Equation_of_State.md) |
| **04** | คำนวณเลขไร้มิติและวิเคราะห์ flow regime | [04_Dimensionless_Numbers.md](04_Dimensionless_Numbers.md) |
| **05** | แปลสมการเป็น OpenFOAM syntax | [05_OpenFOAM_Implementation.md](05_OpenFOAM_Implementation.md) |
| **06** | เลือกและตั้งค่า boundary conditions | [06_Boundary_Conditions.md](06_Boundary_Conditions.md) |
| **07** | ตั้งค่าเริ่มต้นที่เหมาะสม | [07_Initial_Conditions.md](07_Initial_Conditions.md) |

---

## 🔢 State Equation → Solver Selection Decision Tree

```
┌─────────────────────────────────────────────────────────────────┐
│              Equation of State (EOS)                            │
│           ดูรายละเอียด: 03_Equation_of_State.md             │
└────────────────────────┬────────────────────────────────────────┘
                         │
            ┌────────────┴────────────┐
            │                         │
    Incompressible              Compressible
    (ρ = constant)              (ρ = f(p,T))
            │                         │
    ┌───────┴────────┐       ┌────────┴────────┐
    │                │       │                 │
 Isothermal      Thermal   Ideal Gas       Real Gas
    │                │       │                 │
    ▼                ▼       ▼                 ▼
┌─────────┐    ┌─────────┐ ┌─────────┐   ┌─────────┐
│simple   │    │buoyant  │ │rho      │   │rho      │
│Foam     │    │SimpleFoam│ │Simple   │   │Pimple   │
└─────────┘    └─────────┘ └─────────┘   └─────────┘
    │                │       │               │
    └────────────────┴───────┴───────────────┘
                     │
            ┌────────┴────────┐
            │                 │
      Steady-State      Transient
            │                 │
    ┌───────┴───────┐ ┌───────┴────────┐
    │               │ │                │
  SIMPLE          PIMPLE          PIMPLE/PISO
    │               │ │                │
```

**Quick Solver Selection:**

| Flow Type | Mach | Thermal | Solver |
|-----------|------|---------|--------|
| Incompressible, steady | < 0.3 | ❌ | `simpleFoam` |
| Incompressible, steady | < 0.3 | ✅ | `buoyantSimpleFoam` |
| Incompressible, transient | < 0.3 | ❌ | `pimpleFoam` |
| Compressible, steady | > 0.3 | ❌ | `rhoSimpleFoam` |
| Compressible, transient | > 0.3 | ❌ | `rhoPimpleFoam` |
| Compressible, transient | > 0.3 | ✅ | `rhoPimpleThermoFoam` |

---

## 🔤 Mathematics → OpenFOAM Translation

### fvm vs fvc: Visual Explanation

```
┌─────────────────────────────────────────────────────────────────┐
│                    fvm (Finite Volume Method)                    │
│                    Implicit Discretization                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                    ┌────┴────┐
                    │ Matrix  │
                    │ A·x = b │
                    └────┬────┘
                         │
            ┌────────────┴────────────┐
            │                         │
      ∂ϕ/∂t (ddt)           ∇·(ϕu) (div)      ∇²ϕ (laplacian)
         │                      │                  │
    fvm::ddt(ϕ)          fvm::div(ϕ, U)     fvm::laplacian(Γ, ϕ)
         │                      │                  │
    ┌────┴────┐            ┌─────┴─────┐      ┌──────┴──────┐
    │ Coeff.  │            │ Coeff.    │      │  Coeff.    │
    │ ใน A     │            │ ใน A       │      │   ใน A      │
    └────┬────┘            └─────┬─────┘      └──────┬──────┘
         │                      │                  │
         └──────────────────────┼──────────────────┘
                                │
                        สร้างระบบสมการเชิงเส้น
                        แก้ด้วย linear solver
```

```
┌─────────────────────────────────────────────────────────────────┐
│                    fvc (Finite Volume Calculus)                 │
│                    Explicit Calculation                          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                    ┌────┴────┐
                    │  Field  │
                    │   ϕ     │
                    │ (known) │
                    └────┬────┘
                         │
            ┌────────────┴────────────┐
            │                         │
      ∇p (grad)             ∇·ϕ (div)      ∇²ϕ (laplacian)
         │                      │                  │
    fvc::grad(p)          fvc::div(ϕ)         fvc::laplacian(Γ, ϕ)
         │                      │                  │
    ┌────┴────┐            ┌─────┴─────┐      ┌──────┴──────┐
    │ คำนวณ  │            │  คำนวณ    │      │   คำนวณ     │
    │ ค่าทันที│            │  ค่าทันที  │      │   ค่าทันที  │
    └────┬────┘            └─────┬─────┘      └──────┬──────┘
         │                      │                  │
         └──────────────────────┼──────────────────┘
                                │
                        ใช้ค่าที่คำนวณได้
                        เป็น source term
```

### Complete Translation Table

| Operator | Mathematical | fvm (Implicit) | fvc (Explicit) | Use In |
|----------|--------------|----------------|----------------|--------|
| Time derivative | $\frac{\partial \phi}{\partial t}$ | `fvm::ddt(phi)` | `fvc::ddt(phi)` | Transient term |
| Convection | $\nabla \cdot (\phi \mathbf{u})$ | `fvm::div(phi, U)` | `fvc::div(phi)` | Momentum, Energy |
| Diffusion | $\nabla^2 \phi$ | `fvm::laplacian(D, phi)` | `fvc::laplacian(D, phi)` | Viscous, Heat |
| Gradient | $\nabla p$ | — | `fvc::grad(p)` | Pressure force |
| Divergence | $\nabla \cdot \mathbf{u}$ | — | `fvc::div(U)` | Continuity check |

### Configuration Files

| Schemes | File | Controls |
|---------|------|----------|
| `ddtSchemes` | `system/fvSchemes` | Time discretization |
| `divSchemes` | `system/fvSchemes` | Convection schemes |
| `laplacianSchemes` | `system/fvSchemes` | Diffusion schemes |
| `gradSchemes` | `system/fvSchemes` | Gradient calculation |
| `interpolationSchemes` | `system/fvSchemes` | Face interpolation |
| `snGradSchemes` | `system/fvSchemes` | Surface normal gradient |

---

## 🚪 Boundary Conditions: Visual Pairing Guide

```
┌─────────────────────────────────────────────────────────────────┐
│              BOUNDARY CONDITION PAIRING LOGIC                   │
│          ดูรายละเอียด: 06_Boundary_Conditions.md             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                ┌────────┴────────┐
                │                 │
          Dirichlet          Neumann
        (Fixed Value)    (Zero Gradient)
           รู้ค่าที่ขอบ      รู้ความชัน = 0
                │                 │
                │                 │
        ┌───────┴─────────┬───────┴──────────┐
        │                │                  │
    INLET           WALL              OUTLET
        │                │                  │
    ┌───┴───┐        ┌───┴───┐         ┌───┴───┐
    │       │        │       │         │       │
  U:     U:       U:      U:       U:
 fixed  noSlip   noSlip  zeroGrad zeroGrad
 Value                      (or
                            inletOutlet)
    │       │        │       │         │
  p:     p:       p:      p:       p:
 zero   zero    zero    fixed   fixed
 Grad   Grad    Grad    Value   Value
```

### Standard BC Pairs

| ตำแหน่ง | U (Velocity) | p (Pressure) | k | epsilon/omega | เหตุผล |
|---------|--------------|--------------|---|---------------|---------|
| **Inlet** | `fixedValue` | `zeroGradient` | `fixedValue` | `fixedValue` | กำหนด flow rate |
| **Outlet** | `zeroGradient` | `fixedValue` | `zeroGradient` | `zeroGradient` | กำหนด pressure level |
| **Wall (No-slip)** | `noSlip` | `zeroGradient` | `kqWallFunction` | `epsilonWallFunction` | ไม่มี flow เลย |
| **Wall (Slip)** | `slip` | `zeroGradient` | `zeroGradient` | `zeroGradient` | ไหลได้ตามแนวผนัง |
| **Symmetry** | `symmetry` | `symmetry` | `symmetry` | `symmetry` | สมมาตร |

### Common BC Types in OpenFOAM

| Type | OpenFOAM Name | Description | Use Case |
|------|---------------|-------------|----------|
| Dirichlet | `fixedValue` | Fixed value at boundary | Inlet velocity, wall temperature |
| Neumann | `zeroGradient` | $\partial\phi/\partial n = 0$ | Outlet velocity, wall pressure |
| Mixed | `inletOutlet` | Dirichlet if inflow, Neumann if outflow | Outlet with possible backflow |
| Calculated | `calculated` | Calculated from other fields | Pressure in some solvers |
| Wall Function | `kqWallFunction` | Wall function for k-epsilon | Turbulent wall (y+ ~ 30-100) |
| Wall Function | `omegaWallFunction` | Wall function for k-omega | Turbulent wall (y+ ~ 30-100) |

---

## 🏁 Initial Conditions: Best Practices

```
┌─────────────────────────────────────────────────────────────────┐
│                 INITIAL CONDITIONS STRATEGY                     │
│          ดูรายละเอียด: 07_Initial_Conditions.md              │
└────────────────────────┬────────────────────────────────────────┘
                         │
            ┌────────────┴────────────┐
            │                         │
      Steady-State              Transient
            │                         │
    ┌───────┴───────┐       ┌────────┴────────┐
    │               │       │                 │
  Approximation   Physics   Must Match        Physics
  เริ่มต้นง่ายๆ    ตรงกับ     ต้องตรงกับ       ตรงกับ
  Solver จะปรับ     ปัญหา    สภาพจริง          ปัญหา
                    ให้
    │                       │
    ▼                       ▼
┌─────────┐           ┌─────────┐
│ k, ε, ω │           │ k, ε, ω │
│ small   │           │ derived │
│ (1e-10) │           │ from U  │
└─────────┘           └─────────┘
```

### Quick Checklist for Initial Conditions

| Field | Steady-State | Transient | Command |
|-------|--------------|-----------|---------|
| **U** | `(0 0 0)` or estimated | Measured at t=0 | Edit `0/U` |
| **p** | 0 or reference | Measured at t=0 | Edit `0/p` |
| **k** | $1 \times 10^{-10}$ | $1.5 (I U)^2$ | Edit `0/k` |
| **epsilon** | $1 \times 10^{-10}$ | $C_\mu^{3/4} k^{3/2} / \ell$ | Edit `0/epsilon` |
| **omega** | $1 \times 10^{-10}$ | $\epsilon / (C_\mu k)$ | Edit `0/omega` |
| **T** | 300 or ambient | Measured at t=0 | Edit `0/T` |

> ⚠️ **Critical Warning:** อย่าตั้งค่า k, epsilon, omega = 0
> - จะเกิด **divide by zero** ใน turbulence model
> - ใช้ค่าเล็กๆ เช่น `1e-10` แทน

---

## 🧱 Wall Treatment: Quick Decision Guide

```
┌─────────────────────────────────────────────────────────────────┐
│              WALL TREATMENT SELECTION                           │
│   ดูรายละเอียด: 04_Dimensionless_Numbers.md#y-plus           │
│   ดูรายละเอียด: 06_Boundary_Conditions.md#walls              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                    คำนวณ y+ = (ρuₜy)/μ
                         │
            ┌────────────┴────────────┐
            │                         │
      y+ < 5                  30 < y+ < 300
 (Viscous Sublayer)        (Log-Law Region)
            │                         │
    ┌───────┴────────┐        ┌────────┴────────┐
    │                │        │                 │
Low-Re Models    Resolve   Wall Functions   High-Re Models
    │            all           │                 │
    │          layers          │                 │
┌───┴───────┐       │    ┌─────┴─────┐   ┌─────┴─────┐
│ kOmegaSST │       │    │ kEpsilon │   │ kEpsilon  │
│ (low-Re)  │       │    │ + wall   │   │ + wall    │
└───────────┘       │    │ function │   │ function  │
                    │    └───────────┘   └───────────┘
                    │
    ┌───────────────┴───────────────┐
    │                               │
y+ ~ 1-5                       y+ ~ 30-100
(y+ < 1 ดีที่สุด)              (y+ ~ 50 เหมาะสม)
    │                               │
Mesh: หนาแน่นมาก               Mesh: ปานกลาง
ใกล้ผนัง                      ใกล้ผนัง
```

### How to Check y+

```bash
# หลังจากรัน simulation แล้ว
postProcess -func yPlus -latestTime

# หรือเขียนใน controlDict
functions
{
    yPlus
    {
        type            yPlus;
        executeAtWrite  yes;
    }
}
```

### y+ Guidelines

| y+ Range | Region | Recommended Approach | Model | Mesh Requirement |
|----------|--------|---------------------|-------|------------------|
| **y+ < 1** | Viscous sublayer | Resolve everything | Low-Re k-omega SST | Very fine near wall |
| **1 < y+ < 5** | Viscous sublayer | Acceptable | Low-Re models | Fine near wall |
| **5 < y+ < 30** | Buffer zone | Avoid | — | Refine or coarsen |
| **30 < y+ < 100** | Log-law (optimal) | Wall functions | k-epsilon, k-omega SST | Medium near wall |
| **100 < y+ < 300** | Log-law | Wall functions (less accurate) | k-epsilon, k-omega SST | Coarse near wall |
| **y+ > 300** | Wake region | Too coarse | — | Refine mesh |

---

## 📂 Case Directory Structure with Purpose

```
case/
├── 0/                           # ⏰ INITIAL & BOUNDARY CONDITIONS
│   ├── U                        # └─ Velocity field
│   ├── p                        # └─ Pressure field
│   ├── T                        # └─ Temperature field (if thermal)
│   ├── k                        # └─ Turbulence kinetic energy
│   ├── epsilon                  # └─ Turbulence dissipation rate
│   ├── omega                    # └─ Specific dissipation rate
│   ├── nut                      # └─ Turbulent viscosity
│   └── alphasat                 # └─ Phase fraction (multiphase)
│
├── constant/                    # 🔧 PHYSICS & MESH (TIME-INVARIANT)
│   ├── transportProperties      # └─ Viscosity, diffusivity
│   ├── thermophysicalProperties # └─ EOS, Cp, kappa (compressible)
│   ├── turbulenceProperties     # └─ Turbulence model selection
│   ├── RASProperties            # └─ RAS model coefficients
│   ├── LESProperties            # └─ LES model coefficients
│   ├── g                        # └─ Gravity vector (buoyancy)
│   ├── polyMesh/                # └─ Mesh files
│   │   ├── points               #    └─ Node coordinates
│   │   ├── faces                #    └─ Face definitions
│   │   ├── owner                #    └─ Owner cell
│   │   ├── neighbour            #    └─ Neighbor cell
│   │   └── boundary             #    └─ Boundary patches
│   └── cellToRegion             # └─ Cell regions (optional)
│
├── system/                      # ⚙️ NUMERICS & CONTROL
│   ├── controlDict              # ┎─ Time stepping, output
│   │   ├── startFrom            # └─ startTime, latestTime
│   │   ├── startTime            # └─ Initial time
│   │   ├── endTime              # └─ Final time
│   │   ├── deltaT               # └─ Time step size
│   │   ├── writeControl         # └─ timeStep, runTime, etc.
│   │   ├── writeInterval        # └─ Output frequency
│   │   ├── purgeWrite           # └─ Keep latest N results
│   │   ├── scheme               # └─ Euler, backward, CrankNicolson
│   │   └── functions            # └─ Probes, sampling, etc.
│   │
│   ├── fvSchemes                # ┎─ DISCRETIZATION SCHEMES
│   │   ├── ddtSchemes           # └─ Time: Euler, backward
│   │   ├── gradSchemes          # └─ Gradient: Gauss linear
│   │   ├── divSchemes           # └─ Convection: Gauss upwind, linear
│   │   ├── laplacianSchemes     # └─ Diffusion: Gauss linear corrected
│   │   ├── interpolationSchemes # └─ Face interpolation
│   │   ├── snGradSchemes        # └─ Surface normal gradient
│   │   └── wallDist             # └─ Wall distance method
│   │
│   ├── fvSolution               # ┎─ SOLVER SETTINGS
│   │   ├── solvers              # └─ Linear solver for each field
│   │   │   ├── p                # └─ GAMG, PCG
│   │   │   ├── U                # └─ PBiCGStab
│   │   │   └── k, epsilon       # └─ PBiCGStab
│   │   ├── SIMPLE               # └─ SIMPLE algorithm settings
│   │   │   ├── nCorrectors      # └─ Number of corrections
│   │   │   ├── nNonOrthogonalCorrectors
│   │   │   └── residualControl  # └─ Convergence criteria
│   │   ├── PISO                 # └─ PISO algorithm settings
│   │   │   ├── nCorrectors
│   │   │   └── nNonOrthogonalCorrectors
│   │   └── relaxationFactors    # └─ Under-relaxation for SIMPLE
│   │
│   ├── decomposeParDict         # ┎─ PARALLEL RUN SETUP
│   │   ├── numberOfSubdomains   # └─ Number of cores
│   │   └── method               # └─ simple, hierarchical, scotch
│   │
│   └── blockMeshDict            # ┎─ BLOCKED MESH GENERATION
│       ├── vertices            # └─ Block corner points
│       ├── blocks              # └─ Block definitions
│       ├── edges               # └─ Edge grading
│       └── boundary            # └─ Patch names and types
│
├── Allrun                       # ▶️  BATCH SCRIPT TO RUN CASE
├── Allclean                     # 🧹 CLEAN SCRIPT
└── README                       # 📄 CASE DOCUMENTATION
```

---

## ✅ Pre-Run Checklist (Actionable with Commands)

### Step 1: Verify Physics

```bash
# 1.1 Check flow regime
# Calculate Reynolds number: Re = rho * U * L / mu
# Example: rho=1.2, U=10, L=1.0, mu=1.8e-5
python3 -c "print(f'Re = {1.2*10*1.0/1.8e-5:.0f}')"
# If Re > 4000: turbulent
```

```bash
# 1.2 Check Mach number
# Calculate Ma = U / speedOfSound
# Example: U=30, c=340
python3 -c "print(f'Ma = {30/340:.2f}')"
# If Ma < 0.3: incompressible
# If Ma > 0.3: compressible
```

**Decision:**
- [ ] `Re > 4000` → เปิด turbulence model
- [ ] `Ma < 0.3` → ใช้ incompressible solver (simpleFoam, pimpleFoam)
- [ ] `Ma > 0.3` → ใช้ compressible solver (rhoSimpleFoam, rhoPimpleFoam)

### Step 2: Verify Boundary Conditions

```bash
# 2.1 Check BC consistency
foamListTimes
grep -A 5 "boundaryField" 0/U
grep -A 5 "boundaryField" 0/p
```

**Checklist:**
- [ ] **Inlet:** `U` = `fixedValue`, `p` = `zeroGradient`
- [ ] **Outlet:** `U` = `zeroGradient`, `p` = `fixedValue`
- [ ] **Wall:** `U` = `noSlip` or `fixedValue (0 0 0)`
- [ ] **Turbulent wall:** `k`, `epsilon`, `omega` = wall functions

### Step 3: Verify Initial Conditions

```bash
# 3.1 Check initial values
grep "internalField" 0/U
grep "internalField" 0/p
grep "internalField" 0/k
grep "internalField" 0/epsilon
```

**Checklist:**
- [ ] `k`, `epsilon`, `omega` ≠ 0 (ใช้ `1e-10` แทน)
- [ ] `p` มี reference point (fixedValue อย่างน้อย 1 จุด)
- [ ] `U` สมเหตุสมผลกับปัญหา

### Step 4: Verify Numerical Settings

```bash
# 4.1 Check time step for transient
# Calculate Courant number: Co = U * dt / dx
# Example: U=10, dx=0.01, dt=0.001
python3 -c "print(f'Co = {10*0.001/0.01:.2f}')"
# For PISO: Co < 1 recommended
# For PIMPLE: Co < 5 acceptable
```

```bash
# 4.2 Check solver settings
cat system/fvSolution
grep -A 10 "solvers" system/fvSolution
grep -A 10 "SIMPLE\|PISO\|PIMPLE" system/fvSolution
```

**Checklist:**
- [ ] Algorithm ตรงกับปัญหา (SIMPLE/PISO/PIMPLE)
- [ ] Relaxation factors < 1.0 (สำหรับ SIMPLE)
- [ ] Residual control ถูกตั้งค่า

### Step 5: Verify Mesh

```bash
# 5.1 Check mesh quality
checkMesh

# Expected output:
# Mesh OK
# No non-orthogonal cells > 70
# No skewness > 4
```

```bash
# 5.2 Check y+ (หลังจากรันครั้งแรก)
postProcess -func yPlus -latestTime
paraFoam -latestTime
# ใน ParaFOAM: ตรวจสอบ yPlus ที่ผนัง
# - y+ < 5: Low-Re model, resolve BL
# - 30 < y+ < 300: Wall functions
```

**Checklist:**
- [ ] Mesh quality OK (ไม่มี highly non-orthogonal cells)
- [ ] y+ ตรงกับ wall treatment

### Step 6: Final Verification

```bash
# 6.1 Dry run (ไม่รันจริง แค่ตรวจ)
solverName -dryRun

# 6.2 Check all required files
ls 0/
ls constant/polyMesh/
ls system/
```

**Final Checklist:**
- [ ] ไฟล์ครบถ้วน (0/, constant/, system/)
- [ ] BC consistent
- [ ] Initial values สมเหตุสมผล
- [ ] Numerical settings เหมาะสม
- [ ] Mesh quality OK
- [ ] y+ เหมาะสมกับ model

---

## 🎓 Concept Check

<details>
<summary><b>1. ทำไมต้องเข้าใจสมการควบคุมก่อนใช้ OpenFOAM?</b></summary>

**เพราะ:** ทุกการตั้งค่าใน OpenFOAM (schemes, BCs, solver) มาจากสมการเหล่านี้

**ตัวอย่าง:**
- Simulation diverge → อาจเกิดจาก BC ไม่ consistent (กฎอนุรักษ์มวล)
- Convergence ช้า → อาจเกิดจาก pressure-velocity coupling ไม่ถูกต้อง
- k, epsilon ติดลบ → อาจเกิดจากค่าเริ่มต้น = 0 (สมการ turbulence)

**ดูเพิ่มเติม:** [01_Introduction.md](01_Introduction.md), [02_Conservation_Laws.md](02_Conservation_Laws.md)
</details>

<details>
<summary><b>2. SIMPLE กับ PIMPLE ต่างกันอย่างไร?</b></summary>

**SIMPLE:**
- สำหรับ **steady-state** เท่านั้น
- ใช้ **under-relaxation** เพื่อความเสถียร
- 1 correction ต่อ iteration
- เร็วแต่อาจไม่ลู่เข้าถ้า relaxation ไม่เหมาะสม

**PIMPLE:**
- สำหรับ **transient** ที่ต้องการรันด้วย Δt ใหญ่
- ผสม PISO + SIMPLE
- มี **outer corrections** เพื่อลด error ในแต่ละ time step
- ช้ากว่า แต่ robust กว่า

**ดูเพิ่มเติม:** [02_Conservation_Laws.md](02_Conservation_Laws.md#pressure-velocity-coupling), [05_OpenFOAM_Implementation.md](05_OpenFOAM_Implementation.md#algorithms)
</details>

<details>
<summary><b>3. fvm::div กับ fvc::div ต่างกันอย่างไร?</b></summary>

**fvm::div (Implicit):**
- สร้าง **matrix coefficients**
- ใช้ใน term ที่ต้องการความเสถียร (convection, diffusion)
- ค่า implicit → มีส่วนร่วมใน matrix A
- คำนวณช้ากว่า แต่เสถียรกว่า

**fvc::div (Explicit):**
- คำนวณ **ค่าทันที** จาก field ปัจจุบัน
- ใช้เมื่อไม่ต้องการให้ term นั้นอยู่ใน matrix
- ค่า explicit → กลายเป็น source term
- คำนวณเร็ว แต่เสถียรน้อยกว่า (จำกัด Δt)

**ตัวอย่าง:**
```cpp
// Convection (implicit - stable)
fvm::div(phi, U)

// Divergence check (explicit - fast)
fvc::div(phi)  // เช็ค ∇·U ≈ 0?
```

**ดูเพิ่มเติม:** [05_OpenFOAM_Implementation.md](05_OpenFOAM_Implementation.md#fvm-vs-fvc)
</details>

<details>
<summary><b>4. เมื่อไหร่ควรใช้ wall functions vs. resolve boundary layers?</b></summary>

**ใช้ Wall Functions เมื่อ:**
- y+ ≈ 30-100 (optimal at y+ ≈ 50)
- Mesh หยาบกว่า (ไม่ refine หนาแน่นใกล้ผนัง)
- ใช้ k-epsilon หรือ k-omega SST
- เร็วกว่า แต่ accuracy น้อยกว่า

**Resolve Boundary Layers เมื่อ:**
- y+ < 5 (ideal at y+ < 1)
- Mesh หนาแน่นมากใกล้ผนัง
- ใช้ low-Re models (k-omega SST low-Re)
- ช้ากว่า แต่ accuracy สูงกว่า

**ตรวจสอบด้วย:**
```bash
postProcess -func yPlus -latestTime
```

**ดูเพิ่มเติม:** [04_Dimensionless_Numbers.md](04_Dimensionless_Numbers.md#y-plus), [06_Boundary_Conditions.md](06_Boundary_Conditions.md#walls)
</details>

<details>
<summary><b>5. ทำไม k, epsilon, omega ต้องไม่เป็น 0?</b></summary>

**เพราะ:**
- Turbulence models มี **division by k** หรือ **epsilon** ในสมการ
- ถ้า k = 0 → จะ divide by zero → **simulation crash**
- ถ้า epsilon = 0 → ค่าที่ได้อาจ NaN หรือ Inf

**วิธีแก้:**
```cpp
// ใช้ค่าเล็กๆ แทน
internalField   uniform 1e-10;

// หรือคำนวณจาก flow conditions
internalField   uniform 0.005;  // k = 1.5*(I*U)^2
```

**ดูเพิ่มเติม:** [07_Initial_Conditions.md](07_Initial_Conditions.md#turbulence)
</details>

---

## ⚠️ Common Pitfalls (Enhanced with Solutions)

| ปัญหา | สาเหตุ | วิธีแก้ | ตรวจสอบด้วย |
|--------|---------|---------|-------------|
| **Simulation diverge ทันที** | BC ไม่ consistent | Inlet: U fixed, p zeroGrad<br>Outlet: U zeroGrad, p fixed | `grep boundaryField 0/*` |
| **k, epsilon ติดลบ** | ค่าเริ่มต้น = 0 | ใช้ค่าเล็กๆ (1e-10) | `grep internalField 0/k` |
| **Pressure drift** | ไม่มี reference point | ต้องมี p fixedValue อย่างน้อย 1 จุด | `grep "fixedValue" 0/p` |
| **Convergence ช้ามาก** | Δt ใหญ่เกินไกับ PISO | ลด Δt หรือเปลี่ยนเป็น PIMPLE | `grep deltaT system/controlDict` |
| **y+ ผิดทั้งหมด** | Mesh หยาบเกินไป | Refine ใกล้ผนังหรือเปลี่ยน model | `postProcess -func yPlus` |
| **Temperature units ผิด** | สับสน K vs °C | compressible → K เสมอ<br>incompressible → ใช้งานได้ | `check` ใน thermophysicalProperties |
| **Backflow at outlet** | Outlet ใกล้ obstacle มากเกินไป | ขยาย domain หรือใช้ `inletOutlet` | `paraFoam` → visualize U |
| **Time step too large** | Courant number > 1 | ลด Δt หรือใช้ adjustableRunTime | `foamListTimes` → check dt |
| **Non-orthogonal cells** | Mesh quality แย่ | improve mesh หรือเพิ่ม nNonOrthogonalCorrectors | `checkMesh` |
| **Residuals ไม่ลดลง** | Relaxation ผิด | ปรับ relaxationFactors ใน fvSolution | `cat system/fvSolution` |

### How to Debug Divergence

```bash
# 1. Check initial residuals
grep -i "initial residual" log.simpleFoam | tail -20

# 2. Check max residuals
grep -i "max residual" log.simpleFoam | tail -20

# 3. Check Courant number
postProcess -func CourantNo -latestTime

# 4. Check boundedness
postProcess -func mag -latestTime  # ตรวจสอบค่าแปลกๆ

# 5. Visualize
paraFoam -latestTime
# ตรวจสอบ:
# - U มีค่า extreme ไหม
# - p มี oscillation ไหม
# - k, epsilon ติดลบไหม
```

---

## 📖 Visual Summary of All Dimensionless Numbers

```
┌─────────────────────────────────────────────────────────────────┐
│              DIMENSIONLESS NUMBERS QUICK REFERENCE               │
│          ดูรายละเอียด: 04_Dimensionless_Numbers.md           │
└────────────────────────┬────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
    Flow Inertia     Compressibility    Free Surface
   (Reynolds)        (Mach)            (Froude)
        │                │                │
   Re = ρUL/μ       Ma = U/c        Fr = U/√(gL)
        │                │                │
    ┌───┴────┐      ┌────┴────┐     ┌─────┴─────┐
    │        │      │         │     │           │
 Re<2300  Re>4000  Ma<0.3   Ma>0.3  Fr<1       Fr>1
    │        │      │         │     │           │
 Laminar  Turbulent Incomp.  Comp.  Subcritical  Supercritical
    │        │      │         │     │           │
laminar kEpsilon  simple  rho     gravity     wave
       kOmega       Foam    Simple   dominant   dominant
```

### All Dimensionless Numbers in One Table

| Number | Formula | Physical Meaning | Critical Value | Decision |
|--------|---------|------------------|----------------|----------|
| **Reynolds** | $Re = \frac{\rho U L}{\mu}$ | Inertia / Viscosity | 2300, 4000 | Laminar vs Turbulent |
| **Mach** | $Ma = \frac{U}{c}$ | Flow speed / Sound speed | 0.3 | Incompressible vs Compressible |
| **Froude** | $Fr = \frac{U}{\sqrt{gL}}$ | Inertia / Gravity | 1 | Free surface regime |
| **Prandtl** | $Pr = \frac{c_p \mu}{k}$ | Momentum / Thermal diffusivity | 0.7 (air), 7 (water) | Thermal BL thickness |
| **Strouhal** | $St = \frac{f L}{U}$ | Unsteadiness | 0.2 (cylinder) | Vortex shedding |
| **Eckert** | $Ec = \frac{U^2}{c_p T}$ | Kinetic energy / Enthalpy | 1 | Compressibility heating |

---

## 🔗 Cross-Reference Matrix

| Topic | Related Files | Key Concepts |
|-------|--------------|--------------|
| **Conservation Laws** | 01, 02, 05 | Mass, momentum, energy equations |
| **Pressure-Velocity Coupling** | 02, 05 | SIMPLE, PISO, PIMPLE algorithms |
| **EOS** | 03, 04 | Ideal gas, incompressible, Mach number |
| **Turbulence** | 04, 06 | Reynolds number, wall functions, y+ |
| **Boundary Conditions** | 05, 06, 07 | Dirichlet, Neumann, wall functions |
| **Initial Conditions** | 04, 07 | k, epsilon estimation |
| **Numerics** | 05 | fvm vs fvc, discretization schemes |
| **Mesh** | 04, 06 | y+, wall treatment, mesh quality |

---

## 🎯 Takeaways

1. **สมการควบคุมคือฐาน** — ทุกการตั้งค่าใน OpenFOAM มาจากสมการเหล่านี้
2. **Re และ Ma บอกทุกอย่าง** — ตัดสินใจเลือก solver, model, และ numerical schemes
3. **y+ สำคัญมาก** — ต้อง match กับ turbulence model และ wall treatment
4. **BC consistency สำคัญ** — inlet และ outlet ต้องเป็นคู่ที่สมดุล
5. **เริ่มต้นด้วยค่าเล็กๆ** — k, epsilon, omega ไม่เคยเป็น 0

---

## 📚 เอกสารที่เกี่ยวข้อง

### ใน Module เดียวกัน
- **บทก่อนหน้า:** [07_Initial_Conditions.md](07_Initial_Conditions.md) — เงื่อนไขเริ่มต้น
- **บทถัดไป:** [09_Exercises.md](09_Exercises.md) — แบบฝึกหัดประยุกต์
- **ภาพรวม:** [00_Overview.md](00_Overview.md) — ภาพรวมบทนี้

### ลิงก์ไปหัวข้อสำคัญ
- **กฎการอนุรักษ์:** [02_Conservation_Laws.md](02_Conservation_Laws.md)
- **Equation of State:** [03_Equation_of_State.md](03_Equation_of_State.md)
- **เลขไร้มิติ:** [04_Dimensionless_Numbers.md](04_Dimensionless_Numbers.md)
- **OpenFOAM Implementation:** [05_OpenFOAM_Implementation.md](05_OpenFOAM_Implementation.md)
- **Boundary Conditions:** [06_Boundary_Conditions.md](06_Boundary_Conditions.md)
- **Initial Conditions:** [07_Initial_Conditions.md](07_Initial_Conditions.md)

### ไปยังหัวข้อถัดไป
**บทถัดไป:** [09_Exercises.md](09_Exercises.md) — แบบฝึกหัดเพื่อทบทวนความเข้าใจ
