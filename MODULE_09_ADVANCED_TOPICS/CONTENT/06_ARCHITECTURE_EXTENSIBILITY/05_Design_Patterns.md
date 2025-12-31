# Design Patterns in OpenFOAM Architecture

> **Design patterns** provide proven solutions for extensibility and maintainability in OpenFOAM's architecture.

---

## Learning Objectives

By the end of this section, you will be able to:

1. **Identify** key design patterns used in OpenFOAM's architecture
2. **Map** abstract design patterns to concrete OpenFOAM implementations
3. **Apply** design pattern principles when extending OpenFOAM functionality
4. **Select** appropriate patterns for specific extension scenarios

---

## Overview: Design Patterns for Extensibility

Design patterns in OpenFOAM are **reusable solutions** to common software architecture challenges. They provide:

- **Standardized approaches** for implementing extensibility
- **Clear separation of concerns** between core functionality and extensions
- **Runtime flexibility** through dynamic configuration
- **Type safety** through C++ template mechanisms

### The Four Core Patterns

| Pattern | Purpose | OpenFOAM Implementation |
|---------|---------|------------------------|
| **Plugin** | Dynamic feature loading | `libs ("libmyModels.so")` |
| **Registry** | Centralized object storage | `objectRegistry`, `lookupObject()` |
| **Factory** | Object creation abstraction | `Model::New()`, RTS tables |
| **Observer** | Event-driven behavior | `functionObjects` |

---

## 1. Plugin Pattern

### Pattern Concept
**Separate core functionality from optional features** that can be loaded at runtime without recompilation.

### OpenFOAM Implementation

```cpp
// In controlDict or transportProperties
libs (
    "libmyTurbulenceModels.so"
    "libmyBoundaryConditions.so"
);

// Library contents:
// - Auto-registering models via RTS
// - No solver recompilation needed
// - Features loaded dynamically
```

### Plugin Components

```cpp
// 1. Plugin Library Structure
// myModels/
//     ├── Make/
//     │   ├── files
//     │   └── options
//     └── myTurbulenceModel.C
//         (contains auto-registration)

// 2. Declaration
declareRunTimeSelectionTable
(
    autoPtr,
    turbulenceModel,
    dictionary,
    (
        const incompressible::turbulenceModel::transportModel& transport,
        const volScalarField& rho,
        const volVectorField& U,
        const surfaceScalarField& phi,
        const word& propertiesName
    ),
    (transport, rho, U, phi, propertiesName)
);

// 3. Registration
// In myTurbulenceModel.C
defineTypeNameAndDebug(myTurbulenceModel, 0);
addToRunTimeSelectionTable
(
    turbulenceModel,
    myTurbulenceModel,
    dictionary
);
```

### Benefits

- **No solver modification** — Add features without touching core code
- **Modular distribution** — Share functionality as separate libraries
- **Runtime selection** — Choose features via configuration files
- **Independent development** — Test and deploy plugins separately

### When to Use

✅ **Use Plugin Pattern when:**
- Adding optional physics models
- Providing custom boundary conditions
- Implementing specialized turbulence models
- Creating reusable utilities

❌ **Avoid when:**
- Feature is always required (compile into main code)
- Feature has tight coupling with solver internals

---

## 2. Registry Pattern

### Pattern Concept
**Centralized repository** for objects with lookup capabilities, eliminating the need to pass objects through function call chains.

### OpenFOAM Implementation

```cpp
// Core Registry Class
class objectRegistry
{
    // Hash table for storage
    HashTable<regIOobject*> objects_;
    
    // Parent registry for hierarchical structure
    const objectRegistry& parent_;
    
public:
    // Register object
    bool regIOobject::checkOut();
    
    // Lookup by name and type
    template<class Type>
    const Type& lookupObject(const word& name) const;
    
    template<class Type>
    Type& lookupObjectRef(const word& name);
    
    // Check existence
    template<class Type>
    bool foundObject(const word& name) const;
    
    // Iteration support
    HashTable<const regIOobject*>::iterator begin();
    HashTable<const regIOobject*>::iterator end();
};
```

### Registry Hierarchy

