# Automation Framework

Framework สำหรับ Automation

---

## Overview

> **Framework** = Reusable automation templates

---

## 1. Standard Functions

```bash
. $WM_PROJECT_DIR/bin/tools/RunFunctions

runApplication blockMesh
runParallel simpleFoam
```

---

## 2. Error Handling

```bash
#!/bin/bash
set -e  # Exit on error

blockMesh || exit 1
simpleFoam || exit 1
```

---

## 3. Parametric

```bash
#!/bin/bash
for Re in 100 500 1000; do
    caseName="Re_$Re"
    cp -r template $caseName
    sed -i "s/RE_VALUE/$Re/" $caseName/constant/transportProperties
    (cd $caseName && ./Allrun)
done
```

---

## 4. Parallel Batch

```bash
#!/bin/bash
for case in cases/*/; do
    (cd "$case" && ./Allrun) &
done
wait
```

---

## Quick Reference

| Function | Use |
|----------|-----|
| runApplication | Single process |
| runParallel | MPI run |
| set -e | Stop on error |

---

## Concept Check

<details>
<summary><b>1. set -e ทำอะไร?</b></summary>

**Stop script** when command fails
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)