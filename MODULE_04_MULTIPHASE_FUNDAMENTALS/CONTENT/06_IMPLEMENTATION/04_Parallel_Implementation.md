# Parallel Implementation in Multiphase Flow

## Learning Objectives

### What You Will Learn
- Architecture of parallel decomposition strategies for multiphase flows
- Domain decomposition methods specific to dispersed and interface-tracking simulations
- OpenFOAM's parallel implementation infrastructure (scotch, ptscotch, metis)
- Performance optimization techniques for multiphase calculations
- Load balancing challenges and solutions for phase-segregated flows
- Practical HPC job configuration and execution

### Why It Matters
Parallel implementation is **critical** for multiphase CFD because:
- **Resolving interfaces** (VOF) or **tracking dispersed phases** (Euler-Euler) demands extremely fine meshes
- Multiphase flows involve **additional transport equations** and **interphase coupling** that increase computational cost by 2-5x compared to single-phase
- **Phase segregation** creates natural load imbalance - regions with dispersed bubbles/droplets require more computation than single-phase regions
- Industrial multiphase simulations routinely require **millions of cells** and **hundreds of cores** to achieve practical runtimes
- Understanding parallel implementation enables you to **utilize HPC resources effectively** and avoid common pitfalls that waste computation time

### How You Will Apply This
- Configure and execute parallel multiphase simulations on HPC clusters
- Diagnose and resolve load imbalance issues specific to multiphase flows
- Choose appropriate decomposition methods based on your multiphase regime
- Optimize parallel performance through proper mesh distribution
- Interpret parallel performance metrics and scaling behavior
- Write effective SLURM job scripts for multiphase simulations

---

## 1. Fundamental Concepts

### 1.1 Domain Decomposition Strategy

Domain decomposition divides the computational mesh among processor cores. Each core:
- Solves equations on its **subdomain** (local cells)
- Exchanges **boundary data** with neighboring processors (halo/ghost cells)
- Participates in **global parallel communication** (reductions, synchronizations)

**Key decomposition metrics:**
```
Domain balance (ideal = 1.0):
α = max(n_cells_i) / mean(n_cells_i)

Surface-to-volume ratio (lower = better):
β = total_interface_cells / total_internal_cells

Parallel efficiency:
η = T_serial / (N_proc × T_parallel)
```

### 1.2 Parallel Implementation Architecture

OpenFOAM's parallel implementation follows the **MPI standard**:

```cpp
// Pstream library handles MPI communication
#include "Pstream.H"

// Example: Parallel reduction for global sum
scalar globalSum = gSum(localField);

// Example: Parallel max reduction
label globalMax = gMax(localValues);

// Example: Synchronize boundary data
volScalarField::Boundary& bf = field.boundaryField();
forAll(bf, patchi)
{
    fvPatchScalarField& pf = bf[patchi];
    pf.initEvaluate();   // Start communication
    pf.evaluate();       // Complete communication
}
```

**Core parallel classes:**
- `Pstream`: MPI communicator wrapper
- `UPstream`: Processor stream management
- `OPstream`: Output streams (send)
- `IPstream`: Input streams (receive)
- `globalIndex`: Global-to-local indexing

### 1.3 Why Multiphase Parallelization is Different

Multiphase flows introduce **unique parallel challenges**:

| Challenge | Single-Phase | Multiphase | Impact |
|-----------|--------------|------------|--------|
| **Computational load** | Uniform per cell | Varies with phase presence | 2-5x more equations |
| **Interface resolution** | N/A | Intensive in interface regions | Localized hotspots |
| **Phase segregation** | N/A | Clustered particles/bubbles | Severe load imbalance |
| **Interphase coupling** | N/A | Requires communication | More reductions |
| **Free surface tracking** | N/A | Geometric reconstruction (VOF) | Additional synchronization |

---

## 2. Decomposition Methods

### 2.1 Decomposition Utilities

OpenFOAM provides several decomposition methods:

```bash
# Manual decomposition
decomposePar

# Automatic reconstruction
reconstructPar

# Check decomposition quality
checkDecomposition
```

**Available methods** (specified in `system/decomposeParDict`):
- `scotch`: Graph-based partitioning (default, recommended)
- `ptscotch`: Parallel scotch (for large meshes)
- `metis`: Alternative graph partitioner
- `simple`: Geometric (coordinate-based)
- `hierarchical`: Multi-level geometric
- `manual`: User-specified cell distribution

