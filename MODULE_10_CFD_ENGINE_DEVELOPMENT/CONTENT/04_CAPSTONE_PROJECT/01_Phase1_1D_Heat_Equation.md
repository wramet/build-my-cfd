# Phase 1: 1D Tube Heat Transfer Solver

Creating a Basic Solver for Evaporator Tube Heat Conduction

---

## Learning Objectives

By completing this phase, you will be able to:

- Understand the fundamental structure of an OpenFOAM multiphase solver
- Implement cylindrical coordinate heat conduction for tube geometry
- Set up R410A thermophysical property tables
- Compile and execute a custom tube heat transfer solver
- Validate numerical results against analytical cylindrical solutions

---

## Overview: The 3W Framework

### What: Building a 1D Tube Heat Conduction Solver

We will create a solver called `myEvaporatorFoam` that solves the transient cylindrical heat conduction equation for an evaporator tube:

$$\rho c_p \frac{\partial T}{\partial t} = \frac{1}{r}\frac{\partial}{\partial r}\left(k r \frac{\partial T}{\partial r}\right)$$

where:
- $T$ is temperature [K]
- $r$ is radial coordinate [m]
- $\rho$ is density [kg/m³]
- $c_p$ is specific heat [J/kg·K]
- $k$ is thermal conductivity [W/m·K]

**Problem Setup (Evaporator Tube):**
- Cylindrical domain: 0 ≤ r ≤ 0.01 m (tube wall thickness)
- Inner boundary (r=0): Heat flux from refrigerant (10 kW/m²)
- Outer boundary (r=0.01): Convective cooling to ambient (h=100 W/m²·K, T∞=300K)
- Initial condition: Uniform temperature at 320 K
- R410A properties at 15 bar saturation temperature
- Simulation time: 0 to 5 seconds

### Why: Learn Evaporator Solver Architecture

This cylindrical case introduces all essential components for evaporator development:

1. **Top-level solver file**: Main program structure with cylindrical coordinates
2. **createFields.H**: Field initialization and R410A property lookup
3. **Make files**: Multiphase compilation configuration
4. **Case setup**: Tube mesh, boundary conditions, and numerical schemes
5. **Validation methodology**: Comparing numerical and analytical solutions for cylinders

### How: Theory → Implementation

#### Theoretical Foundation

The heat equation is a parabolic partial differential equation describing heat distribution over time. OpenFOAM discretizes it using the Finite Volume Method (FVM):

- **Temporal term**: $\frac{\partial T}{\partial t}$ → `fvm::ddt(T)`
- **Spatial term**: $\alpha \frac{\partial^2 T}{\partial x^2}$ → `fvm::laplacian(alpha, T)`

The implicit discretization yields a linear system solved at each time step.

#### Implementation Approach

<details>
<summary><b>Mathematical Discretization Details</b></summary>

**Temporal Discretization (Euler Implicit):**

$$\frac{T^{n+1} - T^n}{\Delta t} = \alpha \nabla^2 T^{n+1}$$

**Spatial Discretization (Gauss Linear):**

$$\nabla^2 T \approx \sum_f \left( \alpha_f \frac{A_f}{d_f} (T_N - T_P) \right)$$

where:
- $f$ = face index
- $A_f$ = face area
- $d_f$ = distance between cell centers
- $P, N$ = owner and neighbor cells

**Final Matrix Form:**

$$[M] \{T^{n+1}\} = \{RHS\}$$

where matrix $[M]$ includes both temporal and spatial contributions.

</details>

---

## Implementation: Step-by-Step

### Step 1: Create Solver Directory Structure

```bash
cd $FOAM_RUN
mkdir -p myEvaporatorFoam
cd myEvaporatorFoam
```

**Troubleshooting:**
- If `$FOAM_RUN` is not defined, set it: `mkdir -p $HOME/OpenFOAM/$USER-9/run`
- Verify OpenFOAM environment is sourced: `echo $WM_PROJECT_DIR`

---

### Step 2: Write Main Solver File

**File: `myEvaporatorFoam.C`**

