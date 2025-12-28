# Dynamic Library Loading

การโหลด Library แบบ Dynamic

---

## Overview

> Load libraries at runtime without recompiling solver

---

## 1. In controlDict

```cpp
// system/controlDict
libs
(
    "libmyModels.so"
    "libmyBoundaryConditions.so"
);
```

---

## 2. In Code

```cpp
// Load programmatically
#include "dlLibraryTable.H"

dlLibraryTable::open("libmyModels.so");
```

---

## 3. Library Location

```bash
# User libraries
$FOAM_USER_LIBBIN

# System libraries
$FOAM_LIBBIN

# Or set LD_LIBRARY_PATH
```

---

## 4. Compiling Library

```bash
# Structure
myLib/
├── Make/
│   ├── files
│   └── options
├── myModel.H
└── myModel.C

# Make/files
myModel.C
LIB = $(FOAM_USER_LIBBIN)/libmyLib

# Compile
wmake libso
```

---

## 5. What Happens on Load

1. Library loaded to memory
2. Static initializers run
3. RTS registration executes
4. Models available for use

---

## Quick Reference

| Task | How |
|------|-----|
| Load in case | `libs (...)` |
| Load in code | `dlLibraryTable::open()` |
| Compile | `wmake libso` |
| Location | `$FOAM_USER_LIBBIN` |

---

## 🧠 Concept Check

<details>
<summary><b>1. libs directive ทำงานเมื่อไหร่?</b></summary>

**At solver startup** ก่อน read dictionaries
</details>

<details>
<summary><b>2. wmake libso ทำอะไร?</b></summary>

**Compile shared library** (.so file)
</details>

<details>
<summary><b>3. Static initializers ทำอะไร?</b></summary>

**Register classes** กับ RTS tables
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **RTS:** [02_Runtime_Selection_Tables.md](02_Runtime_Selection_Tables.md)