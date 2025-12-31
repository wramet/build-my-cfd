# Practical Exercise - Inheritance and Polymorphism in OpenFOAM

---

## 🎯 Learning Objectives

By completing this exercises in this file, you will be able to:

1. **Design and implement** class hierarchies for physical models in OpenFOAM
2. **Apply** the Run-Time Selection (RTS) system to create flexible, extensible code
3. **Use** polymorphism to write solver-agnostic implementations
4. **Debug** common inheritance-related compilation and runtime errors
5. **Extend** existing OpenFOAM classes with custom implementations

**Prerequisites:** Complete files [01_Introduction.md](01_Introduction.md), [04_Run_Time_Selection_System.md](04_Run_Time_Selection_System.md)

---

## 📋 Exercise Overview

| Exercise | Difficulty | Focus | Est. Time |
|----------|-----------|-------|-----------|
| Ex 1 | Beginner | Basic inheritance | 30 min |
| Ex 2 | Intermediate | Run-Time Selection | 45 min |
| Ex 3 | Intermediate | Polymorphic usage | 30 min |
| Ex 4 | Advanced | Error handling | 45 min |
| Ex 5 | Expert | Full integration | 60 min |

---

## Exercise 1: Basic Inheritance - Source Term Hierarchy

### 📚 What: Understanding Inheritance Basics

**What:** Inheritance allows creating derived classes that reuse and extend base class functionality.

**Why:** In OpenFOAM, this enables:
- Code reuse across similar physical models
- Consistent interfaces for different implementations
- Easier maintenance and testing

**How:** Use `virtual` functions for polymorphic behavior and `public` inheritance for "is-a" relationships.

### 🎯 Task

Create a class hierarchy for different source term models:

1. **Base class** with virtual functions
2. **Derived class** implementing constant source
3. **Verify** correct polymorphic behavior

### 📝 Starter Code

**Base Class Specification:**

```cpp
// sourceModel.H
#ifndef sourceModel_H
#define sourceModel_H

#include "fvMesh.H"
#include "volFields.H"

namespace Foam
{

// Abstract base class for source terms
class sourceModel
{
protected:
    const fvMesh& mesh_;
    
public:
    // Constructor
    sourceModel(const fvMesh& mesh)
    :
        mesh_(mesh)
    {}
    
    // Declare virtual destructor
    virtual ~sourceModel() = default;
    
    // Pure virtual functions - MUST be overridden
    virtual tmp<volScalarField> Su() const = 0;  // Explicit source
    virtual tmp<volScalarField> Sp() const = 0;  // Implicit source
    
    // Virtual function with default implementation
    virtual word type() const
    {
        return word("sourceModel");
    }
};

} // End namespace Foam

#endif
```

**Derived Class to Complete:**

```cpp
// constantSource.H
#ifndef constantSource_H
#define constantSource_H

#include "sourceModel.H"

namespace Foam
{

class constantSource
:
    public sourceModel
{
    // Add member variable for constant value
    dimensionedScalar value_;
    
public:
    // Complete the constructor
    constantSource(const fvMesh& mesh, const dimensionedScalar& val);
    
    // TODO: Override Su() to return constant field
    // TODO: Override Sp() to return zero (no implicit part)
    // TODO: Override type() to return "constantSource"
    
    // TODO: Add TypeName macro for RTTS (Runtime Type Info)
    TypeName("constantSource");
};

} // End namespace Foam

#endif
```

**Implementation File:**

```cpp
// constantSource.C
#include "constantSource.H"

// TODO: Complete constructor initialization list
Foam::constantSource::constantSource
(
    const fvMesh& mesh,
    const dimensionedScalar& val
)
:
    sourceModel(mesh),
    // TODO: Initialize value_ member
{}

// TODO: Implement Su() - create volScalarField with constant value
// TODO: Implement Sp() - return zero field
// TODO: Implement type() - return "constantSource"

// TODO: Add runtime type selection macros
// defineTypeNameAndDebug(constantSource, 0);
```

### 🔍 Verification Steps

1. **Compile Check:**
   ```bash
   wmake libso
   ```
   Expected: Clean compilation without errors

