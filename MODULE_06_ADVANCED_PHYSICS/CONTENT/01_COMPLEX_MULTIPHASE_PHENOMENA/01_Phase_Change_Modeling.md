# Phase Change Modeling (การจำลองการเปลี่ยนสถานะ)

> **Phase change** = Mass transfer between phases driven by thermodynamic non-equilibrium

---

## Learning Objectives (เป้าหมายการเรียนรู้)

After completing this section, you will be able to:

1. **WHAT:** Distinguish between different phase change mechanisms (temperature-driven vs. pressure-driven) and their mathematical formulations
2. **WHY:** Select appropriate phase change models based on physical driving forces, engineering requirements, and available data
3. **HOW:** Implement phase change models in OpenFOAM with proper boundary conditions, solver selection, and parameter calibration

---

## Prerequisites (ความรู้พื้นฐานที่ต้องมี)

Before studying this section, ensure you understand:

- **VOF Method:** Volume of Fluid transport equation (α-equation) from MODULE_04
- **Multiphase Solvers:** Basic familiarity with `interFoam` family and phase fraction notation
- **Thermodynamics:** Understanding of saturation conditions ($T_{sat}$, $p_{sat}$) and phase diagrams
- **OpenFOAM Syntax:** Dictionary file structure, boundary condition specification
- **Turbulence Modeling:** RAS/LES basics for multiphase flows

**Recommended pre-reading:**
- MODULE_04: Multiphase Flow Fundamentals (VOF method)
- MODULE_03: Pressure-Velocity Coupling (PIMPLE algorithm)

---

## 1. WHAT: Phase Change Fundamentals

### 1.1 Definition and Driving Forces

**Phase change** = Conversion between liquid, vapor, and solid states due to thermodynamic imbalance

**Physical principle:** Mass transfer occurs to restore thermodynamic equilibrium. When local conditions deviate from saturation, mass crosses phase boundaries until equilibrium is restored.

**Two fundamental mechanisms:**

| Mechanism | Driving Force | Mathematical Condition | Typical Applications |
|-----------|---------------|------------------------|---------------------|
| **Temperature-Driven** | $T \neq T_{sat}$ (thermal non-equilibrium) | $T > T_{sat}$ → boiling<br>$T < T_{sat}$ → condensation | Boiling, condensation, evaporation, solidification |
| **Pressure-Driven** | $p < p_{sat}$ (pressure drop below saturation) | $p < p_{sat}$ → cavitation | Cavitation in pumps, valves, propellers |

**Key distinction:**
- **Temperature-driven:** Latent heat transport dominates (requires energy equation)
- **Pressure-driven:** Mechanical effects dominate (momentum equation sufficient)

### 1.2 Classification by Phase Transition Type

| Type | Thai | Process | Direction | Driving Force | Energy Required? |
|------|------|---------|-----------|---------------|------------------|
| **Boiling** | การเดือด | Liquid → Vapor | Evaporation | $T > T_{sat}$ | Yes (latent heat) |
| **Condensation** | การควบแน่น | Vapor → Liquid | Condensation | $T < T_{sat}$ | Yes (release heat) |
| **Cavitation** | การเกิดโพรง | Liquid → Vapor | Evaporation | $p < p_{sat}$ | No (adiabatic) |
| **Solidification** | การแข็งตัว | Liquid → Solid | Freezing | $T < T_{melt}$ | Yes (fusion heat) |
| **Evaporation** | การระเหย | Liquid → Vapor (surface) | Mass transfer | Concentration gradient | Yes |

### 1.3 Mathematical Framework: VOF with Phase Change

**Standard VOF equation (no phase change):**
```cpp
∂α/∂t + ∇·(Uα) = 0
```

**Modified VOF with phase change source term:**
```cpp
∂α/∂t + ∇·(Uα) = Γ_evap - Γ_cond

where:
α  = Volume fraction of dispersed phase [-]
Γ_evap = Mass transfer rate: liquid → vapor [kg/(m³·s)]
Γ_cond = Mass transfer rate: vapor → liquid [kg/(m³·s)]
```

**Key insight:** Source terms create/destroy phase volume to account for mass transfer while maintaining overall mass conservation.

**Energy equation coupling (for temperature-driven phase change):**
```cpp
∂(ρh)/∂t + ∇·(ρUh) = ∇·(k∇T) + Γ_evap·h_lv - Γ_cond·h_lv

where:
h  = Specific enthalpy [J/kg]
h_lv = Latent heat of vaporization [J/kg]
```

---

## 2. WHY: Model Selection and Engineering Significance

### 2.1 When Phase Change Modeling Matters

**Critical applications where phase change cannot be ignored:**

1. **Cavitation in hydraulic equipment**
   - **WHY it matters:** Bubble formation → performance loss, vibration, material erosion
   - **Engineering impact:** Pump efficiency drops 20-40% under cavitating conditions; valve erosion can cause catastrophic failure
   - **Design consequence:** Must predict cavitation inception and extent to avoid damage

2. **Boiling heat transfer**
   - **WHY it matters:** Latent heat transport enables high heat flux (up to 1 MW/m²)
   - **Engineering impact:** Enables compact cooling systems for electronics, nuclear reactors, power plants
   - **Design consequence:** Critical heat flux (CHF) prediction prevents burnout accidents

3. **Condensation in heat exchangers**
   - **WHY it matters:** Phase change releases latent heat, significantly enhancing heat transfer
   - **Engineering impact:** Condenser design affects power plant efficiency by 5-10%
   - **Design consequence:** Film thickness prediction determines heat transfer coefficient

4. **Solidification in casting**
   - **WHY it matters:** Phase front position determines microstructure and mechanical properties
   - **Engineering impact:** Cooling rate controls grain size, defect formation
   - **Design consequence:** Must predict solidification time and shrinkage

**Consequences of ignoring phase change:**
- ❌ Incorrect pressure distribution (cavitation zones not captured)
- ❌ Wrong heat transfer rates (latent heat neglected → underestimation by 10-100×)
- ❌ Mass imbalance (no source terms in continuity equation)
- ❌ Failed equipment (unexpected cavitation erosion, overheating)

### 2.2 Model Selection Decision Matrix

#### Quick Reference: Solver Selection by Application

| Scenario | Primary Driver | Recommended Model | OpenFOAM Solver | Complexity |
|----------|---------------|-------------------|-----------------|------------|
| **Pump cavitation** | Pressure drop | Schnerr-Sauer / Kunz | `interPhaseChangeFoam` | Low-Medium |
| **Pool boiling** | Temperature excess | Lee / Thermal phase change | `interCondensatingEvaporatingFoam` | Medium |
| **Flash evaporation** | Combined p & T | Hertz-Knudsen | `multiphaseEulerFoam` | High |
| **Condensation on walls** | Temperature deficit | Thermal phase change | `interCondensatingEvaporatingFoam` | Medium |
| **Solidification** | Temperature drop | Enthalpy-porosity | Custom solver | High |

#### Detailed Model Comparison: Lee vs. Hertz-Knudsen vs. thermalPhaseChange

| Criterion | Lee Model | Hertz-Knudsen Model | thermalPhaseChange (Schnerr-Sauer) |
|-----------|-----------|-------------------|-----------------------------------|
| **Driving Force** | Temperature difference ($T - T_{sat}$) | Pressure & temperature ($p$, $T$) | Pressure difference ($p_{sat} - p$) |
| **Physical Basis** | Empirical rate proportionality | Molecular kinetic theory | Bubble dynamics (Rayleigh-Plesset) |
| **Primary Application** | Boiling, condensation | Flash evaporation, high-accuracy research | Cavitation in hydraulic systems |
| **Complexity** | Low | High | Medium |
| **Computational Cost** | Low (fastest) | High (slowest) | Medium |
| **Calibration Required** | Yes (relaxation coefficient $r$) | Yes (accommodation coefficient $\sigma$) | Yes (bubble density $n$, nucleation size) |
| **Robustness** | Medium (sensitive to $r$) | Low (prone to divergence) | High (most robust) |
| **Physical Fidelity** | Low-Medium | High | Medium |
| **Data Availability** | Easy (standard thermal properties) | Requires accurate molecular properties | Requires bubble nuclei distribution |
| **OpenFOAM Implementation** | `thermalPhaseChange` with Lee formulation | Custom or via `multiphaseEulerFoam` | `SchnerrSauer` in `interPhaseChangeFoam` |
| **Validation Status** | Widely used for engineering | Research-grade, limited validation | Extensively validated (pumps, injectors) |
| **Typical $r$/$\sigma$/$n$ values** | $r = 0.1-1000$ s⁻¹ | $\sigma = 0.01-1.0$ | $n = 10^{11}-10^{15}$ m⁻³ |

#### Decision Criteria Flowchart

```
START: What is your phase change mechanism?
│
├─ Pressure-driven (cavitation)?
│  ├─ YES → Use Schnerr-Sauer
│  │  WHY: Robust, validated for industrial applications
│  │  WHEN: Pumps, valves, propellers, injectors
│  │  DATA NEEDED: Bubble number density (nBubbles)
│  │
│  └─ NO → Continue
│
├─ Temperature-driven (boiling/condensation)?
│  ├─ YES → Need high accuracy?
│  │  ├─ YES + Good thermodynamic data → Hertz-Knudsen
│  │  │  WHY: Most physically rigorous, molecular-scale accuracy
│  │  │  WHEN: Research, validation cases, flash evaporation
│  │  │  WARNING: Computationally expensive, less robust
│  │  │  DATA NEEDED: Accommodation coefficient (σ), molecular weight
│  │  │
│  │  └─ NO + Engineering application → Lee / thermalPhaseChange
│  │  WHY: Simple, fast, sufficient accuracy
│  │  WHEN: Heat exchangers, cooling systems, boilers
│  │  DATA NEEDED: Latent heat (hLv), saturation temperature (Tsat)
│  │  CALIBRATION: Relaxation coefficient r (start with 100 s⁻¹)
│  │
│  └─ Combined pressure & temperature effects?
│     → Hertz-Knudsen (captures both)
│     WHY: Molecular formulation includes p and T dependence
│
END: Select solver and implement
```

