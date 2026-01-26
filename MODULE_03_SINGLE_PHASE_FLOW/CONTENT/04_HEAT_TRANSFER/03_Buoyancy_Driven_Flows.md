# Buoyancy-Driven Flows

Natural Convection และ Boussinesq Approximation

---

## Learning Objectives

After completing this section, you should be able to:

- **WHAT:** Define buoyancy-driven flows and explain when they occur
- **WHY:** Recognize physical scenarios where natural convection dominates forced convection
- **HOW:** Configure OpenFOAM solvers for buoyancy-driven flows using the Boussinesq approximation
- Select appropriate solvers based on temperature differences and flow regimes
- Apply dimensionless numbers (Ra, Gr, Pr) to classify flow behavior
- Implement proper numerical schemes for stable temperature-convection coupling

---

## Overview

### WHAT: Buoyancy-Driven Flow Definition

**Buoyancy-Driven Flow** (Natural Convection) เกิดจากความแตกต่างของอุณหภูมิ → ความแตกต่างของความหนาแน่น → แรงลอยตัวจากแรงโน้มถ่วง

Key characteristics:
- No external fan or pump required
- Driven by density variations due to temperature gradients
- Coupling between momentum and energy equations

### WHY: Physical Importance

Natural convection dominates in many engineering applications:
- **Building ventilation:** Warm air rising, creating natural circulation
- **Electronics cooling:** Heat sinks with natural convection fins
- **Solar collectors:** Buoyancy-driven flow in absorber channels
- **Fire safety:** Smoke movement in buildings
- **Geothermal systems:** Natural circulation in geothermal reservoirs

### HOW: OpenFOAM Solver Selection

| Solver | Type | Use Case | Key Feature |
|--------|------|----------|-------------|
| `buoyantBoussinesqSimpleFoam` | Steady-state |1$\Delta T < 30°C1| Boussinesq approximation, SIMPLE algorithm |
| `buoyantBoussinesqPimpleFoam` | Transient |1$\Delta T < 30°C$, time-dependent | Boussinesq, PIMPLE algorithm |
| `buoyantSimpleFoam` | Steady-state | Large1$\Delta T$, compressible | Full compressible formulation |
| `buoyantPimpleFoam` | Transient | Fire, large1$\Delta T1| Compressible, ideal gas law |

**Decision Guide:**
- Small1$\Delta T1(< 30°C for air) → Boussinesq solvers (faster, simpler)
- Large1$\Delta T1(> 50°C) → Full compressible solvers (more accurate)
- Steady state desired → `SimpleFoam` variants
- Time evolution important → `PimpleFoam` variants

---

## 1. Boussinesq Approximation: WHAT, WHY, HOW

### WHAT: Mathematical Formulation

ถือว่า1$\rho = \text{constant}1ทุกที่ **ยกเว้น** ในเทอมแรงลอยตัว:

**Density Variation:**
$$\rho = \rho_0 [1 - \beta(T - T_0)]$$

**Buoyancy Force Term:**
$$\mathbf{F}_b = \rho_0 \mathbf{g} \beta (T - T_0)$$

Where:
-1$\rho_01= reference density [kg/m³]
-1$\beta1= thermal expansion coefficient [1/K]
-1$T_01= reference temperature [K]
-1$\mathbf{g}1= gravitational acceleration [m/s²]

### WHY: Validity and Approximation Error

**When to Use:**
-1$\beta \Delta T \ll 11(typically1$\beta \Delta T < 0.1$)
-1$\Delta T < 30°C1for air
-1$\Delta T < 5°C1for water
- Flow speeds small compared to speed of sound

**Why It Works:**
The Boussinesq approximation exploits the fact that density differences are small enough to neglect inertia terms but large enough to drive buoyancy. This dramatically simplifies the equations while maintaining physical accuracy for natural convection.

**Physical Intuition:**
Think of hot air rising. The air expands slightly (density decreases ~3% per 10°C for air), creating a buoyancy force. However, the air's inertia (mass × acceleration) hardly changes because the density change is so small.

### HOW: Implementation in OpenFOAM

**Derivation in Momentum Equation:**

Starting from the general momentum equation with gravity:
$$\frac{\partial (\rho \mathbf{U})}{\partial t} + \nabla \cdot (\rho \mathbf{U} \mathbf{U}) = -\nabla p + \mu \nabla^2 \mathbf{U} + \rho \mathbf{g}$$

