# OpenFOAM Containers

คอนเทนเนอร์ใน OpenFOAM — Data structures สำหรับ CFD

> **ทำไม Containers สำคัญ?**
> - **Fields อยู่ใน containers** — List<scalar>, Field<vector>
> - เลือกผิด container = performance ย่ำแย่
> - OpenFOAM containers มี CFD operations ที่ STL ไม่มี

---

## Overview

> **💡 ความแตกต่างจาก STL:**
> - OpenFOAM containers = **STL + CFD features**
> - `Field<T>` มี `max()`, `min()`, `average()`, `sum()`
> - I/O compatible กับ OpenFOAM format

---

## 1. List Types

| Container | ลักษณะ | ใช้เมื่อ |
|-----------|-------|---------|
| `List<T>` | Dynamic array | General purpose |
| `DynamicList<T>` | Auto-grow | Building up data |
| `SortedList<T>` | Always sorted | Fast lookup |
| `FixedList<T, N>` | Fixed size | Small, known size |

### List Example

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

### DynamicList — When Size Unknown

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

---

## 3. Field Types — The Heart of OpenFOAM

> **ทำไม Field สำคัญที่สุด?**
> - **volScalarField, volVectorField สืบทอดจาก Field**
> - Field = List + mathematical operations + CFD functions

### Basic Field Operations

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

### Field Arithmetic

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

### forAll Macro

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

---

## 5. List vs Field — When to Use Which

| | List<scalar> | scalarField |
|-|--------------|-------------|
| `max()` | ❌ | ✅ |
| `min()` | ❌ | ✅ |
| `average()` | ❌ | ✅ |
| `sum()` | ❌ | ✅ |
| Math operations | ❌ | ✅ (+, -, *, /, sqr, sqrt) |
| General data | ✅ | ✅ |
| CFD data | ❌ (use Field) | ✅ |

**กฎ:** ถ้าข้อมูลเป็น physical quantity (T, p, U) → ใช้ Field

---

## 6. Common Operations Summary

| Operation | Description | Example |
|-----------|-------------|---------|
| `max(field)` | Maximum value | `scalar Tmax = max(T)` |
| `min(field)` | Minimum value | `scalar Tmin = min(T)` |
| `sum(field)` | Sum of all elements | `scalar total = sum(m)` |
| `average(field)` | Simple average | `scalar Tavg = average(T)` |
| `mag(field)` | Magnitude | `scalarField speed = mag(U)` |
| `sqr(field)` | Square | `scalarField T2 = sqr(T)` |
| `sqrt(field)` | Square root | `scalarField rootK = sqrt(k)` |

---

## 7. Memory Tips

### ❌ Avoid Unnecessary Copies

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

### ✅ Pre-allocate for DynamicList

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

### ✅ Use tmp for Large Temporaries

```cpp
// BAD: creates intermediate field (large memory)
volScalarField temp = fvc::grad(p) & U;
volScalarField result = fvc::laplacian(alpha, temp);

// GOOD: chain operations (no intermediate storage)
volScalarField result = fvc::laplacian(alpha, fvc::grad(p) & U);
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

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Basic Primitives:** [02_Basic_Primitives.md](02_Basic_Primitives.md)
- **Smart Pointers:** [04_Smart_Pointers.md](04_Smart_Pointers.md)
- **Deep Dive:** [../03_CONTAINERS_MEMORY/00_Overview.md](../03_CONTAINERS_MEMORY/00_Overview.md)