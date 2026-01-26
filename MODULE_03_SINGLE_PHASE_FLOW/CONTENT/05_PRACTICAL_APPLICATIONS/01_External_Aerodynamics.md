# External Aerodynamics

การจำลองพลศาสตร์อากาศภายนอกใน OpenFOAM

---

## Learning Objectives

After completing this module, you will be able to:

1. **Calculate drag and lift coefficients** within 5% of experimental values using proper force coefficient setup
2. **Design appropriate computational domains** for external aerodynamics simulations following established sizing guidelines
3. **Configure boundary layer meshing** with correct y+ values for wall-resolved or wall function approaches
4. **Implement turbulence models** (k-ω SST, k-ε, DES) for flow separation prediction
5. **Set up function objects** for force, moment, and coefficient calculations
6. **Analyze wake structures** and identify flow separation regions
7. **Troubleshoot convergence issues** related to mesh quality, boundary conditions, and solver settings

---

## Overview

### WHAT: External Aerodynamics Simulation

**External aerodynamics** involves predicting flow behavior around objects moving through air or stationary objects in airflow. Key applications include:

- **Automotive:** Vehicle drag reduction, lift optimization, cooling system design
- **Aerospace:** Wing lift prediction, aircraft drag minimization, propeller analysis
- **Civil engineering:** Wind loading on buildings, bridge aerodynamics
- **Sports:** Ball trajectory prediction, cyclist aerodynamics

### WHY: Physical Importance and Practical Value

**Engineering Impact:**
- **Fuel Efficiency:** 10% drag reduction ≈ 5-7% fuel savings for vehicles
- **Performance:** Lift-to-drag ratio determines aircraft range and efficiency
- **Safety:** Wind loads govern structural design of buildings and bridges
- **Compliance:** Regulatory requirements for emissions and safety standards

**Physical Phenomena:**
- **Flow Separation:** Adverse pressure gradients cause boundary layer detachment
- **Wake Formation:** Low-pressure regions behind objects create dominant drag contribution
- **Vortex Shedding:** Periodic vortex formation (St ≈ 0.2 for cylinders) causes oscillating forces
- **Boundary Layer Transition:** Laminar-to-turbulent transition affects separation location

### HOW: OpenFOAM Implementation

**Workflow Overview:**
1. **Domain Design:** Size computational domain to avoid boundary interference (5-10L upstream, 15-20L downstream)
2. **Mesh Generation:** Use snappyHexMesh with surface refinement, wake region refinement, and boundary layer cells
3. **Physics Setup:** Configure incompressible solver (simpleFoam/pimpleFoam) with appropriate turbulence model
4. **Boundary Conditions:** Freestream inlet, pressure outlet, no-slip walls, symmetry/slip sides
5. **Force Calculation:** Use `forces` and `forceCoeffs` function objects for real-time monitoring
6. **Post-Processing:** Analyze wake profiles, pressure distributions, and force contributions

---

## 1. Fundamental Equations and Parameters

### Force Coefficients

The dimensionless force coefficients are defined as:

$$C_D = \frac{F_D}{0.5 \rho U_\infty^2 A}, \quad C_L = \frac{F_L}{0.5 \rho U_\infty^2 A}$$

where:
-1$F_D, F_L1= Drag and lift forces [N]
-1$\rho1= Fluid density [kg/m³]
-1$U_\infty1= Freestream velocity [m/s]
-1$A1= Reference area (frontal for drag, planform for lift) [m²]

**Calculation in OpenFOAM:** Force coefficients are computed automatically using function objects (see Section 4)

### Pressure Coefficient

$$C_p = \frac{p - p_\infty}{0.5 \rho U_\infty^2}$$

-1$C_p = 11at stagnation points
-1$C_p < 01in separated wake regions
- Used to identify separation and reattachment points

### Strouhal Number (Vortex Shedding)

$$St = \f_s D}{U_\infty}$$

For circular cylinders:
-1$St \approx 0.21for1$10^3 < Re_D < 10^5$
- Vortex shedding frequency:1$f_s = St \cdot U_\infty / D$

**Implication:** Transient simulations require time step resolution of at least 20 samples per shedding cycle

### Reynolds Number

$$Re_L = \frac{\rho U_\infty L}{\mu}$$

Characteristic length1$L1varies by application:
- Vehicles: Wheelbase or length
- Airfoils: Chord length
- Cylinders: Diameter

---

## 2. Domain Sizing Guidelines

### Minimum Domain Dimensions

