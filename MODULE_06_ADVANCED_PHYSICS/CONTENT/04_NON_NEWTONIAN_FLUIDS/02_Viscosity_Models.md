# Viscosity Models

**Non-Newtonian Viscosity Models**

---

## 📋 Learning Objectives

By the end of this section, you will be able to:

1. **WHAT**: Distinguish between different viscosity model formulations and understand what physical phenomena each represents
2. **WHEN**: Select appropriate viscosity models for specific non-Newtonian fluids and flow conditions using a systematic decision framework
3. **HOW**: Configure model parameters in OpenFOAM and understand how parameter choices affect numerical stability and physical accuracy
4. **ANALYZE**: Predict how changes in model parameters influence viscosity behavior across shear rate ranges
5. **IMPLEMENT**: Translate theoretical models into OpenFOAM transportProperties dictionaries

---

## Overview

Viscosity models provide the mathematical framework for describing **shear-rate dependent viscosity** in non-Newtonian fluids. Unlike Newtonian fluids where viscosity is constant, non-Newtonian fluids exhibit complex viscosity relationships that depend on:

- **Shear rate** (γ̇): The rate of deformation in the fluid
- **Stress history**: Time-dependent effects in some materials
- **Material structure**: Microstructural changes under flow

This section provides a **comprehensive model reference** organized using the **3W Framework**:
- **WHAT**: Physical representation and mathematical formulation
- **WHEN**: Application domains and selection criteria  
- **HOW**: Parameter implementation and sensitivity considerations

**Cross-reference**: See [01_Non_Newtonian_Fundamentals.md](01_Non_Newtonian_Fundamentals.md) for theoretical derivation of constitutive equations and [04_Numerical_Implementation.md](04_Numerical_Implementation.md) for discretization strategies.

---

## 🎯 Model Selection Flowchart

```
START
  │
  ├─ Does fluid exhibit yield stress?
  │   ├─ YES → Bingham Plastic (simple) or Herschel-Bulkley (complex)
  │   └─ NO  → Continue
  │
  ├─ Does viscosity plateau at low AND high shear rates?
  │   ├─ YES → Cross Model or Carreau Model
  │   └─ NO  → Continue
  │
  ├─ Is simple power-law relationship sufficient?
  │   ├─ YES → Power Law Model
  │   └─ NO  → Consider more sophisticated models
  │
  └─ Check Material Reference Table below
```

**Key decision points**:
1. **Yield stress presence**: Most critical differentiator
2. **Shear rate range**: Low vs. high shear behavior matters
3. **Parameter availability**: Experimental data limits model choice
4. **Computational cost**: Simpler models converge faster

---

## 1. Power Law Model

### WHAT: Physical Representation

The **Power Law model** (Ostwald-de Waele relationship) describes viscosity as a simple power function of shear rate. It captures the most common non-Newtonian behaviors:

**Mathematical Formulation**:
```
η = k · γ̇^(n-1)

where:
  η  = apparent viscosity [Pa·s]
  k  = consistency index [Pa·s^n]  
  γ̇ = shear rate [s⁻¹]
  n  = power law index [-]
```

**Behavior Regimes**:
- **n < 1**: Shear-thinning (pseudoplastic) — viscosity decreases with shear
  - *Examples*: Blood, polymer solutions, paint
- **n = 1**: Newtonian fluid — constant viscosity
- **n > 1**: Shear-thickening (dilatant) — viscosity increases with shear
  - *Examples*: Cornstarch suspensions, some colloids

### WHEN: Application Domain

**Best for**:
- Simple shear-thinning/thickening fluids over limited shear rate ranges
- Materials lacking pronounced low/high shear plateaus
- Preliminary analysis and rapid prototyping

**Limitations**:
- **No infinite-shear limit** → viscosity → 0 or ∞ as γ̇ → ∞ (unphysical)
- **No zero-shear limit** → viscosity → 0 or ∞ as γ̇ → 0 (unphysical)
- **Fails** for wide shear rate ranges with Newtonian plateaus

**Typical Applications**:
- Polymer melts in processing equipment
- Food products (ketchup, chocolate)
- Pharmaceutical suspensions

