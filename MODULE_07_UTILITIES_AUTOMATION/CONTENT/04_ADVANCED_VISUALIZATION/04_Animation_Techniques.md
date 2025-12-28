# 🎥 เทคนิคการสร้างแอนิเมชันขั้นสูง (Advanced Animation Techniques)

> [!TIP] ทำไม Animation สำคัญสำหรับ CFD Engineer?
> แอนิเมชันไม่ได้มีไว้เพื่อความสวยงามเท่านั้น แต่มันเป็น **เครื่องมือสื่อสารที่ทรงพลัง** ที่ช่วยให้:
> - **วิศวกรรับรู้** ลักษณะการไหลที่ซับซ้อน (เช่น Vortex shedding, Recirculation zones) ซึ่งมองไม่เห็นจากภาพนิ่ง
> - **ผู้บริหาร/ลูกค้าเข้าใจ** ผลลัพธ์ได้ทันทีโดยไม่ต้องอ่านกราฟหลายสิบรูป
> - **ตรวจหาข้อผิดพลาด** ได้ง่ายขึ้น (เช่น Unphysical oscillation) เมื่อดูเป็นแอนิเมชัน
> - **ยืนยันความถูกต้อง** ด้วยการเปรียบเทียบ Pattern การไหลกับ Theory หรือ Experiment

**วัตถุประสงค์การเรียนรู้ (Learning Objectives)**: สร้างวิดีโอผลลัพธ์ CFD ที่ลื่นไหล สื่อความหมาย และดึงดูดความสนใจ โดยเน้นเทคนิคการเล่าเรื่องผ่านภาพเคลื่อนไหว
**ระดับความยาก**: ปานกลาง-สูง (Intermediate-Advanced)

---

## 1. มากกว่าแค่ภาพเคลื่อนไหว (Beyond Simple Playback)

> [!NOTE] **📂 OpenFOAM Context: การเก็บข้อมูลสำหรับ Animation**
> ก่อนจะมาสร้างแอนิเมชัน ต้องตั้งค่าการเก็บผลลัพธ์ใน `system/controlDict` ให้เหมาะกับการทำ Animation:
> - **`writeInterval`**: กำหนดความถี่ในการเขียนผลลัพธ์ (เช่น `0.01;` สำหรับ Transient case ที่ละเอียด)
> - **`writeFormat`**: ใช้ `binary` แทน `ascii` เพื่อประหยัดพื้นที่และเขียนเร็วขึ้น
> - **`writeCompression`**: ใช้ `on;` เพื่อบีบอัดไฟล์ (แต่ ParaView อาจอ่านช้าขึ้นนิดหน่อย)
>
> **Function Objects** สำหรับ Animation:
> ```cpp
> // ใน system/controlDict
> functions
> {
>     // สำหรับ Plot Graph แบบ Real-time
>     probeLocation
>     {
>         type        sets;
>         set         probeCell;
>         surface     sampleSurface;
>         fields      (p U);
>     }
> }
> ```

การกดปุ่ม "Play" ใน ParaView เป็นแค่จุดเริ่มต้น แอนิเมชันที่ดีต้องมีการวางแผน:
- **มุมกล้อง (Camera Work)**: กล้องควรเคลื่อนที่เพื่อแสดงจุดที่น่าสนใจ ไม่ใช่แช่นิ่งๆ
- **จังหวะ (Pacing)**: ส่วนที่น่าเบื่อควรเร่งความเร็ว ส่วนที่สำคัญควรสโลว์โมชั่น
- **ข้อมูลประกอบ (Annotation)**: กราฟวิ่งตามเวลา (Dynamic Graphs) ช่วยยืนยันสิ่งที่เห็นในภาพ

---

## 2. ประเภทของแอนิเมชัน CFD

> [!NOTE] **📂 OpenFOAM Context: ข้อมูลที่ต้องการ**
> แต่ละประเภท Animation ต้องการข้อมูลจาก OpenFOAM ที่แตกต่างกัน:
> - **Temporal Animation**: ต้องการ Directory `0/`, `0.01/`, `0.02/`, ... (Time directories) จากการ run Transient solver
> - **Spatial Animation**: ต้องเพียง Directory เดียว (เช่น `500/`) สำหรับ Steady state result
> - **Parameter Sweep**: ต้องการหลาย Case folders (เช่น `case_v10/`, `case_v20/`, `case_v30/`) หรือใช้ `sampleDict` เพื่อ dump ข้อมูลหลายจุด