| Direction | Minimum Size | Rationale |
|-----------|--------------|-----------|
| Upstream | 5-10L | Allows boundary layer development, avoids inlet influence |
| Downstream | 15-20L | Permits wake recovery, prevents outlet BC reflection |
| Sides | 5-10L | Minimizes blockage ratio (< 3% for accuracy) |
| Top | 5-10L | Reduces ceiling effects on flow separation |

**Blockage Ratio:**1$\frac{A_{object}}{A_{inlet}} < 0.031(3%)

For ground vehicles:
- **Ground clearance:** 0.5-1.0 × vehicle height
- **Moving ground:** Use `fixedValue` with vehicle velocity for realistic road simulation

### Domain Creation Example (blockMeshDict)

```cpp
vertices
(
    (0 0 0)              // 0: origin
    (10 0 0)             // 1: 10L upstream
    (40 0 0)             // 2: 30L downstream
    (-5 -5 0)            // 3: side boundary
    (15 -5 0)            // 4: side boundary
    (45 -5 0)            // 5: side boundary
    // ... add top vertices
);

blocks
(
    hex (0 1 2 3 4 5 6 7) (100 50 30) simpleGrading (1 1 1)
);
```

---

## 3. Mesh Generation Strategy

### 3.1 Surface Refinement

```cpp
// system/snappyHexMeshDict
refinementSurfaces
{
    vehicle
    {
        level (2 2);              // Base surface refinement
        patchInfo { type wall; }
    }
    
    wheels
    {
        level (3 3);              // Higher refinement for small features
        patchInfo { type wall; }
    }
}
```

**Refinement Levels:**
- **Level 2-3:** General surface (Δx ≈ 0.125-0.0625 m for 1 m base)
- **Level 4-5:** Critical regions (edges, corners)
- **Level 6-7:** Small features (mirrors, wipers)

### 3.2 Wake Region Refinement

```cpp
refinementRegions
{
    wakeBox
    {
        mode inside;
        levels ((10 2) (20 3));  // Distance from surface: refinement level
    }
    
    separationZone
    {
        mode inside;
        levels ((5 3));
    }
}
```

**Wake Box Placement:**
- Extends from rear of object to domain outlet
- Width: 2-3 × object width
- Height: 2-3 × object height

### 3.3 Boundary Layer Meshing

```cpp
addLayersControls
{
    layers
    {
        vehicle
        {
            nSurfaceLayers      15;        // Number of prism layers
            expansionRatio      1.2;       // Growth rate
            finalLayerThickness 0.5;       // mm (relative to surface)
            minThickness        0.01;      // Prevent collapsed cells
        }
    }
    
    // Layer shrinking to handle curvature
    relativeSizes        true;
    layerTermination     angle;
    maxFaceThicknessRatio 0.5;
}
```

### 3.4 y+ Guidelines

| Approach | Target y+ | First Cell Height | Layers | Application |
|----------|-----------|-------------------|--------|-------------|
| **Wall-resolved LES** | ≈ 1 |1$\Delta y_1 = \frac{y^+ \mu}{\rho u_\tau}1| 20-30 | Fundamental research, high-fidelity |
| **Wall-resolved RANS** | ≈ 1 |1$\Delta y_1 \approx 10^{-5}1m (air, 30 m/s) | 15-20 | Accurate separation prediction |
| **Wall functions** | 30-300 |1$\Delta y_1 \approx 10^{-3}1m (air, 30 m/s) | 5-10 | Industrial applications, fast turnaround |
| **Rough walls** | > 300 | >1$10^{-2}1m | 3-5 | Rough surfaces, ground vehicles |

**First Cell Height Calculator:**

$$\Delta y_1 = \frac{y^+ \mu}{\rho u_\tau}, \quad u_\tau = U_\infty \sqrt{\frac{C_f}{2}}$$

For air at 30 m/s (flat plate,1$C_f \approx 0.003$):
- Wall-resolved ($y^+ = 1$):1$\Delta y_1 \approx 1 \times 10^{-5}1m = 0.01 mm
- Wall functions ($y^+ = 100$):1$\Delta y_1 \approx 1 \times 10^{-3}1m = 1 mm

---

## 4. Force Calculation and Function Objects

### 4.1 Force Coefficients Function Object

