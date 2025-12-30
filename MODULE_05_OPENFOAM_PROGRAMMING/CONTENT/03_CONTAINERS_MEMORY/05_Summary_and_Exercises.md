# Containers & Memory - Summary and Exercises

> **"Theory guides, practice decides" - OpenFOAM Wisdom**
> 
> Understanding containers and memory management in theory is essential, but **practical application** is where true mastery develops.

---

## Learning Objectives

By completing this chapter and exercises, you will be able to:

- **Apply** the 3W Framework (What-Why-How) to container and memory management decisions
- **Choose** appropriate container types (`List`, `DynamicList`, `HashTable`, `PtrList`, `Field`) for specific CFD scenarios
- **Implement** proper memory management using `autoPtr` and `tmp` to avoid leaks and dangling pointers
- **Write** efficient, memory-safe OpenFOAM code following best practices
- **Debug** common memory-related issues in OpenFOAM applications

---

## Module Summary

### What We Covered

**WHAT:** This module explored OpenFOAM's container systems and memory management mechanisms, including smart pointers (`autoPtr`, `tmp`) and specialized container types (`List`, `DynamicList`, `HashTable`, `PtrList`, `Field`).

**WHY:** 
- Prevent memory leaks and dangling pointers through RAII-based design
- Provide type-safe, efficient data structures optimized for CFD operations
- Enable automatic memory management without garbage collection overhead
- Support polymorphic collections and mathematical field operations

**HOW:** Through understanding container selection criteria, implementing smart pointer patterns, and applying best practices for memory-safe code.

| Topic | What (Definition) | Why (Benefits) | How (Implementation) |
|-------|-------------------|----------------|---------------------|
| **Memory Management** | RAII-based smart pointers for automatic cleanup | Prevent memory leaks, dangling pointer exceptions | `autoPtr<T>` for unique ownership, `tmp<T>` for shared temporaries |
| **Container System** | Specialized data structures optimized for CFD | Efficient operations, type safety, performance | `List<T>`, `DynamicList<T>`, `HashTable<T,Key>`, `PtrList<T>`, `Field<T>` |
| **Best Practices** | Usage patterns and common pitfalls | Write maintainable, bug-free code | Follow 3W framework for all design decisions |

### Key Relationships

```
Memory Management Foundation (RAII)
         ↓
    Container Types (List, HashTable, PtrList, Field)
         ↓
  Integration Patterns (smart pointers with containers)
         ↓
   Real-World Usage (CFD applications, boundary conditions)
```

---

## Knowledge Quick Reference

### Container Selection Guide

| Scenario | Recommended Container | Rationale | When to Use |
|----------|---------------------|-----------|-------------|
| **Fixed-size numerical array** | `List<T>` | Compile-time size, zero overhead | Size known at creation, no growth needed |
| **Unknown/growing size** | `DynamicList<T>` | Automatic growth, efficient appends | Building collections incrementally |
| **Key-value lookups** | `HashTable<T, Key>` | O(1) lookup, string keys common | Property dictionaries, named data |
| **Polymorphic objects** | `PtrList<T>` | Base class pointers, virtual dispatch | Boundary conditions, patch fields |
| **CFD field data** | `Field<T>` | Mathematical operators built-in | Mesh fields, cell/face data |
| **Mesh boundary data** | `FieldField<T, T>` | List of fields (one per patch) | Boundary field collections |

### Memory Management Comparison

| Aspect | `autoPtr<T>` | `tmp<T>` |
|--------|-------------|----------|
| **What** | Unique ownership smart pointer | Reference-counted smart pointer |
| **Why** | Exclusive ownership transfer | Efficient sharing of temporaries |
| **Ownership** | Unique (exclusive) | Shared (reference counted) |
| **Copyability** | Move-only | Copyable (increments ref count) |
| **Use Case** | Factory functions, ownership transfer | Temporary fields, fvc:: operations |
| **Cost** | Negligible | Atomic operations for ref counting |
| **Reset** | `.reset(new T)` | `.clear()` |
| **Transfer** | `std::move(ptr)` | Assignment copies |
| **Common Pattern** | Class members, factory returns | fvc:: operations, expression templates |

### Common Operations Quick Reference

