# 4. Mesh Classes: สถาปัตยกรรมระบบเรขาคณิตคำนวณของ OpenFOAM

## 📋 ภาพรวมบท

ยินดีต้อนรับสู่ **The Mesh Classes** - หัวใจของสถาปัตยกรรมระบบเรขาคณิตคำนวณของ OpenFOAM บทนี้จะสำรวจลำดับชั้นคลาสที่ซับซ้อนซึ่งแปลงข้อมูลเรขาคณิตดิบเป็น computational mesh ที่มีประสิทธิภาพสูงสำหรับการจำลอง Finite Volume

### 🎯 วัตถุประสงค์การเรียนรู้

หลังจากเสร็จสิ้นบทนี้ คุณจะเข้าใจ:

1. **ข้อมูลเรขาคณิตถูกจัดระเบียบอย่างไร** ในคลาส mesh แบบลำดับชั้นของ OpenFOAM
2. **พื้นฐานคณิตศาสตร์** ของเรขาคณิต mesh finite volume
3. **กลยุทธ์การเพิ่มประสิทธิภาพ** สำหรับเรขาคณิตการคำนวณ
4. **วิธีการเข้าถึงและจัดการ** ข้อมูล mesh สำหรับแอปพลิเคชันที่กำหนดเอง
5. **ความสัมพันธ์ระหว่างโทโพโลยีและเรขาคณิต** ใน mesh CFD

---

## 🏗️ ลำดับชั้นคลาส Mesh: สถาปัตยกรรมสามชั้น

ระบบ mesh ของ OpenFOAM ทำตาม **รูปแบบสถาปัตยกรรมสามชั้น** ที่ให้รากฐานที่แข็งแกร่งสำหรับพลศาสตร์ของไหลเชิงคำนวณ ในขณะเดียวกันก็รักษาประสิทธิภาพและความยืดหยุ่น ลำดับชั้นนี้แยกการคำนาณทางเรขาคณิต การจัดการโทโพโลยี และการดำเนินการปริมาตรจำกัดออกเป็นชั้นต่างๆ ที่เฉพาะเจาะจง

### ภาพรวมสถาปัตยกรรม

```mermaid
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
subgraph Layer3 [Layer 3: Finite Volume]
    FVM[fvMesh<br/>Discretization & Fields]:::implicit
end

subgraph Layer2 [Layer 2: Topology]
    PM[polyMesh<br/>Connectivity & Parallel]:::explicit
end

subgraph Layer1 [Layer 1: Geometry]
    PSM[primitiveMesh<br/>Math & Metrics]:::implicit
end

FVM --> PM
PM --> PSM
```

> **Figure 1:** สถาปัตยกรรมสามชั้นของระบบเมชใน OpenFOAM ซึ่งแบ่งความรับผิดชอบออกเป็นระดับเรขาคณิต (primitiveMesh), ระดับโทโพโลยี (polyMesh) และระดับการคำนวณฟิสิกส์ (fvMesh) เพื่อประสิทธิภาพและความยืดหยุ่นสูงสุด

> [!TIP] **Physical Analogy: The Anatomy of a High-Rise Building (โครงสร้างตึกระฟ้า)**
>
> ลองมองสถาปัตยกรรม 3 ชั้นนี้เหมือนระบบของตึก:
>
> 1.  **primitiveMesh (โครงสร้างเสา-คาน)**: รู้แค่ว่าเสาอยู่ตรงไหน คานยาวเท่าไหร่ (Geometry) รับน้ำหนักได้ไหม แต่ไม่รู้ว่าเป็นห้องอะไร
> 2.  **polyMesh (แปลนสถาปัตย์)**: กั้นผนัง แบ่งห้อง ใส่ประตูหน้าต่าง (Topology) บอกได้ว่าห้อง A ติดกับห้อง B เป็นห้องมุมหรือห้องกลาง แต่ยังไม่มีระบบน้ำไฟ
> 3.  **fvMesh (ระบบวิศวกรรมประกอบอาคาร - MEP)**: ติดตั้งท่อแอร์ ท่อน้ำ สายไฟ (Fields) ลงไปในห้อง เพื่อให้เกิดการไหลเวียนและใช้งานได้จริง (CFD Simulation)

