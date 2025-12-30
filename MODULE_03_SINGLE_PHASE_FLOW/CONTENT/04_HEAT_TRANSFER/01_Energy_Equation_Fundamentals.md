# Energy Equation Fundamentals

พื้นฐานสมการพลังงานใน OpenFOAM

---

## Learning Objectives

หลังจากอ่านบทนี้ คุณจะสามารถ:

- **อธิบาย (WHAT)** สมการพลังงานในรูปแบบต่างๆ (Temperature, Enthalpy, Internal Energy) และกฎของฟูริเยร์
- **วิเคราะห์ (WHY)** ความแตกต่างระหว่างรูปแบบพลังงานทั้ง 3 และการเลือกใช้งานที่เหมาะสมกับแต่ละสถานการณ์
- **ประยุกต์ (HOW)** ตั้งค่า thermophysicalProperties เลือก solver ที่เหมาะสม และเขียนสมการพลังงานใน OpenFOAM

---

## What is the Energy Equation?

### Basic Definition

สมการพลังงาน (Energy Equation) คือกฎข้อที่สองของเทอร์โมไดนามิกส์ที่ใช้กับระบบไหลเวียน (fluid systems) ซึ่งอธิบายการถ่ายเทความร้อน การเปลี่ยนแปลงของพลังงาน และงานที่เกิดขึ้นในของไหล

### Conservation Form

$$\frac{\partial (\rho E)}{\partial t} + \nabla \cdot (\rho \mathbf{u} E) = \nabla \cdot (k \nabla T) - \nabla \cdot (p \mathbf{u}) + \nabla \cdot (\boldsymbol{\tau} \cdot \mathbf{u}) + Q$$

**Where:**
- $E = e + \frac{1}{2}|\mathbf{u}|^2$ = total energy per unit mass [J/kg]
- $e$ = internal energy [J/kg]
- $\mathbf{u}$ = velocity vector [m/s]
- $p$ = pressure [Pa]
- $k$ = thermal conductivity [W/(m·K)]
- $\boldsymbol{\tau}$ = viscous stress tensor
- $Q$ = heat source/sink [W/m³]

### Physical Terms Breakdown

