# Utility Categories and Organization

หมวดหมู่และการจัดระเบียบ Utilities

> **ลิงก์ที่เกี่ยวข้อง**:
> - ดูภาพรวม Expert Utilities → [00_Overview.md](./00_Overview.md)
> - ดู Architecture → [02_Architecture_and_Design_Patterns.md](./02_Architecture_and_Design_Patterns.md)
> - ดู Essential Utilities → [03_Essential_Utilities_for_Common_CFD_Tasks.md](./03_Essential_Utilities_for_Common_CFD_Tasks.md)

---

## 📋 บทนำ (Introduction)

OpenFOAM มี **utilities มากกว่า 200 ตัว** แต่ไม่ต้องจำทุกตัว! สิ่งสำคัญคือการเข้าใจว่าแต่ละ utility อยู่ใน **หมวดหมู่ไหน** และ **ใช้ทำอะไร** ในบทนี้คุณจะได้เรียนรู้การจัดหมวดหมู่ utilities ตาม **workflow** ของงาน CFD

> [!TIP] **Utilities vs Solvers**
> - **Utilities**: เครื่องมือช่วยเหลือ (เตรียมข้อมูล, ตรวจสอบ, เปลี่ยนข้อมูล)
> - **Solvers**: โปรแกรมคำนวณ (simpleFoam, interFoam, etc.)
>
> ในบทนี้เราโฟกัสที่ **Utilities**

---

## 🔄 1. Organization ตาม Workflow

OpenFOAM utilities ถูกจัดกลุ่มตาม **ขั้นตอนการทำงาน (Workflow)**:

```mermaid
graph LR
    A[Pre-Processing] --> B[Mesh Manipulation]
    B --> C[Running / Parallel]
    C --> D[Post-Processing]
    D --> E[Data Conversion]

    style A fill:#e3f2fd
    style B fill:#fff3e0
    style C fill:#ffe0b2
    style D fill:#c8e6c9
    style E fill:#f3e5f5
```

---

## 🛠️ 2. Pre-Processing Utilities

### 2.1 สร้าง Mesh

| Utility | หน้าที่ | ตัวอย่างการใช้งาน | Output |
|:--------|:---------|:-------------------|:-------|
| **blockMesh** | สร้าง structured mesh จาก block definition | `blockMesh` | `polyMesh/` |
| **snappyHexMesh** | สร้าง complex mesh จาก STL geometry | `snappyHexMesh -overwrite` | `polyMesh/` |
| **extrudeMesh** | สร้าง mesh จาก 2D → 3D | `extrudeMesh` | 3D mesh |

### 2.2 ตัวอย่าง: blockMesh

```bash
# รัน blockMesh
blockMesh

# Output ที่ได้:
# --> log.blockMesh (บันทึกการรัน)
# --> constant/polyMesh/ (mesh files)

# เช็คว่า mesh ถูกสร้างหรือยัง
ls constant/polyMesh/
# points, faces, owner, neighbour, boundary
```

### 2.3 ตั้งค่าเริ่มต้น (Initialization)

| Utility | หน้าที่ | ตัวอย่าง |
|:--------|:---------|:---------|
| **setFields** | กำหนดค่าเริ่มต้น fields | `setFields` |
| **mapFields** | แมปค่าจาก case อื่น | `mapFields source_case` |
| **initFields** | สร้าง fields เปล่า | `initFields` |

**ตัวอย่าง: setFields**

```bash
# ใน system/setFieldsDict กำหนด:
defaultFieldValues
{
    volScalarFieldValue p 0;
    volVectorFieldValue U (0 0 0);
}

regions
{
    boxToCell
    {
        box (0 0 0) (1 1 1);
        fieldValues
        {
            volScalarFieldValue T 300;
        }
    }
}

# รัน
setFields

# Output:
# --> 0/ ได้รับการอัปเดตค่าตาม setFieldsDict
```

### 2.4 สร้าง Zones

