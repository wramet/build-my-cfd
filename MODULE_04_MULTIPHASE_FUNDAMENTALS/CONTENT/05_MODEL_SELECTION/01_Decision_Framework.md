# Model Selection Decision Framework

กรอบการตัดสินใจเลือกแบบจำลอง Multiphase Flow

---

## Learning Objectives

หลังจากศึกษาบทนี้ คุณควรจะสามารถ:
- **จัดหมวดหมู่** multiphase system ตาม phase types และ flow regimes
- **คำนวณและวิเคราะห์** dimensionless numbers ที่จำเป็นสำหรับการเลือก model
- **เลือกใช้** appropriate sub-models (drag, lift, virtual mass, turbulent dispersion) สำหรับแต่ละสถานการณ์
- **ประยุกต์ใช้** incremental complexity approach เพื่อสร้าง stable simulation แบบ step-by-step
- **ตั้งค่า** OpenFOAM phaseProperties และ fvSolution อย่างเหมาะสมกับกรณีศึกษา

---

## Prerequisites

ความรู้พื้นฐานที่ต้องมีก่อนศึกษาบทนี้:

1. **Fundamental Concepts** ([01_FUNDAMENTAL_CONCEPTS/00_Overview.md](01_FUNDAMENTAL_CONCEPTS/00_Overview.md))
   - Flow regimes (separated vs dispersed)
   - Interfacial phenomena basics
   - Volume fraction definitions

2. **Interphase Forces** ([04_INTERPHASE_FORCES](04_INTERPHASE_FORCES))
   - Drag force fundamentals and models
   - Lift force mechanisms
   - Virtual mass concept
   - Turbulent dispersion theory

3. **Numerical Methods** (จาก MODULE_03)
   - Pressure-velocity coupling algorithms
   - Solver stability considerations

---

## Why This Matters

การเลือก model ที่เหมาะสมเป็น **critical decision** ที่มีผลต่อ:
- **Computational cost** — complex model อาจใช้เวลา 10x เพิ่มขึ้น
- **Solution stability** — over-modeling นำไปสู่ divergence
- **Physical accuracy** — under-modeling ทำให้คำตอบผิดพลาด

> **จุดสำคัญ:** เริ่มจาก simple model แล้วค่อยเพิ่มความซับซ้อนตามที่จำเป็นเท่านั้น

---

## Core Principle

> **เลือกโมเดลที่เรียบง่ายที่สุด** ที่ยังคงทำนายฟิสิกส์ที่สำคัญได้ถูกต้อง

---

## 1. System Classification

### 1.1 Phase Types

| System | Solver | Use Case | Key Considerations |
|--------|--------|----------|-------------------|
| **Gas-Liquid** | `interFoam`, `multiphaseEulerFoam` | Bubbles, droplets, boiling | Surface tension critical for VOF |
| **Liquid-Liquid** | `interFoam` | Emulsions, oil-water separation | Density difference often small |
| **Gas-Solid** | `multiphaseEulerFoam` | Fluidized beds, pneumatic conveying | KTGF essential for dense phase |
| **Liquid-Solid** | `twoPhaseEulerFoam` | Slurries, sediment transport | Wall friction important |

### 1.2 Flow Regimes

| Regime | Characteristic Length | Method | Typical α Distribution |
|--------|----------------------|--------|----------------------|
| **Separated** | Interface thickness ≪ domain | VOF | α = 0 or 1 only |
| **Dispersed** | Particle/bubble size ≪ domain | Euler-Euler | 0 < α < 1 continuous |

**Decision Criteria:**
- **VOF**: Interface position ที่แม่นยำสำคัญ (free surface, stratified flow)
- **Euler-Euler**: Particle/bubble statistics สำคัญ (bubbly flow, fluidized bed)

---

## 2. Dimensionless Numbers for Model Selection

### 2.1 Particle Reynolds Number

