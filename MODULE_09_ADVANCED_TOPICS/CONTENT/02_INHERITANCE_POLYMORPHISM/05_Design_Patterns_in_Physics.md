# Advanced Design Patterns in OpenFOAM Physics Models

Design Patterns ขั้นสูงใน OpenFOAM Physics Models

---

## Learning Objectives

By the end of this section, you will be able to:

- **Distinguish** advanced design patterns (Strategy, Template Method, Factory, Builder, Observer) from basic inheritance/polymorphism
- **Apply** the Strategy pattern for interchangeable algorithms in physics models
- **Implement** the Template Method pattern for customizable workflows with fixed structure
- **Recognize** when to use Factory vs. Builder patterns for object creation
- **Identify** the Observer pattern in OpenFOAM's callback and notification systems

**Prerequisites:** Abstract Interfaces (02), Inheritance Hierarchies (03), Run-Time Selection (04)

---

## Overview

> **Design patterns** are reusable solutions to common software design problems that go beyond basic inheritance and polymorphism.

### The 3W Framework

| Aspect | Description |
|--------|-------------|
| **What** | Established patterns that solve recurring design problems in C++ and are specifically applied in OpenFOAM for physics modeling, numerical schemes, and solver architecture |
| **Why** | Promote code reuse, maintainability, extensibility, and provide a common vocabulary for discussing design decisions across teams and codebases |
| **How** | Apply patterns like Strategy, Template Method, Factory, Builder, and Observer following OpenFOAM's coding conventions and leveraging its RTS infrastructure |

---

## Redundancy Note

**This file focuses on patterns BEYOND basic inheritance/polymorphism:**

| Topic | Covered In |
|-------|------------|
| Abstract interfaces, pure virtual functions | [02_Abstract_Interfaces.md](02_Abstract_Interfaces.md) |
| Inheritance hierarchies, TypeName macro | [03_Inheritance_Hierarchies.md](03_Inheritance_Hierarchies.md) |
| Run-Time Selection (RTS) system | [04_Run_Time_Selection_System.md](04_Run_Time_Selection_System.md) |

**This file covers:** Strategy, Template Method, Factory variants, Builder, Observer, and composite patterns.

---

## Pattern 1: Strategy Pattern

### 1.1 What is the Strategy Pattern?

**Definition:** Define a family of interchangeable algorithms and make them independently selectable without changing the clients that use them.

### 1.2 Why Use the Strategy Pattern?

| Benefit | OpenFOAM Example | When to Use |
|---------|------------------|-------------|
| **Runtime swappable algorithms** | Switch turbulence models without recompiling | Multiple solution approaches exist |
| **Isolated testing** | Test each discretization scheme independently | Need to test algorithms in isolation |
| **Open/Closed Principle** | Add new convection schemes without modifying existing code | Extensibility requirement |
| **Algorithm decoupling** | Solver doesn't need to know scheme implementation details | Reduce coupling between components |

### 1.3 How to Implement Strategy in OpenFOAM

**Theory:** Strategy pattern uses composition to hold a reference to a strategy object and delegates algorithmic behavior to it.

```cpp
// Generic Strategy pattern structure
class Context
{
    std::unique_ptr<Strategy> strategy_;  // Composition
    
public:
    void setStrategy(std::unique_ptr<Strategy> s)
    {
        strategy_ = std::move(s);
    }
    
    void execute()
    {
        strategy_->executeAlgorithm();  // Delegation
    }
};
```

**Simple Example:** Numerical integration strategies

```cpp
// Strategy interface
class IntegrationStrategy
{
public:
    virtual double integrate(double (*f)(double), double a, double b) = 0;
    virtual ~IntegrationStrategy() = default;
};

// Concrete Strategy 1: Trapezoidal rule
class TrapezoidalRule : public IntegrationStrategy
{
public:
    virtual double integrate(double (*f)(double), double a, double b) override
    {
        int n = 100;
        double h = (b - a) / n;
        double sum = 0.5 * (f(a) + f(b));
        for (int i = 1; i < n; i++)
            sum += f(a + i * h);
        return sum * h;
    }
};

// Concrete Strategy 2: Simpson's rule
class SimpsonRule : public IntegrationStrategy
{
public:
    virtual double integrate(double (*f)(double), double a, double b) override
    {
        int n = 100;
        double h = (b - a) / n;
        double sum = f(a) + f(b);
        for (int i = 1; i < n; i += 2)
            sum += 4 * f(a + i * h);
        for (int i = 2; i < n; i += 2)
            sum += 2 * f(a + i * h);
        return sum * h / 3;
    }
};
```

**OpenFOAM Example:** Convection schemes as strategies

