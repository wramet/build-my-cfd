# Benchmark Problems for Multiphase Flow Validation

Standardized test cases for verifying simulation accuracy

---

## Learning Objectives

By the end of this section, you should be able to:

- **Explain** the importance of benchmark problems in verifying multiphase flow simulations
- **Select** appropriate benchmark cases for your specific application
- **Set up and execute** benchmark cases correctly in OpenFOAM
- **Evaluate** result accuracy using appropriate acceptance criteria
- **Check** volume conservation, force balance, and other key validation metrics

---

## Overview: What Are Benchmark Problems?

Benchmark problems are standardized test cases used to verify CFD simulation accuracy for multiphase flows. Each benchmark is designed to test specific physical phenomena and numerical capabilities.

**WHY benchmark problems matter:**

- **Code Verification:** Confirms solver implementation matches mathematical formulation
- **Solution Verification:** Evaluates discretization errors and numerical uncertainty
- **Model Validation:** Confirms physics models predict real phenomena correctly
- **Quality Assurance:** Builds confidence in engineering predictions

For the broader verification and validation framework, see [00_Overview.md](00_Overview.md) and [01_Validation_Methodology.md](01_Validation_Methodology.md).

---

## How to Select Appropriate Benchmarks

Selecting the right benchmark depends on your application requirements:

| Consideration | Questions to Ask |
|---------------|------------------|
| **Physics to test** | Surface tension? Gravity separation? Turbulent dispersion? |
| **Solver type** | VOF (`interFoam`) or Eulerian (`multiphaseEulerFoam`)? |
| **Flow regime** | Laminar or turbulent? Dilute or dense? |
| **Available data** | Are experimental or analytical solutions available at sufficient detail? |
| **Computational cost** | Can you run it within available resources? |

**Recommended progression for solver verification:**

1. **Start with simple cases:** Single bubble rising, static interface
2. **Add complexity:** Deformed bubbles, stratified flows
3. **Test advanced features:** Turbulent dispersion, coalescence/breakup
4. **Validate with experiments:** Bubble columns, fluidized beds

---

## Benchmark Decision Matrix

Use this table to quickly identify which benchmark suits your needs:

| Benchmark | Physics Focus | Solver | Difficulty | Key Validation Metrics | Best For... |
|-----------|---------------|--------|------------|------------------------|-------------|
| **Single Bubble Rising** | Buoyancy, surface tension, bubble shape | `interFoam` | ⭐ | Terminal velocity, volume conservation, shape regime | VOF validation, surface tension models |
| **Stratified Flow** | Gravity separation, interface dynamics | `interFoam` | ⭐⭐ | Liquid holdup, pressure gradient, wave characteristics | Pipe flows, separation processes |
| **Fluidized Bed** | Gas-solid drag, dense packing, granular temperature | `multiphaseEulerFoam` | ⭐⭐⭐ | Minimum fluidization velocity, bed expansion, pressure drop | Eulerian solver validation, dense systems |
| **Bubble Column** | Dispersed flows, turbulent dispersion, recirculation | `multiphaseEulerFoam` | ⭐⭐⭐ | Gas holdup, radial profiles, bubble size distribution | Reactor design, scale-up studies |
| **Dam Break** | Free surface, impact pressure, wave propagation | `interFoam` | ⭐⭐ | Wave front position, impact pressure, splash height | Transient validation, free-surface flows |
| **Droplet Impact** | Surface tension, contact angle, spreading dynamics | `interFoam` | ⭐⭐⭐ | Spread factor, rebound height, maximum diameter | Microscale flows, coating processes |

---

## 1. Single Bubble Rising

### What It Tests

VOF solver capability to simulate bubble motion under buoyancy and surface tension forces with accurate volume conservation.

### Physical Setup

| Parameter | Typical Value | Description |
|-----------|---------------|-------------|
| Bubble diameter ($d_b$) | 2-10 mm | Size determines shape regime |
| Domain size | 10 × $d_b$ | Minimizes wall effects |
| Solver | `interFoam` | VOF-based geometric VOF |
| Turbulence model | Laminar or LES | Depends on Reynolds number |
| Fluid system | Air-water | $\sigma = 0.072$ N/m |

