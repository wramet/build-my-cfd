# Foundation Primitives - Summary

สรุป OpenFOAM Primitives — Quick Reference Card

> **ใช้หน้านี้สำหรับ:**
> - ดูสูตร/syntax อย่างรวดเร็ว
> - เปรียบเทียบ types ต่างๆ
> - เป็น cheat sheet ตอนเขียน code

---

## 🎯 Learning Objectives

**What you will be able to do after reviewing this summary:**
- Quickly identify and select the appropriate OpenFOAM primitive type for any programming task
- Understand the syntax and common operations for vectors, tensors, and dimensioned types
- Apply smart pointer patterns correctly for memory management
- Choose the right container type for different data storage needs
- Reference common operators and macros without searching through documentation

---

## 1. Basic Types

### What & Why & How

**What:** Fundamental data types that form the building blocks of all OpenFOAM code

**Why:** OpenFOAM uses specialized types instead of C++ primitives to ensure type safety, dimensional consistency, and clear code intent

**How:** Use these types based on the purpose of the variable

| Type | Purpose (Why) | Example (How) |
|------|---------------|---------------|
| `label` | Index/Counter | `label cellI = 0;` |
| `scalar` | Physical value | `scalar T = 300;` |
| `word` | Name/identifier | `word name = "p";` |
| `Switch` | Boolean flag | `Switch active = true;` |

**When to use which:**
- Need to loop through cells → `label`
- Storing temperature/pressure → `scalar`
- Reading dictionary keys → `word`
- Toggling features → `Switch`

---

## 2. Mathematical Types

### Vector

**What:** 3D geometric vector representing magnitude and direction

**Why:** Essential for CFD calculations involving velocity, position, forces, and gradients

**How:** Use vector operations for geometric calculations

```cpp
// Creation
vector v(1, 2, 3);

// Common operations
scalar len = mag(v);           // Magnitude: |v|
vector unit = v / mag(v);      // Unit vector: v̂
scalar dot = v1 & v2;          // Dot product: v₁·v₂
vector cross = v1 ^ v2;        // Cross product: v₁×v₂
```

**Decision Guide - Vector vs Tensor:**
- Need magnitude/direction only → `vector`
- Need stress/strain rates → `tensor`
- Need rotation matrices → `tensor`

### Tensor

**What:** 3×3 matrix representing second-order quantities

**Why:** Required for stress, strain, and deformation rate calculations

**How:** Use tensor operations for matrix manipulations

```cpp
// Identity tensor
tensor T(1,0,0, 0,1,0, 0,0,1);

// Operations
scalar trace = tr(T);          // Trace: tr(T)
tensor inv = inv(T);           // Inverse: T⁻¹
symmTensor S = symm(T);        // Symmetric part
scalar det = det(T);           // Determinant
```

---

## 3. Dimensioned Types

### What & Why & How

**What:** Numerical values with attached physical units for dimensional consistency

