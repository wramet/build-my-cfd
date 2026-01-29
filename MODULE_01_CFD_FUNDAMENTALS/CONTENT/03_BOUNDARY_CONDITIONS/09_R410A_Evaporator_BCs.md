# R410A Evaporator Boundary Conditions

> **เงื่อนไขขอบเขตสำหรับเครื่องระเหย R410A**

---

## 🎯 Learning Objectives

หลังจากศึกษาบทนี้ คุณจะสามารถ:

1. **เลือกและใช้** Boundary conditions ที่เหมาะสมกับ evaporator สองเฟส
2. **Implement** Mass flow inlet สำหรับของเหลว subcooled
3. **ตั้งค่า** Pressure outlet ที่ saturation pressure
4. **จำลอง** Wall heat transfer จากภายนอก
5. **จัดการกับ** Phase-specific boundaries (void fraction)
6. **สร้าง** Complete BC setup สำหรับ OpenFOAM simulation

### Prerequisites
- ความเข้าใจ Basic BCs — ดู [05_Common_Boundary_Conditions_in_OpenFOAM.md](05_Common_Boundary_Conditions_in_OpenFOAM.md)
- พื้นฐาน Two-phase flow mechanics
- ความเข้าใจ R410A properties

---

## 📋 R410A Evaporator BC Configuration

| Boundary | Type | Key Parameters | Physics |
|----------|------|---------------|---------|
| **Inlet** | Mass flow, subcooled liquid | $\dot{m}$, $T_{subcool}$, $\alpha=0$ | Single-phase liquid |
| **Wall** | External heat flux | $h$, $T_{ext}$, mode=coefficient | Convective heating |
| **Outlet** | Pressure, two-phase | $P_{sat}$, $\alpha$ variable | Mixed-phase flow |
| **Axis** | Symmetry | Axisymmetric | Centerline |

---

## 🔍 Two-Phase Flow Physics in Evaporators

### Phase Distribution Characteristics

| Region | Flow Regime | Void Fraction $\alpha$ | Heat Transfer Mode |
|--------|-------------|------------------------|-------------------|
| **Inlet** | Single-phase liquid | $\alpha = 0$ | Convective |
| **Developing** | Bubbly flow | $0 < \alpha < 0.3$ | Nucleate boiling |
| **Core** | Slug/churn flow | $0.3 < \alpha < 0.8$ | Convective + boiling |
| **Outlet** | Annular flow | $\alpha \rightarrow 1$ | Convective vapor |

### Mass Conservation

For steady-state two-phase flow:

$$
\dot{m}_{in} = \dot{m}_{liquid} + \dot{m}_{vapor} = \rho_l \alpha_l A U + \rho_v \alpha_v A U
$$

Where:
- $\alpha_l + \alpha_v = 1$ (void fraction conservation)
- Quality at outlet: $x = \frac{\dot{m}_{vapor}}{\dot{m}_{total}}$

---

## 🛠️ Boundary Condition Implementation

### 1. Inlet BC: Subcooled Liquid R410A

> **Physical requirements:**
> - Single-phase liquid flow
> - Subcooled temperature (below saturation)
> - Zero void fraction at inlet

**Operating conditions:**
```cpp
// Typical evaporator parameters
m_dot      0.03       // kg/s
D_inlet    0.008      // m (8mm tube)
T_inlet    280        // K (subcooled 3K below saturation)
T_sat      283        // K at 1.0 MPa
P_inlet    1.1e6      // Pa (slightly subcooled)
```

**OpenFOAM implementation:**

