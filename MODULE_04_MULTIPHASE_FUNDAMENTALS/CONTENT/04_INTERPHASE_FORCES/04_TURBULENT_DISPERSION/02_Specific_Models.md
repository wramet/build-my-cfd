# Turbulent Dispersion - Specific Models

โมเดล Turbulent Dispersion เฉพาะ

---

## Overview

> **Turbulent Dispersion** = การกระจายตัวของเฟสกระจาย (bubbles/particles) เนื่องจาก turbulent fluctuations

```mermaid
flowchart LR
    A[Turbulent Eddies] --> B[Random Particle Motion]
    B --> C[Spreading of α]
```

---

## 1. Fundamental Equation

$$\mathbf{F}_{TD} = -C_{TD} \rho_c k_c \nabla \alpha_d$$

หรือ

$$\mathbf{F}_{TD} = -C_{TD} \nu_{t,c} \nabla \alpha_d$$

| Symbol | Meaning | Unit |
|--------|---------|------|
| $C_{TD}$ | Dispersion coefficient | - |
| $k_c$ | Turbulent kinetic energy | m²/s² |
| $\nu_{t,c}$ | Turbulent viscosity | m²/s |
| $\nabla \alpha_d$ | Phase fraction gradient | 1/m |

---

## 2. Burns Model

### Equation

$$\mathbf{F}_{TD} = C_{TD} K_{drag} \frac{\nu_{t,c}}{\sigma_{TD}} \left(\frac{\nabla \alpha_d}{\alpha_d} - \frac{\nabla \alpha_c}{\alpha_c}\right)$$

### Default Parameters

| Parameter | Value |
|-----------|-------|
| $C_{TD}$ | 1.0 |
| $\sigma_{TD}$ | 0.9 |

### OpenFOAM

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

---

## 3. Gosman Model

### Equation

$$\mathbf{F}_{TD} = -C_{TD} \rho_c \nu_{t,c} \nabla \alpha_d$$

### OpenFOAM

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

---

## 4. Lopez de Bertodano

### Equation

$$\mathbf{F}_{TD} = -C_{TD} \rho_c k_c \nabla \alpha_d$$

- ใช้ $k_c$ โดยตรงแทน $\nu_{t,c}$

### OpenFOAM

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

## 5. Model Comparison

| Model | Form | Best For |
|-------|------|----------|
| Burns | $K_{drag} \cdot \nu_t$ | General, coupled with drag |
| Gosman | $\rho \nu_t \nabla\alpha$ | Simple cases |
| Lopez de Bertodano | $\rho k \nabla\alpha$ | High turbulence |

### Coefficient Guidelines

| Model | Typical $C_{TD}$ |
|-------|------------------|
| Burns | 0.5-1.5 |
| Gosman | 0.5-1.0 |
| Lopez de Bertodano | 0.05-0.5 |

---

## 6. When to Use

### Include TD When:

| Condition | TD Important? |
|-----------|---------------|
| High turbulence (Re_t > 100) | Yes |
| Large α gradients | Yes |
| Bubble column core | Yes |
| Near walls | Less important |

### Skip TD When:

- Laminar flow
- Uniform α distribution
- Very small particles (St >> 1)

---

## 7. Numerical Considerations

### Stability

```cpp
// May need lower relaxation
relaxationFactors
{
    equations { "U.*" 0.6; }
}
```

### Interaction with Lift

- TD และ lift อาจ **counteract** กัน
- ตรวจสอบ radial distribution

---

## 8. Verification

### Expected Behavior

- TD ทำให้ **α profile แบนลง**
- Center-line α ลดลง, wall-region α เพิ่มขึ้น

### Monitor

```cpp
functions
{
    radialAlpha
    {
        type    sets;
        fields  (alpha.air);
        sets    ( radialLine { type lineCell; ... } );
    }
}
```

---

## Quick Reference

| Question | Answer |
|----------|--------|
| Default model? | Burns |
| Default $C_{TD}$? | 1.0 |
| When needed? | High turbulence, α gradients |
| Effect? | Flattens α profile |

---

## Concept Check

<details>
<summary><b>1. TD force กระทำทิศไหน?</b></summary>

ทิศทาง **opposite กับ α gradient** — ผลักจากบริเวณที่มี α สูงไปบริเวณที่ α ต่ำ (like diffusion)
</details>

<details>
<summary><b>2. Burns model ต่างจากอื่นอย่างไร?</b></summary>

Burns **couples กับ drag coefficient** ($K_{drag}$) ทำให้ consistent กับ momentum exchange ระหว่างเฟส
</details>

<details>
<summary><b>3. ทำไม $C_{TD}$ ต้อง tune?</b></summary>

เพราะ **turbulent dispersion เป็น empirical closure** — ค่าที่ดีขึ้นกับ flow conditions และ particle size
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Fundamental Concepts:** [01_Fundamental_Concepts.md](01_Fundamental_Concepts.md)
- **Drag Overview:** [../01_DRAG/00_Overview.md](../01_DRAG/00_Overview.md)