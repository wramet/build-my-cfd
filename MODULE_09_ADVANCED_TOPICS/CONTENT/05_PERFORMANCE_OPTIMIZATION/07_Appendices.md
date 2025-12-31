# Appendices: Quick Reference and Practical Tools

เอกสารอ้างอิงและเครื่องมือเสริม

---

## 🎯 Learning Objectives

**หลังจากอ่านบทนี้ คุณจะสามารถ:**

1. **เลือก compiler flags ที่เหมาะสม** สำหรับ debugging และ production
2. **ใช้เครื่องมือ profiling** เพื่อค้นหา performance bottlenecks จริง
3. **ปรับใช้ optimization techniques** พื้นฐานกับโค้ด OpenFOAM
4. **สร้าง performance checklist** สำหรับการตรวจสอบ solver ของคุณ
5. **ตีความ profiler output** และแปลงเป็น action items ที่ชัดเจน

---

## 💡 Why This Matters

**Appendices นี้ไม่ใช่แค่ reference dump** — แต่เป็น **quick-start guide** สำหรับการปรับแต่ง performance จริง

**ทำไมต้องเรียนรู้สิ่งเหล่านี้:**

- **Compiler flags**: ผิดตัวเดียวอาจทำให้ solver ช้าลง 2-5x หรือ crash โดยไม่ทราบสาเหตุ
- **Profiling tools**: การเดาว่า bottleneck อยู่ที่ไหน ≠ การวัดจริง 80% ของ optimization มักเกิดจากจุดที่ไม่คาดคิด
- **Memory profiling**: Memory leaks สะสมระยะยาวทำให้ simulation ขนาดใหญ่ crash หลังจากทำงานหลายวัน
- **Performance checklist**: ช่วยป้องกัน common pitfalls ที่ทุกคนเคยเจอ

**Connection to Previous Sections:**
- **Section 01** แนะนำ profiling concepts เบื้องต้น → Appendices นี้ให้ practical recipes
- **Section 04** อธิบาย compiler-level optimizations → Appendices นี้รวม quick reference
- **Section 05** แสดงการใช้ tools เหล่านี้ใน action → Appendices นี้เป็น cheat sheet

---

## 🔧 How To Apply

**Step-by-Step Workflow:**

1. **Start with Debug build** → ยืนยันว่าโค้ดถูกต้อง
2. **Profile with `perf`** → หา hot functions จริง
3. **Optimize top 3 bottlenecks** → ใช้ techniques จาก Appendix C
4. **Memory check with `valgrind`** → ยืนยันไม่มี leaks
5. **Switch to Opt build** → วัด speedup ที่ได้
6. **Document findings** → ใช้ checklist จาก Appendix E

**Integration with Other Modules:**
- **Template Programming (Module 09)**: Compiler flags กระทบ template instantiation performance
- **Memory Management (Module 09)**: Valgrind output ช่วยระบุ memory anti-patterns
- **Design Patterns (Module 09)**: บาง patterns มี inherent overhead ที่ต้อง measure

---

## A. Compiler Flags

### 📌 Quick Reference

| Scenario | Command | When to Use |
|----------|---------|-------------|
| **Debug** | `wmake -j` | Development, testing |
| **Optimized** | `export WM_COMPILE_OPTION=Opt && wmake -j` | Production runs |
| **Profiling** | `export WM_COMPILE_OPTION=Prof && wmake -j` | Performance analysis |
| **Custom** | Edit `wmake/rules/linux64Gcc/c++` | Special needs |

### 🔍 Before/After: Debug vs Opt

**Before (Debug build):**
```bash
# Compile with debug symbols
wmake myCustomSolver

# Runtime
time myCustomSolver > log
# real 5m23s (baseline for development)
```

**After (Optimized build):**
```bash
# Compile with optimization
export WM_COMPILE_OPTION=Opt
wclean myCustomSolver
wmake myCustomSolver

# Runtime
time myCustomSolver > log
# real 1m47s (3x speedup)
```

