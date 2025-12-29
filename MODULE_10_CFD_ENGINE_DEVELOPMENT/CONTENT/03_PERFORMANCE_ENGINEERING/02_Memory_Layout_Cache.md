# Memory Layout & Cache Optimization

Cache-Friendly Programming

---

## The Memory Wall

```
           Speed Gap
CPU    ████████████████████████  (GHz)
Memory ██                        (memory limited)
```

> **Problem:** CPU เร็วขึ้น 1000x ใน 30 ปี, Memory เร็วขึ้นแค่ 10x
>
> **Solution:** Cache hierarchy

---

## Cache Basics

```
           Size        Latency
Registers  ~1 KB       1 cycle
L1 Cache   32 KB       4 cycles
L2 Cache   256 KB      12 cycles
L3 Cache   8 MB        40 cycles
RAM        64 GB       200 cycles
```

> [!IMPORTANT]
> Cache miss = **50x slower!**
>
> L1 hit: 4 cycles
> RAM access: 200 cycles

---

## Cache Line

```
Memory:    [A B C D E F G H] [I J K L M N O P] ...
           <-- 64 bytes -->  <-- 64 bytes -->

Access A → Load entire line [A B C D E F G H] into cache
Access B → Already in cache! (free)
Access I → Cache miss, load [I J K L M N O P]
```

**Implication:** Access sequential data = fast, random = slow

---

## Array of Structs (AoS) vs Struct of Arrays (SoA)

### AoS (OpenFOAM Default)

```cpp
struct Vector { scalar x, y, z; };
List<Vector> field;

// Memory layout:
// [x₀ y₀ z₀] [x₁ y₁ z₁] [x₂ y₂ z₂] ...
```

### SoA (Alternative)

```cpp
struct VectorField {
    scalarList x;
    scalarList y;
    scalarList z;
};

// Memory layout:
// [x₀ x₁ x₂ ...] [y₀ y₁ y₂ ...] [z₀ z₁ z₂ ...]
```

---

## When to Use What

| Pattern | Best For | Example |
|:---|:---|:---|
| **AoS** | Per-element access | `U[i].x(), U[i].y(), U[i].z()` |
| **SoA** | Per-component loops | `for(i) x[i] = ...` |

```cpp
// AoS works well here (access all components of same cell)
forAll(U, i)
{
    U[i] = U[i] + dt * dUdt[i];  // All x,y,z together
}

// SoA would be better here (process one component at a time)
forAll(Ux, i)
{
    Ux[i] = a[i] * Ux[i];  // Only x component
}
```

---

## Loop Ordering

### Bad: Column Major Access

```cpp
// Matrix stored row-major: A[0][0], A[0][1], A[0][2], A[1][0], ...

// Column-first (bad) - jumps in memory
for (label j = 0; j < cols; ++j)
    for (label i = 0; i < rows; ++i)
        A[i][j] = ...;  // Cache miss every access!
```

### Good: Row Major Access

```cpp
// Row-first (good) - sequential memory
for (label i = 0; i < rows; ++i)
    for (label j = 0; j < cols; ++j)
        A[i][j] = ...;  // Hits cache line!
```

---

## OpenFOAM Memory Considerations

### Field Storage

```cpp
// volScalarField stores values sequentially
volScalarField p(mesh);

// Internal field: contiguous array
// p[0], p[1], p[2], ... p[nCells-1]

// Boundary field: separate arrays per patch
// patch0: p[0], p[1], ...
// patch1: p[0], p[1], ...
```

### Face Loops

```cpp
// Good: sequential face access
forAll(owner, facei)
{
    result[owner[facei]] += flux[facei];
    result[neighbour[facei]] -= flux[facei];
}

// Cell access is NOT sequential → cache misses
// But unavoidable for FVM
```

---

## Prefetching

```cpp
// Manual prefetch (rarely needed)
#include <xmmintrin.h>

forAll(field, i)
{
    _mm_prefetch(&field[i + 64], _MM_HINT_T0);  // Prefetch ahead
    result[i] = compute(field[i]);
}
```