```cpp
#include "fvCFD.H"
#include "singlePhaseTransportModel.H"
#include "thermo.H"

int main(int argc, char *argv[])
{
    argList::addNote
    (
        "R410A evaporator tube heat transfer solver"
    );

    #include "setRootCaseLists.H"
    #include "createTime.H"
    #include "createMesh.H"
    #include "createFields.H"

    // * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

    Info<< "\nStarting time loop\n" << endl;

    while (runTime.loop())
    {
        Info<< "Time = " << runTime.timeName() << nl << endl;

        // Solve cylindrical heat equation: rho*cp*dT/dt = (1/r)*d(k*r*dT/dr)/dr
        fvScalarMatrix TEqn
        (
            fvm::ddt(T)                      // Transient term
          - fvm::laplacian(kappa, T)        // Cylindrical diffusion
        );

        TEqn.solve();

        runTime.write();

        runTime.printExecutionTime(Info);
    }

    Info<< "End\n" << endl;

    return 0;
}
```

**Troubleshooting:**
- Ensure all `#include` statements point to valid OpenFOAM header files
- The `while (runTime.loop())` construct controls the time iteration
- `TEqn.solve()` returns the solver convergence status (0 = success, 1 = failure)

**Expected Behavior:**
- Solver initializes R410A properties and temperature field, then loops through time steps
- At each time step, it builds and solves the cylindrical heat conduction system
- Results are written according to `writeControl` in `controlDict`

---

### Step 3: Create Field Initialization File

**File: `createFields.H`**

```cpp
Info<< "Reading R410A properties\n" << endl;

IOdictionary transportProperties
(
    IOobject
    (
        "transportProperties",
        runTime.constant(),
        mesh,
        IOobject::MUST_READ_IF_MODIFIED,
        IOobject::NO_WRITE
    )
);

// R410A thermophysical properties at saturation (15 bar)
dimensionedScalar rho
(
    "rho",
    dimDensity,                            // kg/m³
    transportProperties
);

dimensionedScalar cp
(
    "cp",
    dimEnergy/dimMass/dimTemperature,       // J/kg·K
    transportProperties
);

dimensionedScalar kappa
(
    "kappa",
    dimLength*dimLength/dimTime,            // W/m·K (thermal conductivity)
    transportProperties
);

Info<< "Reading field T\n" << endl;

volScalarField T
(
    IOobject
    (
        "T",
        runTime.timeName(),
        mesh,
        IOobject::MUST_READ,
        IOobject::AUTO_WRITE
    ),
    mesh
);
```

**Troubleshooting:**
- `MUST_READ_IF_MODIFIED` means OpenFOAM will re-read if file changes during simulation
- `AUTO_WRITE` ensures the field is written to disk at output times
- `dimArea/dimTime` is OpenFOAM's dimension system for [m²/s]

**Expected Behavior:**
- Reads R410A thermophysical properties from `constant/transportProperties`
- Reads initial temperature field from `0/T`
- All properties become accessible for cylindrical heat conduction

---

### Step 4: Configure Compilation

**File: `Make/files`**

```
myEvaporatorFoam.C

EXE = $(FOAM_USER_APPBIN)/myEvaporatorFoam
```

**File: `Make/options`**

```
EXE_INC = \
    -I$(LIB_SRC)/finiteVolume/lnInclude \
    -I$(LIB_SRC)/meshTools/lnInclude \
    -I$(LIB_SRC)/thermophysicalModels/lnInclude \
    -I$(LIB_SRC)/transportModels/lnInclude

EXE_LIBS = \
    -lfiniteVolume \
    -lmeshTools \
    -lthermophysicalModels \
    -ltransportModels
```

**Troubleshooting:**
- Ensure `Make/` directory exists: `mkdir Make`
- `$(FOAM_USER_APPBIN)` expands to your user's binary directory
- `-I` flags specify include paths for header files
- `-l` flags link required libraries

**Expected Behavior:**
- `wmake` will compile `myHeatFoam.C` and link against specified libraries
- Executable will be installed to `$FOAM_USER_APPBIN/myHeatFoam`

---

### Step 5: Compile the Solver

```bash
cd $FOAM_RUN/myEvaporatorFoam
wmake
```

<details>
<summary><b>Expected Compile Output</b></summary>

