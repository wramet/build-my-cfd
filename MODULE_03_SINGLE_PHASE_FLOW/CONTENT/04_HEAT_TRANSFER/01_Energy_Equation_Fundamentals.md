# Energy Equation Fundamentals

สมการพลังงานใน OpenFOAM: ทฤษฎีและการประยุกต์ใช้

---

## Learning Objectives

หลังจากอ่านบทนี้ คุณจะสามารถ:

- **WHAT (Concepts):** อธิบายสมการพลังงานในรูปแบบต่างๆ (Temperature, Enthalpy, Internal Energy), กฎของฟูริเยร์ และกลไกการถ่ายเทความร้อน
- **WHY (Physical Importance):** วิเคราะห์ความแตกต่างระหว่างรูปแบบพลังงานทั้ง 3 และการเลือกใช้งานที่เหมาะสมกับแต่ละสถานการณ์
- **HOW (Implementation):** ตั้งค่า thermophysicalProperties, เลือก solver ที่เหมาะสม, และเขียนสมการพลังงานใน OpenFOAM

---

## What is the Energy Equation?

### 1. Basic Definition (WHAT)

สมการพลังงาน (Energy Equation) คือการประยุกต์กฎข้อที่สองของเทอร์โมไดนามิกส์สำหรับระบบไหลเวียน (fluid systems) ซึ่งอธิบาย:
- การถ่ายเทความร้อน (heat transfer)
- การเปลี่ยนแปลงของพลังงานภายใน (internal energy changes)
- งานที่เกิดจากแรงดันและแรงเฉืออง (pressure and viscous work)

### 2. Mathematical Form

**Conservation Form (Total Energy):**

$$\frac{\partial (\rho E)}{\partial t} + \nabla \cdot (\rho \mathbf{u} E) = \nabla \cdot (k \nabla T) - \nabla \cdot (p \mathbf{u}) + \nabla \cdot (\boldsymbol{\tau} \cdot \mathbf{u}) + Q$$

**Where:**
- $E = e + \frac{1}{2}|\mathbf{u}|^2$ = total energy per unit mass [J/kg]
- $e$ = internal energy [J/kg]
- $\mathbf{u}$ = velocity vector [m/s]
- $p$ = pressure [Pa]
- $k$ = thermal conductivity [W/(m·K)]
- $\boldsymbol{\tau}$ = viscous stress tensor [Pa]
- $Q$ = heat source/sink [W/m³]

### 3. Physical Terms Breakdown (WHY)

