# แนวทางปฏิบัติที่ดีที่สุด (Best Practices for OpenFOAM Utilities)

แนวทางปฏิบัติเหล่านี้ถูกออกแบบมาเพื่อเพิ่มประสิทธิภาพในการทำงาน (Computational Efficiency), ความแม่นยำของผลลัพธ์ (Accuracy) และความสามารถในการทำซ้ำ (Reproducibility) ในโครงการ CFD

---

## 1. การจัดการคุณภาพ Mesh (Mesh Quality Management)

### 1.1 ความสำคัญของคุณภาพ Mesh (Importance of Mesh Quality)

คุณภาพของ Mesh มีผลกระทบโดยตรงต่อ ==ความเสถียรของการคำนวณ (Numerical Stability)== และ ==ความแม่นยำของผลลัพธ์ (Solution Accuracy)== ใน OpenFOAM คุณภาพที่ไม่ดีอาจทำให้เกิดปัญหาต่อไปนี้:

- **Solver Divergence**: การแก้สมการไม่ลู่เข้าสู่คำตอบ
- **Unphysical Solutions**: ผลลัพธ์ที่เป็นไปไม่ได้ทางฟิสิกส์ เช่น ความดันติดลบ หรือความเร็วเกินจริง
- **Slow Convergence**: การลู่เข้าช้าลงอย่างมาก

### 1.2 มาตรวัดคุณภาพ Mesh ที่สำคัญ (Critical Mesh Quality Metrics)

OpenFOAM ใช้หลายมาตรวัดในการประเมินคุณภาพ Mesh:

#### 1.2.1 Non-orthogonality Angle

คือมุมระหว่างเส้นปกติของผิวเซลล์ (Face Normal) กับเส้นเชื่อมระหว่างเซลล์ (Cell-to-Cell Vector)

$$ \theta_{non-orth} = \arccos\left(\frac{\mathbf{S}_f \cdot \mathbf{d}}{|\mathbf{S}_f| |\mathbf{d}|}\right) $$

เมื่อ:
- $\mathbf{S}_f$ = เวกเตอร์ปกติของผิวเซลล์ (Face Area Vector)
- $\mathbf{d}$ = เวกเตอร์เชื่อมระหว่างเซนเตอร์ของเซลล์ (Cell Center Vector)

#### 1.2.2 Skewness

วัดระดับความเบ้อเริ่อของการวางตัวของเซลล์เทียบกับจุดศูนย์กลางเรขาคณิต:

$$ \text{Skewness} = \frac{|\mathbf{d} - 2\mathbf{d}_f|}{|\mathbf{d}|} $$

เมื่อ:
- $\mathbf{d}_f$ = เวกเตอร์จากจุดศูนย์กลางผิว (Face Center) ไปยังจุดจุดกึ่งกลางระหว่างเซลล์ (Interpolation Point)

#### 1.2.3 Aspect Ratio

อัตราส่วนระหว่างขนาดสูงสุดและต่ำสุดของเซลล์:

$$ \text{Aspect Ratio} = \frac{\Delta_{max}}{\Delta_{min}} $$

### 1.3 ลำดับขั้นตอนการตรวจสอบ (Validation Protocol)

คุณควรตรวจสอบคุณภาพ Mesh ในทุกจุดสำคัญของกระบวนการสร้าง เพื่อลดปัญหา Solver Diverge ในภายหลัง

```mermaid
flowchart TD
    A[blockMesh] --> B[checkMesh ครั้งที่ 1]
    B --> C{คุณภาพผ่าน?}
    C -->|ผ่าน| D[snappyHexMesh]
    C -->|ไม่ผ่าน| A
    D --> E[checkMesh ครั้งที่ 2]
    E --> F{คุณภาพผ่าน?}
    F -->|ผ่าน| G[เริ่มการจำลอง]
    F -->|ไม่ผ่าน| D
```
> **Figure 1:** แผนภูมิแสดงขั้นตอนการตรวจสอบคุณภาพเมช (Validation Protocol) ในแต่ละระยะของการสร้างเมช เพื่อให้มั่นใจว่าเมชมีคุณภาพเพียงพอก่อนที่จะเริ่มการจำลองจริง ซึ่งช่วยลดโอกาสในการเกิดปัญหา Solver Divergence

### 1.4 เกณฑ์คุณภาพที่สำคัญ (Critical Metrics)

| มาตรวัด (Metric) | ระดับดีเยี่ยม (Excellent) | ขีดจำกัดที่ยอมรับได้ (Critical) | ผลกระทบเมื่อเกินขีดจำกัด |
|---|---|---|---|
| **Non-orthogonality** | < 50° | < 75° | ความแม่นยำลดลง อาจ Diverge |
| **Skewness** | < 0.5 | < 4.0 | การ Interpolate ไม่แม่นยำ |
| **Aspect Ratio** | < 10 | < 100 | Convergence ช้าลงมาก |

