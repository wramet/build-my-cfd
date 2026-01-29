# Module 02: Meshing and Case Setup

Mesh คือรากฐานของ CFD — ไม่ว่า solver ดีแค่ไหน mesh ที่แย่ก็ทำให้ผลลัพธ์ผิดพลาด

> **ทำไม Meshing สำคัญที่สุด?**
> - **Mesh คุณภาพดี = CFD ที่เชื่อถือได้** — 50%+ ของเวลางาน CFD อยู่ที่ mesh
> - Mesh แย่ → diverge, ช้า, หรือผลผิด แม้ solver ดี
> - ต้องเข้าใจ **blockMesh**, **snappyHexMesh**, และ **checkMesh**

---

## Learning Objectives

> **💡 เป้าหมาย: สามารถสร้าง Mesh คุณภาพสูงสำหรับ geometry ใดก็ได้**

### หลังจากผ่าน Module นี้ คุณจะสามารถ:

1. **เข้าใจกลยุทธ์การสร้าง Mesh** — blockMesh vs snappyHexMesh
2. **เชี่ยวชาญ snappyHexMesh** — Castellated → Snap → Layers
3. **ตรวจสอบคุณภาพ Mesh** — checkMesh, non-orthogonality, skewness
4. **จัดการ Mesh** — topoSet, cellZones, createPatch
5. **Runtime Post-processing** — functionObjects สำหรับ forces, probes

---

## เครื่องมือหลัก

| Tool | ใช้สำหรับ | Input |
|------|----------|-------|
| `blockMesh` | Structured mesh (simple geometry) | `system/blockMeshDict` |
| `snappyHexMesh` | Complex geometry (from STL) | `system/snappyHexMeshDict` |
| `checkMesh` | Mesh quality check | — |
| `topoSet` | Create cell/face sets | `system/topoSetDict` |
| `functionObjects` | Runtime data extraction | `system/controlDict` |

---

## โครงสร้างเนื้อหา

### 01_MESHING_FUNDAMENTALS

- [01_Introduction_to_Meshing.md](01_MESHING_FUNDAMENTALS/01_Introduction_to_Meshing.md) — Mesh คืออะไร? ทำไมคุณภาพสำคัญ?
- [02_OpenFOAM_Mesh_Structure.md](01_MESHING_FUNDAMENTALS/02_OpenFOAM_Mesh_Structure.md) — polyMesh structure

### 02_BLOCKMESH_MASTERY

- [01_BlockMesh_Deep_Dive.md](02_BLOCKMESH_MASTERY/01_BlockMesh_Deep_Dive.md) — Multi-block, grading, curved edges
- [02_Parametric_Meshing.md](02_BLOCKMESH_MASTERY/02_Parametric_Meshing.md) — M4 macros, parametric geometry

### 03_SNAPPYHEXMESH_BASICS

- [01_The_sHM_Workflow.md](03_SNAPPYHEXMESH_BASICS/01_The_sHM_Workflow.md) — 3-step workflow
- [02_Geometry_Preparation.md](03_SNAPPYHEXMESH_BASICS/02_Geometry_Preparation.md) — STL preparation
- [03_Castellated_Mesh_Settings.md](03_SNAPPYHEXMESH_BASICS/03_Castellated_Mesh_Settings.md) — Refinement levels

### 04_SNAPPYHEXMESH_ADVANCED

- [01_Layer_Addition_Strategy.md](04_SNAPPYHEXMESH_ADVANCED/01_Layer_Addition_Strategy.md) — Prism layers for y+
- [02_Refinement_Regions.md](04_SNAPPYHEXMESH_ADVANCED/02_Refinement_Regions.md) — Box, sphere, distance refinement
- [03_Multi_Region_Meshing.md](04_SNAPPYHEXMESH_ADVANCED/03_Multi_Region_Meshing.md) — CHT, porous media

### 05_MESH_QUALITY_AND_MANIPULATION

- [01_Mesh_Quality_Criteria.md](05_MESH_QUALITY_AND_MANIPULATION/01_Mesh_Quality_Criteria.md) — Non-orthogonality, skewness
- [02_Using_TopoSet_and_CellZones.md](05_MESH_QUALITY_AND_MANIPULATION/02_Using_TopoSet_and_CellZones.md) — Zones for MRF, porosity
- [03_Mesh_Manipulation_Tools.md](05_MESH_QUALITY_AND_MANIPULATION/03_Mesh_Manipulation_Tools.md) — transformPoints, mergeMeshes

### 06_RUNTIME_POST_PROCESSING

