# fvMesh Class — Finite Volume Mesh

The Heart of Finite Volume Discretization in OpenFOAM

---

## Learning Objectives

By the end of this section, you will be able to:

- **[What]** Identify the role and structure of `fvMesh` within the OpenFOAM mesh hierarchy
- **[Why]** Understand why `fvMesh` is essential for Finite Volume Method operations and field management
- **[How]** Create and access `fvMesh` objects, retrieve geometric quantities, and use the objectRegistry pattern for custom field registration

---

## Overview

### What is fvMesh?

**fvMesh** is the central mesh class for Finite Volume computations in OpenFOAM. It extends `polyMesh` by adding:

- **FVM-specific geometry**: Face area vectors, cell volumes, interpolation distances
- **Discretization schemes**: Access to `fvSchemes` and `fvSolution` dictionaries
- **Object registry**: Centralized storage and lookup of all fields

```
fvMesh = polyMesh + FVM intelligence + field registry
```

### Why fvMesh Matters

- **Every field needs a mesh** — `volScalarField`, `volVectorField`, etc. all reference `fvMesh`
- **Centralized field management** — The registry pattern enables utilities and function objects to find fields by name
- **Performance** — Proper geometric access prevents redundant calculations and memory overhead

### Prerequisites

Before studying `fvMesh`, you should understand:

- [**primitiveMesh**](03_primitiveMesh.md) — Basic topology concepts (owner, neighbour)
- [**polyMesh**](04_polyMesh.md) — Boundary patches and point/face/cell storage
- [**Geometric Fields**](../05_FIELDS_GEOMETRICFIELDS/00_Overview.md) — `volVectorField`, `surfaceScalarField` types

### Relationship to Other Mesh Classes

```
primitiveMesh (topology only)
    ↓
polyMesh (adds: points, faces, patches)
    ↓
fvMesh (adds: FVM geometry, schemes, registry)
```

**Key additions in fvMesh:**
| Feature | Description |
|---------|-------------|
| `Sf()`, `magSf()` | Face area vectors for flux calculation |
| `V()` | Cell volumes for unsteady terms |
| `delta()` | Cell-cell distances for gradients |
| `schemesDict()` | Access to discretization schemes |
| `objectRegistry` | Field storage and lookup |

---

## 1. Creation and Initialization

### Standard Approach (Recommended)

Most solver templates create the mesh automatically:

```cpp
#include "createMesh.H"
// Creates: fvMesh mesh;
```

The `createMesh.H` header:
- Reads mesh from `constant/polyMesh`
- Initializes FVM geometry (Sf, V, delta)
- Sets up the object registry

### Explicit Creation (Advanced)

For custom code or multi-region simulations:

```cpp
fvMesh mesh
(
    IOobject
    (
        fvMesh::defaultRegion,   // "region0" (default)
        runTime.timeName(),       // Time directory
        runTime,                  // Reference to Time
        IOobject::MUST_READ       // Must read from disk
    )
);
```

**When to use explicit creation:**
- Multi-region solvers (e.g., conjugate heat transfer)
- Custom utilities operating on existing cases
- Dynamic mesh applications with specialized initialization

---

## 2. Geometric Quantities — When to Use What

### Cell-Based Geometry

#### Cell Centers — `C()`

**Usage Context:** Gradient calculations, source term positioning, cell-based post-processing

```cpp
const volVectorField& C = mesh.C();
vector cellCenter = C[cellI];

// Example: Calculate distance from origin
vector origin(0, 0, 0);
forAll(C, cellI)
{
    scalar dist = mag(C[cellI] - origin);
    // Use for: source term localization, cell-based metrics
}

// Example: Find cells within a radius
labelList nearbyCells;
forAll(C, cellI)
{
    if (mag(C[cellI] - origin) < radius)
    {
        nearbyCells.append(cellI);
    }
}
```

**Returns:** `volVectorField` — includes boundary face centers

#### Cell Volumes — `V()`

**Usage Context:** Unsteady terms (dρ/dt), volume integrals, spatial averaging, conservation checks

```cpp
const volScalarField::Internal& V = mesh.V();
scalar cellVolume = V[cellI];

// Example: Integrate scalar field over domain (mass calculation)
scalar totalMass = 0;
forAll(rho, cellI)
{
    totalMass += rho[cellI] * V[cellI];
}

// Example: Volume-weighted average
scalar avgT = sum(T * V) / sum(V);

// Example: Conservation check (mass balance error)
scalar massError = sum(fvc::ddt(rho) * V);
Info << "Mass conservation error: " << massError << endl;
```

**Returns:** `volScalarField::Internal` — no boundary values

**Why `Internal` and not `volScalarField`?**
- Volumes exist only at cell centers, not on boundary faces
- Avoids storing unnecessary boundary condition data
- Reduces memory usage and computational overhead

### Face-Based Geometry

#### Face Area Vectors — `Sf()`

**Usage Context:** Flux calculation (convection terms), surface integrals, force computation, boundary condition implementation

```cpp
const surfaceVectorField& Sf = mesh.Sf();

// Example: Calculate mass flux (convection term in continuity eq.)
surfaceScalarField massFlux
(
    IOobject("massFlux", runTime.timeName(), mesh),
    rho * (U & Sf)  // dot product: velocity × area vector
);
// massFlux[faceI] = ρ × (U·Sf) — mass flow rate through face

// Example: Wall force calculation (pressure + viscous)
label wallI = mesh.boundaryMesh().findPatchID("wall");
vector force = vector::zero;

// Pressure force: F = ∫ p·dS
const fvPatchVectorField& pPatch = p.boundaryField()[wallI];
const vectorField& patchSf = mesh.Sf().boundaryField()[wallI];

forAll(pPatch, faceI)
{
    force += pPatch[faceI] * patchSf[faceI];
}

// Example: Surface integral (Gauss theorem application)
scalar surfaceIntegral = 0;
const surfaceScalarField& phi = ...; // flux field
forAll(phi, faceI)
{
    surfaceIntegral += phi[faceI];  // Sum of face fluxes
}
```

