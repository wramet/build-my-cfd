# บันทึกบทเรียน: Multiphase Flow — จาก VOF สู่ Euler-Euler

**วันที่:** 28 ธันวาคม 2025

> **สิ่งที่จะได้เรียนรู้:**
> 1. เลือก Solver และ Approach ที่ถูกต้องสำหรับ Multiphase
> 2. เข้าใจ VOF Method และ interFoam
> 3. เข้าใจ Euler-Euler และ Interphase Forces
> 4. ตั้งค่า Multiphase Case ได้อย่างถูกต้อง

---

## 1. เมื่อของไหลเดียวไม่เพียงพอ

> **"When one fluid is not enough"**

### 1.1 Multiphase ต่างกับ Single-Phase อย่างไร?

```
Single-Phase:
    1 ชุดสมการ → 1 ความเร็ว → 1 ความดัน
    ง่าย แต่จำกัด

Multiphase:
    หลายเฟส → Interface? → Forces? → Closure?
    ซับซ้อน แต่ทรงพลัง
```

### 1.2 ความท้าทายของ Multiphase

| Challenge | Description | ผลกระทบ |
|-----------|-------------|---------|
| **Property Jump** | ρ, μ เปลี่ยนที่ interface | Numerical instability |
| **Interface Tracking** | ต้องรู้ตำแหน่ง interface | Accuracy depends on method |
| **Closure Models** | ต้องมี models สำหรับ forces | Results depend on model choice |
| **Time Scale** | Interface เคลื่อนที่เร็ว | ต้องใช้ Δt เล็ก (Co < 1) |

### 1.3 Applications

| อุตสาหกรรม | Application | ทำไม Multiphase? |
|------------|-------------|------------------|
| **Marine** | Ship resistance | คลื่น, การกระเซ็น |
| **Oil & Gas** | Slug flow | ก๊าซ-น้ำมันสลับกัน |
| **Chemical** | Bubble column | การผสม, mass transfer |
| **Power** | Fluidized bed | Particle-gas interaction |
| **Automotive** | Fuel sloshing | การกระฉอกในถัง |

---

## 2. วิธีเลือก Approach: VOF vs Euler-Euler

> **คำถามแรกเสมอ: Interface ชัดไหม?**

### 2.1 Decision Tree

```
Interface แบบไหน?
│
├─► Sharp (ชัดเจน) = VOF
│   ตัวอย่าง: น้ำ-อากาศ, dam break, waves
│   Solver: interFoam, multiphaseInterFoam
│
└─► Dispersed (กระจาย) = Euler-Euler
    ตัวอย่าง: ฟองอากาศ, fluidized bed
    Solver: twoPhaseEulerFoam, multiphaseEulerFoam
```

### 2.2 Comparison

| Aspect | VOF | Euler-Euler |
|--------|-----|-------------|
| **Interface** | Resolved (cell level) | Averaged (sub-grid) |
| **Equations** | 1 momentum equation | N momentum equations |
| **Closures** | ไม่ต้อง (ยกเว้น surface tension) | ต้องมี drag, lift, etc. |
| **Cost** | สูง (fine mesh) | ปานกลาง |
| **Best for** | Free surface | Dispersed flows |

### 2.3 Examples

| Scenario | Approach | Solver |
|----------|----------|--------|
| Dam break | VOF | `interFoam` |
| Ship hull | VOF | `interFoam` |
| Bubble column | Euler-Euler | `multiphaseEulerFoam` |
| Fluidized bed | Euler-Euler + KTGF | `multiphaseEulerFoam` |
| Spray | Lagrangian | `sprayFoam` |

---

## 3. VOF Method — Volume of Fluid

> **Physical Analogy:** ภาพถ่ายดิจิทัลของแก้วน้ำ
> - Pixel = Mesh cell
> - สีดำ = น้ำ (α = 1)
> - สีขาว = อากาศ (α = 0)
> - สีเทา = Interface (0 < α < 1)

### 3.1 Phase Fraction (α)

