---
name: Meshing Expert
description: |
  Use this skill when: user wants to learn about meshing, blockMesh, snappyHexMesh, mesh quality, or mesh manipulation in OpenFOAM.
  
  Specialist tutor for MODULE_02_MESHING_AND_CASE_SETUP content.
---

# Meshing Expert

ผู้เชี่ยวชาญด้าน Meshing: blockMesh, snappyHexMesh, Mesh Quality

## Knowledge Base

**Primary Content:** `MODULE_02_MESHING_AND_CASE_SETUP/CONTENT/`

```
01_MESHING_FUNDAMENTALS/
├── 00_Overview.md              → Mesh basics
├── 01_Mesh_Types.md            → Structured, unstructured
└── 02_OpenFOAM_Mesh_Structure.md → points, faces, cells

02_BLOCKMESH_MASTERY/
├── 00_Overview.md              → blockMesh basics
├── 01_Basic_Geometry.md        → vertices, blocks
├── 02_Parametric_Meshing.md    → M4, Python templates
└── 03_Advanced_Grading.md      → simpleGrading, edgeGrading

03_SNAPPYHEXMESH_BASICS/
├── 00_Overview.md              → snappyHexMesh workflow
├── 01_Background_Mesh.md       → Base mesh requirements
├── 02_Geometry_Definition.md   → triSurfaceMesh, STL
└── 03_Castellated_Settings.md  → refinement levels

04_SNAPPYHEXMESH_ADVANCED/
├── 01_Surface_Refinement.md    → Surface layers
├── 02_Refinement_Regions.md    → Box, sphere regions
└── 03_Mesh_Layers.md           → addLayers settings

05_MESH_QUALITY/
├── 01_Quality_Criteria.md      → Non-orthogonality, skewness
├── 02_checkMesh_Output.md      → Interpreting results
└── 03_Mesh_Improvement.md      → Fixing bad cells
```

## Learning Paths

### 🟢 Beginner: "ฉันอยากสร้าง mesh แรก"

| Step | File | Time | Focus |
|------|------|------|-------|
| 1 | `01_MESHING.../02_OpenFOAM_Mesh_Structure.md` | 30 min | points, faces, owner |
| 2 | `02_BLOCKMESH.../00_Overview.md` | 30 min | blockMesh basics |
| 3 | `02_BLOCKMESH.../01_Basic_Geometry.md` | 45 min | vertices, blocks |
| 4 | **Hands-on** | 45 min | cavity mesh |

**Tutorial:**
```bash
cd $FOAM_TUTORIALS/incompressible/icoFoam/cavity/cavity
cat system/blockMeshDict
blockMesh
checkMesh
paraFoam  # View mesh
```

### 🟡 Intermediate: "ฉันอยากใช้ snappyHexMesh"

| Step | File | Time | Focus |
|------|------|------|-------|
| 1 | `03_SNAPPY.../00_Overview.md` | 30 min | 3-step process |
| 2 | `03_SNAPPY.../01_Background_Mesh.md` | 30 min | Base mesh |
| 3 | `03_SNAPPY.../03_Castellated_Settings.md` | 45 min | Refinement |
| 4 | `04_SNAPPY.../03_Mesh_Layers.md` | 45 min | Boundary layers |
| 5 | **Hands-on** | 60 min | motorBike tutorial |

**Tutorial:**
```bash
cd $FOAM_TUTORIALS/incompressible/simpleFoam/motorBike
./Allrun
checkMesh -allGeometry -allTopology
```

### 🔴 Advanced: "ฉันต้อง debug mesh quality"

| Step | File | Time | Focus |
|------|------|------|-------|
| 1 | `05_MESH.../01_Quality_Criteria.md` | 45 min | Quality metrics |
| 2 | `05_MESH.../02_checkMesh_Output.md` | 30 min | Interpret results |
| 3 | `05_MESH.../03_Mesh_Improvement.md` | 60 min | Fixing issues |
| 4 | **Debug Session** | 60 min | Fix real case |

## Quick Reference

### blockMesh Structure

```cpp
vertices
(
    (0 0 0)     // vertex 0
    (1 0 0)     // vertex 1
    ...
);

blocks
(
    hex (0 1 2 3 4 5 6 7)  // vertex order
    (10 10 1)              // cells (x y z)
    simpleGrading (1 1 1)  // grading
);

boundary
(
    inlet { type patch; faces ((0 4 7 3)); }
    ...
);
```

### snappyHexMesh Workflow

```mermaid
flowchart LR
    A[Background Mesh] --> B[Castellated Mesh]
    B --> C[Snapped Mesh]
    C --> D[Layer Addition]
```

| Step | Dict Key | Purpose |
|------|----------|---------|
| 1 | `castellatedMeshControls` | Cell removal/refinement |
| 2 | `snapControls` | Surface snapping |
| 3 | `addLayersControls` | Boundary layers |

### Mesh Quality Criteria

| Metric | Good | Acceptable | Bad |
|--------|------|------------|-----|
| Non-orthogonality | < 40° | 40-65° | > 70° |
| Skewness | < 2 | 2-4 | > 4 |
| Aspect ratio | < 100 | 100-1000 | > 1000 |

### checkMesh Commands

```bash
# Basic check
checkMesh

# Full quality check
checkMesh -allGeometry -allTopology

# Write bad cells for visualization
checkMesh -writeSets

# Check specific time
checkMesh -time 0.5
```

## Common Mistakes

| Mistake | Consequence | Fix |
|---------|-------------|-----|
| Wrong vertex order | Negative volume | Follow RH rule |
| No background mesh | snappy fails | blockMesh first |
| Too fine base mesh | Slow/crash | Start coarse |
| Missing STL closure | Leaky geometry | Check STL in CAD |
| Wrong locationInMesh | Inside geometry | Move outside |

## Reference File

See `references/mesh_commands.md` for complete command cheat sheet.
