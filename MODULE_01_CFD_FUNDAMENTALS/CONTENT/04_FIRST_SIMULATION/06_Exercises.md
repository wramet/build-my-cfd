# แบบฝึกหัด: Lid-Driven Cavity

## Learning Objectives

**Students will be able to:**
- Practice parameter variations (Reynolds number, mesh resolution, time step)
- Modify OpenFOAM case files and observe their effects
- Develop troubleshooting skills for simulation convergence issues
- Validate simulation results against benchmark data
- Perform mesh refinement studies and sensitivity analysis
- Understand numerical scheme selection and stability
- Execute parallel simulations and post-process results
- Debug common simulation errors systematically

---

## Key Takeaways

- **Parameter sensitivity** is essential for understanding CFD behavior
- **Grid convergence** studies validate numerical accuracy
- **Scheme selection** balances accuracy vs. stability trade-offs
- **Validation against experimental/benchmark data** establishes credibility
- **Troubleshooting methodology** follows systematic root-cause analysis
- **Parallel computing** requires domain decomposition and reconstruction
- **Turbulent flows** demand specialized solvers and turbulence modeling

---

## Introduction

### WHY These Exercises?
- **Hands-on practice** — Reading alone is insufficient for CFD mastery
- **Develop troubleshooting skills** — Learn when simulations fail and why
- **Build intuition** — Understand how parameters affect results
- **Prepare for real projects** — Gain confidence for complex simulations

### HOW to Approach These Exercises
1. Start with **Exercise 1** (basic simulation)
2. Progress through **Exercises 2-7** (parameter studies)
3. **Exercise 8** (turbulent flow) is advanced — see note below
4. **Exercise 9** (debugging) is essential for all simulations
5. Complete **Concept Check** to verify understanding

---

## Exercise 1: Basic Simulation

**Estimated Time:** 20-30 minutes

### Learning Outcome
Set up and run a complete OpenFOAM simulation from scratch, following the standard workflow.

### WHAT You Will Do
Run the lid-driven cavity case at Re = 100 using the icoFoam solver.

### WHY This Matters
This exercise establishes the baseline simulation you'll modify in subsequent exercises. Mastery of the basic workflow is prerequisite for all advanced studies.

### HOW to Complete

**Tasks:**
1. Copy tutorial case to working directory
2. Verify setup parameters
3. Generate mesh
4. Run solver
5. Visualize results in ParaView

<details>
<summary><b>Solution</b></summary>

```bash
# 1. Setup case directory
cp -r $FOAM_TUTORIALS/incompressible/icoFoam/cavity/cavity myCase
cd myCase

# 2. Check ν for Re=100
cat constant/transportProperties
# nu = 0.01 → Re = (1×1)/0.01 = 100 ✓

# 3. Generate mesh and check quality
blockMesh
checkMesh

# 4. Run solver with output logging
icoFoam > log.icoFoam 2>&1

# 5. Launch ParaView for visualization
paraFoam
```

**Expected results:**
- Primary vortex in cavity center
- Corner vortices at bottom (secondary vortices)
- Converged solution by t = 0.5 s

</details>

---

## Exercise 2: Change Reynolds Number

**Estimated Time:** 15 minutes per variation

### Learning Outcome
Understand how Reynolds number affects flow characteristics and simulation requirements.

### WHAT You Will Do
Modify kinematic viscosity to achieve Re = 400 and Re = 1000, observing flow changes.

### WHY This Matters
Reynolds number governs flow regime and physics. Understanding its effect is fundamental to CFD.

### HOW to Complete

**Physical relationship:**
$$Re = \frac{UL}{\nu}$$

Where: U = 1 m/s (lid velocity), L = 1 m (cavity length)

<details>
<summary><b>Solution</b></summary>

**Re = 400:**
```cpp
// constant/transportProperties
nu [0 2 -1 0 0 0 0] 0.0025;  // Re = 1/0.0025 = 400
```

**Re = 1000:**
```cpp
nu [0 2 -1 0 0 0 0] 0.001;   // Re = 1/0.001 = 1000
```

**Expected observations:**
- **Re = 400:** Stronger primary vortex, larger corner vortices
- **Re = 1000:** Vortex center shifts toward cavity center, sharper velocity gradients

