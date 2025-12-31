# Common Errors and Debugging in Performance Optimization

ข้อผิดพลาดและการแก้ไขปัญหาด้านประสิทธิภาพ

---

## Learning Objectives

หลังจากอ่านบทนี้ คุณจะสามารถ:
1. **Identify** รู้จักข้อผิดพลาดด้านประสิทธิภาพที่พบบ่อยใน OpenFOAM
2. **Detect** ใช้เครื่องมือ profiler ในการตรวจจับปัญหาด้านประสิทธิภาพ
3. **Quantify** ประเมินผลกระทบของข้อผิดพลาดต่อประสิทธิภาพโดยรวม
4. **Fix** ปรับปรุงและแก้ไขข้อผิดพลาดด้านประสิทธิภาพ
5. **Prevent** ป้องกันการเกิดข้อผิดพลาดซ้ำในการพัฒนาโค้ดครั้งต่อไป

---

## Why This Matters

⚠️ **Performance bugs มักไม่ทำให้โค้ดผิดพลาด แต่ทำให้การคำนวณช้าลงอย่างมาก**

- **Small loops** อาจทำให้โค้ดช้าลง 10-100 เท่า
- **Virtual calls** ใน tight loops สามารถลดประสิทธิภาพ 80-90%
- **Memory leaks** สามารถทำให้การจำลอง crash เมื่อเวลาผ่านไป
- **Unnecessary copies** ทำให้ใช้หน่วยความจำและ CPU time เพิ่มขึ้นอย่างไม่จำเป็น

การเขียนโค้ดที่มีประสิทธิภาพสูงตั้งแต่แรก จะช่วยลดเวลาในการ debug และปรับปรุงประสิทธิภาพในภายหลังได้อย่างมาก

---

## How To Apply

### 📋 Detection vs Fix Strategy

| ขั้นตอน | เครื่องมือ | ระยะเวลา | ผลลัพธ์ที่ได้ |
|---------|-----------|----------|-------------|
| **1. Profile** | perf, valgrind, Instruments | 5-10 นาที | รู้ว่าช้าที่ไหน |
| **2. Analyze** | flame graphs, call graphs | 5-15 นาที | รู้สาเหตุ |
| **3. Fix** | code refactoring | 15-60 นาที | ปรับปรุงโค้ด |
| **4. Verify** | profiler อีกครั้ง | 5-10 นาที | ยืนยันผล |

### 🔍 Prerequisites

- ควรอ่าน [01_Introduction.md](01_Introduction.md) ก่อน เพื่อเข้าใจพื้นฐานด้านประสิทธิภาพ
- ควรอ่าน [02_Expression_Templates_Syntax.md](02_Expression_Templates_Syntax.md) สำหรับการใช้ tmp
- ควรอ่าน [03_Internal_Mechanics.md](03_Internal_Mechanics.md) สำหรับความเข้าใจ virtual function overhead

---

## 1. Allocation in Loop

### 🔴 Problem: Memory Allocation ทุกรอบ

```cpp
while (runTime.loop())
{
    // Allocate NEW volScalarField ทุกรอบ!
    volScalarField temp
    (
        IOobject("temp", runTime.timeName(), mesh, IOobject::NO_READ),
        mesh,
        dimensionedScalar("zero", dimless, 0.0)
    );
    
    temp = computeSomething();
}
```

#### Performance Impact

| จำนวน Cell | Allocation Cost | Total Time (1000 steps) | Speedup |
|-----------|----------------|----------------------|---------|
| 10,000 | ~0.5 ms | 500 ms | 1x |
| 100,000 | ~5 ms | 5,000 ms (5s) | **1x** |
| 1,000,000 | ~50 ms | 50,000 ms (50s) | **1x** |

### 🟢 Solution: Allocate Outside, Reuse Inside

```cpp
// Allocate ครั้งเดียวนอก loop
volScalarField temp
(
    IOobject("temp", runTime.timeName(), mesh, IOobject::NO_READ),
    mesh,
    dimensionedScalar("zero", dimless, 0.0)
);

while (runTime.loop())
{
    temp = computeSomething();  // Reuse
}
```

#### After Fix Performance

| จำนวน Cell | Allocation Cost | Total Time (1000 steps) | Speedup |
|-----------|----------------|----------------------|---------|
| 10,000 | ~0.5 ms (once) | 0.5 ms | **1000x** |
| 100,000 | ~5 ms (once) | 5 ms | **1000x** |
| 1,000,000 | ~50 ms (once) | 50 ms | **1000x** |

### 📊 Profiler Output Example

