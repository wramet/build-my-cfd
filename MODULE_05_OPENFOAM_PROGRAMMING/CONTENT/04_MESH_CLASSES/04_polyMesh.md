# polyMesh: โครงสร้างและการจัดการโทโพโลยี

ข้อมูลหลักของ Mesh ใน OpenFOAM — Topology + Geometry

> **ทำไมต้องรู้ polyMesh?**
> - **เก็บ geometry จริง** (points, faces, cells)
> - เข้าใจ **owner-neighbour convention** → ใช้ flux ถูก
> - รู้จัก **patch types** → ตั้ง BC ได้ถูก

---

## Learning Objectives

หลังจากอ่านบทนี้ คุณจะสามารถ:
- เข้าใจความแตกต่างระหว่าง `primitiveMesh` (topology) และ `polyMesh` (topology + geometry)
- อธิบาย **owner-neighbour convention** และผลต่อการคำนวณ flux
- ระบุและใช้งาน **patch types** ที่เหมาะสมกับสถานการณ์ต่างๆ
- อ่านและแปลความหมายไฟล์ mesh ใน `constant/polyMesh/`
- เชื่อมโยง mesh structure กับ finite volume discretization
- ตรวจสอบและวินิจฉัยปัญหา mesh quality

---

## Prerequisites

- **บทก่อนหน้า:** [03_primitiveMesh.md](03_primitiveMesh.md) — เข้าใจ topology และ face-cell connectivity
- **ความรู้พื้นฐาน:** Finite Volume Method basics (FVM ใช้ face-based discretization)
- **ขณะอ่าน:** เปิด mesh case ตัวอย่างและตรวจสอบไฟล์ใน `constant/polyMesh/`

---

## Overview

> **💡 polyMesh = primitiveMesh + Coordinates**
>
> - `primitiveMesh`: "Face 5 เชื่อม cell 0 กับ cell 1" ← **Topology**
> - `polyMesh`: + "Face 5 อยู่ที่ (0.5, 0.5, 0) พื้นที่ 0.01 m²" ← **Geometry**

```
primitiveMesh (Topology)          polyMesh (Topology + Geometry)
┌─────────────────────┐           ┌──────────────────────────────┐
│ faces, cells        │    +      │ points, face centres, Sf    │
│ owner, neighbour    │    =      │ cell volumes, mesh quality  │
└─────────────────────┘           └──────────────────────────────┘
```

**polyMesh** คือ class หลักที่ใช้เก็บข้อมูล mesh แบบ **polyhedral** (หลายหน้า) โดยรวม:
- **Topology**: การเชื่อมต่อระหว่าง elements (faces, cells, connectivity)
- **Geometry**: ตำแหน่งจริงใน space (points, areas, volumes)

---

## Directory Structure

```
constant/polyMesh/
├── points          # พิกัด vertices (x, y, z)
├── faces           # face-vertex connectivity
├── owner           # owner cell per face
├── neighbour       # neighbour cell (internal faces only)
├── boundary        # patch definitions
├── cellZones       # (optional) cell groupings
├── faceZones       # (optional) face groupings
├── pointZones      # (optional) point groupings
└── sets/           # (optional) cell/face/point sets
```

---

## Mesh File Formats

### 1. points

ไฟล์เก็บพิกัด vertices ทั้งหมดใน mesh:

```
/*
    dimensions      [0 1 0 0 0 0 0];  // Length (meters)
    internalField   nonuniform List<vector> <number_of_points>;
    (
        (0 0 0)           // Vertex 0
        (1 0 0)           // Vertex 1
        (1 1 0)           // Vertex 2
        (0 1 0)           // Vertex 3
        ...
    )
*/
```

**ใน C++ code:**
```cpp
const pointField& points = mesh.points();
forAll(points, i) {
    Info << "Point " << i << ": " << points[i] << endl;
    // points[i] = vector(x, y, z)
}
```

---

### 2. faces

ไฟล์เก็บ vertex connectivity สำหรับแต่ละ face:

