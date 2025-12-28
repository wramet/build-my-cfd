# Instantiation and Specialization

Template Instantiation และ Specialization

---

## Overview

> **Instantiation** = สร้าง concrete code จาก template
> **Specialization** = custom implementation สำหรับ specific types

---

## 1. Implicit Instantiation

```cpp
template<class Type>
Type maximum(const Type& a, const Type& b)
{
    return (a > b) ? a : b;
}

// Compiler generates maximum<scalar> automatically
scalar m = maximum(3.0, 5.0);
```

---

## 2. Explicit Instantiation

```cpp
// Force instantiation (in .C file)
template class List<scalar>;
template class List<vector>;
template scalar maximum(const scalar&, const scalar&);
```

---

## 3. Full Specialization

```cpp
// General template
template<class Type>
void print(const Type& val)
{
    Info << val << endl;
}

// Specialization for vector
template<>
void print<vector>(const vector& val)
{
    Info << "(" << val.x() << ", " << val.y() << ", " << val.z() << ")" << endl;
}
```

---

## 4. Partial Specialization

```cpp
// General
template<class T1, class T2>
class Pair
{
    T1 first_;
    T2 second_;
};

// Partial: both same type
template<class T>
class Pair<T, T>
{
    T first_;
    T second_;
    // Can add special methods...
};
```

---

## 5. Class Member Specialization

```cpp
template<class Type>
class Container
{
public:
    void process();  // General declaration
};

// Specialization of member only
template<>
void Container<scalar>::process()
{
    // Special implementation for scalar
}
```

---

## 6. OpenFOAM Examples

```cpp
// Explicit instantiations in source files
template class GeometricField<scalar, fvPatchField, volMesh>;
template class GeometricField<vector, fvPatchField, volMesh>;
template class GeometricField<tensor, fvPatchField, volMesh>;
```

---

## Quick Reference

| Type | Syntax |
|------|--------|
| Implicit | Automatic from usage |
| Explicit | `template class C<T>;` |
| Full spec | `template<> class C<T>` |
| Partial spec | `template<class T> class C<T, T>` |

---

## Concept Check

<details>
<summary><b>1. Instantiation เกิดเมื่อไหร่?</b></summary>

**Compile-time** เมื่อ template ถูกใช้กับ concrete type
</details>

<details>
<summary><b>2. Full vs Partial specialization?</b></summary>

- **Full**: All parameters specified
- **Partial**: Some parameters remain generic
</details>

<details>
<summary><b>3. ทำไมต้อง explicit instantiation?</b></summary>

**Reduce compile time** และ **control which types are generated**
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Syntax:** [02_Template_Syntax.md](02_Template_Syntax.md)