**Before Fix:**
```
# perf record -g ./solver
# perf report

  45.23%  solver  libOpenFOAM.so      [.] Foam::GeometricField<Foam::double...>::GeometricField
  23.11%  solver  libOpenFOAM.so      [.] Foam::GeometricField<Foam::double...>::~GeometricField
  15.42%  solver  libc-2.31.so        [.] free
  10.15%  solver  libc-2.31.so        [.] malloc
   6.09%  solver  solver              [.] computeSomething
```

**After Fix:**
```
# perf report (after fix)

  78.34%  solver  solver              [.] computeSomething
  12.45%  solver  libOpenFOAM.so      [.] Foam::GeometricField<Foam::double...>::operator=
   5.12%  solver  libm-2.31.so        [.] exp
   4.09%  solver  kernel              [.] memcpy
```

### 🔎 Detection Checklist

- [ ] Check `while (runTime.loop())` หรือ `for` loops
- [ ] Search for `volScalarField`, `volVectorField` declarations inside loops
- [ ] Look for constructor calls in loops
- [ ] Check profiler for malloc/free in hot paths

---

## 2. Not Using tmp

### 🔴 Problem: Unnecessary Temporary Copies

```cpp
// สร้าง temporary volVectorField โดยไม่ตั้งใจ
volScalarField result = fvc::grad(p).component(0);
```

#### Internal Mechanism

```cpp
// เบื้องหลังเกิดอะไรขึ้น:
// 1. fvc::grad(p) สร้าง tmp<volVectorField>
// 2. .component(0) สร้าง volScalarField ใหม่ (copy)
// 3. assignment operator copy อีกครั้ง
// Total: 3 objects created, 2 deleted
```

#### Performance Impact

| Operation | Cost | Frequency | Impact |
|-----------|------|-----------|--------|
| tmp creation | negligible | per call | low |
| volVectorField copy | 5-10 ms | per call | **high** |
| volScalarField copy | 5-10 ms | per call | **high** |
| **Total** | **10-20 ms** | **per call** | **critical** |

### 🟢 Solution: Use tmp<T> Explicitly

```cpp
// ใช้ tmp เพื่อ avoid unnecessary copies
tmp<volVectorField> tgradP = fvc::grad(p);
const volVectorField& gradP = tgradP();  // Reference, no copy
volScalarField result = gradP.component(0);
```

#### Alternative: Const Reference

```cpp
// หรือใช้ const reference ถ้าไม่ต้องการ keep tmp
const volVectorField& gradP = fvc::grad(p)();
volScalarField result = gradP.component(0);
```

#### After Fix Performance

| Operation | Cost | Frequency | Impact |
|-----------|------|-----------|--------|
| tmp creation | negligible | per call | low |
| Reference access | 0 ns | per call | **none** |
| volScalarField creation | 5-10 ms | per call | medium |
| **Total** | **5-10 ms** | **per call** | **50% faster** |

### 📊 Profiler Output Example

**Before Fix:**
```
# perf report

  35.21%  solver  libOpenFOAM.so      [.] Foam::GeometricField<Foam::Vector<double>...>::GeometricField(const Foam::GeometricField<...>&)
  28.45%  solver  libOpenFOAM.so      [.] Foam::GeometricField<Foam::double...>::GeometricField(const Foam::GeometricField<...>&)
  18.32%  solver  kernel              [.] __memcpy_avx_unaligned
  12.11%  solver  libOpenFOAM.so      [.] Foam::fvc::grad<Foam::Vector<double>>
   5.91%  solver  solver              [.] main computation
```

**After Fix:**
```
# perf report (after fix)

  52.34%  solver  solver              [.] main computation
  28.12%  solver  libOpenFOAM.so      [.] Foam::fvc::grad<Foam::Vector<double>>
  12.45%  solver  libOpenFOAM.so      [.] Foam::GeometricField<Foam::Vector<double>>::~GeometricField
   4.32%  solver  libm-2.31.so        [.] sqrt
   2.77%  solver  kernel              [.] __memcpy_avx_unaligned
```

### 🔎 Detection Checklist

- [ ] Search for `fvc::` operations without `tmp<>`
- [ ] Look for chained operations: `fvc::grad(p).component(0)`
- [ ] Check profiler for copy constructors in hot paths
- [ ] Review code for assignment from temporary objects

---

## 3. Cell-by-Cell Virtual Calls

### 🔴 Problem: Virtual Function Call ทุก Cell

```cpp
// Virtual call ทุก cell = millions of calls per time step
forAll(cells, i)
{
    result[i] = model->compute(i);  // Virtual dispatch per cell!
}
```

