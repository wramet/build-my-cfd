# Inheritance Hierarchies in OpenFOAM

ลำดับชั้นการสืบทอดใน OpenFOAM

---

## 📚 Learning Objectives

By the end of this section, you will be able to:

- **Identify** the three-tier structure of OpenFOAM inheritance hierarchies (base → intermediate → concrete)
- **Apply** the Liskov Substitution Principle when designing new physics models
- **Implement** the TypeName macro correctly for run-time type identification
- **Recognize** common anti-patterns that lead to brittle, unmaintainable code
- **Design** extensible class hierarchies following OpenFOAM conventions

**Prerequisites:** Basic C++ inheritance, virtual functions (from 01_Introduction.md)

---

## Overview

> **Inheritance hierarchies** enable OpenFOAM to support hundreds of turbulence models, boundary conditions, and numerical schemes through a unified interface.

### The 3W Framework

| Aspect | Description |
|--------|-------------|
| **What** | A multi-level inheritance structure where abstract base classes define interfaces, intermediate classes share common implementations, and concrete classes provide specific physics models |
| **Why** | Eliminates code duplication, enables plug-and-play model selection via dictionaries, and maintains consistent interfaces across all derived classes |
| **How** | Use pure virtual functions in base classes, template-based intermediate classes for code reuse, and leaf classes with TypeName macros for run-time selection |

---

## 1. OpenFOAM's Three-Tier Hierarchy Pattern

OpenFOAM consistently uses a **three-level inheritance structure**:

```
┌─────────────────────────────────────────────────────────┐
│                   ABSTRACT BASE CLASS                    │
│  Purpose: Define interface (pure virtual functions)     │
│  Example: turbulenceModel, fvPatchField                 │
└──────────────────────┬──────────────────────────────────┘
                       │ inherits
                       ▼
┌─────────────────────────────────────────────────────────┐
│              INTERMEDIATE CLASSES                        │
│  Purpose: Share common code among related models        │
│  Example: eddyViscosity, RASModel, LESModel            │
└──────────────────────┬──────────────────────────────────┘
                       │ inherits
                       ▼
┌─────────────────────────────────────────────────────────┐
│               CONCRETE (LEAF) CLASSES                    │
│  Purpose: Specific physics implementation               │
│  Example: kEpsilon, kOmegaSST, Smagorinsky             │
└─────────────────────────────────────────────────────────┘
```

### Level Comparison Table

| Level | Role | Contains | Example |
|-------|------|----------|---------|
| **Base** | Interface definition | Pure virtual functions, protected data | `turbulenceModel` |
| **Intermediate** | Code reuse | Partial implementations, templates | `eddyViscosity<RASModel>` |
| **Leaf** | Specific model | Complete implementations, TypeName | `kEpsilon` |

---

## 2. Real-World Example: Turbulence Model Hierarchy

### Hierarchy Diagram

```mermaid
flowchart TD
    A[turbulenceModel<br/>{Abstract Base}] --> B[RASModel<br/>{Intermediate}]
    A --> C[LESModel<br/>{Intermediate}]
    A --> D[DESModel<br/>{Intermediate}]
    B --> E[eddyViscosity<br/>{Intermediate}]
    E --> F[kEpsilon<br/>{Concrete}]
    E --> G[kOmegaSST<br/>{Concrete}]
    E --> H[SpalartAllmaras<br/]{Concrete}
    C --> I[Smagorinsky<br/>{Concrete}]
    C --> J[WALE<br/>{Concrete}]
    
    style A fill:#e1f5ff
    style B fill:#fff4e1
    style C fill:#fff4e1
    style D fill:#fff4e1
    style E fill:#fff4e1
    style F fill:#e8f5e9
    style G fill:#e8f5e9
    style H fill:#e8f5e9
    style I fill:#e8f5e9
    style J fill:#e8f5e9
```

### UML Class Diagram

![Turbulence Model Hierarchy](../../images/img_09_002.jpg)