### 2.2 Recommended Configuration for Multiphase

**Example `decomposeParDict` for Euler-Euler:**
```cpp
// File: system/decomposeParDict
method          scotch;

scotchCoeffs
{
    // Write decomposition for visualization
    processorWeights     ( 1.0 1.0 1.0 1.0 );
    
    // Optional: Minimize edge cuts
    // strategy "b";
}

// Number of subdomains (can override with -np flag)
numberOfSubdomains  16;
```

**VOF-specific configuration with refinement regions:**
```cpp
// For VOF with local refinement at interface
method          scotch;

scotchCoeffs
{
    // Global decomposition first
    globalFactor     1.0;
}

// Weight cells by refinement level
// (requires custom weights field)
decompositionWeights
{
    type            cellSource;
    source          cellZone;
    cellZone        refinedInterfaceZone;
    weight          2.0;  // Higher weight = more processors
}
```

### 2.3 Special Cases

#### **2.3.1 Cylindrical/Axisymmetric Geometries**
```cpp
// For pipe flows with bubbles
method          hierarchical;

hierarchicalCoeffs
{
    numberOfSubdomains  64;
    
    // Decompose in axial direction first
    // (direction of bubble flow)
    n                   (64 1 1);
    
    // Order of decomposition axes
    order               xyz;
    
    // Delta for processor boundaries
    delta               0.001;
}
```

#### **2.3.2 Multi-Region Meshes**
```cpp
// For conjugate heat transfer with multiphase
method          scotch;

regions
{
    fluid
    {
        method          scotch;
        numberOfSubdomains  32;
    }
    
    solid
    {
        method          scotch;
        numberOfSubdomains  8;
    }
}
```

---

## 3. Parallel Execution Workflow

### 3.1 Standard Decomposition-Solve-Reconstruct Cycle

**Step 1: Decompose the case**
```bash
# Basic decomposition
decomposePar

# Decompose with specific number of processors
decomposePar -np 32

# Decompose with specific dictionary
decomposePar -dict system/decomposeParDict
```

**Step 2: Run in parallel**
```bash
# OpenMPI syntax
mpirun -np 32 interFoam -parallel

# Intel MPI syntax
mpirun -np 32 interFoam -parallel

# SLURM allocation (see Section 5)
srun interFoam -parallel
```

**Step 3: Reconstruct (optional)**
```bash
# Reconstruct all time directories
reconstructPar

# Reconstruct specific times
reconstructPar -latestTime
reconstructPar -time '(0.5 1.0)'
```

### 3.2 Distributed Running

For large cases exceeding memory per node:

```bash
# Distribute one processor per node first
mpirun -np 16 -pernode interFoam -parallel

# Then continue with local parallelism
mpirun -np 512 interFoam -parallel
```

---

## 4. Performance Optimization

### 4.1 Load Balancing for Multiphase Flows

**Problem**: Phase segregation creates load imbalance

**Example**: Bubbly flow in vertical pipe
- Most bubbles rise in **core region** (center of pipe)
- Cells in core solve **more equations** (bubble tracking, drag, lift)
- Edge processors (near wall) have **lighter load**

**Solution 1: Cell-based weights**
```cpp
// Create cell weights file before decomposition
// File: constant/cellWeights
dimensions      [0 0 0 0 0 0 0];
internalField   uniform 1.0;  // Base weight

boundaryField
{
    ".+"
    {
        type            calculated;
        value           uniform 1.0;
    }
}
```

Then use weighted decomposition:
```bash
# Apply weights during decomposition
decomposePar -dict system/decomposeParDict -fields cellWeights
```

**Solution 2: Zone-based decomposition**
```cpp
// Create cellZones for different phase regions
// File: constant/polyMesh/cellZones

bubblyCoreRegion
{
    type cellZone;
    cellLabels List<label>
    (
        1000 1001 1002 ...  // Core cells
    );
}

singlePhaseOuterRegion
{
    type cellZone;
    cellLabels List<label>
    (
        5000 5001 5002 ...  // Outer cells
    );
}
```

Configure decomposition to balance:
```cpp
// File: system/decomposeParDict
method          scotch;

scotchCoeffs
{
    // Assign more processors to bubbly core
    processorWeights
    (
        1.0 1.0 2.0 2.0 2.0  // Higher weight for core processors
    );
}
```

