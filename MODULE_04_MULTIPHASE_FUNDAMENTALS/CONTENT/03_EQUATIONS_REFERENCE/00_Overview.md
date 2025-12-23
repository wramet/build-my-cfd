# Multiphase Equations Reference

## Overview
This module provides a comprehensive reference for the core conservation equations (mass, momentum, energy) and interfacial phenomena equations used in Eulerian-Eulerian multiphase flow modeling within OpenFOAM. The content covers mathematical foundations, detailed derivations, numerical implementations, and practical applications.

> [!INFO] **Scope and Coverage**
> This reference serves as a complete technical guide for multiphase flow simulations, bridging theoretical foundations with practical OpenFOAM implementation. The material ranges from basic conservation laws to advanced topics like granular flows and compressible multiphase systems.

---

## Mathematical Framework

### **Eulerian Multiphase Flow Theory**

In Eulerian multiphase flow modeling, each phase $k$ is treated as an interpenetrating continuum occupying the same domain, characterized by its **volume fraction** $\alpha_k$ with the fundamental constraint:

$$\sum_{k=1}^{N} \alpha_k = 1 \tag{1.1}$$

Each phase has its own set of conservation equations linked through **interfacial transfer terms**.

#### **Phase Averaging Theorem**

The transition from microscopic to macroscopic descriptions uses **phase averaging**:

$$\langle \phi_k \rangle_V = \frac{1}{V_k} \int_{V_k} \phi_k \, \mathrm{d}V \tag{1.2}$$

where $\phi_k$ is any property of phase $k$ and $V_k$ is the volume occupied by phase $k$.

The **intrinsic phase average** relates to the control volume average:

$$\bar{\phi}_k = \frac{1}{V} \int_{V_k} \phi_k \, \mathrm{d}V = \alpha_k \langle \phi_k \rangle_V \tag{1.3}$$

#### **Spatial Averaging Theorem**

For spatial derivatives of phase-averaged quantities:

$$\langle \nabla \phi_k \rangle_V = \nabla \langle \phi_k \rangle_V + \frac{1}{V_k} \int_{A_k} \phi_k \mathbf{n}_k \, \mathrm{d}A \tag{1.4}$$

The second term accounts for **discontinuities at interfaces**.

#### **Temporal Averaging Theorem**

For temporal derivatives with moving interfaces:

$$\left\langle \frac{\partial \phi_k}{\partial t} \right\rangle_V = \frac{\partial}{\partial t} \langle \phi_k \rangle_V - \frac{1}{V_k} \int_{A_k} \phi_k \mathbf{u}_i \cdot \mathbf{n}_k \, \mathrm{d}A \tag{1.5}$$

where $\mathbf{u}_i$ is the interface velocity.

---

## Conservation Equations

### **General Conservation Law Form**

For any conserved property $\psi_k$ of phase $k$:

$$\frac{\partial}{\partial t}(\alpha_k \rho_k \psi_k) + \nabla \cdot (\alpha_k \rho_k \mathbf{u}_k \psi_k) = \nabla \cdot (\alpha_k \mathbf{J}_k) + \alpha_k S_k + \Gamma_k \tag{2.1}$$

**Variable Definitions:**
- $\alpha_k$: Volume fraction (dimensionless)
- $\rho_k$: Density ($\text{kg/m}^3$)
- $\mathbf{u}_k$: Velocity vector ($\text{m/s}$)
- $\mathbf{J}_k$: Diffusive flux vector
- $S_k$: Source term
- $\Gamma_k$: Interfacial exchange term

### **Mass Conservation**

For each phase $k$:

$$\frac{\partial}{\partial t}(\alpha_k \rho_k) + \nabla \cdot (\alpha_k \rho_k \mathbf{u}_k) = \sum_{j \neq k} \dot{m}_{jk} \tag{2.2}$$

where $\dot{m}_{jk}$ is the mass transfer rate from phase $j$ to phase $k$.

**Mass Conservation Constraint:**
$$\sum_{k=1}^{N} \dot{m}_k = 0 \tag{2.3}$$

For incompressible phases ($\rho_k = \text{constant}$):

$$\frac{\partial \alpha_k}{\partial t} + \nabla \cdot (\alpha_k \mathbf{u}_k) = \frac{1}{\rho_k} \sum_{j \neq k} \dot{m}_{jk} \tag{2.4}$$