```cpp
// system/controlDict
functions
{
    forceCoeffs
    {
        type        forceCoeffs;
        libs        (forces);
        
        // Patches to integrate forces over
        patches     (vehicleBody wheels mirrors);
        
        // Density settings
        rho         rhoInf;        // Use constant density
        rhoInf      1.225;         // kg/m³ (air at 15°C)
        
        // Reference quantities
        magUInf     30.0;          // Freestream velocity [m/s]
        lRef        4.5;           // Reference length [m] (wheelbase)
        Aref        2.2;           // Reference area [m²] (frontal)
        
        // Force directions
        dragDir     (1 0 0);       // Drag = x-direction
        liftDir     (0 0 1);       // Lift = z-direction
        pitchAxis   (0 1 0);       // Pitching moment about y-axis
        
        // Output control
        writeFields  yes;
        log          yes;
        
        // Bin data for sectional analysis
        binData
        {
            nBin        20;           // Number of bins
            direction   (1 0 0);      // Binning direction
            cumulative  yes;
        }
    }
}
```

**Output Location:** `postProcessing/forceCoeffs/0/forceCoeffs.dat`

**Output Format:**
```
# Time        Cd        Cl        Cm        Cd(pressure)    Cd(friction)    Cl(pressure)    Cl(friction)
0            0.321     0.156     -0.042    0.298           0.023           0.151           0.005
100          0.315     0.152     -0.039    0.292           0.023           0.147           0.005
```

### 4.2 Raw Forces Function Object

```cpp
forces
{
    type        forces;
    libs        (forces);
    
    patches     (vehicleBody);
    rho         rhoInf;
    rhoInf      1.225;
    
    // Center of rotation for moments
    CofR        (0 0 0);       // Origin for moment calculation
    
    writeFields  yes;
}
```

**Output:** `postProcessing/forces/0/forces.dat`

### 4.3 Pressure Field Sampling

```cpp
pressureCoeff
{
    type            surfaceRegion;
    libs            (surfMesh);
    
    surfaceFormat   vtk;
    regionType      patch;
    name            vehicleBody;
    
    operation       none;
    fields          (p Cp);
    
    // Write Cp field
    writeFields     yes;
}
```

---

## 5. Turbulence Modeling

### 5.1 Model Selection Guide

| Model | Accuracy | Computational Cost | Memory | Best Use Case |
|-------|----------|-------------------|--------|---------------|
| **k-ω SST** | High (separation) | Medium | Medium | **Recommended default** - attached + mild separation |
| **k-ε** | Medium (separation) | Low | Low | Free shear flows, quick iterations |
| **Spalart-Allmaras** | Medium | Low | Low | Aerodynamic flows with thin shear layers |
| **LES (Smagorinsky)** | Very High | Very High | High | Unsteady wake dynamics, vortex shedding |
| **DES** | High | High | High | Massive separation, bluff bodies |

**Cross-Reference:** For detailed turbulence model theory and implementation, see [Turbulence Modeling Module](../03_TURBULENCE_MODELING/00_Overview.md).

### 5.2 k-ω SST Configuration (Recommended)

```cpp
// constant/turbulenceProperties
simulationType RAS;

RAS
{
    RASModel        kOmegaSST;
    
    turbulence      on;
    
    // Production limiter (prevents over-prediction)
    kOmegaSSTCoeffs
    {
        alphaK1     0.85;
        alphaK2     1.0;
        beta1       0.075;
        beta2       0.0828;
        betaStar    0.09;
        gamma1      0.5532;
        gamma2      0.4403;
        a1          0.31;
        b1          1.0;
        c1          10.0;
    }
}
```

**Advantages of k-ω SST:**
- Combines k-ω near walls (accurate adverse pressure gradient response)
- Switches to k-ε in freestream (robust to inlet turbulence)
- Automatic wall treatment works for y+ = 1 to y+ = 300

### 5.3 Detached Eddy Simulation (DES)

For massive separation (e.g., Formula 1 car, bluff bodies):

```cpp
// constant/turbulenceProperties
simulationType LES;
LES
{
    LESModel        SpalartAllmarasDDES;
    
    turbOnFinalIterOnly false;  // Calculate turbulence every iteration
    
    // DDES shielding function
    DDESCoeffs
    {
        CDES        0.65;       // DES constant
        fd          0.0;        // Delayed function
    }
}
```

**DES Requirements:**
- y+ ≈ 1 (no wall functions)
- Δx ≈ Δy ≈ Δz in wake (isotropic cells)
- Time step: Δt < 0.005 s (resolve vortex shedding)

---

## 6. Boundary Conditions

### 6.1 Inlet Boundary Conditions