สถาปัตยกรรมสามชั้นประกอบด้วย:

1.  **primitiveMesh** - เครื่องมือคำนวณเรขาคณิต
2.  **polyMesh** - กรอบงานโทโพโลยี
3.  **fvMesh** - ชั้นการแบ่งพื้นที่ปริมาตรจำกัด

### โครงสร้างการสืบทอด

```cpp
// Core mesh hierarchy (simplified)
// Base abstract class defining pure topological relationships
primitiveMesh          
    ├── polyMesh       // Adds boundary information to polygonal mesh
    │   ├── fvMesh     // Finite volume mesh with geometric field storage
    │   └── dynamicFvMesh // Extends fvMesh with mesh motion capabilities
    └── extendedMesh   // Extended mesh with additional features
```

> **📂 Source:** `.applications/utilities/mesh/manipulation/polyDualMesh/meshDualiser.C`

**คำอธิบาย:**
- **Source:** เป็นไฟล์ C++ ที่ใช้ในการจัดการ mesh manipulation โดยเฉพาะการสร้าง dual mesh
- **Explanation:** โครงสร้างการสืบทอดแสดงให้เห็นว่า primitiveMesh เป็นฐานนามธรรม (abstract base) ที่กำหนดความสัมพันธ์ทางโทโพโลยี จากนั้น polyMesh เพิ่มข้อมูลเขต (boundary information) และ fvMesh เพิ่มความสามารถด้านการคำนวณ finite volume
- **Key Concepts:** Inheritance hierarchy, topological relationships, boundary patches, finite volume discretization

ที่ฐานมี **primitiveMesh** - abstract base class ที่กำหนดความสัมพันธ์ทางโทโพโลยีระหว่าง mesh entities คลาสนี้รู้จัก:
- **Point-face connectivity**: จุดใดบ้างที่เกิดแต่ละหน้า
- **Face-cell connectivity**: หน้าใดบ้างที่ล้อมรอบแต่ละเซลล์
- **Cell-point connectivity**: จุดใดบ้างที่อยู่ในแต่ละเซลล์
- **Face-edge connectivity**: ขอบใดบ้างที่เกิดแต่ละหน้า (สำหรับคุณสมบัติขั้นสูง)

### การแยกความรับผิดชอบ

| ชั้น | หน้าที่หลัก | ความรับผิดชอบ |
|---|---|---|
| **primitiveMesh** | การคำนาณเรขาคณิตแบบบริสุทธิ์ | • การคำนวณ centers, volumes, normals<br>• เมตริกคุณภาพ mesh<br>• Lazy evaluation |
| **polyMesh** | การจัดการโทโพโลยี | • จัดเก็บ points, faces, cells<br>• owner/neighbor relationships<br>• Boundary patches<br>• การสนับสนุนขนาน |
| **fvMesh** | การแบ่งพื้นที่ปริมาตรจำกัด | • การจัดเก็บฟิลด์เรขาคณิต<br>• API สำหรับ solver<br>• การคำนวณเรขาคณิตตามความต้องการ |

---

## 🔍 แนวคิดระดับสูง: อนุลักษณ์การวางแผนเมือง

จินตนาการการออกแบบ **เมืองทันสมัย**:

- **ผู้สำรวจที่ดิน (Points)**: วัดพิกัดที่แน่นอนของทุกสถานที่
- **ผู้วางแผนที่ดิน (Faces)**: กำหนดเขตที่ดินระหว่างแปลง
- **สถาปนิกเขต (Cells)**: ออกแบบบล็อกสามมิติ (แปลงหลายเหลี่ยม)
- **วิศวกรจราจร (Connectivity)**: สร้างความสัมพันธ์เจ้าของ/ข้างเคียง (ถนน)
- **รัฐบาลเมือง (Boundaries)**: จัดตั้งเขตที่มีกฎต่างกัน (patches)

คลาส mesh ของ OpenFOAM ทำงานเหมือน **ระบบวางแผนเมืองแบบบูรณาการ**นี้ - คลาสละหนึ่งมีความรับผิดชอบเฉพาะ และร่วมกันสร้าง computational domain ที่ทำงานได้ซึ่งสมการ CFD "อยู่และไหล"

