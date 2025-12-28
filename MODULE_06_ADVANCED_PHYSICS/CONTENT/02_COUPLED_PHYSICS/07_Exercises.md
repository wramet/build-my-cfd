# Coupled Physics - Exercises

แบบฝึกหัด Coupled Physics

---

## Exercise 1: Conjugate Heat Transfer

```cpp
// Setup solid region
solidThermo thermo(mesh);

// Thermal conductivity
volScalarField kappa = thermo.kappa();

// Solve energy equation
fvScalarMatrix TEqn
(
    fvm::ddt(rho, cp, T)
  - fvm::laplacian(kappa, T)
);
TEqn.solve();
```

---

## Exercise 2: Multi-Region Setup

```cpp
// constant/regionProperties
regions
(
    fluid  (fluid)
    solid  (solid)
);

// In solver
forAll(fluidRegions, i)
{
    #include "setRegionFluidFields.H"
    #include "solveFluid.H"
}

forAll(solidRegions, i)
{
    #include "setRegionSolidFields.H"
    #include "solveSolid.H"
}
```

---

## Exercise 3: Interface Boundary

```cpp
// 0/T boundary
interface
{
    type            compressible::turbulentTemperatureCoupledBaffleMixed;
    Tnbr            T;
    kappaMethod     fluidThermo;
    value           uniform 300;
}
```

---

## Exercise 4: Object Registry Lookup

```cpp
// Access field from another region
const fvMesh& nbrMesh = runTime.lookupObject<fvMesh>(nbrRegion);
const volScalarField& nbrT = nbrMesh.lookupObject<volScalarField>("T");
```

---

## Exercise 5: Basic Coupled Case

```bash
# Run chtMultiRegionFoam
cd tutorials/heatTransfer/chtMultiRegionFoam/coolingChip
./Allrun
```

---

## Quick Reference

| Task | Code/Command |
|------|--------------|
| Multi-region | chtMultiRegionFoam |
| Interface BC | turbulentTemperatureCoupledBaffleMixed |
| Lookup region | `runTime.lookupObject<fvMesh>()` |
| Split mesh | splitMeshRegions |

---

## Concept Check

<details>
<summary><b>1. CHT ทำอะไร?</b></summary>

**Conjugate Heat Transfer** — solve heat in fluid + solid together
</details>

<details>
<summary><b>2. Interface BC ทำอะไร?</b></summary>

**Exchange heat** ระหว่าง regions
</details>

<details>
<summary><b>3. splitMeshRegions ใช้เมื่อไหร่?</b></summary>

**Split mesh** into multiple regions by cellZone
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **CHT:** [02_Conjugate_Heat_Transfer.md](02_Conjugate_Heat_Transfer.md)
