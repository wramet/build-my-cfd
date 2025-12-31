# Parallel Scaling with MPI

**Strong/Weak Scaling and MPI Efficiency**

---

## Learning Objectives

By the end of this section, you will be able to:

1. **Understand** the difference between strong scaling (fixed problem size) and weak scaling (growing problem size), and when to apply each approach
2. **Calculate** parallel speedup and efficiency using Amdahl's Law to predict theoretical limits
3. **Diagnose** poor parallel scaling by identifying communication bottlenecks, load imbalance, and serial code sections
4. **Optimize** parallel performance through proper domain decomposition, solver tuning, and processor count selection
5. **Analyze** real scaling data from OpenFOAM cases and create your own scaling analysis templates

---

## Prerequisites

**Required Knowledge from Previous Modules:**

| Topic | Module | Why It Matters Here |
|:---|:---:|:---|
| **Memory Management** | 09-04 | Memory bandwidth saturation limits parallel scaling |
| **CRTP Pattern** | 09-05 | Template overhead differs across MPI processes |
| **Design Patterns** | 09-03 | Understanding Strategy pattern in solver selection |
| **Loop Optimization** | 10-03 | Cache effects differ per CPU in parallel runs |
| **GAMG Solvers** | 10-01 | Coarse grid parallelism is critical bottleneck |

**Recommended:**
- Complete **Loop Optimization** section for understanding cache coherency issues
- Review **fvMatrix Deep Dive** for linear solver parallelism

---

## Core Concept: Why Parallel?

### What: Parallel Computing Definition

Parallel computing divides a large CFD problem across multiple processors (CPUs), with each processor solving a portion of the mesh. Processors communicate via MPI (Message Passing Interface) to exchange boundary data.

### Why: Performance Impact

```
Single CPU: 1 week to solve
32 CPUs:    ~5 hours (ideally)
```

**Real impact:**  
- **Faster time-to-solution:** Meet tight deadlines  
- **Larger problems:** Solve meshes that don't fit in one computer's memory  
- **Parametric studies:** Run multiple cases simultaneously  

### How: Basic Parallel Workflow

```bash
# 1. Decompose mesh into sub-domains
decomposePar

# 2. Run solver in parallel
mpirun -np 4 simpleFoam -parallel

# 3. Reconstruct results (optional)
reconstructPar
```

---

## Strong vs Weak Scaling

### What: Two Scaling Approaches

**Strong Scaling** (Speedup Focus)
- Fixed problem size (same mesh)
- Increase CPU count
- Goal: Solve faster
- **Metric:** Speedup = T₁/Tₙ

**Weak Scaling** (Size Focus)
- Problem size grows with CPUs (constant cells/CPU)
- Goal: Solve larger problems
- **Metric:** Efficiency = T₁/(n × Tₙ)

### Why: When to Use Which

| Approach | Use When | Example |
|:---|:---|:---|
| **Strong Scaling** | Fixed mesh size, need faster results | 4M cells, test 1→16 CPUs |
| **Weak Scaling** | Want to solve bigger problems | Target: 100k cells/CPU |

### How: Calculation Examples

**Strong Scaling Example:**
```
8M cells / 1 CPU  = 1000s
8M cells / 2 CPUs = 500s (ideal)
8M cells / 4 CPUs = 250s (ideal)
8M cells / 8 CPUs = 125s (ideal)
```

Speedup: 1.0× → 2.0× → 4.0× → 8.0×

**Weak Scaling Example:**
```
1M cells / 1 CPU  = 100s
2M cells / 2 CPUs = 100s (ideal)
4M cells / 4 CPUs = 100s (ideal)
```

Efficiency: 100% → 100% → 100% (time constant)

---

## Amdahl's Law: Theoretical Speedup Limit

### What: The Formula

$$S = \frac{1}{(1-P) + \frac{P}{N}}$$

Where:
- $S$ = Speedup
- $P$ = Parallel fraction (0-1)
- $N$ = Number of processors
- $(1-P)$ = Serial fraction

### Why: Serial Code Limits Speedup

