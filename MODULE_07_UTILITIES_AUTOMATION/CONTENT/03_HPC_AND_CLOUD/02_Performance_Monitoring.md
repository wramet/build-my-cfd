# Performance Monitoring in Parallel OpenFOAM Simulations
# การตรวจสอบประสิทธิภาพการคำนวณแบบขนานใน OpenFOAM

---

## Learning Objectives | วัตถุประสงค์การเรียนรู้

After completing this module, you will be able to:
| เมื่อสิ้นสุดหมวดนี้ คุณจะสามารถ:

- Understand **WHAT** performance monitoring encompasses in parallel OpenFOAM simulations
| ทำความเข้าใจ **ว่า** การตรวจสอบประสิทธิภาพในการคำนวณแบบขนานคืออะไร

- Recognize **WHY** monitoring is critical for identifying bottlenecks and optimizing computational resources
| ตระหนักถึง **เหตุผล** ที่การตรวจสอบเป็นสิ่งสำคัญในการระบุปัญหาและปรับปรุงประสิทธิภาพการใช้ทรัพยากร

- Apply **HOW** to use comprehensive monitoring tools including built-in commands, PyFoam, and external visualization
| ประยุกต์ใช้ **วิธีการ** ตรวจสอบประสิทธิภาพโดยใช้เครื่องมือต่างๆ ทั้งในตัว OpenFOAM PyFoam และเครื่องมือภายนอก

- Analyze speedup and efficiency metrics to evaluate parallel scaling
| วิเคราะห์ตัวชี้วัดการเพิ่มความเร็วและประสิทธิภาพเพื่อประเมินการสเกลของการคำนวณแบบขนาน

- Identify common performance bottlenecks and apply targeted optimizations
| ระบุปัญหาคอขวดทั่วไปที่ส่งผลต่อประสิทธิภาพและใช้การปรับปรุงที่เหมาะสม

**Estimated Completion Time:** 45-60 minutes | **เวลาที่คาดว่าจะใช้:** 45-60 นาที  
**Difficulty Level:** ⭐⭐⭐ Intermediate | **ระดับความยาก:** ⭐⭐⭐ ระดับกลาง

---

## Prerequisites | ข้อกำหนดเบื้องต้น

Before starting this module, ensure you have:
| ก่อนเริ่มหมวดนี้ ให้ตรวจสอบว่า:

- Completed [01_Domain_Decomposition.md](01_Domain_Decomposition.md) - Understanding decomposition fundamentals
| ผ่านหมวด 01_Domain_Decomposition.md - ทำความเข้าใจพื้นฐานการแบ่งโดเมน

- Running OpenFOAM simulation with parallel setup (4+ processors recommended)
| มีการจำลอง OpenFOAM แบบขนานที่ทำงานอยู่ (แนะนำ 4 โปรเซสเซอร์ขึ้นไป)

- Basic familiarity with Linux command line (grep, awk, bash loops)
| ความคุ้นเคยกับคำสั่ง Linux ในระดับพื้นฐาน (grep awk ลูป bash)

- Python environment with PyFoam installed (optional but recommended)
| สภาพแวดล้อม Python ที่ติดตั้ง PyFoam แล้ว (ไม่บังคับแต่แนะนำ)

---

## 1. What is Performance Monitoring? | การตรวจสอบประสิทธิภาพคืออะไร?

### 1.1 Definition | นิยาม

**Performance monitoring** in parallel OpenFOAM simulations is the systematic process of collecting, analyzing, and interpreting runtime metrics to evaluate computational efficiency and identify optimization opportunities.

**การตรวจสอบประสิทธิภาพ** ในการจำลอง OpenFOAM แบบขนานคือกระบวนการเชิงระบบในการเก็บรวบรวม วิเคราะห์ และตีความข้อมูลเมตริกรันไทม์เพื่อประเมินประสิทธิภาพการคำนวณและระบุโอกาสในการปรับปรุง

### 1.2 Key Monitoring Dimensions | มิติที่สำคัญในการตรวจสอบ

| Dimension | Description | คำอธิบาย |
|-----------|-------------|-----------|
| **Execution Time** | Wall-clock time per time step | เวลาจริงต่อขั้นตอนเวลา |
| **Residual Behavior** | Convergence characteristics | ลักษณะการลู่เข้า |
| **Load Balance** | Work distribution across processors | การกระจายงานไปยังโปรเซสเซอร์ |
| **Memory Usage** | RAM consumption per processor | การใช้หน่วยความจำ RAM ต่อโปรเซสเซอร์ |
| **Communication Overhead** | MPI communication cost | ต้นทุนการสื่อสาร MPI |

---

## 2. Why Monitor Performance? | ทำไมต้องตรวจสอบประสิทธิภาพ?

### 2.1 Benefits of Monitoring | ประโยชน์ของการตรวจสอบ

✅ **Bottleneck Identification** | **การระบุปัญหาคอขวด**
- Detect communication overhead between processors
| ตรวจพบค่าใช้จ่ายในการสื่อสารระหว่างโปรเซสเซอร์

