# Practical Exercise - Design Patterns in OpenFOAM

---

## 🎯 Learning Objectives

After completing this module, you will be able to:
- **Implement** the Factory pattern for runtime object selection in OpenFOAM
- **Apply** the Strategy pattern for interchangeable algorithms
- **Build** Observer pattern implementations for field monitoring
- **Create** Singleton pattern implementations for global state management
- **Identify** appropriate use cases for each design pattern in CFD applications

---

## 📋 Prerequisites

Before starting this module, you should:
- Understand **C++ inheritance and polymorphism** (virtual functions, abstract classes)
- Have basic knowledge of **OpenFOAM dictionary** structure and runtime selection
- Be familiar with **OpenFOAM field types** (`volScalarField`, `volVectorField`)
- Understand **pointers and memory management** in C++

---

## Overview

### WHAT: Design Pattern Implementation
Design patterns provide reusable solutions to common software architecture problems. In OpenFOAM, these patterns enable:
- **Runtime selection** of turbulence models, boundary conditions, and numerical schemes
- **Flexible algorithms** that can be swapped without code modification
- **Extensible monitoring** and data collection systems
- **Global resource management** for meshes, databases, and utilities

### WHY: Pattern Application
Understanding and implementing design patterns helps you:
- **Write maintainable code** that follows OpenFOAM conventions
- **Create extensible solvers** that adapt to different simulation requirements
- **Debug existing OpenFOAM code** more effectively by recognizing patterns
- **Develop professional-quality utilities** following best practices

### HOW: Hands-on Practice
This module provides practical exercises for each major pattern, demonstrating:
- **Real-world OpenFOAM scenarios** where each pattern applies
- **Complete working code** that you can adapt to your projects
- **Pattern-specific considerations** for CFD applications
- **Integration points** with existing OpenFOAM infrastructure

---

## Exercise 1: Factory Pattern for Runtime Selection

### 3W Analysis

**WHAT (Task Description)**
Create a Factory pattern implementation for selecting different source term models at runtime based on dictionary configuration.

**WHY (Learning Goal)**
- Understand how OpenFOAM implements runtime selection for turbulence models, boundary conditions, and discretization schemes
- Learn to decouple object creation from usage, enabling extensibility without modifying existing code
- Practice using OpenFOAM's `autoPtr` and dictionary parsing mechanisms

**HOW (Implementation)**
Implement a factory that reads a `type` keyword from the dictionary and returns the appropriate source model object.

---

### Pattern Demonstrated
**Factory Pattern** - Centralizes object creation logic and enables runtime selection based on configuration.

---

### Implementation

