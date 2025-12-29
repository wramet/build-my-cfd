# Test Framework Coding - Overview

ภาพรวมกรอบการทดสอบ (Test Framework)

> **Test Framework** = Framework สำหรับ testing OpenFOAM code

---

## 1. Testing Levels

```
        ▲ System Tests (10%)
       /  \    - Complete solver runs
      /----\   - Full case validation
     /------\
    / Integration \  Integration Tests (20%)
   /----------------\ - Component interaction
  /   Unit Tests (70%)  \ - Function tests
/------------------------\ - Class tests
```

| Level | Scope | Tool |
|:---|:---|:---|
| **Unit** | Function | Custom test executables |
| **Integration** | Components | Test with mesh + models |
| **System** | Full Case | Allrun/Allclean scripts |

---

## 2. Test Structure

**Unit Test Directory:**
```
tests/unit/
├── Test_vector.C          # Test source
├── Make/
│   ├── files              # Source files
│   └── options            # Compiler flags
└── Test_vector            # Executable
```

**System Test Directory:**
```
tutorials/test_case/
├── Allrun                 # Run test
├── Allclean               # Clean test
├── system/                # Settings
├── constant/              # Mesh
├── 0/                     # Initial conditions
└── expected/              # Reference results
```

---

## 3. Allrun Pattern

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

## 4. Module Contents

| File | Topic | Lines |
|:---|:---|:---:|
| **01_Unit_Testing** | Function tests | ~160 |
| **02_Validation** | Physics checks | ~160 |
| **03_Automation** | Scripts | ~164 |

---

## Quick Reference

| Test Type | Use | Tool |
|:---|:---|:---|
| **Unit** | Single function | Custom executable |
| **Integration** | Components | Test with mesh |
| **System** | Full case | Allrun script |
| **Validation** | Physics | Compare with experiment |

---

## Concept Check

<details>
<summary><b>1. Unit vs System test?</b></summary>

- **Unit**: Test single function (ทดสอบ function เดี่ยว)
- **System**: Test complete solver (ทดสอบ solver ทั้งหมด)
</details>

<details>
<summary><b>2. Allrun ทำอะไร?</b></summary>

**Run case** และ optionally validate (รัน case และตรวจสอบผลลัพธ์)
</details>

<details>
<summary><b>3. expected/ ใช้ทำอะไร?</b></summary>

**Store expected results** สำหรับ comparison (เก็บผลลัพธ์อ้างอิง)
</details>

---

## Related Documents

- **Unit Testing:** [01_Unit_Testing.md](01_Unit_Testing.md)
- **Validation:** [02_Validation_Coding.md](02_Validation_Coding.md)
- **Automation:** [03_Automation_Scripts.md](03_Automation_Scripts.md)
