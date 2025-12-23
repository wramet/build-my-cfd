# 04. Numerical Implementation in OpenFOAM

## Overview

This section examines how OpenFOAM implements non-Newtonian viscosity models numerically, focusing on strain-rate tensor calculations, model-specific algorithms, runtime selection mechanisms, and numerical stability strategies.

---

## 1. Strain-Rate Tensor Calculation

### Mathematical Foundation

The strain-rate tensor $\dot{\boldsymbol{\gamma}}$ is defined as the **symmetric part of the velocity gradient**:

$$
\dot{\boldsymbol{\gamma}} = \nabla \mathbf{u} + (\nabla \mathbf{u})^{\mathrm{T}}
$$

In OpenFOAM's strain-rate-dependent models, the **scalar magnitude of strain-rate** $\dot{\gamma}$ is used:

$$
\dot{\gamma} = \sqrt{2} \; \bigl\| \dot{\boldsymbol{\gamma}} \bigr\|
$$

**Variable Definitions:**
- $\mathbf{u}$ – Fluid velocity vector
- $\nabla \mathbf{u}$ – Velocity gradient tensor
- $(\nabla \mathbf{u})^{\mathrm{T}}$ – Transpose of velocity gradient tensor
- $\|\cdot\|$ – Frobenius norm (`.mag()` in OpenFOAM)

### OpenFOAM Implementation

The calculation appears in `strainRateViscosityModel::strainRate()`:

```cpp
// src/.../strainRateViscosityModel/strainRateViscosityModel.C
tmp<volScalarField> strainRateViscosityModel::strainRate() const
{
    return sqrt(2.0)*mag(symm(fvc::grad(U_)));
}
```

**Computation Breakdown:**

| Operation | Description | Mathematical Equivalent |
|-----------|-------------|-------------------------|
| `fvc::grad(U_)` | Computes velocity gradient tensor | $\nabla \mathbf{u}$ |
| `symm(...)` | Extracts symmetric part | $\frac{1}{2}(\nabla\mathbf{u} + (\nabla\mathbf{u})^{\mathrm{T}})$ |
| `mag(...)` | Returns Frobenius norm | $\|\mathbf{T}\| = \sqrt{\sum_{i,j} T_{ij}^2}$ |
| `sqrt(2.0)` | Scaling factor | Produces $\dot{\gamma}$ |

### Mathematical Properties

The strain-rate tensor represents the **rate of deformation of fluid elements** and is fundamental to non-Newtonian rheology.

For incompressible flow, **the trace of $\dot{\boldsymbol{\gamma}}$ is zero**:

$$
\text{tr}(\dot{\boldsymbol{\gamma}}) = \nabla \cdot \mathbf{u} = 0
$$

This property guarantees **volume conservation in incompressible flow** and is automatically satisfied by the symmetric part of the velocity gradient.

### Finite Volume Implementation Details

OpenFOAM's implementation leverages the **finite volume calculus (fvc) framework**:

#### Step 1: Gradient Computation

`fvc::grad(U_)` uses Gauss's theorem to compute cell-centered velocity gradients from face values:

$$
(\nabla \mathbf{u})_P = \frac{1}{V_P} \sum_f \mathbf{u}_f \cdot \mathbf{S}_f
$$

#### Step 2: Symmetrization

The template function `symm()` extracts the symmetric part:

```cpp
template<class Type>
inline Type symm(const Type& t)
{
    return 0.5*(t + transpose(t));
}
```

#### Step 3: Norm Calculation

`mag()` computes the Frobenius norm:

$$
\|\mathbf{T}\| = \sqrt{\sum_{i,j} T_{ij}^2}
$$

### Performance Considerations

| Aspect | Implementation Benefit |
|--------|----------------------|
| **Memory Management** | `tmp<volScalarField>` enables efficient temporary field handling with automatic reference counting |
| **Parallel Efficiency** | All operations are naturally parallel through OpenFOAM's domain decomposition |
| **Numerical Accuracy** | Calculations benefit from second-order accurate gradient schemes when specified in `fvSchemes` |

### Extension to Anisotropic Models

For anisotropic non-Newtonian models, the **full strain-rate tensor** may be required instead of just the magnitude:

```cpp
tmp<volTensorField> strainRateTensor() const
{
    return symm(fvc::grad(U_));
}
```

This enables models that account for **direction-dependent rheological behavior** such as:
- Fiber stretching
- Liquid crystals
- Complex structured materials

---