$$Re_p = \frac{\rho_c u_{rel} d_p}{\mu_c}$$

| $Re_p$ | Regime | Drag Model | Physical Meaning |
|--------|--------|------------|------------------|
| < 1 | **Stokes** | $C_D = 24/Re_p$ | Viscous forces dominate |
| 1-1000 | **Transition** | Schiller-Naumann | Both viscous + inertial |
| > 1000 | **Newton** | $C_D = 0.44$ | Inertial forces dominate |

**คำนวณ:** ใช้ characteristic velocity $u_{rel}$ จาก terminal velocity หรือ inlet conditions

### 2.2 Eötvös Number

$$Eo = \frac{g(\rho_c - \rho_d)d_p^2}{\sigma}$$

| $Eo$ | Shape | Drag Model | Lift Model |
|------|-------|------------|------------|
| < 1 | Spherical | Schiller-Naumann | Saffman-Mei |
| 1-10 | Slightly deformed | Ishii-Zuber | Tomiyama |
| > 10 | Highly deformed | Tomiyama | Tomiyama (deformable) |

**Physical Insight:** $Eo$ เปรียบเทียบ gravitational force กับ surface tension
- Low $Eo$ → surface tension keeps shape spherical
- High $Eo$ → buoyancy deforms interface

### 2.3 Volume Fraction

| $\alpha_d$ | Concentration | Approach | Required Models |
|------------|---------------|----------|-----------------|
| < 0.1 | **Dilute** | Lagrangian or simple Euler | Drag only |
| 0.1-0.3 | **Moderate** | Euler + consider KTGF | Drag + Lift |
| > 0.3 | **Dense** | **Euler + KTGF** | Drag + KTGF + collisions |

**Critical Note:** KTGF becomes essential above $\alpha_d \approx 0.3$ when particle-particle collisions dominate

---

## 3. Sub-Model Selection Guide

### 3.1 Drag Models

| Model | Use Case | OpenFOAM Keyword | Pros | Cons |
|-------|----------|------------------|------|------|
| **Schiller-Naumann** | Spherical particles, $Re_p < 800$ | `SchillerNaumann` | Simple, validated | Not for deformable |
| **Ishii-Zuber** | Deformed bubbles, $Eo > 1$ | `IshiiZuber` | Captures deformation | Limited to bubbles |
| **Tomiyama** | Contaminated/deformed bubbles | `Tomiyama` | Includes contamination | Complex calibration |
| **Grace** | High viscosity ratio ($\mu_d/\mu_c > 100$) | `Grace` | Viscous effects | Rarely needed |
| **Syamlal-O'Brien** | Fluidized beds, gas-solid | `SyamlalOBrien` | Fits solid data | Not for bubbles |
| **Wen-Yu** | Dilute gas-solid, $\alpha_d < 0.2$ | `WenYu` | Simple | Fails at high α |
| **Ergun** | Dense gas-solid, $\alpha_d > 0.6$ | `Ergun` | Packed bed accurate | Too stiff for flow |

**Decision Flow:**
1. Calculate $Re_p$ and $Eo$
2. Gas-liquid → start with Schiller-Naumann, upgrade if $Eo > 1$
3. Gas-solid → Wen-Yu (dilute) or Ergun (dense)

### 3.2 Lift Models

| Model | Use Case | OpenFOAM Keyword | Key Formula |
|-------|----------|------------------|-------------|
| **Saffman-Mei** | Small particles ($Re_p < 20$) | `SaffmanMei` | Shear-induced |
| **Tomiyama** | Deformable bubbles | `Tomiyama` | $Eo$-dependent |
| **Legendre-Magnaudet** | Clean bubbles, $Re_p < 500$ | `LegendreMagnaudet` | High $Re$ correction |

**When to Include Lift:**
- **Required:** Shear flows (pipe, boundary layer)
- **Optional:** Homogeneous turbulence
- **Skip:** 1D vertical flows

### 3.3 Virtual Mass

