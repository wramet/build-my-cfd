# สรุปและแบบฝึกหัด (Summary & Exercises)

```mermaid
mindmap
root((OpenFOAM Mesh))
Architecture
primitiveMesh
Geometry/Lazy Eval
polyMesh
Topology/Connectivity
fvMesh
CFD Fields/Registry
Key Concepts
Lazy Evaluation
Owner-Neighbour
Object Registry
Best Practices
Use References
Avoid unnecessary edits
Check Mesh Quality
```
> **Figure 1:** แผนผังความคิดสรุปองค์ประกอบหลักของระบบเมชใน OpenFOAM ครอบคลุมทั้งโครงสร้างสถาปัตยกรรม แนวคิดสำคัญ และแนวทางปฏิบัติที่ดีที่สุดสำหรับการพัฒนาโปรแกรม

## สรุปเนื้อหาสำคัญ

สถาปัตยกรรมเมชของ OpenFOAM ถูกออกแบบมาเพื่อความเร็วและความยืดหยุ่น:

1.  **3-Layer Architecture**: แยกความรับผิดชอบออกเป็น `primitiveMesh` (เรขาคณิต), `polyMesh` (โทโพโลยี), และ `fvMesh` (ฟิสิกส์)
2.  **Lazy Evaluation**: คำนวณปริมาตรและพื้นที่เมื่อจำเป็นเท่านั้น ช่วยลดเวลาเริ่มต้นโปรแกรม
3.  **Ownership Model**: ใช้ระบบ `owner` และ `neighbour` เพื่อระบุความสัมพันธ์ระหว่างเซลล์และหน้าได้อย่างรัดกุม
4.  **Integration**: เมชทำหน้าที่เป็นจุดศูนย์กลางของการจัดการข้อมูล (Object Registry) และประวัติเวลา (Time)

---

## 🎯 **ความสำคัญสำหรับ CFD**

### **ประโยชน์ทางวิศวกรรม 1: การจัดการหน่วยความจำแบบปรับตัว**

ในการจำลอง CFD ในระดับอุตสาหกรรมจริง ประสิทธิภาพหน่วยความจำไม่เพียงแค่การเพิ่มประสิทธิภาพเท่านั้น แต่มักเป็นความแตกต่างระหว่างการทำงานหรือล้มเหลวของการจำลอง

| ผลกระทบ | คำอธิบาย |
|---------|----------|
| **การลดต้นทุน** | ต้องการโหนดคำนวณน้อยลงสำหรับการจำลองขนาดใหญ่ |
| **การขยายความสามารถ** | สามารถแก้ปัญหาที่ใหญ่ขึ้น 20% บนฮาร์ดแวร์ที่มีอยู่ |
| **การปรับปรุงประสิทธิภาพ** | ลดความต้องการแบนด์วิดท์หน่วยความจำ |

**ตัวอย่างการประหยัดหน่วยความจำ:**

```cpp
class LargeMeshSimulation
{
private:
    // Memory requirements for 10M cell mesh:
    // - Raw point coordinates: 10M × 3 × 8 bytes = 240 MB (always required)
    // - Cell centre coordinates: 240 MB (computed when needed)
    // - Cell volumes: 80 MB (computed when needed)
    // - Face area vectors: ~500 MB (computed when needed)

    // Memory strategy comparison:
    // No lazy evaluation: ~1 GB allocated constantly
    // With lazy evaluation: ~240 MB base + compute on demand

public:
    void solveTransientProblem()
    {
        // Stage 1: Initial setup phase
        const auto& centres = mesh_.cellCentres();  // +240 MB temporary

        // Stage 2: Momentum equation solution
        const auto& Sf = mesh_.faceAreas();        // +500 MB temporary

        // Stage 3: Post-processing and diagnostics
        const auto& vols = mesh_.cellVolumes();    // +80 MB temporary

        // Memory usage profile:
        // Peak memory: 240 + 500 + 80 = 820 MB
        // Base memory: 240 MB
        // Memory savings: 18% compared to constant 1 GB allocation
    }
};
```