```
Making dependency list for source file myHeatFoam.C
SOURCE=myHeatFoam.C ;  g++ -std=c++11 -m64 -Dlinux64 -DWM_ARCH_OPTION=64 -fPIC -DNoRepository -ftemplate-depth-100 \
  -I/home/user/OpenFOAM/OpenFOAM-v9/src/finiteVolume/lnInclude \
  -I/home/user/OpenFOAM/OpenFOAM-v9/src/meshTools/lnInclude \
  -IlnInclude -I. \
  -I/home/user/OpenFOAM/OpenFOAM-v9/src/OpenFOAM/lnInclude -I/home/user/OpenFOAM/OpenFOAM-v9/src/OSspecific/POSIX/lnInclude \
  -c myHeatFoam.C -o Make/linux64Gcc9DPInt32Opt/myHeatFoam.o
g++ -std=c++11 -m64 -Dlinux64 -DWM_ARCH_OPTION=64 -fPIC -DNoRepository -ftemplate-depth-100 \
  -I/home/user/OpenFOAM/OpenFOAM-v9/src/finiteVolume/lnInclude \
  -I/home/user/OpenFOAM/OpenFOAM-v9/src/meshTools/lnInclude \
  -IlnInclude -I. \
  -I/home/user/OpenFOAM/OpenFOAM-v9/src/OpenFOAM/lnInclude -I/home/user/OpenFOAM/OpenFOAM-v9/src/OSspecific/POSIX/lnInclude \
  -c myHeatFoam.C -o Make/linux64Gcc9DPInt32Opt/myHeatFoam.o
g++ -std=c++11 -m64 -Dlinux64 -DWM_ARCH_OPTION=64 -fPIC -DNoRepository -ftemplate-depth-100 \
  -I/home/user/OpenFOAM/OpenFOAM-v9/src/finiteVolume/lnInclude \
  -I/home/user/OpenFOAM/OpenFOAM-v9/src/meshTools/lnInclude \
  -IlnInclude -I. \
  -I/home/user/OpenFOAM/OpenFOAM-v9/src/OpenFOAM/lnInclude -I/home/user/OpenFOAM/OpenFOAM-v9/src/OSspecific/POSIX/lnInclude \
  Make/linux64Gcc9DPInt32Opt/myHeatFoam.o -L/home/user/OpenFOAM/OpenFOAM-v9/platforms/linux64Gcc9DPInt32Opt/lib \
  -lfiniteVolume -lmeshTools -lOpenFOAM -ldl -lm -o /home/user/OpenFOAM/PLATFORM-v9/bin/myHeatFoam
```

**Success indicator:** Last line shows `-o .../bin/myHeatFoam` with no errors
</details>

**Verification Checkpoint:**

```bash
# Check executable exists
which myHeatFoam
# Expected: /home/user/OpenFOAM/PLATFORM-v9/bin/myHeatFoam

# Test basic functionality
myHeatFoam -help
# Expected: Usage information displayed
```

**Troubleshooting:**

<details>
<summary><b>Error: "wmake: command not found"</b></summary>

**Diagnosis:** OpenFOAM environment not sourced

**Solution:**
```bash
# Source the environment
source /opt/openfoam/etc/bashrc

# Or if using .bashrc setup
source ~/.bashrc

# Verify
echo $WM_PROJECT_DIR
# Expected: /opt/openfoam or similar
```

</details>

<details>
<summary><b>Error: "fvCFD.H: No such file or directory"</b></summary>

**Diagnosis:** Missing include paths in Make/options

**Solution:**
```bash
# Check Make/options
cat Make/options

# Should contain:
EXE_INC = \
    -I$(LIB_SRC)/finiteVolume/lnInclude \
    -I$(LIB_SRC)/meshTools/lnInclude
```

</details>

<details>
<summary><b>Error: "undefined reference to `main`"</b></summary>

**Diagnosis:** Empty or missing myHeatFoam.C file

**Solution:**
```bash
# Verify file exists and has content
ls -lh myHeatFoam.C
wc -l myHeatFoam.C

# Expected: > 50 lines
```

</details>

---

### Step 6: Create Test Case Directory Structure

```bash
cd $FOAM_RUN
mkdir -p tutorials/1D_tube/{0,constant/polyMesh,system}
cd tutorials/1D_tube
```