```cpp
// 0/U - Mass flow inlet
inlet
{
    type            flowRateInletVelocity;
    massFlowRate    constant 0.03;      // kg/s
    density         rho;                  // Use field or constant
    value           uniform (0.54 0 0);  // Initial guess (calculated)
}

// T - Temperature (subcooled)
inlet
{
    type            fixedValue;
    // T = T_sat - ΔT_subcool = 283K - 3K = 280K
    value           uniform 280;          // K
}

// alpha.water - Void fraction (pure liquid)
inlet
{
    type            fixedValue;
    value           uniform 1;            // All liquid, no vapor
}

// nut - Turbulent viscosity
inlet
{
    type            turbulentIntensityInlet;
    intensity       0.05;                // 5% turbulence
    viscosity       nu;                  // Dynamic viscosity field
    value           uniform 0;
}
```

**💡 Calculation details:**
```cpp
// Calculate inlet velocity from mass flow:
// U = m_dot / (ρ * A)
// For R410A liquid at 280K: ρ ≈ 1100 kg/m³
// Tube area: A = πD²/4 = π(0.008)²/4 = 5.03e-5 m²
// U = 0.03 / (1100 * 5.03e-5) = 0.54 m/s
```

### 2. Wall BC: Heat Transfer from External Fluid

> **Heat transfer modes:**
> - Convection from hot fluid (water/air)
> - Heat flux into refrigerant
> - Phase change at wall surface

**Implementation options:**

```cpp
// Option 1: Fixed temperature (if external T known)
wall
{
    type            fixedValue;
    // Wall temperature (set by external conditions)
    value           uniform 300;          // K (27°C)
}

// Option 2: Fixed heat flux (for electric heating)
wall
{
    type            fixedFluxTemperature;
    heatFlux        uniform 50000;       // W/m² (50 kW/m²)
    value           uniform 290;          // Initial guess
}

// Option 3: External convection (recommended)
wall
{
    type            externalTemperature;
    // Convective heat transfer coefficient
    h               uniform 1000;        // W/m²·K (water-side)
    // External fluid temperature
    Ta              uniform 300;         // K (27°C)
    value           uniform 290;          // Initial guess
}
```

**Temperature boundary conditions:**

```cpp
// Additional fields for wall handling
// p_rgh - Pressure at wall
wall
{
    type            zeroGradient;         // dp/dn = 0 at wall
    value           uniform 1.1e6;        // Pa
}

// U - Velocity (no-slip condition)
wall
{
    type            noSlip;               // U = 0 at wall
}

// alpha.water - Void fraction at wall
wall
{
    type            zeroGradient;         // No phase accumulation
    // This allows nucleation at wall when T > T_sat
    value           uniform 1;            // Initial: all liquid
}
```

### 3. Outlet BC: Two-Phase Mixture

> **Key considerations:**
> - Pressure at saturation conditions
> - Allow backflow of vapor
> - Fully developed flow assumptions

**Pressure-temperature coupling:**

```cpp
// p_rgh - Pressure (fixed at saturation)
outlet
{
    type            fixedFluxPressure;
    // Pressure gradient zero (fully developed)
    refValue        uniform 1.08e6;      // Pa (saturation at 285K)
    refGradient     uniform 0;
    value           uniform 1.08e6;
}

// U - Velocity (zero gradient)
outlet
{
    type            zeroGradient;         // dU/dn = 0 (fully developed)
    value           uniform (2.0 0 0);    // Expected velocity
}

// T - Temperature (zero gradient)
outlet
{
    type            zeroGradient;         // dT/dn = 0
    value           uniform 285;          // K (near saturation)
}

// alpha.water - Void fraction (with backflow handling)
outlet
{
    type            inletOutlet;
    // Value when flow is from domain to outlet
    value           uniform 0.8;          // 80% vapor at outlet
    // Value when backflow occurs (outlet to domain)
    inletValue      uniform 0.2;          // Backflow: 20% vapor
}
```

**Why `inletOutlet` for void fraction?**
- ✅ Allows vapor to escape naturally at outlet
- ✅ Handles backflow if outlet pressure fluctuates
- ✅ Prevents unbounded void fraction values

### 4. Axis BC: Centerline (2D Axisymmetric)

> **For 2D axisymmetric simulations:**
> - Symmetry boundary
> - No flow across axis
> - Gradient conditions for tangential velocities