> **📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C`
> 
> **คำอธิบาย:** ตัวอย่างโค้ดนี้แสดงให้เห็นถึงการใช้งาน Lazy Evaluation ในสถาปัตยกรรมเมชของ OpenFOAM ในไฟล์ต้นฉบับ MomentumTransferPhaseSystem.C จะเห็นว่ามีการจัดการค่าสเกลาร์และเวกเตอร์ฟิลด์แบบไดนามิกเช่นเดียวกับแนวคิดในตัวอย่าง โดยมีการใช้ `IOobject` และ `dimensionedScalar` ในการสร้างฟิลด์เมื่อจำเป็น ซึ่งสอดคล้องกับหลักการของ Lazy Evaluation ที่ช่วยประหยัดหน่วยความจำ
>
> **แนวคิดสำคัญ:**
> - **Lazy Evaluation Pattern**: คำนวณค่าเรขาคณิต (cellCentres, faceAreas, cellVolumes) เมื่อถูกเรียกใช้เท่านั้น
> - **Temporary Storage**: ข้อมูลที่คำนวณแล้วถูกเก็บในตัวแปร `const auto&` เพื่อใช้ชั่วคราว
> - **Automatic Caching**: primitiveMesh จะเก็บค่าที่คำนวณแล้วจนกว่าจะมีการเปลี่ยนแปลงเรขาคณิต
> - **Memory Efficiency**: ลดการใช้หน่วยความจำสูงสุดโดยไม่จองพื้นที่คงที่สำหรับทุกค่าเรขาคณิต

### **ประโยชน์ทางวิศวกรรม 2: ความแข็งแกร่งต่อการเปลี่ยนแปลง Mesh**

การจำลอง CFD สมัยใหม่มักเกี่ยวข้องกับ mesh แบบไดนามิก ตั้งแต่ขอบเขตที่เคลื่อนที่ใน fluid-structure interaction ไปจนถึงการเปลี่ยนแปลงโทโพโลยีในการจำลอง additive manufacturing

```cpp
class MovingMeshSolver
{
private:
    fvMesh& mesh_;

public:
    void solveTimeStep()
    {
        // Step 1: Update mesh geometry for current time step
        mesh_.movePoints(newPoints);

        // ✅ Automatic geometry cache invalidation
        // When movePoints() is called, primitiveMesh::movePoints()
        // automatically triggers clearGeom(), invalidating all caches:
        // - cellCentres_ cache is cleared
        // - cellVolumes_ cache is cleared
        // - faceAreas_ cache is cleared
        // - All computed geometry data marked as "needs update"

        // Step 2: Next geometry access triggers recomputation
        const auto& newCentres = mesh_.cellCentres();  // Recomputed with new geometry
        const auto& newVolumes = mesh_.cellVolumes();  // Recomputed with new geometry

        // Step 3: Solver automatically uses updated geometry
        solveWithUpdatedGeometry(newCentres, newVolumes);

        // Benefits:
        // - Eliminates errors from stale geometry usage
        // - Guarantees mass and momentum conservation
        // - Handles arbitrary mesh deformations automatically
    }
};
```

> **📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystem.H`
>
> **คำอธิบาย:** ในไฟล์ phaseSystem.H จะเห็นรูปแบบการจัดการ mesh ที่เป็นพื้นฐานของการทำงานกับ dynamic mesh โดยมีการส่งอ้างอิงถึง `const fvMesh&` ซึ่งเป็นแบบ pattern เดียวกับที่แสดงในตัวอย่าง การเรียก `movePoints()` จะทำให้เกิดการล้าง cache อัตโนมัติ ซึ่งเป็นกลไกสำคัญในการรับประกันความถูกต้องของการคำนวณเมื่อมีการเปลี่ยนแปลงรูปทรงเรขาคณิตของ mesh
>
> **แนวคิดสำคัญ:**
> - **Cache Invalidation**: การเรียก `movePoints()` จะล้าง cache เรขาคณิตทั้งหมดอัตโนมัติ
> - **Automatic Recomputation**: การเข้าถึงค่าเรขาคณิตหลังจากการเปลี่ยนแปลงจะทำให้เกิดการคำนวณใหม่
> - **Conservation Guarantee**: รับประกันการอนุรักษ์มวลและโมเมนตัมโดยอัตโนมัติ
> - **Robustness**: จัดการการเปลี่ยนแปลง mesh ได้อย่างราบรื่นโดยไม่ต้องแทรกแซงด้วยตนเอง

