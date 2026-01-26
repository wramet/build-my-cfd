# Common Pitfalls & Debugging in Vector Calculus

![[unstable_equation_pitfall.png]]
`A tightrope walker representing the solver trying to balance on a thin wire labeled "fvc::laplacian" while being buffeted by wind (numerical instability). A sturdy bridge labeled "fvm::laplacian" is visible right next to them, representing stability, scientific textbook diagram, clean vector line art, white background, high definition, flat design, educational infographic --ar 16:9`

> [!TIP] 🎯 Why Understanding These Pitfalls Matters
> Understanding these common pitfalls will **save you debugging time** and help you **develop stable solvers**. These errors typically stem from misunderstandings about:
> - **Explicit (fvc) vs Implicit (fvm)**: Affects stability and time step size
> - **Dimensional Consistency**: OpenFOAM has automatic unit checking
> - **Mesh Quality**: Mesh quality affects gradient/div/curl calculation accuracy
> - **Type System**: Correct use of Scalar/Vector/Tensor
>
> These tools are located in **src/finiteVolume/** and are used in **solver files (.C files)** which are essential for solver development and boundary conditions

Vector calculus on meshes has technical details that often create problems for solver developers. This section compiles common issues, solutions, and best practices.

---

## 🎯 Learning Objectives

By the end of this section, you will be able to:

1. **Identify Stability Issues**: Recognize when explicit discretization causes solver instability
2. **Apply Dimensional Analysis**: Use OpenFOAM's dimensional checking to catch physics errors
3. **Diagnose Mesh Problems**: Understand how mesh quality affects calculus operations
4. **Debug Type Errors**: Resolve scalar/vector/tensor mismatches effectively
5. **Select Appropriate Schemes**: Match numerical schemes to mesh quality and physics
6. **Optimize Time Step Selection**: Apply CFL-based adaptive time stepping strategies

---

## 🔥 1. Confusion Between `fvc` and `fvm`

> [!NOTE] **📂 OpenFOAM Context**
> This topic relates to **Domain B: Numerics & Linear Algebra** and **Domain E: Coding/Customization**
> - **Solver files**: `applications/solvers/` (e.g., `simpleFoam.C`, `myCustomSolver.C`)
> - **Keywords**: `fvc::` (Explicit), `fvm::` (Implicit), `fvScalarMatrix`, `solve()`
> - **Impact**: Using `fvc` instead of `fvm` makes the solver **unstable** and requires very small time steps
> - **Location**: Main equation loop in solvers
>
> In OpenFOAM, you will see usage in:
> - `src/finiteVolume/fvMesh/fvMesh.H` - Mesh for calculations
> - `src/finiteVolume/fvm/fvm.H` - Implicit operators
> - `src/finiteVolume/fvc/fvc.H` - Explicit operators

### The Core Problem

> [!WARNING] ⚠️ Most Common Error
> Using `fvc::laplacian` in equations where `fvm::laplacian` should be used for terms being solved

### Impact

**When using `fvc::laplacian` incorrectly:**
- Program runs but becomes **highly unstable**
- Requires very small time steps (CFL condition)
- Diffusion term calculated explicitly
- May cause solver explosion

### Stability Condition

For Explicit Laplacian:
$$\Delta t \leq \frac{\Delta x^2}{2\Gamma}$$

Where:
-1$\Delta t1= time step size
-1$\Delta x1= mesh cell size
-1$\Gamma1= diffusion coefficient

### Correct Practices

```cpp
// ❌ WRONG: Using fvc for equation terms being solved
// Using fvc for diffusion term creates explicit scheme - very unstable!
fvScalarMatrix TEqn
(
    fvm::ddt(T) + fvc::laplacian(DT, T) == source
);

// ✅ CORRECT: Use fvm for diffusion terms
// Implicit treatment of diffusion for unconditional stability
fvScalarMatrix TEqn
(
    fvm::ddt(T) + fvm::laplacian(DT, T) == source  // Stable
);

// ✅ CORRECT: Use fvc for source terms or post-processing
// Explicit evaluation is acceptable for known fields
volScalarField diffusionSource = fvc::laplacian(DT, T);  // Correct
```

**Source:** 📂 `applications/solvers/heatTransfer/chtMultiRegionFoam/solidThermophysicalModels/noTherm/solidNoTherm.C`

**Explanation:**
- **Source**: Code example shows `fvm::laplacian` usage in heat transfer solver
- **Key Point**: Choice between `fvc` (explicit) and `fvm` (implicit) significantly impacts solver stability. Diffusion terms that are part of unknown variables should use `fvm` for implicit schemes without time step limitations
- **Concepts**: 
  - **Explicit (fvc)**: Calculated from previous time step, strict stability conditions
  - **Implicit (fvm)**: Calculated from current time step, no time limit but requires solving equation system
  - **CFL Condition**: Stability condition for explicit schemes

### Basic Rules

> [!TIP] 💡 Simple Rules
> - If a term is **the solution you seek** (e.g.,1$T$,1$p$,1$U$), always use `fvm`
> - If a term is **known value** or used as source term, use `fvc`

---

## ⏱️ 2. Time Step Selection Best Practices

> [!NOTE] **📂 OpenFOAM Context**
> This topic relates to **Domain C: Simulation Control** and **Domain B: Numerics**
> - **Files**: `system/controlDict`, `system/fvSchemes`
> - **Keywords**: `deltaT`, `maxCo`, `adjustTimeStep`, `maxAlphaCo`
> - **Commands**: `foamListTimes`, `probeLocations`
> - **Impact**: Proper time step selection balances computational cost with accuracy
>
> In OpenFOAM, you will see usage in:
> - `src/ODE/ODESolvers/` - Time integration schemes
> - `src/finiteVolume/fvMesh/fvMesh.H` - CFL calculation methods

### CFL Number Guidelines

The Courant-Friedrichs-Lewy (CFL) number determines numerical stability:

$$Co = \frac{|U| \Delta t}{\Delta x}$$

| Scheme Type | Max CFL | Stability | Accuracy |
|:---|:---|:---|:---|
| **Explicit** | < 1.0 | Conditionally stable | High |
| **Implicit** | > 10-100 | Unconditionally stable | Moderate |
| **Semi-Implicit** | < 5-10 | Good stability | Good |

### Time Step Control Strategies

```cpp
// In system/controlDict

// Strategy 1: Fixed time step (simple cases)
application     simpleFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         1000;
deltaT          0.001;

// Strategy 2: Automatic time step adjustment (recommended)
adjustTimeStep  yes;
maxCo           0.9;          // Max Courant number
maxDeltaT       1;            // Upper limit on time step

// Strategy 3: Multi-phase flows
adjustTimeStep  yes;
maxCo           0.5;          // More restrictive for multiphase
maxAlphaCo      0.5;          // Phase fraction limit

// Strategy 4: Transient vs Steady-state
// Transient: strict CFL control
// Steady-state: can use larger steps with under-relaxation
```

### Practical Time Step Selection

```cpp
// Method 1: Calculate maximum stable time step
scalar maxDeltaT = GREAT;
const surfaceScalarField& magPhi = mag(phi);

// CFL-based time step calculation
scalar CoNum = max(magPhi/mesh.magSf()/mesh.deltaCoeffs()).value()*runTime.deltaTValue();

if (CoNum > 0.5)
{
    maxDeltaT = min(maxDeltaT, 0.5/CoNum*runTime.deltaTValue());
}

// Method 2: Diffusion-based limit
// For explicit diffusion: Δt < Δx²/(2Γ)
scalar diffDeltaT = 0.5 * sqr(min(mesh.V().field())) 
                  / max(DT.primitiveField());
maxDeltaT = min(maxDeltaT, diffDeltaT);
```

**Source:** 📂 `applications/solvers/multiphase/interFoam/interFoam.C`

### Common Time Step Issues

| Symptom | Cause | Solution |
|:---|:---|:---|
| **Solver diverges immediately** | Time step too large for explicit scheme | Reduce `deltaT` or switch to implicit |
| **Very slow convergence** | Time step too small | Increase `deltaT` or use local time stepping |
| **Oscillating results** | Time step near stability limit | Reduce `deltaT` by factor of 2 |
| **CFL varies wildly** | Poor mesh quality | Improve mesh or use adaptive time stepping |
| **Blow-up at boundaries** | Time step too large for boundary layers | Use smaller `deltaT` or refine boundary mesh |

### Adaptive Time Step Best Practices

```cpp
// Recommended controlDict settings for transient simulations
application     pimpleFoam;

adjustTimeStep  yes;
maxCo           0.9;           // Velocity-based limit
maxAlphaCo      0.9;           // Volume fraction limit (multiphase)
maxDeltaT       1;             // Maximum allowed step
minDeltaT       1e-10;         // Minimum allowed step

// Optional: add time step acceleration for steady-state
// Local time stepping for faster convergence
```

### Time Step Selection Workflow

```cpp
// Recommended workflow for new simulations:

// Step 1: Start with very conservative time step
deltaT 1e-5;

// Step 2: Run for few iterations and monitor maxCo
// Check log file: "Max Courant Number = ..."

// Step 3: If Co < 0.3, increase deltaT gradually
// If Co > 0.7, reduce deltaT

// Step 4: Enable adaptive stepping once stable
adjustTimeStep yes;
maxCo 0.9;
```

---

## 📏 3. Dimension Mismatches

> [!NOTE] **📂 OpenFOAM Context**
> This topic relates to **Domain A: Physics & Fields** and **Domain E: Coding/Customization**
> - **Files**: `applications/solvers/` and `src/finiteVolume/`
> - **Keywords**: `dimensionSet`, `dimensions()`, `dimPressure`, `dimDensity`, `dimAcceleration`
> - **Classes**: `dimensionedScalar`, `dimensionedVector`, `GeometricField`
> - **Location**: Physics calculation functions (e.g., force, acceleration calculations)
> - **Debugging**: Use `Info << field.dimensions() << endl;` to check units
>
> In OpenFOAM, you will see usage in:
> - `src/OpenFOAM/dimensionSet/dimensionSet.H` - Unit checking system
> - `src/OpenFOAM/dimensionedTypes/` - Types with units
> - `src/finiteVolume/fields/GeometricFields/` - Fields with unit checking

### Problem

Forgetting to divide by density ($\rho$) when calculating acceleration from pressure gradient

### Correction Example

```cpp
// ❌ WRONG: Result is [Force/Volume] not [Acceleration]
// fvc::grad(p) has units [Pa/m] = [kg/(m²·s²)]
volVectorField acc = -fvc::grad(p);

// ✅ CORRECT: Result is [Acceleration] = [m/s²]
// p/rho has units [m²/s²], gradient has [m/s²]
volVectorField acc = -fvc::grad(p/rho);

// ✅ CORRECT: Alternative equivalent form
volVectorField acc = -fvc::grad(p) / rho;
```

**Source:** 📂 `applications/solvers/incompressible/simpleFoam/createFields.H`

### Unit Checking

```cpp
// Check field dimensions
Info << "Gradient dimensions: " << fvc::grad(p).dimensions() << endl;
Info << "Acceleration dimensions: " << acc.dimensions() << endl;
```

### Correct Unit Table

| Operation | Input Units | Output Units | Usage |
|:---|:---|:---|:---|
| `fvc::grad(p)` | `[kPa/m]` | `[kPa/m]` | Force per volume |
| `fvc::grad(p/rho)` | `[m²/s²]/m` | `[m/s²]` | Acceleration |
| `fvc::grad(T)` | `[K/m]` | `[K/m]` | Temperature gradient |
| `fvc::laplacian(DT, T)` | `[m²/s]·[K/m²]` | `[K/s]` | Rate of change |

---

## 🕸️ 4. Mesh Quality Issues

> [!NOTE] **📂 OpenFOAM Context**
> This topic relates to **Domain D: Meshing** and **Domain B: Numerics**
> - **Check command**: `checkMesh` in terminal
> - **Mesh files**: `constant/polyMesh/points`, `constant/polyMesh/faces`
> - **Scheme file**: `system/fvSchemes` → `laplacianSchemes`, `gradSchemes`
> - **Keywords**: `non-orthogonality`, `skewness`, `aspectRatio`, `corrected`, `limited`
> - **Check**: `checkMesh -allGeometry -allTopology`
> - **Impact**: Poor mesh causes high error in gradient/laplacian calculations
>
> In OpenFOAM, you will see usage in:
> - `src/meshes/` - Mesh data structures
> - `src/finiteVolume/fvMesh/fvMesh.H` - Mesh access
> - `src/finiteVolume/interpolation/` - Interpolation on meshes

### Non-orthogonality

**Problem**: Calculating Laplacian on meshes with high skewness

**Result**: Cell face values may be incorrect, causing solver divergence

### Problem Diagnosis

```cpp
// Check mesh quality metrics
const polyMesh& mesh = ...;

scalar maxNonOrtho = 0.0;
scalar maxSkewness = 0.0;

forAll(mesh.faceAreas(), faceI)
{
    // Check non-orthogonality
    scalar nonOrtho = ...;
    maxNonOrtho = max(maxNonOrtho, nonOrtho);

    // Check skewness
    scalar skew = ...;
    maxSkewness = max(maxSkewness, skew);
}

Info << "Max non-orthogonality: " << maxNonOrtho << endl;
Info << "Max skewness: " << maxSkewness << endl;
```

**Source:** 📂 `applications/utilities/mesh/generation/checkMesh/checkMesh.C`

### Solution: Select Appropriate Scheme

Choose schemes with non-orthogonality correction in `system/fvSchemes`:

```cpp
// Laplacian Scheme selection for mesh quality
laplacianSchemes
{
    // Basic (high quality meshes only)
    default         Gauss linear;

    // Non-orthogonality correction (recommended)
    default         Gauss linear corrected;

    // Severe non-orthogonality correction
    default         Gauss linear limited 0.5;

    // High skewness
    default         Gauss linear skewCorrected;
}
```

### Scheme Comparison

| Scheme | Stability | Accuracy | Usage |
|:---|:---|:---|:---|
| `Gauss linear` | Moderate | Good | Orthogonal meshes |
| `Gauss linear corrected` | High | Very Good | Slightly skewed |
| `Gauss linear limited` | Very High | Moderate | Highly skewed |
| `Gauss leastSquares` | High | High | Unstructured meshes |

### Mesh Quality Checking

```bash
# Use checkMesh to verify mesh quality
checkMesh -allGeometry -allTopology

# Expected results:
# - Max non-orthogonality < 70°
# - Max skewness < 0.8
# - Max aspect ratio < 1000
```

### Mesh Quality Troubleshooting Examples

#### Example 1: High Non-orthogonality

**Symptom**: Warnings like "Max non-orthogonality = 75" and solver divergence

```cpp
// Diagnostic output from log.simpleFoam:
// --> FOAM Warning : 
//     From function virtual void Foam::fv::gaussLaplacianScheme::corrected...
//     Max non-orthogonality 75 detected.

// Solution 1: Improve mesh
// In snappyHexMeshDict:
// Add more refinement layers
// Increase nSmoothPatch to improve cell quality

// Solution 2: Use corrected scheme
// In system/fvSchemes:
laplacianSchemes
{
    default Gauss linear corrected 0.33;  // Limited correction
}

// Solution 3: Add non-orthogonal correctors
// In system/fvSolution:
simple
{
    nNonOrthogonalCorrectors 3;  // Iterative correction
}
```

#### Example 2: High Skewness

**Symptom**: "Max skewness = 0.95" and unphysical results

```cpp
// Solution: Use skew-corrected schemes
// In system/fvSchemes:
laplacianSchemes
{
    default Gauss linear skewCorrected;
}

// Or use least squares (mesh-independent)
gradSchemes
{
    default leastSquares;  // Works on any mesh
}
```

#### Example 3: High Aspect Ratio

**Symptom**: "Max aspect ratio = 5000" and slow convergence

```cpp
// Solution: Use anisotropic diffusion
laplacianSchemes
{
    // For boundary layers with high aspect ratio
    laplacian(nu,U) Gauss linear corrected 0.5;
    
    // For isotropic regions
    laplacian(k,T) Gauss linear;
}

// Consider improving mesh in boundary layers
// Add prism layers instead of stretching hex cells
```

#### Example 4: Gradient Calculation Issues

**Symptom**: Spurious oscillations near cell size changes

```cpp
// Problem: Default Gauss linear scheme causes issues on non-uniform mesh

// Solution: Use cell-limited scheme
gradSchemes
{
    default Gauss linear;
    grad(p) cellLimited Gauss linear 1;
    grad(U) cellLimited Gauss linear 1;
}

// Or use least squares for better handling
gradSchemes
{
    default leastSquares;
}
```

#### Example 5: Divergence Calculation on Bad Mesh

**Symptom**: "div(phi,U) failed convergence" warnings

```cpp
// Solution: Use upwind or limited schemes
divSchemes
{
    default         Gauss upwind;
    div(phi,U)      Gauss limitedLinearV 1;
    div(phi,k)      Gauss limitedLinear 1;
    div(phi,epsilon) Gauss limitedLinear 1;
}
```

---

## 🔢 5. Type Mismatches

> [!NOTE] **📂 OpenFOAM Context**
> This topic relates to **Domain E: Coding/Customization**
> - **Files**: C++ solver source code (`applications/solvers/*.C`)
> - **Keywords**: `volScalarField`, `volVectorField`, `volTensorField`, `surfaceScalarField`
> - **Operators**: `fvc::div()`, `fvc::curl()`, `fvc::grad()`, `fvc::laplacian()`
> - **Compile Error**: Type errors caught at compile-time
> - **Debugging**: Read compiler error messages carefully
>
> In OpenFOAM, you will see usage in:
> - `src/finiteVolume/fields/volFields/` - Volume field types
> - `src/finiteVolume/fields/surfaceFields/` - Surface field types
> - `src/finiteVolume/fvc/fvcDtdt.C` - Divergence operators
> - `src/finiteVolume/fvc/fvcCurl.C` - Curl operators

### Common Errors

| Symptom | Cause | Fix |
|:---|:---|:---|
| `no match for fvc::div(volScalarField)` | Divergence requires Vector | Check parameter is Vector |
| `cannot convert fvMatrix to GeometricField` | Trying to store `fvm` result in field variable | Use `fvc` for immediate values |
| `no match for fvc::curl(scalarField)` | Curl only works on vector fields | Check field type |

### Corrections and Correct Examples

```cpp
// ❌ ERROR: Divergence of scalar is invalid
volScalarField wrong = fvc::div(T);

// ✅ CORRECT: Divergence of vector
volVectorField U(mesh);
volScalarField divU = fvc::div(U);

// ❌ ERROR: Trying to convert fvMatrix to Field
volScalarField wrong = fvm::laplacian(DT, T);

// ✅ CORRECT: Use fvc for immediate values
volScalarField laplacianT = fvc::laplacian(DT, T);

// ✅ CORRECT: Use fvm for solving equations
fvScalarMatrix TEqn(fvm::laplacian(DT, T));
TEqn.solve();

// ❌ ERROR: Curl of scalar
volVectorField wrong = fvc::curl(p);

// ✅ CORRECT: Curl of vector
volVectorField vorticity = fvc::curl(U);
```

**Source:** 📂 `applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/ThermalPhaseChangePhaseSystem/ThermalPhaseChangePhaseSystem.C`

### Compile-time Type Checking

```cpp
// Check types with static_assert (C++11)
static_assert(
    std::is_same<decltype(fvc::grad(p)), volVectorField>::value,
    "Gradient of scalar must be vector field"
);

// Use decltype for automatic type deduction
auto gradP = fvc::grad(p);  // gradP is volVectorField
```

---

## 📊 6. Summary of Diagnostic Table

> [!NOTE] **📂 OpenFOAM Context**
> This topic relates to **Domain B: Numerics & Linear Algebra** and **Domain C: Simulation Control**
> - **Files**: `system/fvSchemes`, `system/fvSolution`, `system/controlDict`
> - **Keywords**: `residuals`, `tolerances`, `solvers`, `schemes`, `deltaT`, `maxCo`
> - **Log Files**: `log.simpleFoam`, `log.mySolver` - check results
> - **Debugging**: Add `Info <<` statements in solver code
> - **Checking**: Monitor residuals in log files

### Symptom and Solution Table

| 🚩 Symptom | 🔧 Possible Cause | 💡 Solution |
|:---|:---|:---|
| **Solver diverges immediately** | Using `fvc` instead of `fvm` for main terms | Change main terms from `fvc` to `fvm` |
| **`Dimension mismatch`** | Field units inconsistent | Divide by appropriate variable (e.g.,1$\rho$) |
| **Residuals not decreasing** | Check non-orthogonal correction in `fvSchemes` | Add `corrected` or `limited` to laplacianSchemes |
| **Compile Error: `no match`** | Check data type (Scalar/Vector/Tensor) | Verify correct operator for field type |
| **Abnormal results at boundaries** | Incorrect boundary conditions | Check boundary conditions in `0/` directory |
| **CFL > 1 but solver stable** | Explicit scheme in wrong place | Change to implicit scheme for convection/diffusion |
| **Time step must be very small** | Using explicit diffusion | Change from `fvc::laplacian` to `fvm::laplacian` |
| **Mesh quality warning** | High mesh skewness or non-orthogonality | Improve mesh or change scheme |
| **Oscillating residuals** | Time step too close to stability limit | Reduce `deltaT` by factor of 2 |
| **Spurious oscillations** | Gradient scheme too high order | Use `limited` or `cellLimited` schemes |
| **Slow convergence in boundary layers** | High aspect ratio cells | Use anisotropic schemes or improve mesh |

---

## 🧪 7. Debugging Tools

> [!NOTE] **📂 OpenFOAM Context**
> This topic relates to **Domain B: Numerics & Linear Algebra** and **Domain E: Coding/Customization**
> - **Files**: Solver source code (`applications/solvers/*.C`)
> - **Keywords**: `fvc::div()`, `fvc::grad()`, `Info`, `mesh.V()`, `sum()`, `max()`, `mag()`
> - **Classes**: `fvMesh`, `GeometricField`, `dimensionSet`
> - **Debugging Tools**: `Info <<`, `WarningIn`, `FatalErrorIn`
> - **Function Objects**: Can use `system/controlDict` to add monitoring

### Conservation Check

```cpp
// Check mass balance for incompressible flow
volScalarField continuityError = fvc::div(U);

scalar maxContinuityError = max(mag(continuityError));
scalar sumContinuityError = sum(continuityError * mesh.V());

Info << "Max continuity error: " << maxContinuityError << endl;
Info << "Sum continuity error: " << sumContinuityError << endl;

// Value should be near machine precision (~1e-10)
```

**Source:** 📂 `applications/solvers/incompressible/pisoFoam/pisoFoam.C`

### Boundary Check

```cpp
// Check boundary values after gradient calculation
volVectorField gradP = fvc::grad(p);

forAll(gradP.boundaryField(), patchi)
{
    Info << "Patch " << mesh.boundaryMesh()[patchi].name() << ":" << endl;
    Info << "  Gradient: " << gradP.boundaryField()[patchi] << endl;
}
```

### Energy Balance Check

```cpp
// For heat conduction problems
volScalarField heatGen = fvc::laplacian(kappa, T);  // [W/m³]
scalar totalHeatGen = sum(heatGen * mesh.V());

Info << "Total heat generation: " << totalHeatGen << " W" << endl;
```

### CFL Number Monitoring

```cpp
// Calculate and monitor Courant number
surfaceScalarField phiU = phi;
scalarField CoNum = mag(phiU)/(mesh.magSf()*mesh.deltaCoeffs())*runTime.deltaTValue();

scalar maxCo = max(CoNum);
scalar meanCo = average(CoNum);

Info << "Max Courant Number = " << maxCo << endl;
Info << "Mean Courant Number = " << meanCo << endl;
```

---

## ✅ 8. Best Practices

> [!NOTE] **📂 OpenFOAM Context**
> This topic relates to **Domain B: Numerics & Linear Algebra** and **Domain C: Simulation Control**
> - **Files**: `system/fvSchemes`, `system/fvSolution`, `system/controlDict`
> - **Keywords**: `gradSchemes`, `divSchemes`, `laplacianSchemes`, `interpolationSchemes`, `snGradSchemes`
> - **Solver Settings**: `solvers` dictionary in `fvSolution`
> - **Time Control**: `deltaT`, `maxCo` in `controlDict`
> - **Best Practice**: Start with most stable scheme, then increase accuracy

### Equation Writing

> [!INFO] 📋 Checklist for Writing Equations
> 1. Check each term:
>    - "Need stability (Implicit)" or "Need numerical value (Explicit)"
> 2. Choose correct namespace from start (`fvm` vs `fvc`)
> 3. Check unit of each term
> 4. Check data type (Scalar vs Vector vs Tensor)
> 5. Test on high quality mesh first

### Numerical Scheme Selection

```cpp
// In system/fvSchemes

gradSchemes
{
    default         Gauss linear;           // General
    grad(p)         leastSquares;           // Non-uniform mesh
}

divSchemes
{
    default         Gauss upwind;           // High stability
    div(phi,U)      Gauss linearUpwindV grad(U);  // Higher order
    div(phi,T)      Gauss limitedLinear 1;  // Balanced
}

laplacianSchemes
{
    default         Gauss linear corrected; // Non-orthogonality correction
}
```

### Pre-run Checks

```bash
# 1. Check mesh
checkMesh

# 2. Check initial conditions
foamListTimes

# 3. Test with small time steps first
# In controlDict: deltaT 1e-5;

# 4. Add debugging output
# In solver: Info << "Variable: " << variable << endl;
```

### Solver Development Workflow

```cpp
// Recommended workflow for new solver development:

// Step 1: Write equation with all implicit terms
fvScalarMatrix TEqn
(
    fvm::ddt(T) + fvm::div(phi, T) - fvm::laplacian(DT, T) == source
);

// Step 2: Test with first-order schemes (most stable)
divSchemes { default Gauss upwind; }

// Step 3: Verify conservation
Info << "Sum T: " << sum(T * mesh.V()) << endl;

// Step 4: Gradually increase scheme order
divSchemes { div(phi,T) Gauss limitedLinear 1; }

// Step 5: Optimize time step
adjustTimeStep yes;
maxCo 0.9;
```

---

## 🔄 9. Comparison fvc vs fvm

> [!NOTE] **📂 OpenFOAM Context**
> This topic relates to **Domain B: Numerics & Linear Algebra** and **Domain E: Coding/Customization**
> - **Files**: Solver source code (`applications/solvers/*.C`)
> - **Namespaces**: `fvc::` (finite volume calculus), `fvm::` (finite volume method)
> - **Return Types**: `fvc` returns `GeometricField`, `fvm` returns `fvMatrix`
> - **Usage**: `fvm` for implicit discretization (builds matrix), `fvc` for explicit evaluation

### Summary of Differences

| Factor | `fvc::` (Explicit) | `fvm::` (Implicit) |
|:---|:---|:---|
| **Stability** | Time step limited | Unconditionally stable |
| **Accuracy** | Can be higher order | Usually first/second order |
| **Computational Cost** | Low per iteration | Higher per iteration |
| **Memory** | Less storage | Requires matrix storage |
| **Convergence** | May need multiple iterations | Fewer iterations for steady state |
| **Complexity** | Simple | Complex |
| **Result** | `GeometricField` | `fvMatrix` |

### Usage Guidelines

```cpp
// Use fvm:: for:
fvm::ddt(T)           // Temporal derivatives - always implicit
fvm::div(phi, T)      // Convection terms - implicit for stability
fvm::laplacian(DT, T) // Diffusion terms - implicit required

// Use fvc:: for:
fvc::grad(p)          // Pressure gradients - explicit evaluation
fvc::div(U)           // Divergence checks - post-processing
fvc::curl(U)          // Vorticity calculations - derived quantity
fvc::interpolate(U)   // Face interpolations - geometric operation
```

**Source:** 📂 `applications/solvers/heatTransfer/heatFoam/heatFoam.C`

---

## 🎯 10. Practical Application: Case Studies

> [!NOTE] **📂 OpenFOAM Context**
> This topic relates to **Domain E: Coding/Customization** and **Domain B: Numerics & Linear Algebra**
> - **Files**: Custom solver code (e.g., `myCustomSolver.C` in `applications/solvers/`)
> - **Workflow**: Edit solver code → compile (`wmake`) → run simulation
> - **Keywords**: `fvScalarMatrix`, `solve()`, `fvm::`, `fvc::`, `mag()`, `dimensionedScalar`

### Case 1: Unstable Energy Equation

**Problem**: Energy equation diverges immediately on run

```cpp
// ❌ PROBLEMATIC
fvScalarMatrix TEqn
(
    fvm::ddt(T) + fvc::div(phi, T) - fvc::laplacian(DT, T) == source
);
```

**Diagnosis**:
- Convection: `fvc::div` (Explicit, conditionally stable)
- Diffusion: `fvc::laplacian` (Explicit, very restrictive time step)

**Solution**:

```cpp
// ✅ CORRECT
fvScalarMatrix TEqn
(
    fvm::ddt(T) + fvm::div(phi, T) - fvm::laplacian(DT, T) == source
);
```

### Case 2: Incorrect Vorticity Calculation

**Problem**: Need to calculate vorticity magnitude

```cpp
// ❌ ERROR
volScalarField vorticity = fvc::curl(U);  // Type mismatch!

// ✅ CORRECT
volVectorField vorticityVec = fvc::curl(U);
volScalarField vorticityMag = mag(vorticityVec);
```

### Case 3: Gradient with Wrong Units

**Problem**: Calculate buoyancy force but get abnormal results

```cpp
// ❌ WRONG UNITS
volVectorField F_buoyancy = fvc::grad(p) * g;  // [Force/Volume] * [Acceleration]

// ✅ CORRECT
volVectorField F_buoyancy = (rho - rhoRef) * g;  // [Mass/Volume] * [Acceleration]
```

**Source:** 📂 `applications/solvers/multiphase/multiphaseEulerFoam/multiphaseCompressibleMomentumTransportModels/kineticTheoryModels/kineticTheoryModel/kineticTheoryModel.C`

### Case 4: Time Step Instability

**Problem**: Solver runs for 100 iterations then explodes

```cpp
// Diagnosis: Check log file
// Log shows: Max Courant Number gradually increasing to 1.2

// Solution 1: Enable adaptive time stepping
adjustTimeStep yes;
maxCo 0.9;

// Solution 2: Add time step damping
maxDeltaT 0.5;  // Limit maximum step size

// Solution 3: Use more stable schemes
divSchemes { default Gauss upwind; }
```

### Case 5: Non-orthogonal Mesh Instability

**Problem**: Residuals oscillate on complex geometry

```cpp
// Diagnosis: checkMesh shows max non-orthogonality = 78°

// Solution: Add non-orthogonal correctors
simple
{
    nNonOrthogonalCorrectors 3;
}

// And use corrected scheme
laplacianSchemes
{
    default Gauss linear corrected;
}
```

---

## 📚 11. Summary

> [!NOTE] **📂 OpenFOAM Context - Integration Overview**
> This topic integrates all OpenFOAM Domains:
> - **Domain A (Physics)**: Calculating gradient/div/curl of physics fields in `0/` directory
> - **Domain B (Numerics)**: Selecting schemes in `system/fvSchemes` and solvers in `system/fvSolution`
> - **Domain C (Control)**: Setting time step and write interval in `system/controlDict`
> - **Domain D (Meshing)**: Mesh quality affecting calculus operations accuracy
> - **Domain E (Coding)**: Writing custom solver/boundary conditions in `src/` and `applications/solvers/`
>
> **Application**: When writing a new solver, you will use:
> - `fvm::` for main equation terms (implicit)
> - `fvc::` for source terms and post-processing (explicit)
> - Check dimensions with `field.dimensions()`
> - Check mesh quality with `checkMesh`
> - Select appropriate numerical schemes for mesh quality

Using vector calculus in OpenFOAM requires deep understanding of:

1. **Difference between Explicit (`fvc::`) and Implicit (`fvm::`)**
   - Explicit: For source terms and post-processing
   - Implicit: For unknown terms in equations

2. **Dimensional and Type Consistency**
   - Always check units
   - Check Scalar vs Vector vs Tensor

3. **Impact of Mesh Quality**
   - Non-orthogonality requires corrected schemes
   - High skewness requires limited schemes

4. **Appropriate Numerical Scheme Selection**
   - Balance accuracy and stability
   - Adjust to mesh quality

5. **Time Step Selection**
   - CFL number control for transient simulations
   - Adaptive time stepping for robustness
   - Diffusion-based limits for explicit schemes

6. **Systematic Debugging Workflow**
   - Check mesh quality first
   - Verify dimensional consistency
   - Validate field types
   - Select appropriate schemes
   - Monitor CFL numbers and residuals

> [!TIP] 🎯 Remember: When writing new solvers, start with most stable schemes, then gradually increase accuracy after equations work correctly

---

**Avoiding these errors will save debugging time and make your solver work stably and correctly**

---

## 🧠 Concept Check

<details>
<summary><b>1. Why does using `fvc::laplacian` instead of `fvm::laplacian` in diffusion term make solver unstable?</b></summary>

**`fvc::laplacian`** is **explicit** → calculated from **previous time step** values

Problem:
- Must follow **Von Neumann stability:**1$\Delta t \leq \frac{\Delta x^2}{2\Gamma}$
- For fine mesh (small Δx) → **time step must be very small**
- If time step too large → **solver diverges**

**Solution:** Use `fvm::laplacian` which is unconditionally stable

</details>

<details>
<summary><b>2. If `fvc::grad(p)` has units [Pa/m], why can't it be directly used as acceleration?</b></summary>

**Dimensional analysis:**
- `fvc::grad(p)` has units1$[Pa/m] = [kg/(m^2 \cdot s^2)]1= **Force per unit volume**
- **Acceleration** has units1$[m/s^2]$

**Solution:** Must divide by density1$\rho$:
```cpp
volVectorField acc = -fvc::grad(p) / rho;  // Units: [m/s²]
```

</details>

<details>
<summary><b>3. When `checkMesh` shows non-orthogonality > 70°, what should you do?</b></summary>

**Options:**
1. **Improve mesh** — Use better `snappyHexMesh` settings or adjust geometry
2. **Change scheme** in `system/fvSchemes`:
   ```cpp
   laplacianSchemes
   {
       default Gauss linear corrected;  // Add correction
       // or
       default Gauss linear limited 0.5;  // For very bad mesh
   }
   ```
3. **Increase nNonOrthogonalCorrectors** in `system/fvSolution`

</details>

<details>
<summary><b>4. What are the best practices for time step selection in transient simulations?</b></summary>

**Guidelines:**
1. **Use CFL-based control**: Keep Co < 0.9 for explicit schemes
2. **Adaptive time stepping**: Enable `adjustTimeStep yes` in controlDict
3. **Start conservative**: Begin with small `deltaT`, increase gradually
4. **Monitor stability**: Check residuals and Courant number
5. **Consider physics**: Convection requires small steps, diffusion can use larger steps
6. **Balance cost vs accuracy**: Use largest stable time step for acceptable accuracy

```cpp
// Recommended setup:
adjustTimeStep  yes;
maxCo           0.9;
maxDeltaT       1.0;
```

</details>

<details>
<summary><b>5. How do you diagnose gradient calculation issues on non-uniform meshes?</b></summary>

**Symptoms:**
- Spurious oscillations near cell size changes
- Unphysical values in regions with high aspect ratio
- Convergence issues in boundary layers

**Solutions:**
```cpp
// Option 1: Use limited gradient scheme
gradSchemes
{
    default Gauss linear;
    grad(p) cellLimited Gauss linear 1;
}

// Option 2: Use least squares (more robust)
gradSchemes
{
    default leastSquares;
}

// Option 3: Improve mesh quality
// Use more uniform cell sizing
// Add refinement in critical regions
```

</details>

---

## 📖 Related Documents

- **Overview:** [00_Overview.md](00_Overview.md) — Vector Calculus Overview
- **Previous:** [05_Curl_and_Laplacian.md](05_Curl_and_Laplacian.md) — Curl and Laplacian
- **Next:** [07_Summary_and_Exercises.md](07_Summary_and_Exercises.md) — Summary and Exercises
- **fvc vs fvm:** [02_fvc_vs_fvm.md](02_fvc_vs_fvm.md) — Explicit and Implicit Comparison

---

## 🎯 Key Takeaways

- **Stability First**: Use `fvm` for unknown terms, `fvc` for known quantities
- **Check Units**: OpenFOAM's dimensional system catches physics errors early
- **Mesh Matters**: Match numerical schemes to mesh quality (corrected, limited)
- **Time Step Control**: Use CFL-based adaptive time stepping for robustness
- **Debug Systematically**: Check mesh → dimensions → types → schemes → CFL
- **Monitor Convergence**: Track residuals, Courant number, and conservation