```cpp
// Axis boundary condition
axis
{
    type            symmetry;             // No flow across axis
}

// Symmetric field implementations
U
{
    type            symmetry;             // dU/dn = 0
}

T
{
    type            symmetry;             // dT/dn = 0
}

alpha.water
{
    type            symmetry;             // dα/dn = 0
}

p_rgh
{
    type            symmetry;             // dp/dn = 0
}
```

---

## 📦 Complete Boundary Files

### 0/p_rgh - Pressure Field

```cpp
/*--------------------------------*- C++ -*----------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  www.openfoam.org
    \\  /    A nd           | Version:  7
     \\/     M anipulation  |
\*---------------------------------------------------------------------------*/
FoamFile
{
    format      ascii;
    class       volScalarField;
    object      p_rgh;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

boundaryField
{
    inlet
    {
        type            fixedFluxPressure;
        // Reference pressure value (initial guess)
        refValue        uniform 1.1e6;      // Pa
        // Pressure gradient (zero for fully developed)
        refGradient     uniform 0;
        value           uniform 1.1e6;
    }

    outlet
    {
        type            fixedFluxPressure;
        // Fixed at saturation pressure
        refValue        uniform 1.08e6;     // Pa
        refGradient     uniform 0;
        value           uniform 1.08e6;
    }

    wall
    {
        type            zeroGradient;         // No pressure gradient at wall
        value           uniform 1.1e6;
    }

    axis
    {
        type            symmetry;             // Axis of symmetry
    }
}

// ************************************************************************* //
```

### T - Temperature Field

```cpp
/*--------------------------------*- C++ -*----------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  www.openfoam.org
    \\  /    A nd           | Version:  7
     \\/     M anipulation  |
\*---------------------------------------------------------------------------*/
FoamFile
{
    format      ascii;
    class       volScalarField;
    object      T;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 280;          // K (subcooled)
    }

    outlet
    {
        type            zeroGradient;         // Fully developed
        value           uniform 285;
    }

    wall
    {
        type            externalTemperature;
        h               uniform 1000;        // W/m²·K
        Ta              uniform 300;         // K (external fluid)
        value           uniform 290;
    }

    axis
    {
        type            symmetry;
    }
}

// ************************************************************************* //
```

### alpha.water - Void Fraction Field

```cpp
/*--------------------------------*- C++ -*----------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  www.openfoam.org
    \\  /    A nd           | Version:  7
     \\/     M anipulation  |
\*---------------------------------------------------------------------------*/
FoamFile
{
    format      ascii;
    class       volScalarField;
    object      alpha.water;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 1;            // Pure liquid at inlet
    }

    outlet
    {
        type            inletOutlet;
        // Expected quality at outlet
        value           uniform 0.8;          // 80% vapor
        // Value for backflow (if flow reverses)
        inletValue      uniform 0.2;          // 20% vapor backflow
    }

    wall
    {
        type            zeroGradient;         // No phase accumulation
        value           uniform 1;
    }

    axis
    {
        type            symmetry;
    }
}

// ************************************************************************* //
```

### U - Velocity Field

```cpp
/*--------------------------------*- C++ -*----------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  www.openfoam.org
    \\  /    A nd           | Version:  7
     \\/     M anipulation  |
\*---------------------------------------------------------------------------*/
FoamFile
{
    format      ascii;
    class       volVectorField;
    object      U;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

boundaryField
{
    inlet
    {
        type            flowRateInletVelocity;
        massFlowRate    constant 0.03;      // kg/s
        density         rho;                  // Field or constant
        value           uniform (0.54 0 0);
    }

    outlet
    {
        type            zeroGradient;         // Fully developed
        value           uniform (2.0 0 0);
    }

    wall
    {
        type            noSlip;               // No-slip condition
    }

    axis
    {
        type            symmetry;
    }
}

// ************************************************************************* //
```

---