---

## 📐 พื้นฐานคณิตศาสตร์: วิธี Finite Volume

วิธี finite volume (FVM) พื้นฐานอาศัยการแบ่ง computational domain เป็น discrete control volumes (cells) สำหรับแต่ละเซลล์ $V_i$ เราหาอินทิกรัลของสมการที่ควบคุม:

$$
\int_{V_i} \frac{\partial \phi}{\partial t} \, \mathrm{d}V + \oint_{\partial V_i} \phi \mathbf{u} \cdot \mathbf{n} \, \mathrm{d}S = \int_{V_i} S_\phi \, \mathrm{d}V
$$

โดยที่:
- $\phi$ = field variable (ความเร็ว, ความดัน, อุณหภูมิ, เป็นต้น)
- $\mathbf{u}$ = velocity field
- $\mathbf{n}$ = outward unit normal vector ที่พื้นผิว
- $S_\phi$ = source term

คลาส mesh ให้ข้อมูลเรขาคณิตที่จำเป็นในการประเมิน surface integrals และการคำนวณ control volume เหล่านี้ด้วยความแม่นยำสูง

### ทฤษฎีบทของ Gauss: พื้นฐานของ FVM

Finite volume method ถูกสร้างขึ้นจาก **divergence theorem** (ทฤษฎีบทของ Gauss) ซึ่งเป็นพื้นฐานทางคณิตศาสตร์ในการแปลง volume integrals เป็น surface integrals:

$$
\int_V \nabla \cdot \mathbf{F} \, \mathrm{d}V = \oint_{\partial V} \mathbf{F} \cdot \mathrm{d}\mathbf{S}
$$

**ตัวแปร:**
- $\mathbf{F}$ = เวกเตอร์ฟลักซ์
- $V$ = ปริมาตรควบคุม
- $S$ = พื้นผิวควบคุม
- $\mathbf{n}$ = เวกเตอร์หน่วยตั้งฉากต่อพื้นผิว

สำหรับเซลล์ discrete $i$ ที่มีปริมาตร $V_i$ และหน้า $f$ เราประมาณ volume integral โดยรวม fluxes ผ่านหน้าเซลล์ทั้งหมด:

$$
\int_{V_i} \nabla \cdot \mathbf{F} \, \mathrm{d}V \approx \sum_{f \in \partial V_i} \mathbf{F}_f \cdot \mathbf{S}_f
$$

การประมาณ discrete นี้รับประกันการอนุรักษ์แน่นอนของปริมาณที่ถูก transport ระดับเซลล์

---

## 🔧 ส่วนประกอบหลักคลาส Mesh

### 1. คลาส Points

จัดเก็บพิกัดเรขาคณิตของ vertices ของ mesh:

```cpp
class pointField : public Field<point>
{
    // Inherits from Field<point> for efficient storage
    // Provides random access to coordinates via pointField[i]
    // Supports vector operations for geometric calculations
};
```

> **📂 Source:** OpenFOAM core mesh implementation (`src/OpenFOAM/meshes/primitiveMesh/primitiveMesh.H`)

**คำอธิบาย:**
- **Source:** เป็นส่วนหนึ่งของ core mesh implementation ใน OpenFOAM
- **Explanation:** pointField สืบทอดจาก Field<point> เพื่อให้มีการจัดเก็บที่มีประสิทธิภาพ และให้การเข้าถึงแบบสุ่ม (random access) ผ่านตัวดำเนินการ [] รองรับ vector operations สำหรับการคำนวณเรขาคณิตต่างๆ
- **Key Concepts:** Field inheritance, random access, vector operations, coordinate storage

จุดละหนึ่ง $p_i = (x_i, y_i, z_i)$ แทน vertex ในปริภูมิ 3 มิติ คลาส pointField ให้การเข้าถึงสุ่มถึงพิกัดเหล่านี้และรองรับ vector operations สำหรับการคำนวณเรขาคณิต

### 2. คลาส Faces

กำหนดเขตพรหมแบบหลายเหลี่ยมระหว่างเซลล์:

```cpp
class face
{
private:
    List<label> points_;  // List of point indices forming the face

public:
    // Calculate face normal vector using cross product
    vector normal(const pointField&) const;

    // Calculate face centroid as weighted average of points
    point centre(const pointField&) const;

    // Calculate face area using polygon area formula
    scalar area(const pointField&) const;
};
```

> **📂 Source:** OpenFOAM primitive mesh implementation (`src/OpenFOAM/meshes/primitiveMesh/primitiveMesh.H`)

**คำอธิบาย:**
- **Source:** เป็นส่วนหนึ่งของ primitive mesh implementation ใน OpenFOAM
- **Explanation:** face class เก็บรายการดัชนีของจุด (point indices) ที่เป็นเขตของหน้า แต่ละหน้ามี normal vector, centroid และ area ซึ่งคำนวณจากพิกัดของจุดที่ประกอบเป็นหน้า
- **Key Concepts:** Polygonal faces, point connectivity, normal vectors, centroid calculation, area computation

หน้าเชื่อมต่อหลายจุดเพื่อสร้างหลายเหลี่ยม แต่ละหน้ามี:

- **Normal vector**: $\mathbf{n} = \frac{1}{2A}\sum_{i=1}^{n} (\mathbf{r}_i \times \mathbf{r}_{i+1})$
- **Centroid**: ค่าเฉลี่ยถ่วงของพิกัดจุด
- **Area**: คำนวณโดยใช้สูตรพื้นที่หลายเหลี่ยม

### 3. คลาส Cells

แทน control volumes หลายหลี่ยมสามมิติ:

```cpp
class cell
{
private:
    List<label> faces_;  // List of face indices bounding the cell

public:
    // Calculate cell volume using divergence theorem
    scalar mag(const pointField&, const faceList&) const;

    // Calculate cell centroid from face centroids and volumes
    point centre(const pointField&, const faceList&) const;
};
```

> **📂 Source:** OpenFOAM primitive mesh implementation (`src/OpenFOAM/meshes/primitiveMesh/primitiveMesh.H`)

**คำอธิบาย:**
- **Source:** เป็นส่วนหนึ่งของ primitive mesh implementation ใน OpenFOAM
- **Explanation:** cell class เก็บรายการดัชนีของหน้า (face indices) ที่ล้อมรอบเซลล์ ปริมาตรเซลล์คำนวณโดยใช้ divergence theorem ซึ่งรวมผลคุณสมบัติของหน้าทั้งหมดที่ล้อมรอบ
- **Key Concepts:** Control volumes, face connectivity, divergence theorem, volume calculation, centroid computation

แต่ละเซลล์ถูกกำหนดโดย bounding faces การคำนวณปริมาตรเซลล์ใช้ divergence theorem:

$$
V = \frac{1}{6} \sum_{f \in \text{faces}} (\mathbf{c}_f \cdot \mathbf{n}_f) A_f
$$

โดยที่ $\mathbf{c}_f$ คือ face centroid, $\mathbf{n}_f$ คือ face normal และ $A_f$ คือ face area

### 4. Boundary Conditions (Patches)

คอลเลกชันหน้าที่มีพฤติกรรมเฉพาะทางฟิสิกส์:

```cpp
class polyPatch
{
public:
    // Pure virtual function to update mesh topology
    virtual void updateMesh(PolyTopoChange&) = 0;

    // Access to patch-specific fields and properties
    const word& name() const;
    const labelList& meshPoints() const;
    const labelList& meshFaces() const;
};
```

> **📂 Source:** OpenFOAM polyMesh implementation (`src/OpenFOAM/meshes/polyMesh/polyPatches/polyPatch/polyPatch.H`)

**คำอธิบาย:**
- **Source:** เป็นส่วนหนึ่งของ polyMesh implementation ที่จัดการ boundary patches
- **Explanation:** polyPatch เป็น base class สำหรับ boundary patches ทั้งหมด มีฟังก์ชัน virtual สำหรับอัปเดต topology เมื่อ mesh เปลี่ยนแปลง และให้การเข้าถึงข้อมูลเฉพาะของแต่ละ patch เช่น ชื่อ, points, และ faces
- **Key Concepts:** Boundary conditions, virtual functions, mesh topology, patch-specific properties

