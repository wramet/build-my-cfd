# พื้นฐานการใช้ PyFoam (PyFoam Fundamentals)

PyFoam คือไลบรารี Python ที่ทรงพลังที่สุดสำหรับควบคุม OpenFOAM ในบทนี้เราจะเรียนรู้วิธีรัน Solver, เฝ้าดู Residuals, และจัดการ Case ด้วย Python

> **ลิงก์ที่เกี่ยวข้อง**:
> - ดู Environment Setup → [01_Python_Environment_Setup.md](./01_Python_Environment_Setup.md)
> - ดูภาพรวม → [00_Overview.md](./00_Overview.md)
> - ดู Data Analysis → [03_Data_Analysis_with_Pandas.md](./03_Data_Analysis_with_Pandas.md)

## 1. PyFoam คืออะไร?

PyFoam พัฒนาโดย **Bernhard F.W. Gschaider** ตั้งแต่ปี 2006 เป็นเครื่องมือที่ OpenFOAM community ใช้กันอย่างแพร่หลาย

**ความสามารถหลัก:**
- 🎮 ควบคุมการรัน Solver (แทนการรันใน Terminal)
- 📊 พล็อตกราฟ Residuals แบบ Real-time
- 📝 อ่านและแก้ไข Dictionary files (controlDict, fvSchemes ฯลฯ)
- 📁 Clone และจัดการ Case หลายๆ อัน
- 🔍 วิเคราะห์ Log files อัตโนมัติ

> [!TIP] **เปรียบเทียบ PyFoam (Analogy)**
> ให้คิดว่า **OpenFOAM** คือ **"รถยนต์"** ที่มีเครื่องยนต์ทรงพลัง
> **PyFoam** ก็คือ **"หน้าปัดดิจิทัลและระบบ Autopilot"** ที่ช่วยให้คุณควบคุมรถ ดูมาตรวัดต่างๆ (Residuals) และขับไปยังจุดหมาย (Convergence) ได้อย่างสบาย โดยไม่ต้องลงไปจูนเครื่องเองทุกครั้ง

## 2. การรัน Solver ด้วย PyFoam

### 2.1 `pyFoamPlotRunner.py` - เครื่องมือหลัก

**รูปแบบการใช้งาน:**
```bash
pyFoamPlotRunner.py <solver> -case <case_directory>
```

**ตัวอย่าง:**
```bash
# รัน simpleFoam พร้อมพล็อตกราฟ
pyFoamPlotRunner.py simpleFoam -case .

# รันแบบ Silent (ไม่แสดง output ทุก step)
pyFoamPlotRunner.py simpleFoam -case . --silent

# รันและกำหนดเวลาเริ่มต้น
pyFoamPlotRunner.py simpleFoam -case . --starttime=0
```

**สิ่งที่เกิดขึ้น:**
1. PyFoam เปิด Solver ขึ้นมา
2. อ่าน Residuals จาก Log file ทุกๆ ขั้นตอน
3. สร้างกราฟ Gnuplot แสดงความคืบหน้า Real-time
4. เมื่อ Solver จบ กราฟจะถูกบันทึกใน `<case>/PyFoamRunner/`

### 2.2 การเขียน Python Script รัน Solver

```python
from PyFoam.Execution.BasicRunner import BasicRunner

# รัน simpleFoam
runner = BasicRunner(
    argv=["simpleFoam", "-case", "."],
    silent=False  # แสดง output ใน Terminal
)

# เริ่มรัน (Blocking)
runner.start()

# เช็คว่าจบหรือยัง
if runner.runnerOK:
    print("Simulation finished successfully!")
else:
    print("Simulation failed!")

# อ่าน CPU time
print(f"CPU Time: {runner.runner.readCPUTime()} seconds")
```

## 3. การเฝ้าดูและวิเคราะห์ Log Files

### 3.1 `pyFoamPlotWatcher.py` - เฝ้าดู Log ที่รันอยู่แล้ว

