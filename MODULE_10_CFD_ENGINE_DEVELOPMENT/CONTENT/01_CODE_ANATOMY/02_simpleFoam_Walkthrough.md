# simpleFoam Walkthrough

Steady-State Turbulent Incompressible Solver

---

> **Difficulty:** Intermediate
> **Related Files:**
> - Previous: [01_icoFoam_Walkthrough.md](01_icoFoam_Walkthrough.md) - Transient solver foundation
> - Next: [03_kEpsilon_Model_Anatomy.md](03_kEpsilon_Model_Anatomy.md) - Turbulence model details
> - Configuration: `system/fvSolution`, `constant/turbulenceProperties`

---

## Prerequisites

Before studying this walkthrough, ensure you have:

1. ✅ **Completed** the [icoFoam Walkthrough](01_icoFoam_Walkthrough.md) for pressure-velocity coupling fundamentals
2. ✅ **Understanding** of PISO algorithm (from icoFoam)
3. ✅ **Basic knowledge** of RANS turbulence modeling concepts
4. ✅ **Familiarity** with OpenFOAM case structure (`0/`, `constant/`, `system/`)
5. ✅ **Development environment** setup with `compile_commands.json` (see [Module 03](../../../MODULE_03_OPENFOAM_PROGRAMMING/))

---

## Learning Objectives

By the end of this walkthrough, you will be able to:

1. **Differentiate** SIMPLE from PISO algorithms and understand when to use each
2. **Explain** the role of under-relaxation in steady-state simulations
3. **Identify** key code differences between transient (icoFoam) and steady-state (simpleFoam) solvers
4. **Configure** turbulence models using Runtime Selection mechanism
5. **Diagnose** convergence issues and adjust relaxation factors appropriately
6. **Interpret** residual behavior in steady-state iterative solutions

---

## Overview

**simpleFoam** is OpenFOAM's steady-state solver for incompressible, turbulent Newtonian fluids. It implements the **SIMPLE** (Semi-Implicit Method for Pressure-Linked Equations) algorithm for pressure-velocity coupling.

### Key Characteristics

| Feature | Description |
|:---|:---|
| **Time** | Steady-State (pseudo-time iterations only) |
| **Turbulence** | RANS Models (k-ε, k-ω, Spalart-Allmaras, etc.) |
| **P-V Coupling** | SIMPLE algorithm |
| **Under-relaxation** | **Required** for stability |
| **Time Loop** | `simple.loop()` (pseudo-time iterations) |

### SIMPLE vs PISO: Core Difference

<!-- IMAGE: IMG_10_003 -->
<!--
Purpose: Show clear difference between SIMPLE and PISO algorithms
Prompt: "Split-screen infographic comparing PISO and SIMPLE CFD algorithms. **Left Side (PISO - Transient):** Vertical flow of stacked blocks representing time steps. Arrows flowing down. Label: 'Transient / Time-Accurate'. Color: Cool Blue. **Right Side (SIMPLE - Steady):** A large circular cycle representing iterations. Arrows looping continuously. Label: 'Steady-State / Iterative'. Color: Warm Orange. **Comparison Table at Bottom:** Minimalist icons for 'Time' (Clock vs Infinity), 'Relaxation' (None vs Required). **Style:** Modern technical infographic, clean isometric view, soft lighting, professional layout."
-->
![IMG_10_003: SIMPLE vs PISO](IMG_10_003.jpg)

**SIMPLE Algorithm:**
- Single pressure correction per iteration
- Requires under-relaxation for stability
- Iterates until residuals converge (not time-accurate)
- Efficient for steady-state solutions

**See icoFoam Walkthrough** for PISO algorithm details (transient, multiple corrections per time step, no under-relaxation needed).

---

## Comparison: simpleFoam vs icoFoam

| Feature | [icoFoam](01_icoFoam_Walkthrough.md) | simpleFoam |
|:---|:---|:---|
| **Time** | Transient (`runTime.loop()`) | Steady-State (`simple.loop()`) |
| **Turbulence** | Laminar only | RANS Models |
| **P-V Coupling** | PISO | SIMPLE |
| **Under-relaxation** | Not required | **Mandatory** |
| **Pressure Corrections** | Multiple (2-3) per time step | Single per iteration |
| **Convergence** | Time-marching | Residual-based |
| **Primary Use** | Time-dependent flows | Steady operating points |

