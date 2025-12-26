# การทำ Parametric Study อัตโนมัติ (Automated Parametric Study)

Parametric Study คือการรัน Simulation หลายๆ ครั้งเพื่อศึกษาผลของพารามิเตอร์ที่เปลี่ยนไป ในบทนี้เราจะเรียนรู้วิธีเขียน Python Script รันงานแทนเราอัตโนมัติ

> **ลิงก์ที่เกี่ยวข้อง**:
> - ดู PyFoam Fundamentals → [02_PyFoam_Fundamentals.md](./02_PyFoam_Fundamentals.md)
> - ดู Data Analysis → [03_Data_Analysis_with_Pandas.md](./03_Data_Analysis_with_Pandas.md)
> - ดู HPC Integration → [../03_HPC_AND_CLOUD/04_HPC_Integration.md](../03_HPC_AND_CLOUD/04_HPC_Integration.md)

## 1. Parametric Study คืออะไร?

**นิยาม**: การเปลี่ยนค่าพารามิเตอร์ (เช่น ความเร็ว, มุม, ขนาด) แล้วรัน Simulation หลายๆ ครั้งเพื่อดูผลกระทบ

**ตัวอย่าง Use Cases:**
- 🎯 หา Angle of Attack ที่ให้ Lift สูงสุด
- 📏 ทดสอบ Mesh Independence (เปลี่ยนขนาด Cell 3-4 ขนาด)
- 🌪️ ปรับค่า Turbulence Model Constants
- 📐 ออกแบบรูปทรงที่เหมาะสมที่สุด (Optimization)

- 📊 สรุปผลได้รวดเร็ว
- 💾 จัดการข้อมูลได้เป็นระเบียบ

> [!TIP] **เปรียบเทียบ Parametric Study (Analogy)**
> เปรียบเหมือน **"เชฟที่กำลังคิดสูตรอาหารใหม่"**
> เขาต้องทดลองเปลี่ยนส่วนผสมทีละอย่าง (Parameters) เช่น ปริมาณเกลือ (0g, 1g, 2g) หรือน้ำตาล แล้วชิมรสชาติ (Result) เพื่อหาสูตรที่ดีที่สุด (Optimization) แต่แทนที่จะทำทีละจาน ระบบอัตโนมัติช่วยให้เขาสั่งหุ่นยนต์ทำอาหาร 100 จานพร้อมกันได้ในครั้งเดียว

## 2. การวางแผน Parametric Study

### 2.1 กำหนดเป้าหมายชัดเจน

**❌ แย่:** "อยากรันหลายๆ เคสดู่"
**✅ ดี:** "อยากรู้ว่า Angle 0-10 องศา ค่าไหนให้ Cl/Cd สูงสุด"

### 2.2 เลือกพารามิเตอร์ที่เปลี่ยน

```python
# ตัวอย่าง 1: Angle of Attack Study
angles = [0, 2, 4, 6, 8, 10]  # 6 เคส

# ตัวอย่าง 2: Velocity Study
velocities = [10, 15, 20, 25, 30]  # 5 เคส

# ตัวอย่าง 3: Mesh Independence
refinements = [1, 2, 3, 4]  # 4 เคส (Level 1-4)
```

### 2.3 ประเมินเวลาและทรัพยากร

```
จำนวนเคส × เวลา/เคส = เวลาทั้งหมด

ตัวอย่าง:
6 เคส × 2 ชั่วโมง = 12 ชั่วโมง (รันคืนหนึ่ง)
```

**Parametric Study Workflow:**
```mermaid
graph TB
    Start[1. Define Parameters<br/>angles = [0,2,4,6,8,10]] --> Plan[2. Plan Study<br/>Estimate time & resources]
    Plan --> Prepare[3. Prepare Base Case<br/>Clean & tested]
    Prepare --> Script[4. Write Script<br/>Automate everything]
    Script --> Test[5. Test Run<br/>1-2 cases only]
    Test --> FullRun[6. Full Run<br/>Overnight/HPC]
    FullRun --> Analyze[7. Analyze Results<br/>Auto-summary]
    Analyze --> Report[8. Generate Report<br/>Plots & tables]

    style Start fill:#e3f2fd
    style Plan fill:#fff3e0
    style Prepare fill:#ffe0b2
    style Script fill:#ffcc80
    style Test fill:#ffecb3
    style FullRun fill:#c8e6c9
    style Analyze fill:#b2dfdb
    style Report fill:#4CAF50
```

