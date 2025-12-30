# Cavitation Modeling (การจำลอง Cavitation)

> **Cavitation** = Phase change from liquid to vapor when local pressure drops below saturation pressure

<!-- IMAGE: IMG_06_004 -->
<!--
Purpose: เพื่ออธิบายกลไกการเกิด Cavitation ที่ใบพัดหรือ Hydrofoil. ภาพนี้ต้องเชื่อมโยง "กราฟความดัน" ($C_p$) กับ "ตำแหน่งที่เกิดฟอง" (Vapor Region). จุดสำคัญคือ: ฟองจะเกิดเมื่อกราฟความดันจุ่มลงต่ำกว่าเส้น $P_{sat}$ (Saturation Pressure)
Prompt: "Physics Diagram of Hydrofoil Cavitation. **Scene:** A Hydrofoil cross-section in blue water flow. **Overlay Graphs:** 1. **Pressure Coefficient ($C_p$) Curve:** Plotted along the foil chord. The curve dips deeply on the upper surface (Suction side). 2. **Saturation Line ($P_{sat}$):** A horizontal dashed line intersecting the pressure curve. **Vapor Zone:** Calculate the area where Pressure Curve < Saturation Line $\rightarrow$ Highlight this region on the foil surface as 'Vapor/White Bubble Cloud'. **Collapse:** Show bubbles collapsing at the trailing edge where pressure recovers. STYLE: Mixed-media (Engineering Chart + Physical Flow), clear threshold indicators."
-->
![[IMG_06_004.jpg]]

---

## Learning Objectives

After completing this module, you will be able to:

1. **Explain** the physics of cavitation and its engineering significance
2. **Select** appropriate cavitation models for different applications
3. **Configure** thermophysical properties and boundary conditions for cavitation simulations
4. **Implement** stable numerical schemes for phase-change problems
5. **Diagnose** and troubleshoot common cavitation simulation issues
6. **Set up** a complete cavitation case following best practices

---

## Prerequisites

Before studying this module, you should have:

- **Understanding** of VOF (Volume of Fluid) method from `02_INTERPHASE_FORCES/01_DRAG_LIFT_VIRTUAL_MASS`
- **Knowledge** of multiphase transport properties from `01_PHASE_COMPRESSION_EXPANSION`
- **Familiarity** with pressure-velocity coupling algorithms from `MODULE_03/02_PRESSURE_VELOCITY_COUPLING`
- **Experience** with basic OpenFOAM case structure and boundary conditions
- **Understanding** of multiphase turbulence modeling from `05_TURBULENCE_IN_MULTIPHASE_FLOWS`

---

## 1. WHAT: Cavitation Physics and Terminology

### 1.1 Definition

Cavitation is a **phase-change phenomenon** where liquid transforms to vapor when local pressure falls below saturation pressure:

```
p < pSat → liquid → vapor (evaporation/nucleation)
p > pSat → vapor → liquid (condensation/collapse)
```

### 1.2 Cavitation Lifecycle

```
Nucleation → Growth → Transport → Collapse
```

**Stage 1: Nucleation** (การเกิดฟองเริ่มแรก)
- Trigger: Local pressure < saturation pressure
- Location: Low-pressure regions (suction side of hydrofoils, pump impellers)
- Timescale: Microseconds

**Stage 2: Growth** (การเติบโตของฟอง)
- Vapor volume expands rapidly
- Bubble radius increases following Rayleigh-Plesset dynamics
- Driven by pressure difference: $\Delta p = p_{sat} - p$

**Stage 3: Transport** (การเคลื่อนที่)
- Bubbles advect with flow velocity
- Move from low-pressure to high-pressure regions

**Stage 4: Collapse** (การยุบตัว)
- Trigger: Local pressure > saturation pressure
- Result: Shock wave formation, microjet formation
- Damage potential: Extremely high localized pressures (> 1 GPa)

### 1.3 Cavitation Types

| Type | Characteristics | Typical Locations |
|------|-----------------|-------------------|
| **Attached Cavitation** | Stable vapor sheet attached to surface | Hydrofoil suction side, propeller blades |
| **Cloud Cavitation** | Unsteady bubble clouds shedding periodically | Highly loaded foils, pump impellers |
| **Vortex Cavitation** | Cavitation in vortex cores | Tip vortices, hub vortices |
| **Traveling Cavitation** | Individual bubbles moving with flow | Injector nozzles, valves |

---

## 2. WHY: Engineering Significance and Model Selection

### 2.1 Engineering Consequences

| Consequence | Physical Mechanism | Impact |
|-------------|-------------------|--------|
| **Erosion Damage** | Shock waves from asymmetric bubble collapse near walls | Pitting, material loss, reduced component life |
| **Noise** | Implosive collapse generates acoustic waves | Marine vessel signature, comfort issues |
| **Performance Loss** | Vapor cavities modify flow geometry | Reduced head/efficiency in pumps, thrust loss in propellers |
| **Vibration** | Unsteady cavity dynamics | Structural fatigue, bearing damage |

**WHY It Matters:**
- **Marine Industry**: Cavitation can destroy propeller blades in months; erosion repair costs millions annually
- **Hydropower**: Turbine runners suffer erosion, requiring frequent maintenance downtime
- **Pumps**: Cavitation reduces efficiency by 10-30% and causes premature failure in critical systems
- **Injectors**: Cavitation affects fuel atomization quality, impacting combustion efficiency
- **Medical Devices**: Cavitation in ultrasound imaging and lithotripsy requires precise control

**Economic Impact:**
- Marine propeller replacement: $500K - $2M per vessel
- Pump downtime in industry: $10K - $100K per hour
- Hydropower turbine maintenance: $1M - $5M per overhaul

**Design Decision Implications:**
- Cavitation prediction determines safe operating envelopes
- Influences blade geometry, inlet design, and operating conditions
- Drives material selection (e.g., stainless steel vs. bronze vs. coatings)
- Affects maintenance scheduling and component lifecycle planning

### 2.2 Cavitation Model Selection Guide

#### 2.2.1 Decision Criteria

Select cavitation models based on:

1. **Application Type**
   - **Steady-state performance**: SchnerrSauer, Merkle
   - **Transient dynamics**: Kunz, Zwart
   - **High-speed flows**: Kunz (more robust)
   - **Validation studies**: SchnerrSauer (most documented)

2. **Physical Considerations**
   - **Bubble density known**: SchnerrSauer (explicit bubble dynamics)
   - **Characteristic time known**: Kunz, Merkle (time-based formulations)
   - **Industrial applications**: Zwart (optimized for pumps)
   - **Marine applications**: Kunz (proven stability)

3. **Numerical Stability**
   - **Convergence difficulties**: Kunz (most stable, asymmetric coefficients)
   - **Balanced accuracy/stability**: SchnerrSauer, Zwart
   - **High fidelity**: Merkle (less stable but accurate)
   - **Violent cavitation**: Kunz (prevents divergence)

4. **Computational Resources**
   - **Limited resources**: SchnerrSauer (fastest convergence)
   - **High-fidelity requirements**: Merkle (more iterations needed)
   - **Large-scale simulations**: Kunz (stable under relaxed settings)

#### 2.2.2 Model Comparison Matrix

| Model | Accuracy | Stability | Computational Cost | Best Applications | Key Parameter | Strengths | Limitations |
|-------|----------|-----------|-------------------|-------------------|---------------|-----------|-------------|
| **SchnerrSauer** | High | High | Low-Medium | General purpose, marine propellers, validation | Nuclei density `n` | - Widely validated<br>- Explicit physics<br>- Good documentation | - Less stable for violent collapse |
| **Kunz** | Medium | Very High | Medium | Marine propellers, high-speed flows, transient | Vaporization coeff `Cv` | - Most stable<br>- Asymmetric coefficients<br>- Marine industry proven | - Lower physical accuracy<br>- Empirical tuning required |
| **Merkle** | High | Medium | Low-Medium | Industrial pumps, inducers, research | Freestream velocity `UInf` | - Good accuracy<br>- Popular in turbomachinery<br>- Well-documented | - Stability issues<br>- Sensitive to parameters |
| **Zwart** | High | High | Medium | Pumps, inducers, automotive, aerospace | Nucleation site density | - Optimized for pumps<br>- Good cavity prediction<br>- Industrial adoption | - Less flexible for other applications |

#### 2.2.3 Decision Tree

```
Need high numerical stability?
├── Yes → Kunz model (marine propellers, high-speed flows)
└── No → Need high physical accuracy?
    ├── Yes → Is bubble density known?
    │   ├── Yes → SchnerrSauer (validation studies)
    │   └── No → Merkle (pumps, inducers)
    └── No → SchnerrSauer (default choice for general applications)
```

**Quick Selection Guide:**

