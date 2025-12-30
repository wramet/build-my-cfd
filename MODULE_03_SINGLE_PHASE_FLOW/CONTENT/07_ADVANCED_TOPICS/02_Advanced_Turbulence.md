# Advanced Turbulence Models

**LES, DES, and Transition Modeling for Flows Where RANS is Insufficient**

**Estimated Reading Time:** 30-35 minutes

---

## Learning Objectives

By the end of this section, you will be able to:

- **Identify** when to use advanced turbulence modeling (LES/DES/transition) instead of standard RANS approaches
- **Explain** the fundamental differences between LES, DES, and transition modeling approaches
- **Configure** LES simulations with appropriate SGS models and mesh requirements in OpenFOAM
- **Set up** DES simulations with proper RANS-LES hybrid meshing strategies
- **Implement** transition modeling using the γ-Reθ model for practical engineering flows
- **Evaluate** computational costs and accuracy trade-offs between different turbulence approaches

---

## Prerequisites

- **Turbulence Fundamentals** ([Module 03, Section 03](03_TURBULENCE_MODELING/01_Turbulence_Fundamentals.md)): RANS equations, turbulence scales, k-ε and k-ω SST models
- **Wall Treatment** ([Module 03, Section 03](03_TURBULENCE_MODELING/03_Wall_Treatment.md)): y+ concepts, wall functions vs. resolved boundary layers
- **Basic OpenFOAM Setup** ([Module 02](../../MODULE_02_MESHING_AND_CASE_SETUP/)): Creating case directories, setting boundary conditions
- **Mesh Quality** ([Module 02, Section 05](../../MODULE_02_MESHING_AND_CASE_SETUP/CONTENT/05_MESH_QUALITY_AND_MANIPULATION/01_Mesh_Quality_Criteria.md)): Mesh requirements for different flow regimes

---

## Model Selection Guide

### When to Use Advanced Turbulence Models

| Flow Situation | RANS | LES | DES | Transition |
|----------------|------|-----|-----|------------|
| Steady attached flow | ✅ Recommended | ❌ Overkill | ❌ Overkill | ❌ Not needed |
| Mild separation | ✅ Acceptable | ⚠️ Expensive | ⚠️ Possible | ❌ Not needed |
| Vortex shedding | ❌ Fails | ✅ Recommended | ✅ Good choice | ⚠️ Case-dependent |
| Massive separation | ❌ Poor accuracy | ✅ Best accuracy | ✅ Recommended | ❌ Not needed |
| Swirling/rotating flows | ⚠️ Limited | ✅ Excellent | ✅ Good choice | ❌ Not needed |
| High Re + wall-bounded | ⚠️ Challenging | ❌ Too expensive | ✅ Recommended | ⚠️ Case-dependent |
| Low Re airfoils | ⚠️ May overpredict drag | ❌ Expensive | ❌ Expensive | ✅ Essential |
| Turbomachinery | ⚠️ Limited | ⚠️ Expensive | ⚠️ Possible | ✅ Recommended |
| Bluff body aerodynamics | ❌ Poor | ✅ Excellent | ✅ Recommended | ❌ Not needed |

**Key:** ✅ = Good choice, ⚠️ = Case-dependent, ❌ = Not suitable

### Cost vs. Accuracy Trade-off

| Method | Computational Cost | Accuracy | Typical Use Cases |
|--------|-------------------|----------|-------------------|
| RANS (k-ω SST) | 1× (baseline) | Fair to good | Attached flows, mild separation |
| Transition Model | 1.2-1.5× | Good (when relevant) | Low Re external flows, turbomachinery |
| DES/DDES/IDDES | 5-20× | Good to excellent | High Re separated flows, wall-bounded |
| LES (wall-resolved) | 100×+ | Excellent | Fundamental studies, low to moderate Re |
| LES (wall-modeled) | 20-50× | Good to excellent | High Re flows where DES insufficient |
| DNS | 10,000×+ | Exact | Research only, very low Re |

---

## 1. Large Eddy Simulation (LES)

### 1.1 Why Use LES?

**Motivation:** RANS models average all turbulence fluctuations, which works well for steady, attached flows but fails for flows dominated by unsteady, coherent structures. LES bridges this gap by:

- **Resolving** large, energy-carrying eddies directly (which are flow-dependent and cannot be modeled universally)
- **Modeling** only small, isotropic eddies (which are more universal and easier to model)
- **Capturing** unsteady phenomena like vortex shedding, bluff body wakes, and mixing layers naturally

**When to choose LES:**
- You need accurate unsteady flow features
- The flow is dominated by large-scale turbulent structures
- Computational resources are sufficient (factor of ~100× RANS)
- Reynolds number is moderate (Re < 10⁶ for wall-resolved LES)
- You need detailed spectral or frequency-domain information

**When NOT to choose LES:**
- High Reynolds number with thin boundary layers (use DES or wall-modeled LES instead)
- Only steady-state statistics are needed (RANS may suffice)
- Computational budget is limited (DES is more efficient)

### 1.2 What is LES? (Theoretical Foundation)

**Concept:** Spatial filtering of Navier-Stokes equations separates resolved scales from subgrid scales (SGS).

**Filtered Navier-Stokes Equations:**
$$\frac{\partial \bar{u}_i}{\partial t} + \bar{u}_j\frac{\partial \bar{u}_i}{\partial x_j} = -\frac{1}{\rho}\frac{\partial \bar{p}}{\partial x_i} + \nu\frac{\partial^2 \bar{u}_i}{\partial x_j^2} - \frac{\partial \tau_{ij}}{\partial x_j}$$