### 4.2 Communication Minimization

**Reduce parallel communication overhead:**

1. **Minimize processor boundaries**:
   - Use `scotch` instead of `simple`
   - Target surface-to-volume ratio < 0.1

2. **Reduce global reductions**:
   ```cpp
   // BAD: Reduces every iteration
   for (int iter=0; iter<maxIter; iter++)
   {
       scalar residual = gSum(mag(field - field.oldTime()));
   }
   
   // GOOD: Reduce only when needed
   scalar residual = 0;
   for (int iter=0; iter<maxIter; iter++)
   {
       residual += sumLocal(mag(field - field.oldTime()));
   }
   residual = returnReduce(residual, sumOp<scalar>());
   ```

3. **Batch interphase coupling**:
   ```cpp
   // Solve all phase equations before coupling
   forAll(phases, phasei)
   {
       phases[phasei].solve();
   }
   
   // Single coupling call
   phaseSystem.solveInterphase();
   ```

### 4.3 Mesh Quality for Parallel Scaling

**Guidelines:**
- **Minimum cells per processor**: 50,000-100,000
- **Ideal**: 200,000-500,000 cells/processor

```cpp
// Calculate optimal processor count
n_proc_optimal = n_cells / 250000;

// Example: 10M cell mesh
n_proc_optimal = 10,000,000 / 250,000 = 40 processors
```

**Avoid over-decomposition:**
- Communication overhead dominates when cells/processor < 50k
- Multiphase simulations require **more cells/processor** than single-phase

---

## 5. HPC Implementation

### 5.1 SLURM Job Script for Multiphase

**Complete SLURM script for Euler-Euler simulation:**
```bash
#!/bin/bash
#SBATCH --job-name=multiphase_sim
#SBATCH --partition=compute
#SBATCH --nodes=4                    # 4 nodes
#SBATCH --ntasks-per-node=32         # 32 cores per node
#SBATCH --cpus-per-task=1            # 1 CPU per task (no hyperthreading)
#SBATCH --mem=120GB                  # Memory per node
#SBATCH --time=24:00:00              # 24 hour walltime
#SBATCH --output=logs/%x_%j.out      # Output log
#SBATCH --error=logs/%x_%j.err       # Error log

# --- Environment Setup ---
module purge
module load openmpi/4.1.1
module load openfoam/9

# Source OpenFOAM environment
source $WM_PROJECT_DIR/etc/bashrc

# --- Case Setup ---
CASE_DIR=$SLURM_SUBMIT_DIR
cd $CASE_DIR

# Create log directory
mkdir -p logs

# --- Decomposition ---
echo "=== Decomposing case ==="
decomposePar -np 128 | tee logs/decompose.log

# --- Simulation ---
echo "=== Starting simulation ==="
mpirun -np 128 twoPhaseEulerFoam -parallel \
    > logs/solver_${SLURM_JOB_ID}.log 2>&1

# --- Post-Processing (optional) ---
echo "=== Reconstructing results ==="
reconstructPar -latestTime | tee logs/reconstruct.log

# --- Cleanup (optional) ---
# Remove processor directories to save space
# rm -rf processor*

echo "=== Job completed ==="
```

### 5.2 Advanced SLURM Configuration

**Exclusive node allocation (recommended for large runs):**
```bash
#SBATCH --exclusive
#SBATCH --nodes=8
```

**Hyperthreading configuration:**
```bash
#SBATCH --ntasks-per-node=32
#SBATCH --cpus-per-task=2           # Enable hyperthreading
export OMP_NUM_THREADS=2
```

**Memory-optimized configuration:**
```bash
#SBATCH --mem=0                     # Use all memory on node
#SBATCH --mem-per-cpu=4000          # 4GB per core
```

**Array jobs for parameter studies:**
```bash
#SBATCH --array=0-9%2               # 10 jobs, 2 concurrent
#SBATCH --output=logs/param_%A_%a.out

# Pass array ID to case
CASE_BASE="case_${SLURM_ARRAY_TASK_ID}"
cd $CASE_BASE
```

### 5.3 Monitoring Parallel Performance

**During simulation:**
```bash
# Monitor log file in real-time
tail -f logs/solver_123456.log | grep -E "Courant|PIMPLE|time"

# Check processor usage
squeue -u $USER

# Monitor node performance
```