```cpp
// ===== ABSTRACT PRODUCT =====
class sourceModel
{
protected:
    const dictionary dict_;
    
public:
    sourceModel(const dictionary& dict)
    :
        dict_(dict)
    {}
    
    // Interface for all source models
    virtual tmp<volScalarField> sourceTerm(const volScalarField& field) = 0;
    
    virtual ~sourceModel() {}
};

// ===== CONCRETE PRODUCTS =====
class constantSource
:
    public sourceModel
{
    scalar constantValue_;
    
public:
    constantSource(const dictionary& dict)
    :
        sourceModel(dict),
        constantValue_(dict.get<scalar>("value"))
    {
        Info << "Created constant source with value: " 
             << constantValue_ << endl;
    }
    
    virtual tmp<volScalarField> sourceTerm(const volScalarField& field) override
    {
        auto tSource = tmp<volScalarField>::New
        (
            IOobject
            (
                "constantSource",
                field.mesh().time().timeName(),
                field.mesh(),
                IOobject::NO_READ,
                IOobject::NO_WRITE
            ),
            field.mesh(),
            dimensionedScalar(dimless, constantValue_)
        );
        
        return tSource;
    }
};

class functionSource
:
    public sourceModel
{
    autoPtr<Function1<scalar>> function_;
    
public:
    functionSource(const dictionary& dict)
    :
        sourceModel(dict),
        function_(Function1<scalar>::New("valueFunction", dict))
    {
        Info << "Created function source" << endl;
    }
    
    virtual tmp<volScalarField> sourceTerm(const volScalarField& field) override
    {
        scalar tValue = function_->value(field.mesh().time().value());
        
        auto tSource = tmp<volScalarField>::New
        (
            IOobject
            (
                "functionSource",
                field.mesh().time().timeName(),
                field.mesh(),
                IOobject::NO_READ,
                IOobject::NO_WRITE
            ),
            field.mesh(),
            dimensionedScalar(dimless, tValue)
        );
        
        return tSource;
    }
};

class fieldDependentSource
:
    public sourceModel
{
    scalar coefficient_;
    
public:
    fieldDependentSource(const dictionary& dict)
    :
        sourceModel(dict),
        coefficient_(dict.get<scalar>("coefficient"))
    {
        Info << "Created field-dependent source with coefficient: " 
             << coefficient_ << endl;
    }
    
    virtual tmp<volScalarField> sourceTerm(const volScalarField& field) override
    {
        auto tSource = tmp<volScalarField>::New
        (
            IOobject
            (
                "fieldDependentSource",
                field.mesh().time().timeName(),
                field.mesh(),
                IOobject::NO_READ,
                IOobject::NO_WRITE
            ),
            coefficient_ * field
        );
        
        return tSource;
    }
};

// ===== FACTORY =====
class sourceFactory
{
public:
    static autoPtr<sourceModel> create(const word& modelType, const dictionary& dict)
    {
        if (modelType == "constant")
        {
            return autoPtr<sourceModel>(new constantSource(dict));
        }
        else if (modelType == "function")
        {
            return autoPtr<sourceModel>(new functionSource(dict));
        }
        else if (modelType == "fieldDependent")
        {
            return autoPtr<sourceModel>(new fieldDependentSource(dict));
        }
        else
        {
            FatalErrorInFunction
                << "Unknown source type: " << modelType << nl
                << "Valid types: constant, function, fieldDependent" << nl
                << exit(FatalError);
            
            return autoPtr<sourceModel>(nullptr);
        }
    }
};

// ===== USAGE EXAMPLE =====
// In dictionary (e.g., constant/sourceProperties):
// source
// {
//     type fieldDependent;
//     coefficient 0.5;
// }

// In solver code:
/*
const dictionary& sourceDict = mesh.solutionDict().subDict("source");
word sourceType = sourceDict.get<word>("type");

autoPtr<sourceModel> source = sourceFactory::create(sourceType, sourceDict);

tmp<volScalarField> sourceTerm = source->sourceTerm(T);
// Add source term to equation: fvm::ddt(T) + fvm::div(phi, T) == sourceTerm();
*/
```

---

### Exercise 1a: Extend the Factory
**Task**: Add a new source model type called `decaySource` that decays exponentially with time:
```cpp
// S_k = S_0 * exp(-lambda * t)
```

**Requirements**:
1. Create `decaySource` class inheriting from `sourceModel`
2. Read `initialValue` and `decayRate` from dictionary
3. Implement `sourceTerm()` method
4. Update `sourceFactory::create()` to handle the new type

---

## Exercise 2: Strategy Pattern for Interchangeable Schemes

### 3W Analysis

**WHAT (Task Description)**
Implement the Strategy pattern to create interchangeable interpolation schemes that can be selected and swapped at runtime without modifying the using code.

**WHY (Learning Goal)**
- Understand how OpenFOAM implements different convection schemes (upwind, linear, QUICK)
- Learn to encapsulate algorithms making them interchangeable
- Practice separating algorithm implementation from client code

**HOW (Implementation)**
Create an abstract strategy interface and multiple concrete implementations for different interpolation algorithms.

---

### Pattern Demonstrated
**Strategy Pattern** - Defines a family of algorithms, encapsulates each one, and makes them interchangeable at runtime.

---

### Implementation

