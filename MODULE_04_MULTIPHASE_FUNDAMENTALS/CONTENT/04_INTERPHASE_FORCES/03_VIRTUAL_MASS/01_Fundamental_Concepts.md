# 01_Fundamental_Concepts.md

# Virtual Mass - Fundamental Concepts

แนวคิดพื้นฐานของ Virtual Mass

---

## Learning Objectives | วัตถุประสงค์การเรียนรู้

After completing this section, you should be able to:
- **Explain** the physical origin of virtual mass force and when it becomes significant
- **Calculate** effective mass of particles/bubbles with virtual mass contribution
- **Apply** the virtual mass force equation in multiphase flow calculations
- **Determine** appropriate virtual mass coefficients for different geometries
- **Evaluate** when to include virtual mass effects in your simulations

หลังจากเรียนบทนี้ คุณควรจะสามารถ:
- **อธิบาย** แหล่งกำเนิดทางกายภาพของแรง virtual mass และเมื่อไหร่ที่มันมีความสำคัญ
- **คำนวณ** มวลมีประสิทธิภาพของอนุภาค/ฟองโดยคำนึงถึง virtual mass
- **ใช้สมการ** virtual mass force ในการคำนวณการไหลแบบหลายเฟส
- **กำหนด** สัมประสิทธิ์ virtual mass ที่เหมาะสมสำหรับรูปทรงต่างๆ
- **ประเมิน** เมื่อไหร่ควรรวมผลของ virtual mass ในการจำลอง

---

## Overview

> **Virtual Mass** = แรงต้านเพิ่มเติมเมื่อ particle/bubble accelerate เนื่องจากต้องเคลื่อนย้าย surrounding fluid

**Key Insight:** When a particle accelerates through a fluid, it must also accelerate the surrounding fluid. This creates an **apparent mass increase** that affects the particle's dynamics, even though the additional mass is not physically attached to the particle.

---

## 1. Physical Origin

### Why "Virtual"?

**แนวคิดพื้นฐาน:** เมื่อ bubble/particle เร่งความเร็วใน fluid → ต้องเคลื่อนย้าย fluid รอบๆ → fluid ถูก accelerate ด้วย → เพิ่ม apparent mass → เรียกว่า "Virtual" เพราะไม่ใช่ mass จริงของ particle

| Aspect | Description |
|--------|-------------|
| **What** | Added mass effect from accelerating surrounding fluid |
| **Why** | Fluid must be displaced and accelerated with the particle |
| **When** | Significant during acceleration and deceleration phases |
| **Where** | Gas-liquid systems, bubbly flows, particle-laden flows |

### Fundamental Mechanism

Consider a bubble accelerating through liquid:
1. Bubble pushes liquid aside as it moves
2. Liquid in the bubble's path gains kinetic energy
3. This liquid acceleration resists the bubble's motion
4. Effectively, bubble behaves as if it has more mass

**The "Virtual" Component:**
- Not real mass attached to the bubble
- Apparent inertia from fluid coupling
- Depends on displaced fluid volume, not bubble material

---

## 2. Effective Mass Formulation

### Basic Equation

$$m_{eff} = m_{particle} + C_{VM} \cdot m_{displaced}$$

For a spherical particle of radius $r$:

$$m_{eff} = m_{particle} + C_{VM} \cdot \frac{4}{3}\pi r^3 \rho_{continuous}$$

### Mass Ratio Analysis

$$\frac{m_{eff}}{m_{particle}} = 1 + C_{VM} \frac{\rho_{continuous}}{\rho_{particle}}$$

**Example: Air bubble in water**
- $\rho_{air} \approx 1.2$ kg/m³
- $\rho_{water} \approx 1000$ kg/m³
- $C_{VM} = 0.5$ (sphere)
- $m_{eff}/m_{bubble} \approx 1 + 0.5 \times \frac{1000}{1.2} \approx 418$

The bubble behaves as if it has ~400× its actual mass!

---

## 3. Virtual Mass Force Equation

### General Form

$$\mathbf{F}_{VM} = C_{VM} \rho_c \alpha_d \left(\frac{D\mathbf{u}_c}{Dt} - \frac{D\mathbf{u}_d}{Dt}\right)$$

### Symbol Definitions

| Symbol | Meaning | Typical Units |
|--------|---------|---------------|
| $\mathbf{F}_{VM}$ | Virtual mass force | N/m³ |
| $C_{VM}$ | Virtual mass coefficient | - |
| $\rho_c$ | Continuous phase density | kg/m³ |
| $\alpha_d$ | Dispersed phase volume fraction | - |
| $\mathbf{u}_c, \mathbf{u}_d$ | Phase velocities | m/s |
| $D/Dt$ | Material derivative | s⁻¹ |

