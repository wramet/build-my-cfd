# เครื่องมือจัดการเมช (Mesh Manipulation Tools)

นอกจาก `blockMesh` และ `snappyHexMesh` แล้ว OpenFOAM ยังมีชุดเครื่องมือ Utility (กองทัพมด) เพื่อจัดการ Mesh ที่สร้างเสร็จแล้ว ให้พร้อมใช้งานหรือแก้ไขปัญหาเฉพาะหน้า

> **ลิงก์ที่เกี่ยวข้อง**:
> - ดู Mesh Quality Criteria → [01_Mesh_Quality_Criteria.md](./01_Mesh_Quality_Criteria.md)
> - ดู TopoSet และ CellZones → [02_Using_TopoSet_and_CellZones.md](./02_Using_TopoSet_and_CellZones.md)

## 1. การแปลงพิกัด (Transformations)

### `transformPoints`
เครื่องมือสารพัดประโยชน์สำหรับ ย่อ/ขยาย, หมุน, และย้ายตำแหน่ง Mesh

*   **Scale (ย่อ/ขยาย):** เปลี่ยนหน่วยจาก mm เป็น m
    ```bash
    transformPoints -scale '(0.001 0.001 0.001)'
    ```
*   **Translate (ย้าย):** ย้ายจุด (0,0,0) ไปที่อื่น
    ```bash
    transformPoints -translate '(10 0 0)'
    ```
*   **Rotate (หมุน):** หมุนรอบแกน
    ```bash
    # หมุนรอบแกน Z 45 องศา (Roll)
    transformPoints -rollPitchYaw '(0 0 45)' 
    ```

## 2. การรวมและผสม (Merging & Stitching)

### `mergeMeshes`
เอา 2 Case มารวมกันเป็น 1 Case (แต่ยังแยก Region กัน หรือ Mesh ไม่ต่อกัน)
```bash
mergeMeshes . case1 . case2
# ผลลัพธ์จะอยู่ที่ case1 (Master)
```

### `stitchMesh`
เย็บ Patch 2 อันที่อยู่ติดกันให้เนื้อ Mesh เชื่อมกัน (Topologically merge)
*   **เงื่อนไข:** จุดบน Patch ทั้งสองต้องตรงกันเป๊ะ (Perfect match) หรือใช้ Tolerance
*   **การใช้งาน:** `stitchMesh masterPatch slavePatch`

## 3. การจัดการ Topology

### `renumberMesh`
จัดเรียงลำดับ Index ของ Cell ใหม่ (Reordering) เพื่อลด Bandwidth ของ Sparse Matrix
*   **ผลลัพธ์:** ทำให้ Solver รันเร็วขึ้น (Cache efficiency ดีขึ้น) และไฟล์ผลลัพธ์เล็กลงเล็กน้อย
*   **คำแนะนำ:** **ควรทำเสมอ** ก่อนรันเคสใหญ่ๆ!

### `mirrorMesh`
สะท้อน Mesh ข้ามระนาบ (Mirror)
*   เหมาะกับงานสมมาตร (Symmetric) สร้างแค่ครึ่งเดียว แล้ว Mirror เอา
*   ต้องระบุระนาบใน `system/mirrorMeshDict`

### `subsetMesh`
ตัดเอาเฉพาะส่วนของ Mesh ที่ต้องการออกมา (ตาม CellSet)
*   มีประโยชน์มากเวลา Mesh ใหญ่เกินไป แล้วอยากตัดมา Test รันแค่ส่วนเล็กๆ
```bash
# ตัดเฉพาะ CellSet c0 มาสร้าง Mesh ใหม่
subsetMesh c0 -patch outerWall
```

## 4. การตรวจสอบ (Inspection)

### `checkMesh`
(กล่าวไปแล้วในบท Mesh Quality) แต่อย่าลืม Option เสริม:
*   `-allGeometry`: เช็คละเอียดเรื่อง Geometric error
*   `-allTopology`: เช็คละเอียดเรื่องการเชื่อมต่อ
*   `-constant`: เช็ค Mesh ใน folder constant (ไม่ต้องรอ time 0)

