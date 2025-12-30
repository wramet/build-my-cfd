# 02_Momentum_Conservation.md

---

## Learning Objectives

หลังจากศึกษาบทนี้ คุณควรจะสามารถ:

- **อธิบาย (Explain)** สมการโมเมนตัมแบบ multiphase และความแตกต่างจาก single-phase
- **วิเคราะห์ (Analyze)** แต่ละเทอมในสมการโมเมนตัมและนัยสำคัญทางฟิสิกส์
- **ประเมิน (Evaluate)** แรงระหว่างเฟส (interphase forces) และการเลือกใช้โมเดลที่เหมาะสม
- **ใช้ (Apply)** การตั้งค่า boundary conditions ที่เหมาะสมสำหรับปัญหา multiphase flow ใน OpenFOAM
- **เปรียบเทียบ (Compare)** รูปแบบสมการ dimensional และ dimensionless

---

## Overview

สมการอนุรักษ์โมเมนตัมในระบบ multiphase มีความซับซ้อนกว่า single-phase flow เนื่องจาก:

1. **แต่ละเฟสมีสมการโมเมนตัมของตัวเอง** แต่มี **shared pressure** เชื่อมโยงร่วมกัน
2. **Interphase forces** แลกเปลี่ยนโมเมนตัมระหว่างเฟส (Drag, Lift, Virtual Mass, Turbulent Dispersion)
3. **Volume fraction ($\alpha_k$)** ถ่วงน้ำหนักแต่ละเทอมในสมการ
4. **Coupling แบบ two-way** - เฟสหนึ่งส่งผลต่ออีกเฟสหนึ่งและในทางกลับกัน

เอกสารฉบับนี้อธิบาย **What-Why-How** ของสมการโมเมนตัม multiphase พร้อมตัวอย่างการใช้งานใน OpenFOAM

---

## 1. General Form of Momentum Equation

### 1.1 What: สมการโมเมนตัมแบบเต็มรูปแบบ

$$\frac{\partial(\alpha_k \rho_k \mathbf{u}_k)}{\partial t} + \nabla \cdot (\alpha_k \rho_k \mathbf{u}_k \mathbf{u}_k) = -\alpha_k \nabla p + \nabla \cdot (\alpha_k \boldsymbol{\tau}_k) + \alpha_k \rho_k \mathbf{g} + \mathbf{M}_k$$

### 1.2 Why: ทำไมต้องมี volume fraction $\alpha_k$ ทุกเทอม?

ใน multiphase flow, เฟสแต่ละเฟส **ไม่ได้เต็มพื้นที่ทั้งหมด** แต่ใช้พื้นที่ร่วมกัน ดังนั้น:
- แต่ละเทอมจะถูก **scaled ด้วย $\alpha_k$** ซึ่งแทนสัดส่วนปริมาตรของเฟส $k$ ใน control volume
- ถ้า $\alpha_k = 0$: เฟส $k$ ไม่มีอยู่จริง → สมการโมเมนตัมไม่มีผล
- ถ้า $\alpha_k = 1$: กลายเป็น single-phase flow

### 1.3 How: แต่ละเทอมในสมการ

| Term | Mathematical Form | Physical Meaning | Practical Example |
|------|-------------------|------------------|-------------------|
| **Unsteady** | $\frac{\partial(\alpha_k \rho_k \mathbf{u}_k)}{\partial t}$ | Rate of momentum accumulation | การเร่ง/เบรกของ bubble swarm ใน startup |
| **Convection** | $\nabla \cdot (\alpha_k \rho_k \mathbf{u}_k \mathbf{u}_k)$ | Momentum transport by flow | การพาโมเมนตัมเข้า/ออก control volume |
| **Pressure Gradient** | $-\alpha_k \nabla p$ | Force due to pressure difference | แรงผลักดันจากความดันสูง → ต่ำ |
| **Viscous Stress** | $\nabla \cdot (\alpha_k \boldsymbol{\tau}_k)$ | Friction/diffusion of momentum | ความต้านทานจากความหนืดของ fluid |
| **Gravity** | $\alpha_k \rho_k \mathbf{g}$ | Body force due to gravity | แรงโน้มถ่วงที่ทำให้ gas/liquid แยกชั้น |
| **Interphase Forces** | $\mathbf{M}_k$ | Momentum exchange between phases | แรง drag ที่ลดความเร็ว bubble |