ถ้า Solver รันอยู่แล้ว (เช่น รันใน HPC) และอยากดูกราฟ:

```bash
# เปิด Terminal ใหม่ แล้วรัน
pyFoamPlotWatcher.py <log_file>

# ตัวอย่าง
pyFoamPlotWatcher.py log.simpleFoam
```

### 3.2 อ่าน Log files ด้วย Python

```python
from PyFoam.LogAnalysis.BoundingLogAnalyzer import BoundingLogAnalyzer

# วิเคราะห์ Log file
log = BoundingLogAnalyzer()
log.setFileName("log.simpleFoam")

# อ่านข้อมูลทั้งหมด
log.analyze()

# ดู Residuals สุดท้าย
print("Final residuals:")
for var, value in log.time[-1].items():
    print(f"  {var}: {value}")
```

**PyFoam Workflow:**
```mermaid
graph LR
    Start[1. Prepare OpenFOAM Case] --> Choice{How to run?}

    Choice -->|Terminal only| T[Run simpleFoam<br/>No plots]
    Choice -->|With Plots| P[pyFoamPlotRunner.py<br/>Real-time graphs]
    Choice -->|Python Script| S[BasicRunner API<br/>Full control]

    P --> Monitor1[PyFoamPlotWatcher<br/>Monitor HPC jobs]
    S --> Monitor2[Custom Logging<br/>Automation]

    Monitor1 --> Output[Output:<br/>Log file + Gnuplot graphs]
    Monitor2 --> Output
    T --> Output

    style Start fill:#e3f2fd
    style P fill:#fff3e0
    style S fill:#ffe0b2
    style Monitor1 fill:#c8e6c9
    style Monitor2 fill:#b2dfdb
    style Output fill:#4CAF50
```

## 4. การอ่านและแก้ไข Dictionary Files

### 4.1 อ่านค่าจาก controlDict

```python
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile

# อ่าน controlDict
control = ParsedParameterFile("system/controlDict")

# แสดงค่า
print(f"Start Time: {control['startTime']}")
print(f"End Time: {control['endTime']}")
print(f"Write Interval: {control['writeInterval']}")
```

### 4.2 แก้ไขค่าใน Dictionary

```python
# อ่านและแก้ไข
control = ParsedParameterFile("system/controlDict")

# เปลี่ยนค่า
control['endTime'] = 1000
control['writeInterval'] = 100

# เพิ่ม function objects
if 'functions' not in control:
    control['functions'] = {}

control['functions']['myForces'] = {
    'type': 'forces',
    'libs': ['"libforces.so"'],
    'writeControl': 'timeStep',
    'writeInterval': 1,
    'patches': ['"wall"']
}

# บันทึก
control.writeFile()
```

### 4.3 แก้ไข Boundary Conditions

```python
# อ่าน 0/U
u_file = ParsedParameterFile("0/U")

# เปลี่ยนค่าความเร็วที่ Inlet
u_file['boundaryField']['inlet']['type'] = 'fixedValue'
u_file['boundaryField']['inlet']['value'] = 'uniform (10 0 0)'

# บันทึก
u_file.writeFile()
```

## 5. การ Clone และจัดการ Cases

### 5.1 Clone Cases

```python
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory

# Clone case
base = SolutionDirectory("base_case")
new_case = base.clone("new_case")

# หรือใช้คำสั่ง shell
import os
os.system("pyFoamCloneCase.py base_case new_case")
```

### 5.2 Batch Operations

```python
import os
from PyFoam.Execution.BasicRunner import BasicRunner

cases = ["case_angle_0", "case_angle_2", "case_angle_4"]

for case in cases:
    print(f"Running {case}...")

    runner = BasicRunner(
        argv=["simpleFoam", "-case", case],
        silent=True
    )

    runner.start()

    if runner.runnerOK:
        print(f"✅ {case} finished!")
    else:
        print(f"❌ {case} failed!")
```

## 6. เคล็ดลับการใช้ PyFoam