---

## Source Location

```bash
$FOAM_SOLVERS/incompressible/simpleFoam/simpleFoam.C
```

**To explore with IDE intelligence:**
```bash
# Ensure compile_commands.json is generated (see Module 03)
cd $FOAM_SOLVERS/incompressible/simpleFoam
wmake
```

---

## Key Code Sections

### 1. Turbulence Model Initialization

```cpp
#include "singlePhaseTransportModel.H"
#include "turbulentTransportModel.H"

// ...

singlePhaseTransportModel laminarTransport(U, phi);

autoPtr<incompressible::turbulenceModel> turbulence
(
    incompressible::turbulenceModel::New(U, phi, laminarTransport)
);
```

> [!NOTE]
> **Runtime Selection (RTS) in Action!**
>
> Turbulence model is selected from `constant/turbulenceProperties`:
> ```cpp
> simulationType RAS;
> RAS 
> { 
>     model kEpsilon; 
> }
> ```
>
> Available models: kEpsilon, kOmegaSST, SpalartAllmaras, etc.

**Difference from icoFoam:** icoFoam uses only laminar viscosity (`singlePhaseTransportModel`), while simpleFoam adds `turbulenceModel` for RANS closure.

---

### 2. SIMPLE Control Object

```cpp
#include "simpleControl.H"

simpleControl simple(mesh);
```

`simpleControl` reads settings from `system/fvSolution`:

```cpp
SIMPLE
{
    nNonOrthogonalCorrectors 1;
    
    residualControl
    {
        p       1e-4;
        U       1e-4;
    }
    
    relaxationFactors
    {
        fields
        {
            p       0.3;
        }
        equations
        {
            U       0.7;
            k       0.7;
            epsilon 0.7;
        }
    }
}
```

**Key parameters:**
- `nNonOrthogonalCorrectors`: Additional pressure corrections for non-orthogonal meshes
- `residualControl`: Convergence targets for each variable
- `relaxationFactors`: Under-relaxation coefficients (see Section 4)

---

### 3. SIMPLE Loop (Not Time Loop!)

```cpp
Info<< "\nStarting iteration loop\n" << endl;

while (simple.loop())   // NOT runTime.loop()!
{
    Info<< "Iteration = " << runTime.timeName() << nl << endl;
```

> [!IMPORTANT]
> **Pseudo-Time Stepping**
>
> `simple.loop()` uses "iteration number" as the time index:
> - **No physical time meaning**
> - Used only for convergence tracking and output organization
> - Loop exits when residuals < tolerance (set in `residualControl`)

**Contrast with icoFoam:**
```cpp
// icoFoam (transient):
while (runTime.loop())  // Actual physical time progression
{
    // Time-accurate solution
}

// simpleFoam (steady):
while (simple.loop())   // Iteration counter only
{
    // Steady-state convergence
}
```

---

### 4. Momentum Equation with Under-Relaxation

```cpp
    // Momentum predictor
    tmp<fvVectorMatrix> tUEqn
    (
        fvm::div(phi, U)               // Convection
      + turbulence->divDevReff(U)      // Diffusion (laminar + turbulent)
      ==
        fvOptions(U)                   // Source terms
    );
    fvVectorMatrix& UEqn = tUEqn.ref();

    UEqn.relax();                      // CRITICAL: Under-relaxation!

    fvOptions.constrain(UEqn);

    if (simple.momentumPredictor())
    {
        solve(UEqn == -fvc::grad(p));
    }
```

#### Critical: Why `UEqn.relax()`?

**SIMPLE algorithm is not exact** — without relaxation, it oscillates and diverges:

$$U^{new} = \alpha \cdot U^{calculated} + (1-\alpha) \cdot U^{old}$$

Where α (alpha) is the relaxation factor (typically 0.3-0.7).