#### When to Use Each Model: Decision Criteria

**Use Schnerr-Sauer (pressure-driven) when:**
- ✅ Primary mechanism is pressure drop below saturation
- ✅ Working with hydraulic equipment (pumps, valves, turbines)
- ✅ Need robust, industrially-validated solution
- ✅ Computational efficiency is important
- ✅ Have approximate bubble nuclei data
- ❌ Don't use when thermal effects are significant
- ❌ Don't use for boiling/condensation (temperature-driven)

**Use Lee model (temperature-driven) when:**
- ✅ Primary mechanism is temperature difference from $T_{sat}$
- ✅ Simulating boiling or condensation
- ✅ Need fast, practical engineering solution
- ✅ Willing to calibrate relaxation coefficient
- ✅ Working with heat exchangers, cooling systems, boilers
- ❌ Don't use for pure cavitation (pressure-driven)
- ❌ Don't use if high physical accuracy is critical (use Hertz-Knudsen instead)

**Use Hertz-Knudsen when:**
- ✅ Need highest physical accuracy (research-grade)
- ✅ Both pressure and temperature effects are important
- ✅ Have accurate thermophysical properties (molecular weight, accommodation coefficient)
- ✅ Simulating flash evaporation or rapid phase change
- ✅ Computational resources are available (HPC cluster)
- ❌ Don't use for routine engineering (too expensive, less robust)
- ❌ Don't use if molecular properties are uncertain

**Key Decision Questions:**

1. **What is the primary driving force?**
   - Pressure → Schnerr-Sauer
   - Temperature → Lee or Hertz-Knudsen

2. **What is the application?**
   - Industrial design → Schnerr-Sauer or Lee (robust)
   - Research/validation → Hertz-Knudsen (accurate)

3. **What data is available?**
   - Bubble nuclei distribution → Schnerr-Sauer
   - Thermal properties → Lee
   - Molecular properties ($\sigma$, $M$) → Hertz-Knudsen

4. **What are computational constraints?**
   - Limited resources → Lee (fastest)
   - Adequate resources → Schnerr-Sauer (balanced)
   - High-performance computing available → Hertz-Knudsen (most accurate)

---

## 3. HOW: Mathematical Foundation and Implementation

### 3.1 Mass Transfer in VOF Framework

**Governing equations for phase change flows:**

**Continuity equation with phase change:**
```cpp
∇·U = Γ_evap/ρ_v - Γ_cond/ρ_l
```

**Volume fraction transport:**
```cpp
∂α_v/∂t + ∇·(Uα_v) = (Γ_evap - Γ_cond)/ρ_v
```

**Momentum equation (variable density):**
```cpp
∂(ρU)/∂t + ∇·(ρUU) = -∇p + ∇·(μ∇U) + ρg + F_σ
```

**Energy equation (for temperature-driven phase change):**
```cpp
∂(ρh)/∂t + ∇·(ρUh) = ∇·(k∇T) + (Γ_evap - Γ_cond)·h_lv
```

**Key challenge:** Strong coupling between phase change rate (Γ), pressure (p), and temperature (T) requires iterative solution (PIMPLE algorithm)

### 3.2 Mass Transfer Models

#### 3.2.1 Lee Model (Temperature-Driven)

**Physical basis:** Rate proportional to thermal non-equilibrium

**Mathematical formulation:**

$$\Gamma = r \cdot \alpha_{donor} \cdot \rho_{donor} \cdot \frac{|T - T_{sat}|}{T_{sat}} \cdot \text{sign}(T - T_{sat})$$

**Evaporation (liquid → vapor, $T > T_{sat}$):**
$$\Gamma_{evap} = r \cdot \alpha_l \cdot \rho_l \cdot \frac{T - T_{sat}}{T_{sat}}$$

**Condensation (vapor → liquid, $T < T_{sat}$):**
$$\Gamma_{cond} = r \cdot \alpha_v \cdot \rho_v \cdot \frac{T_{sat} - T}{T_{sat}}$$

**Parameters:**
- $r$ = Relaxation coefficient [1/s] (typically 0.1-1000, **must be calibrated**)
- $\alpha_{donor}$ = Volume fraction of donor phase
- $\rho_{donor}$ = Density of donor phase [kg/m³]
- $T$ = Local temperature [K]
- $T_{sat}$ = Saturation temperature [K]

**WHY use Lee model:**
- ✅ Simple formulation, easy to implement
- ✅ Computationally efficient (fastest option)
- ✅ Good for engineering boiling/condensation applications
- ✅ Requires only standard thermal properties
- ❌ Requires calibration of $r$ (not physically based)
- ❌ Less accurate near critical point
- ❌ Cannot capture pressure-driven effects (cavitation)

**Implementation in OpenFOAM:**

**File: `constant/phaseProperties`**
```cpp
phases (water vapor);

water
{
    transportModel  Newtonian;
    nu              1e-06;      // Kinematic viscosity [m²/s]
    rho             1000;       // Density [kg/m³]
    Cp              4181;       // Specific heat [J/(kg·K)]
}

vapor
{
    transportModel  Newtonian;
    nu              4.273e-04;  // Vapor viscosity [m²/s]
    rho             0.554;      // Vapor density at 373 K [kg/m³]
    Cp              2080;       // Specific heat [J/(kg·K)]
}

// Phase change model selection
phaseChangeModel thermalPhaseChange;

thermalPhaseChangeCoeffs
{
    hLv     2.26e6;      // Latent heat of vaporization [J/kg] @ 1 atm
    Tsat    373.15;      // Saturation temperature [K] @ 1 atm
    r       100;         // Relaxation factor [1/s] - CALIBRATE THIS!
    Tmin    300;         // Lower limit [K] - prevents unphysical values
    Tmax    400;         // Upper limit [K] - prevents unphysical values
}
```

**Calibration procedure for $r$:**
```cpp
// Step 1: Start with r = 100 (typical for water)
// Step 2: Run simulation and compare with experimental data
// Step 3: Adjust based on results:
r = 100;         // Starting point

// If boiling too slow (vapor production underestimated):
r = 200-500;     // Increase r (faster phase change)

// If boiling too fast or unstable:
r = 10-50;       // Decrease r (slower phase change)

// Step 4: Verify results are grid-independent
// Step 5: Document final r value for your application
```

**Example calibration for pool boiling:**
```cpp
// Experimental data: Heat flux = 50 kW/m² at ΔT = 5 K
// Simulation with r = 100: Heat flux = 20 kW/m² (underpredicted)
// Simulation with r = 300: Heat flux = 48 kW/m² (good agreement)
// → Use r = 300 for this application
```

#### 3.2.2 Hertz-Knudsen Model (Molecular Kinetics)

**Physical basis:** Net mass flux from molecular collision theory at phase interface

**Mathematical formulation:**

$$\Gamma = \frac{2\sigma}{2-\sigma} \sqrt{\frac{M}{2\pi R}} \left(\frac{p_{sat}}{\sqrt{T_{sat}}} - \frac{p}{\sqrt{T}}\right)$$

**Parameters:**
- $\sigma$ = Accommodation coefficient (0.01-1.0, **material property**)
- $M$ = Molecular weight [kg/mol] (water: 0.018 kg/mol)
- $R$ = Universal gas constant [J/(mol·K)] = 8.314 J/(mol·K)
- $p_{sat}$ = Saturation pressure at $T_{sat}$ [Pa]
- $p$ = Local pressure [Pa]
- $T_{sat}$ = Saturation temperature [K]
- $T$ = Local temperature [K]

**Physical interpretation:**
- $\frac{2\sigma}{2-\sigma}$ = Fraction of molecules that stick to interface
- $\sqrt{\frac{M}{2\pi R}}$ = Molecular mass scaling factor
- $\frac{p_{sat}}{\sqrt{T_{sat}}}$ = Evaporation flux (molecules leaving liquid)
- $\frac{p}{\sqrt{T}}$ = Condensation flux (molecules entering liquid)

**WHY use Hertz-Knudsen:**
- ✅ Physically rigorous (derived from molecular kinetics)
- ✅ No calibration needed if $\sigma$ is known from experiments
- ✅ Captures both pressure and temperature effects simultaneously
- ✅ Most accurate for flash evaporation and rapid phase change
- ❌ Computationally expensive (requires accurate thermophysical properties)
- ❌ Requires accommodation coefficient data (often unavailable)
- ❌ Less robust (can cause divergence if not carefully implemented)
- ❌ Limited validation data compared to Lee/Schnerr-Sauer

**Implementation considerations:**

**Typical accommodation coefficients:**
```cpp
σ = 0.01-0.1;     // Water (strongly depends on surface contamination)
σ = 0.5-1.0;      // Refrigerants, cryogenic fluids
σ = 0.8-1.0;      // Metals (liquid-solid)
```

**OpenFOAM implementation:** Not available as built-in model. Requires custom implementation or use in `multiphaseEulerFoam` with user-defined source terms.