```cpp
// OpenFOAM's convection scheme strategy
template<class Type>
class fv::convectionScheme
{
public:
    // Virtual interface - the strategy
    virtual tmp<GeometricField<Type, fvsPatchField, surfaceMesh>>
    interpolate
    (
        const surfaceScalarField&,
        const GeometricField<Type, fvPatchField, volMesh>&
    ) const = 0;
    
    virtual ~convectionScheme() = default;
};

// Concrete strategy: Upwind
template<class Type>
class fv::upwindScheme : public fv::convectionScheme<Type>
{
public:
    TypeName("upwind");
    
    virtual tmp<GeometricField<Type, fvsPatchField, surfaceMesh>>
    interpolate
    (
        const surfaceScalarField& faceFlux,
        const GeometricField<Type, fvPatchField, volMesh>& vf
    ) const override
    {
        // Upwind interpolation implementation
        return tmp<GeometricField<Type, fvsPatchField, surfaceMesh>>
        (
            new GeometricField<Type, fvsPatchField, surfaceMesh>
            (
                IOobject("upwind::interpolate", vf.mesh().time().timeName(), vf.mesh()),
                vf.mesh(),
                dimensioned<Type>("0", vf.dimensions(), pTraits<Type>::zero),
                extrapolatedCalculatedFvsPatchField<Type>::typeName
            )
        );
        // Actual upwind implementation...
    }
};

// Concrete strategy: Linear upwind
template<class Type>
class fv::linearUpwindScheme : public fv::convectionScheme<Type>
{
public:
    TypeName("linearUpwind");
    
    virtual tmp<GeometricField<Type, fvsPatchField, surfaceMesh>>
    interpolate
    (
        const surfaceScalarField& faceFlux,
        const GeometricField<Type, fvPatchField, volMesh>& vf
    ) const override
    {
        // Linear upwind implementation
        // Uses gradient for higher-order accuracy
    }
};

// Concrete strategy: Central differencing
template<class Type>
class fv::centralScheme : public fv::convectionScheme<Type>
{
public:
    TypeName("central");
    
    virtual tmp<GeometricField<Type, fvsPatchField, surfaceMesh>>
    interpolate
    (
        const surfaceScalarField& faceFlux,
        const GeometricField<Type, fvPatchField, volMesh>& vf
    ) const override
    {
        // Central differencing implementation
    }
};
```

**Solver Usage (Context):**

```cpp
// In fvSolution dictionary
schemes
{
    div(phi,U)      Gauss upwind;         // Strategy: upwind
    div(phi,k)      Gauss linearUpwind;   // Strategy: linearUpwind
    div(phi,epsilon) Gauss upwind;        // Strategy: upwind
}

// Framework code uses strategy polymorphically
template<class Type>
void solveConvection
(
    const surfaceScalarField& phi,
    const GeometricField<Type, fvPatchField, volMesh>& vf,
    const convectionScheme<Type>& scheme  // Strategy reference
)
{
    // Delegate to concrete strategy
    tmp<GeometricField<Type, fvsPatchField, surfaceMesh>> flux =
        scheme.interpolate(phi, vf);
    
    // Use interpolated flux...
}
```

### Strategy Pattern vs. Basic Polymorphism

| Aspect | Basic Polymorphism | Strategy Pattern |
|--------|-------------------|------------------|
| **Intent** | General substitutability | Interchangeable algorithms |
| **Focus** | "Is-a" relationship | "Has-a" relationship (composition) |
| **Changing behavior** | Via inheritance | Via object composition |
| **OpenFOAM example** | `kEpsilon` IS A `turbulenceModel` | `upwindScheme` IS A strategy HELD BY convection term |

---

## Pattern 2: Template Method Pattern

### 2.1 What is the Template Method Pattern?

**Definition:** Define the skeleton of an algorithm in a base class but defer some steps to derived classes, letting subclasses redefine certain steps without changing the algorithm's structure.

### 2.2 Why Use the Template Method Pattern?

| Benefit | OpenFOAM Example | When to Use |
|---------|------------------|-------------|
| **Invariant algorithm structure** | All turbulence models: initialize → solve → update | Fixed workflow with variable steps |
| **Code reuse** | Common initialization in base, specific equations in derived | Common setup/teardown logic |
| **Enforced workflow** | `correct()` always called after construction | Must follow specific sequence |
| **Hook methods** | Optional `postCorrect()` for extensions | Optional customization points |

### 2.3 How to Implement Template Method in OpenFOAM

**Theory:** Base class defines final template method; derived classes override primitive operations.

