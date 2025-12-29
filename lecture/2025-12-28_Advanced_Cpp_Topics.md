# บันทึกบทเรียน: Advanced C++ Topics — เข้าสู่ลึกแห่ง OpenFOAM Source Code

**วันที่:** 28 ธันวาคม 2025

> **สิ่งที่จะได้เรียนรู้:**
> 1. Template Programming
> 2. Inheritance & Polymorphism
> 3. Design Patterns (Factory, Strategy, Observer)
> 4. Memory Management (Smart Pointers)

---

## 1. ทำไมต้องเข้าใจ Advanced C++?

> **"To modify OpenFOAM, you must understand how it's built"**

### 1.1 OpenFOAM C++ Complexity

```
User Level:
    Run cases, modify dictionaries
    → ไม่ต้องรู้ C++

Intermediate Level:
    Write custom utilities, function objects
    → รู้ C++ พื้นฐาน

Advanced Level:
    Modify solvers, create new models
    → ต้องรู้ Templates, Polymorphism, Design Patterns
```

### 1.2 Core C++ Concepts in OpenFOAM

| Concept | Where Used |
|---------|------------|
| **Templates** | GeometricField, List, Field |
| **Inheritance** | Turbulence models, BCs |
| **Virtual Functions** | Polymorphic behavior |
| **Smart Pointers** | Memory management (autoPtr, tmp) |
| **Design Patterns** | Factory, Strategy, Observer |

---

## 2. Template Programming

> **Templates = Generic Programming**
> Write code once, use for any type

### 2.1 Why Templates?

| Benefit | Description |
|---------|-------------|
| **Code Reuse** | Same logic for different types |
| **Type Safety** | Compile-time type checking |
| **Zero Overhead** | No runtime cost |
| **Specialization** | Custom behavior per type |

### 2.2 Basic Syntax

**Function Template:**
```cpp
template<class Type>
Type maximum(const Type& a, const Type& b)
{
    return (a > b) ? a : b;
}

// Usage
scalar s = maximum<scalar>(3.14, 2.71);
vector v = maximum<vector>(v1, v2);
```

**Class Template:**
```cpp
template<class Type>
class Container
{
    Type value_;
public:
    Container(const Type& val) : value_(val) {}
    const Type& value() const { return value_; }
};

// Usage
Container<scalar> cs(3.14);
Container<vector> cv(vector(1, 0, 0));
```

### 2.3 OpenFOAM Template Examples

**GeometricField:**
```cpp
template<class Type, template<class> class PatchField, class GeoMesh>
class GeometricField
{
    // Internal field: Field<Type>
    // Boundary: GeometricBoundaryField<Type, PatchField, GeoMesh>
};

// Type aliases (คุ้นเคยไหม?)
typedef GeometricField<scalar, fvPatchField, volMesh> volScalarField;
typedef GeometricField<vector, fvPatchField, volMesh> volVectorField;
typedef GeometricField<tensor, fvPatchField, volMesh> volTensorField;
typedef GeometricField<scalar, fvsPatchField, surfaceMesh> surfaceScalarField;
```

**Field:**
```cpp
template<class Type>
class Field : public List<Type>
{
public:
    // Field operations
    Type sum() const;
    Type average() const;
    // ...
};

// Usage
Field<scalar> sf(100, 0.0);
Field<vector> vf(100, vector::zero);
```

**fvc:: Operations:**
```cpp
template<class Type>
tmp<GeometricField<Type, fvPatchField, volMesh>>
fvc::grad(const GeometricField<Type, fvPatchField, volMesh>& f);

// Works for any Type!
tmp<volVectorField> gradP = fvc::grad(p);      // scalar → vector
tmp<volTensorField> gradU = fvc::grad(U);      // vector → tensor
```

### 2.4 Template Instantiation

**Explicit Instantiation:**
```cpp
// In .C file
template class GeometricField<scalar, fvPatchField, volMesh>;
template class GeometricField<vector, fvPatchField, volMesh>;
```

**Why needed?**
- Templates are compiled when used
- Header-only can cause bloat
- Explicit instantiation controls compilation

### 2.5 Template Specialization

```cpp
// General template
template<class Type>
Type mag(const Type& x) { return Foam::sqrt(x & x); }

// Specialization for scalar
template<>
scalar mag<scalar>(const scalar& x) { return Foam::mag(x); }
```

---

## 3. Inheritance & Polymorphism

