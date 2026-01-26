# Shell Scripting - Overview

ภาพรวม Shell Scripting

---

## Learning Objectives | วัตถุประสงค์การเรียนรู้

**By the end of this module, you will be able to:**

- ✅ **Understand** the role of shell scripting in OpenFOAM workflows
- ✅ **Create** basic `Allrun` and `Allclean` scripts following OpenFOAM conventions
- ✅ **Apply** standard patterns for case automation and reproducibility
- ✅ **Explain** the purpose of key helper functions like `runApplication`
- ✅ **Avoid** common pitfalls in case script development

---

## Overview | ภาพรวม

> **Shell scripts** = Automate OpenFOAM workflows

### What is Shell Scripting in OpenFOAM? | Shell Scripting คืออะไร?

**Shell scripting** is the practice of writing executable text files containing sequences of commands that the Unix shell (typically `bash`) can execute. In OpenFOAM, shell scripts are the primary mechanism for:

- **Automating** simulation workflows (meshing → solving → post-processing)
- **Ensuring** reproducibility of results
- **Standardizing** case setup and execution
- **Simplifying** complex multi-step operations

**Shell scripting** ในบริบทของ OpenFOAM คือการเขียนไฟล์ข้อความที่ประกอบด้วยลำดับคำสั่งที่ shell (โดยปกติคือ `bash`) สามารถ执行 ได้ ใน OpenFOAM สคริปต์มีบทบาทสำคัญใน:

- **การทำงานอัตโนมัติ** ของ workflow การจำลอง (meshing → solving → post-processing)
- **การรับประกัน** การผลิตผลลัพธ์ที่ซ้ำได้
- **การมาตรฐาน** การตั้งค่าและการดำเนินการ
- **การลดความซับซ้อน** ของปฏิบัติการหลายขั้นตอน

### Why Use Shell Scripts? | ทำไมต้องใช้ Shell Scripts?

**Benefits of OpenFOAM shell scripting:**

| Benefit | Description |
|---------|-------------|
| **Reproducibility** | Exact same commands execute every time, eliminating human error |
| **Documentation** | Scripts serve as executable documentation of workflow steps |
| **Efficiency** | One command (`./Allrun`) replaces dozens of manual commands |
| **Portability** | Scripts work across different systems and OpenFOAM versions |
| **Version Control** | Changes to workflow are tracked in git history |
| **Collaboration** | Team members can run identical simulations without confusion |

**ข้อดีของการใช้ shell scripts:**

| ข้อดี | คำอธิบาย |
|--------|-------------|
| **การทำซ้ำได้** | คำสั่งเดิมทำงานเหมือนเดิมทุกครั้ง ลดข้อผิดพลาดจากมนุษย์ |
| **เอกสาร** | สคริปต์ทำหน้าที่เป็นเอกสารที่ execute ได้ของ workflow |
| **ประสิทธิภาพ** | คำสั่งเดียว (`./Allrun`) แทนการพิมพ์หลายสิบคำสั่ง |
| **ความเป็นสากล** | ทำงานได้บนระบบและเวอร์ชัน OpenFOAM ต่างๆ |
| **การควบคุมเวอร์ชัน** | การเปลี่ยนแปลง workflow ถูกติดตามในประวัติ git |
| **การทำงานร่วมกัน** | สมาชิกในทีมสามารถรันการจำลองเหมือนกันโดยไม่สับสน |

### How Do Shell Scripts Work? | สคริปต์ทำงานอย่างไร?

**Basic script anatomy:**

```
#!/bin/bash          ← Shebang: Tells system which interpreter to use
cd1${0%/*} || exit 1 ← Navigate to script directory (robust path handling)
# Commands here...   ← Actual OpenFOAM commands
```

**Key components:**

1. **Shebang (`#!/bin/bash`)**: First line specifying the interpreter program
2. **Path navigation**: `cd1${0%/*}` ensures script works from any directory
3. **Command execution**: Sequential execution of OpenFOAM utilities
4. **Error handling**: `|| exit 1` stops execution if commands fail