Applying Boussinesq ($\rho \approx \rho_01everywhere except in1$\rho \mathbf{g}$):
$$\rho_0 \left[ \frac{\partial \mathbf{U}}{\partial t} + \nabla \cdot (\mathbf{U} \mathbf{U}) \right] = -\nabla p + \mu \nabla^2 \mathbf{U} + \rho_0 [1 - \beta(T - T_0)] \mathbf{g}$$

Rearranging with modified pressure ($p^* = p - \rho_0 \mathbf{g} \cdot \mathbf{x}$):
$$\frac{\partial \mathbf{U}}{\partial t} + \nabla \cdot (\mathbf{U} \mathbf{U}) = -\nabla p^* + \nu \nabla^2 \mathbf{U} - \mathbf{g} \beta (T - T_0)$$

**Source Code Implementation:**

```cpp
// createFields.H (buoyantBoussinesqSimpleFoam)
volScalarField rhok
(
    IOobject
    (
        "rhok",
        runTime.timeName(),
        mesh,
        IOobject::NO_READ,
        IOobject::AUTO_WRITE
    ),
    mesh,
    dimless,
    calculatedFvPatchScalarField::typeName
);

// Normalized density: ρ/ρ₀ = 1 - β(T - T₀)
rhok = 1.0 - beta * (T - TRef);

// UEqn.H - Momentum Equation
fvVectorMatrix UEqn
(
    fvm::ddt(U)
  + fvm::div(phi, U)
  - fvm::laplacian(nu, U)
 ==
    rhok * g    // Buoyancy source term: (1 - βΔT)g
);
```

---

## 2. Dimensionless Numbers: Flow Regime Classification

### WHAT: Key Dimensionless Groups

**Rayleigh Number (Ra):**
$$Ra = \frac{g \beta \Delta T L^3}{\nu \alpha} = \frac{\text{Buoyancy Forces}}{\text{Viscous Forces} \times \text{Thermal Diffusion}}$$

- Characterizes the ratio of buoyancy to viscous/thermal dissipation
- **Most important parameter** for natural convection

**Grashof Number (Gr):**
$$Gr = \frac{g \beta \Delta T L^3}{\nu^2} = \frac{\text{Buoyancy Forces}}{\text{Viscous Forces}^2}$$

- Ratio of buoyancy to viscous forces
- Related to Rayleigh number:1$Ra = Gr \cdot Pr$

**Prandtl Number (Pr):**
$$Pr = \frac{\nu}{\alpha} = \frac{\text{Momentum Diffusivity}}{\text{Thermal Diffusivity}}$$

- Fluid property (geometry-independent)
- Compares velocity boundary layer to thermal boundary layer

| Fluid | Temperature |1$\nu1[m²/s] |1$\alpha1[m²/s] | Pr |
|-------|-------------|--------------|-----------------|-----|
| Air | 20°C |1$1.5 \times 10^{-5}1|1$2.1 \times 10^{-5}1| 0.71 |
| Water | 20°C |1$1.0 \times 10^{-6}1|1$1.4 \times 10^{-7}1| 7.0 |
| Engine Oil | 20°C |1$1.0 \times 10^{-4}1|1$9.0 \times 10^{-8}1| ~1100 |

### WHY: Physical Significance

**Rayleigh Number Regimes:**

|1$Ra1Range | Flow Regime | Physical Characteristics | Heat Transfer |
|------------|-------------|--------------------------|---------------|
|1$< 10^31| **Conduction dominant** | Minimal fluid motion |1$Nu \approx 11(pure conduction) |
|1$10^3 - 10^91| **Laminar convection** | Steady, organized circulation patterns |1$Nu \propto Ra^{1/4}1|
|1$> 10^91| **Turbulent convection** | Unsteady, chaotic, mixing dominates |1$Nu \propto Ra^{1/3}1|

**Why1$Ra = 10^91is Critical:**
This marks the transition to turbulence where:
- Boundary layers become unstable
- Time-averaged statistics become meaningful
- Turbulence models become necessary
- Heat transfer enhancement increases

### HOW: Application to Simulation Design

**Decision Tree:**

```
Calculate Ra for your geometry
         ↓
    Ra < 10³?
    ─────┬─────
    YES │    NO
        │     ↓
        │  Ra < 10⁹?
        │  ───┬───
        │ YES│  NO
        │    │   ↓
        │    │  Turbulent
        │    │  - Use RANS/LES
        │    │  - Refine wall mesh
        │    │  - y⁺ ≈ 30-300
        │    ↓
    Laminar
    - Coarser mesh OK
    - Direct simulation
```

