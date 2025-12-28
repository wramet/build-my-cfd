# polyMesh: โครงสร้างและการจัดการโทโพโลยี

ข้อมูลหลักของ Mesh ใน OpenFOAM — Topology + Geometry

> **ทำไมต้องรู้ polyMesh?**
> - **เก็บ geometry จริง** (points, faces, cells)
> - เข้าใจ **owner-neighbour convention** → ใช้ flux ถูก
> - รู้จัก **patch types** → ตั้ง BC ได้ถูก

---

## Overview

> **💡 polyMesh = primitiveMesh + Coordinates**
>
> - `primitiveMesh`: "Face 5 เชื่อม cell 0 กับ cell 1"
> - `polyMesh`: + "Face 5 อยู่ที่ (0.5, 0.5, 0) พื้นที่ 0.01 m²"

---

## Directory Structure

```
constant/polyMesh/
├── points          # พิกัด vertices
├── faces           # face-vertex connectivity
├── owner           # owner cell per face
├── neighbour       # neighbour cell (internal faces)
└── boundary        # patch definitions
```

---

## Directory Structure

```
constant/polyMesh/
├── points          # พิกัด vertices
├── faces           # face-vertex connectivity
├── owner           # owner cell per face
├── neighbour       # neighbour cell (internal faces)
└── boundary        # patch definitions
```

---

## Core Data Structures

### Points

```cpp
const pointField& points = mesh.points();
// points[i] = (x, y, z) coordinates of vertex i
```

### Faces

```cpp
const faceList& faces = mesh.faces();
// faces[i] = list of vertex indices forming face i
```

### Owner/Neighbour

```cpp
const labelList& owner = mesh.faceOwner();
const labelList& neighbour = mesh.faceNeighbour();

// For internal face f:
// owner[f] = cell on one side
// neighbour[f] = cell on other side

// For boundary face f:
// owner[f] = adjacent cell
// neighbour[f] = -1 (no neighbour)
```

### Cells

```cpp
const cellList& cells = mesh.cells();
// cells[i] = list of face indices forming cell i
```

### Boundary Patches

```cpp
const polyBoundaryMesh& boundary = mesh.boundaryMesh();

forAll(boundary, patchi)
{
    const polyPatch& patch = boundary[patchi];
    Info << patch.name() << ": " << patch.type() << endl;
}
```

---

## Owner-Neighbour Convention

```
Cell 1 (owner)  ──face──>  Cell 2 (neighbour)
                  ↑
            Normal points
           owner → neighbour
```

**Rules:**
- Face normal always points from **owner to neighbour**
- Owner index < neighbour index (for internal faces)
- Boundary faces have **no neighbour** (= -1)

**Impact on flux calculations:**
- Positive flux = flow in normal direction (owner → neighbour)
- Negative flux = flow against normal (neighbour → owner)

---

## Patch Types

| Type | Math Condition | Use |
|------|----------------|-----|
| `wall` | u = 0 (no-slip) | Solid boundaries |
| `patch` | Generic | Inlet, outlet |
| `symmetryPlane` | u·n = 0 | Mirror symmetry |
| `cyclic` | φ_master = φ_slave | Periodic domains |
| `empty` | ∂/∂z = 0 | 2D simulations |
| `wedge` | Axisymmetric | Rotational symmetry |

---

## Geometric Quantities

```cpp
// Face area vectors (Sf = area × normal)
const vectorField& Sf = mesh.Sf();

// Unit normals
const vectorField& nf = mesh.Sf() / mesh.magSf();

// Face areas
const scalarField& magSf = mesh.magSf();

// Cell volumes
const scalarField& V = mesh.V();

// Cell centers
const vectorField& C = mesh.C();
```

---

## Mesh Quality Checks

```bash
checkMesh
```

| Metric | Target | Impact |
|--------|--------|--------|
| Non-orthogonality | < 70° | Diffusion accuracy |
| Skewness | < 2-4 | Interpolation |
| Aspect ratio | < 100 | Convergence |

---

## Mesh Creation Tools

### blockMesh (Structured)

```cpp
// system/blockMeshDict
vertices ((0 0 0) (1 0 0) ... );
blocks (hex (0 1 2 3 4 5 6 7) (20 20 20) simpleGrading (1 1 1));
boundary
(
    inlet { type patch; faces ((0 4 7 3)); }
    outlet { type patch; faces ((1 2 6 5)); }
    walls { type wall; faces (...); }
);
```

### snappyHexMesh (Complex geometry)

```cpp
// system/snappyHexMeshDict
geometry { myGeometry.stl { type triSurfaceMesh; } }
castellatedMesh true;
addLayers true;
```

---

## FVM Connection

### Divergence Calculation

$$(\nabla \cdot \mathbf{u})_i = \frac{1}{V_i} \sum_f (\mathbf{u} \cdot \mathbf{S})_f$$

```cpp
// Using owner-neighbour convention
forAll(mesh.owner(), facei) {
    divU[own[facei]] += phi[facei];
    divU[nei[facei]] -= phi[facei];  // Opposite sign
}
```

### Laplacian Discretization

$$\nabla \cdot (\Gamma \nabla \phi) \approx \sum_f \Gamma_f \frac{\phi_N - \phi_P}{d_{PN}} A_f$$

---

## Common Pitfalls

| Problem | Cause | Solution |
|---------|-------|----------|
| Wrong flux sign | Face orientation | Check owner/neighbour |
| Solver diverges | High non-orthogonality | Add correctors, use limitedLinear |
| Missing faces | Incomplete boundary | Check `checkMesh` output |
| Parallel fails | Processor boundary | Check decomposition |

---

## 🧠 Concept Check

<details>
<summary><b>1. Owner-neighbour convention มีผลอย่างไร?</b></summary>

กำหนดทิศทางของ face normal (owner → neighbour) ซึ่งกำหนดเครื่องหมายของ flux — positive = ไหลจาก owner ไป neighbour
</details>

<details>
<summary><b>2. Boundary faces ต่างจาก internal faces อย่างไร?</b></summary>

- **Internal**: มีทั้ง owner และ neighbour cells
- **Boundary**: มีแค่ owner (neighbour = -1) และ face normal ชี้ออกนอก domain
</details>

<details>
<summary><b>3. ทำไม checkMesh สำคัญ?</b></summary>

ตรวจสอบ topology (connectivity) และ geometry (quality metrics) — mesh ที่ผิดจะทำให้ solver ไม่เสถียรหรือ diverge
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [03_primitiveMesh.md](03_primitiveMesh.md)
- **บทถัดไป:** [05_fvMesh.md](05_fvMesh.md)