### HOW: Parameter Implementation & Sensitivity

**OpenFOAM Configuration**:
```cpp
// constant/transportProperties
transportModel  powerLaw;
powerLawCoeffs
{
    nuMax   1e-3;    // Maximum viscosity limit [m²/s]
    nuMin   1e-6;    // Minimum viscosity limit [m²/s]  
    k       0.01;    // Consistency index
    n       0.5;     // Power law index (< 1 for shear-thinning)
}
```

**Parameter Sensitivity**:

| Parameter | Effect on η | Physical Meaning | Typical Range |
|-----------|-------------|------------------|---------------|
| **k** | Scales η uniformly | Fluid "thickness" at γ̇ = 1 s⁻¹ | 0.001 - 100 Pa·sⁿ |
| **n** | Controls shear dependence | Degree of non-Newtonian behavior | 0.2 - 1.8 |

**Numerical Stability Guidelines**:
- **nuMax/nuMin**: Critical for preventing unrealistic viscosity values
  - Set nuMax: 10-100× expected maximum viscosity
  - Set nuMin: 0.01-0.1× expected minimum viscosity
- **n < 0.3**: Extreme shear-thinning may cause convergence issues
- **n > 1.5**: Extreme shear-thickening may require under-relaxation

---

## 2. Cross Model

### WHAT: Physical Representation

The **Cross model** extends the power law by incorporating **asymptotic Newtonian plateaus** at both low and high shear rates, providing more physically realistic behavior across wide shear rate ranges.

**Mathematical Formulation**:
```
η = η∞ + (η₀ - η∞) / [1 + (m · γ̇)^n]

where:
  η₀  = zero-shear viscosity [Pa·s]      (low shear plateau)
  η∞  = infinite-shear viscosity [Pa·s]  (high shear plateau)
  m   = time constant [s]                (transition sharpness)
  n   = power index [-]                  (transition slope)
```

**Physical Interpretation**:
- **η₀**: Viscosity when fluid is at rest or very slow deformation
- **η∞**: Viscosity under rapid deformation (molecular alignment)
- **m**: Characteristic time scale for structural breakdown
- **Transition region**: γ̇ ≈ 1/m marks the onset of shear-thinning

### WHEN: Application Domain

**Best for**:
- Polymer solutions and melts with clear Newtonian plateaus
- Biological fluids (blood, synovial fluid)
- Surfactant systems and microemulsions

**Advantages over Power Law**:
- ✓ **Proper limits** at γ̇ → 0 and γ̇ → ∞
- ✓ **Physically realistic** across 3+ decades of shear rate
- ✓ **Four parameters** enable better experimental fitting

**Limitations**:
- Requires accurate measurement of η₀ and η∞
- More computationally expensive than power law
- May overfit limited experimental data

### HOW: Parameter Implementation & Sensitivity

**OpenFOAM Configuration**:
```cpp
transportModel  CrossPowerLaw;
CrossPowerLawCoeffs
{
    nu0     0.01;    // Zero-shear viscosity [m²/s]
    nuInf   0.0001;  // Infinite-shear viscosity [m²/s]
    m       0.1;     // Time constant [s]
    n       0.5;     // Power index
}
```

**Parameter Sensitivity**:

| Parameter | Effect on Viscosity Curve | Physical Meaning |
|-----------|---------------------------|------------------|
| **η₀** | Raises entire curve | Resting fluid structure |
| **η∞** | Lowers high-shear plateau | Fully aligned structure |
| **m** | Shifts transition left/right | Relaxation time scale |
| **n** | Controls transition steepness | Kinetics of breakdown |

**Practical Fitting Guidelines**:
1. **Measure η₀** at γ̇ < 0.01 s⁻¹ (rotational rheometry)
2. **Measure η∞** at γ̇ > 1000 s⁻¹ (capillary rheometry)
3. **Estimate m** from crossover point: γ̇_crossover ≈ 1/m
4. **Fit n** to transition region slope

**Numerical Considerations**:
- **η₀/η∞ ratio**: Ratios > 1000 may cause stiffness
- **m · γ̇**: Very large values (> 10⁶) can cause overflow → use viscosity limits

