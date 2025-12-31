# Inheritance & Polymorphism - Introduction

บทนำ Inheritance และ Polymorphism

---

## Learning Objectives

**By the end of this file, you will be able to:**

1. **Explain** the fundamental concepts of inheritance and polymorphism using the **What-Why-How framework**
2. **Compare** code with and without inheritance to understand concrete benefits
3. **Identify** specific OpenFOAM use cases where polymorphism enables flexibility
4. **Write** basic inheritance code with virtual functions and proper override syntax
5. **Trace** virtual function dispatch from base class pointer to derived implementation

---

## 1. What is Inheritance?

### 1.1 Definition (What?)

**Inheritance** is a mechanism where a derived class inherits members (data and functions) from a base class, establishing an "is-a" relationship between types.

```cpp
class Derived : public Base { ... };
```

### 1.2 Benefits (Why?)

| Benefit | Description |
|---------|-------------|
| **Code reuse** | Share common implementations across multiple derived classes |
| **Type hierarchy** | Model relationships (e.g., `kEpsilon` **is a** `RASModel`) |
| **Polymorphism** | Enable uniform treatment of different types through base interface |
| **Extensibility** | Add new types without modifying existing code |

### 1.3 Implementation (How?)

```cpp
// Base class
class Shape
{
protected:
    point center_;
public:
    virtual scalar area() const = 0;  // Pure virtual
};

// Derived class
class Circle : public Shape
{
    scalar radius_;
public:
    virtual scalar area() const override
    {
        return M_PI * sqr(radius_);
    }
};
```

---

## 2. What is Polymorphism?

### 2.1 Definition (What?)

**Polymorphism** is the ability of objects of different types to respond to the same function call in different ways, achieved through virtual functions and base class pointers/references.

### 2.2 Benefits (Why?)

| Benefit | Description |
|---------|-------------|
| **Flexibility** | Write code that works with multiple types through common interface |
| **Extensibility** | Add new types without modifying existing client code |
| **Runtime dispatch** | Select behavior dynamically based on actual object type |

### 2.3 Implementation (How?)

```cpp
// Use base pointer/reference
Shape* shape = new Circle(1.0);
scalar a = shape->area();  // Calls Circle::area()
```

**What happens:**
1. `shape` is a `Shape*` pointing to a `Circle` object
2. `area()` is a **virtual function**
3. Compiler generates **vtable lookup** at runtime
4. `Circle::area()` is called through virtual dispatch

---

## 3. Before/After: Why Use Inheritance?

### 3.1 WITHOUT Inheritance (Code Duplication)

```cpp
// Turbulence model 1
class kEpsilon
{
    volScalarField k_;
    volScalarField epsilon_;
    const volVectorField& U_;
    
public:
    kEpsilon(const volVectorField& U) : U_(U) {}
    
    void correct()
    {
        // Specific k-epsilon equations
        solve(fvm::ddt(k_) + ... == ...);
        solve(fvm::ddt(epsilon_) + ... == ...);
    }
    
    tmp<volSymmTensorField> divDevReff(const volVectorField& U)
    {
        // Compute Reynolds stress
        return ...;
    }
};

// Turbulence model 2
class kOmegaSST
{
    volScalarField k_;
    volScalarField omega_;
    const volVectorField& U_;
    
public:
    kOmegaSST(const volVectorField& U) : U_(U) {}
    
    void correct()
    {
        // Specific k-omega equations
        solve(fvm::ddt(k_) + ... == ...);
        solve(fvm::ddt(omega_) + ... == ...);
    }
    
    tmp<volSymmTensorField> divDevReff(const volVectorField& U)
    {
        // Compute Reynolds stress (DUPLICATED!)
        return ...;
    }
};

// Solver code - MUST be modified for each model!
void solve()
{
    if (modelType == "kEpsilon")
    {
        kEpsilon turb(U);
        turb.correct();
        divDevReff = turb.divDevReff(U);
    }
    else if (modelType == "kOmegaSST")
    {
        kOmegaSST turb(U);
        turb.correct();
        divDevReff = turb.divDevReff(U);  // Repeated!
    }
    // Add more if blocks for new models...
}
```

**Problems:**
- ❌ Duplicated code (`k_`, `U_`, `divDevReff`)
- ❌ Solver code changes for each new model
- ❌ Cannot store different models in same container
- ❌ No common interface for model selection

---

### 3.2 WITH Inheritance (Clean & Extensible)