> **Inheritance = "is-a" relationship**
> **Polymorphism = Same interface, different behavior**

### 3.1 Class Hierarchies in OpenFOAM

**Turbulence Models:**
```
turbulenceModel (abstract base)
├── RASModel
│   ├── kEpsilon
│   ├── kOmegaSST
│   ├── realizableKE
│   └── ...
└── LESModel
    ├── Smagorinsky
    ├── WALE
    ├── kEqn
    └── ...
```

**Boundary Conditions:**
```
fvPatchField<Type> (abstract base)
├── fixedValueFvPatchField
├── zeroGradientFvPatchField
├── mixedFvPatchField
├── inletOutletFvPatchField
└── ...
```

### 3.2 Virtual Functions

```cpp
// Base class (abstract)
class turbulenceModel
{
public:
    // Pure virtual = must be implemented
    virtual void correct() = 0;
    
    // Virtual = can be overridden
    virtual tmp<volScalarField> k() const;
    virtual tmp<volScalarField> epsilon() const;
    
    // Virtual destructor (important!)
    virtual ~turbulenceModel() = default;
};

// Derived class
class kEpsilon : public turbulenceModel
{
public:
    virtual void correct() override;
    virtual tmp<volScalarField> k() const override;
    virtual tmp<volScalarField> epsilon() const override;
};
```

### 3.3 Polymorphic Usage

```cpp
// User code works with base class pointer
autoPtr<turbulenceModel> turb = turbulenceModel::New(dict);

// Calls correct() on actual type (kEpsilon, kOmegaSST, etc.)
turb->correct();  // Runtime dispatch!

// Works for any turbulence model
volScalarField k = turb->k();
volScalarField eps = turb->epsilon();
```

### 3.4 Abstract Classes

```cpp
// Pure virtual = 0 means "must be implemented"
class fvPatchField
{
public:
    virtual void updateCoeffs() = 0;
    virtual void evaluate() = 0;
    
    // Cannot instantiate this class directly!
};

// Derived class must implement
class fixedValueFvPatchField : public fvPatchField
{
public:
    virtual void updateCoeffs() override
    {
        // Implementation
    }
    
    virtual void evaluate() override
    {
        // Implementation
    }
};
```

---

## 4. Run-Time Selection (RTS)

> **OpenFOAM's Factory Pattern Implementation**
> Create objects from dictionary at runtime

### 4.1 How RTS Works

```cpp
// In dictionary
turbulenceProperties
{
    simulationType RAS;
    RAS
    {
        RASModel    kEpsilon;  // ← String name!
    }
}

// In code
autoPtr<turbulenceModel> turb = turbulenceModel::New(dict);
// → Creates kEpsilon object from string "kEpsilon"
```

### 4.2 RTS Macros

```cpp
// In kEpsilon.H
class kEpsilon : public RASModel
{
    // ...
public:
    TypeName("kEpsilon");  // Declares type name
    
    // ... constructors, methods
};

// In kEpsilon.C
defineTypeNameAndDebug(kEpsilon, 0);

addToRunTimeSelectionTable
(
    turbulenceModel,    // Base class
    kEpsilon,           // This class
    dictionary          // Construction method
);
```

### 4.3 How to Add Your Own Model

```cpp
// 1. Inherit from base class
class myModel : public RASModel
{
public:
    TypeName("myModel");
    
    myModel(const dictionary& dict);
    
    virtual void correct() override;
    // ...
};

// 2. Add to selection table
defineTypeNameAndDebug(myModel, 0);
addToRunTimeSelectionTable(turbulenceModel, myModel, dictionary);

// 3. Use in dictionary
RASModel    myModel;  // Just change the name!
```

---

## 5. Design Patterns

> **Proven solutions to common problems**

### 5.1 Factory Pattern

**Purpose:** Decouple object creation from usage

```cpp
// User code doesn't know concrete type
autoPtr<turbulenceModel> turb = turbulenceModel::New(dict);

// Factory method in base class
static autoPtr<turbulenceModel> New
(
    const dictionary& dict
)
{
    word modelType = dict.lookup("turbulenceModel");
    
    // Lookup in table, create instance
    return autoPtr<turbulenceModel>
    (
        constructorTable[modelType](dict)
    );
}
```

**Benefit:** Add new models without modifying existing code!

### 5.2 Strategy Pattern

**Purpose:** Interchangeable algorithms

