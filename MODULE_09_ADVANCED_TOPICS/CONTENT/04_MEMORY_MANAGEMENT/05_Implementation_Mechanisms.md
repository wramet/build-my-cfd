# Performance Optimization

การปรับปรุงประสิทธิภาพหน่วยความจำ

---

## 🎯 Learning Objectives
เป้าหมายการเรียนรู้

After completing this section, you should be able to:
- **Analyze** cache behavior and memory access patterns in CFD code
- **Apply** profiling tools to identify memory bottlenecks
- **Optimize** memory layout for better cache utilization
- **Tune** memory allocation strategies for performance
- **Measure** the impact of memory optimizations

หลังจากสิ้นสุดส่วนนี้ คุณควรจะสามารถ:
- **วิเคราะห์** พฤติกรรมแคชและรูปแบบการเข้าถึงหน่วยความจำในโค้ด CFD
- **ประยุกต์** เครื่องมือ profiling เพื่อระบุคอขวดหน่วยความจำ
- **ปรับปรุง** เลย์เอาต์หน่วยความจำเพื่อการใช้แคชที่ดีขึ้น
- **ปรับแต่ง** กลยุทธ์การจัดสรรหน่วยความจำเพื่อประสิทธิภาพ
- **วัด** ผลกระทบของการปรับปรุงหน่วยความจำ

---

## Overview

ภาพรวม

> **Performance is not just about algorithms** — memory access patterns matter equally
>
> **ประสิทธิภาพไม่ได้เกี่ยวกับอัลกอริทึมเท่านั้น** — รูปแบบการเข้าถึงหน่วยความจำมีความสำคัญเท่าเทียมกัน

### WHY: Memory Performance in CFD
ทำไม: ประสิทธิภาพหน่วยความจำใน CFD

CFD simulations are memory-bound operations:

การจำลอง CFD เป็นการดำเนินการที่ถูกผูกมัดกับหน่วยความจำ:

- **Memory bandwidth** is often the bottleneck, not CPU cycles
- **Cache misses** can cost 100+ cycles vs 3-4 for L1 hits
- **Memory allocation overhead** impacts solver performance
- **Data layout** determines cache utilization efficiency

- **แบนด์วิดท์หน่วยความจำ** มักเป็นคอขวด ไม่ใช่ CPU cycles
- **Cache misses** อาจมีค่าใช้จ่าย 100+ cycles เทียบกับ 3-4 สำหรับ L1 hits
- **ค่าใช้จ่ายในการจัดสรรหน่วยความจำ** ส่งผลต่อประสิทธิภาพ solver
- **เลย์เอาต์ข้อมูล** กำหนดประสิทธิภาพการใช้แคช

Understanding memory performance is crucial for:
- Reducing simulation runtime through cache optimization
- Scaling efficiently to larger problems
- Minimizing memory allocation overhead
- Writing high-performance OpenFOAM solvers

การทำความเข้าใจประสิทธิภาพหน่วยความจำมีความสำคัญอย่างยิ่งสำหรับ:
- การลดเวลาทำงานของการจำลองผ่านการปรับแต่งแคช
- การขยายขนาดอย่างมีประสิทธิภาพไปยังปัญหาที่ใหญ่ขึ้น
- การลดค่าใช้จ่ายในการจัดสรรหน่วยความจำ
- การเขียน solver OpenFOAM ที่มีประสิทธิภาพสูง

---

## 1. WHEN: Understanding Cache Behavior

เมื่อใด: การทำความเข้าใจพฤติกรรมแคช

### 1.1 Memory Hierarchy

ลำดับชั้นหน่วยความจำ

```cpp
// Latency comparison (approximate cycles)
L1 Cache:  3-4 cycles    // 100x faster than RAM
L2 Cache:  10-15 cycles  // 30x faster than RAM  
L3 Cache:  30-70 cycles  // 10x faster than RAM
Main RAM:  150-300 cycles // Baseline
```

**Key Insight:**
**ข้อเสนอแนะหลัก:**

Cache-friendly code can run **10-100x faster** than cache-unfriendly code, even with identical algorithms.

