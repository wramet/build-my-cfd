# OpenFOAM Implementation

> **Learning Objectives**
> - Master core OpenFOAM C++ classes for FVM
> - Read and navigate OpenFOAM source code
> - Create custom solvers and utilities
> - Debug common compilation errors

> **Prerequisites**
> - [05_Matrix_Assembly.md](05_Matrix_Assembly.md) — Matrix assembly concepts
> - [02_Governing_Equations_in_FVM.md](02_Governing_Equations_in_FVM.md) — Equation discretization theory
> - Basic C++ knowledge

---

## Core Classes API Reference

### fvMesh - Mesh Structure

```cpp
const fvMesh& mesh = ...;

mesh.V();       // Cell volumes (volScalarField)    →  Volume integrals
mesh.Sf();      // Face area vectors                →  Surface integrals
mesh.C();       // Cell centers (volVectorField)    →  ตำแหน่งเก็บค่า
mesh.Cf();      // Face centers                     →  ตำแหน่งคำนวณ flux
```

**Source location:** `src/finiteVolume/finiteVolume/fvMesh.H`

**Files ที่เกี่ยวข้อง:**
- `constant/polyMesh/points` — พิกัดจุดยอด (vertices)
- `constant/polyMesh/faces` — face ประกอบจากจุดอะไรบ้าง
- `constant/polyMesh/owner`, `neighbour` — cell ไหนเป็นเจ้าของ face

---

### volScalarField / volVectorField - Fields

```cpp
volScalarField p
(
    IOobject
    (
        "p",                      // ชื่อ field
        runTime.timeName(),       // Time directory (0, 0.1, 1, ...)
        mesh,                     // อ้างอิง mesh
        IOobject::MUST_READ,      // ต้องอ่านจาก file
        IOobject::AUTO_WRITE      // เขียน output อัตโนมัติ
    ),
    mesh
);
```

**Source locations:**
- `src/finiteVolume/fields/volFields/volScalarField.H`
- `src/finiteVolume/fields/volFields/volVectorField.H`

**Types:**

| Class | Description | Example | Usage |
|-------|-------------|---------|---------|
| `volScalarField` | Scalar ที่ cell centers | p, T, k | ค่าเดี่ยว |
| `volVectorField` | Vector ที่ cell centers | U | มี 3 components |
| `surfaceScalarField` | Scalar ที่ faces | phi (flux) | คำนวณ flux |

---

### fvMatrix - Equation System

```cpp
fvScalarMatrix TEqn
(
    fvm::ddt(T)               // Temporal → เพิ่ม diagonal
  + fvm::div(phi, T)          // Convection → เพิ่ม diagonal + off-diagonal
  - fvm::laplacian(k, T)      // Diffusion → เพิ่ม diagonal + off-diagonal
 ==
    Q                         // Source → เพิ่ม RHS
);

TEqn.solve();  // แก้ [A][T] = [b] ด้วย linear solver
```

**Source location:** `src/finiteVolume/fvMatrices/fvScalarMatrix/fvScalarMatrix.H`

**Key methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `.solve()` | `solverPerformance` | Solve the linear system |
| `.A()` | `volScalarField` | Diagonal coefficients |
| `.H()` | Field type | Off-diagonal + source contributions |
| `.residual()` | scalar | Current residual value |

---

## Code Examples by Equation Type

### Convection-Diffusion Equation

```cpp
// ∂T/∂t + ∇·(uT) = ∇·(α∇T) + Q
fvScalarMatrix TEqn
(
    fvm::ddt(T)
  + fvm::div(phi, T)
  - fvm::laplacian(DT, T)
 ==
    fvOptions(T)
);
TEqn.solve();
```

### Momentum Equation (Incompressible)

```cpp
// ∂u/∂t + ∇·(uu) = -∇p/ρ + ∇·(ν∇u)
fvVectorMatrix UEqn
(
    fvm::ddt(rho, U)
  + fvm::div(phi, U)
  - fvm::laplacian(mu, U)
 ==
    fvOptions(rho, U)
);

solve(UEqn == -fvc::grad(p));
```