**Example implementation sketch:**
```cpp
// Custom phase change model (conceptual)
dimensionedScalar R("R", dimGasConstant, 8.314);
dimensionedScalar M("M", dimMass/dimMoles, 0.018);
dimensionedScalar sigma("sigma", dimless, 0.1);  // Accommodation coefficient

volScalarField preFactor = (2.0*sigma)/(2.0 - sigma) * sqrt(M/(2.0*pi*R));

volScalarField evaporationFlux = preFactor * pSat / sqrt(TSat);
volScalarField condensationFlux = preFactor * p / sqrt(T);

volScalarField Gamma = preFactor * (evaporationFlux - condensationFlux);
```

#### 3.2.3 Schnerr-Sauer Model (Pressure-Driven Cavitation)

**Physical basis:** Bubble dynamics from Rayleigh-Plesset equation (simplified)

**Mathematical formulation:**

**Bubble radius from void fraction:**
$$R_B = \left(\frac{3\alpha}{4\pi n}\right)^{1/3}$$

**Mass transfer rate:**
$$\Gamma = \frac{\rho_v \rho_l}{\rho} \cdot 3 \cdot \frac{\alpha(1-\alpha)}{R_B} \cdot \text{sign}(p_{sat} - p) \sqrt{\frac{2}{3} \frac{|p_{sat} - p|}{\rho_l}}$$

**Parameters:**
- $R_B$ = Bubble radius [m] (computed from α and n)
- $n$ = Bubble number density [1/m³] (typically $10^{11}-10^{15}$ for water)
- $p_{sat}$ = Saturation pressure [Pa] (temperature-dependent)
- Relationship: $\alpha = \frac{4}{3}\pi R_B^3 n$

**Physical interpretation:**
- Derivation from Rayleigh-Plesset equation for bubble growth/collapse
- $\text{sign}(p_{sat} - p)$ determines evaporation vs. condensation
- Square root term represents bubble wall velocity

**WHY use Schnerr-Sauer:**
- ✅ Derived from first principles (bubble dynamics)
- ✅ Robust for industrial cavitating flows
- ✅ Widely validated (pumps, injectors, marine propellers)
- ✅ Computationally efficient (no coupling to energy equation)
- ✅ Only requires bubble nuclei data (nBubbles)
- ❌ Limited to vapor-liquid (no thermal effects)
- ❌ Requires estimation of $n$ and initial $R_B$
- ❌ Cannot capture temperature-driven phase change

**Implementation in OpenFOAM:**

**File: `constant/phaseProperties`**
```cpp
phases (water vapor);

water
{
    transportModel  Newtonian;
    nu              1e-06;      // Kinematic viscosity [m²/s]
    rho             1000;       // Density [kg/m³]
}

vapor
{
    transportModel  Newtonian;
    nu              4.273e-04;  // Vapor viscosity [m²/s]
    rho             0.023;      // Vapor density (at operating conditions)
}

// Phase change model selection
phaseChangeModel SchnerrSauer;

SchnerrSauerCoeffs
{
    nBubbles     1e13;      // Bubble number density [1/m³] - CALIBRATE THIS!
    pSat         2300;      // Saturation pressure [Pa] @ 20°C
    dNucleation  1e-06;     // Initial bubble diameter [m] (1 micron)
}
```

**Parameter significance and calibration:**

**1. Bubble number density (nBubbles):**
```cpp
// Water typical values
nBubbles = 1e13;  // Clean water (high nuclei count)
nBubbles = 1e11;  // Degassed water (low nuclei count)

// Effect: Higher n → faster cavitation onset, more vapor production
// Calibration: Compare cavitation inception number with experiments
```

**2. Saturation pressure (pSat):**
```cpp
// pSat is temperature-dependent! Use Antoine equation for accuracy:
// log10(pSat) = A - B/(C + T)  (pSat in bar, T in °C)
// For water: A = 5.40221, B = 1838.675, C = 240.0 (range 1-100°C)

// Example calculation at 20°C:
pSat = 10^(5.40221 - 1838.675/(240.0 + 20)) * 1e5;  // Result: 2337 Pa

// For constant temperature simulation, use fixed pSat
pSat = 2300;  // Pa @ 20°C

// For variable temperature, implement temperature-dependent pSat
// (requires custom code or table lookup)
```

**3. Nucleation diameter (dNucleation):**
```cpp
// Affects initial bubble size distribution
dNucleation = 1e-06;  // 1 micron (typical for water)

// Smaller dNucleation → faster bubble growth rate
// Calibration: Use microscopic measurements or literature values
```

**Temperature-dependent pSat implementation (optional):**
```cpp
// Custom function for temperature-dependent pSat
// File: $FOAM_USER_DIR/OpenFOAM-*/boundaryConditions/pSat_T.C

dimensionedScalar A("A", dimless, 5.40221);
dimensionedScalar B("B", dimTemperature, 1838.675);
dimensionedScalar C("C", dimTemperature, 240.0);

volScalarField TC = T - 273.15;  // Convert K to °C
volScalarField pSat = pow(10, A.value() - B.value()/(C.value() + TC)) * 1e5;
```

---

### 3.3 Comparison Summary: Mass Transfer Models

| Aspect | Lee Model | Hertz-Knudsen | Schnerr-Sauer |
|--------|-----------|---------------|---------------|
| **Driving Force** | $T - T_{sat}$ | $(p_{sat}/\sqrt{T_{sat}}) - (p/\sqrt{T})$ | $p_{sat} - p$ |
| **Primary Use** | Boiling, condensation | Flash evaporation, research | Cavitation |
| **Complexity** | Low | High | Medium |
| **Speed** | Fast | Slow | Medium |
| **Calibration** | $r$ (relaxation) | $\sigma$ (accommodation) | $n$ (bubble density) |
| **Robustness** | Medium | Low | High |
| **Accuracy** | Low-Medium | High | Medium |
| **Validation** | Good | Limited | Extensive |

---

## 4. OpenFOAM Implementation Guide

### 4.1 Solver Selection Matrix

```bash
# Cavitation (pressure-driven, VOF)
interPhaseChangeFoam

# Boiling/Condensation (temperature-driven, VOF)
interCondensatingEvaporatingFoam

# Multiphase with phase change (Euler-Euler)
reactingTwoPhaseEulerFoam
multiphaseEulerFoam

# Compressible multiphase with phase change
reactingMultiphaseEulerFoam
```

**Detailed solver comparison:**

| Solver | Formulation | Phase Change Model | Turbulence | Typical Use Case | Thermal? |
|--------|------------|-------------------|------------|------------------|----------|
| `interPhaseChangeFoam` | VOF | Schnerr-Sauer, Kunz, Merkle | RAS/LES | Cavitation in pumps, valves | No |
| `interCondensatingEvaporatingFoam` | VOF | Lee (thermalPhaseChange) | RAS/LES | Boiling, condensation | Yes |
| `reactingTwoPhaseEulerFoam` | Euler-Euler | User-defined source terms | RAS | Reacting flows, phase change | Yes |
| `multiphaseEulerFoam` | Euler-Euler | Multiple mechanisms | RAS | Polydisperse flows | Yes |
| `cavitatingFoam` (legacy) | VOF | Schnerr-Sauer, Kunz | RAS/LES | Cavitation (older version) | No |

**Solver selection decision tree:**
```
Is your flow pressure-driven cavitation?
├─ Yes → interPhaseChangeFoam
└─ No (temperature-driven)
    ├─ Using VOF method? → interCondensatingEvaporatingFoam
    └─ Using Euler-Euler? → reactingTwoPhaseEulerFoam
```

### 4.2 Complete Cavitation Setup Example

**Scenario:** Cavitation in a venturi tube (pressure-driven)

**Directory structure:**
```
cavitationCase/
├── 0/
│   ├── p               # Pressure field
│   ├── U               # Velocity field
│   ├── alpha.water     # Volume fraction (water)
│   ├── alpha.vapor     # Volume fraction (vapor) - optional
│   └── T               # Temperature (optional for isothermal)
├── constant/
│   ├── phaseProperties  # Phase change model definition
│   ├── transportProperties
│   ├── thermophysicalProperties (if thermal)
│   └── turbulenceProperties
└── system/
    ├── fvSchemes       # Discretization schemes
    ├── fvSolution      # Linear solvers, algorithm settings
    └── controlDict     # Time control, output
```

**Step-by-step setup:**

**Step 1: Define phases in `constant/phaseProperties`**
```cpp
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v2312                                 |
|   \\  /    A nd           | Website:  www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      phaseProperties;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

phases (water vapor);

// Water phase properties
water
{
    transportModel  Newtonian;
    nu              1e-06;      // Kinematic viscosity [m²/s] @ 20°C
    rho             1000;       // Density [kg/m³]
    Cp              4181;       // Specific heat [J/(kg·K)] (optional for thermal)
}

// Vapor phase properties
vapor
{
    transportModel  Newtonian;
    nu              4.273e-04;  // Vapor kinematic viscosity [m²/s]
    rho             0.023;      // Vapor density [kg/m³] @ 20°C
    Cp              2080;       // Specific heat [J/(kg·K)] (optional for thermal)
}

// Phase change model selection
phaseChangeModel SchnerrSauer;

SchnerrSauerCoeffs
{
    // Bubble number density [1/m³]
    // Higher values → faster cavitation onset
    // Typical range: 1e11 (degassed) to 1e15 (highly nucleated)
    nBubbles     1e13;

    // Saturation pressure [Pa] @ 20°C
    // Use Antoine equation for temperature-dependent pSat
    pSat         2300;

    // Initial bubble diameter [m]
    // Typical: 1 micron for water
    dNucleation  1e-06;

    // Optional: Temperature dependence (requires custom implementation)
    // pSat  table ((300 3536) (350 41700) (373 101325) (400 245000));
}

// Optional: Alternative phase change models (uncomment to use)
// phaseChangeModel Kunz;
// KunzCoeffs
// {
//     UInf           10;       // Characteristic velocity [m/s]
//     tInf           0.01;     // Characteristic time [s]
//     pSat           2300;     // Saturation pressure [Pa]
//     Cc             1000;     // Condensation coefficient
//     Cv             100;      // Evaporation coefficient
// }

// ************************************************************************* //
```