#### List Operations
```cpp
// Creation
List<scalar> data(100, 0.0);           // 100 elements, all zero
List<label> indices(10);                // Uninitialized

// Access
scalar first = data.first();            // data[0]
scalar last = data.last();              // data[size-1]
label n = data.size();                  // Number of elements

// Modification
data = 2.0 * data + 1.0;                // Element-wise operations
```

#### DynamicList Operations
```cpp
// Creation
DynamicList<label> indices;             // Empty
DynamicList<scalar> values(100);        // Pre-allocated capacity

// Growth
indices.append(5);                      // Add single element
values.transfer(list);                  // Transfer from List (efficient)

// Finalization
List<label> result = indices;           // Convert to List (frees extra capacity)
```

#### HashTable Operations
```cpp
// Creation
HashTable<scalar, word> properties;     // Empty
properties.insert("rho", 1000.0);       // Insert

// Lookup
scalar rho = properties["rho"];         // Direct access (may fatal error if missing)
if (properties.found("mu"))             // Safe check
{
    scalar mu = properties["mu"];
}

// Iteration
forAllConstIter(HashTable<scalar, word>, properties, iter)
{
    Info << iter.key() << ": " << iter.object() << endl;
}
```

---

## Exercises

### Exercise 1: Basic List Operations

**WHAT:** Practice creating, populating, and accessing `List` containers for numerical data.

**WHY:** `List<T>` is the most common container in OpenFOAM for fixed-size arrays. Understanding its operations is fundamental.

**HOW:** Create a list, populate it with values, and access elements.

```cpp
List<scalar> values(100, 0.0);

forAll(values, i)
{
    values[i] = sqr(i);  // i²
}

// Access boundary elements
scalar first = values.first();
scalar last = values.last();
label n = values.size();
```

<details>
<summary><b>📊 Expected Output & Questions</b></summary>

**Expected values:**
- `first = 0.0` (i=0: 0²)
- `last = 9801.0` (i=99: 99²)
- `n = 100`

**Questions:**
1. What happens if you access `values[100]`?
2. How would you calculate the sum of all elements?

**Solution (sum):**
```cpp
scalar sum = 0.0;
forAll(values, i)
{
    sum += values[i];
}
// Alternative using OpenFOAM operations:
scalar sum = sum(values);
```
</details>

---

### Exercise 2: DynamicList Growth

**WHAT:** Use `DynamicList` to collect cells meeting a condition without knowing final size in advance.

**WHY:** Many CFD operations require collecting data dynamically (e.g., finding cells above a threshold). `DynamicList` provides efficient growth.

**HOW:** Append elements as needed, then convert to `List` for final use.

```cpp
DynamicList<label> indices;

forAll(mesh.cells(), cellI)
{
    if (cellVolume[cellI] > threshold)
    {
        indices.append(cellI);
    }
}

// Convert to fixed List for final use
List<label> result = indices;
```

<details>
<summary><b>📊 Expected Output & Extensions</b></summary>

**Questions:**
1. What is the time complexity of `append()`?
2. What does the `List` assignment do to the `DynamicList`'s capacity?
3. How would you pre-allocate to minimize reallocations?

**Solution (pre-allocation):**
```cpp
// Estimate final size (if possible)
DynamicList<label> indices(mesh.nCells() / 10);

// Or after initial fill, shrink to fit:
indices.shrink();
List<label> result = indices;
```

**Key Insight:** `DynamicList` grows geometrically (typically 2x), so amortized O(1) append.
</details>

---

### Exercise 3: HashTable Lookups

**WHAT:** Practice safe `HashTable` usage for property storage and retrieval.

**WHY:** `HashTable` is essential for dictionary-like operations (property dictionaries, named parameters). Safe access patterns prevent crashes.

**HOW:** Use `found()` for optional keys, direct access for required keys.

```cpp
HashTable<scalar, word> properties;

properties.insert("density", 1000.0);
properties.insert("viscosity", 1e-6);

// Unsafe direct access (fatal error if missing)
scalar rho = properties["density"];

// Safe access pattern
if (properties.found("temperature"))
{
    scalar T = properties["temperature"];
}
else
{
    Warning << "Temperature not defined, using default" << endl;
    scalar T = 300.0;
}
```