```cpp
// Generic Template Method structure
class AbstractClass
{
public:
    // Final template method - defines algorithm structure
    void templateMethod()
    {
        stepOne();        // Fixed implementation
        stepTwo();        // Overridable
        if (optionalStep())  // Hook (default returns false)
        {
            stepThree();  // Overridable
        }
        stepFour();       // Fixed implementation
    }
    
    virtual ~AbstractClass() = default;
    
protected:
    void stepOne() { /* Fixed */ }
    virtual void stepTwo() = 0;  // Must override
    virtual bool optionalStep() { return false; }  // Hook
    virtual void stepThree() { /* Default */ }
    void stepFour() { /* Fixed */ }
};
```

**Simple Example:** Data processing pipeline

```cpp
class DataProcessor
{
public:
    // Template method - defines workflow
    void process(const std::string& inputFile)
    {
        loadData(inputFile);           // Step 1: Fixed
        validateData();                // Step 2: Overridable
        if (needsPreprocessing())      // Step 3: Hook
        {
            preprocessData();          // Step 4: Overridable
        }
        transformData();               // Step 5: Overridable
        saveResults();                 // Step 6: Fixed
    }
    
protected:
    void loadData(const std::string& file) 
    { 
        std::cout << "Loading data from " << file << std::endl; 
    }
    
    virtual void validateData() { std::cout << "Default validation" << std::endl; }
    
    virtual bool needsPreprocessing() { return false; }  // Hook
    virtual void preprocessData() {}
    
    virtual void transformData() = 0;  // Must override
    
    void saveResults() { std::cout << "Saving results" << std::endl; }
};

// Concrete implementation
class ImageProcessor : public DataProcessor
{
protected:
    virtual void validateData() override
    {
        std::cout << "Validating image format and dimensions" << std::endl;
    }
    
    virtual bool needsPreprocessing() override { return true; }
    
    virtual void preprocessData() override
    {
        std::cout << "Applying noise reduction filter" << std::endl;
    }
    
    virtual void transformData() override
    {
        std::cout << "Applying edge detection algorithm" << std::endl;
    }
};
```

**OpenFOAM Example:** Turbulence model correction

```cpp
// Base template method in turbulence model
template<class BasicTurbulenceModel>
class eddyViscosity
{
public:
    // Template method: Fixed structure of turbulence correction
    void correct()
    {
        // Step 1: Fixed - Calculate strain rate
        calculateStrainRate();
        
        // Step 2: Overridable - Model-specific preprocessing
        preprocessCorrect();
        
        // Step 3: Overridable - Solve transport equations
        correctTransportEquations();
        
        // Step 4: Fixed - Calculate eddy viscosity
        calculateNut();
        
        // Step 5: Hook - Optional post-processing
        if (needsPostCorrection())
        {
            postCorrect();
        }
    }
    
protected:
    // Fixed steps
    void calculateStrainRate()
    {
        // Common calculation for all eddy viscosity models
        const volTensorField gradU(fvc::grad(this->U_));
        this->S_ = symm(gradU);  // Strain rate tensor
    }
    
    void calculateNut()
    {
        // Common nut calculation: nut = Cmu * k^2 / epsilon
        this->nut_ = this->Cmu_*sqr(this->k_)/(this->epsilon_ + this->nutMin_);
        this->nut_.correctBoundaryConditions();
    }
    
    // Overridable steps
    virtual void preprocessCorrect()
    {
        // Default: nothing
    }
    
    virtual void correctTransportEquations() = 0;  // Must implement
    
    // Hook
    virtual bool needsPostCorrection() { return false; }
    virtual void postCorrect() {}
};

// Concrete implementation: kEpsilon
template<class BasicTurbulenceModel>
class kEpsilon : public eddyViscosity<BasicTurbulenceModel>
{
protected:
    virtual void preprocessCorrect() override
    {
        // k-epsilon specific: compute wall functions
        this->nut_.correctBoundaryConditions();
    }
    
    virtual void correctTransportEquations() override
    {
        // Solve k equation
        tmp<fvScalarMatrix> kEqn
        (
            fvm::ddt(alpha_, rho_, k_)
          + fvm::div(alphaRhoPhi_, k_)
          - fvm::laplacian(alpha_*rho_*DkEff(), k_)
         ==
            alpha_*rho_*Pk_
          - fvm::Sp(alpha_*rho_*epsilon_/k_, k_)
        );
        kEqn.solve();
        
        // Solve epsilon equation
        tmp<fvScalarMatrix> epsilonEqn
        (
            fvm::ddt(alpha_, rho_, epsilon_)
          + fvm::div(alphaRhoPhi_, epsilon_)
          - fvm::laplacian(alpha_*rho_*DepsilonEff(), epsilon_)
         ==
            alpha_*rho_*C1_*Pk_*epsilon_/k_
          - fvm::Sp(alpha_*rho_*C2_*epsilon_/k_, epsilon_)
        );
        epsilonEqn.solve();
    }
    
    virtual bool needsPostCorrection() override
    {
        return this->wallTreatmentEnabled_;
    }
    
    virtual void postCorrect() override
    {
        // Apply wall functions
        this->applyWallFunctions();
    }
};

// Concrete implementation: kOmegaSST
template<class BasicTurbulenceModel>
class kOmegaSST : public eddyViscosity<BasicTurbulenceModel>
{
protected:
    virtual void correctTransportEquations() override
    {
        // k-omega SST has different transport equations
        // Includes cross-diffusion term and blending functions
        
        tmp<fvScalarMatrix> kEqn(...);  // Different from k-epsilon
        kEqn.solve();
        
        tmp<fvScalarMatrix> omegaEqn(...);  // Solves for omega, not epsilon
        omegaEqn.solve();
    }
};
```