### Dimensionless Numbers (WHAT controls behavior)

**Eötvös Number ($Eo$):**
$$Eo = \frac{g(\rho_l - \rho_g)d_b^2}{\sigma}$$

- $Eo < 1$: Surface tension dominates → **spherical bubble**
- $1 < Eo < 40$: Intermediate regime → **ellipsoidal/deformed**
- $Eo > 40$: Buoyancy dominates → **spherical cap/skirted**

**Reynolds Number ($Re_b$):**
$$Re_b = \frac{\rho_l u_t d_b}{\mu_l}$$

- $Re_b < 1$: Creeping flow (Stokes regime)
- $1 < Re_b < 100$: Vortex shedding begins
- $Re_b > 100$: Turbulent wake

**Morton Number ($Mo$):**
$$Mo = \frac{g\mu_l^4(\rho_l - \rho_g)}{\rho_l^2 \sigma^3}$$

Combines fluid properties into a single system characterizing parameter (independent of bubble size).

### OpenFOAM Setup (HOW to implement)

```cpp
// constant/transportProperties
phases (gas liquid);

liquid
{
    transportModel  Newtonian;
    nu   [0 2 -1 0 0 0 0] 1.0e-06;  // Water kinematic viscosity
    rho  [1 -3 0 0 0 0 0] 1000;     // Water density
}

gas
{
    transportModel  Newtonian;
    nu   [0 2 -1 0 0 0 0] 1.5e-05;  // Air kinematic viscosity
    rho  [1 -3 0 0 0 0 0] 1.2;      // Air density
}

sigma  [1 0 -2 0 0 0 0] 0.072;     // Surface tension coefficient (N/m)
```

```cpp
// constant/interFoamProperties (optional tuning)
compressionScheme    interfaceCompression;
interfaceCompressionCoeff 0.5;  // Lower = sharper interface, less stable

// For better volume conservation
MULESCorr yes;
nLimiterIter 2;
```

### Acceptance Criteria

| Metric | Target | Notes |
|--------|--------|-------|
| Terminal velocity error | < 10% (spherical), < 15% (deformed) | Compare with Grace (1976) correlation |
| Volume conservation | < 2% change | Check $\int \alpha_g dV$ over time |
| Shape agreement | Qualitative match to regime map | Bhaga & Weber (1981) |
| Path stability | Stable vertical rise | No spurious lateral oscillations |

**Key References:**
- Grace, J.R. (1976): "Shapes and velocities of bubbles" - comprehensive velocity correlation
- Bhaga & Weber (1981): Bubble shape regime map
- Hua & Lou (2007): VOF method validation

**Common Issues:**
- **Volume loss:** Reduce `interfaceCompressionCoeff` or use `MULESCorr yes`
- **Unphysical oscillations:** Check Courant number (< 1 recommended)
- **Incorrect terminal velocity:** Verify surface tension coefficient and mesh refinement

---

## 2. Stratified Two-Phase Flow

### What It Tests

Gravity separation capability, interface dynamics, and pressure-velocity coupling for separated gas-liquid flows in pipes.

### Physical Setup

| Parameter | Typical Value | Description |
|-----------|---------------|-------------|
| Pipe diameter ($D$) | 0.05 m | Lab-scale standard |
| Domain length | $10D - 20D$ | Ensures fully developed flow |
| $U_{gas}$ | 1-10 m/s | Superficial gas velocity |
| $U_{liquid}$ | 0.1-1 m/s | Superficial liquid velocity |
| Inclination | 0° (horizontal) | Can vary ±5° for studies |
| Solver | `interFoam` | VOF-based for interface tracking |

### Dimensionless Numbers

**Froude Number ($Fr$):**
$$Fr = \frac{U_g}{\sqrt{gD}}$$