---

## 3. Carreau Model

### WHAT: Physical Representation

The **Carreau model** is another **five-parameter generalized Newtonian model** similar to Cross but with a different mathematical form that better represents certain polymer fluids.

**Mathematical Formulation**:
```
η = η∞ + (η₀ - η∞) · [1 + (λ · γ̇)²]^((n-1)/2)

where:
  η₀  = zero-shear viscosity [Pa·s]
  η∞  = infinite-shear viscosity [Pa·s]  
  λ   = relaxation time [s]           (inverse of critical shear rate)
  n   = power law index [-]
```

**Comparison with Cross Model**:
- Carreau uses **(λ · γ̇)²** instead of **(m · γ̇)** → smoother transition
- Carreau exponent: **(n-1)/2** vs Cross exponent: **n**
- Both approach Power Law at intermediate shear rates

### WHEN: Application Domain

**Best for**:
- **Blood and biological fluids**: Most widely used model in hemodynamics
- **Polymer melts**: Especially polyolefins and styrenics
- **Fiber suspensions**: Where smooth transition is critical

**Carreau vs Cross**:
| Aspect | Carreau | Cross |
|--------|---------|-------|
| Transition shape | Smoother | Sharper |
| Hemodynamics | Preferred | Less common |
| Polymer melts | Both used | Both used |
| Fitting ease | Slightly harder | Slightly easier |

### HOW: Parameter Implementation & Sensitivity

**OpenFOAM Configuration**:
```cpp
transportModel  Carreau;
CarreauCoeffs
{
    nu0     0.01;    // Zero-shear viscosity [m²/s]
    nuInf   0.0001;  // Infinite-shear viscosity [m²/s]
    lambda  0.1;     // Relaxation time [s]
    n       0.5;     // Power law index
}
```

**Parameter Sensitivity**:

| Parameter | Physical Role | Range Effect |
|-----------|---------------|--------------|
| **λ (lambda)** | Inverse critical shear rate (1/γ̇_c) | Smaller λ → transition at higher γ̇ |
| **n** | Shear-thinning intensity | Lower n → stronger thinning |

**Critical Shear Rate**:
```
γ̇_critical = 1/λ

At γ̇ = γ̇_critical: Viscosity is midway between η₀ and η∞
```

**Blood-Specific Values** (typical at 37°C):
- η₀ = 0.056 Pa·s (56 cP)
- η∞ = 0.0035 Pa·s (3.5 cP)  
- λ = 3.313 s
- n = 0.3568

**Cross-reference**: See [03_Reacting_Flows/06_Practical_Workflow.md](../../03_REACTING_FLOWS/06_Practical_Workflow.md) for blood rheology in cardiovascular simulations.

---

## 4. Bingham Plastic Model

### WHAT: Physical Representation

The **Bingham plastic model** describes materials that behave as **elastic solids** below a critical stress and **Newtonian fluids** above it. This is the simplest yield stress model.

**Mathematical Formulation**:
```
If τ > τy:
  τ = τy + η_p · γ̇
  ⇒ η = τy/γ̇ + η_p

If τ ≤ τy:
  γ̇ = 0  (no flow)
  ⇒ η → ∞ (effectively rigid)

where:
  τy = yield stress [Pa]           (minimum stress to initiate flow)
  η_p = plastic viscosity [Pa·s]   (viscosity after yielding)
```

**Physical Interpretation**:
- **Yield stress (τy)**: Represents material strength of microstructure
  - Particle networks (cement paste)
  - Colloidal gels (mayonnaise)
  - Emulsion droplets (paint)
- **Plastic viscosity (η_p)**: Viscosity of flowing material after structure breaks

### WHEN: Application Domain

**Best for**:
- **Cement and concrete**: Fresh concrete, grouts, mortars
- **Food products**: Mayonnaise, ketchup, tomato paste
- **Drilling muds**: Borehole fluids in oil/gas industry
- **Simple yield stress fluids**: Where post-yield behavior is Newtonian

