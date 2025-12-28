# Mesh Classes - Common Pitfalls

ปัญหาที่พบบ่อยกับ Mesh Classes — เรียนจากความผิดพลาดของคนอื่น

> **ทำไมบทนี้สำคัญ?**
> - **ป้องกัน bugs ที่หายาก** — mesh errors มักจับยาก
> - รู้ **traps ที่พบบ่อย** → หลีกเลี่ยงได้
> - Debug เร็วขึ้นเมื่อเจอ mesh-related errors

---

## 1. Face Indexing Errors

### Problem: Accessing Non-existent Neighbour

```cpp
// BAD: boundary face has no neighbour
forAll(mesh.faceNeighbour(), faceI)
{
    label n = mesh.faceNeighbour()[faceI];  // OK for internal only
}

// GOOD: Check face type
if (faceI < mesh.nInternalFaces())
{
    label n = mesh.faceNeighbour()[faceI];
}
else
{
    // Boundary face - only owner exists
}
```

---

## 2. Boundary vs Internal Faces

### Problem: Wrong Index Range

```cpp
// Internal faces: 0 to nInternalFaces()-1
for (label f = 0; f < mesh.nInternalFaces(); f++) { ... }

// Boundary faces: nInternalFaces() to nFaces()-1
for (label f = mesh.nInternalFaces(); f < mesh.nFaces(); f++) { ... }

// All faces
forAll(mesh.faces(), faceI) { ... }
```

---

## 3. Patch Index Confusion

### Problem: Hardcoding Patch Indices

```cpp
// BAD: Hardcoded index
const fvPatch& inlet = mesh.boundary()[0];

// GOOD: Find by name
label inletI = mesh.boundaryMesh().findPatchID("inlet");
if (inletI >= 0)
{
    const fvPatch& inlet = mesh.boundary()[inletI];
}
```

---

## 4. Memory with Large Meshes

### Problem: Creating Temporary Large Arrays

```cpp
// BAD: Copies entire connectivity
labelListList myCells = mesh.cellCells();

// GOOD: Use reference
const labelListList& cc = mesh.cellCells();
```

---

## 5. Parallel Mesh Issues

### Problem: Ignoring Processor Boundaries

```cpp
// BAD: Assumes all boundary faces are physical
forAll(mesh.boundary(), patchI)
{
    // May include processor patches!
}

// GOOD: Check patch type
forAll(mesh.boundary(), patchI)
{
    if (!isA<processorFvPatch>(mesh.boundary()[patchI]))
    {
        // Physical patch
    }
}
```

---

## 6. Geometry vs Topology

### Problem: Using primitiveMesh for Geometry

```cpp
// BAD: primitiveMesh has no geometry
// const vectorField& C = mesh.cellCentres();  // Error if primitiveMesh

// GOOD: Use polyMesh/fvMesh
const fvMesh& mesh = ...;
const vectorField& C = mesh.C();  // OK
```

---

## 7. Face Orientation

### Problem: Assuming Face Normal Direction

```cpp
// Face normal points from owner to neighbour
const vectorField& Sf = mesh.Sf();

// For cell cellI and face faceI:
if (mesh.faceOwner()[faceI] == cellI)
{
    // Normal points outward
    outwardFlux += phi[faceI];
}
else
{
    // Normal points inward
    outwardFlux -= phi[faceI];
}
```

---

## 8. Mesh Modification

### Problem: Invalid Mesh After Modification

```cpp
// After mesh changes, must update dependent data
mesh.movePoints(newPoints);
mesh.updateMesh(topoChange);

// Fields must be mapped
T.map(newMesh);
```

---

## Quick Troubleshooting

| Problem | Check |
|---------|-------|
| Index out of range | Internal vs boundary face |
| Wrong patch | Use findPatchID |
| Parallel errors | Check processor patches |
| Memory issues | Use references |
| Geometry missing | Use fvMesh not primitiveMesh |

---

## 🧠 Concept Check

<details>
<summary><b>1. ทำไม boundary face ไม่มี neighbour?</b></summary>

เพราะ **boundary face อยู่ขอบ mesh** — มีแค่ cell เดียว (owner)
</details>

<details>
<summary><b>2. processor patch คืออะไร?</b></summary>

**Patch ระหว่าง processors** ใน parallel run — ไม่ใช่ physical boundary
</details>

<details>
<summary><b>3. face normal ชี้ทิศไหน?</b></summary>

**จาก owner ไป neighbour** สำหรับ internal faces
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Mesh Hierarchy:** [02_Mesh_Hierarchy.md](02_Mesh_Hierarchy.md)