> [!WARNING] เกณฑ์เหล่านี้เป็นค่าทั่วไป
> เกณฑ์ข้างต้นอาจแตกต่างกันไปตาม Solver และโจทย์ปัญหา เช่น:
> - **High-Mach Flow** (supersonic): ต้องการ Aspect Ratio ต่ำกว่า 5
> - **Incompressible Flow**: ยอมรับ Non-orthogonality ได้สูงกว่า

### 1.5 การตรวจสอบ Mesh ด้วย checkMesh (Mesh Validation with checkMesh)

#### 1.5.1 คำสั่งพื้นฐาน

```bash
# NOTE: Synthesized by AI - Verify parameters
checkMesh
```

การรัน `checkMesh` โดยไม่มีอาร์กิวเมนต์จะทำการตรวจสอบคุณภาพพื้นฐาน:

```text
Mesh stats
    points:           524288
    faces:            1572864
    internal faces:   1492260
    cells:            524288
    faces per cell:   6
    boundary patches: 6
    point zones:      0
    face zones:       0
    cell zones:       1
```

#### 1.5.2 การตรวจสอบคุณภาพอย่างละเอียด

```bash
# NOTE: Synthesized by AI - Verify parameters
checkMesh -allGeometry -allTopology
```

#### 1.5.3 ตัวอย่าง Output ที่สำคัญ

```text
Mesh non-orthogonality Max: 69.5 average: 12.3
Non-orthogonality check OK.
***High aspect ratio cells found, Aspect ratio : Max: 85.2
  Writing 102 cells with high aspect ratio to set highAspectRatioCells
```

### 1.6 การปรับปรุงคุณภาพ Mesh (Mesh Quality Improvement)

#### 1.6.1 การตั้งค่าใน `snappyHexMeshDict`

```cpp
// NOTE: Synthesized by AI - Verify parameters
// ไฟล์: system/snappyHexMeshDict

// การควบคุม Non-orthogonality
maxNonOrtho 65;

// การควบคุม Skewness
maxBoundarySkewness 20;
maxInternalSkewness 4;

// การควบคุม Aspect Ratio
maxConcave 80;

// การควบคุม Smoothness
minVol 1e-13;
minVolRatio 0.01;
minTetQuality 1e-30;

// การควบคุม Face ที่ไม่ดี
minArea -1;
minTwist 0.02;
minDeterminant 0.001;
minFaceWeight 0.05;
minVolRatio 0.01;
```

> [!TIP] กลยุทธ์การปรับค่า
> - **maxNonOrtho < 70°**: สำหรับการใช้งานทั่วไป
> - **maxNonOrtho < 50°**: สำหรับการคำนวณที่ต้องการความแม่นยำสูง
> - หากต้องการเพิ่มค่าเหล่านี้ ให้พิจารณาใช้ `nonOrthoCorrection` ใน `fvSchemes`

---

## 2. การเพิ่มประสิทธิภาพการรันขนาน (Parallel Optimization)

### 2.1 หลักการของการคำนวณขนาน (Principles of Parallel Computing)

OpenFOAM ใช้ **Domain Decomposition** ในการแบ่งงานคำนวณ โดยแบ่ง Mesh ออกเป็นส่วนย่อย (Subdomains) และส่งไปประมวลผลบน CPU Cores ต่าง ๆ ประสิทธิภาพของการรันขนานขึ้นอยู่กับ:

$$ \text{Speedup} = \frac{T_{serial}}{T_{parallel}(N)} $$

$$ \text{Parallel Efficiency} = \frac{T_{serial}}{N \cdot T_{parallel}(N)} \times 100\% $$

เมื่อ:
- $T_{serial}$ = เวลาที่ใช้ในการรันแบบ Serial
- $T_{parallel}(N)$ = เวลาที่ใช้ในการรันขนานด้วย $N$ Cores
- $N$ = จำนวน Cores

### 2.1.1 Amdahl's Law

กฎของ Amdahl อธิบายขีดจำกัดของการเพิ่มประสิทธิภาพขนาน:

$$ \text{Speedup}(N) = \frac{1}{(1-P) + \frac{P}{N}} $$

เมื่อ $P$ คือส่วนของโปรแกรมที่สามารถทำงานแบบขนานได้

> [!INFO] ผลกระทบของ Communication
> ใน OpenFOAM ยิ่งใช้ Cores มากขึ้น เวลาที่สูญเสียไปกับการ Communication ระหว่าง Cores จะยิ่งเพิ่มขึ้น ทำให้ Parallel Efficiency ลดลง

### 2.2 กลยุทธ์การย่อยโดเมน (Decomposition Strategy)

#### 2.2.1 วิธีการ Decompose ที่สำคัญ

