# Model Selection Quick Reference

**Appendix: Lookup tables and quick decision guides for multiphase flow model selection**

---

## Learning Objectives

By the end of this appendix, you should be able to:
- **WHAT** quick reference tables provide: Rapid lookup of appropriate models for common multiphase scenarios
- **WHY** quick references matter: Enable efficient model selection without re-reading detailed theory
- **HOW** to use these tables: Identify your system type, check key parameters, and select recommended models

**What this is NOT:** This appendix contains only lookup tables and quick guides. For detailed theory, mathematical formulations, and implementation guidance, refer to files 00-04 in this module.

---

## Prerequisites

Before using these reference tables, ensure you have:
- Identified your phase system type (gas-liquid, gas-solid, liquid-liquid, solid-solid)
- Estimated key dimensionless numbers (Re, Eo, Pe, void fraction α)
- Understood your flow regime (dilute vs. dense, spherical vs. deformed)

**For detailed explanations of these prerequisites,** see [00_Overview.md](00_Overview.md) and [01_Decision_Framework.md](01_Decision_Framework.md)

---

## Why This Matters

Model selection is the most critical decision in multiphase CFD simulations. The wrong model choice leads to:
- **Physically unrealistic results** (e.g., incorrect phase distribution, unrealistic velocities)
- **Numerical instability** (divergent solutions, solver crashes)
- **Wasted computational resources** (hours or days of failed simulations)

These quick reference tables help you make informed model selection decisions efficiently, backed by the detailed theory presented in files 00-04.

---

## Quick Selection Tables

### Phase System → Drag Model

| System | Condition | Drag Model | Reference |
|--------|-----------|------------|-----------|
| **Gas-Liquid** | d < 1mm (spherical) | SchillerNaumann | [02_VOF_Method](02_VOF_Method/) |
| **Gas-Liquid** | d > 1mm (deformed) | Tomiyama | [02_VOF_Method](02_VOF_Method/) |
| **Gas-Solid** | Dilute (α < 0.2) | WenYu | [03_Euler_Euler_Method](03_Euler_Euler_Method/) |
| **Gas-Solid** | Dense / Packed | Gidaspow / Ergun | [03_Euler_Euler_Method](03_Euler_Euler_Method/) |
| **Gas-Solid** | Fluidized bed | SyamlalOBrien | [03_Euler_Euler_Method](03_Euler_Euler_Method/) |
| **Liquid-Liquid** | Eo < 0.5 (spherical) | SchillerNaumann | [02_VOF_Method](02_VOF_Method/) |
| **Liquid-Liquid** | Eo > 0.5 (deformed) | Grace | [02_VOF_Method](02_VOF_Method/) |

### Dimensionless Number Quick Reference

| Number | Formula | Physical Meaning | Critical Values |
|--------|---------|------------------|-----------------|
| **Particle Reynolds** | Re_p = ρ_c u_rel d_p / μ_c | Inertia vs. viscous | <1 (creeping), 1-1000 (transitional), >1000 (inertial) |
| **Eötvös Number** | Eo = g(ρ_c-ρ_d)d_p²/σ | Gravity vs. surface | <1 (spherical), >1 (deformed bubbles) |
| **Peclet Number** | Pe = Re_p · Pr | Convection vs. conduction | <10 (conduction), >10 (convection) |

**For detailed theory on dimensionless numbers,** see [01_Decision_Framework.md](01_Decision_Framework.md)

---

## Model Decision Flowcharts

### Drag Model Selection

```
Is it Gas-Liquid?
├── Yes → Is bubble diameter > 1mm?
│   ├── Yes → Tomiyama (deformable)
│   └── No  → SchillerNaumann (spherical)
└── No  → Is it Gas-Solid?
    ├── Yes → Is αs > 0.4 (packed)?
    │   ├── Yes → Ergun or Gidaspow
    │   └── No  → WenYu or SyamlalOBrien
    └── No  → Liquid-Liquid
        └── Use Grace or SchillerNaumann based on Eo
```

**For detailed drag model theory:** [01_DRAG/01_Fundamental_Drag_Concept.md](01_DRAG/01_Fundamental_Drag_Concept.md)

### Lift Model Selection

| Condition | Lift Model | Application | Reference |
|-----------|------------|-------------|-----------|
| Solid particles, Re < 1000 | SaffmanMei | Shear-induced lift | [02_LIFT](02_LIFT/) |
| Gas bubbles in liquid | Tomiyama | Sign reversal for large bubbles | [02_LIFT](02_LIFT/) |
| Negligible lift effects | NoLift | Faster computation | [02_LIFT](02_LIFT/) |