Ratio of inertial to gravitational forces:
- $Fr < 1$: Gravity-dominated (smooth interface)
- $Fr > 1$: Inertia-dominated (wavy interface)

**Lockhart-Martinelli Parameter ($X$):**
$$X = \sqrt{\frac{(dP/dx)_l}{(dP/dx)_g}}$$

Compares pressure drop if each phase flows alone; used for pressure drop correlations.

### Validation Metrics

| Metric | Target Correlation | What It Validates |
|--------|-------------------|-------------------|
| Liquid holdup ($h_l/D$) | Taitel-Dukler (1976) | Interface level prediction |
| Pressure gradient | Lockhart-Martinelli (1949) | Two-phase friction multiplier |
| Wave characteristics | Andritsos & Hanratty (1987) | Interfacial wave dynamics |

### OpenFOAM Setup

```cpp
// 0/alpha.water (initial stratified condition)
boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 0;  // Start with gas phase
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
}

// system/fvSchemes (for interface sharpness)
divSchemes
{
    div(rhoPhi,U)      Gauss upwind;  // Stable for separated flows
    div(phi,alpha)     Gauss vanLeer;  // Compressive scheme for interface
}
```

```cpp
// system/controlDict (monitoring functions)
functions
{
    liquidHoldup
    {
        type            surfMeshSamplers;
        surfaceFormat   none;
        fields          (alpha.water);
        setFormat       raw;
        interpolationScheme cellPoint;
        
        // Extract interface height at multiple axial locations
        // for comparison with Taitel-Dukler correlation
    }
}
```

### Key Challenges and Solutions

| Challenge | Solution |
|-----------|----------|
| **Interface resolution** | Minimum 10-15 cells across interface thickness |
| **Inlet boundary conditions** | Use `fixedValue` for both phases with correct $\alpha$ |
| **Wave development** | Domain length > 15D for fully developed waves |
| **Pressure-velocity coupling** | Use `PIMPLE` with correct `nCorrectors` (2-3) |
| **Turbulence modeling** | Consider `kOmegaSST` for better near-wall treatment |

---

## 3. Fluidized Bed

### What It Tests

Gas-solid drag model accuracy, Eulerian solver capability for dense particulate flows, and kinetic theory of granular flows (KTGF) implementation.

### Physical Setup

| Parameter | Typical Value | Description |
|-----------|---------------|-------------|
| Bed dimensions | $0.3 \times 0.3 \times 2.0$ m | Lab-scale column |
| Particle diameter ($d_p$) | 500 μm | Group B particles (Geldart classification) |
| Particle density ($\rho_p$) | 2500 kg/m³ | Sand/glass beads |
| Initial bed height ($H_0$) | 0.3-0.5 m | Packed bed condition |
| Initial voidage ($\varepsilon_0$) | 0.4-0.45 | Random loose packing |
| Solver | `multiphaseEulerFoam` | Eulerian-Eulerian with KTGF |

### Operating Regimes (WHAT to validate)

| Regime | Velocity Range ($U/U_{mf}$) | Physical Characteristics |
|--------|----------------------------|--------------------------|
| Fixed bed | < 1.0 | No particle motion, static packing |
| Minimum fluidization | = 1.0 | Onset of particle motion, bed expands slightly |
| Bubbling | 1.5-3.0 | Bubble formation and rise, mixing begins |
| Slugging | 3.0-6.0 | Large bubbles (narrow beds), pressure oscillations |
| Turbulent | 6.0-10.0 | Intense mixing, small voids, no distinct bubbles |
| Transport | > 10.0 | Particle elutriation, pneumatic conveying |

### Key Correlations

**Minimum Fluidization Velocity ($U_{mf}$):**

Wen & Yu correlation:
$$Re_{mf} = \sqrt{33.7^2 + 0.0408 Ar} - 33.7$$

where:
$$Ar = \frac{g d_p^3 \rho_g (\rho_p - \rho_g)}{\mu_g^2}$$

**Acceptance criterion:** Predicted $U_{mf}$ within ±10% of correlation.

