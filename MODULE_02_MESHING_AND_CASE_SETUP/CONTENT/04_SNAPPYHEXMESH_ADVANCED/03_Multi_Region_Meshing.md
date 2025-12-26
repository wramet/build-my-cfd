# การสร้างเมชหลายโดเมน (Multi-Region Meshing)

ในโจทย์ที่ซับซ้อน เช่น **Conjugate Heat Transfer (CHT)** (ของไหล + ของแข็ง) หรือ **Porous Media** เราจำเป็นต้องสร้าง Mesh ที่มีหลาย "Zone" อยู่ในเคสเดียวกัน โดยที่แต่ละ Zone เชื่อมต่อกันอย่างสมบูรณ์

`snappyHexMesh` รองรับการทำ Multi-Region แบบอัตโนมัติผ่านฟีเจอร์ **CellZones** และ **FaceZones**

> **ลิงก์ที่เกี่ยวข้อง**:
> - ดูการใช้ TopoSet จัดการ Zones → [../05_MESH_QUALITY_AND_MANIPULATION/02_Using_TopoSet_and_CellZones.md](../05_MESH_QUALITY_AND_MANIPULATION/02_Using_TopoSet_and_CellZones.md)

## 1. แนวคิด FaceZone vs CellZone

*   **CellZone:** กลุ่มของ Cell (ปริมาตร) เช่น "กลุ่ม Cell ที่เป็น Heatsink" (Solid) และ "กลุ่ม Cell ที่เป็นอากาศ" (Fluid)
*   **FaceZone:** กลุ่มของ Face (ผิว) ภายในโดเมน มักใช้เป็น Baffle (แผ่นกั้นบาง) หรือ Fan (พัดลม)

## 2. การเตรียม Geometry สำหรับ Multi-Region

สมมติเรามีท่อ (Fluid) ที่มีครีบระบายความร้อน (Solid) อยู่ข้างใน
เราต้องเตรียมไฟล์ STL 2 ไฟล์ (หรือไฟล์เดียวแยก Solid):
1.  `pipe_fluid.stl` (โดเมนหลัก)
2.  `fins.stl` (โดเมนย่อยข้างใน)

## 3. การตั้งค่าใน `snappyHexMeshDict`

### ขั้นตอนที่ 1: Geometry Section
โหลดไฟล์เข้ามาตามปกติ

```cpp
geometry
{
    fins.stl
    {
        type triSurfaceMesh;
        name fins;
    }
    ...
};
```

### ขั้นตอนที่ 2: RefinementSurfaces (สร้าง FaceZone)
เราต้องบอกให้ sHM สร้าง FaceZone ตรงผิวของ Fins และเก็บ Cell ข้างในไว้ (ไม่ลบทิ้ง)

```cpp
refinementSurfaces
{
    fins
    {
        level (3 3);
        faceZone finsZone;      // ตั้งชื่อ FaceZone
        cellZone finsRegion;    // ตั้งชื่อ CellZone (สำคัญมาก!)
        cellZoneInside inside;  // บอกว่า CellZone นี้คือส่วนที่อยู่ "ข้างใน" STL นี้
        insidePoint (0.1 0.1 0.1); // (Optional) ระบุจุดข้างในถ้า STL ไม่ปิดสนิทดี
    }
}
```

### ขั้นตอนที่ 3: CastellatedMeshControls
ในส่วน `locationInMesh` เราจะระบุจุดที่อยู่ใน **Fluid Domain** ตามปกติ
sHM จะรู้เองว่า:
*   พื้นที่ Fluid -> Keep
*   พื้นที่ Fins (ที่มี `cellZone` กำหนดไว้) -> Keep (ไม่ลบ แม้จะไม่ได้ contain `locationInMesh`)
*   พื้นที่อื่น -> Delete

## 4. ผลลัพธ์ที่ได้

เมื่อรันเสร็จ คุณจะได้ Mesh เดียวที่มี 2 Regions:
1.  Default Region (Fluid)
2.  `finsRegion` (Solid)

ในไฟล์ `constant/polyMesh/cellZones` จะมีรายชื่อ Cell ที่อยู่ใน Fins

## 5. การแยก Region ไปเป็นแยก Folder (SplitMeshRegions)

สำหรับ CHT solver (เช่น `chtMultiRegionFoam`) เราต้องการแยก 2 zones นี้ออกจากกันเป็นคนละ Mesh (แต่ละ Mesh มี Boundary `T`, `U`, `p` ของตัวเอง)