$$\alpha = \frac{V_{water}}{V_{cell}}$$

| α | Meaning |
|---|---------|
| 1.0 | 100% น้ำ |
| 0.5 | Interface (50% น้ำ) |
| 0.0 | 100% อากาศ |

### 3.2 The α Transport Equation

$$\frac{\partial \alpha}{\partial t} + \nabla \cdot (\mathbf{U} \alpha) + \underbrace{\nabla \cdot (\mathbf{U}_r \alpha (1-\alpha))}_{\text{Compression term}} = 0$$

**Compression Term:**
- $\alpha(1-\alpha) = 0$ เมื่อ α = 0 หรือ α = 1
- $\alpha(1-\alpha) = 0.25$ สูงสุดเมื่อ α = 0.5 (interface)
- เทอมนี้ **บีบ interface ให้คมชัด**

### 3.3 Mixture Properties

$$\rho = \alpha \rho_{water} + (1-\alpha) \rho_{air}$$
$$\mu = \alpha \mu_{water} + (1-\alpha) \mu_{air}$$

**ตัวอย่าง:** ที่ interface (α = 0.5)
$$\rho = 0.5 \times 1000 + 0.5 \times 1 = 500.5 \text{ kg/m}^3$$

### 3.4 Single Momentum Equation

$$\frac{\partial (\rho \mathbf{U})}{\partial t} + \nabla \cdot (\rho \mathbf{U} \mathbf{U}) = -\nabla p_{rgh} - \mathbf{g} \cdot \mathbf{x} \nabla \rho + \nabla \cdot \boldsymbol{\tau} + \mathbf{F}_{st}$$

**Note:** ใช้ $p_{rgh} = p - \rho \mathbf{g} \cdot \mathbf{x}$ แทน $p$ → ตั้ง BC ง่ายขึ้น

### 3.5 Surface Tension (Continuum Surface Force)

$$\mathbf{F}_{st} = \sigma \kappa \nabla \alpha$$

โดย $\kappa = -\nabla \cdot \left(\frac{\nabla \alpha}{|\nabla \alpha|}\right)$ = curvature

---

## 4. MULES Algorithm — ทำไม Interface ถึงคม?

> **MULES = Multidimensional Universal Limiter with Explicit Solution**

### 4.1 ปัญหา: Numerical Diffusion

```
Without compression:
[1][1][0.8][0.5][0.3][0.1][0][0]  ← Interface เบลอ (หนา 5 cells!)

With MULES + cAlpha:
[1][1][1][0.5][0][0][0][0]  ← Interface คม (หนา 1-2 cells)
```

### 4.2 cAlpha Parameter

```cpp
// system/fvSolution
solvers
{
    "alpha.*"
    {
        nAlphaCorr      2;      // correction sweeps
        nAlphaSubCycles 2;      // subcycles per time step
        cAlpha          1;      // compression coefficient
    }
}
```

| cAlpha | Effect |
|--------|--------|
| 0 | No compression → diffuse |
| 1 | Standard compression |
| 1.5+ | Aggressive → may oscillate |

### 4.3 nAlphaSubCycles

```cpp
// ทำไมต้อง subcycle?
// Co สำหรับ α อาจสูงกว่า Co รวม
// subcycle = แก้ α หลายครั้งใน 1 time step

nAlphaSubCycles 2;  // default, OK for most cases
maxAlphaCo      0.5; // ควบคุม Courant เฉพาะ α
```

---

## 5. interFoam Case Setup

### 5.1 Directory Structure

```
case/
├── constant/
│   ├── transportProperties  ← ρ, ν, σ
│   ├── turbulenceProperties ← RAS/LES
│   └── g                    ← gravity
├── system/
│   ├── controlDict          ← time, adjustTimeStep
│   ├── fvSchemes            ← divSchemes for alpha
│   ├── fvSolution           ← MULES settings
│   └── setFieldsDict        ← initial α distribution
└── 0/
    ├── alpha.water          ← volume fraction
    ├── p_rgh                ← pressure (minus hydrostatic)
    └── U                    ← velocity
```