| Scenario | Recommended Model | Rationale |
|----------|-------------------|-----------|
| Marine propeller (noise prediction) | Kunz | Stability for transient dynamics |
| Centrifugal pump (performance) | Zwart | Pump-optimized formulation |
| Fuel injector (violent cavitation) | Kunz | Prevents divergence |
| Research validation | SchnerrSauer | Extensive documentation |
| Turbine runner (erosion prediction) | Merkle | Accurate collapse dynamics |
| General-purpose simulation | SchnerrSauer | Best balance of features |

---

## 3. HOW: Cavitation Model Implementation

### 3.1 Solver Selection

```bash
# Primary cavitation solver (recommended)
interPhaseChangeFoam
# - VOF-based
# - Built-in cavitation models
# - Compressible (important for collapse)
# - Handles large density ratios

# Alternative: Multiphase Eulerian
multiphaseEulerFoam
# - Euler-Euler framework
# - More complex, less common for cavitation
# - Useful for bubble swarms

# For reacting flows with cavitation
reactingTwoPhaseEulerFoam
# - Includes heat transfer
# - Chemical reactions
# - Fuel injector applications
```

**WHY `interPhaseChangeFoam`:**
- Explicitly designed for phase-change problems
- Includes all major cavitation models (SchnerrSauer, Kunz, Merkle, Zwart)
- Handles large density ratios (ρ_water/ρ_vapor ≈ 43,000)
- Compressible formulation captures shock waves during collapse
- MULES algorithm ensures bounded alpha field (0 ≤ α ≤ 1)
- Industry-standard solver for cavitation applications

### 3.2 Model 1: SchnerrSauer (General Purpose)

**Physical Basis:** Bubble population dynamics based on nucleation site density

**Configuration:**
```cpp
// constant/phaseProperties
phaseChangeModel SchnerrSauer;

SchnerrSauerCoeffs
{
    n       1.6e13;  // Nucleation site density [1/m³]
    dNuc    2e-6;    // Nucleation diameter [m]
    Cc      1;       // Condensation coefficient
    Cv      1;       // Vaporization coefficient
}
```

**Mass Transfer Rate:**

$$\Gamma = \frac{\rho_v \rho_l}{\rho} \cdot \frac{3 \alpha (1-\alpha)}{R} \sqrt{\frac{2}{3} \frac{|p - p_{sat}|}{\rho_l}} \cdot \text{sign}(p_{sat} - p)$$

Where bubble radius:
$$R = \left(\frac{3\alpha}{4\pi n}\right)^{1/3}$$

**Parameter Tuning Guidelines:**

| Parameter | Typical Range | Physical Meaning | Effect |
|-----------|---------------|------------------|--------|
| `n` | 1e10 - 1e15 [1/m³] | Nucleation site density | Higher → more nucleation sites → larger cavity |
| `dNuc` | 1e-7 - 1e-5 [m] | Initial bubble diameter | Minor effect on final cavity size |
| `Cc` | 0.01 - 1 | Condensation rate multiplier | Lower → slower collapse (more stable) |
| `Cv` | 1 - 100 | Vaporization rate multiplier | Higher → faster growth |

**WHY Use SchnerrSauer:**
- Most widely validated model in literature
- Good balance of accuracy and stability
- Explicit physical parameters (bubble size, density)
- Default choice for most applications
- Extensive documentation and case studies

**Recommended For:**
- Hydrofoil validation studies
- Marine propeller performance prediction
- General cavitation applications
- Cases where bubble dynamics are important

### 3.3 Model 2: Kunz (High Stability)

**Physical Basis:** Empirical rate equation with different timescales for evaporation and condensation

**Configuration:**
```cpp
phaseChangeModel Kunz;

KunzCoeffs
{
    UInf    10;      // Freestream velocity [m/s]
    tInf    0.01;    // Characteristic time [s]
    Cc      0.01;    // Condensation coefficient
    Cv      1000;    // Vaporization coefficient (large for rapid evaporation)
}
```

**Mass Transfer Rate:**

$$\dot{m} = \begin{cases}
C_v \frac{\rho_v \rho_l}{\rho} \frac{(1-\alpha)}{t_{\infty}} & \text{if } p < p_{sat} \\
C_c \frac{\rho_v \rho_l}{\rho} \frac{\alpha}{t_{\infty}} & \text{if } p > p_{sat}
\end{cases}$$

**Parameter Tuning Guidelines:**

| Parameter | Typical Range | Physical Meaning | Effect |
|-----------|---------------|------------------|--------|
| `UInf` | 1 - 50 [m/s] | Characteristic velocity | Scales time constants |
| `tInf` | 0.001 - 0.1 [s] | Characteristic time | Lower → faster phase change |
| `Cc` | 0.001 - 0.1 | Condensation rate | Very low → prevents violent collapse |
| `Cv` | 100 - 10000 | Vaporization rate | High → rapid evaporation |

**WHY Use Kunz:**
- **Asymmetric coefficients** (`Cv >> Cc`): Rapid evaporation, slow condensation
- Prevents "violent" collapse that causes divergence
- Excellent for marine propeller simulations
- Most stable model for transient simulations
- Handles aggressive pressure gradients

**Recommended For:**
- Marine propellers (noise and vibration prediction)
- High-speed flows with violent cavitation
- Cases with stability issues using other models
- Transient simulations with large pressure fluctuations

### 3.4 Model 3: Merkle (Industrial Applications)

**Physical Basis:** Similar to Kunz but with different coefficient scaling and velocity dependence

**Configuration:**
```cpp
phaseChangeModel Merkle;

MerkleCoeffs
{
    UInf    10;      // Freestream velocity [m/s]
    tInf    0.01;    // Characteristic time [s]
    Cc      0.01;    // Condensation coefficient
    Cv      100;     // Vaporization coefficient (lower than Kunz)
}
```

**Mass Transfer Rate:**

$$\dot{m} = \begin{cases}
\frac{C_v}{t_{\infty}} \frac{\rho_v \rho_l}{\rho} \sqrt{\frac{2}{3} \frac{p_{sat} - p}{\rho_l}} & \text{if } p < p_{sat} \\
\frac{C_c}{t_{\infty}} \frac{\rho_v \rho_l}{\rho} \sqrt{\frac{2}{3} \frac{p - p_{sat}}{\rho_l}} & \text{if } p > p_{sat}
\end{cases}$$

**Parameter Tuning Guidelines:**

| Parameter | Typical Range | Physical Meaning | Effect |
|-----------|---------------|------------------|--------|
| `UInf` | 1 - 50 [m/s] | Freestream velocity | Scales cavitation intensity |
| `tInf` | 0.001 - 0.05 [s] | Characteristic time | Lower → faster phase change |
| `Cc` | 0.01 - 0.1 | Condensation rate | Controls collapse dynamics |
| `Cv` | 50 - 200 | Vaporization rate | Controls growth rate |

**WHY Use Merkle:**
- Widely used in pump and inducer simulations
- Better prediction of cavity length compared to Kunz
- Moderate stability (better than SchnerrSauer in some cases)
- Industry-standard for turbomachinery
- Good balance of accuracy and stability

**Recommended For:**
- Centrifugal pumps
- Turbine runners
- Inducers and turbopumps
- Industrial turbomachinery

### 3.5 Model 4: Zwart (Pumps and Inducers)

**Physical Basis:** Similar to SchnerrSauer but with different nucleation model and coefficient formulation

**Configuration:**
```cpp
phaseChangeModel Zwart;

ZwartCoeffs
{
    n       1e13;    // Nucleation site density [1/m³]
    dNuc    2e-6;    // Nucleation diameter [m]
    Cc      0.01;    // Condensation coefficient
    Cv      50;      // Vaporization coefficient
}
```

**Mass Transfer Rate:**

$$\dot{m} = \begin{cases}
C_v \frac{3 \alpha (1-\alpha) \rho_v}{R} \sqrt{\frac{2}{3} \frac{p_{sat} - p}{\rho_l}} & \text{if } p < p_{sat} \\
-C_c \frac{3 \alpha^2 \rho_v}{R} \sqrt{\frac{2}{3} \frac{p - p_{sat}}{\rho_l}} & \text{if } p > p_{sat}
\end{cases}$$

**Parameter Tuning Guidelines:**

| Parameter | Typical Range | Physical Meaning | Effect |
|-----------|---------------|------------------|--------|
| `n` | 1e10 - 1e15 [1/m³] | Nucleation site density | Affects cavity initiation |
| `dNuc` | 1e-7 - 1e-5 [m] | Initial bubble diameter | Minor effect on cavity size |
| `Cc` | 0.001 - 0.1 | Condensation rate | Lower → more stable |
| `Cv` | 10 - 100 | Vaporization rate | Higher → larger cavity |

**WHY Use Zwart:**
- Optimized for pump geometries
- Good prediction of cavity extent
- Popular in automotive and aerospace industries
- Better cavity length prediction than SchnerrSauer for some cases
- Industry-validated for fuel systems

