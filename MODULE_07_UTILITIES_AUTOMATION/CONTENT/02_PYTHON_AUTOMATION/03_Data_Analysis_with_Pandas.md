# การวิเคราะห์ข้อมูล CFD ด้วย Pandas (Data Analysis with Pandas)

หลังจากรัน Simulation เสร็จ ขั้นตอนต่อไปคือการวิเคราะห์ผลลัพธ์ Pandas เป็นเครื่องมือที่ทรงพลังที่สุดสำหรับจัดการและวิเคราะห์ข้อมูล CFD

> **ลิงก์ที่เกี่ยวข้อง**:
> - ดู PyFoam Fundamentals → [02_PyFoam_Fundamentals.md](./02_PyFoam_Fundamentals.md)
> - ดู Python Plotting → [../04_ADVANCED_VISUALIZATION/02_Python_Plotting.md](../04_ADVANCED_VISUALIZATION/02_Python_Plotting.md)
> - ดูภาพรวม → [00_Overview.md](./00_Overview.md)

## 1. Pandas คืออะไรสำหรับ CFD?

**Pandas** คือไลบรารี Python สำหรับจัดการข้อมูลแบบ Tabular (ตาราง) ซึ่ง OpenFOAM output ส่วนใหญ่อยู่ในรูปแบบนี้

- Log files → Residuals, execution time

> [!TIP] **เปรียบเทียบการวิเคราะห์ข้อมูล (Analogy)**
> ให้คิดว่า **Raw Data** จาก OpenFOAM คือ **"แร่ดิบ"** ที่เพิ่งขุดขึ้นมาจากเหมือง (เต็มไปด้วยหินและดิน)
> **Pandas** คือ **"โรงงานแปรรูป"** ที่มีเครื่องจักรทันสมัย ช่วยคัดแยก ล้าง และสกัดเอา **"ทองคำบริสุทธิ์"** (Insight/Graph) ออกมาได้อย่างรวดเร็วและแม่นยำ

**Data Analysis Workflow:**
```mermaid
graph LR
    Raw[OpenFOAM Output<br/>.dat, .csv, log] --> Read[Pandas read_<br/>read_csv read_table]
    Read --> Clean[Clean Data<br/>Drop NaN, Rename cols]
    Clean --> Analyze[Analyze<br/>Mean, Std, Min, Max]
    Analyze --> Plot[Visualize<br/>Matplotlib, Seaborn]
    Plot --> Export[Export<br/>CSV, Excel, Report]

    style Raw fill:#e3f2fd
    style Read fill:#fff3e0
    style Clean fill:#ffe0b2
    style Analyze fill:#ffcc80
    style Plot fill:#c8e6c9
    style Export fill:#4CAF50
```

## 2. การอ่านข้อมูลจาก OpenFOAM

### 2.1 อ่านไฟล์ forces.dat

```python
import pandas as pd
import numpy as np

# อ่านไฟล์
forces = pd.read_csv(
    'postProcessing/forces/0/forces.dat',
    delim_whitespace=True,  # แยกด้วยช่องว่าง
    comment='#',              # ข้าม comment lines
    names=['Time', 'Fx_p', 'Fy_p', 'Fz_p',  # Pressure force
           'Fx_v', 'Fy_v', 'Fz_v',          # Viscous force
           'Mx', 'My', 'Mz']                 # Moments
)

print(forces.head())
```

**Output:**
```
   Time  Fx_p   Fy_p  Fz_p  Fx_v   Fy_v  Fz_v    Mx    My    Mz
0   0.1   1.2   -0.5   0.0   0.01  -0.02  0.00  0.05  0.10  0.00
1   0.2   1.3   -0.6   0.0   0.01  -0.02  0.00  0.06  0.11  0.00
```

### 2.2 อ่านไฟล์ probes.csv

```python
probes = pd.read_csv(
    'postProcessing/probes/0/probes.csv',
    skiprows=1  # ข้าม header ซ้ำ
)

print(probes.head())
```

### 2.3 อ่าน Log file (ขั้นสูง)

```python
# ดึง Residuals จาก log.simpleFoam
import re

residuals = []
with open('log.simpleFoam', 'r') as f:
    for line in f:
        if 'Time = ' in line:
            time = float(line.split('=')[1])
        if 'Ux' in line and 'final residual' in line:
            values = re.findall(r'[\d.]+', line)
            residuals.append({
                'Time': time,
                'Ux': float(values[0]),
                'p': float(values[1])
            })

df_residuals = pd.DataFrame(residuals)
```

## 3. การจัดการและทำความสะอาดข้อมูล

### 3.1 การตั้งชื่อ Columns ใหม่

```python
# ตั้งชื่อสั้นๆ ง่ายต่อการเขียน
forces.columns = ['t', 'fx_p', 'fy_p', 'fz_p',
                  'fx_v', 'fy_v', 'fz_v', 'mx', 'my', 'mz']
```

### 3.2 สร้าง Columns ใหม่

