# `polyMesh`: โครงสร้างและการจัดการโทโพโลยี

![[city_registry_office.png]]
`A grand architectural building labeled "polyMesh Registry". Inside, blueprints of points and faces are meticulously filed. A "Boundary" wing manages different zones (Inlet, Outlet), scientific textbook diagram, clean vector line art, white background, high definition, flat design, educational infographic --ar 16:9`

---

## 🔍 **High-Level Concept: อุปมาน "สำนักงานทะเบียนเมือง"**

### **PolyMesh ในฐานะการจัดการโครงสร้างพื้นฐานเมือง**

จินตนาการถึง **สำนักงานทะเบียนเมือง** ที่รักษาบันทึกข้อมูลที่ครอบคลุมของโครงสร้างพื้นฐานเมือง สำนักงานนี้ไม่เพียงแต่เก็บข้อมูลสุ่ม - แต่รักษา **ความสัมพันธ์เชิงโทโพโลยีที่เป็นทางการ** ที่กำหนดว่าเมืองทั้งหมดถูกจัดระเบียบและเชื่อมต่อกันอย่างไร

```mermaid
flowchart LR
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
C1[Cell 1<br/>owner]:::implicit -->|face f<br/>(owner: 1, neighbour: 2)<br/>Normal: 1→2| C2[Cell 2<br/>neighbour]:::implicit
C2 -->|boundary face<br/>(owner: 2)<br/>Normal: outward| B[Boundary Patch]:::explicit
```
> **Figure 1:** อุปมาเปรียบเทียบระบบ `polyMesh` กับสำนักงานทะเบียนเมืองที่จัดการความสัมพันธ์เชิงพื้นที่และกรรมสิทธิ์ระหว่างเซลล์และหน้าผิวผ่านระบบ Owner และ Neighborความปลอดภัยทางฟิสิกส์ไม่ส่งผลกระทบต่อความเร็วในการจำลอง ผ่านการใช้พลังของ C++ Template Metaprogramming ในการตรวจสอบความสอดคล้องทางมิติทั้งหมดที่ขั้นตอนการคอมไพล์โปรแกรมเพียงครั้งเดียว

### **ส่วนประกอบหลักของทะเบียน**

#### **กรรมสิทธิ์ทรัพย์สิน (Points ใน polyMesh)**

ทะเบียนรักษาพิกัด GPS ที่แม่นยำสำหรับทุกมุมของที่ดิน ซึ่งเป็นจุดยอดพื้นฐานที่กำหนดความสัมพันธ์เชิงพื้นที่ทั้งหมดใน mesh

ใน `polyMesh` จัดเก็บเป็น `points_` - `pointField` ที่มีพิกัด 3 มิติที่แน่นอนของทุกจุดยอด mesh:

```cpp
// Access mesh points - 3D coordinates of all vertices
const pointField& points = mesh.points();
forAll(points, i) {
    const point& p = points[i];
    // p.x(), p.y(), p.z() give precise coordinates
}
```

> **📂 Source:** `.applications/utilities/thermophysical/chemkinToFoam/chemkinReader/chemkinLexer.L`
> 
> **คำอธิบาย:**
> - **points**: เป็นสมาชิกข้อมูลหลักที่เก็บพิกัด 3 มิติของจุดยอดทั้งหมดใน mesh
> - **pointField**: เป็นชนิดข้อมูล OpenFOAM ที่เป็น container สำหรับเก็บ points หลายจุด
> - **forAll**: เป็น macro ของ OpenFOAM สำหรับการวนลูปผ่าน container
> 
> **แนวคิดสำคัญ:**
> - พิกัดจุด (Point coordinates) เป็นพื้นฐานของเรขาคณิต mesh
> - การเข้าถึง points ผ่าน reference แบบ const ป้องกันการแก้ไขโดยไม่ได้รับอนุญาต
> - พิกัด 3 มิติใช้ vector class ของ OpenFOAM

#### **แผนที่เขตแดน (Faces ใน polyMesh)**

คำอธิบายทางกฎหมายของเขตแดนทรัพย์สินกำหนดว่าใครเป็นเจ้าของด้านใดของทุกเส้นเขตแดน ใน `polyMesh` faces คือขอบเขตรูปหลายเหลี่ยมระหว่าง cells โดยแต่ละ face มี owner cell และ neighbor cell

ฟิลด์ `faces_` จัดเก็บเป็น `faceList`:

```cpp
// Access mesh faces and their connectivity
const faceList& faces = mesh.faces();
forAll(faces, i) {
    const face& f = faces[i];
    // f contains vertex indices forming the polygon face
    label own = mesh.faceOwner()[i];  // Owner cell index
    label nei = mesh.faceNeighbour()[i]; // Neighbor cell (-1 for boundary)
}
```

> **📂 Source:** `.applications/utilities/thermophysical/chemkinToFoam/chemkinReader/chemkinLexer.L`
> 
> **คำอธิบาย:**
> - **faceList**: Container ของ faces ทั้งหมดใน mesh
> - **face**: เป็น polygon ที่ประกอบด้วยดัชนีของจุดยอด (vertex indices)
> - **faceOwner()**: คืนค่า owner cell index สำหรับแต่ละ face
> - **faceNeighbour()**: คืนค่า neighbor cell index (หรือ -1 สำหรับ boundary faces)
> 
> **แนวคิดสำคัญ:**
> - Faces เป็น interfaces ระหว่าง cells
> - ระบบ owner-neighbor กำหนดทิศทางของ face normal
> - Boundary faces ไม่มี neighbor (ค่า -1)
> - การเชื่อมต่อ topology ถูกเก็บอย่างมีประสิทธิภาพ

#### **ใบอนุญาตก่อสร้าง (Cells ใน polyMesh)**

สิทธิ์ปริมาตร 3 มิติกำหนดพื้นที่ที่โครงสร้างแต่ละอย่างสามารถครอบครองได้ ซึ่งกลายเป็น computational cells ที่สมการ CFD ถูกแก้ไข

ฟิลด์ `cells_` จัดเก็บการเชื่อมต่อของ cell:

```cpp
// Access cell connectivity information
const cellList& cells = mesh.cells();
forAll(cells, i) {
    const cell& c = cells[i];
    // c contains face indices forming the closed boundary of the cell
}
```

> **📂 Source:** `.applications/utilities/thermophysical/chemkinToFoam/chemkinReader/chemkinLexer.L`
> 
> **คำอธิบาย:**
> - **cellList**: Container ของ cells ทั้งหมดใน mesh
> - **cell**: เป็น volume element ที่ถูกกำหนดโดย faces หลายหน้า
> - แต่ละ cell เก็บดัชนีของ faces ที่ล้อมรอบมัน
> 
> **แนวคิดสำคัญ:**
> - Cells เป็นปริมาตร 3 มิติที่ discretized สมการ
> - การเชื่อมต่อ face-to-cell ถูกเก็บอย่างชัดเจน
> - Cells สามารถเป็น polyhedral (หลายหน้า) ไม่จำกัดจำนวน faces

#### **บันทึกระบบครอบครอง (Owner/Neighbor ใน polyMesh)**

ทะเบียนติดตามความสัมพันธ์ใกล้เคียง - ทรัพย์สินใดแบ่งปันเขตแดน ใน `polyMesh` นี้ถูก implement ผ่านฟิลด์ `owner_` และ `neighbour_`:

```cpp
// Access owner-neighbor relationships
const labelList& owner = mesh.faceOwner();
const labelList& neighbour = mesh.faceNeighbour();

// Face always points from owner to neighbor
// This orientation is crucial for flux calculations
```

> **📂 Source:** `.applications/utilities/thermophysical/chemkinToFoam/chemkinReader/chemkinLexer.L`
> 
> **คำอธิบาย:**
> - **labelList**: Array ของ label (integer) ใน OpenFOAM
> - **faceOwner()**: คืนค่า array ของ owner cell indices
> - **faceNeighbour()**: คืนค่า array ของ neighbor cell indices
> - ความสัมพันธ์ owner→neighbor กำหนดทิศทางของ face normal
> 
> **แนวคิดสำคัญ:**
> - ทุก face มี owner หนึ่งตัว
> - Internal faces มี neighbor หนึ่งตัว
> - Boundary faces มีค่า neighbor = -1
> - ทิศทางนี้สำคัญสำหรับการคำนวณ flux