**Performance analysis:**
```bash
# Extract timing information
grep "ExecutionTime" logs/solver_*.log

# Calculate parallel speedup
# Compare T_serial / T_parallel

# Analyze load balance
# Examine "Pstream::maxProc..." in log
```

### 5.4 Checkpointing and Restart

**Manual checkpoint script:**
```bash
#!/bin/bash
# checkpoint.sh

INTERVAL=3600  # Checkpoint every hour

while true; do
    sleep $INTERVAL
    
    # Create checkpoint
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    CHECKPOINT_DIR="checkpoint_${TIMESTAMP}"
    
    mkdir -p $CHECKPOINT_DIR
    cp -r processor* $CHECKPOINT_DIR/
    
    # Keep last 3 checkpoints only
    ls -td checkpoint_* | tail -n +4 | xargs rm -rf
    
    echo "Checkpoint created: $CHECKPOINT_DIR"
done
```

**Automatic restart in SLURM:**
```bash
#!/bin/bash
#SBATCH --time=04:00:00
#SBATCH --requeue                   # Auto-requeue on timeout

# Check for restart file
LATEST_TIME=$(foamListTimes | tail -1)

if [ -n "$LATEST_TIME" ] && [ "$LATEST_TIME" != "0" ]; then
    echo "Restarting from time: $LATEST_TIME"
    controlDict=$(sed 's/startFrom/latestTime/startFrom/latestTime/' \
        system/controlDict)
    echo "$controlDict" > system/controlDict.tmp
    mv system/controlDict.tmp system/controlDict
fi

mpirun -np 128 twoPhaseEulerFoam -parallel
```

---

## 6. Common Parallel Pitfalls in Multiphase Flows

### 6.1 Load Imbalance Issues

**Symptom**: Poor parallel scaling despite good decomposition

**Diagnostic**:
```bash
# Check processor timing distribution
grep "Pstream::maxProc" solver.log

# Calculate imbalance factor
# (max_time - avg_time) / avg_time
```

**Multiphase-specific causes**:

| Issue | Description | Solution |
|-------|-------------|----------|
| **Phase segregation** | Dispersed phase concentrates in one region | Use weighted decomposition (Section 4.1) |
| **Interface localization** | VOF interface creates computational hotspots | Refine uniformly or use adaptive decomposition |
| **Bubble/droplet clustering** | Local high void fraction increases load | Pre-decompose based on expected flow pattern |

### 6.2 Decomposition Quality Issues

**Problem**: Processor boundaries cut through critical features

**Examples:**
1. **VOF interface cutting**:
   - Interface reconstruction fails at processor boundaries
   - Causes artificial breakup/coalescence

2. **Bubble cluster cutting**:
   - Single bubble split across processors
   - Drag calculation becomes inconsistent

**Solutions**:
```cpp
// Use geometric decomposition with alignment
method          simple;

simpleCoeffs
{
    n               (4 2 2);  // Align with expected flow
    
    // Specify decomposition delta
    delta           0.001;
}
```

### 6.3 Memory Bottlenecks

**Problem**: Out-of-memory errors in parallel runs

**Multiphase-specific memory demands**:
- Phase fields: 2-4× single-phase
- Turbulence models: per-phase (k-ε, k-ω)
- Interphase models: drag, lift, virtual mass matrices
- Geometric interface data (VOF): additional surface fields

**Diagnostic**:
```bash
# Check memory usage per process
# In SLURM:
sacct -j $SLURM_JOB_ID --format=JobID,MaxRSS

# During run:
top -p $(pgrep -d',' twoPhaseEulerFoam)
```

**Solutions**:
1. **Increase memory allocation**:
   ```bash
   #SBATCH --mem-per-cpu=8000  # 8GB per core
   ```

2. **Reduce mesh density** in critical regions

3. **Use different turbulence model** (mixture vs. per-phase)

### 6.4 Communication Overhead

**Symptom**: Parallel efficiency drops rapidly with core count

**Diagnostic**:
```bash
# Measure communication time
grep "Communication" solver.log

# Calculate efficiency
# η = T_1 / (N × T_N)
```

**Multiphase-specific issues**:

1. **Interphase coupling requires global reduction**:
   ```cpp
   // Every iteration, each phase needs:
   // - Global void fraction
   // - Reynolds numbers from all processors
   gSum(alpha_rhou);  // Expensive in parallel
   ```