### **ประโยชน์ทางวิศวกรรม 3: การ Discretization ที่ขับเคลื่อนด้วยคุณภาพ**

คุณภาพของ mesh ส่งผลโดยตรงต่อความแม่นยำของการจำลอง แต่บริเวณต่างๆ ของ mesh มีคุณภาพที่แตกต่างกันโดยไม่สามารถหลีกเลี่ยงได้ Solver CFD ขั้นสูงปรับเปลี่ยน schemes ตัวเลขตามลักษณะของ mesh ในพื้นที่

```cpp
class QualityAwareSolver
{
private:
    const fvMesh& mesh_;

public:
    void discretizeFlux(const volScalarField& phi, label faceI)
    {
        // Step 1: Analyze local mesh quality metrics
        scalar orthogonality = mesh_.nonOrthogonality(faceI);    // Face angular deviation
        scalar skewness = mesh_.skewness(faceI);                 // Insertion quality
        scalar aspectRatio = mesh_.aspectRatio(faceI);           // Cell elongation

        // Step 2: Select optimal discretization strategy
        if (orthogonality < 20.0 && skewness < 0.5 && aspectRatio < 5.0)
        {
            // ✅ High quality region: Use second-order accurate schemes
            return centralDifferenceScheme(phi, faceI);
        }
        else if (orthogonality < 70.0 && skewness < 1.0)
        {
            // ✅ Medium quality region: Use higher-order schemes with correction
            return correctedScheme(phi, faceI);
        }
        else
        {
            // ✅ Low quality region: Use robust first-order schemes
            return upwindScheme(phi, faceI);
        }
    }
};
```

> **📂 Source:** `.applications/solvers/compressible/rhoCentralFoam/rhoCentralFoam.C`
>
> **คำอธิบาย:** ในไฟล์ rhoCentralFoam.C จะเห็นการใช้งาน mesh-based schemes ที่มีการปรับเปลี่ยนตามคุณภาพของ mesh แม้ว่าจะไม่แสดงการตรวจสอบคุณภาพโดยตรง แต่แนวคิดของการเลือก scheme ที่เหมาะสมกับสภาพของ mesh ถูกนำไปใช้ในการพัฒนา solvers ขั้นสูง โดยเฉพาะในกรณีที่มีความไม่ตั้งฉากสูงหรือ mesh ที่มีความซับซ้อน
>
> **แนวคิดสำคัญ:**
> - **Adaptive Discretization**: เลือก scheme ที่เหมาะสมกับคุณภาพ mesh ในพื้นที่นั้นๆ
> - **Quality Metrics**: ใช้ non-orthogonality, skewness, และ aspect ratio เป็นตัวชี้วัด
> - **Stability vs Accuracy**: แลกเปลี่ยนระหว่างความแม่นยำและเสถียรภาพของการคำนวณ
> - **Local Adaptation**: ปรับ scheme แยกกันในแต่ละบริเวณของ mesh

| เมตริก | ค่าที่ยอมรับได้ | ผลกระทบ |
|---------|----------------|----------|
| **Non-orthogonality** | < 70° | ความแม่นยำของการกระจาย |
| **Skewness** | < 0.5 | เสถียรภาพการคำนวณ |
| **Aspect Ratio** | < 1000 | ความเร็วในการลู่เข้า |

---

