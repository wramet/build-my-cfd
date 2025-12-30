# Volume Fields

Volume Fields ใน OpenFOAM

---

## 📋 Learning Objectives

By the end of this section, you will be able to:
- Define what volFields are and where they store data (cell centers)
- Create volScalarField, volVectorField, volTensorField, and volSymmTensorField from files or with initial values
- Access and modify internal field (cell values) and boundary field (patch values) data
- Perform arithmetic and calculus operations on volume fields
- Calculate field statistics (max, min, average, sum)
- Apply and correct boundary conditions properly

**Difficulty:** Beginner | **Reading Time:** ~25 minutes | **Prerequisites:** [02_Basic_Primitives.md](02_Basic_Primitives.md), [03_Dimensioned_Types_Intro.md](03_Dimensioned_Types_Intro.md)

---

## 🎯 When to Use Volume Fields

**Use volFields when:**
- You are working with **state variables** at cell centers (pressure, velocity, temperature, concentration, etc.)
- You need to solve transport equations (convection-diffusion, momentum, energy, etc.)
- You require volume-based operations (divergence, gradient, Laplacian)
- You want to perform statistical analysis on field data (min, max, average, volume integrals)

**Do NOT use volFields when:**
- You need face-based values (use surface fields instead — see [03_Surface_Fields.md](03_Surface_Fields.md))
- You need point-mesh values (use point fields instead)
- You are only working with boundary data (use patch fields directly)

---

## What are Volume Fields?

> **volField** = Cell-centered field values — ค่าหนึ่งค่าต่อ cell ณ จุดศูนย์ถ่วงของเซลล์

Volume fields store values at cell centers, making them ideal for state variables like pressure, velocity, temperature, and other conserved quantities in finite volume methods.

### Physical Meaning (Why)

Finite Volume Method (FVM) discretizes the domain into control volumes (cells). The governing equations are integrated over these control volumes, and the unknown variables are stored at:
- **Cell centroids** for volFields (primary unknowns)
- **Cell faces** for surfaceFields (fluxes)
- **Mesh points** for pointFields (visualization, some BCs)

**Why cell centers?** Gauss's theorem converts volume integrals to surface integrals, requiring cell-centered values to compute face fluxes. This is the natural storage location for conservation laws.

---

## 1. Common Types

### Type Aliases

| Alias | Full Type | Description | Example Use |
|-------|-----------|-------------|-------------|
| `volScalarField` | `GeometricField<scalar, fvPatchField, volMesh>` | Single value per cell | Pressure, temperature, concentration |
| `volVectorField` | `GeometricField<vector, fvPatchField, volMesh>` | Vector per cell | Velocity, displacement |
| `volTensorField` | `GeometricField<tensor, fvPatchField, volMesh>` | Tensor per cell | Stress tensor, gradient tensor |
| `volSymmTensorField` | `GeometricField<symmTensor, fvPatchField, volMesh>` | Symmetric tensor per cell | Strain rate tensor, Reynolds stress |

### Template Structure

```
volScalarField = GeometricField<
    scalar,           // Field rank (0D scalar)
    fvPatchField,     // Boundary field type for finite volume
    volMesh           // Mesh type (finite volume mesh)
>
```

**Key insight:** The `vol` prefix means "volume" but data is actually stored at **cell centers**, not distributed throughout the cell volume. This naming convention originates from the finite volume method where equations are integrated over control volumes.

---

## 2. Creating Volume Fields

### Reading from File

```cpp
// Read from file (MUST_READ)
volScalarField p
(
    IOobject(
        "p",                          // Field name
        runTime.timeName(),           // Time directory
        mesh,                         // Mesh reference
        IOobject::MUST_READ,          // Must read from file
        IOobject::AUTO_WRITE          // Auto-write at output times
    ),
    mesh
);
```

**When to use:** Standard case setup where fields are initialized from time directories (e.g., `0/`, `0.5/`, `1.0/`)

### Creating with Initial Value

```cpp
// Create with uniform initial value (NO_READ)
volVectorField U
(
    IOobject(
        "U",
        runTime.timeName(),
        mesh,
        IOobject::NO_READ,            // Don't read from file
        IOobject::AUTO_WRITE
    ),
    mesh,
    dimensionedVector(
        "U",
        dimVelocity,                  // Dimensions [m/s]
        vector::zero                  // Initial value (0,0,0)
    )
);
```