## 2. Code Analysis of Three Key Models

### 2.1 Bird-Carreau Model

#### Mathematical Foundation

The Bird-Carreau model is one of the most widely used generalized Newtonian fluid models in computational fluid dynamics. It captures the transition between Newtonian behavior at low and high shear rates, making it suitable for simulating polymer melts, blood flow, and other complex fluids.

The basic Bird-Carreau equation relates kinematic viscosity $\nu$ to shear rate $\dot{\gamma}$ through:

$$
\nu = \nu_{\infty} + (\nu_0 - \nu_{\infty})\Bigl[1 + (k\dot{\gamma})^a\Bigr]^{(n-1)/a}
$$

**Where:**
- $\nu_0$ – Zero-shear-rate viscosity (maximum viscosity as $\dot{\gamma} \to 0$)
- $\nu_{\infty}$ – Infinite-shear-rate viscosity (minimum viscosity as $\dot{\gamma} \to \infty$)
- $k$ – Time constant controlling transition region
- $n$ – Power-law index determining shear-thinning behavior
- $a$ – Yasuda exponent (often called $\alpha$) controlling transition sharpness

An alternative formulation uses critical stress $\tau^*$ instead of time constant $k$:

$$
\nu = \nu_{\infty} + (\nu_0 - \nu_{\infty})\Bigl[1 + \bigl(\frac{\nu_0\dot{\gamma}}{\tau^*}\bigr)^a\Bigr]^{(n-1)/a}
$$

#### Implementation Analysis

OpenFOAM's implementation in `BirdCarreau.C` handles both parameter formulations seamlessly:

```cpp
return
    nuInf_
  + (nu0 - nuInf_)
   *pow
    (
        scalar(1)
      + pow
        (
            tauStar_.value() > 0
          ? nu0*strainRate/tauStar_
          : k_*strainRate,
            a_
        ),
        (n_ - 1.0)/a_
    );
```

**Key Implementation Details:**

1. **Parameter Selection**: The conditional operator `tauStar_.value() > 0 ? ... : ...` allows users to specify either critical stress or time constant

2. **Numerical Stability**: The implementation uses `pow()` for efficient nested exponential computation

3. **Exponent Calculation**: The exponent `(n_ - 1.0)/a_` controls the overall shear-thinning behavior

#### Physical Regimes

The Bird-Carreau model exhibits three distinct regimes:

| Regime | Condition | Behavior |
|--------|-----------|----------|
| **Low Shear** | $k\dot{\gamma} \ll 1$ | Viscosity approaches $\nu_0$ (Newtonian plateau) |
| **Transition** | $k\dot{\gamma} \approx 1$ | Viscosity decreases following power-law behavior |
| **High Shear** | $k\dot{\gamma} \gg 1$ | Viscosity approaches $\nu_{\infty}$ (Newtonian plateau) |

**Primary Applications:**
- **Blood flow simulation**: Captures blood's shear-thinning behavior in arteries
- **Polymer processing**: Modeling polymer melts in injection molding and extrusion
- **Food processing**: Simulating non-Newtonian food materials
- **Biomedical applications**: Modeling mucus, synovial fluid, and other biological fluids

---

### 2.2 Herschel-Bulkley Model

#### Mathematical Foundation

The Herschel-Bulkley model extends the power-law model to include yield stress behavior, making it suitable for materials that exhibit solid-like behavior at low stress levels but flow like liquids when applied stress exceeds the yield stress.

The constitutive equation combines yield stress and power-law behavior:

$$
\nu = \min\Bigl(\nu_0,\; \frac{\tau_0}{\dot{\gamma}} + k\dot{\gamma}^{\,n-1}\Bigr)
$$

**Where:**
- $\tau_0$ – Yield stress (minimum stress required to initiate flow)
- $k$ – Consistency index (related to viscosity)
- $n$ – Flow behavior index (power-law exponent)
- $\nu_0$ – Zero-shear-rate viscosity (maximum allowed viscosity)

#### Implementation Analysis

OpenFOAM's implementation in `HerschelBulkley.C` demonstrates careful attention to numerical stability and dimensional consistency:

```cpp
dimensionedScalar tone("tone", dimTime, 1.0);
dimensionedScalar rtone("rtone", dimless/dimTime, 1.0);

return
(
    min
    (
        nu0,
        (tau0_ + k_*rtone*pow(tone*strainRate, n_))
       /max
        (
            strainRate,
            dimensionedScalar ("vSmall", dimless/dimTime, vSmall)
        )
    )
);
```