---

## ⚡ กลไก Lazy Evaluation: ประสิทธิภาพหน่วยความจำ

OpenFOAM ใช้ระบบ **การคำนวณตามความต้องการ** ที่ซับซ้อน ซึ่งจะเลื่อนการคำนาณทางเรขาคณิตที่มีค่าใช้จ่ายสูงไปจนกว่าจะต้องการใช้จริง

```cpp
// 🔧 MECHANISM: Demand-driven geometric calculation
class primitiveMesh
{
private:
    // Storage for computed properties (initially empty)
    // Uses mutable to allow modification in const methods
    mutable autoPtr<vectorField> cellCentresPtr_;
    mutable autoPtr<scalarField> cellVolumesPtr_;
    mutable autoPtr<vectorField> faceCentresPtr_;
    mutable autoPtr<vectorField> faceAreasPtr_;

public:
    // ✅ GETTER: Compute only when needed, cache result
    const vectorField& cellCentres() const
    {
        if (!cellCentresPtr_.valid())  // Not computed yet?
        {
            // Compute on demand using calcCellCentres()
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

> **📂 Source:** OpenFOAM primitiveMesh implementation (`src/OpenFOAM/meshes/primitiveMesh/primitiveMesh.H`)

**คำอธิบาย:**
- **Source:** เป็นส่วนหนึ่งของ primitiveMesh implementation ที่ใช้ lazy evaluation strategy
- **Explanation:** กลไก lazy evaluation ใช้ autoPtr ที่เป็น mutable เพื่อเก็บผลการคำนาณเรขาคณิต ฟังก์ชัน getter จะตรวจสอบว่ามีการคำนวณแล้วหรือยัง ถ้าไม่จึงจะคำนวณ และฟังก์ชัน clearGeom() จะล้าง cache เมื่อ mesh เปลี่ยนแปลง
- **Key Concepts:** Lazy evaluation, demand-driven computation, caching, mutable members, autoPtr smart pointers, memory optimization

### ประสิทธิภาพหน่วยความจำ

| แนวทาง | ความต้องการหน่วยความจำ (double precision) |
|---|---|
| **ดั้งเดิม (คำนวณล่วงหน้า)** | |
| - ปริมาตร cell | $N_{\text{cells}} \times 8$ ไบต์ |
| - พื้นที่หน้า | $N_{\text{faces}} \times 8$ ไบต์ |
| - จุดศูนย์ถ่วงหน้า | $N_{\text{faces}} \times 24$ ไบต์ (เวกเตอร์ 3D) |
| - จุดศูนย์ถ่วง cell | $N_{\text{cells}} \times 24$ ไบต์ |
| **ตามความต้องการ** | |
| - โทโพโลยี | $O(N_{\text{cells}} + N_{\text{faces}} + N_{\text{points}})$ |
| - ปริมาณที่คำนวณ | $O(1)$ ต่อการคำนาณที่ใช้งาน |
| - หน่วยความจำสำหรับผลลัพธ์ | ถูกปล่อยทันทีหลังจากใช้ |

**ประสิทธิภาพ**: สำหรับ mesh ที่มี 1 ล้าน cell การประหยัดหน่วยความจำอาจเกิน **100 MB** เมื่อต้องการเพียงส่วนย่อยของคุณสมบัติทางเรขาคณิตในช่วงเวลาใดๆ

---

## 📊 คุณภาพ Mesh: ตัวชี้วัดและมาตรฐาน

คุณภาพของ mesh ส่งผลโดยตรงต่อความถูกต้องและการบรรจบของการจำลอง CFD OpenFOAM มีตัวชี้วัดคุณภาพหลายอย่าง:

### Non-orthogonality

วัดความเบี่ยงเบนระหว่างเวกเตอร์ปกติของหน้าและเส้นเชื่อมระหว่างจุดศูนย์กลางเซลล์ข้างเคียง:

$$
\theta = \arccos\left(\frac{\mathbf{S}_f \cdot \mathbf{d}}{|\mathbf{S}_f||\mathbf{d}|}\right)
$$

โดยที่:
- $\mathbf{S}_f$ คือเวกเตอร์พื้นที่ของหน้า
- $\mathbf{d}$ คือระยะห่างระหว่างจุดศูนย์กลางเซลล์
- $\theta$ คือมุมระหว่างพวกมัน

### Skewness

วัดว่าจุดศูนย์ถ่วงของหน้าเบี่ยงเบนจากตำแหน่งเหมาะสม:

$$
\text{skewness} = \frac{|\mathbf{c}_f - \mathbf{c}_{proj}|}{|\mathbf{d}|}
$$

### มาตรฐานคุณภาพ Mesh

| ตัวชี้วัด | ดีเยี่ยม | ดี | ยอมรับได้ | ต้องแก้ไข |
|---|---|---|---|---|
| Non-orthogonality | < 30° | 30-50° | 50-70° | > 70° |
| Skewness | < 1.0 | 1.0-2.0 | 2.0-4.0 | > 4.0 |
| Aspect Ratio | < 5 | 5-10 | 10-20 | > 20 |

---

## 🎯 การปรับให้เหมาะสมด้านประสิทธิภาพ

คลาส mesh ของ OpenFOAM รวมถึงการเพิ่มประสิทธิภาพหลายอย่างที่สำคัญ:

| การเพิ่มประสิทธิภาพ | วัตถุประสงค์ | ผลกระทบ |
|---|---|---|
| **Compact Storage** | Contiguous memory layouts | การใช้ cache อย่างมีประสิทธิภาพ |
| **Lazy Evaluation** | ปริมาณทางเรขาคณิต | คำนวณตามความต้องการและจัดเก็บไว้ |
| **Reference Counting** | Smart pointers | ป้องกัน memory leaks ขณะที่รักษาประสิทธิภาพ |
| **Cache-Friendly Algorithms** | Iteration patterns | การเพิ่มประสิทธิภาพสำหรับสถาปัตยกรรม CPU สมัยใหม่ |

---

## ⚠️ ข้อผิดพลาดที่พบบ่อยและวิธีแก้ไข

### ข้อผิดพลาดที่ 1: การเก็บการอ้างอิงเรขาคณิตเก่า

เมื่อคุณเก็บการอ้างอิงไปยัง `cellCentres()`, `faceAreas()`, หรือเรขาคณิตที่คำนวณแล้วที่คล้ายกัน คุณกำลังเก็บตัวชี้ไปยังข้อมูลที่แคชไว้ ซึ่งอาจถูกล้างเมื่อ `clearGeom()` ถูกเรียก

**วิธีแก้ไขที่ถูกต้อง:**
```cpp
// ✅ GOOD: Store only mesh reference
MeshProcessor(const primitiveMesh& mesh) : mesh_(mesh) {}

