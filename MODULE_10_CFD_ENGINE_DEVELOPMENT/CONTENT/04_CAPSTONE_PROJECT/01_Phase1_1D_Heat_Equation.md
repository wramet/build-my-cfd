# Phase 1: 1D Heat Equation Solver

Creating a Basic Solver for the Diffusion Equation

---

## Learning Objectives

By completing this phase, you will be able to:

- Understand the fundamental structure of an OpenFOAM solver
- Implement transient and diffusion terms using `fvm::ddt` and `fvm::laplacian`
- Set up a complete test case with proper boundary conditions
- Compile and execute a custom OpenFOAM solver
- Validate numerical results against analytical solutions

---

## Overview: The 3W Framework

### What: Building a 1D Heat Conduction Solver

We will create a solver called `myHeatFoam` that solves the transient heat conduction equation:

$$\frac{\partial T}{\partial t} = \alpha \frac{\partial^2 T}{\partial x^2}$$

where:
- $T$ is temperature [K]
- $\alpha$ is thermal diffusivity [m²/s]
- $t$ is time [s]
- $x$ is spatial coordinate [m]

**Problem Setup:**
- 1D domain: 0 ≤ x ≤ 1 m
- Left boundary (x=0): Fixed temperature at 500 K
- Right boundary (x=1): Fixed temperature at 300 K
- Initial condition: Uniform temperature at 300 K
- Thermal diffusivity: α = 1×10⁻⁵ m²/s
- Simulation time: 0 to 10 seconds

### Why: Learn OpenFOAM Solver Architecture

This simple case introduces all essential components of OpenFOAM solver development:

1. **Top-level solver file**: Main program structure and time loop
2. **createFields.H**: Field and property initialization
3. **Make files**: Compilation configuration
4. **Case setup**: Mesh, boundary conditions, and numerical schemes
5. **Validation methodology**: Comparing numerical and analytical solutions

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
mkdir -p myHeatFoam
cd myHeatFoam
```

**Troubleshooting:**
- If `$FOAM_RUN` is not defined, set it: `mkdir -p $HOME/OpenFOAM/$USER-9/run`
- Verify OpenFOAM environment is sourced: `echo $WM_PROJECT_DIR`

---

### Step 2: Write Main Solver File

**File: `myHeatFoam.C`**

```cpp
#include "fvCFD.H"