| วิธีการ (Method) | คำอธิบาย | เหมาะสำหรับ | ความซับซ้อน |
|---|---|---|---|
| **scotch** | อัตโนมัติ ลด Interface | เรขาคณิตซับซ้อน | ต่ำ |
| **simple** | แบ่งตามทิศทาง X, Y, Z | เรขาคณิตสมมาตร | ต่ำมาก |
| **hierarchical** | แบ่งตามลำดับชั้น | ระบบ Cluster | ปานกลาง |
| **manual** | ผู้ใช้กำหนดเอง | กรณีพิเศษ | สูง |

#### 2.2.2 การตั้งค่า Decomposition

```cpp
// NOTE: Synthesized by AI - Verify parameters
// ไฟล์: system/decomposeParDict

method scotch; // แนะนำสำหรับเรขาคณิตที่ซับซ้อน

// หรือใช้ simple method
// method simple;
// numberOfSubdomains 16;
// simpleCoeffs
// {
//     n (4 4 1); // แบ่ง 4x4x1 = 16 subdomains
//     delta 0.001;
// }
```

### 2.3 จำนวนเซลล์ต่อ Core (Cell Count per Core)

แนะนำให้มีจำนวนเซลล์ประมาณ **100,000 - 200,000 เซลล์ต่อ 1 Core** เพื่อประสิทธิภาพสูงสุด

$$ N_{optimal} \approx \frac{N_{cells}}{100,000 \sim 200,000} $$

เหตุผลทางทฤษฎี:
- **ต่ำเกินไป (< 50,000 cells/core)**: Overhead จากการ Communication มากเกินไป
- **สูงเกินไป (> 500,000 cells/core)**: ไม่ได้ประโยชน์จากการรันขนาน

### 2.4 การตรวจสอบความสมดุล (Load Balance)

ใช้สูตรคำนวณความไม่สมดุล (Imbalance):

$$ \text{Imbalance} = \frac{N_{max} - N_{avg}}{N_{avg}} \times 100\% $$

เมื่อ:
- $N_{max}$ = จำนวนเซลล์สูงสุดใน Subdomain ใด ๆ
- $N_{avg}$ = จำนวนเซลล์เฉลี่ยต่อ Subdomain

**เป้าหมาย**: ควรมีค่าน้อยกว่า 10% เพื่อไม่ให้มี CPU ตัวใดตัวหนึ่งต้องรอนานเกินไป

#### 2.4.1 การตรวจสอบ Load Balance

```bash
# NOTE: Synthesized by AI - Verify parameters
decomposePar

# ตรวจสอบจำนวนเซลล์ในแต่ละ processor directory
for i in processor*; do
    echo "$i: $(grep 'cells' $i/polyMesh/owner | wc -l)"
done
```

### 2.5 การรันแบบขนาน (Running Parallel Simulations)

#### 2.5.1 คำสั่งพื้นฐาน

```bash
# NOTE: Synthesized by AI - Verify parameters
# 1. Decompose the case
decomposePar

# 2. Run solver in parallel
mpirun -np 16 simpleFoam -parallel

# 3. Reconstruct results
reconstructPar
```

#### 2.5.2 การใช้ machinefile

```bash
# NOTE: Synthesized by AI - Verify parameters
# สร้างไฟล์: machinefile
# node1 slots=4
# node2 slots=4
# node3 slots=4
# node4 slots=4

mpirun -np 16 -hostfile machinefile simpleFoam -parallel
```

### 2.6 การปรับแต่ง Solver สำหรับขนาน (Parallel-Specific Tuning)

```cpp
// NOTE: Synthesized by AI - Verify parameters
// ไฟล์: system/fvSolution

solvers
{
    p
    {
        solver          GAMG;
        tolerance       1e-06;
        relTol          0.01;
        smoother        GaussSeidel;
        nPreSweeps      0;
        nPostSweeps     2;
        cacheAgglomeration on;
        agglomerator    faceAreaPair;
        mergeLevels     1;
        nCellsInCoarsestLevel 50;
    }
}
```

> [!TIP] การเลือก Solver
> - **GAMG**: ดีสำหรับ Mesh ขนาดใหญ่ (หลายล้านเซลล์) และการรันขนาน
> - **PCG**: ดีสำหรับ Mesh ขนาดเล็ก-ปานกลาง
> - **smoothSolver**: ดีสำหรับ Non-orthogonal Mesh สูง

---

## 3. ประสิทธิภาพการ Post-Processing

### 3.1 การเลือกสรร Time Directories (Selective Time Processing)

OpenFOAM เก็บผลลัพธ์ในโฟลเดอร์ตามเวลา (Time Directories) เช่น `0/`, `0.1/`, `0.2/`, ... การประมวลผลทั้งหมดจะใช้เวลาและพื้นที่มหาศาล

### 3.2 การใช้ธง `-latestTime`

สำหรับการทำงานที่ต้องการความรวดเร็ว เช่น การตรวจสอบการบรรจบของผลลัพธ์ (Convergence) ให้ใช้ธง `-latestTime` เสมอ เพื่อประมวลผลเฉพาะโฟลเดอร์เวลาล่าสุดแทนที่จะทำทั้งหมด

