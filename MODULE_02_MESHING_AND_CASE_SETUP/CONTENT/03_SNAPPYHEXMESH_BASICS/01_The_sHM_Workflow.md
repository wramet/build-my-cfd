# กระบวนการทำงานของ snappyHexMesh (The snappyHexMesh Workflow)

> [!TIP] **ทำไมต้องเข้าใจ snappyHexMesh?**
> `snappyHexMesh` เป็นเครื่องมือสร้าง Mesh อัตโนมัติที่ทรงพลังที่สุดใน OpenFOAM การเข้าใจ Workflow 3 ขั้นตอนนี้จะช่วยให้คุณ:
> - **ประหยัดเวลา** ในการสร้าง Mesh สำหรับเรขาคณิตที่ซับซ้อน (Complex Geometry)
> - **ควบคุมคุณภาพ Mesh** ได้อย่างแม่นยำ โดยเลือกความละเอียดตาะตำแหน่งที่ต้องการ
> - **สร้าง Boundary Layer** ที่เหมาะสมกับแบบจำลองความปั่น (Turbulence Models) ซึ่งสำคัญมากต่อความแม่นยำของการคำนวณ
> - **ลดข้อผิดพลาด** จากการตั้งค่าผิดพลาดที่ทำให้ Mesh พัง (Mesh Collapse) หรือ Quality ต่ำเกินไป
>
> ไฟล์ควบคุมหลัก: `system/snappyHexMeshDict` | เรียกใช้ด้วยคำสั่ง: `snappyHexMesh`

## Learning Objectives

หลังจากอ่านบทนี้ คุณจะสามารถ:

- **อธิบาย** แนวคิด 3-Phase Workflow ของ snappyHexMesh ได้อย่างเป็นระบบ
- **เปรียบเทียบ** กระบวนการทำงานของ snappyHexMesh กับประติมากรรมเลโก้ได้อย่างถูกต้อง
- **ระบุ** บทบาทของแต่ละ Phase (Castellated, Snap, Layers) ในการสร้าง Mesh คุณภาพสูง
- **เข้าใจ** โครงสร้างไฟล์ `system/snappyHexMeshDict` และการเลือกเปิด/ปิดแต่ละ Phase สำหรับการ Debug
- **ประยุกต์** การรัน snappyHexMesh แบบ Parallel สำหรับงานขนาดใหญ่
- **ตรวจสอบ** ผลลัพธ์ของแต่ละ Phase ด้วย ParaView และ checkMesh

---

## 1. snappyHexMesh คืออะไร? (What is snappyHexMesh?)

`snappyHexMesh` (sHM) คือเครื่องมือสร้าง Grid แบบอัตโนมัติ (Automated Meshing Tool) ที่ทรงพลังที่สุดของ OpenFOAM โดยใช้วิธีการ **Cut-Cell Method** บนพื้นฐานของ Cartesian Grid เพื่อสร้าง Mesh ที่มีคุณภาพสูง (Hex-dominant) สำหรับเรขาคณิตที่ซับซ้อน

> [!NOTE] **📂 OpenFOAM Context: ไฟล์และคำสั่งที่เกี่ยวข้อง**
> การรัน `snappyHexMesh` จำเป็นต้องใช้ไฟล์และคำสั่งต่อไปนี้:
>
> **ไฟล์ที่ต้องมี:**
> - `system/blockMeshDict` → สร้าง Background Mesh
> - `system/snappyHexMeshDict` → ควบคุมการสร้าง Mesh ทั้ง 3 Phase
> - `system/surfaceFeatureExtractDict` → สกัด Feature Edges (สำคัญมากสำหรับ Snapping)
> - `constant/triSurface/<geometry>.stl` → ไฟล์ Geometry (STL/OBJ)
> - `system/decomposeParDict` → สำหรับการรันแบบ Parallel
>
> **คำสั่งที่ใช้:**
> - `blockMesh` → สร้าง Background Mesh
> - `surfaceFeatureExtract` → สกัด Feature Edges
> - `decomposePar` → แยก Domain
> - `mpirun -np N snappyHexMesh -parallel` → รัน Parallel
> - `checkMesh` → ตรวจสอบคุณภาพ Mesh
> - `reconstructParMesh` → รวมผลลัพธ์กลับ