### 5.2 transportProperties

```cpp
phases (water air);

water
{
    transportModel  Newtonian;
    nu              [0 2 -1 0 0 0 0] 1e-06;    // m²/s
    rho             [1 -3 0 0 0 0 0] 1000;     // kg/m³
}

air
{
    transportModel  Newtonian;
    nu              [0 2 -1 0 0 0 0] 1.48e-05;
    rho             [1 -3 0 0 0 0 0] 1;
}

sigma           [1 0 -2 0 0 0 0] 0.07;  // N/m (surface tension)
```

### 5.3 setFieldsDict — กำหนดค่าเริ่มต้น

```cpp
defaultFieldValues
(
    volScalarFieldValue alpha.water 0  // เริ่มจากอากาศ
);

regions
(
    boxToCell  // สร้างกล่องน้ำ
    {
        box (0 0 0) (0.5 0.5 1);  // (x0,y0,z0) (x1,y1,z1)
        fieldValues (volScalarFieldValue alpha.water 1);
    }
);
```

```bash
# รัน setFields
setFields
```

### 5.4 fvSchemes

```cpp
divSchemes
{
    div(rhoPhi,U)   Gauss linearUpwind grad(U);
    div(phi,alpha)  Gauss vanLeer;  // bounded for α
    div(phirb,alpha) Gauss linear;  // compression flux
}

gradSchemes
{
    default         Gauss linear;
}

laplacianSchemes
{
    default         Gauss linear corrected;
}
```

### 5.5 controlDict — Adaptive Time Stepping

```cpp
application     interFoam;

startTime       0;
endTime         5;
deltaT          0.001;  // initial

adjustTimeStep  yes;
maxCo           0.5;    // overall Courant
maxAlphaCo      0.5;    // Courant for α
maxDeltaT       0.01;   // maximum Δt
```

---

## 6. Euler-Euler Method

> **Core Concept:** ทั้งสองเฟสเป็น "Interpenetrating Continua" — ซ้อนทับกันได้

### 6.1 Conceptual Difference

```
VOF (Sharp Interface):
┌─────────────────────┐
│ Water │ Air         │  ← Interface ชัด
└─────────────────────┘

Euler-Euler (Dispersed):
┌─────────────────────┐
│ ○ ○ ○ ○ ○ ○ ○ ○ ○ │  ← Bubbles กระจาย
│ Water + Air mixed   │
└─────────────────────┘
```

### 6.2 Governing Equations (per phase k)

**Continuity:**
$$\frac{\partial (\alpha_k \rho_k)}{\partial t} + \nabla \cdot (\alpha_k \rho_k \mathbf{u}_k) = \dot{m}_k$$

**Momentum:**
$$\frac{\partial (\alpha_k \rho_k \mathbf{u}_k)}{\partial t} + \nabla \cdot (\alpha_k \rho_k \mathbf{u}_k \mathbf{u}_k) = -\alpha_k \nabla p + \nabla \cdot \boldsymbol{\tau}_k + \mathbf{M}_k$$

**Constraint:**
$$\sum_k \alpha_k = 1$$

### 6.3 Key Differences from Single-Phase

| Aspect | Single-Phase | Euler-Euler |
|--------|--------------|-------------|
| Velocity | 1 field (U) | N fields (U.air, U.water) |
| Volume fraction | — | α.air, α.water |
| Pressure | 1 field | 1 shared field |
| Coupling | — | Interphase forces M_k |

---

## 7. Interphase Forces

> **แรงที่เชื่อม momentum equations ของแต่ละเฟส**

### 7.1 Force Summary

$$\mathbf{M}_{d \to c} = \mathbf{F}_D + \mathbf{F}_L + \mathbf{F}_{VM} + \mathbf{F}_{TD}$$

| Force | Physical Meaning |
|-------|------------------|
| **Drag (F_D)** | ต้านการเคลื่อนที่สัมพัทธ์ |
| **Lift (F_L)** | แรงในทิศตั้งฉากกับการไหล |
| **Virtual Mass (F_VM)** | Inertia ของ fluid รอบ particle |
| **Turbulent Dispersion (F_TD)** | การกระจายจาก turbulence |