### Material Derivative

The material derivative represents acceleration following the fluid motion:

$$\frac{D\mathbf{u}}{Dt} = \frac{\partial \mathbf{u}}{\partial t} + (\mathbf{u} \cdot \nabla)\mathbf{u}$$

| Component | Physical Meaning |
|-----------|------------------|
| $\frac{\partial \mathbf{u}}{\partial t}$ | Local acceleration (time-dependent) |
| $(\mathbf{u} \cdot \nabla)\mathbf{u}$ | Convective acceleration (spatial) |

### Force Direction

- **Positive** when continuous phase accelerates faster than dispersed phase
- **Negative** when dispersed phase accelerates faster
- Always opposes **relative acceleration** between phases

---

## 4. Virtual Mass Coefficient

### Shape Dependence

| Shape | $C_{VM}$ | Application |
|-------|----------|-------------|
| Sphere | 0.5 | Bubbles, droplets, spherical particles |
| Oblate ellipsoid (flat) | > 0.5 | Disc-shaped bubbles |
| Prolate ellipsoid (elongated) | < 0.5 | Elongated drops, filaments |
| Cylinder (L/D = 1) | 0.68 | Short fibers |
| Cylinder (L/D → ∞) | 1.0 | Long fibers in cross-flow |

### Theoretical Foundation

**Potential Flow Around a Sphere:**

For inviscid, irrotational flow around a sphere:
- Kinetic energy of fluid = $\frac{1}{2} \times$ (sphere volume) × $\rho_{fluid} \times u^2$
- This gives $C_{VM} = \frac{1}{2}$

**Derivation Key Points:**
- Assumes potential flow (no viscosity, no separation)
- Valid for high Reynolds numbers
- Reasonably accurate for bubbles/drops with clean interfaces

### Experimental Validation

| Study | System | Measured $C_{VM}$ |
|-------|--------|-------------------|
| Auton et al. (1988) | Clean bubble | 0.5 - 0.6 |
| Odar & Hamilton (1964) | Oscillating sphere | 0.5 - 1.0 |
| Rivero et al. (1991) | Contaminated bubble | Up to 2.0 |

---

## 5. When to Include Virtual Mass

### Decision Matrix

| Condition | Include VM? | Reason |
|-----------|-------------|--------|
| $\rho_d \ll \rho_c$ (gas-liquid) | **YES** | Displaced fluid mass >> particle mass |
| $\rho_d \approx \rho_c$ (liquid-liquid) | Maybe | Depends on acceleration magnitude |
| $\rho_d \gg \rho_c$ (solid-gas) | No | Particle inertia dominates |
| Transient/oscillating flow | **YES** | Acceleration is significant |
| Unsteady startup/shutdown | **YES** | Rapid acceleration changes |
| Steady uniform flow | No | Acceleration ≈ 0 |

### Quantitative Criterion

**Include VM when:**
$$\frac{\rho_d}{\rho_c} < 10 \quad \text{OR} \quad \left|\frac{D\mathbf{u}}{Dt}\right| \text{ is significant}$$

**Alternative criterion (relative importance):**
$$\frac{F_{VM}}{F_{drag}} \sim \frac{C_{VM} \cdot (\rho_c/\rho_d) \cdot (du/dt) \cdot D}{u^2} > 0.1$$

### Flow Regime Guidance

| Flow Type | VM Importance |
|-----------|---------------|
| **Bubbly flow** (gas-liquid) | Critical |
| **Slurry flow** (solid-liquid) | Often important |
| **Pneumatic transport** (solid-gas) | Negligible |
| **Atomization** (liquid-gas) | Depends on droplet size |
| **Wave breaking** | Important |

---

## 6. Concentration Effects

### Zuber Correlation (1964)

**เมื่อ volume fraction สูง — particle ใกล้กัน → interaction effect increases effective VM**

$$C_{VM}^{eff} = C_{VM} (1 + 2.78\alpha_d)$$

### Physical Interpretation

| Regime | Behavior |
|--------|----------|
| $\alpha_d < 0.05$ | Dilute: $C_{VM}^{eff} \approx C_{VM}$ (no interaction) |
| $0.05 < \alpha_d < 0.3$ | Moderate: Linear increase in VM |
| $\alpha_d > 0.3$ | Dense: Significant VM enhancement |

