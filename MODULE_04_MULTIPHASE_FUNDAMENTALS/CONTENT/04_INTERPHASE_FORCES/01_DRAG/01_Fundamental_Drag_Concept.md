# Fundamental Drag Concept

แนวคิดพื้นฐานของแรงต้าน (Drag Force)

---

## Overview

> **Drag Force** = แรงต้านการเคลื่อนที่สัมพัทธ์ระหว่างเฟส — แรงที่สำคัญที่สุดใน multiphase systems

```mermaid
flowchart LR
    A[Bubble/Particle] -->|Relative Velocity| B[Drag Force]
    B -->|Opposes Motion| C[Momentum Exchange]
```

---

## 1. Drag Force Equation

$$\mathbf{F}_D = \frac{1}{2} C_D \rho_c A |\mathbf{u}_r| \mathbf{u}_r$$

| Symbol | Meaning | Unit |
|--------|---------|------|
| $F_D$ | Drag force | N |
| $C_D$ | Drag coefficient | - |
| $\rho_c$ | Continuous phase density | kg/m³ |
| $A$ | Projected area | m² |
| $\mathbf{u}_r$ | Relative velocity | m/s |

### Per Unit Volume

$$\mathbf{F}_D = K (\mathbf{u}_c - \mathbf{u}_d)$$

where $K$ = momentum exchange coefficient [kg/(m³·s)]

---

## 2. Drag Coefficient

### Regimes

| Re Range | Regime | $C_D$ |
|----------|--------|-------|
| Re < 1 | Stokes | 24/Re |
| 1 < Re < 1000 | Transition | $\frac{24}{Re}(1+0.15Re^{0.687})$ |
| Re > 1000 | Newton | 0.44 |

### Reynolds Number

$$Re = \frac{\rho_c |\mathbf{u}_r| d}{\mu_c}$$

---

## 3. Physical Origin

### Viscous Drag (Low Re)

- เกิดจาก **shear stress** บนผิว
- Dominates ใน Stokes regime

### Pressure Drag (High Re)

- เกิดจาก **pressure difference** หน้า-หลัง
- Dominates ใน Newton regime

### Total Drag

$$C_D = C_{D,viscous} + C_{D,pressure}$$

---

## 4. Factors Affecting Drag

### Shape Effects

| Shape | $C_D$ (Re=100) |
|-------|----------------|
| Sphere | 1.0 |
| Ellipsoid | 0.5-1.5 |
| Disk | 1.2 |

### Concentration Effects

$$C_D^{eff} = C_D \cdot f(\alpha_d)$$

**Richardson-Zaki:**
$$f = (1-\alpha_d)^{-n}$$

where $n \approx 4.65$ for low Re

### Surface Contamination

- Surfactants **immobilize** bubble surface
- $C_D$ increases (behaves like rigid sphere)

---

## 5. Drag in OpenFOAM

### phaseProperties

```cpp
drag
{
    (air in water)
    {
        type    SchillerNaumann;
    }
}
```

### Momentum Exchange Coefficient

```cpp
K = (3/4) * Cd * alpha_c * alpha_d * rho_c * |Ur| / d
```

### Available Models

| Model | Best For |
|-------|----------|
| SchillerNaumann | Spherical, Re < 1000 |
| IshiiZuber | Deformed bubbles |
| Tomiyama | Contaminated |
| GidaspowErgunWenYu | Dense gas-solid |

---

## 6. Terminal Velocity

At steady state, drag = buoyancy:

$$u_t = \sqrt{\frac{4(\rho_c - \rho_d)gd}{3\rho_c C_D}}$$

### Stokes Regime

$$u_t = \frac{(\rho_c - \rho_d)gd^2}{18\mu_c}$$

---

## 7. Numerical Considerations

### Implicit Treatment

```cpp
// Implicit in momentum equation
fvm::Sp(K, U)  // Adds to diagonal → stable
```

### Residual Values

```cpp
drag
{
    (air in water)
    {
        type        SchillerNaumann;
        residualRe  1e-3;    // Prevent division by zero
    }
}
```

---

## Quick Reference

| Regime | $C_D$ | Key |
|--------|-------|-----|
| Stokes (Re < 1) | 24/Re | Viscous |
| Transition | Schiller-Naumann | Both |
| Newton (Re > 1000) | 0.44 | Pressure |

---

## Concept Check

<details>
<summary><b>1. ทำไม $C_D$ ลดลงเมื่อ Re เพิ่ม?</b></summary>

เพราะ **viscous drag** (proportional to 1/Re) dominates ที่ low Re แต่เมื่อ Re สูงขึ้น **pressure drag** (constant) จะ dominate
</details>

<details>
<summary><b>2. Implicit treatment ดีอย่างไร?</b></summary>

เพิ่ม **diagonal dominance** ของ matrix → **better convergence** โดยเฉพาะเมื่อ K สูง
</details>

<details>
<summary><b>3. ทำไม contaminated bubbles มี drag สูงกว่า?</b></summary>

Surfactants **immobilize surface** → ไม่มี internal circulation → behaves like **rigid sphere** ที่มี wake ใหญ่กว่า
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Specific Models:** [02_Specific_Drag_Models.md](02_Specific_Drag_Models.md)
- **OpenFOAM Implementation:** [03_OpenFOAM_Implementation.md](03_OpenFOAM_Implementation.md)