# Phase 4: Parallelization

## Learning Objectives

By the end of this phase, you will be able to:
- Configure and execute domain decomposition for parallel CFD simulations
- Run OpenFOAM solvers using MPI on multiple processors
- Analyze parallel performance through strong scaling studies
- Diagnose and resolve common parallelization issues (load imbalance, communication overhead)
- Choose appropriate decomposition methods (Scotch vs. Simple) based on mesh characteristics

---

## WHAT: Why Parallelize?

OpenFOAM simulations can take hours or days on a single CPU. **Parallelization** divides your computational domain across multiple processors, allowing simultaneous computation and dramatically reducing wall-clock time. However, parallelization introduces **communication overhead** between processors and requires careful **load balancing** to achieve efficiency.

---

## WHY: Performance Trade-offs

**Benefits:**
- **Speedup:** Near-linear reduction in computation time (ideal case: 4 CPUs = 4× faster)
- **Larger meshes:** Enables simulation of problems too large for single-processor memory
- **Resource utilization:** Leverages multi-core hardware and HPC clusters

**Costs:**
- **Communication overhead:** Processors must exchange boundary data at each timestep
- **Decomposition time:** Pre-processing step (Scotch: seconds, Simple: milliseconds)
- **Diminishing returns:** Efficiency drops as CPU count increases due to Amdahl's Law

**Key Metrics:**
- **Speedup** = T₁ / Tₙ (time on 1 CPU ÷ time on N CPUs)
- **Efficiency** = Speedup / N × 100% (ideal: 100%, practical: 70-85%)
- **Strong scaling:** Fixed problem size, increasing CPUs (our focus here)

---

## HOW: Parallelization Workflow

The parallelization process follows five steps:
1. **Configure decomposition** via `decomposeParDict`
2. **Decompose mesh** into processor subdomains
3. **Run solver** in parallel with MPI
4. **Reconstruct results** into single domain for post-processing
5. **Analyze performance** through scaling studies

---

## Implementation

### Step 1: Create Decomposition Configuration

Create `system/decomposeParDict` to specify how the domain will be divided:

```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      decomposeParDict;
}

numberOfSubdomains 4;

method          scotch;     // Automatic load balancing (recommended)

// Alternative: simple geometric split
// method          simple;
// simpleCoeffs
// {
//     n               (2 2 1);    // 2×2×1 = 4 processors
//     delta           0.001;      // Tolerance for geometric matching
// }
```

**Key Parameters:**
- `numberOfSubdomains`: Number of processor subdomains (typically = CPU count)
- `method`: Decomposition algorithm (see comparison below)

<details>
<summary><b>🔧 Troubleshooting: Choosing Between Scotch and Simple</b></summary>

**Scotch (Recommended for most cases):**
- Graph-based partitioning optimizing load balance and interface size
- Works with any mesh type (structured/unstructured/hybrid)
- Decomposition time: 1-5 seconds (one-time cost)
- Best for: Complex geometries, unstructured meshes, production runs

**Simple:**
- Geometric split along coordinate axes
- Extremely fast (< 0.1 seconds)
- Best for: Structured hex meshes, simple geometries, testing/debugging

**Rule of thumb:** Start with Scotch. Switch to Simple only if decomposition time becomes problematic (rare).
</details>

---

### Step 2: Decompose the Mesh

```bash
cd tutorials/turbulent_channel

# Decompose into processor subdomains
decomposePar

# Expected output:
# --> FOAM Warning : 
#     From const rectilinearMesh& ...
#     Reading "/home/user/tutorials/turbulent_channel/processor0/.../polyMesh/points"
# ...
# Processor 0: number of cells = 62500
# Processor 1: number of cells = 62500
# Processor 2: number of cells = 62500
# Processor 3: number of cells = 62500
```

**Verification checkpoints:**
```bash
# Check load balance (cells should be roughly equal)
grep "cells" log.decomposePar

# Inspect processor directories
ls -la processor*/ 
# Should show: 0/ 1/ 2/ 3/ with complete polyMesh/ in each

# Check interface size (fewer faces = less communication)
grep "faces.*processor" log.decomposePar
# Example: Processor 0 boundary 1: 1250 faces (to processor 1)
```

<details>
<summary><b>🔧 Troubleshooting: Decomposition Issues</b></summary>