**ทำไมต้องใช้ snappyHexMesh? (Why Use snappyHexMesh?)**

1. **ความยืดหยุ่น**: สามารถสร้าง Mesh สำหรับ Geometry ที่ซับซ้อนได้โดยไม่ต้องสร้าง Block Topology ด้วยมือ
2. **คุณภาพสูง**: ผลลัพธ์เป็น Hex-dominant Mesh ซึ่งมีความแม่นยำสูงกว่า Tetrahedral Mesh สำหรับการแก้สมการ CFD
3. **อัตโนมัติ**: ลดเวลาในการสร้าง Mesh จากหลายวัน/สัปดาห์ เหลือเพียงไม่กี่ชั่วโมง
4. **ควบคุมได้**: สามารถกำหนดความละเอียดแบบ Local Refinement ได้ตามต้องการ

---

## 2. แนวคิดเปรียบเทียบ (Analogy): ประติมากรรมเลโก้

จงจินตนาการว่าคุณต้องการสร้างรูปปั้น "รถยนต์" จากตัวต่อ LEGO:

1. **Background Mesh (blockMesh)**: คุณก่อกองภูเขา LEGO สี่เหลี่ยมก้อนใหญ่ๆ ครอบคลุมพื้นที่ที่จะมีรถอยู่
2. **Castellated Mesh**: คุณเอาเลื่อยมาตัดบล็อก LEGO ส่วนที่ไม่ได้เป็นรูปรถออกไป จนเหลือรูปร่างรถแบบ "ขั้นบันได" (หยักๆ แบบ Pixel)
3. **Snapping**: คุณใช้ความร้อนละลายผิว LEGO ด้านนอกที่หยักๆ ให้ละลายแนบสนิทไปกับผิวรถจริงๆ จนเรียบเนียน
4. **Layer Addition**: คุณทาสีพ่นเคลือบผิวรถหลายๆ ชั้น เพื่อเก็บรายละเอียดที่ผิว

นี่คือกระบวนการเป๊ะๆ ของ `snappyHexMesh`

<!-- IMAGE: IMG_02_004 -->
<!-- 
Purpose: เพื่อแสดงกระบวนการทำงาน 3 ขั้นตอนของ snappyHexMesh ให้เห็นภาพชัดเจนเหมือน "ประติมากรรม" เริ่มจาก 1. แกะสลักหยาบ (Castellated) 2. ขัดผิวให้เรียบ (Snap) 3. เคลือบผิวละเอียด (Layers). ภาพนี้ต้องช่วยให้ผู้เรียนจำลำดับการทำงานและผลลัพธ์ของแต่ละขั้นได้
Prompt: "Sequential 3-Panel Triptych Diagram of snappyHexMesh Process. **Panel 1 (Left - Castellated):** A blocky LEGO-like mesh approximating an airfoil shape. Step-like jagged edges. Label: '1. Castellated'. **Panel 2 (Center - Snap):** The same mesh but vertices are moved to smooth out the jagged edges, fitting the curve perfectly. Label: '2. Snap'. **Panel 3 (Right - Layers):** Zoom in on the surface relative to Panel 2, showing 3 distinct thin prism layers added boundary-aligned. Label: '3. Layers'. **Style:** Technical diagram, flat 2D or simple 3D wireframe, white background, distinct stages side-by-side."
-->
![[IMG_02_004.jpg]]

**ทำไมต้องใช้ 3 Phase? (Why Three Phases?)**

แต่ละ Phase มีวัตถุประสงค์ที่แตกต่างกัน:

- **Phase 1 (Castellated)**: สร้างโครงร่างหยาบแต่รวดเร็ว เพื่อกำหนดความละเอียดโดยรวม
- **Phase 2 (Snapping)**: ปรับปรุงคุณภาพผิวให้เรียบ ซึ่งสำคัญต่อความแม่นยำของการคำนวณ
- **Phase 3 (Layers)**: เพิ่ม Boundary Layer ซึ่งจำเป็นสำหรับ Turbulence Modeling

---

## 3. ภาพรวม 3-Phase Workflow (How Does It Work?)

> [!NOTE] **📂 OpenFOAM Context: การเลือก Phase ในการรัน**
> ใน `system/snappyHexMeshDict` คุณสามารถเลือกรันแต่ละ Phase แยกกันได้ โดยการตั้งค่า:
>
> ```cpp
> castellatedMesh true;  // Phase 1: Refinement + Removal
> snap            true;  // Phase 2: Surface Snapping
> addLayers       true;  // Phase 3: Boundary Layer
> ```
>
> **เทคนิคการ Debug:** แนะนำให้รันทีละ Phase เพื่อตรวจสอบผลลัพธ์ ก่อนจะรันทั้งหมดในครั้งเดียว
>
> **การตรวจสอบ:**
> - ใช้ `checkMesh -latestTime` เพื่อตรวจสอบคุณภาพ Mesh หลังจากแต่ละ Phase
> - เปิดดูใน ParaView ที่ Time directories: 0/, 1/, 2/, 3/

**snappyHexMesh 3-Phase Workflow:**
```mermaid
graph TB
    Start[1. blockMesh<br/>Background Box] --> Phase1[Phase 1: Castellated<br/>Refine & Remove]
    Phase1 --> Phase2[Phase 2: Snapping<br/>Points to Surface]
    Phase2 --> Phase3[Phase 3: Layer Addition<br/>Boundary Layers]
    Phase3 --> Check[checkMesh<br/>Quality Check]
    Check --> Done{Pass?}
    Done -->|Yes| Success[Ready to Solve]
    Done -->|No| Adjust[Adjust Parameters<br/>& Retry]

    style Start fill:#e3f2fd
    style Phase1 fill:#fff3e0
    style Phase2 fill:#ffe0b2
    style Phase3 fill:#ffcc80
    style Check fill:#c8e6c9
    style Success fill:#4CAF50
    style Adjust fill:#ff5252
```

### Phase 1: Castellated Mesh (การขึ้นรูปหยาบ)

> [!NOTE] **📂 OpenFOAM Context: การตั้งค่า Castellated Mesh**
> Phase 1 นี้ถูกควบคุมโดย `castellatedMeshControls` ใน `system/snappyHexMeshDict`:
>
> **Keywords สำคัญ:**
> - `locationInMesh` → พิกัด (x y z) ที่ระบุตำแหน่ง Fluid Domain
> - `refinementSurfaces` → กำหนด Level ของความละเอียดบนผิวแต่ละส่วน
> - `refinementRegions` → กำหนด Refinement Box/Sphere สำหรับเพิ่มความละเอียดเฉพาะจุด
> - `maxGlobalCells` → จำกัดจำนวน Cell สูงสุดทั้งหมด (ป้องกัน Memory Overflow)
> - `nCellsBetweenLevels` → ควบคุมการลดขนาด Cell ระหว่างระดับความละเอียด (ปกติ = 1-3)
>
> **ผลลัพธ์:** Mesh จะถูกเก็บใน Time directory `1/` สามารถเปิดดูใน ParaView ได้

**ทำไม (Why):** เพื่อสร้างโครงร่างหยาบของ Geometry ด้วยการ Refine และลบ Cell ที่อยู่ภายนอก