**Direction:** Points from owner cell to neighbor cell (normal to face, outward from owner)

#### Face Area Magnitudes — `magSf()`

**Usage Context:** Flux normalization, area-weighted averaging, gradient correction factors

```cpp
const surfaceScalarField& magSf = mesh.magSf();

// Example: Normal velocity magnitude
surfaceScalarField magU_normal = mag(U & mesh.Sf()) / magSf;

// Example: Area-weighted boundary average
label inletI = mesh.boundaryMesh().findPatchID("inlet");
scalar avgU_inlet = 0;
scalar areaSum = 0;

const fvPatchScalarField& U_patch = U.boundaryField()[inletI];
const scalarField& magSf_patch = magSf.boundaryField()[inletI];

forAll(U_patch, faceI)
{
    avgU_inlet += U_patch[faceI] * magSf_patch[faceI];
    areaSum += magSf_patch[faceI];
}
avgU_inlet /= areaSum;

// Example: Non-orthogonality check
surfaceVectorField n = Sf / magSf;  // Unit face normals
```

#### Face Centers — `Cf()`

**Usage Context:** Interpolation schemes, boundary condition evaluation, post-processing visualization

```cpp
const surfaceVectorField& Cf = mesh.Cf();

// Example: Linear interpolation using face centers
// (Used internally by fvc::interpolate)
surfaceScalarField faceT = fvc::interpolate(T);
// Internally uses: Tf = T_owner * |Cf - C_nei| / d + T_nei * |Cf - C_own| / d

// Example: Boundary profile visualization
label outletI = mesh.boundaryMesh().findPatchID("outlet");
const vectorField& Cf_outlet = Cf.boundaryField()[outletI];
const scalarField& p_outlet = p.boundaryField()[outletI];

forAll(Cf_outlet, faceI)
{
    Info << "Position: " << Cf_outlet[faceI] 
         << " Pressure: " << p_outlet[faceI] << endl;
}
```

### Interpolation Geometry

#### Cell-Cell Distance — `delta()`

**Usage Context:** Non-orthogonal correction, gradient calculation, explicit diffusion terms

```cpp
const surfaceVectorField& delta = mesh.delta();

// Example: Non-orthogonal correction in gradient calculation
// (Used internally by fvc::grad for non-orthogonal meshes)
surfaceVectorField gradU_f = fvc::interpolate(fvc::grad(U));
vectorField d = mesh.delta();  // Vector from cell center to cell center

// Corrected gradient: ∇U = ∇U_explicit + correction
forAll(d, faceI)
{
    vector e = d[faceI] / mag(d[faceI]);  // Unit vector
    // Apply non-orthogonal correction
}

// Example: Distance for explicit diffusion coefficient
surfaceScalarField gammaDelta = gamma / mag(delta);
```

**Cross-Reference:** See [Boundary Conditions](../../../MODULE_01_CFD_FUNDAMENTALS/CONTENT/03_BOUNDARY_CONDITIONS/00_Overview.md) for gradient treatment and non-orthogonal correction

### Geometric Quantities Decision Guide

**Choose geometric quantity based on your operation:**

| Operation | Use This Quantity | Why |
|-----------|-------------------|-----|
| **Flux calculation** | `Sf()` | Directional area needed for dot product |
| **Mass/volume integral** | `V()` | Cell volume for weighting |
| **Force calculation** | `Sf()` on patches | Pressure × area vector |
| **Gradient computation** | `C()`, `Cf()`, `delta()` | Distance vectors for finite difference |
| **Boundary averaging** | `magSf()` | Area-weighted average |
| **Source term placement** | `C()` | Cell center coordinates |
| **Conservation check** | Sum of `phi` (flux × Sf) | Net flux through boundaries |
| **Mesh quality check** | `V()`, `magSf()`, `delta()` | Cell volumes, face areas, non-orthogonality |

---

## 3. Connectivity Information

### Owner-Neighbor Relationships

**Usage Context:** Matrix assembly, interpolation schemes, flux direction management

```cpp
const labelList& owner = mesh.faceOwner();
const labelList& neighbour = mesh.faceNeighbour();

// Example: Access internal face flux with direction check
forAll(mesh.C().internalField(), faceI)
{
    label own = owner[faceI];
    label nei = neighbour[faceI];

    // Positive flux: flows from owner → neighbor
    // Negative flux: flows from neighbor → owner
    scalar faceFlux = phi[faceI];
    
    // Owner and neighbor cell values
    scalar U_own = U[own];
    scalar U_nei = U[nei];
    
    // Interpolate to face using owner-neighbor relationship
    scalar U_face = 0.5 * (U_own + U_nei);
}

// Example: Build explicit Laplacian matrix (using connectivity)
scalarField diagonal(mesh.nCells(), 0.0);
scalarField offDiagonal(mesh.nInternalFaces(), 0.0);

forAll(mesh.owner(), faceI)
{
    label own = mesh.owner()[faceI];
    label nei = mesh.neighbour()[faceI];
    
    scalar diffCoeff = gamma[faceI] * magSf[faceI] / mag(delta[faceI]);
    
    diagonal[own] += diffCoeff;
    diagonal[nei] += diffCoeff;
    offDiagonal[faceI] -= diffCoeff;
}
```

**Key Points:**
- `owner[faceI]` — Cell ID on the "positive" side (higher index)
- `neighbour[faceI]` — Cell ID on the "negative" side (lower index)
- **Boundary faces**: `neighbour[faceI] = -1` (no neighbor cell)
- **Flux convention**: Positive flux = owner → neighbor

### Access via `lduAddressing`

For matrix operations and linear solvers:

```cpp
const lduAddressing& lduAddr = mesh.lduAddr();
const labelUList& lowerAddr = lduAddr.lowerAddr();  // Owner cells
const labelUList& upperAddr = lduAddr.upperAddr();  // Neighbor cells

// Example: Access matrix coefficients
scalarField& diag = matrix.diag();
scalarField& upper = matrix.upper();
scalarField& lower = matrix.lower();

forAll(lowerAddr, faceI)
{
    label own = lowerAddr[faceI];
    label nei = upperAddr[faceI];
    
    // Matrix assembly: A[own,nei] = upper[faceI]
    //                A[nei,own] = lower[faceI]
}
```