```bash
# NOTE: Synthesized by AI - Verify parameters
# ประมวลผลเฉพาะ latest time
postProcess -func "mag(U)" -latestTime

# ต่างจากการรันทั้งหมด
postProcess -func "mag(U)"  # จะประมวลผลทุก time directory
```

### 3.3 การใช้ธง `-time`

```bash
# NOTE: Synthesized by AI - Verify parameters
# ประมวลผลช่วงเวลาที่ต้องการ
postProcess -func "mag(U)" -time '0:0.5'       # ตั้งแต่ 0 ถึง 0.5
postProcess -func "mag(U)" -time '0:'          # ตั้งแต่ 0 ถึง สิ้นสุด
postProcess -func "mag(U)" -time ':0.5'        # ตั้งแต่เริ่มต้น ถึง 0.5
postProcess -func "mag(U)" -time '0.1,0.2,0.5' # เฉพาะ 0.1, 0.2, และ 0.5
```

### 3.4 ฟังก์ชัน Post-Process ที่มีประโยชน์ (Useful Post-Process Functions)

#### 3.4.1 การคำนวณ yPlus

```bash
# NOTE: Synthesized by AI - Verify parameters
postProcess -func yPlus -latestTime
```

yPlus ถูกนิยามว่า:

$$ y^+ = \frac{y u_\tau}{\nu} = \frac{y \sqrt{\tau_w / \rho}}{\nu} $$

เมื่อ:
- $y$ = ระยะห่างจากผิว (Wall Distance)
- $u_\tau$ = ความเร็วเฉือน (Friction Velocity)
- $\nu$ = ความหนืดจลน์ (Kinematic Viscosity)
- $\tau_w$ = แรงเฉือนผิว (Wall Shear Stress)

#### 3.4.2 การคำนวณ Wall Shear Stress

```bash
# NOTE: Synthesized by AI - Verify parameters
postProcess -func wallShearStress -latestTime
```

$$ \tau_w = \mu \left(\frac{\partial u_t}{\partial y}\right)_{y=0} $$

#### 3.4.3 การคำนวณ Vorticity

```bash
# NOTE: Synthesized by AI - Verify parameters
postProcess -func vorticity -latestTime
```

$$ \boldsymbol{\omega} = \nabla \times \mathbf{U} $$

สำหรับ 2D:
$$ \omega_z = \frac{\partial v}{\partial x} - \frac{\partial u}{\partial y} $$

### 3.5 การรัน Post-processing แบบขนาน

ในกรณีที่ Case มีขนาดใหญ่มาก เราสามารถรันเครื่องมือวิเคราะห์แบบขนานได้เช่นกัน:

```bash
# NOTE: Synthesized by AI - Verify parameters
mpirun -np 4 postProcess -func yPlus -parallel
```

### 3.6 การสร้างฟังก์ชัน Post-Process แบบ Custom

```cpp
// NOTE: Synthesized by AI - Verify parameters
// ไฟล์: system/customPostProcess

myVelocityMag
{
    // ใช้ฟังก์ชัน built-in
    functionObjectLibs ("libfieldFunctionObjects.so");
    type            volMag;
    writeFields     true;
}
```

### 3.7 การใช้ `sampleDict` สำหรับ Sampling ข้อมูล

```cpp
// NOTE: Synthesized by AI - Verify parameters
// ไฟล์: system/sampleDict

type sets;
interpolationScheme cellPoint;

sets
(
    centerline
    {
        type uniform;
        axis x;
        start (0 0 0);
        end (1 0 0);
        nPoints 100;
    }
);

fields (U p k epsilon);
```

```bash
# NOTE: Synthesized by AI - Verify parameters
sample -latestTime
```

---

## 4. การจัดการความสมบูรณ์ของข้อมูล (Data Integrity)

### 4.1 ความสำคัญของความสมบูรณ์ของข้อมูล

ความสมบูรณ์ของข้อมูลมีความสำคัญอย่างยิ่งต่อ:
- **Reproducibility**: สามารถทำซ้ำผลลัพธ์ได้
- **Verification**: สามารถตรวจสอบความถูกต้องได้
- **Collaboration**: สามารถแชร์งานกับทีมได้

### 4.2 กลยุทธ์การสำรองข้อมูล (Backup Strategy)

#### 4.2.1 Critical Backup

สำรองเฉพาะไฟล์คอนฟิกูเรชันที่จำเป็น:

```bash
# NOTE: Synthesized by AI - Verify parameters
#!/bin/bash
# backup_essentials.sh

CASE_NAME=$(basename $PWD)
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="../backups/${CASE_NAME}_${TIMESTAMP}"

mkdir -p $BACKUP_DIR

# Backup ไฟล์คอนฟิกูเรชัน
cp -r system/ $BACKUP_DIR/
cp -r constant/ $BACKUP_DIR/
cp -r 0/ $BACKUP_DIR/

# Backup สคริปต์
cp -r *.sh $BACKUP_DIR/ 2>/dev/null
cp -r Allw* $BACKUP_DIR/ 2>/dev/null

# Backup log files
mkdir -p $BACKUP_DIR/logs
cp log.* $BACKUP_DIR/logs/ 2>/dev/null

echo "Backup saved to: $BACKUP_DIR"
```

