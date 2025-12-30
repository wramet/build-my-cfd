# Parallel Linear Algebra

High-Performance Computing for Large-Scale CFD Simulations

> **Why This Module Matters**
>
> - **Scale matters** — 100M cell cases take days on single core, hours on 32 cores
> - **Domain decomposition** is fundamental to parallel CFD architecture
> - **Communication overhead** can dominate runtime if not understood
> - **Global operations** (gSum, gMax) prevent silent correctness bugs in parallel runs
>
> **Practical Impact:**
> - Poor decomposition → 30-50% performance loss from communication overhead
> - Using local operations instead of global → wrong results in parallel (silently!)
> - Understanding processor boundaries → effective custom boundary conditions

---

## Learning Objectives

By the end of this module, you will be able to:

1. **Understand domain decomposition** — Explain how OpenFOAM partitions meshes and why decomposition quality affects solver performance
2. **Use global operations correctly** — Distinguish between local (sum, max) and global (gSum, gMax) operations and when each is required
3. **Debug parallel issues** — Identify processor communication problems, load imbalance, and parallel-specific bugs
4. **Configure parallel runs** — Set up decomposeParDict, choose appropriate decomposition methods, and validate load balance
5. **Implement parallel-aware code** — Write boundary conditions and functions that work correctly in both serial and parallel

---

## Table of Contents

