# Template Metaprogramming

Template Metaprogramming ใน Dimensioned Types — Advanced C++ สำหรับ OpenFOAM

> **ทำไมต้องรู้ Templates?**
> - เข้าใจวิธีที่ **OpenFOAM reuse code** สำหรับ scalar, vector, tensor
> - อ่าน/เขียน **template-based code** ได้
> - สร้าง custom dimensioned types ได้

---

## Overview

> **💡 Templates = Code ที่ทำงานกับ multiple types**
>
> `dimensioned<scalar>`, `dimensioned<vector>`, `dimensioned<tensor>`
> ใช้ logic เดียวกัน แค่ต่าง type inside

---

## 1. Basic Template Structure

```cpp
template<class Type>
class dimensioned
{
    word name_;
    dimensionSet dimensions_;
    Type value_;

public:
    // Constructors
    dimensioned(const word& name, const dimensionSet& ds, const Type& val);

    // Accessors
    const word& name() const;
    const dimensionSet& dimensions() const;
    const Type& value() const;
    Type& value();
};
```

---

## 2. Type Aliases

```cpp
// Scalar types
typedef dimensioned<scalar> dimensionedScalar;

// Vector types
typedef dimensioned<vector> dimensionedVector;

// Tensor types
typedef dimensioned<tensor> dimensionedTensor;
typedef dimensioned<symmTensor> dimensionedSymmTensor;
typedef dimensioned<sphericalTensor> dimensionedSphericalTensor;
```

---

## 3. Operator Overloading

### Arithmetic Operators

```cpp
// Addition (dimensions must match)
template<class Type>
dimensioned<Type> operator+(const dimensioned<Type>& a,
                            const dimensioned<Type>& b)
{
    return dimensioned<Type>
    (
        '(' + a.name() + '+' + b.name() + ')',
        a.dimensions() + b.dimensions(),  // Check match
        a.value() + b.value()
    );
}

// Multiplication (dimensions combine)
template<class Type1, class Type2>
auto operator*(const dimensioned<Type1>& a,
               const dimensioned<Type2>& b)
{
    return dimensioned<decltype(a.value() * b.value())>
    (
        a.name() + '*' + b.name(),
        a.dimensions() * b.dimensions(),  // Combine
        a.value() * b.value()
    );
}
```

---

## 4. Function Templates

```cpp
// Square root
template<class Type>
dimensioned<Type> sqrt(const dimensioned<Type>& ds)
{
    return dimensioned<Type>
    (
        "sqrt(" + ds.name() + ')',
        pow(ds.dimensions(), 0.5),  // dims / 2
        sqrt(ds.value())
    );
}

// Power
template<class Type>
dimensioned<Type> pow(const dimensioned<Type>& ds, scalar p)
{
    return dimensioned<Type>
    (
        "pow(" + ds.name() + ',' + name(p) + ')',
        pow(ds.dimensions(), p),
        pow(ds.value(), p)
    );
}
```

---

## 5. Field Integration

```cpp
// GeometricField uses dimensioned for initialization
template<class Type, template<class> class PatchField, class GeoMesh>
class GeometricField
{
    // Internal field with dimensions
    DimensionedField<Type, GeoMesh> internalField_;
};

// Usage
volScalarField p
(
    IOobject(...),
    mesh,
    dimensionedScalar("p", dimPressure, 0)  // Template instantiation
);
```

---

## 6. Type Traits

```cpp
// Check if type is dimensioned
template<class Type>
struct isDimensioned : std::false_type {};

template<class Type>
struct isDimensioned<dimensioned<Type>> : std::true_type {};
```

---

## 7. SFINAE for Operations

```cpp
// Only enable for matching dimensions
template<class Type>
typename std::enable_if<
    std::is_same<
        typename Type::dimensions_type,
        dimensionSet
    >::value,
    Type
>::type
safeAdd(const Type& a, const Type& b)
{
    return a + b;
}
```

---

## Quick Reference

| Feature | Usage |
|---------|-------|
| Template class | `dimensioned<Type>` |
| Type alias | `dimensionedScalar` |
| Operators | `+`, `-`, `*`, `/` overloaded |
| Functions | `sqrt()`, `pow()` templated |

---

## 🧠 Concept Check

<details>
<summary><b>1. ทำไมใช้ template?</b></summary>

เพื่อ **code reuse** — same logic for scalar, vector, tensor
</details>

<details>
<summary><b>2. Operator overloading ทำอะไร?</b></summary>

ทำให้ `+`, `*` ฯลฯ **check dimensions** และ **combine** อัตโนมัติ
</details>

<details>
<summary><b>3. Type alias ช่วยอะไร?</b></summary>

**Readability** — `dimensionedScalar` ง่ายกว่า `dimensioned<scalar>`
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **Implementation:** [03_Implementation_Mechanisms.md](03_Implementation_Mechanisms.md)
- **ภาพรวม:** [00_Overview.md](00_Overview.md)