```cpp
// 0/U
inlet
{
    type            freestreamVelocity;
    freestreamValue uniform (30 0 0);      // m/s
}

// 0/p
inlet
{
    type            freestreamPressure;
    freestreamValue uniform 0;            // Pa (gauge pressure)
}

// 0/k
inlet
{
    type            fixedValue;
    value           uniform 0.24;          // k = 1.5*(U*I)²
                                            // I = 0.5% (0.5% turbulence intensity)
}

// 0/omega (for k-ω SST)
inlet
{
    type            fixedValue;
    value           uniform 18.9;          // ω = k^0.5 / (0.09*l)
                                            // l = 0.07*L (mixing length)
}

// 0/nut (turbulent viscosity)
inlet
{
    type            calculated;
    value           uniform 0;
}
```

**Turbulence Intensity Guidelines:**
- **Low turbulence:** I = 0.1-1% (wind tunnel, atmospheric)
- **Medium turbulence:** I = 1-5% (automotive road conditions)
- **High turbulence:** I = 5-20% (industrial environments)

### 6.2 Outlet Boundary Conditions

```cpp
// 0/p
outlet
{
    type            fixedValue;
    value           uniform 0;            // Gauge pressure = 0
}

// 0/U
outlet
{
    type            inletOutlet;          // Zero gradient for outflow
    inletValue      uniform (30 0 0);     // Value for backflow
}

// 0/k, 0/omega
outlet
{
    type            inletOutlet;
    inletValue      uniform 0.24;         // Same as inlet
}
```

**Alternative Outlet:** `zeroGradient` for all variables (if no backflow expected)

### 6.3 Wall Boundary Conditions

**No-Slip Wall (Vehicle Surface):**

```cpp
// 0/U
vehicleBody
{
    type            noSlip;
}

// 0/p
vehicleBody
{
    type            zeroGradient;
}

// 0/k
vehicleBody
{
    type            kLowReWallFunction;   // For y+ ≈ 1
    value           uniform 0;            // Alternatives:
}                                         // - kqWallFunction (y+ > 30)

// 0/omega
vehicleBody
{
    type            omegaWallFunction;
    value           uniform 0;            // Automatic switching based on y+
}

// 0/nut
vehicleBody
{
    type            nutkWallFunction;     // Automatic y+ handling
    value           uniform 0;
}
```

**Moving Ground (for automotive):**

```cpp
ground
{
    type            fixedValue;
    value           uniform (30 0 0);     // Vehicle velocity
}
```

**Symmetry/Side Boundaries:**

```cpp
sides
{
    type            symmetry;             // Enforce zero normal gradient
}

// Alternative: slip (allows tangential flow)
sides
{
    type            slip;
}
```

---

## 7. Solver Configuration

### 7.1 Steady-State Solver (simpleFoam)

**Use For:**
- Initial flow field development
- Quick design iterations
- Attached/weakly separated flows

```cpp
// system/fvSolution
SIMPLE
{
    nNonOrthogonalCorrectors 2;
    
    residualControl
    {
        p       1e-6;
        U       1e-6;
        k       1e-6;
        omega   1e-6;
    }
}

relaxationFactors
{
    fields
    {
        p       0.3;                     // Pressure under-relaxation
    }
    equations
    {
        U       0.7;                     // Momentum under-relaxation
        k       0.7;                     // Turbulence kinetic energy
        omega   0.7;                     // Specific dissipation rate
    }
}
```

**Convergence Criteria:**
- Residuals drop by 3-4 orders of magnitude
- Force coefficients stabilize (ΔCd < 0.001 over 100 iterations)
- Mass balance:1$\sum \dot{m}_{in} - \sum \dot{m}_{out} < 0.1\%$

### 7.2 Transient Solver (pimpleFoam)

**Use For:**
- Strong flow separation
- Vortex shedding analysis
- Unsteady wake dynamics
- DES/LES simulations

```cpp
// system/fvSolution
PIMPLE
{
    nCorrectors      2;                   // Pressure correctors per time step
    nNonOrthogonalCorrectors 2;
    
    nOuterCorrectors 1;                   // Momentum equation iterations
}

// system/controlDict
application     pimpleFoam;

startFrom       startTime;
startTime       0;

stopAt          endTime;
endTime         5.0;                      // Simulation time [s]

deltaT          0.001;                   // Initial time step [s]

adjustTimeStep  yes;
maxCo           0.8;                     // Max Courant number
maxAlphaCo      0.8;                     // For VOF models (not used here)

writeControl    timeStep;
writeInterval   50;                      // Write every 50 time steps

functions
{
    // Monitor force coefficients in real-time
    forceCoeffs
    {
        // ... (see Section 4.1)
    }
}
```

**Time Step Calculation:**

$$\Delta t < \frac{Co \cdot \Delta x}{U_\infty}$$

