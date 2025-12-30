# LES Fundamentals

Large Eddy Simulation สำหรับการจำลองความปั่นป่วน

---

## Learning Objectives

By the end of this module, you will be able to:

- **What:** Define spatial filtering concepts and SGS stress tensor formulations
- **Why:** Understand when LES is preferable to RANS based on flow physics and computational resources
- **How:** Configure and run LES simulations in OpenFOAM with appropriate mesh, boundary conditions, and numerical schemes

---

## Skills Progression Tracker

| Skill | Novice | Competent | Proficient |
|-------|--------|-----------|------------|
| SGS Model Selection | Know basic Smagorinsky | Choose models for flow type | Implement dynamic models |
| LES Mesh Design | Understand y+ requirements | Design wall-resolved meshes | Create hybrid RANS-LES |
| Boundary Conditions | Set basic inlet/outlet | Use turbulent inlet methods | Implement recycling methods |
| Quality Assessment | Check CFL and basic metrics | Analyze resolution indices | Perform spectral analysis |

---

## Overview

**LES** แก้สมการสำหรับ large eddies โดยตรง และใช้ SGS model สำหรับ small eddies:

| Approach | Resolved | Modeled | Cost | When to Use |
|----------|----------|---------|------|-------------|
| DNS | All scales | None | Highest | Fundamental research, simple geometries |
| **LES** | Large eddies | Small eddies (SGS) | High | Unsteady flows, vortex shedding, acoustics |
| RANS | None | All scales | Lowest | Steady flows, industrial design iterations |

**Why LES?** Captures transient turbulent structures that RANS averages out, essential for:
- Flow-induced vibration and noise prediction
- Unsteady wake dynamics and vortex shedding
- Mixing and combustion applications

---

## 1. Spatial Filtering

### Filter Width (WHAT)

**Definition:** Characteristic length scale separating resolved from subgrid scales

$$\Delta = \sqrt[3]{V_{cell}}$$

**Why:** Determines which eddies are explicitly resolved vs. modeled

**How - OpenFOAM:**

```cpp
// constant/turbulenceProperties
LES
{
    delta   cubeRootVol;  // Most common: Δ = V^(1/3)
    
    // Alternative options:
    // delta   maxDeltaxyz;     // Δ = max(Δx, Δy, Δz)
    // delta   smoothDelta;     // Spatially smoothed
    // delta   vanDriestDelta;  // Near-wall damping
}
```

### Filtered Equations (WHAT)

**Filtered Navier-Stokes Equation:**

$$\frac{\partial \bar{u}_i}{\partial t} + \frac{\partial}{\partial x_j}(\bar{u}_i \bar{u}_j) = -\frac{1}{\rho}\frac{\partial \bar{p}}{\partial x_i} + \nu \frac{\partial^2 \bar{u}_i}{\partial x_j^2} - \frac{\partial \tau_{ij}^{SGS}}{\partial x_j}$$

**SGS Stress Tensor:**
$$\tau_{ij}^{SGS} = \overline{u_i u_j} - \bar{u}_i \bar{u}_j$$

**Why:** The SGS stress represents the effect of unresolved small-scale motions on large scales, requiring closure modeling

---

## 2. SGS Models

### Model Comparison (WHY/HOW)

| Model | Formula | Recommended For | Pros | Cons |
|-------|---------|-----------------|------|------|
| **Smagorinsky** | $\nu_{SGS} = (C_s \Delta)^2 |\bar{S}|$ | Simple free shear flows | Robust, well-tested | Over-dissipative near walls |
| **WALE** | Strain/vorticity combination | Wall-bounded flows | Correct y³ near-wall behavior | Less validated |
| **Dynamic** | Computes $C_s$ locally | Complex flows with separation | No tuning needed | Can be unstable |
| **oneEqEddy** | Solves k-equation | General industrial cases | Better for non-equilibrium | Additional PDE solve |

### Smagorinsky Model (HOW)

**What:** Eddy viscosity proportional to strain rate magnitude and filter width squared

