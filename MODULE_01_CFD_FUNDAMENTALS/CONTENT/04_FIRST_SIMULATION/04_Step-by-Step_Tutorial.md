# Step-by-Step Tutorial: Running Your First OpenFOAM Simulation

> **Hands-on Tutorial**: Execute a complete lid-driven cavity CFD simulation from start to finish

---

## Learning Objectives

**Students will be able to:**
- Execute a complete OpenFOAM simulation workflow from mesh generation to visualization
- Navigate and interpret OpenFOAM case directory structure
- Generate and validate mesh quality using standard OpenFOAM utilities
- Configure and run an incompressible laminar flow simulation
- Visualize simulation results using ParaView
- Extract quantitative data for validation and analysis

---

## Overview

**WHAT:** This tutorial provides a comprehensive, hands-on walkthrough of running a complete lid-driven cavity simulation using OpenFOAM's `icoFoam` solver.

**WHY:** Practical experience with a complete simulation workflow builds intuition for CFD concepts and reinforces theoretical knowledge through actual implementation. The lid-driven cavity is a classic benchmark problem that exhibits rich fluid dynamics while remaining computationally tractable for beginners.

**HOW:** You will execute each step of the simulation workflow—mesh generation, boundary condition setup, solver configuration, execution, and post-processing—with detailed explanations of why each step matters and how to verify correct execution at each stage.

---

## Prerequisites

**Before starting this tutorial, ensure you have:**
- ✅ OpenFOAM properly installed and sourced
- ✅ Basic understanding of the lid-driven cavity problem (covered in `03_The_Lid-Driven_Cavity_Problem.md:001`)
- ✅ Familiarity with the OpenFOAM workflow (covered in `02_The_Workflow.md:001`)
- ✅ A terminal with write permissions in your working directory

---

## Case Preparation

### Step 0: Copy Tutorial Case

**WHY:** Starting from a verified, working case allows you to focus on understanding the workflow rather than debugging case setup issues.

```bash
# Copy tutorial case to current directory
cp -r $FOAM_TUTORIALS/incompressible/icoFoam/cavity/cavity .
cd cavity
```

**Verification:**
```bash
ls -la
# Expected: 0/  constant/  system/
```

---

## Phase 1: Mesh Generation and Validation

### Step 1: Examine Case Structure

**WHY:** Understanding the standard OpenFOAM directory structure (`0/`, `constant/`, `system/`) is essential for organizing and modifying any CFD case.

```bash
tree -L 1
```

**Expected structure:**
```
.
├── 0/           # Initial and boundary conditions
├── constant/    # Mesh and physical properties
└── system/      # Solver and numerical scheme settings
```

---

### Step 2: Review Mesh Definition

**WHY:** The mesh definition controls geometry, resolution, and boundary identification. Understanding this file enables you to modify geometry and create custom cases.

```bash
cat constant/polyMesh/blockMeshDict
```

**Key components:**

**Vertices** — define corner points of the computational domain:
```cpp
vertices
(
    (0 0 0)      // vertex 0 - origin
    (1 0 0)      // vertex 1 
    (1 1 0)      // vertex 2
    (0 1 0)      // vertex 3
    (0 0 0.1)    // vertex 4 - elevated in z
    (1 0 0.1)    // vertex 5
    (1 1 0.1)    // vertex 6
    (0 1 0.1)    // vertex 7
);
```

**Blocks** — define how vertices connect to form cells:
```cpp
blocks
(
    hex (0 1 2 3 4 5 6 7) (20 20 1) simpleGrading (1 1 1);
    //   ^^^^^^^^^^^^^^^   ^^^^^^^   ^^^^^^^^^^^^^^^^
    //   vertex list        cells     grading (1 = uniform)
    //                      x y z
);
```

**Boundary patches** — define boundaries for boundary conditions:
```cpp
boundary
(
    movingWall    // Top wall (y=1) — moving lid
    {
        type wall;
        faces ((3 7 6 2));
    }
    fixedWalls   // Bottom and side walls — stationary
    {
        type wall;
        faces
        (
            (0 4 7 3)  // front (x=0)
            (2 6 5 1)  // right (x=1)
            (1 5 4 0)  // bottom (y=0)
        );
    }
    frontAndBack // Front and back planes — 2D simulation
    {
        type empty;  // Special BC for 2D: ignore z-direction
        faces
        (
            (0 3 2 1)  // back (z=0)
            (4 5 6 7)  // front (z=0.1)
        );
    }
);
```