**Why does VM increase with concentration?**
1. Nearby particles restrict fluid motion paths
2. Fluid cannot flow freely around individual particles
3. More fluid is "locked" between particles
4. Collective displacement requires more fluid acceleration

### Applicability of Zuber Correlation

**Best for:**
- Spherical particles at moderate Reynolds numbers
- Uniformly dispersed particles
- Volume fractions up to ~0.3-0.4

**Limitations:**
- Assumes uniform distribution
- Less accurate for highly clustered flows
- May over-predict at very high $\alpha_d$

### Alternative Correlations

| Correlation | Formula | Range |
|-------------|---------|-------|
| Zuber (1964) | $C_{VM}(1 + 2.78\alpha_d)$ | $\alpha_d < 0.3$ |
| Biesheuvel & Spoelstra (1989) | $C_{VM}(1 + 3.2\alpha_d)$ | $\alpha_d < 0.4$ |
| Empirical adjustment | $C_{VM}(1 + k\alpha_d^{2/3})$ | Wide range |

---

## 7. Physical Examples

### Example 1: Rising Bubble

**Scenario:** Air bubble rising in water

| Parameter | Value |
|-----------|-------|
| Bubble radius | 2 mm |
| $\rho_{air}$ | 1.2 kg/m³ |
| $\rho_{water}$ | 1000 kg/m³ |

**Calculation:**
$$\frac{m_{eff}}{m_{bubble}} = 1 + 0.5 \times \frac{1000}{1.2} \approx 418$$

**Physical consequence:**
- Bubble accelerates much more slowly than expected from its mass alone
- Terminal velocity is reached quickly
- Oscillation frequency is reduced

### Example 2: Oscillating Bubble

**Natural frequency with virtual mass:**

$$T = 2\pi\sqrt{\frac{m_{eff}}{k}} = 2\pi\sqrt{\frac{m_{bubble} + C_{VM}m_{displaced}}{k}}$$

Where $k$ is the restoring force constant (buoyancy + surface tension).

**Experimental validation:**
- Clean bubbles: $C_{VM} \approx 0.5$ matches theory
- Contaminated bubbles: $C_{VM}$ up to 2.0 (interface rigidity)

### Example 3: Particle-Laden Turbulence

**In turbulent pipe flow with particles:**

Virtual mass affects:
- Particle response time: $\tau_p = \frac{m_{eff}}{6\pi\mu r}$
- Turbulent dispersion characteristics
- Clustering behavior

---

## 8. OpenFOAM Configuration Reference

### Basic Setup

```cpp
virtualMass
{
    (air in water)
    {
        type    constantCoefficient;
        Cvm     0.5;
    }
}
```

### Multiple Phase Pairs

```cpp
virtualMass
{
    (air in water)
    {
        type    constantCoefficient;
        Cvm     0.5;
    }
    
    (oil in water)
    {
        type    constantCoefficient;
        Cvm     0.5;
    }
}
```

### Field-Dependent Coefficient

```cpp
virtualMass
{
    (air in water)
    {
        type    table;
        values
        (
            (0 0.5)      // Low alpha
            (0.1 0.6)    // Increasing
            (0.2 0.78)   // Zuber correlation
            (0.3 0.95)
        );
    }
}
```

---

## Quick Reference

### Common $C_{VM}$ Values

| Geometry | $C_{VM}$ |
|----------|----------|
| Sphere | 0.5 |
| Cylinder (L/D=1) | 0.68 |
| Long cylinder | 1.0 |

### When to Use

| System | Include VM? |
|--------|-------------|
| Gas-liquid | **Yes** |
| Liquid-liquid | Maybe |
| Solid-gas | No |
| Solid-liquid | Usually yes |

### Key Equations

$$\mathbf{F}_{VM} = C_{VM} \rho_c \alpha_d \left(\frac{D\mathbf{u}_c}{Dt} - \frac{D\mathbf{u}_d}{Dt}\right)$$

$$C_{VM}^{eff} = C_{VM} (1 + 2.78\alpha_d)$$

---

## Key Takeaways | สรุปสำคัญ

### Core Concepts
1. **Virtual mass is NOT real mass** — it's apparent inertia from accelerating surrounding fluid
2. **Significant when** $\rho_d \ll \rho_c$ — gas-liquid systems most affected
3. **Most important during acceleration** — steady flow can often neglect VM
4. **Shape matters** — $C_{VM}$ ranges from 0.5 (sphere) to >1.0 (elongated shapes)

