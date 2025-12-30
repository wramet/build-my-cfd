# Euler-Euler Mathematical Framework

กรอบทางคณิตศาสตร์ของ Euler-Euler Method

---

## Learning Objectives

หลังจากศึกษาส่วนนี้ คุณจะสามารถ:
- Explain the mathematical foundation of volume averaging in Euler-Euler methods
- Derive the ensemble-averaged conservation equations for multiphase flow
- Understand the physical meaning of each term in the momentum equation
- Comprehend interphase coupling mechanisms and their mathematical formulations
- Analyze turbulence modeling approaches for multiphase systems

### Learning Objectives (TH)

หลังจากศึกษาส่วนนี้ คุณจะสามารถ:
- อธิบายกรอบทางคณิตศาสตร์ของการหาค่าเฉลี่ยตามปริมาตรในวิธี Euler-Euler
- อนุพันธ์สมการอนุรักษ์ที่หาค่าเฉลี่ยแล้วสำหรับการไหลหลายเฟส
- เข้าใจความหมายทางฟิสิกส์ของแต่ละเทอมในสมการโมเมนตัม
- เข้าใจกลไกการเชื่อมโยงระหว่างเฟสและการนำเสนอเชิงคณิตศาสตร์
- วิเคราะห์แนวทางการจำลองความปั่นสำหรับระบบหลายเฟส

---

## Key Takeaways

- **Volume averaging** transforms microscopic two-phase physics into macroscopic continuum equations
- **Interphase coupling** through drag, lift, virtual mass, and turbulent dispersion forces is critical
- **Turbulence modeling** requires special treatment for multiphase interactions
- **Pressure-velocity coupling** is more complex than single-phase due to volume fraction constraints
- **Closure relations** for interphase transfer terms determine model accuracy

### Key Takeaways (TH)

- **Volume averaging** แปลงฟิสิกส์ไมโครสโคปิกของสองเฟสให้เป็นสมการคอนตินิวอัมแบบมาโครสโคปิก
- **Interphase coupling** ผ่านแรงลาก, lift, virtual mass และ turbulent dispersion เป็นสิ่งสำคัญ
- **Turbulence modeling** ต้องการการรักษาพิเศษสำหรับปฏิสัมพันธ์หลายเฟส
- **Pressure-velocity coupling** ซับซ้อนกว่าเฟสเดียวเนื่องจากข้อจำกัด volume fraction
- **Closure relations** สำหรับเทอมการถ่ายเทระหว่างเฟสกำหนดความแม่นยำของโมเดล

---

## Prerequisites

- Conservation laws from [01_GOVERNING_EQUATIONS](../../../MODULE_01_CFD_FUNDAMENTALS/CONTENT/01_GOVERNING_EQUATIONS/02_Detailed_Derivation.md)
- Reynolds-averaging concepts from [02_RANS_Models](../../../MODULE_03_SINGLE_PHASE_FLOW/CONTENT/03_TURBULENCE_MODELING/02_RANS_Models.md)
- Navier-Stokes equations fundamentals

---

## 1. Volume Averaging Fundamentals

### 1.1 What is Volume Averaging?

Volume averaging is a mathematical operation that transforms the discontinuous two-phase flow field into continuous equations for each phase. Unlike interface-tracking methods (like VOF), Euler-Euler treats both phases as interpenetrating continua.

### 1.2 Averaging Definitions

**Phase indicator function:**
$$\chi_k(\mathbf{x}, t) = 
\begin{cases}
1 & \text{if phase } k \text{ exists at } \mathbf{x}, t \\
0 & \text{otherwise}
\end{cases}$$

**Volume fraction:**
$$\alpha_k(\mathbf{x}, t) = \langle \chi_k \rangle = \frac{1}{V} \int_V \chi_k \, dV$$

**Volume-averaged quantity:**
$$\langle \phi \rangle_k = \frac{1}{V_k} \int_{V_k} \phi \, dV$$

where $V_k = \alpha_k V$ is the volume occupied by phase $k$ in the averaging volume $V$.

**Constraint:**
$$\sum_{k=1}^{N} \alpha_k = 1$$

