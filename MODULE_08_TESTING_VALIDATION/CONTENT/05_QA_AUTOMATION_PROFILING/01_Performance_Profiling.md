# 01 การวิเคราะห์ประสิทธิภาพ (Performance Profiling)

> [!TIP] ทำไมต้อง Performance Profiling?
> **Performance Profiling** คือการวัดและวิเคราะห์ประสิทธิภาพของ Solver เพื่อระบุจุดคอขวบ (Bottlenecks) ที่ทำให้การคำนวณช้าลง การเดาอาการป่วย (Gut Feeling) มักจะผิด การ Profile จะชี้ให้เห็น **จุดที่แท้จริง** ที่ต้องปรับปรุง เช่น Linear Solver ใช้เวลา 70% ของ total runtime หรือ Parallel I/O ช้ากว่า Single Process เป็นต้น
>
> **🔧 ผลกระทบต่อ OpenFOAM Case:**
> - กระบวนการนี้มีผลโดยตรงต่อการตั้งค่าใน `Make/options` (compiler flags)
> - มีผลต่อการเลือก Linear Solver และ Preconditioner ใน `system/fvSolution`
> - มีผลต่อการตั้งค่า Parallel Decomposition ใน `system/decomposeParDict`
> - ช่วยตัดสินใจเรื่อง Trade-offs: Memory vs Speed, Accuracy vs Cost

---

## 1.1 เมตริกประสิทธิภาพหลัก (Key Performance Metrics)

> [!NOTE] **📂 OpenFOAM Context**
> **Domain:** Simulation Control (Domain C) & Coding/Customization (Domain E)
>
> การวัดประสิทธิภาพใน OpenFOAM ใช้:
> - **cpuTime class:** `#include "cpuTime.H"` ใน C++ code สำหรับจับเวลา function
> - **functionObjects:** `system/controlDict` → `functions` → `cpuTime`, `profiling`, `execFlowFunctionObjects`
> - **External Tools:** `perf`, `valgrind`, `gprof` สำหรับ deep profiling
>
> **🔑 คำสำคัญ:** `cpuTime`, `profiling`, `functionObjects`, `perf`, `valgrind`

### 1.1.1 Execution Time (เวลาการประมวลผล)

```cpp
// ใน Solver code
#include "cpuTime.H"

int main(int argc, char *argv[])
{
    cpuTime timer;

    // ... solver code ...

    Info << "Execution time: " << timer.cpuTimeIncrement() << " s" << endl;
    return 0;
}
```

**แนวคิดหลัก:**
- **Wall Clock Time**: เวลาจริงที่ผู้ใช้รอ (รวม I/O, MPI communication)
- **CPU Time**: เวลาที่ CPU ทำงานจริง (ไม่รวม I/O wait)
- **Elapsed Time**: ต่างจาก Wall Clock ถ้ามีการ sleep/wait

### 1.1.2 Memory Usage (การใช้หน่วยความจำ)

```bash
# ตรวจสอบ Peak Memory
/usr/bin/time -v simpleFoam 2>&1 | grep "Maximum resident set size"

# Output: Maximum resident set size (kbytes): 524288
```

**แนวคิดหลัก:**
- **RSS (Resident Set Size)**: หน่วยความจำที่จองจริงใน RAM
- **Virtual Memory**: หน่วยความจำที่ address ได้ (รวม swap)
- **Heap vs Stack**: `volScalarField` อยู่ใน Heap, local variables อยู่ใน Stack

### 1.1.3 Scaling Metrics (เมตริกการปรับขนาด)

| Metric | คำนวณ | ใช้เมื่อ |
|--------|--------|-----------|
| **Speedup** | $S = T_1 / T_N$ | Strong Scaling |
| **Efficiency** | $E = S / N$ | Strong/Weak Scaling |
| **Parallel Cost** | $C = N \times T_N$ | Cost-benefit analysis |

> [!TIP] Amdahl's Law
> ไม่ว่าจะใช้กี่ CPU ก็ตาม Speedup สูงสุดถูกจำกัดด้วยส่วน Serial:
> $$S_{max} = \frac{1}{(1-P) + P/N}$$
> เมื่อ $P$ = ส่วน Parallel, $N$ = จำนวน CPU

---

## 1.2 เครื่องมือ Profiling ใน OpenFOAM (OpenFOAM Profiling Tools)

### 1.2.1 Built-in Profiling (Profiling ในตัว)

**วิธีที่ 1: ใช้ `cpuTime` ใน Solver Code**

```cpp
// ใน custom solver
#include "cpuTime.H"

// ... ใน time loop
cpuTime solveTimer;

solve(fvm::laplacian(D, T) == source);

scalar solveTime = solveTimer.cpuTimeIncrement();
Info << "Solve time: " << solveTime << " s" << endl;
```