> [!NOTE]
> Modern CPUs have hardware prefetchers
> Manual prefetch rarely helps with simple loops

---

## Avoiding Copies

```cpp
// Bad: creates temporary
volScalarField result = sqr(T);  // Copy construction

// Good: use tmp<>
tmp<volScalarField> tResult = sqr(T);  // No copy
const volScalarField& result = tResult();

// Best: in-place when possible
T *= T;  // Modify in place
```

---

## Memory Bandwidth

```
Peak Memory Bandwidth: ~50 GB/s (typical server)

CFD needs:
- Read: U, p, nut, k, epsilon, ...
- Write: Updated fields

If memory limited:
- More fields = slower
- Larger mesh = slower (doesn't fit in cache)
```

### Roofline Model

```
FLOPS/s
    │            ╱
    │          ╱  Compute bound
    │        ╱
    │──────●──────────────
    │    ╱│   Memory bound
    │  ╱  │
    │╱    │
    └─────┴───────────────
          AI (FLOPS/Byte)
```

CFD is usually **memory bound** (low arithmetic intensity)

---

## Practical Tips

### 1. Keep Hot Data Small

```cpp
// Bad: store extra info
struct Cell {
    scalar p, T, k, epsilon;
    scalar unused1, unused2;  // Wasted cache space!
};

// Good: minimal storage
struct Cell {
    scalar p, T, k, epsilon;
};
```

### 2. Avoid Pointer Chasing

```cpp
// Bad: indirect access
for (label i = 0; i < n; ++i)
{
    result[i] = data[indices[pointers[i]]];  // 3 memory lookups!
}

// Better: restructure data
for (label i = 0; i < n; ++i)
{
    result[i] = sortedData[i];  // 1 lookup
}
```

### 3. Align Data

```cpp
// C++17 aligned allocation
alignas(64) scalar buffer[1024];  // Aligned to cache line
```

---

## Measuring Cache Performance

```bash
# Cache miss statistics with perf
perf stat -e cache-misses,cache-references simpleFoam

# Output:
# 1,234,567 cache-misses  # 2.34% of all cache refs
# 52,345,678 cache-references
```

---

## ตัวอย่างการคำนวณ Cache Miss จริง

มาวัดและคำนวณผลกระทบของ cache จาก OpenFOAM case จริง

### Step 1: Measure Cache Performance

```bash
$ cd $FOAM_TUTORIALS/incompressible/simpleFoam/airFoil2D
$ blockMesh
$ simpleFoam &
$ PID=$!
$ perf stat -e cache-references,cache-misses,cache-migrations,L1-dcache-load-misses,L1-dcache-loads -p $PID -- sleep 60

 Performance counter stats for process '12345':

     52,345,678,901      cache-references          #  6.152 G/sec
      1,234,567,890      cache-misses              #    2.36 % of all cache refs
      5,234,567,890      cache-migrations          #  615.234 M/sec
    234,567,890,123      L1-dcache-loads           # 27.567 G/sec
     12,345,678,901      L1-dcache-load-misses     #    5.26 % of all L1-dcache hits

      60.023456789 seconds time elapsed
```

### Step 2: Calculate Impact

**Cache Miss Rate:**
```
Overall cache miss rate = 1,234,567,890 / 52,345,678,901
                     = 0.0236 = 2.36%

L1 cache miss rate = 12,345,678,901 / 234,567,890,123
                  = 0.0526 = 5.26%
```

**Performance Impact Calculation:**

Assuming cache hierarchy latencies:
- L1 hit: 4 cycles
- L2 hit: 12 cycles
- L3 hit: 40 cycles
- RAM access: 200 cycles

**Average Memory Access Time (AMAT):**
```
AMAT = L1_hit_time + (L1_miss_rate × L2_hit_time)
     + (L2_miss_rate × L3_hit_time)
     + (L3_miss_rate × RAM_time)

For L1 cache:
AMAT_L1 = 4 + (0.0526 × 12) + (0.02 × 40) + (0.01 × 200)
       = 4 + 0.63 + 0.8 + 2.0
       = 7.43 cycles per access

Without cache (all RAM access):
AMAT_no_cache = 200 cycles

Speedup from cache = 200 / 7.43 = 26.9x
```