| Utility | หน้าที่ | Output |
|:--------|:---------|:-------|
| **topoSet** | สร้าง cellSet, faceSet, pointSet | `sets/` |
| **setsToZones** | แปลง sets → zones | `cellZones/`, `faceZones/` |

**ตัวอย่าง: topoSet**

```bash
# สร้าง cellSet จาก box
topoSet -dict system/topoSetDict

# system/topoSetDict:
actions
(
    {
        name    heaterCells;
        type    cellSet;
        action  new;
        source  boxToCell;
        box     (0 0 0) (1 1 1);
    }
);

# Output:
# --> constant/polyMesh/sets/heaterCells
```

---

## 🔧 3. Mesh Manipulation Utilities

### 3.1 แปลง Mesh

| Utility | หน้าที่ | ตัวอย่างการใช้ |
|:--------|:---------|:-----------------|
| **transformPoints** | ขยาย/หมุน/ย้าย mesh | `transformPoints -scale "(10 10 10)"` |
| **refineMesh** | เพิ่มความละเอียด mesh | `refineMesh -overwrite` |
| **mergeMeshes** | รวม 2 meshes ต่อกัน | `mergeMeshes case1 case2` |
| **splitMeshRegions** | แยก mesh เป็น regions | `splitMeshRegions` |

**ตัวอย่าง: transformPoints**

```bash
# ขยาย mesh ใหญ่ขึ้น 10 เท่า (สำหรับ unit conversion)
transformPoints -scale "(0.001 0.001 0.001)"
# mm → m

# หมุน mesh 45 องศารอบแกน Z
transformPoints -rotate "(0 0 45)"

# ย้าย mesh ไปที่ตำแหน่งใหม่
transformPoints -translate "(1 0 0)"
```

### 3.2 ตรวจสอบ Mesh

| Utility | หน้าที่ | Output สำคัญ |
|:--------|:---------|:-------------|
| **checkMesh** | ตรวจสอบคุณภาพ mesh | `log.checkMesh` |
| **patchSummary** | สรุปข้อมูล patches | Patch sizes, types |
| **foamListTimes** | แสดง time steps | เวลาที่มีข้อมูล |

**ตัวอย่าง: checkMesh**

```bash
checkMesh > log.checkMesh 2>&1

# ผลลัพธ์ที่สำคัญ:
grep "Mesh non-orthogonosity" log.checkMesh
# → Max: 70 avg: 5

grep "Failed.*n.*:" log.checkMesh
# → 0 failed faces (ดีมาก!)

grep "Boundary" log.checkMesh
# → Patch sizes, types
```

---

## ⚡ 4. Running / Parallel Utilities

### 4.1 Parallel Processing

| Utility | หน้าที่ | ตัวอย่าง |
|:--------|:---------|:---------|
| **decomposePar** | แบ่ง mesh สำหรับ parallel | `decomposePar` |
| **reconstructPar** | รวมผลลัพธ์จาก parallel | `reconstructPar` |
| **reconstructParMesh** | รวม mesh เท่านั้น | `reconstructParMesh` |

**ตัวอย่าง: decomposePar**

```bash
# แบ่ง mesh เป็น 4 ส่วน
decomposePar

# Output:
# --> processor0/, processor1/, processor2/, processor3/
# --> แต่ละ folder มี mesh ส่วนหนึ่ง

# รัน solver แบบ parallel
mpirun -np 4 simpleFoam -parallel

# รวมผล
reconstructPar

# Output:
# --> เขียน results กลับไปยัง time directories หลัก
```

### 4.2 Utilities ขณะรัน (Running Utilities)

| Utility | หน้าที่ |
|:--------|:---------|
| **foamListTimes** | แสดง time steps ที่มี |
| **decomposePar** | เตรียม parallel |
| **solver** | รัน simulation |

---

## 📊 5. Post-Processing Utilities

### 5.1 Function Objects (หลักๆ ใช้)

