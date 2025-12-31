# Compilation and Machine Code

การ Compile และ Machine Code

---

## 🎯 Learning Objectives

By the end of this file, you will be able to:

1. **Configure** OpenFOAM compilation options (`WM_COMPILE_OPTION`) for different build scenarios
2. **Analyze** the effects of optimization flags (`-O0`, `-O2`, `-O3`) on generated machine code
3. **Examine** assembly output to verify compiler optimizations (inlining, vectorization)
4. **Use** profiling tools (`perf`, `objdump`, `valgrind`) to identify performance bottlenecks
5. **Compare** Debug vs. Optimized builds with concrete performance metrics
6. **Diagnose** optimization failures and missing compiler transformations

---

## 💡 Why This Matters

Understanding compilation and machine code is critical because:

**Real-World Impact:**
- **2-10x speedup**: Optimized builds (`-O3`) vs. Debug builds (`-O0`) can dramatically reduce simulation time
- **Correctness vs. performance trade-off**: Debug builds catch bugs but are too slow for production runs
- **Compiler verification**: Without checking assembly, you can't verify that optimizations are actually happening
- **Portability**: Understanding compiler flags ensures your code performs well across different platforms

**OpenFOAM-Specific Context:**
- OpenFOAM's template-heavy codebase relies heavily on compiler optimizations
- Many "free" performance gains come from `-O3` vectorization and inlining
- wmake build system provides multiple compilation modes for different needs
- Performance regressions often stem from subtle changes in compilation settings

Without understanding compilation mechanics, you're flying blind—optimizations may not trigger, or worse, produce incorrect results.

---

## 📋 Prerequisites

**Required C++ Knowledge:**
- Understanding of compilation stages: preprocessing, compilation, assembly, linking
- Basic familiarity with compiler flags (`-O`, `-g`, `-std=c++14`)
- Ability to read simple assembly (x86/ARM instructions)

**Required OpenFOAM Knowledge:**
- Expression template mechanics (Module 09.05.03)
- tmp class and memory management (Module 09.05.02)
- wmake build system basics

**Related Modules:**
- **Module 09.01 - Template Programming**: How templates enable compile-time optimization
- **Module 09.04 - Memory Management**: Memory allocation patterns and performance

---

## Overview

> Compiler transformations turn template code into efficient machine instructions

OpenFOAM's performance emerges from the compiler's ability to transform high-level template code into optimized machine instructions. This file shows how to control, verify, and debug this transformation process.

---

## 1. Complete Learning Roadmap

This file builds on previous topics in the Performance Optimization module:

### Prerequisites from Previous Files:
- **01_Introduction**: Performance metrics, profiling philosophy
- **02_Expression_Templates_Syntax**: tmp usage patterns
- **03_Internal_Mechanics**: How compiler optimizations work internally

### This File: Compilation and Machine Code
- **Section 2**: WM_COMPILE_OPTION configuration and effects
- **Section 3**: Optimization levels with concrete examples
- **Section 4**: Assembly inspection and verification
- **Section 5**: Profiling tools for compilation analysis

### Building to Next Files:
- **05_Patterns**: Design trade-offs and when to optimize
- **06_Errors**: Debugging optimization failures

**Progression Strategy**: This file shows *how to verify* that compiler optimizations are happening. File 03 explained *how they work* internally. File 05 discusses *when* to apply them.

---

## 2. OpenFOAM Compilation Modes: WM_COMPILE_OPTION

### 2.1 Available Compilation Options

| Option | Full Name | Optimization | Debug Symbols | Use Case |
|--------|-----------|--------------|---------------|----------|
| **Debug** | Debug | `-O0 -g` | Full | Development, debugging |
| **Opt** | Optimized | `-O3` | Minimal | Production runs |
| **Prof** | Profile | `-O2 -pg` | Full + profiling | Performance analysis |
| **System** | System | Varies | Varies | System-specific defaults |

### 2.2 WM_COMPILE_OPTION Effects Table

