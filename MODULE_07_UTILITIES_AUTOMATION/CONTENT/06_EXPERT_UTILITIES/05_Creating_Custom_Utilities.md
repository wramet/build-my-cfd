# Creating Custom Utilities

การสร้าง Utility เอง

---

## Overview

> Create **custom utilities** for specific tasks

---

## 1. Basic Structure

```
myUtility/
├── Make/
│   ├── files
│   └── options
└── myUtility.C
```

---

## 2. Make/files

```make
myUtility.C

EXE = $(FOAM_USER_APPBIN)/myUtility
```

---

## 3. Make/options

```make
EXE_INC = \
    -I$(LIB_SRC)/finiteVolume/lnInclude

EXE_LIBS = \
    -lfiniteVolume
```

---

## 4. Source Code

```cpp
#include "fvCFD.H"

int main(int argc, char *argv[])
{
    #include "setRootCase.H"
    #include "createTime.H"
    #include "createMesh.H"

    // Your code here
    Info << "Mesh cells: " << mesh.nCells() << endl;

    return 0;
}
```

---

## 5. Build

```bash
wmake
```

---

## Quick Reference

| File | Content |
|------|---------|
| Make/files | Sources, target |
| Make/options | Includes, libs |
| .C | Source code |

---

## 🧠 Concept Check

<details>
<summary><b>1. wmake ทำอะไร?</b></summary>

**Compile** utility using OpenFOAM build system
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)