**When to use:** Programmatic field creation, custom initial conditions, temporary fields

### Creating from Existing Field

```cpp
// Clone existing field
volScalarField T2(T1);  // Deep copy

// Create with expression
volScalarField rhoU2
(
    IOobject("rhoU2", runTime.timeName(), mesh, IOobject::NO_READ),
    mesh,
    rho * magSqr(U)  // Compute from other fields
);
```

**When to use:** Derived quantities, temporary working fields, field transformations

---

## 3. Accessing Field Data

### Internal Field (Cell Values)

```cpp
// Method 1: Direct indexing
forAll(T, cellI)
{
    T[cellI] = compute(cellI);
}

// Method 2: Internal field reference (more efficient for bulk operations)
scalarField& Ti = T.ref();  // Non-const reference
const scalarField& Ti = T.internalField();  // Const reference

// Method 3: Primal-ref access (OpenFOAM dev)
scalarField& Ti = T.primitiveFieldRef();
```

**Performance consideration:** Use `.ref()` for write operations and `.internalField()` for read operations. The compiler cannot optimize through virtual function calls in the boundary field, so direct internal field access is always faster.

**Access pattern comparison:**

| Method | Use Case | Performance |
|--------|----------|-------------|
| `T[cellI]` | Random access, single cell | Slow (bounds checking) |
| `T.ref()` | Sequential bulk write | Fast (direct memory) |
| `T.internalField()` | Sequential bulk read | Fast (direct memory) |
| `T.primitiveFieldRef()` | Explicit intent (dev) | Fast (direct memory) |

### Boundary Field (Patch Face Values)

```cpp
// Loop over all boundary patches
forAll(T.boundaryField(), patchI)
{
    // Get reference to patch field (non-const)
    scalarField& Tp = T.boundaryFieldRef()[patchI];
    
    // Get const reference (read-only)
    const scalarField& Tp = T.boundaryField()[patchI];
    
    // Access individual face values
    forAll(Tp, faceI)
    {
        Tp[faceI] = someValue;
    }
}
```

**Performance consideration:** Boundary field access is slower than internal field access due to virtual function dispatch. Cache boundary field references when performing multiple operations on the same patch.

### Accessing Patch by Name

```cpp
// Find patch ID by name
label inletI = mesh.boundaryMesh().findPatchID("inlet");

if (inletI != -1)  // Check if patch exists
{
    // Get/set boundary field values
    const scalarField& Tin = T.boundaryField()[inletI];
    T.boundaryFieldRef()[inletI] == fixedValue;
}
```

**Pitfall:** Always check if `findPatchID()` returns -1 (patch not found) before accessing boundary fields to avoid segmentation faults.

---

## 4. Field Operations

### Arithmetic Operations

```cpp
// Element-wise operations
volScalarField rhoU2 = rho * magSqr(U);      // ρ|U|²
volScalarField Ttotal = T1 + T2;              // Addition
volScalarField deltaT = T - T0;               // Subtraction
volVectorField U_scaled = U * 2.0;            // Scalar multiplication

// In-place operations
T += 273.15;  // Convert Celsius to Kelvin
U *= 0.5;     // Scale velocity
```

**Performance tip:** In-place operations (`+=`, `*=`) avoid temporary field allocation and are more memory-efficient than creating new fields.

### Calculus Operations (Finite Volume Calculus)

All `fvc` (finite volume calculus) operations return NEW fields:

```cpp
// Gradient (returns vector field from scalar field)
volVectorField gradT = fvc::grad(T);

// Divergence (scalar field from surface scalar field)
surfaceScalarField phi = fvc::interpolate(rho * U) & mesh.Sf();
volScalarField divU = fvc::div(phi);

// Laplacian (returns same rank as input)
volScalarField lapT = fvc::laplacian(alpha, T);  // α∇²T

// Curl (returns vector field from vector field)
volVectorField curlU = fvc::curl(U);

// Time derivative
volScalarField dTdt = fvc::ddt(T);
```

**Functional design:** `fvc::` operations never modify the original field — they return new fields. This enables expression templates and operator chaining:

```cpp
volScalarField lapT = fvc::laplacian(kappa, fvc::grad(T) & fvc::grad(T));
```

**See also:** [03_Surface_Fields.md](03_Surface_Fields.md) for face-based field representations used in flux calculations.

---

## 5. Field Statistics

### Global Statistics

