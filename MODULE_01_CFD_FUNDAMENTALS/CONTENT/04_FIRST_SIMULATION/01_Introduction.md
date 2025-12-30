# บทนำ: CFD Simulation Workflow - แนวคิดและแนวทาง

## Learning Objectives

หลังจากอ่านบทนี้ คุณควรจะสามารถ:
- **อธิบาย** 3 ขั้นตอนหลักของ CFD workflow (Pre-processing, Solving, Post-processing)
- **ระบุ** ไฟล์และ directory ที่จำเป็นใน OpenFOAM case structure
- **เลือก** solver ที่เหมาะสมกับปัญหาที่ต้องการแก้
- **วินิจฉัย** ปัญหาพื้นฐานจาก log files และ convergence behavior

---

## Overview

**WHAT**: OpenFOAM CFD workflow เป็นกรอบการทำงานมาตรฐาน 3 ขั้นตอนที่ใช้ในการแก้โจทย์พลศาสตร์ของไหลด้วยเชิงตัวเลข ประกอบด้วย Pre-processing (เตรียมข้อมูล), Solving (คำนวณ), และ Post-processing (วิเคราะห์ผล)

**WHY**: การเข้าใจ workflow เป็นสิ่งจำเป็นเพื่อให้สามารถ debug simulations ได้อย่างมีประสิทธิภาพ เมื่อเกิดปัญหา คุณจะต้องรู้ว่าต้องตรวจสอบไฟล์ใด หรือปรับแต่งส่วนใดของระบบ ซึ่งความเข้าใจ case structure ของ OpenFOAM คือหัวใจสำคัญ

**HOW**: โดยการเรียนรู้ case directory structure ที่เป็นระบบ การแยกส่วน pre-processing/solving/post-processing อย่างชัดเจน และการฝึกตรวจสอบความถูกต้องของแต่ละขั้นตอนก่อนนำไปสู่ขั้นตอนถัดไป

> **💡 KEY INSIGHT:**
> CFD = **Pre-processing + Solving + Post-processing**
> 
> ถ้าไม่เข้าใจขั้นตอน → จะไม่รู้ว่าต้องแก้ไฟล์ไหนเมื่อมีปัญหา
> 
> เข้าใจ workflow = เข้าใจ **case structure** ของ OpenFOAM

---

## CFD คืออะไร?

**WHAT**: Computational Fluid Dynamics (CFD) คือการแก้สมการการไหลของไหลด้วยวิธีเชิงตัวเลขบนคอมพิวเตอร์

**WHY**: สมการการไหล (Navier-Stokes equations) ไม่สามารถแก้ได้แบบ analytical สำหรับปัญหาจริงที่ซับซ้อน → ต้องใช้วิธีเชิงตัวเลขแทน

**HOW**: โดยการ **discretize** สมการบน mesh (แบ่ง domain เป็น cells เล็กๆ) แล้วแก้สมการเชิงตัวเลขที่แต่ละ point

$$\frac{\partial \mathbf{u}}{\partial t} + (\mathbf{u} \cdot \nabla)\mathbf{u} = -\frac{1}{\rho}\nabla p + \nu\nabla^2\mathbf{u}$$

---

## OpenFOAM Workflow: The Big Picture

**WHAT**: กรอบการทำงาน 3 ขั้นตอนที่เป็นหลักการของการทำ CFD ใน OpenFOAM

**WHY**: การแบ่ง workflow ออกเป็น 3 ขั้นตอนช่วยให้จัดการความซับซ้อนได้ และทำให้สามารถตรวจสอบความถูกต้องในแต่ละขั้นตอนได้ง่ายขึ้น

**HOW**: ดูภาพรวมของ 3 ขั้นตอนด้านล่างนี้ และไปรายละเอียดในบทถัดไป

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  PRE-PROCESSING │ → │     SOLVING     │ → │ POST-PROCESSING │
│  • Geometry     │    │  • icoFoam      │    │  • ParaView     │
│  • Mesh         │    │  • simpleFoam   │    │  • Probes       │
│  • BCs          │    │  • pimpleFoam   │    │  • Sampling     │
│  • Properties   │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

> **📖 CROSS-REFERENCE:** รายละเอียดการ implement แต่ละขั้นตอนแบบเต็มรูปแบบ ดูได้ใน [02_The_Workflow.md](02_The_Workflow.md)

