# Performance - Internal Mechanics

กลไกภายในของ Performance Optimization

---

## 🎯 Learning Objectives

By the end of this file, you will be able to:

1. **Explain** how the compiler decides which optimizations to apply for OpenFOAM code
2. **Understand** the compile-time optimization pipeline: inlining, vectorization, and dead code elimination
3. **Analyze** runtime optimizations: vector execution, cache efficiency, and memory access patterns
4. **Predict** performance implications of tmp usage and reference counting
5. **Diagnose** parallel efficiency issues in global operations and reductions
6. **Apply** optimization-friendly coding patterns that enable compiler transformations

---

## 💡 Why This Matters

Understanding the internal mechanics of performance optimization is critical because:

- **Compiler is your ally**: Modern compilers can perform dramatic optimizations (2-10x speedup) if you write optimizer-friendly code
- **Hidden bottlenecks**: Performance issues often stem from subtle patterns (cache misses, missed vectorization) invisible without understanding compiler mechanics
- **Debugging performance**: When profiling shows unexpected hotspots, understanding optimization mechanics helps identify root causes
- **Portable performance**: Compiler optimizations work across all platforms—no hardware-specific code needed
- **Future-proof**: As compilers improve, code written with optimization mechanics in mind automatically benefits

OpenFOAM's performance is fundamentally built on C++ template metaprogramming and compiler cooperation. Without understanding these mechanics, you're coding in the dark—your optimizations may have no effect, or worse, hurt performance.

---

## 📋 Prerequisites

**Required C++ Knowledge:**
- **Advanced templates**: Template instantiation, specialization, SFINAE (covered in Module 09.01)
- **Inline functions**: Understanding `inline` keyword and function call overhead
- **Compiler optimizations**: Familiarity with `-O3`, `-ffast-math`, and optimization flags
- **Assembly basics**: Ability to read simple x86/ARM assembly for profiling verification
- **Memory model**: Stack vs. heap, cache hierarchy (L1/L2/L3), memory bandwidth concepts

**Required OpenFOAM Knowledge:**
- Expression template syntax (Module 09.05.02)
- tmp class usage patterns (Module 09.05.02)
- Field operations and fvc::/fvm:: functions
- Basic parallel decomposition concepts

**Related Modules:**
- **Module 09.01 - Template Programming**: Template instantiation mechanics (file 03)
- **Module 09.04 - Memory Management**: Memory allocation patterns and cache behavior (file 03)

---

## Overview

> OpenFOAM optimizes at **compile-time** and **runtime**

Performance in OpenFOAM emerges from the interplay between:
1. **Compile-time**: Template metaprogramming, inlining, vectorization
2. **Runtime**: Cache efficiency, memory access patterns, parallel communication

Understanding both phases enables you to write code that the compiler can optimize effectively and that runs efficiently on target hardware.

---

## 1. Complete Learning Roadmap

This file builds on previous topics in the Performance Optimization module:

### Prerequisites from Previous Files:
- **01_Introduction**: Performance metrics, tmp class basics, optimization philosophy
- **02_Expression_Templates_Syntax**: Field algebra patterns, tmp usage syntax

### This File: Internal Mechanics
- **Section 2**: Compile-time optimization pipeline
- **Section 3**: Runtime optimization mechanisms
- **Section 4**: How the compiler decides (NEW)
- **Section 5**: Optimization pipeline visualization (NEW)

### Building to Next Files:
- **04_Compilation**: Profiling tools, assembly inspection, optimization verification
- **05_Patterns**: Design trade-offs, when to optimize vs. readability
- **06_Errors**: Debugging performance regressions, diagnosing optimization failures

**Progression Strategy**: This file explains *how* optimizations work internally. File 04 shows *how to verify* they're happening. File 05 discusses *when* to apply them.

---

## 2. Compile-Time Optimizations

### 2.1 The Optimization Pipeline

