# Turbulent Dispersion Overview

ภาพรวมแรงกระจายตัวแบบปั่นป่วน

---

## Overview

> **Turbulent Dispersion** = การกระจายตัวของ bubbles/particles เนื่องจาก turbulent eddies

```mermaid
flowchart LR
    A[Turbulent Eddies] --> B[Randomly Move Particles]
    B --> C[α Distribution Spreads]
```

---

## 1. Physical Mechanism

- Turbulent fluctuations ($u'$) สุ่มเคลื่อนย้าย particles
- ผลลัพธ์: **spreading** ของ phase fraction distribution
- คล้าย diffusion แต่เกิดจาก turbulence

### Analogy

เหมือนการกระจายของควันในอากาศที่ปั่นป่วน — eddies พาควันไปทิศทางสุ่ม

---

## 2. Basic Equation

$$\mathbf{F}_{TD} = -C_{TD} \rho_c k_c \nabla \alpha_d$$

หรือ

$$\mathbf{F}_{TD} = -C_{TD} \rho_c \nu_{t,c} \nabla \alpha_d$$

| Symbol | Meaning |
|--------|---------|
| $C_{TD}$ | Dispersion coefficient |
| $k_c$ | Turbulent kinetic energy |
| $\nu_{t,c}$ | Turbulent viscosity |
| $\nabla \alpha_d$ | Phase fraction gradient |

---

## 3. Direction of Force

- **Opposite** to $\nabla \alpha$
- From high α to low α
- Acts like **diffusion**

```
High α region → Force → Low α region
```

---

## 4. Available Models

### Burns

$$\mathbf{F}_{TD} = C_{TD} K_{drag} \frac{\nu_t}{\sigma_{TD}} \nabla \alpha$$

```cpp
turbulentDispersion
{
    (air in water)
    {
        type    Burns;
        Ctd     1.0;
        sigma   0.9;
    }
}
```

### Gosman

$$\mathbf{F}_{TD} = -C_{TD} \rho_c \nu_t \nabla \alpha_d$$

```cpp
turbulentDispersion
{
    (air in water)
    {
        type    Gosman;
        Ctd     1.0;
    }
}
```

### Lopez de Bertodano

$$\mathbf{F}_{TD} = -C_{TD} \rho_c k_c \nabla \alpha_d$$

```cpp
turbulentDispersion
{
    (air in water)
    {
        type    LopezDeBertodano;
        Ctd     0.1;
    }
}
```

---

## 5. When to Use

| Condition | Include TD? |
|-----------|-------------|
| High turbulence | **Yes** |
| Large α gradients | **Yes** |
| Bubble column | **Yes** |
| Laminar flow | No |
| Uniform distribution | No effect |

---

## 6. Coefficient Selection

| Model | Typical $C_{TD}$ |
|-------|------------------|
| Burns | 0.5-1.5 |
| Gosman | 0.5-1.0 |
| Lopez de Bertodano | 0.05-0.5 |

### Tuning

- Start with default
- Compare radial α profile to experiments
- Adjust if profile too peaked/flat

---

## 7. Effect on Results

### Without TD

- Sharp α gradients maintained
- Particles may concentrate

### With TD

- α profile **flattens**
- More realistic mixing

---

## Quick Reference

| Model | Form | Default $C_{TD}$ |
|-------|------|------------------|
| Burns | $K_{drag} \nu_t$ | 1.0 |
| Gosman | $\rho \nu_t$ | 1.0 |
| Lopez de Bertodano | $\rho k$ | 0.1 |

---

## Concept Check

<details>
<summary><b>1. TD force direction คืออะไร?</b></summary>

**Opposite to α gradient** — ผลักจาก high concentration ไป low concentration (like diffusion)
</details>

<details>
<summary><b>2. Burns model ดีกว่าอื่นอย่างไร?</b></summary>

**Couples กับ drag** ผ่าน $K_{drag}$ → consistent กับ momentum exchange mechanism
</details>

<details>
<summary><b>3. เมื่อไหร่ TD ไม่จำเป็น?</b></summary>

เมื่อ flow เป็น **laminar** หรือ α distribution **uniform** อยู่แล้ว
</details>

---

## Related Documents

- **Specific Models:** [02_Specific_Models.md](02_Specific_Models.md)
- **Fundamental Theory:** [01_Fundamental_Theory.md](01_Fundamental_Theory.md)
- **Drag Overview:** [../01_DRAG/00_Overview.md](../01_DRAG/00_Overview.md)