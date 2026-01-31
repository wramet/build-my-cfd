# 🌊 01: Complex Multiphase Phenomena (ปรากฏการณ์หลายเฟสที่ซับซ้อน)

**Difficulty**: Advanced | **Key Solvers**: `reactingTwoPhaseEulerFoam`, `multiphaseEulerFoam`, `interPhaseChangeFoam`

---

## 📚 Prerequisites (ความรู้พื้นฐานที่ต้องมี)

Before diving into this module, you should be comfortable with:

### Required Knowledge
- **MODULE 04: Multiphase Fundamentals** — Understanding of VOF method, Euler-Euler approach, and basic interfacial forces
- **Basic Thermodynamics** — Concepts of saturation pressure, latent heat, and phase equilibrium
- **Turbulence Modeling** — RANS/LES approaches for multiphase flows
- **OpenFOAM Basics** — Case structure, boundary conditions, and solver selection

### Key Skills to Review
- Setting up multiphase cases in OpenFOAM
- Understanding pressure-velocity coupling (PIMPLE algorithm)
- Mesh quality requirements for interface capturing

> **🎯 Self-Assessment**: Can you explain the difference between VOF and Euler-Euler methods? If not, review MODULE 04 before proceeding.

---

## 🎯 Learning Objectives (วัตถุประสงค์การเรียนรู้)

By the end of this module, you will be able to:

### WHAT (Define and Identify)
1. **Identify Complex Multiphase Phenomena** — Distinguish between simple two-phase flows and complex phenomena involving mass transfer, phase change, and polydisperse systems
2. **Classify Phase Change Mechanisms** — Differentiate between temperature-driven (boiling/condensation) and pressure-driven (cavitation) phase change
3. **Define Population Balance** — Understand when PBE is necessary versus constant-diameter assumptions

### WHY (Engineering Significance)
4. **Select Appropriate Models** — Choose the right cavitation, phase change, or population balance model based on:
   - Physical regime (pressure vs temperature driven)
   - Computational constraints
   - Required accuracy
   - Timescales of interest
5. **Predict Industrial Problems** — Anticipate cavitation damage, boiling crises, or bubble size effects in equipment design

### HOW (Implementation in OpenFOAM)
6. **Configure Phase Change Models** — Set up thermal phase change with proper latent heat and mass transfer coefficients
7. **Implement Cavitation Models** — Configure Schnerr-Sauer, Kunz, or Merkle models with appropriate parameters
8. **Solve Population Balance Equations** — Implement QMOM methods for polydisperse systems
9. **Troubleshoot Convergence Issues** — Identify and resolve common numerical instabilities in coupled physics simulations

---

## 🔬 Module Roadmap (แผนผังการเรียนรู้)

```mermaid
graph TD
    A[Complex Multiphase Phenomena] --> B[Phase Change Modeling]
    A --> C[Cavitation Modeling]
    A --> D[Population Balance]

    B --> B1[Temperature-Driven]
    B --> B2[Boiling/Condensation]
    B --> B3[Mass Transfer Models]

    C --> C1[Pressure-Driven]
    C --> C2[Bubble Dynamics]
    C --> C3[Model Selection]

    D --> D1[Polydisperse Systems]
    D --> D2[QMOM Methods]
    D --> D3[Breakup/Coalescence]

    style A fill:#f96,stroke:#333,stroke-width:4px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C fill:#bfb,stroke:#333,stroke-width:2px
    style D fill:#fbf,stroke:#333,stroke-width:2px
```

### Content Overview

| Section | Focus | Key Solvers | Complexity |
|---------|-------|-------------|------------|
| **01 - Phase Change** | Temperature-driven phase change, boiling, condensation | `reactingTwoPhaseEulerFoam`, `interCondensatingEvaporatingFoam` | ⭐⭐⭐ |
| **02 - Cavitation** | Pressure-driven phase change in high-speed flows | `interPhaseChangeFoam`, `multiphaseEulerFoam` | ⭐⭐⭐⭐ |
| **03 - Population Balance** | Polydisperse bubble/droplet systems | `multiphaseEulerFoam` + PBE | ⭐⭐⭐⭐⭐ |

---

## 💡 Key Concepts: Beyond Simple Multiphase Flow

### From MODULE 04 to MODULE 06: The Complexity Leap

In MODULE 04 (Multiphase Fundamentals), we learned:
- **Two immiscible phases** (e.g., water and air at room temperature)
- **No mass transfer** between phases
- **Constant phase properties** (density, viscosity)

In THIS module, we add complexity:

| Aspect | MODULE 04 (Simple) | MODULE 06 (Complex) |
|--------|-------------------|---------------------|
| **Phases** | 2, immiscible | 2+, with mass transfer |
| **Properties** | Constant | Variable (ρ, μ change with T, p) |
| **Equations** | Continuity + Momentum | + Energy + Species + PBE |
| **Coupling** | One-way | Two-way, strong coupling |
| **Timescales** | Single | Multiple (fast phase change, slow transport) |

### The Three Pillars of Complex Multiphase

```mermaid
graph LR
    A[Complex Multiphase] --> B[Phase Change]
    A --> C[Cavitation]
    A --> D[Population Balance]

    B --> B1[WHAT: Temperature-driven<br>phase transition]
    B --> B2[WHY: Boiling in reactors,<br>condensation in heat exchangers]
    B --> B3[HOW: Thermal phase change<br>models, latent heat]

    C --> C1[WHAT: Pressure-driven<br>vapor formation]
    C --> C2[WHY: Pump/propeller damage,<br>performance loss]
    C --> C3[HOW: Schnerr-Sauer,<br>Kunz, Merkle models]

    D --> D1[WHAT: Size distribution<br>evolution]
    D --> D2[WHY: Interfacial area<br>effects, drag laws]
    D --> D3[HOW: QMOM, moment methods,<br>breakup/coalescence kernels]

    style A fill:#ffd700,stroke:#333,stroke-width:3px
```

---

## 🔥 Phenomenon 1: Phase Change (การเปลี่ยนสถานะ)

### WHAT: Definition and Types

**Phase change** is the transition of matter between liquid, vapor, and solid states, accompanied by:
- **Latent heat absorption/release** ($h_{lv}$ for liquid-vapor)
- **Density jumps** (ρ_water ≈ 1000 kg/m³, ρ_steam ≈ 0.6 kg/m³)
- **Mass transfer** across interfaces