---

## 2. Stress Tensor Formulation

### 2.1 What: Newtonian Stress Tensor

สำหรับ fluid แบบ Newtonian:

$$\boldsymbol{\tau}_k = \mu_k \left(\nabla \mathbf{u}_k + (\nabla \mathbf{u}_k)^T\right) - \frac{2}{3}\mu_k (\nabla \cdot \mathbf{u}_k)\mathbf{I}$$

### 2.2 Why: ทำไมต้องใช้รูปแบบนี้?

- **เทอมแรก** ($\nabla \mathbf{u} + (\nabla \mathbf{u})^T$): การยืดหดและการบิดของ fluid (strain rate tensor)
- **เทอมที่สอง** ($\frac{2}{3}\mu_k (\nabla \cdot \mathbf{u}_k)\mathbf{I}$): แก้ correction สำหรับ compressible flow
- สำหรับ **incompressible flow**: $\nabla \cdot \mathbf{u} = 0$ → เทอมที่สองหายไป

### 2.3 How: Effective Viscosity in Turbulent Flow

$$\mu_{eff} = \mu_{lam} + \mu_t$$

| Component | Symbol | Physical Meaning | When Important |
|-----------|--------|------------------|----------------|
| Laminar Viscosity | $\mu_{lam}$ | ความหนืดโมเลกุล | Low Reynolds number |
| Turbulent Viscosity | $\mu_t$ | ความหนืดเนื่องจาก turbulence | High Reynolds number |

**Practical Note:** ใน OpenFOAM ใช้ `nuEff` (kinematic effective viscosity) แทน $\mu_{eff}/\rho$

---

## 3. Interphase Momentum Transfer (3W Framework)

### 3.1 Overview

$$\mathbf{M}_k = \sum_{l \neq k} (\mathbf{F}^D_{kl} + \mathbf{F}^L_{kl} + \mathbf{F}^{VM}_{kl} + \mathbf{F}^{TD}_{kl})$$

Interphase forces **เชื่อมโยงโมเมนตัมระหว่างเฟส** โดยแต่ละ force มีบทบาทแตกต่างกัน

---

### 3.2 Drag Force ($\mathbf{F}^D_{kl}$)

#### What (อะไรคือ Drag Force?)

$$\mathbf{F}^D_{kl} = K_{kl}(\mathbf{u}_l - \mathbf{u}_k)$$

- $K_{kl}$: Drag coefficient (function of Reynolds number, volume fraction)
- แรงที่ **ต้านการเคลื่อนที่สัมพัทธ์** ระหว่างเฟส
- เป็น **interphase force ที่สำคัญที่สุด** ในส่วนใหญ่ของการใช้งาน

#### Why (ทำไมสำคัญ?)

- ทำให้ **velocity ของทั้งสองเฟสเข้าใกล้กัน** (velocity relaxation)
- ถ้าไม่มี drag: แต่ละเฟสจะเคลื่อนที่ด้วยความเร็วเองอย่างอิสระ → ไม่สมจริง
- ใน bubble column: drag ทำให้ bubble rise ด้วยความเร็ว terminal velocity

#### How (ใช้งานอย่างไร?)

**สถานการณ์ที่ต้องพิจารณา:**
- **Gas-Liquid**: ใช้ Schiller-Naumann หรือ Ishii-Zuber model
- **Liquid-Liquid**: ใช้ model ที่ account สำหรับ viscosity ratio
- **High volume fraction**: ต้องใช้ correction factor (เช่น $K_{kl} \cdot f(\alpha_c)$)

---

### 3.3 Lift Force ($\mathbf{F}^L_{kl}$)

#### What (อะไรคือ Lift Force?)

$$\mathbf{F}^L_{kl} = -C_L \rho_c \alpha_d (\mathbf{u}_r \times \boldsymbol{\omega}_c)$$