**Cross-Reference:** See [Matrix Assembly](../07_SOLVER_DEVELOPMENT/00_Overview.md) for lduMatrix usage in solver development

---

## 4. Boundary Access

### Iterating Over Patches

```cpp
const fvBoundaryMesh& boundary = mesh.boundary();

forAll(boundary, patchI)
{
    const fvPatch& patch = boundary[patchI];

    Info << "Patch: " << patch.name()
         << " Type: " << patch.type()
         << " Faces: " << patch.size()
         << " Start: " << patch.start() << endl;
         
    // Patch start() returns the global face index where this patch begins
    // Internal faces: 0 to mesh.nInternalFaces()-1
    // Boundary faces: mesh.nInternalFaces() to mesh.nFaces()-1
}
```

### Finding Patches by Name

**Always check return value — fundamental safety pattern:**

```cpp
label patchI = mesh.boundaryMesh().findPatchID("inlet");

if (patchI == -1)
{
    FatalErrorInFunction
        << "Patch 'inlet' not found!" 
        << " Available patches: " << mesh.boundaryMesh().names()
        << exit(FatalError);
}

// Safe to use now
const fvPatch& inletPatch = mesh.boundary()[patchI];
```

### Common Boundary Operations

```cpp
// Access patch field values
label wallI = mesh.boundaryMesh().findPatchID("wall");
const fvPatchScalarField& pWall = p.boundaryField()[wallI];

// Access patch geometry
const vectorField& SfWall = mesh.Sf().boundaryField()[wallI];
const vectorField& CfWall = mesh.Cf().boundaryField()[wallI];
const scalarField& magSfWall = mesh.magSf().boundaryField()[wallI];

// Calculate patch average (area-weighted)
scalar avgP = 0;
scalar areaSum = 0;
forAll(pWall, faceI)
{
    scalar area = mag(SfWall[faceI]);
    avgP += pWall[faceI] * area;
    areaSum += area;
}
avgP /= areaSum;

// Calculate total flux through patch
label outletI = mesh.boundaryMesh().findPatchID("outlet");
scalar outletFlux = sum(phi.boundaryField()[outletI]);
Info << "Outlet flux: " << outletFlux << endl;

// Access patch-specific cell values (owner cells of boundary faces)
const labelUList& faceCells = mesh.boundary()[wallI].faceCells();
forAll(faceCells, faceI)
{
    label cellI = faceCells[faceI];  // Owner cell of this boundary face
    scalar cellValue = p[cellI];
}
```

### Boundary Patch Types Reference

| Patch Type | Use Case | Access Pattern |
|------------|----------|----------------|
| **fixedValue** | Dirichlet BC (prescribed value) | Direct field access |
| **fixedGradient** | Neumann BC (prescribed gradient) | Access via `snGrad()` |
| **zeroGradient** | Zero gradient (zero flux) | Same as internal cells |
| **calculated** | Computed from other fields | Depends on calculation |
| **mixed** | Robin BC (value + gradient) | Value fraction based |
| **cyclic** | Periodic boundaries | Paired patches |
| **processor** | Parallel decomposition | Halo cell exchange |

**Cross-Reference:** See [Boundary Conditions](../../../MODULE_01_CFD_FUNDAMENTALS/CONTENT/03_BOUNDARY_CONDITIONS/00_Overview.md) for patch types and implementation details

---

## 5. The objectRegistry Pattern

### Understanding the Registry

**What is the objectRegistry?**

The `objectRegistry` is a fundamental OpenFOAM design pattern that enables runtime object storage and retrieval:

- `fvMesh` **inherits from** `objectRegistry` (is-a relationship)
- Every field registered with mesh becomes a "named object" in the registry
- Enables **runtime field lookup by name** with type safety
- Provides **automatic memory management** through reference counting

**Architecture:**

```
objectRegistry (base class)
    ↑
    | inheritance
    |
fvMesh (is-a registry)
    |
    | stores
    |
    → volScalarField "p"
    → volVectorField "U"
    → surfaceScalarField "phi"
    → ... (all mesh-associated fields)
```

**Why this pattern matters:**

1. **Decoupling** — Utilities don't need to know field origins or how they're created
2. **Extensibility** — Add new fields without changing existing solver code
3. **Consistency** — Single source of truth for all mesh-associated data
4. **Flexibility** — Function objects can access fields by name without recompilation

### Registry Operations

```cpp
// ===== EXISTENCE CHECK =====
// Check if field exists (read-only check, no exception thrown)
bool hasP = mesh.foundObject<volScalarField>("p");
bool hasU = mesh.foundObject<volVectorField>("U");
bool hasPhi = mesh.foundObject<surfaceScalarField>("phi");

if (hasP)
{
    Info << "Pressure field found in registry" << endl;
}

// ===== READ-ONLY LOOKUP =====
// Lookup read-only reference (throws if not found)
const volScalarField& p = mesh.lookupObject<volScalarField>("p");

// Safe lookup pattern (check first, then lookup)
if (mesh.foundObject<volScalarField>("T"))
{
    const volScalarField& T = mesh.lookupObject<volScalarField>("T");
    // Process temperature field
}

// ===== MUTABLE LOOKUP =====
// Lookup mutable reference (for modification)
volVectorField& U = mesh.lookupObjectRef<volVectorField>("U");
U *= 1.1;  // Increase velocity by 10%

// ===== ITERATION =====
// Iterate all registered objects
forAll(mesh.objectRegistry::sortedNames(), i)
{
    const word& name = mesh.objectRegistry::sortedNames()[i];
    Info << "Found object: " << name << endl;
}

// Type-filtered iteration (only volScalarFields)
HashTable<const volScalarField*> scalarFields;
mesh.objectRegistry::lookupClass<volScalarField>(scalarFields);

forAllIter(HashTable<const volScalarField*>, scalarFields, iter)
{
    const word& fieldName = iter.key();
    const volScalarField& field = *iter();
    Info << "Scalar field: " << fieldName << endl;
}
```

