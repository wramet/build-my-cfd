# Automation Framework

เฟรมเวิร์กสำหรับการสร้างระบบอัตโนมัติใน OpenFOAM
Framework for building automation systems in OpenFOAM

---

## 🎯 Learning Objectives

หลังจากอ่านบทนี้ คุณจะสามารถ:
- **เข้าใจ** แนวคิดของ Automation Framework และประโยชน์ที่ได้รับ
- **ใช้งาน** RunFunctions ได้อย่างมีประสิทธิภาพ
- **เลือกใช้** วิธี Error Handling ที่เหมาะสมกับงานแต่ละประเภท
- **สร้าง** Parametric Studies สำหรับ Parameter Sweep
- **จัดการ** Parallel Batch Processing อย่างปลอดภัย
- **หลีกเลี่ยง** Common Pitfalls ในการเขียน Automation Scripts

After studying this section, you will be able to:
- **Understand** Automation Framework concepts and their benefits
- **Use** RunFunctions effectively
- **Choose** appropriate Error Handling methods for different tasks
- **Create** Parametric Studies for Parameter Sweeps
- **Manage** Parallel Batch Processing safely
- **Avoid** Common Pitfalls in automation scripting

---

## 📚 Overview

### What is Automation Framework?

**Automation Framework** คือชุดของฟังก์ชัน เทมเพลต และมาตรฐานที่ OpenFOAM จัดเตรียมไว้เพื่อให้การเขียนสคริปต์ง่ายขึ้น สอดคล้องกัน และนำกลับมาใช้ใหม่ได้

**Automation Framework** is a collection of functions, templates, and standards provided by OpenFOAM to make scripting easier, consistent, and reusable.

### Why Use It?

| ประโยชน์ (Benefits) | คำอธิบาย |
|---------------------|----------|
| **Consistency** | สคริปต์ทุกไฟล์ใช้โครงสร้างเดียวกัน ง่ายต่อการดูแลรักษา |
| **Error Handling** | จัดการข้อผิดพลาดอัตโนมัติ ไม่ต้องเขียนเองทุกครั้ง |
| **Logging** | บันทึกการทำงานโดยอัตโนมัติ ตรวจสอบปัญหาได้ง่าย |
| **Parallel Ready** | รองรับการทำงานแบบ Parallel โดยไม่ต้องแก้โค้ด |

| Benefits | Description |
|----------|-------------|
| **Consistency** | All scripts follow the same structure, easier to maintain |
| **Error Handling** | Automatic error management, no need to write from scratch |
| **Logging** | Automatic operation logging, easier debugging |
| **Parallel Ready** | Built-in parallel processing support |

### How It Works

Framework ประกอบด้วย:
1. **RunFunctions Library** - ฟังก์ชันมาตรฐานใน `$WM_PROJECT_DIR/bin/tools/RunFunctions`
2. **Shell Scripting Conventions** - มาตรฐานการเขียนสคริปต์
3. **Template System** - โครงสร้าง Case ที่นำมาใช้ซ้ำได้

The framework consists of:
1. **RunFunctions Library** - Standard functions in `$WM_PROJECT_DIR/bin/tools/RunFunctions`
2. **Shell Scripting Conventions** - Script writing standards
3. **Template System** - Reusable case structures

---

## 1. Standard Functions

### What are RunFunctions?

**RunFunctions** เป็น library ของฟังก์ชันที่ OpenFOAM จัดเตรียมไว้เพื่อให้การเรียกใช้ solver และ utility สะดวกและสอดคล้องกัน

**RunFunctions** is a library of functions provided by OpenFOAM for convenient and consistent execution of solvers and utilities.

### How runApplication Works Internally

```bash
runApplication blockMesh
```

เบื้องหลังทำงานอย่างไร:
1. **Log Execution**: บันทึกชื่อคำสั่งลงใน `log.<application>`
2. **Run Command**: ดำเนินการคำสั่งจริง (เช่น `blockMesh`)
3. **Check Exit Code**: ตรวจสอบว่าคำสั่งสำเร็จหรือไม่ (exit code 0 = success)
4. **Handle Error**: ถ้าล้มเหลว หยุดสคริปต์และแจ้ง error
5. **Resume Support**: ถ้า run ซ้ำ ข้ามคำสั่งที่สำเร็จแล้ว (ตรวจ `log.*`)

