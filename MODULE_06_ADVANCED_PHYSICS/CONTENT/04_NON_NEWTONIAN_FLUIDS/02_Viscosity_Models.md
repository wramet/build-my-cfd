# Viscosity Models

Non-Newtonian Viscosity Models

---

## Overview

> Models for shear-rate dependent viscosity

---

## 1. Power Law

```
η = k γ̇^(n-1)

k = consistency index
n = power index
n < 1: shear thinning
n > 1: shear thickening
```

```cpp
// constant/transportProperties
transportModel  powerLaw;
powerLawCoeffs
{
    nuMax   1e-3;
    nuMin   1e-6;
    k       0.01;
    n       0.5;
}
```

---

## 2. Cross Model

```
η = η∞ + (η₀ - η∞) / (1 + (m γ̇)^n)

η₀ = zero shear viscosity
η∞ = infinite shear viscosity
m = time constant
```

```cpp
transportModel  CrossPowerLaw;
CrossPowerLawCoeffs
{
    nu0     0.01;
    nuInf   0.0001;
    m       0.1;
    n       0.5;
}
```

---

## 3. Carreau Model

```
η = η∞ + (η₀ - η∞)(1 + (λγ̇)²)^((n-1)/2)

λ = relaxation time
```

---

## 4. Bingham Plastic

```
τ = τy + η_p γ̇  (if τ > τy)
γ̇ = 0           (if τ < τy)

τy = yield stress
η_p = plastic viscosity
```

---

## 5. Herschel-Bulkley

```
τ = τy + k γ̇^n  (if τ > τy)

Combines yield stress + power law
```

---

## 6. Comparison

| Model | Parameters | Use |
|-------|------------|-----|
| Power Law | k, n | Simple fluids |
| Cross | η₀, η∞, m, n | Polymers |
| Carreau | η₀, η∞, λ, n | Blood |
| Bingham | τy, ηp | Cement |

---

## Quick Reference

| Material | Model |
|----------|-------|
| Polymer solution | Cross, Carreau |
| Blood | Carreau |
| Paint | Herschel-Bulkley |
| Toothpaste | Bingham |

---

## Concept Check

<details>
<summary><b>1. n < 1 หมายความว่าอะไร?</b></summary>

**Shear-thinning** — viscosity decreases with shear
</details>

<details>
<summary><b>2. Yield stress ทำให้เกิดอะไร?</b></summary>

**No flow** จนกว่า stress > τy
</details>

<details>
<summary><b>3. Cross ดีกว่า Power Law อย่างไร?</b></summary>

**Proper Newtonian limits** ที่ low/high shear
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Architecture:** [03_OpenFOAM_Architecture.md](03_OpenFOAM_Architecture.md)