### Creating and Registering Custom Fields

**Example 1: Creating a Custom Scalar Field (Auto-Registration)**

```cpp
// Method 1: Direct creation (auto-registers with mesh)
volScalarField myCustomField
(
    IOobject
    (
        "myCustomField",           // Field name (registry lookup key)
        runTime.timeName(),        // Time directory (e.g., "0", "1.5")
        mesh,                      // ← Register with mesh (objectRegistry)
        IOobject::READ_IF_PRESENT, // Read if exists, otherwise create
        IOobject::AUTO_WRITE       // Write to disk automatically
    ),
    mesh,
    dimensionedScalar("zero", dimless, 0)  // Initial uniform value
);

// Field is now accessible via:
// mesh.lookupObject<volScalarField>("myCustomField")
```

**When to use `READ_IF_PRESENT` vs `NO_READ`:**
- `READ_IF_PRESENT`: Field can be pre-initialized in time directory
- `NO_READ`: Field always starts from given initial value

**Example 2: Explicit Registration (Advanced)**

```cpp
// Method 2: Create and explicitly register (for dynamic allocation)
volScalarField::Internal* cellSourcePtr = new volScalarField::Internal
(
    IOobject
    (
        "cellSource",
        runTime.timeName(),
        mesh,
        IOobject::NO_READ,     // Don't read from disk
        IOobject::NO_WRITE     // Don't write to disk
    ),
    mesh,
    dimensionedScalar("zero", dimless, 0)
);

// Explicitly register with mesh (takes ownership of pointer)
mesh.objectRegistry::regIOobject::store(cellSourcePtr);

// Field is now managed by the registry's reference counting system
// No manual delete needed — registry handles cleanup
```

**Example 3: Temporary Field (Not Registered)**

```cpp
// Method 3: Create temporary field (not written to disk, not registered)
tmp<volScalarField> tmpT = tmp<volScalarField>::New
(
    IOobject
    (
        "tempField",
        runTime.timeName(),
        mesh,
        IOobject::NO_READ,
        IOobject::NO_WRITE  // Temporary, not persisted
    ),
    mesh,
    dimensionedScalar("initial", dimTemperature, 293)
);

// Use temporary field
volScalarField& T = tmpT.ref();
T += 100;

// Automatic cleanup when tmpT goes out of scope
```

**Example 4: Practical Custom Field — Cell Quality Metric**

```cpp
// Create field to track cell non-orthogonality
volScalarField cellNonOrthogonality
(
    IOobject
    (
        "cellNonOrthogonality",
        runTime.timeName(),
        mesh,
        IOobject::NO_READ,
        IOobject::AUTO_WRITE  // Write for post-processing
    ),
    mesh,
    dimensionedScalar("zero", dimless, 0)
);

// Calculate based on mesh geometry
const surfaceVectorField& Sf = mesh.Sf();
const volVectorField& C = mesh.C();
const surfaceVectorField& Cf = mesh.Cf();

// Face-based non-orthogonality
surfaceScalarField faceNonOrtho
(
    IOobject
    (
        "faceNonOrtho",
        runTime.timeName(),
        mesh,
        IOobject::NO_READ,
        IOobject::NO_WRITE
    ),
    mag(Sf / magSf) & (Cf - fvc::average(C))
);

// Map to cells
cellNonOrthogonality = fvc::average(faceNonOrtho);
cellNonOrthogonality.correctBoundaryConditions();
```

### Registry Pattern in Practice

**Function Object Example:**

```cpp
// In a custom function object's execute() method:
bool myFunctionObject::execute()
{
    // Access fields without needing them as constructor arguments
    if (mesh.foundObject<volScalarField>("p"))
    {
        const volScalarField& p = mesh.lookupObject<volScalarField>("p");

        // Process pressure field
        scalar maxP = max(p).value();
        scalar minP = min(p).value();
        scalar avgP = sum(p * mesh.V()) / sum(mesh.V());

        Info << "Pressure stats — Min: " << minP 
             << " Max: " << maxP 
             << " Avg: " << avgP << endl;
    }
    else
    {
        WarningInFunction
            << "Pressure field 'p' not found in registry!" << endl;
    }

    return true;
}
```

**Solver Extension Example:**

```cpp
// Add custom transport equation for additional scalar
void solveAdditionalScalar()
{
    // Check if field exists (may be created by boundary condition)
    if (!mesh.foundObject<volScalarField>("myScalar"))
    {
        // Create on-the-fly if not present
        volScalarField myScalar
        (
            IOobject
            (
                "myScalar",
                runTime.timeName(),
                mesh,
                IOobject::MUST_READ,
                IOobject::AUTO_WRITE
            ),
            mesh
        );
    }

    // Solve transport equation
    volScalarField& myScalar = 
        mesh.lookupObjectRef<volScalarField>("myScalar");

    solve
    (
        fvm::ddt(myScalar)
      + fvm::div(phi, myScalar)
      - fvm::laplacian(D, myScalar)
    );
}
```

### Common Pitfalls and Solutions

```cpp
// ===== PITFALL 1: Lookup without checking =====
// ❌ WRONG: Fatal error if "T" doesn't exist
const volScalarField& T = mesh.lookupObject<volScalarField>("T");

// ✅ CORRECT: Always check first
if (mesh.foundObject<volScalarField>("T"))
{
    const volScalarField& T = mesh.lookupObject<volScalarField>("T");
}
else
{
    FatalErrorInFunction
        << "Temperature field 'T' not found!" << exit(FatalError);
}

// ===== PITFALL 2: Memory leak with raw pointers =====
// ❌ WRONG: Manual memory management
volScalarField* fieldPtr = new volScalarField(...);
// Memory leak if not deleted!

// ✅ CORRECT: Let registry manage memory
mesh.objectRegistry::regIOobject::store(fieldPtr);

// ===== PITFALL 3: Type mismatch =====
// ❌ WRONG: Lookup with wrong type throws exception
const volVectorField& p = mesh.lookupObject<volVectorField>("p");  // p is scalar!

// ✅ CORRECT: Use correct type or check type first
const volScalarField& p = mesh.lookupObject<volScalarField>("p");

// Or check type generically:
if (mesh.found("p"))
{
    const regIOobject& obj = mesh.lookupObjectRef<regIOobject>("p");
    if (isA<volScalarField>(obj))
    {
        const volScalarField& p = dynamicCast<const volScalarField&>(obj);
    }
}

// ===== PITFALL 4: Const correctness =====
// ❌ WRONG: Trying to modify const reference
const volScalarField& p = mesh.lookupObject<volScalarField>("p");
p *= 1.1;  // Compilation error!

// ✅ CORRECT: Use lookupObjectRef for mutable access
volScalarField& p = mesh.lookupObjectRef<volScalarField>("p");
p *= 1.1;  // OK
```