| Type | Driving Force | Direction | Example |
|------|---------------|-----------|---------|
| **Boiling** | $T > T_{sat}$ | Liquid → Vapor | Water boiling at 100°C |
| **Condensation** | $T < T_{sat}$ | Vapor → Liquid | Steam condensing on cold surface |
| **Evaporation** | Concentration gradient | Liquid → Vapor (surface only) | Water evaporating at room temperature |
| **Solidification** | $T < T_{melting}$ | Liquid → Solid | Metal casting, ice formation |

### WHY: Engineering Importance

**Why do we care about phase change in CFD?**

1. **Heat Transfer Enhancement** — Boiling can achieve heat transfer coefficients 10-100× higher than single-phase convection
   - **Design Impact**: Nuclear reactor cooling, electronics thermal management, refrigeration systems
   - **Risk**: Boiling crisis (critical heat flux) can cause system failure

2. **Phase Distribution Matters** — The volume fraction of each phase affects:
   - Density and viscosity of the mixture
   - Flow patterns (bubbly, slug, churn, annular)
   - Heat and mass transfer rates

3. **Pressure Drop** — Phase change affects pressure drop in pipes and equipment
   - Two-phase multipliers increase pressure drop beyond single-phase predictions
   - Critical for pump sizing and system design

> **💡 Decision Criteria**: When to include phase change modeling?
> - **YES**: Boiling/condensation heat exchangers, reactors, cryogenics, cooling systems
> - **NO**: Adiabatic gas-liquid flows (e.g., oil-gas pipelines at constant T)

### HOW: OpenFOAM Implementation Overview

**Governing Equation Structure**:

```cpp
// Mass transfer source term in phase continuity equation
// For phase α (liquid) and phase β (vapor):
∂(αₗρₗ)/∂t + ∇·(αₗρₗU) = -ṁ'''    // Liquid loss by evaporation
∂(αᵥρᵥ)/∂t + ∇·(αᵥρᵥU) = +ṁ'''    // Vapor gain by evaporation

where ṁ''' = mass transfer rate per unit volume [kg/(m³·s)]
```

**Key Implementation Components**:

```cpp
// 1. Phase change model selection in constant/phaseProperties
phaseChangeModel thermalPhaseChange;  // OR Lee, HertzKnudsen

thermalPhaseChangeCoeffs
{
    hLv     2.26e6;      // Latent heat of vaporization [J/kg]
    Tsat    373.15;      // Saturation temperature [K]
    r       100;         // Mass transfer coefficient [1/s]
}

// 2. Energy equation coupling (automatic in reactingTwoPhaseEulerFoam)
// T field drives phase change through (T - Tsat)

// 3. Thermophysical properties must include:
// - Specific heat (Cp) for both phases
// - Thermal conductivity (k)
// - Latent heat (hLv)
```

**Solver Selection Guide**:

| Solver | When to Use | Key Features |
|--------|-------------|--------------|
| `interCondensatingEvaporatingFoam` | VOF method, sharp interface | Volume tracking, thermal phase change |
| `reactingTwoPhaseEulerFoam` | Euler-Euler, dispersed phase | Heat transfer, reactions, phase change |
| `multiphaseEulerFoam` | 3+ phases with phase change | Polydisperse, general multiphase |

> **📖 Detailed Implementation**: See [01_Phase_Change_Modeling.md](01_Phase_Change_Modeling.md) for complete setup procedures, boundary conditions, and troubleshooting.

---

## 🌪️ Phenomenon 2: Cavitation (การเกิดโพรงอากาศ)

### WHAT: Definition and Mechanism

**Cavitation** is the formation of vapor cavities in a liquid when local pressure drops below the vapor pressure:

$$p_{local} < p_{sat}(T) \rightarrow \text{liquid} \rightarrow \text{vapor bubbles}$$

**Three Stages of Cavitation**:

1. **Nucleation** — Bubble formation at low-pressure sites (imperfections, dissolved gas)
2. **Growth** — Rapid bubble expansion in low-pressure region
3. **Collapse** — Violent bubble implosion in high-pressure region (shock waves, damage)

### Physical Intuition: The Soda Bottle Analogy

> **🎯 Real-World Comparison**:
> - **Phase Change (Boiling)**: Like **popcorn** — heat (energy) causes transformation
> - **Cavitation**: Like **opening a soda bottle** — pressure drop causes gas release (no heating required!)

| Aspect | Boiling | Cavitation |
|--------|---------|------------|
| **Driving Force** | Temperature increase | Pressure decrease |
| **Primary Variable** | $T > T_{sat}$ | $p < p_{sat}$ |
| **Energy Input** | External heating required | No external heat (Bernoulli effect) |
| **Typical Locations** | Heated surfaces, reactors | Pump impellers, propellers, valves |

### WHY: Engineering Significance

**Why is cavitation critical in engineering design?**

| Impact | Mechanism | Consequence |
|--------|-----------|-------------|
| **Material Damage** | Bubble collapse near surfaces → micro-jets, shock waves (> 1000 MPa) | Pitting, erosion, fatigue failure |
| **Noise & Vibration** | Oscillatory bubble dynamics | Acoustic noise, structural vibration, passenger discomfort |
| **Performance Loss** | Vapor cavity changes flow patterns | Reduced pump head, propeller thrust drop |
| **Efficiency Reduction** | Energy loss to bubble formation | Decreased system efficiency |

**Typical Applications**:
- **Pumps** — Cavitation at impeller inlet limits suction head
- **Propellers** — Tip vortex cavitation affects thrust and efficiency
- **Valves & Orifices** — Local acceleration causes pressure drop
- **Hydro turbines** — Blade cavitation reduces power output

> **💡 Design Decision**: Cavitation modeling is ESSENTIAL when:
> - Fluid velocities > 10 m/s in water
> - Pressure drops approach vapor pressure
> - Equipment lifetime is critical (marine, power generation)
> - Noise/vibration is a concern (submarines, passenger vehicles)

### HOW: OpenFOAM Implementation Overview

**Model Selection Criteria**:

| Model | Accuracy | Stability | Best For | Computational Cost |
|-------|----------|-----------|----------|-------------------|
| **Schnerr-Sauer** | High | High | General purpose, pumps | Medium |
| **Kunz** | Medium | Very High | Marine propellers (robust) | Medium |
| **Merkle** | High | Medium | Industrial, turbomachinery | Medium |
| **Zwart** | High | High | Pumps, inducers | Medium |