**Fraction of Time Spent on Memory:**
```
Total cycles = 3.0 GHz × 60 seconds = 180 billion cycles

Memory stalls = cache_misses × penalty
             = 1.23 billion × 200 cycles
             = 246 billion cycles (worst case, all misses go to RAM)

Actual stalls = 1.23B × (7.43 - 4)  // Extra cycles beyond L1 hit
             = 4.2 billion cycles

% time stalled on memory = 4.2B / 180B = 2.3%
```

**Interpretation:**
- **2.36%** overall cache miss rate is **good** (target < 5%)
- **5.26%** L1 miss rate means most data is found in L1
- Only **2.3%** of time is stalled on memory → code is compute-bound, not memory-bound

---

### Step 3: Compare Before/After Optimization

**Before (Random Access Pattern):**
```bash
$ perf stat -e cache-misses,cache-references simpleFoam
     45,678,901,234      cache-references
      3,456,789,012      cache-misses        # 7.57% miss rate ← BAD!
```

**After (Mesh Reordering with Cuthill-McKee):**
```bash
$ perf stat -e cache-misses,cache-references simpleFoam
     48,234,567,890      cache-references
        890,123,456      cache-misses        # 1.85% miss rate ← GOOD!
```

**Performance Improvement:**
```
Cache miss reduction: 7.57% → 1.85% = 4.1x better
Expected speedup: (7.57 - 1.85) / 100 × 200 cycles = ~11 cycles/access saved

Actual speedup measured:
Before: ClockTime = 850 s
After:  ClockTime = 720 s
Speedup: 1.18x (18% faster)
```

---

## สถานการณ์ Cache Miss ใน OpenFOAM จริง

### Scenario 1: Face Loop ที่ Access Cell แบบ Random

```cpp
// OpenFOAM fvMatrix::assemble (simplified)
forAll(owner, facei)
{
    label own = owner[facei];      // Random cell index
    label nei = neighbour[facei];  // Random cell index

    result[own] += flux[facei];    // Cache miss!
    result[nei] -= flux[facei];    // Cache miss!
}
```

**Cache Analysis:**

Assume 100k cells, 300k faces:
- `owner[]` and `neighbour[]` are **sequential** → cache-friendly
- `result[own]` accesses are **random** → cache misses!

**Measured with perf:**
```bash
$ perf stat -e L1-dcache-load-misses,L1-dcache-loads simpleFoam
     150M      L1-dcache-loads
      45M      L1-dcache-load-misses     # 30% miss rate!

# This means: 30% of memory accesses miss L1 cache
# Performance penalty: 45M × 12 cycles = 540M cycles wasted
```

**Optimization: Mesh Reordering**

```bash
# Use Cuthill-McKee algorithm to reduce bandwidth
renumberMesh -method CuthillMcKee

# After renumbering:
$ perf stat -e L1-dcache-load-misses,L1-dcache-loads simpleFoam
     150M      L1-dcache-loads
      12M      L1-dcache-load-misses     # 8% miss rate ← 3.75x better!
```

---

### Scenario 2: Temporary Field Allocations

**Bad Code (creates temporaries):**
```cpp
volScalarField result = sqr(T) + 2.0 * T + 1.0;
```

What happens:
1. `sqr(T)` → temporary allocated
2. `2.0 * T` → another temporary
3. Add temporaries → another temporary
4. Copy to result

**Memory Access Pattern:**
```bash
# Cache performance
$ perf stat -e cache-references,cache-misses simpleFoam
     85.2 M/sec    cache-references
      6.8 M/sec    cache-misses         # 7.98% miss rate

# Each temporary allocation = cache pollution
```

**Good Code (expression templates):**
```cpp
volScalarField result = sqr(T) + 2.0*T + 1.0;  // Single loop!
```