**For higher Re, you may need to:**
- Increase mesh resolution (see Exercise 3)
- Reduce time step for stability (see Exercise 4)
- Extend simulation time for convergence
- Monitor Courant number (should be < 1)

</details>

---

## Exercise 3: Mesh Refinement Study

**Estimated Time:** 30 minutes

### Learning Outcome
Perform grid convergence study to assess numerical accuracy and mesh independence.

### WHAT You Will Do
Compare 20×20 mesh with 40×40 mesh and quantify differences.

### WHY This Matters
Mesh resolution directly impacts accuracy. Grid convergence studies are **required** for credible CFD results.

### HOW to Complete

**Grid refinement ratio:** r = 2 (20 → 40 cells per direction)

<details>
<summary><b>Solution</b></summary>

```cpp
// constant/polyMesh/blockMeshDict
blocks
(
    hex (0 1 2 3 4 5 6 7) (40 40 1) simpleGrading (1 1 1)
);
```

```bash
# Regenerate mesh
blockMesh
checkMesh

# Run simulation
icoFoam > log.icoFoam 2>&1
```

**Comparison metrics:**
| Metric | 20×20 | 40×40 |
|--------|-------|-------|
| Total cells | 400 | 1,600 |
| Vortex center location | (0.62, 0.75) | (0.617, 0.739) |
| Max velocity at centerline | 0.21 | 0.22 |
| Runtime | ~30 s | ~2 min |

**Expected improvements with finer mesh:**
- Vortex center closer to benchmark (Ghia et al.)
- Smoother velocity profiles
- Better resolution of corner vortices
- Increased computational cost

</details>

---

## Exercise 4: Time Step Sensitivity

**Estimated Time:** 45 minutes (3 runs)

### Learning Outcome
Understand time step selection, Courant-Friedrichs-Lewy (CFL) condition, and temporal accuracy.

### WHAT You Will Do
Test deltaT = 0.001, 0.005, 0.01 for Re = 100 and assess stability/accuracy.

### WHY This Matters
Time step controls temporal resolution and stability. Incorrect values cause divergence or unnecessary computational cost.

### HOW to Complete

**CFL number guideline:**
$$CFL = \frac{U \Delta t}{\Delta x} < 1$$

<details>
<summary><b>Solution</b></summary>

```cpp
// system/controlDict
application     icoFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         0.5;
deltaT          0.001;  // Test: 0.001, 0.005, 0.01
writeControl    timeStep;
writeInterval   20;
```

**Results comparison:**
| deltaT | CFL (approx) | Stability | Accuracy | Runtime |
|--------|--------------|-----------|----------|---------|
| 0.001 | ~0.02 | Very stable | High | Long |
| 0.005 | ~0.1 | Stable | Good | Medium |
| 0.01 | ~0.2 | Marginal | Acceptable | Short |

**Key insight:** Larger deltaT reduces runtime but may compromise accuracy. For transient flows, always check CFL number in log file.

</details>

---

## Exercise 5: Discretization Schemes

**Estimated Time:** 40 minutes

### Learning Outcome
Compare numerical schemes for convection terms and understand accuracy vs. stability trade-offs.

### WHAT You Will Do
Run simulations with `Gauss linear` (2nd order) vs `Gauss upwind` (1st order) schemes.

### WHY This Matters
Scheme selection is fundamental to CFD. Higher-order schemes increase accuracy but may cause stability issues.

### HOW to Complete

**Schemes modify:** Convection term discretization in momentum equation

<details>
<summary><b>Solution</b></summary>

**Gauss linear (2nd order accurate):**
```cpp
// system/fvSchemes
divSchemes
{
    div(phi,U)  Gauss linear;
}
```

**Gauss upwind (1st order accurate):**
```cpp
divSchemes
{
    div(phi,U)  Gauss upwind;
}
```

**Comparison:**
| Scheme | Accuracy | Stability | Numerical Diffusion | Use Case |
|--------|----------|-----------|---------------------|----------|
| linear | 2nd order | May oscillate at high Re | Low | Fine grids, low Re |
| upwind | 1st order | Very stable | High | Coarse grids, high Re |

**Visual differences:**
- **linear:** Sharper velocity gradients, potential oscillations
- **upwind:** Smoother but more diffused results (vortex appears "blurred")

**Practical tip:** Start with upwind for stability, switch to linear after mesh refinement.

</details>

---

## Exercise 6: Validation Against Benchmark Data

