# GeometricFields - Summary and Exercises

สรุปและแบบฝึกหัด GeometricFields

---

## Summary

### Key Concepts

| Concept | Description |
|---------|-------------|
| GeometricField | Field + Mesh + Dimensions + BC |
| Internal field | Cell-centered values |
| Boundary field | Per-patch values |
| dimensionSet | 7 SI base dimensions |

### Template Structure

```cpp
GeometricField<Type, PatchField, GeoMesh>
// Type: scalar, vector, tensor
// PatchField: fvPatchField, fvsPatchField
// GeoMesh: volMesh, surfaceMesh
```

---

## Exercise 1: Field Creation

### Task

สร้างฟิลด์ต่างๆ

```cpp
// Temperature field from file
volScalarField T
(
    IOobject("T", runTime.timeName(), mesh, IOobject::MUST_READ),
    mesh
);

// Velocity with initial value
volVectorField U
(
    IOobject("U", runTime.timeName(), mesh, IOobject::NO_READ),
    mesh,
    dimensionedVector("U", dimVelocity, vector::zero)
);
```

---

## Exercise 2: Field Operations

### Task

ทำ operations บน fields

```cpp
// Magnitude
volScalarField magU = mag(U);

// Component
volScalarField Ux = U.component(0);

// Math
volScalarField dynP = 0.5 * rho * magSqr(U);
```

---

## Exercise 3: Boundary Access

### Task

เข้าถึงและแก้ไข boundary values

```cpp
// Get patch index
label inletI = mesh.boundaryMesh().findPatchID("inlet");

// Read boundary values
const scalarField& Tin = T.boundaryField()[inletI];

// Modify boundary
T.boundaryFieldRef()[inletI] == 400.0;
```

---

## Exercise 4: Calculus Operations

### Task

ใช้ fvc operators

```cpp
// Gradient
volVectorField gradT = fvc::grad(T);

// Divergence
volScalarField divU = fvc::div(phi);

// Laplacian
volScalarField lapT = fvc::laplacian(alpha, T);
```

---

## Exercise 5: Write Custom Field

### Task

สร้างและเขียน custom field

```cpp
volScalarField customField
(
    IOobject
    (
        "customField",
        runTime.timeName(),
        mesh,
        IOobject::NO_READ,
        IOobject::AUTO_WRITE
    ),
    mesh,
    dimensionedScalar("cf", dimless, 0)
);

forAll(customField, cellI)
{
    customField[cellI] = cellI / mesh.nCells();
}

customField.write();
```

---

## Quick Reference

| Type | Location | Example |
|------|----------|---------|
| `volScalarField` | Cell | p, T |
| `volVectorField` | Cell | U |
| `surfaceScalarField` | Face | phi |

| Operation | Code |
|-----------|------|
| Gradient | `fvc::grad(p)` |
| Divergence | `fvc::div(U)` |
| Laplacian | `fvc::laplacian(k, T)` |

---

## Concept Check

<details>
<summary><b>1. IOobject arguments คืออะไร?</b></summary>

- **name**: Field name
- **time**: Time directory
- **registry**: Object database (mesh)
- **readOption**: MUST_READ, READ_IF_PRESENT, NO_READ
- **writeOption**: AUTO_WRITE, NO_WRITE
</details>

<details>
<summary><b>2. boundaryField vs boundaryFieldRef ต่างกันอย่างไร?</b></summary>

- **boundaryField()**: const access (read only)
- **boundaryFieldRef()**: non-const access (can modify)
</details>

<details>
<summary><b>3. forAll macro ทำอะไร?</b></summary>

`forAll(field, i)` = `for(label i=0; i<field.size(); i++)`
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Design Philosophy:** [02_Design_Philosophy.md](02_Design_Philosophy.md)