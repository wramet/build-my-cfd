# บันทึกบทเรียน: OpenFOAM Meshing Mastery

**วันที่:** 28 ธันวาคม 2025

> **สิ่งที่จะได้เรียนรู้:**
> 1. เข้าใจโครงสร้าง Mesh และ Mesh Quality
> 2. สร้าง Mesh ด้วย blockMesh และ snappyHexMesh
> 3. ตรวจสอบและแก้ไขปัญหา Mesh Quality

---

## 1. ทำไม Meshing สำคัญที่สุด?

> **"A bad mesh is the root of all divergence"** — Mesh ที่แย่คือต้นเหตุของทุกความล้มเหลว

### 50%+ ของเวลางาน CFD อยู่ที่ Mesh

```
Mesh Quality กำหนดทุกอย่าง:
┌─────────────────────────────────────────────────────┐
│ Mesh ดี   → Converge เร็ว + ผลลัพธ์แม่นยำ           │
│ Mesh แย่   → Diverge หรือผลผิด แม้ solver ดีแค่ไหน  │
└─────────────────────────────────────────────────────┘
```

**ตัวอย่างผลกระทบ:**

| Mesh Quality | ผลกระทบ |
|--------------|---------|
| Non-ortho > 85° | Solver diverge 100% |
| Skewness > 4 | Accuracy ลดลงอย่างมาก |
| Negative volume | Solver crash ทันที |

---

## 2. โครงสร้าง Mesh ใน OpenFOAM

> OpenFOAM ใช้ **Finite Volume Method** — ทุกอย่างเก็บที่ **Cell Center** และคำนวณ **Flux ผ่าน Face**

### 2.1 องค์ประกอบ Mesh

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    Cell      │     │    Face      │     │    Point     │
│ (ปริมาตร)     │     │  (พื้นผิว)    │     │  (จุดยอด)    │
│              │     │              │     │              │
│ เก็บค่า p, U │──▶  │ คำนวณ Flux   │──▶  │ กำหนดรูปร่าง │
│ ที่ Center   │     │ เข้า/ออก     │     │              │
└──────────────┘     └──────────────┘     └──────────────┘
```

### 2.2 Face Types

| Type | ลักษณะ | หน้าที่ |
|------|--------|---------|
| **Internal Face** | เชื่อม 2 Cells | Flux ระหว่าง Cells |
| **Boundary Face** | อยู่ที่ขอบโดเมน | Inlet, Outlet, Wall |

### 2.3 polyMesh Structure

```
constant/polyMesh/
├── points         ← พิกัด (x, y, z) ของจุดทั้งหมด
├── faces          ← ลำดับจุดที่ประกอบเป็นหน้า
├── owner          ← Face ไหนเป็นของ Cell ไหน
├── neighbour      ← Internal Face เชื่อม Cell ใดกับใด
└── boundary       ← กำหนด patches (inlet, outlet, walls)
```

---

## 3. ประเภทของ Cell

### 3.1 Comparison Table

| Type | หน้า | ข้อดี | ข้อเสีย | สร้างด้วย |
|------|-----|-------|---------|-----------|
| **Hexahedron** | 6 สี่เหลี่ยม | แม่นยำสุด, ประหยัด Cell | สร้างยาก | blockMesh |
| **Tetrahedron** | 4 สามเหลี่ยม | สร้างง่ายอัตโนมัติ | คุณภาพต่ำ, เปลือง | Gmsh, Salome |
| **Prism** | 5 หน้า | Boundary Layer | เฉพาะทาง | snappyHexMesh layers |
| **Polyhedron** | 12-20+ หน้า | เสถียร, หลายเพื่อนบ้าน | ซับซ้อน | polyDualMesh |

### 3.2 Golden Rule

```
พยายาม Hex-dominant (> 80%) เสมอ
+ Prism layers ที่ผนัง
= คุณภาพดีที่สุด
```

### 3.3 ทำไม Hex ดีที่สุด?

**Numerical Diffusion:**
$$\Gamma_{numerical} \approx \frac{U \Delta x}{2} (1 - \cos\theta)$$

- **Hex (θ = 0°):** $\cos 0° = 1$ → Numerical diffusion = 0
- **Tet (θ สูง):** Numerical diffusion สูง → ผลลัพธ์เบลอ

**ประหยัด:**
$$1 \text{ Hex} \approx 5-6 \text{ Tets (ความแม่นยำเท่ากัน)}$$

---

## 4. blockMesh — Structured Mesh

> **ใช้เมื่อ:** รูปทรงง่าย หรือต้องการ Background Mesh สำหรับ snappyHexMesh

### 4.1 blockMeshDict Structure

```cpp
FoamFile { version 2.0; format ascii; class dictionary; object blockMeshDict; }

convertToMeters 0.001;  // mm → m

