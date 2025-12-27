# 🎥 เทคนิคการสร้างแอนิเมชันขั้นสูง (Advanced Animation Techniques)

**วัตถุประสงค์การเรียนรู้ (Learning Objectives)**: สร้างวิดีโอผลลัพธ์ CFD ที่ลื่นไหล สื่อความหมาย และดึงดูดความสนใจ โดยเน้นเทคนิคการเล่าเรื่องผ่านภาพเคลื่อนไหว
**ระดับความยาก**: ปานกลาง-สูง (Intermediate-Advanced)

---

## 1. มากกว่าแค่ภาพเคลื่อนไหว (Beyond Simple Playback)

การกดปุ่ม "Play" ใน ParaView เป็นแค่จุดเริ่มต้น แอนิเมชันที่ดีต้องมีการวางแผน:
- **มุมกล้อง (Camera Work)**: กล้องควรเคลื่อนที่เพื่อแสดงจุดที่น่าสนใจ ไม่ใช่แช่นิ่งๆ
- **จังหวะ (Pacing)**: ส่วนที่น่าเบื่อควรเร่งความเร็ว ส่วนที่สำคัญควรสโลว์โมชั่น
- **ข้อมูลประกอบ (Annotation)**: กราฟวิ่งตามเวลา (Dynamic Graphs) ช่วยยืนยันสิ่งที่เห็นในภาพ

---

## 2. ประเภทของแอนิเมชัน CFD

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

สมมติเราจำลองอุโมงค์ลมในอาคาร เราอยากทำวิดีโอเหมือนโดรนบินผ่าน:

1.  **Prepare**: โหลด OpenFOAM Case, สร้าง Streamlines
2.  **Path**: สร้างเส้น Spline (Source > Spline) เพื่อใช้เป็นเส้นทางเดินกล้อง
3.  **Camera**: ใน Animation View เลือก Camera > **Follow Path** แล้วเลือก Spline ที่สร้าง
4.  **Target**: ตั้ง Camera Focal Point ให้มองไปข้างหน้าตามเส้นทาง (Look Ahead)
5.  **Render**: Export Animation เป็น PNG sequence

---

## 🧠 ตรวจสอบความเข้าใจ (Concept Check)

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
