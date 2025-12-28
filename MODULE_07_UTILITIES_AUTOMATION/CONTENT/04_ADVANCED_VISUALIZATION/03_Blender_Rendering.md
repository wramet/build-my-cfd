# 🎬 การเรนเดอร์ระดับภาพยนตร์ด้วย Blender (Cinematic Rendering with Blender)

**วัตถุประสงค์การเรียนรู้ (Learning Objectives)**: เปลี่ยนผลลัพธ์ CFD ทางวิทยาศาสตร์ให้เป็นงานศิลปะที่สวยงามสมจริงสำหรับการนำเสนอระดับสูงและการตลาด
**ระดับความยาก**: ขั้นสูง (Advanced)

> [!TIP] **ทำไมต้อง Blender สำหรับ OpenFOAM? (Why Blender for OpenFOAM?)**
> การใช้ Blender กับผลลัพธ์ OpenFOAM ไม่ใช่เรื่องของ "ความแม่นยำทางวิทยาศาสตร์" แต่เป็นเรื่องของ **"การสื่อสารผลลัพธ์" (Communication)**
> - **ParaView** → ใช้สำหรับ **วิเคราะห์ข้อมูล** (Analysis) เช่น ตรวจสอบ Convergence, ดู Residuals, วัดค่าที่ตำแหน่งต่างๆ
> - **Blender** → ใช้สำหรับ **การนำเสนอ** (Presentation) เช่น สร้างภาพสวยๆ สำหรับ Report, ทำ Video Demo ส่งลูกค้า, หรือทำ Marketing Material
>
> **การเชื่อมต่อ OpenFOAM → Blender:**
> 1. OpenFOAM เก็บผลลัพธ์ไว้ในโฟลเดอร์เวลา (`0/`, `0.01/`, `0.02/`, ...) ซึ่งเป็นรูปแบบข้อมูลที่ Blender อ่านไม่ได้
> 2. ต้องใช้ utility `foamToVTK` เพื่อแปลงข้อมูลให้เป็น VTK format ก่อน
> 3. จากนั้นใช้ ParaView เพื่อ **Extract Surface**, **Create Streamlines**, หรือ **Create Iso-surfaces**
> 4. สุดท้าย Export ไฟล์เหล่านั้นเป็น X3D/GLTF/PLY format เพื่อนำเข้า Blender
>
> **เป้าหมายสูงสุด:** แปลงตัวเลขที่ซับซ้อน (U, p, k, epsilon, alpha.water) ให้กลายเป็นภาพที่ "เข้าใจง่าย" และ "สวยงาม" สำหรับคนทั่วไป

---

> [!TIP] **เปรียบเทียบ Blender (Analogy)**
> ให้คิดว่า **ParaView** คือ **"ห้องแล็บ"** ที่ทุกอย่างต้องชัดเจน ถูกต้อง แม่นยำ ขาว-ดำ-สีตามค่าตัวเลข
> ส่วน **Blender** คือ **"สตูดิโอถ่ายทำภาพยนตร์"**
> - ที่นี่เราสามารถ **"จัดแสง"** (Lighting) ให้ดูดราม่าหรือนุ่มนวล
> - เราสามารถ **"เปลี่ยนวัสดุ"** (Shading) จากพื้นผิวสีทึบๆ ให้กลายเป็น **"แก้วใส"** (Water/Glass) ที่มีการหักเหแสง หรือ **"ไฟที่เรืองแสง"** (Fire Emission)
> - เราสามารถใส่ **"เมหมอก"** (Volumetric Fog) เพื่อสร้างบรรยากาศ
> เป้าหมายไม่ใช่เพื่อ "วิเคราะห์ข้อมูล" แต่เพื่อ "เล่าเรื่องราว" และ "ดึงดูดผู้ชม"

---

## 1. ทำไมต้องใช้ Blender สำหรับ CFD?

ในงานวิศวกรรมทั่วไป ParaView ก็เพียงพอแล้ว แต่ในบางสถานการณ์ เราต้องการมากกว่าความชัดเจน:

1.  **Photorealism**: การทำให้ของเหลวดูเหมือนน้ำจริงๆ (มีการสะท้อน, ความโปร่งใส)
2.  **Marketing & Presentation**: การนำเสนอโครงการต่อลูกค้าหรือนักลงทุนที่ไม่ใช่วิศวกร
3.  **Complex Compositions**: การรวมผล CFD เข้ากับโมเดล CAD ของผลิตภัณฑ์จริง (เช่น รถยนต์, อาคาร) หรือสภาพแวดล้อมจริง

---

## 2. เวิร์กโฟลว์: OpenFOAM $\to$ ParaView $\to$ Blender

> [!NOTE] **📂 OpenFOAM Context: Data Conversion Pipeline**
> ก่อนที่จะส่งข้อมูลไป Blender ได้ ต้องแปลงข้อมูลจากรูปแบบ OpenFOAM native ให้เป็นรูปแบบที่ Blender เข้าใจก่อน:
>
> **1. การแปลงข้อมูล (Data Conversion):**
> ```bash
> # ใช้ utility ของ OpenFOAM เพื่อแปลงข้อมูลจาก OpenFOAM format เป็น VTK format
> foamToVTK -latestTime  # แปลงเฉพาะเวลาล่าสุด
> foamToVTK              # แปลงทุก time step
> ```
> - **Input:** โฟลเดอร์เวลา (`0/`, `0.1/`, `0.2/`, ...) ที่มีไฟล์ field data (U, p, alpha.water, k, epsilon, etc.)
> - **Output:** โฟลเดอร์ `VTK/` ที่มีไฟล์ `.vtk` หรือ `.vtu` (สำหรับ unstructured mesh)
>
> **2. การเลือก Field ที่ต้องการ:**
> - **Velocity Field (U):** ใช้สร้าง Streamlines, Vector plots
> - **Pressure Field (p):** ใช้สร้าง Contour แสดงการกระจายความดัน
> - **Volume Fraction (alpha.water):** ใช้สร้าง Iso-surface แสดง interface ระหว่างของไหล (เช่น น้ำ-อากาศ)
> - **Turbulence Fields (k, omega, epsilon):** ใช้ visualise โซนที่มี turbulence สูง
> - **Q-criterion:** ใช้ visualise โครงสร้าง vortices (vortex cores)
>
> **3. การ Export จาก ParaView:**
> - เปิดไฟล์ VTK ใน ParaView
> - ใช้ Filter: **Contour** (สำหรับ iso-surface), **StreamTracer** (สำหรับ streamlines)
> - Export เป็น X3D/GLTF/PLY เพื่อนำเข้า Blender
>
> **ข้อควรระวัง:** การแปลงข้อมูลด้วย `foamToVTK` อาจสร้างไฟล์ขนาดใหญ่มากถ้า mesh ละเอียด ควรใช้ options เช่น `-surfaceFields` หรือ `-cellSet` เพื่อลดปริมาณข้อมูล

OpenFOAM ไม่มีวิธีส่งข้อมูลไป Blender โดยตรง เราต้องใช้ ParaView เป็นตัวกลาง:

```mermaid
flowchart LR
    A[OpenFOAM Case] -->|foamToVTK| B[ParaView]
    B -->|Filter: Extract Surface| C[Geometry]
    B -->|Filter: Tube| D[Streamlines]
    C & D -->|Export: X3D/GLTF/PLY| E[Blender]
    E -->|Materials & Lighting| F[Render]
```

### 2.1 การเตรียมข้อมูลใน ParaView