โค้ดที่เป็นมิตรกับแคชสามารถทำงานได้เร็วกว่า **10-100 เท่า** เมื่อเทียบกับโค้ดที่ไม่เป็นมิตรกับแคช แม้ว่าจะใช้อัลกอริทึมเหมือนกัน

### 1.2 Cache Line Basics

พื้นฐาน Cache Line

```cpp
// Modern CPUs: 64-byte cache lines
struct BadLayout {
    double x;      // 8 bytes
    char padding[56];  // Waste most of cache line
    double y;      // Another cache line
};

struct GoodLayout {
    double x, y, z;  // 24 bytes, fits in one line
    double vx, vy, vz;  // Another line
    // Used together → accessed together
};
```

**OpenFOAM field storage (cache-aware):**

```cpp
// GeometricField stores contiguous arrays
List<T> internalField_;  // Sequential access = cache friendly

// GOOD: Iteration pattern
forAll(internalField_, i) {
    internalField_[i] = ...;  // Sequential access
}

// BAD: Random access
forAll(internalField_, i) {
    label j = faceCells[i];  // Indirect access
    internalField_[j] = ...;  // Cache miss likely
}
```

---

## 2. WHAT: Profiling Memory Performance

อะไร: การวิเคราะห์ประสิทธิภาพหน่วยความจำ

### 2.1 Profiling Tools

เครื่องมือ Profiling

#### perf (Linux)

```bash
# Cache miss analysis
perf stat -e cache-references,cache-misses,instructions,cycles simpleFoam

# Output example:
cache-references:      245,832,104
cache-misses:           12,341,023  # 5.02% of all accesses
instructions:        1,234,567,890
cycles:               987,654,321

# IPC = instructions/cycles ≈ 1.25 (good)
```

#### valgrind/cachegrind

```bash
# Detailed cache simulation
valgrind --tool=cachegrind simpleFoam

# Analyze results
cg_annotate cachegrind.out.<pid>

# Key metrics:
# - Ir: Instructions executed
# - I1mr: L1 instruction cache misses
# - D1mr: L1 data cache misses
# - DLmr: Last-level cache misses
```

### 2.2 Memory Access Patterns

รูปแบบการเข้าถึงหน่วยความจำ

**Pattern 1: Sequential Access (GOOD)**

```cpp
// OpenFOAM field iteration
forAll(U, cellI) {
    U[cellI] = vector(1, 0, 0);  // Sequential: cache line prefetch
}
```

**Pattern 2: Strided Access (MEDIUM)**

```cpp
// Every nth element
for (int i = 0; i < size; i += 8) {
    U[i] = ...;  // May skip cache lines
}
```

**Pattern 3: Random Access (BAD)**

```cpp
// Indirect addressing
forAll(faceCells, faceI) {
    label cellI = faceCells[faceI];  // Jump to random location
    U[cellI] = ...;  // Cache miss!
}
```

---

## 3. HOW: Optimization Techniques

อย่างไร: เทคนิคการปรับปรุง

### 3.1 Data Layout Optimization

การปรับปรุงเลย์เอาต์ข้อมูล

#### Structure of Arrays (SoA) vs Array of Structures (AoS)

```cpp
// AoS (Array of Structures) - Cache inefficient for vector ops
struct ParticleAoS {
    vector position;
    vector velocity;
    scalar mass;
};
List<ParticleAoS> particles;  
// Access: particles[i].position.x - poor cache usage

// SoA (Structure of Arrays) - Cache efficient
struct ParticleSoA {
    List<vector> positions;   // Contiguous x, y, z
    List<vector> velocities;  // Contiguous vx, vy, vz
    List<scalar> masses;      // Contiguous masses
};
// Access: positions[i] - better cache line utilization
```

**OpenFOAM example:**

```cpp
// Fields are implicitly SoA
GeometricField<vector> U;      // Separate x, y, z arrays
GeometricField<scalar> p;      // Scalar field

// Vectorized operations automatically benefit
U = fvc::grad(p);  // Sequential access through all cells
```

### 3.2 Loop Optimization

การปรับปรุงลูป

#### Loop Tiling/Blocking

