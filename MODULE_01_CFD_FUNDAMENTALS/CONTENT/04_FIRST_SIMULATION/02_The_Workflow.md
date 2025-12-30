# CFD Simulation Workflow

## Learning Objectives

After completing this module, you will be able to:
- Identify the three main stages of CFD simulation workflow (Pre-processing, Solving, Post-processing)
- Configure boundary conditions, transport properties, and solver settings for OpenFOAM simulations
- Set up and run quantitative data sampling using probes and sample lines
- Diagnose and resolve common convergence issues during simulation

---

## WHAT: The Three-Stage CFD Workflow, WHY: Understanding Workflow Enables Efficient Debugging, HOW: By Mastering Each Stage's Tools and Files

A CFD simulation consists of three distinct stages, each using different tools and file types. Understanding this separation is critical for efficient debugging:

- **Different tools** are used at each stage
- **Debugging becomes targeted** — you know exactly which stage to investigate when issues arise
- **Workflow efficiency increases** — you can navigate between stages confidently

> **💡 Key Insight:** If a simulation fails, you can immediately identify whether the problem is in the mesh (Pre-processing), solver configuration (Solving), or analysis setup (Post-processing).

---

## 1. Pre-Processing

### 1.1 WHAT: Geometry and Mesh Generation, WHY: Quality Mesh Determines Solution Accuracy, HOW: Using blockMesh for Structured Grids

**blockMesh** creates structured hexahedral meshes from block definitions:

```cpp
// constant/polyMesh/blockMeshDict
vertices
(
    (0 0 0)
    (1 0 0)
    (1 1 0)
    (0 1 0)
    (0 0 0.1)
    (1 0 0.1)
    (1 1 0.1)
    (0 1 0.1)
);

blocks
(
    hex (0 1 2 3 4 5 6 7) (20 20 1) simpleGrading (1 1 1)
);

boundary
(
    movingWall  { type wall; faces ((3 7 6 2)); }
    fixedWalls  { type wall; faces ((0 4 7 3) (2 6 5 1) (1 5 4 0)); }
    frontAndBack { type empty; faces ((0 3 2 1) (4 5 6 7)); }
);
```

**Mesh Quality Verification:**

```bash
checkMesh
```

| Metric | Good | Acceptable | Bad |
|--------|------|------------|-----|
| Non-orthogonality | < 50° | 50-70° | > 70° |
| Skewness | < 2 | 2-4 | > 4 |
| Aspect ratio | < 10 | 10-100 | > 100 |

> **📖 See Also:** For detailed boundary condition explanations, see [05_Common_Boundary_Conditions_in_OpenFOAM.md](../../03_BOUNDARY_CONDITIONS/05_Common_Boundary_Conditions_in_OpenFOAM.md)

### 1.2 WHAT: Boundary Condition Specification, WHY: BCs Define the Physical Problem, HOW: Through Field Files in 0/ Directory

**Velocity (0/U):**

```cpp
dimensions      [0 1 -1 0 0 0 0];
internalField   uniform (0 0 0);

boundaryField
{
    movingWall
    {
        type    fixedValue;
        value   uniform (1 0 0);
    }
    fixedWalls
    {
        type    noSlip;
    }
    frontAndBack
    {
        type    empty;
    }
}
```

**Pressure (0/p):**

```cpp
dimensions      [0 2 -2 0 0 0 0];
internalField   uniform 0;

boundaryField
{
    movingWall   { type zeroGradient; }
    fixedWalls   { type zeroGradient; }
    frontAndBack { type empty; }
}
```

### 1.3 WHAT: Fluid Properties, WHY: Define Reynolds Number and Flow Regime, HOW: Through constant/transportProperties

```cpp
// constant/transportProperties
transportModel  Newtonian;
nu              [0 2 -1 0 0 0 0] 0.01;  // Re = UL/ν = 100
```

---

## 2. Solving

### 2.1 WHAT: Solver Configuration Files, WHY: Control Numerical Methods and Convergence, HOW: Through system/ Dictionary Files

**system/controlDict** — Time control:

```cpp
application     icoFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         0.5;
deltaT          0.005;
writeControl    timeStep;
writeInterval   20;
```

**system/fvSchemes** — Discretization schemes:

```cpp
ddtSchemes      { default Euler; }
gradSchemes     { default Gauss linear; }
divSchemes      { div(phi,U) Gauss upwind; }
laplacianSchemes { default Gauss linear corrected; }
interpolationSchemes { default linear; }
snGradSchemes   { default corrected; }
```

**system/fvSolution** — Linear solvers and algorithm settings:

```cpp
solvers
{
    p
    {
        solver      GAMG;
        tolerance   1e-06;
        relTol      0.01;
        smoother    GaussSeidel;
    }
    U
    {
        solver      smoothSolver;
        smoother    GaussSeidel;
        tolerance   1e-05;
        relTol      0;
    }
}

PISO
{
    nCorrectors     2;
    nNonOrthogonalCorrectors 0;
    pRefCell        0;
    pRefValue       0;
}
```

### 2.2 WHAT: Running the Simulation, WHY: Execute the Solver to Compute Solution, HOW: Through Command Line with Output Redirection

```bash
# Serial execution
icoFoam > log.icoFoam 2>&1 &

# Monitor progress
tail -f log.icoFoam

# Check convergence behavior
grep "Initial residual" log.icoFoam
```

