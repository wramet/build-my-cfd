# Loop Optimization & Vectorization

SIMD and Compiler Optimization

---

## What is Vectorization?

```
Scalar (SISD):           Vector (SIMD):
a[0] = b[0] + c[0]       a[0:7] = b[0:7] + c[0:7]
a[1] = b[1] + c[1]       (8 ops in 1 instruction!)
a[2] = b[2] + c[2]
...
```

> **SIMD = Single Instruction, Multiple Data**
>
> Process 4-8+ elements per instruction

---

## Vector Registers

| Architecture | Width | Elements (double) |
|:---|:---:|:---:|
| SSE | 128 bit | 2 |
| AVX | 256 bit | 4 |
| AVX-512 | 512 bit | 8 |
| ARM NEON | 128 bit | 2 |

```
AVX Register (256 bit):
[double₀][double₁][double₂][double₃]
   64b      64b      64b      64b
```

---

## Auto-Vectorization

Modern compilers can vectorize automatically:

```cpp
// Simple loop - compiler will vectorize
for (label i = 0; i < n; ++i)
{
    c[i] = a[i] + b[i];
}

// Compiler output (conceptually):
for (label i = 0; i < n; i += 4)  // Step by vector width
{
    _mm256_store_pd(&c[i], 
        _mm256_add_pd(
            _mm256_load_pd(&a[i]),
            _mm256_load_pd(&b[i])
        )
    );
}
```

---

## Checking Vectorization

```bash
# GCC: Show vectorization decisions
g++ -O3 -fopt-info-vec-optimized -c code.cpp

# Output:
# code.cpp:10: note: LOOP VECTORIZED

# ICC: Vectorization report
icpc -O3 -qopt-report=5 -c code.cpp

# Clang: 
clang++ -O3 -Rpass=loop-vectorize -c code.cpp
```

---

## Compiler Flags

```bash
# OpenFOAM Make/options
EXE_INC = \
    -O3 \
    -march=native \        # Use CPU's best instructions
    -ffast-math \          # Allow FP reordering
    -funroll-loops         # Unroll small loops
```

> [!WARNING]
> `-ffast-math` may change floating-point results!
> Use carefully for validated CFD codes

---

## What Prevents Vectorization?

### 1. Aliasing

```cpp
// Compiler doesn't know if a and c overlap
void add(double* a, double* b, double* c, int n)
{
    for (int i = 0; i < n; ++i)
        c[i] = a[i] + b[i];  // Can't vectorize safely!
}

// Fix: use restrict
void add(double* __restrict a, double* __restrict b, 
         double* __restrict c, int n)
{
    for (int i = 0; i < n; ++i)
        c[i] = a[i] + b[i];  // Now vectorizable!
}
```

### 2. Dependencies

```cpp
// Bad: loop-carried dependency
for (int i = 1; i < n; ++i)
    a[i] = a[i-1] + b[i];  // Each iteration depends on previous!

// This CANNOT be vectorized
```

### 3. Function Calls

```cpp
// Bad: external function breaks vectorization
for (int i = 0; i < n; ++i)
    a[i] = slow_function(b[i]);  // Not vectorized

// Fix: inline the function
inline double fast_function(double x) { return x * x; }

for (int i = 0; i < n; ++i)
    a[i] = fast_function(b[i]);  // Vectorized!
```

### 4. Conditionals

```cpp
// Bad: branch in loop
for (int i = 0; i < n; ++i)
{
    if (b[i] > 0)
        a[i] = b[i];
    else
        a[i] = -b[i];
}

// Better: branchless
for (int i = 0; i < n; ++i)
{
    a[i] = fabs(b[i]);  // Vectorizable!
}
```

---

## OpenMP SIMD

```cpp
// Explicit SIMD hint
#pragma omp simd
for (label i = 0; i < n; ++i)
{
    result[i] = a[i] * b[i] + c[i];
}

// With reduction
scalar sum = 0;
#pragma omp simd reduction(+:sum)
for (label i = 0; i < n; ++i)
{
    sum += a[i] * a[i];
}
```

---

## OpenFOAM's Approach

### TFOR_ALL Macros

```cpp
// FieldFunctions.C
TFOR_ALL_F_OP_FUNC_F(scalar, result, =, ::Foam::sqr, scalar, f)

// Expands to simple loop that compiler can vectorize
for (label i = 0; i < n; ++i)
{
    result[i] = ::Foam::sqr(f[i]);
}
```

