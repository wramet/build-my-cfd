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

## 🎯 Learning Objectives (เป้าหมายการเรียนรู้)

หลังจากอ่านบทนี้ คุณควรจะสามารถ:

1. **อธิบาย (Explain)** ความสำคัญของ Performance Profiling และผลกระทบต่อ OpenFOAM Simulation
2. **วัด (Measure)** เมตริกประสิทธิภาพหลัก (Execution Time, Memory, Scaling) ด้วยเครื่องมือที่เหมาะสม
3. **ใช้ (Use)** เครื่องมือ Profiling ทั้งแบบ Built-in (cpuTime, functionObjects) และ External (perf, gprof, valgrind)
4. **วิเคราะห์ (Analyze)** Strong Scaling และ Weak Scaling เพื่อประเมินประสิทธิภาพ Parallel
5. **ระบุ (Identify)** และ **แก้ไข (Fix)** จุดคอขวบทั่วไปใน OpenFOAM Solvers
6. **ประยุกต์ (Apply)** เทคนิค Profiling กับ Custom Solvers และ Case ของตัวเอง

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

**What (คืออะไร):** Execution Time คือเวลาที่ Solver ใช้ในการคำนวณ แบ่งเป็น 3 ประเภท:

**Why (ทำไมสำคัญ):**
- เป็นตัวชี้วัดหลักว่า Simulation จะเสร็จเมื่อไหร่
- ช่วยตัดสินใจเรื่อง Resource Planning (เช่า HPC กี่ Core กี่ชั่วโมง)
- ใช้เปรียบเทียบประสิทธิภาพระหว่าง Solver Configurations ต่างๆ

**How (วิธีวัด):**

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

**What (คืออะไร):** ปริมาณหน่วยความจำ (RAM) ที่ Solver ใช้ระหว่างรัน

**Why (ทำไมสำคัญ):**
- ถ้า RAM เต็ม → ใช้ Swap → Performance ตก 10-100x
- ช่วยวางแผนว่าเครื่อง/HPC รองรับ Case นี้ได้ไหม
- ใช้ประเมิน Trade-off: แก้ Mesh Density หรือลด Fields ที่เก็บ

**How (วิธีวัด):**

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

**What (คืออะไร):** ตัวชี้วัดประสิทธิภาพของ Parallel Computing

**Why (ทำไมสำคัญ):**
- ช่วยตัดสินใจว่าควรใช้กี่ Core ใน HPC
- ทราบว่าการเพิ่ม Core ยังคุ้มไหม (Diminishing Returns)
- ใช้ประเมิน Cost-benefit: เพิ่ม Core แพงขึ้นแต่เร็วขึ้นกี่เปอร์เซ็นต์

**How (วิธีคำนวณ):**

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

**What (คืออะไร):** เครื่องมือที่ OpenFOAM มีให้มาโดยไม่ต้องติดตั้งเพิ่ม

**Why (ทำไมใช้):**
- ไม่ต้องแก้ Compiler Flags หรือติดตั้ง Tools ภายนอก
- เหมาะสำหรับ Basic Profiling และ Production Runs
- Output แสดงใน Log Files โดยตรง

**How (วิธีใช้):**

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

**What (คืออะไร):** Tools ภายนอกที่ใช้สำหรับ Deep Profiling ระดับ OS/Hardware

**Why (ทำไมใช้):**
- ได้รายละเอียดลึกกว่า Built-in (Function-level, Assembly-level)
- สามารถ Detect ปัญหา Memory Leak, Cache Miss, CPU Stalls
- จำเป็นต้องใช้เมื่อต้อง Optimize Performance ขั้นสูง

**How (วิธีใช้):**

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

**What (คืออะไร):** การเร่งการคำนวณ **ปัญหาขนาดคงที่** ด้วยการเพิ่ม CPU

**Why (ทำสำคัญ):**
- ใช้เมื่อมี Case ขนาดคงที่และอยากเสร็จเร็วขึ้น
- ช่วยตัดสินใจว่าควรใช้กี่ Core (Cost vs Speed)
- ทราบจุดที่การเพิ่ม Core ไม่คุ้ม (Diminishing Returns)

**How (วิธีทดสอบ):**

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

**What (คืออะไร):** การเพิ่มขนาดปัญหาตามสัดส่วน CPU เพื่อให้ **เวลาคงที่**

**Why (ทำสำคัญ):**
- ใช้เมื่อต้องการรัน Mesh ขนาดใหญ่ที่สุดที่ HPC รองรับ
- เหมาะกับ Large-scale Simulations (เช่น LES, DNS)
- ทราบว่า Parallel Code สามารถ Scale ได้ดีแค่ไหน

**How (วิธีทดสอบ):**

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

## 🏋️‍♂️ แบบฝึกหัดปฏิบัติ (Practical Exercise)

### Exercise 1: Basic Profiling ด้วย `cpuTime`

**ภารกิจ:** เพิ่ม `cpuTime` tracking ใน Custom Solver

```cpp
// เพิ่ม code นี้ใน solver
#include "cpuTime.H"

// ใน time loop
cpuTime totalTimer, meshUpdateTimer, solveTimer;

meshUpdateTimer.start();
mesh.update();
scalar meshTime = meshUpdateTimer.cpuTimeIncrement();

solveTimer.start();
solve(fvm::ddt(U) + fvm::div(phi, U) - fvm::laplacian(nu, U));
scalar solveTime = solveTimer.cpuTimeIncrement();

Info << "Timing breakdown:" << nl
     << "  Mesh update: " << meshTime << " s (" << meshTime/totalTimer.cpuTimeIncrement()*100 << "%)" << nl
     << "  Solve:       " << solveTime << " s (" << solveTime/totalTimer.cpuTimeIncrement()*100 << "%)" << endl;
```