**Key Implementation Features:**

1. **Dimensional Consistency**: Auxiliary variables `tone` and `rtone` ensure correct dimensional analysis for power-law terms

2. **Numerical Stability**: `max(strainRate, vSmall)` prevents division by zero when shear rate approaches zero

3. **Viscosity Capping**: The `min(nu0, ...)` operation ensures calculated viscosity doesn't exceed the specified zero-shear viscosity

#### Physical Behavior and Stress Regimes

The Herschel-Bulkley model exhibits different behaviors depending on stress levels:

| State | Condition | Behavior |
|-------|-----------|----------|
| **Solid** | $\tau < \tau_0$ | Material behaves as a solid with effectively infinite viscosity |
| **Yield** | $\tau = \tau_0$ | Material begins to flow with very high effective viscosity |
| **Power-Law** | $\tau > \tau_0$ | Material flows according to power-law behavior |

**Common Applications:**
- **Drilling fluids**: Simulating drilling mud flow in petroleum engineering
- **Concrete and cement**: Simulating fresh concrete flow during construction
- **Food products**: Simulating mayonnaise, tomato paste, and other yield-stress foods
- **Mining slurries**: Simulating tailings and mineral processing slurries
- **Geophysical flows**: Simulating lava and debris flows

---

### 2.3 Power-Law Model (Ostwald–de Waele)

#### Mathematical Foundation

The power-law model is the simplest generalized Newtonian fluid model, representing fluids whose viscosity varies as a power function of shear rate. It serves as the foundation for more complex non-Newtonian fluid models.

The constitutive equation is:

$$
\nu = \min\Bigl(\nu_{\max},\; \max\bigl(\nu_{\min},\; k\dot{\gamma}^{\,n-1}\bigr)\Bigr)
$$

**Where:**
- $k$ – Consistency index (comparable to viscosity)
- $n$ – Flow behavior index (determines shear-thinning or thickening)
- $\nu_{\min}$ and $\nu_{\max}$ – Clipping bounds for numerical stability

#### Implementation Analysis

OpenFOAM's implementation in `powerLaw.C` includes important numerical safeguards:

```cpp
return max
(
    nuMin_,
    min
    (
        nuMax_,
        k_*pow
        (
            max
            (
                dimensionedScalar(dimTime, 1.0)*strainRate,
                dimensionedScalar(dimless, small)
            ),
            n_.value() - scalar(1)
        )
    )
);
```

**Key Implementation Details:**

1. **Viscosity Clipping**: Nested structure `max(nuMin_, min(nuMax_, ...))` ensures calculated viscosity remains within physically possible bounds

2. **Shear Rate Protection**: `max(strainRate, small)` ensures power-law calculation doesn't use zero or negative shear rates

3. **Power Calculation**: Exponent is calculated as `(n_ - 1.0)` following the mathematical relationship between viscosity and shear rate in power-law fluids

#### Physical Behavior and Regimes

The power-law model exhibits different behaviors depending on the flow behavior index $n$:

| Behavior | Condition | Properties | Examples | Applications |
|----------|-----------|------------|----------|--------------|
| **Shear-thinning (Pseudoplastic)** | $n < 1$ | Viscosity decreases as shear rate increases | Blood, polymer solutions, paints | Biological flows, coating processes |
| **Shear-thickening (Dilatant)** | $n > 1$ | Viscosity increases as shear rate increases | Cornstarch mixtures, sand-water suspensions | Impact protection, specialty manufacturing |
| **Newtonian** | $n = 1$ | Constant viscosity regardless of shear rate | Water, air, simple oils | Basic flows |

#### Limitations and Extensions

While the power-law model is computationally efficient and conceptually simple, it has limitations:

- **No Yield Stress**: Cannot simulate materials requiring a threshold stress to initiate flow
- **No Plateaus**: Cannot capture Newtonian behavior at low or high shear rates
- **Dimensional Issues**: Requires careful dimensional analysis for consistency

These limitations motivate the use of more complex models like Bird-Carreau and Herschel-Bulkley for complex fluids, while the power-law model remains valuable for its simplicity and computational efficiency in many engineering applications.

---

## 3. Factory Pattern and Runtime Selection

OpenFOAM employs a sophisticated **dictionary-driven factory pattern** for instantiating appropriate viscosity model instances at runtime.

This design pattern enables remarkable **flexibility** in model selection while maintaining **compile-time type safety** and **runtime efficiency**. The pattern is constructed through three carefully designed macros working together to create a plug-in architecture:

```mermaid
flowchart TD
    A[Dictionary Entry] --> B[viscosityModel::New]
    B --> C{Factory Table Lookup}
    C --> D[Model Found?]
    D -->|Yes| E[Instantiate Model]
    D -->|No| F[Error with Available Models]
    E --> G[Return autoPtr to Model]

    style A fill:#e3f2fd,stroke:#1976d2
    style B fill:#bbdefb,stroke:#1976d2
    style C fill:#90caf9,stroke:#1976d2
    style E fill:#4caf50,stroke:#2e7d32
    style F fill:#f44336,stroke:#c62828
```

### Runtime Selection Table Structure

| Macro | Location Used | Primary Function | Result |
|-------|---------------|------------------|--------|
| **`declareRunTimeSelectionTable`** | Base class header (`viscosityModel.H`) | Declares static table for matching strings to constructors | Establishes interface for derived classes |
| **`defineRunTimeSelectionTable`** | Base class source (`viscosityModel.C`) | Defines storage and initialization of factory structure | Creates factory infrastructure |
| **`addToRunTimeSelectionTable`** | Specific model implementation files | Registers specific models with factory table | Makes available for runtime selection |

### Factory Method Implementation

The main factory method in `viscosityModel` demonstrates the elegance of this approach:

```cpp
// From src/physicalProperties/viscosityModels/viscosityModel/viscosityModelNew.C
Foam::autoPtr<Foam::viscosityModel> Foam::viscosityModel::New
(
    const fvMesh& mesh,
    const word& group
)
{
    // Read the model type from the dictionary (looks for "viscosityModel" or "transportModel")
    const word modelType = IOdictionary
    (
        IOobject
        (
            "transportProperties",
            mesh.time().constant(),
            mesh,
            IOobject::MUST_READ_IF_MODIFIED,
            IOobject::NO_WRITE
        )
    ).lookupOrDefault<word>("viscosityModel", "Newtonian");

    Info<< "Selecting viscosity model " << modelType << endl;

    typename viscosityModel::dictionaryConstructorTable::iterator cstrIter =
        viscosityModel::dictionaryConstructorTablePtr_->find(modelType);

    if (cstrIter == viscosityModel::dictionaryConstructorTablePtr_->end())
    {
        FatalErrorInFunction
            << "Unknown viscosity model " << modelType << nl << nl
            << "Valid viscosity models are : " << endl
            << viscosityModel::dictionaryConstructorTablePtr_->sortedToc()
            << exit(FatalError);
    }

    return autoPtr<viscosityModel>(cstrIter()(mesh, group));
}
```

#### Algorithm: Factory Selection Process

1. **Dictionary Lookup**
   - Reads `transportProperties` dictionary from `constant/` directory
   - Uses `IOobject` for safe file handling

2. **Model Identification**
   - Extracts `viscosityModel` entry
   - Defaults to "Newtonian" if not specified

3. **Factory Lookup**
   - Searches `dictionaryConstructorTable` for requested model type
   - Uses iterator pattern for efficient lookup

4. **Error Handling**
   - Checks if model was found
   - Displays comprehensive error message with list of available models

5. **Instantiation**
   - Calls appropriate constructor
   - Returns `autoPtr` to created model

### Static Registration Mechanism

The registration process for a specific model like `BirdCarreau` demonstrates the power of this system:

```cpp
// In BirdCarreau.C
addToRunTimeSelectionTable
(
    generalisedNewtonianViscosityModel,
    BirdCarreau,
    dictionary
);
```

This macro expands to create a static object that:
- **Self-registers** during static initialization (before `main()` executes)
- **Inserts** `BirdCarreau::New` into the factory table
- **Enables** automatic model discovery by the factory
- **Requires** no modification to core OpenFOAM code

```mermaid
flowchart LR
    A[Static Initialization] --> B[Constructor Object Created]
    B --> C[Registered in Factory Table]
    C --> D[Available at Runtime]

    style A fill:#fff3e0,stroke:#ef6c00
    style B fill:#ffe0b2,stroke:#ef6c00
    style C fill:#ffcc80,stroke:#ef6c00
    style D fill:#ffa726,stroke:#ef6c00
```

### Architectural Benefits

The factory pattern provides several significant advantages:

#### 1. Extensibility
- New models can be added without recompiling core OpenFOAM libraries
- Simply compile your model as a shared library and reference in dictionary

