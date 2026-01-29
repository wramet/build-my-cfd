# Module 02: Meshing and Case Setup (การสร้างเมชและการตั้งค่าเคส)

> [!TIP] | ทำไม Meshing สำคัญใน OpenFOAM?
> Meshing เป็นพื้นฐางที่สำคัญที่สุดในการจำลอง CFD เพราะ:
> - **ความแม่นยำของผลลัพธ์** ขึ้นอยู่กับคุณภาพของเมชโดยตรง เมชที่มีคุณภาพต่ำ (High skewness/low orthogonality) ทำให้ผลลัพธ์มีความคลาดเคลื่อนสูง
> - **ความเสถียรของการคำนวณ** เมชที่ไม่ดีอาจทำให้ Solver  diverge หรือคำนวณไม่ลงตัว (Simulation crash)
> - **ประสิทธิภาพการคำนวณ** เมชที่มีจำนวน Cell มากเกินไปทำให้ใช้เวลาคำนวณนาน แต่ถ้าน้อยเกินไปก็จะไม่ได้ผลลัพธ์ที่แม่นยำ การจัดสรร Refinement Regions จึงมีความสำคัญ
> - **การตั้งค่าเคส (Case Setup)** ที่ถูกต้องเป็นหัวใจสำคัญในการบอก Solver ว่าจะคำนวณอย่างไร รวมถึงการ Monitor ผลลัพธ์แบบ Real-time ด้วย Function Objects
>
> ใน Module นี้ คุณจะเรียนรู้วิธีสร้าง Mesh ที่มีคุณภาพและตั้งค่า Case อย่างถูกต้อง เพื่อให้การจำลอง CFD ของคุณประสบความสำเร็จ!

ยินดีต้อนรับสู่ **Module 02**! ในโมดูลนี้ เราจะเจาะลึกหัวใจสำคัญของการจำลอง CFD นั่นคือ **"การสร้างเมช (Meshing)"** ซึ่งเป็นขั้นตอนที่ส่งผลต่อความแม่นยำและความเสถียรของการคำนวณมากที่สุด นอกจากนี้เราจะเรียนรู้วิธีการตั้งค่า Case ขั้นสูงและการตรวจสอบคุณภาพของเมช

ตารางข้างล่างนี้เชื่อมโยง **เนื้อหาทฤษฎี (Theory)** เข้ากับ **ซอร์สโค้ดจริง (Source Code)** ของ OpenFOAM เพื่อให้คุณเห็นภาพรวมทั้งในเชิงหลักการและการนำไปใช้งานจริง

---

## 📚 ตารางนำทาง (Navigation Table)

> [!NOTE] | **📂 OpenFOAM Context: Meshing Tools & Case Structure**
> ตารางนี้ครอบคลุม **Domain D: Meshing** และ **Domain C: Simulation Control**:
> - **Meshing Utilities** → `applications/utilities/mesh/...` (เครื่องมือสร้างและตรวจสอบเมช)
> - **Mesh Directories** → `constant/polyMesh/` (เก็บไฟล์เมชหลัก: points, faces, owner, neighbour)
> - **Mesh Dictionary Files** → `system/blockMeshDict`, `system/snappyHexMeshDict` (ตั้งค่าการสร้างเมช)
> - **Function Objects** → `system/controlDict` (ตั้งค่าการ Monitor ผลลัพธ์แบบ Real-time)
> - **Quality Checking** → `checkMesh` (ยูทิลิตี้ตรวจสอบคุณภาพเมช)

| หัวข้อ (Topic) | เอกสารทฤษฎี (Theory & Concepts) | โค้ดที่เกี่ยวข้อง (Implementation & Tutorials) |
| :--- | :--- | :--- |
| **1. พื้นฐานการสร้างเมช** | [**01_MESHING_FUNDAMENTALS**](./CONTENT/01_MESHING_FUNDAMENTALS/01_Introduction_to_Meshing.md)<br>เรียนรู้โครงสร้างของ PolyMesh, Cell types, และ Topology | **Source Code:**<br>[`src/OpenFOAM/meshes/polyMesh`](../../src/OpenFOAM/meshes/polyMesh)<br>[`applications/utilities/mesh/manipulation/checkMesh`](../../applications/utilities/mesh/manipulation/checkMesh)<br><br>**Tutorials:**<br>Any tutorial case (`constant/polyMesh`) |
| **2. เจาะลึก blockMesh** | [**02_BLOCKMESH_MASTERY**](./CONTENT/02_BLOCKMESH_MASTERY/01_BlockMesh_Deep_Dive.md)<br>การสร้าง Structured Mesh คุณภาพสูงและการใช้ M4/Python Macro | **Source Code:**<br>[`applications/utilities/mesh/generation/blockMesh`](../../applications/utilities/mesh/generation/blockMesh)<br><br>**Tutorials:**<br>[`tutorials/incompressible/icoFoam/cavity/system/blockMeshDict`](../../tutorials/incompressible/icoFoam/cavity/system/blockMeshDict) |
| **3. พื้นฐาน snappyHexMesh** | [**03_SNAPPYHEXMESH_BASICS**](./CONTENT/03_SNAPPYHEXMESH_BASICS/01_The_sHM_Workflow.md)<br>Workflow ของการสร้าง Mesh อัตโนมัติ (Castellated -> Snap -> Layers) | **Source Code:**<br>[`applications/utilities/mesh/generation/snappyHexMesh`](../../applications/utilities/mesh/generation/snappyHexMesh)<br><br>**Tutorials:**<br>[`tutorials/incompressible/simpleFoam/motorBike`](../../tutorials/incompressible/simpleFoam/motorBike) |
| **4. sHM ขั้นสูง (Advanced)** | [**04_SNAPPYHEXMESH_ADVANCED**](./CONTENT/04_SNAPPYHEXMESH_ADVANCED/01_Layer_Addition_Strategy.md)<br>เทคนิค Layer Addition, Refinement Regions และ Multi-Region | **Source Code:**<br>[`src/mesh/snappyHexMesh/meshRefinement`](../../src/mesh/snappyHexMesh/meshRefinement)<br><br>**Tutorials:**<br>[`tutorials/heatTransfer/chtMultiRegionFoam/multiRegionHeater`](../../tutorials/heatTransfer/chtMultiRegionFoam/multiRegionHeater) |
| **5. คุณภาพและการจัดการเมช** | [**05_MESH_QUALITY_AND_MANIPULATION**](./CONTENT/05_MESH_QUALITY_AND_MANIPULATION/01_Mesh_Quality_Criteria.md)<br>เกณฑ์คุณภาพ (Orthogonality, Skewness), topoSet, และเครื่องมือจัดการเมช | **Source Code:**<br>[`applications/utilities/mesh/manipulation/checkMesh`](../../applications/utilities/mesh/manipulation/checkMesh)<br>[`applications/utilities/mesh/manipulation/topoSet`](../../applications/utilities/mesh/manipulation/topoSet)<br>[`applications/utilities/mesh/manipulation/renumberMesh`](../../applications/utilities/mesh/manipulation/renumberMesh) |
| **6. Runtime Post-processing** | [**06_RUNTIME_POST_PROCESSING**](./CONTENT/06_RUNTIME_POST_PROCESSING/01_Introduction_to_FunctionObjects.md)<br>การใช้ Function Objects เพื่อ Monitor ค่าต่างๆ ขณะรัน (Forces, Probes) | **Source Code:**<br>[`src/functionObjects`](../../src/functionObjects)<br><br>**Tutorials:**<br>[`tutorials/incompressible/pimpleFoam/RAS/propeller`](../../tutorials/incompressible/pimpleFoam/RAS/propeller) |

