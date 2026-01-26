# Heat Transfer Mechanisms

Conduction, Convection, Radiation in OpenFOAM

---

## Learning Objectives

After completing this section, you will be able to:

- **WHAT (Concepts):** Identify and describe the three fundamental heat transfer mechanisms (conduction, convection, radiation) and their governing equations
- **WHY (Physical Importance):** Analyze which mechanism dominates in different physical scenarios and understand the implications for system design
- **HOW (Implementation):** Configure appropriate radiation models, dimensionless numbers, and boundary conditions for each mechanism in OpenFOAM

---

## Overview

OpenFOAM supports all three heat transfer mechanisms through different solver capabilities and boundary condition implementations:

| กลไก | Governing Equation | ไฟล์ตั้งค่า | 何时重要 |
|------|-------------------|------------|---------|
| **Conduction** |1$\mathbf{q} = -k \nabla T1| `fvSchemes` → `laplacianSchemes` | Solids, boundary layers |
| **Convection** |1$q = h(T_s - T_\infty)1| `fvSchemes` → `divSchemes` | Fluid flow, heat exchangers |
| **Radiation** |1$q = \varepsilon \sigma (T^4)1| `constant/radiationProperties` | High temperatures, combustion |

> **📖 Cross-references:**  
> - Fourier's Law and conduction fundamentals → [01_Energy_Equation_Fundamentals.md](01_Energy_Equation_Fundamentals.md)  
> - thermophysicalProperties configuration → [00_Overview.md](00_Overview.md)  
> - Boussinesq approximation details → [03_Buoyancy_Driven_Flows.md](03_Buoyancy_Driven_Flows.md)

---

## 1. Conduction (การนำความร้อน)

### WHAT: Fourier's Law Mechanism

Heat conduction is described by **Fourier's Law**:

$$\mathbf{q} = -k \nabla T$$

**Physical Meaning:**
-1$\mathbf{q}1= heat flux vector [W/m²] — energy flow per unit area
-1$k1= thermal conductivity [W/(m·K)] — material property
-1$\nabla T1= temperature gradient [K/m] — driving force
- Negative sign → heat flows from hot to cold (opposite to gradient)

**Thermal Diffusivity:**
$$\alpha = \frac{k}{\rho c_p} \quad [\text{m}²/\text{s}]$$

Determines how quickly temperature changes propagate through a material.

### WHY: When Conduction Dominates

| Situation | Physical Reason | Example Applications |
|-----------|----------------|---------------------|
| **Solids** | No fluid motion → no convection | Insulation, heat sinks, electronics |
| **Boundary layers** | Velocity → 0 at wall → no advection | All wall-bounded flows |
| **Low Reynolds flows** | Minimal fluid motion | Microfluidics, creeping flows |
| **Stagnant fluids** | Gravity-driven convection suppressed | Enclosed spaces, porous media |

**Rule of Thumb:** Conduction is always present; evaluate if other mechanisms are significant.

### HOW: OpenFOAM Implementation

**Energy Equation with Conduction:**
```cpp
// Standard form in solvers
fvScalarMatrix TEqn
(
    fvm::ddt(T)              // Transient term
  + fvm::div(phi, T)         // Convection (may be zero)
  - fvm::laplacian(DT, T)    // Conduction: DT = k/(rho*cp)
 ==
    fvOptions(T)             // Source terms
);
```

**Thermal Diffusivity Specification:**
```cpp
// constant/transportProperties (incompressible solvers)
DT    [0 2 -1 0 0 0 0] 2.5e-5;  // Thermal diffusivity [m²/s]
```

**Discretization Scheme:**
```cpp
// system/fvSchemes
laplacianSchemes
{
    default          Gauss linear corrected;
    laplacian(DT,T)  Gauss linear corrected;  // Second-order accurate
}
```

**Material Properties Comparison:**

| Material |1$k1[W/(m·K)] |1$\alpha1[m²/s] | Application |
|----------|---------------|-----------------|-------------|
| Copper | 400 |1$1.17 \times 10^{-4}1| Heat exchangers |
| Aluminum | 237 |1$9.7 \times 10^{-5}1| Heat sinks |
| Steel | 50 |1$1.4 \times 10^{-5}1| Structural components |
| Air | 0.026 |1$2.2 \times 10^{-5}1| Insulation (trapped) |
| Water | 0.6 |1$1.4 \times 10^{-7}1| Liquid cooling |

