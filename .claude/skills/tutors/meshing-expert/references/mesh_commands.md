# OpenFOAM Mesh Commands Cheat Sheet

Quick reference for meshing commands and utilities.

## Mesh Generation

| Command | Purpose | Example |
|---------|---------|---------|
| `blockMesh` | Generate from blockMeshDict | `blockMesh` |
| `snappyHexMesh` | Complex geometry meshing | `snappyHexMesh -overwrite` |
| `foamyHexMesh` | Voronoi-based meshing | `foamyHexMesh` |
| `extrudeMesh` | 2D to 3D extrusion | `extrudeMesh` |

## Mesh Quality

| Command | Purpose | Example |
|---------|---------|---------|
| `checkMesh` | Basic quality check | `checkMesh` |
| `checkMesh -allGeometry` | Full geometry check | `checkMesh -allGeometry` |
| `checkMesh -allTopology` | Full topology check | `checkMesh -allTopology` |
| `checkMesh -writeSets` | Write bad cells | `checkMesh -writeSets vtk` |

## Mesh Manipulation

| Command | Purpose | Example |
|---------|---------|---------|
| `transformPoints` | Scale, rotate, translate | `transformPoints -scale '(0.001 0.001 0.001)'` |
| `renumberMesh` | Optimize bandwidth | `renumberMesh -overwrite` |
| `refineMesh` | Uniform refinement | `refineMesh -overwrite` |
| `topoSet` | Create cell/face sets | `topoSet` |
| `subsetMesh` | Extract mesh subset | `subsetMesh myZone` |
| `mergeMeshes` | Combine meshes | `mergeMeshes . ../otherCase` |
| `stitchMesh` | Join separate regions | `stitchMesh patch1 patch2` |
| `createPatch` | Modify boundary patches | `createPatch -overwrite` |

## Mesh Conversion

| Command | Purpose | Example |
|---------|---------|---------|
| `fluentMeshToFoam` | Fluent to OpenFOAM | `fluentMeshToFoam mesh.msh` |
| `gmshToFoam` | Gmsh to OpenFOAM | `gmshToFoam mesh.msh` |
| `ideasUnvToFoam` | IDEAS to OpenFOAM | `ideasUnvToFoam mesh.unv` |
| `starToFoam` | Star-CD to OpenFOAM | `starToFoam mesh` |
| `foamToVTK` | Export to VTK | `foamToVTK` |

## Parallel Meshing

| Command | Purpose | Example |
|---------|---------|---------|
| `decomposePar` | Decompose for parallel | `decomposePar` |
| `reconstructParMesh` | Reconstruct mesh only | `reconstructParMesh -constant` |
| `redistributePar` | Redistribute mesh | `redistributePar -decompose` |

## STL/Surface Tools

| Command | Purpose | Example |
|---------|---------|---------|
| `surfaceCheck` | Check STL quality | `surfaceCheck geometry.stl` |
| `surfaceConvert` | Convert formats | `surfaceConvert in.stl out.obj` |
| `surfaceTransformPoints` | Transform surface | `surfaceTransformPoints -scale '(...)' in.stl out.stl` |
| `surfaceFeatureExtract` | Extract features | `surfaceFeatureExtract` |

## Quality Metrics Reference

### Non-orthogonality

| Range | Status | Action |
|-------|--------|--------|
| 0-40° | Excellent | None needed |
| 40-65° | Acceptable | Monitor |
| 65-70° | Poor | Add nNonOrthCorr |
| >70° | Critical | Remesh |

### Aspect Ratio

| Range | Status |
|-------|--------|
| 1-100 | Good |
| 100-1000 | Acceptable |
| >1000 | May cause issues |

### Skewness

| Range | Status |
|-------|--------|
| 0-2 | Good |
| 2-4 | Acceptable |
| >4 | Problematic |

## Common Flags

| Flag | Purpose |
|------|---------|
| `-overwrite` | Replace existing mesh |
| `-dict <file>` | Use alternative dict |
| `-time <time>` | Operate on specific time |
| `-constant` | Operate on constant directory |
| `-parallel` | Run in parallel |