```
/*
    dimensions      [0 0 0 0 0 0 0];
    internalField   nonuniform List<face> <number_of_faces>;
    (
        4(0 1 5 4)    // Face 0: quadrilateral with vertices 0-1-5-4
        4(1 2 6 5)    // Face 1: vertices 1-2-6-5
        3(0 1 2)      // Face 2: triangular face
        ...
    )
*/
```

**หมายเหตุ:**
- Vertex จัดเรียง **counter-clockwise** เมื่อมองจาก owner cell
- Face normal ชี้จาก owner → neighbour (ดู Section: Owner-Neighbour Convention)

**ใน C++ code:**
```cpp
const faceList& faces = mesh.faces();
forAll(faces, facei) {
    const face& f = faces[facei];
    Info << "Face " << facei << " has " << f.size() << " vertices" << endl;
    // f[0], f[1], ... = vertex indices
}
```

---

### 3. owner

ไฟล์เก็บ owner cell index สำหรับทุก face:

```
/*
    dimensions      [0 0 0 0 0 0 0];
    internalField   nonuniform List<label> <number_of_faces>;
    (
        0    // Face 0 owned by cell 0
        0    // Face 1 owned by cell 0
        1    // Face 2 owned by cell 1
        ...
    )
*/
```

**ใน C++ code:**
```cpp
const labelList& owner = mesh.faceOwner();
label ownCell = owner[facei];  // Owner cell of face 'facei'
```

---

### 4. neighbour

ไฟล์เก็บ neighbour cell index **เฉพาะ internal faces**:

```
/*
    dimensions      [0 0 0 0 0 0 0];
    internalField   nonuniform List<label> <number_of_internal_faces>;
    (
        1    // Face 0 between cell 0 (owner) and cell 1 (neighbour)
        2    // Face 1 between cell 0 (owner) and cell 2 (neighbour)
        ...
    )
*/
```

**หมายเหตุ:**
- Boundary faces **ไม่มี** neighbour (neighbour = -1)
- ขนาดไฟล์ neighbour < ขนาดไฟล์ owner (เพราะไม่รวม boundary faces)

**ใน C++ code:**
```cpp
const labelList& neighbour = mesh.faceNeighbour();
if (neighbour[facei] != -1) {
    // Internal face
    label ownCell = owner[facei];
    label neiCell = neighbour[facei];
} else {
    // Boundary face
}
```

---

### 5. boundary

ไฟล์เก็บ patch definitions ทั้งหมด:

```
/*
    dimensions      [0 0 0 0 0 0 0];
    internalField   nonuniform List<entry> <number_of_patches>;
    (
        inlet
        {
            type            patch;
            nFaces          50;
            startFace       2400;
        }
        
        outlet
        {
            type            patch;
            nFaces          50;
            startFace       2450;
        }
        
        walls
        {
            type            wall;
            inGroups        1(wall);
            nFaces          200;
            startFace       2500;
        }
    )
*/
```

**คำอธิบาย fields:**
- `type`: ประเภทของ boundary patch (ดู Section: Patch Types)
- `nFaces`: จำนวน faces ใน patch นี้
- `startFace`: Index ของ face แรกใน patch (global face index)

**ใน C++ code:**
```cpp
const polyBoundaryMesh& boundary = mesh.boundaryMesh();
forAll(boundary, patchi) {
    const polyPatch& patch = boundary[patchi];
    Info << "Patch " << patch.name() 
         << " (type=" << patch.type() << ")" 
         << " has " << patch.size() << " faces" << endl;
}
```

---

### 6. Optional Zone Files

**cellZones** — กลุ่ม cells สำหรับการจัดการพิเศษ:
```
/*
    dimensions      [0 0 0 0 0 0 0];
    internalField   nonuniform List<labelList> <number_of_zones>;
    (
        rotatingZone
        (
            0 1 2 3 4 5  // Cell indices in this zone
        )
    )
*/
```

**faceZones** — กลุ่ม faces สำหรับ boundary conditions พิเศษ:
```
/*
    dimensions      [0 0 0 0 0 0 0];
    internalField   nonuniform List<labelList> <number_of_zones>;
    (
        cyclicFaces
        (
            100 101 102  // Face indices in this zone
        )
    )
*/
```