### 7.2 Drag — แรงที่สำคัญที่สุด!

$$\mathbf{F}_D = K (\mathbf{u}_c - \mathbf{u}_d)$$

$$K = \frac{3}{4} C_D \frac{\alpha_c \alpha_d \rho_c}{d} |\mathbf{u}_r|$$

**Drag Coefficient Model Selection:**

| Condition | Model |
|-----------|-------|
| Spherical bubbles (Re < 1000) | `SchillerNaumann` |
| Deformed bubbles (Eo > 1) | `IshiiZuber` |
| Contaminated (dirty water) | `Tomiyama` |
| Dilute gas-solid | `WenYu` |
| Dense gas-solid | `GidaspowErgunWenYu` |

### 7.3 Key Dimensionless Numbers

$$Re = \frac{\rho_c |\mathbf{u}_r| d}{\mu_c}$$

$$Eo = \frac{g(\rho_c - \rho_d) d^2}{\sigma}$$

| Eo | Bubble Shape |
|----|--------------|
| < 1 | Spherical |
| 1-10 | Ellipsoidal |
| > 10 | Cap/Wobbling |

### 7.4 Lift Force

$$\mathbf{F}_L = -C_L \alpha_d \rho_c (\mathbf{u}_r \times (\nabla \times \mathbf{u}_c))$$

**Tomiyama Lift:**
- $C_L > 0$ สำหรับ small bubbles → move toward wall
- $C_L < 0$ สำหรับ large bubbles → move toward center

### 7.5 Virtual Mass

$$\mathbf{F}_{VM} = C_{VM} \alpha_d \rho_c \left(\frac{D\mathbf{u}_c}{Dt} - \frac{D\mathbf{u}_d}{Dt}\right)$$

- $C_{VM} = 0.5$ สำหรับ isolated spheres
- สำคัญเมื่อ $\rho_c >> \rho_d$ (gas-liquid)

---

## 8. multiphaseEulerFoam Configuration

### 8.1 phaseProperties

```cpp
type            basicMultiphaseSystem;

phases          (air water);

air
{
    type            purePhaseModel;
    diameterModel   constant;
    d               3e-3;           // 3 mm bubbles
    residualAlpha   1e-6;
}

water
{
    type            purePhaseModel;
    diameterModel   constant;
    d               1e-4;
    residualAlpha   1e-6;
}

blending
{
    default { type linear; minFullyContinuousAlpha.air 0.3; }
}
```

### 8.2 Interphase Force Configuration

```cpp
drag
{
    (air in water)
    {
        type            SchillerNaumann;
        residualRe      1e-3;
    }
}

virtualMass
{
    (air in water)
    {
        type            constantCoefficient;
        Cvm             0.5;
    }
}

lift
{
    (air in water)
    {
        type            Tomiyama;
    }
}
```

---

## 9. Model Selection Guidelines

### 9.1 Golden Rule

> **เริ่มจาก Simple → ค่อยเพิ่ม Complexity**

```
Step 1: Drag only (ต้อง stable ก่อน!)
        ↓
Step 2: + Virtual Mass (ถ้า gas-liquid)
        ↓
Step 3: + Lift (ถ้า shear flow สำคัญ)
        ↓
Step 4: + Turbulent Dispersion (ถ้า high turbulence)
```

### 9.2 Decision Framework

```
Interface ชัดไหม?
├─► ชัด (free surface) → VOF (interFoam)
│
└─► กระจาย (dispersed)
    │
    ├─► Gas-Liquid?
    │   ├─► มี α_d < 0.1? → อาจใช้ Lagrangian
    │   └─► มี α_d > 0.1? → Euler-Euler (multiphaseEulerFoam)
    │
    └─► Gas-Solid?
        ├─► α_solid < 0.3? → Standard Euler-Euler
        └─► α_solid > 0.3? → Need KTGF (granular kinetics)
```