```cpp
// Min/max (global over all cells)
scalar maxT = max(T).value();
scalar minT = min(T).value();

// Average (arithmetic mean of cell values)
scalar avgT = average(T).value();

// Sum (arithmetic sum, NOT volume-weighted)
scalar sumT = gSum(T);

// Volume-weighted sum (∫ T dV)
scalar volumeIntegral = gSum(T * mesh.V());

// Volume-weighted average (∫ T dV / ∫ dV)
scalar volAvgT = gSum(T * mesh.V()) / gSum(mesh.V());
```

**Physics note:** For non-uniform meshes, always use volume-weighted averages (`gSum(T * mesh.V()) / gSum(mesh.V())`) instead of arithmetic averages to account for varying cell sizes.

### Patch Statistics

```cpp
label inletI = mesh.boundaryMesh().findPatchID("inlet");
const scalarField& Tin = T.boundaryField()[inletI];

// Patch statistics
scalar maxInlet = max(Tin);
scalar avgInlet = average(Tin);
scalar areaWeightedAvg = gSum(Tin * mesh.magSf().boundaryField()[inletI]) / 
                         gSum(mesh.magSf().boundaryField()[inletI]);
```

**Performance consideration:** Patch statistics are computed over boundary faces only and are typically much faster than global statistics over all cells.

---

## 6. Boundary Conditions

### Correcting Boundary Conditions

**WHEN to call `correctBoundaryConditions()`:**
- **After solving** a transport equation (the solver calls this automatically)
- **After modifying the internal field** and BCs need to recompute (e.g., fixedGradient BC needs to reevaluate gradient)
- **After changing time** if BCs are time-dependent
- **After mesh motion** if BCs depend on mesh geometry

```cpp
// Example: Manual boundary condition correction
T.internalField() = someNewValues;
T.correctBoundaryConditions();  // Update patch fields based on BC type
```

**What `correctBoundaryConditions()` does:**
- `fixedValue` — Copies internal field values to boundary (no-op, values already set)
- `fixedGradient` — Recomputes boundary values from gradient specification
- `zeroGradient` — Copies adjacent cell values to boundary faces
- `mixed` / `coded` — Recomputes based on BC-specific logic

**Performance tip:** Only call `correctBoundaryConditions()` when necessary. It triggers virtual function calls on all patches and can be expensive for large boundary meshes.

### Common Boundary Condition Operations

```cpp
// Find patch by name
label inletI = mesh.boundaryMesh().findPatchID("inlet");

// Check if patch exists
if (inletI != -1)
{
    // Get const reference (read-only)
    const scalarField& Tin = T.boundaryField()[inletI];
    
    // Get non-const reference (writable)
    scalarField& Tin = T.boundaryFieldRef()[inletI];
    
    // Assign fixed value
    T.boundaryFieldRef()[inletI] == fixedValue;
    
    // Correct after modification
    T.correctBoundaryConditions();
}
```

---

## 7. Performance Considerations

### Memory Access Patterns

**DO:**
```cpp
// Sequential access (cache-friendly)
scalarField& Ti = T.ref();
forAll(Ti, cellI)
{
    Ti[cellI] = compute(cellI);
}
```

**DON'T:**
```cpp
// Random access (cache misses)
forAll(T, cellI)
{
    T[randomIndex[cellI]] = compute(cellI);
}
```

### Internal Field vs Boundary Field Access

| Operation | Relative Performance | Notes |
|-----------|---------------------|-------|
| `T.internalField()[i]` | 1x (baseline) | Direct memory access |
| `T.ref()[i]` | 1x (baseline) | Same as internalField |
| `T[cellI]` | 2-5x slower | Bounds checking overhead |
| `T.boundaryField()[patchI][faceI]` | 10-50x slower | Virtual function dispatch |

**Optimization strategy:** Minimize boundary field access in tight loops. Cache boundary field references when performing multiple operations on the same patch.

### Field Creation Cost

| Operation | Cost | Notes |
|-----------|------|-------|
| `volScalarField T2(T1)` | High | Deep copy, allocates new memory |
| `volScalarField T2(T1.name(), T1)` | High | Same as copy constructor |
| `auto Tptr = T1.clone()` | High | Polymorphic clone (use sparingly) |
| `volScalarField::New(...)` | Medium | Smart pointer allocation |
| Reference aliasing (`T1.ref()`) | Zero | No memory allocation |

**Best practice:** Reuse existing field memory when possible. Use references and `ref()` instead of creating temporary fields in performance-critical code.

