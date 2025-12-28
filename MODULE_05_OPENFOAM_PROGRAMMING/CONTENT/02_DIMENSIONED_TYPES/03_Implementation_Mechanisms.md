# Implementation Mechanisms

กลไกการทำงานภายในของ Dimensioned Types

---

## Overview

> Dimension checking ทำงานผ่าน **operator overloading** และ **runtime validation**

---

## 1. dimensionSet Class

```cpp
class dimensionSet
{
    scalar exponents_[7];  // [M, L, T, Θ, I, N, J]

public:
    // Constructor
    dimensionSet(scalar M, scalar L, scalar T, 
                 scalar Theta, scalar I, scalar N, scalar J);

    // Operators
    dimensionSet operator*(const dimensionSet& ds) const;
    dimensionSet operator/(const dimensionSet& ds) const;
    bool operator==(const dimensionSet& ds) const;

    // Check
    bool dimensionless() const;
};
```

---

## 2. Dimension Arithmetic

### Multiplication

```cpp
// [M L^-3] * [L T^-1] = [M L^-2 T^-1]
dimensionSet a(1, -3, 0, 0, 0, 0, 0);  // density
dimensionSet b(0, 1, -1, 0, 0, 0, 0);  // velocity
dimensionSet c = a * b;  // [1, -2, -1, 0, 0, 0, 0]
```

### Division

```cpp
// [M L^-1 T^-2] / [M L^-3] = [L² T^-2]
dimensionSet p(1, -1, -2, 0, 0, 0, 0);  // pressure
dimensionSet rho(1, -3, 0, 0, 0, 0, 0);  // density
dimensionSet result = p / rho;  // [0, 2, -2, 0, 0, 0, 0]
```

### Power

```cpp
// [L T^-1]² = [L² T^-2]
dimensionSet U(0, 1, -1, 0, 0, 0, 0);
dimensionSet U2 = pow(U, 2);  // [0, 2, -2, 0, 0, 0, 0]
```

---

## 3. dimensionedType Template

```cpp
template<class Type>
class dimensioned
{
    word name_;
    dimensionSet dimensions_;
    Type value_;

public:
    // Access
    const word& name() const { return name_; }
    const dimensionSet& dimensions() const { return dimensions_; }
    const Type& value() const { return value_; }

    // Operators with dimension checking
    dimensioned operator+(const dimensioned&) const;
    dimensioned operator*(const dimensioned&) const;
};
```

---

## 4. Operator Checking

### Addition/Subtraction

```cpp
dimensioned<scalar> operator+(const dimensioned<scalar>& a,
                              const dimensioned<scalar>& b)
{
    // Dimensions must match!
    if (a.dimensions() != b.dimensions())
    {
        FatalError << "Dimension mismatch in +" << abort(FatalError);
    }
    return dimensioned<scalar>(a.name(), a.dimensions(), 
                               a.value() + b.value());
}
```

### Multiplication

```cpp
dimensioned<scalar> operator*(const dimensioned<scalar>& a,
                              const dimensioned<scalar>& b)
{
    return dimensioned<scalar>(
        a.name() + "*" + b.name(),
        a.dimensions() * b.dimensions(),  // Dimensions multiply!
        a.value() * b.value()
    );
}
```

---

## 5. Checking Control

```cpp
// Global flag (use sparingly!)
bool dimensionedType::checking_ = true;

// Disable
dimensionSet::checking(false);

// Re-enable
dimensionSet::checking(true);
```

---

## 6. Common Type Aliases

```cpp
typedef dimensioned<scalar> dimensionedScalar;
typedef dimensioned<vector> dimensionedVector;
typedef dimensioned<tensor> dimensionedTensor;
typedef dimensioned<symmTensor> dimensionedSymmTensor;
typedef dimensioned<sphericalTensor> dimensionedSphericalTensor;
```

---

## Quick Reference

| Operation | Dimension Effect |
|-----------|------------------|
| a + b | Must match |
| a - b | Must match |
| a * b | Multiply exponents |
| a / b | Subtract exponents |
| pow(a, n) | Multiply exponents by n |
| sqrt(a) | Divide exponents by 2 |

---

## Concept Check

<details>
<summary><b>1. Addition ต้อง dimension เหมือนกันไหม?</b></summary>

**ใช่** — ไม่สามารถบวก pressure + velocity ได้
</details>

<details>
<summary><b>2. Multiplication ทำอะไรกับ dimensions?</b></summary>

**บวก exponents** เช่น [M L^-3] × [L T^-1] = [M L^-2 T^-1]
</details>

<details>
<summary><b>3. sqrt() ทำอะไรกับ dimensions?</b></summary>

**หาร exponents ด้วย 2** เช่น sqrt([L² T^-2]) = [L T^-1]
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Template Metaprogramming:** [04_Template_Metaprogramming.md](04_Template_Metaprogramming.md)
