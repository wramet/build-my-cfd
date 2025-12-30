# Non-Newtonian Fluids - Overview

ภาพรวม Non-Newtonian Fluids

---

## 🎯 Learning Objectives

By the end of this module, you will be able to:

1. **Explain** the fundamental differences between Newtonian and non-Newtonian fluid behavior
2. **Identify** common non-Newtonian flow applications in engineering and nature
3. **Select** appropriate viscosity models for different flow scenarios
4. **Configure** non-Newtonian transport properties in OpenFOAM
5. **Navigate** the complete non-Newtonian workflow from model selection to simulation

---

## 1. The 3W Framework

### What are Non-Newtonian Fluids?

**Non-Newtonian fluids** are materials whose viscosity depends on the local shear rate, unlike Newtonian fluids (water, air) which maintain constant viscosity.

**Key characteristic:**
```
η = f(γ̇)  ← Viscosity varies with shear rate
```

**Real-world examples:**
- **Shear-thinning:** Blood, ketchup, paint, polymer solutions
- **Shear-thickening:** Cornstarch suspension, body armor fluids
- **Yield stress:** Toothpaste, mayonnaise, drilling mud, concrete

### Why Do They Matter for CFD?

**Engineering importance:**

| Application | Why Non-Newtonian Matters |
|-------------|---------------------------|
| **Biomedical** | Blood flow in arteries, veins, and medical devices |
| **Food Processing** | Mixing, pumping, and extrusion of viscous foods |
| **Oil & Gas** | Drilling muds, cementing, enhanced oil recovery |
| **Polymers** | Injection molding, extrusion, fiber spinning |
| **Coatings** | Spray painting, roll coating, dip coating |

**Modeling challenges:**
- Viscosity varies throughout the domain (nonlinear coupling)
- Sharp viscosity gradients affect convergence
- Apparent viscosity can change by orders of magnitude
- Temperature effects often coupled with rheology

### How Does OpenFOAM Implement Them?

**Architecture:**
```
transportModel (user selects)
    ↓
viscosityModel class (calculates η)
    ↓
momentum equation (uses η)
```

**Implementation layers:**

1. **Transport properties** (`constant/transportProperties`)
   - Select rheology model
   - Define model coefficients

2. **Viscosity classes** (`src/transportModels`)
   - Calculate apparent viscosity
   - Handle strain rate computation

3. **Solver integration**
   - Standard solvers (simpleFoam, pimpleFoam)
   - Specialized solvers (viscoelasticFluidFoam)

---

## 2. Newtonian vs Non-Newtonian Behavior

| **Property** | **Newtonian** | **Non-Newtonian** |
|--------------|---------------|-------------------|
| **Viscosity** | Constant | Variable with γ̇ |
| **Flow curve** | Linear τ-γ̇ | Nonlinear τ-γ̇ |
| **Examples** | Water, air, oils | Blood, paint, ketchup |
| **Model** | Single constant μ | Function η(γ̇) |
| **Complexity** | Low | Moderate to high |

**Visual comparison:**
```
Newtonian:           Non-Newtonian:
τ                     τ
│                   ╱
│                  ╱  (shear-thinning)
│                 ╱
│                ╱_____________ γ̇
│                ╲
│                 ╲  (shear-thickening)
│                  ╲
└─────────────────── γ̇
```

---

## 3. Model Selection Guide

### Quick Reference Table

| **Model** | **Best For** | **Key Parameters** | **Limitations** |
|-----------|--------------|-------------------|-----------------|
| **Power Law** | Simple shear-thinning/thickening | k (consistency), n (power index) | No zero-shear plateau |
| **Cross** | Polymer solutions, moderate shear | ν₀, ν∞, m, n | Limited range |
| **Carreau** | Wide shear rate range | ν₀, ν∞, λ, n | More parameters |
| **Bingham** | Yield stress materials | νₚ, τy | Discontinuity at yield |
| **Herschel-Bulkley** | Complex yield stress | k, n, τy | Numerical difficulty |