- Identify I/O bottlenecks from frequent disk writes
| ระบุปัญหาคอขวด I/O จากการเขียนดิสก์บ่อย

- Discover imbalanced decomposition leading to idle processors
| ค้นพบการแบ่งโดเมนที่ไม่สมดุลทำให้โปรเซสเซอร์ว่างเปล่า

✅ **Resource Optimization** | **การปรับปรุงทรัพยากร**
- Maximize HPC cluster utilization efficiency
| ปรับปรุงประสิทธิภาพการใช้คลัสเตอร์ HPC ให้สูงสุด

- Reduce computational costs by optimizing core count
| ลดต้นทุนการคำนวณโดยปรับจำนวนคอร์ให้เหมาะสม

- Predict simulation completion time accurately
| ทำนายเวลาที่การจำลองจะเสร็จสิ้นได้อย่างแม่นยำ

✅ **Quality Assurance** | **การรับรองคุณภาพ**
- Verify solver stability through residual analysis
| ตรวจสอบเสถียรภาพของตัวแก้สมการผ่านการวิเคราะห์ค่าเหลือ

- Ensure physical convergence, not just numerical convergence
| รับรองการลู่เข้าทางฟิสิกส์ ไม่ใช่เพียงการลู่เข้าทางตัวเลข

### 2.2 When to Monitor? | เมื่อไหร่ควรตรวจสอบ?

| Scenario | Action | การกระทำ |
|----------|--------|-----------|
| **Initial Setup** | Establish baseline performance | สร้างเส้นฐานประสิทธิภาพ |
| **After Decomposition Changes** | Re-evaluate load balance | ประเมินความสมดุลของภาระงานใหม่ |
| **Scaling Studies** | Check speedup/efficiency curves | ตรวจสอบกราฟการเพิ่มความเร็ว/ประสิทธิภาพ |
| **Performance Degradation** | Diagnose bottlenecks | วินิจฉัยปัญหาคอขวด |
| **Pre-Production Runs** | Validate resource allocation | ตรวจสอบการจัดสรรทรัพยากร |

---

## 3. How to Monitor Performance | วิธีการตรวจสอบประสิทธิภาพ

### 3.1 Built-in OpenFOAM Monitoring Tools | เครื่องมือตรวจสอบในตัว OpenFOAM

#### 3.1.1 Basic Timing | การจับเวลาพื้นฐาน

```bash
# Wall-clock time with system time command
# เวลาจริงด้วยคำสั่ง time ของระบบ
time mpirun -np 4 simpleFoam -parallel

# Output includes:
# - real: wall-clock time
# - user: CPU time in user mode
# - sys: CPU time in system mode
```

#### 3.1.2 Log File Analysis | การวิเคราะห์ไฟล์บันทึก

**Extract Execution Time** | **แยกเวลาการประมวลผล:**

```bash
# Last 5 execution time entries
# 5 รายการสุดท้ายของเวลาประมวลผล
grep 'ExecutionTime' log.simpleFoam | tail -5

# Get final execution time
# รับเวลาประมวลผลสุดท้าย
grep 'ExecutionTime' log.simpleFoam | tail -1

# Clock time summary
# สรุปเวลานาฬิกา
grep 'ClockTime' log.simpleFoam | tail -1
```

**Typical Output Format** | **รูปแบบผลลัพธ์ทั่วไป:**

```
ExecutionTime = 1234.56 s  ClockTime = 1300 s
```

#### 3.1.3 Residual Monitoring | การตรวจสอบค่าเหลือ

```bash
# Extract residuals to separate files
# แยกค่าเหลือออกเป็นไฟล์แยก
foamLog log.simpleFoam

# Creates logs/ directory with:
# สร้างไดเรกทอรี logs/ พร้อมด้วย:
# - logs/p_0, p_1, ... (pressure residuals)
# - logs/Ux_0, Uy_0, Uz_0 (velocity residuals)
# - logs/k_0, epsilon_0 (turbulence residuals)

# Quick plot with gnuplot
# พล็อตเร็วด้วย gnuplot
gnuplot -e "plot 'logs/p_0' w l title 'Pressure Residual'; pause -1"

# Multi-variable plot
# พล็อตหลายตัวแปร
gnuplot -e "
    plot 'logs/p_0' w l title 'p', \
         'logs/Ux_0' w l title 'Ux', \
         'logs/k_0' w l title 'k';
    pause -1
"
```

#### 3.1.4 Load Balance Analysis | การวิเคราะห์ความสมดุลของภาระงาน

```bash
# Per-processor execution time comparison
# เปรียบเทียบเวลาประมวลผลต่อโปรเซสเซอร์
for p in processor*/; do
    echo "===1$p ==="
    grep 'ExecutionTime'1$p/log.* 2>/dev/null | tail -1
done

# Calculate load balance metric (difference percentage)
# คำนวณเมตริกความสมดุลของภาระงาน (เปอร์เซ็นต์ความแตกต่าง)
mpirun -np 4 solver -parallel 2>&1 | \
    grep -E 'ExecutionTime|ClockTime' | \
    awk '{print1$3}' | \
    sort -n | \
    awk '{max=$NF; min=$1; print "Imbalance:", (max-min)/max*100 "%"}'
```