---

## 1. Pre-Processing Concepts

**WHAT**: การเตรียมข้อมูลและตั้งค่าก่อนเริ่ม simulation ซึ่งรวมถึง geometry, mesh, boundary conditions, และ physical properties

**WHY**: Input ที่ผิดพลาดในขั้นตอนนี้จะนำไปสู่ผลลัพธ์ที่ผิดพลาดในทุกขั้นตอนถัดไป "Garbage in, garbage out"

**HOW**: โดยการสร้าง OpenFOAM case structure ที่มี directories และไฟล์ที่จำเป็นครบถ้วน

### Directory Structure Overview

| Directory | ไฟล์ | หน้าที่ |
|-----------|------|--------|
| `0/` | U, p, T, k, ε... | Initial & Boundary Conditions |
| `constant/` | polyMesh/, transportProperties | **Mesh** (points, faces, cells) & Physical properties |
| `system/` | controlDict, fvSchemes, fvSolution | Solver Settings |

### Understanding Mesh Structure

> **💡 WHAT: `constant/polyMesh/` คืออะไร?**
> - **`points`**: พิกัด (x,y,z) ของทุก vertices ใน mesh
> - **`faces`**: ผิว (2D) ที่เกิดจากการเชื่อม vertices เข้าด้วยกัน
> - **`cells`**: volumes 3D ที่เกิดจาก faces ล้อมรอบ
> - **`boundary`**: ชื่อ patches และ types (wall, patch, symmetry, ฯลฯ)

**WHY**: การเข้าใจ mesh structure ช่วยให้เข้าใจว่าข้อมูลถูกเก็บและเข้าถึงอย่างไรใน OpenFOAM

**HOW**: เมื่อรัน `blockMesh` หรือ `snappyHexMesh` ไฟล์เหล่านี้จะถูกสร้างขึ้นอัตโนมัติจาก dictionary files

### Key Pre-Processing Commands

```bash
# Simple geometries
blockMesh

# Complex geometries
snappyHexMesh -overwrite

# Check mesh quality
checkMesh
```

> **📖 CROSS-REFERENCE:** รายละเอียดการสร้าง mesh และการตั้งค่า BCs แบบ step-by-step ดูใน [02_The_Workflow.md](02_The_Workflow.md)

---

## 2. Solving Concepts

**WHAT**: ขั้นตอนคำนวณ numerical solver จะแก้ discretized Navier-Stokes equations บน mesh ที่สร้างไว้

**WHY**: นี่คือหัวใจของ CFD — การแปลง geometry และ physics ให้กลายเป็นคำตอบทางวิศวกรรม

**HOW**: โดยการเลือก solver ที่เหมาะสมกับปัญหา และรันจนกว่าจะ converges

### Solver Selection Guide

| Solver | Use Case | Characteristics |
|--------|----------|-----------------|
| `icoFoam` | Incompressible, laminar, transient | ง่ายที่สุด, เหมาะสำหรับการเรียนรู้ |
| `simpleFoam` | Incompressible, turbulent, steady-state | ใช้งานบ่อยที่สุดสำหรับ industrial flows |
| `pimpleFoam` | Incompressible, turbulent, transient | ผสม PISO + SIMPLE, แม่นยำแต่ช้า |
| `buoyantSimpleFoam` | Buoyancy, heat transfer, steady | สำหรับปัญหา natural convection |

### Running Simulation

```bash
# Serial execution
icoFoam > log.icoFoam &

# Monitor convergence in real-time
tail -f log.icoFoam

# Parallel execution (4 cores)
decomposePar
mpirun -np 4 icoFoam -parallel
reconstructPar
```

> **📖 CROSS-REFERENCE:** รายละเอียดการปรับแต่ง solver settings และ convergence criteria ดูใน [02_The_Workflow.md](02_The_Workflow.md)

---

## 3. Post-Processing Concepts

**WHAT**: การวิเคราะห์และ visualize ผลลัพธ์จาก simulation

**WHY**: ตัวเลขจาก solver ไม่มีความหมายหากไม่แปลงเป็น insights ทางวิศวกรรมที่เข้าใจได้

**HOW**: โดยใช้ ParaView สำหรับ visualization และ functions/probes สำหรับ quantitative analysis