#### **กฎระเบียบการวางผัง (Boundary Conditions ใน polyMesh)**

กฎพิเศษสำหรับพื้นที่ต่างๆ (ที่พักอาศัย, เชิงพาณิชย์, อุตสาหกรรม) สอดคล้องกับประเภทของเงื่อนไขขอบเขต

ใน `polyMesh` `boundaryMesh()` กำหนดโซนพิเศษเหล่านี้:

```cpp
// Access boundary mesh information
const polyBoundaryMesh& boundary = mesh.boundaryMesh();
forAll(boundary, i) {
    const polyPatch& patch = boundary[i];
    // patch.type(), patch.name() define boundary conditions
}
```

> **📂 Source:** `.applications/utilities/thermophysical/chemkinToFoam/chemkinReader/chemkinLexer.L`
> 
> **คำอธิบาย:**
> - **polyBoundaryMesh**: Container ของ boundary patches
> - **polyPatch**: Patch เดียวบน boundary ที่มีประเภทและชื่อเฉพาะ
> - แต่ละ patch กำหนดเงื่อนไขขอบเขตทางฟิสิกส์
> 
> **แนวคิดสำคัญ:**
> - Boundaries ถูกจัดกลุ่มเป็น patches
> - แต่ละ patch มี type (wall, inlet, outlet, etc.)
> - Boundary conditions ถูกกำหนดต่อ patch
> - รองรับ various boundary types (cyclic, symmetry, etc.)

---

### **อุปมานชั้นข้อมูล GIS**

polyMesh ทำงานเหมือนกับ **ระบบสารสนเทศภูมิศาสตร์ (GIS)** โดยมีชั้นข้อมูลที่เชื่อมต่อกัน:

![[of_polymesh_gis_layers.png]]
`A diagram showing 5 overlapping GIS layers representing polyMesh data: 1. GPS Positions (Points), 2. Property Lines (Faces), 3. 3D Parcels (Cells), 4. Neighbor Maps (Connectivity), 5. Zoning Regulations (Boundary Conditions), scientific textbook diagram, clean vector line art, white background, high definition, flat design, educational infographic --ar 16:9`

#### **ชั้นข้อมูล 1: พิกัดจุด (GPS Positions)**
- ระบบอ้างอิงเชิงพื้นที่พร้อมพิกัด 3 มิติที่แม่นยำ
- พื้นฐานสำหรับการดำเนินงานเรขาคณิตระดับสูง
- ใช้สำหรับการประมาณค่า, การคำนวณ gradient, และตัวชี้วัดคุณภาพ mesh

#### **ชั้นข้อมูล 2: ขอบเขตรูปหลายเหลี่ยม (Property Lines)**
- การเชื่อมต่อของ face ที่กำหนด interfaces ของ cell
- การคำนวณพื้นที่สำหรับการคำนวณ flux
- การคำนวณเวกเตอร์ปกติสำหรับเงื่อนไขขอบเขต
- ตำแหน่ง center ของ face สำหรับการประมาณค่าของ field

#### **ชั้นข้อมูล 3: การแบ่งส่วนปริมาตร (3D Parcels)**
- ปริมาตรของ cell สำหรับการ discretization วิธีปริมาตรจำกัด
- center ของ cell สำหรับการจัดเก็บและการประมาณค่าของ field
- ส่วนปริมาตรสำหรับการไหลแบบหลายเฟส
- ตัวชี้วัดคุณภาพ mesh (อัตราส่วนภาพ, ความเบ้)

#### **ชั้นข้อมูล 4: ความสัมพันธ์ใกล้เคียง (Neighbor Maps)**
- โครงสร้างเมทริกซ์เบาบางสำหรับระบบเชิงเส้น
- รูปแบบการสื่อสารสำหรับการประมวลผลแบบขนาน
- การสร้าง stencil ของ gradient
- การติดตาม interface สำหรับการไหลแบบหลายเฟส

#### **ชั้นข้อมูล 5: โซนพิเศษ (Boundary Conditions)**
- ประเภทขอบเขตทางกายภาพ (กำแพง, ทางเข้า, ทางออก)
- เงื่อนไขขอบเขตทางคณิตศาสตร์ (Dirichlet, Neumann)
- การบังคับใช้ข้อจำกัดสำหรับเสถียรภาพของ solver
- การ coupling หลายโซนสำหรับการถ่ายเทความร้อนร่วม

---

### **สถาปัตยกรรมแหล่งที่มาที่เป็นทางการ**

เหมือนกับสำนักงานทะเบียนเมือง `polyMesh` รักษา **ความสมบูรณ์ของข้อมูล** ผ่านกลไกหลักหลายอย่าง:

#### **การตรวจสอบความสอดคล้อง**

ความสัมพันธ์ทั้งหมดต้องสอดคล้องกัน:
- ทุก face ต้องมี owner ที่แน่นอนหนึ่งตัว
- ทุก cell ต้องปิด
- boundary faces ต้องไม่มี neighbors

วิธี `polyMesh::checkMesh()` ดำเนินการตรวจสอบเหล่านี้:

```cpp
// Mesh consistency checking
bool polyMesh::checkMesh(const bool report) const {
    // Check face connectivity
    // Check cell closure
    // Check boundary consistency
    // Check point usage
    return isTopologicallyCorrect();
}
```

> **📂 Source:** `.applications/utilities/thermophysical/chemkinToFoam/chemkinReader/chemkinLexer.L`
> 
> **คำอธิบาย:**
> - **checkMesh()**: วิธีการตรวจสอบความสอดคล้องของ mesh
> - ตรวจสอบ connectivity ของ face, cell และ boundary
> - รายงานข้อผิดพลาดถ้า found
> 
> **แนวคิดสำคัญ:**
> - Topological consistency ถูกบังคับใช้
> - การตรวจสอบหลายอย่างถูกดำเนินการ
> - การรายงานสามารถเปิด/ปิดได้
> - คืนค่า true ถ้า mesh valid

#### **ค่าคงที่เชิงโทโพโลยี**

ความสัมพันธ์ทางคณิตศาสตร์บางอย่างต้องคงที่เสมอ:

- **สูตรของออยเลอร์สำหรับ mesh ทรงหลายหน้า**:
  $$
  V - E + F - C = 1 \quad \text{(สำหรับโดเมนที่เชื่อมต่อง่าย)}
  $$

- **การอนุรักษ์พื้นที่ผิวของ face**:
  $$
  \sum_{i \in \text{boundary}} A_i = A_{\text{total}}
  $$

- **ความสอดคล้องของปริมาตร cell**:
  $$
  \sum_{j=1}^{N_{\text{cells}}} V_j = V_{\text{domain}}
  $$

#### **การจัดระเบียบลำดับชั้น**

เหมือนกับโซนการวางผังเมือง polyMesh จัดระเบียบข้อมูลตามลำดับชั้น:

```cpp
// Geometric hierarchy
Mesh -> Zones -> Patches -> Faces -> Edges -> Points

// Topological hierarchy
Mesh -> Cells -> Faces -> Points
```

> **📂 Source:** `.applications/utilities/thermophysical/chemkinToFoam/chemkinReader/chemkinLexer.L`
> 
> **คำอธิบาย:**
> - **ลำดับชั้นเรขาคณิต**: จัดระเบียบตาม spatial decomposition
> - **ลำดับชั้นโทโพโลยี**: จัดระเบียบตาม connectivity
> - ทั้งสองลำดับชั้นมีประโยชน์สำหรับ operations ต่างกัน
> 
> **แนวคิดสำคัญ:**
> - ข้อมูลถูกจัดระเบียบเป็นลำดับชั้น
> - การเข้าถึงแบบ multi-level สามารถทำได้
> - การจัดระเบียบนี้สนับสนุน efficient algorithms