### 1.3 Favre Averaging (Mass-Weighted)

For compressible flows, we use Favre averaging:
$$\tilde{\phi}_k = \frac{\langle \rho_k \phi_k \rangle_k}{\langle \rho_k \rangle_k}$$

This simplifies the equations by removing density correlations.

### 1.4 Decomposition Rules

Any instantaneous quantity is decomposed as:
$$\phi_k = \langle \phi \rangle_k + \phi'_k$$

Key averaging rules:
1. $\langle \langle \phi \rangle_k \rangle_k = \langle \phi \rangle_k$ (idempotent)
2. $\langle \alpha_k \phi_k \rangle = \alpha_k \langle \phi \rangle_k$ (linearity)
3. $\langle \alpha_k \phi'_k \rangle = 0$ (fluctuation orthogonality)

---

## 2. Derivation of Conservation Equations

### 2.1 Instantaneous Equations

For each phase $k$, the microscopic equations are:

**Mass:**
$$\frac{\partial \rho_k}{\partial t} + \nabla \cdot (\rho_k \mathbf{u}_k) = 0$$

**Momentum:**
$$\frac{\partial (\rho_k \mathbf{u}_k)}{\partial t} + \nabla \cdot (\rho_k \mathbf{u}_k \mathbf{u}_k) = -\nabla p_k + \nabla \cdot \boldsymbol{\tau}_k + \rho_k \mathbf{g}$$

### 2.2 Ensemble Averaging Procedure

**Step 1:** Multiply by phase indicator $\chi_k$

**Step 2:** Apply ensemble average $\langle \cdot \rangle$

**Step 3:** Use spatial averaging theorem:
$$\langle \nabla \phi_k \rangle = \nabla \langle \phi_k \rangle + \frac{1}{V} \int_{A_k} \phi_k \mathbf{n}_k \, dA$$

where $A_k$ is the interface area and $\mathbf{n}_k$ is the unit normal.

### 2.3 Averaged Mass Conservation

$$\frac{\partial (\alpha_k \rho_k)}{\partial t} + \nabla \cdot (\alpha_k \rho_k \mathbf{u}_k) = \Gamma_k$$

where:
- $\alpha_k \rho_k = \langle \rho_k \chi_k \rangle$ is the bulk density
- $\mathbf{u}_k = \frac{\langle \rho_k \mathbf{u}_k \chi_k \rangle}{\langle \rho_k \chi_k \rangle}$ is the mass-averaged velocity
- $\Gamma_k = \sum_{l \neq k} \dot{m}_{lk}$ is the mass transfer rate from phase $l$ to $k$

**Constraint:**
$$\sum_k \Gamma_k = 0 \quad \text{(mass conservation overall)}$$

### 2.4 Averaged Momentum Conservation

$$\frac{\partial (\alpha_k \rho_k \mathbf{u}_k)}{\partial t} + \nabla \cdot (\alpha_k \rho_k \mathbf{u}_k \mathbf{u}_k) = 
-\alpha_k \nabla p + \nabla \cdot (\alpha_k \boldsymbol{\tau}_k) + \alpha_k \rho_k \mathbf{g} + \mathbf{M}_k$$

**Physical meaning of each term:**

| Term | Mathematical Form | Physical Meaning |
|------|-------------------|------------------|
| **Transient** | $\frac{\partial (\alpha_k \rho_k \mathbf{u}_k)}{\partial t}$ | Rate of momentum change per unit volume |
| **Convection** | $\nabla \cdot (\alpha_k \rho_k \mathbf{u}_k \mathbf{u}_k)$ | Momentum transport by fluid motion |
| **Pressure Gradient** | $-\alpha_k \nabla p$ | Force due to pressure variation (shared pressure) |
| **Viscous Stress** | $\nabla \cdot (\alpha_k \boldsymbol{\tau}_k)$ | Diffusion of momentum via viscosity |
| **Gravity** | $\alpha_k \rho_k \mathbf{g}$ | Body force due to gravity |
| **Interphase** | $\mathbf{M}_k$ | Sum of all interphase forces |