```cpp
// constant/turbulenceProperties
simulationType  LES;

LES
{
    LESModel        Smagorinsky;
    turbulence      on;
    delta           cubeRootVol;
    
    SmagorinskyCoeffs
    {
        Cs      0.1;    // Typical: 0.1-0.2 (isotropic turbulence)
        // Cs = 0.1-0.12 for channel flows
        // Cs = 0.15-0.2 for shear layers
    }
}
```

**Why:** Simple and stable, but requires Cs tuning and produces non-zero ν_SGS at walls

### WALE Model (Wall-Adaptive Local Eddy) (HOW)

**What:** Automatically provides ν_SGS → 0 near walls based on velocity gradient tensor

```cpp
LES
{
    LESModel        WALE;
    delta           cubeRootVol;
    
    WALECoeffs
    {
        Cw      0.325;  // Default value
    }
}
```

**Why:** Correct y³ wall behavior without explicit damping functions—ideal for wall-resolved LES

### Dynamic Smagorinsky (HOW)

**What:** Computes Cs dynamically from resolved scales using test filtering

```cpp
LES
{
    LESModel        dynamicSmagorinsky;
    delta           cubeRootVol;
    // No Cs input—computed from energy cascade
    
    dynamicSmagorinskyCoeffs
    {
        filter        simple;  // Test filter type
    }
}
```

**Why:** Adapts to local flow conditions—useful for flows with separation and reattachment

### One-Equation Eddy Model (HOW)

```cpp
LES
{
    LESModel        oneEqEddy;
    delta           cubeRootVol;
    
    oneEqEddyCoeffs
    {
        ck              0.094;
        ce              1.05;  // Energy dissipation coefficient
    }
}
```

**Why:** Solves transport equation for subgrid kinetic energy—better for flows with non-equilibrium turbulence

---

## 3. Boundary Conditions

### Inlet (HOW)

**Turbulent Inlet with Fluctuations:**

```cpp
// 0/U - Turbulent inlet with random fluctuations
inlet
{
    type            turbulentInlet;
    mean            (10 0 0);           // Mean velocity
    fluctuation     (0.5 0.5 0.5);     // RMS fluctuation magnitude
    referenceField  uniform (10 0 0);
}

// Alternative: Synthetic Eddy Method (more realistic)
inlet
{
    type            turbulentDFSEMInlet;  // Discrete Random Flux SEM
    delta           0.01;                 // Eddy length scale
    nEddy           100;                  // Number of eddies
    
    // Optional: specify Reynolds stress tensor
    R               uniform (0.5 0 0 0.5 0 0.3);
}
```

**Why:** LES requires realistic turbulent fluctuations at inlet—laminar or uniform profiles take too long to develop turbulence

### Outlet (HOW)

```cpp
outlet
{
    type            zeroGradient;  // Standard for most cases
}

// Alternative: For backflow prevention
outlet
{
    type            inletOutlet;  // zeroGradient for outflow, fixedValue for backflow
    inletValue      uniform (0 0 0);
    value           uniform (10 0 0);
}
```

### Wall Treatment (HOW)

**Wall-Resolved LES (y+ ≈ 1):**

```cpp
// 0/U - No-slip condition
walls
{
    type            noSlip;
}

// 0/nut - Low Reynolds number treatment
walls
{
    type            nutLowReWallFunction;
    value           uniform 0;  // ν_SGS → 0 at wall
}
```

**Wall-Modeled LES (y+ = 50-200):**

```cpp
// 0/U - Standard wall function
walls
{
    type            noSlip;
}

// 0/nut - Equilibrium wall function
walls
{
    type            nutkWallFunction;
    value           uniform 0;
}
```

---

## 4. Mesh Requirements

### Resolution Guidelines (WHAT/HOW)

**Dimensionless Grid Spacing:**

| Direction | Requirement | Physical Meaning |
|-----------|-------------|------------------|
| Streamwise (Δx⁺) | 40-60 | Capture large eddies in flow direction |
| Spanwise (Δz⁺) | 15-20 | Resolve streak structures |
| Wall-normal (Δy⁺) | ≈ 1 (resolved) | Resolve viscous sublayer |