2. **Runtime Type Check:**
   ```cpp
   // Test in solver
   constantSource src(mesh, dimensionedScalar("value", dimless, 5.0));
   Info << "Source type: " << src.type() << endl;
   ```
   Expected output: `Source type: constantSource`

3. **Polymorphism Test:**
   ```cpp
   sourceModel* model = new constantSource(mesh, dimensionedScalar("value", dimless, 5.0));
   Info << "Via base pointer: " << model->type() << endl;
   delete model;
   ```
   Expected: `Via base pointer: constantSource`

### ✅ Solution

<details>
<summary><b>Click to see complete solution</b></summary>

```cpp
// constantSource.C (Complete)
#include "constantSource.H"

Foam::constantSource::constantSource
(
    const fvMesh& mesh,
    const dimensionedScalar& val
)
:
    sourceModel(mesh),
    value_(val)
{}

Foam::tmp<Foam::volScalarField> Foam::constantSource::Su() const
{
    // Create new volScalarField initialized to constant value
    return tmp<volScalarField>
    (
        new volScalarField
        (
            IOobject
            (
                "Su",
                mesh_.time().timeName(),
                mesh_,
                IOobject::NO_READ,
                IOobject::NO_WRITE
            ),
            mesh_,
            value_
        )
    );
}

Foam::tmp<Foam::volScalarField> Foam::constantSource::Sp() const
{
    // No implicit source term
    dimensionedScalar zero("zero", dimless, 0.0);
    
    return tmp<volScalarField>
    (
        new volScalarField
        (
            IOobject
            (
                "Sp",
                mesh_.time().timeName(),
                mesh_,
                IOobject::NO_READ,
                IOobject::NO_WRITE
            ),
            mesh_,
            zero
        )
    );
}

Foam::word Foam::constantSource::type() const
{
    return word("constantSource");
}

defineTypeNameAndDebug(Foam::constantSource, 0);
```

</details>

### 🚀 Extension Challenge

Add a `timeDependentSource` class that varies source value with simulation time:

```cpp
class timeDependentSource : public sourceModel
{
    dimensionedScalar amplitude_;
    dimensionedScalar frequency_;
    
public:
    // TODO: Implement Su() to return: amplitude_ * sin(2*pi*frequency_*time())
};
```

---

## Exercise 2: Run-Time Selection - Dictionary-Based Factory

### 📚 What: Understanding RTS

**What:** OpenFOAM's factory pattern that creates objects from dictionary specifications.

**Why:** Enables:
- Switch models without recompiling
- User-configurable simulations through dictionary files
- Plugin architecture for custom models

**How:** Combine `TypeName`, `declareRunTimeSelectionTable`, `New()`, and `addToRunTimeSelectionTable`.

### 🎯 Task

Add full RTS support to `sourceModel` hierarchy:

1. **Declare** selection table in base class
2. **Implement** static `New()` factory method
3. **Register** derived classes in table
4. **Test** with dictionary input

### 📝 Enhanced Base Class

```cpp
// sourceModel.H
#ifndef sourceModel_H
#define sourceModel_H

#include "fvMesh.H"
#include "volFields.H"
#include "autoPtr.H"
#include "runTimeSelectionTables.H"

namespace Foam
{

class sourceModel
{
protected:
    const fvMesh& mesh_;
    
public:
    // Runtime type information
    TypeName("sourceModel");
    
    // Declare run-time selection table
    declareRunTimeSelectionTable
    (
        autoPtr,
        sourceModel,
        dictionary,
        (
            const dictionary& dict,
            const fvMesh& mesh
        ),
        (dict, mesh)
    );
    
    // Constructors
    sourceModel(const fvMesh& mesh);
    
    // Destructor
    virtual ~sourceModel() = default;
    
    // Select from dictionary
    static autoPtr<sourceModel> New
    (
        const dictionary& dict,
        const fvMesh& mesh
    );
    
    // Virtual functions
    virtual tmp<volScalarField> Su() const = 0;
    virtual tmp<volScalarField> Sp() const = 0;
};

} // End namespace Foam

#endif
```

### 🔧 Implementation to Complete

