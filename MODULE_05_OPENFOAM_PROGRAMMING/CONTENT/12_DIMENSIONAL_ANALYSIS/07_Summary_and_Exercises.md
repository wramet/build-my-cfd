# Summary and Exercises

สรุปและแบบฝึกหัด

---

## Summary

### Key Concepts

| Concept | Description |
|---------|-------------|
| dimensionSet | 7 exponents |
| dimensionedScalar | Value + name + dims |
| Automatic checking | Operations verify dims |
| Non-dim | Scale to dimless |

### Common Dimensions

| Name | Use |
|------|-----|
| `dimVelocity` | m/s |
| `dimPressure` | Pa |
| `dimTemperature` | K |
| `dimless` | - |

---

## Exercise 1: Create Quantities

```cpp
// Thermal conductivity
dimensionedScalar k
(
    "k",
    dimPower / dimLength / dimTemperature,
    0.6
);

// Specific heat
dimensionedScalar Cp
(
    "Cp",
    dimEnergy / dimMass / dimTemperature,
    4180
);
```

---

## Exercise 2: Verify Equation

```cpp
// Energy equation: ρCp(∂T/∂t) = k∇²T

// Check dimensions:
// LHS: [kg/m³][J/(kg·K)][K/s] = [J/(m³·s)] = [W/m³]
// RHS: [W/(m·K)][K/m²] = [W/m³] ✓

fvScalarMatrix TEqn
(
    fvm::ddt(rho * Cp, T)
 ==
    fvm::laplacian(k, T)
);
```

---

## Exercise 3: Non-Dimensional

```cpp
// Calculate Reynolds number
dimensionedScalar Re = U * L / nu;

// Calculate Prandtl number
dimensionedScalar Pr = nu / alpha;

// Both should be dimensionless
assert(Re.dimensions().dimensionless());
assert(Pr.dimensions().dimensionless());
```

---

## Exercise 4: Source Term

```cpp
// Heat source [W/m³]
dimensionedScalar Q("Q", dimPower/dimVolume, 1e6);

// Add to equation
fvScalarMatrix TEqn
(
    fvm::ddt(rho * Cp, T)
 ==
    fvm::laplacian(k, T)
  + Q
);
```

---

## Quick Reference

| Task | Code |
|------|------|
| Create | `dimensionedScalar("name", dims, val)` |
| Check | `.dimensions().dimensionless()` |
| Access | `.value()` |
| Combine | `dims1 * dims2` |

---

## Concept Check

<details>
<summary><b>1. k มี dimension อะไร?</b></summary>

**[W/(m·K)]** = dimPower / dimLength / dimTemperature
</details>

<details>
<summary><b>2. Source term ใน energy equation?</b></summary>

**[W/m³]** = dimPower / dimVolume
</details>

<details>
<summary><b>3. Re dimensionless ไหม?</b></summary>

**ใช่** — UL/ν = [m/s][m]/[m²/s] = dimless
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Applications:** [05_Advanced_Applications.md](05_Advanced_Applications.md)