**ใน C++ code:**
```cpp
// Access cell zones
const cellZoneMesh& zones = mesh.cellZones();
forAll(zones, zonei) {
    const cellZone& zone = zones[zonei];
    Info << "Zone " << zone.name() << " has " << zone.size() << " cells" << endl;
    
    // Iterate over cells in zone
    forAll(zone, celli) {
        label globalCelli = zone[celli];
        // Process cell...
    }
}
```

---

## Core Data Structures

### Accessing Mesh Data

```cpp
// Get references to core mesh data
const pointField& points = mesh.points();
const faceList& faces = mesh.faces();
const cellList& cells = mesh.cells();
const labelList& owner = mesh.faceOwner();
const labelList& neighbour = mesh.faceNeighbour();
const polyBoundaryMesh& boundary = mesh.boundaryMesh();

// Iterate over all internal faces
forAll(owner, facei) {
    if (mesh.isInternalFace(facei)) {
        label ownCell = owner[facei];
        label neiCell = neighbour[facei];
        // Process internal face...
    }
}

// Iterate over boundary patches
forAll(boundary, patchi) {
    const polyPatch& patch = boundary[patchi];
    forAll(patch, facei) {
        label globalFacei = patch.start() + facei;
        // Process boundary face...
    }
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
1. Face normal ชี้เสมอจาก **owner → neighbour**
2. Owner index < neighbour index (สำหรับ internal faces)
3. Boundary faces มีแค่ **owner** (neighbour = -1)
4. Face normal ของ boundary ชี้ **ออกนอก domain**

**ผลต่อ flux calculations:**
- **Positive flux** = flow ในทิศทาง normal (owner → neighbour)
- **Negative flux** = flow ทิศทางตรงข้าม (neighbour → owner)

**ตัวอย่าง:**
```cpp
// Divergence calculation using owner-neighbour convention
scalarField divU(mesh.nCells(), Zero);

forAll(mesh.owner(), facei) {
    scalar flux = phi[facei];  // Mass/volume flux through face
    
    if (mesh.isInternalFace(facei)) {
        label own = mesh.owner()[facei];
        label nei = mesh.neighbour()[facei];
        
        divU[own] += flux;   // +flux for owner (normal points out)
        divU[nei] -= flux;   // -flux for neighbour (normal points in)
    } else {
        // Boundary face: flux is added to owner only
        label own = mesh.owner()[facei];
        divU[own] += flux;
    }
}
```

---

## Patch Types

### Complete Reference Table

| Type | Math Condition | Use Case | Example |
|------|----------------|----------|---------|
| `patch` | Generic | Inlet, outlet, generic BC | `inlet { type patch; }` |
| `wall` | **u = 0** (no-slip) | Solid boundaries | `walls { type wall; }` |
| `symmetryPlane` | **u·n = 0** | Mirror symmetry | `symmetry { type symmetryPlane; }` |
| `cyclic` | **φ_master = φ_slave** | Periodic domains | `periodic { type cyclic; }` |
| `cyclicAMI` | **φ₁ = AMI(φ₂)** | Non-conformal periodic | `rotorStator { type cyclicAMI; }` |
| `empty` | **∂/∂z = 0** | 2D simulations | `frontAndBack { type empty; }` |
| `wedge` | Axisymmetric | Rotational symmetry | `axis { type wedge; }` |
| `processor` | Parallel domain | Decomposition boundaries | `procBoundary0to1 { type processor; }` |

### Practical Examples

**Example 1: Channel Flow**
```cpp
// system/blockMeshDict
boundary
(
    inlet
    {
        type patch;
        faces ((0 4 7 3));
    }
    
    outlet
    {
        type patch;
        faces ((1 2 6 5));
    }
    
    walls
    {
        type wall;
        faces ((0 1 5 4) (3 2 6 7));
    }
    
    frontAndBack
    {
        type empty;  // 2D simulation
        faces ((0 1 2 3) (4 5 6 7));
    }
)
```

**Example 2: Periodic Domain (Cyclic)**
```cpp
boundary
(
    periodicLeft
    {
        type cyclic;
        neighbourPatch periodicRight;
        faces ((0 4 7 3));
    }
    
    periodicRight
    {
        type cyclic;
        neighbourPatch periodicLeft;
        faces ((1 2 6 5));
    }
)
```

**Example 3: Rotor-Stator Interface (CyclicAMI)**
```cpp
boundary
(
    rotorSide
    {
        type cyclicAMI;
        neighbourPatch statorSide;
        AMIInterpolation 
        {
            type                nearestPatch;
            interpolationMethod cellPointWeight;
        }
        faces (...);
    }
    
    statorSide
    {
        type cyclicAMI;
        neighbourPatch rotorSide;
        faces (...);
    }
)
```

**Example 4: Axisymmetric (Wedge)**
```cpp
// For axisymmetric simulations (typically 5° wedge)
boundary
(
    axis
    {
        type symmetryPlane;
        faces ((0 1 2 3));
    }
    
    wedge1
    {
        type wedge;
        faces ((0 4 7 3));
    }
    
    wedge2
    {
        type wedge;
        faces ((1 5 6 2));
    }
)
```

### Patch Type Selection Flowchart

```
              Is wall boundary?
                 /      \
               Yes       No
               /          \
          type wall   Is periodic?
                      /    \
                    Yes     No
                    /        \
           type cyclic    Is 2D?
                              /    \
                            Yes     No
                            /        \
                       type empty   type patch