**Key Insight:** ใช้ Debug ตอนพัฒนา แต่ **ต้อง benchmark ด้วย Opt build** เพราะ production runs ใช้ Opt เสมอ

### ⚠️ Common Mistakes

**Mistake 1: Mixing flags**
```bash
# WRONG: Conflicting flags
export WM_COMPILE_OPTION=Opt
wmake -j -DDEBUG
```

**Correct:**
```bash
# CORRECT: Consistent flags
export WM_COMPILE_OPTION=Opt
wmake -j
```

**Mistake 2: Assuming Opt is always faster**
- Opt builds บางทีช้ากว่า ถ้าโค้ดมี undefined behavior (UB)
- ใช้ tools อย่าง `valgrind` ยืนยันก่อน optimize

### 🎯 Practical Exercise: Compiler Flag Experiment

```bash
# 1. Create test case
cd $FOAM_RUN
cp -r tutorials/basic/potentialFoam test_compilerFlags
cd test_compilerFlags

# 2. Time Debug build
wmake
time potentialFoam > log.debug 2>&1
echo "Debug time:" $(tail -1 log.debug)

# 3. Time Opt build
export WM_COMPILE_OPTION=Opt
wclean
wmake
time potentialFoam > log.opt 2>&1
echo "Opt time:" $(tail -1 log.opt)

# 4. Compare
echo "Speedup: $(awk 'NR==2{d=$1} NR==2{if(f) print d/f; f=$1}' \
    <(grep 'ExecutionTime' log.debug) <(grep 'ExecutionTime' log.opt))x"
```

**Expected Output:**
```
Debug time: ExecutionTime = 12.45 s
Opt time: ExecutionTime = 4.21 s
Speedup: 2.96x
```

---

## B. Profiling Tools

### 📊 Tool Comparison Matrix

| Tool | What It Measures | Overhead | When to Use | Output Format |
|------|-----------------|----------|-------------|---------------|
| **`perf`** | CPU hotspots, call graphs | ~5% | First pass profiling | Terminal, flame graphs |
| **`gprof`** | Function call counts | ~20% | Legacy code support | Text reports, call graphs |
| **`valgrind/cachegrind`** | Cache misses | ~100x | Deep optimization | Detailed cache analysis |
| **`valgrind/massif`** | Heap usage | ~20x | Memory leak detection | Heap snapshots |
| **`valgrind/memcheck`** | Memory errors | ~100x | Debugging only | Error reports |
| **`vtune`** | CPU, memory, threading | ~10% | Intel CPUs only | GUI, detailed reports |
| **`scalasca`** | MPI communication | ~15% | Parallel scaling | Timeline views |

### 🔧 Perf: First-Line Tool

**Basic Workflow:**
```bash
# 1. Record performance data
perf record -g --call-graph dwarf myCustomSolver > log 2>&1

# 2. Analyze results
perf report --stdio | head -50

# 3. Generate flame graph (optional)
perf script | stackcollapse-perf.pl | flamegraph.pl > perf.svg
```

**Sample Output:**
```
# Overhead  Command        Shared Object
    35.20%  myCustomSolver  myCustomSolver
            |
            ---35%-- solve()
                   |--12%-- fvMatrix::solve()
                   |--8%-- lduMatrix::solve()
                   |--5%-- tmp<N1,N2>::tmp()
                   |--3%-- FieldField::evaluate()
                   `--2%-- other...
    
    18.45%  myCustomSolver  libOpenFOAM.so
            |
            |--10%-- Foam::pow()
            |--5%-- Foam::exp()
            `--3%-- Foam::log()
    
    12.30%  myCustomSolver  libc.so
            |
            |--8%-- memcpy
            |--3%-- memset
            `--1%-- malloc
```

**Interpretation:**
- **Hotspot #1 (35%)**: `solve()` function → focus optimization here
- **Hotspot #2 (18%)**: Math functions → consider vectorization
- **Hotspot #3 (12%)**: Memory operations → check data locality

### 🔍 Before/After: Profiling-Driven Optimization

**Before (no profiling):**
```cpp
// Naive implementation - guess that pow() is bottleneck
forAll(cells, i) {
    scalar rho = pow(p[i], 0.7);  // Expensive?
    rhoField[i] = rho;
}
```

**After (profiling reveals real bottleneck):**
```cpp
// perf shows memcpy is actually the hotspot
// Optimization: pre-allocate and use reference
scalarField& rhoRef = rhoField.ref();
const scalarField& pRef = p.primitiveField();

