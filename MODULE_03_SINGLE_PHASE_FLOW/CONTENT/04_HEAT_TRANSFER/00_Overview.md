# Heat Transfer Overview

การจำลองการถ่ายเทความร้อนใน OpenFOAM

> **ทำไมต้องเข้าใจ Heat Transfer?**
> - **งาน CFD จริงส่วนใหญ่มี thermal** — cooling, heating, HVAC
> - ต้องเลือก solver ให้ถูก — buoyancy vs CHT vs radiation
> - เข้าใหม่ thermophysicalProperties = ตั้งค่าได้ถูก

---

## Learning Objectives

เมื่ออ่านจบบทนี้ คุณจะสามารถ:

1. **WHAT (Concepts):** อธิบายโหมดการถ่ายเทความร้อนทั้ง 3 แบบและสมการพลังงานที่เกี่ยวข้อง
2. **WHY (Physical Importance):** เลือก solver ที่เหมาะสมกับแต่ละสถานการณ์ (natural convection, CHT, radiation)
3. **HOW (Implementation):** ตั้งค่า thermophysicalProperties, boundary conditions และ buoyancy ใน OpenFOAM

---

## Quick Start

> **💡 เลือก Solver จาก Physics:**
>
> | ต้องการจำลอง | Solver | Key File |
> |-------------|--------|----------|
> | Natural convection (small1$\Delta T$) | `buoyantBoussinesqSimpleFoam` | `thermophysicalProperties` |
> | Large1$\Delta T1/ compressible | `buoyantSimpleFoam` | `thermophysicalProperties` |
> | Transient with buoyancy | `buoyantPimpleFoam` | `g`, `thermophysicalProperties` |
> | Solid-fluid coupling (CHT) | `chtMultiRegionFoam` | `regionProperties` |

---

## 1. Heat Transfer Modes

### WHAT: Transfer Mechanisms

| Mode | Mechanism | OpenFOAM Term |
|------|-----------|---------------|
| **Conduction** |1$q = -k\nabla T1| `fvm::laplacian(k, T)` |
| **Convection** |1$q = h(T_s - T_\infty)1| `fvm::div(phi, h)` |
| **Radiation** |1$q = \varepsilon\sigma T^41| `radiationModel` |

### WHY: Physical Importance

- **Conduction:** สำคัญใน solid, boundary layers — heat transfer โดยไม่มีการเคลื่อนที่ของ fluid
- **Convection:** เป็นกลไกหลักใน fluid flow — coupling ระหว่าง velocity และ temperature fields
- **Radiation:** สำคัญใน high-temperature applications (combustion, furnaces) — ต้องใช้ radiation model

### HOW: Energy Equation Implementation

$$\frac{\partial (\rho h)}{\partial t} + \nabla \cdot (\rho \mathbf{u} h) = \nabla \cdot (\alpha_{eff} \nabla h) + Q$$

ใน OpenFOAM:
- Left-hand side: `fvm::ddt(rho, h) + fvm::div(phi, h)`
- Right-hand side: `fvm::laplacian(alphaEff, h) + Q`

---

## 2. Thermophysical Properties

### WHAT: Property Models

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

### WHY: Model Selection Strategy

| Fluid Type | `equationOfState` | `transport` | Use Case |
|------------|-------------------|-------------|----------|
| Incompressible liquid | `rhoConst` | `const` | Water, oils (properties constant) |
| Ideal gas | `perfectGas` | `sutherland` | Air at varying temperatures |
| Boussinesq | `Boussinesq` | `const` | Natural convection, small1$\Delta T1|

### HOW: Key Differences

- **heRhoThermo:**1$\rho1ถูกกำหนดโดยตรง (incompressible หรือ low-Mach)
- **hePsiThermo:**1$\psi = 1/(RT)1ใช้สำหรับ fully compressible flows

> **📖 ดูรายละเอียดเพิ่มเติมใน:** [01_Energy_Equation_Fundamentals.md](01_Energy_Equation_Fundamentals.md)

---

## 3. Boundary Conditions (0/T)

### WHAT: Common BCs for Temperature

### Fixed Temperature

```cpp
hotWall { type fixedValue; value uniform 350; }
```

**WHY:** ใช้เมื่อ surface temperature เป็นค่าคงที่ (known boundary condition)

### Fixed Heat Flux

```cpp
heater { type fixedGradient; gradient uniform 1000; }  // W/m²
```

**WHY:** ใช้สำหรับ prescribed heat input (heater, electronics cooling)

### Convective (Robin BC)

```cpp
external
{
    type    externalWallHeatFluxTemperature;
    mode    coefficient;
    h       uniform 25;      // W/m²K
    Ta      uniform 293;     // Ambient temperature
}
```

**WHY:** Simulate convection ที่ boundary โดยไม่ต้อง mesh external domain — ใช้ coefficient1$h1และ1$T_\infty$

### Adiabatic

```cpp
insulated { type zeroGradient; }
```