**Why:** LES requires sufficient resolution to capture energy-containing eddies—coarse mesh = excessive SGS dissipation

### y+ Target (WHY/HOW)

| LES Type | y+ | Cells in BL | Mesh Size | When to Use |
|----------|-------|-------------|-----------|-------------|
| Wall-resolved | ≈ 1 | 10-15 | Very large | Accurate wall physics, acoustics |
| Wall-modeled | 50-200 | 5-8 | Moderate | High Re flows, limited resources |

**Mesh Example (Channel Flow, Reτ = 1000):**
```python
# Approximate cell counts for wall-resolved LES
# Domain: 4π × 2 × 2π (streamwise × wall-normal × spanwise)
nx = 200   # Δx⁺ ≈ 60
ny = 150   # Stretched, Δy⁺_wall ≈ 1
nz = 100   # Δz⁺ ≈ 20
# Total: ~3 million cells
```

### CFL Requirement (WHAT/HOW)

**Courant-Friedrichs-Lewy Condition:**

$$CFL = \frac{|u| \Delta t}{\Delta x} < 0.5$$

**Why:** LES resolves transient eddies moving through mesh—high CFL introduces temporal diffusion that smears structures

**Implementation:**

```cpp
// system/controlDict
application     pimpleFoam;

startFrom       startTime;
startTime       0;

stopAt          endTime;
endTime         10;  // Flow-through times

adjustTimeStep  yes;
maxCo           0.5;     // Maximum CFL

maxDeltaT       0.001;   // Upper limit
```

**Post-process CFL:**
```bash
# Check actual CFL during simulation
foamListTimes
postProcess -func CourantNo -latestTime

# Visualize
paraFoam
```

---

## 5. Solver Settings

### fvSchemes (HOW)

**Key Principle:** Use low-dissipation schemes to preserve turbulent structures

```cpp
// system/fvSchemes
ddtSchemes
{
    default     backward;   // Second-order implicit
    // Alternative: Euler (first-order, for initialization only)
}

gradSchemes
{
    default     Gauss linear;
}

divSchemes
{
    default     none;
    
    // Convection schemes for LES
    div(phi,U)  Gauss linear;                    // Central differencing
    // Alternatives:
    // div(phi,U)  Gauss linearUpwind grad(U);   // For stability
    // div(phi,U)  Gauss LUSGS;                  // Low-dissipation
    
    div(phi,k)  Gauss limitedLinear 1;
    div(phi,B)  Gauss limitedLinear 1;
}

laplacianSchemes
{
    default     Gauss linear corrected;  // Non-orthogonal correction
}

interpolationSchemes
{
    default     linear;
}

snGradSchemes
{
    default     corrected;
}
```

**Why:** Central differencing minimizes numerical dissipation—critical for maintaining energy cascade

### fvSolution (HOW)

```cpp
// system/fvSolution
solvers
{
    p
    {
        solver          GAMG;
        tolerance       1e-06;
        relTol          0.01;
        smoother        GaussSeidel;
        nPreSweeps      0;
        nPostSweeps     2;
        cacheAgglomeration on;
        agglomerator    faceAreaPair;
        mergeLevels     1;
    }
    
    pFinal
    {
        $p;
        relTol          0;
    }
    
    U
    {
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-05;
        relTol          0.1;
    }
    
    k
    {
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-05;
        relTol          0.1;
    }
}

PIMPLE
{
    nOuterCorrectors    1;      // LES typically uses 1
    nCorrectors         2;      // Pressure equation iterations
    nNonOrthogonalCorrectors 1;
    
    // Optional: momentum predictor
    momentumPredictor  yes;
}
```

---

## 6. Quality Metrics

### SGS Resolution Index (WHAT)

**Definition:** Ratio of modeled to total viscosity

$$\eta = \frac{\nu_{SGS}}{\nu + \nu_{SGS}} = \frac{\nu_{SGS}}{\nu_{eff}}$$

**Interpretation:**

