# Turbulent Dispersion - Fundamental Theory

ทฤษฎีพื้นฐานของ Turbulent Dispersion

---

## Overview

> Turbulent dispersion = การกระจายของ particles/bubbles เนื่องจาก turbulent fluctuations

---

## 1. Physical Mechanism

### Turbulent Eddies

- Eddies สุ่มเคลื่อนย้าย particles
- ผลลัพธ์: α distribution spreads
- คล้าย diffusion process

### Analogy

เหมือนควันกระจายในอากาศปั่นป่วน — eddies พาควันไปทิศทางสุ่ม

---

## 2. Mathematical Formulation

### Force Equation

$$\mathbf{F}_{TD} = -D_{TD} \nabla \alpha_d$$

where dispersion coefficient:

$$D_{TD} = C_{TD} \rho_c k_c$$

หรือ

$$D_{TD} = C_{TD} \rho_c \nu_t$$

---

## 3. Relation to Turbulence

### Turbulent Diffusivity

$$D_t = \frac{\nu_t}{Sc_t}$$

| Variable | Meaning |
|----------|---------|
| $\nu_t$ | Turbulent viscosity |
| $Sc_t$ | Turbulent Schmidt number (~0.9) |

### Connection to k

$$\nu_t = C_\mu \frac{k^2}{\varepsilon}$$

---

## 4. Effect on α Distribution

### Without TD

- Sharp α gradients maintained
- Particles may concentrate

### With TD

- α profile flattens
- More realistic mixing

---

## 5. Stokes Number Effect

$$St = \frac{\tau_p}{\tau_f}$$

| St | Behavior |
|----|----------|
| << 1 | Follows turbulence |
| >> 1 | Unaffected by turbulence |

---

## 6. Key Parameters

| Parameter | Effect |
|-----------|--------|
| $C_{TD}$ ↑ | More dispersion |
| $k$ ↑ | More dispersion |
| $\nabla\alpha$ ↑ | Stronger force |

---

## Quick Reference

| Quantity | Formula |
|----------|---------|
| Force | $-D_{TD} \nabla\alpha$ |
| Direction | Opposite to α gradient |
| Effect | Flattens α profile |

---

## Concept Check

<details>
<summary><b>1. TD force direction คืออะไร?</b></summary>

**Opposite to α gradient** — from high concentration to low (like diffusion)
</details>

<details>
<summary><b>2. Stokes number บอกอะไร?</b></summary>

บอกว่า particle จะ **follow turbulent eddies** หรือไม่ — St << 1 = follows, St >> 1 = unaffected
</details>

<details>
<summary><b>3. ทำไม TD ทำให้ α profile แบนลง?</b></summary>

เพราะ TD force **ผลักจาก high α ไป low α** — เหมือน diffusion ทำให้ concentration เฉลี่ยออก
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Specific Models:** [02_Specific_Models.md](02_Specific_Models.md)
- **Drag Overview:** [../01_DRAG/00_Overview.md](../01_DRAG/00_Overview.md)