| Aspect | Debug (`-O0`) | Opt (`-O3`) | Performance Difference |
|--------|---------------|-------------|------------------------|
| **Inlining** | Disabled | Aggressive | 2-10x speedup in small functions |
| **Vectorization** | Disabled | Full AVX/SSE | 4-8x speedup in field ops |
| **Loop unrolling** | Disabled | Enabled | 1.5-3x speedup in tight loops |
| **Binary size** | Small | Large | - (unrelated to speed) |
| **Compile time** | Fast | Slow | - (build time only) |
| **Debugging** | Easy | Difficult | - (developer experience) |
| **Simulation speed** | **1x baseline** | **2-10x faster** | ⭐ **Critical impact** |

### 2.3 Setting Compilation Mode

```bash
# Method 1: Environment variable (affects all wmake calls)
export WM_COMPILE_OPTION=Opt
wmake

# Method 2: Per-build override
WM_COMPILE_OPTION=Debug wmake

# Method 3: Check current setting
echo $WM_COMPILE_OPTION

# Method 4: Examine actual flags
wmake -j 2>&1 | grep CXXFLAGS
# Output: CXXFLAGS = -O3 -std=c++14 -Dlinux64 -DMPICH_SKIP_MPICXX ...
```

### 2.4 Performance Impact: Debug vs. Opt

**Benchmark: Simple Scalar Transport Solver**

```bash
# Debug build
WM_COMPILE_OPTION=Debug wmake mySolver
time mySolver
# real  8m45s
# user  8m12s
# sys   0m28s

# Optimized build
WM_COMPILE_OPTION=Opt wmake mySolver
time mySolver
# real  1m15s
# user  1m08s
# sys   0m07s

# Speedup: 7.0x faster (!)
```

**Benchmark: Large Case (10M cells)**

| Build Type | Time per Iteration | Memory Usage | Total Simulation Time |
|------------|-------------------|--------------|----------------------|
| Debug (`-O0`) | 12.5 seconds | 1.2 GB | **~35 hours** |
| Opt (`-O3`) | 1.8 seconds | 1.2 GB | **~5 hours** |
| **Speedup** | **7x** | Same | **7x faster** |

---

## 3. Optimization Levels: Concrete Examples

### 3.1 Optimization Flag Comparison

| Flag | Optimizations Enabled | When to Use | Performance Impact |
|------|----------------------|-------------|-------------------|
| `-O0` | None | Debugging | Baseline (slowest) |
| `-O1` | Basic inlining, dead code elim. | Faster debug builds | 1.5-2x vs -O0 |
| `-O2` | + Loop unrolling, vectorization | Production default | 3-5x vs -O0 |
| `-O3` | + Aggressive inlining, auto-vectorization | Performance-critical | 4-10x vs -O0 |

### 3.2 Before/After: Function Inlining

**C++ Source:**

```cpp
// Template function (src/OpenFOAM/fields/Fields/Fields/scalarField.C)
template<class Type>
inline Type sqr(const Type& x)
{
    return x * x;
}

// Usage in solver
scalar result = sqr(1.5);
```

**Assembly with -O0 (No inlining):**

```asm
# Compiler generates function call
call    _Z3sqrIdET_RKT_    # Call sqr<double>()
movq    %rax, -8(%rbp)     # Store result
# Instructions: ~15 (call overhead + stack ops)
```

**Assembly with -O3 (Inlining):**

```asm
# Compiler inserts function body directly
movsd   .LC0(%rip), %xmm1     # Load 1.5
mulsd   %xmm1, %xmm1          # Multiply: 1.5 * 1.5
movsd   %xmm1, -8(%rbp)       # Store result: 2.25
# Instructions: 3 (no function call)
# Speedup: ~5x for this call
```

### 3.3 Before/After: Loop Vectorization

**C++ Source:**

```cpp
// Field scaling operation
forAll(field, i)
{
    field[i] = 2.0 * field[i] + 1.0;
}
```

**Assembly with -O0 (Scalar, 1 element at a time):**

```asm
.L3:
    movsd   (%rax), %xmm1       # Load 1 double
    mulsd   %xmm0, %xmm1        # Multiply by 2.0
    addsd   %xmm2, %xmm1        # Add 1.0
    movsd   %xmm1, (%rax)       # Store 1 double
    addq    $8, %rax            # Next element
    cmpq    %rbx, %rax
    jne     .L3                 # Loop back
# Each iteration: 1 double processed
```

