# Inheritance and Virtual Functions

Inheritance และ Virtual Functions ใน OpenFOAM

---

## 📋 Learning Objectives

After completing this section, you will be able to:

- **Identify** appropriate base classes for different OpenFOAM model types
- **Implement** inheritance hierarchies following OpenFOAM conventions
- **Override** virtual functions correctly with proper syntax
- **Avoid** common pitfalls related to virtual destructors and object slicing
- **Apply** the `virtual`, `override`, and `final` keywords appropriately

---

## 📚 Prerequisites

**Required Knowledge:**

- **C++ Fundamentals:** Classes, objects, constructors, and destructors
- **Pointers and References:** Understanding pointer types and dereferencing
- **Basic OOP Concepts:** Encapsulation and access modifiers (`public`, `private`, `protected`)
- **Function Overloading:** Difference between overloading and overriding
- **OpenFOAM Basics:** Familiarity with Run-Time Selection (RTS) from previous sections

**Recommended Preparation:**

- Review [04_Classes_Objects_and_Pointers.md](04_Classes_Objects_and_Pointers.md)
- Understand [00_Overview.md](00_Overview.md) for module context

---

## 🎯 Key Takeaways

- ✅ **Always declare virtual destructors** in base classes intended for polymorphic use
- ✅ **Use `override` keyword** to catch signature mismatches at compile time
- ✅ **Prefer `final` keyword** when preventing further inheritance
- ✅ **Call base class methods** when extending rather than replacing behavior
- ✅ **Select appropriate base classes** based on functionality, not arbitrary choice

---

## Overview

> Leverage OpenFOAM's **class hierarchy** for extensible model development through inheritance and virtual functions

Inheritance enables code reuse and polymorphic behavior in OpenFOAM. Virtual functions allow derived classes to provide specific implementations while maintaining a common interface through base class pointers. This is fundamental to OpenFOAM's extensibility model.

---

## 1. Base Class Selection

### 1.1 Common Base Classes in OpenFOAM

| Need | Base Class | Header Location | Purpose |
|------|------------|-----------------|---------|
| Turbulence Modeling | `turbulenceModel` | `turbulenceModel.H` | RANS/LES turbulence closures |
| Thermodynamics | `basicThermo` | `basicThermo.H` | Equation of state, heat capacity |
| Boundary Conditions | `fvPatchField` | `fvPatchField.H` | Custom boundary conditions |
| Function Objects | `functionObject` | `functionObject.H` | Runtime data processing/output |
| Finite Volume Schemes | `fvScalarScheme` | `fvSchemes.H` | Discretization schemes |
| Physical Models | `immiscibleIncompressibleTwoPhaseMixture` | `immiscibleIncompressibleTwoPhaseMixture.H` | Multiphase models |

### 1.2 Selection Guidelines

**When choosing a base class, consider:**

1. **Functionality Match:** Does the base class provide the interface you need?
2. **Data Availability:** Does it contain necessary member variables?
3. **Polymorphic Requirements:** Will your class be used through base pointers?
4. **Existing Conventions:** What do similar models in OpenFOAM inherit from?

```cpp
// ✅ Correct: Inherit from appropriate turbulence model
class myKEpsilon : public turbulenceModel
{
    // Inherits all turbulence-related infrastructure
};

// ❌ Wrong: Inheriting from unrelated base
class myKEpsilon : public functionObject  // Doesn't make sense!
{
    // No access to turbulence-specific methods
};
```

---

## 2. Implementation Pattern

### 2.1 Standard Class Declaration

```cpp
#ifndef myModel_H
#define myModel_H

#include "turbulenceModel.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

class myModel
:
    public turbulenceModel
{
    // Private Data
    volScalarField k_;
    volScalarField epsilon_;
    volScalarField nut_;

public:
    // Runtime Type Information
    TypeName("myModel");

    // Constructors
    myModel
    (
        const volVectorField& U,
        const surfaceScalarField& phi,
        const transportModel& transport
    );

    // Destructor - ALWAYS virtual in polymorphic base!
    virtual ~myModel() = default;

    // Member Functions
    virtual tmp<volScalarField> k() const override;
    virtual tmp<volScalarField> epsilon() const override;
    virtual tmp<volScalarField> nuEff() const override;
    virtual void correct() override;
};

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

} // End namespace Foam

#endif

// ************************************************************************* //
```

### 2.2 Key Components Explained

