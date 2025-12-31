# Phase 5: Optimization

---

## Learning Objectives

By the end of this phase, you will be able to:

- **Apply profiling techniques** (perf, gprof) to identify performance hotspots in OpenFOAM solvers
- **Optimize linear solver settings** by selecting appropriate algorithms and preconditioners for your problem type
- **Balance accuracy vs. speed** through intelligent tolerance settings and discretization scheme adjustments
- **Measure and validate performance improvements** quantitatively with before/after comparisons
- **Achieve 2x speedup** through systematic optimization while maintaining solution accuracy

---

## 1. Why Optimization? (The Why)

Performance optimization is critical for practical CFD workflows:

- **Faster design iterations**: Reduce simulation time from hours to minutes
- **Larger problems**: Enable more detailed meshes within reasonable timeframes
- **Cost efficiency**: Maximize HPC cluster utilization and reduce computational costs
- **Competitive advantage**: Rapid prototyping requires rapid simulation

**The optimization challenge**: OpenFOAM solvers have dozens of tunable parameters. Which ones matter most? How do you avoid sacrificing accuracy? This phase teaches you a systematic approach.

---

## 2. Optimization Strategy (The What)

### The Optimization Hierarchy

Not all optimizations yield equal benefits. Focus efforts on high-impact areas:

```
Impact hierarchy (typical turbulent flow):
┌─────────────────────────────────────────────────────┐
│ 65% Linear Solver (GAMG vs PCG)          ← BIGGEST │
│ 15% Gradient/Divergence Schemes                    │
│ 10% I/O Operations                                  │
│ 5%  Compiler Optimization                           │
│ 5%  Other (mesh, BCs, etc.)                        │
└─────────────────────────────────────────────────────┘
```

### Optimization Decision Tree

<details>
<summary><b>Click to expand: Optimization Strategy Selection Guide</b></summary>

```
START: Measure baseline performance
│
├─ What is problem size?
│  ├─ < 50k cells → Focus on compiler flags, stay with PCG
│  └─ > 100k cells → Use GAMG, parallel scaling
│
├─ Where is time spent? (Run perf/gprof)
│  ├─ > 60% in linear solver → Optimize fvSolution settings
│  ├─ > 30% in I/O → Reduce write frequency
│  ├─ > 20% in gradients → Check discretization schemes
│  └─ > 15% in turbulence → Consider simpler model
│
├─ Is solution accuracy critical?
│  ├─ YES → Keep relTol=0, monitor residuals closely
│  └─ NO  → Use relTol=0.01, accept small accuracy loss
│
└─ Target speedup achieved?
   ├─ NO → Try additional optimizations from hierarchy
   └─ YES → Verify accuracy, document results
```

</details>

### Key Parameters to Tune

| Parameter | Impact | Trade-off |
|:---|:---|:---|
| **Solver type** (PCG → GAMG) | ⭐⭐⭐⭐⭐ | Memory usage, setup cost |
| **relTol** (0 → 0.01) | ⭐⭐⭐⭐ | Accuracy |
| **Write interval** | ⭐⭐⭐ | Data resolution |
| **Compiler flags** (-O1 → -O3) | ⭐⭐⭐ | Compilation time, debugging |
| **Discretization schemes** | ⭐⭐ | Accuracy |

---

## 3. Implementation Guide (The How)

### Step 1: Establish Performance Baseline

**Before optimizing anything, measure your starting point.**

<details>
<summary><b>Checkpoint: Expected Baseline Output</b></summary>

```bash
cd tutorials/turbulent_channel

# Run baseline case with timing
time mpirun -np 4 myHeatFoam -parallel > log.baseline 2>&1

# Extract final clock time
grep "ClockTime" log.baseline | tail -1
# Expected: ClockTime = 120 s (example - yours will vary)

# Count total solver iterations
grep "No Iterations" log.baseline | wc -l
# Expected: ~15,000 total iterations
```

**Record your baseline:**
- Total runtime: _____ s
- Solver iterations: _____
- Memory usage: _____ GB

</details>

### Step 2: Profile to Identify Hotspots

**Profiling reveals where time is actually spent—don't guess!**

<details>
<summary><b>Option A: Using perf (Linux kernel profiling)</b></summary>