**Example Calculation:**

Vertical plate,1$L = 0.31m,1$\Delta T = 201K, air at 20°C:

$$Ra = \frac{(9.81)(3.0 \times 10^{-3})(20)(0.3)^3}{(1.5 \times 10^{-5})(2.1 \times 10^{-5})}$$
$$Ra = \frac{0.0159}{3.15 \times 10^{-10}} \approx 5.0 \times 10^7$$

→ **Laminar regime** ($10^3 < Ra < 10^9$)

---

## 3. OpenFOAM Case Setup: Implementation Details

### WHAT: Required Files and Structure

```
buoyancyCase/
├── 0/
│   ├── p           # Pressure (modified pressure p*)
│   ├── U           # Velocity
│   └── T           # Temperature
├── constant/
│   ├── g           # Gravitational acceleration
│   ├── transportProperties  # ν, β, Prt
│   └── thermophysicalProperties  # (for compressible solvers)
└── system/
    ├── fvSchemes
    └── fvSolution
```

### HOW: Configuration Files

**constant/g - Gravitational Acceleration**

```cpp
dimensions      [0 1 -2 0 0 0 0];
value           (0 0 -9.81);  // Negative z-direction
```

**Why:** Defines direction and magnitude of gravity. The buoyancy force opposes this direction when1$T > T_{ref}$.

**constant/transportProperties - Boussinesq Parameters**

```cpp
transportModel  Newtonian;

nu      [0 2 -1 0 0 0 0]  1.5e-05;  // Kinematic viscosity [m²/s]
beta    [0 0 0 -1 0 0 0]  3.0e-03;  // Thermal expansion [1/K]
Prt     [0 0 0 0 0 0 0]   0.9;      // Turbulent Prandtl number
```

**Thermal Expansion Coefficients:**

| Fluid | Temperature |1$\beta1[1/K] |
|-------|-------------|---------------|
| Air | 20°C |1$3.0 \times 10^{-3}1|
| Water | 20°C |1$2.1 \times 10^{-4}1|
| Water | 80°C |1$6.3 \times 10^{-4}1|

**Why These Values Matter:**
- **$\nu$**: Controls viscous damping and boundary layer thickness
- **$\beta$**: Directly scales buoyancy force magnitude
- **$Prt$**: Relates turbulent momentum and heat transfer (0.9 for air)

---

## 4. Numerical Settings: Stability and Convergence

### WHAT: Schemes and Solvers

**system/fvSchemes - Discretization**

```cpp
gradSchemes
{
    default         Gauss linear;
}

divSchemes
{
    div(phi,U)  bounded Gauss limitedLinearV 1;
    div(phi,T)  bounded Gauss limitedLinear 1;  // bounded สำคัญ!
    div(phi,k)  bounded Gauss limitedLinear 1;
    div(phi,epsilon) bounded Gauss limitedLinear 1;
}

laplacianSchemes
{
    default         Gauss linear corrected;
}
```

**WHY `bounded` Scheme for Temperature:**
1. **Prevents unphysical values:** Temperature oscillations can create1$T < 01K or1$T > 10^61K
2. **Ensures stability:** Bounded schemes guarantee solution stays within bounds
3. **Maintains energy balance:** Non-physical temperatures corrupt buoyancy force

**HOW Relaxation Affects Convergence:**

```cpp
// system/fvSolution
SIMPLE
{
    nNonOrthogonalCorrectors 1;
    
    residualControl
    {
        p       1e-4;
        U       1e-4;
        T       1e-4;      // Tight tolerance for temperature
        epsilon 1e-4;
    }
}

relaxationFactors
{
    fields
    {
        p       0.3;       // Pressure: under-relaxation for stability
    }
    equations
    {
        U       0.7;       // Velocity: moderate relaxation
        T       0.5;       // Temperature: lower for strong coupling
        k       0.7;
        epsilon 0.7;
    }
}
```

**Why1$T1Relaxation = 0.5:**
- Temperature and velocity are **strongly coupled** through buoyancy
- Low relaxation prevents oscillation between momentum and energy equations
- Trade-off: slower convergence per iteration, but more stable

---

## 5. Boundary Conditions: Practical Examples

### WHAT: Common Configurations

**Hot Vertical Wall (Left):**

```cpp
// 0/T
leftWall
{
    type            fixedValue;
    value           uniform 350;  // Hot wall [K]
}

// 0/U
leftWall
{
    type            noSlip;
}
```

