# Practical Usage of Non-Newtonian Fluids in OpenFOAM

---

## Learning Objectives

By the end of this section, you should be able to:

1. **Select the appropriate solver** for different non-Newtonian flow applications
2. **Configure transport properties** for various viscosity models in OpenFOAM
3. **Set up and run** a complete non-Newtonian simulation from start to finish
4. **Apply mesh strategies** to accurately capture shear-rate-dependent behavior
5. **Diagnose and resolve** convergence issues specific to non-Newtonian simulations
6. **Post-process and visualize** variable viscosity fields effectively
7. **Estimate model parameters** from experimental rheological data

---

## 1. Overview

This section provides **practical, hands-on guidance** for setting up and running non-Newtonian fluid simulations in OpenFOAM. While theoretical fundamentals were covered in [01_Non_Newtonian_Fundamentals.md](01_Non_Newtonian_Fundamentals.md) and viscosity models in [02_Viscosity_Models.md](02_Viscosity_Models.md), this document focuses on **implementation workflow, solver selection, parameter estimation, and troubleshooting**.

The key challenges in non-Newtonian CFD are:

- **Strong nonlinearity** due to viscosity dependence on shear rate
- **Numerical instability** when viscosity varies over orders of magnitude
- **Parameter uncertainty** - material properties often come from limited experimental data
- **Mesh resolution** requirements near walls where shear rates are highest

---

## 2. Solver Selection Guide

### 2.1 Standard Solvers with Non-Newtonian Support

OpenFOAM's incompressible solvers support non-Newtonian models through the `transportModel` specification:

| Solver | Flow Type | Temporal | Recommended Use |
|--------|-----------|----------|-----------------|
| **simpleFoam** | Steady-state, incompressible | Steady | **Fully developed flows**; initial guess; quick screening |
| **pimpleFoam** | Transient, incompressible | Transient | **General-purpose transient**; startup flows; time-dependent BCs |
| **pisoFoam** | Transient, incompressible | Transient | Time-accurate transient; smaller time steps |
| **nonNewtonianIcoFoam** | Transient, laminar | Transient | **Laminar non-Newtonian only**; educational purposes |

### 2.2 Specialized Rheology Solvers

| Solver | Purpose | When to Use |
|--------|---------|-------------|
| **viscoelasticFluidFoam** | Viscoelastic fluids (e.g., polymer melts) | Elastic effects important (Weissenberg number > 0.5) |
| **rheoFoam** | Advanced rheological models | Complex constitutive equations; Giesekus, Oldroyd-B, etc. |
| **interFoam** | Multiphase with non-Newtonian | Free surface flows (paint coating, food processing) |

### 2.3 Solver Decision Flowchart

```
Start → Is flow steady-state? 
         ├─ Yes → simpleFoam (try first)
         │        ↓ Converged?
         │        ├─ Yes → Done
         │        └─ No → Try pimpleFoam with pseudo-transient
         └─ No → Is viscoelastic?
                  ├─ Yes → viscoelasticFluidFoam or rheoFoam
                  └─ No → pimpleFoam (standard)
```

---

## 3. Transport Properties Configuration

### 3.1 Setting the Transport Model

The **central configuration** for all non-Newtonian simulations is in `constant/transportProperties`:

```cpp
// constant/transportProperties

transportModel  CrossPowerLaw;  // Select model: PowerLaw, CrossPowerLaw, 
                                // CarreauYasuda, HerschelBulkley, etc.

nu              [0 2 -1 0 0 0 0]  0.001;  // Reference viscosity (initial value)

// Model-specific coefficients
CrossPowerLawCoeffs
{
    nu0     [0 2 -1 0 0 0 0]  0.01;    // Zero-shear viscosity (m²/s)
    nuInf   [0 2 -1 0 0 0 0]  0.0001;  // Infinite-shear viscosity (m²/s)
    m       [0 0 1 0 0 0 0]  0.1;      // Time constant (s)
    n       [0 0 0 0 0 0 0]  0.5;      // Power-law index (dimensionless)
}
```

**Key Models:**