**Expected Output:**
```
Timing breakdown:
  Mesh update: 0.52 s (4.2%)
  Solve:       11.87 s (95.8%)
```

### Exercise 2: Strong Scaling Test

**ภารกิจ:** ทดสอบ Strong Scaling ด้วย Script นี้

```bash
#!/bin/bash
# strongScalingTest.sh

SOLVER=simpleFoam
CASE_NAME=cavity
CORES=(1 2 4 8)
echo "#Cores Time(s) Speedup Efficiency" > scaling_results.txt

T1=0
for n in "${CORES[@]}"; do
    cp -r $CASE_NAME ${CASE_NAME}_n${n}
    decomposePar -np $n -case ${CASE_NAME}_n${n} > /dev/null
    mpirun -np $n $SOLVER -parallel -case ${CASE_NAME}_n${n} > log.${n} 2>&1
    T=$(grep "ExecutionTime" log.${n} | awk '{print $3}')
    
    if [ $n -eq 1 ]; then
        T1=$T
    fi
    
    S=$(echo "$T1 / $T" | bc -l)
    E=$(echo "$S / $n" | bc -l)
    
    printf "%d %s %s %s\n" $n $T $S $E >> scaling_results.txt
    rm -rf ${CASE_NAME}_n${n}
done

cat scaling_results.txt
```

### Exercise 3: Memory Profiling

**ภารกิจ:** ติดตาม Peak Memory ระหว่าง Simulation

```bash
#!/bin/bash
# memoryProfile.sh

SOLVER=simpleFoam
CASE=cavity

decomposePar -case $CASE
mpirun -np 4 $SOLVER -parallel -case $CASE > log.solver 2>&1 &

PID=$!
while kill -0 $PID 2>/dev/null; do
    MEM=$(ps -o rss= -p $PID | awk '{sum+=$1} END {print sum/1024}')
    echo "$(date +%s) $MEM" >> memory_usage.dat
    sleep 5
done

# Plot กราฟ
gnuplot -e "set terminal png; set output 'memory.png'; plot 'memory_usage.dat' with lines title 'Memory (MB)'"
```

---

## 📋 Key Takeaways (สรุปสาระสำคัญ)

### What (อะไรคือ Performance Profiling?)
Performance Profiling คือการวัดและวิเคราะห์ประสิทธิภาพของ OpenFOAM Solvers เพื่อระบุและแก้ไขจุดคอขวบ

### Why (ทำไมต้องทำ?)
- **Gut Feeling มักผิด** - คุณคิดว่า Linear Solver ช้า แต่จริงๆ อาจเป็น I/O หรือ MPI Communication
- **Cost Optimization** - ช่วยตัดสินใจว่าควรใช้กี่ Core เพื่อประหยัดเงิน HPC
- **Time Savings** - แก้ที่ Bottleneck ที่แท้จริง สามารถลดเวลาได้ 30-50%

### How (ทำอย่างไร?)
1. **เลือกเครื่องมือที่เหมาะสม**
   - Built-in (`cpuTime`, `profiling`) → สำหรับ Basic Profiling
   - External (`perf`, `gprof`) → สำหรับ Deep Dive

2. **วัดเมตริกหลัก 3 อย่าง**
   - Execution Time (Wall Clock, CPU Time)
   - Memory Usage (RSS, Peak)
   - Scaling (Speedup, Efficiency)

3. **ทดสอบ Scaling**
   - Strong Scaling: เพิ่ม Core กับ Mesh คงที่
   - Weak Scaling: เพิ่ม Core พร้อม Mesh

4. **วินิจฉัยและแก้ไข**
   - Profile ก่อน อย่าเดา!
   - ดู % time → Focus ที่ Top Bottlenecks
   - แก้ไข → Verify ด้วยการ Profile อีกครั้ง

### Best Practices
- ✅ **Profile Early** - อย่ารอจน Project ใกล้ Deadline
- ✅ **Profile Often** - ทุกครั้งที่เปลี่ยน Solver/Mesh
- ✅ **Document Results** - เก็บ Log ไว้เปรียบเทียบ
- ❌ **Don't Guess** - ใช้ Data ไม่ใช่ Gut Feeling
- ❌ **Don't Premature Optimize** - แก้ที่ Bottleneck ไม่ใช่ที่อื่น

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

4. **ถาม:** ความแตกต่างระหว่าง Wall Clock Time และ CPU Time?
   <details>
   <summary>เฉลย</summary>
   <b>ตอบ:</b> <b>Wall Clock Time</b> คือเวลาจริงที่ผู้ใช้รอ (รวม I/O wait, MPI communication, sleep) <b>CPU Time</b> คือเวลาที่ CPU ทำงานจริง (ไม่รวมเวลาที่ Process รอ I/O หรือ Process อื่น)
   </details>

5. **ถาม:** Amdahl's Law บอกอะไรกับเรา?
   <details>
   <summary>เฉลย</summary>
   <b>ตอบ:</b> Amdahl's Law บอกว่า Speedup สูงสุดถูกจำกัดด้วยส่วน Serial (1-P) ถ้า Code มีส่วน Serial 10% ไม่ว่าจะใช้กี่ CPU ก็ตาม Speedup สูงสุดคือ 10x เท่านั้น ดังนั้นการลดส่วน Serial สำคัญกว่าการเพิ่ม CPU
   </details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md) — ภาพรวม QA, Automation & Profiling
- **Regression Testing:** [02_Regression_Testing.md](02_Regression_Testing.md) — การทดสอบถอยหลัง
- **Debugging:** [03_Debugging_Troubleshooting.md](03_Debugging_Troubleshooting.md) — การดีบักและแก้ปัญหา