Where:
- $\bar{u}_i$ = filtered (resolved) velocity
- $\tau_{ij} = \overline{u_i u_j} - \bar{u}_i \bar{u}_j$ = subgrid-scale stress tensor (must be modeled)

**Subgrid-Scale (SGS) Models:**

**Smagorinsky Model (most common):**
$$\nu_t = (C_s \Delta)^2 |\bar{S}|$$

Where:
- $C_s$ = Smagorinsky constant (typically 0.1-0.2)
- $\Delta$ = filter width (usually cube root of cell volume)
- $|\bar{S}| = \sqrt{2\bar{S}_{ij}\bar{S}_{ij}}$ = strain rate magnitude

**Dynamic Smagorinsky:**
- $C_s$ computed dynamically during simulation
- Better for complex flows with varying turbulence characteristics
- Can backscatter (energy from small to large scales)

**WALE (Wall-Adapting Local Eddy-viscosity):**
- Better near-wall behavior
- Correct $y^3$ scaling near walls
- Recommended for wall-bounded flows

**k-equation SGS:**
- Solves transport equation for SGS turbulent kinetic energy
- More expensive but more accurate for complex flows

| SGS Model | Advantages | Disadvantages | Typical Use |
|-----------|------------|---------------|-------------|
| Smagorinsky | Simple, robust | Over-dissipates, poor near walls | General flows, initial studies |
| dynamicKEqn | Adapts to flow | Can be unstable | Complex flows with varying turbulence |
| WALE | Good wall behavior | More complex | Wall-bounded flows |
| kEqn | More physical | Expensive | High-accuracy requirements |

### 1.3 How to Set Up LES in OpenFOAM

#### Step 1: Mesh Requirements

**Wall-resolved LES (most accurate):**

| Parameter | Requirement | Rationale |
|-----------|-------------|-----------|
| y+ | ≈ 1 | Resolve viscous sublayer |
| Δx+ | 50-100 | Streamwise resolution in wall units |
| Δz+ | 15-30 | Spanwise resolution in wall units |
| Cell aspect ratio | ≈ 20-40 max near walls | Maintain numerical stability |
| CFL number | 0.3-0.5 (max 1.0) | Temporal resolution requirement |

```cpp
// system/controlDict
application     pimpleFoam;

startFrom       latestTime;

controls
{
    maxCo       0.5;           // Critical for LES accuracy
    maxAlphaCo  1.0;
}
```

**Mesh estimation formula:**
$$N_{LES} \approx \frac{Re_L}{144} \left(\frac{L}{\delta}\right)^3$$

Where $Re_L$ is Reynolds number based on length $L$ and boundary layer thickness $\delta$.

#### Step 2: Configure turbulenceProperties

```cpp
// constant/turbulenceProperties
simulationType LES;

LES
{
    // Model selection
    LESModel        Smagorinsky;  // Options: Smagorinsky, dynamicKEqn, WALE, kEqn

    turbulence      on;

    // Filter width definition
    delta           cubeRootVol;  // Options: cubeRootVol, maxDeltaxyz, smoothDelta
    // cubeRootVol: Δ = V^(1/3) — most common
    // maxDeltaxyz: Δ = max(Δx, Δy, Δz) — conservative
    // smoothDelta: spatially smoothed — more expensive

    // Model coefficients
    SmagorinskyCoeffs
    {
        Cs          0.1;          // Default: 0.167
                                   // Lower = less dissipation
                                   // Higher = more stable
    }

    // If using dynamicKEqn:
    // dynamicKEqnCoeffs
    // {
    //     filter       simple;
    // }
}
```

#### Step 3: Initial and Boundary Conditions

```cpp
// 0/k (SGS turbulent kinetic energy)
dimensions      [0 2 -2 0 0 0 0];

internalField   uniform 0.1;  // Small initial value

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 0.1;
    }
    outlet
    {
        type            zeroGradient;
    }
    walls
    {
        type            zeroGradient;  // SGS k goes to zero at walls
    }
}
```

```cpp
// 0/nuSgs (SGS eddy viscosity)
dimensions      [0 2 -1 0 0 0 0];

internalField   uniform 1e-5;

boundaryField
{
    inlet
    {
        type            calculated;
        value           uniform 1e-5;
    }
    outlet
    {
        type            zeroGradient;
    }
    walls
    {
        type            nuSgsWallFunction;  // Automatic wall treatment
        value           uniform 0;
    }
}
```

#### Step 4: Solver Settings

```cpp
// system/fvSchemes
ddtSchemes
{
    default         backward;  // Second-order implicit for time accuracy
}

gradSchemes
{
    default         Gauss linear;
}

divSchemes
{
    default         Gauss limitedLinearV 1;  // Bounded scheme for convection
    div(phi,k)      Gauss limitedLinear 1;
    div(phi,nuSgs)  Gauss limitedLinear 1;
}

laplacianSchemes
{
    default         Gauss linear corrected;
}
```

```cpp
// system/fvSolution
solvers
{
    p
    {
        solver          GAMG;
        tolerance       1e-06;
        relTol          0.01;
    }

    "(U|k|nuSgs)"
    {
        solver          smoothSolver;
        smoother        GaussSeidel;
        tolerance       1e-05;
        relTol          0.1;
    }
}

PIMPLE
{
    nCorrectors     2;
    nNonOrthogonalCorrectors 0;
}
```