### Selection Flowchart

```
Start
  ↓
Does it have yield stress?
  ├─ Yes → Herschel-Bulkley (or Bingham if simple)
  └─ No → Shear-thinning or thickening?
       ├─ Thin → Wide shear range?
       │        ├─ Yes → Carreau
       │        └─ No → Cross or Power Law
       └─ Thick → Power Law (n > 1)
```

---

## 4. OpenFOAM Workflow

### Step 1: Select Solver

| **Solver** | **When to Use** |
|------------|-----------------|
| **simpleFoam** | Steady-state, incompressible |
| **pimpleFoam** | Transient, incompressible |
| **viscoelasticFluidFoam** | Viscoelastic fluids |
| **nonNewtonianIcoFoam** | Simple transient (legacy) |

### Step 2: Configure Transport Properties

```cpp
// constant/transportProperties
transportModel  CrossPowerLaw;

CrossPowerLawCoeffs
{
    // Zero-shear viscosity [m²/s]
    nu0         0.01;
    
    // Infinite-shear viscosity [m²/s]
    nuInf       0.0001;
    
    // Time constant [s]
    m           0.1;
    
    // Power law index [-]
    n           0.5;
    
    // Viscosity equation bounds
    nuMin       0.00001;
    nuMax       0.1;
}
```

### Step 3: Adjust Numerical Schemes

```cpp
// system/fvSchemes
gradSchemes
{
    default Gauss linear;
}

divSchemes
{
    div(phi,U) Gauss upwind;  // Use upwind for stability
}

laplacianSchemes
{
    laplacian(nu,U) Gauss linear corrected;
}
```

### Step 4: Monitor Convergence

**Key variables to check:**
- `U` (velocity) - should converge smoothly
- `p` (pressure) - sensitive to viscosity changes
- `nu` (viscosity) - check bounds are respected

---

## 5. Module Roadmap

This module provides comprehensive coverage of non-Newtonian fluid simulation:

| **File** | **Content Focus** | **Key Topics** |
|----------|-------------------|----------------|
| **02_Viscosity_Models** | Deep theory | Model derivations, parameter estimation, validation |
| **03_OpenFOAM_Architecture** | Implementation | Class structure, code organization, customization |
| **04_Numerical_Implementation** | Numerical methods | Stability, convergence, discretization |
| **05_Practical_Guide** | Hands-on workflow | Case setup, debugging, best practices |

**Recommended learning path:**
1. Start here (00) for big picture
2. Study models in detail (02)
3. Understand implementation (03)
4. Master numerics (04)
5. Apply to real cases (05)

---

## 📊 Quick Reference: Parameter Interpretation

| **Parameter** | **Physical Meaning** | **Implication** |
|---------------|---------------------|-----------------|
| **n < 1** | Shear-thinning | Viscosity decreases with shear rate |
| **n > 1** | Shear-thickening | Viscosity increases with shear rate |
| **n = 1** | Newtonian | Constant viscosity (power law) |
| **τy > 0** | Yield stress | No flow below threshold stress |
| **ν₀** | Zero-shear viscosity | Viscosity at γ̇ → 0 |
| **ν∞** | Infinite-shear viscosity | Viscosity at γ̇ → ∞ |
| **λ** | Characteristic time | Transition shear rate ~ 1/λ |

**Typical ranges:**
- Blood: n ≈ 0.6-0.8 (moderate shear-thinning)
- Paint: n ≈ 0.3-0.5 (strong shear-thinning)
- Drilling mud: τy ≈ 5-50 Pa (yield stress)
- Polymer melts: λ ≈ 0.1-10 s (viscoelastic)

---

## 🧠 Concept Check

<details>
<summary><b>1. Is blood a non-Newtonian fluid?</b></summary>

**Yes** - Blood exhibits shear-thinning behavior (n ≈ 0.6-0.8). At low shear rates (in veins), viscosity is higher. At high shear rates (in arteries), viscosity decreases, improving flow.