```cpp
// Abstract base class
class turbulenceModel
{
protected:
    const volVectorField& U_;
    
public:
    turbulenceModel(const volVectorField& U) : U_(U) {}
    virtual ~turbulenceModel() = default;
    
    // Common interface - ALL models MUST implement
    virtual void correct() = 0;
    virtual tmp<volSymmTensorField> divDevReff(const volVectorField& U) = 0;
    
    // Common implementation - SHARED by all models
    scalar nut() const { return nut_; }
    
protected:
    volScalarField nut_;
};

// Derived model 1
class kEpsilon : public turbulenceModel
{
    volScalarField k_;
    volScalarField epsilon_;
    
public:
    kEpsilon(const volVectorField& U) : turbulenceModel(U) {}
    
    virtual void correct() override
    {
        solve(fvm::ddt(k_) + ... == ...);
        solve(fvm::ddt(epsilon_) + ... == ...);
    }
    
    virtual tmp<volSymmTensorField> divDevReff(const volVectorField& U) override
    {
        return ...;
    }
};

// Derived model 2
class kOmegaSST : public turbulenceModel
{
    volScalarField k_;
    volScalarField omega_;
    
public:
    kOmegaSST(const volVectorField& U) : turbulenceModel(U) {}
    
    virtual void correct() override
    {
        solve(fvm::ddt(k_) + ... == ...);
        solve(fvm::ddt(omega_) + ... == ...);
    }
    
    virtual tmp<volSymmTensorField> divDevReff(const volVectorField& U) override
    {
        return ...;
    }
};

// Solver code - UNIFIED for all models!
void solve()
{
    autoPtr<turbulenceModel> turb = turbulenceModel::New(U);
    
    turb->correct();  // Calls appropriate model's correct()
    auto divDevReff = turb->divDevReff(U);
}
```

**Benefits:**
- ✅ Shared members in base class (`U_`, `nut_`)
- ✅ Solver code unchanged for new models
- ✅ Can store any model in `autoPtr<turbulenceModel>`
- ✅ Common interface enforced by compiler

---

## 4. Why in OpenFOAM? Concrete Use Cases

### 4.1 Turbulence Models

| Problem | Inheritance Solution |
|---------|---------------------|
| **Need multiple models** | `turbulenceModel` base + `kEpsilon`, `kOmegaSST` derived |
| **Switch models without recompiling** | Virtual `correct()` + RTS factory |
| **Solver code unchanged** | Base class pointer `autoPtr<turbulenceModel>` |

**Dictionary-driven:**
```cpp
simulationType  RAS;
RAS
{
    RASModel        kEpsilon;  // Change to kOmegaSST, no code change!
    turbulence      on;
}
```

**Code:**
```cpp
// Single line works for ANY model
autoPtr<turbulenceModel> turb = turbulenceModel::New(...);
turb->correct();  // Dispatches to kEpsilon::correct() or kOmegaSST::correct()
```

---

### 4.2 Boundary Conditions

| Problem | Inheritance Solution |
|---------|---------------------|
| **Pluggable BC types** | `fvPatchField` base + many derived types |
| **Add custom BC** | Derive from `fixedValueFvPatchField` |
| **Same evaluation syntax** | Virtual `updateCoeffs()` method |

**Dictionary-driven:**
```
inlet
{
    type            fixedValue;  // Or zeroGradient, mixed, etc.
    value           uniform (0 0 0);
}
```

**Code:**
```cpp
// Single interface for ALL BC types
const fvPatchField<scalar>& patch = field.boundaryField()[patchI];
patch.updateCoeffs();  // Calls correct derived implementation
```

---

### 4.3 Interchangeable Solvers

| Problem | Inheritance Solution |
|---------|---------------------|
| **Multiple discretization schemes** | `fv::divScheme` base + derived schemes |
| **Runtime scheme selection** | Virtual `div()` + RTS from `schemes` dict |
| **Consistent interface** | All schemes implement `fvc::div(Scheme, field)` |

**Dictionary-driven:**
```cpp
divSchemes
{
    div(phi,U)      Gauss linearUpwind grad(U);  // Change scheme here
}
```

**Code:**
```cpp
// Works with ANY div scheme
tmp<GeometricField<scalar, fvsPatchField, surfaceMesh>> divPhiU = 
    fvc::div(turbulence->divScheme("div(phi,U)"), phi, U);
```

---

## 5. Virtual Functions: How They Work

### 5.1 Mechanism

```cpp
turbulenceModel* turb = new kEpsilon(U);
turb->correct();  // Virtual call
```