```cpp
// fvSchemes
divSchemes
{
    div(phi,U)   Gauss linear;      // Strategy 1
    // div(phi,U)   Gauss upwind;   // Strategy 2
    // div(phi,U)   Gauss QUICK;    // Strategy 3
}

// Same interface, different algorithm
fvc::div(phi, U);  // Uses selected scheme
```

**OpenFOAM Implementation:**
```cpp
// Interpolation scheme is a strategy
tmp<surfaceInterpolationScheme<Type>> scheme =
    surfaceInterpolationScheme<Type>::New(mesh, dict);

// Use polymorphically
surfaceScalarField phiU = scheme().interpolate(U);
```

### 5.3 Observer Pattern (Function Objects)

**Purpose:** Notify observers when state changes

```cpp
// controlDict
functions
{
    fieldAverage
    {
        type            fieldAverage;
        fields          (U p);
        writeControl    writeTime;
    }
    
    probes
    {
        type            probes;
        probeLocations  ((0.5 0.5 0.5));
        fields          (U p);
    }
}

// Observers automatically called at each time step!
```

**Implementation:**
```cpp
// Each time step
runTime.functionObjects().execute();

// Calls all registered function objects
// fieldAverage, probes, etc. are "observers"
```

### 5.4 Template Method Pattern

**Purpose:** Define algorithm skeleton, let subclasses fill in details

```cpp
class solver
{
public:
    void run()
    {
        // Template method
        preSolve();         // Hook for subclass
        
        while (loop())
        {
            solve();        // Must implement
            postProcess();  // Hook for subclass
        }
        
        finalize();         // Hook for subclass
    }
    
protected:
    virtual void preSolve() {}      // Default empty
    virtual void solve() = 0;        // Pure virtual
    virtual void postProcess() {}    // Default empty
    virtual void finalize() {}       // Default empty
};
```

### 5.5 Singleton Pattern

**Purpose:** Single global instance

```cpp
// Time is effectively a singleton
Time& runTime = Time::New();

// objectRegistry is a singleton per mesh
const objectRegistry& db = mesh.thisDb();
```

---

## 6. Memory Management

> **Smart Pointers = Automatic Memory Management**

### 6.1 The Problem

```cpp
// Raw pointer - manual management
Model* ptr = new Model();
// ... use ptr ...
delete ptr;  // Must remember!

// What if exception? Memory leak!
// What if multiple owners? Double delete!
```

### 6.2 OpenFOAM Smart Pointers

| Type | Ownership | Use Case |
|------|-----------|----------|
| **autoPtr<T>** | Unique (move) | Factory returns |
| **tmp<T>** | Shared (ref count) | Temporaries |
| **PtrList<T>** | List of pointers | Collections |
| **refPtr<T>** | Optional | Ref or pointer |

### 6.3 autoPtr — Unique Ownership

```cpp
// Factory returns autoPtr
autoPtr<turbulenceModel> turb = turbulenceModel::New(dict);

// Access with () or ->
turb->correct();
scalar k = turb().k()[0];

// Move ownership
autoPtr<turbulenceModel> turb2 = std::move(turb);
// turb is now empty!

// Auto-cleanup when out of scope
// No manual delete needed!
```

**Key Properties:**
- Unique ownership (only one owner)
- Move-only (no copy)
- Auto-delete when destroyed

### 6.4 tmp — Reference Counting

```cpp
// fvc:: returns tmp
tmp<volVectorField> tGradP = fvc::grad(p);

// Use the temporary
volVectorField& gradP = tGradP();
U -= gradP * dt;

// Multiple references OK
tmp<volVectorField> tRef = tGradP;  // Ref count = 2

// Auto-cleanup when all references destroyed
// When tGradP and tRef go out of scope → delete
```

**Why tmp for temporaries?**
```cpp
// Without tmp (inefficient)
volVectorField gradP = fvc::grad(p);  // Copy!
volScalarField divU = fvc::div(U);    // Copy!
volScalarField result = divU + mag(gradP);  // More copies!

// With tmp (efficient)
volScalarField result = fvc::div(U) + mag(fvc::grad(p));
// tmp objects auto-cleaned after expression
```

### 6.5 PtrList — List of Pointers

```cpp
// Create list
PtrList<volScalarField> species(nSpecies);

// Set elements
forAll(species, i)
{
    species.set
    (
        i,
        new volScalarField
        (
            IOobject("Y" + names[i], ...),
            mesh
        )
    );
}

// Use
species[0] = 1.0;

// Auto-cleanup all when PtrList destroyed
```

