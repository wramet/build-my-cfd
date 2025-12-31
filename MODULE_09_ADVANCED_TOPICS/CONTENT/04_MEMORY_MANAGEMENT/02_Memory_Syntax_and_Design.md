# Memory Management - Syntax and Design

Syntax และ Design ของ Memory Management

---

## Learning Objectives

**Learning Objectives | วัตถุประสงค์การเรียนรู้**

- **Understand** the syntax and usage patterns of OpenFOAM's smart pointer types
- **Distinguish** between different smart pointer types and their appropriate use cases
- **Apply** best practices for memory management in OpenFOAM code
- **Avoid** common memory-related pitfalls through anti-pattern recognition

---

## Overview

> **OpenFOAM uses smart pointers for automatic memory management**
>
> OpenFOAM ใช้ smart pointers สำหรับจัดการหน่วยความจำอัตโนมัติ

**Why Smart Pointers? | ทำไมต้องใช้ Smart Pointers?**

OpenFOAM's smart pointer system provides automatic memory management, preventing memory leaks and dangling pointers common in C++ development. Understanding when and how to use each type is critical for writing robust, efficient OpenFOAM code.

---

## 1. autoPtr - Unique Ownership

**What | อะไร**

`autoPtr` manages exclusive ownership of dynamically allocated objects. Only one `autoPtr` can own the object at any time.

**When to Use | เมื่อไหร่ควรใช้**
- Factory methods that create and return new objects
- Local ownership of heap-allocated objects
- Transfer of ownership between scopes
- Polymorphic object creation (using virtual constructors)

**How | อย่างไร**

### Basic Syntax

```cpp
// Creating and initializing
autoPtr<volScalarField> fieldPtr
(
    new volScalarField
    (
        IOobject
        (
            "T",
            runTime.timeName(),
            mesh,
            IOobject::NO_READ,
            IOobject::AUTO_WRITE
        ),
        mesh
    )
);
```

### Accessing the Object

```cpp
// Dereference operator returns reference
volScalarField& field = fieldPtr();

// Arrow operator for member access
scalar value = fieldPtr->average()[0];
```

### Checking Validity

```cpp
// Check if pointer owns an object
if (fieldPtr.valid())
{
    // Safe to use
    Info << "Field size: " << fieldPtr()->size() << endl;
}

// Check if pointer is empty
if (!fieldPtr.empty())
{
    // Pointer owns something
}
```

### Transferring Ownership

```cpp
// Method 1: Move semantics (C++11 and later)
autoPtr<volScalarField> newOwner = std::move(fieldPtr);

// After move, fieldPtr is now empty
if (!fieldPtr.valid())
{
    Info << "Ownership transferred" << endl;
}

// Method 2: Explicit transfer (older style)
autoPtr<volScalarField> anotherOwner = fieldPtr.ptr();
```

### Factory Pattern Example

```cpp
// Base class with virtual constructor
class turbulenceModel
{
public:
    // What: Factory method creating derived types
    // When: Selecting model at runtime based on dictionary
    static autoPtr<turbulenceModel> New
    (
        const volVectorField& U,
        const surfaceScalarField& phi,
        transportModel& transport
    );
};

// Usage - runtime selection
autoPtr<turbulenceModel> turbulence = 
    turbulenceModel::New(U, phi, laminarTransport);

// Ownership transferred to turbulence variable
```

---

## 2. tmp - Reference-Counted Temporaries

**What | อะไร**

`tmp` provides reference-counted smart pointers for temporary objects, enabling efficient expression template evaluation and automatic cleanup.

**When to Use | เมื่อไหร่ควรใช้**
- Returning temporary field calculations from functions
- Chaining field operations without intermediate copies
- Storing references to temporary objects that may be reused
- All `fvc::` and `fvm::` operations

**How | อย่างไร**

### Basic Syntax

```cpp
// Creating from field operations
tmp<volScalarField> tGradP = fvc::grad(p);

// Creating from existing field
tmp<volScalarField> tField = tmp<volScalarField>
(
    new volScalarField(p)
);
```

### Accessing the Object

```cpp
// Const reference (doesn't increment refCount)
const volScalarField& constField = tField();

// Non-const reference (increments refCount)
volScalarField& mutableField = tField.ref();

// Const reference method
const volScalarField& anotherConst = tField.constRef();
```

### Reference Counting Behavior

