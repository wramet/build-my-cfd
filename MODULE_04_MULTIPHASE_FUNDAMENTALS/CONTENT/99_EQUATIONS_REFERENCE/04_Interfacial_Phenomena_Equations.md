# Interfacial Phenomena Equations

สมการปรากฏการณ์ที่ผิวสัมผัส

---

## 1. Surface Tension

### Young-Laplace Equation

$$\Delta p = \sigma \kappa = \sigma \left(\frac{1}{R_1} + \frac{1}{R_2}\right)$$

| Variable | Meaning |
|----------|---------|
| $\Delta p$ | Pressure jump |
| $\sigma$ | Surface tension [N/m] |
| $\kappa$ | Mean curvature [1/m] |
| $R_1, R_2$ | Principal radii |

### Special Cases

| Shape | κ |
|-------|---|
| Sphere (R) | 2/R |
| Cylinder (R) | 1/R |
| Flat | 0 |

---

## 2. CSF Model

$$\mathbf{F}_\sigma = \sigma \kappa \nabla \alpha$$

### Curvature

$$\kappa = -\nabla \cdot \hat{\mathbf{n}} = -\nabla \cdot \frac{\nabla \alpha}{|\nabla \alpha|}$$

---

## 3. Contact Angle

### Young's Equation

$$\cos\theta = \frac{\sigma_{SG} - \sigma_{SL}}{\sigma_{LG}}$$

| θ | Wettability |
|---|-------------|
| < 90° | Hydrophilic |
| > 90° | Hydrophobic |

---

## 4. Capillary Pressure

$$p_c = p_{nw} - p_w = \sigma \kappa$$

---

## 5. Marangoni Effect

$$\tau_M = \nabla_s \sigma = \frac{d\sigma}{dT} \nabla_s T$$

---

## 6. Dimensionless Numbers

| Number | Formula | Meaning |
|--------|---------|---------|
| Capillary | $Ca = \frac{\mu U}{\sigma}$ | Viscous/surface tension |
| Weber | $We = \frac{\rho U^2 L}{\sigma}$ | Inertia/surface tension |
| Eötvös | $Eo = \frac{\Delta\rho g L^2}{\sigma}$ | Buoyancy/surface tension |

---

## 7. OpenFOAM Implementation

```cpp
// constant/transportProperties
sigma   [1 0 -2 0 0 0 0] 0.072;

// Contact angle BC
wall
{
    type    constantAlphaContactAngle;
    theta0  70;
}
```

---

## Quick Reference

| Equation | Application |
|----------|-------------|
| Young-Laplace | Bubble pressure |
| CSF | Interface force |
| Young | Contact angle |

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Mass Conservation:** [01_Mass_Conservation.md](01_Mass_Conservation.md)
- **Momentum Conservation:** [02_Momentum_Conservation.md](02_Momentum_Conservation.md)