**Cold Vertical Wall (Right):**

```cpp
// 0/T
rightWall
{
    type            fixedValue;
    value           uniform 300;  // Cold wall [K]
}
```

**Adiabatic (Insulated) Walls:**

```cpp
// 0/T - Zero heat flux
topWall
{
    type            zeroGradient;  // ∂T/∂n = 0
}

bottomWall
{
    type            zeroGradient;
}
```

**Pressure Boundary Conditions:**

```cpp
// 0/p - Modified pressure (p* = p - ρ₀g·x)
// For closed cavity:
allWalls
{
    type            fixedFluxPressure;
    gradient        uniform 0;
}

// For open boundaries:
inlet
{
    type            totalPressure;  // p₀ = p + ½ρ|U|²
    p0              uniform 0;
    value           uniform 0;
}
```

### WHY: BC Selection

**Fixed Temperature Walls:**
- Drives buoyancy force directly
- Used for heated/cooled surfaces
- Strong coupling with momentum equation

**Adiabatic Walls:**
- No heat transfer through boundary
- Represents insulated surfaces
- Temperature gradient = 0 at wall

**Fixed Flux Walls:**

```cpp
heatedWall
{
    type            externalWallHeatFlux;
    q               uniform 1000;  // Heat flux [W/m²]
    mode            coefficient;
}
```

- Prescribed heat transfer rate
- Common in electronics cooling
- Temperature adjusts to achieve flux

---

## 6. Post-Processing: Analysis and Validation

### WHAT: Nusselt Number Calculation

**Definition:**
$$Nu = \frac{h L}{k} = \frac{q'' L}{k \Delta T}$$

Where:
-1$h1= convective heat transfer coefficient [W/(m²·K)]
-1$L1= characteristic length [m]
-1$k1= thermal conductivity [W/(m·K)]
-1$q''1= wall heat flux [W/m²]

**Physical Meaning:**
-1$Nu = 1$: Pure conduction (no convection enhancement)
-1$Nu > 1$: Convection enhances heat transfer
- Typical values:1$Nu \sim 10-10001depending on1$Ra$

### HOW: OpenFOAM Implementation

**wallHeatFlux Function Object:**

```cpp
// system/controlDict
functions
{
    wallHeatFlux
    {
        type            wallHeatFlux;
        libs            ("libfieldFunctionObjects.so");
        
        patches         (hotWall coldWall);
        writeControl    timeStep;
        writeInterval   10;
        
        // Output: wallHeatFlux, wallHeatFluxTopo
    }
    
    nusseltNumber
    {
        type            surfaceRegion;
        libs            ("libsampling.so");
        
        operation       average;
        surfaceFormat   none;
        
        // Calculate Nu from wallHeatFlux
        fields          (wallHeatFlux);
    }
}
```

**Manual Calculation (paraFoam):**

```python
# Python Calculator in ParaView
# For hot wall at T_hot, cold at T_cold, length L:
q_wall = wallHeatFlux_hot  # W/m²
k_fluid = 0.026            # Thermal conductivity of air [W/(m·K)]
dT = T_hot - T_cold        # [K]
L = 0.3                    # Characteristic length [m]

Nu_local = q_wall * L / (k_fluid * dT)
```

### WHY: Validation with Correlations

**Theoretical Correlations:**

| Configuration | Rayleigh Range | Correlation | Notes |
|---------------|----------------|-------------|-------|
| Vertical plate (laminar) |1$10^4 < Ra < 10^91|1$Nu = 0.59 Ra^{1/4}1| Average Nu |
| Vertical plate (turbulent) |1$10^9 < Ra < 10^{13}1|1$Nu = 0.10 Ra^{1/3}1| Local independent of x |
| Horizontal plate (hot facing up) |1$10^5 < Ra < 10^71|1$Nu = 0.54 Ra^{1/4}1| Upper surface |
| Horizontal plate (hot facing down) |1$10^5 < Ra < 10^{10}1|1$Nu = 0.27 Ra^{1/4}1| Lower surface |
| Enclosed cavity |1$10^3 < Ra < 10^91|1$Nu = 0.18 Ra^{1/4}1| Aspect ratio ≈ 1 |

**Comparison Procedure:**

1. Calculate1$Ra1from simulation parameters
2. Compute theoretical1$Nu1from correlation
3. Extract1$Nu1from OpenFOAM results
4. Compare:1$\frac{|Nu_{CFD} - Nu_{corr}|}{Nu_{corr}} < 10\%1→ Good agreement

