# Architecture - Overview

OpenFOAM Architecture and Extensibility Mechanisms

---

## Learning Objectives

After completing this module, you should be able to:

1. **Identify** the 5 core extensibility mechanisms in OpenFOAM
2. **Distinguish** between compile-time and run-time extension approaches
3. **Select** the appropriate mechanism for specific extension scenarios
4. **Navigate** the module structure to find detailed implementation guidance
5. **Apply** the Quick Reference table to solve common extension problems

---

## 1. What is OpenFOAM Extensibility?

OpenFOAM is **highly extensible** by design through:

- **Run-Time Selection (RTS)** - Choose models/methods at runtime without recompilation
- **Dynamic Library Loading** - Add custom functionality via shared libraries
- **Function Objects** - Hook into solver execution for custom operations
- **Object Registry** - Centralized data storage and lookup system
- **Template Metaprogramming** - Compile-time polymorphism for performance

> **Key Principle:** OpenFOAM separates **interface** (abstract base classes) from **implementation** (concrete models), enabling unlimited customization while maintaining solver stability.

---

## 2. The 5 Core Extensibility Mechanisms

### 2.1 Run-Time Selection (RTS)

| Aspect | Description |
|--------|-------------|
| **Purpose** | Select models/schemes from dictionary files at runtime |
| **Use Case** | Choosing turbulence models, discretization schemes, boundary conditions |
| **Implementation** | Virtual constructor tables + `New` factory methods |
| **Benefit** | No solver recompilation needed when changing models |

```cpp
// Dictionary-driven selection
autoPtr<turbulenceModel> turb = turbulenceModel::New(dict);
```

### 2.2 Dynamic Library Loading

| Aspect | Description |
|--------|-------------|
| **Purpose** | Load custom code as shared libraries (.so files) |
| **Use Case** | Adding user-defined models, boundary conditions, function objects |
| **Implementation** | `libs` directive in controlDict triggers auto-registration |
| **Benefit** | Extend functionality without modifying OpenFOAM source code |

```cpp
// In controlDict
libs ("libmyCustomModels.so");

// All models in library auto-register on load
```

### 2.3 Function Objects

| Aspect | Description |
|--------|-------------|
| **Purpose** | Execute custom operations during solver execution |
| **Use Case** | Post-processing, monitoring, sampling, data export |
| **Implementation** | Inherit from `functionObject` class, register in `functions` dictionary |
| **Benefit** | Non-intrusive coupling with existing solvers |

```cpp
// Post-processing hooks in controlDict
functions
{
    pressureAverage 
    {
        type    fieldAverage;
        fields  (p);
    }
    
    forceCoeffs
    {
        type    forces;
        patches (wing);
    }
}
```

### 2.4 Object Registry

| Aspect | Description |
|--------|-------------|
| **Purpose** | Centralized object storage and lookup system |
| **Use Case** | Access mesh, fields, boundary conditions from custom code |
| **Implementation** | Hierarchical registry with string-based lookup |
| **Benefit** | Universal access to simulation data without passing pointers |

```cpp
// Lookup objects from registry
const volScalarField& T = 
    mesh_.lookupObject<volScalarField>("T");

// Register custom objects
mesh_.thisDb().registerObject(myCustomField);
```

### 2.5 Template Metaprogramming

| Aspect | Description |
|--------|-------------|
| **Purpose** | Compile-time polymorphism for field operations |
| **Use Case** | Generic geometric fields, matrix operations, boundary conditions |
| **Implementation** | C++ templates with partial specialization |
| **Benefit** | Type-safe, zero-overhead abstractions |

```cpp
// Generic field operations
template<class Type>
void processField(GeometricField<Type, fvPatchField, volMesh>& field);

// Instantiated for specific types
processField(scalarField);  // volScalarField
processField(vectorField);  // volVectorField
```

---

## 3. Quick Reference Table

| Need | Solution | Location |
|------|----------|----------|
| **Select model at runtime** | Run-Time Selection (RTS) | 02_Runtime_Selection_Tables.md |
| **Add custom models** | Dynamic Library Loading | 03_Dynamic_Loading.md |
| **Post-process data** | Function Objects | 04_FunctionObjects.md |
| **Access simulation data** | Object Registry | 02_Runtime_Selection_Tables.md |
| **Create generic code** | Template Metaprogramming | 05_Design_Patterns.md |
| **Debug extension issues** | Error handling + debugging | 06_Common_Errors_and_Debugging.md |

---

## 4. Module Structure