```cpp
// BEFORE: Cache thrashing
for (int j = 0; j < NJ; j++) {
    for (int i = 0; i < NI; i++) {
        A[i][j] = B[i][j] + C[i][j];  // Row-major: scan columns slowly
    }
}

// AFTER: Tiled for cache efficiency
const int TILE = 32;  // Fits in L1 cache
for (int jj = 0; jj < NJ; jj += TILE) {
    for (int ii = 0; ii < NI; ii += TILE) {
        // Process tile that fits in cache
        for (int j = jj; j < min(jj+TILE, NJ); j++) {
            for (int i = ii; i < min(ii+TILE, NI); i++) {
                A[i][j] = B[i][j] + C[i][j];
            }
        }
    }
}
```

#### Loop Fusion

```cpp
// BEFORE: Multiple passes over data
forAll(T, i) T[i] = ...;      // Pass 1
forAll(T, i) T[i] += ...;     // Pass 2
forAll(T, i) T[i] *= ...;     // Pass 3

// AFTER: Single pass
forAll(T, i) {
    T[i] = ...;
    T[i] += ...;  // Reuse cached data
    T[i] *= ...;
}
```

### 3.3 Memory Allocation Optimization

การปรับปรุงการจัดสรรหน่วยความจำ

#### Preallocation Strategy

```cpp
// BAD: Repeated allocation
for (int i = 0; i < n; i++) {
    List<label> localLabels(100);  // Allocate every iteration
    // ... use localLabels ...
}  // Deallocate every iteration

// GOOD: Reuse allocation
List<label> localLabels(100);
for (int i = 0; i < n; i++) {
    localLabels.clear();  // O(1) - keeps capacity
    // ... use localLabels ...
}
```

#### Temporary Field Management

```cpp
// BAD: Creates new temporary each iteration
while (runtime.loop()) {
    tmp<volScalarField> tDivU = fvc::div(U);  // Allocation
    solve(fvm::laplacian(nu, U) == tDivU());
}  // Deallocation

// GOOD: Reuse workspace
tmp<volScalarField> tDivU;
while (runtime.loop()) {
    tDivU = fvc::div(U);  // Reuse if possible
    solve(fvm::laplacian(nu, U) == tDivU());
}
```

### 3.4 Compiler Optimizations

การปรับปรุงคอมไพเลอร์

#### Memory Alignment

```cpp
// OpenFOAM ensures alignment for SIMD
// Align data to 16/32/64 byte boundaries

struct AlignedVector {
    double x, y, z;
} __attribute__((aligned(32)));  // AVX alignment

// Enables SIMD vectorization
#pragma omp simd
for (int i = 0; i < n; i++) {
    vectors[i].x *= 2.0;  // Vectorized operation
}
```

#### Prefetching

```cpp
// Explicit prefetch (advanced)
for (int i = 0; i < n; i++) {
    __builtin_prefetch(&data[i + 16]);  // Prefetch ahead
    process(data[i]);
}
```

---

## 4. OpenFOAM-Specific Optimizations

การปรับปรุงเฉพาะสำหรับ OpenFOAM

### 4.1 Field Operations

การดำเนินการ Field

```cpp
// Cache-friendly: In-place operations
U += fvc::grad(p);  // Reuses U's memory

// Cache-unfriendly: Unnecessary temporaries
tmp<volVectorField> gradP = fvc::grad(p);
volVectorField temp = U + gradP();  // Extra allocation
U = temp;  // Another allocation
```

### 4.2 Mesh Access Patterns

รูปแบบการเข้าถึง Mesh

```cpp
// GOOD: Cell-based iteration
forAll(mesh.cells(), cellI) {
    const cell& c = mesh.cells()[cellI];
    // Process all faces in cell
}  // Better locality

// AVOID: Random face access
forAll(mesh.faces(), faceI) {
    // Jump around the mesh
    label owner = mesh.faceOwner()[faceI];
    label neighbour = mesh.faceNeighbour()[faceI];
}
```

### 4.3 Parallel Performance Considerations

ข้อควรพิจารณาประสิทธิภาพแบบขนาน

```cpp
// Memory-bound parallelization
#pragma omp parallel for
forAll(U, i) {
    U[i] = ...;  // Each thread has different cache lines
}

// False sharing risk (BAD)
struct Counter {
    int value;
};
Counter counters[omp_get_max_threads()];  // Same cache line

// Fix: Align to cache line
struct alignas(64) Counter {
    int value;
};
```

