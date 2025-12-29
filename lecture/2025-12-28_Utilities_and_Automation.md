# บันทึกบทเรียน: Utilities & Automation — จาก User สู่ CFD Specialist

**วันที่:** 28 ธันวาคม 2025

> **สิ่งที่จะได้เรียนรู้:**
> 1. Shell Scripting สำหรับ OpenFOAM (Allrun, Allclean)
> 2. Python Automation (PyFoam, fluidfoam, PyVista)
> 3. HPC & Parallel Computing
> 4. Professional Practices (Git, Documentation, Utilities)

---

## 1. ทำไม Automation สำคัญ?

> **"The difference between an amateur and a professional is automation"**

### 1.1 Manual vs Automated Workflow

```
=== Manual (ช้า, เสี่ยงผิดพลาด) ===

1. cd case_folder
2. blockMesh
3. checkMesh
4. simpleFoam
5. paraFoam
6. (คลิก screenshot)
7. (copy ตัวเลขลง Excel)
8. ทำซ้ำ 100 ครั้ง... 😫

=== Automated (เร็ว, repeatable) ===

1. ./Allrun   # รันทุก case
2. python analyze.py   # วิเคราะห์ผล
3. ได้ PDF report พร้อมส่ง! 🚀
```

### 1.2 Time Savings

| Task | Manual | Automated |
|------|--------|-----------|
| Setup 10 cases | 2 hours | 5 minutes |
| Run parametric study | 2 days | 2 hours |
| Generate report | 4 hours | 10 minutes |

### 1.3 What Employers Want

```
❌ "คนที่รันโปรแกรมเป็น"
✅ "คนที่สร้างระบบการทำงานได้"
```

---

## 2. Shell Scripting — Automation Backbone

> **Shell = ภาษาพื้นฐานที่ OpenFOAM ใช้ทุกที่**

### 2.1 Allrun Pattern

**Standard template สำหรับรัน case:**

```bash
#!/bin/bash
cd ${0%/*} || exit 1    # ไปที่ directory ของ script

# Source OpenFOAM functions
. $WM_PROJECT_DIR/bin/tools/RunFunctions

# Pre-processing
runApplication blockMesh
runApplication checkMesh
runApplication setFields

# Solver
runApplication simpleFoam

# Post-processing
runApplication postProcess -func yPlus
```

### 2.2 Allclean Pattern

**Reset case กลับไปสถานะเริ่มต้น:**

```bash
#!/bin/bash
cd ${0%/*} || exit 1

# Remove time directories
rm -rf 0.[0-9]* [1-9]*

# Remove logs
rm -rf log.*

# Remove post-processing
rm -rf postProcessing

# Restore initial conditions
cp -r 0.orig 0
```

### 2.3 RunFunctions

**Functions มาตรฐานใน OpenFOAM:**

| Function | Description |
|----------|-------------|
| `runApplication` | รันคำสั่ง + log to file |
| `runParallel` | รันแบบ parallel |
| `getApplication` | อ่านชื่อ solver จาก controlDict |
| `restore0Dir` | คืน 0 directory |

**ตัวอย่าง:**
```bash
# runApplication blockMesh
# → รัน blockMesh
# → log ไป log.blockMesh
# → ถ้า error → หยุดและแจ้ง
```

### 2.4 Useful Bash Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `grep` | ค้นหาข้อความ | `grep "Time =" log.simpleFoam` |
| `sed` | แก้ไขข้อความ | `sed -i 's/old/new/g' file` |
| `awk` | ดึงข้อมูล | `awk '{print $2}' data.txt` |
| `find` | หาไฟล์ | `find . -name "*.log"` |
| `xargs` | ส่งต่อ arguments | `find . -name "0" | xargs rm -rf` |

### 2.5 Parametric Study with Bash

```bash
#!/bin/bash
# Mesh independence study

for cells in 1000 2000 4000 8000; do
    case_name="mesh_${cells}"
    
    # Clone case
    cp -r base_case $case_name
    
    # Modify blockMeshDict
    sed -i "s/nCells/$cells/g" $case_name/system/blockMeshDict
    
    # Run
    (cd $case_name && ./Allrun)
    
    echo "Completed: $case_name"
done
```

---

## 3. Python Automation — The Modern Approach

> **"Python is the glue that holds the modern CFD workflow together"**

### 3.1 Python CFD Toolbox

