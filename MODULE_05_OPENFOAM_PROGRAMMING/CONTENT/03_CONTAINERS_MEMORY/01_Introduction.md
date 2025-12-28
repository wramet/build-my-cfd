# Containers & Memory - Introduction

บทนำ Containers และ Memory Management

---

## Overview

> OpenFOAM containers = **Efficient data structures** for CFD

---

## 1. Why Custom Containers?

| Need | Solution |
|------|----------|
| CFD-specific ops | `Field<T>` with `max()`, `sum()` |
| Large data | Memory-efficient storage |
| Parallelism | Designed for decomposition |
| Safety | Smart pointers |

---

## 2. Container Categories

### Arrays

| Type | Description |
|------|-------------|
| `List<T>` | Dynamic array |
| `DynamicList<T>` | Growable list |
| `FixedList<T,N>` | Fixed size |
| `Field<T>` | CFD operations |

### Maps

| Type | Description |
|------|-------------|
| `HashTable<T,Key>` | Hash map |
| `Map<T>` | Ordered map |

### Smart Pointers

| Type | Description |
|------|-------------|
| `autoPtr<T>` | Unique ownership |
| `tmp<T>` | Reference counted |
| `PtrList<T>` | Pointer list |

---

## 3. Basic Usage

### List

```cpp
List<scalar> values(100, 0.0);
values[0] = 1.0;
values.append(999.0);
```

### Field

```cpp
scalarField T(100, 300.0);
scalar maxT = max(T);
scalar avgT = average(T);
```

### HashTable

```cpp
HashTable<scalar, word> props;
props.insert("density", 1000);
scalar rho = props["density"];
```

---

## 4. Memory Management

### autoPtr (Unique)

```cpp
autoPtr<Model> model(new Model(...));
Model& ref = model();
```

### tmp (Shared)

```cpp
tmp<volScalarField> tField = fvc::grad(p);
volScalarField& field = tField();
```

---

## 5. Module Contents

| File | Topic |
|------|-------|
| 02_Memory_Management | autoPtr, tmp |
| 03_Container_System | List, Field, Hash |
| 04_Integration | Best practices |
| 05_Summary | Exercises |

---

## Quick Reference

| Need | Use |
|------|-----|
| Array | `List<T>` |
| CFD array | `Field<T>` |
| Key-value | `HashTable<T,K>` |
| Unique ptr | `autoPtr<T>` |
| Temporary | `tmp<T>` |

---

## Concept Check

<details>
<summary><b>1. ทำไมไม่ใช้ std::vector?</b></summary>

OpenFOAM containers มี **CFD-specific operations** และ **parallel support**
</details>

<details>
<summary><b>2. Field ดีกว่า List อย่างไร?</b></summary>

**Field** มี `max()`, `min()`, `average()`, `sum()` built-in
</details>

<details>
<summary><b>3. autoPtr vs tmp ใช้เมื่อไหร่?</b></summary>

- **autoPtr**: Factory returns, unique ownership
- **tmp**: Temporary calculations (fvc::)
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Memory Management:** [02_Memory_Management_Fundamentals.md](02_Memory_Management_Fundamentals.md)