```cpp
// ===== STRATEGY INTERFACE =====
template<class Type>
class interpolationScheme
{
public:
    // Interpolate between two values based on position (0 to 1)
    virtual Type interpolate
    (
        const Type& valueA,
        const Type& valueB,
        const scalar position
    ) const = 0;
    
    // Name of the scheme
    virtual word name() const = 0;
    
    virtual ~interpolationScheme() {}
};

// ===== CONCRETE STRATEGIES =====
// 1. Linear Interpolation
template<class Type>
class linearScheme
:
    public interpolationScheme<Type>
{
public:
    virtual Type interpolate
    (
        const Type& valueA,
        const Type& valueB,
        const scalar position
    ) const override
    {
        // Linear interpolation: a + t*(b-a)
        return valueA + position * (valueB - valueA);
    }
    
    virtual word name() const override
    {
        return "linear";
    }
};

// 2. Cubic Interpolation (smoothstep)
template<class Type>
class cubicScheme
:
    public interpolationScheme<Type>
{
public:
    virtual Type interpolate
    (
        const Type& valueA,
        const Type& valueB,
        const scalar position
    ) const override
    {
        // Smooth interpolation: 3t² - 2t³
        scalar t2 = position * position;
        scalar t3 = t2 * position;
        scalar weight = 3*t2 - 2*t3;
        
        return valueA + weight * (valueB - valueA);
    }
    
    virtual word name() const override
    {
        return "cubic";
    }
};

// 3. Upwind-Biased Interpolation
template<class Type>
class upwindScheme
:
    public interpolationScheme<Type>
{
    scalar biasFactor_;
    
public:
    upwindScheme(scalar biasFactor = 0.75)
    :
        biasFactor_(biasFactor)
    {}
    
    virtual Type interpolate
    (
        const Type& valueA,
        const Type& valueB,
        const scalar position
    ) const override
    {
        // Bias toward upstream value
        Type upstream = (position > 0.5) ? valueA : valueB;
        Type downstream = (position > 0.5) ? valueB : valueA;
        
        return upstream * biasFactor_ + downstream * (1.0 - biasFactor_);
    }
    
    virtual word name() const override
    {
        return "upwind";
    }
};

// ===== CONTEXT (USER OF STRATEGY) =====
template<class Type>
class interpolator
{
    autoPtr<interpolationScheme<Type>> scheme_;
    
public:
    // Constructor with runtime scheme selection
    interpolator(const word& schemeName)
    {
        if (schemeName == "linear")
        {
            scheme_ = autoPtr<interpolationScheme<Type>>
            (
                new linearScheme<Type>()
            );
        }
        else if (schemeName == "cubic")
        {
            scheme_ = autoPtr<interpolationScheme<Type>>
            (
                new cubicScheme<Type>()
            );
        }
        else if (schemeName == "upwind")
        {
            scheme_ = autoPtr<interpolationScheme<Type>>
            (
                new upwindScheme<Type>()
            );
        }
        else
        {
            FatalError << "Unknown interpolation scheme: " << schemeName
                       << exit(FatalError);
        }
    }
    
    // Perform interpolation using selected strategy
    Type interpolate
    (
        const Type& valueA,
        const Type& valueB,
        const scalar position
    ) const
    {
        return scheme_->interpolate(valueA, valueB, position);
    }
    
    // Change strategy at runtime
    void setScheme(const word& schemeName)
    {
        if (schemeName == "linear")
        {
            scheme_.reset(new linearScheme<Type>());
        }
        else if (schemeName == "cubic")
        {
            scheme_.reset(new cubicScheme<Type>());
        }
        else if (schemeName == "upwind")
        {
            scheme_.reset(new upwindScheme<Type>());
        }
    }
    
    word schemeName() const
    {
        return scheme_->name();
    }
};

// ===== USAGE EXAMPLE =====
/*
// Create interpolator with initial scheme
interpolator<scalar> interp("linear");

// Perform interpolation
scalar result1 = interp.interpolate(0.0, 1.0, 0.5);  // = 0.5

// Change scheme at runtime
interp.setScheme("cubic");
scalar result2 = interp.interpolate(0.0, 1.0, 0.5);  // = 0.5 (smooth)

// Apply to fields
volScalarField interpolatedField
(
    IOobject
    (
        "interpolatedField",
        mesh.time().timeName(),
        mesh,
        IOobject::NO_READ,
        IOobject::AUTO_WRITE
    ),
    mesh,
    dimensionedScalar(dimless, Zero)
);

forAll(interpolatedField, cellI)
{
    scalar t = mesh.cellCentres()[cellI].x() / mesh.bounds().span().x();
    interpolatedField[cellI] = interp.interpolate(field1[cellI], field2[cellI], t);
}
*/
```

---

### Exercise 2a: Add New Strategy
**Task**: Implement a `monotonicScheme` that preserves monotonicity (prevents overshoots):

```cpp
// Requirements:
// 1. Detect if interpolation would create overshoot (result outside [a,b])
// 2. If overshoot detected, clamp to nearest bound
// 3. Otherwise use linear interpolation
```

---

## Exercise 3: Observer Pattern for Field Monitoring

### 3W Analysis

**WHAT (Task Description)**
Create an Observer pattern implementation to monitor field values and automatically trigger actions when specific conditions are met (e.g., convergence, maximum value exceeded).