### 1.4 LES Workflow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                  LES SIMULATION WORKFLOW                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. PRE-PROCESSING                                           │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ • Re ~ 10³-10⁵ (wall-resolved)                      │    │
│  │ • Estimate cells: N ≈ Re_L/144 × (L/δ)³            │    │
│  │ • Create isotropic mesh (y+ ≈ 1, Δ+ ≈ 50)          │    │
│  │ • checkMesh: non-orthogonality < 70°               │    │
│  └─────────────────────────────────────────────────────┘    │
│                           ↓                                   │
│  2. TURBULENCE SETUP                                         │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ • simulationType LES                                │    │
│  │ • Choose SGS model: Smagorinsky/WALE/dynamicKEqn    │    │
│  │ • Set Cs ≈ 0.1-0.2                                  │    │
│  │ • Set maxCo ≤ 0.5                                   │    │
│  └─────────────────────────────────────────────────────┘    │
│                           ↓                                   │
│  3. INITIAL CONDITIONS                                       │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ • k (SGS): small initial value (~0.1U²)            │    │
│  │ • nuSgs: initialize from RANS or small value       │    │
│  │ • Run preliminary RANS for better IC (optional)    │    │
│  └─────────────────────────────────────────────────────┘    │
│                           ↓                                   │
│  4. SOLVE                                                    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ • Use pimpleFoam or solver for incompressible       │    │
│  │ • Monitor Co number every timestep                  │    │
│  │ • Sample statistics after flow development (~10T)   │    │
│  │ • Run for sufficient time for statistical convergence│    │
│  └─────────────────────────────────────────────────────┘    │
│                           ↓                                   │
│  5. POST-PROCESSING                                          │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ • Time-average fields (Umean, pmean, etc.)          │    │
│  │ • RMS fluctuations (uRMS, vRMS, wRMS)              │    │
│  │ • Spectral analysis (FFT in time)                   │    │
│  │ • Reynolds stress (-u'v')                           │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 1.5 Practical LES Exercise: Channel Flow

**Objective:** Validate LES setup against DNS data at Reτ = 395.

**Steps:**
1. Create channel geometry with periodic boundaries in streamwise/spanwise
2. Generate mesh with y+ ≈ 1, Δx+ ≈ 50, Δz+ ≈ 15
3. Set up Smagorinsky LES with Cs = 0.1
4. Run until statistical convergence (monitor bulk velocity)
5. Compare mean velocity and Reynolds stress profiles to Moser et al. DNS data

---

## 2. Detached Eddy Simulation (DES)

### 2.1 Why Use DES?

**Motivation:** Wall-resolved LES is prohibitively expensive at high Reynolds numbers due to the fine near-wall resolution required (y+ ≈ 1). DES addresses this by:

- **Using RANS** in the boundary layer (where turbulence is mostly steady and can be modeled)
- **Switching to LES** in separated regions (where unsteady eddies are important)
- **Reducing cost** by factor of 5-20× compared to wall-resolved LES

**When to choose DES:**
- High Reynolds number (Re > 10⁶)
- Wall-bounded flows with massive separation
- Bluff bodies with wakes (aircraft, buildings, vehicles)
- Cases where LES is too expensive but RANS is inaccurate

**When NOT to choose DES:**
- Attached flows (RANS is sufficient)
- Purely separated flows without walls (LES is better)
- Cases with ambiguous RANS-LES transition (may cause GIS)

### 2.2 What is DES? (Theoretical Foundation)

**Concept:** Hybrid RANS-LES model that switches based on grid spacing.

**Length Scale Modification:**
$$l_{DES} = \min(l_{RANS}, C_{DES} \Delta)$$

Where:
- $l_{RANS}$ = RANS length scale (e.g., $k^{3/2}/\epsilon$ for k-ε)
- $C_{DES}$ = calibration constant (typically 0.65)
- $\Delta$ = local grid spacing (usually max(Δx, Δy, Δz))

**Switching behavior:**
- Near walls: $l_{RANS} < C_{DES}\Delta$ → RANS mode
- Separated regions: $C_{DES}\Delta < l_{RANS}$ → LES mode

### 2.3 DES Variants

| Variant | Key Feature | Pros | Cons | When to Use |
|---------|-------------|------|------|-------------|
| **DES (original)** | Simple min switching | Easy to implement | Prone to Grid-Induced Separation (GIS) | Research only |
| **DDES** (Delayed DES) | Shield function prevents early switch | Prevents GIS in thick boundary layers | Slightly more complex | Most general-purpose cases |
| **IDDES** (Improved DDES) | Hybrid DES + wall-modeled LES | Best near-wall treatment | Most complex setup | High Re with thin boundary layers |

**Grid-Induced Separation (GIS):**
- Occurs when grid is refined in RANS region
- Causes premature switch to LES mode
- Results in "artificial separation" due to modeled stress depletion
- **DDES prevents this** with shielding function based on eddy viscosity

### 2.4 How to Set Up DES in OpenFOAM

#### Step 1: Mesh Requirements

**Hybrid meshing strategy:**

| Zone | y+ Requirement | Cell Size | Aspect Ratio | Notes |
|------|----------------|-----------|--------------|-------|
| Near-wall (RANS) | 30-100 | Moderate | Can be high | Use wall functions |
| Separated region (LES) | Refined | Isotropic | ≈ 1-20 | Resolve eddies |
| Interface | Gradual transition | Smooth change | — | Avoid abrupt jumps |

