# Containers & Memory - First Steps

Introduction to OpenFOAM's custom container system and why it differs from standard C++ libraries

---

## 🎯 Learning Objectives

By the end of this section, you will be able to:

- **Identify** the limitations of standard C++ STL containers for CFD applications
- **Explain** why OpenFOAM developed its own container system
- **Select** appropriate container types for different use cases
- **Write** basic code using OpenFOAM's fundamental containers (List, Field, HashTable)
- **Distinguish** between different memory management strategies (autoPtr vs tmp)

---

## 1. Why Not Use Standard C++ Containers?

### **What:** The STL Limitation Problem

Standard Template Library (STL) containers like `std::vector`, `std::map`, and smart pointers were designed for general-purpose programming. They lack CFD-specific functionality needed for computational fluid dynamics.

### **Why:** CFD Needs Specialized Tools

| Requirement | STL Solution | OpenFOAM Solution |
|-------------|--------------|-------------------|
| Mathematical operations on arrays | Manual loops | `Field<T>::max()`, `sum()`, `average()` |
| Parallel data distribution | Complex external libraries | Built-in decomposition support |
| Memory efficiency for large fields | Generic allocation | Optimized for CFD memory patterns |
| Temporary field management | `std::shared_ptr` overhead | `tmp<T>` with reference counting |
| Geometry-aware operations | Not available | `boundaryField`, `internalField` |

### **How:** Real-World Impact

```cpp
// STL approach - requires manual loops
std::vector<double> T(100, 300.0);
double maxT = *std::max_element(T.begin(), T.end());
double sumT = std::accumulate(T.begin(), T.end(), 0.0);

// OpenFOAM approach - built-in operations
scalarField T(100, 300.0);
scalar maxT = max(T);      // Direct call
scalar sumT = sum(T);      // Parallel-aware
```

**Performance Benefit:** OpenFOAM's `Field<T>` operations are:
- **Parallel-ready** by default (MPI-aware)
- **Optimized** for CFD access patterns
- **Concise** - less code to write and maintain

---

## 2. Container Categories Overview

### **What:** OpenFOAM's Container Taxonomy

OpenFOAM provides three main categories of containers, each designed for specific use cases in CFD simulations.

### **Why:** Different Problems Need Different Tools

| Category | Primary Use Case | Example |
|----------|------------------|---------|
| **Arrays** | Store field data (pressure, velocity, temperature) | `volScalarField`, `surfaceVectorField` |
| **Maps** | Lookup tables, boundary conditions, dictionaries | `boundaryConditions`, `transportProperties` |
| **Smart Pointers** | Memory management for large objects | Turbulence models, numerical schemes |

### **How:** Quick Selection Guide

#### **Array Containers**

| Type | When to Use | Key Features |
|------|-------------|--------------|
| `List<T>` | General-purpose dynamic array | Basic array, serial only |
| `Field<T>` | CFD field data with math operations | `max()`, `sum()`, `average()`, parallel-aware |
| `DynamicList<T>` | Growing array (unknown final size) | Efficient `append()` operations |
| `FixedList<T,N>` | Compile-time known size | Stack allocation, fixed geometry |

#### **Map Containers**

| Type | When to Use | Key Features |
|------|-------------|--------------|
| `HashTable<T,Key>` | Fast key-value lookup | O(1) access, unordered |
| `Map<T>` | Simple key-value storage | Type-safe wrapper |

#### **Smart Pointers**

| Type | Ownership Model | When to Use |
|------|-----------------|-------------|
| `autoPtr<T>` | Unique ownership | Factory methods, single-owner objects |
| `tmp<T>` | Reference-counted | Temporary field calculations (fvc:: operators) |
| `refPtr<T>` | Optional reference | Modern alternative to raw pointers |

---

## 3. First Steps: Basic Container Usage

### **What:** Essential Code Patterns

### **How:** Practical Examples

#### **3.1 Working with Lists**