```cpp
// sourceModel.C
#include "sourceModel.H"

// TODO: Define runtime type information
// defineTypeNameAndDebug(sourceModel, 0);

// TODO: Define runtime selection table
// defineRunTimeSelectionTable(sourceModel, dictionary);

// Constructor
Foam::sourceModel::sourceModel(const fvMesh& mesh)
:
    mesh_(mesh)
{}

// TODO: Implement New() factory method
// 1. Read "type" entry from dictionary
// 2. Lookup in selection table
// 3. Return autoPtr to constructed object
Foam::autoPtr<Foam::sourceModel> Foam::sourceModel::New
(
    const dictionary& dict,
    const fvMesh& mesh
)
{
    // TODO: Complete implementation
    // const word modelType = dict.get<word>("type");
    // 
    // Info<< "Selecting sourceModel type " << modelType << endl;
    //
    // auto cstrIter = dictionaryConstructorTablePtr_->cfind(modelType);
    //
    // TODO: Check if found, return error if not
    //
    // return autoPtr<sourceModel>(cstrIter()(dict, mesh));
}
```

### 🔧 Derived Class Registration

```cpp
// constantSource.C (Add to previous implementation)
#include "constantSource.H"

// Define type info (already done)
defineTypeNameAndDebug(Foam::constantSource, 0);

// TODO: Add to runtime selection table
// addToRunTimeSelectionTable(sourceModel, constantSource, dictionary);
```

### 📝 Dictionary File

```cpp
// constant/transportProperties
source
{
    type    constantSource;    // Specifies which class to instantiate
    
    value   100;               // Class-specific parameters
    // Add optional:
    // value   uniform 100;   // Alternative syntax
}
```

### 🔍 Verification Steps

1. **Dictionary Parsing Test:**
   ```bash
   # Test dictionary reading
   testSourceModel -dict constant/transportProperties
   ```

2. **Runtime Selection Output:**
   Expected console output:
   ```
   Selecting sourceModel type constantSource
   ```

3. **Factory Method Test:**
   ```cpp
   dictionary dict = ...;  // Read from file
   autoPtr<sourceModel> src = sourceModel::New(dict, mesh);
   
   Info << "Created: " << src->type() << endl;
   Info << "Source magnitude: " << average(src->Su()).value() << endl;
   ```
   Expected:
   ```
   Created: constantSource
   Source magnitude: 100
   ```

4. **Error Handling Test:**
   ```cpp
   // Try invalid type
   dictionary badDict;
   badDict.add("type", word("nonexistentSource"));
   autoPtr<sourceModel> bad = sourceModel::New(badDict, mesh);
   ```
   Expected: Clear error message indicating available types

### ✅ Solution

<details>
<summary><b>Click to see New() implementation</b></summary>

```cpp
Foam::autoPtr<Foam::sourceModel> Foam::sourceModel::New
(
    const dictionary& dict,
    const fvMesh& mesh
)
{
    // Read model type from dictionary
    const word modelType = dict.get<word>("type");
    
    Info<< "Selecting sourceModel type " << modelType << endl;
    
    // Find constructor in selection table
    auto cstrIter = dictionaryConstructorTablePtr_->cfind(modelType);
    
    // Error handling
    if (!cstrIter.found())
    {
        FatalErrorInFunction
            << "Unknown sourceModel type " << modelType << nl << nl
            << "Valid types:" << nl
            << dictionaryConstructorTablePtr_->sortedToc()
            << exit(FatalError);
    }
    
    // Call constructor and return
    return autoPtr<sourceModel>(cstrIter()(dict, mesh));
}
```

</details>

<details>
<summary><b>Click to see derived class registration</b></summary>

```cpp
// constantSource.C (end of file)
addToRunTimeSelectionTable
(
    Foam::sourceModel,
    Foam::constantSource,
    dictionary
);
```

</details>

### 🚀 Extension Challenge

Add error recovery for dictionary input:

```cpp
// In New(), attempt to suggest corrections for typos
wordList validTypes = dictionaryConstructorTablePtr_->sortedToc();
word suggested = findClosestWord(modelType, validTypes);

if (suggested != word::null)
{
    WarningInFunction
        << "Unknown type " << modelType << ", did you mean " 
        << suggested << "?";
}
```