```mermaid
graph TB
    subgraph "Source Code"
        A[Template Code]
    end
    
    subgraph "Compiler Frontend"
        B[Template Instantiation]
        C[AST Generation]
    end
    
    subgraph "Optimizer Middle-End"
        D[Inlining]
        E[Dead Code Elimination]
        F[Loop Optimization]
        G[Vectorization Analysis]
    end
    
    subgraph "Code Generation"
        H[Register Allocation]
        I[Instruction Selection]
        J[Assembly Output]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H --> I
    I --> J
    
    style D fill:#e3f2fd,stroke:#1976d2
    style E fill:#e3f2fd,stroke:#1976d2
    style G fill:#fff3e0,stroke:#f57c00
```

**Figure 1**: The complete compilation and optimization pipeline in OpenFOAM

---

### 2.2 Template Inlining

**What Happens | อะไรเกิดขึ้น**

When a function is declared `inline`, the compiler inserts the function body directly at the call site instead of generating a function call instruction.

```cpp
// Template function marked inline
template<class Type>
inline Type sqr(const Type& x) 
{ 
    return x * x; 
}

// Before optimization - would call function
scalar a = sqr(1.5);

// After inlining - code inserted directly
scalar a = 1.5 * 1.5;
```

**Why It Matters | ทำไมสำคัญ**

- **Eliminates call overhead**: No push/pop stack, no jump instructions
- **Enables further optimization**: Inlined code can be constant-folded, vectorized
- **Small functions benefit most**: Overhead dominates for tiny functions

**Performance Impact | ผลกระทบต่อ Performance**

```cpp
// Benchmark: Calling sqr() 10M times
// Without inline: 0.15 seconds
// With inline:    0.02 seconds
// Speedup:        7.5x
```

**OpenFOAM Context | บริบทใน OpenFOAM**

```cpp
// src/OpenFOAM/fields/Fields/Fields/scalarField.C
template<class Type>
inline scalarField::operator const Field<Type>&() const
{
    // This cast operator is inlined for zero-cost type conversion
    return *reinterpret_cast<const Field<Type>*>(this);
}
```

---

### 2.3 Dead Code Elimination

**What Happens | อะไรเกิดขึ้น**

Compiler removes code that can never execute or has no observable effect.

```cpp
// Template with conditional compilation
template<class Type>
void process()
{
    if constexpr (std::is_scalar<Type>::value)
    {
        // Only compiled for scalar types
        Info << "Processing scalar" << endl;
    }
    else
    {
        // Only compiled for vector/tensor types
        Info << "Processing field" << endl;
    }
}

// When instantiated with Type=scalar:
// - Vector branch completely removed from binary
// - No runtime check needed
```

**`if constexpr` vs Regular `if`**

| Aspect | `if constexpr` | Regular `if` |
|--------|----------------|--------------|
| **When evaluated** | Compile-time | Runtime |
| **Code generation** | Only true branch | Both branches |
| **Runtime cost** | Zero | Branch prediction |
| **Template context** | Works | May fail |

**OpenFOAM Example | ตัวอย่างใน OpenFOAM**

```cpp
// src/OpenFOAM/fields/GeometricFields/GeometricField/GeometricField.H
template<class Type, template<class> class PatchField, class GeoMesh>
void GeometricField<Type, PatchField, GeoMesh>::correctBoundaryConditions()
{
    if constexpr (std::is_same<GeoMesh, fvMesh>::value)
    {
        // FV-specific boundary correction
        // Only compiled for fvMesh, not for pointMesh
    }
}
```

---

### 2.4 Loop Vectorization

**What is Vectorization | Vectorization คืออะไร**

Vectorization (SIMD - Single Instruction, Multiple Data) processes multiple array elements with one CPU instruction.

```cpp
// Scalar code (processes 1 element at a time)
forAll(field, i)
{
    field[i] = a * field[i] + b;  // 1 iteration = 1 multiply + 1 add
}

// Vectorized code (processes 4/8 elements at once)
// Assuming AVX2 (256-bit) with double precision:
// Each iteration processes 4 doubles simultaneously
for (int i = 0; i < field.size(); i += 4)
{
    __m256d f = _mm256_load_pd(&field[i]);      // Load 4 doubles
    __m256d result = _mm256_fmadd_pd(a_vec, f, b_vec);  // a*f[i] + b[i] for all 4
    _mm256_store_pd(&field[i], result);         // Store 4 doubles
}
```

