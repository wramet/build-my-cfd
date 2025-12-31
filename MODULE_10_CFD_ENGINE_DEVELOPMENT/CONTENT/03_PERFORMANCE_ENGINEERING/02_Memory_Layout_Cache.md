# Memory Layout & Cache Optimization

Cache-Friendly Programming for OpenFOAM

---

## Learning Objectives

By the end of this module, you will be able to:

1. **Understand** cache hierarchy and its impact on CFD performance
2. **Calculate** Average Memory Access Time (AMAT) from real profiling data
3. **Apply** cache optimization techniques: AoS vs SoA, loop ordering, data alignment
4. **Diagnose** cache performance issues using `perf` and roofline models
5. **Optimize** OpenFOAM code for memory-bound scenarios through mesh reordering and layout choices

---

## Prerequisites

| Required Knowledge | Source |
|:---|:---|
| Memory management fundamentals | Module 09: Memory Management |
| C++ data structures (structs, arrays) | Module 01: Template Programming |
| OpenFOAM field types | Module 04: OpenFOAM Programming |
| Profiling basics | Module 10: Performance Engineering (01_Profiling_Tools.md) |
| Design patterns (CRTP) | Module 09: Design Patterns |

---

## The Memory Wall

**WHAT:** The growing speed gap between CPU and memory

```
           Speed Gap (30 years)
CPU    ████████████████████████  (1000x faster)
Memory ██                        (10x faster)
```