$$\mathbf{F}_{VM} = C_{VM} \rho_c \alpha_d \left(\frac{D\mathbf{u}_c}{Dt} - \frac{D\mathbf{u}_d}{Dt}\right)$$

| Condition | $\rho_d/\rho_c$ | $C_{VM}$ | Action |
|-----------|-----------------|----------|--------|
| Heavy particles | > 1000 | Ignore | Adds stiffness, negligible effect |
| Light particles | < 10 | 0.5 | **Essential** for stability |
| Intermediate | 10-1000 | 0.2-0.5 | Test sensitivity |

**Physical Meaning:** Virtual mass accounts for fluid acceleration around accelerating particles

### 3.4 Turbulent Dispersion

| Model | Use Case | OpenFOAM Keyword | Notes |
|-------|----------|------------------|-------|
| **Burns** | General-purpose | `Burns` | $C_{td} \approx 0.1-1.0$ |
| **Lopez de Bertodano** | Bubbly flow | `LopezDeBertodano` | Calibrated for bubbles |
| **Constant** | Simple approximation | `constantCoefficient` | Fixed diffusion |

**When Required:**
- Turbulent intensity > 5%
- Important for phase distribution in pipes
- Reduces excessive segregation

---

## 4. Comprehensive Decision Tree

```mermaid
flowchart TD
    A[Start: What is your multiphase system?] --> B{Flow Regime?}
    
    B -->|Separated Flow<br/>Sharp interface| C[VOF Method<br/>interFoam]
    B -->|Dispersed Flow<br/>Bubbles/particles| D{Phase Types?}
    
    C --> C1[Key: Interface tracking<br/>α ∈ {0,1}<br/>Include surface tension]
    C1 --> END1[Configure: interFoam]
    
    D -->|Gas-Liquid| E{Calculate Eötvös}
    D -->|Gas-Solid| F{Calculate α_d}
    D -->|Liquid-Solid| G{Calculate α_d}
    
    E -->|Eo < 1<br/>Spherical| H[Drag: Schiller-Naumann<br/>Lift: Saffman-Mei]
    E -->|Eo > 1<br/>Deformed| I[Drag: Tomiyama<br/>Lift: Tomiyama]
    
    F -->|α_d < 0.1<br/>Dilute| J[Drag: Wen-Yu<br/>KTGF: No]
    F -->|α_d 0.1-0.3<br/>Moderate| K[Drag: Wen-Yu/Ergun<br/>KTGF: Optional]
    F -->|α_d > 0.3<br/>Dense| L[Drag: Ergun<br/>KTGF: Yes]
    
    G -->|α_d < 0.3| M[Drag: Schiller-Naumann<br/>Wall lubrication]
    G -->|α_d > 0.3| N[Drag: Schiller-Naumann<br/>KTGF: Optional]
    
    H --> O{Density Ratio}
    I --> O
    J --> O
    K --> O
    L --> O
    M --> O
    N --> O
    
    O -->|ρ_d/ρ_c < 10<br/>Light particles| P[Add Virtual Mass<br/>C_VM = 0.5]
    O -->|ρ_d/ρ_c > 1000<br/>Heavy particles| Q[Skip Virtual Mass]
    O -->|10 < ρ_d/ρ_c < 1000| R[Test C_VM = 0.2]
    
    P --> S{Flow Type}
    Q --> S
    R --> S
    
    S -->|Shear flow<br/>Pipe/boundary layer| T[Add Lift Force]
    S -->|Homogeneous| U[Lift: Optional]
    
    T --> V{Turbulence}
    U --> V
    
    V -->|High turbulence<br/>k/ε > 5%| W[Add Turbulent Dispersion<br/>Burns model]
    V -->|Low turbulence| X[Dispersion: Skip]
    
    W --> END2[Configure: multiphaseEulerFoam]
    X --> END2
    
    style C fill:#e1f5ff
    style H fill:#fff4e1
    style I fill:#fff4e1
    style J fill:#ffe1f5
    style K fill:#ffe1f5
    style L fill:#ffe1f5
    style P fill:#e1ffe1
    style Q fill:#ffe1e1
    style T fill:#e1e1ff
    style W fill:#e1e1ff
```