| Model | Parameters | Typical Application |
|-------|------------|---------------------|
| **PowerLaw** | `K` (consistency), `n` (index) | Simple shear-thinning/thickening |
| **CrossPowerLaw** | `nu0`, `nuInf`, `m`, `n` | Polymer solutions; bounded viscosity |
| **CarreauYasuda** | `nu0`, `nuInf`, `lambda`, `n`, `a` | Blood, Carreau fluids; flexible |
| **HerschelBulkley** | `tau0`, `K`, `n` | Yield stress fluids; cement, food |
| **BirdCarreau** | `nu0`, `nuInf`, `lambda`, `n` | Carreau model alternative |

**Cross-reference:** See [02_Viscosity_Models.md](02_Viscosity_Models.md) for complete model equations and parameter ranges.

### 3.2 Complete Example: Power Law Fluid

```cpp
transportModel  powerLaw;

powerLawCoeffs
{
    nuMax   [0 2 -1 0 0 0 0]  100.0;  // Limit viscosity (stability)
    nuMin   [0 2 -1 0 0 0 0]  1e-6;   // Minimum viscosity
    k       [0 2 -1 0 0 0 0]  0.05;   // Consistency index (Pa·sⁿ)
    n       [0 0 0 0 0 0 0]  0.6;     // Power-law index
}
```

**Interpretation:**
- **n < 1**: Shear-thinning (pseudoplastic) — viscosity decreases with shear rate
- **n = 1**: Newtonian (constant viscosity)
- **n > 1**: Shear-thickening (dilatant) — viscosity increases with shear rate

### 3.3 Complete Example: Herschel-Bulkley (Yield Stress)

```cpp
transportModel  HerschelBulkley;

HerschelBulkleyCoeffs
{
    tau0    [0 -2 1 0 0 0 0]  5.0;    // Yield stress (Pa)
    k       [0 2 -1 0 0 0 0]  0.1;    // Consistency (Pa·sⁿ)
    n       [0 0 0 0 0 0 0]  0.5;     // Flow index
    nu0     [0 2 -1 0 0 0 0]  1000;   // Viscosity for τ < τ0 (Pa·s)
}
```

**Usage note:** Yield stress fluids require careful initialization — start with high viscosity where stress < yield stress.

---

## 4. Common Materials and Their Parameters

### 4.1 Biological Fluids

| Material | Model | Key Parameters | Reference |
|----------|-------|----------------|-----------|
| **Blood** | Carreau | nu0=0.056 m²/s, n=0.35, λ=3.3 s | [2] |
| **Blood (simplified)** | Power Law | n=0.35-0.5 | Arterial flows |
| **Mucus** | Herschel-Bulkley | τ0=0.2-2 Pa, n=0.3-0.7 | Respiratory |
| **Synovial fluid** | Carreau-Yasuda | n≈0.2-0.4 | Joint lubrication |

### 4.2 Polymer Solutions and Melts

| Material | Model | Key Parameters | Application |
|----------|-------|----------------|-------------|
| **Xanthan gum (0.5%)** | Power Law | n=0.4-0.6, K=0.5-2 Pa·sⁿ | Food thickener |
| **Polyethylene melt** | Cross | nu0≈1000-10000 Pa·s, n=0.3-0.7 | Extrusion |
| **PAA solutions** | Carreau | λ=0.1-10 s, n=0.2-0.8 | Drag reduction |

### 4.3 Industrial Materials

| Material | Model | Key Parameters | Application |
|----------|-------|----------------|-------------|
| **Paint** | Herschel-Bulkley | τ0=5-20 Pa, n=0.4-0.8 | Coating processes |
| **Cement paste** | Bingham | τ0=10-100 Pa, μ=0.01-0.1 Pa·s | Concrete pumping |
| **Drilling mud** | Herschel-Bulkley | τ0=5-50 Pa, n=0.5-0.8 | Oil & gas |
| **Chocolate** | Casson/Herschel-Bulkley | τ0≈10-50 Pa, n≈0.5 | Food processing |
| **Toothpaste** | Bingham | τ0≈50-200 Pa | Consumer products |

> ⚠️ **Parameter uncertainty:** Literature values vary widely. Always verify with experimental data if possible.

---

## 5. Parameter Estimation from Experimental Data

### 5.1 Rheometer Data Fitting

**Step 1: Obtain viscosity vs. shear rate data**

