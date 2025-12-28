# Utility Categories

หมวดหมู่ของ Utilities

---

## Overview

> OpenFOAM utilities organized by **function**

---

## 1. Pre-Processing

| Utility | Use |
|---------|-----|
| blockMesh | Structured mesh |
| snappyHexMesh | Complex mesh |
| setFields | Initialize |
| topoSet | Create zones |

---

## 2. Mesh Manipulation

| Utility | Use |
|---------|-----|
| transformPoints | Scale/rotate |
| refineMesh | Add resolution |
| mergeMeshes | Combine |
| splitMeshRegions | Multi-region |

---

## 3. Running

| Utility | Use |
|---------|-----|
| decomposePar | Parallel prep |
| reconstructPar | Merge results |

---

## 4. Post-Processing

| Utility | Use |
|---------|-----|
| postProcess | Function objects |
| foamToVTK | Export |
| sample | Extract data |

---

## Quick Reference

| Phase | Utilities |
|-------|-----------|
| Pre | blockMesh, setFields |
| Mesh | transform, refine |
| Parallel | decompose, reconstruct |
| Post | postProcess, foamToVTK |

---

## 🧠 Concept Check

<details>
<summary><b>1. topoSet ใช้ทำอะไร?</b></summary>

**Create cellZones, faceZones** for regions/BCs
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)