```

---

## Geometric Quantities

### Built-in Access Functions

```cpp
// Face area vectors (Sf = area × normal)
const surfaceVectorField& Sf = mesh.Sf();
// Sf[facei] = vector pointing in normal direction with magnitude = face area

// Unit face normals
const surfaceVectorField& nf = mesh.Sf() / mesh.magSf();
// nf[facei] = unit normal vector (|nf| = 1)

// Face areas (magnitude)
const surfaceScalarField& magSf = mesh.magSf();
// magSf[facei] = face area in m²

// Cell volumes
const volScalarField& V = mesh.V();
// V[celli] = cell volume in m³

// Cell centers
const volVectorField& C = mesh.C();
// C[celli] = (x, y, z) coordinate of cell center

// Face centers
const surfaceVectorField& Cf = mesh.Cf();
// Cf[facei] = (x, y, z) coordinate of face center
```

### Practical Usage Examples

**Calculate Face-to-Cell-Center Distance**
```cpp
forAll(mesh.owner(), facei) {
    label ownCell = mesh.owner()[facei];
    vector ownC = mesh.C()[ownCell];
    vector faceC = mesh.Cf()[facei];
    scalar dOwn = mag(faceC - ownC);  // Distance from owner to face
    
    if (mesh.isInternalFace(facei)) {
        label neiCell = mesh.neighbour()[facei];
        vector neiC = mesh.C()[neiCell];
        scalar dNei = mag(faceC - neiC);  // Distance from neighbour to face
        scalar dPN = dOwn + dNei;  // Total owner-neighbour distance
        
        Info << "Face " << facei 
             << ": dOwn=" << dOwn 
             << ", dNei=" << dNei 
             << ", dPN=" << dPN << endl;
    }
}
```

**Find Cells with Small Volumes (Quality Check)**
```cpp
const volScalarField& V = mesh.V();
scalar minVol = GREAT;
scalar maxVol = -GREAT;
label minCelli = -1;
label maxCelli = -1;

forAll(V, celli) {
    if (V[celli] < minVol) {
        minVol = V[celli];
        minCelli = celli;
    }
    if (V[celli] > maxVol) {
        maxVol = V[celli];
        maxCelli = celli;
    }
}

Info << "Cell volume range: " << minVol << " (cell " << minCelli 
     << ") to " << maxVol << " (cell " << maxCelli << ")" << endl;

// Warn if volumes are suspiciously small
if (minVol < SMALL) {
    WarningIn("main()")
        << "Cell " << minCelli << " has very small volume: " << minVol
        << endl;
}
```

**Verify Face Normal Consistency**
```cpp
// Check that face normals point from owner to neighbour
const surfaceVectorField& Sf = mesh.Sf();
const labelList& owner = mesh.faceOwner();
const labelList& neighbour = mesh.faceNeighbour();