| File | Focus | Key Content |
|------|-------|-------------|
| **00_Overview** | WHAT | Architecture overview, all 5 mechanisms (current file) |
| **01_Introduction** | WHY | Motivation, benefits, when to use each mechanism |
| **02_RTS** | HOW | Runtime selection tables, virtual constructors |
| **03_Dynamic_Loading** | HOW | Shared libraries, registration macros |
| **04_FunctionObjects** | HOW | Custom function object implementation |
| **05_Patterns** | HOW | Design patterns (Factory, Strategy, Template) |
| **06_Errors** | HOW | Common errors, debugging techniques |
| **07_Exercise** | PRACTICE | Complete runnable examples with verification |

---

## 5. When to Use Each Mechanism

### Decision Tree

```
┌─────────────────────────────────────────┐
│ What do you want to extend?             │
└─────────────┬───────────────────────────┘
              │
    ┌─────────┴─────────┐
    │                   │
Physics model        Solver behavior
(turbulence,         (monitoring,
 discretization)      data export)
    │                   │
    │              Use Function Objects
    │
    ├─ Available in OpenFOAM?
    │  │
    │  ├─ Yes → Use RTS (select in dict)
    │  └─ No  → Create custom model
    │            │
    │         Dynamic Library
    │            (compile & load)
    │
┌───┴───────────────────────┐
│ Need to access data?      │
│ → Use Object Registry     │
└───────────────────────────┘
```

---

## 6. Key Takeaways

### ✓ Fundamental Concepts

1. **OpenFOAM extensibility** is built on 5 core mechanisms: RTS, Dynamic Loading, Function Objects, Object Registry, and Templates
2. **Runtime flexibility** comes from virtual constructors and dictionary-driven selection
3. **Compile-time performance** is maintained through template metaprogramming
4. **Modular design** allows extensions without modifying core solver code

### ✓ Practical Guidelines

1. **Use RTS** when selecting from existing models/schemes
2. **Use Dynamic Libraries** when creating custom models or boundary conditions
3. **Use Function Objects** for non-intrusive solver extensions (monitoring, post-processing)
4. **Use Object Registry** for accessing simulation data from custom code
5. **Use Templates** when creating generic, type-safe abstractions

### ✓ Next Steps

- Read **01_Introduction.md** to understand WHY these mechanisms matter
- Study **02_RTS.md** through **05_Patterns.md** for detailed HOW-TO implementation
- Practice with **07_Exercise.md** to build working extensions

---

## 🧠 Self-Assessment

<details>
<summary><b>1. What are the 5 core extensibility mechanisms in OpenFOAM?</b></summary>

**Answer:** Run-Time Selection (RTS), Dynamic Library Loading, Function Objects, Object Registry, and Template Metaprogramming.
</details>

<details>
<summary><b>2. When should you use Dynamic Library Loading vs. RTS?</b></summary>

**Answer:** Use **RTS** when selecting from existing registered models (no compilation needed). Use **Dynamic Library Loading** when creating custom models that don't exist in OpenFOAM (requires compilation and loading via `libs` directive).
</details>

<details>
<summary><b>3. What is the primary purpose of the Object Registry?</b></summary>

**Answer:** To provide **centralized, string-based lookup** of simulation objects (mesh, fields, boundary conditions) without needing to pass pointers through function calls.
</details>

<details>
<summary><b>4. How do Function Objects differ from custom turbulence models?</b></summary>

**Answer:** Function Objects are **non-intrusive hooks** for monitoring/post-processing that don't modify solver behavior. Custom turbulence models **replace physics calculations** and participate in the solution process.
</details>

<details>
<summary><b>5. What is the advantage of template metaprogramming in OpenFOAM?</b></summary>

**Answer:** It provides **type-safe, zero-overhead abstractions** through compile-time polymorphism, enabling generic field operations without runtime performance penalties.
</details>

---

## 📖 Related Documentation

- **Motivation & Benefits:** [01_Introduction.md](01_Introduction.md)
- **RTS Implementation:** [02_Runtime_Selection_Tables.md](02_Runtime_Selection_Tables.md)
- **Dynamic Loading:** [03_Dynamic_Loading.md](03_Dynamic_Loading.md)
- **Function Objects:** [04_FunctionObjects.md](04_FunctionObjects.md)
- **Design Patterns:** [05_Design_Patterns.md](05_Design_Patterns.md)
- **Error Handling:** [06_Common_Errors_and_Debugging.md](06_Common_Errors_and_Debugging.md)
- **Practical Exercises:** [07_Practical_Exercise.md](07_Practical_Exercise.md)