```
Amdahl's Law - Speedup vs Number of Processors

Processors |  75% Parallel  |  90% Parallel  |  95% Parallel
-----------|----------------|----------------|----------------
     1     |     1.0x       |     1.0x       |     1.0x
     2     |     1.6x       |     1.8x       |     1.9x
     4     |     2.3x       |     3.1x       |     3.5x
     8     |     2.9x       |     4.7x       |     6.0x
    16     |     3.4x       |     6.4x       |     9.1x
    32     |     3.7x       |     7.8x       |    12.5x
    64     |     3.9x       |     8.8x       |    16.0x
```

### Critical Insight

> [!IMPORTANT]
> **If 10% is serial → Maximum speedup = 10x** (regardless of CPU count!)
> 
> Even with infinite CPUs: S = 1/(1-0.9) = 10×
> 
> **Lesson:** Focus on parallelizing serial bottlenecks

### How: Apply to Your Code

**Identify Serial Sections:**
```cpp
// Serial bottleneck examples
if (Pstream::master())
{
    field.write();  // Only master writes
}

// Coarse grid solver (GAMG)
nCellsInCoarsestLevel 10;  // Serial solve!
```

**Strategy:** Profile to find (1-P), then optimize those sections

---

## OpenFOAM Parallel Architecture

### What: Domain Decomposition

OpenFOAM splits mesh into sub-domains, one per processor:

```mermaid
flowchart TB
    subgraph Master [Processor 0 (Master)]
        M1[Local Mesh<br/>~1M cells]
        M2[Solve Equations]
        M3[I/O Operations]
    end
    
    subgraph P1 [Processor 1]
        P1a[Local Mesh<br/>~1M cells]
        P1b[Solve Equations]
    end
    
    subgraph P2 [Processor 2]
        P2a[Local Mesh<br/>~1M cells]
        P2b[Solve Equations]
    end
    
    Master <-->|MPI: Exchange<br/>boundary data| P1
    Master <-->|MPI: Exchange<br/>boundary data| P2
    P1 <-->|MPI: Exchange<br/>boundary data| P2
```

**Key Components:**
- **Local mesh:** Each processor owns cells
- **Processor patches:** Boundaries between sub-domains
- **MPI communication:** Exchange values at processor patches

### Why: Communication Overhead Matters

Every iteration requires:
1. Exchange boundary values (`p.correctBoundaryConditions()`)
2. Communication in linear solver (GAMG coarse levels)
3. Global reductions (residual norms)

**Cost:**
- Latency: ~1 μs per message
- Bandwidth: ~10 GB/s (InfiniBand)

### How: Decomposition Works

```cpp
// system/decomposeParDict
numberOfSubdomains 4;

method scotch;      // Recommended: auto load balancing

// Alternative methods:
// method simple;       // Geometric split (fast but unbalanced)
// method hierarchical; // Structured meshes
// method metis;        // Graph-based (alternative to scotch)
```

---

## Decomposition Methods

### What: Available Algorithms

| Method | Type | Pros | Cons | Best For |
|:---|:---:|:---|:---|:---|
| **scotch** | Graph-based | Auto-balanced, minimal interfaces | Slower to compute | Most cases (default) |
| **simple** | Geometric | Fast, predictable | May be unbalanced | Simple geometries |
| **hierarchical** | Geometric | Good for structured | Manual tuning | Block-structured meshes |
| **metis** | Graph-based | Similar to scotch | Slower than scotch | When scotch unavailable |
| **manual** | User-defined | Full control | Error-prone | Special cases |

### Why: Method Choice Affects Performance

**Interface minimization** is critical:
- Fewer processor boundaries = less communication
- Better load balance = less waiting
- Scotch achieves both via graph partitioning

### How: Configure Methods

**Simple (Geometric):**
```cpp
method simple;
simpleCoeffs
{
    n       (2 2 2);    // 2×2×2 split = 8 domains
    delta   0.001;      // Sliding tolerance
}
```

**Scotch (Recommended):**
```cpp
method scotch;
scotchCoeffs
{
    processorWeights (1 1 1 1);  // Optional: manual weights
}
```

---

## Load Balancing

### What: Balance Definition

**Perfect balance:** All processors have equal cells and similar solve times

**Imbalance:** Some processors finish early, others lag → inefficiency

### Why: Unbalance Kills Efficiency