void process()
{
    // ✅ Retrieve fresh geometry data when needed
    const vectorField& centres = mesh_.cellCentres();
    processCentres(centres);

    // If mesh changes...
    // mesh_.clearGeom();

    // ✅ Retrieve new data after changes
    const vectorField& newCentres = mesh_.cellCentres();
    processCentres(newCentres);
}
```

> **📂 Source:** Best practice pattern from OpenFOAM mesh utilities

**คำอธิบาย:**
- **Source:** เป็น pattern ที่แนะนำจาก OpenFOAM mesh utilities
- **Explanation:** การเก็บ reference ไปยัง geometric data ที่คำนวณแล้วอาจทำให้เกิดการใช้ข้อมูลที่ล้างแล้ว (stale data) วิธีที่ถูกต้องคือเก็บ reference ไปยัง mesh และดึงข้อมูลเรขาคณิตใหม่ทุกครั้งที่ต้องการ
- **Key Concepts:** Reference validity, cache invalidation, demand-driven computation, memory safety

### ข้อผิดพลาดที่ 2: การละเลยคุณภาพเมช

คุณภาพเมชที่ไม่ดีอาจทำให้เกิดความไม่เสถียรเชิงตัวเลขและผลลัพธ์ที่ไม่ถูกต้อง

**แนวทางปฏิบัติที่ดีที่สุด:**
- ตรวจสอบ mesh quality ก่อนการคำนวณ
- เลือก discretization schemes ที่เหมาะสมกับ mesh quality
- ปรับปรุง mesh หากคุณภาพต่ำกว่ามาตรฐาน

---

## 🚀 การประยุกต์ใช้ใน CFD

สถาปัตยกรรม mesh นี้ทำให้สามารถ:

-   **Flux Calculations**: Face areas และ normals สำหรับ convection terms
-   **Gradient Computations**: Cell centers และ volumes สำหรับ diffusion terms
-   **Boundary Conditions**: Patch-specific physics และ constraints
-   **Adaptive Meshing**: การปรับเปลี่ยน dynamic ของ mesh topology
-   **Parallel Computation**: Domain decomposition และ load balancing

---

## 💎 บทสรุป

คลาส mesh เหล่านี้เป็น**รากฐาน**ที่การคำนาณ CFD ทั้งหมดถูกสร้างขึ้น โดยให้กรอบทางเรขาคณิตที่แปลงสมการเชิงอนุพันธ์ย่อยให้เป็นระบบพีชคณิตที่สามารถแก้ไขได้ผ่านวิธี Finite Volume

**การออกแบบสะท้อนถึง:**
- ความต้องการของพลศาสตร์ของไหลเชิงคำนวณ
- ความยืดหยุ่นสำหรับการประยุกต์ใช้ทางวิศวกรรมที่หลากหลาย
- ประสิทธิภาพสำหรับการประมวลผลขนาดใหญ่
- ความแม่นยำทางคณิตศาสตร์สำหรับผลลัพธ์ที่เชื่อถือได้

การออกแบบที่สวยงามของคลาส mesh ของ OpenFOAM ให้รากฐานที่มั่นคงสำหรับการจำลอง CFD ที่มีประสิทธิภาพสูง ทำให้เป็นหนึ่งในระบบเรขาคณิตการคำนาณที่ซับซ้อนที่สุดใน scientific computing

---

## 🧠 9. Concept Check (ทดสอบความเข้าใจ)

1.  **ทำไม OpenFOAM ถึงต้องแยก `primitiveMesh` ออกจาก `polyMesh`? ทำไมไม่รวมเป็น Class เดียว?**
    <details>
    <summary>เฉลย</summary>
    เพื่อแยก **Geometry (เรขาคณิต)** ออกจาก **Topology (ความเชื่อมโยง)** อย่างชัดเจน ทำให้เราสามารถเปลี่ยนรูปร่างเมช (เช่น Mesh Motion) ได้โดยไม่ต้องรื้อโครงสร้างความเชื่อมโยงใหม่ หรือสามารถใช้ Algorithm ทางเรขาคณิตซ้ำได้ในบริบทอื่นๆ ที่ไม่ใช่ CFD
    </details>

2.  **ในมุมมองของ "Lazy Evaluation" ถ้าเราไม่เคยเรียกใช้ฟังก์ชัน `mesh.cellCentres()` เลย ข้อมูลจุดศูนย์กลางเซลล์จะถูกคำนวณหรือไม่?**
    <details>
    <summary>เฉลย</summary>
    **ไม่ถูกคำนวณ** ระบบจะคำนวณก็ต่อเมื่อมีการเรียกใช้ครั้งแรกเท่านั้น (On-demand) ซึ่งช่วยประหยัดหน่วยความจำและเวลาสำหรับ Field ที่ไม่ได้ใช้งานในการจำลองนั้นๆ
    </details>

3.  **ความสัมพันธ์ระหว่าง FVM (Finite Volume Method) กับ `face` คืออะไร?**
    <details>
    <summary>เฉลย</summary>
    ใน FVM `face` คือประตูผ่านของ Fluxes (การไหลของมวล, โมเมนตัม, พลังงาน) ระหว่าง Cell ทฤษฎีบทของ Gauss (Divergence Theorem) เปลี่ยนปริพันธ์เชิงปริมาตรให้เป็นผลรวมของ Fluxes ผ่าน `face` เหล่านี้นั่นเอง
    </details>