**Ergun Equation (packed bed pressure drop):**
$$\frac{\Delta P}{L} = \frac{150\mu(1-\varepsilon)^2}{\varepsilon^3 d_p^2}U + \frac{1.75\rho(1-\varepsilon)}{\varepsilon^3 d_p}U^2$$

At minimum fluidization: $\Delta P/L = (\rho_p - \rho_g)(1-\varepsilon_{mf})g$

### OpenFOAM Setup

```cpp
// constant/phaseProperties
phases (particles air);

particles
{
    diameterModel constant;
    d   uniform 5e-4;  // 500 μm
    
    rho     [1 -3 0 0 0 0 0] 2500;
    
    // Maximum packing fraction (random close packing)
    alphaMax    uniform 0.63;
    
    // Granular viscosity model
    viscosityModel kinetic;
}

air
{
    transportModel  Newtonian;
    nu   [0 2 -1 0 0 0 0] 1.5e-05;
    rho  [1 -3 0 0 0 0 0] 1.2;
}

drag
{
    (particles in air)
    {
        type    GidaspowErgunWenYu;
        
        // Automatically switches between:
        // - Ergun (dense, alpha < 0.8)
        // - WenYu (dilute, alpha > 0.8)
    }
}
```

```cpp
// constant/turbulenceProperties (kineticTheoryModel)
simulationType  twoPhaseRAS;

RAS
{
    RASModel        kEpsilon;
    
    kineticTheory on;
    
    // Granular temperature equation
    granularity     on;
    
    // Granular Prandtl number
    Prt             0.9;
}
```

```cpp
// system/controlDict (monitoring)
functions
{
    bedExpansion
    {
        type            surfMeshSamplers;
        surfaceFormat   none;
        fields          (alpha.particles);
        
        // Extract bed surface height over time
    }
    
    pressureDrop
    {
        type            surfaceRegion;
        operation       areaAverage;
        region          inlet;
        fields          (p);
    }
}
```

### Validation Metrics

| Metric | Target | Reference Method |
|--------|--------|------------------|
| $U_{mf}$ prediction | ±10% | Wen & Yu (1966) correlation |
| Bed expansion ratio | Qualitative agreement | Experimental bed height vs. velocity |
| Pressure drop | Ergun equation | $\Delta P/L$ across bed |
| Bubble frequency | Visual comparison | Image analysis or pressure fluctuations |
| Solid mixing pattern | Qualitative match | Tracer experiments |

**Common Issues:**

| Issue | Cause | Solution |
|-------|-------|----------|
| **Poor $U_{mf}$ prediction** | Incorrect drag model | Switch to `GidaspowErgunWenYu` |
| **Unstable simulation** | High solid volume fraction | Reduce time step, use implicit drag |
| **Excessive bubble size** | Insufficient resolution | Refine mesh, especially near distributor |
| **Incorrect granular temperature** | Wrong KTGF parameters | Check restitution coefficient (0.9-0.99) |

---

## 4. Bubble Column

### What It Tests

Dispersed gas-liquid flows, turbulent dispersion, lift force effects, and recirculation patterns in reactor-scale systems.

### Physical Setup

| Parameter | Typical Value | Description |
|-----------|---------------|-------------|
| Column height ($H$) | 1-2 m | Scale affects hydrodynamics |
| Column diameter ($D$) | 0.15-0.3 m | Aspect ratio $H/D$ important |
| Sparger type | Perforated plate | Determines initial bubble size |
| Hole diameter | 1-2 mm | Affects bubble size distribution |
| Gas holdup ($\varepsilon_g$) | 5-30% | Operating range |
| Superficial gas velocity ($U_g$) | 0.01-0.3 m/s | Controls flow regime |
| Solver | `multiphaseEulerFoam` | Eulerian-Eulerian with turbulence |

### Flow Regimes

| Regime | $U_g$ (m/s) | Characteristics |
|--------|-------------|-----------------|
| Homogeneous (bubbly) | < 0.03 | Small bubbles, uniform rise, minimal recirculation |
| Transition | 0.03-0.05 | Onset of coalescence, some large bubbles |
| Heterogeneous (churn-turbulent) | > 0.05 | Large bubbles, strong recirculation, mixing |

