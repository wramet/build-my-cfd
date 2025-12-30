# Specific Drag Models

โมเดล Drag เฉพาะสำหรับระบบหลายเฟส

---

## Learning Objectives

**What will you learn?**

- Identify the characteristics and suitable applications for each drag model
- Select the appropriate drag model based on dispersed phase type, flow regime, and dimensionless numbers
- Compare and contrast models for bubble systems, particle systems, and granular flows
- Understand when to use simple correlations versus complex multi-regime models

---

## Overview

```mermaid
flowchart TD
    A[Drag Models] --> B[Rigid Sphere]
    A --> C[Deformable]
    A --> D[Granular]
    B --> B1[SchillerNaumann]
    B --> B2[WenYu]
    C --> C1[IshiiZuber]
    C --> C2[Tomiyama]
    D --> D1[GidaspowErgunWenYu]
    D --> D2[SyamlalOBrien]
```

---

## 1. Schiller-Naumann

### Equation

$$C_D = \max\left(\frac{24}{Re}(1 + 0.15Re^{0.687}), 0.44\right)$$

### Use Case

- Spherical particles/bubbles
- $Re < 1000$
- Clean systems
- Low to moderate Reynolds numbers

---

## 2. Ishii-Zuber

### Equation

$$C_D = \begin{cases}
\frac{24}{Re}(1 + 0.1Re^{0.75}) & \text{Stokes regime} \\
\frac{2}{3}\sqrt{Eo} & \text{Distorted regime} \\
\frac{8}{3} & \text{Cap regime}
\end{cases}$$

### Use Case

- Deformable bubbles
- Gas-liquid with $Eo > 1$
- Clean bubble systems
- Wide range of bubble shapes

---

## 3. Tomiyama

### Equation

$$C_D = \max\left[\min\left(\frac{24}{Re}(1+0.15Re^{0.687}), \frac{72}{Re}\right), \frac{8Eo}{3(Eo+4)}\right]$$

### Use Case

- Contaminated bubbles (surfactants)
- General purpose for gas-liquid
- Systems with impurities
- Practical industrial applications

### Comparison

| System | Model |
|--------|-------|
| Clean bubbles | Ishii-Zuber |
| Contaminated | Tomiyama |

---

## 4. Grace

### Equation

$$C_D = \frac{4}{3}\frac{gd(\rho_l-\rho_g)}{\rho_l u_t^2}$$

where $u_t$ from Grace correlation

### Use Case

- High viscosity ratio
- Large bubbles
- Pure liquid systems
- Wide range of Morton numbers

---

## 5. Wen-Yu

### Equation

$$C_D = \frac{24}{\alpha_c Re}(1 + 0.15(\alpha_c Re)^{0.687}) \cdot \alpha_c^{-1.65}$$

### Use Case

- Fluidized beds (dilute: $\alpha_d < 0.2$)
- Gas-solid systems
- Low particle volume fractions
- Dilute phase transport

---

## 6. Gidaspow (Ergun + Wen-Yu)

### Equation

$$\beta = \begin{cases}
\frac{150\alpha_d^2\mu_c}{\alpha_c d_p^2} + \frac{1.75\alpha_d\rho_c|u_r|}{d_p} & \alpha_c < 0.8 \\
\frac{3}{4}C_D\frac{\alpha_c\alpha_d\rho_c|u_r|}{d_p}\alpha_c^{-2.65} & \alpha_c \geq 0.8
\end{cases}$$

### Use Case

- Dense fluidized beds
- Gas-solid with variable $\alpha$
- Circulating fluidized beds
- Systems transitioning between dense and dilute regimes

---

## 7. Syamlal-O'Brien

### Equation

$$C_D = \frac{0.63 + 4.8/\sqrt{Re/v_r}}^2$$

where $v_r$ is terminal velocity ratio

### Use Case

- Fluidized beds
- Empirically tuned for specific systems
- When experimental data available for calibration
- Gas-solid flow with known terminal velocities

---

## 8. Model Selection Flowchart

