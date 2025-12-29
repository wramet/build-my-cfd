# Phase 5: Optimization

Achieve 2x Speedup

---

## Objective

> **ทำให้ solver เร็วขึ้นอย่างน้อย 2 เท่า** จาก baseline

---

## เป้าหมายการเรียนรู้

- ใช้เทคนิค profiling
- Optimize solver settings
- วัดผลการปรับปรุงอย่างเชิงปริมาณ

---

## Step 1: สร้าง Baseline

```bash
# Run baseline case
cd tutorials/turbulent_channel

# Record baseline time
time mpirun -np 4 myHeatFoam -parallel > log.baseline 2>&1

# Extract timing
grep "ClockTime" log.baseline | tail -1
# Example: ClockTime = 120 s
```

**Baseline: 120 seconds** (example)

---

## Step 2: Profile

### Use perf

```bash
# Profile single-processor run for analysis
perf record -g myHeatFoam > log.profile 2>&1

# Analyze
perf report --hierarchy
```

### ตัวอย่าง perf Output จริง

```bash
$ perf report --hierarchy
#
# Children      Self  Command  Shared Object       Symbol
# ........  ........  .......  ..................  .......................................
#
    65.25%     0.00%  myHeatFoam  myHeatFoam          [.] Foam::fvMatrix<double>::solve
    42.18%     0.00%  myHeatFoam  libmyHeatFoam.so    [.] Foam::GAMG::solve
    38.50%     2.15%  myHeatFoam  libGAMGPrecon.so    [.] Foam::GAMG::performCycle
    15.32%     0.85%  myHeatFoam  libfiniteVolume.so  [.] Foam::fvc::grad<double>
    12.45%     0.42%  myHeatFoam  libfiniteVolume.so  [.] Foam::fvm::div<double>
     8.76%     0.31%  myHeatFoam  libturbulence.so    [.] Foam::kEpsilon::correct
     6.18%     0.18%  myHeatFoam  libfiniteVolume.so  [.] Foam::lduMatrix::Amul
     5.32%     5.32%  myHeatFoam  [kernel]            [k] memcpy
     4.85%     0.12%  myHeatFoam  libfiniteVolume.so  [.] Foam::fvPatchField::updateCoeffs
     4.10%     0.08%  myHeatFoam  libmyHeatFoam.so    [.] Foam::tmp<Foam::GeometricField<double>>::~tmp
```

**Interpretation:**
- **65%** spent in linear solver (`fvMatrix::solve`)
- **42%** in GAMG preconditioner → this is where we should focus!
- **15%** in gradient calculations
- **12%** in divergence terms

### Alternative: gprof

```bash
# First, recompile with profiling
cd myHeatFoam
vim Make/options

# Add:
EXE_INC = \
    ... \
    -pg

# Recompile
wclean
wmake

# Run
myHeatFoam

# วิเคราะห์
gprof myHeatFoam gmon.out > gprof_report.txt
```

### ตัวอย่าง gprof Output จริง

```
Flat profile:

 Each sample counts as 0.01 seconds.
  %   cumulative   self              self     total
 time   seconds   seconds    calls  us/call  us/call  name
 42.18      5.06     5.06   150000     33.7     45.2  Foam::GAMG::solve
 15.32      6.90     1.84    30000     61.3    125.0  Foam::fvc::grad<double>
 12.45      8.39     1.49    30000     49.7    102.3  Foam::fvm::div<double>
  8.76      9.44     1.05    15000     70.0    150.0  Foam::kEpsilon::correct
  6.18     10.18     0.74   450000      1.6      3.2  Foam::lduMatrix::Amul
  5.32     10.82     0.64  4582341      0.0      0.0  memcpy
  4.85     11.40     0.58    30000     19.3     38.5  Foam::fvPatchField::updateCoeffs
  4.10     11.89     0.49   60000      8.2     16.4  Foam::tmp::~tmp
```

### ระบุ Hotspots

```
Typical breakdown:
+ 65%  fvMatrix::solve (Linear Solver) ← OPTIMIZE THIS!
   + 42%  GAMG preconditioner
   + 15%  BC communication
   + 8%   Matrix operations
+ 15%  fvc::grad
+ 12%  fvm::div
+ 9%   Turbulence
+ 9%   Other (I/O, memcpy, etc.)
```