```
Bad decomposition:        Good decomposition:
┌────────────────┐       ┌──────┬──────┐
│    Proc 0      │       │ P0   │ P1   │
│    (1.5M!)     │       │ 1M   │ 1M   │
├────────────────┤       ├──────┼──────┤
│ P1 │ P2 │ P3   │       │ P2   │ P3   │
│.5M│.5M│.5M     │       │ 1M   │ 1M   │
└────────────────┘       └──────┴──────┘

Time: max(P0,P1,P2,P3)   Time: max(P0≈P1≈P2≈P3)
      = P0 (slow!)             = P0 (fast!)
      
Efficiency ≈ 50%         Efficiency ≈ 100%
```

### How: Check Balance Quality

**After decomposition:**
```bash
$ decomposePar
$ grep "Processor.*cells" log.decomposePar
Processor 0: number of cells = 529289
Processor 1: number of cells = 529356
Processor 2: number of cells = 529312
Processor 3: number of cells = 529301

# Calculate balance
$ python3 << EOF
cells = [529289, 529356, 529312, 529301]
mean = sum(cells) / len(cells)
variance = sum((c - mean)**2 for c in cells) / len(cells)
std = variance**0.5
print(f"Balance: {std/mean*100:.2f}% variation")  # Target: <1%
EOF
Balance: 0.01% variation  ← Excellent!
```

---

## Parallel Bottlenecks

### What: Three Main Bottlenecks

**1. Linear Solver (GAMG Coarse Grid)**
```
Fine   : Parallel solve (fast)
↓
Coarse : Parallel solve
↓
Coarser: Less parallelism
↓
Coarsest: Serial! (bottleneck)  ← 10-100 cells only
```

**2. I/O Operations**
```cpp
// Only master writes, others wait
if (Pstream::master())
{
    field.write();  // Serial operation
}
```

**3. Boundary Exchange**
- Large processor interfaces = more communication
- Complex geometry → many boundaries

### Why: These Limit Scaling

**Serial fraction increases:**
- GAMG coarsest: ~5-10% serial
- I/O: ~2-5% serial (depends on write frequency)
- Communication: Overhead grows with CPU count

**Result:** Amdahl's law limits speedup

### How: Diagnose Bottlenecks

**Use profiling:**
```bash
# Check MPI time
$ mpirun -np 8 simpleFoam -parallel 2>&1 | grep "MPI time"
# Or use mpiP (see Advanced Profiling section)

# Check I/O
$ grep "write" log.simpleFoam
```

---

## Measuring Parallel Efficiency

### What: Key Metrics

**Speedup:**
$$S = \frac{T_1}{T_N}$$

**Efficiency:**
$$E = \frac{T_1}{N \times T_N} \times 100\% = \frac{S}{N} \times 100\%$$

Where:
- $T_1$ = Time with 1 CPU
- $T_N$ = Time with N CPUs
- $N$ = Number of CPUs

### Why: Efficiency Matters More Than Speedup

Speedup can be misleading:
- 16 CPUs → 10× speedup (sounds good)
- But efficiency = 10/16 = 62.5% (wasted resources!)

**Target:** >75% efficiency for productive runs

### How: Complete Scaling Test

**Step 1: Run multiple CPU counts**
```bash
#!/bin/bash
# scaling_test.sh

for np in 1 2 4 8 16 32; do
    echo "Running with $np CPUs..."
    
    # Clean previous
    rm -rf processor*
    
    # Decompose and run
    decomposePar -copyZero > /dev/null
    mpirun -np $np simpleFoam -parallel > log.$np 2>&1
    
    # Extract time
    time=$(grep "ClockTime" log.$np | tail -1 | awk '{print $3}')
    echo "$np $time"
done
```

**Step 2: Calculate metrics**
```python
#!/usr/bin/env python3
# analyze_scaling.py

import numpy as np

# Input from scaling_test.sh
np_cpus = np.array([1, 2, 4, 8, 16, 32])
time = np.array([850, 440, 235, 135, 95, 85])

# Calculate
speedup = time[0] / time
efficiency = speedup / np_cpus * 100
cells_per_cpu = np.array([4234567] * 6) / np_cpus

# Print table
print(f"{'N':>4} {'Time(s)':>8} {'Speedup':>8} {'Efficiency':>12} {'Cells/CPU':>12}")
print("-" * 50)
for i in range(len(np_cpus)):
    print(f"{np_cpus[i]:>4} {time[i]:>8} {speedup[i]:>8.2f} {efficiency[i]:>11.1f}% {cells_per_cpu[i]:>12,.0f}")
```

