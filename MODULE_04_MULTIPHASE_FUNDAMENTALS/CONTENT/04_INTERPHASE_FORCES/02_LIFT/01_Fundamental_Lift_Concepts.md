# Fundamental Lift Concepts

แนวคิดพื้นฐานของแรงยก

---

## 1. Lift Force Definition

$$\mathbf{F}_L = -C_L \rho_c \alpha_d (\mathbf{u}_r \times \boldsymbol{\omega})$$

| Symbol | Meaning |
|--------|---------|
| $C_L$ | Lift coefficient |
| $\rho_c$ | Continuous phase density |
| $\mathbf{u}_r$ | Relative velocity |
| $\boldsymbol{\omega}$ | Vorticity ($\nabla \times U$) |

---

## 2. Physical Origin

### Shear-Induced Lift

- Bubble ใน shear flow ถูกผลักตั้งฉากกับ flow
- เกิดจาก **velocity gradient** รอบ bubble

### Direction

- **Perpendicular** to relative velocity
- Depends on vorticity direction

---

## 3. Coefficient Values

| Bubble Size | Eo | $C_L$ | Direction |
|-------------|-----|-------|-----------|
| Small | < 4 | + (0.5) | Toward wall |
| Large | > 10 | - (-0.29) | Toward center |

### Sign Change

At Eo ≈ 4, lift direction reverses due to deformation.

---

## 4. Key Parameters

### Eötvös Number

$$Eo = \frac{g \Delta\rho d^2}{\sigma}$$

### Shear Rate

$$Sr = \frac{d |\nabla U|}{|u_r|}$$

---

## 5. When to Include

| Condition | Include? |
|-----------|----------|
| Shear flow | **Yes** |
| Uniform flow | No |
| Pipe flow | **Yes** |
| Bubbly flow | **Yes** |

---

## 6. OpenFOAM

```cpp
lift
{
    (air in water)
    {
        type    Tomiyama;  // Or constantCoefficient
    }
}
```

---

## Quick Reference

| Parameter | Effect |
|-----------|--------|
| $C_L$ > 0 | Toward wall |
| $C_L$ < 0 | Toward center |
| Eo < 4 | Positive lift |
| Eo > 10 | Negative lift |

---

## Concept Check

<details>
<summary><b>1. ทำไม lift ตั้งฉากกับ velocity?</b></summary>

เพราะเกิดจาก **cross product** $\mathbf{u}_r \times \omega$ — perpendicular โดยนิยาม
</details>

<details>
<summary><b>2. ทำไม large bubbles มี negative lift?</b></summary>

Bubble ใหญ่ **deform** → wake asymmetry reverses → lift direction reverses
</details>

<details>
<summary><b>3. vorticity มาจากไหน?</b></summary>

จาก **curl ของ velocity field** → บอก local rotation ของ flow
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Specific Models:** [02_Specific_Lift_Models.md](02_Specific_Lift_Models.md)
- **Implementation:** [03_OpenFOAM_Implementation.md](03_OpenFOAM_Implementation.md)