### Visualization with ParaView

```bash
paraFoam
```

**สิ่งที่สามารถแสดงผลได้:**
- Velocity vectors, contours
- Pressure fields
- Streamlines and pathlines
- Iso-surfaces
- Derived quantities (vorticity, wall shear stress, etc.)

### Quantitative Data Extraction

```cpp
// system/controlDict
functions
{
    probes
    {
        type        probes;
        fields      (U p);
        probeLocations ((0.5 0.5 0.05));
    }
}
```

> **📖 CROSS-REFERENCE:** ตัวอย่างการใช้ probes และ sampling แบบละเอียด พร้อม hands-on tutorial ดูใน [04_Hands_On_Tutorial.md](04_Hands_On_Tutorial.md)

---

## Case Directory Structure

**WHAT**: โครงสร้าง directory มาตรฐานของ OpenFOAM case ที่ต้องมีทุกครั้ง

**WHY**: OpenFOAM solvers คาดหวังที่จะเจอไฟล์ในตำแหน่งที่กำหนดเท่านั้น ผิดตำแหน่ง = solver crash

**HOW**: ทำตาม standard structure ด้านล่างนี้

```
myCase/
├── 0/                           # Initial & Boundary conditions
│   ├── U                        # Velocity field
│   └── p                        # Pressure field
├── constant/
│   ├── polyMesh/                # Mesh files
│   │   ├── blockMeshDict        # Mesh generation dictionary
│   │   ├── boundary             # Boundary patch definitions
│   │   ├── faces                # Face connectivity
│   │   ├── neighbour            # Cell neighbor information
│   │   ├── owner                # Face ownership
│   │   └── points               # Vertex coordinates
│   └── transportProperties      # Physical properties (ν, ρ, etc.)
├── system/
│   ├── controlDict              # Time/solver control
│   ├── fvSchemes                # Discretization schemes
│   └── fvSolution               # Linear solver settings
└── Allrun                       # Run script (optional)
```

---

## Essential Configuration Files

### system/controlDict

**WHAT**: ไฟล์ควบคุมเวลาและ output ของ simulation

**WHY**: กำหนดว่า simulation จะรันนานแค่ไหน และเซฟผลลัพธ์เมื่อไร

**HOW**: 

```cpp
application     icoFoam;          // Solver to use
startFrom       startTime;        // Where to start
startTime       0;                // Start time
stopAt          endTime;          // When to stop
endTime         0.5;              // End time (s)
deltaT          0.005;            // Time step (s)
writeControl    timeStep;         // Output control
writeInterval   20;               // Write every 20 steps
```

### system/fvSchemes

**WHAT**: กำหนด discretization schemes สำหรับแต่ละ term ในสมการ

**WHY**: ความแม่นยำและความเสถียรขึ้นอยู่กับการเลือก scheme

**HOW**:

```cpp
ddtSchemes      { default Euler; }           // Time discretization
gradSchemes     { default Gauss linear; }    // Gradient calculation
divSchemes      { div(phi,U) Gauss upwind; } // Convection terms
laplacianSchemes { default Gauss linear corrected; } // Diffusion terms
```

### system/fvSolution

**WHAT**: ตั้งค่า linear solvers และ algorithm-specific parameters

**WHY**: ความเร็วและความสามารถในการ converge ขึ้นอยู่กับ settings เหล่านี้

**HOW**:

```cpp
solvers
{
    p  { solver GAMG; tolerance 1e-6; relTol 0.01; }
    U  { solver smoothSolver; smoother GaussSeidel; tolerance 1e-5; relTol 0; }
}
PISO { nCorrectors 2; pRefCell 0; pRefValue 0; }
```

> **📖 CROSS-REFERENCE:** รายละเอียดการเลือกและปรับแต่ง schemes/solvers ดูใน [02_The_Workflow.md](02_The_Workflow.md)

---

## Convergence Monitoring

**WHAT**: การตรวจสอบว่า simulation ได้ converge หรือยัง

**WHY**: ถ้าไม่ converge → ผลลัพธ์ไม่น่าเชื่อถือ ต้องหาสาเหตุและแก้ไข

**HOW**: ตรวจสอบ residuals จาก log files

### Checking Residuals