**Basic Setup Structure**:

```cpp
// constant/transportProperties
phases (water vapor);

phaseChangeModel SchnerrSauer;

SchnerrSauerCoeffs
{
    n       1e13;    // Nucleation site density [1/m³]
    dNuc    2e-6;    // Nucleation diameter [m]
    pSat    2300;    // Saturation pressure [Pa] at 20°C
    Cc      1;       // Condensation coefficient
    Cv      1;       // Vaporization coefficient
}

// Mass transfer rate (calculated automatically):
// If p < pSat: ṁ''' = C_v * (rate of bubble growth)
// If p > pSat: ṁ''' = C_c * (rate of bubble collapse)
```

**Key Numerical Requirements**:

```cpp
// system/controlDict
maxCo           0.3;      // Critical for stability!
maxAlphaCo      0.3;      // Volume fraction CFL limit

// system/fvSolution
PIMPLE
{
    nCorrectors      3;    // Increased for pressure-velocity coupling
    nAlphaCorr      1;
    nAlphaSubCycles 2;    // Sub-cycle volume fraction
}
```

> **📖 Detailed Implementation**: See [02_Cavitation_Modeling.md](02_Cavitation_Modeling.md) for:
> - Complete model formulations and equations
> - Boundary condition setup
> - Mesh requirements for pressure gradient capture
> - Post-processing: cavitation number, vapor volume visualization

---

## 📊 Phenomenon 3: Population Balance (สมดุลประชากร)

### WHAT: Definition and Motivation

**Population Balance Equation (PBE)** tracks the evolution of particle/bubble size distributions in multiphase flows.

**Why do we need it?**

In MODULE 04, we assumed:
- **Monodisperse systems** — all bubbles/droplets have the same diameter
- **Constant diameter** — no breakup, no coalescence

**But real systems are POLYDISPERSE**:

```mermaid
graph LR
    A[Small Bubbles<br>d = 1 mm] -->|Coalescence| B[Medium Bubbles<br>d = 3 mm]
    B -->|Coalescence| C[Large Bubbles<br>d = 10 mm]
    C -->|Breakup| B
    B -->|Breakup| A

    style A fill:#8f8,stroke:#333
    style B fill:#ff8,stroke:#333
    style C fill:#f88,stroke:#333
```

**Key Processes**:

| Process | Mechanism | Effect on Distribution |
|---------|-----------|------------------------|
| **Breakup** — การแตกตัว | Turbulent eddies > surface tension | Shifts to smaller sizes |
| **Coalescence** — การรวมตัว | Bubble collisions + film drainage | Shifts to larger sizes |
| **Growth** — การเติบโต | Phase change (condensation/evaporation) | Changes size uniformly |
| **Nucleation** — การเกิดใหม่ | Supersaturation, nucleation sites | Adds small particles |

### WHY: Engineering Impact

**Why does bubble size distribution matter?**

1. **Interfacial Area** — Mass/heat transfer scales with total surface area:
   $$a_{interfacial} = \sum_i (n_i \cdot \pi d_i^2)$$
   - **Smaller bubbles** → larger interfacial area → faster mass transfer
   - **Critical for**: Reactors, fermenters, gas-liquid contactors

2. **Drag and Rise Velocity** — Bubble size affects terminal velocity:
   - Small bubbles (d < 1 mm): spherical, rise slowly
   - Large bubbles (d > 10 mm): ellipsoidal/cap-shaped, rise fast
   - **Affects**: Flow patterns, phase distribution

3. **Model Accuracy** — Constant-diameter assumption fails when:
   - Wide size distribution exists (span > 2)
   - Significant breakup/coalescence occurs
   - System has long residence times

> **💡 Decision Criteria**: When to use Population Balance?
> - **YES**: Bubble columns, fermenters, emulsions, sprays with breakup
> - **NO**: Narrow size distributions, short residence times, monodisperse systems

### HOW: OpenFOAM Implementation Overview

**Solution Methods**:

| Method | Approach | Pros | Cons | Computational Cost |
|--------|----------|------|------|-------------------|
| **Discrete (DQMOM)** | Track size bins directly | Accurate | Expensive (many equations) | High |
| **Moment-based (QMOM)** | Track statistical moments | Efficient | Requires quadrature | Medium |
| **Class Method** | Discrete sections | Flexible | Can be slow | Medium-High |

**QMOM (Quadrature Method of Moments)** is most common:

```cpp
// Instead of tracking every size, track moments:
// M_k = ∫₀^∞ n(d) · d^k dd

// M_0 = Total number of particles [1/m³]
// M_1 = Total length [m/m³]
// M_2 = Total surface area [m²/m³]
// M_3 = Total volume [m³/m³]

// Evolution equation for each moment:
∂M_k/∂t + ∇·(U M_k) = B_k - D_k   // Birth - Death terms
```

**Implementation Structure**:

```cpp
// constant/phaseProperties
phases (water air);

populationBalance on;

populationBalanceCoeffs
{
    // Continuous phase (water)
    continuousPhaseName water;

    // Dispersed phase (air bubbles)
    dispersedPhase air;

    // Size distribution moments
    nNodes  4;    // Number of quadrature nodes

    // Breakup kernel
    breakupModel Lehr;
    breakupCoeffs { ... }

    // Coalescence kernel
    coalescenceModel constant;
    coalescenceCoeffs { ... }
}
```

**Key Outputs**:

```cpp
// Fields calculated by PBE:
// - n: Number density distribution [1/m⁴]
// - d: Mean Sauter diameter [m]
// - d32: Sauter mean diameter (surface-weighted)
// - a: Interfacial area density [1/m]

// Post-process with:
foamListTimes
paraFoam -builtin
```

> **📖 Detailed Implementation**: See [03_Population_Balance_Modeling.md](03_Population_Balance_Modeling.md) for:
> - Complete PBE formulation
> - Kernel selection (breakup/coalescence models)
> - QMOM implementation details
> - Validation cases and tutorials

---

## 🔄 R410A Flow Regimes in Evaporator Tubes (สภาพการไหลของ R410A ในท่�ะระบายความร้อน)