```bash
# Profile single-processor run for detailed analysis
perf record -g myHeatFoam > log.profile 2>&1

# Generate hierarchical report
perf report --hierarchy
```

**Expected output excerpt** (top 10 lines shown):
```bash
# Children      Self  Command  Shared Object       Symbol
    65.25%     0.00%  myHeatFoam  myHeatFoam          [.] Foam::fvMatrix<double>::solve
    42.18%     0.00%  myHeatFoam  libmyHeatFoam.so    [.] Foam::GAMG::solve
    38.50%     2.15%  myHeatFoam  libGAMGPrecon.so    [.] Foam::GAMG::performCycle
    15.32%     0.85%  myHeatFoam  libfiniteVolume.so  [.] Foam::fvc::grad<double>
    12.45%     0.42%  myHeatFoam  libfiniteVolume.so  [.] Foam::fvm::div<double>
     8.76%     0.31%  myHeatFoam  libturbulence.so    [.] Foam::kEpsilon::correct
     6.18%     0.18%  myHeatFoam  libfiniteVolume.so  [.] Foam::lduMatrix::Amul
     5.32%     5.32%  myHeatFoam  [kernel]            [k] memcpy
```

**Interpretation:**
- **65%** in linear solver (`fvMatrix::solve`) ← **Primary target!**
- **42%** in GAMG preconditioner
- **15%** in gradient calculations
- **12%** in divergence terms

</details>

<details>
<summary><b>Option B: Using gprof (GCC profiling)</b></summary>

```bash
# Step 1: Recompile with profiling flags
cd myHeatFoam
vim Make/options

# Add profiling flag:
EXE_INC = \
    ... \
    -pg

# Step 2: Recompile
wclean
wmake

# Step 3: Run solver to generate profiling data
myHeatFoam

# Step 4: Analyze
gprof myHeatFoam gmon.out > gprof_report.txt
```

**Expected output excerpt:**
```
Flat profile:

 %   cumulative   self              self     total
time   seconds   seconds    calls  us/call  us/call  name
42.18      5.06     5.06   150000     33.7     45.2  Foam::GAMG::solve
15.32      6.90     1.84    30000     61.3    125.0  Foam::fvc::grad<double>
12.45      8.39     1.49    30000     49.7    102.3  Foam::fvm::div<double>
 8.76      9.44     1.05    15000     70.0    150.0  Foam::kEpsilon::correct
 6.18     10.18     0.74   450000      1.6      3.2  Foam::lduMatrix::Amul
```

**Remove profiling flags after analysis** (they slow down execution by ~10%).

</details>

#### Troubleshooting: Profiling Issues

<details>
<summary><b>Issue: perf command not found</b></summary>

**Solution:**
```bash
# Ubuntu/Debian
sudo apt-get install linux-tools-common linux-tools-generic

# CentOS/RHEL
sudo yum install perf

# Alternative: Use built-in OpenFOAM timing
time mpirun -np 4 myHeatFoam -parallel
```

</details>

<details>
<summary><b>Issue: perf permission denied</b></summary>

**Solution:**
```bash
# Temporary fix (current session)
echo 0 | sudo tee /proc/sys/kernel/perf_event_paranoid

# Permanent fix
echo "kernel.perf_event_paranoid = 0" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

</details>

---

### Step 3: Optimize Linear Solver Settings

**The highest-impact optimization—typically 30-50% speedup.**

#### Original Configuration (system/fvSolution)

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

**Typical performance:**
- Iterations per timestep: 40-50
- Total runtime: 120 s (baseline)

#### Optimized Configuration

```cpp
solvers
{
    T
    {
        solver          GAMG;              // Multigrid solver
        smoother        GaussSeidel;
        tolerance       1e-06;
        relTol          0.01;              // Stop at 1% of initial residual
        nPreSweeps      0;
        nPostSweeps     2;
        nFinestSweeps   2;
        cacheAgglomeration true;           // Cache mesh agglomeration
        agglomerator    faceAreaPair;
        mergeLevels     1;
    }
}
```

**Key changes:**
- **PCG → GAMG**: Algebraic multigrid solves multiple scales simultaneously
- **relTol 0 → 0.01**: Stop when residual reduced by 100x (vs. absolute tolerance)
- **cacheAgglomeration**: Reuse mesh coarsening structure

<details>
<summary><b>Checkpoint: Expected Performance Improvement</b></summary>

```bash
# Run optimized case
mpirun -np 4 myHeatFoam -parallel > log.gamg 2>&1

