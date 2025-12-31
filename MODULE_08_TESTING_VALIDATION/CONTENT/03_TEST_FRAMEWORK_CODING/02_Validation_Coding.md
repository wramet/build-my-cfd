# Validation Coding

การเขียนโค้ดสำหรับ Validation

---

## Learning Objectives

เมื่ออ่านบทนี้จบ คุณจะสามารถ:

- อธิบายความแตกต่างระหว่าง Validation และ Verification และทราบ **ว่า**ทำไม Validation สำคัญ
- เลือกวิธีการ Validation ที่เหมาะสมกับปัญหาที่ต้องแก้ไข (**วิธีการเลือก** Validation method)
- เขียนโค้ด OpenFOAM สำหรับ Post-processing functions และ Sampling (**HOW**)
- คำนวณ Error metrics (RMSE, L2 norm) และตั้งเกณฑ์ Pass/Fail สำหรับการทดสอบ
- สร้าง Workflow ที่เชื่อมโยง Post-processing → Sampling → Comparison → Validation

---

## Overview

> **Validation** = Verify simulation matches physical reality

### What is Validation?

**Validation** เป็นกระบวนการตรวจสอบว่าแบบจำลอง (model) และการจำลอง (simulation) ของเราสอดคล้องกับ **ความเป็นจริงทางฟิสิกส์** หรือไม่ โดยการเปรียบเทียบผลลัพธ์จากการจำลองกับข้อมูลอ้างอิงที่น่าเชื่อถือ

### Why Validation Matters

> "A validated model builds confidence; an unvalidated one builds bridges that may fall."

- **ความน่าเชื่อถือ (Credibility):** การมีการ Validation ที่ดีช่วยสร้างความมั่นใจว่าแบบจำลองของเราสามารถทำนายปรากฏการณ์จริงได้
- **ขอบเขตการใช้งาน (Applicability):** ช่วยกำหนดขอบเขตที่แบบจำลองให้ผลลัพธ์ที่ถูกต้อง
- **การตัดสินใจ (Decision Making):** ในงานวิศวกรรม การตัดสินใจอาจขึ้นอยู่กับผลลัพธ์จากแบบจำลอง หากไม่มีการ Validation อาจนำไปสู่การตัดสินใจที่ผิดพลาด
- **การปรับปรุง (Improvement):** การเปรียบเทียบกับข้อมูลจริงช่วยชี้ให้เห็นจุดอ่อนของแบบจำลองและแนวทางการพัฒนาต่อ

### How Validation Works

กระบวนการ Validation มีขั้นตอนหลักดังนี้:

1. **เลือกข้อมูลอ้างอิง (Reference Data):** Experimental data, Analytical solution, หรือ Benchmark
2. **สร้างการจำลอง (Simulation):** ตั้งค่า OpenFOAM case ที่สอดคล้องกับเงื่อนไขข้อมูลอ้างอิง
3. **Post-processing:** ดึงข้อมูลจากการจำลองในรูปแบบที่เปรียบเทียบได้
4. **Comparison:** เปรียบเทียบและคำนวณค่า Error metrics
5. **Assessment:** ตัดสินว่าผลลัพธ์อยู่ในช่วงที่ยอมรับได้หรือไม่ (Pass/Fail)

---

## 1. Validation Types

### WHAT: ประเภทของ Validation

| Type | Compare Against | เมื่อไหร่ใช้ | ข้อดี | ข้อเสีย |
|------|-----------------|---------------|--------|---------|
| **Experimental** | Lab data | เมื่อมีข้อมูลจริง | ความถูกต้องสูงสุด | แพง ใช้เวลามาก |
| **Analytical** | Exact solutions | กรณีง่ายที่มีคำตอบแน่นอน | รวดเร็ว ถูก | จำกัดกับกรณีพิเศษ |
| **Benchmark** | Standard cases | เปรียบเทียบกับมาตรฐาน | เปรียบเทียบกับชุมชน | อาจไม่ตรงกับปัญหาเรา |
| **Code-to-code** | Other solvers | ตรวจสอบการ implement | หา bug ได้ดี | ไม่รับประกันความถูกต้อง |

### WHY: ทำไมต้องหลายประเภท?

แต่ละประเภทมีจุดประสงค์และขอบเขตที่แตกต่างกัน:
- **Experimental Validation:** ใกล้เคียงการใช้งานจริงที่สุด แต่ต้องการทรัพยากรมาก
- **Analytical Validation:** เหมาะสำหรับตรวจสอบว่า solver ทำงานถูกต้องในกรณีพื้นฐาน
- **Benchmark:** ช่วยเปรียบเทียบกับมาตรฐานอุตสาหกรรมหรืองานวิจัย
- **Code-to-code:** ช่วยตรวจสอบว่า implementation ไม่มี bug แม้ว่าจะไม่รับประกันความถูกต้องทางฟิสิกส์

### HOW: เลือกวิธีการ Validation

การเลือกวิธี Validation ขึ้นอยู่กับ:

1. **วัตถุประสงค์ (Objective):**
   - พัฒนา solver ใหม่? → Code-to-code + Analytical
   - ศึกษาปรากฏการณ์ฟิสิกส์? → Experimental + Benchmark
   - งานวิศวกรรมจริง? → Experimental (ถ้ามี) หรือ Benchmark

2. **ทรัพยากรที่มี (Available Resources):**
   - มีข้อมูล experimental? → Experimental Validation
   - มีเวลาจำกัด? → Analytical + Code-to-code
   - งบประมาณจำกัด? → Analytical หรือ Benchmark ฟรี

3. **ความซับซ้อนของปัญหา (Problem Complexity):**
   - กรณีง่าย (Flow ในท่อ) → Analytical + Experimental
   - กรณีซับซ้อน (Turbulence) → Experimental + Benchmark

4. **ขั้นตอนแนะนำ (Recommended Workflow):**
   ```
   Step 1: Analytical Validation (ถ้ามี) → ตรวจ solver
   Step 2: Code-to-code → ตรวจ implementation
   Step 3: Benchmark → เปรียบเทียบมาตรฐาน
   Step 4: Experimental → ใกล้จริงที่สุด (ถ้ามี)
   ```

---

## 2. Post-Processing Function

### WHAT: Field Averaging คืออะไร?

**Field Averaging** เป็นการคำนวณค่าเฉลี่ยของฟิลด์ (เช่น ความเร็ว U, ความดัน p) ตลอดเวลาที่กำหนด เพื่อให้ได้ค่าที่นำไปเปรียบเทียบกับข้อมูลอ้างอิงได้ง่ายขึ้น โดยเฉพาะสำหรับการไหลแบบไม่สม่ำเสมอ (Unsteady flow)

### WHY: ทำไมต้อง Average?

- **ลดความผันผวน (Reduce Fluctuations):** กรณี Turbulent flow มีการ fluctuate มาก การใช้ค่าเฉลี่ยทำให้เปรียบเทียบได้ง่ายขึ้น
- **ใกล้เคียงการวัดจริง (Match Experiments):** ข้อมูล experimental มักเป็นค่าเฉลี่ย (time-averaged)
- **เสถียรภาพทางสถิติ (Statistical Stability):** ค่าเฉลี่ยมีความเสถียรมากกว่าค่า instantaneous

### HOW: เขียน Post-processing Function

**ก่อนดูโค้ด:** เราจะเพิ่ม function ใน `system/controlDict` เพื่อให้ OpenFOAM คำนวณค่าเฉลี่ยของฟิลด์อัตโนมัติระหว่างรัน solver

```cpp
// In system/controlDict
functions
{
    fieldAverage1
    {
        type            fieldAverage;        // ประเภท function: คำนวณค่าเฉลี่ย
        writeControl    writeTime;           // เขียนเมื่อถึง writeTime
        
        // ฟิลด์ที่ต้องการ average
        fields
        (
            U                               // Velocity field
            { 
                mean on;                    // เปิดการคำนวณค่าเฉลี่ย
                prime2Mean on;              // เปิดการคำนวณ variance (fluctuation^2)
            }
            p                               // Pressure field
            { 
                mean on;                    // เฉพาะค่าเฉลี่ย (ไม่ต้องการ variance)
            }
        );
    }
}
```

**ผลลัพธ์:** OpenFOAM จะสร้างไฟล์ใหม่ เช่น `U_mean`, `p_mean` ที่สามารถนำไปเปรียบเทียบได้

---

## 3. Sampling

### WHAT: Sampling คืออะไร?

**Sampling** เป็นการดึงค่าฟิลด์จากพื้นที่ 3D มาเป็นข้อมูล 1D หรือ 2D เพื่อให้สามารถเปรียบเทียบกับข้อมูลที่วัดจากการทดลองได้ง่ายขึ้น

### WHY: ทำไมต้อง Sample?

- **ลดมิติข้อมูล (Reduce Dimensionality):** ข้อมูล experimental มักเป็นจุดวัดหรือเส้น ไม่ใช่ฟิลด์ 3D เต็ม
- **ความง่ายในการเปรียบเทียบ (Easy Comparison):** เปรียบเทียบกราฟ 1D ง่ายกว่า contour 3D
- **ประหยัดพื้นที่ (Storage Efficiency):** ข้อมูลเส้น 100 จุดเล็กกว่าข้อมูล volume ล้านเซลล์

### HOW: สร้าง Sampling Function

**ก่อนดูโค้ด:** เราจะ sample ค่าฟิลด์ตามแนวเส้น (line) โดยกำหนดจุดเริ่มต้น จุดสิ้นสุด และจำนวนจุดที่ต้องการ

```cpp
// Sample along line in system/controlDict
functions
{
    sample1
    {
        type            sets;               // ประเภท: sample ตาม set ที่กำหนด
        writeControl    writeTime;          // เขียนเมื่อถึง writeTime
        setFormat       raw;                // รูปแบบไฟล์: raw (x, y, z, value)
        
        // วิธี interpolation เมื่อ sample ระหว่างเซลล์
        interpolationScheme cellPoint;      // cellPoint = bilinear interpolation
        
        fields          (U p);              // ฟิลด์ที่ต้องการ sample
        
        sets
        (
            centerLine
            {
                type    uniform;            // Sample ที่สม่ำเสมอตามแนวเส้น
                axis    x;                  // แนวเส้นตามแกน x
                
                // จุดเริ่มต้นและสิ้นสุดของเส้น sample (x, y, z)
                start   (0 0.5 0.5);         // เริ่มที่ x=0, y=0.5, z=0.5
                end     (1 0.5 0.5);         // จบที่ x=1, y=0.5, z=0.5
                
                nPoints 100;                 // Sample 100 จุดตามแนวเส้น
            }
        );
    }
}
```

