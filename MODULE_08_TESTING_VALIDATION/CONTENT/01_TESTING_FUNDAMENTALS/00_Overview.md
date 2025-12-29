# Testing Fundamentals - Overview

ภาพรวมพื้นฐานการทดสอบ (Testing Fundamentals)

> **Testing** = Verify code correctness และ physics accuracy

---

## 1. Verification vs Validation

| Concept | Question | OpenFOAM Context |
|:---|:---|:---|
| **Verification** | Are we solving equations **right**? | Code, Math, Numerics → `system/fvSchemes`, `system/fvSolution` |
| **Validation** | Are we solving the **right** equations? | Physics, Experiment → `0/`, `constant/`, benchmarks |

> **จำง่ายๆ:** Verification = Math Check | Validation = Physics Check

---

## 2. Testing Levels (ปิรามิดการทดสอบ)

```
         ▲ Validation (5%)
        /  \    - Compare with experiment
       /----\   - Benchmark cases
      /------\
     / System Tests (15%)\ - Full solver runs
    /---------------------\
   / Integration Tests (20%)\ - Component interaction
  /----------------------------\
/     Unit Tests (60%)         \ - Function tests
--------------------------------
```

| Level | Scope | OpenFOAM Example | Time |
|:---|:---|:---|:---:|
| **Unit** | Single function | Test `vector::operator^()` | Seconds |
| **Integration** | Components | Test `fvMesh` + `volScalarField` | Minutes |
| **System** | Full Case | Run `simpleFoam` on tutorial | Hours |
| **Validation** | Physics | Compare with wind tunnel data | Days |

---

## 3. Module Structure

| Folder | Topic | Content |
|:---|:---|:---|
| **02_VERIFICATION** | Code correctness | MMS, Grid Convergence, GCI |
| **03_TEST_FRAMEWORK** | Coding tests | Unit Tests, Integration, Automation |
| **04_VALIDATION** | Physics accuracy | Benchmarks, Experimental comparison |
| **05_QA_AUTOMATION** | CI/profiling | Regression Testing, Performance Profiling |

---

## Quick Reference

| ต้องการ | ใช้อะไร |
|:---|:---|
| Test function | Unit Test |
| Test solver | System Test |
| Test physics | Validation |
| Auto-test | CI/CD |
| Profile performance | Profiling Tools |

---

## Concept Check

<details>
<summary><b>1. Verification vs Validation?</b></summary>

- **Verification**: Code does math right (แก้สมการถูกไหม?)
- **Validation**: Results match reality (ใช้สมการถูกไหม?)
</details>

<details>
<summary><b>2. Unit test คืออะไร?</b></summary>

**Test single function/class** in isolation
</details>

<details>
<summary><b>3. ทำไมต้อง automate?</b></summary>

**Consistent, reproducible** testing on every change
</details>

---

## Related Documents

- **Verification:** [../02_VERIFICATION_FUNDAMENTALS/00_Overview.md](../02_VERIFICATION_FUNDAMENTALS/00_Overview.md)
- **Test Framework:** [../03_TEST_FRAMEWORK_CODING/00_Overview.md](../03_TEST_FRAMEWORK_CODING/00_Overview.md)
- **Validation:** [../04_VALIDATION_BENCHMARKS/00_Overview.md](../04_VALIDATION_BENCHMARKS/00_Overview.md)
- **QA & Profiling:** [../05_QA_AUTOMATION_PROFILING/00_Overview.md](../05_QA_AUTOMATION_PROFILING/00_Overview.md)