| η Value | Quality Assessment |
|---------|-------------------|
| < 0.2 | Excellent: >80% of turbulence resolved |
| 0.2-0.5 | Good: Sufficiently resolved large scales |
| 0.5-0.8 | Marginal: Consider mesh refinement |
| > 0.8 | Poor: RANS may be more appropriate |

**How - Post-process:**

```cpp
// system/controlDict - Add runtime calculation
functions
{
    sgsResolution
    {
        type            coded;
        functionObjectLibs ("libutilityFunctionObjects.so");
        writeFields     true;
        
        code
        #{
            const volScalarField& nut = mesh().lookupObject<volScalarField>("nut");
            const volScalarField& nu = mesh().lookupObject<volScalarField>("nu");
            volScalarField eta = nut/(nu + nut);
            eta.write();
        #};
    }
}
```

### Energy Spectrum Check (WHAT)

**Theory:** Inertial range should follow Kolmogorov -5/3 law

$$E(\kappa) \propto \kappa^{-5/3}$$

**Why:** Validates that LES captures correct energy cascade physics

**How - Generate Spectrum:**

```bash
# Post-process: Sample point history
postProcess -func probes -latestTime

# Extract time series
# Write Python/MATLAB script for FFT

# Python example:
import numpy as np
from scipy import signal

# Load u-component time history
u = np.loadtxt('postProcessing/probes/0/U')

# Compute PSD
freqs, psd = signal.welch(u, fs=1/dt, nperseg=1024)

# Plot log-log
plt.loglog(freqs, psd)
plt.loglog(freqs, C*freqs**(-5/3), '--')  # Compare to -5/3
```

**Quality Indicators:**
- Clear -5/3 slope in inertial range → Good resolution
- Premature roll-off → Insufficient resolution
- No inertial range → Mesh too coarse or RANS regime

---

## 7. Workflow

### Step-by-Step Process (HOW)

```bash
# 1. Generate LES-quality mesh
blockMesh
checkMesh  # Verify non-orthogonality < 70°

# Optional: Calculate required mesh spacing
# python3 <<< "print(f'y+ < 1 requires y_wall < {1/1000}')"

# 2. Configure LES model
# Edit constant/turbulenceProperties
# Set appropriate delta and LESModel

# 3. Set low-dissipation numerical schemes
# Edit system/fvSchemes: Use central differencing

# 4. Initialize turbulent field (optional)
# Use RANS solution as initial condition
# Or apply random perturbations
funkySetFields -field U -expression "U + 0.1*randNormal()"

# 5. Run LES simulation
pimpleFoam > log.pimpleFoam &

# 6. Monitor key metrics
tail -f log.pimpleFoam | grep "Courant"
postProcess -func CourantNo

# 7. Post-process statistics
# Time averaging after flow development
postProcess -func fieldAverage

# Check SGS resolution
# (See coded functionObject in Section 6)

# 8. Visualization
paraFoam -builtin
```

### Typical Runtime Behavior

**Flow Development:**
- **t = 0-2T:** Initial transient (discard from statistics)
- **t = 2-10T:** Statistical development
- **t > 10T:** Collect statistics

**where T = L/U_char is flow-through time**

---

## 8. Practical Tips

### Initialization Strategy

**Option 1: RANS Initialization**
```bash
# Run RANS first
simpleFoam > log.simpleFoam

# Switch to LES (turbulenceProperties)
pimpleFoam > log.pimpleFoam
```

**Option 2: Synthetic Turbulence**
```bash
# Add random fluctuations to mean flow
funkySetFields -field U -expression "U + 0.1*randNormal()"
```

### Common Issues and Solutions

| Issue | Symptom | Fix |
|-------|---------|-----|
| Divergence | Residuals spike, CFL → ∞ | Reduce maxCo, check mesh quality |
| Laminar solution | No fluctuations | Check inlet BC, add perturbations |
| No turbulence production | k_SGS → 0 | Verify Re is sufficiently high |
| Excessive dissipation | Energy spectrum decays too fast | Use central differencing, refine mesh |

