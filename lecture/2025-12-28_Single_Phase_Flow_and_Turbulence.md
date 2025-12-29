# บันทึกบทเรียน: Single-Phase Flow และ Turbulence Modeling

**วันที่:** 28 ธันวาคม 2025

> **สิ่งที่จะได้เรียนรู้:**
> 1. เลือก Solver และตั้งค่าสำหรับ Incompressible Flow
> 2. เข้าใจ SIMPLE, PISO, PIMPLE algorithms
> 3. เลือก Turbulence Model และ Wall Treatment

---

## 1. Single-Phase Flow Solvers

> **กฎทอง:** คำนวณ Re และ Ma ก่อนเลือก Solver เสมอ!

### 1.1 Reynolds Number — Laminar vs Turbulent

$$Re = \frac{UL}{\nu} = \frac{\text{Inertia}}{\text{Viscosity}}$$

| Re Range | Flow Regime | Implications |
|----------|-------------|--------------|
| < 2,300 | Laminar | ไม่ต้องใช้ turbulence model |
| 2,300-4,000 | Transitional | ยากที่สุด ต้องระวัง |
| > 4,000 | Turbulent | ต้องใช้ turbulence model |

### 1.2 Mach Number — Compressibility

$$Ma = \frac{U}{c} = \frac{\text{Flow Speed}}{\text{Sound Speed}}$$

| Ma | Regime | ρ Assumption |
|----|--------|--------------|
| < 0.3 | Incompressible | ρ = constant |
| 0.3-0.8 | Subsonic compressible | ρ = ρ(p,T) |
| > 1 | Supersonic | Shock waves possible |

### 1.3 Solver Selection

```
Re < 2300?
  ├─ Steady → icoFoam (แต่มักใช้ simpleFoam + laminar)
  └─ Transient → icoFoam หรือ pimpleFoam + laminar

Re > 4000?
  ├─ Ma < 0.3? (Incompressible)
  │   ├─ Steady → simpleFoam + kOmegaSST
  │   └─ Transient → pimpleFoam + kOmegaSST
  └─ Ma > 0.3? (Compressible)
      ├─ Steady → rhoSimpleFoam
      └─ Transient → rhoPimpleFoam
```

### 1.4 Common Solvers

| Solver | Type | Use Case |
|--------|------|----------|
| **simpleFoam** | Steady, incompressible | 90% of industrial cases |
| **pimpleFoam** | Transient, incompressible | Unsteady, Co > 1 |
| **pisoFoam** | Transient, incompressible | Accurate time, Co < 1 |
| **icoFoam** | Transient, laminar | Simple, educational |
| **rhoSimpleFoam** | Steady, compressible | Ma > 0.3 |

---

## 2. Pressure-Velocity Coupling

> **ปัญหา:** Momentum ต้องใช้ p, แต่ Continuity ต้องใช้ U → งูกินหาง!

### 2.1 The Problem

```
Momentum Equation:
∂U/∂t + ∇·(UU) = -∇p + ν∇²U
         ↑           ↑
     ต้องรู้ U     ต้องรู้ p

Continuity Equation:
∇·U = 0
  ↑
ต้องรู้ U (แต่ U มาจาก Momentum ที่ต้องรู้ p!)
```

**ไม่มีสมการ p โดยตรง!** → ต้องสร้าง Pressure Poisson Equation

### 2.2 Pressure Poisson Equation

จาก Momentum discretization:

$$\mathbf{u}_P = \mathbf{H}(\mathbf{u}) - \frac{1}{a_P}\nabla p$$

แทนลง Continuity ($\nabla \cdot \mathbf{u} = 0$):

$$\nabla \cdot \left(\frac{1}{a_P}\nabla p\right) = \nabla \cdot \mathbf{H}(\mathbf{u})$$

**นี่คือ Pressure equation!** (Elliptic, symmetric → ใช้ PCG/GAMG)

---

## 3. SIMPLE Algorithm

> **Semi-Implicit Method for Pressure-Linked Equations** — สำหรับ Steady-state

### 3.1 Algorithm Flow

```
┌──────────────────────────────────────────────────────┐
│  SIMPLE Loop (iterate จนกว่า residuals จะต่ำ)       │
│                                                      │
│  1. Momentum Predictor: แก้ U ด้วย p เก่า           │
│          UEqn.solve()                               │
│                                                      │
│  2. Pressure Correction: แก้ p ให้ satisfy ∇·U=0   │
│          pEqn.solve()                               │
│                                                      │
│  3. Velocity Correction: แก้ U ด้วย p ใหม่          │
│          U -= rAU * fvc::grad(p)                   │
│                                                      │
│  4. Under-Relaxation: จำกัดการเปลี่ยนแปลง           │
│          p = α_p * p_new + (1-α_p) * p_old         │
└──────────────────────────────────────────────────────┘
→ Repeat จนกว่า residuals < target
```