**WHY (Learning Goal)**
- Understand how OpenFOAM's functionObjects monitor fields during simulation
- Learn to implement event-driven systems where multiple observers respond to field changes
- Practice decoupling monitoring logic from solver code

**HOW (Implementation)**
Implement a subject (field) that maintains a list of observers and notifies them when the field changes.

---

### Pattern Demonstrated
**Observer Pattern** - Defines a one-to-many dependency between objects so that when one object changes state, all dependents are notified automatically.

---

### Implementation

```cpp
// ===== OBSERVER INTERFACE =====
class fieldObserver
{
public:
    // Called when field changes
    virtual void update(const volScalarField& field) = 0;
    
    // Observer identifier
    virtual word name() const = 0;
    
    virtual ~fieldObserver() {}
};

// ===== CONCRETE OBSERVERS =====
// 1. Maximum Value Monitor
class maxMonitor
:
    public fieldObserver
{
    scalar warningThreshold_;
    scalar fatalErrorThreshold_;
    
public:
    maxMonitor(scalar warnThresh, scalar fatalThresh)
    :
        warningThreshold_(warnThresh),
        fatalErrorThreshold_(fatalThresh)
    {}
    
    virtual void update(const volScalarField& field) override
    {
        scalar fieldMax = max(field).value();
        
        if (fieldMax > fatalErrorThreshold_)
        {
            FatalErrorInFunction
                << "Field " << field.name() << " exceeded fatal threshold: "
                << fieldMax << " > " << fatalErrorThreshold_ << nl
                << exit(FatalError);
        }
        else if (fieldMax > warningThreshold_)
        {
            WarningInFunction
                << "Field " << field.name() << " exceeded warning threshold: "
                << fieldMax << " > " << warningThreshold_ << endl;
        }
    }
    
    virtual word name() const override
    {
        return "maxMonitor";
    }
};

// 2. Convergence Monitor
class convergenceMonitor
:
    public fieldObserver
{
    scalar tolerance_;
    scalar previousResidual_;
    label iterationCounter_;
    
public:
    convergenceMonitor(scalar tol)
    :
        tolerance_(tol),
        previousResidual_(GREAT),
        iterationCounter_(0)
    {}
    
    virtual void update(const volScalarField& field) override
    {
        // Calculate residual (simplified)
        scalar currentResidual = sum(mag(field)).value();
        
        if (iterationCounter_ > 0)
        {
            scalar relativeChange = mag(currentResidual - previousResidual_) 
                                   / (previousResidual_ + SMALL);
            
            if (relativeChange < tolerance_)
            {
                Info << "Field " << field.name() 
                     << " converged! Relative change: " << relativeChange
                     << " < " << tolerance_ << endl;
            }
        }
        
        previousResidual_ = currentResidual;
        iterationCounter_++;
    }
    
    virtual word name() const override
    {
        return "convergenceMonitor";
    }
};

// 3. Statistics Logger
class statsLogger
:
    public fieldObserver
{
    OFstream logFile_;
    label writeInterval_;
    label counter_;
    
public:
    statsLogger(const fileName& logPath, label interval = 10)
    :
        logFile_(logPath),
        writeInterval_(interval),
        counter_(0)
    {
        logFile_ << "Time,Min,Max,Mean,Sum" << endl;
    }
    
    virtual void update(const volScalarField& field) override
    {
        if (counter_ % writeInterval_ == 0)
        {
            scalar fieldMin = min(field).value();
            scalar fieldMax = max(field).value();
            scalar fieldMean = average(field).value();
            scalar fieldSum = sum(field).value();
            
            logFile_ << field.time().timeName() << ","
                     << fieldMin << ","
                     << fieldMax << ","
                     << fieldMean << ","
                     << fieldSum << endl;
        }
        counter_++;
    }
    
    virtual word name() const override
    {
        return "statsLogger";
    }
};

// ===== SUBJECT (FIELD WITH OBSERVERS) =====
class observableField
:
    public volScalarField
{
    List<autoPtr<fieldObserver>> observers_;
    
public:
    observableField
    (
        const IOobject& io,
        const fvMesh& mesh
    )
    :
        volScalarField(io, mesh)
    {}
    
    // Attach an observer
    void attachObserver(autoPtr<fieldObserver> observer)
    {
        observers_.append(observer);
        Info << "Attached observer: " << observer->name() << endl;
    }
    
    // Detach an observer by name
    void detachObserver(const word& observerName)
    {
        forAll(observers_, i)
        {
            if (observers_[i]->name() == observerName)
            {
                Info << "Detaching observer: " << observerName << endl;
                observers_.remove(i);
                break;
            }
        }
    }
    
    // Notify all observers of field change
    void notifyObservers()
    {
        forAll(observers_, i)
        {
            observers_[i]->update(*this);
        }
    }
    
    // Override assignment operator to trigger notification
    void operator=(const volScalarField& rhs)
    {
        volScalarField::operator=(rhs);
        notifyObservers();
    }
};

// ===== USAGE EXAMPLE =====
/*
// Create observable field
observableField T
(
    IOobject
    (
        "T",
        runTime.timeName(),
        mesh,
        IOobject::MUST_READ,
        IOobject::AUTO_WRITE
    ),
    mesh
);

// Attach observers
T.attachObserver
(
    autoPtr<fieldObserver>
    (
        new maxMonitor(300.0, 500.0)  // Warn at 300K, fatal at 500K
    )
);

T.attachObserver
(
    autoPtr<fieldObserver>
    (
        new convergenceMonitor(1e-6)
    )
);

T.attachObserver
(
    autoPtr<fieldObserver>
    (
        new statsLogger("fieldStats.csv", 10)
    )
);

// During solver loop, observers are automatically notified
// when T is updated:
// solve(TEqn == ...);  // This calls T.operator=(), triggering notifications
*/
```