> **Figure 1:** UML class diagram showing the complete turbulence model inheritance hierarchy. The diagram illustrates how abstract base classes (`turbulenceModel`) provide the interface foundation, intermediate classes (`eddyViscosity`, `RASModel`) share common implementations, and concrete leaf classes (`kEpsilon`, `kOmegaSST`) deliver specific physics models.

---

## 3. Base Class: Interface Definition

**Purpose:** Define the contract that all turbulence models must fulfill.

```cpp
// File: turbulenceModel.H
class turbulenceModel
{
protected:
    // Common data for ALL turbulence models
    const volVectorField& U_;        // Velocity field
    const surfaceScalarField& phi_;  // Flux field
    const dictionary& dict_;          // Model dictionary

public:
    // WHAT: Run-time type identification macro
    // WHY: Enables selection from dictionary
    TypeName("turbulenceModel");

    // Pure virtual interface - MUST be implemented by derived classes
    virtual tmp<volScalarField> k() const = 0;
    virtual tmp<volScalarField> epsilon() const = 0;
    virtual tmp<volScalarField> omega() const = 0;
    virtual tmp<volScalarField> nuEff() const = 0;
    virtual tmp<volSymmTensorField> R() const = 0;
    virtual void correct() = 0;
    
    // Virtual destructor - CRITICAL for polymorphic deletion
    virtual ~turbulenceModel() = default;
};
```

**Key Design Points:**
- **Protected data:** Accessible to derived classes, hidden from users
- **Pure virtual (`= 0`):** Forces derived classes to implement
- **Virtual destructor:** Prevents memory leaks when deleting via base pointer

---

## 4. Intermediate Classes: Code Reuse

**Purpose:** Share implementations common to groups of related models.

### 4.1 RAS/LES Level (Template Parameter)

```cpp
// File: RASModel.H
template<class BasicTurbulenceModel>
class RASModel : public BasicTurbulenceModel
{
protected:
    // RAS-specific coefficients
    dimensionedScalar sigmaEpsilon_;
    dimensionedScalar Cmu_;

public:
    TypeName("RASModel");
    
    // Common RAS calculations
    virtual tmp<volScalarField> R() const;
};
```

### 4.2 Eddy Viscosity Level (Shared Implementation)

```cpp
// File: eddyViscosity.H
template<class BasicTurbulenceModel>
class eddyViscosity : public BasicTurbulenceModel
{
protected:
    // Shared by ALL eddy viscosity models
    volScalarField nut_;  // Turbulent viscosity
    
public:
    TypeName("eddyViscosity");
    
    // SHARED IMPLEMENTATION - not pure virtual!
    virtual tmp<volScalarField> nuEff() const
    {
        // Effective viscosity = laminar + turbulent
        return tmp<volScalarField>
        (
            new volScalarField
            (
                IOobject::groupName("nuEff", this->U_.group()),
                this->nut_ + this->nu()
            )
        );
    }
    
    // Derived classes MUST implement these
    virtual tmp<volScalarField> k() const = 0;
    virtual tmp<volScalarField> epsilon() const = 0;
    virtual void correct() = 0;
};
```

**Why Intermediate Classes?**
- Single implementation of `nuEff()` shared by kEpsilon, kOmegaSST, SpalartAllmaras, etc.
- Changes propagate automatically to all derived models
- Reduces code duplication by ~70% in turbulence library

---

## 5. Concrete Classes: Specific Implementation

**Purpose:** Complete implementation with specific transport equations.

```cpp
// File: kEpsilon.H
template<class BasicTurbulenceModel>
class kEpsilon 
:
    public eddyViscosity<RASModel<BasicTurbulenceModel>>
{
    // Model-specific fields
    volScalarField k_;
    volScalarField epsilon_;
    
    // Model coefficients
    dimensionedScalar Cmu_;
    dimensionedScalar C1_;
    dimensionedScalar C2_;
    dimensionedScalar sigmaEpsilon_;
    
public:
    TypeName("kEpsilon");  // Registers class for run-time selection
    
    // Constructor
    kEpsilon
    (
        const volScalarField& rho,
        const volVectorField& U,
        const surfaceScalarField& phi,
        const typename BasicTurbulenceModel::transportModel& transport
    );
    
    // Implementation of pure virtual functions
    virtual tmp<volScalarField> k() const { return k_; }
    virtual tmp<volScalarField> epsilon() const { return epsilon_; }
    virtual void correct();  // Solves k and epsilon transport equations
};
```