**Limitations**:
- ✗ **No shear-thinning** after yield (many real fluids shear-thin)
- ✗ **Abrupt transition** at τy (real materials have gradual yielding)
- ✗ **Discontinuous derivative** at yield point can cause numerical issues

**When to use instead**:
- Use **Herschel-Bulkley** if post-yield shear-thinning is significant
- Use **Papanastasiou regularisation** for numerical stability (see Section 4.3)

### HOW: Parameter Implementation & Sensitivity

**OpenFOAM Configuration**:
```cpp
transportModel  BinghamPlastic;
BinghamPlasticCoeffs
{
    tauY    10;      // Yield stress [Pa]
    etaP    0.01;    // Plastic viscosity [Pa·s]
    nuMax   1e-3;    // Maximum viscosity cap [m²/s]
}
```

**Parameter Sensitivity**:

| Parameter | Physical Effect | Typical Range |
|-----------|----------------|---------------|
| **τy** | Threshold stress to initiate flow | 1 - 1000 Pa |
| **η_p** | Flow resistance after yielding | 0.001 - 10 Pa·s |

**Numerical Challenges**:

1. **Discontinuity at τ = τy**:
   - Apparent viscosity → ∞ as γ̇ → 0
   - **Solution**: Regularisation (Papanastasiou, Bercovier-Engelman)

2. **Yield surface tracking**:
   - Need to accurately locate where τ = τy
   - **Solution**: Small time steps, fine mesh near walls

3. **Plug flow regions**:
   - Unyielded core moves as solid body
   - **Solution**: Ensure mesh resolves yield surface

**Papanastasiou Regularisation** (recommended for OpenFOAM):
```cpp
// Regularised Bingham (OpenFOAM default approach)
η_reg = η_p + τy/γ̇ · [1 - exp(-m·γ̇)]

where m = regularisation parameter (typically 100-1000 s)
```

**Cross-reference**: See [04_Numerical_Implementation.md](04_Numerical_Implementation.md) for yield stress algorithms and [02_Coupled_Physics/02_Conjugate_Heat_Transfer.md](../../02_COUPLED_PHYSICS/02_Conjugate_Heat_Transfer.md) for solidification modeling with yield stress.

---

## 5. Herschel-Bulkley Model

### WHAT: Physical Representation

The **Herschel-Bulkley model** combines **yield stress behavior** (from Bingham) with **power law shear-thinning/thickening** (from Power Law). It is the most versatile generalized Newtonian model.

**Mathematical Formulation**:
```
If τ > τy:
  τ = τy + k · γ̇^n
  ⇒ η = τy/γ̇ + k · γ̇^(n-1)

If τ ≤ τy:
  γ̇ = 0 (no flow)

where:
  τy = yield stress [Pa]
  k  = consistency index [Pa·s^n]
  n  = power law index [-]
```

**Relationship to Other Models**:
```
Herschel-Bulkley General Form:
  τ = τy + k · γ̇^n

Special Cases:
├─ τy = 0, n = 1  → Newtonian (η = k)
├─ τy = 0, n ≠ 1  → Power Law  
├─ τy > 0, n = 1  → Bingham Plastic
└─ τy > 0, n < 1  → True Herschel-Bulkley (yield + shear-thinning)
```

### WHEN: Application Domain

**Best for**:
- **Paints and coatings**: Yield stress prevents sagging, shear-thinning aids spraying
- **Foams and emulsions**: Complex yielding + thinning behavior
- **Mining slurries**: Mineral suspensions with yield stress
- **Food gels**: Yield stress + shear-thinning (yogurt, purees)

**Advantages**:
- ✓ Most realistic for many industrial materials
- ✓ Captures both yielding AND post-yield rheology
- ✓ Three parameters provide good experimental fitting

**Challenges**:
- ✗ **Four-parameter fit** (τy, k, n) requires extensive rheometry
- ✗ **Computationally expensive** due to conditional behavior
- ✗ **Parameter correlation**: τy and k can be correlated in fitting

### HOW: Parameter Implementation & Sensitivity