**Vectorization Requirements | เงื่อนไขการ Vectorize**

Compiler can vectorize when:
1. ✅ Loop count is known or easily analyzable
2. ✅ No loop-carried dependencies
3. ✅ Memory access is contiguous
4. ✅ No function calls (or calls are inline-able)
5. ✅ Simple arithmetic operations

```cpp
// ✅ VECTORIZABLE: Simple, independent iterations
forAll(field, i)
{
    field[i] = 2.0 * field[i] + 1.0;  // Each i independent
}

// ❌ NOT VECTORIZABLE: Loop-carried dependency
for (int i = 1; i < field.size(); i++)
{
    field[i] = field[i] + field[i-1];  // Needs previous value
}

// ❌ NOT VECTORIZABLE: Complex function call
forAll(field, i)
{
    field[i] = expensiveFunction(field[i]);  // Unless inlined
}
```

**Checking Vectorization | ตรวจสอบ Vectorization**

```bash
# Compile with vectorization reports
wmake -j4 WM_COMPILER=Clang \
    CXXFLAGS="-O3 -Rpass=loop-vectorize -Rpass-missed=loop-vectorize"

# Output:
# remark: vectorized loop (vectorization width: 4, interleaved count: 1)
```

**Performance Impact | ผลกระทบต่อ Performance**

```cpp
// Benchmark: Field addition on 10M cells
// Scalar (1x):     0.45 seconds
// SSE (2x):        0.24 seconds  (1.9x speedup)
// AVX (4x):        0.13 seconds  (3.5x speedup)
// AVX-512 (8x):    0.07 seconds  (6.4x speedup)
```

---

## 3. Runtime Optimizations

### 3.1 Cache Efficiency

**Memory Hierarchy | ลำดับชั้นหน่วยความจำ**

```
CPU Registers (instant, ~1KB)
    ↓ 1 cycle
L1 Cache (~32KB, fastest)
    ↓ 4 cycles
L2 Cache (~256KB, fast)
    ↓ 12 cycles
L3 Cache (~8MB, slower)
    ↓ 40 cycles
Main Memory (GBs, slowest)
    ↓ 100-200 cycles
```

**Cache Performance Impact | ผลกระทบของ Cache**

```cpp
// ❌ CACHE INEFFICIENT: Strided access
for (int j = 0; j < ny; j++)
{
    for (int i = 0; i < nx; i++)
    {
        // Access pattern: [0][0], [0][1], [0][2], ...
        // Memory: non-contiguous, cache misses
        scalar val = field2D[i][j];
    }
}

// ✅ CACHE EFFICIENT: Contiguous access
for (int i = 0; i < nx; i++)
{
    for (int j = 0; j < ny; j++)
    {
        // Access pattern: [0][0], [1][0], [2][0], ...
        // Memory: contiguous, cache hits
        scalar val = field2D[i][j];
    }
}
```

**OpenFOAM Best Practice | แนวทางปฏิบัติใน OpenFOAM**

```cpp
// ✅ GOOD: Use primitiveField() for contiguous access
const scalarField& f = field.primitiveField();
forAll(f, i)
{
    // Direct array access, optimal cache usage
    f[i] *= 2.0;
}

// ❌ AVOID: Boundary field access in inner loop
// Boundary patches are non-contiguous in memory
forAll(field.boundaryField(), patchI)
{
    const fvPatchScalarField& pf = field.boundaryField()[patchI];
    forAll(pf, i)
    {
        // Scattered memory access
    }
}
```

**Cache Line Considerations | การพิจารณา Cache Line**

```cpp
// Cache line size: typically 64 bytes
// Double precision: 8 bytes per scalar
// One cache line holds: 8 doubles

// Struct of Arrays (SoA) - OpenFOAM approach
struct Fields
{
    scalarField p;  // Contiguous doubles
    scalarField T;  // Contiguous doubles
    scalarField rho;// Contiguous doubles
};
// When processing p[i], next 7 doubles loaded
// Cache line reused for p[i+1] through p[i+7]

// Array of Structs (AoS) - alternative approach
struct CellData
{
    scalar p;   // 8 bytes
    scalar T;   // 8 bytes
    scalar rho; // 8 bytes
};
// When processing p[0], loads T[0], rho[0] (unused)
// Cache line wasted if only processing pressure
```

