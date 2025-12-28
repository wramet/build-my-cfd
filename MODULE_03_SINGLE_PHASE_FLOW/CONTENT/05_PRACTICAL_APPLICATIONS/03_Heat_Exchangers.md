# Heat Exchangers

การจำลองเครื่องแลกเปลี่ยนความร้อนด้วย Conjugate Heat Transfer

---

## Overview

**ความท้าทาย:** แก้สมการของไหลและความร้อนพร้อมกันใน fluid และ solid domains พร้อมรักษาความต่อเนื่องที่ interface

**2 แนวทาง:**
1. **Multi-Region CHT** → `chtMultiRegionFoam` (แม่นยำ)
2. **Porous Media** → `fvOptions` (เร็ว แต่ต้อง calibrate)

---

## 1. Performance Metrics

### Effectiveness

$$\varepsilon = \frac{q_{actual}}{q_{max}} = \frac{q_{actual}}{C_{min}(T_{h,in} - T_{c,in})}$$

### NTU

$$NTU = \frac{UA}{C_{min}}$$

### LMTD

$$\Delta T_{LMTD} = \frac{\Delta T_1 - \Delta T_2}{\ln(\Delta T_1/\Delta T_2)}$$

---

## 2. Multi-Region Setup

### Directory Structure

```
constant/
├── regionProperties
├── hotFluid/
│   ├── polyMesh/
│   └── thermophysicalProperties
├── coldFluid/
│   ├── polyMesh/
│   └── thermophysicalProperties
└── solidWall/
    ├── polyMesh/
    └── thermophysicalProperties
```

### Fluid Properties

```cpp
// constant/hotFluid/thermophysicalProperties
thermoType
{
    type            heRhoThermo;
    mixture         pureMixture;
    transport       const;
    thermo          hConst;
    equationOfState perfectGas;
    energy          sensibleEnthalpy;
}

mixture
{
    thermodynamics { Cp 1005; Hf 0; }
    transport { mu 1.8e-5; Pr 0.71; }
}
```

### Solid Properties

```cpp
// constant/solidWall/thermophysicalProperties
thermoType
{
    type            heSolidThermo;
    mixture         pureMixture;
    transport       constIso;
    thermo          hConst;
    equationOfState rhoConst;
}

mixture
{
    thermodynamics { Cp 903; }
    transport { kappa 237; }  // Aluminum
    equationOfState { rho 2700; }
}
```

### Interface BC

```cpp
// 0/T for each region
hotFluid_to_solidWall
{
    type    compressible::turbulentTemperatureCoupledBaffleMixed;
    Tnbr    T;
    value   uniform 300;
}
```

---

## 3. Porous Media Approach

### fvOptions

```cpp
// system/fvOptions
porousHeatExchanger
{
    type            explicitPorositySource;
    cellZone        heatExchangerZone;
    
    explicitPorositySourceCoeffs
    {
        type    DarcyForchheimer;
        d       (1e5 1e5 1e5);  // Darcy coeff
        f       (10 10 10);      // Forchheimer coeff
    }
}

heatSource
{
    type            scalarSemiImplicitSource;
    cellZone        heatExchangerZone;
    
    scalarSemiImplicitSourceCoeffs
    {
        T { Su 10000; Sp 0; }  // W/m³
    }
}
```

---

## 4. Monitoring

### Function Objects

```cpp
// system/controlDict
functions
{
    tempInlet
    {
        type        surfaceFieldValue;
        operation   weightedAverage;
        weightField phi;
        fields      (T);
        patches     (inlet);
    }
    
    pressureDrop
    {
        type    pressureDifference;
        patches (inlet outlet);
    }
    
    heatTransfer
    {
        type    wallHeatTransferCoeff;
        patches (heatExchangerWalls);
    }
}
```

---

## 5. Validation

### LMTD Method

Compare:
$$Q_{CFD} = \dot{m} c_p (T_{in} - T_{out})$$
$$Q_{theory} = U A \Delta T_{LMTD}$$

$$Error = \left|\frac{Q_{CFD} - Q_{theory}}{Q_{theory}}\right| < 10\%$$

### Energy Balance

$$\left|\frac{\dot{Q}_{hot} - \dot{Q}_{cold}}{\dot{Q}_{hot}}\right| < 5\%$$

### Nusselt Number

Compare with correlations:
- **Dittus-Boelter:** $Nu = 0.023 Re^{0.8} Pr^n$
- **Gnielinski:** more accurate for $3000 < Re < 5 \times 10^6$

---

## 6. Mesh Guidelines

| Parameter | Target | Reason |
|-----------|--------|--------|
| $y^+$ | ≈ 1 | Accurate wall heat flux |
| Expansion ratio | < 1.2 | Numerical stability |
| Non-orthogonality | < 65° | Gradient accuracy |
| Layers on interface | 3-5 | Heat transfer capture |

---

## Concept Check

<details>
<summary><b>1. Multi-Region กับ Porous ต่างกันอย่างไร?</b></summary>

- **Multi-Region:** แก้สมการจริงในทุก domain → แม่นยำ แต่ช้าและต้องการ mesh ละเอียด
- **Porous:** แทนที่โครงสร้างซับซ้อนด้วย resistance term → เร็ว แต่ต้อง calibrate กับ experiment
</details>

<details>
<summary><b>2. Interface BC ทำงานอย่างไร?</b></summary>

`turbulentTemperatureCoupledBaffleMixed` บังคับให้:
- Temperature เท่ากันที่ interface
- Heat flux ต่อเนื่อง: $q = -k_{fluid}\nabla T = -k_{solid}\nabla T$
</details>

<details>
<summary><b>3. ทำไม $y^+$ ใกล้ 1 สำคัญสำหรับ heat transfer?</b></summary>

Temperature gradient สูงสุดอยู่ใน viscous sublayer — ถ้า mesh หยาบเกินจะ miss gradient นี้ → heat flux ผิดพลาด
</details>

---

## Related Documents

- **บทก่อนหน้า:** [02_Internal_Flow_and_Piping.md](02_Internal_Flow_and_Piping.md)
- **บทถัดไป:** [04_HVAC_Applications.md](04_HVAC_Applications.md)