<details>
<summary><b>📊 Expected Output & Extensions</b></summary>

**Questions:**
1. What happens with `properties["undefined"]`?
2. How do you remove an entry?
3. How would you iterate over all key-value pairs?

**Solution (iteration):**
```cpp
forAllConstIter(HashTable<scalar, word>, properties, iter)
{
    Info << "Property: " << iter.key() 
         << " = " << iter.object() << endl;
}

// Removal
properties.erase("viscosity");
```

**Common Pitfall:** Using `operator[]` on missing keys causes FatalError. Always use `found()` first for optional keys.
</details>

---

### Exercise 4: autoPtr Ownership Transfer

**WHAT:** Understand unique ownership and transfer semantics with `autoPtr`.

**WHY:** `autoPtr` prevents memory leaks when transferring ownership between scopes (factory functions, class members).

**HOW:** Create with ownership, check validity, transfer ownership explicitly.

```cpp
// Create with ownership
autoPtr<volScalarField> fieldPtr
(
    new volScalarField
    (
        IOobject("T", runTime.timeName(), mesh),
        mesh,
        dimensionedScalar("T", dimTemperature, 300)
    )
);

// Access reference (no ownership change)
volScalarField& field = fieldPtr();

// Check validity
if (fieldPtr.valid())
{
    Info << "Field has " << field.size() << " cells" << endl;
}

// Transfer ownership
autoPtr<volScalarField> newOwner = std::move(fieldPtr);

// fieldPtr is now empty!
if (!fieldPtr.valid())
{
    Info << "Ownership transferred" << endl;
}
```

<details>
<summary><b>📊 Expected Output & Common Mistakes</b></summary>

**Questions:**
1. What happens if you access `fieldPtr` after `std::move`?
2. When should you use `std::move` vs copy?
3. How do you reset an `autoPtr` to empty?

**Solution:**
```cpp
// After std::move, fieldPtr is null
// Accessing fieldPtr() would be fatal error

// Reset to empty explicitly
fieldPtr.reset();

// Or reset with new object
fieldPtr.reset(new volScalarField(...));

// Common factory pattern
autoPtr<volScalarField> createField(const word& name)
{
    return autoPtr<volScalarField>
    (
        new volScalarField(IOobject(name, ...), mesh)
    );
}
```

**Key Rule:** After `std::move`, the source is invalidated. Never use it again.
</details>

---

### Exercise 5: tmp Reference Counting

**WHAT:** Use `tmp` for efficient temporary field management in calculations.

**WHY:** `tmp` eliminates unnecessary copies in chained operations (e.g., `fvc::div(fvc::grad(p))`) and provides automatic cleanup.

**HOW:** Accept `tmp` returns from functions, use references to access, let cleanup happen automatically.

```cpp
// Function returning temporary
tmp<volScalarField> computeMagnitude(const volVectorField& vf)
{
    return tmp<volScalarField>
    (
        new volScalarField(mag(vf))
    );
}

// Usage
tmp<volScalarField> tMag = computeMagnitude(U);
volScalarField& magU = tMag();

// Real-world: fvc:: operations return tmp
tmp<volVectorField> gradP = fvc::grad(p);
volVectorField& pressureGrad = gradP();

// Automatic cleanup when gradP goes out of scope
```

<details>
<summary><b>📊 Expected Output & Best Practices</b></summary>

**Questions:**
1. Why does `fvc::grad(p)` return `tmp` instead of a reference?
2. What happens if you assign `gradP` to another `tmp`?
3. When should you call `.ptr()`?

**Solution:**
```cpp
// Copy increments reference count
tmp<volVectorField> gradP2 = gradP;  // Both share ownership

// Explicitly take ownership (rarely needed)
autoPtr<volVectorField> uniqueGrad = gradP.ptr();
// gradP is now null

// Common pattern: inline usage
volVectorField gradP = fvc::grad(p);
// tmp destroyed immediately after assignment

// Chained operations (no intermediate fields!)
tmp<volScalarField> divGradU = fvc::div(fvc::grad(U));
```

**Key Insight:** `tmp` enables efficient expression templates. Temporary fields are automatically cleaned up when no longer referenced.
</details>

