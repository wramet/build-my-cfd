# Performance Optimization - Overview

ภาพรวม Performance Optimization

---

## Overview

> OpenFOAM uses **templates** and **smart memory** for performance

---

## 1. Optimization Strategies

| Strategy | Benefit |
|----------|---------|
| **Templates** | Compile-time optimizations |
| **tmp** | Avoid copies |
| **Inlining** | No call overhead |
| **Vectorization** | SIMD operations |

---

## 2. Expression Templates

```cpp
// Efficient field operations
volScalarField result = a + b + c;

// tmp manages temporaries
tmp<volScalarField> gradP = fvc::grad(p);
```

---

## 3. Memory Efficiency

```cpp
// Good: Reuse fields
forAll(result, i)
{
    result[i] = compute(i);
}

// Bad: Create new field each time
result = volScalarField(...);  // Allocation!
```

---

## 4. Parallel Performance

```cpp
// Use global operations
scalar maxVal = gMax(field);
scalar totalSum = gSum(field);
```

---

## 5. Module Contents

| File | Topic |
|------|-------|
| 01_Introduction | Basics |
| 02_Expression_Templates | Syntax |
| 03_Mechanics | How it works |
| 04_Compilation | Machine code |
| 05_Patterns | Trade-offs |
| 06_Errors | Issues |
| 07_Appendices | Extra |

---

## Quick Reference

| Need | Approach |
|------|----------|
| Field ops | Use tmp |
| Inner loops | Inline |
| Parallel | Global ops |
| Memory | Reuse allocations |

---

## 🧠 Concept Check

<details>
<summary><b>1. tmp ช่วย performance อย่างไร?</b></summary>

**Avoids unnecessary copies** และ manages temporaries
</details>

<details>
<summary><b>2. Templates ช่วยอย่างไร?</b></summary>

**Compile-time specialization** → inlining, optimization
</details>

<details>
<summary><b>3. Biggest bottleneck คืออะไร?</b></summary>

**Memory bandwidth** — cache efficiency สำคัญ
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **Introduction:** [01_Introduction.md](01_Introduction.md)
- **Expression Templates:** [02_Expression_Templates_Syntax.md](02_Expression_Templates_Syntax.md)