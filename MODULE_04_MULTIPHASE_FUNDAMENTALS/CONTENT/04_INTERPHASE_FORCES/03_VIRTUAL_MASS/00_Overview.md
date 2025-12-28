# Virtual Mass Overview

ภาพรวม Virtual Mass Force

---

## Overview

> **Virtual Mass** = แรงต้านเพิ่มเติมเนื่องจากต้องเคลื่อนย้าย surrounding fluid เมื่อ particle accelerates

```mermaid
flowchart LR
    A[Bubble Accelerates] --> B[Pushes Liquid]
    B --> C[Added Inertia]
    C --> D[Virtual Mass Force]
```

---

## 1. Basic Equation

$$\mathbf{F}_{VM} = C_{VM} \rho_c \alpha_d \left(\frac{D\mathbf{u}_c}{Dt} - \frac{D\mathbf{u}_d}{Dt}\right)$$

| Symbol | Meaning |
|--------|---------|
| $C_{VM}$ | Virtual mass coefficient |
| $\rho_c$ | Continuous phase density |
| $D/Dt$ | Material derivative |

---

## 2. Virtual Mass Coefficient

| Shape | $C_{VM}$ |
|-------|----------|
| Sphere | 0.5 |
| Oblate | > 0.5 |
| Prolate | < 0.5 |

---

## 3. When to Include

| System | Include? |
|--------|----------|
| Gas-liquid | **Yes** |
| Liquid-liquid | Usually no |
| Solid-gas | No |
| Transient flow | **Yes** |

### Rule

$$\text{Include if } \frac{\rho_d}{\rho_c} < 10$$

---

## 4. OpenFOAM Configuration

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

## 5. Physical Interpretation

### Effective Mass

$$m_{eff} = m_{particle} + C_{VM} \cdot m_{displaced}$$

For a sphere in water:
$$m_{eff} = m_{bubble} + 0.5 \times \rho_{water} \times V_{bubble}$$

---

## Quick Reference

| Parameter | Value |
|-----------|-------|
| Sphere $C_{VM}$ | 0.5 |
| Gas-liquid | Include |
| Solid-gas | Skip |

---

## Concept Check

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

## Related Documents

- **Fundamental Concepts:** [01_Fundamental_Concepts.md](01_Fundamental_Concepts.md)
- **OpenFOAM Implementation:** [02_OpenFOAM_Implementation.md](02_OpenFOAM_Implementation.md)
- **Drag Overview:** [../01_DRAG/00_Overview.md](../01_DRAG/00_Overview.md)