# OpenFOAM Containers

คอนเทนเนอร์ใน OpenFOAM

---

## Overview

> OpenFOAM containers = STL-like but optimized for CFD

---

## 1. List Types

| Container | Description | Use |
|-----------|-------------|-----|
| `List<T>` | Dynamic array | General |
| `DynamicList<T>` | Growable list | Building |
| `SortedList<T>` | Always sorted | Lookup |
| `FixedList<T, N>` | Fixed size | Small data |

### List Example

```cpp
// Create and initialize
List<scalar> values(100, 0.0);

// Access
values[0] = 1.0;
scalar first = values.first();
scalar last = values.last();

// Size
label n = values.size();

// Append
values.append(999.0);
```

---

## 2. HashTable

```cpp
// String-keyed hash
HashTable<scalar, word> props;
props.insert("density", 1000);
props.insert("viscosity", 1e-3);

// Access
scalar rho = props["density"];

// Check existence
if (props.found("density")) { ... }
```

---

## 3. Field Types

### Basic Field

```cpp
// Scalar field
scalarField T(100, 300.0);

// Vector field
vectorField U(100, vector::zero);

// Operations
scalarField T2 = sqr(T);
scalar maxT = max(T);
scalar avgT = average(T);
```

### forAll Macro

```cpp
forAll(T, cellI)
{
    T[cellI] = computeT(cellI);
}

// Equivalent to:
for (label cellI = 0; cellI < T.size(); cellI++) { ... }
```

---

## 4. PtrList

```cpp
// List of pointers (polymorphic)
PtrList<volScalarField> fields(3);

forAll(fields, i)
{
    fields.set(i, new volScalarField(...));
}

// Access
volScalarField& f = fields[0];
```

---

## 5. autoPtr and tmp

### autoPtr (Unique ownership)

```cpp
autoPtr<volScalarField> fieldPtr(new volScalarField(...));

// Access
volScalarField& field = fieldPtr();

// Transfer ownership
autoPtr<volScalarField> newOwner = fieldPtr.clone();
```

### tmp (Reference counted)

```cpp
// Return temporary
tmp<volScalarField> result = fvc::grad(p);

// Use result
volVectorField gradP = result();

// Memory freed when tmp destroyed
```

---

## 6. Common Operations

| Operation | Description |
|-----------|-------------|
| `max(field)` | Maximum value |
| `min(field)` | Minimum value |
| `sum(field)` | Sum of all elements |
| `average(field)` | Average |
| `mag(field)` | Magnitude |
| `sqr(field)` | Square |
| `sqrt(field)` | Square root |

---

## 7. Memory Tips

### Avoid Copies

```cpp
// Bad: creates copy
List<scalar> copy = original;

// Good: use reference
const List<scalar>& ref = original;
```

### Pre-allocate

```cpp
// Bad: grows repeatedly
DynamicList<scalar> dyn;
forAll(source, i) { dyn.append(source[i]); }

// Good: reserve space
DynamicList<scalar> dyn(expectedSize);
```

---

## Quick Reference

| Need | Use |
|------|-----|
| Dynamic array | `List<T>` |
| Growable list | `DynamicList<T>` |
| Key-value | `HashTable<T, Key>` |
| Pointer list | `PtrList<T>` |
| Smart pointer | `autoPtr<T>` |
| Temporary | `tmp<T>` |

---

## Concept Check

<details>
<summary><b>1. List vs DynamicList ต่างกันอย่างไร?</b></summary>

- **List**: Fixed size after creation
- **DynamicList**: Can grow with `append()`
</details>

<details>
<summary><b>2. autoPtr vs tmp ต่างกันอย่างไร?</b></summary>

- **autoPtr**: Unique ownership (move only)
- **tmp**: Reference counted (can share)
</details>

<details>
<summary><b>3. forAll macro ดีกว่า range-for อย่างไร?</b></summary>

**forAll** ให้ index `cellI` สำหรับ access ค่าอื่นๆ ที่ใช้ same indexing
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Basic Primitives:** [02_Basic_Primitives.md](02_Basic_Primitives.md)