## ⚡ Convergence and Stability Tips

### Common Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| **Pressure oscillations** | Outlet pressure fix too strong | Use `fixedFluxPressure` with relaxation |
| **Mass imbalance** | BCs don't conserve mass | Check $\dot{m}_{in} = \dot{m}_{out}$ |
| **Void fraction > 1** | Backflow not handled properly | Set realistic `inletValue` for `inletOutlet` |
| **Divergence at startup** | Initial conditions far from solution | Use gradual ramping of heat flux |
| **Nucleation at wall** | BC prevents bubble formation | Use `zeroGradient` for $\alpha$ at wall |

### Initialization Strategy

```cpp
// Initial conditions in 0/
// Should match typical operating conditions
p_rgh      uniform 1.1e6;    // Pa (slightly subcooled)
T          uniform 282;      // K (near saturation)
alpha.water uniform 0.1;      // Small vapor fraction
U          uniform (1.0 0 0); // Moderate inlet velocity
```

### Runtime Adjustments

```cpp
// Relaxation factors in system/fvSolution
relaxationFactors
{
    p_rgh       0.3;
    U           0.7;
    T           0.5;
    alpha.water 0.5;
}
```

---

## 📚 R410A Property Considerations

### Thermophysical Properties

| Property | Liquid Phase | Vapor Phase | Unit |
|----------|-------------|-------------|------|
| Density | 1100 | 45 | kg/m³ |
| Viscosity | 1.5e-4 | 1.2e-5 | Pa·s |
| Specific heat | 1400 | 1000 | J/kg·K |
| Thermal conductivity | 0.08 | 0.02 | W/m·K |

### Saturation Properties (at 1.1 MPa)

```cpp
// Property definitions
T_sat      283;     // K
h_fg       1.8e5;   // J/kg (latent heat)
rho_l      1100;    // kg/m³
rho_v      45;      // kg/m³
```

---

## 🔍 Verification and Validation

### Mass Conservation Check

```bash
# After running simulation, check mass balance
postProcess -func "massFlowInletOutlet"
```

### Expected Results

| Parameter | Value | Validation |
|-----------|-------|------------|
| Inlet velocity | 0.54 m/s | From $\dot{m} = \rho A U$ |
| Outlet quality | 0.7-1.0 | From energy balance |
| Pressure drop | 0.02-0.05 MPa | From flow resistance |
| Heat flux | 50 kW/m² | From q = h(T_ext - T) |

### Physical Validation

1. **Phase change should occur** when T > T_sat
2. **Void fraction should increase** along tube length
3. **Pressure should drop** due to flow acceleration
4. **Temperature should rise** due to heat addition

---

## 📚 Concept Check

<details>
<summary><b>1. ทำไมต้องใช้ fixedFluxPressure แทน fixedValue ที่ outlet?</b></summary>

**`fixedFluxPressure` ดีกว่าสำหรับ outlet:**
- ✅ ให้ pressure gradient zero (fully developed flow)
- ✅ จัดการกับ backflow ได้ดี
- ✅ ลด oscillation ใน transient simulation
- ✅ More physical for outlet boundaries

**`fixedValue` ใช้ได้:**
- ถ้ารู้ pressure แน่นอน (จาก measurement)
- ใน steady-state ที่ converging
</details>

<details>
<summary><b>2. เมื่อไหร่ควรใช้ zeroGradient กับ inletOutlet สำหรับ alpha?</b></summary>

**ใช้ zeroGradient:**
- ที่ wall: ไม่มีการสะสมเฟสที่ผนัง
- ในบาง cases ที่ outlet (ถ้าไม่มี backflow)

**ใช้ inletOutlet:**
- ที่ outlet: จัดการ backflow ได้
- ใช้ในสถานการณ์ที่ flow direction อาจเปลี่ยนแปลง
</details>

<details>
<summary><b>3. การจัดการกับ nucleation ที่ผนัง</b></summary>

