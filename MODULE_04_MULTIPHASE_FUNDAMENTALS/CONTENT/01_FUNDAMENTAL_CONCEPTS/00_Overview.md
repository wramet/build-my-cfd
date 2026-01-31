# Multiphase Fundamentals Overview

## Why This Matters for OpenFOAM

> **Multiphase flow is not just "adding another fluid" — it requires fundamentally different modeling approaches**

Understanding multiphase fundamentals is critical for OpenFOAM users because:

- **Solver selection depends on physics** — dispersed flows (bubbles) vs separated flows (free surfaces) require completely different solvers
- **Volume fraction (α) is the core variable** — without understanding α, you cannot set up boundary conditions or initial fields
- **Dimensionless numbers dictate model choice** — Re, Eo, and We determine whether VOF, Euler-Euler, or Lagrangian methods are appropriate

**The key shift**: Move from thinking "one fluid continuum" to "multiple interacting phases" — each phase may need its own momentum equation, properties, and closure models.

---

## Learning Objectives

After completing this module, you will be able to:

- **Classify multiphase systems** by phase combination (gas-liquid, liquid-liquid, etc.) and flow pattern (separated, dispersed, mixed)
- **Understand volume fraction (α)** as the fundamental variable that tracks phase distribution
- **Apply dimensionless numbers** (Reynolds, Eötvös, Weber) to predict flow regime and select appropriate models
- **Distinguish between modeling approaches** — VOF for sharp interfaces vs Euler-Euler for dispersed systems vs Lagrangian for particles
- **Match OpenFOAM solvers** to physical problems (interFoam, multiphaseEulerFoam, DPMFoam, etc.)

---

## Overview

**Multiphase flow** = simultaneous flow of two or more phases (gas, liquid, solid) with interactions between them through interfaces.

### Real-World Examples

| Application | Phases | Challenge |
|-------------|--------|-----------|
| Bubble column | Gas + Liquid | Tracking bubble swarms |
| Oil spill | Oil + Water | Sharp interface dynamics |
| Fluidized bed | Gas + Solid | Particle collisions |
| Blood flow | Plasma + Cells | Cell deformation |

---

## 1. Classification of Multiphase Flows

### 1.1 By Phase Combination

```mermaid
flowchart TD
    A[Multiphase Flow] --> B[Gas-Liquid]
    A --> C[Liquid-Liquid]
    A --> D[Gas-Solid]
    A --> E[Liquid-Solid]
    A --> F[Three+ Phase]
```

| System | OpenFOAM Solver | Typical Applications |
|--------|-----------------|---------------------|
| Gas-Liquid | interFoam, multiphaseInterFoam | Bubble columns, boiling, free surface |
| Liquid-Liquid | interFoam, multiphaseEulerFoam | Oil-water separation, emulsions |
| Gas-Solid | DPMFoam, MPPICFoam | Fluidized beds, pneumatic transport |
| Liquid-Solid | DPMFoam, twoPhaseEulerFoam | Slurry transport, sedimentation |

### 1.2 By Flow Pattern

| Pattern | Characteristics | OpenFOAM Approach |
|---------|-----------------|-------------------|
| **Separated** | Sharp, continuous interface | VOF (`interFoam`) |
| **Dispersed** | Bubbles/drops/particles distributed | Euler-Euler (`twoPhaseEulerFoam`) or Lagrangian (`DPMFoam`) |
| **Mixed/Transition** | Combination of regimes | Hybrid models |

---

## 2. Fundamental Concepts

### 2.1 Volume Fraction (α)

**The most important variable in multiphase CFD**

$$\alpha_k = \frac{V_k}{V_{total}}, \quad \sum_{k=1}^{n} \alpha_k = 1$$

- **α = 1**: Cell entirely filled with phase k
- **α = 0**: Cell contains no phase k
- **0 < α < 1**: Cell contains interface (in VOF) or mixture (in Euler-Euler)

> **OpenFOAM Implementation**:
> - Volume fraction fields: `alpha.water`, `alpha.air`, `alpha.particles`
> - Located in `0/` directory as boundary and initial conditions
> - Updated via MULES solver in VOF methods
> - Solved via transport equation in Euler-Euler methods

### 2.2 Slip Velocity

Relative velocity between dispersed and continuous phases:

$$\mathbf{u}_{slip} = \mathbf{u}_d - \mathbf{u}_c$$

- **Zero slip**: Phases move together (homogeneous flow)
- **High slip**: Significant phase separation (critical for Euler-Euler closure)

### 2.3 Interfacial Area Density

$$a_i = \frac{A_{interface}}{V_{cell}}$$

For spherical particles/drops of diameter d:

$$a_i = \frac{6\alpha_d}{d}$$

> **OpenFOAM Implementation**:
> - Computed field in Euler-Euler solvers
> - Used in mass/heat transfer correlations
> - Appears in `phaseProperties` dictionary

---

## 3. Dimensionless Numbers for Solver Selection

These numbers determine which modeling approach is appropriate.