### 9.3 Numerical Settings

```cpp
// system/fvSolution
PIMPLE
{
    nOuterCorrectors    3;
    nCorrectors         2;
    nAlphaSubCycles     2;
}

relaxationFactors
{
    fields
    {
        p               0.3;
        "alpha.*"       0.7;
    }
    equations
    {
        U               0.7;
    }
}
```

---

## 10. Quick Reference Tables

### 10.1 Solver Selection

| Flow Type | Interface | Solver |
|-----------|-----------|--------|
| Dam break | Sharp | `interFoam` |
| Waves | Sharp | `interFoam` |
| Bubble column | Dispersed | `multiphaseEulerFoam` |
| Fluidized bed | Dispersed | `multiphaseEulerFoam` + KTGF |
| Spray | Lagrangian | `sprayFoam` |

### 10.2 Drag Model Selection

| System | Condition | Model |
|--------|-----------|-------|
| Gas-Liquid | Spherical | `SchillerNaumann` |
| Gas-Liquid | Deformed (Eo > 1) | `IshiiZuber` |
| Gas-Liquid | Contaminated | `Tomiyama` |
| Gas-Solid | Dilute | `WenYu` |
| Gas-Solid | Dense | `GidaspowErgunWenYu` |

### 10.3 Interphase Force Requirements

| System | Drag | VM | Lift | TD |
|--------|------|-----|------|-----|
| Gas-Liquid (bubbly) | ✓ | ✓ | Often | Sometimes |
| Liquid-Liquid | ✓ | Rarely | Rarely | Rarely |
| Gas-Solid | ✓ | No | No | Sometimes |

---

## 11. 🧠 Advanced Concept Check

### Level 1: Fundamentals

<details>
<summary><b>Q1: ทำไม VOF ถึงประหยัดกว่า Euler-Euler สำหรับ free surface?</b></summary>

**คำตอบ:**

**VOF (One-Fluid Formulation):**
- 1 momentum equation สำหรับ mixture
- ใช้ mixture properties (ρ, μ) จาก α
- ไม่ต้องมี closure models สำหรับ interphase forces

**Euler-Euler (Two-Fluid):**
- N momentum equations (1 ต่อ 1 phase)
- ต้องแก้ระบบสมการใหญ่กว่า
- ต้องมี closure models → additional uncertainty

**สรุป:**
- VOF: 1 set of equations + α transport = ถูกกว่า
- Euler-Euler: N sets of equations + closures = แพงกว่า

**แต่ VOF ต้อง:**
- Fine mesh เพื่อ resolve interface
- Small Δt (Co < 1)

</details>

<details>
<summary><b>Q2: cAlpha ทำหน้าที่อะไรใน interFoam?</b></summary>

**คำตอบ:**

**cAlpha = Interface Compression Coefficient**

ควบคุม velocity counter-gradient $\mathbf{U}_r$ ใน α equation:
$$\nabla \cdot (\mathbf{U}_r \alpha (1-\alpha))$$

**Mechanism:**
```
U_r = cAlpha * max(|U|) * n_f

โดย n_f = ∇α / |∇α| = direction ของ interface
```

| cAlpha | Effect |
|--------|--------|
| 0 | ไม่มี compression → interface diffuses |
| 1 | Standard → sharp interface |
| > 1.5 | Aggressive → may cause wrinkles/oscillation |

**Best Practice:**
- Start with `cAlpha 1`
- ถ้า interface ยังเบลอ → เพิ่มเป็น 1.2-1.5
- ถ้ามี oscillation → ลดลง

</details>

<details>
<summary><b>Q3: ทำไมใช้ p_rgh แทน p ใน interFoam?</b></summary>

**คำตอบ:**

**Definition:**
$$p_{rgh} = p - \rho \mathbf{g} \cdot \mathbf{x}$$

**ประโยชน์:**