**Focus on:** Linear Solver (65%) — biggest gain potential!

---

## Step 3: Optimize Linear Solver

### fvSolution เดิม

```cpp
solvers
{
    T
    {
        solver          PCG;
        preconditioner  DIC;
        tolerance       1e-06;
        relTol          0;
    }
}
```

### fvSolution ที่ Optimize แล้ว

```cpp
solvers
{
    T
    {
        solver          GAMG;       // Multigrid!
        smoother        GaussSeidel;
        tolerance       1e-06;
        relTol          0.01;       // Stop early!
        nPreSweeps      0;
        nPostSweeps     2;
        nFinestSweeps   2;
        cacheAgglomeration true;
        agglomerator    faceAreaPair;
        mergeLevels     1;
    }
}
```

**Expected:** 30-50% faster solve

---

## Step 4: Reduce I/O

### Original controlDict

```cpp
writeControl    runTime;
writeInterval   0.1;     // Write every 0.1 s
```

### Optimized controlDict

```cpp
writeControl    runTime;
writeInterval   1;       // Write every 1 s (10x less!)
writeCompression true;   // Smaller files
purgeWrite      5;       // Keep only last 5 times
```

**Expected:** 5-10% faster (less I/O stalls)

---

## Step 5: Adjust Discretization

### Accuracy vs Speed Tradeoffs

```cpp
gradSchemes
{
    // Original: corrected (accurate, slower)
    default         Gauss linear corrected;
    
    // Faster: orthogonal (if mesh is good)
    // default      Gauss linear;
}

laplacianSchemes
{
    // Original: corrected
    default         Gauss linear corrected;
    
    // Faster: limited correction
    // default      Gauss linear limited 0.5;
}
```

> [!WARNING]
> Changing schemes may affect accuracy!
> Only use for well-behaved meshes

---

## Step 6: Compiler Optimization

### Recompile with Optimization

```bash
# Edit Make/options
EXE_INC = \
    ... \
    -O3 \
    -march=native \
    -DNDEBUG              # Disable debug checks

# Recompile
wmake
```

**Expected:** 10-20% faster

---

## Step 7: Measure Improvement

### Run Optimized Case

```bash
time mpirun -np 4 myHeatFoam -parallel > log.optimized 2>&1

# Compare
BASELINE=120
OPTIMIZED=$(grep "ClockTime" log.optimized | tail -1 | awk '{print $3}')
SPEEDUP=$(echo "scale=2; $BASELINE / $OPTIMIZED" | bc)
echo "Speedup: ${SPEEDUP}x"
```

---

## Step-by-Step Optimization Results

### Optimization 1: เปลี่ยนจาก PCG เป็น GAMG

**ก่อน (PCG):**
```bash
# system/fvSolution
solvers
{
    T
    {
        solver          PCG;
        preconditioner  DIC;
        tolerance       1e-06;
        relTol          0;
    }
}
```

**Runtime output:**
```bash
Time = 0.1
T: Solving, Initial residual = 1.00e-02, Final residual = 9.87e-07, No Iterations 45
ExecutionTime = 8.54 s  ClockTime = 10 s

Time = 0.2
T: Solving, Initial residual = 9.85e-03, Final residual = 9.76e-07, No Iterations 44
ExecutionTime = 17.12 s ClockTime = 20 s
...
Final ClockTime = 120 s
```

**After (GAMG):**
```bash
# system/fvSolution
solvers
{
    T
    {
        solver          GAMG;
        smoother        GaussSeidel;
        tolerance       1e-06;
        relTol          0;
        nPreSweeps      0;
        nPostSweeps     2;
        nFinestSweeps   2;
        cacheAgglomeration on;
        agglomerator    faceAreaPair;
        mergeLevels     1;
    }
}
```

**Runtime output:**
```bash
Time = 0.1
T: Solving, Initial residual = 1.00e-02, Final residual = 9.92e-07, No Iterations 8
ExecutionTime = 5.82 s  ClockTime = 6 s

Time = 0.2
T: Solving, Initial residual = 9.88e-03, Final residual = 9.78e-07, No Iterations 7
ExecutionTime = 11.64 s ClockTime = 12 s
...
Final ClockTime = 80 s
```