**For detailed lift model theory:** [02_LIFT/01_Fundamental_Lift_Concepts.md](02_LIFT/01_Fundamental_Lift_Concepts.md)

### Turbulence Model Selection

| System | αd Range | Turbulence Model | Dispersion Model | Reference |
|--------|----------|------------------|------------------|-----------|
| Dilute bubbly | < 0.1 | kEpsilon | Simonin | [04_TURBULENT_DISPERSION](04_TURBULENT_DISPERSION/) |
| Dense bubbly | > 0.1 | mixtureKEpsilon | Simonin | [04_TURBULENT_DISPERSION](04_TURBULENT_DISPERSION/) |
| Gas-Solid dilute | < 0.1 | kEpsilon | dispersedPhase | [04_TURBULENT_DISPERSION](04_TURBULENT_DISPERSION/) |
| Gas-Solid dense | > 0.3 | perPhase kEpsilon | Burns | [04_TURBULENT_DISPERSION](04_TURBULENT_DISPERSION/) |

**For detailed turbulence theory:** [04_TURBULENT_DISPERSION/01_Fundamental_Theory.md](04_TURBULENT_DISPERSION/01_Fundamental_Theory.md)

### Heat Transfer Model Selection

| Pe Range | Regime | Model | Application | Reference |
|----------|--------|-------|-------------|-----------|
| < 10 | Conduction dominant | Spherical | Low Re particles | Module 03: Heat Transfer |
| > 10 | Convection dominant | RanzMarshall | Moderate Re | Module 03: Heat Transfer |
| High Re, turbulent | — | Gunn | Dense flows | Module 03: Heat Transfer |

**For detailed heat transfer theory:** See Module 03, Section 04: Heat Transfer

### Virtual Mass Model Selection

| Condition | Model | Cvm Value | When to Use | Reference |
|-----------|-------|-----------|-------------|-----------|
| Heavy particles (ρd/ρc > 1000) | negligible | — | Solid particles in gas | [03_VIRTUAL_MASS](03_VIRTUAL_MASS/) |
| Light particles/bubbles | constant | 0.5 | Gas bubbles in liquid | [03_VIRTUAL_MASS](03_VIRTUAL_MASS/) |
| Variable (research) | Zuber | f(α) | Research applications | [03_VIRTUAL_MASS](03_VIRTUAL_MASS/) |

**For detailed virtual mass theory:** [03_VIRTUAL_MASS/01_Fundamental_Concepts.md](03_VIRTUAL_MASS/01_Fundamental_Concepts.md)

---

## OpenFOAM Configuration Quick Reference

### Phase Interaction Template

```cpp
// constant/phaseProperties
phases
{
    water { type liquid; }
    air   { type gas; }
}

phaseInteraction
{
    // DRAG - Select from table above
    dragModel       Tomiyama;
    TomiyamaCoeffs
    {
        C1    0.44;   // High Re drag
        C2    24.0;   // Low Re (24/Re)
        C3    0.15;   // Re exponent
        C4    6.0;    // Eo correction
    }
    
    // LIFT - Select from table above
    liftModel       Tomiyama;
    TomiyamaCoeffs
    {
        CL    0.5;    // Positive = towards wall
    }
    
    // VIRTUAL MASS - Select from table above
    virtualMassModel constant;
    constantCoeffs
    {
        Cvm    0.5;  // Typically 0.5 for spheres
    }
    
    // TURBULENT DISPERSION - Select from table above
    turbulentDispersionModel Simonin;
    
    // HEAT TRANSFER - Select from table above
    heatTransferModel RanzMarshall;
    RanzMarshallCoeffs
    {
        Pr    0.7;  // Prandtl number
    }
}
```

### Turbulence Properties Template

```cpp
// constant/turbulenceProperties
simulationType  RAS;

RAS
{
    RASModel    kEpsilon;  // or mixtureKEpsilon, kOmegaSST
    
    kEpsilonCoeffs
    {
        Cmu         0.09;
        C1          1.44;
        C2          1.92;
        sigmaK      1.0;
        sigmaEps    1.3;
    }
}
```

**For detailed implementation guidance:** See respective model subsections in 01-04 folders

---

## Common Issues

