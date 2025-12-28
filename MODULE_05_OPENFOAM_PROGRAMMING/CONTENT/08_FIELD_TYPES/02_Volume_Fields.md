# Volume Fields

Volume Fields ใน OpenFOAM

---

## Overview

> **volField** = Cell-centered field values

---

## 1. Common Types

| Alias | Full Type |
|-------|-----------|
| `volScalarField` | `GeometricField<scalar, fvPatchField, volMesh>` |
| `volVectorField` | `GeometricField<vector, fvPatchField, volMesh>` |
| `volTensorField` | `GeometricField<tensor, fvPatchField, volMesh>` |
| `volSymmTensorField` | `GeometricField<symmTensor, fvPatchField, volMesh>` |

---

## 2. Creation

### From File

```cpp
volScalarField p
(
    IOobject("p", runTime.timeName(), mesh, IOobject::MUST_READ),
    mesh
);
```

### With Initial Value

```cpp
volVectorField U
(
    IOobject("U", runTime.timeName(), mesh, IOobject::NO_READ),
    mesh,
    dimensionedVector("U", dimVelocity, vector::zero)
);
```

---

## 3. Access

### Internal Field

```cpp
// Access cell values
forAll(T, cellI)
{
    T[cellI] = compute(cellI);
}

// Or use internal field reference
const scalarField& Ti = T.internalField();
```

### Boundary Field

```cpp
forAll(T.boundaryField(), patchI)
{
    scalarField& Tp = T.boundaryFieldRef()[patchI];
}
```

---

## 4. Operations

### Arithmetic

```cpp
volScalarField rhoU2 = rho * magSqr(U);
volScalarField Ttotal = T1 + T2;
```

### Calculus

```cpp
volVectorField gradT = fvc::grad(T);
volScalarField divU = fvc::div(phi);
volScalarField lapT = fvc::laplacian(alpha, T);
```

---

## 5. Statistics

```cpp
scalar maxT = max(T).value();
scalar minT = min(T).value();
scalar avgT = average(T).value();
scalar sumT = gSum(T * mesh.V());  // Volume-weighted
```

---

## 6. Boundary Conditions

```cpp
// Access patch by name
label inletI = mesh.boundaryMesh().findPatchID("inlet");

// Get/set values
const scalarField& Tin = T.boundaryField()[inletI];
T.boundaryFieldRef()[inletI] == fixedValue;

// Correct after solve
T.correctBoundaryConditions();
```

---

## Quick Reference

| Method | Description |
|--------|-------------|
| `T[cellI]` | Access cell value |
| `T.boundaryField()[patchI]` | Access patch |
| `fvc::grad(T)` | Gradient |
| `fvc::div(phi)` | Divergence |
| `max(T).value()` | Maximum |

---

## Concept Check

<details>
<summary><b>1. volScalarField อยู่ที่ไหน?</b></summary>

**Cell centers** — ค่าหนึ่งค่าต่อ cell
</details>

<details>
<summary><b>2. boundaryField vs internalField?</b></summary>

- **internal**: All cells
- **boundary**: Patch faces only
</details>

<details>
<summary><b>3. correctBoundaryConditions() ทำอะไร?</b></summary>

**Update boundary values** ตาม BC type
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Surface Fields:** [03_Surface_Fields.md](03_Surface_Fields.md)