# Compare iterations
echo "Baseline iterations:"
grep "No Iterations" log.baseline | head -5
echo "GAMG iterations:"
grep "No Iterations" log.gamg | head -5

# Expected output:
# Baseline:  T: Solving, ..., No Iterations 45
# GAMG:      T: Solving, ..., No Iterations 8

# Measure speedup
BASELINE=120
GAMG_TIME=$(grep "ClockTime" log.gamg | tail -1 | awk '{print $3}')
SPEEDUP=$(echo "scale=2; $BASELINE / $GAMG_TIME" | bc)
echo "Speedup: ${SPEEDUP}x"
# Expected: 1.4x - 1.6x
```

**Expected results:**
- Runtime: 120s → 75s (1.6x speedup)
- Iterations per step: 45 → 8
- **Why it works**: Multigrid eliminates low-frequency errors efficiently

</details>

#### Troubleshooting: Solver Optimization

<details>
<summary><b>Issue: GAMG slower than PCG on small meshes</b></summary>

**Diagnosis**: GAMG has setup overhead. For meshes < 100k cells, PCG may be faster.

**Solution**:
```cpp
// For small meshes (< 100k cells), use optimized PCG
solvers
{
    T
    {
        solver          PCG;
        preconditioner  DIC;              // Or DILU for better convergence
        tolerance       1e-06;
        relTol          0.01;
    }
}

// For large meshes (> 100k cells), use GAMG
solvers
{
    T
    {
        solver          GAMG;
        // ... (as above)
    }
}
```

</details>

<details>
<summary><b>Issue: Solver divergence after optimization</b></summary>

**Diagnosis**: relTol too aggressive or solver settings incompatible with mesh quality.

**Solution**:
```bash
# 1. Reduce relTol gradually
relTol 0.001;     // More conservative than 0.01

# 2. Check mesh quality
checkMesh

# 3. Verify time step stability
deltaT  0.001;    // Reduce if unstable

# 4. Add under-relaxation (if using PIMPLE)
relaxationFactors
{
    equations
    {
        T       0.7;    // Reduce from 1.0
    }
}
```

</details>

---

### Step 4: Reduce I/O Overhead

**Frequent file writes can stall simulations—especially on parallel filesystems.**

#### Original Configuration (system/controlDict)

```cpp
writeControl    runTime;
writeInterval   0.1;     // Write every 0.1 seconds
```

**Impact**: 100 write events over 10-second simulation

#### Optimized Configuration

```cpp
writeControl    runTime;
writeInterval   1;       // Write every 1 second (10x reduction)
writeCompression true;   // Compress output files
purgeWrite      5;       // Keep only last 5 timesteps
```

**Additional optimization**: Write only essential fields
```cpp
functions
{
    writeFields
    {
        type            sets;
        fields          (T);     // Only temperature, not U, p, k, epsilon
    }
}
```

<details>
<summary><b>Checkpoint: Expected I/O Reduction</b></summary>

```bash
# Compare disk usage
du -sh 0.* baseline/
du -sh 1.* optimized/

# Expected results:
# Baseline:  2.5 GB (100 time directories)
# Optimized: 250 MB  (10 time directories, compressed)

# Runtime comparison
echo "Baseline with frequent I/O:"
grep "ClockTime" log.baseline | tail -1
# ClockTime = 80 s (after GAMG optimization)

echo "Optimized with reduced I/O:"
grep "ClockTime" log.io_optimized | tail -1
# ClockTime = 72 s

# Speedup: 1.11x cumulative
```

**Expected results:**
- Runtime: 80s → 72s (1.11x speedup)
- Disk usage: 2.5 GB → 250 MB (10x reduction)

</details>

#### Troubleshooting: I/O Issues

<details>
<summary><b>Issue: Disk space exhausted</b></summary>

**Immediate action**:
```bash
# Remove old time directories
foamListTimes -rm