> [!NOTE] **📂 OpenFOAM Context: Field Selection & Extraction**
> การเตรียมข้อมูลใน ParaView ก่อนส่งไป Blender เป็นการแปลง **Field Data** ให้เป็น **Geometric Data** ที่ Blender เข้าใจ:
>
> **1. Iso-surfaces (Contour):**
> - **ใช้กับ:** Volume Fraction (`alpha.water`), Q-criterion, Pressure (`p`)
> - **ตัวอย่าง:** สร้าง interface ระหว่างน้ำและอากาศ โดยตั้งค่า Contour value = 0.5 สำหรับ `alpha.water`
> - **OpenFOAM Source:** Field `alpha.water` จาก solver `interFoam`, `multiphaseInterFoam`
>
> **2. Streamlines (StreamTracer with Tube Filter):**
> - **ใช้กับ:** Velocity Field (`U`)
> - **ตัวอย่าง:** สร้างเส้นแสดงทิศทางการไหล และใช้ Tube filter เพื่อให้มีความหนา (3D geometry)
> - **OpenFOAM Source:** Field `U` จากทุก solver (simpleFoam, pimpleFoam, interFoam, etc.)
> - **ข้อควรระวัง:** ต้องใช้ **Tube** filter เพราะ Blender ไม่เห็น Lines 1D ใน rendering
>
> **3. Slices (Cut Planes):**
> - **ใช้กับ:** ทุก Field ที่ต้องการดู Cross-section
> - **ตัวอย่าง:** สร้าง Slice บนระนาบ XY, YZ, หรือ XZ และใช้ **Triangulate** filter
> - **OpenFOAM Source:** 任意 Field (`U`, `p`, `T`, `k`, etc.)
>
> **4. Scalar Coloring (Vertex Colors):**
> - **ใช้กับ:** การแสดงค่า Field เช่น Velocity magnitude, Pressure บนพื้นผิว
> - **ตัวอย่าง:** ใช้ ParaView's "Color by" และ Export เป็น X3D เพื่อรักษาสี
> - **OpenFOAM Source:** 任意 Scalar Field (magnitude of `U`, `p`, `T`, etc.)
>
> **ข้อควรระวัง:** ใช้ **Decimate** filter ใน ParaView เพื่อลดจำนวน polygons ถ้า mesh ละเอียดเกินไป ซึ่งจะทำให้ Blender ทำงานช้าหรือค้าง

Blender ทำงานกับ "พื้นผิว" (Polygonal Mesh) ได้ดีที่สุด ไม่ใช่ Volume Data (แม้จะทำได้แต่ยากกว่า)

1.  **Iso-surfaces**: สร้าง Contour ของ Q-criterion หรือ Volume Fraction (alpha.water)
2.  **Streamlines**: สร้าง StreamTracer และใช้ filter **Tube** เพื่อเปลี่ยนเส้นให้เป็นท่อ 3 มิติ (สำคัญมาก! Blender มองไม่เห็นเส้น 1D)
3.  **Slices**: สร้าง Slice และใช้ **Triangulate** filter
4.  **Export**: ไปที่ `File > Export Scene...` แล้วเลือก format **X3D** (แนะนำ), **GLTF**, หรือ **PLY**

> [!WARNING] **ขนาดไฟล์**
> ไฟล์ Geometry ที่ Export อาจมีขนาดใหญ่มาก ควรใช้ **Decimate** filter ใน ParaView เพื่อลดจำนวน Polygons ลงก่อน Export หากรายละเอียดสูงเกินความจำเป็น

---

## 3. การตั้งค่าใน Blender (Blender Setup)

### 3.1 การนำเข้า (Import)

1.  เปิด Blender ลบ Cube เริ่มต้นทิ้ง
2.  `File > Import > X3D Extensible 3D (.x3d)`
3.  ปรับ Scale (OpenFOAM เป็นเมตร, Blender เป็นเมตร แต่บางที Export มา scale อาจเพี้ยน ให้ตรวจสอบ Dimension)
4.  คลิกขวาที่วัตถุเลือก **Shade Smooth** เพื่อลบเหลี่ยมมุมของ Mesh

### 3.2 การสร้างวัสดุ (Materials)

นี่คือหัวใจสำคัญของการทำให้ดูสมจริง:

**วัสดุน้ำ (Water Material):**
- ใช้ **Principled BSDF**
- **Transmission**: 1.0 (โปร่งใส)
- **Roughness**: 0.0 - 0.1 (ผิวมันวาว)
- **IOR (Index of Refraction)**: 1.333 (ดัชนีหักเหของน้ำ)
- **Color**: สีฟ้าอ่อน

**วัสดุควัน/ไฟ (Smoke/Fire Material):**
- ใช้ **Principled Volume** (ต่อเข้ากับ Volume socket ของ Material Output)
- **Density**: ควบคุมความหนาแน่นของควัน
- **Emission Strength**: ควบคุมความสว่างของไฟ
- **Emission Color**: ใช้ Blackbody node เพื่อจำลองสีอุณหภูมิ