---

### Exercise 6: PtrList Polymorphism

**WHAT:** Manage multiple fields with `PtrList` for polymorphic collections.

**WHY:** `PtrList` is essential for managing collections of objects (boundary conditions, patch fields) where polymorphism and ownership management are required.

**HOW:** Create `PtrList` with size, use `set()` to assign pointers, access via indexing.

```cpp
// List of 3 scalar fields
PtrList<volScalarField> fields(3);

forAll(fields, i)
{
    fields.set
    (
        i,
        new volScalarField
        (
            IOobject("field" + name(i), runTime.timeName(), mesh),
            mesh,
            dimensionedScalar("zero", dimless, 0)
        )
    );
}

// Access
volScalarField& f0 = fields[0];
volScalarField& f1 = fields[1];

// PtrList owns the pointers - automatic cleanup
```

<details>
<summary><b>📊 Expected Output & Extensions</b></summary>

**Questions:**
1. What happens if you don't call `set()` for an index?
2. How do you resize a `PtrList`?
3. What's the difference between `set(i, ptr)` and `set(i)`?

**Solution:**
```cpp
// Check if pointer is set
if (fields.set(0))  // Returns true if index 0 has a pointer
{
    // Access is safe
}

// Resize (preserves existing pointers)
fields.setSize(5);

// Clear specific index (deletes pointer)
fields.set(0).reset(NULL);
// Or simply:
fields.set(0);

// Clear all
PtrList<volScalarField> emptyFields;
fields.transfer(emptyFields);
```

**Common Pattern:** `PtrList` is ideal for boundary fields (`volField<T>::BoundaryField` is essentially `PtrList`).
</details>

---

## Concept Check

### 1. Container Selection

<details>
<summary><b>❓ Question: When should you use List vs DynamicList?</b></summary>

**Answer:**

- **Use `List<T>` when:**
  - **WHAT:** Final size is known at construction
  - **WHY:** Zero overhead, compile-time allocation
  - **HOW:** Construct with known size, no growth operations
  
- **Use `DynamicList<T>` when:**
  - **WHAT:** Size is unknown or will grow
  - **WHY:** Automatic memory management, efficient appends
  - **HOW:** Append elements, convert to `List` at the end

**Real-world example:**
```cpp
// Cell centers: known size
vectorField cellCentres = mesh.C();

// Boundary cells: unknown until runtime
DynamicList<label> boundaryCells;
forAll(mesh.boundary(), patchI)
{
    // ...collect cells
}
List<label> boundaryCellsList = boundaryCells;
```
</details>

---

### 2. Memory Management

<details>
<summary><b>❓ Question: autoPtr vs tmp - when to use which?</b></summary>

**Answer:**

| Use Case | Choice | What | Why |
|----------|--------|------|-----|
| Factory function | `autoPtr` | Unique ownership transfer | Clear ownership semantics |
| fvc:: operations | `tmp` | Shared temporaries | Efficient chaining |
| Class member | `autoPtr` | Exclusive ownership | Lifecycle tied to class |
| Function return | `tmp` if potentially shared | Reference counting | Avoid copies |
| Function return | `autoPtr` if unique | Ownership transfer | Explicit transfer |

**Key distinction:**
- `autoPtr` = "I own this object exclusively" (unique ownership)
- `tmp` = "This object might be shared, clean up when last reference dies" (shared ownership)
</details>

---

### 3. tmp in OpenFOAM

<details>
<summary><b>❓ Question: Why do all fvc:: functions return tmp?</b></summary>

**Answer:**

**WHAT:** All finite volume calculus operations (`fvc::grad`, `fvc::div`, etc.) return `tmp<T>`.

**WHY:**
1. **Avoid unnecessary copies:** The result might be used immediately or assigned
2. **Expression templates:** Enables efficient chained operations
3. **Automatic cleanup:** Temporary fields are destroyed when no longer needed

**HOW:**
```cpp
// Without tmp: would require 3 allocations
volScalarField laplacianP = fvc::div(fvc::grad(p));

// With tmp: grad(p) temporary cleaned up after div() consumes it
// - grad(p) creates tmp<volVectorField>
// - div() consumes it, creates tmp<volScalarField>
// - Assignment to laplacianP, tmp destroyed
```