```
┌────────────────────────────────────────────────────┐
│          Python CFD Automation Ecosystem           │
├──────────────┬──────────────┬──────────────────────┤
│   PyFoam     │  fluidfoam   │      PyVista         │
│ The Commander│  Data Bridge │   The Visualizer     │
├──────────────┼──────────────┼──────────────────────┤
│ • Run Solver │ • Read Fields│ • 3D Visualization   │
│ • Monitor    │ • NumPy      │ • Slice, Clip        │
│ • Clone Case │ • No VTK     │ • Streamlines        │
└──────────────┴──────────────┴──────────────────────┘
              │
    ┌─────────┴─────────┐
    │  Pandas + Matplotlib │
    │    The Analyst      │
    │ • Statistics        │
    │ • Plotting          │
    │ • Data Processing   │
    └─────────────────────┘
```

### 3.2 PyFoam — The Commander

**ติดตั้ง:**
```bash
pip install PyFoam
```

**รัน Solver จาก Python:**
```python
from PyFoam.Execution.BasicRunner import BasicRunner

runner = BasicRunner(
    argv=["simpleFoam", "-case", "myCase"],
    silent=True
)
runner.start()
```

**Monitor Residuals Real-time:**
```bash
pyFoamPlotRunner.py simpleFoam -case myCase
```

**Clone Case:**
```python
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory

original = SolutionDirectory("base_case")
clone = original.cloneCase("new_case")
```

### 3.3 fluidfoam — Data Bridge

**อ่าน Fields เข้า NumPy โดยตรง:**

```python
from fluidfoam import readfield

# Read velocity field
U = readfield("myCase", "1000", "U")  # Returns (3, nCells) array

# Read pressure
p = readfield("myCase", "1000", "p")  # Returns (nCells,) array

# U is now NumPy → ใช้กับ NumPy/Pandas ได้เลย!
import numpy as np
velocity_magnitude = np.linalg.norm(U, axis=0)
```

### 3.4 PyVista — The Visualizer

**สร้างภาพ 3D โดยไม่ต้องเปิด ParaView:**

```python
import pyvista as pv

# Read VTK file
mesh = pv.read("VTK/myCase_1000.vtk")

# Create plotter
plotter = pv.Plotter(off_screen=True)
plotter.add_mesh(mesh, scalars="p", cmap="jet")
plotter.camera_position = "xy"

# Save screenshot
plotter.screenshot("result.png")
```

**Make Animation:**
```python
for time in times:
    mesh = pv.read(f"VTK/myCase_{time}.vtk")
    plotter.clear()
    plotter.add_mesh(mesh, scalars="U", cmap="jet")
    plotter.write_frame()  # Add to GIF
```

### 3.5 Pandas — Data Analysis

**วิเคราะห์ Forces:**

```python
import pandas as pd
import matplotlib.pyplot as plt

# Read postProcessing output
df = pd.read_csv(
    "postProcessing/forces/0/forces.dat",
    sep=r'\s+',
    skiprows=3,
    names=["time", "Fx", "Fy", "Fz", "Mx", "My", "Mz"]
)

# Plot drag coefficient
plt.figure(figsize=(10, 6))
plt.plot(df["time"], df["Fx"], label="Drag")
plt.xlabel("Time [s]")
plt.ylabel("Force [N]")
plt.legend()
plt.savefig("drag_history.png")

# Statistics
print(f"Average Drag: {df['Fx'].mean():.4f} N")
print(f"Std Dev: {df['Fx'].std():.4f} N")
```

### 3.6 Parametric Study with Python

```python
import os
import pandas as pd
from PyFoam.Execution.BasicRunner import BasicRunner

# Parameters
angles = [0, 2, 4, 6, 8, 10]
results = []

for angle in angles:
    case_name = f"airfoil_aoa_{angle}"
    
    # 1. Clone case
    os.system(f"cp -r base_case {case_name}")
    
    # 2. Modify boundary condition
    # (ใช้ PyFoam หรือ sed)
    modify_bc(case_name, angle)
    
    # 3. Run solver
    runner = BasicRunner(
        argv=["simpleFoam", "-case", case_name],
        silent=True
    )
    runner.start()
    
    # 4. Extract results
    cl, cd = extract_forces(case_name)
    results.append({"angle": angle, "Cl": cl, "Cd": cd})
    
    print(f"AoA {angle}°: Cl = {cl:.4f}, Cd = {cd:.4f}")

# 5. Analyze
df = pd.DataFrame(results)
df.to_csv("parametric_results.csv")

# 6. Plot
df.plot(x="angle", y=["Cl", "Cd"], marker="o")
plt.savefig("cl_cd_vs_aoa.png")
```

