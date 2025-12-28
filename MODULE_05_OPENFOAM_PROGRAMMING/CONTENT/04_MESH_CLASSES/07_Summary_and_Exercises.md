# Mesh Classes - Summary and Exercises

สรุปและแบบฝึกหัด — ฝึกทำเพื่อเข้าใจจริง

> **ทำไมต้องทำ Exercises?**
> - อ่านอย่างเดียวไม่พอ — **ต้องเขียน code เอง**
> - ฝึก access mesh data จนคล่อง
> - เตรียมพร้อมสำหรับ real solver development

---

## Summary

### Class Hierarchy

| Class | Purpose |
|-------|---------|
| `primitiveMesh` | Topology |
| `polyMesh` | + Geometry |
| `fvMesh` | + FV methods |

### Key Methods

| Method | Returns |
|--------|---------|
| `nCells()` | Number of cells |
| `nFaces()` | Number of faces |
| `nPoints()` | Number of vertices |
| `nInternalFaces()` | Internal face count |

---

## Exercise 1: Basic Mesh Info

```cpp
Info << "Mesh statistics:" << endl;
Info << "  Cells: " << mesh.nCells() << endl;
Info << "  Faces: " << mesh.nFaces() << endl;
Info << "  Internal faces: " << mesh.nInternalFaces() << endl;
Info << "  Boundary faces: " << mesh.nFaces() - mesh.nInternalFaces() << endl;
Info << "  Points: " << mesh.nPoints() << endl;
```

---

## Exercise 2: Cell Geometry

```cpp
// Get cell centers and volumes
const vectorField& C = mesh.C();
const scalarField& V = mesh.V();

// Find largest cell
label maxCell = 0;
scalar maxVol = 0;
forAll(V, cellI)
{
    if (V[cellI] > maxVol)
    {
        maxVol = V[cellI];
        maxCell = cellI;
    }
}

Info << "Largest cell: " << maxCell << " volume: " << maxVol << endl;
```

---

## Exercise 3: Face Connectivity

```cpp
// Loop over internal faces
for (label faceI = 0; faceI < mesh.nInternalFaces(); faceI++)
{
    label owner = mesh.faceOwner()[faceI];
    label neighbour = mesh.faceNeighbour()[faceI];
    
    // Face connects owner and neighbour
}

// Loop over boundary faces
for (label faceI = mesh.nInternalFaces(); faceI < mesh.nFaces(); faceI++)
{
    label owner = mesh.faceOwner()[faceI];
    // Only owner exists for boundary faces
}
```

---

## Exercise 4: Patch Access

```cpp
const fvBoundaryMesh& boundary = mesh.boundary();

forAll(boundary, patchI)
{
    const fvPatch& patch = boundary[patchI];
    
    Info << "Patch: " << patch.name()
         << " faces: " << patch.size()
         << " type: " << patch.type() << endl;
}

// Find specific patch
label inletI = mesh.boundaryMesh().findPatchID("inlet");
if (inletI >= 0)
{
    const fvPatch& inlet = mesh.boundary()[inletI];
}
```

---

## Exercise 5: Cell-Cell Connectivity

```cpp
// Get all neighbours of a cell
const labelListList& cc = mesh.cellCells();

label cellI = 100;
const labelList& neighbours = cc[cellI];

Info << "Cell " << cellI << " has " << neighbours.size() << " neighbours" << endl;
```

---

## Quick Reference

| Connectivity | Method |
|--------------|--------|
| Face→Owner | `faceOwner()[f]` |
| Face→Neighbour | `faceNeighbour()[f]` |
| Cell→Faces | `cells()[c]` |
| Cell→Cells | `cellCells()[c]` |
| Point→Cells | `pointCells()[p]` |

---

## 🧠 Concept Check

<details>
<summary><b>1. Internal vs boundary face ต่างกันอย่างไร?</b></summary>

- **Internal**: มี 2 cells (owner + neighbour)
- **Boundary**: มี 1 cell (owner only)
</details>

<details>
<summary><b>2. หา patch ID อย่างไร?</b></summary>

```cpp
label patchI = mesh.boundaryMesh().findPatchID("patchName");
```
</details>

<details>
<summary><b>3. face normal ชี้ทิศไหน?</b></summary>

**จาก owner ไป neighbour** สำหรับ internal faces
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **fvMesh:** [05_fvMesh.md](05_fvMesh.md)