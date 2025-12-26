# Module 02: Meshing and Case Setup (การสร้างการแบ่งส่วนและตั้งค่าเคส)

ความสำเร็จของการจำลอง CFD (Computational Fluid Dynamics) ไม่ได้ขึ้นอยู่กับแค่การเลือก Solver ที่ถูกต้อง แต่เริ่มต้นที่ **คุณภาพของ Mesh (Grid)** และ **การตั้งค่าเคส (Case Setup)** ที่เหมาะสม โมดูลนี้ถูกออกแบบมาเพื่อเติมเต็มช่องว่างระหว่างทฤษฎีพื้นฐานกับการทำงานจริง โดยเน้นเครื่องมือที่ทรงพลังที่สุดของ OpenFOAM คือ `snappyHexMesh` และระบบ `functionObjects`

## 🎯 วัตถุประสงค์การเรียนรู้ (Learning Objectives)

เมื่อเรียนจบโมดูลนี้ ผู้เรียนจะสามารถ:
1.  **เข้าใจกลยุทธ์การสร้าง Mesh**: รู้ว่าเมื่อไหร่ควรใช้ Structured Mesh (`blockMesh`) และเมื่อไหร่ควรใช้ Unstructured/Hybrid Mesh (`snappyHexMesh`)
2.  **เชี่ยวชาญ snappyHexMesh**: ตั้งแต่ขั้นตอน Castellated, Snap, ไปจนถึง Layer Addition เพื่อจับ Boundary Layer
3.  **ตรวจสอบและปรับปรุงคุณภาพ Mesh**: ใช้ `checkMesh` วิเคราะห์ปัญหาและความเข้าใจในค่า Non-orthogonality, Skewness, และ Aspect Ratio
4.  **จัดการ Mesh ขั้นสูง**: การใช้ `topoSet`, `cellSet`, `createPatch` เพื่อจัดการโซนต่างๆ โดยไม่ต้องสร้างใหม่
5.  **ตั้งค่า Runtime Post-processing**: ดึงข้อมูล Forces, Probes, และค่าเฉลี่ย (Averaging) ระหว่างคำนวณโดยไม่ต้องรอให้เสร็จ

## 📚 โครงสร้างเนื้อหา (Module Structure)

### 01_MESHING_FUNDAMENTALS (พื้นฐานการแบ่งส่วน)
*   **01_Introduction_to_Meshing.md**: Mesh คืออะไร? ทำไมคุณภาพถึงสำคัญ? ประเภทของ Cell (Hex, Tet, Poly)
*   **02_OpenFOAM_Mesh_Structure.md**: โครงสร้างไฟล์ `constant/polyMesh` (points, faces, owner, neighbour) คืออะไร?

### 02_BLOCKMESH_MASTERY (การใช้งาน blockMesh ขั้นสูง)
*   **01_BlockMesh_Deep_Dive.md**: เทคนิคการสร้าง Multi-block, Grading, และ Curved edges
*   **02_Parametric_Meshing.md**: การใช้ M4 macro หรือ tools อื่นๆ เพื่อทำ Parametric geometry

### 03_SNAPPYHEXMESH_BASICS (พื้นฐาน snappyHexMesh)
*   **01_The_sHM_Workflow.md**: เข้าใจกระบวนการ 3 ขั้นตอน: Castelated -> Snap -> Layers
*   **02_Geometry_Preparation.md**: การเตรียมไฟล์ STL/OBJ ให้สะอาดและพร้อมใช้งาน (Watertight geometry)
*   **03_Castellated_Mesh_Settings.md**: การกำหนด Refinement levels และ Features

### 04_SNAPPYHEXMESH_ADVANCED (การใช้งาน snappyHexMesh ขั้นสูง)
*   **01_Layer_Addition_Strategy.md**: เทคนิคการสร้าง Prism layers สำหรับ Turbulence modeling ($y+$)
*   **02_Refinement_Regions.md**: การใช้ Shapes (Box, Sphere) และ Mode (Inside, Distance) เพื่อปรับความละเอียดเฉพาะจุด
*   **03_Multi_Region_Meshing.md**: การสร้าง Mesh สำหรับ CHT (Conjugate Heat Transfer) หรือ Porous media

### 05_MESH_QUALITY_AND_MANIPULATION (คุณภาพและการจัดการ Mesh)
*   **01_Mesh_Quality_Criteria.md**: Non-orthogonality, Skewness คืออะไรและส่งผลต่อ Divergence อย่างไร?
*   **02_Using_TopoSet_and_CellZones.md**: การสร้าง Zones เพื่อใช้กำหนด Porosity หรือ MRF (Multiple Reference Frame)
*   **03_Mesh_Manipulation_Tools.md**: `transformPoints` (Scale/Rotate), `mergeMeshes`, `stitchMesh`

### 06_RUNTIME_POST_PROCESSING (การประมวลผลระหว่างรัน)
*   **01_Introduction_to_FunctionObjects.md**: หัวใจของการดึงข้อมูลโดยไม่ต้องเขียนโค้ด
*   **02_Forces_and_Coefficients.md**: การคำนวณ $C_l, C_d$ แบบ Real-time
*   **03_Sampling_and_Probes.md**: การดึงกราฟเส้น (Line plotting) และจุดตรวจสอบ (Monitoring points)

---

> [!NOTE]
> โมดูลนี้เป็น **"สะพานเชื่อม (Bridge)"** ที่สำคัญที่สุดก่อนที่คุณจะก้าวไปสู่การจำลองแบบ Multi-phase หรือ Advanced Physics เพราะถ้า Mesh ไม่ดี solver ที่ดีที่สุดก็ไม่สามารถให้คำตอบที่ถูกต้องได้

เริ่มกันที่ [01_MESHING_FUNDAMENTALS/01_Introduction_to_Meshing.md](./01_MESHING_FUNDAMENTALS/01_Introduction_to_Meshing.md)
