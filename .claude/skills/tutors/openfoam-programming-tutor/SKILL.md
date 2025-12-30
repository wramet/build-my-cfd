---
name: OpenFOAM Programming Tutor
description: |
  Use this skill when: user wants to learn OpenFOAM C++ programming, understand field classes, write custom solvers, or understand the OpenFOAM source code architecture.
  
  Specialist tutor for MODULE_05_OPENFOAM_PROGRAMMING content.
---

# OpenFOAM Programming Tutor

ผู้เชี่ยวชาญด้าน OpenFOAM C++ Programming

## Knowledge Base

**Primary Content:** `MODULE_05_OPENFOAM_PROGRAMMING/CONTENT/`

```
01_FOUNDATION_PRIMITIVES/
├── 00_Overview.md              → Basic types overview
├── 02_Basic_Primitives.md      → scalar, vector, tensor
├── 03_Dimensioned_Types.md     → dimensionedScalar
└── 04_Smart_Pointers.md        → autoPtr, tmp

03_CONTAINERS_MEMORY/
├── 02_Memory_Management.md     → RAII, smart pointers
└── 03_Reference_Counting.md    → tmp pattern

04_MESH_CLASSES/
├── 00_Overview.md              → Mesh hierarchy
├── 03_primitiveMesh.md         → Topology
└── 05_fvMesh.md                → FVM geometry

05_FIELDS_GEOMETRICFIELDS/
├── 00_Overview.md              → Field types
├── 02_Design_Philosophy.md     → Template design
└── 03_Inheritance.md           → Class hierarchy

06_MATRICES_LINEARALGEBRA/
├── 00_Overview.md              → Matrix types
├── 03_fvMatrix.md              → Sparse matrix
└── 04_Linear_Solvers.md        → GAMG, PCG

10_VECTOR_CALCULUS/
├── 00_Overview.md              → fvc vs fvm
├── 02_fvc_vs_fvm.md            → Explicit vs Implicit
└── 04_Divergence.md            → fvc::div, fvm::div

11_TENSOR_ALGEBRA/
├── 00_Overview.md              → Tensor types
└── 04_Tensor_Operations.md     → &, &&, dev(), symm()
```

## Learning Paths

### 🟢 Beginner: "ฉันอยากอ่าน OpenFOAM code ได้"

**Goal:** เข้าใจ basic types และ field structure

| Step | File | Time | Focus |
|------|------|------|-------|
| 1 | `01_FOUNDATION.../00_Overview.md` | 30 min | Type categories |
| 2 | `01_FOUNDATION.../02_Basic_Primitives.md` | 30 min | scalar, vector, tensor |
| 3 | `05_FIELDS.../00_Overview.md` | 30 min | Field types |
| 4 | `10_VECTOR.../00_Overview.md` | 30 min | fvc vs fvm |
| 5 | **Code Study** | 60 min | laplacianFoam source |

**Code to Study:**
```
applications/solvers/basic/laplacianFoam/
├── laplacianFoam.C    → Main solver
├── createFields.H     → Field creation
└── Make/              → Compilation
```

**Key Patterns:**
```cpp
// Field creation
volScalarField T
(
    IOobject("T", runTime.timeName(), mesh, ...),
    mesh
);

// Field operation
fvc::laplacian(DT, T)   // Explicit
fvm::laplacian(DT, T)   // Implicit
```

---

### 🟡 Intermediate: "ฉันอยากเข้าใจ solver architecture"

**Goal:** เข้าใจ mesh, matrices, and solution loop

| Step | File | Time | Focus |
|------|------|------|-------|
| 1 | `04_MESH.../05_fvMesh.md` | 45 min | Mesh geometry |
| 2 | `06_MATRICES.../03_fvMatrix.md` | 45 min | Sparse matrix |
| 3 | `10_VECTOR.../02_fvc_vs_fvm.md` | 60 min | Discretization |
| 4 | `03_CONTAINERS.../02_Memory.md` | 30 min | Smart pointers |
| 5 | **Code Study** | 90 min | simpleFoam source |

**simpleFoam Structure:**
```cpp
while (simple.loop())
{
    // Momentum predictor
    fvVectorMatrix UEqn
    (
        fvm::ddt(U)
      + fvm::div(phi, U)
      - fvm::laplacian(nu, U)
     ==
        -fvc::grad(p)
    );
    UEqn.solve();
    
    // Pressure correction
    fvScalarMatrix pEqn
    (
        fvm::laplacian(rAU, p) == fvc::div(phiHbyA)
    );
    pEqn.solve();
}
```

---

### 🔴 Advanced: "ฉันอยากเขียน solver เอง"

**Goal:** Implement custom solver from scratch

| Step | File | Time | Focus |
|------|------|------|-------|
| 1 | All `01_FOUNDATION` files | 2 hrs | Complete foundation |
| 2 | All `06_MATRICES` files | 2 hrs | Linear algebra |
| 3 | `11_TENSOR.../04_Tensor_Operations.md` | 1 hr | Tensor math |
| 4 | **Project** | 4+ hrs | Custom solver |

**Custom Solver Template:**
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
        // Your equations here
        fvScalarMatrix TEqn
        (
            fvm::ddt(T)
          + fvm::div(phi, T)
          - fvm::laplacian(DT, T)
        );
        TEqn.solve();
        
        runTime.write();
    }
    
    return 0;
}
```

## Quick Reference

### Field Types

| Type | Description | Example |
|------|-------------|---------|
| `volScalarField` | Cell-centered scalar | p, T, k |
| `volVectorField` | Cell-centered vector | U |
| `surfaceScalarField` | Face scalar | phi (flux) |
| `volTensorField` | Cell-centered tensor | tau |

### fvc vs fvm

| Operator | fvc | fvm |
|----------|-----|-----|
| ddt | Explicit time derivative | Implicit time derivative |
| div | Evaluates directly | Adds to matrix |
| laplacian | Evaluates directly | Adds to matrix |
| grad | Evaluates directly | N/A |

**Rule:**
- `fvm` → Unknown being solved → goes into matrix
- `fvc` → Known from previous iteration → explicit

### Smart Pointers

| Type | Use Case | Behavior |
|------|----------|----------|
| `autoPtr<T>` | Unique ownership | Deletes on destroy |
| `tmp<T>` | Temporary fields | Reference counted |
| `const T&` | Read-only access | No ownership |

## Source Code Locations

```
$FOAM_SRC/
├── OpenFOAM/
│   ├── primitives/       → scalar, vector, tensor
│   ├── containers/       → List, HashTable
│   └── fields/           → Field, GeometricField
├── finiteVolume/
│   ├── fvMesh/           → Mesh classes
│   ├── fvMatrices/       → fvMatrix
│   ├── fvc/              → Explicit operators
│   └── fvm/              → Implicit operators
└── meshTools/            → Mesh manipulation
```

## Common Patterns

### Factory Pattern (Runtime Selection)
```cpp
autoPtr<turbulenceModel> turbulence = 
    turbulenceModel::New(U, phi, transport);
```

### tmp Pattern (Expression Templates)
```cpp
tmp<volVectorField> tGradP = fvc::grad(p);
U -= rAU*tGradP();
```

### RAII (Resource Acquisition)
```cpp
{
    IOobject io(...);  // Opens file
    volScalarField T(io, mesh);
}  // File closed automatically
```

## Related Topics

- **CFD Theory** → `cfd-fundamentals` tutor
- **Solver Usage** → `single-phase-tutor`
- **Multiphase Solvers** → `multiphase-tutor`
