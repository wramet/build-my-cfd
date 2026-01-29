# Phase Change Theory and Expansion Term (ทฤษฎีการเปลี่ยนสภาพและ Expansion Term)

## Learning Objectives

After studying this section, you should be able to:
- **Derive** the expansion term for two-phase flow with phase change
- **Implement** the Lee evaporation model in C++
- **Modify** the pressure equation to include the expansion source term
- **Understand** why the expansion term is critical for convergence
- **Calculate** mass transfer rates based on temperature deviation from saturation

---

## Navigation Map

```
10_Two_Phase_Flow
      │
      ▼
11_Phase_Change_Theory ← YOU ARE HERE
      │
      ▼
12_Refrigerant_Properties
```

---

## Overview

The expansion term is the **most critical component** for two-phase flow simulations with phase change. Without it, the pressure equation will diverge due to the large density ratio between liquid and vapor phases.

> **Why is the expansion term critical?**
> - **Volume expansion**: When liquid evaporates to vapor, volume increases ~30x for R410A
> - **Pressure source**: This creates a massive source term in the pressure equation
> - **Without it**: Pressure-velocity coupling fails, simulation diverges
> - **With it**: Mass conservation is enforced, solver converges

---

## 1. Thermodynamic Foundations

### Saturation Properties

**Saturation Temperature $T_{sat}(P)$**:
The temperature at which phase change occurs at a given pressure.

For R410A refrigerant:
$$T_{sat} \approx 39.4°C \text{ at } 10 \text{ bar}$$

**Clausius-Clapeyron Relation**:
$$\frac{dP}{dT} = \frac{h_{fg}}{T(v_g - v_l)}$$

Where:
- $h_{fg}$ = latent heat of vaporization (J/kg)
- $v_g$ = specific volume of vapor (m³/kg)
- $v_l$ = specific volume of liquid (m³/kg)

### Latent Heat

**Latent Heat $h_{fg}$**:
Energy required to convert liquid to vapor at constant temperature.

$$h_{fg} = h_v - h_l$$

For R410A at 10 bar:
$$h_{fg} \approx 200 \text{ kJ/kg}$$

> **⚠️ Important**: Latent heat is **NOT** temperature-dependent in the Lee model
> - Simplifies implementation
> - Reasonable approximation for small temperature ranges
> - For accuracy, use CoolProp for temperature-dependent $h_{fg}(T,P)$

---

## 2. The Expansion Term (CRITICAL)

### Mathematical Derivation

Starting from **mass conservation for two-phase flow**:

$$\frac{\partial \rho}{\partial t} + \nabla \cdot (\rho \mathbf{U}) = 0$$

For **incompressible phases** ($\rho_l = \text{constant}$, $\rho_v = \text{constant}$) with **phase change**:

$$\nabla \cdot \mathbf{U} = \dot{m}\left(\frac{1}{\rho_v} - \frac{1}{\rho_l}\right)$$

Where:
- $\dot{m}$ = mass transfer rate (kg/m³s)
- $\dot{m} > 0$ = evaporation (liquid → vapor)
- $\dot{m} < 0$ = condensation (vapor → liquid)
- $\rho_v$ = vapor density (~30-50 kg/m³ for R410A)
- $\rho_l$ = liquid density (~1000 kg/m³ for R410A)

### Derivation Step-by-Step

**Step 1: Start with mixture density**

$$\rho = \alpha \rho_v + (1 - \alpha) \rho_l$$

Where $\alpha$ = void fraction (vapor volume fraction)

**Step 2: Differentiate with respect to time**

$$\frac{\partial \rho}{\partial t} = \frac{\partial \alpha}{\partial t} (\rho_v - \rho_l)$$

**Step 3: Mass transfer rate definition**

$$\dot{m} = \frac{\partial \alpha}{\partial t} \rho_v$$

(Positive $\dot{m}$ = liquid converting to vapor)

**Step 4: Substitute into continuity equation**

