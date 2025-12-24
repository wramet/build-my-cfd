# 06 Common Errors and Debugging in Multiphase Solvers

## Correct Usage: Dictionary-Driven Configuration

In OpenFOAM's multiphase solver architecture, the dictionary-driven configuration system enables creation of general-purpose solvers that can handle any phase configuration without code modification. This approach demonstrates the power of factory patterns combined with runtime polymorphism.

The phase properties dictionary (`constant/phaseProperties`) defines all phases and their thermophysical properties:

```cpp
// constant/phaseProperties
phases (water air);

water {
    type            pure;
    rho             uniform 1000;
    mu              uniform 0.001;
}

air {
    type            pure;
    rho             uniform 1.225;
    mu              uniform 1.8e-5;
}
```

**📚 Source:**
`constant/phaseProperties` - Runtime configuration dictionary for multiphase simulations

**💡 Explanation:**
This dictionary file demonstrates OpenFOAM's configuration-driven approach where phase properties are defined at runtime rather than compile-time. The `phases` keyword lists all phase names, followed by individual phase blocks specifying transport properties (density `rho` and viscosity `mu`). This format allows the same solver binary to handle arbitrary phase combinations.

**🎯 Key Concepts:**
- Dictionary-driven configuration
- Runtime polymorphism
- Phase property specification
- Factory pattern preparation

The solver code remains completely generic, automatically creating configured phases through the factory system:

```cpp
// Generate interfacial models from dictionary configuration
this->generateInterfacialModels(dragModels_);
this->generateInterfacialModels(virtualMassModels_);
this->generateInterfacialModels(liftModels_);
```

**📚 Source:**
`.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C:56-60`

**💡 Explanation:**
The `generateInterfacialModels()` template method reads phase interface definitions from dictionaries and instantiates appropriate model objects using the runtime selection table. This demonstrates the factory pattern where concrete model types are created based on dictionary entries without hard-coded class names.

**🎯 Key Concepts:**
- Template-based model generation
- Runtime selection tables
- Hash table storage for models
- Automatic object instantiation

This design pattern enables a single solver binary to handle any combination of phases, with new phase types added through registration rather than code modification.

---

## Error 1: Object Slicing

Object slicing is a critical C++ error that occurs when an object of a derived class is passed by value to a function expecting a base class object. This slices off the derived class portion, causing incorrect polymorphic behavior.

### Problem

Passing by value copies only the base `phaseModel` portion, losing derived class information:

```cpp
// WRONG: Pass-by-value causes derived object slicing
void processPhase(phaseModel phase) {  // Copies only phaseModel portion
    phase.correct();  // Always calls phaseModel::correct(), never derived implementation
}
```

**📚 Source:**
Generic C++ polymorphism principle - applicable to all OpenFOAM phase models

**💡 Explanation:**
When a derived class object is passed by value to a function expecting base class, C++ creates a base class object through "object slicing." Only base class members are copied, derived class data is lost, and virtual dispatch calls base implementations instead of derived ones.

**🎯 Key Concepts:**
- Object slicing mechanism
- Value vs reference semantics
- Virtual function dispatch
- Memory layout differences

### Solution

Pass by reference to preserve polymorphism:

```cpp
// CORRECT: Pass-by-reference preserves polymorphism
void processPhase(const phaseModel& phase) {  // Reference to actual object
    phase.correct();  // Calls derived class implementation via virtual dispatch
}
```

**📚 Source:**
Standard C++ best practice - used throughout OpenFOAM codebase

**💡 Explanation:**
Passing by reference (`&`) avoids copying and preserves the complete object including derived class portions. Virtual function calls correctly dispatch to derived class implementations through the vtable mechanism.

**🎯 Key Concepts:**
- Reference semantics
- Virtual dispatch tables
- const correctness
- Interface-based programming

### Best Practice

Use smart pointers for both polymorphism and ownership management:

```cpp
// BEST: Use smart pointers for automatic memory management
void processPhase(autoPtr<phaseModel> phase) {
    phase->correct();  // Clear ownership semantics with automatic cleanup
}
```

**📚 Source:`
OpenFOAM memory management pattern - consistent with `autoPtr<T>` usage in `src/OpenFOAM/memory/autoPtr.H`

**💡 Explanation:**
`autoPtr` provides exclusive ownership semantics with automatic destruction. The arrow operator (`->`) dereferences the pointer while maintaining ownership clarity. This pattern combines polymorphism with RAII (Resource Acquisition Is Initialization) principles.

**🎯 Key Concepts:**
- RAII idiom
- Exclusive ownership
- Automatic resource management
- Exception safety

---

## Error 2: Missing Virtual Destructor

When using polymorphic base classes, virtual destructors are necessary to ensure proper cleanup when deleting derived objects through base class pointers.

### Problem

Memory leaks with derived classes:

```cpp
// WRONG: Memory leak with derived classes
class dragModel {
public:
    ~dragModel() {}  // Non-virtual destructor
};

