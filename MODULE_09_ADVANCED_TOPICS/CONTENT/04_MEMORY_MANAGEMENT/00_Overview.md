# Memory Management - Overview

ภาพรวม Memory Management

---

## Overview

> OpenFOAM uses **smart pointers** for automatic memory management

---

## 1. Smart Pointer Types

| Type | Ownership | Use |
|------|-----------|-----|
| `autoPtr<T>` | Unique | Factory returns |
| `tmp<T>` | Shared | Temporaries |
| `PtrList<T>` | List | Collections |
| `refPtr<T>` | Optional | Ref or pointer |

---

## 2. autoPtr

```cpp
autoPtr<Model> model = Model::New(dict);
model().compute();  // Access via ()
```

---

## 3. tmp

```cpp
tmp<volScalarField> tField = fvc::grad(p);
volScalarField& field = tField();
// Auto-cleanup when tField destroyed
```

---

## 4. PtrList

```cpp
PtrList<volScalarField> fields(n);
fields.set(0, new volScalarField(...));
```

---

## 5. Module Contents

| File | Topic |
|------|-------|
| 01_Introduction | Basics |
| 02_Syntax | Usage patterns |
| 03_Mechanics | How it works |
| 04_Math | Theory |
| 05_Implementation | Details |
| 06_Patterns | Design patterns |
| 07_Errors | Common issues |

---

## Quick Reference

| Need | Use |
|------|-----|
| Factory return | `autoPtr<T>` |
| Temporary | `tmp<T>` |
| Pointer list | `PtrList<T>` |
| Check valid | `.valid()` |

---

## 🧠 Concept Check

<details>
<summary><b>1. autoPtr vs tmp?</b></summary>

- **autoPtr**: Unique, move only
- **tmp**: Reference counted
</details>

<details>
<summary><b>2. ทำไม OpenFOAM ใช้ smart pointers?</b></summary>

**Automatic cleanup** — ป้องกัน memory leaks
</details>

<details>
<summary><b>3. tmp cleanup เมื่อไหร่?</b></summary>

เมื่อ **all references destroyed**
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **Introduction:** [01_Introduction.md](01_Introduction.md)
- **Syntax:** [02_Memory_Syntax_and_Design.md](02_Memory_Syntax_and_Design.md)