# Runtime Selection Tables

Creating Objects from Strings at Runtime

---

## 🎯 Learning Objectives

By the end of this section, you will be able to:

- **Explain** the Runtime Selection Tables (RTS) mechanism and its role in OpenFOAM's plugin architecture
- **Implement** the complete RTS workflow: declare tables, register classes, and create factory methods
- **Write** production-ready RTS code with proper error handling and type safety
- **Debug** common RTS issues using logging and validation techniques
- **Compare** RTS with other extensibility mechanisms (inheritance, templates) and choose appropriately

---

## Overview

**Runtime Selection Tables (RTS)** is OpenFOAM's factory pattern implementation that enables object creation from string identifiers at runtime. It decouples interface definitions from concrete implementations, allowing users to select models/schemes through dictionary files without code modification or recompilation.

**Key Concept**: RTS transforms compile-time constructor calls into runtime string-based dispatch, enabling the plugin architecture that makes OpenFOAM extensible.

### Position in Extensibility Framework

| Mechanism | What It Solves | When To Use |
|-----------|----------------|-------------|
| **Inheritance/Polymorphism** | Type hierarchies & virtual dispatch | Multiple types with common interface |
| **Runtime Selection Tables** | String-based object creation | User-selectable models, schemes, BCs |
| **Template Metaprogramming** | Compile-time code generation | Type-safe generic algorithms |
| **Dynamic Library Loading** | Plugin discovery without relinking | Optional/additional functionality |

---

## 1. Architecture and Mechanism

### 1.1 Complete Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│                        RTS ARCHITECTURE                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  DECLARATION (Base Class Header)                                    │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ declareRunTimeSelectionTable                                │   │
│  │   - Creates static hash table                               │   │
│  │   - Defines constructor pointer type                        │   │
│  │   - Declares lookup function                                │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                    ↓                                │
│  REGISTRATION (Derived Class .C file)                              │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ addToRunTimeSelectionTable                                   │   │
│  │   - Adds entry to hash table                                │   │
│  │   - Maps: string → constructor pointer                      │   │
│  │   - Runs at static initialization                           │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                    ↓                                │
│  FACTORY METHOD (Base Class .C file)                               │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ ClassName::New()                                             │   │
│  │   - Reads "type" from dictionary                            │   │
│  │   - Looks up constructor in table                           │   │
│  │   - Invokes constructor, returns object                     │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                    ↓                                │
│  USAGE (Application Code)                                           │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ autoPtr<ClassName> obj = ClassName::New(dict);              │   │
│  │ obj->method();                                              │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 What Makes RTS Work

**Static Initialization Order**: Registration happens during program startup (before `main()`) via static variable initialization. This ensures all derived classes are registered before any lookup occurs.

**Hash Table Lookup**: OpenFOAM uses `HashTable` for O(1) string-to-constructor mapping, making object creation efficient.

**autoPtr Ownership**: Factory methods return `autoPtr` to transfer ownership unambiguously—caller receives a new object and is responsible for its lifetime.

---

## 2. Complete Implementation Example

Below is a **minimal, complete, runnable example** showing all RTS pieces working together.

### 2.1 Base Class Declaration

```cpp
// BaseModel.H
#ifndef BaseModel_H
#define BaseModel_H

#include "dictionary.H"
#include "autoPtr.H"

namespace Foam
{

// Abstract base class
class BaseModel
{
protected:
    word name_;
    dictionary dict_;


public:
    // Runtime type information
    TypeName("BaseModel");

    // Declare runtime selection table
    declareRunTimeSelectionTable
    (
        autoPtr,              // Return type
        BaseModel,            // Base class name
        dictionary,           // Lookup table name
        (const dictionary& dict, const word& name),  // Constructor signature
        (dict, name)          // Constructor parameters
    );

    // Constructors
    BaseModel(const dictionary& dict, const word& name)
    :
        name_(name),
        dict_(dict)
    {
        Info << "Constructing BaseModel: " << name_ << endl;
    }

    // Destructor
    virtual ~BaseModel()
    {
        Info << "Destroying BaseModel: " << name_ << endl;
    }

    // Virtual interface
    virtual void compute() = 0;

    // Factory method
    static autoPtr<BaseModel> New(const dictionary& dict);
};

} // End namespace Foam

#endif
```