**วัสดุ Streamlines:**
- ใช้ **Emission Shader** ผสมกับ **Glass**
- ทำให้เส้นดูเรืองแสงและมีความล้ำสมัย

### 3.3 การจัดแสง (Lighting)

แสงที่ดีเปลี่ยนโมเดลโง่ๆ ให้ดูโปรได้:

1.  **HDRI (High Dynamic Range Imaging)**: ใช้รูปภาพ 360 องศาเป็นแสงสภาพแวดล้อม (โหลดฟรีจาก PolyHaven) ให้แสงเงาที่สมจริงที่สุด
2.  **Area Lights**: ใช้เสริมแสงในจุดที่ต้องการเน้น (Rim Light, Key Light)

---

## 4. การเรนเดอร์ (Rendering Engines)

Blender มี 2 เครื่องยนต์หลัก:

| Engine | ลักษณะ | เหมาะสำหรับ |
| :--- | :--- | :--- |
| **Eevee** | Real-time (เหมือน Game Engine), เร็วมาก | Animation ยาวๆ, พรีวิว, งานที่ไม่เน้น Refraction เป๊ะๆ |
| **Cycles** | Ray-tracing (คำนวณแสงจริง), ช้าแต่สวยสมจริง | ภาพนิ่ง, งานที่ต้องการความสมจริงสูงสุด (แก้ว, น้ำ) |

---

## 5. การทำ Automation ด้วย Python (`bpy`)

> [!NOTE] **📂 OpenFOAM Context: Automated Workflow Integration**
> การใช้ Python ใน Blender เชื่อมต่อกับ OpenFOAM workflow ได้หลายวิธี:
>
> **1. Batch Processing Multiple Time Steps:**
> - **OpenFOAM Output:** หลาย time directories (`0.1/`, `0.2/`, `0.3/`, ...)
> - **ParaView Script:** ใช้ Python script ของ ParaView (`pvpython`) เพื่อ:
>   - เปิดแต่ละ time step
>   - สร้าง iso-surface/streamlines
>   - Export เป็น X3D/PLY โดยอัตโนมัติ
> - **Blender Script:** ใช้ `bpy` เพื่อ:
>   - นำเข้าไฟล์ทั้งหมด
>   - ตั้งค่า material (water, glass, emission)
>   - Render เป็น image sequence
>
> **2. Function Objects Integration:**
> - **OpenFOAM:** ใช้ `functions` ใน `controlDict` เพื่อ export surface/sampling data อัตโนมัติระหว่าง simulation
>   ```cpp
>   // ตัวอย่าง controlDict
>   functions
>   {
>       exportSurface
>       {
>           type            surfaces;
>           functionObjectLibs ("libsampling.so");
>           outputControl   timeStep;
>           outputInterval  10;
>           surfaceFormat   vtk;
>           fields          (U p alpha.water);
>           surfaces
>           (
>               zPlane
>               {
>                   type        plane;
>                   planeType   pointAndNormal;
>                   pointAndNormalDict
>                   {
>                       point   (0 0 0);
>                       normal  (0 0 1);
>                   }
>               }
>           );
>       }
>   }
>   ```
> - **Blender:** อ่านไฟล์ VTK ที่ export มาจาก function object โดยตรง
>
> **3. Python Automation Pipeline:**
> ```bash
> # ตัวอย่าง workflow แบบ end-to-end
> # 1. Run OpenFOAM simulation
> solverName > log &
>
> # 2. ใช้ pvpython export เป็น X3D ทุกๆ N time steps
> pvpython export_paraview.py
>
> # 3. ใช้ Blender render animation
> blender -b -P render_blender.py
> ```
>
> **4. การตั้งค่า Material อัตโนมัติ:**
> - ตั้งค่า `Principled BSDF` parameters (Transmission, IOR, Roughness) ผ่าน script
> - กำหนด Vertex Color ให้ตรงกับ field values จาก OpenFOAM (เช่น velocity magnitude)
>
> **ข้อดี:** ลดเวลาทำงานซ้ำๆ และทำให้การสร้าง visualization ที่ซับซ้อนเป็นไปโดยอัตโนมัติ

