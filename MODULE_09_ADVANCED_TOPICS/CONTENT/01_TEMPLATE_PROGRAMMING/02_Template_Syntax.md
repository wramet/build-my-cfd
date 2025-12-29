# Template Syntax

ไวยากรณ์ Template

---

## Overview

> Template syntax = `template<parameters> declaration`

<!-- IMAGE: IMG_09_001 -->
<!-- 
Purpose: เพื่อแสดงหลักการ "Generic Programming" ของ C++ Template. ภาพนี้ต้องสื่อว่า Code ต้นฉบับมีแค่ "แม่พิมพ์" (Template) อันเดียว แต่ Compiler ปั๊มออกมาเป็น Class หลายเวอร์ชัน (Instantiation) เช่น `GeometricField<scalar>`, `GeometricField<vector>`.
Prompt: "C++ Template Instantiation Mechanism. **Input Source:** A Blueprint Scroll marked `template<class T> class Field`. **Processing:** A Compiler Gear Machine interacting with the blueprint. **Output (Generated Code):** Three distinct Instantiated Classes popping out: 1. `Field<Scalar>` (Yellow). 2. `Field<Vector>` (Green). 3. `Field<Tensor>` (Red). **Concept:** 'Write Once, Generate Many'. STYLE: Compiler process conceptual art, crisp code blocks, industrial machine metaphor."
-->
![IMG_09_001: C++ Template Instantiation](IMG_09_001.jpg)

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