**Recommended For:**
- Automotive fuel pumps
- Aerospace inducers
- Injector nozzles
- Pump performance optimization

---

## 4. HOW: Thermophysical Properties Setup

### 4.1 Property Configuration

```cpp
// constant/transportProperties
phases (water vapor);

water
{
    transportModel  Newtonian;
    nu              1e-6;    // Kinematic viscosity [m²/s]
    rho             1000;    // Density [kg/m³]
    // Optional: Cp for thermal cavitation
    // Cp              4181;    // Specific heat [J/kg/K]
    // Pr              7.0;     // Prandtl number
}

vapor
{
    transportModel  Newtonian;
    nu              4.273e-4;  // Kinematic viscosity [m²/s]
    rho             0.023;     // Density [kg/m³] at 20°C
    // Cp              1900;     // Specific heat [J/kg/K]
    // Pr              0.95;     // Prandtl number
}

// Saturation pressure (CRITICAL: Must match operating temperature)
pSat    2300;  // [Pa] for water at 20°C
```

**Parameter Significance:**

| Parameter | Liquid | Vapor | Ratio | Impact |
|-----------|--------|-------|-------|--------|
| **Density (ρ)** | 1000 kg/m³ | 0.023 kg/m³ | 43,000:1 | Large ratio → numerical stiffness |
| **Viscosity (ν)** | 1e-6 m²/s | 4.27e-4 m²/s | 1:427 | Vapor viscosity higher due to low density |
| **pSat** | 2300 Pa (20°C) | - | - | Controls cavity onset |

**WHY These Properties Matter:**
- **Large density ratio**: Requires special numerics (compressible formulation)
- **pSat**: **Most critical parameter** - Small errors cause large prediction errors
- **Viscosity**: Affects boundary layer and pressure distribution
- **Temperature dependence**: pSat varies exponentially with temperature

### 4.2 Saturation Pressure Reference (Water)

| Temperature | pSat (Pa) | pSat (bar) | Application |
|-------------|-----------|------------|-------------|
| 5°C | 872 | 0.009 | Cold water systems |
| 10°C | 1,228 | 0.012 | Cold climate marine |
| 15°C | 1,705 | 0.017 | Cooling water |
| 20°C | 2,339 | 0.023 | Room temperature (standard) |
| 25°C | 3,169 | 0.032 | Standard lab conditions |
| 30°C | 4,246 | 0.042 | Warm water |
| 40°C | 7,381 | 0.074 | Hot water systems |
| 50°C | 12,349 | 0.123 | Warm industrial |
| 60°C | 19,940 | 0.199 | Hot industrial |
| 75°C | 38,598 | 0.386 | Near boiling |
| 90°C | 70,140 | 0.701 | Very hot water |
| 100°C | 101,325 | 1.013 | Boiling point |

**Temperature Correction Formula:**
For small temperature ranges (±10°C), use linear approximation:
$$p_{sat}(T) \approx p_{sat}(T_0) \cdot \exp\left[\frac{L}{R_{gas}}\left(\frac{1}{T_0} - \frac{1}{T}\right)\right]$$

**WHY Temperature Matters:**
- pSat varies exponentially with temperature (Clausius-Clapeyron relation)
- **5°C error → ~30% error in pSat → dramatically different cavity size**
- **10°C error → ~70% error in pSat → completely wrong prediction**
- Always verify temperature in experiments/operating conditions
- For high-accuracy work, use temperature-dependent pSat

### 4.3 Temperature-Dependent Saturation Pressure

For cases with significant temperature variations:

```cpp
// constant/thermophysicalProperties (for thermal cavitation)
thermoType
{
    type            heRhoThermo;
    mixture         multiComponentMixture;
    transport       sutherland;
    thermo          janaf;
    energy          sensibleEnthalpy;
    equationOfState perfectGas;
    specie          specie;
}

// Or use tabulated pSat
functions
{
    pSatTable
    {
        type            table;
        values          
        (
            (280  991)    // 7°C
            (290  1919)   // 17°C
            (293  2339)   // 20°C
            (300  3536)   // 27°C
            (310  6228)   // 37°C
        );
        default         2339;
        outOfBounds     clamp;
    }
}
```

---

## 5. HOW: Mathematical Formulation

### 5.1 VOF Equation with Phase Change

**Volume Fraction Transport:**

$$\frac{\partial \alpha}{\partial t} + \nabla \cdot (\mathbf{U} \alpha) = \frac{\dot{m}}{\rho}$$

**Where:**
- $\alpha$: Vapor volume fraction (0 = liquid, 1 = vapor)
- $\mathbf{U}$: Velocity field
- $\dot{m}$: Mass transfer rate [kg/m³/s] (positive for evaporation, negative for condensation)
- $\rho$: Mixture density = $\alpha \rho_v + (1-\alpha) \rho_l$

### 5.2 Mass Transfer Rate (General Form)

$$\dot{m} = \begin{cases}
\dot{m}_e & \text{if } p < p_{sat} \text{ (evaporation)} \\
-\dot{m}_c & \text{if } p > p_{sat} \text{ (condensation)}
\end{cases}$$

**General Formulation:**

$$\dot{m} = C \cdot \frac{\rho_v \rho_l}{\rho} \cdot f(\alpha) \cdot \sqrt{\frac{2}{3} \frac{|p - p_{sat}|}{\rho_l}} \cdot \text{sign}(p_{sat} - p)$$

**Where:**
- $C$: Model coefficient (C_v or C_c)
- $f(\alpha)$: Volume fraction function (model-dependent)
- Sign function ensures phase change in correct direction

### 5.3 Model-Specific Formulations

**SchnerrSauer:**
$$f(\alpha) = \frac{3 \alpha (1-\alpha)}{R}, \quad R = \left(\frac{3\alpha}{4\pi n}\right)^{1/3}$$

**Kunz:**
$$f(\alpha) = \begin{cases}
\frac{1-\alpha}{t_{\infty}} & \text{(evaporation)} \\
\frac{\alpha}{t_{\infty}} & \text{(condensation)}
\end{cases}$$

**Merkle:**
$$f(\alpha) = \frac{1}{t_{\infty}}$$

**Zwart:**
$$f(\alpha) = \begin{cases}
\frac{3 \alpha (1-\alpha)}{R} & \text{(evaporation)} \\
\frac{3 \alpha^2}{R} & \text{(condensation)}
\end{cases}$$

### 5.4 Mixture Properties

**Density:**
$$\rho = \alpha \rho_v + (1-\alpha) \rho_l$$

**Viscosity:**
$$\mu = \alpha \mu_v + (1-\alpha) \mu_l$$

**Velocity:**
$$\mathbf{U} = \frac{\alpha \rho_v \mathbf{U}_v + (1-\alpha) \rho_l \mathbf{U}_l}{\rho}$$

**WHY Mixture Formulation:**
- Single-field formulation avoids solving separate momentum equations
- MULES algorithm ensures bounded alpha (0 ≤ α ≤ 1)
- Large density ratios handled through compressible formulation

---

## 6. HOW: Practical Workflow - Step-by-Step Setup

### Step 1: Case Directory Structure

```bash
cavitationCase/
├── 0/                          # Initial fields
│   ├── p                       # Pressure field
│   ├── U                       # Velocity field
│   ├── alpha.water             # Volume fraction (liquid)
│   ├── k                       # Turbulence kinetic energy
│   ├── omega                   # Specific dissipation rate (SST k-ω)
│   └── nut                     # Turbulent viscosity
├── constant/
│   ├── transportProperties     # Phase properties
│   ├── phaseProperties         # Cavitation model
│   ├── turbulenceProperties    # Turbulence model
│   └── polyMesh/               # Mesh files
└── system/
    ├── controlDict             # Time control
    ├── fvSchemes               # Discretization schemes
    └── fvSolution              # Linear solvers
```

**Initialization Commands:**

```bash
# Create case skeleton
cp -r $FOAM_TUTORIALS/multiphase/interPhaseChangeFoam/cavitation/ .
cd cavitation

# Or create from template
mkdir -p 0 constant/polyMesh system
```

### Step 2: Boundary Conditions

**Pressure (p):**

```cpp
// 0/p
dimensions      [1 -1 -2 0 0 0 0];

internalField   uniform 1e5;  // 1 bar reference

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 2e5;  // High pressure drives flow (2 bar)
    }

    outlet
    {
        type            fixedValue;
        value           uniform 1e5;  // Lower pressure → cavitation (1 bar)
    }

    walls
    {
        type            zeroGradient;  // Allow pressure to evolve
    }
    
    // For rotating machinery (optional)
    rotor
    {
        type            zeroGradient;
    }
}
```

**Velocity (U):**