class SchillerNaumann : public dragModel {
    volScalarField* customField_;  // Allocated in constructor
public:
    ~SchillerNaumann() { delete customField_; }  // Never called through base pointer
};

// Usage:
dragModel* model = new SchillerNaumann(dict);
delete model;  // Calls only dragModel::~dragModel() - memory leak!
```

**📚 Source:`
`.applications/solvers/multiphase/multiphaseEulerFoam/interfacialModels/dragModel/dragModel.H`

**💡 Explanation:**
Deleting a derived object through a base class pointer without virtual destructor causes undefined behavior. Most implementations call only the base destructor, leaving derived resources leaked. The C++ standard considers this undefined behavior.

**🎯 Key Concepts:**
- Destructor dispatch
- Resource cleanup
- Undefined behavior
- Memory leak patterns

### Solution

Virtual destructor ensures proper cleanup:

```cpp
// CORRECT: Virtual destructor ensures proper cleanup
class dragModel {
public:
    virtual ~dragModel() = default;  // Virtual destructor
};
```

**📚 Source:`
`.applications/solvers/multiphase/multiphaseEulerFoam/interfacialModels/dragModel/dragModel.H` (base class pattern)

**💡 Explanation:**
Declaring `virtual` ensures derived destructors are called correctly through base pointers. The `= default` syntax requests compiler-generated destructor implementation while maintaining virtual dispatch.

**🎯 Key Concepts:**
- Virtual destructor declaration
- Polymorphic deletion safety
- Compiler-generated defaults
- C++11 syntax

**⚠️ Remember:** When a base class has any virtual functions, always declare a virtual destructor to avoid undefined behavior and memory leaks.

---

## Error 3: Bypassing the Factory System

Creating objects directly bypasses OpenFOAM's powerful factory registration system, losing the benefits of runtime extensibility and configuration-driven object creation.

### Problem

Hardcoded type creation requires code changes for new types:

```cpp
// WRONG: Hardcoded type creation
autoPtr<phaseModel> phase(new purePhaseModel(dict, mesh));
// Adding new phase types requires code changes throughout codebase
```

**📚 Source:`
Anti-pattern - contradicts factory pattern in `MomentumTransferPhaseSystem.C`

**💡 Explanation:**
Direct instantiation hardcodes concrete types into the solver, violating the Open-Closed Principle (open for extension, closed for modification). Every new phase type requires recompilation of dependent code.

**🎯 Key Concepts:**
- Tight coupling
- Compile-time dependencies
- Violation of Open-Closed Principle
- Configuration vs hardcoding

### Solution

Use factory method for extensible object creation:

```cpp
// CORRECT: Use factory method
autoPtr<phaseModel> phase = phaseModel::New(dict, mesh);
// New phase types added through registration only - no code changes needed
```

**📚 Source:`
`.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C:56-60`

**💡 Explanation:**
The `New()` static factory method looks up the type name in the runtime selection table and calls the appropriate constructor through registered function pointers. New types are added solely through registration macros without modifying existing code.

**🎯 Key Concepts:**
- Factory method pattern
- Runtime type lookup
- Registration-based extension
- Dictionary-driven instantiation

### Benefits of Factory Pattern

The factory pattern enables:
- Runtime registration of new types
- Dictionary-driven object creation
- Extensible architecture without core code modification

---

## Error 4: Incorrect Constructor Signature

Factory patterns require derived classes to match base class constructor signatures exactly for successful object creation through `addToRunTimeSelectionTable`.

### Problem

Constructor signature doesn't match factory requirements:

```cpp
// WRONG: Doesn't match factory signature
class badPhaseModel : public phaseModel {
public:
    badPhaseModel(const fvMesh& mesh) {}  // Missing dictionary parameter
    // addToRunTimeSelectionTable will fail at compile or runtime
};
```

**📚 Source:`
Common error pattern - violates factory signature requirements in OpenFOAM registration macros

**💡 Explanation:**
Runtime selection tables store constructor function pointers with specific signatures. Mismatched signatures cannot be cast to the expected function pointer type, causing compilation failures or runtime crashes when attempting instantiation.

**🎯 Key Concepts:**
- Function pointer types
- Signature matching
- Type safety in factories
- Constructor forwarding

### Solution

Match base factory signature exactly:

```cpp
// CORRECT: Match base factory signature exactly
class goodPhaseModel : public phaseModel {
public:
    goodPhaseModel(const dictionary& dict, const fvMesh& mesh)
    : phaseModel(dict, mesh) {}  // Proper base constructor delegation
};
```