```python
# รวม Pressure + Viscous force
forces['fx_total'] = forces['fx_p'] + forces['fx_v']
forces['fy_total'] = forces['fy_p'] + forces['fy_v']

# คำนวณ Drag Coefficient (เบื้องต้น)
A_ref = 2.0  # m^2
rho = 1.225  # kg/m^3
U_inf = 20   # m/s
q_dyn = 0.5 * rho * U_inf**2

forces['Cd'] = forces['fx_total'] / (q_dyn * A_ref)

print(forces[['t', 'fx_total', 'Cd']].head())
```

### 3.3 ลบข้อมูลที่ไม่ต้องการ

```python
# ลบแถวที่ Cd = NaN หรือ Inf
forces_clean = forces[~forces['Cd'].isin([np.nan, np.inf])]

# ลบข้อมูลช่วง Start-up (เช่น t < 1)
forces_steady = forces_clean[forces_clean['t'] > 1.0]
```

## 4. การวิเคราะห์เชิงสถิติ

### 4.1 ค่าสถิติพื้นฐาน

```python
# ค่าเฉลี่ยช่วง 100 iterations สุดท้าย
last_100 = forces_steady.tail(100)

mean_fx = last_100['fx_total'].mean()
std_fx = last_100['fx_total'].std()
min_fx = last_100['fx_total'].min()
max_fx = last_100['fx_total'].max()

print(f"Mean Fx: {mean_fx:.2f} ± {std_fx:.2f} N")
print(f"Range: [{min_fx:.2f}, {max_fx:.2f}] N")
```

**Output:**
```
Mean Fx: 12.45 ± 0.23 N
Range: [12.01, 13.02] N
```

### 4.2 ตรวจสอบ Convergence

```python
# ตรวจสอบว่าค่า Cd ลู่เข้าหรือยัง (Rolling mean)
forces['Cd_rolling'] = forces['Cd'].rolling(window=50).mean()

# คำนวณ % Change ระหว่างช่วง
first_half = forces['Cd'].iloc[:len(forces)//2].mean()
second_half = forces['Cd'].iloc[len(forces)//2:].mean()
percent_change = abs((second_half - first_half) / first_half * 100)

print(f"Percent change: {percent_change:.2f}%")

if percent_change < 1.0:
    print("✅ Converged!")
else:
    print("❌ Not converged yet")
```

### 4.3 การเปรียบเทียบ Cases หลายๆ อัน

```python
# อ่านข้อมูล 3 cases
cases = {
    'angle_0': 'case_angle_0/postProcessing/forces/0/forces.dat',
    'angle_5': 'case_angle_5/postProcessing/forces/0/forces.dat',
    'angle_10': 'case_angle_10/postProcessing/forces/0/forces.dat'
}

results = []
for name, path in cases.items():
    df = pd.read_csv(path, delim_whitespace=True, comment='#',
                      names=['t', 'fx_p', 'fy_p', 'fz_p',
                             'fx_v', 'fy_v', 'fz_v', 'mx', 'my', 'mz'])
    df['fx_total'] = df['fx_p'] + df['fx_v']
    df['case'] = name
    results.append(df)

# รวมทุก case
all_data = pd.concat(results, ignore_index=True)

# คำนวณค่าเฉลี่ยแต่ละ case
summary = all_data.groupby('case')['fx_total'].agg(['mean', 'std'])
print(summary)
```

**Output:**
```
          mean       std
case
angle_0   10.2  0.15
angle_5   12.8  0.22
angle_10  15.3  0.31
```

## 5. การพล็อตกราฟด้วย Matplotlib

### 5.1 พล็อต Drag Coefficient ตามเวลา

```python
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))
plt.plot(forces['t'], forces['Cd'], label='Cd', linewidth=2)
plt.plot(forces['t'], forces['Cd_rolling'], label='Cd (rolling mean)',
         linewidth=2, linestyle='--')
plt.xlabel('Time (s)')
plt.ylabel('Drag Coefficient')
plt.title('Drag Coefficient vs Time')
plt.legend()
plt.grid(True)
plt.savefig('Cd_vs_time.png', dpi=300)
plt.show()
```

### 5.2 พล็อต Forces หลายค่าพร้อมกัน

```python
fig, axes = plt.subplots(2, 1, figsize=(10, 8))

# Pressure force
axes[0].plot(forces['t'], forces['fx_p'], label='Fx (pressure)')
axes[0].plot(forces['t'], forces['fx_v'], label='Fx (viscous)')
axes[0].set_ylabel('Force (N)')
axes[0].legend()
axes[0].grid(True)

# Total force
axes[1].plot(forces['t'], forces['fx_total'], 'r-', linewidth=2)
axes[1].set_xlabel('Time (s)')
axes[1].set_ylabel('Total Fx (N)')
axes[1].grid(True)

plt.tight_layout()
plt.savefig('forces_decomposed.png', dpi=300)
plt.show()
```

