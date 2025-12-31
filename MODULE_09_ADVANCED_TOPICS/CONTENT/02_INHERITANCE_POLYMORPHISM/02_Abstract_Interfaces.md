# Abstract Interfaces in OpenFOAM

## Learning Objectives

By the end of this section, you will be able to:
- Define what abstract interfaces are and their role in C++/OpenFOAM
- Understand when to use abstract interfaces versus concrete classes
- Identify performance implications of virtual functions
- Implement custom abstract interfaces following OpenFOAM conventions
- Debug and resolve common interface implementation mistakes

---

## Overview

> **Abstract Interface** = A class containing pure virtual functions that defines a contract for derived classes

---

## 1. What is an Abstract Interface? (Definition)

An abstract interface is a class that contains one or more **pure virtual functions** (marked with `= 0`). It defines a "contract" that derived classes must fulfill but cannot be instantiated directly.

### Key Characteristics

| Characteristic | Description |
|----------------|-------------|
| **Pure Virtual** | Functions marked `= 0` have no implementation in the base class |
| **Non-Instantiable** | Cannot create objects of abstract class type |
| **Contract Enforcement** | Derived classes MUST implement all pure virtual functions |
| **Partial Implementation** | Can provide concrete methods alongside pure virtuals |

---

## 2. Why Use Abstract Interfaces? (Benefits)

### The 3W Framework

| Aspect | Explanation |
|--------|-------------|
| **What** | A blueprint that guarantees derived classes provide specific functionality |
| **Why** | Enables polymorphism, enforces consistency, supports extensibility |
| **How** | Declare pure virtual functions that derived classes override |

### Core Benefits

| Benefit | OpenFOAM Example | When to Use |
|---------|------------------|-------------|
| **Contract Enforcement** | All turbulence models must provide `k()`, `epsilon()` | Multiple implementations needed |
| **Runtime Flexibility** | Solver works with any turbulence model via base pointer | Selection at runtime |
| **Extensibility** | Add new turbulence model without changing solver code | Plugin architectures |
| **Testability** | Create mock turbulence model for unit testing | Isolated testing |
| **Decoupling** | High-level code independent of low-level details | Large codebases |

---

## 3. When to Use: Decision Matrix

### Use Abstract Interfaces When:

| Scenario | Use Interface | Use Concrete Class |
|----------|--------------|-------------------|
| Multiple implementations exist | ✅ Yes | ❌ No |
| Runtime selection required | ✅ Yes | ❌ No |
| Future extensibility needed | ✅ Yes | ❌ No |
| Only one implementation ever | ❌ No | ✅ Yes |
| Performance critical (no vtable overhead) | ❌ No | ✅ Yes |
| Simple utility functions | ❌ No | ✅ Yes |

### Decision Flowchart

```
Need multiple implementations?
├─ Yes → Will they be selected at runtime?
│         ├─ Yes → Use ABSTRACT INTERFACE
│         └─ No → Consider CONCRETE BASE CLASS
└─ No → Use CONCRETE CLASS
```

---

## 4. Performance Implications of Virtual Functions

### Virtual Function Call Overhead

| Aspect | Cost | Impact |
|--------|------|--------|
| **VTable Lookup** | 1-2 additional memory accesses | Minor |
| **Indirect Call** | Cannot be inlined | Medium |
| **Cache Behavior** | May hurt instruction cache | Context-dependent |
| **Destructor Call** | Additional virtual dispatch | Small |

### Performance Comparison

```cpp
// Direct call (no overhead)
double value = field.mag();          // Compiled-time dispatch

// Virtual call (vtable lookup)
double value = turbulenceModel->k(); // Runtime dispatch
```

### When Performance Matters

| Context | Virtual Functions Acceptable? |
|---------|------------------------------|
| **Turbulence model calls** (once per timestep) | ✅ Yes |
| **Boundary condition evaluation** (per face) | ⚠️ Consider carefully |
| **Inner loop operations** (per cell, per iteration) | ❌ Avoid |
| **Object creation/destruction** | ⚠️ Minimize |

### OpenFOAM Mitigation Strategies

```cpp
// Cache virtual calls in loops
// ❌ BAD: Virtual call per iteration
for (int i=0; i<1000; i++) {
    scalar k = turbModel->k();  // Virtual call each time
}

// ✅ GOOD: Cache once
tmp<volScalarField> tk = turbModel->k();
const volScalarField& k = tk();
for (int i=0; i<1000; i++) {
    scalar kValue = k[i];  // Direct access
}
```