---

## 4. HPC & Parallel Computing

> **HPC = Run large CFD on clusters**

### 4.1 Parallel Workflow

```
┌─────────────────────────────────────────────────────┐
│              OpenFOAM Parallel Run                   │
├─────────────────────────────────────────────────────┤
│                                                     │
│  [Original Mesh]                                    │
│        │                                            │
│        ↓ decomposePar                              │
│  ┌─────┼─────┬─────┬─────┐                         │
│  │ P0  │ P1  │ P2  │ P3  │  (4 processor dirs)    │
│  └──┬──┴──┬──┴──┬──┴──┬──┘                         │
│     │     │     │     │                            │
│     ↓     ↓     ↓     ↓   mpirun -np 4            │
│  [Solve][Solve][Solve][Solve]                      │
│     │     │     │     │                            │
│     └──┬──┴──┬──┴──┬──┘                            │
│        ↓ reconstructPar                            │
│  [Reconstructed Result]                            │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 4.2 Key Commands

```bash
# 1. Decompose mesh
decomposePar

# 2. Run in parallel
mpirun -np 16 simpleFoam -parallel

# 3. Reconstruct results
reconstructPar

# Optional: Reconstruct specific times
reconstructPar -time 100:200
```

### 4.3 decomposeParDict

```cpp
// system/decomposeParDict
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      decomposeParDict;
}

numberOfSubdomains  16;

method          scotch;  // หรือ simple, hierarchical

// สำหรับ simple method
simpleCoeffs
{
    n           (4 4 1);
    delta       0.001;
}
```

### 4.4 Decomposition Methods

| Method | Best For | Pros/Cons |
|--------|----------|-----------|
| `simple` | Structured mesh | Fast, แบ่งตามแกน |
| `scotch` | General | ดีที่สุดสำหรับส่วนใหญ่ |
| `hierarchical` | Clustered | สำหรับ multi-node |
| `ptscotch` | Very large | Parallel decomposition |

### 4.5 HPC Job Script (SLURM)

```bash
#!/bin/bash
#SBATCH --job-name=cfdsim
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=32
#SBATCH --time=24:00:00
#SBATCH --partition=compute

# Load OpenFOAM
module load openfoam/v2312

# Source OpenFOAM
source $FOAM_BASHRC

# Run
cd $SLURM_SUBMIT_DIR
decomposePar
mpirun simpleFoam -parallel
reconstructPar
```

### 4.6 Scaling Considerations

| Cells | Processors | Cells/Proc | Expected Speedup |
|-------|------------|------------|------------------|
| 1M | 1 | 1,000,000 | 1x |
| 1M | 8 | 125,000 | ~6-7x |
| 1M | 16 | 62,500 | ~10-12x |
| 1M | 64 | 15,625 | ~15-20x (diminishing) |

**Rule of Thumb:**
- Target: 50,000-200,000 cells per processor
- Too few cells → communication overhead dominates
- Too many → under-utilizing resources

---

## 5. Professional Practices

### 5.1 Project Organization

**Recommended Structure:**

```
project/
├── README.md           # Project description
├── cases/
│   ├── base/           # Template case
│   ├── mesh_study/     # Mesh independence
│   └── production/     # Final runs
├── scripts/
│   ├── run_all.py      # Automation
│   ├── analyze.py      # Post-processing
│   └── plot_results.py # Visualization
├── results/
│   ├── figures/        # Plots
│   └── data/           # CSV outputs
├── docs/
│   └── report.md       # Documentation
└── .gitignore          # Exclude large files
```

### 5.2 Git for CFD

**What to Track:**
```
✅ system/ files (fvSchemes, fvSolution, controlDict)
✅ constant/ files (transportProperties, turbulenceProperties)
✅ 0.orig/ (initial conditions template)
✅ Scripts (Allrun, Python)
✅ Documentation

❌ Time directories (0.001, 0.002, ...)
❌ postProcessing/ (regenerable)
❌ log.* files
❌ processor* directories
```

**.gitignore for OpenFOAM:**
```gitignore
# Time directories
[0-9]*
!0/
!0.orig/