**วิธีที่ 2: ใช้ `profiling` functionObject**

```cpp
// ใน system/controlDict
functions
{
    profiling
    {
        type        profiling;
        active      true;
        cpuInfo     true;    // แสดง CPU usage
        memInfo     true;    // แสดง Memory usage
        sysInfo     true;    // แสดง System info
        writeControl    writeTime;
        writeInterval   1;
    }
}
```

**Output ตัวอย่าง:**
```
Profiling information
    CPU time: 125.3 s
    Clock time: 128.1 s
    Memory: 1.2 GB
    CPU load: 97.5%
```

### 1.2.2 External Profiling Tools (เครื่องมือภายนอก)

**Tool 1: `perf` (Linux Performance Counter)**

```bash
# 1. Record performance data
perf record -g --call-graph dwarf simpleFoam

# 2. Analyze results
perf report

# Output example:
#   45.23%  simpleFoam  libopenmpi.so     [.] MPI_Wait
#   23.11%  simpleFoam  libGKlib.so       [.] gk_msort
#   12.45%  simpleFoam  libfiniteVolume.so [.] Foam::fvMatrix::solve
```

**คำอธิบาย:** `perf` ใช้ hardware performance counters วัด:
- **CPU Cycles**: จำนวน cycle ที่ CPU ทำงาน
- **Cache Misses**: จำนวนครั้งที่ cache miss (ส่งผลต่อ performance)
- **Instructions**: จำนวน instruction ที่ execute

**Tool 2: `gprof` (GNU Profiler)**

```bash
# 1. Compile with profiling flags
wmake CFLAGS="-pg" CXXFLAGS="-pg"

# 2. Run solver
simpleFoam

# 3. Analyze
gprof simpleFoam gmon.out > profile.txt
```

**Output ตัวอย่าง:**
```
Flat profile:
Each sample counts as 0.01 seconds.
  %   cumulative   self              self     total
 time   seconds   seconds    calls  ms/call  ms/call  name
 45.2     12.34    12.34     1000    12.34    25.67  Foam::fvMatrix::solve()
 23.1     18.67     6.33     5000     1.27     3.45  Foam::lduMatrix::solver()
```

**Tool 3: Valgrind (Memory Profiling)**

```bash
# Massif: Heap profiling
valgrind --tool=massif simpleFoam

# วิเคราะห์ผล
ms_print massif.out.12345

# Output example:
#   KB    123.45^                                       @@
#   KB     99.12^                                   :   #  :
#   KB     74.78^                               :@@@#:   :  ::
```

---

## 1.3 การวิเคราะห์ Scaling (Scaling Analysis)

### 1.3.1 Strong Scaling (การปรับขนาดแบบ Strong)

> **จุดมุ่งหมาย:** เร่งการคำนาณ **ปัญหาขนาดคงที่** ด้วยการเพิ่ม CPU

```bash
# Script ทดสอบ Strong Scaling
#!/bin/bash
# testStrongScaling.sh

CASE=airfoil
SOLVER=simpleFoam
CORES="1 2 4 8 16 32"

for n in $CORES; do
    echo "Testing with $n cores..."

    # Decompose
    decomposePar -np $n -case $CASE

    # Run
    mpirun -np $n $SOLVER -parallel -case $CASE > log.$n

    # Extract time
    TIME=$(grep "ExecutionTime" log.$n | awk '{print $3}')
    echo "$n $TIME" >> scaling.dat
done
```

**กราฟ Strong Scaling ที่คาดหวัง:**
- **Ideal Speedup**: เส้นตรง $S = N$
- **Actual Speedup**: โค้งลงเมื่อ CPU มากขึ้น (เพราะ communication overhead)

### 1.3.2 Weak Scaling (การปรับขนาดแบบ Weak)

> **จุดมุ่งหมาย:** เพิ่มขนาดปัญหาตามสัดส่วน CPU เพื่อให้ **เวลาคงที่**

```bash
# Script ทดสอบ Weak Scaling
#!/bin/bash
# testWeakScaling.sh

BASE_CASE=channel
SOLVER=simpleFoam
CORES="1 2 4 8 16 32"

for n in $CORES; do
    echo "Testing with $n cores..."

    # Scale mesh size: 10K cells per core
    CELLS=$((n * 10000))

    # Modify blockMeshDict
    sed -i "s/nx .*/nx $((n*20));/" $BASE_CASE/system/blockMeshDict

    # Generate mesh
    blockMesh -case $BASE_CASE

    # Decompose and run
    decomposePar -np $n -case $BASE_CASE
    mpirun -np $n $SOLVER -parallel -case $BASE_CASE > log.$n

    # Extract time
    TIME=$(grep "ExecutionTime" log.$n | awk '{print $3}')
    echo "$n $TIME" >> weak_scaling.dat
done
```

