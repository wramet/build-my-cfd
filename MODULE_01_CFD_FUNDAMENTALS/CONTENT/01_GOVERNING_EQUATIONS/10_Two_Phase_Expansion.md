# Two-Phase Flow with Phase Change (R410A Evaporator)
# การไหลสองเฟสพร้อมการเปลี่ยนเฟส (เครื่องระเหย R410A)

## Learning Objectives

หลังจากศึกษาบทนี้ คุณควรจะสามารถ:
- **อธิบาย** การแก้สมการอนุรักษ์สำหรับการไหลสองเฟสพร้อมการเปลี่ยนเฟส
- **เขียน** สมการควบคุมที่รวมเทอม expansion สำหรับการระเหย
- **จำลอง** ค่าพลังงานแฝง (latent heat) ในสมการพลังงาน
- **ออกแบบ** เครื่องระเหย R410A ที่ใช้ OpenFOAM
- **เปรียบเทียบ** โมเดลการเปลี่ยนเฟสต่างๆ (cavitation vs heat transfer limited)
- **พัฒนา** code สำหรับโมเดลการเปลี่ยนเฟสใน OpenFOAM

---

## Navigation Map

```
02_Conservation_Laws (Single Phase)
         │
         ▼
10_Two_Phase_Expansion ← YOU ARE HERE
         │
    └────┘
         ▼
[Two-Phase Flow Fundamentals] (หมวดหมู่ถัดไป)
```

---

## Overview

ในการเปลี่ยนเฟส (phase change) เช่น การระเหยในเครื่องระเหย R410A สมการอนุรักษ์ที่เรียนมาสำหรับ single-phase flow ไม่เพียงพอ:

> **ที่มาของความยาก:**
> - **มวลไม่เก็บตาม** เนื่องจากของเหลวเปลี่ยนไปเป็นไอ (density ลดลง 30x)
> - **พลังงานดูดซับ** จำนวนมหาศาลจากการระเหย (latent heat)
> - **Interface tracking** ระหว่างของเหลวและไอ
> - **คุณสมบัติแปรตามสภาพ** (ρ, μ, k ใหม่ทุก cell)

> **ประเด็นสำคัญสำหรับ R410A:**
> - ความหนาแน่นของเหลว ≈ 1000 kg/m³, ไอ ≈ 30 kg/m³
> - อัตราการขยายตัว ≈ 33 เท่า
> - ความร้อนแฝง ≈ 200 kJ/kg ที่ 10°C

---

## 1. Mass Equation with Phase Change Expansion

### สมการความต่อเนื่องที่มีเทอม Expansion

สำหรับการไหลสองเฟสที่มีการเปลี่ยนเฟส เราต้องเพิ่มเทอม expansion:

$$
\boxed{\frac{\partial (\alpha_l \rho_l) + \partial (\alpha_v \rho_v)}{\partial t} + \nabla \cdot [(\alpha_l \rho_l + \alpha_v \rho_v) \mathbf{U}] = 0}
$$

สำหรับการระเหย (evaporation) จะมี source term เพิ่มเข้ามา:

$$
\frac{\partial \alpha_l \rho_l}{\partial t} + \nabla \cdot (\alpha_l \rho_l \mathbf{U}) = -\dot{m}_{evap}
$$

$$
\frac{\partial \alpha_v \rho_v}{\partial t} + \nabla \cdot (\alpha_v \rho_v \mathbf{U}) = +\dot{m}_{evap}
$$

โดยที่:
- $\alpha_l, \alpha_v$ = volume fraction of liquid/vapor ($\alpha_l + \alpha_v = 1$)
- $\rho_l, \rho_v$ = density of liquid/vapor phases
- $\dot{m}_{evap}$ = evaporation rate per unit volume [kg/m³s]

### ⭐ Expansion Term Verification

> **File:** `openfoam_temp/src/fvModels/general/phaseChange/phaseChange.C`
> **Lines:** 235-250