**Problem: Unequal cell distribution**
```bash
# Symptom: Wide variation in cell counts
Processor 0: 80000 cells  # Too many!
Processor 1: 60000 cells
Processor 2: 60000 cells  
Processor 3: 50000 cells

# Solution: Switch from simple to scotch
# Edit system/decomposeParDict:
method  scotch;  # Was: simple
```

**Problem: Decomposition fails with "cannot find points file"**
```bash
# Symptom: Error reading mesh points
# Solution: Ensure mesh exists in constant/polyMesh
ls constant/polyMesh/points
# If missing, re-run mesh generation (e.g., blockMesh)
```
</details>

---

### Step 3: Run Parallel Simulation

```bash
# Execute solver on 4 processors using MPI
mpirun -np 4 myHeatFoam -parallel > log.parallel 2>&1

# Monitor progress in real-time
tail -f log.parallel

# Expected output pattern:
# Time = 0.1
# Processor 0: Solving for T, Initial residual = 1.00000e+00, Final residual = 9.87654e-02
# Processor 1: Solving for T, Initial residual = 1.00000e+00, Final residual = 9.87654e-02
# ...
# Time = 0.2
# ...
# End
```

**Performance monitoring:**
```bash
# Track individual processor performance
mpirun -np 4 myHeatFoam -parallel 2>&1 | tee log.parallel

# Check for communication overhead
grep "communication" log.parallel

# Verify all processors finish at similar times (load balance)
grep "ClockTime" log.parallel
```

<details>
<summary><b>🔧 Troubleshooting: MPI Runtime Errors</b></summary>

**Error: "MPI_Init failed"**
```bash
# Symptom:
mpirun -np 4 myHeatFoam -parallel
--------------------------------------------------------------------------
MPI_ABORT was invoked on rank 3 in communicator MPI_COMM_WORLD
with errorcode -1.

# Diagnosis: MPI misconfiguration or incompatible libraries
# Solutions:
# 1. Check MPI installation
which mpirun
mpirun --version

# 2. Test MPI stack
mpirun -np 4 hostname
# Should print your machine name 4 times

# 3. Verify OpenFOAM MPI configuration
echo $WM_MPLIB
# Should show: SYSTEMOPENMPI, FJMPI, or similar

# 4. Re-source OpenFOAM environment
source $WM_PROJECT_DIR/etc/bashrc
```

**Error: "Load imbalance" (slow processors)**
```bash
# Symptom: Wide variation in processor times
Processor 0: Solving time = 50 s
Processor 1: Solving time = 85 s  ← Much slower! (waiting)
Processor 2: Solving time = 52 s
Processor 3: Solving time = 48 s

# Impact: Overall runtime dominated by slowest processor

# Solution: Improve decomposition balance
# 1. Check cell distribution
grep "cells" log.decomposePar

# 2. Switch to scotch (if using simple)
method scotch;

# 3. Increase processor count for better granularity
numberOfSubdomains 8;  # More, smaller subdomains
```
</details>

---

### Step 4: Reconstruct Results

After parallel execution, combine processor directories into single domain for visualization:

```bash
# Merge all processor subdomains
reconstructPar

# Expected output:
# --> FOAM Warning :
#     From reconstructPar::... 
#     Reconstructing mesh for time 0
# Reconstructing mesh for time 0.1
# Reconstructing mesh for time 0.2
# ...
# End.

# Verify reconstructed fields
ls 0.1/ 
# Should show: T  UniformMeshPoints ...

# Visualize in ParaView
paraFoam -builtin
```

**Note:** If you only need specific time steps, use:
```bash
reconstructPar -latestTime     # Last timestep only
reconstructPar -time '0:0.5'   # Range of times
```

---

## Validation: Scaling Analysis

### Run Scaling Study

Test performance across different processor counts to quantify efficiency:

```bash
#!/bin/bash
# scaling_test.sh

CASE="turbulent_channel"

for NP in 1 2 4 8; do
    echo "Running with $NP processors..."
    
    # Clean previous processor directories
    rm -rf processor*
    
    # Update decomposition for this CPU count
    sed -i "s/numberOfSubdomains.*/numberOfSubdomains $NP;/" system/decomposeParDict
    
    # Decompose
    decomposePar > log.decompose.$NP 2>&1
    
    # Run parallel simulation
    mpirun -np $NP myHeatFoam -parallel > log.run.$NP 2>&1
    
    # Extract execution time
    TIME=$(grep "ClockTime" log.run.$NP | tail -1 | awk '{print $3}')
    echo "$NP processors: $TIME seconds"
done
```