#### 2. Runtime Flexibility
- Models can be changed by editing dictionary entries
- No recompilation needed, enabling rapid prototyping

#### 3. Type Safety
- Compile-time checking ensures all registered models implement required interface
- Prevents runtime errors from mismatched interfaces

#### 4. Centralized Management
- Automatic discovery of all available models
- Displayed in error messages, providing clear user guidance

#### 5. Dependency Injection
- Enables decoupling between solver code and specific model implementations
- Makes system more maintainable and testable

This architecture exemplifies **OpenFOAM's design philosophy**: providing a robust, extensible framework that can be customized by users without modifying the core CFD codebase.

---

## 4. Numerical Stability Strategies

### The Singularity Problem

Many non-Newtonian models, particularly those with yield stress (e.g., Herschel-Bulkley), have mathematical issues as $\dot{\gamma} \to 0$:

$$
\mu_{eff} = \frac{\tau_0}{\dot{\gamma}} + \dots
$$

As shear rate approaches zero, viscosity tends toward **infinity ($\infty$)**, which computers cannot handle.

> [!WARNING] Numerical Singularity
> Without proper handling, the division by zero causes solver divergence or crashes.

### Regularization Techniques

OpenFOAM and researchers use several techniques to address this issue:

#### 1. Viscosity Capping

The simplest approach is to specify `nuMax` in the dictionary:

$$
\mu = \min(\mu_{calculated}, \mu_{max})
$$

**Implementation:**
```cpp
return min(nu0_, calculated_viscosity);
```

#### 2. Papanastasiou Regularization

Adds an exponential term to make the viscosity curve continuous and smooth:

$$
\tau = \tau_y [1 - \exp(-m\dot{\gamma})] + K\dot{\gamma}^n
$$

Where $m$ is the stress growth parameter controlling regularization.

#### 3. Bercovier-Engleman Regularization

Adds a small value ($\epsilon$) to the denominator:

$$
\mu = \frac{\tau_y}{\sqrt{\dot{\gamma}^2 + \epsilon^2}} + \dots
$$

### Implementation Safeguards

OpenFOAM uses several numerical safeguards at the C++ code level:

```cpp
// Prevent division by zero in Herschel-Bulkley
volScalarField shearRate = max(strainRate,
    dimensionedScalar("vSmall", dimRate, 1e-6));

// Viscosity bounding (Limiting)
mu = max(muMin, min(muMax, mu_calculated));
```

### Comparison of Regularization Methods

| Method | Advantages | Disadvantages | Best For |
|--------|------------|---------------|----------|
| **Capping** | Simple to implement | May introduce discontinuities | Quick prototyping |
| **Papanastasiou** | Smooth transition | Requires tuning parameter $m$ | High accuracy requirements |
| **Bercovier-Engleman** | Mathematically elegant | Can affect low-shear behavior | Theoretical studies |

### Stabilization Strategies

Non-Newtonian simulations often converge more difficultly than Newtonian flows due to constantly changing viscosity.

```mermaid
graph TD
    A[Stabilization Strategies] --> B[Field Relaxation]
    A --> C[Viscosity Bounding]
    A --> D[Iterative Coupling]

    B --> B1[U: 0.3-0.7, p: 0.3]
    C --> C1[nuMin / nuMax limits]
    D --> D1[Picard Iteration]

    style A fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style B fill:#bbdefb
    style C fill:#bbdefb
    style D fill:#bbdefb
```

| Strategy | Description | Effect |
|----------|-------------|--------|
| **Under-Relaxation** | Limit changes in `U` and `p` fields per iteration | Prevents calculation from jumping to divergence |
| **Viscosity Relaxation** | Gradually update viscosity values | Prevents viscosity oscillation between iterations |
| **Implicit Treatment** | Calculate viscosity together with momentum equation | Increases stability but computationally heavier |

### Recommended fvSolution Settings

For non-Newtonian simulations, consider these relaxation factors in `fvSolution`:

```cpp
solvers
{
    p
    {
        solver          GAMG;
        tolerance       1e-06;
        relTol          0.1;
    }

    pFinal
    {
        $p;
        relTol          0;
    }

    U
    {
        solver          smoothSolver;
        smoother        GaussSeidel;
        tolerance       1e-05;
        relTol          0.1;
    }
}

relaxationFactors
{
    fields
    {
        p               0.3;
        U               0.5;
    }
}
```

### Troubleshooting Guide

> [!TIP] Common Issues and Solutions