- $\mathbf{u}_r = \mathbf{u}_d - \mathbf{u}_c$: Relative velocity
- $\boldsymbol{\omega}_c = \nabla \times \mathbf{u}_c$: Vorticity of continuous phase
- แรงที่ **ตั้งฉากกับ relative velocity และ vorticity**

#### Why (ทำไมสำคัญ?)

- ทำให้ bubbles/droplets **เคลื่อนที่ข้าม streamlines** (lateral migration)
- ใน channel flow: lift ทำให้ bubbles **accumulate ที่กำแพงหรือ center** ขึ้นกับขนาด
- สำคัญในการทำนาย **phase distribution** ใน cross-section

#### How (ใช้งานอย่างไร?)

**สถานการณ์ที่ต้องพิจารณา:**
- **Bubbles in shear flow**: Lift coefficient $C_L$ ขึ้นกับ bubble size (Reynolds number)
- **Small bubbles**: $C_L > 0$ → move toward wall
- **Large bubbles**: $C_L < 0$ → move toward center
- ใช้ Tomiyama model สำหรับการใช้งานที่หลากหลาย

---

### 3.4 Virtual Mass Force ($\mathbf{F}^{VM}_{kl}$)

#### What (อะไรคือ Virtual Mass?)

$$\mathbf{F}^{VM}_{kl} = C_{VM} \rho_c \alpha_d \left(\frac{D\mathbf{u}_c}{Dt} - \frac{D\mathbf{u}_d}{Dt}\right)$$

- $C_{VM}$: Virtual mass coefficient (typically 0.5 for spheres)
- แรงเนื่องจาก **acceleration of displaced fluid** รอบๆ particle/droplet/bubble
- Material derivative: $\frac{D\mathbf{u}}{Dt} = \frac{\partial \mathbf{u}}{\partial t} + \mathbf{u} \cdot \nabla \mathbf{u}$

#### Why (ทำไมสำคัญ?)

- เมื่อ dispersed phase **accelerate/decelerate**, continuous phase ต้องเคลื่อนที่เพื่อให้ทาง
- เพิ่ม **inertia** ของ dispersed phase (เหมือนมี mass เพิ่มขึ้น)
- สำคัญใน **unsteady flow** หรือเมื่อมี **large acceleration**

#### How (ใช้งานอย่างไร?)

**สถานการณ์ที่ต้องพิจารณา:**
- **Bubble column startup**: Virtual mass สำคัญในช่วง transient
- **Slug flow**: การเคลื่อนที่ของ gas slug ต้องใช้ virtual mass
- **Steady-state**: มัก **neglect** ได้ (acceleration ≈ 0)

---

### 3.5 Turbulent Dispersion Force ($\mathbf{F}^{TD}_{kl}$)

#### What (อะไรคือ Turbulent Dispersion?)

$$\mathbf{F}^{TD}_{kl} = -C_{TD} \rho_c k_c \nabla \alpha_d$$

- $k_c$: Turbulent kinetic energy of continuous phase
- แรงที่ **กระจาย dispersed phase** จาก region ที่มี concentration สูง → ต่ำ
- Driven by **turbulent fluctuations** ของ continuous phase

#### Why (ทำไมสำคัญ?)

- โดยไม่มี turbulent dispersion: dispersed phase จะ **clump** ด้วยตัวเอง
- Turbulence ทำให้ **mixing** ของ phases ดีขึ้น
- สำคัญใน **high-turbulence flow** (เช่น jet, stirred tank)

#### How (ใช้งานอย่างไร?)

**สถานการณ์ที่ต้องพิจารณา:**
- **High Reynolds number**: $k_c$ สูง → turbulent dispersion สำคัญ
- **Low Reynolds number**: มัก neglect ได้
- ใช้ Burns หรือ Lopez de Bertodano model

---

## 4. Physical Interpretation: Shared Pressure Concept

### 4.1 What: Shared Pressure คืออะไร?

ใน Euler-Euler approach, **pressure field $p$ แชร์ร่วมกันทุกเฟส**:

$$p = p_1 = p_2 = \cdots = p_N$$