```cpp
// 0/U
dimensions      [0 1 -1 0 0 0 0];

internalField   uniform (10 0 0);  // 10 m/s freestream

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform (10 0 0);
    }

    outlet
    {
        type            zeroGradient;  // Allow outflow
    }

    walls
    {
        type            noSlip;        // Solid boundary
    }
    
    // For symmetric geometries (optional)
    symmetry
    {
        type            symmetry;
    }
}
```

**Volume Fraction (alpha.water):**

```cpp
// 0/alpha.water (Note: OpenFOAM uses liquid phase as alpha.water)
dimensions      [0 0 0 0 0 0 0];

internalField   uniform 1;  // 1 = pure liquid, 0 = pure vapor

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 1;    // Liquid inlet
    }

    outlet
    {
        type            zeroGradient;  // Allow free outflow
    }

    walls
    {
        type            zeroGradient;  // No flux through walls
    }
}
```

**Turbulence (k and omega for SST k-ω):**

```cpp
// 0/k
dimensions      [0 2 -2 0 0 0 0];

internalField   uniform 0.05;  // Low turbulence intensity

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 0.05;
    }

    outlet
    {
        type            zeroGradient;
    }

    walls
    {
        type            kqRWallFunction;
        value           uniform 0;
    }
}

// 0/omega
dimensions      [0 0 -1 0 0 0 0];

internalField   uniform 100;  // Specific dissipation rate

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 100;
    }

    outlet
    {
        type            zeroGradient;
    }

    walls
    {
        type            omegaWallFunction;
        value           uniform 100;
    }
}
```

### Step 3: Numerical Schemes

```cpp
// system/fvSchemes
ddtSchemes
{
    default         Euler;  // First-order (stable for startup)
    // Use backward for second-order accuracy (more expensive)
    // Use CrankNicolson for second-order temporal accuracy
}

gradSchemes
{
    default         Gauss linear;
    // For better accuracy on distorted meshes:
    // grad(p)       Gauss linear;
    // grad(U)       Gauss linear;
}

divSchemes
{
    div(rhoPhi,U)       Gauss linearUpwind grad(U);  // Bounded, stable
    div(phi,alpha)      Gauss vanLeer;               // NVD/TVD scheme (CRITICAL)
    div(phi,alpha.water)Gauss vanLeer;               // Ensure boundedness
    div(rhoPhi,k)       Gauss linearUpwind grad(k);
    div(rhoPhi,omega)   Gauss linearUpwind grad(omega);
    div(((rho*nuEff)*dev2(T(grad(U))))) Gauss linear;
    
    // For higher accuracy (less stable):
    // div(rhoPhi,U)   Gauss limitedLinearV 1;
    // div(phi,alpha)  Gauss MUSCL;  // Second-order
}

laplacianSchemes
{
    default         Gauss linear corrected;  // Non-orthogonal correction
    // For highly non-orthogonal meshes:
    // laplacian(nuEff,U) Gauss linear limited 0.5;
}

interpolationSchemes
{
    default         linear;
}

snGradSchemes
{
    default         corrected;
}
```

**WHY These Schemes:**
- `vanLeer` for alpha: Bounded (0 ≤ α ≤ 1), prevents overshoots, TVD scheme
- `linearUpwind` for U: Stable for high-speed flows, prevents oscillations
- `corrected` laplacian: Handles non-orthogonal meshes up to 70°
- `Euler` ddt: Most stable for initial transients

### Step 4: Solver Settings

```cpp
// system/fvSolution
PIMPLE
{
    nCorrectors      3;        // Pressure correction iterations
    nNonOrthogonalCorrectors 0;  // Increase for non-orthogonal meshes
    nAlphaCorr       1;        // Volume fraction corrections
    nAlphaSubCycles  2;        // Sub-cycle alpha for stability
    pRefPoint        (0 0 0);  // Reference point for pressure
    pRefValue        1e5;      // Reference pressure [Pa]
    
    // For better convergence:
    // nCorrectors    5;
    // nAlphaSubCycles 4;
}

solvers
{
    p
    {
        solver          GAMG;
        tolerance       1e-7;
        relTol          0.01;
        smoother        GaussSeidel;
        
        // For difficult cases:
        // solver          PBiCGStab;
        // preconditioner  DILU;
    }

    pFinal
    {
        solver          GAMG;
        tolerance       1e-7;
        relTol          0;      // Drive to tight tolerance in final iteration
    }

    U
    {
        solver          smoothSolver;
        smoother        GaussSeidel;
        tolerance       1e-6;
        relTol          0.1;
    }

    "(k|omega)"
    {
        solver          smoothSolver;
        smoother        GaussSeidel;
        tolerance       1e-6;
        relTol          0.1;
    }

    alpha.water
    {
        solver          smoothSolver;
        smoother        GaussSeidel;
        tolerance       1e-6;
        relTol          0;      // Tight tolerance for boundedness
        
        // MULES limiters (automatic in interPhaseChangeFoam):
        // nAlphaSubCycles 2;
        // alphaBCs       no;
    }
}

relaxationFactors
{
    fields
    {
        p               0.3;    // Pressure relaxation for stability
        rho             0.05;   // Density relaxation
    }
    equations
    {
        U               0.7;    // Momentum relaxation
    }
}
```

### Step 5: Time Control

```cpp
// system/controlDict
application     interPhaseChangeFoam;

startFrom       startTime;
startTime       0;

stopAt          endTime;
endTime         0.5;    // Adjust based on flow-through time
                  // Typical: 3-5 flow-through times for steady-state

deltaT          1e-5;   // Small initial timestep

writeControl    timeStep;
writeInterval   100;    // Output frequency

adjustTimeStep  yes;
maxCo           0.3;    // CRITICAL: Must be < 0.5 for stability
maxAlphaCo      0.3;    // Limit alpha Courant number

// Optional: Function objects for monitoring
functions
{
    cavitationVolume
    {
        type            volRegion;
        functionObject  phaseVolume;
        region          cavity;
        phase           vapor;
        writeFields     false;
        
        // Or use:
        // type            coded;
        // code            
        // #{
        //     const volScalarField& alpha =
        //         mesh().lookupObject<volScalarField>("alpha.water");
        //     scalar vaporVol = gSum((1.0 - alpha) * mesh().V());
        //     Info << "Vapor volume: " << vaporVol << endl;
        // #};
    }
    
    forces
    {
        type            forces;
        functionObjectLibs ("libforces.so");
        patches         (walls);
        rho             rhoInf;
        log             true;
        rhoInf          1000;
        CofR            (0 0 0);  // Center of rotation
    }
    
    probes
    {
        type            probes;
        functionObjectLibs ("libsampling.so");
        probeLocations
        (
            (0.01 0 0)
            (0.02 0 0)
            (0.03 0 0)
        );
        fields          (p alpha.water);
        writeControl    timeStep;
        writeInterval   10;
    }
}
```

**WHY These Time Settings:**
- `maxCo < 0.3`: Critical for stability, prevents pressure overshoots
- `maxAlphaCo < 0.3`: Limits interface propagation speed
- `adjustTimeStep`: Automatic timestep adjustment based on Co
- `relTol 0` for pFinal: Ensures tight pressure-velocity coupling

### Step 6: Mesh Considerations

**Mesh Guidelines:**

| Requirement | Recommendation | Rationale |
|-------------|----------------|------------|
| **y+** | < 1 (low-Re) or 30-300 (wall functions) | Accurate wall pressure prediction |
| **Refinement** | Aggressive in low-pressure zones | Resolve cavity formation |
| **Non-orthogonality** | < 70° | Maintain accuracy |
| **Aspect ratio** | < 1000 | Numerical stability |
| **Interface resolution** | ~10 cells across cavity | Capture vapor-liquid interface |

**Example Mesh Refinement (blockMeshDict):**

```cpp
// constant/polyMesh/blockMeshDict (excerpt)
vertices
(
    (0 0 0)        // 0
    (0.1 0 0)      // 1
    (0.1 0.05 0)   // 2
    (0 0.05 0)     // 3
    // ... more vertices
);

blocks
(
    hex (0 1 2 3 4 5 6 7) (100 50 1) simpleGrading (1 1 1)
);

boundary
(
    inlet { type patch; faces ((3 7 6 2)); }
    outlet { type patch; faces ((1 5 6 2)); }
    walls { type wall; faces ((0 4 5 1)); }
);
```

**Example Mesh Refinement (snappyHexMeshDict):**

```cpp
// system/snappyHexMeshDict
castellatedMesh on;
snap            on;
addLayers       off;  // Or on for boundary layer refinement

geometry
{
    hydrofoil.stl
    {
        type triSurfaceMesh;
        regions
        {
            ".*"
            {
                name foil;
            }
        }
    }
}

refinementSurfaces
{
    foil
    {
        level (2 3);  // Base refinement level
    }
}

refinementRegions
{
    cavitationZone
    {
        mode            inside;
        levels          ((1E-3 4) (5E-4 5));  // Aggressive refinement
    }
}

locationInMesh (0.01 0.01 0);  // Point inside fluid region
```

