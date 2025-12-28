# Turbulence Fundamentals

พื้นฐานทางฟิสิกส์และคณิตศาสตร์ของความปั่นป่วน

---

## Overview

| Regime | Condition | Model |
|--------|-----------|-------|
| Laminar | $Re < 2300$ (pipe) | `laminar` |
| Transitional | $2300 < Re < 4000$ | Transition models |
| Turbulent | $Re > 4000$ | RANS, LES, DNS |

---

## 1. Turbulence Characteristics

| Property | Description |
|----------|-------------|
| **Irregular** | Random, chaotic motion |
| **Diffusive** | Enhanced mixing of mass, momentum, heat |
| **Dissipative** | Energy cascades from large to small scales |
| **3D** | Always three-dimensional |
| **Multi-scale** | Integral scale → Kolmogorov scale |

```mermaid
flowchart LR
    A[Large Eddies] --> B[Energy Cascade]
    B --> C[Small Eddies]
    C --> D[Dissipation → Heat]
```

---

## 2. Reynolds Decomposition

$$\phi = \bar{\phi} + \phi'$$

| Term | Meaning |
|------|---------|
| $\bar{\phi}$ | Time-averaged (mean) |
| $\phi'$ | Fluctuation ($\overline{\phi'} = 0$) |

**Applied to velocity:**
$$\mathbf{u} = \bar{\mathbf{u}} + \mathbf{u}'$$

---

## 3. RANS Equations

### Continuity (Averaged)
$$\nabla \cdot \bar{\mathbf{u}} = 0$$

### Momentum (Averaged)
$$\rho \frac{\partial \bar{\mathbf{u}}}{\partial t} + \rho (\bar{\mathbf{u}} \cdot \nabla) \bar{\mathbf{u}} = -\nabla \bar{p} + \mu \nabla^2 \bar{\mathbf{u}} + \nabla \cdot \boldsymbol{\tau}_R$$

### Reynolds Stress Tensor
$$\tau_{R,ij} = -\rho \overline{u'_i u'_j}$$

> **Closure Problem:** 6 unknowns ($\tau_{R,ij}$) แต่ไม่มีสมการเพิ่ม

---

## 4. Boussinesq Hypothesis

$$\boldsymbol{\tau}_R = 2\mu_t \bar{\mathbf{D}} - \frac{2}{3}\rho k \mathbf{I}$$

| Term | Definition |
|------|------------|
| $\mu_t$ | Eddy viscosity |
| $\bar{\mathbf{D}}$ | Mean strain rate tensor |
| $k$ | Turbulent kinetic energy |

### Effective Viscosity
$$\nu_{eff} = \nu + \nu_t$$

---

## 5. Key Turbulence Variables

### Turbulent Kinetic Energy (TKE)
$$k = \frac{1}{2}\overline{u'_i u'_i} = \frac{1}{2}(\overline{u'^2} + \overline{v'^2} + \overline{w'^2})$$

### Dissipation Rate
$$\varepsilon = \nu \overline{\frac{\partial u'_i}{\partial x_j}\frac{\partial u'_i}{\partial x_j}}$$

### Specific Dissipation Rate
$$\omega = \frac{\varepsilon}{\beta^* k}$$

---

## 6. k-ε Model

### Eddy Viscosity
$$\nu_t = C_\mu \frac{k^2}{\varepsilon}$$

### Transport Equations

**k-equation:**
$$\frac{\partial k}{\partial t} + \bar{u}_j \frac{\partial k}{\partial x_j} = P_k - \varepsilon + \nabla \cdot \left(\frac{\nu_t}{\sigma_k}\nabla k\right)$$

**ε-equation:**
$$\frac{\partial \varepsilon}{\partial t} + \bar{u}_j \frac{\partial \varepsilon}{\partial x_j} = C_1 \frac{\varepsilon}{k} P_k - C_2 \frac{\varepsilon^2}{k} + \nabla \cdot \left(\frac{\nu_t}{\sigma_\varepsilon}\nabla \varepsilon\right)$$

### Standard Constants

| Constant | Value |
|----------|-------|
| $C_\mu$ | 0.09 |
| $C_1$ | 1.44 |
| $C_2$ | 1.92 |
| $\sigma_k$ | 1.0 |
| $\sigma_\varepsilon$ | 1.3 |

---

## 7. OpenFOAM Implementation

### turbulenceProperties

```cpp
simulationType RAS;

RAS
{
    RASModel    kEpsilon;
    turbulence  on;
    printCoeffs on;
}
```

### Key Fields

| File | Variable |
|------|----------|
| `0/k` | Turbulent kinetic energy |
| `0/epsilon` | Dissipation rate |
| `0/omega` | Specific dissipation (k-ω) |
| `0/nut` | Eddy viscosity |

### Solver Code

```cpp
// UEqn.H - Momentum equation with turbulence
tmp<fvVectorMatrix> tUEqn
(
    fvm::ddt(rho, U)
  + fvm::div(phi, U)
  + turbulence->divDevRhoReff(U)  // Reynolds stress
 ==
    fvOptions(rho, U)
);
```

---

## Concept Check

<details>
<summary><b>1. ทำไม Reynolds Stress ถึงต้องการ closure model?</b></summary>

เพราะการทำ Reynolds averaging สร้างเทอมใหม่ $\overline{u'_i u'_j}$ (6 ตัวแปร) ที่ไม่มีสมการควบคุม — ต้องสร้างสมการเพิ่มหรือใช้สมมติฐานเช่น Boussinesq
</details>

<details>
<summary><b>2. $\nu_t$ กับ $\nu$ ต่างกันอย่างไร?</b></summary>

- **$\nu$**: คุณสมบัติของ **ของไหล** (molecular viscosity)
- **$\nu_t$**: คุณสมบัติของ **การไหล** (eddy viscosity) — ขึ้นกับ turbulence intensity ไม่ใช่ของไหล
</details>

<details>
<summary><b>3. Energy cascade คืออะไร?</b></summary>

กระบวนการถ่ายโอนพลังงานจาก **large eddies** ไปยัง **small eddies** จนถึง Kolmogorov scale ที่พลังงานถูกเปลี่ยนเป็นความร้อนโดย viscosity
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **บทถัดไป:** [02_RANS_Models.md](02_RANS_Models.md)
- **Wall Treatment:** [03_Wall_Treatment.md](03_Wall_Treatment.md)