---

### Exercise 3a: Create New Observer
**Task**: Implement a `gradientMonitor` observer that:
1. Calculates field gradients using `fvc::grad()`
2. Warns if maximum gradient exceeds a threshold
3. Writes cells with high gradients to a `cellSet` for visualization

---

## Exercise 4: Singleton Pattern for Global Registry

### 3W Analysis

**WHAT (Task Description)**
Implement a Singleton pattern to create a global registry for managing shared simulation resources (e.g., mesh databases, material properties, lookup tables).

**WHY (Learning Goal)**
- Understand when single access point is appropriate vs. when to avoid global state
- Learn thread-safe singleton implementation patterns
- Practice managing resource lifecycle and initialization order

**HOW (Implementation)**
Create a class with private constructor, static instance pointer, and public access method with lazy initialization.

---

### Pattern Demonstrated
**Singleton Pattern** - Ensures a class has only one instance and provides a global point of access to it.

---

### Implementation

```cpp
// ===== SINGLETON REGISTRY =====
class simulationRegistry
{
private:
    // Private instance pointer (Meyers Singleton uses function-local static)
    simulationRegistry()
    :
        initialized_(false)
    {
        Info << "Initializing simulation registry" << endl;
    }
    
    // Prevent copying
    simulationRegistry(const simulationRegistry&) = delete;
    void operator=(const simulationRegistry&) = delete;
    
    // Registry data
    bool initialized_;
    
    HashTable<autoPtr<volScalarField>> scalarFields_;
    HashTable<autoPtr<volVectorField>> vectorFields_;
    HashTable<dictionary> propertyDictionaries_;
    
    // Mesh reference
    const fvMesh* meshPtr_;
    
public:
    // Thread-safe singleton access (Meyers Singleton)
    static simulationRegistry& instance()
    {
        static simulationRegistry instance;
        return instance;
    }
    
    // ===== REGISTRY METHODS =====
    
    // Set mesh reference
    void setMesh(const fvMesh& mesh)
    {
        meshPtr_ = &mesh;
        initialized_ = true;
        Info << "Registry: Mesh registered" << endl;
    }
    
    // Register a scalar field
    void registerField(const word& name, autoPtr<volScalarField> field)
    {
        if (scalarFields_.found(name))
        {
            Warning << "Field " << name << " already registered. Overwriting." << endl;
        }
        scalarFields_.insert(name, field);
        Info << "Registry: Registered scalar field " << name << endl;
    }
    
    // Register a vector field
    void registerField(const word& name, autoPtr<volVectorField> field)
    {
        if (vectorFields_.found(name))
        {
            Warning << "Field " << name << " already registered. Overwriting." << endl;
        }
        vectorFields_.insert(name, field);
        Info << "Registry: Registered vector field " << name << endl;
    }
    
    // Register a property dictionary
    void registerProperties(const word& name, const dictionary& dict)
    {
        propertyDictionaries_.insert(name, dict);
        Info << "Registry: Registered properties " << name << endl;
    }
    
    // Retrieve scalar field
    volScalarField& getScalarField(const word& name)
    {
        if (!scalarFields_.found(name))
        {
            FatalErrorInFunction
                << "Scalar field " << name << " not found in registry" << nl
                << "Available fields: " << scalarFields_.toc() << nl
                << exit(FatalError);
        }
        return scalarFields_[name]();
    }
    
    // Retrieve vector field
    volVectorField& getVectorField(const word& name)
    {
        if (!vectorFields_.found(name))
        {
            FatalErrorInFunction
                << "Vector field " << name << " not found in registry" << nl
                << "Available fields: " << vectorFields_.toc() << nl
                << exit(FatalError);
        }
        return vectorFields_[name]();
    }
    
    // Retrieve property dictionary
    const dictionary& getProperties(const word& name) const
    {
        if (!propertyDictionaries_.found(name))
        {
            FatalErrorInFunction
                << "Properties " << name << " not found in registry" << nl
                << exit(FatalError);
        }
        return propertyDictionaries_[name];
    }
    
    // Check if field exists
    bool hasField(const word& name) const
    {
        return scalarFields_.found(name) || vectorFields_.found(name);
    }
    
    // List all registered items
    void listContents() const
    {
        Info << "\n=== Simulation Registry Contents ===" << nl;
        
        Info << "Scalar Fields:" << nl;
        Info << "  " << scalarFields_.toc() << nl;
        
        Info << "Vector Fields:" << nl;
        Info << "  " << vectorFields_.toc() << nl;
        
        Info << "Property Dictionaries:" << nl;
        Info << "  " << propertyDictionaries_.toc() << nl;
        
        Info << "====================================\n" << endl;
    }
    
    // Clear all entries
    void clear()
    {
        scalarFields_.clear();
        vectorFields_.clear();
        propertyDictionaries_.clear();
        Info << "Registry: All entries cleared" << endl;
    }
};

// ===== USAGE EXAMPLE =====
/*
// In main solver or custom utility:

// Initialize registry with mesh
simulationRegistry& registry = simulationRegistry::instance();
registry.setMesh(mesh);

// Register some fields
registry.registerField
(
    "T",
    autoPtr<volScalarField>::New
    (
        IOobject("T", runTime.timeName(), mesh, IOobject::MUST_READ, IOobject::AUTO_WRITE),
        mesh
    )
);

registry.registerField
(
    "U",
    autoPtr<volVectorField>::New
    (
        IOobject("U", runTime.timeName(), mesh, IOobject::MUST_READ, IOobject::AUTO_WRITE),
        mesh
    )
);

// Register material properties
dictionary transportProps;
transportProps.add("nu", dimensionedScalar("nu", dimViscosity, 1e-6));
registry.registerProperties("transport", transportProps);

// List contents
registry.listContents();

// Access from anywhere in code
volScalarField& T = registry.getScalarField("T");
const dictionary& props = registry.getProperties("transport");

scalar nu = props.get<scalar>("nu");
Info << "Kinematic viscosity: " << nu << endl;
*/
```

