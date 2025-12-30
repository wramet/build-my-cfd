# Combustion Models

---

## 🎯 Learning Objectives

หลังจากศึกษาบทนี้ คุณจะสามารถ:

1. **เข้าใจ** ความแตกต่างของ turbulent-chemistry interaction models ใน OpenFOAM
2. **เลือกใช้** combustion model ที่เหมาะสมกับ regime ของปัญหาที่ต้องการแก้ไข
3. **ตั้งค่า** combustion model parameters อย่างถูกต้องใน `constant/combustionProperties`
4. **ประเมิน** ข้อดีและข้อจำกัดของแต่ละ model
5. **วิเคราะห์** ความสัมพันธ์ระหว่าง Damköhler number และ Karlovitz number กับ model selection
6. **ปรับปรุง** model coefficients สำหรับ specific applications

---

## Overview

> **Combustion Models ใน OpenFOAM: Turbulence-Chemistry Interaction**

Combustion models มีบทบาทสำคัญในการจำลองปฏิกิริยาเคมีในกระแส turbulent เนื่องจาก flame ในสถานการณ์จริงส่วนใหญ่เป็น turbulent ทำให้การคำนวณ direct integration ของ chemical kinetics มีค่าใช้จ่ายสูงมาก ดังนั้นจึงต้องใช้ **turbulence-chemistry interaction models** เพื่อลด computational cost ในขณะที่ยังคงความแม่นยำที่เหมาะสม

### ทำไมต้อง Combustion Model?

**Physical Challenge:**
- Turbulent flames มี time scales หลายระดับ (chemistry ~10⁻⁶ s, turbulence ~10⁻³ s)
- Direct Numerical Simulation (DNS) ต้องการ resolution ที่ละเอียดเกินไปสำหรับ industrial applications
- Need for **closure models** ที่ represent interaction ระหว่า่าง turbulence และ chemistry

**OpenFOAM Approach:**
- ให้หลาย combustion models ที่ใช้ hypotheses ต่างกัน
- แต่ละ model เหมาะกับ flow regimes และ computational resources ที่แตกต่างกัน
- Integration กับ chemical kinetics ผ่าน `thermo` และ `chemistry` libraries

**Computational Challenge Scale:**
```
DNS:  O(10⁹) cells × 10⁻⁸ s timestep → O(10⁶) CPU hours
RANS: O(10⁶) cells × 10⁻⁴ s timestep → O(10²) CPU hours
```

---

## What: Combustion Models คืออะไร?

Combustion model คือ **mathematical closure** สำหรับ averaging nonlinear chemical source terms ใน turbulent reacting flows:

$$\overline{\dot{\omega}_i} \neq \dot{\omega}_i(\overline{Y}, \overline{T}, \overline{p})$$

เนื่องจาก reaction rate $\dot{\omega}_i$ เป็น **highly nonlinear function** ของ temperature (Arrhenius dependence), Reynolds/Favre averaging ทำให้เกิด **closure problem**:

$$\overline{\dot{\omega}_i} = \overline{\dot{\omega}_i(\text{fluctuating states})}$$

แต่ละ model ใช้ assumptions ต่างกันในการ compute $\overline{\dot{\omega}_i}$ จาก mean quantities $\tilde{Y}_i, \tilde{T}, \tilde{p}$

### Closure Problem Fundamentals

**Favre Average Definition:**

$$\tilde{\phi} = \frac{\overline{\rho \phi}}{\overline{\rho}}, \quad \phi = \tilde{\phi} + \phi''$$

**Nonlinear Reaction Rate:**

$$\dot{\omega}_i(T, Y_j) = A T^\beta \exp\left(-\frac{T_a}{T}\right) \prod_j Y_j^{\nu_j}$$

**Averaged Rate:**

$$\overline{\dot{\omega}_i} = A \overline{T^\beta \exp\left(-\frac{T_a}{T}\right) \prod_j Y_j^{\nu_j}} \neq A \tilde{T}^\beta \exp\left(-\frac{T_a}{\tilde{T}}\right) \prod_j \tilde{Y}_j^{\nu_j}$$

**Modeling Approaches:**

| Approach | Strategy | Key Assumption |
|----------|----------|----------------|
| **Moment closure** | Expand $\overline{\dot{\omega}_i}$ in moments | Small fluctuations |
| **PDF methods** | Integrate over joint PDF | PDF shape known |
| **Flamelet** | Reduce to 1D flames | Thin flame |
| **EDC/PaSR** | Reacting volume fraction | Mixing-kinetics split |

---

## Why: ทำไมต้องใช้ Turbulence-Chemistry Interaction?

### 1. Damköhler Number (Da)

$$Da = \frac{\tau_{\text{flow}}}{\tau_{\text{chem}}} = \frac{\text{flow time scale}}{\text{chemical time scale}}$$

**Time Scale Definitions:**

$$\tau_{\text{flow}} = \frac{k}{\varepsilon} = \frac{\text{turbulent kinetic energy}}{\text{dissipation rate}}$$

$$\tau_{\text{chem}} = \left[\frac{1}{Y_i}\frac{dY_i}{dt}\right]^{-1} \approx \frac{\delta_L}{S_L}$$

**Physical Interpretation:**

| Da Regime | Physics | Model Requirements |
|-----------|---------|-------------------|
| **Da ≪ 1** (Fast chemistry) | $\tau_{\text{chem}} \ll \tau_{\text{flow}}$ — reactions complete before mixing | **Mixing-controlled:** Flamelet, EDC |
| **Da ≫ 1** (Slow chemistry) | $\tau_{\text{chem}} \gg \tau_{\text{flow}}$ — mixing complete before reactions | **Kinetically-controlled:** Laminar, PaSR |
| **Da ~ 1** (Mixed regime) | $\tau_{\text{chem}} \sim \tau_{\text{flow}}$ — both important | **Both important:** PaSR, EDC |

**Typical Da Values:**

```
Laminar flame:              Da = O(1) - O(10)
Premixed turbulent flame:   Da = O(0.1) - O(10)
Diffusion flame (jet):      Da = O(1) - O(100)
Autoignition (HCCI):        Da ≪ 1 (slow chemistry)
```

### 2. Karlovitz Number (Ka)

