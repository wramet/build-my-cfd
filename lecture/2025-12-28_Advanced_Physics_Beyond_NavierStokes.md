# บันทึกบทเรียน: Advanced Physics — Beyond Navier-Stokes

**วันที่:** 28 ธันวาคม 2025

> **สิ่งที่จะได้เรียนรู้:**
> 1. Phase Change & Cavitation
> 2. Conjugate Heat Transfer (CHT)
> 3. Reacting Flows & Combustion
> 4. Non-Newtonian Fluids

---

## 1. Overview: เมื่อ Navier-Stokes ไม่พอ

> **Standard CFD:**
> $$\frac{\partial \rho \mathbf{U}}{\partial t} + \nabla \cdot (\rho \mathbf{U}\mathbf{U}) = -\nabla p + \mu \nabla^2 \mathbf{U}$$
> 
> **Advanced Physics:**
> + Phase Change (boiling, condensation)
> + Chemical Reactions
> + Non-constant viscosity
> + Solid-Fluid coupling

### 1.1 MODULE_06 Overview

| Topic | Physics | Solver |
|-------|---------|--------|
| **Phase Change** | Boiling, Cavitation | `interPhaseChangeFoam` |
| **Coupled Physics** | CHT, FSI | `chtMultiRegionFoam` |
| **Reacting Flows** | Combustion | `reactingFoam`, `XiFoam` |
| **Non-Newtonian** | Variable viscosity | `simpleFoam` + viscosity model |

---

## 2. Phase Change — Boiling & Condensation

> **Physical Analogy:** การคั่วป๊อปคอร์น
> - ความร้อนถึงจุดวิกฤต → ของเหลวใน kernel ระเบิดเป็นไอ
> - ต้องใส่พลังงาน (latent heat) เพื่อเปลี่ยนสถานะ

### 2.1 When Does Phase Change Occur?

| Process | Condition | Direction |
|---------|-----------|-----------|
| **Boiling/Evaporation** | T > T_sat | Liquid → Vapor |
| **Condensation** | T < T_sat | Vapor → Liquid |

### 2.2 Driving Force

$$\dot{m}'' \propto \frac{T - T_{sat}}{T_{sat}}$$

**Key Parameters:**
- $T_{sat}$ = saturation temperature (depends on pressure)
- $h_{lv}$ = latent heat of vaporization
- $\dot{m}''$ = mass transfer rate per area

### 2.3 Lee Model

**Most common phase change model in OpenFOAM:**

$$\dot{m}_{lv} = r_l \alpha_l \rho_l \frac{T - T_{sat}}{T_{sat}} \quad (T > T_{sat}, \text{ evaporation})$$

$$\dot{m}_{vl} = r_v \alpha_v \rho_v \frac{T_{sat} - T}{T_{sat}} \quad (T < T_{sat}, \text{ condensation})$$

| Parameter | Meaning | Typical Value |
|-----------|---------|---------------|
| $r_l$, $r_v$ | Relaxation coefficients | 0.1 - 10 s⁻¹ |
| $\alpha$ | Volume fraction | 0-1 |
| $\rho$ | Density | phase property |

### 2.4 OpenFOAM Configuration

```cpp
// constant/phaseProperties
phaseChange
{
    model   Lee;
    LeeCoeffs
    {
        pSat    1e5;        // Saturation pressure [Pa]
        TSat    373.15;     // Saturation temp [K]
        R       461;        // Specific gas constant
        hVap    2.26e6;     // Latent heat [J/kg]
        rv      0.1;        // Relaxation (condensation)
        rl      0.1;        // Relaxation (evaporation)
    }
}
```

---

## 3. Cavitation — Pressure-Driven Vapor

> **Physical Analogy:** การเปิดขวดน้ำอัดลม
> - ฟองไม่ได้เกิดจากความร้อน
> - เกิดจากความดันลดลงอย่างรวดเร็ว
> - ก๊าซที่ละลายอยู่ขยายตัวออกมา

### 3.1 Boiling vs Cavitation

| Aspect | Boiling | Cavitation |
|--------|---------|------------|
| **Driving Force** | High Temperature | Low Pressure |
| **Condition** | T > T_sat | P < P_v |
| **Energy** | Heat input | Kinetic → Potential |
| **Location** | Heat source | High velocity regions |