```cpp
// From phaseChange.C
void Foam::fv::phaseChange::addSup
(
    const volScalarField& alpha,
    const volScalarField& rho,
    const volScalarField& heOrYi,
    fvMatrix<scalar>& eqn
) const
{
    const volScalarField mDot = this->mDot();

    // Expansion term for mass conservation
    if (heOrYi.name() == alpha1().name())
    {
        eqn += mDot;
    }
    else if (heOrYi.name() == alpha2().name())
    {
        eqn -= mDot;
    }

    // Energy equation with latent heat
    if (is<volScalarField>(heOrYi))
    {
        const tmp<volScalarField> tLfraction = Lfraction();
        const tmp<volScalarField> tL = L();
        eqn += tLfraction() * tL() * mDot;
    }
}
```

### สมการในรูปทั่วไป (General Form)

สมการความต่อเนื่องสามารถเขียนในรูปทั่วไปได้:

$$
\frac{\partial \alpha}{\partial t} + \nabla \cdot (\alpha \mathbf{U}) = \frac{\dot{m}_{phase}}{\rho_{phase}}
$$

สำหรับ liquid-to-vapor phase change:

$$
\frac{\partial \alpha_v}{\partial t} + \nabla \cdot (\alpha_v \mathbf{U}) = +\frac{\dot{m}_{evap}}{\rho_v}
$$

$$
\frac{\partial \alpha_l}{\partial t} + \nabla \cdot (\alpha_l \mathbf{U}) = -\frac{\dot{m}_{evap}}{\rho_l}
$$

---

## 2. Energy Equation with Latent Heat

### Energy Equation for Phase Change

สมการพลังงานต้องรวมเทอม latent heat:

$$
\frac{\partial (\rho h)}{\partial t} + \nabla \cdot (\rho \mathbf{U} h) = \nabla \cdot (k \nabla T) + \underbrace{\dot{m}_{evap} L_{evap}}_{S_{latent}} + S_{other}
$$

โดยที่:
- $h = c_p T + \text{const}$ = specific enthalpy
- $L_{evap}$ = latent heat of vaporization [J/kg]
- $S_{latent} = \dot{m}_{evap} L_{evap}$ = latent heat source

### 🔥 Split Energy Approach (วิธีแบ่งพลังงาน)

แทนที่จะใช้ single energy equation เราอาจแบ่งเป็น 2 สมการ:

สำหรับ liquid phase:
$$
\frac{\partial (\alpha_l \rho_l h_l)}{\partial t} + \nabla \cdot (\alpha_l \rho_l h_l \mathbf{U}) = \nabla \cdot (\alpha_l k_l \nabla T) - \dot{m}_{evap} L_{evap}
$$

สำหรับ vapor phase:
$$
\frac{\partial (\alpha_v \rho_v h_v)}{\partial t} + \nabla \cdot (\alpha_v \rho_v h_v \mathbf{U}) = \nabla \cdot (\alpha_v k_v \nabla T) + \dot{m}_{evap} L_{evap}
$$

> **อนาล็อกทางกายภาพ:** การระเหยเหมือนกับเติมน้ำแข็งลงในน้ำร้อน - ทำให้อุณหภูมิลดลงถึงจุดหยุดเยือน

### ⭐ Latent Heat Implementation

> **File:** `openfoam_temp/src/fvModels/general/phaseChange/phaseChangeI.H`
> **Lines:** 200-225

```cpp
// Latent heat calculation from phaseChangeI.H
tmp<DimensionedField<scalar, volMesh>> Foam::fv::phaseChange::L
(
    const label mDoti
) const
{
    // Get the saturated liquid and vapour enthalpies
    const scalarField hSatL = fluidThermos().phase1().thermo().hSat();
    const scalarField hSatV = fluidThermos().phase2().thermo().hSat();

    // Latent heat = h_vapour - h_liquid
    return tmp<DimensionedField<scalar, volMesh>>
    (
        new DimensionedField<scalar, volMesh>
        (
            IOobject::groupName("L", alpha1().name()),
            mesh_,
            dimensionSet(0, 2, -2, 0, 0),
            hSatV - hSatL
        )
    );
}
```

---

## 3. Momentum Equation for Two-Phase Flow

### Modification for Two-Phase Flows

สมการโมเมนตัมสำหรับสองเฟส:

$$
\frac{\partial (\rho \mathbf{U})}{\partial t} + \nabla \cdot (\rho \mathbf{U} \mathbf{U}) = -\nabla p + \nabla \cdot (\boldsymbol{\tau}) + \rho \mathbf{g} + \mathbf{F}_{surface}
$$