### 3.2 Under-Relaxation — ทำไมสำคัญ?

**ปัญหา:** SIMPLE แก้ p และ U แยกกัน — ค่าที่อัปเดตอาจ overshoot

$$\phi^{new} = \alpha \cdot \phi^{computed} + (1-\alpha) \cdot \phi^{old}$$

**กฎสำคัญ:** $\alpha_p + \alpha_U \approx 1$ (บางคนใช้)

| Variable | Stable | Aggressive | ถ้า Diverge |
|----------|--------|------------|-------------|
| p | 0.3 | 0.5 | 0.1-0.2 |
| U | 0.7 | 0.8 | 0.5-0.6 |
| k, ε, ω | 0.7 | 0.8 | 0.4-0.5 |

### 3.3 OpenFOAM Settings

```cpp
// system/fvSolution
SIMPLE
{
    nNonOrthogonalCorrectors 1;  // เพิ่มถ้า mesh เบี้ยว
    
    residualControl
    {
        p       1e-5;
        U       1e-5;
        "(k|epsilon|omega)" 1e-5;
    }
}

relaxationFactors
{
    fields
    {
        p       0.3;    // pressure - relax มาก
    }
    equations
    {
        U       0.7;
        k       0.7;
        epsilon 0.7;
    }
}
```

---

## 4. PISO Algorithm

> **Pressure-Implicit Split-Operator** — สำหรับ Transient (Co < 1)

### 4.1 vs SIMPLE

| Aspect | SIMPLE | PISO |
|--------|--------|------|
| **Type** | Steady-state | Transient |
| **Relaxation** | Required | Not needed |
| **Correctors** | 1 per iteration | nCorrectors per ∆t |
| **Time accuracy** | N/A | 2nd order possible |

### 4.2 Algorithm

```
┌──────────────────────────────────────────────────────┐
│  Per Time Step:                                      │
│                                                      │
│  1. Momentum Predictor: แก้ U^*                     │
│                                                      │
│  2. PISO Corrector Loop (nCorrectors = 2-3):        │
│     ├─ Pressure Equation                            │
│     └─ Velocity Correction                          │
│                                                      │
│  3. Time Step → Next                                │
└──────────────────────────────────────────────────────┘
```

### 4.3 Settings

```cpp
PISO
{
    nCorrectors 2;              // 2-3 สำหรับ Co < 1
    nNonOrthogonalCorrectors 1;
}

// ไม่ต้องใช้ relaxationFactors!
```

### 4.4 Courant Number

$$Co = \frac{U \cdot \Delta t}{\Delta x}$$

**PISO requires:** Co < 1 (typically 0.5-0.9)

```cpp
// system/controlDict
adjustTimeStep  yes;
maxCo           0.9;
```

---

## 5. PIMPLE Algorithm

> **PISO + SIMPLE = PIMPLE** — Best of both worlds

### 5.1 Key Difference

```
PIMPLE = SIMPLE outer loop + PISO inner loop
       = สามารถใช้ ∆t ใหญ่ขึ้น (Co > 1)
```

### 5.2 Algorithm

```
┌──────────────────────────────────────────────────────┐
│  Per Time Step:                                      │
│                                                      │
│  SIMPLE Outer Loop (nOuterCorrectors):              │
│    ├─ Momentum Predictor                            │
│    ├─ PISO Inner Loop (nCorrectors):                │
│    │   ├─ Pressure Equation                        │
│    │   └─ Velocity Correction                      │
│    └─ Under-Relaxation (if not last outer)         │
│                                                      │
│  Time Step → Next                                   │
└──────────────────────────────────────────────────────┘
```

### 5.3 Settings

```cpp
PIMPLE
{
    nOuterCorrectors    2;      // SIMPLE iterations per time step
    nCorrectors         2;      // PISO correctors per outer
    nNonOrthogonalCorrectors 1;
    
    // Optional: stop outer loop if converged
    residualControl
    {
        U   1e-5;
        p   1e-4;
    }
}
```

### 5.4 Comparison

| Algorithm | Courant | Use Case | Cost |
|-----------|---------|----------|------|
| **PISO** | Co < 1 | Accurate transients | Low |
| **PIMPLE** | Co > 1 | Large ∆t transients | Medium |
| **SIMPLE** | Steady | Final solution only | Low |

**Rule of Thumb:**
- ต้องการ time accuracy → PISO
- ต้องการความเร็ว → PIMPLE
- ไม่สน transient → SIMPLE

---

## 6. Rhie-Chow Interpolation

> **ปัญหา Checkerboard:** Collocated grid + Central diff → p oscillation

### 6.1 The Problem