### 3.2 When Does Cavitation Occur?

$$\sigma = \frac{P_\infty - P_v}{\frac{1}{2}\rho U^2}$$

**Cavitation Number:**
- $\sigma < \sigma_{crit}$ → Cavitation occurs
- High U, Low P → Low σ → Cavitation

### 3.3 Cavitation Models

| Model | Use Case |
|-------|----------|
| **Schnerr-Sauer** | General, bubble-based |
| **Kunz** | Stable, less accurate |
| **Merkle** | Turbomachinery |

### 3.4 Schnerr-Sauer Model

**Based on Rayleigh-Plesset bubble dynamics:**

$$\frac{d\alpha_v}{dt} = \frac{3\alpha_v(1-\alpha_v)}{R_b} \sqrt{\frac{2}{3} \frac{|P_v - P|}{\rho_l}}$$

```cpp
// constant/transportProperties
phaseChangeTwoPhaseMixture
{
    type            SchnerrSauer;
    
    SchnerrSauerCoeffs
    {
        nBubbles    1e13;       // Nucleation sites per m³
        pSat        2300;       // Vapor pressure [Pa]
        dNuc        1e-6;       // Nucleation diameter [m]
    }
}
```

### 3.5 Common Cavitation Problems

| Application | Concern |
|-------------|---------|
| Propellers | Erosion, noise, efficiency loss |
| Pumps | Performance drop, damage |
| Valves | Flow choking, vibration |
| Hydrofoils | Lift reduction |

---

## 4. Population Balance — When Size Matters

> **Problem:** Euler-Euler assumes single bubble size
> **Reality:** Bubbles break up and coalesce → size distribution

### 4.1 Why PBE Matters

| Phenomenon | Effect |
|------------|--------|
| **Breakup** | Large → Small bubbles |
| **Coalescence** | Small → Large bubbles |
| **Size Distribution** | Affects drag, surface area |

### 4.2 Population Balance Equation

$$\frac{\partial n(d)}{\partial t} + \nabla \cdot (\mathbf{U} n) = B_{breakup} - D_{breakup} + B_{coal} - D_{coal}$$

โดย $n(d)$ = number density of bubbles with diameter $d$

### 4.3 Solution Methods

| Method | Description | Cost |
|--------|-------------|------|
| **Classes** | Discrete size bins | High |
| **QMOM** | Track moments | Medium |
| **DQMOM** | Extended QMOM | Medium |

### 4.4 OpenFOAM Configuration

```cpp
// constant/phaseProperties
air
{
    diameterModel   velocityGroup;
    velocityGroupCoeffs
    {
        populationBalance   bubbles;
        shapeModel          spherical;
        sizeGroups
        (
            f1 { d 0.001; }
            f2 { d 0.002; }
            f3 { d 0.004; }
        );
    }
}

populationBalances
{
    bubbles
    {
        continuousPhase water;
        coalescenceModels ( LehrMilliesMewesCoalesecence{} );
        breakupModels ( LuoSvendsenBreakup{} );
    }
}
```

---

## 5. Conjugate Heat Transfer (CHT)

> **CHT = Heat transfer across fluid-solid interface**

### 5.1 Why CHT?

**Standard approach:** Fixed wall temperature or heat flux

**CHT approach:** Solve temperature in both fluid AND solid

| Approach | Solid | BC at Interface |
|----------|-------|-----------------|
| Fixed T | Ignored | `fixedValue` |
| Fixed q | Ignored | `fixedGradient` |
| **CHT** | Solved | `coupled` |

### 5.2 Multi-Region Concept

```
┌─────────────────────────────────────┐
│           Solid Region              │
│    ∂T/∂t = α∇²T (conduction only)   │
├────────────── Interface ────────────┤
│           Fluid Region              │
│  ∂T/∂t + U·∇T = α∇²T (convection)  │
└─────────────────────────────────────┘
```

**At Interface:**
- Temperature continuous: $T_{solid} = T_{fluid}$
- Heat flux continuous: $-k_s \frac{\partial T}{\partial n} = -k_f \frac{\partial T}{\partial n}$