### Dictionary Selection (Result of TypeName)

```cpp
// In turbulenceProperties dictionary
simulationType  RAS;

RAS
{
    RASModel        kEpsilon;  // ← Uses TypeName "kEpsilon"
    
    turbulence      on;
    
    kEpsilonCoeffs
    {
        Cmu             0.09;
        C1              1.44;
        C2              1.92;
        sigmaEpsilon    1.3;
    }
}
```

---

## 6. The TypeName Macro: Deep Dive

### What TypeName Actually Does

The `TypeName("className")` macro expands to code that enables run-time selection:

```cpp
// What you write:
TypeName("kEpsilon");

// What the macro generates (simplified):
class kEpsilon
{
public:
    // 1. Static type name accessor
    static const word& typeName
    {
        static const word name("kEpsilon");
        return name;
    }
    
    // 2. Virtual type name accessor
    virtual const word& type() const { return typeName; }
};
```

### TypeName Requirements

| Requirement | Example | Why It Matters |
|-------------|---------|----------------|
| **Must match class name** | `class kEpsilon` → `TypeName("kEpsilon")` | Dictionary lookup uses this string |
| **Must be unique** | No two classes can have same TypeName | Prevents selection conflicts |
| **Must be in public section** | `public: TypeName(...)` | RTTI system needs access |
| **Required in leaf classes** | Concrete models only | Intermediate classes may not need it |

### Common TypeName Mistakes

❌ **Incorrect:** Typo in TypeName string
```cpp
class kEpsilon
{
public:
    TypeName("kEpslion");  // Typo! Dictionary selection will fail
};
```

✅ **Correct:** Exact match
```cpp
class kEpsilon
{
public:
    TypeName("kEpsilon");  // Matches class name exactly
};
```

---

## 7. Design Principles for Hierarchies

### 7.1 Liskov Substitution Principle (LSP)

**Definition:** You should be able to substitute any derived class for its base class without breaking the program.

**OpenFOAM Example:**
```cpp
// This code should work with ANY turbulenceModel
void solveFlow(turbulenceModel& turb)  // Base class reference
{
    // These calls work for kEpsilon, kOmegaSST, SpalartAllmaras, etc.
    turb.correct();           // Polymorphic call
    scalar ke = turb.k().weightedAverage(mesh.V()).value();
    scalar eps = turb.epsilon().weightedAverage(mesh.V()).value();
}

// Valid substitutions:
kEpsilon keModel(...);
solveFlow(keModel);           // ✅ Works

kOmegaSST sstModel(...);
solveFlow(sstModel);          // ✅ Works

SpalartAllmaras saModel(...);
solveFlow(saModel);           // ✅ Works
```

**LSP Violation Example:**
```cpp
// ❌ BAD: Derived class breaks base class contract
class myCustomModel : public turbulenceModel
{
public:
    virtual void correct() override
    {
        // VIOLATION: Throws exception for certain conditions
        if (mesh_.time().value() > 1000)
        {
            FatalError << "This model doesn't work after t=1000";
        }
        // ... rest of implementation
    }
};

// This breaks LSP - you can't substitute myCustomModel everywhere
```

### 7.2 Open/Closed Principle

- **Open for extension:** Add new turbulence models without modifying existing code
- **Closed for modification:** Base classes (`turbulenceModel`) rarely change

**Example:** Adding a new turbulence model requires:
1. Create new leaf class inheriting from existing hierarchy
2. Implement pure virtual functions
3. Add TypeName macro
4. No changes to existing models ✅

### 7.3 Single Responsibility Principle

Each level has a single, well-defined responsibility:

| Level | Single Responsibility |
|-------|----------------------|
| Base | Define interface only |
| Intermediate | Share specific type of code |
| Leaf | Implement specific physics |

---

## 8. Anti-Patterns to Avoid

### Anti-Pattern 1: Deep Nesting Hell