```
Time (top-level registry)
├── mesh (sub-registry)
│   ├── T (volScalarField)
│   ├── p (volScalarField)
│   └── U (volVectorField)
└── controlDict (IOdictionary)
```

### Usage Examples

```cpp
// 1. Field Access in Custom BC
class myFixedValueFvPatchField
:
    public fixedValueFvPatchField
{
    // Direct field lookup
    const volScalarField& T =
        patch().lookupObject<volScalarField>("T");
    
    // Access mesh through registry
    const fvMesh& mesh = patch().boundaryMesh().mesh();
};

// 2. Inter-Field Communication
void computeHeatTransfer()
{
    // Get fields without passing as parameters
    const volScalarField& T = mesh.lookupObject<volScalarField>("T");
    const volScalarField& rho = mesh.lookupObject<volScalarField>("rho");
    const volVectorField& U = mesh.lookupObject<volVectorField>("U");
    
    // Perform computation
    volScalarField h = rho * Cp * T;
}

// 3. FunctionObject Field Access
class myFunctionObject
:
    public functionObject
{
    virtual bool execute()
    {
        // Access runtime fields
        if (mesh_.foundObject<volScalarField>("T"))
        {
            const volScalarField& T =
                mesh_.lookupObject<volScalarField>("T");
            
            // Process field
            Info<< "Max T: " << max(T).value() << endl;
        }
        return true;
    }
};
```

### Benefits

- **Decoupling** — Components access objects without direct references
- **Flexibility** — Add/remove objects without changing function signatures
- **Type safety** — Compile-time type checking via templates
- **Hierarchical organization** — Nested registries for logical grouping

### When to Use

✅ **Use Registry Pattern when:**
- Multiple components need access to shared objects
- Object availability varies at runtime
- Building loosely coupled systems

❌ **Avoid when:**
- Object lifetime is clearly scoped and local
- Direct parameter passing is more explicit

---

## 3. Factory Pattern + Runtime Selection Tables

### Pattern Concept
**Encapsulate object creation** behind a common interface, allowing types to be selected at runtime via configuration.

### OpenFOAM Implementation

```cpp
// 1. Abstract Base Class
class RASModel
:
    public turbulenceModel
{
public:
    // Factory method
    static autoPtr<RASModel> New
    (
        const volScalarField& rho,
        const volVectorField& U,
        const surfaceScalarField& phi,
        const word& propertiesName
    );
    
    // Virtual interface
    virtual tmp<volSymmTensorField> R() const = 0;
    virtual tmp<volScalarField> k() const = 0;
    virtual tmp<volScalarField> epsilon() const = 0;
    
    // Declare RTS table
    declareRunTimeSelectionTable
    (
        autoPtr,
        RASModel,
        dictionary,
        (
            const volScalarField& rho,
            const volVectorField& U,
            const surfaceScalarField& phi,
            const word& propertiesName
        ),
        (rho, U, phi, propertiesName)
    );
};

// 2. Factory Implementation
autoPtr<RASModel> RASModel::New
(
    const volScalarField& rho,
    const volVectorField& U,
    const surfaceScalarField& phi,
    const word& propertiesName
)
{
    // Read model type from dictionary
    const word modelType =
        IOdictionary
        (
            IOobject
            (
                propertiesName,
                U.time().constant(),
                U.mesh(),
                IOobject::MUST_READ,
                IOobject::NO_WRITE
            )
        ).lookup("RASModel")
    
    // Lookup constructor table
    dictionaryConstructorTable::iterator cstrIter =
        dictionaryConstructorTablePtr_->find(modelType);
    
    // Error handling
    if (cstrIter == dictionaryConstructorTablePtr_->end())
    {
        FatalErrorInFunction
            << "Unknown RASModel type " << modelType
            << nl << nl
            << "Valid RASModel types:" << nl
            << dictionaryConstructorTablePtr_->sortedToc()
            << exit(FatalError);
    }
    
    // Create and return object
    return cstrIter()(rho, U, phi, propertiesName);
}

// 3. Concrete Model
class kEpsilon
:
    public RASModel
{
    // Auto-registration
    TypeName("kEpsilon");
    
    // Constructor
    kEpsilon
    (
        const volScalarField& rho,
        const volVectorField& U,
        const surfaceScalarField& phi,
        const word& propertiesName
    );
    
    // Register in RTS table
    addToRunTimeSelectionTable
    (
        RASModel,
        kEpsilon,
        dictionary
    );
    
    // Implementation
    virtual tmp<volSymmTensorField> R() const;
};
```