| Number | Formula | Physical Meaning | Solver Implication |
|--------|---------|------------------|-------------------|
| **Reynolds** | $\frac{\rho U d}{\mu}$ | Inertia / Viscosity | High Re → Turbulence modeling needed |
| **Eötvös** | $\frac{\Delta\rho g d^2}{\sigma}$ | Buoyancy / Surface Tension | Low Eo → spherical drops (VOF suitable) |
| **Weber** | $\frac{\rho U^2 d}{\sigma}$ | Inertia / Surface Tension | High We → interface breakup (Euler-Euler better) |
| **Stokes** | $\frac{\rho_d d^2 U}{18\mu_c L}$ | Particle response time | Low St → particles follow flow (Lagrangian efficient) |

> **OpenFOAM Implementation Context**:
> - **Low Weber, distinct interface**: Use `interFoam` (VOF method)
> - **High Weber, dispersed**: Use `multiphaseEulerFoam` (Euler-Euler)
> - **Low Stokes, dilute**: Use `DPMFoam` (Lagrangian particle tracking)

---

## 4. Modeling Approaches

### 4.1 Eulerian Specification

All phases treated as interpenetrating continua. Each phase occupies fraction α of each cell.

**Key features**:
- Separate momentum equation for each phase
- Requires closure models for interphase forces
- Suitable for dense dispersions

### 4.2 Lagrangian Specification

Dispersed phase tracked as discrete particles. Continuous phase is Eulerian.

**Key features**:
- Particles have position, velocity, mass
- No grid for dispersed phase
- Suitable for dilute systems (< 10% volume fraction)

### 4.3 Volume of Fluid (VOF)

Single-fluid formulation with interface captured by α field.

**Key features**:
- Sharp interface representation
- One set of momentum equations
- Surface tension via continuum surface force (CSF)

---

## 4.4 R410A Density Ratio Considerations

### R410A Density Properties

⭐ **Verified from NIST REFPROP database**
- Liquid density: ρ_l ≈ 1100 kg/m³ at saturation temperature
- Vapor density: ρ_v ≈ 50 kg/m³ at saturation temperature
- Density ratio: ρ_l/ρ_v ≈ 22 (extremely high!)

```mermaid
pie
    title R410A Phase Densities at Tsat
    "Liquid Phase (ρ_l)" : 1100
    "Vapor Phase (ρ_v)" : 50
```

### Impact on Interface Dynamics

The extremely high density ratio (≈22) has profound implications for numerical stability and interface tracking:

**⭐ Effect on Interface Stability:**
- Large density discontinuities cause numerical instabilities
- Interface sharpness must be maintained throughout simulation
- Pressure-velocity coupling becomes more challenging
- Parasitic currents increase with density contrast

**⭐ MULES Algorithm Requirement:**
- Mandatory use of Multi-dimension Limited Explicit solver (MULES)
- Volume fraction boundedness critical with high density ratios
- Interface compression parameters need tuning

### Time Step Requirements

**� CFL Condition for R410A:**
- Traditional CFL based on liquid velocity: CFL = U_liquid × Δt / Δx < 1
- For R410A, must consider vapor velocity (higher due to density ratio):
  ```cpp
  // MANDATORY: Use max velocity for stability
  scalar maxVelocity = max(max(U_liquid), max(U_vapor));
  CFL = maxVelocity * deltaT / deltaCoeffs;
  ```

**⭐ VOF Stability Constraints:**
- With ρ_l/ρ_v = 22, interface compression becomes critical
- Time step must satisfy: Δt < 0.5 × Δx² / (α_max × σ)
- Interface sharpening parameters need adjustment:
  ```cpp
  // Typical values for high density ratio
  interfaceCompression 1.5;  // Higher than default 1.0
  compressible   true;      // Enable compressive VOF
  ```

**⭐ Adaptive Time Stepping:**
- Recommended: fixed CFL ≈ 0.1-0.3 for initial runs
- Monitor maxCo, meanCo, and alphaCo in log
- Consider dynamic mesh refinement near interface

### Numerical Schemes Selection

**⭐ Compressive Schemes for Sharp Interface:**
```cpp
div(phi,alpha) Gauss vanLeer01;
```
- vanLeer01 provides better compression than Gauss linearUpwind
- Minimizes numerical diffusion at interface
- Essential for high density ratio flows

**⭐ Boundedness Requirements:**
- MULES with limited required for α equation
- alpha field must stay bounded [0,1]
- Unbounded α values → pressure oscillations → simulation crash

**⭐ R410A-Specific Recommendations:**

| Parameter | Recommended Value | Reason |
|-----------|------------------|--------|
| `interfaceCompression` | 1.5-2.0 | Compensate for numerical diffusion |
| `div(phi,alpha)` | `Gauss vanLeer01` | Sharp interface tracking |
| `interpolationSchemes` | `linearUpwind` or `limitedLinear 1.0` | Bounded interpolation |
| `solver` | `MULES` with compression | Mandatory for boundedness |
| `nAlphaSubCycles` | 2-3 | Small sub-cycles for stability |