**อย่างไร (How):**
1. **Refinement:** โปรแกรมจะวนลูปตรวจสอบว่า Cell ไหนตัดผ่าน Geometry หรืออยู่ใน Refinement Region ถ้าใช่ จะทำการแตก Cell แม่ (Parent) เป็น 8 Cell ลูก (Children)
2. **Level Control:** ความละเอียดจะถูกกำหนดเป็น "Level" (ระดับ 0 = พื้นฐาน, ระดับ 1 = แตก 1 ครั้ง, ระดับ 2 = แตก 2 ครั้ง...)
3. **Removal:** เมื่อ Refine จนพอใจ โปรแกรมจะลบ Cell ที่อยู่ผิดฝั่งทิ้ง (กำหนดโดย `locationInMesh`)

> [!WARNING] **จุดตาย:**
> `locationInMesh` ต้องเป็นพิกัด (x y z) ที่ **ไม่อยู่** บนผิวและ **ไม่อยู่** บนขอบของ Cell (ควรเลี่ยงจุดอย่าง 0, 0.5, 1 ให้ใช้ 0.00134 แทน)

### Phase 2: Snapping (การดึงผิวให้เรียบ)

> [!NOTE] **📂 OpenFOAM Context: การตั้งค่า Snapping Phase**
> Phase 2 นี้ถูกควบคุมโดย `snapControls` ใน `system/snappyHexMeshDict`:
>
> **Keywords สำคัญ:**
> - `nSmoothPatch` → จำนวนครั้งที่ Smooth ผิว (ปกติ = 3-5)
> - `tolerance` → ค่าความคลาดเคลื่อนที่ยอมรับได้ (ปกติ = 1.0-4.0)
> - `nSolveIter` → จำนวนรอบการแก้ปัญหา (Solver Iterations)
> - `nRelaxIter` → จำนวนรอบการผ่อนคลาย (Relaxation Iterations)
> - `nFeatureSnapIter` → จำนวนรอบการดึงผิวตาม Feature Edges
>
> **ความสำคัญ:** Snapping จะสำเร็จได้ต้องอาศัย Castellated Mesh ที่ละเอียดพอ (Level สูงพอ) มิฉะนั้นจะไม่สามารถดึงผิวให้เรียบได้
>
> **ผลลัพธ์:** Mesh จะถูกเก็บใน Time directory `2/`

**ทำไม (Why):** เพื่อแก้ไขผิว "ขั้นบันได" ให้เป็น "ผิวเรียบ" ซึ่งสำคัญต่อความแม่นยำของการคำนวณ

**อย่างไร (How):**
1. **Point Displacement:** จุดยอด (Vertices) ของเซลล์ที่อยู่ติดผิวจะถูก "ดีด" เข้าไปหาพื้นผิวของ STL
2. **Smoothing:** เมื่อจุดขยับ Cell อาจเบี้ยว (Skewness) โปรแกรมจะทำการ Smooth (เกลี่ย) จุดภายในเพื่อกระจายความเครียด
3. **Iterative Morphing:** ทำซ้ำหลายรอบจนกว่า Error จะต่ำกว่าเกณฑ์

### Phase 3: Layer Addition (การเพิ่มชั้นผิว)

> [!NOTE] **📂 OpenFOAM Context: การตั้งค่า Layer Addition**
> Phase 3 นี้ถูกควบคุมโดย `addLayersControls` ใน `system/snappyHexMeshDict`:
>
> **Keywords สำคัญ:**
> - `layers` → ระบุ Patch ไหนที่ต้องการ Layer และจำนวน Layer
> - `expansionRatio` → อัตราส่วนการขยายตัวของ Layer (ปกติ = 1.0-1.5)
> - `finalLayerThickness` → ความหนาของ Layer ชั้นนอกสุด
> - `minThickness` → ความหนาขั้นต่ำที่ยอมรับได้
> - `nGrow` → จำนวนรอบการขยาย Layer (Layer Growing)
> - `maxFaceThicknessRatio` → อัตราส่วนความหนาสูงสุดระหว่าง Faces ต่างๆ
> - `nSmoothSurfaceNormals` → จำนวนรอบการ Smooth Normal Vector
>
> **เทคนิค:** Layer Addition เป็น Phase ที่ล้มเหลวง่ายที่สุด แนะนำให้เริ่มจาก `expansionRatio = 1.0` แล้วค่อยๆ เพิ่ม ถ้า Layer ไม่ขึ้น
>
> **ผลลัพธ์:** Mesh สุดท้ายจะถูกเก็บใน Time directory `3/` ซึ่งเป็น Mesh ที่พร้อมใช้งาน