### 4.1 Quick Reference Table

| Question | Check | Decision |
|----------|-------|----------|
| **Interface tracking?** | Separate phases, sharp boundary | VOF (`interFoam`) |
| **Many collisions?** | α > 0.3, dense phase | KTGF required |
| **Light particles?** | ρ_d/ρ_c < 10 | Virtual Mass (C_VM = 0.5) |
| **Heavy particles?** | ρ_d/ρ_c > 1000 | Skip Virtual Mass |
| **Deformed bubbles?** | Eo > 1 | Tomiyama drag + lift |
| **Spherical particles?** | Eo < 1 | Schiller-Naumann drag |
| **Shear flow?** | Pipe, boundary layer | Include lift |
| **High turbulence?** | Ti > 5% | Turbulent dispersion |
| **Gas-solid dense?** | α > 0.3 | Ergun + KTGF |
| **Gas-solid dilute?** | α < 0.1 | Wen-Yu drag |

---

## 5. OpenFOAM Implementation

### 5.1 phaseProperties Dictionary

```cpp
// constant/phaseProperties

// 1. Define phases
phases
(
    gas
    liquid
);

// 2. Specify dispersed phase properties
gas
{
    // Diameter model
    diameterModel   constant;
    d               0.003;          // [m]
    
    // Optional: Granular temperature for KTGF
    // granularModel   kineticTheory;
    // e               0.9;            // Restitution coefficient
    // alphaMax        0.63;           // Maximum packing
}

liquid
{
    // Continuous phase often empty
}

// 3. Drag model (REQUIRED)
drag
{
    (gas in liquid)
    {
        type    SchillerNaumann;     // Options: Tomiyama, IshiiZuber, etc.
    }
}

// 4. Virtual mass (if ρ_d/ρ_c < 10)
virtualMass
{
    (gas in liquid)
    {
        type    constantCoefficient;
        Cvm     0.5;                 // Typical for bubbles
    }
}

// 5. Lift (if shear flow important)
lift
{
    (gas in liquid)
    {
        type    Tomiyama;            // Options: SaffmanMei, LegendreMagnaudet
    }
}

// 6. Turbulent dispersion (if high turbulence)
turbulentDispersion
{
    (gas in liquid)
    {
        type    Burns;
        Ctd     1.0;                 // Typically 0.1-1.0
    }
}

// 7. Wall lubrication (for pipe flow)
wallLubrication
{
    (gas in liquid)
    {
        type    Antal;
        Cw1     0.01;
        Cw2     0.02;
    }
}
```

### 5.2 fvSolution for Stability

```cpp
// system/fvSolution

solvers
{
    // Coupled solver for multiphase
    "alpha.*"
    {
        solver          GAMG;
        tolerance       1e-8;
        relTol          0.01;
        
        // Smoother for volume fraction
        smoother        GaussSeidel;
    }
    
    p
    {
        solver          GAMG;
        tolerance       1e-7;
        relTol          0.01;
    }
}

// RELAXATION IS CRITICAL FOR STABILITY
relaxationFactors
{
    fields
    {
        p               0.3;         // Pressure: strong relaxation
        "alpha.*"       0.5;         // Volume fraction: moderate
    }
    
    equations
    {
        U               0.7;         // Velocity: mild relaxation
        k               0.6;         // Turbulence: moderate
        epsilon         0.6;
    }
}
```

### 5.3 fvSchemes for Multiphase