#### **Volume Fraction Evolution**

The volume fraction equation follows from mass conservation:

$$\frac{\partial \alpha_k}{\partial t} + \nabla \cdot (\alpha_k \mathbf{u}_k) = \frac{1}{\rho_k} \sum_{j \neq k} \dot{m}_{jk} \tag{2.5}$$

### **Momentum Conservation**

For each phase $k$:

$$\frac{\partial}{\partial t}(\alpha_k \rho_k \mathbf{u}_k) + \nabla \cdot (\alpha_k \rho_k \mathbf{u}_k \mathbf{u}_k) = -\alpha_k \nabla p + \nabla \cdot (\alpha_k \boldsymbol{\tau}_k) + \alpha_k \rho_k \mathbf{g} + \mathbf{M}_k \tag{2.6}$$

**Stress Tensor for Newtonian Fluids:**
$$\boldsymbol{\tau}_k = \mu_k \left( \nabla \mathbf{u}_k + (\nabla \mathbf{u}_k)^T \right) - \frac{2}{3}\mu_k (\nabla \cdot \mathbf{u}_k)\mathbf{I} \tag{2.7}$$

#### **Interfacial Momentum Transfer**

The interfacial momentum transfer $\mathbf{M}_k$ consists of several forces:

$$\mathbf{M}_k = \sum_{j \neq k} \left[ \mathbf{M}_{kj}^{drag} + \mathbf{M}_{kj}^{lift} + \mathbf{M}_{kj}^{vm} + \mathbf{M}_{kj}^{td} \right] \tag{2.8}$$

**Drag Force:**
$$\mathbf{M}_{kj}^{drag} = K_{kj}(\mathbf{u}_j - \mathbf{u}_k) \tag{2.9}$$

**Lift Force:**
$$\mathbf{M}_{kj}^{lift} = C_L \rho_k \alpha_k \alpha_j (\mathbf{u}_j - \mathbf{u}_k) \times (\nabla \times \mathbf{u}_k) \tag{2.10}$$

**Virtual Mass Force:**
$$\mathbf{M}_{kj}^{vm} = C_{vm} \rho_k \alpha_k \alpha_j \left( \frac{\mathrm{D}\mathbf{u}_j}{\mathrm{D}t} - \frac{\mathrm{D}\mathbf{u}_k}{\mathrm{D}t} \right) \tag{2.11}$$

**Conservation Constraint:**
$$\sum_{k=1}^{N} \mathbf{M}_k = \mathbf{0} \tag{2.12}$$

### **Energy Conservation**

For each phase $k$:

$$\frac{\partial}{\partial t}(\alpha_k \rho_k h_k) + \nabla \cdot (\alpha_k \rho_k \mathbf{u}_k h_k) = \alpha_k \frac{\partial p_k}{\partial t} + \nabla \cdot (\alpha_k k_k \nabla T_k) + Q_k + \sum_{j \neq k} \dot{m}_{jk} h_j \tag{2.13}$$

where $h_k$ is the specific enthalpy and $Q_k$ represents interfacial heat transfer.

---

## Interfacial Phenomena

### **Surface Tension Effects**

#### **Young-Laplace Equation**

The pressure jump across a curved interface due to surface tension:

$$\Delta p = p_2 - p_1 = \sigma \kappa \tag{3.1}$$

where $\sigma$ is the surface tension coefficient and $\kappa$ is the interface curvature:

$$\kappa = \nabla \cdot \mathbf{n} = \nabla \cdot \left( \frac{\nabla \alpha}{|\nabla \alpha|} \right) \tag{3.2}$$

**Special Cases:**
| Shape | Curvature ($\kappa$) | Pressure Jump |
|-------|-------------------|---------------|
| Sphere | $2/R$ | $\Delta p = \frac{2\sigma}{R}$ |
| Cylinder | $1/R$ | $\Delta p = \frac{\sigma}{R}$ |

#### **Continuum Surface Force (CSF) Model**

For diffuse interfaces, surface tension becomes a volume force:

$$\mathbf{F}_{st} = \sigma \kappa \nabla \alpha \tag{3.3}$$

### **Marangoni Effects**

Surface tension gradients drive flow along interfaces:

$$\mathbf{F}_{Marangoni} = \nabla_s \sigma \cdot |\nabla \alpha| \tag{3.4}$$

where $\nabla_s$ is the surface gradient operator:

$$\nabla_s = (\mathbf{I} - \mathbf{n}\mathbf{n}) \cdot \nabla \tag{3.5}$$

**Temperature-Dependent Surface Tension:**
$$\frac{\partial \sigma}{\partial T} < 0 \quad \text{(for most liquids)} \tag{3.6}$$

### **Contact Angle and Wetting**

#### **Young's Equation**

At the three-phase contact line:

$$\cos \theta = \frac{\sigma_{sg} - \sigma_{sl}}{\sigma_{lg}} \tag{3.7}$$

**Wetting Regimes:**
| Regime | Contact Angle | Condition |
|--------|---------------|------------|
| Complete wetting | $\theta = 0°$ | $\sigma_{sg} - \sigma_{sl} = \sigma_{lg}$ |
| Partial wetting | $0° < \theta < 90°$ | $\sigma_{sg} > \sigma_{sl}$ |
| Non-wetting | $90° < \theta < 180°$ | $\sigma_{sg} < \sigma_{sl}$ |
| Complete non-wetting | $\theta = 180°$ | $\sigma_{sg} - \sigma_{sl} = -\sigma_{lg}$ |

---

## Turbulence Modeling

### **Mixture Turbulence Models**

For multiphase flows, the mixture $k$-$\epsilon$ model:

**Turbulent Kinetic Energy:**
$$\frac{\partial (\rho_m k)}{\partial t} + \nabla \cdot (\rho_m \mathbf{u}_m k) = \nabla \cdot \left( \frac{\mu_{t,m}}{\sigma_k} \nabla k \right) + P_k - \rho_m \epsilon + \sum_{k,l} K_{kl} |\mathbf{u}_k - \mathbf{u}_l|^2 \tag{4.1}$$

**Dissipation Rate:**
$$\frac{\partial (\rho_m \epsilon)}{\partial t} + \nabla \cdot (\rho_m \mathbf{u}_m \epsilon) = \nabla \cdot \left( \frac{\mu_{t,m}}{\sigma_\epsilon} \nabla \epsilon \right) + C_{\epsilon 1} \frac{\epsilon}{k} P_k - C_{\epsilon 2} \rho_m \frac{\epsilon^2}{k} \tag{4.2}$$

**Mixture Turbulent Viscosity:**
$$\mu_{t,m} = \rho_m C_\mu \frac{k^2}{\epsilon} \tag{4.3}$$

### **Phase-Specific Turbulence**

**Sato Model for Dispersed Phase:**
$$\mu_{t,d} = 0.6 \rho_d \alpha_d d_p |\mathbf{u}_c - \mathbf{u}_d| \tag{4.4}$$

---

## Special Cases

### **Granular Flow Equations**

#### **Granular Temperature**

Fluctuating kinetic energy of particles:

$$\Theta_s = \frac{1}{3} \langle \mathbf{c} \cdot \mathbf{c} \rangle \tag{5.1}$$

where $\mathbf{c} = \mathbf{u}_p - \bar{\mathbf{u}}_s$ is the fluctuating velocity.

#### **Granular Pressure**

Total granular pressure includes kinetic and collisional contributions:

$$p_s = \rho_s \Theta_s \left[ 1 + 2g_0 \alpha_s (1 + e) \right] \tag{5.2}$$

**Radial Distribution Function:**
$$g_0 = \frac{1}{(1 - \alpha_s)^3} \quad \text{(for moderate concentrations)} \tag{5.3}$$

#### **Collisional Dissipation**

Energy dissipation due to inelastic collisions:

$$\gamma_\Theta = 3(1 - e^2) g_0 \alpha_s^2 \rho_s d_p \Theta_s^{3/2} \tag{5.4}$$

#### **Granular Viscosity**

Total granular viscosity:

$$\mu_s = \frac{\rho_s d_p \sqrt{\Theta_s}}{6} \left[ \frac{1}{g_0(1+e)} + \frac{8}{5} \alpha_s (1+e) \right] \tag{5.5}$$

### **Compressible Multiphase Flow**

#### **Mixture Sound Speed**