vertices
(
    (0 0 0)       // 0
    (100 0 0)     // 1
    (100 100 0)   // 2
    (0 100 0)     // 3
    (0 0 10)      // 4
    (100 0 10)    // 5
    (100 100 10)  // 6
    (0 100 10)    // 7
);

blocks
(
    hex (0 1 2 3 4 5 6 7) (20 20 1) simpleGrading (1 1 1)
);

boundary
(
    inlet  { type patch; faces ((0 4 7 3)); }
    outlet { type patch; faces ((1 2 6 5)); }
    walls  { type wall;  faces ((0 1 5 4) (3 7 6 2)); }
    frontAndBack { type empty; faces ((0 3 2 1) (4 5 6 7)); }
);
```

### 4.2 Vertex Ordering — กฎมือขวา!

```
      7───────6
     /│      /│
    4───────5 │
    │ │     │ │
    │ 3─────│─2
    │/      │/
    0───────1

แกน x₁: 0 → 1
แกน x₂: 0 → 3
แกน x₃: 0 → 4 (extrusion)
```

**ถ้าเรียงผิด:** Inside-out cells → Negative volume → Crash!

### 4.3 Grading — อัด Cell ที่ผนัง

**simpleGrading (gx gy gz):**

$$g = \frac{\text{ขนาด Cell สุดท้าย}}{\text{ขนาด Cell แรก}}$$

| ค่า g | ผลลัพธ์ | ใช้เมื่อ |
|-------|---------|---------|
| g = 1 | Uniform (เท่ากันหมด) | ทั่วไป |
| g > 1 | Cell โตขึ้นเรื่อยๆ | อัดแน่นที่ inlet |
| g < 1 | Cell เล็กลงเรื่อยๆ | อัดแน่นที่ outlet |

**ตัวอย่าง: อัดแน่นทั้งสองฝั่ง (Wall)**

```cpp
blocks
(
    hex (...) (20 20 1) simpleGrading 
    (
        ((0.5 0.5 0.25)(0.5 0.5 4))  // Two-sided grading
        1 
        1
    )
);
```

### 4.4 Edges — เส้นโค้ง

| Type | ลักษณะ | ใช้เมื่อ |
|------|--------|---------|
| **arc** | ส่วนโค้งวงกลม | ท่อโค้ง |
| **spline** | โค้งเรียบหลายจุด | Airfoil |
| **polyLine** | หักหลายท่อน | รูปทรงเหลี่ยม |

```cpp
edges
(
    arc 1 5 (1.1 0.5 0.5)  // โค้งระหว่าง vertex 1-5 ผ่านจุด
);
```

---

## 5. snappyHexMesh — Complex Geometry

> **Analogy:** ประติมากรรม LEGO
> 1. กองบล็อก (Background Mesh)
> 2. เลื่อยตัด (Castellated)
> 3. ละลายผิว (Snap)
> 4. ทาสีชั้นๆ (Layers)

### 5.1 Three-Phase Workflow

```
blockMesh → snappyHexMesh (Phase 1-2-3) → checkMesh
   │              │              │             │
   │              │              │             │
   ▼              ▼              ▼             ▼
Background    Castellated     Snapped      Quality
  Mesh          Mesh           Mesh         Check
```

### 5.2 Phase 1: Castellated (ขั้นบันได)

**เป้าหมาย:** Refine และลบ Cell ที่ไม่ต้องการ

```cpp
castellatedMesh true;

castellatedMeshControls
{
    maxLocalCells   100000;        // Cell/process
    maxGlobalCells  2000000;       // Total cells
    minRefinementCells 10;
    nCellsBetweenLevels 3;         // ความนุ่มนวลการเปลี่ยนขนาด
    
    locationInMesh (0.001 0.001 0.001);  // ⚠️ ต้องอยู่ในโซน fluid!
    
    refinementSurfaces
    {
        car { level (3 5); }       // min-max level
    }
    
    refinementRegions
    {
        box { mode inside; levels ((1e15 4)); }
    }
}
```

**⚠️ จุดตาย: locationInMesh**
- ต้อง **ไม่อยู่** บนผิว geometry
- ต้อง **ไม่อยู่** บนขอบ cell (เลี่ยง 0, 0.5, 1)
- ใช้ค่าแปลกๆ เช่น `(0.00134 0.00234 0.00534)`

### 5.3 Phase 2: Snapping (ดึงผิวเรียบ)

**เป้าหมาย:** เปลี่ยนผิว "ขั้นบันได" เป็น "เรียบ"

```cpp
snap true;

snapControls
{
    nSmoothPatch 3;           // จำนวนรอบ smooth
    tolerance 1.0;            // ค่าความคลาดเคลื่อน
    nSolveIter 30;            // รอบแก้สมการ
    nRelaxIter 5;             // รอบ relaxation
    nFeatureSnapIter 10;      // ดึงตาม feature edges
}
```

**เทคนิค:** ต้อง run `surfaceFeatureExtract` ก่อน!

```bash
# สกัด feature edges (มุมคมชัด)
surfaceFeatureExtract
```

### 5.4 Phase 3: Layer Addition (ยากที่สุด!)

**เป้าหมาย:** สร้าง Prism layers สำหรับ Boundary Layer

```cpp
addLayers true;