### Factory + RTS Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                     Configuration Phase                     │
│                                                             │
│  RASProperties  ──────►  Read "kEpsilon"                    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     Factory Method                          │
│                                                             │
│  RASModel::New() ─────►  Lookup "kEpsilon" in table         │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  RTS Table Lookup                           │
│                                                             │
│  ┌─────────────────────────────────────────┐              │
│  │ kEpsilon      ──►  kEpsilon::New()     │              │
│  │ kOmegaSST     ──►  kOmegaSST::New()    │              │
│  │ SpalartAllmaras ─►  SpalartAllmaras::New() │           │
│  └─────────────────────────────────────────┘              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Object Creation                           │
│                                                             │
│  kEpsilon constructor called ──►  kEpsilon object created  │
└─────────────────────────────────────────────────────────────┘
```

### Benefits

- **Runtime flexibility** — Select models via configuration
- **Extensibility** — Add new types without modifying factory
- **Type safety** — Compile-time checking of all constructors
- **Centralized error handling** — Invalid type detection in one place
- **Self-documenting** — `sortedToc()` lists available types

### When to Use

✅ **Use Factory + RTS when:**
- Multiple interchangeable implementations exist
- Runtime selection via configuration is needed
- Adding new implementations frequently

❌ **Avoid when:**
- Only one implementation exists
- Object creation logic is trivial

---

## 4. Observer Pattern (Function Objects)

### Pattern Concept
**Define subscription mechanism** to notify multiple objects about events occurring in observed objects.

### OpenFOAM Implementation

```cpp
// 1. Observer Interface
class functionObject
{
public:
    // Lifecycle hooks
    virtual bool execute() = 0;
    virtual bool write() = 0;
    virtual bool end() = 0;
    virtual bool read(const dictionary&) = 0;
    
    // Time tracking
    virtual const word& name() const = 0;
    virtual scalar timeToNextWrite() = 0;
};

// 2. Subject (Solver)
class simpleSolver
{
    // Function object list (observers)
    functionObjectList functions_;
    
    void loop()
    {
        while (runTime.run())
        {
            runTime++;
            
            // Notify observers
            functions_.execute();
            
            solve();
            
            // Notify observers
            functions_.write();
        }
    }
};

// 3. Concrete Observer
class maxMagUFunctionObject
:
    public functionObject
{
    const fvMesh& mesh_;
    word fieldName_;
    
public:
    maxMagUFunctionObject
    (
        const word& name,
        const Time& runTime,
        const dictionary& dict
    )
    :
        functionObject(name),
        mesh_(runTime.lookupObject<fvMesh>("region0")),
        fieldName_(dict.lookupOrDefault<word>("field", "U"))
    {}
    
    virtual bool execute()
    {
        // Get current field
        const volVectorField& U =
            mesh_.lookupObject<volVectorField>(fieldName_);
        
        // Compute and report
        scalar maxU = max(mag(U)).value();
        Info<< "Max |U|: " << maxU << endl;
        
        return true;
    }
    
    virtual bool write()
    {
        // Optional write to file
        return true;
    }
};
```

### Configuration

```cpp
// In system/controlDict
functions
{
    // Observer 1
    maxVelocity
    {
        type            maxMagU;
        field           U;
        writeInterval   10;
    }
    
    // Observer 2
    heatFluxReport
    {
        type            surfaceRegion;
        functionObjectLibs ("libfieldFunctionObjects.so");
        operation       areaNormalAverage;
        region          type            patch;
        patches         (".*Wall");
        fields          (T);
    }
    
    // Observer 3
    residuals
    {
        type            residuals;
        fields          (p U T);
        tolerance       1e-5;
    }
}
```

### Observer Sequence Diagram

```
┌─────────┐                    ┌──────────────┐                    ┌─────────────────┐
│  Time   │                    │    Solver    │                    │ functionObjects │
└────┬────┘                    └──────┬───────┘                    └────────┬────────┘
     │                               │                                      │
     │  ++runTime                     │                                      │
     ├───────────────────────────────►│                                      │
     │                               │                                      │
     │                               │  execute() called                    │
     │                               ├─────────────────────────────────────►│
     │                               │                                      │
     │                               │                                      │  maxMagU: execute()
     │                               │                                      │  residuals: execute()
     │                               │                                      │
     │                               │  ◄────────────────────────────────── │
     │                               │                                      │
     │                               │  solve()                             │
     │                               ├───────────────────┐                  │
     │                               │                   │                  │
     │                               │  write() called    │                  │
     │                               ├─────────────────────────────────────►│
     │                               │                                      │
     │                               │                                      │  Write outputs
     │                               │                                      │
     │                               │  ◄────────────────────────────────── │
     │                               │                                      │
     │  ◄───────────────────────────│                                      │
     │                               │                                      │