### Practical Guidelines
- **Include VM for**: bubbly flows, slurry flows, unsteady multiphase flows
- **Neglect VM for**: solid-gas flows, steady-state calculations (unless acceleration is large)
- **Concentration effects**: Use Zuber correlation when $\alpha_d > 0.05$
- **Default value**: $C_{VM} = 0.5$ for spherical particles

### Common Pitfalls
- ❌ Forgetting VM in gas-liquid systems → under-predicted inertia
- ❌ Using $C_{VM} = 0.5$ for non-spherical particles → incorrect force magnitude
- ❌ Neglecting concentration effects at high $\alpha_d$ → under-predicted VM
- ❌ Including VM in steady uniform flow → unnecessary computational cost

### สรุปภาษาไทย
- **Virtual Mass** = มวลเสมือนจากการเร่ง fluid รอบๆ particle
- **สำคัญที่สุด** เมื่อ density ต่างกันมาก (gas-liquid)
- **ช่วงเวลาสำคัญ** ขณะเร่ง/ลดความเร็ว (unsteady)
- **ค่าพื้นฐาน** $C_{VM} = 0.5$ สำหรับ sphere

---

## Concept Check | ทดสอบความเข้าใจ

<details>
<summary><b>1. ทำไม bubble มี effective mass > actual mass?</b></summary>

เพราะต้อง **accelerate surrounding liquid** ด้วย — liquid ที่ถูกเคลื่อนย้ายเพิ่ม inertia ให้ bubble

**Physical explanation:**
- Bubble displaces liquid as it moves
- This displaced liquid gains kinetic energy
- Energy must come from bubble's work
- Effectively increases bubble's inertia

</details>

<details>
<summary><b>2. $C_{VM} = 0.5$ มาจากไหน?</b></summary>

จาก **potential flow theory** — fluid "attached" กับ sphere มีปริมาตร = ครึ่งหนึ่งของ sphere volume

**Derivation:**
- Assumes inviscid, irrotational flow
- Kinetic energy of fluid = $\frac{1}{2} \rho V u^2$
- This gives added mass = $\frac{1}{2} \rho V_{sphere}$
- Valid for clean interfaces at high Re

</details>

<details>
<summary><b>3. ทำไม solid-gas ไม่ต้องใช้ VM?</b></summary>

เพราะ **solid มี density สูงกว่า gas มาก** — particle inertia dominate อยู่แล้ว, gas displacement negligible

**Quantitative example:**
- Sand particle: $\rho \approx 2600$ kg/m³
- Air: $\rho \approx 1.2$ kg/m³
- $\rho_{solid}/\rho_{gas} \approx 2167 \gg 10$
- VM contribution < 0.1% of particle mass

</details>

<details>
<summary><b>4. เมื่อไหร่ควรใช้ Zuber correlation?</b></summary>

เมื่อ **dispersed phase fraction > 0.05** — particle interaction เริ่มสำคัญ

**Signs you need Zuber:**
- Volume fraction α_d > 0.05 (5%)
- Moderately concentrated suspensions
- Uniformly distributed particles
- Avoid at very high α_d (> 0.4) where more complex models needed

</details>

<details>
<summary><b>5. Virtual mass force ทำงานในทิศทางไหน?</b></summary>

Virtual mass force **opposes relative acceleration** ระหว่างเฟส

$$\mathbf{F}_{VM} \propto \left(\frac{D\mathbf{u}_c}{Dt} - \frac{D\mathbf{u}_d}{Dt}\right)$$

**Direction rules:**
- Points toward dispersed phase if continuous accelerates faster
- Points toward continuous phase if dispersed accelerates faster
- Always resists velocity difference changes

</details>

---

## Related Documents

### Prerequisites
- **Multiphase Flow Fundamentals:** [../01_FUNDAMENTAL_CONCEPTS/00_Overview.md](../01_FUNDAMENTAL_CONCEPTS/00_Overview.md)
- **Interfacial Phenomena:** [../01_FUNDAMENTAL_CONCEPTS/02_Interfacial_Phenomena.md](../01_FUNDAMENTAL_CONCEPTS/02_Interfacial_Phenomena.md)

### Complementary Forces
- **Drag Force:** [../01_DRAG/00_Overview.md](../01_DRAG/00_Overview.md)
- **Lift Force:** [../02_LIFT/00_Overview.md](../02_LIFT/00_Overview.md)

### Implementation
- **Mathematical Framework:** [02_Mathematical_Framework.md](02_Mathematical_Framework.md)
- **OpenFOAM Implementation:** [03_OpenFOAM_Implementation.md](03_OpenFOAM_Implementation.md)

### Module Overview
- **Virtual Mass Overview:** [00_Overview.md](00_Overview.md)