# Fundamental Drag Concept

แนวคิดพื้นฐานของแรงต้าน (Drag Force)

---

## Learning Objectives

**What will you learn?**

- **Understand** the physical origins of drag force in multiphase systems
- **Derive** the drag coefficient relationship across different Reynolds number regimes
- **Analyze** how shape, concentration, and surface contamination affect drag behavior
- **Calculate** terminal velocity using drag-buoyancy balance
- **Apply** drag force equations to momentum exchange calculations

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

<!-- IMAGE: IMG_04_003 -->
<!-- 
Purpose: เพื่อแสดง Free Body Diagram ของฟองอากาศที่กำลังลอยขึ้นในของเหลว. ภาพนี้เป็นกุญแจสำคัญในการเข้าใจเทอม Momentum Source ใน Euler-Euler ($M_{source}$) โดยต้องโชว์แรงหลักทุกตัว: แรงขับเคลื่อน (Buoyancy - Gravity) และแรงต้านทาน (Drag - Mass - Lift)
Prompt: "Engineering Free Body Diagram (FBD) of a rising gas bubble. **Central Object:** A spherical bubble. **Forces:** 1. **Buoyancy ($\mathbf{F}_b$):** Upward, Green arrow (Driving force). 2. **Gravity ($\mathbf{F}_g$):** Downward, Black arrow. 3. **Drag ($\mathbf{F}_D$):** Downward, Red arrow (Opposing motion). 4. **Lift ($\mathbf{F}_L$):** Sideways, Blue arrow (Due to shear). **Velocities:** Vector $\mathbf{U}_{bubble}$ (Up) and $\mathbf{U}_{liquid}$ (Background flow). **Effect:** Turbulent wake trailing behind the bubble. STYLE: Technical schematics, clean lines, forces color-coded."
-->
![[IMG_04_003.jpg]]

The fundamental drag force equation relates the drag force to relative velocity:

$$\mathbf{F}_D = \frac{1}{2} C_D \rho_c A |\mathbf{u}_r| \mathbf{u}_r$$

| Symbol | Meaning | Unit |
|--------|---------|------|
| $F_D$ | Drag force | N |
| $C_D$ | Drag coefficient | - |
| $\rho_c$ | Continuous phase density | kg/m³ |
| $A$ | Projected area | m² |
| $\mathbf{u}_r$ | Relative velocity ($\mathbf{u}_d - \mathbf{u}_c$) | m/s |

### Per Unit Volume Form

For Euler-Euler formulations, drag is expressed per unit volume:

$$\mathbf{F}_D = K (\mathbf{u}_c - \mathbf{u}_d)$$

where $K$ = momentum exchange coefficient [kg/(m³·s)]

---

## 2. Drag Coefficient Regimes

The drag coefficient $C_D$ varies with Reynolds number, reflecting different physical mechanisms:

### Reynolds Number

$$Re = \frac{\rho_c |\mathbf{u}_r| d}{\mu_c}$$

### Regime Definitions

| Re Range | Regime | $C_D$ Correlation | Dominant Mechanism |
|----------|--------|-------------------|-------------------|
| Re < 1 | Stokes | $\frac{24}{Re}$ | Viscous drag |
| 1 < Re < 1000 | Transition | $\frac{24}{Re}(1+0.15Re^{0.687})$ | Mixed |
| Re > 1000 | Newton | 0.44 | Pressure drag |

### Stokes Regime Derivation

For creeping flow (Re ≪ 1), the exact solution gives:

$$C_D = \frac{24}{Re}$$

Substituting into drag equation:

$$\mathbf{F}_D = 3\pi \mu_c d \mathbf{u}_r$$

This linear relationship is the **Stokes Drag Law**.

### Transition Regime

The Schiller-Naumann correlation bridges Stokes and Newton regimes:

$$C_D = \frac{24}{Re}(1+0.15Re^{0.687})$$

### Newton Regime

For fully turbulent flow (Re ≫ 1000):

$$C_D \approx 0.44 = \text{constant}$$

