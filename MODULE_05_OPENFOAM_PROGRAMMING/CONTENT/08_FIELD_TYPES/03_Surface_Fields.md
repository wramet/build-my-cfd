# Surface Fields

Surface fields in OpenFOAM

---

## Learning Objectives

By the end of this section, you will be able to:
- Identify when to use surface fields versus volume fields
- Create and manipulate surface field types in OpenFOAM
- Compute fluxes using interpolation schemes
- Apply divergence operators to convert surface fields to volume fields
- Access and iterate over face-centered data
- Understand the physical meaning of flux conservation

**Prerequisites:** Familiarity with volume fields (see [02_Volume_Fields.md](02_Volume_Fields.md)), basic finite volume concepts
**Difficulty:** Intermediate
**Estimated Reading Time:** 15 minutes

---

## Overview

> **surfaceField** = Face-centered field values (one value per face)

Surface fields store values at face centers rather than cell centers. They are fundamental to finite volume methods because:
- **Conservation laws are enforced at faces** (flux enters/leaves cells through faces)
- **Boundary conditions are applied at faces** (walls, inlets, outlets)
- **Flux calculations require face values** (mass, momentum, energy transport)

---

## 1. What: Physical Meaning of Surface Fields

### Why Face-Centered Values Matter

In finite volume methods, we solve conservation equations:
```
d/dt ∫(ρU) dV + ∮(ρU)U·dS = ∫∇·τ dV
                   ↑
                   Flux through faces
```