**Results:**
- **Time:** 120s → 80s
- **Speedup:** 1.5x
- **Iterations:** 45 → 8 per timestep
- **Why:** Multigrid solves multiple scales simultaneously

---

### Optimization 2: เพิ่ม relTol

**ก่อน (relTol = 0):**
```bash
T: Solving, Initial residual = 1.00e-02, Final residual = 9.92e-07, No Iterations 8
```

**After (relTol = 0.01):**
```bash
solvers
{
    T
    {
        solver          GAMG;
        relTol          0.01;       // Stop early!
        // ... other settings
    }
}
```

**Runtime output:**
```bash
T: Solving, Initial residual = 1.00e-02, Final residual = 8.54e-05, No Iterations 3
ExecutionTime = 3.12 s  ClockTime = 3.5 s
```

**Results:**
- **Time:** 80s → 70s
- **Speedup:** 1.14x
- **Iterations:** 8 → 3 per timestep
- **Accuracy:** residual reduced to 1e-4 instead of 1e-6 (still good enough!)

**Verification of accuracy:**
```python
# Compare final T field
import numpy as np

T_baseline = np.loadtxt('baseline_T.csv')
T_relTol = np.loadtxt('reltol_T.csv')

error = np.max(np.abs(T_baseline - T_relTol))
print(f"Max difference: {error:.6e}")
# Output: Max difference: 2.345e-04 (negligible!)
```

---

### Optimization 3: ลด I/O

**ก่อน (write ทุก 0.1s):**
```bash
# system/controlDict
writeControl    runTime;
writeInterval   0.1;
```

**Output:**
```bash
Time = 0.1
T: Solving...
Writing T
ExecutionTime = 5.82 s  ClockTime = 6 s
Writing T to file "0.1/T" ← I/O overhead!

Time = 0.2
T: Solving...
Writing T
ExecutionTime = 11.64 s ClockTime = 12 s
Writing T to file "0.2/T" ← I/O overhead!
```

**หลัง (write ทุก 1s):**
```bash
# system/controlDict
writeControl    runTime;
writeInterval   1;       // 10x less frequent!
writeCompression true;   // Compressed files
purgeWrite      5;       // Keep only last 5 timesteps
```

**Runtime output:**
```bash
Time = 0.1
T: Solving...
ExecutionTime = 5.42 s  ClockTime = 5.8 s  ← No I/O!

Time = 0.2
T: Solving...
ExecutionTime = 10.84 s ClockTime = 11.6 s ← No I/O!

Time = 1.0
T: Solving...
Writing T
ExecutionTime = 54.2 s ClockTime = 58 s
Writing T to file "1/T" ← Only write now!
```

**Results:**
- **Time:** 70s → 65s
- **Speedup:** 1.08x
- **Disk writes:** 100 → 10 files
- **Disk space:** 2.5GB → 250MB (with compression)

---

### Optimization 4: Compiler Optimization

**ก่อน (-O1, debug mode):**
```bash
# Make/options
EXE_INC = \
    -I$(LIB_SRC)/finiteVolume/lnInclude \
    -I$(LIB_SRC)/meshTools/lnInclude \
    -g -O1      # Debug symbols, low optimization
```

**Check current binary:**
```bash
$ file myHeatFoam
myHeatFoam: ELF 64-bit LSB executable, x86-64, not stripped

$ size myHeatFoam
   text    data     bss     dec     hex filename
 245832   12480   28764  287076   461f4 myHeatFoam
```

**หลัง (-O3, native architecture):**
```bash
# Make/options
EXE_INC = \
    -I$(LIB_SRC)/finiteVolume/lnInclude \
    -I$(LIB_SRC)/meshTools/lnInclude \
    -O3 \                    # Maximum optimization
    -march=native \          # CPU-specific instructions
    -DNDEBUG \               # No debug checks
    -funroll-loops           # Unroll loops
```