**💡 KEY INSIGHT:** The `empty` boundary type indicates a 2D simulation—only one cell exists in the z-direction, and the solver ignores momentum equations in that direction.

---

### Step 3: Generate Mesh

**WHY:** The discretized mesh is the foundation of CFD simulations—all equations are solved on this mesh.

```bash
blockMesh
```

**Expected output:**
```
Creating block mesh from "constant/polyMesh/blockMeshDict"
Creating topology blocks
Creating block mesh topology
...
Writing polyMesh
```

<details>
<summary><b>🔧 TROUBLESHOOTING: blockMesh errors</b></summary>

**Common errors:**
- **"number of vertices does not match"**: Check that vertex count in `blocks` matches `vertices` list
- **"face is not convex"**: Vertices defining a face must be in the same plane
- **"patch is not defined"**: All faces in `boundary` section must reference valid patch names

**Quick fix:**
```bash
# Check for syntax errors
blockMesh -help
# Run with detailed output
blockMesh > log.blockMesh 2>&1
less log.blockMesh
```
</details>

---

### Step 4: Validate Mesh Quality

**WHY:** Mesh quality directly affects solution accuracy and stability. Validating the mesh before running the solver prevents wasted computation time.

```bash
checkMesh
```

**Expected output:**
```
Mesh stats
    points:           882
    internal points:  0
    faces:            1640
    internal faces:   760
    cells:            400
    faces per cell:   6
    boundary patches: 3
    ---
Mesh OK.
```

**Key metrics to verify:**
- ✅ **Mesh OK** — no critical issues
- ✅ **Non-orthogonality** < 70° (for laminar flow)
- ✅ **Aspect ratio** < 1000 (prevents numerical errors)
- ✅ **Determinant** > 0.01 (measures cell skewness)

<details>
<summary><b>🔧 TROUBLESHOOTING: Mesh quality issues</b></summary>

**If `checkMesh` reports warnings:**
- **High non-orthogonality (>70°)**: Consider `nNonOrthogonalCorrectors` in `fvSolution`
- **High aspect ratio**: Refine mesh or adjust cell grading
- **Failed cells**: Re-examine `blockMeshDict` geometry definition

**Re-run after corrections:**
```bash
blockMesh
checkMesh
```
</details>

---

## Phase 2: Physics and Boundary Conditions

### Step 5: Examine Boundary Conditions

**WHY:** Boundary conditions define the physical problem being solved. Incorrect BCs produce physically meaningless results, regardless of solver accuracy.

**Velocity (`0/U`):**
```bash
cat 0/U
```

```cpp
dimensions      [0 1 -1 0 0 0 0];      // m/s
internalField   uniform (0 0 0);       // Initial velocity: fluid at rest

boundaryField
{
    movingWall
    {
        type            fixedValue;    // Dirichlet BC
        value           uniform (1 0 0); // Lid velocity: 1 m/s in x-direction
    }
    fixedWalls
    {
        type            noSlip;         // No-slip condition (U=0 at walls)
    }
    frontAndBack
    {
        type            empty;          // 2D simulation — ignore z-direction
    }
}
```

**Pressure (`0/p`):**
```cpp
dimensions      [0 2 -2 0 0 0 0];      // m²/s² (kinematic pressure)
internalField   uniform 0;             // Initial guess

boundaryField
{
    movingWall
    {
        type            zeroGradient;   // Neumann BC: ∂p/∂n = 0
    }                                     // (No pressure condition specified at walls)
    fixedWalls
    {
        type            zeroGradient;   // ∂p/∂n = 0 at all walls
    }
    frontAndBack
    {
        type            empty;
    }
}
```

**💡 KEY INSIGHT:** Pressure uses `zeroGradient` at walls because the incompressible flow solver determines pressure from the velocity field's continuity constraint, not from boundary conditions. A reference pressure is fixed via `pRefCell` in `system/fvSolution`.

---

### Step 6: Configure Fluid Properties

**WHY:** Fluid properties (kinematic viscosity) determine the Reynolds number and flow regime. Correct properties ensure physical realism.

