# Heat Transfer Mechanisms

กลไกการถ่ายเทความร้อน: Conduction, Convection, Radiation

---

## Learning Objectives

หลังจากอ่านบทนี้ คุณจะสามารถ:

- **WHAT (Concepts):** อธิบายกลไกการถ่ายเทความร้อนทั้ง 3 แบบ (conduction, convection, radiation) และสมการที่ควบคุมแต่ละกลไก
- **WHY (Physical Importance):** วิเคราะห์ว่ากลไกใดครอบคลุม (dominant) ในสถานการณ์ต่างๆ และผลกระทบต่อการออกแบบระบบ
- **HOW (Implementation):** ตั้งค่า radiation models, dimensionless numbers และ boundary conditions ที่เหมาะสมใน OpenFOAM

---

## Overview

OpenFOAM รองรับทั้ง 3 กลไกการถ่ายเทความร้อน:

| กลไก | เทอม | ไฟล์ตั้งค่า |
|------|------|------------|
| **Conduction** | $\nabla \cdot (k \nabla T)$ | `fvSchemes` → `laplacianSchemes` |
| **Convection** | $\nabla \cdot (\phi T)$ | `fvSchemes` → `divSchemes` |
| **Radiation** | Stefan-Boltzmann | `constant/radiationProperties` |

> **📖 Fourier's Law และ Conduction fundamentals** อยู่ใน [01_Energy_Equation_Fundamentals.md](01_Energy_Equation_Fundamentals.md)  
> **📖 thermophysicalProperties และ basic BCs** อยู่ใน [00_Overview.md](00_Overview.md)  
> **📖 Boussinesq approximation details** อยู่ใน [03_Buoyancy_Driven_Flows.md](03_Buoyancy_Driven_Flows.md)

---

## 1. Conduction (การนำความร้อน)

### WHAT: Fourier's Law

> **ดูรายละเอียด Fourier's Law ใน:** [01_Energy_Equation_Fundamentals.md](01_Energy_Equation_Fundamentals.md#fouriers-law-heat-conduction-mechanism)

$$\mathbf{q} = -k \nabla T$$

**Physical Meaning:**
- Heat flux ($\mathbf{q}$) flows from hot to cold (opposite to temperature gradient)
- $k$ = thermal conductivity [W/(m·K)]
- $\nabla T$ = temperature gradient [K/m]

### WHY: When Conduction Dominates

| Situation | Why Conduction Dominates |
|-----------|--------------------------|
| Solids (no flow) | No convection mechanism |
| Boundary layers | Velocity near zero at wall |
| Low Reynolds flow | Minimal advection |
| Insulated systems | Heat transfer through solid walls |

### HOW: Implementation in OpenFOAM

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

**Thermal Diffusivity:**
$$\alpha = \frac{k}{\rho c_p}$$

```cpp
// constant/transportProperties (for incompressible solvers)
DT    [0 2 -1 0 0 0 0] 2.5e-5;  // Thermal diffusivity [m²/s]
```

**Discretization Schemes:**
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

### WHAT: Forced Convection

**Newton's Law of Cooling:**
$$q_w = h_c (T_w - T_\infty)$$

**Dimensionless Numbers:**

