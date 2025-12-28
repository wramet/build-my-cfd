# Expression Templates

Expression Templates ใน OpenFOAM

---

## Overview

> **Expression templates** = Compile-time optimization for field operations

---

## 1. The Problem

### Naive Implementation

```cpp
// A + B + C without optimization:
// 1. tmp1 = A + B  (allocate, loop)
// 2. tmp2 = tmp1 + C  (allocate, loop)
// 3. result = tmp2

// Creates unnecessary temporaries!
```

---

## 2. OpenFOAM Solution

### tmp Class

```cpp
// tmp holds either:
// - Pointer to new object (owns)
// - Reference to existing (doesn't own)

tmp<volScalarField> result = fvc::grad(p);
```

### Lazy Evaluation

Operations return `tmp` that can be:
- Used immediately (evaluated)
- Passed to other operations (delayed)

---

## 3. Efficient Chaining

```cpp
// Efficient: single allocation for result
volScalarField result = a + b + c;

// OpenFOAM handles temporaries internally
```

---

## 4. tmp Pattern

```cpp
// Function returning tmp
tmp<volScalarField> computeField()
{
    return tmp<volScalarField>
    (
        new volScalarField(...)
    );
}

// Use result
tmp<volScalarField> tField = computeField();
volScalarField& field = tField();

// Memory freed when tField goes out of scope
```

---

## 5. fvc Operations

All `fvc::` operations return `tmp`:

```cpp
tmp<volVectorField> gradP = fvc::grad(p);
tmp<volScalarField> divPhi = fvc::div(phi);
tmp<volScalarField> lapT = fvc::laplacian(alpha, T);
```

---

## 6. Avoiding Copies

```cpp
// Bad: forces copy
volScalarField result = fvc::grad(p).component(0);

// Good: use tmp
tmp<volVectorField> gradP = fvc::grad(p);
volScalarField result = gradP().component(0);
```

---

## 7. Memory Efficiency

| Pattern | Temporaries |
|---------|-------------|
| `a + b + c` | Optimized |
| `tmp = f(); use(tmp())` | Single allocation |
| Keep tmp alive | No dangling refs |

---

## Quick Reference

| Pattern | Usage |
|---------|-------|
| Return tmp | `return tmp<T>(new T(...))` |
| Use tmp | `tmp<T> t = f(); t()` |
| Chain ops | `a + b + c` (automatic) |

---

## 🧠 Concept Check

<details>
<summary><b>1. tmp ช่วยอะไร?</b></summary>

**Automatic memory management** และ **avoid unnecessary copies**
</details>

<details>
<summary><b>2. fvc:: return อะไร?</b></summary>

**tmp<Field>** — temporary ที่ manage memory อัตโนมัติ
</details>

<details>
<summary><b>3. expression templates ทำอะไร?</b></summary>

**Delay evaluation** จนกว่าจะจำเป็น → ลด temporaries
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Operators:** [03_Operator_Overloading.md](03_Operator_Overloading.md)