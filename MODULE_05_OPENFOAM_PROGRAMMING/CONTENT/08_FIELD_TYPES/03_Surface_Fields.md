# Surface Fields

Surface Fields ใน OpenFOAM

---

## Overview

> **surfaceField** = Face-centered field values

---

## 1. Common Types

| Alias | Use |
|-------|-----|
| `surfaceScalarField` | Flux (phi) |
| `surfaceVectorField` | Face areas (Sf) |

---

## 2. Why Surface Fields?

| Need | Use |
|------|-----|
| Mass/volume flux | `surfaceScalarField phi` |
| Face areas | `mesh.Sf()` |
| Cell-to-cell interpolation | `fvc::interpolate()` |

---

## 3. Creation

### From Mesh

```cpp
// Face area vectors
const surfaceVectorField& Sf = mesh.Sf();

// Face area magnitudes
const surfaceScalarField& magSf = mesh.magSf();
```

### Computed

```cpp
// Volume flux
surfaceScalarField phi = fvc::flux(U);

// Interpolated
surfaceScalarField rhof = fvc::interpolate(rho);
```

---

## 4. Flux Calculation

```cpp
// Volume flux
surfaceScalarField phi = fvc::interpolate(U) & mesh.Sf();

// Mass flux
surfaceScalarField rhoPhi = fvc::interpolate(rho) * phi;
// or
surfaceScalarField rhoPhi = fvc::interpolate(rho * U) & mesh.Sf();
```

---

## 5. Access

```cpp
// Internal faces
forAll(phi, faceI)
{
    scalar flux = phi[faceI];
}

// Boundary faces
forAll(phi.boundaryField(), patchI)
{
    const scalarField& phip = phi.boundaryField()[patchI];
}
```

---

## 6. Common Operations

```cpp
// Divergence (surface → volume)
volScalarField divPhi = fvc::div(phi);

// Average to cells
volScalarField avgPhi = fvc::average(phi);

// Sum face values per cell
volScalarField sumPhi = fvc::surfaceSum(phi);
```

---

## Quick Reference

| Need | Code |
|------|------|
| Face areas | `mesh.Sf()` |
| Interpolate | `fvc::interpolate(T)` |
| Compute flux | `fvc::flux(U)` |
| Divergence | `fvc::div(phi)` |

---

## Concept Check

<details>
<summary><b>1. surfaceField อยู่ที่ไหน?</b></summary>

**Face centers** — ค่าหนึ่งค่าต่อ face
</details>

<details>
<summary><b>2. phi มี dimension อะไร?</b></summary>

**[L^3 T^-1]** (volume flux) หรือ **[M T^-1]** (mass flux)
</details>

<details>
<summary><b>3. ทำไมต้อง interpolate?</b></summary>

**Cell values → face values** สำหรับ flux calculation
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Volume Fields:** [02_Volume_Fields.md](02_Volume_Fields.md)