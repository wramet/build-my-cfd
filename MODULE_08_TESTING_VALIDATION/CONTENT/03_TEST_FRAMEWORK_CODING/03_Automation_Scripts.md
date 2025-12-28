# Automation Scripts

สคริปต์สำหรับ Automation Testing

---

## Overview

> **Automation** = ทำให้ testing เป็น reproducible และ consistent

---

## 1. Basic Test Script

```bash
#!/bin/bash
# runTest.sh

case=$1
solver=$2

# Run simulation
cd $case
blockMesh
$solver

# Check result
if grep -q "FOAM FATAL" log.$solver; then
    echo "FAILED"
    exit 1
fi
echo "PASSED"
```

---

## 2. Allrun Pattern

```bash
#!/bin/bash
# Allrun

cd ${0%/*} || exit 1
. $WM_PROJECT_DIR/bin/tools/RunFunctions

runApplication blockMesh
runApplication simpleFoam

# Post-process
runApplication postProcess -func 'yPlus'
```

---

## 3. Allclean Pattern

```bash
#!/bin/bash
# Allclean

cd ${0%/*} || exit 1

rm -rf 0.* [1-9]* log.* postProcessing processor*
cp -r 0.orig 0
```

---

## 4. Comparison Script

```bash
#!/bin/bash
# compare.sh

expected="expected/result.txt"
actual="postProcessing/result.txt"

if diff -q "$expected" "$actual" > /dev/null; then
    echo "✓ Results match"
else
    echo "✗ Results differ"
    diff "$expected" "$actual"
    exit 1
fi
```

---

## 5. Batch Testing

```bash
#!/bin/bash
# runAllTests.sh

for case in test_*/; do
    echo "Testing: $case"
    (cd "$case" && ./Allrun)
    if [ $? -ne 0 ]; then
        echo "FAILED: $case"
        failed+=("$case")
    fi
done

echo "Failed: ${#failed[@]} tests"
```

---

## 6. CI Integration

```yaml
# .github/workflows/test.yml
name: OpenFOAM Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: ./runAllTests.sh
```

---

## Quick Reference

| Script | Purpose |
|--------|---------|
| `Allrun` | Run case |
| `Allclean` | Clean case |
| `runTest.sh` | Single test |
| `runAllTests.sh` | Batch tests |

---

## Concept Check

<details>
<summary><b>1. Allrun ทำไม?</b></summary>

**Standard pattern** สำหรับ reproducible case execution
</details>

<details>
<summary><b>2. CI ช่วยอะไร?</b></summary>

**Automatic testing** ทุก commit — catch regressions เร็ว
</details>

<details>
<summary><b>3. diff ใช้ทำอะไร?</b></summary>

**Compare results** กับ expected — verify correctness
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Unit Testing:** [01_Unit_Testing.md](01_Unit_Testing.md)