### 4.2 Why: ทำไมต้องใช้ Shared Pressure?

**ข้อสมมติพื้นฐาน:** เฟสทั้งหมด **co-located** ใน control volume เดียวกัน
- เนื่องจาก **length scale ของ bubbles/droplets** ≫ **length scale ของ local equilibrium**
- Pressure จึง **equalize** ที่ scale ของ control volume อย่างรวดเร็ว
- แต่ละเฟสไม่มี pressure field แยกกัน

**Consequences:**
1. **Single pressure equation** สำหรับทั้งระบบ (ไม่ใช่ $N$ equations)
2. Pressure-velocity coupling ต้อง **account สำหรับทุกเฟส**
3. ใช้ **continuum pressure** ไม่ใช่ pressure ภายใน bubble

### 4.3 How: Implementation Considerations

**Numerical Implications:**
- Pressure gradient term: $-\alpha_k \nabla p$ → แต่ละเฟสได้รับ **fraction** ของ pressure force
- ถ้า $\alpha_k \to 0$: เฟส $k$ ไม่ได้รับ pressure force (เนื่องจากไม่มีอยู่จริง)
- ใน OpenFOAM: `fvc::reconstruct(p)` ใช้ reconstruct velocity จาก pressure flux

**Common Pitfall:**
❌ **ไม่ถูกต้อง:** ตั้งค่า pressure boundary conditions ที่ต่างกันสำหรับแต่ละเฟส  
✅ **ถูกต้อง:** ใช้ pressure BC ชุดเดียว แต่ velocity BC สามารถต่างกันได้

---

## 5. OpenFOAM Implementation

### 5.1 Momentum Equation in Code

```cpp
// File: UEqn.H (twoPhaseEulerFoam solver)

fvVectorMatrix U1Eqn
(
    fvm::ddt(alpha1, rho1, U1)              // ∂(α₁ρ₁U₁)/∂t
  + fvm::div(alphaRhoPhi1, U1)              // ∇·(α₁ρ₁U₁U₁)
  + MRF.DDt(alpha1, rho1, U1)               // Optional: Moving reference frame
 ==
    fvm::laplacian(alpha1*rho1*nuEff1, U1)  // ∇·(α₁τ₁)
  + fvOptions(alpha1, rho1, U1)             // Optional: Source terms
  + phase1.turbulence().divDevRhoReff(U1)   // Turbulence contribution
);

fvVectorMatrix U2Eqn
(
    fvm::ddt(alpha2, rho2, U2)
  + fvm::div(alphaRhoPhi2, U2)
  + MRF.DDt(alpha2, rho2, U2)
 ==
    fvm::laplacian(alpha2*rho2*nuEff2, U2)
  + fvOptions(alpha2, rho2, U2)
  + phase2.turbulence().divDevRhoReff(U2)
);
```

### 5.2 Interphase Forces in Code

```cpp
// Drag force (typical implementation)
Kd = drag->K();                              // Drag coefficient
F_drag = Kd * (U2 - U1);                     // K(u₂ - u₁)

// Lift force
F_lift = Cl * rho1 * alpha2 * (Urel ^ omega1); // C_L α ρ (u_r × ω)

// Virtual mass
Cvm = 0.5;                                   // Virtual mass coefficient
F_vm = Cvm * rho1 * alpha2 * (fvc::DDt(U1) - fvc::DDt(U2));

// Add to momentum equations
U1Eqn += (F_drag + F_lift + F_vm + F_td);
U2Eqn -= (F_drag + F_lift + F_vm + F_td);    // Equal and opposite
```

### 5.3 Pressure Gradient Term

```cpp
// File: pEqn.H (pressure equation)

// Pressure gradient added to momentum predictor
surfaceScalarField phiHbyA1
(
    "phiHbyA1",
    fvc::interpolate(rho1*alpha1)
   *(
        fvc::flux(H1)                         // Predicted flux
      + alpha1*rho1*rAU1 * (-fvc::grad(p))   // Pressure gradient
    )
);

// Reconstruct velocity from pressure
U1 = H1 - rAU1 * fvc::grad(p);
```

---