ส่วนที่เพิ่มเข้ามา:
- $\rho = \alpha_l \rho_l + \alpha_v \rho_v$ = mixture density
- $\boldsymbol{\tau} = \alpha_l \boldsymbol{\tau}_l + \alpha_v \boldsymbol{\tau}_v$ = mixture stress tensor
- $\mathbf{F}_{surface}$ = surface tension force

### Surface Tension Force

สำหรับ interface ระหว่าง liquid/vapor:

$$
\mathbf{F}_{surface} = \sigma \kappa \delta_{interface} \mathbf{n}
$$

โดยที่:
- $\sigma$ = surface tension [N/m]
- $\kappa$ = curvature of interface [1/m]
- $\delta_{interface}$ = delta function at interface
- $\mathbf{n}$ = normal vector of interface

### ⭐ OpenFOAM Two-Phase Implementation

> **File:** `openfoam_temp/applications/modules/twoPhaseVoFSolver/twoPhaseVoFSolver.C`
> **Lines:** 75-80

```cpp
// Surface tension force calculation
tmp<surfaceScalarField> Foam::solvers::twoPhaseVoFSolver::surfaceTensionForce() const
{
    return interface.surfaceTensionForce();
}

// In solver loop:
fvVectorMatrix UEqn
(
    fvm::ddt(U)
  + fvm::div(phi, U)
  - fvm::laplacian(nu, U)
  ==
    fvOptions(U)
  + surfaceTensionForce()  // Add surface tension
);

UEqn.relax();
solve(UEqn);
```

---

## 4. VOF Transport Equation with Source Term

### Volume of Fraction (VOF) Method

VOF ใช้ track volume fraction ของแต่ละเฟส:

$$
\frac{\partial \alpha_l}{\partial t} + \nabla \cdot (\alpha_l \mathbf{U}) = S_\alpha
$$

ที่ไหน:
- $S_\alpha = \frac{\dot{m}_{evap}}{\rho_l}$ for evaporation
- $S_\alpha = -\frac{\dot{m}_{cond}}{\rho_v}$ for condensation

### Interface Compression Scheme

เพื่อลด numerical diffusion:

$$
\frac{\partial \alpha_l}{\partial t} + \nabla \cdot (\tilde{\mathbf{U}} \alpha_l) = 0
$$

โดยที่ $\tilde{\mathbf{U}} = \mathbf{U} + \mathbf{U}_{r}$ (compressive velocity)

### ⭐ VOF Implementation in OpenFOAM

> **File:** `openfoam_temp/src/OpenFOAM/fields/volFields/volScalarField/volScalarField.C`
> **Lines:** Interface compression

```cpp
// VOF transport with phase change
fvScalarMatrix alphaEqn
(
    fvm::ddt(alpha_l)
  + fvm::div(phi, alpha_l, divAlphaScheme)
  - fvm::laplacian
    (
        alpha_l * alpha_v * (1/rho_l + 1/rho_v) * mDot(),
        alpha_l
    )
  ==
    fvOptions(alpha_l)
);

// Add source term from phase change
alphaEqn += fvm::Sp(-mDot()/rho_l, alpha_l) + fvm::SuSp(mDot()/rho_l, alpha_l);

alphaEqn.relax();
alphaEqn.solve();
```

---

## 5. Phase Change Models for R410A

### 5.1 Heat Transfer Limited Phase Change

สำหรับระบบที่การเปลี่ยนเฟสถูกจำกัดด้วย heat transfer:

$$
\dot{m}_{evap} = \frac{q_{liquid} - q_{vapour}}{L_{evap}}
$$

โดยที่:
- $q_{liquid} = h_{liq} (T - T_{sat})$ = heat flux to interface
- $q_{vapour} = h_{vap} (T_{sat} - T)$ = heat flux from interface
- $T_{sat}$ = saturation temperature

### 5.2 Pressure-Based Cavitation Models

สำหรับ cavitation (vaporization จาก low pressure):

$$
\dot{m}_{vapour} =
\begin{cases}
C_v \frac{p_v - p}{\rho_l} \sqrt{\frac{2(p_v - p)}{3\rho_l}} & \text{if } p < p_v \\
0 & \text{otherwise}
\end{cases}
$$

### ⭐ SchnerrSauer Cavitation Model