### Validation Metrics

| Quantity | Measurement Technique | Reference Data Sources |
|----------|----------------------|------------------------|
| **Global gas holdup** | $\varepsilon_g = \frac{V_g}{V_{total}}$ | Volume expansion or differential pressure |
| **Radial holdup profile** | Conductivity/optical probes | Parabolic: core-annular distribution |
| **Bubble size distribution** | Image analysis/photography | Sauter mean diameter $d_{32}$ |
| **Liquid velocity field** | PIV/LDA/CT | Recirculation patterns, vortex core |
| **Interfacial area concentration** | $a = \frac{6\varepsilon_g}{d_{32}}$ | Mass transfer coefficient correlation |

### OpenFOAM Setup

```cpp
// constant/phaseProperties
phases (gas liquid);

gas
{
    diameterModel constant;
    d   uniform 0.003;  // 3 mm Sauter mean diameter
    
    rho     [1 -3 0 0 0 0 0] 1.2;
}

liquid
{
    transportModel  Newtonian;
    nu   [0 2 -1 0 0 0 0] 1.0e-06;
    rho  [1 -3 0 0 0 0 0] 1000;
}

drag
{
    (gas in liquid)
    {
        type    SchillerNaumann;  // Standard for clean bubbles
        
        // Alternative models:
        // - IshiiZuber: wider range of Reynolds numbers
        // - Tomiyama: includes deformation effects
    }
}

lift
{
    (gas in liquid)
    {
        type    constant;  // or Tomiyama for size-dependent
        Cl      0.1;       // Positive for small bubbles (< 5.8 mm)
    }
}

turbulentDispersion
{
    (gas in liquid)
    {
        type    constant;
        Ctd     1.0;  // Burns et al. (2004) recommended value
    }
}

virtualMass
{
    (gas in liquid)
    {
        type    constant;
        Cvm     0.5;  // Theoretical value for spheres
    }
}
```

```cpp
// constant/turbulenceProperties
simulationType  twoPhaseRAS;

RAS
{
    RASModel        kEpsilon;
    
    turbulence      on;
    
    // Bubble-induced turbulence source
    bubbleTurbulence on;
}
```

```cpp
// system/controlDict (function objects)
functions
{
    gasHoldup
    {
        type            volRegion;
        operation       volAverage;
        fields          (alpha.gas);
        writeControl    timeStep;
        writeInterval   10;
    }
    
    radialProfile
    {
        type            sets;
        setFormat       raw;
        
        sets
        (
            r0
            {
                axis    distance;
                start   (0 0.1 0);       // At column center, mid-height
                end     (0.075 0.1 0);    // To wall (D/2)
                nPoints 50;
            }
        );
        
        fields          (alpha.gas U.liquid);
    }
    
    liquidVelocityField
    {
        type            surfaces;
        surfaceFormat   vtk;
        
        surfaces
        (
            midHeight
            {
                type            plane;
                basePoint       (0 0 1.0);   // At H/2
                normal          (0 0 1);
            }
        );
        
        fields          (U.liquid alpha.gas);
        writeControl    outputTime;
    }
}
```

### Key Considerations

**WHY bubble size distribution matters:**
- Constant diameter models often insufficient
- Polydisperse systems require population balance models
- Coalescence and breakup affect interfacial area

**Lift force direction:**
- Small bubbles ($d < d_{crit} \approx 5.8$ mm for air-water): Positive $C_l$ → migrate toward wall
- Large bubbles ($d > d_{crit}$): Negative $C_l$ → migrate toward center
- Use Tomiyama model for size-dependent lift coefficient

**Turbulent dispersion importance:**
- Essential for spreading gas phase radially
- Without it, bubbles accumulate at wall or center (unphysical)
- $C_{td} \approx 1.0$ recommended for most systems