2. **VOF interface reconstruction synchronization**:
   - Requires processor boundary exchange
   - More frequent than single-phase

**Mitigation**:
- Use **larger subdomains** (more cells/processor)
- **Reduce coupling frequency** (every N time steps)
- Choose **segregated solvers** over coupled

### 6.5 I/O Bottlenecks

**Problem**: Parallel file writing becomes very slow

**Symptoms**:
- Simulation stalls during time directory writing
- File system overload on hundreds of processors

**Solutions**:
```cpp
// File: system/controlDict

// Option 1: Reduce write frequency
writeInterval    0.1;  // Instead of 0.01

// Option 2: Write master only
writeFormat      ascii;  // Not binary
runTimeModifiable yes;

// Option 3: Use on-the-fly post-processing
// Instead of writing everything, process and write reduced data
functions
{
    surfaces
    {
        type            surfaces;
        writeFields     false;  // Don't write full fields
        surfaceFormat   vtk;
    }
}
```

**For HPC systems**:
- Use **parallel file systems** (Lustre, GPFS)
- Limit concurrent writers (< 100 processors writing simultaneously)
- Use **collective I/O** buffering

---

## 7. Debugging Parallel Issues

### 7.1 Common Error Messages

**"FOAM FATAL ERROR: Attempting to write to a sub-directory of a case which contains processor directories"**
- **Cause**: Writing decomposed case without proper structure
- **Fix**: Use `reconstructPar` first, or write to `processor*/` directories

**"different number of faces on local and global processor"**
- **Cause**: Mesh inconsistency across processors
- **Fix**: Run `checkMesh -parallel` on decomposed case

**"cannot find file" in processor directories**
- **Cause**: Incomplete decomposition
- **Fix**: Ensure all time directories decomposed: `decomposePar -allRegions`

### 7.2 Debugging Tools

**Check decomposition quality**:
```bash
# Visualize processor distribution
decomposePar -dict system/decomposeParDict
paraFoam -builtin -parallel

# Check cell balance
python3 << EOF
import numpy as np
for i in range(128):
    cells = !grep "cells" processor$i/constant/polyMesh/owner
    print(f"Proc {i}: {cells[0].split()[1]}")
EOF
```

**Test scaling**:
```bash
# Run scaling study
for nproc in 8 16 32 64 128; do
    decomposePar -np $nproc
    time mpirun -np $nproc solver -parallel
    reconstructPar -latestTime
    rm -rf processor*
done
```

---

## 8. Best Practices Summary

### 8.1 Pre-Simulation
1. **Check mesh quality** before decomposition
2. **Estimate memory requirements**: `cells × phases × fields × 8 bytes`
3. **Choose decomposition method** based on flow regime
4. **Plan for phase segregation** if dispersed flow expected

### 8.2 During Simulation
1. **Monitor load balance** via log files
2. **Track parallel efficiency**: should remain > 70%
3. **Use appropriate time step** for parallel stability
4. **Check for I/O bottlenecks** if write times are long

### 8.3 Post-Processing
1. **Reconstruct only necessary times**
2. **Use parallel post-processing** for large datasets
3. **Archive processor directories** for potential restarts

### 8.4 Multiphase-Specific Guidelines

| Flow Regime | Recommended Decomposition | Cells/Processor |
|-------------|---------------------------|-----------------|
| **VOF (free surface)** | scotch with refinement weights | 200,000-500,000 |
| **Bubbly flow (segregated)** | weighted by void fraction | 150,000-300,000 |
| **Homogeneous dispersion** | standard scotch | 250,000-500,000 |
| **Slug flow (intermittent)** | simple (axial decomposition) | 200,000-400,000 |

---

## 9. Further Reading

- OpenFOAM User Guide: **Chapter 3 - Running OpenFOAM cases in parallel**
- OpenFOAM Programmer's Guide: **Parallel processing**
- HPC Best Practices: **MPI Tutorial** (Lawrence Livermore National Laboratory)
- G. Paul et al., "Parallel Computational Fluid Dynamics" (book)
- M. Sahin, "Parallel Performance of OpenFOAM for Multiphase Flows" (conference paper)

---

**Next Module**: `[07_Advanced_Topics]` → `[04_Multiphysics]` for coupling multiphase flows with heat transfer, chemical reactions, and electromagnetics.