### 2.1 Temporal Animation (แอนิเมชันตามเวลา)
แสดงวิวัฒนาการของการไหลตั้งแต่ $t_{start}$ ถึง $t_{end}$
- **เหมาะสำหรับ**: Transient flow, Vortex shedding, Sloshing
- **เทคนิค**: ใช้ **Temporal Interpolator** เพื่อให้วิดีโอลื่นไหลแม้ Time step ของการคำนวณจะห่างกัน

### 2.2 Spatial Animation (แอนิเมชันตามพื้นที่)
หยุดเวลา (Freeze Time) แล้วเคลื่อนกล้องไปรอบๆ หรือตัด Slice ไล่ไปตามแกน
- **เหมาะสำหรับ**: Steady state result, การสำรวจโครงสร้างภายในที่ซับซ้อน
- **เทคนิค**: ใช้ **Camera Path** หรือ **Animation View** ใน ParaView เพื่อ Keyframe ตำแหน่งกล้อง

### 2.3 Parameter Sweep (แอนิเมชันเปรียบเทียบ)
แสดงผลลัพธ์เมื่อเปลี่ยนค่าพาร์รามิเตอร์ (เช่น เพิ่มความเร็วลม, เปลี่ยนองศาปีก)
- **เหมาะสำหรับ**: Design optimization, Sensitivity analysis

---

## 3. เทคนิคใน ParaView Animation View

> [!NOTE] **📂 OpenFOAM Context: เวลาจริง vs. เฟรมจริง**
> ความเข้าใจที่ถูกต้องเรื่อง "เวลา" ใน OpenFOAM และ Animation:
> - **OpenFOAM Time (`startTime`, `endTime`)**: ถูกกำหนดใน `controlDict` ผ่าน keyword `startFrom` และ `stopAt`
> - **Time Step (`deltaT`)**: ถูกกำหนดใน `controlDict` (หรือ Adaptive time stepping)
> - **Write Interval**: ถูกกำหนดใน `controlDict` (เช่น `writeInterval 0.01;`) → **นี่คือจำนวน Time folders ที่ ParaView จะเห็น**
> - **Animation Frames**: เป็นเรื่องของ ParaView เท่านั้น (ไม่เกี่ยวกับ OpenFOAM)
>
> **ตัวอย่าง**: ถ้า `writeInterval` = 0.1s และ `endTime` = 10s → จะมี 100 Time directories → ถ้าต้องการ Animation 30fps ยาว 5 วินาที → ต้องใช้ 150 เฟรม → ParaView จะ Interpolate ระหว่าง 100 Time directories ให้ได้ 150 เฟรม

หน้าต่าง **Animation View** คือหัวใจของการควบคุม:

### 3.1 Mode: Sequence vs Real Time
- **Sequence**: กำหนดจำนวนเฟรมคงที่ (เช่น 300 เฟรม) ParaView จะคำนวณว่าแต่ละเฟรมต้องอยู่เวลาไหน (เหมาะสำหรับ Video Output ที่ต้องการ Frame Rate คงที่)
- **Real Time**: เล่นตามเวลาจริงของการจำลอง (ไม่แนะนำสำหรับ Export วิดีโอ เพราะเฟรมอาจกระตุก)

### 3.2 Keyframing Camera
เราสามารถเปลี่ยนมุมกล้องได้ในขณะที่เวลาเดินไป:
1.  ใน Animation View, เลือก **Camera** ในช่องแรก
2.  คลิก `+` เพื่อเพิ่ม Track
3.  Double click ที่แถบเวลาเพื่อเพิ่ม **Keyframe**
4.  ในแต่ละ Keyframe, เราสามารถหมุนกล้องไปมุมที่ต้องการแล้วกด "Use Current"

### 3.3 Temporal Interpolator
ถ้าเราเก็บผลลัพธ์ (Write Interval) ทุก 0.1 วินาที แต่อยากได้วิดีโอ 60fps ที่สมูท
- ใช้ Filter **Temporal Interpolator**
- มันจะสร้างข้อมูล "ระหว่างกลาง" (Linear Interpolation) ให้โดยอัตโนมัติ ทำให้วิดีโอไม่กระตุกแม้ข้อมูลจริงจะมีน้อย

---

## 4. การซ้อนทับข้อมูล (Data Overlay)