$$\frac{\partial \alpha}{\partial t} (\rho_v - \rho_l) + \nabla \cdot (\rho \mathbf{U}) = 0$$

$$\frac{\dot{m}}{\rho_v} (\rho_v - \rho_l) + \nabla \cdot (\rho \mathbf{U}) = 0$$

**Step 5: Simplify for incompressible phases**

$$\dot{m}\left(1 - \frac{\rho_l}{\rho_v}\right) + \rho_v \nabla \cdot \mathbf{U} = 0$$

$$\boxed{\nabla \cdot \mathbf{U} = \dot{m}\left(\frac{1}{\rho_v} - \frac{1}{\rho_l}\right)}$$

### Why This is Critical

**Density Ratio for R410A**:
$$\frac{\rho_v}{\rho_l} \approx \frac{30}{1000} = \frac{1}{30}$$

**Volume Expansion Factor**:
$$\frac{1}{\rho_v} - \frac{1}{\rho_l} = \frac{1}{30} - \frac{1}{1000} \approx 0.032 \text{ m³/kg}$$

This means:
- **1 kg of liquid** → **30 kg of vapor** (volume-wise)
- **Mass transfer creates massive velocity divergence**
- **Pressure equation MUST account for this**

### Implementation in Pressure Equation

The pressure correction equation **MUST include** the expansion term:

$$\nabla \cdot \left(\frac{1}{A_p} \nabla p'\right) = \nabla \cdot \mathbf{U}^* - S_{expansion}$$

Where:
$$S_{expansion} = \dot{m}\left(\frac{1}{\rho_v} - \frac{1}{\rho_l}\right)$$

> **❌ FORBIDDEN**: Using standard pressure equation without $S_{expansion}$
> - This is the #1 reason two-phase simulations diverge
> - The pressure-velocity coupling assumes $\nabla \cdot \mathbf{U} = 0$
> - With phase change, $\nabla \cdot \mathbf{U} \neq 0$

---

## 3. Lee Evaporation Model

### Mass Transfer Rate

The **Lee model** calculates mass transfer based on temperature deviation from saturation:

$$\dot{m} = r_e \alpha_l \rho_l \frac{T - T_{sat}}{T_{sat}}$$

For **evaporation** ($T > T_{sat}$):
$$\dot{m} = r_e \alpha_l \rho_l \max\left(0, \frac{T - T_{sat}}{T_{sat}}\right)$$

For **condensation** ($T < T_{sat}$):
$$\dot{m} = -r_c \alpha_v \rho_v \max\left(0, \frac{T_{sat} - T}{T_{sat}}\right)$$

Where:
- $r_e$ = evaporation coefficient (typical: 0.1 to 10 s⁻¹)
- $r_c$ = condensation coefficient (typical: 0.1 to 10 s⁻¹)
- $\alpha_l$ = liquid volume fraction = $(1 - \alpha)$
- $\alpha_v$ = vapor volume fraction = $\alpha$
- $\rho_l$ = liquid density
- $\rho_v$ = vapor density

### Coefficient Tuning

**Guidelines for $r_e$ and $r_c$**:

| Value Range | Stability | Accuracy | Recommendation |
|-------------|-----------|----------|----------------|
| 0.01 - 0.1 | Very stable | Low (slow phase change) | Use for initial testing |
| 0.1 - 1 | Stable | Moderate | Default starting point |
| 1 - 10 | May be unstable | High | Tune after stable solution found |

> **💡 Tip**: Start with $r_e = r_c = 0.1$ and increase gradually
> - If simulation diverges → decrease coefficients
> - If phase change is too slow → increase coefficients
> - Always verify mass conservation after tuning

---

## 4. Implementation Focus (C++)

### Class Structure

```cpp
class LeeEvaporationModel
{
private:
    const dimensionedScalar r_e_;      // Evaporation coefficient
    const dimensionedScalar r_c_;      // Condensation coefficient
    const volScalarField& T_;          // Temperature field
    const volScalarField& alpha_;      // Void fraction field
    const dimensionedScalar rho_l_;    // Liquid density
    const dimensionedScalar rho_v_;    // Vapor density
    const volScalarField& T_sat_;     // Saturation temperature

public:
    // Constructor
    LeeEvaporationModel(
        const dimensionedScalar& r_e,
        const dimensionedScalar& r_c,
        const volScalarField& T,
        const volScalarField& alpha,
        const dimensionedScalar& rho_l,
        const dimensionedScalar& rho_v,
        const volScalarField& T_sat
    )
    :
        r_e_(r_e),
        r_c_(r_c),
        T_(T),
        alpha_(alpha),
        rho_l_(rho_l),
        rho_v_(rho_v),
        T_sat_(T_sat)
    {}

    // Calculate mass transfer rate
    tmp<volScalarField> calculateMassTransfer() const
    {
        // Liquid and vapor fractions
        volScalarField alpha_l = scalar(1) - alpha_;
        volScalarField alpha_v = alpha_;

        // Evaporation (T > T_sat)
        volScalarField m_evap = r_e_ * alpha_l * rho_l_ *
            max((T_ - T_sat_) / T_sat_, scalar(0));

        // Condensation (T < T_sat)
        volScalarField m_cond = -r_c_ * alpha_v * rho_v_ *
            max((T_sat_ - T_) / T_sat_, scalar(0));

        return tmp<volScalarField>(
            m_evap + m_cond
        );
    }

    // Calculate expansion term source
    tmp<volScalarField> expansionTerm() const
    {
        tmp<volScalarField> m_dot = calculateMassTransfer();

        // Volume expansion factor
        dimensionedScalar volExp = (scalar(1) / rho_v_) - (scalar(1) / rho_l_);

        return tmp<volScalarField>(
            m_dot * volExp
        );
    }
};
```

### Pressure Equation Modification

```cpp
// In the PISO loop or pressure correction equation:

// Calculate expansion term
tmp<volScalarField> S_expansion = leeModel.expansionTerm();

// Predicted velocity divergence
volScalarField divU = fvc::div(phi_);

// Pressure equation with expansion term
fvScalarMatrix pEqn
(
    fvm::laplacian(1/A_U, p_corr)
 ==
 divU - S_expansion  // <-- CRITICAL: Include expansion term
);

pEqn.solve();

// Correct velocity
phi += fvc::interpolate(p_corr) & mesh.Sf();
```

### Alpha Equation with Source

```cpp
// Void fraction transport with phase change source

tmp<fvScalarMatrix> alphaEqn
(
    fvm::ddt(alpha)
  + fvm::div(phi, alpha)
  - fvm::laplacian(D_alpha, alpha)
 ==
    // Phase change source
    leeModel.calculateMassTransfer() / rho_v_
);

alphaEqn.solve();

// Bounding (CRITICAL for stability)
alpha = max(min(alpha, scalar(1)), scalar(0));
```

---

## 5. Energy Equation with Latent Heat

### Energy Balance

With phase change, the energy equation includes **latent heat source**:

$$\frac{\partial (\rho h)}{\partial t} + \nabla \cdot (\rho \mathbf{U} h) = \nabla \cdot (k \nabla T) - \dot{m} h_{fg}$$

Where:
- $h_{fg}$ = latent heat (J/kg)
- $\dot{m} h_{fg}$ = energy absorbed/released by phase change

> **Sign Convention**:
> - **Evaporation** ($\dot{m} > 0$): Energy **absorbed** (cooling)
> - **Condensation** ($\dot{m} < 0$): Energy **released** (heating)

### Implementation

```cpp
// Energy equation with latent heat source

tmp<fvScalarMatrix> TEqn
(
    fvm::ddt(rho, T)
  + fvm::div(phi, T)
  - fvm::laplacian(k/rho/Cp, T)
 ==
    // Latent heat source
   -leeModel.calculateMassTransfer() * h_fg / rho / Cp
);

TEqn.solve();
```

---

## 6. Verification Checklist

Before running a simulation with phase change:

- [ ] Expansion term included in pressure equation
- [ ] Sign convention correct ($\dot{m} > 0$ for evaporation)
- [ ] Density ratio terms correct ($1/\rho_v - 1/\rho_l$)
- [ ] Latent heat included in energy equation
- [ ] Alpha field bounded [0, 1]
- [ ] Mass transfer coefficients tuned ($r_e$, $r_c$)
- [ ] Mass conservation verified ($\sum \dot{m} \approx 0$)

---

## 7. Common Pitfalls

### ❌ **Wrong**: Standard incompressible pressure equation

```cpp
// This is WRONG for two-phase flow with phase change!
fvScalarMatrix pEqn
(
    fvm::laplacian(1/A_U, p_corr) == fvc::div(phi_)
);
```

### ✅ **Correct**: Include expansion term

```cpp
// Correct: Include expansion term
fvScalarMatrix pEqn
(
    fvm::laplacian(1/A_U, p_corr) == fvc::div(phi_) - S_expansion
);
```

### ❌ **Wrong**: Unbounded alpha field

```cpp
alphaEqn.solve();
// Alpha can go outside [0, 1] → DIVERGENCE
```

### ✅ **Correct**: Bounded alpha field

```cpp
alphaEqn.solve();
alpha = max(min(alpha, scalar(1)), scalar(0));  // CRITICAL
```

### ❌ **Wrong**: Too large mass transfer coefficient

```cpp
const scalar r_e = 100.0;  // Too large! Will cause instability
```

### ✅ **Correct**: Start small, tune gradually

```cpp
const scalar r_e = 0.1;  // Start small
// Increase gradually after solution is stable
```

---

## 8. Testing and Validation

### Test Case: 1D Evaporating Film

**Setup**:
- Liquid film at $T < T_{sat}$ on heated wall
- Wall temperature $T_w > T_{sat}$
- Measure evaporation rate

**Validation**:
```cpp
// Calculate total mass transfer
scalar totalMassTransfer = fvc::domainIntegrate(
    leeModel.calculateMassTransfer()
).value();

// Should match analytical solution
Info << "Total mass transfer: " << totalMassTransfer << endl;
```

### Convergence Criteria

- **Mass conservation**: $|\sum \dot{m}| / \dot{m}_{in} < 10^{-6}$
- **Alpha bounds**: $\min(\alpha) \geq 0$, $\max(\alpha) \leq 1$
- **Pressure residual**: $< 10^{-6}$
- **Energy balance**: $|Q_{in} - Q_{out} - \dot{m} h_{fg}| < 10^{-3}$

---

## Summary

| Component | Equation | Purpose |
|-----------|----------|---------|
| **Expansion Term** | $\nabla \cdot \mathbf{U} = \dot{m}(1/\rho_v - 1/\rho_l)$ | Account for volume change |
| **Lee Model** | $\dot{m} = r \alpha \rho (T - T_{sat})/T_{sat}$ | Calculate mass transfer |
| **Pressure Eq** | $\nabla \cdot (1/A_p \nabla p') = \nabla \cdot \mathbf{U}^* - S_{expansion}$ | Enforce mass conservation |
| **Energy Eq** | $\partial(\rho h)/\partial t + \nabla \cdot (\rho \mathbf{U} h) = \nabla \cdot (k \nabla T) - \dot{m} h_{fg}$ | Include latent heat |

> **🎯 Key Takeaway**: The expansion term is **non-negotiable** for two-phase flow with phase change. Without it, your simulation will diverge.

---

## References

- **File**: `openfoam_temp/src/transportModels/twoPhaseModels/interfaceProperties/interfaceProperties.C`
- **Paper**: Lee, W.H. (1979). "A Pressure Iteration Scheme for Two-Phase Flow Modeling"
- **Next**: Day 12 - Refrigerant Properties (CoolProp integration)