addLayersControls
{
    layers
    {
        "car.*"  { nSurfaceLayers 5; }
        "ground" { nSurfaceLayers 3; }
    }
    
    expansionRatio 1.3;           // อัตราขยาย layer
    finalLayerThickness 0.5;      // ความหนาชั้นนอกสุด (สัมพัทธ์)
    minThickness 0.1;             // ความหนาขั้นต่ำ
    
    // ถ้าล้มเหลว:
    nGrow 0;
    featureAngle 130;
    nRelaxIter 5;
    nSmoothSurfaceNormals 1;
    nSmoothNormals 3;
    nSmoothThickness 10;
}
```

**ทำไมล้มเหลวบ่อย?**
1. พื้นที่ไม่พอ (Mesh แน่นเกินไป)
2. มุมแหลม (Normal vectors ชนกัน)
3. ผิวคุณภาพต่ำ (Skewness สูง)

**กลยุทธ์แก้ไข:**
```
1. เริ่มด้วย expansionRatio = 1.0 (uniform)
2. ลด nSurfaceLayers ลง
3. เพิ่ม featureAngle
4. ตรวจสอบ log ว่า layer ล้มเหลวตรงไหน
```

---

## 6. Mesh Quality Metrics

> **`checkMesh` คือเพื่อนที่ดีที่สุดของคุณ**

### 6.1 Non-Orthogonality (ศัตรูตัวฉกาจ!)

**นิยาม:** มุมระหว่างเส้นเชื่อม cell centers กับ normal ของ face

$$\theta = \arccos\left(\frac{\vec{d} \cdot \vec{n}}{|\vec{d}||\vec{n}|}\right)$$

| ค่า θ | สถานะ | การแก้ไข |
|------|-------|---------|
| < 70° | ✅ ดีมาก | ไม่ต้องทำอะไร |
| 70-80° | ⚠️ พอใช้ | `nNonOrthogonalCorrectors 1` |
| 80-85° | ⚠️ แย่ | `nNonOrthogonalCorrectors 2-3` |
| > 85° | ❌ อันตราย | ต้องแก้ Mesh! |

**ใน fvSolution:**
```cpp
SIMPLE
{
    nNonOrthogonalCorrectors 2;  // เพิ่มถ้า non-ortho สูง
}
```

**ทำไมแย่?**
- Laplacian ($\nabla^2 \phi$) ต้องการ flux ตั้งฉากกับ face
- ถ้าไม่ตั้งฉาก → flux ผิด → error สะสม → diverge

### 6.2 Skewness

**นิยาม:** ระยะห่างระหว่างจุดตัดกับ centroid ของ face

| ค่า | สถานะ |
|-----|-------|
| < 2 | ✅ ดีมาก |
| 2-4 | ⚠️ พอใช้ |
| > 4 | ❌ แย่ |

**ผลกระทบ:**
- Second-order accuracy → First-order
- Interpolation error สูง

### 6.3 Aspect Ratio

**นิยาม:** ด้านยาวสุด / ด้านสั้นสุด

| บริเวณ | ค่าที่ยอมรับ |
|--------|-------------|
| Free stream | < 10-20 |
| Boundary Layer | < 1000 (ถ้าไหลขนาน) |

### 6.4 Negative Volume

**ความหมาย:** Cell กลับตะศิลา (inside-out)

**สถานะ:** ❌ Fatal Error — Solver รันไม่ได้!

**สาเหตุ:**
1. blockMesh: เรียงจุดผิดกฎมือขวา
2. snappyHexMesh: Snap ทะลุอีกฝั่ง
3. Dynamic Mesh: เคลื่อนที่จนทับกัน

---

## 7. checkMesh Workflow

### 7.1 Basic Check

```bash
checkMesh
# ดูผลลัพธ์:
# - Mesh OK ✅
# - ***Problem with face xxx*** ❌
```

### 7.2 Detailed Check

```bash
checkMesh -allGeometry -allTopology

# สร้าง CellSets:
# - nonOrthoFaces
# - skewFaces
# - negativeVolumeCells
```

### 7.3 Visualize Problems

```bash
# แปลงเป็น VTK
foamToVTK -cellSet nonOrthoFaces

