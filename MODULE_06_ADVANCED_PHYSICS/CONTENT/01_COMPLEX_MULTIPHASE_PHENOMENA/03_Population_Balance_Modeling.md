# Population Balance Modeling (การจำลองสมดุลประชากร)

> **PBM** = Track particle size distribution evolution in polydisperse multiphase systems

---

## Learning Objectives (เป้าหมายการเรียนรู้)

หลังจากอ่านบทนี้ คุณจะสามารถ:
- **ตัดสินใจ** เลือกระหว่าง PBM กับ constant diameter assumption ได้อย่างเหมาะสม
- **อธิบาย** ความสำคัญของ PBM ต่อการทำนาย mass transfer และ reactor performance ในระบบอุตสาหกรรม
- **ตั้งค่า** Population Balance Model ใน OpenFOAM สำหรับ bubble column และ liquid-liquid systems
- **เลือกใช้** โมเดล coalescence และ breakup ที่เหมาะสมกับแต่ละ application
- **แก้ปัญหา** ประเด็นด้าน numerical stability และ mass conservation ใน PBM simulations
- **ปรับเทียบ** พารามิเตอร์โมเดลเพื่อ matching กับ experimental data

---

## Prerequisites (ความรู้พื้นฐานที่ต้องมี)

- **Euler-Euler Multiphase Framework** (MODULE_03): ความเข้าใจเรื่อง phase fractions, velocity fields, interphase momentum transfer
- **Turbulence Modeling** (MODULE_01): ความเข้าใจ k-ε model, turbulent dissipation rate (ε), และ turbulent kinetic energy (k)
- **Numerical Methods**: ความเข้าใจเรื่อง discretization schemes, solver tolerance, และ under-relaxation
- **Interphase Forces** (MODULE_04): ความเข้าใจ drag, lift, virtual mass forces ใน multiphase flows

---

## Decision Flowchart: PBM vs Constant Diameter

```
START: Is bubble/droplet size distribution important for your application?
│
├─ NO → Use constant diameter (mean d32)
│         ✓ Lower computational cost (solves 1 eqn vs N)
│         ✓ Faster convergence
│         ✓ Sufficient for well-defined, monodisperse systems
│         ✗ Cannot capture breakup/coalescence dynamics
│
└─ YES → Are sizes polydisperse (significant variation > ±20%)?
           │
           ├─ NO → Use 2-3 size groups (narrow distribution)
           │         ✓ Moderate cost increase
           │         ✓ Captures limited size variation
           │
           └─ YES → Is breakup/coalescence significant?
                     │
                     ├─ NO → Use fixed size groups (f0, f1, f2...)
                     │         ✓ Size changes only via transport
                     │         ✓ No source term computation
                     │
                     └─ YES → Use full PBM with source terms
                               ✓ Coalescence models (Lehr, PrinceBlanch...)
                               ✓ Breakup models (Luo, Laakkonen...)
                               ✓ Higher cost (2-5x slower)
                               ✓ Realistic distribution evolution
                               ✗ Requires calibration
```

---

## 1. WHAT: Population Balance Modeling Fundamentals (พื้นฐาน PBM)

### 1.1 Core Concepts

**Population Balance Modeling (PBM)** เป็นวิธีการ track **evolution of particle size distribution** (PSD) ในระบบ multiphase ที่มี:

| Application | Primary Phenomena | Characteristic Length Scale |
|-------------|-------------------|---------------------------|
| **Bubble Columns** | Bubble breakup, coalescence | 0.1 - 10 mm |
| **Liquid-Liquid Emulsions** | Droplet coalescence, breakup | 1 - 500 μm |
| **Crystallizers** | Crystal growth, nucleation, attrition | 1 - 1000 μm |
| **Gas-Liquid Reactors** | Bubble dynamics, mass transfer | 0.5 - 5 mm |
| **Flotation Cells** | Bubble-particle attachment | 0.05 - 2 mm |

### 1.2 Key Terminology

| Term | Symbol | Definition | Unit |
|------|--------|------------|------|
| **Number density function** | $n(d, \mathbf{x}, t)$ | # particles per unit volume per size interval | 1/m⁴ |
| **Sauter Mean Diameter** | $d_{32}$ | Volume-to-surface area ratio | m |
| **Coalescence kernel** | $\omega(d_i, d_j)$ | Rate of particle merger | m³/s |
| **Breakup frequency** | $g(d)$ | Rate of particle fragmentation | 1/s |
| **Size fraction** | $f_i$ | Volume fraction of size group i | - |

### 1.3 Traditional vs PBM Approach

**Traditional Multiphase (Constant Diameter):**
```cpp
// constant/phaseProperties
phases ( water air )
{
    air
    {
        diameterModel constant;
        d              0.003;  // Fixed 3 mm bubbles everywhere
    }
}
```

**Limitations:**
- ❌ ฟองมีขนาดคงที่ → interfacial area เปลี่ยนเฉพาะเมื่อ volume fraction เปลี่ยน
- ❌ ไม่สามารถ capture **breakup** หรือ **coalescence** ได้
- ❌ ทำนาย mass transfer ผิดพลาดใน high-shear zones (impeller, sparger)
- ❌ ไม่สามารถทำนาย local d32 variations ได้

**PBM Approach (Variable Diameter):**
```cpp
// constant/phaseProperties
phases ( water air )
{
    air
    {
        diameterModel velocityGroup;
        sizeGroups
        (
            f0 { d 1e-4; }   // 100 μm
            f1 { d 2e-4; }   // 200 μm
            f2 { d 4e-4; }   // 400 μm
            f3 { d 8e-4; }   // 800 μm
            f4 { d 1.6e-3; } // 1.6 mm
            f5 { d 3.2e-3; } // 3.2 mm
        );
    }
}
```

**Advantages:**
- ✅ Track **size distribution evolution** ตามเวลาและตำแหน่ง
- ✅ Predict **local interfacial area** ได้แม่นยำ
- ✅ Capture **breakup** (high shear → smaller bubbles) และ **coalescence** (low shear → larger bubbles)
- ✅ Enable accurate mass/heat transfer predictions

---

## 2. WHY: Engineering Significance of PBM (ความสำคัญทางวิศวกรรม)

### 2.1 Industrial Impact: Why PBM Matters

**Critical Question:** *When does particle size distribution affect process performance?*

| Application | Why PBM Matters | Economic Impact |
|-------------|-----------------|-----------------|
| **Bubble Column Reactors** | Interfacial area → k<sub>L</sub>a → reaction rate → conversion | ±20% error in d32 → ±20% error in reactor yield → $M/year losses |
| **Flotation Cells** | Bubble size determines particle-bubble collision efficiency → recovery rate | 5% recovery increase = $10-50M/year for Cu/Mo mines |
| **Emulsification** | Droplet distribution affects stability, rheology, product quality | Product failure or customer returns |
| **Crystallizers** | Crystal Size Distribution (CSD) impacts filterability, bioavailability, dissolution | Batch rejection or reprocessing costs |
| **Gas-Liquid Absorbers** | d32 drives mass transfer coefficient → equipment sizing | Oversizing (CAPEX waste) or undersizing (performance shortfall) |