#### Internal Mechanism

```cpp
// Virtual call mechanism:
// 1. Load vtable pointer from object
// 2. Look up function address in vtable
// 3. Indirect jump through function pointer
// Cost: ~5-10 CPU cycles per call (vs 1 for direct)
```

#### Performance Impact

| Mesh Size | Cells/Step | Calls/Step | Cost/Call | Total Overhead |
|-----------|-----------|-----------|-----------|---------------|
| 10K | 10,000 | 10,000 | 10 cycles | 100K cycles |
| 100K | 100,000 | 100,000 | 10 cycles | 1M cycles |
| 1M | 1,000,000 | 1,000,000 | 10 cycles | **10M cycles** |
| 10M | 10,000,000 | 10,000,000 | 10 cycles | **100M cycles** |

**Translation:** 10M cells = ~10-30ms overhead per time step just for virtual dispatch!

### 🟢 Solution: Batch Operations

```cpp
// Single virtual call, compute all cells at once
result = model->computeField();
```

#### Implementation Example

```cpp
// Before (slow):
class TurbulenceModel
{
public:
    virtual scalar compute(const label cellI) = 0;
};

forAll(result, i)
{
    result[i] = turbulence->compute(i);  // Virtual per cell
}

// After (fast):
class TurbulenceModel
{
public:
    virtual tmp<volScalarField> computeField() = 0;
};

tmp<volScalarField> tResult = turbulence->computeField();
result = tResult();
```

#### After Fix Performance

| Mesh Size | Virtual Calls | Overhead | Speedup |
|-----------|--------------|----------|---------|
| 10K | 1 | negligible | ~1.2x |
| 100K | 1 | negligible | **~5x** |
| 1M | 1 | negligible | **~10x** |
| 10M | 1 | negligible | **~20x** |

### 📊 Profiler Output Example

**Before Fix:**
```
# perf report

  28.45%  solver  solver              [.] TurbulenceModel::compute
  22.34%  solver  solver              [.] 0x0000000000401234  (vtable lookup)
  18.12%  solver  kernel              [.] __memmove_avx_unaligned
  15.67%  solver  libstdc++.so.6      [.] std::vector<double>::operator[]
  10.23%  solver  libm-2.31.so        [.] pow
   5.19%  solver  solver              [.] actual computation
```

**After Fix:**
```
# perf report (after fix)

  65.78%  solver  solver              [.] TurbulenceModel::computeField
  18.23%  solver  libm-2.31.so        [.] pow
  10.12%  solver  kernel              [.] __memmove_avx_unaligned
   3.45%  solver  solver              [.] std::vector<double>::operator[]
   2.42%  solver  libstdc++.so.6      [.] std::vector<double>::size
```

### 🔎 Detection Checklist

- [ ] Search for `forAll` loops calling virtual functions
- [ ] Look for `model->`, `turbulence->` in innermost loops
- [ ] Check profiler for indirect call overhead
- [ ] Review flame graphs for tall narrow peaks (virtual dispatch)

---

## 4. Unnecessary Copies

### 🔴 Problem: Value Semantics When Reference Suffices

```cpp
// Unnecessary copy of entire List
List<scalar> copy = original;

// Unnecessary copy of field
volScalarField copyField = originalField;
```

#### Memory Cost

| Type | Size (1M cells) | Copy Cost | Memory Impact |
|------|----------------|-----------|---------------|
| `List<scalar>` | 8 MB | 2-5 ms | +8 MB |
| `volScalarField` | 24 MB | 10-20 ms | +24 MB |
| `volVectorField` | 72 MB | 30-50 ms | +72 MB |

### 🟢 Solution: Use References

```cpp
// Const reference - no copy
const List<scalar>& ref = original;

// Const reference to field
const volScalarField& refField = originalField;

// Non-const reference if modification needed
List<scalar>& modifiable = original;
```

#### After Fix Performance

| Operation | Before | After | Speedup |
|-----------|--------|-------|---------|
| List copy | 2-5 ms | 0 ns | **∞** |
| Field copy | 10-20 ms | 0 ns | **∞** |
| Memory usage | +X MB | +0 MB | **saves X MB** |

### 📊 Profiler Output Example

**Before Fix:**
```
# perf report

  42.34%  solver  kernel              [.] __memcpy_avx_unaligned
  23.12%  solver  libstdc++.so.6      [.] std::vector<double>::vector(const vector&)
  18.45%  solver  libOpenFOAM.so      [.] Foam::List<double>::List(const List<double>&)
  10.23%  solver  solver              [.] actual computation
   5.86%  solver  libm-2.31.so        [.] sqrt
```