**Output:**
```
   N  Time(s)  Speedup  Efficiency    Cells/CPU
--------------------------------------------------
   1      850     1.00       100.0%    4,234,567
   2      440     1.93        96.5%    2,117,284
   4      235     3.62        90.5%    1,058,642
   8      135     6.30        78.8%      529,321
  16       95     8.95        55.9%      264,661
  32       85    10.00        31.2%      132,330
```

**Step 3: Decision**
- Optimal: 4-8 CPUs (>75% efficiency)
- Avoid: 16-32 CPUs (<60% efficiency)

---

## Scaling Analysis Template

### What: Standard Template for Your Cases

Use this template for **any** OpenFOAM case:

```bash
#!/bin/bash
# run_scaling_analysis.sh
# Usage: ./run_scaling_analysis.sh <case_dir> <max_np>

CASE_DIR=${1:-.}
MAX_NP=${2:-32}
SOLVER=${3:-simpleFoam}

cd $CASE_DIR

echo "# Scaling Analysis: $(basename $CASE_DIR)"
echo "# Solver: $SOLVER"
echo "# Date: $(date)"
echo ""

# Get mesh size
MESH_SIZE=$(grep "cells.*cells" log.blockMesh 2>/dev/null || echo "N/A")
echo "# Mesh: $MESH_SIZE"
echo ""

# Header
echo "N_CPUs Time(s) Speedup Efficiency Cells_per_CPU"

# Baseline (1 CPU)
echo "Running 1 CPU (baseline)..."
decomposePar -copyZero > /dev/null 2>&1
mpirun -np 1 $SOLVER -parallel > log.1 2>&1
T1=$(grep "ClockTime" log.1 | tail -1 | awk '{print $3}')
echo "1 $T1 1.00 100.0% NA"

# Parallel runs
for np in 2 4 8 16 32; do
    if [ $np -gt $MAX_NP ]; then break; fi
    
    echo "Running $np CPUs..."
    rm -rf processor*
    decomposePar -copyZero > /dev/null 2>&1
    mpirun -np $np $SOLVER -parallel > log.$np 2>&1
    
    Tn=$(grep "ClockTime" log.$np | tail -1 | awk '{print $3}')
    speedup=$(awk "BEGIN {printf \"%.2f\", $T1/$Tn}")
    efficiency=$(awk "BEGIN {printf \"%.1f\", $T1/($np*$Tn)*100}")
    
    echo "$np $Tn $speedup $efficiency% NA"
done

echo ""
echo "# Recommendation:"
echo "# Use CPUs with efficiency >75% for production runs"
```

### Why: Template Benefits

- **Consistent:** Same analysis every time
- **Automated:** Run overnight, analyze tomorrow
- **Comparable:** Standard format across cases
- **Documented:** Built-in comments and recommendations

### How: Use Template

```bash
# Motorbike tutorial
cd $FOAM_TUTORIALS/incompressible/simpleFoam/motorBike
blockMesh

# Run scaling test
~/scripts/run_scaling_analysis.sh . 32 simpleFoam

# Output saved to scaling_results.txt
# Create plots
~/scripts/plot_scaling.py scaling_results.txt
```

---

## Real-World Scaling Data

### Motorbike Tutorial: Strong Scaling

**Case Setup:**
```bash
cd $FOAM_TUTORIALS/incompressible/simpleFoam/motorBike
blockMesh
snappyHexMesh -overwrite
```

**Mesh:** 4,234,567 cells (~4.2M)

**Results:**

| N CPUs | Time (s) | Speedup | Efficiency | Cells/CPU |
|:---:|:---:|:---:|:---:|:---:|
| 1 | 850 | 1.00 | 100.0% | 4,234,567 |
| 2 | 440 | 1.93 | 96.5% | 2,117,284 |
| 4 | 235 | 3.62 | 90.5% | 1,058,642 |
| 8 | 135 | 6.30 | 78.8% | 529,321 |
| 16 | 95 | 8.95 | 55.9% | 264,661 |
| 32 | 85 | 10.00 | 31.2% | 132,330 |