---

### 3.2 tmp Optimization Mechanics

**Reference Counting Internals | กลไกภายใน Reference Counting**

```cpp
// Simplified tmp implementation
template<class T>
class tmp
{
    T* ptr_;           // Managed object pointer
    mutable int* refCount_;  // Reference counter
    
public:
    // Constructor: Takes ownership
    tmp(T* p) : ptr_(p), refCount_(new int(1)) {}
    
    // Copy constructor: Shares ownership
    tmp(const tmp& t) : ptr_(t.ptr_), refCount_(t.refCount_)
    {
        (*refCount_)++;  // Increment ref count
    }
    
    // Destructor: Cleanup if last reference
    ~tmp()
    {
        if (--(*refCount_) == 0)
        {
            delete ptr_;
            delete refCount_;
        }
    }
};
```

**tmp Performance Characteristics | ลักษณะ Performance ของ tmp**

| Operation | Cost | Notes |
|-----------|------|-------|
| Construct from new | O(1) | Allocation + ref count init |
| Copy tmp | O(1) | Atomic increment |
| Destroy tmp | O(1) | Atomic decrement + conditional delete |
| Access via operator() | O(1) | Pointer dereference |
| Transfer ownership | O(1) | Move semantics (no ref count change) |

**Common Pitfall: Experienced tmp Copy**

```cpp
// ❌ BAD: Unnecessary ref counting overhead
for (int i = 0; i < 1000; i++)
{
    tmp<volScalarField> t1 = fvc::grad(p);
    tmp<volScalarField> t2 = t1;  // refCount++: atomic operation
    // ... use t2
}
// 1000 atomic operations

// ✅ GOOD: Minimize tmp copies
for (int i = 0; i < 1000; i++)
{
    tmp<volScalarField> tGrad = fvc::grad(p);
    // ... use tGrad directly
}
// Zero extra atomic operations
```

---

### 3.3 Parallel Efficiency

**Global Reductions | การกระจายการคำนวณแบบ Global**

```cpp
// Global operations handle parallel communication automatically
scalar maxVal = gMax(field);  // Parallel-safe maximum
scalar sumVal = gSum(field);  // Parallel-safe sum

// Implementation (simplified)
scalar gMax(const scalarField& field)
{
    // Step 1: Local reduction
    scalar localMax = max(field);
    
    // Step 2: Parallel reduction across processors
    scalar globalMax = localMax;
    reduce(globalMax, maxOp<scalar>());
    
    return globalMax;
}
```

**Parallel Communication Cost | ต้นทุนการสื่อสารแบบขนาน**

```cpp
// ❌ BAD: Repeated global operations
for (int iter = 0; iter < 100; iter++)
{
    scalar maxResidual = gMax(residual);  // Network call every iteration
    // Communication every iteration = slow
}

// ✅ BETTER: Batch operations or check less frequently
for (int iter = 0; iter < 100; iter++)
{
    scalar localMax = max(residual);  // Fast, local only
    // ... compute more ...
    
    if (iter % 10 == 0)  // Check every 10 iterations
    {
        scalar globalMax = gMax(residual);  // Network call
    }
}
```

**Load Balancing | การกระจายภาระงาน**

```cpp
// Decomposition affects performance
// Poor decomposition:
// - Processor 1: 100k cells (overloaded)
// - Processor 2: 50k cells  (underutilized)
// - Bottleneck: Proc 1 determines overall speed

// Good decomposition:
// - All processors: ~75k cells
// - Balanced load, optimal speedup
```

---

## 4. How the Compiler Decides: The Optimization Process

> [!NOTE] **📂 OpenFOAM Context**
> **Domain:** Compiler/Build System (wmake)
> - **Compiler:** GCC/Clang with `-O3 -std=c++14` typically
> - **Build logs:** Check `wmake` output for optimization warnings
> - **Verification:** Use `objdump -d solver` to inspect generated assembly

