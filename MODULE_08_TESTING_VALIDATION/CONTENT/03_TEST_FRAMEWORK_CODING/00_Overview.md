# Test Framework - Overview

ภาพรวม Test Framework

---

## Overview

> Framework สำหรับ testing OpenFOAM code

---

## 1. Testing Levels

| Level | Scope | Tools |
|-------|-------|-------|
| **Unit** | Function | Custom asserts |
| **Integration** | Components | Test cases |
| **System** | Full solver | Allrun scripts |

---

## 2. Unit Test Structure

```cpp
#include "fvCFD.H"

int main()
{
    // Test vector cross product
    vector a(1, 0, 0);
    vector b(0, 1, 0);
    vector c = a ^ b;
    
    if (mag(c - vector(0, 0, 1)) > SMALL)
    {
        FatalError << "Cross product failed";
        return 1;
    }
    
    Info << "PASSED" << endl;
    return 0;
}
```

---

## 3. System Test Structure

```
testCase/
├── Allrun
├── Allclean
├── system/
├── constant/
├── 0/
└── expected/
```

---

## 4. Allrun Pattern

```bash
#!/bin/bash
cd ${0%/*} || exit 1
. $WM_PROJECT_DIR/bin/tools/RunFunctions

runApplication blockMesh
runApplication simpleFoam

# Validate
if diff -q expected/p postProcessing/p > /dev/null; then
    echo "PASSED"
else
    echo "FAILED"
    exit 1
fi
```

---

## 5. Module Contents

| File | Topic |
|------|-------|
| 01_Unit_Testing | Function tests |
| 02_Validation | Physics checks |
| 03_Automation | Scripts |

---

## Quick Reference

| Test Type | Use |
|-----------|-----|
| Unit | Single function |
| Integration | Components |
| System | Full case |
| Validation | Physics |

---

## Concept Check

<details>
<summary><b>1. Unit vs System test?</b></summary>

- **Unit**: Test single function
- **System**: Test complete solver
</details>

<details>
<summary><b>2. Allrun ทำอะไร?</b></summary>

**Run case** และ optionally validate
</details>

<details>
<summary><b>3. expected/ ใช้ทำอะไร?</b></summary>

**Store expected results** สำหรับ comparison
</details>

---

## Related Documents

- **Unit Testing:** [01_Unit_Testing.md](01_Unit_Testing.md)
- **Automation:** [03_Automation_Scripts.md](03_Automation_Scripts.md)