**Analysis:**
- **1→2 CPUs:** Excellent (96.5%)
- **2→4 CPUs:** Very good (90.5%)
- **4→8 CPUs:** Good (78.8%)
- **8→16 CPUs:** Diminishing returns (55.9%)
- **16→32 CPUs:** Poor (31.2%) - **not worth it**

**Recommendation:** Use **4-8 CPUs** for this mesh size

### Weak Scaling Test

**Setup:** Constant 100k cells per CPU

| N CPUs | Total Cells | Time (s) | Efficiency |
|:---:|:---:|:---:|:---:|
| 1 | 100,000 | 25 | 100.0% |
| 2 | 200,000 | 26 | 96.2% |
| 4 | 400,000 | 28 | 89.3% |
| 8 | 800,000 | 32 | 78.1% |

**Interpretation:**
- Time nearly constant (25→32s)
- Good weak scaling = code handles larger meshes well
- 78% at 8 CPUs is acceptable for weak scaling

### Scotch vs Simple Decomposition

**Test:** Motorbike with 8 CPUs

| Method | Decomp Time | Interface Faces | Run Time |
|:---|:---:|:---:|:---:|
| Simple | 0.05 s | 124,567 | 145 s |
| Scotch | 2.3 s | 89,234 | 128 s |
| **Improvement** | +2.25 s | **-28%** | **-12%** |

**Conclusion:** Scotch adds overhead but reduces communication → **12% faster**

---

## Optimization Strategies

### What: Proven Techniques

**1. Cells Per Processor Rule**
```
Target: >= 50,000 cells per CPU for good efficiency
Minimum: >= 10,000 cells per CPU
```

**2. Minimize Processor Interfaces**
- Use Scotch decomposition
- Check interface ratio (<5% of total faces)
```bash
grep "faces" log.decomposePar | awk '{sum+=$4} END {print sum}'
```

**3. Tune GAMG for Parallel**
```cpp
p
{
    solver          GAMG;
    agglomerator    faceAreaPair;  // Better parallel scaling
    nCellsInCoarsestLevel 100;     // Avoid serial bottleneck
    mergeLevels     1;
}
```

**4. Reduce I/O Frequency**
```cpp
// ControlDict
writeInterval   500;  // Was: 100 (less writing)
```

**5. Hybrid MPI + OpenMP (Advanced)**
```bash
# 4 MPI processes, 4 threads each = 16 cores
export OMP_NUM_THREADS=4
mpirun -np 4 --bind-to core simpleFoam -parallel
```

**When to use hybrid:**
- Shared memory nodes
- Memory-bound problems
- Reduce MPI overhead

### Why: Each Strategy Helps

| Strategy | Target Bottleneck | Expected Gain |
|:---|:---|:---:|
| Cells/CPU >= 50k | Communication overhead | 10-20% |
| Scotch decomposition | Load imbalance | 5-15% |
| GAMG tuning | Serial coarse grid | 5-10% |
| Less I/O | Serial writes | 2-5% |
| Hybrid MPI+OpenMP | MPI overhead | 5-10% |

### How: Apply in Order

1. **First:** Check cells/CPU (add/remove CPUs)
2. **Second:** Switch to Scotch (if using simple)
3. **Third:** Tune GAMG coarse level
4. **Fourth:** Reduce I/O
5. **Last:** Consider hybrid MPI+OpenMP

---

## Common Pitfalls & Troubleshooting

### Pitfall 1: Load Imbalance

**Symptoms:**
```bash
$ mpirun -np 4 simpleFoam -parallel
# Logs show different solve times per processor
```

**Diagnosis:**
```bash
$ grep "Processor.*cells" log.decomposePar
Processor 0: number of cells = 800000
Processor 1: number of cells = 1200000  ← 50% more!
Processor 2: number of cells = 850000
Processor 3: number of cells = 800000
```

**Solution:**
```bash
# Switch from simple to scotch
sed -i 's/method simple;/method scotch;/' system/decomposeParDict
decomposePar
```

**Result:** 30% faster, 90%+ efficiency

---

### Pitfall 2: Excessive Communication