### Field Operators

```cpp
// These are designed for vectorization
volScalarField result = a + b;  // Vectorized add
result = sqr(T);                // Vectorized sqr
result *= 2.0;                  // Vectorized scale
```

---

## Loop Unrolling

```cpp
// Original
for (int i = 0; i < n; ++i)
    a[i] = b[i] + c[i];

// Unrolled (compiler does this)
for (int i = 0; i < n; i += 4)
{
    a[i]   = b[i]   + c[i];
    a[i+1] = b[i+1] + c[i+1];
    a[i+2] = b[i+2] + c[i+2];
    a[i+3] = b[i+3] + c[i+3];
}
```

**Benefit:** Less loop overhead, better instruction pipelining

---

## Benchmarking Vectorization

```cpp
#include <chrono>

auto start = std::chrono::high_resolution_clock::now();

for (int rep = 0; rep < 1000; ++rep)
{
    for (label i = 0; i < n; ++i)
        result[i] = a[i] * b[i];
}

auto end = std::chrono::high_resolution_clock::now();
auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);

Info << "Time: " << duration.count() << " us" << endl;
```

---

## Expression Templates (Avoid Temporaries)

```cpp
// Without expression templates
tmp<volScalarField> t1 = a + b;    // Temp 1
tmp<volScalarField> t2 = t1 * c;   // Temp 2
volScalarField result = t2;        // Copy to result

// With expression templates
volScalarField result = a + b * c; // Single loop, no temps!
```

How it works:
```cpp
// Expression tree (compiled, not runtime)
//        =
//       / \
//   result  +
//          / \
//         a   *
//            / \
//           b   c

// Evaluated as single loop:
for (i = 0; i < n; ++i)
    result[i] = a[i] + b[i] * c[i];
```

---

## Assembly Output จริง: Vectorized vs Non-Vectorized

มาดู assembly code จริงเพื่อเปรียบเทียบ scalar กับ vectorized code

### Example: Simple Vector Addition

**C++ Code:**
```cpp
void vector_add(double* __restrict c,
                const double* __restrict a,
                const double* __restrict b, int n)
{
    for (int i = 0; i < n; ++i)
        c[i] = a[i] + b[i];
}
```

### Compile with Different Flags

**Non-Vectorized (-O1):**
```bash
$ g++ -O1 -S -masm=intel vector_add.cpp -o vector_add_O1.s
```

**Assembly Output (Scalar):**
```asm
; vector_add_O1.s
_Z11vector_addPdPKdS0_i:
    test    esi, esi          ; Check if n > 0
    jle     .L2               ; If n <= 0, return
    xor     eax, eax          ; i = 0
.L3:
    movsd   xmm0, QWORD PTR [rdi+rax*8]    ; Load a[i] (1 double)
    addsd   xmm0, QWORD PTR [rdx+rax*8]    ; b[i] = a[i] + b[i] (SCALAR!)
    movsd   QWORD PTR [rcx+rax*8], xmm0    ; Store c[i]
    add     rax, 1             ; i++
    cmp     rax, rsi           ; i < n?
    jne     .L3                ; Loop back
.L2:
    ret
```

**Characteristics:**
- `movsd`, `addsd` = **scalar** instructions (1 double at a time)
- Loop processes **1 element per iteration**
- ** xmm** registers (128-bit, holding 1 double)

---

**Vectorized (-O3 -march=haswell):**
```bash
$ g++ -O3 -march=haswell -S -masm=intel vector_add.cpp -o vector_add_O3.s
```