```cpp
// system/fvSchemes

ddtSchemes
{
    default         Euler;          // Start with 1st order
}

gradSchemes
{
    default         Gauss linear;
    
    // Limited scheme for α to prevent overshoot
    grad(α)         Gauss vanLeer;
}

divSchemes
{
    // Upwind for stability
    div(phi,α)      Gauss vanLeer;
    div(phi,U)      Gauss upwind;
    
    // MULES for boundedness (VOF)
    div(phirb,α)    Gauss limitedLinearV 1;
}

laplacianSchemes
{
    default         Gauss linear corrected;
}
```

---

## 6. Incremental Complexity Strategy

### 6.1 Step-by-Step Approach

เริ่มจาก model ที่เรียบง่ายที่สุดแล้วค่อยเพิ่มความซับซ้อน

**Step 1: Drag Only (Baseline)**
```cpp
// Test convergence and basic physics
drag { (gas in liquid) { type SchillerNaumann; } }
```

**Step 2: Add Virtual Mass (if light particles)**
```cpp
// Check if stability improves
virtualMass { (gas in liquid) { type constantCoefficient; Cvm 0.5; } }
```

**Step 3: Add Lift (if shear flow)**
```cpp
// Assess wall peaking or phase distribution
lift { (gas in liquid) { type Tomiyama; } }
```

**Step 4: Add Turbulent Dispersion (if high turbulence)**
```cpp
// Improve phase mixing prediction
turbulentDispersion { (gas in liquid) { type Burns; Ctd 1.0; } }
```

**Step 5: Add KTGF (if dense phase, α > 0.3)**
```cpp
// granularModel kineticTheory;
// e 0.9;
```

### 6.2 Validation Checklist

หลังจากแต่ละ step:
- [ ] **Mass balance:** ∑αᵢ = 1 globally
- [ ] **Boundedness:** 0 ≤ α ≤ 1 everywhere
- [ ] **Stability:** Residuals decrease monotonically
- [ ] **Physical sanity:** Velocities, pressure drops reasonable

---

## 7. Common Issues and Solutions

| Issue | Symptom | Solution |
|-------|---------|----------|
| **Divergence** | Residuals explode | Reduce relaxation factors (p: 0.2, α: 0.3) |
| **Overshoot** | α < 0 or α > 1 | Add MULES limiter, reduce timestep |
| **Excessive segregation** | All particles at wall | Add turbulent dispersion |
| **Unphysical oscillations** | Velocity flickering | Check Courant number, add virtual mass |
| **KTGF instability** | α_solid → 0 or 1 | Use `alphaMin` and `alphaMax` limits |
| **Wrong drag regime** | Poor velocity prediction | Recalculate Re_p, switch model |

---

## Key Takeaways

1. **Start Simple, Add Complexity**
   - Drag → Virtual Mass → Lift → Dispersion → KTGF
   - ทดสอบ convergence หลังจากแต่ละ step

2. **Dimensionless Numbers Guide Model Selection**
   - $Re_p$ → drag model
   - $Eo$ → bubble deformation
   - $\alpha_d$ → KTGF requirement
   - $\rho_d/\rho_c$ → virtual mass necessity

3. **Stability Requires Careful Tuning**
   - Relaxation factors: p (0.2-0.3), α (0.3-0.5)
   - Bounded schemes: MULES for VOF, limiters for α
   - Timestep control: Co < 0.5 for multiphase

4. **Physical Insight > Blind Model Addition**
   - Understand what each force represents
   - Add only what your flow regime requires
   - Validate against experimental data when possible

---

## Concept Check

<details>
<summary><b>1. ทำไมไม่ควรใช้ทุก model พร้อมกัน?</b></summary>

เพราะ:
- **Over-modeling** → solver stiffness และ divergence
- **Computational waste** — เสียเวลาคำนวณโดยไม่จำเป็น
- **Potential conflicts** — บาง models อาจ contradict กันเช่น drag + excessive lift
- **Calibration nightmare** — ยากต่อการทดสอบ sensitivity

**Guideline:** เริ่มจาก drag only แล้วค่อยเพิ่มตามที่จำเป็น
</details>