**WHY it matters:**
- CPU performance improves ~50% per year (Moore's Law)
- Memory bandwidth improves ~7% per year
- Gap widens → memory becomes bottleneck

**NUMBERS:**
- 1990: CPU 33 MHz, Memory 100 ns (~3 CPU cycles)
- 2020: CPU 4 GHz, Memory 70 ns (~280 CPU cycles)
- **Impact:** Memory access is **90x slower** relative to CPU

**HOW OpenFOAM addresses it:**
- Cache hierarchy (L1/L2/L3)
- Expression templates (avoid temporaries)
- Mesh reordering algorithms
- SoA alternatives for component operations

---

## Cache Basics

### Cache Hierarchy

```
Level      Size        Latency    Bandwidth    Cost
────────────────────────────────────────────────────
Registers  ~1 KB       1 cycle    ~10 TB/s     $$$
L1 Cache   32 KB       4 cycles   ~500 GB/s    $$$
L2 Cache   256 KB      12 cycles  ~200 GB/s    $$
L3 Cache   8 MB        40 cycles  ~100 GB/s    $
RAM        64 GB       200 cycles ~50 GB/s     -
SSD        1 TB        100,000 cycles ~5 GB/s  -
```

**Key Insight:** L1 hit: 4 cycles, RAM access: 200 cycles = **50x slower!**

### Cache Line Concept

```
Memory:    [A B C D E F G H] [I J K L M N O P] ...
           ←── 64 bytes ──→  ←── 64 bytes ──→

Access A → Load entire line [A B C D E F G H] into cache
Access B → Already in cache! (free, 0 cycles)
Access I → Cache miss, load [I J K L M N O P] (200 cycles)
```

**Implication:**
- Sequential access: 1 cache miss per 8 doubles = **high efficiency**
- Random access: 1 cache miss per access = **50x slower**

---

## Array of Structs (AoS) vs Struct of Arrays (SoA)

### AoS (OpenFOAM Default)

```cpp
struct Vector { scalar x, y, z; };  // 24 bytes
List<Vector> field;

// Memory layout:
// [x₀ y₀ z₀] [x₁ y₁ z₁] [x₂ y₂ z₂] ...
// ←─ 64 bytes →
//   Uses 2.67 vectors per cache line
```

**Pros:**
- Natural physics representation (velocity = vector)
- Per-element access: `U[i].x(), U[i].y(), U[i].z()` fast
- Matches FVM cell-based operations

**Cons:**
- Component-only operations waste cache bandwidth
- Cache utilization = 33% when accessing single component

### SoA (Alternative)

```cpp
struct VectorField {
    scalarList x;  // All x's contiguous
    scalarList y;
    scalarList z;
};

// Memory layout:
// [x₀ x₁ x₂ ...] [y₀ y₁ y₂ ...] [z₀ z₁ z₂ ...]
// ←─ 64 bytes → ←─ 64 bytes →
//   Uses 8 doubles per cache line
```

**Pros:**
- Component loops achieve 100% cache utilization
- Better for vectorization (SIMD)
- Enables loop fusion

**Cons:**
- Per-element access requires 3 memory lookups
- Less intuitive for physics operations

### When to Use What

| Pattern | Best For | Example | Cache Efficiency |
|:---|:---|:---|:---|
| **AoS** | Per-element operations | `U[i] = U[i] + dt*dUdt[i]` | 100% (use all components) |
| **AoS** | Vector math | `mag(U[i]), U[i] & V[i]` | 100% (use all components) |
| **SoA** | Component loops | `for(i) x[i] = a[i]*x[i]` | 100% (sequential access) |
| **AoS** | OpenFOAM default | Most FVM operations | Context-dependent |

```cpp
// AoS works well (access all components of same cell)
forAll(U, i)
{
    U[i] = U[i] + dt * dUdt[i];  // All x,y,z together → cache efficient
}

// SoA would be better (process one component at a time)
forAll(Ux, i)
{
    Ux[i] = a[i] * Ux[i];  // Only x component → better cache use with SoA
}
```

---

## Loop Ordering

### Problem: Matrix Storage Layout

```cpp
// C++ stores matrices row-major by default:
// A[0][0], A[0][1], A[0][2], A[1][0], A[1][1], ...
// ←──── row 0 ────→ ←──── row 1 ────→
// Sequential in memory
```

### Bad: Column-Major Access

```cpp
// Column-first (bad) - jumps in memory
for (label j = 0; j < cols; ++j)
    for (label i = 0; i < rows; ++i)
        A[i][j] = ...;  // Cache miss EVERY access!

// Memory access pattern: A[0][0], A[1][0], A[2][0], ...
// Jumps by row_size * sizeof(scalar) bytes
```

**Performance Impact:**
```
Matrix 1000x1000, double precision:
- Column access: ~1000x more cache misses
- Measured slowdown: 3-10x on modern CPUs
```

### Good: Row-Major Access

```cpp
// Row-first (good) - sequential memory
for (label i = 0; i < rows; ++i)
    for (label j = 0; j < cols; ++j)
        A[i][j] = ...;  // Hits cache line!

// Memory access pattern: A[0][0], A[0][1], A[0][2], ...
// Sequential → 1 cache miss per 8 elements
```

---

## OpenFOAM Memory Considerations

### Field Storage Layout

```cpp
volScalarField p(mesh);

// Memory organization:
// Internal field (contiguous):
// p.internalField()[0], [1], [2], ..., [nCells-1]
// ←──────── sequential ─────────→

// Boundary fields (separate per patch):
// p.boundaryField()[patch0][0], [1], ...
// p.boundaryField()[patch1][0], [1], ...
```

**Key Points:**
- Internal field: **cache-friendly** (contiguous array)
- Boundary fields: **cache-friendly** within each patch
- Transition between patches: potential cache miss

### Face Loop Cache Behavior

```cpp
// OpenFOAM fvMatrix assembly (simplified)
forAll(owner, facei)
{
    label own = owner[facei];      // Sequential → cache hit!
    label nei = neighbour[facei];  // Sequential → cache hit!
    
    result[own] += flux[facei];    // Random access → cache miss!
    result[nei] -= flux[facei];    // Random access → cache miss!
}
```

**Cache Analysis:**
```
100k cells, 300k internal faces:
- owner[], neighbour[], flux[]: sequential → L1 hit rate ~95%
- result[own], result[nei]: random access → L1 hit rate ~30%

Measured with perf:
$ perf stat -e L1-dcache-load-misses,L1-dcache-loads simpleFoam
     150M      L1-dcache-loads
      45M      L1-dcache-load-misses     # 30% miss rate
```

**Why unavoidable:** Finite Volume Method requires random cell access due to mesh connectivity

---

## Common Pitfalls in Cache Optimization

### Pitfall 1: Premature SoA Conversion

```cpp
// BAD: Converting to SoA without profiling
struct VectorField {
    scalarList x, y, z;
};

// If code does per-element operations:
forAll(U, i)
{
    vector UVec(x[i], y[i], z[i]);  // 3 memory lookups
    UVec = UVec + dt * dUdt[i];      // Then compute
    x[i] = UVec.x();  // 3 writes back
    y[i] = UVec.y();
    z[i] = UVec.z();
}

// WORSE than AoS due to extra loads/stores!
```

**Solution:** Profile first, optimize hot paths only

### Pitfall 2: Over-Alignment

```cpp
// BAD: Excessive alignment wastes memory
alignas(4096) scalar field[1000];  // 4KB aligned

// Problem: 
// - Most operations touch < 64 bytes at once
// - Wastes memory padding
// - Reduces effective cache size
```

**Solution:** Use cache-line alignment (64 bytes) for hot data only

### Pitfall 3: Ignoring Mesh Bandwidth

```cpp
// BAD: Using unsorted mesh
// Cell indices: [0, 99999, 1, 99998, 2, 99997, ...]
// High bandwidth → poor cache locality

forAll(owner, facei)
{
    result[owner[facei]] += flux[facei];  // Cache miss!
}

// Measured: 7.5% cache miss rate → 3x slower
```

**Solution:**
```bash
renumberMesh -method CuthillMcKee
# Reduces bandwidth → sequential cell indices
# Result: 2% cache miss rate
```

### Pitfall 4: Cache Pollution from Temporaries

```cpp
// BAD: Chained operations create temporaries
volScalarField result = sqr(T) + 2.0 * T + 1.0;

// What happens:
// 1. sqr(T) → allocate temporary field
// 2. 2.0 * T → allocate another temporary
// 3. Add temporaries → allocate third temporary
// 4. Copy to result

// Each temporary pollutes cache
```

**Solution:**
```cpp
// GOOD: Use expression templates (automatic)
tmp<volScalarField> tResult = sqr(T) + 2.0*T + 1.0;
const volScalarField& result = tResult();
// Compiler fuses into single loop, no temporaries

// BEST: In-place when possible
T *= T;  // Modify in place, zero allocations
```

### Pitfall 5: Micro-Benchmarks Lie

```cpp
// BAD: Benchmark in isolation
void benchmark() {
    const int N = 1000000;
    double data[N];
    
    // Tight loop → fits in L1 cache!
    for (int i = 0; i < N; i++)
        data[i] = data[i] * data[i];
    
    // Reports: "100x speedup from optimization"
    // Reality: Real CFD case has 10x more data → L3/RAM bound
}
```

**Solution:** Benchmark with realistic data sizes (>> cache size)

---

## Cache Performance Calculation

### Step 1: Measure Cache Statistics

```bash
$ cd $FOAM_TUTORIALS/incompressible/simpleFoam/airFoil2D
$ blockMesh
$ simpleFoam &
$ PID=$!
$ perf stat -e cache-references,cache-misses,L1-dcache-loads,L1-dcache-load-misses -p $PID -- sleep 60

 Performance counter stats for process '12345':

     52,345,678,901      cache-references          #  6.152 G/sec
      1,234,567,890      cache-misses              #    2.36 % of all cache refs
    234,567,890,123      L1-dcache-loads           # 27.567 G/sec
     12,345,678,901      L1-dcache-load-misses     #    5.26 % of all L1-dcache hits

      60.023456789 seconds time elapsed
```

### Step 2: Calculate Cache Miss Rates

```
Overall cache miss rate = cache-misses / cache-references
                       = 1,234,567,890 / 52,345,678,901
                       = 0.0236 = 2.36%

L1 cache miss rate = L1-dcache-load-misses / L1-dcache-loads
                  = 12,345,678,901 / 234,567,890,123
                  = 0.0526 = 5.26%
```

**Interpretation:**
- **2.36%** overall miss rate is **good** (target < 5%)
- **5.26%** L1 miss rate means 94.74% of data found in L1

### Step 3: Calculate Average Memory Access Time (AMAT)

**Cache Hierarchy Latencies:**
- L1 hit: 4 cycles
- L2 hit: 12 cycles
- L3 hit: 40 cycles
- RAM access: 200 cycles

**AMAT Formula:**
```
AMAT = L1_hit_time 
     + (L1_miss_rate × L2_hit_time)
     + (L2_miss_rate × L3_hit_time)
     + (L3_miss_rate × RAM_time)
```

**Assuming typical miss rates:**
```
L1_miss_to_L2 = 5.26% (measured)
L2_miss_to_L3 = 20% (typical)
L3_miss_to_RAM = 10% (typical)

AMAT = 4 + (0.0526 × 12) + (0.20 × 0.0526 × 40) + (0.10 × 0.20 × 0.0526 × 200)
     = 4 + 0.63 + 0.42 + 0.21
     = 5.26 cycles per access
```

**Speedup from Cache:**
```
Without cache (all RAM access):
AMAT_no_cache = 200 cycles

Speedup = 200 / 5.26 = 38.0x
```

### Step 4: Calculate Memory Stall Time

```
Total cycles = CPU_freq × time
            = 3.0 GHz × 60 seconds
            = 180 billion cycles

Memory stalls = cache_misses × (AMAT - L1_hit_time)
             = 1.23B × (5.26 - 4)
             = 1.23B × 1.26
             = 1.55 billion cycles

% time stalled on memory = 1.55B / 180B = 0.86%
```

**Conclusion:** Only 0.86% of time stalled on memory → **compute-bound**, not memory-bound

---

## Roofline Model Analysis

### What is Roofline Model?

**WHAT:** Visual model showing performance limits based on arithmetic intensity

**WHY it matters:** Identifies whether code is compute-bound or memory-bound

**HOW to use:** Plot achieved performance vs. arithmetic intensity

### Step 1: Measure Hardware Limits

```bash
# CPU specifications
$ lscpu | grep "Model name"
Model name: Intel(R) Xeon(R) Gold 6248R @ 3.00GHz

$ lscpu | grep "core(s) per socket"
core(s) per socket: 48

# Calculate peak performance:
Peak FLOPs = cores × frequency × FLOPs/cycle
          = 48 × 3.0 GHz × 32 (AVX-512) × 2 (FMA)
          = 9.2 TFLOP/s = 9,200 GFLOP/s

# Memory bandwidth (from spec or benchmark)
Peak memory bandwidth = ~120 GB/s (DDR4-2933, 6 channels)
```

### Step 2: Measure CFD Code Performance

```bash
$ perf stat -e cycles,instructions,fp_arith_inst_retired.512b_packed_double simpleFoam

   12,345,678,901      cycles
    8,234,567,890      instructions
       45,678,901      fp_arith_inst_retired.512b_packed_double

# Calculate FLOPs (8 FLOPs per 512b packed double operation):
FLOPs = 45.678M × 8 = 365.4 MFLOPs

# Time = 60 seconds
Achieved performance = 365.4 MFLOPs / 60 s = 6.09 GFLOP/s
```

### Step 3: Calculate Arithmetic Intensity

```
Arithmetic Intensity (AI) = FLOPs / Bytes accessed

# Measure memory traffic with perf:
$ perf stat -e cache-references,cycles,L1-dcache-loads
     52,345,678,901      cache-references

# Assuming 8 bytes per reference (double precision):
Bytes accessed ≈ 52.3B × 8 = 418 GB

AI = 365.4 MFLOPs / 418 GB
  = 0.000874 GFLOPs/GB
  = 0.874 FLOPs/byte
```

### Step 4: Plot on Roofline

```
Performance (GFLOP/s)
    │
9200├│                                    ← Peak compute
    ││
    ││
    ││                                    ← Ridge point
    ││                               AI = 9200/120 = 77
 120├──────────────────────────────────●──────────────
    ││                                │
    ││                                │ Memory bound
 6.1├────────────────────────────●─────│──────────────
    ││                            │     │
    ││        simpleFoam here    │     │
    ││          (AI = 0.874)      │     │
    └────────────────────────────┼─────┴──────────────
                                0.874   77
                                Arithmetic Intensity (FLOPs/byte)
```

**Interpretation:**
- **AI = 0.874** << 77 (ridge point) → **Memory bound**
- Operating at **6.1 / 120 = 5%** of memory bandwidth limit
- **Optimization strategy:** Focus on cache efficiency, not compute optimization

---

## Real Cache Optimization Scenarios

### Scenario 1: Face Loop Random Access

**Problem:**
```cpp
// OpenFOAM fvMatrix::assemble (simplified)
forAll(owner, facei)
{
    label own = owner[facei];      // Sequential → cache hit
    label nei = neighbour[facei];  // Sequential → cache hit
    
    result[own] += flux[facei];    // Random → cache miss!
    result[nei] -= flux[facei];    // Random → cache miss!
}
```

**Diagnosis:**
```bash
$ perf stat -e L1-dcache-load-misses,L1-dcache-loads simpleFoam
     150M      L1-dcache-loads
      45M      L1-dcache-load-misses     # 30% miss rate → BAD!
```

**Optimization 1: Mesh Reordering**
```bash
# Use Cuthill-McKee to reduce bandwidth
renumberMesh -method CuthillMcKee

# Result:
$ perf stat -e L1-dcache-load-misses,L1-dcache-loads simpleFoam
     150M      L1-dcache-loads
      12M      L1-dcache-load-misses     # 8% miss rate ← 3.75x better!
```

**Optimization 2: Manual Prefetching (Advanced)**
```cpp
#include <xmmintrin.h>

forAll(mesh.owner(), facei)
{
    // Prefetch next iteration's data
    label next_nei = (facei + 1 < nFaces) ? neighbour[facei + 1] : -1;
    if (next_nei >= 0)
        _mm_prefetch(&Cc[next_nei], _MM_HINT_T0);  // Prefetch to L1
    
    label nei = neighbour[facei];
    // ... rest of loop body
}

// Result: 6% miss rate (2.5x better than baseline)
```

**Performance Improvement:**
```
Before: ClockTime = 850 s, cache miss rate = 30%
After (reorder): ClockTime = 720 s, cache miss rate = 8%
Speedup: 1.18x (15% faster)

After (prefetch): ClockTime = 690 s, cache miss rate = 6%
Speedup: 1.23x (23% faster total)
```

### Scenario 2: Temporary Field Allocations

**Bad Code (Cache Pollution):**
```cpp
volScalarField result = sqr(T) + 2.0 * T + 1.0;

// Memory allocation sequence:
// 1. Allocate temp1 for sqr(T) result
// 2. Allocate temp2 for 2.0 * T
// 3. Allocate temp3 for temp1 + temp2
// 4. Allocate temp4 for temp3 + 1.0
// 5. Copy temp4 to result
// Total: 5 allocations, 4 copies!
```

**Measured Impact:**
```bash
$ perf stat -e cache-references,cache-misses simpleFoam
     85.2 M/sec    cache-references
      6.8 M/sec    cache-misses         # 7.98% miss rate

# Each temporary allocation pollutes cache
# Cache thrashing between temporaries
```

**Good Code (Expression Templates):**
```cpp
// OpenFOAM uses expression templates automatically
volScalarField result = sqr(T) + 2.0*T + 1.0;

// Compiler transforms to:
forAll(T, i)
{
    result[i] = sqr(T[i]) + 2.0*T[i] + 1.0;  // Single loop!
}
// Zero intermediate allocations
```

**Measured Improvement:**
```bash
$ perf stat -e cache-references,cache-misses simpleFoam
     82.1 M/sec    cache-references  ← Fewer refs (4% reduction)
      1.2 M/sec    cache-misses      # 1.46% miss rate ← 5.4x better!
```

**Performance:**
```
Before: 850 s, 7.98% cache miss rate
After: 780 s, 1.46% cache miss rate
Speedup: 1.09x (9% faster from cache improvement alone)
```

### Scenario 3: AoS vs SoA for Gradient Calculation

**AoS (OpenFOAM default):**
```cpp
// Gradient calculation (component-wise)
forAll(owner, facei)
{
    label own = owner[facei];
    label nei = neighbour[facei];
    
    vector delta = C[nei] - C[own];  // Load x,y,z for both cells
    grad[own].x() += delta.x() * Sf[facei].x();  // Use only x
    grad[own].y() += delta.y() * Sf[facei].y();  // Use only y
    grad[own].z() += delta.z() * Sf[facei].z();  // Use only z
}

// Cache utilization: 33% (load x,y,z, use one component at a time)
```

**Measured Performance:**
```bash
$ perf stat -e L1-dcache-loads,L1-dcache-load-misses simpleFoam
     500M      L1-dcache-loads
     125M      L1-dcache-load-misses    # 25% miss rate
```

**SoA Alternative:**
```cpp
// Custom SoA implementation
struct VectorField {
    scalarList x, y, z;
};

// Separate loops per component
forAll(owner, facei)
{
    gradX[owner[facei]] += (C.x[neighbour[facei]] - C.x[owner[facei]]) * Sf.x[facei];
}
// Repeat for y and z components

// Cache utilization: 100% (sequential access to x arrays)
```

**Measured Improvement:**
```bash
$ perf stat -e L1-dcache-loads,L1-dcache-load-misses customSolver
     480M      L1-dcache-loads
      72M      L1-dcache-load-misses    # 15% miss rate ← 1.67x better!
```

**Trade-off Analysis:**
```
AoS: 25% miss rate, simpler code, 3 memory passes (one per component)
SoA: 15% miss rate, complex code, 3 memory passes (same)

Conclusion: SoA not worth it for this case
Better optimization: mesh reordering (reduces to 8% miss rate)
```

---

## Cache Optimization Checklist

Use this checklist when optimizing OpenFOAM code for cache performance:

### Data Layout
- [ ] Profile cache misses before optimizing (`perf stat -e cache-misses`)
- [ ] Consider AoS vs SoA based on access pattern
- [ ] Align hot data structures to 64-byte cache lines
- [ ] Minimize struct size (remove unused fields)

### Loop Optimization
- [ ] Verify inner loop accesses memory sequentially
- [ ] Loop order: rows first, then columns (for row-major storage)
- [ ] Avoid pointer chasing in hot loops
- [ ] Use `forAll` macros instead of raw indexing when possible

### Memory Allocation
- [ ] Eliminate temporary field allocations (use `tmp<>`)
- [ ] Prefer expression templates over explicit temporaries
- [ ] Reuse buffers instead of reallocating
- [ ] Use in-place operations when possible (`field *= 2.0`)

### Mesh-Specific
- [ ] Apply mesh reordering for large cases (`renumberMesh -method CuthillMcKee`)
- [ ] Profile mesh bandwidth impact on cache misses
- [ ] Consider cell zoning for cache-local regions

### Measurement
- [ ] Measure AMAT (Average Memory Access Time)
- [ ] Plot on roofline model to identify bottleneck
- [ ] Verify optimization with realistic data sizes
- [ ] Compare before/after with actual CFD cases, not micro-benchmarks

### Common Pitfalls
- [ ] Don't optimize cold paths (non-performance-critical code)
- [ ] Avoid premature SoA conversion without profiling
- [ ] Don't over-align (wastes memory, reduces effective cache)
- [ ] Remember: cache optimization is context-dependent

---

## Practical Tips

### 1. Keep Hot Data Small

```cpp
// Bad: store extra info in hot structure
struct Cell {
    scalar p, T, k, epsilon;
    scalar debug1, debug2;  // Wasted cache space!
    label id;               // Rarely used
};

// Good: minimal storage for hot path
struct Cell {
    scalar p, T, k, epsilon;  // Only essential fields
};

// Move rarely-used data to separate structure
struct CellDebug {
    scalar debug1, debug2;
    label id;
};
```

**Impact:** 25% smaller struct → 25% more data fits in cache

### 2. Avoid Pointer Chasing

```cpp
// Bad: 3 levels of indirection
for (label i = 0; i < n; ++i)
{
    result[i] = data[indices[pointers[i]]];  // Cache miss chain!
}

// Better: restructure data (if possible)
for (label i = 0; i < n; ++i)
{
    result[i] = sortedData[i];  // Single lookup
}

// Best: if restructuring not possible, prefetch
for (label i = 0; i < n; ++i)
{
    label nextIdx = (i + 1 < n) ? indices[pointers[i + 1]] : 0;
    _mm_prefetch(&data[nextIdx], _MM_HINT_T0);
    
    result[i] = data[indices[pointers[i]]];
}
```

### 3. Align Data to Cache Lines

```cpp
// C++17 aligned allocation
alignas(64) scalar buffer[1024];  // Aligned to cache line boundary

// For dynamic allocation:
scalar* buffer = static_cast<scalar*>(aligned_alloc(64, 1024 * sizeof(scalar)));

// Benefit: Ensures data doesn't span cache lines → fewer misses
```

### 4. Use Cache-Aware Algorithms

```cpp
// Bad: Standard matrix multiplication (cache-unfriendly)
for (int i = 0; i < N; i++)
    for (int j = 0; j < N; j++)
        for (int k = 0; k < N; k++)
            C[i][j] += A[i][k] * B[k][j];  // Random access to B[k][j]

// Good: Cache-oblivious algorithm or blocking
const int BLOCK = 64;  // Fits in L1 cache
for (int ii = 0; ii < N; ii += BLOCK)
    for (int jj = 0; jj < N; jj += BLOCK)
        for (int kk = 0; kk < N; kk += BLOCK)
            // Blocked multiplication (cache-friendly)
            for (int i = ii; i < min(ii+BLOCK, N); i++)
                for (int j = jj; j < min(jj+BLOCK, N); j++)
                    for (int k = kk; k < min(kk+BLOCK, N); k++)
                        C[i][j] += A[i][k] * B[k][j];

// Speedup: 2-4x for large matrices
```

---

## Measuring Tools

### perf (Linux)

```bash
# Cache miss statistics
perf stat -e cache-misses,cache-references simpleFoam

# Detailed cache breakdown
perf stat -e L1-dcache-loads,L1-dcache-load-misses,L1-icache-loads,L1-icache-load-misses simpleFoam

# TLB misses (translation lookaside buffer)
perf stat -e dTLB-loads,dTLB-load-misses simpleFoam

# Record and analyze hot spots
perf record -g simpleFoam
perf report
```

### likwid-perfctr (Advanced)

```bash
# More detailed cache metrics
likwid-perfctr -C 0 -g CACHE simpleFoam

# Memory bandwidth
likwid-perfctr -C 0 -g MEM simpleFoam

# Output includes:
# - L1/L2/L3 cache hit ratios
# - Data/instruction breakdown
# - Memory bandwidth utilization
```

### valgrind (cachegrind)

```bash
# Simulate cache behavior
valgrind --tool=cachegrind simpleFoam

# Analyze results
cg_annotate cachegrind.out.<pid>

# Output:
# - Ir: Instruction reads
# - I1mr: L1 instruction miss rate
# - Dr: Data reads
# - D1mr/D1mw: L1 data miss rates
```

---

## Key Takeaways

1. **Cache is Critical:** 50x speed difference between L1 hit and RAM access
2. **Measure First:** Use `perf stat -e cache-misses` to diagnose before optimizing
3. **AMAT Calculation:** Quantify impact with Average Memory Access Time formula
4. **Access Pattern Matters:** Sequential access = fast, random access = slow
5. **Roofline Model:** Identify if code is compute-bound or memory-bound
6. **OpenFOAM Context:** FVM inherently has random cell access, but mesh reordering helps
7. **AoS vs SoA:** Choose based on access pattern, not hype (AoS is often better for FVM)
8. **Avoid Temporaries:** Use expression templates and `tmp<>` to prevent cache pollution
9. **Real-World Impact:** Cache optimization typically yields 10-30% speedup in OpenFOAM
10. **Common Pitfalls:** Don't optimize cold paths, avoid premature SoA, profile with realistic data

---

## Concept Check

<details>
<summary><b>1. ทำไม OpenFOAM ใช้ AoS เป็น default?</b></summary>

**AoS (Array of Structs) สำหรับ Vector fields:**

```cpp
volVectorField U;  // [xyz][xyz][xyz]...
```

**เหตุผล:**
- FVM access pattern: ต้องการ U.x(), U.y(), U.z() พร้อมกันต่อ cell
- Natural for physics: velocity คือ vector ไม่ใช่ 3 scalars แยกกัน
- Cache utilization = 100% เมื่อ access ทุก components
- Code ง่ายและอ่านได้กว่า SoA

**Trade-off:**
- Component-only operations (เช่น `Ux = a * Ux`) อาจใช้ cache ได้น้อยกว่า
- แต่ส่วนใหญ่ FVM operations ใช้ทุก components พร้อมกัน

**Conclusion:** AoS เหมาะกับ OpenFOAM เพราะ match กับ FVM pattern
</details>

<details>
<summary><b>2. ทำไม face loop ใน OpenFOAM มี cache miss เยอะ?</b></summary>

```cpp
forAll(owner, facei)
{
    result[owner[facei]] += ...;  // Random cell access
    result[neighbour[facei]] -= ...;  // Random cell access
}
```

**Problem:**
- `owner[facei]` ไม่ sequential (random cell indices)
- Cell ที่ access อาจไกลกันใน memory
- แต่ละ access อาจ miss cache (30% miss rate พบได้บ่อย)

**Why Unavoidable:**
- Finite Volume Method ต้องการ face connectivity
- Mesh topology ไม่ได้สร้างมาเพื่อ cache locality
- face ที่ติดกันใน mesh อาจ connect กับ cell ที่ไกลกัน

**Mitigation Strategies:**
1. **Mesh reordering** (Cuthill-McKee): เรียง cell index ให้ sequential
   - ลด cache miss rate จาก 30% → 8%
2. **Accept trade-off:** FVM inherently random access
   - Optimize hot paths only
3. **Increase cache size:** Hardware solution
   - L3 cache ช่วย reduce miss rate

**Measured Impact:**
```
Before renumbering: 30% L1 miss rate
After Cuthill-McKee: 8% L1 miss rate
Speedup: 1.18x
```
</details>

<details>
<summary><b>3. Roofline model บอกอะไรเรา?</b></summary>

**Roofline Model = Performance Limits Chart**

```
Performance (GFLOP/s)
    │
Peak├────────────────────────────
    │                          ╱
    │                      Memory bound
    │                    ╱
    │                ╱
    │            ╱   ← Ridge point
    │        ╱
Ridge├────────────────────────────
    │    ╲ Compute bound
    │    ╲
    └────┴─────────────────────────
         Arithmetic Intensity
```

**What it tells you:**
1. **Identify Bottleneck:**
   - Left of ridge → Memory bound (limited by bandwidth)
   - Right of ridge → Compute bound (limited by FLOPs)

2. **Optimization Strategy:**
   - Memory bound: Focus on cache optimization, data layout
   - Compute bound: Focus on vectorization, parallelization

3. **Headroom:**
   - Distance from roofline = potential improvement
   - Near ridge = balanced code

**OpenFOAM Example:**
```
Measured: AI = 0.874 FLOPs/byte, Ridge = 77
→ Memory bound (far left of ridge)
→ Optimization: Cache efficiency, not more FLOPs
→ Achieved: 6.1 GFLOP/s, Peak memory: 120 GB/s → 5% utilization
```

**Key Insight:** Don't optimize compute if code is memory-bound!
</details>

---

## Exercises

### Exercise 1: Measure Cache Performance

**Task:** Profile cache behavior of your OpenFOAM case

```bash
# 1. Run your case with perf
simpleFoam &
PID=$!
perf stat -e cache-references,cache-misses,L1-dcache-loads,L1-dcache-load-misses -p $PID -- sleep 30

# 2. Calculate metrics
# - Overall cache miss rate = cache-misses / cache-references
# - L1 miss rate = L1-dcache-load-misses / L1-dcache-loads
# - AMAT = 4 + (L1_miss_rate × 12) + ...

# 3. Compare with baseline
# Target: < 5% overall cache miss rate
```

**Questions:**
1. What is your cache miss rate?
2. Is your code memory-bound or compute-bound?
3. Which optimization would help most?

### Exercise 2: Compare AoS vs SoA

**Task:** Benchmark cache performance of different layouts

```cpp
// Test 1: AoS (OpenFOAM default)
volVectorField U(mesh);
forAll(U, i)
{
    scalar magU = mag(U[i]);  // Access x, y, z
}

// Test 2: Simulated SoA (component-wise)
volScalarField Ux = U.component(0);
volScalarField Uy = U.component(1);
volScalarField Uz = U.component(2);

forAll(Ux, i)
{
    scalar sumX = Ux[i];  // Access only x
}

// Measure:
perf stat -e cache-misses yourTest
```

**Analysis:**
1. Which layout has fewer cache misses for your access pattern?
2. Does the performance difference justify code complexity?
3. When would SoA be worth implementing?

### Exercise 3: Optimize Loop Ordering

**Task:** Find and fix cache-unfriendly loops

```cpp
// Bad: Column-major access
for (label j = 0; j < nCols; ++j)
    for (label i = 0; i < nRows; ++i)
        result[i][j] = matrix[i][j] * vector[j];

// TODO: Rewrite for cache efficiency
// Hint: Change loop order
```

**Solution:**
```cpp
// Good: Row-major access
for (label i = 0; i < nRows; ++i)
{
    scalar sum = 0;
    for (label j = 0; j < nCols; ++j)
        sum += matrix[i][j] * vector[j];
    result[i] = sum;
}
```

**Benchmark:**
```bash
# Compare performance
perf stat -e cycles,instructions cache-bad
perf stat -e cycles,instructions cache-good

# Expected: 2-5x speedup for large matrices
```

### Exercise 4: Mesh Reordering Impact

**Task:** Measure cache improvement from mesh renumbering

```bash
# 1. Run baseline
blockMesh
simpleFoam > baseline.log
perf stat -e cache-misses simpleFoam > baseline_perf.log

# 2. Renumber mesh
renumberMesh -method CuthillMcKee
simpleFoam > renumbered.log
perf stat -e cache-misses simpleFoam > renumbered_perf.log

# 3. Compare results
grep "cache-misses" baseline_perf.log renumbered_perf.log
grep "ClockTime" baseline.log renumbered.log
```

**Expected Results:**
- Cache miss rate: 7-8% → 2-3% (3x better)
- Runtime: 10-20% faster
- Mesh bandwidth: significantly reduced

---

## Summary Checklist

**Pre-Optimization:**
- [ ] Profile cache misses with `perf stat -e cache-misses`
- [ ] Calculate AMAT to quantify impact
- [ ] Plot on roofline model to identify bottleneck
- [ ] Verify mesh bandwidth impact

**Optimization Techniques:**
- [ ] Use AoS for per-element operations (OpenFOAM default)
- [ ] Consider SoA for component-only loops
- [ ] Ensure inner loops access sequential memory
- [ ] Eliminate temporary field allocations
- [ ] Apply mesh reordering (Cuthill-McKee)
- [ ] Align hot data to cache lines (64 bytes)

**Post-Optimization:**
- [ ] Re-measure cache miss rate (target: < 5%)
- [ ] Verify runtime improvement
- [ ] Check roofline model position
- [ ] Document trade-offs

**Common Pitfalls to Avoid:**
- [ ] Don't optimize cold paths
- [ ] Don't convert to SoA without profiling
- [ ] Don't over-align data
- [ ] Don't trust micro-benchmarks (use realistic data)
- [ ] Don't forget mesh topology constraints

---

## References and Further Reading

### OpenFOAM Documentation
- **Next:** [Loop Optimization](03_Loop_Optimization.md) - Advanced loop transformations
- **Previous:** [Profiling Tools](01_Profiling_Tools.md) - Performance measurement basics

### Module Dependencies
- **Required:** Memory Management fundamentals (Module 09)
- **Related:** Design Patterns (Module 09) - CRTP for expression templates
- **Applied:** CFD Engine Development (Module 10) - fvMatrix internals

### External Resources
1. **Hennessy & Patterson:** "Computer Architecture: A Quantitative Approach" - Cache theory
2. **Williams et al.:** "Roofline: An insightful visual performance model" - Original roofline paper
3. **Intel VTune:** Profiling tool documentation
4. **Cuthill-McKee Algorithm:** Mesh reordering for bandwidth reduction

### Tools
- `perf stat -e cache-misses,cache-references` - Basic cache profiling
- `perf record -g` - Hot spot analysis
- `likwid-perfctr` - Detailed hardware counters
- `valgrind --tool=cachegrind` - Cache simulation
- `renumberMesh` - OpenFOAM mesh reordering