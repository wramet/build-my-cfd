I'll refactor this OpenFOAM documentation file following the global strategy and specific instructions.

```markdown
# Numerical Implementation

## 🎯 Learning Objectives

By the end of this section, you will be able to:

1. **Understand** the OpenFOAM viscosity model interface and how it integrates with the solver
2. **Implement** core numerical implementations for common non-Newtonian models (Power Law, Cross, Carreau)
3. **Identify and resolve** numerical stability issues specific to non-Newtonian simulations
4. **Apply** proper boundary treatments and under-relaxation strategies
5. **Configure** OpenFOAM dictionaries for non-Newtonian transport models
6. **Troubleshoot** common numerical errors and convergence problems

---

## Overview

The numerical implementation of non-Newtonian models in OpenFOAM requires careful handling of the coupling between viscosity and strain rate. Unlike Newtonian fluids where viscosity is constant, non-Newtonian models introduce nonlinearities that demand special numerical treatment to ensure stability and convergence.

### Implementation Architecture

```
Solver (e.g., simpleFoam)
    ↓
Transport Model (viscosityModel)
    ↓
Specific Model (CrossPowerLaw, PowerLaw, etc.)
    ↓
Runtime Selection Table
```

The implementation separates **core functionality** (what to compute) from **numerical stability** (how to compute it reliably).

---

## 1. Core Implementation: Viscosity Model Interface

### 1.1 Base Class Architecture

All non-Newtonian models inherit from the `viscosityModel` base class, which defines the interface for viscosity calculation.

```cpp
// Base class interface (in transportModel)
class viscosityModel
{
    public:
        // Calculate viscosity based on strain rate
        tmp<volScalarField> nu() const
        {
            return calcNu(strainRate());
        }
        
        // Virtual function for derived models
        virtual tmp<volScalarField> calcNu(
            const volScalarField& strainRate
        ) const = 0;
        
        // Strain rate calculation
        tmp<volScalarField> strainRate() const
        {
            return sqrt(2.0) * mag(symm(fvc::grad(U)));
        }
};
```

**Key Points:**
- The `nu()` method is called by the solver at each time step
- `strainRate()` computes the magnitude of the strain rate tensor: $\|\dot{\gamma}\| = \sqrt{2}|\text{symm}(\nabla \mathbf{U})|$
- Derived models override `calcNu()` with their specific constitutive equations

---

## 2. Core Implementation: Specific Model Equations

### 2.1 Power Law Model Implementation

```cpp
// PowerLaw.C
tmp<volScalarField> PowerLaw::calcNu(
    const volScalarField& strainRate
) const
{
    // η = k * γ̇^(n-1)
    // k = consistency index
    // n = power law index
    
    volScalarField nu = k_ * pow(
        strainRate + dimensionedScalar("SMALL", dimless, SMALL),
        n_ - 1.0
    );
    
    return nu;
}
```

**Numerical Safeguards:**
- `SMALL` added to strain rate to prevent division by zero
- Resulting viscosity automatically clipped by min/max limits

### 2.2 Cross Power Law Model Implementation

```cpp
// CrossPowerLaw.C
tmp<volScalarField> CrossPowerLaw::calcNu(
    const volScalarField& strainRate
) const
{
    // η = η∞ + (η₀-η∞) / (1 + (mγ̇)^n)
    // nu0 = zero shear viscosity
    // nuInf = infinite shear viscosity
    // m = time constant
    // n = power law index
    
    volScalarField numerator = nu0_ - nuInf_;
    volScalarField denominator = 1.0 + pow(
        m_ * strainRate,
        n_
    );
    
    volScalarField nu = nuInf_ + numerator / denominator;
    
    return nu;
}
```

**Numerical Advantages:**
- Bounded between `nu0` and `nuInf`
- No singularities (denominator ≥ 1)
- Well-behaved at zero and infinite shear rates

### 2.3 Carreau-Yasuda Model Implementation

```cpp
// CarreauYasuda.C
tmp<volScalarField> CarreauYasuda::calcNu(
    const volScalarField& strainRate
) const
{
    // η = η∞ + (η₀-η∞) * [1 + (λγ̇)^a]^((n-1)/a)
    // lambda = time constant
    // a = Yasuda exponent (usually 2)
    // n = power law index
    
    scalar a = yasudaExponent_;
    scalar nMinusA = (n_ - 1.0) / a;
    
    volScalarField term = 1.0 + pow(
        lambda_ * strainRate,
        a
    );
    
    volScalarField nu = nuInf_ + (nu0_ - nuInf_) * pow(
        term,
        nMinusA
    );
    
    return nu;
}
```

---

## 3. Numerical Stability: Critical Issues and Solutions

### 3.1 Zero Shear Rate Singularity

**Problem:** At zero velocity gradient, strain rate = 0, causing:
- Division by zero in power law models
- Infinite viscosity values
- Solver divergence

**Solution Implementation:**
```cpp
// Method 1: Add small value (SMALL)
volScalarField safeStrainRate = strainRate + SMALL;