---

## 2. Convection (การพาความร้อน)

### WHAT: Forced vs Natural Convection

**Newton's Law of Cooling (Convective Heat Transfer):**
$$q_w = h_c (T_w - T_\infty)$$

Where:
-1$q_w1= wall heat flux [W/m²]
-1$h_c1= convective heat transfer coefficient [W/(m²·K)]
-1$T_w1= wall temperature [K]
-1$T_\infty1= bulk/fluid temperature [K]

**Dimensionless Numbers:**

> **📖 Prandtl number derivation and significance** → [01_Energy_Equation_Fundamentals.md](01_Energy_Equation_Fundamentals.md#dimensionless-numbers-for-heat-transfer)

| Number | Formula | Physical Meaning | Typical Range |
|--------|---------|------------------|---------------|
| **Reynolds** |1$Re = \frac{\rho U L}{\mu}1| Inertia / Viscous forces |1$10^2 - 10^71|
| **Prandtl** |1$Pr = \frac{\mu c_p}{k}1| Momentum / Thermal diffusivity | 0.7 (air) - 7000 (oils) |
| **Nusselt** |1$Nu = \frac{h L}{k}1| Convective / Conductive heat transfer |1$1 - 1000+1|

**Empirical Correlations for1$Nu$:**

**Dittus-Boelter (Turbulent Flow in Pipes):**
$$Nu = 0.023 \, Re^{0.8} \, Pr^{n}$$
-1$n = 0.41for heating ($T_w > T_\infty$)
-1$n = 0.31for cooling ($T_w < T_\infty$)

**Use Case:** Estimate1$h1when experimental data is unavailable:
$$h = \frac{Nu \cdot k}{L}$$

### WHY: Natural vs Forced Convection

| Aspect | Forced Convection | Natural Convection |
|--------|-------------------|-------------------|
| **Driving Force** | External (pump, fan, blower) | Buoyancy (density differences) |
| **Governing Parameter** | Reynolds number ($Re$) | Rayleigh number ($Ra$) |
| **Velocity Scale** | Imposed ($U$) |1$U \sim \sqrt{g \beta \Delta T L}1|
| **Applications** | Heat exchangers, electronics cooling, HVAC | Radiators, atmospheric flows, cooling fins |
| **OpenFOAM Solvers** | `simpleFoam` + energy, `pimpleFoam` | `buoyantBoussinesqSimpleFoam`, `buoyantSimpleFoam` |

**Natural Convection Physics:**

> **📖 Complete natural convection theory** → [03_Buoyancy_Driven_Flows.md](03_Buoyancy_Driven_Flows.md)

Buoyancy force from thermal expansion:
$$\mathbf{f}_b = (\rho - \rho_\infty) \mathbf{g} \approx \rho \beta (T - T_\infty) \mathbf{g}$$

Rayleigh number determines regime:
$$Ra = \frac{g \beta \Delta T L^3}{\nu \alpha} = \frac{\text{Buoyancy forces}}{\text{Viscous diffusion}}$$

### HOW: Convection Implementation

**Forced Convection (Standard Solvers):**
```cpp
// simpleFoam + energy equation
fvScalarMatrix TEqn
(
    fvm::div(phi, T)              // Advection from flow velocity
  - fvm::laplacian(DT, T)         // Conduction
 ==
    fvOptions(T)
);
```

**Natural Convection (Boussinesq Approximation):**
```cpp
// buoyantBoussinesqSimpleFoam
volScalarField rho(1.0 - beta*(T - TRef));  // Density variation

fvVectorMatrix UEqn
(
    fvm::div(phi, U)
  + turbulence->divDevReff(U)
 ==
    rho*g  // Buoyancy source term (gravity * density variation)
);
```

**Boussinesq Applicability:**
- Valid when1$\Delta T / T_{ref} < 0.11(~10% variation)
- For air:1$\Delta T < 301K at room temperature
- Faster than full compressible solvers

**Natural Convection Regimes (based on1$Ra$):**

|1$Ra1Range | Regime | Characteristics | Solver Recommendation |
|------------|--------|-----------------|----------------------|
|1$< 10^31| Conduction-dominated | Negligible fluid motion | `laplacianFoam` (solid approximation) |
|1$10^3 - 10^91| Laminar natural convection | Steady, buoyancy-driven | `buoyantBoussinesqSimpleFoam` |
|1$> 10^91| Turbulent natural convection | Unsteady, chaotic | `buoyantPimpleFoam` |

---

## 3. Radiation (การแผ่รังสี)

### WHAT: Stefan-Boltzmann Law

Thermal radiation is electromagnetic energy emission due to temperature:

$$q_{rad} = \varepsilon \sigma (T_{hot}^4 - T_{cold}^4)$$

**Parameters:**
-1$\sigma = 5.67 \times 10^{-8}1W/(m²·K⁴) — Stefan-Boltzmann constant
-1$\varepsilon1= emissivity (0 to 1) — surface property
-1$T^41dependence — **strong** temperature sensitivity

**Key Insight:** Radiation increases dramatically with temperature:
- Doubling1$T1→ 16× increase in1$q_{rad}$
-1$T = 3001K → negligible
-1$T = 15001K → dominant mechanism

### WHY: When Radiation Matters

| Application | Why Radiation Dominates | Temperature Range | Emissivity Examples |
|-------------|------------------------|-------------------|-------------------|
| **Combustion chambers** | Flames > 1500 K, soot participates |1$> 10001K | 0.8-0.9 (soot) |
| **Furnaces, boilers** | Large1$\Delta T$, participating gases | 800 - 2000 K | 0.4-0.9 |
| **Solar heating** | Direct radiation source | 300 - 400 K (with source) | 0.9 (black absorber) |
| **Electronics cooling** | Usually negligible |1$< 4001K | 0.1-0.9 (materials) |
| **Spacecraft** | Vacuum → no convection | 200 - 400 K | 0.1-0.8 (surfaces) |

**Rule of Thumb:**
- Radiation significant when1$T > 6001K OR1$\Delta T > 2001K
- In vacuum/space, radiation is the **only** heat transfer mechanism
- With participating media (smoke, soot, CO₂, H₂O), radiation can dominate even at lower1$T$

### HOW: Radiation Models in OpenFOAM

#### P1 Model (Optically Thick Media)

**Best for:** Combustion, fires, enclosed spaces with participating media

**Configuration:**
```cpp
// constant/radiationProperties
radiationModel  P1;

P1Coeffs
{
    absorptivity    absorptivity [0 -1 0 0 0 0 0] 0.1;  // Absorption coefficient [1/m]
    // Optional: scatterCoeff for scattering media
}
```

**Governing Equation:**
$$\nabla \cdot \left( \frac{1}{3\kappa} \nabla G \right) = \kappa (4\sigma T^4 - G)$$

Where:
-1$G1= incident radiation [W/m²] — radiative energy flux
-1$\kappa1= absorption coefficient [1/m]
- P1 approximates radiation as a diffusion process

**Advantages:**
- Fast computation (diffusion-like equation)
- Handles participating media well
- Simple implementation

**Limitations:**
- **NOT** suitable for transparent media (air, vacuum)
- **NOT** accurate for surface-to-surface radiation
- Assumes optically thick media ($\kappa L \gg 1$)

**Applications:**
- Combustion chambers (soot, CO₂, H₂O radiation)
- Fires with smoke
- Industrial furnaces with participating gases

#### View Factor Model (Surface-to-Surface)

**Best for:** Vacuum, transparent media, well-defined enclosures

**Configuration:**
```cpp
// constant/radiationProperties
radiationModel  viewFactor;

viewFactorCoeffs
{
    nBands          1;                     // Single wavelength band
    emissivity      constant 0.8;          // Surface emissivity
    // Optional: viewFactorFile for pre-computed view factors
}
```

**Physical Model:**
- Computes geometric view factors between all surface pairs
- Solves radiative exchange integral:1$q_{i} = \sum_j F_{ij} \sigma \varepsilon (T_i^4 - T_j^4)$
-1$F_{ij}1= view factor from surface1$i1to1$j$

**Advantages:**
- Accurate for surface-to-surface radiation
- Handles transparent media perfectly
- Exact geometric treatment

**Limitations:**
- **Computationally expensive:**1$O(N^2)1where1$N1= number of faces
- Long setup time (view factor calculation)
- Not suitable for participating media

**Applications:**
- Satellite thermal analysis (space → vacuum)
- Electronic enclosures (air is transparent)
- Radiators with opaque surfaces
- Building thermal analysis

#### Model Selection Guide

```
Is your fluid transparent (air, vacuum)?
├─ YES → viewFactor model
└─ NO (smoke, soot, participating gases)
   └─ P1 model
```

---

## 4. Thermal Boundary Conditions (Advanced)

### WHAT: Specialized BCs for Each Mechanism

> **📖 Basic BC fundamentals** → [00_Overview.md](00_Overview.md#boundary-conditions)

| Mechanism | BC Type | OpenFOAM BC Name | Key Parameters |
|-----------|---------|------------------|----------------|
| **Conduction** | Fixed temperature | `fixedValue` | `value uniform 300` |
| **Conduction** | Fixed heat flux | `fixedGradient` | `gradient uniform 1000` |
| **Conduction** | Adiabatic (insulated) | `zeroGradient` | (none) |
| **Convection** | Newton's cooling | `externalWallHeatFluxTemperature` | `h`, `Ta` |
| **Radiation** | Surface radiation | `greyDiffusiveRadiation` | `emissivity`, `Ta` |
| **Coupled** | Conjugate heat transfer | `compressible::turbulentTemperatureCoupledBaffleMixed` | (region coupling) |

### WHY: Robin Boundary Condition (Convection)

**Convective BC (Robin Type):**
$$-k \frac{\partial T}{\partial n} = h (T_w - T_\infty)$$

**Physical Interpretation:**
- **Left side:** Conductive flux into wall (Fourier's Law)
- **Right side:** Convective flux away from wall (Newton's Law)
- **Balance:** Energy continuity at interface

**Advantages of `externalWallHeatFluxTemperature`:**
- **No external mesh needed** — avoids meshing ambient fluid
- **Reduced computational cost** — smaller domain
- **Empirical flexibility** — use measured1$h1or correlations
- **Multilayer support** — can model composite walls

### HOW: BC Implementation Examples

#### Basic External Convection

```cpp
// 0/T — Forced convection to ambient
boundaryField
{
    outerWalls
    {
        type        externalWallHeatFluxTemperature;
        mode        coefficient;             // Use h coefficient mode
        
        // Convection parameters
        h           uniform 10;              // [W/(m²·K)] — heat transfer coefficient
        Ta          uniform 293;             // [K] — ambient temperature
    }
}
```

#### Multi-Layer Composite Wall

**Physical scenario:** Brick wall + insulation layer

```cpp
// 0/T — Conduction through multiple layers
externalWall
{
    type            externalWallHeatFluxTemperature;
    mode            coefficient;

    h               uniform 25;              // External convection
    Ta              uniform 300;             // Ambient temperature

    // Layer 1: Brick (5 cm thick)
    thicknessLayers (0.05);                  // [m] — layer thickness
    kappaLayers     (0.7);                   // [W/(m·K)] — thermal conductivity

    // Layer 2: Insulation (2 cm thick)
    thicknessLayers (0.05 0.02);             // Add to list
    kappaLayers     (0.7 0.04);              // Brick + insulation
}
```

**Equivalent thermal resistance:**
$$R_{total} = \frac{L_1}{k_1} + \frac{L_2}{k_2} + \frac{1}{h}$$

#### Combined Convection + Radiation

**Physical scenario:** Hot surface with both cooling mechanisms

```cpp
// 0/T — Coupled heat transfer
heatedSurface
{
    type            externalWallHeatFluxTemperature;
    mode            coefficient;

    // Convection parameters
    h               uniform 15;              // [W/(m²·K)]
    Ta              uniform 293;             // [K]

    // Radiation parameters
    emissivity      0.85;                    // Surface emissivity [0-1]
    
    radiation
    {
        type            greyDiffusiveRadiation;
        T               T;                    // Temperature field name
        // Optional: specify ambient radiation temperature
    }
}
```

**Total heat flux:**
$$q_{total} = q_{conv} + q_{rad} = h(T_w - T_\infty) + \varepsilon \sigma (T_w^4 - T_{amb}^4)$$

#### Radiative Equilibrium (No Convection)

```cpp
// 0/T — Surface radiation only
hotSurface
{
    type            externalWallHeatFluxTemperature;
    mode            coefficient;
    
    h               uniform 0;               // No convection
    Ta              uniform 300;             // Reference (unused)
    
    emissivity      1.0;                     // Blackbody
    radiation
    {
        type            greyDiffusiveRadiation;
        T               T;
    }
}
```

**Use Case:** Space applications (vacuum → no convection)

---

## 5. Solver Selection Guide

### WHAT: Heat Transfer Solvers in OpenFOAM

| Solver | Mechanisms | Type | Key Use Cases |
|--------|------------|------|---------------|
| `laplacianFoam` | Conduction only | Transient | Solids, heat diffusion, transient thermal analysis |
| `buoyantSimpleFoam` | Conduction + Convection (large ΔT) | Steady-state | Natural convection, compressible, large ΔT |
| `buoyantBoussinesqSimpleFoam` | Conduction + Convection (small ΔT) | Steady-state | Natural convection, incompressible, small ΔT |
| `buoyantPimpleFoam` | Conduction + Convection + Transient | Transient | Unsteady buoyancy-driven flows |
| `chtMultiRegionFoam` | All + CHT | Transient/Steady | Conjugate heat transfer (solid-fluid coupling) |
| `rhoPimpleFoam` + energy | All (optional radiation) | Transient | General compressible flow with heat transfer |

### WHY: Solver Decision Flowchart

```
Start: Identify Your Physics
│
├─ Is solid only (no fluid domain)?
│   └─ YES → laplacianFoam
│
├─ Fluid flow present?
│   ├─ Is buoyancy significant (Ra > 10³)?
│   │   ├─ NO → Use standard solver (simpleFoam + energy equation)
│   │   └─ YES → Continue
│   │
│   ├─ Is temperature variation small (ΔT < 30 K for air)?
│   │   ├─ YES → buoyantBoussinesqSimpleFoam (faster, simpler)
│   │   └─ NO → Continue
│   │
│   ├─ Is transient required?
│   │   ├─ YES → buoyantPimpleFoam
│   │   └─ NO → buoyantSimpleFoam
│   │
│   └─ Is solid-fluid coupling required (CHT)?
│       └─ YES → chtMultiRegionFoam
│
└─ Temperature > 600 K or large ΔT?
    └─ Add radiation model
        ├─ Participating media (smoke, soot) → P1
        └─ Transparent media (air, vacuum) → viewFactor
```

### HOW: Solver Configuration Comparison

> **📖 thermophysicalProperties details** → [00_Overview.md](00_Overview.md#thermophysical-properties)

| Solver | Energy Form | Equation of State | Compressible | Typical ΔT | Speed |
|--------|-------------|-------------------|--------------|------------|-------|
| `buoyantBoussinesqSimpleFoam` | T (sensible enthalpy) | `rhoConst` | No (incompressible) | < 30 K | ⭐⭐⭐ Fastest |
| `buoyantSimpleFoam` | h (enthalpy) | `perfectGas` | Yes | > 30 K | ⭐⭐ Medium |
| `buoyantPimpleFoam` | h (enthalpy) | `perfectGas` | Yes | > 30 K | ⭐ Slowest (transient) |
| `chtMultiRegionFoam` | Varies | Varies | Yes (fluid) / No (solid) | Any | ⭐ Complex |

**Key Configuration Differences:**

**Boussinesq Solver (Small ΔT):**
```cpp
// constant/thermophysicalProperties
transport    Newtonian;
rho          rho [1 -3 0 0 0] 1.2;           // Constant density
CP           CP [0 2 -2 -1 -1] 1007;        // Specific heat
beta         beta [0 0 0 -1] 0.0034;        // Thermal expansion coeff [1/K]
```

**Compressible Solver (Large ΔT):**
```cpp
// constant/thermophysicalProperties
thermoType
{
    type            heRhoThermo;
    mixture         pureMixture;
    transport       sutherland;
    thermo          janaf;
    equationOfState perfectGas;
    specie          specie;
    energy          sensibleEnthalpy;
}
```

---

## Key Takeaways

### 1. Mechanism Selection Summary

| Mechanism | Governing Law | Key Parameter | Dominant When | OpenFOAM Implementation |
|-----------|---------------|---------------|---------------|------------------------|
| **Conduction** |1$\mathbf{q} = -k \nabla T1|1$k1[W/(m·K)] | Solids, low velocity | `laplacian(DT,T)` in all solvers |
| **Forced Convection** |1$q = h(T_s - T_\infty)1|1$h1[W/(m²·K)] | High1$Re$, external flow | `div(phi,T)` + external convection BC |
| **Natural Convection** |1$\mathbf{f}_b = \rho \beta \Delta T \mathbf{g}1|1$Ra1| Buoyancy-driven,1$Ra > 10^31| `buoyantBoussinesqSimpleFoam` |
| **Radiation** |1$q = \varepsilon \sigma T^41|1$\varepsilon$,1$T^41|1$T > 6001K, participating media | `radiationModel` (P1 or viewFactor) |

### 2. Critical Dimensionless Numbers

| Number | Formula | Physical Meaning | Use For |
|--------|---------|------------------|---------|
| **Prandtl ($Pr$)** |1$\frac{\mu c_p}{k}1| Ratio of momentum to thermal diffusivity | Fluid property, velocity/thermal BL thickness ratio |
| **Nusselt ($Nu$)** |1$\frac{h L}{k}1| Ratio of convective to conductive transfer | Calculating1$h1from correlations |
| **Rayleigh ($Ra$)** |1$\frac{g \beta \Delta T L^3}{\nu \alpha}1| Ratio of buoyancy to viscous forces | Natural convection regime selection |

### 3. Implementation Checklist

- [ ] **Identify dominant mechanism(s):** Conduction always present; evaluate1$Re$,1$Ra$,1$T1for convection/radiation
- [ ] **Select solver:** Use flowchart in Section 5
- [ ] **Configure thermophysicalProperties:** Match EoS to physics (Boussinesq vs compressible)
- [ ] **Set boundary conditions:** Use `externalWallHeatFluxTemperature` for convection
- [ ] **Add radiation model (if needed):** P1 (participating) vs viewFactor (surface-to-surface)
- [ ] **Validate with correlations:** Compare1$Nu1with empirical correlations (Dittus-Boelter)

### 4. Common Mistakes to Avoid

| Mistake | Consequence | Solution |
|---------|-------------|----------|
| Using Boussinesq for large ΔT | Large errors in density → incorrect buoyancy | Switch to `buoyantSimpleFoam` for ΔT > 30 K |
| Forgetting radiation at high T | Underpredicted heat transfer (can be >50% error) | Add `radiationModel` when1$T > 6001K |
| Wrong1$h1value | Inaccurate BC → wrong temperature field | Calculate1$h1from1$Nu1correlations using Dittus-Boelter |
| Using P1 for transparent media | Overpredicted radiation | Use `viewFactor` for vacuum/air |
| Neglecting multilayer walls | Incorrect thermal resistance | Use `thicknessLayers`, `kappaLayers` |

### 5. Quick Reference: BC Examples

```cpp
// Fixed temperature (Dirichlet)
type            fixedValue;
value           uniform 300;

// Fixed heat flux (Neumann)
type            fixedGradient;
gradient        uniform 1000;  // [W/m²] / k

// Adiabatic (insulated)
type            zeroGradient;  // No parameters

// External convection
type            externalWallHeatFluxTemperature;
mode            coefficient;
h               uniform 10;
Ta              uniform 293;

// Convection + radiation + multilayer
type            externalWallHeatFluxTemperature;
mode            coefficient;
h               uniform 25;
Ta              uniform 300;
emissivity      0.85;
thicknessLayers (0.05 0.02);
kappaLayers     (0.7 0.04);
```

---

## Concept Check

<details>
<summary><b>1. เมื่อไหร่ควรใช้ Boussinesq approximation และทำไม?</b></summary>

**ใช้เมื่อ:**1$\Delta T / T_{ref} < 0.11(≈10%) หรือ1$\Delta T < 301K สำหรับอากาศ

**ทำไม:** 
- เร็วกว่า full compressible solver (density คงที่ → solve น้อยกว่า)
- เสถียรกว่า (nonlinearities น้อยกว่า)
- Valid สำหรับ natural convection ส่วนใหญ่ในงานวิศวกรรม

**Solver:** `buoyantBoussinesqSimpleFoam`
</details>

<details>
<summary><b>2. อธิบายความแตกต่างระหว่าง P1 และ viewFactor radiation models</b></summary>

**P1 Model:**
- สำหรับ participating media (ควัน, soot, ก๊าซที่ดูดกลืน)
- เร็ว (solve diffusion-like equation)
- ใช้ได้ไม่ดีกับ transparent media

**viewFactor Model:**
- สำหรับ surface-to-surface radiation ใน transparent media (vacuum, air)
- ช้า (compute view factors ระหว่างทุก patch)
- Accurate สำหรับ geometries ที่ซับซ้อน

**เลือกอย่างไร:** มี smoke/soot/participating gases? → P1; มี transparent fluid → viewFactor
</details>

<details>
<summary><b>3. externalWallHeatFluxTemperature BC ต้องระบุ parameters อะไรบ้าง?</b></summary>

**Required (สำหรับ convection):**
- `mode coefficient` — ระบุว่าใช้โหมด h coefficient
- `h` — heat transfer coefficient [W/(m²·K)]
- `Ta` — ambient temperature [K]

**Optional:**
- `thicknessLayers` — list ของความหนาแต่ละ layer [m]
- `kappaLayers` — list ของ conductivity แต่ละ layer [W/(m·K)]
- `emissivity` — สำหรับ radiation coupling [0-1]

**ตัวอย่างการคำนวณ total resistance:**
$$R_{total} = \sum \frac{L_i}{k_i} + \frac{1}{h}$$
</details>

<details>
<summary><b>4. ทำไม radiation มีความสำคัญมากใน high-temperature applications?</b></summary>

**เพราะ:**1$q_{rad} \propto T^41— อยู่ในรูป power 4

**Impact:**
- T เพิ่ม 2 เท่า → q เพิ่ม **16 เท่า**
- T = 300 K → radiation ≈ 5% ของ total heat transfer
- T = 1500 K → radiation ≈ **80-90%** ของ total

**ตัวอย่าง:**
Combustion chamber (T ≈ 2000 K):
- Conduction: ~10%
- Convection: ~20%
- Radiation: ~70% ← **dominant**

**ดังนั้น:** ถ้าไม่ model radiation ใน high-T applications → errors อาจเกิน 50%
</details>

<details>
<summary><b>5. อธิบาย Dittus-Boelter correlation และการใช้งาน</b></summary>

**สมการ:**
$$Nu = 0.023 \, Re^{0.8} \, Pr^{n}$$

**ใช้สำหรับ:**
- Turbulent forced convection ใน pipes ($Re > 4000$)
- ประมาณค่า Nusselt number เมื่อไม่มี experimental data

**ขั้นตอนใช้:**
1. Calculate1$Re = \rho U D / \mu$
2. Find1$Pr1from fluid properties table
3. Compute1$Nu1using Dittus-Boelter
4. Calculate1$h = Nu \cdot k / D$
5. Use1$h1ใน `externalWallHeatFluxTemperature` BC

**ตัวอย่าง:**
- Air flowing in pipe:1$Re = 10^5$,1$Pr = 0.7$, heating ($n=0.4$)
-1$Nu = 0.023 \times (10^5)^{0.8} \times (0.7)^{0.4} = 230$
- If1$D = 0.051m,1$k = 0.0261W/(m·K):
  -1$h = 230 \times 0.026 / 0.05 = 1201W/(m²·K)
</details>

<details>
<summary><b>6. Different physical situations where different mechanisms dominate</b></summary>

**Conduction-dominant:**
- Heat sink fins (solid aluminum)
- Insulation materials (foam, fiberglass)
- Microelectronic chips (very small length scales)

**Forced convection-dominant:**
- Car radiator (air flow over fins)
- Electronics cooling with fan
- Heat exchanger tubes (fluid flow inside)

**Natural convection-dominant:**
- Room heating (radiator, no fan)
- Atmospheric boundary layer
- Cooling fins without forced flow

**Radiation-dominant:**
- Furnace interiors (T > 1000 K)
- Combustion chambers (flames radiate)
- Spacecraft (vacuum → no convection)

**Multiple mechanisms (need all):**
- Boiler (combustion radiation + convection to water)
- Solar water heater (solar radiation + natural convection)
- Building envelope (conduction through walls + convection + solar radiation)
</details>

---

## Related Documents

- **บทก่อนหน้า:** [01_Energy_Equation_Fundamentals.md](01_Energy_Equation_Fundamentals.md) — Fourier's Law, Prandtl number details, energy equation derivation
- **ภาพรวม:** [00_Overview.md](00_Overview.md) — thermophysicalProperties configuration, basic BCs
- **บทถัดไป:** [03_Buoyancy_Driven_Flows.md](03_Buoyancy_Driven_Flows.md) — Natural convection deep dive, Boussinesq approximation
- **CHT:** [04_Conjugate_Heat_Transfer.md](04_Conjugate_Heat_Transfer.md) — Solid-fluid coupling, multi-region simulations