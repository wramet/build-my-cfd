# Factory Pattern

Factory Pattern ใน OpenFOAM

---

## Overview

> **Factory** = Create objects without specifying exact class

---

## 1. Problem Solved

```cpp
// Without Factory - hardcoded selection
turbulenceModel* turb;
if (type == "kEpsilon")
    turb = new kEpsilon(...);
else if (type == "kOmegaSST")
    turb = new kOmegaSST(...);
// ... many more if-else
```

---

## 2. Factory Solution

```cpp
// With Factory - dictionary-driven
autoPtr<turbulenceModel> turb = turbulenceModel::New(dict);
// Automatically creates correct type!
```

---

## 3. Implementation

### Base Class

```cpp
class turbulenceModel
{
public:
    declareRunTimeSelectionTable
    (
        autoPtr, turbulenceModel, dictionary,
        (const dictionary& dict), (dict)
    );

    static autoPtr<turbulenceModel> New(const dictionary& dict);
};
```

### Registration

```cpp
// In kEpsilon.C
addToRunTimeSelectionTable(turbulenceModel, kEpsilon, dictionary);
```

### Factory Method

```cpp
autoPtr<turbulenceModel> turbulenceModel::New(const dictionary& dict)
{
    word type(dict.lookup("type"));
    return dictionaryConstructorTable(type)(dict);
}
```

---

## 4. Benefits

| Benefit | Description |
|---------|-------------|
| **Decoupling** | User code independent of concrete |
| **Extensibility** | Add models without changing user |
| **Configuration** | Dictionary-driven selection |
| **Maintenance** | Central creation point |

---

## 5. Usage

```cpp
// constant/turbulenceProperties
turbulenceModel
{
    type    kOmegaSST;
}

// In solver
autoPtr<turbulenceModel> turb = turbulenceModel::New(dict);
turb->correct();
```

---

## Quick Reference

| Component | Purpose |
|-----------|---------|
| `declareRunTimeSelectionTable` | Create table |
| `addToRunTimeSelectionTable` | Register class |
| `Model::New(dict)` | Factory method |

---

## 🧠 Concept Check

<details>
<summary><b>1. Factory ดีกว่า if-else อย่างไร?</b></summary>

**Open-closed** — add new types without modifying user code
</details>

<details>
<summary><b>2. autoPtr return ทำไม?</b></summary>

**Ownership transfer** — caller owns object
</details>

<details>
<summary><b>3. Registration ทำเมื่อไหร่?</b></summary>

**Static initialization** — at program startup
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Strategy:** [03_Strategy_Pattern.md](03_Strategy_Pattern.md)