**Step-by-step:**
1. Compiler creates **vtable** (virtual function table) for each polymorphic class
2. `turb` object contains hidden **vptr** (pointer to vtable)
3. `turb->correct()` performs:
   - Load vptr from object
   - Lookup `correct()` function pointer in vtable
   - Jump to `kEpsilon::correct()`

### 5.2 vtable Structure

```cpp
// turbulenceModel vtable
turbulenceModel::$vtable:
    correct        -> 0 (pure virtual, no implementation)
    divDevReff     -> 0 (pure virtual)
    ~turbulenceModel -> turbulenceModel::~turbulenceModel()

// kEpsilon vtable
kEpsilon::$vtable:
    correct        -> kEpsilon::correct()
    divDevReff     -> kEpsilon::divDevReff()
    ~turbulenceModel -> kEpsilon::~kEpsilon()
```

---

## 6. OpenFOAM Patterns Summary

| Pattern | Purpose | OpenFOAM Example |
|---------|---------|------------------|
| **Abstract base** | Define interface | `turbulenceModel`, `fvPatchField<Type>` |
| **Pure virtual** | Force implementation | `virtual void correct() = 0;` |
| **Virtual override** | Provide specific behavior | `void correct() override;` |
| **Run-Time Selection** | Factory creation | `Model::New(dictionary)` |
| **Template + Inheritance** | Type generality | `GeometricField<Type, PatchField, GeoMesh>` |

---

## Quick Reference

| Concept | Syntax | Purpose |
|---------|--------|---------|
| Pure virtual | `virtual void f() = 0;` | Force derived implementation |
| Override | `virtual void f() override;` | Explicitly override base function |
| Final | `virtual void f() final;` | Prevent further overriding |
| Virtual destructor | `virtual ~Base() {}` | Proper cleanup through base pointer |
| Base access | `Base::method()` | Call base class implementation |
| Factory | `Model::New(dict)` | Runtime object creation |

---

## 🧠 Concept Check

<details>
<summary><b>1. What problem does inheritance solve in OpenFOAM?</b></summary>

**Problem:** Multiple turbulence models need common interface  
**Solution:** `turbulenceModel` base class defines `correct()`, derived models implement specifics  
**Result:** Solver code works with ANY model through base pointer
</details>

<details>
<summary><b>2. How does virtual function dispatch work?</b></summary>

1. Each polymorphic object has hidden **vptr** (pointer to vtable)
2. **vtable** contains function pointers for virtual functions
3. Virtual call: `ptr->method()` → vtable lookup → jump to derived implementation
4. Enables **runtime dispatch** based on actual object type
</details>

<details>
<summary><b>3. What does the override keyword do?</b></summary>

**Compiler check** that the function:
- Actually overrides a base class virtual function
- Has the **exact same signature** as the base function
- Catches errors at **compile time** (misspelled name, wrong parameters)

**Example:**
```cpp
virtual void corrct() override;  // Compile error: no "corrct" in base
virtual void correct() override;  // OK
```
</details>

<details>
<summary><b>4. Why use autoPtr<turbulenceModel> instead of turbulenceModel*?</b></summary>

**`autoPtr`** provides:
- **Automatic memory management** (deletes object when out of scope)
- **Ownership semantics** (clear who owns the object)
- **Exception safety** (cleanup even if error occurs)

**Modern alternative:** `std::unique_ptr<turbulenceModel>`
</details>

---

## Key Takeaways

✓ **Inheritance** establishes "is-a" relationships and enables code reuse through base/derived classes  
✓ **Polymorphism** allows objects of different types to respond to the same interface differently  
✓ **Virtual functions** enable runtime dispatch via vtable lookup when called through base pointers  
✓ **Abstract classes** define interfaces with pure virtual functions that derived classes must implement  
✓ **In OpenFOAM**, polymorphism enables interchangeable turbulence models, boundary conditions, and discretization schemes  
✓ **RTS (Run-Time Selection)** combines virtual functions with factory pattern for dictionary-driven object creation  
✓ **The override keyword** provides compile-time checking that functions correctly override base implementations  

---

## 📖 Related Documents

- **Overview:** [00_Overview.md](00_Overview.md) — Module roadmap and prerequisites
- **Interfaces:** [02_Abstract_Interfaces.md](02_Abstract_Interfaces.md) — Abstract class design in detail
- **Hierarchies:** [03_Inheritance_Hierarchies.md](03_Inheritance_Hierarchies.md) — Designing class hierarchies
- **RTS:** [04_Run_Time_Selection_System.md](04_Run_Time_Selection_System.md) — Factory pattern implementation