**ผลลัพธ์:** OpenFOAM จะสร้างไฟล์ใน `postProcessing/sample1/<time>/centerLine_U.xy` และ `centerLine_p.xy` ที่มี 4 คอลัมน์: `x, y, z, value`

**Cross-reference:** การใช้ข้อมูลจาก sampling จะถูกนำไปใช้ใน [Section 4: Compare with Data](#4-compare-with-data) และ [Section 5: Error Metrics](#5-error-metrics) ต่อไป

---

## 4. Compare with Data

### WHAT: การเปรียบเทียบข้อมูล

การเปรียบเทียบข้อมูลจาก Simulation กับข้อมูลอ้างอิง (Experimental/Analytical) เพื่อประเมินความถูกต้องของแบบจำลอง

### WHY: ทำไมต้องเปรียบเทียบ?

- **หาความแตกต่าง (Identify Discrepancies):** เห็นภาพรวมว่า simulation ใกล้เคียงข้อมูลจริงแค่ไหน
- **ตรวจสอบแนวโน้ม (Check Trends):** แม้ค่าจะไม่ตรง แต่ pattern อาจถูกต้อง
- **เลือกพื้นที่วิเคราะห์ (Select Regions):** บางพื้นที่อาจมีความแม่นยำสูงกว่า

### HOW: เขียน Python Script สำหรับเปรียบเทียบ

**ก่อนดูโค้ด:** เราจะใช้ Python + Matplotlib อ่านข้อมูลจาก OpenFOAM (ที่ sample มาจาก Section 3) และข้อมูล experimental แล้ว plot เปรียบเทียบ

```python
#!/usr/bin/env python3
"""
เปรียบเทียบข้อมูล OpenFOAM กับ Experimental Data
Input: 
  - postProcessing/sample1/0/centerLine_U.xy (จาก OpenFOAM sampling)
  - experimental_data.csv (ข้อมูลจากการทดลอง)
Output:
  - validation.png (กราฟเปรียบเทียบ)
"""

import numpy as np
import matplotlib.pyplot as plt

# 1. Load simulation data (จาก sampling section 3)
# ไฟล์ format: x, y, z, Ux, Uy, Uz
sim = np.loadtxt('postProcessing/sample1/0/centerLine_U.xy')
x_sim = sim[:, 0]          # คอลัมน์ 0 = x position
U_sim = sim[:, 1]          # คอลัมน์ 1 = velocity (x-direction)

# 2. Load experimental data
# ไฟล์ format: x_position, velocity (คั่นด้วย comma)
exp = np.loadtxt('experimental_data.csv', delimiter=',')
x_exp = exp[:, 0]
U_exp = exp[:, 1]

# 3. Plot comparison
plt.figure(figsize=(10, 6))
plt.plot(x_sim, U_sim, 'b-', linewidth=2, label='OpenFOAM Simulation')
plt.plot(x_exp, U_exp, 'ro', markersize=6, label='Experimental Data')

plt.xlabel('Position x (m)', fontsize=12)
plt.ylabel('Velocity U (m/s)', fontsize=12)
plt.title('Velocity Profile Comparison', fontsize=14)
plt.legend(fontsize=12)
plt.grid(True, alpha=0.3)

# 4. Save figure
plt.savefig('validation.png', dpi=150, bbox_inches='tight')
print("✓ Saved validation.png")

# 5. Basic statistics (ดูเพิ่มเติมใน Section 5)
mean_diff = np.mean(np.abs(U_sim - np.interp(x_sim, x_exp, U_exp)))
print(f"✓ Mean absolute difference: {mean_diff:.4f} m/s")
```

**Cross-reference:** หลังจาก plot เปรียบเทียบแล้ว สามารถคำนวณ Error metrics เชิงปริมาณได้ใน [Section 5: Error Metrics](#5-error-metrics)

---

## 5. Error Metrics

### WHAT: Error Metrics คืออะไร?

**Error Metrics** เป็นตัวชี้วัดเชิงปริมาณที่บอกว่า Simulation แตกต่างจากข้อมูลอ้างอิงมากน้อยเพียงใด แต่ละ metric มีความหมายและการใช้งานที่แตกต่างกัน

### WHY: ทำไมต้อง Error Metrics?

- **ความเป็นวัตถุประสงค์ (Objectivity):** ตัวเลขชัดเจนกว่าการดูกราฟด้วยตาเปล่า
- **การตัดสินใจ Pass/Fail:** สามารถกำหนดเกณฑ์ (criteria) ได้ชัดเจน
- **เปรียบเทียบระหว่าง Cases:** ตัวเลขทำให้เปรียบเทียบได้ง่ายว่า case ไหนดีกว่า

### HOW: คำนวณ Error Metrics

**ก่อนดูโค้ด:** เราจะคำนวณ 3 metrics หลักที่ใช้บ่อยใน CFD Validation

```python
#!/usr/bin/env python3
"""
คำนวณ Error Metrics สำหรับ Validation
Input: ข้อมูล Simulation และ Experimental (จาก Section 4)
Output: Error metrics (Relative Error, RMSE, L2 Norm)
"""

import numpy as np

# สมมติว่ามีข้อมูลแล้วจาก Section 4
# sim_data = array ของค่า simulation
# exp_data = array ของค่า experimental ที่ interpolat ให้มีจำนวนจุดเท่ากัน

# 1. Relative Error (%)
# เหมาะสำหรับดูว่า error มีขนาดเทียบกับค่าจริงเท่าไหร่
# ระวัง: ห้ามหารด้วยศูนย์!
rel_error = np.abs(sim_data - exp_data) / (np.abs(exp_data) + 1e-10) * 100
mean_rel_error = np.mean(rel_error)

print(f"Mean Relative Error: {mean_rel_error:.2f}%")
# การตีความ: < 5% = ดีมาก, 5-10% = ดี, > 20% = ต้องตรวจสอบ

# 2. Root Mean Square Error (RMSE)
# Metric ที่นิยมที่สุด ให้ความสำคัญกับ error ขนาดใหญ่ (เพราะยกกำลังสอง)
rmse = np.sqrt(np.mean((sim_data - exp_data)**2))
print(f"RMSE: {rmse:.4f}")
# การตีความ: ค่า RMSE อยู่ในหน่วยเดียวกับข้อมูล (เช่น m/s)

# 3. L2 Norm (Normalized RMS)
# ทำให้สามารถเปรียบเทียบระหว่าง problems ที่มี scale ต่างกัน
l2_norm = np.sqrt(np.sum((sim_data - exp_data)**2)) / np.sqrt(np.sum(exp_data**2))
print(f"L2 Norm: {l2_norm:.4f}")
# การตีความ: 0 = ตรงเป๊ะ, 0.1 = error 10%, 1 = error เท่ากับ signal

# 4. Correlation Coefficient (R²)
# ดูว่า trend ตรงกันหรือไม่ (ไม่สนใจค่าสัมบูรณ์)
correlation = np.corrcoef(sim_data, exp_data)[0, 1]
r_squared = correlation**2
print(f"R²: {r_squared:.4f}")
# การตีความ: 1 = trend ตรงกันสมบูรณ์, > 0.9 = ดี, < 0.5 = trend ไม่ตรงกัน

# Summary
print("\n=== Validation Summary ===")
print(f"Mean Relative Error: {mean_rel_error:.2f}%")
print(f"RMSE: {rmse:.4f} (หน่วยเดียวกับข้อมูล)")
print(f"L2 Norm: {l2_norm:.4f} (normalized)")
print(f"R²: {r_squared:.4f} (trend correlation)")
```

### HOW TO CHOOSE: เลือก Metric ที่เหมาะสม

| Situation | Recommended Metric | เหตุผล |
|-----------|-------------------|---------|
| ต้องการเปรียบเทียบ scale | Relative Error | เห็น error เป็น % |
| ต้องการ penalty สำหรับ outliers | RMSE | ยกกำลังสองให้ความสำคัญกับ error ใหญ่ |
| เปรียบเทียบหลาย problems | L2 Norm | Normalized ทำให้เปรียบเทียบข้าม problems ได้ |
| ดูว่า trend ตรงไหม | R² | ไม่สนค่าสัมบูรณ์ ดู pattern การเปลี่ยนแปลง |

**Cross-reference:** หลังจากคำนวณ error แล้ว สามารถนำไปตั้งเกณฑ์ Pass/Fail ได้ใน [Section 6: Pass/Fail Criteria](#6-passfail-criteria)

---

## 6. Pass/Fail Criteria

### WHAT: Pass/Fail Criteria

เกณฑ์การตัดสินว่า Simulation ผ่านการ Validation หรือไม่ โดยกำหนดค่าความคลาดเคลื่อนสูงสุดที่ยอมรับได้ (Tolerance)

### WHY: ทำไมต้อง Tolerance?

> "All models are wrong, but some are useful" — George Box

- **ไม่มี Simulation ที่ exact 100%:** มี error จากการปัดเศษ, discretization, turbulence modeling
- **การตัดสินใจที่ชัดเจน:** รู้ได้ทันทีว่า case ผ่านหรือไม่ โดยไม่ต้องมองกราฟทุกครั้ง
- **Automation:** สามารถเขียน script ทดสอบอัตโนมัติได้

### HOW: ตั้งเกณฑ์และทดสอบ

**ก่อนดูโค้ด:** เราจะกำหนด tolerance (เช่น RMSE < 5%) และเขียน script ทดสอบว่าผ่านหรือไม่

#### 6.1 กำหนด Tolerance (Setting Criteria)

```python
#!/usr/bin/env python3
"""
ตั้งเกณฑ์ Pass/Fail สำหรับ Validation
ค่า tolerance ขึ้นอยู่กับ:
  - ความซับซ้อนของปัญหา (Complexity)
  - ความแม่นยำที่ต้องการ (Required accuracy)
  - คุณภาพข้อมูลอ้างอิง (Quality of reference data)
"""

# ตัวอย่างเกณฑ์ (ตัวอย่างเท่านั้น ปรับตามงานของคุณ)
VALIDATION_CRITERIA = {
    'velocity_rmse': {
        'tolerance': 0.05,          # 5% ของค่า velocity สูงสุด
        'unit': 'm/s',
        'description': 'RMSE ของ velocity'
    },
    'pressure_l2_norm': {
        'tolerance': 0.10,          # 10% (L2 norm normalized)
        'unit': 'dimensionless',
        'description': 'L2 norm ของ pressure'
    },
    'relative_error_max': {
        'tolerance': 15.0,          # 15% (maximum mean relative error)
        'unit': '%',
        'description': 'Relative error เฉลี่ยสูงสุด'
    }
}

# คำนวณค่า tolerance ในหน่วยจริงๆ
def check_tolerance(metric_value, tolerance_percent, reference_max):
    """
    Check if metric is within tolerance
    tolerance_percent: tolerance เป็น % (เช่น 5%)
    reference_max: ค่าสูงสุดของ reference data (สำหรับ convert % เป็น absolute value)
    """
    tolerance_absolute = tolerance_percent / 100.0 * reference_max
    return metric_value <= tolerance_absolute, tolerance_absolute
```

#### 6.2 Python Pass/Fail Script

```python
#!/usr/bin/env python3
"""
ทดสอบ Pass/Fail ด้วย Python
Input: Error metrics จาก Section 5
Output: PASS/FAIL + Report
"""

import numpy as np
import sys

# โหลดข้อมูลจาก Section 4 และ 5
sim_data = np.loadtxt('simulation_data.txt')
exp_data = np.loadtxt('experimental_data.txt')

# คำนวณ error metrics (จาก Section 5)
rmse = np.sqrt(np.mean((sim_data - exp_data)**2))
l2_norm = np.sqrt(np.sum((sim_data - exp_data)**2)) / np.sqrt(np.sum(exp_data**2))
mean_rel_error = np.mean(np.abs(sim_data - exp_data) / (np.abs(exp_data) + 1e-10)) * 100

# ตั้งเกณฑ์ (tolerance)
TOLERANCE_RMSE = 0.05       # 5% ของค่าสูงสุด
TOLERANCE_L2 = 0.10         # 10%
TOLERANCE_REL = 15.0        # 15%

# แปลง tolerance เป็นค่าจริง (สมมติค่าสูงสุด = 10 m/s)
MAX_REF_VALUE = 10.0
rmse_tolerance = TOLERANCE_RMSE / 100.0 * MAX_REF_VALUE

# ทดสอบแต่ละ criterion
results = []

# Test 1: RMSE
rmse_pass = rmse <= rmse_tolerance
results.append(('RMSE', rmse, rmse_tolerance, rmse_pass))

# Test 2: L2 Norm
l2_pass = l2_norm <= TOLERANCE_L2
results.append(('L2 Norm', l2_norm, TOLERANCE_L2, l2_pass))

# Test 3: Relative Error
rel_pass = mean_rel_error <= TOLERANCE_REL
results.append(('Relative Error', mean_rel_error, TOLERANCE_REL, rel_pass))

# แสดงผล
print("\n" + "="*60)
print("VALIDATION REPORT".center(60))
print("="*60)

all_pass = True
for name, value, tolerance, passed in results:
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{name:20s}: {value:8.4f} / {tolerance:8.4f} [{status}]")
    if not passed:
        all_pass = False

print("="*60)

if all_pass:
    print("✓ VALIDATION PASSED")
    print("  All criteria within tolerance")
    sys.exit(0)
else:
    print("✗ VALIDATION FAILED")
    print("  Some criteria exceed tolerance")
    sys.exit(1)
```

#### 6.3 Bash Pass/Fail Script

```bash
#!/bin/bash
# ทดสอบ Pass/Fail ด้วย Bash
# Input: error value (จาก Python script หรือ manual calculation)
# Output: PASS/FAIL

# คำนวณ error (สมมติได้จาก output ของ Python)
ERROR_RMSE=$(python3 -c "
import numpy as np
sim = np.loadtxt('simulation_data.txt')
exp = np.loadtxt('experimental_data.txt')
rmse = np.sqrt(np.mean((sim - exp)**2))
print(rmse)
")

# ตั้งเกณฑ์ (5% ของค่า max = 10 m/s → 0.5 m/s)
TOLERANCE=0.5

# ทดสอบ (ใช้ bc สำหrับเปรียบเทียบทศนิยม)
if [ $(echo "$ERROR_RMSE < $TOLERANCE" | bc -l) -eq 1 ]; then
    echo "✓ PASSED: RMSE ($ERROR_RMSE) < Tolerance ($TOLERANCE)"
    exit 0
else
    echo "✗ FAILED: RMSE ($ERROR_RMSE) >= Tolerance ($TOLERANCE)"
    exit 1
fi
```

**Cross-reference:** การทดสอบ Pass/Fail นี้สามารถนำไปใช้ใน Automation scripts ได้ ดูรายละเอียดใน [03_Automation_Scripts.md](03_Automation_Scripts.md)

---

## 7. Practical Workflow Example

### WHAT: Workflow ที่สมบูรณ์

ตัวอย่างการเชื่อมโยงทุกส่วนเข้าด้วยกัน (Post-processing → Sampling → Comparison → Validation)

### WHY: ทำไมต้อง Workflow?

- **ความเป็นระบบ (Systematic):** ไม่พลาดขั้นตอนสำคัญ
- **Reproducibility:** สามารถทำซ้ำได้ง่าย
- **Automation:** สามารถเขียน script ทำให้เป็นไปโดยอัตโนมัติ

### HOW: ตัวอย่าง Workflow แบบ Step-by-Step

```bash
#!/bin/bash
# Complete Validation Workflow for OpenFOAM Case
# ใช้สำหรับ Flow ในท่อ (Pipe Flow) เปรียบเทียบกับ Experimental Data

set -e  # หยุดถ้ามี error

# ========================================
# STEP 1: Setup
# ========================================
echo "=== Step 1: Setup ==="
CASE_DIR="$PWD"
EXP_DATA="$CASE_DIR/experimental_velocity_profile.csv"
OUTPUT_DIR="$CASE_DIR/validation_results"

mkdir -p "$OUTPUT_DIR"

# ========================================
# STEP 2: Add Post-processing Functions
# ========================================
echo "=== Step 2: Configure Post-processing ==="

# เพิ่ม fieldAverage function (จาก Section 2)
cat >> "$CASE_DIR/system/controlDict" << 'EOF'
functions
{
    fieldAverage1
    {
        type            fieldAverage;
        writeControl    writeTime;
        fields
        (
            U { mean on; prime2Mean on; }
            p { mean on; }
        );
    }
    
    sample1
    {
        type            sets;
        writeControl    writeTime;
        setFormat       raw;
        interpolationScheme cellPoint;
        fields          (U);
        sets
        (
            centerLine
            {
                type    uniform;
                axis    x;
                start   (0 0.5 0.5);
                end     (1 0.5 0.5);
                nPoints 100;
            }
        );
    }
}
EOF

# ========================================
# STEP 3: Run Simulation
# ========================================
echo "=== Step 3: Run Simulation ==="
cd "$CASE_DIR"
blockMesh
simpleFoam  # หรือ solver อื่นๆ

# ========================================
# STEP 4: Extract Data
# ========================================
echo "=== Step 4: Extract Data ==="
# OpenFOAM สร้าง sampled data อัตโนมัติใน postProcessing/
SAMPLE_FILE="$CASE_DIR/postProcessing/sample1/*/centerLine_U.xy"
cp $SAMPLE_FILE "$OUTPUT_DIR/simulation_data.xy"

# ========================================
# STEP 5: Compare and Validate
# ========================================
echo "=== Step 5: Validation ==="

python3 << 'PYTHON_EOF'
import numpy as np
import matplotlib.pyplot as plt
import sys

# Load data
sim = np.loadtxt('validation_results/simulation_data.xy')
exp = np.loadtxt('experimental_velocity_profile.csv', delimiter=',')

# Extract velocity (column 1 = Ux)
x_sim = sim[:, 0]
u_sim = sim[:, 1]
x_exp = exp[:, 0]
u_exp = exp[:, 1]

# Plot comparison
plt.figure(figsize=(10, 6))
plt.plot(x_sim, u_sim, 'b-', linewidth=2, label='OpenFOAM')
plt.plot(x_exp, u_exp, 'ro', markersize=6, label='Experiment')
plt.xlabel('Position x (m)')
plt.ylabel('Velocity (m/s)')
plt.title('Validation: Velocity Profile')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('validation_results/comparison_plot.png', dpi=150)
print("✓ Saved validation_results/comparison_plot.png")

# Calculate error metrics
u_exp_interp = np.interp(x_sim, x_exp, u_exp)
rmse = np.sqrt(np.mean((u_sim - u_exp_interp)**2))
l2_norm = np.sqrt(np.sum((u_sim - u_exp_interp)**2)) / np.sqrt(np.sum(u_exp_interp**2))
rel_error = np.mean(np.abs(u_sim - u_exp_interp) / np.abs(u_exp_interp)) * 100

print(f"\n=== Error Metrics ===")
print(f"RMSE: {rmse:.4f} m/s")
print(f"L2 Norm: {l2_norm:.4f}")
print(f"Mean Relative Error: {rel_error:.2f}%")

# Pass/Fail criteria
TOLERANCE_RMSE = 0.05  # 5% of max velocity
TOLERANCE_L2 = 0.10
TOLERANCE_REL = 15.0

all_pass = True

if rmse > TOLERANCE_RMSE:
    print(f"\n✗ FAIL: RMSE ({rmse:.4f}) > {TOLERANCE_RMSE}")
    all_pass = False
else:
    print(f"✓ PASS: RMSE within tolerance")

if l2_norm > TOLERANCE_L2:
    print(f"✗ FAIL: L2 Norm ({l2_norm:.4f}) > {TOLERANCE_L2}")
    all_pass = False
else:
    print(f"✓ PASS: L2 Norm within tolerance")

if rel_error > TOLERANCE_REL:
    print(f"✗ FAIL: Relative Error ({rel_error:.2f}%) > {TOLERANCE_REL}%")
    all_pass = False
else:
    print(f"✓ PASS: Relative Error within tolerance")

# Save report
with open('validation_results/report.txt', 'w') as f:
    f.write("OpenFOAM Validation Report\n")
    f.write("="*50 + "\n\n")
    f.write(f"RMSE: {rmse:.4f} m/s\n")
    f.write(f"L2 Norm: {l2_norm:.4f}\n")
    f.write(f"Relative Error: {rel_error:.2f}%\n\n")
    f.write(f"Status: {'PASS' if all_pass else 'FAIL'}\n")

if all_pass:
    print("\n✓ VALIDATION PASSED")
    sys.exit(0)
else:
    print("\n✗ VALIDATION FAILED")
    sys.exit(1)
PYTHON_EOF

# ========================================
# STEP 6: Summary
# ========================================
if [ $? -eq 0 ]; then
    echo ""
    echo "================================"
    echo "✓ Validation Complete: PASSED"
    echo "================================"
    echo "Results saved in: $OUTPUT_DIR"
    ls -lh "$OUTPUT_DIR"
else
    echo ""
    echo "================================"
    echo "✗ Validation Complete: FAILED"
    echo "================================"
    echo "Check $OUTPUT_DIR/report.txt for details"
    exit 1
fi
```

### Workflow Diagram

```
┌──────────────────┐
│   1. Setup       │ → สร้าง case และเตรียมข้อมูล experimental
└────────┬─────────┘
         ↓
┌──────────────────┐
│ 2. Configure     │ → เพิ่ม functions (fieldAverage, sample)
│    Functions     │
└────────┬─────────┘
         ↓
┌──────────────────┐
│ 3. Run           │ → blockMesh → solver
│    Simulation    │
└────────┬─────────┘
         ↓
┌──────────────────┐
│ 4. Extract       │ → OpenFOAM สร้าง sampled data
│    Data          │
└────────┬─────────┘
         ↓
┌──────────────────┐
│ 5. Validate      │ → Plot → Calculate Error → Pass/Fail
└────────┬─────────┘
         ↓
┌──────────────────┐
│ 6. Report        │ → Summary + Decision
└──────────────────┘
```

---

## Key Takeaways

1. **Validation vs Verification:** 
   - **Validation** = ตรวจสอบว่า simulation ตรงกับ **physical reality** (เปรียบเทียบกับ experiment)
   - **Verification** = ตรวจสอบว่า **code** ทำงานถูกต้อง (เปรียบเทียบกับ analytical solution)

2. **เลือกวิธี Validation ให้เหมาะกับงาน:**
   - มีข้อมูลจริง? → Experimental Validation
   - กรณีง่าย? → Analytical Solution
   - เปรียบเทียบมาตรฐาน? → Benchmark
   - ตรวจ solver? → Code-to-code

3. **3W Framework ใน Practice:**
   - **WHAT:** รู้จัก Validation types, Error metrics
   - **WHY:** เข้าใจว่าทำไมต้อง validate, tolerance matters
   - **HOW:** เขียน controlDict functions, Python scripts, Pass/Fail tests

4. **Error Metrics:**
   - **RMSE:** เน้น error ขนาดใหญ่ (ยกกำลังสอง)
   - **L2 Norm:** Normalized → เปรียบเทียบข้าม problems ได้
   - **Relative Error:** เห็น error เป็น %

5. **Pass/Fail Criteria:**
   - ต้องกำหนด tolerance ที่ชัดเจน
   - ขึ้นอยู่กับความแม่นยำที่ต้องการและคุณภาพข้อมูลอ้างอิง
   - สามารถ automate ได้ด้วย Bash/Python scripts

6. **Workflow:**
   - Setup → Configure Functions → Run Simulation → Extract Data → Validate → Report
   - ทุกขั้นตอนสามารถ automate ได้ (ดู [03_Automation_Scripts.md](03_Automation_Scripts.md))

---

## Quick Reference

### Common OpenFOAM Functions

| Task | Function | Parameter |
|------|----------|-----------|
| Time average | `fieldAverage` | `mean on`, `prime2Mean on` |
| Line sample | `sets` | `type uniform; axis x; start/end` |
| Probe points | `probes` | `probeLocations` |
| Surface data | `surfaces` | `type sampledSurfaces` |

### Error Metrics Summary

| Metric | Formula | เหมาะกับ |
|--------|---------|-----------|
| RMSE | √(mean((sim - exp)²)) | General purpose |
| L2 Norm | ||sim - exp||₂ / ||exp||₂ | Cross-problem comparison |
| Relative Error | \|sim - exp\| / \|exp\| × 100% | Percentage view |
| R² | correlation² | Trend checking |

### Common Tolerances

| Application | Typical RMSE Tolerance |
|-------------|----------------------|
| R&D (basic) | 10-20% |
| Engineering design | 5-10% |
| High-accuracy research | < 5% |
| Code verification | < 1% |

---

## Concept Check

<details>
<summary><b>1. Validation vs Verification?</b></summary>

- **Validation:** ตรวจสอบว่า **model & simulation** ตรงกับ **physical reality** (เปรียบเทียบกับ experiment)
- **Verification:** ตรวจสอบว่า **code** แก้สมการถูกต้องหรือไม่ (เปรียบเทียบกับ analytical solution)

**ตัวอย่าง:**
- Validation: จำลอง flow รอบตัวถังรถแล้วเปรียบเทียบกับ wind tunnel data
- Verification: แก้สมการ Navier-Stokes แล้วเปรียบบกับ exact solution (เช่น Poiseuille flow)

</details>

<details>
<summary><b>2. RMSE คืออะไร? ใช้เมื่อไหร่?</b></summary>

**RMSE (Root Mean Square Error)** = √(mean((sim - exp)²))

**ใช้เมื่อ:**
- ต้องการ metric ทั่วไปที่ใช้ได้กับทุกกรณี
- ต้องการให้ความสำคัญกับ error ขนาดใหญ่ (เพราะยกกำลังสอง)
- ต้องการหน่วยเดียวกับข้อมูล (เช่น m/s หรือ Pa)

**ข้อดี:** ใช้ง่าย, แพร่หลาย, เหมาะกับกรณีส่วนใหญ่  
**ข้อเสีย:** ไม่ normalized → เปรียบเทียบข้าม problems ยาก
</details>

<details>
<summary><b>3. ทำไมต้อง tolerance? Numerical simulations ไม่ exact?</b></summary>

**ทำไมต้อง tolerance:**
- **Discretization error:** แบ่ง space เป็นเซลล์ → ไม่ต่อเนื่องเหมือน reality
- **Modeling assumptions:** Turbulence models, boundary conditions เป็นการประมาณ
- **Numerical precision:** คอมพิวเตอร์เก็บทศนิยมจำกัด (floating point error)
- **Measurement uncertainty:** ข้อมูล experimental ก็มี error ด้วย

**การเลือก tolerance:**
- ขึ้นอยู่กับ **application** (engineering vs research)
- ขึ้นอยู่กับ **คุณภาพข้อมูลอ้างอิง** (high-quality data → low tolerance)
- ขึ้นอยู่กับ **cost** (tolerance ต่ำ → mesh ละเอียด → แพง)

**ตัวอย่าง:**
- R&D/Prototype: tolerance 10-20% ยอมรับได้
- ออกแบบ critical (เครื่องบิน): tolerance < 5%
- Code verification: tolerance < 1%

</details>

<details>
<summary><b>4. เลือก Validation type อย่างไร?</b></summary>

**คำถามที่ต้องถามตัวเอง:**

1. **วัตถุประสงค์อะไร?**
   - พัฒนา solver → Code-to-code + Analytical
   - งานวิจัยฟิสิกส์ → Experimental + Benchmark
   - งานวิศวกรรม → Experimental (ถ้ามี) / Benchmark

2. **ทรัพยากรอะไรมี?**
   - มีเงิน/เวลา → Experimental
   - จำกัด → Analytical หรือ Benchmark ฟรี
   
3. **ความซับซ้อนของปัญหา?**
   - ง่าย (analytical มี) → ใช้ Analytical
   - ปานกลาง → Benchmark
   - ซับซ้อน (turbulence) → Experimental

**Workflow แนะนำ:**
```
Analytical (ถ้ามี) → Code-to-code → Benchmark → Experimental
(ง่าย → ยาก)      (ถูก)           (มาตรฐาน)      (แพงแต่ดีที่สุด)
```

</details>

<details>
<summary><b>5. Sampling ทำอะไร? ทำไมต้อง interpolationScheme?</b></summary>

**Sampling:** ดึงค่าฟิลด์จาก volume 3D มาเป็น line/points 1D-2D เพื่อเปรียบเทียบกับ experiment

**ทำไมต้อง interpolationScheme:**
- OpenFOAM เก็บค่าฟิลด์ที่ **cell centers** (ไม่ได้ทุกจุดใน space)
- เวลา sample ที่จุดที่ไม่ใช่ cell center → ต้อง **interpolate**
- **cellPoint:** ใช้ bilinear interpolation (ค่าประมาณจากเซลล์รอบๆ) → ดี, smooth
- **cell:** ใช้ค่าจากเซลล์ที่จุดอยู่ (nearest cell) → แม่นยำน้อยกว่า

**ตัวอย่าง:**
```cpp
interpolationScheme cellPoint;  // แนะนำ: smooth และแม่นยำ
interpolationScheme cell;        // เร็วแต่แม่นยำน้อยกว่า
```

</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Unit Testing:** [01_Unit_Testing.md](01_Unit_Testing.md)
- **Automation Scripts:** [03_Automation_Scripts.md](03_Automation_Scripts.md) - สำหรับ automate workflow ทั้งหมด