Drag force now scales with velocity squared: $\mathbf{F}_D \propto |\mathbf{u}_r|\mathbf{u}_r$

---

## 3. Physical Origin of Drag

### Viscous Drag (Low Re)

**Mechanism:** Shear stress on particle surface

- Caused by **velocity gradient** in boundary layer
- Skin friction dominates
- Scales with velocity: $F_D \propto u_r$
- Dominates in **Stokes regime** (Re < 1)

$$C_{D,viscous} = \frac{24}{Re}$$

### Pressure Drag (High Re)

**Mechanism:** Pressure difference between front and rear

- Caused by **flow separation** and wake formation
- Form drag dominates
- Scales with velocity squared: $F_D \propto u_r^2$
- Dominates in **Newton regime** (Re > 1000)

$$C_{D,pressure} \approx 0.44$$

### Total Drag Coefficient

$$C_D = C_{D,viscous} + C_{D,pressure}$$

The relative contribution shifts with Reynolds number.

---

## 4. Factors Affecting Drag

### Shape Effects

Particle shape dramatically alters drag:

| Shape | $C_D$ (Re=100) | Effect |
|-------|----------------|--------|
| Sphere | 1.0 | Baseline |
| Ellipsoid (streamlined) | 0.5-0.8 | Delays separation |
| Disk (bluff) | 1.1-1.2 | Early separation |

**Shape correction:** $C_D' = C_D \cdot \Phi_{shape}$

### Concentration Effects

In dense suspensions, particle-particle interactions modify drag:

$$C_D^{eff} = C_D \cdot f(\alpha_d)$$

**Richardson-Zaki correlation:**
$$f = (1-\alpha_d)^{-n}$$

where $n \approx 4.65$ for low Re, decreasing at higher Re.

**Physical mechanism:** Crowding increases effective viscosity and alters wake interactions.

### Surface Contamination

Surfactants significantly affect bubble drag:

| Condition | Surface Motion | $C_D$ Effect |
|-----------|----------------|--------------|
| Clean bubble | Free-slip (internal circulation) | Lower $C_D$ |
| Contaminated | No-slip (rigid surface) | Higher $C_D$ |

**Mechanism:** Surfactants **immobilize** surface → no internal circulation → behaves like rigid sphere with larger wake.

**Implication:** $C_D$ can increase by 50-100% for contaminated bubbles.

### Turbulence Effects

High turbulence levels can:
- Enhance momentum exchange → higher effective drag
- Modify separation points → reduce form drag
- Depend on turbulent intensity relative to particle size

---

## 5. Terminal Velocity

At steady state, drag balances buoyancy:

$$\mathbf{F}_D + \mathbf{F}_g + \mathbf{F}_b = 0$$

### General Expression

$$u_t = \sqrt{\frac{4(\rho_c - \rho_d)gd}{3\rho_c C_D}}$$

Note: $C_D$ itself depends on $u_t$ through Re → implicit equation.

### Stokes Regime Solution

For $C_D = 24/Re$:

$$u_t = \frac{(\rho_c - \rho_d)gd^2}{18\mu_c}$$

**Key scaling:** $u_t \propto d^2$ (strong size dependence)

### Newton Regime Solution

For $C_D = 0.44$:

$$u_t = 1.74\sqrt{\frac{(\rho_c - \rho_d)gd}{\rho_c}}$$

**Key scaling:** $u_t \propto \sqrt{d}$ (weaker size dependence)

---

## 6. Numerical Considerations

### Implicit vs Explicit Treatment

**Implicit (recommended):**
```cpp
// Implicit in momentum equation
fvm::Sp(K, U)  // Adds to diagonal → stable
```

**Advantages:**
- Unconditionally stable for large K
- Improves diagonal dominance of matrix
- Better convergence at high phase fractions

**Explicit:**
```cpp
// Explicit source term
K * (Uc - Ud)  // Can cause instability
```

**Disadvantages:**
- Stability constraint: $\Delta t < 1/K$
- May require severe time-step reduction

### Residual Values

Prevent division by zero at low relative velocities:

```cpp
drag
{
    (air in water)
    {
        type        SchillerNaumann;
        residualRe  1e-3;    // Prevents Re → 0
    }
}
```

**Modified Re calculation:**
$$Re_{eff} = \max\left(\frac{\rho_c |\mathbf{u}_r| d}{\mu_c}, Re_{residual}\right)$$

### Convergence Issues

**Symptoms:**
- Oscillations in velocity field
- Slow convergence of momentum equations

**Solutions:**
1. Use implicit treatment
2. Under-relax momentum equation (0.7-0.9)
3. Limit K to maximum physically reasonable value
4. Ensure proper initial conditions

---

## Key Takeaways

- **Drag force** originates from viscous shear (low Re) and pressure differences (high Re), with the drag coefficient $C_D$ capturing regime-dependent behavior through Reynolds number correlations
- **Three regimes** govern drag: Stokes ($C_D = 24/Re$, viscous-dominated), Transition (Schiller-Naumann correlation), and Newton ($C_D \approx 0.44$, pressure-dominated)
- **Shape, concentration, and surface contamination** significantly modify drag: streamlined shapes reduce $C_D$, particle crowding increases effective drag via $(1-\alpha_d)^{-n}$, and surfactants can double $C_D$ by immobilizing bubble surfaces
- **Terminal velocity** balances drag and buoyancy, with different scaling laws in each regime: $u_t \propto d^2$ in Stokes flow versus $u_t \propto \sqrt{d}$ in Newton flow
- **Numerical stability** requires implicit drag treatment (fvm::Sp) and residual Reynolds number limiting to prevent division by zero at low relative velocities

---

## Quick Reference

| Regime | Re Range | $C_D$ Correlation | Key Characteristic |
|--------|----------|-------------------|-------------------|
| Stokes | Re < 1 | 24/Re | Viscous-dominated, linear drag |
| Transition | 1-1000 | $\frac{24}{Re}(1+0.15Re^{0.687})$ | Mixed mechanisms |
| Newton | Re > 1000 | 0.44 | Pressure-dominated, quadratic drag |

**Key Equations:**
- Reynolds number: $Re = \rho_c |\mathbf{u}_r| d / \mu_c$
- Drag force: $\mathbf{F}_D = \frac{1}{2} C_D \rho_c A |\mathbf{u}_r| \mathbf{u}_r$
- Terminal velocity (Stokes): $u_t = (\rho_c - \rho_d)gd^2 / (18\mu_c)$

---

## Concept Check

<details>
<summary><b>1. ทำไม $C_D$ ลดลงเมื่อ Re เพิ่ม?</b></summary>

เพราะ **viscous drag** (proportional to 1/Re) dominates ที่ low Re แต่เมื่อ Re สูงขึ้น **pressure drag** (constant) จะ dominate
</details>

<details>
<summary><b> Implicit treatment ดีอย่างไร?</b></summary>

เพิ่ม **diagonal dominance** ของ matrix → **better convergence** โดยเฉพาะเมื่อ K สูง
</details>

<details>
<summary><b>3. ทำไม contaminated bubbles มี drag สูงกว่า?</b></summary>

Surfactants **immobilize surface** → ไม่มี internal circulation → behaves like **rigid sphere** ที่มี wake ใหญ่กว่า
</details>

<details>
<summary><b>4. ทำไม terminal velocity scale กับ $d^2$ ใน Stokes regime แต่ $\sqrt{d}$ ใน Newton regime?</b></summary>

ใน Stokes regime, $C_D \propto 1/Re \propto 1/u_t$ → drag $\propto u_t$ → force balance ให้ $u_t \propto d^2$. ใน Newton regime, $C_D = \text{const}$ → drag $\propto u_t^2$ → force balance ให้ $u_t \propto \sqrt{d}$
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Specific Models:** [02_Specific_Drag_Models.md](02_Specific_Drag_Models.md)
- **OpenFOAM Implementation:** [03_OpenFOAM_Implementation.md](03_OpenFOAM_Implementation.md)