### 5.3 Directory Structure

```
case/
├── constant/
│   ├── regionProperties        ← Defines regions
│   ├── fluid/
│   │   ├── transportProperties
│   │   └── turbulenceProperties
│   └── solid/
│       └── thermophysicalProperties
├── system/
│   ├── fluid/
│   │   ├── fvSchemes
│   │   └── fvSolution
│   └── solid/
│       ├── fvSchemes
│       └── fvSolution
└── 0/
    ├── fluid/
    │   ├── T, U, p
    └── solid/
        └── T
```

### 5.4 regionProperties

```cpp
regions
(
    fluid   ( cabin )
    solid   ( heater wall )
);
```

### 5.5 Interface Boundary Conditions

```cpp
// 0/fluid/T at interface
interface
{
    type            compressible::turbulentTemperatureCoupledBaffleMixed;
    Tnbr            T;      // Field name in neighbor region
    kappaMethod     fluidThermo;
    value           uniform 300;
}

// 0/solid/T at interface
interface
{
    type            compressible::turbulentTemperatureCoupledBaffleMixed;
    Tnbr            T;
    kappaMethod     solidThermo;
    value           uniform 300;
}
```

### 5.6 Solver: chtMultiRegionFoam

```bash
# Split mesh into regions
splitMeshRegions -cellZones -overwrite

# Run solver
chtMultiRegionFoam
```

---

## 6. Reacting Flows — Combustion

> **Reacting Flow = Fluid Flow + Chemical Reactions**

### 6.1 Additional Equations

**Species Transport:**
$$\frac{\partial (\rho Y_i)}{\partial t} + \nabla \cdot (\rho \mathbf{U} Y_i) = \nabla \cdot (\rho D_i \nabla Y_i) + \omega_i$$

โดย:
- $Y_i$ = mass fraction of species $i$
- $D_i$ = diffusion coefficient
- $\omega_i$ = reaction rate (source term!)

**Energy Equation:**
$$\frac{\partial (\rho h)}{\partial t} + \nabla \cdot (\rho \mathbf{U} h) = \nabla \cdot (k \nabla T) + \dot{Q}_{reaction}$$

### 6.2 Combustion Regimes

| Regime | Description | Flame |
|--------|-------------|-------|
| **Premixed** | Fuel + Air mixed before | Thin flame (deflagration) |
| **Non-premixed** | Fuel and Air separate | Diffusion flame |
| **Partially premixed** | Mix of both | Complex |

### 6.3 Key Solvers

| Solver | Use Case |
|--------|----------|
| `reactingFoam` | General multi-species |
| `XiFoam` | Premixed combustion |
| `sprayFoam` | Spray + combustion |
| `fireFoam` | Fire simulation |

### 6.4 Chemistry-Turbulence Interaction

**Problem:** Reaction timescale << Turbulence timescale
**Challenge:** Sub-grid mixing affects reaction rate

| Model | Description |
|-------|-------------|
| **EDC** | Eddy Dissipation Concept |
| **PaSR** | Partially Stirred Reactor |
| **Flamelet** | Tabulated chemistry |
| **Finite Rate** | Direct Arrhenius |

### 6.5 Finite Rate Chemistry

**Arrhenius Equation:**
$$k = A T^n \exp\left(-\frac{E_a}{RT}\right)$$

```cpp
// constant/chemistryProperties
chemistryType
{
    chemistrySolver ode;
    chemistryThermo psi;
}

chemistry on;
initialChemicalTimeStep 1e-7;

odeCoeffs
{
    solver seulex;
    eps    0.05;
}
```

### 6.6 Species Thermodynamic Properties

```cpp
// constant/thermophysicalProperties
thermoType
{
    type            hePsiThermo;
    mixture         reactingMixture;
    transport       sutherland;
    thermo          janaf;
    equationOfState perfectGas;
    specie          specie;
    energy          sensibleEnthalpy;
}

// Species defined in constant/reactions
```

### 6.7 CHEMKIN Format

OpenFOAM can read CHEMKIN-format mechanism files:

```
constant/
├── reactions           ← Reaction definitions
└── thermo.compressibleGas  ← Thermodynamic data
```

---