### 6.6 Memory Best Practices

```cpp
// ✅ Good: Use smart pointers
autoPtr<Model> model = Model::New(dict);
tmp<volScalarField> tField = fvc::div(phi);

// ❌ Bad: Raw pointers
Model* model = new Model(dict);  // Must delete!
volScalarField* field = new volScalarField(...);  // Leak risk!

// ✅ Good: Return tmp from functions
tmp<volScalarField> myFunction()
{
    return tmp<volScalarField>::New(...);
}

// ❌ Bad: Return raw pointer
volScalarField* myFunction()
{
    return new volScalarField(...);  // Who deletes?
}
```

---

## 7. Quick Reference

### 7.1 Template Syntax

| Syntax | Meaning |
|--------|---------|
| `template<class T>` | Type parameter |
| `T::value_type` | Dependent type |
| `template<>` | Specialization |
| `typedef ... Alias` | Type alias |

### 7.2 Inheritance Syntax

| Syntax | Meaning |
|--------|---------|
| `virtual void f() = 0` | Pure virtual |
| `void f() override` | Override base |
| `virtual ~Base()` | Virtual destructor |

### 7.3 Design Patterns

| Pattern | OpenFOAM Example |
|---------|------------------|
| Factory | `Model::New(dict)` |
| Strategy | fvSchemes selection |
| Observer | functionObjects |
| Singleton | Time, registries |

### 7.4 Smart Pointers

| Type | Use |
|------|-----|
| `autoPtr<T>` | Factory returns |
| `tmp<T>` | Temporaries |
| `PtrList<T>` | Pointer collections |

---

## 8. 🧠 Advanced Concept Check

### Level 1: Fundamentals

<details>
<summary><b>Q1: Template vs Inheritance ต่างกันอย่างไร?</b></summary>

**คำตอบ:**

| Aspect | Template | Inheritance |
|--------|----------|-------------|
| **When** | Compile-time | Run-time |
| **Type** | Known at compile | May be unknown |
| **Overhead** | Zero | Virtual call overhead |
| **Flexibility** | Type must exist | Late binding |

**Template (Static Polymorphism):**
```cpp
template<class T>
void process(T& obj) { obj.compute(); }
// T must have compute() at compile time
```

**Inheritance (Dynamic Polymorphism):**
```cpp
void process(Base* obj) { obj->compute(); }
// Actual type determined at runtime via virtual
```

</details>

<details>
<summary><b>Q2: ทำไม OpenFOAM ใช้ทั้ง Template และ Inheritance?</b></summary>

**คำตอบ:**

**Templates for Type Genericity:**
```cpp
// Same Field class for any data type
Field<scalar>, Field<vector>, Field<tensor>

// Type known at compile time
// Zero runtime overhead
```

**Inheritance for Model Selection:**
```cpp
// Model not known until runtime (from dictionary)
turbulenceModel::New(dict)  
// kEpsilon? kOmegaSST? User decides!
```

**Combined:**
```cpp
// fvPatchField<Type> 
// Template: works for scalar, vector, etc.
// Inheritance: fixedValue, zeroGradient, etc.
fvPatchField<scalar>  ← fixedValueFvPatchField<scalar>
                      ← zeroGradientFvPatchField<scalar>
```

</details>

<details>
<summary><b>Q3: autoPtr vs tmp ต่างกันอย่างไร?</b></summary>

**คำตอบ:**

| Aspect | autoPtr | tmp |
|--------|---------|-----|
| **Ownership** | Unique | Shared |
| **Copy** | Move only | Reference count |
| **Use case** | Factory return | Temporaries |
| **Multiple refs** | No | Yes |

**autoPtr:**
```cpp
autoPtr<Model> a = Model::New(dict);
autoPtr<Model> b = std::move(a);  // a is now empty
// Only b owns the object
```

**tmp:**
```cpp
tmp<Field> t1 = fvc::grad(p);
tmp<Field> t2 = t1;  // Both reference same
// Deleted when both t1 and t2 destroyed
```

</details>

### Level 2: Implementation

<details>
<summary><b>Q4: RTS Macros ทำงานอย่างไร?</b></summary>

**คำตอบ:**

**TypeName("kEpsilon"):**
```cpp
// Generates:
static const char* typeName_() { return "kEpsilon"; }
virtual const word& type() const { return typeName(); }
```