<!-- IMAGE: IMG_10_004 -->
<!--
Purpose: Visualize effect of Under-Relaxation on SIMPLE convergence
Prompt: "Scientific data visualization of Under-Relaxation in CFD. **Layout:** Three horizontal panels. **Left Panel (Instability):** Graph of 'Residual vs Iteration'. A red jagged line oscillating wildly and growing. Label: 'No Relaxation (Divergence)'. **Center Panel (The Mechanism):** Conceptual blending visualization. Two liquid streams merging: 'Computed Value' (New) and 'Previous Value' (Old) mixing to form 'Relaxed Value'. Formula: 'φ_new = α*φ_new + (1-α)*φ_old'. **Right Panel (Stability):** Graph showing a smooth blue curve decaying exponentially. Label: 'With Relaxation (Convergence)'. **Style:** High-contrast technical plots, white background, textbook quality illustration."
-->
![IMG_10_004: Under-Relaxation Effect](IMG_10_004.jpg)

**Difference from icoFoam:** icoFoam does **not** use `UEqn.relax()` because PISO's multiple pressure corrections provide stability through small time steps.

---

### 5. Understanding `turbulence->divDevReff(U)`

```cpp
// Returns: -div((νeff) grad(U)) - div((νeff) grad(U)^T)
//        = -div(νeff dev(2 S)) where S = 0.5(grad(U) + grad(U)^T)
```

**Breaking it down:**
- `νeff = ν + νt` (molecular + turbulent viscosity)
- `dev()` = deviatoric part (subtract 1/3 trace for incompressible flow)
- Handles both laminar and turbulent stress in single term

**See:** [03_kEpsilon_Model_Anatomy.md](03_kEpsilon_Model_Anatomy.md) for complete turbulence model implementation.

---

### 6. Pressure Correction

```cpp
    // Pressure-velocity coupling
    {
        volScalarField rAU(1.0/UEqn.A());
        volVectorField HbyA(constrainHbyA(rAU*UEqn.H(), U, p));

        surfaceScalarField phiHbyA("phiHbyA", fvc::flux(HbyA));
        adjustPhi(phiHbyA, U, p);

        // Non-orthogonal pressure corrector loop
        while (simple.correctNonOrthogonal())
        {
            fvScalarMatrix pEqn
            (
                fvm::laplacian(rAU, p) == fvc::div(phiHbyA)
            );

            pEqn.setReference(pRefCell, pRefValue);
            pEqn.solve();

            if (simple.finalNonOrthogonalIter())
            {
                phi = phiHbyA - pEqn.flux();
            }
        }

        #include "continuityErrs.H"

        // Correct velocity
        U = HbyA - rAU*fvc::grad(p);
        U.correctBoundaryConditions();
    }
```

**Key difference from icoFoam PISO:**
- **PISO:** Multiple `while (piso.correct())` loops (typically 2-3) per time step
- **SIMPLE:** Single `while (simple.correctNonOrthogonal())` loop per iteration