---

### Exercise 4a: Extend Registry
**Task**: Add the following methods to `simulationRegistry`:

1. **Field Lookup Table**:
   ```cpp
   // Cache field statistics (min, max, mean)
   void cacheStatistics(const word& fieldName);
   scalar getCachedStat(const word& fieldName, const word& statName);
   ```

2. **Dependency Tracking**:
   ```cpp
   // Register that field A depends on field B
   void addDependency(const word& fieldA, const word& fieldB);
   // Get all dependencies of a field
   wordList getDependencies(const word& fieldName);
   ```

---

## Complete Example: Integrated Pattern Usage

### Scenario: Custom Scalar Transport Solver

This example demonstrates all four patterns working together:

```cpp
// ===== PATTERN 1: FACTORY - Source Term Selection =====
autoPtr<sourceModel> source = sourceFactory::create
(
    mesh.solutionDict().get<word>("sourceType"),
    mesh.solutionDict().subDict("sourceCoeffs")
);

// ===== PATTERN 2: STRATEGY - Interpolation Scheme =====
interpolator<scalar> faceInterp
(
    mesh.schemesDict().get<word>("interpolationScheme")
);

// ===== PATTERN 3: OBSERVER - Field Monitoring =====
observableField T
(
    IOobject("T", runTime.timeName(), mesh, IOobject::MUST_READ, IOobject::AUTO_WRITE),
    mesh
);

T.attachObserver(autoPtr<fieldObserver>(new maxMonitor(300.0, 500.0)));
T.attachObserver(autoPtr<fieldObserver>(new convergenceMonitor(1e-6)));

// ===== PATTERN 4: SINGLETON - Global Registry =====
simulationRegistry& registry = simulationRegistry::instance();
registry.setMesh(mesh);
registry.registerField("T", autoPtr<volScalarField>::New(T));

// ===== MAIN TIME LOOP =====
while (runTime.loop())
{
    Info << "Time = " << runTime.timeName() << endl;
    
    // Get source term (Factory)
    tmp<volScalarField> Su = source->sourceTerm(T);
    
    // Solve transport equation
    fvScalarMatrix TEqn
    (
        fvm::ddt(T)
      + fvm::div(phi, T)
      - fvm::laplacian(DT, T)
     == Su
    );
    
    TEqn.solve();
    
    // Observers automatically notified when T is updated
    
    // Access from registry if needed
    // registry.getScalarField("T");
    
    runTime.write();
}
```