**Performance gain:** Eliminates copies in complex expressions like `fvc::div(fvc::grad(fvc::flux(U)))`.

**Real-world impact:** In large CFD simulations, this optimization can save gigabytes of memory allocations per time step.
</details>

---

## Common Pitfalls & Solutions

### Pitfall 1: Forgetting to Check HashTable Keys

**WHAT:** Accessing missing keys causes FatalError.

**WHY:** `HashTable::operator[]` has undefined behavior for missing keys (OpenFOAM implementation throws FatalError).

**HOW:** Always use `found()` for optional keys.

```cpp
// ❌ PROBLEM:
scalar value = properties["missingKey"];  // FatalError!

// ✅ SOLUTION:
if (properties.found("missingKey"))
{
    scalar value = properties["missingKey"];
}
else
{
    // Handle missing key (use default, throw warning, etc.)
}
```

---

### Pitfall 2: Using Moved autoPtr

**WHAT:** Accessing an `autoPtr` after `std::move` causes crash.

**WHY:** `std::move` transfers ownership, leaving the source empty/null.

**HOW:** Never use the source after `std::move`.

```cpp
// ❌ PROBLEM:
autoPtr<T> ptr1 = ...;
autoPtr<T> ptr2 = std::move(ptr1);
ptr1()->someMethod();  // Crash! ptr1 is null

// ✅ SOLUTION:
autoPtr<T> ptr1 = ...;
autoPtr<T> ptr2 = std::move(ptr1);
// Never use ptr1 again
ptr2()->someMethod();  // OK
```

---

### Pitfall 3: Unnecessary tmp Copies

**WHAT:** Converting `tmp` to references unnecessarily.

**WHY:** Defeats the purpose of reference counting - creates extra copies.

**HOW:** Use `tmp` directly, let it manage lifetime.

```cpp
// ❌ PROBLEM:
tmp<volScalarField> tField = fvc::grad(p);
volScalarField field = tField();  // Unnecessary conversion

// ✅ SOLUTION:
// Direct assignment (tmp converts automatically)
volScalarField field = fvc::grad(p);

// Or keep as tmp if passing to another function
tmp<volScalarField> tField = fvc::grad(p);
tmp<volScalarField> tDiv = fvc::div(tField);
```

---

## Next Steps

### Continue Your Learning Journey

#### 1. Explore Real OpenFOAM Source Code

**WHAT:** Study actual implementations to solidify understanding.

**WHY:** Seeing production code reinforces patterns and reveals idioms not covered in tutorials.

**HOW:**
- Browse `src/OpenFOAM/containers/` for actual implementations:
  - `src/OpenFOAM/containers/Lists/List/List.H` - List implementation
  - `src/OpenFOAM/containers/HashTables/HashTable/HashTable.H` - HashTable implementation
  - `src/OpenFOAM/memory/autoPtr/autoPtr.H` - autoPtr implementation
  - `src/OpenFOAM/memory/tmp/tmp.H` - tmp implementation

**Study these specific examples:**
- `src/finiteVolume/fields/fvsFields/fvsPatchField/` - `PtrList` usage in boundary fields
- `applications/solvers/incompressible/icoFoam/icoFoam.C` - `tmp` patterns in solvers
- `src/finiteVolume/fields/fvPatchFields/basic/fixedValue/fixedValueFvPatchField.C` - `autoPtr` in boundary conditions

#### 2. Recommended Next Modules

- **04_MESH_CLASSES:** Apply container and memory concepts to mesh data structures
- **02_DIMENSIONED_TYPES:** Review dimensional analysis with containers (if needed)
- **05_Engineering_Benefits:** Real-world case studies (if available in this module)

#### 3. Practice Projects

Apply what you've learned:

**Project 1: Custom Boundary Condition**
- **WHAT:** Write a boundary condition that uses `autoPtr` for factory pattern
- **WHY:** Practice ownership transfer in real OpenFOAM extension
- **HOW:**
  ```cpp
  // In makePatchTypeField function
  autoPtr<myFvPatchField> ptr
  (
      new myFvPatchField(patch, fieldDict)
  );
  return ptr;
  ```