**Step 2: Initial conditions for water volume fraction (`0/alpha.water`)**
```cpp
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      alpha.water;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 0 0 0 0 0 0];

internalField   uniform 1;  // Start with pure liquid (α_water = 1)

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 1;  // Liquid inlet
    }

    outlet
    {
        type            zeroGradient;  // Allow α to evolve
    }

    walls
    {
        type            zeroGradient;  // No phase flux at walls
    }
}

// ************************************************************************* //
```

**Step 3: Pressure boundary conditions (`0/p`)**
```cpp
dimensions      [1 -1 -2 0 0 0 0];

internalField   uniform 1e5;  // 1 bar initial pressure

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 2e5;  // High pressure inlet (2 bar)
    }

    outlet
    {
        type            fixedValue;
        value           uniform 5e3;  // Low pressure outlet (5 kPa) → triggers cavitation
        // Cavitation occurs when p_local < pSat (2300 Pa)
    }

    walls
    {
        type            zeroGradient;
    }
}
```

**Step 4: Solution control (`system/fvSolution`)**
```cpp
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      fvSolution;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

solvers
{
    p
    {
        solver          GAMG;
        tolerance       1e-7;
        relTol          0.01;
        smoother        GaussSeidel;
    }

    pFinal
    {
        solver          GAMG;
        tolerance       1e-7;
        relTol          0;
    }

    U
    {
        solver          smoothSolver;
        smoother        GaussSeidel;
        tolerance       1e-6;
        relTol          0.1;
    }

    UFinal
    {
        $U;
        relTol          0;
    }

    alpha.water
    {
        solver          smoothSolver;
        smoother        GaussSeidel;
        tolerance       1e-8;
        relTol          0;  // Tight tolerance for sharp interface
    }
}

PIMPLE
{
    // Pressure-velocity coupling parameters
    nCorrectors     3;        // Increase for stability with rapid phase change
    nNonOrthogonalCorrectors 1;

    // Volume fraction transport
    nAlphaCorr      2;        // VOF iterations per time step
    nAlphaSubCycles 2;        // Sub-cycle for sharp interface

    // Phase change stability
    maxCo           0.3;      // Reduce for rapid phase change (default: 1.0)
    rDeltaTSmoothingCoeff 0.1;  // Smoothing for adjustable time step
    alphaCoMax      1;        // Max Courant for α equation
}

// Optional: Relaxation factors for stability
relaxationFactors
{
    fields
    {
        p               0.3;
        rho             0.05;  // Important for variable density
    }

    equations
    {
        U               0.7;
        UFinal          1;
    }
}

// ************************************************************************* //
```

**Step 5: Discretization schemes (`system/fvSchemes`)**
```cpp
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      fvSchemes;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

ddtSchemes
{
    default         Euler;  // First-order transient
    // Use backward for second-order accuracy (more stable)
    // default      backward;
}

gradSchemes
{
    default         Gauss linear;
}

divSchemes
{
    default         none;

    // Convection schemes
    div(phi,U)      Gauss linearUpwind grad(U);  // Bounded second-order
    div(phi,alpha)  Gauss vanLeer;  // Interface compression
    div(phiv,p)     Gauss linearUpwind grad(p);  // Pressure convection

    // Diffusion schemes
    div((nuEff*dev2(T(grad(U))))) Gauss linear;
}

laplacianSchemes
{
    default         Gauss linear corrected;
}

interpolationSchemes
{
    default         linear;
}

snGradSchemes
{
    default         corrected;
}

// ************************************************************************* //
```

**Step 6: Time control (`system/controlDict`)**
```cpp
application     interPhaseChangeFoam;

startFrom       startTime;

startTime       0;

stopAt          endTime;

endTime         0.1;  // [s] - Adjust based on flow time scale

deltaT          1e-5;  // [s] - Start with small timestep

// Adjustable time stepping for stability
adjustTimeStep  yes;

maxCo           0.3;  // Match PIMPLE maxCo
maxAlphaCo      1.0;   // Max Courant for α equation

// Time step limits
maxDeltaT       1e-3;  // [s] - Maximum timestep
minDeltaT       1e-7;  // [s] - Minimum timestep (for rapid phase change)

// Output control
writeControl    timeStep;

writeInterval   100;  // Write every 100 timesteps

writeFormat     ascii;

writePrecision  6;

// Function objects for monitoring
functions
{
    // Monitor vapor volume
    vaporVolume
    {
        type            volRegion;
        functionObject  volFieldValue;
        enabled         true;
        writeFields     false;
        region          type;
        name            internalField;

        operation       volAverage;

        fields
        (
            alpha.vapor  // Average vapor volume fraction
        );
    }

    // Monitor mass transfer rate
    massTransferRate
    {
        type            coded;
        enabled         true;
        
        codeWrite
        #{
            // Access phase change model
            const volScalarField& alphaWater = mesh().lookupObject<volScalarField>("alpha.water");
            const volScalarField& alphaVapor = mesh().lookupObject<volScalarField>("alpha.vapor");
            
            // Calculate total vapor volume
            scalar vaporVolume = fvc::domainIntegrate(alphaVapor).value();
            
            Info << "Vapor volume: " << vaporVolume << " m³" << endl;
        #};
    }
}
```

**Step 7: Run the simulation**
```bash
# Mesh generation (example with blockMesh)
blockMesh

# Initialize fields
cp -r 0_orig 0

# Run solver
interPhaseChangeFoam

# Monitor progress in real-time
tail -f log.interPhaseChangeFoam

# Post-process with ParaView
paraFoam
```

### 4.3 Boiling/Condensation Setup Example

**Scenario:** Pool boiling on heated surface (temperature-driven)

**Key differences from cavitation setup:**

**1. Use `interCondensatingEvaporatingFoam` solver**
```bash
solver interCondensatingEvaporatingFoam;
```

**2. Temperature boundary conditions (`0/T`)**
```cpp
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      T;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 0 0 1 0 0 0];  // Temperature [K]

internalField   uniform 373.15;  // Initial at saturation temperature

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 373.15;  // Saturated liquid inlet
    }

    heatedBottom
    {
        type            fixedValue;
        value           uniform 383.15;  // 10 K above Tsat → boiling
        // Heat flux: q'' = h(T_wall - T_sat)
    }

    condensingWall
    {
        type            fixedValue;
        value           uniform 363.15;  // 10 K below Tsat → condensation
    }

    topAtmosphere
    {
        type            pressureInletOutletTemperature;
        inletValue      uniform 373.15;
        value           $inletValue;
    }

    walls
    {
        type            zeroGradient;  // Adiabatic walls
    }
}

// ************************************************************************* //
```

**3. Thermophysical properties (`constant/thermophysicalProperties`)**
```cpp
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "constant";
    object      thermophysicalProperties;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

thermoType
{
    type            heRhoThermo;
    mixture         multiComponentMixture;
    transport       sutherland;
    thermo          janaf;
    energy          sensibleEnthalpy;
    equationOfState perfectGas;
    specie          specie;
    // Alternative for incompressible liquids:
    // type            heRhoThermo;
    // mixture         multiComponentMixture;
    // transport       const;
    // thermo          hConst;
    // energy          sensibleEnthalpy;
    // equationOfState rhoConst;
    // specie          specie;
}

mixture
{
    specie
    {
        nMoles          1;
        molWeight       18.015;  // Water [g/mol]
    }

    thermodynamics
    {
        Cp              4181;    // [J/(kg·K)] - Specific heat
        Hf              0;       // [J/kg] - Formation enthalpy
    }

    transport
    {
        mu              1e-3;    // [Pa·s] - Dynamic viscosity
        Pr              7.0;     // Prandtl number
        k               0.6;     // [W/(m·K)] - Thermal conductivity
    }
}

// ************************************************************************* //
```

**4. Phase change model with Lee formulation (`constant/phaseProperties`)**
```cpp
phases (water vapor);

water
{
    transportModel  Newtonian;
    nu              1e-06;
    rho             1000;
    Cp              4181;
    k               0.6;      // Thermal conductivity [W/(m·K)]
}

vapor
{
    transportModel  Newtonian;
    nu              4.273e-04;
    rho             0.554;    // At 373 K
    Cp              2080;
    k               0.025;    // Thermal conductivity [W/(m·K)]
}

// Lee model for temperature-driven phase change
phaseChangeModel thermalPhaseChange;

thermalPhaseChangeCoeffs
{
    // Thermodynamic properties
    hLv     2.257e6;    // Latent heat of vaporization [J/kg] @ 1 atm
    Tsat    373.15;     // Saturation temperature [K] @ 1 atm (100°C)

    // Mass transfer coefficient (MUST BE CALIBRATED)
    r       100;        // Relaxation factor [1/s]
    // r = 10-50: Slow phase change (stable, underpredicted)
    // r = 100-300: Moderate phase change (typical for water)
    // r = 500-1000: Fast phase change (may be unstable)

    // Numerical stability limits
    Tmin    300;        // Minimum temperature [K] (prevents unphysical values)
    Tmax    450;        // Maximum temperature [K] (prevents unphysical values)

    // Optional: Temperature-dependent properties
    // hLv table ((300 2.43e6) (350 2.32e6) (373.15 2.257e6) (400 2.15e6));
}
```