forAll(rhoRef, i) {
    rhoRef[i] = pow(pRef[i], 0.7);  // Acceptable - not the bottleneck
}

// Real win: reduce temporary copies elsewhere
```

**Performance Impact:**
- Before: 5m23s total runtime
- After: 3m12s (40% faster)
- Key insight: **pow() wasn't the bottleneck — memory copies were**

### 🎯 Practical Exercise: Profile Your Solver

```bash
# 1. Setup test case
cd $FOAM_RUN
cd myTestcase

# 2. Profile with perf
perf record -g --call-graph dwarf myCustomSolver > log 2>&1

# 3. Top 10 hotspots
perf report --stdio --sort=overhead | head -20

# 4. Generate annotated source (optional)
perf annotate --stdio | less

# 5. Identify:
#    - Top 3 functions by overhead?
#    - Any OpenFOAM internals in top 10?
#    - Any opportunities for easy wins?
```

---

## C. Common Optimizations

### 📌 Optimization Quick Reference

| Technique | Flag | Speedup | Trade-off | When to Use |
|-----------|------|---------|-----------|-------------|
| **Inlining** | `-finline-functions` | 10-30% | Larger binary | Small, frequently-called functions |
| **Vectorization** | `-march=native` | 2-4x | CPU-specific | Production on known hardware |
| **Link-time** | `-flto` | 5-15% | Longer compile | Large projects with many files |
| **Aggressive** | `-O3 -ffast-math` | 10-50% | May change results | Validated physics only |

### 🔍 Before/After: Vectorization

**Before (no vectorization):**
```cpp
// Scalar operations (1 float per CPU cycle)
for (label i = 0; i < n; i++) {
    c[i] = a[i] * b[i];
}
// Assembly: 1 mul per iteration
```

**After (auto-vectorized with -march=native):**
```cpp
// Same code, but compiler generates AVX instructions
// Compiler output (objdump -d):
// vmulps  (%rax), %ymm0, %ymm1  # 8 floats per cycle!
```

**Performance Impact:**
- Before: 100ms for 10M elements
- After: 15ms for 10M elements (6.7x speedup)

**How to Verify:**
```bash
# Check if vectorization happened
objdump -d myCustomSolver | grep -i "vmulps\|vaddps"
# If empty, no vectorization occurred

# Add compiler flags to force vectorization
export WM_COMPILE_OPTION=Opt
wmake
```

### ⚙️ Compiler Flag Combinations

**Conservative (safe for all physics):**
```bash
export WM_COMPILE_OPTION=Opt
# Equivalent to -O2
```

**Aggressive (for validated cases):**
```bash
# Edit wmake/rules/linux64Gcc/c++:
c++OPT = -O3 -march=native -flto -funroll-loops
```

**Profiling-enabled:**
```bash
# Edit wmake/rules/linux64Gcc/c++:
c++OPT = -O2 -pg -fno-omit-frame-pointer
```

### 🎯 Practical Exercise: Benchmark Optimizations

```bash
# 1. Create baseline
export WM_COMPILE_OPTION=Opt
wclean && wmake
time myCustomSolver > log.baseline

# 2. Add inlining
# Edit wmake/rules/linux64Gcc/c++:
# c++OPT = -O2 -finline-functions
wclean && wmake
time myCustomSolver > log.inline

# 3. Add vectorization
# Edit wmake/rules/linux64Gcc/c++:
# c++OPT = -O2 -finline-functions -march=native
wclean && wmake
time myCustomSolver > log.vector

