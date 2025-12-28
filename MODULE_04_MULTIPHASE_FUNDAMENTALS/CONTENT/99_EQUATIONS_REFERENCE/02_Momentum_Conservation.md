# Momentum Conservation Equations

สมการอนุรักษ์โมเมนตัมสำหรับ Multiphase

---

## Overview

> แต่ละเฟส $k$ มีสมการโมเมนตัมของตัวเอง เชื่อมโยงผ่าน **shared pressure** และ **interphase forces**

---

## 1. General Form

$$\frac{\partial(\alpha_k \rho_k \mathbf{u}_k)}{\partial t} + \nabla \cdot (\alpha_k \rho_k \mathbf{u}_k \mathbf{u}_k) = -\alpha_k \nabla p + \nabla \cdot (\alpha_k \boldsymbol{\tau}_k) + \alpha_k \rho_k \mathbf{g} + \mathbf{M}_k$$

| Term | Meaning |
|------|---------|
| $\frac{\partial(\alpha_k \rho_k \mathbf{u}_k)}{\partial t}$ | Unsteady |
| $\nabla \cdot (\alpha_k \rho_k \mathbf{u}_k \mathbf{u}_k)$ | Convection |
| $-\alpha_k \nabla p$ | Pressure gradient |
| $\nabla \cdot (\alpha_k \boldsymbol{\tau}_k)$ | Viscous stress |
| $\alpha_k \rho_k \mathbf{g}$ | Gravity |
| $\mathbf{M}_k$ | Interphase forces |

---

## 2. Stress Tensor

### Newtonian Fluid

$$\boldsymbol{\tau}_k = \mu_k \left(\nabla \mathbf{u}_k + (\nabla \mathbf{u}_k)^T\right) - \frac{2}{3}\mu_k (\nabla \cdot \mathbf{u}_k)\mathbf{I}$$

### Effective Viscosity

$$\mu_{eff} = \mu_{lam} + \mu_t$$

---

## 3. Interphase Momentum Transfer

$$\mathbf{M}_k = \sum_{l \neq k} (\mathbf{F}^D_{kl} + \mathbf{F}^L_{kl} + \mathbf{F}^{VM}_{kl} + \mathbf{F}^{TD}_{kl})$$

### Drag Force

$$\mathbf{F}^D_{kl} = K_{kl}(\mathbf{u}_l - \mathbf{u}_k)$$

### Lift Force

$$\mathbf{F}^L_{kl} = -C_L \rho_c \alpha_d (\mathbf{u}_r \times \boldsymbol{\omega}_c)$$

### Virtual Mass

$$\mathbf{F}^{VM}_{kl} = C_{VM} \rho_c \alpha_d \left(\frac{D\mathbf{u}_c}{Dt} - \frac{D\mathbf{u}_d}{Dt}\right)$$

### Turbulent Dispersion

$$\mathbf{F}^{TD}_{kl} = -C_{TD} \rho_c k_c \nabla \alpha_d$$

---

## 4. OpenFOAM Implementation

### Momentum Equation

```cpp
fvVectorMatrix UEqn
(
    fvm::ddt(alpha, rho, U)           // ∂(αρU)/∂t
  + fvm::div(alphaPhi, U)             // ∇·(αρUU)
  ==
    fvm::laplacian(alpha*nuEff, U)    // ∇·(ατ)
  + alpha*rho*g                       // αρg
  + interfacialForces                 // M_k
);
```

### Pressure Gradient

```cpp
// Added in pEqn.H
fvc::reconstruct
(
    (fvc::interpolate(rho*g) & mesh.Sf())
  - phiHbyA
  + fvc::snGrad(p)*mesh.magSf()
)
```

---

## 5. Dimensionless Form

$$\frac{\partial(\alpha_k \tilde{\mathbf{u}}_k)}{\partial \tilde{t}} + \nabla \cdot (\alpha_k \tilde{\mathbf{u}}_k \tilde{\mathbf{u}}_k) = -\alpha_k \nabla \tilde{p} + \frac{1}{Re}\nabla^2(\alpha_k \tilde{\mathbf{u}}_k) + \frac{1}{Fr^2}\alpha_k \hat{\mathbf{g}}$$

| Number | Formula |
|--------|---------|
| Reynolds | $Re = \frac{\rho U L}{\mu}$ |
| Froude | $Fr = \frac{U}{\sqrt{gL}}$ |

---

## 6. Boundary Conditions

### Inlet

```cpp
U.water
{
    type    fixedValue;
    value   uniform (0 0 1);
}
```

### Wall

```cpp
U.water
{
    type    noSlip;
}
```

### Outlet

```cpp
U.water
{
    type    zeroGradient;
}
```

---

## Quick Reference

| Component | Equation / Model |
|-----------|------------------|
| Convection | $\nabla \cdot (\alpha \rho UU)$ |
| Pressure | Shared $p$ field |
| Viscous | $\nabla \cdot (\alpha \tau)$ |
| Drag | $K(\mathbf{u}_c - \mathbf{u}_d)$ |
| Lift | $C_L(\mathbf{u}_r \times \omega)$ |

---

## Concept Check

<details>
<summary><b>1. ทำไมใช้ shared pressure?</b></summary>

เพราะ Euler-Euler ถือว่าเฟสอยู่ **co-located** ในปริมาตรเดียวกัน → ความดันต้องเท่ากันที่ทุกจุด
</details>

<details>
<summary><b>2. Interphase forces รวมอยู่ใน M_k อะไรบ้าง?</b></summary>

- **Drag**: ต้านการเคลื่อนที่สัมพัทธ์
- **Lift**: ตั้งฉากกับ velocity gradient
- **Virtual Mass**: เนื่องจาก displaced fluid inertia
- **Turbulent Dispersion**: กระจายเนื่องจาก turbulence
</details>

<details>
<summary><b>3. fvm vs fvc ต่างกันอย่างไร?</b></summary>

- **fvm**: Implicit (adds to matrix)
- **fvc**: Explicit (adds to RHS)
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Mass Conservation:** [01_Mass_Conservation.md](01_Mass_Conservation.md)
- **Energy Conservation:** [03_Energy_Conservation.md](03_Energy_Conservation.md)