**Project 2: Custom Function Object**
- **WHAT:** Implement a function object using `tmp` for field calculations
- **WHY:** Practice efficient temporary field management
- **HOW:**
  ```cpp
  tmp<volScalarField> calculateMetric()
  {
      return tmp<volScalarField>
      (
          new volScalarField(fvc::div(fvc::grad(UField)))
      );
  }
  ```

**Project 3: Material Properties Utility**
- **WHAT:** Create a utility using `HashTable` for material properties
- **WHY:** Practice safe dictionary-like operations
- **HOW:**
  ```cpp
  HashTable<scalar, word> properties;
  properties.insert("rho", 1000.0);
  properties.insert("mu", 0.001);
  
  if (properties.found("rho"))
  {
      Info << "Density: " << properties["rho"] << endl;
  }
  ```

### External Resources

- **OpenFOAM Source Code:** [GitHub Repository](https://github.com/OpenFOAM/OpenFOAM-dev) - Browse `src/OpenFOAM/containers/` and `src/OpenFOAM/memory/`
- **C++ Smart Pointers:** [cppreference.com](https://en.cppreference.com/w/cpp/memory) - Compare `std::unique_ptr` with OpenFOAM's `autoPtr`
- **CFD Online:** [OpenFOAM Programming Forum](https://www.cfd-online.com/Forums/openfoam-programming-development/) - Community help
- **OpenFOAM Wiki:** [Guide to Programming](https://openfoamwiki.net/index.php/Guide:Programming_introduction) - Additional examples

---

## Key Takeaways

✅ **3W Framework Application:**
   - **WHAT:** Choose appropriate container for the data structure
   - **WHY:** Match container characteristics to use case requirements
   - **HOW:** Implement following OpenFOAM idioms and best practices

✅ **Container Selection:**
   - `List<T>` for fixed-size, known-at-creation arrays
   - `DynamicList<T>` for growing collections
   - `HashTable<T, Key>` for key-value lookups
   - `PtrList<T>` for polymorphic object collections
   - `Field<T>` for CFD field data with mathematical operators

✅ **Memory Management:**
   - `autoPtr<T>` for unique ownership (factory functions, class members)
   - `tmp<T>` for shared temporaries (fvc:: operations, expression templates)
   - Both use RAII for automatic cleanup

✅ **Best Practices:**
   - Always check `HashTable::found()` before accessing optional keys
   - Never use `autoPtr` after `std::move`
   - Use `tmp` directly, avoid unnecessary conversions
   - Convert `DynamicList` to `List` when growth is complete

✅ **Real-World Patterns:**
   - Boundary conditions use `autoPtr` for factory pattern
   - fvc:: operations return `tmp` for efficiency
   - `PtrList` manages boundary field collections
   - `HashTable` stores property dictionaries

✅ **Practice is Essential:**
   - Reading alone is insufficient
   - Write code, experiment, make mistakes
   - Study OpenFOAM source code for idioms
   - Build real utilities and extensions

**Remember:** OpenFOAM's container and memory management systems are designed for **performance** and **safety**. Understanding when and how to use each tool is critical for writing efficient, maintainable CFD code. The 3W Framework (What-Why-How) guides all design decisions - apply it consistently!

---

## Module Completion Checklist

Use this checklist to assess your readiness:

- [ ] **Understanding:** I can explain when to use each container type
- [ ] **Application:** I can write memory-safe code using `autoPtr` and `tmp`
- [ ] **Practice:** I have completed all 6 exercises with solutions
- [ ] **Debugging:** I have identified and fixed at least one common pitfall
- [ ] **Code Reading:** I have read some OpenFOAM source code using these concepts
- [ ] **Real Application:** I am ready to apply these skills in real OpenFOAM development
- [ ] **3W Framework:** I can apply What-Why-How thinking to container decisions

**If you can check all boxes, you're ready for Module 04: Mesh Classes!**

---

**Previous:** [04_Integration_and_Best_Practices.md](04_Integration_and_Best_Practices.md)  
**Next:** [04_MESH_CLASSES/00_Overview.md](../04_MESH_CLASSES/00_Overview.md)