---

## 6. Schemes and Solution Dictionary Access

### Accessing Discretization Schemes

```cpp
const fvSchemes& schemes = mesh.schemesDict();

// Get specific scheme settings
word divScheme = schemes.div("div(phi,U)");
word gradScheme = schemes.grad("grad(U)");
word laplacianScheme = schemes.laplacian("laplacian(nu,U)");

// Check available schemes
if (schemes.defaultFluxRequired())
{
    Info << "Flux field must be provided for divergence schemes" << endl;
}

// Get interpolation scheme
word interpScheme = schemes.interp("interpolate(U)");

// Example: Conditional behavior based on scheme
if (divScheme == "Gauss upwind")
{
    Info << "Using first-order upwind — increased numerical diffusion" << endl;
}
else if (divScheme == "Gauss linearUpwind")
{
    Info << "Using second-order upwind — better accuracy" << endl;
}
```

### Accessing Solution Controls

```cpp
const fvSolution& solution = mesh.solutionDict();

// Get relaxation factors
scalar pRelax = solution.fieldRelaxationFactor("p");
scalar URelax = solution.fieldRelaxationFactor("U");
scalar kRelax = solution.fieldRelaxationFactor("k");

// Get solver settings
const dictionary& pSolver = solution.solverDict("p");
word pSolverType = pSolver.get<word>("solver");
scalar pTolerance = pSolver.get<scalar>("tolerance");
label pMaxIter = pSolver.get<label>("maxIter");

// Example: Adaptive solver settings
if (pTolerance > 1e-4)
{
    WarningInFunction
        << "Pressure tolerance is loose — consider tightening" << endl;
}

// Get algorithm settings
word algorithm = solution.solverDict("SIMPLE").get<word>("algorithm");
if (algorithm == "SIMPLE")
{
    scalar nNonOrthCorr = 
        solution.solverDict("SIMPLE").get<scalar>("nNonOrthogonalCorrectors");
}
```

**Cross-Reference:** See [Discretization Schemes](../../../MODULE_03_SINGLE_PHASE_FLOW/CONTENT/02_PRESSURE_VELOCITY_COUPLING/00_Overview.md) for detailed scheme explanations

---

## 7. Mesh Motion and Updates

### Moving Mesh Points

**Usage Context:** Dynamic meshes, FSI, overset grids, moving boundaries

```cpp
// Update mesh after point motion (triggers geometric recalculation)
mesh.movePoints(newPoints);

// Example: Deform mesh based on displacement field
pointVectorField& pointDisplacement = mesh.lookupObjectRef<pointVectorField>
(
    "pointDisplacement"
);

// Get current points and apply displacement
pointField newPoints = mesh.points();
newPoints += pointDisplacement;

// Update mesh geometry (recalculates Sf, V, delta, etc.)
mesh.movePoints(newPoints);

// Example: Oscillating boundary
scalar t = runTime.value();
label movingWallI = mesh.boundaryMesh().findPatchID("movingWall");

pointField& points = const_cast<pointField&>(mesh.points());
forAll(mesh.boundary()[movingWallI], faceI)
{
    label faceI_global = mesh.boundary()[movingWallI].start() + faceI;
    const face& f = mesh.faces()[faceI_global];
    
    forAll(f, pointI)
    {
        label pointI = f[pointI];
        points[pointI].x() = 0.01 * Foam::sin(2 * pi * t);  // Oscillate in x
    }
}

mesh.movePoints(points);
```

### Topology Changes

**Usage Context:** Adaptive mesh refinement (AMR), cell removal/addition, polyhedral cell changes

```cpp
// Update mesh after topology modification
// (e.g., after cell refinement, cell removal, crack propagation)
mesh.updateMesh(mapPolyMesh);

// Example: Check if topology changed
if (mesh.topoChanging())
{
    Info << "Mesh topology has changed — updating fields" << endl;
    
    // Fields are automatically mapped to new mesh via mapPolyMesh
    // Additional updates may be needed for custom data structures
}

// Example: Store pre-refinement data
forAll(mesh.C(), cellI)
{
    scalar oldCellValue = myField[cellI];
    // ... after refinement, access mapped value via mapPolyMesh
}
```

**Cross-Reference:** See [Dynamic Meshes](../../../MODULE_03_SINGLE_PHASE_FLOW/CONTENT/07_ADVANCED_TOPICS/01_High_Performance_Computing.md) for AMR and dynamic mesh techniques

---

## 8. Practical Example: Complete Field Creation and Usage

### Example: Custom Energy Equation Solver

