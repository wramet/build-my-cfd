# Energy Conservation Equations

สมการอนุรักษ์พลังงานสำหรับ Multiphase

---

## Overview

> แต่ละเฟสมีสมการพลังงานของตัวเอง เชื่อมโยงผ่าน **interphase heat transfer**

---

## 1. General Form

$$\frac{\partial(\alpha_k \rho_k h_k)}{\partial t} + \nabla \cdot (\alpha_k \rho_k h_k \mathbf{u}_k) = \nabla \cdot (\alpha_k k_k \nabla T_k) + \alpha_k \frac{Dp}{Dt} + Q_k$$

| Term | Meaning |
|------|---------|
| $\frac{\partial(\alpha_k \rho_k h_k)}{\partial t}$ | Enthalpy storage |
| $\nabla \cdot (\alpha_k \rho_k h_k \mathbf{u}_k)$ | Convection |
| $\nabla \cdot (\alpha_k k_k \nabla T_k)$ | Conduction |
| $\alpha_k \frac{Dp}{Dt}$ | Pressure work |
| $Q_k$ | Interphase heat transfer |

---

## 2. Interphase Heat Transfer

$$Q_k = \sum_{l \neq k} h_{kl} A_{kl} (T_l - T_k)$$

| Symbol | Meaning | Unit |
|--------|---------|------|
| $h_{kl}$ | Heat transfer coefficient | W/(m²·K) |
| $A_{kl}$ | Interfacial area | m²/m³ |
| $T_k, T_l$ | Phase temperatures | K |

### Nusselt Number

$$h = \frac{Nu \cdot k_c}{d_p}$$

### Common Correlations

| Correlation | Use Case |
|-------------|----------|
| Ranz-Marshall | Spherical particles |
| Hughmark | Bubble columns |
| Gunn | Fluidized beds |

---

## 3. Ranz-Marshall Correlation

$$Nu = 2 + 0.6 Re^{1/2} Pr^{1/3}$$

| Limit | Nu |
|-------|-----|
| Re → 0 | 2 (conduction only) |
| High Re | $\propto Re^{1/2}$ |

---

## 4. Temperature vs Enthalpy

### Enthalpy Form

$$h = \int_{T_{ref}}^{T} c_p \, dT$$

### Temperature Form

$$\frac{\partial(\alpha_k \rho_k c_{p,k} T_k)}{\partial t} + \nabla \cdot (\alpha_k \rho_k c_{p,k} T_k \mathbf{u}_k) = ...$$

---

## 5. OpenFOAM Implementation

### Energy Equation

```cpp
fvScalarMatrix EEqn
(
    fvm::ddt(alpha, rho, h)           // ∂(αρh)/∂t
  + fvm::div(alphaPhi, h)             // ∇·(αρhU)
  ==
    fvc::div(alphaKappaEff*fvc::grad(T))  // ∇·(αk∇T)
  + alpha*dpdt                         // αDp/Dt
  + interphaseHeatTransfer             // Q_k
);
```

### Thermophysical Model

```cpp
// constant/thermophysicalProperties.water
thermoType
{
    type            heRhoThermo;
    mixture         pureMixture;
    transport       const;
    thermo          hConst;
    equationOfState rhoConst;
    specie          specie;
    energy          sensibleEnthalpy;
}

mixture
{
    Cp      4180;
    Hf      0;
}
```

---

## 6. Phase Change

### Latent Heat

$$Q_{latent} = \dot{m}_{lk} \cdot L_{lk}$$

| Symbol | Meaning |
|--------|---------|
| $\dot{m}_{lk}$ | Mass transfer rate |
| $L_{lk}$ | Latent heat |

### Saturation Model

```cpp
// constant/phaseProperties
saturationTemperatureModel
{
    type    constant;
    value   373.15;
}
```

---

## 7. Boundary Conditions

### Fixed Temperature

```cpp
T.water
{
    type    fixedValue;
    value   uniform 300;
}
```

### Heat Flux

```cpp
T.water
{
    type    fixedGradient;
    gradient uniform 1000;  // W/m²
}
```

### Adiabatic

```cpp
T.water
{
    type    zeroGradient;
}
```

---

## Quick Reference

| Component | Equation |
|-----------|----------|
| Convection | $\nabla \cdot (\alpha \rho h U)$ |
| Conduction | $\nabla \cdot (\alpha k \nabla T)$ |
| Interphase | $h_{kl} A_{kl} (T_l - T_k)$ |
| Phase change | $\dot{m} L$ |

---

## Concept Check

<details>
<summary><b>1. ทำไมใช้ enthalpy แทน temperature?</b></summary>

เพราะ **enthalpy เป็น conserved quantity** และรวม latent heat สำหรับ phase change ได้ง่ายกว่า
</details>

<details>
<summary><b>2. Ranz-Marshall ให้ Nu = 2 เมื่อไหร่?</b></summary>

เมื่อ **Re → 0** (no relative motion) — heat transfer เกิดจาก **conduction เท่านั้น** (sphere in stagnant fluid)
</details>

<details>
<summary><b>3. Interfacial area สำคัญอย่างไร?</b></summary>

เพราะ **heat transfer ∝ area** — ถ้า bubbles เล็กลง, surface area/volume เพิ่มขึ้น → heat transfer ดีขึ้น
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Mass Conservation:** [01_Mass_Conservation.md](01_Mass_Conservation.md)
- **Momentum Conservation:** [02_Momentum_Conservation.md](02_Momentum_Conservation.md)