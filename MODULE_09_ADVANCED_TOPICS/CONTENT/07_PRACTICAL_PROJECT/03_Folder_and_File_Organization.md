# Folder and File Organization

การจัดโครงสร้างโฟลเดอร์และไฟล์

---

## Overview

> Follow OpenFOAM **naming conventions** for maintainability

---

## 1. Standard Layout

```
myModel/
├── Make/
│   ├── files      # Sources + target
│   └── options    # Includes + libs
├── lnInclude/     # Auto-generated
├── myModel.H      # Declaration
├── myModel.C      # Implementation
└── myModelI.H     # Optional inline
```

---

## 2. Header File (.H)

```cpp
#ifndef myModel_H
#define myModel_H

#include "baseClass.H"

namespace Foam
{

class myModel : public baseClass
{
    // ...
};

}

#endif
```

---

## 3. Source File (.C)

```cpp
#include "myModel.H"

// Optionally include template implementations
#ifdef NoRepository
    #include "myModelTemplates.C"
#endif

namespace Foam
{

defineTypeNameAndDebug(myModel, 0);

// Implementation

}
```

---

## 4. Make/files

```make
myModel.C
AnotherSource.C

LIB = $(FOAM_USER_LIBBIN)/libMyModel
```

---

## 5. Make/options

```make
EXE_INC = \
    -I$(LIB_SRC)/finiteVolume/lnInclude

EXE_LIBS = \
    -lfiniteVolume
```

---

## 6. Naming Conventions

| Item | Convention |
|------|------------|
| Class | PascalCase |
| File | same as class |
| Function | camelCase |
| Variable | camelCase_ |

---

## Quick Reference

| File | Content |
|------|---------|
| `.H` | Declarations |
| `.C` | Implementations |
| `I.H` | Inline methods |
| `Templates.C` | Template code |

---

## 🧠 Concept Check

<details>
<summary><b>1. lnInclude ทำไม?</b></summary>

**Symlinks** สำหรับ include paths — auto-generated
</details>

<details>
<summary><b>2. แยก .H และ .C ทำไม?</b></summary>

**Compilation efficiency** และ readability
</details>

<details>
<summary><b>3. Make/options ใส่อะไร?</b></summary>

**Include paths** และ **libraries**
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Compilation:** [04_Compilation_process.md](04_Compilation_process.md)