$$Ka = \left(\frac{u'}{S_L}\right)^{3/2}\left(\frac{\delta_L}{l}\right)^{1/2} = \frac{\tau_{\text{chem}}}{\tau_{\eta}}$$

where:
- $u'$ = turbulent velocity fluctuation
- $S_L$ = laminar flame speed
- $\delta_L$ = laminar flame thickness
- $l$ = integral length scale
- $\tau_{\eta}$ = Kolmogorov time scale

**Physical Meaning:**

- **Ka < 1:** $\tau_{\eta} > \tau_{\text{chem}}$ — smallest eddies larger than flame thickness
- **Ka > 1:** $\tau_{\eta} < \tau_{\text{chem}}$ — eddies penetrate flame structure

| Ka Regime | Flame Structure | Turbulence-Chemistry Interaction | Model Choice |
|-----------|----------------|----------------------------------|--------------|
| **Ka < 1** (Corrugated flamelets) | Flame intact, wrinkled | Weak — flame surface area increased | **Flamelet models**, Xi |
| **1 < Ka < 100** (Thin reaction zones) | Flame thinned but continuous | Moderate — inner layer affected | **EDC, PaSR** |
| **Ka > 100** (Broken reaction zones) | Flame structure disrupted | Strong — well-stirred regime | **PaSR, well-stirred** |

**Borghi Diagram:**

```
Ka
↑
│ Broken Reaction Zones (Ka > 100)
│─────────────────────────────────
│ Thin Reaction Zones (1 < Ka < 100)
│─────────────────────────────────
│ Corrugated Flamelets (Ka < 1)
│
└────────────────────────────────────→ Da
   Slow  Da=1  Fast
```

### 3. Regime Classification

**Premixed Combustion Regimes:**

| Regime | Da | Ka | Physical Description | Model |
|--------|----|----|----------------------|-------|
| Wrinkled flamelets | ≫1 | ≪1 | Flame surface wrinkled, inner layer intact | Flamelet, Xi |
| Corrugated flamelets | ≫1 | <1 | Strong wrinkling, flame surface increased | Xi, Flamelet |
| Thin reaction zones | ~1 | 1-100 | Inner layer thinned, quasi-steady | PaSR, EDC |
| Broken reaction zones | ~1 | >100 | Local extinction, distributed reaction | PaSR |

**Non-Premixed Combustion Regimes:**

| Regime | Da | Physical Description | Model |
|--------|----|----------------------|-------|
| Flamelet | >10 | Thin flames, fast chemistry | Flamelet (diffusion) |
| Thin reaction zones | ~1-10 | Moderate Damköhler | EDC, PaSR |
| Distributed reaction | <1 | Slow chemistry, well-mixed | PaSR, Laminar |

---

## How: Model Selection & Implementation

---

## 1. Model Comparison

### Quantitative Comparison

| Model | Computational Cost | Memory Usage | Accuracy (Da~1) | Applicability | Implementation Complexity |
|-------|-------------------|--------------|-----------------|---------------|-------------------------|
| **Laminar** | ★☆☆☆☆ (Very High) | ★★★★☆ (Low) | ★★★★★ (DNS quality) | DNS, laminar flames | ★★★☆☆ (Medium) |
| **EDC** | ★★★☆☆ (Medium) | ★★☆☆☆ (Medium) | ★★★☆☆ (Moderate) | Industrial furnaces | ★★☆☆☆ (Simple) |
| **PaSR** | ★★★★☆ (Fast) | ★★★☆☆ (Medium) | ★★★☆☆ (Moderate) | Large domains, mixed regimes | ★★☆☆☆ (Simple) |
| **Flamelet** | ★★★★★ (Very Fast) | ★☆☆☆☆ (High) | ★★★★☆ (Good) | Premixed/diffusion flames | ★☆☆☆☆ (Complex preprocessing) |
| **Xi** | ★★★★☆ (Fast) | ★★★☆☆ (Medium) | ★★★☆☆ (Moderate) | Premixed turbulent flames | ★★☆☆☆ (Simple) |

**Cost Quantification (relative to laminar):**

```
Flamelet:     0.01-0.05×  (table lookup)
Xi:           0.1-0.3×    (transport eqn, no chemistry)
PaSR:         0.3-0.7×    (single chemistry solve)
EDC:          0.5-1.0×    (iterative chemistry)
Laminar:      1.0×        (direct integration)
```

### Theoretical Foundation Comparison

| Model | Key Hypothesis | Mathematical Approach | Closure Strategy |
|-------|---------------|----------------------|------------------|
| **Laminar** | No turbulence-chemistry interaction | Direct ODE integration | $\overline{\dot{\omega}_i} = \dot{\omega}_i(\tilde{Y}, \tilde{T}, \tilde{p})$ |
| **EDC** | Fine structures are Perfectly Stirred Reactors | Eddy dissipation rate → reacting volume fraction | $\overline{\dot{\omega}_i} = \frac{\gamma^*}{\tau^*} \rho (Y_i^* - \tilde{Y}_i)$ |
| **PaSR** | Cell = PSR + non-reacting volume | Mixing time → chemical conversion rate | $\overline{\dot{\omega}_i} = \kappa \dot{\omega}_i(\text{PSR})$ |
| **Flamelet** | Flame thin relative to turbulent scales | 1D flame libraries → lookup tables | $\overline{\dot{\omega}_i} = \int \dot{\omega}_i(Z) \tilde{P}(Z) dZ$ |
| **Xi** | Flame surface area wrinkled by turbulence | Transport equation for flame surface density | $\overline{\dot{\omega}_T} = \rho_u S_L \Sigma$ |

### Model Selection Criteria

| Criterion | Weight | Evaluation Method |
|-----------|--------|-------------------|
| **Computational budget** | High | CPU hours available, grid size |
| **Flow regime** | High | Da, Ka calculation |
| **Flame type** | High | Premixed vs. diffusion vs. mixed |
| **Chemical complexity** | Medium | Number of species, stiffness |
| **Validation data** | Medium | Experimental data available |
| **Expertise** | Low | Familiarity with model tuning |

---

## 2. Laminar Combustion Model

### Physical Principles

**Direct Integration** ของ chemical kinetics โดยไม่มี turbulence-chemistry interaction closure:

- **Assumption:** ไม่มี turbulence หรือ flame thickness >> turbulent length scales
- **Applicability:** Laminar flames, Direct Numerical Simulation (DNS)
- **Limitations:** ไม่เหมาะกับ industrial turbulent flames (overly expensive)

**When is Direct Integration Valid?**

1. **Laminar flows:** Re < 2300 (pipes), local Re in flame zone
2. **DNS:** All turbulent scales resolved (Δx < η_Kolmogorov)
3. **Validation cases:** Comparing with analytical solutions

**Physical Rationale for DNS:**
```
Turbulent energy cascade:
Integral scale (l) ──→ Taylor scale (λ) ──→ Kolmogorov scale (η)
   ↓                    ↓                     ↓
Energy-containing    Viscous              Dissipation
eddies               effects               range

DNS requirement: Δx < η → N_cells ~ (l/η)³ ~ Re^(9/4)
```

### Mathematical Formulation

**Governing Equations:**

Species conservation:

$$\frac{\partial (\rho Y_i)}{\partial t} + \nabla \cdot (\rho \mathbf{u} Y_i) = \nabla \cdot (\rho D_i \nabla Y_i) + \dot{\omega}_i$$

Energy conservation (enthalpy form):

$$\frac{\partial (\rho h)}{\partial t} + \nabla \cdot (\rho \mathbf{u} h) = \nabla \cdot \left(\frac{k}{c_p} \nabla h\right) + \frac{Dp}{Dt} + \dot{\omega}_h$$

where sensible enthalpy $h = \sum Y_i h_i(T) + \Delta h_f^0$

**Reaction Rate Computation:**

At **each cell**, solve chemistry ODE system:

$$\frac{dY_i}{dt} = \frac{\dot{\omega}_i(T, Y_j, p)}{\rho}, \quad i = 1, ..., N_{\text{species}}$$

$$\frac{dT}{dt} = \frac{1}{\rho c_v}\left(-\sum h_{f,i}^0 \dot{\omega}_i - \sum \int c_{p,i} dT \cdot \dot{\omega}_i\right)$$

**Arrhenius Rate Example:**

$$\dot{\omega}_i = k_f \prod_{\text{reactants}} Y_j^{\nu_j} - k_r \prod_{\text{products}} Y_k^{\nu_k}$$

$$k_f = A T^\beta \exp\left(-\frac{T_a}{T}\right)$$

where $A$ = pre-exponential factor, $T_a$ = activation temperature

### Implementation in OpenFOAM

**Basic Configuration:**

```cpp
// constant/combustionProperties
combustionModel laminar;

// Optional: adjust chemistry solver
chemistrySolver
{
    solver          stiff;          // stiff | nonStiff
    tolerance       1e-09;          // ODE tolerance
    maxIter         100;            // Max iterations per timestep
    
    // Time scale control
    cTau            0.05;           // Courant number for chemistry
    eps             0.01;           // Small time step threshold
}

// Chemistry model
chemistryModel
{
    type            rhoReactionThermo;
    mechanism       methane_22sp.dat;  // Chemistry mechanism file
}
```

**Advanced Options:**

```cpp
// For stiff chemistry (recommended)
chemistrySolver
{
    solver          stiff;
    method          Rosenbrock;     // Rosenbrock | Seulex | Rodas
    
    // Adaptive time stepping
    eps             0.001;          // Error tolerance
    minTemp         300;            // Minimum chemistry temperature
}

// Multirate methods (separate fast/slow chemistry)
multirate
{
    nFastSpecies    5;              // Number of fast species
    fastMode        steadyState;    // steadyState | analytical
}
```

**Solver Compatibility:**

```
Laminar model works with:
- reactingFoam (compressible)
- rhoReactingFoam (compressible, rho-based)
- rhoReactingBuoyantFoam (buoyancy)
- srfoReactingFoam (density-based, compressible)
```

### When to Use

| Scenario | Why Laminar? | Computational Cost |
|----------|--------------|-------------------|
| **DNS studies** | Resolve all turbulent scales | O(10⁶) CPU hours for 3D |
| **Laminar flame validation** | Compare with analytical solutions | O(1) CPU hours |
| **1D flames** | Flame speed calculations, flame structure | Minutes |
| **Small Bunsen burners** | Low Reynolds number (Re < 100) | O(1-10) CPU hours |
| **Fundamental research** | Study detailed flame structure | High |

### Limitations

1. **Computational cost:**
   - ODE solve at every cell, every timestep
   - Stiff chemistry → small chemical time scales (τ_chem ~ 10⁻⁹ s)
   - Maximum Δt limited by chemistry, not CFL

2. **Stiff chemistry:**
   ```
   Methane mechanism (22 species):
   - Fast species: H, O, OH → τ ~ 10⁻⁹ s
   - Slow species: CH4, CO2 → τ ~ 10⁻⁴ s
   - Stiffness ratio: ~10⁵
   → Requires implicit ODE solver
   ```

3. **No turbulent closure:**
   - Ignores turbulence fluctuations on reaction rates
   - For RANS/LES: $\overline{\dot{\omega}_i} \neq \dot{\omega}_i(\tilde{T}, \tilde{Y}_j)$
   - **Never use laminar model for RANS/LES turbulent flames**

### Validation Example

**1D Premixed Flame:**

```cpp
// Initial conditions (flat flame)
T     300 2000;        // Temperature profile (unburnt → burnt)
CH4   0.055 0;         // Methane mass fraction
O2    0.23 0;          // Oxygen
N2    0.715 0.77;      // Nitrogen
CO2   0 0.15;          // Carbon dioxide
H2O   0 0.12;          // Water

// Boundary conditions
inlet
{
    type            fixedValue;
    value           uniform (300 0.055 0.23 0.715 0 0);  // Unburnt
}

outlet
{
    type            zeroGradient;  // Allow flame propagation
}
```

**Expected Output:**
- Laminar flame speed: $S_L \approx 0.38$ m/s (methane-air, φ=1)
- Flame thickness: $\delta_L \approx 0.5$ mm
- Adiabatic flame temperature: $T_{ad} \approx 2220$ K

---

## 3. Eddy Dissipation Concept (EDC)

### Physical Principles

**EDC (Eddy Dissipation Concept)** พัฒนาโดย Magnussen (1981), refined 2005-2016:

- **Core idea:** Turbulent mixing controls reaction rate through **fine structures**
- **Hypothesis:** Reactions occur in **intermittent fine structures** where mixing is most intense
- **Analogy:** Eddy dissipation rate ε determines volume fraction of reacting regions
- **Origin:** Extension of Eddy Dissipation Model (EDM) to finite-rate chemistry

**Historical Development:**
```
1976: Eddy Dissipation Model (EDM)
       - Infinite rate chemistry assumption
       - Reaction rate ∝ min(fuel, oxidizer)
       
1981: Eddy Dissipation Concept (EDC)
       - Finite-rate chemistry extension
       - Fine structure concept
       
2005: Revised EDC (Magnussen)
       - Improved constants
       
2016: EDC v2016 (OpenFOAM default)
       - Optimized for wide Da range
       - Better extinction predictions
```

**Physical Picture:**
```
Turbulent Flow = Fine Structures (reacting) + Surroundings (non-reacting)
     ↓                          ↓
Small volume, intense mixing  Bulk flow, transport only
(γ* fraction of total)        ((1-γ*) fraction)

Fine Structure Properties:
- Size: η (Kolmogorov scale)
- Time scale: τ* (residence time)
- State: Perfectly Stirred Reactor (PSR)
```

**Two-Zone Concept:**

1. **Fine Structures (γ*):**
   - Small volume fraction (~1-10%)
   - Intense mixing, high dissipation
   - Chemical reactions occur here
   - Modeled as PSR

2. **Surroundings (1-γ*):**
   - Bulk fluid
   - Transport-dominated
   - No chemical reactions

### Mathematical Formulation

**1. Fine Structure Volume Fraction (γ*):**

$$\gamma^* = C_\gamma \left(\frac{\nu \varepsilon}{k^2}\right)^{1/4}$$

where:
- $C_\gamma$ = model coefficient (default: 2.1377 for v2016)
- $k$ = turbulent kinetic energy [m²/s²]
- $\varepsilon$ = dissipation rate [m²/s³]
- $\nu$ = kinematic viscosity [m²/s]

**Physical interpretation:**
- High $\varepsilon$ → small, intense fine structures → larger $\gamma^*$
- Low $k$ → less turbulent energy → smaller $\gamma^*$

**Typical values:**
- Industrial furnace: $\gamma^* \approx 0.02-0.05$ (2-5%)
- Gas turbine: $\gamma^* \approx 0.05-0.10$ (5-10%)
- Jet flame: $\gamma^* \approx 0.03-0.08$ (3-8%)

**2. Fine Structure Residence Time (τ*):**

$$\tau^* = C_\tau \left(\frac{\nu}{\varepsilon}\right)^{1/2}$$

where $C_\tau$ = model coefficient (default: 0.4082 for v2016)

**Physical meaning:**
- Time fluid spends in fine structure
- Controls chemical conversion rate
- Related to Kolmogorov time scale: $\tau_\eta = (\nu/\varepsilon)^{1/2}$

**Typical values:**
- $\tau^* \approx 0.4 \times 10^{-3} - 10^{-2}$ s (industrial flames)

**3. Effective Reaction Rate:**

$$\overline{\dot{\omega}_i} = \frac{\gamma^*}{\tau^*} \rho \left( Y_i^* - \tilde{Y}_i \right)$$

where:
- $Y_i^*$ = fine structure composition (from PSR solution)
- $\tilde{Y}_i$ = mean (Favre-averaged) composition
- $\rho$ = density

**Algorithm:**

1. **Compute fine structure properties:**
   - $\gamma^* = C_\gamma (\nu \varepsilon / k^2)^{1/4}$
   - $\tau^* = C_\tau (\nu / \varepsilon)^{1/2}$

2. **Solve PSR in fine structure:**
   - Steady-state chemistry at $(T^*, Y_i^*)$
   - Residence time $\tau^*$
   - Input: mean composition $\tilde{Y}_i$

3. **Calculate effective rate:**
   - $\overline{\dot{\omega}_i} = (\gamma^* / \tau^*) \rho (Y_i^* - \tilde{Y}_i)$

4. **Update mean composition:**
   - Transport equation with source term $\overline{\dot{\omega}_i}$

**PSR Solution in Fine Structure:**

Steady-state PSR equation:

$$\frac{Y_i^* - \tilde{Y}_i}{\tau^*} = \frac{\dot{\omega}_i(T^*, Y_j^*)}{\rho^*}$$

Solve iteratively for $(T^*, Y_j^*)$ using ODE solver.

**4. Effective Temperature:**

Energy balance in fine structure:

$$\frac{T^* - \tilde{T}}{\tau^*} = -\frac{1}{\rho^* c_{p,v}} \sum h_{f,i}^0 \dot{\omega}_i(T^*, Y_j^*)$$

### Implementation in OpenFOAM

**Basic Configuration:**

```cpp
// constant/combustionProperties
combustionModel EDC;

EDCCoeffs
{
    // EDC version
    version         v2016;    // v2016 (default) | v2005 | original
    
    // Optional: custom coefficients (v2016 uses optimized defaults)
    // Cgamma         2.1377;  // Fine structure constant
    // Ctau           0.4082;  // Residence time constant
    
    // Reacting fraction (advanced)
    // C1             2.1377;  // Same as Cgamma
    // C2             0.4082;  // Same as Ctau
}

// Chemistry model
chemistryModel
{
    type            rhoReactionThermo;
    
    // Reduced mechanism recommended for EDC
    mechanism       reducedMechanism_22sp.dat;
    
    // Solver settings
    chemistrySolver
    {
        solver      stiff;
        tolerance   1e-09;
    }
}
```

**Version Comparison:**

| Version | Cγ | Cτ | Recommended For |
|---------|----|----|-----------------|
| **v2016** (default) | 2.1377 | 0.4082 | Wide Da range, industrial |
| **v2005** | 2.1377 | 0.4082 | High Da, fast chemistry |
| **original** | 2.1377 | 0.4082 | Legacy compatibility |

**Advanced Configuration:**

```cpp
EDCCoeffs
{
    version         v2016;
    
    // Fine structure model options
    Cgamma          2.1377;         // Fine structure volume fraction
    Ctau            0.4082;         // Residence time
    
    // PSR solution control
    PSRsolver
    {
        maxIter         10;         // Max PSR iterations
        tolerance       1e-06;      // PSR convergence tolerance
    }
    
    // Experimental: multi-stage EDC
    // nStages         3;              // Number of fine structure stages
    // stageDistribution 0.5 0.3 0.2; // Volume fraction per stage
}

// Turbulence model (required)
turbulence
{
    simulationType  RAS;        // RAS | LES
    
    RAS
    {
        RASModel        kEpsilon;
        turbulence      on;
        
        // k-ε coefficients (affect γ*, τ*)
        Cmu             0.09;
        C1              1.44;
        C2              1.92;
        sigmaEps        1.3;    // Affects ε prediction → γ*
    }
}
```

**Thermodynamics Configuration:**

```cpp
// constant/thermophysicalProperties
thermoType
{
    type            hePsiThermo;
    mixture         multiComponentMixture;
    transport       sutherland;
    thermo          janaf;
    energy          sensibleEnthalpy;
    equationOfState perfectGas;
    specie          specie;
}

mixture
{
    specie
    {
        nMoles          1;
        molWeight       28.96;  // Air equivalent
    }
    
    // Include all species in reduced mechanism
    // CH4 O2 N2 CO2 H2O H2 CO H OH H2O2 HO2 CH3 CH3O CH2O
    thermodynamics
    {
        // ... (NASA polynomial coefficients)
    }
}
```

### When to Use

| Application | Why EDC? | Typical Settings |
|-------------|----------|------------------|
| **Industrial furnaces** | Mixing-controlled combustion, high turbulence | Da ~ 0.1-1, γ* ~ 0.02-0.05 |
| **Gas turbines** | High turbulence intensity, non-premixed | Da ~ 0.5-2, γ* ~ 0.05-0.10 |
| **Diesel engines** | Non-premixed, high Ka, transient | Da ~ 0.1-10, vary with crank angle |
| **Jet flames** | Diffusion flames with strong turbulence | Da ~ 1-10, γ* ~ 0.03-0.08 |
| **Utility boilers** | Large scale, mixing-limited | Da < 1, γ* ~ 0.01-0.03 |

**Decision Criteria:**

Use EDC when:
1. **Turbulence intensity** high (u' > S_L)
2. **Mixing-controlled** regime (Da < 1 or Da ~ 1)
3. **No pre-computed tables** available
4. **Industrial applications** with limited validation data

Avoid EDC when:
1. **Laminar or low-turbulence** flames (use Laminar or Flamelet)
2. **Premixed flames** with well-defined S_L (use Xi)
3. **Very slow chemistry** (Da ≫ 1) (use PaSR or Laminar)

### Advantages

1. **Physical basis:**
   - Links reaction rate to turbulence dissipation
   - Theoretically grounded in turbulence phenomenology
   - Accounts for finite-rate chemistry (unlike EDM)

2. **Robustness:**
   - Works for wide range of Da numbers (0.01-100)
   - Handles extinction and ignition
   - Validated for many industrial applications

3. **No prior calculations:**
   - Unlike flamelet models (no pre-processing)
   - Direct integration with CFD solver
   - Easy to set up for new fuels

4. **LES-friendly:**
   - Resolved scales provide ε field
   - SGS models for k, ε (if using k-ε SGS)
   - Natural extension to LES

### Limitations

1. **Empirical constants:**
   - Cγ, Cτ tuned for specific applications
   - May need adjustment for:
     - Different fuels
     - Extreme pressures
     - Supersonic flows
   - **Recommendation:** Calibrate with experimental data

2. **Fine structure assumption:**
   - May not hold for all regimes:
     - Low Da: finite-rate effects important
     - High Ka: broken reaction zones
     - Very high Re: different fine structure dynamics
   - **Limit:** Validity boundary not clearly defined

3. **Computational cost:**
   - Requires chemistry solver for fine structures
   - PSR iteration at each cell
   - Cost: 0.5-1.0 × laminar (still significant)

4. **Grid sensitivity:**
   - Need sufficient resolution for ε field
   - ε depends on mesh quality (especially near walls)
   - **Recommendation:** y+ < 5 for wall-bounded flows

### Calibration Guidelines

**Step 1: Baseline Simulation**

```cpp
// Use default v2016 coefficients
EDCCoeffs
{
    version         v2016;
}
```

**Step 2: Compare with Experimental Data**

```
Key validation metrics:
- Flame temperature (T_max, T_profile)
- Species concentrations (CO, UHC, NOx)
- Flame length/shape
- Heat flux distribution
```

**Step 3: Adjust Coefficients**

If **underpredicting** reaction rates (flame too long):
```cpp
Cgamma          2.5;     // Increase reacting volume
```

If **overpredicting** reaction rates (flame too short/extinction not captured):
```cpp
Cgamma          1.8;     // Decrease reacting volume
Ctau            0.5;     // Increase residence time
```

**Step 4: Validate for Multiple Conditions**

```
Test matrix:
- Different equivalence ratios (φ = 0.7, 1.0, 1.3)
- Different flow rates (Re variations)
- Different fuels (if applicable)
```

---

## 4. Partially Stirred Reactor (PaSR)

### Physical Principles

**PaSR (Partially Stirred Reactor)** ตาม concept ของ Kolmogorov (1942) และ Chorny (1989):

- **Core idea:** Each computational cell = **mixture** of reacting PSR + non-reacting fluid
- **Hypothesis:** Mixing time $\tau_{\text{mix}}$ controls chemical conversion
- **Split:** Cell volume split into reacting fraction $\kappa$ and non-reacting $(1-\kappa)$
- **Advantage over EDC:** Single chemistry solve, adaptive reacting fraction

**Historical Background:**
```
1949: Well-Stirred Reactor (WSR) concept
      - Perfect mixing assumption
      - Single zone reactor
      
1980s: Partially Stirred Reactor (PaSR)
       - Two-zone concept
       - Reacting + non-reacting volumes
       
1990s: Integration with CFD (Chorny, 1989)
       - Cell-level PSR
       - Mixing time from turbulence
       
2000s: OpenFOAM implementation
       - Integration with rhoReactingFoam
       - LES applications
```

**Physical Picture:**
```
Computational Cell:
┌─────────────────────────────────────┐
│  Cell = κ × PSR + (1-κ) × Inert    │
│                                     │
│  ┌──────────┐      ┌─────────────┐  │
│  │  PSR     │      │   Inert     │  │
│  │  (κV)    │      │  ((1-κ)V)   │  │
│  │          │      │             │  │
│  │  Fast    │      │  Transport  │  │
│  │  Rxns    │      │  only       │  │
│  └──────────┘      └─────────────┘  │
│                                     │
│  Effective:                        │
│  ˙ω_i = κ × ˙ω_i(PSR)              │
└─────────────────────────────────────┘

κ depends on:
- Chemical time scale (τ_chem)
- Mixing time scale (τ_mix)
- κ = τ_chem / (τ_chem + τ_mix)
```

**Two-Zone Mass Transfer:**

Mass transfer rate between zones:
$$\dot{m} = \frac{\kappa (1-\kappa) \rho V}{\tau_{\text{mix}}}$$

**Key Differences from EDC:**

| Aspect | EDC | PaSR |
|--------|-----|------|
| **Zones** | Fine structures + surroundings | PSR + inert |
| **Volume fraction** | γ* (from ε) | κ (from Da) |
| **Chemistry solves** | Iterative PSR in fine structures | Single PSR |
| **Adaptivity** | Fixed (from k, ε) | Adaptive (from τ_chem) |
| **Computational cost** | Higher | Lower |

### Mathematical Formulation

**1. Mixing Time Scale:**

$$\tau_{\text{mix}} = C_{\text{mix}} \frac{k}{\varepsilon}$$

where:
- $C_{\text{mix}}$ = mixing constant (typically 0.1-0.5)
- $k$ = turbulent kinetic energy [m²/s²]
- $\varepsilon$ = dissipation rate [m²/s³]

**Physical interpretation:**
- Time scale for turbulent mixing at cell level
- Related to integral time scale: $\tau_t = k / \varepsilon$
- $C_{\text{mix}}$ accounts for:
  - Subgrid mixing (LES)
  - Molecular diffusion effects
  - Non-ideal mixing

**Typical values:**
- $\tau_{\text{mix}} \approx 0.1 \times (k/\varepsilon)$ (well-mixed)
- $\tau_{\text{mix}} \approx 0.5 \times (k/\varepsilon)$ (poorly mixed)

**2. Chemical Time Scale:**

$$\tau_{\text{chem}} = \left[ \frac{1}{Y_i} \frac{dY_i}{dt} \right]^{-1}_{\text{kinetics}}$$

Computed from chemical kinetics:

$$\tau_{\text{chem}} = \min_i \left( \frac{Y_i}{|\dot{\omega}_i|/\rho} \right)$$

or using maximum production rate:

$$\tau_{\text{chem}} = \frac{\text{fuel mass fraction}}{\text{fuel production rate}}$$

**Approximation for fast calculations:**
```cpp
// OpenFOAM implementation uses
τ_chem = max(τ_chem, i)  // Maximum over all species
```

**Typical values:**
- Methane-air (φ=1): $\tau_{\text{chem}} \approx 10^{-4} - 10^{-3}$ s
- Heptane: $\tau_{\text{chem}} \approx 10^{-5} - 10^{-4}$ s
- Hydrogen: $\tau_{\text{chem}} \approx 10^{-6} - 10^{-5}$ s (fast!)

**3. Reacting Volume Fraction:**

$$\kappa = \frac{\tau_{\text{chem}}}{\tau_{\text{chem}} + \tau_{\text{mix}}}$$

**Physical regimes:**

| Regime | Condition | κ | Physics |
|--------|-----------|----|---------|
| **Fast chemistry** | $\tau_{\text{chem}} \ll \tau_{\text{mix}}$ | $\kappa \rightarrow 1$ | Entire cell reacts, equilibrium |
| **Slow chemistry** | $\tau_{\text{chem}} \gg \tau_{\text{mix}}$ | $\kappa \rightarrow 0$ | Small reacting region, kinetically controlled |
| **Mixed** | $\tau_{\text{chem}} \sim \tau_{\text{mix}}$ | $\kappa \approx 0.5$ | Both mixing and kinetics important |

**Key insight:** κ automatically adjusts to local Damköhler number:
$$Da = \frac{\tau_{\text{mix}}}{\tau_{\text{chem}}} \rightarrow \kappa = \frac{1}{1 + Da}$$

**4. Effective Reaction Rate:**

$$\overline{\dot{\omega}_i} = \kappa \cdot \dot{\omega}_i(T^*, Y_j^*)$$

where $(T^*, Y_j^*)$ = PSR solution (steady-state chemistry)

**PSR Solution:**

Steady-state energy and species equations in PSR:

$$\frac{T^* - \tilde{T}}{\tau_{\text{res}}} = -\frac{1}{\rho c_v} \sum h_{f,i}^0 \dot{\omega}_i(T^*, Y_j^*)$$

$$\frac{Y_j^* - \tilde{Y}_j}{\tau_{\text{res}}} = \frac{\dot{\omega}_j(T^*, Y_k^*)}{\rho}$$

where $\tau_{\text{res}}$ = residence time in PSR

**Residence time in PaSR:**
$$\tau_{\text{res}} = \frac{\tau_{\text{mix}}}{\kappa} = \tau_{\text{chem}} + \tau_{\text{mix}}$$

### Implementation in OpenFOAM

**Basic Configuration:**

```cpp
// constant/combustionProperties
combustionModel PaSR;

PaSRCoeffs
{
    // Mixing model type
    mixingModel     simple;      // simple | kEpsilon | advanced
    
    // Mixing time constant
    Cmix            0.3;         // 0.1 (fast mixing) to 0.5 (slow mixing)
    
    // Chemical time scale calculation
    chemicalTimeScale   on;      // on | off (use constant τ_chem)
    
    // Optional: constant chemical time (if chemicalTimeScale = off)
    // tauChem         0.001;        // Constant τ_chem [s]
}
```

**Mixing Models:**

**1. Simple Mixing (default):**
```cpp
mixingModel     simple;
Cmix            0.3;         // τ_mix = Cmix × (k/ε)
```

**2. k-ε Based:**
```cpp
mixingModel     kEpsilon;
Cmix            0.3;         // Same as simple, but with k-ε validation checks
```

**3. Advanced (local mixing):**
```cpp
mixingModel     advanced;
Cmix            0.3;

// Advanced options
CmixCalc        local;         // Calculate locally (vs constant)
minTauMix       1e-05;         // Minimum τ_mix [s]
maxTauMix       0.1;           // Maximum τ_mix [s]
```

**Chemistry Configuration:**

```cpp
// constant/chemistryProperties
chemistryModel
{
    type            rhoReactionThermo;
    
    // Reduced mechanism recommended for PaSR
    mechanism       skeletal_16sp.dat;  // Faster than full mechanism
    
    // ODE solver settings
    chemistrySolver
    {
        solver          stiff;
        tolerance       1e-09;
        maxIter         100;
        
        // Time scale control
        cTau            0.05;
    }
}
```

**Recommended Mechanisms:**

| Application | Full Mechanism | Recommended Reduced | Species | Speedup |
|-------------|----------------|---------------------|---------|---------|
| **Methane** | GRI-Mech 3.0 (53 sp) | skeletal_16sp | 16 | 5-10× |
| **Heptane** | LLn (160 sp) | reduced_44sp | 44 | 10-20× |
| **Hydrogen** | H2 (9 sp) | (use full) | 9 | - |
| **Syngas** | CO/H2 (12 sp) | (use full) | 12 | - |

**Thermodynamics:**

```cpp
// constant/thermophysicalProperties
thermoType
{
    type            hePsiThermo;
    mixture         multiComponentMixture;
    transport       sutherland;
    thermo          janaf;
    energy          sensibleEnthalpy;
    equationOfState perfectGas;
    specie          specie;
}
```

**LES Configuration:**

```cpp
// constant/turbulenceProperties (for LES)
simulationType  LES;

LES
{
    LESModel        dynamicKEpsilon;
    turbulence      on;
    
    delta           cubeRootVol;    // Grid filter width
    
    // Subgrid-scale mixing
    // k, ε from SGS model → τ_mix
}
```

### When to Use

| Application | Why PaSR? | Typical Settings |
|-------------|----------|------------------|
| **Large combustion chambers** | Computational efficiency, adaptive | Cmix = 0.2-0.4 |
| **Flows with varying Da** | Adapts to local conditions | Cmix = 0.3 (default) |
| **Premixed + diffusion** | Handles mixed regimes | Cmix = 0.1-0.5 |
| **LES simulations** | Subgrid-scale modeling | Use LES SGS for τ_mix |
| **HCCI engines** | Autoignition, slow chemistry | Cmix = 0.4-0.5 |
| **Gas turbines (premixed)** | Moderate Da, large domain | Cmix = 0.2-0.3 |
| **Industrial furnaces** | Mixed regime | Cmix = 0.3-0.4 |

**Decision Criteria:**

Use PaSR when:
1. **Variable Da** across domain (some regions fast, some slow)
2. **Computational efficiency** critical (large domains)
3. **LES simulations** (natural SGS framework)
4. **Mixed regimes** (premixed + diffusion)

Avoid PaSR when:
1. **Laminar flames** (use Laminar)
2. **Purely premixed** with known S_L (use Xi)
3. **Purely mixing-controlled** (EDC may be better)

### Advantages

1. **Adaptive:**
   - Reacting fraction adjusts to local Da
   - κ → 1 for fast chemistry (equilibrium)
   - κ → 0 for slow chemistry (kinetically limited)
   - **Key advantage:** Single model for wide Da range

2. **Efficient:**
   - Single chemistry solve per cell (vs. EDC's fine structures)
   - No iteration for PSR (direct κ calculation)
   - Cost: 0.3-0.7 × laminar

3. **LES-friendly:**
   - Natural framework for SGS combustion
   - τ_mix from SGS turbulence model
   - κ represents subgrid reacting fraction

4. **Simple setup:**
   - Few parameters (Cmix only)
   - No pre-processing
   - Easy to calibrate

### Limitations

1. **Mixing constant:**
   - $C_{\text{mix}}$ requires calibration
   - Default 0.3 works for many cases
   - May need adjustment for:
     - Different fuels
     - Extreme pressures
     - Specific geometries

2. **PSR assumption:**
   - May not capture finite-rate effects accurately
   - Steady-state PSR may not represent transient chemistry
   - **Limitation:** Ignition/extinction hysteresis

3. **Stiff chemistry:**
   - Still needs robust ODE solver
   - Reduced mechanism recommended
   - Chemical time scale calculation can be expensive

4. **Grid dependency:**
   - τ_mix depends on k, ε (grid-sensitive)
   - Need sufficient resolution for turbulence

### Calibration Guidelines

**Step 1: Start with Default**

```cpp
Cmix            0.3;         // Default works for many cases
```

**Step 2: Analyze Da Distribution**

```bash
# Post-process Da field
postProcess -func "DaCalculator"  // Custom function object

# Da = τ_mix / τ_chem = (Cmix × k/ε) / τ_chem
```

**Step 3: Adjust Cmix**

If **Da too low** (overpredicting reactions):
```cpp
Cmix            0.5;         // Increase τ_mix → larger Da
```

If **Da too high** (underpredicting reactions):
```cpp
Cmix            0.2;         // Decrease τ_mix → smaller Da
```

**Step 4: Validate for Multiple Conditions**

```
Test matrix:
- Different loads (25%, 50%, 100%)
- Different equivalence ratios
- Different fuels (if applicable)
```

**Advanced Calibration:**

```cpp
mixingModel     advanced;
Cmix            0.3;
CmixCalc        local;         // Spatially varying Cmix

// Define Cmix field (e.g., from empirical correlation)
// Cmix(x,y,z) = f(turbulence intensity, strain rate)
```

---

## 5. Premixed Flame (Xi Model)

### Physical Principles

**Xi Model (Flame Surface Density Approach):**

- **Core idea:** Track **flame surface area** enhancement by turbulence
- **Key parameter:** $\Xi$ = flame wrinkling factor = actual flame area / projected area
- **Applicability:** **Premixed** turbulent flames only
- **Alternative name:** Flame Surface Density (FSD) model

**Historical Development:**
```
1950s: Damköhler hypothesis
       - Turbulent flame speed ∝ turbulent velocity
       
1970s: Flame surface density concept (Marble, Broadwell)
       - Track flame surface area evolution
       
1980s-90s: Xi transport equation (Cant, Pope, Weller)
          - wrinkling factor transport
          
2000s: OpenFOAM implementation (XiFoam)
       - Algebraic and transport Xi models
```

**Physical Picture:**
```
Laminar Flame:
  |  Flat flame front
  |  Flame area = projected area
  |  S_T = S_L (flame speed = laminar speed)

Turbulent Flame:
  ~~~ Wrinkled/contorted front
  ~~~ Flame area > projected area
  ~~~ S_T = Xi × S_L (flame speed increased)

Xi = A_actual / A_projected
    = wrinkling factor
    = flame surface density / flame thickness
```

**Key Concepts:**

1. **Flame Surface Density ($\Sigma$):**
   $$\Sigma = \frac{A_{\text{flame}}}{V_{\text{cell}}}$$
   - Flame area per unit volume
   - Units: [m²/m³] = [m⁻¹]

2. **Flame Wrinkling Factor ($\Xi$):**
   $$\Xi = \frac{A_{\text{actual}}}{A_{\text{projected}}}$$
   - Dimensionless
   - Xi > 1 for turbulent flames

3. **Turbulent Flame Speed ($S_T$):**
   $$S_T = \Xi \times S_L$$
   - Enhanced by turbulence
   - Depends on u' (turbulent intensity)

**Turbulence Effects on Flame:**

| Turbulence Level | Effect on Flame | Xi | Flame Structure |
|------------------|-----------------|----|-----------------|
| **Weak** (u' < SL) | Small wrinkles | Xi ≈ 1-1.5 | Wrinkled flamelets |
| **Moderate** (u' ~ SL) | Increased surface area | Xi ≈ 1.5-3 | Corrugated flamelets |
| **Strong** (u' >> SL) | Distributed reaction | Xi ≫ 3 | Thin reaction zones |

### Mathematical Formulation

**1. Flame Surface Density Transport Equation:**

$$\frac{\partial (\rho \Sigma)}{\partial t} + \nabla \cdot (\rho \mathbf{u} \Sigma) = \nabla \cdot \left(\frac{\mu_t}{Sc_\Sigma} \nabla \Sigma\right) + \rho S_L \sigma \Xi$$

where:
- $\Sigma$ = flame surface density [m⁻¹]
- $S_L$ = laminar flame speed [m/s]
- $\sigma$ = flame stretch rate [s⁻¹]
- $\Xi$ = wrinkling factor [-]
- $Sc_\Sigma$ = Schmidt number for Σ transport

**Physical meaning of terms:**
- **LHS:** Rate of change + advection of flame surface
- **RHS term 1:** Diffusive transport (turbulent diffusion)
- **RHS term 2:** Source term (flame surface production by wrinkling)

**2. Xi Transport (Weller model):**

$$\frac{\partial (\rho \Xi)}{\partial t} + \nabla \cdot (\rho \mathbf{u} \Xi) = \nabla \cdot (D_t \nabla \Xi) + \rho \alpha \Xi \frac{u'}{S_L} - \rho \beta \frac{S_L}{\delta_L} (\Xi - 1)$$

where:
- $D_t$ = turbulent diffusivity [m²/s]
- $u'$ = turbulent velocity fluctuation [m/s]
- $\delta_L$ = laminar flame thickness [m]
- $\alpha$ = wrinkling production coefficient [-]
- $\beta$ = wrinkling destruction coefficient [-]

**Physical interpretation:**
- **Production term:** $\alpha \Xi (u'/S_L)$ — turbulence creates wrinkles
- **Destruction term:** $\beta (S_L/\delta_L) (\Xi - 1)$ — flame propagation reduces wrinkles
- **Balance:** $\Xi$ reaches steady state when production = destruction

**3. Reaction Rate:**

$$\dot{\omega}_T = \rho_u S_L \Sigma = \rho_u S_L \frac{\Xi}{\delta_L}$$

where:
- $\rho_u$ = unburnt gas density [kg/m³]
- $\dot{\omega}_T$ = fuel consumption rate [kg/(m³·s)]

**Alternative formulation (progress variable approach):**

$$\dot{\omega}_c = \rho_u S_T |\nabla c| = \rho_u (\Xi S_L) |\nabla c|$$

where $c$ = progress variable (0 = unburnt, 1 = burnt)

**4. Laminar Flame Properties:**

**Laminar flame speed ($S_L$):**
$$S_L = S_{L,0} \left(\frac{T_u}{T_{u,0}}\right)^\alpha \left(\frac{p}{p_0}\right)^\beta$$

where:
- $S_{L,0}$ = reference flame speed [m/s]
- $T_u$ = unburnt temperature [K]
- $p$ = pressure [Pa]
- $\alpha, \beta$ = exponents (typically α ≈ 2, β ≈ -0.5)

**Laminar flame thickness ($\delta_L$):**
$$\delta_L = \frac{D}{S_L} = \frac{\lambda}{\rho c_p S_L}$$

where:
- $D$ = thermal diffusivity [m²/s]
- $\lambda$ = thermal conductivity [W/(m·K)]
- $c_p$ = specific heat [J/(kg·K)]

**5. Regime Classification (Borghi Diagram):**

| Regime | Ka | Xi Behavior | Flame Structure |
|------------------|-------------|-----------------|
| **Wrinkled flamelets** | ≪1 | Xi ≈ 1-1.5 | Flame intact, surface wrinkled |
| **Corrugated flamelets** | <1 | Xi ≈ 1.5-3 | Strong wrinkling |
| **Thin reaction zones** | 1-100 | Xi ≈ 3-10 | Inner layer thinned |
| **Broken reaction zones** | >100 | Xi ≫ 10 | Distributed reaction |

**Model validity:** Xi model valid for Ka < 100 (corrugated flamelets regime)

### Implementation in OpenFOAM

**Basic Configuration:**

```cpp
// constant/combustionProperties
combustionModel  Xi;

XiCoeffs
{
    // Flame wrinkling model
    XiModel         transport;     // transport | algebraic | correlation
    
    // Shape parameters
    XiShapeCoeff    0.8;           // Flame shape parameter (0.5-1.5)
    XiCoef          0.6;           // Model coefficient
    
    // Schmidt number for Xi transport
    Sc              0.7;           // Turbulent Schmidt number
    
    // Correlation options (if XiModel = correlation)
    // correlationType    Gulder;     // Gulder | Peters | Muppala
    
    // Optional: laminar flame speed model
    SLModel          polynomial;   // polynomial | correlation | table
}
```

**Xi Model Types:**

**1. Transport Model (default):**
```cpp
XiModel         transport;

// Solves transport equation for Xi
// Recommended for: general premixed turbulent flames
```

**2. Algebraic Model:**
```cpp
XiModel         algebraic;
XiCoef          0.6;

// Xi calculated algebraically from u'/SL
// Faster, but less accurate for transient cases
// Xi = 1 + XiCoef × (u' / SL)
```

**3. Correlation Model:**
```cpp
XiModel         correlation;
correlationType    Gulder;     // Gulder | Peters | Muppala

// Uses empirical correlation for turbulent flame speed
// ST/SL = f(u'/SL, l/δL)
```

**Correlation Examples:**

**Gülder Correlation:**
$$\frac{S_T}{S_L} = 1 + \alpha \left(\frac{u'}{S_L}\right)^n \left(\frac{l}{\delta_L}\right)^m$$

where α ≈ 0.5-1.0, n ≈ 0.5-1.0, m ≈ 0.3-0.5

**Laminar Flame Speed Model:**

```cpp
// Option 1: Polynomial (default)
SLModel          polynomial;

// constant/SLProperties
SLCoeffs
{
    // Methane-air at φ = 1.0
    TRef            300;           // Reference temperature [K]
    pRef            101325;        // Reference pressure [Pa]
    SLRef           0.38;          // Reference flame speed [m/s]
    
    // Temperature exponent
    alpha           2.0;           // S_L ∝ T^α
    
    // Pressure exponent
    beta            -0.5;          // S_L ∝ p^β
    
    // Equivalence ratio dependence (optional)
    phiDependence   polynomial;
    phiCoeffs       (0 1.0 -0.2);  // Polynomial coefficients
}

// Option 2: Table (from detailed calculations)
SLModel          table;
SLTable          "constant/SLTable.dat";

// SLTable.dat format:
// T [K]  p [Pa]  phi   SL [m/s]
// 300    101325  0.8   0.25
// 300    101325  1.0   0.38
// 300    101325  1.2   0.32
```

**Thermodynamics Configuration:**

```cpp
// constant/thermophysicalProperties
thermoType
{
    type            hePsiThermo;
    mixture         multiComponentMixture;
    transport       sutherland;
    thermo          janaf;
    energy          sensibleEnthalpy;
    equationOfState perfectGas;
    specie          specie;
}

// For Xi model: need unburnt/burnt states
unburnt
{
    T               300;            // Unburnt temperature
    p               101325;         // Pressure
    CH4             0.055;          // Methane (φ=1)
    O2              0.23;
    N2              0.715;
}

burnt
{
    T               2220;           // Adiabatic flame temperature
    p               101325;
    CO2             0.15;
    H2O             0.12;
    N2              0.73;
}
```

**Solver Usage:**

```bash
# XiFoam solver
XiFoam

# Or with reactingFoam
rhoReactingFoam -combustionModel Xi
```

**Boundary Conditions:**

```cpp
// 0/boundaryField

inlet
{
    type            fixedValue;
    value           uniform 0;     // c = 0 (unburnt)
}

walls
{
    type            zeroGradient;  // Allow flame propagation
}

outlet
{
    type            inletOutlet;
    inletValue      uniform 1;     // c = 1 if backflow
    value           uniform 0;
}
```

### When to Use

| Application | Why Xi? | Typical Settings |
|-------------|---------|------------------|
| **Gas engines (SI)** | Premixed combustion, flame tracking | XiModel = transport, SLModel = polynomial |
| **Premixed burners** | Flame propagation tracking | XiModel = algebraic (faster) |
| **Explosion modeling** | Flame speed prediction | XiModel = transport, XiCoef = 0.6-1.0 |
| **LES of premixed flames** | Subgrid flame surface | Use LES with Xi transport |
| **Gas turbines (premixed)** | Lean premixed combustion | XiModel = correlation |

**Decision Criteria:**

Use Xi when:
1. **Premixed combustion** (fuel+air premixed)
2. **Well-defined laminar flame speed** ($S_L$ known)
3. **Flame propagation** important
4. **Moderate Ka** (< 100, corrugated flamelets)

Avoid Xi when:
1. **Diffusion flames** (use flamelet or EDC)
2. **Partially premixed** (use PaSR)
3. **High Ka** (> 100, broken reaction zones)
4. **Unknown $S_L$** (requires detailed chemistry)

### Advantages

1. **Efficient:**
   - No chemistry ODE integration (flame speed correlations)
   - Fast: 0.1-0.3 × laminar model
   - Suitable for large domains

2. **Physical:**
   - Explicitly tracks flame surface evolution
   - Based on turbulence-chemistry interaction theory
   - Captures flame wrinkling physics

3. **Fast:**
   - No chemistry mechanism needed (if $S_L$ from correlations)
   - Quick parametric studies
   - Transient simulations

4. **Validated:**
   - Extensive validation for SI engines
   - Well-established for premixed flames

### Limitations

1. **Premixed only:**
   - Not applicable to diffusion flames
   - Not applicable to partially premixed flames
   - **Alternative:** Use flamelet (diffusion) or PaSR (mixed)

2. **Flame speed dependency:**
   - Requires accurate $S_L$ data (pressure, temperature, equivalence ratio)
   - Inaccurate $S_L$ → wrong flame position
   - **Challenge:** $S_L$ for complex fuels (multi-component)

3. **Model constants:**
   - Xi coefficients need calibration
   - $\alpha, \beta$ in transport equation
   - **Recommendation:** Calibrate with experimental flame data

4. **Regime limitations:**
   - Breaks down for high Ka (broken reaction zones)
   - Valid for Ka < 100
   - **Alternative:** Use PaSR for high Ka

### Validation Example

**Case: Premixed turbulent Bunsen flame**

```
Parameters:
- Fuel: CH4 + air (φ = 0.9)
- Bulk velocity: U = 5 m/s
- Turbulence intensity: u' = 1 m/s
- Laminar flame speed: SL = 0.35 m/s
- Flame thickness: δL = 0.5 mm

Damköhler number: Da = SL / u' = 0.35 / 1.0 = 0.35
Karlovitz number: Ka ≈ 5 (thin reaction zones regime)

Expected Xi: 1.5-2.5 (from correlations)
```

**Expected Results:**
- Flame cone angle: θ ≈ 30-45°
- Turbulent flame speed: ST ≈ 0.5-0.9 m/s
- Flame brush thickness: δT ≈ 5-10 mm

---

## 6. Flamelet Models

### Physical Principles

**Flamelet Approach:**

- **Core idea:** Flame = **ensemble of 1D laminar flames** embedded in turbulent flow
- **Hypothesis:** Flame thickness $\delta_L \ll$ turbulent length scale $l_t$
- **Key concept:** **Flamelet library** parameterized by mixture fraction $Z$ and scalar dissipation rate $\chi$
- **Advantage:** **Very fast** — no chemistry integration during CFD (table lookup)

**Historical Background:**
```
1970s: Flamelet concept (Peters, Williams)
       - Counter-flow diffusion flames
       - Thin flame assumption
       
1980s: Flamelet libraries
       - Parameterization by Z, χ
       - Tabulation approach
       
1990s: PDF integration
       - Statistical treatment of Z fluctuations
       - Beta-PDF integration
       
2000s: OpenFOAM implementation
       - flameletFoam solver
       - FGM (Flamelet Generated Manifolds)
```

**Physical Picture:**
```
Turbulent Flame = Collection of 1D Flamelets
     ↓                         ↓
Counter-current diffusion flames  Strained laminar flames

Each flamelet: 1D diffusion flame
Fuel  →  ←  Oxidizer
  ↓           ↓
Reaction zone at Z = Zst

Turbulent flow:
- Each point has local (Z, χ)
- Map to flamelet library
- Retrieve Y_i(Z, χ), T(Z, χ)
```

**Key Concepts:**

1. **Mixture Fraction ($Z$):**
   $$Z = \frac{Z_{\text{fuel}} - Z_{\text{oxidizer}}}{Z_{\text{fuel}}^{\text{st}} - Z_{\text{oxidizer}}}$$
   - $Z = 1$: pure fuel
   - $Z = 0$: pure oxidizer
   - $Z = Z_{\text{st}}$: stoichiometric mixture

2. **Scalar Dissipation Rate ($\chi$):**
   $$\chi = 2D |\nabla Z|^2$$
   - Measure of local mixing rate
   - Units: [s⁻¹]
   - Analogous to strain rate

3. **Flamelet Library:**
   $$Y_i = Y_i(Z, \chi), \quad T = T(Z, \chi), \quad \rho = \rho(Z, \chi)$$
   - Pre-computed table
   - 2D lookup: $(Z, \chi) \rightarrow (Y_i, T, \rho)$

**Flamelet Regime:**

| Condition | Meaning | Validity |
|-----------|---------|----------|
| **Da > 10** | Fast chemistry | Flamelet valid |
| **Ka < 100** | Flame intact | Flamelet valid |
| **δL << l_t** | Thin flame | Flamelet valid |

### Mathematical Formulation

**1. Mixture Fraction Transport:**

$$\frac{\partial (\rho Z)}{\partial t} + \nabla \cdot (\rho \mathbf{u} Z) = \nabla \cdot \left(\frac{\mu_t}{Sc_t} \nabla Z\right)$$

**Boundary conditions:**
- $Z = 1$ at fuel inlet
- $Z = 0$ at oxidizer inlet
- $Z \in [0, 1]$ in domain

**2. Mixture Fraction Variance ($\widetilde{Z''^2}$):**

$$\frac{\partial (\rho \widetilde{Z''^2})}{\partial t} + \nabla \cdot (\rho \mathbf{u} \widetilde{Z''^2}) = \nabla \cdot \left(\frac{\mu_t}{Sc_t} \nabla \widetilde{Z''^2}\right) + 2 \frac{\mu_t}{Sc_t} |\nabla \tilde{Z}|^2 - \rho \chi$$

**3. Scalar Dissipation Rate ($\chi$):**

**Definition:**
$$\chi = 2D \left(\frac{\partial Z}{\partial x}\right)^2$$

**Modeled in RANS:**
$$\tilde{\chi} = C_\chi \frac{\varepsilon}{k} \widetilde{Z''^2}$$

where $C_\chi \approx 2.0$

**4. Flamelet Equations (steady):**

**Species equation in mixture fraction space:**
$$\rho \frac{\partial Y_i}{\partial t} - \rho \frac{\chi}{2} \frac{\partial^2 Y_i}{\partial Z^2} = \dot{\omega}_i$$

**Energy equation:**
$$\rho \frac{\partial T}{\partial t} - \rho \frac{\chi}{2} \frac{\partial^2 T}{\partial Z^2} = -\sum h_{f,i}^0 \dot{\omega}_i$$

**Steady-state solution:**
$$\rho \frac{\chi}{2} \frac{d^2 Y_i}{dZ^2} = -\dot{\omega}_i$$

**5. Flamelet Library:**

$$Y_i = Y_i(Z, \chi_{\text{st}}), \quad T = T(Z, \chi_{\text{st}})$$

where $\chi_{\text{st}}$ = scalar dissipation at stoichiometric mixture

**Parameterization:**
- $Z \in [0, 1]$ — mixture fraction
- $\chi_{\text{st}} \in [\chi_{\text{min}}, \chi_{\text{quench}}]$ — scalar dissipation rate
- $\chi_{\text{quench}}$ = quenching scalar dissipation (flame extinction)

**6. PDF Integration (for RANS):**

**Favre-averaged species mass fraction:**
$$\tilde{Y}_i = \int_0^1 \int_0^{\chi_{\text{max}}} Y_i(Z, \chi) \tilde{P}(Z, \chi) \, d\chi \, dZ$$

**Beta-PDF for mixture fraction:**
$$\tilde{P}(Z) = \frac{Z^{\alpha-1} (1-Z)^{\beta-1}}{B(\alpha, \beta)}$$

where:
- $\alpha = \tilde{Z} \left(\frac{\tilde{Z}(1-\tilde{Z})}{\widetilde{Z''^2}} - 1\right)$
- $\beta = (1-\tilde{Z}) \left(\frac{\tilde{Z}(1-\tilde{Z})}{\widetilde{Z''^2}} - 1\right)$
- $B(\alpha, \beta)$ = Beta function

**Delta-PDF for scalar dissipation:**
$$\tilde{P}(\chi) = \delta(\chi - \tilde{\chi})$$

**Simplified integration:**
$$\tilde{Y}_i = \int_0^1 Y_i(Z, \tilde{\chi}) \tilde{P}(Z) \, dZ$$

### Implementation in OpenFOAM

Flamelet models require **two-stage setup**:

**Stage 1: Generate Flamelet Library**

**Using FlameMaster (external tool):**

```bash
# FlameMaster input file
flamelet methane_diffusion.dat

# Parameters
FUEL CH4
OXIDIZER O2 N2 0.21 0.79
P 101325
T_FUEL 300
T_OXIDIZER 300

# Scalar dissipation range
CHI_ST 0.1 1 10 100 500 1000  # [s^-1]

# Output
OUTPUT flameletLibrary.dat
```

**Using OpenFOAM utilities:**

```bash
# Use flamelet generation utility
flameletGen

# Input parameters
-m mechanism.dat     # Chemistry mechanism
-Zmin 0              # Minimum mixture fraction
-Zmax 1              # Maximum mixture fraction
-nZ 50               # Number of Z points
-chiStMin 0.1        # Minimum scalar dissipation [s^-1]
-chiStMax 1000       # Maximum scalar dissipation [s^-1]
-nChi 20             # Number of chi points
```

**Output: `constant/flameletLibrary.dat`**

```
# Format: Z  chi_st  Y_CH4  Y_O2  Y_CO2  Y_H2O  T  rho
0.000  0.1    0.000  0.233  0.000  0.000  300   1.18
0.000  1.0    0.000  0.233  0.000  0.000  300   1.18
...
0.055  0.1    0.000  0.000  0.150  0.120  2220  0.17
0.055  1.0    0.000  0.020  0.130  0.100  2000  0.19
...
1.000  0.1    1.000  0.000  0.000  0.000  300   0.65
1.000  1.0    1.000  0.000  0.000  0.000  300   0.65
```

**Stage 2: OpenFOAM Configuration**

```cpp
// constant/combustionProperties
combustionModel flamelet;

flameletCoeffs
{
    // Flamelet library file
    flameletLibrary  "constant/flameletLibrary.dat";
    
    // Parameterization
    variable         Z chiSt;      // Z chiSt | Z chi
    
    // Interpolation method
    interpolationScheme linear;    // linear | spline
    
    // Table dimensions
    nZ               50;           // Mixture fraction points
    nChi             20;           // Scalar dissipation points
    
    // PDF integration for turbulence (RANS)
    pdfIntegration   true;
    pdfType          beta;         // beta | delta
    
    // Optional: variance equation
    Zvariance        on;           // Solve for Z''^2
}
```

**Thermodynamics Configuration:**

```cpp
// constant/thermophysicalProperties
thermoType
{
    type            hePsiFlameletThermo;    // Specialized thermo for flamelets
    flameletLibrary constant/flameletLibrary.dat;
    
    // Alternative: use multicomponent thermo with lookup
    // type            hePsiThermo;
    // mixture         flameletMixture;
}
```

**Mixture Fraction Boundary Conditions:**

```cpp
// 0/Z

fuelInlet
{
    type            fixedValue;
    value           uniform 1;     // Pure fuel
}

airInlet
{
    type            fixedValue;
    value           uniform 0;     // Pure air
}

walls
{
    type            zeroGradient;
}

outlet
{
    type            inletOutlet;
    inletValue      uniform 0;
    value           uniform 0;
}
```

**Solver Usage:**

```bash
# Flamelet solver
flameletFoam

# Or with reactingFoam
rhoReactingFoam -combustionModel flamelet
```

### When to Use

| Application | Why Flamelet? | Typical Settings |
|-------------|---------------|------------------|
| **Gas turbine combustors** | Diffusion flames, high Da | nZ = 50, nChi = 20 |
| **Jet flames (non-premixed)** | Well-established methodology | PDF integration = on |
| **Fast CFD** | No chemistry integration (lookup) | Linear interpolation |
| **Parametric studies** | Quick exploration of conditions | Vary χ_st range |
| **Diesel engines** | Non-premixed, high pressure | High-Z resolution |

**Decision Criteria:**

Use flamelet when:
1. **Diffusion flames** (fuel+air mix during combustion)
2. **High Da** (> 10, fast chemistry)
3. **Moderate Ka** (< 100, flame intact)
4. **Computational efficiency** critical
5. **Detailed chemistry** desired (in library)

Avoid flamelet when:
1. **Premixed flames** (use Xi or premixed flamelet)
2. **Low Da** (< 1, slow chemistry) (use PaSR or laminar)
3. **High Ka** (> 100, broken reaction zones) (use PaSR)
4. **Strong unsteady effects** (flamelet may not capture transient)

### Advantages

1. **Very fast:**
   - No ODE integration (table lookup)
   - Cost: 0.01-0.05 × laminar model
   - **Fastest combustion model**

2. **Comprehensive chemistry:**
   - Can include detailed mechanisms (100+ species)
   - No penalty during CFD (pre-processed)
   - Accurate minor species (CO, UHC, NOx)

3. **Well-validated:**
   - Extensive literature for common fuels
   - Standard for gas turbine combustion
   - Benchmark data available

4. **Memory-efficient:**
   - Small library vs. full chemistry
   - 50 × 20 = 1000 points
   - Fast lookup

### Limitations

1. **Diffusion-dominated:**
   - Originally for non-premixed flames
   - Premixed flamelet models (FSD, FGM) more complex
   - **Alternative:** Use Xi for premixed

2. **Flamelet assumption:**
   - Breaks down for low Da, high Ka
   - Validity: Da > 10, Ka < 100
   - **Limit:** Not valid for broken reaction zones

3. **Pre-processing:**
   - Need to generate libraries (external tools)
   - Additional setup time
   - Need expertise in flamelet generation

4. **Regime-specific:**
   - Each regime needs different library:
     - Diffusion flamelet
     - Premixed flamelet (FGM)
     - Partially premixed flamelet
   - **Challenge:** Multiple flamelet libraries for mixed regimes

5. **Strain rate effects:**
   - Scalar dissipation χ must be modeled
   - χ from turbulence model (uncertain)
   - **Limitation:** Extinction prediction depends on accuracy of χ

### Flamelet-Generated Manifolds (FGM)

**Extension to Premixed Flames:**

```cpp
// constant/combustionProperties
combustionModel FGM;  // Flamelet Generated Manifolds

FGMCoeffs
{
    // FGM library
    flameletLibrary  "constant/FGMLibrary.dat";
    
    // Parameterization (different from diffusion flamelet)
    variable         c progressVariable;  // Progress variable c
    
    // Progress variable definition
    progressVariable
    {
        type            sum;
        species         (Y_CO2 Y_H2O);    // c = Y_CO2 + Y_H2O
    }
    
    // Table dimensions
    nZ               30;                   // Fewer Z points than diffusion
    nC               50;                   // Progress variable points
}
```

**FGM vs. Diffusion Flamelet:**

| Aspect | Diffusion Flamelet | FGM (Premixed) |
|--------|-------------------|----------------|
| **Parameters** | $(Z, \chi)$ | $(Z, c)$ or $(c, \dot{c})$ |
| **Flame type** | Non-premixed | Premixed/partially premixed |
| **Library** | Counter-flow diffusion flames | 1D premixed flames |
| **Cost** | Very fast | Very fast |

---

## 7. Selection Guide

### Decision Tree

```
Start
  ↓
Is the flame premixed?
  YES → Is Ka < 100?
         YES → Use Xi model (XiFoam)
         NO → Consider PaSR or EDC (high Ka)
  NO (diffusion/mixed) → What's Da?
         Da >> 1 (slow chemistry) → PaSR or laminar
         Da << 1 (fast chemistry) → EDC or flamelet
         Da ~ 1 (mixed) → PaSR or EDC
  ↓
Do you have detailed chemistry mechanism?
  YES → Can use laminar, EDC, PaSR, flamelet
  NO → Use flamelet (pre-computed) or Xi (correlations)
  ↓
Computational budget?
  Limited → Flamelet or Xi
  Moderate → PaSR
  High → EDC or laminar
```

### Quantitative Selection Matrix

| Regime | Da | Ka | Flame Type | Recommended Model | Rationale |
|--------|----|----|------------|-------------------|-----------|
| **Laminar flame** | - | - | Laminar | Laminar | Direct integration |
| **Corrugated flamelets** | >1 | <1 | Premixed | Xi, flamelet | Flame surface tracking |
| **Thin reaction zones** | ~1 | 1-100 | Premixed/mixed | EDC, PaSR | Mixing-kinetics interaction |
| **Broken reaction zones** | ~1 | >100 | Premixed | PaSR | Well-stirred regime |
| **Diffusion flame (fast)** | <1 | - | Non-premixed | Flamelet, EDC | Mixing-controlled |
| **Diffusion flame (slow)** | >1 | - | Non-premixed | PaSR, laminar | Kinetically-controlled |
| **Industrial furnace** | ~1 | >10 | Mixed | EDC | Proven industrial use |
| **Gas engine (SI)** | >1 | <10 | Premixed | Xi | Premixed flame tracking |
| **Gas turbine (premixed)** | ~1 | 1-50 | Premixed | Xi, flamelet (FGM) | Flame surface or manifolds |
| **Gas turbine (diffusion)** | <1 | - | Non-premixed | Flamelet, EDC | Mixing-controlled |
| **Diesel engine** | 0.1-10 | 10-100 | Diffusion | EDC, PaSR | Transient, mixed regime |
| **HCCI engine** | ≫1 | <1 | Premixed (autoignition) | Laminar, PaSR | Slow chemistry |
| **Jet flame (CH4/air)** | ~1 | 1-10 | Non-premixed | Flamelet, EDC | Well-studied |
| **Explosion** | ~1 | >100 | Premixed | PaSR | Well-mixed regime |

### Solver Compatibility

| Model | OpenFOAM Solver | Thermo Type | Key Requirements |
|-------|-----------------|-------------|------------------|
| **Laminar** | reactingFoam, rhoReactingFoam, rhoReactingBuoyantFoam | hePsiThermo | Chemistry mechanism |
| **EDC** | reactingFoam, rhoReactingFoam | hePsiThermo | Reduced mechanism |
| **PaSR** | reactingFoam, rhoReactingFoam | hePsiThermo | Reduced mechanism |
| **Xi** | XiFoam, psiReactingFoam | hePsiThermo | Laminar flame speed ($S_L$) |
| **Flamelet (diffusion)** | flameletFoam, rhoReactingFoam | hePsiFlameletThermo | Flamelet library |
| **Flamelet (FGM)** | rhoReactingFoam | hePsiThermo | FGM library |

### Model Selection Workflow

**Step 1: Characterize Flow**

```bash
# Calculate key dimensionless numbers
Da = (k/ε) / τ_chem          # Damköhler number
Ka = τ_chem / τ_η           # Karlovitz number
```

**Step 2: Identify Flame Type**

```
Premixed:      Fuel+air mixed before combustion
Non-premixed:  Fuel+air mix at flame front
Mixed:         Both regimes present
```

**Step 3: Consult Selection Matrix**

Use quantitative selection matrix above.

**Step 4: Verify Resources**

```
Computational budget:  CPU hours available
Memory:                RAM available
Expertise:             Familiarity with model
```

**Step 5: Validate**

```
Compare with experimental data
Sensitivity analysis on model constants
```

---

## Quick Reference

### Model-Specific Parameters Summary

| Model | Key Parameter | Physical Meaning | Typical Range | Effect of Increase |
|-------|---------------|------------------|---------------|-------------------|
| **Laminar** | - | - | - | - |
| **EDC** | `Cγ`, `Cτ` | Fine structure coefficients | Default (v2016) | Higher Cγ → faster reactions |
| **PaSR** | `Cmix` | Mixing time constant | 0.1-0.5 | Higher Cmix → slower reactions (larger Da) |
| **Xi** | `XiCoef` | Wrinkling factor coefficient | 0.5-1.5 | Higher XiCoef → larger flame surface |
| **Flamelet** | `χst` | Stoichiometric scalar dissipation | 1-100 s⁻¹ | Higher χst → more strain (extinction) |

### Common Thermo Types

```cpp
// Detailed chemistry (laminar, EDC, PaSR)
thermoType
{
    type            hePsiThermo;
    mixture         multiComponentMixture;
    transport       sutherland;
    thermo          janaf;
    energy          sensibleEnthalpy;
    equationOfState perfectGas;
    specie          specie;
}

// Flamelet
thermoType
{
    type            hePsiFlameletThermo;
    flameletLibrary constant/flameletLibrary.dat;
}
```

### Computational Cost Comparison

```
Relative cost (laminar = 1.0):

Flamelet:     0.01-0.05
Xi:           0.1-0.3
PaSR:         0.3-0.7
EDC:          0.5-1.0
Laminar:      1.0
```

---

## 🧠 Concept Check

<details>
<summary><b>1. EDC คืออะไร และทำงานอย่างไร?</b></summary>

**Eddy Dissipation Concept** — combustion model ที่สมมติว่า reactions occur in **fine structures** ที่ถูกสร้างโดย turbulent dissipation rate ($\varepsilon$)

**Working principle:**
1. Calculate fine structure volume fraction: $\gamma^* = C_\gamma (\nu \varepsilon / k^2)^{1/4}$
2. Calculate fine structure residence time: $\tau^* = C_\tau (\nu / \varepsilon)^{1/2}$
3. Solve chemistry in fine structures (as PSR)
4. Reacting volume = $\gamma^*$ × total volume
5. Effective rate = $(\gamma^* / \tau^*) \times \rho (Y_i^* - \tilde{Y}_i)$

**Physical interpretation:**
- High $\varepsilon$ → small, intense fine structures → larger $\gamma^*$ → faster reactions
- Low $\varepsilon$ → large, weak fine structures → mixing-limited

**Use when:** Industrial applications with mixing-controlled combustion (furnaces, gas turbines, diesel engines)
</details>

<details>
<summary><b>2. PaSR แตกต่างจาก EDC อย่างไร?</b></summary>

**PaSR (Partially Stirred Reactor):**
- Cell = mixture of reacting PSR + non-reacting fluid
- Reacting fraction $\kappa = \tau_{\text{chem}} / (\tau_{\text{chem}} + \tau_{\text{mix}})$
- **Single chemistry solve** per cell
- **Adaptive:** $\kappa$ adjusts to local Da
- เหมาะกับ cases ที่มี **varying Da** (fast chemistry in some regions, slow in others)
- Computational cost: 0.3-0.7 × laminar

**EDC (Eddy Dissipation Concept):**
- Focuses on fine structures determined by $\varepsilon$
- **Iterative** PSR solution in fine structures
- **Fixed** reacting volume fraction $\gamma^*$ (from k, ε)
- เหมาะกับ **mixing-controlled** regimes (Da < 1)
- Computational cost: 0.5-1.0 × laminar

**Key difference:** PaSR is **adaptive** (κ varies with Da), EDC is **fixed** (γ* from turbulence)

**When to choose:**
- Use PaSR if Da varies significantly across domain
- Use EDC if Da is consistently low (mixing-controlled)
</details>

<details>
<summary><b>3. Premixed vs diffusion combustion — เลือก model อย่างไร?</b></summary>

| Flame Type | Characteristic | Mixture Fraction (Z) | Recommended Models |
|------------|----------------|---------------------|-------------------|
| **Premixed** | Fuel+air mixed before combustion | Uniform Z (≈ constant) | Xi, flamelet (FGM), PaSR |
| **Diffusion** | Fuel+air mix during combustion | Large Z variations (0-1) | Flamelet (diffusion), EDC, PaSR |
| **Partially premixed** | Mixed regime | Some Z variations | PaSR, EDC, flamelet (mixed) |

**Key indicator:** Mixture fraction $Z$ distribution
- Uniform Z (σ_Z² ≈ 0) → premixed
- Large Z variations (σ_Z² ≈ 0.1-0.2) → diffusion
- Mixed → partially premixed

**Model selection by flame type:**
```
Premixed + Ka < 100:     Xi model (flame surface tracking)
Premixed + Ka > 100:     PaSR (well-stirred)
Diffusion + Da < 1:      Flamelet or EDC (mixing-controlled)
Diffusion + Da > 1:      PaSR or laminar (kinetically-controlled)
Mixed:                   PaSR or EDC (handles both)
```
</details>

<details>
<summary><b>4. ทำไมต้องลดจำนวน species ใน reduced mechanisms?</b></summary>

**Stiff ODE Problem:**
- Full mechanisms (50+ species) → stiff chemical source terms
- Stiffness ratio = τ_slow / τ_fast ≈ 10⁵-10⁶
- Stiffness → very small time steps (Δt ~ 10⁻⁸ s)
- Computational cost ∝ n_species × n_cells × n_steps

**Example: Methane Combustion**

| Mechanism | Species | Reactions | Stiffness | Cost (relative) |
|-----------|---------|-----------|-----------|-----------------|
| **Full** (GRI-Mech 3.0) | 53 | 325 | 10⁶ | 1.0 (baseline) |
| **Skeletal** | 16 | 41 | 10³ | 0.1-0.2 |
| **Reduced** | 12 | 10 | 10² | 0.05-0.1 |

**Reduction strategies:**

1. **Skeletal mechanism:** Remove unimportant species
   - Use sensitivity analysis
   - Remove species with low sensitivity
   - Example: 50 → 16 species

2. **Steady-state assumption:** Fast intermediates in quasi-steady state
   - dY_i/dt ≈ 0 for fast species (H, O, OH)
   - Algebraic equations instead of ODEs

3. **Lumping:** Group similar species
   - Example: C₃H₆ + C₃H₈ → C₃H₇ (generic)

**Impact on accuracy:**

| Property | Full Mechanism | Reduced (16 sp) | Error |
|----------|----------------|-----------------|-------|
| Major species (CO₂, H₂O) | 15%, 12% | 14.8%, 11.7% | <2% |
| Ignition delay | 2.5 ms | 2.0 ms | 20% |
| Flame speed | 0.38 m/s | 0.36 m/s | 5% |

**Recommendation:**
- **EDC, PaSR:** Use reduced mechanisms (16-22 species)
- **Flamelet:** Can use detailed mechanisms (pre-processed)
- **Laminar:** Use detailed if affordable, reduced for speed

**Trade-off:**
```
Accuracy vs. Cost:
Full mechanism:     High accuracy, very high cost
Reduced mechanism:  Good accuracy (5-10% error), low cost
Very reduced:       Moderate accuracy (20% error), very low cost
```
</details>

<details>
<summary><b>5. XiFoam ใช้เมื่อไหร์ และมีข้อจำกัดอะไรบ้าง?</b></summary>

**XiFoam Use Cases:**
- **Premixed turbulent flames** (e.g., gas engines, SI engines, premixed burners)
- Cases with well-defined laminar flame speed $S_L$
- Flame propagation tracking required
- Moderate Karlovitz number (Ka < 100)

**Key Inputs:**
- Laminar flame speed $S_L(T, p, \phi)$ — from correlations or 1D calculations
- Unburnt gas properties ($\rho_u, Y_{i,u}$)
- Turbulence quantities (k, ε for u')

**Limitations:**

1. **Premixed only** — ไม่เหมาะกับ diffusion flames
   - Use flamelet or EDC for non-premixed

2. **Flame speed dependency** — inaccurate $S_L$ → wrong flame position
   - **Challenge:** $S_L$ for complex fuels (multi-component, additives)
   - **Solution:** Use detailed 1D calculations or experimental correlations

3. **Regime limitations** — breaks down for high Ka (broken reaction zones)
   - Valid for Ka < 100
   - For Ka > 100, use PaSR

4. **Model coefficients** — Xi parameters need calibration
   - $\alpha, \beta$ in Xi transport equation
   - XiCoef in algebraic model
   - **Calibration:** Compare with experimental flame data

5. **No detailed chemistry** — only flame speed
   - Cannot predict minor species (CO, UHC, NOx) accurately
   - **Alternative:** Use flamelet (with detailed chemistry)

**Alternative model selection:**
```
Non-premixed:          Use flamelet or EDC
High Ka (>100):        Use PaSR
Detailed chemistry:    Use flamelet or laminar
Unknown S_L:           Use PaSR (with chemistry mechanism)
```
</details>

<details>
<summary><b>6. Flamelet model มีข้อดีอะไรเมื่อเปรียบเทียบกับ EDC และ PaSR?</b></summary>

**Advantages of Flamelet:**

1. **Very fast:**
   - No chemistry integration (table lookup)
   - Cost: 0.01-0.05 × laminar (vs. 0.3-0.7 × for PaSR, 0.5-1.0 × for EDC)
   - **Speedup:** 10-100× faster than EDC/PaSR

2. **Detailed chemistry:**
   - Can include 100+ species (pre-processed)
   - Accurate minor species (CO, UHC, NOx)
   - **No penalty** during CFD run (pre-computed)

3. **Well-validated:**
   - Extensive literature for common fuels (methane, jet-A, etc.)
   - Standard for gas turbine combustion
   - Benchmark data available (e.g., Sandia flames)

**Comparison:**

| Aspect | Flamelet | EDC | PaSR |
|--------|----------|-----|------|
| **Computational cost** | ★★★★★ (Very fast) | ★★★☆☆ (Medium) | ★★★★☆ (Fast) |
| **Chemistry detail** | 100+ species | Limited by reduced mechanism | Limited by reduced mechanism |
| **Setup complexity** | ★☆☆☆☆ (Complex) | ★★☆☆☆ (Simple) | ★★☆☆☆ (Simple) |
| **Regime range** | Narrow (high Da, low Ka) | Wide (all Da) | Wide (all Da) |
| **Pre-processing** | Required (library generation) | Not required | Not required |

**When to choose flamelet:**

✅ **Use flamelet when:**
- Diffusion flames (non-premixed)
- High Da (> 10, fast chemistry)
- Moderate Ka (< 100, flame intact)
- Computational efficiency critical
- Detailed chemistry desired

❌ **Avoid flamelet when:**
- Premixed flames (use Xi or FGM)
- Low Da (< 1, slow chemistry)
- High Ka (> 100, broken reaction zones)
- Strong unsteady effects
- Multiple regimes (mixed premixed/diffusion)

**Example: Gas turbine combustor**

```
Regime: Non-premixed, Da ≈ 20, Ka ≈ 10
→ Flamelet ideal

Computational time:
- Flamelet:  10 CPU hours
- EDC:       200 CPU hours
- PaSR:      150 CPU hours
- Laminar:   500 CPU hours

Speedup: 20-50× vs. EDC/PaSR
```
</details>

<details>
<summary><b>7. จะทราบได้อย่างไรว่า flow อยู่ใน regime ไหน (Da, Ka calculation)?</b></summary>

**Step 1: Calculate Flow Time Scale (τ_flow)**

$$\tau_{\text{flow}} = \frac{k}{\varepsilon} = \frac{\text{turbulent kinetic energy}}{\text{dissipation rate}}$$

**From OpenFOAM:**
```cpp
// Post-process function object
functions
{
    tauFlow
    {
        type            coded;
        functionObjectLibs ("libutilityFunctionObjects.so");
        code
        #{
            const volScalarField& k = mesh().lookupObject<volScalarField>("k");
            const volScalarField& epsilon = mesh().lookupObject<volScalarField>("epsilon");
            volScalarField tauFlow = k / epsilon;
            tauFlow.write();
        #};
    }
}
```

**Typical values:**
- Industrial furnace: τ_flow ≈ 10⁻³ - 10⁻² s
- Gas turbine: τ_flow ≈ 10⁻⁴ - 10⁻³ s
- Jet flame: τ_flow ≈ 10⁻³ - 10⁻¹ s

**Step 2: Calculate Chemical Time Scale (τ_chem)**

$$\tau_{\text{chem}} = \left[ \frac{1}{Y_i} \frac{dY_i}{dt} \right]^{-1}$$

**Approximation:**
$$\tau_{\text{chem}} \approx \frac{\delta_L}{S_L}$$

where:
- $\delta_L$ = laminar flame thickness ≈ 0.5 mm (methane)
- $S_L$ = laminar flame speed ≈ 0.38 m/s (methane, φ=1)

**Typical values:**
- Methane-air: τ_chem ≈ 1.3 × 10⁻³ s
- Heptane: τ_chem ≈ 10⁻⁴ s (faster)
- Hydrogen: τ_chem ≈ 10⁻⁵ s (very fast!)

**Step 3: Calculate Damköhler Number (Da)**

$$Da = \frac{\tau_{\text{flow}}}{\tau_{\text{chem}}} = \frac{k / \varepsilon}{\delta_L / S_L}$$

**From OpenFOAM (post-process):**
```bash
# Use PyFoam or custom utility
foamCalc Da -k k -epsilon epsilon -SL 0.38 -deltaL 5e-4
```

**Interpretation:**
- Da > 10: Fast chemistry (mixing-controlled) → Flamelet, EDC
- Da ~ 1: Mixed regime → PaSR, EDC
- Da < 0.1: Slow chemistry (kinetically-controlled) → PaSR, Laminar

**Step 4: Calculate Karlovitz Number (Ka)**

$$Ka = \frac{\tau_{\text{chem}}}{\tau_{\eta}} = \left(\frac{u'}{S_L}\right)^{3/2}\left(\frac{\delta_L}{l}\right)^{1/2}$$

where:
- $u' = \sqrt{2k/3}$ = turbulent velocity fluctuation
- $l = 0.07 L$ = integral length scale (L = characteristic length)
- $\tau_\eta = (\nu/\varepsilon)^{1/2}$ = Kolmogorov time scale

**From OpenFOAM:**
```cpp
// Calculate Ka
volScalarField uPrime = sqrt(2.0/3.0 * k);
volScalarField l = 0.07 * characteristicLength;
volScalarField Ka = pow(uPrime / SL, 1.5) * sqrt(deltaL / l);
```

**Interpretation:**
- Ka < 1: Corrugated flamelets → Flamelet, Xi
- 1 < Ka < 100: Thin reaction zones → EDC, PaSR
- Ka > 100: Broken reaction zones → PaSR

**Step 5: Classify Regime**

Use Borghi diagram:

```
Ka
↑
│ Broken Reaction Zones (Ka > 100)
│─────────────────────────────────
│ Thin Reaction Zones (1 < Ka < 100)
│─────────────────────────────────
│ Corrugated Flamelets (Ka < 1)
│
└────────────────────────────────────→ Da
   Slow (Da < 1)  Mixed (Da ~ 1)  Fast (Da > 10)
```

**Example: Industrial Furnace**

```
Parameters:
k = 1.0 m²/s²
ε = 100 m²/s³
SL = 0.38 m/s
δL = 5 × 10⁻⁴ m
u' = 0.8 m/s
l = 0.1 m

Time scales:
τ_flow = k/ε = 0.01 s
τ_chem = δL/SL = 1.3 × 10⁻³ s

Dimensionless numbers:
Da = τ_flow / τ_chem = 0.01 / 1.3e-3 ≈ 7.7 (fast chemistry)
Ka = (u'/SL)^(3/2) × (δL/l)^(1/2)
   = (0.8/0.38)^1.5 × (5e-4/0.1)^0.5
   ≈ 3.4 × 0.07 ≈ 0.24 (corrugated flamelets)

Regime: Corrugated flamelets, fast chemistry
Model recommendation: Flamelet or EDC
```
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Fundamentals:** [01_Reacting_Flow_Fundamentals.md](01_Reacting_Flow_Fundamentals.md)
- **Species Transport:** [02_Species_Transport.md](02_Species_Transport.md)
- **Chemistry Models:** [03_Chemistry_Models.md](03_Chemistry_Models.md)
- **Practical Workflow:** [05_Practical_Workflow.md](05_Practical_Workflow.md)

---

## 📌 Key Takeaways

1. **Combustion models คือ closure** สำหรับ turbulence-chemistry interaction
   - $\overline{\dot{\omega}_i} \neq \dot{\omega}_i(\tilde{Y}, \tilde{T}, \tilde{p})$
   - เนื่องจาก nonlinear reaction rate และ turbulent fluctuations

2. **Model selection depends on**:
   - Flow regime (premixed vs. diffusion vs. mixed)
   - Damköhler number (Da = τ_flow / τ_chem)
   - Karlovitz number (Ka = τ_chem / τ_η)
   - Computational resources (CPU hours, memory)
   - Validation data availability

3. **Model characteristics:**
   - **EDC = mixing-controlled** (fine structures, Da < 1)
   - **PaSR = adaptive** (Da-dependent, κ = τ_chem / (τ_chem + τ_mix))
   - **Xi = premixed** (flame surface tracking, Ka < 100)
   - **Flamelet = fast lookup** (2D table, Da > 10, Ka < 100)
   - **Laminar = direct integration** (DNS validation only)

4. **Computational cost hierarchy:**
   ```
   Flamelet (fastest) < Xi < PaSR < EDC < Laminar (slowest)
   0.01×             0.2×   0.5×   0.7×   1.0×
   ```

5. **Reduced mechanisms** แนะนำสำหรับ EDC และ PaSR
   - Full mechanism (53 sp) → reduced (16 sp): 5-10× speedup
   - Error in major species <5%, ignition delay <20%

6. **Calibration** ของ model constants จำเป็นสำหรับ accurate predictions
   - EDC: Cγ, Cτ (fine structure coefficients)
   - PaSR: Cmix (mixing time constant)
   - Xi: α, β (wrinkling coefficients)

7. **Validation workflow:**
   - Characterize regime (Da, Ka calculation)
   - Select model (use quantitative selection matrix)
   - Run simulation with default constants
   - Compare with experimental data
   - Adjust constants iteratively
   - Validate for multiple conditions

8. **Key physical insight:**
   - **Fast chemistry (Da ≫ 1):** Mixing-controlled → use EDC or flamelet
   - **Slow chemistry (Da ≪ 1):** Kinetically-controlled → use PaSR or laminar
   - **Mixed regime (Da ~ 1):** Both important → use PaSR or EDC
   - **High Ka (> 100):** Broken reaction zones → use PaSR
   - **Premixed:** Use Xi or flamelet (FGM)
   - **Non-premixed:** Use flamelet or EDC