| Symptom | Possible Cause | Solution |
|---------|----------------|----------|
| **Immediate divergence** | Time step too large or viscosity unbounded | Reduce time step or add reasonable `nuMax` |
| **Viscosity oscillation** | Insufficient relaxation | Lower `relaxationFactors` for `U` (e.g., 0.3 or 0.5) |
| **Slow convergence** | Over-relaxation | Reduce relaxation factors gradually |
| **NaN values** | Division by zero | Ensure proper regularization in model |

### Best Practices

1. **Always use viscosity limits** (`nuMin`, `nuMax`) for yield-stress fluids
2. **Start with lower relaxation factors** and increase gradually once stable
3. **Monitor viscosity field** during initial iterations to ensure bounded values
4. **Use appropriate time stepping** - explicit methods may require very small time steps
5. **Consider implicit treatment** for strongly non-Newtonian behavior

---

## 5. Performance Considerations

### Computational Cost Comparison

| Model | Computational Cost | Algorithm Complexity |
|-------|-------------------|---------------------|
| **Power-Law** | Lowest | Single power function |
| **Herschel-Bulkley** | Medium | Yield stress handling required |
| **Bird-Carreau** | Highest | Nested exponential functions |

### Memory Management

OpenFOAM's use of `tmp<volScalarField>` provides several benefits:

```cpp
tmp<volScalarField> strainRate() const
{
    return sqrt(2.0)*mag(symm(fvc::grad(U_)));
}
```

**Advantages:**
- Automatic reference counting
- Efficient temporary field handling
- Avoids unnecessary memory allocation
- Enables return value optimization

### Parallel Efficiency

All strain-rate and viscosity calculations are:
- **Naturally parallel** through field operations
- **Domain decomposed** automatically by OpenFOAM
- **Load balanced** across processors

### Accuracy vs. Efficiency Trade-offs

| Aspect | High Accuracy | High Efficiency |
|--------|---------------|-----------------|
| **Gradient Scheme** | Second-order (Gauss linear) | First-order (Gauss upwind) |
| **Regularization** | Papanastasiou (tuned) | Simple capping |
| **Solver Settings** | Strict tolerance | Relaxed tolerance |

---

## 6. Summary: Key Implementation Insights

### Core Implementation Principles

1. **Strain-Rate Calculation**: Centralized in `strainRateViscosityModel` using `sqrt(2)*mag(symm(grad(U)))`

2. **Model Hierarchy**: Clear separation between interface (`viscosityModel`), strain-rate handling (`strainRateViscosityModel`), and specific constitutive equations

3. **Runtime Selection**: Factory pattern enables dictionary-driven model selection without recompilation

4. **Numerical Stability**: Multiple safeguards including viscosity bounding, regularization, and relaxation strategies

### Key Takeaways

> [!INFO] Design Philosophy
> OpenFOAM's non-Newtonian implementation demonstrates:
> - **Modularity**: Clear separation of concerns
> - **Extensibility**: Easy to add new models
> - **Robustness**: Comprehensive numerical safeguards
> - **Efficiency**: Optimized field operations and memory management

### Integration with Solvers

Non-Newtonian models integrate with solvers through the transport model interface:

```cpp
// In solver main loop
const volScalarField& nu = transport.nu();  // Get viscosity field
transport.correct();                          // Update viscosity
```

### Recommended Workflow

1. **Model Selection**: Choose appropriate model based on fluid behavior
2. **Parameter Identification**: Obtain model parameters from rheometry data
3. **Numerical Setup**: Configure regularization and stability measures
4. **Validation**: Start with simple test cases (e.g., pipe flow)
5. **Application**: Apply to complex geometry with confidence

---

## References and Further Reading

### OpenFOAM Source Files
- `src/physicalProperties/viscosityModels/viscosityModel/`
- `src/physicalProperties/viscosityModels/generalisedNewtonianViscosityModels/`

### Key Papers
- Bird, R. B., et al. (1977). "Dynamics of Polymer Liquids"
- Herschel, W. H., & Bulkley, R. (1926). "Konsistenzmessungen von Gummi-Benzollösungen"
- Papanastasiou, T. C. (1987). "Flows of Materials with Yield"

### Related Documentation
- [[00_Overview]] - Non-Newtonian fluid fundamentals
- [[02_2._Blueprint_The_Viscosity-Model_Hierarchy]] - Class hierarchy details
- [[07_7._Usage_Configuring_a_Non-Newtonian_Case]] - Practical case setup