// Method 2: Minimum viscosity clipping
nu = max(nu, nuMin_);
nu = min(nu, nuMax_);

// Method 3: Regularized power law
nu = k_ * pow(sqrt(strainRate*strainRate + SMALL*SMALL), n_ - 1.0);
```

### 3.2 Viscosity Bounding

**Problem:** Unbounded viscosity variations cause instability:
- Very high viscosity → stiff equations
- Very low viscosity → unrealistic velocities

**Implementation:**
```cpp
// In model constructor or calcNu()
nu = max(nu, nuMin_);  // Prevent near-zero viscosity
nu = min(nu, nuMax_);  // Prevent infinite viscosity

// Recommended values (problem-dependent):
nuMin_ = 1e-6;  // Slightly above physical minimum
nuMax_ = 1e+3;  // Reasonable upper bound
```

### 3.3 Implicit vs Explicit Treatment

**Explicit Treatment (Unstable for large viscosity variations):**
```cpp
// BAD: Viscosity lagged by one iteration
volScalarField nu = model.nu();  // Old value
fvVectorMatrix UEqn
(
    fvm::ddt(rho, U)
  + fvm::div(phi, U)
  - fvm::laplacian(nu, U)  // Uses old viscosity
);
```

**Implicit Treatment (Recommended):**
```cpp
// GOOD: Viscosity updated each iteration
for (int corr = 0; corr < nCorr; corr++)
{
    volScalarField nu = model.nu();  // Updated
    
    fvVectorMatrix UEqn
    (
        fvm::ddt(rho, U)
      + fvm::div(phi, U)
      - fvm::laplacian(nu, U)  // Uses current viscosity
    );
    
    UEqn.solve();
}
```

### 3.4 Under-Relaxation

**Problem:** Large viscosity changes between iterations cause divergence

**Solution:**
```cpp
// Method 1: Relax viscosity field
volScalarField nuNew = model.calcNu(strainRate);
nu = 0.7 * nu + 0.3 * nuNew;  // 30% relaxation

// Method 2: Relax velocity (in fvSolution)
relaxationFactors
{
    U           0.3;  // More aggressive for non-Newtonian
    p           0.3;
}

// Method 3: Combined approach
// - Relax velocity (0.3-0.5)
// - Limit viscosity change per iteration (max 50%)
```

---

## 4. Dictionary Configuration

### 4.1 Basic Transport Properties

```cpp
// constant/transportProperties
transportModel  CrossPowerLaw;  // Runtime selection

CrossPowerLawCoeffs
{
    // Physical parameters
    nu0         1e-3;     // Zero shear viscosity [m²/s]
    nuInf       1e-6;     // Infinite shear viscosity [m²/s]
    
    // Model coefficients
    m           1.0;      // Time constant [s]
    n           0.5;      // Power law index [-]
    
    // Numerical safeguards
    nuMin       1e-7;     // Minimum viscosity
    nuMax       1e-2;     // Maximum viscosity
}
```

### 4.2 Model Runtime Selection Table

Available models in standard OpenFOAM:

| Model Keyword | Class Name | File Location |
|--------------|-----------|---------------|
| `PowerLaw` | PowerLaw | `transportModels/PowerLaw` |
| `CrossPowerLaw` | CrossPowerLaw | `transportModels/CrossPowerLaw` |
| `Carreau` | Carreau | `transportModels/Carreau` |
| `BirdCarreau` | BirdCarreau | `transportModels/BirdCarreau` |
| `HerschelBulkley` | HerschelBulkley | `transportModels/HerschelBulkley` |

---

## 5. Troubleshooting Common Numerical Errors

### 5.1 Solver Divergence

**Symptoms:**
- Solution blows up after a few iterations
- Maximum iterations reached without convergence
- Residuals increase instead of decreasing

**Diagnosis & Solutions:**

```cpp
// Check 1: Viscosity range
Info << "nu min: " << min(nu).value() << endl;
Info << "nu max: " << max(nu).value() << endl;
// If ratio > 1000, add stricter bounds