### 2.2 Physical Mechanisms: The d32 Connection

**Sauter Mean Diameter (d32)** is the critical link between size distribution and interfacial area:

$$d_{32} = \frac{\sum_i n_i d_i^3}{\sum_i n_i d_i^2} = \frac{\sum_i \alpha_i d_i}{\sum_i \alpha_i}$$

**Interfacial Area:**
$$A_{int} = \frac{6\alpha}{d_{32}}$$

**Mass Transfer Coefficient:**
$$k_L a \propto A_{int} \propto \frac{1}{d_{32}}$$

**Engineering Consequence:**
- **20% error in d32** → **20% error in k<sub>L</sub>a** → **20% error in reactor performance**
- **Design implication:** PBM enables accurate d32 prediction → reliable scale-up and optimization

### 2.3 Case Studies: PBM in Action

**Case 1: Bubble Column Scale-up**
- **Problem:** Lab-scale (0.1 m) to pilot-scale (1 m) → poor mass transfer prediction
- **Root cause:** Constant d32 assumption failed to capture shear-induced breakup at larger scale
- **Solution:** PBM with LehrMilliesMewes breakup model
- **Result:** d32 predictions within ±10% of experimental data → successful scale-up

**Case 2: Flotation Cell Optimization**
- **Problem:** Recovery rate varies unpredictably with operating conditions
- **Root cause:** Bubble size distribution changes with gas rate and impeller speed
- **Solution:** PBM to predict local d32 → adjust air rate and impeller RPM
- **Result:** Recovery increased from 85% to 92% → $15M/year additional revenue

**Case 3: Crystallizer Product Quality**
- **Problem:** Crystal CSD too broad → filterability issues
- **Root cause:** Breakup and attrition not captured by constant size model
- **Solution:** PBM with nucleation and growth models
- **Result:** CSD narrowed → filtration time reduced by 40%

### 2.4 Decision Criteria: When to Invest in PBM

**Use PBM when:**
- ✅ Size distribution affects **interfacial area** → mass/heat transfer rates
- ✅ **Polydispersity** is significant (size range > 2x)
- ✅ **Breakup and coalescence** are significant (high shear zones, mixing zones)
- ✅ Experimental data shows **size distribution changes** with operating conditions
- ✅ **Scale-up** from lab to pilot/plant scale
- ✅ **Optimization** of mass/heat transfer limited processes

**Use constant diameter when:**
- ✅ Size distribution is narrow (monodisperse, σ/d < 10%)
- ✅ Interfacial area estimation error is acceptable (±20-30%)
- ✅ Computational cost is a concern (preliminary design, screening studies)
- ✅ System is well-characterized with constant d32

---

## 3. HOW: Mathematical Formulation (สมการพื้นฐาน)

### 3.1 General Population Balance Equation

$$\frac{\partial n}{\partial t} + \nabla \cdot (\mathbf{u} n) = \underbrace{\mathcal{B}_{coal} - \mathcal{D}_{coal}}_{\text{Coalescence}} + \underbrace{\mathcal{B}_{break} - \mathcal{D}_{break}}_{\text{Breakup}}$$

**Terms Explained:**

| Symbol | Meaning | Unit | Physical Significance |
|--------|---------|------|----------------------|
| $n(d, \mathbf{x}, t)$ | Number density function | 1/m⁴ | # of particles per unit volume per size interval |
| $\mathcal{B}_{coal}$ | Birth from coalescence | 1/(m⁴·s) | Small particles merge → create larger |
| $\mathcal{D}_{coal}$ | Death from coalescence | 1/(m⁴·s) | Particles merge → disappear from current size |
| $\mathcal{B}_{break}$ | Birth from breakup | 1/(m⁴·s) | Large particles break → create smaller |
| $\mathcal{D}_{break}$ | Death from breakup | 1/(m⁴·s) | Particles break → disappear from current size |

### 3.2 Coalescence Source Terms

**Birth (formation of size d from smaller particles):**
$$\mathcal{B}_{coal} = \frac{1}{2} \int_0^d \omega(d', d-d') n(d') n(d-d') \, dd'$$

**Death (loss of size d when merging with others):**
$$\mathcal{D}_{coal} = n(d) \int_0^\infty \omega(d, d') n(d') \, dd'$$

**Coalescence Kernel (mechanism):**
$$\omega(d_i, d_j) = \underbrace{\frac{\pi}{4} (d_i + d_j)^2 |\mathbf{u}_i - \mathbf{u}_j|}_{\text{Collision frequency}} \cdot \underbrace{P_{coal}}_{\text{Coalescence efficiency}}$$

**Physical interpretation:**
1. **Collision frequency** ∝ cross-sectional area (size)² × relative velocity
2. **Coalescence efficiency** depends on film drainage vs contact time

### 3.3 Breakup Source Terms