> **File:** `openfoam_temp/src/twoPhaseModels/incompressibleCavitation/SchnerrSauer/SchnerrSauer.H`
> **Lines:** 147-148

```cpp
// SchnerrSauer cavitation model implementation
virtual Pair<tmp<volScalarField::Internal>> mDotcvAlpha() const
{
    tmp<volScalarField::Internal> mDotl
    (
        Cc_ * alphav * sqrt(2.0/3.0) * (p0_ - p())/p0_
    );

    tmp<volScalarField::Internal> mDotv
    (
        Cv_ * alphal * p()/(p0_ - p()) * sqrt(2.0 * (p() - pSat_)/(3.0 * rhol()))
    );

    return Pair<tmp<volScalarField::Internal>>(mDotl, mDotv);
}
```

### 5.3 Lee Model for Evaporation

สำหรับการระเหยโดยตรงจาก temperature:

$$
\dot{m}_{evap} = r_{evap} \alpha_l \rho_l \frac{T - T_{sat}}{T_{sat}} \quad \text{for } T > T_{sat}
$$

$$
\dot{m}_{cond} = r_{cond} \alpha_v \rho_v \frac{T_{sat} - T}{T_{sat}} \quad \text{for } T < T_{sat}
$$

---

## 6. C++ Implementation Example

### R410A Phase Change Model

```cpp
// File: R410AevaporationModel.H
class R410AevaporationModel : public fv::phaseChange
{
private:
    // Model parameters
    dimensionedScalar rEvap_;        // Evaporation coefficient [s⁻¹]
    dimensionedScalar rCond_;        // Condensation coefficient [s⁻¹]
    dimensionedScalar T_sat_;       // Saturation temperature [K]
    dimensionedScalar L_evap_;       // Latent heat [J/kg]

    // Refrigerant properties (temperature dependent)
    dimensionedScalar rho_l_;        // Liquid density
    dimensionedScalar rho_v_;        // Vapour density
    dimensionedScalar mu_l_;         // Liquid dynamic viscosity
    dimensionedScalar mu_v_;         // Vapour dynamic viscosity

    // Calculate saturation pressure using Antoine equation
    dimensionedScalar saturationPressure(const dimensionedScalar& T) const;

public:
    TypeName("R410Aevaporation");

    R410AevaporationModel
    (
        const word& name,
        const fvMesh& mesh,
        const dictionary& dict
    );

    // Mass transfer rate calculation
    virtual tmp<DimensionedField<scalar, volMesh>> mDot() const;

    // Update properties based on temperature
    void correctProperties();

    // Source term addition
    virtual void addSup
    (
        const volScalarField& alpha,
        const volScalarField& rho,
        const volScalarField& heOrYi,
        fvMatrix<scalar>& eqn
    ) const;
};
```

### Implementation Details

```cpp
// File: R410AevaporationModel.C
tmp<DimensionedField<scalar, volMesh>> R410AevaporationModel::mDot() const
{
    // Get temperature field
    const volScalarField& T = this->T();

    // Calculate mass transfer rate
    const volScalarField mDotl =
        rCond_ * alpha2() * rho_v_ *
        (T_sat_ - T) / T_sat_;

    const volScalarField mDotv =
        rEvap_ * alpha1() * rho_l_ *
        (T - T_sat_) / T_sat_;

    // Return net mass transfer
    return mDotl + mDotv;
}

void R410AevaporationModel::addSup
(
    const volScalarField& alpha,
    const volScalarField& rho,
    const volScalarField& heOrYi,
    fvMatrix<scalar>& eqn
) const
{
    // Get mass transfer rate
    const volScalarField mDot = mDot();

    // Add to mass conservation
    if (heOrYi.name() == alpha1().name())
    {
        eqn += mDot;           // Liquid phase gains mass from condensation
    }
    else if (heOrYi.name() == alpha2().name())
    {
        eqn -= mDot;           // Vapour phase loses mass from evaporation
    }

    // Add latent heat to energy equation
    if (is<volScalarField>(heOrYi))
    {
        const tmp<volScalarField> tL = L();
        eqn += L_evap_ * mDot;
    }
}
```

### Make File Configuration

