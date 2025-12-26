# กระบวนการทำงานของ snappyHexMesh (The snappyHexMesh Workflow)

`snappyHexMesh` (sHM) คือเครื่องมือสร้าง Grid แบบอัตโนมัติ (Automated Meshing Tool) ที่ทรงพลังที่สุดของ OpenFOAM โดยใช้วิธีการ **Cut-Cell Method** บนพื้นฐานของ Cartesian Grid เพื่อสร้าง Mesh ที่มีคุณภาพสูง (Hex-dominant) สำหรับเรขาคณิตที่ซับซ้อน

## 1. แนวคิดเปรียบเทียบ (Analogy): ประติมากรรมเลโก้

จงจินตนาการว่าคุณต้องการสร้างรูปปั้น "รถยนต์" จากตัวต่อ LEGO:

1.  **Background Mesh (blockMesh)**: คุณก่อกองภูเขา LEGO สี่เหลี่ยมก้อนใหญ่ๆ ครอบคลุมพื้นที่ที่จะมีรถอยู่
2.  **Castellated Mesh**: คุณเอาเลื่อยมาตัดบล็อก LEGO ส่วนที่ไม่ได้เป็นรูปรถออกไป จนเหลือรูปร่างรถแบบ "ขั้นบันได" (หยักๆ แบบ Pixel)
3.  **Snapping**: คุณใช้ความร้อนละลายผิว LEGO ด้านนอกที่หยักๆ ให้ละลายแนบสนิทไปกับผิวรถจริงๆ จนเรียบเนียน
4.  **Layer Addition**: คุณทาสีพ่นเคลือบผิวรถหลายๆ ชั้น เพื่อเก็บรายละเอียดที่ผิว

นี่คือกระบวนการเป๊ะๆ ของ `snappyHexMesh`

## 2. โครงสร้างไฟล์ `system/snappyHexMeshDict`

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

## 3. ขั้นตอนการทำงานแบบเจาะลึก (Detailed Phases)

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
ขั้นตอนที่เป็นเหมือนการ "แกะสลัก" บล็อกพื้นฐาน

1.  **Refinement:** โปรแกรมจะวนลูปตรวจสอบว่า Cell ไหนตัดผ่าน Geometry หรืออยู่ใน Refinement Region ถ้าใช่ จะทำการแตก Cell แม่ (Parent) เป็น 8 Cell ลูก (Children)
2.  **Level Control:** ความละเอียดจะถูกกำหนดเป็น "Level" (ระดับ 0 = พื้นฐาน, ระดับ 1 = แตก 1 ครั้ง, ระดับ 2 = แตก 2 ครั้ง...)
3.  **Removal:** เมื่อ Refine จนพอใจ โปรแกรมจะลบ Cell ที่อยู่ผิดฝั่งทิ้ง (กำหนดโดย `locationInMesh`)

> [!WARNING] **จุดตาย:**
> `locationInMesh` ต้องเป็นพิกัด (x y z) ที่ **ไม่อยู่** บนผิวและ **ไม่อยู่** บนขอบของ Cell (ควรเลี่ยงจุดอย่าง 0, 0.5, 1 ให้ใช้ 0.00134 แทน)

### Phase 2: Snapping (การดึงผิวให้เรียบ)
การเปลี่ยนผิว "ขั้นบันได" ให้เป็น "ผิวเรียบ"

1.  **Point Displacement:** จุดยอด (Vertices) ของเซลล์ที่อยู่ติดผิวจะถูก "ดีด" เข้าไปหาพื้นผิวของ STL
2.  **Smoothing:** เมื่อจุดขยับ Cell อาจเบี้ยว (Skewness) โปรแกรมจะทำการ Smooth (เกลี่ย) จุดภายในเพื่อกระจายความเครียด
3.  **Iterative Morphing:** ทำซ้ำหลายรอบจนกว่า Error จะต่ำกว่าเกณฑ์

### Phase 3: Layer Addition (การเพิ่มชั้นผิว)
ขั้นตอนที่ยากที่สุดและมักล้มเหลวบ่อยที่สุด

1.  **Push Back:** Mesh ที่สร้างเสร็จแล้วจะถูกดันถอยหลังออกมาในแนว Normal
2.  **Insertion:** สร้าง Cell ใหม่แทรกเข้าไปในช่องว่างนั้น
3.  **Quality Check:** ถ้าแทรกแล้ว Mesh Quality แย่ โปรแกรมจะยกเลิกการสร้าง Layer ตรงนั้น (Layer Collapse)

## 4. Workflow การรันคำสั่ง (Execution Guide)

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

## 5. การ Debug ด้วย ParaView

`snappyHexMesh` สามารถเขียนผลลัพธ์ออกมาทีละขั้นตอนได้ ถ้าคุณไม่ใส่ `-overwrite` มันจะสร้าง Time folder:
*   `0/`: Background Mesh
*   `1/`: Castellated Mesh (ดูว่าละเอียดพอไหม)
*   `2/`: Snapped Mesh (ดูว่าผิวเรียบไหม)
*   `3/`: Layer Mesh (ดูว่า Layer ขึ้นครบไหม)

> [!TIP]
> ให้เช็คทีละ Step เสมอ! อย่าพยายามแก้ Layer (Step 3) ถ้า Castellated (Step 1) ยังหยาบเกินไป เพราะ Snap จะไม่มีทางสวยถ้า Cell ต้นทางไม่ละเอียดพอ

> **ลิงก์ที่เกี่ยวข้อง**:
> - ดูวิธีเตรียม Geometry ที่สะอาด → [02_Geometry_Preparation.md](./02_Geometry_Preparation.md)
> - ดูการตั้งค่า Castellated Mesh → [03_Castellated_Mesh_Settings.md](./03_Castellated_Mesh_Settings.md)
> - ดูเทคนิค Layer Addition → [../04_SNAPPYHEXMESH_ADVANCED/01_Layer_Addition_Strategy.md](../04_SNAPPYHEXMESH_ADVANCED/01_Layer_Addition_Strategy.md)

---

## 📝 แบบฝึกหัด (Exercises)

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

ในบทถัดไป เราจะมาดูวิธีการเตรียมไฟล์ Geometry (.stl/.obj) ให้ "Clean" และพร้อมสำหรับการ Mesh ซึ่งเป็นด่านแรกที่คนส่วนใหญ่ตกม้าตาย → [02_Geometry_Preparation.md](./02_Geometry_Preparation.md)