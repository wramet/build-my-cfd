# Verification - Introduction

บทนำ Verification

---

## Overview

> **Verification** = Are we solving the equations correctly?

---

## 1. Verification Types

| Type | Check |
|------|-------|
| **Code** | Implementation correct? |
| **Solution** | Solver converges? |
| **Calculation** | Results consistent? |

---

## 2. Method of Manufactured Solutions (MMS)

```cpp
// Create exact solution
volScalarField Texact
(
    mesh,
    dimensionedScalar("T", dimTemperature, 0)
);

forAll(Texact, cellI)
{
    scalar x = mesh.C()[cellI].x();
    Texact[cellI] = sin(x);  // Known solution
}

// Calculate source term for this solution
volScalarField source = fvc::laplacian(alpha, Texact);

// Solve with source
solve(fvm::laplacian(alpha, T) == source);

// Compare
scalar error = gSum(mag(T - Texact) * mesh.V()) / gSum(mesh.V());
```

---

## 3. Order of Accuracy

```bash
# Run with different mesh sizes
for n in 10 20 40 80; do
    blockMesh -dict system/blockMeshDict.$n
    solver
    # Record error
done

# Should see error ~ h^p (p = order of scheme)
```

---

## 4. Conservation Check

```cpp
// Mass conservation
scalar massIn = gSum(phi.boundaryField()[inlet]);
scalar massOut = gSum(phi.boundaryField()[outlet]);

if (mag(massIn + massOut) > SMALL)
{
    Warning << "Mass not conserved";
}
```

---

## Quick Reference

| Check | Method |
|-------|--------|
| Implementation | MMS |
| Convergence | Residuals |
| Order | Grid refinement |
| Conservation | Flux balance |

---

## Concept Check

<details>
<summary><b>1. MMS คืออะไร?</b></summary>

**Manufactured Solution** — create exact answer, verify solver finds it
</details>

<details>
<summary><b>2. Order of accuracy ตรวจอย่างไร?</b></summary>

**Grid refinement study** — error should decrease as h^p
</details>

<details>
<summary><b>3. Conservation check ทำอะไร?</b></summary>

**Verify fluxes balance** — in = out
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Architecture:** [03_OpenFOAM_Architecture.md](03_OpenFOAM_Architecture.md)