# Parallel
processor*/

# Logs
log.*
*.log

# Post-processing
postProcessing/
VTK/

# Mesh
constant/polyMesh/
!constant/polyMesh/blockMeshDict
```

### 5.3 Essential Utilities

| Category | Utilities |
|----------|-----------|
| **Mesh** | `blockMesh`, `snappyHexMesh`, `checkMesh` |
| **Manipulation** | `setFields`, `mapFields`, `subsetMesh` |
| **Parallel** | `decomposePar`, `reconstructPar` |
| **Post** | `postProcess`, `sample`, `probes` |
| **Debug** | `foamToVTK`, `writeCellCentres` |

### 5.4 Custom Utility Template

```cpp
// myUtility.C
#include "fvCFD.H"

int main(int argc, char *argv[])
{
    #include "setRootCase.H"
    #include "createTime.H"
    #include "createMesh.H"

    // Read fields
    volScalarField p
    (
        IOobject("p", runTime.timeName(), mesh, IOobject::MUST_READ),
        mesh
    );

    // Custom calculation
    scalar pMax = gMax(p);
    scalar pMin = gMin(p);
    
    Info<< "Pressure range: " << pMin << " to " << pMax << endl;

    return 0;
}
```

**Compile:**
```bash
wmake
```

---

## 6. Quick Reference

### 6.1 Shell Commands

| Task | Command |
|------|---------|
| Run case | `./Allrun` |
| Clean case | `./Allclean` |
| Check mesh | `checkMesh` |
| View mesh | `paraFoam` |
| Monitor run | `tail -f log.simpleFoam` |

### 6.2 Python Libraries

| Library | Purpose |
|---------|---------|
| `PyFoam` | Case management, run solver |
| `fluidfoam` | Read fields to NumPy |
| `PyVista` | 3D visualization |
| `Pandas` | Data analysis |
| `Matplotlib` | Plotting |

### 6.3 HPC Commands

| Task | Command |
|------|---------|
| Decompose | `decomposePar` |
| Run parallel | `mpirun -np N solver -parallel` |
| Reconstruct | `reconstructPar` |
| Check decomposition | `checkDecomposePar` |

---

## 7. 🧠 Advanced Concept Check

### Level 1: Fundamentals

<details>
<summary><b>Q1: runApplication vs การรันตรงๆ ต่างกันอย่างไร?</b></summary>

**คำตอบ:**

| Aspect | `runApplication` | Direct run |
|--------|------------------|------------|
| **Logging** | อัตโนมัติ (log.appName) | ต้อง redirect เอง |
| **Error handling** | หยุดทันทีถ้า error | ต้อง check $? เอง |
| **Skip if done** | ถ้ามี log แล้วจะ skip | รันซ้ำทุกครั้ง |

```bash
# runApplication
runApplication blockMesh
# → สร้าง log.blockMesh
# → ถ้า error ก็หยุด

# Direct (ต้องจัดการเอง)
blockMesh > log.blockMesh 2>&1 || exit 1
```

</details>

<details>
<summary><b>Q2: PyFoam, fluidfoam, PyVista ต่างกันอย่างไร?</b></summary>

**คำตอบ:**

| Library | หน้าที่ | ตัวอย่าง |
|---------|--------|----------|
| **PyFoam** | ควบคุม OpenFOAM | รัน solver, clone case |
| **fluidfoam** | อ่านข้อมูล | อ่าน U, p → NumPy |
| **PyVista** | แสดงผล 3D | Slice, screenshot |

**Workflow:**
```
PyFoam: รัน case → fluidfoam: อ่านผล → PyVista: visualize
```

</details>

<details>
<summary><b>Q3: ทำไมต้อง decompose ก่อน parallel run?</b></summary>

**คำตอบ:**

**MPI (Message Passing Interface):**
- แต่ละ processor ทำงานแยกกัน
- ต้องมี "ส่วน" ของ mesh ของตัวเอง
- สื่อสารกันผ่าน boundaries

**decomposePar:**
```
Original mesh (1M cells)
    ↓
