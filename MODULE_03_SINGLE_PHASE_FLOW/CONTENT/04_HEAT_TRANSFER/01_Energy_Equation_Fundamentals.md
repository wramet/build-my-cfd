# Energy Equation Fundamentals

พื้นฐานสมการพลังงานใน OpenFOAM

---

## Overview

| Form | Use Case | Solver |
|------|----------|--------|
| Temperature (T) | Incompressible | `buoyantBoussinesqSimpleFoam` |
| Enthalpy (h) | Compressible | `buoyantSimpleFoam` |
| Internal Energy (e) | High temperature | `rhoPimpleFoam` |

---

## 1. Governing Equations

### Incompressible (Temperature Form)

$$\frac{\partial T}{\partial t} + \mathbf{u} \cdot \nabla T = \alpha \nabla^2 T + \frac{Q}{\rho c_p}$$

**Where:**
- $\alpha = k/(\rho c_p)$ = thermal diffusivity [m²/s]

### Compressible (Enthalpy Form)

$$\frac{\partial (\rho h)}{\partial t} + \nabla \cdot (\rho \mathbf{u} h) = \nabla \cdot (k \nabla T) + \frac{Dp}{Dt} + Q$$

---

## 2. Fourier's Law

$$\mathbf{q} = -k \nabla T$$

| Symbol | Meaning | Unit |
|--------|---------|------|
| $\mathbf{q}$ | Heat flux | W/m² |
| $k$ | Thermal conductivity | W/(m·K) |
| $\nabla T$ | Temperature gradient | K/m |

---

## 3. Turbulent Heat Transfer

### Effective Thermal Diffusivity

$$\alpha_{eff} = \frac{\nu}{Pr} + \frac{\nu_t}{Pr_t}$$

| Parameter | Typical Value |
|-----------|---------------|
| $Pr$ (air) | 0.71 |
| $Pr_t$ | 0.85-0.9 |

---

## 4. Dimensionless Numbers

### Prandtl Number
$$Pr = \frac{\nu}{\alpha} = \frac{\mu c_p}{k}$$

| Fluid | Pr |
|-------|---:|
| Liquid metals | ~0.01 |
| Air | 0.71 |
| Water | 7.0 |
| Oil | ~100 |

### Nusselt Number
$$Nu = \frac{hL}{k}$$

### Peclet Number
$$Pe = Re \cdot Pr = \frac{uL}{\alpha}$$

---

## 5. Buoyancy Coupling

### Boussinesq Approximation

$$\mathbf{F}_b = \rho_0 \beta (T - T_{ref}) \mathbf{g}$$

| Symbol | Meaning |
|--------|---------|
| $\beta$ | Thermal expansion coefficient [1/K] |
| $T_{ref}$ | Reference temperature |
| $\mathbf{g}$ | Gravity vector |

---

## 6. OpenFOAM Implementation

### thermophysicalProperties

```cpp
thermoType
{
    type            hePsiThermo;
    mixture         pureMixture;
    transport       const;
    thermo          hConst;
    equationOfState perfectGas;
    energy          sensibleEnthalpy;
}

mixture
{
    specie { molWeight 28.9; }
    thermodynamics { Cp 1005; Hf 0; }
    transport { mu 1.8e-5; Pr 0.71; }
}
```

### Energy Equation Code

```cpp
// TEqn.H
fvScalarMatrix TEqn
(
    fvm::ddt(rho, T)
  + fvm::div(rhoPhi, T)
  - fvm::laplacian(turbulence->alphaEff(), T)
 ==
    fvModels.source(rho, T)
);
TEqn.relax();
TEqn.solve();
```

---

## 7. Solver Selection

| Solver | Type | Use Case |
|--------|------|----------|
| `buoyantSimpleFoam` | Steady | Natural convection |
| `buoyantPimpleFoam` | Transient | Unsteady buoyancy |
| `buoyantBoussinesqSimpleFoam` | Steady | Small ΔT |
| `chtMultiRegionFoam` | Conjugate | Solid-fluid heat |

---

## 8. Thermophysical Models

| Model | Transport | Thermo |
|-------|-----------|--------|
| Constant | `const` | `hConst` |
| Polynomial | `polynomial` | `polynomial` |
| Sutherland | `sutherland` | `janaf` |

---

## Concept Check

<details>
<summary><b>1. Enthalpy กับ Internal Energy ต่างกันอย่างไร?</b></summary>

- **Enthalpy (h)**: รวม flow work ($p/\rho$) ไว้แล้ว เหมาะกับ open systems
- **Internal Energy (e)**: ไม่รวม flow work เหมาะกับ closed systems
</details>

<details>
<summary><b>2. ทำไม $Pr_t$ มีค่าประมาณ 0.85?</b></summary>

ค่าเชิงประจักษ์ที่บ่งบอกว่า momentum และ heat diffuse ด้วยอัตราใกล้เคียงกันใน turbulent flow แต่ไม่เท่ากันทีเดียว
</details>

<details>
<summary><b>3. Boussinesq approximation ใช้เมื่อไหร่?</b></summary>

เมื่อ $\Delta\rho/\rho \ll 1$ (temperature variation เล็ก) — ถือว่า $\rho$ คงที่ทุกที่ยกเว้นในเทอม buoyancy
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **บทถัดไป:** [02_Heat_Transfer_Mechanisms.md](02_Heat_Transfer_Mechanisms.md)
- **Buoyancy:** [03_Buoyancy_Driven_Flows.md](03_Buoyancy_Driven_Flows.md)