### Pressure Poisson Equation

```cpp
// ∇·(1/A ∇p) = ∇·(H/A)
volScalarField rAU(1.0/UEqn.A());
volVectorField HbyA(rAU*UEqn.H());
surfaceScalarField phiHbyA(fvc::flux(HbyA));

fvScalarMatrix pEqn
(
    fvm::laplacian(rAU, p) == fvc::div(phiHbyA)
);
pEqn.solve();
```

### Energy Equation (Compressible)

```cpp
// ∂(ρh)/∂t + ∇·(ρuh) = ∇·(α∇h) + dp/dt
fvScalarMatrix hEqn
(
    fvm::ddt(rho, h)
  + fvm::div(phi, h)
  - fvm::laplacian(alpha, h)
 ==
    fvc::ddt(rho, K) + fvc::div(phi, K)  // Kinetic energy
);
hEqn.solve();
```

---

## Custom Solver Template

### File Structure

```
myCustomFoam/
├── Make/
│   ├── files       # Source files to compile
│   └── options     # Include paths, libraries
├── myCustomFoam.C  # Main solver code
└── createFields.H  # Field initialization (optional)
```

### Make/files

```bash
myCustomFoam.C

EXE = $(FOAM_USER_APPBIN)/myCustomFoam
```

### Make/options

```bash
EXE_INC = \
    -I$(LIB_SRC)/finiteVolume/lnInclude \
    -I$(LIB_SRC)/meshTools/lnInclude

EXE_LIBS = \
    -lfiniteVolume \
    -lmeshTools
```

### Main Solver Code

```cpp
#include "fvCFD.H"

int main(int argc, char *argv[])
{
    #include "setRootCase.H"
    #include "createTime.H"
    #include "createMesh.H"
    #include "createFields.H"

    while (runTime.loop())
    {
        Info<< "Time = " << runTime.timeName() << endl;

        // --- Solve equations here ---
        fvScalarMatrix TEqn
        (
            fvm::ddt(T)
          + fvm::div(phi, T)
          - fvm::laplacian(DT, T)
        );
        TEqn.solve();

        runTime.write();
    }

    Info<< "End\n" << endl;
    return 0;
}
```

### Compiling

```bash
wmake
```

---

## Configuration File Examples

### system/fvSchemes

```cpp
ddtSchemes
{
    default         Euler;          // 1st order, stable
    // backward       2nd order for transient;
}

gradSchemes
{
    default         Gauss linear;
}

divSchemes
{
    default         none;
    
    // Convection schemes
    div(phi,U)      Gauss linearUpwind grad(U);
    div(phi,T)      Gauss limitedLinearV 1;
    div(phi,k)      Gauss upwind;
    div(phi,epsilon) Gauss upwind;
    
    // Other terms
    div((nuEff*dev2(T(grad(U))))) Gauss linear;
}

laplacianSchemes
{
    default         Gauss linear corrected;
}

snGradSchemes
{
    default         corrected;
}
```

### system/fvSolution

```cpp
solvers
{
    p
    {
        solver          GAMG;
        tolerance       1e-06;
        relTol          0.01;
        smoother        GaussSeidel;
        nPreSweeps      0;
        nPostSweeps    2;
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

    "(k|epsilon|omega)"
    {
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-05;
        relTol          0.1;
    }
}

SIMPLE
{
    nNonOrthogonalCorrectors 0;
    
    consistency    yes;    // Check mass consistency
    residualControl
    {
        p               1e-4;
        U               1e-4;
        "(k|epsilon|omega)" 1e-4;
    }
}

PIMPLE
{
    momentumPredictor yes;
    nOuterCorrectors  50;
    nCorrectors       2;
    nNonOrthogonalCorrectors 0;
    
    consistent       yes;    // PIMPLE algorithm
}

relaxationFactors
{
    fields
    {
        p               0.3;
        rho             0.05;
    }
    equations
    {
        U               0.7;
        h               0.7;
        k               0.7;
        epsilon         0.7;
    }
}
```

---

## How to Read OpenFOAM Source Code

### Source Code Structure