```

### Benefits

- **Non-intrusive** — Add post-processing without solver modification
- **Composable** — Chain multiple function objects
- **Reconfigurable** — Enable/disable via configuration
- **Standardized interface** — Consistent hook points across solvers
- **Extensible** — Create custom function objects

### When to Use

✅ **Use Observer Pattern when:**
- Adding monitoring, logging, or analysis
- Implementing conditional logic during simulation
- Extracting data during runtime
- Cross-cutting concerns (e.g., reporting, validation)

❌ **Avoid when:**
- Logic is core to solver algorithm
- Direct access to solver internal state is required

---

## 5. Pattern Integration in OpenFOAM

### Pattern Interaction Map

```
┌────────────────────────────────────────────────────────────┐
│                      Plugin Pattern                        │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  libmyModels.so ──►  Register in RTS tables          │ │
│  └──────────────────────────────────────────────────────┘ │
└──────────────────────────┬─────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────────┐
│                    Factory + RTS                           │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  Model::New() ──►  Lookup RTS table ──►  Create obj  │ │
│  └──────────────────────────────────────────────────────┘ │
└──────────────────────────┬─────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────────┐
│                     Registry Pattern                       │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  mesh.lookupObject<Model>("modelName")               │ │
│  └──────────────────────────────────────────────────────┘ │
└──────────────────────────┬─────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────────┐
│                    Observer Pattern                        │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  functionObject::execute() ──►  Access via Registry  │ │
│  └──────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

### Real-World Example: Custom Turbulence Model

```cpp
// Plugin Pattern: Compile as separate library
// myTurbulenceModels/Make/files

myTurbulenceModel.C
LIB = $(FOAM_USER_LIBBIN)/libmyTurbulenceModels

// Factory + RTS: Auto-registration
class myTurbulenceModel
:
    public RASModel
{
    TypeName("myModel");
    
    addToRunTimeSelectionTable
    (
        RASModel,
        myTurbulenceModel,
        dictionary
    );
};

// Configuration: Select via dictionary
// constant/turbulenceProperties
RASModel myModel;

myCoeffs
{
    Cmy1     0.13;
    Cmy2     0.5;
}

// Observer: Monitor during simulation
// system/controlDict
functions
{
    turbulenceReport
    {
        type            turbulenceFields;
        functionObjectLibs ("libutilityFunctionObjects.so");
        fields          (k epsilon nut);
    }
    
    customAnalysis
    {
        type            coded;
        // ... custom function object
    }
}

// Runtime: Registry access
void myFunctionObject::execute()
{
    // Registry pattern: Access turbulence model
    const incompressible::RASModel& turbulence =
        mesh_.lookupObject<incompressible::RASModel>
        (
            turbulenceModel::propertiesName
        );
    
    // Access model data
    const volScalarField& k = turbulence.k();
    const volScalarField& epsilon = turbulence.epsilon();
    
    // Perform analysis
    Info<< "Max k: " << max(k).value() << endl;
}
```