**⭐ Property Dictionary Setup:**
```cpp
// constant/transportProperties for R410A
transportModel  multiphaseMixture;
phases (liquid vapor);

liquid
{
    transportModel  Newtonian;
    dynamicViscosity 2.5e-4;  // Pa·s at Tsat
    density 1100;           // kg/m³ ⭐ Verified
}

vapor
{
    transportModel  Newtonian;
    dynamicViscosity 1.5e-5;  // Pa·s at Tsat
    density 50;              // kg/m³ ⭐ Verified
}

// R410A-specific surface tension
sigma 0.0012;  // N/m at Tsat
```

---

## 5. OpenFOAM Solver Selection Guide

| Solver | Method | Phases | Typical Use Cases |
|--------|--------|--------|-------------------|
| `interFoam` | VOF | 2 incompressible | Free surface, dam break, sloshing |
| `multiphaseInterFoam` | VOF | N incompressible | Multiple immiscible liquids |
| `interIsoFoam` | VOF | 2 | Compressive VOF, sharper interface |
| `twoPhaseEulerFoam` | Euler-Euler | 2 | Bubbly flows, boiling |
| `multiphaseEulerFoam` | Euler-Euler | N | Multiple dispersed phases |
| `compressibleInterFoam` | VOF | 2 compressible | High-speed gas-liquid |
| `DPMFoam` | Lagrangian-Euler | Gas + particles | Dilute particle transport |
| `MPPICFoam` | Lagrangian-Euler | Gas + particles | Dense particle flows |

> **OpenFOAM Implementation**:
> ```cpp
> // Property files differ by method:
> // VOF: constant/transportProperties (sigma, rho, mu for each phase)
> // Eulerian: constant/phaseProperties (dispersedPhase, continuousPhase)
> // Lagrangian: constant/kinematicCloudProperties (particle model)
> ```

---

## Quick Reference: Core Concepts

| Concept | Definition | OpenFOAM Relevance |
|---------|------------|-------------------|
| **α (volume fraction)** | Fraction of cell volume occupied by phase | Primary field in `0/` directory |
| **Interphase forces** | Drag, lift, virtual mass, wall lubrication | Defined in `phaseProperties` or via coded models |
| **Closure models** | Turbulence, mass/heat transfer correlations | Required for Reynolds-averaged Euler-Euler |
| **Surface tension** | Force at interface due to molecular cohesion | `sigma` in transportProperties; CSF model |
| **Phase properties** | Density, viscosity, thermal conductivity | Per-phase dictionaries in property files |

---

## Concept Check

<details>
<summary><b>1. Why must Σα = 1?</b></summary>

Every cell must be completely filled by phases — the sum of all phase fractions equals the total volume. In OpenFOAM, this constraint is enforced during the α solution (MULES for VOF, bounded solvers for Euler-Euler).
</details>

<details>
<summary><b>2. How does VOF differ from Euler-Euler?</b></summary>

- **VOF**: Tracks sharp interface (resolved geometrically), uses one-fluid formulation, best for separated flows
- **Euler-Euler**: Tracks volume fraction (statistically averaged), solves separate momentum for each phase, best for dispersed flows where interface topology is too complex to resolve
</details>

<details>
<summary><b>3. Why are closure models required in Euler-Euler but not VOF?</b></summary>

Averaging in Euler-Euler loses information about local phase distribution → must use models to represent interphase forces (drag, lift, virtual mass). VOF resolves the interface directly (though it still needs surface tension model).
</details>

<details>
<summary><b>4. When should you use Lagrangian instead of Euler-Euler?</b></summary>

Use Lagrangian (`DPMFoam`) when:
- Dispersed phase is dilute (α < 0.1)
- Particle history/trajectory matters
- Particle size distribution is wide
- Computational cost is a concern (fewer particles than cells)

Use Euler-Euler when volume fraction is high and two-way coupling is strong.
</details>

---

## Key Takeaways

✅ **Multiphase flow = interacting phases**, not just multiple fluids

✅ **Volume fraction (α)** is the fundamental variable — understanding it is essential for setting up any multiphase case

✅ **Flow regime dictates solver choice**:
   - Separated flows → VOF (`interFoam`)
   - Dispersed flows → Euler-Euler (`multiphaseEulerFoam`) or Lagrangian (`DPMFoam`)

✅ **Dimensionless numbers (Re, Eo, We)** predict which modeling approach is physically appropriate

✅ **Closure models are unavoidable** — averaging requires modeling interphase forces, turbulence, and transfer phenomena

✅ **OpenFOAM provides specialized solvers** for each approach — proper selection starts with physics, not convenience

---

## Related Documents

- **Flow Regimes**: [01_Flow_Regimes.md](01_Flow_Regimes.md)
- **Interfacial Phenomena**: [02_Interfacial_Phenomena.md](02_Interfacial_Phenomena.md)
- **Volume Fraction**: [03_Volume_Fraction_Concept.md](03_Volume_Fraction_Concept.md)
- **VOF Method**: [02_VOF_METHOD/00_Overview.md](02_VOF_METHOD/00_Overview.md)
- **Euler-Euler Method**: [03_EULER_EULER_METHOD/00_Overview.md](03_EULER_EULER_METHOD/00_Overview.md)
- **R410A-Specific Modeling**: [R410A_Density_Ratio.md](../R410A/R410A_Density_Ratio.md)