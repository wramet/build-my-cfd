# ภาพรวม OpenFOAM Utilities (OpenFOAM Utilities Overview)

OpenFOAM Utilities คือกระดูกสันหลังของการประมวลผลในเวิร์กโฟลว์ CFD สมัยใหม่ โดยมีเครื่องมือเฉพาะทางมากกว่า 170 รายการที่ช่วยในการจัดการงานซ้ำซ้อน การสร้างเวิร์กโฟลว์ที่ซับซ้อน และขยายขีดความสามารถของ OpenFOAM ให้ครอบคลุมทุกความต้องการทางวิศวกรรม

---

## 1. ระบบนิเวศของ OpenFOAM Utility (The Utility Ecosystem)

### 1.1 ปรัชญาหลัก (Core Philosophy)

Utilities คือแอปพลิเคชันแบบ Command-line ที่ออกแบบมาเพื่อจัดการแง่มุมเฉพาะของเวิร์กโฟลว์ CFD ซึ่งแตกต่างจาก Solvers ตรงที่ไม่ได้คำนวณฟิสิกส์ของการไหลโดยตรง แต่จะเน้นที่:

- **Pre-processing**: การสร้างเมช, การย่อยโดเมน, การกำหนดค่าเริ่มต้น
- **Mesh Manipulation**: การตรวจสอบคุณภาพและการปรับปรุงความละเอียด
- **Post-processing**: การวิเคราะห์ข้อมูลและการแสดงภาพ
- **Automation**: การเขียนสคริปต์และการประมวลผลแบบกลุ่ม (Batch Processing)

> [!INFO] ความแตกต่างระหว่าง Solver และ Utility
> - **Solver**: คำนวณสมการกำลังดุลย์ (Governing Equations) และแก้สมการเชิงอนุพันธ์
> - **Utility**: จัดการข้อมูล เมช และผลลัพธ์ แต่ไม่แก้สมการฟิสิกส์โดยตรง

### 1.2 สถาปัตยกรรมของ Utility (System Architecture)

ยูทิลิตี้ทุกตัวมีโครงสร้างที่เป็นมาตรฐานเพื่อให้ง่ายต่อการพัฒนาและใช้งาน:

- **`argList.H`**: จัดการคำสั่งและอาร์กิวเมนต์ที่ป้อนเข้ามา
- **`fvMesh.H`**: อินเทอร์เฟซสำหรับเข้าถึงข้อมูล Mesh
- **`timeSelector.H`**: ควบคุมการเลือกช่วงเวลาในการประมวลผล

#### โครงสร้างของ Utility แบบมาตรฐาน

โครงสร้างพื้นฐานของ Utility ใน OpenFOAM สามารถแสดงได้ดังนี้:

```cpp
// NOTE: Synthesized by AI - Verify parameters
#include "fvCFD.H"
#include "timeSelector.H"

int main(int argc, char *argv[])
{
    // จัดการ arguments และตั้งค่าเวลา
    timeSelector::addOptions();
    argList::addNote("Description of utility functionality");

    #include "setRootCaseLists.H"
    #include "createTime.H"
    #include "createMesh.H"

    // เลือกช่วงเวลาที่ต้องการประมวลผล
    instantList timeDirs = timeSelector::select
    (
        runTime.times(),
        args
    );

    // วนลูปผ่านทุก time directory
    forAll(timeDirs, timeI)
    {
        runTime.setTime(timeDirs[timeI], timeI);

        // อ่านข้อมูลฟิลด์
        #include "createFields.H"

        // ประมวลผลตามวัตถุประสงค์ของ utility
        // ... operations ...

        Info<< "Processed time = " << runTime.timeName() << nl;
    }

    return 0;
}
```

---

## 2. หมวดหมู่ของ Utility และการจัดกลุ่ม (Categories & Organization)

### 2.1 Mesh Utilities (85+ เครื่องมือ)

