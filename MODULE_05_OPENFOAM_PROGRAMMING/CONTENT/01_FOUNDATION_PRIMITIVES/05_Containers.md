# OpenFOAM Containers

คอนเทนเนอร์ใน OpenFOAM — Data structures สำหรับ CFD

---

## Learning Objectives | วัตถุประสงค์การเรียนรู้

After completing this section, you should be able to:
- **Distinguish** between different container types (List, Field, HashTable, PtrList) and their use cases
- **Apply** the appropriate container for specific CFD programming scenarios
- **Utilize** Field operations and mathematical functions for efficient data manipulation
- **Implement** memory-efficient coding practices to avoid performance bottlenecks
- **Choose** between List and Field based on data characteristics and required operations

---

## Overview

OpenFOAM provides specialized container classes that extend standard C++ containers with CFD-specific functionality. Unlike STL containers, OpenFOAM containers include mathematical operations, field aggregations, and seamless integration with OpenFOAM's I/O system.

> **💡 ความแตกต่างจาก STL:**
> - OpenFOAM containers = **STL + CFD features**
> - `Field<T>` มี `max()`, `min()`, `average()`, `sum()`
> - I/O compatible กับ OpenFOAM format

---

## 1. List Types

### What (คืออะไร)
List containers are dynamic array structures that provide flexible data storage with automatic memory management.

### Why (ทำไมสำคัญ)
- **Performance**: Choosing the wrong container leads to poor performance
- **Flexibility**: Different list types optimize for different usage patterns
- **Memory**: Proper selection prevents unnecessary reallocations and memory waste

### How (ใช้อย่างไร)

| Container | ลักษณะ | ใช้เมื่อ | Performance |
|-----------|-------|---------|-------------|
| `List<T>` | Dynamic array | General purpose, size known | O(1) access, O(n) resize |
| `DynamicList<T>` | Auto-grow | Building up data incrementally | Amortized O(1) append |
| `SortedList<T>` | Always sorted | Fast lookup required | O(log n) search |
| `FixedList<T, N>` | Fixed size | Small, known size at compile-time | Stack allocation, fastest |

#### List Example

```cpp
// Create and initialize
List<scalar> values(100, 0.0);  // 100 elements, all 0

// Access
values[0] = 1.0;              // Index access
scalar first = values.first();  // First element
scalar last = values.last();    // Last element

// Size operations
label n = values.size();
values.resize(200);            // Resize

// Append
values.append(999.0);          // Add to end
```

#### DynamicList — When Size Unknown

```cpp
// Create with capacity (not size)
DynamicList<scalar> temps(100);  // Capacity 100, size 0

// Append elements
forAll(cells, i)
{
    if (needThisCell(i))
    {
        temps.append(T[i]);  // Grows automatically
    }
}

// Transfer to fixed List when done (optional)
List<scalar> finalTemps(temps);
```

> **ทำไมใช้ DynamicList?**
> - `List::append()` = reallocate ทุกครั้ง (ช้า)
> - `DynamicList::append()` = pre-allocated growth (เร็ว)

---

## 2. HashTable — Key-Value Storage

### What (คืออะไร)
HashTable provides O(1) key-based lookup for storing key-value pairs, commonly used for named properties and dictionary lookups.

### Why (ทำไมสำคัญ)
- **Fast Lookup**: Constant-time access by name/key instead of linear search
- **Flexible Storage**: Store any type with string keys
- **Dictionary Integration**: Natural fit for OpenFOAM dictionary system

### How (ใช้อย่างไร)

> **ใช้เมื่อ:** ต้องการ lookup by name/key

```cpp
// String-keyed hash (common for properties)
HashTable<scalar, word> props;
props.insert("density", 1000);
props.insert("viscosity", 1e-3);

// Access
scalar rho = props["density"];

// Check existence before access (safe)
if (props.found("density"))
{
    scalar rho = props["density"];
}

// Iterate
forAllConstIters(props, iter)
{
    Info << iter.key() << " = " << iter.val() << endl;
}
```

**Common Use Cases:**
- Boundary condition properties by patch name
- Transport coefficients lookup
- Material property dictionaries

---

## 3. Field Types — The Heart of OpenFOAM

### What (คืออะไร)
Field<T> is the fundamental data structure for CFD computations, representing arrays of physical quantities on mesh entities (cells, faces, points).