**ทำไม (Why):** เพื่อสร้าง Boundary Layer ที่จำเป็นสำหรับ Turbulence Modeling และการคำนวณ Gradient บนผิว

**อย่างไร (How):**
1. **Push Back:** Mesh ที่สร้างเสร็จแล้วจะถูกดันถอยหลังออกมาในแนว Normal
2. **Insertion:** สร้าง Cell ใหม่แทรกเข้าไปในช่องว่างนั้น
3. **Quality Check:** ถ้าแทรกแล้ว Mesh Quality แย่ โปรแกรมจะยกเลิกการสร้าง Layer ตรงนั้น (Layer Collapse)

---

## 4. โครงสร้างไฟล์ `system/snappyHexMeshDict`

> [!NOTE] **📂 OpenFOAM Context: โครงสร้าง snappyHexMeshDict**
> ไฟล์ `system/snappyHexMeshDict` เป็น Dictionary File ที่ควบคุมทั้ง 3 Phase ของการสร้าง Mesh โดยแต่ละส่วนประกอบด้วย:
>
> **Keywords หลัก:**
> - `castellatedMesh`, `snap`, `addLayers` → เปิด/ปิดการทำงานแต่ละ Phase
> - `geometry` → กำหนด Surface (STL/OBJ) และ Refinement Regions
> - `castellatedMeshControls` → ควบคุม Refinement Levels, LocationInMesh, และการลบ Cell
> - `snapControls` → ควบคุมความเรียบของผิว (nSmoothPatch, tolerance)
> - `addLayersControls` → ควบคุม Layer Thickness, Expansion Ratio, และ Layer Settings
>
> การเข้าใจโครงสร้างนี้จำเป็นต่อการ Debug เมื่อ Mesh ไม่สำเร็จ

ไฟล์ควบคุมหลักจะแบ่งออกเป็น 3 ส่วนใหญ่ๆ ตามกระบวนการทำงาน:

```cpp
castellatedMesh true; // เปิด/ปิด Phase 1
snap            true; // เปิด/ปิด Phase 2
addLayers       true; // เปิด/ปิด Phase 3

geometry
{
    car.stl { type triSurfaceMesh; name car; }
    refinementBox { type box; min (0 0 0); max (1 1 1); }
};

castellatedMeshControls { ... } // ควบคุมความละเอียด
snapControls { ... }            // ควบคุมการเข้าผิว
addLayersControls { ... }       // ควบคุมชั้น Boundary Layer
```

**การตั้งค่าเพื่อ Debug:**

สำหรับการ Debug คุณสามารถเลือกรันแต่ละ Phase แยกกันได้:

```cpp
// รันเฉพาะ Phase 1
castellatedMesh true;
snap            false;
addLayers       false;

// รันเฉพาะ Phase 1 + 2
castellatedMesh true;
snap            true;
addLayers       false;
```

---

## 5. Workflow การรันคำสั่ง (Execution Guide)

การรัน `snappyHexMesh` สำหรับงานจริง (Mesh > 500k cells) ควรใช้โหมด Parallel:

```bash
# 1. สร้าง Background Mesh (ต้องครอบคลุม Geometry ทั้งหมด)
blockMesh

# 2. สกัด Feature Edges (สำคัญมากเพื่อให้มุมคมชัด!)
# อ่านไฟล์ surfaceFeatureExtractDict
surfaceFeatureExtract

# 3. แยกโดเมนเพื่อคำนวณแบบขนาน
decomposePar

# 4. รัน sHM (แบบทับโฟลเดอร์เดิม -overwrite)
# ใช้ mpirun -np <จำนวน Core>
mpirun -np 4 snappyHexMesh -overwrite -parallel > log.shm

# 5. ตรวจสอบคุณภาพ
checkMesh -latestTime

# 6. รวมผลลัพธ์กลับ (ถ้าต้องการดูผลเต็มๆ)
reconstructParMesh -constant
```

> [!TIP] **เทคนิคการ Debug:**
> หากต้องการตรวจสอบผลลัพธ์ทีละ Phase ให้ลบ `-overwrite` flag:
> ```bash
> snappyHexMesh -parallel > log.shm
> ```
> จะได้ Time directories: 0/, 1/, 2/, 3/ ซึ่งสามารถเปิดดูใน ParaView ได้

---

## 6. การ Debug ด้วย ParaView

> [!NOTE] **📂 OpenFOAM Context: การตรวจสอบ Mesh ด้วย ParaView**
> `snappyHexMesh` สามารถเขียนผลลัพธ์ออกมาทีละขั้นตอน โดยไม่ใช้ `-overwrite` flag:
>
> **Time Directories:**
> - `0/` → Background Mesh จาก `blockMesh` (ตรวจสอบว่าครอบคลุม Geometry)
> - `1/` → Castellated Mesh (ตรวจสอบ Refinement Level และการลบ Cell)
> - `2/` → Snapped Mesh (ตรวจสอบความเรียบของผิว)
> - `3/` → Final Mesh with Layers (ตรวจสอบ Layer Quality)
>
> **เทคนิคการ Visualize:**
> 1. เปิด ParaView → File → Open → เลือก `case.foam`
> 2. ใช้ `Mesh Regions` เพื่อดูเฉพาะส่วนที่ต้องการ
> 3. ใช้ `Extract Surface` เพื่อดูผิว Mesh ชัดขึ้น
> 4. ใช้ `Cell Size` Coloring เพื่อดูความละเอียดของ Mesh
>
> **ตัวช่วยการ Debug:**
> - ใช้ `checkMesh -latestTime -allGeometry -allTopology` เพื่อดูรายงานคุณภาพ Mesh แบบละเอียด
> - ตรวจสอบ Log file (`log.shm`) สำหรับ Layer collapse warnings

`snappyHexMesh` สามารถเขียนผลลัพธ์ออกมาทีละขั้นตอนได้ ถ้าคุณไม่ใส่ `-overwrite` มันจะสร้าง Time folder:

- `0/`: Background Mesh
- `1/`: Castellated Mesh (ดูว่าละเอียดพอไหม)
- `2/`: Snapped Mesh (ดูว่าผิวเรียบไหม)
- `3/`: Layer Mesh (ดูว่า Layer ขึ้นครบไหม)

> [!TIP]
> ให้เช็คทีละ Step เสมอ! อย่าพยายามแก้ Layer (Step 3) ถ้า Castellated (Step 1) ยังหยาบเกินไป เพราะ Snap จะไม่มีทางสวยถ้า Cell ต้นทางไม่ละเอียดพอ

---

## 📌 Key Takeaways

1. **3-Phase Workflow**: snappyHexMesh ทำงานใน 3 ขั้นตอน: Castellated (แกะสลักหยาบ) → Snapping (เรียบผิว) → Layer Addition (เคลือบชั้นผิว)

2. **Analogy**: คิดง่ายๆ เหมือน "ประติมากรรมเลโก้" - ตัดบล็อก → เรียบผิว → เคลือบสี

3. **Sequential Dependency**: แต่ละ Phase พึ่งพา Phase ก่อนหน้า Castellated ต้องละเอียดพอ Snapping จึงจะสวย และต้อง Snap สวย Layer จึงจะขึ้น