> [!NOTE] **📂 OpenFOAM Context: Function Objects สำหรับ Data Sampling**
> ก่อนจะมา Plot กราฟใน ParaView ต้องให้ OpenFOAM บันทึกข้อมูลที่สนใจก่อน โดยใช้ **Function Objects** ใน `system/controlDict`:
>
> **ตัวอย่าง 1: Probe ที่จุดเดียว**
> ```cpp
> // system/controlDict
> functions
> {
>     probePoint
>     {
>         type            probes;
>         functionObjectLibs ("libsampling.so");
>         outputControl   timeStep;
>         outputInterval  1;
>         probeLocations
>         (
>             (0.1 0.0 0.0)    // พิกัดจุดที่ต้องการวัด
>         );
>         fields          (p U k epsilon);
>         setFormat       csv;    // บันทึกเป็นไฟล์ .csv
>     }
> }
> ```
>
> **ตัวอย่าง 2: Surface Sampling (เช่น หน้า Section ตัด)**
> ```cpp
>     cuttingPlane
>     {
>         type            surfaces;
>         functionObjectLibs ("libsampling.so");
>         outputControl   outputTime;
>         surfaceFormat   vtk;
>         fields          (p U);
>         surfaces
>         {
>             zNormal
>             {
>                 type        cuttingPlane;
>                 plane       pointAndNormalDict;
>                 pointAndNormalDict
>                 {
>                     basePoint       (0 0 0);
>                     normalVector    (0 0 1);
>                 }
>                 interpolate true;
>             }
>         }
>     }
> ```
>
> **ผลลัพธ์**: จะถูกเก็บใน `postProcessing/probePoint/0/probePoint.csv` และ `postProcessing/cuttingPlane/0/surfaces/...` ซึ่งสามารถโหลดเข้า ParaView ได้โดยตรง

วิดีโอที่ดีควรมีกราฟยืนยันผล:

### 4.1 Plot Data Over Time
1.  เลือกจุด (Probe) หรือพื้นที่ที่สนใจ
2.  ใช้ Filter **Plot Selection Over Time**
3.  เมื่อเล่น Animation เส้นแนวตั้งในกราฟจะวิ่งแสดงเวลาปัจจุบัน

### 4.2 Programmable Filter for Annotation
ใช้ Python เพื่อเขียน Text ที่เปลี่ยนไปตามเวลา เช่น แสดงค่า Flow Rate แบบ Real-time บนหน้าจอ:

```python
# ใน Programmable Filter (Output type: vtkTable)
# Script:
import numpy as np
t = inputs[0].Information.Get(vtk.vtkDataObject.DATA_TIME_STEP())
output.RowData.append(t, "Time")
# ... คำนวณค่าอื่นๆ ...
```
แล้วใช้ **Text View** หรือ **Python Annotation** แสดงผล

---

## 5. การเข้ารหัสวิดีโอ (Video Encoding)

> [!NOTE] **📂 OpenFOAM Context: Batch Script สำหรับ Render Automation**
> สำหรับ Production Animation แนะนำให้ใช้ **ParaView in Batch Mode** ผ่าน Python script แทนการกดเอา:
>
> ```python
> # renderAnimation.py
> from paraview.simple import *
> import os
>
> # 1. Load OpenFOAM case
> reader = OpenFOAMReader(FileName="/path/to/case.foam")
> reader.MeshRegions = ["internalMesh", "patch_inlet"]
>
> # 2. Setup view
> renderView = GetActiveViewOrCreateRenderView()
> renderView.CameraPosition = [1, 1, 1]
>
> # 3. Create animation scene
> animationScene = GetAnimationScene()
> animationScene.AnimationTime = 0.0
> animationScene.EndTime = 10.0
> animationScene.NumberOfFrames = 300
>
> # 4. Save as PNG sequence
> writer = CreateAnimationWriter("frame_%04d.png", Magnification=2, FrameRate=30)
> animationScene.SaveAnimation()
> ```
>
> **Run ด้วย Command Line**:
> ```bash
> pvbatch --sym=/path/to/renderAnimation.py
> ```
>
> **ข้อดี**: สามารถ run บน HPC Cluster โดยไม่ต้องมี GUI และสามารถ Render หลาย View พร้อมกันได้

ParaView Export AVI ได้ แต่ไฟล์มักจะใหญ่และคุณภาพต่ำ แนะนำ Workflow นี้:

1.  **Export Image Sequence**: บันทึกเป็น PNG (`frame_0001.png`, `frame_0002.png`, ...)
    - ข้อดี: ไม่เสียคุณภาพ, ถ้าเรนเดอร์หลุดกลางทางก็ต่อได้
2.  **รวมด้วย FFmpeg**:

```bash
# คำสั่ง FFmpeg มาตรฐานสำหรับวิดีโอคุณภาพสูงขนาดเล็ก (H.264)
ffmpeg -framerate 30 -i frame_%04d.png \
       -c:v libx264 -preset slow -crf 18 \
       -pix_fmt yuv420p \
       output_video.mp4
```