---

## Quick Reference

| Operation | Syntax | Returns | Performance |
|-----------|--------|---------|-------------|
| **Access cell** | `T[cellI]` | `scalar&` | Slow (bounds check) |
| **Internal field** | `T.internalField()` or `T.ref()` | `scalarField&` | Fast (direct) |
| **Boundary field** | `T.boundaryField()[patchI]` | `fvPatchScalarField` | Slow (virtual) |
| **Gradient** | `fvc::grad(T)` | `volVectorField` | Medium (new field) |
| **Divergence** | `fvc::div(phi)` | `volScalarField` | Medium (new field) |
| **Laplacian** | `fvc::laplacian(alpha, T)` | `volScalarField` | Medium (new field) |
| **Maximum** | `max(T).value()` | `scalar` | Fast (reduction) |
| **Minimum** | `min(T).value()` | `scalar` | Fast (reduction) |
| **Average** | `average(T).value()` | `scalar` | Fast (reduction) |
| **Volume integral** | `gSum(T * mesh.V())` | `scalar` | Fast (reduction) |
| **Correct BCs** | `T.correctBoundaryConditions()` | `void` | Slow (all patches) |

---

## 🎯 Key Takeaways

- **volFields store ONE value per cell** at the cell center — this is their defining characteristic
- The `vol` prefix means "volume" but data is actually stored at **cell centers**, not distributed throughout the cell volume
- **Always call `correctBoundaryConditions()`** after modifying internal field or after solving to update boundary values consistently
- Use `internalField()` for cell values and `boundaryField()[patchI]` for patch face values
- Calculus operations (`fvc::grad`, `fvc::div`, `fvc::laplacian`) return NEW fields — they do NOT modify the original field in-place
- **Performance matters:** Internal field access is 10-50x faster than boundary field access — use `T.ref()` for bulk operations
- For non-uniform meshes, use volume-weighted statistics instead of arithmetic averages to account for varying cell sizes

---

## 🧠 Concept Check

<details>
<summary><b>1. volScalarField อยู่ที่ไหน?</b></summary>

**Cell centers** — ค่าหนึ่งค่าต่อ cell ณ จุดศูนย์ถ่วงของเซลล์  
Each cell holds exactly ONE scalar value at its centroid

</details>

<details>
<summary><b>2. What's the difference between internalField and boundaryField?</b></summary>

- **internalField** — All cell values (interior domain)
- **boundaryField** — Face values on boundary patches only  
Memory layout: `[internalField | boundaryField[0] | boundaryField[1] | ... ]`

</details>

<details>
<summary><b>3. When should you call correctBoundaryConditions()?</b></summary>

**After** any operation that invalidates boundary consistency:
- After solving (automatic)
- After manual internal field modification
- After time step for time-dependent BCs
- After mesh motion for geometry-dependent BCs

</details>

<details>
<summary><b>4. Why do fvc:: operations return NEW fields instead of modifying in-place?</b></summary>

**Functional programming design** — enables expression templates and operator chaining:
```cpp
volScalarField lapT = fvc::laplacian(kappa, fvc::grad(T) & fvc::grad(T));
```
Original field remains unchanged unless explicitly assigned

</details>

<details>
<summary><b>5. Why is internalField access faster than boundaryField access?</b></summary>

**Internal field:** Direct memory access through `scalarField&` (contiguous array)  
**Boundary field:** Virtual function dispatch through `fvPatchField` polymorphic interface

Performance difference: 10-50x slower for boundary field access due to indirect function calls and non-contiguous memory layout.

</details>

---

## 📖 Related Documentation

- **ภาพรวม:** [00_Overview.md](00_Overview.md) — Field hierarchy and design philosophy
- **Surface Fields:** [03_Surface_Fields.md](03_Surface_Fields.md) — Face-centered fields for flux calculations
- **Point Values:** [04_Point_Values.md](04_Point_Values.md) — Interpolation from cell centers to mesh points
- **Dimension Checking:** [06_Dimensional_Checking.md](06_Dimensional_Checking.md) — Dimension consistency for field operations
- **Common Pitfalls:** [07_Common_Pitfalls.md](07_Common_Pitfalls.md) — Memory management and performance issues

---

## Next Steps

Practice creating and manipulating volume fields in the exercises section. Then proceed to [Surface Fields](03_Surface_Fields.md) to understand face-based field representations used in finite volume flux calculations.