```cpp
// Initial tmp owns the object (refCount = 1)
tmp<volScalarField> t1 = fvc::grad(p);

// Assignment shares ownership (refCount = 2)
tmp<volScalarField> t2 = t1;

// Both reference the same underlying object
Info << "Same object? " << (&t1() == &t2()) << endl;  // true

// When t2 goes out of scope, refCount decreases to 1
// When t1 goes out of scope, refCount reaches 0, object deleted
```

### Expression Chaining

```cpp
// What: Chain operations without intermediate copies
// Why: tmp enables efficient expression evaluation
tmp<volScalarField> magGradU = mag(fvc::grad(U));

// Each operation returns tmp, sharing ownership temporarily
// Final result computed once, intermediate temporaries auto-cleaned
```

### Const Correctness

```cpp
// What: Const tmp cannot be converted to non-const reference
const tmp<volScalarField> constTmp = fvc::grad(p);

// This works - const access
const volScalarField& field = constTmp();

// This FAILS - cannot get non-const from const tmp
// volScalarField& bad = constTmp.ref();  // Compilation error
```

---

## 3. PtrList - Dynamic Pointer Collections

**What | อะไร**

`PtrList` manages a dynamic list of pointers, taking ownership of each element and providing safe indexed access.

**When to Use | เมื่อไหร่ควรใช้**
- Collections of boundary conditions
- Multiple fields of the same type
- Lists of models or objects
- When collection size is determined at runtime

**How | อย่างไร**

### Basic Syntax

```cpp
// Construct with specified size
PtrList<volScalarField> fields(5);

// Construct from list
PtrList<entry> entries = dict.lookup("models");
```

### Setting Elements

```cpp
// Method 1: Set with index
fields.set(0, new volScalarField(...));
fields.set(1, new volScalarField(...));

// Method 2: Construct and set
forAll(fields, i)
{
    fields.set
    (
        i,
        new volScalarField
        (
            IOobject("field" + Foam::name(i), ...),
            mesh
        )
    );
}
```

### Accessing Elements

```cpp
// Bounds-checked access
volScalarField& field = fields[3];

// Const access
const volScalarField& cField = fields[3];

// Check if element is set
if (fields.set(3))
{
    // Safe to access
    Info << "Field size: " << fields[3].size() << endl;
}
```

### Iteration

```cpp
// Iterate with index
forAll(fields, i)
{
    if (fields.set(i))
    {
        fields[i].write();
    }
}

// Range-based for (C++11)
for (volScalarField& field : fields)
{
    if (&field != nullptr)
    {
        field.write();
    }
}
```

### Ownership Transfer

```cpp
// Transfer from PtrList to autoPtr
autoPtr<volScalarField> extracted = fields.set(3);

// After extraction, slot 3 is now empty
if (!fields.set(3))
{
    Info << "Slot 3 is empty" << endl;
}
```

---

## 4. refPtr - Optional Reference or Pointer

**What | อะไร**

`refPtr` can hold either a reference to an existing object or a pointer to an owned object, providing flexibility in parameter passing.

**When to Use | เมื่อไหร่ควรใช้**
- Function parameters that may accept either references or newly created objects
- Optional object ownership
- Caching computed results
- Conditional object creation

**How | อย่างไร**

```cpp
// Holding a reference
volScalarField existingField(mesh);
refPtr<volScalarField> refHolder(existingField);

// Holding ownership
refPtr<volScalarField> ptrHolder
(
    new volScalarField(IOobject(...), mesh)
);

// Access (works for both cases)
volScalarField& field = refHolder();
```

---

## 5. Anti-Patterns vs Best Practices

### Anti-Pattern 1: Raw Pointer Creation

**❌ Anti-Pattern**

```cpp
// BAD: Who deletes this? Memory leak!
volScalarField* field = new volScalarField(IOobject(...), mesh);

// Using the field
field->write();

// Forgetting to delete - memory leak!
```

**✅ Best Practice**

```cpp
// GOOD: Smart pointer auto-deletes
autoPtr<volScalarField> fieldPtr
(
    new volScalarField(IOobject(...), mesh)
);

// fieldPtr automatically deletes when out of scope
```

---

### Anti-Pattern 2: Dangling Reference to Temporary

**❌ Anti-Pattern**

```cpp
// BAD: Storing reference to temporary that gets destroyed
const volVectorField& gradU = fvc::grad(U)();

// gradU is now dangling! The tmp was destroyed here
// Using gradU later = undefined behavior
solve(gradU & gradU);  // CRASH or wrong results
```

**✅ Best Practice**