For Co = 0.8, Δx = 0.01 m, U = 30 m/s:
- Δt < 0.8 × 0.01 / 30 ≈ 2.7 × 10⁻⁴ s

**Vortex Shedding Resolution:**
- Shedding period:1$T_s = 1/f_s = D / (St \cdot U_\infty)$
- Required time steps per period: > 20
- Example (cylinder, D = 0.1 m, St = 0.2, U = 30 m/s):
  -1$T_s1= 0.1 / (0.2 × 30) = 0.0167 s
  - Δt < 0.0167 / 20 ≈ 8 × 10⁻⁴ s

### 7.3 Numerical Schemes

```cpp
// system/fvSchemes
ddtSchemes
{
    default         Euler;                // Steady: none, Transient: Euler or backward
}

gradSchemes
{
    default         Gauss linear;
    grad(U)         Gauss linear;         // Alternative: cellLimited Gauss linear 1
}

divSchemes
{
    default         none;
    
    div(phi,U)      Gauss linearUpwindV grad(U);   // Second-order upwind
    div(phi,k)      Gauss upwind;                  // First-order (robust)
    div(phi,omega)  Gauss upwind;
    
    // For DES/LES, use bounded schemes:
    // div(phi,U)      Gauss LUST grad(U);
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
```

---

## 8. Post-Processing and Analysis

### 8.1 Wake Analysis

```cpp
// system/controlDict
functions
{
    wakeLineX
    {
        type            sets;
        libs            (sampling);
        
        setFormat       raw;
        
        sets
        (
            wakeLineX
            {
                type    uniform;
                axis    x;              // Sampling direction
                start   (3 0 0);        // Behind object
                end     (10 0 0);       // Further downstream
                nPoints 100;            // Resolution
            }
            
            wakeLineZ
            {
                type    uniform;
                axis    z;              // Vertical profile
                start   (5 -1 0);
                end     (5 -1 3);
                nPoints 100;
            }
        );
        
        fields          (p U k omega Cp);
        
        // Write to CSV for MATLAB/Python
        writeControl    timeStep;
        writeInterval   1;
    }
}
```

**Analysis Metrics:**
- **Wake deficit:**1$\Delta U = U_\infty - U_{wake}1(target: < 20% at outlet)
- **Pressure recovery:**1$C_p1should approach 0 at outlet
- **Turbulence intensity:**1$I = \sqrt{\frac{2}{3}k} / U1in wake

### 8.2 Surface Pressure Distribution

```cpp
surfacePressure
{
    type            surfaces;
    libs            (surfMesh);
    
    surfaceFormat   vtk;
    
    fields          (p Cp);
    
    surfaces
    (
        vehicleSurface
        {
            type        patch;
            patches     (vehicleBody);
            triangulate  false;
        }
    );
}
```

**Visualization:**
- ParaView: `Cp` field on vehicle surface
- Identify: High1$C_p1at stagnation, low1$C_p1in separated regions

### 8.3 Drag Decomposition

**Total Drag Components:**

$$C_D = C_{D,pressure} + C_{D,friction}$$

- **Pressure Drag:** Dominant for bluff bodies (70-90% for cars)
- **Friction Drag:** Dominant for streamlined bodies (airfoils: 50-70%)

**Extract from Output:**

```bash
# Parse forceCoeffs.dat
tail -1 postProcessing/forceCoeffs/0/forceCoeffs.dat
# Output: 0.315  0.152  -0.039  0.292  0.023  0.147  0.005
#                       Cd_total  Cl     Cm     Cd_p  Cd_f    Cl_p    Cl_f
```

**Percentage Calculation:**
- Pressure drag %:1$C_{D,pressure} / C_D × 100 = 0.292 / 0.315 × 100 ≈ 93\%$
- Friction drag %:1$C_{D,friction} / C_D × 100 = 0.023 / 0.315 × 100 ≈ 7\%$

### 8.4 Q-Criterion for Vortex Identification

```cpp
// system/controlDict (for transient cases)
QCriterion
{
    type            functionObject;
    libs            (fieldFunctionObjects);
    
    // Q = 0.5*(||Ω||² - ||S||²)
    // Ω = vorticity tensor, S = strain rate tensor
    
    writeFields     yes;
    
    // Auto-generated field: Q
}
```

**Visualization:**
- ParaView: Contour `Q` field (typical range: 100-1000 s⁻²)
- Identify: Vortex cores, separation lines, wake structures

---

## 9. Troubleshooting Guide

### 9.1 Convergence Issues

