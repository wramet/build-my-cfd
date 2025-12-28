# Memory Management - Syntax and Design

Syntax และ Design ของ Memory Management

---

## Overview

> OpenFOAM uses **smart pointers** for automatic memory management

---

## 1. autoPtr

```cpp
// Unique ownership
autoPtr<volScalarField> fieldPtr
(
    new volScalarField(IOobject(...), mesh)
);

// Access
volScalarField& field = fieldPtr();

// Check validity
if (fieldPtr.valid()) { ... }

// Transfer ownership
autoPtr<volScalarField> newOwner = std::move(fieldPtr);
```

---

## 2. tmp

```cpp
// Reference-counted temporary
tmp<volScalarField> tField = fvc::grad(p);

// Access
volScalarField& field = tField();

// Store reference (keeps alive)
tmp<volScalarField> stored = tField;

// Auto-cleanup when all references gone
```

---

## 3. PtrList

```cpp
// List of owned pointers
PtrList<volScalarField> fields(n);

// Set elements
forAll(fields, i)
{
    fields.set(i, new volScalarField(...));
}

// Access
volScalarField& f = fields[i];

// Check if set
if (fields.set(i)) { ... }
```

---

## 4. Design Patterns

| Smart Pointer | Ownership | Use Case |
|---------------|-----------|----------|
| `autoPtr` | Unique | Factory returns |
| `tmp` | Shared | Temporaries |
| `PtrList` | List | Collections |
| `refPtr` | Optional | Reference/pointer |

---

## 5. Best Practices

```cpp
// Good: Use smart pointers
autoPtr<Model> model = Model::New(dict);

// Bad: Raw pointers
Model* model = new Model(dict);  // Who deletes?

// Good: tmp for temporaries
tmp<volVectorField> gradP = fvc::grad(p);

// Bad: Store reference to temporary
const volVectorField& bad = fvc::grad(p)();  // Dangling!
```

---

## Quick Reference

| Need | Use |
|------|-----|
| Unique ownership | `autoPtr<T>` |
| Shared temporary | `tmp<T>` |
| Optional ref | `refPtr<T>` |
| Pointer list | `PtrList<T>` |

---

## Concept Check

<details>
<summary><b>1. autoPtr vs tmp?</b></summary>

- **autoPtr**: Unique, move only
- **tmp**: Reference counted, can share
</details>

<details>
<summary><b>2. tmp ช่วยอะไร?</b></summary>

**Automatic cleanup** ของ temporary fields
</details>

<details>
<summary><b>3. ทำไม fvc:: return tmp?</b></summary>

เพราะสร้าง **temporary field** — tmp manages lifetime
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Mechanics:** [03_Internal_Mechanics.md](03_Internal_Mechanics.md)