**5. Energy equation settings (`system/fvSchemes`)**
```cpp
divSchemes
{
    default         none;

    // Energy equation
    div(phi,h)      Gauss linearUpwind grad(h);  // Enthalpy convection
    div(phi,K)      Gauss linear;  // Kinetic energy

    // Standard schemes
    div(phi,U)      Gauss linearUpwind grad(U);
    div(phi,alpha)  Gauss vanLeer;
    div((nuEff*dev2(T(grad(U))))) Gauss linear;
}
```

**6. Solution stability for boiling (`system/fvSolution`)**
```cpp
PIMPLE
{
    // More conservative settings for boiling
    nCorrectors     4;        // Increase for energy coupling
    nNonOrthogonalCorrectors 2;

    nAlphaCorr      2;
    nAlphaSubCycles 3;        // More sub-cycles for rapid phase change

    // Stricter time step control
    maxCo           0.2;      // Reduce from 0.3 for boiling
    rDeltaTSmoothingCoeff 0.05;

    // Under-relaxation for energy coupling
    nOuterCorr      2;        // Outer iterations for T-U coupling
}

solvers
{
    h  // Enthalpy
    {
        solver          GAMG;
        tolerance       1e-7;
        relTol          0.01;
        smoother        GaussSeidel;
    }

    T  // Temperature (if used instead of h)
    {
        solver          GAMG;
        tolerance       1e-6;
        relTol          0.01;
    }
}
```

**7. Run boiling simulation**
```bash
# Initialize temperature field
setFields

# Run solver
interCondensatingEvaporatingFoam

# Monitor phase change rate
foamMonitorT postProcessing/vaporVolume/0/volAverage(alpha.vapor)

# Post-process
paraFoam
```

### 4.4 Advanced: Implementing Temperature-Dependent Saturation Pressure

**Challenge:** pSat varies significantly with temperature (Antoine equation)

**Solution 1: Table lookup (simplest)**
```cpp
// constant/phaseProperties
SchnerrSauerCoeffs
{
    nBubbles     1e13;
    
    // Temperature-dependent saturation pressure
    pSat  table 
    (
        (273.15  611)      // 0°C: 611 Pa
        (293.15  2337)     // 20°C: 2.3 kPa
        (313.15  7376)     // 40°C: 7.4 kPa
        (333.15  19914)    // 60°C: 19.9 kPa
        (353.15  47367)    // 80°C: 47.4 kPa
        (373.15  101325)   // 100°C: 1 atm
        (393.15  198500)   // 120°C: 198.5 kPa
    );
    
    dNucleation  1e-06;
}
```

**Solution 2: Custom function object (more accurate)**
```cpp
// Custom function to compute pSat from Antoine equation
// Save as: constant/phaseProperties

functions
{
    pSatFromAntoine
    {
        type            coded;
        enabled         true;
        
        codeWrite
        #{
            // Antoine equation constants for water
            const dimensionedScalar A("A", dimless, 5.40221);
            const dimensionedScalar B("B", dimTemperature, 1838.675);
            const dimensionedScalar C("C", dimTemperature, 240.0);
            
            // Get temperature field (convert K to °C)
            const volScalarField& T = mesh().lookupObject<volScalarField>("T");
            volScalarField TC = T - 273.15;
            
            // Compute pSat using Antoine equation (result in bar, convert to Pa)
            volScalarField pSat = pow(10, A.value() - B.value()/(C.value() + TC)) * 1e5;
            
            // Store as field for visualization
            pSat.write();
        #};
    }
}
```

---

## 5. Troubleshooting and Best Practices

### 5.1 Common Issues and Solutions

| Problem | Root Cause | Solution | Verification |
|---------|------------|----------|--------------|
| **Simulation divergence** | Timestep too large for rapid phase change | Reduce `maxCo` to 0.2-0.3; use adjustable time stepping | Check Courant number: `postProcess -func CourantNo` |
| **Unphysical temperature spikes** | Wrong BC or Cp values; energy imbalance | Verify boundary conditions match thermophysical properties | Monitor energy balance: `postProcess -func "mag(rho*h)"` |
| **Pressure oscillations** | Large density variations during phase change | Increase `nCorrectors` to 3-5; use `nAlphaSubCycles` | Plot pressure history; check for high-frequency oscillations |
| **Mass imbalance** | Γ_evap ≠ Γ_cond (asymmetric transfer) | Check model formulation; ensure conservation | Compute global mass: `postProcess -func "volIntegrate(rho)"` |
| **Interface smearing** | Insufficient VOF resolution | Refine mesh near interface; use `interfaceCompression` | Visualize α field; check interface thickness |
| **Cavitation not appearing** | Pressure never drops below p_sat | Verify outlet pressure is sufficiently low | Plot p field; ensure p_min < p_sat |
| **Boiling too slow** | Relaxation coefficient r too small | Increase r by factor of 2-5 | Compare vapor volume vs. experimental data |
| **Boiling too fast/unstable** | Relaxation coefficient r too large | Decrease r by factor of 2-5 | Monitor simulation stability (divergence check) |
| **Phase change in wrong direction** | Sign error in source term | Verify BC driving force has correct sign | Check $T_{wall} - T_{sat}$ or $p - p_{sat}$ |
| **Memory explosion** | Excessive output from function objects | Reduce write frequency; disable verbose output | Monitor memory usage with `top` or `htop` |

### 5.2 Parameter Calibration Guidelines

#### Lee Model Relaxation Coefficient ($r$)

**Physical meaning:** Characteristic frequency of phase change [1/s]

**Calibration procedure:**
```cpp
// Step 1: Initial guess based on application
r = 100;  // [1/s] - Starting point for water

// Step 2: Run simulation with experimental data
// Compare: vapor volume, heat flux, bubble detachment frequency

// Step 3: Adjust based on results
if (boilingRate < experimental) {
    r *= 2;  // Increase by factor of 2
} else if (boilingRate > experimental) {
    r /= 2;  // Decrease by factor of 2
}

// Step 4: Iterate until agreement (typical range: 10-1000 s⁻¹)

// Step 5: Validate with different conditions (verify r is robust)
```

**Typical values by application:**
```cpp
// Pool boiling (nucleate boiling regime)
r = 50-200 s⁻¹;

// Film boiling (rapid vaporization)
r = 500-1000 s⁻¹;

// Condensation (slower phase change)
r = 10-50 s⁻¹;

// Flash evaporation (very rapid)
r = 1000+ s⁻¹;
```

**Calibration checklist:**
- [ ] Compare vapor volume fraction vs. time
- [ ] Compare heat flux: $q'' = -k \nabla T$
- [ ] Compare bubble detachment frequency (if available)
- [ ] Verify results are grid-independent
- [ ] Document final r value for reproducibility

#### Schnerr-Sauer Bubble Density ($n_{Bubbles}$)

**Physical meaning:** Number of bubble nuclei per unit volume [1/m³]

**Calibration procedure:**
```cpp
// Step 1: Estimate based on water quality
nBubbles = 1e13;  // [1/m³] - Clean water with nucleation sites

// Step 2: Compare cavitation inception number
// σ_inception = (p_inlet - p_vapor) / (0.5 * ρ * U²)

// Step 3: Adjust based on cavitation extent
if (cavitationExtent < experimental) {
    nBubbles *= 10;  // Increase nuclei count (faster cavitation)
} else if (cavitationExtent > experimental) {
    nBubbles /= 10;  // Decrease nuclei count
}

// Step 4: Iterate (typical range: 1e11 - 1e15 m⁻³)
```

**Typical values by water quality:**
```cpp
// Degassed water (few nuclei)
nBubbles = 1e11 m⁻³;

// Tap water (moderate nuclei)
nBubbles = 1e13 m⁻³;

// Highly aerated water (many nuclei)
nBubbles = 1e15 m⁻³;
```

**Experimental measurement techniques:**
- Acoustic cavitation detection
- Laser scattering
- High-speed imaging of bubble nuclei

#### Hertz-Knudsen Accommodation Coefficient ($\sigma$)

**Physical meaning:** Fraction of molecules that "stick" to phase interface

**Typical values:**
```cpp
// Water (depends strongly on surface contamination)
σ = 0.01-0.1;  // Pure water on contaminated surface
σ = 0.5-1.0;   // Clean water-vapor interface

// Refrigerants
σ = 0.5-1.0;

// Cryogenic fluids (liquid nitrogen, oxygen)
σ = 0.8-1.0;
```

**Literature sources:**
- Labuntsov & Yagov (2007) - "Mechanics of Liquid-Gas Systems"
- Carelli (2020) - "Accommodation Coefficients for Phase Change"

### 5.3 Verification and Validation Checklist

**Before trusting results, verify:**

- [ ] **Mass conservation:** Global mass balance error < 0.1%
  ```bash
  postProcess -func "volIntegrate(rho)" > mass_balance.log
  # Check: ΔM/M_initial < 0.001
  ```

- [ ] **Energy balance:** (for boiling) Check energy source/sink terms
  ```bash
  postProcess -func "volIntegrate(rho*h)" > energy_balance.log
  # Verify: Energy_in - Energy_out = Latent_heat * Mass_transfer
  ```

- [ ] **Saturation condition:** Phase change only occurs near $T_{sat}$ or $p_{sat}$
  ```bash
  # Visualize phase change regions
  paraFoam -colormap "T - Tsat" 
  # Phase change should be localized where T ≈ Tsat
  ```

- [ ] **Mesh independence:** Refine mesh by factor of 2, check if results change < 2%
  ```bash
  # Run with coarse mesh
  interPhaseChangeFoam > log_coarse
  
  # Run with refined mesh (refinementCells in blockMeshDict)
  interPhaseChangeFoam > log_fine
  
  # Compare vapor volume fraction
  grep "Vapor volume:" log_coarse log_fine
  ```