```cpp
// Create custom temperature field with registration
volScalarField T
(
    IOobject
    (
        "T",                        // Field name
        runTime.timeName(),         // Time directory
        mesh,                       // Register with mesh
        IOobject::MUST_READ,        // Read initial conditions
        IOobject::AUTO_WRITE        // Write results
    ),
    mesh
);

// Create auxiliary field for heat source
volScalarField Q_source
(
    IOobject
    (
        "Q_source",                 // Field name
        runTime.timeName(),
        mesh,
        IOobject::READ_IF_PRESENT,  // Optional (if not present, zero)
        IOobject::AUTO_WRITE
    ),
    mesh,
    dimensionedScalar("zero", dimEnergy/dimTime/dimVolume, 0)
);

// Create material property field
volScalarField k
(
    IOobject
    (
        "k",                        // Thermal conductivity
        runTime.timeName(),
        mesh,
        IOobject::READ_IF_PRESENT,
        IOobject::AUTO_WRITE
    ),
    mesh,
    dimensionedScalar("k", dimPower/dimLength/dimTemperature, 0.025)
);

// Solve energy equation
{
    // Lookup flux field (should exist from momentum solver)
    if (mesh.foundObject<surfaceScalarField>("phi"))
    {
        const surfaceScalarField& phi = 
            mesh.lookupObject<surfaceScalarField>("phi");

        // Solve: dT/dt + div(phi,T) = div(k grad(T)) + Q
        solve
        (
            fvm::ddt(T)
          + fvm::div(phi, T)
          - fvm::laplacian(k, T)
         ==
            Q_source
        );
    }
    else
    {
        FatalErrorInFunction
            << "Flux field 'phi' not found — solve momentum first!" 
            << exit(FatalError);
    }

    // Calculate statistics
    scalar Tmax = max(T).value();
    scalar Tmin = min(T).value();
    scalar Tavg = sum(T * mesh.V()) / sum(mesh.V());

    Info << "Temperature — Min: " << Tmin 
         << " Max: " << Tmax 
         << " Avg: " << Tavg << endl;

    // Calculate heat flux through boundaries
    const surfaceScalarField::Boundary& TBf = T.boundaryField();
    const surfaceScalarField::Boundary& magSfBf = mesh.magSf().boundaryField();

    forAll(mesh.boundary(), patchI)
    {
        const fvPatch& patch = mesh.boundary()[patchI];
        scalar heatFlux = 0;

        // q = -k * dT/dn
        scalarField patchGradT = fvc::snGrad(T).boundaryField()[patchI];
        scalarField patchFlux = -k.boundaryField()[patchI] * patchGradT;

        heatFlux = sum(patchFlux * magSfBf[patchI]);

        Info << "Patch " << patch.name() 
             << " heat flux: " << heatFlux << " W" << endl;
    }
}
```

---

## Key Takeaways

### Core Concepts

- **fvMesh extends polyMesh** with FVM-specific geometry (`Sf`, `V`, `delta`) and field registry (`objectRegistry`)
- **Geometric access is fundamental** — Every FVM operation (flux, gradient, integral) relies on mesh geometry
- **ObjectRegistry enables flexibility** — Fields stored by name, looked up at runtime without compile-time dependencies

### Best Practices

1. **Always check patch lookup** — `findPatchID()` returns -1 if not found
2. **Use const references** for geometry access — prevents accidental modification and improves performance
3. **Check field existence** before `lookupObject()` to avoid runtime FatalError
4. **Register custom fields** properly with mesh using `IOobject` constructor
5. **Use `Internal` fields** for cell-only data (e.g., volumes) to avoid unnecessary boundary storage
6. **Choose geometric quantities wisely** — Match the quantity to your physical operation (flux vs. integral vs. gradient)

### Common Patterns

```cpp
// ===== GEOMETRY ACCESS =====
const volVectorField& C = mesh.C();           // Cell centers
const surfaceVectorField& Sf = mesh.Sf();     // Face area vectors
const volScalarField::Internal& V = mesh.V(); // Cell volumes

// ===== PATCH ACCESS =====
label patchI = mesh.boundaryMesh().findPatchID("patchName");
if (patchI != -1) 
{
    const fvPatch& patch = mesh.boundary()[patchI];
    // Safe to use patch
}

// ===== FIELD LOOKUP =====
if (mesh.foundObject<volScalarField>("fieldName"))
{
    const volScalarField& field = mesh.lookupObject<volScalarField>("fieldName");
}

// ===== CUSTOM FIELD CREATION =====
volScalarField customField
(
    IOobject("name", runTime.timeName(), mesh,
             IOobject::READ_IF_PRESENT, IOobject::AUTO_WRITE),
    mesh,
    dimensionedScalar("zero", dimless, 0)
);

// ===== OWNER-NEIGHBOR ACCESS =====
const labelList& owner = mesh.owner();
const labelList& neighbour = mesh.neighbour();
scalar flux = phi[faceI];  // Positive: owner → neighbor
```

### When to Use Which Geometric Quantity

| For This Operation | Use This | Method |
|-------------------|----------|--------|
| **Convective flux** | Face area vector | `mesh.Sf()` |
| **Volume integral** | Cell volumes | `mesh.V()` |
| **Force calculation** | Patch area vectors | `mesh.Sf().boundaryField()[patchI]` |
| **Gradient calculation** | Cell/face centers + distances | `mesh.C()`, `mesh.Cf()`, `mesh.delta()` |
| **Area-weighted average** | Face areas | `mesh.magSf()` |
| **Source term positioning** | Cell centers | `mesh.C()` |
| **Conservation check** | Face fluxes | `sum(phi)` |

---

## Practice Exercises

### Exercise 1: Mesh Statistics Utility

Write a function that calculates and prints:
- Total cell count
- Total mesh volume
- Boundary face count per patch
- Minimum and maximum cell volumes

```cpp
void printMeshStats(const fvMesh& mesh)
{
    Info << "=== Mesh Statistics ===" << endl;
    Info << "Cells: " << mesh.nCells() << endl;
    Info << "Faces: " << mesh.nFaces() << endl;
    Info << "Internal faces: " << mesh.nInternalFaces() << endl;
    Info << "Boundary patches: " << mesh.boundary().size() << endl;
    
    // Total volume
    scalar totalVol = sum(mesh.V()).value();
    Info << "Total volume: " << totalVol << " m³" << endl;
    
    // Volume statistics
    const volScalarField::Internal& V = mesh.V();
    scalar minV = min(V).value();
    scalar maxV = max(V).value();
    Info << "Cell volume range: [" << minV << ", " << maxV << "] m³" << endl;
    
    // Boundary faces per patch
    Info << "\nBoundary faces:" << endl;
    forAll(mesh.boundary(), patchI)
    {
        const fvPatch& patch = mesh.boundary()[patchI];
        Info << "  " << patch.name() << ": " 
             << patch.size() << " faces" << endl;
    }
}
```