**กราฟ Weak Scaling ที่คาดหวัง:**
- **Ideal**: เส้นนอน (time คงที่)
- **Actual**: ค่อยๆ เพิ่มขึ้นเมื่อ CPU มาก (เพราะ communication)

---

## 1.4 จุดคอขวบทั่วไป (Common Bottlenecks)

| Bottleneck | อาการ | วิธีแก้ |
|:---|:---|:---|
| **Linear Solver** | Solve step ใช้เวลา > 60% | - เปลี่ยน Preconditioner (GAMG → DIC) <br> - ลด tolerance ใน `system/fvSolution` |
| **I/O** | Write time ใช้เวลานาน | - ลด `writeInterval` <br> - ใช้ `masterCollating` สำหรับ parallel |
| **Memory** | RAM เต็ม ใช้ Swap | - ลด fields ที่เก็บ <br> - ใช้ `tmp` fields ชั่วคราว |
| **Load Imbalance** | บาง CPU idle บางตัว overload | - ปรับ `decomposeParDict` <br> - ใช้ `scotch` แทน `simple` |
| **Cache Miss** | perf แสดง cache miss สูง | - จัดเรียง data contiguously <br> - ใช้ `UList` แทน `List` |

> [!TIP] การวินิจฉัย Bottleneck
> 1. **Profile ก่อน** อย่าเดา! ใช้ `perf` หรือ `gprof`
> 2. **ดู % time** ถ้า function ไหน > 30% นั่นคือ bottleneck
> 3. **แก้ที่ bottleneck** อย่าแก้ที่อื่น (Premature optimization คือ root of all evil)

---

## 1.5 ตัวอย่างการ Profile Solver จริง (Real-World Example)

### ปัญหา: `myCustomSolver` ช้าเกินไป

**Step 1: Profile ด้วย `perf`**

```bash
perf record -g myCustomSolver
perf report --stdio
```

**Output:**
```
# 45.23%  myCustomSolver  libopenmpi.so     [.] MPI_Allreduce
# 23.11%  myCustomSolver  libfiniteVolume.so [.] Foam::fvm::laplacian
# 12.45%  myCustomSolver  libfiniteVolume.so [.] Foam::lduMatrix::solve
```

**Step 2: วินิจฉัย**
- **MPI_Allreduce ใช้เวลา 45%** → Parallel communication ช้า
- **fvm::laplacian 23%** → Discretization ช้า
- **lduMatrix::solve 12%** → Linear solver ใช้เวลาน้อย

**Step 3: แก้ไข**

```cpp
// ก่อนแก้: Global reduction ทุก time step
scalar globalSum = gSum(field);

// หลังแก้: Accumulate แล้วค่อย reduce
scalar localSum = sum(field);
scalar globalSum = returnReduce(localSum, sumOp<scalar>());
```

**ผลลัพธ์:**
- เวลาลดจาก 120s → 75s (37.5% faster)

---

## 🧠 ตรวจสอบความเข้าใจ (Concept Check)

1. **ถาม:** ทำไมต้อง Profile แทนที่จะเดา?
   <details>
   <summary>เฉลย</summary>
   <b>ตอบ:</b> เพราะ Gut Feeling มักผิด ตัวอย่างเช่น คุณคิดว่า Linear Solver ช้า แต่จริงๆ แล้ว I/O ใช้เวลา 50% การแก้ Linear Solver จะไม่ช่วยให้เร็วขึ้นเลย
   </details>

2. **ถาม:** Strong Scaling vs Weak Scaling ใช้เมื่อไหร่?
   <details>
   <summary>เฉลย</summary>
   <b>ตอบ:</b> <b>Strong Scaling</b> ใช้เมื่อมี Mesh ขนาดคงที่และอยากเร่งให้เสร็จเร็วขึ้น <b>Weak Scaling</b> ใช้เมื่อต้องการรัน Mesh ขนาดใหญ่ที่สุดที่ RAM รองรับ โดยไม่สนใจว่าจะใช้เวลานานแค่ไหน
   </details>

3. **ถาม:** ถ้า perf แสดงว่า `MPI_Wait` ใช้เวลา 40% แก้ยังไง?
   <details>
   <summary>เฉลย</summary>
   <b>ตอบ:</b> แปลว่า Process รอ communication กันมาก เกิดจาก (1) Load imbalance ให้แก้ decomposition, (2) Global reduction บ่อยเกินไปให้ลด frequency, หรือ (3) Network ช้าให้เปลี่ยนจาก Ethernet เป็น InfiniBand
   </details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md) — ภาพรวม QA, Automation & Profiling
- **Regression Testing:** [02_Regression_Testing.md](02_Regression_Testing.md) — การทดสอบถอยหลัง
- **Debugging:** [03_Debugging_Troubleshooting.md](03_Debugging_Troubleshooting.md) — การดีบักและแก้ปัญหา