#### 3.1.5 Memory Usage Monitoring | การตรวจสอบการใช้หน่วยความจำ

```bash
# Detailed memory statistics
# สถิติหน่วยความจำโดยละเอียด
/usr/bin/time -v mpirun -np 4 simpleFoam -parallel

# Key metrics to look for:
# เมตริกสำคัญที่ต้องดู:
# - Maximum resident set size: peak memory usage
# - Average resident set size: typical memory usage
# - Major page faults: indicate memory pressure

# Real-time monitoring with top
# ตรวจสอบแบบเรียลไทม์ด้วย top
top -b -n 1 | grep -E 'simpleFoam|COMMAND'

# Memory per processor (if running separate)
# หน่วยความจำต่อโปรเซสเซอร์ (หากรันแยก)
ps aux | grep simpleFoam | awk '{print1$6/1024 " MB"}'
```

---

### 3.2 Advanced Monitoring with PyFoam | การตรวจสอบขั้นสูงด้วย PyFoam

#### 3.2.1 Installation | การติดตั้ง

```bash
# Using pip
pip install PyFoam

# Verify installation
from PyFoam import __version__
print(__version__)
```

#### 3.2.2 PlotRunner for Real-time Monitoring | PlotRunner สำหรับการตรวจสอบแบบเรียลไทม์

```bash
# Automatic plotting during solver execution
# พล็อตอัตโนมัติระหว่างการทำงานของตัวแก้สมการ
pyFoamPlotRunner.py --progress simpleFoam -parallel

# Generates live plots for:
# สร้างพล็อตสดสำหรับ:
# - Residuals convergence
# - Execution time per timestep
# - Courant number evolution
```

#### 3.2.3 Log File Analysis with PyFoam | การวิเคราะห์ไฟล์บันทึกด้วย PyFoam

```bash
# Extract solver statistics
# แยกสถิติตัวแก้สมการ
pyFoamPlotStatistics.py log.simpleFoam

# Custom residual plotting
# พล็อตค่าเหลือแบบกำหนดเอง
pyFoamPlotResiduals.py --log log.simpleFoam \
    --fields "(p|U|k|epsilon)" \
    --output residuals.png

# Timeline analysis
# การวิเคราะห์ไทม์ไลน์
pyFoamTimelinePlot.py log.simpleFoam
```

---

### 3.3 Speedup and Efficiency Analysis | การวิเคราะห์การเพิ่มความเร็วและประสิทธิภาพ

#### 3.3.1 Key Metrics Definition | นิยามตัวชี้วัดสำคัญ

**Speedup (S)** | **การเพิ่มความเร็ว (S):**

```
S(n) = T₁ / Tₙ
```

Where:
- `T₁` = Execution time with 1 processor
- `Tₙ` = Execution time with n processors

**Efficiency (E)** | **ประสิทธิภาพ (E):**

```
E(n) = S(n) / n × 100%
```

Where:
- `n` = Number of processors
- `S(n)` = Speedup with n processors

#### 3.3.2 Practical Scaling Study | การศึกษาการสเกลจริง

```bash
#!/bin/bash
# scaling_study.sh - Automated scaling analysis

# Baseline: 1 core
T1=$(mpirun -np 1 simpleFoam -parallel 2>&1 | \
     grep 'ExecutionTime' | tail -1 | \
     awk '{print1$3}')

# Test multiple core counts
for cores in 2 4 8 16 32; do
    Tn=$(mpirun -np1$cores simpleFoam -parallel 2>&1 | \
         grep 'ExecutionTime' | tail -1 | \
         awk '{print1$3}')
    
    S=$(echo "scale=2;1$T1 /1$Tn" | bc)
    E=$(echo "scale=2;1$S /1$cores * 100" | bc)
    
    echo "$cores cores: T=$Tn s, Speedup=$Sx, Efficiency=$E%"
done
```

#### 3.3.3 Interpreting Results | การตีความผลลัพธ์

| Efficiency Range | Interpretation | การตีความ |
|-----------------|----------------|--------------|
| **> 80%** | Excellent scaling | การสเกลยอดเยี่ยม |
| **60-80%** | Good scaling | การสเกลดี |
| **40-60%** | Acceptable but check bottlenecks | ยอมรับได้แต่ตรวจสอบปัญหาคอขวด |
| **< 40%** | Poor scaling, investigate decomposition | การสเกลแย่ ตรวจสอบการแบ่งโดเมน |

**Typical Speedup Behavior** | **พฤติกรรมการเพิ่มความเร็วทั่วไป:**

```
Ideal (Linear)     Actual (Typical)
    |                    /
S = |                  /
    |                /
    |              _/
    |          _ _/
    |    _ _ _/
    +----------------- n
        (cores)
```

---

### 3.4 Performance Visualization Techniques | เทคนิคการแสดงผลประสิทธิภาพ