### `patchSummary`
ดูข้อมูลสรุปของแต่ละ Patch (จำนวนหน้า, พื้นที่, ประเภท)
*   ช่วยเช็คว่าเราตั้งชื่อ Patch ถูกไหม หรือพื้นที่หน้าตัด Inlet ถูกต้องตามทฤษฎีไหม

---
**สรุป Workflow ของโปร:**
1.  Generate Mesh (`blockMesh`/`snappyHexMesh`)
2.  `checkMesh` (ตรวจสอบคุณภาพ)
3.  `transformPoints` (ถ้าขนาดผิด หรือต้องย้ายที่)
4.  `renumberMesh` (เพื่อความเร็ว)
5.  Ready to solve!

**Mesh Manipulation Tools Workflow:**
```mermaid
graph TB
    Start[1. Generate Mesh<br/>blockMesh / snappyHexMesh] --> Check[2. checkMesh<br/>Verify quality]
    Check --> Quality{Mesh OK?}

    Quality -->|No| Fix[Fix Mesh Issues]
    Fix --> TransformA[transformPoints<br/>Scale/Translate/Rotate]
    Fix --> Stitch[stitchMesh<br/>Connect patches]
    Fix --> Merge[mergeMeshes<br/>Combine cases]

    Quality -->|Yes| TransformB[transformPoints<br/>If needed]
    TransformB --> Mirror[mirrorMesh<br/>If symmetric]
    Mirror --> Subset[subsetMesh<br/>If need part]
    Subset --> Renumber[renumberMesh<br/>Optimize ordering]

    TransformA --> Renumber
    Stitch --> Renumber
    Merge --> Renumber

    Renumber --> Final[5. Ready to Solve]

    style Start fill:#e3f2fd
    style Check fill:#fff3e0
    style Quality fill:#ffe0b2
    style Fix fill:#ffccbc
    style Renumber fill:#c8e6c9
    style Final fill:#4CAF50
    style TransformA fill:#f8bbd0
    style TransformB fill:#f8bbd0
```

---

## 📝 แบบฝึกหัด (Exercises)

### แบบฝึกหัดระดับง่าย (Easy)
1. **True/False**: `renumberMesh` ช่วยเพิ่มความเร็วในการคำนวณของ Solver
   <details>
   <summary>คำตอบ</summary>
   ✅ จริง - จัดเรียงลำดับ Cell ใหม่เพื่อลด Bandwidth ของ Sparse Matrix
   </details>

2. **เลือกตอบ**: คำสั่งไหนใช้สำหรับเปลี่ยนหน่วย Mesh จาก mm เป็น m?
   - a) stitchMesh
   - b) transformPoints -scale
   - c) mergeMeshes
   - d) mirrorMesh
   <details>
   <summary>คำตอบ</summary>
   ✅ b) transformPoints -scale '(0.001 0.001 0.001)'
   </details>

### แบบฝึกหัดระดับปานกลาง (Medium)
3. **อธิบาย**: แตกต่างระหว่าง `mergeMeshes` และ `stitchMesh` คืออะไร?
   <details>
   <summary>คำตอบ</summary>
   - mergeMeshes: รวม 2 Case เข้าด้วยกัน แต่ Mesh ยังแยกกัน (ไม่ต่อกัน)
   - stitchMesh: เย็บ Patch 2 อันให้เชื่อมต่อกันทาง Topology
   </details>

4. **เขียนคำสั่ง**: จงเขียนคำสั่งเพื่อหมุน Mesh รอบแกน Z 45 องศา
   <details>
   <summary>คำตอบ</summary>
   ```bash
   transformPoints -rollPitchYaw '(0 0 45)'
   ```
   </details>

### แบบฝึกหัดระดับสูง (Hard)
5. **Hands-on**: สร้าง Mesh แล้วทดลองใช้ `renumberMesh` เปรียบเทียบขนาดไฟล์ก่อน/หลัง

6. **วิเคราะห์**: เปรียบเทียบกลยุทธ์ระหว่าง:
   - สร้าง Mesh ขนาดใหญ่ทีเดียว
   - สร้าง Mesh เล็กๆ แยกแล้วค่อย merge
   ในแง่ของเวลาในการสร้าง Mesh และคุณภาพของ Mesh ที่ได้