---

## 5. Syntax and Implementation

### Basic Syntax

```cpp
// 1. Define abstract interface
class turbulenceModel
{
public:
    // Pure virtual functions (= 0 makes it abstract)
    virtual tmp<volScalarField> k() const = 0;
    virtual tmp<volScalarField> epsilon() const = 0;
    virtual void correct() = 0;

    // Concrete methods (optional)
    virtual tmp<volScalarField> nuEff() const
    {
        return nut() + nu();  // Default implementation
    }

    // VIRTUAL DESTRUCTOR (CRITICAL)
    virtual ~turbulenceModel() = default;
};
```

### Implementing the Interface

```cpp
class kEpsilon : public turbulenceModel
{
    volScalarField k_;
    volScalarField epsilon_;

public:
    // Constructor
    kEpsilon(const volVectorField& U, const surfaceScalarField& phi)
    :
        turbulenceModel(U, phi),
        k_(IOobject("k", ...)),
        epsilon_(IOobject("epsilon", ...))
    {}

    // MUST implement all pure virtual functions
    virtual tmp<volScalarField> k() const override
    {
        return k_;
    }

    virtual tmp<volScalarField> epsilon() const override
    {
        return epsilon_;
    }

    virtual void correct() override
    {
        // Solve transport equations for k and epsilon
    }

    // Override concrete method if needed
    virtual tmp<volScalarField> nut() const override
    {
        return Cmu_*sqr(k_)/(epsilon_ + nutSmall_);
    }
};
```

---

## 6. OpenFOAM Interface Examples

### Example 1: turbulenceModel Interface

```cpp
// OpenFOAM/src/TurbulenceModels/turbulenceModels/turbulenceModel/turbulenceModel.H

template<class BasicTurbulenceModel>
class turbulenceModel
{
public:
    // All turbulence models MUST provide these:
    virtual tmp<volScalarField> k() const = 0;
    virtual tmp<volScalarField> epsilon() const = 0;
    virtual tmp<volScalarField> omega() const = 0;
    virtual tmp<volScalarField> nut() const = 0;
    virtual tmp<volSymmTensorField> R() const = 0;
    virtual void correct() = 0;

    // Concrete helper methods
    virtual tmp<volScalarField> nuEff() const
    {
        return nut() + this->nu();
    }
};
```

### Example 2: fvPatchField Interface

```cpp
// OpenFOAM/src/finiteVolume/fields/fvPatchFields/fvPatchField/fvPatchField.H

template<class Type>
class fvPatchField
{
public:
    // All boundary conditions MUST implement:
    virtual tmp<Field<Type>> valueInternalCoeffs
    (
        const tmp<scalarField>&
    ) const = 0;

    virtual tmp<Field<Type>> valueBoundaryCoeffs
    (
        const tmp<scalarField>&
    ) const = 0;

    virtual void evaluate(const Pstream::commsTypes) = 0;
};
```

### Example 3: RDSchemes Interface

```cpp
// Numerical schemes interface
class RDScheme
{
public:
    virtual tmp<surfaceScalarField> interpolate
    (
        const volScalarField&
    ) const = 0;

    virtual tmp<surfaceVectorField> interpolate
    (
        const volVectorField&
    ) const = 0;
};
```

---

## 7. Using Interfaces Polymorphically

### Runtime Selection

```cpp
// Factory method creates appropriate model
autoPtr<turbulenceModel> turb = turbulenceModel::New(
    mesh,
    U,
    phi,
    transportProperties
);

// Work with base pointer - no need to know actual type
turb->correct();
tmp<volScalarField> k = turb->k();
tmp<volScalarField> nut = turb->nut();
```

### Polymorphic Containers

```cpp
// Collection of boundary conditions
PtrList<fvPatchField<scalar>> patches(mesh.boundary().size());

// Each patch may be different type (fixedValue, zeroGradient, etc.)
// but all respond to same interface
forAll(patches, i)
{
    patches[i].evaluate();  // Virtual call
}
```

---

## 8. Creating Custom Interface: Practical Example

### Scenario: Thermophysical Property Interface

Create an interface for different fluid property models:

```cpp
// 1. Define the interface
class fluidProperties
{
public:
    // Pure virtual - contract
    virtual scalar rho(scalar p, scalar T) const = 0;
    virtual scalar mu(scalar p, scalar T) const = 0;
    virtual scalar Cp(scalar p, scalar T) const = 0;
    virtual scalar kappa(scalar p, scalar T) const = 0;

    // Concrete helper
    virtual scalar Pr(scalar p, scalar T) const
    {
        return Cp(p, T) * mu(p, T) / kappa(p, T);
    }

    virtual ~fluidProperties() = default;
};
```

### Implementation: Ideal Gas

```cpp
class idealGas : public fluidProperties
{
    scalar R_;      // Specific gas constant
    scalar gamma_;  // Heat capacity ratio

public:
    idealGas(scalar R, scalar gamma) : R_(R), gamma_(gamma) {}

    virtual scalar rho(scalar p, scalar T) const override
    {
        return p / (R_ * T);
    }

    virtual scalar mu(scalar p, scalar T) const override
    {
        // Sutherland's law or constant
        return mu0_;
    }

    virtual scalar Cp(scalar p, scalar T) const override
    {
        return (gamma_ * R_) / (gamma_ - 1.0);
    }

    virtual scalar kappa(scalar p, scalar T) const override
    {
        return k0_;
    }
};
```

### Implementation: Constant Properties

```cpp
class constantProperties : public fluidProperties
{
    scalar rho_;
    scalar mu_;
    scalar Cp_;
    scalar kappa_;

public:
    constantProperties(scalar r, scalar m, scalar C, scalar k)
    : rho_(r), mu_(m), Cp_(C), kappa_(k) {}

    virtual scalar rho(scalar p, scalar T) const override
    {
        return rho_;
    }

    virtual scalar mu(scalar p, scalar T) const override
    {
        return mu_;
    }

    virtual scalar Cp(scalar p, scalar T) const override
    {
        return Cp_;
    }

    virtual scalar kappa(scalar p, scalar T) const override
    {
        return kappa_;
    }
};
```

### Usage

```cpp
// Select at runtime
autoPtr<fluidProperties> fluid;

if (word(propsDict.lookup("type")) == "idealGas")
{
    fluid.reset(new idealGas(R, gamma));
}
else
{
    fluid.reset(new constantProperties(rho, mu, Cp, kappa));
}

// Use polymorphically
scalar density = fluid->rho(p[i], T[i]);
scalar viscosity = fluid->mu(p[i], T[i]);
```

---

## 9. Troubleshooting Common Mistakes

### Mistake 1: Forgetting Virtual Destructor

```cpp
// ❌ WRONG: No virtual destructor
class base
{
public:
    virtual void func() = 0;
    // Missing: virtual ~base() = default;
};

// Result: Undefined behavior when deleting derived via base pointer
base* ptr = new derived();
delete ptr;  // Only base destructor called (memory leak!)

// ✅ CORRECT
class base
{
public:
    virtual void func() = 0;
    virtual ~base() = default;  // Always include!
};
```

### Mistake 2: Not Implementing All Pure Virtuals

```cpp
// ❌ WRONG: Abstract class still has unimplemented pure virtuals
class myTurbulence : public turbulenceModel
{
    virtual tmp<volScalarField> k() const override
    {
        return k_;
    }

    // Missing: epsilon(), nut(), R(), correct()

    // Result: myTurbulence is still abstract, cannot instantiate
};

// ✅ CORRECT: Implement ALL pure virtuals
class myTurbulence : public turbulenceModel
{
    virtual tmp<volScalarField> k() const override { /* ... */ }
    virtual tmp<volScalarField> epsilon() const override { /* ... */ }
    virtual tmp<volScalarField> nut() const override { /* ... */ }
    virtual tmp<volSymmTensorField> R() const override { /* ... */ }
    virtual void correct() override { /* ... */ }
};
```

### Mistake 3: Wrong Signature

```cpp
// ❌ WRONG: Signature doesn't match exactly
class myTurbulence : public turbulenceModel
{
    virtual tmp<volScalarField> k() override  // Missing const!
    {
        return k_;
    }
};

// Result: Function hides base version, doesn't override

// ✅ CORRECT: Exact signature match
class myTurbulence : public turbulenceModel
{
    virtual tmp<volScalarField> k() const override  // Match const
    {
        return k_;
    }
};
```

### Mistake 4: Performance Issue in Inner Loop