**Mesh Quality Check:**

```bash
# Check mesh quality
checkMesh

# Look for:
# - Non-orthogonality < 70°
# - Aspect ratio < 1000
# - No severely ill-defined cells
# - Boundary layer adequate for y+
```

### Step 7: Run and Monitor

**Complete Workflow:**

```bash
# 1. Clean previous results
foamCleanTutorials
rm -rf 0.[1-9]*

# 2. Check mesh
checkMesh > log.checkMesh 2>&1
cat log.checkMesh | grep -E "Non-orthogonality|Aspect|Failed"

# 3. Initialize fields
cp -r 0_orig 0

# 4. Decompose for parallel (optional)
decomposePar > log.decomposePar 2>&1

# 5. Run solver in parallel
mpirun -np 4 interPhaseChangeFoam -parallel > log.interPhaseChangeFoam 2>&1 &

# 6. Monitor convergence in real-time
tail -f log.interPhaseChangeFoam | grep "Courant"
tail -f log.interPhaseChangeFoam | grep "alpha.water"

# 7. Check cavitation volume evolution
grep "Vapor volume" log.interPhaseChangeFoam

# 8. Reconstruct (if parallel)
reconstructPar

# 9. Post-process
paraFoam -builtin
```

**Key Monitoring Indicators:**

| Indicator | Good | Bad | Action |
|-----------|------|-----|--------|
| **Courant number** | < maxCo (0.3) | > 0.5 | Reduce deltaT, check mesh |
| **Alpha bounds** | 0 ≤ α ≤ 1 | α < 0 or α > 1 | Check schemes, reduce Co |
| **Residuals** | Decreasing | Flat/increasing | Increase nCorrectors |
| **Cavitation volume** | Reaching steady | Oscillating wildly | Check stability, adjust model |
| **Mass balance** | Conserved | Drifting | Check BCs |

**Convergence Criteria:**

```bash
# Check if simulation converged
grep "Time =" log.interPhaseChangeFoam | tail -20
# Should show time advancing steadily

# Check residuals
grep "solution" log.interPhaseChangeFoam | tail -20
# Should be below tolerance

# Check cavity stability
grep "Vapor volume" log.interPhaseChangeFoam | tail -20
# Should reach quasi-steady state
```

### Step 8: Post-Processing

**ParaView Visualization:**

```python
# Python script for ParaView (save as cavity.py)
from paraview.simple import *

# Load case
cavitation = OpenFOAMReader(FileName='./cavitationCase.foam')
cavitation.MeshRegions = ['internalMesh', 'walls']

# Set time to visualize
t = GetTimeSteps()[-1]  # Last timestep
animationScene.TimeKeeper = t

# Create vapor volume contour
alphaContour = Contour(Input=cavitation)
alphaContour.ContourBy = ['POINTS', 'alpha.water']
alphaContour.Isosurfaces = [0.5]  # Vapor-liquid interface
alphaContour.PointMergeMethod = 'Uniform Binning'

# Color by pressure
alphaContour.ColorArrayName = ['POINTS', 'p']

# Render
Render()
WriteImage('cavitation_final.png')

# Animate (optional)
for t in GetTimeSteps()[::10]:  # Every 10th timestep
    animationScene.TimeKeeper = t
    Render()
    WriteImage(f'cavitation_{t:.4f}.png')
```

**Quantitative Analysis:**

```bash
# Extract cavity volume over time
foamListTimes
for time in $(foamListTimes); do
    vaporVol=$(foamDictionary -entry alpha.water -value $time 2>/dev/null | \
               awk -F'[()]' '{sum+=$2} END {print sum}')
    echo "$time $vaporVol" >> cavity_volume.dat
done

# Plot with gnuplot
gnuplot << EOF
set terminal png
set output 'cavity_volume.png'
plot 'cavity_volume.dat' w l t 'Vapor Volume'
EOF

# Extract pressure distribution
sample -latestTime -sets "(probeLine)"
```

---

## 7. Troubleshooting Guide

### 7.1 Common Issues and Solutions

| Problem | Symptoms | Root Cause | Solution |
|---------|----------|------------|----------|
| **Divergence** | Simulation crashes, residuals explode | Timestep too large | Reduce `maxCo` to 0.2, reduce `deltaT` |
| **Oscillations** | Cavitation cavity fluctuates wildly | Pressure-velocity coupling weak | Increase `nCorrectors` to 5-7 |
| **Unphysical cavitation** | Cavitation where p > p_sat | Wrong pSat value | Verify temperature, recalculate pSat |
| **No cavitation** | Expected cavitation doesn't appear | pSat set too low or pressure too high | Check pSat, reduce outlet pressure |
| **Alpha overshoot** | α < 0 or α > 1 | Numerical scheme issue | Use `MULES` limiters, check `div(phi,alpha)` |
| **Slow convergence** | Takes thousands of iterations | Mesh too coarse | Refine mesh in cavitation zone |
| **Mass imbalance** | Total mass not conserved | Wrong boundary conditions | Check BCs, ensure no-slip on walls |
| **Cavity not attached** | Cavitation appears in bulk flow | Nucleation parameters wrong | Adjust `n` or `dNuc` in SchnerrSauer |
| **Cavity too small** | Underpredicted cavitation extent | Condensation too fast | Reduce `Cc`, increase `Cv` |
| **Cavity too large** | Overpredicted cavitation extent | Evaporation too fast | Reduce `Cv`, increase `Cc` |

### 7.2 Detailed Troubleshooting

#### Issue 1: Simulation Divergence

**Symptoms:**
```
Time = 0.001

GAMG: Solving for p, Initial residual = 0.001, Final residual = 0.0001, No Iterations 3
GAMG: Solving for p, Initial residual = 1.5, Final residual = 1.2, No Iterations 1000
--> FOAM FATAL ERROR:
Maximum number of iterations exceeded
```

**Diagnosis:**
```bash
# Check Courant number
grep "Courant number" log.interPhaseChangeFoam | tail -20
# Likely > 0.5 or even > 1.0

# Check alpha bounds
foamDictionary -entry alpha.water -value 0.001
# May show values outside [0, 1]
```

**Solutions (in order of priority):**

1. **Reduce timestep:**
   ```cpp
   // system/controlDict
   maxCo           0.2;    // Was 0.3
   maxAlphaCo      0.2;
   deltaT          5e-6;   // Force smaller timestep
   ```

2. **Increase pressure iterations:**
   ```cpp
   // system/fvSolution
   nCorrectors    5;       // Was 3
   ```

3. **Add relaxation:**
   ```cpp
   // system/fvSolution
   relaxationFactors
   {
       p       0.2;  // Add pressure relaxation
       U       0.5;
   }
   ```

4. **Check mesh quality:**
   ```bash
   checkMesh > log.checkMesh
   # Look for non-orthogonality > 70°
   ```

#### Issue 2: Alpha Field Overshoot

**Symptoms:**
```bash
foamDictionary -entry alpha.water -value 0.001
# Output: alpha.water = uniform 1.05;  # Should be ≤ 1
# Or: alpha.water = uniform -0.02;   # Should be ≥ 0
```

**Root Cause:**
Unbounded discretization scheme for alpha equation

**Solutions:**

1. **Use bounded scheme:**
   ```cpp
   // system/fvSchemes
   div(phi,alpha)      Gauss vanLeer;  // Bounded TVD
   div(phi,alpha.water)Gauss vanLeer;
   ```

2. **Increase MULES sub-cycles:**
   ```cpp
   // system/fvSolution
   nAlphaSubCycles  4;  // Was 2
   ```

3. **Check for bad mesh:**
   ```bash
   checkMesh -allGeometry -allTopology
   # Look for high aspect ratio or skewed cells
   ```

#### Issue 3: No Cavitation Formation

**Symptoms:**
- Alpha.water remains 1.0 throughout domain
- Pressure drops below pSat but no vapor forms

**Diagnosis:**
```bash
# Check pressure field
foamDictionary -entry internalField -value 0/p

# Check pSat value
foamDictionary -entry pSat -value constant/transportProperties
```

**Solutions:**

1. **Verify pSat value:**
   ```cpp
   // constant/transportProperties
   pSat    2300;  // [Pa] for water at 20°C
   ```

2. **Lower outlet pressure:**
   ```cpp
   // 0/p
   outlet
   {
       type            fixedValue;
       value           uniform 5e3;  // Lower (was 1e5)
   }
   ```

3. **Increase velocity:**
   ```cpp
   // 0/U
   inlet
   {
       type            fixedValue;
       value           uniform (20 0 0);  // Increase (was 10 m/s)
   }
   ```

4. **Check cavitation model coefficients:**
   ```cpp
   // constant/phaseProperties
   Cv      100;  // Increase vaporization rate (was 1)
   ```

### 7.3 Parameter Sensitivity Analysis

