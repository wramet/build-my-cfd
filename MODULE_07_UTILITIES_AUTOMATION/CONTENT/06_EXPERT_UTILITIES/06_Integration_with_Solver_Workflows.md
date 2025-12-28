# Solver Workflow Integration

การ Integrate Utilities กับ Solver

---

## Overview

> **Integrate utilities** เข้ากับ solver workflow

---

## 1. Pre-Processing

```bash
#!/bin/bash
# Allrun.pre
blockMesh
snappyHexMesh -overwrite
checkMesh
setFields
decomposePar
```

---

## 2. Solve

```bash
#!/bin/bash
# Allrun.solve
mpirun -np $NPROCS simpleFoam -parallel > log.solver 2>&1
```

---

## 3. Post-Processing

```bash
#!/bin/bash
# Allrun.post
reconstructPar -latestTime
postProcess -func 'yPlus'
foamToVTK -latestTime
python3 scripts/plot_results.py
```

---

## 4. Complete Workflow

```bash
#!/bin/bash
# Allrun
./Allrun.pre
./Allrun.solve
./Allrun.post
```

---

## 5. Function Objects

```cpp
// system/controlDict
functions
{
    fieldAverage1 { type fieldAverage; ... }
    forces1 { type forces; ... }
}
```

---

## Quick Reference

| Phase | Scripts |
|-------|---------|
| Pre | Mesh, setFields |
| Solve | Run solver |
| Post | Process, visualize |

---

## Concept Check

<details>
<summary><b>1. Function objects ดีอย่างไร?</b></summary>

**On-the-fly** post-processing during simulation
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)