**Expected results table (example):**
```
NP    Time (s)    Speedup    Efficiency
1     100         1.00x      100%
2     52          1.92x      96%
4     28          3.57x      89%
8     18          5.56x      69%
```

<details>
<summary><b>📊 Visualization Code (Python Scaling Analysis)</b></summary>

```python
import matplotlib.pyplot as plt
import numpy as np

# Data from scaling test (replace with your measurements)
np = [1, 2, 4, 8]
time = [100, 52, 28, 18]  # seconds

# Calculate performance metrics
speedup = np.array(time[0]) / np.array(time)
efficiency = speedup / np.array(np) * 100

# Print comparison table
print("NP\tTime\tSpeedup\tEfficiency")
for i in range(len(np)):
    print(f"{np[i]}\t{time[i]}\t{speedup[i]:.2f}\t{efficiency[i]:.1f}%")

# Create side-by-side plots
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Speedup plot
axes[0].plot(np, speedup, 'bo-', label='Actual', linewidth=2)
axes[0].plot(np, np, 'k--', label='Ideal (Linear)', linewidth=1.5)
axes[0].set_xlabel('Number of Processors', fontsize=12)
axes[0].set_ylabel('Speedup', fontsize=12)
axes[0].legend(fontsize=11)
axes[0].set_title('Strong Scaling: Speedup', fontsize=13, fontweight='bold')
axes[0].grid(True, alpha=0.3)

# Efficiency plot
axes[1].bar(np, efficiency, color='steelblue', alpha=0.7, edgecolor='black')
axes[1].set_xlabel('Number of Processors', fontsize=12)
axes[1].set_ylabel('Efficiency (%)', fontsize=12)
axes[1].set_title('Parallel Efficiency', fontsize=13, fontweight='bold')
axes[1].set_ylim([0, 105])
axes[1].axhline(y=70, color='r', linestyle='--', linewidth=1, label='70% threshold')
axes[1].legend(fontsize=10)
axes[1].grid(True, axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('scaling_analysis.png', dpi=150)
print("Plot saved to scaling_analysis.png")
```

**Interpretation guidelines:**
- Speedup > 3.5× on 4 CPUs = good parallel efficiency
- Efficiency > 70% = acceptable for most applications
- Efficiency < 50% = communication overhead dominates (consider larger mesh)
</details>

<details>
<summary><b>📋 Scotch vs Simple: Detailed Comparison</b></summary>

| Aspect | **Scotch** (Recommended) | **Simple** |
|:---|:---|:---|
| **Algorithm** | Graph-based partitioning | Geometric coordinate split |
| **Load balancing** | Automatic, optimal optimization | Manual, prone to imbalance |
| **Interface minimization** | Built-in objective function | Not considered |
| **Decomposition speed** | Slower (1-5 seconds) | Very fast (< 0.1 seconds) |
| **Mesh compatibility** | Any (structured/unstructured/hybrid) | Structured grids only |
| **Reproducibility** | May vary slightly between runs | Deterministic, always identical |

**Real-world benchmark: 100k cell mesh**

**Method: simple (2 2 1)**
```
Processor 0: 25,000 cells
Processor 1: 25,000 cells
Processor 2: 25,000 cells
Processor 3: 25,000 cells
Interface faces: 5,400 total

Decomposition time: 0.05 s
Simulation time: 120 s
Total: 120.05 s
```

**Method: scotch**
```
Processor 0: 25,001 cells
Processor 1: 25,002 cells
Processor 2: 24,997 cells
Processor 3: 25,000 cells
Interface faces: 3,800 total  ← 30% less communication!

Decomposition time: 2.5 s
Simulation time: 95 s
Total: 97.5 s  ← 23% faster overall!
```

**Conclusion:** Scotch adds small decomposition overhead but saves significant simulation time through reduced communication. Net benefit increases with mesh size and iteration count.
</details>

---

## Concept Check

<details>
<summary><b>1. Why does scotch generally outperform simple decomposition?</b></summary>

**simple (geometric split):**
- Divides domain along coordinate axes (x × y × z)
- Ignores actual mesh topology and cell distribution
- May cut through complex regions, creating imbalanced loads
- Large processor interfaces if cuts align poorly with mesh structure