ครอบคลุมตั้งแต่การสร้างเมชหกเหลี่ยมแบบโครงสร้าง (**blockMesh**) ไปจนถึงการสร้างเมชสำหรับเรขาคณิตที่ซับซ้อน (**snappyHexMesh**) และการตรวจสอบคุณภาพเมช (**checkMesh**)

#### สมการพื้นฐานของ Mesh Quality

การประเมินคุณภาพของเมชใช้เกณฑ์ทางเรขาคณิตและคณิตศาสตร์:

$$
\text{Non-Orthogonality} = \max\left[\left(1 - \frac{\mathbf{S}_f \cdot \mathbf{d}}{|\mathbf{S}_f| |\mathbf{d}|}\right) \times 100\right]
$$

$$
\text{Aspect Ratio} = \frac{\Delta_{max}}{\Delta_{min}}
$$

$$
\text{Skewness} = \frac{|\mathbf{d} - \mathbf{d}_{ideal}|}{|\mathbf{d}_{ideal}|}
$$

โดยที่:
- $\mathbf{S}_f$ = เวกเตอร์พื้นที่ผิวหน้าเซลล์ (Face area vector)
- $\mathbf{d}$ = เวกเตอร์ระยะห่างระหว่างเซนทรอยด์ของเซลล์ข้างเคียง
- $\Delta_{max}, \Delta_{min}$ = ขนาดเซลล์สูงสุดและต่ำสุด

> [!WARNING] เกณฑ์คุณภาพเมชที่แนะนำ
> - **Non-Orthogonality**: < 70° (ideal: < 50°)
> - **Aspect Ratio**: < 1000 (ideal: < 100)
> - **Skewness**: < 4 (ideal: < 2)

#### ตัวอย่างการตั้งค่า `checkMesh`

```cpp
// NOTE: Synthesized by AI - Verify parameters
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      meshQualityDict;
}

// เกณฑ์การตรวจสอบคุณภาพเมช
maxNonOrthogonal 70;
maxBoundarySkewness 4;
maxInternalSkewness 4;
maxConcave 80;
minFlatness 0.5;
minVol 1e-13;
minTetQuality 1e-30;
minArea -1;
minTwist 0.02;
minDeterminant 0.001;
minFaceWeight 0.05;
minVolRatio 0.01;
minTriangleTwist -1;
nSmoothScale 4;
errorReduction 0.75;
```

### 2.2 Post-Processing Utilities (25+ เครื่องมือ)

เน้นการแปลงข้อมูลไปสู่รูปแบบที่มนุษย์เข้าใจได้ เช่น **foamToVTK** สำหรับ ParaView และการคำนวณปริมาณอนุพัทธ์ผ่านเครื่องมือ **postProcess**

#### การคำนวณ Gradient และ Divergence

กระบวนการคำนวณปริมาณอนุพัทธ์ใช้หลักการของ Finite Volume Method:

$$
\nabla \phi = \frac{1}{V_P} \sum_f \phi_f \mathbf{S}_f
$$

$$
\nabla \cdot \mathbf{u} = \frac{1}{V_P} \sum_f \mathbf{u}_f \cdot \mathbf{S}_f
$$

โดยที่:
- $V_P$ = ปริมาตรของเซลล์
- $\phi_f$ = ค่าของฟิลด์ที่ผิวหน้า
- $\mathbf{u}_f$ = เวกเตอร์ความเร็วที่ผิวหน้า
- $\mathbf{S}_f$ = เวกเตอร์พื้นที่ผิวหน้า

#### ตัวอย่างการใช้งาน `postProcess`

```bash
# NOTE: Synthesized by AI - Verify parameters
# คำนวณ vorticity
postProcess -func "vorticity"

# คำนวณ wall shear stress
postProcess -func "wallShearStress"

# คำนวณ pressure coefficient
postProcess -func "mag(U)" -latestTime
postProcess -func "Cp" -latestTime

# สร้าง surfaces sampling
postProcess -func surfaces
```