```mermaid
flowchart TD
    A[Start] --> B{Dispersed phase?}
    B -->|Bubble| C{Eo?}
    B -->|Particle| D{α_d?}
    C -->|< 1| E[SchillerNaumann]
    C -->|> 1| F{Clean?}
    F -->|Yes| G[IshiiZuber]
    F -->|No| H[Tomiyama]
    D -->|< 0.2| I[WenYu]
    D -->|> 0.2| J[GidaspowErgunWenYu]
    D -->|Calibrated| K[SyamlalOBrien]
```

---

## Model Comparison Summary

| Model | Phase Type | Volume Fraction | Key Parameter | Complexity | Best Application |
|-------|-----------|-----------------|---------------|------------|------------------|
| SchillerNaumann | Gas-liquid, Solid-liquid | Dilute | Re | Low | Spherical bubbles/particles |
| IshiiZuber | Gas-liquid | Dilute | Eo | Medium | Clean deformed bubbles |
| Tomiyama | Gas-liquid | Dilute | Re, Eo | Medium | Contaminated bubbles |
| Grace | Gas-liquid | Dilute | Eo, Mo | High | Large bubbles, high viscosity |
| WenYu | Gas-solid | Dilute (α_d < 0.2) | α_c | Low | Dilute fluidized beds |
| GidaspowErgunWenYu | Gas-solid | All | α_c | High | Dense fluidized beds |
| SyamlalOBrien | Gas-solid | All | v_r | Medium | Calibrated systems |

---

## Key Takeaways

- **Bubble systems**: Use Schiller-Naumann for spherical bubbles (Eo < 1), Ishii-Zuber for clean deformed bubbles, Tomiyama for contaminated systems
- **Gas-solid dilute**: Wen-Yu is appropriate for particle volume fractions below 0.2
- **Gas-solid dense**: Gidaspow blends Ergun (dense) and Wen-Yu (dilute) with a switching function at α_c = 0.8
- **Calibrated models**: Syamlal-O'Brien requires experimental data but can provide better accuracy for specific systems
- **Dimensionless numbers**: Eötvös number (Eo) indicates bubble deformation, Reynolds number (Re) indicates flow regime, volume fraction (α) determines particle-particle interactions

---

## Quick Reference

| Model | Best For | Key Parameter |
|-------|----------|---------------|
| SchillerNaumann | Spherical, Re < 1000 | Re |
| IshiiZuber | Deformed bubbles | Eo |
| Tomiyama | Contaminated systems | Re, Eo |
| Grace | High μ ratio | Terminal velocity |
| WenYu | Dilute gas-solid | α |
| Gidaspow | Dense gas-solid | α (switching) |
| SyamlalOBrien | Calibrated systems | v_r |

---

## Concept Check

<details>
<summary><b>1. SchillerNaumann กับ Tomiyama ต่างกันอย่างไร?</b></summary>

- **SchillerNaumann**: Rigid spheres, ไม่รวม deformation
- **Tomiyama**: รวม Eo effects และ surface contamination
</details>

<details>
<summary><b>2. ทำไม Gidaspow มี switching function?</b></summary>

เพราะ **Ergun** ใช้สำหรับ packed beds (dense) แต่ **Wen-Yu** ใช้สำหรับ dilute → Gidaspow switches ระหว่าง regimes
</details>

<details>
<summary><b>3. residualRe คืออะไร?</b></summary>

ค่า minimum Re เพื่อป้องกัน division by zero เมื่อ velocity ใกล้ศูนย์
</details>

<details>
<summary><b>4. เมื่อไรควรใช้ Grace correlation?</b></summary>

เมื่อระบบมี viscosity ratio สูง หรือ bubble ขนาดใหญ่ในของเหลวที่มีความหนืดสูง ซึ่ง Schiller-Naumann หรือ Ishii-Zuber อาจไม่แม่นยำพอ
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Fundamental Concepts:** [01_Fundamental_Drag_Concept.md](01_Fundamental_Drag_Concept.md)
- **OpenFOAM Implementation:** [03_OpenFOAM_Implementation.md](03_OpenFOAM_Implementation.md)