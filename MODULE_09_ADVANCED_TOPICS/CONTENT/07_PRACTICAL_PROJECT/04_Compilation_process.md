# Compilation Process

กระบวนการ Compile

---

## Overview

> OpenFOAM uses **wmake** build system

---

## 1. Directory Structure

```
myProject/
├── Make/
│   ├── files      # Source files
│   └── options    # Compile options
├── myModel.H
├── myModel.C
└── myModelI.H     # Optional inline
```

---

## 2. Make/files

```make
# Source files
myModel.C

# Target
# For library:
LIB = $(FOAM_USER_LIBBIN)/libmyModel

# For application:
EXE = $(FOAM_USER_APPBIN)/mySolver
```

---

## 3. Make/options

```make
EXE_INC = \
    -I$(LIB_SRC)/finiteVolume/lnInclude \
    -I$(LIB_SRC)/meshTools/lnInclude

EXE_LIBS = \
    -lfiniteVolume \
    -lmeshTools
```

---

## 4. Build Commands

```bash
# Build
wmake

# Build library
wmake libso

# Clean
wclean

# Parallel build
wmake -j
```

---

## 5. Debug vs Opt

```bash
# Debug (with symbols)
export WM_COMPILE_OPTION=Debug
wclean && wmake

# Optimized
export WM_COMPILE_OPTION=Opt
wclean && wmake
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Build | `wmake` |
| Library | `wmake libso` |
| Clean | `wclean` |
| Debug | `WM_COMPILE_OPTION=Debug` |

---

## 🧠 Concept Check

<details>
<summary><b>1. Make/files ใส่อะไร?</b></summary>

**Source files** และ **target** (LIB หรือ EXE)
</details>

<details>
<summary><b>2. Make/options ใส่อะไร?</b></summary>

**Include paths** (EXE_INC) และ **libraries** (EXE_LIBS)
</details>

<details>
<summary><b>3. wmake libso ต่างจาก wmake อย่างไร?</b></summary>

**libso** = shared library, **wmake** = executable
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Errors:** [07_Common_Errors_and_Debugging.md](07_Common_Errors_and_Debugging.md)