**OpenFOAM Configuration**:
```cpp
transportModel  HerschelBulkley;
HerschelBulkleyCoeffs
{
    tauY    10;      // Yield stress [Pa]
    k       0.5;     // Consistency index [Pa·s^n]
    n       0.5;     // Power law index
    nuMin   1e-6;    // Minimum viscosity [m²/s]
    nuMax   1e-3;    // Maximum viscosity [m²/s]
}
```

**Parameter Sensitivity**:

| Parameter | Physical Effect | Impact on Flow |
|-----------|----------------|----------------|
| **τy** | Increases unyielded plug size | Larger plug regions, higher pressure gradients |
| **k** | Increases overall viscosity magnitude | Higher viscous dissipation |
| **n** | Controls post-yield shear dependence | n < 1: velocity profile flattening in sheared regions |

**Parameter Correlation**:
```
High τy + Low n  → Similar flow to Low τy + High k

Experimental fitting strategy:
1. Measure τy independently (stress ramp test)
2. Fix τy, fit k and n from flow curve
```

**Practical Application Examples**:

| Material | τy (Pa) | k (Pa·sⁿ) | n |
|----------|---------|-----------|---|
| Latex paint | 5-20 | 1-5 | 0.3-0.6 |
| Cement paste | 50-500 | 0.1-10 | 0.3-0.7 |
| Drilling mud | 10-100 | 0.5-5 | 0.4-0.8 |

**Numerical Stability Tips**:
1. **Viscosity limits critical**: Set nuMax = 10³-10⁴ × η_p to prevent explosion near τy
2. **Yield surface resolution**: Refine mesh near walls and anticipated yield surfaces
3. **Regularisation**: Use Papanastasiou for convergence:
   ```cpp
   m 500; // Regularisation parameter in transportProperties
   ```

---

## 6. Model Comparison Summary

### Comprehensive Comparison Table

| Model | Parameters | Physical Features | Computational Cost | Key Advantages | Main Limitations |
|-------|------------|-------------------|-------------------|----------------|------------------|
| **Power Law** | 2 (k, n) | Shear-thinning/thickening | Low | Simple, fast, widely applicable | No yield stress, unphysical limits |
| **Cross** | 4 (η₀, η∞, m, n) | Plateaus + thinning | Medium | Realistic across wide shear range | Requires more data |
| **Carreau** | 4 (η₀, η∞, λ, n) | Plateaus + thinning | Medium | Best for blood, smooth transition | Slightly harder to fit |
| **Bingham** | 2 (τy, η_p) | Yield stress | Medium-High | Simple yield behavior | No post-yield thinning |
| **Herschel-Bulkley** | 3 (τy, k, n) | Yield + thinning | High | Most versatile | Complex parameter fitting |

### Material-to-Model Mapping

**Quick Reference Guide**:

| Material Class | Recommended Model | Alternative | Rationale |
|----------------|-------------------|-------------|-----------|
| **Polymer solutions** | Cross | Carreau | Clear low/high shear plateaus |
| **Polymer melts** | Carreau | Cross | Smooth transition, industry standard |
| **Blood** | Carreau | Cross | Extensive validation in hemodynamics |
| **Paint** | Herschel-Bulkley | Bingham | Yield stress + shear-thinning |
| **Toothpaste** | Bingham | Herschel-Bulkley | Simple yield behavior sufficient |
| **Cement paste** | Bingham | Herschel-Bulkley | Post-yield often Newtonian |
| **Drilling muds** | Herschel-Bulkley | Bingham | Often shear-thinning after yield |
| **Food gels (yogurt)** | Herschel-Bulkley | Carreau | Yield + thinning + plateau |
| **Suspensions (high conc.)** | Herschel-Bulkley | Power Law | Yield stress common |
| **Simple shear-thinning fluids** | Power Law | - | Limited parameter data available |

### Decision Tree (Expanded)