❌ **Problem:** Too many inheritance levels
```cpp
// BAD: 6+ levels deep
turbulenceModel → RASModel → eddyViscosity → linearEddyViscosity → 
    twoEquationTurbulence → kEpsilon → realizableKE
```

**Issues:**
- Difficult to debug
- Code navigation becomes complex
- Compile times increase dramatically

✅ **Solution:** Keep it shallow (3-4 levels max)
```cpp
// GOOD: 3 levels
turbulenceModel → eddyViscosity<RASModel> → kEpsilon
```

### Anti-Pattern 2: Concrete Base Classes

❌ **Problem:** Base class has implementation
```cpp
// BAD: Base class with implementation
class turbulenceModel
{
public:
    virtual void correct()
    {
        // Default implementation - violates pure virtual purpose
        Info << "Using default turbulence" << endl;
    }
};
```

**Issues:**
- Derived classes may accidentally use incomplete implementation
- Violates "interface-only" purpose of base class

✅ **Solution:** Use pure virtual functions
```cpp
// GOOD: Pure virtual forces implementation
class turbulenceModel
{
public:
    virtual void correct() = 0;  // Must implement
};
```

### Anti-Pattern 3: Diamond Inheritance

❌ **Problem:** Multiple paths to same base
```cpp
// BAD: Diamond structure
    Base
    /    \
   A      B
    \    /
     C
```

**Issues:**
- Ambiguity in function calls
- Multiple copies of Base data

✅ **Solution:** Virtual inheritance (rarely needed in OpenFOAM)
```cpp
// GOOD: Use virtual inheritance if unavoidable
class A : virtual public Base { };
class B : virtual public Base { };
class C : public A, public B { };  // Only one Base subobject
```

### Anti-Pattern 4: God Object Base Class

❌ **Problem:** Base class knows too much
```cpp
// BAD: Base class with all possible fields
class turbulenceModel
{
protected:
    volScalarField k_;
    volScalarField epsilon_;
    volScalarField omega_;
    volScalarField nut_;
    volScalarField nuTilda_;
    volScalarField gamma_;
    volScalarField ReThetat_;
    // ... 20+ fields that not all models need
};
```

**Issues:**
- Wasted memory for models that don't use certain fields
- Unclear which fields are relevant to which model

✅ **Solution:** Only common data in base
```cpp
// GOOD: Minimal base class
class turbulenceModel
{
protected:
    const volVectorField& U_;      // All models need velocity
    const surfaceScalarField& phi_; // All models need flux
    // Model-specific fields go in derived classes
};
```

---

## 9. Boundary Condition Hierarchy Example

OpenFOAM applies the same hierarchy pattern to boundary conditions:

```cpp
// Level 1: Abstract Base
template<class Type>
class fvPatchField
{
public:
    TypeName("fvPatchField");
    
    virtual tmp<fvPatchField<Type>> clone() const = 0;
    virtual void updateCoeffs() = 0;
};

// Level 2: Intermediate (common behavior)
class fixedValueFvPatchField : public fvPatchField<Type>
{
protected:
    Type value_;  // Shared storage mechanism
    
public:
    TypeName("fixedValueFvPatchField");
    
    // Implementation of updateCoeffs
    virtual void updateCoeffs() { /* common code */ }
};

// Level 3: Specialized intermediate
class uniformFixedValueFvPatchField 
:
    public fixedValueFvPatchField<Type>
{
public:
    TypeName("uniformFixedValueFvPatchField");
};

// Level 4: Concrete (with TypeName for selection)
// (OpenFOAM has many concrete BC classes)
```

### Dictionary Selection for BCs

```cpp
// In 0/U file
boundary
{
    inlet
    {
        type            uniformFixedValue;  // ← TypeName lookup
        value           uniform (10 0 0);
    }
    
    outlet
    {
        type            zeroGradient;       // ← TypeName lookup
    }
    
    walls
    {
        type            noSlip;             // ← TypeName lookup
    }
}
```

---

## 10. Practical Exercise: Design Your Own Hierarchy

### Exercise: Transport Property Hierarchy

Design a three-level hierarchy for fluid properties (viscosity models):