---

## 7. Troubleshooting: Common Issues and Solutions

### Issue 1: Solution Divergence

**Symptoms:**
- Residuals increase exponentially
- Temperature values become unrealistic ($T < 01K or1$T > 10^61K)

**Causes & Solutions:**

| Cause | Solution |
|-------|----------|
| Time step too large | Reduce `deltaT` by factor of 2-10 |
| Insufficient under-relaxation | Lower relaxation factors (T to 0.3) |
| Missing `bounded` scheme | Add `bounded` to all `div(phi,T)` terms |
| Poor mesh quality | Check non-orthogonality, skewness |

**Diagnosis Code:**
```cpp
// system/fvSolution - Add for debugging
SIMPLE
{
    residualControl
    {
        p       1e-4;
        U       1e-4;
        T       1e-4;
        k       1e-4;
        epsilon 1e-4;
    }
    
    // Detect oscillation
    nNonOrthogonalCorrectors 2;  // Increase for bad meshes
}
```

### Issue 2: No Convection Observed

**Symptoms:**
- Velocity field remains nearly zero
- Heat transfer appears conduction-dominated ($Nu \approx 1$)
- Temperature contours show linear gradient

**Causes & Solutions:**

| Cause | Diagnosis | Solution |
|-------|-----------|----------|
| Gravity direction wrong | Check `constant/g` | Verify direction opposes buoyancy |
|1$\beta1too small | Check units | Should be1$O(10^{-3})1for air |
|1$\Delta T1too small | Calculate1$Ra1| May need larger1$\Delta T1|
| Wrong solver | Check solver type | Ensure using buoyancy solver |

**Verification:**
```bash
# Check gravity
cat constant/g

# Check beta
grep "beta" constant/transportProperties

# Calculate expected Ra
# Ra = g·β·ΔT·L³/(ν·α)
# Should be > 10³ for observable convection
```

### Issue 3: Slow Convergence

**Symptoms:**
- Residuals plateau at1$10^{-2}1to1$10^{-3}$
- Solution oscillates between iterations

**Solutions:**

```cpp
// system/fvSolution - Optimize relaxation
relaxationFactors
{
    fields    { p 0.2; }      // Lower pressure relaxation
    equations { U 0.5; T 0.3; }  // Lower equation relaxation
}

// Use tighter residual control
SIMPLE
{
    residualControl
    {
        p       1e-5;  // Tighter tolerance
        U       1e-5;
        T       1e-6;  // Tightest for T
    }
}
```

**Advanced:**
- Use `solver GAMG` for pressure
- Increase mesh resolution in boundary layers
- Run transient simulation even if steady state desired

---

## Key Takeaways

### Boussinesq Approximation

✅ **Use When:**
-1$\Delta T < 30°C1(air) or1$\Delta T < 5°C1(water)
- Flow speeds << speed of sound
- Small density variations ($\beta \Delta T < 0.1$)

❌ **Avoid When:**
- Large temperature differences
- Compressibility effects important
- Variable property fluids required

### Flow Regime Decision Tree

```
Calculate Ra = g·β·ΔT·L³/(ν·α)
    ↓
    Ra < 10³ → Pure conduction (Nu ≈ 1)
    ↓
10³ < Ra < 10⁹ → Laminar natural convection
    - Coarse mesh acceptable
    - No turbulence model
    - Use correlations: Nu ∝ Ra^(1/4)
    ↓
    Ra > 10⁹ → Turbulent natural convection
    - Refine mesh (y⁺ ≈ 30-300)
    - RANS turbulence model required
    - Use correlations: Nu ∝ Ra^(1/3)
```

### Solver Selection Matrix

|1$\Delta T1| Steady | Transient |
|------------|--------|-----------|
| Small (< 30°C) | `buoyantBoussinesqSimpleFoam` | `buoyantBoussinesqPimpleFoam` |
| Large (> 50°C) | `buoyantSimpleFoam` | `buoyantPimpleFoam` |

### Critical Settings Checklist

- [ ] **Gravity:** `constant/g` defined in correct direction
- [ ] **Beta:** Thermal expansion coefficient set correctly ($\sim 10^{-3}1for air)
- [ ] **Bounded schemes:** `div(phi,T)` uses `bounded Gauss`
- [ ] **Relaxation:**1$T1relaxation ≤ 0.5 for stability
- [ ] **Residuals:** Tight tolerance on1$T1($< 10^{-6}$)
- [ ] **Validation:** Compare1$Nu1with correlations

