# GeometricFields - Introduction

บทนำ GeometricField

---

## Overview

> **GeometricField** = Core data structure for CFD fields

---

## 1. What is GeometricField?

A GeometricField combines:

| Component | Purpose |
|-----------|---------|
| **Values** | Numerical data |
| **Mesh** | Spatial location |
| **Dimensions** | Physical units |
| **Boundaries** | Patch conditions |

---

## 2. Template Parameters

```cpp
template<class Type, template<class> class PatchField, class GeoMesh>
class GeometricField
```

| Parameter | Examples |
|-----------|----------|
| `Type` | scalar, vector, tensor |
| `PatchField` | fvPatchField, fvsPatchField |
| `GeoMesh` | volMesh, surfaceMesh |

---

## 3. Common Field Types

### Volume Fields (Cell-centered)

```cpp
volScalarField p;   // Pressure
volVectorField U;   // Velocity
volTensorField R;   // Stress tensor
```

### Surface Fields (Face-centered)

```cpp
surfaceScalarField phi;  // Mass flux
surfaceVectorField Sf;   // Face area vectors
```

---

## 4. Basic Usage

### Create and Initialize

```cpp
volScalarField T
(
    IOobject("T", runTime.timeName(), mesh, IOobject::MUST_READ),
    mesh
);
```

### Access Values

```cpp
// Cell value
scalar T0 = T[0];

// All cells
forAll(T, cellI)
{
    T[cellI] = compute(cellI);
}
```

### Operations

```cpp
volScalarField T2 = sqr(T);
scalar maxT = max(T).value();
```

---

## 5. Why Not Just Arrays?

| Feature | Array | GeometricField |
|---------|-------|----------------|
| Dimension check | ❌ | ✅ |
| Mesh aware | ❌ | ✅ |
| Boundary handling | ❌ | ✅ |
| I/O integrated | ❌ | ✅ |
| Old time | ❌ | ✅ |

---

## Quick Reference

| Alias | Type | Location |
|-------|------|----------|
| `volScalarField` | scalar | Cell |
| `volVectorField` | vector | Cell |
| `surfaceScalarField` | scalar | Face |
| `surfaceVectorField` | vector | Face |

---

## Concept Check

<details>
<summary><b>1. GeometricField มีอะไรมากกว่า array?</b></summary>

**Mesh + Dimensions + BC + I/O + Old time**
</details>

<details>
<summary><b>2. vol vs surface field?</b></summary>

- **vol**: Cell centers
- **surface**: Face centers
</details>

<details>
<summary><b>3. ทำไมต้อง template?</b></summary>

**Code reuse** — same structure for scalar, vector, tensor
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Design Philosophy:** [02_Design_Philosophy.md](02_Design_Philosophy.md)