```
OpenFOAM เก็บ p และ U ที่ cell center เดียวกัน (collocated)

ถ้าใช้ central difference:
∂p/∂x|_P ≈ (p_E - p_W) / 2∆x

ไม่มี p_P ในสมการ! → p สามารถ oscillate:
[100, 0, 100, 0, 100, 0] → แต่ ∇p = 0 ทุกที่!
```

### 6.2 The Solution

**Rhie-Chow Interpolation:**

$$U_f = \overline{U} - \overline{\left(\frac{1}{a_P}\right)} \left(\nabla p|_f - \overline{\nabla p}\right)$$

**ผลลัพธ์:** p ต้อง smooth ไม่งั้น face velocity จะผิด → ป้องกัน checkerboard

---

## 7. Turbulence Modeling

> **ปัญหา:** Direct simulation ต้องจับทุก eddy → cost astronomical
> **ทางออก:** Model eddy effects แทน

### 7.1 Turbulence Approaches

```
DNS (Direct Numerical Simulation)
  ↑ แม่นยำที่สุด แต่แพงมาก
  │ Resolve ทุก scale
  │
LES (Large Eddy Simulation)
  │ Resolve large eddies, model small
  │
RANS (Reynolds-Averaged)
  ↓ ถูกที่สุด แต่ approximate
    Model ทุก eddy effects
```

| Approach | Cost | Accuracy | Industrial Use |
|----------|------|----------|----------------|
| **DNS** | Extreme | Exact | Research only |
| **LES** | High | High | Special cases |
| **RANS** | Low | Good | 95%+ of industry |

### 7.2 RANS: Reynolds Averaging

**Reynolds Decomposition:**
$$\phi = \bar{\phi} + \phi'$$

**Averaging:**
$$\overline{\phi' \cdot \psi'} \neq 0$$

**Problem:** Averaged equations มี $\overline{u'_i u'_j}$ → **Reynolds Stress** → ต้อง model!

### 7.3 Eddy Viscosity Hypothesis

$$-\overline{u'_i u'_j} = \nu_t \left(\frac{\partial \bar{u}_i}{\partial x_j} + \frac{\partial \bar{u}_j}{\partial x_i}\right) - \frac{2}{3}k\delta_{ij}$$

**Idea:** Turbulent mixing ≈ enhanced viscosity ($\nu_t$)

**Transport models แก้หา $\nu_t$:**
- k-ε: $\nu_t = C_\mu \frac{k^2}{\varepsilon}$
- k-ω: $\nu_t = \frac{k}{\omega}$

---

## 8. k-ε Model

> **Standard choice for simple flows**

### 8.1 Transport Equations

**Turbulent Kinetic Energy (k):**
$$\frac{\partial k}{\partial t} + \nabla \cdot (\mathbf{u}k) = \nabla \cdot \left[\left(\nu + \frac{\nu_t}{\sigma_k}\right)\nabla k\right] + G_k - \varepsilon$$

**Dissipation Rate (ε):**
$$\frac{\partial \varepsilon}{\partial t} + \nabla \cdot (\mathbf{u}\varepsilon) = \nabla \cdot \left[\left(\nu + \frac{\nu_t}{\sigma_\varepsilon}\right)\nabla \varepsilon\right] + C_1\frac{\varepsilon}{k}G_k - C_2\frac{\varepsilon^2}{k}$$

### 8.2 Eddy Viscosity

$$\nu_t = C_\mu \frac{k^2}{\varepsilon}$$

### 8.3 Standard Coefficients

| Constant | Value |
|----------|-------|
| $C_\mu$ | 0.09 |
| $C_1$ | 1.44 |
| $C_2$ | 1.92 |
| $\sigma_k$ | 1.0 |
| $\sigma_\varepsilon$ | 1.3 |

### 8.4 Pros/Cons

| ✅ Pros | ❌ Cons |
|---------|---------|
| เสถียร, converge เร็ว | แย่ใกล้ผนัง |
| ดีสำหรับ free shear flows | Under-predict separation |
| ใช้ง่าย | Over-predict ν_t |

---

## 9. k-ω SST Model

> **Industry standard — recommended for most cases**

### 9.1 Why SST?

**SST = Shear Stress Transport**
- **Near wall:** ใช้ k-ω (ดีใกล้ผนัง)
- **Free stream:** ใช้ k-ε (เสถียรไกลผนัง)

**Blending Function $F_1$:**
- $F_1 \to 1$: near wall → k-ω behavior
- $F_1 \to 0$: free stream → k-ε behavior

### 9.2 Eddy Viscosity Limiter

$$\nu_t = \frac{a_1 k}{\max(a_1\omega, SF_2)}$$

**ป้องกัน over-prediction ใน adverse pressure gradient**

### 9.3 Pros/Cons