Use a rotational rheometer to measure η(γ̇) over a wide range (γ̇ = 0.01 to 1000 s⁻¹).

**Step 2: Plot and identify flow regime**

- **Power-law region**: log η vs log γ̇ is linear
- **Zero-shear plateau**: η constant at low γ̇
- **Infinite-shear plateau**: η constant at high γ̇
- **Yield stress**: finite stress at γ̇ → 0

**Step 3: Select model based on curve shape**

| Curve Shape | Recommended Model |
|-------------|-------------------|
| Single linear log-log region | Power Law |
| Two plateaus + transition | Cross or Carreau |
| Plateaus + asymmetric transition | Carreau-Yasuda |
| Finite stress intercept | Herschel-Bulkley/Bingham |

**Step 4: Fit parameters (example: Power Law)**

For power-law fluids, fit log η vs log γ̇:

```
log η = log K + n log γ̇
     → Linear regression gives:
        - Slope = n
        - Intercept = log K
```

**Python fitting example:**

```python
import numpy as np
from scipy.optimize import curve_fit

# Experimental data
shear_rate = np.array([0.1, 1, 10, 100, 1000])  # 1/s
viscosity = np.array([1.2, 0.8, 0.5, 0.3, 0.2])  # Pa·s

# Power-law model
def power_law(gamma, K, n):
    return K * gamma**(n-1)

# Fit (note: OpenFOAM's K = η·γ̇^(1-n))
params, _ = curve_fit(lambda g, K, n: K * g**(n-1), 
                      shear_rate, viscosity, 
                      p0=[0.5, 0.5])
K_fit, n_fit = params

print(f"K = {K_fit:.4f} Pa·s^{n_fit:.2f}")
print(f"n = {n_fit:.4f}")
```

**Step 5: Convert to OpenFOAM units**

OpenFOAM uses **kinematic viscosity** ν = η/ρ:

```python
rho = 1000  # kg/m³
nu0 = eta0 / rho  # Convert to m²/s
```

### 5.2 Quick Estimation Methods

**When rheometer data is unavailable:**

| Material | Approx. n | Approx. K (Pa·sⁿ) | Estimation method |
|----------|-----------|-------------------|-------------------|
| Blood | 0.35-0.5 | 0.01-0.05 | Literature + adjust hematocrit |
| Polymer 1% | 0.3-0.7 | 0.1-10 | Molecular weight correlation |
| Paint | 0.4-0.8 | τ0+Kγ̇ⁿ | Flow cup test + iteration |
| Food purees | 0.3-0.6 | 1-50 | Back-extrusion test |

**Rule of thumb:**
- **Shear-thinning fluids**: n = 0.2-0.7 (most common)
- **Yield stress fluids**: τ0 ≈ 10-100 Pa for semi-solids
- **Highly pseudoplastic**: n < 0.3 (e.g., xanthan gum)

---

## 6. Mesh Strategy for Non-Newtonian Flows

### 6.1 Why Mesh Resolution Matters More

Non-Newtonian flows have **sharp viscosity gradients** near walls due to:

```
Wall:  γ̇ → 0  →  η → η0 (high viscosity)
        ↓
Bulk:  γ̇ large → η → η∞ (low viscosity)
```

Viscosity may vary by **orders of magnitude** across just a few cell layers.

### 6.2 Wall Meshing Guidelines

**Recommendation:** y⁺ ≈ 1 for non-Newtonian (stricter than Newtonian)

```cpp
// system/blockMeshDict

// Option 1: Graded mesh (recommended)
boundary
{
    wall
    {
        type            wall;
        
        // Grading: small cells at wall, expanding outward
        // 20 cells in wall-normal direction
        // Grading factor 0.1 = size ratio smallest/largest
        grading        (1 0.1 1);  // (x y z) grading
    }
}

blocks
(
    hex (0 1 2 3 4 5 6 7)
    (50 100 1)           // 100 cells in wall-normal (y)
    simpleGrading (1 0.1 1)  // 10:1 expansion from wall
);
```

**Alternative: snappyHexMesh with boundary layers**