**Assembly with -O3 -march=native (AVX2, 4 doubles at once):**

```asm
.L3:
    vmovupd (%rax), %ymm1       # Load 4 doubles (256-bit)
    vfmadd231pd %ymm0, %ymm2, %ymm1  # FMA: 2.0*x + 1.0 for all 4
    vmovupd %ymm1, (%rax)       # Store 4 doubles
    addq    $32, %rax           # Next 4 elements
    cmpq    %rbx, %rax
    jne     .L3
# Each iteration: 4 doubles processed
# Speedup: ~3.5x for large arrays
```

### 3.4 Checking Generated Assembly

```bash
# Method 1: Examine object file
objdump -d mySolver.o | grep "_Z3sqrIdET" -A 20

# Method 2: Examine shared library
objdump -d libmySolver.so | grep "field_scaling" -A 30

# Method 3: Interactive disassembly (GDB)
gdb mySolver
(gdb) disassemble sqr(double const&)
(gdb) disassemble /m 0x401000  # Show at address

# Method 4: Compiler output (assembly source)
wmake WM_COMPILE_OPTION=Opt CXXFLAGS="-O3 -S"
ls -l *.s  # Assembly source files
cat mySolver.C.s | grep -A 20 "sqr"
```

### 3.5 Vectorization Verification

```bash
# Compile with vectorization reports (Clang)
wmake WM_COMPILE_OPTION=Opt \
    CXXFLAGS="-O3 -Rpass=loop-vectorize -Rpass-missed=loop-vectorize"

# Expected output:
# remark: vectorized loop (vectorization width: 4, interleaved count: 1)
# mySolver.C:145:12

# If no vectorization:
# remark: loop not vectorized: loop control flow is not understood
# mySolver.C:145:12

# GCC equivalent
wmake WM_COMPILE_OPTION=Opt \
    CXXFLAGS="-O3 -fopt-info-vec -fopt-info-vec-missed"
```

---

## 4. Profiling Tools for Compilation Analysis

### 4.1 perf: CPU Performance Counters

```bash
# Record performance data
perf record -g --call-graph dwarf mySolver

# Analyze hotspots
perf report

# Example output:
# 35.20%  solver   libmySolver.so  [.] Foam::fvm::ddt<double>
# 18.45%  solver   libmySolver.so  [.] Foam::fvc::grad<double>
#  8.15%  solver   libcore.so      [.] Foam::GeometricField::operator[]
#
# Interpretation:
# - fvm::ddt consumes 35% of time → Optimize this
# - fvc::grad at 18% → Secondary target
# - Check if these are vectorized with perf annotate
```

### 4.2 perf annotate: Assembly-Level Analysis

```bash
# Annotate with assembly
perf record mySolver
perf annotate

# Output shows cycles per instruction:
# Percent | Source code & Disassembly of mySolver for cycles:uh (502748 samples)
# --------------------------------------------------------------------------------
#
#     8.94 │        movsd    (%rdi), %xmm1
#    35.21 │        mulsd    %xmm0, %xmm1          # ← Hot instruction (!)
#    12.45 │        addsd    %xmm2, %xmm1
#             movsd    %xmm1, (%rdi)
#             addq     $8, %rdi
#             cmpq     %rax, %rdi
#          ┌──jne      +20
#          │  rep ret
#
# This shows the multiplication is the hotspot → Check if vectorized
```

### 4.3 valgrind/cachegrind: Cache Analysis

```bash
# Cache simulation
valgrind --tool=cachegrind mySolver

# View results
cg_annotate cachegrind.out.<pid>

# Key metrics:
# Ir  I1mr  I1mr  Dr  D1mr  D1mw  Dw  D1mw  D1mw
# === Instructions, L1 cache misses, Data reads/writes
#
# High D1mr/D1mw = Cache misses → Check memory access patterns
```

### 4.4 objdump: Binary Inspection