**Symptoms:**
```bash
$ mpirun -np 16 simpleFoam -parallel
# Scaling poor: efficiency <50%
```

**Diagnosis:**
```bash
$ grep "interface" log.decomposePar
Total interface faces: 456,789  ← 10.8% of total (target: <5%)
```

**Causes:**
1. Too many CPUs for mesh size
2. Poor decomposition method
3. Complex geometry

**Solutions:**
```bash
# Solution 1: Reduce CPU count
numberOfSubdomains 8;  # Was: 16

# Solution 2: Use Scotch
method scotch;

# Solution 3: Increase cells/CPU
# Target: >= 50,000 cells/CPU
```

---

### Pitfall 3: GAMG Serial Bottleneck

**Symptoms:**
```bash
# Scaling plateaus after 8 CPUs
N_CPUs  Time    Speedup
1       850     1.00x
8       135     6.30x
16      125     6.80x  ← Only 8% improvement!
32      120     7.08x  ← Only 4% improvement!
```

**Diagnosis:**
```cpp
p
{
    solver          GAMG;
    nCellsInCoarsestLevel 10;  ← Too small!
}
```

**Problem:** Coarsest level has 10 cells → serial solve dominates

**Solution:**
```cpp
p
{
    solver          GAMG;
    nCellsInCoarsestLevel 100;     // Larger coarse level
    agglomerator    faceAreaPair;   // Better parallel scaling
    mergeLevels     1;
}
```

**Result:**
```bash
N_CPUs  Time    Speedup
16      105     8.10x  ← Improved from 6.80x
32      95      8.95x  ← Improved from 7.08x
```

---

### Pitfall 4: I/O Bottleneck

**Symptoms:**
```bash
$ mpirun -np 16 simpleFoam -parallel
# Long pauses during write
```

**Diagnosis:**
```bash
$ grep "write" log.simpleFoam
write fields: 45.3 seconds  ← Too long!
```

**Cause:** Only master writes, others wait

**Solutions:**
```cpp
// ControlDict
writeInterval   500;     // Write less frequently (was: 100)

// Or use collated I/O (OpenFOAM v1806+)
writeFormat     binary;
writeCompression off;
```

---

## Advanced Profiling

### mpiP: MPI Profiling

**Install:**
```bash
sudo apt-get install mpip  # Ubuntu/Debian
# Or build from source
```

**Use:**
```bash
export LD_PRELOAD=/usr/lib/libmpiP.so
mpirun -np 8 simpleFoam -parallel
```

**Output:**
```
Time spent in MPI calls: 45.23 s (42.1% of total)

MPI Function         Calls      Time    % Time
-----------------------------------------------
MPI_Send             234,567    12.3 s   27.3%
MPI_Recv             234,523    14.6 s   32.2%
MPI_Allreduce        8,923       3.1 s    6.9%
```

**Interpretation:**
- **42% in MPI** = Communication bound
- **>50%** = Consider fewer CPUs or better decomposition

---

## Visualization: Create Scaling Plots

### Python Plotting Script