4. **Debug Strategy**: รันทีละ Phase โดยปรับ `castellatedMesh`, `snap`, `addLayers` และตรวจสอบด้วย ParaView ที่ Time directories 0/, 1/, 2/, 3/

5. **Critical Parameters**:
   - `locationInMesh` (Phase 1) → กำหนด Fluid Domain ผิด = Mesh หาย
   - `tolerance` (Phase 2) → ควบคุมความเรียบผิว
   - `expansionRatio` (Phase 3) → ควบคุม Layer Thickness

6. **Parallel Execution**: งานจริง (Mesh > 500k cells) ต้องรัน Parallel ด้วย `decomposePar` + `mpirun` เพื่อประหยัดเวลา

7. **Quality Check**: ใช้ `checkMesh -latestTime` และ ParaView เพื่อตรวจสอบ Mesh Quality หลังจากแต่ละ Phase

---

## 🧠 Concept Check: ทดสอบความเข้าใจ

### แบบฝึกหัดระดับง่าย (Easy)
1. **True/False**: `snappyHexMesh` สามารถรันได้โดยไม่ต้องสร้าง Background Mesh ด้วย `blockMesh` ก่อน
   <details>
   <summary>คำตอบ</summary>
   ❌ เท็จ - ต้องมี Background Mesh จาก `blockMesh` ก่อนเสมอ
   </details>

2. **เลือกตอบ**: Phase ไหนที่ตัด Geometry ออกตามรูปร่างจริง?
   - a) Phase 1: Castellated
   - b) Phase 2: Snapping
   - c) Phase 3: Layer Addition
   - d) ทุก Phase
   <details>
   <summary>คำตอบ</summary>
   ✅ a) Phase 1: Castellated - เป็นขั้นตอนที่ลบ Cell ที่อยู่ภายนอก Geometry
   </details>

### แบบฝึกหัดระดับปานกลาง (Medium)
3. **อธิบาย**: ทำไม `locationInMesh` ถึงเป็นจุดสำคัญมาก?
   <details>
   <summary>คำตอบ</summary>
   เพราะ sHM ใช้จุดนี้เพื่อตัดสินใจว่า Cell ไหนคือ Fluid (คงไว้) และ Cell ไหนคือ Solid (ลบทิ้ง) ถ้าระบุผิด Mesh จะหายหมด
   </details>

4. **สังเกต**: เมื่อรัน `snappyHexMesh` โดยไม่ใส่ `-overwrite` จะมีโฟลเดอร์ Time กี่โฟลเดอร์?
   <details>
   <summary>คำตอบ</summary>
   4 โฟลเดอร์: 0/ (Background), 1/ (Castellated), 2/ (Snapped), 3/ (Layer)
   </details>

### แบบฝึกหัดระดับสูง (Hard)
5. **Hands-on**: รัน `snappyHexMesh` จาก Tutorial ใดๆ แล้วเปิดดู Time folders ทั้ง 4 ใน ParaView เพื่อดูการเปลี่ยนแปลงของ Mesh ทีละ Phase

6. **วิเคราะห์**: เปรียบเทียบข้อดี-ข้อเสียระหว่างการรัน `snappyHexMesh` แบบ Serial กับ Parallel (ใช้ `decomposePar` + `mpirun`)

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ดูวิธีเตรียม Geometry ที่สะอาด**: [02_Geometry_Preparation.md](./02_Geometry_Preparation.md)
- **ดูการตั้งค่า Castellated Mesh**: [03_Castellated_Mesh_Settings.md](./03_Castellated_Mesh_Settings.md)
- **ดูเทคนิค Layer Addition**: [../04_SNAPPYHEXMESH_ADVANCED/01_Layer_Addition_Strategy.md](../04_SNAPPYHEXMESH_ADVANCED/01_Layer_Addition_Strategy.md)
- **บทก่อนหน้า**: [../02_BLOCKMESH_MASTERY/02_Parametric_Meshing.md](../02_BLOCKMESH_MASTERY/02_Parametric_Meshing.md)