**⚠️ Critical: DO NOT over-refine in attached boundary layer regions**
- Excessive refinement in RANS zone triggers premature LES mode
- This causes Grid-Induced Separation (GIS)
- Refine only where separation is expected or confirmed

```cpp
// Example: snappyHexMesh refinement regions
refinementRegions
{
    wakeRegion
    {
        mode            inside;
        levels          ((1E5 4) (1E4 3));  // Refine in wake
    }

    // Don't refine near-wall attached region!
}
```

#### Step 2: Configure turbulenceProperties

```cpp
// constant/turbulenceProperties
simulationType DES;

DES
{
    // Model selection
    DESModel        SpalartAllmarasDDES;  // Options:
                                           // SpalartAllmarasDES
                                           // SpalartAllmarasDDES (recommended)
                                           // SpalartAllmarasIDDES (best for thin BL)

    turbulence      on;

    // DES coefficient
    CDES            0.65;  // Default for Spalart-Allmaras
                           // Lower = more RANS, Higher = more LES
                           // 0.65 is standard calibration

    // If using IDDES:
    // IDDESCoeffs
    // {
    //     cT         1.87;   // Grid spacing parameter
    //     cT2        1.0;    // Additional parameter
    //     // ... see OpenFOAM documentation for full list
    // }
}
```

#### Step 3: Initial and Boundary Conditions

```cpp
// 0/nut (eddy viscosity for Spalart-Allmaras)
dimensions      [0 2 -1 0 0 0 0];

internalField   uniform 1e-4;

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 1e-4;
    }
    outlet
    {
        type            zeroGradient;
    }
    walls
    {
        type            nutkWallFunction;  // RANS wall treatment
        value           uniform 0;
    }
}
```

```cpp
// 0/nuTilda (Spalart-Allmaras working variable)
dimensions      [0 2 -1 0 0 0 0];

internalField   uniform 1e-4;

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 5e-4;  // Typical inlet value
    }
    outlet
    {
        type            zeroGradient;
    }
    walls
    {
        type            nutkWallFunction;
        value           uniform 0;
    }
}
```

#### Step 4: Solver Settings

```cpp
// system/controlDict
application     pimpleFoam;

startFrom       latestTime;

controls
{
    maxCo       0.8;  // Slightly higher than pure LES
    maxAlphaCo  1.0;
}
```

```cpp
// system/fvSchemes
ddtSchemes
{
    default         backward;
}

gradSchemes
{
    default         Gauss linear;
}

divSchemes
{
    default         Gauss limitedLinearV 1;
    div(phi,nuTilda) Gauss limitedLinear 1;
}

laplacianSchemes
{
    default         Gauss linear corrected;
}
```

### 2.5 DES Workflow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                  DES SIMULATION WORKFLOW                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. PRE-PROCESSING                                           │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ • Identify separation zones (from experiments/RANS) │    │
│  │ • Create hybrid mesh:                               │    │
│  │   - Near-wall: y+ ≈ 30-100 (RANS zone)            │    │
│  │   - Separated: isotropic, refined (LES zone)       │    │
│  │ • ⚠️ DO NOT over-refine attached BL regions       │    │
│  └─────────────────────────────────────────────────────┘    │
│                           ↓                                   │
│  2. TURBULENCE SETUP                                         │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ • simulationType DES                                │    │
│  │ • Choose model: SpalartAllmarasDDES (recommended)  │    │
│  │ • Set CDES = 0.65 (standard)                       │    │
│  │ • Set maxCo ≤ 0.8                                   │    │
│  └─────────────────────────────────────────────────────┘    │
│                           ↓                                   │
│  3. INITIAL CONDITIONS                                       │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ • nuTilda: initialize from RANS solution           │    │
│  │ • Run preliminary RANS for better IC (recommended) │    │
│  │ • Map RANS → DES fields (mapFields)               │    │
│  └─────────────────────────────────────────────────────┘    │
│                           ↓                                   │
│  4. SOLVE                                                    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ • Run pimpleFoam                                    │    │
│  │ • Monitor DES mode (RANS vs LES regions)           │    │
│  │ • Check for GIS (artificial separation)            │    │
│  │ • Sample statistics after flow development         │    │
│  └─────────────────────────────────────────────────────┘    │
│                           ↓                                   │
│  5. VALIDATION                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ • Verify RANS mode in attached BL                  │    │
│  │ • Verify LES mode in separated regions             │    │
│  │ • Check resolved turbulent content                 │    │
│  │ • Compare to experimental data if available        │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 2.6 Monitoring DES Behavior

**Check RANS vs LES regions:**
```bash
# Post-process DES length scale
postProcess -func " DESLengthScale"

# Visualize l_RANS vs C_DES*Δ
# In ParaFOAM: Look for regions where l_RANS ≈ C_DES*Δ (transition zone)
```

**Identify Grid-Induced Separation:**
- Check for separation in regions where experiments show attached flow
- Examine mesh refinement in RANS zones (should be moderate)
- Compare RANS solution: if DES separates earlier, likely GIS

### 2.7 Practical DES Exercise: Flow Past a Cube

**Objective:** Set up DES for turbulent flow over a surface-mounted cube (Re_H = 40,000).

**Steps:**
1. Create mesh with:
   - y+ ≈ 50 on cube surfaces and floor (RANS zone)
   - Refined wake region (LES zone)
   - Gradual transition at separation lines