## 3. การเตรียม Base Case

**ห้ามรัน Script กับ Base Case ที่ยังไม่ได้ทดสอบ!**

### Checklist:
- ✅ รันแบบ Manual 1 ครั้ง จนผ่าน
- ✅ Function Objects พร้อม (forces, forceCoeffs)
- ✅ Mesh Quality OK
- ✅ Converged ภายในเวลาที่กำหนด

## 4. การเขียน Script รัน Parametric Study

### 4.1 Script รัน Sequential (ง่ายที่สุด)

```python
#!/usr/bin/env python3
"""
Automated Parametric Study: Angle of Attack
Author: Your Name
Date: 2025-12-26
"""

import os
import shutil
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
from PyFoam.Execution.BasicRunner import BasicRunner
import pandas as pd
import numpy as np

# ========================================
# 1. CONFIGURATION
# ========================================
BASE_CASE = "airfoil_base"
ANGLES = [0, 2, 4, 6, 8, 10]
SOLVER = "simpleFoam"

# ========================================
# 2. FUNCTION: สร้าง Case
# ========================================
def create_case(base_path, new_path, angle):
    """Clone case และแก้ไข Boundary Condition"""

    # Clone
    if os.path.exists(new_path):
        shutil.rmtree(new_path)
    shutil.copytree(base_path, new_path)

    # แก้ไข 0/U (คำนวณ Ux, Uy จากมุม)
    u_file = ParsedParameterFile(f"{new_path}/0/U")

    # แปลง angle เป็น radians
    alpha = np.radians(angle)
    u_mag = 10.0  # m/s

    u_x = u_mag * np.cos(alpha)
    u_y = u_mag * np.sin(alpha)

    # กำหนดค่า Inlet
    u_file['boundaryField']['inlet']['type'] = 'fixedValue'
    u_file['boundaryField']['inlet']['value'] = f'uniform ({u_x} {u_y} 0)'

    u_file.writeFile()

    print(f"✅ Created case: {new_path} (angle={angle}°)")
    return new_path

# ========================================
# 3. FUNCTION: รัน Solver
# ========================================
def run_solver(case_path):
    """รัน Solver และ return success/fail"""

    runner = BasicRunner(
        argv=[SOLVER, "-case", case_path],
        silent=True  # ไม่แสดง output
    )

    runner.start()

    if runner.runnerOK:
        print(f"✅ {case_path}: Simulation finished!")
        return True
    else:
        print(f"❌ {case_path}: Simulation failed!")
        return False

# ========================================
# 4. FUNCTION: สกัดผลลัพธ์
# ========================================
def extract_results(case_path, angle):
    """อ่าน Cd, Cl จาก forceCoeffs.dat"""

    file_path = f"{case_path}/postProcessing/forceCoeffs/0/forceCoeffs.dat"

    if not os.path.exists(file_path):
        print(f"⚠️  {case_path}: No results file found")
        return None

    df = pd.read_csv(
        file_path,
        delim_whitespace=True,
        comment='#',
        names=['t', 'Cd', 'Cl', 'Cm']
    )

    # ค่าเฉลี่ย 50 steps สุดท้าย
    last_50 = df.tail(50)

    result = {
        'angle': angle,
        'Cd': last_50['Cd'].mean(),
        'Cl': last_50['Cl'].mean(),
        'Cl_Cd_ratio': last_50['Cl'].mean() / last_50['Cd'].mean()
    }

    print(f"📊 Angle {angle}°: Cd={result['Cd']:.4f}, Cl={result['Cl']:.4f}")
    return result

# ========================================
# 5. MAIN LOOP
# ========================================
def main():
    print("="*60)
    print("PARAMETRIC STUDY: ANGLE OF ATTACK")
    print("="*60)

    all_results = []

    for angle in ANGLES:
        case_name = f"airfoil_angle_{angle}"

        # สร้าง case
        create_case(BASE_CASE, case_name, angle)

        # รัน solver
        success = run_solver(case_name)

        if success:
            # สกัดผล
            result = extract_results(case_name, angle)
            if result:
                all_results.append(result)

    # ========================================
    # 6. SUMMARIZE RESULTS
    # ========================================
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    df_results = pd.DataFrame(all_results)
    print(df_results)

    # หาค่าที่ดีที่สุด
    best_idx = df_results['Cl_Cd_ratio'].idxmax()
    best_angle = df_results.loc[best_idx, 'angle']
    best_ratio = df_results.loc[best_idx, 'Cl_Cd_ratio']

    print(f"\n🏆 BEST ANGLE: {best_angle}°")
    print(f"   Cl/Cd Ratio: {best_ratio:.2f}")

    # บันทึก
    df_results.to_csv('parametric_study_results.csv', index=False)
    print("\n✅ Results saved to parametric_study_results.csv")

if __name__ == "__main__":
    main()
```