#### 4.2.2 Results Backup

สำรองไฟล์ที่สกัดออกมาแล้ว (โฟลเดอร์ `postProcessing/`) แทนที่จะเก็บ Time directories ทั้งหมดที่รันขนาน

```bash
# NOTE: Synthesized by AI - Verify parameters
#!/bin/bash
# extract_results.sh

# สกัดข้อมูลสำคัญ
postProcess -func yPlus -latestTime
postProcess -func wallShearStress -latestTime

# สร้างไฟล์ CSV สำหรับ plotting
foamListTimes | grep -E '^[0-9]' | tail -1 > latest_time.txt
LATEST_TIME=$(cat latest_time.txt)

# สำรองเฉพาะข้อมูลที่สำคัญ
mkdir -p results_backup
cp postProcessing/*/sets/*/CSV/*/*.csv results_backup/ 2>/dev/null
cp postProcessing/*/graphs/*//*/graphUniform/results.csv results_backup/ 2>/dev/null
```

### 4.3 การใช้ระบบควบคุมเวอร์ชัน (Git)

ใช้ Git เพื่อติดตามการเปลี่ยนแปลงของไฟล์ Dictionary แต่ควรใส่โฟลเดอร์ `processor*`, `VTK/` และไฟล์ผลลัพธ์ขนาดใหญ่ไว้ใน `.gitignore`

#### 4.3.1 ตัวอย่าง .gitignore

```bash
# NOTE: Synthesized by AI - Verify parameters
# ไฟล์: .gitignore

# Processor directories from parallel runs
processor*/
[0-9]*/
processor[0-9]*/

# Post-processing directories
postProcessing/
sets/
graphs/
surfaces/

# VTK files
*.vtk
VTK/

# Log files
log.*
*.log

# Graph files
*.xy

# Backup files
*~
*.bak
*.BAK

# Core dumps
core
core.*

# Temporary files
*.tmp
*.temp
```

#### 4.3.2 การใช้ Git สำหรับ OpenFOAM Projects

```bash
# NOTE: Synthesized by AI - Verify parameters
# 1. เริ่มต้น repository
git init

# 2. สร้าง .gitignore (จากตัวอย่างด้านบน)
# ... (วางเนื้อหา .gitignore)

# 3. เพิ่มไฟล์คอนฟิกูเรชัน
git add system/ constant/ 0/ .gitignore

# 4. Commit ครั้งแรก
git commit -m "Initial commit: base configuration"

# 5. สร้าง branch สำหรับการทดลอง
git checkout -b experiment/higher_resolution

# 6. ทำการเปลี่ยนแปลงและ commit
git add system/blockMeshDict
git commit -m "Increase mesh resolution in boundary layer"

# 7. กลับไป main branch เมื่อต้องการ
git checkout main
```

### 4.4 การตรวจสอบความสมบูรณ์ (Verification)

#### 4.4.1 การตรวจสอบไฟล์ Dictionary

```bash
# NOTE: Synthesized by AI - Verify parameters
# ตรวจสอบ syntax ของไฟล์ dictionary
foamDictionary system/blockMeshDict

# ตรวจสอบ boundary conditions
foamListTimes
foamListBoundaries
```

#### 4.4.2 การเปรียบเทียบ Case

```bash
# NOTE: Synthesized by AI - Verify parameters
#!/bin/bash
# compare_cases.sh

CASE1=$1
CASE2=$2

echo "Comparing $CASE1 vs $CASE2"

# เปรียบเทียบ system/fvSchemes
diff $CASE1/system/fvSchemes $CASE2/system/fvSchemes

# เปรียบเทียบ system/fvSolution
diff $CASE1/system/fvSolution $CASE2/system/fvSolution

# เปรียบเทียบ mesh stats
echo "Mesh stats $CASE1:"
grep -E "points|faces|cells" $CASE1/log.checkMesh 2>/dev/null || echo "No log.checkMesh found"

echo "Mesh stats $CASE2:"
grep -E "points|faces|cells" $CASE2/log.checkMesh 2>/dev/null || echo "No log.checkMesh found"
```

---

## 5. การปรับแต่งประสิทธิภาพ Solver (Solver Performance Tuning)

### 5.1 การเลือก Solver ที่เหมาะสม (Choosing the Right Solver)

การเลือก Solver ที่เหมาะสมมีผลต่อทั้งความแม่นยำและเวลาในการคำนวณ