### Why (ทำคัญที่สุด)
- **Mathematical Operations**: Built-in element-wise arithmetic and mathematical functions
- **CFD Aggregations**: Native support for max, min, average, sum operations
- **Foundation**: volScalarField, volVectorField, surfaceScalarField all inherit from Field<T>
- **Performance**: Optimized for numerical computations with expression templates

### How (ใช้อย่างไร)

> **ทำไม Field สำคัญที่สุด?**
> - **volScalarField, volVectorField สืบทอดจาก Field**
> - Field = List + mathematical operations + CFD functions

#### Basic Field Operations

```cpp
// Scalar field
scalarField T(100, 300.0);        // 100 cells, T = 300

// Vector field
vectorField U(100, vector::zero);  // 100 cells, U = (0,0,0)

// Mathematical operations
scalarField T2 = sqr(T);          // T²
scalarField rootT = sqrt(T);      // √T
scalarField absT = mag(T);        // |T|

// CFD aggregations
scalar maxT = max(T);             // Maximum
scalar minT = min(T);             // Minimum
scalar avgT = average(T);         // Average
scalar sumT = sum(T);             // Sum
```

#### Field Arithmetic

```cpp
scalarField a(100, 1.0);
scalarField b(100, 2.0);

// Element-wise operations
scalarField c = a + b;    // [3, 3, 3, ...]
scalarField d = a * b;    // [2, 2, 2, ...]
scalarField e = a / b;    // [0.5, 0.5, 0.5, ...]

// Scalar multiplication
scalarField f = 2.0 * a;  // [2, 2, 2, ...]
```

#### forAll Macro

> **ทำไมใช้ forAll?**
> - ให้ index อัตโนมัติ
> - เข้ากับ OpenFOAM style
> - ปลอดภัยกว่า manual indexing

```cpp
forAll(T, cellI)
{
    T[cellI] = computeT(cellI);
    // cellI = 0, 1, 2, ... T.size()-1
}

// Equivalent to:
for (label cellI = 0; cellI < T.size(); cellI++)
{
    T[cellI] = computeT(cellI);
}
```

**หลาย fields ที่ใช้ indexเดียวกัน:**
```cpp
forAll(U, cellI)
{
    // cellI valid for all fields on same mesh
    U[cellI] = velocity(p[cellI], rho[cellI]);
}
```

---

## 4. PtrList — List of Pointers

### What (คืออะไร)
PtrList<T> manages a list of pointers to objects, providing automatic memory management and polymorphism support.

### Why (ทำไมสำคัญ)
- **Polymorphism**: Store base class pointers pointing to derived objects
- **Variable Size**: Handle objects of different sizes
- **Lazy Allocation**: Set individual elements later when needed
- **Automatic Cleanup**: Automatic memory deallocation on destruction

### How (ใช้อย่างไร)

> **ใช้เมื่อ:**
> - ต้องการ polymorphism (base class pointer → derived objects)
> - Object sizes vary
> - Lazy allocation (set later)

```cpp
// List of 3 pointers (initially null)
PtrList<volScalarField> fields(3);

// Set each element
forAll(fields, i)
{
    fields.set
    (
        i,
        new volScalarField
        (
            IOobject("field" + name(i), ...),
            mesh
        )
    );
}

// Access
volScalarField& f = fields[0];

// Check if set
if (fields.set(i)) { ... }  // true if not null
```

**Common Use Cases:**
- Multiple turbulence fields (k, epsilon, omega, etc.)
- Boundary condition patch fields
- Multiple species in reacting flows
- Multiple regions in multi-region simulations

---

## 5. List vs Field — Decision Guide

### Decision Flowchart

```
┌─────────────────────────────────┐
│     What data are you storing?   │
└─────────────────┬───────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
   Physical Data      General Data
   (T, p, U, rho)     (indices, names)
        │                   │
        ▼                   ▼
   ┌─────────┐         ┌─────────┐
   │ Field<T> │         │ List<T>  │
   └─────────┘         └─────────┘
        │                   │
    Need math?         Size known?
        │                   │
    ┌───┴────┐        ┌────┴────┐
    │        │        │         │
   Yes       No      Yes       No
    │        │        │         │
   Field    List    List  DynamicList
```

### Comparison Table

