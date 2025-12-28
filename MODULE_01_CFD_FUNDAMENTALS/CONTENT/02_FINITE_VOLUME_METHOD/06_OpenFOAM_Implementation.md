# OpenFOAM Implementation

การนำ FVM ไปใช้ใน OpenFOAM ผ่าน C++ Classes

---

## Core Classes

### fvMesh - Mesh Structure

```cpp
// Access mesh data
const fvMesh& mesh = ...;

mesh.V();       // Cell volumes (volScalarField)
mesh.Sf();      // Face area vectors (surfaceVectorField)
mesh.C();       // Cell centers (volVectorField)
mesh.Cf();      // Face centers (surfaceVectorField)
```

**Files:**
- `constant/polyMesh/points` — Vertices
- `constant/polyMesh/faces` — Face connectivity
- `constant/polyMesh/owner`, `neighbour` — Cell-face relations

### volScalarField / volVectorField - Fields

```cpp
volScalarField p
(
    IOobject
    (
        "p",                      // Name
        runTime.timeName(),       // Time directory
        mesh,                     // Mesh reference
        IOobject::MUST_READ,      // Read from 0/p
        IOobject::AUTO_WRITE      // Auto-save
    ),
    mesh
);
```

**Types:**
| Class | Description | Example |
|-------|-------------|---------|
| `volScalarField` | Scalar at cell centers | p, T, k |
| `volVectorField` | Vector at cell centers | U |
| `surfaceScalarField` | Scalar at faces | phi (flux) |

### fvMatrix - Equation System

```cpp
fvScalarMatrix TEqn
(
    fvm::ddt(T)               // Temporal → [A]
  + fvm::div(phi, T)          // Convection → [A]
  - fvm::laplacian(k, T)      // Diffusion → [A]
 ==
    Q                         // Source → [b]
);

TEqn.solve();
```

**Result:** $[A][T] = [b]$

---

## fvm vs fvc

| Prefix | Name | Output | Use |
|--------|------|--------|-----|
| `fvm::` | Finite Volume Method | Matrix → [A] | Implicit terms |
| `fvc::` | Finite Volume Calculus | Field | Explicit terms |

**ตัวอย่าง Momentum Equation:**

$$\rho\frac{\partial \mathbf{u}}{\partial t} + \nabla \cdot (\rho \mathbf{u} \mathbf{u}) - \nabla \cdot (\mu \nabla \mathbf{u}) = -\nabla p$$

```cpp
fvVectorMatrix UEqn
(
    fvm::ddt(rho, U)          // Implicit temporal
  + fvm::div(phi, U)          // Implicit convection
  - fvm::laplacian(mu, U)     // Implicit diffusion
);

solve(UEqn == -fvc::grad(p)); // Explicit pressure gradient
```

**กฎ:** Unknowns ที่ต้องการ solve → `fvm::`, ค่าที่รู้แล้ว → `fvc::`

---

## Discretization Operators

| Operator | Implicit | Explicit |
|----------|----------|----------|
| Time derivative | `fvm::ddt(φ)` | `fvc::ddt(φ)` |
| Divergence | `fvm::div(F, φ)` | `fvc::div(F)` |
| Laplacian | `fvm::laplacian(Γ, φ)` | `fvc::laplacian(Γ, φ)` |
| Gradient | — | `fvc::grad(φ)` |

**ไม่มี `fvm::grad()`** เพราะ gradient ไม่สร้าง implicit contribution ที่มีประโยชน์

---

## Pressure-Velocity Coupling

### SIMPLE (Steady-State)

```cpp
// 1. Solve momentum predictor
solve(UEqn == -fvc::grad(p));

// 2. Calculate pressure equation coefficients
volScalarField rAU(1.0/UEqn.A());
volVectorField HbyA(rAU*UEqn.H());
surfaceScalarField phiHbyA(fvc::flux(HbyA));

// 3. Solve pressure Poisson equation
fvScalarMatrix pEqn(fvm::laplacian(rAU, p) == fvc::div(phiHbyA));
pEqn.solve();

// 4. Correct velocity
U = HbyA - rAU*fvc::grad(p);
```

### PISO (Transient)

```cpp
for (int corr = 0; corr < nCorr; corr++)
{
    // Similar steps but multiple pressure corrections
}
```

---

## Configuration Files

### system/fvSchemes

```cpp
ddtSchemes
{
    default         Euler;
}

gradSchemes
{
    default         Gauss linear;
}

divSchemes
{
    div(phi,U)      Gauss linearUpwind grad(U);
    div(phi,k)      Gauss upwind;
}

laplacianSchemes
{
    default         Gauss linear corrected;
}
```

### system/fvSolution

```cpp
solvers
{
    p
    {
        solver      GAMG;
        tolerance   1e-6;
        relTol      0.01;
    }
    U
    {
        solver      PBiCGStab;
        preconditioner DILU;
        tolerance   1e-5;
        relTol      0.1;
    }
}

SIMPLE
{
    nNonOrthogonalCorrectors 1;
}

relaxationFactors
{
    fields { p 0.3; }
    equations { U 0.7; }
}
```

---

## Creating Custom Solvers

### File Structure

```
myFoam/
├── Make/
│   ├── files
│   └── options
└── myFoam.C
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
        // Solve equations
        fvScalarMatrix TEqn(fvm::ddt(T) - fvm::laplacian(k, T) == Q);
        TEqn.solve();

        runTime.write();
    }

    return 0;
}
```

### Compiling

```bash
wmake
```

---

## Concept Check

<details>
<summary><b>1. fvm กับ fvc ต่างกันอย่างไร?</b></summary>

- **fvm::**: สร้าง matrix coefficients (implicit) → ใช้กับ unknowns
- **fvc::**: คำนวณ field โดยตรง (explicit) → ใช้กับ known values
</details>

<details>
<summary><b>2. ทำไมไม่มี fvm::grad()?</b></summary>

Gradient operator ไม่สร้าง implicit contribution ที่ใช้งานได้ เพราะ $\nabla p$ ไม่มี unknown $p$ ในรูปแบบที่สามารถ linearize ได้
</details>

<details>
<summary><b>3. SIMPLE กับ PISO แตกต่างกันอย่างไร?</b></summary>

- **SIMPLE**: Steady-state, 1 pressure correction per iteration, ต้อง relax
- **PISO**: Transient, multiple pressure corrections per time step, ไม่ต้อง relax
</details>

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [05_Matrix_Assembly.md](05_Matrix_Assembly.md) — Matrix Assembly
- **บทถัดไป:** [07_Best_Practices.md](07_Best_Practices.md) — Best Practices