### 2.5 Averaged Energy Conservation

$$\frac{\partial (\alpha_k \rho_k h_k)}{\partial t} + \nabla \cdot (\alpha_k \rho_k h_k \mathbf{u}_k) = 
\nabla \cdot (k_{eff,k} \nabla T_k) + Q_k + \Pi_k^h$$

where:
- $h_k$ = specific enthalpy
- $k_{eff,k}$ = effective thermal conductivity
- $Q_k$ = heat source (e.g., external heating)
- $\Pi_k^h$ = interphase heat transfer

---

## 3. Stress Tensor and Viscosity Modeling

### 3.1 Viscous Stress Tensor

For Newtonian phase $k$:
$$\boldsymbol{\tau}_k = \mu_k \left[ \nabla \mathbf{u}_k + (\nabla \mathbf{u}_k)^T - \frac{2}{3}(\nabla \cdot \mathbf{u}_k)\mathbf{I} \right]$$

This represents:
- **Strain rate**: $\nabla \mathbf{u}_k + (\nabla \mathbf{u}_k)^T$
- **Dilatation**: $-\frac{2}{3}(\nabla \cdot \mathbf{u}_k)\mathbf{I}$ (ensures $\boldsymbol{\tau}_k$ is traceless)

### 3.2 Effective Viscosity

In turbulent multiphase flow:
$$\mu_{eff,k} = \mu_{lam,k} + \mu_{t,k}$$

**Laminar viscosity** ($\mu_{lam,k}$): Physical property of the fluid

**Turbulent viscosity** ($\mu_{t,k}$): Modeled via turbulence closure (see Section 6)

### 3.3 Shear-Induced vs Bubble-Induced Turbulence

For bubbly flows:
$$\mu_{t,k} = \mu_{t,SI} + \mu_{t,BI}$$

- **Shear-induced**: Standard turbulence from velocity gradients
- **Bubble-induced**: Additional pseudo-turbulence from bubble wakes

---

## 4. Interphase Coupling Forces

### 4.1 General Form

The total interphase force on phase $k$:
$$\mathbf{M}_k = \sum_{l \neq k} \mathbf{M}_{kl}$$

where $\mathbf{M}_{kl}$ is the force exerted by phase $l$ on phase $k$.

**Action-reaction:**
$$\mathbf{M}_{kl} = -\mathbf{M}_{lk}$$

### 4.2 Individual Force Components

$$\mathbf{M}_{kl} = \mathbf{F}^D_{kl} + \mathbf{F}^L_{kl} + \mathbf{F}^{VM}_{kl} + \mathbf{F}^{TD}_{kl} + \mathbf{F}^{WL}_{kl}$$

#### 4.2.1 Drag Force

**Physical meaning:** Resistance due to relative motion between phases

$$\mathbf{F}^D_{kl} = K_{kl} (\mathbf{u}_l - \mathbf{u}_k)$$

**Drag coefficient:**
$$K_{kl} = \frac{3}{4} C_D \frac{\alpha_k \alpha_l \rho_c}{d_p} |\mathbf{u}_r|$$

where:
- $C_D$ = drag coefficient (function of Reynolds number)
- $\rho_c$ = continuous phase density
- $d_p$ = particle/droplet/bubble diameter
- $\mathbf{u}_r = \mathbf{u}_l - \mathbf{u}_k$ = relative velocity

**Drag coefficient correlations:**
- **Stokes regime** (Re < 1): $C_D = \frac{24}{Re_p}$
- **Newton regime** (Re > 1000): $C_D \approx 0.44$
- **Schiller-Naumann**: $C_D = \frac{24}{Re_p}(1 + 0.15 Re_p^{0.687})$

#### 4.2.2 Lift Force

**Physical meaning:** Force due to velocity gradient (shear) in continuous phase

$$\mathbf{F}^L_{kl} = -C_L \rho_c \alpha_d (\mathbf{u}_r \times \boldsymbol{\omega}_c)$$

where:
- $C_L$ = lift coefficient (typically ~0.5 for spheres)
- $\boldsymbol{\omega}_c = \nabla \times \mathbf{u}_c$ = vorticity of continuous phase
- Subscript $d$ = dispersed phase, $c$ = continuous phase