For homogeneous equilibrium mixtures (Wood's equation):

$$\frac{1}{c_{mix}^2} = \sum_k \frac{\alpha_k}{\rho_k c_k^2} \tag{5.6}$$

**Two-Phase Case:**
$$\frac{1}{c_{mix}^2} = \frac{\alpha_l}{\rho_l c_l^2} + \frac{\alpha_g}{\rho_g c_g^2} \tag{5.7}$$

#### **Critical Flow Conditions**

Maximum mass flux through a nozzle:

$$G_{cr}^{HEM} = \sqrt{ \left[ \frac{x}{v_g} + \frac{(1-x)}{v_l} \right] \left[ \frac{x}{\rho_g c_g^2} + \frac{(1-x)}{\rho_l c_l^2} \right] } \tag{5.8}$$

---

## Closure Relations

### **Equations of State**

**Ideal Gas Law:**
$$p = \rho R T \tag{6.1}$$

**van der Waals Equation:**
$$\left(p + \frac{a\rho^2}{M^2}\right)\left(\frac{1}{\rho} - \frac{b}{M}\right) = R T \tag{6.2}$$

### **Transport Properties**

**Temperature-Dependent Viscosity (Arrhenius Model):**
$$\mu = \mu_0 \exp\left(\frac{E}{RT}\right) \tag{6.3}$$

**Chapman-Enskog Theory for Gases:**
$$k = \frac{5}{4} \mu c_p \tag{6.4}$$

### **Mixture Properties**

**Effective Density:**
$$\rho_{mix} = \sum_k \alpha_k \rho_k \tag{6.5}$$

**Effective Viscosity:**
$$\mu_{mix} = \sum_k \alpha_k \mu_k \tag{6.6}$$

**Effective Thermal Conductivity:**
$$k_{mix} = \sum_k \alpha_k k_k \tag{6.7}$$

---

## Numerical Implementation in OpenFOAM

### **Key Classes and Files**

| Component | Location | Description |
|-----------|----------|------------|
| **Multiphase Solvers** | `applications/solvers/multiphase/` | `multiphaseEulerFoam`, `twoPhaseEulerFoam` |
| **Phase System Classes** | `src/phaseSystemModels/` | `phaseSystem.H`, `dragModel.H`, `heatTransferModel.H` |
| **Turbulence Models** | `src/turbulenceModels/` | `kEpsilon.H`, `kOmega.H`, `LESModel.H` |
| **Thermophysical Models** | `src/thermophysicalModels/` | `specie.H`, `perfectGas.H`, `incompressibleGas.H` |

### **Momentum Equation Implementation**

```cpp
// OpenFOAM momentum equation for phase k
fvVectorMatrix UEqn
(
    fvm::ddt(alpha, rho, U) + fvm::div(alphaRhoPhi, U)
 ==
    -fvc::grad(p) + fvc::div(alpha*tau) + alpha*rho*g
    + interfacialMomentumTransfer
);
```

### **Volume Fraction Boundedness**

The MULES (Multidimensional Universal Limiter with Explicit Solution) algorithm ensures:

$$0 \leq \alpha_k \leq 1 \quad \text{and} \quad \sum_k \alpha_k = 1 \tag{7.1}$$

### **Time Step Constraints**

**CFL Condition for Compressible Flow:**
$$\Delta t \leq \frac{C_{CFL} \Delta x}{c_{mix} + |\mathbf{u}|} \tag{7.2}$$

**Low Mach Number Preconditioning:**
For $M < 0.3$, use artificial compressibility parameter $\beta$:

$$\frac{\partial p}{\partial t} + \beta^2 \rho_0 \nabla \cdot \mathbf{u} = 0 \tag{7.3}$$

---

## Solution Algorithms

### **SIMPLE Algorithm (Steady-State)**

1. **Momentum Prediction**: Solve momentum equations
2. **Pressure Correction**: Solve pressure correction equation
3. **Velocity Correction**: Update velocities based on pressure correction
4. **Volume Fraction Update**: Solve phase fraction equations
5. **Turbulence Correction**: Update turbulence quantities

### **PISO Algorithm (Transient)**

```cpp
// Main time loop in OpenFOAM
while (runTime.loop())
{
    #include "CourantNo.H"     // Time step control

    // Momentum predictor
    #include "UEqn.H"

    // Pressure-velocity coupling
    for (int corr = 0; corr < nCorr; corr++)
    {
        #include "pEqn.H"
    }

    // Volume fraction correction
    #include "alphaEqns.H"

    // Turbulence equations
    turbulence->correct();

    // Output results
    runTime.write();
}
```

---

## Dimensionless Analysis

### **Key Dimensionless Numbers**

| Number | Definition | Physical Meaning |
|---------|------------|-------------------|
| **Reynolds** | $Re_k = \frac{\rho_k |\mathbf{u}_k| L}{\mu_k}$ | Inertial/viscous forces ratio |
| **Froude** | $Fr_k = \frac{|\mathbf{u}_k|^2}{gL}$ | Inertial/gravity forces ratio |
| **Weber** | $We_k = \frac{\rho_k |\mathbf{u}_k|^2 L}{\sigma}$ | Inertial/surface tension forces ratio |
| **Eötvös** | $Eo = \frac{(\rho_k - \rho_l) g d_p^2}{\sigma}$ | Gravity/surface tension forces ratio |
| **Marangoni** | $Ma = \frac{|\partial \sigma/\partial T| \Delta T L}{\mu \alpha}$ | Thermocapillary/viscous forces ratio |

### **Flow Regime Maps**

**Bubble Flow Regimes:**
| Regime | Condition | Characteristics |
|--------|-----------|-----------------|
| **Bubble flow** | $Eo \gg 1$, $Re < 1$ | Spherical bubbles |
| **Slug flow** | Moderate $Eo$ and $Re$ | Large gas slugs |
| **Churn flow** | $Re \gg 1$, moderate $Eo$ | Unstable flow |
| **Annular flow** | $Re \gg 1$, $\alpha_l \ll 1$ | Liquid film on walls |

---

## Validation and Verification

### **Convergence Criteria**

**Residual-Based Convergence:**
$$R_\phi = \frac{\sum_i |a_P \phi_P - \sum_N a_N \phi_N - S_P|}{\sum_i |a_P \phi_P|} < \epsilon_{tol} \tag{8.1}$$

Typical tolerance: $\epsilon_{tol} = 10^{-6}$

### **Conservation Checks**

- **Mass Balance**: $\sum_{in} \dot{m} - \sum_{out} \dot{m} < \epsilon_m$
- **Momentum Balance**: Check force equilibrium
- **Energy Balance**: Verify energy conservation

### **Test Cases**

| Test Case | Physics | Validation |
|-----------|---------|-------------|
| **Dam Break** | Gravity-driven flow | Interface tracking |
| **Bubble Column** | Drag, lift, turbulent dispersion | Phase distribution |
| **Boiling** | Heat transfer, phase change | Heat flux comparison |

---

## Topic Roadmap

This reference is organized into the following interconnected topics:

1. **[[Foundation and Mathematical Framework]]**: Phase averaging, governing equations, conservation laws
2. **[[Mass Conservation Equations]]**: Continuity equations, mass transfer, volume fraction constraints
3. **[[Momentum Conservation Equations]]**: Phase momentum, interfacial forces, drag models
4. **[[Energy Conservation Equations]]**: Phase energy, heat transfer, enthalpy equations
5. **[[Interfacial Phenomena Equations]]**: Surface tension, Marangoni effects, contact angle dynamics
6. **[[Turbulence Modeling Equations]]**: Mixture turbulence, dispersed phase models
7. **[[Closure Relations]]**: Equations of state, transport properties, mixture models
8. **[[Dimensionless Analysis]]**: Key numbers, flow regimes, similarity criteria
9. **[[Special Cases]]**: Granular flows, compressible multiphase, limiting cases
10. **[[Cross-References]]**: Navigation guide, implementation details, related documentation

---

> [!TIP] **Practical Implementation Guide**
> For successful multiphase simulations in OpenFOAM:
> 1. **Choose appropriate phase models** based on flow physics
> 2. **Ensure numerical stability** through proper time step selection
> 3. **Validate against experimental data** when possible
> 4. **Monitor volume fraction boundedness** throughout simulation
> 5. **Consider computational efficiency** vs. model accuracy trade-offs

The comprehensive coverage of these topics provides both theoretical understanding and practical implementation guidance for multiphase flow modeling in OpenFOAM.