**Estimated Time:** 30 minutes

### Learning Outcome
Extract quantitative data from simulations and compare with established experimental/numerical benchmarks.

### WHAT You Will Do
Extract centerline velocity profiles and compare with Ghia et al. (1982) benchmark data.

### WHY This Matters
Validation is **essential** for CFD credibility. Comparison with trusted data verifies your setup is correct.

### HOW to Complete

**Reference:** Ghia, U., Ghia, K.N., Shin, C.T. (1982). "High-Re solutions for incompressible flow using the Navier-Stokes equations and a multigrid method." *Journal of Computational Physics* 48, 387-411.

<details>
<summary><b>Solution</b></summary>

**1. Add sampling function to controlDict:**
```cpp
// system/controlDict (add to functions block)
functions
{
    sample1
    {
        type            sets;
        libs            (sampling);
        writeControl    writeTime;
        setFormat       raw;
        
        sets
        (
            verticalCenterline
            {
                type    uniform;
                axis    y;
                start   (0.5 0 0.05);
                end     (0.5 1 0.05);
                nPoints 100;
            }
        );
        fields          (U);
    }
}
```

**2. Run post-processing:**
```bash
# Extract data at final time
postProcess -func sample1 -latestTime

# View data
cat postProcessing/sample1/0.5/verticalCenterline_U.xy
```

**3. Data location:**
```
postProcessing/sample1/0.5/verticalCenterline_U.xy
```

**4. Compare with Ghia et al. (Re = 100):**

| y | U_x (Ghia) | U_x (OpenFOAM) | Error (%) |
|---|------------|----------------|-----------|
| 0.1 | -0.03717 | -0.036 | ~3% |
| 0.5 | -0.20581 | -0.202 | ~2% |
| 0.9 | 0.32734 | 0.321 | ~2% |

**Expected agreement:** Within 3-5% for properly resolved mesh

</details>

---

## Exercise 7: Parallel Computation

**Estimated Time:** 25 minutes

### Learning Outcome
Decompose domain, run parallel simulation, and reconstruct results for post-processing.

### WHAT You Will Do
Run cavity case in parallel on 4 cores using domain decomposition.

### WHY This Matters
Parallel computing reduces runtime for large cases. Understanding the workflow is essential for practical CFD.

### HOW to Complete

**Key concepts:**
- **Decomposition:** Split mesh into subdomains
- **Parallel execution:** Each core solves one subdomain
- **Reconstruction:** Merge subdomain results for visualization

<details>
<summary><b>Solution</b></summary>

**1. Create decomposition dictionary:**
```cpp
// system/decomposeParDict
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      decomposeParDict;
}

numberOfSubdomains 4;
method          simple;

simpleCoeffs
{
    n           (2 2 1);  // 2×2×1 decomposition
    delta       0.001;
}
```

**2. Execute parallel workflow:**
```bash
# Decompose domain
decomposePar

# Verify decomposition (optional)
ls processor* | wc -l  # Should show 4 processors

# Run in parallel
mpirun -np 4 icoFoam -parallel > log.icoFoam 2>&1

# Reconstruct results
reconstructPar

# Visualize (uses reconstructed 0.5/* files)
paraFoam
```

**Speedup comparison:**
| Configuration | Runtime | Speedup |
|--------------|---------|---------|
| Serial (1 core) | 30 s | 1.0× |
| Parallel (4 cores) | 10 s | 3.0× |

**Note:** Speedup is rarely linear due to communication overhead.

</details>

---

## Exercise 8: Turbulent Flow at High Reynolds Number

**Estimated Time:** 45-60 minutes

**Prerequisites:** Completion of Exercises 1-7 recommended

### Learning Outcome
Set up and run turbulent flow simulation using RANS turbulence modeling.

### WHAT You Will Do
Configure cavity simulation for Re = 10,000 using turbulence model and appropriate solver.

### WHY This Matters
Turbulent flows require fundamentally different approaches from laminar flows. This exercise prepares you for advanced CFD applications.

### ⚠️ IMPORTANT NOTE
This exercise introduces **advanced concepts** covered in detail in:
- **Module XX:** Turbulence Modeling (future module)
- **Module XX:** RANS/LES Methods (future module)

For now, focus on understanding **setup requirements** rather than detailed turbulence theory.

### HOW to Complete