**Why:** Prevents unit mismatch errors (the #1 source of CFD bugs) and enables automatic unit conversion

**How:** Always use dimensioned types for physical quantities with units

```cpp
// Creation
dimensionedScalar rho("rho", dimDensity, 1000);

// Access components
word n = rho.name();                    // "rho"
dimensionSet d = rho.dimensions();      // [mass][length]⁻³
scalar v = rho.value();                 // 1000

// Operations (dimension-checked)
dimensionedScalar Re = rho * U * L / mu;  // OK if dimensionless
```

**Decision Tree - Dimensioned vs Plain Type:**

```
Is this a physical quantity with units?
├─ Yes → Use dimensioned<Type>
│   ├─ Scalar → dimensionedScalar
│   ├─ Vector → dimensionedVector
│   └─ Tensor → dimensionedTensor
└─ No → Use plain type (label, scalar, vector)
    ├─ Index/counter → label
    ├─ Pure number → scalar
    └─ Position/velocity → vector
```

**Common Pitfalls:**
❌ **Wrong:** `scalar p = 101325;` (no units)
✅ **Right:** `dimensionedScalar p("p", dimPressure, 101325);`

---

## 4. Smart Pointers

### What & Why & How

**What:** Smart pointer types that manage memory automatically and prevent memory leaks

**Why:** OpenFOAM uses these for safe ownership transfer, temporary object management, and polymorphic collections

**How:** Choose based on ownership semantics

| Type | Ownership Pattern | Use Case |
|------|-------------------|----------|
| `autoPtr` | Unique ownership | Factory methods, exclusive ownership |
| `tmp` | Temporary result | Function returns, intermediate calculations |
| `PtrList` | Polymorphic collection | Arrays of derived objects |

```cpp
// autoPtr: Unique ownership
autoPtr<Model> model(Model::New(dict));

// tmp: Temporary result (auto-deleted)
tmp<volScalarField> tField = fvc::grad(p);
volScalarField& field = tField();  // Reference to use

// PtrList: Polymorphic collection
PtrList<volScalarField> fields(n);
fields.set(i, new volScalarField(...));
```

**Decision Tree - Smart Pointer Selection:**

```
Need to manage dynamic object?
├─ Factory creates object → autoPtr<T>
│   └─ Exclusive ownership, will be moved
├─ Function returns temporary → tmp<T>
│   └─ Auto-deleted after use
└─ Collection of derived objects → PtrList<T>
    └─ Runtime polymorphism needed
```

**Common Pitfalls:**
❌ **Wrong:** Storing `tmp` longer than needed (holds memory)
✅ **Right:** Use `tmp` only as function return or temporary

---

## 5. Containers

### What & Why & How

**What:** Specialized container classes optimized for CFD operations

**Why:** Different data structures are optimized for different access patterns and operations

**How:** Choose based on usage pattern and required operations

| Container | When to Use | Key Methods |
|-----------|-------------|-------------|
| `List<T>` | Fixed-size array | `append()`, `remove()`, `size()` |
| `Field<T>` | CFD field data | `max()`, `min()`, `average()`, `sum()` |
| `HashTable` | Key-value lookup | `insert()`, `found()`, `lookup()` |
| `DynamicList` | Growing array | `append()` (auto-grows) |

```cpp
// List: General purpose
List<scalar> values(100, 0.0);

// Field: CFD operations
scalarField T(100, 300.0);
scalar maxT = max(T);           // Built-in reduction
scalar avgT = average(T);       // Statistical operations

// HashTable: Dictionary-like access
HashTable<scalar, word> props;
props.insert("rho", 1000);
if (props.found("mu")) { ... }

// DynamicList: Auto-expanding
DynamicList<scalar> data;
data.append(1.0);  // Grows automatically
```

**Decision Tree - Container Selection:**

```
Need to store multiple values?
├─ Need key-based lookup → HashTable
│   └─ Dictionary-like access
├─ Need CFD operations → Field<T>
│   └─ Built-in math/reductions
├─ Size unknown at compile → DynamicList<T>
│   └─ Auto-expanding
└─ Fixed size known → List<T>
    └─ Basic array operations
```

**Common Pitfalls:**
❌ **Wrong:** Using `List` when you need `Field` operations
✅ **Right:** Use `Field` for mesh data to get built-in CFD operations

---

## 6. Common Operations Reference

### Scalar Operations

| Operation | Code | Description |
|-----------|------|-------------|
| Magnitude | `mag(v)` | |v| for vector/tensor |
| Square | `sqr(x)` | x² |
| Square root | `sqrt(x)` | √x |
| Absolute | `mag(x)` | \|x\| for scalar |

### Vector Operations

| Operation | Code | Returns |
|-----------|------|---------|
| Dot product | `a & b` | scalar |
| Cross product | `a ^ b` | vector |
| Component access | `v.x()`, `v.y()`, `v.z()` | scalar |

### Tensor Operations

| Operation | Code | Description |
|-----------|------|-------------|
| Trace | `tr(T)` | Sum of diagonal |
| Determinant | `det(T)` | Matrix determinant |
| Inverse | `inv(T)` | T⁻¹ |
| Symmetric part | `symm(T)` | (T + Tᵀ)/2 |
| Skew part | `skew(T)` | (T - Tᵀ)/2 |

---

## 7. forAll Macro

### What & Why & How

**What:** OpenFOAM's range-based loop macro for iterating over containers

**Why:** Cleaner syntax than traditional C++ loops, automatically handles container size

**How:** Use for all read-only iterations over OpenFOAM containers

```cpp
// forAll macro (preferred)
forAll(field, i)
{
    field[i] = compute(i);
}

// Equivalent traditional loop (avoid)
for (label i = 0; i < field.size(); i++)
{
    field[i] = compute(i);
}

// Const version for read-only
forAll(field, i)
{
    Info << field[i] << endl;
}
```

**Decision Guide - Loop Selection:**

```
Need to iterate over container?
├─ Read-only access → forAll(field, i)
├─ Need index and value → forAll(field, i)
└─ Modifying container → forAll(field, i)
    └─ For cell/face loops, use specialized iterators
```

**Common Pitfalls:**
❌ **Wrong:** Mixing `forAll` with container modification that changes size
✅ **Right:** Use `forAll` only when container size doesn't change

---

## 🎯 Quick Reference Card

### Decision Table: Type Selection

| Need | Use Type | Why |
|------|----------|-----|
| **Loop index** | `label` | Integer counter |
| **Physical value** | `scalar` | Double precision |
| **Dictionary key** | `word` | String without spaces |
| **On/off flag** | `Switch` | Boolean wrapper |
| **3D position/velocity** | `vector` | Geometric quantity |
| **Stress/strain** | `tensor` | 3×3 matrix |
| **Value with units** | `dimensionedScalar` | Dimensional safety |
| **Unique ownership** | `autoPtr<T>` | Exclusive ownership |
| **Temporary field** | `tmp<T>` | Auto cleanup |
| **Polymorphic array** | `PtrList<T>` | Derived objects |
| **Fixed array** | `List<T>` | Basic container |
| **CFD data** | `Field<T>` | Built-in operations |
| **Key-value map** | `HashTable<K,V>` | Fast lookup |
| **Growing array** | `DynamicList<T>` | Auto expansion |

### Syntax Quick Lookup

```cpp
// Type declarations
label i = 0;
scalar x = 1.0;
vector v(0, 0, 0);
tensor T(1,0,0, 0,1,0, 0,0,1);

// Dimensioned types
dimensionedScalar rho("rho", dimDensity, 1000);

// Smart pointers
autoPtr<Model> ptr(new Model);
tmp<volScalarField> tFld = fvc::grad(p);

// Containers
List<scalar> lst(10, 0.0);
Field<scalar> fld(10, 0.0);
HashTable<word, scalar> table;

// Loops
forAll(container, i) { ... }
```

---

## 🧠 Concept Check

<details>
<summary><b>1. & vs ^ ต่างกันอย่างไร?</b></summary>

**What:** Both are vector operators with different results
- **`&`** (Dot product) → Returns **scalar**: `a · b = |a||b|cos(θ)`
- **`^`** (Cross product) → Returns **vector**: `a × b` perpendicular to both

**When to use:**
- Dot product → Project one vector onto another, calculate work
- Cross product → Find perpendicular vector, calculate torque

```cpp
scalar dotProd = v1 & v2;  // Scalar result
vector crossProd = v1 ^ v2; // Vector result
```
</details>

<details>
<summary><b>2. Field vs List ต่างกันอย่างไร?</b></summary>

**What:** Both are containers but `Field` is CFD-specialized

**Key differences:**
- **`List<T>`**: Basic array with append/remove operations
- **`Field<T>`**: CFD-enhanced list with mathematical operations

**When to use Field:**
```cpp
scalarField T(100, 300.0);
scalar maxT = max(T);        // Built-in max
scalar avgT = average(T);    // Built-in average
scalar sumT = sum(T);        // Built-in sum
```

**When to use List:**
```cpp
List<scalar> values(100);
values.append(1.0);          // Basic operations only
```

**Decision:** Use `Field` for mesh/data fields, `List` for general arrays
</details>

<details>
<summary><b>3. tmp ใช้เมื่อไหร่?</b></summary>

**What:** `tmp<T>` is a smart pointer for temporary objects

**When to use:**
- Function returns a temporary field (e.g., `fvc::grad(p)`)
- Intermediate calculation results
- Avoiding unnecessary copies

**Why:**
```cpp
// WITHOUT tmp - creates copy
volScalarField gradP = fvc::grad(p);  // Copy made

// WITH tmp - no copy
tmp<volScalarField> tGradP = fvc::grad(p);  // Temporary
volScalarField& gradP = tGradP();  // Reference
// tGradP auto-deleted after use
```

**Common pattern:**
```cpp
tmp<volScalarField> tResult = someFunction();
resultRef = tResult();  // Get reference
// tResult automatically cleaned up
```
</details>

<details>
<summary><b>4. autoPtr vs tmp: เลือกอะไรเมื่อไหร่?</b></summary>

**Decision Tree:**

```
Need smart pointer?
├─ Factory function creates object → autoPtr<T>
│   └─ Model::New() returns autoPtr
│   └─ You take exclusive ownership
├─ Function returns computed field → tmp<T>
│   └─ fvc::grad() returns tmp
│   └─ Auto-deleted after use
└─ Storing in collection → PtrList<T>
    └─ Runtime polymorphism
```

**Examples:**
```cpp
// autoPtr: Exclusive ownership
autoPtr<fvMesh> meshPtr = createMesh();
fvMesh& mesh = meshPtr();  // Reference

// tmp: Temporary result
tmp<volScalarField> tGrad = fvc::grad(p);
volScalarField& grad = tGrad();  // Auto-cleanup
```
</details>

<details>
<summary><b>5. dimensionedScalar จำเป็นต้องใช้เสมอหรือ?</b></summary>

**What:** `dimensionedScalar` adds unit checking to values

**When REQUIRED:**
- Reading from dictionaries (units specified in file)
- Physical constants with units
- Boundary conditions with units

**When NOT needed:**
- Loop counters → `label`
- Pure numbers (Re, Pr) → `scalar`
- Array indices → `label`

**Decision Guide:**
```cpp
// NEEDS units
dimensionedScalar p("p", dimPressure, 101325);

// NO units needed
label cellI = 0;           // Just an index
scalar Re = 1000;          // Dimensionless
scalar pi = 3.14159;       // Pure number
```

**Rule of thumb:** If it has physical units, use `dimensioned<Type>`
</details>

---

## 🎯 Best Practices Summary

### Type Selection Rules

1. **Always use dimensioned types for physical quantities**
   - Prevents unit errors at compile time
   - Documents units in code
   - Enables automatic unit conversion

2. **Use smart pointers correctly**
   - `autoPtr` for factory-created objects
   - `tmp` for temporary returns only
   - Never store `tmp` longer than necessary

3. **Choose containers based on operations needed**
   - `Field` for CFD data (has built-in reductions)
   - `List` for general arrays
   - `HashTable` for dictionary-like access

4. **Prefer `forAll` over traditional loops**
   - Cleaner syntax
   - Automatically handles size
   - Standard OpenFOAM idiom

### Common Mistakes to Avoid

❌ **Don't:**
```cpp
scalar p = 101325;  // No units!
List<volScalarField> fields;  // Wrong container
for (int i = 0; i < field.size(); i++)  // Wrong loop type
```

✅ **Do:**
```cpp
dimensionedScalar p("p", dimPressure, 101325);  // Units!
PtrList<volScalarField> fields;  // Polymorphic collection
forAll(field, i)  // OpenFOAM style
```

---

## 📖 Cross-References

### Within This Module

- **Overview:** [00_Overview.md](00_Overview.md) — Module structure and learning path
- **Introduction:** [01_Introduction.md](01_Introduction.md) — Why these primitives matter
- **Basic Types:** [02_Basic_Primitives.md](02_Basic_Primitives.md) — Deep dive on label, scalar, word
- **Dimensioned Types:** [03_Dimensioned_Types_Intro.md](03_Dimensioned_Types_Intro.md) — Dimension system explained
- **Smart Pointers:** [04_Smart_Pointers.md](04_Smart_Pointers.md) — Memory management patterns
- **Containers:** [05_Containers.md](05_Containers.md) — All container types detailed
- **Exercises:** [07_Exercises.md](07_Exercises.md) — Practice problems

### Related Modules

- **Mesh Data:** See [MODULE_02](../../MODULE_02_MESHING_AND_CASE_SETUP) for `Field` usage on meshes
- **Solver Development:** See [MODULE_03](../../MODULE_03_SINGLE_PHASE_FLOW) for `tmp` in function returns
- **Custom Boundary Conditions:** See [MODULE_05](../../MODULE_05_OPENFOAM_PROGRAMMING) for `autoPtr` in factories

---

## 🔍 Further Reading

- **Source Code:** `$FOAM_SRC/OpenFOAM/fields/` — Implementation of all types
- **Programming Guide:** OpenFOAM Programmer's Guide Ch. 2-3
- **Dimensioned Types Guide:** See [03_Dimensioned_Types_Intro.md](03_Dimensioned_Types_Intro.md)
- **Container Reference:** See [05_Containers.md](05_Containers.md)

---

## 📋 Check Your Understanding

**Before moving to exercises, verify you can:**

- [ ] Choose the correct basic type (label/scalar/word/Switch)
- [ ] Use vector and tensor operations correctly
- [ ] Create and manipulate dimensionedScalar
- [ ] Select appropriate smart pointer (autoPtr/tmp/PtrList)
- [ ] Pick the right container for your use case
- [ ] Write forAll loops correctly
- [ ] Avoid common type selection mistakes

---

## 🎯 Key Takeaways

1. **Type Safety First:** Always use dimensioned types for physical quantities to catch unit errors at compile time

2. **Smart Pointer Semantics Matter:**
   - `autoPtr` = exclusive ownership (factory pattern)
   - `tmp` = temporary result (auto cleanup)
   - `PtrList` = polymorphic collection

3. **Container Choice Drives Performance:**
   - `Field<T>` for CFD operations (built-in math)
   - `List<T>` for general arrays
   - `HashTable<K,V>` for fast lookups

4. **Use OpenFOAM Idioms:** `forAll` loops, `&` for dot product, `^` for cross product, `mag()` for magnitude

5. **Think in Physics:** When selecting types, ask "Does this have units?" → If yes, use dimensioned type

6. **This Summary is Your Cheat Sheet:** Bookmark this page for quick syntax lookup when writing OpenFOAM code

---

**Next:** [07_Exercises.md](07_Exercises.md) — Practice these concepts with hands-on exercises