**Usage in solver:**

```cpp
// All turbulence models use same template method
turbulence->correct();  // Calls template method in base class
                         // Which calls derived class implementations
```

---

## Pattern 3: Factory Pattern Variants

### 3.1 Simple Factory vs. Factory Method vs. Abstract Factory

| Pattern | Description | OpenFOAM Example |
|---------|-------------|------------------|
| **Simple Factory** | Single class with creation method | `dimensionedScalar::lookupOrDefault()` |
| **Factory Method** | Subclasses decide what to create | `turbulenceModel::New()` (RTS) |
| **Abstract Factory** | Families of related products | `fvSchemes` factory for all scheme types |

### 3.2 Simple Factory in OpenFOAM

**What:** A class with a method that creates objects based on input parameters.

**Why:** Centralize object creation logic, hide complex initialization.

```cpp
// OpenFOAM example: dimensionedScalar factory
class dimensionedScalar
{
public:
    // Simple factory method
    static dimensionedScalar lookupOrDefault
    (
        const word& keyword,
        const dictionary& dict,
        const dimensionSet& dims,
        const scalar defaultValue
    )
    {
        if (dict.found(keyword))
        {
            // Create from dictionary entry
            return dimensionedScalar(keyword, dims, dict);
        }
        else
        {
            // Create with default value
            return dimensionedScalar(keyword, dims, defaultValue);
        }
    }
};

// Usage
dimensionedScalar Cmu = 
    dimensionedScalar::lookupOrDefault
    (
        "Cmu",
        coeffsDict,
        dimless,
        0.09  // Default if not in dictionary
    );
```

### 3.3 Factory Method (Already Covered in RTS)

The Run-Time Selection system (covered in file 04) IS the Factory Method pattern.

```cpp
// Factory Method in RTS
autoPtr<turbulenceModel> turbulenceModel::New(const dictionary& dict)
{
    word modelName = dict.lookup("model");
    
    // Factory method decides which concrete class to instantiate
    auto* ctorPtr = dictionaryConstructorTable(modelName);
    return ctorPtr(dict);
}
```

### 3.4 Abstract Factory in OpenFOAM

**What:** Interface for creating families of related objects without specifying their concrete classes.

**Why:** When multiple objects must work together (schemes, boundary conditions, etc.).

```cpp
// Abstract factory for finite volume schemes
class fvSchemes
{
public:
    // Factory methods for related scheme families
    virtual autoPtr<convectionScheme<scalar>> 
    convectionScheme(const surfaceScalarField&) const = 0;
    
    virtual autoPtr<convectionScheme<vector>> 
    convectionScheme(const surfaceScalarField&) const = 0;
    
    virtual autoPtr<laplacianScheme<scalar>> 
    laplacianScheme() const = 0;
    
    virtual autoPtr<gradScheme<scalar>> 
    gradScheme() const = 0;
    
    virtual autoPtr<divScheme<scalar>> 
    divScheme() const = 0;
};

// Concrete factory
class GaussSchemesFactory : public fvSchemes
{
    const dictionary& schemesDict_;
    
public:
    virtual autoPtr<convectionScheme<scalar>>
    convectionScheme(const surfaceScalarField& phi) const override
    {
        word schemeName = schemesDict_.subDict("divSchemes")
                                     .lookup("div(phi,scalar)");
        
        return convectionScheme<scalar>::New(phi, schemesDict_);
    }
    
    virtual autoPtr<laplacianScheme<scalar>>
    laplacianScheme() const override
    {
        word schemeName = schemesDict_.subDict("laplacianSchemes")
                                     .lookup("laplacian(nu)");
        
        return laplacianScheme<scalar>::New(schemesDict_);
    }
    
    // ... other factory methods
};

// Usage - creates consistent family of schemes
autoPtr<fvSchemes> schemes = new GaussSchemesFactory(schemesDict);
auto convection = schemes->convectionScheme(phi);
auto laplacian = schemes->laplacianScheme();
// All schemes are compatible (Gauss family)
```