```bash
cat constant/transportProperties
```

```cpp
transportModel  Newtonian;              // Newtonian fluid (constant viscosity)
nu              [0 2 -1 0 0 0 0] 0.01; // Kinematic viscosity: 0.01 m²/s
```

**Calculate Reynolds Number:**
$$Re = \frac{UL}{\nu} = \frac{(1\ \text{m/s})(1\ \text{m})}{0.01\ \text{m}^2/\text{s}} = 100$$

**Interpretation:**
- **Re = 100**: Laminar flow regime
- Steady-state solution achievable
- No turbulence modeling required

**💡 QUICK VARIATION:** Change `nu` to `0.001` for Re=1000 (transitional regime) or `0.1` for Re=10 (highly viscous, creeping flow).

---

## Phase 3: Solver Configuration

### Step 7: Configure Solver Control

**WHY:** Control dictionaries determine simulation duration, time stepping, output frequency, and numerical schemes—all critical for obtaining accurate, stable solutions.

**Time control (`system/controlDict`):**
```cpp
application     icoFoam;               // Incompressible laminar Navier-Stokes solver
startFrom       startTime;             // Begin from initial conditions in 0/
startTime       0;                     // Starting time
stopAt          endTime;               // Stop when endTime is reached
endTime         0.5;                   // Final simulation time (s)
deltaT          0.005;                 // Time step size (s)
writeControl    timeStep;              // Control output frequency by time step
writeInterval   20;                    // Write results every 20 steps (every 0.1 s)
```

**Numerical schemes (`system/fvSchemes`):**
```cpp
ddtSchemes
{
    default         Euler;              // First-order transient scheme (stable)
}

gradSchemes
{
    default         Gauss linear;       // Central differencing: 2nd order accurate
}

divSchemes
{
    default         none;               // Require explicit specification
    div(phi,U)      Gauss linear;      // Convection term: 2nd order central differencing
    // ✅ ACCURATE for Re ≤ 400 (stable laminar flow)
    
    // ⚠️ FOR HIGHER Re (unstable with central differencing):
    // div(phi,U) Gauss linearUpwind grad(U);  // 2nd order upwind: more stable
    // div(phi,U) Gauss upwind;                 // 1st order upwind: very stable, diffusive
}

laplacianSchemes
{
    default         Gauss linear orthogonal; // Diffusion term: 2nd order
}
```

**💡 SCHEME SELECTION GUIDE:**
- **Gauss linear**: Most accurate for low-to-moderate Re (≤400)
- **Gauss linearUpwind**: Good balance of accuracy and stability (Re 400-2000)
- **Gauss upwind**: Most stable, most diffusive (use only if diverging)

**Linear solvers (`system/fvSolution`):**
```cpp
solvers
{
    p                                   // Pressure Poisson equation
    {
        solver          PCG;             // Preconditioned Conjugate Gradient
        preconditioner  DIC;             // Diagonal Incomplete Cholesky
        tolerance       1e-06;           // Absolute tolerance
        relTol          0.05;            // Relative tolerance (5% of initial residual)
    }

    U                                   // Momentum equation
    {
        solver          smoothSolver;    // Iterative smoother
        smoother        symGaussSeidel;  // Symmetric Gauss-Seidel
        tolerance       1e-05;           // Absolute tolerance
        relTol          0;               // Solve to tight tolerance (no early exit)
    }
}

PISO                                // Pressure-Implicit with Splitting of Operators
{
    nCorrectors     2;                // Number of pressure corrections per time step
    nNonOrthogonalCorrectors 0;       // For non-orthogonal meshes (0 for this case)
    pRefCell        0;                // Cell index where pressure is fixed
    pRefValue       0;                // Reference pressure value (Pa)
}
```

**💡 KEY INSIGHT:** The `pRefCell` and `pRefValue` entries are **essential** for incompressible flow because pressure is only determined up to an arbitrary constant. These entries fix that constant to ensure a well-posed mathematical problem.

---

## Phase 4: Simulation Execution

### Step 8: Run Simulation

**WHY:** Executing the solver iteratively advances the solution in time, solving the discretized Navier-Stokes equations at each step.

```bash
# Run solver in background with logging
icoFoam > log.icoFoam 2>&1 &

# Monitor real-time output
tail -f log.icoFoam
```

