# 🗺️ Learning Navigator: Meshing and Case Setup

> [!TIP]
> **ทำไม Meshing ถึงสำคัญ?** Mesh คือพื้นฐานที่สำคัญที่สุดของการจำลอง CFD คุณภาพของเมสมีผลต่อความแม่นยำ (accuracy), เสถียรภาพ (stability), และความเร็วในการคำนวณ (convergence speed) โดยตรง ใน OpenFOAM, เมชถูกเก็บใน `constant/polyMesh/` และถูกสร้างด้วย utilities อย่าง `blockMesh` และ `snappyHexMesh` การเข้าใจโครงสร้างและการสร้างเมสจะช่วยให้คุณสามารถสร้างเคสที่มีประสิทธิภาพและแก้ปัญหาได้อย่างมั่นใจ

> **วัตถุประสงค์**: เอกสารนี้เป็น **เส้นทางการเรียนรู้แบบคู่ขนาน** ที่เชื่อมโยงเนื้อหาทฤษฎี (.md) กับ Source Code และ Utilities จริงใน OpenFOAM

---

## 📋 สารบัญ

1. [Meshing Fundamentals](#1-meshing-fundamentals-พื้นฐานการสร้างเมช)
2. [BlockMesh Mastery](#2-blockmesh-mastery-การใช้-blockmesh)
3. [snappyHexMesh Basics](#3-snappyhexmesh-basics-พื้นฐาน-snappyhexmesh)
4. [snappyHexMesh Advanced](#4-snappyhexmesh-advanced-snappyhexmesh-ขั้นสูง)
5. [Mesh Quality and Manipulation](#5-mesh-quality-and-manipulation-คุณภาพและการจัดการเมช)
6. [Runtime Post-Processing](#6-runtime-post-processing-การประมวลผลระหว่างรัน)

---

## 1. Meshing Fundamentals (พื้นฐานการสร้างเมช)

> [!NOTE]
> **📂 OpenFOAM Context**:
> - **Case Files**: เมชที่สร้างเสร็จจะถูกเก็บใน `constant/polyMesh/` ซึ่งประกอบด้วย `points`, `faces`, `owner`, `neighbour`, `boundary`
> - **Utilities**: `blockMesh` (อ่าน `system/blockMeshDict`), `snappyHexMesh` (อ่าน `system/snappyHexMeshDict`)
> - **Keywords**: `convertToMeters`, `blocks`, `boundary`, `vertices` ใน blockMeshDict

| 📖 เนื้อหา | 📝 คำอธิบาย | 🔧 Source Code ที่เกี่ยวข้อง |
|-----------|------------|---------------------------|
| [[00_Overview]] | ภาพรวมของโมดูล | - |
| [[01_MESHING_FUNDAMENTALS/01_Introduction_to_Meshing]] | แนะนำการสร้างเมช | `utilities/mesh/generation/blockMesh/` |
| [[01_MESHING_FUNDAMENTALS/02_OpenFOAM_Mesh_Structure]] | โครงสร้างเมชใน OpenFOAM | `utilities/mesh/manipulation/` |

---

## 2. BlockMesh Mastery (การใช้ blockMesh)

> [!NOTE]
> **📂 OpenFOAM Context**:
> - **File**: `system/blockMeshDict` - ไฟล์กำหนดค่าสำหรับสร้างเมชแบบ structured
> - **Keywords**: `vertices` (มุม), `blocks` (โซน), `edges` (ความโค้ง), `boundary` (boundary patches), `grading` (ขยายเซลล์), `arc` (curve edges)
> - **Utility**: รันด้วยคำสั่ง `blockMesh` ใน terminal

| 📖 เนื้อหา | 📝 คำอธิบาย | 🔧 Source Code ที่เกี่ยวข้อง |
|-----------|------------|---------------------------|
| [[02_BLOCKMESH_MASTERY/01_BlockMesh_Deep_Dive]] | การใช้ blockMesh แบบลึกซึ้ง | `utilities/mesh/generation/blockMesh/blockMesh.C` |
| [[02_BLOCKMESH_MASTERY/02_Parametric_Meshing]] | การสร้างเมชแบบ Parametric | `utilities/mesh/generation/blockMesh/` |

### 🎯 Study Guide

| ขั้นตอน | กิจกรรม | เวลาโดยประมาณ |
|--------|---------|--------------|
| 1 | อ่าน `01_BlockMesh_Deep_Dive` เข้าใจ syntax | 30 นาที |
| 2 | เปิด tutorial case ศึกษา `blockMeshDict` | 30 นาที |
| 3 | ลองสร้างเมชด้วย blockMesh | 45 นาที |

---

## 3. snappyHexMesh Basics (พื้นฐาน snappyHexMesh)

> [!NOTE]
> **📂 OpenFOAM Context**:
> - **File**: `system/snappyHexMeshDict` - ไฟล์กำหนดค่าสำหรับสร้างเมชแบบ unstructured จาก geometry
> - **Keywords**: `castellatedMesh` (phase 1), `snap` (phase 2), `addLayers` (phase 3), `geometry` (STL/OBJ), `refinementSurfaces`, `refinementRegions`
> - **Utility**: รันด้วย `snappyHexMesh -overwrite` ต้องการ background mesh จาก blockMesh ก่อน

| 📖 เนื้อหา | 📝 คำอธิบาย | 🔧 Source Code ที่เกี่ยวข้อง |
|-----------|------------|---------------------------|
| [[03_SNAPPYHEXMESH_BASICS/01_The_sHM_Workflow]] | ขั้นตอนการทำงานของ sHM | `utilities/mesh/generation/snappyHexMesh/` |
| [[03_SNAPPYHEXMESH_BASICS/02_Geometry_Preparation]] | การเตรียม Geometry | `utilities/surface/` |
| [[03_SNAPPYHEXMESH_BASICS/03_Castellated_Mesh_Settings]] | การตั้งค่า Castellated Mesh | `utilities/mesh/generation/snappyHexMesh/` |

---

## 4. snappyHexMesh Advanced (snappyHexMesh ขั้นสูง)

> [!NOTE]
> **📂 OpenFOAM Context**:
> - **File**: `system/snappyHexMeshDict` (advanced sections)
> - **Keywords**: `addLayersControls` (layer addition), `layers` (specify surface layers), `nSurfaceLayers`, `expansionRatio`, `finalLayerThickness`, `minThickness`, `refinementRegions` (local refinement)
> - **Advanced**: Multi-region meshing, layer quality control, feature edge refinement

| 📖 เนื้อหา | 📝 คำอธิบาย | 🔧 Source Code ที่เกี่ยวข้อง |
|-----------|------------|---------------------------|
| [[04_SNAPPYHEXMESH_ADVANCED/01_Layer_Addition_Strategy]] | กลยุทธ์การเพิ่ม Layer | `utilities/mesh/generation/snappyHexMesh/` |
| [[04_SNAPPYHEXMESH_ADVANCED/02_Refinement_Regions]] | การกำหนดพื้นที่ Refinement | `utilities/mesh/generation/snappyHexMesh/` |
| [[04_SNAPPYHEXMESH_ADVANCED/03_Multi_Region_Meshing]] | การสร้างเมชหลาย Region | `utilities/mesh/generation/snappyHexMesh/` |

---

## 5. Mesh Quality and Manipulation (คุณภาพและการจัดการเมช)

> [!NOTE]
> **📂 OpenFOAM Context**:
> - **Utilities**: `checkMesh` (ตรวจสอบคุณภาพ), `topoSet` (สร้าง sets), `refineMesh` (refine), `createBaffles` (แปลง internal faces)
> - **Keywords**: `maxNonOrthogonality`, `maxSkewness`, `maxAspectRatio` (mesh quality criteria), `cellSet`, `faceSet`, `pointSet` (topoSet actions)
> - **Output**: `checkMesh` แจ้ง warning ถ้า mesh quality ไม่ผ่านเกณฑ์

| 📖 เนื้อหา | 📝 คำอธิบาย | 🔧 Source Code ที่เกี่ยวข้อง |
|-----------|------------|---------------------------|
| [[05_MESH_QUALITY_AND_MANIPULATION/01_Mesh_Quality_Criteria]] | เกณฑ์คุณภาพเมช | `utilities/mesh/manipulation/checkMesh/` |
| [[05_MESH_QUALITY_AND_MANIPULATION/02_Using_TopoSet_and_CellZones]] | การใช้ topoSet และ cellZones | `utilities/mesh/manipulation/topoSet/` |
| [[05_MESH_QUALITY_AND_MANIPULATION/03_Mesh_Manipulation_Tools]] | เครื่องมือจัดการเมช | `utilities/mesh/manipulation/` |

---

## 6. Runtime Post-Processing (การประมวลผลระหว่างรัน)

> [!NOTE]
> **📂 OpenFOAM Context**:
> - **File**: `system/controlDict` - นิยาม function objects ที่นี่
> - **Keywords**: `functions` (block), `type` (เช่น `forces`, `probes`, `sets`, `surfaces`), `writeControl`, `writeInterval`, `timeStart`, `timeEnd`
> - **Examples**: `forces` (คำนวณ lift/drag), `probes` (sample ที่จุด), `surfaceIso` (iso-surfaces), `fieldMinMax` (min/max values)

| 📖 เนื้อหา | 📝 คำอธิบาย | 🔧 Source Code ที่เกี่ยวข้อง |
|-----------|------------|---------------------------|
| [[06_RUNTIME_POST_PROCESSING/01_Introduction_to_FunctionObjects]] | แนะนำ Function Objects | `utilities/postProcessing/` |
| [[06_RUNTIME_POST_PROCESSING/02_Forces_and_Coefficients]] | การคำนวณแรงและสัมประสิทธิ์ | `utilities/postProcessing/forces/` |
| [[06_RUNTIME_POST_PROCESSING/03_Sampling_and_Probes]] | การ Sampling และ Probes | `utilities/postProcessing/sampling/` |

---

## 📁 OpenFOAM Mesh Utilities Structure

```
applications/utilities/
├── mesh/
│   ├── generation/
│   │   ├── blockMesh/         ← 🌟 สร้างเมช structured
│   │   ├── snappyHexMesh/     ← 🌟 สร้างเมช unstructured
│   │   └── foamyMesh/         ← Alternative mesher
│   │
│   ├── manipulation/
│   │   ├── checkMesh/         ← ตรวจสอบคุณภาพเมช
│   │   ├── topoSet/           ← สร้าง cell/face zones
│   │   └── refineMesh/        ← Refine เมช
│   │
│   └── conversion/            ← แปลงรูปแบบเมช
│
├── postProcessing/
│   ├── forces/                ← คำนวณแรง
│   └── sampling/              ← Sampling probes
│
└── surface/                   ← จัดการ geometry surfaces
```

---

## 🎓 Learning Path

```mermaid
graph TD
    classDef content fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef code fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef milestone fill:#fff9c4,stroke:#f9a825,stroke-width:2px

    A[01_MESHING_FUNDAMENTALS]:::content --> B[blockMesh utility]:::code
    B --> C[02_BLOCKMESH_MASTERY]:::content
    C --> D[03_SNAPPYHEXMESH_BASICS]:::content
    D --> E[snappyHexMesh utility]:::code
    E --> F[04_SNAPPYHEXMESH_ADVANCED]:::content
    F --> G[05_MESH_QUALITY]:::content
    G --> H[checkMesh utility]:::code
    H --> I[06_RUNTIME_POST_PROCESSING]:::content
    I --> J[postProcess utilities]:::code
    J --> K[🎯 Create Production-Quality Mesh!]:::milestone
```

---

## 🆕 What's New (2025-12-26 Update)

### Enhanced Content Features

บทเรียนทุกไฟล์ใน MODULE_02 ได้รับการปรับปรุงเพื่อการเรียนรู้ที่ดีขึ้น:

1. **🎨 Mermaid Workflow Diagrams**
   - เพิ่ม Diagram ประกอบการอธิบายแต่ละหัวข้อ
   - ช่วยให้เข้าใจ Flow และความสัมพันธ์ระหว่าง Process ต่างๆ
   - Visualize แนวคิดที่ซับซ้อน (เช่น sHM workflow, topoSet operations, Function objects)

2. **🔗 Cross-Reference Links**
   - เพิ่มลิงก์เชื่อมโยงระหว่างบทเรียนที่เกี่ยวข้อง
   - ช่วยให้สามารถอ้างอิงและเปรียบเทียบแนวคิดได้ง่ายขึ้น

3. **📝 Hands-on Exercises**
   - เพิ่มแบบฝึกหัด 3 ระดับความยาก (Easy, Medium, Hard) ทุกไฟล์
   - **Easy**: True/False และ Multiple Choice ทบทวนแนวคิด
   - **Medium**: อธิบายและเขียนคำสั่ง ประยุกต์ใช้ความรู้
   - **Hard**: Hands-on และวิเคราะห์ ฝึกทักษะขั้นสูง
   - คำตอบทั้งหมดอยู่ใน `<details>` tags สามารถเปิดดูได้

### Statistics

- **Total Files Enhanced**: 17 content files
- **Sections**: 6 main sections
- **Mermaid Diagrams**: 17 workflow diagrams
- **Exercises**: 102 questions (34 Easy, 34 Medium, 34 Hard)

---

*Last Updated: 2025-12-26*