# 4. Compare
echo "Baseline: $(grep ExecutionTime log.baseline)"
echo "Inline: $(grep ExecutionTime log.inline)"
echo "Vector: $(grep ExecutionTime log.vector)"
```

---

## D. Memory Profiling

### 🔍 Why Memory Profiling Matters

**Real-World Scenario:**
- Solver รันได้ 100 timesteps แล้ว crash
- Memory usage แนวโน้มเพิ่มขึ้นเรื่อยๆ
- สาเหตุ: memory leak ใน custom boundary condition

**Tools for Detection:**
| Tool | Detects | Use Case |
|------|---------|----------|
| **massif** | Heap growth trends | Long-running simulations |
| **memcheck** | Leaks, invalid access | Debugging crashes |
| **address sanitizer** | Use-after-free | Development testing |

### 🔧 Massif: Memory Usage Over Time

**Basic Usage:**
```bash
# 1. Run with massif
valgrind --tool=massif \
         --massif-out-file=massif.out \
         myCustomSolver > log 2>&1

# 2. Analyze results
ms_print massif.out | less

# 3. Find peak memory
grep -A 5 "detailed" massif.out | head -20
```

**Sample Output:**
```
KB
101.5^                                                                       #
     |                                                                      :#
     |                                                                    ::# 
     |                                                                  :::# 
     |                                                                ::::# 
     |                                                              :::::# 
     |                                                            :::::::# 
     |                                                          :::::::::# 
     |                                                        :::::::::# 
     |                                                      :::::::::# 
     |                                                    :::::::::# 
     |                                                  :::::::::# 
     |                                                :::::::::# 
     |                                              :::::::::# 
     |                                            :::::::::# 
     |                                          :::::::::# 
     |                                        :::::::::# 
     |                                      :::::::::# 
     |                                    :::::::::# 
     |                                  :::::::::# 
     |                                :::::::::# 
     |                              :::::::::# 
     |                            :::::::::# 
     |                          :::::::::# 
     |                        :::::::::# 
     |                      :::::::::# 
     |                    :::::::::# 
   0 +----------------------------------------------
     0                                                                   100

