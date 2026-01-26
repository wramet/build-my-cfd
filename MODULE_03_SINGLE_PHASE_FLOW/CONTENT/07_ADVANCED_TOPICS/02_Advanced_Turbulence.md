# Advanced Turbulence Models

**LES, DES, and Transition Modeling for Flows Where RANS is Insufficient**

**Estimated Reading Time:** 35-40 minutes

---

## Learning Objectives

By the end of this section, you will be able to:

- **Identify** when to use advanced turbulence modeling (LES/DES/transition) instead of standard RANS approaches
- **Explain** the fundamental differences between LES, DES, and transition modeling approaches
- **Configure** LES simulations with appropriate SGS models and mesh requirements in OpenFOAM
- **Set up** DES simulations with proper RANS-LES hybrid meshing strategies
- **Implement** transition modeling using the γ-Reθ model for practical engineering flows
- **Evaluate** computational costs and accuracy trade-offs between different turbulence approaches
- **Diagnose** common issues like Grid-Induced Separation and incorrect transition prediction

---

## Prerequisites

**Essential Knowledge:**
- **Turbulence Fundamentals** ([Module 03, Section 03](03_TURBULENCE_MODELING/01_Turbulence_Fundamentals.md)) - RANS equations, turbulence scales, k-ε and k-ω SST models
- **Wall Treatment** ([Module 03, Section 03](03_TURBULENCE_MODELING/03_Wall_Treatment.md)) - y+ concepts, wall functions vs. resolved boundary layers
- **Basic OpenFOAM Setup** ([Module 02](../../MODULE_02_MESHING_AND_CASE_SETUP/)) - Creating case directories, setting boundary conditions
- **Mesh Quality** ([Module 02, Section 05](../../MODULE_02_MESHING_AND_CASE_SETUP/CONTENT/05_MESH_QUALITY_AND_MANIPULATION/01_Mesh_Quality_Criteria.md)) - Mesh requirements for different flow regimes

**Recommended Background:**
- **RANS Models** ([Module 03, Section 03](03_TURBULENCE_MODELING/02_RANS_Models.md)) - Understanding of k-ε, k-ω, and Spalart-Allmaras models
- **Numerical Methods** ([Module 03, Section 07](07_ADVANCED_TOPICS/01_Numerical_Methods.md)) - Discretization schemes (helpful for LES stability)

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

**Quick decision tree:**
```
Need unsteady features?
├─ No → Use RANS (fastest)
└─ Yes
   ├─ Low Re (< 10⁶) + thin boundary layers?
   │  └─ Yes → Use wall-resolved LES (most accurate)
   ├─ High Re (> 10⁶) + wall-bounded?
   │  └─ Yes → Use DES (balance accuracy/cost)
   └─ Separated flows without walls?
      └─ Yes → Use LES (best accuracy)

Need transition prediction?
├─ Yes (Re < 10⁶, low Tu) → Use γ-Reθ model
└─ No → Fully turbulent RANS
```

---

## 1. Large Eddy Simulation (LES)

### 1.1 Why Use LES?

**Motivation:** RANS models time-average all turbulence fluctuations, which works well for steady, attached flows but fails for flows dominated by unsteady, coherent structures. LES bridges this gap by:

- **Resolving** large, energy-carrying eddies directly (which are flow-dependent and cannot be modeled universally)
- **Modeling** only small, isotropic eddies (which are more universal and easier to model)
- **Capturing** unsteady phenomena like vortex shedding, bluff body wakes, and mixing layers naturally

**When to choose LES:**
- You need accurate unsteady flow features (vortex shedding, acoustic sources, mixing)
- The flow is dominated by large-scale turbulent structures
- Computational resources are sufficient (factor of ~100× RANS for wall-resolved)
- Reynolds number is moderate (Re < 10⁶ for wall-resolved LES)
- You need detailed spectral or frequency-domain information

**When NOT to choose LES:**
- High Reynolds number with thin boundary layers (use DES or wall-modeled LES instead)
- Only steady-state statistics are needed (RANS may suffice)
- Computational budget is limited (DES is more efficient)
- High Re external aerodynamics with attached boundary layers (DES better)

### 1.2 What is LES? (Theoretical Foundation)

**Concept:** Spatial filtering of Navier-Stokes equations separates resolved scales from subgrid scales (SGS).