| ปัญหา (Problem) | Solver ที่แนะนำ | ลักษณะเฉพาะ |
|---|---|---|
| **Laminar, Incompressible** | `simpleFoam` | Steady-state, SIMPLE algorithm |
| **Laminar, Incompressible, Transient** | `pimpleFoam` | Transient, PIMPLE algorithm |
| **Turbulent, RANS** | `kOmegaSST`, `kEpsilon` | เสถียรดี |
| **Turbulent, LES** | `pimpleFoam` + LES model | ต้องการ Mesh ละเอียด |
| **Multiphase (VOF)** | `interFoam` | สำหรับ Free surface |
| **Compressible** | `rhoSimpleFoam`, `rhoPimpleFoam` | พิจารณาความหนาแน่น |

### 5.2 การปรับแต่ง Under-Relaxation Factors

Under-Relaxation Factors ถูกใช้เพื่อป้องกันการ Diverge ในการแก้สมการ Iterative:

$$ \phi^{n+1} = \phi^n + \alpha \left(\phi^* - \phi^n\right) $$

เมื่อ $\alpha$ คือ Under-Relaxation Factor

#### 5.2.1 การตั้งค่าใน `fvSolution`

```cpp
// NOTE: Synthesized by AI - Verify parameters
// ไฟล์: system/fvSolution

relaxationFactors
{
    fields
    {
        p               0.3; // ความดัน - ลดช้าเพื่อเสถียรภาพ
        rho             0.05; // ความหนาแน่น - ลดช้ามาก (ถ้าเป็น compressible)
    }
    equations
    {
        U               0.7; // ความเร็ว - ค่าปานกลาง
        k               0.7; // Turbulence kinetic energy
        epsilon         0.7; // Dissipation rate
    }
}
```

> [!TIP] กลยุทธ์การปรับ Under-Relaxation
> - เริ่มต้นด้วยค่าปานกลาง (p: 0.3, U: 0.7)
> - หาก Diverge: ลดค่าลง (p: 0.2, U: 0.5)
> - หาก Convergence ช้า: เพิ่มค่าขึ้นอย่างระมัดระวัง

### 5.3 การปรับแต่ง Numerical Schemes

#### 5.3.1 การเลือก Discretization Schemes

```cpp
// NOTE: Synthesized by AI - Verify parameters
// ไฟล์: system/fvSchemes

ddtSchemes
{
    default steadyState; // หรือ Euler สำหรับ transient
}

gradSchemes
{
    default Gauss linear;
    grad(p) Gauss linear;
    grad(U) Gauss linear;
}

divSchemes
{
    default none;

    // สำหรับ Convection terms - ขึ้นกับ Mesh และ Physics
    div(phi,U)      bounded Gauss linearUpwindV grad(U); // ดีกว่า upwind
    div(phi,k)      bounded Gauss upwind; // ทนทาน แต่ diffusive
    div(phi,epsilon) bounded Gauss upwind;

    // สำหรับ Diffusion terms
    div((nuEff*dev2(T(grad(U))))) Gauss linear;
}

laplacianSchemes
{
    default Gauss linear corrected; // corrected สำคัญสำหรับ non-orthogonal
}

interpolationSchemes
{
    default linear;
}

snGradSchemes
{
    default corrected; // สำคัญสำหรับ boundary layers
}
```

#### 5.3.2 ผลกระทบของ Schemes ต่อ Accuracy

การเลือก Convection Scheme มีผลต่อความแม่นยำและความเสถียร:

$$ \frac{\partial \phi}{\partial t} + \nabla \cdot (\mathbf{u} \phi) = \Gamma \nabla^2 \phi $$

| Scheme | Order | Numerical Diffusion | Stability |
|---|---|---|---|
| **Upwind** | 1st | สูง | ดีมาก |
| **Linear** | 2nd | ต่ำ | ปานกลาง |
| **LinearUpwindV** | 2nd | ปานกลาง | ดี |
| **QUICK** | 3rd | ต่ำมาก | ต้องปรับค่า |
| **TVD Schemes** | Variable | ต่ำ | ดี |

### 5.4 การตั้งค่า Convergence Criteria

```cpp
// NOTE: Synthesized by AI - Verify parameters
// ไฟล์: system/fvSolution

solvers
{
    p
    {
        solver          GAMG;
        tolerance       1e-06; // Absolute tolerance
        relTol          0.01;  // Relative tolerance (1%)
    }

    U
    {
        solver          smoothSolver;
        smoother        GaussSeidel;
        tolerance       1e-05;
        relTol          0.1;
    }
}
```

> [!INFO] ความหมายของ Tolerance
> - **tolerance**: ค่าสัมบูรณ์ที่ยอมรับได้ (Absolute Residual)
> - **relTol**: ค่าสัมพัทธ์ที่ยอมรับได้ (Relative Residual)
> - เมื่อ Initial Residual < ค่าที่ตั้งไว้ ถือว่า Converged ใน Iteration นั้น

---

## 6. การวินิจฉัยปัญหา (Troubleshooting)

