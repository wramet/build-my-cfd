# Factory Pattern

Factory Pattern ใน OpenFOAM

---

## Overview

> **Factory** = Create objects without specifying exact class

<!-- IMAGE: IMG_09_004 -->
<!-- 
Purpose: เพื่อเปรียบเทียบความยุ่งเหยิงของการเขียน Code แบบ Hard-Coded (Spaghetti if-else) กับความงามของ Factory Pattern. ภาพนี้ต้องโชว์ 2 สถานการณ์ เพื่อชูจุดเด่นของ "Open-Closed Principle" (เพิ่ม Feature ใหม่โดยไม่ต้องแก้ Code เก่า)
Prompt: "Comparison Diagram: Hard-Coded vs Factory Pattern. **Panel A (The Mess):** Code blocks showing a massive Chain of `if (type == 'A') ... else if (type == 'B') ...`. A stressed developer adding a new case involves cutting the chain. **Panel B (Factory Pattern):** A Clean 'Factory Hub' where small Model Modules (A, B, C, New D) plug in independently. The Factory doesn't change when Module D is plugged in. STYLE: Software architecture comparison, clean vs messy contrast, modular blocks."
-->
![IMG_09_004: Factory Pattern](IMG_09_004.jpg)

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