#### 3.4.1 Gnuplot Scripts | สคริปต์ Gnuplot

**Speedup/Efficiency Plot** | **พล็อตการเพิ่มความเร็ว/ประสิทธิภาพ:**

```bash
# Create data file: scaling.dat
# สร้างไฟล์ข้อมูล: scaling.dat
cat > scaling.dat << EOF
# cores  time(s)  speedup  efficiency(%)
1        1200     1.00     100.0
2        620      1.94     96.8
4        340      3.53     88.2
8        200      6.00     75.0
16       130      9.23     57.7
32       100      12.00    37.5
EOF

# Plotting script
# สคริปต์พล็อต
gnuplot << EOF
set terminal pngcairo size 800,600 enhanced font 'Arial,12'
set output 'scaling_analysis.png'
set multiplot layout 1,2

# Speedup plot
set title "Parallel Speedup"
set xlabel "Number of Cores"
set ylabel "Speedup (S)"
plot 'scaling.dat' u 1:3 w lp pt 7 ps 1.5 lc 'blue' \
     title 'Actual Speedup', \
     x w l lc 'gray' dt 2 title 'Ideal (Linear)'

# Efficiency plot
set title "Parallel Efficiency"
set xlabel "Number of Cores"
set ylabel "Efficiency (%)"
plot 'scaling.dat' u 1:4 w lp pt 7 ps 1.5 lc 'red' \
     title 'Efficiency', \
     100 w l lc 'gray' dt 2 title 'Ideal (100%)'

unset multiplot
EOF
```

**Residual Convergence Plot** | **พล็อตการลู่เข้าของค่าเหลือ:**

```bash
# After running foamLog
# หลังจากรัน foamLog
gnuplot << EOF
set terminal pngcairo size 1000,600 enhanced font 'Arial,10'
set output 'convergence.png'
set logscale y
set format y "10^{%L}"
set xlabel "Iteration"
set ylabel "Residual"
set title "Solver Convergence History"
set key top right

plot 'logs/p_0' w l lw 2 lc 'blue' title 'Pressure', \
     'logs/Ux_0' w l lw 2 lc 'red' title 'Ux', \
     'logs/Uy_0' w l lw 2 lc 'green' title 'Uy', \
     'logs/Uz_0' w l lw 2 lc 'orange' title 'Uz'
EOF
```

#### 3.4.2 Python Visualization | การแสดงผลด้วย Python

```python
#!/usr/bin/env python3
# plot_scaling.py - Advanced scaling visualization

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline

# Data from scaling study
cores = np.array([1, 2, 4, 8, 16, 32])
times = np.array([1200, 620, 340, 200, 130, 100])
speedup = times[0] / times
efficiency = speedup / cores * 100

# Create figure
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Speedup plot
ax1.plot(cores, speedup, 'bo-', linewidth=2, markersize=8, label='Actual')
ax1.plot(cores, cores, 'k--', linewidth=1.5, label='Ideal Linear')
ax1.fill_between(cores, speedup, cores, alpha=0.2, color='red')
ax1.set_xlabel('Number of Cores', fontsize=12)
ax1.set_ylabel('Speedup (S)', fontsize=12)
ax1.set_title('Parallel Speedup Analysis', fontsize=14, fontweight='bold')
ax1.grid(True, alpha=0.3)
ax1.legend(fontsize=11)

# Efficiency plot
ax2.plot(cores, efficiency, 'rs-', linewidth=2, markersize=8)
ax2.axhline(y=80, color='green', linestyle='--', linewidth=1, label='Good (>80%)')
ax2.axhline(y=60, color='orange', linestyle='--', linewidth=1, label='Fair (60-80%)')
ax2.axhline(y=40, color='red', linestyle='--', linewidth=1, label='Poor (<40%)')
ax2.set_xlabel('Number of Cores', fontsize=12)
ax2.set_ylabel('Efficiency (%)', fontsize=12)
ax2.set_title('Parallel Efficiency Analysis', fontsize=14, fontweight='bold')
ax2.grid(True, alpha=0.3)
ax2.legend(fontsize=11)
ax2.set_ylim([0, 110])

plt.tight_layout()
plt.savefig('performance_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

# Print summary
print("=== Performance Summary ===")
print(f"Optimal core count: {cores[np.argmax(efficiency)]} cores")
print(f"Best efficiency: {max(efficiency):.1f}%")
```

---

### 3.5 Common Bottleneck Identification | การระบุปัญหาคอขวดทั่วไป

#### 3.5.1 Communication Overhead | ค่าใช้จ่ายในการสื่อสาร

**Symptoms** | **อาการ:**

```bash
# Poor scaling despite balanced mesh
# การสเกลแยะแม้ว่า mesh จะสมดุล
# Time per timestep increases with more cores
# เวลาต่อ timestep เพิ่มขึ้นเมื่อใช้คอร์เพิ่ม

# Check communication time in log
# ตรวจสอบเวลาการสื่อสารใน log
grep -i "communication" log.simpleFoam
grep -i "mpi" log.simpleFoam
```

**Diagnosis** | **การวินิจฉัย:**