### 5.3 เปรียบเทียบ Cases หลายๆ อัน

```python
plt.figure(figsize=(10, 6))

for name, group in all_data.groupby('case'):
    plt.plot(group['t'], group['fx_total'], label=name, linewidth=2)

plt.xlabel('Time (s)')
plt.ylabel('Fx (N)')
plt.title('Force Comparison: Different Angles')
plt.legend()
plt.grid(True)
plt.savefig('force_comparison.png', dpi=300)
plt.show()
```

## 6. การส่งออกข้อมูล

### 6.1 ส่งออกเป็น CSV

```python
# ส่งออกข้อมูลที่สะอาดแล้ว
forces_steady.to_csv('forces_processed.csv', index=False)
```

### 6.2 ส่งออกเป็น Excel

```python
# ส่งออกหลาย sheets
with pd.ExcelWriter('simulation_report.xlsx') as writer:
    forces.to_excel(writer, sheet_name='Raw Data')
    forces_steady.to_excel(writer, sheet_name='Steady State')
    summary.to_excel(writer, sheet_name='Summary')
```

### 6.3 สร้าง Report อัตโนมัติ

```python
from datetime import datetime

report = f"""
Simulation Report
Generated: {datetime.now()}

Case: Airfoil Flow
Solver: simpleFoam

Results:
- Final Cd: {forces['Cd'].iloc[-1]:.4f}
- Mean Fx (last 100): {mean_fx:.2f} ± {std_fx:.2f} N
- Std Dev (%): {std_fx/mean_fx*100:.2f}%

Convergence: {'✅ Yes' if percent_change < 1 else '❌ No'}
"""

with open('report.txt', 'w') as f:
    f.write(report)

print(report)
```

---

## 🧠 ตรวจสอบความเข้าใจ (Concept Check)

### แบบฝึกหัดระดับง่าย (Easy)
1. **True/False**: Pandas สามารถอ่านไฟล์ `.dat` จาก OpenFOAM ได้โดยตรง
   <details>
   <summary>คำตอบ</summary>
   ✅ จริง - ใช้ `pd.read_csv()` พร้อม `delim_whitespace=True`
   </details>

2. **เลือกตอบ**: Method ไหนใช้คำนวณค่าเฉลี่ย?
   - a) df.mean()
   - b) df.avg()
   - c) df.average()
   - d) df.calc_mean()
   <details>
   <summary>คำตอบ</summary>
   ✅ a) df.mean() - คำนวณค่าเฉลี่ยของแต่ละ column
   </details>

### แบบฝึกหัดระดับปานกลาง (Medium)
3. **อธิบาย**: ทำไมต้องใช้ Rolling Mean ในการตรวจสอบ Convergence?
   <details>
   <summary>คำตอบ</summary>
   - ข้อมูล CFD มีการ oscillation (ขึ้นลง) เล็กน้อย
   - Rolling mean ช่วย smooth ข้อมูลให้เห็น trend ชัดเจน
   - ช่วยลด noise จาก numerical fluctuations
   </details>

4. **เขียนโค้ด**: จงเขียน Python script เพื่อ:
   - อ่าน `forces.dat`
   - คำนวณ Lift Coefficient (Cl) จาก Fy
   - หาค่าเฉลี่ย Cl ช่วง 100 steps สุดท้าย
   - พล็อตกราฟ Cl vs Time
   <details>
   <summary>คำตอบ</summary>
   ```python
   import pandas as pd
   import matplotlib.pyplot as plt

   forces = pd.read_csv('postProcessing/forces/0/forces.dat',
                        delim_whitespace=True, comment='#',
                        names=['t', 'fx_p', 'fy_p', 'fz_p',
                               'fx_v', 'fy_v', 'fz_v', 'mx', 'my', 'mz'])

   forces['fy_total'] = forces['fy_p'] + forces['fy_v']
   forces['Cl'] = forces['fy_total'] / (0.5 * 1.225 * 20**2 * 2.0)

   last_100 = forces.tail(100)
   mean_cl = last_100['Cl'].mean()
   print(f"Mean Cl (last 100): {mean_cl:.4f}")

   plt.plot(forces['t'], forces['Cl'])
   plt.xlabel('Time')
   plt.ylabel('Cl')
   plt.grid(True)
   plt.savefig('Cl_vs_time.png')
   ```
   </details>

### แบบฝึกหัดระดับสูง (Hard)
5. **Hands-on**: รัน OpenFOAM case จริง แล้วใช้ Pandas วิเคราะห์ผลลัพธ์ (Cd, Cl) พร้อมพล็อตกราฟ

6. **วิเคราะห์**: เปรียบเทียบวิธีการ Post-process 3 แบบ:
   - ใช้ ParaView (GUI)
   - ใช้ Python + Pandas
   - ใช้ Excel
   ในแง่ของความรวดเร็ว, ความยืดหยุ่น, และความสามารถในการทำซ้ำ (Reproducibility)