- [ ] **Time step independence:** Halve $\Delta t$, verify solution unchanged < 1%
  ```bash
  # Run with dt = 1e-5
  interPhaseChangeFoam
  
  # Run with dt = 5e-6
  interPhaseChangeFoam
  
  # Compare results at same physical time
  ```

- [ ] **Experimental validation:** Compare with benchmark cases
  ```cpp
  // Benchmark: Cavitation in venturi (Stutz & Reboud 1997)
  // Measure: Vapor volume fraction, pressure distribution
  
  // Benchmark: Pool boiling (Kandlikar 1990)
  // Measure: Heat flux vs. wall superheat (boiling curve)
  ```

**Validation criteria:**
- Vapor volume fraction: ±10% error (acceptable)
- Heat flux: ±15% error (acceptable)
- Cavitation inception number: ±5% error (good)

### 5.4 Best Practices for Stable Simulations

**1. Time step control:**
```cpp
// Use adjustable time stepping
adjustTimeStep  yes;
maxCo           0.3;  // Stricter than default (1.0)
maxAlphaCo      1.0;

// Set reasonable limits
maxDeltaT       1e-3;
minDeltaT       1e-7;
```

**2. Under-relaxation:**
```cpp
relaxationFactors
{
    fields
    {
        p               0.3;  // Aggressive pressure relaxation
        rho             0.05; // Very conservative for density
    }

    equations
    {
        U               0.7;  // Moderate momentum relaxation
        h               0.7;  // Moderate enthalpy relaxation
    }
}
```

**3. Solver tolerances:**
```cpp
solvers
{
    p
    {
        solver          GAMG;
        tolerance       1e-7;  // Tight tolerance
        relTol          0.01;
    }

    alpha.water
    {
        solver          smoothSolver;
        tolerance       1e-8;  // Very tight for sharp interface
        relTol          0;     // No relative tolerance
    }
}
```

**4. Mesh quality:**
```cpp
// Refine near expected phase change regions
refinementBoxes
{
    venturiThroat
    {
        mode            inside;
        cellSize        0.1e-3;  // 0.1 mm cells
    }
}

// Ensure non-orthogonality < 70°
checkMesh -allGeometry -allTopology
```

**5. Boundary condition consistency:**
```cpp
// Ensure T_wall - T_sat has correct sign
// For boiling: T_wall > T_sat (evaporation at wall)
heatedWall
{
    type            fixedValue;
    value           uniform 383.15;  // > Tsat (373.15)
}

// For condensation: T_wall < T_sat (condensation at wall)
coldWall
{
    type            fixedValue;
    value           uniform 363.15;  // < Tsat (373.15)
}
```

**6. Monitoring and debugging:**
```cpp
// Add function objects for critical quantities
functions
{
    // Monitor Courant number
    CourantNo
    {
        type            CourantNo;
        functionObjectLibs ("libfieldFunctionObjects.so");
        writeFields     true;
    }

    // Monitor vapor production rate
    vaporProductionRate
    {
        type            coded;
        codeWrite
        #{
            const volScalarField& alphaVapor = mesh().lookupObject<volScalarField>("alpha.vapor");
            scalar vaporVol = fvc::domainIntegrate(alphaVapor).value();
            scalar dVaporDt = 0;
            
            if (timeIndex() > 0) {
                static scalar vaporVolOld = vaporVol;
                dVaporDt = (vaporVol - vaporVolOld) / deltaTime().value();
                vaporVolOld = vaporVol;
            }
            
            Info << "Vapor production rate: " << dVaporDt << " m³/s" << endl;
        #};
    }
}
```

---

## 6. Practice Exercises

### Exercise 1: Cavitation in a Venturi Tube

**Objective:** Capture cavitation cloud formation in venturi throat

**Setup:**
- **Geometry:** 2D axisymmetric venturi (inlet diameter: 20mm, throat diameter: 10mm, length: 100mm)
- **Fluid:** Water at 20°C
- **Inlet conditions:** Velocity = 10 m/s, pressure = 1 bar
- **Outlet conditions:** Pressure = 5 kPa (below p_sat = 2.3 kPa)

**Tasks:**
1. **Mesh generation:** Create blockMeshDict with refinement in throat region
   - Target cell size: 0.5mm in throat, 2mm elsewhere
   - Verify mesh quality with `checkMesh`

2. **Solver setup:** Configure `interPhaseChangeFoam` with Schnerr-Sauer model
   - Set `nBubbles = 1e13`, `pSat = 2300` Pa
   - Use adjustable time stepping with `maxCo = 0.3`

3. **Simulation:** Run until $t = 0.1$ s (steady-state cavitation)

4. **Post-processing:**
   - Plot vapor volume fraction along centerline
   - Calculate cavitation number: $\sigma = \frac{p_{inlet} - p_{vapor}}{0.5 \rho U^2}$
   - Compare with experimental data (Stutz & Reboud 1997)

5. **Parametric study:** Vary outlet pressure (2 kPa, 5 kPa, 10 kPa)
   - Plot cavitation extent vs. outlet pressure
   - Identify cavitation inception pressure

**Expected outcome:** Cavitation appears when outlet pressure < 20 kPa

**Deliverables:**
- Vapor volume fraction contour plot (ParaView)
- Pressure distribution along centerline
- Cavitation number vs. outlet pressure curve

---

### Exercise 2: Pool Boiling Simulation

**Objective:** Simulate nucleate boiling on heated surface

**Setup:**
- **Geometry:** 2D rectangular domain (width: 10mm, height: 20mm)
- **Fluid:** Water at 1 atm
- **Boundary conditions:**
  - Bottom wall: $T = 383$ K (10 K above $T_{sat}$)
  - Top surface: $p = 101325$ Pa (atmospheric)
  - Initial temperature: 373.15 K (saturated)

**Tasks:**
1. **Mesh generation:** Create structured mesh with refinement near bottom wall
   - Cell size: 0.1mm near wall, 0.5mm elsewhere

2. **Solver setup:** Implement Lee model with `thermalPhaseChange`
   - Start with $r = 100$ s⁻¹
   - Set `hLv = 2.257e6` J/kg, `Tsat = 373.15` K

3. **Calibration:** Adjust relaxation coefficient $r$
   - Compare bubble detachment frequency with experimental data
   - Target heat flux: ~50 kW/m² at $\Delta T = 10$ K

4. **Analysis:**
   - Calculate heat flux: $q'' = -k \nabla T$ at wall
   - Measure bubble detachment frequency (Hz)
   - Compute Nusselt number: $Nu = \frac{hL}{k}$ where $h = \frac{q''}{\Delta T}$

5. **Validation:** Compare boiling curve with literature (Kandlikar 1990)
   - Plot $q''$ vs. $\Delta T$ for $r = 50, 100, 200$ s⁻¹

**Challenge:** Capture ebullition cycle (nucleation → growth → detachment)

**Deliverables:**
- Temperature field showing boiling onset
- Vapor volume evolution over time
- Boiling curve (heat flux vs. wall superheat)

---

### Exercise 3: Condensation on Cold Vertical Plate

**Objective:** Simulate film condensation and compare with Nusselt theory

**Setup:**
- **Geometry:** Vertical plate (height: 100mm, thickness: 5mm)
- **Fluid:** Saturated steam at 400 K
- **Boundary conditions:**
  - Plate surface: $T = 360$ K (below $T_{sat}$)
  - Vapor inlet: $T = 400$ K, $\alpha_vapor = 1$
  - Outlet: $p = 101325$ Pa

**Tasks:**
1. **Mesh generation:** 2D domain with refinement near plate surface
   - Cell size: 0.05mm near wall (capture thin film)

2. **Solver setup:** Use `interCondensatingEvaporatingFoam`
   - Lee model for condensation ($\Gamma_{cond} > 0$)
   - Set $r = 50$ s⁻¹ (slower than boiling)

3. **Simulation:** Run until steady film thickness achieved

4. **Analysis:**
   - Measure condensate film thickness $\delta$ vs. height $y$
   - Calculate local heat transfer coefficient: $h(y) = \frac{q''(y)}{T_{sat} - T_{wall}}$
   - Compute average Nusselt number: $\overline{Nu} = \frac{\overline{h}L}{k}$

5. **Validation:** Compare with Nusselt film condensation theory
   $$\delta(y) = \left(\frac{4 \mu_l k_l (T_{sat} - T_{wall}) y}{\rho_l g h_{lv}}\right)^{1/4}$$

**Expected result:** Film thickness increases with height (parabolic profile)

**Deliverables:**
- Liquid film thickness profile
- Heat transfer coefficient vs. height
- Comparison with Nusselt theory (error analysis)

---

### Exercise 4: Flash Evaporation in Supersonic Nozzle

**Objective:** Simulate rapid evaporation due to pressure drop

**Setup:**
- **Geometry:** Converging-diverging nozzle (throat diameter: 5mm)
- **Fluid:** Liquid water at 473 K (200°C, high pressure)
- **Process:** Water flashes to vapor as pressure drops below $p_{sat}$

**Tasks:**
1. **Mesh generation:** Axisymmetric nozzle with throat refinement
   - Cell size: 0.1mm in throat region

2. **Solver setup:** Implement Hertz-Knudsen model
   - Accommodation coefficient: $\sigma = 0.1$ (water)
   - Temperature-dependent $p_{sat}$ (Antoine equation)

3. **Simulation:** Capture shock wave and phase change

4. **Analysis:**
   - Plot pressure, temperature, and vapor fraction along nozzle
   - Identify phase change onset location
   - Compare with isentropic expansion (no phase change)

**Challenge:** Strong coupling between pressure drop and phase change