How it works internally:
1. **Log Execution**: Records command name to `log.<application>`
2. **Run Command**: Executes the actual command (e.g., `blockMesh`)
3. **Check Exit Code**: Verifies success (exit code 0 = success)
4. **Handle Error**: Stops script and reports error if failed
5. **Resume Support**: On re-run, skips already completed commands (checks `log.*`)

### Usage Examples

```bash
#!/bin/bash

# Source the RunFunctions library
.1$WM_PROJECT_DIR/bin/tools/RunFunctions

# Standard workflow
runApplication blockMesh
runApplication decomposePar
runParallel simpleFoam 4
runApplication reconstructPar

# With custom arguments
runApplication topoSet -dict system/topoSetDict.custom

# Utility operations
runApplication foamListTimes
runApplication foamCloneCase original case_copy
```

### Available Functions

| ฟังก์ชัน | การใช้งาน | ตัวอย่าง |
|---------|-----------|--------|
| `runApplication` | รันคำสั่ง single process | `runApplication blockMesh` |
| `runParallel` | รันคำสั่งแบบ parallel | `runParallel simpleFoam 4` |
| `cloneCase` | คัดลอก case พร้อม log | `cloneCase base case_01` |

| Function | Usage | Example |
|----------|-------|---------|
| `runApplication` | Run single process command | `runApplication blockMesh` |
| `runParallel` | Run parallel command | `runParallel simpleFoam 4` |
| `cloneCase` | Clone case with logs | `cloneCase base case_01` |

---

## 2. Error Handling

### Why Error Handling Matters

ใน OpenFOAM simulations ข้อผิดพลาดหนึ่งจุดทำให้ทั้ง workflow ผิดพลาด การหยุดทันทีช่วย:
- ประหยัดเวลา (ไม่รัน solver บน mesh พัง)
- ประหยัดทรัพยากร (ไม่สิ้นเปลือง CPU)
- บันทึก error ไว้วิเคราะห์