**High Sensitivity (Small changes → large effects):**

| Parameter | Sensitivity | Effect of 10% increase |
|-----------|-------------|------------------------|
| **pSat** | Very High | ±30-50% cavity volume change |
| **Cc / Cv** | High | 2-5x cavity size change for factor of 2 |
| **maxCo** | High | > 0.5 → divergence likely |
| **nCorrectors** | Medium | 3→5 improves convergence 2-3x |

**Low Sensitivity:**
- `dNuc`: 2e-6 to 5e-6 has minor effect on cavity size
- `nu` (viscosity): Within 50% of reference, small effect
- `UInf` in Kunz: Scales time constant but not final state

### 7.4 Convergence Checklist

**Before starting simulation:**

- [ ] Mesh quality verified (checkMesh passed)
- [ ] pSat value matches operating temperature
- [ ] Boundary conditions verified (inlet/outlet pressure difference)
- [ ] Cavitation zone mesh refined
- [ ] Initial fields set correctly (alpha = 1)
- [ ] Numerical schemes appropriate (vanLeer for alpha)

**During simulation:**

- [ ] maxCo < 0.3 maintained throughout
- [ ] nCorrectors ≥ 3 for tight pressure-velocity coupling
- [ ] Alpha field bounded (0 ≤ α ≤ 1)
- [ ] Residuals decreasing monotonically
- [ ] Cavitation volume reaching steady state

**For high-fidelity results:**

- [ ] y+ < 1 for wall-bounded flows
- [ ] Grid independence verified (2-3 mesh levels)
- [ ] Time-averaged quantities monitored (not just instantaneous)
- [ ] Physical units verified (Pa vs bar, etc.)

---

## Quick Reference Card

### Critical Parameters

| Parameter | Typical Value | Units | Impact | High Value → |
|-----------|---------------|-------|--------|--------------|
| **pSat** (water 20°C) | 2300 | Pa | High: Controls cavity onset | Larger cavity |
| **maxCo** | < 0.3 | - | High: Stability | Risk divergence |
| **nCorrectors** | 3-5 | - | High: Coupling accuracy | Better convergence |
| **Cc** (condensation) | 0.01-1 | - | High: Collapse rate | Faster collapse |
| **Cv** (vaporization) | 1-1000 | - | High: Growth rate | Larger cavity |
| **n** (SchnerrSauer) | 1e10-1e15 | 1/m³ | High: Nucleation sites | More cavitation |

### Boundary Condition Summary

| Boundary | p | U | alpha.water | k | omega |
|----------|---|---|-------------|---|-------|
| **Inlet** | fixedValue (high) | fixedValue | fixedValue (1) | fixedValue | fixedValue |
| **Outlet** | fixedValue (low) | zeroGradient | zeroGradient | zeroGradient | zeroGradient |
| **Walls** | zeroGradient | noSlip | zeroGradient | kqRWallFunction | omegaWallFunction |
| **Symmetry** | symmetryPlane | symmetryPlane | symmetryPlane | symmetryPlane | symmetryPlane |

### Solver Commands

```bash
# Serial
interPhaseChangeFoam -case /path/to/case

# Parallel
decomposePar
mpirun -np 4 interPhaseChangeFoam -parallel
reconstructPar

# Check mesh
checkMesh

# Monitor
tail -f log.interPhaseChangeFoam | grep "Courant"
```

### Common File Locations

| File | Location | Purpose |
|------|----------|---------|
| **phaseProperties** | constant/ | Cavitation model settings |
| **transportProperties** | constant/ | Phase properties, pSat |
| **controlDict** | system/ | Time control, output |
| **fvSchemes** | system/ | Discretization schemes |
| **fvSolution** | system/ | Solver settings |

---

## Practice Exercises

### Exercise 1: Model Selection

Given the following scenarios, recommend the most appropriate cavitation model and explain your reasoning:

1. **Marine propeller** at 20 knots, focus on noise prediction
2. **Centrifugal pump** at 3000 RPM, focus on performance
3. **Inject nozzle** with violent cavitation, focus on stability
4. **Hydrofoil** validation against experimental data

<details>
<summary>Solutions</summary>

**1. Marine propeller at 20 knots (noise prediction):**
- **Recommended: Kunz model**
- **Reasoning:** 
  - Transient noise prediction requires stable simulation over long times
  - Asymmetric coefficients (Cv >> Cc) prevent violent collapse divergence
  - Marine industry standard for propeller simulations
  - High stability allows larger timesteps for acoustic analysis

**2. Centrifugal pump at 3000 RPM (performance):**
- **Recommended: Zwart model**
- **Reasoning:**
  - Optimized specifically for pump geometries
  - Good prediction of cavity extent and location
  - Widely validated in industrial pump applications
  - Accurate performance prediction (head, efficiency)

**3. Inject nozzle (violent cavitation, stability focus):**
- **Recommended: Kunz model**
- **Reasoning:**
  - Most stable model for violent cavitation events
  - Asymmetric coefficients prevent divergence
  - Handles rapid pressure changes well
  - Can complete simulation where other models would crash

**4. Hydrofoil validation (experimental comparison):**
- **Recommended: SchnerrSauer model**
- **Reasoning:**
  - Most widely validated model in literature
  - Extensive documentation and case studies
  - Explicit physical parameters for tuning
  - Best for comparison with published data

</details>

### Exercise 2: Troubleshooting

A simulation shows:
- Cavitation appearing throughout the domain (not just low-pressure zones)
- Alpha field shows values α = -0.05 and α = 1.03

Identify the problems and propose solutions.

<details>
<summary>Solutions</summary>

**Diagnosis:**

**Problem 1: Unbounded alpha field**
- **Symptoms:** α < 0 and α > 1
- **Root Cause:** Numerical scheme not bounded, allowing overshoots
- **Impact:** Unphysical mass transfer, potential divergence

**Problem 2: Widespread cavitation**
- **Symptoms:** Cavitation everywhere, not just low-pressure zones
- **Root Cause:** Possible incorrect pSat causing unphysical phase change
- **Impact:** Wrong physics, meaningless results

**Solutions:**

**Step 1: Fix alpha scheme**
```cpp
// system/fvSchemes
div(phi,alpha)      Gauss vanLeer;  // Change to bounded scheme
div(phi,alpha.water)Gauss vanLeer;
```

**Step 2: Verify pSat value**
```cpp
// constant/transportProperties
pSat    2300;  // Verify: water at 20°C
```

**Step 3: Reduce timestep for stability**
```cpp
// system/controlDict
maxCo           0.2;    // Reduce from 0.3
maxAlphaCo      0.2;
```

**Step 4: Increase MULES sub-cycles**
```cpp
// system/fvSolution
nAlphaSubCycles  4;  // Increase from 2
```

**Step 5: Add pressure relaxation**
```cpp
// system/fvSolution
relaxationFactors
{
    p       0.2;
    rho     0.05;
}
```

**Verification:**
```bash
# Re-run with changes
interPhaseChangeFoam > log 2>&1

# Monitor alpha bounds
for t in $(foamListTimes); do
    min=$(foamDictionary -entry alpha.water -value $t | grep -o "min=[-e.0-9]*" | cut -d= -f2)
    max=$(foamDictionary -entry alpha.water -value $t | grep -o "max=[-e.0-9]*" | cut -d= -f2)
    echo "$t: alpha in [$min, $max]"
done
```

**Expected outcome:**
- Alpha bounded within [0, 1]
- Cavitation only in regions where p < p_sat
- Stable convergence

</details>

### Exercise 3: Parametric Study

Create a parametric study script to investigate the effect of `Cv` (vaporization coefficient) on cavity size. Range: Cv = 10, 50, 100, 500, 1000.

**Requirements:**
1. Automate case setup for each Cv value
2. Run each simulation
3. Extract final cavity volume
4. Generate plot of cavity volume vs. Cv

<details>
<summary>Solution Template</summary>