| ✅ Pros | ❌ Cons |
|---------|---------|
| ดีใกล้ผนัง | Cost สูงกว่า k-ε |
| ทำนาย separation ได้ | Sensitive ต่อ mesh |
| Handles adverse pressure gradient | ต้องการ y+ control |

### 9.4 Model Selection

| Flow Type | k-ε | k-ω SST |
|-----------|-----|---------|
| Internal (pipe) | ✓ | ✓ |
| External (airfoil) | ✗ | ✓ |
| Separation | ✗ | ✓ |
| Adverse pressure gradient | ✗ | ✓ |
| Fast computation | ✓ | ✗ |

---

## 10. Wall Treatment and y+

> **y+ = ตัวบอกว่าอยู่ใกล้ผนังแค่ไหน (dimensionless)**

### 10.1 Definition

$$y^+ = \frac{y \cdot u_\tau}{\nu}$$

โดย:
- $y$ = distance from wall
- $u_\tau = \sqrt{\tau_w/\rho}$ = friction velocity
- $\nu$ = kinematic viscosity

### 10.2 Boundary Layer Structure

```
                    │
   Log-law region   │   u+ = (1/κ)ln(y+) + B
   (y+ = 30-300)    │   
────────────────────┼────────────────────
   Buffer layer     │   Transition (ยากที่สุด!)
   (y+ = 5-30)      │   ❌ หลีกเลี่ยงบริเวณนี้
────────────────────┼────────────────────
   Viscous sublayer │   u+ = y+
   (y+ < 5)         │
════════════════════╧════════════════════ Wall
```

### 10.3 Wall Treatment Approaches

| Approach | Target y+ | Mesh | Use Case |
|----------|-----------|------|----------|
| **Wall Functions** | 30-300 | Coarse | Industrial RANS |
| **Wall-Resolved** | ≈ 1 | Fine | High accuracy, LES |
| **Enhanced (Spalding)** | Any | Flexible | When unsure |

### 10.4 Wall Boundary Conditions

**For k-ε with Wall Functions:**
```cpp
// 0/nut
walls { type nutkWallFunction; value uniform 0; }

// 0/k
walls { type kqRWallFunction; value uniform 0; }

// 0/epsilon
walls { type epsilonWallFunction; value uniform 0; }
```

**For k-ω SST with Wall Functions:**
```cpp
// 0/nut
walls { type nutkWallFunction; value uniform 0; }

// 0/k
walls { type kqRWallFunction; value uniform 0; }

// 0/omega
walls { type omegaWallFunction; value uniform 0; }
```

**For Wall-Resolved (Low-Re):**
```cpp
// 0/nut
walls { type nutLowReWallFunction; value uniform 0; }

// 0/k
walls { type fixedValue; value uniform 0; }
```

**Universal (Spalding — works for any y+):**
```cpp
// 0/nut
walls { type nutUSpaldingWallFunction; value uniform 0; }
```

### 10.5 Checking y+

```bash
# Post-process
postProcess -func yPlus -latestTime

# Or runtime
# system/controlDict
functions
{
    yPlus
    {
        type    yPlus;
        libs    (fieldFunctionObjects);
    }
}
```

### 10.6 First Cell Height Calculation

$$\Delta y = \frac{y^+ \cdot \nu}{u_\tau}$$

**Estimate $u_\tau$:**
$$u_\tau \approx U_\infty \sqrt{\frac{C_f}{2}}$$

**Flat plate correlation:**
$$C_f \approx 0.058 \cdot Re_L^{-0.2}$$

---

## 11. Inlet Boundary Conditions for Turbulence

### 11.1 From Intensity and Length Scale

$$k = \frac{3}{2}(UI)^2$$
$$\varepsilon = C_\mu^{3/4}\frac{k^{3/2}}{L_t}$$
$$\omega = \frac{k^{0.5}}{C_\mu^{0.25} L_t}$$

Where:
- $I$ = turbulence intensity (typically 1-10%)
- $L_t$ = turbulent length scale (often 0.07 × hydraulic diameter)

### 11.2 OpenFOAM Settings

```cpp
// 0/k
inlet
{
    type    turbulentIntensityKineticEnergyInlet;
    intensity 0.05;  // 5%
    value   uniform 0.01;
}

// 0/epsilon
inlet
{
    type    turbulentMixingLengthDissipationRateInlet;
    mixingLength 0.01;  // [m]
    value   uniform 0.01;
}

// 0/omega
inlet
{
    type    turbulentMixingLengthFrequencyInlet;
    mixingLength 0.01;
    value   uniform 1;
}
```

---

## 12. Quick Reference

### 12.1 turbulenceProperties

```cpp
simulationType RAS;

RAS
{
    RASModel    kOmegaSST;  // or kEpsilon
    turbulence  on;
    printCoeffs on;
}
```

### 12.2 fvSchemes for Turbulence