```cpp
// 1. Public inheritance
class myModel : public turbulenceModel
//                ^^^^^^
//                Public inheritance enables polymorphism

// 2. RTS macro - enables runtime selection
TypeName("myModel");
// Registers class in RTS table with name "myModel"

// 3. Virtual destructor
virtual ~myModel() = default;
// ^^^^^^^
// Ensures proper cleanup when deleted via base pointer

// 4. Override specifier
virtual void correct() override;
//                  ^^^^^^^^
// Compiler verifies this actually overrides a base method
```

---

## 3. Virtual vs Override vs Final

### 3.1 Comparison Table

| Keyword | Purpose | Where Used | Compile Check | Runtime Behavior |
|---------|---------|------------|---------------|------------------|
| **`virtual`** | Enable polymorphic dispatch | Base class declaration | ✅ Checks function is virtual | ✅ Enables dynamic binding |
| **`override`** | Verify override | Derived class declaration | ✅ Must match base signature | ❌ No runtime effect |
| **`final`** | Prevent further override/inheritance | Derived class or function | ✅ Cannot be overridden | ❌ No runtime effect |
| **`= 0`** | Pure virtual (must implement) | Base class declaration | ✅ Derived must implement | ✅ Makes class abstract |

### 3.2 Usage Examples

```cpp
class Base
{
public:
    // Pure virtual - derived MUST implement
    virtual void mustImplement() = 0;
    
    // Virtual with default - derived MAY override
    virtual void canOverride()
    {
        Info << "Base implementation\n";
    }
    
    // Non-virtual - derived CANNOT override polymorphically
    void cannotOverride()
    {
        Info << "Static binding\n";
    }
};

class Derived : public Base
{
public:
    // ✅ MUST implement pure virtual
    void mustImplement() override
    {
        Info << "Derived implementation\n";
    }
    
    // ✅ Override with compiler verification
    void canOverride() override
    {
        Info << "Derived implementation\n";
        // Can still call base:
        // Base::canOverride();
    }
    
    // ❌ Cannot override non-virtual
    // void cannotOverride() override;  // COMPILE ERROR!
};

class FinalDerived final : public Derived
{
public:
    // ❌ Cannot inherit from final class
    // class MoreDerived : public FinalDerived {};  // ERROR!
    
    // ❌ Cannot override final method
    // void canOverride() override final;  // Would prevent further override
};
```

### 3.3 When to Use Each

```cpp
// ✅ Use virtual in base class to enable polymorphism
class Base
{
    virtual void process() = 0;  // Interface
};

// ✅ Use override in derived to ensure correctness
class Derived : public Base
{
    void process() override  // Compiler checks signature match
    {
        // Implementation
    }
};

// ✅ Use final to prevent further derivation
class Leaf final : public Base
{
    void process() override final  // Cannot be overridden again
    {
        // Final implementation
    }
};

// ❌ Common mistake: forgetting virtual in base
class Base
{
    void process();  // Not virtual - no polymorphism!
};

class Derived : public Base
{
    void process() override;  // ERROR! Nothing to override
};
```

---

## 4. Override Virtual Functions

### 4.1 Basic Override Implementation

```cpp
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

tmp<volScalarField> myModel::k() const
{
    return k_;
}

tmp<volScalarField> myModel::epsilon() const
{
    return epsilon_;
}

tmp<volScalarField> myModel::nuEff() const
{
    return tmp<volScalarField>
    (
        new volScalarField
        (
            IOobject
            (
                "nuEff",
                mesh_.time().timeName(),
                mesh_,
                IOobject::NO_READ,
                IOobject::NO_WRITE
            ),
            nut_ + nu()  // Eddy viscosity + molecular viscosity
        )
    );
}

void myModel::correct()
{
    // Transport turbulence properties
    nut_ = Cmu_*sqr(k_)/(epsilon_ + epsilon_.small());
    
    // Solve k-epsilon equations
    tmp<fvScalarMatrix> kEqn
    (
        fvm::ddt(phase_, k_)
      + fvm::div(phaseAlphaphi_, k_)
      - fvm::laplacian(DkEff_, k_)
     ==
        Pk_ - fvm::Sp(epsilon_/k_, k_)
    );
    
    kEqn.relax();
    kEqn.solve();
    
    tmp<fvScalarMatrix> epsilonEqn
    (
        fvm::ddt(phase_, epsilon_)
      + fvm::div(phaseAlphaphi_, epsilon_)
      - fvm::laplacian(DepsilonEff_, epsilon_)
     ==
        (C1_*Pk_*epsilon_/k_ - fvm::Sp(C2_*epsilon_/k_, epsilon_))
    );
    
    epsilonEqn.relax();
    epsilonEqn.solve();
}

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
```