**scotch (graph partitioning):**
- Models mesh as graph (cells = nodes, faces = edges)
- Simultaneously optimizes: (1) equal cell count per processor, (2) minimized interface faces
- Reduces communication overhead → faster simulation
- Adapts to complex geometries and local refinements

**When to use simple:**
- Structured hex meshes with uniform spacing
- Reproducible decomposition required (e.g., regression testing)
- Debugging parallel code (deterministic behavior)
</details>

<details>
<summary><b>2. Why does parallel efficiency decrease as CPU count increases?</b></summary>

**Primary causes:**

1. **Communication overhead growth**
   - Each processor exchanges boundary data with neighbors every timestep
   - Number of communications increases with processor count
   - Surface-to-volume ratio: More processors = more interface, less interior

2. **Serial bottlenecks**
   - Linear algebra solvers (e.g., coarse grid correction in AMG) have serial sections
   - Amdahl's Law: Speedup limited by non-parallelizable code fraction
   - If 10% is serial, maximum speedup = 10× regardless of CPU count

3. **Load imbalance challenges**
   - Perfect balance becomes harder with more subdomains
   - Heterogeneous hardware (CPU frequency variations, memory bandwidth)
   - Some processors wait (idle) while others finish

**When efficiency drops below 50-70%:**
- Adding more CPUs wastes resources (diminishing returns)
- **Solution:** Use larger mesh size (weak scaling) instead of more CPUs
- **Rule of thumb:** Maintain > 100k cells per processor for CFD
</details>

<details>
<summary><b>3. What is the difference between strong scaling and weak scaling?</b></summary>

**Strong scaling (this exercise):**
- **Fixed problem size**, varying processor count
- Goal: Minimize wall-clock time for given simulation
- Question: "How much faster can I solve THIS problem?"
- Typical efficiency: 70-90% at 4 CPUs, 50-70% at 8 CPUs

**Weak scaling:**
- **Fixed problem size per processor**, varying both problem size and CPU count
- Goal: Solve larger problems within same time
- Question: "How large a problem can I solve in same time?"
- Typical efficiency: 80-95% even at high CPU counts

**Example:**
- Strong scaling: 100k cells on 1, 2, 4, 8 CPUs (time should decrease)
- Weak scaling: 100k cells on 1 CPU, 200k on 2 CPUs, 400k on 4 CPUs (time should stay constant)

**Practical implication:** Strong scaling hits communication limits; weak scaling tests solver's ability to handle large-scale problems efficiently.
</details>

---

## Key Takeaways

- **Decomposition method matters:** Scotch optimizes both load balance and communication, typically outperforming simple geometric split despite higher pre-processing cost
- **Efficiency declines with CPU count:** Communication overhead and serial portions limit scaling (Amdahl's Law); efficiency > 70% is good, < 50% indicates diminishing returns
- **Balance is critical:** Unequal cell distribution causes fast processors to wait for slow ones, defeating parallelization purpose
- **Scaling studies reveal bottlenecks:** Measure speedup/efficiency across multiple CPU counts to identify optimal configuration for your hardware and problem size
- **Reconstruction for visualization only:** Use `-parallel` flag for computation, then `reconstructPar` before post-processing in ParaView

---

## Exercises

1. **Compare decomposition methods:** Run the same case with both `scotch` and `simple` methods. Quantify the difference in (a) decomposition time, (b) simulation time, (c) interface size
2. **Large mesh scaling:** Increase mesh size to 1M cells and repeat scaling study. How does efficiency change compared to 100k cell case? (Demonstrates weak scaling benefits)
3. **Communication profiling:** Install `mpiP` (MPI Profiler) and measure communication time fraction. What percentage of total runtime is spent in MPI communication for 4 CPUs vs. 8 CPUs?
4. **Load imbalance analysis:** Intentionally create an imbalanced mesh (e.g., refine one region) and compare scotch vs. simple performance

---

## Deliverables

- [ ] `system/decomposeParDict` configured for both scotch and simple methods
- [ ] Successful parallel run producing identical results to serial (verify: `diff serial/0.1/T reconstructed/0.1/T`)
- [ ] Scaling table with times for 1, 2, 4, 8 CPUs
- [ ] Speedup and efficiency plots with interpretation
- [ ] Processor boundary face counts from `log.decomposePar`

---

## Next Phase

When Phase 4 is complete and your parallel scaling shows > 70% efficiency, proceed to [Phase 5: Optimization](05_Phase5_Optimization.md) to reduce solver iterations and memory usage through advanced techniques.