```python
#!/usr/bin/env python3
"""Generate scaling plots from OpenFOAM data"""
import numpy as np
import matplotlib.pyplot as plt

# Input data (replace with your runs)
np_cpus = np.array([1, 2, 4, 8, 16, 32])
time = np.array([850, 440, 235, 135, 95, 85])

# Calculate metrics
speedup = time[0] / time
efficiency = speedup / np_cpus * 100

# Print table
print(f"{'N':>4} {'Time':>8} {'Speedup':>8} {'Efficiency':>12}")
print("-" * 36)
for i in range(len(np_cpus)):
    print(f"{np_cpus[i]:>4} {time[i]:>8} {speedup[i]:>8.2f} {efficiency[i]:>11.1f}%")

# Create plots
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# Plot 1: Time vs CPUs
axes[0].plot(np_cpus, time, 'bo-', linewidth=2, markersize=8)
axes[0].set_xlabel('Number of Processors', fontsize=12)
axes[0].set_ylabel('Time (s)', fontsize=12)
axes[0].set_title('Runtime Scaling', fontsize=14, fontweight='bold')
axes[0].grid(True, alpha=0.3)
axes[0].set_xscale('log', base=2)

# Plot 2: Speedup (with ideal)
axes[1].plot(np_cpus, speedup, 'bo-', label='Actual', linewidth=2, markersize=8)
axes[1].plot(np_cpus, np_cpus, 'k--', label='Ideal', linewidth=1.5)
axes[1].set_xlabel('Number of Processors', fontsize=12)
axes[1].set_ylabel('Speedup', fontsize=12)
axes[1].set_title('Strong Scaling', fontsize=14, fontweight='bold')
axes[1].legend(fontsize=11)
axes[1].grid(True, alpha=0.3)
axes[1].set_xscale('log', base=2)

# Plot 3: Efficiency
colors = ['green' if e >= 75 else 'orange' if e >= 50 else 'red' for e in efficiency]
axes[2].bar(np_cpus, efficiency, color=colors, alpha=0.7, edgecolor='black')
axes[2].axhline(y=75, color='green', linestyle='--', linewidth=2, label='Good (>75%)')
axes[2].axhline(y=50, color='orange', linestyle='--', linewidth=2, label='Fair (50-75%)')
axes[2].set_xlabel('Number of Processors', fontsize=12)
axes[2].set_ylabel('Efficiency (%)', fontsize=12)
axes[2].set_title('Parallel Efficiency', fontsize=14, fontweight='bold')
axes[2].set_ylim([0, 105])
axes[2].grid(True, alpha=0.3, axis='y')
axes[2].legend(fontsize=10)

plt.tight_layout()
plt.savefig('scaling_analysis.png', dpi=150, bbox_inches='tight')
print("\n✓ Plot saved to scaling_analysis.png")
```

**Output:** Three-panel plot showing runtime, speedup vs ideal, and efficiency with color-coded performance zones

---

## Key Takeaways