---

## Exercise 3: Polymorphic Usage in Solver

### 📚 What: Polymorphism in Practice

**What:** Writing solver code that works with any derived class through base class interface.

**Why:** Solvers remain unchanged when adding new models - users only add derived classes and register them.

**How:** Use base class pointers/references and virtual functions.

### 🎯 Task

Integrate `sourceModel` into a heat equation solver with polymorphic usage.

### 📝 Solver Integration

**Complete the solver code:**

```cpp
// myHeatFoam.C
#include "fvCFD.H"
#include "sourceModel.H"

int main(int argc, char *argv[])
{
    #include "setRootCaseLists.H"
    #include "createTime.H"
    #include "createMesh.H"
    
    // TODO: Create fields (T, phi, etc.)
    // volScalarField T(...);
    // surfaceScalarField phi(...);
    
    // TODO: Read transport properties dictionary
    IOdictionary transportProps
    (
        IOobject
        (
            "transportProperties",
            runTime.constant(),
            mesh,
            IOobject::MUST_READ,
            IOobject::NO_WRITE
        )
    );
    
    // Create source model polymorphically
    // TODO: Use sourceModel::New() to create from subdictionary
    const dictionary& sourceDict = transportProps.subDict("source");
    autoPtr<sourceModel> source = sourceModel::New(sourceDict, mesh);
    
    Info<< "Thermal diffusivity: " << alpha << nl
        << "Source model: " << source->type() << endl;
    
    while (runTime.loop())
    {
        #include "readTimeControls.H"
        
        // TODO: Build equation using polymorphic interface
        fvScalarMatrix TEqn
        (
            fvm::ddt(T)
          + fvm::div(phi, T)
          - fvm::laplacian(alpha, T)
          ==
            // TODO: Add explicit source: source->Su()
            // TODO: Add implicit source: fvm::Sp(source->Sp()/T, T)
        );
        
        TEqn.solve();
        
        #include "write.H"
    }
    
    return 0;
}
```

### 📝 Alternative Source Models

**Gaussian Source:**

```cpp
// gaussianSource.H
class gaussianSource : public sourceModel
{
    dimensionedScalar magnitude_;
    vector center_;
    dimensionedScalar sigma_;
    
public:
    TypeName("gaussianSource");
    
    gaussianSource(const dictionary& dict, const fvMesh& mesh);
    
    virtual tmp<volScalarField> Su() const override;
    virtual tmp<volScalarField> Sp() const override;
};

// gaussianSource.C
gaussianSource::gaussianSource
(
    const dictionary& dict,
    const fvMesh& mesh
)
:
    sourceModel(mesh),
    magnitude_(dict.get<dimensionedScalar>("magnitude")),
    center_(dict.get<vector>("center")),
    sigma_(dict.get<dimensionedScalar>("sigma"))
{}

tmp<volScalarField> gaussianSource::Su() const
{
    const volVectorField& C = mesh_.C();
    
    auto tSu = tmp<volScalarField>::New
    (
        IOobject
        (
            "Su",
            mesh_.time().timeName(),
            mesh_,
            IOobject::NO_READ,
            IOobject::NO_WRITE
        ),
        mesh_,
        dimensionedScalar("zero", magnitude_.dimensions(), 0.0)
    );
    
    volScalarField& Su = tSu.ref();
    
    // Gaussian distribution: mag * exp(-|r-center|^2 / sigma^2)
    Su = magnitude_ * exp(-magSqr(C - center_) / sqr(sigma_));
    
    return tSu;
}

tmp<volScalarField> gaussianSource::Sp() const
{
    return tmp<volScalarField>::New
    (
        IOobject
        (
            "Sp",
            mesh_.time().timeName(),
            mesh_,
            IOobject::NO_READ,
            IOobject::NO_WRITE
        ),
        mesh_,
        dimensionedScalar("zero", dimless, 0.0)
    );
}

addToRunTimeSelectionTable(sourceModel, gaussianSource, dictionary);
```

