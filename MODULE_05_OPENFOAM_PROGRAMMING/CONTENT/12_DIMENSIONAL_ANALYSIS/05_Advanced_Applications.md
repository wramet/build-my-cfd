# Advanced Applications

---

## Learning Objectives

By the end of this section, you will be able to:
- Define custom dimensions for specialized physical quantities
- Calculate derived quantities with proper dimensional checking
- Implement dimensionally-consistent source terms and boundary conditions
- Work with turbulence quantities using correct dimensions
- Apply non-dimensional groups for validation and analysis

---

## Overview

**What:** Advanced applications of dimensional analysis for custom quantities, source terms, boundary conditions, and turbulence modeling.

**Why:** Dimensional consistency prevents physics errors in complex simulations and enables automatic verification of derived quantities.

**How:** Use OpenFOAM's dimension system to define custom quantities, validate derived expressions, and ensure correctness in source terms, boundary conditions, and turbulence models.

---

## 1. Custom Dimensions

Define physical quantities with compound dimensions:

```cpp
// Specific heat capacity [J/(kg·K)]
dimensionedScalar Cp
(
    "Cp",
    dimEnergy / dimMass / dimTemperature,
    1005
);

// Thermal conductivity [W/(m·K)]
dimensionedScalar k
(
    "k",
    dimPower / dimLength / dimTemperature,
    0.025
);
```

---

## 2. Derived Quantities

OpenFOAM automatically verifies dimensional consistency:

```cpp
// Thermal diffusivity α = k/(ρ·Cp) [m²/s]
dimensionedScalar alpha = k / (rho * Cp);
// Dimensional check: [W/(m·K)] / ([kg/m³]·[J/(kg·K)]) = [m²/s] ✓

// Reynolds number (dimensionless)
volScalarField Re = mag(U) * L / nu;
// [m/s]·[m] / [m²/s] = dimless ✓

// Kinematic viscosity from dynamic viscosity
dimensionedScalar nu = mu / rho;
// [Pa·s] / [kg/m³] = [m²/s] ✓
```

---

## 3. Source Terms

Source terms must match equation dimensions:

```cpp
// Heat source [W/m³]
dimensionedScalar Q
(
    "Q",
    dimPower / dimVolume,
    1e6
);

// Energy equation with source
fvScalarMatrix TEqn
(
    fvm::ddt(rho, Cp, T) == fvm::laplacian(k, T) + Q
);

// Momentum source [N/m³ = kg/(m²·s²)]
dimensionedScalar F
(
    "F",
    dimMass * dimLength / pow3(dimTime),
    0.5
);
```

---

## 4. Boundary Conditions

Boundary conditions require consistent dimensions:

```cpp
// Heat flux [W/m²]
dimensionedScalar qw
(
    "qw",
    dimPower / dimArea,
    1000
);

// Fixed gradient BC (temperature gradient from heat flux)
T.boundaryFieldRef()[patchI] == qw / k;

// Velocity inlet [m/s]
dimensionedVector U_inlet
(
    "U_inlet",
    dimVelocity,
    vector(1, 0, 0)
);
```

---

## 5. Turbulence Quantities

Different turbulence models use specific quantities:

### k-ε Model
```cpp
// Turbulent kinetic energy [m²/s²]
dimensionedScalar k0
(
    "k0",
    sqr(dimVelocity),
    0.1
);

// Dissipation rate [m²/s³]
dimensionedScalar epsilon0
(
    "epsilon0",
    sqr(dimVelocity) / dimTime,
    0.01
);

// Eddy viscosity: νt = Cμ·k²/ε [m²/s]
volScalarField nut = Cmu * sqr(k) / epsilon;
```

### k-ω Model
```cpp
// Specific dissipation rate [1/s]
dimensionedScalar omega0
(
    "omega0",
    dimless / dimTime,
    1000
);

// Eddy viscosity: νt = k/ω [m²/s]
volScalarField nut = k / omega;
```

### Spalart-Allmaras Model
```cpp
// Modified eddy viscosity [m²/s]
dimensionedScalar nuTilda0
(
    "nuTilda0",
    sqr(dimLength) / dimTime,
    1e-5
);
```

---

## 6. Non-Dimensional Groups

*See also: [04_Non_Dimensionalization.md](04_Non_Dimensionalization.md) for comprehensive coverage*

Common dimensionless numbers for validation:

```cpp
// Nusselt number (convection strength)
volScalarField Nu = h * L / k_thermal;

// Prandtl number (momentum vs thermal diffusivity)
dimensionedScalar Pr = nu / alpha;

// Peclet number (convection vs diffusion)
volScalarField Pe = mag(U) * L / alpha;

// Stanton number (heat transfer coefficient)
volScalarField St = h / (rho * Cp * mag(U));

// Friction factor
dimensionedScalar f = deltaP * L / (0.5 * rho * sqr(mag(U)) * D);
```

---

## Quick Reference

| Quantity | Dimension | Expression |
|----------|-----------|------------|
| Specific heat | `dimEnergy/(dimMass·dimTemperature)` | J/(kg·K) |
| Heat flux | `dimPower/dimArea` | W/m² |
| Thermal diffusivity | `sqr(dimLength)/dimTime` | m²/s |
| Source (energy) | `dimPower/dimVolume` | W/m³ |
| Source (momentum) | `dimMass·dimLength/dimTime³` | N/m³ |
| k (TKE) | `sqr(dimVelocity)` | m²/s² |
| ε (dissipation) | `sqr(dimVelocity)/dimTime` | m²/s³ |
| ω (spec. dissipation) | `dimless/dimTime` | 1/s |
| ν̃ (SA) | `sqr(dimLength)/dimTime` | m²/s |

---

## Key Takeaways

- **Custom dimensions** enable automatic verification of complex derived quantities
- **Source terms** must match the governing equation's dimensional balance
- **Turbulence quantities** have specific dimensions per model (k-ε, k-ω, SA)
- **Non-dimensional groups** provide validation and physical insight
- **Dimensional checking** catches physics errors at compile-time

---

## Concept Check

<details>
<summary><b>1. What is the dimension of turbulent kinetic energy k?</b></summary>

**[m²/s²]** — kinetic energy per unit mass (velocity squared)
</details>

<details>
<summary><b>2. What dimension should a heat source term have?</b></summary>

**[W/m³]** = `dimPower/dimVolume` — energy per unit volume per unit time
</details>

<details>
<summary><b>3. How do k-ε and k-ω models differ in their second variable?</b></summary>

k-ε uses **ε** (dissipation, m²/s³), while k-ω uses **ω** (specific dissipation, 1/s). Both produce eddy viscosity as m²/s.
</details>

<details>
<summary><b>4. Why use dimensionless numbers like Nu or Re?</b></summary>

They enable **generalization** across scales, **validation** against literature, and **physical insight** into regime behavior.
</details>

---

## Related Documentation

- **Overview:** [00_Overview.md](00_Overview.md)
- **Non-Dimensionalization:** [04_Non_Dimensionalization.md](04_Non_Dimensionalization.md) - Comprehensive theory
- **Dimensioned Types:** [02_Dimensioned_Types.md](../02_DIMENSIONED_TYPES/02_Physics_Aware_Type_System.md)