### 6.1 ปัญหาที่พบบ่อยและวิธีแก้ไข

#### 6.1.1 Solver Divergence

```text
--> FOAM FATAL ERROR:
Maximum number of iterations exceeded
```

**วิธีแก้ไข:**

1. ลด Under-Relaxation Factors
2. ตรวจสอบ Mesh Quality (Non-orthogonality, Skewness)
3. เริ่มต้นด้วย Initial Conditions ที่ดีกว่า
4. ใช้ Upwind Schemes ชั่วคราว

#### 6.1.2 การ Convergence ช้า

**วิธีแก้ไข:**

1. เพิ่ม Under-Relaxation Factors (อย่างระมัดระวัง)
2. ใช้ Mesh ที่สม่ำเสมอมากขึ้น
3. ตรวจสอบ Boundary Conditions
4. ใช้ Schemes ที่มีความแม่นยำสูงกว่า

#### 6.1.3 ผลลัพธ์ไม่เป็นทางกายภาพ (Unphysical Results)

เช่น ความดันติดลบ หรือความเร็วสูงผิดปกติ

**วิธีแก้ไข:**

1. ตรวจสอบ Boundary Conditions (โดยเฉพาะ Outlet)
2. ตรวจสอบ Courant Number (Co < 1 สำหรับ explicit solvers)
3. ตรวจสอบ Mesh Quality
4. ลด Time Step สำหรับ Transient Cases

### 6.2 การตรวจสอบ Courant Number

Courant Number (CFL Condition) สำคัญสำหรับความเสถียรของการคำนวณ Transient:

$$ Co = \frac{|\mathbf{U}| \Delta t}{\Delta x} $$

เมื่อ:
- $|\mathbf{U}|$ = ความเร็ว
- $\Delta t$ = Time step
- $\Delta x$ = ขนาดเซลล์

```bash
# NOTE: Synthesized by AI - Verify parameters
# คำนวณ Courant Number
postProcess -func CourantNo -latestTime
```

> [!WARNING] ขีดจำกัด Courant Number
> - **Explicit Solvers**: ต้องมี Co < 1 (หรือ Co < 0.5 สำหรับความเสถียรสูง)
> - **Implicit Solvers**: อาจใช้ Co ได้สูงกว่า แต่แนะนำ Co < 10

### 6.3 การตรวจสอบ Residuals

```bash
# NOTE: Synthesized by AI - Verify parameters
# ดู residuals จาก log file
foamLog log.simpleFoam

# Plot residuals
gnuplot plotResiduals.gnuplot
```

#### 6.3.1 ตัวอย่าง Gnuplot Script

```bash
# NOTE: Synthesized by AI - Verify parameters
# ไฟล์: plotResiduals.gnuplot

set terminal pngcairo size 800,600
set output 'residuals.png'

set logscale y
set xlabel 'Iteration'
set ylabel 'Residual'
set title 'Solver Residuals'

plot "logs/linearSolverP_0" u 1:3 w l t 'p', \
     "logs/linearSolverUx_0" u 1:3 w l t 'Ux', \
     "logs/linearSolverUy_0" u 1:3 w l t 'Uy'
```

---

## 7. Automation และ Workflow (Automation and Workflow)

### 7.1 การสร้าง Automation Scripts

Automation เป็นกุญแจสำคัญในการทำงาน OpenFOAM อย่างมีประสิทธิภาพ

#### 7.1.1 ตัวอย่าง Script: Full Workflow

```bash
# NOTE: Synthesized by AI - Verify parameters
#!/bin/bash
# ไฟล์: runSimulation.sh

set -e  # หยุดเมื่อเจอ error

echo "=== OpenFOAM Simulation Workflow ==="

# 1. Clean case (optional)
echo "Step 1: Cleaning previous results..."
foamCleanTutorials

# 2. Generate mesh
echo "Step 2: Generating mesh..."
blockMesh > log.blockMesh 2>&1
if [ $? -ne 0 ]; then
    echo "ERROR: blockMesh failed. Check log.blockMesh"
    exit 1
fi

# 3. Check mesh
echo "Step 3: Checking mesh quality..."
checkMesh > log.checkMesh 2>&1

# 4. Decompose for parallel
echo "Step 4: Decomposing case..."
decomposePar > log.decomposePar 2>&1

# 5. Run solver
echo "Step 5: Running solver..."
mpirun -np 4 simpleFoam -parallel > log.simpleFoam 2>&1

# 6. Reconstruct
echo "Step 6: Reconstructing results..."
reconstructPar > log.reconstructPar 2>&1

# 7. Post-process
echo "Step 7: Post-processing..."
postProcess -func yPlus -latestTime > log.postProcess 2>&1

echo "=== Simulation Complete ==="
echo "Results available at: $(foamListTimes | tail -1)"
```

### 7.2 การใช้ PyFoam สำหรับ Automation