---

## Pattern 4: Builder Pattern

### 4.1 What is the Builder Pattern?

**Definition:** Separate the construction of complex objects from their representation, allowing the same construction process to create different representations.

### 4.2 Why Use the Builder Pattern?

| Benefit | OpenFOAM Example | When to Use |
|---------|------------------|-------------|
| **Complex object construction** | `fvMesh` with multiple initialization steps | Objects with many configuration options |
| **Step-by-step construction** | `IOdictionary` with multiple setup phases | Construction has multiple stages |
| **Immutable objects** | Fields created once, never modified | Thread-safe object creation |
| **Fluent interface** | Method chaining for readability | Clean API for object creation |

### 4.3 How to Implement Builder in OpenFOAM

**Theory:** Builder class handles construction, director orchestrates the process.

```cpp
// Generic Builder pattern
class Product
{
    // Complex object with many parts
};

class Builder
{
public:
    virtual void buildPartA() = 0;
    virtual void buildPartB() = 0;
    virtual void buildPartC() = 0;
    virtual Product getResult() = 0;
};

class ConcreteBuilder : public Builder
{
    Product product_;
    
public:
    void buildPartA() override { /* ... */ }
    void buildPartB() override { /* ... */ }
    void buildPartC() override { /* ... */ }
    Product getResult() override { return product_; }
};

class Director
{
    Builder& builder_;
    
public:
    Director(Builder& b) : builder_(b) {}
    
    void construct()
    {
        builder_.buildPartA();
        builder_.buildPartB();
        builder_.buildPartC();
    }
};
```

**OpenFOAM Example:** Field construction with fluent interface

```cpp
// Builder for volScalarField
class volScalarFieldBuilder
{
    fvMesh& mesh_;
    word name_;
    dimensionSet dimensions_;
    scalar initialValue_;
    bool readFromFile_;
    word boundaryFieldType_;
    
public:
    volScalarFieldBuilder(fvMesh& mesh) : mesh_(mesh), initialValue_(0), readFromFile_(false) {}
    
    // Fluent interface for step-by-step construction
    volScalarFieldBuilder& name(const word& n)
    {
        name_ = n;
        return *this;
    }
    
    volScalarFieldBuilder& dimensions(const dimensionSet& dims)
    {
        dimensions_ = dims;
        return *this;
    }
    
    volScalarFieldBuilder& value(scalar v)
    {
        initialValue_ = v;
        return *this;
    }
    
    volScalarFieldBuilder& readFrom(bool b)
    {
        readFromFile_ = b;
        return *this;
    }
    
    volScalarFieldBuilder& boundaryFieldType(const word& type)
    {
        boundaryFieldType_ = type;
        return *this;
    }
    
    // Build method
    autoPtr<volScalarField> build()
    {
        IOobject io
        (
            name_,
            mesh_.time().timeName(),
            mesh_,
            readFromFile_ ? IOobject::MUST_READ : IOobject::NO_READ,
            IOobject::AUTO_WRITE
        );
        
        autoPtr<volScalarField> field
        (
            new volScalarField
            (
                io,
                mesh_,
                dimensionedScalar("0", dimensions_, initialValue_)
            )
        );
        
        // Apply boundary field type if specified
        if (!boundaryFieldType_.empty())
        {
            field->boundaryFieldRef().setType(boundaryFieldType_);
        }
        
        return field;
    }
};

// Usage with fluent interface
autoPtr<volScalarField> p =
    volScalarFieldBuilder(mesh)
        .name("p")
        .dimensions(dimPressure)
        .value(101325)
        .readFrom(true)
        .boundaryFieldType("zeroGradient")
        .build();

// Alternative usage
autoPtr<volScalarField> T =
    volScalarFieldBuilder(mesh)
        .name("T")
        .dimensions(dimTemperature)
        .value(300)
        .build();
```

---

## Pattern 5: Observer Pattern

### 5.1 What is the Observer Pattern?

**Definition:** Define a one-to-many dependency between objects so that when one object changes state, all its dependents are notified and updated automatically.

### 5.2 Why Use the Observer Pattern?

| Benefit | OpenFOAM Example | When to Use |
|---------|------------------|-------------|
| **Event-driven updates** | Mesh updates notify all fields | State changes affect multiple objects |
| **Loose coupling** | Function objects observe solver state | Subjects don't need to know observers |
| **Dynamic subscription** | Runtime selection of function objects | Observers can be added/removed at runtime |
| **Broadcasting** | Time step notifications to all models | One event, many recipients |