### Exercise 2: Cell Quality Indicator

Create a custom field that stores cell aspect ratio (max edge / min edge approximation):

```cpp
volScalarField aspectRatio
(
    IOobject
    (
        "aspectRatio",
        runTime.timeName(),
        mesh,
        IOobject::NO_READ,
        IOobject::AUTO_WRITE
    ),
    mesh,
    dimensionedScalar("one", dimless, 1.0)
);

// Approximate aspect ratio using cell volume and face areas
const volScalarField::Internal& V = mesh.V();
const surfaceScalarField& magSf = mesh.magSf();

// Simple approximation: aspectRatio ~ (max_face_area / min_face_area)^(1/2)
// (This is a simplified metric — actual aspect ratio requires edge analysis)
forAll(aspectRatio, cellI)
{
    scalar maxArea = 0;
    scalar minArea = GREAT;
    
    // Iterate faces touching this cell
    const labelList& cellFaces = mesh.cells()[cellI];
    forAll(cellFaces, faceI)
    {
        scalar area = magSf[faceI];
        maxArea = max(maxArea, area);
        minArea = min(minArea, area);
    }
    
    aspectRatio[cellI] = sqrt(maxArea / (minArea + SMALL));
}

aspectRatio.correctBoundaryConditions();
Info << "Max aspect ratio: " << max(aspectRatio).value() << endl;
```

### Exercise 3: Boundary Flux Integration

Calculate total mass, momentum, and energy flux through each patch:

```cpp
forAll(mesh.boundary(), patchI)
{
    const fvPatch& patch = mesh.boundary()[patchI];
    const surfaceScalarField::Boundary& phiBf = phi.boundaryField();
    const volVectorField::Boundary& UBf = U.boundaryField();
    const volScalarField::Boundary& pBf = p.boundaryField();
    const scalarField& magSfPatch = mesh.magSf().boundaryField()[patchI];

    // Mass flux: ∫ ρ(U·dS)
    scalar patchMassFlux = sum(phiBf[patchI]);

    // Momentum flux: ∫ ρU(U·dS)
    vector patchMomFlux = sum
    (
        UBf[patchI] * phiBf[patchI] * magSfPatch
    );

    // Pressure force: ∫ p dS
    const vectorField& SfPatch = mesh.Sf().boundaryField()[patchI];
    vector patchPressureForce = sum(pBf[patchI] * SfPatch);

    Info << "Patch: " << patch.name() << nl
         << "  Mass flux: " << patchMassFlux << " kg/s" << nl
         << "  Momentum flux: " << patchMomFlux << " N" << nl
         << "  Pressure force: " << patchPressureForce << " N" << nl
         << endl;
}
```

### Exercise 4: Field Registry Query Tool

Create a utility that lists all registered fields and their properties:

```cpp
void listRegisteredFields(const fvMesh& mesh)
{
    Info << "\n=== Registered Fields ===" << endl;

    // List all volScalarFields
    HashTable<const volScalarField*> scalarFields;
    mesh.objectRegistry::lookupClass<volScalarField>(scalarFields);
    
    Info << "\nvolScalarFields (" << scalarFields.size() << "):" << endl;
    forAllConstIter(HashTable<const volScalarField*>, scalarFields, iter)
    {
        const volScalarField& field = *iter();
        Info << "  " << field.name() 
             << " — Min: " << min(field).value()
             << " Max: " << max(field).value() << endl;
    }

    // List all volVectorFields
    HashTable<const volVectorField*> vectorFields;
    mesh.objectRegistry::lookupClass<volVectorField>(vectorFields);
    
    Info << "\nvolVectorFields (" << vectorFields.size() << "):" << endl;
    forAllConstIter(HashTable<const volVectorField*>, vectorFields, iter)
    {
        const volVectorField& field = *iter();
        Info << "  " << field.name() << endl;
    }

    // List all surfaceScalarFields
    HashTable<const surfaceScalarField*> surfaceScalarFields;
    mesh.objectRegistry::lookupClass<surfaceScalarField>(surfaceScalarFields);
    
    Info << "\nsurfaceScalarFields (" << surfaceScalarFields.size() << "):" << endl;
    forAllConstIter(HashTable<const surfaceScalarField*>, surfaceScalarFields, iter)
    {
        const surfaceScalarField& field = *iter();
        Info << "  " << field.name() << endl;
    }
}
```

---

## Concept Check

<details>
<summary><b>1. What is the primary difference between fvMesh and polyMesh?</b></summary>

**fvMesh adds:**
- **FVM-specific geometric quantities**: `Sf` (face area vectors), `V` (cell volumes), `delta` (cell-cell distances)
- **Access to discretization schemes**: `fvSchemes` and `fvSolution` dictionaries
- **ObjectRegistry capability**: Field storage and lookup by name (runtime polymorphism)

**polyMesh provides:**
- **Basic topology**: Owner, neighbour connectivity
- **Geometric storage**: Points, faces, cells, boundary patches
- **Mesh modification tools**: Refinement, deformation

Both are needed, but fvMesh is the mesh class used in actual FVM solvers because it provides the geometric data structures needed for finite volume discretization.

**Key distinction:** `polyMesh` is about mesh storage and topology; `fvMesh` is about FVM operations and field management.
</details>

<details>
<summary><b>2. Why does mesh.V() return volScalarField::Internal instead of volScalarField?</b></summary>

**Answer:** Cell volumes exist only at cell centers, not on boundary faces. Using `Internal` avoids:

1. **Wasted memory** — No boundary values to store (saves ~20-30% memory for typical meshes)
2. **Confusion** — Boundary face volumes have no physical meaning (what is the "volume" of a boundary face?)
3. **Consistency** — Other cell-only properties (e.g., `deltaCoeffs`) use `Internal` field types
4. **Correctness** — Prevents accidental use of meaningless boundary values

**Technical detail:** 
- `volScalarField` = `DimensionedField` + `GeometricBoundaryField` (internal + boundary)
- `volScalarField::Internal` = `DimensionedField` (internal only)

**Rule:** If data only exists at cells, use `DimensionedField` (or `volScalarField::Internal`). If data includes boundary faces, use `volField`.
</details>