#### การตั้งค่า `postProcess` ในไฟล์ `functions`

```cpp
// NOTE: Synthesized by AI - Verify parameters
functions
{
    // คำนวณ vorticity
    vorticity1
    {
        type            vorticity;
        functionObjectLibs ("libfieldFunctionObjects.so");
        writeControl    timeStep;
        writeInterval   10;
    }

    // คำนวณ wall shear stress
    wallShearStress1
    {
        type            wallShearStress;
        functionObjectLibs ("libfieldFunctionObjects.so");
        writeControl    timeStep;
        writeInterval   10;
    }

    // คำนวณ pressure coefficient
    Cp
    {
        type            surfaceRegion;
        functionObjectLibs ("libfieldFunctionObjects.so");
        writeControl    timeStep;
        writeInterval   10;
        surfaceFormat   none;
        regionType      patch;
        name            inlet;
        operation       none;

        fields
        (
            p
            U
        );

        Cp
        {
            $p;
            result      Cp;
        }
    }
}
```

### 2.3 Parallel Processing Utilities (4 เครื่องมือ)

เครื่องมือที่สำคัญที่สุดคือ **decomposePar** สำหรับการย่อยโดเมนก่อนรันขนาน และ **reconstructPar** สำหรับรวบรวมผลลัพธ์กลับคืนมา

#### สมการของ Domain Decomposition

การแบ่งโดเมนใช้หลักการของ Graph Partitioning:

$$
\min \sum_{i=1}^{N} \sum_{j=i+1}^{N} w_{ij} \cdot \delta(p_i, p_j)
$$

โดยที่:
- $w_{ij}$ = น้ำหนักของการเชื่อมต่อระหว่างเซลล์ $i$ และ $j$
- $\delta(p_i, p_j)$ = ฟังก์ชันที่เท่ากับ 1 ถ้าเซลล์อยู่คนละ partition และ 0 ถ้าอยู่ partition เดียวกัน
- $N$ = จำนวนเซลล์ทั้งหมด

> [!TIP] กลยุทธ์การแบ่งโดเมน
> - **simple**: แบ่งตามแกน X, Y, Z เหมาะกับเรขาคณิตที่เป็นระเบียบ
> - **scotch**: อัตโนมัติและมีประสิทธิภาพสูง
> - **hierarchical**: ผสม simple + scorch เหมาะกับระบบ HPC

#### ตัวอย่างการตั้งค่า `decomposePar`

```cpp
// NOTE: Synthesized by AI - Verify parameters
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      decomposeParDict;
}

// จำนวน processors
numberOfSubdomains 4;

// วิธีการแบ่งโดเมน
method scotch;

// หรือใช้ simple method
// method simple;

// simpleCoeffs สำหรับ simple method
simpleCoeffs
{
    n           (4 1 1);  // แบ่ง 4 ในแกน X, 1 ใน Y, 1 ใน Z
    delta       0.001;
}

// scotchCoeffs สำหรับ scotch method
scotchCoeffs
{
    processorWeights
    (
        1
        1
        1
        1
    );
}

// hierarchicalCoeffs สำหรับ hierarchical method
hierarchicalCoeffs
{
    n           (4 1 1);
    delta       0.001;
    method      scotch;
}
```

---

## 3. การผสานรวมกับเวิร์กโฟลว์ (Workflow Integration)

เพื่อให้การทำงานมีประสิทธิภาพ ยูทิลิตี้เหล่านี้มักถูกรันต่อเนื่องกันในรูปแบบไปป์ไลน์:

```mermaid
flowchart TD
    A[เตรียมเรขาคณิต] --> B[blockMesh/snappyHexMesh]
    B --> C[checkMesh]
    C -->|ผ่าน| D[decomposePar]
    C -->|ไม่ผ่าน| B
    D --> E[Solver Execution]
    E --> F[reconstructPar]
    F --> G[postProcess/foamToVTK]
    G --> H[Visualization]

    style A fill:#e1f5ff
    style B fill:#fff4e1
    style C fill:#ffe1e1
    style D fill:#e1ffe1
    style E fill:#e1f5ff
    style F fill:#e1ffe1
    style G fill:#fff4e1
    style H fill:#f0e1ff
```
> **Figure 1:** แผนภูมิแสดงลำดับการทำงาน (Workflow) ในการใช้งาน Utilities ร่วมกับ Solver ของ OpenFOAM โดยเน้นการตรวจสอบคุณภาพเมชและการจัดการข้อมูลแบบขนาน (Parallel Processing) ก่อนนำไปแสดงผล

### 3.1 การสร้าง Automation Script

ตัวอย่างสคริปต์ Bash สำหรับ automation:

```bash
#!/bin/bash
# NOTE: Synthesized by AI - Verify parameters

# 1. สร้างเมช
blockMesh

# 2. ตรวจสอบคุณภาพเมช
checkMesh > mesh_check.log

# 3. ตรวจสอบว่าเมชผ่านเกณฑ์หรือไม่
if grep -q "Failed" mesh_check.log; then
    echo "Mesh quality check failed!"
    exit 1
fi

# 4. แบ่งโดเมนสำหรับ parallel
decomposePar

# 5. รัน solver แบบ parallel
mpirun -np 4 solverName -parallel

# 6. รวมผลลัพธ์
reconstructPar

# 7. Post-processing
postProcess -func "vorticity"
foamToVTK

# 8. ล้างข้อมูลชั่วคราว
rm -rf processor*

echo "Simulation completed successfully!"
```

### 3.2 การประยุกต์ใช้ utilities ในกรณีศึกษาจริง

#### Case Study: การวิเคราะห์การไหลผ่านท่อ

**ขั้นตอน:**

1. **Pre-processing**:
   - ใช้ `blockMesh` สร้างเมชพื้นฐาน
   - ใช้ `snappyHexMesh` ปรับปรุงความละเอียดบริเวณผนัง
   - ใช้ `checkMesh` ตรวจสอบคุณภาพ

2. **Simulation**:
   - ใช้ `decomposePar` แบ่งโดเมนเป็น 8 processors
   - รัน `simpleFoam` แบบ parallel

3. **Post-processing**:
   - ใช้ `postProcess` คำนวณ wall shear stress
   - ใช้ `foamToVTK` แปลงข้อมูลสำหรับ ParaView
   - ใช้ `sample` ดึงข้อมูลตามจุดที่กำหนด

> **[MISSING DATA]**: Insert specific simulation results/graphs for this section.

---

## 4. หลักการเขียน Custom Utility

### 4.1 โครงสร้างพื้นฐาน

การสร้าง custom utility ทำได้โดย:

1. สร้าง directory ใหม่ใน `$FOAM_USER_APPBIN`
2. เขียนไฟล์ `.C` หลัก
3. สร้างไฟล์ `Make/FILES` และ `Make/options`
4. คอมไพล์ด้วย `wmake`

#### ตัวอย่าง Custom Utility: การคำนวณ Volume Flow Rate