```cpp
// GOOD: Store tmp to keep temporary alive
tmp<volVectorField> tGradU = fvc::grad(U);

// Temporary lives as long as tGradU exists
const volVectorField& gradU = tGradU();

// Now safe to use
solve(gradU & gradU);
```

---

### Anti-Pattern 3: Unnecessary Copy

**❌ Anti-Pattern**

```cpp
// BAD: Forces copy of temporary field
volScalarField magU = mag(U)();

// magU is a full copy, expensive for large fields
```

**✅ Best Practice**

```cpp
// GOOD: Use tmp to avoid copy
tmp<volScalarField> tMagU = mag(U);

// No copy made, just reference counting
const volScalarField& magU = tMagU();
```

---

### Anti-Pattern 4: Invalid autoPtr Access

**❌ Anti-Pattern**

```cpp
// BAD: Accessing after move
autoPtr<volScalarField> ptr1(new volScalarField(...));
autoPtr<volScalarField> ptr2 = std::move(ptr1);

// ptr1 is now empty! This will crash
ptr1()->write();  // SEGFAULT
```

**✅ Best Practice**

```cpp
// GOOD: Check validity before access
autoPtr<volScalarField> ptr1(new volScalarField(...));
autoPtr<volScalarField> ptr2 = std::move(ptr1);

if (ptr1.valid())
{
    ptr1()->write();
}
else
{
    Info << "ptr1 is empty" << endl;
}
```

---

### Anti-Pattern 5: PtrList Index Out of Bounds

**❌ Anti-Pattern**

```cpp
// BAD: Accessing unset PtrList element
PtrList<volScalarField> fields(3);

fields.set(0, new volScalarField(...));
fields.set(2, new volScalarField(...));

// Index 1 was never set! This will crash
fields[1].write();  // SEGFAULT
```

**✅ Best Practice**

```cpp
// GOOD: Always check if element is set
PtrList<volScalarField> fields(3);

fields.set(0, new volScalarField(...));
fields.set(2, new volScalarField(...));

forAll(fields, i)
{
    if (fields.set(i))
    {
        fields[i].write();
    }
}
```

---

## 6. Choosing the Right Smart Pointer

### Decision Tree

```
Need a collection of pointers?
├─ Yes → Use PtrList<T>
└─ No
    ├─ Need to share ownership?
    │   ├─ Yes → Use tmp<T> (reference counted)
    │   └─ No
    │       ├─ Might hold reference OR owned object?
    │       │   ├─ Yes → Use refPtr<T>
    │       │   └─ No → Use autoPtr<T> (unique ownership)
```

### Comparison Table

| Smart Pointer | Ownership Model | Reference Counted | Copyable | Typical Use |
|--------------|-----------------|-------------------|----------|-------------|
| `autoPtr<T>` | Unique | ❌ No | ❌ Move only | Factory returns, local ownership |
| `tmp<T>` | Shared | ✅ Yes | ✅ Yes | Field operations, temporaries |
| `refPtr<T>` | Optional | ❌ No | ✅ Yes | Flexible parameters, caching |
| `PtrList<T>` | List of owned | ❌ No | ❌ No | Dynamic collections |

### Selection Guidelines

**When to use `autoPtr<T>` | เมื่อไหร่ใช้ autoPtr**
- Factory methods returning new objects
- Unique ownership required
- Transfer of ownership between scopes
- Polymorphic object creation

**When to use `tmp<T>` | เมื่อไหร่ใช้ tmp**
- All `fvc::` and `fvm::` operations
- Chaining field operations
- Returning temporary calculations
- Avoiding unnecessary copies
- Expression template evaluation

**When to use `refPtr<T>` | เมื่อไหรีใช้ refPtr**
- Function parameters accepting references or new objects
- Optional ownership scenarios
- Caching computed results
- Conditional object creation

**When to use `PtrList<T>` | เมื่อไหร่ใช้ PtrList**
- Runtime-sized collections
- Multiple objects of same type
- Boundary condition collections
- Model lists

---

## Key Takeaways

**Key Takeaways | สรุปสิ่งสำคัญ**

**1. Smart Pointer Selection**
- **`autoPtr`** for unique ownership and factory returns
- **`tmp`** for shared temporaries and field operations
- **`PtrList`** for dynamic collections of owned pointers
- **`refPtr`** for flexible reference/pointer ownership

