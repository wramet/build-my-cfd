# Virtual Mass - Fundamental Concepts

แนวคิดพื้นฐานของ Virtual Mass

---

## Overview

> **Virtual Mass** = แรงต้านเพิ่มเติมเมื่อ particle/bubble accelerate เนื่องจากต้องเคลื่อนย้าย surrounding fluid

---

## 1. Physical Origin

### Why "Virtual"?

- เมื่อ bubble เร่ง → ต้องเคลื่อนย้าย liquid รอบๆ
- Liquid ถูก accelerate ด้วย → เพิ่ม apparent mass
- "Virtual" เพราะไม่ใช่ mass จริงของ bubble

### Effective Mass

$$m_{eff} = m_{bubble} + C_{VM} \cdot m_{displaced}$$

For sphere: $C_{VM} = 0.5$
$$m_{eff} = m_{bubble} + 0.5 \cdot \frac{4}{3}\pi r^3 \rho_{liquid}$$

---

## 2. Force Equation

$$\mathbf{F}_{VM} = C_{VM} \rho_c \alpha_d \left(\frac{D\mathbf{u}_c}{Dt} - \frac{D\mathbf{u}_d}{Dt}\right)$$

| Symbol | Meaning |
|--------|---------|
| $C_{VM}$ | Virtual mass coefficient |
| $\rho_c$ | Continuous phase density |
| $\alpha_d$ | Dispersed phase fraction |
| $D/Dt$ | Material derivative |

### Material Derivative

$$\frac{D\mathbf{u}}{Dt} = \frac{\partial \mathbf{u}}{\partial t} + (\mathbf{u} \cdot \nabla)\mathbf{u}$$

---

## 3. Virtual Mass Coefficient

### Shape Dependence

| Shape | $C_{VM}$ |
|-------|----------|
| Sphere | 0.5 |
| Oblate ellipsoid | > 0.5 |
| Prolate ellipsoid | < 0.5 |
| Cylinder (L/D = 1) | 0.68 |

### Theoretical Derivation

From potential flow around sphere:
$$C_{VM} = \frac{1}{2}$$

---

## 4. When to Include

| Condition | Include? |
|-----------|----------|
| ρ_d << ρ_c (gas-liquid) | **Yes** |
| ρ_d ≈ ρ_c (liquid-liquid) | Usually no |
| ρ_d >> ρ_c (solid-gas) | No |
| Transient/oscillating | **Yes** |
| Steady uniform flow | Less important |

### Rule of Thumb

Include VM when:
$$\frac{\rho_d}{\rho_c} < 10$$

---

## 5. Concentration Effects

### Zuber Correlation

$$C_{VM}^{eff} = C_{VM}(1 + 2.78\alpha_d)$$

At high α_d, effective VM increases due to nearby particles.

---

## 6. Physical Examples

### Rising Bubble

- Bubble accelerates upward
- Must push liquid aside
- Effective mass ≈ 1.5× bubble mass

### Oscillating Bubble

- Period depends on effective mass
- $T = 2\pi\sqrt{m_{eff}/k}$
- Experiments confirm $C_{VM} \approx 0.5$

---

## 7. OpenFOAM Configuration

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

## Quick Reference

| Parameter | Value |
|-----------|-------|
| Sphere $C_{VM}$ | 0.5 |
| Gas-liquid | Include |
| Liquid-liquid | Usually skip |
| Solid-gas | Skip |

---

## Concept Check

<details>
<summary><b>1. ทำไม bubble มี effective mass > actual mass?</b></summary>

เพราะต้อง **accelerate surrounding liquid** ด้วย — liquid ที่ถูกเคลื่อนย้ายเพิ่ม inertia ให้ bubble
</details>

<details>
<summary><b>2. $C_{VM} = 0.5$ มาจากไหน?</b></summary>

จาก **potential flow theory** — fluid "attached" กับ sphere มีปริมาตร = ครึ่งหนึ่งของ sphere volume
</details>

<details>
<summary><b>3. ทำไม solid-gas ไม่ต้องใช้ VM?</b></summary>

เพราะ **solid มี density สูงกว่า gas มาก** — particle inertia dominate อยู่แล้ว, gas displacement negligible
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **OpenFOAM Implementation:** [02_OpenFOAM_Implementation.md](02_OpenFOAM_Implementation.md)
- **Drag Overview:** [../01_DRAG/00_Overview.md](../01_DRAG/00_Overview.md)