**WHY:** ใช้สำหรับ insulated walls — ไม่มี heat flux ผ่าน boundary

---

## 4. Buoyancy Setup

### WHAT: Gravity & Density Variations

### constant/g

```cpp
dimensions [0 1 -2 0 0 0 0];
value      (0 -9.81 0);
```

### WHY: Buoyancy Importance

Buoyancy drives natural convection — coupling ระหว่าง temperature และ velocity through density variations

### HOW: Boussinesq Approximation

$$\rho = \rho_0 [1 - \beta(T - T_0)]$$

Valid when:1$\beta \Delta T \ll 11(typically1$\Delta T < 30$°C for air)

**ข้อดี:**
- ลด computational cost —1$\rho1เป็นค่าคงที่ในส่วนใหญ่
- Simple to implement

**ข้อจำกัด:**
- ใช้ได้เฉพาะ small temperature variations
- ไม่เหมาะกับ compressible flows

> **📖 ดูรายละเอียดเพิ่มเติมใน:** [03_Buoyancy_Driven_Flows.md](03_Buoyancy_Driven_Flows.md)

---

## 5. Dimensionless Numbers

### WHAT: Key Parameters

| Number | Formula | Physical Meaning |
|--------|---------|------------------|
|1$Ra1|1$\frac{g\beta\Delta T L^3}{\nu\alpha}1| Buoyancy vs diffusion |
|1$Pr1|1$\frac{\nu}{\alpha}1| Momentum vs thermal diffusion |
|1$Nu1|1$\frac{hL}{k}1| Convection vs conduction |

### WHY: Flow Regime Determination

|1$Ra1Range | Regime | Characteristics |
|------------|--------|-----------------|
|1$< 10^31| Conduction dominant | Heat transfer โดย conduction เป็นหลัก |
|1$10^3 - 10^91| Laminar convection | Buoyancy-driven laminar flow |
|1$> 10^91| Turbulent convection | Turbulent natural convection |

### HOW: Practical Use

- **Rayleigh number ($Ra$):** ใช้เลือก turbulence model และ grid resolution
- **Prandtl number ($Pr$):** ใช้ตั้งค่าใน `thermophysicalProperties`
- **Nusselt number ($Nu$):** ใช้ validate ผลลัพธ์กับ empirical correlations

---

## 6. Post-Processing

### WHAT: Heat Transfer Metrics

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

**WHY:** Measure ปริมาณ heat transfer ผ่าน walls — สำคัญสำหรับ design และ validation

### Nusselt Number Calculation

$$Nu = \frac{q'' L}{k \Delta T}$$

**HOW:** คำนวณจาก wall heat flux, characteristic length และ temperature difference

---

## Concept Check

<details>
<summary><b>1. Boussinesq approximation ใช้เมื่อไหร่?</b></summary>

ใช้เมื่อ1$\Delta T1น้อย (< 30°C สำหรับอากาศ) — สมมติว่า1$\rho = const1ยกเว้นในเทอม buoyancy ช่วยลด computational cost
</details>

<details>
<summary><b>2. `heRhoThermo` vs `hePsiThermo` ต่างกันอย่างไร?</b></summary>

- **heRhoThermo**: ใช้1$\rho1โดยตรง (incompressible หรือ low-Mach)
- **hePsiThermo**: ใช้1$\psi = 1/(RT)1(fully compressible)
</details>

<details>
<summary><b>3. ทำไม CHT ต้องใช้ multi-region?</b></summary>

เพราะ solid และ fluid มี governing equations ต่างกัน — solid ไม่มี convection แค่ Laplace equation ต้องแยก mesh และ couple ที่ interface
</details>

---

## Key Takeaways

1. **Solver Selection:** เลือก solver ตาม physics — `buoyantBoussinesqSimpleFoam` (small1$\Delta T$), `buoyantSimpleFoam` (large1$\Delta T$), `chtMultiRegionFoam` (solid-fluid coupling)
2. **Thermophysical Properties:** ใช้ `heRhoThermo` สำหรับ incompressible/low-Mach, `hePsiThermo` สำหรับ compressible
3. **Boundary Conditions:** `fixedValue`, `fixedGradient`, `externalWallHeatFluxTemperature` คือ BCs หลักสำหรับ heat transfer
4. **Buoyancy:** ใช้ Boussinesq approximation สำหรับ small temperature variations — ตั้งค่าใน `constant/g`
5. **Dimensionless Numbers:**1$Ra$,1$Pr$,1$Nu1ใช้เลือก solver, ตั้งค่า properties และ validate ผลลัพธ์

---

## Related Documents

- **บทถัดไป:** [01_Energy_Equation_Fundamentals.md](01_Energy_Equation_Fundamentals.md)
- **Buoyancy:** [03_Buoyancy_Driven_Flows.md](03_Buoyancy_Driven_Flows.md)
- **CHT:** [04_Conjugate_Heat_Transfer.md](04_Conjugate_Heat_Transfer.md)