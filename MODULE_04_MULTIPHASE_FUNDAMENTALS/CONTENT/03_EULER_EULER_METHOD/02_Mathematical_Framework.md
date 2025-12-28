# Euler-Euler Mathematical Framework

กรอบทางคณิตศาสตร์ของ Euler-Euler Method

---

## 1. Volume Averaging

$$\langle \phi \rangle_k = \frac{1}{V_k} \int_{V_k} \phi \, dV$$

$$\alpha_k = \frac{V_k}{V}, \quad \sum_k \alpha_k = 1$$

---

## 2. Conservation Equations

### Mass

$$\frac{\partial(\alpha_k \rho_k)}{\partial t} + \nabla \cdot (\alpha_k \rho_k \mathbf{u}_k) = \dot{m}_k$$

### Momentum

$$\frac{\partial(\alpha_k \rho_k \mathbf{u}_k)}{\partial t} + \nabla \cdot (\alpha_k \rho_k \mathbf{u}_k \mathbf{u}_k) = -\alpha_k \nabla p + \nabla \cdot \boldsymbol{\tau}_k + \alpha_k \rho_k \mathbf{g} + \mathbf{M}_k$$

### Energy

$$\frac{\partial(\alpha_k \rho_k h_k)}{\partial t} + \nabla \cdot (\alpha_k \rho_k h_k \mathbf{u}_k) = \nabla \cdot (k_k \nabla T_k) + Q_k$$

---

## 3. Stress Tensor

$$\boldsymbol{\tau}_k = \mu_k \left(\nabla \mathbf{u}_k + (\nabla \mathbf{u}_k)^T - \frac{2}{3}(\nabla \cdot \mathbf{u}_k)\mathbf{I}\right)$$

### Effective Viscosity

$$\mu_{eff} = \mu_{lam} + \mu_t$$

---

## 4. Interphase Forces

$$\mathbf{M}_k = \sum_{l \neq k} (\mathbf{F}^D + \mathbf{F}^L + \mathbf{F}^{VM} + \mathbf{F}^{TD})$$

| Force | Formula |
|-------|---------|
| Drag | $K(\mathbf{u}_l - \mathbf{u}_k)$ |
| Lift | $-C_L \rho_c \alpha_d (\mathbf{u}_r \times \omega)$ |
| VM | $C_{VM} \rho_c \alpha_d \frac{D\mathbf{u}_r}{Dt}$ |
| TD | $-C_{TD} \rho_c k \nabla \alpha_d$ |

---

## 5. Pressure Equation

From mixture continuity:

$$\sum_k \nabla \cdot (\alpha_k \rho_k \mathbf{u}_k) = 0$$

Leads to Poisson equation:

$$\nabla \cdot \left(\sum_k \frac{\alpha_k}{\rho_k} \nabla p\right) = \text{source}$$

---

## 6. Turbulence

### Per-Phase k-ε

$$\frac{\partial(\alpha_k k_k)}{\partial t} + \nabla \cdot (\alpha_k \mathbf{u}_k k_k) = P_k - \varepsilon_k + \Pi_k$$

where $\Pi_k$ = interphase turbulent transfer

---

## Quick Reference

| Equation | Key Terms |
|----------|-----------|
| Mass | α, ρ, U |
| Momentum | + τ, g, M |
| Energy | + k∇T, Q |
| Pressure | From continuity |

---

## Concept Check

<details>
<summary><b>1. ทำไมต้อง volume average?</b></summary>

เพราะ Euler-Euler ไม่ track interface → ใช้ **averaged properties** แทน
</details>

<details>
<summary><b>2. Pressure equation มาจากไหน?</b></summary>

จาก **mixture continuity** — บังคับให้ velocity fields รวมกันเป็น divergence-free
</details>

<details>
<summary><b>3. $\Pi_k$ คืออะไร?</b></summary>

**Interphase turbulent transfer** — sources/sinks จาก wakes, bubble-induced turbulence
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Introduction:** [01_Introduction.md](01_Introduction.md)
- **Implementation:** [03_Implementation_Concepts.md](03_Implementation_Concepts.md)