**Direction:** Perpendicular to both relative velocity and vorticity

#### 4.2.3 Virtual Mass Force

**Physical meaning:** Additional inertia when accelerating dispersed phase through continuous phase

$$\mathbf{F}^{VM}_{kl} = C_{VM} \rho_c \alpha_d \left( \frac{D\mathbf{u}_l}{Dt} - \frac{D\mathbf{u}_k}{Dt} \right)$$

where:
- $C_{VM}$ = virtual mass coefficient (0.5 for spheres)
- $\frac{D}{Dt} = \frac{\partial}{\partial t} + \mathbf{u} \cdot \nabla$ = material derivative

**When important:** 
- High acceleration (unsteady flows)
- Large density ratio ($\rho_c/\rho_d \gg 1$)
- Bubble columns, slurry flows

#### 4.2.4 Turbulent Dispersion Force

**Physical meaning:** Spreading of particles due to turbulent fluctuations

$$\mathbf{F}^{TD}_{kl} = -C_{TD} \rho_c k_c \nabla \alpha_d$$

where:
- $C_{TD}$ = turbulent dispersion coefficient (~1.0)
- $k_c$ = turbulent kinetic energy of continuous phase

**Effect:** Homogenizes volume fraction distribution

#### 4.2.5 Wall Lubrication Force

**Physical meaning:** Repulsive force preventing particles from touching walls

$$\mathbf{F}^{WL}_{kl} = \frac{\alpha_d \rho_c}{d_p} f_{WL}(y) (\mathbf{n}_w \cdot \mathbf{u}_r) \mathbf{n}_w$$

where:
- $y$ = distance to wall
- $\mathbf{n}_w$ = wall normal vector
- $f_{WL}(y)$ = decaying function of wall distance

### 4.3 Force Magnitude Comparison

| Flow Type | Dominant Forces | Negligible Forces |
|-----------|-----------------|-------------------|
| **Stokes settling** | Drag, Gravity | Lift, VM, TD |
| **Bubble column** | Drag, Lift, TD | Wall lubrication (bulk) |
| **Rapid mixing** | Drag, VM | TD (transient) |
| **Pipe flow** | Drag, WL, TD | VM (steady) |

---

## 5. Pressure-Velocity Coupling

### 5.1 Mixture Continuity Constraint

Summing mass conservation over all phases:
$$\sum_k \left[ \frac{\partial (\alpha_k \rho_k)}{\partial t} + \nabla \cdot (\alpha_k \rho_k \mathbf{u}_k) \right] = \sum_k \Gamma_k = 0$$

For incompressible phases ($\rho_k$ = constant):
$$\sum_k \nabla \cdot (\alpha_k \mathbf{u}_k) = 0$$

### 5.2 Pressure Equation Derivation

**Step 1:** Take divergence of momentum equation for each phase

**Step 2:** Sum over all phases (assuming shared pressure)

**Step 3:** Use continuity constraint to eliminate velocity divergences

**Result (simplified for incompressible flow):**
$$\nabla \cdot \left[ \sum_k \frac{\alpha_k}{\rho_k} \nabla p \right] = \sum_k \nabla \cdot \mathbf{u}_k^* - \frac{\partial}{\partial t} \sum_k \alpha_k$$

where $\mathbf{u}_k^*$ is the intermediate velocity from momentum prediction.

### 5.3 Solution Algorithm (Simplified PIMPLE)

```
1. Solve momentum equations (predict U*)
2. Solve pressure equation (enforce continuity)
3. Correct velocities and fluxes
4. Update volume fractions
5. Repeat until convergence
```

**Key difference from single-phase:** Volume fractions appear in all terms, requiring strong coupling between phases.

---

## 6. Turbulence Modeling

### 6.1 Challenges in Multiphase Turbulence

1. **Different time/length scales** for each phase
2. **Interphase effects** (wake-induced turbulence)
3. **Damping/enhancement** near interfaces
4. **Bubble-induced turbulence** in dispersed flows