<details>
<summary><b>2. KTGF คืออะไรและใช้เมื่อไหร่?</b></summary>

**Kinetic Theory of Granular Flow** — model ที่อธิบาย **particle-particle collisions** โดย analogize particles เป็น "gas molecules"

**ใช้เมื่อ:**
- $\alpha_d > 0.3$ (dense phase)
- Particle-particle collisions dominate
- Fluidized beds, packed beds, dense slurries

**ไม่ต้องใช้เมื่อ:**
- Dilute flows ($\alpha_d < 0.1$)
- Gas-liquid systems (bubbles don't collide like solids)
</details>

<details>
<summary><b>3. VOF กับ Euler-Euler ต่างกันอย่างไร?</b></summary>

| Aspect | VOF | Euler-Euler |
|--------|-----|-------------|
| **What tracked** | Interface position | Volume fraction field |
| **α resolution** | Sharp (0 or 1) | Diffuse (0 < α < 1) |
| **Use case** | Separated flows | Dispersed flows |
| **Computational cost** | High (interface reconstruction) | Moderate |
| **Example** | Free surface, stratified | Bubbly flow, fluidized bed |

**Rule of thumb:** ถ้า interface แม่นยำสำคัญ → VOF; ถ้า statistics สำคัญ → Euler-Euler
</details>

<details>
<summary><b>4. เมื่อไหร่ควรใช้ Virtual Mass?</b></summary>

**Use when:**
- $\rho_d/\rho_c < 10$ (light particles)
- Accelerating flows (unsteady, rapid changes)
- Bubbly flows with large acceleration

**Skip when:**
- $\rho_d/\rho_c > 1000$ (heavy particles)
- Steady-state flows
- Particles much denser than continuous phase

**Why:** Virtual mass accounts for fluid inertia around accelerating particles — สำคัญเมื่อ particle inertia ไม่ dominate
</details>

<details>
<summary><b>5. Eötvös number บอกอะไร?</b></summary>

$$Eo = \frac{\text{gravitational force}}{\text{surface tension force}} = \frac{g(\rho_c - \rho_d)d_p^2}{\sigma}$$

| $Eo$ | Physical Meaning | Model Implication |
|------|------------------|-------------------|
| < 1 | Surface tension dominates → spherical shape | Schiller-Naumann drag |
| > 1 | Buoyancy deforms interface | Tomiyama/Ishii-Zuber drag |

**Practical use:** Calculate $Eo$ แล้วเลือก drag model ที่ fit bubble shape
</details>

---

## Related Documents

### Hierarchy Overview
- **Module Overview:** [00_Overview.md](00_Overview.md) — ภาพรวมทั้ง module

### Decision Support
- **This File:** [01_Decision_Framework.md](01_Decision_Framework.md) — วิธีการตัดสินใจ (คุณอยู่ที่นี่)
- **Quick Reference:** [02_Gas_Liquid_Systems.md](02_Gas_Liquid_Systems.md) — Gas-liquid เฉพาะ
- **Quick Reference:** [03_Gas_Solid_Systems.md](03_Gas_Solid_Systems.md) — Gas-solid เฉพาะ
- **Reference Lookup:** [04_Parameter_Tables.md](04_Parameter_Tables.md) — ตารางค่า parameters

### Theoretical Foundations
- **Drag Fundamentals:** [../04_INTERPHASE_FORCES/01_DRAG/00_Overview.md](../04_INTERPHASE_FORCES/01_DRAG/00_Overview.md)
- **Lift Fundamentals:** [../04_INTERPHASE_FORCES/02_LIFT/00_Overview.md](../04_INTERPHASE_FORCES/02_LIFT/00_Overview.md)
- **Flow Regimes:** [../01_FUNDAMENTAL_CONCEPTS/01_Flow_Regimes.md](../01_FUNDAMENTAL_CONCEPTS/01_Flow_Regimes.md)