### Tip 1: รันหลาย Solver ต่อเนื่อง

```python
# รัน blockMesh → snappyHexMesh → simpleFoam
solvers = [
    ["blockMesh", "-case", "."],
    ["snappyHexMesh", "-case", "."],
    ["simpleFoam", "-case", "."]
]

for solver in solvers:
    runner = BasicRunner(argv=solver, silent=True)
    runner.start()

    if not runner.runnerOK:
        print(f"Solver {solver[0]} failed!")
        break
```

### Tip 2: Auto-restart ถ้า Diverge

```python
import time

max_restarts = 3
for attempt in range(max_restarts):
    runner = BasicRunner(argv=["simpleFoam", "-case", "."])
    runner.start()

    if runner.runnerOK:
        print("Success!")
        break
    else:
        print(f"Attempt {attempt+1} failed. Restarting...")
        time.sleep(5)
```

### Tip 3: สร้าง Custom Plotting

```python
from PyFoam.Execution.AnnotatedCommonPlotRunner import AnnotatedCommonPlotRunner

runner = AnnotatedCommonPlotRunner(
    argv=["simpleFoam", "-case", "."],
    customRegexp=[  # Custom plot rules
        ("force_coefficient",  # Plot name
         r"Cd = %f%",  # Regex pattern
         {"type": "dynamic", "theTitle": "Drag Coefficient"}),
    ]
)

runner.start()
```

---

## 🧠 ตรวจสอบความเข้าใจ (Concept Check)

### แบบฝึกหัดระดับง่าย (Easy)
1. **True/False**: `pyFoamPlotRunner.py` สร้างกราฟ Real-time ในระหว่างรัน Solver
   <details>
   <summary>คำตอบ</summary>
   ✅ จริง - PyFoam อ่าน Log files และพล็อตกราฟ Gnuplot แบบ Real-time
   </details>

2. **เลือกตอบ**: Class ไหนใช้อ่าน Dictionary files?
   - a) BasicRunner
   - b) ParsedParameterFile
   - c) BoundingLogAnalyzer
   - d) SolutionDirectory
   <details>
   <summary>คำตอบ</summary>
   ✅ b) ParsedParameterFile - ใช้อ่านและแก้ไข controlDict, 0/U ฯลฯ
   </details>

### แบบฝึกหัดระดับปานกลาง (Medium)
3. **อธิบาย**: แตกต่างระหว่าง `pyFoamPlotRunner.py` และ `pyFoamPlotWatcher.py` คืออะไร?
   <details>
   <summary>คำตอบ</summary>
   - pyFoamPlotRunner.py: รัน Solver ใหม่พร้อมสร้างกราฟ
   - pyFoamPlotWatcher.py: เฝ้าดู Solver ที่รันอยู่แล้ว (เช่น HPC) แล้วสร้างกราฟ
   </details>

4. **เขียนโค้ด**: จงเขียน Python script เพื่อ:
   - อ่าน `system/controlDict`
   - เปลี่ยน `endTime` เป็น `2000`
   - เพิ่ม `writeInterval` เป็น `50`
   - บันทึกไฟล์
   <details>
   <summary>คำตอบ</summary>
   ```python
   from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile

   control = ParsedParameterFile("system/controlDict")
   control['endTime'] = 2000
   control['writeInterval'] = 50
   control.writeFile()
   print("controlDict updated!")
   ```
   </details>

### แบบฝึกหัดระดับสูง (Hard)
5. **Hands-on**: ใช้ `pyFoamPlotRunner.py` รัน Tutorial case จริง และตรวจสอบกราฟที่สร้างใน `PyFoamRunner/`

6. **วิเคราะห์**: เปรียบเทียบวิธีรัน Solver 3 แบบ:
   - รันใน Terminal (simpleFoam)
   - ใช้ pyFoamPlotRunner.py
   - ใช้ Python BasicRunner
   ในแง่ของความยืดหยุ่นในการควบคุม และความง่ายในการ Automation