### Flow Regime Maps for Evaporator Tubes (แผนภูมิสภาพการไหลสำหรับท่อระบายความร้อน)

#### Baker Map for Horizontal Tubes (แผนภูมิ เบกเกอร์ สำหรับท่อแนวนอน)

The **Baker map** is the standard flow regime classification for horizontal tube flow. For R410A evaporators, we must consider the refrigerant's unique thermophysical properties:

```mermaid
graph TB
    subgraph Baker Map for R410A
        A[Gas Fraction x] --> B[Regime Identification]
        B --> C{Superficial Gas Velocity J_g}
        C -->|J_g < 0.5 m/s| D[Bubbly Flow]
        C -->|0.5 < J_g < 3 m/s| E[Slug Flow]
        C -->|3 < J_g < 10 m/s| F[Churn Flow]
        C -->|J_g > 10 m/s| G[Annular/Mist Flow]
    end

    style D fill:#8f8,stroke:#333
    style E fill:#ff8,stroke:#333
    style F fill:#f88,stroke:#333
    style G fill:#88f,stroke:#333
```

**R410A-Specific Adjustments**:
- ⭐ Density ratio $\rho_l/\rho_g$ ≈ 25 (vs. 100 for water/steam) affects transition velocities
- ⭐ Surface tension σ ≈ 8.2 mN/m (25% lower than water) promotes bubble coalescence
- ⭐ Oil content (POE lubricant) shifts transitions by 10-20%

#### Taitel-Dukler Map for Vertical Tubes (แผนภูมิ ไทเทล-ดักเลอร์ สำหรับท่อแนวตั้ง)

Vertical R410A flow follows different patterns due to buoyancy effects:

```mermaid
graph TD
    subgraph Vertical Flow Regimes
        A[Kinematic Ratio F] --> B{Flow Pattern}
        F = j_g / sqrt(g D (ρ_l - ρ_g)/ρ_l)

        B -->|F < 0.04| C[Bubbly]
        B -->|0.04 < F < 0.35| D[Slug]
        B -->|0.35 < F < 1.0| E[Churn]
        B -->|F > 1.0| F[Annular]
    end

    style C fill:#8f8,stroke:#333
    style D fill:#ff8,stroke:#333
    style E fill:#f88,stroke:#333
    style F fill:#88f,stroke:#333
```

**Critical Parameters**:
- F < 0.04: Bubble coalescence dominates
- 0.04 < F < 0.35: Taylor bubble formation
- F > 1.0: Strong upward annular flow

### Flow Regimes in R410A Evaporators (สภาพการไหลของ R410A ในท่อระบายความร้อน)

#### Bubbly Flow (การไหลแบบฟองอากาศ)

**Characteristics**:
- Quality range: x < 0.1
- Bubble shape: spherical → elliptical as velocity increases
- Bubble diameter: 0.1-2 mm (smaller than water due to lower σ)
- Heat transfer mechanism: forced convection + nucleation

```mermaid
graph LR
    subgraph Bubbly Flow
        A[Liquid continuous phase] --> B[Individual gas bubbles]
        B --> C[d_b = 0.1-2 mm]
        C --> D[Bubble coalescence]
    end
```

**R410A-Specific Features**:
- ⭐ Nucleation sites: Higher density due to lower surface tension
- ⭐ Bubble departure diameter: Smaller than refrigerants with higher σ
- ⭐ Heat transfer enhancement: 5-10× single-phase flow

#### Slug Flow (การไหลแบบน้ำเต้า)

**Characteristics**:
- Quality range: 0.1 < x < 0.3
- Structure: Taylor bubbles with liquid slugs
- Bubble length: 1-5 tube diameters
- Frequency: 5-20 Hz depending on tube diameter

```cpp
// Typical slug flow parameters for R410A
const tubeDiameter = 0.0095;    // 9.5 mm
const bubbleLength = 0.03;       // 30 mm (3-4 D)
const voidFraction = 0.3;       // At slug flow transition
```

**Heat Transfer Characteristics**:
- Local heat transfer peaks 2-5× single-phase
- Intermittent cooling of wall surface
- Enhanced mixing compared to bubbly flow

#### Annular Flow (การไหลแบบวงแหวน)

**Characteristics**:
- Quality range: x > 0.3
- Structure: Liquid film on walls, gas core in center
- Film thickness: 0.1-1 mm
- Wave formation on liquid film

```mermaid
graph TD
    subgraph Annular Flow Cross-Section
        A[Tube Wall] --> B[Liquid Film δ = 0.1-1 mm]
        B --> C[Vapor Core]
        C --> D[Droplets in vapor core?]
        D -->|At high x| E[Mist flow]
    end

    style A fill:#333
    style B fill:#00f
    style C fill:#8f8
    style D fill:#ff8
    style E fill:#f88
```

**R410A Film Dynamics**:
- Film flow rate: $Q_f = \frac{\rho_l \delta^2}{\mu_l}$
- Interfacial waves: Increase heat transfer by 30-50%
- Dryout risk: Critical at x > 0.8 for 10 mm tubes

#### Mist Flow (การไหลแบบหมอก)

**Characteristics**:
- Quality range: x > 0.8
- Structure: Gas phase with entrained liquid droplets
- Droplet size: 10-50 μm
- Very low liquid holdup

**Engineering Implications**:
- ⭐ High pressure drop due to wall friction
- ⭐ Possible compressor liquid slugging
- ⭐ Heat transfer dominated by forced convection

### Quality-Based Regime Transitions (การเปลี่ยนสภาพการไหลตามคุณสมบัติ)

#### Quality Definition (คำนวณคุณภาพ)

The vapor quality (x) is defined as:
$$x = \frac{h - h_l}{h_v - h_l}$$

where:
- h = mixture enthalpy [J/kg]
- $h_l$ = saturated liquid enthalpy [J/kg]
- $h_v$ = saturated vapor enthalpy [J/kg]

**R410A Thermophysical Properties**:

| Quality x | Temperature (°C) | Pressure (bar) | Density (kg/m³) | Heat Transfer (W/m²K) |
|-----------|------------------|---------------|-----------------|-----------------------|
| 0.0       | 5.0              | 17.9          | 1190            | 2000-5000             |
| 0.1       | 5.0              | 17.9          | 1100            | 4000-8000             |
| 0.2       | 5.0              | 17.9          | 1000            | 6000-12000            |
| 0.3       | 5.0              | 17.9          | 900             | 8000-15000            |
| 0.4       | 5.0              | 17.9          | 800             | 10000-18000           |
| 0.5       | 5.0              | 17.9          | 700             | 12000-20000           |