## 7. Non-Newtonian Fluids

> **Newtonian:** $\tau = \mu \dot{\gamma}$ (constant μ)
> **Non-Newtonian:** $\tau = \eta(\dot{\gamma}) \dot{\gamma}$ (μ depends on shear rate)

### 7.1 Examples

| Fluid | Behavior | Application |
|-------|----------|-------------|
| Blood | Shear-thinning | Biomedical |
| Ketchup | Shear-thinning + yield | Food |
| Corn starch | Shear-thickening | Fun! |
| Paint | Shear-thinning | Coating |
| Polymer melt | Viscoelastic | Manufacturing |

### 7.2 Behavior Types

```
Shear Rate (γ̇) →

                   Shear-thickening (n > 1)
                  /
Viscosity ────────── Newtonian (n = 1)
                  \
                   Shear-thinning (n < 1)
```

### 7.3 Common Models

**Power Law:**
$$\eta = k \dot{\gamma}^{n-1}$$

| Parameter | Meaning |
|-----------|---------|
| $k$ | Consistency index |
| $n$ | Flow behavior index |
| $n < 1$ | Shear-thinning |
| $n = 1$ | Newtonian |
| $n > 1$ | Shear-thickening |

**Cross Model:**
$$\eta = \eta_\infty + \frac{\eta_0 - \eta_\infty}{1 + (m\dot{\gamma})^n}$$

**Carreau Model:**
$$\eta = \eta_\infty + (\eta_0 - \eta_\infty)[1 + (\lambda\dot{\gamma})^2]^{(n-1)/2}$$

**Herschel-Bulkley (with yield stress):**
$$\tau = \tau_y + k\dot{\gamma}^n$$

### 7.4 OpenFOAM Configuration

```cpp
// constant/transportProperties
transportModel  CrossPowerLaw;

CrossPowerLawCoeffs
{
    nu0     0.01;       // η₀ (zero shear viscosity)
    nuInf   0.0001;     // η∞ (infinite shear viscosity)
    m       0.1;        // Time constant
    n       0.5;        // Power law index (< 1 = thinning)
}
```

```cpp
// Alternative: Power Law
transportModel  powerLaw;

powerLawCoeffs
{
    nuMax   1e-2;       // Maximum viscosity
    nuMin   1e-6;       // Minimum viscosity
    k       0.01;       // Consistency
    n       0.5;        // Flow index
}
```

### 7.5 Available Models

| Model | OpenFOAM Keyword |
|-------|------------------|
| Power Law | `powerLaw` |
| Cross | `CrossPowerLaw` |
| Carreau | `Carreau` |
| Herschel-Bulkley | `HerschelBulkley` |
| Bird-Carreau | `BirdCarreau` |

---

## 8. Quick Reference

### 8.1 Solver Selection

| Physics | Solver |
|---------|--------|
| Phase change (VOF) | `interPhaseChangeFoam` |
| Phase change (Euler) | `reactingTwoPhaseEulerFoam` |
| Cavitation | `interPhaseChangeFoam` |
| CHT | `chtMultiRegionFoam` |
| Combustion (premixed) | `XiFoam` |
| Combustion (general) | `reactingFoam` |
| Non-Newtonian | Standard solvers + model |

### 8.2 Key Files by Physics

| Physics | Key Files |
|---------|-----------|
| Phase Change | `phaseProperties`, `thermophysicalProperties` |
| Cavitation | `transportProperties` |
| CHT | `regionProperties`, per-region fvSchemes/fvSolution |
| Reacting | `chemistryProperties`, `reactions`, `thermophysicalProperties` |
| Non-Newtonian | `transportProperties` |

---

## 9. 🧠 Advanced Concept Check

### Level 1: Fundamentals

<details>
<summary><b>Q1: Boiling กับ Cavitation ต่างกันอย่างไร?</b></summary>

**คำตอบ:**

| Aspect | Boiling | Cavitation |
|--------|---------|------------|
| **Cause** | T > T_sat | P < P_v |
| **Driving Force** | Heat addition | Pressure drop |
| **Location** | Near heat source | High velocity regions |
| **Energy** | Thermal → Phase change | Kinetic → Potential |