### 2.3 WHAT: Convergence Criteria and Troubleshooting, WHY: Ensure Reliable and Accurate Solutions, HOW: By Monitoring Residuals and Diagnosing Common Issues

**Convergence Criteria:**
- Residuals decrease by 3-4 orders of magnitude
- Solution stops changing significantly (steady state)

**Common Problems and Solutions:**

| Problem | Cause | Solution |
|---------|-------|----------|
| Divergence | Time step too large | Reduce `deltaT` |
| No convergence | Inconsistent BCs | Check U-p pairing |
| Oscillations | Unstable scheme | Switch to upwind |

---

## 3. Post-Processing

### 3.1 WHAT: Visualization with ParaView, WHY: Qualitative Understanding of Flow Physics, HOW: Using paraFoam Command

```bash
paraFoam
```

**Key Visualizations:**
1. **Velocity magnitude** — Check max/min values
2. **Streamlines** — Observe flow patterns
3. **Pressure contours** — Examine distribution
4. **Animation** — View time evolution

### 3.2 WHAT: Quantitative Data Analysis, WHY: Extract Numerical Data for Validation, HOW: Using Sampling Functions in controlDict

> **⚠️ Note:** For detailed step-by-step sampling examples and hands-on implementation, see [04_Step-by-Step_Tutorial.md](04_Step-by-Step_Tutorial.md) — Step 10.

**Probes** — Monitor at specific points:

```cpp
// system/controlDict
functions
{
    probes
    {
        type            probes;
        libs            (sampling);
        writeControl    timeStep;
        writeInterval   1;
        fields          (U p);
        probeLocations  ((0.5 0.5 0.05));
    }
}
```

**Sample Lines** — Extract data along lines:

> **⚠️ Version Note:** In OpenFOAM v4+, use `functions` in `controlDict` instead of separate `sampleDict`

**Method 1: Using controlDict functions (recommended for OpenFOAM v4+):**

```cpp
// system/controlDict
functions
{
    centerlineY
    {
        type            sets;
        setFormat       raw;
        fields          (U p);
        interpolationScheme cellPoint;

        sets
        (
            centerlineY
            {
                type    uniform;
                axis    y;
                start   (0.5 0 0.05);
                end     (0.5 1 0.05);
                nPoints 100;
            }
        );
    }
}
```

**Method 2: Using postProcess utility:**

```bash
# Run after simulation completes
postProcess -func centerlineY
```

Output is written to `postProcessing/centerlineY/`

---

## Workflow Summary

```bash
#!/bin/bash
# Allrun script

# 1. Clean
foamCleanTutorials  # Only for tutorials from $FOAM_TUTORIALS
# Or for custom cases:
# rm -rf 0/*/processor* */postProcessing/ [0-9]*/

# 2. Mesh
blockMesh
checkMesh

# 3. Solve
icoFoam > log.icoFoam 2>&1

# 4. Post-process
paraFoam
```

---

## Key Takeaways

- **Three distinct stages** — Pre-processing (mesh, BCs, properties), Solving (configuration, execution), Post-processing (visualization, analysis)
- **Quality mesh first** — Always verify mesh quality with `checkMesh` before running the solver
- **Convergence monitoring** — Track residuals through log files and recognize divergence patterns
- **U-p boundary pairing** — Velocity and pressure boundary conditions must be physically consistent
- **Pressure reference** — Incompressible flows require `pRefCell` and `pRefValue` for unique pressure solutions
- **Sampling for validation** — Use probes and sample lines to extract quantitative data for comparison with benchmarks

---

## Concept Check

<details>
<summary><b>1. WHY is the empty boundary condition used for frontAndBack?</b></summary>

Because this is a 2D simulation — there is no variation in the z-direction, so the solver does not need to solve equations in that direction. The `empty` type tells OpenFOAM to ignore the third dimension.
</details>

<details>
<summary><b>2. WHAT does the PISO nCorrectors parameter control?</b></summary>

The number of pressure-velocity coupling correction iterations per time step. Values of 2-3 are sufficient for most cases. Higher values improve coupling accuracy but increase computational cost.
</details>

<details>
<summary><b>3. WHY must pRefCell and pRefValue be specified?</b></summary>

In incompressible flow, the governing equations contain only pressure gradients (∇p), not absolute pressure values. This means pressure is defined only up to an arbitrary constant. Fixing the value at one cell ensures a unique mathematical solution.
</details>

<details>
<summary><b>4. HOW does decreasing deltaT help with divergence?</b></summary>

Smaller time steps reduce the change in solution between iterations, improving stability for explicit schemes and tight coupling between pressure and velocity in transient simulations.
</details>

---

## Related Documents

- **Previous:** [01_Introduction.md](01_Introduction.md) — Introduction to OpenFOAM
- **Next:** [03_The_Lid-Driven_Cavity_Problem.md](03_The_Lid-Driven_Cavity_Problem.md) — Cavity Flow Problem Definition
- **Hands-on Tutorial:** [04_Step-by-Step_Tutorial.md](04_Step-by-Step_Tutorial.md) — Complete Implementation with Detailed Sampling Examples
- **Boundary Conditions:** [../../03_BOUNDARY_CONDITIONS/05_Common_Boundary_Conditions_in_OpenFOAM.md](../../03_BOUNDARY_CONDITIONS/05_Common_Boundary_Conditions_in_OpenFOAM.md) — Comprehensive BC Reference