---

## Concept Check

<details>
<summary><b>1. LES ต่างจาก RANS อย่างไร?</b></summary>

**What:** 
- **LES:** แก้สมการสำหรับ large eddies โดยตรง ใช้ model เฉพาะ small eddies (SGS) → จับ transient structures ได้ดี
- **RANS:** เฉลี่ยทุก scales → เห็นเฉพาะ mean flow

**Why:** เลือก LES เมื่อต้องการ unsteady phenomena (vortex shedding, acoustics, mixing) เลือก RANS เมื่อต้องการ steady design iterations

**How:** LES ต้องการ mesh ละเอียด 10-100x กว่า RANS และ computational cost สูงกว่ามาก
</details>

<details>
<summary><b>2. WALE ดีกว่า Smagorinsky ตรงไหน?</b></summary>

**What:** WALE ให้ ν_SGS ∝ y³ ใกล้ผนัง Smagorinsky ให้ ν_SGS ≠ 0

**Why:** Smagorinsky ต้องใช้ damping functions ที่ซับซ้อน WALE ทำอัตโนมัติจาก velocity gradient tensor

**How:** เลือก WALE สำหรับ wall-bounded flows Smagorinsky สำหรับ free shear flows
</details>

<details>
<summary><b>3. ทำไม LES ต้องการ CFL < 1?</b></summary>

**What:** CFL = |u|Δt/Δx measures temporal resolution relative to mesh

**Why:** LES ต้องการ temporal accuracy สูงเพื่อจับ transient structures ที่เคลื่อนที่ผ่าน mesh — CFL สูงเกินไปจะทำให้ eddies ถูก temporal diffusion smeared หรือหายไป

**How:** ใช้ `adjustTimeStep yes; maxCo 0.5;` ใน controlDict
</details>

<details>
<summary><b>4. SGS resolution index η บอกอะไร?</b></summary>

**What:** η = ν_SGS/(ν + ν_SGS) measures fraction of modeled turbulence

**Why:** η < 0.2 หมายถึง resolved > 80% → LES quality good

**How:** Post-process ด้วย coded functionObject หรือ Python script
</details>

---

## Key Takeaways

✅ **Filtering Concept:** Spatial filtering separates resolved scales (directly computed) from subgrid scales (modeled via SGS)

✅ **Model Selection:** Smagorinsky for simplicity, WALE for wall-bounded flows, Dynamic for complex flows with separation

✅ **Mesh Resolution:** Wall-resolved LES requires y+ ≈ 1 with Δx⁺ ≈ 50, Δz⁺ ≈ 15—typically 10-100x more cells than RANS

✅ **Numerical Schemes:** Use low-dissipation schemes (central differencing) to preserve turbulent energy cascade

✅ **Quality Assessment:** Monitor SGS resolution index (η < 0.2) and energy spectrum (-5/3 slope) to validate LES quality

✅ **Computational Cost:** LES is 10-100x more expensive than RANS but provides unique unsteady flow physics

---

## Related Documents

- **บทก่อนหน้า:** [03_Wall_Treatment.md](03_Wall_Treatment.md) - Wall boundary conditions for LES vs RANS
- **บทถัดไป:** [06_Des_Simulation.md](06_Des_Simulation.md) - Detached Eddy Simulation (hybrid RANS-LES)
- **Solver Reference:** [01_Incompressible_Flow_Solvers.md](../../01_INCOMPRESSIBLE_FLOW_SOLVERS/01_Introduction.md) - pimpleFoam and solver details
- **Mesh Design:** [01_Introduction_to_Meshing.md](../../02_MESHING_AND_CASE_SETUP/01_MESHING_FUNDAMENTALS/01_Introduction_to_Meshing.md) - Mesh quality guidelines

---

## References

1. Sagaut, P. (2006). *Large Eddy Simulation for Incompressible Flows*. Springer.
2. Pope, S.B. (2000). *Turbulent Flows*. Cambridge University Press.
3. OpenFOAM User Guide: LES Models
4. GEKO (Generalized k-ω) Documentation