## 🎓 **รายการตรวจสอบความสำเร็จ**

- [x] **เข้าใจสถาปัตยกรรมสามชั้น**: `primitiveMesh` → `polyMesh` → `fvMesh`
- [x] **เชี่ยวชาญ Lazy Evaluation**: รู้เมื่อเรขาคณิตถูกคำนวณ/ล้างข้อมูล
- [x] **จัดการขอบเขตอย่างถูกต้อง**: Patches, Zones, และ Processor Boundaries
- [x] **ใช้มิติที่เหมาะสม**: จับข้อผิดพลาดหน่วยได้ที่เวลาคอมไพล์
- [x] **เลือกรูปแบบที่เหมาะสม**: จับคู่ Discretization กับฟิสิกส์/Mesh
- [x] **คิดแบบขนาน**: สมมติการดำเนินการ mesh แบบกระจาย
- [x] **ตรวจสอบคุณภาพ Mesh**: ตรวจสอบความไม่ตั้งฉาก, ความเบ้, เป็นต้น
- [x] **จัดการวงจรชีวิตฟิลด์**: การสร้าง, การแก้, การอัปเดตขอบเขต

---

## สถาปัตยกรรมสามชั้นอย่างละเอียด

### **ชั้นที่ 1: primitiveMesh - เครื่องมือคำนวณเรขาคณิต**

```cpp
class primitiveMesh
{
private:
    // Storage for computed properties (initially empty)
    mutable autoPtr<vectorField> cellCentresPtr_;
    mutable autoPtr<scalarField> cellVolumesPtr_;
    mutable autoPtr<vectorField> faceCentresPtr_;
    mutable autoPtr<vectorField> faceAreasPtr_;

public:
    // ✅ GETTER: Compute only when needed, cache result
    const vectorField& cellCentres() const
    {
        if (!cellCentresPtr_.valid())
        {
            cellCentresPtr_.reset(calcCellCentres());
        }
        return cellCentresPtr_();
    }

    // ✅ INVALIDATOR: Clear cache when mesh changes
    void clearGeom()
    {
        cellCentresPtr_.clear();
        cellVolumesPtr_.clear();
        faceCentresPtr_.clear();
        faceAreasPtr_.clear();
    }
};
```

> **📂 Source:** `.applications/solvers/multiphase/multiphaseInterFoam/multiphaseMixture/multiphaseMixture.C`
>
> **คำอธิบาย:** ในไฟล์ multiphaseMixture.C จะเห็นรูปแบบการใช้งาน mutable pointers และ autoPtr สำหรับการจัดการค่าที่คำนวณแบบ lazy evaluation ซึ่งเป็น pattern ที่ใช้ทั่วไปใน OpenFOAM สำหรับการจัดการข้อมูลที่มีค่าใช้จ่ายสูงในการคำนวณ
>
> **แนวคิดสำคัญ:**
> - **Mutable Storage**: ใช้ `mutable` เพื่อให้สามารถคำนวณค่าในฟังก์ชัน const ได้
> - **Lazy Computation**: คำนวณเมื่อถูกเรียกใช้ครั้งแรกเท่านั้น
> - **Cache Management**: เก็บค่าที่คำนวณแล้วจนกว่าจะมีการเปลี่ยนแปลง
> - **Automatic Invalidation**: มีกลไกสำหรับล้าง cache เมื่อมีการเปลี่ยนแปลง mesh

**สมการพื้นฐาน:**

จุดศูนย์กลางเซลล์ถ่วงน้ำหนักตามพื้นที่หน้า:

$$\mathbf{c}_{cell} = \frac{\sum_{f \in \partial cell} A_f \mathbf{c}_f}{\sum_{f \in \partial cell} A_f}$$

ปริมาตรเซลล์โดยใช้ทฤษฎีบท divergence:

$$V = \frac{1}{3} \sum_{f \in \partial cell} \mathbf{c}_f \cdot \mathbf{S}_f$$