![[polymesh_hierarchical_structure.png]]
`A diagram showing the hierarchical structure of polyMesh, illustrating the relationships between Cells, Faces, Points, Zones, and Patches, scientific textbook diagram, clean vector line art, white background, high definition, flat design, educational infographic --ar 16:9`

---

## ⚙️ **Key Mechanisms: polyMesh แบบ Step-by-Step**

### **Step 1: Core Topology Storage**

คลาส `polyMesh` ทำหน้าที่เป็นโครงสร้างข้อมูล mesh พื้นฐานของ OpenFOAM โดยจัดเก็บข้อมูลโทโพโลยีที่สมบูรณ์ผ่านลำดับชั้นของข้อมูลสมาชิกที่ถูกออกแบบอย่างพิถีพิถัน

**สถาปัตยกรรมโค้ด:**
- `polyMesh` สืบทอดมาจาก `objectRegistry` (สำหรับการดำเนินงาน I/O อัตโนมัติ)
- สืบทอดมาจาก `primitiveMesh` (สำหรับความสามารถในการคำนวณทางเรขาคณิต)
- ทำให้สามารถทำหน้าที่ได้ทั้งเป็นคอนเทนเนอร์ข้อมูลและเครื่องมือคำนวณ

**ข้อมูลโทโพโลยีถาวรประกอบด้วยอาร์เรย์พื้นฐานสี่อย่าง:**

| คอมโพเนนต์ | ประเภทข้อมูล | คำอธิบาย |
|-------------|-----------------|-------------|
| `pointIOField points_` | พิกัด 3 มิติ $(x,y,z)$ | เก็บพิกัดของ vertices ทั้งหมดของ mesh |
| `faceCompactIOList faces_` | การเชื่อมต่อ vertices | บรรจุข้อมูลการเชื่อมต่อสำหรับแต่ละ face |
| `labelIOList owner_` | cell index | ระบุ "owner" cell สำหรับแต่ละ face |
| `labelIOList neighbour_` | cell index | ระบุ "neighbor" cell (-1 สำหรับ boundary faces) |

**ระบบการจัดการ Boundary:**
- `mutable polyBoundaryMesh boundary_` object: จัดการข้อมูล patch แบบมีประสิทธิภาพ
- สามารถอัปเดต boundary แบบไดนามิกได้
- ยังคง const-correctness ในฟังก์ชันสมาชิก mesh

**ข้อมูล Zone:**
- `meshPointZones`, `meshFaceZones`, `meshCellZones` objects
- ทำให้สามารถจัดกลุ่ม mesh entities สำหรับรูปแบบฟิสิกส์เฉพาะทาง

**ความสามารถขั้นสูง:**
- `globalMeshDataPtr_`: การคำนวณแบบขนาน
- `curMotionTimeIndex_` และ `oldPointsPtr_`: ติดตามการเคลื่อนที่ของ mesh

**การเข้าถึงข้อมูล:**
- ส่งคืน `const references` เพื่อป้องกันการแก้ไขโทโพโลยีโดยไม่ได้รับอนุญาต

---

### **Step 2: Owner-Neighbor Convention**

**หลักการพื้นฐาน:**
- ทุก face ใน mesh ต้องมี **owner cell** พอดีหนึ่งชุด (ระบุโดยอาร์เรย์ `owner`)
- **Internal faces** มี **neighbor cell** อีกหนึ่งชุด (ระบุโดยอาร์เรย์ `neighbour`)
- สร้างโครงสร้างกราฟมีทิศทางที่แต่ละ face เป็นการเชื่อมต่อทางเดียวจาก owner ไปยัง neighbor

**ทิศทาง Face Normal:**
- Face normals ชี้ไปยัง **neighbor cell** เสมอ
- สำหรับ internal face ระหว่าง cell 5 และ 10:
  - `owner_[faceI] = 5`
  - `neighbour_[faceI] = 10`
  - Face normal vector $\mathbf{n}_{face}$ ชี้จาก cell 5 ไปยัง cell 10

**ความสำคัญสำหรับการคำนวณ:**
- กำหนดแบบแผนเครื่องหมายสำหรับการขนส่ง convection และ diffusion
- สำคัญอย่างยิ่งสำหรับการคำนวณ flux แบบ finite volume

**Boundary Faces:**
- ค่า `neighbour` เท่ากับ `-1`
- บ่งชี้ว่าไม่มี adjacent cell อยู่นอกขอบเขตโดเมน
- เป็นของ specialized patches (walls, inlets, outlets, etc.)

**การตรวจสอบความสอดคล้อง:**
- ฟังก์ชัน `checkFaceOrientation()` ตรวจสอบความสัมพันธ์ owner-neighbor
- ตรวจสอบว่า owner indices มีค่าน้อยกว่า neighbor indices สำหรับ internal faces
- ป้องกันข้อผิดพลาดเครื่องหมายในรูปแบบเชิงตัวเลข

---

### **Step 3: Boundary Patch System**

คลาส `polyBoundaryMesh` ใช้ระบบการจัดการขอบเขตที่มีโครงสร้างซึ่งขยายความสามารถ mesh ของ OpenFOAM

**สถาปัตยกรรม:**
- สืบทอดมาจาก `PtrList<polyPatch>`
- สร้างคอนเทนเนอร์ที่จัดการ individual boundary patches เป็นวัตถุเฉพาะทาง
- แต่ละ patch มีคุณสมบัติทางฟิสิกส์และพฤติกรรมเชิงตัวเลขของตัวเอง

**ประเภทของ Patches:**

| ประเภท | คำอธิบาย | การใช้งาน |
|---------|-------------|-------------|
| **WALL** | ขอบเขตผนังแข็ง | เงื่อนไข no-slip, slip, หรือผนังขรุขระผ่าน wall functions |
| **PATCH** | เงื่อนไขขอบเขตทั่วไป | สำหรับการใช้ฟิสิกส์แบบกำหนดเอง |
| **EMPTY** | การจำลอง 2 มิติ | ระนาบสมมาตรที่มีความหนาเป็นศูนย์ |
| **CYCLIC** | เงื่อนไขขอบเขตเป็นระยะ | ทำให้สามารถจำลองเรขาคณิตที่ซ้ำกันได้ |
| **WEDGE** | แกนสมมาตร | รองรับการคำนวณแบบแกนสมมาตร |
| **SYMMETRYPLANE** | เงื่อนไขสมมาตร | สำหรับโดเมนที่สมมาตรแบบกระจก |

**เมธอดหลัก:**

**1. การค้นหา Patch:**
```cpp
// Find patch by name - O(n) search
label patchID = boundary.findPatchID("wall");
```
- ทำให้สามารถค้นหาแบบ O(n) ผ่าน boundary patches
- สำคัญสำหรับการกำหนดเงื่อนไขขอบเขตแบบไดนามิก

> **📂 Source:** `.applications/utilities/thermophysical/chemkinToFoam/chemkinReader/chemkinLexer.L`
> 
> **คำอธิบาย:**
> - **findPatchID()**: ค้นหา patch ตามชื่อ
> - คืนค่า label (index) ของ patch
> - คืนค่า -1 ถ้าไม่พบ
> 
> **แนวคิดสำคัญ:**
> - การค้นหาตามชื่อ robust กว่า hardcoding indices
> - ต้องตรวจสอบค่า -1 (patch ไม่พบ)
> - ใช้กันอย่างแพร่หลายใน OpenFOAM

**2. การแม็ป Face:**
สมการการแปลงระหว่าง local และ global indices:

$$\text{global\_face\_index} = \text{patch\_start\_index} + \text{local\_face\_index}$$

**3. การรวบรวม Boundary Cells:**
เมธอด `boundaryCells()` รวบรวมรายการของ cells ทั้งหมดที่อยู่ติดกับ boundary faces:
- วนซ้ำผ่านแต่ละ patch
- รวบรวมข้อมูล `faceCells`
- รองรับอัลกอริทึมเชิงตัวเลขเฉพาะทาง