```cpp
// system/snappyHexMeshDict

addLayersControls
{
    layers
    {
        "wall.*"
        {
            nSurfaceLayers  15;          // More layers than Newtonian
            
            // First layer thickness (estimated from expected shear rate)
            // For γ̇ ≈ 1000 s⁻¹, want Δy ≈ 0.01/γ̇ = 1e-5 m
            firstLayerThickness  1e-5;   // m
            
            expansionRatio    1.2;       // Gradual expansion
            finalLayerThickness  0.5;    // Relative to overall
            minThickness      0.001;     // Safety minimum
        }
    }
}
```

### 6.3 Mesh Quality Checks

**Run before simulation:**

```bash
checkMesh -allGeometry -allTopology
```

**Critical requirements for non-Newtonian:**

| Metric | Requirement | Why |
|--------|-------------|-----|
| **Non-orthogonality** | < 65° | Viscosity gradients amplify errors |
| **Aspect ratio** | < 100 (preferably < 50) | Extreme ratios cause viscosity oscillation |
| **Skewness** | < 0.8 | Poor skewness causes convergence failure |
| **Near-wall resolution** | Δy < 0.1/γ̇_max | Resolve shear-rate boundary layer |

---

## 7. Complete Worked Example: Pipe Flow of Power-Law Fluid

### 7.1 Problem Statement

**Flow:** 2D axisymmetric pipe, L = 1 m, R = 0.05 m  
**Fluid:** Power-law, n = 0.5, K = 0.05 Pa·sⁿ, ρ = 1000 kg/m³  
**Boundary conditions:** Inlet velocity = 0.1 m/s, outlet pressure = 0 (gauge)  
**Goal:** Compute velocity profile and pressure drop

### 7.2 Case Structure

```bash
powerLawPipe/
├── 0/
│   ├── U
│   ├── p
│   └── nut  (turbulence, if needed)
├── constant/
│   ├── transportProperties
│   ├── polyMesh/
│   └── turbulenceProperties
├── system/
│   ├── blockMeshDict
│   ├── controlDict
│   ├── fvSchemes
│   └── fvSolution
└── Allrun
```

### 7.3 Configuration Files

**`0/U` - Velocity field**

```cpp
dimensions      [0 1 -1 0 0 0 0];

internalField   uniform (0.01 0 0);  // Small initial value

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform (0.1 0 0);  // m/s
    }
    outlet
    {
        type            zeroGradient;
    }
    wall
    {
        type            noSlip;
    }
    axis
    {
        type            symmetryPlane;  // For 2D axisymmetric
    }
}
```

**`0/p` - Pressure field**

```cpp
dimensions      [0 2 -2 0 0 0 0];

internalField   uniform 0;

boundaryField
{
    inlet
    {
        type            zeroGradient;
    }
    outlet
    {
        type            fixedValue;
        value           uniform 0;  // Gauge pressure
    }
    wall
    {
        type            zeroGradient;
    }
    axis
    {
        type            symmetryPlane;
    }
}
```

**`constant/transportProperties`**

```cpp
transportModel  powerLaw;

powerLawCoeffs
{
    nuMax   0.1;        // Pa·s / 1000 kg/m³ = 1e-4 m²/s
    nuMin   1e-9;
    k       0.05;       // Pa·sⁿ (consistency)
    n       0.5;        // Power-law index (shear-thinning)
}
```

**`system/fvSolution` - Relaxation for stability**

```cpp
solvers
{
    p
    {
        solver          GAMG;
        tolerance       1e-6;
        relTol          0.01;
    }
    
    pFinal
    {
        $p;
        relTol          0;
    }
    
    U
    {
        solver          smoothSolver;
        smoother        GaussSeidel;
        tolerance       1e-5;
        relTol          0.1;
    }
}

SIMPLE
{
    nNonOrthogonalCorrectors  2;
    
    relaxationFactors
    {
        U       0.3;      // CRITICAL: Reduce for non-Newtonian
        p       0.3;
        nu      0.5;      // Relax viscosity updates
    }
}
```

### 7.4 Running the Simulation

```bash
# Generate mesh
blockMesh

# Run solver (steady-state)
simpleFoam

# Monitor convergence in another terminal
# Watch residual file
tail -f log.simpleFoam | grep "Solving for"
```

**Expected convergence behavior:**