```cpp
// NOTE: Synthesized by AI - Verify parameters
#include "fvCFD.H"
#include "surfaceFields.H"
#include "singlePhaseTransportModel.H"
#include "turbulentTransportModel.H"

// คำนวณ volume flow rate ผ่าน patch ที่ระบุ
int main(int argc, char *argv[])
{
    timeSelector::addOptions();
    argList::addNote
    (
        "Calculate volume flow rate through specified patches"
    );

    #include "setRootCaseLists.H"
    #include "createTime.H"
    #include "createMesh.H"

    instantList timeDirs = timeSelector::select
    (
        runTime.times(),
        args
    );

    // อ่านชื่อ patch จาก dictionary
    IOdictionary flowRateDict
    (
        IOobject
        (
            "flowRateDict",
            runTime.system(),
            mesh,
            IOobject::MUST_READ,
            IOobject::NO_WRITE
        )
    );

    wordList patchNames(flowRateDict.lookup("patches"));

    forAll(timeDirs, timeI)
    {
        runTime.setTime(timeDirs[timeI], timeI);

        Info<< "Time = " << runTime.timeName() << endl;

        // อ่านค่าความเร็ว
        volVectorField U
        (
            IOobject
            (
                "U",
                runTime.timeName(),
                mesh,
                IOobject::MUST_READ,
                IOobject::NO_WRITE
            ),
            mesh
        );

        // คำนวณ volume flow rate
        scalar totalFlowRate = 0.0;

        forAll(patchNames, i)
        {
            label patchID = mesh.boundaryMesh().findPatchID(patchNames[i]);

            if (patchID != -1)
            {
                scalar flowRate = sum
                (
                    mesh.boundary()[patchID].Sf() &
                    U.boundaryField()[patchID]
                );

                Info<< "Patch " << patchNames[i]
                    << " flow rate: " << flowRate << " m^3/s" << endl;

                totalFlowRate += flowRate;
            }
        }

        Info<< "Total flow rate: " << totalFlowRate << " m^3/s"
            << nl << endl;
    }

    return 0;
}
```

#### การตั้งค่า `Make/FILES`

```bash
# NOTE: Synthesized by AI - Verify parameters
myUtility.C

EXE = $(FOAM_USER_APPBIN)/myUtility
```

#### การตั้งค่า `Make/options`

```bash
# NOTE: Synthesized by AI - Verify parameters
EXE_INC = \
    -I$(LIB_SRC)/finiteVolume/lnInclude \
    -I$(LIB_SRC)/meshTools/lnInclude \
    -I$(LIB_SRC)/transportModels \
    -I$(LIB_SRC)/turbulenceModels

EXE_LIBS = \
    -lfiniteVolume \
    -lmeshTools \
    -lincompressibleTransportModels \
    -lincompressibleTurbulenceModels
```

---

## 5. เทคนิคขั้นสูงและ Best Practices

### 5.1 การใช้งาน Utilities ร่วมกับ Python Automation

```python
# NOTE: Synthesized by AI - Verify parameters
import subprocess
import os
import re

class OpenFOAMWorkflow:
    def __init__(self, case_dir):
        self.case_dir = case_dir
        os.chdir(case_dir)

    def run_command(self, cmd):
        """รันคำสั่ง OpenFOAM utility"""
        try:
            result = subprocess.run(
                cmd.split(),
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error running {cmd}: {e.stderr}")
            return None

    def check_mesh_quality(self, max_non_ortho=70):
        """ตรวจสอบคุณภาพเมช"""
        output = self.run_command("checkMesh")

        if output:
            # แยกข้อมูล non-orthogonality
            match = re.search(r'Max.*?non-ortho.*?(\d+)', output)
            if match:
                non_ortho = int(match.group(1))
                return non_ortho < max_non_ortho

        return False

    def run_simulation(self, np=4):
        """รัน simulation แบบ parallel"""
        self.run_command("decomposePar")
        self.run_command(f"mpirun -np {np} solverName -parallel")
        self.run_command("reconstructPar")

# การใช้งาน
workflow = OpenFOAMWorkflow("/path/to/case")
if workflow.check_mesh_quality():
    workflow.run_simulation(np=8)
```

### 5.2 การปรับแต่ง Mesh Quality อัตโนมัติ