```bash
# Profile MPI communication
# โพรไฟล์การสื่อสาร MPI
mpirun -np 8 -mca pml_ob1_verbose 30 simpleFoam -parallel 2>&1 | \
    grep -E "sent|received|bytes"

# Check processor boundary size
# ตรวจสอบขนาดขอบเขตโปรเซสเซอร์
for proc in processor*/; do
    echo "$proc:1$(grep -c 'boundary'1$proc/points 2>/dev/null || echo 0) faces"
done
```

**Solutions** | **แนวทางแก้ไข:**

- Use `scotch` decomposition with higher weight for processor boundaries
| ใช้การแบ่งโดเมน `scotch` พร้อมน้ำหนักสูงสำหรับขอบเขตโปรเซสเซอร์

- Increase cells per processor ratio
| เพิ่มอัตราส่วนเซลล์ต่อโปรเซสเซอร์

- Consider larger cells (reduce mesh resolution if possible)
| พิจารณาเซลล์ที่ใหญ่ขึ้น (ลดความละเอียด mesh ถ้าเป็นไปได้)

#### 3.5.2 I/O Bottleneck | ปัญหาคอขวด I/O

**Symptoms** | **อาการ:**

```bash
# Long write times in log
# เวลาเขียนนานใน log
grep "Write" log.simpleFoam

# High CPU wait time
# เวลารอสูง CPU
iostat -x 1 5  # during simulation

# Disk saturation
# ดิสก์เต็ม
df -h
```

**Solutions** | **แนวทางแก้ไข:**

```bash
# Reduce write frequency in controlDict
# ลดความถี่ในการเขียนใน controlDict
writeControl    timeStep;
writeInterval   100;  # instead of 10

# Disable unnecessary fields
# ปิดฟิลด์ที่ไม่จำเป็น
// In controlDict
functions
{
    // Comment out field exports not needed
    // ใส่ comment การ export ฟิลด์ที่ไม่ต้องการ
}

# Use parallel file system (Lustre, GPFS)
# ใช้ระบบไฟล์แบบขนาน (Lustre GPFS)
```

#### 3.5.3 Load Imbalance | ความไม่สมดุลของภาระงาน

**Symptoms** | **อาการ:**

```bash
# Significant execution time differences
# ความแตกต่างของเวลาประมวลผลอย่างมีนัยสำคัญ
# Calculate max time difference:
max_time=$(for p in processor*/; do
    grep 'ExecutionTime'1$p/log.* 2>/dev/null | tail -1 | awk '{print1$3}'
done | sort -n | tail -1)

min_time=$(for p in processor*/; do
    grep 'ExecutionTime'1$p/log.* 2>/dev/null | tail -1 | awk '{print1$3}'
done | sort -n | head -1)

imbalance=$(echo "scale=1; ($max_time -1$min_time) /1$max_time * 100" | bc)
echo "Load Imbalance:1$imbalance%"

# If > 10%, consider re-decomposition
# หาก > 10% พิจารณาแบ่งโดเมนใหม่
```

**Solutions** | **แนวทางแก้ไข:**

```bash
# Try different decomposition methods
# ลองวิธีการแบ่งโดเมนที่แตกต่างกัน

# Simple (fast, may not balance well)
decomposePar -method simple

# Scotch (recommended for complex geometries)
decomposePar -method scotch

# Hierarchical (for hybrid parallelization)
decomposePar -method hierarchical \
    -decompositionMethod scotch \
    -numberOfSubdomains 8
```

#### 3.5.4 Memory Issues | ปัญหาหน่วยความจำ

**Symptoms** | **อาการ:**

- Simulation crashes with "out of memory" errors
| การจำลองขัดข้องด้วยข้อผิดพลาด "out of memory"

- Swap usage increases during simulation
| การใช้ swap เพิ่มขึ้นระหว่างการจำลอง

- Performance degradation over time
| ประสิทธิภาพลดลงตามเวลา

**Solutions** | **แนวทางแก้ไข:**

```bash
# Monitor memory in real-time
# ตรวจสอบหน่วยความจำแบบเรียลไทม์
watch -n 1 'ps aux | grep simpleFoam | awk "{sum+=\$6} END {print "Total:", sum/1024, "MB"}"'

# Reduce memory usage:
# ลดการใช้หน่วยความจำ:

# 1. Reduce mesh resolution
# ลดความละเอียด mesh

# 2. Use fewer processors with more memory per processor
# ใช้โปรเซสเซอร์น้อยลงแต่มีหน่วยความจำมากกว่าต่อโปรเซสเซอร์

# 3. Optimize solver settings (e.g., GAMG instead of PCG)
# ปรับแต่งการตั้งค่าตัวแก้สมการ (เช่น GAMG แทน PCG)
```

---

## 4. Practical Examples | ตัวอย่างการปฏิบัติจริง

### Example 1: Complete Monitoring Workflow | ขั้นตอนการตรวจสอบที่สมบูรณ์