```
$FOAM_SRC/
├── finiteVolume/           # FVM implementation
│   ├── fvMesh/            # Mesh class
│   ├── fvMatrices/        # Matrix classes
│   ├── interpolation/     # Interpolation schemes
│   └── snGrad/            # Surface normal gradient
├── OpenFOAM/              # Core field classes
│   ├── fields/            # Field templates
│   ├── matrices/          # Matrix storage
│   └── db/                # Database, IOobject
└── meshTools/             # Mesh utilities
```

### Finding Code Navigation

**To find where a class is defined:**

```bash
# Find header file
find $FOAM_SRC -name "fvMatrix.H"

# Find implementation
find $FOAM_SRC -name "fvMatrix.C"

# Search for specific method
grep -r "solve()" $FOAM_SRC/finiteVolume/fvMatraries/
```

**Understanding template classes:**

OpenFOAM uses extensive templates. The actual code is in `.C` files:

```cpp
// fvScalarMatrix.C
#include "fvScalarMatrix.H"

// Template instantiation
template<>
void Foam::fvScalarMatrix<scalar>::solve()
{
    // Implementation
}
```

### Key Source Files to Study

| Concept | Source File | What to Look For |
|---------|-------------|------------------|
| fvm:: operators | `finiteVolume/fvMatrices/fvScalarMatrix/` | How matrix coeffs are built |
| fvc:: operators | `finiteVolume/fvc/` | How field calculations work |
| Boundary conditions | `finiteVolume/fields/fvPatchFields/` | BC value calculation |
| Linear solvers | `OpenFOAM/matrices/lduMatrix/solvers/` | Iterative solver algorithms |

---

## Common Compile Errors with Fixes

### Error: No such file or directory

```
fatal error: fvCFD.H: No such file or directory
```

**Cause:** Missing include paths in Make/options

**Fix:**
```bash
EXE_INC = \
    -I$(LIB_SRC)/finiteVolume/lnInclude \
    -I$(LIB_SRC)/meshTools/lnInclude
```

---

### Error: Undefined reference

```
undefined reference to `Foam::fvMatrix<double>::solve()'
```

**Cause:** Missing library linkage in Make/options

**Fix:**
```bash
EXE_LIBS = \
    -lfiniteVolume \
    -lmeshTools
```

---

### Error: 'fvm::ddt' was not declared

```
error: 'fvm' has not been declared
```

**Cause:** Field type mismatch or missing header

**Fix:**
```cpp
// Wrong
surfaceScalarField T(...);
fvm::ddt(T);  // Error!

// Correct
volScalarField T(...);
fvm::ddt(T);  // OK
```

---

### Error: Template deduction failed

```
error: no matching function for call to 'div(...)`
```

**Cause:** Wrong field type for operator

**Fix:**
```cpp
// Wrong - div expects surfaceScalarField for flux
volScalarField phi(...);
fvm::div(phi, U);  // Error!

// Correct
surfaceScalarField phi(...);
fvm::div(phi, U);  // OK
```

---

### Error: Incompatible operand types

```
error: invalid operands of types 'double' and 'Foam::fvScalarMatrix'
```

**Cause:** Comparing matrix instead of solving

**Fix:**
```cpp
// Wrong
if (UEqn == -fvc::grad(p)) { ... }  // Error!

// Correct
solve(UEqn == -fvc::grad(p));
```

---

## Practical Reference: fvm vs fvc Usage

| Operator | Implicit (fvm) | Explicit (fvc) | When to Use |
|----------|---------------|----------------|-------------|
| Time derivative | `fvm::ddt(φ)` | `fvc::ddt(φ)` | fvm for unknown, fvc for known |
| Divergence | `fvm::div(F, φ)` | `fvc::div(F)` | fvm for unknown field, fvc for flux only |
| Laplacian | `fvm::laplacian(Γ, φ)` | `fvc::laplacian(Γ, φ)` | fvm for unknown, fvc for known |
| Gradient | — | `fvc::grad(φ)` | **Never fvm::grad!** |

> **Theory reference:** See [02_Governing_Equations_in_FVM.md](02_Governing_Equations_in_FVM.md) for mathematical background

---

## Practical Reference: Pressure-Velocity Coupling

> **Theory reference:** See [02_Governing_Equations_in_FVM.md](02_Governing_Equations_in_FVM.md) for SIMPLE/PISO algorithm theory

### SIMPLE Configuration

```cpp
// In createFields.H
SimpleVector<double> pRefCell(0);
scalar pRefValue = 0;