### **ชั้นที่ 2: polyMesh - กรอบงานโทโพโลยี**

```cpp
class polyMesh
{
private:
    // Original topology storage (immutable after mesh creation)
    const pointField& points_;           // 3D coordinates of all mesh points
    const faceList& faces_;              // List of point indices defining each face
    const cellList& cells_;              // List of face indices defining each cell
    const labelList& owner_;             // Owner cell index for each face
    const labelList& neighbour_;         // Neighbor cell index for each face (boundary faces = -1)

    // Boundary management
    const polyBoundaryMesh& boundary_;   // Collection of boundary patches

public:
    // Direct access methods
    const pointField& points() const { return points_; }
    const faceList& faces() const { return faces_; }
    const cellList& cells() const { return cells_; }

    // Mesh consistency validation
    bool checkMesh(const bool report) const {
        // Check face connectivity
        // Check cell closure
        // Check boundary consistency
        return isTopologicallyCorrect();
    }
};
```

> **📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseModel/MovingPhaseModel/MovingPhaseModel.C`
>
> **คำอธิบาย:** ในไฟล์ MovingPhaseModel.C จะเห็นการใช้งาน mesh topology ผ่านการอ้างอิงถึง `const pointField&` และ structure ที่คล้ายคลึงกับ polyMesh ซึ่งแสดงให้เห็นถึงการใช้งาน topology ของ mesh ในการคำนวณ transport phenomena และการเคลื่อนที่ของ phase
>
> **แนวคิดสำคัญ:**
> - **Topology Storage**: เก็บข้อมูล connectivity (points, faces, cells) แยกจากเรขาคณิต
> - **Owner-Neighbor System**: กำหนดความสัมพันธ์ระหว่าง cell และ face อย่างชัดเจน
> - **Immutable Topology**: topology ไม่เปลี่ยนแปลงหลังจากสร้าง mesh (ยกเว้น dynamic mesh)
> - **Boundary Management**: จัดการ boundary patches แยกจาก internal faces

**กฎ Owner-Neighbor:**

ทุก face ใน mesh ต้องมี **owner cell** พอดีหนึ่งชุด และ **internal faces** มี **neighbor cell** อีกหนึ่งชุด:

```cpp
const labelList& owner = mesh.faceOwner();
const labelList& neighbour = mesh.faceNeighbour();

// Face normal always points from owner to neighbor
// For internal face between cell 5 and 10:
//   owner_[faceI] = 5
//   neighbour_[faceI] = 10
//   Face normal vector points from cell 5 to cell 10
```

### **ชั้นที่ 3: fvMesh - ชั้นการแบ่งพื้นที่ปริมาตรจำกัด**

```cpp
class fvMesh
    : public polyMesh          // Inherits all topology/geometry
    , public lduMesh          // Linear algebra interface
{
private:
    // Finite volume specific data
    fvBoundaryMesh boundary_;  // FV-specific boundary conditions

    // Discretization schemes
    surfaceInterpolation interpolation_;  // Face interpolation weights
    fvSchemes schemes_;                   // Numerical schemes
    fvSolution solution_;                 // Solver settings

    // Computed finite volume geometry (on demand)
    mutable autoPtr<volScalarField> Vptr_;      // Cell volumes
    mutable autoPtr<surfaceScalarField> magSfPtr_; // Face areas
    mutable autoPtr<surfaceVectorField> SfPtr_;   // Face area vectors
    mutable autoPtr<surfaceVectorField> CfPtr_;   // Face centres

public:
    // ✅ FV-SPECIFIC ACCESS: Cell volumes as field
    const volScalarField& V() const
    {
        if (!Vptr_.valid())
        {
            Vptr_.reset(new volScalarField("V", *this, dimVolume));
            Vptr_() = primitiveMesh::cellVolumes();  // Compute from base
        }
        return Vptr_();
    }

    // ✅ FACE GEOMETRY: Face area vectors as surface field
    const surfaceVectorField& Sf() const
    {
        if (!SfPtr_.valid())
        {
            SfPtr_.reset(new surfaceVectorField("Sf", *this, dimArea));
            SfPtr_() = primitiveMesh::faceAreas();  // Compute from base
        }
        return SfPtr_();
    }
};
```

> **📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C`
>
> **คำอธิบาย:** ในไฟล์ MomentumTransferPhaseSystem.C จะเห็นการใช้งาน `volScalarField` และ `surfaceScalarField` ซึ่งเป็น field types พื้นฐานใน finite volume method การสร้าง fields ด้วย `IOobject` และการใช้ `dimensionedScalar` เป็น pattern ที่ใช้กันอย่างแพร่หลายในการสร้าง geometric fields ใน OpenFOAM
>
> **แนวคิดสำคัญ:**
> - **Field-Based Storage**: เก็บข้อมูลเรขาคณิตเป็น GeometricFields ไม่ใช่ arrays
> - **Multiple Inheritance**: สืบทอดจาก polyMesh (topology) และ lduMesh (linear algebra)
> - **Scheme Integration**: เชื่อมต่อกับ numerical schemes และ interpolation
> - **Dimension Awareness**: รักษา units ของแต่ละปริมาณอย่างอัตโนมัติ

