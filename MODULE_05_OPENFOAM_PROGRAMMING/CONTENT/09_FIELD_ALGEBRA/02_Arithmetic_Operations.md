# Arithmetic Operations

การดำเนินการทางคณิตศาสตร์บน Fields

---

## Overview

> OpenFOAM provides **element-wise** arithmetic on entire fields

---

## 1. Basic Arithmetic

```cpp
volScalarField a, b, c;

// Addition
c = a + b;

// Subtraction
c = a - b;

// Multiplication
c = a * b;

// Division
c = a / b;
```

---

## 2. With Scalars

```cpp
// Scalar multiplication
c = 2.0 * a;
c = a * 2.0;

// Division by scalar
c = a / 2.0;

// With dimensioned scalar
dimensionedScalar offset("offset", a.dimensions(), 1.0);
c = a + offset;
```

---

## 3. Mathematical Functions

| Function | Description |
|----------|-------------|
| `sqr(a)` | a² |
| `sqrt(a)` | √a |
| `mag(v)` | |v| |
| `magSqr(v)` | |v|² |
| `sin(a)`, `cos(a)` | Trig functions |
| `exp(a)`, `log(a)` | Exponential |
| `pow(a, n)` | aⁿ |

```cpp
volScalarField T2 = sqr(T);
volScalarField speed = mag(U);
volScalarField kinetic = 0.5 * rho * magSqr(U);
```

---

## 4. Vector Operations

```cpp
// Magnitude
volScalarField speed = mag(U);

// Component access
volScalarField Ux = U.component(0);
volScalarField Uy = U.component(1);
volScalarField Uz = U.component(2);

// Dot product
volScalarField dot = U1 & U2;

// Cross product
volVectorField cross = U1 ^ U2;
```

---

## 5. Tensor Operations

```cpp
volTensorField gradU = fvc::grad(U);

// Trace
volScalarField trGradU = tr(gradU);

// Symmetric part
volSymmTensorField S = symm(gradU);

// Skew-symmetric part
volTensorField W = skew(gradU);

// Deviatoric
volSymmTensorField devS = dev(S);
```

---

## 6. Statistics

```cpp
scalar maxT = max(T).value();
scalar minT = min(T).value();
scalar avgT = average(T).value();
scalar sumT = gSum(T);  // Global sum (parallel)
```

---

## Quick Reference

| Operation | Code |
|-----------|------|
| Square | `sqr(a)` |
| Magnitude | `mag(v)` |
| Dot product | `a & b` |
| Cross product | `a ^ b` |
| Component | `v.component(i)` |
| Maximum | `max(f).value()` |

---

## 🧠 Concept Check

<details>
<summary><b>1. sqr vs pow(a,2)?</b></summary>

**sqr** เร็วกว่า — specific optimization for squaring
</details>

<details>
<summary><b>2. sum vs gSum?</b></summary>

- **sum**: Local processor
- **gSum**: Global (parallel)
</details>

<details>
<summary><b>3. symm(gradU) คืออะไร?</b></summary>

**Symmetric part** = ½(gradU + gradUᵀ) = strain rate tensor
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Operators:** [03_Operator_Overloading.md](03_Operator_Overloading.md)