### 2.2 Derived Class Registration

```cpp
// LinearModel.C
#include "BaseModel.H"
#include "addToRunTimeSelectionTable.H"

// Define derived class
class LinearModel
:
    public BaseModel
{
    scalar coefficient_;

public:
    // Register type name
    TypeName("LinearModel");

    // Constructor
    LinearModel(const dictionary& dict, const word& name)
    :
        BaseModel(dict, name),
        coefficient_(dict.lookupOrDefault<scalar>("coeff", 1.0))
    {
        Info << "  Constructing LinearModel with coeff=" << coefficient_ << endl;
    }

    // Implementation
    virtual void compute()
    {
        Info << "  LinearModel::compute() -> y = " << coefficient_ << " * x" << endl;
    }

    // Destructor
    virtual ~LinearModel()
    {
        Info << "  Destroying LinearModel" << endl;
    }
};

// Add to runtime selection table
addToRunTimeSelectionTable
(
    BaseModel,
    LinearModel,
    dictionary
);

// Another derived class
class QuadraticModel
:
    public BaseModel
{
    scalar a_, b_;

public:
    TypeName("QuadraticModel");

    QuadraticModel(const dictionary& dict, const word& name)
    :
        BaseModel(dict, name),
        a_(dict.lookupOrDefault<scalar>("a", 1.0)),
        b_(dict.lookupOrDefault<scalar>("b", 0.0))
    {
        Info << "  Constructing QuadraticModel with a=" << a_ << ", b=" << b_ << endl;
    }

    virtual void compute()
    {
        Info << "  QuadraticModel::compute() -> y = " << a_ << " * x² + " << b_ << " * x" << endl;
    }

    virtual ~QuadraticModel()
    {
        Info << "  Destroying QuadraticModel" << endl;
    }
};

addToRunTimeSelectionTable
(
    BaseModel,
    QuadraticModel,
    dictionary
);
```

### 2.3 Factory Method Implementation

```cpp
// BaseModel.C
#include "BaseModel.H"

// Define the selection table
defineTypeNameAndDebug(BaseModel, 0);

// Add constructor table to hash table
defineRunTimeSelectionTable(BaseModel, dictionary);

// Factory method
autoPtr<BaseModel> BaseModel::New(const dictionary& dict)
{
    // Read model type from dictionary
    word modelName(dict.lookup("type"));

    // Log for debugging
    Info << "BaseModel::New: Creating model '" << modelName << "'" << endl;

    // Lookup constructor pointer in table
    autoPtrConstructorTable::iterator cstrIter =
        dictionaryConstructorTablePtr_->find(modelName);

    // Check if model exists
    if (cstrIter == dictionaryConstructorTablePtr_->end())
    {
        FatalErrorInFunction
            << "Unknown BaseModel type '" << modelName << "'"
            << nl << "Valid types:" << nl
            << dictionaryConstructorTablePtr_->sortedToc()
            << exit(FatalError);
    }

    // Call constructor through pointer
    return autoPtr<BaseModel>(cstrIter()(dict, modelName));
}
```

### 2.4 Usage in Application

```cpp
// mainTest.C
#include "BaseModel.H"

using namespace Foam;

int main()
{
    // Example 1: Linear model
    {
        Info << "\n=== Test 1: Linear Model ===" << endl;
        dictionary dict;
        dict.add("type", word("LinearModel"));
        dict.add("coeff", 2.5);

        autoPtr<BaseModel> model = BaseModel::New(dict);
        model->compute();
    } // autoPtr destroys object here

    // Example 2: Quadratic model
    {
        Info << "\n=== Test 2: Quadratic Model ===" << endl;
        dictionary dict;
        dict.add("type", word("QuadraticModel"));
        dict.add("a", 3.0);
        dict.add("b", 1.5);

        autoPtr<BaseModel> model = BaseModel::New(dict);
        model->compute();
    }

    Info << "\n=== All tests completed ===" << endl;
    return 0;
}
```

### 2.5 Compilation and Execution