| Feature | List<scalar> | scalarField |
|---------|--------------|-------------|
| `max()` | ❌ | ✅ |
| `min()` | ❌ | ✅ |
| `average()` | ❌ | ✅ |
| `sum()` | ❌ | ✅ |
| Math operations (+, -, *, /) | ❌ | ✅ |
| sqr(), sqrt(), mag() | ❌ | ✅ |
| General data storage | ✅ | ✅ |
| CFD simulation data | ❌ (use Field) | ✅ |
| Memory efficiency | Higher | Lower (more features) |
| I/O compatible | Limited | Full OpenFOAM format |

**กฎ:** ถ้าข้อมูลเป็น physical quantity (T, p, U) → ใช้ Field

---

## 6. Common Operations Summary

| Operation | Description | Example | Return Type |
|-----------|-------------|---------|-------------|
| `max(field)` | Maximum value | `scalar Tmax = max(T)` | scalar |
| `min(field)` | Minimum value | `scalar Tmin = min(T)` | scalar |
| `sum(field)` | Sum of all elements | `scalar total = sum(m)` | scalar |
| `average(field)` | Simple average | `scalar Tavg = average(T)` | scalar |
| `mag(field)` | Magnitude | `scalarField speed = mag(U)` | Field<scalar> |
| `sqr(field)` | Square | `scalarField T2 = sqr(T)` | Field<T> |
| `sqrt(field)` | Square root | `scalarField rootK = sqrt(k)` | Field<T> |
| `pow(field, n)` | Power n | `scalarField T3 = pow(T, 3)` | Field<T> |
| `pos(field)` | Positive part | `scalarField Tpos = pos(T)` | Field<T> |
| `neg(field)` | Negative part | `scalarField Tneg = neg(T)` | Field<T> |

---

## 7. Performance Tips & Common Pitfalls

### Memory Efficiency

#### ❌ Avoid Unnecessary Copies

```cpp
// BAD: creates full copy
List<scalar> copy = original;  // Millions of elements copied!

// GOOD: use reference
const List<scalar>& ref = original;  // Just a pointer

// GOOD: use const reference for read-only
void process(const List<scalar>& data)  // No copy
{
    // read data...
}
```

#### ✅ Pre-allocate for DynamicList

```cpp
// BAD: grows repeatedly (many reallocations)
DynamicList<scalar> dyn;
forAll(source, i)
{
    dyn.append(source[i]);  // May reallocate each time
}

// GOOD: reserve space upfront
DynamicList<scalar> dyn(expectedSize);  // Allocate once
forAll(source, i)
{
    dyn.append(source[i]);  // No reallocation
}
```

#### ✅ Use tmp for Large Temporaries

```cpp
// BAD: creates intermediate field (large memory)
volScalarField temp = fvc::grad(p) & U;
volScalarField result = fvc::laplacian(alpha, temp);

// GOOD: chain operations (no intermediate storage)
volScalarField result = fvc::laplacian(alpha, fvc::grad(p) & U);
```

### Common Pitfalls

#### Pitfall 1: Using List for Physical Data

```cpp
// ❌ WRONG: No CFD operations available
List<scalar> T(100, 300.0);
scalar avgT = average(T);  // COMPILATION ERROR!

// ✅ CORRECT: Use Field for physical quantities
scalarField T(100, 300.0);
scalar avgT = average(T);  // Works!
```

#### Pitfall 2: Unnecessary Field Copies

```cpp
// ❌ WRONG: Creates full copy
scalarField newT = oldT;  
newT *= 1.1;  // Modifies copy, not original

// ✅ CORRECT: Use reference to avoid copy
scalarField& newT = oldT;  // Reference
newT *= 1.1;  // Modifies original
```

#### Pitfall 3: Forgetting const References

```cpp
// ❌ WRONG: Pass by value copies entire field
void process(scalarField data) { ... }

// ✅ CORRECT: Const reference for read-only
void process(const scalarField& data) { ... }
```

#### Pitfall 4: Manual Index Instead of forAll

```cpp
// ❌ WRONG: Error-prone, verbose
for (label i = 0; i < U.size(); i++)
{
    U[i] = ...;
}

// ✅ CORRECT: Idiomatic OpenFOAM
forAll(U, i)
{
    U[i] = ...;
}
```