## 6. Dimensionless Form and Scaling Analysis

### 6.1 What: Dimensionless Momentum Equation

$$\frac{\partial(\alpha_k \tilde{\mathbf{u}}_k)}{\partial \tilde{t}} + \nabla \cdot (\alpha_k \tilde{\mathbf{u}}_k \tilde{\mathbf{u}}_k) = -\alpha_k \nabla \tilde{p} + \frac{1}{Re}\nabla^2(\alpha_k \tilde{\mathbf{u}}_k) + \frac{1}{Fr^2}\alpha_k \hat{\mathbf{g}}$$

- Tilde ($\tilde{}$): Dimensionless variables
- $\hat{\mathbf{g}}$: Unit gravity vector

### 6.2 Why: ทำไมต้อง Dimensionless?

**Scaling analysis** ช่วยให้:
1. **Identify dominant mechanisms** (ซึ่งเทอมใหญ่กว่า?)
2. **Design experiments** ที่ dynamically similar
3. **Understand limiting behavior** (เช่น $Re \to \infty$)

### 6.3 How: Key Dimensionless Numbers

| Number | Formula | Physical Meaning | When Important |
|--------|---------|------------------|----------------|
| **Reynolds** | $Re = \frac{\rho U L}{\mu}$ | Inertia / Viscosity | เทียบสมดุล inertial vs viscous forces |
| **Froude** | $Fr = \frac{U}{\sqrt{gL}}$ | Inertia / Gravity | Free surface flows, stratified flows |
| **Eötvös** | $Eo = \frac{(\rho_c - \rho_d) g d^2}{\sigma}$ | Buoyancy / Surface tension | Bubble/droplet shape |
| **Morton** | $Mo = \frac{g \mu_c^4 \Delta \rho}{\rho_c^2 \sigma^3}$ | Property effects | Regime maps |

**Example:**
- $Re \gg 1$: Inertia dominates → **inviscid approximation** อาจใช้ได้
- $Fr \approx 1$: Gravity important → **stratification** สำคัญ
- $Eo \gg 1$: Buoyancy dominates surface tension → **deformed bubbles**

---

## 7. Boundary Conditions: When to Use What

### 7.1 Inlet Boundary Conditions

| Type | When to Use | Example Syntax | Notes |
|------|-------------|----------------|-------|
| **fixedValue** |  Known velocity at inlet | `U.water { type fixedValue; value uniform (0 0 1); }` | Most common for inlets |
| **pressureInletVelocity** | Pressure specified, velocity adjusts | `U.water { type pressureInletVelocity; value $internalField; }` | Backflow prevention built-in |
| **flowRateInletVelocity** | Mass/volumetric flow rate known | `U.water { type flowRateInletVelocity; massFlowRate 0.1; }` | Ensures correct flow rate |

### 7.2 Wall Boundary Conditions

| Type | When to Use | Example Syntax | Notes |
|------|-------------|----------------|-------|
| **noSlip** |  Viscous walls, accurate boundary layer | `U.water { type noSlip; }` | Velocity = 0 at wall |
| **slip** | Free-slip walls, symmetry | `U.water { type slip; }` | Normal velocity = 0 |
| **partialSlip** |  Rough walls, empirical slip length | `U.water { type partialSlip; value uniform 0; slipFraction 0.9; }` | Intermediate between slip/no-slip |

**When to use which?**
- **Liquid-solid interface**: `noSlip` (most realistic)
- **Free surface (symmetry)**: `slip`
- **Coarse mesh / computational efficiency**: `slip` (sacrifice accuracy)

### 7.3 Outlet Boundary Conditions

| Type | When to Use | Example Syntax | Notes |
|------|-------------|----------------|-------|
| **zeroGradient** | Fully developed flow | `U.water { type zeroGradient; }` | $\partial U / \partial n = 0$ |
| **pressureDirectedInletOutletVelocity** | Pressure-driven, backflow possible | `U.water { type pressureDirectedInletOutletVelocity; inletValue uniform (0 0 0); }` | Prevents backflow instability |
| **fixedMeanValue** | Mean velocity known | `U.water { type fixedMeanValue; meanValue 1.0; }` | Ensures average velocity |