1. **Boundary Conditions ง่ายขึ้น:**
```cpp
// ที่ free surface ที่ pressure = atmospheric
// ถ้าใช้ p: ต้องคำนวณ hydrostatic ทุก face
// ถ้าใช้ p_rgh: ตั้งค่าเป็น 0 ได้เลย
outlet { type fixedValue; value uniform 0; }
```

2. **Numerical Stability:**
- $\rho \mathbf{g} \cdot \mathbf{x}$ varies smoothly → แยกออกจาก pressure solve
- Pressure solve ทำงานกับ dynamic pressure เท่านั้น

3. **จำเป็นสำหรับ variable density:**
- density jump ที่ interface → ต้องจัดการ hydrostatic อย่างถูกต้อง

</details>

### Level 2: Modeling

<details>
<summary><b>Q4: ทำไม Drag ถึงเป็นแรงที่สำคัญที่สุดใน Euler-Euler?</b></summary>

**คำตอบ:**

**Drag ควบคุม:**
1. **Slip Velocity:** ความเร็วสัมพัทธ์ระหว่างเฟส
2. **Phase Distribution:** bubbles อยู่ที่ไหน
3. **Mass Transfer Rate:** ถ้ามี interphase transfer

**Magnitude:**
```
Typical force magnitudes in bubble column:

Drag:       ~10-100 N/m³
Lift:       ~1-10 N/m³
Virtual Mass: ~0.1-1 N/m³
```

**ถ้า Drag ผิด:**
- Slip velocity ผิด → α distribution ผิด
- Mixing ผิด → residence time ผิด
- Heat/mass transfer ผิด

**กฎ:** เริ่มจาก Drag ให้ stable ก่อน → ค่อยเพิ่ม forces อื่น

</details>

<details>
<summary><b>Q5: IshiiZuber ดีกว่า SchillerNaumann เมื่อไหร่?</b></summary>

**คำตอบ:**

**SchillerNaumann:**
$$C_D = \frac{24}{Re}(1 + 0.15 Re^{0.687}) \quad (Re < 1000)$$
$$C_D = 0.44 \quad (Re \geq 1000)$$

- ออกแบบสำหรับ **rigid spheres**
- ไม่คิดผลของ bubble deformation

**IshiiZuber:**
- คิดผลของ **bubble shape** จาก Eötvös number
- มี regimes: Stokes, Viscous, Distorted, Churn-turbulent

| Eo | Regime | C_D |
|----|--------|-----|
| < 1 | Spherical | ~ SchillerNaumann |
| 1-10 | Ellipsoidal | Modified |
| > 10 | Cap | 8/3 Eo / (Eo + 4) |

**Rule of Thumb:**
- $Eo < 1$: SchillerNaumann OK
- $Eo > 1$: ใช้ IshiiZuber หรือ Tomiyama

$$Eo = \frac{g \Delta\rho d^2}{\sigma}$$

</details>

<details>
<summary><b>Q6: KTGF ใช้เมื่อไหร่และทำไม?</b></summary>

**คำตอบ:**

**KTGF = Kinetic Theory of Granular Flow**

**ใช้เมื่อ:** α_solid > 0.3 (dense regime)

**ทำไมต้องมี?**

ใน dense regime:
- Particle-particle collisions สำคัญ
- ต้องมี "granular pressure" ป้องกัน over-packing
- ต้องมี "granular viscosity" จาก collisions

**KTGF provides:**
```cpp
// Granular pressure
p_s = α_s ρ_s Θ (1 + 4 g_0 α_s η)

// Granular viscosity  
μ_s = μ_kinetic + μ_collision + μ_friction

// Where Θ = granular temperature (random kinetic energy)
```

**Without KTGF:**
- α_s สามารถเกิน packing limit!
- Unphysical compression

**Configuration:**
```cpp
// constant/phaseProperties
solids
{
    type            granular;
    Theta           on;  // solve granular temperature
    residualAlpha   1e-6;
}
```

</details>

### Level 3: Numerical

<details>
<summary><b>Q7: ทำไม Co_max ต้องต่ำกว่าสำหรับ VOF?</b></summary>

**คำตอบ:**

