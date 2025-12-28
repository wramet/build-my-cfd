# Non-Newtonian Numerical Implementation

การ Implement Non-Newtonian ใน OpenFOAM

---

## Overview

> Non-Newtonian viscosity depends on **shear rate**

---

## 1. Viscosity Model Interface

```cpp
// In transportModel
tmp<volScalarField> nu() const
{
    return calcNu(strainRate());
}

// Strain rate
tmp<volScalarField> strainRate()
{
    return sqrt(2.0) * mag(symm(fvc::grad(U)));
}
```

---

## 2. Power Law Model

```cpp
volScalarField nu = k * pow(strainRate, n - 1);

// k = consistency index
// n = power law index (n < 1: shear thinning)
```

---

## 3. Cross Model

```cpp
volScalarField nu = nuInf + (nu0 - nuInf)
    / (1 + pow(m * strainRate, n));

// nu0 = zero shear viscosity
// nuInf = infinite shear viscosity
```

---

## 4. Dictionary Setup

```cpp
// constant/transportProperties
transportModel  CrossPowerLaw;

CrossPowerLawCoeffs
{
    nu0     1e-3;
    nuInf   1e-6;
    m       1.0;
    n       0.5;
}
```

---

## 5. Implicit Treatment

```cpp
// For stability, treat viscosity implicitly
fvVectorMatrix UEqn
(
    fvm::ddt(rho, U)
  + fvm::div(phi, U)
  - fvm::laplacian(nu, U)  // nu from model
);
```

---

## 6. Numerical Issues

| Issue | Solution |
|-------|----------|
| Infinite viscosity | Min/max limits |
| Strain rate = 0 | Add SMALL |
| Instability | Under-relax viscosity |

```cpp
nu = max(nu, nuMin);
nu = min(nu, nuMax);
```

---

## Quick Reference

| Model | Equation |
|-------|----------|
| Power Law | η = k γ̇^(n-1) |
| Cross | η = η∞ + (η₀-η∞)/(1+(mγ̇)^n) |
| Carreau | η = η∞ + (η₀-η∞)(1+(λγ̇)²)^((n-1)/2) |

---

## Concept Check

<details>
<summary><b>1. Shear thinning คืออะไร?</b></summary>

**Viscosity ลด** เมื่อ shear rate เพิ่ม (n < 1)
</details>

<details>
<summary><b>2. ทำไมต้อง limit viscosity?</b></summary>

**Prevent infinite** values at zero shear rate
</details>

<details>
<summary><b>3. Strain rate คำนวณอย่างไร?</b></summary>

**√2 |symm(∇U)|** — magnitude of strain tensor
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Viscosity Models:** [02_Viscosity_Models.md](02_Viscosity_Models.md)
