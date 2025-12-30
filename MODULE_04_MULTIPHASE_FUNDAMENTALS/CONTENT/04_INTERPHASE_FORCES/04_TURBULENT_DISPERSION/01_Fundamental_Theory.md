# Turbulent Dispersion - Fundamental Theory

ทฤษฎีพื้นฐานของ Turbulent Dispersion: การกระจายตัวของอนุภาคจากความปั่นป่วน

---

## Learning Objectives

หลังจากศึกษาบทนี้ คุณควรจะสามารถ:
- **อนุมาน**สมการ turbulent dispersion force จากหลักการพื้นฐานของ turbulence kinetics
- **อธิบาย**กลไกทางฟิสิกส์ของ turbulent eddies ที่ส่งผลต่อการกระจายตัวของ particles/bubbles
- **วิเคราะห์**บทบาทของ Stokes number ที่กำหนดพฤติกรรมของ particles ในสนามความปั่นป่วน
- **คำนวณ**dispersion coefficient จาก turbulence kinetic energy และ turbulence viscosity
- **แยกแยะ**regimes ที่แตกต่างของ particle-turbulence interaction ด้วย Stokes number analysis
- **เชื่อมโยง**turbulent dispersion กับ turbulent diffusion ใน single-phase flows

---

## Why This Matters

> "Understanding why turbulent dispersion occurs enables you to predict when it matters, select appropriate models, and interpret simulation results correctly."

Turbulent dispersion เป็น **กลไกที่สำคัญที่สุด**ในการกระจายตัวของ dispersed phase ใน flows ที่มีความปั่นป่วนสูง การเข้าใจตั้งแต่พื้นฐานทางทฤษฎีจะช่วยให้คุณ:
- ทำนายว่าเมื่อไร turbulent dispersion จะสำคัญ
- เลือกโมเดลที่เหมาะสมกับ regime ที่สนใจ
- ตีความผลลัพธ์จากการจำลองได้อย่างถูกต้อง

---

## 1. Physical Mechanism: Why Dispersion Occurs

### 1.1 Turbulent Eddies as Transport Agents

Turbulent flow ประกอบด้วย **eddies ขนาดต่างๆ** ที่เคลื่อนที่แบบสุ่ม:

- **Large eddies** → Transport particles over long distances
- **Small eddies** → Mix particles locally
- **Random motion** → Net transport from high to low concentration

### 1.2 The Dispersion Process

```
High α → Turbulent eddies pick up particles → Random transport → Low α
```

**Key insight:** Eddies ทำหน้าที่เหมือน "random walkers" ที่พา particles เดินทางแบบสุ่ม → **Net transport** จากความเข้มข้นสูงไปต่ำ

### 1.3 Analogy: Smoke in Turbulent Air

เหมือน **ควันกระจายในอากาศปั่นป่วน**:
- Eddies พาควันไปทิศทางสุ่ม → กระจายตัวออก
- ถ้าไม่มี turbulence → ควันจะลอยตรง (advection only)
- ถ้ามี turbulence → ควันกระจาย (advection + dispersion)

---

## 2. Mathematical Foundation: First Principles

### 2.1 Reynolds Decomposition

ใน turbulent flows, velocity ถูกแยกเป็น:
$$\mathbf{u} = \overline{\mathbf{u}} + \mathbf{u}'$$

| Symbol | Meaning |
|--------|---------|
| $\overline{\mathbf{u}}$ | Mean velocity |
| $\mathbf{u}'$ | Fluctuating velocity (turbulence) |

### 2.2 Particle Equation of Motion

สำหรับ particle ขนาดเล็กใน turbulent flow:
$$\frac{d\mathbf{u}_p}{dt} = \frac{\mathbf{u} - \mathbf{u}_p}{\tau_p}$$

where:
$$\tau_p = \frac{\rho_p d_p^2}{18\mu_c}$$

### 2.3 Derivation of Dispersion Force

จากการ averaged momentum equation สำหรับ dispersed phase:

**Step 1:** Reynolds averaging ของ dispersed phase momentum:
$$\overline{\alpha_d \mathbf{u}_d \mathbf{u}_d} = \alpha_d \overline{\mathbf{u}}_d \overline{\mathbf{u}}_d + \overline{\alpha_d \mathbf{u}'_d \mathbf{u}'_d}$$

**Step 2:** Closure problem → ต้องการ model สำหรับ $\overline{\alpha_d \mathbf{u}'_d \mathbf{u}'_d}$

**Step 3:** Gradient diffusion hypothesis:
$$\overline{\alpha_d \mathbf{u}'_d \mathbf{u}'_d} = -D_{TD} \nabla \alpha_d$$

**Final form:**
$$\mathbf{F}_{TD} = -D_{TD} \nabla \alpha_d$$

### 2.4 Dispersion Coefficient Derivation

จาก **turbulence kinetic energy (k)**:

**Dimensional analysis:**
$$D_{TD} \sim u' \cdot l$$

where:
- $u' \sim \sqrt{\frac{2}{3}k}$ (turbulence velocity scale)
- $l$ (turbulence length scale)

**Result:**
$$D_{TD} = C_{TD} \rho_c k_c$$

หรือจาก **turbulent viscosity**:
$$D_{TD} = C_{TD} \rho_c \nu_t$$

where:
$$\nu_t = C_\mu \frac{k^2}{\varepsilon}$$

### 2.5 Connection to Turbulent Diffusion

ใน single-phase flows:
$$D_t = \frac{\nu_t}{Sc_t}$$

| Variable | Meaning |
|----------|---------|
| $\nu_t$ | Turbulent viscosity |
| $Sc_t$ | Turbulent Schmidt number (~0.9) |

