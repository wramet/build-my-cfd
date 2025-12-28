# Architecture Design Patterns

Design Patterns สำหรับ Extensibility

---

## Overview

> OpenFOAM architecture uses **patterns for extensibility**

---

## 1. Plugin Pattern

```cpp
// Load library at runtime
libs ("libmyModels.so");

// Models in library auto-register
```

---

## 2. Registry Pattern

```cpp
// Central storage
class objectRegistry
{
    HashTable<regIOobject*> objects_;
public:
    template<class Type>
    const Type& lookupObject(const word& name) const;
};

// Usage
const volScalarField& T = mesh.lookupObject<volScalarField>("T");
```

---

## 3. Factory + RTS

```cpp
// Factory method uses RTS
autoPtr<Model> Model::New(const dictionary& dict)
{
    word type(dict.lookup("type"));
    return dictionaryConstructorTable(type)(dict);
}
```

---

## 4. Function Object Pattern

```cpp
// Post-processing hooks
class functionObject
{
public:
    virtual bool execute() = 0;
    virtual bool write() = 0;
};

// Registered in controlDict
functions { ... }
```

---

## 5. Application to OpenFOAM

| Pattern | Use |
|---------|-----|
| Plugin | Dynamic libraries |
| Registry | Object lookup |
| Factory | Model creation |
| Observer | Function objects |

---

## Quick Reference

| Pattern | OpenFOAM Example |
|---------|------------------|
| Plugin | `libs (...)` |
| Registry | `mesh.lookupObject()` |
| Factory | `Model::New()` |
| Observer | `functionObjects` |

---

## Concept Check

<details>
<summary><b>1. Plugin pattern ดีอย่างไร?</b></summary>

**Add features without recompiling** solver
</details>

<details>
<summary><b>2. Registry pattern ช่วยอะไร?</b></summary>

**Centralized lookup** — ไม่ต้อง pass objects everywhere
</details>

<details>
<summary><b>3. Function objects = Observer?</b></summary>

**ใช่** — observe solver events and react
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **RTS:** [02_Runtime_Selection_Tables.md](02_Runtime_Selection_Tables.md)