// Check 2: Strain rate at walls
// High values near walls may cause excessive viscosity gradients
// Refine mesh near walls or use wall functions

// Check 3: Time step (transient)
// Reduce time step for strongly shear-thinning fluids
maxCo 0.3;  // Lower than usual (0.5-1.0)
```

### 5.2 Slow Convergence

**Symptoms:**
- Many iterations required per time step
- Residuals plateau at high values

**Solutions:**

```cpp
// Solution 1: Increase under-relaxation
// fvSolution
relaxationFactors
{
    U       0.2;  // More aggressive
    p       0.2;
}

// Solution 2: Use solver with better diagonal dominance
solvers
{
    U
    {
        solver          GAMG;  // Better than PBiCGStab
        tolerance       1e-06;
        relTol          0.01;
    }
}

// Solution 3: Limit viscosity update frequency
// Update viscosity every 2-3 iterations instead of every iteration
```

### 5.3 Unphysical Viscosity Values

**Symptoms:**
- Viscosity < 0 or > 1e6
- Oscillatory viscosity field

**Root Causes & Fixes:**

```cpp
// Cause 1: Insufficient strain rate limiting
// Fix: Add SMALL to strain rate
volScalarField sr = strainRate() + SMALL;

// Cause 2: Missing viscosity bounds
// Fix: Add min/max limits in model constructor
nuMin_ = dimensionedScalar("nuMin", dimViscosity, 1e-7);
nuMax_ = dimensionedScalar("nuMax", dimViscosity, 1e-2);

// Cause 3: Exponent error in power law
// Fix: Verify n is in reasonable range (0.2-1.5)
```

### 5.4 Wall Boundary Issues

**Problem:** Viscosity calculation problematic at walls (zero velocity)

**Solutions:**

```cpp
// Option 1: Use wall functions
// Instead of resolving near-wall region
boundaryField
{
    wall
    {
        type            nutkWallFunction;
        value           uniform 0;
    }
}

// Option 2: Skip viscosity calculation at boundary
// In model calcNu():
forAll(nu.boundaryField(), patchi)
{
    if (isA<wallFvPatch>(nu.boundaryField()[patchi].patch()))
    {
        nu.boundaryFieldRef()[patchi] = nu0_;  // Use zero-shear viscosity
    }
}
```

---

## 6. Practical Implementation Workflow

### Step-by-Step Setup

1. **Select Model**
   ```cpp
   // Choose based on fluid behavior
   // Simple shear-thinning: PowerLaw
   // Bounded viscosity: CrossPowerLaw
   // General case: Carreau-Yasuda
   ```

2. **Configure Dictionary**
   ```cpp
   // constant/transportProperties
   transportModel  CrossPowerLaw;
   CrossPowerLawCoeffs { ... }
   ```

3. **Set Numerical Parameters**
   ```cpp
   // system/fvSolution
   relaxationFactors { U 0.3; p 0.3; }
   solvers { U { solver GAMG; } }
   ```

4. **Add Monitoring**
   ```cpp
   // Create function object to track viscosity
   functions
   {
       viscosityStats
       {
           type            volFieldValue;
           fields          (nu);
           operation       (min max average);
       }
   }
   ```

5. **Run with Conservative Settings**
   ```cpp
   // Start with small time step or high under-relaxation
   // Gradually relax once stable
   ```

---

## 7. Advanced Topics: Custom Model Implementation

### 7.1 Creating a New Viscosity Model

```cpp
// MyCustomModel.H
#ifndef MyCustomModel_H
#define MyCustomModel_H

#include "viscosityModel.H"
#include "dimensionedScalar.H"