### Physical Insight

**The Coupling Loop:**
```
T ↑ → ρ ↓ → Buoyancy ↑ → U ↑ → Convection ↑ → T distribution changes
```

This **two-way coupling** between momentum and energy is what makes buoyancy-driven flows challenging:
- Temperature affects velocity (via buoyancy)
- Velocity affects temperature (via convection)
- **Cannot solve separately** - requires iterative coupling

---

## Concept Check

<details>
<summary><b>1. Boussinesq Approximation สมมติอะไร?</b></summary>

สมมติว่าความหนาแน่นคงที่ทุกที่ **ยกเว้น** ในเทอมแรงลอยตัว:
$$\rho = \rho_0[1 - \beta(T-T_0)]$$

ใช้ได้เมื่อ1$\beta\Delta T \ll 11(เช่น1$\Delta T < 30°C1สำหรับอากาศ)

ข้อดี: ลดความซับซ้อนของสมการ เร็วกว่า compressible formulation
ข้อเสีย: ใช้ไม่ได้กับ1$\Delta T1ใหญ่
</details>

<details>
<summary><b>2. ทำไม `bounded` scheme สำคัญสำหรับ T?</b></summary>

ป้องกัน temperature oscillation และค่าที่ไม่เป็นกายภาพ เช่น:
-1$T < 01K (negative absolute temperature - impossible!)
-1$T > 10^61K (unrealistic for room temperature flows)

 bounded scheme รับประกันว่า:
- Temperature อยู่ในช่วงที่กำหนด
- ไม่เกิด numerical oscillation
- Energy balance ถูกต้อง

หากไม่ใช้ bounded: ค่า T ผิดพลาด → ค่า buoyancy force ผิด → แรงลอยตัวทำนายไม่ถูกต้อง → solution diverge
</details>

<details>
<summary><b>3.1$Ra > 10^91บ่งบอกอะไร?</b></summary>

$Ra > 10^91บ่งบอกว่าการไหลเป็น **turbulent natural convection**

ลักษณะเฉพาะ:
- Boundary layers กลายเป็น unstable (transition to turbulence)
- Flow มี unsteady, chaotic motion
- Heat transfer ถูก enhance อย่างมาก

ผลกระทบต่อ simulation:
- **ต้องใช้ turbulence model** (k-ε, k-ω SST, หรือ LES)
- **ต้อง refine mesh** ตามสูตร y⁺ calculation
- **อาจต้องใช้ transient solver** แม้จะต้องการ steady state

Correlation:1$Nu \propto Ra^{1/3}1(turbulent) vs1$Nu \propto Ra^{1/4}1(laminar)
</details>

<details>
<summary><b>4. ทำไมความสัมพันธ์ระหว่าง p และ T เรียกว่า "two-way coupling"?</b></summary>

ใน buoyancy-driven flows:

**Velocity → Temperature (Convection):**
$$\frac{\partial T}{\partial t} + \mathbf{U} \cdot \nabla T = \alpha \nabla^2 T$$
Velocity field transports heat

**Temperature → Velocity (Buoyancy):**
$$\frac{\partial \mathbf{U}}{\partial t} + \mathbf{U} \cdot \nabla \mathbf{U} = -\nabla p + \nu \nabla^2 \mathbf{U} - \mathbf{g}\beta(T-T_0)$$
Temperature drives velocity through buoyancy

**Why "Two-Way":**
- ไม่สามารถ solve U equation โดยไม่รู้ T
- ไม่สามารถ solve T equation โดยไม่รู้ U
- ต้อง iterate ระหว่างสอง equations จนกว่าจะ converge

**Contrast with forced convection:**
- Forced convection: U known from inlet, T equation solved independently → **one-way coupling**
- Natural convection: U and T must be solved simultaneously → **two-way coupling**
</details>

---

## Related Documents

- **บทก่อนหน้า:** [02_Heat_Transfer_Mechanisms.md](02_Heat_Transfer_Mechanisms.md) - Conduction, convection, radiation fundamentals
- **บทถัดไป:** [04_Conjugate_Heat_Transfer.md](04_Conjugate_Heat_Transfer.md) - Fluid-solid heat transfer coupling
- **Dimensionless Numbers Reference:** See 01_Energy_Equation_Fundamentals.md for Fourier's Law derivation
- **Thermophysical Properties:** See 00_Overview.md for full property tables