```cpp
// Create a list of 100 scalars, initialized to 0.0
List<scalar> values(100, 0.0);

// Access elements
values[0] = 1.0;
values[99] = 999.0;

// Get size
label size = values.size();  // Returns 100

// Resize (keeps existing elements)
values.resize(200);
```

#### **3.2 Field Operations (CFD-Powered)**

```cpp
// Create a temperature field
scalarField T(100, 300.0);  // 100 cells, initial T = 300K

// Built-in mathematical operations
scalar maxT = max(T);           // Maximum temperature
scalar minT = min(T);           // Minimum temperature
scalar avgT = average(T);       // Average temperature
scalar sumT = sum(T);           // Sum of all values

// Element-wise operations
scalarField T2 = T + 100;       // Add 100 to all elements
scalarField T3 = T * 2.0;       // Multiply all elements by 2
```

**Why Field is Powerful:** All operations are parallel-aware. When running in parallel, `max(T)` automatically finds the global maximum across all processors.

#### **3.3 HashTable for Lookups**

```cpp
// Create a hash table for material properties
HashTable<scalar, word> props;

// Insert properties
props.insert("density", 1000.0);      // Water density (kg/m³)
props.insert("viscosity", 0.001);     // Dynamic viscosity (Pa·s)
props.insert("temperature", 293.0);   // Reference temperature (K)

// Retrieve values
scalar rho = props["density"];
scalar mu = props["viscosity"];

// Check existence
if (props.found("thermalConductivity")) {
    scalar k = props["thermalConductivity"];
}
```

---

## 4. Memory Management Fundamentals

### **What:** Why OpenFOAM Needs Custom Smart Pointers

CFD simulations allocate large amounts of memory:
- A single `volScalarField` for 1 million cells ≈ 8 MB (double precision)
- Typical case: 10-100 fields = 80-800 MB minimum
- **Temporary fields** created during calculations can cause memory leaks if not managed properly

### **Why:** autoPtr vs tmp

| Pointer | Ownership | Typical Use | Example |
|---------|-----------|-------------|---------|
| **autoPtr** | Unique, transferable | Factory returns, single-owner objects | Turbulence model creation |
| **tmp** | Reference-counted | Temporary field calculations | fvc::div, fvc::grad results |
| **refPtr** | Optional reference | Modern alternative to raw pointers | Optional boundary conditions |

### **How:** Usage Patterns

#### **4.1 autoPtr (Unique Ownership)**

```cpp
// Factory method returning autoPtr
autoPtr<incompressible::turbulenceModel> turbulenceModel =
    incompressible::turbulenceModel::New(U, phi, laminarTransport);

// Transfer ownership to another autoPtr
autoPtr<incompressible::turbulenceModel> myModel = turbulenceModel;

// Access the underlying object
incompressible::turbulenceModel& model = myModel();

// Use the model
scalar k = model.k();  // Access turbulent kinetic energy

// Automatic cleanup when myModel goes out of scope
```

**Key Points:**
- Ownership can be **transferred** (move semantics)
- Only **one** autoPtr can own the object at a time
- Object is **automatically deleted** when autoPtr goes out of scope

#### **4.2 tmp (Reference Counted)**

```cpp
// fvc::grad returns tmp<volVectorField>
tmp<volVectorField> tgradP = fvc::grad(p);

// Option 1: Use immediately and let tmp clean up
volVectorField& gradP = tgradP();

// Option 2: Transfer to a named field
volVectorField gradP("gradP", tgradP);

// Option 3: Keep as tmp for further operations
tmp<volScalarField> tdivGradP = fvc::div(tgradP);  // tgradP automatically cleaned up
```

**Key Points:**
- **Reference counting** allows multiple tmp objects to share the same data
- When reference count reaches **zero**, object is deleted
- Enables **expression chaining** without intermediate copies

---

## 5. Module Roadmap

This module provides comprehensive coverage of OpenFOAM's container and memory management systems:

| Section | Content | Focus |
|---------|---------|-------|
| **00_Overview** | System architecture and design philosophy | High-level understanding |
| **01_Introduction** | ⭐ First steps and basic usage | **Hands-on fundamentals** |
| **02_Memory_Management** | Deep dive into autoPtr, tmp, refPtr | Advanced ownership patterns |
| **03_Container_System** | List, Field, HashTable internals | Implementation details |
| **04_Integration** | Best practices and common pitfalls | Production-ready code |
| **05_Summary_Exercises** | Practical exercises | Skill validation |

---

## 📋 Quick Reference

### Container Selection Guide

| Need | Use | Alternative |
|------|-----|-------------|
| General array | `List<T>` | `std::vector<T>` |
| CFD field data | `Field<T>` | `List<T>` (no math ops) |
| Growing array | `DynamicList<T>` | `List<T>` with manual resize |
| Fixed size | `FixedList<T,N>` | C-style array |
| Key-value lookup | `HashTable<T,Key>` | `Map<T>` |
| Unique ownership | `autoPtr<T>` | `std::unique_ptr<T>` |
| Temporary calculation | `tmp<T>` | `std::shared_ptr<T>` |

### Common Operations

```cpp
// List operations
List<scalar> list(100, 0.0);
list.append(1.0);
list.resize(200);

// Field operations
scalarField field(100, 300.0);
scalar m = max(field);      // Maximum
scalar s = sum(field);      // Sum
scalar a = average(field);  // Average

// HashTable operations
HashTable<scalar, word> table;
table.insert("key", 1.0);
scalar value = table["key"];
bool found = table.found("key");

// Smart pointer operations
autoPtr<Object> ptr(new Object);
Object& obj = ptr();

tmp<Field> tfield = fvc::grad(field);
Field& fieldRef = tfield();
```

---

## 🧠 Concept Check

<details>
<summary><b>1. Why doesn't OpenFOAM use std::vector for field data?</b></summary>

**Answer:** `std::vector` lacks built-in mathematical operations (`max()`, `sum()`, `average()`) and parallel communication support. OpenFOAM's `Field<T>` provides CFD-specific functionality and is MPI-aware from the ground up.

</details>

<details>
<summary><b>2. What's the key difference between List<T> and Field<T>?</b></summary>

**Answer:** `List<T>` is a basic dynamic array (similar to `std::vector`), while `Field<T>` extends `List<T>` with mathematical operations (`max()`, `min()`, `sum()`, `average()`) and parallel communication support.

</details>

<details>
<summary><b>3. When should you use autoPtr vs tmp?</b></summary>

**Answer:** 
- Use **autoPtr** for unique ownership (factory methods, single-owner objects like turbulence models)
- Use **tmp** for temporary calculations that may be shared (fvc:: operator results, intermediate field computations)

</details>

<details>
<summary><b>4. How does tmp prevent memory leaks?</b></summary>

**Answer:** `tmp` uses reference counting. When multiple `tmp` objects reference the same data, the reference count increases. When each `tmp` goes out of scope, the count decreases. When the count reaches zero, the data is automatically deleted.

</details>

---

## 🔗 Related Documentation

- **System Overview:** [00_Overview.md](00_Overview.md)
- **Memory Management:** [02_Memory_Management_Fundamentals.md](02_Memory_Management_Fundamentals.md)
- **Container Details:** [03_Container_System_Internals.md](03_Container_System_Internals.md)
- **Best Practices:** [04_Integration_and_Best_Practices.md](04_Integration_and_Best_Practices.md)

---

## 🎯 Key Takeaways

✓ **OpenFOAM containers** are specialized for CFD, not a replacement for STL
✓ **`Field<T>`** provides mathematical operations and parallel support out of the box
✓ **`autoPtr<T>`** manages unique ownership (use for factory returns)
✓ **`tmp<T>`** manages temporary calculations with reference counting
✓ **Choose containers** based on use case: arrays, maps, or smart pointers
✓ **Memory leaks** are prevented through automatic cleanup in smart pointers

---

## 📚 Next Steps

**→ Continue to:** [02_Memory_Management_Fundamentals.md](02_Memory_Management_Fundamentals.md)

Learn advanced memory management patterns, transfer semantics, and how to write leak-free OpenFOAM code.