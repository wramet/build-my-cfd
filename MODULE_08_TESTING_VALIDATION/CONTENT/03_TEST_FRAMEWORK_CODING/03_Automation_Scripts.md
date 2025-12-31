# Automation Scripts for OpenFOAM Testing

สคริปต์สำหรับ automation testing ใน OpenFOAM

---

## 🎯 Learning Objectives

หลังจากอ่านบทนี้ คุณจะสามารถ:

1. **เขียน** Allrun และ Allclean scripts ตามมาตรฐาน OpenFOAM
2. **สร้าง** automated test scripts ที่ตรวจสอบผลลัพธ์
3. **ออกแบบ** comparison scripts สำหรับ validation
4. **integrate** test scripts กับ CI/CD pipelines (GitHub Actions, GitLab CI)
5. **เขียน** regression test scripts สำหรับ code changes

---

## 🏗️ 3W Framework

### What: Automation Scripts คืออะไร?

**Automation scripts** คือ shell scripts ที่ช่วย:
- รัน cases อัตโนมัติ (Allrun)
- Cleanup cases (Allclean)
- ตรวจสอบผลลัพธ์ (validation scripts)
- เปรียบเทียบกับ reference data (comparison scripts)

### Why: ทำไมต้อง Automate?

| Manual | Automated |
|--------|-----------|
| Forget steps | Consistent every time |
| Human errors | Reproducible |
| Time-consuming | Fast iteration |
| Hard to repeat | Easy regression testing |

### How: Standard Patterns

```bash
# Standard OpenFOAM workflow
./Allrun          # Run complete case
./Allclean        # Clean for fresh run
./runTest.sh      # Run with validation
```

---

## 1. Allrun Script Pattern

### 1.1 Basic Allrun

```bash
#!/bin/bash
cd "${0%/*}" || exit                                # Run from this directory
. ${WM_PROJECT_DIR:?}/bin/tools/RunFunctions        # Source run functions

# Mesh generation
runApplication blockMesh

# Initialize fields (optional)
runApplication setFields

# Run solver
runApplication simpleFoam
```

### 1.2 Enhanced Allrun with Error Handling

```bash
#!/bin/bash
cd "${0%/*}" || exit
. ${WM_PROJECT_DIR:?}/bin/tools/RunFunctions

# Function to run with check
runWithCheck() {
    local app=$1
    runApplication "$app"
    if [ ! -f "log.$app" ] || grep -q "FOAM FATAL" "log.$app"; then
        echo "ERROR: $app failed"
        exit 1
    fi
}

# Run with validation
runWithCheck blockMesh
runWithCheck checkMesh
runWithCheck simpleFoam

# Post-process
runApplication postProcess -func "yPlus"

echo "Case completed successfully"
```

### 1.3 Parallel Allrun

```bash
#!/bin/bash
cd "${0%/*}" || exit
. ${WM_PROJECT_DIR:?}/bin/tools/RunFunctions

# Number of processors
nProcs=4

# Serial mesh generation
runApplication blockMesh

# Decompose
runApplication decomposePar

# Parallel run
runParallel simpleFoam

# Reconstruct
runApplication reconstructPar -latestTime

# Cleanup processor directories
rm -rf processor*

echo "Parallel case completed"
```

---

## 2. Allclean Script Pattern

### 2.1 Basic Allclean

```bash
#!/bin/bash
cd "${0%/*}" || exit
. ${WM_PROJECT_DIR:?}/bin/tools/CleanFunctions

# Standard cleanup
cleanCase
```

### 2.2 Enhanced Allclean with Safety

```bash
#!/bin/bash
cd "${0%/*}" || exit
. ${WM_PROJECT_DIR:?}/bin/tools/CleanFunctions

echo "Cleaning case..."

# 1. Remove time directories (except 0)
foamListTimes -rm

# 2. Remove processor directories
rm -rf processor*

# 3. Remove logs
rm -f log.*

# 4. Remove post-processing
rm -rf postProcessing

# 5. Remove mesh (but keep 0/)
rm -rf constant/polyMesh

# 6. Remove VTK output
rm -rf VTK

echo "Case cleaned"
```

---

## 3. Test Runner Scripts

### 3.1 Basic Test Script