### 📝 Dictionary Examples

**Constant Source:**
```cpp
// constant/transportProperties
source
{
    type    constantSource;
    value   uniform 100;
}
```

**Gaussian Source:**
```cpp
source
{
    type        gaussianSource;
    
    magnitude   uniform 500;
    center      (0.5 0.5 0.5);
    sigma       uniform 0.1;
}
```

### 🔍 Verification Steps

1. **Switching Models:**
   ```bash
   # Run with constant source
   myHeatFoam
   # Edit transportProperties, change type to gaussianSource
   myHeatFoam
   ```
   Expected: Different T field distributions

2. **Output Verification:**
   ```cpp
   // Add to solver
   Info<< "Source sum: " << sum(source->Su() * mesh.V()).value() << nl
       << "Source max: " << max(source->Su()).value() << endl;
   ```

3. **Convergence Check:**
   Monitor solver residuals - implicit source (`Sp`) should improve convergence

### ✅ Solution

<details>
<summary><b>Click to see complete solver integration</b></summary>

```cpp
#include "fvCFD.H"
#include "sourceModel.H"

int main(int argc, char *argv[])
{
    #include "setRootCaseLists.H"
    #include "createTime.H"
    #include "createMesh.H"
    
    // Create field T
    volScalarField T
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
    
    // Create flux field
    surfaceScalarField phi
    (
        IOobject
        (
            "phi",
            runTime.timeName(),
            mesh,
            IOobject::READ_IF_PRESENT,
            IOobject::AUTO_WRITE
        ),
        fvc::flux(unity)
    );
    
    // Read properties
    IOdictionary transportProps
    (
        IOobject
        (
            "transportProperties",
            runTime.constant(),
            mesh,
            IOobject::MUST_READ,
            IOobject::NO_WRITE
        )
    );
    
    dimensionedScalar alpha
    (
        "alpha",
        dimViscosity,
        transportProps.lookup("alpha")
    );
    
    // Create source polymorphically
    const dictionary& sourceDict = transportProps.subDict("source");
    autoPtr<sourceModel> source = sourceModel::New(sourceDict, mesh);
    
    Info<< "\nThermal diffusivity alpha: " << alpha << nl
        << "Source model type: " << source->type() << nl
        << "Source magnitude (max): " << max(source->Su()).value() << nl
        << endl;
    
    while (runTime.loop())
    {
        Info<< "Time = " << runTime.timeName() << nl << endl;
        
        // Polymorphic equation - works with ANY derived class!
        fvScalarMatrix TEqn
        (
            fvm::ddt(T)
          + fvm::div(phi, T)
          - fvm::laplacian(alpha, T)
          ==
            source->Su()           // Explicit part
          + fvm::Sp(source->Sp()/T, T)  // Implicit part
        );
        
        TEqn.solve();
        
        #include "write.H"
        
        Info<< "ExecutionTime = " << runTime.elapsedCpuTime() << " s"
            << "  ClockTime = " << runTime.elapsedClockTime() << " s"
            << nl << endl;
    }
    
    Info<< "End\n" << endl;
    
    return 0;
}
```

</details>

### 🚀 Extension Challenge

1. **Add time-varying source** with ramp-up period
2. **Implement table-based source** reading values from external file
3. **Create composite source** combining multiple models

---

## Exercise 4: Error Handling and Debugging

### 📚 What: Common Inheritance Errors

**What:** Typical compilation and runtime issues with inheritance in OpenFOAM.

**Why:** Understanding these patterns reduces debugging time significantly.

**How:** Learn error messages and prevention strategies.

### 🎯 Task

Debug and fix common inheritance errors.

### 🐛 Error Scenarios

**Scenario 1: Missing Virtual Destructor**

```cpp
// PROBLEMATIC CODE
class badBase
{
public:
    // WARNING: No virtual destructor!
    ~badBase() = default;
    
    virtual void work() = 0;
};

class badDerived : public badBase
{
    double* data_;
public:
    badDerived() : data_(new double[1000]) {}
    
    ~badDerived()
    {
        delete[] data_;  // This will NOT be called via base pointer!
    }
    
    virtual void work() override {}
};

void test()
{
    badBase* obj = new badDerived();
    delete obj;  // MEMORY LEAK - ~badDerived() not called!
}
```