**Assembly Output (AVX2 Vectorized):**
```asm
; vector_add_O3.s
_Z11vector_addPdPKdS0_i:
    test    esi, esi          ; Check if n > 0
    jle     .L2
    mov     rax, rsi          ; n
    and     rax, -3           ; Round down to multiple of 4
    je      .L5               ; If n < 4, skip vector loop
    xor     edx, edx          ; i = 0
.L3:
    vmovupd ymm0, YMMWORD PTR [rdi+rdx*8]    ; Load 4 doubles from a[]
    vaddpd  ymm0, ymm0, YMMWORD PTR [rdx+rdx*8]  ; Add 4 doubles from b[] (VECTOR!)
    vmovupd YMMWORD PTR [rcx+rdx*8], ymm0    ; Store 4 doubles to c[]
    add     rdx, 4             ; i += 4 (step by vector width!)
    cmp     rdx, rax           ; i < n_rounded?
    jne     .L3                ; Vector loop back
.L5:
    cmp     rdx, rsi           ; i < n?
    jge     .L2                ; If done, return

    ; Scalar tail (remaining 1-3 elements)
    movsd   xmm0, QWORD PTR [rdi+rdx*8]    ; Load a[i]
    addsd   xmm0, QWORD PTR [rdx+rdx*8]    ; Add b[i]
    movsd   QWORD PTR [rcx+rdx*8], xmm0    ; Store c[i]
    add     rdx, 1             ; i++
    cmp     rdx, rsi
    jne     .L5
.L2:
    vzerupper                  ; Clear ymm registers
    ret
```

**Characteristics:**
- `vmovupd`, `vaddpd` = **AVX2** vector instructions (4 doubles at a time!)
- Loop processes **4 elements per iteration**
- **ymm** registers (256-bit, holding 4 doubles)
- **Scalar tail** handles remaining elements (n % 4)

---

### Performance Comparison

**Benchmark Results:**
```bash
# Non-vectorized (scalar)
Time for 1 billion elements: 2.45 seconds
Throughput: 408 Mops/s

# Vectorized (AVX2, 4-wide)
Time for 1 billion elements: 0.68 seconds
Throughput: 1.47 Gops/s

Speedup: 3.6x
```

**Why not 4x speedup?**
- Loop overhead still present
- Memory bandwidth limited
- Scalar tail for non-multiple sizes

---

## ตรวจสอบ Vectorization ใน OpenFOAM

### วิธี 1: Compiler Report

```bash
# Compile with vectorization report
wclean
wmake > make.log 2>&1

# Check for vectorization messages
grep "LOOP VECTORIZED" make.log
# Output:
# fieldFunctions.C:150: note: LOOP VECTORIZED
# fieldFunctions.C:180: note: LOOP VECTORIZED
# fvMatrix.C:420: note: LOOP VECTORIZED

# Check for failed vectorization
grep "NOT VECTORIZED" make.log
# Output:
# turbulenceModel.C:230: note: not vectorized: data dependence
```

---

### Method 2: Examine Binary with objdump

```bash
# Find function address
$ nm simpleFoam | grep Foam::fvc::grad
000000000050a340 T _ZN4Foam3fvc4gradIdNS_12GeometricFieldId...
$ objdump -d simpleFoam --start-address=0x50a340 --stop-address=0x50a500 | head -50
```

**Output (Non-vectorized):**
```asm
50a340:       48 89 7c 24 08    mov    %rdi,0x8(%rsp)
50a345:       48 83 ec 18       sub    $0x18,%rsp
50a349:       48 89 34 24       mov    %rsi,(%rsp)
50a34d:       f2 0f 10 05      movsd  0x0(%rip),%xmm0        # Load 1 double
50a352:       f2 0f 58 05      addsd  0x0(%rip),%xmm0        # SCALAR add
50a357:       f2 0f 11 04      movsd  %xmm0,(%rsp)          # Store 1 double
```

**Characteristics:**
- `movsd`, `addsd` = **scalar** instructions
- xmm registers (128-bit)

---

**Output (Vectorized with AVX):**
```asm
50a340:       c5 fd 6f 05     vmovupd 0x0(%rip),%ymm0        # Load 4 doubles
50a345:       c5 fd 58 05     vaddpd  0x0(%rip),%ymm0,%ymm0 # VECTOR add (4 at once!)
50a34a:       c5 fd 7f 05     vmovupd %ymm0,0x0(%rip)       # Store 4 doubles
50a34f:       c5 f5 58 c5     vaddpd  %ymm1,%ymm0,%ymm0     # Another vector add
```

**Characteristics:**
- `vmovupd`, `vaddpd` = **AVX** vector instructions (256-bit)
- ymm registers (256-bit, holding 4 doubles)
- 4x throughput!

---

### Method 3: Check Specific Instruction Patterns

```bash
# Count scalar vs vector instructions
$ objdump -d simpleFoam | grep -c "movsd"   # Scalar loads
12543

$ objdump -d simpleFoam | grep -c "vmovupd" # Vector loads (AVX)
87234

$ objdump -d simpleFoam | grep -c "vmulpd"  # Vector mul (AVX)
45621
```