**📚 Source:`
Constructor signature pattern from phase model implementations

**💡 Explanation:**
The derived constructor must accept the exact parameters expected by the factory table and forward them to the base constructor through the initialization list. This ensures proper object initialization and compatibility with the runtime selection mechanism.

**🎯 Key Concepts:**
- Constructor delegation
- Initialization lists
- Parameter forwarding
- Base class initialization

OpenFOAM's runtime selection tables require exact signature matching:
- `const dictionary& dict` parameter for configuration
- `const fvMesh& mesh` parameter for mesh reference
- Proper base constructor delegation

This ensures the factory can consistently create objects through the `New(dict, mesh)` interface used throughout OpenFOAM's multiphase solver architecture.

---

## Error 5: Missing Runtime Type Information

OpenFOAM uses the `TypeName()` macro to identify class types at runtime. Missing this macro prevents the RTS system from locating and creating objects.

### Problem

```cpp
// WRONG: Missing TypeName macro
class myCustomPhase : public phaseModel {
    // No TypeName() declaration
    // Factory system cannot identify this type
};
```

**📚 Source:`
OpenFOAM RTTI system - defined in `src/OpenFOAM/db/RunTimeSelections/typeInfo.H`

**💡 Explanation:**
The `TypeName()` macro declares static type name information used by the runtime selection table for dictionary lookup. Without it, the factory cannot associate dictionary type names with concrete classes during instantiation.

**🎯 Key Concepts:**
- Runtime type identification
- String-based type lookup
- Static type name storage
- Factory registration keys

### Solution

```cpp
// CORRECT: Declare TypeName in class
class myCustomPhase : public phaseModel {
public:
    TypeName("myCustomPhase");  // Required for RTS
    // ... rest of implementation
};
```

**📚 Source:`
Standard pattern in all OpenFOAM model classes (e.g., drag models, phase models)

**💡 Explanation:**
The `TypeName("myCustomPhase")` macro expands to declare static `typeName` and runtime type information methods. The string parameter must match the type name used in dictionaries for instantiation.

**🎯 Key Concepts:**
- Macro expansion
- Static member declaration
- Type name string literal
- Dictionary-to-class mapping

---

## Error 6: Forgetting to Register with Run-Time Selection Table

After creating a new class, it must be registered with the factory system via the `addToRunTimeSelectionTable` macro. Missing this registration prevents the class from being instantiated through dictionaries.

### Problem

```cpp
// Class properly implemented but not registered
class myCustomPhase : public phaseModel {
public:
    TypeName("myCustomPhase");
    myCustomPhase(const dictionary& dict, const fvMesh& mesh);
    // ... Missing registration in .C file
};

// In .C file, missing:
// addToRunTimeSelectionTable(phaseModel, myCustomPhase, dictionary);
```

**📚 Source:`
Common registration error - violates OpenFOAM's extensibility model

**💡 Explanation:**
The class definition alone doesn't add it to the runtime selection table. The registration macro creates a static table entry that maps the type name to a constructor function pointer. Without registration, the factory cannot find the class during `New()` calls.

**🎯 Key Concepts:**
- Static initialization
- Constructor function pointers
- Table entry creation
- Linkage requirements

### Solution

```cpp
// In .C file, must have registration:
addToRunTimeSelectionTable
(
    phaseModel,
    myCustomPhase,
    dictionary
);
```

**📚 Source:`
`.applications/solvers/multiphase/multiphaseEulerFoam/interfacialModels/dragModel/dragModels/SchillerNaumann/SchillerNaumann.C` (registration example)

**💡 Explanation:**
This macro expands to code that creates a static object whose constructor adds the class to the runtime selection table before `main()` executes. The three parameters specify base class, derived class, and constructor table type.

**🎯 Key Concepts:**
- Static table population
- Macro code generation
- Constructor table specification
- Pre-main initialization

---

## Debug Technique: Checking Factory Registration

When experiencing runtime selection issues, use the following utility to verify which models are registered:

```cpp
// Utility to check registration status
template<class BaseType>
void listRegisteredModels() {
    Info << "Registered " << BaseType::typeName << " models:" << nl;
    const auto& table = BaseType::dictionaryConstructorTable();
    forAllConstIter(typename BaseType::dictionaryConstructorTable, table, iter) {
        Info << "  " << iter.key() << nl;
    }
}

// Use in development:
listRegisteredModels<phaseModel>();
listRegisteredModels<dragModel>();
```

**📚 Source:`
Debug utility pattern for OpenFOAM runtime selection tables

**💡 Explanation:**
This template function accesses the static `dictionaryConstructorTable()` member of the base class, iterating through all registered entries and printing their type name keys. Useful for verifying successful registration and diagnosing factory issues.

**🎯 Key Concepts:**
- Template utility functions
- Hash table iteration
- Static member access
- Runtime type introspection

When implementing custom models, perform this verification check immediately after compilation to confirm successful registration.

---

## Summary of Best Practices

1. **Always Use References or Pointers** for passing polymorphic objects to avoid object slicing

2. **Declare Virtual Destructors** in every base class with virtual functions

3. **Use Factory Methods** (`New()`) instead of direct object construction

4. **Verify Constructor Signatures** match factory table requirements exactly

5. **Use TypeName Macro** for runtime type information

6. **Register with addToRunTimeSelectionTable** in .C files for all derived classes

7. **Check Registration** after compilation to confirm models are added to runtime selection tables

8. **Use Smart Pointers** (`autoPtr`, `tmp`) for safe memory management