forAll(owner, facei) {
    if (mesh.isInternalFace(facei)) {
        label own = owner[facei];
        label nei = neighbour[facei];
        
        vector d = mesh.C()[nei] - mesh.C()[own];
        vector n = Sf[facei] / mag(Sf[facei]);
        
        scalar cosAngle = (n & d) / mag(d);
        
        if (cosAngle < 0) {
            WarningIn("main()")
                << "Face " << facei << " normal may be inverted"
                << endl;
        }
    }
}
```

---

## Mesh Quality Checks

### Using checkMesh

```bash
checkMesh
```

### Key Quality Metrics

| Metric | Target | Impact | Command to Check |
|--------|--------|--------|------------------|
| **Non-orthogonality** | < 70° | Diffusion accuracy | `checkMesh -allGeometry -orthogonality` |
| **Skewness** | < 2-4 | Interpolation accuracy | `checkMesh -allGeometry -skewness` |
| **Aspect ratio** | < 100 | Convergence stability | `checkMesh -allGeometry -aspectRatio` |
| **Face weight** | > 0.01 | Matrix conditioning | `checkMesh -allTopology` |
| **Determinant** | > 0.01 | Matrix stability | `checkMesh -allTopology` |

### Example Output

```bash
# Check for specific issues
checkMesh -allGeometry -allTopology -time 0

# Example output:
Mesh OK
Overall number of cells of each type in the mesh:
hexahedra:     8000
prisms:        0
wedges:        0
pyramids:      0
tet wedges:    0
tetrahedra:    0
polyhedra:     0

Checking geometry...
    Overall domain bounding box (0 0 0) (1 1 1)
    Mesh (non-empty, non-wedge) directions (1 1 1)
    All edges aligned with or perpendicular to coordinate axes
    Non-orthogonality Max: 0 average: 0
    Skewness Max: 0 average: 0
    Coupled point location match (average 0) OK.
```

### Handling High Non-orthogonality

**Adjust Solver Settings:**

```cpp
// system/fvSolution
solvers
{
    p
    {
        solver          GAMG;
        tolerance       1e-06;
        relTol          0.01;
        smoother        GaussSeidel;
        
        // Add non-orthogonal correctors
        nCorrectors     2;  // Multiple correctors for non-ortho > 70°
    }
}

// system/fvSchemes
laplacianSchemes
{
    laplacian(nu,U)  Gauss linear corrected;  // Add 'corrected' for non-ortho
}
```

**Handling Skewness:**

```cpp
// system/fvSchemes
interpolationSchemes
{
    default linear;
}

// Use limited schemes for high skewness
gradSchemes
{
    default cellLimited Gauss linear 1;
}

divSchemes
{
    div(phi,U)  Gauss limitedLinearV 1;
}
```

---

## Mesh Creation Tools

### blockMesh (Structured Meshes)

```cpp
// system/blockMeshDict
convertToMeters 1;

vertices
(
    (0 0 0)    // 0
    (1 0 0)    // 1
    (1 1 0)    // 2
    (0 1 0)    // 3
    (0 0 1)    // 4
    (1 0 1)    // 5
    (1 1 1)    // 6
    (0 1 1)    // 7
);

blocks
(
    hex (0 1 2 3 4 5 6 7) (20 20 20) simpleGrading (1 1 1)
);

boundary
(
    inlet { type patch; faces ((0 4 7 3)); }
    outlet { type patch; faces ((1 2 6 5)); }
    walls { type wall; faces ((0 1 5 4) (1 2 6 5) (2 3 7 6) (3 0 4 7)); }
);
```

---

### snappyHexMesh (Complex Geometry)

```cpp
// system/snappyHexMeshDict
castellatedMesh true;
snap true;
addLayers true;

geometry
{
    myGeometry.stl
    {
        type triSurfaceMesh;
        name myGeometry;
    }
}

refinementSurfaces
{
    myGeometry.stl
    {
        level (2 2);  // Surface refinement level
    }
}

