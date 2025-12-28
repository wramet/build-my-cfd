# Heat Transfer Mechanisms

กลไกการถ่ายเทความร้อน: Conduction, Convection, Radiation

---

## Overview

OpenFOAM รองรับทั้ง 3 กลไกการถ่ายเทความร้อน:

| กลไก | เทอม | ไฟล์ตั้งค่า |
|------|------|------------|
| **Conduction** | $\nabla \cdot (k \nabla T)$ | `fvSchemes` → `laplacianSchemes` |
| **Convection** | $\nabla \cdot (\phi T)$ | `fvSchemes` → `divSchemes` |
| **Radiation** | Stefan-Boltzmann | `constant/radiationProperties` |

---

## 1. Conduction (การนำความร้อน)

### Fourier's Law

$$\mathbf{q} = -k \nabla T$$

```cpp
// Energy equation in solver
fvScalarMatrix TEqn
(
    fvm::ddt(T)
  + fvm::div(phi, T)
  - fvm::laplacian(DT, T)  // DT = k/(rho*cp)
 ==
    fvOptions(T)
);
```

### Thermal Diffusivity

$$\alpha = \frac{k}{\rho c_p}$$

```cpp
// constant/transportProperties
DT    [0 2 -1 0 0 0 0] 2.5e-5;  // Thermal diffusivity [m²/s]
```

### laplacianSchemes

```cpp
// system/fvSchemes
laplacianSchemes
{
    default          Gauss linear corrected;
    laplacian(DT,T)  Gauss linear corrected;
}
```

---

## 2. Convection (การพาความร้อน)

### Forced Convection

$$q_w = h_c (T_w - T_\infty)$$

**Dimensionless Numbers:**

| Number | Formula | Meaning |
|--------|---------|---------|
| Reynolds | $Re = \frac{\rho U L}{\mu}$ | Inertia / Viscosity |
| Prandtl | $Pr = \frac{\mu c_p}{k}$ | Momentum / Heat diffusion |
| Nusselt | $Nu = \frac{h L}{k}$ | Convection / Conduction |

**Dittus-Boelter correlation:**
$$Nu = 0.023 \, Re^{0.8} \, Pr^{0.4}$$

### Natural Convection (Boussinesq)

$$\mathbf{f}_b = \rho \mathbf{g} \beta (T - T_{ref})$$

```cpp
// buoyantBoussinesqSimpleFoam
volVectorField gEffect = rho*(1 - beta*(T - TRef))*g;

fvVectorMatrix UEqn
(
    fvm::div(phi, U)
  + turbulence->divDevReff(U)
 ==
    gEffect
);
```

**Rayleigh Number:**
$$Ra = \frac{g \beta \Delta T L^3}{\nu \alpha}$$

---

## 3. Radiation (การแผ่รังสี)

### Stefan-Boltzmann Law

$$q_{rad} = \varepsilon \sigma (T_{hot}^4 - T_{cold}^4)$$

- $\sigma = 5.67 \times 10^{-8}$ W/(m²·K⁴)
- $\varepsilon$ = emissivity (0 to 1)

### P1 Model

```cpp
// constant/radiationProperties
radiationModel  P1;

P1Coeffs
{
    absorptivity    absorptivity [0 -1 0 0 0 0 0] 0.1;
}
```

**P1 equation:**
$$\nabla \cdot \left( \frac{1}{3\kappa} \nabla G \right) = \kappa (4\sigma T^4 - G)$$

### View Factor Model

```cpp
radiationModel  viewFactor;

viewFactorCoeffs
{
    nBands          1;
    emissivity      constant 0.8;
}
```

---

## 4. Thermal Boundary Conditions

### Common BCs

| Type | BC Name | Usage |
|------|---------|-------|
| Fixed temperature | `fixedValue` | Constant wall temp |
| Fixed heat flux | `fixedGradient` | Constant q'' |
| Adiabatic | `zeroGradient` | Insulated wall |
| Convection | `externalWallHeatFluxTemperature` | h, T∞ |
| Radiation | `greyDiffusiveRadiation` | ε, T_amb |

### Examples

```cpp
// 0/T
boundaryField
{
    inlet
    {
        type        fixedValue;
        value       uniform 300;
    }
    
    walls
    {
        type        externalWallHeatFluxTemperature;
        mode        coefficient;
        h           uniform 10;        // [W/(m²·K)]
        Ta          uniform 293;       // Ambient [K]
    }
    
    insulated
    {
        type        zeroGradient;
    }
}
```

---

## 5. Heat Transfer Solvers

| Solver | Type | Use Case |
|--------|------|----------|
| `laplacianFoam` | Pure conduction | Solids only |
| `buoyantSimpleFoam` | Steady, buoyant | Natural convection |
| `buoyantBoussinesqSimpleFoam` | Steady, Boussinesq | Small ΔT |
| `buoyantPimpleFoam` | Transient | Large ΔT, compressible |
| `chtMultiRegionFoam` | Conjugate | Multi-region solid/fluid |

### thermophysicalProperties

```cpp
// constant/thermophysicalProperties
thermoType
{
    type            heRhoThermo;
    mixture         pureMixture;
    transport       const;
    thermo          hConst;
    equationOfState perfectGas;
    specie          specie;
    energy          sensibleEnthalpy;
}

mixture
{
    specie { molWeight 28.9; }
    thermodynamics { Cp 1005; Hf 0; }
    transport { mu 1.8e-5; Pr 0.7; }
}
```

---

## Concept Check

<details>
<summary><b>1. เมื่อไหร่ควรใช้ Boussinesq approximation?</b></summary>

เมื่อ $\Delta T / T_{ref} < 0.1$ (ประมาณ 10%) — สำหรับ natural convection ที่การเปลี่ยนแปลงอุณหภูมิไม่มาก ช่วยลดความซับซ้อนของสมการโดยถือว่า ρ คงที่ยกเว้นในเทอม buoyancy
</details>

<details>
<summary><b>2. P1 radiation model เหมาะกับงานแบบไหน?</b></summary>

เหมาะกับ optically thick media (สื่อกลางที่มีการดูดกลืนสูง) เช่น ห้องเผาไหม้ที่มีควัน — ไม่เหมาะกับ transparent media หรือ surface-to-surface radiation ในที่โล่ง
</details>

<details>
<summary><b>3. externalWallHeatFluxTemperature ต้องระบุอะไรบ้าง?</b></summary>

- `mode coefficient` หรือ `flux`
- `h` = heat transfer coefficient [W/(m²·K)]
- `Ta` = ambient temperature [K]
- Optional: `thicknessLayers`, `kappaLayers` สำหรับผนังหลายชั้น
</details>

---

## Related Documents

- **บทก่อนหน้า:** [01_Energy_Equation_Fundamentals.md](01_Energy_Equation_Fundamentals.md)
- **บทถัดไป:** [03_Buoyancy_Driven_Flows.md](03_Buoyancy_Driven_Flows.md)