**Key changes from laminar case:**
1. Different solver (transient vs. steady-state options)
2. Turbulence model specification
3. Additional transport equations (k, ε, ω)
4. Wall boundary conditions
5. Different mesh requirements (y+ considerations)

<details>
<summary><b>Solution</b></summary>

**1. Solver selection:**
```cpp
// system/controlDict
application     pimpleFoam;  // Transient turbulent
// OR
application     simpleFoam;  // Steady-state turbulent
```

**2. Turbulence model:**
```cpp
// constant/turbulenceProperties
simulationType  RAS;
RAS
{
    RASModel        kEpsilon;
    turbulence      on;
    printCoeffs     on;
}
```

**3. Additional boundary conditions (create these files):**

```cpp
// 0/k (turbulent kinetic energy)
dimensions      [0 2 -2 0 0 0 0];
internalField   uniform 0.1;

boundaryField
{
    movingWall
    {
        type            fixedValue;
        value           uniform 0.1;
    }
    fixedWalls
    {
        type            kqRWallFunction;
        value           uniform 0.1;
    }
    frontAndBack
    {
        type            empty;
    }
}
```

```cpp
// 0/epsilon (dissipation rate)
dimensions      [0 2 -3 0 0 0 0];
internalField   uniform 0.01;

boundaryField
{
    movingWall
    {
        type            fixedValue;
        value           uniform 0.01;
    }
    fixedWalls
    {
        type            epsilonWallFunction;
        value           uniform 0.01;
    }
    frontAndBack
    {
        type            empty;
    }
}
```

```cpp
// 0/nut (turbulent viscosity)
dimensions      [0 2 -1 0 0 0 0];
internalField   uniform 0;

boundaryField
{
    movingWall
    {
        type            nutkWallFunction;
        value           uniform 0;
    }
    fixedWalls
    {
        type            nutkWallFunction;
        value           uniform 0;
    }
    frontAndBack
    {
        type            empty;
    }
}
```

**4. Mesh requirements:**
- **y+ ≈ 30-300** for standard wall functions
- Finer near-wall resolution than laminar case
- Typical: 60×60 cells with boundary layer grading

**5. Expected differences from laminar:**
- Slower convergence
- Higher residual tolerance acceptable (~1e-4)
- Time-averaged flow statistics
- More complex vortex structures