```bash
# Disassemble specific function
objdump -d libmySolver.so | grep -A 50 "sqr<double>"

# Check for vectorization
objdump -d libmySolver.so | grep -B 5 -A 10 "vmovupd"

# Output indicating AVX2:
# vmovupd (%rax), %ymm1     # YMM = 256-bit AVX2
# vfmadd231pd ...           # Fused multiply-add
```

---

## 5. Common Compilation Issues

### 5.1 Optimization Failures

| Symptom | Cause | Solution |
|---------|-------|----------|
| No vectorization reports | Loop-carried dependencies | Restructure loop |
| Binary too large | Excessive inlining (`-O3`) | Use `-O2` or `__attribute__((noinline))` |
| Slow despite `-O3` | Missing `-march=native` | Add `-march=native` to CXXFLAGS |
| Wrong results | Aggressive optimization bug | Use `-ffast-math` carefully, verify with `-O0` |

### 5.2 Debugging Performance Regressions

```bash
# Step 1: Bisect compilation flags
for flag in "-O2" "-O3" "-O3 -march=native"; do
    echo "Testing: $flag"
    wmake CXXFLAGS="$flag"
    time mySolver
done

# Step 2: Check for inlining
objdump -d libmySolver.so | grep "call" | wc -l
# Fewer calls = more inlining

# Step 3: Verify vectorization
perf stat -e cycles,instructions,cache-misses mySolver
# IPC (Instructions Per Cycle) > 1.0 = good vectorization
```

---

## Quick Reference

| Task | Command | Output |
|------|---------|--------|
| **Set Debug mode** | `export WM_COMPILE_OPTION=Debug` | No optimizations, full symbols |
| **Set Opt mode** | `export WM_COMPILE_OPTION=Opt` | Full `-O3` optimizations |
| **Check flags** | `wmake 2>&1 \| grep CXXFLAGS` | Show compilation flags |
| **Examine assembly** | `objdump -d lib.so \| grep func -A 20` | Disassemble function |
| **Profile CPU** | `perf record -g mySolver; perf report` | Hotspot analysis |
| **Check vectorization** | `wmake CXXFLAGS="-O3 -Rpass=vec"` | Vectorization reports |
| **Cache analysis** | `valgrind --tool=cachegrind mySolver` | Cache miss rates |

---

## 🔑 Key Takeaways

### Compilation Mode Selection

1. **Debug (`-O0`)**: Development, catching bugs, gdb debugging
2. **Opt (`-O3`)**: Production runs, maximum performance (2-10x faster)
3. **Prof (`-O2 -pg`)**: Performance profiling with gprof

### Optimization Verification

1. **Check assembly**: `objdump -d` to verify inlining and vectorization
2. **Use compiler reports**: `-Rpass=vec` shows vectorization success/failure
3. **Profile with perf**: Identify actual hotspots, don't guess
4. **Compare builds**: Benchmark `-O0` vs `-O3` to measure improvement

### Common Patterns

| Need | Approach | Example |
|------|----------|---------|
| Faster builds | Use `-O0` for development | `WM_COMPILE_OPTION=Debug` |
| Production runs | Always use `-O3` | `WM_COMPILE_OPTION=Opt` |
| Verify vectorization | Check for AVX instructions | `objdump -d \| grep vmovupd` |
| Find hotspots | Profile with perf | `perf record -g` |
| Debug performance | Compare assembly | `objdump -d` at different flags |

---

## 🧠 Concept Check

<details>
<summary><b>1. -O3 ดีกว่า -O2 เสมอไหม?</b></summary>

**ไม่เสมอ** — แต่ใน OpenFOAM ส่วนใหญ่ดีกว่า

**Trade-offs:**
- ✅ **Pros**: Aggressive inlining, more vectorization, faster code
- ❌ **Cons**: Larger binaries, longer compile times, harder to debug

**When -O2 might be better**:
- Development builds (faster compilation)
- Debugging optimization bugs
- Memory-constrained systems (smaller binary)

**For OpenFOAM production**: Always use `-O3` (2-10x speedup is worth it).
</details>

<details>
<summary><b>2. Debug build ช้ากว่าเท่าไหร่?</b></summary>

**2-10x ช้ากว่า** — ขึ้นอยู่กับ solver