**Standard CFD:** Co < 1 sufficient (explicit convection)

**VOF:** Co < 0.5 often needed

**เหตุผล:**

1. **Interface Sharpness:**
   - α changes from 0 → 1 ใน 1-2 cells
   - High gradient ต้องการ accurate advection
   - Large Co → interface smears

2. **MULES Algorithm:**
   - Explicit → ต้อง satisfy CFL condition
   - Compression term adds additional constraint

3. **Property Jump:**
   - ρ, μ เปลี่ยนที่ interface
   - Large Co → wrong mixture properties

**Best Practice:**
```cpp
adjustTimeStep  yes;
maxCo           0.5;
maxAlphaCo      0.5;  // เฉพาะ α (อาจต่ำกว่า maxCo)
```

</details>

<details>
<summary><b>Q8: ทำไม nAlphaSubCycles ช่วย stability?</b></summary>

**คำตอบ:**

**Concept:**
แก้ α equation หลายครั้งใน 1 time step ของ flow

```
Time step Δt:
├── α subcycle 1 (Δt/2): solve α equation
├── α subcycle 2 (Δt/2): solve α equation
└── Momentum solve with new α
```

**ประโยชน์:**

1. **Lower α-Courant:**
   - αCo = (Δt/n) × |u| / Δx < αCo_main
   - Interface travels less per subcycle

2. **Better Compression:**
   - Compression term evaluated more often
   - Interface stays sharper

3. **Stability:**
   - MULES is explicit → subcycling helps

**Settings:**
```cpp
nAlphaSubCycles 2;  // default
// ถ้ายัง unstable → เพิ่มเป็น 3-4
// แต่เพิ่ม cost!
```

</details>

<details>
<summary><b>Q9: residualAlpha และ residualRe คืออะไร?</b></summary>

**คำตอบ:**

**Problem: Division by Zero**

เมื่อ α → 0 หรือ |u_r| → 0:

$$K = \frac{3}{4} C_D \frac{\alpha_c \alpha_d \rho_c}{d} |\mathbf{u}_r|$$
$$C_D = \frac{24}{Re} \quad \text{where } Re = \frac{\rho |u_r| d}{\mu}$$

ถ้า α_d = 0 หรือ u_r = 0 → K หรือ C_D เป็น undefined!

**Solution: Residual Values**

```cpp
residualAlpha   1e-6;   // α_min สำหรับคำนวณ
residualRe      1e-3;   // Re_min สำหรับ C_D
residualU       1e-4;   // |u_r|_min
```

**Effect:**
```cpp
// Instead of:
alpha_d = 0 → K = 0/0 = NaN

// We get:
alpha_d = max(alpha_d, 1e-6) → K = finite value
```

**Balance:**
- Too low: near-zero values cause issues
- Too high: affects physics (artificial drag)

</details>

---

## 12. ⚡ Hands-on Challenges

### Challenge 1: Dam Break (⭐⭐⭐)

**Setup:**
```bash
cp -r $FOAM_TUTORIALS/multiphase/interFoam/laminar/damBreak .
```

**Tasks:**
1. รัน case และดู animation
2. ทดลองเปลี่ยน cAlpha (0.5, 1, 2) → เปรียบเทียบ sharpness
3. ทดลองเปลี่ยน maxCo (0.2, 0.5, 1) → ดู stability

---

### Challenge 2: Bubble Column (⭐⭐⭐⭐)

**Setup:**
```bash
cp -r $FOAM_TUTORIALS/multiphase/multiphaseEulerFoam/bubbleColumn .
```

**Tasks:**
1. รัน case และดู bubble distribution
2. เปลี่ยน drag model: SchillerNaumann → IshiiZuber
3. เปรียบเทียบ void fraction profile

---

### Challenge 3: Model Sensitivity (⭐⭐⭐⭐⭐)

**วัตถุประสงค์:** เข้าใจผลกระทบของ closure models

**Tasks:**
1. รัน bubble column ด้วย:
   - Drag only
   - Drag + Virtual Mass
   - Drag + VM + Lift