**See also:**
- [Turbulence Modeling Documentation](https://www.openfoam.com/documentation/guides/latest/doc/turbulence.html)
- [Wall Function Guide](https://www.openfoam.com/documentation/guides/latest/doc/boundary-cond-wall.html)

</details>

---

## Exercise 9: Debugging Divergent Simulations

**Estimated Time:** 30 minutes (per debugging scenario)

### Learning Outcome
Develop systematic troubleshooting methodology for simulation convergence failures.

### WHAT You Will Do
Diagnose and fix a diverging simulation using common error patterns and solutions.

### WHY This Matters
All CFD practitioners encounter convergence issues. Systematic debugging saves hours of frustration.

### HOW to Complete

**Debugging workflow:**
1. **Identify symptoms** (error message, residuals, behavior)
2. **Check logs** (last 100 lines of solver log)
3. **Isolate cause** (mesh, BC, schemes, parameters)
4. **Apply fix** (modify appropriate setting)
5. **Verify solution** (confirm convergence)

<details>
<summary><b>Solution</b></summary>

**Scenario: Maximum iterations error**
```
FOAM FATAL ERROR:
Maximum number of iterations exceeded
```

**Possible causes & systematic fixes:**

**1. Time step too large**
```cpp
// system/controlDict
deltaT  0.0005;  // Reduce from current value

// Check Courant number in log:
// "Max Courant Number = 2.3" → Too high! Reduce deltaT
```

**2. Mesh quality issues**
```bash
# Check mesh quality metrics
checkMesh

# Look for:
# - Non-orthogonality > 70°
# - Skewness > 4
# - Concave cells
```

**Fix:** Improve mesh grading or cell distribution

**3. Unstable numerical scheme**
```cpp
// system/fvSchemes
divSchemes
{
    div(phi,U)  Gauss upwind;  // Change from linear to upwind
}
```

**4. Boundary condition mismatch**
```bash
# Verify patch names match
cat constant/polyMesh/boundary  # Check patch names

# Verify BC consistency
cat 0/U  # Check boundaryField names
cat 0/p  # Should have same patches
```

**5. Insufficient solver tolerance**
```cpp
// system/fvSolution
solvers
{
    p
    {
        solver          GAMG;
        tolerance       1e-06;  // Tighten tolerance
        relTol          0.01;
    }
    U
    {
        solver          smoothSolver;
        tolerance       1e-05;  // Tighten tolerance
        relTol          0.1;
    }
}
```

**6. Under-relaxation factors (for steady solvers)**
```cpp
// system/fvSolution (for simpleFoam)
relaxationFactors
{
    fields
    {
        p       0.3;  // Reduce from default
    }
    equations
    {
        U       0.5;  // Reduce from default
    }
}
```

**Debugging checklist:**
- [ ] Check last 100 lines of log file
- [ ] Verify mesh quality with checkMesh
- [ ] Confirm BC patch names match
- [ ] Monitor Courant number
- [ ] Test with first-order schemes
- [ ] Reduce time step
- [ ] Tighten solver tolerances

</details>

---

## Concept Check

Test your understanding with these questions.

<details>
<summary><b>1. For Re = 500, what value of ν is required?</b></summary>

**Solution:**

$$\nu = \frac{UL}{Re} = \frac{1 \times 1}{500} = 0.002 \text{ m}^2/\text{s}$$

```cpp
// constant/transportProperties
nu [0 2 -1 0 0 0 0] 0.002;
```

</details>

<details>
<summary><b>2. How many cells does a 40×40 mesh contain?</b></summary>

**Solution:**

Total cells = 40 × 40 × 1 = **1,600 cells** (quasi-2D case)

This is 4× more cells than the 20×20 mesh (400 cells), leading to approximately 4× longer runtime.

</details>

<details>
<summary><b>3. Why is reconstructPar needed after parallel runs?</b></summary>

**Solution:**

`decomposePar` splits the mesh into separate subdomains (processor*/ directories). After parallel execution:
- Results are distributed across processor0/, processor1/, etc.
- `reconstructPar` merges these into a single domain
- Reconstructed data (e.g., 0.5/*) is required for visualization

Without reconstruction, ParaView cannot display the complete solution.

</details>

<details>
<summary><b>4. What is the grid convergence index (GCI) for the mesh refinement study?</b></summary>

**Solution:**

GCI quantifies uncertainty from mesh discretization:

$$GCI = \frac{F_s |\epsilon|}{r^p - 1}$$

Where:
- \(F_s\) = safety factor (1.25 for comparisons)
- \(\epsilon\) = relative error between meshes
- \(r\) = refinement ratio (2 for 20→40)
- \(p\) = order of accuracy (2 for icoFoam)

For example, if max velocity differs by 4.8% between meshes:

$$GCI_{21} = \frac{1.25 \times 0.048}{2^2 - 1} \approx 3.2\%$$

This indicates the numerical uncertainty from mesh resolution is approximately 3.2%.

</details>

---

## Summary and Next Steps

### Skills Developed

✓ **Case management** — Setup, run, and modify OpenFOAM cases  
✓ **Parameter studies** — Reynolds number, mesh, time step sensitivity  
✓ **Scheme selection** — Understand accuracy vs. stability trade-offs  
✓ **Validation** — Compare with benchmark data  
✓ **Parallel computing** — Domain decomposition and reconstruction  
✓ **Troubleshooting** — Systematic debugging methodology  

### Further Practice

- **Explore other geometries:** Backward-facing step, channel flow
- **Advanced post-processing:** Force calculations, field averages
- **Automation:** Python/bash scripts for batch parameter studies
- **Turbulence:** Complete Module XX on turbulence modeling

### Related Documentation

- **Previous:** [05_Expected_Results.md](05_Expected_Results.md) — Benchmark results
- **Next:** [00_Overview.md](00_Overview.md) — Return to module overview
- **Module Reference:** [03_BOUNDARY_CONDITIONS/05_Common_Boundary_Conditions_in_OpenFOAM.md](../../03_BOUNDARY_CONDITIONS/05_Common_Boundary_Conditions_in_OpenFOAM.md) — Boundary condition details
- **Numerical Methods:** [02_FINITE_VOLUME_METHOD/00_Overview.md](../../02_FINITE_VOLUME_METHOD/00_Overview.md) — Discretization schemes