**Expected output pattern:**
```
Time = 0.05

Courant Number mean: 0.001234 max: 0.045678
diagonal:  Solving for rho, Initial residual = 0, Final residual = 0, No Iterations 0
PIMPLE: iteration 1
smoothSolver:  Solving for Ux, Initial residual = 0.012345, Final residual = 3.456e-06, No Iterations 4
smoothSolver:  Solving for Uy, Initial residual = 0.023456, Final residual = 5.678e-06, No Iterations 4
PCG:  Solving for p, Initial residual = 0.123456, Final residual = 0.0061728, No Iterations 12
time step continuity errors : sum local = 4.567e-07, global = -2.345e-19, cumulative = -2.345e-19
PIMPLE: iteration 2
...
ExecutionTime = 1.23 s  ClockTime = 2.45 s

Time = 0.1

...
```

**Key metrics to monitor:**
- ✅ **Courant Number**: < 1.0 for stability (typically < 0.5 for accuracy)
- ✅ **Initial residuals**: Should decrease over time
- ✅ **Continuity errors**: Should be very small (< 1e-5)

<details>
<summary><b>🔧 TROUBLESHOOTING: Divergence or instability</b></summary>

**Symptoms:**
- Residuals increasing or not decreasing
- Courant number > 1.0
- "Maximum number of iterations exceeded" warnings

**Solutions:**
1. **Reduce time step**: Edit `controlDict`: `deltaT 0.001;` (half of current)
2. **Change divergence scheme**: In `fvSchemes`, use `Gauss upwind` instead of `Gauss linear`
3. **Add non-orthogonal correctors**: In `fvSolution`: `nNonOrthogonalCorrectors 1;`

**Resume from last time step:**
```bash
# Edit controlDict, then:
icoFoam >> log.icoFoam 2>&1 &
```
</details>

**Check residuals history:**
```bash
# Extract pressure residuals
grep "Solving for p" log.icoFoam | tail -20

# Extract Courant numbers
grep "Courant Number" log.icoFoam | tail -20
```

**💡 INTERMEDIATE VALIDATION:** Residuals should decrease monotonically. If residuals plateau or increase, the simulation may be diverging—refer to troubleshooting above.

---

### Step 9: Verify Simulation Completion

**WHY:** Confirming that the simulation completed successfully ensures that results are physically meaningful and ready for analysis.

```bash
# Check final time directory
ls -d 0.*

# Should include: 0.1  0.2  0.3  0.4  0.5

# Check final residuals
tail -50 log.icoFoam | grep "Solving for"
```

**Expected final state:**
- ✅ Time directories up to `endTime` (0.5) exist
- ✅ Final residuals < 1e-5 for U and < 1e-6 for p
- ✅ No error messages in log file

---

## Phase 5: Visualization and Analysis

### Step 10: Visualize Results in ParaView

**WHY:** Visualization transforms numerical data into intuitive flow patterns, enabling qualitative assessment of solution correctness and physical insight.

```bash
paraFoam
```

**ParaView workflow:**

**1. Load and apply mesh:**
- Click **Apply** (green checkmark) → mesh appears
- Use **Outline** or **Surface with Edges** representation

**2. Visualize velocity magnitude:**
- **Color by** → **U** → **Magnitude**
- Adjust color scale: **Rescale to Custom Range** (0 to 1 m/s)
- **Representation**: **Surface** (smooth contours)

**3. Display velocity vectors:**
- **Add filter** → **Glyph**
- Set **Glyph Type** to **Arrow**
- **Scale Mode**: **Scale by magnitude**
- **Color by** → **U** → **Magnitude**
- Adjust **Scale Factor** (try 0.05-0.1)

**4. Create streamlines:**
- **Add filter** → **Stream Tracer**
- Set **Seed Type** to **High Resolution Line Source**
- Position seed line in center of vortex
- **Color by** → **U** → **vorticity** (optional)

**5. Animate flow evolution:**
- Enable **Animation View** (filmstrip icon)
- Click **Play** to animate time steps 0 → 0.5

**💡 VISUALIZATION BEST PRACTICES:**
- Use **Color Maps**: **Cool to Warm** or **Jet** for velocity magnitude
- **Export screenshots**: **File** → **Export Screenshot...** or `Ctrl+E` / `Cmd+E`
- **Save state**: **File** → **Save State** (reproducible visualization setup)