#### Transition Criteria (เกณฑ์การเปลี่ยนสภาพ)

**Bubbly → Slug Transition**:
- Critical void fraction: α_g = 0.25-0.30
- Flow velocity criterion: $U_{g} > 0.3 \sqrt{gD}$
- R410A adjustment: occurs at lower velocity due to lower density ratio

**Slug → Annular Transition**:
- Critical quality: x = 0.25-0.35
- Weber number: $We = \frac{\rho_g U^2 D}{\sigma} > 30$
- Tube diameter effect: smaller tubes shift transition to higher quality

**Annular → Mist Transition**:
- Critical quality: x = 0.75-0.90
- Film thickness criterion: δ/D < 0.05
- Weber number: $We > 200$

### Mass Flux Effects (ผลกระทบของอัตราการไหล)

#### Superficial Velocity Effects

```cpp
// Mass flux effects on flow transitions
volScalarField G = rho_mixture * U_magnitude;  // kg/m²s

if (G < 100) {
    // Low mass flux: buoyancy dominates
    transitionQualities.bubblyToSlug = 0.20;
    transitionQualities.slugToAnnular = 0.30;
} else if (G > 300) {
    // High mass flux: inertia dominates
    transitionQualities.bubblyToSlug = 0.25;
    transitionQualities.slugToAnnular = 0.35;
}
```

**Mass Flux Ranges for R410A**:

| Mass Flux (kg/m²s) | Flow Pattern | Typical Velocity (m/s) |
|-------------------|--------------|-------------------------|
| 50-150            | Stratified   | 0.1-0.3                 |
| 150-300           | Slug/Bubbly  | 0.3-0.8                 |
| 300-500           | Annular      | 0.8-1.5                 |
| 500-800           | Mist/Annular | 1.5-2.5                 |

### R410A-Specific Characteristics (ลักษณะเฉพาะของ R410A)

#### Density Ratio Effects (ผลกระทบของอัตราส่วนความหนาแน่น)

The density ratio $\rho_l/\rho_g$ significantly impacts flow patterns:

**For R410A at 5°C**:
- ρ_l = 1190 kg/m³
- ρ_g = 18.2 kg/m³
- Ratio = 65.4 (vs. 1000 for water/steam)

**Impact on Flow Maps**:
- Lower transition velocities compared to water
- More stable annular flow regime
- Reduced bubble coalescence rates

#### Surface Tension Influence (ผลกระทบของแรงตึงผิวน้ำ)

R410A surface tension characteristics:

```cpp
// Surface tension temperature dependence
surfaceTension = 0.0082 - 0.00012 * (T - 273); // 8.2 mN/m at 5°C

// Weber number calculation
We = rho_gas * U_squared * D / surfaceTension;
```

**Effects**:
- Smaller bubble departure diameters
- Earlier transition to annular flow
- Increased interfacial heat transfer coefficients

#### Refrigerant Oil Effects (ผลกระทบของน้ำมันหล่อลื่น)

POE (Polyol Ester) oil in R410A systems:

- **Typical oil concentration**: 1-5% by weight
- **Effect on surface tension**: Reduces by 10-20%
- **Effect on viscosity**: Increases liquid phase viscosity by 15-30%

**Flow Regime Modifications**:
- Oil promotes slug flow at lower qualities
- Reduces annular film stability
- Increases pressure drop by 5-15%

> **⭐ IMPLEMENTATION NOTE**: When modeling R410A evaporator flows in OpenFOAM:
> 1. Use the `reactingTwoPhaseEulerFoam` solver
> 2. Define R410A properties in `constant/thermophysicalProperties`
> 3. Implement quality-dependent heat transfer correlations
> 4. Include surface tension effects in interface model selection

---

## 🆚 Comparative Summary: Three Phenomena

| Aspect | Phase Change | Cavitation | Population Balance |
|--------|--------------|------------|-------------------|
| **Primary Driver** | Temperature difference | Pressure difference | Size-dependent processes |
| **Timescale** | Medium (seconds) | Very fast (ms) | Variable (slow-fast) |
| **Key Challenge** | Latent heat coupling | Pressure-velocity coupling | Computational cost |
| **Typical Solver** | `reactingTwoPhaseEulerFoam` | `interPhaseChangeFoam` | `multiphaseEulerFoam` + PBE |
| **Mesh Requirements** | Capture thermal gradients | Resolve pressure drops | Sufficient for turbulence |
| **Stability Issues** | Temperature spikes | Pressure oscillations | Moment divergence |
| **Industrial Applications** | Power gen, refrigeration, nuclear | Marine, pumps, turbines | Reactors, separations, sprays |

---

## 🛠️ Hands-on Tutorials (บทเรียนปฏิบัติ)

### Tutorial 1: Boiling in a Heated Channel (การเดือดในท่อสี่เหลี่ยม)

**Objective**: Simulate nucleate boiling in a 2D channel with bottom heating

#### WHAT you'll simulate
- Water flowing in a channel (velocity: 0.1 m/s)
- Bottom wall at $T_{wall} = 383$ K ($T_{sat} = 373$ K)
- Top wall at $T_{wall} = 300$ K
- Observe vapor bubble formation and growth

#### WHY this matters
- Demonstrates temperature-driven phase change
- Relevant to electronics cooling, reactor design
- Shows importance of wall superheat

#### HOW to implement

**Step 1: Geometry & Mesh**
```bash
# Create 2D channel (length: 0.1 m, height: 0.01 m)
blockMesh
```

**Step 2: Select Solver**
```bash
# Use reactingTwoPhaseEulerFoam for thermal phase change
solver: reactingTwoPhaseEulerFoam
```

**Step 3: Configure Phase Change Model**
```cpp
// constant/phaseProperties
phaseChangeModel thermalPhaseChange;

thermalPhaseChangeCoeffs
{
    hLv     2.26e6;      // Latent heat [J/kg]
    Tsat    373.15;      // Saturation temperature [K]
    r       100;         // Mass transfer coefficient [1/s]
}
```

