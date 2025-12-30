# Energy Conservation Equations

สมการอนุรักษ์พลังงานสำหรับ Multiphase Flow

---

## Learning Objectives

เป้าหมายการเรียนรู้ (Learning Objectives):

- **เข้าใจ** (Understand) รูปแบบสมการอนุรักษ์พลังงานสำหรับแต่ละเฟสในระบบ multiphase
- **วิเคราะห์** (Analyze) บทบาทของ interphase heat transfer ในการเชื่อมโยงพลังงานระหว่างเฟส
- **เลือกใช้** (Select) heat transfer correlation ที่เหมาะสมกับสถานการณ์จำลองที่แตกต่างกัน
- **ประเมิน** (Evaluate) ข้อดี-ข้อเสียระหว่าง enthalpy และ temperature formulations
- **ประยุกต์** (Apply) การตั้งค่า boundary conditions และ thermophysical models ใน OpenFOAM

---

## 1. Overview of Energy Conservation

### 1.1 What is Energy Conservation in Multiphase Flow?

**สมการอนุรักษ์พลังงาน** (Energy Conservation Equation) ในระบบ multiphase เป็นสมการที่อธิบายการเปลี่ยนแปลงของพลังงานภายในแต่ละเฟส โดยมีลักษณะเด่นคือ:

- **แต่ละเฟสมีสมการพลังงานของตัวเอง** — แต่ละ phase มี temperature/enthalpy และ thermodynamic properties ที่แตกต่างกัน
- **เชื่อมโยงผ่าน interphase heat transfer** — พลังงานแลกเปลี่ยนระหว่างเฟสผ่าน interface
- **รองรับ phase change** — รวม latent heat effects สำหรับการเปลี่ยนสถานะ

### 1.2 Why Does Energy Conservation Matter?

**ทำไมต้องใส่ใจกับสมการพลังงาน?**

1. **Temperature-driven flows** — ความแตกต่างของอุณหภูมิสร้าง buoyancy forces → ส่งผลต่อ flow patterns
2. **Heat transfer efficiency** — สำคัญใน heat exchangers, condensers, boilers
3. **Phase change prediction** — จำลองการ evaporate/condense ได้ถูกต้อง
4. **Chemical reaction rates** — reactions dependent on temperature
5. **Safety analysis** — temperature runaway ใน reactors

### 1.3 How is Energy Conserved in Multiphase Systems?

**กลไกการถ่ายเทความร้อนในระบบ multiphase:**

| Mechanism | Description | Equation |
|-----------|-------------|----------|
| **Convection** | พลังงานถูกพาไปกับ mass flow | $\nabla \cdot (\alpha_k \rho_k h_k \mathbf{u}_k)$ |
| **Conduction** | ความร้อนไหลผ่าน temperature gradient | $\nabla \cdot (\alpha_k k_k \nabla T_k)$ |
| **Interphase Transfer** | แลกเปลี่ยนความร้อนระหว่างเฟส | $h_{kl} A_{kl} (T_l - T_k)$ |
| **Pressure Work** | งานจากความดัน | $\alpha_k \frac{Dp}{Dt}$ |
| **Latent Heat** | พลังงานจาก phase change | $\dot{m}_{lk} \cdot L_{lk}$ |

---

## 2. General Form of Energy Equation

### 2.1 Enthalpy Formulation

**สมการพลังงานแบบ enthalpy** (เป็นรูปแบบที่ใช้บ่อยที่สุดใน OpenFOAM):

$$\boxed{\frac{\partial(\alpha_k \rho_k h_k)}{\partial t} + \nabla \cdot (\alpha_k \rho_k h_k \mathbf{u}_k) = \nabla \cdot (\alpha_k k_k \nabla T_k) + \alpha_k \frac{Dp}{Dt} + Q_k + Q_{latent,k}}$$

#### Term-by-Term Breakdown