<details>
<summary><b>3. What happens if you call mesh.lookupObject<volScalarField>("T") and "T" doesn't exist?</b></summary>

**Answer:** The program throws a `FatalError` and terminates with a message like:
```
--> FOAM FATAL ERROR:
    request for volScalarField T while objectRegistry is empty
```

**Correct pattern:**
```cpp
if (mesh.foundObject<volScalarField>("T"))
{
    const volScalarField& T = mesh.lookupObject<volScalarField>("T");
    // Safe to use T
}
else
{
    WarningInFunction << "Temperature field T not found!" << endl;
    // Handle missing field case
}
```

**Why this behavior?** The `lookupObject` method performs a type-checked lookup and fails hard if the object doesn't exist or has the wrong type. This prevents silent errors and undefined behavior that could occur with null pointer dereferences.

**Alternative:** Use `lookupObjectRef` if you need a mutable (non-const) reference.
</details>

<details>
<summary><b>4. How do you create a custom field that is automatically registered with the mesh?</b></summary>

**Answer:** Pass the mesh as the `IOobject` registry:

```cpp
volScalarField myField
(
    IOobject
    (
        "myField",           // Registry lookup key (name)
        runTime.timeName(),  // Time directory
        mesh,                // ← Register with this mesh (crucial!)
        IOobject::NO_READ,   // Don't read from disk (initialize below)
        IOobject::AUTO_WRITE // Auto-write on output
    ),
    mesh,                      // Mesh for field dimensions
    dimensionedScalar("zero", dimless, 0)  // Initial uniform value
);
```

**Key points:**
- `mesh` in `IOobject` constructor → auto-registers with mesh's objectRegistry
- Field immediately accessible via `mesh.lookupObject<volScalarField>("myField")`
- `AUTO_WRITE` → included in time directories (0/, 1/, 2/, etc.)
- `NO_READ` → Field is created with given initial value, not read from disk
- `READ_IF_PRESENT` → Read if file exists, otherwise create with given value

**Memory management:** Once registered, the registry manages the field's lifecycle. No manual `new`/`delete` needed.
</details>

<details>
<summary><b>5. What is the difference between mesh.Sf() and mesh.magSf()? When should you use each?</b></summary>

**Answer:** `Sf()` returns the **area vector** (magnitude + direction), while `magSf()` returns just the **magnitude** (scalar area).

**Sf() — Area Vector:**
- **Type:** `surfaceVectorField`
- **Contains:** Vector pointing from owner to neighbor, magnitude = face area
- **Use for:** 
  - Flux calculation: `phi = rho * (U & Sf)` (dot product)
  - Force calculation: `F = sum(p * Sf)` on patches
  - Direction-dependent operations

**magSf() — Scalar Area:**
- **Type:** `surfaceScalarField`
- **Contains:** Face area magnitude only
- **Use for:**
  - Normalization: `U_normal = (U & Sf) / magSf`
  - Area-weighted averaging: `avg = sum(value * magSf) / sum(magSf)`
  - Mesh quality metrics

**Relationship:**
```cpp
mesh.magSf() == mag(mesh.Sf())  // Always true
mesh.Sf() / mesh.magSf() == faceNormal  // Unit normal vector
```

**Performance tip:** `magSf()` is computed once and stored. Avoid recalculating `mag(mesh.Sf())` — use `mesh.magSf()` directly.
</details>

<details>
<summary><b>6. What is the objectRegistry pattern, and why is it important in OpenFOAM?</b></summary>

**Answer:** The `objectRegistry` is a design pattern that enables runtime storage and retrieval of objects by name, with type safety.

**Key features:**
1. **Named storage** — Objects stored with string keys (e.g., "p", "U", "T")
2. **Type-safe lookup** — Template methods ensure type correctness at compile time
3. **Automatic memory management** — Reference counting via `regIOobject`
4. **Decoupling** — Utilities don't need to know field origins

**Why it matters:**
- **Function objects** can access fields without solver modification
- **Utilities** (e.g., `foamListTimes`) work with any case
- **Boundary conditions** can create auxiliary fields dynamically
- **Multi-region solvers** can manage multiple field registries

**Example:**
```cpp
// Solver creates field
volScalarField p(...);  // Auto-registers with mesh

// Function object (no compile-time dependency)
if (mesh.foundObject<volScalarField>("p"))  // Runtime check
{
    const volScalarField& p = mesh.lookupObject<volScalarField>("p");
    // Process pressure field
}
```

**Architecture:** `fvMesh` inherits from `objectRegistry`, so every mesh is-a registry. All fields registered with mesh become children of the mesh registry.
</details>

---

## Navigation

### Within Mesh Classes Module

- **Previous:** [04_polyMesh.md](04_polyMesh.md) — Boundary patches and polyhedral mesh
- **Current:** [05_fvMesh.md](05_fvMesh.md) — Finite Volume mesh and field registry
- **Next:** [06_Mesh_Usage_Patterns.md](06_Mesh_Usage_Patterns.md) — Common patterns and best practices

### Cross-Module References

- **[Geometric Fields](../05_FIELDS_GEOMETRICFIELDS/00_Overview.md)** — Field types used with fvMesh (`volScalarField`, `surfaceVectorField`, etc.)
- **[Boundary Conditions](../../../MODULE_01_CFD_FUNDAMENTALS/CONTENT/03_BOUNDARY_CONDITIONS/00_Overview.md)** — Patch types and BC implementation details
- **[Discretization Schemes](../../../MODULE_03_SINGLE_PHASE_FLOW/CONTENT/02_PRESSURE_VELOCITY_COUPLING/00_Overview.md)** — Scheme dictionary usage and selection
- **[Solver Development](../07_SOLVER_DEVELOPMENT/00_Overview.md)** — Matrix assembly using mesh connectivity and lduAddressing
- **[Dynamic Meshes](../../../MODULE_03_SINGLE_PHASE_FLOW/CONTENT/07_ADVANCED_TOPICS/01_Dynamic_Meshes.md)** — Mesh motion and topology changes