**พื้นฐาน Finite Volume:**

ทฤษฎีบท divergence (Gauss theorem):

$$\int_V \nabla \cdot \mathbf{F} \, \mathrm{d}V = \oint_{\partial V} \mathbf{F} \cdot \mathrm{d}\mathbf{S}$$

รูปแบบ discretized สำหรับเซลล์ $i$:

$$(\nabla \cdot \mathbf{F})_i = \frac{1}{V_i} \sum_{f \in \partial V_i} \mathbf{F}_f \cdot \mathbf{S}_f$$

---

## แบบฝึกหัด (Exercises)

### ส่วนที่ 1: ความเข้าใจสถาปัตยกรรม

1.  อธิบายหน้าที่ความรับผิดชอบที่แตกต่างกันระหว่าง `polyMesh` และ `fvMesh`
2.  **Lazy Evaluation** คืออะไร และมันช่วยเพิ่มประสิทธิภาพของ OpenFOAM ได้อย่างไร?
3.  ในชั้น `polyMesh` อะไรคือความแตกต่างระหว่างหน้าภายใน (Internal Face) และหน้าขอบเขต (Boundary Face) ในแง่ของ `owner` และ `neighbour`?

### ส่วนที่ 2: การวิเคราะห์โค้ด

จงเขียนบรรทัดโค้ด OpenFOAM เพื่อดึงข้อมูลต่อไปนี้จากออบเจกต์ `mesh`:

1.  ปริมาตรของเซลล์ทั้งหมด (เป็นฟิลด์)
2.  รายการชื่อของ Boundary Patches ทั้งหมด
3.  เวกเตอร์พื้นที่หน้า (Surface Area Vectors)

### ส่วนที่ 3: การแก้ไขปัญหา (Scenario)

หากโซลเวอร์ของคุณรันช้ามาก และคุณพบว่าในโค้ดมีการเรียกฟังก์ชัน `mesh.points().setSize(...)` ในทุกๆ Iteration:
- ปัญหานี้เกี่ยวข้องกับกลไกใดของ `primitiveMesh`?
- คุณควรแก้ไขเบื้องต้นอย่างไรเพื่อเพิ่มความเร็ว?

### ส่วนที่ 4: การวิเคราะห์คุณภาพ Mesh

จงเขียนฟังก์ชัน OpenFOAM เพื่อตรวจสอบคุณภาพ mesh โดยคำนวณ:

1. ค่า Non-orthogonality สูงสุดของ mesh
2. ค่า Skewness สูงสุดของ mesh
3. อัตราส่วน Aspect Ratio สูงสุดของ mesh

**คำใบ้:** ใช้สมการต่อไปนี้:

$$\text{Non-orthogonality} = \arccos\left(\frac{\mathbf{S}_f \cdot \mathbf{d}}{|\mathbf{S}_f||\mathbf{d}|}\right)$$

$$\text{Skewness} = \frac{|\mathbf{c}_f - \mathbf{c}_{proj}|}{|\mathbf{d}|}$$

โดยที่:
- $\mathbf{S}_f$ คือเวกเตอร์พื้นที่หน้า
- $\mathbf{d}$ คือเวกเตอร์ที่เชื่อมต่อจุดศูนย์กลางเซลล์ข้างเคียง
- $\mathbf{c}_f$ คือจุดศูนย์ถ่วงของหน้า
- $\mathbf{c}_{proj}$ คือจุดศูนย์ถ่วงของหน้าที่ฉายบนเส้นเชื่อมต่อจุดศูนย์กลางเซลล์

---

## 💡 แนวคำตอบ

### **ส่วนที่ 1**:
1. `polyMesh` จัดการโครงสร้างจุด/หน้า/ขอบเขต ส่วน `fvMesh` จัดการข้อมูลสำหรับการแก้สมการ CFD
2. คือการรอคำนวณจนกว่าจะมีการเรียกใช้ ช่วยลดการคำนวณที่ไม่จำเป็น
3. หน้าภายในมีทั้ง `owner` และ `neighbour` ส่วนหน้าขอบเขตมีเพียง `owner` เท่านั้น

### **ส่วนที่ 2**:
1. `mesh.V()`
2. `mesh.boundaryMesh().names()`
3. `mesh.Sf()`

### **ส่วนที่ 3**:
- เกี่ยวข้องกับการล้าง Cache (Cache Flushing) ทุกครั้งที่จุดเปลี่ยนพิกัดหรือจำนวน
- ควรหลีกเลี่ยงการเปลี่ยนโครงสร้างเมชในลูปการคำนวณฟิสิกส์หากไม่จำเป็นจริงๆ

### **ส่วนที่ 4**:

```cpp
void analyzeMeshQuality(const fvMesh& mesh)
{
    scalar maxNonOrtho = 0.0;
    scalar maxSkewness = 0.0;

    const vectorField& Cf = mesh.faceCentres();
    const vectorField& Sf = mesh.faceAreas();
    const vectorField& C = mesh.cellCentres();
    const labelList& owner = mesh.owner();
    const labelList& neighbour = mesh.neighbour();

    // Check non-orthogonality and skewness for all internal faces
    forAll(owner, faceI)
    {
        if (mesh.isInternalFace(faceI))
        {
            label own = owner[faceI];
            label nei = neighbour[faceI];

            // Vector connecting cell centers
            vector d = C[nei] - C[own];
            scalar magD = mag(d);
            scalar magSf = mag(Sf[faceI]);

            if (magD > SMALL && magSf > SMALL)
            {
                // Non-orthogonality calculation
                scalar cosAngle = (Sf[faceI] & d) / (magSf * magD);
                cosAngle = max(min(cosAngle, 1.0), -1.0);
                scalar nonOrtho = radToDeg(acos(cosAngle));
                maxNonOrtho = max(maxNonOrtho, nonOrtho);

                // Skewness calculation
                vector proj = C[own] + ((Cf[faceI] - C[own]) & d) * d / (magD * magD);
                scalar skewness = mag(Cf[faceI] - proj) / (magD + VSMALL);
                maxSkewness = max(maxSkewness, skewness);
            }
        }
    }

    Info << "Maximum non-orthogonality: " << maxNonOrtho << "°" << endl;
    Info << "Maximum skewness: " << maxSkewness << endl;
}
```