| Symptom | Possible Cause | Solution |
|---------|----------------|----------|
| **Residuals oscillating** | Under-relaxation too high | Reduce `p` to 0.2, `U` to 0.5 in `fvSolution` |
| **Forces not stabilizing** | Poor mesh quality | Check `checkMesh` output: non-orthogonality < 70°, skewness < 2 |
| **Slow convergence** | Inadequate initial guess | Run 100 iterations with first-order schemes, then switch to second-order |
| **Divergence after iterations** | Incorrect boundary conditions | Verify inlet turbulence: k > 0, ω > 0, nut >= 0 |

### 9.2 Mesh-Related Problems

| Issue | Diagnosis | Fix |
|-------|-----------|-----|
| **y+ too high/wrong** | Check `postProcessing/yPlus` | Re-mesh with adjusted `finalLayerThickness` |
| **High aspect ratio cells** | `checkMesh` reports > 1000 | Reduce `expansionRatio` in `addLayersControls` |
| **Negative volumes** | Mesh generation failure | Simplify STL geometry, fix surface defects |
| **Insufficient wake resolution** | Wake appears "blocky" | Add `refinementRegions` wake box with level 3-4 |

### 9.3 Force Coefficient Errors

| Error | Root Cause | Correction |
|-------|-----------|------------|
| **Cd negative** | Drag direction reversed | Check `dragDir` in function object (should be flow direction) |
| **Cd unrealistic (> 10)** | Incorrect reference area | Verify `Aref` matches frontal area in [m²] |
| **Cl = 0 for symmetric body** | Lift direction wrong | Confirm `liftDir` is perpendicular to flow and gravity |
| **Forces jump suddenly** | Time step too large (transient) | Reduce `maxCo` to 0.5 or lower Δt |

### 9.4 Turbulence Model Issues

| Problem | Model Behavior | Remedy |
|---------|----------------|--------|
| **No separation predicted** | k-ε too dissipative | Switch to k-ω SST or DES |
| **Separation too early** | y+ too low for wall functions | Either refine to y+ ≈ 1 (wall-resolved) or coarsen to y+ > 30 (wall functions) |
| **Residuals stuck at 10⁻³** | Turbulence residuals slow | Reduce `k` and `omega` relaxation to 0.5 |
| **k blows up (k > 10²)** | Inlet turbulence too high | Recalculate `k` from intensity: k = 1.5(U·I)² |

### 9.5 Boundary Condition Troubleshooting

**Symptom:** Backflow at outlet

**Diagnosis:**
```bash
# Check outlet velocity
paraFoAM -builtin
# Visualize U field at outlet patch
```

**Solutions:**
1. **Extend domain:** Increase downstream length to 20-30L
2. **Raise outlet pressure:** Use `fixedValue 1000` (Pa) instead of 0
3. **Use pressure outlet:**
```cpp
outlet
{
    type            pressureInletOutletVelocity;
    phi             phi;
    value           uniform (30 0 0);
}
```

---

## 10. Best Practices and Validation

### 10.1 Verification Checklist

**Before Running Simulation:**
- [ ] Domain sizing: 5-10L upstream, 15-20L downstream, < 3% blockage
- [ ] Mesh quality: `checkMesh` shows all OK (no severe errors)
- [ ] y+ check: Run 10 iterations, check `yPlus` function object
- [ ] Boundary conditions: All patches assigned, no undefined boundaries
- [ ] Initial conditions: k, ω, nut fields initialized
- [ ] Function objects: `forceCoeffs` configured with correct Aref, lRef

**During Simulation:**
- [ ] Monitor residuals: Should decrease monotonically (after initial iterations)
- [ ] Monitor forces: Cd and Cl should stabilize (Δ < 1% over 100 iterations)
- [ ] Check mass balance: `postProcessing/probes` for inlet/outlet mass flow

**Post-Simulation:**
- [ ] Wake deficit: U wake should recover to > 80% freestream at outlet
- [ ] Pressure drag vs friction drag: Sanity check for body shape
- [ ] Compare with literature: Cd for Ahmed body ≈ 0.25-0.30 (depending on slant angle)

### 10.2 Validation: Ahmed Body (Standard Test Case)

**Geometry:**
- Length: 1.044 m
- Height: 0.288 m
- Width: 0.389 m
- Slant angle: 25° (critical for separation)

**Expected Results (k-ω SST, y+ ≈ 1):**

| Slant Angle | Cd | Separation Location |
|-------------|-----|---------------------|
| 0° (square-back) | 0.30 | At roof rear edge |
| 25° | 0.25-0.28 | On slant surface |
| 35° | 0.24 | At slant top edge |