// In solver loop
while (runTime.loop())
{
    // Momentum predictor
    solve(UEqn == -fvc::grad(p));
    
    // Pressure equation
    volScalarField rAU(1.0/UEqn.A());
    volVectorField HbyA(rAU*UEqn.H());
    surfaceScalarField phiHbyA(fvc::flux(HbyA));
    
    fvScalarMatrix pEqn(fvm::laplacian(rAU, p) == fvc::div(phiHbyA));
    pEqn.solve();
    
    // Velocity correction
    U = HbyA - rAU*fvc::grad(p);
    U.correctBoundaryConditions();
}
```

### PISO Configuration

```cpp
for (int corr = 0; corr < nCorr; corr++)
{
    // Multiple pressure corrections per time step
    fvScalarMatrix pEqn(fvm::laplacian(rAU, p) == fvc::div(phiHbyA));
    pEqn.solve();
    
    U = HbyA - rAU*fvc::grad(p);
    U.correctBoundaryConditions();
}
```

---

## Concept Check

<details>
<summary><b>1. How do you find where fvm::div() is implemented?</b></summary>

```bash
# Find source location
find $FOAM_SRC -name "*.C" -o -name "*.H" | xargs grep -l "fvm::div"

# Look in:
# finiteVolume/fvMatrices/fvScalarMatrix/fvDiv.C
```
</details>

<details>
<summary><b>2. What's the difference between volScalarField and surfaceScalarField?</b></summary>

- `volScalarField`: Values stored at cell centers
- `surfaceScalarField`: Values stored at faces (interpolated)

Used for flux calculation: `phi` is always `surfaceScalarField`
</details>

<details>
<summary><b>3. Why does wmake fail with "undefined reference"?</b></summary>

Missing library in `Make/options`:

```bash
EXE_LIBS = \
    -lfiniteVolume \   # Required for fvMesh, fvMatrix
    -lmeshTools        # Required for mesh operations
```
</details>

<details>
<summary><b>4. What do UEqn.A() and UEqn.H() return?</b></summary>

- `UEqn.A()`: Diagonal coefficients (volScalarField)
- `UEqn.H()`: Off-diagonal + source contributions

Used in pressure equation for Rhie-Chow interpolation (see theory in 02)
</details>

<!-- IMAGE: IMG_01_006 -->
<!--
Purpose: อธิบายปัญหา Checkerboard Pressure ที่เกิดขึ้นหากใช้ Linear Interpolation ปกติกับ Collocated Grid ซึ่งดูเหมือนถูกต้อง (Gradient=0) แต่จริงๆ ผิด (Oscillation). เปรียบเทียบกับ Rhie-Chow ที่แก้ปัญหานี้
Prompt: "Checkerboard Pressure Concept. **Top Panel (Collocated Grid):** A 1D row of cells showing pressure values [100, 0, 100, 0]. The central difference gradient is zero despite oscillation. Label: 'Unphysical Oscillation'. **Bottom Panel (Staggered/Rhie-Chow):** Smooth pressure gradient showing correct interpolation. Label: 'Rhie-Chow Corrected'. **Style:** Scientific plot or grid schematic, red oscillation vs green smooth line."
-->
![IMG_01_006: Checkerboard Pressure vs Rhie-Chow](IMG_01_006.jpg)

---

## Related Documents

- **บทก่อนหน้า:** [05_Matrix_Assembly.md](05_Matrix_Assembly.md) — Matrix Assembly theory
- **ทฤษฎีที่เกี่ยวข้อง:** [02_Governing_Equations_in_FVM.md](02_Governing_Equations_in_FVM.md) — Discretization theory
- **บทถัดไป:** [07_Troubleshooting.md](07_Troubleshooting.md) — Common issues and solutions