```
                      START
                        │
            ┌───────────┴───────────┐
            │ Does material have   │
            │ measurable YIELD STRESS?
            └───────────┬───────────┘
               YES              │ NO
                │               │
        ┌───────┴───────┐   ┌───┴────────────────┐
        │ Post-yield    │   │ Wide shear rate    │
        │ behavior      │   │ range (>2 decades)? │
        │ Newtonian?    │   └───┬────────────────┘
        └───────┬───────┘   YES          NO
      YES           NO          │            │
       │             │    ┌────┴─────┐      │
       │             │    │ Plateaus │      │
  BINGHAM    Herschel- │ present?  │  POWER LAW
              Bulkley  └────┬─────┘
                        YES          NO
                         │            │
                    CARREAU      POWER LAW
                   or CROSS    (limited range)
                        │
                Biological fluids?
                    YES    NO
                     │      │
                 CARREAU   CROSS
```

---

## 7. Parameter Sensitivity Analysis

### General Sensitivity Principles

**All models follow these sensitivity rules**:

1. **Viscosity magnitude parameters** (k, η₀, η_p): Scale pressure drop proportionally
   - 2× increase → ~2× increase in pressure drop (Newtonian limit)

2. **Shear-dependence parameters** (n, m, λ): Control viscosity gradient
   - More sensitive at **intermediate shear rates**
   - Less sensitive near plateaus

3. **Yield stress** (τy): Creates step-change in behavior
   - Small τy changes → Large changes in plug region size
   - Most sensitive parameter near yield point

### Power Law Sensitivity

**Shear rate where viscosity changes most rapidly**:
```
γ̇_critical = [1/(k(n-1))]^(1/(n-1))

Example: k=0.01, n=0.5
γ̇_critical = [1/(0.01×-0.5)]^(-2) = 100 s⁻¹
```

**Practical implication**: 
- Ensure experimental data covers γ̇_critical
- Numerical issues if shear rates span < 0.1× to > 10× γ̇_critical

### Cross/Carreau Sensitivity

**Transition sharpness** controlled by:
- **Cross**: Parameter `n` (larger n = sharper transition)
- **Carreau**: Parameter `n` (smaller n = sharper transition)

**η₀/η∞ ratio effects**:
```
Ratio < 10:    Nearly Newtonian (weak non-linearity)
Ratio ~ 100:   Moderate non-Newtonian effects
Ratio > 1000:  Strong non-Newtonian, may need under-relaxation
```

### Yield Stress Model Sensitivity

**Bingham number (Bn)** - dimensionless yield stress:
```
Bn = τy · L / (η_p · V)

where:
  L = characteristic length [m]
  V = characteristic velocity [m/s]
```

**Flow regime correlation**:
```
Bn < 0.1:   Yield stress negligible (nearly Newtonian)
Bn ~ 1:     Transition regime (yield + viscous both important)
Bn > 10:    Plug flow dominant (yield stress controls)
```

**Herschel-Bulkley additional sensitivity**:
- **n < 0.5**: Extreme shear-thinning → potential convergence issues
- **n > 1**: Shear-thickening after yield → rare, difficult to converge

---

## 8. Cross-References to Related Content

### Within This Module

- **[01_Non_Newtonian_Fundamentals.md](01_Non_Newtonian_Fundamentals.md)**: Theoretical derivation of constitutive equations, stress tensor formulation
- **[03_OpenFOAM_Architecture.md](03_OpenFOAM_Architecture.md)**: Runtime selection mechanism for viscosity models
- **[04_Numerical_Implementation.md](04_Numerical_Implementation.md)**: 
  - Discretization of viscous terms
  - Yield stress algorithms and regularisation
  - Under-relaxation strategies for highly non-linear models

### Across Modules

- **[02_Coupled_Physics/04_Object_Registry_Architecture.md](../../02_COUPLED_PHYSICS/04_Object_Registry_Architecture.md)**: How transportProperties dictionary is loaded and accessed
- **[03_Single_Phase_Flow/02_Pressure_Velocity_Coupling/04_Underrelaxation_Practices.md](../../03_SINGLE_PHASE_FLOW/CONTENT/02_PRESSURE_VELOCITY_COUPLING/04_Underrelaxation_Practices.md)**: Stability considerations for non-Newtonian viscosity
- **[05_OpenFOAM_Programming/05_Fields_GeometricFields/02_Design_Philosophy.md](../../05_OPENFOAM_PROGRAMMING/CONTENT/05_FIELDS_GEOMETRICFIELDS/02_Design_Philosophy.md)**: VolSurfaceField implementation for viscosity fields