```bash
#!/bin/bash
# runTest.sh - Run case and validate results

set -e  # Exit on error

CASE_DIR=$(dirname "$0")
cd "$CASE_DIR"

echo "=== Running Test: $(basename $PWD) ==="

# 1. Clean previous run
./Allclean

# 2. Run case
./Allrun

# 3. Validate results
echo "Validating results..."

# Check final residuals
FINAL_RESIDUAL=$(grep "Solving for p" log.simpleFoam | tail -1 | awk '{print $8}' | tr -d ',')
if (( $(echo "$FINAL_RESIDUAL > 1e-4" | bc -l) )); then
    echo "FAIL: Residual too high ($FINAL_RESIDUAL)"
    exit 1
fi

echo "PASS: Test completed successfully"
```

### 3.2 Comparison Script

```bash
#!/bin/bash
# compare_results.sh - Compare with reference data

TOLERANCE=1e-5

# Compare pressure at probe point
CFD_VALUE=$(postProcess -func "probes" -latestTime | grep "^0.5" | awk '{print $2}')
REF_VALUE=101325.0

DIFF=$(echo "scale=10; ($CFD_VALUE - $REF_VALUE) / $REF_VALUE" | bc -l)
ABS_DIFF=$(echo "scale=10; if ($DIFF < 0) -1*$DIFF else $DIFF" | bc -l)

if (( $(echo "$ABS_DIFF > $TOLERANCE" | bc -l) )); then
    echo "FAIL: Difference $ABS_DIFF exceeds tolerance $TOLERANCE"
    exit 1
else
    echo "PASS: Difference $ABS_DIFF within tolerance"
fi
```

---

## 4. CI Integration

### 4.1 GitHub Actions

```yaml
# .github/workflows/openfoam-tests.yml
name: OpenFOAM Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    container:
      image: openfoam/openfoam2312-jammy

    steps:
      - uses: actions/checkout@v4

      - name: Run tests
        run: |
          source /usr/lib/openfoam/openfoam2312/etc/bashrc
          cd tutorials/incompressible/simpleFoam/pitzDaily
          ./Allrun
          ./runTest.sh

      - name: Upload logs on failure
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: logs
          path: "**/log.*"
```

### 4.2 GitLab CI

```yaml
# .gitlab-ci.yml
stages:
  - test

openfoam-tests:
  stage: test
  image: openfoam/openfoam2312-jammy
  script:
    - source /usr/lib/openfoam/openfoam2312/etc/bashrc
    - ./Allrun
    - ./runTest.sh
  artifacts:
    when: on_failure
    paths:
      - log.*
```

---

## 5. Regression Testing

### 5.1 Multi-Case Runner

```bash
#!/bin/bash
# run_all_tests.sh - Run all test cases

PASSED=0
FAILED=0
FAILED_CASES=()

for case_dir in tutorials/*/; do
    if [ -f "$case_dir/runTest.sh" ]; then
        echo "Testing: $case_dir"
        if (cd "$case_dir" && ./runTest.sh); then
            ((PASSED++))
        else
            ((FAILED++))
            FAILED_CASES+=("$case_dir")
        fi
    fi
done

echo ""
echo "=== Test Summary ==="
echo "Passed: $PASSED"
echo "Failed: $FAILED"

if [ $FAILED -gt 0 ]; then
    echo "Failed cases:"
    printf '%s\n' "${FAILED_CASES[@]}"
    exit 1
fi
```

---

## ⚠️ Common Pitfalls

| Problem | Cause | Solution |
|---------|-------|----------|
| Script not executable | Missing chmod | `chmod +x Allrun` |
| "command not found" | OpenFOAM not sourced | Add `source $WM_PROJECT_DIR/etc/bashrc` |
| Residual parsing fails | Log format changed | Update grep pattern |
| Tolerance too strict | Numerical noise | Use relative tolerance |

---

## 🧠 Concept Check

<details>
<summary><b>1. runApplication กับ runParallel ต่างกันอย่างไร?</b></summary>

**runApplication:** รัน serial (single processor)
- ไม่ต้อง decompose
- เหมาะกับ pre/post-processing

**runParallel:** รัน parallel (multi-processor)
- ต้อง decompose ก่อน
- ใช้ mpirun
</details>

<details>
<summary><b>2. ทำไมต้องใช้ set -e ใน test scripts?</b></summary>

**Exit immediately on error:**
- ป้องกัน false positives
- ไม่ต้อง check exit status ทุก command
- ทำให้ script fail fast
</details>

---

## 📖 Related Documents

- [00_Overview.md](00_Overview.md) — Module overview
- [01_Unit_Testing.md](../01_TESTING_FUNDAMENTALS/) — Unit testing
- [02_Validation_Coding.md](02_Validation_Coding.md) — Validation scripts