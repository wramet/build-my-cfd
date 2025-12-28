# Architecture and Design Patterns

สถาปัตยกรรม Utilities

---

## Overview

> Utilities follow **common patterns**

---

## 1. Standard Structure

```cpp
#include "fvCFD.H"

int main(int argc, char *argv[])
{
    #include "setRootCase.H"
    #include "createTime.H"
    #include "createMesh.H"

    // Utility logic

    return 0;
}
```

---

## 2. Command Line Args

```cpp
argList::addOption("patch", "name", "patch name");
argList::addBoolOption("overwrite", "...");

// Access
word patchName = args.get<word>("patch");
bool overwrite = args.found("overwrite");
```

---

## 3. Field Access

```cpp
// Read field
volScalarField T(IOobject("T", ...), mesh);

// Write field
T.write();
```

---

## Quick Reference

| Include | Purpose |
|---------|---------|
| setRootCase.H | Parse args |
| createTime.H | Create Time |
| createMesh.H | Create mesh |

---

## Concept Check

<details>
<summary><b>1. setRootCase ทำอะไร?</b></summary>

**Parse command line** and set case directory
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)