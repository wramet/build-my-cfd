# Containers & Memory - Overview

OpenFOAM Containers & Memory Management — Foundation of Efficient Data Storage

> **🎯 Why Containers & Memory Matter in OpenFOAM**
> - **Every** field, mesh, and boundary condition lives in containers
> - **Memory management errors** = memory leaks = simulation crashes
> - **Choosing the right container** = optimal performance and safety
> - **Smart pointers** prevent common C++ memory issues in CFD code

---

## 🎯 Learning Objectives

After completing this module, you will be able to:

- **Identify** the appropriate OpenFOAM container for different use cases
- **Explain** the differences between `List`, `Field`, `DynamicList`, and `FixedList`
- **Choose** between `autoPtr`, `tmp`, and `PtrList` based on ownership semantics
- **Apply** best practices for memory management in OpenFOAM code
- **Avoid** common memory leaks and performance pitfalls

---

## Overview

> **💡 OpenFOAM Containers = STL + CFD Features + Memory Safety**
>
> - `Field<T>` provides max(), sum(), average() that std::vector lacks
> - `tmp<T>` prevents memory leaks from temporary field calculations
> - `PtrList<T>` supports polymorphism for boundary conditions
> - Built-in **dimensional consistency** checking for physical quantities

```mermaid
flowchart TD
    A[OpenFOAM Containers] --> B[Array Containers]
    A --> C[Map Containers]
    A --> D[Smart Pointers]
    
    B --> E[List<T> - Dynamic Array]
    B --> F[Field<T> - CFD Array]
    B --> G[DynamicList<T> - Growable]
    B --> H[FixedList<T,N> - Compile-time]
    
    C --> I[HashTable<T,Key> - O(1) Lookup]
    C --> J[Map<T> - Ordered Map]
    
    D --> K[autoPtr<T> - Unique Ownership]
    D --> L[tmp<T> - Reference Counted]
    D --> M[PtrList<T> - Pointer List]
    
    style F fill:#e1f5ff
    style K fill:#fff4e1
    style L fill:#fff4e1
```

---

## 1. Array Containers

### **What** - Definition
Dynamic and fixed-size arrays optimized for CFD operations.

### **Why** - Benefits
- **Field<T>**: Built-in CFD operations (max, sum, average, weighted average)
- **DynamicList<T>**: Efficient growth without reallocation overhead
- **FixedList<T,N>**: Compile-time size for performance-critical code

### **How** - When to Use

| Container | Purpose | Use Case | Performance |
|-----------|---------|----------|-------------|
| `List<T>` | General dynamic array | Standard array operations | O(1) access |
| `DynamicList<T>` | Growable array | Unknown size at allocation | Efficient growth |
| `Field<T>` | CFD array with operations | Field data (U, p, T) | Optimized for math |
| `FixedList<T,N>` | Compile-time size | Small fixed arrays (tensors) | Stack allocation |

---

## 2. Map Containers

### **What** - Definition
Key-value storage structures for dictionary and property management.

### **Why** - Benefits
- **HashTable**: Fast O(1) lookup for dictionary access
- **Map**: Ordered iteration with O(log n) operations
- **Word-keyed** for string-based property storage

### **How** - When to Use

| Container | Purpose | Use Case | Complexity |
|-----------|---------|----------|------------|
| `HashTable<T,Key>` | Fast key-value lookup | Dictionary properties | O(1) lookup |
| `Map<T>` | Ordered map | Sorted iteration needed | O(log n) ops |

---

## 3. Smart Pointers

### **What** - Definition
Memory-managing pointers that automate ownership and lifetime control.

### **Why** - Benefits
- **Prevent memory leaks** in complex CFD calculations
- **Clarify ownership semantics** in code
- **Enable efficient temporary object reuse** (tmp)
- **Support polymorphic BCs** (PtrList)

### **How** - When to Use

| Type | Ownership | Use Case | Move? | Copy? |
|------|-----------|----------|-------|-------|
| `autoPtr<T>` | Unique (exclusive) | Factory methods, BC creation | ✅ Yes | ❌ No |
| `tmp<T>` | Reference counted | Temporary calculations (fvc::) | ✅ Yes | ✅ Yes |
| `PtrList<T>` | List of owned pointers | Boundary condition lists | ✅ Yes | ❌ No |

---

## 4. Quick Examples

### **What** - These examples demonstrate the most common container patterns in OpenFOAM.

### **Why** - Understanding these patterns is essential because they appear in virtually every OpenFOAM solver and utility.

### **How** - Study these patterns and apply them in your own code.

#### List — Basic Array Operations