refinementRegions
{
    myGeometry.stl
    {
        mode inside;
        levels ((0.1 4) (0.2 3));  // Region-based refinement
    }
}

addLayersControls
{
    layers
    {
        myGeometry_stl
        {
            nSurfaceLayers 3;
        }
    }
}
```

---

## FVM Connection

### Divergence Theorem

$$(\nabla \cdot \mathbf{u})_i = \frac{1}{V_i} \sum_f (\mathbf{u} \cdot \mathbf{S})_f$$

```cpp
// Finite Volume implementation
forAll(mesh.owner(), facei) {
    scalar flux = phi[facei];  // Surface integral (u·Sf)
    
    label own = mesh.owner()[facei];
    divU[own] += flux;  // Add to owner
    
    if (mesh.isInternalFace(facei)) {
        label nei = mesh.neighbour()[facei];
        divU[nei] -= flux;  // Subtract from neighbour (opposite normal)
    }
}

// Normalize by cell volume
divU /= mesh.V();
```

---

### Laplacian Discretization

$$\nabla \cdot (\Gamma \nabla \phi) \approx \sum_f \Gamma_f \frac{\phi_N - \phi_P}{d_{PN}} A_f$$

```cpp
// Using geometric quantities from polyMesh
forAll(mesh.owner(), facei) {
    label own = mesh.owner()[facei];
    label nei = mesh.neighbour()[facei];
    
    scalar gammaF = fvc::interpolate(gamma, facei);  // Face diffusivity
    scalar magSf = mesh.magSf()[facei];              // Face area
    vector d = mesh.C()[nei] - mesh.C()[own];        // Cell-center distance
    scalar dPN = mag(d);                              // Distance magnitude
    
    scalar faceFlux = gammaF * magSf / dPN;
    
    // Add to matrix diagonal and off-diagonal
    matrix[own][own] += faceFlux;
    matrix[own][nei] -= faceFlux;
    matrix[nei][nei] += faceFlux;
    matrix[nei][own] -= faceFlux;
}
```

---

### Gradient Calculation

$$\nabla \phi_i = \frac{1}{V_i} \sum_f \phi_f \mathbf{S}_f$$

```cpp
volVectorField gradPhi(fvc::grad(phi));