**Filtered Navier-Stokes Equations:**
$$\frac{\partial \bar{u}_i}{\partial t} + \bar{u}_j\frac{\partial \bar{u}_i}{\partial x_j} = -\frac{1}{\rho}\frac{\partial \bar{p}}{\partial x_i} + \nu\frac{\partial^2 \bar{u}_i}{\partial x_j^2} - \frac{\partial \tau_{ij}}{\partial x_j}$$

Where:
-1$\bar{u}_i1= filtered (resolved) velocity
-1$\tau_{ij} = \overline{u_i u_j} - \bar{u}_i \bar{u}_j1= subgrid-scale stress tensor (must be modeled)

**Filtering operation:**
$$\bar{u}(\mathbf{x}) = \int G(\mathbf{x} - \mathbf{x'}; \Delta) u(\mathbf{x'}) d\mathbf{x'}$$

Where1$G1is the filter function and1$\Delta1is the filter width (typically related to cell size).

**Subgrid-Scale (SGS) Models:**

**Smagorinsky Model (most common):**
$$\nu_t = (C_s \Delta)^2 |\bar{S}|$$

Where:
-1$C_s1= Smagorinsky constant (typically 0.1-0.2)
-1$\Delta1= filter width (usually cube root of cell volume)
-1$|\bar{S}| = \sqrt{2\bar{S}_{ij}\bar{S}_{ij}}1= strain rate magnitude

**Dynamic Smagorinsky:**
-1$C_s1computed dynamically during simulation
- Better for complex flows with varying turbulence characteristics
- Can backscatter (energy from small to large scales)
- More expensive and potentially unstable

**WALE (Wall-Adapting Local Eddy-viscosity):**
- Better near-wall behavior
- Correct1$y^31scaling near walls
- Recommended for wall-bounded flows
- Zero eddy viscosity in pure shear (automatically)

**k-equation SGS:**
- Solves transport equation for SGS turbulent kinetic energy
- More expensive but more accurate for complex flows
- Better for flows with rapid changes in turbulence

| SGS Model | Advantages | Disadvantages | Typical Use |
|-----------|------------|---------------|-------------|
| Smagorinsky | Simple, robust, stable | Over-dissipates, poor near walls | General flows, initial studies |
| dynamicKEqn | Adapts to flow, backscatter | Can be unstable, expensive | Complex flows with varying turbulence |
| WALE | Good wall behavior, automatic | More complex | Wall-bounded flows |
| kEqn | More physical, accurate | Expensive | High-accuracy requirements |

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

Where1$Re_L1is Reynolds number based on length1$L1and boundary layer thickness1$\delta$.

**Example:** For Re = 10⁶ with L/δ = 100:
$$N_{LES} \approx \frac{10^6}{144} \times 100^3 \approx 7 \times 10^{10} \text{ cells (impractical)}$$

This demonstrates why wall-resolved LES is impractical at high Re.

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

    // If using WALE:
    // WALECoeffs
    // {
    //     Ck          0.094;
    //     Cw          0.325;
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

**Key files to create:**
- `constant/polyMesh/blockMeshDict` - Channel mesh
- `constant/turbulenceProperties` - LES configuration
- `0/U`, `0/p`, `0/k`, `0/nuSgs` - Initial/boundary conditions
- `system/controlDict`, `system/fvSchemes`, `system/fvSolution` - Solver settings

**Validation data:**
- Mean velocity: u+ = y+ for y+ < 5 (viscous sublayer)
- Log-law region: u+ = (1/κ) ln(y+) + B, κ ≈ 0.41, B ≈ 5.0

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
- External aerodynamics at moderate to high Re

**When NOT to choose DES:**
- Attached flows (RANS is sufficient and faster)
- Purely separated flows without walls (LES is better and simpler)
- Cases with ambiguous RANS-LES transition (may cause GIS)
- Very low Re flows (wall-resolved LES may be feasible)

### 2.2 What is DES? (Theoretical Foundation)

**Concept:** Hybrid RANS-LES model that switches based on grid spacing.

**Length Scale Modification:**
$$l_{DES} = \min(l_{RANS}, C_{DES} \Delta)$$

Where:
-1$l_{RANS}1= RANS length scale (e.g.,1$k^{3/2}/\epsilon1for k-ε, or1$\tilde{\nu}/S1for Spalart-Allmaras)
-1$C_{DES}1= calibration constant (typically 0.65)
-1$\Delta1= local grid spacing (usually max(Δx, Δy, Δz))

**Switching behavior:**
- Near walls:1$l_{RANS} < C_{DES}\Delta1→ RANS mode (modeled turbulence)
- Separated regions:1$C_{DES}\Delta < l_{RANS}1→ LES mode (resolved turbulence)

**Eddy viscosity modification:**
$$\nu_t = \frac{l_{DES}^2}{\nu} |\tilde{S}|$$

This ensures that:
- In RANS regions: standard RANS eddy viscosity
- In LES regions: SGS eddy viscosity with length scale ≈ Δ

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

**DDES shielding function:**
$$f_d = 1 - \tanh\left([\beta_1 d]^2\right)$$

Where:
-1$d1= distance to wall
-1$\beta_11= calibration parameter
-1$f_d → 11in LES region,1$f_d → 01in RANS region

**IDDES additional features:**
- Wall-modeled LES capability in near-wall region
- Better handling of "gray area" between RANS and LES
- More accurate for flows with thin boundary layers

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

**Recommended meshing workflow:**
1. Start with coarse mesh, run RANS to identify separation zones
2. Refine only in separated regions
3. Keep moderate resolution in attached boundary layers
4. Use gradual refinement (max 2:1 size ratio between adjacent cells)

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

**Model selection guidelines:**
- **SpalartAllmarasDDES**: Default choice for most applications (prevents GIS)
- **SpalartAllmarasIDDES**: Use for high Re flows with thin boundary layers
- **SpalartAllmarasDES**: Avoid unless validating against old cases

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

**Best practice: Initialize from RANS solution**
```bash
# 1. Run RANS first
simpleFoam

# 2. Map RANS solution to DES case
mapFields ../ransCase -consistent

# 3. Switch turbulenceProperties to DES
# 4. Continue with pimpleFoam
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

**Visualization in ParaView:**
1. Load `DESLenghtScale` field
2. Compare `l_RANS` and `C_DES*Δ`
3. Identify transition zones where they are equal
4. Check for unexpected early transitions

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

**Expected validation:**
- Strouhal number St ≈ 0.1-0.15 for vortex shedding
- Recirculation length L/H ≈ 1-2
- Reynolds stress distribution in wake

---

## 3. Transition Modeling

### 3.1 Why Model Transition?

**Motivation:** Standard RANS models assume fully turbulent flow everywhere. For low-to-moderate Reynolds number flows, this can:

- **Overpredict skin friction** (laminar BL has lower drag)
- **Miss separation bubbles** (laminar separation → turbulent reattachment)
- **Inaccurate lift prediction** (transition affects pressure distribution)
- **Wrong heat transfer** (laminar vs. turbulent Nusselt number differs significantly)

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
- When transition location is known to be very near leading edge

**Impact of transition (example: airfoil at Re = 200,000):**
| Parameter | Fully Turbulent | With Transition | Difference |
|-----------|----------------|-----------------|------------|
| Drag coefficient Cd | 0.025 | 0.015 | -40% |
| Lift coefficient Cl | 0.8 | 0.9 | +12.5% |
| Transition location | N/A (x/c = 0) | x/c = 0.4 | — |

### 3.2 What is Transition? (Physical Mechanisms)

**Transition types:**

| Transition Type | Physical Mechanism | Trigger | Typical Applications |
|----------------|-------------------|---------|---------------------|
| **Natural transition** | Tollmien-Schlichting (T-S) waves | Low free-stream turbulence (< 0.5%) | Clean airfoils, smooth surfaces |
| **Bypass transition** | Bypass of T-S waves, streak growth | High turbulence intensity (> 1%) | Turbomachinery, rough surfaces |
| **Separation-induced transition** | Laminar separation bubble → turbulent reattachment | Adverse pressure gradient at low Re | Low Re airfoils (Re < 500,000) |
| **Crossflow transition** | Crossflow instability in 3D BL | Sweep angle, pressure gradient | Swept wings, turbomachinery blades |

**Key parameters:**
- **Tu (turbulence intensity):** Free-stream disturbance level
  - Tu < 0.5%: Clean wind tunnel, natural transition
  - Tu = 1-3%: Typical atmospheric conditions
  - Tu > 5%: Turbomachinery, rough surfaces
- **Reθ (momentum thickness Reynolds number):** Critical threshold for transition
- **Pressure gradient:** Accelerating (stabilizing) vs. decelerating (destabilizing)
- **Surface roughness:** Trips transition earlier
- **Acoustic disturbances:** Can trigger early transition

**Transition prediction challenges:**
- Strongly dependent on free-stream turbulence intensity
- Sensitive to pressure gradient
- Surface roughness effects difficult to quantify
- Three-dimensional effects (crossflow) complicate prediction

### 3.3 The γ-Reθ Model

**Concept:** Two-equation model that tracks:
- **γ (gamma):** Intermittency (0 = laminar, 1 = turbulent)
- **Reθ:** Momentum thickness Reynolds number (controls transition onset)

**Model advantages:**
- Local (non-local calculations not required)
- Compatible with standard RANS models (k-ω SST)
- Calibrated for wide range of flows
- Relatively easy to implement

**Transport equations:**

**Intermittency (γ):**
$$\frac{\partial (\rho \gamma)}{\partial t} + \frac{\partial (\rho u_j \gamma)}{\partial x_j} = P_\gamma - E_\gamma + \frac{\partial}{\partial x_j}\left[(\nu + \frac{\nu_t}{\sigma_\gamma})\frac{\partial \gamma}{\partial x_j}\right]$$

Where:
-1$P_\gamma1= production term (triggers transition)
-1$E_\gamma1= destruction term (relaminarization)
-1$\sigma_\gamma1= model constant

**Transition momentum thickness Re (Reθ):**
$$\frac{\partial (\rho \tilde{R}e_\theta)}{\partial t} + \frac{\partial (\rho u_j \tilde{R}e_\theta)}{\partial x_j} = P_{\theta} + \frac{\partial}{\partial x_j}\left[\sigma_{\theta}(\nu + \nu_t)\frac{\partial \tilde{R}e_\theta}{\partial x_j}\right]$$

**Coupling with turbulence model:**
- Eddy viscosity is multiplied by intermittency:1$\nu_{t,eff} = \nu_t \cdot \gamma$
- In laminar regions (γ → 0): turbulence production is suppressed
- In turbulent regions (γ → 1): standard RANS behavior
- Production term in k-equation:1$P_k = \gamma \cdot P_{k,standard}$

**Transition onset criteria:**
$$Re_{\theta} > Re_{\theta,c}(Tu, \lambda_\theta)$$

Where:
-1$Re_{\theta,c}1= critical Reynolds number (function of Tu and pressure gradient)
-1$\lambda_\theta1= pressure gradient parameter

### 3.4 How to Set Up Transition Modeling in OpenFOAM

#### Step 1: Prerequisites

**Required turbulence model:**
- k-ω SST (most common and recommended)
- Can work with other models but SST is best calibrated

**Grid requirements:**
- y+ ≈ 1 (resolve viscous sublayer for accurate transition prediction)
- Similar resolution to wall-resolved LES in boundary layer
- Adequate streamwise resolution to capture transition region (Δx+ ≈ 50)
- At least 20-30 cells in boundary layer

**Computational cost:**
- 1.2-1.5× standard RANS (due to additional equations)
- Significantly cheaper than LES/DES for applicable flows

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

**Tu-based inlet values:**

| Tu | k (for U=10 m/s) | Reθ | Transition behavior |
|----|------------------|-----|---------------------|
| 0.1% | 0.00015 | 200 | Very late transition |
| 0.5% | 0.00375 | 400 | Late transition |
| 1% | 0.015 | 600 | Moderate transition |
| 2% | 0.06 | 1000 | Early transition |
| 5% | 0.375 | 2000 | Very early transition |

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

**Solution strategy:**
1. Start with first-order schemes and low maxCo (0.3-0.5)
2. Run until solution stabilizes
3. Gradually increase to second-order schemes
4. Increase maxCo to 0.5-0.8 for efficiency

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
- Lower drag than fully turbulent (Cd reduced by 30-50%)
- Possible laminar separation bubble near leading edge
- Higher lift than fully turbulent prediction

**Validation:**
- Compare Cf distribution to XFOIL or experimental data
- Check for sudden rise in Cf (indicates transition)
- Verify transition location matches expected range

### 3.6 Troubleshooting Transition Models

| Issue | Symptom | Solution |
|-------|---------|----------|
| No transition predicted | γ = 1 everywhere | Check inlet Tu, reduce Reθ, verify mesh resolution |
| Early transition | γ drops too quickly | Increase inlet Reθ, decrease Tu |
| Unstable solution | Oscillations in γ | Reduce maxCo, use upwind schemes initially |
| Wrong transition location | γ transitions at wrong x | Adjust Reθ based on experimental data |
| Solution diverges | Residuals increase | Use lower under-relaxation, start with first-order schemes |
| No effect on results | Same as fully turbulent | Verify transition is enabled, check γ field values |

**Verification checklist:**
- [ ] Transition model enabled in turbulenceProperties
- [ ] k-ω SST is the base RANS model
- [ ] Mesh has y+ ≈ 1 in boundary layer
- [ ] Inlet Tu and Reθ are physically reasonable
- [ ] Gamma field shows variation (0 < γ < 1 in transition region)
- [ ] Results differ from fully turbulent case

---

## 4. Summary and Key Takeaways

### 4.1 Model Selection Summary

**Quick decision guide:**

```
FLOW ASSESSMENT
│
├─ Need unsteady features?
│  ├─ No → RANS (fast, adequate for attached flows)
│  └─ Yes → Continue
│
├─ Reynolds number
│  ├─ Low (< 10⁶) → Wall-resolved LES (most accurate)
│  └─ High (> 10⁶) → Continue
│
├─ Wall-bounded?
│  ├─ Yes → DES (optimal cost/accuracy balance)
│  └─ No → LES (simplest, most accurate)
│
└─ Need transition prediction?
   ├─ Yes (Re < 10⁶, low Tu) → γ-Reθ model
   └─ No → Fully turbulent
```

**Computational cost hierarchy:**
```
RANS (1×) → Transition (1.2-1.5×) → DES (5-20×) → LES (100×) → DNS (10,000×)
```

**Critical success factors:**

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
| Using wrong SGS model | Poor results for specific flow | Use WALE for wall-bounded, dynamic for complex flows |
| Ignoring GIS in DES | Artificial separation, wrong physics | Use DDES/IDDES, verify RANS mode in attached BL |

### 4.3 Quick Reference Tables

**LES SGS Model Selection:**

| Application | Recommended Model | Cs/Settings | Reason |
|-------------|-------------------|-------------|---------|
| General flows | Smagorinsky | Cs = 0.1-0.15 | Simple, robust, good starting point |
| Wall-bounded | WALE | Default settings | Correct y³ scaling near walls |
| Complex flows | dynamicKEqn | Dynamic calculation | Adapts to local flow conditions |
| High accuracy | kEqn | Solve SGS k-equation | Most physical, higher cost |

**DES Variant Selection:**

| Application | Recommended Model | Notes |
|-------------|-------------------|-------|
| General purpose | SpalartAllmarasDDES | Prevents GIS, default choice |
| High Re, thin BL | SpalartAllmarasIDDES | Wall-modeled LES capability |
| Research (old cases) | SpalartAllmarasDES | May have GIS issues, avoid for new cases |

**Transition Model Applications:**

| Flow Type | Tu Range | Expected Transition | Reθ Range |
|-----------|----------|-------------------|-----------|
| Clean wind tunnel | 0.1-0.5% | Late (x/c > 0.5) | 100-300 |
| Atmosphere (low) | 1-2% | Moderate (x/c ≈ 0.3-0.5) | 400-800 |
| Turbomachinery | 3-10% | Early (x/c < 0.2) | 1000-2000 |
| Rough surfaces | > 5% | Very early | > 2000 |

**Mesh Requirements Summary:**

| Method | y+ | Δx+ | Δz+ | Aspect Ratio | Cost |
|--------|----|----|----|--------------|------|
| RANS | 1-100 | — | — | < 1000 | 1× |
| LES (wall-resolved) | ≈ 1 | 50-100 | 15-30 | 20-40 | 100× |
| DES (RANS zone) | 30-100 | — | — | < 100 | 5-20× |
| DES (LES zone) | — | ≈ 50 | ≈ 20 | ≈ 1-20 | — |
| Transition | ≈ 1 | ≈ 50 | — | < 50 | 1.2-1.5× |

### 4.4 Best Practices

**LES:**
1. Start with Smagorinsky model (Cs = 0.1-0.15)
2. Verify mesh resolution before running (check y+, Δ+)
3. Keep CFL ≤ 0.5 for temporal accuracy
4. Initialize from RANS if possible (faster startup)
5. Sample statistics only after flow development (≥ 10T)
6. Use second-order time schemes (backward) for accuracy

**DES:**
1. Always use DDES or IDDES (avoid original DES)
2. Initialize from RANS solution (mapFields)
3. Refine only in separated regions (NOT attached BL)
4. Monitor for GIS (compare to RANS solution)
5. Use y+ ≈ 30-100 in RANS regions
6. Verify LES mode in separated regions

**Transition:**
1. Use with k-ω SST only (best calibrated)
2. Resolve viscous sublayer (y+ ≈ 1)
3. Match inlet Tu to experimental conditions
4. Start with low CFL and first-order schemes
5. Verify γ shows variation (0 < γ < 1)
6. Compare to fully turbulent case to quantify effect

### 4.5 Key Takeaways

1. **RANS is sufficient** for attached, steady flows
   - Use as default for initial design iterations
   - Transition modeling adds 20-50% cost for low Re flows

2. **LES provides most accurate unsteady results**
   - Resolves large eddies directly
   - Requires y+ ≈ 1, Δ+ ≈ 50 (wall-resolved)
   - Prohibitively expensive at high Re (~100× RANS)

3. **DES balances accuracy and cost**
   - RANS in boundary layer, LES in separated regions
   - 5-20× RANS cost (much cheaper than wall-resolved LES)
   - Use DDES/IDDES to prevent Grid-Induced Separation

4. **Transition modeling is essential for low Re**
   - Significant drag reduction (30-50%)
   - Affects lift, separation, heat transfer
   - γ-Reθ model is practical for engineering flows

5. **Mesh quality is critical**
   - LES: y+ ≈ 1, isotropic cells, Δ+ ≈ 50
   - DES: Hybrid mesh, moderate refinement in RANS zones
   - Transition: y+ ≈ 1, adequate streamwise resolution

6. **Inlet conditions matter**
   - LES/DES: Realistic turbulence spectra
   - Transition: Correct Tu and Reθ
   - Always match experimental conditions when possible

7. **Computational cost scales with Reynolds number**
   - Wall-resolved LES cost ∝ Re^(2.4-2.8)
   - DES cost ∝ Re^1.5 (much better scaling)
   - Transition modeling adds minimal overhead

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
1. Generate appropriate mesh using blockMeshDict
2. Set up LES with Smagorinsky model in turbulenceProperties
3. Configure fvSchemes and fvSolution for LES
4. Run until statistical convergence (monitor reattachment length)
5. Compare reattachment length (x_r/h) to experiments (~6-7)
6. Extract mean velocity profiles at various x/h locations

**Validation:**
- Reattachment length: x_r/h ≈ 6-7
- Mean velocity profiles at x/h = 1, 3, 5, 7
- Reynolds stress profiles (-u'v', u'²)

**Files to create:**
- `constant/polyMesh/blockMeshDict` - Step geometry
- `constant/turbulenceProperties` - LES configuration
- `0/U`, `0/p`, `0/k`, `0/nuSgs` - Initial/boundary conditions
- `system/controlDict`, `system/fvSchemes`, `system/fvSolution` - Solver settings

**Expected outcome:** Accurate prediction of reattachment length and turbulent statistics.

### Exercise 2: DES of Flow Around a Cylinder

**Objective:** Compare DES vs. RANS for vortex shedding.

**Setup:**
- Re_D = 100,000 (subcritical)
- Mesh: hybrid RANS-LES
- Model: SpalartAllmarasDDES
- Compare to RANS (k-ω SST)

**Tasks:**
1. Create mesh with y+ ≈ 50 on cylinder surface (RANS zone)
2. Refine wake region for LES mode (isotropic cells)
3. Run both RANS and DES simulations
4. Compare:
   - Strouhal number (St ≈ 0.2 for this Re)
   - Lift and drag coefficients
   - Wake structure and vortex shedding
   - Computational cost

**Validation:**
- Strouhal number: St = fD/U∞ ≈ 0.2
- Drag coefficient: Cd ≈ 1.2
- Lift coefficient amplitude: Cl' ≈ 0.5
- DES should capture vortex shedding, RANS should not

**Key learning:** DES captures unsteady physics that RANS misses, at moderate computational cost.

### Exercise 3: Transition Modeling on Airfoil

**Objective:** Predict transition location at low Re.

**Setup:**
- Airfoil: NACA 0012
- Re_c = 200,000, α = 2°
- Mesh: C-mesh with y+ ≈ 1
- Model: k-ω SST + γ-Reθ
- Inlet Tu = 0.1% (clean wind tunnel)

**Tasks:**
1. Generate fine boundary layer mesh (≈ 30 cells in BL)
2. Set inlet conditions: Tu = 0.1%, Reθ = 200
3. Run with and without transition model
4. Compare:
   - Skin friction coefficient Cf distribution
   - Drag coefficient (Cd)
   - Transition location vs. XFOIL predictions
   - Lift coefficient (Cl)

**Validation:**
- Compare to XFOIL predictions
- Check transition location (x/c ≈ 0.3-0.5)
- Verify drag reduction (≈ 30-50% lower than fully turbulent)
- Examine Cf for sudden rise (indicates transition)

**Expected outcome:** Transition model predicts delayed transition and lower drag compared to fully turbulent.

### Exercise 4: Comparative Study

**Objective:** Compare all advanced methods on same geometry.

**Geometry:** 2D hill at Re_h = 10,000

**Methods to test:**
1. RANS (k-ω SST)
2. Transition model (γ-Reθ)
3. DES (SpalartAllmarasDDES)
4. LES (Smagorinsky)

**Tasks:**
1. Set up each method separately
2. Run all simulations to convergence
3. Compare:
   - Separation bubble size
   - Reattachment length
   - Velocity profiles
   - Computational cost (CPU hours)
   - Wall clock time

**Analysis:**
- Create table comparing accuracy vs. cost
- Identify which method is optimal for this flow
- Discuss trade-offs and recommendations

**Expected findings:**
- RANS: Fast but may miss separation details
- Transition: Similar to RANS (fully turbulent at this Re)
- DES: Good accuracy, moderate cost
- LES: Best accuracy, highest cost

---

## Concept Check Questions

<details>
<summary><b>1. What is the fundamental difference between LES and RANS?</b></summary>

**Answer:**
- **RANS:** Time-averages all turbulence fluctuations, models everything with eddy viscosity
- **LES:** Spatially filters equations, resolves large eddies directly, models only small subgrid scales
- **Result:** LES captures unsteady, large-scale turbulent structures that RANS cannot
- **Cost:** LES is ~100× more expensive than RANS for wall-resolved simulations
</details>

<details>
<summary><b>2. Why is DES more efficient than wall-resolved LES for high Re flows?</b></summary>

**Answer:**
- **Wall-resolved LES:** Requires y+ ≈ 1 everywhere → extremely fine mesh near walls → ~100× RANS cost
- **DES:** Uses RANS in boundary layer (y+ ≈ 30-100) + LES only in separated regions → 5-20× RANS cost
- **Savings:** Near-wall resolution dominates cell count for high Re; DES avoids this by using RANS there
- **Trade-off:** Slightly less accurate than pure LES but much more affordable
</details>

<details>
<summary><b>3. What is Grid-Induced Separation (GIS) and how does DDES prevent it?</b></summary>

**Answer:**
- **GIS:** Occurs when DES switches to LES mode too early in attached boundary layers due to local mesh refinement
- **Consequence:** Artificial separation because RANS-modeled stresses are depleted
- **DDES solution:** Adds "delay function" (fd) that keeps model in RANS mode in thick boundary layers, even if mesh is locally refined
- **Key:** DDES shields the RANS mode from premature switching using eddy viscosity and wall distance
</details>

<details>
<summary><b>4. When should you use transition modeling instead of fully turbulent RANS?</b></summary>

**Answer:**
Use transition modeling when:
- Reynolds number is low to moderate (Re < 10⁶ for external flows)
- Free-stream turbulence intensity is low (< 3%)
- Laminar regions significantly affect performance (drag, lift, heat transfer)
- Applications: Low Re airfoils, turbomachinery, wind turbines, some heat transfer cases
- **Skip transition** for high Re flows (> 10⁷) or high turbulence environments (> 5% Tu)
</details>

<details>
<summary><b>5. What are the additional fields required for γ-Reθ transition modeling?</b></summary>

**Answer:**
Three additional fields beyond standard k-ω SST:
1. **gamma (γ):** Intermittency (0 = laminar, 1 = turbulent)
2. **ReTheta:** Transition momentum thickness Reynolds number (controls onset)
3. **thetat:** Critical Reθ at transition onset (boundary condition)

These fields are transported and coupled to the turbulence model via intermittency. The eddy viscosity is modified as νt,eff = νt · γ.
</details>

<details>
<summary><b>6. What are the mesh requirements for wall-resolved LES?</b></summary>

**Answer:**
- **y+ ≈ 1** (resolve viscous sublayer)
- **Streamwise spacing:** Δx+ ≈ 50-100 in wall units
- **Spanwise spacing:** Δz+ ≈ 15-30 in wall units
- **Cell aspect ratio:** ≈ 1 (isotropic) in core, up to 20-40 near walls
- **CFL number:** 0.3-0.5 for temporal accuracy

These requirements make wall-resolved LES extremely expensive at high Re. The cell count scales as N ∝ Re^2.4, which is why DES is preferred for high Re flows.
</details>

<details>
<summary><b>7. How do you choose between Smagorinsky, WALE, and dynamic SGS models for LES?</b></summary>

**Answer:**
- **Smagorinsky:** Default choice, simple, robust. Good for general flows. Cs = 0.1-0.2
- **WALE:** Better near-wall behavior (correct y³ scaling). Use for wall-bounded flows. No Cs needed
- **dynamicKEqn:** Adapts Cs to local flow conditions. Good for complex flows with varying turbulence. Can backscatter energy
- **Choice:** Start with Smagorinsky; switch to WALE for wall-bounded cases or dynamic for complex flows with varying turbulence characteristics
</details>

<details>
<summary><b>8. What are the key differences between DES, DDES, and IDDES?</b></summary>

**Answer:**
- **DES (original):** Simple min(l_RANS, C_DES·Δ) switching. Prone to Grid-Induced Separation (GIS)
- **DDES (Delayed DES):** Adds shielding function fd to prevent premature switching in attached boundary layers. Prevents GIS
- **IDDES (Improved DDES):** Combines DDES with wall-modeled LES capability. Best near-wall treatment for high Re flows with thin boundary layers
- **Recommendation:** Use DDES for most cases, IDDES for high Re with thin BL, avoid original DES
</details>

<details>
<summary><b>9. How does turbulence intensity (Tu) affect transition prediction?</b></summary>

**Answer:**
- **Low Tu (< 0.5%):** Late transition, typically x/c > 0.5 for airfoils. Natural transition via T-S waves
- **Moderate Tu (1-3%):** Moderate transition, x/c ≈ 0.3-0.5. Typical atmospheric conditions
- **High Tu (> 5%):** Early transition, x/c < 0.2. Bypass transition, common in turbomachinery
- **Effect on Reθ:** Higher Tu → lower critical Reθ → earlier transition
- **Modeling:** γ-Reθ model uses Tu to calculate critical Reθ for transition onset
</details>

<details>
<summary><b>10. What are the signs that your LES mesh is too coarse?</b></summary>

**Answer:**
- Excessive energy dissipation (turbulent kinetic energy decays too fast)
- SGS eddy viscosity is too high (νSgs >> ν)
- Poor agreement with experimental data (especially in spectral content)
- Missing high-frequency fluctuations in velocity probes
- Inaccurate prediction of separation or reattachment
- **Verification:** Check Δ+ = Δ·uτ/ν ≈ 50-100 in critical regions
- **Solution:** Refine mesh or switch to DES if refinement is impractical
</details>

---

## Related Documents

### Within This Module
- **Prerequisites:**
  - [Turbulence Fundamentals](01_Turbulence_Fundamentals.md) - RANS basics, turbulence scales
  - [RANS Models](02_RANS_Models.md) - k-ε, k-ω, Spalart-Allmaras models
  - [Wall Treatment](03_Wall_Treatment.md) - y+ concepts, wall functions

### Complementary Topics
- **High-Performance Computing:** [01_High_Performance_Computing.md](01_High_Performance_Computing.md) - Parallel scaling for LES/DES
- **Numerical Methods:** [03_Numerical_Methods.md](03_Numerical_Methods.md) - Discretization schemes (relevant for LES stability)
- **Mesh Quality:** [Module 02, Section 05](../../MODULE_02_MESHING_AND_CASE_SETUP/CONTENT/05_MESH_QUALITY_AND_MANIPULATION/01_Mesh_Quality_Criteria.md) - Mesh requirements for advanced turbulence

### Further Reading
- Pope, S. B. (2000). *Turbulent Flows*. Cambridge University Press. (Chapters 10-13 for LES)
- Sagaut, P. (2006). *Large Eddy Simulation for Incompressible Flows*. Springer.
- Langtry, R. B., & Menter, F. R. (2009). "Correlation-based transition modeling for unstructured parallelized computational fluid dynamics codes." *AIAA Journal*, 47(12).
- Spalart, P. R., et al. (2006). "A new version of detached-eddy simulation, resistant to ambiguous grid densities." *Theoretical and Computational Fluid Dynamics*, 20(3).

---

**Last Updated:** 2025-12-31