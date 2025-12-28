# Performance - Internal Mechanics

กลไกภายในของ Performance Optimization

---

## Overview

> OpenFOAM optimizes at **compile-time** and **runtime**

---

## 1. Compile-Time Optimizations

### Template Inlining

```cpp
// Templates can be inlined
template<class Type>
inline Type sqr(const Type& x) { return x * x; }

// Compiler can inline entire expression
scalar y = sqr(a) + sqr(b);
```

### Dead Code Elimination

```cpp
// Compiler removes unreachable code
if constexpr (std::is_scalar<Type>::value)
{
    // Only compiled for scalars
}
```

---

## 2. Runtime Optimizations

### Vectorization

```cpp
// Simple loops can be vectorized
forAll(field, i)
{
    field[i] = a * field[i] + b;  // SIMD possible
}
```

### Cache Efficiency

```cpp
// Contiguous memory access
const scalarField& f = field.primitiveField();
forAll(f, i) { ... }  // Good cache usage
```

---

## 3. tmp Optimization

```cpp
// tmp avoids unnecessary copies
tmp<volScalarField> result = computeField();

// Reference counting delays cleanup
tmp<volScalarField> copy = result;  // No copy, ref count++
```

---

## 4. Parallel Efficiency

```cpp
// Global reductions
scalar maxVal = gMax(field);  // Parallel safe

// Local then reduce
scalar localMax = max(field);
reduce(localMax, maxOp<scalar>());
```

---

## Quick Reference

| Optimization | Level |
|--------------|-------|
| Inlining | Compile |
| Vectorization | Compile |
| Cache locality | Runtime |
| tmp management | Runtime |

---

## Concept Check

<details>
<summary><b>1. Inlining ช่วยอย่างไร?</b></summary>

**Eliminates function call overhead** — code inserted at call site
</details>

<details>
<summary><b>2. Vectorization คืออะไร?</b></summary>

**Process multiple values in one instruction** (SIMD)
</details>

<details>
<summary><b>3. Cache efficiency สำคัญไหม?</b></summary>

**มาก** — memory access เป็น bottleneck หลัก
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Expression Templates:** [02_Expression_Templates_Syntax.md](02_Expression_Templates_Syntax.md)