# เปิด ParaView
paraview constant/polyMesh/
# → Include Sets → ดูตำแหน่งปัญหา
```

---

## 8. Quick Reference Tables

### 8.1 Tool Selection

| รูปทรง | Tool | เหตุผล |
|--------|------|--------|
| กล่อง, ท่อตรง | blockMesh | Hex quality สูงสุด |
| รถยนต์, เครื่องบิน | snappyHexMesh | ซับซ้อน, automatic |
| รูปทรงซับซ้อนมาก | Gmsh/Salome → import | external tools |

### 8.2 Quality Thresholds

| Metric | Good | OK | Bad | Fatal |
|--------|------|-----|-----|-------|
| Non-orthogonality | < 50° | < 70° | 70-85° | > 85° |
| Skewness | < 2 | < 4 | > 4 | — |
| Aspect Ratio | < 10 | < 100 | > 100 | — |
| Volume | + | + | + | Negative! |

### 8.3 Refinement Level vs Cell Size

| Background | Level | Cell Size | Factor |
|------------|-------|-----------|--------|
| 0.1 m | 0 | 0.1 m | 1× |
| 0.1 m | 1 | 0.05 m | 2× |
| 0.1 m | 2 | 0.025 m | 4× |
| 0.1 m | 3 | 0.0125 m | 8× |
| 0.1 m | N | 0.1/2^N m | 2^N× |

---

## 9. Common Workflow

```bash
# 1. สร้าง Background Mesh
blockMesh > log.blockMesh

# 2. สกัด Feature Edges
surfaceFeatureExtract > log.features

# 3. รัน snappyHexMesh
snappyHexMesh -overwrite > log.sHM

# หรือ Parallel:
decomposePar
mpirun -np 4 snappyHexMesh -overwrite -parallel > log.sHM
reconstructParMesh -constant

# 4. ตรวจสอบคุณภาพ
checkMesh -allGeometry -allTopology

# 5. ดูผลใน ParaView
paraFoam
```

---

## 10. Decision Trees

### เลือก Meshing Tool

```
รูปทรงเป็น Box/Cylinder/Simple?
  → blockMesh (Hex สะอาดที่สุด)

รูปทรงซับซ้อน (STL/CAD)?
  → snappyHexMesh
      └─ ต้องมี blockMesh ก่อน (background)
      
Mesh จาก software อื่น?
  → gmshToFoam / ideasUnvToFoam / fluent3DMeshToFoam
```

### แก้ไข checkMesh Error

```
❌ Negative volume?
  → blockMesh: ตรวจ vertex ordering
  → sHM: ตรวจ locationInMesh, snapControls

❌ High non-orthogonality (> 85°)?
  → เพิ่ม nCellsBetweenLevels
  → ลด refinement level
  → ตรวจ background mesh

❌ High skewness?
  → ลด featureAngle
  → เพิ่ม nSmoothPatch
  → ตรวจ STL quality

❌ Layer failed?
  → เริ่มด้วย expansionRatio = 1.0
  → ลด nSurfaceLayers
  → เพิ่ม featureAngle
```

---

## 11. สรุปท้ายบท

### หลักการ 3 ข้อจำง่าย

1. **Hex-dominant เสมอ**
   - Hex > Prism > Poly > Tet
   - ใช้ snappyHexMesh ไม่ใช่ tet mesher

2. **checkMesh ทุกครั้ง**
   - Non-ortho < 70°, Skewness < 4
   - ไม่มี negative volume

3. **Layer = y+ ที่ถูกต้อง**
   - Wall function: y+ ≈ 30-300
   - Resolve boundary layer: y+ < 1

---

*"Mesh ที่ดีคือ Mesh ที่ Solver ชอบ — Orthogonal, Low Skewness, Smooth Grading"*

---

## 12. 🧠 Advanced Concept Check

> **คำเตือน:** คำถามเหล่านี้ต้องการความเข้าใจลึก

### Level 1: Foundation Understanding

<details>
<summary><b>Q1: ทำไม OpenFOAM ถึงเก็บ Mesh แบบ Face-addressing แทนที่จะเป็น Cell-addressing?</b></summary>

**คำตอบ:**

**Face-addressing:**
- เก็บ `owner` (Cell ที่อยู่ "ซ้าย" ของ Face) และ `neighbour` (Cell ที่อยู่ "ขวา")
- ทำให้คำนวณ Flux ผ่าน Face ได้โดยตรง

**ข้อดี:**
1. **FVM needs Flux:** สมการ Conservation ต้องการ Flux ผ่าน Face ไม่ใช่ Cell
2. **Efficiency:** วนลูปผ่าน Face เพียงครั้งเดียว แล้วบวกลบให้ทั้งสอง Cells
3. **Flexibility:** รองรับ Polyhedral cells (กี่หน้าก็ได้)

**เปรียบเทียบ:**
```cpp
// Face-addressing (OpenFOAM)
forAll(faces, faceI)
{
    flux[owner[faceI]] += phi[faceI];
    flux[neighbour[faceI]] -= phi[faceI];
}