**When to use which?**
- **Fully developed exit**: `zeroGradient` (most common)
- **Possibility of backflow**: `pressureDirectedInletOutletVelocity` (robust)
- **Confined outlet**: `fixedMeanValue` (constrain flow rate)

### 7.4 Symmetry/Periodic Boundaries

| Type | When to Use | Notes |
|------|-------------|-------|
| **symmetry** | Physical symmetry plane | Velocity = mirrored |
| **cyclic** | Periodic domains (e.g., pipe sections) | Connects two patches |

---

## 8. Common Pitfalls and Troubleshooting

### 8.1 Numerical Issues

| Problem | Possible Cause | Solution |
|---------|----------------|----------|
| **Diverging solution** | Too large time step | Reduce `maxDeltaT` or use `adjustTimeStep yes` |
| **Pressure-velocity decoupling** | Incorrect interpolation | Check `interpolate(rho)` and flux schemes |
| **Unphysical velocity spikes** | Poor mesh quality | Check non-orthogonality, aspect ratio |

### 8.2 Modeling Issues

| Problem | Possible Cause | Solution |
|---------|----------------|----------|
| **Bubbles not moving** | Drag coefficient too high | Check drag model, $K_d$ magnitude |
| **Incorrect phase distribution** | Missing lift force | Enable lift force with correct $C_L$ |
| **Oscillating solution** | Missing virtual mass in startup | Add virtual mass for unsteady cases |

### 8.3 Boundary Condition Pitfalls

❌ **Incorrect:** Using `zeroGradient` at inlet (allows backflow unrestricted)  
✅ **Correct:** Use `pressureInletVelocity` or `fixedValue`

❌ **Incorrect:** Using `fixedValue` at outlet (over-specifies problem)  
✅ **Correct:** Use `zeroGradient` or pressure-based BC

❌ **Incorrect:** Different pressure BC for each phase  
✅ **Correct:** Single shared pressure field

---

## 9. Key Takeaways

### 9.1 Summary

1. **แต่ละเฟสมีสมการโมเมนตัมของตัวเอง** แต่ **shared pressure** เชื่อมโยงร่วมกัน
2. **Volume fraction ($\alpha_k$)** scales ทุกเทอมในสมการ
3. **Interphase forces** (Drag, Lift, Virtual Mass, Turbulent Dispersion) เป็นหัวใจของ coupling ระหว่างเฟส
4. **Drag** มักเป็น interphase force ที่สำคัญที่สุด แต่ force อื่นๆ อาจสำคัญในสถานการณ์เฉพาะ
5. **Boundary conditions** ต้องเลือกให้เหมาะกับ physical problem และ numerical stability
6. **Scaling analysis** ช่วยให้เข้าใจ dominant mechanisms และ design simulations

### 9.2 Practical Guidelines

| Scenario | Key Considerations |
|----------|-------------------|
| **Steady bubble column** | Drag dominant, neglect virtual mass |
| **Unsteady slug flow** | Include virtual mass and lift |
| **Highly turbulent mixing** | Turbulent dispersion critical |
| **Laminar pipe flow** | Viscous terms dominate, $Re$ low |
| **Free surface flow** | Include surface tension, check $Eo$ |

---

## 10. Concept Check

<details>
<summary><b>1. ทำไมต้องใช้ shared pressure ใน Euler-Euler approach?</b></summary>

เพราะ Euler-Euler ถือว่าเฟสทั้งหมด **co-located** ใน control volume เดียวกัน และ pressure equalizes ที่ scale ของ control volume อย่างรวดเร็ว ดังนั้นจึงมี pressure field เดียวทุกเฟส แต่แต่ละเฟสได้รับ pressure force เป็น fraction ($\alpha_k \nabla p$) ตาม volume fraction ของตัวเอง
</details>

<details>
<summary><b>2. Interphase forces มีอะไรบ้าง? และใช้เมื่อไร?</b></summary>