```bash
#!/bin/bash
# complete_monitoring.sh - End-to-end performance monitoring

CASE="myCase"
SOLVER="simpleFoam"
CORES=(1 2 4 8)

echo "=== Starting Performance Monitoring ==="
date

# 1. Check decomposition
# ตรวจสอบการแบ่งโดเมน
echo "1. Checking decomposition..."
decomposePar > decompose.log 2>&1
for proc in processor*/; do
    cells=$(grep "^nCells:"1$proc/*/polyMesh/blockMeshDict 2>/dev/null || echo "0")
    echo "$proc:1$cells cells"
done

# 2. Run solver with timing
# รันตัวแก้สมการพร้อมจับเวลา
echo "2. Running solver with1${CORES[2]} cores..."
/usr/bin/time -v mpirun -np1${CORES[2]}1$SOLVER -parallel \
    > log.$SOLVER 2>&1

# 3. Extract performance metrics
# แยกเมตริกประสิทธิภาพ
echo "3. Extracting metrics..."
grep 'ExecutionTime' log.$SOLVER | tail -5
grep 'ClockTime' log.$SOLVER | tail -1

# 4. Check residuals
# ตรวจสอบค่าเหลือ
foamLog log.$SOLVER
echo "Residuals extracted to logs/"

# 5. Analyze load balance
# วิเคราะห์ความสมดุลของภาระงาน
echo "5. Load balance analysis:"
for p in processor*/; do
    exec_time=$(grep 'ExecutionTime'1$p/log.* 2>/dev/null | tail -1 | awk '{print1$3}')
    echo "$p:1$exec_time s"
done

# 6. Memory summary
# สรุปหน่วยความจำ
echo "6. Memory usage:"
grep -E "Maximum resident|Average resident" \
    /usr/bin/time -v mpirun -np1${CORES[2]}1$SOLVER -parallel 2>&1 | \
    grep -A1 "resident"

# 7. Generate plots
# สร้างพล็อต
echo "7. Generating visualization..."
python3 plot_scaling.py  # (from Section 3.4.2)

echo "=== Monitoring Complete ==="
```

### Example 2: Identifying and Fixing Load Imbalance | การระบุและแก้ไขความไม่สมดุลของภาระงาน

```bash
#!/bin/bash
# diagnose_imbalance.sh

# Step 1: Measure current imbalance
# ขั้นตอนที่ 1: วัดความไม่สมดุลปัจจุบัน
echo "Measuring current load balance..."
times=()
for p in processor*/; do
    t=$(grep 'ExecutionTime'1$p/log.* 2>/dev/null | \
        tail -1 | awk '{print1$3}')
    times+=($t)
    echo "$p:1${t}s"
done

max_time=$(printf "%s\n" "${times[@]}" | sort -n | tail -1)
min_time=$(printf "%s\n" "${times[@]}" | sort -n | head -1)
imbalance=$(echo "scale=1; ($max_time -1$min_time) /1$max_time * 100" | bc)

echo "Current imbalance:1$imbalance%"

if ((1$(echo "$imbalance > 10" | bc -l) )); then
    echo "WARNING: Poor load balance detected!"
    
    # Step 2: Try scotch decomposition
    # ขั้นตอนที่ 2: ลองการแบ่งโดเมน scotch
    echo "Re-decomposing with scotch..."
    rm -rf processor*
    decomposePar -method scotch > decompose_scotch.log 2>&1
    
    # Step 3: Re-run and measure
    # ขั้นตอนที่ 3: รันใหม่และวัด
    mpirun -np 8 simpleFoam -parallel > log.new 2>&1
    
    # Step 4: Verify improvement
    # ขั้นตอนที่ 4: ตรวจสอบการปรับปรุง
    echo "Measuring new load balance..."
    # (repeat time measurement)
    # (วัดเวลาซ้ำ)
else
    echo "Load balance is acceptable."
fi
```

---

## 5. Troubleshooting Guide | คู่มือการแก้ปัญหา

### 5.1 Performance Issues | ปัญหาประสิทธิภาพ

| Problem | Symptom | Solution | วิธีแก้ไข |
|---------|---------|----------|-----------|
| **Poor Scaling** | Speedup < 50% of ideal | Check decomposition method, cell count per processor | ตรวจสอบวิธีแบ่งโดเมน จำนวนเซลล์ต่อโปรเซสเซอร์ |
| **High Communication** | Efficiency drops with more cores | Use scotch, reduce processor boundaries | ใช้ scotch ลดขอบเขตโปรเซสเซอร์ |
| **I/O Bottleneck** | Long write times | Reduce write frequency, use parallel I/O | ลดความถี่ในการเขียน ใช้ I/O แบบขนาน |
| **Memory Exhaustion** | Crash, swap usage | Reduce cores, decrease mesh resolution | ลดโปรเซสเซอร์ ลดความละเอียด mesh |
| **Residual Stagnation** | No convergence | Check time step, boundary conditions, mesh quality | ตรวจสอบขั้นตอนเวลา เงื่อนไขขอบเขต คุณภาพ mesh |

### 5.2 Diagnostic Commands | คำสั่งวินิจฉัย

