# Memory Design Patterns

Design Patterns สำหรับ Memory Management

---

## Overview

> Patterns for **safe, efficient** memory management

---

## 1. RAII (Resource Acquisition Is Initialization)

```cpp
class FieldManager
{
    autoPtr<volScalarField> field_;

public:
    FieldManager(const fvMesh& mesh)
    : field_(new volScalarField(..., mesh))
    {}

    // Automatic cleanup in destructor
    ~FieldManager() = default;  // autoPtr handles it
};
```

---

## 2. Factory with autoPtr

```cpp
class Model
{
public:
    static autoPtr<Model> New(const dictionary& dict)
    {
        word type(dict.lookup("type"));
        return autoPtr<Model>(new ConcreteModel(dict));
    }
};

// Usage: ownership transferred to caller
autoPtr<Model> model = Model::New(dict);
```

---

## 3. tmp for Temporaries

```cpp
tmp<volScalarField> computeField(const volScalarField& T)
{
    return tmp<volScalarField>
    (
        new volScalarField
        (
            IOobject("result", ...),
            sqr(T)
        )
    );
}

// Automatic cleanup
tmp<volScalarField> result = computeField(T);
```

---

## 4. PtrList for Collections

```cpp
PtrList<volScalarField> phases(n);

forAll(phases, i)
{
    phases.set(i, new volScalarField(...));
}

// All cleaned up when PtrList destroyed
```

---

## 5. Object Registry Pattern

```cpp
// Field registers with mesh
volScalarField T(..., mesh);

// Lookup later
const volScalarField& T = mesh.lookupObject<volScalarField>("T");
```

---

## Quick Reference

| Pattern | When |
|---------|------|
| RAII | Resource lifetime |
| Factory + autoPtr | Object creation |
| tmp return | Temporaries |
| PtrList | Polymorphic collections |

---

## 🧠 Concept Check

<details>
<summary><b>1. RAII คืออะไร?</b></summary>

**Tie resource lifetime to object lifetime** — auto cleanup
</details>

<details>
<summary><b>2. Factory return autoPtr ทำไม?</b></summary>

**Transfer ownership** to caller cleanly
</details>

<details>
<summary><b>3. Object registry ช่วยอะไร?</b></summary>

**Centralized lookup** — ไม่ต้อง pass pointers everywhere
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Errors:** [07_Common_Errors_and_Debugging.md](07_Common_Errors_and_Debugging.md)