// Cell-addressing (ต้องวนซ้ำซ้อน)
forAll(cells, cellI)
{
    forAll(cell[cellI].faces(), fi)
    {
        // ซ้ำซ้อนและช้า
    }
}
```

</details>

<details>
<summary><b>Q2: ทำไม Background Mesh สำหรับ snappyHexMesh ต้องครอบคลุม Geometry ทั้งหมด?</b></summary>

**คำตอบ:**

**หลักการ snappyHexMesh:**
1. **Castellated:** ตัด cells ตาม geometry → ต้องมี cells ให้ตัด!
2. **Snap:** ดึงจุดเข้าหาผิว → ต้องมีจุดอยู่ใกล้ผิว!
3. **Layers:** ดัน mesh ถอยหลัง → ต้องมี mesh ให้ดัน!

**ถ้า Background ไม่ครอบคลุม:**
```
❌ Geometry โผล่พ้น Background
   → snappyHexMesh ไม่มี cells ให้ refine
   → ส่วนนั้นหายไป!
```

**Best Practice:**
```cpp
// Background mesh ควรใหญ่กว่า geometry 10-20%
vertices
(
    (-1 -1 -1)  // min - margin
    (11 11 11)  // max + margin
);
```

</details>

<details>
<summary><b>Q3: "nCellsBetweenLevels" มีผลต่อ Mesh Quality อย่างไร?</b></summary>

**คำตอบ:**

**นิยาม:** จำนวน cells buffer ระหว่างการเปลี่ยน refinement level

**ผลกระทบ:**
```
nCellsBetweenLevels = 1:
┌───┬───┬─┬─┐
│   │   │ │ │  ← เปลี่ยนกะทันหัน!
├───┼───┼─┼─┤     Non-ortho สูง
│   │   │ │ │     Skewness สูง
└───┴───┴─┴─┘

nCellsBetweenLevels = 3:
┌───┬───┬──┬──┬─┬─┐
│   │   │  │  │ │ │  ← เปลี่ยนค่อยๆ
├───┼───┼──┼──┼─┼─┤     Non-ortho ต่ำ
│   │   │  │  │ │ │     Skewness ต่ำ
└───┴───┴──┴──┴─┴─┘
```

**Trade-off:**
- ค่าสูง → Mesh quality ดี แต่ cell count เพิ่ม
- ค่าต่ำ → ประหยัดแต่ quality แย่

**Recommendation:**
- Default: 3
- High quality needed: 4-5
- Memory limited: 2

</details>

### Level 2: Deep Understanding

<details>
<summary><b>Q4: ทำไม Layer Addition ถึงล้มเหลวบ่อยที่สุดใน snappyHexMesh?</b></summary>

**คำตอบ:**

**กระบวนการ Layer Addition:**
1. คำนวณ Normal direction ของแต่ละ Face
2. "ดัน" Mesh ถอยหลังตาม Normal
3. แทรก Layer cells ในช่องว่าง
4. ตรวจสอบ Quality → ถ้าแย่ก็ยกเลิก Layer ตรงนั้น

**สาเหตุที่ล้มเหลว:**

| ปัญหา | เหตุผล | แก้ไข |
|-------|--------|-------|
| **มุมแหลม** | Normal vectors ชนกัน | เพิ่ม featureAngle |
| **พื้นที่จำกัด** | ดันแล้วชน feature อื่น | ลด nSurfaceLayers |
| **Concave corners** | Layer ทับซ้อนกัน | ใช้ nGrow |
| **Bad base mesh** | Snap quality แย่ | แก้ Phase 2 ก่อน |

**Debug Strategy:**
```bash
# รัน Phase ที่ละอัน
castellatedMesh true;
snap true;
addLayers false;  # ปิด layers ก่อน