**Why:**
- No inlining: Function call overhead everywhere
- No vectorization: 1 element at a time instead of 4-8
- No loop unrolling: More branch mispredictions

**Rule of thumb**:
- Simple solver: ~2-3x slower
- Complex solver with heavy field ops: ~5-10x slower
- Debug builds are for debugging, not for running simulations

**Best practice**: Develop with `-O0`, run with `-O3`.
</details>

<details>
<summary><b>3. inline keyword จำเป็นไหม?</b></summary>

**ไม่จำเป็นเสมอ** — compiler ตัดสินใจเอง

**Compiler heuristic:**
- Small functions (< ~300 instructions): Auto-inlined at `-O2`/`-O3`
- Template functions: Almost always inlined
- Large functions: Rarely inlined (code bloat)

**When to use `inline`:**
- Header-only templates (required)
- Small performance-critical functions (hint)
- Force inlining with `__attribute__((always_inline))`

**Best practice**: Trust the compiler first, use hints only when profiling shows need.
</details>

<details>
<summary><b>4. How do I verify vectorization is happening?</b></summary>

**Three methods:**

**Method 1: Compiler reports**
```bash
wmake CXXFLAGS="-O3 -Rpass=loop-vectorize"
# Look for: "remark: vectorized loop (width: 4)"
```

**Method 2: Assembly inspection**
```bash
objdump -d lib.so | grep "vmovupd\|vfmadd"
# AVX instructions (YMM registers) = vectorized
```

**Method 3: Performance counters**
```bash
perf stat -e instructions,cycles,cycles:u mySolver
# IPC > 1.0 = vectorization working
# IPC ~0.5 = scalar execution (bad)
```

**What to look for**:
- `vmovupd`/`vmovapd`: AVX loads/stores
- `vfmadd231pd`: Fused multiply-add (4-8 doubles per instruction)
- YMM registers (256-bit) instead of XMM (128-bit)
</details>

<details>
<summary><b>5. ทำไม benchmark แล้วไม่เห็น speedup จาก -O3?</b></summary>

**Possible causes:**

**1. Memory-bound (not CPU-bound)**:
```bash
# Check with perf
perf stat -e cache-misses mySolver
# High cache-misses → memory bandwidth bound
# Solution: Improve cache locality, not compiler flags
```

**2. Small problem size**:
```cpp
// Too small for vectorization to matter
for (int i = 0; i < 10; i++) ...  // Overhead > benefit

// Need larger loops
for (int i = 0; i < 1000000; i++) ...  // Vectorization pays off
```

**3. Optimization blockers**:
- Virtual function calls in tight loops
- Pointer aliasing (use `__restrict__`)
- Complex control flow (`break`, `continue`)

**Diagnosis**:
```bash
# Check if vectorized
wmake CXXFLAGS="-O3 -Rpass=vec -Rpass-missed=vec"

# Check assembly
objdump -d lib.so | grep "call"
# Many calls = inlining failed
```
</details>

---

## 📖 Related Documentation

### Within This Module:
- **Overview:** [00_Overview.md](00_Overview.md) — Complete learning roadmap
- **Internal Mechanics:** [03_Internal_Mechanics.md](03_Internal_Mechanics.md) — How optimizations work internally
- **Design Patterns:** [05_Design_Patterns_and_Trade-offs.md](05_Design_Patterns_and_Trade-offs.md) — When to apply optimizations

### Cross-Module References:
- **Module 09.01 - Template Programming:** How templates enable compile-time optimization
- **Module 09.04 - Memory Management:** Cache efficiency and memory allocation patterns
- **Module 08.05 - QA and Profiling:** [01_Performance_Profiling.md](../../MODULE_08_TESTING_VALIDATION/CONTENT/05_QA_AUTOMATION_PROFILING/01_Performance_Profiling.md) — Profiling techniques in depth

### External Resources:
- [GCC Optimization Flags](https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html)
- [LLVM Clang Optimization](https://clang.llvm.org/docs/UsersManual.html#options-for-optimizing-code)
- [Intel Optimization Manual](https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html)
- [OpenFOAM Programmer's Guide - Build System](https://cfd.direct/openfoam/programmers-guide/)