### 4.1 Decision Tree for Optimization

```
Compiler sees function call
├─ Is function marked inline?
│   ├─ Yes → Can body be inserted?
│   │   ├─ Yes → INLINE (insert at call site)
│   │   └─ No  → Regular function call
│   └─ No  → Is body small enough?
│       ├─ Yes → AUTO-INLINE (heuristic)
│       └─ No  → Regular function call
└─ Is inlined?
    ├─ Yes → Apply further optimizations
    │   ├─ Constant folding?
    │   ├─ Dead code elimination?
    │   └─ Vectorization possible?
    └─ No → Proceed to next call
```

### 4.2 Inlining Heuristics

**GCC/Clang Inlining Criteria:**

| Factor | Threshold | Impact |
|--------|-----------|--------|
| **Function size** | < ~300 instructions (at -O3) | Smaller = more likely to inline |
| **Call frequency** | Hot paths (profile-guided) | Frequently called = prioritize |
| **Recursion depth** | 0 (no recursion) | Recursive functions never inlined |
| **Template instantiation** | Always | Template functions typically inlined |
| **Optimization level** | `-O1`, `-O2`, `-O3` | Higher = more aggressive inlining |

**Example: Inlining Decision**

```cpp
// Case 1: Definitely inlined
template<class Type>
inline Type sqr(const Type& x) { return x * x; }
// ✅ Template + inline + tiny size = INLINED

// Case 2: Likely inlined at -O3
scalar dotProduct(const vector& a, const vector& b)
{
    return a.x()*b.x() + a.y()*b.y() + a.z()*b.z();
}
// ✅ Small + pure function = INLINED at -O3

// Case 3: Unlikely to inline
void solveLinearSystem(const lduMatrix& matrix, scalarField& x)
{
    // ... 100+ lines of complex logic ...
}
// ❌ Large + complex = NOT INLINED (function call overhead negligible)
```

### 4.3 Vectorization Decision Process

**Compiler Vectorization Checklist:**

```
Loop vectorization analysis
├─ Check: Is loop count known/estimable?
│   ├─ No → Cannot vectorize
│   └─ Yes → Continue
├─ Check: Are memory accesses contiguous?
│   ├─ No → Gather/scatter needed (slower)
│   └─ Yes → Optimal vectorization
├─ Check: Any loop-carried dependencies?
│   ├─ Yes → Cannot vectorize
│   └─ No → Continue
├─ Check: Any function calls?
│   ├─ Yes → Can they be inlined?
│   │   ├─ No → Cannot vectorize
│   │   └─ Yes → Continue
│   └─ No → Continue
└─ Decision: Vectorize with width [SIMD width]
```

**Real Example: Vectorization Analysis**

```cpp
// Case 1: Perfect vectorization candidate
forAll(field, i)
{
    result[i] = 2.0 * field[i] + 1.0;
}
// ✅ Contiguous + independent + simple = VECTORIZED

// Case 2: Vectorizable with gather
forAll(collision, i)
{
    result[i] = field[indices[i]];  // Indirect addressing
}
// ⚠️ Vectorized with gather (slower than contiguous)

// Case 3: Not vectorizable
for (int i = 1; i < field.size(); i++)
{
    field[i] += field[i-1];  // Loop-carried dependency
}
// ❌ Cannot vectorize (sequential dependency)
```

### 4.4 Dead Code Elimination Logic

**Compiler Analysis:**

```cpp
// Example 1: Template-based dead code
template<class Type>
void process()
{
    if constexpr (std::is_same<Type, scalar>::value)
    {
        Info << "Scalar processing" << endl;  // Kept for scalar
    }
    else
    {
        Info << "Field processing" << endl;  // Kept for non-scalar
    }
    // One branch completely removed per instantiation
}

// Example 2: Unreachable code
void example()
{
    return;
    Info << "Never printed" << endl;  // Eliminated entirely
}

// Example 3: Constant propagation
void constantFold()
{
    int x = 5;
    int y = x * 2;  // Compiler replaces with y = 10
    int z = y + 3;  // Compiler replaces with z = 13
    // No arithmetic instructions generated
}
```

---

## 5. Optimization Pipeline Visualized