### 4.2 Return Type Considerations

```cpp
// ✅ Return by value for simple types
virtual scalar yPlus() const
{
    return yPlus_;
}

// ✅ Return tmp<> for OpenFOAM fields
virtual tmp<volScalarField> k() const
{
    return k_;
}

// ✅ Return const reference for cached results
virtual const volScalarField& epsilon() const
{
    return epsilon_;
}

// ❌ Avoid returning raw pointers to OpenFOAM objects
// virtual volScalarField* k() const;  // Memory leak risk!
```

---

## 5. Call Base Class Methods

### 5.1 Extending Base Behavior

```cpp
void myModel::correct()
{
    // Call base implementation first
    turbulenceModel::correct();
    // ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    // Initializes common turbulence model state
    
    // Then add model-specific behavior
    calculateProductionTerm();
    solveAdditionalEquations();
    updateCoefficients();
}
```

### 5.2 Complete Replacement

```cpp
void myModel::correct()
{
    // ❌ Don't call base if replacing entirely
    // turbulenceModel::correct();
    
    // Implement custom behavior from scratch
    customCalculation();
}
```

### 5.3 Using Base Class Data

```cpp
tmp<volScalarField> myModel::nuEff() const
{
    // Access base class member functions
    const volScalarField& nu = this->nu();
    //                              ^^^^^^^^
    //                              Calls turbulenceModel::nu()
    
    return tmp<volScalarField>
    (
        new volScalarField(nut_ + nu)
    );
}
```

### 5.4 Scope Resolution Operator

```cpp
void Derived::someMethod()
{
    // ✅ Explicit base class call
    Base::someMethod();
    
    // ✅ Call through this pointer
    this->Base::someMethod();
    
    // ❌ Ambiguous if not specified (could be infinite recursion)
    // someMethod();  // Calls Derived::someMethod() recursively!
}
```

---

## 6. Virtual Destructors

### 6.1 Why Virtual Destructors Are Essential

```cpp
// ❌ WITHOUT virtual destructor
class Base
{
public:
    ~Base()  // NOT virtual!
    {
        Info << "Base destructor\n";
    }
};

class Derived : public Base
{
    scalarField* data_;
    
public:
    Derived() : data_(new scalarField(100)) {}
    
    ~Derived()  // NOT called when deleted via base pointer!
    {
        delete data_;
        Info << "Derived destructor\n";
    }
};

Base* ptr = new Derived();
delete ptr;  // ⚠️ ONLY ~Base() called! Memory leak from data_!

// ✅ WITH virtual destructor
class Base
{
public:
    virtual ~Base()  // ✅ VIRTUAL!
    {
        Info << "Base destructor\n";
    }
};

class Derived : public Base
{
    scalarField* data_;
    
public:
    Derived() : data_(new scalarField(100)) {}
    
    ~Derived() override  // ✅ Called via base pointer
    {
        delete data_;
        Info << "Derived destructor\n";
    }
};

Base* ptr = new Derived();
delete ptr;  // ✅ ~Derived() called, then ~Base() - proper cleanup!
```

### 6.2 Rule of Thumb

**If your class has ANY virtual functions, it MUST have a virtual destructor.**

```cpp
class Base
{
public:
    virtual void process() = 0;
    
    // ✅ ALWAYS include when you have virtual functions
    virtual ~Base() = default;
    
    // OR if you need custom cleanup:
    // virtual ~Base()
    // {
    //     cleanup();
    // }
};
```

### 6.3 Default vs Custom Destructor

```cpp
// ✅ Use = default when compiler-generated is sufficient
virtual ~myModel() = default;

// ✅ Implement custom when cleanup needed
virtual ~myModel()
{
    // Close files
    if (filePtr_.valid())
    {
        filePtr_->close();
    }
    
    // Deallocate dynamic memory
    delete[] rawData_;
    
    Info << "myModel destroyed\n";
}
```

---

## 7. Common Pitfalls and Solutions

### 7.1 Signature Mismatch

```cpp
// ❌ WRONG: Const mismatch
class Base
{
public:
    virtual void process();
};

class Derived : public Base
{
public:
    void process() const override;  // ERROR! Signature doesn't match
};

// ✅ CORRECT: Match exact signature
class Derived : public Base
{
public:
    void process() override;  // Matches Base::process()
};
```

### 7.2 Forgetting Override Keyword