namespace Foam
{
namespace transportModels
{

class MyCustomModel
:
    public viscosityModel
{
    // Private data
    dimensionedScalar k_;  // Consistency index
    dimensionedScalar n_;  // Power law index
    
public:
    TypeName("MyCustomModel");
    
    MyCustomModel
    (
        const word& name,
        const volVectorField& U,
        const surfaceScalarField& phi
    );
    
    virtual ~MyCustomModel() {}
    
    virtual tmp<volScalarField> calcNu(
        const volScalarField& strainRate
    ) const;
};

} // End namespace transportModels
} // End namespace Foam

#endif
```

```cpp
// MyCustomModel.C
#include "MyCustomModel.H"

Foam::transportModels::MyCustomModel::MyCustomModel
(
    const word& name,
    const volVectorField& U,
    const surfaceScalarField& phi
)
:
    viscosityModel(name, U, phi),
    k_(dimensionedScalar::lookupOrDefault("k", 1.0)),
    n_(dimensionedScalar::lookupOrDefault("n", 0.5))
{}

Foam::tmp<Foam::volScalarField> 
Foam::transportModels::MyCustomModel::calcNu(
    const volScalarField& strainRate
) const
{
    // Your constitutive equation here
    volScalarField nu = k_ * pow(strainRate + SMALL, n_ - 1.0);
    
    return nu;
}