2. Set up SpalartAllmarasDDES model
3. Initialize from RANS solution
4. Monitor DES switching behavior
5. Compare wake statistics and Strouhal number to experiments

---

## 3. Transition Modeling

### 3.1 Why Model Transition?

**Motivation:** Standard RANS models assume fully turbulent flow everywhere. For low-to-moderate Reynolds number flows, this can:

- **Overpredict skin friction** (laminar BL has lower drag)
- **Miss separation bubbles** (laminar separation → turbulent reattachment)
- **Inaccurate lift prediction** (transition affects pressure distribution)

**When to use transition modeling:**
- External aerodynamics at low Re (airfoils, wings, wind turbines)
- Turbomachinery (compressor/turbine blades)
- Heat transfer applications (transition affects Nusselt number)
- Natural convection (laminar → turbulent transition)
- Low Re water flows (marine propellers, underwater vehicles)

**When NOT to use transition modeling:**
- High Re flows (Re > 10⁷) with naturally turbulent boundary layers
- Internal flows with high disturbance levels
- When turbulence intensity is high (> 5%)

### 3.2 What is Transition? (Physical Mechanisms)

| Transition Type | Physical Mechanism | Trigger | Typical Applications |
|----------------|-------------------|---------|---------------------|
| **Natural transition** | Tollmien-Schlichting (T-S) waves | Low free-stream turbulence (< 0.5%) | Clean airfoils, smooth surfaces |
| **Bypass transition** | Bypass of T-S waves, streak growth | High turbulence intensity (> 1%) | Turbomachinery, rough surfaces |
| **Separation-induced transition** | Laminar separation bubble → turbulent reattachment | Adverse pressure gradient at low Re | Low Re airfoils (Re < 500,000) |
| **Crossflow transition** | Crossflow instability in 3D BL | Sweep angle, pressure gradient | Swept wings, turbomachinery blades |

**Key parameters:**
- **Tu (turbulence intensity):** Free-stream disturbance level
- **Reθ (momentum thickness Reynolds number):** Critical threshold for transition
- **Pressure gradient:** Accelerating (stabilizing) vs. decelerating (destabilizing)
- **Surface roughness:** Trips transition earlier

### 3.3 The γ-Reθ Model

**Concept:** Two-equation model that tracks:
- **γ (gamma):** Intermittency (0 = laminar, 1 = turbulent)
- **Reθ:** Momentum thickness Reynolds number (controls transition onset)

**Transport equations:**

**Intermittency (γ):**
$$\frac{\partial (\rho \gamma)}{\partial t} + \frac{\partial (\rho u_j \gamma)}{\partial x_j} = P_\gamma - E_\gamma + \frac{\partial}{\partial x_j}\left[(\nu + \frac{\nu_t}{\sigma_\gamma})\frac{\partial \gamma}{\partial x_j}\right]$$

**Transition momentum thickness Re (Reθ):**
$$\frac{\partial (\rho \tilde{R}e_\theta)}{\partial t} + \frac{\partial (\rho u_j \tilde{R}e_\theta)}{\partial x_j} = P_{\theta} + \frac{\partial}{\partial x_j}\left[\sigma_{\theta}(\nu + \nu_t)\frac{\partial \tilde{R}e_\theta}{\partial x_j}\right]$$

**Coupling with turbulence model:**
- Eddy viscosity is multiplied by intermittency: $\nu_{t,eff} = \nu_t \cdot \gamma$
- In laminar regions (γ → 0): turbulence production is suppressed
- In turbulent regions (γ → 1): standard RANS behavior

### 3.4 How to Set Up Transition Modeling in OpenFOAM

#### Step 1: Prerequisites

**Required turbulence model:**
- k-ω SST (most common and recommended)
- Can work with other models but SST is best calibrated

**Grid requirements:**
- y+ ≈ 1 (resolve viscous sublayer for accurate transition prediction)
- Similar resolution to wall-resolved LES in boundary layer
- Adequate streamwise resolution to capture transition region

#### Step 2: Configure turbulenceProperties

```cpp
// constant/turbulenceProperties
simulationType RAS;

RAS
{
    // Base turbulence model (MUST be SST)
    RASModel        kOmegaSST;

    turbulence      on;

    // Enable transition modeling
    transition      on;

    // Transition model
    transitionModel gammaReTheta;  // Langtry-Menter γ-Reθ model

    // γ-Reθ coefficients
    gammaReThetaCoeffs
    {
        // Transition onset correlation
        maxTransitionLength 50;    // Max transition length (dimensionless)
        criticalReThet      200;   // Critical Reθ for transition

        // Empirical correlations (usually defaults are fine)
        ca1                 2.0;
        ca2                 0.06;
        ce1                 1.0;
        ce2                 50.0;
        cTheta              0.03;
        sigmaTheta          2.0;
    }

    // Standard SST coefficients
    kOmegaSSTCoeffs
    {
        // ... (standard SST settings)
    }
}
```

#### Step 3: Initial and Boundary Conditions

**Additional fields required:**

```cpp
// 0/gamma (intermittency)
dimensions      [0 0 0 0 0 0 0];

internalField   uniform 1;  // Start fully turbulent (converges faster)

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 1;  // Free-stream intermittency
                                   // Use 1 for external flows
    }
    outlet
    {
        type            zeroGradient;
    }
    walls
    {
        type            zeroGradient;
    }
}
```