# Check disk space
df -h .
```

**Preventive configuration** (add to controlDict):
```cpp
writeControl    runTime;
writeInterval   2;             // Write even less frequently
writeCompression true;
purgeWrite      3;             // Keep only last 3 snapshots

// Post-process on-the-fly instead of storing
functions
{
    probes
    {
        type            probes;
        functionObjectLibs ("libsampling.so");
        writeControl    timeStep;
        writeInterval   1;
        probeLocations  ( (0.05 0.05 0) );
        fields          (T);
    }
}
```

</details>

---

### Step 5: Adjust Discretization Schemes

**Trade accuracy for speed—only for well-behaved problems.**

<details>
<summary><b>Optional Optimization: Faster schemes (use with caution)</b></summary>

```cpp
// Original: maximum accuracy
gradSchemes
{
    default         Gauss linear corrected;     // Non-orthogonal correction
}

laplacianSchemes
{
    default         Gauss linear corrected;     // Non-orthogonal correction
}

// Faster: reduced corrections (requires high-quality mesh)
gradSchemes
{
    default         Gauss linear;               // No correction (orthogonal only)
}

laplacianSchemes
{
    default         Gauss linear limited 0.5;   // Limited correction
}
```

**When to use**:
- ✓ Mesh is predominantly orthogonal (> 95%)
- ✓ Preliminary design studies
- ✓ Well-understood physics

**When NOT to use**:
- ✗ High aspect ratio cells
- ✗ Complex geometries
- ✗ Production-quality results

**Expected speedup**: 5-10% (varies heavily with mesh quality)

</details>

---

### Step 6: Compiler Optimization

**Rebuild solver with aggressive compiler flags—typically 10-20% speedup.**

#### Step 6a: Check Current Compilation

```bash
# Examine current Make/options
cat myHeatFoam/Make/options

# Check binary size and optimization
file myHeatFoam
size myHeatFoam
```

#### Step 6b: Add Optimization Flags

Edit `myHeatFoam/Make/options`:

```cpp
EXE_INC = \
    -I$(LIB_SRC)/finiteVolume/lnInclude \
    -I$(LIB_SRC)/meshTools/lnInclude \
    -O3 \                    // Maximum optimization
    -march=native \          // CPU-specific instruction sets
    -DNDEBUG \               // Disable debug checks
    -funroll-loops           // Unroll small loops
```

#### Step 6c: Recompile and Verify

```bash
# Clean and rebuild
wclean
wmake

# Check new binary size (should be larger)
size myHeatFoam

# Run benchmark
time mpirun -np 4 myHeatFoam -parallel > log.o3 2>&1
```

<details>
<summary><b>Checkpoint: Expected Compiler Improvement</b></summary>

```bash
# Binary size comparison
# Before (-O1):  text=245KB, data=12KB
# After  (-O3):  text=312KB, data=13KB  (+27% size from loop unrolling)

# Runtime comparison
BASELINE=72
O3_TIME=$(grep "ClockTime" log.o3 | tail -1 | awk '{print $3}')
SPEEDUP=$(echo "scale=2; $BASELINE / $O3_TIME" | bc)
echo "Speedup: ${SPEEDUP}x"
# Expected: 1.15x - 1.20x

# Overall cumulative speedup
echo "Cumulative speedup: $(echo "scale=2; 120 / $O3_TIME" | bc)x"
# Target: 2.0x or higher
```

**Expected results:**
- Runtime: 72s → 60s (1.20x speedup)
- Binary size: +25% (larger but faster)
- **Overall cumulative**: 120s → 60s (2.0x speedup achieved!)

</details>

#### Troubleshooting: Compiler Issues

<details>
<summary><b>Issue: Different results with -O3 optimization</b></summary>

**Diagnosis**: Aggressive optimization can reorder floating-point operations, causing small numerical differences.

**Solutions**:
```bash
# Option 1: Ensure floating-point consistency
EXE_INC = \
    ... \
    -O3 \
    -fno-fast-math          // Don't reorder FP operations

# Option 2: Disable strict aliasing
EXE_INC = \
    ... \
    -O3 \
    -fno-strict-aliasing    // Safer pointer optimization

# Option 3: Use intermediate optimization
EXE_INC = \
    ... \
    -O2                     // Between -O1 and -O3