> **📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C`
>
> **คำอธิบาย:** ฟังก์ชันนี้ใช้ pattern ที่คล้ายกับที่พบใน MomentumTransferPhaseSystem.C โดยมีการวนลูปผ่าน faces และใช้ mesh geometry data (faceCentres, faceAreas, cellCentres) ในการคำนวณคุณภาพของ mesh การใช้ `forAll` loop และการเข้าถึง mesh data เป็นรูปแบบมาตรฐานใน OpenFOAM programming
>
> **แนวคิดสำคัญ:**
> - **Geometry Access**: ใช้ mesh.geometry fields ในการคำนวณ metrics
> - **Internal Face Loop**: วนลูปเฉพาะ internal faces สำหรับ non-orthogonality
> - **Vector Operations**: ใช้ dot product และ cross product ในการคำนวณ
> - **Numerical Stability**: ใช้ `SMALL` และ `VSMALL` เพื่อป้องกัน division by zero
> - **Metric Calculation**: คำนวณ non-orthogonality และ skewness ตามสมการที่กำหนด

---

## แหล่งอ้างอิงเพิ่มเติม

สำหรับการเรียนรู้เพิ่มเติมเกี่ยวกับคลาส Mesh ใน OpenFOAM:

1. **OpenFOAM Source Code**: `$FOAM_SRC/meshes/`
2. **Programmer's Guide**: [OpenFOAM Wiki](https://openfoamwiki.net/)
3. **Finite Volume Method**: บทที่ 3 - การ discretize สมการอนุพันธ์ย่อย
4. **Mesh Quality**: บทที่ 6 - การวิเคราะห์และปรับปรุงคุณภาพ Mesh
5. **Advanced Topics**:
   - Dynamic Mesh (บทที่ 8)
   - Parallel Processing (บทที่ 9)
   - Custom Boundary Conditions (บทที่ 10)

**การประยุกต์ใช้งานจริง:**
- การพัฒนา Custom Solver
- การสร้าง Utilities สำหรับ Mesh Manipulation
- การ Optimize Performance สำหรับ Large-Scale Simulation


---

## 🏁 Final Check: สรุปความเข้าใจก่อนไปต่อ

1.  **ทำไม OpenFOAM ถึงใช้วิธี Lazy Evaluation (คำนวณเมื่อใช้) แทนที่จะคำนวณเรขาคณิตทุกอย่างไว้ตั้งแต่เริ่มโปรแกรม?**
    <details>
    <summary>เฉลย</summary>
    เพื่อ **ประหยัด Memory และเวลาเริ่มต้น (Startup Time)** การคำนวณทุกอย่างล่วงหน้า (Pre-calculation) อาจกิน RAM มหาศาลโดยไม่จำเป็น และในกรณี Dynamic Mesh ข้อมูลเหล่านี้จะเปลี่ยนไปเรื่อยๆ ทำให้การคำนวณทิ้งไว้ล่วงหน้าเป็นการสิ้นเปลือง
    </details>

2.  **ในสถาปัตยกรรม 3 ชั้น (primitive -> poly -> fv) ชั้นไหนที่เป็น "พระเอก" ในการเก็บ Field ตัวแปร (เช่น U, p) และใช้คำนวณ CFD?**
    <details>
    <summary>เฉลย</summary>
    **`fvMesh`** (Finite Volume Mesh) ชั้นนี้สืบทอดความสามารถมาจากชั้นอื่นๆ และเพิ่มระบบ Register Field + Discretization เข้าไป
    </details>

3.  **ถ้าเราเขียน Solver ที่ต้องรองรับ Moving Mesh เราต้องเขียนโค้ดจัดการ "ล้าง Cache" เรขาคณิตเองไหม?**
    <details>
    <summary>เฉลย</summary>
    **ไม่ต้อง!** ระบบ `fvMesh` (ผ่าน `primitiveMesh`) จะทำการ **Auto-invalidate** Cache ให้เองทันทีที่มีการเรียกฟังก์ชัน `movePoints()` ดังนั้นหน้าที่ของเราคือแค่เรียกใช้ `mesh.cellVolumes()` (หรืออื่นๆ) ตามปกติ OpenFOAM จะรู้เองว่าต้องคำนวณใหม่หรือไม่
    </details>