```bash
# Full diagnostic suite
# ชุดวินิจฉัยครบวงจร
diagnose_performance() {
    echo "=== Performance Diagnostic Report ==="
    echo "Date:1$(date)"
    echo ""
    
    # 1. System info
    echo "1. System Information:"
    lscpu | grep -E "CPU\(s\)|Thread|Core|Socket"
    free -h
    echo ""
    
    # 2. Case info
    echo "2. Case Information:"
    echo "Cells:1$(checkMesh | grep 'cells:' | awk '{print1$2}')"
    echo "Processors:1$(ls -d processor* | wc -l)"
    echo ""
    
    # 3. Performance metrics
    echo "3. Performance Metrics:"
    grep 'ExecutionTime' log.* | tail -1
    grep 'ClockTime' log.* | tail -1
    echo ""
    
    # 4. Load balance
    echo "4. Load Balance:"
    for p in processor*/; do
        t=$(grep 'ExecutionTime'1$p/log.* 2>/dev/null | tail -1 | awk '{print1$3}')
        echo "$p:1$t s"
    done
    echo ""
    
    # 5. Residual status
    echo "5. Latest Residuals:"
    tail -n 1 logs/p_0 2>/dev/null || echo "No residual data"
    echo ""
    
    echo "=== End Report ==="
}

# Run diagnostic
# รันการวินิจฉัย
diagnose_performance > diagnostic_report.txt
cat diagnostic_report.txt
```

---

## 6. Key Takeaways | สรุปสำคัญ

### Essential Concepts | แนวคิดสำคัญ

✅ **WHAT** | Performance monitoring involves tracking execution time, residuals, load balance, memory, and communication overhead
| การตรวจสอบประสิทธิภาพเกี่ยวข้องกับการติดตามเวลาประมวลผล ค่าเหลือ ความสมดุลของภาระงาน หน่วยความจำ และค่าใช้จ่ายในการสื่อสาร

✅ **WHY** | Monitoring enables bottleneck identification, resource optimization, and quality assurance for production simulations
| การตรวจสอบช่วยให้สามารถระบุปัญหาคอขวด ปรับปรุงทรัพยากร และรับรองคุณภาพสำหรับการจำลองเชิงผลิต

✅ **HOW** | Use built-in tools (time, grep, foamLog), PyFoam for advanced analysis, and custom scripts for visualization
| ใช้เครื่องมือในตัว (time grep foamLog) PyFoam สำหรับการวิเคราะห์ขั้นสูง และสคริปต์กำหนดเองสำหรับการแสดงผล

### Performance Checklist | รายการตรวจสอบประสิทธิภาพ

- [ ] Baseline performance measured (1 core execution time)
| [ ] วัดประสิทธิภาพพื้นฐาน (เวลาประมวลผล 1 คอร์)

- [ ] Scaling study conducted (2, 4, 8, 16+ cores)
| [ ] ทำการศึกษาการสเกล (2, 4, 8, 16+ คอร์)

- [ ] Efficiency > 60% for optimal core count
| [ ] ประสิทธิภาพ > 60% สำหรับจำนวนคอร์ที่เหมาะสม

- [ ] Load imbalance < 10%
| [ ] ความไม่สมดุลของภาระงาน < 10%

- [ ] Residuals monitored and converging
| [ ] ติดตามค่าเหลือและลู่เข้า

- [ ] Memory usage within limits
| [ ] การใช้หน่วยความจำอยู่ในขีดจำกัด

- [ ] Visualization generated for analysis
| [ ] สร้างการแสดงผลสำหรับการวิเคราะห์

### Quick Reference Command Summary | สรุปคำสั่งอ้างอิง

```bash
# Timing
# การจับเวลา
time mpirun -np 4 solver -parallel
/usr/bin/time -v mpirun -np 4 solver -parallel

# Residuals
# ค่าเหลือ
foamLog log.solver
gnuplot -e "plot 'logs/p_0' w l"

# Load Balance
# ความสมดุลของภาระงาน
for p in processor*/; do grep ExecutionTime1$p/log.* | tail -1; done

# Memory
# หน่วยความจำ
/usr/bin/time -v mpirun -np 4 solver -parallel 2>&1 | grep "resident"

# PyFoam
# PyFoam
pyFoamPlotRunner.py --progress solver -parallel
pyFoamPlotStatistics.py log.solver
```

---

## 7. Related Reading | บทความที่เกี่ยวข้อง

### Prerequisite Reading | บทความที่ต้องอ่านก่อน

- **[01_Domain_Decomposition.md](01_Domain_Decomposition.md)** - Understanding domain decomposition strategies and their impact on performance
| ทำความเข้าใจกลยุทธ์การแบ่งโดเมนและผลกระทบต่อประสิทธิภาพ

- **[00_Overview.md](00_Overview.md)** - High-level overview of parallel simulation concepts
| ภาพรวมระดับสูงของแนวคิดการจำลองแบบขนาน

### Next Steps | ขั้นตอนถัดไป