**Step 4: Set Boundary Conditions**
```cpp
// 0/T
inlet
{
    type            fixedValue;
    value           uniform 300;  // K
}

bottomWall
{
    type            fixedValue;
    value           uniform 383;  // K (heated)
}

topWall
{
    type            fixedValue;
    value           uniform 300;  // K (cooled)
}
```

**Step 5: Run Simulation**
```bash
reactingTwoPhaseEulerFoam
```

**Step 6: Post-process**
```bash
paraFoam -builtin
# Visualize: alpha.vapor (vapor volume fraction), T (temperature)
```

**Expected Results**:
- Vapor bubbles form near heated wall where T > T_sat
- Bubbles grow and detach due to buoyancy
- Heat transfer enhancement visible in temperature field

---

### Tutorial 2: Cavitation on a Hydrofoil (การเกิดโพรงบนใบพัด)

**Objective**: Analyze cavitation patterns on a NACA hydrofoil

#### WHAT you'll simulate
- NACA 0012 hydrofoil at angle of attack = 8°
- Inlet velocity: 10 m/s
- Outlet pressure: 1 bar
- Observe vapor cavity on suction side

#### WHY this matters
- Critical for marine propeller design
- Demonstrates pressure-driven phase change
- Shows link between pressure distribution and cavitation

#### HOW to implement

**Step 1: Geometry**
```bash
# Use NACA 0012 airfoil profile
# Angle of attack: 8 degrees
```

**Step 2: Select Solver**
```bash
solver: interPhaseChangeFoam
```

**Step 3: Configure Cavitation Model**
```cpp
// constant/transportProperties
phases (water vapor);

phaseChangeModel SchnerrSauer;

SchnerrSauerCoeffs
{
    n       1e13;    // Nucleation site density [1/m³]
    dNuc    2e-6;    // Nucleation diameter [m]
    pSat    2300;    // Saturation pressure [Pa] at 20°C
    Cc      1;       // Condensation coefficient
    Cv      1;       // Vaporization coefficient
}
```

**Step 4: Set Boundary Conditions**
```cpp
// 0/p
inlet
{
    type            fixedValue;
    value           uniform 2e5;  // 2 bar
}

outlet
{
    type            fixedValue;
    value           uniform 1e5;  // 1 bar (pressure drop drives cavitation)
}

// 0/U
inlet
{
    type            fixedValue;
    value           uniform (10 0 0);  // m/s
}
```

**Step 5: Mesh Refinement**
```bash
# Refine near leading/trailing edges
# Capture pressure gradients
```

**Step 6: Post-process**
```bash
# Calculate cavitation number
# σ = (p - p_sat) / (0.5 * rho * U^2)
paraFoam -builtin
# Visualize: alpha.vapor, p field
```

**Expected Results**:
- Vapor cavity forms on suction side where p < p_sat
- Cavity collapses near trailing edge (pressure recovery)
- Cavitation number correlates with cavity size

---

### Tutorial 3: Bubble Column with Population Balance (หอถังหมักพร้อม PBE)

**Objective**: Simulate polydisperse bubbles in a bubble column

#### WHAT you'll simulate
- Cylindrical column (height: 1 m, diameter: 0.1 m)
- Air injected from bottom at 0.01 m/s
- Water as continuous phase
- Bubbles undergo breakup and coalescence

#### WHY this matters
- Relevant to chemical reactors, fermenters
- Shows importance of size distribution
- Demonstrates PBE vs monodisperse comparison

#### HOW to implement

**Step 1: Geometry**
```bash
# 2D axisymmetric column
# Height: 1 m, Diameter: 0.1 m
```

**Step 2: Select Solver**
```bash
solver: multiphaseEulerFoam
```

**Step 3: Configure Population Balance**
```cpp
// constant/phaseProperties
populationBalance on;

populationBalanceCoeffs
{
    continuousPhaseName water;
    dispersedPhase air;
    
    // QMOM settings
    nNodes  4;    // Number of quadrature nodes
    
    // Breakup kernel
    breakupModel Lehr;
    breakupCoeffs
    {
        // Lehr model parameters
    }
    
    // Coalescence kernel
    coalescenceModel constant;
    coalescenceCoeffs
    {
        // Constant coalescence rate
    }
}
```

**Step 4: Set Boundary Conditions**
```cpp
// 0/alpha.air
inlet
{
    type            fixedValue;
    value           uniform 0.2;  // Gas volume fraction
}

outlet
{
    type            pressureInletOutletVelocity;
    value           uniform 0;
}
```

**Step 5: Run Comparison**
```bash
# Run WITHOUT PBE (constant diameter)
multiphaseEulerFoam

# Run WITH PBE
multiphaseEulerFoam
```

**Step 6: Post-process**
```bash
# Plot: d32 (Sauter mean diameter) vs height
# Compare gas holdup with/without PBE
# Calculate interfacial area density
paraFoam -builtin
```

**Expected Results**:
- Without PBE: constant bubble diameter
- With PBE: bubbles break up near inlet (high turbulence)
- Larger bubbles at top due to coalescence
- Interfacial area significantly different from monodisperse case

---

## ⚠️ Common Pitfalls (ปัญหาที่พบบ่อยและวิธีแก้ไข)

### Phase Change Issues

| Symptom | Cause | Solution |
|---------|-------|----------|
| **Temperature spikes** (T → ∞) | Mass transfer rate too high, latent heat imbalance | Reduce relaxation factor `r`, check energy equation convergence |
| **No phase change observed** | Wall temperature too close to T_sat | Increase temperature difference, verify phase change model is active |
| **Divergence during startup** | Initial conditions far from equilibrium | Initialize with equilibrium state, use smaller Δt for first steps |

### Cavitation Issues

| Symptom | Cause | Solution |
|---------|-------|----------|
| **Pressure oscillations** | Co > 0.3, rapid phase change | Reduce maxCo to 0.2-0.3, increase nCorrectors |
| **Unphysical cavitation** (p > p_sat but bubbles exist) | pSat set incorrectly, wrong units | Verify pSat value (Pa, not bar!), check temperature |
| **No cavitation observed** | Pressure drop insufficient | Increase velocity, reduce outlet pressure, check mesh resolution |

### Population Balance Issues

