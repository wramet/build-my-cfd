# Expression Templates Syntax

Syntax ของ Expression Templates

---

## Overview

> Expression templates = **Compile-time optimization** for field operations

---

## 1. Problem

```cpp
// Naive: creates temporaries
volScalarField result = a + b + c;

// Without optimization:
// tmp1 = a + b
// tmp2 = tmp1 + c
// result = tmp2
// 2 temporaries created!
```

---

## 2. Solution: tmp Class

```cpp
// OpenFOAM uses tmp to manage temporaries
tmp<volScalarField> result = fvc::grad(p);

// Returned tmp manages memory
// Automatic cleanup when scope ends
```

---

## 3. Operator Chaining

```cpp
// tmp enables efficient chaining
volScalarField result = a + b + c;

// OpenFOAM optimizes this internally
// Fewer allocations than naive approach
```

---

## 4. fvc Operations Return tmp

```cpp
tmp<volVectorField> gradP = fvc::grad(p);
tmp<volScalarField> divU = fvc::div(U);
tmp<volScalarField> lapT = fvc::laplacian(alpha, T);

// Use result
volScalarField& field = gradP();
```

---

## 5. Best Practices

```cpp
// Good: Keep tmp alive
tmp<volScalarField> tField = fvc::mag(U);
scalar maxU = max(tField()).value();

// Bad: Immediate destruction
fvc::mag(U);  // Result discarded!

// Bad: Dangling reference
const volScalarField& bad = fvc::mag(U)();  // tmp dies!
```

---

## Quick Reference

| Pattern | Result |
|---------|--------|
| `fvc::op(f)` | Returns `tmp<Field>` |
| `tmp()` | Access contained field |
| Chain ops | Optimized internally |

---

## 🧠 Concept Check

<details>
<summary><b>1. Expression templates ทำอะไร?</b></summary>

**Delay evaluation** จนกว่าจะจำเป็น → ลด temporaries
</details>

<details>
<summary><b>2. tmp ช่วยอย่างไร?</b></summary>

**Manages temporary lifetime** → automatic cleanup
</details>

<details>
<summary><b>3. ทำไมต้อง keep tmp alive?</b></summary>

ถ้า tmp destroyed ก่อนใช้ reference → **dangling**
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Mechanics:** [03_Internal_Mechanics.md](03_Internal_Mechanics.md)