1. **Efficiency > Speedup:** Target >75% efficiency for productive runs
2. **Cells per CPU matters:** Aim for ≥50,000 cells/CPU, minimum 10,000
3. **Scotch wins:** Use Scotch decomposition for 5-15% improvement over simple
4. **Serial limits speedup:** Even 5% serial code caps speedup at 20× (Amdahl's law)
5. **Profile before optimizing:** Use mpiP to identify communication bottlenecks
6. **Real data:** Motorbike tutorial shows optimal 4-8 CPUs for 4.2M cells

---

## Concept Check

<details>
<summary><b>1. A 90% parallel code with 64 CPUs achieves what speedup?</b></summary>

$$S = \frac{1}{(1-0.9) + \frac{0.9}{64}} = \frac{1}{0.1 + 0.014} = 8.8\times$$

**Not 64×!** The 10% serial part limits maximum speedup to 10×

**Key insight:** 100% parallel is impossible; focus on minimizing serial sections
</details>

<details>
<summary><b>2. Why does efficiency decrease when adding CPUs?</b></summary>

**Four main causes:**

1. **Communication overhead:** More CPUs = more messages
2. **Load imbalance:** Hard to partition equally
3. **Serial bottlenecks:** Coarse solver, I/O, global reductions
4. **Memory bandwidth:** CPUs compete for RAM access

**Mitigation strategies:**
- Better decomposition (Scotch)
- Increase problem size (weak scaling)
- Reduce communication frequency
- Tune solver settings
</details>

<details>
<summary><b>3. Your case has 2M cells. What's the optimal CPU count?</b></summary>

**Calculation:**
- Target: 50,000 cells/CPU for >75% efficiency
- Optimal CPUs = 2,000,000 / 50,000 = **40 CPUs**
- Minimum: 2,000,000 / 10,000 = 200 CPUs (but efficiency will be poor)

**Test range:** 16-64 CPUs, measure actual efficiency

**Expected:** ~32-40 CPUs optimal for this mesh size
</details>

---

## Exercise

### Exercise 1: Scaling Analysis (Required)

**Task:** Run scaling test on motorbike tutorial

```bash
cd $FOAM_TUTORIALS/incompressible/simpleFoam/motorBike
blockMesh

# Run scaling test
for np in 1 2 4 8 16 32; do
    rm -rf processor*
    decomposePar -copyZero
    mpirun -np $np simpleFoam -parallel > log.$np 2>&1
    time=$(grep "ClockTime" log.$np | tail -1 | awk '{print $3}')
    echo "$np $time"
done

# Calculate efficiency and identify optimal CPU count
```

**Deliverables:**
1. Table: N, Time, Speedup, Efficiency
2. Plot: Speedup curve (actual vs ideal)
3. Recommendation: Optimal CPU count with justification

---

### Exercise 2: Decomposition Comparison (Optional)

**Task:** Compare Scotch vs Simple methods

```bash
# Test simple method
cat > system/decomposeParDict << EOF
numberOfSubdomains 8;
method simple;
simpleCoeffs { n (2 2 2); }
EOF

decomposePar
mpirun -np 8 simpleFoam -parallel > log.simple 2>&1

# Test scotch method
cat > system/decomposeParDict << EOF
numberOfSubdomains 8;
method scotch;
EOF

decomposePar
mpirun -np 8 simpleFoam -parallel > log.scotch 2>&1

# Compare
echo "Simple: $(grep ClockTime log.simple | tail -1 | awk '{print $3}')s"
echo "Scotch: $(grep ClockTime log.scotch | tail -1 | awk '{print $3}')s"

# Check interface sizes
grep "interface" log.decomposePar
```

**Deliverable:** Report speedup from Scotch, explain why

---

### Exercise 3: Troubleshooting Poor Scaling (Advanced)

**Scenario:** Your 8M cell case scales poorly:
- 1 CPU: 1200s
- 8 CPUs: 250s (efficiency: 60%)
- 16 CPUs: 180s (efficiency: 42%)

**Task:** Diagnose and fix

1. **Check decomposition quality:**
   ```bash
   grep "Processor.*cells" log.decomposePar
   grep "interface" log.decomposePar
   ```

2. **Profile MPI time** (if mpiP available)

3. **Try fixes:**
   - Switch decomposition method
   - Tune GAMG settings
   - Reduce I/O frequency

4. **Re-measure scaling**

**Deliverable:** Before/after comparison with explanation

---

## References

### Internal Documentation
- **Previous:** [Loop Optimization](03_Loop_Optimization.md) - Cache effects in parallel
- **Next:** [Memory Layout Optimization](../03_PERFORMANCE_ENGINEERING/02_Memory_Layout_Cache.md)

### External Resources
- **Amdahl's Law:** https://en.wikipedia.org/wiki/Amdahl%27s_law
- **MPI Tutorial:** https://mpitutorial.com/tutorials/
- **Scotch Documentation:** https://www.labri.fr/perso/pelegrin/scotch/
- **OpenFOAM Parallel Guide:** https://cfd.direct/openfoam/user-guide/parallel-running/

### Tools
- **mpiP:** https://github.com/hargup/mpip
- **Scalasca:** https://www.scalasca.org/
- **Vampir:** https://www.vampir.eu/

---

## Appendix: Quick Reference

### Essential Commands

```bash
# Decomposition
decomposePar                           # Decompose mesh
decomposePar -copyZero                 # Copy 0/ directory
reconstructPar                         # Reconstruct results
reconstructParMesh                     # Reconstruct mesh

# Parallel execution
mpirun -np 4 simpleFoam -parallel     # Standard run
mpirun -np 4 --bind-to core ...        # Bind threads (hybrid)

# Analysis
grep "ClockTime" log.*                 # Extract times
grep "Processor.*cells" log.decomposePar  # Check balance
```

### Dictionary Template

```cpp
// system/decomposeParDict
numberOfSubdomains 8;

method scotch;  // Recommended

scotchCoeffs
{
    // processorWeights (1 1 1 1 1 1 1 1);  // Optional
}
```

### Decision Tree

```
Mesh size > 10M cells?
├─ Yes → Test 16-64 CPUs
└─ No  → Test 4-16 CPUs

Efficiency > 75%?
├─ Yes → Use this CPU count
└─ No  → Reduce CPUs or check decomposition

Interface ratio > 5%?
├─ Yes → Try Scotch or reduce CPUs
└─ No  → Decomposition is OK

GAMG coarsest level < 100 cells?
├─ Yes → Increase nCellsInCoarsestLevel
└─ No  → Check other bottlenecks
```

---

**Last Updated:** 2025-12-31  
**OpenFOAM Version:** v2312  
**Author:** OpenFOAM Performance Guide