---

## 5. Measuring Optimization Impact

การวัดผลกระทบของการปรับปรุง

### 5.1 Benchmarking Framework

กรอบการวัดประสิทธิภาพ

```cpp
// Simple benchmark timer
class Timer {
    clock_t start_;
public:
    Timer() : start_(clock()) {}
    double elapsed() const {
        return double(clock() - start_) / CLOCKS_PER_SEC;
    }
};

// Usage
Timer t;
// ... operation ...
std::cout << "Time: " << t.elapsed() << " s\n";
```

### 5.2 Performance Metrics

ตัวชี้วัดประสิทธิภาพ

| Metric | Target | Tool |
|--------|--------|------|
| Cache hit rate | >95% L1, >90% L2 | perf, cachegrind |
| IPC (Instructions Per Cycle) | >1.0 | perf |
| Memory bandwidth | >80% peak | stream benchmark |
| Allocation overhead | <5% runtime | custom profiling |

| ตัวชี้วัด | เป้าหมาย | เครื่องมือ |
|--------|--------|------|
| อัตรา cache hit | >95% L1, >90% L2 | perf, cachegrind |
| IPC (Instructions Per Cycle) | >1.0 | perf |
| แบนด์วิดท์หน่วยความจำ | >80% สูงสุด | stream benchmark |
| ค่าใช้จ่ายการจัดสรร | <5% รันไทม์ | profiling แบบกำหนดเอง |

---

## Key Takeaways
สรุปสิ่งสำคัญ

### 🎯 Core Concepts
แนวคิดหลัก

**WHAT (Memory performance factors):**
**ปัจจัยประสิทธิภาพหน่วยความจำ:**

- **Cache locality:** Sequential access > random access
- **Data layout:** SoA > AoS for vector operations
- **Allocation overhead:** Minimize temporary allocations
- **Memory bandwidth:** Often the bottleneck, not CPU

**แคชความเป็นใจท้องถิ่น:** การเข้าถึงต่อเนื่องดีกว่าการเข้าถึงแบบสุ่ม
**เลย์เอาต์ข้อมูล:** SoA ดีกว่า AoS สำหรับการดำเนินการเวกเตอร์
**ค่าใช้จ่ายการจัดสรร:** ลดการจัดสรรชั่วคราว
**แบนด์วิดท์หน่วยความจำ:** มักเป็นคอขวด ไม่ใช่ CPU

**WHY (Optimization matters):**
**ทำไมการปรับปรุงสำคัญ:**

- 10-100x speedup possible from cache optimization
- Memory-bound workloads dominate CFD simulations
- Small changes in access patterns = big impact
- Profiling reveals true bottlenecks

**เพิ่มความเร็วได้ 10-100 เท่าจากการปรับแต่งแคช**
**งานที่ผูกมัดกับหน่วยความจำครองงาน CFD**
**การเปลี่ยนแปลงเล็กน้อยในรูปแบบการเข้าถึง = ผลกระทบใหญ่**
**Profiling เปิดเผยคอขวดที่แท้จริง

**HOW (Optimization strategies):**
**กลยุทธ์การปรับปรุง:**

- **PROFILE first:** Measure before optimizing
- **Sequential access:** Organize loops for cache lines
- **Preallocate:** Reuse memory when possible
- **Tile loops:** Fit working set in cache
- **Align data:** Enable SIMD operations

**วิเคราะห์ก่อน:** วัดก่อนปรับปรุง
**การเข้าถึงต่อเนื่อง:** จัดระเบียบลูปสำหรับ cache lines
**จัดสรรล่วงหน้า:** ใช้หน่วยความจำซ้ำเมื่อเป็นไปได้
**ลูปแบบกระเบื้อง:** ใส่ working set ในแคช
**จัดแนวข้อมูล:** เปิดใช้งานการดำเนินการ SIMD

### 📊 Optimization Checklist

รายการตรวจสอบการปรับปรุง