เช่นเดียวกับ ParaView, Blender สามารถเขียนสคริปต์ได้ด้วย `bpy` เพื่อทำงานซ้ำๆ:

```python
import bpy
import os

# โฟลเดอร์ที่มีไฟล์ PLY (1 ไฟล์ต่อ 1 Time Step)
input_dir = "/path/to/ply_files"
ply_files = sorted([f for f in os.listdir(input_dir) if f.endswith(".ply")])

# ลบวัตถุเก่าทั้งหมด
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# ตั้งค่า Material
mat = bpy.data.materials.new(name="Water")
mat.use_nodes = True
nodes = mat.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Transmission'].default_value = 1.0
bsdf.inputs['Roughness'].default_value = 0.05
bsdf.inputs['IOR'].default_value = 1.333

# Loop นำเข้าและเรนเดอร์ (แบบง่าย - หรือใช้ Modifier เพื่อ swap mesh)
for i, ply_file in enumerate(ply_files):
    bpy.ops.import_mesh.ply(filepath=os.path.join(input_dir, ply_file))
    obj = bpy.context.selected_objects[0]
    obj.data.materials.append(mat)
    
    # ตั้งค่าเฟรมและเรนเดอร์ (ในทางปฏิบัติมักใช้วิธี Sequence Modifier)
    # ...
```

> [!TIP] **Mesh Sequence Cache**
> วิธีที่ดีที่สุดในการทำ Animation ใน Blender จากไฟล์ CFD คือการนำเข้าไฟล์แรก แล้วใช้ Modifier ชื่อ **"Mesh Sequence Cache"** เพื่ออ่านไฟล์ Alembic (.abc) หรือ PC2 ที่ Export มาจาก ParaView วิธีนี้ไม่ต้องเขียน Python เพื่อ loop import ทีละเฟรม

---

## 6. ข้อจำกัดและแนวทางแก้ไข

- **ปัญหา**: "Z-fighting" (ผิวซ้อนกันกระพริบ)
    - **แก้**: ขยับวัตถุห่างกันเล็กน้อย หรือใช้ Pass Index
- **ปัญหา**: ไฟล์ใหญ่เกินไป Blender ค้าง
    - **แก้**: ลดรายละเอียด Mesh ตั้งแต่ใน ParaView (Decimate)
- **ปัญหา**: สี (Scalar Field) ไม่มาด้วย
    - **แก้**: X3D/VRML รองรับ Vertex Color ต้องตั้งค่า Material ใน Blender ให้ใช้ Attribute "Col" หรือ Vertex Color

---

## 🧠 ตรวจสอบความเข้าใจ (Concept Check)

1.  **ถาม:** ทำไมเราต้องใช้ Filter "Tube" กับ Streamlines ใน ParaView ก่อนส่งไป Blender?
    <details>
    <summary>เฉลย</summary>
    <b>ตอบ:</b> เพราะ Streamlines ปกติเป็นเส้น 1 มิติ (Lines) ซึ่งไม่มี "พื้นผิว" ให้แสงตกกระทบ และ Blender (โดยเฉพาะ Cycles Render) จะมองไม่เห็นเส้นเหล่านี้ในการเรนเดอร์ การทำ Tube เปลี่ยนเส้นให้เป็นทรงกระบอก 3 มิติที่มีผิวรับแสงเงาได้
    </details>

2.  **ถาม:** ถ้าต้องการทำ Animation น้ำไหลที่สมจริงที่สุด ควรใช้ Render Engine ตัวไหนใน Blender?
    <details>
    <summary>เฉลย</summary>
    <b>ตอบ:</b> **Cycles** เพราะเป็น Ray-tracing engine ที่คำนวณการสะท้อน (Reflection) และการหักเห (Refraction) ของแสงผ่านน้ำได้ถูกต้องตามหลักฟิสิกส์ ในขณะที่ Eevee ใช้การประมาณค่า (Screen Space Reflections) ซึ่งอาจดูไม่สมจริงเท่า
    </details>