1. [Domain Decomposition](#1-domain-decomposition)
2. [Processor Boundaries and Communication](#2-processor-boundaries-and-communication)
3. [Global vs Local Operations](#3-global-vs-local-operations)
4. [Matrix Assembly in Parallel](#4-matrix-assembly-in-parallel)
5. [Reduction Operations Reference](#5-reduction-operations-reference)
6. [Running Parallel Simulations](#6-running-parallel-simulations)
7. [Debugging Parallel Code](#7-debugging-parallel-code)
8. [Performance Optimization](#8-performance-optimization)

---

## 1. Domain Decomposition

### 1.1 What is Domain Decomposition?

**Domain decomposition** divides the computational mesh into subdomains, each assigned to a processor:

```
┌─────────────────────────────────────┐
│         Full Domain (100M cells)     │
├──────────┬──────────┬──────────┬──────┤
│  Proc 0  │  Proc 1  │  Proc 2  │ Pr 3 │
│   25M    │   25M    │   25M    │ 25M  │
│  cells   │  cells   │  cells   │cells │
└──────────┴──────────┴──────────┴──────┘
```

**Why decomposition quality matters:**

| Aspect | Good Decomposition | Poor Decomposition | Consequence |
|--------|-------------------|-------------------|-------------|
| **Load balance** | Equal cells per processor | Imbalanced | Some cores idle → 20-40% speed loss |
| **Boundary area** | Minimized processor boundaries | Fragmented | Excessive communication → 30-50% slowdown |
| **Contiguity** | Single connected region | Scattered pieces | Cache inefficiency, memory overhead |

### 1.2 Decomposition Methods

OpenFOAM provides three main decomposition methods (system/decomposeParDict):

```cpp
numberOfSubdomains  16;

// Method 1: Scotch (RECOMMENDED for unstructured meshes)
method              scotch;
// Uses graph partitioning to minimize boundaries
// Best for: Complex geometries, tetrahedral meshes

// Method 2: Hierarchical (GOOD for structured meshes)
method              hierarchical;
simpleCoeffs
{
    n   (4 4 1);    // 4 × 4 × 1 = 16 processors
}
// Best for: Block-structured grids, simple geometries

// Method 3: Simple (LEGACY, rarely used)
method              simple;
// Block decomposition along coordinate axes
// Issues: Poor load balance for complex geometries
```

**Practical file paths:**
- Configuration: `system/decomposeParDict`
- Output: `processor0/`, `processor1/`, ... directories
- Preview decomposition: `paraFoam -touch -processor` → visualize cell zones in ParaView

**How to choose:**

| Mesh Type | Recommended Method | Why |
|-----------|-------------------|-----|
| Unstructured (tet, poly) | `scotch` | Graph partitioning minimizes boundaries |
| Structured (hex, blockMesh) | `hierarchical` | Preserves structure, cache-friendly |
| Simple geometries | `hierarchical` | Predictable decomposition |
| Complex geometries | `scotch` | Handles irregularities optimally |

**Real-world example:**

```bash
# Check decomposition balance
decomposePar
# Look for: "cell statistics" output
# Good: Each proc has ±5% of average cells
# Bad: One proc has 2x others → severe imbalance

# Visualize decomposition
paraFoam -touch -processor
# In ParaView: Color by "processorID" cell zone
# Look for: Fragmented regions (bad) vs contiguous blocks (good)
```

---

## 2. Processor Boundaries and Communication

### 2.1 What are Processor Boundaries?

When decomposing, OpenFOAM creates **processor patches** at subdomain interfaces:

```cpp
// Automatic patch creation
// After decomposePar, check constant/polyMesh/boundary

// Example boundary file excerpt:
processor0_to_1
{
    type            processorCyclic;
    nFaces          1524;
    matchTolerance  0.0001;
    // ... communicates data between proc 0 and 1
}

// In code, detect processor boundaries:
forAll(mesh.boundary(), patchI)
{
    if (isA<processorFvPatch>(mesh.boundary()[patchI]))
    {
        const processorFvPatch& procPatch = 
            refCast<const processorFvPatch>(mesh.boundary()[patchI]);
        
        Info << "Processor boundary to neighbor: " 
             << procPatch.neighbProcNo() << endl;
    }
}
```

**Why this matters for boundary conditions:**

- **Standard BCs** (fixedValue, zeroGradient) work transparently on processor patches
- **Custom BCs** must handle processor patches correctly or parallel runs will fail
- **Data exchange** happens automatically during solve() calls

### 2.2 Communication Process

```
Iteration Loop:
┌─────────────────────────────────────────────────┐
│ 1. Compute local values (each proc)              │
│    ↓                                             │
│ 2. Exchange boundary data (MPI communication)    │
│    ↓                                             │
│ 3. Update ghost cells (halo cells)               │
│    ↓                                             │
│ 4. Continue computation                          │
└─────────────────────────────────────────────────┘

Communication overhead ∝ (processor boundary area) × (iterations)
```

**Practical consequence:**

A case with:
- 10M cells, 4 processors
- Poor decomposition: 2M boundary faces
- Good decomposition: 500k boundary faces

**Performance difference:** ~25% slower with poor decomposition due to communication overhead

---

## 3. Global vs Local Operations

### 3.1 The Critical Distinction

**This is the #1 source of parallel bugs in OpenFOAM!**

```cpp
// ❌ WRONG in parallel (local only)
scalar totalMass = sum(rho * mesh.V());  
// → Only sums cells on THIS processor
// → Wrong answer (1/N of true value on average)

// ✓ CORRECT in parallel (global reduction)
scalar totalMass = gSum(rho * mesh.V()); 
// → Sums across ALL processors
// → Correct answer in serial AND parallel
```

### 3.2 Operation Reference

| Operation | Local (Single Proc) | Global (All Procs) | When to Use |
|-----------|-------------------|-------------------|-------------|
| **Sum** | `sum(field)` | `gSum(field)` | Total mass, volume, flux |
| **Maximum** | `max(field)` | `gMax(field)` | Find global extreme values |
| **Minimum** | `min(field)` | `gMin(field)` | Find global extreme values |
| **Average** | `average(field)` | `gAverage(field)` | Domain-averaged quantities |
| **Product** | `prod(field)` | `gProd(field)` | Rarely used |
| **Sum of mag** | `sum(mag(field))` | `gSumMag(field)` | L1 norm |

**Why "average" is especially tricky:**

```cpp
// ❌ WRONG
scalar avgT = sum(T) / T.size();  
// → Divides local sum by local size
// → Each processor gets different (wrong) average

// ✓ CORRECT
scalar avgT = gAverage(T);  // Handles weighting automatically

// ✓ ALSO CORRECT (if manual control needed)
scalar avgT = gSum(T) / gSum(mesh.V());  // Mass-weighted average
```

### 3.3 Practical Examples

**Example 1: Residual monitoring**

```cpp
// In solver loop
scalar initialResidual = 0;
{
    // Local residual (on this processor)
    scalar localResidual = gSumMag(mag(TEqn.residual()));
    
    // Global residual (across all processors)
    initialResidual = localResidual / 
                      (gSum(T.internalField().size()) + SMALL);
    
    // Note: Many solvers handle this internally, but custom 
    // convergence checks must use global operations
}
```

**Example 2: Computing global Courant number**

```cpp
// ❌ WRONG
scalar maxCo = max(Co);  // Only checks this processor

// ✓ CORRECT
scalar maxCo = gMax(Co); // Checks ALL processors
Info << "Max Courant number: " << maxCo << endl;
```

**Example 3: Mass balance check**

```cpp
// Mass flux through boundaries
scalar massIn = 0.0;
scalar massOut = 0.0;

forAll(mesh.boundary(), patchI)
{
    const fvPatch& patch = mesh.boundary()[patchI];
    
    // Sum flux on this patch (LOCAL operation)
    scalar patchFlux = sum(rhoPhi.boundaryField()[patchI]);
    
    // Add to global totals (GLOBAL operation)
    massIn += max(patchFlux, 0.0);   // Inflow
    massOut += max(-patchFlux, 0.0);  // Outflow
}

// Reduce across processors
massIn = gSum(massIn);
massOut = gSum(massOut);

scalar imbalance = mag(massIn - massOut) / (0.5 * (massIn + massOut));
Info << "Mass imbalance: " << imbalance << endl;
```

### 3.4 Debugging Template

```cpp
// Add to custom functions to verify parallel correctness
if (Pstream::parRun())
{
    scalar localValue = sum(mag(p - pOld));
    scalar globalValue = gSum(mag(p - pOld));
    
    if (mag(localValue - globalValue) > SMALL)
    {
        Warning << "Processor " << Pstream::myProcNo() 
                << ": Local != global difference!" << endl;
    }
}
```

---

## 4. Matrix Assembly in Parallel

### 4.1 How It Works

**Key insight:** Matrix assembly is largely **transparent** to the user

```cpp
// This works identically in serial and parallel
fvScalarMatrix TEqn
(
    fvm::ddt(T)
  + fvm::div(phi, T)
  - fvm::laplacian(DT, T)
 ==
    fvm::SuSp(Source, T)
);

TEqn.solve();  // Parallel-aware solve automatically
```

### 4.2 Behind the Scenes

Each processor:

1. **Assembles local matrix** for its cells
   - Diagonal coefficients (internal)
   - Off-diagonal coefficients (neighbor connections)
   - Source terms

2. **Processor boundaries treated as BC**
   - Coefficients to processor neighbors stored in BC
   - Similar to cyclic patches conceptually

3. **Communication during linear solve**
   - Matrix-vector products require neighbor data
   - MPI communication happens within GAMG/GCG solvers
   - Reduction operations for convergence checks

```
Local matrix structure (simplified):
┌────────────────────────────────────┐
│  Internal cells                    │
│  ┌───┬───┬───┐                     │
│  │ A │ B │ C │  ← Local matrix    │
│  ├───┼───┼───┤    (this proc)     │
│  │ D │ E │ F │                     │
│  └───┴───┴───┘                     │
│                                    │
│  Processor BCs → ┌─────┐           │
│                   │ MPI │ ← Ghost  │
│                   └─────┘   values│
└────────────────────────────────────┘
```

### 4.3 Solver Considerations

**Linear solvers** (system/fvSolution):

```cpp
solvers
{
    T
    {
        // AMG solver is parallel-aware
        solver          GAMG;
        tolerance       1e-06;
        relTol          0.1;
        
        smoother        GaussSeidel;
        
        // Processor-aware preconditioning
        nPreSweeps      0;
        nPostSweeps     2;
        nFinestSweeps   2;
        
        cacheAgglomeration on;
        agglomerator    faceAreaPair;  // Good for parallel
        mergeLevels     1;
    }
    
    p
    {
        // MUST use global reduction preconditioner
        solver          PCG;
        preconditioner  DIC;  // ✓ Parallel-safe
        // preconditioner  DILU;  // ✗ NOT parallel-safe
        
        tolerance       1e-06;
        relTol          0.01;
    }
}
```

**Critical warning:** Some preconditioners are NOT parallel-safe:

| Preconditioner | Parallel Safe? | Notes |
|---------------|----------------|-------|
| **DIC** (Diagonal Incomplete Cholesky) | ✓ Yes | Safe, but slower than DILU in serial |
| **DILU** (Diagonal ILU) | ✗ No | Silent wrong answers in parallel! |
| **GAMG** | ✓ Yes | Best for large cases |
| **PBiCGStab** | ✓ Yes | Use with DIC or none |

---

## 5. Reduction Operations Reference

> **Note:** This table serves as a quick reference. For detailed explanation of WHY global operations are required, see [Section 3](#3-global-vs-local-operations).

### 5.1 Complete Reduction Reference Table

| Operation | Function | Return Type | Typical Use Case | Parallel Safe? |
|-----------|----------|-------------|------------------|----------------|
| **Sum** | `sum(field)` | `Type` | Sum over local cells | No (local only) |
| **Global Sum** | `gSum(field)` | `Type` | Total mass, flux | ✓ Yes |
| **Max** | `max(field)` | `Type` | Find local maximum | No (local only) |
| **Global Max** | `gMax(field)` | `Type` | Find global maximum | ✓ Yes |
| **Min** | `min(field)` | `Type` | Find local minimum | No (local only) |
| **Global Min** | `gMin(field)` | `Type` | Find global minimum | ✓ Yes |
| **Average** | `average(field)` | `Type` | Local average (unweighted) | No (local only) |
| **Global Avg** | `gAverage(field)` | `Type` | Domain average | ✓ Yes |
| **Sum of Mag** | `sum(mag(field))` | `scalar` | L1 norm local | No (local only) |
| **Global Sum Mag** | `gSumMag(field)` | `scalar` | L1 norm global | ✓ Yes |

### 5.2 Field-Specific Operations

| Field Type | Reduction | Notes |
|-----------|-----------|-------|
| **volScalarField** | `gSum(field)` | Returns scalar |
| **volVectorField** | `gSum(field)` | Returns vector (each component reduced) |
| **volTensorField** | `gSum(field)` | Returns tensor (each component reduced) |
| **surfaceScalarField** | `gSum(field & mesh.Sf())` | Flux through faces |

### 5.3 Advanced Reduction Patterns

```cpp
// Pattern 1: Weighted sum
scalar weightedSum = gSum(weightField * valueField);

// Pattern 2: Conditional reduction
scalar sumPositive = gSum(pos(field) * field);  // Sum only positive values

// Pattern 3: Field statistics
scalar mean = gAverage(field);
scalar var = gSum(magSqr(field - mean)) / (gSum(mesh.V()) / gSum(mesh.V()/field.size()));

// Pattern 4: Check if ANY processor has condition
bool anyAboveThreshold = gMax(pos(field - threshold)) > 0.5;
```

---

## 6. Running Parallel Simulations

### 6.1 Standard Workflow

```bash
# 1. Decompose case
decomposePar

# Output: processor0/, processor1/, ..., processorN/

# 2. Run parallel (adjust N to your core count)
mpirun -np 16 solver -parallel

# Alternative syntax (OpenFOAM ≥ 4.x)
mpirun -np 16 solver -parallel

# Or with MPI launcher options
mpirun -np 16 --bind-to core --map-by socket:PE=4 solver -parallel

# 3. Reconstruct results (optional, for post-processing)
reconstructPar

# 4. Clean processor directories (when done)
rm -rf processor*
```

### 6.2 System Configuration

**File: system/decomposeParDict**

```cpp
// Basic configuration
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      decomposeParDict;
}

// Number of subdomains (should match mpirun -np)
numberOfSubdomains  16;

// Decomposition method
method              scotch;  // RECOMMENDED

// Scotch-specific settings (if using scotch)
scotchCoeffs
{
    // Optional: Write decomposition weights
    // processorWeights (1.0 1.0 1.0 ...);
    
    // Optional: Minimize communication
    // strategy "quality";  // Default
}

// Hierarchical method (alternative)
hierarchicalCoeffs
{
    n       (4 4 1);  // 16 processors: 4 × 4 × 1
    
    // Ordering of decomposition axes
    order   xyz;      // Decompose x first, then y, then z
    
    // Alternative: delta decomposition (load-aware)
    // delta    0.001;  // Tolerance for cell distribution
}

// Simple method (legacy, not recommended)
simpleCoeffs
{
    n   (4 4 1);
    
    // Define which direction to decompose first
    // delta 0.001;
}
```

### 6.3 Validation Checklist

After decomposing, verify:

```bash
# 1. Check cell distribution
decomposePar | grep "cells"

# Expected output:
# Processor 0: number of cells = 156234
# Processor 1: number of cells = 157891
# ...

# Good: All processors within ±5% of mean
# Bad: One processor has 2x others → severe imbalance

# 2. Verify processor patches
ls processor0/constant/polyMesh/boundary
# Look for: processor0_to_1, processor0_to_2, etc.

# 3. Preview in ParaView
paraFoam -touch -processor
# Open ParaView, color by "processorID" cell zone
# Should see: Reasonably contiguous regions

# 4. Check load balance (advanced)
# Run short test, check CPU usage via htop
# All cores should be at ~95-100%
# Bad sign: Some cores idle, others at 100%
```

---

## 7. Debugging Parallel Code

### 7.1 Processor-Specific Execution

```cpp
// Only execute on master processor (rank 0)
if (Pstream::myProcNo() == 0)
{
    Info << "Master processor writing summary" << endl;
    // Write output files, print global info
}

// Only execute on specific processor
if (Pstream::myProcNo() == 1)
{
    // Debug info from processor 1
}

// Execute on all processors
Info << "Processor " << Pstream::myProcNo() 
     << " of " << Pstream::nProcs() << endl;
```

### 7.2 Data Gathering and Scattering

```cpp
// Gather data from all processors to master
List<scalar> localValues(Pstream::nProcs());
localValues[Pstream::myProcNo()] = localSum;

// Gather to master
Pstream::gather(localValues);

// Now master has all values
if (Pstream::myProcNo() == 0)
{
    Info << "Values from all processors: " << localValues << endl;
}

// Scatter data from master to all
Pstream::scatter(someGlobalValue);
// Now all processors have the same value
```

### 7.3 Common Parallel Bugs

**Bug 1: Missing global reduction**

```cpp
// ❌ Symptom: Different (wrong) answers on different proc counts
scalar maxT = max(T);  // Only local max

// ✓ Fix: Use global reduction
scalar maxT = gMax(T);  // Global max
```

**Bug 2: Writing files from all processors**

```cpp
// ❌ Symptom: File corruption or I/O errors
ofstream file("output.dat");  // All procs try to write!

// ✓ Fix: Only master writes
if (Pstream::myProcNo() == 0)
{
    OFstream file("output.dat");
    file << data << endl;
}
```

**Bug 3: Not checking if running in parallel**

```cpp
// ✓ Robust pattern
if (Pstream::parRun())
{
    // Parallel-specific operations
    scalar globalValue = gSum(localValue);
}
else
{
    // Serial fallback (redundant but safe)
    scalar globalValue = sum(localValue);
}

// Or even simpler: gSum() works in serial too!
scalar globalValue = gSum(localValue);  // Always correct
```

**Bug 4: Processor boundary patches in custom BCs**

```cpp
// ❌ Custom BC that fails on processor patches
void MyPatch::updateCoeffs()
{
    // This breaks when applied to processor boundaries!
    const fvPatch& p = patch();
    forAll(p, i)
    {
        // Direct neighbor access fails on processor patches
        // because neighbor data is on different processor
    }
}

// ✓ Fix: Handle processor patches specially
void MyPatch::updateCoeffs()
{
    if (isA<processorFvPatch>(patch()))
    {
        // Processor patches handled by framework
        return;
    }
    
    // Normal patch processing
    // ...
}
```

### 7.4 Debugging Tools

```cpp
// Add to custom code for debugging

// 1. Print distribution of field
if (Pstream::myProcNo() == 0)
{
    Info << "Field distribution:" << nl
         << "  Min: " << gMin(field) << nl
         << "  Max: " << gMax(field) << nl
         << "  Avg: " << gAverage(field) << nl
         << "  Sum: " << gSum(field) << endl;
}

// 2. Check processor balance
label nLocalCells = mesh.nCells();
label nGlobalCells = gSum(nLocalCells);
scalar loadImbalance = mag(scalar(nLocalCells) * Pstream::nProcs() 
                           - nGlobalCells) / nGlobalCells;

if (loadImbalance > 0.1)  // 10% imbalance threshold
{
    Warning << "Processor " << Pstream::myProcNo() 
            << " has " << loadImbalance * 100 << "% load imbalance" << endl;
}

// 3. Synchronization check
scalar syncCheck = sum(mag(p - pOld));
reduce(syncCheck, sumOp<scalar>());
```

---

## 8. Performance Optimization

### 8.1 Load Balancing

**Signs of poor load balance:**

```bash
# Monitor during run
htop  # Look for idle cores

# Or use MPI profiling
mpirun -np 16 -mca coll_tuned_use_dynamic_rules 1 \
       -mca coll_tuned_dynamic_rules_filename rules.xml \
       solver -parallel

# In log file, look for:
# - Vastly different iteration counts between processors
# - Some processors finishing much earlier
```

**Improving load balance:**

1. **Use scotch decomposition** (default recommendation)
2. **Increase subdomain count** slightly (e.g., 20 procs for 16 cores)
   - OS scheduler can balance better
3. **Avoid too many procs** for small cases (< 50k cells per proc inefficient)
4. **Check mesh quality** — highly skewed cells lead to imbalance

### 8.2 Communication Overhead

**Minimize communication:**

```cpp
// ❌ Bad: Global reduction every iteration
for (int iter = 0; iter < 1000; iter++)
{
    scalar globalCheck = gSum(expensiveComputation());  // Synchronizes all procs
    // ... use globalCheck
}

// ✓ Better: Local checks, global only when needed
for (int iter = 0; iter < 1000; iter++)
{
    scalar localCheck = sum(expensiveComputation());
    scalar globalCheck = localCheck;
    
    // Only communicate when necessary
    if (iter % 10 == 0)  // Every 10 iterations
    {
        globalCheck = gSum(localCheck);
    }
    // ... use globalCheck (may be slightly stale)
}
```

### 8.3 Scalability Analysis

**Strong scaling** (fixed problem size, increasing processors):

```
Speedup = T_serial / T_parallel
Ideal: Linear speedup (16x faster on 16 procs)

Plot: Speedup vs processor count
Good: Near-linear up to many cores
Bad: Plateaus early → communication bottleneck
```

**Weak scaling** (fixed problem size per processor):

```
Efficiency = (T_1 / N) / T_N
Ideal: Constant time as problem size grows with cores

Plot: Time per million cells vs processor count
Good: Flat (constant time per cell)
Bad: Increases → communication overhead grows
```

**Practical limits:**

| Mesh Size | Optimal Cores | Cells per Core |
|-----------|--------------|----------------|
| 1M cells | 4-8 | 125k-250k |
| 10M cells | 16-32 | 300k-600k |
| 100M cells | 64-128 | 780k-1.5M |
| 1B cells | 256-512 | 2M-4M |

Going beyond these ranges gives diminishing returns due to communication overhead.

---

## Key Takeaways

1. **Always use global operations in code that might run in parallel**
   - `gSum()`, `gMax()`, `gMin()`, `gAverage()` instead of local versions
   - Using local operations → silent wrong answers in parallel

2. **Domain decomposition quality dramatically affects performance**
   - Use `scotch` for unstructured meshes (minimizes boundaries)
   - Use `hierarchical` for structured meshes (preserves cache locality)
   - Aim for ±5% load balance and minimal processor boundary area

3. **Processor boundaries are created and handled automatically**
   - Custom boundary conditions must detect and handle processor patches
   - Linear solvers (GAMG, PCG) are parallel-aware if configured correctly

4. **Debug parallel code with processor-specific execution**
   - `if (Pstream::myProcNo() == 0)` for master-only operations
   - Print from each processor to identify communication issues
   - Check load balance via `gSum(mesh.nCells())` distribution

5. **Performance optimization focuses on minimizing communication**
   - Good decomposition → 30-50% performance improvement
   - Avoid excessive global reductions in tight loops
   - Target 500k-1M cells per core for optimal efficiency

---

## Concept Check

<details>
<summary><b>1. Why must you use gSum() instead of sum() in parallel code?</b></summary>

**Answer:** `sum()` only operates on cells local to the current processor, giving 1/N of the true value (on average). `gSum()` performs a global reduction across all processors via MPI, summing local contributions from all subdomains. Using `sum()` in parallel gives **silently wrong results** — the code runs without errors but produces incorrect answers.
</details>

<details>
<summary><b>2. What are processor patches and how are they created?</b></summary>

**Answer:** Processor patches are special boundary types created automatically by `decomposePar` at interfaces between subdomains. They handle MPI communication of field data between neighboring processors during matrix assembly and linear solves. Custom boundary conditions must check for processor patches using `isA<processorFvPatch>()` and handle them appropriately (usually by letting the framework manage them automatically).
</details>

<details>
<summary><b>3. Why is scotch decomposition generally preferred over simple or hierarchical?</b></summary>

**Answer:** Scotch uses graph partitioning to **minimize processor boundary area** while maintaining load balance. Fewer boundary cells → less MPI communication → better parallel performance. Simple and hierarchical methods can create fragmented decompositions with excessive communication overhead, especially for complex, unstructured meshes. Hierarchical is competitive for structured meshes where it can preserve cache-friendly data access patterns.
</details>

<details>
<summary><b>4. How can you check if your parallel simulation has load imbalance?</b></summary>

**Answer:** Several methods:
1. **After decomposePar:** Check cell counts per processor (should be within ±5%)
2. **During run:** Use `htop` to monitor CPU usage (idle cores indicate imbalance)
3. **In code:** Compute `gSum(mesh.nCells()) / Pstream::nProcs()` vs local cell count
4. **From timing:** Look for processors finishing at vastly different times

Poor decomposition → some processors have 2x more cells → those procs become bottlenecks, wasting parallel resources.
</details>

<details>
<summary><b>5. What's wrong with using DILU preconditioner in parallel runs?</b></summary>

**Answer:** DILU (Diagonal Incomplete LU) is **not parallel-safe** — it requires global information about the matrix structure that is not available in the decomposed form. Using DILU in parallel gives **incorrect solutions** because each processor computes incomplete LU factorization independently, leading to inconsistent preconditioning across subdomains. Use DIC (Diagonal Incomplete Cholesky) or GAMG instead — these are parallel-aware.
</details>

---

## Related Documentation

- **Linear Solvers:** [04_Linear_Solvers_Hierarchy.md](04_Linear_Solvers_Hierarchy.md) — Deep dive into parallel solver configuration
- **Matrix Assembly:** [03_fvMatrix_Architecture.md](03_fvMatrix_Architecture.md) — How matrices are constructed locally
- **Overview:** [00_Overview.md](00_Overview.md) — High-level introduction to parallel linear algebra in OpenFOAM

---

## Practical Exercises

### Exercise 1: Decompose and Analyze

```bash
# Navigate to a tutorial case
cd $FOAM_TUTORIALS/incompressible/simpleFoam/airFoil2D

# Decompose with scotch
decomposePar

# Examine processor distribution
for i in processor*; do
    echo "$i: $(grep 'cells' $i/constant/polyMesh/points | wc -l) cells"
done

# Visualize in ParaView
paraFoam -touch -processor
# Open ParaView, load case, color by processorID
# Assess: Are regions contiguous? Is load balanced?

# Try hierarchical decomposition
# Edit system/decomposeParDict, change method to hierarchical
# Run decomposePar again and compare
```

**Goal:** Understand how decomposition method affects partition quality.

### Exercise 2: Global Operations Practice

Create a custom function object (`globalStats`) that:

```cpp
// In code
volScalarField T = mesh.lookupObject<volScalarField>("T");

// Compute global statistics
scalar Tmin = gMin(T);
scalar Tmax = gMax(T);
scalar Tavg = gAverage(T);
scalar Tsum = gSum(T);

// Write to file (master only)
if (Pstream::myProcNo() == 0)
{
    OFstream file("globalStats.dat");
    file << "Min: " << Tmin << nl
         << "Max: " << Tmax << nl
         << "Avg: " << Tavg << nl
         << "Sum: " << Tsum << endl;
}
```

**Goal:** Practice using global reductions and master-only file writing.

### Exercise 3: Parallel Bug Hunt

```cpp
// This code has parallel bugs. Find and fix them!

scalar residual = 0;
for (int i = 0; i < maxIter; i++)
{
    // Update field
    T = T + omega * (T_new - T);
    
    // Check convergence
    residual = max(mag(T - T_old));  // Bug?
    
    if (residual < tolerance)
    {
        Info << "Converged!" << endl;  // Bug?
        break;
    }
    
    T_old = T;
}

// Write result
ofstream file("solution.dat");  // Bug?
file << T << endl;
```

**Bugs to find:**
1. Line 10: `max()` should be `gMax()` for parallel correctness
2. Line 13: Prints from all processors (should check `Pstream::myProcNo() == 0`)
3. Line 21: All processors write to same file (should be master-only)

---

**Last Updated:** 2024-12-30
**OpenFOAM Version:** 9+, v2012+, v2212+ (concepts apply broadly)
**Contributors:** OpenFOAM CFD Training Materials