- [ ] Profile with `perf` or `cachegrind`
- [ ] Identify cache hotspots
- [ ] Reorganize data layout for sequential access
- [ ] Preallocate frequently used containers
- [ ] Fuse loops when possible
- [ ] Align data structures for SIMD
- [ ] Measure impact of each optimization
- [ ] Document performance gains

### 🔗 Connecting the Dots

เชื่อมโยงแนวคิด

```
Memory Mechanics (03) ← Performance Optimization (08) → Practical Application (07)
         ↓                              ↓                         ↓
   How memory                 How to optimize              How to apply
   works internally          memory access                in real CFD code
```

- **File 03 (Internal Mechanics)** explains HOW memory allocation works internally
- **File 08 (This file)** shows HOW to optimize memory access patterns
- **File 07 (Practical Exercise)** demonstrates applying optimizations in CFD code

**ไฟล์ 03 (กลไกภายใน)** อธิบายวิธีการทำงานของการจัดสรรหน่วยความจำภายใน
**ไฟล์ 08 (ไฟล์นี้)** แสดงวิธีการปรับรูปแบบการเข้าถึงหน่วยความจำ
**ไฟล์ 07 (แบบฝึกหัด)** สาธิตการใช้การปรับปรุงในโค้ด CFD

### ⚠️ Common Pitfalls
ข้อผิดพลาดทั่วไป

❌ **DON'T:** Optimize without profiling first
✅ **DO:** Measure to find true bottlenecks

❌ **DON'T:** Sacrifice correctness for speed
✅ **DO:** Verify results match before optimization

❌ **DON'T:** Over-optimize rarely-used code
✅ **DO:** Focus on hotspots (inner loops)

❌ **อย่า:** ปรับปรุงโดยไม่มีการวิเคราะห์ก่อน
✅ **ทำ:** วัดเพื่อค้นหาคอขวดที่แท้จริง

❌ **อย่า:** เสียสละความถูกต้องเพื่อความเร็ว
✅ **ทำ:** ยืนยันผลลัพธ์ตรงกันก่อนการปรับปรุง

❌ **อย่า:** ปรับปรุงโค้ดที่ไม่ค่อยใช้เกินไป
✅ **ทำ:** เน้นที่จุดร้อน (inner loops)

---

## 🧠 Concept Check
ทดสอบความเข้าใจ

<details>
<summary><b>1. Why does sequential access perform better than random access?</b></summary>

**Answer:** CPUs fetch data in cache lines (typically 64 bytes). Sequential access maximizes cache line utilization because:
- Adjacent elements are prefetched automatically
- One cache miss brings in multiple useful values
- Hardware prefetchers detect sequential patterns

Random access causes frequent cache misses because each access likely targets a different cache line, wasting memory bandwidth.

**คำตอบ:** CPU ดึงข้อมูลใน cache lines (โดยทั่วไป 64 bytes) การเข้าถึงต่อเนื่องเพิ่มประสิทธิภาพการใช้ cache line เพราะ:
- องค์ประกอบที่อยู่ติดกันถูก prefetch อัตโนมัติ
- การ miss cache ครั้งเดียวนำค่าหลายค่าที่มีประโยชน์มา
- ตัว prefetch ฮาร์ดแวร์ตรวจจับรูปแบบต่อเนื่อง

การเข้าถึงแบบสุ่มทำให้เกิด cache misses บ่อยเพราะแต่ละการเข้าถึงมักมีเป้าหมายเป็น cache line ที่ต่างกัน สิ้นเปลืองแบนด์วิดท์หน่วยความจำ

**Key Point:** Cache line reuse = performance

**จุดสำคัญ:** การใช้ cache line ซ้ำ = ประสิทธิภาพ
</details>

<details>
<summary><b>2. What is the difference between SoA and AoS?</b></summary>

**Answer:** 

**AoS (Array of Structures):**
```cpp
struct Particle { vector pos, vel; };
Particle p[1000];  // Interleaved data
```
- Good for: Random access to individual particles
- Bad for: Vector operations (only uses 1/3 of cache line)

**SoA (Structure of Arrays):**
```cpp
struct Particles { 
    List<vector> pos, vel; 
};
```
- Good for: Vector ops, cache-friendly sequential access
- Bad for: Random particle access

