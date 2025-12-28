# Utility Best Practices

แนวปฏิบัติที่ดีสำหรับ Utilities

---

## Overview

> Follow best practices for **reliable workflows**

---

## 1. Error Handling

```bash
#!/bin/bash
set -e  # Exit on error

blockMesh || { echo "blockMesh failed"; exit 1; }
```

---

## 2. Logging

```bash
simpleFoam > log.simpleFoam 2>&1

# Check for errors
if grep -q "FOAM FATAL" log.simpleFoam; then
    echo "Solver failed"
    exit 1
fi
```

---

## 3. Cleanup

```bash
#!/bin/bash
# Allclean
rm -rf 0.[0-9]* [1-9]* log.* postProcessing
cp -r 0.orig 0
```

---

## 4. Reproducibility

```bash
# Document environment
echo "OpenFOAM: $WM_PROJECT_VERSION" > environment.txt
echo "Date: $(date)" >> environment.txt
```

---

## 5. Parallel Safety

```bash
# Decompose before parallel run
decomposePar -force
mpirun -np $NPROCS solver -parallel
reconstructPar -latestTime
```

---

## Quick Reference

| Practice | Why |
|----------|-----|
| `set -e` | Stop on error |
| Log output | Debug later |
| Cleanup script | Fresh start |
| Document | Reproduce |

---

## 🧠 Concept Check

<details>
<summary><b>1. set -e ทำอะไร?</b></summary>

**Exit script** เมื่อ command fails
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)