| Force | When Important |
|-------|----------------|
| **Drag** | เกือบทุกกรณี - สำคัญที่สุด |
| **Lift** | การกระจาย phase ใน shear flow |
| **Virtual Mass** | Unsteady flow, large acceleration |
| **Turbulent Dispersion** | High turbulence, mixing problems |

Drag คือ interphase force ที่พื้นฐานที่สุด ส่วน force อื่นๆ เพิ่มเมื่อสถานการณ์จำเพาะต้องการ
</details>

<details>
<summary><b>3. อะไรคือความแตกต่างระหว่าง fvm และ fvc ใน OpenFOAM?</b></summary>

| Method | Full Name | Usage | Position in Matrix |
|--------|-----------|-------|-------------------|
| **fvm** | Finite Volume Method | Implicit | Left-hand side (matrix) |
| **fvc** | Finite Volume Calculus | Explicit | Right-hand side (source) |

**Example:**
- `fvm::laplacian(nu, U)`: Implicit viscous term (added to matrix)
- `fvc::grad(p)`: Explicit pressure gradient (source term)
</details>

<details>
<summary><b>4. ทำไมต้อง scaling ด้วย volume fraction $\alpha_k$ ทุกเทอม?</b></summary>

เพราะใน multiphase flow, แต่ละเฟส **ไม่ได้เต็มพื้นที่ทั้งหมด** แต่แบ่งปัน control volume กับเฟสอื่น ดังนั้น:
- แต่ละเทอมจึงต้อง scaled ด้วย $\alpha_k$ เพื่อแทนส่วนของ control volume ที่เฟส $k$ ครอบครอง
- ถ้า $\alpha_k = 0$: เฟส $k$ ไม่มีอยู่ → สมการไม่มีผล
- ถ้า $\alpha_k = 1$: กลายเป็น single-phase flow
</details>

<details>
<summary><b>5. Boundary conditions ไหนเหมาะกับ inlet ที่มี possibility of backflow?</b></summary>

`pressureInletVelocity` หรือ `pressureDirectedInletOutletVelocity`:

```cpp
U.water
{
    type            pressureInletVelocity;
    value           uniform (0 0 0);   // Used when backflow occurs
    phi             phi.water;         // Flux field
    rho             rho;               // Density field
}
```

BC ประเภทนี้:
- ใช้ velocity ที่ระบุเมื่อ flow เข้า
- ใช้ **zeroGradient** เมื่อ backflow (prevents unphysical reverse flow)
</details>

---

## Related Documents

### ภาพรวมและพื้นฐาน
- **ภาพรวม Multiphase:** [00_Overview.md](00_Overview.md)
- **Mass Conservation:** [01_Mass_Conservation.md](01_Mass_Conservation.md)
- **Energy Conservation:** [03_Energy_Conservation.md](03_Energy_Conservation.md)

### Interphase Forces (รายละเอียดเฉพาะ)
- **Drag:** [04_INTERPHASE_FORCES/01_DRAG/00_Overview.md](../04_INTERPHASE_FORCES/01_DRAG/00_Overview.md)
- **Lift:** [04_INTERPHASE_FORCES/02_LIFT/00_Overview.md](../04_INTERPHASE_FORCES/02_LIFT/00_Overview.md)
- **Virtual Mass:** [04_INTERPHASE_FORCES/03_VIRTUAL_MASS/00_Overview.md](../04_INTERPHASE_FORCES/03_VIRTUAL_MASS/00_Overview.md)
- **Turbulent Dispersion:** [04_INTERPHASE_FORCES/04_TURBULENT_DISPERSION/00_Overview.md](../04_INTERPHASE_FORCES/04_TURBULENT_DISPERSION/00_Overview.md)

### Model Selection
- **Decision Framework:** [05_MODEL_SELECTION/01_Decision_Framework.md](../05_MODEL_SELECTION/01_Decision_Framework.md)
- **Gas-Liquid Systems:** [05_MODEL_SELECTION/02_Gas_Liquid_Systems.md](../05_MODEL_SELECTION/02_Gas_Liquid_Systems.md)

---

**Document Version:** 1.0  
**Last Updated:** 2025-12-30  
**Author:** OpenFOAM Multiphase Documentation Team