Number of snapshots: 52
 Detailed snapshots: [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
 Peak memory usage: 101,456 KB at snapshot #50
```

**Interpretation:**
- Memory grows monotonically → **potential leak**
- Flat memory after initial growth → **normal behavior**
- Sawtooth pattern → **allocation/deallocation cycles**

### 🔍 Before/After: Fixing Memory Leaks

**Before (memory leak):**
```cpp
// Bug: Creating new object each iteration
for (label i = 0; i < nIter; i++) {
    volScalarField* field = new volScalarField(
        IOobject("temp", mesh),
        mesh,
        dimensionedScalar("zero", dimless, 0)
    );
    // Never deleted!
}
// Result: Memory grows unbounded
```

**After (fixed):**
```cpp
// Solution 1: Stack allocation (preferred)
for (label i = 0; i < nIter; i++) {
    volScalarField field(
        IOobject("temp", mesh),
        mesh,
        dimensionedScalar("zero", dimless, 0)
    );
    // Automatically destroyed at end of scope
}

// Solution 2: Smart pointer (if dynamic allocation needed)
for (label i = 0; i < nIter; i++) {
    auto field = autoPtr<volScalarField>::New(
        IOobject("temp", mesh),
        mesh,
        dimensionedScalar("zero", dimless, 0)
    );
    // Automatically managed
}
```

**Memory Impact:**
- Before: 2.1 GB peak, crash at timestep 120
- After: 450 MB stable, runs to completion (500 timesteps)

### 🎯 Practical Exercise: Detect Memory Leaks

```bash
# 1. Run solver with massif
valgrind --tool=massif \
         --massif-out-file=massif.out \
         --time-unit=B \
         myCustomSolver > log 2>&1

# 2. Check for leaks
ms_print massif.out | tail -50

# 3. Run with memcheck (more detailed)
valgrind --tool=memcheck \
         --leak-check=full \
         --show-leak-kinds=all \
         --track-origins=yes \
         myCustomSolver > log.memcheck 2>&1

# 4. Summarize leaks
grep "definitely lost" log.memcheck
grep "indirectly lost" log.memcheck
```

---

## E. Performance Checklist

### ✅ Pre-Run Checklist

**Before Starting Optimization:**
- [ ] **Baseline established**: Have timing data from current implementation
- [ ] **Correctness verified**: Results match validated case within tolerance
- [ ] **Debug build clean**: No compiler warnings, passes all tests
- [ ] **Reproducibility confirmed**: Multiple runs give consistent timings (±2%)

### ✅ Code Review Checklist

**Memory Management:**
- [ ] **Use `tmp` for temporaries**: Avoid unnecessary copies
  ```cpp
  // BAD
  tmp<volScalarField> tRho = ...;
  volScalarField rho = tRho();  // Creates copy
  
  // GOOD
  tmp<volScalarField> tRho = ...;
  tRho().ref()  // Work directly
  ```

- [ ] **Avoid allocations in loops**: Pre-allocate outside
  ```cpp
  // BAD
  for (int i = 0; i < 1000; i++) {
      List<scalar> data(1000);  // Allocates every iteration!
  }
  
  // GOOD
  List<scalar> data(1000);
  for (int i = 0; i < 1000; i++) {
      // Reuse data
  }
  ```

- [ ] **Use global reduction ops**: `gSum`, `gMax` instead of manual reduction
  ```cpp
  // BAD
  scalar sum = 0;
  forAll(field, i) sum += field[i];
  sum = returnReduce(sum, sumOp<scalar>());  // Manual reduction
  
  // GOOD
  scalar sum = gSum(field);  // Built-in, optimized
  ```

**Algorithm Efficiency:**
- [ ] **Check cache efficiency**: Use spatial locality
  ```cpp
  // BAD: Random access
  forAll(cells, i) {
      label j = randomIndex();
      field[j] = value;
  }
  
  // GOOD: Sequential access
  forAll(field, i) {
      field[i] = value;
  }
  ```

- [ ] **Use const references**: Avoid copies
  ```cpp
  // BAD
  void func(volScalarField field)  // Copy by value!
  
  // GOOD
  void func(const volScalarField& field)  // Reference
  ```

### ✅ Profiling Checklist

**Performance Measurement:**
- [ ] **Profile before optimizing**: Don't guess, measure
- [ ] **Use multiple tools**: `perf` + `valgrind` + profiling build
- [ ] **Focus on hotspots**: Top 3 functions = 80% of gains
- [ ] **Document baseline**: Keep logs for comparison
  ```bash
  # Example documentation
  echo "Baseline: $(grep ExecutionTime log)" > timing.log
  echo "Compiler: $(wmake -show-cxxcompiler)" >> timing.log
  echo "Flags: $(wmake -show-cxxflags)" >> timing.log
  ```

### ✅ Post-Optimization Checklist

**After Making Changes:**
- [ ] **Re-verify correctness**: Results still match baseline
- [ ] **Measure actual speedup**: Use same test case
- [ ] **Profile again**: Confirm bottleneck moved, not just hidden
- [ ] **Document changes**: What was tried, what worked
  ```bash
  # Example change log
  echo "Optimization: Changed List to UList" >> timing.log
  echo "Speedup: 1.35x" >> timing.log
  echo "Verified: diff log.new log.baseline" >> timing.log
  ```

### 📊 Performance Metrics Template

**Track Your Optimizations:**

| Metric | Baseline | After Opt 1 | After Opt 2 | Target |
|--------|----------|-------------|-------------|--------|
| **Execution time** | 5m23s | 3m45s | 2m12s | < 3m |
| **Memory peak** | 1.2 GB | 1.1 GB | 0.9 GB | < 1 GB |
| **Timesteps/day** | 140 | 220 | 350 | > 300 |
| **Speedup** | 1.0x | 1.43x | 2.46x | > 2x |

---

## 🎓 Further Reading

### OpenFOAM-Specific Resources

1. **OpenFOAM Wiki - Optimization**
   - https://openfoamwiki.net/index.php/Category:Optimization
   - คู่มือการ optimize solvers และ utilities

2. **OpenFOAM Programmer's Guide**
   - Chapter 6: Performance and Optimization
   - Official recommendations from OpenFOAM developers

3. **OpenFOAM CFD Direct**
   - https://cfd.direct/openfoam/manual/
   - Section on coding guidelines and efficiency

### General Performance Resources

4. **Linux `perf` Examples**
   - https://www.brendangregg.com/perf.html
   - Comprehensive `perf` tutorial with flame graphs

5. **Valgrind User Manual**
   - https://valgrind.org/docs/manual/manual.html
   - Detailed tool usage and output interpretation

6. **Compiler Optimization Guides**
   - GCC: https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html
   - Intel: https://www.intel.com/content/www/us/en/docs/cpp-compiler/

### Related Modules

7. **Module 09 - Template Programming**
   - Template instantiation performance
   - Compile-time optimization techniques

8. **Module 09 - Memory Management**
   - Memory allocation strategies
   - Smart pointer usage in OpenFOAM

9. **Module 08 - Testing and Validation**
   - Performance regression testing
   - Automated benchmarking

---

## 📝 Key Takeaways

### Quick Reference Summary

**Compiler Flags:**
- **Debug**: `wmake` — Development and testing
- **Opt**: `export WM_COMPILE_OPTION=Opt` — Production runs (2-5x speedup)
- **Prof**: `export WM_COMPILE_OPTION=Prof` — Performance analysis

**Profiling Workflow:**
1. Run `perf record -g solver` → หา hotspots
2. Focus on top 3 functions → 80% ของ performance gains
3. Optimize → Verify correctness
4. Re-profile → ยืนยัน improvements

**Memory Profiling:**
- **massif**: Track heap growth → Detect leaks in long runs
- **memcheck**: Find leaks and errors → Debug crashes
- **Address sanitizer**: Catch use-after-free → Development testing

**Common Optimizations:**
- **Inlining** (`-finline-functions`): 10-30% speedup
- **Vectorization** (`-march=native`): 2-4x speedup on numerical code
- **Link-time optimization** (`-flto`): 5-15% speedup

**Performance Checklist:**
- Profile **before** optimizing
- Use `tmp` for temporaries
- Avoid allocations in loops
- Use global reduction ops (`gSum`, `gMax`)
- Re-verify correctness after changes

### Critical Lessons

1. **Don't guess — Measure**: 80% ของ bottlenecks อยู่ที่ไม่คาดคิด
2. **Optimize the right things**: Top 3 hotspots = majority of gains
3. **Correctness first**: Fast but wrong = worse than slow but correct
4. **Document everything**: Keep timing logs, compiler flags, results
5. **Cross-reference modules**: Template programming affects compile time, memory management affects runtime

---

## 🧠 Concept Check

<details>
<summary><b>1. เมื่อไหร่ควรใช้ profiling tools?</b></summary>

**ตอบ:** **ก่อนเริ่ม optimize** — หา actual bottlenecks ก่อนเสมอ

**เหตุผล:**
- การเดาว่า bottleneck อยู่ที่ไหน มักผิด
- 80% ของ performance issue มาจาก 20% ของโค้ด
- Profiling ช่วย prioritize งาน optimization อย่างมีประสิทธิภาพ

**Best practice:**
```bash
# Step 1: Profile
perf record -g solver
perf report

# Step 2: Identify top 3 hotspots

# Step 3: Optimize only those

# Step 4: Re-profile to confirm
```
</details>

<details>
<summary><b>2. WM_COMPILE_OPTION ทำอะไรและมีค่าอะไรบ้าง?</b></summary>

**ตอบ:** **Select compilation mode** — Debug, Opt, Prof, หรือ custom

**ค่าที่มี:**
- **Debug** (default): `-g -O0` — Full symbols, no optimization
- **Opt**: `-O2` — Optimized for production
- **Prof**: `-O2 -pg` — Optimized + profiling data

**Best practice:**
```bash
# Development: Debug
wmake

# Production: Opt
export WM_COMPILE_OPTION=Opt
wmake

# Analysis: Prof
export WM_COMPILE_OPTION=Prof
wmake
```
</details>

<details>
<summary><b>3. `perf` ใช้ทำอะไรและอ่าน output อย่างไร?</b></summary>

**ตอบ:** **CPU profiling** — หา hot functions ที่ consume CPU time

**Usage:**
```bash
# Record
perf record -g solver

# Report
perf report --stdio

# Output example:
# 35.20%  solver  solver
#         |
#         ---35%-- solve()
#                |--12%-- fvMatrix::solve()
#                |--8%-- lduMatrix::solve()
```

**Interpretation:**
- **35%** ของเวลาอยู่ใน `solve()`
- **12%** ใน `fvMatrix::solve()` → potential target
- Focus ที่ top 3-5 functions
</details>

<details>
<summary><b>4. `valgrind --tool=massif` บอกอะไร?</b></summary>

**ตอบ:** **Memory usage over time** — Detect leaks and memory growth patterns

**Usage:**
```bash
valgrind --tool=massif solver
ms_print massif.out
```

**Output patterns:**
- **Monotonic growth**: Memory leak
- **Flat after initial**: Normal behavior
- **Sawtooth**: Allocation/deallocation cycles

**Best practice:**
- Run on long simulations (> 100 timesteps)
- Check for monotonic growth
- Use `memcheck` for detailed leak reports
</details>

<details>
<summary><b>5. Optimization flags มี trade-offs อะไรบ้าง?</b></summary>

**ตอบ:** **Speed vs safety vs portability**

| Flag | Benefit | Risk | When to Use |
|------|---------|------|-------------|
| `-O2` | 2-3x speedup | Safe for most code | Production |
| `-O3` | 10-20% extra | May change results | Validated cases only |
| `-march=native` | 2-4x on numerical | CPU-specific | Known hardware |
| `-ffast-math` | 10-50% on math | May reduce accuracy | Non-sensitive physics |
| `-flto` | 5-15% speedup | Longer compile | Large projects |

**Best practice:**
- Start with `-O2` (WM_COMPILE_OPTION=Opt)
- Add aggressive flags **after validation**
- Test on small cases first
</details>

<details>
<summary><b>6. Performance checklist สำคัญที่สุดคืออะไร?</b></summary>

**ตอบ:** **Profile before optimizing** + **Verify correctness after**

**Critical items:**
1. ✅ Profile first → หา bottlenecks จริง
2. ✅ Use `tmp` for temporaries → ลด copies
3. ✅ Avoid allocations in loops → Pre-allocate
4. ✅ Use global reductions → `gSum`, `gMax`
5. ✅ Re-verify correctness → Results still valid
6. ✅ Re-profile → Confirm improvements

**Common mistakes:**
- ❌ Optimizing cold code (waste of time)
- ❌ Assuming faster = better (might be wrong results)
- ❌ Not measuring speedup (illusion of improvement)
- ❌ Over-optimizing (diminishing returns)
</details>

---

## 🔗 Cross-References to Related Modules

**Template Programming (Module 09.01):**
- Compiler flags affect template instantiation time
- Use `-flto` to optimize template-heavy code

**Memory Management (Module 09.04):**
- Valgrind output helps identify memory anti-patterns
- Use `autoPtr`, `tmp`, `refPtr` properly

**Design Patterns (Module 09.03):**
- Some patterns (e.g., Strategy) have inherent overhead
- Profile to determine if pattern cost is acceptable

**Testing and Validation (Module 08):**
- Regression testing ensures optimizations don't break physics
- Automated benchmarking tracks performance over time

---

## 📖 Related Documentation in This Module

- **Overview:** [00_Overview.md](00_Overview.md) — Module roadmap and prerequisites
- **Section 01:** [01_Introduction.md](01_Introduction.md) — Why performance matters in OpenFOAM
- **Section 04:** [04_Compiler_Level_Optimizations.md](04_Compiler_Level_Optimizations.md) — Deep dive on compiler flags
- **Section 05:** [05_Practical_Exercise.md](05_Practical_Exercise.md) — Hands-on optimization workflow