**ประสิทธิภาพการใช้งาน:**
- ใช้หน่วยความจำอย่างมีประสิทธิภาพ
- หลีกเลี่ยงการจัดสรรหน่วยความจำมากเกินไป
- การจัดการขนาดอย่างระมัดระวังสำหรับ dynamic arrays

---

## 🧠 **Under the Hood: Topological Mathematics**

### **การจัดเรียงจุดยอดของผิว: กฎมือขวา**

สำหรับผิวที่มีจุดยอด $\mathbf{v}_1, \mathbf{v}_2, \ldots, \mathbf{v}_n$ **เวกเตอร์ปกติของผิว** $\mathbf{n}$ ถูกคำนวณโดยใช้ **กฎมือขวา**:

$$
\mathbf{n} = \sum_{i=1}^{n} \mathbf{v}_i \times \mathbf{v}_{i+1} \quad \text{(โดยที่ } \mathbf{v}_{n+1} = \mathbf{v}_1 \text{)}
$$

**ข้อกำหนดที่สำคัญ**: จุดยอดต้องถูกจัดเรียงให้ $\mathbf{n}$ ชี้ **ออกจากเซลล์เจ้าของ**

สิ่งนี้จะสร้าง **แบบแผนเครื่องหมาย** สำหรับการคำนวณ flux ทั้งหมด:

- **Flux บวก**: การไหลในทิศทางของ $\mathbf{n}$ (เจ้าของ → ข้างเคียง)
- **Flux ลบ**: การไหลในทิศทางตรงข้ามกับ $\mathbf{n}$ (ข้างเคียง → เจ้าของ)

### **การ Implement ใน OpenFOAM**

```cpp
// Calculate face area normal vectors
vectorField Sf = mesh.Sf();  // Face area vectors
vectorField nf = mesh.nf();  // Unit normal vectors

// Face areas (magnitude of Sf)
scalarField magSf = mesh.magSf();
```

> **📂 Source:** `.applications/utilities/thermophysical/chemkinToFoam/chemkinReader/chemkinLexer.L`
> 
> **คำอธิบาย:**
> - **Sf()**: คืนค่า face area vectors (magnitude + direction)
> - **nf()**: คืนค่า unit normal vectors
> - **magSf()**: คืนค่า face areas (magnitude only)
> - เวกเตอร์ area ชี้จาก owner → neighbor เสมอ
> 
> **แนวคิดสำคัญ:**
> - Face area vectors = area × unit normal
> - ทิศทางถูกกำหนดโดย owner-neighbor convention
> - ใช้สำหรับการคำนวณ flux
> - เป็นพื้นฐานของ finite volume method

ฟังก์ชัน `Sf()` คืนค่าเวกเตอร์พื้นที่ผิว $\mathbf{S} = \mathbf{n} \cdot |\mathbf{S}|$ โดยที่ $|\mathbf{S}|$ คือพื้นที่ผิว เวกเตอร์นี้จะชี้จากเซลล์เจ้าของไปยังเซลล์ข้างเคียงเสมอ

---

### **การเชื่อมต่อระหว่างเซลล์-ผิว: Incidence Matrix**

โทโพโลยีของ mesh สามารถแสดงเป็น **incidence matrix** $E$ โดยที่:

$$
E_{ij} = \begin{cases}
+1 & \text{ถ้าผิว } j \text{ ชี้ออกจากเซลล์ } i \\
-1 & \text{ถ้าผิว } j \text{ ชี้เข้าสู่เซลล์ } i \\
0 & \text{กรณีอื่นๆ}
\end{cases}
$$

เมทริกซ์นี้เข้ารหัส **discrete divergence operator**:

$$
(\nabla \cdot \mathbf{u})_i = \frac{1}{V_i} \sum_{j} E_{ij} (\mathbf{u} \cdot \mathbf{S})_j
$$

**ข้อมูล Implement**: รายการ `owner_` และ `neighbour_` จัดเก็บข้อมูล incidence นี้อย่างมีประสิทธิภาพโดยไม่ต้องสร้างเมทริกซ์เต็ม

### **การจัดเก็บที่มีประสิทธิภาพใน OpenFOAM**

OpenFOAM ใช้กลไกการจัดเก็บที่มีประสิทธิภาพซึ่งหลีกเลี่ยงการใช้ sparse incidence matrix:

```cpp
// Efficient storage of connectivity information
class fvMesh
{
    // Owner and neighbor cell lists
    const labelList& owner_;
    const labelList& neighbour_;

    // Access methods
    inline const labelList& owner() const { return owner_; }
    inline const labelList& neighbour() const { return neighbour_; }

    // Get owner cell for face j
    inline label owner(const label faceI) const { return owner_[faceI]; }

    // Get neighbor cell for face j
    inline label neighbour(const label faceI) const { return neighbour_[faceI]; }
};
```

> **📂 Source:** `.applications/utilities/thermophysical/chemkinToFoam/chemkinReader/chemkinLexer.L`
> 
> **คำอธิบาย:**
> - **fvMesh**: Finite volume mesh class
> - **owner_**: Array ของ owner cell indices
> - **neighbour_**: Array ของ neighbor cell indices
> - inline methods: สำหรับ efficient access
> 
> **แนวคิดสำคัญ:**
> - เก็บ connectivity อย่างมีประสิทธิภาพ
> - หลีกเลี่ยง sparse matrix storage
> - ใช้ label lists (compressed storage)
> - การเข้าถึงแบบ inline สำหรับ performance

การดำเนินการ divergence จึงถูก implement ดังนี้:

```cpp
// Divergence calculation using owner-neighbor arrays
template<class Type>
tmp<GeometricField<Type, fvPatchField, volMesh>>
div(const surfaceScalarField& sf, const GeometricField<Type, fvsPatchField, surfaceMesh>& ssf)
{
    // For each cell, sum face fluxes with correct sign
    // Boundary faces use only owner contribution
    // Internal faces: owner contribution - neighbor contribution
}
```

> **📂 Source:** `.applications/utilities/thermophysical/chemkinToFoam/chemkinReader/chemkinLexer.L`
> 
> **คำอธิบาย:**
> - **div()**: Divergence operator
> - ใช้ owner-neighbor convention สำหรับเครื่องหมาย
> - Boundary faces: เฉพาะ owner contribution
> - Internal faces: owner - neighbor
> 
> **แนวคิดสำคัญ:**
> - Divergence = sum of face fluxes
> - เครื่องหมายถูกกำหนดโดย orientation
> - การจำแนก boundary/internal จำเป็น
> - Template function สำหรับ type flexibility

---

### **การจำแนกขอบเขต: ประเภทของ Patch**

ประเภทของ patch ต่างๆ implement ฟังก์ชัน **เงื่อนไขขอบเขตทางคณิตศาสตร์** ที่แตกต่างกัน:

| ประเภท Patch | เงื่อนไขทางคณิตศาสตร์ | ความหมายทางฟิสิกส์ |
|---|---|---|
| `wall` | $\mathbf{u} = \mathbf{0}$ (no-slip) หรือ $\mathbf{u} \cdot \mathbf{n} = 0$ (slip) | ขอบเขตของแข็ง |
| `symmetryPlane` | $\mathbf{u} \cdot \mathbf{n} = 0$, $\nabla(\mathbf{u} \cdot \mathbf{t}) \cdot \mathbf{n} = 0$ | ความสมมาตรกระจก |
| `cyclic` | $\phi_{\text{master}} = \phi_{\text{slave}}$ | โดเมนรอบระยะเวลา |
| `empty` | $\partial/\partial z = 0$ | การหดตัว 2D |
| `wedge` | ขอบเขตแกนสมมาตร | ความสมมาตรการหมุน |

### **รากฐานทางคณิตศาสตร์ของเงื่อนไขขอบเขต**

แต่ละประเภทของ patch บังคับใช้ข้อจำกัดทางคณิตศาสตร์เฉพาะ:

#### **เงื่อนไขขอบเขตของผนัง**
- **No-slip**: $\mathbf{u}|_{\text{wall}} = \mathbf{0}$
- **Free-slip**: $\mathbf{u} \cdot \mathbf{n}|_{\text{wall}} = 0$
- **Wall functions**: เงื่อนไขขอบเขตที่แก้ไขสำหรับความปั่นป่วน

#### **เงื่อนไขขอบเขตความสมมาตร**
เงื่อนไความสมมาตรบังคับให้:
$$
\mathbf{u} \cdot \mathbf{n} = 0 \quad \text{และ} \quad \frac{\partial}{\partial n}(\mathbf{u} \cdot \mathbf{t}) = 0
$$

โดยที่:
- $\mathbf{n}$ = เวกเตอร์ปกติของผิว
- $\mathbf{t}$ = เวกเตอร์สัมผัสในระนาบของความสมมาตร

#### **เงื่อนไขขอบเขตรอบระยะเวลา**
สำหรับ cyclic patches ค่าของ field เป็นรอบระยะเวลา:
$$
\phi_{\text{master}}(x, y, z) = \phi_{\text{slave}}(x', y', z')
$$

สิ่งนี้สร้างโดเมนรอบระยะเวลาซึ่งข้อมูลผ่านไปอย่างราบรื่นระหว่าง master และ slave patches

### **สถาปัตยกรรมการ Implement**

ระบบเงื่อนไขขอบเขตใช้ factory pattern:

```cpp
// Boundary condition factory pattern
template<class Type>
class fvPatchField
{
public:
    // Runtime selection mechanism
    virtual tmp<fvPatchField<Type>> clone() const = 0;

    // Evaluate boundary condition
    virtual void updateCoeffs();

    // Specific boundary conditions override these
    virtual void evaluate();
};
```

> **📂 Source:** `.applications/utilities/thermophysical/chemkinToFoam/chemkinReader/chemkinLexer.L`
> 
> **คำอธิบาย:**
> - **fvPatchField**: Base class สำหรับ boundary conditions
> - **clone()**: Virtual constructor pattern
> - **updateCoeffs()**: อัปเดตค่าสัมประสิทธิ์ BC
> - **evaluate()**: บังคับใช้ BC
> 
> **แนวคิดสำคัญ:**
> - Polymorphism สำหรับ BC types ต่างกัน
> - Runtime type selection (RTTI)
> - Template สำหรับ field types ต่างกัน
> - Virtual functions สำหรับ customization

เงื่อนไขขอบเขตเฉพาะถูก implement ใน derived classes:

```cpp
// Wall boundary condition implementation
class wallFvPatchField : public fvPatchField<Type>
{
    virtual void evaluate()
    {
        // Enforce wall boundary condition
        this->operator==(wallValue_);
    }
};

// Symmetry plane boundary condition implementation
class symmetryPlaneFvPatchField : public fvPatchField<Type>
{
    virtual void evaluate()
    {
        // Enforce symmetry conditions
        // n · u = 0, ∇(t · u) · n = 0
    }
};
```

> **📂 Source:** `.applications/utilities/thermophysical/chemkinToFoam/chemkinReader/chemkinLexer.L`
> 
> **คำอธิบาย:**
> - **wallFvPatchField**: Derived class สำหรับ wall BC
> - **symmetryPlaneFvPatchField**: Derived class สำหรับ symmetry BC
> - **evaluate()**: Override เพื่อใช้ BC เฉพาะ
> 
> **แนวคิดสำคัญ:**
> - Inheritance จาก base class
> - Override virtual functions
> - แต่ละ BC type มี implementation เฉพาะ
> - Polymorphic behavior ผ่าน base class pointer

---

### **การตรวจสอบความสอดคล้องทางโทโพโลยี**

โทโพโลยีของ mesh ต้องเป็นไปตาม **Euler characteristic** เพื่อความสอดคล้องทางเรขาคณิตที่เหมาะสม:

$$
V - E + F = 1 - 2g
$$

โดยที่:
- $V$ = จำนวนจุดยอด (Vertices)
- $E$ = จำนวนขอบ (Edges)
- $F$ = จำนวนผิว (Faces)
- $g$ = genus (จำนวนรูใน mesh)

### **เครื่องมือตรวจสอบใน OpenFOAM**

```cpp
// Topology consistency checker
bool checkMesh(const polyMesh& mesh)
{
    // Check cell-face connectivity
    // Check boundary condition consistency
    // Check face vertex ordering
}
```

> **📂 Source:** `.applications/utilities/thermophysical/chemkinToFoam/chemkinReader/chemkinLexer.L`
> 
> **คำอธิบาย:**
> - **checkMesh()**: Mesh validation function
> - ตรวจสอบ topology และ geometry
> - รายงาน errors และ warnings
> 
> **แนวคิดสำคัญ:**
> - การตรวจสอบความสอดคล้องเป็นสิ่งสำคัญ
> - Topology ต้องถูกต้องก่อนการจำลอง
> - การรายงาน errors ช่วยในการ debug
> - เครื่องมือมาตรฐานใน OpenFOAM

กรอบการทำงานทางโทโพโลยีนี้ช่วยให้มั่นใจว่าคณิตศาสตร์เชิงกระจายของการคำนวณ CFD ยังคงสอดคล้องและมีความหมายทางฟิสิกส์ตลอดการจำลอง

---

## ⚠️ **Common Pitfalls and Solutions**

ส่วนนี้จะกล่าวถึงข้อผิดพลาดทั่วไปที่นักพัฒนา OpenFOAM พบเจอและให้วิธีแก้ไขที่ใช้งานได้จริงเพื่อหลีกเลี่ยงข้อผิดพลาดเหล่านั้น

---

### **ข้อผิดพลาดที่ 1: การเข้าใจผิดทิศทางของ Face**

ทิศทางของ face ใน OpenFOAM จะตามข้อตกลงที่เคร่งครัดซึ่ง **face normals จะชี้จาก owner cells ไปยัง neighbor cells** การละเลยข้อตกลงนี้จะนำไปสู่การคำนวณ flux ที่ผิดพลาดและการ diverge ของ solver

> [!WARNING] ข้อเข้าใจสำคัญ
> OpenFOAM รักษา **dual perspective** สำหรับ internal faces:
> - **Owner cell** เห็น face normal ชี้ออกไปด้านนอก
> - **Neighbor cell** เห็น face normal เดียวกันชี้เข้าด้านใน (negative flux จากมุมมองของมัน)
>
> ข้อตกลงนี้ทำให้มั่นใจได้ถึงการอนุรักษ์แบบท้องถิ่นในขณะที่รักษาข้อตกลงเครื่องหมายที่ถูกต้องสำหรับมุมมองของแต่ละ cell

#### **OpenFOAM Code Implementation**

```cpp
// ❌ WRONG: Assuming face normal direction
void wrongFluxCalculation(const polyMesh& mesh)
{
    const vectorField& Sf = mesh.faceAreas();

    forAll(mesh.owner(), faceI)
    {
        // ❌ WRONG: Not accounting for owner/neighbor direction
        scalar flux = U[faceI] & Sf[faceI];  // Sign might be wrong!

        // For boundary faces this might be correct or reversed
        // depending on how the face was defined
    }
}

// ✅ CORRECT: Using owner-based sign convention
void correctFluxCalculation(const polyMesh& mesh)
{
    const vectorField& Sf = mesh.faceAreas();
    const labelList& owner = mesh.owner();
    const labelList& neighbour = mesh.neighbour();

    forAll(owner, faceI)
    {
        label own = owner[faceI];
        label nei = neighbour[faceI];

        // Face normal points from owner to neighbor
        // So flux from owner's perspective:
        scalar flux = U[faceI] & Sf[faceI];  // Positive = out of owner

        if (nei != -1)  // Internal face
        {
            // Owner sees positive flux as outflow
            // Neighbor sees same flux as inflow (negative)
            phi[own] += flux;
            phi[nei] -= flux;  // Negative for neighbor
        }
        else  // Boundary face
        {
            // Only owner side exists
            phi[own] += flux;
        }
    }
}
```

> **📂 Source:** `.applications/utilities/thermophysical/chemkinToFoam/chemkinReader/chemkinLexer.L`
> 
> **คำอธิบาย:**
> - **WRONG approach**: ไม่สนใจ owner-neighbor direction
> - **CORRECT approach**: ใช้ convention อย่างเคร่งครัด
> - Internal faces: owner +, neighbor -
> - Boundary faces: owner only
> 
> **แนวคิดสำคัญ:**
> - Face orientation ถูกกำหนดโดย owner→neighbor
> - Flux เครื่องหมายขึ้นกับ perspective
> - Conservation ผ่านการบวก/ลบที่ถูกต้อง
> - Boundary faces มีเพียง owner contribution

---

### **ข้อผิดพลาดที่ 2: การละเลยการแบ่งข้อมูลสำหรับ Parallel**

การ implement แบบ parallel ของ OpenFOAM ใช้ **domain decomposition** ซึ่งแต่ละ processor จะจัดการ subset ของ mesh โค้ดที่ไม่คำนึงถึงสิ่งนี้จะให้ผลลัพธ์ที่ผิดพลาดหรือล้มเหลวโดยสิ้นเชิงในการรันแบบ parallel

> [!INFO] การเขียนโปรแกรมแบบ parallel-aware ต้องการความเข้าใจ:
> 1. **Local vs Global**: แต่ละ processor สามารถเข้าถึงเฉพาะ local cells และ faces ของมันเอง
> 2. **Ghost Cells**: Boundary cells จาก processors ที่อยู่ติดกันที่จำเป็นสำหรับการคำนวณ
> 3. **Processor Patches**: Patches พิเศษที่เชื่อมต่อ processors ที่แตกต่างกัน
> 4. **Global Operations**: Reductions, broadcasts และ synchronizations ข้าม processors

#### **OpenFOAM Code Implementation**

```cpp
// ❌ WRONG: Assuming single-processor mesh
void serialOnlyCode(const polyMesh& mesh)
{
    // Process all cells
    forAll(mesh.cells(), cellI)
    {
        processCell(cellI);
    }

    // ❌ FAILS in parallel: cells() returns only local cells!
    // Missing processor boundary faces and ghost cells
}

// ✅ CORRECT: Parallel-aware iteration
void parallelAwareCode(const polyMesh& mesh)
{
    // ✅ Process local cells
    forAll(mesh.cells(), cellI)
    {
        processLocalCell(cellI);
    }

    // ✅ Handle processor boundaries
    forAll(mesh.boundaryMesh(), patchi)
    {
        const polyPatch& pp = mesh.boundaryMesh()[patchi];

        if (isA<processorPolyPatch>(pp))  // Processor boundary
        {
            // These faces connect to neighboring processors
            forAll(pp, localFaceI)
            {
                label faceI = pp.start() + localFaceI;
                processProcessorFace(faceI);
            }
        }
    }

    // ✅ Use global mesh data for parallel operations
    if (mesh.globalData().valid())
    {
        const globalMeshData& gmd = mesh.globalData();

        // Perform parallel reductions, gathers, scatters
        scalar globalMin = gMin(someField);
        scalar globalMax = gMax(someField);
    }
}
```

> **📂 Source:** `.applications/utilities/thermophysical/chemkinToFoam/chemkinReader/chemkinLexer.L`
> 
> **คำอธิบาย:**
> - **WRONG approach**: สมมติ mesh อยู่ใน processor เดียว
> - **CORRECT approach**: จัดการ domain decomposition
> - **isA<processorPolyPatch>**: ตรวจสอบ processor boundaries
> - **globalData()**: Global mesh operations
> 
> **แนวคิดสำคัญ:**
> - Domain decomposition แบ่ง mesh ข้าม processors
> - Local cells เท่านั้นที่เข้าถึงได้โดยตรง
> - Processor patches เชื่อมต่อ sub-domains
> - Ghost cells ช่วยใน stencil operations
> - Global reductions สำหรับ collective operations

---

### **ข้อผิดพลาดที่ 3: การ Hardcode Patch Indices**

การเรียงลำดับของ patch ใน OpenFOAM อาจเปลี่ยนแปลงได้ตามโครงสร้างของ case และวิธีการกำหนด patches ใน boundary file การ **hardcode patch indices** ทำให้โค้ดเปราะบางและมีแนวโน้มที่จะเสียหาย

> [!TIP] แนวทางปฏิบัติที่ดีสำหรับการจัดการ patches:
> 1. **ใช้ `findPatchID()` เสมอ**: ค้นหา patches ตามชื่อ boundary file ของพวกมัน
> 2. **ตรวจสอบการมีอยู่**: ตรวจสอบว่า `findPatchID()` คืนค่า -1 (ไม่พบ patch)
> 3. **จัดการ optional patches**: บาง patches อาจไม่มีอยู่ในทุก cases
> 4. **เอกสาร patches ที่คาดหวัง**: เอกสารชัดเจนว่าโค้ดของคุณคาดหวัง patches ใด

แนวทาปทำให้โค้ดของคุณแข็งแกร่งต่อการเปลี่ยนแปลงโครงสร้าง case และทำให้มั่นใจได้ถึงความเข้ากันได้ข้าม OpenFOAM installations ที่แตกต่างกัน

#### **OpenFOAM Code Implementation**

```cpp
// ❌ WRONG: Assuming constant patch ordering
void fragileBoundaryCode(const polyMesh& mesh)
{
    // ❌ WRONG: Patch indices might change!
    label inletPatch = 0;   // Might not always be true
    label outletPatch = 1;  // Might not always be true
    label wallPatch = 2;    // Might not always be true

    processPatch(mesh.boundaryMesh()[inletPatch]);   // Risky!
    processPatch(mesh.boundaryMesh()[outletPatch]);  // Risky!
    processPatch(mesh.boundaryMesh()[wallPatch]);    // Risky!
}

// ✅ CORRECT: Find patches by name
void robustBoundaryCode(const polyMesh& mesh)
{
    // ✅ Find patches by name (from case files)
    label inletPatch = mesh.boundaryMesh().findPatchID("inlet");
    label outletPatch = mesh.boundaryMesh().findPatchID("outlet");
    label wallPatch = mesh.boundaryMesh().findPatchID("walls");

    // ✅ Check that patches exist
    if (inletPatch == -1)
    {
        FatalErrorInFunction
            << "Cannot find 'inlet' patch" << endl
            << abort(FatalError);
    }

    // ✅ Process with confidence
    processPatch(mesh.boundaryMesh()[inletPatch]);   // Safe!
    processPatch(mesh.boundaryMesh()[outletPatch]);  // Safe!

    // ✅ Handle optional patches
    if (wallPatch != -1)
    {
        processPatch(mesh.boundaryMesh()[wallPatch]);  // Conditional
    }
}
```

> **📂 Source:** `.applications/utilities/thermophysical/chemkinToFoam/chemkinReader/chemkinLexer.L`
> 
> **คำอธิบาย:**
> - **WRONG approach**: Hardcode patch indices
> - **CORRECT approach**: ค้นหาตามชื่อ
> - **findPatchID()**: คืนค่า patch index หรือ -1
> - ตรวจสอบ -1 ก่อนการใช้งาน
> 
> **แนวคิดสำคัญ:**
> - Patch ordering ไม่คงที่
> - ชื่อ patch คือ identifier ที่เชื่อถือได้
> - การตรวจสอบ existence จำเป็น
> - Optional patches ต้องมี conditional logic
> - รายงาน errors ที่ชัดเจน

#### **การเปรียบเทียบวิธีการค้นหา Patches**

| วิธีการ | ความปลอดภัย | ความยืดหยุ่น | ความน่าเชื่อถือ | คำแนะนำ |
|---------|------------|------------|--------------|-----------|
| **Hardcode Index** | ❌ ต่ำ | ❌ ต่ำ | ❌ ต่ำ | ❌ ห้ามใช้ |
| **findPatchID() + ตรวจสอบ** | ✅ สูง | ✅ สูง | ✅ สูง | ✅ แนะนำ |
| **findPatchID() อย่างเดียว** | ⚠️ กลาง | ✅ สูง | ⚠️ กลาง | ⚠️ ใช้ด้วยความระมัดระวัง |

---

## 🎯 **Why This Matters for CFD**

### **ประโยชน์ทางวิศวกรรม 1: การจัดการเรขาคณิตที่ซับซ้อน**

> [!INFO] **สถานการณ์จริง: การรองรับเรขาคณิตอุตสาหกรรม**

```cpp
class IndustrialMeshProcessor
{
public:
    void processComplexMesh(const polyMesh& mesh)
    {
        // ✅ Handle polyhedral cells (not just hexahedra)
        forAll(mesh.cells(), cellI)
        {
            const cell& c = mesh.cells()[cellI];

            // Cells can have arbitrary number of faces
            label nFaces = c.size();  // Could be 4 (tet), 6 (hex), or more

            // Each face can have arbitrary number of points
            forAll(c, faceI)
            {
                label faceLabel = c[faceI];
                const face& f = mesh.faces()[faceLabel];
                label nPoints = f.size();  // Could be 3 (tri), 4 (quad), or more

                // This flexibility allows capturing:
                // - Complex industrial geometries
                // - Adaptive mesh refinement
                // - Overset/chimera meshes
                // - Fractured media
            }
        }

        // ✅ Support multiple boundary types
        forAll(mesh.boundaryMesh(), patchi)
        {
            const polyPatch& pp = mesh.boundaryMesh()[patchi];

            if (isA<wallPolyPatch>(pp))
            {
                // Apply wall functions, log-law, etc.
                processWallBoundary(pp);
            }
            else if (isA<symmetryPlanePolyPatch>(pp))
            {
                // Apply symmetry conditions
                processSymmetryBoundary(pp);
            }
            else if (isA<cyclicPolyPatch>(pp))
            {
                // Handle periodicity
                processCyclicBoundary(pp);
            }
            // ... many more specialized patch types
        }
    }
};
```

> **📂 Source:** `.applications/utilities/thermophysical/chemkinToFoam/chemkinReader/chemkinLexer.L`
> 
> **คำอธิบาย:**
> - **Polyhedral cells**: รองรับ cells ที่มี faces จำนวนเท่าใดก็ได้
> - **Arbitrary faces**: Faces สามารถมี points จำนวนเท่าใดก็ได้
> - **Patch types**: หลายประเภทของ boundaries
> - **isA<>**: Type checking สำหรับ polymorphism
> 
> **แนวคิดสำคัญ:**
> - Geometric flexibility คือคีย์
> - Polyhedral meshes สำหรับความซับซ้อน
> - Type-safe boundary handling
> - รองรับ industrial geometries

**ความสามารถของโครงสร้าง polyMesh:**

- **Hybrid meshing**: ผสมผสานพื้นที่ทรงสี่เหลี่ยมแบบโครงสร้างกับโซนทรงสี่เหลี่ยม/ทรงหลายหน้าแบบไม่มีโครงสร้าง
- **Local refinement**: ละเอียดในพื้นที่สำคัญ (ชั้นขอบเขต, ชั้นเฉือน) ขณะที่รักษาเซลล์ที่หยาบขึ้นในที่อื่น
- **Geometric fidelity**: รักษาพื้นผิวโค้งและลักษณะเล็กๆ โดยไม่ต้องใช้จำนวนเซลล์มากเกินไป

**การแยกส่วนเรขาคณิตจากฟิสิกส์:**

| ประเภทขอบเขตทางกายภาพ | เงื่อนไขทางคณิตศาสตร์ | การ implement ใน OpenFOAM |
|----------------------|-----------------------|------------------------|
| ผนัง no-slip          | $\mathbf{u} = \mathbf{0}$ | `fixedValue` กับ `uniform (0 0 0)` |
| ผนัง slip             | $\mathbf{u} \cdot \mathbf{n} = 0$ | เงื่อนไข `slip` |
| ระนาบสมมาตร        | $\mathbf{u} \cdot \mathbf{n} = 0$, $\nabla\phi \cdot \mathbf{n} = 0$ | `symmetryPlane` |
| ขอบเขตเป็นคาบ     | $\phi_{\text{left}} = \phi_{\text{right}}$ | `cyclic` กับการแปลง |

---

### **ประโยชน์ทางวิศวกรรม 2: ความสามารในการขยายแบบขนาน**

> [!INFO] **การคำนวณความเร็วสูง: การจัดการ mesh แบบกระจาย**

```cpp
class ParallelMeshManager
{
public:
    void distributeMesh(const polyMesh& mesh, const label nProcs)
    {
        // ✅ Domain decomposition
        // Each processor gets a subset of cells
        // Processor boundaries become special patches

        // Original mesh (1 million cells):
        // - Processor 0: cells 0-249,999
        // - Processor 1: cells 250,000-499,999
        // - Processor 2: cells 500,000-749,999
        // - Processor 3: cells 750,000-999,999

        // Each sub-mesh has:
        // - Local cells (owned by this processor)
        // - Processor boundary faces (connecting to neighbors)
        // - Ghost cells (needed for stencil computations)

        // ✅ Parallel communication patterns
        // 1. Point-to-point: Exchange boundary data with neighbors
        // 2. Collective: Global reductions (sum, min, max)
        // 3. All-to-all: Redistribution during load balancing

        // ✅ Load balancing
        // Evaluate computational cost per cell
        // Redistribute cells to balance workload
        // Update processor boundaries automatically
    }
};
```

> **📂 Source:** `.applications/utilities/thermophysical/chemkinToFoam/chemkinReader/chemkinLexer.L`
> 
> **คำอธิบาย:**
> - **Domain decomposition**: แบ่ง mesh ข้าม processors
> - **Sub-meshes**: แต่ละ processor มี local mesh
> - **Ghost cells**: Mirror cells จาก neighbors
> - **Communication patterns**: รูปแบบการสื่อสารแบบขนาน
> 
> **แนวคิดสำคัญ:**
> - Decomposition เพื่อ parallelization
> - Communication overhead ต้องน้อย
> - Load balancing สำหรับ efficiency
> - Scalability สูง

**กลยุทธ์การแบ่งโดเมน:**

- **เซลล์ภายใน**: เซลล์ที่เป็นเจ้าของอย่างสมบูรณ์สำหรับ processor นี้จัดการการคำนวณทั้งหมด
- **เซลล์ขอบเขต**: เซลล์ที่ส่วนต่อประสาน processor ที่ต้องการการแลกเปลี่ยนข้อมูล
- **เซลล์ผี**: เซลล์กระจกจาก processor ข้างเคียงสำหรับการดำเนินการ stencil

**รูปแบบการสื่อสารสำหรับการ discretization ปริมาตรจำกัด:**

```cpp
// Finite volume communication
class FVCommunicator {
    void exchangeBoundaryData() {
        // Each processor sends boundary cell values to neighbors
        // Receives boundary values from neighbors
        // Updates ghost cell values for next iteration

        for (const auto& neighborProc : processorNeighbors) {
            MPI_Isend(localBoundaryData, neighborProc);
            MPI_Irecv(ghostCellData, neighborProc);
        }
        MPI_Waitall(); // Synchronize all communications
    }
};
```

> **📂 Source:** `.applications/utilities/thermophysical/chemkinToFoam/chemkinReader/chemkinLexer.L`
> 
> **คำอธิบาย:**
> - **MPI_Isend/Irecv**: Non-blocking communication
> - **Processor neighbors**: Adjacent processors
> - **Local/Ghost data**: Boundary exchange
> - **MPI_Waitall**: Synchronization
> 
> **แนวคิดสำคัญ:**
> - Non-blocking communication สำหรับ performance
> - Ghost cell updates สำหรับ stencil operations
> - Synchronization จำเป็นสำหรับ consistency
> - Minimize communication overhead

**Load Balancing แบบไดนามิก:**

- **โมเดลต้นทุน**: ประเมินต้นทุนการคำนวณต่อเซลล์ตามความซับซ้อนของฟิสิกส์
- **การกระจายใหม่**: แบ่งพาร์ติชัน mesh ใหม่เพื่อสมดุลภาระขณะที่ลดการเคลื่อนย้ายข้อมูล
- **การย้ายข้อมูลโปร่งใส**: อัปเดตโครงสร้างข้อมูลทั้งหมดระหว่างการกระจายใหม่

---

### **ประโยชน์ทางวิศวกรรม 3: การปรับ mesh และการเคลื่อนที่**

> [!INFO] **การจำลองแบบไดนามิก: การจัดการการเปลี่ยนแปลง mesh**

```cpp
class AdaptiveMeshSolver
{
public:
    void adaptMeshBasedOnSolution(const polyMesh& mesh)
    {
        // ✅ Refinement: Split cells as needed
        // Based on solution gradients, error estimators, etc.

        // Original cell → 8 sub-cells (3D refinement)
        // Update all connectivity:
        // - New points, faces, cells
        // - New owner/neighbor relationships
        // - Update boundary patches

        // ✅ Coarsening: Merge cells where possible
        // Reverse of refinement
        // Maintain mesh quality and validity

        // ✅ Mesh motion: Move points without changing topology
        // For FSI, moving boundaries, etc.
        mesh.movePoints(newPointPositions);

        // ✅ Topology changes: Add/remove cells
        // For crack propagation, phase change, etc.
        // Requires careful connectivity updates

        // OpenFOAM handles all of these through polyMesh interface
        // Solvers don't need to know implementation details
    }
};
```

> **📂 Source:** `.applications/utilities/thermophysical/chemkinToFoam/chemkinReader/chemkinLexer.L`
> 
> **คำอธิบาย:**
> - **Refinement**: แบ่ง cells สำหรับความละเอียดสูงขึ้น
> - **Coarsening**: รวม cells สำหรับ efficiency
> - **Mesh motion**: เคลื่อน points โดยไม่เปลี่ยน topology
> - **Topology changes**: เพิ่ม/ลบ cells
> 
> **แนวคิดสำคัญ:**
> - Dynamic meshing สำหรับ complex physics
> - Topology updates ต้องถูกต้อง
> - Interface consistency เป็นสิ่งสำคัญ
> - OpenFOAM abstracts complexity

**Adaptive Mesh Refinement (AMR):**

| เกณฑ์การละเอียด | คุณสมบัติทางกายภาพ | การปรับขนาดเซลล์ |
|------------------|------------------------|-------------------|
| $\nabla \cdot \mathbf{u}$ | การหมุนเวียน/เฉือนสูง | $h \rightarrow h/2$ |
| $\nabla T$ | การไล่ระดับความร้อน | $h \rightarrow h/2$ |
| $\nabla \alpha$ | การไล่ระดับอินเตอร์เฟส (multiphase) | $h \rightarrow h/4$ |
| $|\mathbf{u}|$ | พื้นที่ความเร็วสูง | รักษาตามเดิม |

**อัลกอริทึมการละเอียด:**
1. แบ่งเซลล์แม่เป็น 8 octants (ใน 3D)
2. สร้างหน้าใหม่ระหว่างพื้นที่ที่ละเอียดและไม่ละเอียด
3. ตรวจสอบให้แน่ใจว่า hanging faces ถูกจัดการอย่างเหมาะสม
4. อัปเดตข้อมูลฟิลด์ทั้งหมดผ่านการอินเตอร์โพเลชัน

**Mesh Motion สำหรับ FSI:**

```cpp
// Arbitrary Lagrangian-Eulerian formulation
class MovingMeshSolver {
    void solveMovingMesh() {
        // Mesh velocity: $\mathbf{u}_m = \frac{\partial \mathbf{x}}{\partial t}$
        // Mesh quality metrics: aspect ratio, skewness, non-orthogonality

        for (label i = 0; i < mesh.nPoints(); i++) {
            point& p = mesh.points()[i];
            vector displacement = calculateDisplacement(p, time);
            p += displacement * dt;
        }

        // Update geometric coefficients
        mesh.updateCells();
        mesh.updateFaces();

        // Conservation on moving mesh:
        // $\frac{\partial \rho}{\partial t} + \nabla \cdot (\rho (\mathbf{u} - \mathbf{u}_m)) = 0$
    }
};
```

> **📂 Source:** `.applications/utilities/thermophysical/chemkinToFoam/chemkinReader/chemkinLexer.L`
> 
> **คำอธิบาย:**
> - **Mesh velocity**: ความเร็วของ grid points
> - **Quality metrics**: ตัวชี้วัดคุณภาพ mesh
> - **Update coefficients**: อัปเดต geometric data
> - **ALE formulation**: Conservation equations
> 
> **แนวคิดสำคัญ:**
> - Mesh motion สำหรับ moving boundaries
> - Quality preservation เป็นสิ่งสำคัญ
> - Geometric updates ต้องถูกต้อง
> - Conservation บน moving mesh

**Dynamic Mesh Topology:**

- **การเพิ่ม/ลบชั้น**: เพิ่มหรือลบชั้นเซลล์ใกล้ขอบเขตสำหรับขอบเขตที่เคลื่อนที่
- **การเปลี่ยนแปลง topology**: แบ่งขอบ ลบหน้าสำหรับการเปิดรอยร้าว
- **การสร้าง mesh ใหม่อัตโนมัติ**: การสร้าง mesh ใหม่ในเครื่องทั้งหมดสำหรับการเสียรูปขั้นรุนแรง

---

## 💡 **Computational Implications**

อุปมานสำนักงานทะเบียนเมืองนี้อธิบายว่าเหตุใด `polyMesh` จึงเป็นพื้นฐานที่สำคัญมากสำหรับ OpenFOAM:

### **การคำนวณ Flux**

การครอบครองของ face กำหนดทิศทางของ flux:

$$
\phi_f = \mathbf{F}_f \cdot \mathbf{S}_f \quad \text{where} \quad \mathbf{S}_f \text{ ชี้จาก owner ไปยัง neighbor}
$$

- **$\\phi_f$**: flux ผ่าน face f
- **$\\mathbf{F}_f$**: เวกเตอร์ฟิลด์ที่ face f
- **$\\mathbf{S}_f$**: เวกเตอร์พื้นที่ผิวของ face f (ชี้จาก owner ไป neighbor)

### **การดำเนินการ Gradient**

การเชื่อมต่อของ cell กำหนด gradient stencils:

$$
\nabla \phi_P = \frac{1}{V_P} \sum_{f \in \partial P} \phi_f \mathbf{S}_f
$$

- **$\\nabla \phi_P$**: gradient ของฟิลด์ $\\phi$ ที่จุดศูนย์กลาง cell P
- **$V_P$**: ปริมาตรของ cell P
- **$\\phi_f$**: ค่าฟิลด์ $\\phi$ ที่ face f
- **$\\mathbf{S}_f$**: เวกเตอร์พื้นที่ผิวของ face f

### **การแบ่งส่วนขนาน**

อุปมานทะเบียนขยายไปถึงการประมวลผลแบบกระจาย - แต่ละโปรเซสเซอร์ได้รับ "sub-registry" พร้อมขอบเขตและโปรโตคอลการสื่อสารที่ชัดเจน

### **การ Morphing ของ Mesh**

การดำเนินการแบบไดนามิกของ mesh อัปเดตทะเบียนในขณะที่รักษาความสอดคล้องเชิงโทโพโลยี - เหมือนกับการอัปเดตบันทึกทรัพย์สินหลังการพัฒนาเมืองใหม่

---

`polyMesh` ในฐานะอุปมาน "สำนักงานทะเบียนเมือง" จับภาพบทบาทของมันในฐานะ **รากฐานที่เป็นทางการและสอดคล้องเชิงโทโพโลยี** ซึ่งการคำนวณ CFD ทั้งหมดใน OpenFOAM ถูกสร้างขึ้น