**Fix:**
```cpp
class goodBase
{
public:
    virtual ~goodBase() = default;  // ALWAYS use virtual destructor
};
```

**Scenario 2: Forgetting `override` Keyword**

```cpp
// PROBLEMATIC
class mySource : public sourceModel
{
public:
    virtual tmp<volScalarField> Su() const;  // Typo: should be Su()!
    // Compiler generates warning, but code compiles
    // Runtime: pure virtual function called - crashes!
};

// CORRECT
class mySource : public sourceModel
{
public:
    virtual tmp<volScalarField> Su() const override;  // Enforces match
    // If base class signature differs: COMPILATION ERROR
};
```

**Scenario 3: Missing RTS Registration**

```cpp
// Problem: Class defined but not registered
class newSource : public sourceModel
{
    TypeName("newSource");
    // ...
};

// Error at runtime:
// --> FOAM FATAL ERROR:
//     Unknown sourceModel type newSource
//     Valid types: (constantSource)

// Fix: Add to .C file
addToRunTimeSelectionTable(sourceModel, newSource, dictionary);
```

**Scenario 4: Incorrect Dictionary Syntax**

```cpp
// File: constant/transportProperties

// WRONG - typo in keyword
source
{
    Type    constantSource;  // Should be 'type', not 'Type'
    value   100;
}

// Error message:
// --> FOAM FATAL IO ERROR:
//     keyword 'type' is undefined in dictionary ".../transportProperties.source"

// WRONG - missing semicolon
source
{
    type    constantSource
    value   100;
}

// WRONG - wrong value type
source
{
    type    constantSource;
    value   "100";  // Should be number, not string
}
```

### 🔍 Debugging Checklist

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Pure virtual called | Missing override or destructor issue | Check all virtual functions match base |
| Unknown type error | Missing `addToRunTimeSelectionTable` | Add registration in .C file |
| Segmentation fault | Null pointer or deleted object | Check `autoPtr` usage, use `valid()` |
| Linker error | Missing virtual table definition | Implement all pure virtuals, check `TypeName` |
| Dictionary read error | Typos in dict file | Compare with working examples |

### 🛠️ Debugging Tools

**Enable Debug Output:**

```cpp
// In derived class constructor
debugSource::debug = 1;  // Enable debug messages

// In New() method
if (debug)
{
    Info<< "sourceModel::New(): Creating " << modelType << endl;
}
```

**Type Information:**

```cpp
// Check runtime type
Info<< "Object type: " << src.type() << nl
    << "Is constantSource? " << (isType<constantSource>(src) ? "Yes" : "No") << endl;
```

**Memory Checking:**

```cpp
// Use valgrind
valgrind --leak-check=full myHeatFoam

// Expected with proper autoPtr:
// All heap blocks were freed -- no leaks are possible
```

### ✅ Diagnostic Test

```cpp
// Add to solver for diagnostics
#ifdef DEBUG_INHERITANCE
    Info<< "=== Source Model Debug Info ===" << nl;
    Info<< "Type: " << source->type() << nl;
    Info<< "Address: " << &source() << nl;
    Info<< "Valid: " << source.valid() << nl;
    Info<< "Su field size: " << source->Su().size() << nl;
    Info<< "Sp field size: " << source->Sp().size() << nl;
    Info<< "================================" << nl;
#endif
```

---

## Exercise 5: Advanced Integration - Custom Boundary Condition

### 🎯 Expert Challenge

Create a complete custom boundary condition using inheritance and RTS:

**Requirements:**
1. Inherit from `fixedValueFvPatchField`
2. Add dictionary parameters
3. Implement `updateCoeffs()` for time-varying behavior
4. Register in RTS table
5. Test in actual simulation

### 📝 Template