**ทั้งสองผลิตฟองไอ แต่สาเหตุต่างกัน:**
- Boiling: ให้ความร้อน → T สูง → เดือด
- Cavitation: เพิ่มความเร็ว → P ต่ำ → เกิดฟอง

</details>

<details>
<summary><b>Q2: ทำไม CHT ต้องใช้ Multi-region?</b></summary>

**คำตอบ:**

**ของไหลกับของแข็งมีสมการต่างกัน:**

| Domain | Equation |
|--------|----------|
| Fluid | $\frac{\partial T}{\partial t} + \mathbf{U} \cdot \nabla T = \alpha \nabla^2 T$ |
| Solid | $\frac{\partial T}{\partial t} = \alpha \nabla^2 T$ |

- Fluid มี **convection** (U·∇T)
- Solid มีแค่ **conduction**

**ถ้าใช้ mesh เดียว:**
- ต้อง solver ที่ handle ทั้งสอง
- หรือ neglect solid dynamics

**Multi-region:**
- แยก mesh → แยก solver
- Couple ที่ interface ด้วย BC พิเศษ

</details>

<details>
<summary><b>Q3: Why is n < 1 called "shear-thinning"?</b></summary>

**คำตอบ:**

**Power Law:**
$$\eta = k \dot{\gamma}^{n-1}$$

**ถ้า n < 1:**
$$\eta = k \dot{\gamma}^{negative}$$

เมื่อ $\dot{\gamma}$ เพิ่ม → $\dot{\gamma}^{negative}$ ลด → $\eta$ ลด!

**ตัวอย่าง:** Blood, paint, ketchup
- ที่ shear สูง (flowing) → viscosity ต่ำ → ไหลง่าย
- ที่ shear ต่ำ (rest) → viscosity สูง → ค้างอยู่กับที่

**Biological advantage:**
Blood ไหลง่ายใน arteries (high shear) แต่หนืดเมื่อหยุด (clotting)

</details>

### Level 2: Modeling

<details>
<summary><b>Q4: Lee model relaxation coefficient (r) มีผลอย่างไร?</b></summary>

**คำตอบ:**

$$\dot{m}_{lv} = r_l \alpha_l \rho_l \frac{T - T_{sat}}{T_{sat}}$$

**r ควบคุม:**
- **r สูง:** Mass transfer เร็ว → ใกล้ equilibrium
- **r ต่ำ:** Mass transfer ช้า → non-equilibrium effects

**Practical:**
| r | Effect | Use |
|---|--------|-----|
| 0.1 | Slow, stable | Initial runs |
| 1-10 | Moderate | General |
| 100+ | Fast, may diverge | Near-equilibrium |

**Tuning:**
- เริ่มจาก r = 0.1 → เพิ่มจนได้ผลที่ต้องการ
- ถ้า diverge → ลด r และ ลด Δt

</details>

<details>
<summary><b>Q5: EDC (Eddy Dissipation Concept) คืออะไร?</b></summary>

**คำตอบ:**

**Problem:** Combustion timescale << Turbulence timescale

**EDC Idea:**
- Reactions occur in "fine structures" (small eddies)
- Rate limited by mixing, not chemistry

$$\overline{\dot{\omega}} = \frac{1}{\tau^*} \gamma^* \rho (Y - Y^*)$$

โดย:
- $\tau^*$ = characteristic time (from k, ε)
- $\gamma^*$ = fine structure volume fraction
- $Y^*$ = equilibrium composition

**Advantage:**
- ไม่ต้องแก้ stiff chemistry ODE ใน high turbulence
- Faster than finite-rate

**Limitation:**
- Assumes chemistry is fast
- May miss extinction/ignition phenomena

</details>

<details>
<summary><b>Q6: Population Balance ทำไมต้องใช้กับ bubble column?</b></summary>

**คำตอบ:**

**Standard Euler-Euler:**
- Assumes single mean diameter $d$
- Drag ∝ $d²$, Surface area ∝ $d²$

**Reality:**
```
Inlet: Small bubbles (d = 1 mm)
       ↓ Coalescence
Middle: Mixed sizes (d = 1-10 mm)
       ↓ Breakup (turbulence)
Top: Size distribution
```

