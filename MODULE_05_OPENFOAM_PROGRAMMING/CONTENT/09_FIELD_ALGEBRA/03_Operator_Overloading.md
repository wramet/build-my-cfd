# Operator Overloading

Operator Overloading ใน Field Algebra

---

## Overview

> OpenFOAM overloads C++ operators for **natural mathematical syntax**

---

## 1. Arithmetic Operators

### Basic Math

```cpp
volScalarField a, b, c;

c = a + b;   // Addition
c = a - b;   // Subtraction
c = a * b;   // Multiplication
c = a / b;   // Division
```

### With Scalars

```cpp
c = 2.0 * a;        // Scalar multiplication
c = a / 2.0;        // Scalar division
c = a + dimensionedScalar("c", a.dimensions(), 1.0);
```

---

## 2. Vector/Tensor Operators

### Inner Product (&)

```cpp
volVectorField U, V;
volScalarField dot = U & V;  // Dot product

volTensorField T;
volVectorField result = T & U;  // Tensor-vector product
```

### Outer Product (*)

```cpp
volVectorField U, V;
volTensorField outer = U * V;  // Outer product
```

### Cross Product (^)

```cpp
volVectorField cross = U ^ V;  // Cross product
```

---

## 3. Special Operators

| Operator | Meaning |
|----------|---------|
| `&` | Inner/dot product |
| `*` | Outer product or scalar mult |
| `^` | Cross product |
| `&&` | Double contraction |

---

## 4. Comparison Operators

```cpp
// Element-wise comparison
volScalarField result = pos(T - Tcrit);  // 1 where T > Tcrit
volScalarField result = neg(T - Tcrit);  // 1 where T < Tcrit
```

---

## 5. Assignment Operators

```cpp
T += source;      // Add in place
T -= sink;        // Subtract in place
T *= factor;      // Multiply in place
T /= divisor;     // Divide in place
```

---

## 6. Boundary Assignment

```cpp
// Set entire boundary
T.boundaryFieldRef()[patchI] == fixedValue;

// Note: == is special assignment for boundary!
```

---

## 7. Dimension Checking

All operators check dimensions:

```cpp
// Valid
volScalarField dynP = 0.5 * rho * magSqr(U);

// Invalid (compile/runtime error)
// volScalarField bad = p + U;  // Dimension mismatch
```

---

## Quick Reference

| Operator | Usage |
|----------|-------|
| `+`, `-` | Add/subtract |
| `*` | Multiply (or outer) |
| `/` | Divide |
| `&` | Inner product |
| `^` | Cross product |
| `&&` | Double contraction |

---

## Concept Check

<details>
<summary><b>1. & vs * ต่างกันอย่างไร?</b></summary>

- **&**: Inner product (reduces rank)
- *****: Outer product (increases rank)
</details>

<details>
<summary><b>2. == ที่ boundary ทำอะไร?</b></summary>

**Special assignment** — set boundary values
</details>

<details>
<summary><b>3. operators check dimensions ไหม?</b></summary>

**ใช่** — dimension mismatch จะ error
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Arithmetic:** [02_Arithmetic_Operations.md](02_Arithmetic_Operations.md)