```cpp
// 0/ReTheta (transition momentum thickness Reynolds number)
dimensions      [0 0 0 0 0 0 0];

internalField   uniform 1000;  // Initial guess

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 1000;  // Estimate from experiments
                                      // Higher Tu → lower ReThetat
    }
    outlet
    {
        type            zeroGradient;
    }
    walls
    {
        type            zeroGradient;
    }
}
```

```cpp
// 0/thetat (transition onset momentum thickness Re)
dimensions      [0 0 0 0 0 0 0];

internalField   uniform 200;

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 200;  // Critical Reθ
    }
    outlet
    {
        type            zeroGradient;
    }
    walls
    {
        type            zeroGradient;
    }
}
```

**Standard k and omega fields:**

```cpp
// 0/k (turbulent kinetic energy)
boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 0.01;  // Based on Tu: k = 1.5(U·Tu)²
                                      // For Tu = 2%, U = 10 m/s: k ≈ 0.006
    }
    // ...
}
```

```cpp
// 0/omega (specific dissipation rate)
boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 1000;  // Based on turbulent length scale
                                       // ω = k^0.5/(l·C^0.25)
    }
    // ...
}
```

#### Step 4: Estimating Inlet Values

**From turbulence intensity (Tu) and length scale (l):**

```python
# Python example for calculating inlet values
U = 10.0           # Free-stream velocity [m/s]
Tu = 0.02          # Turbulence intensity [2%]
l = 0.01           # Turbulent length scale [m]
nu = 1.5e-5        # Kinematic viscosity [m²/s]

k = 1.5 * (U * Tu)**2
omega = k**0.5 / (l * 0.09**0.25)
ReTheta = 1000 + 2000 * Tu  # Approximate correlation

print(f"k = {k:.6f} m²/s²")
print(f"omega = {omega:.2f} 1/s")
print(f"ReTheta = {ReTheta:.0f}")
```

#### Step 5: Solver Settings

```cpp
// system/controlDict
application     pimpleFoam;

startFrom       latestTime;

controls
{
    maxCo       0.5;  // Lower than standard RANS for stability
}
```

```cpp
// system/fvSchemes
ddtSchemes
{
    default         Euler;  // Start with first-order for stability
    // Later switch to backward for accuracy
}

gradSchemes
{
    default         Gauss linear;
}

divSchemes
{
    default         Gauss upwind;  // Start with upwind for stability
    // Later switch to limitedLinear for accuracy
    div(phi,k)      Gauss limitedLinear 1;
    div(phi,omega)  Gauss limitedLinear 1;
    div(phi,gamma)  Gauss limitedLinear 1;
    div(phi,ReTheta) Gauss limitedLinear 1;
}

laplacianSchemes
{
    default         Gauss linear corrected;
}
```

### 3.5 Practical Transition Modeling Exercise: Airfoil at Low Re

**Objective:** Predict transition on NACA 0012 airfoil at Re_c = 200,000, α = 2°.

**Steps:**
1. Create C-mesh around airfoil with y+ ≈ 1
2. Set boundary conditions:
   - Inlet Tu = 0.1% (clean wind tunnel)
   - Reθ ≈ 200 (laminar conditions)
   - gamma = 1 at inlet (allows model to find transition)
3. Run with kOmegaSST + gammaReTheta
4. Compare:
   - Skin friction distribution (look for transition region)
   - Lift and drag vs. fully turbulent case
   - Transition location vs. XFOIL predictions

**Expected results:**
- Transition at x/c ≈ 0.3-0.5 (depends on Tu)
- Lower drag than fully turbulent
- Possible laminar separation bubble near leading edge

### 3.6 Troubleshooting Transition Models

| Issue | Symptom | Solution |
|-------|---------|----------|
| No transition predicted | γ = 1 everywhere | Check inlet Tu, reduce Reθ, verify mesh resolution |
| Early transition | γ drops too quickly | Increase inlet Reθ, decrease Tu |
| Unstable solution | Oscillations in γ | Reduce maxCo, use upwind schemes initially |
| Wrong transition location | γ transitions at wrong x | Adjust Reθ based on experimental data |

---

## 4. Summary and Key Takeaways

### 4.1 Model Selection Summary

**Model Selection Guide:**
- **RANS:** Use for attached flows, steady-state calculations, initial design iterations
- **Transition modeling:** Add for low Re external flows, turbomachinery, when transition affects performance
- **DES:** Use for high Re flows with massive separation where LES is too expensive
- **LES:** Use for fundamental studies, moderate Re flows, when detailed unsteady information is needed

**Computational Cost Hierarchy:**
```
RANS (baseline) → Transition (+20-50%) → DES (5-20×) → LES (100×) → DNS (10,000×)
```

**Critical Success Factors:**

| Aspect | LES | DES | Transition |
|--------|-----|-----|------------|
| Mesh quality | ⭐⭐⭐⭐⭐ Critical | ⭐⭐⭐⭐ Important | ⭐⭐⭐⭐ Important |
| Time step (CFL) | ⭐⭐⭐⭐⭐ Critical | ⭐⭐⭐⭐ Important | ⭐⭐⭐ Moderate |
| Initial conditions | ⭐⭐⭐⭐ Important | ⭐⭐⭐⭐ Important | ⭐⭐⭐ Important |
| Boundary conditions | ⭐⭐⭐ Important | ⭐⭐⭐ Important | ⭐⭐⭐⭐ Critical (Tu) |
| Physical modeling | ⭐⭐⭐ SGS choice | ⭐⭐⭐⭐ Model variant | ⭐⭐⭐⭐⭐ Calibration |