---

## 6. Pattern Selection Guide

### Decision Tree

```
Need to add functionality?
│
├─► Add NEW physics model?
│   └─► Use Plugin + Factory + RTS
│       • Compile as library
│       • Auto-register via RTS
│       • Select via dictionary
│
├─► Access existing objects?
│   └─► Use Registry
│       • lookupObject<Type>(name)
│       • Centralized access
│
├─► Add runtime behavior?
│   └─► Use Observer (functionObjects)
│       • execute() at each time step
│       • write() at write intervals
│
└─► Create multiple related objects?
    └─► Use Factory
        • Common interface
        • Runtime type selection
```

### Pattern Comparison

| Aspect | Plugin | Registry | Factory | Observer |
|--------|--------|----------|---------|----------|
| **Primary Use** | Extensibility | Object access | Object creation | Event handling |
| **Configuration** | `libs` | N/A | Dictionary entry | `functions` |
| **Compile-time** | Separate lib | Core + plugins | Base + derived | Core + derived |
| **Runtime impact** | Dynamic loading | Lookup overhead | Virtual dispatch | Callback overhead |
| **Type safety** | High | Template-based | Virtual functions | Virtual functions |

---

## 7. Practical Exercise: Pattern Integration

### Objective
Create a complete example demonstrating all four patterns working together.

### Task: Custom Boundary Condition with Monitoring

#### Part 1: Create Plugin Library

```bash
# Create directory structure
mkdir -p $FOAM_RUN/userLibs/myBoundaryConditions
cd $FOAM_RUN/userLibs/myBoundaryConditions

# Create files
touch myBC.C
touch Make/files
touch Make/options
```

**Make/files:**
```cpp
myBC.C

LIB = $(FOAM_USER_LIBBIN)/libmyBoundaryConditions
```

**Make/options:**
```cpp
EXE_INC = \
    -I$(LIB_SRC)/finiteVolume/lnInclude \
    -I$(LIB_SRC)/meshTools/lnInclude

LIB_LIBS = \
    -lfiniteVolume \
    -lmeshTools
```

#### Part 2: Implement Boundary Condition (Factory + RTS)