```
Time = 1
...
Solving for U, Initial residual = 0.5, Final residual = 0.003
Solving for p, Initial residual = 0.8, Final residual = 0.02
Time = 2
...
Solving for U, Initial residual = 0.3, Final residual = 0.001
...
[Continue until residuals < 1e-4]
```

### 7.5 Post-Processing

**Extract velocity profile:**

```bash
# Sample along radius at outlet
sample -dict system/sampleDict

# system/sampleDict:
// locations
mesh
{
    type    midPoint;
    axis    xyz;
}
// fields
fields
(
    U
    p
    nu
);
// sets
sets
(
    outletProfile
    {
        type    uniform;
        axis    y;  // Radial direction
        start   (1.0 0.0 0.0);
        end     (1.0 0.05 0.0);
        nPoints 100;
    }
);
```

**Visualization in ParaView:**

1. Open `powerLawPipe.foam`
2. Create **Slice** at outlet (x = 1.0)
3. Plot **U** over line (radial coordinate)
4. Add **nu** (kinematic viscosity) to see variable viscosity field

**Expected analytical comparison** (power-law pipe flow):

```
u(r) = u_max * [1 - (r/R)^((n+1)/n)]

For n = 0.5: u(r) = u_max * [1 - (r/R)^3]
```

The numerical solution should match within ~5% if mesh is adequate.

---

## 8. Convergence and Stability Strategies

### 8.1 Common Convergence Issues

| Symptom | Cause | Solution |
|---------|-------|----------|
| **Oscillating residuals** | Viscosity overshoot | Reduce relaxation; limit ν_max/ν_min |
| **Divergence after few iterations** | Initial guess far from solution | Start with Newtonian, gradually switch |
| **Slow convergence** | Strong coupling | Use under-relaxation; more correctors |
| **Local instability** | Poor mesh quality | Refine near walls; reduce aspect ratio |
| **"Maximum iterations exceeded"** | Solver tolerance too tight | Loosen solver tolerance initially |

### 8.2 Stability Techniques

**Technique 1: Progressive ramping**

```cpp
// Gradually reduce relaxation during simulation
SIMPLE
{
    relaxationFactors
    {
        U       0.7;      // Start relaxed
        p       0.7;
    }
}
// After 100 iterations, manually edit fvSolution:
// U: 0.7 → 0.5 → 0.3
// p: 0.7 → 0.5 → 0.3
```

**Technique 2: Viscosity limiting**

Prevents extreme values that cause instability:

```cpp
powerLawCoeffs
{
    nuMax   100.0;    // Upper bound (m²/s)
    nuMin   1e-6;     // Lower bound (prevents zero viscosity)
}
```

**Technique 3: Pseudo-transient continuation**

Use transient solver to "march" to steady state:

```cpp
// Use pimpleFoam instead of simpleFoam
// system/controlDict:

application     pimpleFoam;

deltaT          0.001;     // Small time step
endTime         1.0;       // Run until steady

// system/fvSolution:
PIMPLE
{
    nCorrectors     2;
    nNonOrthogonalCorrectors  0;
    
    relaxationFactors
    {
        U       0.3;
        p       0.3;
    }
}
```

**Technique 4: Initialize as Newtonian**

```cpp
// Start with simple Newtonian fluid
transportModel  Newtonian;
nu              0.001;

// Run for 50 iterations
simpleFoam > log.newtonian &

// Then switch to non-Newtonian
// Edit constant/transportProperties:
transportModel  powerLaw;
powerLawCoeffs { ... }

// Restart
simpleFoam > log.nonnewtonian &
```

### 8.3 Monitoring Convergence

**Key indicators to track:**

```bash
# Extract residuals
grep "Solving for U" log.simpleFoam | \
    awk '{print $4, $7, $10}' > residuals_U.dat

# Plot with gnuplot or Python
```

**Convergence criteria:**

1. **Residuals** < 1e-4 for U, p
2. **Balance check:** Inlet mass flow ≈ Outlet mass flow (within 1%)
3. **Field stability:** Max(U) and Min(U) not changing significantly
4. **Viscosity field:** Smooth distribution, no localized spikes

---

## 9. Post-Processing and Visualization

### 9.1 Writing Viscosity Field