**Nucleation at wall:**
- เกิดเมื่อ T_wall > T_sat
- ใช้ `zeroGradient` สำหรับ alpha.water ที่ผนัง
- ให้ solver คำนวณ phase change โดยตรง

**ปัญหา:**
- `fixedValue` ที่ผนังจะบล็อก nucleation
- `inletOutlet` ไม่เหมาะสมที่ผนัง
</details>

<details>
<summary><b>4. Convergence สำหรับ two-phase flow</b></summary>

**Strategies:**
1. **Initial conditions:** ใกล้เคียง solution
2. **Relaxation factors:** ใช้ factors ที่ต่ำ (0.3-0.5)
3. **Gradual ramping:** ค่อยๆ เพิ่ม heat flux
4. **Mesh:** ละเอียดพอสำหรับ resolve interfaces

**พารามิเตอร์ที่สำคัญ:**
- relaxationFactors{alpha.water 0.5}
- ใช้ adaptive time stepping
</details>

---

## 🔗 Cross-References

### Related Files in This Module
- **Previous:** [05_Common_Boundary_Conditions_in_OpenFOAM.md](05_Common_Boundary_Conditions_in_OpenFOAM.md) — Basic BCs
- **Previous:** [06_Advanced_Boundary_Conditions.md](06_Advanced_Boundary_Conditions.md) — Advanced BC techniques
- **Next:** [07_Troubleshooting_Boundary_Conditions.md](07_Troubleshooting_Boundary_Conditions.md) — BC debugging

### Prerequisite Knowledge
- **Two-phase flow:** [MODULE_01_CFD_FUNDAMENTALS/CONTENT/05_TWO_PHASE_FLOW/](../05_TWO_PHASE_FLOW/)
- **Evaporator theory:** [MODULE_01_CFD_FUNDAMENTALS/CONTENT/06_PHASE_CHANGE_THEORY/](../06_PHASE_CHANGE_THEORY/)
- **R410A properties:** [MODULE_01_CFD_FUNDAMENTALS/CONTENT/07_REFRIGERANT_PROPERTIES/](../07_REFRIGERANT_PROPERTIES/)

---

## 📌 Key Takeaways

### ✅ Core Concepts
1. **Mass flow inlet:** สำหรับของเหลว subcooled ที่จุดเริ่มต้น
2. **External heat flux:** จำลองการถ่ายเทความร้อนจากภายนอก
3. **Pressure outlet:** คงค่าที่ saturation pressure
4. **Phase-specific BCs:** ใช้ inletOutlet สำหรับ void fraction ที่ outlet

### ✅ Implementation Best Practices
1. **Start conservative:** ใช้ relaxation factors ที่ต่ำ
2. **Check mass balance:** $\dot{m}_{in} = \dot{m}_{out}$
3. **Physical validation:** ตรวจสอบว่า solution ตรงกับ physics
4. **Gradual approach:** เพิ่ม heat flux ทีละน้อย

### ✅ Common Pitfalls to Avoid
1. ❌ ใช้ `fixedValue` สำหรับ pressure ที่ outlet → ลด convergence
2. ❌ ใช้ `inletOutlet` ที่ wall → ไม่เหมาะสมสำหรับ nucleation
3. ❌ ไม่ตรวจ mass conservation → ไม่ได้ solution ที่ถูกต้อง
4. ❌ Initial condition ไกลจาก solution → divergence

### ✅ Quick Reference
- **Inlet:** `flowRateInletVelocity` + `fixedValue(T)` + `fixedValue(α=1)`
- **Wall:** `externalTemperature` + `zeroGradient(α)`
- **Outlet:** `fixedFluxPressure` + `inletOutlet(α)`
- **Axis:** `symmetry`

---

**หัวข้อถัดไป:** [07_Troubleshooting_Boundary_Conditions.md](07_Troubleshooting_Boundary_Conditions.md) — การวินิจฉัยและแก้ปัญหา BCs

---