# Virtual Mass Overview

ภาพรวม Virtual Mass Force

---

## Learning Objectives

**Learning Objectives | วัตถุประสงค์การเรียนรู้**

- Understand when virtual mass effects are significant in multiphase flows
- Identify which flow regimes require virtual mass modeling
- Configure virtual mass coefficients in OpenFOAM

---

## What is Virtual Mass? | Virtual Mass คืออะไร?

> **Virtual Mass** = Additional apparent mass due to surrounding fluid being accelerated along with a particle
>
> **Virtual Mass** = แรงต้านเพิ่มเติมเนื่องจากต้องเคลื่อนย้าย surrounding fluid เมื่อ particle accelerates

**Physical Picture | ภาพกายภาพ:**

```mermaid
flowchart LR
    A[Bubble Accelerates] --> B[Pushes Liquid]
    B --> C[Added Inertia]
    C --> D[Virtual Mass Force]
```

When a particle accelerates through a continuous phase, it must accelerate the surrounding fluid with it. This adds **apparent inertia** to the particle's motion.

---

## Why is it Important? | ทำไมสำคัญ?

| Scenario | Impact |
|----------|--------|
| **Gas-liquid flows** | ✅ Dominant effect - liquid inertia >> gas inertia |
| **Transient acceleration** | ✅ Critical - rapid velocity changes |
| **Bubble dynamics** | ✅ Essential - controls bubble response time |
| **Solid-gas flows** | ❌ Negligible - solid dominates |

**Key Principle:** Virtual mass matters when dispersed phase density is much lower than continuous phase density.

**Decision Rule:**

$$\text{Include if } \frac{\rho_d}{\rho_c} < 10$$

---

## How to Model? | การจำลอง

### 1. Governing Equation

$$\mathbf{F}_{VM} = C_{VM} \rho_c \alpha_d \left(\frac{D\mathbf{u}_c}{Dt} - \frac{D\mathbf{u}_d}{Dt}\right)$$

| Symbol | Meaning |
|--------|---------|
| $C_{VM}$ | Virtual mass coefficient |
| $\rho_c$ | Continuous phase density |
| $\alpha_d$ | Dispersed phase volume fraction |
| $D/Dt$ | Material derivative |

### 2. Virtual Mass Coefficient

| Shape | $C_{VM}$ | Notes |
|-------|----------|-------|
| Sphere | 0.5 | From potential flow theory |
| Oblate | > 0.5 | Flattened shapes |
| Prolate | < 0.5 | Elongated shapes |

### 3. OpenFOAM Configuration

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

---

## Key Takeaways | สรุปสำคัญ

- ✅ **Virtual mass = apparent inertia** from accelerating surrounding fluid
- ✅ **Critical for gas-liquid** systems where $\rho_d \ll \rho_c$
- ✅ **$C_{VM} = 0.5$ for spheres** from potential flow theory
- ✅ **Negligible for solid-gas** - particle inertia dominates
- ✅ **Configure in `virtualMass` sub-dictionary** in OpenFOAM

---

## Quick Reference | อ้างอิงรวดเร็ว

| Parameter | Value | When to Use |
|-----------|-------|-------------|
| Sphere $C_{VM}$ | 0.5 | Default for spherical particles |
| Gas-liquid flows | **Include** | Always significant |
| Liquid-liquid | Maybe | Check density ratio |
| Solid-gas | Skip | Negligible effect |
| $\rho_d/\rho_c < 10$ | **Include** | General rule |

---

## Concept Check | ทดสอบความเข้าใจ

<details>
<summary><b>1. ทำไมเรียก "virtual" mass?</b></summary>

เพราะไม่ใช่ mass จริงของ particle — เป็น **apparent mass** เนื่องจาก surrounding fluid ที่ถูกเคลื่อนย้าย
</details>

<details>
<summary><b>2. $C_{VM} = 0.5$ มาจากไหน?</b></summary>

จาก **potential flow theory** รอบ sphere — fluid "attached" มีปริมาตร = ครึ่งหนึ่งของ sphere
</details>

<details>
<summary><b>3. ทำไม solid-gas ไม่ต้องใช้?</b></summary>

เพราะ solid มี **density สูงกว่า gas มาก** — particle inertia dominate อยู่แล้ว
</details>

---

## Related Documents | เอกสารที่เกี่ยวข้อง

**Prerequisites:**
- [../01_FUNDAMENTAL_CONCEPTS/02_Interfacial_Phenomena.md](../../01_FUNDAMENTAL_CONCEPTS/02_Interfacial_Phenomena.md)

**Parallel Concepts:**
- [../01_DRAG/00_Overview.md](../01_DRAG/00_Overview.md) - Primary interphase force
- [../02_LIFT/00_Overview.md](../02_LIFT/00_Overview.md) - Shear-induced forces

**Module Overview:**
- [../00_Overview.md](../00_Overview.md) - All interphase forces