```bash
# Compilation (assuming wmake)
cd $FOAM_USER_LIBBIN
wmake

# Execution
./mainTest

# Expected output:
# BaseModel::New: Creating model 'LinearModel'
# Constructing BaseModel: model1
#   Constructing LinearModel with coeff=2.5
#   LinearModel::compute() -> y = 2.5 * x
#   Destroying LinearModel
# Destroying BaseModel: model1
#
# BaseModel::New: Creating model 'QuadraticModel'
# Constructing BaseModel: model2
#   Constructing QuadraticModel with a=3, b=1.5
#   QuadraticModel::compute() -> y = 3 * x² + 1.5 * x
#   Destroying QuadraticModel
# Destroying BaseModel: model2
#
# === All tests completed ===
```

---

## 3. Macro Reference

### 3.1 Declaration Macros

Used in **base class header** to declare the selection table.

| Macro | Purpose | Parameters |
|-------|---------|------------|
| `TypeName(name)` | Sets runtime type name | String literal |
| `declareRunTimeSelectionTable(...)` | Declares the selection table | See below |

**declareRunTimeSelectionTable Parameters**:

```cpp
declareRunTimeSelectionTable(
    ReturnType,        // autoPtr, tmp, or PtrList
    ClassName,         // Base class name
    TableName,         // Table identifier (e.g., dictionary)
    (ConstructorArgs), // Constructor signature with parentheses
    (ActualArgs)       // Constructor parameters without types
);
```

### 3.2 Definition Macros

Used in **derived class source** files to register with the table.

| Macro | Purpose | Location |
|-------|---------|----------|
| `defineTypeNameAndDebug(Type, Debug)` | Define type name & debug switch | Top of .C file |
| `addToRunTimeSelectionTable(...)` | Register class constructor | After class definition |

**addToRunTimeSelectionTable Parameters**:

```cpp
addToRunTimeSelectionTable(
    BaseClassName,   // Base class name
    DerivedClassName,// Derived class name
    TableName        // Same as in declareRunTimeSelectionTable
);
```

### 3.3 Factory Method Pattern

Standard factory method signature:

```cpp
static autoPtr<BaseClass> New(
    const dictionary& dict
);
```

Implementation steps:
1. Read "type" keyword from dictionary
2. Look up in constructor table
3. Call constructor through pointer
4. Return autoPtr for ownership transfer

---

## 4. Advanced Patterns

### 4.1 Multiple Constructor Signatures

Classes can support multiple selection tables:

```cpp
// Base class with two construction methods
class fvPatch
{
    // Dictionary-based construction
    declareRunTimeSelectionTable
    (
        autoPtr,
        fvPatch,
        dictionary,
        (const polyPatch& patch, const fvBoundaryMesh& bm),
        (patch, bm)
    );

    // Mapper-based construction (for mesh-to-mesh mapping)
    declareRunTimeSelectionTable
    (
        autoPtr,
        fvPatch,
        mapper,
        (const fvPatch& patch, const fvPatchMapper& mapper),
        (patch, mapper)
    );
};
```

### 4.2 Optional Registration with Debug

```cpp
// Conditional registration (useful for experimental models)
#ifdef EXPERIMENTAL_FEATURES
    addToRunTimeSelectionTable
    (
        BaseModel,
        ExperimentalModel,
        dictionary
    );
#endif
```

### 4.3 Registration with Additional Metadata

```cpp
// Store model capabilities in static registry
static void registerModel()
{
    addToRunTimeSelectionTable(BaseModel, MyModel, dictionary);
    
    // Additional metadata
    ModelRegistry::instance().addCapability
    (
        MyModel::typeName,
        {"steady-state", "compressible", "RANS"}
    );
}

// Call at static initialization
namespace { MyModelRegistration reg; }
```

---

## 5. Error Handling and Debugging

### 5.1 Common Issues

| Symptom | Cause | Solution |
|---------|-------|----------|
| "Unknown type" error | Class not registered | Check `addToRunTimeSelectionTable` is compiled |
| Segmentation fault | Wrong constructor signature | Match parameters in declare/register |
| Linker errors | Missing `defineRunTimeSelectionTable` | Add to base class .C file |
| Multiple definitions | Header-only implementation | Move registration to .C file |

### 5.2 Debugging Techniques

**List Available Models**:

```cpp
// In factory method
Info << "Available models:" << nl
    << dictionaryConstructorTablePtr_->sortedToc() << endl;
```

**Trace Registration**:

```cpp
// In derived class constructor
addToRunTimeSelectionTable(...);

// Add debug output
if (debug)
{
    Info << "Registered: " << DerivedClassName::typeName << endl;
}
```

**Validate Dictionary**:

```cpp
// Before lookup
if (!dict.found("type"))
{
    FatalErrorInFunction
        << "Missing 'type' entry in dictionary"
        << exit(FatalError);
}
```

### 5.3 Production Error Handling

```cpp
autoPtr<BaseModel> BaseModel::New(const dictionary& dict)
{
    word modelName;
    
    // Safe lookup with validation
    if (!dict.readIfPresent("type", modelName))
    {
        // Try default
        modelName = dict.lookupOrDefault<word>("defaultType", "StandardModel");
        WarningInFunction
            << "No 'type' specified, using default: " << modelName << endl;
    }

    // Lookup with detailed error reporting
    auto cstrIter = dictionaryConstructorTablePtr_->find(modelName);
    
    if (cstrIter == dictionaryConstructorTablePtr_->end())
    {
        // Provide helpful error message
        FatalErrorInFunction
            << "Unknown model type: " << modelName << nl
            << "Available types:" << nl
            << indent << dictionaryConstructorTablePtr_->sortedToc() << nl
            << nl
            << "Did you mean:"
            << suggestSimilar(modelName, dictionaryConstructorTablePtr_->sortedToc())
            << exit(FatalError);
    }

    // Create object
    return cstrIter()(dict);
}
```

---

## 6. Best Practices

### 6.1 DO ✓

- **Use descriptive type names** that match dictionary entries
- **Register in .C files** (not headers) to avoid linker errors
- **Return autoPtr** from factory methods for clear ownership semantics
- **Provide helpful error messages** listing available types
- **Document required dictionary entries** in class comments
- **Use const references** for large constructor parameters
- **Validate constructor parameters** before returning from factory

### 6.2 DON'T ✗

- **Don't forget `TypeName` macro**—required for registration
- **Don't mix signatures** between declare and register macros
- **Don't use raw pointers** for factory returns (prefer autoPtr)
- **Don't suppress registration errors**—they indicate real problems
- **Don't create cycles** in initialization dependencies
- **Don't assume registration order**—it's implementation-dependent

---

## 🎓 Key Takeaways

- **RTS enables plugin architecture** by mapping string identifiers to constructor pointers at runtime
- **Three-piece implementation**: (1) Declare table in base class, (2) Register derived classes, (3) Provide factory method
- **Static initialization** performs registration before `main()` executes, ensuring availability at lookup time
- **HashTable lookup** provides O(1) object creation from dictionary "type" entries
- **autoPtr return** transfers ownership unambiguously—caller receives a new object and manages its lifetime
- **Multiple constructor signatures** can coexist via separate selection tables
- **Error messages** should list available types to help users debug configuration errors
- **Use RTS when**: User needs model selection, supporting plugins, avoiding recompilation for extensions
- **Prefer alternatives when**: All types known at compile-time (use templates), performance critical (avoid indirection)

---

## 📚 Further Reading

- **Related Topics**:
  - [03_Dynamic_Library_Loading.md](03_Dynamic_Library_Loading.md) — Loading plugins without relinking
  - [04_Run_Time_Selection_System.md](04_Run_Time_Selection_System.md) — Complete RTS architecture
- **OpenFOAM Source**:
  - `src/OpenFOAM/db/runTimeSelection/` — Implementation
  - `src/turbulenceModels` — Extensive RTS examples
- **Design Patterns**:
  - Factory Pattern motivation and implementation
  - Plugin architecture best practices

---

## 🔍 Quick Reference

| Aspect | Syntax/Location |
|--------|-----------------|
| **Declare Table** | `declareRunTimeSelectionTable(autoPtr, Base, dict, (args), (params))` |
| **Define Table** | `defineRunTimeSelectionTable(Base, dict)` in .C file |
| **Register Class** | `addToRunTimeSelectionTable(Base, Derived, dict)` in .C file |
| **Factory Method** | `static autoPtr<Base> New(const dictionary& dict)` |
| **Usage** | `autoPtr<Base> obj = Base::New(dict);` |
| **Dictionary Format** | `type ModelName;` |