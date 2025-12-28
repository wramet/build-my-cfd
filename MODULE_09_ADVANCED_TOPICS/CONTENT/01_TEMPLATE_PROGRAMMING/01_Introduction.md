# Template Programming - Introduction

บทนำ Template Programming

---

## Overview

> **Templates** = C++ mechanism for generic programming

---

## 1. What are Templates?

| Concept | Description |
|---------|-------------|
| **Generic code** | Write once, use with any type |
| **Compile-time** | Code generated at compilation |
| **Type-safe** | Full type checking |
| **Zero overhead** | No runtime cost |

---

## 2. Why Templates in OpenFOAM?

```cpp
// Without templates: need separate classes
volScalarField, volVectorField, volTensorField...

// With templates: one class, many types
template<class Type, ...>
class GeometricField;

typedef GeometricField<scalar,...> volScalarField;
typedef GeometricField<vector,...> volVectorField;
```

---

## 3. Basic Example

```cpp
// Function template
template<class Type>
Type maximum(const Type& a, const Type& b)
{
    return (a > b) ? a : b;
}

// Usage
scalar m1 = maximum(3.0, 5.0);      // Works with scalar
vector m2 = maximum(v1, v2);         // Works with vector
```

---

## 4. OpenFOAM Template Classes

| Class | Template Parameters |
|-------|---------------------|
| `List<T>` | Element type |
| `Field<T>` | Value type |
| `GeometricField<T,P,M>` | Type, Patch, Mesh |
| `tmp<T>` | Field type |
| `autoPtr<T>` | Object type |

---

## 5. Module Contents

| File | Topic |
|------|-------|
| 02_Syntax | Template syntax |
| 03_Mechanics | How templates work |
| 04_Instantiation | Specialization |
| 05_Patterns | Design patterns |
| 06_Errors | Common errors |
| 07_Exercise | Practice |

---

## Quick Reference

| Concept | Syntax |
|---------|--------|
| Class template | `template<class T> class C` |
| Function template | `template<class T> T f(T)` |
| Instantiation | `C<int> obj;` |

---

## Concept Check

<details>
<summary><b>1. Template vs Runtime polymorphism?</b></summary>

- **Template**: Compile-time, no overhead
- **Inheritance**: Runtime, virtual call overhead
</details>

<details>
<summary><b>2. ทำไม OpenFOAM ใช้ templates?</b></summary>

**Code reuse** — same Field class for scalar, vector, tensor
</details>

<details>
<summary><b>3. Templates ทำงานเมื่อไหร่?</b></summary>

**Compile-time** — compiler generates code for each type used
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Syntax:** [02_Template_Syntax.md](02_Template_Syntax.md)