2. Plot: radial void fraction profile
3. วิเคราะห์: model ไหนสำคัญที่สุด?

---

## 13. ❌ Common Mistakes

### Mistake 1: ใช้ VOF กับ Dispersed Flow

```
❌ WRONG: ใช้ interFoam จำลอง bubble column

ปัญหา:
- ต้อง resolve ทุก bubble → mesh ละเอียดมาก!
- Cost astronomical

✅ CORRECT: ใช้ multiphaseEulerFoam
```

---

### Mistake 2: Co สูงเกินไปกับ VOF

```cpp
// ❌ สูงเกินไป
maxCo 1.0;
maxAlphaCo 1.0;

// ผลลัพธ์: interface diffuses, unphysical results

// ✅ Safe values
maxCo 0.5;
maxAlphaCo 0.5;
```

---

### Mistake 3: ลืม setFields

```bash
# ❌ รัน interFoam โดยไม่ setFields
interFoam  # α = 0 everywhere!

# ✅ setFields ก่อน
setFields
interFoam
```

---

### Mistake 4: ใช้ linear scheme กับ α

```cpp
// ❌ Unbounded!
div(phi,alpha) Gauss linear;  // α can go < 0 or > 1

// ✅ Bounded
div(phi,alpha) Gauss vanLeer;
div(phi,alpha) Gauss MUSCL;
```

---

### Mistake 5: Euler-Euler ไม่ verify Drag model

```cpp
// ❌ ใช้ default โดยไม่คิด
drag { (air in water) { type SchillerNaumann; } }

// ❓ ต้องถาม:
// - Bubble size?
// - Eo number?
// - System contamination?

// ✅ Check Eo first
Eo = g Δρ d² / σ = 9.81 × 999 × (0.003)² / 0.07 = 1.26
// Eo > 1 → use IshiiZuber or Tomiyama
```

---

### Mistake 6: Skip stability check ก่อนเพิ่ม forces

```cpp
// ❌ เพิ่ม forces ทั้งหมดทีเดียว
drag { ... }
lift { ... }
virtualMass { ... }
turbulentDispersion { ... }
// ถ้า diverge → ไม่รู้ว่าตัวไหนผิด!

// ✅ Incremental approach
// 1. Drag only → stable?
// 2. + Virtual Mass → stable?
// 3. + Lift → stable?
```

---

## 14. 🔗 เชื่อมโยงกับ Repository

| หัวข้อ | ไฟล์ใน Repository |
|--------|-------------------|
| **Fundamental Concepts** | `MODULE_04/01_FUNDAMENTAL_CONCEPTS/` |
| **VOF Method** | `MODULE_04/02_VOF_METHOD/` |
| **Euler-Euler** | `MODULE_04/03_EULER_EULER_METHOD/` |
| **Interphase Forces** | `MODULE_04/04_INTERPHASE_FORCES/` |
| **Model Selection** | `MODULE_04/05_MODEL_SELECTION/` |
| **Implementation** | `MODULE_04/06_IMPLEMENTATION/` |
| **Validation** | `MODULE_04/07_VALIDATION/` |
| **Equations Reference** | `MODULE_04/99_EQUATIONS_REFERENCE/` |

---

## 15. สรุป: หลักการ 5 ข้อสำหรับ Multiphase

1. **เลือก Approach ให้ถูก**
   - Sharp interface → VOF
   - Dispersed → Euler-Euler

2. **Co < 0.5 สำหรับ VOF**
   - ใช้ adjustTimeStep
   - Interface ต้องการ accuracy

3. **เริ่มจาก Simple model**
   - Drag only ก่อน!
   - ค่อยเพิ่ม complexity

4. **ตรวจ dimensionless numbers**
   - Eo → bubble shape
   - Re → drag regime

5. **Validate กับ experiments**
   - Multiphase = high uncertainty
   - ต้อง verify ผลลัพธ์

---

*"Multiphase is not just adding another fluid — it's changing the entire way of thinking"*