**Sparger modeling:**
- Directly modeling perforated plate requires fine mesh
- Alternative: Use uniform inlet with effective bubble size
- Distributor region effects can propagate upward

**Common Validation Data:**
- Deckwer (1992): Bubble column handbook (comprehensive correlations)
- Krishna et al. (1999): CFD validation studies (well-documented experiments)
- Chen et al. (2005): Comprehensive experimental dataset (PIV measurements)

---

## 5. Additional Benchmark Cases

### Dam Break

**What it tests:** Free-surface dynamics, impact pressures, transient wave propagation

**Setup:**
```cpp
// Initial water column (typical)
// Column: 0.146 × 0.146 m (width × height)
// Domain: 0.584 × 0.438 m (length × height)
// Fluid: Water (rho = 1000, nu = 1e-6)
```

**Validation metrics:**
- Wave front position vs. time (Martin & Moyce, 1952)
- Impact pressure at wall
- Maximum splash height

**Difficulty:** ⭐⭐ (good for transient validation)

### Droplet Impact

**What it tests:** Surface tension-dominated flows, contact angle dynamics, spreading behavior

**Key dimensionless number:**
$$We = \frac{\rho U^2 D}{\sigma}$$

- $We < 5$: Surface tension dominates (droplet rebounds)
- $5 < We < 30$: Spreading without breakup
- $We > 30$: Splashing and breakup

**Validation metrics:**
- Maximum spread factor ($D_{max}/D_0$)
- Rebound height (for $We < 5$)
- Contact line dynamics

**Difficulty:** ⭐⭐⭐ (requires fine mesh near wall)

### Rayleigh-Taylor Instability

**What it tests:** Interface instability, buoyancy-driven mixing, numerical diffusion

**Setup:**
- Heavy fluid over light fluid
- Perturbed interface (sinusoidal perturbation)
- Atwood number: $A = \frac{\rho_h - \rho_l}{\rho_h + \rho_l}$

**Validation metrics:**
- Growth rate of initial perturbation
- Spike and bubble velocities
- Mixing zone width

**Difficulty:** ⭐⭐⭐⭐ (challenging for numerical stability)

---

## 6. OpenFOAM Validation Tools

### Function Objects for Automated Validation

```cpp
// system/controlDict
functions
{
    // ===== VOLUME CONSERVATION CHECK =====
    volumeConservation
    {
        type            volRegion;
        operation       volIntegrate;
        fields          (alpha.gas);
        writeControl    timeStep;
        writeInterval   1;
        
        // Check: should remain constant (±2%)
    }
    
    // ===== GLOBAL QUANTITIES =====
    gasHoldup
    {
        type            volRegion;
        operation       volAverage;
        fields          (alpha.gas);
        writeControl    timeStep;
        writeInterval   10;
    }
    
    // ===== FORCE CALCULATION (for bubble rise) =====
    forceCoeffs
    {
        type            forces;
        functionObjectLibs ("libforces.so");
        patches         (walls);
        rho             rhoInf;
        rhoInf          1000;  // Liquid density
        log             yes;
        
        // Output: drag and lift forces
    }
    
    // ===== TIME SERIES PROBES =====
    measurementPoints
    {
        type            probes;
        probeLocations  
        (
            (0.05 0.1 0.5)   // In region of interest
            (0.05 0.1 1.0)   // Multiple heights
        );
        fields          (U p alpha.gas);
        writeControl    timeStep;
    }
    
    // ===== VERTICAL/LINE SAMPLING =====
    centerlineProfile
    {
        type            sets;
        setFormat       raw;
        
        sets
        (
            centerline
            {
                axis    z;
                start   (0.05 0.05 0);
                end     (0.05 0.05 2.0);
                nPoints 100;
            }
        );
        
        fields          (alpha.gas U.air p);
        writeControl    outputTime;
    }
    
    // ===== INTERFACE HEIGHT (stratified flows) =====
    interfaceHeight
    {
        type            surfMeshSamplers;
        surfaceFormat   none;
        fields          (alpha.water);
        setFormat       raw;
        interpolationScheme cellPoint;
        
        // Extract interface location at multiple axial positions
    }
}
```