| Term | Mathematical Expression | Physical Meaning |
|------|------------------------|------------------|
| **Unsteady** | $\frac{\partial (\rho E)}{\partial t}$ | Rate of energy change with time |
| **Convection** | $\nabla \cdot (\rho \mathbf{u} E)$ | Energy transport due to fluid motion |
| **Conduction** | $\nabla \cdot (k \nabla T)$ | Heat diffusion (Fourier's law) |
| **Pressure Work** | $-\nabla \cdot (p \mathbf{u})$ | Work done by pressure forces |
| **Viscous Dissipation** | $\nabla \cdot (\boldsymbol{\tau} \cdot \mathbf{u})$ | Conversion of kinetic energy to heat |
| **Source** | $Q$ | Heat generation/absorption |

---

## Why Different Forms Matter?

### Three Forms in OpenFOAM

OpenFOAM จัดเตรียมสมการพลังงานใน 3 รูปแบบหลัก ขึ้นอยู่กับ **ลักษณะของปัญหา** และ **ความแม่นยำที่ต้องการ**:

| Form | Mathematical Variable | Energy Type | Primary Use Case | Key Advantage |
|------|----------------------|-------------|------------------|----------------|
| **Temperature (T)** | $T$ | None directly | Incompressible flows with small ΔT | Simplest form, fastest convergence |
| **Enthalpy (h)** | $h = e + p/\rho$ | Flow work included | Compressible flows, significant pressure changes | Automatically accounts for compression work |
| **Internal Energy (e)** | $e$ | Molecular energy only | High-temperature flows, combustion | More fundamental, avoids ambiguity |

### Physical Interpretation

**WHAT (ความหมาย):**
- **Temperature (T)**: ตัวแปรหนึ่งเดียวที่วัดง่าย แต่ไม่ได้วัดพลังงานโดยตรง
- **Enthalpy (h)**: พลังงานที่รวม flow work ($p/\rho$) เข้าไว้ด้วย — สำคัญใน open systems
- **Internal Energy (e)**: พลังงานระดับโมเลกุล (kinetic + potential) ของโมเลกุล

**WHY (ทำไมต้องแยก):**
- **Computational Efficiency**: T-form เร็วที่สุด เหมาะกับปัญหาที่ $\rho \approx$ constant
- **Physical Accuracy**: h-form จำเป็นเมื่อ pressure work สำคัญ (compressible flows)
- **Numerical Stability**: e-form บางครั้งให้การลู่เข้าที่ดีกว่าใน high-temperature flows

**HOW (เมื่อไหร่ใช้อะไร):**
- ใช้ **T-form** เมื่อ: $\Delta T < 50$ K, $\Delta \rho/\rho < 0.05$, incompressible
- ใช้ **h-form** เมื่อ: Ma > 0.3, มี compression/expansion อย่างมีนัยสำคัญ
- ใช้ **e-form** เมื่อ: T > 1500 K, combustion, detailed thermodynamics

### Comparison Matrix

| Criterion | Temperature (T) | Enthalpy (h) | Internal Energy (e) |
|-----------|----------------|--------------|---------------------|
| **Complexity** | ★☆☆ Simplest | ★★☆ Standard | ★★★ Most complex |
| **Computational Cost** | Lowest | Medium | Highest |
| **Physical Accuracy** | Low (limited range) | High | Highest |
| **Convergence Speed** | Fastest | Medium | Slowest |
| **Memory Usage** | Minimal | Moderate | High |
| **Best For** | Simple convection | General CFD | Combustion/reactions |

---

## How It's Implemented in OpenFOAM

### 1. Thermophysical Properties Dictionary

OpenFOAM ใช้ `thermophysicalProperties` dictionary เพื่อกำหนดรูปแบบพลังงาน:

```cpp
// constant/thermophysicalProperties

thermoType
{
    // รูปแบบพลังงานที่เลือกใช้
    type            hePsiThermo;          // หรือ heRhoThermo
    mixture         pureMixture;          // สำหรับ single fluid

    // โมเดล transport (viscosity, thermal conductivity)
    transport       const;                // const | polynomial | sutherland

    // โมเดล thermodynamic properties (Cp, Hf)
    thermo          hConst;               // hConst | polynomial | janaf

    // สมการสถานะ (equation of state)
    equationOfState perfectGas;           // perfectGas | rhoConst | incompressiblePerfectGas

    // รูปแบบพลังงาน — สำคัญมาก!
    energy          sensibleEnthalpy;     // sensibleEnthalpy | sensibleInternalEnergy | absoluteEnthalpy
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
        Pr              0.71;              // Prandtl number
        // หรือใช้ k (thermal conductivity) โดยตรง:
        // k               0.0261;           // [W/(m·K)]
    }
}
```

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

### 3. Key Implementation Differences

| Aspect | T-form | h-form | e-form |
|--------|--------|--------|--------|
| **Primary Variable** | `volScalarField T` | `volScalarField h` | `volScalarField e` |
| **Density Treatment** | Constant ($\rho_0$) | Variable ($\rho(p,T)$) | Variable ($\rho(p,e)$) |
| **Boundary Conditions** | `fixedValue` for T | `fixedValue` for h | `fixedValue` for e |
| **Source Terms** | `fvModels.source(T)` | `fvModels.source(rho, h)` | `fvModels.source(rho, e)` |
| **Post-Processing** | Direct T output | `thermo.T()` | `thermo.T()` |
| **Energy Variable** | N/A | `he` (enthalpy) | `he` (internal energy) |
| **Pressure Work** | Neglected | Included ($Dp/Dt$) | Included ($p\nabla\cdot u$) |
| **Viscous Dissipation** | Neglected | Included | Included |

### 4. Thermodynamic Correction

After solving for energy, OpenFOAM automatically converts to temperature:

```cpp
// In thermophysicalModel library
template<class BasicThermo, class Thermo>
BasicThermo::thermoType::he Thermo::HE
(
    const Thermo& thermo,
    const typename Thermo::solutionType& solution,
    const typename Thermo::solutionType& p,
    const typename Thermo::solutionType& T
)
{
    // For sensibleEnthalpy:
    return thermo.Cp()*T + thermo.Hf();  // h = Cp*T + Hf

    // For sensibleInternalEnergy:
    return thermo.Cv()*T + thermo.Hf();  // e = Cv*T + Hf
}
```

### 5. Solver Mapping

| Solver | Energy Form | Equation of State | Key Characteristic |
|--------|-------------|-------------------|-------------------|
| `buoyantBoussinesqSimpleFoam` | Temperature | `rhoConst` | Incompressible, small ΔT |
| `buoyantSimpleFoam` | Enthalpy | `perfectGas` | Steady, compressible |
| `buoyantPimpleFoam` | Enthalpy | `perfectGas` | Transient, compressible |
| `rhoPimpleFoam` | Internal Energy | `perfectGas` | High-speed, compressible |
| `rhoSimpleFoam` | Enthalpy/Energy | `perfectGas` | Steady high-speed |
| `chtMultiRegionFoam` | Enthalpy | Varies | Conjugate heat transfer |

---

## Fourier's Law: Heat Conduction Mechanism

### WHAT: Definition

กฎของฟูริเยร์ (Fourier's Law) อธิบายการนำความร้อน (heat conduction) ซึ่งเป็นกลไกพื้นฐานที่สุดของการถ่ายเทความร้อน

$$\mathbf{q} = -k \nabla T$$

### WHY: Physical Interpretation

| Symbol | Physical Meaning | Unit | Typical Value (Air at 300 K) |
|--------|------------------|------|------------------------------|
| $\mathbf{q}$ | Heat flux vector | W/m² | - |
| $k$ | Thermal conductivity | W/(m·K) | 0.026 |
| $\nabla T$ | Temperature gradient | K/m | - |

**Negative Sign**: Heat flows from hot to cold (opposite to gradient direction)

**Physical Meaning**: Heat flux is proportional to temperature gradient — larger gradient → larger heat flux

### Thermal Conductivity Values

| Material | k [W/(m·K)] | Application |
|----------|-------------|-------------|
| **Copper** | 401 | Heat exchangers, cooling systems |
| **Aluminum** | 237 | Heat sinks, automotive parts |
| **Steel** | 50-60 | Structural components |
| **Water** | 0.6 | Liquid cooling |
| **Air** | 0.026 | Insulation, ambient convection |
| **Insulation** | 0.02-0.05 | Building materials |

### HOW: Implementation in OpenFOAM

```cpp
// Laminar thermal diffusivity
volScalarField alpha = turbulence->alpha();  // α = k/(ρcp)

// Effective thermal diffusivity (with turbulence)
volScalarField alphaEff = turbulence->alphaEff();  // α_eff = α + α_t

// Heat conduction term in energy equation
-fvm::laplacian(alphaEff, T)  // -∇·(α_eff ∇T) = -∇·(k/(ρcp) ∇T)
```

**Discretization Details**:
- `fvm::laplacian()` uses implicit discretization for stability
- `alphaEff` combines molecular and turbulent diffusivity
- Negative sign automatically handled by OpenFOAM's finite volume formulation

---

## Turbulent Heat Transfer

### WHAT: Effective Diffusivity

ใน turbulent flow การถ่ายเทความร้อนเกิดจากทั้ง **molecular diffusion** และ **turbulent eddies**:

$$\alpha_{eff} = \alpha + \alpha_t = \frac{\nu}{Pr} + \frac{\nu_t}{Pr_t}$$

### WHY: Reynolds Analogy

| Mechanism | Momentum Diffusivity | Thermal Diffusivity | Ratio |
|-----------|---------------------|---------------------|-------|
| Molecular | $\nu = \mu/\rho$ | $\alpha = k/(\rho c_p)$ | $Pr = \nu/\alpha$ |
| Turbulent | $\nu_t$ | $\alpha_t$ | $Pr_t = \nu_t/\alpha_t$ |

**Prandtl Number ($Pr$)**: สัดส่วนระหว่าง diffusion ของ momentum และ heat

**Turbulent Prandtl Number ($Pr_t$)**: สัดส่วนเดียวกันใน turbulent flow — ค่าทดลอง ≈ 0.85-0.90

**Physical Interpretation**:
- $Pr \ll 1$: Heat diffuses much faster than momentum (liquid metals)
- $Pr \approx 1$: Similar diffusion rates (gases)
- $Pr \gg 1$: Momentum diffuses much faster than heat (oils)

### HOW: OpenFOAM Implementation

```cpp
// In turbulenceModel library
tmp<volScalarField> kappat() const
{
    return tmp<volScalarField>
    (
        new volScalarField
        (
            IOobject
            (
                "kappat",
                mesh_.time().timeName(),
                mesh_,
                IOobject::NO_READ,
                IOobject::NO_WRITE
            ),
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
```

| Parameter | Symbol | Value (Air) | Value (Water) | Value (Liquid Metal) |
|-----------|--------|-------------|---------------|---------------------|
| Molecular Pr | $Pr$ | 0.71 | 7.0 | ~0.01 |
| Turbulent Pr | $Pr_t$ | 0.85 | 0.85 | 0.85 |

### Wall Functions for Heat Transfer

OpenFOAM จัดเตรียม wall functions สำหรับ turbulent heat transfer:

```cpp
// In boundary conditions
wall
{
    type            compressible::alphatWallFunction;
    Prt             0.85;              // Turbulent Prandtl number
    value           uniform 0;         // Initial value
}
```

---

## Dimensionless Numbers

### Prandtl Number (Pr)

$$Pr = \frac{\nu}{\alpha} = \frac{\mu c_p}{k}$$

**Physical Meaning**: อัตราส่วนของความหนา (thickness) ระหว่าง velocity boundary layer และ thermal boundary layer

| Fluid | Pr | Characteristics | Boundary Layer Relation |
|-------|---:|-----------------|------------------------|
| **Liquid metals** | ~0.01 | Thermal layer >> velocity layer | $\delta_T \gg \delta$ |
| **Air** | 0.71 | Similar thickness | $\delta_T \approx \delta$ |
| **Water** | 7.0 | Velocity layer >> thermal layer | $\delta_T \ll \delta$ |
| **Oil** | ~100 | Thermal layer very thin | $\delta_T \ll \delta$ |

**Prandtl Number Effect on Heat Transfer**:
- Low Pr: Thermal effects penetrate deeper into flow
- High Pr: Thermal effects confined near wall

### Nusselt Number (Nu)

$$Nu = \frac{hL}{k} = \frac{\text{convective heat transfer}}{\text{conductive heat transfer}}$$

**Physical Meaning**: อัตราเพิ่มของ heat transfer จาก convection เมื่อเทียบกับ conduction เท่านั้น

**Typical Correlations**:
- **Laminar flow over flat plate**: $Nu = 0.664 Re^{1/2} Pr^{1/3}$
- **Turbulent flow over flat plate**: $Nu = 0.037 Re^{4/5} Pr^{1/3}$
- **Pipe flow (laminar)**: $Nu = 3.66$ (constant wall temperature)
- **Pipe flow (turbulent)**: $Nu = 0.023 Re^{0.8} Pr^{0.4}$ (Dittus-Boelter)

### Peclet Number (Pe)

$$Pe = Re \cdot Pr = \frac{uL}{\alpha}$$

**Physical Meaning**: อัตราส่วนระหว่าง convective และ diffusive heat transfer

| Regime | Pe | Dominant Mechanism | Numerical Consideration |
|--------|---:|-------------------|------------------------|
| $Pe < 1$ | Diffusion dominates | Conduction | Standard discretization OK |
| $Pe > 1$ | Convection dominates | Advection | May need upwind schemes |
| $Pe \gg 1$ | Strong convection | Advection-dominated | High-resolution schemes needed |

### Relationship Between Dimensionless Numbers

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
└─────────────────────────────────────────────────────────┘

                   │
                   │ × Nusselt (Nu)
                   │   Ratio: Convection / Conduction
                   ▼
┌─────────────────────────────────────────────────────────┐
│              Stanton (St = Nu/(Re·Pr))                   │
│              Ratio: Actual / Maximum Heat Transfer      │
└─────────────────────────────────────────────────────────┘
```

---

## Key Takeaways

### Summary Table: Three Energy Forms

| Aspect | Temperature (T) | Enthalpy (h) | Internal Energy (e) |
|--------|----------------|--------------|---------------------|
| **Mathematical Form** | $T$ | $h = e + p/\rho$ | $e$ |
| **Energy Type** | Indirect (via $C_p$) | Flow work included | Molecular energy only |
| **Primary Use Case** | Incompressible, small ΔT | Compressible, natural convection | High-temperature, combustion |
| **OpenFOAM Energy Keyword** | N/A | `sensibleEnthalpy` | `sensibleInternalEnergy` |
| **thermophysicalProperties** | `rhoConst` EoS | `perfectGas` EoS | `perfectGas` EoS |
| **Typical Solvers** | `buoyantBoussinesqSimpleFoam` | `buoyantSimpleFoam`, `buoyantPimpleFoam` | `rhoPimpleFoam`, `reactingFoam` |
| **Complexity** | ★☆☆ Simplest | ★★☆ Standard | ★★★ Most complex |
| **Computational Cost** | Lowest | Medium | Highest |
| **Physical Accuracy** | Low (limited range) | High | Highest |
| **Pressure Work** | Neglected | Included | Included |
| **Convergence Speed** | Fastest | Medium | Slowest |

### Decision Flowchart

```
Start
 │
 ├─ Is fluid essentially incompressible (Δρ/ρ < 0.05)?
 │   ├─ YES → Use Temperature (T) form
 │   │         Solver: buoyantBoussinesqSimpleFoam
 │   │         Energy: Not specified (direct T)
 │   │         EoS: rhoConst
 │   │
 │   └─ NO → Continue
 │
 ├─ Is pressure work significant (Ma > 0.3 or large Δp)?
 │   ├─ YES → Use Enthalpy (h) form
 │   │         Energy: sensibleEnthalpy
 │   │         Solver: buoyantSimpleFoam / buoyantPimpleFoam
 │   │         EoS: perfectGas
 │   │
 │   └─ NO → Consider Internal Energy (e) form
 │           Energy: sensibleInternalEnergy
 │           Solver: rhoPimpleFoam
 │           EoS: perfectGas
 │
End
```

### Essential Equations

| Concept | Equation | When to Use |
|---------|----------|-------------|
| **Fourier's Law** | $\mathbf{q} = -k\nabla T$ | All heat transfer |
| **Energy (T-form)** | $\frac{DT}{Dt} = \alpha\nabla^2 T + \frac{Q}{\rho c_p}$ | Incompressible |
| **Energy (h-form)** | $\frac{\partial(\rho h)}{\partial t} + \nabla\cdot(\rho\mathbf{u}h) = \nabla\cdot(k\nabla T) + \frac{Dp}{Dt} + Q$ | Compressible |
| **Energy (e-form)** | $\frac{\partial(\rho e)}{\partial t} + \nabla\cdot(\rho\mathbf{u}e) = \nabla\cdot(k\nabla T) - p\nabla\cdot\mathbf{u} + Q$ | Fundamental |
| **Effective Diffusivity** | $\alpha_{eff} = \frac{\nu}{Pr} + \frac{\nu_t}{Pr_t}$ | Turbulent flows |
| **Prandtl Number** | $Pr = \frac{\mu c_p}{k}$ | Characterize fluid |
| **Nusselt Number** | $Nu = \frac{hL}{k}$ | Heat transfer coefficient |
| **Peclet Number** | $Pe = \frac{uL}{\alpha} = Re \cdot Pr$ | Convection vs diffusion |

### Common Mistakes to Avoid

1. ❌ **Using wrong energy variable** for your solver: Always check `energy` keyword in `thermophysicalProperties`
2. ❌ **Inconsistent boundary conditions**: If `energy` is `sensibleEnthalpy`, use `h` field for BCs, not `T`
3. ❌ **Ignoring turbulence effects**: For turbulent flows, always use `alphaEff()` instead of `alpha()`
4. ❌ **Wrong thermophysical model**: `hConst` assumes constant $C_p$ — use `polynomial` for large temperature ranges
5. ❌ **Neglecting viscous dissipation**: Important in high-speed flows (Ma > 1)
6. ❌ **Wrong Prandtl number**: Use $Pr_t \approx 0.85$ for turbulent flows, not molecular $Pr$

### Quick Reference: thermophysicalProperties

```cpp
// INCOMPRESSIBLE + BOUSSINESQ (T-form)
thermoType
{
    type            heRhoThermo;
    mixture         pureMixture;
    transport       const;
    thermo          hConst;
    equationOfState rhoConst;           // ← Constant density
    energy          sensibleEnthalpy;   // ← Enthalpy form (still used internally)
}

// COMPRESSIBLE (h-form)
thermoType
{
    type            hePsiThermo;
    mixture         pureMixture;
    transport       const;
    thermo          hConst;
    equationOfState perfectGas;         // ← Variable density
    energy          sensibleEnthalpy;   // ← Enthalpy form
}

// HIGH-TEMPERATURE (e-form)
thermoType
{
    type            hePsiThermo;
    mixture         pureMixture;
    transport       sutherland;         // ← T-dependent viscosity
    thermo          janaf;              // ← T-dependent Cp
    equationOfState perfectGas;
    energy          sensibleInternalEnergy;  // ← Internal energy form
}
```

### Best Practices

1. **Start simple**: Begin with T-form if applicable, upgrade to h-form/e-form as needed
2. **Verify consistency**: Ensure `energy` keyword matches solver expectations
3. **Check convergence**: Monitor residual levels for energy equation
4. **Validate results**: Compare with analytical solutions or experimental data
5. **Document choices**: Record why specific energy form was selected

---

## Concept Check

<details>
<summary><b>1. อะไรคือความแตกต่างหลักระหว่าง Enthalpy (h) และ Internal Energy (e)?</b></summary>

- **Enthalpy (h)**: รวม flow work ($p/\rho$) เข้าไว้แล้ว — เหมาะกับ open systems ที่มีการไหลเข้า-ออกของขอบเขต (boundary)
- **Internal Energy (e)**: พลังงานระดับโมเลกุลเท่านั้น — เหมาะกับ closed systems หรือเมื่อต้องการความแม่นยำในระดับพื้นฐาน

ใน OpenFOAM: `h = he` และ `e = he - p/rho`

**Key difference**: Enthalpy automatically accounts for work done by pressure forces during flow into/out of control volume.
</details>

<details>
<summary><b>2. ทำไม Turbulent Prandtl Number ($Pr_t$) มีค่า ≈ 0.85 ไม่ใช่ 1.0?</b></summary>

ค่าเชิงประจักษ์จากการทดลองแสดงว่า:
- Momentum และ heat diffuse ด้วยอัตราใกล้เคียงกัน (เลย $Pr_t \approx 1$)
- แต่ไม่เท่ากันทีเดียว — turbulent eddies transport momentum ได้ดีกว่า heat เล็กน้อย
- ค่า 0.85 ให้ผลลัพธ์ที่ตรงกับการทดลองสำหรับ most flows

**Physical reason**: Turbulent eddies have different effectiveness for momentum vs heat transport due to:
- Different length scales involved
- Pressure-velocity correlations in momentum transport
- Absence of pressure-temperature correlations in heat transport
</details>

<details>
<summary><b>3. เมื่อไหร่ควรใช้ Temperature form (T) แทน Enthalpy form (h)?</b></summary>

ใช้ **T-form** เมื่อ:
1. Fluid is essentially incompressible ($\Delta\rho/\rho < 0.05$)
2. Temperature variations are small ($\Delta T < 50$ K)
3. Computational speed is priority
4. Using Boussinesq approximation for buoyancy

ใช้ **h-form** เมื่อ:
1. Fluid is compressible (Ma > 0.3 หรือมี compression/expansion อย่างมีนัยสำคัญ)
2. Natural convection ที่ density changes เป็นสำคัญ
3. ต้องการ physical accuracy สูง
4. Pressure work cannot be neglected

**Decision criterion**: If density variations affect flow physics significantly → use h-form
</details>

<details>
<summary><b>4. ถ้า `energy` keyword คือ `sensibleEnthalpy` แต่ solver ใช้ `buoyantBoussinesqSimpleFoam` จะเกิดอะไรขึ้น?</b></summary>

จะเกิด **inconsistency**:

- `buoyantBoussinesqSimpleFoam` ใช้ **T-form** (solves for T directly)
- แต่ `sensibleEnthalpy` บอก OpenFOAM ว่าควรใช้ **h-form**

**Result**: Solver อาจไม่ทำงาน หรือให้ผิดพลาด เพราะ:
1. Boundary conditions อาจถูกตั้งเป็น `h` แต่ solver ต้องการ `T`
2. `thermo.correct()` จะ convert h → T ซึ่งไม่จำเป็นสำหรับ Boussinesq

**Solution**: สำหรับ `buoyantBoussinesqSimpleFoam`, ใช้:
```cpp
energy          sensibleEnthalpy;   // OK internally
equationOfState rhoConst;           // ← This makes it effectively T-form
```
หรือใช้ `buoyantSimpleFoam` ถ้าต้องการ true h-form
</details>

<details>
<summary><b>5. ความสัมพันธ์ระหว่าง Pr, Re, Pe และ Nu คืออะไร?</b></summary>

**Prandtl (Pr)**: อัตราส่วนระหว่าง momentum diffusion และ thermal diffusion (property of fluid)

**Reynolds (Re)**: อัตราส่วนระหว่าง inertial forces และ viscous forces (flow condition)

**Peclet (Pe)**: ผลคูณของ Re และ Pr — อัตราส่วนระหว่าง convection และ diffusion
$$Pe = Re \times Pr = \frac{uL}{\nu} \times \frac{\nu}{\alpha} = \frac{uL}{\alpha}$$

**Nusselt (Nu)**: อัตราส่วนระหว่าง convective heat transfer และ conductive heat transfer
- Nu = 1: Pure conduction (no convection)
- Nu > 1: Convection enhances heat transfer

**Stanton (St)**: อัตราส่วนระหว่าง actual heat transfer และ maximum possible
$$St = \frac{Nu}{Re \cdot Pr} = \frac{Nu}{Pe}$$
</details>

<details>
<summary><b>6. ทำไมต้องมีการใช้ alphaEff แทน alpha ใน turbulent flow?</b></summary>

ใน turbulent flow การถ่ายเทความร้อนเกิดจาก 2 กลไก:

1. **Molecular diffusion** ($\alpha = \frac{k}{\rho c_p}$): การนำความร้อนระดับโมเลกุล — ค่าคงที่
2. **Turbulent eddies** ($\alpha_t = \frac{\nu_t}{Pr_t}$): การผสมผสานโดย turbulent eddies — ค่าตาม position

**alphaEff** รวมทั้ง 2 กลไก:
$$\alpha_{eff} = \alpha + \alpha_t$$

ใน laminar flow: $\alpha_{eff} \approx \alpha$ (เพราะ $\nu_t \approx 0$)

ใน turbulent flow: $\alpha_{eff} \gg \alpha$ (เพราะ $\nu_t \gg \nu$)

**OpenFOAM implementation**:
```cpp
// Laminar
volScalarField alpha = turbulence->alpha();

// Turbulent (use this!)
volScalarField alphaEff = turbulence->alphaEff();
```
</details>

---

## Related Documents

- **ภาพรวม Heat Transfer**: [00_Overview.md](00_Overview.md)
- **กลไกการถ่ายเทความร้อน**: [02_Heat_Transfer_Mechanisms.md](02_Heat_Transfer_Mechanisms.md)
- **Buoyancy-Driven Flows** (รายละเอียด Boussinesq): [03_Buoyancy_Driven_Flows.md](03_Buoyancy_Driven_Flows.md)
- **Conjugate Heat Transfer**: [04_Conjugate_Heat_Transfer.md](04_Conjugate_Heat_Transfer.md)
- **Turbulence Modeling**: [../../03_TURBULENCE_MODELING/00_Overview.md](../../03_TURBULENCE_MODELING/00_Overview.md)