**Reference:**
- Ahmed, S.R., et al. (1984). "On the flow and aerodynamic forces on an Ahmed body". SAE Technical Paper.

### 10.3 Performance Optimization

**Mesh Size vs Accuracy:**

| Approach | Cells (approx.) | Cd Error | Runtime (100 cores) |
|----------|-----------------|----------|---------------------|
| Coarse (wall functions) | 2-5 million | ±5% | 1-2 hours |
| Medium (y+ ≈ 5) | 5-15 million | ±2% | 4-8 hours |
| Fine (y+ ≈ 1) | 15-50 million | ±1% | 12-48 hours |
| DES | 50-200 million | ±0.5% | 2-7 days |

**Parallel Scaling:**
- OpenFOAM scales efficiently to 100-1000 cores for RANS
- For DES: Use 200-500 cores (I/O becomes bottleneck at high core counts)

---

## Key Takeaways

### Domain Design
- **Minimum sizing:** 5-10L upstream, **15-20L downstream**, 5-10L sides/top
- **Blockage ratio:** Keep < 3% to avoid artificial acceleration
- **Wake region:** Extend refinement box from object rear to outlet

### Mesh Requirements
- **y+ guidelines:** Wall-resolved (y+ ≈ 1, 15-20 layers) or wall functions (y+ = 30-300, 5-10 layers)
- **First cell height:** ~0.01 mm for y+ = 1, ~1 mm for y+ = 100 (air, 30 m/s)
- **Wake refinement:** 2-3 levels finer than surface refinement

### Turbulence Modeling
- **Default choice:** k-ω SST (best balance of accuracy and cost)
- **Switch to DES:** When massive separation dominates (Cd varies > 10% in transient)
- **Avoid k-ε:** For flows with adverse pressure gradients (separation prediction poor)

### Force Calculation
- **Function objects:** Use `forceCoeffs` for real-time monitoring
- **Reference values:** Aref = frontal area, lRef = wheelbase (vehicles) or chord (airfoils)
- **Drag decomposition:** Pressure drag typically 70-90% for bluff bodies, friction drag dominates for streamlined shapes

### Convergence Criteria
- **Residuals:** Drop by 3-4 orders of magnitude (< 10⁻⁵)
- **Forces:** Stabilize to ΔCd < 0.001 over 100 iterations
- **Mass balance:** Inlet/outlet mass flow difference < 0.1%

### Common Pitfalls
1. **Insufficient downstream length** → Wake affects outlet, causing backflow
2. **Incorrect y+** → Wall functions fail, turbulence model inaccurate
3. **Wrong reference area** → Force coefficients meaningless
4. **First-order schemes** → Excessive numerical dissipation, delayed separation
5. **Over-relaxation** → Oscillating residuals, unstable convergence

---

## Concept Check

<details>
<summary><b>1. Why must downstream be longer than upstream?</b></summary>

**Answer:** The wake expands and requires space for pressure recovery before reaching the outlet. If the outlet is too close, the pressure boundary condition will artificially influence the flow around the object, causing incorrect separation and force predictions. Typically, wake regions require 3-4× more length than upstream to fully recover to freestream conditions.

**Key Point:** Downstream should be 15-20L vs 5-10L upstream to allow wake development and pressure recovery.
</details>

<details>
<summary><b>2. When should you use k-ω SST vs k-ε turbulence models?</b></summary>

**Answer:** 
- **k-ω SST:** Use for flows with adverse pressure gradients and separation (automotive, bluff bodies). It combines k-ω near walls (accurate separation prediction) with k-ε in freestream (robustness).
- **k-ε:** Use for free shear flows without strong pressure gradients (jets, mixing layers). It over-predicts eddy viscosity in adverse pressure gradients, delaying separation.

**Rule of Thumb:** Default to k-ω SST for external aerodynamics; only use k-ε for quick iterations or free-stream dominated flows.
</details>

<details>
<summary><b>3. For an Ahmed body at 30 m/s with 0.3 m² frontal area, if the measured drag force is 45 N, what is Cd?</b></summary>

**Answer:** 

$$C_D = \frac{F_D}{0.5 \rho U_\infty^2 A} = \frac{45}{0.5 \times 1.225 \times 30^2 \times 0.3}$$

$$C_D = \frac{45}{0.5 \times 1.225 \times 900 \times 0.3} = \frac{45}{165.375} \approx 0.272$$

**Check:** For Ahmed body, Cd ≈ 0.25-0.30, so this is reasonable.
</details>