---

## 🎓 Practice Problems

### Problem 1: Model Selection

**Scenario**: You are simulating flow of a new cosmetic cream in a tube. Rheometry shows:
- No flow below 15 Pa stress
- Viscosity = 2000 cP at rest
- Viscosity = 50 cP at shear rate 100 s⁻¹
- Viscosity = 20 cP at shear rate 1000 s⁻¹

**Question**: Which model is most appropriate? Justify your answer.

<details>
<summary>Solution</summary>

**Answer**: **Herschel-Bulkley** is the best choice.

**Reasoning**:
1. **Yield stress present** (15 Pa) → Rules out Power Law, Cross, Carreau
2. **Shear-thinning after yield** (2000 → 50 → 20 cP) → Rules out pure Bingham
3. **No clear high-shear plateau** in this range → Herschel-Bulkley preferred over Carreau

**Parameter estimates**:
- τy ≈ 15 Pa
- At γ̇ = 100 s⁻¹: η = τy/γ̇ + k·γ̇^(n-1) → 0.05 = 15/100 + k·100^(n-1)
- Solve for k, n using both data points

</details>

---

### Problem 2: Parameter Sensitivity

**Scenario**: A Power Law fluid has k = 0.5 Pa·s⁰·⁶ and n = 0.4. You need to halve the pressure drop in a pipe flow while maintaining the same velocity profile shape.

**Question**: What parameter changes achieve this?

<details>
<summary>Solution</summary>

**Answer**: **Reduce k to 0.25 Pa·s⁰·⁶, keep n = 0.4**

**Reasoning**:
- Velocity profile shape in Power Law flow depends only on `n`
- Pressure drop scales approximately with `k` for fixed geometry and velocity
- Halving `k` → ~50% pressure drop reduction
- Maintaining `n` → Same velocity profile shape (same degree of shear-thinning)

**Verification**:
```
Original: η = 0.5 · γ̇^(0.4-1) = 0.5 · γ̇^(-0.6)
Modified: η = 0.25 · γ̇^(-0.6)

At any γ̇: η_modified = 0.5 × η_original
```
</details>

---

### Problem 3: Cross Model Analysis

**Scenario**: A polymer solution has Cross model parameters:
- η₀ = 1 Pa·s
- η∞ = 0.001 Pa·s  
- m = 0.5 s
- n = 0.8

**Questions**:
a) What is the critical shear rate?
b) What is the viscosity at γ̇ = 2 s⁻¹?
c) Is this fluid strongly or weakly shear-thinning?

<details>
<summary>Solution</summary>

**a) Critical shear rate**:
```
γ̇_critical ≈ 1/m = 1/0.5 = 2 s⁻¹
```

**b) Viscosity at γ̇ = 2 s⁻¹**:
```
η = η∞ + (η₀ - η∞) / [1 + (m·γ̇)^n]
η = 0.001 + (1 - 0.001) / [1 + (0.5×2)^0.8]
η = 0.001 + 0.999 / [1 + 1^0.8]
η = 0.001 + 0.999 / 2
η = 0.5005 Pa·s
```

**c) Shear-thinning strength**:
```
η₀/η∞ ratio = 1/0.001 = 1000
```
**Strong shear-thinning** (ratio >> 100), but `n = 0.8` indicates **gradual transition** (mild non-linearity)

</details>

---

### Problem 4: Yield Stress Design

**Scenario**: You need to design a cement slurry with:
- Minimum yield stress 50 Pa (to prevent particle settling)
- Maximum pumping pressure 200 kPa
- Pipe length 10 m, diameter 0.1 m
- Target velocity 0.5 m/s

**Question**: What maximum plastic viscosity (η_p) can you use? (Assume Bingham plastic)

<details>
<summary>Solution</summary>

**Answer**: **η_p ≤ 3.2 Pa·s**

**Calculation**:

1. **Wall shear stress** from pressure drop:
```
τ_w = ΔP · D / (4 · L) = 200,000 × 0.1 / (4 × 10) = 500 Pa
```

2. **Bingham plastic wall stress**:
```
τ_w = τ_y + η_p · (8V/D)

500 = 50 + η_p · (8 × 0.5 / 0.1)
500 = 50 + η_p · 40
η_p = 450 / 40 = 11.25 Pa·s
```

Wait - let me recalculate. The relationship for Bingham plastic in laminar pipe flow is:
```
τ_w = τ_y + (η_p · 8V / D) 

Solving for η_p:
η_p = (τ_w - τ_y) · D / (8V)
η_p = (500 - 50) × 0.1 / (8 × 0.5)
η_p = 45 × 0.1 / 4
η_p = 1.125 Pa·s
```

**Maximum η_p ≈ 1.1 Pa·s** to stay within pressure limit

(Note: This is simplified - turbulent Bingham flow is more complex)

</details>

---

## ✅ Key Takeaways

1. **Model Selection Hierarchy**:
   - **Yield stress present** → Bingham or Herschel-Bulkley
   - **Wide shear rate range** → Cross or Carreau
   - **Limited data, narrow range** → Power Law

2. **Physical Meaning of Parameters**:
   - **Magnitude parameters** (k, η₀, η_p): Scale viscosity uniformly
   - **Shape parameters** (n, m, λ): Control shear-dependence
   - **Yield stress** (τy): Creates flow/no-flow threshold

3. **Numerical Stability**:
   - Always set viscosity limits (nuMin, nuMax) for Power Law and yield stress models
   - Use regularisation for Bingham/Herschel-Bulkley in OpenFOAM
   - Expect convergence challenges when η₀/η∞ > 1000 or n < 0.3

4. **Cross-Reference Links**:
   - See [01_Non_Newtonian_Fundamentals.md](01_Non_Newtonian_Fundamentals.md) for constitutive equation derivation
   - See [04_Numerical_Implementation.md](04_Numerical_Implementation.md) for discretization details
   - See [03_OpenFOAM_Architecture.md](03_OpenFOAM_Architecture.md) for runtime selection

5. **Practical Workflow**:
   1. Measure rheology across relevant shear rate range
   2. Identify features: yield stress? plateaus? transition sharpness?
   3. Select model using flowchart (Section 2)
   4. Fit parameters to experimental data
   5. Set viscosity limits based on fitted extremes
   6. Validate simulation against analytical/experimental benchmarks

---

## 📚 Further Reading

### OpenFOAM Implementation
- **Source Code**: `src/transportModels/viscosityModels/`
  - `powerLaw.H`, `powerLaw.C`
  - `CrossPowerLaw.H`, `CrossPowerLaw.C`
  - `Carreau.H`, `Carreau.C`
  - `BinghamPlastic.H`, `BinghamPlastic.C`
  - `HerschelBulkley.H`, `HerschelBulkley.C`

### Rheology References
- Barnes, H. A., Hutton, J. F., & Walters, K. (1989). *An Introduction to Rheology*. Elsevier.
- Macosko, C. W. (1994). *Rheology: Principles, Measurements, and Applications*. Wiley-VCH.
- Bird, R. B., Armstrong, R. C., & Hassager, O. (1987). *Dynamics of Polymeric Liquids*. Wiley.

### OpenFOAM Tutorials
- `tutorials/transportModels/nonNewtonianIcoFoam/` - Power Law example
- `tutorials/multiphase/interFoam/ras/rotatingTank` - VOF with non-Newtonian fluids

---

## 📖 Related Documentation

- **Overview**: [00_Overview.md](00_Overview.md) - Module roadmap and prerequisites
- **Fundamentals**: [01_Non_Newtonian_Fundamentals.md](01_Non_Newtonian_Fundamentals.md) - Constitutive equations and stress tensors
- **Architecture**: [03_OpenFOAM_Architecture.md](03_OpenFOAM_Architecture.md) - Runtime selection and model registration
- **Implementation**: [04_Numerical_Implementation.md](04_Numerical_Implementation.md) - Discretization and solver strategies