- [01_Introduction_to_FunctionObjects.md](06_RUNTIME_POST_PROCESSING/01_Introduction_to_FunctionObjects.md) — Runtime data extraction
- [02_Forces_and_Coefficients.md](06_RUNTIME_POST_PROCESSING/02_Forces_and_Coefficients.md) — Cl, Cd calculation
- [03_Sampling_and_Probes.md](06_RUNTIME_POST_PROCESSING/03_Sampling_and_Probes.md) — Line plots, monitoring points

---

## Mesh Types Quick Reference

| Type | Tool | Cell Shape | Use Case |
|------|------|------------|----------|
| Structured | blockMesh | Hexahedral | Simple geometry, high quality |
| Unstructured | snappyHexMesh | Hex-dominant | Complex geometry |
| Tetrahedral | External (Gmsh) | Tet | Very complex, imported |
| Polyhedral | polyDualMesh | Polyhedral | After tet conversion |

---

## Quality Metrics

| Metric | Good | Acceptable | Bad |
|--------|------|------------|-----|
| Non-orthogonality | < 50° | 50-70° | > 70° |
| Skewness | < 2 | 2-4 | > 4 |
| Aspect ratio | < 10 | 10-100 | > 100 |
| Max volume ratio | < 4 | 4-10 | > 10 |

---

## Key Takeaways

- ✅ **Mesh quality สำคัญที่สุด** — 50%+ ของเวลา CFD อยู่ที่การสร้าง mesh ที่ดี
- ✅ **blockMesh** สำหรับ simple geometry ที่ต้องการคุณภาพสูง
- ✅ **snappyHexMesh** สำหรับ complex geometry ด้วย 3-step workflow: Castellated → Snap → Layers
- ✅ **checkMesh** ต้องใช้ทุกครั้ง — ตรวจสอบ non-orthogonality, skewness, aspect ratio
- ✅ **functionObjects** ช่วยดึงข้อมูลระหว่าง run ทำให้ประหยัดเวลาและ disk space
- ✅ **Mesh manipulation** (topoSet, cellZones) จำเป็นสำหรับ advanced features (MRF, porosity, CHT)

---

## Concept Check

<details>
<summary><b>1. ทำไม checkMesh ถึงสำคัญ?</b></summary>

Mesh คุณภาพต่ำทำให้:
- Solver diverge
- ผลลัพธ์ไม่แม่นยำ
- Convergence ช้า
</details>

<details>
<summary><b>2. blockMesh vs snappyHexMesh ต่างกันอย่างไร?</b></summary>

- **blockMesh**: Structured, manual vertex definition, simple geometry
- **snappyHexMesh**: Semi-automated, snaps to STL surface, complex geometry
</details>

<details>
<summary><b>3. functionObjects มีประโยชน์อย่างไร?</b></summary>

ดึงข้อมูล (forces, averages, probes) ระหว่าง run — ไม่ต้องรอ simulation เสร็จ ไม่ต้องเก็บ data ขนาดใหญ่
</details>

<details>
<summary><b>4. Metric ไหนที่บ่งชี้ว่า mesh มีปัญหามากที่สุด?</b></summary>

**Non-orthogonality > 70°** หรือ **skewness > 4** โดยทั่วไปจะทำให้ solver diverge หรือ converge ช้ามาก
</details>

<details>
<summary><b>5. Layer cells ใน snappyHexMesh ใช้สำหรับอะไร?</b></summary>

สำหรับ **resolve boundary layer** เพื่อให้ได้ **y+ values** ที่เหมาะสมกับ turbulence model ที่ใช้
</details>

---

## Learning Path

```
Start: 01_MESHING_FUNDAMENTALS
           ↓
    02_BLOCKMESH_MASTERY (เรียนพื้นฐาน structured mesh)
           ↓
    03_SNAPPYHEXMESH_BASICS (เรียน workflow ขั้นต้น)
           ↓
    04_SNAPPYHEXMESH_ADVANCED (ขั้นสูง: layers, multi-region)
           ↓
    05_MESH_QUALITY_AND_MANIPULATION (ตรวจสอบและจัดการ mesh)
           ↓
    06_RUNTIME_POST_PROCESSING (ดึงข้อมูลระหว่าง run)
```

**💡 Tip:** หากเป็นมือใหม่ — ทำ 01 → 02 → 03 ตามลำดับก่อน  
**💡 Tip:** หากมีพื้นฐานแล้ว — ข้ามไป 03 → 04 ได้เลย

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [MODULE_01_CFD_FUNDAMENTALS](../MODULE_01_CFD_FUNDAMENTALS/00_Overview.md) — Governing equations, boundary conditions
- **บทถัดไป:** [01_Introduction_to_Meshing.md](01_MESHING_FUNDAMENTALS/01_Introduction_to_Meshing.md) — เริ่มต้นเรียนรู้ mesh fundamentals