```cpp
divSchemes
{
    div(phi,U)      Gauss linearUpwind grad(U);
    div(phi,k)      Gauss upwind;          // Bounded!
    div(phi,epsilon) Gauss upwind;
    div(phi,omega)  Gauss upwind;
}
```

### 12.3 fvSolution for Turbulence

```cpp
solvers
{
    "(k|epsilon|omega)"
    {
        solver      smoothSolver;
        smoother    symGaussSeidel;
        tolerance   1e-8;
        relTol      0.1;
    }
}

relaxationFactors
{
    equations
    {
        k       0.7;
        epsilon 0.7;
        omega   0.7;
    }
}
```

---

## 13. Decision Trees

### Solver Selection

```
คำนวณ Re = UL/ν

Re < 2300?
  → Laminar
      Steady? → simpleFoam + simulationType laminar
      Transient? → pimpleFoam + simulationType laminar

Re > 4000?
  → Turbulent → คำนวณ Ma = U/c
      Ma < 0.3? (Incompressible)
        Steady? → simpleFoam + RANS
        Transient? → pimpleFoam + RANS
      Ma > 0.3? (Compressible)
        → rhoSimpleFoam / rhoPimpleFoam
```

### Turbulence Model Selection

```
Flow มี separation หรือ adverse pressure gradient?
  Yes → k-ω SST (mandatory)
  No →
      ต้องการความเร็ว?
        Yes → k-ε
        No → k-ω SST (safe choice)
```

### Wall Treatment Selection

```
ต้องการความแม่นยำสูง (heat transfer, drag)?
  Yes → Wall-resolved (y+ ≈ 1)
        → nutLowReWallFunction
  No →
      Mesh can maintain y+ = 30-300?
        Yes → Wall functions (nutkWallFunction)
        No → Enhanced (nutUSpaldingWallFunction)
```

---

## 14. สรุปท้ายบท

### หลักการ 3 ข้อจำง่าย

1. **SIMPLE = Steady, PIMPLE = Transient**
   - SIMPLE ต้องมี under-relaxation
   - PIMPLE/PISO ไม่ต้อง (แต่ช่วยได้)

2. **k-ω SST = Safe Choice**
   - ใช้ได้เกือบทุก flow type
   - ดีกว่า k-ε ใน separation/external

3. **y+ ต้องถูกต้อง**
   - Wall functions: 30-300
   - Wall-resolved: ≈ 1
   - หลีกเลี่ยง 5-30!

---

*"Turbulence is the last unsolved problem of classical physics" — Richard Feynman*

---

## 15. 🧠 Advanced Concept Check

### Level 1: Foundation

<details>
<summary><b>Q1: ทำไม SIMPLE ต้องใช้ Under-Relaxation แต่ PISO ไม่ต้อง?</b></summary>

**คำตอบ:**

**SIMPLE (Steady-state):**
- แก้ Momentum และ Pressure แยกกัน
- ค่าที่อัปเดตมาจาก guess ที่อาจไกลจาก solution มาก
- Without relaxation: oscillate หรือ diverge

**PISO (Transient):**
- แต่ละ time step เริ่มจากค่าที่ใกล้ solution (จาก time step ก่อน)
- Multiple pressure corrections ใน 1 time step ช่วย converge
- ∆t เล็กพอ → ค่าเปลี่ยนน้อย → ไม่ต้อง relax

**Analogy:**
- SIMPLE = กระโดดหา target (ต้องจำกัดระยะ)
- PISO = เดินหา target (ก้าวเล็กๆ หลายก้าว)

</details>

<details>
<summary><b>Q2: Pressure Poisson Equation มาจากไหน?</b></summary>

**คำตอบ:**

**Step 1: Discretized Momentum**
$$a_P \mathbf{u}_P = \mathbf{H}(\mathbf{u}) - \nabla p$$

**Step 2: Solve for velocity**
$$\mathbf{u}_P = \frac{\mathbf{H}(\mathbf{u})}{a_P} - \frac{1}{a_P}\nabla p$$

**Step 3: Apply Continuity** ($\nabla \cdot \mathbf{u} = 0$)
$$\nabla \cdot \left(\frac{\mathbf{H}(\mathbf{u})}{a_P}\right) = \nabla \cdot \left(\frac{1}{a_P}\nabla p\right)$$

**Result: Pressure Poisson Equation**
$$\nabla \cdot \left(\frac{1}{a_P}\nabla p\right) = \nabla \cdot \mathbf{H}(\mathbf{u})$$

**OpenFOAM Code:**
```cpp
volScalarField rAU = 1.0/UEqn.A();      // 1/a_P
volVectorField HbyA = rAU*UEqn.H();      // H(u)/a_P
fvm::laplacian(rAU, p) == fvc::div(HbyA) // Pressure eq
```

</details>

<details>
<summary><b>Q3: ทำไม α_p ต้องน้อยกว่า α_U?</b></summary>