OpenFOAM does **not** write ν by default — must enable:

```cpp
// system/controlDict

functions
{
    viscosityField
    {
        type            writeObjects;
        objects         (nu);  // kinematic viscosity
        writeControl    timeStep;
        writeInterval   10;
    }
    
    shearRate
    {
        // Shear rate magnitude: |γ̇| = √(2 D:D)
        type            coded;
        functionObjectLibs ("libutilityFunctionObjects.so");
        writeControl    timeStep;
        writeInterval   10;
        
        codeWrite
        #{
            const volScalarField magShearRate
            (
                mag(symm(fvc::grad(U)))
            );
            magShearRate.write();
        #};
    }
}
```

### 9.2 ParaView Visualization

**Visualization checklist:**

1. **Variable viscosity field**
   - Open `.foam` file in ParaView
   - Color by `nu` (kinematic viscosity)
   - Should show high ν near walls, low ν in bulk

2. **Shear rate distribution**
   - Display `magShearRate` (if written)
   - Identify high-shear regions (walls, contractions)

3. **Streamlines**
   - Use **Stream Tracer** filter
   - Color by velocity magnitude or ν

4. **Comparison slices**
   - Compare velocity profiles at different x-locations
   - Verify developed flow (profiles should match)

### 9.3 Quantitative Analysis

**Pressure drop calculation:**

```python
# Extract pressure at inlet and outlet
import pandas as pd
import numpy as np

# Sample output from postProcessing/sample/
inlet_p = pd.read_csv('postProcessing/sample/1000/inlet_U_p.csv')
outlet_p = pd.read_csv('postProcessing/sample/1000/outlet_U_p.csv')

dp = inlet_p['p'].mean() - outlet_p['p'].mean()
print(f"Pressure drop: {dp:.2f} Pa")

# Compare with analytical (for power-law pipe flow):
# Δp/L = (2K/L) * ((3n+1)/n)^n * (Q/(πR³))^n * R
```

**Flow rate calculation:**

```bash
# Integrate velocity at outlet
postProcess -func "patchIntegrate(U,outlet)"

# Output gives flux (m³/s)
```

---

## 10. Advanced Topics

### 10.1 Temperature-Dependent Viscosity

Many fluids have strong temperature dependence (e.g., polymer melts):

```cpp
transportModel  temperatureDependent;

temperatureDependentCoeffs
{
    // Arrhenius-type model
    nu0     0.01;       // Reference viscosity
    T0      293;        // Reference temperature (K)
    Ea_R    2000;       // Activation energy / gas constant
    
    // Nu = nu0 * exp(Ea/R * (1/T - 1/T0))
}
```

**Requires:** Conjugate heat transfer solver (e.g., `buoyantSimpleFoam`)  
**Cross-reference:** See [02_Conjugate_Heat_Transfer.md](02_Conjugate_Heat_Transfer.md) in MODULE 06.

### 10.2 Coupling with Turbulence

**For high Reynolds number non-Newtonian flows:**

```cpp
// constant/turbulenceProperties
simulationType  RAS;

RAS
{
    RASModel        kEpsilon;
    
    // Modify turbulence for variable viscosity
    turbulence      on;
    
    // Optional: viscosity-dependent turbulence
    // (e.g., low-Re corrections)
}
```

**Challenge:** Standard turbulence models assume Newtonian fluid  
**Approach:** Use effective viscosity ν_eff = ν + ν_t in turbulence equations  
**Caution:** Model validity for non-Newtonian turbulence is **not well-established**

### 10.3 Parallel Run Considerations

Non-Newtonian simulations may have **load imbalance** due to:

- Varying viscosity across domains
- Different iteration counts per processor

**Mitigation:**

```bash
# Use decomposition that minimizes boundary communication
decomposePar -method scotch -force 64

# Run in parallel
mpirun -np 64 simpleFoam -parallel

# Reconstruct
reconstructPar
```

---

## 11. Troubleshooting Guide

### 11.1 Quick Diagnostic Checklist