| Symptom | Cause | Solution |
|---------|-------|----------|
| **Negative moments** (M_k < 0) | Numerical instability, large time steps | Reduce Δt, use under-relaxation for moments |
| **Zero size evolution** | Breakup/coalescence coefficients too small | Verify kernel parameters, check literature values |
| **Extremely slow convergence** | Too many size bins/nodes | Reduce nNodes, use QMOM instead of discrete method |

### General Multiphase Issues

| Symptom | Cause | Solution |
|---------|-------|----------|
| **Volume fraction bounds violated** (α < 0 or α > 1) | MULES compression issue, large Δt | Reduce maxAlphaCo, check divScheme for alpha |
| **Mass imbalance** (total mass not conserved) | Inconsistent mass transfer rates | Verify ṁ_evap = ṁ_cond at equilibrium, check phaseProperties |
| **Solver won't start** | Missing thermophysical properties | Ensure Cp, k, hLv are defined for ALL phases |

---

## 🧠 Concept Check: Self-Assessment

<details>
<summary><b>1. What is the FUNDAMENTAL DIFFERENCE between boiling and cavitation?</b></summary>

**Answer**:
- **Boiling** is **temperature-driven**: occurs when $T > T_{sat}$ at constant (or near-constant) pressure
- **Cavitation** is **pressure-driven**: occurs when $p < p_{sat}$ at constant (or near-constant) temperature

**Both** result in liquid → vapor phase change, but the **driving force** and **applications** differ significantly.

**Example scenarios**:
- Boiling: Water in a kettle heated to 100°C at 1 atm
- Cavitation: Water flowing through a pump inlet at 20°C, pressure drops to 2 kPa (below p_sat)
</details>

<details>
<summary><b>2. When should you use Population Balance modeling instead of assuming constant bubble diameter?</b></summary>

**Answer**: Use PBE when:
1. **Size distribution affects key outcomes** (interfacial area, mass transfer, reaction rates)
2. **Significant breakup/coalescence occurs** (high turbulence, long residence times)
3. **Wide size distribution exists** (span = (d90 - d10)/d50 > 2)
4. **Accuracy is critical** (design optimization, scale-up)

**Constant diameter is acceptable when**:
- Narrow size distribution (monodisperse systems)
- Short residence times (minimal breakup/coalescence)
- Qualitative results only (flow patterns, not mass transfer)

**Rule of thumb**: If bubble/droplet size changes by > 50% through the domain, use PBE.
</details>

<details>
<summary><b>3. Why does phase change modeling make CFD simulations much more challenging?</b></summary>

**Answer**: Phase change introduces **strong coupling** between multiple physical phenomena:

1. **Mass-Energy Coupling**: Latent heat ($h_{lv}$) links mass transfer to temperature field
   - Evaporation absorbs energy → cools liquid
   - Condensation releases energy → heats liquid
   - Temperature and phase fraction equations become tightly coupled

2. **Density Jumps**: Large density ratio (ρ_liquid/ρ_vapor ≈ 1000 for water/steam)
   - Rapid density changes cause pressure waves
   - Requires small time steps (CFL limit based on compressibility)