- **[03_Solver_IO_Memory_Optimization.md](03_Solver_IO_Memory_Optimization.md)** - Advanced optimization techniques for solver settings, I/O operations, and memory management
| เทคนิคการปรับปรุงขั้นสูงสำหรับการตั้งค่าตัวแก้สมการ การดำเนินการ I/O และการจัดการหน่วยความจำ

### Additional Resources | ทรัพยากรเพิ่มเติม

- **OpenFOAM User Guide:** Section 4.5 - Running applications in parallel
| คู่มือผู้ใช้ OpenFOAM: หัวข้อ 4.5 - การรันแอปพลิเคชันแบบขนาน

- **PyFoam Documentation:** [https://github.com/PyFoam/PyFoam](https://github.com/PyFoam/PyFoam)
| เอกสาร PyFoam

- **HPC Optimization Best Practices:** Check your institution's HPC documentation
| แนวปฏิบัติที่ดีในการปรับปรุง HPC: ตรวจสอบเอกสาร HPC ของสถาบันของคุณ

---

## 8. Practice Exercises | แบบฝึกหัด

### Exercise 1: Basic Monitoring | การตรวจสอบพื้นฐาน

1. Run `icoFoam` tutorial case with 4 processors
| รันเคส tutorial `icoFoam` ด้วย 4 โปรเซสเซอร์

2. Extract and compare execution times across all processors
| แยกและเปรียบเทียบเวลาประมวลผลทั้งหมดโปรเฟสเซอร์

3. Plot residual convergence for pressure and velocity
| พล็อตการลู่เข้าของค่าเหลือสำหรับความดันและความเร็ว

**Success Criteria:** | **เกณฑ์ความสำเร็จ:**
- Load imbalance < 15%
| ความไม่สมดุลของภาระงาน < 15%

- Residual plot shows clear convergence
| พล็อตค่าเหลือแสดงการลู่เข้าที่ชัดเจน

### Exercise 2: Scaling Study | การศึกษาการสเกล

1. Run the same case with 1, 2, 4, 8, and 16 processors
| รันเคสเดียวกันด้วย 1, 2, 4, 8 และ 16 โปรเซสเซอร์

2. Calculate speedup and efficiency for each configuration
| คำนวณการเพิ่มความเร็วและประสิทธิภาพสำหรับแต่ละการกำหนดค่า

3. Generate speedup/efficiency plots and identify optimal core count
| สร้างพล็อตการเพิ่มความเร็ว/ประสิทธิภาพและระบุจำนวนคอร์ที่เหมาะสม

**Success Criteria:** | **เกณฑ์ความสำเร็จ:**
- Correct speedup/efficiency calculations
| การคำนวณการเพิ่มความเร็ว/ประสิทธิภาพที่ถูกต้อง

- Optimal core count justified by efficiency curve
| จำนวนคอร์ที่เหมาะสมได้รับการยืนยันโดยกราฟประสิทธิภาพ

### Exercise 3: Bottleneck Diagnosis | การวินิจฉัยปัญหาคอขวด

1. Identify the bottleneck in a poorly-scaling case (provided)
| ระบุปัญหาคอขวดในเคสที่สเกลได้แย่ (ให้มา)

2. Apply appropriate solution (decomposition, I/O, memory optimization)
| ใช้วิธีแก้ไขที่เหมาะสม (การแบ่งโดเมน I/O การปรับปรุงหน่วยความจำ)

3. Verify improvement with before/after performance comparison
| ตรวจสอบการปรับปรุงด้วยการเปรียบเทียบประสิทธิภาพก่อน/หลัง

**Success Criteria:** | **เกณฑ์ความสำเร็จ:**
- Bottleneck correctly identified
| ระบุปัญหาคอขวดได้อย่างถูกต้อง

- Measurable performance improvement (>20% speedup or efficiency gain)
| การปรับปรุงประสิทธิภาพที่วัดได้ (>20% การเพิ่มความเร็วหรือการเพิ่มประสิทธิภาพ)

---

## 9. Glossary | อภิธานศัพท์

| Term | Thai | Definition |
|------|------|------------|
| **Speedup** | การเพิ่มความเร็ว | Ratio of single-processor to multi-processor execution time |
| **Efficiency** | ประสิทธิภาพ | Speedup normalized by number of processors (S/n) |
| **Load Balance** | ความสมดุลของภาระงาน | Even distribution of computational work across processors |
| **Residual** | ค่าเหลือ | Numerical error measure indicating convergence |
| **Bottleneck** | ปัญหาคอขวด | Limiting factor reducing overall performance |
| **I/O** | อินพุต/เอาต์พุต | Input/output operations (disk read/write) |
| **Scaling** | การสเกล | Performance behavior as processor count increases |
| **MPI Overhead** | ค่าใช้จ่าย MPI | Communication cost between processors |

---

**Module:** 08_HPC_AND_CLOUD → **Topic:** 02_Performance_Monitoring  
**Status:** 🟢 Complete | **Last Updated:** 2024-12-31  
**Contributors:** OpenFOAM Documentation Team  
**License:** CC BY-SA 4.0