| Term | Mathematical | Physical Meaning | หน่วย (Unit) |
|------|--------------|------------------|--------------|
| **Unsteady** | $\frac{\partial(\alpha_k \rho_k h_k)}{\partial t}$ | Rate of enthalpy storage | J/(m³·s) |
| **Convection** | $\nabla \cdot (\alpha_k \rho_k h_k \mathbf{u}_k)$ | Enthalpy transported by flow | J/(m³·s) |
| **Diffusion** | $\nabla \cdot (\alpha_k k_k \nabla T_k)$ | Heat conduction (Fourier's law) | J/(m³·s) |
| **Pressure Work** | $\alpha_k \frac{Dp}{Dt}$ | Compression/expansion work | J/(m³·s) |
| **Interphase** | $Q_k$ | Heat transfer between phases | J/(m³·s) |
| **Phase Change** | $Q_{latent,k}$ | Latent heat from evaporation/condensation | J/(m³·s) |

#### Key Variables

| Symbol | Meaning | Typical Value |
|--------|---------|---------------|
| $\alpha_k$ | Volume fraction of phase k | 0 - 1 |
| $\rho_k$ | Density (kg/m³) | Water: 998, Air: 1.2 |
| $h_k$ | Specific enthalpy (J/kg) | Function of T |
| $k_k$ | Thermal conductivity (W/m·K) | Water: 0.6, Air: 0.026 |
| $\mathbf{u}_k$ | Phase velocity (m/s) | - |

---

## 3. Interphase Heat Transfer (Deep Dive)

### 3.1 What is Interphase Heat Transfer?

**Interphase Heat Transfer** เป็นกระบวนการแลกเปลี่ยนความร้อนระหว่างเฟสผ่าน interface ซึ่งเป็นเอกลักษณ์เฉพาะของระบบ multiphase

$$Q_k = \sum_{l \neq k} h_{kl} A_{kl} (T_l - T_k)$$

### 3.2 Why is Interphase Heat Transfer Critical?

**ทำไมต้องใส่ใจกับ interphase heat transfer?**

1. **Temperature equilibrium driving force** — phases มุ่งสู่ thermal equilibrium
2. **Dominant mechanism in dispersed flows** — bubbles/droplets มี surface area มาก
3. **Controls phase change rate** — heat transfer limits evaporation/condensation
4. **Affects flow stability** — thermal gradients สร้าง local buoyancy

### 3.3 How to Model Interphase Heat Transfer?

#### Core Components

| Component | Symbol | Physical Meaning | หน่วย |
|-----------|--------|------------------|--------|
| **Heat Transfer Coefficient** | $h_{kl}$ | Measure of heat transfer efficiency | W/(m²·K) |
| **Interfacial Area Density** | $A_{kl}$ | Contact area per unit volume | m²/m³ |
| **Temperature Difference** | $(T_l - T_k)$ | Driving force for heat transfer | K |

#### Heat Transfer Coefficient via Nusselt Number

$$h_{kl} = \frac{Nu_{kl} \cdot k_c}{d_p}$$

| Symbol | Meaning |
|--------|---------|
| $Nu_{kl}$ | Nusselt number (dimensionless heat transfer coefficient) |
| $k_c$ | Continuous phase thermal conductivity (W/m·K) |
| $d_p$ | Particle/droplet/bubble diameter (m) |

---

## 4. Heat Transfer Correlation Selection

### 4.1 What are Nusselt Number Correlations?

**Nusselt correlations** คือ empirical correlations ที่ใช้คำนวณ heat transfer coefficient โดยทั่วไปอยู่ในรูป:

$$Nu = f(Re, Pr, \text{geometry})$$

| Parameter | Definition | Physical Meaning |
|-----------|------------|------------------|
| **Re** | $\rho_c U_r d_p / \mu_c$ | Inertia vs viscous forces |
| **Pr** | $c_{p,c} \mu_c / k_c$ | Momentum vs thermal diffusivity |
| **U_r** | $\| \mathbf{u}_d - \mathbf{u}_c \|$ | Relative velocity |

### 4.2 Why Correlation Selection Matters?

**ผลกระทบจากการเลือก correlation ที่ไม่เหมาะสม:**

| Wrong Choice | Consequence |
|--------------|-------------|
| Under-predicted heat transfer | Temperature ไม่ equilibrium → phase change ผิดพลาด |
| Over-predicted heat transfer | Numerical instability, ทำนาย heat transfer เร็วเกินไป |
| Wrong regime application | Unphysical results |

### 4.3 Common Correlations — When to Use What?

#### Ranz-Marshall Correlation

**WHAT:**
$$Nu = 2 + 0.6 Re^{1/2} Pr^{1/3}$$

**WHEN TO USE:**
- Spherical particles/droplets
- Rigid spheres (ไม่มี internal circulation)
- **Re range:** 0 - 10⁴
- **Pr range:** 0.7 - 10⁴

**WHY THIS ONE:**
- Simple, widely validated
- Asymptotically correct: $Nu \to 2$ when $Re \to 0$ (conduction limit)

**Practical Examples:**
```
✓ Water droplets in air (spray drying)
✓ Solid particles in gas (fluidized bed)
✗ Bubbles with internal circulation
✗ Highly deformed droplets
```

---

#### Hughmark Correlation

**WHAT:**
$$Nu = 2 + 0.6 Re^{1/2} Pr^{1/3} \cdot f(Re, We)$$

**WHEN TO USE:**
- Bubble columns
- Gas-liquid systems
- Accounts for bubble deformation

**Practical Examples:**
```
✓ Air bubbles in water (bubble column)
✓ Gas injection in liquids
✗ Solid particles (use Ranz-Marshall instead)
```

---

#### Gunn Correlation

**WHAT:**
$$Nu = (7 - 10\alpha_c + 5\alpha_c^2)(1 + 0.7 Re^{0.2} Pr^{1/3}) + (1.33 - 2.4\alpha_c + 1.2\alpha_c^2) Re^{0.7} Pr^{1/3}$$

**WHEN TO USE:**
- Packed beds
- Fluidized beds (dense phase)
- High particle concentration

**Practical Examples:**
```
✓ Packed bed reactors
✓ Fluidized bed heat exchangers
✓ Porous media flows
✗ Dilute systems (use Ranz-Marshall)
```

---

#### Tomiyama Correlation (for Bubbles)

**WHAT:**
Accounts for bubble shape distortion via Eötvös number:

$$Nu = f(Re, Pr, Eo)$$

**WHEN TO USE:**
- Large, deformable bubbles
- contaminated systems

**Practical Examples:**
```
✓ Large bubbles in water (Eo > 5)
✓ Wastewater treatment
✗ Small, spherical bubbles
```

---

### 4.4 Correlation Selection Flowchart

```
                    Start
                      │
                      ▼
            ┌─────────────────────┐
            │  Dispersed Phase?   │
            └─────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        │                           │
        ▼                           ▼
  ┌──────────┐              ┌──────────────┐
  │  Bubbles?│              │  Particles?  │
  └──────────┘              └──────────────┘
        │                           │
   Small (< 2mm)              Spherical?
        │                    ┌─────┴─────┐
        ▼                    │           │
  ┌──────────┐            Yes          No
  │ Ranz-    │              │           │
  │ Marshall │              ▼           ▼
  └──────────┘        ┌─────────┐ ┌──────────┐
        │            │Ranz-    │ │  Gunn    │
        │            │Marshall │ └──────────┘
        ▼            └─────────┘
   Large (> 2mm)
        │
        ▼
  ┌──────────────┐
  │  Tomiyama    │
  │  / Hughmark  │
  └──────────────┘
```

---

## 5. Temperature vs Enthalpy Formulations

### 5.1 What's the Difference?

| Aspect | **Enthalpy Form** (Preferred) | **Temperature Form** |
|--------|------------------------------|----------------------|
| **Variable** | Specific enthalpy $h$ | Temperature $T$ |
| **Equation** | $\partial(\alpha \rho h)/\partial t + \dots$ | $\partial(\alpha \rho c_p T)/\partial t + \dots$ |
| **Phase Change** | Natural — $h$ includes latent heat | Complicated — need source terms |
| **Conservation** | Directly conserved | Not directly conserved |

### 5.2 Why Use Enthalpy Formulation?

**ข้อดีของ Enthalpy Formulation:**

1. **Conserved variable** — enthalpy เป็น conserved quantity (like mass, momentum)
2. **Phase change handled naturally** — latent heat  included in $h$ definition
3. **Consistent with thermodynamics** — $h = h(T, p)$
4. **OpenFOAM default** — most solvers use enthalpy

**ข้อเสียของ Temperature Formulation:**

1. **Non-conservative** — $c_p$ may vary with $T$
2. **Phase change requires explicit source** — must add $\dot{m} L$ separately
3. **Numerically less robust** — for phase change problems

### 5.3 When to Use Each Formulation?

| Scenario | Recommended Form | ทำไม? |
|----------|------------------|--------|
| **Phase change** (boiling, condensation) | **Enthalpy** | Latent heat รวมอยู่ใน $h$ แล้ว |
| **Single-phase, constant $c_p$** | Either | เหมือนกันทางคณิตศาสตร์ |
| **Highly compressible** | Enthalpy | Consistent with energy conservation |
| **Simple heat transfer** | Temperature | Easier to post-process |

---

## 6. Phase Change and Latent Heat

### 6.1 What is Phase Change in Energy Equation?

**Phase Change** (Evaporation/Condensation) เป็นกระบวนการที่ mass และ energy แลกเปลี่ยนระหว่างเฟสพร้อมกัน:

$$Q_{latent,k} = \sum_{l \neq k} \dot{m}_{lk} \cdot L_{lk}$$

### 6.2 Why Latent Heat Matters?

**ทำไม latent heat สำคัญ?**

1. **Huge energy effect** — $L_{water} \approx 2.26 \times 10^6$ J/kg (very large!)
2. **Controls phase change rate** — heat transfer ถูก消耗 ไปกับ latent heat
3. **Temperature pinning** — saturation temperature คงที่ระหว่าง phase change

**Practical Impact:**
```
Example: Evaporating 1 kg water
- Sensible heat (20°C → 100°C): ~335 kJ
- Latent heat (100°C water → 100°C vapor): 2260 kJ
→ Latent heat is ~6.8x larger!
```

### 6.3 How to Model Phase Change in OpenFOAM?

#### Latent Heat Source Term

The latent heat appears as source term in both phases:

| Phase | Source Term |
|-------|-------------|
| **Evaporating phase (liquid → gas)** | $-\dot{m}_{lg} \cdot L_{lg}$ (loses energy) |
| **Condensing phase (gas → liquid)** | $+\dot{m}_{gl} \cdot L_{gl}$ (gains energy) |

#### Saturation Temperature Model

```cpp
// constant/phaseProperties
saturationTemperatureModel
{
    // Option 1: Constant saturation temperature
    type    constantSaturationTemperature;
    value   373.15;  // Water boiling point [K]
    
    // Option 2: Antoine equation (T-dependent)
    // type    antoine;
    // A       8.07131;
    // B       1730.63;
    // C       233.426;
}
```

#### Latent Heat Definition

```cpp
// constant/phaseProperties
L
{
    // Constant latent heat
    type    constant;
    value   2260000;  // [J/kg] for water
}
```

---

## 7. OpenFOAM Implementation

### 7.1 Energy Equation in Code

#### Complete Enthalpy Equation

```cpp
// File: phaseSystem::EEqns()
// Location: applications/solvers/multiphase/reactingEulerFoam/

forAll(phases, phasei)
{
    phaseModel& phase = phases[phasei];
    volScalarField& h = phase.thermo().h();
    
    fvScalarMatrix EEqn
    (
        fvm::ddt(alpha, rho, h)                    // ∂(αρh)/∂t
      + fvm::div(alphaPhi, h)                      // ∇·(αρhU)
      - fvm::laplacian(alphaKappaEff, T)           // ∇·(αk∇T)
      + alpha*fvc::ddt(p)                          // αDp/Dt
      + alpha*(fvc::div(phi, fvc::absolute(phase.U(), p))) // Pressure work
      ==
       interphaseHeatTransfer[phasei]              // Q_k (interphase)
      + latentHeatTransfer[phasei]                 // Q_latent (phase change)
    );
    
    EEqn.relax();
    EEqn.solve();
}
```

#### Key Components Explained

| Code | Physical Term | Description |
|------|---------------|-------------|
| `fvm::ddt(alpha, rho, h)` | $\frac{\partial(\alpha \rho h)}{\partial t}$ | Unsteady term |
| `fvm::div(alphaPhi, h)` | $\nabla \cdot (\alpha \rho h \mathbf{u})$ | Convection |
| `fvm::laplacian(alphaKappaEff, T)` | $\nabla \cdot (\alpha k \nabla T)$ | Conduction |
| `alpha*fvc::ddt(p)` | $\alpha \frac{Dp}{Dt}$ | Pressure work |
| `interphaseHeatTransfer[phasei]` | $Q_k$ | Interphase heat transfer |

---

### 7.2 Interphase Heat Transfer Model

```cpp
// Location: src/phaseSystemModels/lagrangian/interphaseHeatTransferModel/

// Ranz-Marshall correlation
template<class PhaseType>
void RanzMarshall<PhaseType>::calculate()
{
    const PhaseType& dispersedPhase = dispersedPhase_;
    const PhaseType& continuousPhase = continuousPhase_;
    
    // Nusselt number
    volScalarField Re = dispersedPhase.Reynolds();
    volScalarField Pr = continuousPhase.Prandtl();
    
    volScalarField Nu = 2.0 + 0.6*sqrt(Re)*cbrt(Pr);
    
    // Heat transfer coefficient
    htc_ = Nu * continuousPhase.kappa() / dispersedPhase.d();
    
    // Interfacial area
    volScalarField Ai = 6.0 * alpha_d / dispersedPhase.d();
    
    // Heat transfer rate [W/m³]
    Q_ = htc_ * Ai * (continuousPhase.T() - dispersedPhase.T());
}
```

---

### 7.3 Thermophysical Properties Setup

#### Water Phase (Liquid)

```cpp
// constant/thermophysicalProperties.water

thermoType
{
    type            heRhoThermo;           // Enthalpy-based thermo
    mixture         pureMixture;           // Single component
    transport       const;                 // Constant transport properties
    thermo          hConst;                // Constant specific heat
    equationOfState rhoConst;              // Constant density
    specie          specie;
    energy          sensibleEnthalpy;     // ← Use enthalpy!
}

mixture
{
    specie
    {
        molWeight       18.02;             // [kg/kmol]
    }
    
    thermodynamics
    {
        Cp              4180;              // [J/kg/K] Specific heat
        Hf              0;                 // [J/kg] Enthalpy of formation
    }
    
    transport
    {
        mu              0.001;             // [Pa·s] Dynamic viscosity
        Pr              6.99;              // Prandtl number
        kappa           0.6;               // [W/m/K] Thermal conductivity
    }
}
```

#### Air Phase (Gas)

```cpp
// constant/thermophysicalProperties.air

thermoType
{
    type            heRhoThermo;
    mixture         pureMixture;
    transport       const;
    thermo          hConst;
    equationOfState perfectGas;            // ← Compressible!
    specie          specie;
    energy          sensibleEnthalpy;
}

mixture
{
    specie
    {
        molWeight       28.96;
    }
    
    thermodynamics
    {
        Cp              1005;              // [J/kg/K]
        Hf              0;
    }
    
    transport
    {
        mu              1.8e-5;
        Pr              0.71;
        kappa           0.026;
    }
}
```

---

### 7.4 Latent Heat Configuration

```cpp
// constant/phaseProperties (for twoPhaseReactingEulerFoam)

phases
(
    water
    {
        ...
    }
    
    air
    {
        ...
    }
);

// Phase change model
phaseChange
{
    type    evaporationCondensation;
    
    // Mass transfer model
    massTransfer
    {
        type    constant;                  // Or: frozen, SchillerNaumann
        value   0.1;                       // [s⁻¹] Mass transfer coefficient
    }
    
    // Saturation temperature
    saturationTemperatureModel
    {
        type    constantSaturationTemperature;
        value   373.15;                    // [K]
    }
    
    // Latent heat
    L
    {
        type    constant;
        value   2260000;                   // [J/kg]
    }
}
```

---

## 8. Boundary Conditions

### 8.1 Temperature Boundary Conditions

#### Fixed Temperature (Dirichlet)

```cpp
T.water
{
    type            fixedValue;
    value           uniform 300;            // [K] Constant wall temperature
}
```

**Use cases:**
- Isothermal walls
- Inlet temperature
- Phase change boundaries

---

#### Heat Flux (Neumann)

```cpp
T.water
{
    type            fixedGradient;
    gradient        uniform 1000;           // [K/m] → q = -k∇T
}
```

**Use cases:**
- Constant heat flux walls
- Insulated walls (gradient = 0)
- Known heat transfer rate

**Example: Heat flux calculation**
```
For water with k = 0.6 W/m·K:
gradient = 1000 K/m → q = 0.6 × 1000 = 600 W/m²
```

---

#### Adiabatic (Insulated)

```cpp
T.water
{
    type            zeroGradient;           // No heat flux
}
```

**Use cases:**
- Insulated walls
- Symmetry planes
- Outlet boundaries

---

#### Convective Boundary (Robin)

```cpp
T.water
{
    type            externalWallHeatFlux;
    mode            coefficient;
    h               10;                     // [W/m²/K] HTC
    Ta              uniform 293;            // [K] Ambient temperature
}
```

**Use cases:**
- Natural convection to ambient
- Forced convection cooling
- Realistic wall conditions

---

### 8.2 Common Pitfalls in BC Setup

| Pitfall | Symptom | Solution |
|---------|---------|----------|
| Inconsistent BCs between phases | Non-physical temperature jump | Ensure $T_{water}$ and $T_{air}$ BCs at wall are compatible |
| Wrong gradient sign | Wrong heat flux direction | Remember: flux = -k∇T (negative gradient) |
| Zero gradient at inlet | Backflow issues | Use `inletOutlet` or `zeroGradient` with caution |
| Fixed temperature at outlet | Reflection of waves | Use `zeroGradient` for convective outlet |

---

## 9. Practical Examples

### 9.1 Example 1: Heat Transfer in Bubble Column

**Scenario:** Air bubbles rising in heated water

```
Geometry:      Cylindrical column, H = 2 m, D = 0.5 m
Phases:        Air (dispersed), Water (continuous)
Heat input:    5 kW from bottom wall
Goal:          Predict temperature distribution
```

**Correlation Selection:**
- Use **Hughmark** or **Tomiyama** correlation (deformable bubbles)
- Interfacial area: $A = 6\alpha_g / d_b$ with $d_b = 5$ mm

**Key Settings:**
```cpp
// constant/phaseProperties
heatTransferModel
{
    type    heatTransferModel;
    phases  (air water);
    
    air
    {
        type    Hughmark;
        Pr      0.71;
    }
}
```

---

### 9.2 Example 2: Condensing Steam in Shell-and-Tube

**Scenario:** Steam condensing on cold tubes

```
Geometry:      Shell-and-tube heat exchanger
Phases:        Steam (gas), Water (liquid film)
Wall T:        300 K
Steam T:       373 K (saturation)
Goal:          Predict condensation rate
```

**Key Physics:**
- Latent heat: $L = 2.26 \times 10^6$ J/kg
- Interphase heat transfer drives condensation
- Must include phase change model

**Configuration:**
```cpp
phaseChange
{
    type    evaporationCondensation;
    saturationTemperatureModel
    {
        type    constantSaturationTemperature;
        value   373.15;
    }
    L
    {
        type    constant;
        value   2260000;
    }
}
```

---

### 9.3 Example 3: Fluidized Bed Reactor

**Scenario:** Catalytic particles in gas stream

```
Geometry:      Cylindrical reactor
Phases:        Solid particles (dispersed), Gas (continuous)
Particle size: 100 μm
Solid volume fraction: 0.3 - 0.5
Goal:          Predict temperature field
```

**Correlation Selection:**
- Use **Gunn correlation** (dense particle system)
- Account for volume fraction effects

---

## 10. Common Pitfalls and Debugging

### 10.1 Numerical Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| **Temperature oscillations** | Too large time step | Reduce time step, use under-relaxation |
| **Non-convergence** | Strong coupling between phases | Use coupled solver, multiple outer iterations |
| **Negative temperature** | Large heat source, poor mesh | Refine mesh, limit heat transfer rate |
| **Temperature jump at interface** | Inconsistent thermodynamics | Check thermophysical properties consistency |

### 10.2 Physical Modeling Mistakes

| Mistake | Consequence | How to Detect |
|---------|-------------|---------------|
| **Wrong correlation** | Incorrect heat transfer rate | Compare with experimental data |
| **Ignoring latent heat** | Wrong phase change rate | Check energy balance |
| **Inconsistent BCs** | Non-physical results | Verify BCs at all boundaries |
| **Wrong saturation T** | No/incorrect phase change | Check saturation model setup |

### 10.3 Debugging Checklist

```
□ Thermophysical properties set for ALL phases?
□ Energy equation enabled in solver?
□ Interfacial area calculated correctly?
□ Nusselt correlation appropriate for flow regime?
□ Boundary conditions consistent across phases?
□ Latent heat included for phase change cases?
□ Time step satisfies: Δt < (ρcp/ k)·(Δx²) ?
□ Mesh refined near walls for heat transfer?
```

---

## 11. Quick Reference

### 11.1 Equation Summary

| Component | Equation | Notes |
|-----------|----------|-------|
| **Full energy eq.** | $\frac{\partial(\alpha_k \rho_k h_k)}{\partial t} + \nabla \cdot (\alpha_k \rho_k h_k \mathbf{u}_k) = \nabla \cdot (\alpha_k k_k \nabla T_k) + \alpha_k \frac{Dp}{Dt} + Q_k$ | Enthalpy form |
| **Interphase transfer** | $Q_k = \sum_{l \neq k} h_{kl} A_{kl} (T_l - T_k)$ | Sum over all phases |
| **Nusselt number** | $Nu = h d_p / k_c$ | Definition |
| **Ranz-Marshall** | $Nu = 2 + 0.6 Re^{1/2} Pr^{1/3}$ | Spherical particles |
| **Latent heat** | $Q_{latent} = \dot{m}_{lk} L_{lk}$ | Phase change source |

---

### 11.2 Common Heat Transfer Correlations

| Correlation | Formula | Use Case | Re Range |
|-------------|---------|----------|----------|
| **Ranz-Marshall** | $Nu = 2 + 0.6 Re^{1/2} Pr^{1/3}$ | Spherical particles | 0 - 10⁴ |
| **Hughmark** | $Nu = f(Re, Pr, We)$ | Bubbles, columns | 0 - 10⁴ |
| **Gunn** | $Nu = f(Re, Pr, \alpha)$ | Packed beds | 0 - 10⁵ |
| **Tomiyama** | $Nu = f(Re, Pr, Eo)$ | Deformable bubbles | > 0 |

---

### 11.3 OpenFOAM Commands

```bash
# Check thermophysical properties
cat constant/thermophysicalProperties.water

# Verify phase change settings
cat constant/phaseProperties

# Monitor temperature during simulation
postProcess -func "sampleDict" -latestTime

# Plot temperature distribution
paraFoam -builtin
```

---

## Key Takeaways

**บทสรุปสำคัญ (Key Takeaways):**

1. **Each phase has its own energy equation** — coupled through interphase heat transfer
2. **Enthalpy formulation is preferred** — especially for phase change problems (natural latent heat inclusion)
3. **Interphase heat transfer ∝ area** — bubble/droplet size สำคัญมากต่อ heat transfer efficiency
4. **Correlation selection matters** — Ranz-Marshall (spheres), Hughmark (bubbles), Gunn (packed beds)
5. **Latent heat dominates phase change** — $L_{water} \approx 2260$ kJ/kg (≈7x sensible heat!)
6. **Boundary conditions must be consistent** — ตรวจสอบ BCs ของทุก phase ที่ walls/interfaces
7. **Nusselt number correlations are empirical** — validate with experimental data when possible

---

## Concept Check

<details>
<summary><b>1. ทำไม enthalpy formulation ถูกนิยมกว่า temperature formulation?</b></summary>

**Because:**
- Enthalpy เป็น **conserved variable** (เหมือน mass, momentum)
- **Latent heat รวมอยู่ใน enthalpy** แล้ว → phase change ได้自然 (natural)
- Temperature formulation ต้องเพิ่ม source term สำหรับ phase change แยก
- **OpenFOAM default** — most multiphase solvers ใช้ enthalpy

</details>

<details>
<summary><b>2. Ranz-Marshall correlation ให้ Nu = 2 เมื่อไหร่ และทำไม?</b></summary>

**เมื่อ Re → 0** (no relative velocity between phases)

**Why?**
- เป็น **conduction-only limit** — sphere ใน stagnant fluid
- Analytical solution สำหรับ steady-state conduction จาก sphere: $Nu = 2$
- แสดงว่า correlation นี้ **physically consistent** (asymptotically correct)

</details>

<details>
<summary><b>3. Interfacial area density สำคัญอย่างไรต่อ heat transfer?</b></summary>

**เพราะ Heat transfer ∝ interfacial area:**

$$Q_{kl} = h_{kl} A_{kl} (T_l - T_k)$$

**Impact:**
- **Smaller bubbles → larger area/volume** → heat transfer ดีขึ้น
- Example: bubble diameter ลดครึ่ง → area เพิ่ม 2 เท่า (สำหรับ volume เท่ากัน)
- **Coalescence** (bubbles รวมตัว) → area ลด → heat transfer แย่ลง
- ต้องระมัดระวังใน systems ที่มี bubble coalescence/breakup

</details>

<details>
<summary><b>4. ทำไม latent heat ของ water สูงมากและส่งผลอย่างไร?</b></summary>

**Latent heat of vaporization (water at 1 atm):**
- $L \approx 2260$ kJ/kg

**Comparison:**
- Sensible heat: 20°C → 100°C: $\Delta h \approx 335$ kJ/kg
- **Latent heat ≈ 6.8x larger!**

**Consequences:**
1. **Phase change dominates energy balance** — ไม่สามารถมองข้ามได้
2. **Temperature pinning** — อุณหภูมิคงที่ตรง saturation จนกว่า phase change เสร็จ
3. **Heat transfer limits evaporation rate** — ไม่ใช่ mass transfer
4. **Simulation requires small time steps** — เนื่องจาก large energy changes

</details>

<details>
<summary><b>5. เมื่อไหร่ควรใช้ Gunn correlation แทน Ranz-Marshall?</b></summary>

**Use Gunn when:**
- **Dense particle systems** — packed beds, fluidized beds
- **High volume fraction** — $\alpha_s > 0.3$
- **Particle-particle interactions** สำคัญ

**Use Ranz-Marshall when:**
- **Dilute systems** — $\alpha_d < 0.1$
- **Isolated particles** — no interaction effects
- **Spherical, rigid particles**

**Key difference:** Gunn accounts for **volume fraction effects** (flow around closely packed particles)

</details>

---

## Related Documents

### In This Module

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Mass Conservation:** [01_Mass_Conservation.md](01_Mass_Conservation.md)
- **Momentum Conservation:** [02_Momentum_Conservation.md)

### Cross-Module

- **Heat Transfer:** [04_HEAT_TRANSFER](../../MODULE_03_SINGLE_PHASE_FLOW/CONTENT/04_HEAT_TRANSFER/00_Overview.md)
- **Phase Change Models:** [02_VOF_METHOD](../02_VOF_METHOD/00_Overview.md)
- **Interphase Forces:** [04_INTERPHASE_FORCES](../04_INTERPHASE_FORCES/01_DRAG/00_Overview.md)

### Solver Documentation

- `reactingEulerFoam` — Reacting multiphase with heat transfer
- `twoPhaseEulerFoam` — Non-reacting with heat transfer
- `interPhaseChangeFoam` — VOF with phase change

---

**Last Updated:** 2025-12-30  
**OpenFOAM Version:** v9+  
**Author:** OpenFOAM Multiphase Flow Documentation Team