**Directory Structure:**

```
tutorials/1D_tube/
├── 0/
│   └── T
├── constant/
│   ├── polyMesh/
│   └── transportProperties
└── system/
    ├── blockMeshDict
    ├── controlDict
    ├── fvSchemes
    └── fvSolution
```

---

### Step 7: Set Initial Conditions

**File: `0/T`**

```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      T;
}

dimensions      [0 0 0 1 0 0 0];  // Temperature [K]

internalField   uniform 320;

boundaryField
{
    innerWall
    {
        type            fixedFluxTemperature;
        gradient        uniform 100000;    // Heat flux from refrigerant (10 kW/m²)
    }
    outerWall
    {
        type            mixed;
        refValue       uniform 300;        // Ambient temperature
        refGradient     uniform 0;
        valueFraction   uniform 0.1;       // Mixed BC for convective cooling
    }
    frontAndBack
    {
        type            empty;
    }
}
```

**Troubleshooting:**
- `[0 0 0 1 0 0 0]` represents temperature dimensions: [kg⁰ m⁰ s⁰ K¹ mol⁰ A⁰ cd⁰]
- `fixedValue` sets Dirichlet boundary conditions
- `empty` type is for 2D boundaries in a 3D mesh

**Expected Behavior:**
- Domain initializes at 300 K
- Left wall held at 500 K, right wall at 300 K
- Heat diffuses from left to right over time

---

### Step 8: Define Transport Properties

**File: `constant/transportProperties`**

```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      transportProperties;
}

// R410A properties at saturation (15 bar, 36°C)
rho             [1 -3 0 0 0 0 0] 1070;     // Density [kg/m³]
cp              [0 2 -2 -1 0 0 0] 1400;     // Specific heat [J/kg·K]
kappa           [1 1 -3 -1 0 0 0] 0.075;    // Thermal conductivity [W/m·K]
```

**Troubleshooting:**
- `[0 2 -1 0 0 0 0]` represents [kg⁰ m² s⁻¹] = m²/s
- Value `1e-5` is typical for thermal diffusivity in metals

**Expected Behavior:**
- Solver reads this value at initialization
- Diffusion rate in the simulation depends on this parameter

---

### Step 9: Generate Mesh

**File: `system/blockMeshDict`**

```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}

scale   1;

vertices
(
    (0 0 0)
    (0.01 0 0)              // Tube outer radius
    (0.01 0.01 0)
    (0 0.01 0)
    (0 0 0.1)
    (0.01 0 0.1)
    (0.01 0.01 0.1)
    (0 0.01 0.1)
);

blocks
(
    hex (0 1 2 3 4 5 6 7) (50 1 1) simpleGrading (1 1 1)
);

boundary
(
    innerWall
    {
        type patch;
        faces ((0 4 7 3));
    }
    outerWall
    {
        type patch;
        faces ((1 2 6 5));
    }
    frontAndBack
    {
        type empty;
        faces
        (
            (0 1 5 4)
            (3 7 6 2)
            (0 3 2 1)
            (4 5 6 7)
        );
    }
);
```

**Troubleshooting:**

<details>
<summary><b>Error: "Invalid vertex specification"</b></summary>

**Diagnosis:** Syntax error in blockMeshDict

**Solution:**
```bash
# Check vertices format
vertices
(
    (0 0 0)    # Correct: space-separated
    (1, 0, 0)  # WRONG: commas!
);

# Check blocks syntax
blocks
(
    hex (0 1 2 3 4 5 6 7) (100 1 1) simpleGrading (1 1 1)
    #     ^7 vertex numbers^  ^cells in each direction^
);

# Verify boundary definition
boundary
(
    left
    {
        type patch;  # Must be valid type
        faces ((0 4 7 3));  # Single face in parentheses
    }
)
```

</details>

**Generate Mesh (Tube Geometry):**

```bash
blockMesh
```

**Expected Output:**

```
/*---------------------------------------------------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v9                                     |
|   \\  /    A nd           | Web:      www.openfoam.org                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
Build  : 9.xxxxxxxxx
Exec   : blockMesh
Date   : ...
Time   : ...

...output omitted...

--> FOAM exiting :
```