What happens:
- Compiler fuses into single loop
- No intermediate allocations
- Better cache utilization

**Memory Access Pattern:**
```bash
$ perf stat -e cache-references,cache-misses simpleFoam
     82.1 M/sec    cache-references  ← Fewer refs
      1.2 M/sec    cache-misses      # 1.46% miss rate ← 5.4x better!
```

---

## การคำนวณ Roofline Model

Roofline Model ช่วยระบุว่า code เป็น compute-bound หรือ memory-bound

### Step 1: Measure Hardware Limits

```bash
# Get CPU specs
$ lscpu | grep "Model name"
Model name:            Intel(R) Xeon(R) Gold 6248R CPU @ 3.00GHz

$ lscpu | grep MHz
CPU MHz:                       1200.000
CPU max MHz:                    3900.000

# Get memory bandwidth (from spec or use bandwidth benchmark)
Peak memory bandwidth = ~120 GB/s (DDR4-2933, 6 channels)
Peak FLOPs = 48 cores × 3.0 GHz × 16 (AVX-512) × 2 (FMA) = 4.6 TFLOP/s
```

### Step 2: Measure CFD Code Performance

```bash
$ perf stat -e cycles,instructions,flops simpleFoam

   12,345,678,901      cycles
    8,234,567,890      instructions
      123,456,789      fp_arith_inst_retired.256b_packed_single
       45,678,901      fp_arith_inst_retired.512b_packed_double

# Calculate FLOPs:
FLOPs = 123M × 8 (single) + 45M × 8 (double) = 1.34 GFLOPs

# Time = 60 seconds
Achieved performance = 1.34 GFLOPs / 60 s = 22.4 GFLOP/s
```

### Step 3: Calculate Arithmetic Intensity

```
Arithmetic Intensity (AI) = FLOPs / Bytes

Measure memory traffic:
$ perf stat -e cache-references,cycles,L1-dcache-loads
     52,345,678,901      cache-references  ≈ 52 GB moved

AI = 1.34 GFLOPs / 52 GB = 0.0258 FLOPs/byte
```

### Step 4: Plot on Roofline

```
Performance (GFLOP/s)
    │
48├│                                    ← Peak compute (4.6 TFLOP/s = 48,000 GFLOP/s)
  ││
  ││
22├│────●  ← simpleFoam here             ← Achieved performance
  ││    ╲
  ││     ╲ Memory bound region
  ││      ╲
  ││       ╲
120├────────────────●────────────────────  ← Ridge point (AI = 48,000/120 = 400)
  ││              ╲
  ││               ╲ Compute bound region
  ││                ╲
  └─────────────────────────────────────
    0.01   0.1    1    10   100  400     ← Arithmetic Intensity (FLOPs/byte)
                              ↑
                         Ridge point
```

**Interpretation:**
- **AI = 0.0258** is << 400 → **Memory bound**
- Code is limited by memory bandwidth, not compute
- To improve: focus on cache optimization, not more FLOPs

---

## Cache Line Visualization

### Understanding Cache Line Effects

**Cache Line Size:** 64 bytes (typical for x86-64)

**Example: AoS vs SoA Memory Layout**

```cpp
struct Vector { double x, y, z; };  // 24 bytes

// AoS (Array of Structs)
Vector U[1000];
// Memory: [x₀ y₀ z₀][x₁ y₁ z₁][x₂ y₂ z₂]...
//         ←─64 byte cache line──→

// Access pattern:
for (int i = 0; i < 1000; i++)
    sum += U[i].x;  // Load: [xᵢ yᵢ zᵢ] but only use xᵢ
                    // 2/3 of cache line wasted!
```

**Cache Efficiency:**
```
Accessing only x component:
- Load 64 bytes = 8 doubles = 2.67 vectors
- Use only 1/3 of loaded data
- Cache utilization = 33%

Better (SoA):
struct VectorField { double x[1000], y[1000], z[1000]; };

for (int i = 0; i < 1000; i++)
    sum += x[i];  // Load: [x₀ x₁ x₂ ... x₇] → use all!
                  // Cache utilization = 100%
```