In OpenFOAM simulations, a single error breaks the entire workflow. Stopping immediately helps:
- Save time (don't run solver on broken mesh)
- Save resources (don't waste CPU)
- Preserve error information for analysis

### set -e vs || exit Pattern

#### 1. set -e (Exit on Any Error)

```bash
#!/bin/bash
set -e  # Exit immediately if any command fails

blockMesh
snappyHexMesh
simpleFoam

# ถ้า blockMesh ล้มเหลว สคริปต์หยุดทันที ไม่รันต่อ
```

**เมื่อไหร่ควรใช้:**
- **Simple workflows** ที่ต้องการหยุดทุกครั้งที่มี error
- **Sequential dependencies** ที่ขั้นตอนถัดไปขึ้นกับขั้นตอนก่อนหน้า
- **Quick prototyping** ที่ต้องการ fail-fast

**When to use:**
- **Simple workflows** where you want to stop on every error
- **Sequential dependencies** where later steps depend on earlier ones
- **Quick prototyping** requiring fail-fast behavior

#### 2. || exit Pattern (Selective Error Handling)

```bash
#!/bin/bash
# ไม่ใช้ set -e เพื่อให้ควบคุมได้ทีละคำสั่ง

blockMesh || exit 1
snappyHexMesh || exit 1
simpleFoam || exit 1

# หรือ handle error แต่ละอย่างแยกกัน
blockMesh || {
    echo "ERROR: blockMesh failed"
    exit 1
}

# หรือทำอย่างอื่นถ้า error
if ! blockMesh; then
    echo "Mesh generation failed, trying alternative..."
    blockMesh -dict system/blockMeshDict.alt || exit 1
fi
```

**เมื่อไหร่ควรใช้:**
- **Complex workflows** ที่ต้องการ custom error handling
- **Fallback mechanisms** ที่มีทางเลือกสำรอง
- **Partial success scenarios** ที่บางขั้นตอน fail ได้

**When to use:**
- **Complex workflows** requiring custom error handling
- **Fallback mechanisms** with alternatives
- **Partial success scenarios** where some steps can fail

### Comparison Table

| แนวทาง | ข้อดี | ข้อเสีย | Use Case |
|--------|--------|---------|----------|
| `set -e` | Simple, concise | No flexibility | Standard workflows |
| `|| exit` | Granular control | More verbose | Complex workflows |
| Manual `if` | Maximum control | Very verbose | Fallback scenarios |

| Approach | Pros | Cons | Use Case |
|----------|------|------|----------|
| `set -e` | Simple, concise | No flexibility | Standard workflows |
| `|| exit` | Granular control | More verbose | Complex workflows |
| Manual `if` | Maximum control | Very verbose | Fallback scenarios |

### Common Pitfalls

❌ **Wrong:**
```bash
#!/bin/bash
set -e

# นี่ไม่หยุดเมื่อ grep ไม่เจอคำ
grep "value" file.txt || true  # || true makes it always succeed

# หรือ pipe ไม่สนใจ error
someCommand | grep "pattern"  # Exit status จะเป็นของ grep
```

✅ **Correct:**
```bash
#!/bin/bash
set -e

# ใช้ pipefail ถ้าต้องการตรวจสอบ pipe
set -o pipefail
someCommand | grep "pattern"

# หรือ disable set -e ชั่วคราว
set +e
grep "value" file.txt || true
set -e
```

---

## 3. Parametric Studies

### What is Parametric Study?

**Parametric Study** คือการรัน simulation หลายครั้งโดยเปลี่ยนค่า parameter ตัวหนึ่ง (หลายตัว) เพื่อศึกษาผลกระทบ

**Parametric Study** is running multiple simulations while varying one or more parameters to study their effects.

### Why Automate?

- **Efficiency:** รันทั้ง night โดยไม่ต้อง monitor
- **Consistency:** ทุก case ใช้ workflow เดียวกัน
- **Reproducibility:** ง่ายต่อการ track ว่าค่าไหนให้ผลลัพธ์อย่างไร

- **Efficiency:** Run overnight without monitoring
- **Consistency:** Every case uses identical workflow
- **Reproducibility:** Easy to track which parameter gives which result

### How It Works: Template System

```bash
#!/bin/bash
# parametricStudy.sh

# ========================================
# Configuration
# ========================================
TEMPLATE_CASE="base_case"
OUTPUT_DIR="parametric_results"
RE_VALUES=(100 500 1000 2000 5000)

# ========================================
# Setup
# ========================================
mkdir -p1$OUTPUT_DIR

# ========================================
# Parameter Sweep Loop
# ========================================
for Re in "${RE_VALUES[@]}"; do
    # Create case name
    caseName="Re_${Re}"
    echo "========================================"
    echo "Setting up case:1$caseName"
    echo "========================================"
    
    # Clone template case
    cp -r1$TEMPLATE_CASE1$OUTPUT_DIR/$caseName
    
    # Modify parameter using sed
    # sed: stream editor for text replacement
    # -i: edit file in-place
    # "s/RE_VALUE/$Re/": substitute RE_VALUE with actual Re number
    sed -i "s/RE_VALUE/$Re/"1$OUTPUT_DIR/$caseName/constant/transportProperties
    
    # Run simulation
    (cd1$OUTPUT_DIR/$caseName && ./Allrun)
    
    echo "Completed:1$caseName"
    echo ""
done

echo "All simulations completed!"
```

### Understanding sed Command

```bash
sed -i "s/RE_VALUE/$Re/" filename
```

แยกส่วนประกอบ:
- `sed`: **Stream Editor** - tool สำหรับแก้ไข text ใน files
- `-i`: **In-place** - แก้ไข file โดยตรง (ไม่สร้าง file ใหม่)
- `"s/RE_VALUE/$Re/"`: **Substitution command**
  - `s`: substitute
  - `RE_VALUE`: pattern ที่ต้องการค้นหา (placeholder)
  - `$Re`: ค่าที่จะนำมาแทนที่
  - `/`: delimiter คั่น pattern

Breaking it down:
- `sed`: **Stream Editor** - tool for text modification in files
- `-i`: **In-place** - edit file directly (no new file created)
- `"s/RE_VALUE/$Re/"`: **Substitution command**
  - `s`: substitute
  - `RE_VALUE`: pattern to search for (placeholder)
  - `$Re`: replacement value
  - `/`: delimiter separating patterns

### Template File Example

**constant/transportProperties** (in template):
```openfoam
transportModel  Newtonian;

nu              nu [0 2 -1 0 0 0 0]  RE_VALUE;
```

**After sed -i "s/RE_VALUE/1000/":**
```openfoam
transportModel  Newtonian;

nu              nu [0 2 -1 0 0 0 0]  0.001;
```

### Multi-Parameter Study

```bash
#!/bin/bash
# Two parameters: Reynolds number and mesh resolution

Re_VALUES=(100 1000)
REFINEMENT_LEVELS=(0 1 2)

for Re in "${Re_VALUES[@]}"; do
    for level in "${REFINEMENT_LEVELS[@]}"; do
        caseName="Re_${Re}_ref${level}"
        cp -r template1$caseName
        
        # Modify transport properties
        sed -i "s/RE_VALUE/$Re/"1$caseName/constant/transportProperties
        
        # Modify refinement level
        sed -i "s/REFINEMENT_LEVEL/$level/"1$caseName/system/snappyHexMeshDict
        
        (cd1$caseName && ./Allrun)
    done
done
```

### Advanced: Python Integration

```bash
#!/bin/bash
# Use Python for complex parameter calculations

for i in {1..10}; do
    caseName="case_$i"
    cp -r template1$caseName
    
    # Calculate parameter using Python
    velocity=$(python3 -c "print(1.0 +1$i * 0.5)")
    viscosity=$(python3 -c "print(1.0 / ($i + 1))")
    
    sed -i "s/U_INLET/$velocity/"1$caseName/0/U
    sed -i "s/NU_VALUE/$viscosity/"1$caseName/constant/transportProperties
    
    (cd1$caseName && ./Allrun)
done
```

---

## 4. Parallel Batch Processing

### What is Parallel Batch?

**Parallel Batch** คือการรันหลาย cases พร้อมกันบนเครื่องเดียว โดยใช้ CPU cores ที่ว่าง

**Parallel Batch** is running multiple cases simultaneously on a single machine using available CPU cores.

### Why Use It?

- **Speed:** รัน cases หลายตัวพร้อมกันใช้เวลาเท่า case นานที่สุด
- **Resource Utilization:** ใช้ CPU ทั้งหมดที่มี
- **Overhead:** ไม่ต้องใช้ scheduler ซับซ้อน

- **Speed:** Multiple cases finish in time of the longest case
- **Resource Utilization:** Uses all available CPUs
- **Overhead:** No complex scheduler needed

### Basic Parallel Batch

```bash
#!/bin/bash
# parallelBatch.sh

# Loop through all cases
for case in cases/*/; do
    echo "Starting:1$case"
    
    # Run in background with &
    # Subshell (...) isolates directory changes
    (cd "$case" && ./Allrun) &
done

# Wait for all background jobs to complete
wait

echo "All cases completed!"
```

### Understanding the Pattern

```bash
(cd "$case" && ./Allrun) &
```

แยกส่วนประกอบ:
- `(...)`: **Subshell** - สร้าง shell environment ใหม่
  - `cd` จะไม่กระทบ parent shell
  - Variables จะไม่ leak ไปยัง cases อื่น
- `cd "$case"`: เปลี่ยน directory ไปยัง case
- `&&`: รัน ./Allrun ถ้า cd สำเร็จ
- `&`: **Background operator** - รันใน background ไม่รอให้เสร็จ

Breaking it down:
- `(...)`: **Subshell** - creates isolated shell environment
  - `cd` doesn't affect parent shell
  - Variables don't leak to other cases
- `cd "$case"`: change to case directory
- `&&`: run ./Allrun only if cd succeeds
- `&`: **Background operator** - run without waiting for completion

### Safety: Concurrent File Access Warning

⚠️ **CRITICAL WARNING**

การรัน parallel มีความเสี่ยง:

1. **File System Locks:** บาง filesystems ไม่รองรับ concurrent writes
2. **Memory Limits:** รันหลาย solvers พร้อมกันอาจ OOM
3. **I/O Bottleneck:** หลาย cases เขียน disk พร้อมกัน ช้าลง

Parallel processing has risks:

1. **File System Locks:** Some filesystems don't support concurrent writes
2. **Memory Limits:** Running multiple solvers simultaneously may cause OOM
3. **I/O Bottleneck:** Multiple cases writing to disk simultaneously slows down

### Safe Parallel Batch

```bash
#!/bin/bash
# safeParallelBatch.sh

MAX_PARALLEL=4  # Limit concurrent jobs
running=0

for case in cases/*/; do
    # Check if we've reached max parallel jobs
    while [1$running -ge1$MAX_PARALLEL ]; do
        sleep 1  # Wait before checking again
        
        # Update running count (count background jobs)
        running=$(jobs -r | wc -l)
    done
    
    echo "Starting:1$case (running:1$running/$MAX_PARALLEL)"
    
    # Run in background
    (cd "$case" && ./Allrun) &
    
    ((running++))
done

# Wait for remaining jobs
wait
echo "All cases completed!"
```

### Parallel with Resource Monitoring

```bash
#!/bin/bash
# parallelWithMonitoring.sh

check_resources() {
    local mem_percent=$(free | awk '/Mem/{printf("%.0f"),1$3/$2*100}')
    local load_avg=$(uptime | awk '{print1$10}' | sed 's/,//')
    
    echo "Memory:1${mem_percent}% | Load:1${load_avg}"
    
    # Stop launching if memory > 90%
    if [1$mem_percent -gt 90 ]; then
        return 1  # Don't launch new jobs
    fi
    return 0
}

for case in cases/*/; do
    # Wait until resources available
    while ! check_resources; do
        echo "Waiting for resources..."
        sleep 10
    done
    
    (cd "$case" && ./Allrun) &
done

wait
```

### Comparison: Sequential vs Parallel

| แนวทาง | เวลา (4 cases) | การใช้ CPU | ความซับซ้อน |
|--------|----------------|------------|------------|
| Sequential | 4 × 2h = 8h | 25% | ต่ำ |
| Parallel Unlimited | 2h | 100% | ต่ำ |
| Parallel Limited (2 jobs) | 4h | 50% | ปานกลาง |

| Approach | Time (4 cases) | CPU Usage | Complexity |
|----------|---------------|-----------|------------|
| Sequential | 4 × 2h = 8h | 25% | Low |
| Parallel Unlimited | 2h | 100% | Low |
| Parallel Limited (2 jobs) | 4h | 50% | Medium |

### Common Pitfalls

❌ **Wrong:**
```bash
# ไม่ใช้ subshell - cd จะกระทบ loop
for case in cases/*/; do
    cd "$case" && ./Allrun &
done
# ทุก cases จะรันใน directory เดียวกัน!
```

❌ **Wrong:**
```bash
# ไม่มี wait - script จบก่อน cases เสร็จ
for case in cases/*/; do
    (cd "$case" && ./Allrun) &
done
# Script ends immediately, jobs become orphans
```

✅ **Correct:**
```bash
# ใช้ subshell และ wait
for case in cases/*/; do
    (cd "$case" && ./Allrun) &
done
wait  # Critical: wait for all background jobs
```

---

## 🚨 Common Pitfalls

### 1. Forgetting to Source RunFunctions

❌ **Wrong:**
```bash
#!/bin/bash
runApplication blockMesh  # Error: command not found
```

✅ **Correct:**
```bash
#!/bin/bash
.1$WM_PROJECT_DIR/bin/tools/RunFunctions
runApplication blockMesh
```

### 2. Mixing Absolute and Relative Paths

❌ **Wrong:**
```bash
cd1$CASE_DIR
runApplication blockMesh -case ~/cases/base  # Confusion
```

✅ **Correct:**
```bash
cd1$CASE_DIR
runApplication blockMesh  # Uses current directory
```

### 3. Not Checking Template Placeholders

❌ **Wrong:**
```bash
sed -i "s/RE_VALUE/$Re/" file.txt  # If RE_VALUE not found, no error
```

✅ **Correct:**
```bash
if grep -q "RE_VALUE" file.txt; then
    sed -i "s/RE_VALUE/$Re/" file.txt
else
    echo "ERROR: RE_VALUE placeholder not found!"
    exit 1
fi
```

### 4. Overwriting Log Files

❌ **Wrong:**
```bash
for Re in 100 200; do
    runApplication solver > log.txt  # Overwrites each iteration
done
```

✅ **Correct:**
```bash
for Re in 100 200; do
    runApplication solver > log_${Re}.txt  # Separate log per iteration
done
```

### 5. Not Cleaning Up Temporary Files

❌ **Wrong:**
```bash
# After 100 iterations, you have 100 processor directories
for i in {1..100}; do
    cp -r template case_$i
    (cd case_$i && ./Allrun)
done
```

✅ **Correct:**
```bash
for i in {1..100}; do
    cp -r template case_$i
    (cd case_$i && ./Allrun)
    
    # Clean up processor directories to save space
    rm -rf case_$i/processor*
done
```

---

## 📋 Quick Reference

### Standard Functions

| ฟังก์ชัน | การใช้งาน | ตัวอย่าง | Exit on Fail? |
|---------|-----------|--------|---------------|
| `runApplication` | Single process | `runApplication blockMesh` | ✅ Yes |
| `runParallel` | MPI parallel | `runParallel simpleFoam 4` | ✅ Yes |
| `cloneCase` | Copy case | `cloneCase base new` | N/A |

### Error Handling

| คำสั่ง | ผลลัพธ์ | ใช้เมื่อ |
|--------|---------|----------|
| `set -e` | Exit on any error | Simple workflows |
| `set +e` | Disable exit | Error recovery sections |
| `|| exit 1` | Exit if command fails | Selective handling |
| `|| true` | Always continue | Non-critical commands |

### sed Substitution

| Pattern | คำอธิบาย | ตัวอย่าง |
|---------|----------|---------|
| `s/old/new/` | Replace first occurrence | `s/foo/bar/` |
| `s/old/new/g` | Replace all occurrences | `s/foo/bar/g` |
| `s/old/new/i` | Case-insensitive replace | `s/foo/bar/i` |

### Parallel Operators

| Operator | คำอธิบาย | ตัวอย่าง |
|---------|----------|---------|
| `&` | Run in background | `command &` |
| `wait` | Wait for background jobs | `wait` |
| `jobs -r` | List running jobs | `jobs -r` |

---

## 🎯 Key Takeaways

### Core Concepts
- **Automation Framework** ให้โครงสร้างมาตรฐานสำหรับ OpenFOAM scripting
- **RunFunctions** จัดการ logging และ error handling ให้อัตโนมัติ
- **Error handling** มี 2 แนวทางหลัก: `set -e` (simple) และ `|| exit` (flexible)

### Best Practices
- **ใช้ RunFunctions** เสมอเพื่อความสอดคล้อง
- **เลือก error handling** ให้เหมาะกับความซับซ้อนของ workflow
- **Parametric studies** ควรใช้ template + sed/Python สำหรับความยืดหยุ่น
- **Parallel batch** ต้อง monitor resources และใช้ subshell

### When to Use What
- **Standard workflows:** `runApplication` + `set -e`
- **Parameter sweeps:** Template + sed loop
- **Multi-case processing:** Parallel batch + wait
- **Complex error handling:** `|| exit` patterns

### Core Concepts
- **Automation Framework** provides standard structure for OpenFOAM scripting
- **RunFunctions** handles logging and error handling automatically
- **Error handling** has 2 main approaches: `set -e` (simple) and `|| exit` (flexible)

### Best Practices
- **Use RunFunctions** always for consistency
- **Choose error handling** based on workflow complexity
- **Parametric studies** should use templates + sed/Python for flexibility
- **Parallel batch** must monitor resources and use subshells

### When to Use What
- **Standard workflows:** `runApplication` + `set -e`
- **Parameter sweeps:** Template + sed loop
- **Multi-case processing:** Parallel batch + wait
- **Complex error handling:** `|| exit` patterns

---

## 🧠 Concept Check

<details>
<summary><b>1. set -e ทำอะไร?</b></summary>

**Stop script** when any command fails (exit code ≠ 0)

When to use:
- Simple sequential workflows
- When all steps must complete successfully
- Quick prototyping requiring fail-fast
</details>

<details>
<summary><b>2. runApplication ทำอะไรนอกเหนือจากรันคำสั่ง?</b></summary>

**runApplication** does:
1. Logs command to `log.<application>`
2. Runs the actual command
3. Checks exit code
4. Stops script on failure
5. Supports resume (skips completed commands via log files)

This provides **consistent error handling** and **execution tracking**.
</details>

<details>
<summary><b>3. sed "s/RE_VALUE/100/" ทำอะไร?</b></summary>

**Substitutes text** in files:
- `s`: substitute command
- `RE_VALUE`: text to find (placeholder)
- `100`: replacement text
- Finds all occurrences of "RE_VALUE" and replaces with "100"

Use for **parameter injection** in template files.
</details>

<details>
<summary><b>4. ทำไมต้องใช้ subshell (...) ใน parallel batch?</b></summary>

**Subshell isolation** prevents:
- Directory changes affecting other cases (`cd` stays in subshell)
- Variable conflicts between parallel jobs
- State corruption from concurrent execution

Without subshell, all jobs would run in the **same directory**!
</details>

<details>
<summary><b>5. เมื่อไหร่ควรใช้ || exit แทน set -e?</b></summary>

Use `|| exit` when:
- Need **custom error messages** per command
- Implementing **fallback mechanisms**
- Some commands can **fail gracefully**
- Need **different exit codes** for different errors

Use `set -e` for **standard workflows** where any failure should stop execution.
</details>

---

## 📖 Related Documentation

### Prerequisites
- **Shell Basics:** [01_Automation_Strategy.md](01_Automation_Strategy.md)
- **OpenFOAM Environment:** [00_Overview.md](00_Overview.md)

### Advanced Topics
- **Parametric Meshing:** [02_BLOCKMESH_MASTERY](../../MODULE_02_MESHING_AND_CASE_SETUP/CONTENT/02_BLOCKMESH_MASTERY/01_BlockMesh_Deep_Dive.md)
- **Parallel Processing:** [03_SNAPPYHEXMESH_BASICS](../../MODULE_02_MESHING_AND_CASE_SETUP/CONTENT/03_SNAPPYHEXMESH_BASICS/03_Castellated_Mesh_Settings.md)

### Case Studies
- **Workflow Automation:** [../Exercises/](../Exercises/)
- **Template Systems:** [../Templates/](../Templates/)

---

## 💻 Practice Exercises

### Exercise 1: Basic Parametric Study
สร้าง script ที่รัน simulation สำหรับ Reynolds numbers: 100, 500, 1000, 2000
Create a script that runs simulations for Reynolds numbers: 100, 500, 1000, 2000

<details>
<summary>Solution</summary>

```bash
#!/bin/bash
TEMPLATE="base_case"

for Re in 100 500 1000 2000; do
    caseName="Re_$Re"
    cp -r1$TEMPLATE1$caseName
    sed -i "s/RE_VALUE/$Re/"1$caseName/constant/transportProperties
    (cd1$caseName && ./Allrun)
done
```
</details>

### Exercise 2: Safe Parallel Batch
สร้าง parallel batch script ที่รันไม่เกิน 3 cases พร้อมกัน
Create a parallel batch script that runs maximum 3 cases simultaneously

<details>
<summary>Solution</summary>

```bash
#!/bin/bash
MAX_PARALLEL=3
running=0

for case in cases/*/; do
    while [1$running -ge1$MAX_PARALLEL ]; do
        sleep 1
        running=$(jobs -r | wc -l)
    done
    
    (cd "$case" && ./Allrun) &
    ((running++))
done

wait
```
</details>

### Exercise 3: Error Handling Comparison
เปรียบเทียบผลลัพธ์ของ script ที่ใช้ `set -e` vs script ที่ใช้ `|| exit` เมื่อ blockMesh fail
Compare results of script using `set -e` vs script using `|| exit` when blockMesh fails

<details>
<summary>Analysis</summary>

**With set -e:**
- Script stops immediately at blockMesh failure
- No cleanup or logging happens after failure
- Simple but abrupt

**With || exit:**
- Can add custom error message before exit
- Can run cleanup commands (`rm -rf temp/ || exit 1`)
- More control over failure handling
</details>