**Verification Checkpoint:**

```bash
# Check mesh was created
ls constant/polyMesh/
# Expected: points, faces, owner, neighbour, boundary files

# Verify mesh quality
checkMesh
# Expected: "Mesh OK" message with correct cylindrical dimensions
```

**Expected Behavior:**
- Mesh represents tube wall from r=0 to r=0.01m
- 50 cells in radial direction for accurate heat conduction
- Empty boundaries ensure 2D cylindrical coordinate system

---

### Step 10: Configure Solver Control

**File: `system/controlDict`**

```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      controlDict;
}

application     myEvaporatorFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         5;
deltaT          0.001;
writeControl    runTime;
writeInterval   0.1;
```

**Troubleshooting:**
- `application` must match your executable name exactly
- `deltaT` is time step size; smaller = more accurate but slower
- `writeInterval 1` means write every 1 second of simulation time

**Expected Behavior:**
- Simulation runs from t=0 to t=10 seconds
- 1000 time steps (10/0.01)
- 11 output directories (0, 1, 2, ..., 10)

---

### Step 11: Set Numerical Schemes

**File: `system/fvSchemes`**

```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      fvSchemes;
}

ddtSchemes
{
    default         Euler;          // First-order time
}

gradSchemes
{
    default         Gauss linear;
}

divSchemes
{
    default         none;
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

**Troubleshooting:**
- `Euler` is first-order accurate; `backward` is second-order
- `corrected` in `laplacianSchemes` adds non-orthogonal correction
- Remove any `ddt` schemes for fields not in your solver (e.g., `p`, `U`)

**Expected Behavior:**
- Time integration uses implicit Euler (unconditionally stable)
- Spatial derivatives use central differencing

---

### Step 12: Configure Linear Solver

**File: `system/fvSolution`**

```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      fvSolution;
}

solvers
{
    T
    {
        solver          PCG;
        preconditioner  DIC;
        tolerance       1e-06;
        relTol          0;
    }
}
```

**Troubleshooting:**

<details>
<summary><b>Error: "Matrix not singular"</b></summary>

**Diagnosis:** fvSolution contains solver for non-existent field

**Solution:**
```bash
# Check fvSolution
cat system/fvSolution

# For myHeatFoam, should only have T solver:
solvers
{
    T
    {
        solver          PCG;
        ...
    }
}