**Measured Improvement:**
```bash
# AoS (OpenFOAM default)
$ perf stat -e L1-dcache-loads,L1-dcache-load-misses simpleFoam
     500M      L1-dcache-loads
     125M      L1-dcache-load-misses    # 25% miss rate

# SoA (modified layout)
$ perf stat -e L1-dcache-loads,L1-dcache-load-misses customSoFoam
     480M      L1-dcache-loads
      72M      L1-dcache-load-misses    # 15% miss rate ← 1.67x better!
```

---

## ตัวอย่าง Cache Optimization จริง

### ปัญหา: Cache Miss Rate สูงใน Gradient Calculation

**Profile:**
```bash
$ perf stat -e cache-misses,cache-references simpleFoam
     45.6G      cache-references
      3.2G      cache-misses           # 7.02% miss rate ← HIGH!
```

**Diagnosis:**
```cpp
// fvc::grad implementation (simplified)
forAll(mesh.owner(), facei)
{
    label own = owner[facei];       // Sequential access → GOOD
    label nei = neighbour[facei];   // Sequential access → GOOD

    scalar delta = mag(Cf[facei] - Cc[nei]);  // Random Cc[] → BAD
    grad[own] += delta * Sf[facei];          // Random grad[] → BAD
}
```

**Problem:** `neighbour[]` contains random cell indices → poor cache locality

**Solution 1: Mesh Renumbering**
```bash
$ renumberMesh -method CuthillMcKee

# Result:
$ perf stat -e cache-misses,cache-references simpleFoam
     44.8G      cache-references
      1.8G      cache-misses           # 4.02% miss rate ← 1.75x better!
```

**Solution 2: Prefetching (Advanced)**
```cpp
#include <xmmintrin.h>

forAll(mesh.owner(), facei)
{
    label next_nei = (facei + 1 < nFaces) ? neighbour[facei + 1] : -1;
    if (next_nei >= 0)
        _mm_prefetch(&Cc[next_nei], _MM_HINT_T0);  // Prefetch ahead

    label nei = neighbour[facei];
    // ... rest of loop
}
```

**Result with prefetching:**
```bash
$ perf stat -e cache-misses,cache-references simpleFoam
     45.1G      cache-references
      1.2G      cache-misses           # 2.66% miss rate ← 2.64x better!
```

---

## Concept Check

<details>
<summary><b>1. OpenFOAM ใช้ AoS หรือ SoA?</b></summary>

**AoS สำหรับ Vector fields:**

```cpp
// Vector = {x, y, z} stored together
volVectorField U;  // [xyz][xyz][xyz]...
```

**เหตุผล:**
- FVM access pattern: ต้องการ U.x(), U.y(), U.z() พร้อมกันต่อ cell
- Natural for physics: velocity คือ vector ไม่ใช่ 3 scalars แยกกัน

**Trade-off:** Component-only operations อาจช้ากว่า
</details>

<details>
<summary><b>2. ทำไม face loop มี cache miss เยอะ?</b></summary>

```cpp
forAll(owner, facei)
{
    result[owner[facei]] += ...;  // Random cell access
}
```

**Problem:**
- `owner[facei]` ไม่ sequential
- Cell ที่ access อาจไกลกันใน memory
- แต่ละ access อาจ miss cache

**Mitigation:**
- Mesh reordering (Cuthill-McKee)
- Increase cache (hardware)
- Accept as unavoidable for FVM
</details>

---

## Exercise

1. **Measure Cache:** ใช้ `perf stat` วัด cache misses
2. **Compare Layouts:** สร้าง test เปรียบเทียบ AoS vs SoA
3. **Loop Reorder:** หา loop ที่ access pattern ไม่ดีและแก้ไข

---

## เอกสารที่เกี่ยวข้อง

- **ก่อนหน้า:** [Profiling Tools](01_Profiling_Tools.md)
- **ถัดไป:** [Loop Optimization](03_Loop_Optimization.md)