# ตรวจ Phase 2 ให้ผ่านก่อน
# แล้วค่อยเปิด addLayers true
```

</details>

<details>
<summary><b>Q5: Non-orthogonal Corrector แก้ปัญหาอย่างไร และเสียอะไรแลก?</b></summary>

**คำตอบ:**

**ปัญหา Non-orthogonality:**
เมื่อ face normal ไม่ขนานกับเส้นเชื่อม cell centers:

$$\text{Flux} = \Gamma \frac{\phi_N - \phi_P}{|\vec{d}|}$$

ค่านี้ผิดเพราะ $\vec{d}$ ไม่ตั้งฉากกับ Face

**การแก้ไข (Deferred Correction):**

$$\text{Flux} = \underbrace{\Gamma \frac{\phi_N - \phi_P}{|\vec{d}|}}_{\text{Orthogonal}} + \underbrace{\Gamma \vec{k} \cdot (\nabla\phi)_f}_{\text{Non-ortho correction}}$$

โดย $\vec{k} = \vec{S} - \frac{\vec{S} \cdot \vec{d}}{|\vec{d}|^2}\vec{d}$

**วิธีการ:**
1. แก้สมการโดยไม่มี correction → ได้ $\phi^{(0)}$
2. คำนวณ correction term → แก้ใหม่ → ได้ $\phi^{(1)}$
3. ทำซ้ำ N รอบ (N = nNonOrthogonalCorrectors)

**Trade-off:**
| Correctors | ข้อดี | ข้อเสีย |
|------------|-------|---------|
| 0 | เร็วสุด | ผิดถ้า non-ortho สูง |
| 1-2 | สมดุล | ช้าลง 2-3× |
| 3+ | ถูกต้อง | ช้ามาก |

</details>

<details>
<summary><b>Q6: อธิบายหลักการ "Refinement Level" ใน snappyHexMesh</b></summary>

**คำตอบ:**

**หลักการ Octree:**
แต่ละ Level = แบ่ง Cell แม่เป็น 8 Cell ลูก (2×2×2)

```
Level 0: 1 cell (original)
Level 1: 8 cells (2³)
Level 2: 64 cells (4³)
Level 3: 512 cells (8³)
Level N: 2^(3N) cells จาก 1 cell เดิม
```

**Cell Size:**
$$\Delta x_{level} = \frac{\Delta x_{background}}{2^{level}}$$

**ตัวอย่าง:**
```
Background = 0.1 m
Level 0 = 0.1 m
Level 1 = 0.05 m
Level 2 = 0.025 m
Level 3 = 0.0125 m
Level 4 = 0.00625 m
```

**การใช้งานใน snappyHexMeshDict:**
```cpp
refinementSurfaces
{
    car
    {
        level (2 4);  // min level 2, max level 4
        // ผิวเรียบ → level 2
        // มุมคม (feature edges) → level 4
    }
}
```

</details>

### Level 3: Expert Understanding

<details>
<summary><b>Q7: ทำไมต้อง run surfaceFeatureExtract ก่อน snappyHexMesh?</b></summary>

**คำตอบ:**

**ปัญหา:**
STL file เก็บแค่ triangles ไม่รู้ว่า edges ไหนเป็นมุมคม (feature edge)

**surfaceFeatureExtract ทำอะไร:**
1. อ่าน STL
2. หามุมระหว่าง triangles ที่ติดกัน
3. ถ้ามุม > `includedAngle` → เก็บเป็น feature edge
4. เขียนไฟล์ `.eMesh` สำหรับ snappyHexMesh

**ผลลัพธ์:**
```
constant/triSurface/
├── car.stl
└── car.eMesh  ← feature edges
```

**สำคัญอย่างไร:**
- **ไม่มี feature edges:** สน้าปผิวเรียบ มุมหายไป
- **มี feature edges:** sHM จะ refine และ snap ตาม edges → มุมคมชัด

```cpp
// ใน snappyHexMeshDict
castellatedMeshControls
{
    features
    (
        { file "car.eMesh"; level 4; }  // refine ตาม edges
    );
}
```

</details>

<details>
<summary><b>Q8: อธิบายความแตกต่างระหว่าง finalLayerThickness กับ firstLayerThickness</b></summary>

**คำตอบ:**

**สองวิธีกำหนดความหนา Layer:**

**1. finalLayerThickness (Outside → Inside):**
```
Wall → Layer1 → Layer2 → ... → LayerN → Core mesh
       ↑                        ↑
       บาง                      หนา (finalLayerThickness)
```
- กำหนดความหนาของ Layer ชั้นนอกสุด (ติด core mesh)
- Expansion ratio คำนวณย้อนกลับ

**2. firstLayerThickness (Inside → Outside):**
```
Wall → Layer1 → Layer2 → ... → LayerN → Core mesh
       ↑
       หนา (firstLayerThickness)
```
- กำหนดความหนาของ Layer ชั้นแรก (ติด wall)
- ควบคุม y+ โดยตรง

**ใช้อันไหนดี?**

| ต้องการ | ใช้ | เหตุผล |
|---------|-----|--------|
| ควบคุม y+ | firstLayerThickness | y+ = f(first layer height) |
| Layer ไม่ล้มเหลว | finalLayerThickness | ง่ายต่อการ fit กับ core mesh |

**คำนวณ y+:**
$$y^+ = \frac{y \cdot u_\tau}{\nu}$$

$$u_\tau = \sqrt{\frac{\tau_w}{\rho}}$$

**Rule of thumb:**
- Wall function: y+ ≈ 30-300 → firstLayerThickness ≈ 1-10 mm
- Low-Re (resolve): y+ < 1 → firstLayerThickness ≈ 0.01-0.1 mm

</details>

<details>
<summary><b>Q9: ทำไม Prism layers ถึงสำคัญสำหรับ Turbulence modeling?</b></summary>

**คำตอบ:**

**Boundary Layer Physics:**
ใกล้ผนัง มี velocity gradient สูงมาก:

$$\frac{\partial u}{\partial y} \approx \frac{U_\infty}{\delta_{BL}}$$

โดย $\delta_{BL}$ เป็น boundary layer thickness (บางมาก)

**ปัญหาถ้าไม่มี Prism layers:**

```
Mesh แบบ Isotropic:        Mesh แบบ Prism layers:
┌───┬───┬───┐               ┌─────────────┐
│   │   │   │  ↑            ├─────────────┤ ← บาง (จับ gradient)
│   │   │   │  │    vs      ├─────────────┤
│   │   │   │  กว้าง         ├─────────────┤
└───┴───┴───┘               ├─────────────┤
Wall                        └─────────────┘
                            Wall