```cpp
// myBC.C
#ifndef myBC_C
#define myBC_C

#include "fvPatchFielder.H"
#include "volFields.H"
#include "addToRunTimeSelectionTable.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

class myFixedValueFvPatchField
:
    public fixedValueFvPatchField<scalar>
{
    // Private data
    
    //- Reference field name
    word refFieldName_;
    
    //- Scaling factor
    scalar scale_;


public:
    
    //- Runtime type information
    TypeName("myFixedValue");
    
    // Constructors
    
    myFixedValueFvPatchField
    (
        const fvPatch&,
        const DimensionedField<scalar, volMesh>&
    );
    
    myFixedValueFvPatchField
    (
        const fvPatch&,
        const DimensionedField<scalar, volMesh>&,
        const dictionary&
    );
    
    myFixedValueFvPatchField
    (
        const myFixedValueFvPatchField&,
        const fvPatch&,
        const DimensionedField<scalar, volMesh>&,
        const fvPatchFieldMapper&
    );
    
    myFixedValueFvPatchField
    (
        const myFixedValueFvPatchField&
    );
    
    // Member functions
    
    virtual void updateCoeffs();
    
    virtual void write(Ostream&) const;
    
    // * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
    
    // Build mesh constructor table
    makePatchTypeFieldTypename
    (
        fvPatchScalarField,
        myFixedValueFvPatchField
    );
};

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

myFixedValueFvPatchField::myFixedValueFvPatchField
(
    const fvPatch& p,
    const DimensionedField<scalar, volMesh>& iF
)
:
    fixedValueFvPatchField<scalar>(p, iF),
    refFieldName_("T"),
    scale_(1.0)
{}


myFixedValueFvPatchField::myFixedValueFvPatchField
(
    const fvPatch& p,
    const DimensionedField<scalar, volMesh>& iF,
    const dictionary& dict
)
:
    fixedValueFvPatchField<scalar>(p, iF, dict),
    refFieldName_(dict.lookupOrDefault<word>("refField", "T")),
    scale_(dict.lookupOrDefault<scalar>("scale", 1.0))
{
    // Registry Pattern: Access reference field
    const objectRegistry& db = patch().boundaryMesh().mesh();
    
    if (db.foundObject<volScalarField>(refFieldName_))
    {
        const volScalarField& refField =
            db.lookupObject<volScalarField>(refFieldName_);
        
        Info<< "myBC: Found reference field " << refFieldName_
            << " with range: " << min(refField).value()
            << " to " << max(refField).value() << endl;
    }
}


myFixedValueFvPatchField::myFixedValueFvPatchField
(
    const myFixedValueFvPatchField& ptf,
    const fvPatch& p,
    const DimensionedField<scalar, volMesh>& iF,
    const fvPatchFieldMapper& mapper
)
:
    fixedValueFvPatchField<scalar>(ptf, p, iF, mapper),
    refFieldName_(ptf.refFieldName_),
    scale_(ptf.scale_)
{}


myFixedValueFvPatchField::myFixedValueFvPatchField
(
    const myFixedValueFvPatchField& ptf
)
:
    fixedValueFvPatchField<scalar>(ptf),
    refFieldName_(ptf.refFieldName_),
    scale_(ptf.scale_)
{}


void myFixedValueFvPatchField::updateCoeffs()
{
    if (updated())
    {
        return;
    }
    
    // Registry Pattern: Get reference field
    const objectRegistry& db = patch().boundaryMesh().mesh();
    
    if (db.foundObject<volScalarField>(refFieldName_))
    {
        const volScalarField& refField =
            db.lookupObject<volScalarField>(refFieldName_);
        
        // Calculate boundary values
        scalarField& patchField = *this;
        
        forAll(patchField, i)
        {
            label faceCell = patch().faceCells()[i];
            patchField[i] = scale_ * refField[faceCell];
        }
    }
    
    fixedValueFvPatchField<scalar>::updateCoeffs();
}


void myFixedValueFvPatchField::write(Ostream& os) const
{
    fvPatchField<scalar>::write(os);
    os.writeKeyword("refField") << refFieldName_
        << token::END_STATEMENT << nl;
    os.writeKeyword("scale") << scale_
        << token::END_STATEMENT << nl;
    this->writeEntry("value", os);
}

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

makePatchTypeField(fvPatchScalarField, myFixedValueFvPatchField);

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

} // End namespace Foam

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

#endif
```

#### Part 3: Create Function Object (Observer)

```bash
mkdir -p $FOAM_RUN/userLibs/myFunctionObjects
cd $FOAM_RUN/userLibs/myFunctionObjects
```

**Make/files:**
```cpp
myBCMonitor.C

LIB = $(FOAM_USER_LIBBIN)/libmyFunctionObjects
```