```cmake
// File: Make/files
R410AevaporationModel.C
EXE_INC = -I$(LIB_SRC)/finiteVolume/lnInclude \
          -I$(LIB_SRC)/twoPhaseModels/lnInclude \
          -I$(LIB_SRC)/thermophysicalModels/basic/lnInclude

LIB_LIBS = -lfiniteVolume \
           -ltwoPhaseMixture \
           -lfluidThermo
```

### Case Dictionary Configuration

```dict
// File: constant/phaseChangeProperties
R410Aevaporation
{
    type            R410Aevaporation;

    // Evaporation/condensation coefficients
    rEvap           0.1;      // Evaporation rate coefficient [s⁻¹]
    rCond           0.01;     // Condensation rate coefficient [s⁻¹]

    // Saturation properties
    T_sat           283.15;   // Saturation temperature [K]
    L_evap          220000;   // Latent heat [J/kg]

    // Refrigerant properties (temperature dependent)
    rho_l           1000;     // Liquid density [kg/m³]
    rho_v           30;       // Vapour density [kg/m³]
    mu_l            0.0002;   // Liquid viscosity [Pa·s]
    mu_v            0.00001;  // Vapour viscosity [Pa·s]
}
```

---

## 7. Mixture Properties Calculation

### Properties for Two-Phase Flow

คุณสมบัติของส่วนผสม (mixture properties):

$$
\rho_{mix} = \alpha_l \rho_l + \alpha_v \rho_v
$$

$$
\mu_{mix} = \alpha_l \mu_l + \alpha_v \mu_v
$$

$$
k_{mix} = \alpha_l k_l + \alpha_v k_v
$$

### OpenFOAM Mixture Property Calculation

```cpp
// Calculate mixture properties
volScalarField rho = alpha_l * rho_l + alpha_v * rho_v;
volScalarField mu = alpha_l * mu_l + alpha_v * mu_v;
volScalarField k = alpha_l * k_l + alpha_v * k_v;

// Sound speed for compressible flows
volScalarField c_sqr
(
    "c",
    dimensionedScalar("c", dimVelocity*dimVelocity, 1000)
);
```

---

## 8. Numerical Considerations

### Challenges in Two-Phase Flow Simulation

| ปัญหา | ผลกระทบ | วิธีการแก้ไข |
|-------|---------|-------------|
| **Strong source terms** | ล้มเหลวที่ convergence | Under-relaxation (0.1-0.3) |
| **Sharp gradients** | Numerical diffusion | Interface compression |
| **Time step constraints** | CFL violations | Adaptive time stepping |
| **Property discontinuities** | Stiff equations | Smooth property blending |

### Stability Criteria

สำหรับ time stepping ใน two-phase flow:

1. **Courant number**: $Co = \frac{U \Delta t}{\Delta x} < 1$
2. **Interface Courant**: $Co_{interface} = \frac{U_{interface} \Delta t}{\Delta x} < 0.5$
3. **Phase change rate**: $\frac{\dot{m} \Delta t}{\rho \Delta x} < 0.1$

---

## 9. Validation and Verification

### Test Cases for R410A Evaporator

1. **Pool Boiling Validation**
   - ตรวจสอบ Nusselt number vs heat flux
   - ตรวจสอบ void fraction distribution

2. **Flow Boiling Test**
   - Pressure drop correlation
   - Heat transfer coefficient vs quality

3. **Evaporator Performance**
   - Cooling capacity prediction
   - Superheat/quality along tube

### Benchmark with Experimental Data

```cpp
// Error calculation for validation
scalar calculateRMSE(const volScalarField& numerical, const volScalarField& experimental)
{
    scalarField diff = numerical.primitiveField() - experimental.primitiveField();
    scalarField diffSquared = diff * diff;

    return sqrt(gSum(diffSquared) / diffSquared.size());
}

// Validation report
Info << "RMSE temperature: " << calculateRMSE(T_numerical, T_exp) << " K" << endl;
Info << "RMSE void fraction: " << calculateRMSE(alpha_numerical, alpha_exp) << endl;
```

---

## 10. R410A Evaporator Implementation Steps

### Step-by-Step Implementation

1. **Set up case structure**
   ```bash
   mkdir -p R410A_evaporator/{constant,system}
   ```

2. **Create mesh**
   ```cpp
   // Generate pipe mesh
   createMesh pipeMesh
   {
       type            pipe;
       length          1.0;    // m
       diameter        0.01;   // m
   }
   ```