### 6.2 Per-Phase k-ε Model

**Turbulent kinetic energy (phase k):**
$$\frac{\partial (\alpha_k k_k)}{\partial t} + \nabla \cdot (\alpha_k \mathbf{u}_k k_k) = 
\nabla \cdot \left( \alpha_k \frac{\mu_{t,k}}{\sigma_k} \nabla k_k \right) + P_k - \alpha_k \varepsilon_k + \Pi_k$$

**Dissipation rate (phase k):**
$$\frac{\partial (\alpha_k \varepsilon_k)}{\partial t} + \nabla \cdot (\alpha_k \mathbf{u}_k \varepsilon_k) = 
\nabla \cdot \left( \alpha_k \frac{\mu_{t,k}}{\sigma_\varepsilon} \nabla \varepsilon_k \right) + 
C_{1\varepsilon} \frac{\varepsilon_k}{k_k} P_k - C_{2\varepsilon} \alpha_k \frac{\varepsilon_k^2}{k_k} + \Pi_k^\varepsilon$$

**Production term:**
$$P_k = \mu_{t,k} \left[ \nabla \mathbf{u}_k + (\nabla \mathbf{u}_k)^T \right] : \nabla \mathbf{u}_k$$

**Interphase transfer terms:**
- $\Pi_k$ = turbulent kinetic energy exchange between phases
- $\Pi_k^\varepsilon$ = dissipation exchange (often neglected)

### 6.3 Mixture Turbulence Models

**Simpler approach:** Use single-phase model for mixture velocity

**Mixture k-ε:**
$$\frac{\partial (\rho_m k_m)}{\partial t} + \nabla \cdot (\rho_m \mathbf{u}_m k_m) = \nabla \cdot \left( \frac{\mu_{t,m}}{\sigma_k} \nabla k_m \right) + P_m - \rho_m \varepsilon_m$$

where:
- $\rho_m = \sum_k \alpha_k \rho_k$ = mixture density
- $\mathbf{u}_m = \frac{1}{\rho_m} \sum_k \alpha_k \rho_k \mathbf{u}_k$ = mixture velocity

**Limitations:** Cannot capture per-phase turbulence differences

### 6.4 Bubble-Induced Turbulence (BIT)

**Additional source in k-equation:**
$$S_{BIT} = C_{BIT} \frac{\alpha_d \rho_c}{d_p} |\mathbf{u}_r|^3$$

**Physical origin:** Turbulence generated in bubble wakes

**Models:**
- **Sato model**: $\mu_{t,BI} = \rho_c C_{BIT} \alpha_d d_p |\mathbf{u}_r|$
- **More sophisticated:** Resolve wake scales via DNS or LES

---

## 7. Closure Relations Summary

| Term | Closure Type | Typical Correlations |
|------|--------------|----------------------|
| **Drag coefficient** | Empirical | Schiller-Naumann, Ishii-Zuber |
| **Lift coefficient** | Constant/Correlation | $C_L = 0.5$ (spheres), Tomiyama |
| **Virtual mass** | Potential flow theory | $C_{VM} = 0.5$ (spheres) |
| **Turbulent dispersion** | TKE-based | $C_{TD} \approx 1.0$ |
| **Interphase area** | Geometric/PDF | $a_i = \frac{6\alpha_d}{d_p}$ (spherical) |

---

## 8. Mathematical Properties

### 8.1 Well-Posedness Requirements

1. **Hyperbolicity** of characteristic equations (requires virtual mass for certain regimes)
2. **Positivity** of volume fractions ($\alpha_k > 0$)
3. **Boundedness** of phase velocities

### 8.2 Numerical Challenges

- **Stiffness**: Large interphase coupling terms require implicit treatment
- **Volume fraction boundedness**: Requires specialized schemes (MULES in OpenFOAM)
- **Pressure-velocity coupling**: More iterations than single-phase

---

## Concept Check

<details>
<summary><b>1. ทำไมต้อง volume averaging?</b></summary>