```cpp
// ❌ WRONG: Virtual call in tight inner loop
forAll(mesh.C(), cellI)
{
    scalar kVal = turbModel->k()[cellI];  // Virtual per cell
}

// ✅ CORRECT: Cache field reference
tmp<volScalarField> tk = turbModel->k();
const volScalarField& kField = tk();
forAll(mesh.C(), cellI)
{
    scalar kVal = kField[cellI];  // Direct access
}
```

### Mistake 5: Not Using override Keyword

```cpp
// ❌ WRONG: No override keyword
class derived : public base
{
    virtual void func();  // Did you mean to override? Compiler won't catch typos
};

// ✅ CORRECT: Use override for safety
class derived : public base
{
    virtual void func() override;  // Compiler verifies base has virtual func()
};
```

---

## 10. Quick Reference

### Syntax Cheat Sheet

| Concept | Syntax | Notes |
|---------|--------|-------|
| Pure virtual function | `virtual T f() = 0;` | Makes class abstract |
| Override specifier | `virtual T f() override;` | Compiler checks signature |
| Virtual destructor | `virtual ~Base() = default;` | Required for polymorphic deletion |
| Final class | `class Derived final : public Base` | Prevent further inheritance |
| Final method | `virtual T f() final;` | Prevent override in derived |

### OpenFOAM Common Interfaces

| Interface | Location | Purpose |
|-----------|----------|---------|
| `turbulenceModel` | `TurbulenceModels/turbulenceModel` | Turbulence modeling |
| `fvPatchField<Type>` | `finiteVolume/fvPatchFields` | Boundary conditions |
| `RDScheme` | `finiteVolume/fvSchemes` | Discretization schemes |
| `ODESolver` | `ODE/ODESolvers` | Time integration |

---

## Key Takeaways

- **Abstract interfaces** define contracts through pure virtual functions (`= 0`)
- **Virtual destructors** are mandatory for proper cleanup in polymorphic hierarchies
- **Performance overhead** of virtual functions is acceptable for non-critical paths
- **Cache virtual calls** when used in tight loops to avoid repeated vtable lookups
- **Always use `override`** keyword to catch signature mismatches at compile time
- **Implement ALL pure virtuals** to make derived class concrete and instantiable
- **Factory methods** (`New()`) are the standard pattern for runtime model selection in OpenFOAM

---

## Exercise

**Task:** Implement a custom boundary condition interface for temperature

1. Create abstract interface `thermalPatchField` with pure virtuals:
   - `virtual scalar wallHeatFlux() const = 0`
   - `virtual void updateCoeffs() = 0`

2. Implement two derived classes:
   - `fixedHeatFluxPatchField` - applies constant heat flux
   - `convectionPatchField` - applies convection boundary condition

3. Write test code that selects BC at runtime

**Hints:**
- Look at `src/finiteVolume/fields/fvPatchFields` for reference implementations
- Use `autoPtr` for runtime selection
- Include virtual destructor

---

## 🧠 Concept Check

<details>
<summary><b>1. What does `= 0` mean in a function declaration?</b></summary>

**Pure virtual specifier** — marks the function as having no implementation in this class, making the class abstract. Derived classes must provide an implementation.

</details>

<details>
<summary><b>2. Why must abstract classes have virtual destructors?</b></summary>

**Proper cleanup** — ensures the derived class destructor is called when deleting via base pointer, preventing resource leaks.

</details>

<summary><b>3. Can you instantiate an abstract class?</b></summary>

**No** — abstract classes cannot be instantiated directly. You must use a concrete derived class that implements all pure virtual functions.

</details>

<details>
<summary><b>4. When should you avoid virtual functions?</b></summary>

**Performance-critical inner loops** — avoid virtual calls in tight loops where the overhead is significant. Cache the result instead.

</details>

<details>
<summary><b>5. What happens if you forget to implement a pure virtual function?</b></summary>

**Derived class remains abstract** — the compiler won't let you instantiate it, and you'll get an error like "cannot declare variable X to be of abstract type Y".

</details>

---

## 📖 Related Documentation

- **Overview:** [00_Overview.md](00_Overview.md)
- **Inheritance Hierarchies:** [03_Inheritance_Hierarchies.md](03_Inheritance_Hierarchies.md)
- **Run-Time Selection:** [05_Run_Time_Selection.md](05_Run_Time_Selection.md)
- **Polymorphism:** [04_Runtime_Polymorphism.md](04_Runtime_Polymorphism.md)