---

## Quick Reference: Pattern Selection Guide

| Pattern | Use Case | OpenFOAM Example | Key Benefit |
|---------|----------|------------------|-------------|
| **Factory** | Runtime object selection from dictionary | Turbulence models (`RASModel`, `LESModel`) | Extensibility without code changes |
| **Strategy** | Interchangeable algorithms | Convection schemes (`upwind`, `linear`, `QUICK`) | Runtime algorithm swapping |
| **Observer** | Event-driven monitoring | `functionObjects` for field output | Decoupled monitoring logic |
| **Singleton** | Global resource management | `Time` database, `argList` | Single access point to shared data |

---

## 🔑 Key Takeaways

### Design Pattern Benefits
1. **Factory Pattern**: Enables OpenFOAM's runtime selection mechanism - users can choose models/schemes via dictionary without recompiling
2. **Strategy Pattern**: Allows algorithm experimentation - test different discretization schemes without solver changes
3. **Observer Pattern**: Implements automated monitoring - separate simulation logic from data collection and convergence checking
4. **Singleton Pattern**: Manages global state - provides controlled access to shared resources

### Implementation Best Practices
- **Use `autoPtr`** for Factory returns to manage ownership
- **Declare virtual destructors** in abstract base classes
- **Prefer composition over inheritance** - patterns should compose functionality
- **Avoid Singleton abuse** - global state complicates testing and thread safety

### Pattern Combinations
- **Factory + Strategy**: Create strategies at runtime based on dictionary
- **Observer + Singleton**: Singleton registry notifies observers of globally-relevant events
- **All Four Together**: See complete solver example above

---

## 🧠 Concept Check

<details>
<summary><b>1. Why use Factory instead of direct `new` calls?</b></summary>

**Answer**: The Factory pattern enables **runtime selection** based on dictionary configuration. Users can change models/schemes without:
- Recompiling the solver
- Modifying source code
- Knowing concrete class implementations

The Factory also **decouples** client code from concrete classes, making it easier to add new types later.
</details>

<details>
<summary><b>2. How does the Strategy pattern improve code flexibility?</b></summary>

**Answer**: The Strategy pattern **encapsulates algorithms** into separate classes, enabling:
- **Runtime swapping** of algorithms without changing client code
- **Easy testing** by swapping real strategies with mocks
- **Algorithm families** with shared interface
- **Open/Closed Principle**: open for extension (new strategies), closed for modification (existing code)

OpenFOAM uses this for convection schemes - you can switch from `linear` to `upwind` in `fvSchemes` without touching solver code.
</details>

<details>
<summary><b>3. What are the advantages and disadvantages of Singleton pattern?</b></summary>

**Answer**: 

**Advantages**:
- **Single access point** to global resources
- **Lazy initialization** - created only when first needed
- **Controlled instance creation** - prevents multiple instances
- **Global availability** - access from anywhere in code

**Disadvantages**:
- **Global state** - makes testing difficult (hidden dependencies)
- **Thread safety** - requires careful implementation
- **Lifetime management** - destruction order issues
- **Violation of dependency injection** - hides dependencies

**Best Practice**: Use Singleton sparingly. Prefer dependency injection for testability. Use Meyer's Singleton (function-local static) for thread-safe lazy initialization in C++11 and later.
</details>

<details>
<summary><b>4. When should you use the Observer pattern in CFD code?</b></summary>