**คำตอบ:**

**Coupling Strength:**
- p กับ U coupled อย่างแรง
- เปลี่ยน p → เปลี่ยน ∇p → เปลี่ยน U ทันที
- เปลี่ยน U → เปลี่ยน flux → เปลี่ยน p ทันที

**Stability Analysis:**
- ถ้า relax p มาก (α_p สูง) → U เปลี่ยนมาก → p เปลี่ยนมาก → oscillate
- ต้องจำกัด p มากกว่า U

**Typical Values:**
- α_p = 0.3, α_U = 0.7
- บางคนใช้กฎ: α_p + α_U ≈ 1

</details>

### Level 2: Deep Understanding

<details>
<summary><b>Q4: k-ε ทำนาย Separation แย่ เพราะอะไร?</b></summary>

**คำตอบ:**

**หลักการ:**
k-ε over-predict $\nu_t$ ใกล้ผนัง

**สาเหตุ:**
1. **ε Equation ใกล้ผนัง:** Wall ขัดขวาง large eddies → ε สูงกว่าจริง → k/ε underestimate
2. **จริงๆ:** near-wall k ต้องลดลงเร็วกว่าที่ k-ε predict
3. **ผลลัพธ์:** $\nu_t = C_\mu k^2/\varepsilon$ → over-predicted

**ผลกระทบ:**
- High $\nu_t$ → flow เกาะผิวได้ดีเกินจริง
- Separation ถูก delay หรือ under-predicted
- Recirculation zone สั้นกว่าจริง

**ทำไม k-ω SST ดีกว่า:**
- Near wall: ใช้ k-ω ซึ่งไม่ต้องกำหนด ε ที่ผนัง
- Eddy viscosity limiter ป้องกัน over-prediction

</details>

<details>
<summary><b>Q5: อธิบาย "Blending Function" ใน k-ω SST</b></summary>

**คำตอบ:**

**ปัญหา:**
- k-ω ดีใกล้ผนัง แต่ sensitive ต่อ freestream values
- k-ε ดีใน freestream แต่แย่ใกล้ผนัง

**SST Solution: Blending Function $F_1$**

$$\phi_{SST} = F_1 \cdot \phi_{k-\omega} + (1-F_1) \cdot \phi_{k-\epsilon}$$

**$F_1$ Behavior:**
```
Distance from wall →

F₁ = 1.0 ──┐
           │   k-ω behavior
           │
F₁ = 0.5 ──┼── Transition
           │
F₁ = 0.0 ──┘   k-ε behavior (transformed)
```

**$F_1$ Definition:**
$$F_1 = \tanh\left(\arg_1^4\right)$$

โดย $\arg_1$ ขึ้นกับ:
- $y$ (wall distance)
- $k$, $\omega$
- $\nu$, $\nu_t$

</details>

<details>
<summary><b>Q6: ทำไมต้องหลีกเลี่ยง y+ = 5-30?</b></summary>

**คำตอบ:**

**Boundary Layer Structure:**

| Region | y+ | Profile | Model Assumption |
|--------|-----|---------|------------------|
| Viscous sublayer | < 5 | $u^+ = y^+$ | Linear ✓ |
| Buffer layer | 5-30 | Transition | ❌ ไม่มีสูตร! |
| Log-law | 30-300 | $u^+ = \frac{1}{\kappa}\ln y^+ + B$ | Log-law ✓ |

**Buffer Layer Problem:**
- ไม่มีสูตร analytical ที่ถูกต้อง
- Linear ก็ผิด, Log-law ก็ผิด
- Wall functions จะให้ $\tau_w$ ผิดมาก

**Solutions:**
1. **Wall functions:** ตั้ง y+ = 30-300 (อยู่ใน log-law)
2. **Wall-resolved:** ตั้ง y+ < 1 (อยู่ใน viscous sublayer)
3. **Spalding WF:** ใช้ unified formula ที่ครอบคลุมทุก region

</details>

### Level 3: Expert

<details>
<summary><b>Q7: nCorrectors vs nOuterCorrectors ใน PIMPLE ต่างกันอย่างไร?</b></summary>

**คำตอบ:**

**Structure:**
```
Per Time Step:
  └─ nOuterCorrectors (SIMPLE-like outer loop)
       └─ nCorrectors (PISO-like inner loop)
```

**nCorrectors (Inner Loop):**
- จำนวน pressure corrections ต่อ outer iteration
- ช่วยให้ satisfy continuity
- Typical: 2-3

**nOuterCorrectors (Outer Loop):**
- จำนวน SIMPLE-like iterations ต่อ time step
- ช่วยให้ใช้ ∆t ใหญ่ได้ (Co > 1)
- With relaxation (except last outer)
- Typical: 1-5

**Settings:**