| Term | Mathematical Expression | Physical Meaning | Engineering Significance |
|------|------------------------|------------------|---------------------------|
| **Unsteady** | $\frac{\partial (\rho E)}{\partial t}$ | Rate of energy change with time | สำคัญใน transient problems (startup, shutdown) |
| **Convection** | $\nabla \cdot (\rho \mathbf{u} E)$ | Energy transport due to fluid motion | การพาพลังงานโดยการไหลของของไหล |
| **Conduction** | $\nabla \cdot (k \nabla T)$ | Heat diffusion (Fourier's law) | การนำความร้อน — สำคัญใน solids, boundary layers |
| **Pressure Work** | $-\nabla \cdot (p \mathbf{u})$ | Work done by pressure forces | สำคัญใน compressible flows (compression/expansion) |
| **Viscous Dissipation** | $\nabla \cdot (\boldsymbol{\tau} \cdot \mathbf{u})$ | Conversion of kinetic to thermal energy | สำคัญใน high-speed flows (Ma > 1) |
| **Source** | $Q$ | Heat generation/absorption | แหล่งความร้อน เช่น จาก chemical reactions, electrical heating |

### 4. Fourier's Law: Foundation of Heat Conduction

**WHAT (Definition):**
$$\mathbf{q} = -k \nabla T$$

กฎของฟูริเยร์อธิบายว่า heat flux ($\mathbf{q}$) แปรผันตาม temperature gradient ($\nabla T$)

**WHY (Physical Meaning):**
| Symbol | Physical Meaning | Unit | Typical Value |
|--------|------------------|------|---------------|
| $\mathbf{q}$ | Heat flux vector | W/m² | - |
| $k$ | Thermal conductivity | W/(m·K) | Air: 0.026, Water: 0.6, Copper: 401 |
| $\nabla T$ | Temperature gradient | K/m | - |

**Negative Sign**: Heat flows from hot to cold (opposite to gradient direction)

**HOW (Implementation in OpenFOAM):**
```cpp
// Heat conduction term in energy equation
-fvm::laplacian(alphaEff, T)  // -∇·(α_eff ∇T) = -∇·(k/(ρcp) ∇T)

// Where alphaEff = k/(ρ·cp) is thermal diffusivity
```

> **📖 Note**: thermophysicalProperties การตั้งค่าแบบละเอียด ดูได้ใน [00_Overview.md](00_Overview.md)

---

## Why Different Forms Matter?

### 1. Three Forms in OpenFOAM (WHAT)

OpenFOAM จัดเตรียมสมการพลังงานใน **3 รูปแบบหลัก** ขึ้นอยู่กับ **ลักษณะของปัญหา** และ **ความแม่นยำที่ต้องการ**:

| Form | Mathematical Variable | Energy Definition | Primary Use Case | Key Advantage |
|------|----------------------|------------------|------------------|----------------|
| **Temperature (T)** | $T$ | None directly (measurable) | Incompressible flows, small ΔT | Simplest, fastest convergence |
| **Enthalpy (h)** | $h = e + p/\rho$ | Flow work included | Compressible flows, natural convection | Accounts for compression work automatically |
| **Internal Energy (e)** | $e$ | Molecular energy only | High-temperature, combustion | Most fundamental, detailed thermodynamics |

### 2. Physical Interpretation (WHY)

**ความหมายแต่ละรูปแบบ:**

| Form | Physical Meaning | When it Matters |
|------|------------------|-----------------|
| **Temperature (T)** | ตัวแปรวัดง่าย แต่ไม่ใช่พลังงานโดยตรง — ใช้ในการวัดและ boundary conditions | เมื่อ density ≈ constant, temperature variations น้อย |
| **Enthalpy (h)** | พลังงานที่รวม flow work ($p/\rho$) — สำคัญใน open systems | เมื่อมีการไหลเข้า-ออกของ control volume, compression/expansion สำคัญ |
| **Internal Energy (e)** | พลังงานระดับโมเลกุล (kinetic + potential) — property ของสาร | เมื่อต้องการความแม่นยำในระดับพื้นฐายสุด, combustion |

**ทำไมต้องแยก (Why Separate?):**

1. **Computational Efficiency:**
   - T-form เร็วที่สุด ($\rho$ = constant, simplified equation)
   - เหมาะกับ problems ที่ $\Delta T$ น้อย, incompressible

2. **Physical Accuracy:**
   - h-form จำเป็นเมื่อ pressure work สำคัญ
   - Compressible flows ต้องรวม compression/expansion work

3. **Numerical Stability:**
   - e-form บางครั้งให้การลู่เข้าดีกว่าใน high-temperature flows
   - ลดความซับซ้อนใน thermodynamic calculations

### 3. When to Use Each Form (HOW)

| Criterion | Temperature (T) | Enthalpy (h) | Internal Energy (e) |
|-----------|----------------|--------------|---------------------|
| **Density Variation** | $\Delta\rho/\rho < 0.05$ | $\Delta\rho/\rho > 0.05$ | Variable (high T) |
| **Temperature Range** | $\Delta T < 50$ K | $\Delta T > 50$ K | $T > 1500$ K |
| **Mach Number** | Ma < 0.1 | Ma > 0.3 | Ma > 0.3 (high-speed) |
| **Buoyancy** | Boussinesq approximation | Full compressible | Full compressible |
| **Chemical Reactions** | No | Simple | Combustion, reacting flows |
| **Computational Cost** | ★☆☆ Lowest | ★★☆ Medium | ★★★ Highest |
| **Physical Accuracy** | Low (limited range) | High | Highest |

### 4. Comparison Matrix: Decision Guide

```
┌─────────────────────────────────────────────────────────────────┐
│                    ENERGY FORM SELECTION                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Start Problem                                                  │
│       │                                                         │
│       ├─ Is ρ essentially constant? (Δρ/ρ < 0.05)               │
│       │   ├─ YES → Use Temperature (T) form                     │
│       │   │         Solver: buoyantBoussinesqSimpleFoam         │
│       │   │         EoS: rhoConst                               │
│       │   │         Advantages: Fast, simple, robust           │
│       │   │                                                      │
│       │   └─ NO → Continue                                      │
│       │                                                          │
│       ├─ Is pressure work significant? (Ma > 0.3 or large Δp)   │
│       │   ├─ YES → Use Enthalpy (h) form                        │
│       │   │         Solver: buoyantSimpleFoam / buoyantPimpleFoam│
│       │   │         EoS: perfectGas                             │
│       │   │         Advantages: Physical accuracy, automatic    │
│       │   │                   compression work accounting       │
│       │   │                                                      │
│       │   └─ NO → Consider Internal Energy (e) form             │
│       │           Solver: rhoPimpleFoam                         │
│       │           EoS: perfectGas                               │
│       │           Advantages: Most fundamental, best for        │
│       │                     combustion, detailed thermo         │
│       │                                                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## How It's Implemented in OpenFOAM

### 1. Thermophysical Properties Dictionary Structure

**WHAT (Basic Structure):**

OpenFOAM ใช้ `thermophysicalProperties` dictionary เพื่อกำหนดรูปแบบพลังงาน:

```cpp
// constant/thermophysicalProperties

thermoType
{
    // Type selector: compressibility handling
    type            hePsiThermo;          // hePsiThermo (compressible) | heRhoThermo (incompressible)

    // Mixture composition
    mixture         pureMixture;          // pureMixture | multiComponentMixture

    // Transport models (viscosity, thermal conductivity)
    transport       const;                // const | polynomial | sutherland

    // Thermodynamic properties (Cp, Hf)
    thermo          hConst;               // hConst | polynomial | janaf

    // Equation of state
    equationOfState perfectGas;           // perfectGas | rhoConst | incompressiblePerfectGas

    // Energy form - MOST IMPORTANT FOR THIS CHAPTER!
    energy          sensibleEnthalpy;     // sensibleEnthalpy | sensibleInternalEnergy
}

mixture
{
    specie
    {
        molWeight       28.9;              // [kg/kmol]
    }

    thermodynamics
    {
        Cp              1005;              // [J/(kg·K)]
        Hf              0;                 // [J/kg] — formation enthalpy
    }

    transport
    {
        mu              1.8e-5;            // [Pa·s] — dynamic viscosity
        Pr              0.71;              // Prandtl number (molecular)
        // หรือใช้ k (thermal conductivity) โดยตรง:
        // k               0.0261;           // [W/(m·K)]
    }
}
```

**WHY (Component Significance):**

| Component | Physical Meaning | Impact on Energy Form |
|-----------|------------------|----------------------|
| `energy: sensibleEnthalpy` | Solves for enthalpy $h$ | Includes pressure work automatically |
| `energy: sensibleInternalEnergy` | Solves for internal energy $e$ | More fundamental, requires explicit pressure work term |
| `equationOfState: perfectGas` | Variable density $\rho(p,T)$ | Requires compressible energy form (h or e) |
| `equationOfState: rhoConst` | Constant density | Can use simplified T-form |

**HOW (Configuration Examples):**

> **📖 Detailed configuration examples for each energy form:**
> - T-form (Boussinesq): See [00_Overview.md](00_Overview.md) Section 2
> - h-form (compressible): See [00_Overview.md](00_Overview.md) Section 2
> - e-form (high-T): See [00_Overview.md](00_Overview.md) Section 2

### 2. Energy Equation Discretization

**Temperature Form (T-form):**

```cpp
// Found in: buoyantBoussinesqSimpleFoam/createFields.H
volScalarField T
(
    IOobject
    (
        "T",
        runTime.timeName(),
        mesh,
        IOobject::MUST_READ,
        IOobject::AUTO_WRITE
    ),
    mesh
);

// TEqn.H
fvScalarMatrix TEqn
(
    fvm::ddt(T)                              // Unsteady term: ∂T/∂t
  + fvm::div(phi, T)                         // Convection: u·∇T
  - fvm::laplacian(alphaEff, T)              // Diffusion: ∇·(α∇T)
 ==
    fvModels.source(T)                       // Source terms: Q/(ρcp)
);

TEqn.relax(factor);
TEqn.solve();
```

**Characteristics:**
- ✅ Simplest form, fastest convergence
- ✅ Direct temperature output (no conversion needed)
- ❌ Neglects pressure work and viscous dissipation
- ❌ Valid only for small temperature variations

**Enthalpy Form (h-form):**

```cpp
// Found in: buoyantSimpleFoam/createFields.H
volScalarField h
(
    IOobject
    (
        "h",
        runTime.timeName(),
        mesh,
        IOobject::MUST_READ,
        IOobject::AUTO_WRITE
    ),
    mesh
);

// hEqn.H
fvScalarMatrix hEqn
(
    fvm::ddt(rho, h)                         // ∂(ρh)/∂t
  + fvm::div(phi, h)                         // ∇·(ρuh)
  - fvm::laplacian(turbulence->alphaEff(), h) // ∇·(k∇T)
 ==
    fvc::ddt(rho, K) + fvc::div(phi, K)      // Mechanical energy: Dp/Dt
  + fvModels.source(rho, h)                  // Viscous dissipation + sources
);

hEqn.relax(factor);
hEqn.solve();

// Update temperature from enthalpy
thermo.correct();
```

**Characteristics:**
- ✅ Includes pressure work (mechanical energy term)
- ✅ Automatic density variation handling
- ✅ Physical accuracy for compressible flows
- ❌ Requires conversion from h to T post-solve
- ❌ Higher computational cost than T-form

**Internal Energy Form (e-form):**

```cpp
// Found in: rhoPimpleFoam (when energy sensibleInternalEnergy)
volScalarField e
(
    IOobject
    (
        "e",
        runTime.timeName(),
        mesh,
        IOobject::MUST_READ,
        IOobject::AUTO_WRITE
    ),
    thermo.rho() * thermo.he()              // e = he - p/rho
);

// eEqn.H
fvScalarMatrix eEqn
(
    fvm::ddt(rho, e)                         // ∂(ρe)/∂t
  + fvm::div(phi, e)                         // ∇·(ρue)
  - fvm::laplacian(turbulence->alphaEff(), e)
 ==
    rho * (U & fvc::grad(p)) / rho           // Pressure work: p∇·u
  + compressibility * psi * p * fvc::ddt(p)  // Compression work
  + fvModels.source(rho, e)
);

eEqn.solve();
thermo.correct();
```

**Characteristics:**
- ✅ Most fundamental form
- ✅ Best for combustion and reacting flows
- ✅ Direct connection to thermodynamics
- ❌ Highest computational cost
- ❌ Slowest convergence
- ❌ Most complex to implement

### 3. Key Implementation Differences

| Aspect | T-form | h-form | e-form |
|--------|--------|--------|--------|
| **Primary Variable** | `volScalarField T` | `volScalarField h` | `volScalarField e` |
| **Field Declaration** | Direct in createFields.H | Direct in createFields.H | `thermo.he()` after thermo.correct() |
| **Density Treatment** | Constant ($\rho_0$) | Variable ($\rho(p,T)$) | Variable ($\rho(p,e)$) |
| **Boundary Conditions** | `fixedValue` for T | `fixedValue` for h | `fixedValue` for e |
| **Source Term Syntax** | `fvModels.source(T)` | `fvModels.source(rho, h)` | `fvModels.source(rho, e)` |
| **Post-Processing** | Direct T output | `thermo.T()` | `thermo.T()` |
| **Pressure Work** | Neglected | Included ($Dp/Dt$) | Included ($p\nabla\cdot u$) |
| **Viscous Dissipation** | Neglected | Included | Included |
| **Convergence Speed** | Fastest | Medium | Slowest |
| **Memory Usage** | Minimal | Moderate | High |

### 4. Thermodynamic Correction

After solving for energy, OpenFOAM automatically converts to temperature:

```cpp
// In thermophysicalModel library (simplified)
template<class Thermo>
typename Thermo::he Thermo::HE
(
    const Thermo& thermo,
    const typename Thermo::solutionType& p,
    const typename Thermo::solutionType& T
)
{
    // For sensibleEnthalpy:
    if (energy == sensibleEnthalpy)
    {
        return thermo.Cp()*T + thermo.Hf();  // h = Cp*T + Hf
    }

    // For sensibleInternalEnergy:
    if (energy == sensibleInternalEnergy)
    {
        return thermo.Cv()*T + thermo.Hf();  // e = Cv*T + Hf
    }
}

// In solver, after solving energy equation:
thermo.correct();  // Updates T from h or e
```

### 5. Solver Mapping

| Solver | Energy Form | Equation of State | Key Characteristic | Typical Applications |
|--------|-------------|-------------------|-------------------|----------------------|
| `buoyantBoussinesqSimpleFoam` | Temperature (T) | `rhoConst` | Incompressible, small ΔT | Room ventilation, electronics cooling (small ΔT) |
| `buoyantSimpleFoam` | Enthalpy (h) | `perfectGas` | Steady, compressible | Natural convection with large ΔT |
| `buoyantPimpleFoam` | Enthalpy (h) | `perfectGas` | Transient, compressible | Unsteady buoyancy-driven flows |
| `rhoPimpleFoam` | Internal Energy (e) | `perfectGas` | High-speed, compressible | High-Mach flows, shock waves |
| `rhoSimpleFoam` | Enthalpy/Energy (h/e) | `perfectGas` | Steady high-speed | Steady compressible flows |
| `chtMultiRegionFoam` | Enthalpy (h) | Varies | Conjugate heat transfer | Solid-fluid coupling, heat exchangers |
| `reactingFoam` | Internal Energy (e) | `perfectGas` | Combustion | Chemical reactions, combustion |

### 6. Boundary Condition Examples

```cpp
// ========== Temperature BCs (T-form) ==========
inlet
{
    type            fixedValue;
    value           uniform 300;              // [K]
}

hotWall
{
    type            fixedValue;
    value           uniform 350;              // [K]
}

adiabaticWall
{
    type            zeroGradient;             // ∇T·n = 0
}

// ========== Enthalpy BCs (h-form) ==========
inlet
{
    type            fixedValue;
    value           uniform 300000;          // [J/kg] ≈ Cp*T for air
}

heatedWall
{
    type            fixedValue;
    value           uniform 350000;          // [J/kg] ≈ Cp*350 for air
}

wallWithHeatFlux
{
    type            externalWallHeatFlux;
    mode            coefficient;
    h               uniform 10;               // [W/(m²·K)] heat transfer coeff
    Ta              uniform 350;              // [K] ambient temperature
}

// ========== Adiabatic (all forms) ==========
adiabaticWall
{
    type            zeroGradient;             // No heat flux
}
```

**Key Points:**
- T-form: BC values in Kelvin [K]
- h-form: BC values in J/kg (≈ Cp × T)
- ZeroGradient: Identical for all forms (adiabatic)

### 7. Source Terms Implementation

```cpp
// Volumetric heat source (e.g., electrical heating)
fvOptions
{
    heatSource
    {
        type            scalarCodedSource;
        selectionMode   all;

        field           h;                   // or T or e

        code
        #{
            const vectorField& C = mesh_.C();
            scalarField& source = eqn.source();

            // Heat source in region x < 0.1
            forAll(C, i)
            {
                if (C[i].x() < 0.1)
                {
                    source[i] += 1e5;        // [W/m³]
                }
            }
        #};
    }
}
```

---

## Turbulent Heat Transfer

### 1. Effective Diffusivity (WHAT)

ใน turbulent flow การถ่ายเทความร้อนเกิดจากทั้ง **molecular diffusion** และ **turbulent eddies**:

$$\alpha_{eff} = \alpha + \alpha_t = \frac{\nu}{Pr} + \frac{\nu_t}{Pr_t}$$

**Components:**
- $\alpha = \frac{k}{\rho c_p} = \frac{\nu}{Pr}$ = molecular thermal diffusivity
- $\alpha_t = \frac{\nu_t}{Pr_t}$ = turbulent thermal diffusivity
- $\nu_t$ = turbulent eddy viscosity (from turbulence model)
- $Pr_t$ = turbulent Prandtl number (≈ 0.85 for most flows)

### 2. Reynolds Analogy (WHY)

| Mechanism | Momentum Diffusivity | Thermal Diffusivity | Ratio |
|-----------|---------------------|---------------------|-------|
| **Molecular** | $\nu = \mu/\rho$ | $\alpha = k/(\rho c_p)$ | $Pr = \nu/\alpha$ |
| **Turbulent** | $\nu_t$ | $\alpha_t$ | $Pr_t = \nu_t/\alpha_t$ |

**Physical Meaning:**
- **Prandtl Number ($Pr$)**: สัดส่วนระหว่าง momentum diffusion และ thermal diffusion
- **Turbulent Prandtl Number ($Pr_t$)**: สัดส่วนเดียวกันใน turbulent flow

**Interpretation:**
| Pr Range | Fluid | Characteristics |
|----------|-------|-----------------|
| $Pr \ll 1$ (~0.01) | Liquid metals | Heat diffuses >> momentum (thermal layer thick) |
| $Pr \approx 1$ (0.7) | Air | Similar diffusion rates |
| $Pr \gg 1$ (~7-100) | Water, oils | Momentum diffuses >> heat (thermal layer thin) |

### 3. OpenFOAM Implementation (HOW)

```cpp
// In turbulenceModel library (simplified)
tmp<volScalarField> kappat() const  // Turbulent thermal conductivity
{
    return tmp<volScalarField>
    (
        new volScalarField
        (
            IOobject("kappat", mesh_.time().timeName(), mesh_),
            rho_ * Cp_ * (nut_ / Prt_)  // k_t = ρ * Cp * (ν_t / Pr_t)
        )
    );
}

// Effective thermal diffusivity
tmp<volScalarField> alphaEff() const
{
    return tmp<volScalarField>
    (
        new volScalarField
        (
            IOobject("alphaEff", mesh_.time().timeName(), mesh_),
            alpha() + alpha_t()  // α_eff = α + α_t
        )
    );
}

// Usage in energy equation
-fvm::laplacian(turbulence->alphaEff(), h)  // ∇·(α_eff ∇h)
```

### 4. Wall Functions for Heat Transfer

OpenFOAM provides wall functions for turbulent heat transfer:

```cpp
// In boundary conditions (0/T or 0/h)
wall
{
    type            compressible::alphatWallFunction;
    Prt             0.85;              // Turbulent Prandtl number
    value           uniform 0;         // Initial value (will be computed)
}
```

**Typical Values:**
| Parameter | Symbol | Air | Water | Liquid Metal |
|-----------|--------|-----|-------|--------------|
| Molecular Pr | $Pr$ | 0.71 | 7.0 | ~0.01 |
| Turbulent Pr | $Pr_t$ | 0.85 | 0.85 | 0.85 |

---

## Dimensionless Numbers for Heat Transfer

### 1. Prandtl Number (Pr)

$$Pr = \frac{\nu}{\alpha} = \frac{\mu c_p}{k}$$

**Physical Meaning**: อัตราส่วนของความหนา (thickness) ระหว่าง velocity boundary layer ($\delta$) และ thermal boundary layer ($\delta_T$)

| Fluid | Pr | Characteristics | Boundary Layer Relation |
|-------|---:|-----------------|------------------------|
| **Liquid metals** | ~0.01 | Thermal layer >> velocity layer | $\delta_T \gg \delta$ |
| **Air** | 0.71 | Similar thickness | $\delta_T \approx \delta$ |
| **Water** | 7.0 | Velocity layer >> thermal layer | $\delta_T \ll \delta$ |
| **Oil** | ~100 | Thermal layer very thin | $\delta_T \ll \delta$ |

**Effect on Heat Transfer:**
- Low Pr: Thermal effects penetrate deeper into flow
- High Pr: Thermal effects confined near wall

### 2. Nusselt Number (Nu)

$$Nu = \frac{hL}{k} = \frac{\text{convective heat transfer}}{\text{conductive heat transfer}}$$

**Physical Meaning**: อัตราเพิ่มของ heat transfer จาก convection เมื่อเทียบกับ conduction เท่านั้น

**Interpretation:**
- Nu = 1: Pure conduction (no convection enhancement)
- Nu > 1: Convection enhances heat transfer
- Higher Nu → Better heat transfer

**Typical Correlations:**
| Flow Configuration | Correlation | Application |
|--------------------|-------------|-------------|
| Laminar flat plate | $Nu = 0.664 Re^{1/2} Pr^{1/3}$ | External flow |
| Turbulent flat plate | $Nu = 0.037 Re^{4/5} Pr^{1/3}$ | External flow (high Re) |
| Laminar pipe flow | $Nu = 3.66$ | Constant wall T |
| Turbulent pipe flow | $Nu = 0.023 Re^{0.8} Pr^{0.4}$ | Dittus-Boelter |

> **📖 Note**: Rayleigh number ($Ra$) สำหรับ buoyancy-driven flows ดูรายละเอียดใน [03_Buoyancy_Driven_Flows.md](03_Buoyancy_Driven_Flows.md)

### 3. Peclet Number (Pe)

$$Pe = Re \cdot Pr = \frac{uL}{\alpha}$$

**Physical Meaning**: อัตราส่วนระหว่าง convective และ diffusive heat transfer

| Regime | Pe | Dominant Mechanism | Numerical Consideration |
|--------|---:|-------------------|------------------------|
| $Pe < 1$ | Diffusion dominates | Conduction | Standard discretization OK |
| $Pe > 1$ | Convection dominates | Advection | May need upwind schemes |
| $Pe \gg 1$ | Strong convection | Advection-dominated | High-resolution schemes needed |

### 4. Relationships Between Dimensionless Numbers

```
┌─────────────────────────────────────────────────────────┐
│                    Reynolds (Re)                        │
│              Ratio: Inertial / Viscous                  │
└──────────────────┬──────────────────────────────────────┘
                   │
                   │ × Prandtl (Pr)
                   │   Ratio: Momentum / Thermal Diffusion
                   ▼
┌─────────────────────────────────────────────────────────┐
│                    Peclet (Pe)                          │
│              Ratio: Convection / Diffusion              │
└──────────────────┬──────────────────────────────────────┘
                   │
                   │ × Nusselt (Nu)
                   │   Ratio: Convection / Conduction
                   ▼
┌─────────────────────────────────────────────────────────┐
│              Stanton (St = Nu/(Re·Pr))                   │
│              Ratio: Actual / Maximum Heat Transfer      │
└─────────────────────────────────────────────────────────┘
```

**Summary:**
- **Pr** = Fluid property (momentum vs thermal diffusion)
- **Re** = Flow condition (inertia vs viscosity)
- **Pe** = Heat transfer regime (convection vs diffusion)
- **Nu** = Heat transfer effectiveness (convection vs conduction)
- **St** = Efficiency (actual vs maximum possible)

---

## Key Takeaways

### 1. Summary Table: Three Energy Forms

| Aspect | Temperature (T) | Enthalpy (h) | Internal Energy (e) |
|--------|----------------|--------------|---------------------|
| **Mathematical Form** | $T$ | $h = e + p/\rho$ | $e$ |
| **Energy Type** | Indirect (via $C_p$) | Flow work included | Molecular energy only |
| **Primary Use Case** | Incompressible, small ΔT | Compressible, natural convection | High-temperature, combustion |
| **OpenFOAM Energy Keyword** | N/A | `sensibleEnthalpy` | `sensibleInternalEnergy` |
| **Equation of State** | `rhoConst` | `perfectGas` | `perfectGas` |
| **Typical Solvers** | `buoyantBoussinesqSimpleFoam` | `buoyantSimpleFoam`, `buoyantPimpleFoam` | `rhoPimpleFoam`, `reactingFoam` |
| **Complexity** | ★☆☆ Simplest | ★★☆ Standard | ★★★ Most complex |
| **Computational Cost** | Lowest | Medium | Highest |
| **Physical Accuracy** | Low (limited range) | High | Highest |
| **Pressure Work** | Neglected | Included | Included |
| **Viscous Dissipation** | Neglected | Included | Included |
| **Convergence Speed** | Fastest | Medium | Slowest |
| **Memory Usage** | Minimal | Moderate | High |
| **Best For** | Simple convection | General CFD | Combustion/reactions |

### 2. Decision Flowchart

```
┌─────────────────────────────────────────────────────────────────┐
│                    ENERGY FORM SELECTION                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Start Problem                                                  │
│       │                                                         │
│       ├─ Is ρ essentially constant? (Δρ/ρ < 0.05)               │
│       │   ├─ YES → Use Temperature (T) form                     │
│       │   │         Solver: buoyantBoussinesqSimpleFoam         │
│       │   │         Energy: Not specified (direct T)            │
│       │   │         EoS: rhoConst                               │
│       │   │                                                      │
│       │   └─ NO → Continue                                      │
│       │                                                          │
│       ├─ Is pressure work significant? (Ma > 0.3 or large Δp)   │
│       │   ├─ YES → Use Enthalpy (h) form                        │
│       │   │         Energy: sensibleEnthalpy                    │
│       │   │         Solver: buoyantSimpleFoam / buoyantPimpleFoam│
│       │   │         EoS: perfectGas                             │
│       │   │                                                      │
│       │   └─ NO → Consider Internal Energy (e) form             │
│       │           Energy: sensibleInternalEnergy                │
│       │           Solver: rhoPimpleFoam                         │
│       │           EoS: perfectGas                               │
│       │                                                          │
└─────────────────────────────────────────────────────────────────┘
```

### 3. Essential Equations

| Concept | Equation | When to Use |
|---------|----------|-------------|
| **Fourier's Law** | $\mathbf{q} = -k\nabla T$ | All heat transfer problems |
| **Energy (T-form)** | $\frac{DT}{Dt} = \alpha\nabla^2 T + \frac{Q}{\rho c_p}$ | Incompressible, small ΔT |
| **Energy (h-form)** | $\frac{\partial(\rho h)}{\partial t} + \nabla\cdot(\rho\mathbf{u}h) = \nabla\cdot(k\nabla T) + \frac{Dp}{Dt} + Q$ | Compressible, natural convection |
| **Energy (e-form)** | $\frac{\partial(\rho e)}{\partial t} + \nabla\cdot(\rho\mathbf{u}e) = \nabla\cdot(k\nabla T) - p\nabla\cdot\mathbf{u} + Q$ | Fundamental, combustion |
| **Effective Diffusivity** | $\alpha_{eff} = \frac{\nu}{Pr} + \frac{\nu_t}{Pr_t}$ | Turbulent flows |
| **Prandtl Number** | $Pr = \frac{\mu c_p}{k}$ | Characterize fluid properties |
| **Nusselt Number** | $Nu = \frac{hL}{k}$ | Heat transfer coefficient calculation |
| **Peclet Number** | $Pe = \frac{uL}{\alpha} = Re \cdot Pr$ | Convection vs diffusion regime |
| **Thermal Diffusivity** | $\alpha = \frac{k}{\rho c_p}$ | Heat conduction rate |

### 4. Common Mistakes to Avoid

1. ❌ **Using wrong energy variable** for your solver:
   - Always check `energy` keyword in `thermophysicalProperties`
   - Ensure BCs match the energy form (T vs h vs e)

2. ❌ **Inconsistent boundary conditions**:
   - If `energy` is `sensibleEnthalpy`, use `h` field for BCs, not `T`
   - Value conversion: $h \approx C_p \times T$ (for constant $C_p$)

3. ❌ **Ignoring turbulence effects**:
   - For turbulent flows, always use `alphaEff()` instead of `alpha()`
   - Use $Pr_t \approx 0.85$ for turbulent flows, not molecular $Pr$

4. ❌ **Wrong thermophysical model**:
   - `hConst` assumes constant $C_p$ — use `polynomial` for large temperature ranges
   - `janaf` for high-temperature applications (combustion)

5. ❌ **Neglecting viscous dissipation**:
   - Important in high-speed flows (Ma > 1)
   - Included automatically in h-form and e-form

6. ❌ **Wrong Prandtl number**:
   - Use molecular $Pr$ (fluid property) in `thermophysicalProperties`
   - Use turbulent $Pr_t$ (≈ 0.85) in wall boundary conditions

### 5. Best Practices

1. **Start simple**: Begin with T-form if applicable, upgrade to h-form/e-form as needed
2. **Verify consistency**: Ensure `energy` keyword matches solver expectations
3. **Check convergence**: Monitor residual levels for energy equation
4. **Validate results**: Compare with analytical solutions or experimental data
5. **Document choices**: Record why specific energy form was selected
6. **Use appropriate discretization schemes**:
   - Upwind for high Pe (convection-dominated)
   - Central differencing for low Pe (diffusion-dominated)

---

## Concept Check

<details>
<summary><b>1. อะไรคือความแตกต่างหลักระหว่าง Enthalpy (h) และ Internal Energy (e)?</b></summary>

**คำตอบ:**

- **Enthalpy (h)**: รวม flow work ($p/\rho$) เข้าไว้แล้ว
  - เหมาะกับ open systems ที่มีการไหลเข้า-ออกของ control volume
  - ใช้ใน most compressible flow solvers
  - คำนวณ: $h = e + p/\rho$

- **Internal Energy (e)**: พลังงานระดับโมเลกุลเท่านั้น
  - เหมาะกับ closed systems หรือเมื่อต้องการความแม่นยำในระดับพื้นฐาน
  - ใช้ใน combustion และ reacting flows
  - property ของ substance (ไม่ขึ้นกับ flow)

**ใน OpenFOAM:**
```cpp
h = thermo.he();              // For sensibleEnthalpy
e = thermo.he() - p/rho;      // For sensibleInternalEnergy
```

**Key difference**: Enthalpy automatically accounts for work done by pressure forces during flow into/out of control volume.
</details>

<details>
<summary><b>2. ทำไม Turbulent Prandtl Number ($Pr_t$) มีค่า ≈ 0.85 ไม่ใช่ 1.0?</b></summary>

**คำตอบ:**

ค่าเชิงประจักษ์จากการทดลองแสดงว่า:

1. **Momentum และ heat diffuse ด้วยอัตราใกล้เคียงกัน**
   - ทำให้ $Pr_t \approx 1$ (theoretical expectation)

2. **แต่ไม่เท่ากันทีเดียว**
   - Turbulent eddies transport momentum ได้ดีกว่า heat เล็กน้อย
   - ค่า 0.85 ให้ผลลัพธ์ที่ตรงกับการทดลองสำหรับ most flows

**Physical reasons:**
- **Different length scales**: Velocity and temperature fluctuations have different scales
- **Pressure-velocity correlations**: Present in momentum transport, enhance $\nu_t$
- **No pressure-temperature correlations**: Absent in heat transport
- **Buoyancy effects**: Can affect temperature but not momentum directly

**Practical impact:**
```cpp
// In thermophysicalProperties
transport { Pr 0.71; }      // Molecular Prandtl (fluid property)

// In boundary conditions
wall { Prt 0.85; }          // Turbulent Prandtl (empirical constant)
```
</details>

<details>
<summary><b>3. เมื่อไหร่ควรใช้ Temperature form (T) แทน Enthalpy form (h)?</b></summary>

**คำตอบ:**

**ใช้ T-form เมื่อ:**
1. Fluid is essentially incompressible ($\Delta\rho/\rho < 0.05$)
2. Temperature variations are small ($\Delta T < 50$ K)
3. Computational speed is priority
4. Using Boussinesq approximation for buoyancy

**ใช้ h-form เมื่อ:**
1. Fluid is compressible (Ma > 0.3 หรือมี compression/expansion อย่างมีนัยสำคัญ)
2. Natural convection ที่ density changes เป็นสำคัญ
3. ต้องการ physical accuracy สูง
4. Pressure work cannot be neglected

**Decision criterion:**
- If density variations affect flow physics significantly → use h-form
- If $\Delta T$ is small and density ≈ constant → use T-form

**Example:**
```cpp
// Room heating with ΔT = 10 K → T-form
Solver: buoyantBoussinesqSimpleFoam

// Combustion chamber with ΔT = 2000 K → h-form or e-form
Solver: reactingFoam (e-form) or buoyantSimpleFoam (h-form)
```
</details>

<details>
<summary><b>4. ถ้า `energy` keyword คือ `sensibleEnthalpy` แต่ solver ใช้ `buoyantBoussinesqSimpleFoam` จะเกิดอะไรขึ้น?</b></summary>

**คำตอบ:**

จะเกิด **inconsistency**:

- `buoyantBoussinesqSimpleFoam` ใช้ **T-form** (solves for T directly)
- แต่ `sensibleEnthalpy` บอก OpenFOAM ว่าควรใช้ **h-form**

**Result**: Solver อาจไม่ทำงาน หรือให้ผิดพลาด เพราะ:
1. Boundary conditions อาจถูกตั้งเป็น `h` แต่ solver ต้องการ `T`
2. `thermo.correct()` จะ convert h → T ซึ่งไม่จำเป็นสำหรับ Boussinesq

**Solution**:
```cpp
// For buoyantBoussinesqSimpleFoam, this is acceptable:
thermoType
{
    type            heRhoThermo;
    mixture         pureMixture;
    transport       const;
    thermo          hConst;
    equationOfState rhoConst;           // ← This makes it effectively T-form
    energy          sensibleEnthalpy;   // Still used internally, but ρ = const
}

// OR use true h-form solver:
// Change to: buoyantSimpleFoam (compressible, h-form)
```
</details>

<details>
<summary><b>5. ความสัมพันธ์ระหว่าง Pr, Re, Pe และ Nu คืออะไร?</b></summary>

**คำตอบ:**

**Prandtl (Pr):** อัตราส่วนระหว่าง momentum diffusion และ thermal diffusion
$$Pr = \frac{\nu}{\alpha} = \frac{\mu c_p}{k}$$
- **Property of fluid** (ไม่ขึ้นกับ flow conditions)
- Air: 0.71, Water: 7.0, Oil: ~100

**Reynolds (Re):** อัตราส่วนระหว่าง inertial forces และ viscous forces
$$Re = \frac{\rho u L}{\mu} = \frac{u L}{\nu}$$
- **Flow condition** (ขึ้นกับ velocity, geometry)

**Peclet (Pe):** ผลคูณของ Re และ Pr — อัตราส่วนระหว่าง convection และ diffusion
$$Pe = Re \times Pr = \frac{u L}{\nu} \times \frac{\nu}{\alpha} = \frac{u L}{\alpha}$$

**Nusselt (Nu):** อัตราส่วนระหว่าง convective heat transfer และ conductive heat transfer
$$Nu = \frac{h L}{k}$$
- Nu = 1: Pure conduction (no convection)
- Nu > 1: Convection enhances heat transfer

**Stanton (St):** อัตราส่วนระหว่าง actual heat transfer และ maximum possible
$$St = \frac{Nu}{Re \cdot Pr} = \frac{Nu}{Pe}$$

**Hierarchy:**
```
Re (flow condition)
    ↓
    × Pr (fluid property)
    ↓
Pe (heat transfer regime)
    ↓
    Nu (effectiveness)
    ↓
St (efficiency)
```
</details>

<details>
<summary><b>6. ทำไมต้องมีการใช้ alphaEff แทน alpha ใน turbulent flow?</b></summary>

**คำตอบ:**

ใน turbulent flow การถ่ายเทความร้อนเกิดจาก **2 กลไก**:

1. **Molecular diffusion** ($\alpha = \frac{k}{\rho c_p}$):
   - การนำความร้อนระดับโมเลกุล
   - ค่าคงที่ (property of fluid)
   - สำคัญใน laminar flow

2. **Turbulent eddies** ($\alpha_t = \frac{\nu_t}{Pr_t}$):
   - การผสมผสานโดย turbulent eddies
   - ค่าตาม position (field quantity)
   - $\nu_t \gg \nu$ ใน turbulent regions

**alphaEff** รวมทั้ง 2 กลไก:
$$\alpha_{eff} = \alpha + \alpha_t$$

**Behavior:**
- **Laminar flow**: $\alpha_{eff} \approx \alpha$ (เพราะ $\nu_t \approx 0$)
- **Turbulent flow**: $\alpha_{eff} \gg \alpha$ (เพราะ $\nu_t \gg \nu$)

**OpenFOAM implementation:**
```cpp
// Laminar flow (or near walls)
volScalarField alpha = turbulence->alpha();

// Turbulent flow (always use this for turbulence!)
volScalarField alphaEff = turbulence->alphaEff();

// In energy equation
-fvm::laplacian(turbulence->alphaEff(), h)  // Correct for turbulence
```

**Consequences of using wrong alpha:**
- ใช้ `alpha()` ใน turbulent flow → Underpredict heat transfer (missing $\alpha_t$)
- ใช้ `alphaEff()` ใน laminar flow → No harm (alphaEff = alpha when $\nu_t = 0$)
</details>

<details>
<summary><b>7. ทำไมต้องมีการเรียก thermo.correct() หลังจาก solve energy equation?</b></summary>

**คำตอบ:**

`thermo.correct()` ทำหน้าที่ **update temperature จาก energy variable**:

**For h-form:**
```cpp
// Solve: hEqn.solve();

// Then:
thermo.correct();  // Converts: h → T

// Internally (simplified):
T = (h - Hf) / Cp;  // Inverts: h = Cp*T + Hf
```

**For e-form:**
```cpp
// Solve: eEqn.solve();

// Then:
thermo.correct();  // Converts: e → T

// Internally (simplified):
T = (e - Hf) / Cv;  // Inverts: e = Cv*T + Hf
```

**Why needed:**
1. **Energy equation solves for h or e** (not T directly)
2. **Other equations need T** (equation of state, buoyancy, etc.)
3. **Post-processing needs T** (visualization, analysis)

**Without thermo.correct():**
- Temperature field would be outdated
- Density calculation would be wrong ($\rho = \rho(p,T)$)
- Buoyancy force would be incorrect ($F_b \propto \Delta T$)

**For T-form:**
- No need for thermo.correct() (T is solved directly)
- But thermo.correct() is still called for consistency
</details>

---

## Related Documents

- **ภาพรวม Heat Transfer**: [00_Overview.md](00_Overview.md) — thermophysicalProperties แบบละเอียด
- **กลไกการถ่ายเทความร้อน**: [02_Heat_Transfer_Mechanisms.md](02_Heat_Transfer_Mechanisms.md) — conduction, convection, radiation
- **Buoyancy-Driven Flows** (รายละเอียด Boussinesq): [03_Buoyancy_Driven_Flows.md](03_Buoyancy_Driven_Flows.md) — natural convection, Rayleigh number
- **Conjugate Heat Transfer**: [04_Conjugate_Heat_Transfer.md](04_Conjugate_Heat_Transfer.md) — solid-fluid coupling
- **Turbulence Modeling**: [../../03_TURBULENCE_MODELING/00_Overview.md](../../03_TURBULENCE_MODELING/00_Overview.md) — turbulence models สำหรับ heat transfer