### 4.2 การเพิ่ม Plotting อัตโนมัติ

```python
import matplotlib.pyplot as plt

def plot_results(df_results):
    """พล็อตกราฟสรุปผล"""

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # Cd vs Angle
    axes[0, 0].plot(df_results['angle'], df_results['Cd'], 'ro-')
    axes[0, 0].set_xlabel('Angle (deg)')
    axes[0, 0].set_ylabel('Cd')
    axes[0, 0].set_title('Drag Coefficient')
    axes[0, 0].grid(True)

    # Cl vs Angle
    axes[0, 1].plot(df_results['angle'], df_results['Cl'], 'bo-')
    axes[0, 1].set_xlabel('Angle (deg)')
    axes[0, 1].set_ylabel('Cl')
    axes[0, 1].set_title('Lift Coefficient')
    axes[0, 1].grid(True)

    # Cl/Cd vs Angle
    axes[1, 0].plot(df_results['angle'], df_results['Cl_Cd_ratio'], 'go-')
    axes[1, 0].set_xlabel('Angle (deg)')
    axes[1, 0].set_ylabel('Cl/Cd')
    axes[1, 0].set_title('Aerodynamic Efficiency')
    axes[1, 0].grid(True)

    # Polar Plot
    axes[1, 1].plot(df_results['Cd'], df_results['Cl'], 'mo-')
    axes[1, 1].set_xlabel('Cd')
    axes[1, 1].set_ylabel('Cl')
    axes[1, 1].set_title('Polar Plot')
    axes[1, 1].grid(True)

    # ใส่ labels
    for _, row in df_results.iterrows():
        axes[1, 1].annotate(f"{row['angle']}°",
                            (row['Cd'], row['Cl']),
                            textcoords="offset points", xytext=(5,5), ha='left')

    plt.tight_layout()
    plt.savefig('parametric_study_plots.png', dpi=300)
    print("✅ Plots saved to parametric_study_plots.png")
```

## 5. การรันแบบ Parallel (HPC)

ถ้ามี HPC Cluster สามารถรันหลายเคสพร้อมกัน:

### 5.1 ใช้ GNU Parallel

```bash
# สร้าง script รัน 1 เคส
cat > run_one_case.sh << 'EOF'
#!/bin/bash
angle=$1
python3 parametric_single.py --angle $angle
EOF

chmod +x run_one_case.sh

# รัน 6 เคสพร้อมกัน
seq 0 2 10 | parallel -j 6 ./run_one_case.sh {}
```

### 5.2 ใช้ Python multiprocessing

```python
from multiprocessing import Pool
import os

def run_single_case(angle):
    """ฟังก์ชันรัน 1 เคส (สำหรับ parallel)"""
    case_name = f"airfoil_angle_{angle}"
    create_case(BASE_CASE, case_name, angle)
    run_solver(case_name)
    result = extract_results(case_name, angle)
    return result

if __name__ == "__main__":
    # รัน parallel (6 cores)
    with Pool(processes=6) as pool:
        all_results = pool.map(run_single_case, ANGLES)

    df_results = pd.DataFrame(all_results)
    plot_results(df_results)
```

## 6. เคล็ดลับการ Parametric Study

### Tip 1: ใช้ Function Objects อย่างถูกต้อง