**Recompile:**
```bash
$ wclean
$ wmake

Making dependency list for source file myHeatFoam.C
SOURCE=myHeatFoam.C ;  g++ -std=c++11 -m64 -Dlinux64 \
    -DMPICH_SKIP_MPICXX -fPIC -O3 -march=native -DNDEBUG \
    -funroll-loops -I... -c myHeatFoam.C
...
LD: g++ -std=c++11 -m64 -Dlinux64 -DMPICH_SKIP_MPICXX \
    -fPIC -O3 -march=native -Xlinker --add-needed \
    -o /home/user/OpenFOAM/.../platforms/linux64GccDPInt32Opt/bin/myHeatFoam
```

**Check optimized binary:**
```bash
$ size myHeatFoam
   text    data     bss     dec     hex filename
 312456   12840   29876  355172   56b64 myHeatFoam  ← Larger (unrolled loops)
```

**Runtime comparison:**
```bash
# Before (-O1)
$ time mpirun -np 4 myHeatFoam -parallel
real    1m5.000s
user    3m45.200s
sys     0m15.400s

# After (-O3 -march=native)
$ time mpirun -np 4 myHeatFoam -parallel
real    0m55.000s
user    3m10.800s
sys     0m12.200s
```

**Results:**
- **Time:** 65s → 55s
- **Speedup:** 1.18x
- **Code size:** Increased 23% (unrolled loops)
- **Note:** Binary is larger but runs faster!

---

## สรุปการ Optimization ทั้งหมด

| Step | Optimization | Time (s) | Δ Time | Speedup | Cumulative |
|:---:|:---|:---:|:---:|:---:|:---:|
| 0 | **Baseline (PCG)** | 120 | — | 1.00x | 1.00x |
| 1 | Switch to GAMG | 80 | -40 | 1.50x | 1.50x |
| 2 | Add relTol 0.01 | 70 | -10 | 1.14x | 1.71x |
| 3 | Reduce I/O | 65 | -5 | 1.08x | **1.85x** |
| 4 | Compiler -O3 | 55 | -10 | 1.18x | **2.18x** |

**Goal achieved: 2x speedup!** 🎉

---

## ตารางเปรียบเทียบก่อน/หลัง

| Metric | Baseline | Optimized | Improvement |
|:---|:---:|:---:|:---:|
| **Total Time** | 120 s | 55 s | **2.18x faster** |
| **Solver Iterations** | 45/timestep | 3/timestep | 15x fewer |
| **Total Iterations** | 15,000 | 1,000 | 15x fewer |
| **Time per Iteration** | 8 ms | 55 ms | 7x slower (but OK!) |
| **Write Events** | 100 | 10 | 10x fewer |
| **Disk Usage** | 2.5 GB | 250 MB | 10x less |
| **Binary Size** | 287 KB | 355 KB | +24% |
| **Memory Usage** | 1.2 GB | 1.1 GB | -8% |
| **Max T Error** | — | 2.3e-4 | Negligible |

---

## Additional Optimizations

### 1. Under-relaxation Tuning

```cpp
relaxationFactors
{
    equations
    {
        T       0.9;    // Higher = faster convergence
    }
}
```

### 2. Adjust Iterations

```cpp
PIMPLE
{
    nOuterCorrectors    2;    // Reduce if stable
    nCorrectors         1;
}
```

### 3. Time Step

```cpp
deltaT          0.01;     // Larger if stable
```

---

## Measuring Specific Improvements

### Linear Solver Iterations

```bash
# Count solver iterations
grep "iterations" log.baseline | wc -l
grep "iterations" log.optimized | wc -l

# Fewer iterations = faster solver
```

### Time per Iteration

```bash
# Calculate
grep "ExecutionTime" log.* | awk '{print $5}' | sort -n | tail -10
```

---

## ปัญหา Profiling และ Optimization ที่พบบ่อย

### ปัญหา 1: perf ไม่มี

**อาการ:**
```bash
$ perf record -g myHeatFoam
bash: perf: command not found
```

**วินิจฉัย:** perf tools ไม่ได้ติดตั้งในระบบ

**วิธีแก้:**
```bash
# Ubuntu/Debian
sudo apt-get install linux-tools-common linux-tools-generic

# CentOS/RHEL
sudo yum install perf

# Or use alternative profiling methods
# Option 1: gprof (requires recompilation with -pg)
# Option 2: time command (basic timing)
# Option 3: OpenFOAM built-in profiling
```

---

### ปัญหา 2: ไม่มีสิทธิ์ใช้ perf