3. **Configure thermophysical properties**
   ```dict
   // constant/thermophysicalProperties
   R410A
   {
       type            R410A;
       sigma           0.024;   // Surface tension [N/m]
   }
   ```

4. **Set up solver**
   ```dict
   // system/controlDict
   application     twoPhaseVoFSolver;
   startFrom       startTime;
   startTime       0;
   stopAt          endTime;
   endTime         0.1;
   deltaT          0.0001;
   ```

5. **Boundary conditions**
   ```dict
   // 0/U
   inlet
   {
       type            flowRateInletVelocity;
       volumetricFlowRate 0.001;  // m³/s
   }

   outlet
   {
       type            pressureOutlet;
       p               1e5;     // Pa
   }
   ```

---

## 11. Common Issues and Solutions

### Issues in R410A Evaporation Simulation

| ปัญหา | สาเหตุ | วิธีแก้ไข |
|-------|---------|-------------|
| **Numerical instability** | Large density ratio | Use compressible solver, limit α extremes |
| **Mass imbalance** | Poor discretization | Use interface compression, refine mesh |
| **Slow convergence** | Strong phase change | Under-relaxation, smaller time steps |
| **Unphysical results** | Incorrect properties | Use accurate R410A property tables |

### Debugging Tips

```bash
# Check continuity error
grep "continuity error" log.twoPhaseVoFSolver

# Check alpha bounds
postProcess -func "max(alpha1) max(alpha2) min(alpha1) min(alpha2)"

# Verify mass conservation
postProcess -func "sum(alpha1) sum(alpha2)"
```

---

## 12. Next Topics

เมื่อสำเร็จการจำลอง two-phase flow นี้ คุณสามารถ:

### Advanced Topics
- **Turbulence in Two-Phase Flow** → Euler-Euler vs Euler-Lagrange
- **Non-Equilibrium Phase Change** → Account for thermal non-equilibrium
- **Microchannel Heat Exchangers** → Surface effects dominate

### Implementation Focus
- **Coupling with System Solver** → Link with cycle simulation
- **Optimization** → Design of experiments for evaporator performance
- **Uncertainty Quantification** → Sensitivity analysis

### Learning Path
- **Module 03**: [Finite Volume Discretization](../02_FINITE_VOLUME_METHOD/00_Introduction.md)
- **Module 04**: [Two-Phase Flow Fundamentals](../05_TWO_PHASE_FLOW/00_Two_Phase_Flow_Fundamentals.md)
- **Module 05**: [OpenFOAM Programming](../../05_OPENFOAM_PROGRAMMING/00_Introduction.md)

---

## Concept Check

<details>
<summary><b>1. ทำไมสมการความต่อเนื่องจะต้องมี source term ในการเปลี่ยนเฟส?</b></summary>

**คำตอบ:** เนื่องจากมวลถูกเปลี่ยนจากเฟสหนึ่งไปยังอีกเฟสหนึ่ง:

- **Evaporation**: ของเหลวเปลี่ยนไปเป็นไอ → มวลของเหลวลด มวลไอเพิ่ม
- **Condensation**: ไอเปลี่ยนไปเป็นของเหลว → มวลไอลด มวลของเหลวเพิ่ม

**ใน OpenFOAM:**
```cpp
// Liquid equation: loses mass
eqn += mDot;  // mDot > 0 for evaporation

// Vapor equation: gains mass
eqn -= mDot;  // mDot > 0 for evaporation
```

**ที่มาของ source term:** เป็นการสอดคล้องกับกฎอนุรักษ์มวลระดับพื้นที่ ที่มวลสุทธิใน control volume ไม่เปลี่ยนแปลง

</details>

<details>
<summary><b>2. ความแตกต่างระหว่าง Cavitation และ Evaporation อะไรคือ?</b></summary>

**คำตอบ:** ความแตกต่างเชิงกายภาพ:

| คุณสมบัติ | Cavitation | Evaporation |
|---------|-----------|------------|
| **กลไก** | Pressure-driven | Temperature-driven |
| **เงื่อนไข** | $p < p_{sat}$ | $T > T_{sat}$ |
| **สถานที่** | ภายในของไหล (bulk) | ใกล้ผิวเส้น (surface) |
| **ใช้กับ** | ไอน้ำในน้ำมัน | R410A ใน evaporator |
| **โมเดล** | SchnerrSauer, Kunz | Lee, heat transfer limited |