```bash
#!/bin/bash
# cavitation_parametric.sh - Parametric study of Cv effect

# Configuration
BASE_CASE="case_base"
CV_VALUES=(10 50 100 500 1000)
RESULTS_FILE="cavity_volume_vs_Cv.dat"

# Clean previous results
rm -f $RESULTS_FILE
rm -rf case_Cv_*

# Header for results file
echo "# Cv Cavity_Volume[m3]" > $RESULTS_FILE

# Loop over Cv values
for Cv in "${CV_VALUES[@]}"; do
    
    echo "=========================================="
    echo "Running case with Cv = $Cv"
    echo "=========================================="
    
    # Create new case directory
    CASE_DIR="case_Cv_$Cv"
    cp -r $BASE_CASE $CASE_DIR
    cd $CASE_DIR
    
    # Modify phaseProperties
    sed -i "s/Cv.*/Cv      $Cv;/" constant/phaseProperties
    
    # Run simulation
    echo "Starting simulation..."
    interPhaseChangeFoam > log.$Cv 2>&1
    
    # Check if simulation completed
    if [ $? -eq 0 ]; then
        echo "Simulation completed successfully"
    else
        echo "ERROR: Simulation failed!"
        cd ..
        continue
    fi
    
    # Extract final time
    FINAL_TIME=$(ls -1 [0-9]* | sort -n | tail -1)
    
    # Calculate cavity volume (integral of (1 - alpha.water))
    CAVITY_VOL=$(foamDictionary -entry alpha.water -value $FINAL_TIME 2>/dev/null | \
                  awk -F'[()]' '{
                      for(i=1; i<=NF; i++) {
                          if($i ~ /min=/) min=$(i+1);
                          if($i ~ /max=/) max=$(i+1);
                      }
                  } END {
                      # Approximate: volume fraction * domain volume
                      # For more accuracy, use post-processing
                      print "N/A"  # Placeholder
                  }')
    
    # Better approach: use sample or post-process
    # Here we use ParaView python script or foamCalc
    foamCalc magGrad alpha.water -latestTime
    
    # Extract from log (if function object used)
    if grep -q "Vapor volume" log.$Cv; then
        CAVITY_VOL=$(grep "Vapor volume" log.$Cv | tail -1 | awk '{print $3}')
    fi
    
    # Write to results file
    echo "$Cv $CAVITY_VOL" >> ../$RESULTS_FILE
    
    echo "Cv = $Cv, Cavity Volume = $CAVITY_VOL"
    
    cd ..
done

echo "=========================================="
echo "Parametric study complete!"
echo "Results saved to: $RESULTS_FILE"
echo "=========================================="

# Generate plot (requires gnuplot)
if command -v gnuplot &> /dev/null; then
    gnuplot << EOF
    set terminal pngcairo enhanced font 'Arial,12'
    set output 'cavity_volume_vs_Cv.png'
    set title 'Effect of Vaporization Coefficient on Cavity Volume'
    set xlabel 'Cv (vaporization coefficient)'
    set ylabel 'Cavity Volume [m³]'
    set grid
    set logscale x
    plot '$RESULTS_FILE' w lp pt 7 ps 1.5 lc rgb 'blue' t 'Simulation data'
EOF
    echo "Plot generated: cavity_volume_vs_Cv.png"
else
    echo "Gnuplot not found. Skipping plot generation."
    echo "Manual plotting: gnuplot> plot '$RESULTS_FILE' w lp"
fi
```

**Post-processing script (extract_cavity_volume.py):**

```python
#!/usr/bin/env python3
"""
Extract cavity volume from OpenFOAM results
"""
import os
import sys
import numpy as np

def read_field(time_dir, field_name):
    """Read OpenFOAM field and return numpy array"""
    # This is a simplified version
    # In practice, use PyFoam or read binary format
    pass

def calculate_cavity_volume(case_dir, time_dir):
    """Calculate vapor volume: V_cav = integral(1 - alpha.water) dV"""
    alpha_file = os.path.join(case_dir, time_dir, "alpha.water")
    
    # Use foamCalc to compute volume
    os.system(f"foamCalc volMag alpha.water {time_dir} -case {case_dir}")
    
    # Read and sum
    # (Implementation details depend on OpenFOAM version)
    
    return cavity_volume

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: extract_cavity_volume.py <case_dir> <time>")
        sys.exit(1)
    
    case_dir = sys.argv[1]
    time = sys.argv[2] if len(sys.argv) > 2 else "0.5"
    
    vol = calculate_cavity_volume(case_dir, time)
    print(f"Cavity volume: {vol:.6e} m³")
```

**Usage:**

```bash
# Make scripts executable
chmod +x cavitation_parametric.sh
chmod +x extract_cavity_volume.py

# Run parametric study
./cavitation_parametric.sh

# View results
cat cavity_volume_vs_Cv.dat
```

**Expected trends:**
- Higher Cv → Larger cavity volume
- Relationship typically logarithmic
- Very high Cv (≥ 1000) may cause instability

</details>

### Exercise 4: Grid Independence Study

Perform a grid independence study for a cavitation case:

1. Create 3 mesh refinement levels (coarse, medium, fine)
2. Run simulation on each mesh
3. Compare cavity volume and pressure distribution
4. Determine if results are grid-independent

<details>
<summary>Solution Outline</summary>

**Step 1: Define mesh refinement levels**

```cpp
// system/snappyHexMeshDict (template)
refinementLevels
{
    coarse  ( (1E-3 3) );
    medium  ( (1E-3 4) );
    fine    ( (1E-3 5) (5E-4 6) );
}
```

**Step 2: Create script to automate**

```bash
#!/bin/bash
# grid_independence.sh

MESHES=("coarse" "medium" "fine")
LEVELS=(3 4 5)

for i in {0..2}; do
    MESH=${MESHES[$i]}
    LEVEL=${LEVELS[$i]}
    
    echo "Creating $MESH mesh (refinement level $LEVEL)..."
    
    # Modify snappyHexMeshDict
    sed -i "s/refinementLevels.*/refinementLevels\n    {\n        cavitationZone\n        {\n            levels  ((1E-3 $LEVEL));\n        }\n    }/" system/snappyHexMeshDict
    
    # Generate mesh
    snappyHexMesh -overwrite > log.snappyHexMesh_$MESH 2>&1
    
    # Run simulation
    interPhaseChangeFoam > log.interPhaseChangeFoam_$MESH 2>&1
    
    # Extract results
    FINAL_TIME=$(ls -1 [0-9]* | sort -n | tail -1)
    CELL_COUNT=$(foamDictionary -entry nCells -value polyMesh)
    
    echo "$MESH: $CELL_COUNT cells"
done
```

**Step 3: Compare results**

```python
# analyze_grid_independence.py
import matplotlib.pyplot as plt
import numpy as np

# Data (example)
meshes = ['coarse', 'medium', 'fine']
cells = [1e5, 5e5, 2e6]
cavity_vol = [1.2e-4, 1.5e-4, 1.55e-4]

# Plot convergence
plt.figure(figsize=(10, 6))
plt.subplot(1, 2, 1)
plt.loglog(cells, cavity_vol, 'o-')
plt.xlabel('Number of cells')
plt.ylabel('Cavity volume [m³]')
plt.title('Grid Convergence')
plt.grid(True)

# Calculate GCI (Grid Convergence Index)
# Richardson extrapolation
r = 2  # Refinement ratio
f1, f2, f3 = cavity_vol  # fine, medium, coarse
f21_ext = f1 + (f1 - f2) / (r**2 - 1)
e21 = abs((f1 - f2) / f1)
e32 = abs((f2 - f3) / f2)

plt.subplot(1, 2, 2)
plt.plot(meshes, cavity_vol, 'o-')
plt.xlabel('Mesh level')
plt.ylabel('Cavity volume [m³]')
plt.title('Cavity Volume vs Mesh')
plt.grid(True)

plt.tight_layout()
plt.savefig('grid_independence.png')
```

**Step 4: Convergence criteria**

Results are grid-independent if:
- Difference between medium and fine < 2%
- GCI < 5%
- Qualitative agreement in cavity shape

</details>

---

## Key Takeaways

### Core Concepts

1. **Cavitation is a phase-change phenomenon** driven by local pressure dropping below saturation pressure (p < p_sat). Understanding this threshold behavior is essential for prediction and control.

2. **Model selection matters critically**: 
   - SchnerrSauer for general purpose and validation (default choice)
   - Kunz for stability in marine applications with violent cavitation
   - Zwart for industrial pumps and turbomachinery
   - Merkle for research and accuracy-focused studies

3. **Saturation pressure is the most critical parameter**: Small errors in temperature → large errors in cavitation prediction. A 5°C error causes ~30% error in pSat → dramatically different cavity size. Always verify pSat against operating conditions.

4. **Numerical stability is challenging but manageable**: 
   - Keep maxCo < 0.3 for stability
   - Use bounded schemes (vanLeer) for alpha to prevent overshoots
   - Increase nCorrectors for tight pressure-velocity coupling
   - Consider asymmetric coefficients (Kunz model) for difficult cases

5. **Mesh quality is essential for accuracy**: Refine regions where p < p_sat is expected; use low-Re mesh (y+ < 1) near walls for accurate pressure prediction; ensure non-orthogonality < 70° for stability

### Engineering Significance

6. **Cavitation causes major engineering problems**: Material damage (erosion), noise, performance loss, and vibration. Understanding cavitation is critical for:
   - **Marine Industry**: Propeller design and signature control
   - **Hydropower**: Turbine runner lifetime prediction
   - **Pumps**: Efficiency optimization and failure prevention
   - **Injectors**: Fuel atomization quality and combustion efficiency

### Practical Implementation

7. **Follow the systematic workflow**: Case structure → Boundary conditions → Numerical schemes → Solver settings → Mesh → Run → Monitor → Post-process. Each step has critical parameters that affect success.