---

## 🛠️ วิธีการใช้งาน (How to use)

> [!NOTE] | **📂 OpenFOAM Context: Case Workflow**
> ขั้นตอนการใช้งานตรงกับ **Workflow มาตรฐานของ OpenFOAM Case**:
> - **Step 1: เตรียมเมช** → รัน `blockMesh` หรือ `snappyHexMesh` (อ่านจาก `system/blockMeshDict` หรือ `system/snappyHexMeshDict`)
> - **Step 2: ตรวจสอบคุณภาพ** → รัน `checkMesh` (ตรวจสอบ Orthogonality, Skewness, Non-orthogonality)
> - **Step 3: ตั้งค่าเคส** → แก้ไฟล์ใน `0/` (Initial/Boundary conditions), `constant/` (Mesh, Transport properties), `system/` (Control dicts)
> - **Step 4: รัน Solver** → รัน `solverName` (เช่น `simpleFoam`, `interFoam`)
> - **Step 5: Monitor ผลลัพธ์** → ใช้ Function Objects ใน `controlDict` หรือ `paraFoam` เพื่อดูผลลัพธ์

1.  **อ่านทฤษฎี**: เริ่มต้นจากลิงก์ในคอลัมน์ "เอกสารทฤษฎี" เพื่อทำความเข้าใจ Concept
2.  **ดูโค้ดจริง**: คลิกที่ลิงก์ในคอลัมน์ "โค้ดที่เกี่ยวข้อง" เพื่อดูว่า OpenFOAM เขียน C++ อย่างไร หรือดูตัวอย่างการตั้งค่าใน Tutorial
3.  **ลงมือทำ**: ลองรัน Tutorial case ที่แนะนำ และปรับแก้ค่าตามการทดลองในบทเรียน

## 🚀 เป้าหมายการเรียนรู้ (Learning Objectives)

> [!NOTE] | **📂 OpenFOAM Context: Key Files & Commands**
> หลังจากผ่าน Module นี้ คุณจะสามารถจัดการไฟล์และยูทิลิตี้ต่อไปนี้ได้อย่างมั่นใจ:
> - **Mesh Structure** → `constant/polyMesh/points`, `faces`, `owner`, `neighbour` (โครงสร้างข้อมูลเมช)
> - **Mesh Generation** → `system/blockMeshDict`, `system/snappyHexMeshDict` (ตั้งค่าการสร้างเมช)
> - **Quality Checks** → `checkMesh -allTopology -allGeometry` (ตรวจสอบคุณภาพเมช)
> - **Post-processing** → `system/controlDict` ภายใน `functions` sub-dictionary (ตั้งค่า Function Objects)
> - **Utilities** → `blockMesh`, `snappyHexMesh`, `topoSet`, `refineMesh` (เครื่องมือจัดการเมช)

*   [ ] เข้าใจโครงสร้างไฟล์ Mesh ของ OpenFOAM (`points`, `faces`, `owner`, `neighbour`)
*   [ ] สามารถสร้าง Structured Mesh ด้วย `blockMesh` ได้อย่างคล่องแคล่ว
*   [ ] สามารถใช้ `snappyHexMesh` สร้าง Mesh สำหรับ Geometry ที่ซับซ้อนได้
*   [ ] เข้าใจเกณฑ์คุณภาพ Mesh (`checkMesh`) และรู้วิธีแก้ไขเมื่อ Mesh พัง
*   [ ] สามารถใช้ Function Objects ในการดึงข้อมูลผลลัพธ์แบบ Real-time ได้

ขอให้สนุกกับการสร้าง Mesh! 🕸️
