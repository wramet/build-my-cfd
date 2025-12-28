# Model Development Rationale

หลักการพัฒนา Model

---

## Overview

> Build on OpenFOAM patterns for **maintainable** models

---

## 1. Design Goals

| Goal | How |
|------|-----|
| **Reusable** | Use templates, inheritance |
| **Extensible** | Use RTS |
| **Testable** | Modular design |
| **Maintainable** | Follow OpenFOAM style |

---

## 2. Inheritance Strategy

```cpp
// Inherit from appropriate base
class myModel : public turbulenceModel
{
    // Use base class infrastructure
};
```

---

## 3. RTS Integration

```cpp
// Enable dictionary selection
TypeName("myModel");

declareRunTimeSelectionTable(...);

addToRunTimeSelectionTable(...);
```

---

## 4. Field Usage

```cpp
// Store fields as members
volScalarField k_;
volScalarField epsilon_;

// Use autoPtr for optional
autoPtr<volScalarField> nuTilda_;
```

---

## 5. Method Design

```cpp
// Virtual for extensibility
virtual void correct();

// Access methods
virtual tmp<volScalarField> k() const;
```

---

## 6. Dictionary Reading

```cpp
// Use coeffDict for coefficients
coeffDict().readEntry("Cmu", Cmu_);

// Or with default
Cmu_ = coeffDict().getOrDefault<scalar>("Cmu", 0.09);
```

---

## Quick Reference

| Aspect | Approach |
|--------|----------|
| Base class | Inherit from existing |
| Extensibility | RTS |
| Fields | Member variables |
| Coefficients | Dictionary |

---

## 🧠 Concept Check

<details>
<summary><b>1. ทำไมใช้ inheritance?</b></summary>

**Reuse** base class infrastructure และ fit OpenFOAM ecosystem
</details>

<details>
<summary><b>2. RTS ช่วยอะไร?</b></summary>

**User can select** model จาก dictionary
</details>

<details>
<summary><b>3. Dictionary coefficients ดีอย่างไร?</b></summary>

**Tunable** โดยไม่ต้อง recompile
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Folder Organization:** [03_Folder_and_File_Organization.md](03_Folder_and_File_Organization.md)