**Answer**: Use Observer pattern when:
- **Multiple actions** needed on field changes (monitoring, logging, convergence checking)
- **Decoupling monitoring** from solver logic - solver shouldn't know about monitoring details
- **Dynamic subscriptions** - observers can be added/removed at runtime
- **Event-driven systems** - react to simulation events without polling

OpenFOAM's `functionObjects` are essentially observers - they monitor fields and perform actions (write probes, calculate forces, check convergence) without solver code knowing the details.
</details>

<details>
<summary><b>5. How do you choose between Factory and Strategy patterns?</b></summary>

**Answer**: 

**Factory Pattern** - use for **object creation**:
- Creating different model types at runtime
- Selection based on configuration (dictionary, command line)
- Complex initialization logic that should be centralized
- Example: turbulence model selection, boundary condition selection

**Strategy Pattern** - use for **algorithm behavior**:
- Swapping algorithms at runtime
- Different implementations of same operation
- Algorithm variations with shared interface
- Example: convection schemes, interpolation methods, time integration schemes

They can **work together**: Factory creates Strategy objects at runtime.
</details>

<details>
<summary><b>6. What's the relationship between these patterns and OpenFOAM's RTS (Run-Time Selection) system?</b></summary>

**Answer**: OpenFOAM's RTS system is a **sophisticated Factory implementation**:

**RTS Components**:
1. **`New` function** - static Factory method in each model class
2. **`TypeName` macro** - registers type name for lookup
3. **`runtimeSelectionTable`** - static registry of available types
4. **Dictionary lookup** - reads `type` keyword and creates appropriate object

**How it works**:
```cpp
// In turbulence model class:
// Runtime selection table declaration
declareRunTimeSelectionTable
(
    autoPtr,
    compressible::RASModel,
    dictionary,
    (
        const volScalarField& rho,
        const volVectorField& U,
        const surfaceScalarField& phi,
        transportModel& transport
    ),
    (rho, U, phi, transport)
);

// Factory creation
autoPtr<RASModel> RASModel::New
(
    const volScalarField& rho,
    const volVectorField& U,
    const surfaceScalarField& phi,
    transportModel& transport
)
{
    word modelType = transport.lookup("RASModel");
    
    typename dictionaryConstructorTable::iterator cstrIter =
        dictionaryConstructorTablePtr_->find(modelType);
    
    return cstrIter()(rho, U, phi, transport);
}
```

Our exercises demonstrate the **principles** behind this sophisticated system.
</details>

---

## 📖 Related Documents

### Pattern Theory & Fundamentals
- **📋 Overview**: [00_Overview.md](00_Overview.md) - All patterns summarized with comparison
- **🎯 Fundamentals**: [01_Introduction.md](01_Introduction.md) - Theory and classification

### Pattern-Specific Deep Dives
- **🏭 Factory Pattern**: [02_Factory_Pattern.md](02_Factory_Pattern.md) - Runtime selection implementation
- **♟️ Strategy Pattern**: [03_Strategy_Pattern.md](03_Strategy_Pattern.md) - Interchangeable algorithms
- **🔄 Pattern Synergy**: [04_Pattern_Synergy.md](04_Pattern_Synergy.md) - Combining multiple patterns
- **⚡ Performance Analysis**: [05_Performance_Analysis.md](05_Performance_Analysis.md) - Performance considerations

### Applied Topics
- **🔧 C++ in OpenFOAM**: [MODULE_05_OPENFOAM_PROGRAMMING/02_Cpp_Fundamentals_for_OpenFOAM.md](../../MODULE_05_OPENFOAM_PROGRAMMING/CONTENT/02_Cpp_Fundamentals_for_OpenFOAM.md)
- **🎛️ Run-Time Selection**: [MODULE_05_OPENFOAM_PROGRAMMING/05_Runtime_Selection_System.md](../../MODULE_05_OPENFOAM_PROGRAMMING/CONTENT/05_Runtime_Selection_System.md)
- **📊 Function Objects**: [MODULE_03_PROCESSING_ANALYSIS/07_Function_Objects.md](../../MODULE_03_PROCESSING_ANALYSIS/CONTENT/07_Function_Objects.md)

---

**Next Steps**: Practice these patterns in your own OpenFOAM utilities. Start with the Factory pattern for runtime model selection, then progress to Strategy for algorithm flexibility. Use Observer for monitoring and Singleton only when global state is truly necessary.