### Post-Processing Workflow

```bash
# ===== PRE-PROCESSING =====
# Check mesh quality
checkMesh

# Verify initial conditions
postProcess -func volIntegrate -time 0

# ===== DURING SIMULATION =====
# Monitor volume conservation (real-time)
tail -f postProcessing/volumeConservation/0/volIntegrate_alpha.gas

# Check Courant number
grep Courant log.interFoam | tail -20

# ===== POST-PROCESSING =====
# Extract results at final time
sample -dict system/sampleDict -latestTime

# Generate validation plots
gnuplot scripts/plot_velocity.gnu
python scripts/plot_comparison.py

# Compare with reference data
python scripts/compare_benchmark.py \
    --case bubbleRise \
    --ref grace1976 \
    --metric terminal_velocity

# Grid convergence analysis (see 03_Grid_Convergence.md)
python scripts/gci_analysis.py \
    --meshes coarse medium fine \
    --key_quantity terminal_velocity
```

### Validation Checklist

Use this checklist before declaring a benchmark "validated":

- [ ] **Mesh independence:** GCI < 5% (see [03_Grid_Convergence.md](03_Grid_Convergence.md))
- [ ] **Time convergence:** Results independent of $\Delta t$
- [ ] **Volume conservation:** $|\frac{d}{dt}\int \alpha dV| < 2\%$
- [ ] **Force balance:** Drag matches expected within tolerance
- [ ] **Comparison with reference:** Key metrics within acceptance criteria
- [ ] **Reproducibility:** Can be reproduced on different meshes/machines
- [ ] **Documentation:** All parameters, BCs, and solver settings recorded

---

## Key Takeaways

- **Benchmark problems are essential** for establishing CFD code credibility—never skip this step
- **Each benchmark tests specific physics**—select benchmarks matching your application requirements
- **Grid convergence is mandatory** for all benchmarks—detailed methodology in [03_Grid_Convergence.md](03_Grid_Convergence.md)
- **OpenFOAM provides powerful validation tools**—leverage function objects for automated data extraction during simulations
- **Progressive complexity is key**—start with simple cases (single bubble) and advance to complex systems (bubble columns)
- **Document all validation results**—create validation reports for future reference and comparison
- **Acceptance criteria vary**—define appropriate tolerances based on engineering requirements and reference data quality
- **Physical realism matters**—ensure dimensionless numbers ($Re$, $Eo$, $Fr$, etc.) match the intended regime

---

## Concept Check Questions

<details>
<summary><b>Q1: How do benchmark problems differ from general test cases?</b></summary>

**A:** Benchmarks have specific characteristics:
- **Reference data:** High-quality experimental or analytical solutions available
- **Community acceptance:** Recognized standards in the research community
- **Targeted testing:** Designed to test specific physics or numerical capabilities
- **Reproducibility:** Can be independently reproduced by others

General test cases may be used for development or debugging without necessarily having reference data or community acceptance.
</details>

<details>
<summary><b>Q2: Why is single bubble rising a good starting point for VOF validation?</b></summary>

**A:** It's **simple yet comprehensive**:
- **Easy setup:** Define bubble geometry, fluid properties, and release
- **Clear physics:** Combines buoyancy + surface tension + drag (all essential for multiphase)
- **Abundant reference data:** Grace (1976), Bhaga & Weber (1981) provide detailed regime maps
- **Clear acceptance criteria:** Terminal velocity, volume conservation, bubble shape
- **Low computational cost:** Can run multiple meshes for grid independence studies

This makes it ideal for establishing baseline solver capability before advancing to complex cases.
</details>

<details>
<summary><b>Q3: What are the main challenges in simulating stratified flows?</b></summary>

**A:** Key challenges include:

1. **Interface resolution:** Requires ≥10 cells across interface for accurate surface tension
2. **Inlet BC specification:** Must correctly prescribe volume fractions and velocities for both phases
3. **Wave development:** Domain must be long enough ($>15D$) for flow development
4. **Pressure-velocity coupling:** Critical for separated flows—requires proper PIMPLE settings
5. **Turbulence modeling:** Interfacial turbulence is complex and challenging to capture
</details>