**Requirements:**
1. Base class: `transportModel` with pure virtual `nu()`
2. Intermediate class: `Newtonian` with shared density handling
3. Concrete classes: `constantViscosity`, `temperatureDependent`

<details>
<summary><b>Skeleton Solution</b></summary>

```cpp
// Level 1: Base Class
class transportModel
{
protected:
    const volVectorField& U_;
    
public:
    TypeName("transportModel");
    virtual tmp<volScalarField> nu() const = 0;
    virtual ~transportModel() = default;
};

// Level 2: Intermediate Class
class Newtonian : public transportModel
{
protected:
    volScalarField rho_;  // Shared density field
    
public:
    TypeName("Newtonian");
    
    virtual tmp<volScalarField> nu() const = 0;  // Still pure
};

// Level 3: Concrete Class
class constantViscosity : public Newtonian
{
protected:
    dimensionedScalar nu0_;
    
public:
    TypeName("constantViscosity");
    
    virtual tmp<volScalarField> nu() const
    {
        return tmp<volScalarField>(nu0_);
    }
};
```

</details>

---

## 📋 Key Takeaways

| Concept | Key Point |
|---------|-----------|
| **Three-tier structure** | Base (interface) → Intermediate (shared code) → Leaf (implementation) |
| **Liskov Substitution** | Any derived class must work wherever base class is expected |
| **TypeName macro** | Enables run-time selection from dictionary; must match class name exactly |
| **Anti-patterns** | Avoid deep nesting, concrete bases, diamond inheritance, god objects |
| **OpenFOAM pattern** | Consistently applied across turbulence, BCs, numerical schemes, etc. |
| **Design principle** | "Open for extension, closed for modification" |

---

## 🧠 Concept Check

<details>
<summary><b>1. What is the primary purpose of an abstract base class in OpenFOAM?</b></summary>

**Interface definition only.** Base classes define pure virtual functions that create a contract. They contain protected data accessible to derived classes but should not contain implementation logic (except possibly virtual destructors).

</details>

<details>
<summary><b>2. Why does OpenFOAM use intermediate template classes like <code>eddyViscosity&lt;RASModel&gt;</code>?</b></summary>

**Code reuse.** Intermediate classes implement functionality shared by multiple derived classes (like `nuEff()` calculation for all eddy-viscosity models). Templates allow the same intermediate class to work with different base types (RAS, LES, DES).

</details>

<summary><b>3. What happens if you mistype the TypeName macro string?</b></summary>

**Run-time selection fails silently.** When you specify the model in a dictionary (e.g., `RASModel kEpsilon;`), OpenFOAM looks up "kEpsilon" in its run-time selection table. If `TypeName("kEpslion")` contains a typo, the lookup fails and you get a "Unknown turbulence model" error, even though the class is compiled.

</details>

<details>
<summary><b>4. How does the Liskov Substitution Principle apply to turbulence models?</b></summary>

**Any turbulenceModel reference can use any concrete model.** Solver code written with `turbulenceModel& turb` works with `kEpsilon`, `kOmegaSST`, `SpalartAllmaras`, or any future model, because all derived classes honor the base class contract (implement all pure virtual functions correctly without throwing unexpected exceptions).

</details>

<details>
<summary><b>5. What is the "Diamond Problem" in inheritance and does OpenFOAM encounter it?</b></summary>

**Diamond problem occurs when a class inherits from two classes that both inherit from the same base,** creating ambiguity. OpenFOAM generally avoids this through careful hierarchy design (single inheritance chains). When multiple inheritance is needed, virtual inheritance can resolve it, but it's rare in OpenFOAM.

</details>

---

## 📖 Related Documentation

- **Module Overview:** [00_Overview.md](00_Overview.md)
- **Introduction:** [01_Introduction.md](01_Introduction.md)
- **Abstract Interfaces:** [02_Abstract_Interfaces.md](02_Abstract_Interfaces.md)
- **Run-Time Selection:** [04_Run_Time_Selection_System.md](04_Run_Time_Selection_System.md)
- **Design Patterns:** [05_Design_Patterns_in_Physics.md](05_Design_Patterns_in_Physics.md)