**Key physical insight:** 
- Volume fields store cell-averaged values (what's **inside** the control volume)
- Surface fields store face-centered values (what crosses the **boundary** of the control volume)
- **Flux = transported quantity × face area**: Always computed at faces

### Flux Conservation

For any conserved quantity (mass, momentum, energy):
```
Flux out - Flux in = Accumulation + Source
     ↑              ↑
   face-based    cell-based
```

This is why OpenFOAM separates:
- `volField<T>`: Storage and solution
- `surfaceField<T>`: Transport and flux calculations

---

## 2. When to Use Surface Fields

| Scenario | Use Surface Field | Physical Reason |
|----------|-------------------|-----------------|
| **Flux calculations** | `surfaceScalarField phi` | Flux crosses faces, not cells |
| **Face-based operations** | `surfaceVectorField Sf` | Boundary conditions at faces |
| **Interpolation** | `fvc::interpolate(T)` | Need values at cell interfaces |
| **Divergence operations** | `fvc::div(phi)` | Computes sum over face fluxes per cell |
| **Gradient reconstruction** | `fvc::grad(p)` | Uses face values for cell gradients |
| **Convective terms** | All flux-based terms | Conservation enforced at face level |

**Rule of thumb:** Use surface fields whenever computing transport across cell boundaries.

---

## 3. Common Types

| Alias | Template Type | Typical Use | Dimensions |
|-------|---------------|-------------|------------|
| `surfaceScalarField` | `SurfaceField<scalar>` | Flux (phi), face magnitudes | Various (flux: [L³T⁻¹]) |
| `surfaceVectorField` | `SurfaceField<vector>` | Face areas (Sf), face normals | [L²] |
| `surfaceTensorField` | `SurfaceField<tensor>` | Stress at faces | Various |

---

## 4. Creation and Initialization

### From Mesh (Geometric Quantities)

```cpp
// Face area vectors: normal × area
const surfaceVectorField& Sf = mesh.Sf();

// Face area magnitudes (just the area)
const surfaceScalarField& magSf = mesh.magSf();

// Face unit normals: Sf / |Sf|
surfaceVectorField nf = mesh.Sf() / mesh.magSf();
```

### Computed from Volume Fields (Flux Calculation)

```cpp
// Volume flux: U · Sf (velocity dot face area)
surfaceScalarField phi = fvc::flux(U);

// Interpolate cell values to faces
surfaceScalarField rhof = fvc::interpolate(rho);
surfaceVectorField Uf = fvc::interpolate(U);

// Using specific interpolation scheme
surfaceScalarField pF = fvc::interpolate(p, "linear");
```

---

## 5. Interpolation: Cell Values → Face Values

### Physical Reasoning

Cell-centered values represent averages over cell volumes. To compute flux across a face, we need the value **at the face** where transport actually occurs:

```
Cell P (owner)          Cell N (neighbor)
    |--------|--------|
           ^ 
           | Face f
    φ = U · Sf computed here
```

### Common Schemes

| Scheme | Formula | Stability | When to Use |
|--------|---------|-----------|-------------|
| `linear` | Arithmetic mean | Conditional (may oscillate) | Smooth fields, structured meshes |
| `upwind` | Upstream cell value | Unconditionally stable | Dominant convection, robust simulations |
| `central` | Central differencing | Conditional | Symmetric transport, low convection |
| `linearUpwind` | Linear + upwind bias | Stable | Accurate convection with stability |

### Code Examples

```cpp
// Default interpolation (uses scheme from fvSchemes)
surfaceScalarField Uf = fvc::interpolate(U);

// Explicit scheme selection
surfaceScalarField T_f = fvc::interpolate(T, "linearUpwind");

// Physical flux: U interpolated to faces · face area
surfaceScalarField phi = fvc::interpolate(U) & mesh.Sf();

// Compact equivalent using flux utility
surfaceScalarField phi = fvc::flux(U);
```

**See 00_Overview.md:Section 4** for complete interpolation scheme comparison.

---

## 6. Flux Calculations

### Volume Flux (φ)

```cpp
// Method 1: Interpolate then dot with Sf
surfaceScalarField phi = fvc::interpolate(U) & mesh.Sf();

// Method 2: Use flux utility (preferred)
surfaceScalarField phi = fvc::flux(U);

// Physical meaning: [m/s] · [m²] = [m³/s]
```

### Mass Flux (ρφ)

```cpp
// Method 1: Density × volume flux
surfaceScalarField rhoPhi = fvc::interpolate(rho) * phi;

// Method 2: Interpolate (ρU) then dot
surfaceScalarField rhoPhi = fvc::interpolate(rho * U) & mesh.Sf();

// Physical meaning: [kg/m³] · [m³/s] = [kg/s]
```

### Momentum Flux

```cpp
// Convective flux: (ρU)U · Sf
surfaceVectorField phiU = fvc::interpolate(rho * U) * (fvc::interpolate(U) & mesh.Sf());

// Compact form using flux utility
surfaceVectorField phiU = fvc::flux(phi, U);

// Physical meaning: [kg/s] · [m/s] = [kg·m/s²] = [N]
```

### Energy Flux

```cpp
// Enthalpy flux: ρφh
surfaceScalarField rhoPhiH = fvc::interpolate(rho * h) * phi;

// Total energy flux: ρφ(E + p/ρ)
surfaceScalarField rhoPhiE = fvc::interpolate(rho * (E + p/rho)) * phi;
```

---

## 7. Access Patterns

### Internal Faces

```cpp
// Loop over all internal faces
forAll(phi, faceI)
{
    scalar flux = phi[faceI];
    scalar area = mesh.magSf()[faceI];
    vector normal = mesh.Sf()[faceI] / area;
}

// Access owner and neighbor cells
forAll(mesh.owner(), faceI)
{
    label own = mesh.owner()[faceI];  // Owner cell
    label nei = mesh.neighbour()[faceI]; // Neighbor cell
    
    // Flux from own to nei (positive if own → nei)
    scalar flux = phi[faceI];
}
```

### Boundary Faces

```cpp
// Access boundary patch
forAll(phi.boundaryField(), patchI)
{
    const fvsPatchScalarField& phip = phi.boundaryField()[patchI];
    
    forAll(phip, faceI)
    {
        scalar flux = phip[faceI];
    }
}

// Example: Zero flux at walls
label wallPatchID = mesh.boundaryMesh().findPatchID("wall");
phi.boundaryFieldRef()[wallPatchID] = 0.0;
```

---

## 8. Surface ↔ Volume Conversions

### Surface → Volume (Divergence)

```cpp
// Divergence: sum of face fluxes per cell
// Physical meaning: net source/sink at each cell
volScalarField divPhi = fvc::div(phi);     // ∇·φ
volVectorField divU = fvc::div(phi, U);    // ∇·(φU)

// Conservation check: for incompressible flow, ∇·U = 0
volScalarField divU_check = fvc::div(phi);
Info << "Max div(U) = " << max(divU_check).value() << endl;
```

### Surface → Volume (Averaging)

```cpp
// Average face values to cell centers
volScalarField avgPhi = fvc::average(phi);

// Sum face values per cell (not average)
volScalarField sumPhi = fvc::surfaceSum(phi);
```

### Volume → Surface → Volume (Reconstruction)

```cpp
// Volume → Surface
surfaceScalarField phi = fvc::flux(U);

// Surface → Volume (compute divergence)
volScalarField divU = fvc::div(phi);

// Volume → Surface again
surfaceScalarField phi_corrected = fvc::interpolate(divU);
```

---

## 9. Common Pitfalls

### 1. Inconsistent Interpolation Schemes

**Problem:** Using different schemes for `rho` and `U` when computing `rhoPhi`

```cpp
// WRONG: Different schemes
surfaceScalarField rhof = fvc::interpolate(rho, "upwind");
surfaceScalarField Uf = fvc::interpolate(U, "linear");
surfaceScalarField rhoPhi = rhof * (Uf & mesh.Sf());

// CORRECT: Same scheme or use flux()
surfaceScalarField rhoPhi = fvc::flux(rho, U);
```

### 2. Boundary Condition Violation

**Problem:** Forgetting to enforce zero flux at walls

```cpp
// After computing flux, enforce wall BC
label wallPatchID = mesh.boundaryMesh().findPatchID("wall");
phi.boundaryFieldRef()[wallPatchID] = 0.0;
phi.correctBoundaryConditions();
```

### 3. Dimension Mismatch

**Problem:** Flux has wrong dimensions

```cpp
// Check dimensions
Info << "Phi dimensions: " << phi.dimensions() << endl;
// Volume flux should be: [0 3 -1 0 0 0 0] (m³/s)
// Mass flux should be: [1 0 -1 0 0 0 0] (kg/s)
```

**See 07_Pitfalls.md** for comprehensive error patterns.

---

## Quick Reference

| Operation | Code | Result Type | Physical Meaning |
|-----------|------|-------------|------------------|
| Face area vectors | `mesh.Sf()` | `surfaceVectorField` | Direction × area |
| Face magnitudes | `mesh.magSf()` | `surfaceScalarField` | Just the area |
| Interpolate | `fvc::interpolate(T)` | `surface...Field` | Cell → face values |
| Compute flux | `fvc::flux(U)` | `surfaceScalarField` | Volume flux [m³/s] |
| Mass flux | `fvc::flux(rho, U)` | `surfaceScalarField` | Mass flux [kg/s] |
| Divergence | `fvc::div(phi)` | `volScalarField` | ∇·φ per cell |
| Average | `fvc::average(phi)` | `volScalarField` | Face → cell average |
| Surface sum | `fvc::surfaceSum(phi)` | `volScalarField` | Sum of face values |

---

## Key Takeaways

- **Surface fields live at faces**—one value per face, used for transport calculations
- **Flux = velocity · face area**: Physical transport always happens across faces, not cells
- **Interpolation bridges cell and face values**: Essential because conserved quantities cross cell boundaries at faces
- **Divergence converts surface to volume**: Summing face fluxes gives net source/sink per cell (∇·φ)
- **Mass flux = density × volume flux**: Always account for density in compressible flows
- **Conservation is enforced at faces**: This is why finite volume methods use surface fields for flux calculations
- **Choose interpolation schemes carefully**: Balance accuracy (linear) vs. stability (upwind)
- **Check boundary conditions**: Walls should have zero flux for normal velocity

---

## 🧠 Concept Check

<details>
<summary><b>1. Where are surface field values located?</b></summary>

**At face centers**—one value per face, not per cell

**Physical meaning:** These represent the value of a quantity exactly at the location where transport occurs between cells
</details>

<details>
<summary><b>2. What are the dimensions of volume flux (φ)?</b></summary>

**[L³T⁻¹]** = [m³/s] (cubic meters per second)

**Mass flux:** [MT⁻¹] = [kg/s]
</details>

<details>
<summary><b>3. Why must we interpolate cell values to faces?</b></summary>

**Cell values → face values** for flux calculation

**Physical reason:** Transport equations involve flux integrals over cell faces: ∮φU·dS. We need values at the face to evaluate this integral.
</details>

<details>
<summary><b>4. When should you use a surface field instead of a volume field?</b></summary>

Use **surface fields** for:
- Computing fluxes (mass, momentum, energy transport)
- Applying boundary conditions at faces
- Operations requiring face-normal values (dot products with Sf)
- Divergence operations that sum face contributions

Use **volume fields** for:
- Storage and solution of transport equations
- Cell-centered post-processing and visualization
- Source terms defined per cell volume
- Time integration (solution variables)

**Key principle:** Solution variables are volume fields; flux calculations use surface fields
</details>

<details>
<summary><b>5. What is the physical meaning of ∇·φ (divergence of flux)?</b></summary>

**Net source/sink per unit volume**

Mathematically: ∇·φ = lim_(V→0) (1/V) ∮_∂V φ·dS

Physical interpretation:
- Positive: More flux leaving than entering (source)
- Negative: More flux entering than leaving (sink)
- Zero: Flux in = flux out (conserved, steady state)

**Example:** For incompressible flow, ∇·U = 0 ensures mass conservation
</details>

---

## 📚 Related Documentation

- **Overview:** [00_Overview.md](00_Overview.md) — Complete field type comparison table
- **Volume Fields:** [02_Volume_Fields.md](02_Volume_Fields.md) — Cell-centered field fundamentals
- **Dimensioned Fields:** [06_Dimensioned_Fields.md](06_Dimensioned_Fields.md) — Understanding flux dimensions
- **Point Fields:** [05_Point_Fields.md](05_Point_Fields.md) — Point interpolation comparison
- **Field Operations:** See [06_MATRICES_LINEARALGEBRA](../06_MATRICES_LINEARALGEBRA/00_Overview.md) for matrix operations