8. **Monitor the right indicators**: Courant number (< maxCo), alpha bounds (0 ≤ α ≤ 1), residual convergence, and cavity volume evolution. These early warnings prevent wasted computation.

9. **Troubleshoot systematically**: Identify symptoms → diagnose root cause → apply targeted solution. Most problems stem from timestep too large, wrong pSat, or unbounded alpha schemes.

10. **Verify physical realism**: Check units, compare with experimental data, validate against published cases, ensure mass conservation, and verify cavity location matches pressure distribution.

---

## Concept Check

<details>
<summary><b>1. When does cavitation occur?</b></summary>

**Answer:** When local pressure falls below saturation pressure (p < p_sat)

The liquid undergoes phase change to vapor, forming bubbles that grow in low-pressure regions and collapse when transported to higher-pressure zones. This threshold behavior is highly sensitive to small changes in pressure or temperature.

**Why it matters:**
- Cavitation onset determines safe operating envelopes for pumps, propellers, and turbines
- Small changes in operating conditions can trigger or eliminate cavitation
- Understanding this threshold is key to design and control strategies

</details>

<details>
<summary><b>2. Why is the Kunz model preferred for marine propellers?</b></summary>

**Answer:** High numerical stability due to asymmetric coefficients (Cv >> Cc)

The large vaporization coefficient (Cv ≈ 1000) allows rapid bubble growth, while the small condensation coefficient (Cc ≈ 0.01) prevents violent collapse that can cause simulation divergence. This asymmetric treatment is critical for transient marine applications where:
- Long simulation times are required (noise, vibration prediction)
- Cavitation dynamics can be violent and unstable
- Computational efficiency is important (larger timesteps possible)

**Trade-offs:**
- Lower physical accuracy compared to SchnerrSauer
- Requires empirical tuning for each application
- Less predictive capability for novel geometries

</details>

<details>
<summary><b>3. What happens if maxCo is set to 0.8 in a cavitation simulation?</b></summary>

**Answer:** Likely divergence or unphysical results

Large timestep leads to:
- **Pressure overshoots** → unphysical cavitation prediction (cavitation where p > p_sat)
- **Alpha field instability** (α < 0 or α > 1) → violates VOF definition
- **Poor capture of rapid phase-change dynamics** → inaccurate cavity size and location
- **Mass conservation errors** → non-physical results

**Solution:** Reduce maxCo to < 0.3 (typically 0.2-0.3) for stability

**Why Co is so critical for cavitation:**
- Phase change occurs on very short timescales (microseconds)
- Large timesteps miss the rapid dynamics of bubble growth and collapse
- Explicit treatment of phase change source terms is conditionally stable
- OpenFOAM's MULES algorithm becomes less effective at large Co

</details>

<details>
<summary><b>4. How does saturation pressure vary with temperature?</b></summary>

**Answer:** Exponentially (Clausius-Clapeyron relation)

Example for water:
- **20°C:** pSat = 2,339 Pa (reference point)
- **50°C:** pSat = 12,349 Pa (~5x increase for 30°C rise)
- **100°C:** pSat = 101,325 Pa (~43x increase for 80°C rise)

**Critical implications:**
- A **5°C error causes ~30% error in pSat** → dramatically different cavity size
- A **10°C error causes ~70% error in pSat** → completely wrong prediction
- Temperature measurement errors are a major source of simulation discrepancy
- For high-accuracy work, use temperature-dependent pSat or tabulated data

**Practical tip:**
Always verify operating temperature in experiments or field conditions before setting pSat. When in doubt, run a sensitivity analysis (±5°C) to assess the impact on predictions.

</details>

<details>
<summary><b>5. Why use the vanLeer scheme for the alpha equation?</b></summary>

**Answer:** Bounded scheme prevents overshoots (α < 0 or α > 1)

Cavitation simulations involve:
- **Large density ratios** (ρ_water/ρ_vapor ≈ 43,000)
- **Rapid phase change** (microsecond timescales)
- **Sharp interfaces** (vapor-liquid boundary)

Unbounded schemes can produce unphysical volume fractions:
- **Negative alpha** → non-physical mass transfer, negative density
- **Alpha > 1** → violates VOF definition (α is a volume fraction)
- **Oscillations** near interface → spurious cavitation, divergence

**Why vanLeer specifically:**
- TVD (Total Variation Diminishing) scheme
- Preserves monotonicity (no new extrema created)
- Second-order accuracy in smooth regions
- First-order near discontinuities (prevents oscillations)
- Well-tested for VOF simulations in OpenFOAM

**Alternatives:**
- `Gauss MUSCL` - Second-order, less stable
- `Gauss limitedLinearV` - Bounded, less accurate
- `Gauss upwind` - Most stable, very diffusive (not recommended)

</details>

<details>
<summary><b>6. What is the difference between pSat and operating pressure?</b></summary>

**Answer:**

**pSat (Saturation Pressure):**
- **Property of the fluid** at a given temperature
- **Threshold value** that determines if cavitation occurs
- **Fixed by thermodynamics** (Clausius-Clapeyron relation)
- Example: pSat = 2,339 Pa for water at 20°C

**Operating Pressure:**
- **Local pressure field** in the flow (p)
- **Variable throughout the domain**
- **Determined by flow physics** (Bernoulli, boundary conditions, geometry)
- Example: p = 1e5 Pa at inlet, p = 5e3 Pa at suction peak

**Cavitation criterion:**
```
Cavitation occurs where: p_local < pSat
No cavitation where:    p_local ≥ pSat
```

**Common confusion:**
- pSat is NOT a boundary condition
- pSat is NOT the reference pressure
- pSat is a material property that varies with temperature
- Setting outlet pressure below pSat doesn't guarantee cavitation (depends on local pressure field)

**Example:**
```
Inlet:  p = 2e5 Pa (2 bar)
Outlet: p = 1e5 Pa (1 bar)
pSat = 2,339 Pa (water at 20°C)

Cavitation will occur in regions where local pressure drops below 2,339 Pa
(typically at suction peak of hydrofoil, near impeller blade tips, etc.)
NOT at the outlet where p = 1e5 Pa >> pSat
```

</details>

---

## Related Documentation

- **Overview:** [00_Overview.md](00_Overview.md) — Complex multiphase phenomena overview and motivation
- **Phase Change Theory:** [01_Phase_Change_Modeling.md](01_Phase_Change_Modeling.md) — General phase-change physics, boiling, and evaporation
- **Population Balance:** [03_Population_Balance_Modeling.md](03_Population_Balance_Modeling.md) — Bubble size distribution modeling
- **Turbulence:** [05_TURBULENCE_IN_MULTIPHASE_FLOWS/05_Turbulence_in_Multiphase_Flows.md](../05_TURBULENCE_IN_MULTIPHASE_FLOWS/05_Turbulence_in_Multiphase_Flows.md) — Turbulence modeling for cavitation
- **Module 4 Equations:** [../../99_EQUATIONS_REFERENCE/02_Momentum_Conservation.md](../../99_EQUATIONS_REFERENCE/02_Momentum_Conservation.md) — Two-phase momentum equations
- **Module 3 Coupling:** [../../MODULE_03_SINGLE_PHASE_FLOW/CONTENT/02_PRESSURE_VELOCITY_COUPLING/05_Algorithm_Comparison.md](../../MODULE_03_SINGLE_PHASE_FLOW/CONTENT/02_PRESSURE_VELOCITY_COUPLING/05_Algorithm_Comparison.md) — PIMPLE algorithm details

---

## References and Further Reading

**Classic Papers:**

1. Schnerr, G. H., & Sauer, J. (2001). "Physical and numerical modeling of unsteady cavitation dynamics." *International Conference on Multiphase Flow.*
2. Kunz, R. F., et al. (2000). "A preconditioned Navier-Stokes method for two-phase flows with application to cavitation prediction." *AIAA Paper 2000-1513.*
3. Merkle, C. L., et al. (1998). "Computational modeling of the dynamics of sheet cavitation." *Third International Symposium on Cavitation.*
4. Zwart, P. J., Gerber, A. G., & Belamri, T. A. (2004). "A two-phase model for predicting cavitation dynamics." *ICM 2004.*

**OpenFOAM-Specific:**

5. OpenFOAM User Guide, Section 7.4: interPhaseChangeFoam solver
6. OpenFOAM Programmer's Guide: MULES algorithm for VOF
7. OpenFOAM Wiki: Cavitation modeling examples and tutorials

**Textbooks:**

8. Brennen, C. E. (1995). *Cavitation and Bubble Dynamics*. Oxford University Press.
9. Franc, J. P., & Michel, J. M. (2004). *Fundamentals of Cavitation*. Kluwer Academic.
10. Neshan, H. (2019). *Cavitation in Fluid Machinery*. Springer.