// Manual implementation using polyMesh
forAll(mesh.C(), celli) {
    vector grad = Zero;
    const cell& c = mesh.cells()[celli];
    
    forAll(c, facei) {
        label globalFacei = c[facei];
        scalar phiF = fvc::interpolate(phi, globalFacei);
        vector Sf = mesh.Sf()[globalFacei];
        
        grad += phiF * Sf;
    }
    
    grad[celli] = grad / mesh.V()[celli];
}
```

---

## Common Pitfalls

| Problem | Cause | Solution | Code Check |
|---------|-------|----------|------------|
| **Wrong flux sign** | Face orientation confusion | Verify owner → neighbour direction | `Info << mesh.Sf()[facei] << endl;` |
| **Solver diverges** | High non-orthogonality | Add correctors, use `limitedLinear` | `checkMesh -orthogonality` |
| **Missing faces** | Incomplete boundary definition | Check `checkMesh` output | `checkMesh -allTopology` |
| **Parallel fails** | Processor boundary mismatch | Check `decomposePar` | `reconstructPar -latesttime` |
| **NaN values** | Zero cell volume | Check mesh quality | `checkMesh -allGeometry` |
| **Wrong BC** | Incorrect patch type | Verify patch types match physics | `ls constant/polyMesh/boundary` |

---

## Practical Example: Accessing Mesh Data

### Example 1: Calculate Cell-to-Cell Distances

```cpp
// Example: Calculate cell-to-cell distances
void calculateCellDistances(const fvMesh& mesh)
{
    const vectorField& cellCenters = mesh.C();
    const labelList& owner = mesh.faceOwner();
    const labelList& neighbour = mesh.faceNeighbour();
    
    // Store distances in a map
    Map<scalar> cellDistances;
    
    forAll(owner, facei) {
        if (mesh.isInternalFace(facei)) {
            label own = owner[facei];
            label nei = neighbour[facei];
            
            scalar distance = mag(cellCenters[nei] - cellCenters[own]);
            
            // Create a unique key for the cell pair
            label key = std::min(own, nei) * mesh.nCells() + std::max(own, nei);
            cellDistances.insert(key, distance);
        }
    }
    
    // Report statistics
    scalar minDist = GREAT;
    scalar maxDist = -GREAT;
    
    forAllConstIter(Map<scalar>, cellDistances, iter) {
        minDist = min(minDist, iter());
        maxDist = max(maxDist, iter());
    }
    
    Info << "Cell distance range: " << minDist << " to " << maxDist << endl;
}
```

### Example 2: Verify Boundary Face Consistency

```cpp
// Check that all boundary faces have correct outward normals
void checkBoundaryNormals(const fvMesh& mesh)
{
    const polyBoundaryMesh& boundary = mesh.boundaryMesh();
    const surfaceVectorField& Sf = mesh.Sf();
    
    forAll(boundary, patchi) {
        const polyPatch& patch = boundary[patchi];
        
        forAll(patch, facei) {
            label globalFacei = patch.start() + facei;
            label ownCell = mesh.owner()[globalFacei];
            
            // Vector from cell center to face center
            vector d = mesh.Cf()[globalFacei] - mesh.C()[ownCell];
            vector n = Sf[globalFacei] / mag(Sf[globalFacei]);
            
            // For boundary faces, n should point in same direction as d
            scalar cosAngle = (n & d) / mag(d);
            
            if (cosAngle < 0) {
                WarningIn("checkBoundaryNormals()")
                    << "Boundary face " << globalFacei 
                    << " on patch " << patch.name()
                    << " has inward-pointing normal" << endl;
            }
        }
    }
}
```

### Example 3: Extract Cells Near Boundary

```cpp
// Find all cells adjacent to a specific boundary patch
labelList getBoundaryAdjacentCells(const fvMesh& mesh, const word& patchName)
{
    const polyBoundaryMesh& boundary = mesh.boundaryMesh();
    label patchi = boundary.findPatchID(patchName);
    
    if (patchi == -1) {
        FatalErrorIn("getBoundaryAdjacentCells")
            << "Patch " << patchName << " not found"
            << exit(FatalError);
    }
    
    const polyPatch& patch = boundary[patchi];
    labelList adjacentCells(patch.size());
    
    forAll(patch, facei) {
        label globalFacei = patch.start() + facei;
        adjacentCells[facei] = mesh.owner()[globalFacei];
    }
    
    return adjacentCells;
}