```cpp
class Base
{
public:
    virtual void process();
};

class Derived : public Base
{
public:
    // ❌ Without override: typo not caught!
    void proces();  // Creates new function, doesn't override
    
    // ✅ With override: compiler catches error
    void proces() override;  // ERROR! No Base::proces() to override
};
```

### 7.3 Object Slicing

```cpp
class Base
{
public:
    virtual void process() { Info << "Base\n"; }
};

class Derived : public Base
{
public:
    void process() override { Info << "Derived\n"; }
};

// ❌ SLICING: Object copy loses derived portion
Derived d;
Base b = d;  // Slices! Copies only Base portion
b.process();  // Prints "Base" - polymorphism lost!

// ✅ POLYMORPHISM: Use pointers or references
Derived d;
Base* ptr = &d;  // No slicing
ptr->process();  // Prints "Derived" - polymorphism works!

Base& ref = d;   // No slicing
ref.process();   // Prints "Derived" - polymorphism works!
```

### 7.4 Calling Virtual Functions in Constructors

```cpp
class Base
{
public:
    Base()
    {
        // ⚠️ DANGER: Virtual call in constructor
        init();  // Calls Base::init(), not Derived::init()!
    }
    
    virtual void init()
    {
        Info << "Base init\n";
    }
};

class Derived : public Base
{
    scalarField data_;
    
public:
    Derived() : data_(100)
    {
        // Derived portion not yet constructed in Base constructor!
    }
    
    void init() override
    {
        // ⚠️ data_ not initialized when Base constructor calls this!
        data_ = 0.0;  
    }
};

// ✅ SOLUTION: Two-phase initialization
class Derived : public Base
{
    scalarField data_;
    
public:
    Derived() : data_(100)
    {
        // Don't call virtual init() here
    }
    
    void init() override
    {
        // ✅ Now data_ is constructed
        data_ = 0.0;
    }
    
    void initialize()
    {
        // ✅ Call after construction complete
        init();
    }
};
```

### 7.5 Diamond Problem (Multiple Inheritance)

```cpp
// ⚠️ POTENTIAL ISSUE: Diamond hierarchy
class Base { public: virtual void f() {} };
class A : public Base {};
class B : public Base {};
class Diamond : public A, public B {};  // ERROR! Ambiguous Base

// ✅ SOLUTION: Virtual inheritance
class Base { public: virtual void f() {} };
class A : virtual public Base {};
class B : virtual public Base {};
class Diamond : public A, public B {};  // OK! Single Base subobject
```

---

## 8. Best Practices Summary

### ✅ DO's

1. **Always declare virtual destructor** in polymorphic base classes
2. **Use `override` keyword** on all overridden functions
3. **Prefer `final` keyword** when preventing further inheritance
4. **Call base class methods** using `Base::method()` syntax
5. **Match exact signatures** when overriding virtual functions
6. **Use pointers/references** for polymorphic behavior
7. **Return `tmp<>`** for OpenFOAM field objects
8. **Initialize base classes** properly in constructor initializer list

### ❌ DON'Ts

1. **Don't forget `virtual`** in base class declarations
2. **Don't rely on implicit conversions** - be explicit with scope resolution
3. **Don't call virtual functions** from constructors/destructors
4. **Don't copy polymorphic objects** - use pointers/references instead
5. **Don't mix `override`** with non-virtual base functions
6. **Don't return raw pointers** from functions returning fields
7. **Don't use `using` declarations** to override virtual functions
8. **Don't make destructors non-virtual** in polymorphic classes

---

## 9. Integration Example

### 9.1 Complete Working Example

