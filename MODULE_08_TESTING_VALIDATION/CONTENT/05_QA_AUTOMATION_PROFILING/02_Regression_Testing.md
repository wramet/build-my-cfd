# Regression Testing

การทดสอบ Regression

---

## Overview

> **Regression testing** = Ensure changes don't break existing functionality

---

## 1. What to Test

| Level | Example |
|-------|---------|
| **Unit** | Function outputs |
| **Integration** | Solver components |
| **System** | Complete cases |
| **Benchmark** | Standard results |

---

## 2. Test Case Structure

```
testCase/
├── Allrun
├── Allclean
├── system/
├── constant/
├── 0/
└── expected/
    └── results.txt
```

---

## 3. Allrun with Validation

```bash
#!/bin/bash
cd ${0%/*} || exit 1
. $WM_PROJECT_DIR/bin/tools/RunFunctions

# Run
runApplication blockMesh
runApplication simpleFoam

# Validate
postProcess -func 'probes'

# Compare
diff -q expected/probes.txt postProcessing/probes/0/p > /dev/null
if [ $? -eq 0 ]; then
    echo "PASSED"
else
    echo "FAILED"
    exit 1
fi
```

---

## 4. Tolerance-Based Comparison

```python
#!/usr/bin/env python3
import numpy as np

expected = np.loadtxt('expected/results.txt')
actual = np.loadtxt('postProcessing/results.txt')

# Check within tolerance
tol = 1e-6
if np.allclose(expected, actual, rtol=tol):
    print("PASSED")
    exit(0)
else:
    print(f"FAILED: max diff = {np.max(np.abs(expected - actual))}")
    exit(1)
```

---

## 5. Running All Tests

```bash
#!/bin/bash
# runRegressionTests.sh

passed=0
failed=0

for test in tests/*/; do
    echo "Testing: $test"
    (cd "$test" && ./Allrun) > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        ((passed++))
        echo "  ✓ PASSED"
    else
        ((failed++))
        echo "  ✗ FAILED"
    fi
done

echo "Results: $passed passed, $failed failed"
[ $failed -eq 0 ] || exit 1
```

---

## 6. CI Integration

```yaml
# .github/workflows/regression.yml
name: Regression Tests

on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    container: openfoam/openfoam-v2312
    steps:
      - uses: actions/checkout@v2
      - run: ./runRegressionTests.sh
```

---

## Quick Reference

| Task | Script |
|------|--------|
| Run test | `Allrun` |
| Clean | `Allclean` |
| Compare | `diff` or Python |
| Batch | `runRegressionTests.sh` |

---

## Concept Check

<details>
<summary><b>1. Regression testing ทำไม?</b></summary>

**Catch bugs** ที่เกิดจากการเปลี่ยนแปลง code
</details>

<details>
<summary><b>2. Tolerance ใช้ทำไม?</b></summary>

**Floating-point differences** — ไม่ exact เท่ากัน
</details>

<details>
<summary><b>3. CI ช่วยอย่างไร?</b></summary>

**Auto-run tests** ทุก commit — catch issues เร็ว
</details>

---

## Related Documents

- **ภาพรวม:** [../05_QA_AUTOMATION_PROFILING/00_Overview.md](../05_QA_AUTOMATION_PROFILING/00_Overview.md)
- **Debugging:** [03_Debugging_Troubleshooting.md](03_Debugging_Troubleshooting.md)