| Utility | หน้าที่ | ตัวอย่าง |
|:--------|:---------|:---------|
| **postProcess** | รัน function objects | `postProcess -func forces` |
| **sample** | สุ่มข้อมูลจาก surfaces/lines | `sample -dict system/sampleDict` |
| **probes** | วัดค่าที่จุดวัด | (ใน controlDict) |

**ตัวอย่าง: postProcess**

```bash
# คำนวณ forces หลังจากรันเสร็จ
postProcess -func forces

# Output:
# --> postProcessing/forces/0/forces.dat
# time, Fx, Fy, Fz, Mx, My, Mz

# คำนวณ flow rate ผ่าน patches
postProcess -func "flowRatePatch(name=inlet)"

# คำนวณ pressure drop
postProcess -func "pressureDrop(p0 inlet outlet)"
```

### 5.2 Sample Utility

```bash
# system/sampleDict:
type sets;
sets
{
    midLine
    {
        type    uniform;
        axis    distance;
        start   (0 0 0);
        end     (1 0 0);
        nPoints 100;
    }
}

# รัน
sample

# Output:
# --> sets/midLine/1000/   (time directories)
# --> line_U.xy, line_p.xy
```

---

## 🔄 6. Data Conversion Utilities

### 6.1 Export ไปยังรูปแบบอื่น

| Utility | หน้าที่ | Output |
|:--------|:---------|:-------|
| **foamToVTK** | Export → VTK (ParaView) | `*.vtk` |
| **foamToEnsight** | Export → Ensight | `*.case` |
| **foamToSurface** | Extract surfaces | `*.obj`, `*.stl` |

**ตัวอย่าง: foamToVTK**

```bash
# Export ทุก time steps
foamToVTK

# Output:
# --> VTK/0/, VTK/100/, VTK/200/ ...
# --> ใช้เปิดใน ParaView ได้เลย

# Export เฉพาะ time step สุดท้าย
foamToVTK -latestTime

# Export เฉพาะบาง fields
foamToVTK -fields "(p U)"
```

---

## 📋 Quick Reference

### 6.1 ค้นหา Utilities

```bash
# ดู utilities ทั้งหมด
ls $FOAM_APPBIN
ls $FOAM_USER_APPBIN

# ค้นหา utility ที่มีชื่อ "mesh"
ls $FOAM_APPBIN | grep -i mesh

# ดู help
utilityName -help
```

### 6.2 Mapping ตาม Phase

| Phase | Utilities หลัก |
|:------|:--------------|
| **Pre** | blockMesh, snappyHexMesh, setFields, topoSet |
| **Mesh** | transformPoints, refineMesh, checkMesh |
| **Parallel** | decomposePar, reconstructPar |
| **Post** | postProcess, sample, foamToVTK |
| **Convert** | foamToVTK, foamToEnsight, foamToSurface |

---

## 🎯 7. Best Practices: การเลือกใช้ Utilities

### 7.1 ทำงานตามลำดับที่ถูกต้อง

```bash
# ❌ ผิด (ลำดับไม่ถูก)
decomposePar
blockMesh    # สาย!
reconstructPar

# ✅ ถูก
blockMesh      # 1. สร้าง mesh
checkMesh      # 2. ตรวจสอบ
decomposePar   # 3. แบ่ง parallel
mpirun -np 4 simpleFoam -parallel  # 4. รัน
reconstructPar # 5. รวมผล
postProcess -func forces  # 6. Post-process
```

### 7.2 ตรวจสอบผลลัพธ์เสมอ

```bash
# เช็คทุกขั้นตอน
blockMesh && grep -q "end" log.blockMesh
checkMesh && ! grep -q "Failed.*n.*:" log.checkMesh
decomposePar && ls processor*/constant/polyMesh/points
```

---

## 📝 แบบฝึกหัด (Exercises)

