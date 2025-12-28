# Heat Transfer Overview

การจำลองการถ่ายเทความร้อนใน OpenFOAM

> **ทำไมต้องเข้าใจ Heat Transfer?**
> - **งาน CFD จริงส่วนใหญ่มี thermal** — cooling, heating, HVAC
> - ต้องเลือก solver ให้ถูก — buoyancy vs CHT vs radiation
> - เข้าใหม่ thermophysicalProperties = ตั้งค่าได้ถูก

---

## Quick Start

> **💡 เลือก Solver จาก Physics:**
>
> | ต้องการ | Solver |
> |--------|--------|
> | Natural convection (small ΔT) | `buoyantBoussinesqSimpleFoam` |
> | Large ΔT / compressible | `buoyantSimpleFoam` |
> | Solid-fluid coupling | `chtMultiRegionFoam` |

| ต้องการจำลอง | Solver | Key File |
|-------------|--------|----------|
| Natural convection (small $\Delta T$) | `buoyantBoussinesqSimpleFoam` | `thermophysicalProperties` |
| Large $\Delta T$ / compressible | `buoyantSimpleFoam` | `thermophysicalProperties` |
| Transient with buoyancy | `buoyantPimpleFoam` | `g`, `thermophysicalProperties` |
| Solid-fluid coupling (CHT) | `chtMultiRegionFoam` | `regionProperties` |

---

---

## 1. Heat Transfer Modes

| Mode | Mechanism | OpenFOAM Term |
|------|-----------|---------------|
| **Conduction** | $q = -k\nabla T$ | `fvm::laplacian(k, T)` |
| **Convection** | $q = h(T_s - T_\infty)$ | `fvm::div(phi, h)` |
| **Radiation** | $q = \varepsilon\sigma T^4$ | `radiationModel` |

### Energy Equation

$$\frac{\partial (\rho h)}{\partial t} + \nabla \cdot (\rho \mathbf{u} h) = \nabla \cdot (\alpha_{eff} \nabla h) + Q$$

---

## 2. Thermophysical Properties

### constant/thermophysicalProperties

```cpp
thermoType
{
    type            heRhoThermo;       // or hePsiThermo (compressible gas)
    mixture         pureMixture;
    transport       const;             // or sutherland
    thermo          hConst;
    equationOfState rhoConst;          // or perfectGas
    specie          specie;
    energy          sensibleEnthalpy;
}

mixture
{
    specie { molWeight 28.96; }
    equationOfState { rho 1.225; }
    thermodynamics { Cp 1005; Hf 0; }
    transport { mu 1.8e-5; Pr 0.7; }
}
```

### Model Selection

| Fluid Type | `equationOfState` | `transport` |
|------------|-------------------|-------------|
| Incompressible liquid | `rhoConst` | `const` |
| Ideal gas | `perfectGas` | `sutherland` |
| Boussinesq | `Boussinesq` | `const` |

---

## 3. Boundary Conditions (0/T)

### Fixed Temperature

```cpp
hotWall { type fixedValue; value uniform 350; }
```

### Fixed Heat Flux

```cpp
heater { type fixedGradient; gradient uniform 1000; }  // W/m²
```

### Convective (Robin)

```cpp
external
{
    type    externalWallHeatFluxTemperature;
    mode    coefficient;
    h       uniform 25;      // W/m²K
    Ta      uniform 293;     // Ambient temperature
}
```

### Adiabatic

```cpp
insulated { type zeroGradient; }
```

---

## 4. Buoyancy Setup

### constant/g

```cpp
dimensions [0 1 -2 0 0 0 0];
value      (0 -9.81 0);
```

### Boussinesq Approximation

$$\rho = \rho_0 [1 - \beta(T - T_0)]$$

Valid when: $\beta \Delta T \ll 1$

---

## 5. Dimensionless Numbers

| Number | Formula | Physical Meaning |
|--------|---------|------------------|
| $Ra$ | $\frac{g\beta\Delta T L^3}{\nu\alpha}$ | Buoyancy vs diffusion |
| $Pr$ | $\frac{\nu}{\alpha}$ | Momentum vs thermal diffusion |
| $Nu$ | $\frac{hL}{k}$ | Convection vs conduction |

### Flow Regime

| $Ra$ Range | Regime |
|------------|--------|
| $< 10^3$ | Conduction dominant |
| $10^3 - 10^9$ | Laminar convection |
| $> 10^9$ | Turbulent convection |

---

## 6. Post-Processing

### Wall Heat Flux

```cpp
// system/controlDict
functions
{
    wallHeatFlux
    {
        type    wallHeatFlux;
        patches (hotWall coldWall);
    }
}
```

### Nusselt Number

$$Nu = \frac{q'' L}{k \Delta T}$$

---

## Concept Check

<details>
<summary><b>1. Boussinesq approximation ใช้เมื่อไหร่?</b></summary>

ใช้เมื่อ $\Delta T$ น้อย (< 30°C สำหรับอากาศ) — สมมติว่า $\rho = const$ ยกเว้นในเทอม buoyancy ช่วยลด computational cost
</details>

<details>
<summary><b>2. `heRhoThermo` vs `hePsiThermo` ต่างกันอย่างไร?</b></summary>

- **heRhoThermo**: ใช้ $\rho$ โดยตรง (incompressible หรือ low-Mach)
- **hePsiThermo**: ใช้ $\psi = 1/(RT)$ (fully compressible)
</details>

<details>
<summary><b>3. ทำไม CHT ต้องใช้ multi-region?</b></summary>

เพราะ solid และ fluid มี governing equations ต่างกัน — solid ไม่มี convection แค่ Laplace equation ต้องแยก mesh และ couple ที่ interface
</details>

---

## Related Documents

- **บทถัดไป:** [01_Energy_Equation_Fundamentals.md](01_Energy_Equation_Fundamentals.md)
- **Buoyancy:** [03_Buoyancy_Driven_Flows.md](03_Buoyancy_Driven_Flows.md)
- **CHT:** [04_Conjugate_Heat_Transfer.md](04_Conjugate_Heat_Transfer.md)