OpenFOAM uses SoA for fields: all x-coordinates stored contiguously, enabling efficient vector operations.

**คำตอบ:** OpenFOAM ใช้ SoA สำหรับ fields: พิกัด x ทั้งหมดเก็บแบบต่อเนื่อง เปิดใช้งานการดำเนินการเวกเตอร์ที่มีประสิทธิภาพ

**Key Point:** Match data layout to access pattern

**จุดสำคัญ:** จับคู่เลย์เอาต์ข้อมูลกับรูปแบบการเข้าถึง
</details>

<details>
<summary><b>3. How do you measure cache performance?</b></summary>

**Answer:** Use profiling tools:

**Linux perf:**
```bash
perf stat -e cache-references,cache-misses,cycles ./solver
# Look for: cache-misses/cache-references ratio (<10% is good)
```

**Valgrind cachegrind:**
```bash
valgrind --tool=cachegrind ./solver
cg_annotate cachegrind.out.*
# Shows: L1, L2, LL cache miss rates per function
```

**Key metrics:**
- L1 miss rate: <5% (target)
- L3 miss rate: <1% (target)
- IPC: >1.0 (instructions per cycle)

**คำตอบ:** ใช้เครื่องมือ profiling ตัวชี้วัดหลัก:
- อัตรา miss L1: <5% (เป้าหมาย)
- อัตรา miss L3: <1% (เป้าหมาย)
- IPC: >1.0 (instructions per cycle)

**Key Point:** You can't optimize what you don't measure

**จุดสำคัญ:** คุณไม่สามารถปรับปรุงสิ่งที่คุณไม่วัด
</details>

<details>
<summary><b>4. When should you use loop tiling?</b></summary>

**Answer:** Use loop tiling when:

1. **Working set > cache size:** The data accessed in inner loops doesn't fit in cache
2. **Multi-dimensional arrays:** Accessing 2D/3D arrays with poor locality
3. **Nested loops:** Outer loop causes cache eviction before reuse

**Example:**
```cpp
// Cache thrashing: NJ * NI > L2 cache
for (int j = 0; j < NJ; j++)
    for (int i = 0; i < NI; i++)
        A[i][j] = ...;  // Flushes cache each row iteration

// Tiled: Processes blocks that fit in cache
for (int jj = 0; jj < NJ; jj += TILE)
    for (int ii = 0; ii < NI; ii += TILE)
        // Process TILE×TILE block
```

Choose TILE size ≈ sqrt(cache size / data type size).

**คำตอบ:** เลือกขนาด TILE ≈ sqrt(ขนาดแคช / ขนาดประเภทข้อมูล)

**Key Point:** Make the working set fit in cache

**จุดสำคัญ:** ทำให้ working set พอดีในแคช
</details>

---

## 📖 Further Reading
เอกสารอ้างอิงเพิ่มเติม

### Internal Dependencies
การพึ่งพาภายใน

- **Internal Mechanics:** [03_Internal_Mechanics.md](03_Internal_Mechanics.md) — How memory allocation works
- **Design Patterns:** [05_Design_Patterns.md](05_Design_Patterns.md) — Memory management patterns
- **Practical Exercise:** [07_Practical_Exercise.md](07_Practical_Exercise.md) — Apply optimizations in code

### OpenFOAM Examples
ตัวอย่าง OpenFOAM

```bash
# Profile a simple solver
cd $FOAM_RUN/tutorials/incompressible/simpleFoam
perf stat -e cache-misses,cycles simpleFoam

# Check field memory layout
ls $FOAM_SRC/OpenFOAM/fields/
# - GeometricField: Cache-friendly contiguous storage
```

### External Resources
แหล่งข้อมูลภายนอก

- *What Every Programmer Should Know About Memory* (Ulrich Drepper)
- [Intel VTune Profiler](https://www.intel.com/content/www/us/en/developer/tools/oneapi/vtune-profiler.html)
- [CppCon: High Performance C++](https://www.youtube.com/results?search_query=cppcon+performance)
- OpenFOAM: `$FOAM_SRC/OpenFOAM/db/IOstreams/memory/`

---

**Previous:** [04_Memory_Syntax_and_Design.md](04_Memory_Syntax_and_Design.md) — Memory management syntax