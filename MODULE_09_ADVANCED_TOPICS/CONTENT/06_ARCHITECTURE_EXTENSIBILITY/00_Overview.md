# Architecture - Overview

ภาพรวม Architecture และ Extensibility

---

## Overview

> OpenFOAM = **Highly extensible** through RTS and dynamic loading

---

## 1. Extensibility Features

| Feature | Purpose |
|---------|---------|
| **RTS** | Runtime model selection |
| **Dynamic libs** | Load without recompile |
| **Function objects** | Post-processing hooks |
| **Object registry** | Centralized lookup |

---

## 2. Run-Time Selection

```cpp
// Dictionary-driven selection
autoPtr<turbulenceModel> turb = turbulenceModel::New(dict);
```

---

## 3. Dynamic Library Loading

```cpp
// In controlDict
libs ("libmyModels.so");

// Models auto-register on load
```

---

## 4. Function Objects

```cpp
// Post-processing hooks
functions
{
    average { type fieldAverage; ... }
}
```

---

## 5. Module Contents

| File | Topic |
|------|-------|
| 01_Introduction | Basics |
| 02_RTS | Selection tables |
| 03_Dynamic_Loading | Libraries |
| 04_FunctionObjects | Hooks |
| 05_Patterns | Design patterns |
| 06_Errors | Debugging |
| 07_Exercise | Practice |

---

## Quick Reference

| Need | Solution |
|------|----------|
| Select model | RTS |
| Add without recompile | Dynamic lib |
| Post-process | Function object |
| Find object | Registry |

---

## Concept Check

<details>
<summary><b>1. RTS คืออะไร?</b></summary>

**Run-Time Selection** — create from dictionary string
</details>

<details>
<summary><b>2. libs directive ทำอะไร?</b></summary>

**Load shared library** ที่มี registered models
</details>

<details>
<summary><b>3. Function objects ใช้เมื่อไหร่?</b></summary>

**Post-processing** — sampling, averaging, monitoring
</details>

---

## Related Documents

- **Introduction:** [01_Introduction.md](01_Introduction.md)
- **RTS:** [02_Runtime_Selection_Tables.md](02_Runtime_Selection_Tables.md)