**สำหรับ multiphase:** Turbulent dispersion ≈ turbulent diffusion + inertia effects

---

## 3. Stokes Number Analysis

### 3.1 Definition

$$St = \frac{\tau_p}{\tau_f} = \frac{\text{Particle response time}}{\text{Turbulence time scale}}$$

where:
- $\tau_p = \frac{\rho_p d_p^2}{18\mu_c}$ (particle relaxation time)
- $\tau_f = \frac{k}{\varepsilon}$ (turbulence time scale)

### 3.2 Physical Interpretation

| Stokes Number | Physical Meaning | Particle Behavior |
|--------------|------------------|-------------------|
| $St \ll 1$ | Particles respond fast | **Follows turbulent eddies** |
| $St \sim 1$ | Particle inertia ≈ turbulence | **Partial correlation** |
| $St \gg 1$ | Particles respond slow | **Unaffected by turbulence** |

### 3.3 Regime Diagram

```
Dispersion Effectiveness vs Stokes Number:

St << 1: ██████████ (Maximum dispersion)
St ~  1: ██████░░░░ (Moderate dispersion)
St >> 1: ██░░░░░░░░ (Minimal dispersion)
```

### 3.4 Practical Implications

**Bubble columns (St << 1):**
- Bubbles follow eddies ได้ดี
- Dispersion สำคัญมาก → จำลองแรงดันสูงต้องรวม TD

**Fluidized beds (St ~ 1):**
- Partial dispersion
- ต้องพิจารณาร่วมกับโมเดลอื่น

**Spray flows (St >> 1):**
- Droplets unaffected โดย turbulence
- Dispersion น้อย → อาจละเว้น TD

---

## 4. Effect on Phase Distribution

### 4.1 Without Turbulent Dispersion

เมื่อไม่มี TD:
- **Sharp α gradients** ถูกรักษา
- Particles อาจ concentrate ในบาง regions
- Unphysical clustering → ไม่ realistic

### 4.2 With Turbulent Dispersion

เมื่อมี TD:
- **α profile flattens** → กระจายตัวดีขึ้น
- More realistic mixing
- Improved prediction ของ holdup และ residence time

### 4.3 Quantitative Impact

เมื่อ $D_{TD}$ เพิ่มขึ้น:
- **Mixing length** ↑ → particles travel farther
- **Concentration gradients** ↓ → more uniform
- **Residence time distribution** ↑ → broader RTD curve

---

## 5. Key Parameters Summary

| Parameter | Physical Meaning | Effect on Dispersion |
|-----------|-----------------|----------------------|
| $C_{TD}$ ↑ | Model coefficient | More dispersion |
| $k$ ↑ | Turbulence intensity | More dispersion |
| $\nu_t$ ↑ | Turbulent viscosity | More dispersion |
| $\nabla\alpha$ ↑ | Concentration gradient | Stronger TD force |
| $St$ ↑ | Particle inertia | Less dispersion (for St >> 1) |

---

## Theoretical Insights

### Insight 1: Dispersion ≠ Diffusion

- **Diffusion**: Molecular scale (random molecular motion)
- **Dispersion**: Turbulent eddies scale (random eddy motion)

แต่ทั้งคู่ใช้ gradient diffusion model!

### Insight 2: Two-Way Coupling

Particles ก็ส่งผลกลับไปที่ turbulence ด้วย:
- **High α** → Turbulence modulation (damping/enhancement)
- **Small particles** → May increase turbulence
- **Large particles** → May suppress turbulence

### Insight 3: Anisotropy Matters

ใน reality, turbulent dispersion **ไม่ isotropic**:
- **Vertical** dispersion ≠ **Horizontal** dispersion
- Buoyancy + gravity ส่งผลต่อ dispersion patterns

---

## Concept Check

<details>
<summary><b>1. ทำไม turbulent dispersion force มีทิศทางตรงข้ามกับ α gradient?</b></summary>

เพราะ eddies พา particles จาก **high concentration → low concentration** → Net transport ลง gradient เหมือน diffusion process
</details>

<details>
<summary><b>2. Stokes number บอกอะไรเกี่ยวกับ particle-turbulence interaction?</b></summary>

$St = \tau_p/\tau_f$ บอกว่า particle จะ **follow turbulent eddies** หรือไม่:
- $St \ll 1$: Follows eddies → high dispersion
- $St \gg 1$: Unaffected → low dispersion
</details>

<details>
<summary><b>3. ทำไม dispersion coefficient เกี่ยวข้องกับ k (turbulence kinetic energy)?</b></summary>

เพราะ $k \sim u'^2$ และ $D_{TD} \sim u' \cdot l$ → Turbulence ที่แข็งแรง ($k$ สูง) มี velocity fluctuations ที่ใหญ่ → Transport particles ได้ดีขึ้น
</details>

<details>
<summary><b>4. Dispersion และ diffusion ต่างกันอย่างไร?</b></summary>

- **Diffusion**: Molecular scale (random molecular motion)
- **Dispersion**: Turbulent eddy scale (random eddy motion)
แต่ใช้ gradient diffusion model เหมือนกัน!
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md) - Quick start และ model selection guidance
- **Specific Models:** [02_Specific_Models.md](02_Specific_Models.md) - Model implementation และ tuning
- **Drag Overview:** [../01_DRAG/00_Overview.md](../01_DRAG/00_Overview.md) - Drag forces ที่เกี่ยวข้อง
- **Lift Overview:** [../02_LIFT/00_Overview.md](../02_LIFT/00_Overview.md) - Lift forces ที่อาจ interact กับ dispersion