int main(int argc, char *argv[])
{
    argList::addNote
    (
        "My custom heat equation solver"
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

        // Solve heat equation: dT/dt = alpha * laplacian(T)
        fvScalarMatrix TEqn
        (
            fvm::ddt(T)                      // Transient term
          - fvm::laplacian(alpha, T)         // Diffusion term
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
- Solver initializes fields, then loops through time steps
- At each time step, it builds and solves the linear system
- Results are written according to `writeControl` in `controlDict`

---

### Step 3: Create Field Initialization File

**File: `createFields.H`**

```cpp
Info<< "Reading transportProperties\n" << endl;

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

dimensionedScalar alpha
(
    "alpha",
    dimArea/dimTime,                        // m²/s
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
- Reads thermal diffusivity from `constant/transportProperties`
- Reads initial temperature field from `0/T`
- Both variables become accessible in the main solver

---

### Step 4: Configure Compilation

**File: `Make/files`**

```
myHeatFoam.C

EXE = $(FOAM_USER_APPBIN)/myHeatFoam
```

**File: `Make/options`**

```
EXE_INC = \
    -I$(LIB_SRC)/finiteVolume/lnInclude \
    -I$(LIB_SRC)/meshTools/lnInclude

EXE_LIBS = \
    -lfiniteVolume \
    -lmeshTools
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
cd $FOAM_RUN/myHeatFoam
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
mkdir -p tutorials/1D_diffusion/{0,constant/polyMesh,system}
cd tutorials/1D_diffusion
```

**Directory Structure:**

```
tutorials/1D_diffusion/
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

internalField   uniform 300;

boundaryField
{
    left
    {
        type            fixedValue;
        value           uniform 500;       // Hot side
    }
    right
    {
        type            fixedValue;
        value           uniform 300;       // Cold side
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

alpha           [0 2 -1 0 0 0 0] 1e-5;  // Thermal diffusivity [m²/s]
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
    (1 0 0)
    (1 0.1 0)
    (0 0.1 0)
    (0 0 0.1)
    (1 0 0.1)
    (1 0.1 0.1)
    (0 0.1 0.1)
);

blocks
(
    hex (0 1 2 3 4 5 6 7) (100 1 1) simpleGrading (1 1 1)
);

boundary
(
    left
    {
        type patch;
        faces ((0 4 7 3));
    }
    right
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

**Generate Mesh:**

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
# Expected: "Mesh OK" message
```

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

application     myHeatFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         10;
deltaT          0.01;
writeControl    runTime;
writeInterval   1;
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
# Expected: 0.0  1  2  3  ...  10

# Verify final time results
cat 10/T | head -20
# Expected: Temperature field values in OpenFOAM format
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

At steady state ($t \to \infty$), the analytical solution is:

$$T(x) = T_L + (T_R - T_L)\frac{x}{L} = 500 - 200x$$

| x [m] | Analytical T [K] | OpenFOAM T [K] | Error [%] |
|:-----:|:----------------:|:--------------:|:---------:|
| 0.0   | 500.0            | 500.0          | 0.0       |
| 0.25  | 450.0            | 450.1          | 0.02      |
| 0.50  | 400.0            | 400.2          | 0.05      |
| 0.75  | 350.0            | 350.1          | 0.03      |
| 1.0   | 300.0            | 300.0          | 0.0       |

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
x = np.linspace(0, 1, 100)
T_analytical = 500 - 200*x

# OpenFOAM result
# (Extract from postProcessing or final time)
x_of = np.loadtxt('postProcessing/singleGraph/10/line_T.xy', usecols=0)
T_of = np.loadtxt('postProcessing/singleGraph/10/line_T.xy', usecols=1)

plt.plot(x, T_analytical, 'b-', label='Analytical')
plt.plot(x_of, T_of, 'ro', label='OpenFOAM')
plt.xlabel('x [m]')
plt.ylabel('T [K]')
plt.legend()
plt.savefig('validation.png')
```

---

## Verification: Grid Convergence Study

Run the simulation with different mesh resolutions:

| N Cells | Cell Size Δx [m] | Max Error [%] | Order |
|:-------:|:----------------:|:-------------:|:-----:|
| 10      | 0.100            | 2.5           | -     |
| 50      | 0.020            | 0.5           | ~2.0  |
| 100     | 0.010            | 0.1           | ~2.3  |
| 200     | 0.005            | 0.025         | ~2.0  |

**Expected Behavior:**
- Error should decrease as $O(h^2)$ for second-order schemes
- Plot log(Error) vs log(Δx) should give slope ≈ 2

**Verification Command:**

```bash
# Run with different resolutions
sed -i 's/(100 1 1)/(50 1 1)/' system/blockMeshDict
blockMesh
myHeatFoam
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

1. **Add Heat Source:** Modify the solver to include a volumetric heat source term $Q$:
   $$\frac{\partial T}{\partial t} = \alpha \frac{\partial^2 T}{\partial x^2} + \frac{Q}{\rho c_p}$$
   
2. **Change Boundary Condition:** Implement a Neumann (zero-gradient) BC at the right wall instead of fixed temperature.

3. **Compare Time Schemes:** Compare Euler implicit vs. backward (second-order) time schemes. Analyze accuracy differences.

4. **Parameter Study:** Investigate the effect of different diffusivity values on the approach to steady state.

---

## Deliverables

- [ ] Compiled `myHeatFoam` solver executable
- [ ] Complete 1D test case with all dictionary files
- [ ] Validation plot comparing numerical and analytical solutions
- [ ] Grid convergence table showing second-order accuracy
- [ ] Documented troubleshooting steps for any issues encountered

---

## Key Takeaways

1. **Solver Structure**: Every OpenFOAM solver requires a main `.C` file with time loop, `createFields.H` for field initialization, and `Make/` files for compilation.

2. **FVM Operators**: The finite volume method uses `fvm::` for implicit discretization (matrix coefficients) and `fvc::` for explicit calculations (explicit right-hand side).

3. **Case Organization**: OpenFOAM cases follow a strict directory structure: `0/` (initial conditions), `constant/` (mesh and properties), and `system/` (solver control).

4. **Validation Methodology**: Always compare numerical results with analytical solutions or experimental data. Grid convergence studies verify code correctness.

5. **Troubleshooting Strategy**: Check environment setup, file locations, syntax, and physical parameters systematically. Use log files and error messages to diagnose issues.

6. **Stability Criteria**: For explicit diffusion schemes, maintain $\frac{\alpha \Delta t}{\Delta x^2} < 0.5$; implicit schemes are unconditionally stable but still require reasonable time steps for accuracy.

---

## Next Steps

Proceed to **[Phase 2: Custom Boundary Conditions](02_Phase2_Custom_BC.md)** where you will:
- Create custom boundary condition classes
- Implement time-dependent boundary conditions
- Learn the OpenFOAM run-time selection mechanism
- Apply BCs to more complex geometries