**Pressure-velocity coupling mechanics** are covered in detail in [01_icoFoam_Walkthrough.md](01_icoFoam_Walkthrough.md#6-pressure-correction-loop).

---

### 7. Pressure Field Relaxation

```cpp
    p.relax();     // Explicit field relaxation
```

> [!NOTE]
> **Equation Relaxation vs Field Relaxation**
>
> | Type | What it does | When to use |
> |:---|:---|:---|
> | `UEqn.relax()` | Modifies matrix diagonal before solving | **Before** solve |
> | `p.relax()` | Blends field with previous iteration values | **After** solve |

**Formula:**
```cpp
p = alpha * p_new + (1 - alpha) * p_old;
```

**Not used in icoFoam** — PISO achieves stability through time stepping instead.

---

### 8. Turbulence Model Update

```cpp
    laminarTransport.correct();
    turbulence->correct();      // Solve k and ε equations
```

**What `turbulence->correct()` does:**
1. Calculate production term G from velocity field
2. Solve k transport equation
3. Solve ε transport equation  
4. Update turbulent viscosity: νt = Cμ k²/ε

**RANS equations solved:**
```
∂(U k)/∂xi - ∂(νeff ∂k/∂xi)/∂xi = P - ε
∂(U ε)/∂xi - ∂(νeff ∂ε/∂xi)/∂xi = C1 (ε/k) P - C2 ε²/k
```

---

### 9. Convergence Checking

```cpp
    runTime.write();
    
    Info<< "ExecutionTime = " << runTime.elapsedCpuTime() << " s\n\n";
}

// Loop exits automatically when:
// - All residuals < tolerance (set in fvSolution residualControl)
// - OR maximum iterations reached
```

**Example residual output:**
```
Iteration = 50
smoothSolver: Solving for Ux, Initial residual = 2.3e-04, Final residual = 1.2e-06
GAMG: Solving for p, Initial residual = 8.5e-05, Final residual = 3.4e-07
```

---

## SIMPLE vs PISO Algorithm Comparison

```mermaid
flowchart TB
    subgraph PISO [PISO - Transient (icoFoam)]
        A1[Start Time Step Δt] --> B1[Momentum Predictor]
        B1 --> C1[Pressure Correction 1]
        C1 --> C2[Pressure Correction 2]
        C2 --> C3[Pressure Correction N]
        C3 --> D1[Update U, p]
        D1 --> E1[Next Time Step]
    end

    subgraph SIMPLE [SIMPLE - Steady (simpleFoam)]
        A2[Start Iteration] --> B2[Momentum with Relax]
        B2 --> C2[Single Pressure Correction]
        C2 --> D2[U and p Field Relax]
        D2 --> E2[Turbulence Update]
        E2 --> F2{Residuals < Tolerance?}
        F2 -- No --> A2
        F2 -- Yes --> G2[Converged]
    end
```

**Key Takeaway:**
- **PISO:** Time-accurate, multiple corrections, stable via small Δt
- **SIMPLE:** Steady-state, single correction, stable via under-relaxation

---

## Convergence Behavior and Diagnostics

> **Understanding how SIMPLE converges** — and what to do when it doesn't

### What Does "Convergence" Mean?

In simpleFoam, convergence means:
- Residuals drop below specified tolerance
- Solution stops changing significantly between iterations
- Mass, momentum, and turbulence equations are in balance

### Typical Convergence Pattern

```
Residual │
1.0e+00  │●
         │ ●
1.0e-01  │   ●
         │     ●
1.0e-02  │       ●
         │         ●
1.0e-03  │           ●
         │             ●
1.0e-04  │               ●
         │                 ●
1.0e-05  │                   ●
         └───────────────────────→ Iteration
           1   10  20  30  50  100
```

**Good convergence:** Smooth monotonic decay
- Iteration 1: 1.00e+00
- Iteration 50: 1.00e-04
- Iteration 100: 1.00e-06 ✓ Converged

### How Under-Relaxation Prevents Oscillation

**Physical intuition:**
- SIMPLE guesses pressure from velocity
- Velocity depends on pressure gradient
- **Feedback loop!** Small errors get amplified

**Without relaxation:**
```
Iteration 10:  p = 100 Pa    →  U = 1.0 m/s
Iteration 11:  p = 150 Pa ❌  →  U = 0.5 m/s  (over-correction!)
Iteration 12:  p = 50 Pa ❌   →  U = 1.5 m/s  (wild oscillation)
```

**With relaxation (α = 0.7):**
```
Iteration 10:  p = 100 Pa  →  U = 1.0 m/s
Iteration 11:  p = 135 Pa  →  U = 0.85 m/s  (70% new + 30% old)
Iteration 12:  p = 115 Pa  →  U = 0.95 m/s  (smooth approach!)
```

---

## Common Convergence Problems and Solutions

### Problem 1: Slow Convergence

**Symptoms:**
- Residuals decrease but very slowly
- Takes 500+ iterations to reach 1e-4

**Causes and fixes:**

| Cause | Solution |
|:---|:---|
| Relaxation too conservative | Increase α_U to 0.8 or 0.9 |
| Poor initial guess | Run `potentialFoam` first |
| Poor mesh quality | Check orthogonality, aspect ratio |

**Example:**
```cpp
// Before (slow):
relaxationFactors { fields { p 0.2; } equations { U 0.5; } }

// After (faster):
relaxationFactors { fields { p 0.3; } equations { U 0.7; } }
```

---

### Problem 2: Oscillating Residuals

**Symptoms:**
```
Iteration 50:  p residual = 2.3e-04
Iteration 51:  p residual = 8.1e-04  ← Jump up!
Iteration 52:  p residual = 1.9e-04
Iteration 53:  p residual = 9.5e-04  ← Oscillating!
```

**Cause:** Relaxation factors too aggressive

**Solution:**
```cpp
// Reduce relaxation factors
relaxationFactors
{
    fields
    {
        p       0.2;    // Was 0.5
    }
    equations
    {
        U       0.5;    // Was 0.7
        k       0.5;
        epsilon 0.5;
    }
}
```

---

### Problem 3: Stagnation (Residuals Flat)

**Symptoms:**
```
Iteration 100:  U residual = 1.2e-03
Iteration 150:  U residual = 1.2e-03  ← Stuck!
Iteration 200:  U residual = 1.2e-03
```

**Causes and fixes:**

1. **Turbulence model not converged**
   ```cpp
   // Check k and ε residuals
   // If not converged, increase relaxation:
   relaxationFactors
   {
       equations
       {
           k       0.5;    // Reduce from 0.7
           epsilon 0.5;
       }
   }
   ```

2. **Inconsistent boundary conditions**
   - Check inlet/outlet mass balance
   - Verify turbulent quantities (k, ε, ω) at inlet

3. **Need better linear solver**
   ```cpp
   // system/fvSolution
   solvers
   {
       p
       {
           solver          GAMG;      // Was PCG
           tolerance       1e-06;
           relTol          0.01;      // Stricter!
       }
   }
   ```

---

### Residual Targets: What Values to Use?

```cpp
// system/fvSolution
SIMPLE
{
    nNonOrthogonalCorrectors 1;
    residualControl
    {
        p       1e-05;   // Strict for pressure
        U       1e-04;   // Moderate for velocity
        k       1e-04;   // Moderate for turbulence
        epsilon 1e-04;   // Moderate
    }
}
```

**Guidelines:**
- **Engineering accuracy:** 1e-4 generally sufficient
- **Validation studies:** Use 1e-5 or 1e-6
- **Debugging phase:** Start at 1e-3, tighten later

---

### Monitoring Convergence in Real-Time

```bash
# Watch residuals while running
simpleFoam 2>&1 | grep "Initial residual"

# Or use pyFoam for plotting
pyFoamPlotRunner.py simpleFoam

# Output log shows:
# Time = 1
# smoothSolver:  Solving for Ux, Initial residual = 1.00000e+00, Final residual = 2.34567e-06, No Iterations 5
# GAMG:  Solving for p, Initial residual = 5.67890e-01, Final residual = 4.56789e-07, No Iterations 20
```

---

### When to Stop?

**Automatic (recommended):**
- Use `residualControl` in fvSolution
- Solver stops when all residuals below targets

**Manual:**
- Monitor log file
- Stop when residuals stabilize below acceptable threshold
- Verify physical quantities (lift, drag) are stable

**Example:**
```
Iteration 500:
U residual:  8.5e-05  < 1e-04 ✓
p residual:  2.1e-05  < 1e-04 ✓
k residual:  5.3e-05  < 1e-04 ✓
Cl = 0.45 ± 0.001  ✓ (stable)
→ CONVERGED!
```

---

## Under-Relaxation Settings

```cpp
// system/fvSolution
relaxationFactors
{
    fields
    {
        p       0.3;    // Pressure: conservative
    }
    equations
    {
        U       0.7;    // Velocity: can be higher
        k       0.7;
        epsilon 0.7;
    }
}
```

### Rules of Thumb

| Variable | High Re | Low Re | Notes |
|:---|:---|:---|:---|
| **p** | 0.2-0.3 | 0.5-0.7 | More conservative at high Re |
| **U** | 0.5-0.7 | 0.7-0.9 | Can be more aggressive |
| **k, ε** | 0.5-0.7 | 0.5-0.7 | Start moderate, adjust as needed |

**Adjustment strategy:**
1. Start with default values
2. If diverging → decrease by 20-30%
3. If converging slowly → increase by 10-20%

---

## Concept Check Questions

<details>
<summary><b>1. Why doesn't simpleFoam have `fvm::ddt(U)`?</b></summary>

**Steady-state means no time derivative!**

$$\cancelto{0}{\frac{\partial U}{\partial t}} + \nabla \cdot (UU) = -\nabla p + \nu \nabla^2 U$$

The `runTime.timeName()` in simpleFoam represents iteration number, not physical time.

**Contrast with icoFoam:**
```cpp
// icoFoam (transient):
fvm::ddt(U) + fvm::div(phi, U) == ...  // Time derivative included

// simpleFoam (steady):
fvm::div(phi, U) == ...                 // No time derivative
```
</details>

<details>
<summary><b>2. What does `turbulence->correct()` do?</b></summary>

For kEpsilon model:

1. **Calculate Production:** $G = \nu_t S^2$ (from strain rate)
2. **Solve k equation:** 
   $$\nabla \cdot (U k) - \nabla \cdot (\nu_{eff} \nabla k) = G - \epsilon$$
3. **Solve ε equation:**
   $$\nabla \cdot (U \epsilon) - \nabla \cdot (\nu_{eff} \nabla \epsilon) = C_1 \frac{\epsilon}{k} G - C_2 \frac{\epsilon^2}{k}$$
4. **Update νt:** $\nu_t = C_\mu \frac{k^2}{\epsilon}$

**See:** [03_kEpsilon_Model_Anatomy.md](03_kEpsilon_Model_Anatomy.md) for full implementation.
</details>

<details>
<summary><b>3. Why does SIMPLE require under-relaxation but PISO doesn't?</b></summary>

**PISO (icoFoam):**
- Uses multiple pressure corrections per time step
- Each correction progressively fixes non-linearity
- Small time steps → small changes → inherently stable

**SIMPLE (simpleFoam):**
- Uses single pressure correction per iteration
- Non-linearity not fully corrected
- Must under-relax to damp oscillations

**Trade-off:**
- PISO: Time-accurate but computationally expensive per time step
- SIMPLE: Faster per iteration but requires many iterations to converge
</details>

<details>
<summary><b>4. When should I use simpleFoam vs icoFoam?</b></summary>

**Use simpleFoam when:**
- You only need the final steady-state solution
- Flow is time-invariant or you care about time-averaged behavior
- Industrial applications: pumps, airfoils at fixed angle, pipe flow

**Use icoFoam when:**
- You need time-accurate transient behavior
- Flow physics depend on time evolution (vortex shedding, start-up)
- Studying unsteady phenomena: DNS, LES foundations

**Example:**
- Flow over cylinder at Re=100 → icoFoam (von Kármán vortex street)
- Pressure drop in pipe at Re=1e5 → simpleFoam (fully turbulent, steady)
</details>

---

## Key Takeaways

1. **SIMPLE Algorithm:** Designed for steady-state problems using pseudo-time iterations with under-relaxation for stability, unlike PISO which uses time-accurate transient advancement

2. **Under-Relaxation is Critical:** The `UEqn.relax()` and `p.relax()` calls prevent oscillation by blending new values with previous iteration values — the key difference from transient solvers

3. **Turbulence Integration:** simpleFoam adds RANS modeling through `turbulence->divDevReff()` which combines laminar and turbulent viscosity effects automatically

4. **Convergence Monitoring:** SIMPLE converges when residuals drop below targets (not when time advances), requiring careful monitoring of residual behavior and relaxation factors

5. **Configuration-Driven:** The `simpleControl` object reads `system/fvSolution` to control relaxation factors, residual targets, and non-orthogonal correctors

6. **Runtime Selection:** Turbulence models are selected at runtime via `constant/turbulenceProperties`, enabling solver flexibility without recompilation

---

## Hands-On Exercise

### Exercise: Compare Convergence with Different Relaxation Factors

**Objective:** Understand the impact of under-relaxation on SIMPLE convergence behavior

**Prerequisites:**
- OpenFOAM installation
- A simpleFoam test case (e.g., `tutorials/incompressible/simpleFoam/airfoil2D`)

**Tasks:**

#### Task 1: Baseline Run
1. Navigate to your test case
2. Check default relaxation factors in `system/fvSolution`:
   ```bash
   grep -A 10 "relaxationFactors" system/fvSolution
   ```
3. Run the solver and record convergence:
   ```bash
   simpleFoam 2>&1 | tee log.simpleFoam_baseline
   ```
4. Count iterations to convergence:
   ```bash
   grep "Final residual" log.simpleFoam_baseline | wc -l
   ```

#### Task 2: Aggressive Relaxation
1. Modify `system/fvSolution`:
   ```cpp
   relaxationFactors
   {
       fields
       {
           p       0.5;    // Increase from 0.3
       }
       equations
       {
           U       0.9;    // Increase from 0.7
           k       0.9;
           epsilon 0.9;
       }
   }
   ```
2. Clear previous results:
   ```bash
   foamCleanTutorials
   ```
3. Run again:
   ```bash
   simpleFoam 2>&1 | tee log.simpleFoam_aggressive
   ```
4. **Questions:**
   - Did it converge faster or slower?
   - Are residuals smooth or oscillating?
   - Check for divergence: `grep "diverg" log.simpleFoam_aggressive`

#### Task 3: Conservative Relaxation
1. Modify to very conservative values:
   ```cpp
   relaxationFactors
   {
       fields
       {
           p       0.1;    // Very conservative
       }
       equations
       {
           U       0.3;    // Very conservative
           k       0.3;
           epsilon 0.3;
       }
   }
   ```
2. Clear and run:
   ```bash
   foamCleanTutorials
   simpleFoam 2>&1 | tee log.simpleFoam_conservative
   ```
3. **Questions:**
   - Did it converge?
   - How many iterations compared to baseline?
   - Is convergence monotonic and smooth?

#### Task 4: Plot Comparison
1. Extract residuals from each log:
   ```bash
   # For each log file
   grep "Solving for Ux" log.simpleFoam_* | awk '{print $7}' > residuals_baseline.txt
   grep "Solving for Ux" log.simpleFoam_aggressive | awk '{print $7}' > residuals_aggressive.txt
   grep "Solving for Ux" log.simpleFoam_conservative | awk '{print $7}' > residuals_conservative.txt
   ```
2. Plot (Python example):
   ```python
   import matplotlib.pyplot as plt
   
   with open('residuals_baseline.txt') as f:
       base = [float(line) for line in f]
   
   plt.semilogy(base, label='Baseline (p=0.3, U=0.7)')
   # Plot others...
   plt.xlabel('Iteration')
   plt.ylabel('Residual')
   plt.legend()
   plt.savefig('convergence_comparison.png')
   ```

#### Task 5: Analysis Questions

1. **Convergence Speed:** Which settings converged fastest? Slowest?

2. **Stability:** Did any settings cause oscillation or divergence?

3. **Optimal Settings:** Based on your results, what relaxation factors would you recommend for this case?

4. **Physics Dependence:** How might optimal values change for:
   - Higher Reynolds number?
   - More complex geometry?
   - Poorer mesh quality?

---

## Next Steps

### Continue Learning

1. **Next Document:** [03_kEpsilon_Model_Anatomy.md](03_kEpsilon_Model_Anatomy.md)
   - Deep dive into turbulence model implementation
   - Understanding k-ε transport equations
   - How `divDevReff()` is constructed

2. **Related Topics:**
   - [Module 06: Advanced Physics](../../../MODULE_06_ADVANCED_PHYSICS/) - Multiphase and coupled physics
   - [Module 08: Testing and Validation](../../../MODULE_08_TESTING_VALIDATION/) - Verification methods for steady-state solvers

3. **Practical Application:**
   - Try different turbulence models (kOmegaSST, SpalartAllmaras)
   - Experiment with `fvSolution` settings for your own cases
   - Compare simpleFoam results with transient icoFoam for same geometry

### Further Reading

- **OpenFOAM User Guide:** SIMPLE algorithm theory and implementation
- **CFD Online:** SIMPLE vs PISO comparison forums
- **Ferziger & Perić:** Computational Methods for Fluid Dynamics (Chapter 7: Pressure-Velocity Coupling)

---

## Related Files Cross-Reference

| This Document | References | Referenced By |
|:---|:---|:---|
| **simpleFoam Walkthrough** | [01_icoFoam_Walkthrough.md](01_icoFoam_Walkthrough.md) - PISO algorithm, pressure-velocity coupling | [03_kEpsilon_Model_Anatomy.md](03_kEpsilon_Model_Anatomy.md) - Turbulence model details |
| | [Module 03: OpenFOAM Programming](../../../MODULE_03_OPENFOAM_PROGRAMMING/) - Solver basics, compile_commands.json | [Module 06: Advanced Physics](../../../MODULE_06_ADVANCED_PHYSICS/) - RANS applications |
| | [Module 08: Testing](../../../MODULE_08_TESTING_VALIDATION/) - Verification methods | [Module 10: CFD Engine Dev](../../../MODULE_10_CFD_ENGINE_DEVELOPMENT/) - Custom solver development |