**After Fix:**
```
# perf report (after fix)

  68.45%  solver  solver              [.] actual computation
  15.23%  solver  libm-2.31.so        [.] sqrt
  10.12%  solver  libstdc++.so.6      [.] std::vector<double>::operator[]
   4.32%  solver  libOpenFOAM.so      [.] Foam::List<double>::operator[]
   1.88%  solver  kernel              [.] __memcpy_avx_unaligned
```

### 🔎 Detection Checklist

- [ ] Search for `List<T> copy =` assignments
- [ ] Look for field assignments without `&` reference
- [ ] Check profiler for `memcpy` in unexpected places
- [ ] Review function parameters - pass by value vs const reference

---

## 5. Missing const Correctness

### 🔴 Problem: Compiler Cannot Optimize

```cpp
// Non-const reference - compiler assumes modification
void process(List<scalar>& data)
{
    scalar sum = 0;
    forAll(data, i)
    {
        sum += data[i];  // Must reload every iteration
    }
}
```

#### Performance Impact

| Optimization | Without const | With const | Impact |
|-------------|--------------|-----------|--------|
| Loop unrolling | Limited | Full | 10-20% |
| Vectorization | Disabled | Enabled | 200-400% |
| Register reuse | Limited | Full | 5-10% |

### 🟢 Solution: Use const Where Possible

```cpp
// Const reference - enables optimization
void process(const List<scalar>& data)
{
    scalar sum = 0;
    forAll(data, i)
    {
        sum += data[i];  // Can load once, keep in register
    }
}
```

#### Generated Assembly (simplified)

**Without const:**
```asm
; Compiler must reload data[i] each time
mov rax, [data_ptr]     ; Reload pointer
mov xmm0, [rax + i*8]   ; Load value
add sum, xmm0
```

**With const:**
```asm
; Compiler knows data won't change
mov rax, [data_ptr]     ; Load pointer once
mov xmm0, [rax + i*8]   ; Load value
add sum, xmm0           ; Keep in register
; Unrolled iteration:
add sum, [rax + (i+1)*8]
add sum, [rax + (i+2)*8]
add sum, [rax + (i+3)*8]
```

---

## Complete Detection vs Fix Table

| Error Type | Detection Method | Profiler Signatures | Fix Strategy | Expected Speedup |
|-----------|-----------------|---------------------|--------------|-----------------|
| **Allocation in Loop** | Code review, valgrind | High malloc/free, GeometricField constructor | Move outside loop | 10-1000x |
| **Missing tmp** | Search for fvc:: without tmp<> | High copy constructor time | Use tmp<> or const ref& | 1.5-3x |
| **Virtual in Loop** | forAll with ->, flame graph | High indirect call count | Batch operations | 5-20x |
| **Unnecessary Copy** | Assignments without &, code review | High memcpy, List copy constructor | Use const reference | 2-10x |
| **Missing const** | Function parameter review | Low vectorization, high register pressure | Add const qualifiers | 1.1-1.5x |
| **Poor Cache Locality** | Cache miss profiling | High cache miss rate | Reorder data access | 1.5-3x |

---

## Quick Troubleshooting Guide

### 🚨 Symptom → Solution Mapping

| Symptom | Likely Cause | Quick Fix | Verify With |
|---------|-------------|-----------|-------------|
| **Loop very slow** | Allocation in loop | Move outside | `perf record -e cycles:k` |
| **High memory usage** | Unnecessary copies | Use `const&` | valgrind --massif |
| **Cache thrashing** | Poor data access | Reorder loops | `perf stat -e cache-misses` |
| **Slow function calls** | Virtual dispatch | Batch operations | flame graph |
| **High CPU time, low work** | Copy overhead | tmp optimization | profiler hot spots |
| **No vectorization** | Missing const | Add `const` | `objdump -d -S` |

### 📊 Performance Quantification Template

```cpp
// Add timing to your code:
cpuTime timer;

// Before fix
timer.cpuTimeStart();
// ... slow code ...
scalar slowTime = timer.cpuTimeIncrement();

// After fix
timer.cpuTimeStart();
// ... fast code ...
scalar fastTime = timer.cpuTimeIncrement();

Info << "Speedup: " << slowTime/fastTime << endl;
```

---

## 🧠 Concept Check

<details>
<summary><b>1. Loop allocation ช้าแค่ไหน?</b></summary>

**มาก** — allocation+deallocation ทุก iteration ทำให้ช้าลง 10-1000 เท่าขึ้นกับขนาด mesh
</details>