**Impact:**
| Size | Rise velocity | Interfacial area | Mass transfer |
|------|---------------|------------------|---------------|
| Small | Slow | High | High |
| Large | Fast | Low | Low |

**PBE Gives:**
- Size distribution evolution
- Correct surface area → mass transfer
- Correct drag → phase distribution

**Without PBE:**
ผลลัพธ์อาจผิด 30-50% สำหรับ mass transfer rate!

</details>

### Level 3: Numerical

<details>
<summary><b>Q7: ทำไม Phase Change ต้องใช้ Δt เล็ก?</b></summary>

**คำตอบ:**

**Phase Change = Strong Source Term:**
$$\frac{\partial \alpha}{\partial t} = \dot{m}/\rho$$

**Problem:**
เมื่อ $\dot{m}$ สูง → α เปลี่ยนเร็ว → ρ เปลี่ยนเร็ว

**ผลกระทบ:**
1. **Density ratio:** ρ_l/ρ_v ∼ 1000 for water
2. **Volume expansion:** Large when liquid → vapor
3. **Pressure spike:** ถ้า volume เพิ่มเร็วเกินแก้ pressure ทัน

**Solution:**
```cpp
adjustTimeStep  yes;
maxCo           0.2;    // ต่ำกว่าปกติ!
maxAlphaCo      0.1;

// หรือ
deltaT          1e-6;   // Fixed small Δt
```

</details>

<details>
<summary><b>Q8: CHT interface ต้อง "coupled" อย่างไร?</b></summary>

**คำตอบ:**

**Requirements at interface:**

1. **Temperature continuity:**
$$T_{solid} = T_{fluid}$$

2. **Heat flux continuity:**
$$q_s = q_f$$
$$-k_s \frac{\partial T_s}{\partial n} = -k_f \frac{\partial T_f}{\partial n}$$

**OpenFOAM Implementation:**

```cpp
// turbulentTemperatureCoupledBaffleMixed
// ทำ iteration ระหว่าง regions:

// 1. Solid side คำนวณ ∂T/∂n
// 2. ส่ง heat flux ให้ fluid
// 3. Fluid update T
// 4. ส่ง T กลับให้ solid
// 5. Repeat จน converge
```

**Alternative: Monolithic**
- แก้ทุก region พร้อมกัน
- Faster convergence แต่ complex implementation

</details>

<details>
<summary><b>Q9: Non-Newtonian ทำให้ solver ยากขึ้นอย่างไร?</b></summary>

**คำตอบ:**

**Newtonian:**
- μ = constant
- Linear viscous term: μ∇²U

**Non-Newtonian:**
- μ = μ(γ̇) where γ̇ = |∇U + ∇Uᵀ|
- ต้องคำนวณ γ̇ ก่อน → แล้วคำนวณ μ

**Complications:**

1. **Non-linearity:**
   - μ depends on U → Equation becomes non-linear
   - ต้อง iterate มากขึ้น

2. **Stiff viscosity range:**
   ```
   η₀ = 0.01 Pa·s (at rest)
   η∞ = 0.0001 Pa·s (flowing)
   ```
   Ratio = 100x → numerical stiffness

3. **Yield stress (Herschel-Bulkley):**
   - μ → ∞ when τ < τy
   - ต้องใช้ regularization: μ_max = cutoff

**Solution:**
```cpp
// Use under-relaxation
relaxationFactors
{
    equations { U 0.5; }  // ต่ำกว่าปกติ
}

// Limit viscosity
nuMax 1e-2;
nuMin 1e-6;
```

</details>

---

## 10. ⚡ Hands-on Challenges

### Challenge 1: Boiling in a Channel (⭐⭐⭐⭐)

**วัตถุประสงค์:** จำลอง phase change

```bash
# หา tutorial
find $FOAM_TUTORIALS -name "*boil*" -o -name "*phaseChange*"
```

**Tasks:**
1. Set up heating element at bottom wall
2. Run until vapor bubbles form
3. Plot temperature and α over time

---

### Challenge 2: CHT Heat Sink (⭐⭐⭐⭐)

**วัตถุประสงค์:** จำลอง heat sink cooling