3. **Source Term Stiffness**: Mass transfer source terms ($\dot{m}'''$) can be very large
   - $\dot{m}'''$ can change rapidly near $T_{sat}$ or $p_{sat}$
   - Requires under-relaxation and careful time step selection

4. **Multiple Timescales**:
   - Fast: Phase change (milliseconds)
   - Slow: Fluid transport (seconds)
   - Stiff system of equations requiring implicit solvers

**Result**: More iterations, smaller time steps, higher computational cost.
</details>

<details>
<summary><b>4. In the Schnerr-Sauer cavitation model, what do the parameters `n`, `dNuc`, `pSat`, `Cc`, and `Cv` represent?</b></summary>

**Answer**:
- **n** (nucleation site density): Number of bubble nucleation sites per unit volume [1/m³]
  - Typical: 10¹² - 10¹⁴ 1/m³ for water
  - Higher value → more potential bubble formation sites

- **dNuc** (nucleation diameter): Initial size of nucleated bubbles [m]
  - Typical: 1-10 μm (1e-6 to 1e-5 m)
  - Affects initial mass transfer rate

- **pSat** (saturation pressure): Pressure at which phase change occurs [Pa]
  - Temperature-dependent (e.g., 2300 Pa for water at 20°C)
  - **CRITICAL**: Must be in correct units (Pa, NOT bar!)

- **Cc** (condensation coefficient): Scaling factor for vapor → liquid collapse
  - Typical: 0.01 - 1
  - Lower values → slower collapse (more stable)

- **Cv** (vaporization coefficient): Scaling factor for liquid → vapor growth
  - Typical: 1 - 1000
  - Higher values → faster bubble growth

**Tuning tips**:
- Start with Cc = Cv = 1 (default)
- If unstable, reduce Cc (slower collapse)
- If no cavitation observed, increase Cv or decrease pSat
</details>

<details>
<summary><b>5. What is the "coupled physics" challenge in complex multiphase flows?</b></summary>

**Answer**: In MODULE 04 (simple multiphase), we solved:
- Continuity equation for each phase
- Momentum equation for mixture

**In MODULE 06 (complex multiphase), we solve ADDITIONALLY**:
- Energy equation (temperature field)
- Species equations (mass fractions)
- Population balance (size moments)

**All these equations are COUPLED**:

```mermaid
graph TD
    A[Velocity U] -->|Advection| B[Pressure p]
    B -->|Buoyancy| A
    B -->|Phase change| C[Volume Fraction α]
    C -->|Density| B
    D[Temperature T] -->|Latent heat| C
    C -->|Mass transfer| D
    E[Bubble Size d] -->|Interfacial area| C
    C -->|Turbulence| E

    style A fill:#8f8
    style B fill:#ff8
    style C fill:#f88
    style D fill:#88f
    style E fill:#f8f
```

**Implications**:
1. **Cannot solve equations sequentially** — must iterate within each time step
2. **Convergence is harder** — more residuals to monitor
3. **Initial conditions matter** — start near equilibrium state
4. **Computational cost increases** — 3-10× slower than simple multiphase

**OpenFOAM response**: Use PIMPLE algorithm with increased `nCorrectors` (3-5 iterations).
</details>

---

## 📋 Key Takeaways (สรุปสิ่งสำคัญ)

### Core Concepts
1. **Complex multiphase flows involve coupled physics**: mass transfer, energy, and population balance equations
2. **Phase change driving forces differ**: Temperature-driven (boiling) vs pressure-driven (cavitation)
3. **Size distributions matter**: Real systems are polydisperse; PBE captures evolution
4. **Numerical stability is critical**: Strong coupling requires careful time step and solver settings

### Decision Framework

| Your Scenario | Use This Approach | Key Solver |
|---------------|-------------------|------------|
| Heat exchanger with boiling | Phase change modeling | `reactingTwoPhaseEulerFoam` |
| Pump/propeller at high speed | Cavitation modeling | `interPhaseChangeFoam` |
| Bubble column reactor | Population balance | `multiphaseEulerFoam` + PBE |
| Simple two-phase flow (no mass transfer) | MODULE 04 methods | `interFoam`, `twoPhaseEulerFoam` |

### Best Practices
- **Start simple**: Validate without phase change, then add complexity
- **Monitor all residuals**: p, U, T, alpha, and species
- **Use small time steps initially**: Co < 0.3 for phase change/cavitation
- **Check mass balance**: Total mass should be conserved (or follow known trend)
- **Verify physical parameters**: pSat, T_sat, h_Lv with literature

---

## 📖 Further Reading and Related Content

### Within This Module
- **[01_Phase_Change_Modeling.md](01_Phase_Change_Modeling.md)** — Detailed implementation of boiling/condensation models
- **[02_Cavitation_Modeling.md](02_Cavitation_Modeling.md)** — Complete cavitation model formulations and validation cases
- **[03_Population_Balance_Modeling.md](03_Population_Balance_Modeling.md)** — PBE theory, QMOM methods, and kernel selection

### Prerequisites
- **[MODULE 04: Multiphase Fundamentals](../../MODULE_04_MULTIPHASE_FUNDAMENTALS/CONTENT/00_Overview.md)** — VOF, Euler-Euler, interfacial forces

### Advanced Topics
- **[MODULE 06: Section 02 - Coupled Physics](../02_COUPLED_PHYSICS/00_Overview.md)** — Fluid-structure interaction, conjugate heat transfer
- **[MODULE 06: Section 03 - Reacting Flows](../03_REACTING_FLOWS/00_Overview.md)** — Chemical reactions with phase change

### External Resources
- **OpenFOAM Documentation**:
  - `interPhaseChangeFoam` solver guide
  - `reactingTwoPhaseEulerFoam` tutorial cases
- **Recommended Textbooks**:
  - Ishii & Hibiki (2011) — Thermo-Fluid Dynamics of Two-Phase Flow
  - Brennen (2013) — Cavitation and Bubble Dynamics
  - Ramkrishna (2000) — Population Balances: Theory and Applications

---

## ✅ Practice Exercises (แบบฝึกหัด)

### Exercise 1: Phase Change Model Selection
**Scenario**: You're designing a steam condenser for a power plant. Inlet is 90% steam at 400 K, outlet should be 100% liquid water at 350 K. Pressure is constant at 1 atm.

**Questions**:
1. Which phase change model should you use? (Lee, thermal, Hertz-Knudsen?)
2. What are the key parameters you need to set?
3. What boundary conditions do you need for temperature?

<details>
<summary>Click for solution</summary>

**Solution**:
1. Use **thermal phase change model** (temperature-driven, condensation)
2. Key parameters:
   - `Tsat = 373.15 K` (at 1 atm)
   - `hLv = 2.26e6 J/kg` (latent heat)
   - `r = 100-1000 1/s` (mass transfer coefficient)
3. Boundary conditions:
   - Inlet: `alpha.water = 0.1`, `T = 400 K`
   - Walls: `T = 300 K` (cooled)
   - Outlet: `zeroGradient` for alpha and T
</details>

---

### Exercise 2: Cavitation Number Calculation
**Scenario**: A pump operates with inlet velocity 15 m/s, inlet pressure 50 kPa. Water is at 20°C (p_sat = 2.3 kPa). Calculate the cavitation number.

**Questions**:
1. What is the cavitation number formula?
2. Is the pump likely to experience cavitation?
3. What design change would reduce cavitation risk?

<details>
<summary>Click for solution</summary>

**Solution**:
1. Cavitation number: $\sigma = \frac{p - p_{sat}}{0.5 \rho U^2}$
   - $p = 50,000$ Pa
   - $p_{sat} = 2,300$ Pa
   - $\rho = 1000$ kg/m³
   - $U = 15$ m/s
   - $\sigma = \frac{50000 - 2300}{0.5 \times 1000 \times 15^2} = \frac{47700}{112500} = 0.42$

2. **Yes, cavitation is likely** (typically $\sigma < 1$ indicates cavitation risk)

3. **To reduce risk**:
   - Increase inlet pressure (e.g., install booster pump)
   - Reduce inlet velocity (larger impeller inlet)
   - Lower fluid temperature (reduces p_sat)
</details>

---

### Exercise 3: Population Balance Necessity
**Scenario**: You're simulating a bubble column with:
- Inlet bubble diameter: 5 mm (monodisperse)
- Column height: 2 m
- Superficial gas velocity: 0.02 m/s
- Liquid: water (ρ = 1000 kg/m³)

**Questions**:
1. Under what conditions would you NEED population balance modeling?
2. If you observe bubble diameters from 2 mm to 15 mm throughout the column, does constant-diameter assumption work?
3. How would you verify if PBE is necessary?

<details>
<summary>Click for solution</summary>

**Solution**:
1. **Need PBE when**:
   - Significant breakup occurs (high turbulence, high shear)
   - Significant coalescence occurs (high gas holdup, long residence time)
   - Interfacial area affects mass transfer/reaction rates

2. **No, constant diameter will NOT work**:
   - Size range (2-15 mm) shows significant evolution
   - Span = (15 - 2)/5 = 2.6 > 2 (wide distribution)
   - Interfacial area will be WRONG with constant d

3. **Verification approach**:
   - Run with PBE and plot d32 vs height
   - If d32 changes by > 20%, PBE is necessary
   - Compare mass transfer rates with/without PBE
   - If mass transfer is a key output, use PBE

**Rule**: If in doubt, try PBE and compare with monodisperse case. If results differ significantly (> 10%), use PBE.
</details>

---

**Ready to dive into the first topic?** Continue to [01_Phase_Change_Modeling.md](01_Phase_Change_Modeling.md)