**addToRunTimeSelectionTable:**
```cpp
// Registers constructor in static table:
// constructorTable["kEpsilon"] = &kEpsilon::New;
```

**turbulenceModel::New(dict):**
```cpp
word modelType = dict.lookup("RASModel");
// modelType = "kEpsilon"

return constructorTable[modelType](dict);
// Calls kEpsilon::New(dict)
```

**Magic:** String → Object creation!

</details>

<details>
<summary><b>Q5: ทำไม tmp ช่วยเรื่อง performance?</b></summary>

**คำตอบ:**

**Without tmp:**
```cpp
volVectorField gradP = fvc::grad(p);     // Allocate + Copy
volScalarField divU = fvc::div(U);       // Allocate + Copy
volScalarField result = divU + gradP;    // Allocate + Copy

// 3 allocations, copies everywhere!
```

**With tmp:**
```cpp
volScalarField result = fvc::div(U) + mag(fvc::grad(p));

// tmp<volVectorField> from grad → used → destroyed
// tmp<volScalarField> from div → used → destroyed
// Only result is allocated
```

**Additional Optimization:**
```cpp
// tmp can steal memory instead of copy
tmp<T> operator+(const tmp<T>& a, const tmp<T>& b)
{
    // If a is last use, reuse its memory!
    if (a.movable()) return tmp<T>(a.ptr()->operator+=(b()));
}
```

</details>

<details>
<summary><b>Q6: Virtual Destructor ทำไมต้องมี?</b></summary>

**คำตอบ:**

**Without virtual destructor:**
```cpp
class Base { ~Base() { cout << "Base"; } };
class Derived : public Base { ~Derived() { cout << "Derived"; } };

Base* ptr = new Derived();
delete ptr;  // Only prints "Base"!
             // Derived destructor NOT called → leak!
```

**With virtual destructor:**
```cpp
class Base { virtual ~Base() { cout << "Base"; } };
class Derived : public Base { ~Derived() { cout << "Derived"; } };

Base* ptr = new Derived();
delete ptr;  // Prints "Derived" then "Base" ✅
```

**Rule:** If class has virtual functions → always virtual destructor!

</details>

### Level 3: Advanced

<details>
<summary><b>Q7: CRTP (Curiously Recurring Template Pattern) คืออะไร?</b></summary>

**คำตอบ:**

**Pattern:**
```cpp
template<class Derived>
class Base
{
    void interface()
    {
        static_cast<Derived*>(this)->implementation();
    }
};

class Concrete : public Base<Concrete>
{
    void implementation() { /* ... */ }
};
```

**OpenFOAM Use:**
```cpp
template<class CloudType>
class KinematicCloud : public CloudType
{
    // CloudType is templated base
    // Derived injects behavior at compile time
};
```

**Benefits:**
- Static polymorphism (no virtual overhead)
- Access derived in base at compile time

</details>

<details>
<summary><b>Q8: Expression Templates ใน OpenFOAM ทำงานอย่างไร?</b></summary>

**คำตอบ:**

**Problem:**
```cpp
Field a, b, c, d;
Field result = a + b + c + d;

// Without optimization:
// tmp1 = a + b;      // Allocate
// tmp2 = tmp1 + c;   // Allocate
// tmp3 = tmp2 + d;   // Allocate
// result = tmp3;     // Copy
```

**Expression Templates:**
```cpp
// Build expression tree at compile time
// Evaluate once in single loop

result[i] = a[i] + b[i] + c[i] + d[i];  // One loop!
```

**OpenFOAM Partial Implementation:**
```cpp
// tmp reuse mechanism
template<class Type>
tmp<Field<Type>> operator+
(
    const tmp<Field<Type>>& t1,
    const Field<Type>& f2
)
{
    if (t1.movable())
    {
        t1.ref() += f2;  // Reuse memory!
        return t1;
    }
    // ...
}
```

</details>

<details>
<summary><b>Q9: สร้าง Custom Turbulence Model อย่างไร?</b></summary>

**คำตอบ:**

**Step 1: Create files**
```
myTurbulenceModels/
├── myKEpsilon/
│   ├── myKEpsilon.H
│   └── myKEpsilon.C
└── Make/
    ├── files
    └── options
```

**Step 2: Implement (myKEpsilon.H)**
```cpp
#include "RASModel.H"

class myKEpsilon : public RASModel
{
    // Additional fields
    volScalarField k_;
    volScalarField epsilon_;
    
public:
    TypeName("myKEpsilon");
    
    myKEpsilon
    (
        const alphaField& alpha,
        const rhoField& rho,
        const volVectorField& U,
        // ...
    );
    
    virtual void correct() override;
};
```