**Deliverables:**
- Vapor fraction contour plot
- Pressure-temperature phase diagram trajectory
- Mass flow rate comparison (with vs. without phase change)

---

## 7. Key Takeaways (สรุปสิ่งสำคัญ)

### WHAT (Definitions and Fundamentals)

- **Phase change** = Mass transfer driven by thermodynamic non-equilibrium
  - Temperature-driven: $T \neq T_{sat}$ (boiling, condensation)
  - Pressure-driven: $p < p_{sat}$ (cavitation)

- **Mass transfer rate ($\Gamma$)** = Source term in VOF equation [kg/(m³·s)]
  - $\Gamma_{evap} > 0$: Liquid → Vapor (vapor volume increases)
  - $\Gamma_{cond} > 0$: Vapor → Liquid (vapor volume decreases)

- **Governing equations:**
  - VOF equation with source term: $\frac{\partial \alpha}{\partial t} + \nabla \cdot (U\alpha) = \frac{\Gamma_{evap} - \Gamma_{cond}}{\rho}$
  - Energy equation (for boiling): $\frac{\partial(\rho h)}{\partial t} + \nabla \cdot (\rho Uh) = \nabla \cdot (k\nabla T) + \Gamma \cdot h_{lv}$

### WHY (Engineering Significance and Decision Criteria)

- **Cavitation:** Causes 20-40% efficiency loss, vibration, erosion in hydraulic machinery
  - **Model choice:** Schnerr-Sauer (robust, validated)

- **Boiling:** Enables high heat flux cooling (up to 1 MW/m²) in power/thermal systems
  - **Model choice:** Lee (fast, engineering accuracy) or Hertz-Knudsen (research-grade)

- **Model selection matters:** Wrong model → incorrect physics, wasted computation, failed designs

**Decision matrix:**
- **Pressure-driven + industrial application** → Schnerr-Sauer
- **Temperature-driven + engineering** → Lee
- **Temperature-driven + research** → Hertz-Knudsen
- **Combined p & T effects** → Hertz-Knudsen

### HOW (Implementation Details)

**Lee model (temperature-driven):**
$$\Gamma = r \cdot \alpha_{donor} \cdot \rho_{donor} \cdot \frac{|T - T_{sat}|}{T_{sat}}$$
- **Parameters:** $r$ (relaxation, must calibrate), $T_{sat}$ (saturation temperature)
- **Use:** Boiling, condensation
- **Solver:** `interCondensatingEvaporatingFoam`
- **Calibration:** $r = 50-1000$ s⁻¹ (start with 100)

**Schnerr-Sauer model (pressure-driven):**
$$\Gamma = \frac{\rho_v \rho_l}{\rho} \cdot 3 \cdot \frac{\alpha(1-\alpha)}{R_B} \cdot \text{sign}(p_{sat} - p) \sqrt{\frac{2}{3} \frac{|p_{sat} - p|}{\rho_l}}$$
- **Parameters:** $n_{Bubbles}$ (nuclei density), $p_{sat}$ (saturation pressure), $R_B$ (bubble radius)
- **Use:** Cavitation in pumps, valves, propellers
- **Solver:** `interPhaseChangeFoam`
- **Calibration:** $n = 10^{11}-10^{15}$ m⁻³ (start with $10^{13}$)

**Hertz-Knudsen model (molecular kinetics):**
$$\Gamma = \frac{2\sigma}{2-\sigma} \sqrt{\frac{M}{2\pi R}} \left(\frac{p_{sat}}{\sqrt{T_{sat}}} - \frac{p}{\sqrt{T}}\right)$$
- **Parameters:** $\sigma$ (accommodation coefficient), $M$ (molecular weight)
- **Use:** Research, flash evaporation, high accuracy required
- **Solver:** Custom or `multiphaseEulerFoam`
- **Calibration:** $\sigma = 0.01-1.0$ (literature values)

**Implementation checklist:**
- [ ] Select appropriate solver and model
- [ ] Define phases in `constant/phaseProperties`
- [ ] Set boundary conditions (pressure, temperature, α)
- [ ] Configure solution control (maxCo, nCorrectors)
- [ ] Implement monitoring (vapor volume, mass transfer rate)
- [ ] Run calibration procedure (adjust relaxation parameters)
- [ ] Verify mass and energy conservation
- [ ] Validate with experimental data

### Best Practices

1. **Start simple:** Use Schnerr-Sauer for cavitation, Lee for boiling (Hertz-Knudsen for advanced research)
2. **Calibrate carefully:** Adjust relaxation coefficients against experimental data ($r$ or $n_{Bubbles}$)
3. **Ensure stability:** Use `maxCo < 0.3`, `nCorrectors ≥ 3`, adjustable time stepping
4. **Verify conservation:** Check mass balance error < 0.1%, energy balance for boiling
5. **Mesh resolution:** Refine interface region (at least 10 cells across interface thickness)
6. **Monitor convergence:** Track vapor volume, mass transfer rate, residuals
7. **Document parameters:** Record all calibrated values for reproducibility

---

## 8. Concept Check (ทดสอบความเข้าใจ)

<details>
<summary><b>Question 1: What are the two fundamental drivers of phase change?</b></summary>

**Answer:**

**Two primary mechanisms:**
1. **Temperature-driven:** $T \neq T_{sat}$ (boiling, condensation, solidification)
2. **Pressure-driven:** $p < p_{sat}$ (cavitation)

**Key insight:** Phase change is nature's way of restoring thermodynamic equilibrium. When local conditions deviate from saturation, mass transfer occurs until equilibrium is restored.

**Examples:**
- Water at 380 K, 1 atm → $T > T_{sat}$ (373 K) → **boiling** (evaporation)
- Water at 20°C, 2 kPa → $p < p_{sat}$ (2.3 kPa) → **cavitation** (evaporation)
- Steam at 360 K, 1 atm → $T < T_{sat}$ (373 K) → **condensation**

**Physical interpretation:**
- $T > T_{sat}$: Liquid has excess thermal energy → molecules escape → vaporization
- $p < p_{sat}$: Pressure drops below vapor pressure → liquid "flashes" to vapor → cavitation
- $T < T_{sat}$: Vapor loses thermal energy → molecules condense → liquid formation

</details>

<details>
<summary><b>Question 2: Why is the mass transfer source term (Γ) necessary in the VOF equation?</b></summary>

**Answer:**

**Standard VOF equation (no phase change):**
$$\frac{\partial \alpha}{\partial t} + \nabla \cdot (U\alpha) = 0$$

This equation conserves volume fraction but **prevents phase transformation**. It only tracks the motion of existing phases.

**Modified VOF with phase change:**
$$\frac{\partial \alpha}{\partial t} + \nabla \cdot (U\alpha) = \underbrace{\Gamma_{evap} - \Gamma_{cond}}_{\text{Mass Transfer}}$$

**Why this matters:**

**Physical interpretation:**
- **$\Gamma_{evap} > 0$:** Liquid converts to vapor (α_vapor increases, α_liquid decreases)
- **$\Gamma_{cond} > 0$:** Vapor converts to liquid (α_vapor decreases, α_liquid increases)
- **Without Γ:** Volume fractions would remain constant regardless of T or p (no phase change)

**Conservation properties:**
- **Mass conservation:** $\Gamma_{evap}/\rho_v = \Gamma_{cond}/\rho_l$ (mass leaving liquid = mass entering vapor)
- **Energy conservation:** (for boiling) Energy removed = $\Gamma \cdot h_{lv}$ (latent heat)

**Example calculation:**
```cpp
// Water at 380 K (boiling)
T = 380 K;  // 7 K above Tsat (373 K)
alpha_l = 1.0;  // Initially pure liquid
r = 100;  // Relaxation coefficient

// Mass transfer rate (Lee model)
Gamma_evap = r * alpha_l * rho_l * (T - Tsat)/Tsat
           = 100 * 1.0 * 1000 * (380 - 373)/373.15
           = 1876 kg/(m³·s)

// This means 1876 kg of liquid vaporizes per m³ per second
```

**Key takeaway:** Γ represents mass crossing the phase boundary per unit volume per unit time, enabling the VOF equation to account for phase transformation.

</details>

<details>
<summary><b>Question 3: How do I choose between Lee, Hertz-Knudsen, and Schnerr-Sauer models?</b></summary>

**Answer:**

**Decision flowchart:**

```
Is phase change pressure-driven (cavitation)?
├─ Yes → Use Schnerr-Sauer (robust, validated for hydraulic applications)
│
└─ No (temperature-driven boiling/condensation)
    ├─ Need high accuracy + have good data?
    │  └─ Yes → Hertz-Knudsen (physically rigorous, molecular-scale accuracy)
    │
    └─ Need robust engineering solution?
       └─ Yes → Lee model (simple, efficient, requires calibration)
```

**Comparison table:**

| Model | Accuracy | Speed | Calibration | Data Required | Best For |
|-------|----------|-------|-------------|---------------|----------|
| **Schnerr-Sauer** | Medium | Fast | Low (nBubbles) | Bubble nuclei distribution | Cavitation in pumps, valves |
| **Lee** | Low-Medium | Fast | High (r coefficient) | Thermal properties ($h_{lv}$, $T_{sat}$) | Boiling, condensation |
| **Hertz-Knudsen** | High | Slow | Medium (σ coefficient) | Molecular properties ($\sigma$, $M$) | Research, validation |

**Detailed decision criteria:**

**Use Schnerr-Sauer (pressure-driven) when:**
- ✅ Primary mechanism is pressure drop below saturation
- ✅ Working with hydraulic equipment (pumps, valves, turbines)
- ✅ Need robust, industrially-validated solution
- ✅ Computational efficiency is important
- ❌ Don't use when thermal effects are significant

