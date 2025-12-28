# Non-Newtonian Practical Usage

การใช้งาน Non-Newtonian ในทางปฏิบัติ

---

## Overview

> Setup และ run Non-Newtonian simulations

---

## 1. Solver Selection

| Solver | Use |
|--------|-----|
| `simpleFoam` | Steady incompressible |
| `pimpleFoam` | Transient incompressible |
| `viscoelasticFluidFoam` | Viscoelastic |
| `rheoFoam` | Advanced rheology |

---

## 2. Transport Properties

```cpp
// constant/transportProperties
transportModel  CrossPowerLaw;

CrossPowerLawCoeffs
{
    nu0     0.01;      // Zero shear viscosity
    nuInf   0.0001;    // Infinite shear viscosity
    m       0.1;       // Time constant
    n       0.5;       // Power index
}
```

---

## 3. Common Materials

| Material | Model | n |
|----------|-------|---|
| Blood | Carreau | 0.35 |
| Polymer | Power Law | 0.2-0.6 |
| Paint | Herschel-Bulkley | 0.4-0.8 |
| Cement | Bingham | - |

---

## 4. Mesh Considerations

```cpp
// Fine mesh near walls for shear rate
// Capture shear-thinning effects

blocks
(
    hex (...)
    (20 100 1)  // More cells in y (wall-normal)
    simpleGrading (1 0.1 1)
);
```

---

## 5. Convergence Tips

```cpp
// system/fvSolution
relaxationFactors
{
    equations
    {
        U       0.5;  // Reduce for stability
        p       0.3;
    }
}
```

---

## 6. Post-Processing

```cpp
// View viscosity field
functions
{
    viscosity
    {
        type    writeObjects;
        objects (nu);
    }
}
```

---

## Quick Reference

| Task | Setting |
|------|---------|
| Model | `transportModel` in transportProperties |
| Parameters | Model-specific Coeffs |
| Stability | Lower relaxation |
| Output | Write nu field |

---

## 🧠 Concept Check

<details>
<summary><b>1. simpleFoam ใช้กับ non-Newtonian ได้ไหม?</b></summary>

**ใช่** — just set transportModel
</details>

<details>
<summary><b>2. Mesh near wall สำคัญไหม?</b></summary>

**มาก** — capture high shear rate region
</details>

<details>
<summary><b>3. ทำไม convergence ยาก?</b></summary>

**Nonlinear viscosity** — changes with solution
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Implementation:** [04_Numerical_Implementation.md](04_Numerical_Implementation.md)