| Problem | Possible Cause | Quick Check | Solution |
|---------|----------------|-------------|----------|
| Unrealistic bubble velocities | Wrong drag model | Calculate Eo number | Use Tomiyama if Eo > 1 |
| Wall peaking incorrect | Lift model issue | Check bubble size | Use Tomiyama lift for d > 1mm |
| Unstable near packed bed | Wrong dense model | Check solid fraction αs | Switch to Gidaspow/Ergun if αs > 0.4 |
| Poor heat transfer | Wrong Nu correlation | Calculate Pe number | Use Gunn if Pe > 100 |
| Divergent solution | Incompatible models | Check all model pairs | Ensure models are compatible for your regime |

**For detailed troubleshooting:** See individual model sections in 01-04 folders

---

## Key Takeaways

### Core Selection Principles

1. **Phase System Determines Model Choice**
   - Gas-liquid: Focus on bubble deformation (Eo number)
   - Gas-solid: Focus on solid fraction (α) and regime transitions
   - Liquid-liquid: Consider surface tension effects

2. **Dimensionless Numbers Guide Selection**
   - Calculate Re_p, Eo, and Pe first
   - Use these numbers to select appropriate regime-specific models
   - Always verify your regime assumptions match simulation results

3. **Model Compatibility Matters**
   - Not all model combinations are numerically stable
   - Dense-phase models require careful under-relaxation
   - When in doubt, start simple and add complexity gradually

### Practical Implementation Tips

- Start with Schiller-Naumann + NoLift + NoVirtualMass for initial simulations
- Add complexity (Tomiyama, lift, virtual mass) only after baseline is stable
- Always check that your selected models match your flow regime
- Document your model selection rationale for reproducibility

---

## Concept Check

<details>
<summary><b>Q1: When should you use Tomiyama instead of Schiller-Naumann for drag?</b></summary>

**Answer:** Use Tomiyama when bubble diameter > 1mm or Eo > 1. Schiller-Naumann assumes spherical particles, while Tomiyama accounts for bubble deformation effects that become significant at larger bubble sizes.

**Reference:** [01_DRAG/02_Specific_Drag_Models.md](01_DRAG/02_Specific_Drag_Models.md)
</details>

<details>
<summary><b>Q2: When is the Gidaspow drag model appropriate?</b></summary>

**Answer:** Gidaspow is used for gas-solid systems with high solid fractions. It combines Wen-Yu (dilute) and Ergun (packed bed) correlations using a blending function, making it suitable across a wide range of volume fractions.

**Reference:** [01_DRAG/02_Specific_Drag_Models.md](01_DRAG/02_Specific_Drag_Models.md)
</details>

<details>
<summary><b>Q3: Why is virtual mass particularly important for bubbly flows?</b></summary>

**Answer:** Bubbles have much lower density than the surrounding liquid. When a bubble accelerates, it must also accelerate the surrounding liquid, creating significant added mass effects. The virtual mass coefficient (typically Cvm = 0.5) captures this effect and is crucial for accurate bubble dynamics.

**Reference:** [03_VIRTUAL_MASS/01_Fundamental_Concepts.md](03_VIRTUAL_MASS/01_Fundamental_Concepts.md)
</details>

<details>
<summary><b>Q4: How do you select between kEpsilon and mixtureKEpsilon for turbulence?</b></summary>

**Answer:** Use kEpsilon for dilute dispersed phase (α < 0.1) where the continuous phase turbulence dominates. Use mixtureKEpsilon for dense dispersed phase (α > 0.1) where the dispersed phase significantly affects mixture turbulence properties.

**Reference:** [04_TURBULENT_DISPERSION/01_Fundamental_Theory.md](04_TURBULENT_DISPERSION/01_Fundamental_Theory.md)
</details>

---

## Related Documentation

- **Decision Methodology:** [01_Decision_Framework.md](01_Decision_Framework.md) - Systematic approach to model selection
- **Drag Models:** [01_DRAG/](01_DRAG/) - Detailed drag theory and implementation
- **Lift Models:** [02_LIFT/](02_LIFT/) - Lift force theory and model options
- **Virtual Mass:** [03_VIRTUAL_MASS/](03_VIRTUAL_MASS/) - Added mass effects
- **Turbulent Dispersion:** [04_TURBULENT_DISPERSION/](04_TURBULENT_DISPERSION/) - Turbulence-induced phase interactions
- **System-Specific Guides:**
  - Gas-Liquid: [02_Gas_Liquid_Systems.md](02_Gas_Liquid_Systems.md)
  - Gas-Solid: [03_Gas_Solid_Systems.md](03_Gas_Solid_Systems.md)