**อาการ:**
```bash
$ perf record -g myHeatFoam
Error:
You may not have permission to collect stats.
Consider tweaking /proc/sys/kernel/perf_event_paranoid:
-1 - For system-wide profiling
0 - For kernel profiling (needs CAP_SYS_ADMIN)
1 - For profiling kernel and user space (default)
2 - For user-space profiling only
>=3 - No profiling allowed
```

**วิธีแก้:**
```bash
# Temporary fix (current session only)
echo 0 | sudo tee /proc/sys/kernel/perf_event_paranoid

# Permanent fix (add to /etc/sysctl.conf)
echo "kernel.perf_event_paranoid = 0" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# Alternative: Run with sudo (not recommended for production)
sudo perf record -g myHeatFoam
```

---

### ปัญหา 3: Solver Diverge หลัง Optimization

**อาการ:**
```bash
Time = 5.0
T: Solving, Initial residual = 1.00e+00, Final residual = nan, No Iterations 1000
--> FOAM FATAL ERROR:
Illegal wave speed detected
```

**วินิจฉัย:** relTol aggressive เกินไปหรือ solver settings ไม่เข้ากัน

**วิธีแก้:**
```bash
# 1. Reduce relTol gradually
relTol 0.01;   # Was 0.1
relTol 0.001;  # Even more conservative

# 2. Check mesh quality
checkMesh

# 3. Verify time step stability
deltaT  0.001;  # Reduce from 0.01

# 4. Add under-relaxation
relaxationFactors
{
    equations
    {
        T       0.7;    # Reduce from 0.9
    }
}
```

---

### ปัญหา 4: GAMG ช้ากว่า PCG

**อาการ:**
```bash
# With PCG: 60 seconds
# With GAMG: 85 seconds ← Slower!
```

**วินิจฉัย:** GAMG overhead สูงเกินไปสำหรับปัญหาเล็กหรือ settings ผิด

**วิธีแก้:**
```bash
# 1. Check problem size
# GAMG is only beneficial for >100k cells

# 2. Optimize GAMG parameters
solvers
{
    T
    {
        solver          GAMG;
        smoother        GaussSeidel;     // Try: DILU, DIC
        nPreSweeps      0;               // Try: 1
        nPostSweeps     2;               // Try: 1
        nFinestSweeps   2;               // Try: 1
        cacheAgglomeration on;           // Critical!
        mergeLevels     1;               // Try: 2
        maxCoarseDirs  50;              // Add this
    }
}

# 3. For small meshes, stick with PCG
solvers
{
    T
    {
        solver          PCG;
        preconditioner  DIC;             // Or DILU
    }
}
```

---

### ปัญหา 5: -O3 Compilation ได้ผลลัพธ์ผิด

**อาการ:**
```bash
# Results with -O1: Max T = 350 K
# Results with -O3: Max T = 312 K ← Different!
```

**วินิจฉัย:** Aggressive optimization เปลี่ยนพฤติกรรม floating-point

**วิธีแก้:**
```bash
# 1. Verify it's not numerical tolerance
diff <(grep "ClockTime" log.O1) <(grep "ClockTime" log.O3)

# 2. Check for strict aliasing issues
EXE_INC = \
    ... \
    -O3 \
    -fno-strict-aliasing    # Add this

# 3. Ensure floating-point consistency
EXE_INC = \
    ... \
    -O3 \
    -fno-fast-math          # Don't reorder FP operations

# 4. Use intermediate optimization
EXE_INC = \
    ... \
    -O2                     # Between -O1 and -O3
```

---

### ปัญหา 6: ไม่สามารถทำ 2x Speedup ได้

**อาการ:** ได้แค่ 1.3x speedup แม้ทำครบทุก optimization

**วินิจฉัย:**
1. Baseline ดีอยู่แล้ว
2. Optimize ผิดจุด
3. Mesh size เล็กเกินไป

**วิธีแก้:**
```bash
# 1. Check if baseline is already efficient
perf report baseline
# If solver is only 30% of time, optimizing it gives <1.3x

# 2. Identify real bottleneck
perf report --hierarchy
# Maybe I/O or turbulence model is the issue

# 3. Try larger problem size
# Scale up mesh by 8x (2x in each direction)
# Better parallel scaling with larger problems

# 4. Consider algorithmic changes
# Switch turbulence model: kEpsilon → kOmegaSST
# Use faster BC: zeroGradient → fixedValue
```