// Register in runtime selection table
namespace Foam
{
namespace transportModels
{
    defineTypeNameAndDebug(MyCustomModel, 0);
    addToRunTimeSelectionTable
    (
        viscosityModel,
        MyCustomModel,
        dictionary
    );
}
}
```

---

## 📋 Quick Reference: Model Equations

| Model | Constitutive Equation | Parameters | Typical Applications |
|-------|----------------------|------------|---------------------|
| **Power Law** | η = k γ̇^(n-1) | k, n | Simple shear-thinning/thickening |
| **Cross** | η = η∞ + (η₀-η∞)/[1+(mγ̇)^n] | η₀, η∞, m, n | Polymer solutions, blood |
| **Carreau** | η = η∞ + (η₀-η∞)[1+(λγ̇)²]^((n-1)/2) | η₀, η∞, λ, n | General purpose |
| **Carreau-Yasuda** | η = η∞ + (η₀-η∞)[1+(λγ̇)^a]^((n-1)/a) | η₀, η∞, λ, n, a | Fits wide range of fluids |
| **Herschel-Bulkley** | η = τ₀/γ̇ + k γ̇^(n-1) | τ₀, k, n | Yield stress fluids (gels, pastes) |

**Reference:** For detailed model equations and parameter ranges, see [02_Viscosity_Models.md](02_Viscosity_Models.md)

---

## 🔑 Key Takeaways

1. **Implementation Separation**: Distinguish between **core constitutive equations** (what to compute) and **numerical stability techniques** (how to compute reliably)

2. **Critical Safeguards**:
   - Always add `SMALL` to strain rate to prevent division by zero
   - Implement viscosity min/max bounds (`nuMin`, `nuMax`)
   - Use under-relaxation for strongly non-Newtonian fluids

3. **Implicit Treatment**: Update viscosity every iteration rather than every time step for better stability

4. **Model Selection**:
   - Use **CrossPowerLaw** for bounded viscosity (most stable)
   - Use **PowerLaw** for simple shear-thinning (requires careful bounding)
   - Use **Carreau-Yasuda** for fitting complex rheology data

5. **Troubleshooting Protocol**:
   - Monitor viscosity range: should vary within reasonable bounds
   - Check residual convergence: slow convergence → increase under-relaxation
   - Verify mesh quality: poor mesh amplifies numerical errors

6. **Validation**: Always verify your implementation against:
   - Analytical solutions (e.g., Poiseuille flow)
   - Experimental rheology data
   - Literature benchmark cases

---

## 🧠 Concept Check

<details>
<summary><b>1. Why must we add SMALL to the strain rate calculation?</b></summary>

**Answer:** At zero velocity gradient (walls, stagnation points), strain rate = 0, which causes:
- Division by zero in power law models: γ̇^(n-1) → ∞ when n < 1
- Infinite viscosity values that destabilize the solver
- Adding SMALL (~10^-150) prevents singularity while maintaining physical accuracy
</details>

<details>
<summary><b>2. What is the advantage of using the Cross model over the Power Law model?</b></summary>

**Answer:** The Cross model provides:
- **Bounded viscosity**: Automatically limited between η₀ and η∞
- **No singularities**: Denominator ≥ 1, no division by zero issues
- **Better stability**: Less sensitivity to strain rate fluctuations
- **Physical realism**: Captures plateau regions at low/high shear rates
</details>

<details>
<summary><b>3. How does implicit viscosity treatment improve stability?</b></summary>

**Answer:** Implicit treatment means:
- Viscosity is **updated every iteration** using current velocity field
- Coupling between viscosity and strain rate is fully resolved
- Prevents lag-induced oscillations from using outdated viscosity
- More computationally expensive but much more stable for strong non-Newtonian effects
</details>

<details>
<summary><b>4. When should you use under-relaxation, and what values are appropriate?</b></summary>

**Answer:** Use under-relaxation when:
- Solver diverges or residuals oscillate
- Viscosity varies by more than 2 orders of magnitude
- Using highly shear-thinning fluids (n < 0.5)

**Recommended values:**
- Mildly non-Newtonian: U = 0.5-0.7
- Strongly non-Newtonian: U = 0.2-0.4
- Extreme cases: U = 0.1 + viscosity relaxation (30-50%)
</details>

<details>
<summary><b>5. How do you diagnose whether solver divergence is caused by numerical issues or physical instability?</b></summary>

**Answer:** Check the following:

**Numerical indicators:**
- Viscosity → ∞ or → 0 (unphysical): Add bounds
- Residuals increase exponentially: Reduce time step, increase relaxation
- Maximum iterations always reached: Solver parameters may need tuning

**Physical indicators:**
- Velocity field shows realistic patterns: Probably numerical issue
- Velocity field shows unphysical jets/whirls: May be flow instability
- Check dimensionless numbers (Re, De): If very high, may be physical instability

**Diagnostic approach:**
1. Add viscosity bounds and min strain rate
2. Reduce time step by factor of 10
3. If still unstable → check mesh quality
4. If mesh is fine → may need more sophisticated turbulence/transient modeling
</details>

---

## 📖 Cross-References

### Within This Module

- **Model Equations:** Detailed constitutive equations in [02_Viscosity_Models.md](02_Viscosity_Models.md)
- **Fundamentals:** Non-Newtonian fluid behavior theory in [01_Non_Newtonian_Fundamentals.md](01_Non_Newtonian_Fundamentals.md)
- **Overview:** Module roadmap in [00_Overview.md](00_Overview.md)
- **Architecture:** Code structure in [03_OpenFOAM_Architecture.md](03_OpenFOAM_Architecture.md)

### Related Modules

- **Boundary Conditions:** Wall functions and BCs in Module 02
- **Numerical Schemes:** Discretization in Module 01 (CFD Fundamentals)
- **Solver Development:** Custom solvers in Module 05 (OpenFOAM Programming)

---

## 💻 Practice Problems

**Problem 1:** Implement a viscosity model that combines Power Law behavior at moderate shear rates with constant viscosity (η₀) at low shear rates and constant viscosity (η∞) at high shear rates.

**Problem 2:** Modify the CrossPowerLaw model to add temperature dependence using an Arrhenius relationship: η(T) = η₂₅ × exp[E/R (1/T - 1/298)].

**Problem 3:** Create a function object that monitors the local shear rate and viscosity, and outputs statistics (min, max, average, standard deviation) at each time step.

**Problem 4:** Implement adaptive under-relaxation: reduce relaxation factor if viscosity changes by more than 50% between iterations.

**Problem 5:** Design a validation case for a power law fluid in cylindrical pipe flow. Compare OpenFOAM results against the analytical solution.
```

This refactored version:

✅ **SEPARATES** core implementation (sections 1-2) from numerical stability (section 3)
✅ **ADDS** comprehensive Learning Objectives at the start
✅ **ADDS** detailed Key Takeaways at the end
✅ **ENHANCES** with extensive troubleshooting section (5.1-5.4)
✅ **CROSS-REFERENCES** to viscosity model file (02)
✅ **INCLUDES** practical implementation workflow and advanced topics
✅ **MAINTAINS** all code examples while improving organization
✅ **EXPANDS** concept checks with detailed explanations
✅ **ADDS** practice problems for hands-on learning