→ จับ gradient ไม่ได้!       → จับ gradient ได้!
```

**ผลกระทบ:**
1. **Wall shear stress ($\tau_w$):** คำนวณผิด → Drag ผิด
2. **Heat transfer:** คำนวณผิด → Temperature ผิด
3. **Turbulence models:** ต้องการ y+ ที่ถูกต้อง

**y+ Requirements:**
| Model | y+ | Prism layers |
|-------|-----|--------------|
| Wall function (k-ε) | 30-300 | 3-5 layers |
| Low-Re (k-ω SST) | < 1 | 10-20 layers |
| LES | < 1 | 15-30 layers |

</details>

---

## 13. ⚡ Advanced Hands-on Challenges

### Challenge 1: blockMesh Multi-Block Practice (⭐⭐⭐)

**วัตถุประสงค์:** เข้าใจ multi-block topology

**Task:** สร้าง blockMeshDict สำหรับ "ท่อโค้ง 90°"

**Requirements:**
1. Radius = 0.5 m, Diameter = 0.1 m
2. ใช้ arc edges
3. Grading อัดแน่นที่ผนังท่อ
4. checkMesh ต้องผ่าน (non-ortho < 50°)

**Hints:**
```cpp
edges
(
    arc 0 4 (0.5 0.353553 0)  // R*cos(45°), R*sin(45°)
);
```

---

### Challenge 2: snappyHexMesh Parameter Study (⭐⭐⭐⭐)

**วัตถุประสงค์:** เข้าใจผลกระทบของ parameters

**Setup:**
```bash
cp -r $FOAM_TUTORIALS/incompressible/simpleFoam/motorBike .
```

**Tasks:**
1. รัน sHM ด้วย default settings → บันทึก cell count, quality
2. เปลี่ยน `nCellsBetweenLevels` (1, 3, 5) → เปรียบเทียบ
3. เปลี่ยน refinement level (2, 4, 6) → เปรียบเทียบ
4. Plot: cell count vs non-orthogonality

**Expected Learning:**
- Trade-off ระหว่าง quality และ cost
- Parameter sensitivity

---

### Challenge 3: Layer Addition Debugging (⭐⭐⭐⭐⭐)

**วัตถุประสงค์:** เรียนรู้การ debug layer failures

**Setup:**
ใช้ STL ที่มีมุมแหลม (เช่น cube หรือ sphere)

**Tasks:**
1. สร้าง case ด้วย default layer settings → สังเกตว่าล้มเหลวตรงไหน
2. อ่าน log.sHM หาว่า layer ล้มเหลวเพราะอะไร
3. ทดลอง:
   - เพิ่ม featureAngle (60 → 130 → 180)
   - ลด nSurfaceLayers (5 → 3 → 1)
   - เปลี่ยน expansionRatio (1.3 → 1.1 → 1.0)
4. หาค่าที่ทำให้ layers ขึ้นครบ 100%

---

### Challenge 4: y+ Verification (⭐⭐⭐⭐⭐)

**วัตถุประสงค์:** เชื่อมโยง mesh กับ turbulence modeling

**Setup:**
```bash
cp -r $FOAM_TUTORIALS/incompressible/simpleFoam/pitzDaily .
```

**Tasks:**
1. รัน simulation → สร้าง yPlus field
   ```cpp
   // ใน controlDict
   functions { yPlus { type yPlus; libs (fieldFunctionObjects); } }
   ```

2. ดูค่า y+ บน walls ใน ParaView

3. คำถาม:
   - y+ อยู่ในช่วงที่เหมาะสมกับ wall function หรือไม่?
   - ถ้าต้องการ resolve boundary layer ต้องเพิ่มกี่ layers?

4. แก้ไข mesh แล้วรันใหม่ → เปรียบเทียบ Cd, Cl

---

### Challenge 5: Mesh Independence Study (⭐⭐⭐)

**วัตถุประสงค์:** เข้าใจ Grid Convergence

**Setup:**
ใช้ case ง่ายๆ เช่น flow over cylinder

**Tasks:**
1. สร้าง 3 mesh levels:
   - Coarse: ~10,000 cells
   - Medium: ~40,000 cells
   - Fine: ~160,000 cells

2. รันแต่ละ case → วัดค่า Cd

3. คำนวณ GCI:
   $$GCI = F_s \frac{|f_2 - f_1|}{r^p - 1}$$

4. Cd ที่ได้ grid independent หรือยัง?

---

## 14. ❌ Common Mistakes และ Solutions

### Mistake 1: ลืม surfaceFeatureExtract

```bash
# ❌ WRONG - run sHM โดยไม่มี feature edges
snappyHexMesh -overwrite