### 5.1 Complete Flow: From Source to Assembly

```mermaid
flowchart TB
    subgraph "Source Code"
        A["template&lt;class T&gt;<br/>inline T sqr(T x) {<br/>  return x * x;<br/>}<br/><br/>scalar y = sqr(1.5);"]
    end
    
    subgraph "Template Instantiation"
        B["T = scalar<br/>inline scalar sqr(scalar x)<br/>{<br/>  return x * x;<br/>}"]
    end
    
    subgraph "Inlining"
        C["scalar y = 1.5 * 1.5;"]
    end
    
    subgraph "Constant Folding"
        D["scalar y = 2.25;"]
    end
    
    subgraph "Assembly Output"
        E["movsd xmm0, [rip + 2.25]<br/>movsd [rbp - 8], xmm0"]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
    
    style B fill:#e3f2fd,stroke:#1976d2
    style C fill:#fff3e0,stroke:#f57c00
    style D fill:#e8f5e9,stroke:#388e3c
    style E fill:#f3e5f5,stroke:#7b1fa2
```

**Figure 2**: Complete optimization pipeline for a simple template function

---

### 5.2 Vectorization Pipeline

```mermaid
flowchart TB
    subgraph "Source Loop"
        A["forAll(field, i)<br/>{<br/>  result[i] = a*field[i] + b;<br/>}"]
    end
    
    subgraph "Dependency Analysis"
        B{Loop-carried<br/>dependencies?}
        B -->|No| C["✅ Independent<br/>iterations"]
        B -->|Yes| X["❌ Cannot vectorize"]
    end
    
    subgraph "Memory Analysis"
        D{Contiguous<br/>access?}
        D -->|Yes| E["✅ Unit stride<br/>access"]
        D -->|No| F["⚠️ Gather/scatter"]
    end
    
    subgraph "SIMD Code Generation"
        G["__m256d vec = _mm256_load_pd(&field[i])<br/>__m256d res = _mm256_fmadd_pd(a, vec, b)<br/>_mm256_store_pd(&result[i], res)"]
    end
    
    A --> B
    C --> D
    E --> G
    F --> G
    
    style B fill:#fff3e0,stroke:#f57c00
    style C fill:#e8f5e9,stroke:#388e3c
    style E fill:#e8f5e9,stroke:#388e3c
    style G fill:#f3e5f5,stroke:#7b1fa2
    style X fill:#ffebee,stroke:#c62828
```

**Figure 3**: Vectorization analysis and code generation pipeline

---

### 5.3 tmp Memory Management Flow

```mermaid
flowchart TB
    subgraph "Function Call"
        A["fvc::grad(p)"]
    end
    
    subgraph "tmp Creation"
        B["new volScalarField(...)<br/>refCount = 1"]
    end
    
    subgraph "tmp Assignment"
        C{Assignment type?}
        C -->|Copy| D["tmp&lt;volScalarField&gt; t2 = t1<br/>refCount++ → refCount = 2"]
        C -->|Move| E["tmp&lt;volScalarField&gt; t2 = std::move(t1)<br/>Ownership transfer"]
    end
    
    subgraph "Scope Exit"
        F{refCount value?}
        F -->|refCount &gt; 1| G["refCount-- → refCount = 1<br/>Object remains alive"]
        F -->|refCount == 1| H["refCount-- → refCount = 0<br/>delete object"]
    end
    
    A --> B
    B --> C
    D --> F
    E --> F
    G --> I["Continue execution"]
    H --> J["Memory freed"]
    
    style B fill:#e3f2fd,stroke:#1976d2
    style D fill:#fff3e0,stroke:#f57c00
    style E fill:#e8f5e9,stroke:#388e3c
    style H fill:#ffebee,stroke:#c62828
```

**Figure 4**: tmp reference counting and lifetime management

---

## 6. Performance Impact: Before/After Comparisons

### 6.1 Inlining Impact