### 4.2 Common Pitfalls and Solutions

| Pitfall | Consequence | Solution |
|---------|-------------|----------|
| Using LES on too-coarse mesh | Excessive dissipation, wrong results | Verify Δ+ requirements, use finer mesh or switch to DES |
| Over-refining DES mesh in RANS zone | Grid-induced separation (GIS) | Use DDES/IDDES, keep moderate refinement in attached BL |
| Neglecting transition at low Re | Overpredicted drag, wrong separation location | Use γ-Reθ model when Re < 10⁶ for external flows |
| CFL too high for LES | Temporal aliasing, wrong dynamics | Keep maxCo ≤ 0.5, monitor Co distribution |
| Insufficient sampling time | Poor statistics, noisy results | Sample for > 10 large-eddy turnover times |
| Wrong inlet turbulence | Wrong transition/separation behavior | Match experimental Tu and length scale |

### 4.3 Quick Reference Tables

**LES SGS Model Selection:**

| Application | Recommended Model | Cs/Settings |
|-------------|-------------------|-------------|
| General flows | Smagorinsky | Cs = 0.1-0.15 |
| Wall-bounded | WALE | Default settings |
| Complex flows | dynamicKEqn | Dynamic calculation |
| High accuracy | kEqn | Solve SGS k-equation |

**DES Variant Selection:**

| Application | Recommended Model | Notes |
|-------------|-------------------|-------|
| General purpose | SpalartAllmarasDDES | Prevents GIS |
| High Re, thin BL | SpalartAllmarasIDDES | Wall-modeled LES capability |
| Research (old cases) | SpalartAllmarasDES | May have GIS issues |

**Transition Model Applications:**

| Flow Type | Tu Range | Expected Transition |
|-----------|----------|-------------------|
| Clean wind tunnel | 0.1-0.5% | Late (x/c > 0.5) |
| Atmosphere (low) | 1-2% | Moderate (x/c ≈ 0.3-0.5) |
| Turbomachinery | 3-10% | Early (x/c < 0.2) |
| Rough surfaces | > 5% | Very early |

### 4.4 Workflow Quick Guides

**LES Quick Start:**
```bash
# 1. Check mesh resolution
checkMesh
python3 calculate_yplus.py  # Verify y+ ≈ 1, Δ+ ≈ 50

# 2. Set up turbulence
# constant/turbulenceProperties: simulationType LES;
# constant/turbulenceProperties: LESModel Smagorinsky;

# 3. Set time step
# system/controlDict: maxCo 0.5;

# 4. Run
pimpleFoam

# 5. Monitor
tail -f log.pimpleFoam | grep Co
```

**DES Quick Start:**
```bash
# 1. Create hybrid mesh
# Near-wall: y+ ≈ 50, moderate resolution
# Wake: refined, isotropic

# 2. Run RANS first
simpleFoam  # Get good initial conditions

# 3. Switch to DES
# constant/turbulenceProperties: simulationType DES;
# constant/turbulenceProperties: DESModel SpalartAllmarasDDES;

# 4. Continue DES run
pimpleFoam
```

**Transition Quick Start:**
```bash
# 1. Create fine mesh with y+ ≈ 1
# 2. Estimate inlet conditions
# k = 1.5*(U*Tu)^2
# omega = k^0.5/(l*0.09^0.25)

# 3. Set up transition model
# constant/turbulenceProperties: transitionModel gammaReTheta;

# 4. Initialize gamma and ReTheta
# 0/gamma: internalField uniform 1
# 0/ReTheta: internalField uniform 1000

# 5. Run
pimpleFoam

# 6. Check transition location
# Look for gamma dropping from 1 to 0 then returning to 1
```

---

## 5. Practical Exercises

### Exercise 1: LES of Backward-Facing Step

**Objective:** Validate LES setup against experimental data.

**Setup:**
- Re_h = 5,000 (based on step height)
- Mesh: y+ ≈ 1, Δx+ ≈ 50, Δz+ ≈ 15
- SGS model: Smagorinsky with Cs = 0.1
- Time step: maxCo ≤ 0.5

**Tasks:**
1. Generate appropriate mesh
2. Set up LES with Smagorinsky model
3. Run until statistical convergence
4. Compare reattachment length (x_r/h) to experiments (~6-7)
5. Extract mean velocity profiles at various x/h locations

**Expected outcome:** Accurate prediction of reattachment length and turbulent statistics.

### Exercise 2: DES of Flow Around a Cylinder

**Objective:** Compare DES vs. RANS for vortex shedding.

**Setup:**
- Re_D = 100,000 (subcritical)
- Mesh: hybrid RANS-LES
- Model: SpalartAllmarasDDES
- Compare to RANS (k-ω SST)

**Tasks:**
1. Create mesh with y+ ≈ 50 on cylinder surface
2. Refine wake region for LES mode
3. Run both RANS and DES
4. Compare:
   - Strouhal number (St ≈ 0.2 for this Re)
   - Lift and drag coefficients
   - Wake structure and vortex shedding

**Expected outcome:** DES captures unsteady vortex shedding, RANS does not.

### Exercise 3: Transition Modeling on Airfoil

**Objective:** Predict transition location at low Re.