```cpp
// myKEpsilon.H
#ifndef myKEpsilon_H
#define myKEpsilon_H

#include "turbulenceModel.H"
#include "volFields.H"

class myKEpsilon
:
    public turbulenceModel
{
    // Private Data
    volScalarField k_;
    volScalarField epsilon_;
    volScalarField nut_;
    
    dimensionedScalar Cmu_;
    dimensionedScalar C1_;
    dimensionedScalar C2_;
    dimensionedScalar sigmaK_;
    dimensionedScalar sigmaEps_;

public:
    TypeName("myKEpsilon");
    
    myKEpsilon
    (
        const volVectorField& U,
        const surfaceScalarField& phi,
        const transportModel& transport
    );
    
    virtual ~myKEpsilon() = default;
    
    // Member Functions
    virtual tmp<volScalarField> k() const override
    {
        return k_;
    }
    
    virtual tmp<volScalarField> epsilon() const override
    {
        return epsilon_;
    }
    
    virtual tmp<volScalarField> nuEff() const override
    {
        return tmp<volScalarField>
        (
            new volScalarField
            (
                IOobject
                (
                    "nuEff",
                    mesh_.time().timeName(),
                    mesh_,
                    IOobject::NO_READ,
                    IOobject::NO_WRITE
                ),
                nut_ + nu()
            )
        );
    }
    
    virtual void correct() override;
};

#endif

// myKEpsilon.C
#include "myKEpsilon.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

myKEpsilon::myKEpsilon
(
    const volVectorField& U,
    const surfaceScalarField& phi,
    const transportModel& transport
)
:
    turbulenceModel(U, phi, transport),
    k_
    (
        IOobject
        (
            "k",
            U.time().timeName(),
            U.mesh(),
            IOobject::MUST_READ,
            IOobject::AUTO_WRITE
        ),
        U.mesh()
    ),
    epsilon_
    (
        IOobject
        (
            "epsilon",
            U.time().timeName(),
            U.mesh(),
            IOobject::MUST_READ,
            IOobject::AUTO_WRITE
        ),
        U.mesh()
    ),
    nut_
    (
        IOobject
        (
            "nut",
            U.time().timeName(),
            U.mesh(),
            IOobject::MUST_READ,
            IOobject::AUTO_WRITE
        ),
        U.mesh()
    ),
    Cmu_("Cmu", dimless, 0.09),
    C1_("C1", dimless, 1.44),
    C2_("C2", dimless, 1.92),
    sigmaK_("sigmaK", dimless, 1.0),
    sigmaEps_("sigmaEps", dimless, 1.3)
{
    nut_ = Cmu_*sqr(k_)/(epsilon_ + epsilon_.small());
}

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

void myKEpsilon::correct()
{
    // Call base class correct (if needed)
    turbulenceModel::correct();
    
    // Calculate turbulent viscosity
    nut_ = Cmu_*sqr(k_)/(epsilon_ + epsilon_.small());
    
    // Wall functions
    if (wallTreatment_.wallFunctions())
    {
        wallTreatment_->correct(k_, epsilon_);
    }
    
    // k equation
    tmp<fvScalarMatrix> kEqn
    (
        fvm::ddt(k_)
      + fvm::div(phi_, k_)
      - fvm::laplacian(DkEff(), k_)
     ==
        Pk - fvm::Sp(epsilon_/k_, k_)
    );
    
    kEqn.relax();
    solve(kEqn);
    
    // epsilon equation
    tmp<fvScalarMatrix> epsilonEqn
    (
        fvm::ddt(epsilon_)
      + fvm::div(phi_, epsilon_)
      - fvm::laplacian(DepsilonEff(), epsilon_)
     ==
        (C1_*Pk*epsilon_/k_ - fvm::Sp(C2_*epsilon_/k_, epsilon_))
    );
    
    epsilonEqn.relax();
    solve(epsilonEqn);
}

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

} // End namespace Foam

// ************************************************************************* //
```

---

## Quick Reference

### Virtual Function Keywords

| Keyword | Syntax | Effect |
|---------|--------|--------|
| `virtual` | `virtual void f() = 0;` | Declares virtual/pure virtual |
| `override` | `void f() override;` | Verifies override (C++11) |
| `final` | `void f() override final;` | Prevents further override |
| `= 0` | `virtual void f() = 0;` | Pure virtual (must implement) |
| `= default` | `virtual ~Base() = default;` | Use compiler-generated |

### OpenFOAM Base Classes

```cpp
// Turbulence models
turbulenceModel
RASModel, LESModel

// Thermodynamics
basicThermo
psiThermo, rhoThermo

// Boundary conditions
fvPatchField<scalar>
fixedValueFvPatchField, zeroGradientFvPatchField

// Function objects
functionObject
logFiles, sets, surfaces

// Physical models
immiscibleIncompressibleTwoPhaseMixture
phaseModel
```

---

## 🧠 Concept Check

<details>
<summary><b>1. What does the <code>override</code> keyword do?</b></summary>

**Answer:** The `override` keyword instructs the compiler to verify that the function actually overrides a base class virtual function. If the signature doesn't match or there's no base virtual function, the compiler generates an error. This catches typos and signature mismatches at compile time.

**Example:**
```cpp
void proces() override;  // ERROR! No Base::proces() to override
void process() override; // OK! Matches Base::process()
```
</details>

<details>
<summary><b>2. Why must you use a virtual destructor in polymorphic base classes?</b></summary>