**Clinical relevance:** This behavior aids in circulation and affects blood pressure measurements.
</details>

<details>
<summary><b>2. What does n = 1 mean in the Power Law model?</b></summary>

**Newtonian behavior** - When n = 1, the Power Law reduces to constant viscosity (η = k). This is the mathematical bridge between non-Newtonian and Newtonian models.

**Practical note:** If your data suggests n ≈ 1, consider using Newtonian model for simplicity.
</details>

<details>
<summary><b>3. What is yield stress and why is it important?</b></summary>

**Yield stress (τy)** is the minimum shear stress required to initiate flow. Below τy, the material behaves like a solid. Above τy, it flows like a fluid.

**Applications:**
- **Toothpaste:** Stays on brush until squeezed (τ > τy)
- **Drilling mud:** Suspends cuttings when not pumping
- **Concrete:** Flows when vibrated but holds shape when static

**Modeling challenge:** Numerical discontinuity at τy requires special treatment in OpenFOAM (regularized models).
</details>

<details>
<summary><b>4. When should I use Cross vs. Carreau model?</b></summary>

**Use Cross model when:**
- You have moderate shear rate range
- You need simple 4-parameter model
- Data shows clear zero-shear plateau

**Use Carreau model when:**
- You have wide shear rate range (decades)
- You need smoother transition
- You want better fit at intermediate shear rates

**Decision:** Fit both to your data and compare R² values.
</details>

---

## 📚 Key Takeaways

### Core Concepts

1. **Non-Newtonian fluids** have viscosity that depends on shear rate (η = f(γ̇))
2. **Three main categories**: shear-thinning, shear-thickening, yield stress
3. **Model selection** depends on fluid type, shear rate range, and application
4. **OpenFOAM implementation** is modular: transportModel → viscosityModel → solver

### Practical Guidelines

1. **Always validate** your rheology model against experimental data
2. **Start simple** - Power Law before complex models like Carreau
3. **Monitor viscosity bounds** to prevent numerical instability
4. **Use appropriate solvers** - simpleFoam for steady, pimpleFoam for transient
5. **Check convergence** - variable viscosity can cause solver issues

### Common Pitfalls

| **Pitfall** | **Consequence** | **Solution** |
|-------------|-----------------|--------------|
| Wrong model choice | Poor predictions | Validate with experimental data |
| Unbounded viscosity | Solver divergence | Set νMin/νMax in transportProperties |
| Inadequate mesh | Wrong shear rates | Mesh refinement near walls |
| Poor initial guess | Slow convergence | Start from Newtonian solution |

### Next Steps

- **Deep dive into models:** See [02_Viscosity_Models.md](02_Viscosity_Models.md) for mathematical derivations
- **Understand implementation:** See [03_OpenFOAM_Architecture.md](03_OpenFOAM_Architecture.md) for code structure
- **Master numerics:** See [04_Numerical_Implementation.md](04_Numerical_Implementation.md) for stability analysis

---

## 📖 Cross-References

### Within This Module

- **Viscosity Models:** [02_Viscosity_Models.md](02_Viscosity_Models.md) - Model equations and derivations
- **Architecture:** [03_OpenFOAM_Architecture.md](03_OpenFOAM_Architecture.md) - Implementation details
- **Numerical Methods:** [04_Numerical_Implementation.md](04_Numerical_Implementation.md) - Stability and convergence
- **Practical Guide:** [05_Practical_Guide.md](05_Practical_Guide.md) - Workflow and best practices

### Related Modules

- **Single-Phase Fundamentals:** See `MODULE_03_SINGLE_PHASE_FLOW` for governing equations
- **Multiphase Flows:** See `MODULE_04_MULTIPHASE_FUNDAMENTALS` for dispersed non-Newtonian flows
- **OpenFOAM Programming:** See `MODULE_05_OPENFOAM_PROGRAMMING` for custom model development

---

*Last Updated: 2025-12-31*