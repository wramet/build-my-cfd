# Container System

ระบบ Container ใน OpenFOAM

---

## Overview

> OpenFOAM containers = STL-like with CFD optimizations

---

## 1. List Types

### List<T>

```cpp
// Fixed size array
List<scalar> values(100, 0.0);

// Access
values[0] = 1.0;
scalar first = values.first();
scalar last = values.last();

// Size
label n = values.size();
values.resize(200);
```

### DynamicList<T>

```cpp
// Growable list
DynamicList<label> indices;

// Add elements
indices.append(5);
indices.append(10);

// Pre-allocate for efficiency
DynamicList<label> big;
big.reserve(1000);
```

### FixedList<T, N>

```cpp
// Compile-time fixed size
FixedList<scalar, 3> rgb;
rgb[0] = 1.0;  // R
rgb[1] = 0.5;  // G
rgb[2] = 0.0;  // B
```

---

## 2. HashTable

```cpp
// String-keyed hash
HashTable<scalar, word> props;

// Insert
props.insert("density", 1000);
props["viscosity"] = 1e-6;

// Lookup
scalar rho = props["density"];

// Check existence
if (props.found("temperature")) { ... }

// Iterate
forAllConstIters(props, iter)
{
    Info << iter.key() << ": " << iter.val() << endl;
}
```

---

## 3. Field<T>

```cpp
// CFD-optimized array with operations
scalarField T(100, 300.0);
vectorField U(100, vector::zero);

// Math operations
scalarField T2 = sqr(T);
scalar maxT = max(T);
scalar avgT = average(T);
scalar sumT = sum(T);

// Vector operations
scalarField magU = mag(U);
vectorField normalized = U / (mag(U) + SMALL);
```

---

## 4. forAll Macro

```cpp
// Iterate with index
forAll(field, i)
{
    field[i] = compute(i);
}

// Equivalent to:
for (label i = 0; i < field.size(); i++) { ... }

// Reverse iteration
forAllReverse(field, i) { ... }
```

---

## 5. SubList and SubField

```cpp
// View into existing data (no copy)
List<scalar> data(100);
SubList<scalar> sub(data, 20, 10);  // 20 elements starting at 10

// SubField for Field
scalarField full(100);
SubField<scalar> partial(full, 50);  // First 50
```

---

## 6. Sorting

```cpp
List<scalar> values = {...};

// Sort in place
sort(values);

// Sort with indices
labelList order;
sortedOrder(values, order);
```

---

## Quick Reference

| Container | Use |
|-----------|-----|
| `List<T>` | Fixed array |
| `DynamicList<T>` | Growable |
| `FixedList<T,N>` | Compile-time size |
| `Field<T>` | CFD operations |
| `HashTable<T,K>` | Key-value |
| `SubList<T>` | View (no copy) |

---

## Concept Check

<details>
<summary><b>1. Field vs List ต่างกันอย่างไร?</b></summary>

**Field** มี CFD operations: `max()`, `min()`, `average()`, `sum()`, `mag()`
</details>

<details>
<summary><b>2. SubList ดีอย่างไร?</b></summary>

**No copy** — แค่ view เข้าไปใน data เดิม, memory efficient
</details>

<details>
<summary><b>3. forAll ดีกว่า for loop อย่างไร?</b></summary>

**Cleaner syntax** และ **consistent with OpenFOAM style**
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Memory Management:** [02_Memory_Management_Fundamentals.md](02_Memory_Management_Fundamentals.md)