**Birth (formation of size d from breakup of larger particles):**
$$\mathcal{B}_{break} = \int_d^\infty g(d') \beta(d|d') n(d') \, dd'$$

**Death (loss of size d when it breaks):**
$$\mathcal{D}_{break} = g(d) n(d)$$

**Breakup Rate (mechanism):**
$$g(d) = C_1 \frac{\epsilon^{1/3}}{d^{2/3}} \exp\left(-C_2 \frac{\sigma}{\rho_d \epsilon^{2/3} d^{5/3}}\right)$$

**Physical interpretation:**
1. **Breakup frequency** ∝ turbulent eddy frequency (∼ ε<sup>1/3</sup>/d<sup>2/3</sup>)
2. **Breakup probability** ∝ exp(-surface energy/turbulent energy)
3. Small particles resist breakup (high surface energy/volume ratio)
4. High turbulence (ε) promotes breakup

---

## 4. HOW: Implementation in OpenFOAM (การนำไปใช้ใน OpenFOAM)

### 4.1 Phase Properties Setup

```cpp
// constant/phaseProperties
phases ( water air );

water
{
    transportModel  Newtonian;
    nu              1e-06;
    rho             1000;
    sigma           0.07;   // Surface tension [N/m]
}

air
{
    transportModel  Newtonian;
    nu              1.48e-05;
    rho             1;

    // ===== PBM SETUP =====
    diameterModel   velocityGroup;  // Discrete size groups method

    velocityGroupCoeffs
    {
        populationBalance bubbles;  // Reference name

        shapeModel spherical;        // Assume spherical particles

        sizeGroups
        (
            f0 { d 1e-4; }    // 100 μm - microbubbles
            f1 { d 2e-4; }    // 200 μm
            f2 { d 4e-4; }    // 400 μm
            f3 { d 8e-4; }    // 800 μm
            f4 { d 1.6e-3; }  // 1.6 mm
            f5 { d 3.2e-3; }  // 3.2 mm - large bubbles
        );
    }

    populationBalanceCoeffs
    {
        populationBalance bubbles;

        // ===== COALESCENCE MODELS =====
        coalescenceModels
        (
            LehrMilliesMewes
            {
                // Turbulent-driven coalescence
                C1  0.15;   // Collision frequency coefficient
                C2  0.006;  // Film drainage coefficient
            }
        );

        // ===== BREAKUP MODELS =====
        breakupModels
        (
            LehrMilliesMewes
            {
                // Turbulent breakup
                C1     0.084;  // Breakup frequency coefficient
                C2     1.26;   // Surface tension exponent
                WeCrit 1.3;    // Critical Weber number
            }
        );
    }
}
```

**Configuration Guidelines:**

| Parameter | Recommended Range | Effect | Tuning Strategy |
|-----------|-------------------|--------|-----------------|
| **Number of size groups** | 4-8 | More groups = better resolution but higher cost | Use geometric progression; start with 6 |
| **Size range** | 0.1-10 × expected d32 | Must cover expected size range | Extend range if distribution shifts |
| **C1 (breakup)** | 0.04-0.16 | Higher = more breakup → smaller bubbles | Match experimental d32 |
| **C2 (breakup)** | 0.8-2.0 | Higher = less breakup → larger bubbles | Match distribution shape |
| **C1 (coalescence)** | 0.10-0.20 | Higher = more coalescence → larger bubbles | Match large-bubble tail |
| **C2 (coalescence)** | 0.004-0.010 | Higher = less coalescence → smaller bubbles | Match small-bubble population |

### 4.2 Boundary Conditions for Size Groups

**Each size group** (`f0`, `f1`, ..., `f5`) is a `volScalarField` representing the volume fraction of that size class.

```cpp
// 0/f0 (size group 0 - smallest bubbles)
dimensions      [0 0 0 0 0 0 0];

internalField   uniform 0;

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 0.03;  // 3% of gas phase in size group 0 (15% of inlet gas)
    }

    outlet
    {
        type            zeroGradient;
    }

    walls
    {
        type            zeroGradient;
    }
}
```

**Mass Conservation Check:**
```cpp
// 0/alpha.air (total gas fraction)
dimensions      [0 0 0 0 0 0 0];

internalField   uniform 0;

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 0.2;  // 20% gas holdup at inlet
    }

    outlet
    {
        type            zeroGradient;
    }

    walls
    {
        type            zeroGradient;
    }
}

// CRITICAL: Verify Σ(f0 + f1 + f2 + ... ) = alpha.air everywhere
// If not, mass conservation is violated!
```

**Inlet Distribution Strategy:**

| Distribution Type | When to Use | Example Setup |
|-------------------|-------------|---------------|
| **Gaussian** | Known mean size and variance | Peak at f2-f3, decreasing outward |
| **Monodisperse** | Well-defined inlet size | All mass in single group |
| **Experimental** | Measured inlet distribution | Match experimental histogram |

### 4.3 Numerical Schemes

```cpp
// system/fvSchemes
ddtSchemes
{
    default         Euler;  // First-order for stability (use backward for steady-state)
}

gradSchemes
{
    default         Gauss linear;
}

divSchemes
{
    // CRITICAL: Use upwind for size groups to prevent numerical oscillations
    // Source terms can cause instability with high-order schemes
    div(phi,f0)     Gauss upwind;
    div(phi,f1)     Gauss upwind;
    div(phi,f2)     Gauss upwind;
    div(phi,f3)     Gauss upwind;
    div(phi,f4)     Gauss upwind;
    div(phi,f5)     Gauss upwind;

    // Other fields
    div(phi,U)      Gauss upwind;
    div(phi,k)      Gauss upwind;
    div(phi,epsilon) Gauss upwind;
}

laplacianSchemes
{
    default         Gauss linear corrected;
}

interpolationSchemes
{
    default         linear;
}
```

**Scheme Selection Guidelines:**
- **Size groups:** Always use `upwind` (stability over accuracy)
- **Pressure:** `linear` (second-order accuracy acceptable)
- **Velocity:** `upwind` for turbulent flows (stability)
- **Turbulence:** `upwind` for k and ε (boundedness)

### 4.4 Solver Configuration

```cpp
// system/fvSolution
solvers
{
    // Size groups - loose tolerance acceptable
    "\"f.*\""
    {
        solver          GAMG;
        tolerance       1e-6;
        relTol          0.1;       // Relaxed for stability
        smoother        GaussSeidel;
    }

    // Pressure - strict tolerance
    p_rgh
    {
        solver          GAMG;
        tolerance       1e-8;
        relTol          0.01;
    }

    // Velocity
    U.air
    {
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-6;
        relTol          0.1;
    }

    U.water
    {
        $U.air;
    }

    // Turbulence
    k
    {
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-6;
        relTol          0.1;
    }

    epsilon
    {
        $k;
    }
}

// Under-relaxation for PBM stability
relaxationFactors
{
    equations
    {
        "\"f.*\""      0.7;  // Size groups (critical for stability)
        U.*            0.7;
        p_rgh          0.3;
        k              0.8;
        epsilon        0.8;
    }
}

// PIMPLE settings for transient simulations
PIMPLE
{
    nCorrectors      3;
    nNonOrthogonalCorrectors 0;
    nAlphaCorr      1;
    nAlphaSubCycles 2;
}
```

### 4.5 Time Step Control

```cpp
// system/controlDict
application     multiphaseEulerFoam;

startFrom       startTime;
startTime       0;

stopAt          endTime;
endTime         10;

deltaT          0.001;

adjustTimeStep  yes;

maxCo           0.5;   // Max Courant number (reduce if unstable)
maxAlphaCo      0.5;   // Max volumetric Courant number

// Time step constraints for PBM:
// 1. Co < 0.5 (Courant constraint)
// 2. Source term stiffness: Δt < 1/max(S_coal, S_break)
// 3. Reduce to 0.0005 if oscillations occur
```

---

## 5. HOW: Coalescence Models (โมเดลการรวมตัว)

### 5.1 Model Selection Guide

| Model | Best For | Mechanism | Complexity | Computational Cost | When to Use |
|-------|----------|-----------|------------|-------------------|-------------|
| **LehrMilliesMewes** | Bubbles in turbulent flow | Turbulent collision + film drainage | High | Medium | **Default for bubble columns** |
| **PrinceBlanch** | Bubbles with surfactants | Collision + film drainage (surfactant-aware) | High | Medium | Surface contamination matters |
| **CoulaloglouTavlarides** | Liquid-liquid dispersions | Droplet collision | Medium | Low-Medium | Emulsification, liquid-liquid systems |
| **Constant** | Testing/debugging | Fixed rate | Low | Low | Initial testing only |

### 5.2 Lehr-Millies-Mewes Model (Default for Bubbles)

**Mechanism:**
$$\omega(d_i, d_j) = \frac{\pi}{4} (d_i + d_j)^2 u_{turb} \cdot \exp\left(-\frac{t_{drainage}}{t_{contact}}\right)$$

**Physics:**
1. **Collision frequency** ∝ (size)² × turbulent velocity fluctuations
2. **Coalescence efficiency** ∝ exp(-drainage time/contact time)
3. Film drainage time depends on viscosity, surface tension
4. Contact time depends on turbulent intensity

```cpp
LehrMilliesMewes
{
    C1  0.15;   // Turbulent frequency coefficient [dimensionless]
    C2  0.006;  // Film drainage coefficient [dimensionless]

    // Tuning guidelines:
    // - Higher C1 → more collisions → more coalescence → larger bubbles
    // - Higher C2 → slower drainage → less coalescence → smaller bubbles
    // - Typical range: C1 = 0.10-0.20, C2 = 0.004-0.010
}
```

**Parameter Tuning Strategy:**

| Symptom | Diagnosis | Adjustment |
|---------|-----------|------------|
| **Bubbles coalesce too much** (all mass in f4-f5) | Excessive coalescence | Increase C2 (slower drainage) or decrease C1 |
| **Bubbles too small** (mass stuck in f0-f1) | Insufficient coalescence | Decrease C2 (faster drainage) or increase C1 |
| **Coalescence effect too weak** | Model underpredicts | Increase C1 by 20-50% |
| **Numerical instability** | Source term too stiff | Reduce C1; decrease time step |

**Effect on Flow Regimes:**
- **High shear zones** (impeller): Turbulence dominates → coalescence suppressed
- **Low shear zones** (bulk, upper regions): Coalescence dominates → larger bubbles
- **Equilibrium**: Balance between breakup and coalescence → steady-state d32

### 5.3 Prince-Blanch Model (Surfactant Effects)

**When to use:** Systems with surface contamination (surfactants, salts, oils)

**Mechanism:** Includes surfactant concentration effect on film drainage

```cpp
PrinceBlanch
{
    C1  0.08;
    C2  0.01;
    // Additional parameters for surfactant effect
    Cs  0.001;  // Surfactant concentration [mol/m³]
}
```

---

## 6. HOW: Breakup Models (โมเดลการแตกตัว)

### 6.1 Model Selection Guide

| Model | Best For | Mechanism | Complexity | When to Use |
|-------|----------|-----------|------------|-------------|
| **LehrMilliesMewes** | Turbulent bubble breakup | Eddy-particle collision | Medium | **Default for bubbles** |
| **LuoSvendsen** | Viscous droplets | Energy density criterion | High | High-viscosity systems (μ > 10 cP) |
| **Laakkonen** | High shear regions | Shear-induced breakup | High | Mixers, rotors, high-shear devices |
| **MartinezBazan** | Highly turbulent flows | Turbulent stress | High | High-Re flows (Re > 10⁵) |

### 6.2 Lehr-Millies-Mewes Breakup Model (Default)

**Mechanism:**
$$g(d) = C_1 \frac{\epsilon^{1/3}}{d^{2/3}} \exp\left(-C_2 \frac{\sigma}{\rho_d \epsilon^{2/3} d^{5/3}}\right)$$

**Physics:**
1. **Breakup frequency** ∝ turbulent eddy frequency (∼ ε<sup>1/3</sup>/d<sup>2/3</sup>)
   - Higher turbulence → more energetic eddies → more breakup
   - Smaller bubbles → higher eddy frequency → more breakup
2. **Breakup probability** ∝ exp(-surface energy/turbulent energy)
   - Surface energy resists breakup (small bubbles resist more)
   - Turbulent energy promotes breakup (high ε promotes breakup)

```cpp
LehrMilliesMewes
{
    C1     0.084;  // Frequency coefficient [dimensionless]
    C2     1.26;   // Surface tension coefficient [dimensionless]
    WeCrit 1.3;    // Critical Weber number [dimensionless]

    // Tuning guidelines:
    // - Higher C1 → more breakup → smaller bubbles
    // - Higher C2 → less breakup → larger bubbles
    // - WeCrit: breakup occurs when We > WeCrit
    // - Typical range: C1 = 0.04-0.16, C2 = 0.8-2.0, WeCrit = 1.0-1.5
}
```

**Parameter Tuning Strategy:**

| Symptom | Diagnosis | Adjustment |
|---------|-----------|------------|
| **Bubbles too large** (d32 > 2× experimental) | Insufficient breakup | Increase C1 (more breakup) or decrease C2 (less resistance) |
| **Bubbles too small** (d32 < 0.5× experimental) | Excessive breakup | Decrease C1 (less breakup) or increase C2 (more resistance) |
| **High shear zones wrong** | Local breakup incorrect | Adjust WeCrit (higher → more breakup resistance) |
| **Breakup too localized** | Model overpredicts shear effect | Reduce C1; check turbulence model |

**Breakup vs Coalescence Competition:**

| Location | Dominant Process | Expected d32 | Model Adjustment |
|----------|------------------|--------------|------------------|
| **Near sparger** | Breakup dominates | Small (0.5-2 mm) | High C1, low C2 (coalescence) |
| **Impeller zone** | Breakup dominates | Small (0.3-1 mm) | Max C1, min C2 (coalescence) |
| **Bulk flow** | Equilibrium | Medium (2-4 mm) | Balance C1, C2 |
| **Upper region** | Coalescence dominates | Large (3-6 mm) | Low C1, high C2 (coalescence) |

### 6.3 Luo-Svendsen Model (Viscous Droplets)

**When to use:** High-viscosity dispersed phase (μ<sub>d</sub> > 10 cP)

**Mechanism:** Energy density criterion - breakup occurs when turbulent eddy energy exceeds surface energy

```cpp
LuoSvendsen
{
    C1  0.08;   // Frequency coefficient
    C2  1.0;    // Surface tension coefficient
    // Viscosity effects included automatically via μd
}
```

---

## 7. HOW: Solvers and Running Simulations (การรันแบบจำลอง)

### 7.1 Supported Solvers

```bash
# General multiphase Euler-Euler with PBM
multiphaseEulerFoam           # Baseline solver for PBM
reactingTwoPhaseEulerFoam     # + reactions and heat transfer
compressibleTwoPhaseEulerFoam # + compressibility effects (high Mach)

# Specialized (older, may have limited PBM support)
bubbleFoam                    # Legacy bubble column solver
twoPhaseEulerFoam             # Simplified 2-phase
```

**Solver Selection Guide:**

| Solver | PBM Support | Reactions | Heat Transfer | Compressible | When to Use |
|--------|-------------|------------|---------------|--------------|-------------|
| **multiphaseEulerFoam** | ✅ Full | ❌ | ❌ | ❌ | **Default for PBM** |
| **reactingTwoPhaseEulerFoam** | ✅ Full | ✅ | ✅ | ❌ | Reactive systems |
| **compressibleTwoPhaseEulerFoam** | ✅ Full | ✅ | ✅ | ✅ | High Mach number |

### 7.2 Running PBM Simulation

```bash
# 1. Setup case from tutorial
cp -r $FOAM_TUTORIALS/multiphase/multiphaseEulerFoam/bubbleColumn myPBMCase
cd myPBMCase

# 2. Modify phaseProperties to use velocityGroup
# Edit constant/phaseProperties:
#    - Change diameterModel from "constant" to "velocityGroup"
#    - Add sizeGroups (f0-f5)
#    - Add coalescence and breakup models

# 3. Create initial fields for size groups
# Create 0/f0, 0/f1, ..., 0/f5
# Initialize with zero or small seed value

# 4. (Optional) Initialize with setFields
cat > system/setFieldsDict << EOF
regions
(
    boxToCell
    {
        box (0 0 0) (0.1 1 1);
        fieldValues
        (
            volScalarFieldValue f0 0.01
            volScalarFieldValue f1 0.02
            volScalarFieldValue f2 0.03
            volScalarFieldValue f3 0.04
            volScalarFieldValue f4 0.05
            volScalarFieldValue f5 0.06
        );
    }
);
EOF

setFields -dict system/setFieldsDict

# 5. Run simulation
multiphaseEulerFoam > log &

# 6. Monitor convergence in real-time
tail -f log | grep -E "Time =|d32 mean =|Courant"

# 7. Check mass conservation
foamListTimes
for time in $(foamListTimes); do
    sumFields $time/f*  # Check sum of size fractions
done

# 8. Post-process
paraFoam -builtin
```

### 7.3 Running in Parallel

```bash
# Decompose case for parallel run
decomposePar

# Run in parallel (4 cores)
mpirun -np 4 multiphaseEulerFoam -parallel > log &

# Reconstruct results
reconstructPar

# Check parallel scalability
# 1 core: 100% reference time
# 2 cores: ~55% (1.8x speedup)
# 4 cores: ~35% (2.8x speedup)
# 8 cores: ~25% (4.0x speedup)
```

---

## 8. HOW: Post-Processing and Validation (การวิเคราะห์ผลลัพธ์)

### 8.1 Sauter Mean Diameter (d32) Analysis

OpenFOAM calculates **Sauter Mean Diameter** automatically:

$$d_{32} = \frac{\sum_i n_i d_i^3}{\sum_i n_i d_i^2} = \frac{\sum_i \alpha_i d_i}{\sum_i \alpha_i}$$

**Physical significance:**
- $d_{32}$ represents volume-to-surface-area ratio
- Directly related to interfacial area: $A_{int} = 6\alpha/d_{32}$

**Extract d32 field:**
```cpp
// system/controlDict
functions
{
    d32Field
    {
        type            surfaces;
        functionObjectLibs ("libsampling.so");
        writeFields     (d32);  // Automatically computed by PBM
        surfaceFormat   vtk;
        interpolationScheme cellPoint;
        surfaces
        (
            plane( (0 0 0) (0 0 1) );
        );
    }

    // Time-averaged d32
    d32Average
    {
        type            fieldAverage;
        functionObjectLibs ("libfieldFunctionObjects.so");
        fields
        (
            d32
        );
        mean            on;
    }
}
```

**Calculate d32 manually (for verification):**
```python
# Python script to calculate d32 from size fractions
import numpy as np

# Size group diameters [m]
d = np.array([1e-4, 2e-4, 4e-4, 8e-4, 1.6e-3, 3.2e-3])

# Size fractions (example values)
f = np.array([0.01, 0.02, 0.05, 0.08, 0.03, 0.01])

# Calculate d32
d32 = np.sum(f * d) / np.sum(f)

print(f"Sauter Mean Diameter: {d32*1000:.2f} mm")

# Calculate interfacial area
alpha_gas = np.sum(f)
A_int = 6 * alpha_gas / d32
print(f"Interfacial Area: {A_int:.2f} m²/m³")
```

### 8.2 Size Distribution Visualization

```bash
# Sample size fractions along a line
cat > system/probesDict << EOF
probes
{
    type            probes;
    probeLocations
    (
        (0.1 0 0)   // Near inlet
        (0.5 0 0)   // Mid-column
        (0.9 0 0)   // Near outlet
    );
    writeFields     (f0 f1 f2 f3 f4 f5 d32);
    writeControl    timeStep;
    writeInterval   10;
}
EOF

# Run simulation with probes
multiphaseEulerFoam

# Plot in Python
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read probe data at final time
time_dirs = !ls postProcessing/probes
final_time = time_dirs[-1]

f_data = []
for i in range(6):
    df = pd.read_csv(f'postProcessing/probes/{final_time}/f{i}', skiprows=1, delim_whitespace=True)
    f_data.append(df.iloc[:, 2].values)  # Extract probe 1 data

# Size group diameters
d = np.array([1e-4, 2e-4, 4e-4, 8e-4, 1.6e-3, 3.2e-3])

# Plot distribution at probe location 1 (x = 0.5 m)
plt.figure(figsize=(10, 6))
plt.bar(d*1000, f_data[5], width=np.array(d)*0.5*1000, edgecolor='black')
plt.xlabel('Bubble Diameter [mm]', fontsize=12)
plt.ylabel('Volume Fraction', fontsize=12)
plt.title('Bubble Size Distribution at x = 0.5 m', fontsize=14)
plt.grid(True, alpha=0.3)
plt.savefig('size_distribution.png', dpi=300)
```

### 8.3 Interfacial Area Calculation

```python
# Calculate interfacial area distribution
A_int_groups = 6 * f / d  # Interfacial area per group [m²/m³]
A_int_total = np.sum(A_int_groups)

print(f"Total Interfacial Area: {A_int_total:.2f} m²/m³")
print(f"Mass Transfer Coefficient (kL*a): ~{0.001 * A_int_total:.4f} 1/s")

# Plot interfacial area contribution by group
plt.figure(figsize=(10, 6))
plt.bar(d*1000, A_int_groups, width=np.array(d)*0.5*1000, edgecolor='black')
plt.xlabel('Bubble Diameter [mm]', fontsize=12)
plt.ylabel('Interfacial Area Contribution [m²/m³]', fontsize=12)
plt.title('Interfacial Area Distribution', fontsize=14)
plt.grid(True, alpha=0.3)
```

### 8.4 Validation Against Experimental Data

**Validation Checklist:**

| Measured Quantity | How to Extract | Validation Target | Acceptable Error |
|-------------------|----------------|-------------------|------------------|
| **Gas holdup** | `alpha.air` field average | Compare with experiment | ±5% |
| **Mean bubble size** | $d_{32}$ field average | Compare with photography/Probe | ±10% |
| **Size distribution** | Histogram of `f0-f5` | Qualitative/quantitative match | Shape match |
| **Interfacial area** | $6\alpha/d_{32}$ | Compare with mass transfer data | ±15% |
| **Radial profile** | $d_{32}(r)$ at different heights | Compare with probe measurements | ±15% |

**Validation Procedure:**
1. **Geometry:** Match experimental dimensions (diameter, height, sparger location)
2. **Boundary conditions:** Match gas flow rate, inlet size distribution
3. **Turbulence model:** Validate k and ε against PIV/LDA data
4. **Calibration:** Adjust C1 and C2 to match experimental d32
5. **Validation:** Compare holdup and distribution against independent dataset

**Common Validation Pitfalls:**
- ❌ Using wrong turbulence model (use k-ε for bubble columns)
- ❌ Inlet size distribution not matched to experiment
- ❌ Wall functions not appropriate for low-Re flows
- ❌ Insufficient mesh resolution near sparger
- ✅ **Best practice:** Grid independence study + sensitivity analysis

---

## 9. Troubleshooting and Best Practices (การแก้ปัญหา)

### 9.1 Common Issues and Solutions

| Symptom | Likely Cause | Diagnostic Action | Solution |
|---------|--------------|-------------------|----------|
| **Mass imbalance** (Σf ≠ α<sub>gas</sub>) | Size groups don't sum to total phase fraction | Check `sum(f0..f5) - alpha.air` in paraFoam | Ensure BCs are consistent; tighten solver tolerance to 1e-6 |
| **Slow convergence** | Strong source terms causing stiffness | Monitor coalescence/breakup rates in log | Use under-relaxation (0.5-0.7 for size groups); reduce number of size groups |
| **Unrealistic distribution** (all mass in one group) | Wrong coalescence/breakup parameters | Plot source terms vs time | Re-calibrate model coefficients; check turbulence model |
| **Numerical oscillations** | Inadequate discretization | Check `divSchemes` for size groups | Use `upwind` for all `div(phi,f*)`; reduce time step |
| **d32 blows up** (NaN or huge values) | Zero in denominator | Check where `sum(f*d^2) ≈ 0` | Add small initial seeding (min 0.01) to all groups |
| **Simulation crashes** | Extreme source terms | Monitor max coalescence/breakup rates | Limit time step (maxCo < 0.3); add source term limiting |
| **Bubbles don't evolve** | Source terms too weak or wrong | Check ε field; verify model activation | Verify turbulence model; increase C1 values |
| **Negative size fractions** | Numerical instability | Check min values in paraFoam | Use upwind scheme; reduce time step; add min limiter |

### 9.2 Parameter Calibration Strategy

**Step-by-Step Calibration Workflow:**

1. **Start with default coefficients** (LehrMilliesMewes)
   ```cpp
   // Initial guess
   Breakup:     C1 = 0.084, C2 = 1.26
   Coalescence: C1 = 0.15,  C2 = 0.006
   ```

2. **Match mean d32** by tuning breakup first (C1<sub>breakup</sub>)
   - d32 too large → increase C1 (more breakup)
   - d32 too small → decrease C1 (less breakup)
   - Target: ±10% of experimental d32

3. **Match distribution shape** by tuning coalescence (C2<sub>coal</sub>)
   - Too many large bubbles → increase C2 (less coalescence)
   - Too many small bubbles → decrease C2 (more coalescence)
   - Target: Qualitative match to histogram

4. **Validate interfacial area** against mass transfer data
   - Calculate A<sub>int</sub> = 6α/d32
   - Compare with k<sub>L</sub>a measurements

5. **Sensitivity analysis:** Vary coefficients by ±20%
   - Assess uncertainty in predictions
   - Identify most sensitive parameters

6. **Cross-validation:** Test against different operating conditions
   - Different gas flow rates
   - Different viscosities/surface tensions

**Calibration Tips:**
- **Calibrate breakup first**, then coalescence (breakup has stronger effect)
- **Use global d32** for initial tuning, then adjust local distribution
- **Document all parameter changes** for reproducibility
- **Validate with independent dataset** (not used for calibration)

### 9.3 Performance Optimization

**Reducing Computational Cost:**

| Strategy | Cost Reduction | Trade-off |
|----------|----------------|-----------|
| **Reduce size groups** (8 → 4) | 30-40% | Loss of resolution in distribution |
| **Coarser mesh** (Δx × 2) | 50-60% | Less accurate flow prediction |
| **Larger time step** (Δt × 2) | 30-40% | May need under-relaxation adjustment |
| **Parallel computing** (4 cores) | 2.5-3x speedup | Diminishing returns beyond 8 cores |
| **2D axisymmetric** | 70-80% | Only for axisymmetric geometries |

**Recommended Setup for Different Stages:**

| Stage | Size Groups | Mesh | Time Step | Parallelization |
|-------|-------------|------|-----------|-----------------|
| **Initial testing** | 4-6 | Coarse | Large (0.002) | Serial or 2 cores |
| **Parameter study** | 6-8 | Medium | Medium (0.001) | 4 cores |
| **Final validation** | 8-10 | Fine | Small (0.0005) | 8 cores |

### 9.4 Mass Conservation Verification

**Critical Check:**
```bash
# Verify Σ(f0..f5) = alpha.air at all times
for t in $(foamListTimes); do
    echo "Time: $t"
    sumFields $t/f0 $t/f1 $t/f2 $t/f3 $t/f4 $t/f5
    # Compare with $t/alpha.air
done
```

**Expected:** Difference < 1% of α<sub>gas</sub>

**If mass conservation violated:**
1. Check boundary conditions (inlet Σf = α<sub>gas</sub>)
2. Verify solver tolerance (tighten to 1e-6)
3. Check for negative size fractions (numerical instability)
4. Reduce time step

---

## Key Takeaways (สรุปสำคัญ)

1. **Use PBM when** size distribution affects interfacial area → mass/heat transfer (bubble columns, crystallizers, emulsifiers, flotation cells)
2. **PBM adds computational cost** (solves N additional transport equations where N = # of size groups) — use 4-8 groups for most applications
3. **d32 is critical**: 20% error in d32 → 20% error in k<sub>L</sub>a → 20% error in reactor performance
4. **LehrMilliesMewes** is the default model for bubble breakup and coalescence in turbulent flows
5. **Always verify** Σ(f<sub>0</sub> + f<sub>1</sub> + ... ) = α<sub>phase</sub> for mass conservation
6. **Calibrate systematically**: Tune breakup (C1) first → match d32, then coalescence (C2) → match distribution shape
7. **Use upwind schemes** for size group transport to prevent numerical oscillations
8. **Under-relaxation is critical**: Use 0.5-0.7 for size groups to maintain stability
9. **Validate against experiments**: Compare gas holdup (±5%), mean d32 (±10%), and interfacial area (±15%)
10. **Industrial relevance**: PBM enables accurate scale-up and optimization of mass/heat transfer limited processes

---

## Practice Exercises (แบบฝึกหัด)

### Exercise 1: Setup Basic PBM Case
**Objective:** Convert a constant-diameter bubble column to use PBM

**Steps:**
```bash
# 1. Copy tutorial case
cp -r $FOAM_TUTORIALS/multiphase/multiphaseEulerFoam/bubbleColumn myPBM
cd myPBM

# 2. Edit constant/phaseProperties:
#    - Change diameterModel from "constant" to "velocityGroup"
#    - Add 6 size groups (f0-f5) with diameters: 100, 200, 400, 800, 1600, 3200 μm
#    - Add LehrMilliesMewes coalescence model (C1=0.15, C2=0.006)
#    - Add LehrMilliesMewes breakup model (C1=0.084, C2=1.26, WeCrit=1.3)

# 3. Create initial fields in 0/:
#    - Create 0/f0, 0/f1, ..., 0/f5
#    - Set internalField: uniform 0
#    - Set inlet BC: distribute 20% gas among groups (Gaussian: peak at f2-f3)
#    - Set walls/outlet: zeroGradient

# 4. Modify system/fvSchemes:
#    - Add div(phi,f0-f5) schemes with Gauss upwind

# 5. Modify system/fvSolution:
#    - Add solver for "\"f.*\"" with GAMG, tolerance 1e-6, relTol 0.1
#    - Add relaxationFactors for size groups: 0.7

# 6. Run for 10 seconds
multiphaseEulerFoam > log &

# 7. Check results
#    - Plot d32 evolution: should reach 2-5 mm at steady state
#    - Verify mass conservation: Σ(f0..f5) ≈ alpha.air
#    - Check size distribution at different heights
```

**Expected Results:**
- Mean d32 at steady state: 2-5 mm (depending on operating conditions)
- Size distribution: Broad distribution with peak in mid-range (f2-f4)
- Mass conservation error: < 1%

---

### Exercise 2: Parameter Sensitivity Analysis
**Objective:** Investigate effect of breakup coefficient on bubble size distribution

**Cases to Run:**

| Case | C1 (breakup) | Expected d32 [mm] | Expected Distribution |
|------|--------------|-------------------|----------------------|
| A | 0.04 | 4-6 (larger) | Shifted to f4-f5 |
| B | 0.084 | 2-4 (baseline) | Balanced across f2-f4 |
| C | 0.16 | 1-2 (smaller) | Shifted to f1-f2 |

**Procedure:**
1. Create three cases: caseA, caseB, caseC
2. Modify only C1 in breakup model (keep other parameters identical)
3. Run each case for 10 seconds
4. Extract d32 contour plots at t=10s
5. Plot size distribution histograms at x=0.5 m
6. Calculate interfacial area: A<sub>int</sub> = 6α/d32

**Analysis:**
- Quantify % change in interfacial area: (A<sub>int,C</sub> - A<sub>int,A</sub>) / A<sub>int,A</sub> × 100%
- Expected: 50-100% increase in interfacial area from Case A to C
- Discuss implications for mass transfer and reactor design

---

### Exercise 3: Validation Against Experimental Data
**Objective:** Compare PBM predictions against bubble column experiments

**Reference:** Deen, N.G., Solberg, T., Hjertager, B.H. (2010) - "Flow structure in bubble columns"

**Experimental Data:**
| Quantity | Experiment |
|----------|------------|
| Column diameter | 0.15 m |
| Column height | 1.5 m |
| Superficial gas velocity | 0.02 m/s |
| Gas holdup | 0.25 |
| Mean d32 [mm] | 4.5 |

**Setup:**
1. Match experimental geometry in blockMeshDict
2. Set inlet gas velocity: 0.02 m/s
3. Use inlet size distribution: Gaussian with mean 4 mm
4. Use PBM with LehrMilliesMewes models

**Calibration:**
1. Run simulation with default coefficients
2. Compare predicted d32 with experimental value
3. Adjust C1 (breakup) to match mean d32
4. Adjust C2 (coalescence) to match distribution shape

**Validation:**
5. Compare gas holdup: α<sub>gas</sub> (predicted vs 0.25)
6. Compare size distribution shape with experimental histogram
7. Calculate errors: |predicted - experimental| / experimental × 100%

**Deliverable:** Validation report including:
1. Simulation setup (mesh, BCs, models, parameters)
2. d32 contour plot at steady state
3. Size distribution histogram at 3 locations (x=0.25, 0.75, 1.25 m)
4. Error analysis table
5. Discussion of discrepancies and potential improvements

---

### Exercise 4: Scale-up Simulation
**Objective:** Use PBM to predict scale-up from lab-scale to pilot-scale bubble column

**Lab-scale (0.1 m diameter):**
- Superficial gas velocity: 0.02 m/s
- Mean d32: 3 mm (from experiment or Exercise 3)

**Pilot-scale (1 m diameter):**
- Same superficial gas velocity: 0.02 m/s
- **Question:** What is the expected mean d32?

**Procedure:**
1. Setup lab-scale simulation (0.1 m diameter, 1 m height)
2. Calibrate PBM parameters to match lab-scale d32
3. Create pilot-scale geometry (1 m diameter, 5 m height)
4. Use identical PBM parameters (scale-up principle)
5. Run pilot-scale simulation
6. Extract d32 at different heights and radial positions

**Analysis:**
- Compare mean d32 between lab and pilot scales
- Explain differences (if any) based on flow regime changes
- Discuss implications for mass transfer and reactor design
- **Critical question:** Can lab-scale parameters be directly applied to pilot-scale?

---

## 🧠 Concept Check

<details>
<summary><b>1. When should you use PBM instead of constant diameter? Provide specific industrial examples.</b></summary>

**Use PBM when:**
- **Bubble column reactors:** Interfacial area drives mass transfer → reaction rates. Scale-up from lab to pilot often fails without PBM due to changing shear conditions.
- **Flotation cells:** Bubble size determines particle-bubble collision efficiency. 20% error in d32 → 20% error in recovery → $M/year losses.
- **Crystallizers:** Crystal Size Distribution (CSD) impacts filterability, bioavailability. Product quality directly tied to CSD.
- **Emulsification:** Droplet distribution affects product stability. Narrow distribution → stable emulsion; broad distribution → phase separation.
- **Gas-liquid absorbers:** d32 drives k<sub>L</sub>a → equipment sizing. PBM enables optimal design vs oversizing (CAPEX waste) or undersizing (performance shortfall).

**Use constant diameter when:**
- Size distribution is narrow (monodisperse, σ/d < 10%)
- Interfacial area estimation error is acceptable (±20-30%)
- Computational cost is a concern (preliminary design, screening studies)
- System is well-characterized with minimal breakup/coalescence

**Decision metric:** If process is mass/heat transfer limited AND size distribution is polydisperse → use PBM.

</details>

<details>
<summary><b>2. What is the Sauter Mean Diameter (d32) and why is it critical for reactor design?</b></summary>

**Definition:**
$$d_{32} = \frac{\sum n_i d_i^3}{\sum n_i d_i^2} = \frac{\sum \alpha_i d_i}{\sum \alpha_i}$$

**Physical meaning:**
- d32 represents the **volume-to-surface-area ratio**
- It is the diameter of a sphere with the same volume-to-surface-area ratio as the entire population

**Engineering significance:**
1. **Interfacial area calculation:** $A_{int} = 6\alpha/d_{32}$
   - d32 directly determines interfacial area available for mass/heat transfer
2. **Mass transfer coefficient:** $k_L a \propto A_{int} \propto 1/d_{32}$
   - Reactor performance (conversion, yield) scales with 1/d32
3. **Design implications:**
   - **20% error in d32** → **20% error in k<sub>L</sub>a** → **20% error in reactor performance**
   - For a $100M/year chemical plant, 20% error = $20M/year uncertainty
   - PBM's main value: predicting local d32 for reliable scale-up and optimization

**Example:**
- Bubble column: d32 = 3 mm → A<sub>int</sub> = 200 m²/m³ → k<sub>L</sub>a = 0.2 1/s → 90% conversion
- If d32 is underestimated by 20% (d32 = 2.4 mm): A<sub>int</sub> = 250 m²/m³ → k<sub>L</sub>a = 0.25 1/s → 95% conversion
- **Design consequence:** Oversizing or undersizing reactor by 20-30%

</details>

<details>
<summary><b>3. How do coalescence and breakup models interact to determine the equilibrium bubble size?</b></summary>

**Competition between mechanisms:**

| Location | Dominant Process | Driving Force | Result |
|----------|------------------|---------------|--------|
| **High shear** (impeller, sparger) | Breakup dominates | Turbulent eddies collide with bubbles → energy transfer | Smaller bubbles (d32: 0.5-2 mm) |
| **Low shear** (bulk, upper regions) | Coalescence dominates | Bubbles collide → film drainage → merger | Larger bubbles (d32: 3-6 mm) |
| **Equilibrium** | Breakup = Coalescence | Balance of turbulent and surface energy | Steady-state d32 |

**Model interaction:**
- **Breakup rate:** $g(d) = C_1 \frac{\epsilon^{1/3}}{d^{2/3}} \exp(-C_2 \frac{\sigma}{\rho \epsilon^{2/3} d^{5/3}})$
  - Increases with turbulence (ε)
  - Decreases with bubble size (d) - small bubbles resist breakup
  - Decreases with surface tension (σ) - higher σ resists breakup

- **Coalescence rate:** $\omega(d_i, d_j) \propto \text{collision frequency} \times \text{efficiency}$
  - Increases with collision frequency (turbulence)
  - Decreases with film drainage time (surface tension, viscosity)

**At equilibrium:**
$$\mathcal{B}_{coal} - \mathcal{D}_{coal} = \mathcal{D}_{break} - \mathcal{B}_{break}$$

**Practical calibration implications:**
- **If bubbles too large everywhere:** Increase breakup (C1<sub>breakup</sub>) or decrease coalescence (C2<sub>coal</sub>)
- **If bubbles too small everywhere:** Decrease breakup (C1<sub>breakup</sub>) or increase coalescence (C2<sub>coal</sub>)
- **If distribution shape wrong:** Adjust coalescence (C2<sub>coal</sub>) to control large-bubble tail
- **Calibrate against experimental d32** at different operating conditions (gas flow rates, impeller speeds)

**Spatial variation:**
- PBM naturally captures local d32 variations
- High shear near impeller → small bubbles
- Low shear in bulk → large bubbles
- This spatial resolution is critical for accurate mass transfer prediction

</details>

<details>
<summary><b>4. What are the common numerical challenges in PBM simulations and how do you mitigate them?</b></summary>

**Common Challenges:**

| Challenge | Cause | Symptoms | Mitigation |
|-----------|-------|----------|------------|
| **Mass conservation violation** | Σf ≠ α<sub>gas</sub> | Negative fractions or sum > α | Use upwind schemes; tighten tolerance; check BCs |
| **Numerical oscillations** | Source term stiffness | Oscillatory d32 evolution | Reduce time step; increase under-relaxation; use upwind |
| **Slow convergence** | Strong coupling between size groups | Residuals plateau | Use under-relaxation (0.5-0.7); reduce number of groups |
| **d32 blowup** | Zero denominator (Σf·d² ≈ 0) | NaN or huge values | Add initial seeding (min 0.01) to all groups |
| **All mass in one group** | Coalescence/breakup imbalance | Unrealistic distribution | Re-calibrate model coefficients |

**Best Practices:**
1. **Numerical schemes:**
   - Always use `upwind` for size group transport: `div(phi,f*)`
   - Use `Euler` (first-order) for ddt in initial testing
   - Switch to `backward` for steady-state accuracy

2. **Solver settings:**
   - Loose tolerance for size groups (1e-6, relTol 0.1)
   - Strict tolerance for pressure (1e-8, relTol 0.01)
   - Under-relaxation: 0.5-0.7 for size groups

3. **Time step control:**
   - maxCo < 0.5 (reduce to 0.3 if unstable)
   - Adaptive time stepping based on source term magnitude
   - Smaller time step near start (transient initialization)

4. **Initialization:**
   - Small seeding in all groups (0.01-0.05) to avoid zero denominator
   - Realistic inlet distribution (Gaussian or experimental)
   - Verify Σf = α<sub>gas</sub> at t=0

5. **Monitoring:**
   - Check mass conservation every time step
   - Plot d32 evolution to detect oscillations
   - Monitor max source term rates

**Diagnostic workflow:**
```
Simulation unstable?
│
├─ Check mass conservation
│   └─ Violated → Verify BCs; tighten tolerance
│
├─ Check for negative fractions
│   └─ Yes → Reduce time step; increase under-relaxation
│
├─ Check d32 evolution
│   └─ Oscillating → Use upwind; reduce time step
│
└─ Check source terms
    └─ Too large → Reduce C1/C2; limit time step
```

</details>

---

## 📖 Related Documentation

- **ภาพรวม:** [00_Overview.md](00_Overview.md) — Overview of complex multiphase phenomena
- **Phase Change:** [01_Phase_Change_Modeling.md](01_Phase_Change_Modeling.md) — Boiling, condensation, and solidification
- **Cavitation:** [02_Cavitation_Modeling.md](02_Cavitation_Modeling.md) — Cavity formation and collapse
- **Interphase Forces:** [../../MODULE_04_MULTIPHASE_FUNDAMENTALS/CONTENT/04_INTERPHASE_FORCES/](../../MODULE_04_MULTIPHASE_FUNDAMENTALS/CONTENT/04_INTERPHASE_FORCES/) — Drag, lift, virtual mass forces
- **Multiphase Solvers:** [../../MODULE_03_SINGLE_PHASE_FLOW/CONTENT/](../../MODULE_03_SINGLE_PHASE_FLOW/CONTENT/) — Euler-Euler framework fundamentals