**Use Lee model (temperature-driven) when:**
- ✅ Primary mechanism is temperature difference from $T_{sat}$
- ✅ Simulating boiling or condensation
- ✅ Need fast, practical engineering solution
- ✅ Willing to calibrate relaxation coefficient
- ❌ Don't use for pure cavitation (pressure-driven)

**Use Hertz-Knudsen when:**
- ✅ Need highest physical accuracy (research-grade)
- ✅ Both pressure and temperature effects are important
- ✅ Have accurate thermophysical properties
- ❌ Don't use for routine engineering (too expensive, less robust)

**Key questions to ask:**
1. **What is the primary driving force?** (Pressure → Schnerr-Sauer, Temperature → Lee or Hertz-Knudsen)
2. **What is the application?** (Industrial design → robust models, Research → accurate models)
3. **What data is available?** (Bubble nuclei → Schnerr-Sauer, Thermal → Lee, Molecular → Hertz-Knudsen)
4. **What are computational constraints?** (Limited → Lee, Adequate → Schnerr-Sauer, HPC → Hertz-Knudsen)

</details>

<details>
<summary><b>Question 4: What causes simulation divergence in phase change problems?</b></summary>

**Answer:**

**Common causes (in order of likelihood):**

**1. Timestep too large (60% of cases)**
- **Problem:** Rapid phase change → stiff source terms → numerical instability
- **Symptoms:** Residuals spike, simulation crashes, "maximum number of iterations" error
- **Fix:** 
  ```cpp
  maxCo 0.2-0.3;  // Reduce from default (1.0)
  adjustTimeStep yes;
  maxDeltaT 1e-3;
  minDeltaT 1e-7;
  ```
- **Verification:** Check Courant number with `postProcess -func CourantNo`

**2. Incorrect relaxation coefficient (20% of cases)**
- **Problem:** Lee model $r$ too high → unstable mass transfer → oscillations
- **Symptoms:** Vapor volume fluctuates wildly, temperature spikes
- **Fix:**
  ```cpp
  // Start with conservative value
  r = 10-50;  // Instead of 100-1000
  
  // Gradually increase if stable
  r = 50 → 100 → 200 (monitor stability)
  ```
- **Verification:** Plot vapor volume vs. time (should be smooth, not oscillatory)

**3. Inconsistent boundary conditions (10% of cases)**
- **Problem:** Wall T conflicting with phase change direction
- **Symptoms:** Phase change in wrong direction (condensation instead of boiling)
- **Fix:** 
  ```cpp
  // For boiling: ensure T_wall > T_sat
  heatedWall { value uniform 383.15; }  // > Tsat (373.15)
  
  // For condensation: ensure T_wall < T_sat
  coldWall { value uniform 363.15; }  // < Tsat (373.15)
  ```
- **Verification:** Check T field visualization in ParaView

**4. Insufficient pressure-velocity coupling (10% of cases)**
- **Problem:** Large density variations → weak coupling between p and U
- **Symptoms:** Pressure oscillations, "momentum predictor diverging"
- **Fix:**
  ```cpp
  PIMPLE
  {
      nCorrectors 4-5;  // Increase from default (2)
      nOuterCorr 2;     // Add outer iterations
  }
  
  relaxationFactors
  {
      p   0.3;  // Aggressive pressure relaxation
      rho 0.05; // Very conservative density relaxation
  }
  ```
- **Verification:** Monitor p residuals (should decrease monotonically)

**Debugging workflow:**
```bash
# Step 1: Check Courant number
foamListTimes | tail -1 | xargs -I {} postProcess -func "CourantNo" -time {}
# Look for maxCo > 0.3 (problematic)

# Step 2: Monitor mass transfer rate
grep "Vapor production rate:" log.interPhaseChangeFoam
# Look for sudden spikes or oscillations

# Step 3: Verify global mass balance
postProcess -func "volIntegrate(rho)" > mass_balance.log
# Check: ΔM/M_initial < 0.001

# Step 4: Check pressure-velocity coupling
grep "PIMPLE: iteration" log.interPhaseChangeFoam
# Look for "solution diverged" or "max iterations reached"
```

**Proactive stability measures:**
```cpp
// Use under-relaxation
relaxationFactors { p 0.3; rho 0.05; U 0.7; }

// Increase solver iterations
nCorrectors 4;
nAlphaCorr 2;

// Use implicit schemes for convection
div(phi,U) Gauss linearUpwindV grad(U);
```

**Key takeaway:** Phase change simulations are **stiff** (rapid source terms). Always start with conservative settings (small dt, low relaxation) and gradually increase as stability is verified.

</details>

<details>
<summary><b>Question 5: How do I calibrate the Lee model relaxation coefficient (r)?</b></summary>

**Answer:**

**Physical meaning of $r$:** Characteristic frequency of phase change [1/s]. Higher $r$ = faster phase change rate.

**Step-by-step calibration procedure:**

**Step 1: Initial guess**
```cpp
// Based on application type
r = 100;  // s⁻¹ - Typical starting point for water boiling
```

**Step 2: Run simulation with experimental data**
```bash
interCondensatingEvaporatingFoam > log.calibration
```

**Step 3: Compare results with experiments**
```cpp
// Metrics to compare:
1. Vapor volume fraction vs. time
2. Heat flux at wall: q'' = -k * dT/dy
3. Bubble detachment frequency (if available)
```

**Step 4: Adjust $r$ based on discrepancy**
```cpp
// If boiling too slow (vapor production underestimated):
r *= 2;  // Double the relaxation coefficient

// If boiling too fast or unstable:
r /= 2;  // Halve the relaxation coefficient

// Repeat until agreement (typical range: 10-1000 s⁻¹)
```

**Step 5: Verify robustness**
```cpp
// Test calibrated r with different conditions:
// - Different wall temperatures
// - Different flow rates
// - Different geometries

// If r works across conditions → good calibration
// If r needs adjustment → model may not be appropriate
```

**Typical values by application:**
```cpp
// Pool boiling (nucleate boiling regime)
r = 50-200 s⁻¹;

// Film boiling (rapid vaporization)
r = 500-1000 s⁻¹;

// Condensation (slower phase change)
r = 10-50 s⁻¹;

// Flash evaporation (very rapid)
r = 1000+ s⁻¹;
```

**Example calibration for pool boiling:**
```cpp
// Experimental data: Heat flux = 50 kW/m² at ΔT = 5 K

// Iteration 1: r = 100
// Simulation result: Heat flux = 20 kW/m² (underpredicted)
// Action: Increase r

// Iteration 2: r = 250
// Simulation result: Heat flux = 48 kW/m² (close)
// Action: Slight increase

// Iteration 3: r = 300
// Simulation result: Heat flux = 52 kW/m² (good agreement)
// Action: Stop calibration, use r = 300

// Validation: Test at ΔT = 10 K
// Experimental: 100 kW/m², Simulation: 105 kW/m² (5% error)
// Conclusion: Calibration successful (error < 10%)
```

**Calibration checklist:**
- [ ] Compare vapor volume fraction vs. time
- [ ] Compare heat flux: $q'' = -k \nabla T$ at wall
- [ ] Compare bubble detachment frequency (if available)
- [ ] Verify results are grid-independent (refine mesh by 2×)
- [ ] Test robustness with different operating conditions
- [ ] Document final $r$ value for reproducibility

**Key warning:** $r$ is **not** a physical property (it's a numerical parameter). Calibrated values are **not transferable** between different geometries, flow conditions, or fluids. Always recalibrate for new applications.

</details>

---

## 9. Related Documentation

### Prerequisites
- **MODULE_04:** [Multiphase Flow Fundamentals](../../MODULE_04_MULTIPHASE_FUNDAMENTALS) — VOF method, phase fraction transport
- **MODULE_03:** [Pressure-Velocity Coupling](../../MODULE_03_SINGLE_PHASE_FLOW/CONTENT/02_PRESSURE_VELOCITY_COUPLING) — PIMPLE algorithm

### Advanced Topics
- **Cavitation:** [02_Cavitation_Modeling.md](02_Cavitation_Modeling.md) — Detailed cavitation modeling techniques
- **Population Balance:** [03_Population_Balance_Modeling.md](03_Population_Balance_Modeling.md) — Bubble size distribution modeling
- **Complex Phenomena:** [00_Overview.md](00_Overview.md) — Roadmap of advanced multiphase phenomena

### Solver Documentation
- **interPhaseChangeFoam:** OpenFOAM user guide — Pressure-driven phase change
- **interCondensatingEvaporatingFoam:** OpenFOAM source code — Temperature-driven phase change
- **multiphaseEulerFoam:** OpenFOAM wiki — Euler-Euler multiphase with phase change

### External Resources
- **Literature:**
  - Brennen (1995) "Cavitation and Bubble Dynamics" — Fundamentals of cavitation
  - Kandlikar (1990) "Heat Transfer Mechanisms During Pool Boiling" — Boiling curves
  - Ishii & Hibiki (2011) "Thermo-Fluid Dynamics of Two-Phase Flow" — Multiphase theory

- **Benchmark Cases:**
  - Stutz & Reboud (1997) "Experiments on unsteady cavitation" — Venturi cavitation validation
  - Kunz et al. (2000) "A preconditioned Navier-Stokes method for two-phase flows" — 2D cavitating flow

- **Tutorials:**
  - `$FOAM_TUTORIALS/multiphase/interPhaseChangeFoam/` — Cavitation examples
  - `$FOAM_RUN/tutorials/multiphase/interCondensatingEvaporatingFoam/` — Boiling examples

---

**End of Phase Change Modeling Documentation**

For questions or issues, consult the OpenFOAM community forum: https://www.cfd-online.com/Forums/openfoam/