**ส่วนประกอบพื้นฐานของสคริปต์:**

1. **Shebang (`#!/bin/bash`)**: บรรทัดแรกระบุโปรแกรม interpreter
2. **การนำทางเส้นทาง**: `cd1${0%/*}` รับประกันว่าสคริปต์ทำงานจากไดเรกทอรีใดก็ได้
3. **การ execute คำสั่ง**: การ execute ตามลำดับของ utilities ของ OpenFOAM
4. **การจัดการข้อผิดพลาด**: `|| exit 1` หยุดการ execute หากคำสั่งล้มเหลว

---

## Allrun/Allclean Workflow | ขั้นตอนการทำงาน

```
┌─────────────────────────────────────────────────────────────┐
│                    OpenFOAM Case                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│    ┌──────────────┐         ┌──────────────┐               │
│    │   Allrun     │────────>│  Simulation  │               │
│    │              │         │    Results   │               │
│    └──────────────┘         └──────────────┘               │
│         │                                                    │
│         │ One command                                       │
│         │                                                    │
│         ▼                                                    │
│    ┌────────────────────────────────────────┐              │
│    │  1. blockMesh      (Create mesh)       │              │
│    │  2. snappyHexMesh  (Refine mesh)       │              │
│    │  3. decomposePar   (Parallel setup)    │              │
│    │  4. solver         (Run simulation)    │              │
│    │  5. reconstructPar (Merge results)     │              │
│    └────────────────────────────────────────┘              │
│                                                              │
│    ┌──────────────┐         ┌──────────────┐               │
│    │  Allclean    │────────>│   Clean      │               │
│    │              │         │   State      │               │
│    └──────────────┘         └──────────────┘               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. Allrun Pattern | รูปแบบ Allrun

### Complete Template | เทมเพลตที่สมบูรณ์

```bash
#!/bin/bash
cd1${0%/*} || exit 1    # Navigate to script directory
.1$WM_PROJECT_DIR/bin/tools/RunFunctions  # Load OpenFOAM helper functions

# Mesh generation
runApplication blockMesh

# Optional: Mesh refinement
if [ -f system/snappyHexMeshDict ]
then
    runApplication snappyHexMesh
fi

# Decompose for parallel run
runApplication decomposePar

# Run solver (adjust number of cores as needed)
runApplication simpleFoam

# Reconstruct parallel results
runApplication reconstructPar

# Post-processing
runApplication foamToVTK
```

### Breaking Down the Pattern | การวิเคราะห์รูปแบบ

```bash
#!/bin/bash
├─ Shebang line - specifies bash interpreter
│
cd1${0%/*} || exit 1
├─1${0%/*} = directory containing this script
├─ cd = change to that directory
└─ || exit 1 = stop if directory change fails
│
.1$WM_PROJECT_DIR/bin/tools/RunFunctions
├─ . (dot) = source command (load functions into current shell)
├─1$WM_PROJECT_DIR = OpenFOAM installation directory
└─ Provides: runApplication, runParallel, etc.
│
runApplication blockMesh
├─ Wrapper around actual command
├─ Creates log.blockMesh file automatically
└─ Continues or stops based on success/failure
```

### Common Variations | รูปแบบที่พบบ่อย

**Sequential solvers (for convergence studies):**

```bash
#!/bin/bash
cd1${0%/*} || exit 1
.1$WM_PROJECT_DIR/bin/tools/RunFunctions

runApplication simpleFoam
runApplication `(new solver)`
runApplication postProcess -func "yPlus"
```

**Parallel execution with specified cores:**

```bash
#!/bin/bash
cd1${0%/*} || exit 1
.1$WM_PROJECT_DIR/bin/tools/RunFunctions

runApplication decomposePar
runParallel simpleFoam 4          # Run on 4 cores
runApplication reconstructPar
```

---

## 2. Allclean Pattern | รูปแบบ Allclean

### Complete Template | เทมเพลตที่สมบูรณ์

```bash
#!/bin/bash
cd1${0%/*} || exit 1    # Navigate to script directory

# Remove all time directories except 0 and 0.orig
rm -rf 0.[0-9]* [1-9]* processor* 

# Remove log files
rm -rf log.*

# Remove post-processing directories
rm -rf postProcessing sets surfaces sampleSurfaces

# Remove VTK and other visualization files
rm -rf VTK *.vtk

# Reset initial conditions from backup
cp -rf 0.orig 0
```

### Safety Features | คุณสมบัติความปลอดภัย

```bash
#!/bin/bash
cd1${0%/*} || exit 1

# Preserve 0.orig directory
echo "Cleaning case directory..."
echo "Preserving 0.orig directory"

# Selective cleaning with confirmation
read -p "Remove processor directories? (y/n) " -n 1 -r
echo
if [[1$REPLY =~ ^[Yy]1]]
then
    rm -rf processor*
    echo "Processor directories removed"
fi

# Standard cleanup
rm -rf 0.[0-9]* [1-9]* log.* postProcessing

# Always reset initial conditions
cp -rf 0.orig 0
echo "Initial conditions reset from 0.orig"
```

### What Gets Cleaned? | อะไรถูกลบออก?

| Pattern | What it Removes | Why |
|---------|-----------------|-----|
| `0.[0-9]*` | Time directories 0.1, 0.2, etc. | Intermediate timesteps |
| `[1-9]*` | Time directories 1, 2, 3, etc. | Solution timesteps |
| `processor*` | Parallel decomposition directories | Parallel run artifacts |
| `log.*` | All log files | Previous execution logs |
| `postProcessing` | Function object results | Post-processing data |
| `VTK`, `*.vtk` | Visualization files | ParaView/viewer files |

| รูปแบบ | ที่ลบออก | ทำไม |
|--------|-----------------|-----|
| `0.[0-9]*` | ไดเรกทอรีเวลา 0.1, 0.2, ฯลฯ | Timesteps ระหว่างหัวข้อ |
| `[1-9]*` | ไดเรกทอรีเวลา 1, 2, 3, ฯลฯ | Timesteps ของโซลูชัน |
| `processor*` | ไดเรกทอรีการแยกส่วนขนาน | อาร์ติแฟกต์การรันแบบขนาน |
| `log.*` | ไฟล์ log ทั้งหมด | บันทึกการ execute ครั้งก่อน |
| `postProcessing` | ผลลัพธ์ของ function object | ข้อมูล post-processing |
| `VTK`, `*.vtk` | ไฟล์การแสดงผล | ไฟล์ ParaView/viewer |

---

## 3. Module Contents | เนื้อหาโมดูล

| File | Topic | Description |
|------|-------|-------------|
| [01_Strategy](01_Strategy.md) | Planning | กลยุทธ์การวางแผน automation |
| [02_Framework](02_Framework.md) | Templates | เฟรมเวิร์กและเทมเพลตมาตรฐาน |

---

## Quick Reference | คู่มืออ้างอิง

### Script Types | ประเภทของสคริปต์

| Script | Purpose | When to Use | Example Content |
|---------|---------|-------------|-----------------|
| **Allrun** | Run complete case | Standard simulation workflow | Mesh → Decompose → Solve → Reconstruct |
| **Allclean** | Clean case artifacts | Starting fresh simulation | Remove time dirs, logs, processor dirs |
| **Allrun.pre** | Pre-processing only | Mesh generation/refinement testing | blockMesh, snappyHexMesh |
| **Allrun.post** | Post-processing only | Extracting results from completed run | foamToVTK, sampleDict |

### Shebang Options | ตัวเลือก Shebang

| Shebang | Interpreter | Use Case |
|---------|-------------|----------|
| `#!/bin/bash` | Bash shell | **DEFAULT** - Most OpenFOAM scripts |
| `#!/bin/sh` | POSIX shell | Maximum portability (basic scripts only) |
| `#!/usr/bin/env python3` | Python 3 | Advanced scripting with Python libraries |

### Common Helper Functions | ฟังก์ชันช่วยทั่วไป

| Function | Source | What It Does |
|----------|--------|--------------|
| `runApplication` | `RunFunctions` | Execute command with logging to `log.<app>` |
| `runParallel` | `RunFunctions` | Execute in parallel with specified cores |
| `getApplication` | `RunFunctions` | Detect solver name from controlDict |
| `cloneCase` | `RunFunctions` | Copy entire case directory structure |

### Path Patterns | รูปแบบเส้นทาง

| Pattern | Meaning | Example |
|---------|---------|---------|
| `${0%/*}` | Directory of script | `/path/to/case` (if script is `/path/to/case/Allrun`) |
| `$WM_PROJECT_DIR` | OpenFOAM installation | `/opt/openfoam9` |
| `$FOAM_RUN` | User run directory | `~/OpenFOAM/user-9/run` |
| `$FOAM_TUTORIALS` | Tutorial directory | `/opt/openfoam9/tutorials` |

---

## Common Pitfalls | ข้อผิดพลาดทั่วไป

### ❌ Bad Practices | การปฏิบัติที่ไม่ถูกต้อง

```bash
#!/bin/bash
# PROBLEM: No path navigation - assumes executed from case directory
runApplication blockMesh

# PROBLEM: No error handling
rm -rf 0.*  # Might delete 0.orig if not careful!

# PROBLEM: Hard-coded paths
cp /home/user/OpenFOAM/templates/0.orig 0

# PROBLEM: No shebang
./myScript.sh  # Might use wrong shell!
```

### ✅ Best Practices | แนวปฏิบัติที่ดีที่สุด

```bash
#!/bin/bash
# SOLUTION: Always navigate to script directory
cd1${0%/*} || exit 1

# SOLUTION: Use specific patterns, verify backups exist
if [ -d 0.orig ]
then
    cp -rf 0.orig 0
else
    echo "ERROR: 0.orig not found!"
    exit 1
fi

# SOLUTION: Use OpenFOAM environment variables
templateDir=$FOAM_TUTORIALS/incompressible/simpleFoam/airFoil2D
if [ -d "$templateDir" ]
then
    cp -rf1$templateDir/0.orig .
fi

# SOLUTION: Always specify shebang
#!/bin/bash
```

### Pitfall Checklist | รายการตรวจสอบข้อผิดพลาด

- [ ] **Always** start with `#!/bin/bash` shebang
- [ ] **Always** include `cd1${0%/*} || exit 1`
- [ ] **Never** hard-code absolute paths (use `$WM_PROJECT_DIR`)
- [ ] **Always** backup `0` to `0.orig` before cleaning
- [ ] **Never** use `rm -rf 0.*` without checking `0.orig` exists
- [ ] **Always** use `runApplication` instead of direct commands (for logging)
- [ ] **Always** make scripts executable: `chmod +x Allrun`
- [ ] **Never** assume user is in case directory when executing

---

## Key Takeaways | สรุปสิ่งสำคัญ

### Core Concepts | แนวคิดหลัก

1. **Shell scripts are the foundation of OpenFOAM automation**
   - Transform manual workflows into repeatable, documented processes
   - Enable collaboration through standardized execution methods

2. **Always follow the standard Allrun/Allclean pattern**
   - Start with shebang and path navigation
   - Use `runApplication` for consistent logging
   - Provide `Allclean` for clean case reset

3. **Scripts should be portable and robust**
   - Use relative paths and environment variables
   - Include error handling (`|| exit 1`)
   - Test on different systems/OpenFOAM versions

4. **Shell scripts serve as executable documentation**
   - Well-written scripts explain the workflow implicitly
   - Comment complex operations for future maintainers
   - Include in version control for workflow tracking

### Remember | จำไว้

> **Every OpenFOAM case should have `Allrun` and `Allclean` scripts.**  
> This is not just a convention—it's essential for reproducible CFD simulations.

**ทุกกรณี OpenFOAM ควรมีสคริปต์ `Allrun` และ `Allclean`**  
นี่ไม่ใช่แค่约定—มันจำเป็นสำหรับการจำลอง CFD ที่ทำซ้ำได้

---

## 🧠 Concept Check | ทดสอบความเข้าใจ

<details>
<summary><b>1. What does runApplication do? | runApplication ทำอะไร?</b></summary>

**Answer:** `runApplication` is an OpenFOAM helper function that:
1. Executes the specified command (e.g., `blockMesh`)
2. Automatically creates a log file (`log.blockMesh`)
3. Checks if the command succeeded (returns error code)
4. Continues or stops script execution based on success/failure

**คำตอบ:** `runApplication` เป็นฟังก์ชันช่วยของ OpenFOAM ที่:
1. Execute คำสั่งที่ระบุ (เช่น `blockMesh`)
2. สร้างไฟล์ log โดยอัตโนมัติ (`log.blockMesh`)
3. ตรวจสอบว่าคำสั่งสำเร็จหรือไม่ (รหัสข้อผิดพลาด)
4. ดำเนินการหรือหยุดสคริปต์ตามความสำเร็จ/ล้มเหลว

**Why use it instead of direct commands?**  
- Automatic logging (don't have to redirect output manually)
- Consistent error handling (script stops on failure)
- Standardized output format across OpenFOAM installations

**ทำไมต้องใช้แทนคำสั่งโดยตรง?**  
- Logging อัตโนมัติ (ไม่ต้อง redirect output ด้วยตนเอง)
- การจัดการข้อผิดพลาดที่สม่ำเสมอ (สคริปต์หยุดเมื่อล้มเหลว)
- รูปแบบ output มาตรฐานในการติดตั้ง OpenFOAM
</details>

<details>
<summary><b>2. Why use Allrun and Allclean? | ทำไมต้องใช้ Allrun และ Allclean?</b></summary>

**Answer:**

**Allrun:**
- **Standardized workflow** - One command executes entire simulation pipeline
- **Reproducibility** - Exact same steps every time, eliminating human error
- **Documentation** - Script serves as executable documentation of workflow
- **Collaboration** - Team members can run identical simulations without confusion
- **Version control** - Changes to workflow tracked in git history

**Allclean:**
- **Clean state** - Remove all results to restart simulation from scratch
- **Disk space** - Remove large time directories and processor files
- **Testing** - Easy to test different mesh/solver settings without conflicts
- **Backup preservation** - Safely restore initial conditions from `0.orig`

**คำตอบ:**

**Allrun:**
- **Workflow มาตรฐาน** - คำสั่งเดียว execute pipeline การจำลองทั้งหมด
- **การทำซ้ำได้** - ขั้นตอนเหมือนเดิมทุกครั้ง ลบข้อผิดพลาดจากมนุษย์
- **เอกสาร** - สคริปต์ทำหน้าที่เป็นเอกสารที่ execute ได้ของ workflow
- **การทำงานร่วมกัน** - สมาชิกในทีมสามารถรันการจำลองเหมือนกันโดยไม่สับสน
- **การควบคุมเวอร์ชัน** - การเปลี่ยนแปลง workflow ถูกติดตามในประวัติ git

**Allclean:**
- **สถานะสะอาด** - ลบผลลัพธ์ทั้งหมดเพื่อเริ่มการจำลองใหม่
- **พื้นที่ดิสก์** - ลบไดเรกทอรีเวลาและไฟล์ processor ขนาดใหญ่
- **การทดสอบ** - ทดสอบการตั้งค่า mesh/solver ที่แตกต่างได้ง่ายโดยไม่มีความขัดแย้ง
- **การรักษาข้อมูลสำรอง** - กู้คืนเงื่อนไขเริ่มต้นจาก `0.orig` อย่างปลอดภัย

**Together, they ensure any case can be:**  
- Run with a single command (`./Allrun`)  
- Reset to clean state (`./Allclean`)  
- Reproduced exactly by anyone with access to the case directory

**ร่วมกัน พวกเขารับประกันว่ากรณีใดๆ สามารถ:**  
- รันด้วยคำสั่งเดียว (`./Allrun`)  
- รีเซ็ตเป็นสถานะสะอาด (`./Allclean`)  
- ผลิตซ้ำได้อย่างแม่นยำโดยใครก็ตามที่มีสิทธิ์เข้าถึงไดเรกทอรีกรณี
</details>

<details>
<summary><b>3. What does1${0%/*} mean and why is it important? |1${0%/*} หมายถึงอะไรและทำไมสำคัญ?</b></summary>

**Answer:** 

`${0%/*}` is a bash parameter expansion that extracts the **directory path** from the script's own location:

- `$0` = The script's own path (e.g., `/home/user/foam/run/case/Allrun`)
- `%/*` = Remove shortest match of `/*` from the end (removes filename)
- Result = Directory path (e.g., `/home/user/foam/run/case`)

**Example:**
```bash
# If script is: /home/user/OpenFOAM/run/myCase/Allrun
${0%/*}  # Expands to: /home/user/OpenFOAM/run/myCase
cd1${0%/*} || exit 1  # Change to that directory
```

**`${0%/*}` เป็นการขยายพารามิเตอร์ bash ที่ดึง** เส้นทางไดเรกทอรี **จากตำแหน่งของสคริปต์เอง:**

- `$0` = เส้นทางของสคริปต์เอง (เช่น `/home/user/foam/run/case/Allrun`)
- `%/*` = ลบการจับคู่ที่สั้นที่สุดของ `/*` จากตอนท้าย (ลบชื่อไฟล์)
- ผลลัพธ์ = เส้นทางไดเรกทอรี (เช่น `/home/user/foam/run/case`)

**Why it's important:**

| Without `cd1${0%/*}` | With `cd1${0%/*}` |
|---------------------|-------------------|
| Must be in case directory to run | Can run from any directory |
| `./Allrun` works, `../case/Allrun` fails | Both work correctly |
| Relative paths break | Relative paths work |
| Users must know location | Location independent |

**ทำไมสำคัญ:**

| โดยไม่มี `cd1${0%/*}` | ด้วย `cd1${0%/*}` |
|---------------------|-------------------|
| ต้องอยู่ในไดเรกทอรีกรณีเพื่อรัน | สามารถรันจากไดเรกทอรีใดก็ได้ |
| `./Allrun` ทำงาน, `../case/Allrun` ล้มเหลว | ทั้งคู่ทำงานได้อย่างถูกต้อง |
| เส้นทางสัมพัทธ์เสีย | เส้นทางสัมพัทธ์ทำงาน |
| ผู้ใช้ต้องรู้ตำแหน่ง | ไม่ขึ้นกับตำแหน่ง |

**Best practice:** Always include this line at the start of every OpenFOAM script!

**แนวปฏิบัติที่ดีที่สุด:** ควรรวมบรรทัดนี้ไว้ตอนเริ่มของทุกสคริปต์ OpenFOAM!
</details>

<details>
<summary><b>4. What is the purpose of the shebang line (#!/bin/bash)? | จุดประสงค์ของบรรทัด shebang (#!/bin/bash) คืออะไร?</b></summary>

**Answer:**

The **shebang** (`#!`) is a special line at the very beginning of a script that tells the **operating system which interpreter to use** when executing the script.

**How it works:**

```bash
#!/bin/bash    ← Shebang: Use /bin/bash to interpret this file
# Rest of script...
```

**Without shebang:**
- System uses default shell (often `/bin/sh`)
- Bash-specific features may fail
- Behavior varies across systems

**With shebang:**
- System explicitly uses `/bin/bash`
- Bash features work consistently
- Behavior is predictable across systems

**Shebang คืออะไร:** บรรทัด **shebang** (`#!`) เป็นบรรทัดพิเศษที่ตอนเริ่มของสคริปต์ที่บอก **ระบบปฏิบัติการว่าจะใช้ interpreter ใด** เมื่อ execute สคริปต์

**ตัวอย่าง shebang ทั่วไป:**

| Shebang | Interpreter | When to Use |
|---------|-------------|-------------|
| `#!/bin/bash` | Bash | **DEFAULT** for OpenFOAM scripts |
| `#!/bin/sh` | POSIX shell | Maximum portability |
| `#!/usr/bin/env python3` | Python 3 | Python scripting |

**Why it's critical for OpenFOAM:**

Many OpenFOAM scripts use **bash-specific features** like:
- Parameter expansion (`${0%/*}`)
- Arrays (`applications=(blockMesh snappyHexMesh)`)
- Double brackets `[[` for tests
- Certain pattern matching

Without `#!/bin/bash`, these might fail on systems where `/bin/sh` is not bash.

**ทำไมสำคัญสำหรับ OpenFOAM:**

สคริปต์ OpenFOAM หลายตัวใช้ **คุณสมบัติเฉพาะของ bash** เช่น:
- การขยายพารามิเตอร์ (`${0%/*}`)
- อาร์เรย์ (`applications=(blockMesh snappyHexMesh)`)
- วงเล็บคู่ `[[` สำหรับการทดสอบ
- การจับคู่รูปแบบบางอย่าง

โดยไม่มี `#!/bin/bash` เหล่านี้อาจล้มเหลวบนระบบที่ `/bin/sh` ไม่ใช่ bash

**Rule:** **Always** start OpenFOAM scripts with `#!/bin/bash`

**กฎ:** **ควร** เริ่มสคริปต์ OpenFOAM ด้วย `#!/bin/bash` เสมอ
</details>

<details>
<summary><b>5. How do you make a script executable? | คุณทำให้สคริปต์ execute ได้อย่างไร?</b></summary>

**Answer:**

Use the `chmod` command to make a script executable:

```bash
chmod +x Allrun     # Make Allrun executable
chmod +x Allclean   # Make Allclean executable
```

**What `chmod +x` does:**

- `chmod` = Change mode (modify file permissions)
- `+x` = Add execute permission
- Allows the script to be run directly: `./Allrun`

**Verification:**

```bash
ls -l Allrun  # Check permissions
# Output: -rwxr-xr-x 1 user group 1234 Jan 1 12:00 Allrun
#           ^^^
#           Execute permissions (x = executable)
```

**Common permission issues:**

```bash
# Problem: Permission denied
./Allrun
bash: ./Allrun: Permission denied

# Solution: Add execute permission
chmod +x Allrun
./Allrun  # Now works!
```

**ใช้คำสั่ง `chmod` เพื่อทำให้สคริปต์ execute ได้:**

```bash
chmod +x Allrun     # ทำให้ Allrun execute ได้
chmod +x Allclean   # ทำให้ Allclean execute ได้
```

**การตรวจสอบ:**

```bash
ls -l Allrun  # ตรวจสอบการอนุญาต
# ผลลัพธ์: -rwxr-xr-x 1 user group 1234 Jan 1 12:00 Allrun
#           ^^^
#           การอนุญาตในการ execute (x = executable)
```

**ปัญหาการอนุญาตทั่วไป:**

```bash
# ปัญหา: การอนุญาตถูกปฏิเสธ
./Allrun
bash: ./Allrun: Permission denied

# วิธีแก้: เพิ่มการอนุญาต execute
chmod +x Allrun
./Allrun  # ตอนนี้ทำงาน!
```

**Alternative (if you can't change permissions):**

```bash
bash Allrun    # Run using bash interpreter explicitly
```

**ทางเลือก (หากคุณไม่สามารถเปลี่ยนการอนุญาต):**

```bash
bash Allrun    # รันโดยใช้ interpreter bash อย่างชัดเจน
```
</details>

---

## 📖 Related Documents | เอกสารที่เกี่ยวข้อง

- **[Strategy](01_Strategy.md)** — กลยุทธ์การวางแผนและออกแบบระบบ automation
- **[Framework](02_Framework.md)** — เฟรมเวิร์กและเทมเพลตมาตรฐานสำหรับการพัฒนาสคริปต์

---

**Next:** [01_Strategy.md](01_Strategy.md) — Learn how to plan your automation strategy effectively