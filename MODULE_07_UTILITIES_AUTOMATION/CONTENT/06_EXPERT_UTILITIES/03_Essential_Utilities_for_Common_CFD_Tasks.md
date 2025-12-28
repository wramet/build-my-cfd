# Essential Utilities

Utilities ที่จำเป็นสำหรับ CFD

---

## Overview

> OpenFOAM มี **utilities มากมาย** สำหรับ common tasks

---

## 1. Mesh Utilities

| Utility | Use |
|---------|-----|
| blockMesh | Structured mesh |
| snappyHexMesh | Complex geometry |
| checkMesh | Verify quality |
| transformPoints | Scale/rotate |

```bash
blockMesh
checkMesh
transformPoints -scale '(0.001 0.001 0.001)'
```

---

## 2. Field Utilities

| Utility | Use |
|---------|-----|
| setFields | Initialize |
| mapFields | Interpolate |
| foamToVTK | Export |

```bash
setFields
foamToVTK -latestTime
```

---

## 3. Parallel Utilities

| Utility | Use |
|---------|-----|
| decomposePar | Split |
| reconstructPar | Merge |

```bash
decomposePar -force
mpirun -np 4 simpleFoam -parallel
reconstructPar
```

---

## 4. Post-Processing

| Utility | Use |
|---------|-----|
| postProcess | Function objects |
| sample | Extract data |
| probes | Point values |

```bash
postProcess -func 'yPlus'
```

---

## Quick Reference

| Task | Utility |
|------|---------|
| Create mesh | blockMesh |
| Check mesh | checkMesh |
| Initialize | setFields |
| Decompose | decomposePar |
| Post-process | postProcess |

---

## 🧠 Concept Check

<details>
<summary><b>1. checkMesh ตรวจอะไร?</b></summary>

**Mesh quality** — skewness, non-orthogonality
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)