---

### Issue 7: Disk Space Running Out

**Symptom:**
```bash
$ ls -lh 0.1/T
-rw-r--r-- 1 user user 2.5G Oct 15 10:30 0.1/T

$ df -h .
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1       50G   48G  2.0G  96% /home  ← Almost full!
```

**Solution:**
```bash
# Immediate: Clean old time directories
rm -rf 0.*
foamListTimes -rm

# Add to controlDict:
writeControl    runTime;
writeInterval   1;         # Write less frequently
writeCompression true;     # Compress output
purgeWrite      3;         # Keep only last 3 timesteps

# Add to system/controlDict:
functions
{
    # Only write essential fields
    writeFields
    {
        type            sets;
        fields          (T);  # Only T, not U, p, k, epsilon
    }
}

# Post-process on-the-fly (don't store)
functions
{
    probes
    {
        type            probes;
        functionObjectLibs ("libsampling.so");
        writeControl    timeStep;
        writeInterval   1;
        probeLocations  ( (0.05 0.05 0) );  // Single point
        fields          (T);
    }
}
```

---

## Optimization Verification Checklist

Before claiming "2x speedup", verify:

- [ ] **Accuracy preserved:**
  ```bash
  # Compare key metrics
  baseline_T=$(tail -1 postProcessing/patchAverage/baseline/right_T.dat | awk '{print $2}')
  optimized_T=$(tail -1 postProcessing/patchAverage/optimized/right_T.dat | awk '{print $2}')
  error=$(echo "scale=6; ($baseline_T - $optimized_T) / $baseline_T" | bc)
  echo "Relative error: $error"
  # Should be < 1%
  ```

- [ ] **Reproducible:**
  ```bash
  # Run 3 times
  for i in 1 2 3; do
      time mpirun -np 4 myHeatFoam -parallel > log.run.$i 2>&1
  done

  # Check variance < 5%
  ```

- [ ] **Stable convergence:**
  ```bash
  # Check residuals
  grep "Final residual" log.optimized | tail -20
  # Should monotonically decrease
  ```

- [ ] **Physical correctness:**
  ```bash
  # Check energy balance
  # Heat flux in should equal heat flux out
  ```

---

## Concept Check

<details>
<summary><b>1. ทำไม GAMG เร็วกว่า PCG?</b></summary>

**PCG:** (Conjugate Gradient)
- O(n) per iteration
- Many iterations needed
- Doesn't handle scales well

**GAMG:** (Algebraic Multigrid)
- O(n) total (optimal!)
- Solves coarse and fine together
- Excellent for Laplacian equations

**When GAMG works best:**
- Elliptic equations (pressure, temperature)
- Large meshes (>100k cells)
</details>

<details>
<summary><b>2. relTol ทำอะไร?</b></summary>

**Stopping criteria:**
- `tolerance`: Stop when residual < tolerance
- `relTol`: Stop when residual < relTol × initial_residual

**Example:**
```
Initial residual: 1e-2
tolerance: 1e-6
relTol: 0.01

Stop when:
  residual < 1e-6  OR
  residual < 0.01 × 1e-2 = 1e-4  ← This triggers first!
```

**relTol 0.01:** "Reduce residual by 100x" — often enough!
</details>

---

## Final Checklist

- [ ] Profile completed
- [ ] Hotspots identified
- [ ] Linear solver optimized
- [ ] I/O reduced
- [ ] Compiler flags set
- [ ] **2x speedup achieved**
- [ ] Before/after comparison documented

---

## Project Complete! 🎉

คุณได้สร้าง:
1. Heat equation solver จาก scratch
2. Custom boundary condition
3. Turbulence integration
4. Parallel execution
5. Optimized performance

**พร้อมสำหรับเขียน CFD Engine ของคุณเอง!**

---

## ก้าวต่อไป

- [Beyond OpenFOAM](../05_BEYOND_OPENFOAM/00_Overview.md) — เรียนรู้ alternatives
- เริ่มต้น project ใหม่ของคุณเอง!