# ✅ CORRECT
surfaceFeatureExtract
snappyHexMesh -overwrite
```

**ผลลัพธ์:** มุมคมของ geometry จะหายไป หรือ snap ไม่ดี

---

### Mistake 2: locationInMesh อยู่บนผิว

```cpp
// ❌ WRONG - พิกัดอยู่บนผิว geometry!
locationInMesh (0 0 0);

// ✅ CORRECT - พิกัดอยู่ใน fluid domain อย่างแน่นอน
locationInMesh (0.00134 0.00234 0.00534);
```

**ผลลัพธ์:** sHM ลบผิด cells → mesh หายหมด หรือกลับด้าน

---

### Mistake 3: Background mesh เล็กกว่า geometry

```cpp
// ❌ WRONG - geometry โผล่พ้น background
vertices
(
    (0 0 0)
    (1 1 1)  // geometry กว้าง 1.2 m!
);

// ✅ CORRECT - ครอบคลุม + margin
vertices
(
    (-0.5 -0.5 -0.5)
    (1.5 1.5 1.5)
);
```

**ผลลัพธ์:** ส่วนที่โผล่พ้นจะหายไป

---

### Mistake 4: ไม่ตรวจ checkMesh ก่อนรัน

```bash
# ❌ WRONG - รัน solver เลย
simpleFoam

# ✅ CORRECT - ตรวจ mesh ก่อน
checkMesh -allGeometry -allTopology
# ดูว่า Mesh OK หรือมี errors
simpleFoam
```

**ผลลัพธ์:** Solver อาจ diverge โดยไม่รู้สาเหตุ

---

### Mistake 5: Refinement level สูงเกินไป

```cpp
// ❌ WRONG - level 8 บน surface ทั้งหมด!
refinementSurfaces
{
    car { level (8 8); }  // 2^8 = 256× refinement!
}

// ✅ CORRECT - ใช้ level ตามความจำเป็น
refinementSurfaces
{
    car { level (3 5); }  // min 3, max 5 ที่ features
}
```

**ผลลัพธ์:** Cell count ระเบิด → out of memory

---

### Mistake 6: blockMesh vertex ordering ผิด

```cpp
// ❌ WRONG - ไม่ตามกฎมือขวา
hex (0 3 2 1 4 7 6 5) (10 10 10) simpleGrading (1 1 1)
//   ↑ ผิดลำดับ!

// ✅ CORRECT - ตามกฎมือขวา
hex (0 1 2 3 4 5 6 7) (10 10 10) simpleGrading (1 1 1)
```

**ผลลัพธ์:** Negative volume cells → Solver crash

---

### Mistake 7: Grading สูงเกินไป

```cpp
// ❌ WRONG - grading 100 ใน 5 cells
blocks
(
    hex (...) (5 10 1) simpleGrading (100 1 1)
);

// ✅ CORRECT - grading ควร < 1.2^N
blocks
(
    hex (...) (20 10 1) simpleGrading (10 1 1)  // ~1.12 per cell
);
```

**ผลลัพธ์:** High aspect ratio, non-orthogonality

---

### Mistake 8: ไม่ใช้ -overwrite

```bash
# ❌ WRONG - สร้าง time directories 1/, 2/, 3/
snappyHexMesh

# ต้อง copy mesh กลับ
cp -r 3/polyMesh constant/polyMesh

# ✅ CORRECT - overwrite โดยตรง
snappyHexMesh -overwrite
```

**ผลลัพธ์:** Mesh อยู่ใน `3/` ไม่ใช่ `constant/` → solver หา mesh ไม่เจอ

---

## 15. 🔗 เชื่อมโยงกับ Repository

### อ่านเพิ่มเติม:

| หัวข้อ | ไฟล์ใน Repository |
|--------|-------------------|
| **Mesh Structure** | `MODULE_02/01_MESHING_FUNDAMENTALS/` |
| **blockMesh ลึกขึ้น** | `MODULE_02/02_BLOCKMESH_MASTERY/` |
| **snappyHexMesh** | `MODULE_02/03_SNAPPYHEXMESH_BASICS/` |
| **Layer Addition** | `MODULE_02/04_SNAPPYHEXMESH_ADVANCED/` |
| **Mesh Quality** | `MODULE_02/05_MESH_QUALITY_AND_MANIPULATION/` |
| **functionObjects** | `MODULE_02/06_RUNTIME_POST_PROCESSING/` |
| **polyMesh Classes** | `MODULE_05/04_MESH_CLASSES/` |

---

*"Mesh ที่ดีใช้เวลาสร้าง แต่ประหยัดเวลา debug solver หลายเท่า"*
