# Buoyancy-Driven Flows

Natural Convection และ Boussinesq Approximation

---

## Overview

**Buoyancy-Driven Flow** เกิดจากความแตกต่างของอุณหภูมิ → ความแตกต่างของความหนาแน่น → แรงลอยตัวจากแรงโน้มถ่วง

| Solver | Type | Use Case |
|--------|------|----------|
| `buoyantBoussinesqSimpleFoam` | Steady | $\Delta T < 30°C$ |
| `buoyantBoussinesqPimpleFoam` | Transient | $\Delta T < 30°C$, time-dependent |
| `buoyantSimpleFoam` | Steady | $\Delta T$ large, compressible |
| `buoyantPimpleFoam` | Transient | Fire, large $\Delta T$ |

---

## 1. Boussinesq Approximation

ถือว่า $\rho = const$ ทุกที่ **ยกเว้น** ในเทอมแรงลอยตัว:

$$\rho = \rho_0 [1 - \beta(T - T_0)]$$

### Buoyancy Force

$$\mathbf{F}_b = \rho_0 \mathbf{g} \beta (T - T_0)$$

### Validity

- $\beta \Delta T \ll 1$
- $\Delta T < 30°C$ สำหรับอากาศ

---

## 2. Dimensionless Numbers

### Rayleigh Number

$$Ra = \frac{g \beta \Delta T L^3}{\nu \alpha}$$

| $Ra$ Range | Flow Regime |
|------------|-------------|
| $< 10^3$ | Conduction dominant |
| $10^3 - 10^9$ | Laminar convection |
| $> 10^9$ | Turbulent convection |

### Grashof Number

$$Gr = \frac{g \beta \Delta T L^3}{\nu^2}$$

### Prandtl Number

$$Pr = \frac{\nu}{\alpha}$$

| Fluid | Pr |
|-------|-----|
| Air | 0.71 |
| Water | 7 |
| Oils | ~100 |

---

## 3. OpenFOAM Setup

### constant/g

```cpp
dimensions      [0 1 -2 0 0 0 0];
value           (0 0 -9.81);
```

### constant/transportProperties

```cpp
transportModel  Newtonian;

nu      [0 2 -1 0 0 0 0]  1.5e-05;
beta    [0 0 0 -1 0 0 0]  3.0e-03;  // Air at 20°C
Prt     [0 0 0 0 0 0 0]   0.9;      // Turbulent Prandtl
```

| Fluid | $\beta$ [1/K] |
|-------|---------------|
| Air (20°C) | $3.0 \times 10^{-3}$ |
| Water (20°C) | $2.1 \times 10^{-4}$ |

---

## 4. Numerical Settings

### fvSolution

```cpp
SIMPLE
{
    nNonOrthogonalCorrectors 1;
    residualControl { p 1e-4; U 1e-4; T 1e-4; }
}

relaxationFactors
{
    fields    { p 0.3; }
    equations { U 0.7; T 0.5; }  // T lower for stability
}
```

### fvSchemes

```cpp
divSchemes
{
    div(phi,U)  bounded Gauss limitedLinearV 1;
    div(phi,T)  bounded Gauss limitedLinear 1;  // bounded สำคัญ!
}
```

---

## 5. Solver Code

### Boussinesq in Momentum Equation

```cpp
// createFields.H
volScalarField rhok
(
    1.0 - beta * (T - TRef)  // Normalized density
);

// UEqn.H
fvVectorMatrix UEqn
(
    fvm::ddt(U)
  + fvm::div(phi, U)
  - fvm::laplacian(nu, U)
 ==
    rhok * g    // Buoyancy source term
);
```

---

## 6. Post-Processing

### Nusselt Number

$$Nu = \frac{h L}{k} = \frac{q'' L}{k \Delta T}$$

```cpp
// system/controlDict
functions
{
    wallHeatFlux
    {
        type    wallHeatFlux;
        patches (hotWall);
    }
}
```

### Correlations

| Configuration | Correlation |
|---------------|-------------|
| Vertical plate (laminar) | $Nu = 0.59 Ra^{1/4}$ |
| Vertical plate (turbulent) | $Nu = 0.10 Ra^{1/3}$ |

---

## Concept Check

<details>
<summary><b>1. Boussinesq Approximation สมมติอะไร?</b></summary>

สมมติว่าความหนาแน่นคงที่ทุกที่ **ยกเว้น** ในเทอมแรงลอยตัว:
$$\rho = \rho_0[1 - \beta(T-T_0)]$$
ใช้ได้เมื่อ $\beta\Delta T \ll 1$
</details>

<details>
<summary><b>2. ทำไม `bounded` scheme สำคัญสำหรับ T?</b></summary>

ป้องกัน temperature oscillation และค่าที่ไม่เป็นกายภาพ (เช่น $T < 0$K) ซึ่งอาจเกิดจาก convection scheme ที่ไม่ bounded
</details>

<details>
<summary><b>3. $Ra > 10^9$ บ่งบอกอะไร?</b></summary>

การไหลจะเป็น **turbulent natural convection** — ต้องใช้ turbulence model และอาจต้องเพิ่มความละเอียด mesh
</details>

---

## Related Documents

- **บทก่อนหน้า:** [02_Heat_Transfer_Mechanisms.md](02_Heat_Transfer_Mechanisms.md)
- **บทถัดไป:** [04_Conjugate_Heat_Transfer.md](04_Conjugate_Heat_Transfer.md)