<details>
<summary><b>2. หา performance issues อย่างไร?</b></summary>

**Profile** ด้วย perf, valgrind หรือ Instruments:
```bash
# Linux
perf record -g ./solver
perf report

# macOS
instruments -t "Time Profiler" ./solver

# Memory profiling
valgrind --tool=massif ./solver
```
</details>

<details>
<summary><b>3. virtual call ช้าเมื่อไหร่?</b></summary>

**ใน tight loops** — millions of calls per step ทำให้ช้าลง 5-20 เท่า ใช้ batch operations แทน
</details>

<details>
<summary><b>4. tmp<> ช่วยอะไร?</b></summary>

**Avoid copies** — ลด temporary object creation ใช้กับ return values จาก fvc:: operations
</details>

<details>
<summary><b>5. const reference ทำอะไร?</b></summary>

**Enable optimization** — compiler สามารถ vectorize, cache, และ optimize ได้ดีขึ้น
</details>

---

## 🎯 Key Takeaways

### ✅ Do's

1. **Profile before optimizing** — ใช้ profiler หา hotspot ก่อน
2. **Allocate once, reuse many** — สร้าง object นอก loop
3. **Use tmp<> for temporaries** — ลด unnecessary copies
4. **Batch virtual calls** — เรียก virtual function ครั้งเดียว
5. **Pass by const reference** — ใช้ `const T&` แทน `T`
6. **Add const everywhere** — ช่วย compiler optimize

### ❌ Don'ts

1. **Don't guess** — อย่าโดเดา ให้ profiler บอก
2. **Don't allocate in loops** — หลีกเลี่ยงสร้าง object ใน loop
3. **Don't copy unnecessarily** — ใช้ reference แทน copy
4. **Don't virtual in hot loops** — หลีกเลี่ยง virtual dispatch ใน tight loops
5. **Don't ignore const** — ใส่ const เพื่อ enable optimization
6. **Don't over-optimize** — เน้นที่ hotspot ก่อน

### 📈 Performance Impact Summary

| Issue | Impact | Fix Difficulty | Speedup |
|-------|--------|---------------|---------|
| Allocation in loop | **Critical** | Easy | 10-1000x |
| Virtual in loop | **High** | Medium | 5-20x |
| Missing tmp | Medium | Easy | 1.5-3x |
| Unnecessary copy | Medium | Easy | 2-10x |
| Missing const | Low | Easy | 1.1-1.5x |

---

## 📖 เอกสารที่เกี่ยวข้อง

### ภายใน Module นี้

- **ภาพรวม:** [00_Overview.md](00_Overview.md) — เหตุผลและประโยชน์ของ performance optimization
- **Introduction:** [01_Introduction.md](01_Introduction.md) — แนวคิดและกระบวนการ optimize
- **Expression Templates:** [02_Expression_Templates_Syntax.md](02_Expression_Templates_Syntax.md) — การใช้ tmp<> อย่างถูกต้อง
- **Internal Mechanics:** [03_Internal_Mechanics.md](03_Internal_Mechanics.md) — เข้าใจ virtual dispatch overhead
- **Design Patterns:** [05_Design_Patterns_and_Trade-offs.md](05_Design_Patterns_and_Trade-offs.md) — การออกแบบเพื่อประสิทธิภาพ

### Cross-Module References

- **Template Programming:** [MODULE_09_ADVANCED_TOPICS/CONTENT/01_TEMPLATE_PROGRAMMING/05_Design_Patterns.md](../../01_TEMPLATE_PROGRAMMING/05_Design_Patterns.md) — Expression templates สำหรับ lazy evaluation
- **Memory Management:** [MODULE_09_ADVANCED_TOPICS/CONTENT/04_MEMORY_MANAGEMENT/05_Implementation_Mechanisms.md](../../04_MEMORY_MANAGEMENT/05_Implementation_Mechanisms.md) — Memory allocation strategies และ reference counting
- **Virtual Functions:** [MODULE_09_ADVANCED_TOPICS/CONTENT/02_INHERITANCE_POLYMORPHISM/07_Performance_Considerations.md](../../02_INHERITANCE_POLYMORPHISM/07_Performance_Considerations.md) — Virtual function overhead และ trade-offs
- **Testing & Validation:** [MODULE_08_TESTING_VALIDATION/CONTENT/05_QA_AUTOMATION_PROFILING/01_Performance_Profiling.md](../../../MODULE_08_TESTING_VALIDATION/CONTENT/05_QA_AUTOMATION_PROFILING/01_Performance_Profiling.md) — เครื่องมือ profiling ที่ใช้ใน practice