processor0/ (250k cells)
processor1/ (250k cells)
processor2/ (250k cells)
processor3/ (250k cells)
```

**reconstructPar:**
```
processor0-3/ → รวมกลับเป็น single mesh
```

</details>

### Level 2: Practical

<details>
<summary><b>Q4: Cells ต่อ processor ควรเป็นเท่าไหร่?</b></summary>

**คำตอบ:**

**Target: 50,000 - 200,000 cells/processor**

| Cells/Proc | Effect |
|------------|--------|
| < 10,000 | MPI overhead สูง, ช้า |
| 50,000-200,000 | Optimal |
| > 500,000 | Processor ใช้ไม่คุ้ม |

**ตัวอย่าง:**
```
Mesh: 4M cells
Optimal: 20-80 processors
(4M/80 = 50k, 4M/20 = 200k)
```

**Strong Scaling Law:**
```
Speedup = T_1 / T_n

Ideal: T_16 = T_1 / 16
Real:  T_16 = T_1 / 12  (75% efficiency)
```

</details>

<details>
<summary><b>Q5: scotch vs simple decomposition ต่างกันอย่างไร?</b></summary>

**คำตอบ:**

| Method | Algorithm | Best For |
|--------|-----------|----------|
| **simple** | แบ่งตามแกน (x, y, z) | Structured, simple geometry |
| **scotch** | Graph partitioning | Complex geometry, general |

**simple:**
```cpp
simpleCoeffs { n (4 4 1); }  // แบ่ง 4x4x1 = 16 processors
```
- เร็ว แต่ quality ไม่ดีสำหรับ complex mesh

**scotch:**
```cpp
method scotch;  // ไม่ต้องตั้งค่าเพิ่ม
```
- ช้ากว่าเล็กน้อย แต่ balance ดีกว่า
- ลด communication ระหว่าง processors

</details>

<details>
<summary><b>Q6: อะไรควร track ใน Git สำหรับ OpenFOAM case?</b></summary>

**คำตอบ:**

**Track:**
```
✅ system/           # fvSchemes, fvSolution, controlDict
✅ constant/         # transportProperties, turbulenceProperties
✅ 0.orig/           # Initial conditions template
✅ Allrun, Allclean  # Scripts
✅ *.py              # Python scripts
```

**Don't Track:**
```
❌ 0.001/, 0.002/    # Time directories (large, regenerable)
❌ processor*/       # Parallel decomposition
❌ postProcessing/   # Regenerable
❌ log.*             # Regenerable
❌ *.foam            # ParaView files
```

**เหตุผล:**
- Time directories อาจมี 10GB+
- Git ไม่เหมาะกับ large binary files
- ใช้ .gitignore จำกัด

</details>

### Level 3: Advanced

<details>
<summary><b>Q7: ทำ Mesh Independence Study อย่างไร?</b></summary>

**คำตอบ:**

**Workflow:**
```python
mesh_sizes = [10000, 20000, 40000, 80000, 160000]
results = []

for n_cells in mesh_sizes:
    # 1. Modify blockMeshDict
    modify_mesh(n_cells)
    
    # 2. Generate mesh
    os.system("blockMesh")
    
    # 3. Run solver
    os.system("simpleFoam")
    
    # 4. Extract result of interest
    cd = extract_drag_coefficient()
    results.append({"cells": n_cells, "Cd": cd})

# 5. Check convergence
# ถ้า Cd ไม่เปลี่ยน >1% → mesh independent
```

**Plot Richardson Extrapolation:**
```python
# h = (1/n_cells)^(1/3)  # characteristic size
# Extrapolate to h → 0
```

</details>

<details>
<summary><b>Q8: fluidfoam vs postProcess -func ต่างกันอย่างไร?</b></summary>

**คำตอบ:**

| Aspect | fluidfoam | postProcess |
|--------|-----------|-------------|
| **Environment** | Python | Command line |
| **Output** | NumPy array | Files |
| **Flexibility** | สูง (Python!) | จำกัด (built-in funcs) |
| **Speed** | เร็ว (direct read) | ช้า (OpenFOAM startup) |

**fluidfoam:**
```python
from fluidfoam import readfield
U = readfield("case", "1000", "U")  # → NumPy array
# ใช้กับ NumPy/Pandas ได้ทันที
```

**postProcess:**
```bash
postProcess -func 'singleGraph(start=(0 0 0), end=(1 0 0))'
# → สร้างไฟล์ใน postProcessing/
```

**Use Case:**
- ต้องการ custom analysis → fluidfoam
- ต้องการ standard output → postProcess

</details>

<details>
<summary><b>Q9: สร้าง Custom Utility อย่างไร?</b></summary>

**คำตอบ:**

**1. สร้าง Directory:**
```bash
mkdir myUtility
cd myUtility
```

**2. เขียน Code (myUtility.C):**
```cpp
#include "fvCFD.H"