# Verify accuracy difference is acceptable
diff <(grep "ClockTime" log.O1) <(grep "ClockTime" log.O3)
```

**Acceptable threshold**: < 0.1% difference in key quantities (max T, heat flux, etc.)

</details>

---

### Step 7: Validate Accuracy Preservation

**Speedup is meaningless if results are wrong!**

<details>
<summary><b>Accuracy Verification Checklist</b></summary>

```bash
# 1. Compare key metrics (e.g., max temperature)
BASELINE_T=$(tail -1 postProcessing/baseline/max_T.dat | awk '{print $2}')
OPTIMIZED_T=$(tail -1 postProcessing/optimized/max_T.dat | awk '{print $2}')
ERROR=$(echo "scale=6; ($BASELINE_T - $OPTIMIZED_T) / $BASELINE_T" | bc)
echo "Relative error: $ERROR"
# Should be < 0.01 (1%)

# 2. Check convergence behavior
grep "Final residual" log.optimized | tail -20
# Should monotonically decrease (no oscillations)

# 3. Verify physical consistency
# Example: Energy balance check (heat in = heat out)

# 4. Visual inspection
paraFoam -builtin
# Compare contour plots side-by-side
```

**Acceptance criteria**:
- ✓ Key quantity error < 1%
- ✓ Monotonic residual convergence
- ✓ Physical conservation maintained
- ✓ Visual inspection consistent

</details>

---

## 4. Results Summary

### Optimization Results Table

| Step | Optimization | Time (s) | Δ Time | Speedup | Cumulative |
|:---:|:---|:---:|:---:|:---:|:---:|
| 0 | **Baseline (PCG)** | 120 | — | 1.00× | 1.00× |
| 1 | Switch to GAMG | 75 | -45 | 1.60× | 1.60× |
| 2 | Add relTol 0.01 | 68 | -7 | 1.10× | 1.76× |
| 3 | Reduce I/O | 62 | -6 | 1.10× | 1.94× |
| 4 | Compiler -O3 | 55 | -7 | 1.13× | **2.18×** |

**Goal achieved: 2× speedup!** 🎉

### Before/After Comparison

| Metric | Baseline | Optimized | Improvement |
|:---|:---:|:---:|:---:|
| **Total Time** | 120 s | 55 s | **2.18× faster** |
| **Solver Iterations** | 45/timestep | 3/timestep | 15× fewer |
| **Total Iterations** | 15,000 | 1,000 | 15× fewer |
| **Write Events** | 100 | 10 | 10× fewer |
| **Disk Usage** | 2.5 GB | 250 MB | 10× reduction |
| **Memory Usage** | 1.2 GB | 1.1 GB | 8% reduction |
| **Max Temperature Error** | — | 2.3×10⁻⁴ | Negligible |

---

## 5. Key Takeaways

1. **Profile before optimizing**: Never guess where time is spent. Use perf or gprof to identify hotspots quantitatively.

2. **Focus on high-impact areas**: The linear solver typically consumes 60-70% of runtime. Optimize this first for maximum ROI.

3. **GAMG > PCG for large meshes**: Algebraic multigrid solvers provide 1.5-2× speedup on meshes > 100k cells by handling multiple scales simultaneously.

4. **relTol is your friend**: Setting relTol=0.01 (stop at 1% of initial residual) provides 10-15% speedup with minimal accuracy loss for most engineering applications.

5. **I/O matters**: Frequent file writes can consume 10-15% of runtime. Reduce write frequency and enable compression for substantial gains.

6. **Compiler flags are easy wins**: -O3 -march=native provides 10-20% speedup with zero code changes.

7. **Validate everything**: Speedup is worthless if results are wrong. Always verify key quantities within 1% of baseline.

8. **Diminishing returns apply**: Each optimization yields smaller gains. Stop when the cost (complexity, accuracy risk) exceeds the benefit.

9. **Problem size matters**: GAMG and advanced optimizations pay off primarily on large meshes. Small problems may not benefit.

10. **Document your optimizations**: Keep a log of changes and their impact for future reference and reproducibility.

---

## 6. Concept Check

<details>
<summary><b>1. Why is GAMG faster than PCG for large problems?</b></summary>

**Answer:**

**PCG (Preconditioned Conjugate Gradient):**
- O(n) per iteration
- Requires many iterations (40-50) for convergence
- Struggles with low-frequency errors
- Single-scale solver

**GAMG (Geometric-Algebraic Multigrid):**
- O(n) total complexity (optimal!)
- Solves coarse and fine scales simultaneously
- Eliminates low-frequency errors on coarse grids
- Fewer iterations (3-8) per timestep

**When GAMG excels:**
- Elliptic equations (pressure Poisson, heat diffusion)
- Large meshes (> 100k cells)
- Problems with multiple length scales

**When PCG is better:**
- Small meshes (< 50k cells)
- Limited memory availability
- Quick prototype runs

</details>

<details>
<summary><b>2. What does relTol actually do?</b></summary>

**Answer:**

relTol provides a **relative stopping criterion** vs. the absolute tolerance.

**Stopping condition**: Solver stops when EITHER condition is met:
```
residual < tolerance          (absolute: e.g., 1e-6)
OR
residual < relTol × initial_residual  (relative: e.g., 1e-4)
```

**Example:**
```
Initial residual: 1e-2
tolerance:       1e-6
relTol:          0.01