<details>
<summary><b>🔧 TROUBLESHOOTING: ParaView issues</b></summary>

**No mesh appears after applying:**
- Check that simulation completed successfully
- Verify time directories contain result files: `ls 0.5/`

**ParaView crashes or hangs:**
- Large time steps can cause memory issues — try loading fewer time steps
- Use **paraFoam -builtin** for built-in reader (older OpenFOAM versions)

**Vectors too dense or too sparse:**
- In Glyph filter, adjust **Maximum Number of Points** or use **Masking**
</details>

---

### Step 11: Extract Quantitative Data for Validation

**WHY:** Quantitative comparison with benchmark data (e.g., Ghia et al., 1982) validates simulation accuracy and builds confidence in OpenFOAM results.

**Add sampling functions to `system/controlDict`:**

```cpp
functions
{
    // === Time-averaged statistics ===
    fieldAverage1
    {
        type            fieldAverage;
        libs            (fieldFunctionObjects);
        writeControl    writeTime;
        
        fields
        (
            U 
            { 
                mean on;           // Compute time-average ⟨U⟩
                prime2Mean on;     // Compute fluctuations U'U'
                base time;         // Start averaging from t=0
            }
            p 
            { 
                mean on; 
                prime2Mean on; 
                base time; 
            }
        );
    }
    
    // === Line sampling (centerline profiles) ===
    sample1
    {
        type            sets;
        libs            (sampling);
        writeControl    writeTime;
        
        interpolationScheme cellPoint;     // Bilinear interpolation
        setFormat       raw;                // Plain text output
        
        sets
        (
            centerlineY
            {
                type    uniform;            // Uniformly-spaced sampling
                axis    x;                  // Sample along x-axis
                start   (0 0.5 0.05);       // Start point (x=0, y=0.5, z=center)
                end     (1 0.5 0.05);       // End point (x=1, y=0.5, z=center)
                nPoints 100;                // Number of sample points
            }
            centerlineX
            {
                type    uniform;
                axis    y;
                start   (0.5 0 0.05);       // Vertical line at x=0.5
                end     (0.5 1 0.05);
                nPoints 100;
            }
        );
        
        fields (U p);                      // Sample velocity and pressure
    }
}
```

**Extract data:**

**Option 1: Re-run simulation with functions enabled**
```bash
# Re-run (functions auto-execute)
icoFoam > log.icoFoam 2>&1 &
```

**Option 2: Post-process existing results (faster)**
```bash
# Extract data from saved time directories
postProcess -func sample1 > log.postProcess 2>&1 &
```

**Output location:**
```bash
# Sampled data
ls sets/
# centerlineX/  centerlineY/

# Averaged fields
ls 0.5/
# UMean  pMean UPrime2Mean  pPrime2Mean
```

**Plotting and validation:**
```bash
# View sampled data
cat sets/centerlineX/0.5/UMean_xy.csv
```

**💡 REFERENCE:** Compare your u-velocity profile along the vertical centerline (x=0.5) with Ghia et al. (1982) benchmark data for Re=100. Maximum error should be < 2% for a well-resolved simulation.

<details>
<summary><b>📚 See also: Detailed post-processing guide</b></summary>

For advanced sampling techniques (surfaces, clouds, probes) and additional function objects, see **[02_The_Workflow.md:500](02_The_Workflow.md:500)** for a comprehensive post-processing reference.
</details>

---

## Parameter Variations and Experiments

**WHY:** Systematic parameter variations build intuition for how physical properties and numerical settings affect flow behavior and solution quality.

### Experiment 1: Change Reynolds Number

**Objective:** Understand how viscosity affects flow features

**Procedure:**
```bash
# Edit kinematic viscosity
sed -i 's/nu.*/nu [0 2 -1 0 0 0 0] 0.001;/' constant/transportProperties
```

**New Reynolds number:**
$$Re = \frac{1 \times 1}{0.001} = 1000$$

**Expected changes:**
- ✅ Primary vortex shifts toward center
- ✅ Secondary corner vortices appear (bottom-left and bottom-right)
- ✅ Longer physical time to reach steady state
- ⚠️ May require smaller `deltaT` (try 0.001) and finer mesh