> **📖 Prandtl number details** ใน [01_Energy_Equation_Fundamentals.md](01_Energy_Equation_Fundamentals.md#dimensionless-numbers-for-heat-transfer)

| Number | Formula | Meaning | Typical Use |
|--------|---------|---------|-------------|
| Reynolds | $Re = \frac{\rho U L}{\mu}$ | Inertia / Viscosity | Characterize flow regime |
| Prandtl | $Pr = \frac{\mu c_p}{k}$ | Momentum / Heat diffusion | Fluid property |
| Nusselt | $Nu = \frac{h L}{k}$ | Convection / Conduction | Heat transfer coefficient |

**Dittus-Boelter Correlation (Turbulent Flow):**
$$Nu = 0.023 \, Re^{0.8} \, Pr^{0.4}$$

Use this to estimate $h$ for boundary conditions when empirical data is unavailable.

### WHY: Natural vs Forced Convection

| Type | Driving Force | Typical Applications | Key Parameter |
|------|---------------|----------------------|---------------|
| **Forced** | External (pump, fan) | Heat exchangers, electronics cooling | Reynolds number |
| **Natural** | Buoyancy (density differences) | Radiators, atmospheric flows | Rayleigh number |

### HOW: Natural Convection Setup

**Boussinesq Approximation:**

> **📖 ดูรายละเอียด Boussinesq approximation ใน:** [03_Buoyancy_Driven_Flows.md](03_Buoyancy_Driven_Flows.md)

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

**Rayleigh Number (Flow Regime):**

> **📖 Ra/Pr/Nu definitions** ใน [03_Buoyancy_Driven_Flows.md](03_Buoyancy_Driven_Flows.md)

$$Ra = \frac{g \beta \Delta T L^3}{\nu \alpha}$$

| $Ra$ Range | Regime | Characteristics |
|------------|--------|-----------------|
| $< 10^3$ | Conduction dominant | Minimal fluid motion |
| $10^3 - 10^9$ | Laminar convection | Steady buoyancy-driven flow |
| $> 10^9$ | Turbulent convection | Chaotic, unsteady flow |

---

## 3. Radiation (การแผ่รังสี)

### WHAT: Stefan-Boltzmann Law

$$q_{rad} = \varepsilon \sigma (T_{hot}^4 - T_{cold}^4)$$

**Parameters:**
- $\sigma = 5.67 \times 10^{-8}$ W/(m²·K⁴) — Stefan-Boltzmann constant
- $\varepsilon$ = emissivity (0 to 1) — surface property
- $T^4$ dependence — radiation increases dramatically with temperature

### WHY: When Radiation Matters

| Application | Why Radiation Dominates | Typical Temperature Range |
|-------------|------------------------|---------------------------|
| Combustion chambers | Flames > 1500 K | $> 1000$ K |
| Furnaces, boilers | Large temperature differences | 800 - 2000 K |
| Solar heating | Direct radiation source | 300 - 400 K (with source) |
| Electronics cooling | Negligible at < 400 K | $< 400$ K |

**Rule of Thumb:** Radiation becomes significant when $T > 600$ K or $\Delta T > 200$ K

### HOW: Radiation Models in OpenFOAM

#### P1 Model (Optically Thick Media)

```cpp
// constant/radiationProperties
radiationModel  P1;

P1Coeffs
{
    absorptivity    absorptivity [0 -1 0 0 0 0 0] 0.1;
}
```

**P1 Equation:**
$$\nabla \cdot \left( \frac{1}{3\kappa} \nabla G \right) = \kappa (4\sigma T^4 - G)$$

Where:
- $G$ = incident radiation [W/m²]
- $\kappa$ = absorption coefficient [1/m]

**Best For:**
- Enclosed spaces with participating media (smoke, soot)
- Combustion chambers, fires
- **NOT** suitable for transparent media or surface-to-surface radiation

#### View Factor Model (Surface-to-Surface)

```cpp
radiationModel  viewFactor;

viewFactorCoeffs
{
    nBands          1;
    emissivity      constant 0.8;
}
```

**Best For:**
- Vacuum or transparent media (air at low temperature)
- Enclosures with well-defined surfaces
- Satellite thermal analysis, electronic enclosures

**Computationally Expensive:** Requires view factor calculation (N² complexity)

---

## 4. Thermal Boundary Conditions (Advanced)

### WHAT: Specialized BCs for Heat Transfer

| Type | BC Name | Usage | Key Parameters |
|------|---------|-------|----------------|
| Fixed temperature | `fixedValue` | Constant wall temp | `value uniform 300` |
| Fixed heat flux | `fixedGradient` | Constant q'' | `gradient uniform 1000` |
| Adiabatic | `zeroGradient` | Insulated wall | (No parameters) |
| Convection | `externalWallHeatFluxTemperature` | h, T∞ | `mode coefficient`, `h`, `Ta` |
| Radiation | `greyDiffusiveRadiation` | ε, T_amb | `emissivity`, `Ta` |

> **📖 BC fundamentals ใน:** [00_Overview.md](00_Overview.md#3-boundary-conditions-0t)

### WHY: Robin Boundary Condition (Convection)

**Convective BC (Robin Type):**
$$-k \frac{\partial T}{\partial n} = h (T_w - T_\infty)$$

Combines conduction (left) and convection (right) at the boundary

**Advantages:**
- Avoid meshing external fluid domain
- Reduces computational cost
- Uses empirical $h$ from correlations or experiments

### HOW: BC Examples

#### External Convection

```cpp
// 0/T
boundaryField
{
    walls
    {
        type        externalWallHeatFluxTemperature;
        mode        coefficient;
        h           uniform 10;        // [W/(m²·K)]
        Ta          uniform 293;       // Ambient [K]
    }
}
```

#### Multi-Layer Wall (Conjugate Effect)

```cpp
externalWall
{
    type            externalWallHeatFluxTemperature;
    mode            coefficient;

    h               uniform 25;
    Ta              uniform 300;

    // Wall layers (solid conduction)
    thicknessLayers (0.05 0.02);      // [m] — two layers
    kappaLayers     (0.7 0.04);       // [W/(m·K)] — brick + insulation
}
```

#### Combined Convection + Radiation

```cpp
heatedSurface
{
    type            externalWallHeatFluxTemperature;
    mode            coefficient;

    h               uniform 15;       // Convection coefficient
    Ta              uniform 293;      // Ambient temperature

    // Radiation parameters
    emissivity      0.85;             // Surface emissivity
    radiation
    {
        type            greyDiffusiveRadiation;
        T               T;             // Use temperature field
    }
}
```

---

## 5. Solver Selection Guide

### WHAT: Heat Transfer Solvers in OpenFOAM

| Solver | Type | Mechanisms | Use Case |
|--------|------|------------|----------|
| `laplacianFoam` | Pure conduction | Conduction only | Solids only, transient |
| `buoyantSimpleFoam` | Steady, buoyant | Conduction + Convection | Natural convection, large ΔT |
| `buoyantBoussinesqSimpleFoam` | Steady, Boussinesq | Conduction + Convection | Small ΔT, incompressible |
| `buoyantPimpleFoam` | Transient | Conduction + Convection | Large ΔT, compressible |
| `chtMultiRegionFoam` | Conjugate | All + solid-fluid coupling | Multi-region solid/fluid |

### WHY: Choosing the Right Solver

**Decision Flowchart:**

```
Start
 │
 ├─ Is solid only (no fluid flow)?
 │   ├─ YES → laplacianFoam
 │   └─ NO → Continue
 │
 ├─ Is buoyancy significant (Ra > 10³)?
 │   ├─ NO → Use standard solver (simpleFoam + energy)
 │   └─ YES → Continue
 │
 ├─ Is ΔT small (< 30 K for air)?
 │   ├─ YES → buoyantBoussinesqSimpleFoam (faster)
 │   └─ NO → Continue
 │
 ├─ Is transient required?
 │   ├─ YES → buoyantPimpleFoam
 │   └─ NO → buoyantSimpleFoam
 │
 └─ Is solid-fluid coupling required?
     └─ YES → chtMultiRegionFoam
```

### HOW: Quick Solver Reference

> **📖 thermophysicalProperties details ใน:** [00_Overview.md](00_Overview.md#2-thermophysical-properties)

| Solver | Energy Form | EoS | Key Feature |
|--------|-------------|-----|-------------|
| `buoyantBoussinesqSimpleFoam` | T-form | `rhoConst` | Fastest, small ΔT |
| `buoyantSimpleFoam` | h-form | `perfectGas` | Large ΔT, steady |
| `buoyantPimpleFoam` | h-form | `perfectGas` | Large ΔT, transient |
| `chtMultiRegionFoam` | Varies | Varies | Multi-region coupling |

---

## Key Takeaways

### Summary Table: Heat Transfer Mechanisms Comparison

| Mechanism | Governing Equation | Key Parameter | Dominant When | OpenFOAM Implementation |
|-----------|-------------------|---------------|---------------|------------------------|
| **Conduction** | $\mathbf{q} = -k \nabla T$ | $k$ [W/(m·K)] | Solids, boundary layers | `laplacian(k,T)` |
| **Forced Convection** | $q = h(T_s - T_\infty)$ | $h$ [W/(m²·K)] | High Re flows | `div(phi,T)` |
| **Natural Convection** | $\mathbf{f}_b = \rho \beta \Delta T \mathbf{g}$ | $Ra$ | Buoyancy-driven | `buoyantBoussinesqSimpleFoam` |
| **Radiation** | $q = \varepsilon \sigma T^4$ | $\varepsilon$, $T^4$ | $T > 600$ K | `radiationModel` |

### Critical Dimensionless Numbers

| Number | Formula | Physical Meaning | Application |
|--------|---------|------------------|-------------|
| **Prandtl ($Pr$)** | $\frac{\mu c_p}{k}$ | Velocity vs thermal BL thickness | Fluid property characterization |
| **Nusselt ($Nu$)** | $\frac{h L}{k}$ | Convection vs conduction | Heat transfer coefficient calculation |
| **Rayleigh ($Ra$)** | $\frac{g \beta \Delta T L^3}{\nu \alpha}$ | Buoyancy vs diffusion | Natural convection regime selection |

### Implementation Checklist

1. **Identify dominant mechanism(s):** Conduction always present; check if convection or radiation are significant
2. **Select solver:** Use flowchart in Section 5
3. **Set up thermophysicalProperties:** Match equationOfState to your physics (details in [00_Overview.md](00_Overview.md))
4. **Configure boundary conditions:** Use `externalWallHeatFluxTemperature` for convection
5. **Add radiation model (if needed):** Choose P1 or viewFactor based on media transparency
6. **Validate with dimensionless numbers:** Calculate $Ra$, $Nu$ and compare with correlations

### Mechanism Selection Decision Tree

```
Start: What dominates your heat transfer?
│
├─ Only solids (no fluid)?
│  └─ Conduction only → laplacianFoam
│
├─ Fluid flow present?
│  ├─ High velocity flow (forced)?
│  │  └─ Forced convection → simpleFoam + energy equation
│  │
│  └─ Buoyancy-driven (natural)?
│     ├─ Small ΔT (< 30 K)?
│     │  └─ Boussinesq → buoyantBoussinesqSimpleFoam
│     │
│     └─ Large ΔT (> 30 K)?
│        └─ Full compressible → buoyantSimpleFoam / buoyantPimpleFoam
│
└─ Temperature > 600 K or large ΔT?
   └─ Add radiation model → P1 (participating) or viewFactor (surface)
```

---

## Concept Check

<details>
<summary><b>1. เมื่อไหร่ควรใช้ Boussinesq approximation?</b></summary>

เมื่อ $\Delta T / T_{ref} < 0.1$ (ประมาณ 10%) หรือ $\Delta T < 30$ K สำหรับอากาศ — ใช้สำหรับ natural convection ที่การเปลี่ยนแปลงอุณหภูมิไม่มาก ช่วยลดความซับซ้อนของสมการโดยถือว่า ρ คงที่ยกเว้นในเทอม buoyancy

**Solver:** `buoyantBoussinesqSimpleFoam`
</details>

<details>
<summary><b>2. P1 radiation model เหมาะกับงานแบบไหน?</b></summary>

เหมาะกับ **optically thick media** (สื่อกลางที่มีการดูดกลืนสูง) เช่น:
- ห้องเผาไหม้ที่มีควัน (combustion chambers)
- ระบบที่มี soot หรือ participating media

**ไม่เหมาะกับ:**
- Transparent media (อากาศบริสุทธิ์)
- Surface-to-surface radiation ในที่โล่ง (ใช้ viewFactor model)
</details>

<details>
<summary><b>3. externalWallHeatFluxTemperature ต้องระบุอะไรบ้าง?</b></summary>

**Required:**
- `mode coefficient` หรือ `flux`
- `h` = heat transfer coefficient [W/(m²·K)]
- `Ta` = ambient temperature [K]

**Optional:**
- `thicknessLayers`, `kappaLayers` สำหรับผนังหลายชั้น (multilayer walls)
- `emissivity` สำหรับ radiation coupling
</details>

<details>
<summary><b>4. ทำไม Radiation สำคัญใน high-temperature applications?</b></summary>

เพราะสมการ radiation $q \propto T^4$ — เมื่อ T เพิ่มขึ้น 2 เท่า heat flux จาก radiation เพิ่มขึ้น 16 เท่า

**ตัวอย่าง:**
- ที่ 300 K: radiation เล็กน้อยเมื่อเทียบกับ convection
- ที่ 1500 K (combustion): radiation ครอบคลุมเหนือกว่า conduction + convection รวมกัน
</details>

<details>
<summary><b>5. สมการ Dittus-Boelter ใช้ทำอะไร?</b></summary>

ใช้ประมาณค่า Nusselt number (และดังนั้น h) สำหรับ turbulent forced convection ใน pipes:

$$Nu = 0.023 \, Re^{0.8} \, Pr^{0.4}$$

**ใช้เมื่อ:**
- ไม่มีข้อมูล empirical จากการทดลอง
- ต้องการตั้งค่า `h` ใน `externalWallHeatFluxTemperature` BC
- Flow อยู่ใน turbulent regime ($Re > 4000$)

**จาก Nu คำนวณ h:**
$$h = \frac{Nu \cdot k}{L}$$
</details>

---

## Related Documents

- **บทก่อนหน้า:** [01_Energy_Equation_Fundamentals.md](01_Energy_Equation_Fundamentals.md) — Fourier's Law fundamentals, Prandtl number details
- **ภาพรวม:** [00_Overview.md](00_Overview.md) — thermophysicalProperties และ BC fundamentals
- **บทถัดไป:** [03_Buoyancy_Driven_Flows.md](03_Buoyancy_Driven_Flows.md) — Natural convection รายละเอียด
- **CHT:** [04_Conjugate_Heat_Transfer.md](04_Conjugate_Heat_Transfer.md) — Solid-fluid coupling