#### Pitfall 5: HashTable Without Checking Existence

```cpp
// ❌ WRONG: Crashes if key doesn't exist
scalar value = props["unknownKey"];

// ✅ CORRECT: Check first
if (props.found("unknownKey"))
{
    scalar value = props["unknownKey"];
}
// Or use lookup with default
scalar value = props.lookup("unknownKey", defaultValue);
```

---

## Quick Reference

| Need | Use | ทำไม |
|------|-----|------|
| Dynamic array | `List<T>` | General purpose |
| Building list | `DynamicList<T>` | Pre-allocated growth |
| Lookup by name | `HashTable<T, word>` | O(1) access |
| Physical data | `Field<T>` | Has CFD operations |
| Pointers | `PtrList<T>` | Polymorphism |
| Smart pointer | `autoPtr<T>`, `tmp<T>` | Memory management |

---

## Key Takeaways | สรุปสำคัญ

1. **Container Selection Matters**: Choose List vs Field based on data type and required operations
   - Physical quantities (T, p, U) → Field
   - General data → List
   
2. **Field is CFD-Optimized**: Field<T> provides mathematical operations and aggregations that List doesn't
   - Built-in: max(), min(), average(), sum()
   - Element-wise arithmetic: +, -, *, /
   - Math functions: sqr(), sqrt(), mag()

3. **Memory Management is Critical**: 
   - Use const references to avoid copies
   - Pre-allocate DynamicList when size is predictable
   - Chain Field operations to minimize temporaries

4. **forAll is Idiomatic**: Use forAll macro instead of manual indexing for cleaner, safer code

5. **HashTable for Named Access**: Use HashTable when O(1) lookup by name is required

6. **PtrList for Polymorphism**: Use PtrList when managing multiple objects of varying types or sizes

---

## 🧠 Concept Check

<details>
<summary><b>1. List vs DynamicList ต่างกันอย่างไร?</b></summary>

| | List | DynamicList |
|-|------|-------------|
| Size | Fixed after creation | **Grows automatically** |
| `append()` | Reallocates every time (slow) | Pre-allocated growth (fast) |
| ใช้เมื่อ | Size known upfront | Building data incrementally |
</details>

<details>
<summary><b>2. Field กับ List ต่างกันอย่างไร?</b></summary>

**Field = List + CFD operations:**
```cpp
// Field has these, List doesn't:
scalar maxT = max(T);
scalar avgT = average(T);
scalarField T2 = sqr(T);
scalarField sum = T1 + T2;
```

**กฎ:** Physical data → Field, Other data → List
</details>

<details>
<summary><b>3. forAll macro ดีกว่า range-for อย่างไร?</b></summary>

**forAll gives index:**
```cpp
forAll(T, cellI)
{
    T[cellI] = p[cellI] / (R * rho[cellI]);  // cellI ใช้กับทุก field
}
```

**range-for ให้ value ไม่มี index:**
```cpp
for (auto& val : T)
{
    val = ???;  // ไม่มี index สำหรับ access p, rho
}
```
</details>

<details>
<summary><b>4. เมื่อไหร่ใช้ HashTable?</b></summary>

**เมื่อต้องการ lookup by name/key:**
```cpp
// Properties from dictionary
HashTable<scalar, word> props;
props.insert("density", 1000);
props.insert("viscosity", 1e-3);

// Later...
scalar rho = props["density"];  // O(1) access, not O(n)
```

**ใช้บ่อยใน:** dictionary lookup, boundary patches by name
</details>

<details>
<summary><b>5. ทำไมต้องใช้ const reference?</b></summary>

**ป้องกันการ copy ข้อมูลจำนวนมหาศาล:**
```cpp
// BAD: Copies 1 million elements
void process(List<scalar> data) { ... }

// GOOD: Just a pointer (8 bytes)
void process(const List<scalar>& data) { ... }
```

**Performance impact:** Copy = O(n) time + O(n) memory, Reference = O(1) time + O(1) memory
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Basic Primitives:** [02_Basic_Primitives.md](02_Basic_Primitives.md)
- **Smart Pointers:** [04_Smart_Pointers.md](04_Smart_Pointers.md)
- **Deep Dive:** [../03_CONTAINERS_MEMORY/00_Overview.md](../03_CONTAINERS_MEMORY/00_Overview.md)