**Re-run:**
```bash
# Clean previous results
foamCleanTutorials

# Regenerate mesh (if changed)
blockMesh

# Run simulation
icoFoam > log.icoRe1000 2>&1 &
```

---

### Experiment 2: Refine Mesh Resolution

**Objective:** Assess grid convergence and discretization error

**Procedure:**
```bash
# Edit blockMeshDict
# Change: hex (0 1 2 3 4 5 6 7) (20 20 1) ...
# To:     hex (0 1 2 3 4 5 6 7) (40 40 1) ...
```

**Expected changes:**
- ✅ Improved accuracy (lower discretization error)
- ✅ Better resolution of velocity gradients near walls
- ⚠️ Increased computational cost (~4x more cells)
- ⚠️ May require smaller `deltaT` for stability

**Re-run:**
```bash
# Regenerate mesh
blockMesh

# Check mesh quality
checkMesh

# Run simulation
icoFoam > log.icoFine 2>&1 &
```

**💡 GRID CONVERGENCE STUDY:** Repeat for meshes (20×20), (40×40), and (80×80). Compare u-velocity profiles at x=0.5. When profiles overlap visually, the solution is grid-independent.

---

### Experiment 3: Extend Simulation Time

**Objective:** Verify steady-state convergence

**Procedure:**
```bash
# Edit controlDict
sed -i 's/endTime.*/endTime 2.0;/' system/controlDict
```

**Verification:**
```bash
# Compare velocity fields at different times
diff 0.5/U 1.0/U  # Should be small differences
diff 1.0/U 2.0/U  # Should be nearly identical (steady state)
```

**💡 STEADY-STATE CHECK:** If `U` fields at t=1.0 and t=2.0 are nearly identical (max difference < 1e-5), the flow has reached steady state.

---

## Troubleshooting Guide

### Common Issues and Solutions

| **Problem** | **Likely Cause** | **Solution** | **Reference** |
|-------------|------------------|--------------|---------------|
| `blockMesh: Fatal error` | Syntax error in `blockMeshDict` | Check vertices, blocks, and boundary definitions | `02_The_Workflow.md:300` |
| `Mesh not OK` from `checkMesh` | Invalid geometry or high aspect ratio | Re-examine `blockMeshDict` vertices and grading | Step 4 above |
| **Diverging residuals** | Time step too large or unstable scheme | Reduce `deltaT` or change `div(phi,U)` to `Gauss upwind` | Step 8 troubleshooting |
| **High Courant number** | Velocity field causing CFL violation | Reduce `deltaT`: try 0.001 or 0.0005 | Step 8 monitoring |
| **ParaView crash** | Memory issues with many time steps | Use `paraFoam -builtin` or load fewer time steps | Step 10 troubleshooting |
| **No vortex formation** | Incorrect boundary conditions | Verify `movingWall` has `fixedValue (1 0 0)` in `0/U` | Step 5 BCs |
| **Pressure drifts** | Missing `pRefCell` in `fvSolution` | Add `pRefCell 0; pRefValue 0;` to `PISO` section | Step 7 solver config |

---

## Concept Check

<details>
<summary><b>1. Why is the <code>empty</code> boundary type used for frontAndBack?</b></summary>

**Answer:** The `empty` type indicates a 2D simulation. The mesh has only one cell in the z-direction, and the `empty` boundary condition tells the solver to ignore momentum equations in that direction, effectively reducing the 3D solver to 2D. This is more efficient than a full 3D simulation while maintaining accuracy for planar flows.

**Key concept:** 2D simulations in OpenFOAM are actually thin 3D domains with `empty` boundaries on the front and back planes.
</details>

<details>
<summary><b>2. What does <code>pRefCell 0; pRefValue 0;</code> mean, and why is it necessary?</b></summary>

**Answer:** This fixes the pressure at cell index 0 to a reference value of 0 Pa. This is **necessary** for incompressible flow because the pressure Poisson equation only determines pressure up to an arbitrary constant—without a reference pressure, the system is mathematically ill-posed and the solution will drift or diverge.

**Key concept:** Incompressible solvers require a pressure reference to ensure a well-posed mathematical problem.
</details>

