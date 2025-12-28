# Template Syntax

ไวยากรณ์ Template

---

## Overview

> Template syntax = `template<parameters> declaration`

---

## 1. Class Template

```cpp
template<class Type>
class Container
{
    Type value_;
    
public:
    Container(const Type& val) : value_(val) {}
    const Type& value() const { return value_; }
    void setValue(const Type& val) { value_ = val; }
};

// Usage
Container<scalar> s(3.14);
Container<vector> v(vector(1, 2, 3));
```

---

## 2. Function Template

```cpp
template<class Type>
Type maximum(const Type& a, const Type& b)
{
    return (a > b) ? a : b;
}

// Usage (type deduction)
scalar m = maximum(3.0, 5.0);

// Explicit type
scalar m = maximum<scalar>(3.0, 5.0);
```

---

## 3. Multiple Parameters

```cpp
template<class Type, class GeoMesh>
class DimensionedField
{
    Type* dataPtr_;
    const GeoMesh::Mesh& mesh_;
};

// Non-type parameters
template<class Type, int N>
class FixedList
{
    Type data_[N];
};
```

---

## 4. Template Template Parameters

```cpp
template<class Type, template<class> class PatchField, class GeoMesh>
class GeometricField
{
    // PatchField is itself a template
};
```

---

## 5. Default Parameters

```cpp
template<class Type = scalar, class Allocator = std::allocator<Type>>
class List
{
    // ...
};

// Usage
List<> defaultList;           // List<scalar, std::allocator<scalar>>
List<vector> vectorList;      // List<vector, std::allocator<vector>>
```

---

## 6. Member Function Templates

```cpp
class Converter
{
public:
    template<class Type>
    Type convert(const scalar& val)
    {
        return Type(val);
    }
};
```

---

## 7. Type Aliases

```cpp
// typedef
typedef GeometricField<scalar, fvPatchField, volMesh> volScalarField;

// using (modern C++)
using volVectorField = GeometricField<vector, fvPatchField, volMesh>;
```

---

## Quick Reference

| Syntax | Use |
|--------|-----|
| `template<class T>` | Single type parameter |
| `template<class T, class U>` | Multiple types |
| `template<class T, int N>` | Type + non-type |
| `template<class T = int>` | Default parameter |

---

## 🧠 Concept Check

<details>
<summary><b>1. class vs typename in template?</b></summary>

**Same meaning** สำหรับ template parameters
</details>

<details>
<summary><b>2. Non-type parameters ใช้อะไรได้?</b></summary>

**Integral types**, enums, pointers, references
</details>

<details>
<summary><b>3. Template template parameter ใช้เมื่อไหร่?</b></summary>

เมื่อ parameter เป็น **template itself** เช่น container type
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Mechanics:** [03_Internal_Mechanics.md](03_Internal_Mechanics.md)