### 5.3 How to Implement Observer in OpenFOAM

**Theory:** Subject maintains observer list; observers register and receive notifications.

```cpp
// Generic Observer pattern
class Observer
{
public:
    virtual void update(const std::string& message) = 0;
    virtual ~Observer() = default;
};

class Subject
{
    std::vector<Observer*> observers_;
    
public:
    void attach(Observer* obs) { observers_.push_back(obs); }
    void detach(Observer* obs) { /* remove from vector */ }
    
    void notify(const std::string& message)
    {
        for (auto* obs : observers_)
            obs->update(message);
    }
};
```

**OpenFOAM Example:** Function objects as observers

```cpp
// Abstract observer: functionObject
class functionObject
{
public:
    // Called by solver (subject)
    virtual autoPtr<functionObject> clone() const = 0;
    virtual bool execute() = 0;      // Called each time step
    virtual bool write() = 0;         // Called at write time
    virtual bool end() = 0;           // Called at simulation end
    
    virtual ~functionObject() = default;
};

// Concrete observer: forces function object
class forces : public functionObject
{
    const fvMesh& mesh_;
    const wordList patchNames_;
    
public:
    TypeName("forces");
    
    forces(const word& name, const Time& t, const dictionary& dict)
    :
        mesh_(t.lookupObject<fvMesh>("region0")),
        patchNames_(dict.lookup("patches"))
    {}
    
    virtual bool execute() override
    {
        // Calculate and output forces
        Info << "Forces on patches: ";
        for (const word& patchName : patchNames_)
        {
            vector force = calculateForce(mesh_.boundary()[patchName]);
            Info << patchName << ": " << force << " ";
        }
        Info << endl;
        return true;
    }
    
    virtual bool write() override
    {
        // Write force history to file
        return true;
    }
    
    virtual bool end() override
    {
        Info << "Final force summary" << endl;
        return true;
    }
    
private:
    vector calculateForce(const fvPatch& patch)
    {
        // Integrate pressure and viscous forces over patch
        // ...
        return vector::zero;
    }
};

// Subject: Time (solver) maintains function object list
class Time
{
    PtrList<functionObject> functionObjects_;
    
public:
    void addFunctionObject(autoPtr<functionObject> fo)
    {
        label sz = functionObjects_.size();
        functionObjects_.set(sz, fo.ptr());
    }
    
    // Notify all observers each time step
    bool run()
    {
        while (timeIndex_ < endTime_)
        {
            timeIndex_++;
            deltaT_ = ...;
            
            // Solve equations
            
            // Notify observers
            forAll(functionObjects_, i)
            {
                functionObjects_[i].execute();
            }
            
            if (writeTime())
            {
                forAll(functionObjects_, i)
                {
                    functionObjects_[i].write();
                }
            }
        }
        
        // Final notification
        forAll(functionObjects_, i)
        {
            functionObjects_[i].end();
        }
    }
};

// Dictionary configuration (controlDict)
functions
{
    forces
    {
        type    forces;
        patches (inlet outlet walls);
        log     true;
    }
    
    probes
    {
        type    probes;
        probeLocations
        (
            (0.1 0.1 0.1)
            (0.5 0.5 0.5)
        );
    }
}
```

**Mesh change observer example:**

```cpp
// Subject: mesh
class fvMesh
{
    List<refPtr<meshObject>> objects_;
    
public:
    // Notify all mesh objects when mesh changes
    void movePoints(const pointField& newPoints)
    {
        points_ = newPoints;
        
        // Notify all observers
        forAll(objects_, i)
        {
            if (objects_[i].valid())
            {
                objects_[i]().movePoints();
            }
        }
    }
};

// Observer: meshObject (e.g., interpolation schemes)
class meshObject
{
public:
    virtual void movePoints() = 0;
    virtual ~meshObject() = default;
};

class interpolationCellPoint : public meshObject
{
    const fvMesh& mesh_;
    
public:
    virtual void movePoints() override
    {
        // Rebuild interpolation weights after mesh motion
        rebuildWeights();
    }
    
private:
    void rebuildWeights()
    {
        // Recalculate cell-to-point interpolation
    }
};
```

---

## Pattern Comparison Summary