```bash
#!/bin/bash
# NOTE: Synthesized by AI - Verify parameters

# วนลูปเพื่อปรับปรุงคุณภาพเมช
max_iter=5
iter=0

while [ $iter -lt $max_iter ]
do
    # ตรวจสอบคุณภาพเมช
    checkMesh > mesh_report.txt

    # ตรวจสอบ non-orthogonality
    non_ortho=$(grep "Max:" mesh_report.txt | awk '{print $2}')

    if (( $(echo "$non_ortho < 70" | bc -l) )); then
        echo "Mesh quality acceptable: $non_ortho"
        break
    fi

    echo "Iteration $((iter+1)): Non-orthogonality = $non_ortho"

    # ปรับปรุงเมช
    refineMesh -overwrite

    ((iter++))
done
```

---

## 6. สรุปการเลือกใช้ Utilities

### 6.1 ตารางเปรียบเทียบการใช้งาน

| งาน | Utility หลัก | Utility รอง | หมายเหตุ |
|------|---------------|--------------|-----------|
| สร้างเมชฐาน | `blockMesh` | - | เริ่มจาก geometry ง่าย |
| ปรับปรุงเมช | `snappyHexMesh` | `refineMesh` | ใช้ surface เป็นพื้นฐาน |
| ตรวจสอบคุณภาพ | `checkMesh` | `meshQualityReport` | ต้องทำก่อนรัน solver |
| แบ่งโดเมน | `decomposePar` | `decomposeParMetis` | เลือก method ให้เหมาะกับเครื่อง |
| รวมผลลัพธ์ | `reconstructPar` | `reconstructParMesh` | ทำหลังจาก parallel run |
| แปลงข้อมูล | `foamToVTK` | `foamToEnsight` | สำหรับ visualization |
| คำนวณอนุพัทธ์ | `postProcess` | - | สามารถกำหนด function เอง |

---

## 🎓 สรุปแนวคิดสำคัญ

ระบบนิเวศของ OpenFOAM Utility มอบแนวทางที่เป็นระบบในการจัดการข้อมูล CFD ขนาดใหญ่:

- **ความหลากหลาย**: มีเครื่องมือให้เลือกใช้มากกว่า 170 รายการ
- **ความแม่นยำ**: อิงตามหลักการทางคณิตศาสตร์ที่เข้มงวดในการจัดการฟิลด์และเมช
- **ความเป็นอัตโนมัติ**: สามารถนำมารวมกันเป็นสคริปต์เพื่อให้ทำงานได้โดยอัตโนมัติ 100%
- **ความยืดหยุ่น**: สามารถเขียน custom utility ของตัวเองได้ง่าย
- **ประสิทธิภาพ**: รองรับ parallel processing สำหรับข้อมูลขนาดใหญ่

> [!TIP] แหล่งข้อมูลเพิ่มเติม
> - OpenFOAM User Guide: ดูรายการ utilities ทั้งหมด
> - OpenFOAM Programmer's Guide: วิธีเขียน custom utility
> - $WM_PROJECT_DIR/applications/utilities: ดู source code ตัวอย่าง

---

## 7. การตรวจสอบและ Validation

### 7.1 การตรวจสอบความถูกต้องของ Utility Output

เมื่อใช้ utilities ให้ตรวจสอบ:

1. **Mass Conservation**: ตรวจสอบว่า mass balance ถูกต้อง
2. **Physical Consistency**: ตรวจสอบว่าผลลัพธ์สอดคล้องกับฟิสิกส์
3. **Mesh Independence**: ตรวจสอบว่าผลลัพธ์ไม่ขึ้นกับความละเอียดเมช

### 7.2 การ Debug Utilities

```bash
# NOTE: Synthesized by AI - Verify parameters
# รันด้วย verbose mode
utilityName -debug

# ตรวจสอบ dependencies
ldd $FOAM_USER_APPBIN/utilityName

# ตรวจสอบ log files
tail -f log.utilityName
```

---

**หัวข้อถัดไป**: [[02_Utility_Categories_and_Organization]] เพื่อเจาะลึกแต่ละหมวดหมู่เครื่องมือ