คำสั่ง:
```bash
splitMeshRegions -cellZones -overwrite
```

ผลลัพธ์:
จะเกิดโฟลเดอร์ `constant/fluid/polyMesh` และ `constant/solid/polyMesh`
และที่รอยต่อระหว่าง Fluid-Solid จะเกิด Boundary type ใหม่ชื่อ **`mappedWall`** (ทำหน้าที่ส่งผ่านความร้อนระหว่างกัน)

## 6. สรุป Workflow สำหรับ CHT

1.  เตรียม STL แยกชิ้น (Fluid.stl, Solid.stl)
2.  ตั้งค่า `snappyHexMeshDict`:
    *   กำหนด `cellZone` ให้กับ Solid STL
    *   `locationInMesh` อยู่ใน Fluid
3.  รัน `snappyHexMesh`
4.  รัน `splitMeshRegions -cellZones -overwrite`
5.  ตั้งค่า Boundary Condition ใน `0/fluid/...` และ `0/solid/...` ให้รอยต่อเป็น `turbulentTemperatureCoupledBaffleMixed`

**Multi-Region Meshing Workflow:**
```mermaid
graph TB
    Start[1. Prepare STLs<br/>fluid.stl + solid.stl] --> Step2[2. Setup snappyHexMeshDict<br/>Define cellZone for solid]
    Step2 --> Step3[3. Run snappyHexMesh<br/>Single mesh with zones]
    Step3 --> Step4[4. splitMeshRegions<br/>Separate fluid/constant<br/>and solid/constant]
    Step4 --> Step5[5. Setup BCs<br/>mappedWall at interface]
    Step5 --> Done[Ready for chtMultiRegionFoam]

    style Start fill:#e3f2fd
    style Step2 fill:#fff3e0
    style Step3 fill:#ffe0b2
    style Step4 fill:#ffcc80
    style Step5 fill:#c8e6c9
    style Done fill:#4CAF50
```

นี่คือวิธีที่มืออาชีพใช้ทำ Simulation หม้อน้ำ, Heat Exchanger, หรือมอเตอร์ไฟฟ้า!

---

## 📝 แบบฝึกหัด (Exercises)

### แบบฝึกหัดระดับง่าย (Easy)
1. **True/False**: `splitMeshRegions` สร้าง Mesh แยกกันสำหรับแต่ละ Region
   <details>
   <summary>คำตอบ</summary>
   ✅ จริง - สร้าง `constant/fluid/polyMesh` และ `constant/solid/polyMesh` แยกกัน
   </details>

2. **เลือกตอบ**: Boundary type ไหนที่เกิดขึ้นอัตโนมัติระหว่าง Fluid-Solid interface หลังจาก `splitMeshRegions`?
   - a) wall
   - b) patch
   - c) mappedWall
   - d) cyclic
   <details>
   <summary>คำตอบ</summary>
   ✅ c) mappedWall - สำหรับส่งผ่านความร้อนระหว่างกัน
   </details>

### แบบฝึกหัดระดับปานกลาง (Medium)
3. **อธิบาย**: ทำไมต้องกำหนด `cellZoneInside inside` ใน `refinementSurfaces`?
   <details>
   <summary>คำตอบ</summary>
   เพื่อบอก sHM ว่า Cell ที่อยู่ข้างใน STL นี้คือ "Solid region" ที่ต้องเก็บไว้ ไม่ให้ลบทิ้ง
   </details>

4. **สร้าง**: จงเขียน `refinementSurfaces` block สำหรับ `heatsink.stl` ที่กำหนด cellZone ชื่อ `heatsinkZone`
   <details>
   <summary>คำตอบ</summary>
   ```cpp
   refinementSurfaces
   {
       heatsink.stl
       {
           level (2 3);
           faceZone heatsinkZone;
           cellZone heatsinkRegion;
           cellZoneInside inside;
       }
   }
   ```
   </details>

### แบบฝึกหัดระดับสูง (Hard)
5. **Hands-on**: สร้าง Mesh 2 Regions (กล่อง + sphere ตรงกลาง) แล้วรัน `splitMeshRegions` และตรวจสอบผลลัพธ์

6. **วิเคราะห์**: เปรียบเทียบ Multi-region meshing กับการสร้าง Mesh แยกแล้วค่อย merge ในแง่ของ:
   - ความง่ายในการ setup
   - ความต่อเนื่องของ mesh ที่รอยต่อ
   - ความยืดหยุ่นในการปรับเปลี่ยน geometry