```cpp
// timeVaryingMappedFvPatchField.H
#ifndef timeVaryingMappedFvPatchField_H
#define timeVaryingMappedFvPatchField_H

#include "fixedValueFvPatchFields.H"

namespace Foam
{

template<class Type>
class timeVaryingMappedFvPatchField
:
    public fixedValueFvPatchField<Type>
{
    // Private data
    autoPtr<Function1<Type>> timeSeries_;
    
public:
    // RTTS
    TypeName("timeVaryingMapped");
    
    // Constructors
    timeVaryingMappedFvPatchField
    (
        const fvPatch&,
        const DimensionedField<Type, volMesh>&
    );
    
    timeVaryingMappedFvPatchField
    (
        const fvPatch&,
        const DimensionedField<Type, volMesh>&,
        const dictionary&
    );
    
    // Implementation
    virtual void updateCoeffs();
    
    // Write
    virtual void write(Ostream&) const;
    
    // - RTS - //
    static autoPtr<fvPatchField<Type>> New
    (
        const fvPatch&,
        const DimensionedField<Type, volMesh>&,
        const dictionary&
    );
};

} // End namespace Foam

#ifdef NoRepository
    #include "timeVaryingMappedFvPatchField.C"
#endif

#endif
```

### 🔑 Key Points

1. **Must inherit** from appropriate `fvPatchField` base
2. **TypeName** must match dictionary `type` entry
3. **updateCoeffs()** called every solver iteration
4. **Use Function1** for time-varying expressions
5. **Register** with `makePatchTypeField`

### 📝 Boundary Condition Dictionary

```cpp
// 0/T
boundaryField
{
    inlet
    {
        type            timeVaryingMapped;
        
        // Time series data
        timeSeries      table
        (
            (0    300)    // (time value)
            (10   350)
            (20   400)
            (30   400)
            (40   300)
        );
        
        value           uniform 300;
    }
}
```

---

## 🎓 Key Takeaways

### Core Concepts

| Concept | Key Points |
|---------|-----------|
| **Inheritance** | Use `virtual` for polymorphic behavior, `override` to enforce correct signatures |
| **RTS** | Requires: `TypeName`, `declareRunTimeSelectionTable`, `New()`, `addToRunTimeSelectionTable` |
| **Polymorphism** | Write solvers to base class interface - extend without modifying solver |
| **autoPtr** | Smart pointer ensuring proper cleanup - use for factory-created objects |

### Best Practices

1. **ALWAYS** use `virtual` destructor in polymorphic base classes
2. **ALWAYS** mark overrides with `override` keyword (C++11)
3. **NEVER** forget `addToRunTimeSelectionTable` in .C file
4. **ALWAYS** check `autoPtr::valid()` before dereferencing
5. **PREFER** composition over inheritance when appropriate

### Common Patterns

**Factory Creation:**
```cpp
autoPtr<Model> obj = Model::New(dictionary, mesh);
```

**Polymorphic Usage:**
```cpp
obj->virtualFunction();  // Dispatches to derived class
```

**Smart Pointer Ownership:**
```cpp
autoPtr<Model> owner = obj.ptr();  // Transfer ownership
```

---

## 📚 Related Documentation

- **Inheritance Fundamentals:** [02_Abstract_Interfaces.md](02_Abstract_Interfaces.md)
- **RTS System:** [04_Run_Time_Selection_System.md](04_Run_Time_Selection_System.md)
- **Design Patterns:** [05_Design_Patterns_in_Physics.md](05_Design_Patterns_in_Physics.md)
- **Error Debugging:** [06_Common_Errors_and_Debugging.md](06_Common_Errors_and_Debugging.md)

---

## 🧪 Testing Checklist

Use this checklist before considering an exercise complete:

- [ ] Compiles without warnings
- [ ] All pure virtual functions implemented
- [ ] RTS registration complete
- [ ] Dictionary file parses correctly
- [ ] Runtime output shows correct model selection
- [ ] Physical results are reasonable
- [ ] Memory leaks checked (valgrind)
- [ ] Multiple models tested without code changes

---

## 🚀 Next Steps

After mastering these exercises:

1. **Explore** OpenFOAM source code for inheritance examples
2. **Create** your own turbulence model subclass
3. **Implement** custom boundary conditions
4. **Contribute** to OpenFOAM extensions repository

---

**End of Practical Exercise**