เพราะ Euler-Euler ไม่ track interface → ใช้ **averaged properties** แทน → แปลงปัญหาไม่ต่อเนื่อง (discontinuous) ให้เป็นสมการต่อเนื่อง (continuous) ที่แก้ได้ด้วยวิธีคอนตินิวอัม

**Key insight:** Volume averaging allows us to write separate conservation equations for each phase while maintaining coupling through interphase transfer terms.
</details>

<details>
<summary><b>2. Pressure equation มาจากไหน?</b></summary>

จาก **mixture continuity** — บังคับให้ velocity fields รวมกันเป็น divergence-free

**Derivation path:**
1. Sum mass conservation: $\sum_k \nabla \cdot (\alpha_k \mathbf{u}_k) = 0$
2. Take divergence of momentum equations
3. Eliminate velocity terms using continuity
4. Obtain Poisson-type equation for pressure

**Physical meaning:** Pressure adjusts instantaneously to satisfy the constraint that volume fractions sum to unity everywhere.
</details>

<details>
<summary><b>3. $\Pi_k$ คืออะไร?</b></summary>

**Interphase turbulent transfer** — sources/sinks จาก wakes, bubble-induced turbulence

**Components:**
- **Wake production**: Turbulence generated behind particles/bubbles
- **Dissipation modification**: Changed dissipation rates near interfaces
- **Redistribution**: TKE transfer between phases

**Modeling approaches:**
- **Zero-equation**: Algebraic functions of slip velocity
- **Two-equation**: Additional transport for interphase TKE transfer
- **Scale-similarity**: Based on resolved fluctuations
</details>

<details>
<summary><b>4. เมื่อไหร่ต้องใช้ virtual mass force?</b></summary>

**Cases where VM is critical:**
1. High acceleration (rapid transients)
2. Large density ratio ($\rho_c/\rho_d \gg 1$)
3. Unsteady flows (wave tank, sloshing)
4. Bubble columns with large bubbles

**Physical intuition:** When accelerating a bubble through liquid, you must also accelerate the surrounding liquid that moves with the bubble.

**Mathematical role:** VM force provides hyperbolicity to the characteristic equations, improving numerical stability.
</details>

<details>
<summary><b>5. ทำไม drag force สำคัญที่สุด?</b></summary>

**Reasons:**
1. **Magnitude**: Typically 1-2 orders larger than other interphase forces
2. **Determines slip velocity**: Sets relative velocity between phases
3. **Affects all other phenomena**: Mixing, heat/mass transfer depend on slip
4. **Energy dissipation**: Major sink of turbulent kinetic energy

**Order of magnitude (typical):**
- Drag: $O(10^2 - 10^3)$ N/m³
- Lift: $O(1 - 10)$ N/m³
- VM: $O(10 - 100)$ N/m³ (transients only)
- TD: $O(1)$ N/m³

**Modeling priority:** Get drag right first, then consider secondary forces.
</details>

---

## Related Documents

### Prerequisites
- **Governing Equations:** [02_Detailed_Derivation.md](../../../MODULE_01_CFD_FUNDAMENTALS/CONTENT/01_GOVERNING_EQUATIONS/02_Detailed_Derivation.md)
- **Turbulence Modeling:** [02_RANS_Models.md](../../../MODULE_03_SINGLE_PHASE_FLOW/CONTENT/03_TURBULENCE_MODELING/02_RANS_Models.md)
- **Navier-Stokes Derivation:** [02_Detailed_Derivation.md](../../../MODULE_01_CFD_FUNDAMENTALS/CONTENT/01_GOVERNING_EQUATIONS/02_Detailed_Derivation.md)

### Same Module
- **Overview:** [00_Overview.md](00_Overview.md)
- **Concepts:** [01_Introduction.md](01_Introduction.md)
- **Implementation:** [03_Implementation_Concepts.md](03_Implementation_Concepts.md)

### Applied Concepts
- Interphase force correlations → Applied in `interFoam` solver
- Turbulence modeling → Discussed in [Turbulence_Fundamentals](../../../MODULE_03_SINGLE_PHASE_FLOW/CONTENT/03_TURBULENCE_MODELING/01_Turbulence_Fundamentals.md)