| Pattern | Intent | OpenFOAM Use Case | Key Benefit |
|---------|--------|-------------------|-------------|
| **Strategy** | Interchangeable algorithms | Convection schemes (upwind, central, etc.) | Runtime algorithm selection |
| **Template Method** | Fixed structure, variable steps | `correct()` in turbulence models | Enforce workflow, allow customization |
| **Factory Method** | Delegates creation to subclasses | `turbulenceModel::New()` (RTS) | Runtime type selection |
| **Abstract Factory** | Families of related products | `fvSchemes` for all scheme types | Consistent object families |
| **Builder** | Complex construction step-by-step | Field initialization, mesh setup | Fluent API, complex setup |
| **Observer** | One-to-many notifications | Function objects, mesh updates | Event-driven behavior |

---

## Composite Patterns in OpenFOAM

Real OpenFOAM code often combines multiple patterns:

### Example: Turbulence Model Hierarchy

```cpp
// Combines: Template Method + Factory Method + Strategy

// Template Method: fixed correct() workflow
class turbulenceModel
{
public:
    void correct()  // Template method
    {
        preprocess();
        solveEquations();
        postprocess();
    }
    
protected:
    virtual void preprocess() {}
    virtual void solveEquations() = 0;
    virtual void postprocess() {}
};

// Factory Method: RTS creates appropriate model
autoPtr<turbulenceModel> turb = turbulenceModel::New(dict);

// Strategy: solver uses turbulence model polymorphically
solver->solve(turb);  // Can be kEpsilon, kOmegaSST, etc.
```

### Example: Boundary Condition System

```cpp
// Combines: Factory + Strategy + Template Method

// Factory: create from dictionary
autoPtr<fvPatchField<scalar>> patch = 
    fvPatchField<scalar>::New(patchName, mesh.boundary()[patchi], fieldDict);

// Strategy: different BCs implement different update strategies
class fixedValueFvPatchField : public fvPatchField<scalar>
{
    virtual void updateCoeffs() override  // Strategy implementation
    {
        // Fixed value update logic
    }
};

// Template Method: BC evaluation follows fixed pattern
void evaluate()
{
    updateCoeffs();     // Overridable
    evaluateInternal();  // Fixed
    evaluateBoundary();  // Fixed
}
```

---

## Exercise

### Task: Implement a Multi-Strategy Numerical Scheme

Create a numerical scheme system that uses multiple design patterns:

**Requirements:**
1. **Strategy Pattern:** Implement two flux calculation strategies:
   - `CentralFlux`: Central differencing
   - `UpwindFlux`: Upwind differencing

2. **Template Method Pattern:** Create a base `fluxScheme` class with:
   - Fixed: `calculate()` method (template method)
   - Overridable: `computeFlux()` (strategy)
   - Hook: `needsLimiter()` and `applyLimiter()`

3. **Factory Pattern:** Add RTS to create schemes from dictionary

**Skeleton Solution:**

<details>
<summary>Solution</summary>

```cpp
// fluxScheme.H
class fluxScheme
{
public:
    TypeName("fluxScheme");
    
    declareRunTimeSelectionTable
    (
        autoPtr,
        fluxScheme,
        dictionary,
        (const dictionary& dict),
        (dict)
    );
    
    // Template method
    tmp<surfaceScalarField> calculate
    (
        const surfaceScalarField& phi,
        const volScalarField& field
    ) const;
    
    virtual ~fluxScheme() = default;
    
protected:
    // Overridable strategy
    virtual tmp<surfaceScalarField> computeFlux
    (
        const surfaceScalarField& phi,
        const volScalarField& field
    ) const = 0;
    
    // Hook
    virtual bool needsLimiter() const { return false; }
    virtual tmp<surfaceScalarField> applyLimiter
    (
        const surfaceScalarField& flux
    ) const;
};

// centralFlux.H
class centralFlux : public fluxScheme
{
public:
    TypeName("central");
    
    centralFlux(const dictionary& dict);
    
protected:
    virtual tmp<surfaceScalarField> computeFlux
    (
        const surfaceScalarField& phi,
        const volScalarField& field
    ) const override;
};

// upwindFlux.H
class upwindFlux : public fluxScheme
{
    dimensionedScalar limiterThreshold_;
    
public:
    TypeName("upwind");
    
    upwindFlux(const dictionary& dict);
    
protected:
    virtual tmp<surfaceScalarField> computeFlux
    (
        const surfaceScalarField& phi,
        const volScalarField& field
    ) const override;
    
    virtual bool needsLimiter() const override { return true; }
    
    virtual tmp<surfaceScalarField> applyLimiter
    (
        const surfaceScalarField& flux
    ) const override;
};

// fluxScheme.C
defineRunTimeSelectionTable(fluxScheme, dictionary);

tmp<surfaceScalarField> fluxScheme::calculate
(
    const surfaceScalarField& phi,
    const volScalarField& field
) const
{
    // Step 1: Compute flux (strategy)
    tmp<surfaceScalarField> flux = computeFlux(phi, field);
    
    // Step 2: Apply limiter if needed (hook)
    if (needsLimiter())
    {
        flux = applyLimiter(flux());
    }
    
    return flux;
}

// centralFlux.C
defineTypeNameAndDebug(centralFlux, 0);
addToRunTimeSelectionTable(fluxScheme, centralFlux, dictionary);

tmp<surfaceScalarField> centralFlux::computeFlux
(
    const surfaceScalarField& phi,
    const volScalarField& field
) const
{
    return fvc::interpolate(field) * phi;
}

// upwindFlux.C
defineTypeNameAndDebug(upwindFlux, 0);
addToRunTimeSelectionTable(fluxScheme, upwindFlux, dictionary);

upwindFlux::upwindFlux(const dictionary& dict)
:
    fluxScheme(dict),
    limiterThreshold_(dict.lookupOrDefault<scalar>("limiterThreshold", 0.5))
{}

tmp<surfaceScalarField> upwindFlux::computeFlux
(
    const surfaceScalarField& phi,
    const volScalarField& field
) const
{
    return upwind<scalar>(phi, field);
}

tmp<surfaceScalarField> upwindFlux::applyLimiter
(
    const surfaceScalarField& flux
) const
{
    // Apply flux limiter
    return min(mag(flux), limiterThreshold_) * sign(flux);
}

// Usage
autoPtr<fluxScheme> scheme = fluxScheme::New(fluxDict);
tmp<surfaceScalarField> divFlux = fvc::div(scheme->calculate(phi, T));
```