<details>
<summary><b>Q4: Why must fluidized beds use Eulerian solvers instead of Lagrangian tracking?</b></summary>

**A:** Due to **high particle concentration** ($\alpha_s > 0.1-0.2$):

| Aspect | Lagrangian (DPM) | Eulerian |
|--------|-------------------|----------|
| **Particle interactions** | Binary collisions (computationally expensive) | Modeled via kinetic theory |
| **Computational cost** | O(N) where N = number of particles | O(1) per cell |
| **Dense systems** | Prohibitively expensive | Efficient |
| **Statistical noise** | High (requires many particles) | Low (continuum fields) |

Eulerian framework uses **kinetic theory of granular flows (KTGF)** to model particle-phase stress and momentum transfer efficiently.
</details>

<details>
<summary><b>Q5: How do bubble columns and fluidized beds differ in modeling challenges?</b></summary>

**A:** Key differences:

| Aspect | Bubble Column (gas-liquid) | Fluidized Bed (gas-solid) |
|--------|----------------------------|---------------------------|
| **Density ratio** | $\rho_g/\rho_l \approx 0.001$ | $\rho_g/\rho_p \approx 0.0005$ (similar) |
| **Phase continuity** | Dispersed gas in continuous liquid | Dispersed solid in continuous gas |
| **Particle/bubble size** | Bubbles: 1-10 mm (can coalesce) | Particles: 50-500 μm (fixed size) |
| **Interphase forces** | Drag + lift + virtual mass (all important) | Drag dominates (others negligible) |
| **Turbulence** | Liquid-phase turbulence dominates | Granular temperature critical |
| **Closure models** | Simpler (mostly drag + dispersion) | Complex (KTGF + collisional stresses) |

Bubble columns focus on dispersed bubble dynamics, while fluidized beds require granular flow physics.
</details>

<details>
<summary><b>Q6: How do function objects assist the validation process?</b></summary>

**A:** Function objects enable **automated, real-time data extraction** during simulation:

- **`volIntegrate`**: Check volume conservation ($\int \alpha dV$ should be constant)
- **`volAverage`**: Calculate global quantities ($\bar{\alpha}_g$, $\varepsilon_g$, average pressure)
- **`forces`**: Measure drag/lift forces acting on bubbles/particles
- **`probes`**: Collect time-series data at specific monitoring points
- **`sets`**: Sample along lines/plane for profiles (velocity, holdup, etc.)

**Advantages:**
- No need to stop simulation to extract data
- Consistent output format across all cases
- Can plot real-time validation metrics
- Reduces post-processing effort
- Enables automated validation workflows
</details>

<details>
<summary><b>Q7: What is the recommended progression when validating a new multiphase solver?</b></summary>

**A:** Progressive validation strategy:

1. **Static interface test:** Verify surface tension implementation with stationary interface
2. **Single bubble rising:** Test buoyancy, surface tension, and volume conservation
3. **Stratified flow:** Validate gravity separation and interface tracking
4. **Droplet impact:** Test transient dynamics and contact line behavior
5. **Bubble column:** Validate dispersed flows and turbulence
6. **Application-specific case:** Test with your actual geometry/conditions

This **increasing complexity** approach isolates issues early and builds confidence systematically.
</details>

---

## Related Documents

- **Overview:** [00_Overview.md](00_Overview.md) — Verification and validation framework
- **Methodology:** [01_Validation_Methodology.md](01_Validation_Methodology.md) — Step-by-step validation procedures
- **Grid Convergence:** [03_Grid_Convergence.md](03_Grid_Convergence.md) — GCI calculation and mesh independence studies (detailed methodology referenced throughout this document)
- **Uncertainty Quantification:** [04_Uncertainty_Quantification.md](04_Uncertainty_Quantification.md) — Monte Carlo methods for uncertainty analysis