```bash
# View residuals during simulation
grep "Solving for" log.icoFoam

# Extract and plot with foamLog
foamLog log.icoFoam
gnuplot
gnuplot> plot "logs/p_0" with lines
```

### Convergence Criteria

**เกณฑ์ทั่วไป:**
- Initial residual ควรลดลง **3-4 orders of magnitude**
- Final residual < **tolerance** ที่กำหนดใน `fvSolution`
- ถ้า residuals ไม่ลดลง → ต้องตรวจสอบ:

1. Mesh quality (`checkMesh`)
2. Boundary conditions (ความสอดคล้องของ U-p)
3. Time step (CFL condition)
4. Discretization schemes

> **📖 CROSS-REFERENCE:** การแก้ไขปัญหา convergence และ troubleshooting ดูใน [02_The_Workflow.md](02_The_Workflow.md)

---

## Concept Check

<details>
<summary><b>1. ถ้า residuals ไม่ลดลง ควรตรวจอะไรก่อน?</b></summary>

**คำตอบ:** ตรวจสอบตามลำดับนี้:
1. **Mesh quality** — `checkMesh` ดูว่ามี non-orthogonal cells หรือ skewness มากเกินไปหรือไม่
2. **Boundary conditions** — ตรวจว่า U และ p สอดคล้องกัน (mass conservation)
3. **Time step** — CFL number สูงเกินไปอาจทำให้ไม่ converge
4. **Discretization schemes** — upwind (stable) หรือ linear (accurate but may oscillate)
</details>

<details>
<summary><b>2. pRefCell และ pRefValue ใช้ทำไม?</b></summary>

**คำตอบ:** ใน incompressible flow, pressure ถูกกำหนดได้ถึง **constant** เท่านั้น (เพิ่ม p ด้วยค่าคงที่ไหนก็ได้ สมการยังเป็นจริง) → ต้อง fix ค่าที่ cell ใดเซลล์หนึ่งเพื่อให้ solver สามารถแก้สมการได้ โดยปกติ fix ที่ cell 0 ให้มีค่า p = 0
</details>

<details>
<summary><b>3. Gauss upwind กับ Gauss linear ต่างกันอย่างไร?</b></summary>

**คำตอบ:**
- **`Gauss upwind`**: 1st order, **stable** (bound-preserving), แต่ **diffusive** (ทำให้ gradients จางลง)
- **`Gauss linear`**: 2nd order, **accurate**, แต่อาจ **oscillate** ได้ที่ high Péclet number
- ที่ถูกต้อง: เริ่มด้วย upwind เพื่อ稳定性 แล้วค่อยเปลี่ยนเป็น linear เมื่อ converge แล้ว
</details>

<details>
<summary><b>4. Pre-processing, Solving, และ Post-processing ต่างกันอย่างไร?</b></summary>

**คำตอบ:**
- **Pre-processing**: เตรียมข้อมูล (geometry, mesh, BCs) — input สำหรับ solver
- **Solving**: คำนวณสมการบน mesh — แก้ PDEs เชิงตัวเลข
- **Post-processing**: วิเคราะห์ผลลัพธ์ — visualization และ quantitative analysis
</details>

---

## Key Takeaways

1. **OpenFOAM workflow มี 3 ขั้นตอนหลัก**: Pre-processing (เตรียม), Solving (คำนวณ), Post-processing (วิเคราะห์)
2. **Case structure คือหัวใจ**: `0/`, `constant/`, `system/` directories ต้องถูกต้องและครบถ้วน
3. **เลือก solver ให้เหมาะกับปัญหา**: laminar/turbulent, steady/transient, compressible/incompressible
4. **Convergence คือสิ่งสำคัญ**: ตรวจ residuals อยู่เสมอ ถ้าไม่ลดลง → หาสาเหตุและแก้ไข
5. **Input quality กำหนด output quality**: "Garbage in, garbage out" — ตรวจสอบทุกอย่างก่อนรัน solver

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [00_Overview.md](00_Overview.md) — ภาพรวมของ First Simulation
- **บทถัดไป:** [02_The_Workflow.md](02_The_Workflow.md) — Workflow Details และ Reference แบบละเอียด
- **Hands-on:** [04_Hands_On_Tutorial.md](04_Hands_On_Tutorial.md) — ทำตาม step-by-step tutorial พร้อม examples เต็มรูปแบบ