Stop when:
  residual < 1e-6                        (would take many iterations)
  OR residual < 0.01 × 1e-2 = 1e-4       (triggers first!)
```

**relTol=0.01 means**: "Reduce residual by 100× from initial value"

**Why it works**: Early timesteps don't need machine precision. 1% residual is often sufficient for convergence to final solution.

</details>

<details>
<summary><b>3. Why does -O3 produce different results than -O1?</b></summary>

**Answer:**

Aggressive compiler optimizations can change floating-point operation order:

**-O1 optimizations** (conservative):
- Basic inlining
- Simple loop unrolling
- Preserves FP operation order

**-O3 optimizations** (aggressive):
- Extensive loop unrolling
- Vectorization (SIMD)
- Instruction reordering
- **Can change FP addition order**

**The problem**: Floating-point addition is not associative due to rounding:
```cpp
(a + b) + c ≠ a + (b + c)  // Different rounding!
```

**Solutions**:
1. Verify accuracy difference is acceptable (< 0.1%)
2. Use `-fno-fast-math` to preserve FP operation order
3. Use `-O2` as intermediate option
4. Ensure reproducibility with fixed random seeds, etc.

**Bottom line**: Small numerical differences are expected. Verify they don't affect engineering conclusions.

</details>

---

## 7. Final Verification Checklist

Before claiming successful optimization, verify:

- [ ] **Baseline measured**: Record initial runtime, iterations, memory usage
- [ ] **Profiling completed**: Identified hotspots with perf or gprof
- [ ] **Linear solver optimized**: GAMG configured for large meshes
- [ ] **Tolerance adjusted**: relTol set to 0.01 (if acceptable)
- [ ] **I/O reduced**: Write interval and compression configured
- [ ] **Compiler flags set**: -O3 -march=native in Make/options
- [ ] **Recompiled**: Solver rebuilt with optimization
- [ ] **Performance measured**: 2× speedup achieved (or better)
- [ ] **Accuracy validated**: Key quantities within 1% of baseline
- [ ] **Convergence verified**: Residuals decrease monotonically
- [ ] **Results documented**: Before/after comparison saved

---

## 8. Project Completion 🎉

Congratulations! You have completed the comprehensive capstone project:

**Phase 1**: Built 1D heat equation solver from scratch  
**Phase 2**: Implemented custom boundary conditions  
**Phase 3**: Integrated turbulence modeling (k-ε)  
**Phase 4**: Parallelized with MPI domain decomposition  
**Phase 5**: Achieved 2× performance optimization  

**Skills mastered**:
- OpenFOAM solver architecture
- Custom boundary condition development
- Runtime selection and polymorphism
- Parallel CFD programming
- Performance profiling and optimization

**You are now ready to**: Design and implement your own CFD engines, extend OpenFOAM for your research, and contribute to the open-source CFD community.

---

## Next Steps

- Explore [Beyond OpenFOAM](../05_BEYOND_OPENFOAM/00_Overview.md) for alternative CFD tools
- Start your own research project with the capstone codebase as a template
- Contribute bug fixes or features to the OpenFOAM foundation
- Dive into advanced topics (template metaprogramming, GPU acceleration)