**Step 3: Register (myKEpsilon.C)**
```cpp
#include "myKEpsilon.H"
#include "addToRunTimeSelectionTable.H"

defineTypeNameAndDebug(myKEpsilon, 0);
addToRunTimeSelectionTable
(
    turbulenceModel,
    myKEpsilon,
    dictionary
);

// Implementations...
```

**Step 4: Use in case**
```cpp
// turbulenceProperties
RAS
{
    RASModel    myKEpsilon;
}
```

</details>

---

## 9. ⚡ Hands-on Challenges

### Challenge 1: Template Function (⭐⭐)

**สร้าง template function ที่หา average ของ Field:**

```cpp
template<class Type>
Type fieldAverage(const Field<Type>& f)
{
    // Implement
}

// Test
Field<scalar> sf(100, 2.0);
Field<vector> vf(100, vector(1, 2, 3));

Info << fieldAverage(sf) << endl;      // Should print 2.0
Info << fieldAverage(vf) << endl;      // Should print (1 2 3)
```

---

### Challenge 2: Simple Model with RTS (⭐⭐⭐⭐)

**สร้าง simple model ที่ใช้ RTS:**

1. Base class: `myModel`
2. Derived: `modelA`, `modelB`
3. Select from dictionary
4. Test polymorphic behavior

---

### Challenge 3: Analyze OpenFOAM Source (⭐⭐⭐⭐⭐)

**วัตถุประสงค์:** เข้าใจ source code จริง

**Tasks:**
1. หา `kEpsilon.H` ใน src/TurbulenceModels/
2. ระบุ: base class, virtual functions, RTS macros
3. หา `correct()` implementation
4. อธิบาย turbulent viscosity calculation

---

## 10. ❌ Common Mistakes

### Mistake 1: Forget Virtual Destructor

```cpp
// ❌ Missing virtual destructor
class Base { ~Base(); };
// Memory leak when delete via base pointer!

// ✅ Virtual destructor
class Base { virtual ~Base() = default; };
```

---

### Mistake 2: Raw Pointer Memory Leak

```cpp
// ❌ Raw pointer
volScalarField* field = new volScalarField(...);
// Must remember to delete!

// ✅ Smart pointer
tmp<volScalarField> tField(...);
// Auto-cleanup!
```

---

### Mistake 3: Missing RTS Macros

```cpp
// ❌ Forgot registration
class myModel : public base
{
    // No TypeName, no addToRunTimeSelectionTable
};
// Error: "Unknown model type myModel"

// ✅ Complete registration
TypeName("myModel");
// + addToRunTimeSelectionTable in .C
```

---

### Mistake 4: Template Linker Errors

```cpp
// ❌ Template implementation in .C file
// File: MyClass.H
template<class T> class MyClass { void method(); };

// File: MyClass.C
template<class T> void MyClass<T>::method() { ... }
// Linker error: undefined reference!

// ✅ Implementation in header (or explicit instantiation)
// File: MyClass.H
template<class T> class MyClass { void method() { ... } };
```

---

## 11. 🔗 เชื่อมโยงกับ Repository

| หัวข้อ | ไฟล์ใน Repository |
|--------|-------------------|
| **Template Programming** | `MODULE_09/01_TEMPLATE_PROGRAMMING/` |
| **Inheritance** | `MODULE_09/02_INHERITANCE_POLYMORPHISM/` |
| **Design Patterns** | `MODULE_09/03_DESIGN_PATTERNS/` |
| **Memory Management** | `MODULE_09/04_MEMORY_MANAGEMENT/` |

---

## 12. สรุป: Advanced C++ Principles

### หลักการ 5 ข้อ

1. **Templates for Type Genericity**
   - Same code for different types
   - Compile-time, zero overhead

2. **Inheritance for Model Selection**
   - Runtime polymorphism
   - User selects via dictionary

3. **RTS = OpenFOAM's Factory**
   - String → Object creation
   - Extensible without modifying core

4. **Smart Pointers Always**
   - autoPtr for ownership
   - tmp for temporaries

5. **Learn by Reading Source**
   - Best documentation is the code
   - Find patterns, understand why

---

*"Understanding C++ design is the key to mastering OpenFOAM development"*