```cpp
// Create list of 100 elements initialized to 0.0
List<scalar> values(100, 0.0);

// OpenFOAM-style iteration
forAll(values, i)
{
    values[i] = sqr(i);  // values[i] = i²
}
```

#### Field — CFD Operations

```cpp
// Create temperature field
scalarField T(100, 300.0);  // 100 cells, 300K initial

// Built-in CFD operations (not in std::vector)
scalar maxT = max(T);           // Maximum temperature
scalar avgT = average(T);       // Average temperature
scalar sumT = sum(T);           // Sum of all values
```

#### HashTable — Dictionary Access

```cpp
// Create properties dictionary
HashTable<scalar, word> props;

// Insert key-value pairs
props.insert("rho", 1000);      // Density: 1000 kg/m³
props.insert("mu", 0.001);      // Viscosity: 0.001 Pa·s

// Fast O(1) lookup
scalar rho = props["rho"];
```

#### autoPtr — Factory Pattern

```cpp
// Factory method returns autoPtr (unique ownership)
autoPtr<turbulenceModel> model = turbulenceModel::New(dict);

// Access with operator()
model->correct();

// Transfer ownership (std::move equivalent)
autoPtr<turbulenceModel> otherModel = std::move(model);
```

#### tmp — Temporary Results

```cpp
// fvc::grad() returns tmp<volScalarField>
// Automatically manages temporary memory
tmp<volScalarField> tGrad = fvc::grad(p);

// Use the gradient
volScalarField& gradP = tGrad();

// tmp destructor called here - memory freed automatically
```

---

## 5. Module Contents

### **What** - This module covers containers and memory management from fundamentals to advanced patterns.

### **Prerequisites**
- C++ fundamentals (pointers, references)
- Basic OpenFOAM syntax (forAll, etc.)

### **Expected Outcomes**
- Write memory-safe OpenFOAM code
- Choose optimal containers for performance
- Debug memory-related issues

| File | Topic | Key Concepts |
|------|-------|--------------|
| **01_Introduction** | Fundamentals | Basic container types, when to use what |
| **02_Memory_Management** | Smart pointers | autoPtr, tmp, ownership semantics |
| **03_Container_System** | Deep dive | List, Field, Hash implementation details |
| **04_Integration** | Best practices | Integration patterns, common pitfalls |
| **05_Summary** | Review & exercises | Practice problems, summary |

---

## 🧠 Concept Check

<details>
<summary><b>1. List vs Field — What's the difference?</b></summary>

**Answer:**
- **List<T>**: General-purpose array, basic operations
- **Field<T>**: CFD-optimized array with built-in operations:
  - `max()`, `min()`, `sum()`, `average()`
  - `gMax()`, `gMin()`, `gSum()` (parallel reductions)
  - Component-wise operations for vectors/tensors
</details>

<details>
<summary><b>2. autoPtr vs tmp — When to use which?</b></summary>

**Answer:**
- **autoPtr<T>**: Unique ownership, transferable
  - Use for: Factory methods, BC creation, single-owner objects
  - Cannot be copied, only moved
  
- **tmp<T>**: Reference-counted temporary
  - Use for: Temporary calculation results (fvc:: operations)
  - Can be copied, automatically manages lifetime
</details>

<details>
<summary><b>3. HashTable vs Map — Performance tradeoffs?</b></summary>

**Answer:**
- **HashTable<T,Key>**: 
  - O(1) average lookup/insert/delete
  - Unordered iteration
  - Best for: Dictionary access, property storage
  
- **Map<T>**: 
  - O(log n) lookup/insert/delete
  - Ordered iteration (sorted by key)
  - Best for: When you need sorted access
</details>

<details>
<summary><b>4. What happens if you delete an object held by tmp?</b></summary>

**Answer:**
**Don't do it!** `tmp` manages memory automatically. Manual deletion causes:
- Double-free errors (tmp tries to delete again)
- Memory corruption
- Segmentation faults

**Rule:** Never call `delete` on objects managed by smart pointers.
</details>

---

## 📖 Related Documentation

- **Next:** [01_Introduction.md](01_Introduction.md) — Container fundamentals and basic usage
- **Deep Dive:** [03_Container_System.md](03_Container_System.md) — Implementation details and advanced patterns
- **Memory Management:** [02_Memory_Management.md](02_Memory_Management.md) — Smart pointers in depth

---

## 🎯 Key Takeaways

1. **Containers are fundamental** — every OpenFOAM solver relies on them
2. **Choose wisely** — `Field` for CFD data, `List` for general arrays
3. **Smart pointers prevent leaks** — use `autoPtr` for ownership, `tmp` for temporaries
4. **HashTable for speed** — O(1) dictionary access vs O(log n) for Map
5. **Memory safety matters** — proper container use prevents crashes and leaks