```bash
cp -r $FOAM_TUTORIALS/heatTransfer/chtMultiRegionFoam/heatedDuct .
```

**Tasks:**
1. เข้าใจ directory structure (multi-region)
2. รัน simulation
3. วิเคราะห์ temperature distribution in solid vs fluid

---

### Challenge 3: Non-Newtonian Pipe Flow (⭐⭐⭐)

**วัตถุประสงค์:** เปรียบเทียบ Newtonian vs Non-Newtonian

**Tasks:**
1. Set up pipe flow (simpleFoam)
2. Run with Newtonian (constant ν)
3. Switch to Power Law (n = 0.5)
4. Compare velocity profiles

---

## 11. ❌ Common Mistakes

### Mistake 1: Δt ใหญ่เกินสำหรับ Phase Change

```cpp
// ❌ Too large
deltaT 0.01;
maxCo 1;

// Phase change source term too strong → divergence!

// ✅ Conservative
adjustTimeStep yes;
maxCo 0.2;
maxAlphaCo 0.1;
```

---

### Mistake 2: ลืม Split Mesh สำหรับ CHT

```bash
# ❌ Forgot to split
chtMultiRegionFoam  # Error: no regions!

# ✅ Split first
splitMeshRegions -cellZones -overwrite
chtMultiRegionFoam
```

---

### Mistake 3: Wrong Interface BC

```cpp
// ❌ Fixed temperature at interface
interface { type fixedValue; value 300; }
// ไม่ coupled! Heat transfer wrong.

// ✅ Coupled BC
interface
{
    type    compressible::turbulentTemperatureCoupledBaffleMixed;
    Tnbr    T;
    kappaMethod fluidThermo;
}
```

---

### Mistake 4: Chemistry Stiffness

```cpp
// ❌ Default ODE solver
solver  Euler;
// Very stiff chemistry → need tiny Δt or diverge

// ✅ Stiff ODE solver
solver  seulex;
eps     0.05;
```

---

### Mistake 5: Viscosity Limits Missing

```cpp
// ❌ No limits
powerLawCoeffs
{
    k   0.01;
    n   0.3;
}
// At low shear: ν → ∞ → divergence!

// ✅ With limits
powerLawCoeffs
{
    nuMax   1e-2;
    nuMin   1e-6;
    k       0.01;
    n       0.3;
}
```

---

## 12. 🔗 เชื่อมโยงกับ Repository

| หัวข้อ | ไฟล์ใน Repository |
|--------|-------------------|
| **Phase Change** | `MODULE_06/01_COMPLEX_MULTIPHASE_PHENOMENA/` |
| **Cavitation** | `MODULE_06/01_COMPLEX_MULTIPHASE_PHENOMENA/02_Cavitation_Modeling.md` |
| **Population Balance** | `MODULE_06/01_COMPLEX_MULTIPHASE_PHENOMENA/03_Population_Balance_Modeling.md` |
| **Coupled Physics** | `MODULE_06/02_COUPLED_PHYSICS/` |
| **CHT** | `MODULE_06/02_COUPLED_PHYSICS/02_Conjugate_Heat_Transfer.md` |
| **FSI** | `MODULE_06/02_COUPLED_PHYSICS/03_Fluid_Structure_Interaction.md` |
| **Reacting Flows** | `MODULE_06/03_REACTING_FLOWS/` |
| **Non-Newtonian** | `MODULE_06/04_NON_NEWTONIAN_FLUIDS/` |

---

## 13. สรุป: หลักการ Advanced Physics

### หลักการ 5 ข้อ

1. **Start Simple, Add Complexity**
   - Basic flow first → add phase change / reactions
   - Verify each step before adding next

2. **Understand the Driving Force**
   - Boiling: T > T_sat
   - Cavitation: P < P_v
   - Reactions: Concentration gradients

3. **Time Step Control is Critical**
   - Strong source terms → need small Δt
   - adjustTimeStep with conservative Co

4. **Multi-Region = Multiple Meshes**
   - CHT needs separate fluid/solid regions
   - Interface BC couples them

5. **Validate Against Experiments**
   - Advanced physics = high uncertainty
   - Always compare with experimental data

---

*"Advanced physics is not just adding more equations — it's understanding how different phenomena interact"*