| Co | nOuter | nCorrector | Analogy |
|----|--------|------------|---------|
| < 0.5 | 1 | 2 | Pure PISO |
| 0.5-2 | 2-3 | 2 | Typical PIMPLE |
| > 2 | 3-5 | 2-3 | Strong PIMPLE |

</details>

<details>
<summary><b>Q8: "Realizability" ใน k-ε Realizable หมายถึงอะไร?</b></summary>

**คำตอบ:**

**Problem with Standard k-ε:**

Reynolds Stress มี physical constraint:
$$\overline{u'^2} \geq 0, \quad \overline{v'^2} \geq 0, \quad \overline{w'^2} \geq 0$$

**Physical Realizability:**
$$C_\mu \frac{k^2}{\varepsilon} < \frac{2k}{3S}$$

Where S = strain rate magnitude

**Standard k-ε:**
$C_\mu = 0.09$ = constant → อาจ violate realizability ใน high strain

**Realizable k-ε:**
$$C_\mu = \frac{1}{A_0 + A_s \frac{kS}{\varepsilon}}$$

$C_\mu$ ลดลงเมื่อ strain สูง → ป้องกัน unphysical $\nu_t$

**Benefits:**
- ดีกว่าสำหรับ rotating flows
- ดีกว่าสำหรับ streamline curvature
- ไม่ produce negative normal stresses

</details>

<details>
<summary><b>Q9: LES ต่างจาก RANS อย่างไรในระดับ fundamental?</b></summary>

**คำตอบ:**

**RANS (Reynolds-Averaged):**
- **Average:** Time average
- **Result:** $\bar{\phi}$ = mean field
- **Model:** ทุก turbulent scales
- **Cost:** Low (steady solution possible)

**LES (Large Eddy Simulation):**
- **Filter:** Spatial filter (grid-based)
- **Result:** $\tilde{\phi}$ = filtered (resolved) field
- **Model:** เฉพาะ sub-grid scales
- **Cost:** High (must be unsteady)

**Mathematical Difference:**

| Aspect | RANS | LES |
|--------|------|-----|
| Decomposition | $\phi = \bar{\phi} + \phi'$ | $\phi = \tilde{\phi} + \phi''$ |
| Averaging | Time | Spatial |
| $\overline{\bar{\phi}}$ | $= \bar{\phi}$ | $\neq \tilde{\phi}$ |
| Modeled term | Reynolds Stress | SGS Stress |

**Key Implication:**
- RANS: เฉลี่ยหมด → steady solution ได้
- LES: เฉลี่ย spatial → ยังเหลือ time variation → ต้อง transient

**Grid Requirement:**
- RANS: Grid Independence (mesh ละเอียดพอ = ผลเหมือนกัน)
- LES: Grid = Filter! (mesh ละเอียด = resolve มากขึ้น = ผลต่าง!)

</details>

---

## 16. ⚡ Advanced Hands-on Challenges

### Challenge 1: SIMPLE vs PIMPLE Comparison (⭐⭐⭐)

**วัตถุประสงค์:** เห็นความแตกต่างระหว่าง algorithms

**Setup:**
```bash
cp -r $FOAM_TUTORIALS/incompressible/simpleFoam/pitzDaily pitzDaily_simple
cp -r pitzDaily_simple pitzDaily_pimple
```

**Tasks:**
1. รัน simpleFoam → บันทึกจำนวน iterations ถึง convergence
2. แปลง pitzDaily_pimple เป็น transient:
   - ใช้ pimpleFoam
   - ∆t = 0.001, endTime = 0.5
3. เปรียบเทียบ:
   - Wall clock time
   - Final velocity profile
   - ผลลัพธ์ต่างกันไหม?

---

### Challenge 2: Turbulence Model Comparison (⭐⭐⭐⭐)

**วัตถุประสงค์:** เห็นความแตกต่างระหว่าง models

**Setup:**
```bash
cp -r $FOAM_TUTORIALS/incompressible/simpleFoam/motorBike motorBike_kE
cp -r motorBike_kE motorBike_SST
```

**Tasks:**
1. รัน motorBike_kE ด้วย kEpsilon
2. รัน motorBike_SST ด้วย kOmegaSST
3. เปรียบเทียบ:
   - Cd, Cl
   - Separation point
   - Wake structure

---

### Challenge 3: y+ Investigation (⭐⭐⭐⭐)

**วัตถุประสงค์:** เข้าใจ y+ impact on results

**Setup:**
สร้าง channel flow case (หรือใช้ tutorial)

**Tasks:**
1. สร้าง 3 mesh levels:
   - y+ ≈ 1 (wall-resolved)
   - y+ ≈ 30 (wall function range)
   - y+ ≈ 100 (wall function range)

2. รันแต่ละ case ด้วย:
   - Wall-resolved: nutLowReWallFunction
   - Wall function: nutkWallFunction

3. Plot velocity profile และเปรียบเทียบกับ log-law

---

### Challenge 4: Relaxation Factor Sensitivity (⭐⭐⭐)

**วัตถุประสงค์:** เข้าใจ stability/convergence tradeoff

**Setup:**
ใช้ simpleFoam tutorial ใดก็ได้

**Tasks:**
1. รันด้วย conservative: α_p = 0.1, α_U = 0.3
2. รันด้วย default: α_p = 0.3, α_U = 0.7
3. รันด้วย aggressive: α_p = 0.5, α_U = 0.9

4. เปรียบเทียบ:
   - อันไหน diverge?
   - อันไหน converge เร็วที่สุด?
   - Residual plot ต่างกันอย่างไร?

---

### Challenge 5: Inlet Turbulence Sensitivity (⭐⭐⭐⭐⭐)

**วัตถุประสงค์:** เข้าใจ inlet BC impact

**Setup:**
ใช้ backward facing step หรือ pipe flow

**Tasks:**
1. ทดสอบ turbulence intensity: 1%, 5%, 10%
2. ทดสอบ length scale: 0.001m, 0.01m, 0.1m

3. วิเคราะห์:
   - ผลลัพธ์เปลี่ยนมากไหม?
   - Parameter ไหน sensitive กว่า?
   - ที่ไหนในโดเมนที่เห็นผลต่าง?

---

## 17. ❌ Common Mistakes

### Mistake 1: ใช้ SIMPLE กับ Transient

```cpp
// ❌ WRONG - SIMPLE ไม่มี time accuracy
application simpleFoam;  // for transient problem!

// ✅ CORRECT
application pimpleFoam;  // for transient
```

---

### Mistake 2: ลืม Under-Relaxation กับ SIMPLE

```cpp
// ❌ WRONG - ไม่มี relaxation
relaxationFactors
{
    // empty!
}

// ✅ CORRECT
relaxationFactors
{
    fields { p 0.3; }
    equations { U 0.7; k 0.7; epsilon 0.7; }
}
```

---

### Mistake 3: y+ ผิดช่วง

```bash
# ❌ WRONG - y+ = 10 (buffer layer!)
# Using wall functions but y+ in buffer layer

# ✅ CORRECT
# Wall functions: y+ = 30-300
# Wall-resolved: y+ < 1
```

---

### Mistake 4: ใช้ upwind กับ U (เมื่อต้องการความแม่นยำ)

```cpp
// ❌ WRONG for production - too diffusive
div(phi,U) Gauss upwind;

// ✅ CORRECT
div(phi,U) Gauss linearUpwind grad(U);
```

---

### Mistake 5: ใช้ linear กับ k, ε, ω

```cpp
// ❌ WRONG - can go negative!
div(phi,k)      Gauss linear;
div(phi,epsilon) Gauss linear;

// ✅ CORRECT - bounded
div(phi,k)      Gauss upwind;
div(phi,epsilon) Gauss upwind;
```

---

### Mistake 6: Co > 1 กับ PISO

```cpp
// ❌ WRONG - Co > 1 but using PISO
PISO { nCorrectors 2; }

// ✅ CORRECT - use PIMPLE for Co > 1
PIMPLE
{
    nOuterCorrectors 2;
    nCorrectors 2;
}
```

---

### Mistake 7: ไม่กำหนด nut ที่ inlet

```cpp
// ❌ WRONG - nut undefined at inlet
// (error or zero nut)

// ✅ CORRECT
inlet
{
    type    calculated;
    value   uniform 0;
}
```

---

### Mistake 8: Wall BC ไม่ตรงกับ model

```cpp
// ❌ WRONG - k-ω model but epsilon BC
omega
{
    type epsilonWallFunction;  // Wrong variable!
}

// ✅ CORRECT
omega
{
    type omegaWallFunction;
}
```

---

## 18. 🔗 เชื่อมโยงกับ Repository

| หัวข้อ | ไฟล์ใน Repository |
|--------|-------------------|
| **Solvers Overview** | `MODULE_03/01_INCOMPRESSIBLE_FLOW_SOLVERS/` |
| **P-V Coupling** | `MODULE_03/02_PRESSURE_VELOCITY_COUPLING/` |
| **Turbulence** | `MODULE_03/03_TURBULENCE_MODELING/` |
| **Heat Transfer** | `MODULE_03/04_HEAT_TRANSFER/` |
| **Practical Cases** | `MODULE_03/05_PRACTICAL_APPLICATIONS/` |
| **V&V** | `MODULE_03/06_VALIDATION_AND_VERIFICATION/` |
| **fvc/fvm** | `MODULE_05/10_VECTOR_CALCULUS/` |

---

*"The turbulence modeling is not about getting the exact answer, but about getting a useful answer efficiently"*