**ใน OpenFOAM:**
- Cavitation: `twoPhaseVoFSolver + cavitationModel`
- Evaporation: `multiphaseEuler + heatTransferLimitedPhaseChange`

</details>

<details>
<summary><b>3. ทำไม interface compression scheme สำคัญสำหรับ VOF?</b></summary>

**คำตอบ:** เพื่อลด numerical diffusion ที่ทำให้ interface เบลอ:

**ปัญหา:**
- พื้นที่ผิวเส้น (interface area) ลดลงจาก numerical diffusion
- หากไม่มี compression, หลังจาก vài timestep จะได้ส่วนผสมที่ uniform
- ไม่สามารถ track interface ได้อย่างถูกต้อง

**วิธีแก้ไข:**
```cpp
// เพิ่ม compressive velocity
surfaceScalarField rhoPhi_compress =
    -fvc::flux(alpha_l) * max(min(rho_v/rho_l - 1, 1), -1);

// ใช้ใส่ใน discretization
fvm::div(phi + rhoPhi_compress, alpha_l)
```

**ผลลัพธ์:** Interface ที่คมชัด ทำให้ surface tension force คำนวณได้อย่างถูกต้อง

</details>

<details>
<summary><b>4. จะ handle discontinuity ของ properties ที่ interface ได้อย่างไร?</b></summary>

**คำตอบ:** มีหลายวิธี:

### 1. Harmonic Mean (Default in OpenFOAM)
```cpp
// For diffusion coefficient
volScalarField Gamma = alpha_l * k_l + alpha_v * k_v;

// Use harmonic mean for faces
surfaceScalarField Gamma_f = fvc::interpolate(Gamma);
```

### 2. Mass Weighted Average
```cpp
// Better for strong density contrasts
surfaceScalarField Gamma_f =
    fvc::interpolate(alpha_l) * k_l +
    fvc::interpolate(alpha_v) * k_v;
```

### 3. Interface Sharpening
```cpp
// Add correction near interface
volScalarField interfaceDist = mag(grad(alpha_l));
Gamma_f *= (1 + 10 * interfaceDist);
```

### 4. Multidomain Approach
```cpp
// Solve separate equations with interface coupling
fvScalarField TEqn_l( ... );
fvScalarField TEqn_v( ... );

// Couple at interface
TEqn_l.addSup(..., interfaceRegion);
TEqn_v.addSup(..., interfaceRegion);
```

</details>

---

## References

### OpenFOAM Source References
- **twoPhaseMixture**: `openfoam_temp/src/twoPhaseModels/twoPhaseMixture/twoPhaseMixture.H`
- **phaseChange**: `openfoam_temp/src/fvModels/general/phaseChange/phaseChange.H`
- **SchnerrSauer**: `openfoam_temp/src/twoPhaseModels/incompressibleCavitation/SchnerrSauer/SchnerrSauer.H`
- **heatTransferLimitedPhaseChange**: `openfoam_temp/applications/modules/multiphaseEuler/fvModels/heatTransferLimitedPhaseChange/heatTransferLimitedPhaseChange.H`

### Academic References
- **Schnerr & Sauer (2001)**: "Physical and numerical modeling of unsteady cavitation dynamics"
- **Anglart et al. (1997)**: "CFD prediction of flow and phase distribution in fuel assemblies with spacers"
- **Kunz et al. (2001)**: "A preconditioned Navier-Stokes method for two-phase flows"

### Textbooks
- **Bartak et al. (2015)**: "Computational Fluid Dynamics for Engineers"
- **Kern & Krause (2009)**: "VDI Heat Atlas"

---

### Related Documents
- **Previous Module**: [09_Exercises.md](../09_Exercises.md) — Practice single-phase conservation laws
- **Next Module**: [05_Two_Phase_Fundamentals](../../05_TWO_PHASE_FLOW/00_Two_Phase_Flow_Fundamentals.md) — VOF and Euler-Euler methods
- **Implementation**: [05_OpenFOAM_Programming](../../05_OPENFOAM_PROGRAMMING/00_Introduction.md) — Custom solver development