- `-framerate 30`: ความเร็ว 30 เฟรมต่อวินาที
- `-crf 18`: คุณภาพ (ต่ำกว่า = ชัดกว่า, 18-23 คือค่าที่แนะนำ)
- `-pix_fmt yuv420p`: เพื่อให้เล่นได้บนทุก Player (สำคัญมาก! ถ้าไม่ใส่ บางโปรแกรมเปิดไม่ออกป)

---

## 6. กรณีศึกษา: การสร้าง "Fly-through" Animation

> [!NOTE] **📂 OpenFOAM Context: การสร้าง Streamlines สำหรับ Camera Path**
> ก่อนจะทำ Fly-through Animation ต้องสร้างเส้นทาง Camera Path จากข้อมูล OpenFOAM:
>
> **Option 1: ใช้ ParaView Streamlines**
> - Load OpenFOAM case
> - Filter → Streamline
> - Seed Type: Point Cloud (หรือ High Resolution Line Source)
> - Vector: U (velocity field)
> - สร้าง Streamline แล้ว Export เป็น .vtk หรือ .obj
>
> **Option 2: สร้าง Path จาก Geometry**
> ```python
> # ใน ParaView Python Shell
> from paraview.simple import *
>
> # สร้าง Spline จากจุดที่กำหนด
> spline = Spline(Source="Points")
> spline.Points = [0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0]  # (x,y,z) 4 จุด
>
> # ใช้เป็น Camera Path
> animationScene = GetAnimationScene()
> animationScene.Chaos = spline
> ```
>
> **เทคนิคพิเศษ**: ถ้าต้องการ Camera ตาม Streamlines ของ Flow จริง:
> ```python
> # ใช้ Pstreamlines แทน Streamlines ปกติ
> # เพื่อให้ได้เส้นทางที่ smooth และ follow flow ดีกว่า
> ```

สมมติเราจำลองอุโมงค์ลมในอาคาร เราอยากทำวิดีโอเหมือนโดรนบินผ่าน:

1.  **Prepare**: โหลด OpenFOAM Case, สร้าง Streamlines
2.  **Path**: สร้างเส้น Spline (Source > Spline) เพื่อใช้เป็นเส้นทางเดินกล้อง
3.  **Camera**: ใน Animation View เลือก Camera > **Follow Path** แล้วเลือก Spline ที่สร้าง
4.  **Target**: ตั้ง Camera Focal Point ให้มองไปข้างหน้าตามเส้นทาง (Look Ahead)
5.  **Render**: Export Animation เป็น PNG sequence

---

## 🧠 Concept Check

1.  **ถาม:** ทำไมการ Export เป็น "Image Sequence" (PNG) ถึงดีกว่าการ Export เป็นไฟล์วิดีโอ (.avi/.mp4) โดยตรงจาก ParaView?
    <details>
    <summary>เฉลย</summary>
    <b>ตอบ:</b> 
    1. **คุณภาพ**: PNG เป็น Lossless compression ภาพชัดที่สุด
    2. **ความปลอดภัย**: ถ้าคอมค้างหรือโปรแกรมหลุดตอนเฟรมที่ 99 จาก 100 เราก็ยังมี 99 รูปแรก แต่ถ้าเป็นวิดีโอไฟล์เดียว ไฟล์อาจเสียทั้งหมด
    3. **ความยืดหยุ่น**: เราสามารถเอารูปไปปรับ Frame rate, ใส่เพลงประกอบ หรือตัดต่อใหม่ทีหลังได้ง่ายกว่า
    </details>

2.  **ถาม:** Temporal Interpolator มีข้อจำกัดอะไรบ้าง?
    <details>
    <summary>เฉลย</summary>
    <b>ตอบ:</b> Temporal Interpolator ใช้ **Linear Interpolation** ระหว่าง Time steps ซึ่งถ้าการไหลมีการเปลี่ยนแปลงที่รวดเร็วมาก (เช่น High frequency fluctuation) ข้อมูลที่ Interpolate ออกมาอาจจะไม่ตรงกับความจริงทางฟิสิกส์ (Aliasing) หรือถ้า Mesh มีการเปลี่ยนแปลง (Dynamic Mesh) อาจจะทำให้ Topology ผิดพลาดได้
    </details>


---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md) — ภาพรวม Visualization
- **บทก่อนหน้า:** [03_Blender_Rendering.md](03_Blender_Rendering.md) — Blender Rendering
- **ParaView:** [01_ParaView_Visualization.md](01_ParaView_Visualization.md) — ParaView Visualization
