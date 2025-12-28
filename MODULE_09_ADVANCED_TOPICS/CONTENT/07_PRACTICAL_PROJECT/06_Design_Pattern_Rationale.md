# Design Pattern Rationale

หลักการใช้ Design Patterns

---

## Overview

> Apply OpenFOAM patterns for consistent code

---

## 1. Factory Pattern

```cpp
// Create from dictionary
autoPtr<turbulenceModel> turb = turbulenceModel::New(dict);
```

### Why?

- User selects model type
- No solver changes needed
- Easy to add models

---

## 2. Strategy Pattern

```cpp
// Interchangeable algorithms
fvSchemes
{
    divSchemes { div(phi,U) Gauss upwind; }
}
```

### Why?

- Change without recompile
- Compare easily
- Tunable per case

---

## 3. Template Method

```cpp
class solver
{
    void main()
    {
        init();          // Override
        while (loop())
        {
            solve();     // Override
            postProcess();
        }
    }
};
```

### Why?

- Fixed algorithm structure
- Customize specific steps

---

## 4. RAII

```cpp
// Resource lifetime = object lifetime
autoPtr<volScalarField> field(new volScalarField(...));
// Automatic cleanup
```

### Why?

- No memory leaks
- Exception safe

---

## Quick Reference

| Pattern | When |
|---------|------|
| Factory | Create from dict |
| Strategy | Interchangeable |
| Template | Fixed structure |
| RAII | Resource management |

---

## 🧠 Concept Check

<details>
<summary><b>1. Factory vs direct construction?</b></summary>

**Factory**: Selection at runtime, decoupled code
</details>

<details>
<summary><b>2. Strategy vs hardcoded?</b></summary>

**Strategy**: Changeable without recompile
</details>

<details>
<summary><b>3. RAII ช่วยอะไร?</b></summary>

**Automatic cleanup** — no manual delete needed
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Inheritance:** [05_Inheritance_and_Virtual_Functions.md](05_Inheritance_and_Virtual_Functions.md)