</details>

---

## Key Takeaways

| Pattern | Key Point | OpenFOAM Example |
|---------|-----------|------------------|
| **Strategy** | Interchangeable algorithms via composition | Convection schemes, turbulence models |
| **Template Method** | Fixed workflow with overridable steps | `correct()`, `evaluate()` |
| **Factory Method** | RTS for runtime object creation | `ClassName::New()` |
| **Abstract Factory** | Create families of related objects | `fvSchemes` for scheme families |
| **Builder** | Step-by-step complex construction | Field initialization, mesh setup |
| **Observer** | One-to-many event notifications | Function objects, mesh updates |

### Pattern Selection Guide

| Situation | Recommended Pattern |
|-----------|---------------------|
| Multiple interchangeable algorithms | **Strategy** |
| Fixed workflow with customizable steps | **Template Method** |
| Runtime type selection from dictionary | **Factory Method** (RTS) |
| Creating compatible families of objects | **Abstract Factory** |
| Complex object with many configuration options | **Builder** |
| State changes should notify multiple objects | **Observer** |

---

## 🧠 Concept Check

<details>
<summary><b>1. What's the key difference between Strategy pattern and basic polymorphism?</b></summary>

**Strategy emphasizes composition** ("has-a" relationship) for interchangeable algorithms, while basic polymorphism emphasizes inheritance ("is-a" relationship) for general substitutability. Strategy is about algorithms, polymorphism is about type relationships.

</details>

<details>
<summary><b>2. How does Template Method enforce workflow while allowing customization?</b></summary>

**The base class defines a final template method** that calls overridable primitive operations in a fixed sequence. Derived classes customize by overriding specific steps, but cannot change the overall algorithm structure.

</details>

<details>
<summary><b>3. Why is OpenFOAM's Run-Time Selection an example of Factory Method pattern?</b></summary>

**Factory Method delegates object creation to subclasses** through virtual constructors. In OpenFOAM, `turbulenceModel::New()` delegates creation to specific derived class constructors selected via dictionary, with each derived class registered via `addToRunTimeSelectionTable`.

</details>

<details>
<summary><b>4. When should you use Builder vs. Factory pattern?</b></summary>

**Use Builder for complex multi-step construction** with many configuration options (e.g., creating a field with name, dimensions, initial value, BC types). **Use Factory for simple single-call creation** when you just need to select a type at runtime (e.g., selecting turbulence model).

</details>

<details>
<summary><b>5. How do function objects demonstrate the Observer pattern?</b></summary>

**Function objects register with the Time object** (subject) and receive notifications at specific events (execute at each timestep, write at output times, end at simulation end). The solver doesn't need to know what the function objects do - it just broadcasts notifications.

</details>

---

## 📖 Related Documentation

- **Overview:** [00_Overview.md](00_Overview.md)
- **Abstract Interfaces:** [02_Abstract_Interfaces.md](02_Abstract_Interfaces.md)
- **Inheritance Hierarchies:** [03_Inheritance_Hierarchies.md](03_Inheritance_Hierarchies.md)
- **Run-Time Selection:** [04_Run_Time_Selection_System.md](04_Run_Time_Selection_System.md)