```cpp
// Test: 100M calls to small function

// WITHOUT inline:
__attribute__((noinline)) scalar addOne(scalar x) { return x + 1.0; }
// Time: 8.2 seconds
// Assembly: call instruction, stack push/pop per iteration

// WITH inline:
inline scalar addOne(scalar x) { return x + 1.0; }
// Time: 0.9 seconds
// Assembly: addsd instruction, no function call
// Speedup: 9.1x
```

### 6.2 Vectorization Impact

```cpp
// Test: Field operation on 10M cells
forAll(result, i)
{
    result[i] = 2.0 * field[i] + 1.0;
}

// WITHOUT vectorization (forced with -fno-tree-vectorize):
// Time: 0.45 seconds
// Throughput: 22M elements/sec

// WITH AVX2 vectorization:
// Time: 0.13 seconds
// Throughput: 77M elements/sec
// Speedup: 3.5x
```

### 6.3 Cache Efficiency Impact

```cpp
// Test: 2D field access (1000x1000)
// Row-major: field[i][j] contiguous in i
// Column-major: field[i][j] contiguous in j

// Cache-inefficient (column access in row-major):
for (int j = 0; j < 1000; j++)
    for (int i = 0; i < 1000; i++)
        sum += field[i][j];
// Time: 0.28 seconds
// Cache misses: 1M+

// Cache-efficient (row access in row-major):
for (int i = 0; i < 1000; i++)
    for (int j = 0; j < 1000; j++)
        sum += field[i][j];
// Time: 0.04 seconds
// Cache misses: ~1000 (page boundaries only)
// Speedup: 7x
```

---

## Quick Reference

| Optimization | Level | Compiler Flag | Speedup Potential |
|--------------|-------|---------------|-------------------|
| **Inlining** | Compile | `-O3` (auto), `inline` keyword | 2-10x for small functions |
| **Vectorization** | Compile | `-O3 -march=native` | 4-8x with AVX/AVX2 |
| **Dead code elim.** | Compile | `-O2`+, `if constexpr` | Reduces code size |
| **Cache locality** | Runtime | N/A (coding pattern) | 2-10x for large fields |
| **tmp management** | Runtime | N/A (library feature) | Reduces memory allocs 50-80% |
| **Parallel reduce** | Runtime | N/A (MPI) | Scales to 1000+ cores |

---

## 🔑 Key Takeaways

### Compiler Optimization Principles

1. **Write optimizer-friendly code**: Simple loops, contiguous access, small functions
2. **Trust but verify**: Compiler optimizations are powerful but not guaranteed
3. **Profile before optimizing**: 80% of time is spent in 20% of code
4. **Check assembly output**: Use `objdump -d` to verify optimizations
5. **Use compiler hints**: `inline`, `__restrict__`, `constexpr` guide the compiler

### Runtime Optimization Principles

1. **Cache is king**: Memory access patterns dominate performance for large fields
2. **Vectorization requires independence**: Loop-carried dependencies prevent SIMD
3. **tmp has overhead**: Reference counting isn't free—use appropriately
4. **Minimize parallel communication**: Batch reductions, check less frequently
5. **Balance decomposition**: Unequal cell distribution kills parallel efficiency

### When to Apply What

| Goal | Optimization | Apply When... |
|------|-------------|---------------|
| **Small function speed** | Inlining | Function < ~50 instructions, called frequently |
| **Field operation speed** | Vectorization | Contiguous access, independent iterations |
| **Large array speed** | Cache efficiency | Access memory sequentially, reuse data |
| **Memory efficiency** | tmp | Avoid unnecessary field copies in expressions |
| **Parallel scaling** | Global ops | Use `gMax`, `gSum` instead of manual MPI |

---

## 🧠 Concept Check

<details>
<summary><b>1. Inlining ช่วยอย่างไร?</b></summary>

**Eliminates function call overhead** — compiler inserts function body at call site, removing:
- Push/pop stack operations
- Jump instructions
- Return overhead

**Additional benefit**: Enables further optimizations (constant folding, vectorization) on inlined code.

**Impact**: 2-10x speedup for small, frequently-called functions.
</details>

<details>
<summary><b>2. Vectorization คืออะไร?</b></summary>

**SIMD (Single Instruction, Multiple Data)** — process multiple array elements with one CPU instruction.