**2. Common Pitfalls to Avoid**
- Never store references to `tmp` temporaries without keeping the `tmp` alive
- Always check `autoPtr.valid()` and `PtrList.set()` before access
- Avoid raw pointers with `new` - use smart pointers instead
- Remember that `std::move()` leaves the source empty

**3. Memory Management Principles**
- Smart pointers automatically clean up when out of scope
- `tmp` uses reference counting to share ownership efficiently
- `autoPtr` transfers ownership exclusively via move semantics
- `PtrList` owns and manages lifetime of all its elements

**4. OpenFOAM Integration**
- All `fvc::` operations return `tmp<T>` - store if reused later
- Factory methods (`Model::New()`) return `autoPtr<T>`
- Field expressions chain efficiently using `tmp` reference counting
- Boundary conditions typically stored in `PtrList`

---

## 🧠 Concept Check

<details>
<summary><b>1. What's the key difference between autoPtr and tmp?</b></summary>

**What: ความแตกต่างหลักระหว่าง autoPtr และ tmp**

- **`autoPtr`**: Unique ownership, move-only, exclusive access
- **`tmp`**: Shared ownership via reference counting, copyable

Use `autoPtr` when you need single-owner semantics, and `tmp` when you need to share temporary objects (like field operation results).
</details>

<details>
<summary><b>2. Why do fvc:: operations return tmp?</b></summary>

**Why: ทำไม fvc:: operations ถึง return tmp?**

Because they create **temporary field objects** that may be chained in expressions. The `tmp` reference counting allows:
- Efficient expression chaining without copies
- Automatic cleanup when all references are gone
- Optional storage if the result is reused

Example: `mag(fvc::grad(U))` - both `grad()` and `mag()` return `tmp`, sharing ownership temporarily.
</details>

<summary><b>3. What happens if you store a reference to a tmp temporary without keeping the tmp?</b></summary>

**What: อะไรเกิดขึ้นถ้าเก็บ reference ไปยัง tmp โดยไม่ retain tmp?**

You get a **dangling reference**. The temporary object is destroyed when the `tmp` goes out of scope, leaving your reference pointing to invalid memory.

```cpp
// BAD
const volScalarField& field = fvc::grad(p)();  // tmp destroyed here
// field is now dangling!

// GOOD
tmp<volScalarField> tField = fvc::grad(p);  // tmp kept alive
const volScalarField& field = tField();
```
</details>

<details>
<summary><b>4. When should you choose PtrList over List<autoPtr<T>>?</b></summary>

**When: เมื่อไหร่ควรเลือก PtrList แทน List<autoPtr<T>>?

Use **`PtrList<T>`** when:
- You need direct indexed access (`[i]`)
- Collection size is fixed after construction
- You want simpler syntax for pointer management

Use **`List<autoPtr<T>>`** when:
- You need `List` operations (resize, append, etc.)
- Elements may be added/removed dynamically
- You need standard container interface

For most OpenFOAM collections, `PtrList<T>` is preferred.
</details>

<details>
<summary><b>5. tmp ช่วยอะไรใน OpenFOAM?</b></summary>

**What: tmp ช่วยอะไรใน OpenFOAM?**

`tmp` provides:
- **Automatic cleanup** ของ temporary fields
- **Reference counting** สำหรับ sharing ownership
- **Expression chaining** โดยไม่ต้อง copy data
- **Memory efficiency** ใน field operations

ทำให้เขียน expression ได้สะอาดเช่น `solve(fvc::ddt(phi) + fvc::div(phi, U))` โดยไม่มี memory leak
</details>

---

## 📖 Related Documentation

### Prerequisites | แหล่งอ้างอิงก่อนหน้า
- **Overview:** [00_Overview.md](00_Overview.md)
- **Introduction:** [01_Introduction.md](01_Introduction.md)

### Current Module | โมดูลปัจจุบัน
- **Internal Mechanics:** [03_Internal_Mechanics.md](03_Internal_Mechanics.md) - ศึกษากลไกภายในของ reference counting และ memory management
- **Performance Considerations:** [07_Performance_Considerations.md](07_Performance_Considerations.md) - ผลกระทบของ smart pointers ต่อ performance

### Related Topics | หัวข้อที่เกี่ยวข้อง
- **Design Patterns:** [03_Design_Patterns](../03_DESIGN_PATTERNS/00_Overview.md) - Factory pattern ใช้ autoPtr
- **Turbulence Modeling:** Uses `autoPtr` for runtime selection
- **Boundary Conditions:** Uses `PtrList` for patch field management