<details>
<summary><b>4. Your simulation shows Cd = 0.45 for a passenger car (expected: 0.28). What are the first 3 things to check?</b></summary>

**Answer:**
1. **Reference area:** Is Aref correctly set to frontal area? (Common mistake: using total surface area instead)
2. **y+ values:** Are they too high for the wall treatment? (k-ω SST with wall functions needs y+ > 30; if y+ ≈ 1 without wall-resolved mesh, results are unreliable)
3. **Domain blockage:** Is the object too large relative to the domain? (Blockage > 3% causes artificial acceleration, increasing drag)

**Next Steps:** Verify `Aref` in function object, run `yPlus` check, measure blockage ratio.
</details>

<details>
<summary><b>5. Explain the physical mechanism of vortex shedding behind a cylinder.</b></summary>

**Answer:**

Vortex shedding occurs due to **flow instability** in the wake:
1. **Boundary layer separation** occurs at both sides of the cylinder (≈ 80-85° from stagnation)
2. **Shear layers** roll up into discrete vortices due to Kelvin-Helmholtz instability
3. **Alternate shedding** creates oscillating pressure field (low pressure on vortex-generating side)
4. **Strouhal number** (St ≈ 0.2) relates shedding frequency to velocity and diameter:1$f_s = St \cdot U_\infty / D$

**Practical Impact:** Vortex shedding causes oscillating lift and drag forces, leading to vibration (e.g., bridge resonance, telephone wire "singing"). In OpenFOAM, resolve this with transient simulations (pimpleFoam) and Δt small enough to capture the shedding frequency.

**Time Step Requirement:** For accurate shedding, need > 20 time steps per period: Δt < 1/(20·f_s)
</details>

<details>
<summary><b>6. Troubleshooting Scenario: Your residuals plateau at 10⁻³, and Cd oscillates between 0.28 and 0.31. What's wrong?</b></summary>

**Answer:**

**Diagnosis:** Unsteady flow causing transient behavior in steady-state solver

**Root Causes (in order of likelihood):**
1. **Vortex shedding:** The flow is inherently unsteady (e.g., strong separation, bluff body). steady-state `simpleFoam` cannot converge because the solution oscillates between shedding states.

2. **Numerical instability:** Under-relaxation factors too high, causing solution oscillation

3. **Mesh issues:** High aspect ratio cells or poor quality causing local instability

**Solutions:**
- **Switch to transient solver:** Run `pimpleFoam` with appropriate Δt to resolve shedding
- **Reduce relaxation:** Lower `p` to 0.2, `U` to 0.5 in `SIMPLE` section
- **Check mesh:** Run `checkMesh` and fix non-orthogonal cells (> 70°)

**Verification:** Monitor force coefficients over time. If periodic oscillation persists with period matching Strouhal shedding frequency, use transient solver.
</details>

---

## Related Documents

- **Next Module:** [02_Internal_Flow_and_Piping.md](02_Internal_Flow_and_Piping.md) - Internal aerodynamics, pipe flow, pressure drop calculations
- **Turbulence Modeling:** [../03_TURBULENCE_MODELING/00_Overview.md](../03_TURBULENCE_MODELING/00_Overview.md) - Detailed turbulence model theory, y+ calculation, wall treatment
- **Heat Transfer:** [../04_HEAT_TRANSFER/00_Overview.md](../04_HEAT_TRANSFER/00_Overview.md) - Conjugate heat transfer for exhaust systems, brake cooling
- **Mesh Quality:** [../../MODULE_02_MESHING_AND_CASE_SETUP/CONTENT/05_MESH_QUALITY_AND_MANIPULATION/01_Mesh_Quality_Criteria.md](../../MODULE_02_MESHING_AND_CASE_SETUP/CONTENT/05_MESH_QUALITY_AND_MANIPULATION/01_Mesh_Quality_Criteria.md) - Mesh diagnostics, y+ verification
- **Function Objects:** [../../MODULE_02_MESHING_AND_CASE_SETUP/CONTENT/06_RUNTIME_POST_PROCESSING/01_Introduction_to_FunctionObjects.md](../../MODULE_02_MESHING_AND_CASE_SETUP/CONTENT/06_RUNTIME_POST_PROCESSING/01_Introduction_to_FunctionObjects.md) - Advanced force/moment monitoring

---

**Module Status:** ✅ Complete with Learning Objectives, 3W Framework, Key Takeaways, and Troubleshooting Scenarios

**Cross-References:** Turbulence Modeling (Module 03), Mesh Quality (Module 02), Function Objects (Module 02)