**myBCMonitor.C:**
```cpp
#include "fvMesh.H"
#include "Time.H"
#include "functionObject.H"
#include "addToRunTimeSelectionTable.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

class myBCMonitorFunctionObject
:
    public functionObject
{
    // Private data
    
    const fvMesh& mesh_;
    word patchName_;
    word fieldName_;
    ofstream logFile_;
    scalar lastWriteTime_;


public:
    
    //- Runtime type information
    TypeName("myBCMonitor");
    
    // Constructors
    
    myBCMonitorFunctionObject
    (
        const word& name,
        const Time& runTime,
        const dictionary& dict
    )
    :
        functionObject(name),
        mesh_(runTime.lookupObject<fvMesh>("region0")),
        patchName_(dict.lookup("patch")),
        fieldName_(dict.lookup("field")),
        lastWriteTime_(-1)
    {
        // Open log file
        fileName logPath = runTime.path()/"myBCMonitor_" + patchName_ + ".csv";
        logFile_.open(logPath.c_str());
        
        if (logFile_.good())
        {
            logFile_ << "Time,Min,Max,Avg" << endl;
            Info<< "myBCMonitor: Logging to " << logPath << endl;
        }
    }
    
    virtual ~myBCMonitorFunctionObject()
    {
        if (logFile_.is_open())
        {
            logFile_.close();
        }
    }
    
    
    // Member functions
    
    virtual bool execute()
    {
        // Registry Pattern: Access field
        if (mesh_.foundObject<volScalarField>(fieldName_))
        {
            const volScalarField& field =
                mesh_.lookupObject<volScalarField>(fieldName_);
            
            // Get patch
            label patchID = mesh_.boundaryMesh().findPatchID(patchName_);
            
            if (patchID != -1)
            {
                const fvPatchScalarField& patchField = field.boundaryField()[patchID];
                
                scalar minVal = gMin(patchField);
                scalar maxVal = gMax(patchField);
                scalar avgVal = gAverage(patchField);
                
                // Log to console
                Info<< "myBCMonitor (" << patchName_ << "): "
                    << "min=" << minVal
                    << ", max=" << maxVal
                    << ", avg=" << avgVal << endl;
                
                // Log to file
                if (logFile_.good())
                {
                    logFile_ << mesh_.time().value() << ","
                            << minVal << ","
                            << maxVal << ","
                            << avgVal << endl;
                }
            }
        }
        
        return true;
    }
    
    virtual bool write()
    {
        return true;
    }
    
    virtual bool end()
    {
        return true;
    }
    
    virtual bool read(const dictionary& dict)
    {
        return true;
    }
};

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

defineTypeNameAndDebug(myBCMonitorFunctionObject, 0);
addToRunTimeSelectionTable
(
    functionObject,
    myBCMonitorFunctionObject,
    dictionary
);

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

} // End namespace Foam
```

#### Part 4: Configure and Test

**0/ T:**
```cpp
dimensions      [0 0 0 0 0 0 0];

internalField   uniform 300;

boundaryField
{
    inlet
    {
        type            myFixedValue;  // Plugin + Factory
        refField        T;
        scale           1.2;
        value           uniform 300;
    }
    
    outlet
    {
        type            zeroGradient;
    }
    
    walls
    {
        type            fixedValue;
        value           uniform 350;
    }
}
```

**system/controlDict:**
```cpp
application     simpleFoam;

startFrom       startTime;

startTime       0;

stopAt          endTime;

endTime         1000;

deltaT          0.01;

writeControl    timeStep;

writeInterval   100;

functions
{
    // Observer Pattern
    myInletMonitor
    {
        type            myBCMonitor;
        patch           inlet;
        field           T;
        writeInterval   1;
    }
    
    myWallMonitor
    {
        type            myBCMonitor;
        patch           walls;
        field           T;
        writeInterval   1;
    }
}

// Plugin Pattern: Load custom libraries
libs
(
    "libmyBoundaryConditions.so"
    "libmyFunctionObjects.so"
);
```

#### Part 5: Build and Run

```bash
# Compile libraries
cd $FOAM_RUN/userLibs/myBoundaryConditions
wmake

cd $FOAM_RUN/userLibs/myFunctionObjects
wmake

# Run simulation
cd $FOAM_RUN/testPattern
simpleFoam

# Monitor output
tail -f myBCMonitor_inlet.csv
```

#### Part 6: Verification

```bash
# Check library loading
grep "libmy" log.simpleFoam

# Expected output:
# ;--> FOAM Warning : 
#     From function static_cast<void*>(dlopen(const char*, int))
#     in file dlOpen.C at line 118
#     could not load "libmyBoundaryConditions.so"
#     libmyBoundaryConditions.so: cannot open shared object file: No such file or directory
# 
# Correct output (success):
# libmyBoundaryConditions.so: loaded successfully

# Check function object output
ls -la myBCMonitor_*.csv
cat myBCMonitor_inlet.csv

# Expected CSV format:
# Time,Min,Max,Avg
# 0,360.0,360.0,360.0
# 0.01,360.0,360.0,360.0
# ...

# Check solver logs
grep "myBCMonitor" log.simpleFoam

# Expected output:
# myBCMonitor (inlet): min=360.0, max=360.0, avg=360.0
# myBCMonitor (walls): min=350.0, max=350.0, avg=350.0
```

### Exercise Tasks