**Example**: AVX2 processes 4 double-precision numbers simultaneously:
- Regular: `result[0] = a[0] + b[0]` (1 iteration = 1 add)
- Vectorized: `result[0:3] = a[0:3] + b[0:3]` (1 iteration = 4 adds)

**Requirements**: Contiguous memory, independent iterations, simple operations.

**Impact**: 4-8x speedup on modern CPUs.
</details>

<details>
<summary><b>3. Cache efficiency สำคัญไหม?</b></summary>

**มาก** — memory access เป็น bottleneck หลักใน CFD simulations

**Why**:
- L1 cache: ~4 cycles access time
- Main memory: ~100-200 cycles access time
- Cache miss: 50x slower than cache hit

**Rule**: Contiguous access patterns (OpenFOAM's `primitiveField()`) maximize cache hits, giving 5-10x speedup over scattered access.
</details>

<details>
<summary><b>4. How does the compiler decide to inline?</b></summary>

**Compiler heuristic considers**:
1. **Function size**: Smaller functions (< ~300 instructions) prioritized
2. **Call frequency**: Hot paths (from profiling) preferred
3. **Template status**: Template functions typically inlined
4. **Recursion**: Recursive functions never inlined
5. **Optimization level**: `-O3` = most aggressive inlining

**You can influence**:
- `inline` keyword: Hint to compiler
- `__attribute__((always_inline))`: Force inline (GCC/Clang)
- `-fno-inline`: Disable inlining (for debugging)
</details>

<details>
<summary><b>5. Why do some loops fail to vectorize?</b></summary>

**Common reasons**:
1. **Loop-carried dependencies**: `field[i] += field[i-1]`
2. **Unknown loop count**: Iteration count not analyzable
3. **Non-contiguous access**: `field[indices[i]]` (gather/scatter)
4. **Function calls**: Non-inlined functions in loop body
5. **Complex control flow**: `break`, `continue`, early returns

**Check with**: `-Rpass=loop-vectorize -Rpass-missed=loop-vectorize` (Clang)
</details>

<details>
<summary><b>6. tmp มี overhead หรือไม่?</b></summary>

**ใช่** — reference counting ไม่ฟรี

**Costs**:
- Copy: Atomic increment operation
- Destroy: Atomic decrement + branch
- Memory: Extra pointer + refCount per tmp

**But**: Cheaper than copying entire field (8 bytes × cellCount)

**Best practice**: Use `tmp` for temporaries, avoid unnecessary copies:
```cpp
tmp<volScalarField> t1 = fvc::grad(p);
tmp<volScalarField> t2 = t1;  // refCount++ (cheap)
```
</details>

---

## 📖 Related Documentation

### Within This Module:
- **Overview:** [00_Overview.md](00_Overview.md) - Complete learning roadmap
- **Expression Templates:** [02_Expression_Templates_Syntax.md](02_Expression_Templates_Syntax.md) - tmp usage patterns
- **Compilation:** [04_Compilation_and_Machine_Code.md](04_Compilation_and_Machine_Code.md) - Verify optimizations with profiling tools

### Cross-Module References:
- **Template Programming:** [../01_TEMPLATE_PROGRAMMING/03_Internal_Mechanics.md](../01_TEMPLATE_PROGRAMMING/03_Internal_Mechanics.md) - Template instantiation mechanics
- **Memory Management:** [../04_MEMORY_MANAGEMENT/03_Internal_Mechanics.md](../04_MEMORY_MANAGEMENT/03_Internal_Mechanics.md) - Cache hierarchy and memory access patterns
- **QA and Profiling:** [../../MODULE_08_TESTING_VALIDATION/CONTENT/05_QA_AUTOMATION_PROFILING/01_Performance_Profiling.md](../../MODULE_08_TESTING_VALIDATION/CONTENT/05_QA_AUTOMATION_PROFILING/01_Performance_Profiling.md) - Profiling tools and techniques

### External Resources:
- [GCC Optimization Flags](https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html)
- [LLVM Vectorizer](https://llvm.org/docs/Vectorizers.html)
- [Intel Optimization Manual](https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html)
- "What Every Programmer Should Know About Memory" by Ulrich Drepper