### ระดับง่าย (Easy)
1. **True/False**: `blockMesh` เป็น solver
   <details>
   <summary>คำตอบ</summary>
   ❌ เท็จ - `blockMesh` เป็น utility (pre-processing), ไม่ใช่ solver
   </details>

2. **เลือกตอบ**: Utility ไหนใช้ตรวจสอบคุณภาพ mesh?
   - a) checkMesh
   - b) postProcess
   - c) decomposePar
   - d) foamToVTK
   <details>
   <summary>คำตอบ</summary>
   ✅ a) checkMesh
   </details>

### ระดับปานกลาง (Medium)
3. **อธิบาย**: แตกต่างระหว่าง `decomposePar` และ `reconstructPar` คืออะไร?
   <details>
   <summary>คำตอบ</summary>
   - **decomposePar**: แบ่ง mesh ออกเป็นหลายส่วนสำหรับ parallel processing
   - **reconstructPar**: รวมผลลัพธ์จาก parallel processing กลับมาเป็น single mesh
   </details>

4. **เขียนคำสั่ง**: จงเขียนคำสั่งเพื่อ:
   - สร้าง mesh
   - ตรวจสอบ mesh
   - แบ่ง mesh เป็น 4 ส่วน
   <details>
   <summary>คำตอบ</summary>
   ```bash
   blockMesh
   checkMesh
   decomposePar
   ```
   </details>

### ระดับสูง (Hard)
5. **Hands-on**: ใช้ `transformPoints` เพื่อ:
   - ขยาย mesh 10 เท่า
   - หมุน mesh 90 องศา
   - ย้าย mesh ไป (1, 2, 3)

6. **Project**: สร้าง script ที่:
   - รัน blockMesh
   - ตรวจสอบ mesh quality
   - ถ้า mesh ผ่าน → รัน solver
   - ถ้า mesh ไม่ผ่าน → แจ้งเตือนและหยุด

---

## 🧠 Concept Check

<details>
<summary><b>1. Utilities แบ่งเป็นกี่หมวดหมู่หลัก?</b></summary>

**5 หมวดหมู่หลัก** ตาม workflow:
1. **Pre-Processing**: blockMesh, snappyHexMesh, setFields
2. **Mesh Manipulation**: transformPoints, refineMesh, checkMesh
3. **Running/Parallel**: decomposePar, reconstructPar
4. **Post-Processing**: postProcess, sample
5. **Data Conversion**: foamToVTK, foamToEnsight
</details>

<details>
<summary><b>2. topoSet ใช้ทำอะไร?</b></summary>

ใช้ **สร้าง cellZones, faceZones, pointZones** สำหรับ:
- กำหนด boundary conditions เฉพาะส่วน
- กำหนด source terms ใน region เฉพาะ
- สร้าง regions สำหรับ multi-region simulations

ตัวอย่าง: สร้าง "heater zone" สำหรับใส่ heat source
</details>

<details>
<summary><b>3. postProcess ต่างจากการใช้ ParaView อย่างไร?</b></summary>

| ด้าน | postProcess | ParaView |
|:-----|:-----------|:---------|
| **วิธีใช้** | Command line | GUI |
| **Speed** | เร็ว (batch) | ช้ากว่า (manual) |
| **Automation** | ง่าย (script) | ยาก |
| **Use case** | Batch processing, Automated | Interactive visualization |

**postProcess** เหมาะกับ **automation** และ **batch processing**
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md) — ภาพรวม Expert Utilities
- **Architecture:** [02_Architecture_and_Design_Patterns.md](02_Architecture_and_Design_Patterns.md) — สถาปัตยกรรม Utilities
- **Essential Utilities:** [03_Essential_Utilities_for_Common_CFD_Tasks.md](03_Essential_Utilities_for_Common_CFD_Tasks.md) — Utilities ที่ใช้บ่อย
- **Time-Saving Benefits:** [04_Time-Saving_Benefits.md](04_Time-Saving_Benefits.md) — ประโยชน์จาก Utilities