**Interpretation:**
- High count of `vmulpd`, `vaddpd` = **Good vectorization!**
- Mostly `movsd`, `addsd` = **Scalar code** (not optimized)

---

## ตัวอย่าง Vectorization ใน OpenFOAM จริง

### OpenFOAM Field Operations

**Code:**
```cpp
// OpenFOAM/src/finiteVolume/fields/fvPatchFields/calculate fvPatch.H
template<class Type>
void calculate_fvPatch()
{
    const Field<Type>& pf = patchInternalField();
    Field<Type>& newFld = *this;

    forAll(pf, i)
    {
        newFld[i] = pf[i] * 2.0;  // Should vectorize!
    }
}
```

**Compile with flags:**
```bash
EXE_INC = \
    -O3 \
    -march=haswell \
    -fopt-info-vec-merged
```

**Compiler Output:**
```
calculate_fvPatch.H:45:3: note: basic block will be vectorized using 256-bit vectors
calculate_fvPatch.H:45:3: note:   using masks
calculate_fvPatch.H:45:3: note: LOOP VECTORIZED
```

**Assembly (extracted):**
```asm
; Loop body
vmovupd ymm0, YWORD PTR [rsi+rax*8]    ; Load 4 doubles
vmulpd  ymm0, ymm0, YWORD PTR .LC0[rip]  ; Multiply by 2.0 (broadcast)
vmovupd YWORD PTR [rdx+rax*8], ymm0    ; Store 4 doubles
add     rax, 4                          ; i += 4
cmp     rax, r8                         ; Check loop end
jne     .L2                             ; Loop back
```

**Key Instruction:**
```
vmulpd  ymm0, ymm0, YWORD PTR .LC0[rip]
```
- `.LC0` contains constant `2.0` duplicated 4 times
- Single instruction multiplies **4 doubles** by constant!

---

## เปรียบเทียบ Assembly ก่อน/หลัง

### Scenario: บวกสอง Fields

**Non-Optimized Code:**
```cpp
void addFields_scalar(double* result, const double* a, const double* b, int n)
{
    for (int i = 0; i < n; i++)
        result[i] = a[i] + b[i];
}
```

**Assembly (g++ -O1):**
```asm
; Scalar: 1 add per iteration
.L3:
    movsd   xmm0, QWORD PTR [rdi+rax*8]    ; Load a[i]
    addsd   xmm0, QWORD PTR [rsi+rax*8]    ; Add b[i]
    movsd   QWORD PTR [rdx+rax*8], xmm0    ; Store result[i]
    add     rax, 1                          ; i++
    cmp     rax, rcx
    jne     .L3

; Instructions per iteration: 4
; Bytes processed: 8 (1 double)
```

---

**Optimized Code:**
```cpp
void addFields_vector(double* __restrict result,
                      const double* __restrict a,
                      const double* __restrict b, int n)
{
    int i = 0;
    // Vectorized loop (AVX2)
    for (; i + 4 <= n; i += 4)
    {
        __m256d va = _mm256_load_pd(&a[i]);    // Load 4 doubles
        __m256d vb = _mm256_load_pd(&b[i]);    // Load 4 doubles
        __m256d vr = _mm256_add_pd(va, vb);    // Add 4 doubles
        _mm256_store_pd(&result[i], vr);       // Store 4 doubles
    }

    // Scalar tail
    for (; i < n; i++)
        result[i] = a[i] + b[i];
}
```

**Assembly (g++ -O3 -march=haswell -ffast-math):**
```asm
; Vectorized: 4 adds per iteration
.L3:
    vmovupd ymm0, YWORD PTR [rsi+rdx*8]     ; Load 4 doubles from a
    vaddpd  ymm0, ymm0, YWORD PTR [rcx+rdx*8]  ; Add 4 doubles from b
    vmovupd YWORD PTR [rax+rdx*8], ymm0     ; Store 4 doubles
    add     rdx, 4                           ; i += 4
    cmp     rdx, r8
    jne     .L3

; Instructions per iteration: 4 (same!)
; Bytes processed: 32 (4 doubles)
; Speedup: 4x (in theory), 3.2x (measured, due to memory)
```

---

## ตรวจหาปัญหา Vectorization

### ปัญหา 1: Alias Prevention