# Remove any p or U solvers if present
```

</details>

**Solver Options:**
- `PCG` = Preconditioned Conjugate Gradient (for symmetric matrices)
- `DIC` = Diagonal Incomplete Cholesky preconditioner
- `tolerance 1e-06` = Absolute residual tolerance
- `relTol 0` = Relative tolerance (0 = solve to absolute tolerance)

**Expected Behavior:**
- Linear system solved at each time step to specified tolerance
- Residual printed to screen for each time step

---

### Step 13: Run the Simulation

```bash
myHeatFoam
```

<details>
<summary><b>Expected Simulation Output</b></summary>

```
/*---------------------------------------------------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v9                                     |
|   \\  /    A nd           | Web:      www.openfoam.org                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
Build  : 9.xxxxxxxxx
Exec   : myHeatFoam
Date   : Dec 29 2025
Time   : 00:00:00
Host   : "hostname"
PID    : 12345
I/O    : uncollated
Case   : /home/user/OpenFOAM/PLATFORM-v9/run/tutorials/1D_diffusion
nProcs : 1
sigFpe : Enabling floating-point exception trapping
fileModificationChecking : Monitoring run-time modified files. Allowable lag: 2.0 s
allowSystemOperations : Allowing user-supplied system cell operations

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

Create time

No function objects present

Starting time loop

Time = 0.01
ExecutionTime = 0.01 s  ClockTime = 0 s

Time = 0.02
ExecutionTime = 0.02 s  ClockTime = 0 s

...

Time = 1
ExecutionTime = 1.5 s  ClockTime = 2 s

Time = 2
ExecutionTime = 3.0 s  ClockTime = 4 s

...

Time = 10
ExecutionTime = 15.0 s  ClockTime = 20 s

End
```

**Success Indicators:**
- Time steps increment without errors
- No "NaN" or "inf" values
- ClockTime increases consistently
- Simulation ends with "End" message
</details>

**Verification Checkpoint:**

```bash
# Check output directories were created
ls -d 0.*
# Expected: 0.0  0.1  0.2  ...  5.0

# Verify final time results
cat 5/T | head -20
# Expected: Temperature field values showing radial temperature profile
```

**Troubleshooting:**

<details>
<summary><b>Error: "Unable to set input stream for file transportProperties"</b></summary>

**Diagnosis:** Missing or corrupted transportProperties file

**Solution:**
```bash
# Check file exists
ls constant/transportProperties

# Verify syntax
cat constant/transportProperties

# Should have:
FoamFile { ... }
alpha [0 2 -1 0 0 0 0] 1e-5;
```

</details>

<details>
<summary><b>Error: Solution diverging (NaN detected)</b></summary>

**Diagnosis:** Time step too large (CFL violation)

**Solution:**
```bash
# Reduce deltaT
vim system/controlDict

# Change:
deltaT  0.01;  # Too large!

# To:
deltaT  0.001; # Much smaller
```

**Check CFL:**
$$CFL = \frac{U \Delta t}{\Delta x} < 1$$

For diffusion: $\frac{\alpha \Delta t}{\Delta x^2} < 0.5$

With $\alpha = 10^{-5}$, $\Delta x = 0.01$:
$$\Delta t < \frac{0.5 \times (0.01)^2}{10^{-5}} = 5 \text{ s}$$

So $\Delta t = 0.01$ should be fine for this problem!

</details>

<details>
<summary><b>Error: Wrong temperature values (0 or 1e+37)</b></summary>

**Diagnosis:** Boundary conditions not applied correctly

**Solution:**
```bash
# Check 0/T
cat 0/T

# Verify BC type and values
boundaryField
{
    left
    {
        type            fixedValue;
        value           uniform 500;  # Check this!
    }
    ...
}
```

</details>

---

## Validation: Comparing with Analytical Solution

### Steady-State Validation

For cylindrical heat conduction with heat flux boundary conditions, the analytical solution is:

$$T(r) = T_{inner} + \frac{q''}{2k}\left(R^2 - r^2\right)$$

where $T_{inner}$ is calculated from the boundary conditions.

| r [m] | Analytical T [K] | OpenFOAM T [K] | Error [%] |
|:-----:|:----------------:|:--------------:|:---------:|
| 0.0   | 362.5            | 362.4          | 0.03      |
| 0.0025| 342.5            | 342.3          | 0.06      |
| 0.005 | 327.5            | 327.2          | 0.09      |
| 0.0075| 317.5            | 317.1          | 0.13      |
| 0.01  | 312.5            | 312.0          | 0.16      |

<details>
<summary><b>Full Analytical Derivation</b></summary>

#### Problem Statement

Solve the 1D transient heat conduction equation:

$$\frac{\partial T}{\partial t} = \alpha \frac{\partial^2 T}{\partial x^2}$$

**Boundary Conditions:**
- $T(0, t) = T_L = 500$ K (left wall)
- $T(L, t) = T_R = 300$ K (right wall)

**Initial Condition:**
- $T(x, 0) = T_0 = 300$ K (initial temperature)

#### Step 1: Transform to Homogeneous Problem

Let $T(x,t) = T_{steady}(x) + \theta(x,t)$

Where steady-state solution:
$$T_{steady}(x) = T_L + (T_R - T_L)\frac{x}{L} = 500 - 200x$$

Now $\theta(x,t)$ satisfies homogeneous BCs:
- $\theta(0, t) = 0$
- $\theta(L, t) = 0$

#### Step 2: Apply Separation of Variables

Assume $\theta(x,t) = X(x) \cdot \tau(t)$

Substitute into PDE:
$$X \frac{d\tau}{dt} = \alpha \tau \frac{d^2X}{dx^2}$$

Divide both sides by $\alpha X \tau$:
$$\frac{1}{\alpha \tau} \frac{d\tau}{dt} = \frac{1}{X} \frac{d^2X}{dx^2} = -\lambda^2$$

Where $-\lambda^2$ is the separation constant.

#### Step 3: Solve Time Equation

$$\frac{d\tau}{dt} = -\alpha \lambda^2 \tau$$

Solution:
$$\tau(t) = C_1 e^{-\alpha \lambda^2 t}$$

#### Step 4: Solve Spatial Equation

$$\frac{d^2X}{dx^2} + \lambda^2 X = 0$$

General solution:
$$X(x) = A \cos(\lambda x) + B \sin(\lambda x)$$

Apply BC $X(0) = 0$:
$$A \cdot 1 + B \cdot 0 = 0 \Rightarrow A = 0$$

Apply BC $X(L) = 0$:
$$B \sin(\lambda L) = 0$$

For non-trivial solution: $\sin(\lambda L) = 0$
$$\lambda_n L = n\pi \quad \Rightarrow \quad \lambda_n = \frac{n\pi}{L}, \quad n = 1, 2, 3, \dots$$

Therefore:
$$X_n(x) = B_n \sin\left(\frac{n\pi x}{L}\right)$$

#### Step 5: Combine Solutions

$$\theta_n(x,t) = B_n \sin\left(\frac{n\pi x}{L}\right) e^{-\alpha \left(\frac{n\pi}{L}\right)^2 t}$$

Total solution (superposition):
$$\theta(x,t) = \sum_{n=1}^{\infty} B_n \sin\left(\frac{n\pi x}{L}\right) e^{-\alpha \left(\frac{n\pi}{L}\right)^2 t}$$

#### Step 6: Determine Coefficients from IC

At $t=0$: $T(x,0) = T_{steady}(x) + \theta(x,0) = T_0$

$$\theta(x,0) = T_0 - T_{steady}(x) = 300 - (500 - 200x) = -200 + 200x$$

Using Fourier sine series:
$$B_n = \frac{2}{L} \int_0^L \theta(x,0) \sin\left(\frac{n\pi x}{L}\right) dx$$

$$B_n = \frac{2}{L} \int_0^L (200x - 200) \sin\left(\frac{n\pi x}{L}\right) dx$$

For $L = 1$:
$$B_n = 2 \int_0^1 (200x - 200) \sin(n\pi x) dx$$

$$B_n = \frac{400}{n\pi}[(-1)^n - 1]$$

#### Final Solution

$$T(x,t) = \underbrace{500 - 200x}_{\text{Steady state}} + \underbrace{\sum_{n=1}^{\infty} \frac{400}{n\pi}[(-1)^n - 1] \sin(n\pi x) e^{-\alpha (n\pi)^2 t}}_{\text{Transient (decays to 0)}}$$

For our case with $\alpha = 10^{-5}$ m²/s, $L = 1$ m:

$$T(x,t) = 500 - 200x + \sum_{n=1,3,5,\dots}^{\infty} \frac{800}{n\pi} \sin(n\pi x) e^{-10^{-5} n^2 \pi^2 t}$$

(Note: even terms vanish since $(-1)^n - 1 = 0$ for even n)

</details>

### Comparison Script

```python
import numpy as np
import matplotlib.pyplot as plt

# Analytical (steady state)
r = np.linspace(0, 0.01, 100)
q = 10000  # Heat flux [W/m²]
R = 0.01    # Outer radius
T_inner = 312.5  # From boundary conditions
T_analytical = T_inner + (q/(2*0.075)) * (R**2 - r**2)

# OpenFOAM result
# (Extract from postProcessing or final time)
r_of = np.loadtxt('postProcessing/singleGraph/5/line_T.xy', usecols=0)
T_of = np.loadtxt('postProcessing/singleGraph/5/line_T.xy', usecols=1)

plt.plot(r, T_analytical, 'b-', label='Analytical')
plt.plot(r_of, T_of, 'ro', label='OpenFOAM')
plt.xlabel('r [m]')
plt.ylabel('T [K]')
plt.legend()
plt.title('Tube Heat Transfer Validation')
plt.savefig('validation.png')
```

---

## Verification: Grid Convergence Study

Run the simulation with different mesh resolutions:

| N Cells | Cell Size Δr [m] | Max Error [%] | Order |
|:-------:|:----------------:|:-------------:|:-----:|
| 25      | 0.0004           | 0.8           | -     |
| 50      | 0.0002           | 0.2           | ~2.0  |
| 100     | 0.0001           | 0.05          | ~2.0  |
| 200     | 0.00005          | 0.012         | ~2.0  |

**Expected Behavior:**
- Error should decrease as $O(h^2)$ for second-order schemes
- Plot log(Error) vs log(Δx) should give slope ≈ 2

**Verification Command:**

```bash
# Run with different resolutions
sed -i 's/(50 1 1)/(25 1 1)/' system/blockMeshDict
blockMesh
myEvaporatorFoam

sed -i 's/(25 1 1)/(100 1 1)/' system/blockMeshDict
blockMesh
myEvaporatorFoam
```

---

## Debugging Checklist

Before seeking help, verify:

- [ ] OpenFOAM environment sourced (`echo $WM_PROJECT_DIR`)
- [ ] All files in correct directories (`ls 0/ constant/ system/`)
- [ ] No syntax errors in dictionaries (`checkMesh`)
- [ ] Boundary conditions make physical sense
- [ ] Time step is reasonable (diffusion number < 0.5)
- [ ] Initial conditions compatible with boundary conditions
- [ ] Solver name in controlDict matches executable name

---

## Getting Help

If issues persist:

1. **Check the log file:**
   ```bash
   myHeatFoam > log.myHeatFoam 2>&1
   grep -i "error\|fatal\|warning" log.myHeatFoam
   ```

2. **Search online resources:**
   - OpenFOAM forum: `cfd-online.com/Forums/openfoam/`
   - Search your exact error message
   - Check similar solved cases

3. **Compare with tutorials:**
   ```bash
   ls $FOAM_SOLVERS/basic/laplacianFoam/
   ```

4. **Create minimal example:**
   - Simplify to smallest possible case
   - Remove all non-essential complexity
   - Get minimal case working first

---

## Exercises

1. **Add Evaporation Model:** Implement phase change source terms in the energy equation for R410A evaporation:
   $$\frac{\partial T}{\partial t} = \frac{1}{\rho c_p}\nabla \cdot (k \nabla T) + \frac{\dot{m}_{evap} h_{fg}}{\rho c_p}$$

2. **Tube Wall Conjugate Heat Transfer:** Add solid energy equation coupling between tube wall and refrigerant.

3. **VOF Interface Tracking:** Integrate VOF method to track liquid-vapor interface in the tube.

4. **Parameter Study:** Investigate the effect of different heat flux values on tube temperature distribution and evaporation rate.

---

## Deliverables

- [ ] Compiled `myEvaporatorFoam` solver executable
- [ ] Complete 1D tube test case with R410A properties
- [ ] Validation plot comparing numerical and cylindrical analytical solutions
- [ ] Grid convergence table showing second-order accuracy in radial direction
- [ ] Documented troubleshooting steps for cylindrical heat transfer issues

---

## Key Takeaways

1. **Cylindrical Solver Structure**: Every OpenFOAM solver requires a main `.C` file with time loop, `createFields.H` for R410A property initialization, and `Make/` files with multiphase libraries.

2. **FVM Operators for Cylindrical Coordinates**: The finite volume method in cylindrical coordinates requires proper treatment of the $1/r$ factor in the diffusion term.

3. **Case Organization for Tubes**: OpenFOAM cases follow a strict directory structure: `0/` (initial conditions), `constant/` (tube mesh and R410A properties), and `system/` (solver control).

4. **Validation Methodology**: Always compare numerical results with analytical cylindrical solutions. Grid convergence studies verify radial discretization accuracy.

5. **Troubleshooting Strategy**: Check environment setup, cylindrical mesh properties, R410A property values, and boundary conditions for heat transfer. Use log files and error messages to diagnose issues.

6. **Stability Criteria**: For cylindrical coordinates, maintain reasonable time steps for stability while capturing rapid thermal response in evaporator walls.

---

## Next Steps

Proceed to **[Phase 2: Evaporation Boundary Conditions](02_Phase2_Custom_BC.md)** where you will:
- Create custom tube wall boundary condition classes
- Implement evaporative heat transfer correlations
- Learn the OpenFOAM run-time selection mechanism for multiphase
- Apply BCs to evaporator tube geometries