1. **[Plugin Pattern]** Compile the boundary condition library
   - Verify library loads correctly
   - Check for compilation errors

2. **[Factory Pattern]** Test boundary condition selection
   - Try changing `scale` parameter
   - Verify runtime selection works

3. **[Registry Pattern]** Modify function object
   - Access additional fields (e.g., `p`, `U`)
   - Implement field combinations

4. **[Observer Pattern]** Add new function objects
   - Create residual calculator
   - Implement gradient monitor

### Expected Results

```
┌─────────────────────────────────────────────────────────────┐
│                    Compilation Success                       │
├─────────────────────────────────────────────────────────────┤
│ wmake libmyBoundaryConditions                               │
│ → libmyBoundaryConditions.so created in $FOAM_USER_LIBBIN   │
├─────────────────────────────────────────────────────────────┤
│ wmake libmyFunctionObjects                                  │
│ → libmyFunctionObjects.so created in $FOAM_USER_LIBBIN      │
├─────────────────────────────────────────────────────────────┤
│ simpleFoam execution                                         │
├─────────────────────────────────────────────────────────────┤
│ Plugin Pattern:                                             │
│ → libmyBoundaryConditions.so: loaded successfully           │
│ → libmyFunctionObjects.so: loaded successfully              │
├─────────────────────────────────────────────────────────────┤
│ Factory + RTS:                                              │
│ → myFixedValue boundary condition instantiated               │
├─────────────────────────────────────────────────────────────┤
│ Registry Pattern:                                           │
│ → Reference field T found: range 300.0 to 350.0             │
├─────────────────────────────────────────────────────────────┤
│ Observer Pattern:                                           │
│ → myBCMonitor (inlet): min=360.0, max=360.0, avg=360.0     │
│ → myBCMonitor (walls): min=350.0, max=350.0, avg=350.0     │
├─────────────────────────────────────────────────────────────┤
│ Output Files:                                               │
│ → myBCMonitor_inlet.csv (time-series data)                 │
│ → myBCMonitor_walls.csv (time-series data)                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Takeaways

### Design Pattern Benefits

1. **Plugin Pattern**
   - Enables **modular development** without recompiling core
   - Facilitates **third-party extensions** and custom models
   - Supports **runtime feature selection**

2. **Registry Pattern**
   - Provides **centralized object management**
   - Eliminates **parameter passing chains**
   - Enables **loose coupling** between components

3. **Factory + RTS Pattern**
   - Encapsulates **object creation complexity**
   - Enables **runtime type selection** via configuration
   - Simplifies **adding new implementations**

4. **Observer Pattern**
   - Implements **event-driven architecture**
   - Enables **non-intrusive monitoring**
   - Supports **composable behaviors**

### Pattern Synergy

```
Plugin ──► Loads library ──► Registers in Factory
                              ↓
                        Creates objects
                              ↓
                        Stores in Registry
                              ↓
                        Observer accesses
```

### Best Practices

✅ **Do:**
- Use patterns for **extensibility points** in your code
- Document **pattern usage** in comments
- Provide **examples** for each pattern
- Test **pattern interactions** thoroughly

❌ **Don't:**
- Force patterns into **simple scenarios**
- Create **unnecessary abstraction layers**
- Ignore **performance implications**
- Mix patterns **inconsistently**

---

## References

### Internal Documentation
- **Overview:** [00_Overview.md](00_Overview.md)
- **RTS Details:** [02_Runtime_Selection_Tables.md](02_Runtime_Selection_Tables.md)
- **Dynamic Loading:** [03_Dynamic_Library_Loading.md](03_Dynamic_Library_Loading.md)
- **Function Objects:** [04_FunctionObject_Integration.md](04_FunctionObject_Integration.md)

### External Resources
- **Design Patterns:** Gamma, Helm, Johnson, Vlissides (1994). *Design Patterns: Elements of Reusable Object-Oriented Software*
- **OpenFOAM Code:** `$FOAM_SRC/OpenFOAM/db/RunTimeSelection/`
- **Function Objects:** `$FOAM_SRC/OpenFOAM/db/functionObjects/`