**Code that won't vectorize:**
```cpp
void multiply(double* a, double* b, int n)  // No __restrict!
{
    for (int i = 0; i < n; i++)
        a[i] = a[i] * b[i];  // Compiler worries about overlap
}
```

**Compiler output:**
```
multiply.cpp:5: note: not vectorized: possible aliasing
multiply.cpp:5: note: not vectorized: data dependence
```

**Fix:**
```cpp
void multiply(double* __restrict a, double* __restrict b, int n)
{
    for (int i = 0; i < n; i++)
        a[i] = a[i] * b[i];  // Now vectorizes!
}
```

---

### ปัญหา 2: Loop-Carried Dependency

**Code that won't vectorize:**
```cpp
void cumulative_sum(double* a, int n)
{
    for (int i = 1; i < n; i++)
        a[i] += a[i-1];  // Each iteration depends on previous!
}
```

**Compiler output:**
```
cumulative_sum.cpp:4: note: not vectorized: unsafe dependent memory operation
```

**This CANNOT be vectorized** — must restructure algorithm

---

## ตรวจสอบ Vectorization ใน OpenFOAM จริง

### Test Case: TField Operations

```bash
# Create test program
$ cat test_vectorize.C
#include "fvCFD.H"

int main()
{
    const int n = 1000000;
    List<scalar> a(n), b(n), c(n);

    forAll(a, i)
    {
        a[i] = i;
        b[i] = i * 2;
    }

    // Test 1: Simple addition (should vectorize)
    forAll(a, i)
        c[i] = a[i] + b[i];

    // Test 2: Square root (harder to vectorize)
    forAll(a, i)
        c[i] = sqrt(a[i]);

    Info << "Done" << endl;
    return 0;
}

# Compile with vectorization report
$ wmake
```

**Compiler Output:**
```
test_vectorize.C:20: note: LOOP VECTORIZED (simple addition)
test_vectorize.C:25: note: LOOP VECTORIZED (sqrt using svml)
```

**Check assembly:**
```bash
$ objdump -d test_vectorize | grep -A 10 "LOOP VECTORIZED"

; Test 1: Addition (4-wide AVX2)
vmovupd ymm0, YWORD PTR [rsi+rax*8]
vaddpd  ymm0, ymm0, YWORD PTR [rcx+rax*8]  ← Vectorized!
vmovupd YWORD PTR [rdx+rax*8], ymm0

; Test 2: Sqrt (4-wide AVX2 with SVML)
vsqrtpd ymm0, YWORD PTR [rsi+rax*8]      ← Vectorized sqrt!
vmovupd YWORD PTR [rdx+rax*8], ymm0
```

**Performance:**
```bash
# Time without vectorization (-O1 -fno-tree-vectorize)
Time: 45 ms

# Time with vectorization (-O3 -march=haswell)
Time: 12 ms

Speedup: 3.75x
```

---

## Concept Check

<details>
<summary><b>1. Loop นี้ vectorize ได้ไหม?</b></summary>

```cpp
for (int i = 1; i < n; ++i)
    a[i] = a[i-1] * 2;
```

**ไม่ได้!** เพราะมี loop-carried dependency

`a[i]` depends on `a[i-1]` ซึ่งคำนวณใน iteration ก่อนหน้า

**Fix:** ไม่มีวิธีแก้ง่ายๆ — ต้อง restructure algorithm
</details>

<details>
<summary><b>2. ทำไม `-ffast-math` อันตราย?</b></summary>

`-ffast-math` enables:
- Reorder operations: `(a+b)+c` → `a+(b+c)`
- Assume no NaN/Inf
- Assume no signed zeros

**Problem:**
- Floating-point is NOT associative
- Results may differ from validated code
- May hide numerical issues

**When to use:**
- Performance critical + numerical stability verified
- Not for validation/certification runs
</details>

---

## Exercise

1. **Check Vectorization:** คอมไพล์ OpenFOAM ด้วย `-fopt-info-vec` และดู output
2. **Fix Aliasing:** เพิ่ม `__restrict` และวัดความเร็ว
3. **Benchmark:** เปรียบเทียบ `-O2` vs `-O3 -march=native`

---

## เอกสารที่เกี่ยวข้อง

- **ก่อนหน้า:** [Memory Layout & Cache](02_Memory_Layout_Cache.md)
- **ถัดไป:** [Parallel Scaling](04_Parallel_Scaling.md)