```cpp
// system/controlDict
functions
{
    #includeFunc forceCoeffs

    forceCoeffs
    {
        type        forceCoeffs;
        libs        ("libforces.so");
        writeControl timeStep;
        writeInterval 1;

        rho         rhoInf;
        rhoInf      1.225;
        magUInf     10;

        // สำคัญมาก: กำหนด direction ให้ถูกต้อง
        liftDir     (0 1 0);  // ตั้ง
        dragDir     (1 0 0);  // นอน
        pitchAxis   (0 0 1);

        patches     ("airfoil");
    }
}
```

### Tip 2: บันทึกทุกอย่าง

```python
import logging

# ตั้งค่า logging
logging.basicConfig(
    filename='parametric_study.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logging.info(f"Starting parametric study with angles: {ANGLES}")
logging.info(f"Base case: {BASE_CASE}")

# ใน loop
logging.info(f"Created case {case_name}")
logging.info(f"Simulation finished: {success}")

# เมื่อ error
try:
    result = extract_results(case_name, angle)
except Exception as e:
    logging.error(f"Failed to extract results for angle {angle}: {e}")
```

### Tip 3: Resume จากจุดที่หยุด

```python
# เช็คว่ามีเคสไหนเสร็จแล้วบ้าง
completed_cases = []
for angle in ANGLES:
    case_name = f"airfoil_angle_{angle}"
    if os.path.exists(f"{case_name}/postProcessing/forceCoeffs/0/forceCoeffs.dat"):
        completed_cases.append(angle)

# รันเฉพาะที่ยังไม่เสร็จ
remaining_angles = [a for a in ANGLES if a not in completed_cases]

print(f"✅ Completed: {completed_cases}")
print(f"⏳ Remaining: {remaining_angles}")
```

---

## 🧠 ตรวจสอบความเข้าใจ (Concept Check)

### แบบฝึกหัดระดับง่าย (Easy)
1. **True/False**: Parametric Study ควรเริ่มด้วยการรัน Script ทันทีโดยไม่ต้องทดสอบ Base Case
   <details>
   <summary>คำตอบ</summary>
   ❌ เท็จ - ต้องทดสอบ Base Case ให้แน่ใจว่าผ่านก่อน ไม่งั้นจะเสียเวลา
   </details>

2. **เลือกตอบ**: ถ้ารัน 6 เคส แต่ละเคสใช้เวลา 2 ชั่วโมง รัน Sequential ใช้เวลาทั้งหมดเท่าไหร่?
   - a) 2 ชั่วโมง
   - b) 6 ชั่วโมง
   - c) 12 ชั่วโมง
   - d) 24 ชั่วโมง
   <details>
   <summary>คำตอบ</summary>
   ✅ c) 12 ชั่วโมง - 6 × 2 = 12 (ถ้ารัน parallel จะเร็วกว่า)
   </details>

### แบบฝึกหัดระดับปานกลาง (Medium)
3. **อธิบาย**: ข้อดีของการใช้ Logging ใน Parametric Study คืออะไร?
   <details>
   <summary>คำตอบ</summary>
   - ติดตามความคืบหน้าได้แม้จะรัน Background
   - ทราบว่าเคสไหนผิดพลาดและสาเหตุ
   - มีบันทึกสำหรับ Audit และ Reproducibility
   </details>

4. **เขียนโค้ด**: จงเขียน Python loop สำหรับสร้าง 3 cases พร้อมกันโดยไม่ต้องรัน Solver
   <details>
   <summary>คำตอบ</summary>
   ```python
   import os
   import shutil

   base = "airfoil_base"
   velocities = [10, 15, 20]

   for v in velocities:
       case_name = f"velocity_{v}"
       if os.path.exists(case_name):
           shutil.rmtree(case_name)
       shutil.copytree(base, case_name)
       print(f"✅ Created {case_name}")
   ```
   </details>

### แบบฝึกหัดระดับสูง (Hard)
5. **Hands-on**: ใช้ Script จริงรัน Parametric Study 3 เคส (เช่น Angle 0, 5, 10 องศา) และสรุปผล

6. **วิเคราะห์**: เปรียบเทียบกลยุทธ์รัน Parametric Study:
   - Sequential (1 เค้วต่อเนื่อง)
   - Parallel (6 เคสพร้อมกันบน HPC)
   ในแง่ของ:
   - เวลารันทั้งหมด (Total walltime)
   - ประสิทธิภาพการใช้ CPU
   - ความยากในการ setup และ Debug