PyFoam เป็นเครื่องมือ Python สำหรับจัดการ OpenFOAM Cases

```python
# NOTE: Synthesized by AI - Verify parameters
# ไฟล์: automate_case.py

from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
from PyFoam.Execution.BasicRunner import BasicRunner
import os

# 1. แก้ไข fvSchemes
scheme_file = ParsedParameterFile("system/fvSchemes")
scheme_file["divSchemes"]["div(phi,U)"] = "bounded Gauss linearUpwindV grad(U)"
scheme_file.writeFile()

# 2. รัน blockMesh
print("Running blockMesh...")
runner = BasicRunner("blockMesh", silent=False)
runner.start()

# 3. ตรวจสอบผลลัพธ์
if runner.stoppedOK():
    print("blockMesh completed successfully")
else:
    print("blockMesh failed")
```

---

## 8. การวิเคราะห์และ Validation (Analysis and Validation)

### 8.1 การเปรียบเทียบกับ Experimental Data

> **[MISSING DATA]**: Insert specific simulation results/graphs for this section.

เมื่อมีข้อมูลทดลอง สามารถใช้ OpenFOAM เพื่อ Validation ได้:

$$ \text{Error} = \frac{1}{N} \sum_{i=1}^{N} \left|\frac{\phi_{CFD,i} - \phi_{exp,i}}{\phi_{exp,i}}\right| \times 100\% $$

### 8.2 การทำ Grid Convergence Study

เพื่อยืนยันว่าผลลัพธ์ไม่ขึ้นกับ Mesh Resolution:

$$ \phi_i = \phi_{exact} + C h_i^p $$

เมื่อ:
- $\phi_i$ = ผลลัพธ์ที่ Mesh resolution $i$
- $h_i$ = ขนาดเซลล์
- $p$ = Order of convergence

---

## 🎓 สรุปหลักการสำคัญ

### Best Practices Checklist

1. **ตรวจสอบ Mesh อย่างเข้มงวด** ในทุกขั้นตอน
   - ใช้ `checkMesh` หลัง blockMesh และ snappyHexMesh
   - ตรวจสอบ Non-orthogonality < 75°, Skewness < 4.0
   - ปรับปรุง Mesh หากไม่ผ่านเกณฑ์

2. **รันขนานอย่างชาญฉลาด** โดยเลือกจำนวน Core และวิธีการย่อยโดเมนที่เหมาะสม
   - ใช้ 100,000 - 200,000 เซลล์ต่อ Core
   - ใช้ `scotch` method สำหรับเรขาคณิตซับซ้อน
   - ตรวจสอบ Load Balance < 10%

3. **วิเคราะห์ผลอย่างมีเป้าหมาย** โดยประมวลผลเฉพาะข้อมูลที่จำเป็น
   - ใช้ `-latestTime` สำหรับการตรวจสอบรวดเร็ว
   - ใช้ `-time` สำหรับ range ที่ต้องการ
   - รัน Post-processing แบบขนานสำหรับ Cases ใหญ่

4. **จัดการข้อมูลอย่างเป็นระบบ** ผ่านการทำ Automation และ Backup สม่ำเสมอ
   - ใช้ Git สำหรับ configuration files
   - สำรองเฉพาะไฟล์ที่จำเป็น (system/, constant/, 0/)
   - ใช้ `.gitignore` สำหรับไฟล์ขนาดใหญ่

### แนวทางการแก้ปัญหาแบบ Systematic

```mermaid
flowchart TD
    A[เริ่มต้น] --> B[ตรวจสอบ Mesh]
    B --> C{Mesh OK?}
    C -->|ไม่| D[ปรับปรุง Mesh]
    D --> B
    C -->|ใช่| E[เลือก Solver & Schemes]
    E --> F[ตั้งค่า Parameters]
    F --> G[รัน Simulation]
    G --> H{Converge?}
    H -->|ไม่| I[วินิจฉัยปัญหา]
    I --> J[ปรับ Parameters/Mesh]
    J --> G
    H -->|ใช่| K[Post-Processing]
    K --> L[Validation]
    L --> M[เสร็จสิ้น]
```
> **Figure 2:** แนวทางการแก้ปัญหาอย่างเป็นระบบ (Systematic Troubleshooting) ครอบคลุมตั้งแต่การประเมินเมช การเลือกพารามิเตอร์ของ Solver การตรวจสอบความบรรจบ ไปจนถึงการสรุปผลและตรวจสอบความถูกต้องของข้อมูล

---

## References

> [!INFO] แหล่งอ้างอิงเพิ่มเติม
> - OpenFOAM User Guide: https://cfd.direct/openfoam/user-guide/
> - OpenFOAM Programmer's Guide: https://cfd.direct/openfoam/programmers-guide/
> - CFD Online: https://www.cfd-online.com/Forums/openfoam/
> - OpenFOAM Wiki: https://openfoamwiki.net/

---

**[END OF DOCUMENT]**