| Check | Command | Expected Result |
|-------|---------|-----------------|
| **Mesh quality** | `checkMesh` | No failed checks |
| **Boundary conditions** | `foamListBC` | All faces assigned |
| **Initial fields** | `paraFoam -builtin` | No undefined regions |
| **Transport model** | `grep transportModel constant/transportProperties` | Model name matches |
| **Parameter sanity** | Visual inspection | ν₀ > ν∞, 0.1 < n < 2 |

### 11.2 Common Error Messages

**Error: "Unknown transportModel [ModelName]"**

```
→ Cause: Typo in model name or model not compiled
→ Fix: Check spelling; use exact case (e.g., powerLaw, not PowerLaw)
→ Verify: ls $FOAM_SRC/transportModels
```

**Error: "Maximum number of iterations exceeded"**

```
→ Cause: Solver cannot converge within maxIters
→ Fix: Increase maxIters in fvSolution, or loosen tolerance
→ Check: Is viscosity varying too rapidly? Add viscosity limits.
```

**Error: "Negative viscosity encountered"**

```
→ Cause: Power-law model with n > 1 AND low shear rate
→ Fix: Add nuMax/nuMin limits; check K parameter
→ Prevent: Initialize with reasonable velocity field
```

**Error: "Floating point exception"**

```
→ Cause: Division by zero (often in viscosity calculation)
→ Fix: Ensure nuMin > 0; check for zero shear rate regions
→ Debug: Write shear rate field to identify problem zones
```

### 11.3 Performance Tuning

**Speed up convergence:**

1. **Better initial guess**
   ```cpp
   // Use potentialFlow solver for initialization
   potentialFoam -writep
   ```

2. **Coarse-to-fine strategy**
   ```bash
   # Run on coarse mesh first (2x coarser)
   # Then map to fine mesh:
   mapFields ../coarseCase -sourceTime latestTime
   ```

3. **Linear solver optimization**
   ```cpp
   // system/fvSolution
   U
   {
       solver          GAMG;        // Faster for large meshes
       smoother        GaussSeidel;
       tolerance       1e-5;
       relTol          0.1;
       
       // Multigrid settings
       cacheAgglomeration on;
       nCellsInCoarsestLevel 100;
   }
   ```

---

## Key Takeaways

1. **Solver selection** starts with standard incompressible solvers (`simpleFoam`, `pimpleFoam`) — specialized rheology solvers only for viscoelastic fluids with significant elastic effects.

2. **Transport properties configuration** is the primary control point for non-Newtonian behavior — model selection and parameter accuracy are critical for physical realism.

3. **Parameter estimation** from rheometer data follows a systematic workflow: (1) collect viscosity vs. shear rate data, (2) identify flow regime, (3) select appropriate model, (4) fit parameters via regression, (5) convert to OpenFOAM units (kinematic viscosity).

4. **Mesh resolution** near walls is more critical for non-Newtonian flows than Newtonian — viscosity can vary by orders of magnitude across boundary layers; use graded or boundary-layer meshing with y⁺ ≈ 1.

5. **Convergence challenges** arise from strong nonlinearity; mitigation strategies include viscosity limiting (`nuMax`, `nuMin`), under-relaxation (U, p ≤ 0.3), progressive ramping, and pseudo-transient continuation.

6. **Post-processing** for non-Newtonian flows requires explicit writing of the viscosity field (`nu`) and shear rate (`magShearRate`) via controlDict functions — these are not written by default.

7. **Validation** against analytical solutions (e.g., power-law pipe flow) or experimental data is essential — compare velocity profiles, pressure drop, and viscosity distributions.

8. **Common failure modes** include: oscillating residuals (reduce relaxation), divergence from poor initialization (start Newtonian), and instability from extreme viscosity values (use viscosity limits).

9. **Advanced considerations** include temperature-dependent viscosity (requires conjugate heat transfer), turbulence coupling (model validity uncertain), and parallel load balancing for variable viscosity fields.

10. **Practical workflow**: (1) Estimate parameters from data/literature, (2) Set up case with appropriate solver, (3) Refine mesh near walls, (4) Configure stability controls (relaxation, limits), (5) Run with monitoring, (6) Validate against benchmarks, (7) Post-process viscosity and shear rate fields.

---

## Practice Problems

### Problem 1: Model Selection

For each application, recommend the most appropriate viscosity model and justify:

(a) Blood flow in a coronary artery  
(b) Paint coating on a vertical surface  
(c) Polymer melt extrusion through a die  
(d) Cement paste pumping in a pipeline  
(e) Chocolate flowing through a nozzle

**Hint:** Consider shear rate range, yield stress, and temperature effects.

---

### Problem 2: Parameter Estimation

You have rheometer data for a food product:

| γ̇ (1/s) | η (Pa·s) |
|---------|----------|
| 0.1     | 10.5     |
| 1       | 3.2      |
| 10      | 1.0      |
| 100     | 0.4      |
| 1000    | 0.35     |

(a) Plot log η vs. log γ̇ and identify the flow regime  
(b) Fit a power-law model (estimate K and n)  
(c) Check if a Cross model would be more appropriate  
(d) Convert parameters to OpenFOAM input format (ρ = 1050 kg/m³)

---

### Problem 3: Mesh Sensitivity

For a power-law fluid (n = 0.4, K = 0.1 Pa·sⁿ) in a 4:1 contraction:

(a) Calculate expected shear rate at the wall for Re = 100  
(b) Determine required near-wall cell size for y⁺ ≈ 1  
(c) Design a graded mesh specification for `blockMeshDict`  
(d) Estimate total cell count for a 3D axisymmetric geometry

---

### Problem 4: Convergence Troubleshooting

A `simpleFoam` case for a Herschel-Bulkley fluid shows:

```
Time = 45
Solving for U, Initial residual = 0.03, Final residual = 0.002
Solving for p, Initial residual = 0.15, Final residual = 0.008
Time = 46
Solving for U, Initial residual = 0.04, Final residual = 0.003
Solving for p, Initial residual = 0.18, Final residual = 0.01
```

The residuals are **increasing** instead of decreasing.

(a) Diagnose the likely cause  
(b) Propose 3 specific remedial actions  
(c) Write modified `fvSolution` settings to implement your solution

---

### Problem 5: Post-Processing

Given a converged power-law pipe flow case:

(a) Write a `controlDict` function to output: (i) ν field, (ii) γ̇ magnitude, (iii) wall shear stress  
(b) Create a ParaView pipeline to compare numerical vs. analytical velocity profiles  
(c) Calculate the friction factor and compare with the theoretical value for n = 0.6

---

## 📖 Further Reading

### OpenFOAM Documentation

- **User Guide:** Section 4.4 - Transport Models  
- ** Programmer's Guide:** Chapter 6 - Turbulence Modeling (discusses transport properties)  
- **Doxygen:** `PowerLaw` and `CrossPowerLaw` classes

### Cross-References Within This Module

- **Fundamentals:** [01_Non_Newtonian_Fundamentals.md](01_Non_Newtonian_Fundamentals.md) — Theoretical background
- **Viscosity Models:** [02_Viscosity_Models.md](02_Viscosity_Models.md) — Complete model equations
- **Numerical Implementation:** [04_Numerical_Implementation.md](04_Numerical_Implementation.md) — How models are coded in OpenFOAM
- **Architecture:** [03_OpenFOAM_Architecture.md](03_OpenFOAM_Architecture.md) — Class hierarchy for transport models

### External Resources

1. **Bird, R.B., Armstrong, R.C., and Hassager, O.** (1987). *Dynamics of Polymeric Liquids, Vol. 1* (2nd ed.). Wiley. — **Authoritative reference** for rheology models.

2. **Macosko, C.W.** (1994). *Rheology: Principles, Measurements, and Applications*. Wiley. — Practical rheometry techniques.

3. **Chhabra, R.P., and Richardson, J.F.** (2008). *Non-Newtonian Flow and Applied Rheology* (2nd ed.). Butterworth-Heinemann. — Engineering applications.

4. **OpenFOAM Wiki:** [Non-Newtonian Flow](https://openfoamwiki.net/index.php/Non-Newtonian_Flow) — Community examples and tips.

5. **Tukovic, et al.** (2018). "OpenFOAM for Non-Newtonian Fluid Flow Simulations." *Journal of Polymers*. — Case studies and validation.

---

**Next:** [04_Numerical_Implementation.md](04_Numerical_Implementation.md) — How non-Newtonian models are implemented in OpenFOAM's source code.