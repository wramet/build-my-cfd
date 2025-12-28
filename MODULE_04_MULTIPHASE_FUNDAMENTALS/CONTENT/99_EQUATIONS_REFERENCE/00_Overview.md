# Equations Reference Overview

ภาพรวมสมการอ้างอิงสำหรับ Multiphase Flow

---

## 1. Conservation Laws

### Mass (Continuity)

$$\frac{\partial(\alpha_k \rho_k)}{\partial t} + \nabla \cdot (\alpha_k \rho_k \mathbf{u}_k) = \sum_{l \neq k} \dot{m}_{lk}$$

### Momentum

$$\frac{\partial(\alpha_k \rho_k \mathbf{u}_k)}{\partial t} + \nabla \cdot (\alpha_k \rho_k \mathbf{u}_k \mathbf{u}_k) = -\alpha_k \nabla p + \nabla \cdot \boldsymbol{\tau}_k + \alpha_k \rho_k \mathbf{g} + \mathbf{M}_k$$

### Energy

$$\frac{\partial(\alpha_k \rho_k h_k)}{\partial t} + \nabla \cdot (\alpha_k \rho_k h_k \mathbf{u}_k) = \nabla \cdot (k_k \nabla T_k) + Q_k$$

### Constraint

$$\sum_k \alpha_k = 1$$

---

## 2. Interphase Forces

| Force | Equation |
|-------|----------|
| **Drag** | $\mathbf{F}_D = K(\mathbf{u}_c - \mathbf{u}_d)$ |
| **Lift** | $\mathbf{F}_L = -C_L \rho_c \alpha_d (\mathbf{u}_r \times \boldsymbol{\omega})$ |
| **Virtual Mass** | $\mathbf{F}_{VM} = C_{VM} \rho_c \alpha_d \frac{D\mathbf{u}_r}{Dt}$ |
| **Turbulent Dispersion** | $\mathbf{F}_{TD} = -C_{TD} \rho_c k_c \nabla \alpha_d$ |

---

## 3. Drag Correlations

### Schiller-Naumann

$$C_D = \max\left(\frac{24}{Re}(1 + 0.15Re^{0.687}), 0.44\right)$$

### Ishii-Zuber (Distorted)

$$C_D = \frac{2}{3}\sqrt{Eo}$$

### Tomiyama

$$C_D = \max\left[\min\left(\frac{24}{Re}(1+0.15Re^{0.687}), \frac{72}{Re}\right), \frac{8Eo}{3(Eo+4)}\right]$$

---

## 4. Dimensionless Numbers

| Number | Formula | Meaning |
|--------|---------|---------|
| Reynolds | $Re = \frac{\rho U d}{\mu}$ | Inertia/viscosity |
| Eötvös | $Eo = \frac{g\Delta\rho d^2}{\sigma}$ | Buoyancy/surface tension |
| Morton | $Mo = \frac{g\mu^4\Delta\rho}{\rho^2\sigma^3}$ | Fluid properties |
| Weber | $We = \frac{\rho U^2 d}{\sigma}$ | Inertia/surface tension |
| Froude | $Fr = \frac{U}{\sqrt{gL}}$ | Inertia/gravity |
| Stokes | $St = \frac{\rho_d d^2 U}{18\mu_c L}$ | Particle response |

---

## 5. Surface Tension

### Young-Laplace

$$\Delta p = \sigma \kappa = \sigma \left(\frac{1}{R_1} + \frac{1}{R_2}\right)$$

### CSF Force

$$\mathbf{F}_\sigma = \sigma \kappa \nabla \alpha$$

---

## 6. Heat Transfer

### Interphase

$$Q_k = h_{kl} A_{kl} (T_l - T_k)$$

### Ranz-Marshall

$$Nu = 2 + 0.6 Re^{1/2} Pr^{1/3}$$

---

## 7. Terminal Velocity

### Stokes

$$u_t = \frac{(\rho_c - \rho_d) g d^2}{18 \mu_c}$$

### General

$$u_t = \sqrt{\frac{4(\rho_c - \rho_d)gd}{3\rho_c C_D}}$$

---

## 8. Turbulence (k-ε)

$$\frac{\partial k}{\partial t} + \nabla \cdot (\mathbf{u} k) = \nabla \cdot \left(\frac{\nu_t}{\sigma_k} \nabla k\right) + P_k - \varepsilon$$

$$\frac{\partial \varepsilon}{\partial t} + \nabla \cdot (\mathbf{u} \varepsilon) = \nabla \cdot \left(\frac{\nu_t}{\sigma_\varepsilon} \nabla \varepsilon\right) + C_{1\varepsilon}\frac{\varepsilon}{k}P_k - C_{2\varepsilon}\frac{\varepsilon^2}{k}$$

$$\nu_t = C_\mu \frac{k^2}{\varepsilon}$$

---

## Quick Reference

| Equation | Key Variables |
|----------|---------------|
| Continuity | α, ρ, U |
| Momentum | α, ρ, U, p, τ, M |
| Energy | α, ρ, h, T, Q |
| Drag | K, C_D, Re |
| Surface tension | σ, κ |

---

## 🧠 Concept Check

<details>
<summary><b>1. สมการ Continuity สำหรับ Multiphase มีอะไรเพิ่มจาก Single-phase?</b></summary>

**เพิ่ม Volume Fraction ($\alpha_k$) และ Mass Transfer:**

$$\frac{\partial(\alpha_k \rho_k)}{\partial t} + \nabla \cdot (\alpha_k \rho_k \mathbf{u}_k) = \sum_{l \neq k} \dot{m}_{lk}$$

- **$\alpha_k$:** สัดส่วนปริมาตรของเฟส k
- **$\dot{m}_{lk}$:** อัตราการถ่ายเทมวลระหว่างเฟส

</details>

<details>
<summary><b>2. Drag Correlation ไหนเหมาะกับประเภทฟองใด?</b></summary>

| Correlation | เหมาะกับ | ช่วง Eo/Re |
|-------------|----------|------------|
| **Schiller-Naumann** | Spherical | Re < 1000 |
| **Ishii-Zuber** | Distorted | Eo > 4 |
| **Tomiyama** | ทั่วไป | Wide range |

</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **Mass Conservation:** [01_Mass_Conservation.md](01_Mass_Conservation.md)
- **Momentum Conservation:** [02_Momentum_Conservation.md](02_Momentum_Conservation.md)
- **Energy Conservation:** [03_Energy_Conservation.md](03_Energy_Conservation.md)
- **Interfacial Equations:** [04_Interfacial_Phenomena_Equations.md](04_Interfacial_Phenomena_Equations.md)