// Usage
labelList wallCells = getBoundaryAdjacentCells(mesh, "walls");
Info << "Found " << wallCells.size() << " cells adjacent to walls" << endl;
```

---

## 🧠 Concept Check

<details>
<summary><b>1. Owner-neighbour convention มีผลอย่างไรต่อการคำนวณ flux?</b></summary>

กำหนดทิศทางของ face normal (owner → neighbour) ซึ่งกำหนดเครื่องหมายของ flux:
- **Positive flux** = flow ไปในทิศทาง normal (จาก owner ไป neighbour)
- **Negative flux** = flow ทิศทางตรงข้าม (จาก neighbour ไป owner)

ใน divergence theorem:
```cpp
divU[owner] += flux;    // เพิ่ม flux ให้ owner (normal ชี้ออก)
divU[neighbour] -= flux; // ลบ flux จาก neighbour (normal ชี้เข้า)
```
</details>

<details>
<summary><b>2. Boundary faces ต่างจาก internal faces อย่างไร?</b></summary>

| Feature | Internal Faces | Boundary Faces |
|---------|---------------|----------------|
| **Owner cell** | ✓ มี | ✓ มี |
| **Neighbour cell** | ✓ มี | ✗ ไม่มี (nei = -1) |
| **Face normal** | owner → neighbour | ชี้ออกนอก domain |
| **ไฟล์ neighbour** | รวมอยู่ | ไม่รวม |
| **Flux contribution** | ทั้ง owner และ nei | เฉพาะ owner เท่านั้น |
</details>

<details>
<summary><b>3. ทำไม checkMesh สำคัญ?</b></summary>

`checkMesh` ตรวจสอบ:
- **Topology**: connectivity, owner-neighbour consistency, unused points
- **Geometry**: non-orthogonality, skewness, aspect ratio, cell volumes

Mesh ที่มี quality ต่ำจะทำให้:
- Solver ไม่เสถียร (instability)
- การคำนวณไม่แม่นยำ (numerical diffusion)
- Diverge หรือให้ผลผิดปกติ
</details>

<details>
<summary><b>4. polyMesh ต่างจาก primitiveMesh อย่างไร?</b></summary>

- **primitiveMesh**: เก็บ **topology** เท่านั้น (faces, cells, owner, neighbour)
  - ตอบคำถาม: "Face 5 เชื่อม cell อะไรกับ cell อะไร?"
  
- **polyMesh**: เก็บ **topology + geometry** (primitiveMesh + points, areas, volumes)
  - ตอบคำถาม: "Face 5 เชื่อม cell 0 กับ 1, อยู่ที่ (x,y,z), พื้นที่ 0.01 m²"

polyMesh ใช้สำหรับ finite volume calculations (ต้องการ face areas, cell volumes, normals)
</details>

<details>
<summary><b>5. เลือก patch type อย่างไร?</b></summary>

```
Is solid boundary? → type wall
Is periodic boundary? → type cyclic / cyclicAMI
Is 2D simulation? → type empty (frontAndBack)
Is symmetry plane? → type symmetryPlane
Else → type patch (generic inlet/outlet)
```

**ตัวอย่าง:**
- ผนังท่อ → `type wall`
- รอยต่อระหว่าง rotor-stator → `type cyclicAMI`
- แกนสมมาตร (2D axisymmetric) → `type wedge`
- Inlet/outlet ทั่วไป → `type patch`
</details>

---

## Key Takeaways

- **polyMesh = primitiveMesh + Geometry** — เพิ่ม coordinates, areas, volumes ให้ topology
- **Owner-neighbour convention** กำหนดทิศทาง face normal → สำคัญมากสำหรับ flux calculations
- **Mesh files** (`points`, `faces`, `owner`, `neighbour`, `boundary`) เก็บข้อมูล topology และ geometry แบบ binary/ASCII
- **Patch types** ต้อง match กับ physical boundary conditions (`wall`, `patch`, `cyclic`, `empty`, ...)
- **Mesh quality** (non-orthogonality, skewness, aspect ratio) ส่งผลต่อ solver stability และ accuracy
- **FVM discretization** ใช้ geometric quantities จาก polyMesh (`Sf`, `magSf`, `V`, `C`) ในการคำนวณ
- **checkMesh** เป็นเครื่องมือสำคัญในการ verify mesh topology และ geometry

---

## Navigation

**บทในหมวดนี้:**
1. [01_Introduction.md](01_Introduction.md) — Introduction to Mesh Classes
2. [02_meshObject.md](02_meshObject.md) — Mesh Object Registry
3. [03_primitiveMesh.md](03_primitiveMesh.md) — Mesh Topology
4. **04_polyMesh.md** (current) — Mesh Geometry
5. [05_fvMesh.md](05_fvMesh.md) — Finite Volume Mesh

**โมดูลที่เกี่ยวข้อง:**
- **Fields Module**: `GeometricField`, `volVectorField`, `surfaceScalarField`
- **Boundary Conditions**: การใช้งาน patch types กับ field boundary conditions
- **Solver Development**: การใช้ polyMesh ใน discretization

**เอกสาร OpenFOAM:**
- [polyMesh Class Documentation](https://www.openfoam.com/documentation/guide-code/mesh/meshes/poly-mesh/)
- [User Guide: Mesh Generation](https://cfd.direct/openfoam/user-guide/v9-mesh-generation/)
- [Programmer's Guide: Mesh Description](https://cfd.direct/openfoam/programmers-guide/)

**Next Step:** อ่าน [05_fvMesh.md](05_fvMesh.md) เพื่อเรียนรู้ว่า finite volume mesh ใช้ polyMesh อย่างไรในการแก้ PDEs