**Setup:**
- Airfoil: NACA 0012
- Re_c = 200,000, α = 2°
- Mesh: C-mesh with y+ ≈ 1
- Model: k-ω SST + γ-Reθ

**Tasks:**
1. Generate fine boundary layer mesh
2. Set inlet Tu = 0.5% (clean tunnel)
3. Run with and without transition model
4. Compare:
   - Skin friction coefficient Cf
   - Drag coefficient (Cd)
   - Transition location vs. XFOIL

**Expected outcome:** Transition model predicts delayed transition and lower drag compared to fully turbulent.

---

## Concept Check Questions

<details>
<summary><b>1. What is the fundamental difference between LES and RANS?</b></summary>

**Answer:**
- **RANS:** Time-averages all turbulence fluctuations, models everything with eddy viscosity
- **LES:** Spatially filters equations, resolves large eddies directly, models only small subgrid scales
- **Result:** LES captures unsteady, large-scale turbulent structures that RANS cannot
</details>

<details>
<summary><b>2. Why is DES more efficient than wall-resolved LES for high Re flows?</b></summary>

**Answer:**
- **Wall-resolved LES:** Requires y+ ≈ 1 everywhere → extremely fine mesh near walls → ~100× RANS cost
- **DES:** Uses RANS in boundary layer (y+ ≈ 30-100) + LES only in separated regions → 5-20× RANS cost
- **Savings:** Near-wall resolution dominates cell count for high Re; DES avoids this by using RANS there
</details>

<details>
<summary><b>3. What is Grid-Induced Separation (GIS) and how does DDES prevent it?</b></summary>

**Answer:**
- **GIS:** Occurs when DES switches to LES mode too early in attached boundary layers due to local mesh refinement
- **Consequence:** Artificial separation because RANS-modeled stresses are depleted
- **DDES solution:** Adds "delay function" that keeps model in RANS mode in thick boundary layers, even if mesh is locally refined
- **Key:** DDES shields the RANS mode from premature switching
</details>

<details>
<summary><b>4. When should you use transition modeling instead of fully turbulent RANS?</b></summary>

**Answer:**
Use transition modeling when:
- Reynolds number is low to moderate (Re < 10⁶ for external flows)
- Free-stream turbulence intensity is low (< 3%)
- Laminar regions significantly affect performance (drag, lift, heat transfer)
- Applications: Low Re airfoils, turbomachinery, wind turbines, some heat transfer cases
- **Skip transition** for high Re flows (> 10⁷) or high turbulence environments
</details>

<details>
<summary><b>5. What are the additional fields required for γ-Reθ transition modeling?</b></summary>

**Answer:**
Three additional fields beyond standard k-ω SST:
1. **gamma (γ):** Intermittency (0 = laminar, 1 = turbulent)
2. **ReTheta:** Transition momentum thickness Reynolds number
3. **thetat:** Critical Reθ at transition onset

These fields are transported and coupled to the turbulence model via intermittency.
</details>

<details>
<summary><b>6. What are the mesh requirements for wall-resolved LES?</b></summary>

**Answer:**
- **y+ ≈ 1** (resolve viscous sublayer)
- **Streamwise spacing:** Δx+ ≈ 50-100
- **Spanwise spacing:** Δz+ ≈ 15-30
- **Cell aspect ratio:** ≈ 1 (isotropic) in core, up to 20-40 near walls
- **CFL number:** 0.3-0.5 for temporal accuracy

These requirements make wall-resolved LES extremely expensive at high Re.
</details>

<details>
<summary><b>7. How do you choose between Smagorinsky, WALE, and dynamic SGS models for LES?</b></summary>

**Answer:**
- **Smagorinsky:** Default choice, simple, robust. Good for general flows.
- **WALE:** Better near-wall behavior (correct y³ scaling). Use for wall-bounded flows.
- **dynamicKEqn:** Adapts Cs to local flow conditions. Good for complex flows with varying turbulence.
- **Choice:** Start with Smagorinsky; switch to WALE for wall-bounded cases or dynamic for complex flows.
</details>

---

## Related Documents

### Within This Module
- **Prerequisites:**
  - [Turbulence Fundamentals](01_Turbulence_Fundamentals.md) - RANS basics, turbulence scales
  - [Wall Treatment](03_Wall_Treatment.md) - y+ concepts, wall functions

### Complementary Topics
- **High-Performance Computing:** [01_High_Performance_Computing.md](01_High_Performance_Computing.md) - Parallel scaling for LES/DES
- **Numerical Methods:** [03_Numerical_Methods.md](03_Numerical_Methods.md) - Discretization schemes and AMR
- **Mesh Quality:** [Module 02, Section 05](../../MODULE_02_MESHING_AND_CASE_SETUP/CONTENT/05_MESH_QUALITY_AND_MANIPULATION/01_Mesh_Quality_Criteria.md) - Mesh requirements

### Further Reading
- Pope, S. B. (2000). *Turbulent Flows*. Cambridge University Press. (Chapters 10-13 for LES)
- Sagaut, P. (2006). *Large Eddy Simulation for Incompressible Flows*. Springer.
- Langtry, R. B., & Menter, F. R. (2009). "Correlation-based transition modeling for unstructured parallelized computational fluid dynamics codes." *AIAA Journal*, 47(12).
- Spalart, P. R., et al. (2006). "A new version of detached-eddy simulation, resistant to ambiguous grid densities." *Theoretical and Computational Fluid Dynamics*, 20(3).

---

**Last Updated:** 2025-12-30