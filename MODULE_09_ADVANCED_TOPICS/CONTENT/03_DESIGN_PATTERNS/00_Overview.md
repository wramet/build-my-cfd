# Design Patterns - Overview

ภาพรวม Design Patterns ใน OpenFOAM

---

## Overview

> **Design Patterns** = Proven solutions to common problems

---

## 1. Key Patterns in OpenFOAM

| Pattern | Use |
|---------|-----|
| **Factory** | Create models from dict |
| **Strategy** | Interchangeable algorithms |
| **Template Method** | Define algorithm skeleton |
| **Observer** | Function objects |
| **Singleton** | Global registries |

---

## 2. Factory Pattern

```cpp
// Create turbulence model from dictionary
autoPtr<turbulenceModel> turb = turbulenceModel::New(dict);

// User code doesn't know concrete type
turb->correct();
```

---

## 3. Strategy Pattern

```cpp
// Interchangeable schemes
fvSchemes
{
    divSchemes
    {
        div(phi,U)  Gauss linear;      // or upwind, QUICK...
    }
}

// Algorithm selected at runtime
```

---

## 4. Template Method

```cpp
class solver
{
public:
    void run()
    {
        initialize();       // Override in derived
        while (loop())
        {
            solve();        // Override in derived
            postProcess();  // Default implementation
        }
    }
};
```

---

## 5. Observer (Function Objects)

```cpp
// controlDict
functions
{
    fieldAverage { type fieldAverage; ... }
    probes { type probes; ... }
}

// Automatically called at each time step
```

---

## 6. Module Contents

| File | Topic |
|------|-------|
| 01_Introduction | Basics |
| 02_Factory | Factory pattern |
| 03_Strategy | Strategy pattern |
| 04_Synergy | Pattern combinations |
| 05_Performance | Analysis |
| 06_Exercise | Practice |

---

## Quick Reference

| Pattern | OpenFOAM Example |
|---------|------------------|
| Factory | `Model::New(dict)` |
| Strategy | fvSchemes selection |
| Observer | functionObjects |
| Singleton | Time, mesh registries |

---

## 🧠 Concept Check

<details>
<summary><b>1. Factory pattern ดีอย่างไร?</b></summary>

**Decouple creation from usage** — user code works with any model
</details>

<details>
<summary><b>2. Strategy vs Inheritance?</b></summary>

**Strategy**: Algorithms as objects, changeable at runtime
</details>

<details>
<summary><b>3. Function objects = Observer?</b></summary>

**ใช่** — registered observers called at each time step
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **Introduction:** [01_Introduction.md](01_Introduction.md)
- **Factory:** [02_Factory_Pattern.md](02_Factory_Pattern.md)