**Answer:** When deleting a derived object through a base pointer, a non-virtual destructor results in undefined behavior. Only the base class destructor is called, causing resource leaks. A virtual destructor ensures both derived and base destructors are called in proper order.

**Example:**
```cpp
Base* ptr = new Derived();
delete ptr;
// Without virtual: only ~Base() called - LEAK!
// With virtual: ~Derived() then ~Base() called - CLEAN!
```
</details>

<details>
<summary><b>3. What is a pure virtual function and when should you use it?</b></summary>

**Answer:** A pure virtual function (`virtual void f() = 0;`) declares an interface without implementation. It makes the class abstract, preventing instantiation. Derived classes MUST implement all pure virtual functions to become concrete classes. Use this when the base class defines an interface but has no meaningful default implementation.

**Example:**
```cpp
class Shape {
public:
    virtual double area() = 0;  // Pure virtual - must implement
    virtual void draw() { /* default implementation */ }
};

class Circle : public Shape {
public:
    double area() override { return PI * r * r; }  // Required
    // Inherits default draw() implementation
};
```
</details>

<details>
<summary><b>4. What is object slicing and how do you avoid it?</b></summary>

**Answer:** Object slicing occurs when copying a derived object to a base object. Only the base portion is copied, losing derived-specific data and polymorphic behavior. Avoid slicing by using pointers or references instead of value semantics.

**Example:**
```cpp
Derived d;
Base b = d;     // SLICING! Loses derived portion
Base* ptr = &d; // OK! Polymorphism preserved
Base& ref = d;  // OK! Polymorphism preserved
```
</details>

<details>
<summary><b>5. When should you use <code>final</code> on a function or class?</b></summary>

**Answer:** Use `final` to prevent further overriding or inheritance:
- **On a function:** Prevents derived classes from overriding this specific function
- **On a class:** Prevents any class from inheriting from this class

This is useful for:
- Sealing leaf implementations
- Performance optimization (compiler can devirtualize)
- Design intent communication
- Preventing accidental further derivation

**Example:**
```cpp
class Leaf final : public Base { }; // Cannot inherit from Leaf

void process() override final { }   // Cannot override in further derived
```
</details>

<details>
<summary><b>6. What's the difference between <code>virtual</code>, <code>override</code>, and <code>final</code>?</b></summary>

**Answer:**

| Keyword | Location | Effect |
|---------|----------|--------|
| `virtual` | Base class | Enables polymorphic dispatch |
| `override` | Derived class | Verifies function overrides base virtual |
| `final` | Derived class or function | Prevents further override/inheritance |

**Usage:**
```cpp
// Base declares virtual
virtual void f() = 0;

// Derived uses override to verify
void f() override { }

// Leaf uses final to prevent further
void f() override final { }
```

`virtual` enables polymorphism, `override` verifies correctness, `final` prevents extension.
</details>

<details>
<summary><b>7. How do you properly call a base class method from a derived override?</b></summary>

**Answer:** Use the scope resolution operator with the base class name:

```cpp
void Derived::correct()
{
    // Option 1: Explicit base class
    Base::correct();
    
    // Option 2: Through this pointer
    this->Base::correct();
    
    // Now add derived-specific behavior
    derivedSpecificWork();
}
```

This allows extending base behavior rather than completely replacing it. The derived method first delegates to the base implementation, then adds its own logic.
</details>

---

## 📖 Related Documentation

### Within This Module

- **Classes and Objects:** [04_Classes_Objects_and_Pointers.md](04_Classes_Objects_and_Pointers.md)
- **Design Patterns:** [06_Design_Pattern_Rationale.md](06_Design_Pattern_Rationale.md)
- **Module Overview:** [00_Overview.md](00_Overview.md)

### OpenFOAM Documentation

- **Programming Guide:** `$FOAM_DOC/Guides/ProgrammingGuide.pdf`
- **Doxygen:** `turbulenceModel`, `basicThermo`, `fvPatchField` class references
- **Source Code:** `$FOAM_SRC/TurbulenceModels/turbulenceModels/`

### External Resources

- **C++ Virtual Functions:** [cppreference.com](https://en.cppreference.com/w/cpp/language/virtual)
- **OOP Best Practices:** Effective C++ by Scott Meyers (Item 7, 14, 27)
- **Runtime Polymorphism:** Modern C++ Design by Andrei Alexandrescu

---

**Next:** Learn about [Design Patterns](06_Design_Pattern_Rationale.md) in OpenFOAM to see how inheritance and virtual functions combine to create extensible architectures.