int main(int argc, char *argv[])
{
    #include "setRootCase.H"
    #include "createTime.H"
    #include "createMesh.H"

    // Custom code here
    Info<< "Mesh has " << mesh.nCells() << " cells" << endl;

    return 0;
}
```

**3. สร้าง Make/files:**
```
myUtility.C

EXE = $(FOAM_USER_APPBIN)/myUtility
```

**4. สร้าง Make/options:**
```
EXE_INC = \
    -I$(LIB_SRC)/finiteVolume/lnInclude

EXE_LIBS = \
    -lfiniteVolume
```

**5. Compile:**
```bash
wmake
```

**6. Run:**
```bash
myUtility -case myCase
```

</details>

---

## 8. ⚡ Hands-on Challenges

### Challenge 1: Write Allrun (⭐⭐)

**สร้าง Allrun สำหรับ case ที่มี:**
- blockMesh
- snappyHexMesh
- simpleFoam
- postProcess (forces, yPlus)

---

### Challenge 2: Python Parametric Study (⭐⭐⭐)

**สร้าง Python script ที่:**
1. Clone base case 5 ครั้งด้วย Re ต่างกัน
2. แก้ไข transportProperties
3. รัน solver
4. Extract และ plot results

---

### Challenge 3: HPC Job Script (⭐⭐⭐⭐)

**เขียน SLURM job script ที่:**
1. Decompose mesh
2. Run on 64 processors
3. Reconstruct at the end
4. Email notification เมื่อเสร็จ

---

## 9. ❌ Common Mistakes

### Mistake 1: ไม่ใช้ 0.orig

```bash
# ❌ หลัง run แล้ว 0/ ถูก overwrite
rm -rf 0
# ไม่มี initial conditions!

# ✅ ใช้ 0.orig
cp -r 0 0.orig   # ก่อน run
cp -r 0.orig 0   # เวลา clean
```

---

### Mistake 2: Track Time Directories ใน Git

```
# ❌ Git repo ใหญ่มาก
git add .  # รวม 0.001/, 0.002/ ด้วย!

# ✅ ใช้ .gitignore
echo "[0-9]*" >> .gitignore
echo "!0.orig/" >> .gitignore
```

---

### Mistake 3: Over-decompose

```bash
# ❌ 1M cells บน 128 processors
# = 7,800 cells/processor
# MPI overhead > computation!

# ✅ Target 50k-200k cells/processor
# 1M cells → 5-20 processors
```

---

### Mistake 4: ลืม reconstructPar

```bash
# ❌ ดู results ใน processor0/
paraFoam  # เห็นแค่ 1 processor!

# ✅ Reconstruct first
reconstructPar
paraFoam  # เห็นทั้งหมด
```

---

## 10. 🔗 เชื่อมโยงกับ Repository

| หัวข้อ | ไฟล์ใน Repository |
|--------|-------------------|
| **Shell Scripting** | `MODULE_07/01_SHELL_SCRIPTING/` |
| **Python Automation** | `MODULE_07/02_PYTHON_AUTOMATION/` |
| **HPC & Cloud** | `MODULE_07/03_HPC_AND_CLOUD/` |
| **Visualization** | `MODULE_07/04_ADVANCED_VISUALIZATION/` |
| **Professional Practice** | `MODULE_07/05_PROFESSIONAL_PRACTICE/` |
| **Expert Utilities** | `MODULE_07/06_EXPERT_UTILITIES/` |

---

## 11. สรุป: Automation Principles

### หลักการ 5 ข้อ

1. **Automate Everything Repeatable**
   - ถ้าทำซ้ำ 2 ครั้ง → เขียน script

2. **Start with Bash, Scale with Python**
   - Simple automation → Bash
   - Data analysis, parametric → Python

3. **Version Control is Essential**
   - Git for reproducibility
   - .gitignore for large files

4. **Know Your Scaling Limits**
   - 50k-200k cells/processor
   - More processors ≠ always faster

5. **Document as You Go**
   - README.md in every project
   - Comments in scripts

---

*"The best CFD engineer is not the one who runs the most simulations, but the one who extracts the most insight with the least effort"*