<details>
<summary><b>3. Why is <code>Gauss linear</code> used for <code>div(phi,U)</code>, and when should you change it?</b></summary>

**Answer:** `Gauss linear` is a second-order central differencing scheme that is most accurate for laminar flows (Re ≤ ~400). However, it can become unstable at higher Reynolds numbers or with coarse meshes. If residuals diverge or Courant numbers spike, switch to:
- `Gauss linearUpwind` — More stable, still 2nd order (best for moderate Re)
- `Gauss upwind` — Most stable, 1st order (most diffusive, use as last resort)

**Key concept:** Scheme selection balances accuracy and stability—always start with `Gauss linear` and only downgrade if necessary.
</details>

<details>
<summary><b>4. What is the purpose of the <code>sample1</code> function object?</b></summary>

**Answer:** The `sample1` function object extracts field data along user-defined lines during or after the simulation. This enables quantitative validation against benchmark data (e.g., Ghia et al., 1982) and comparison between different simulations. The output is written to `sets/` directories as CSV files for plotting and analysis.

**Key concept:** Function objects automate data extraction, eliminating manual post-processing and ensuring reproducible analysis.
</details>

---

## Key Takeaways

### Core Concepts

✅ **OpenFOAM workflow follows a systematic process**: mesh → BCs → properties → solver config → execution → post-processing. Each step builds on the previous one.

✅ **Mesh quality is foundational**: Always validate with `checkMesh` before running the solver. Poor-quality meshes produce inaccurate or divergent solutions regardless of solver settings.

✅ **Boundary conditions encode the physics**: Incorrect BCs produce meaningless results. Verify that BCs match the physical problem being solved (e.g., moving lid for cavity flow).

✅ **Scheme selection balances accuracy and stability**: Second-order schemes (`Gauss linear`) are most accurate but may require smaller time steps or finer meshes for stability.

✅ **Residual monitoring is essential**: Decreasing residuals indicate convergence. Plateauing or increasing residuals signal divergence—stop and diagnose.

### Practical Skills

✅ **Standard OpenFOAM directory structure**: `0/` (initial/boundary conditions), `constant/` (mesh & properties), `system/` (solver & scheme settings)

✅ **Mesh generation with blockMesh**: Vertices → blocks → boundary patches. Understanding this file enables custom geometry creation.

✅ **Solver control dictionaries**: `controlDict` (time stepping), `fvSchemes` (discretization), `fvSolution` (linear solvers & algorithm settings)

✅ **Visualization workflow**: ParaView enables qualitative assessment (contours, vectors, streamlines) for solution validation.

✅ **Data extraction for validation**: Function objects (`sample`, `fieldAverage`) automate quantitative comparison with benchmarks.

### Next Steps

- **Compare with benchmark data**: Validate your Re=100 results against Ghia et al. (1982) reference values
- **Explore higher Reynolds numbers**: Try Re=400, 1000, and observe secondary vortex formation
- **Grid convergence study**: Run meshes at (20×20), (40×40), (80×80) and assess discretization error
- **Advanced visualization**: Experiment with vorticity contours, Q-criterion, and iso-surfaces in ParaView

---

## Related Documentation

### Within This Module

- **Previous:** [03_The_Lid-Driven_Cavity_Problem.md](03_The_Lid-Driven_Cavity_Problem.md) — Mathematical formulation and analytical background
- **Previous:** [02_The_Workflow.md](02_The_Workflow.md) — Comprehensive workflow reference with detailed post-processing
- **Next:** [05_Expected_Results.md](05_Expected_Results.md) — Benchmark results and quantitative validation

### External Resources

- **OpenFOAM User Guide:** [https://cfd.direct/openfoam/user-guide/](https://cfd.direct/openfoam/user-guide/) — Official documentation
- **OpenFOAM Wiki:** [https://openfoamwiki.net/](https://openfoamwiki.net/) — Community tutorials and tips
- **ParaView Guide:** [https://www.paraview.org/docs/](https://www.paraview.org/docs/) — Visualization techniques
- **Ghia et al. (1982):** "High-Re solutions for incompressible flow" — Benchmark data for cavity flow

---

**Last updated:** 2025-12-30  
**OpenFOAM version:** v9+ (compatible with v2212, v2306, v2312)  
**Corresponding author:** [Your Name] — [email]