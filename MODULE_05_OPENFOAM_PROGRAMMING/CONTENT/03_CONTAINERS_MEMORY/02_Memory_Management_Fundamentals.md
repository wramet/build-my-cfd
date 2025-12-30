# Memory Management Fundamentals

พื้นฐานการจัดการหน่วยความจำใน OpenFOAM — RAII และ Smart Pointers

> **ทำไมบทนี้สำคัญที่สุด?**
> - **CFD ใช้ memory มหาศาล** — leak เล็กๆ = crash
> - เข้าใจ `autoPtr` vs `tmp` = เขียน code ที่ปลอดภัย
> - RAII principle = ไม่ต้อง `delete` เอง

---

## Learning Objectives

หลังจากอ่านบทนี้ คุณจะสามารถ:

- **อธิบาย** (Explain) หลักการ RAII และประโยชน์ต่อการจัดการ memory ใน CFD applications
- **เลือกใช้** (Select) smart pointer ที่เหมาะสม (`autoPtr` vs `tmp` vs raw pointer) สำหรับ use case ต่างๆ
- **ประยุกต์ใช้** (Apply) reference counting mechanism เพื่อป้องกัน memory leaks
- **หลีกเลี่ยง** (Avoid) ข้อผิดพลาดทั่วไปในการจัดการ memory ด้วย smart pointers
- **Debug** ปัญหา memory-related ด้วย valgrind และเทคนิคอื่นๆ

---

## Decision Guide: Which Smart Pointer to Use?

| Scenario | Recommended Type | Why? |
|----------|-----------------|------|
| Mesh/Solver objects | `autoPtr<T>` | Exclusive ownership, shouldn't be copied |
| Field calculations | `tmp<T>` | Shared ownership, reference counting saves copies |
| Optional objects | `autoPtr<T>` | Can be empty/null, controlled lifecycle |
| Expression results | `tmp<T>` | Efficient sharing of intermediate results |
| Legacy API integration | Raw `T*` | Only when required by interface |
| Temporary in loop | `tmp<T>` | Reuses memory across iterations |
| Transfer ownership | `autoPtr<T>` + `release()` | Explicit ownership transfer |
| Function return values | `autoPtr<T>` (factory) or `tmp<T>` (computed) | Factory returns owned objects; computed returns shared |

---

## RAII Principle

### What? (Definition)
**Resource Acquisition Is Initialization** — ทรัพยากรถูกจัดการอัตโนมัติตาม object lifetime

### Why? (Motivation/Benefits)
- **Automatic cleanup** — ไม่ต้อง `delete` ด้วยตนเอง
- **Exception-safe** — cleanup แม้มี error หรือ exception
- **No memory leaks** — destructor รับประกันการปล่อย memory
- **Predictable lifecycle** — resource ผูกกับ scope

### How? (Implementation)

```cpp
{
    autoPtr<volScalarField> p(new volScalarField(...));
    // Memory allocated
    
    solve(*p);
    // Memory in use
    
} // Memory freed automatically (destructor called)
```

**Key Mechanism:** Constructor acquires resource → Destructor releases resource

---

## Smart Pointers

<!-- IMAGE: IMG_05_003 -->
<!-- 
Purpose: เพื่อเปรียบเทียบ Memory Ownership Model ของ Smart Pointers 2 ตัวหลักใน OpenFOAM: `autoPtr` (เจ้าของคนเดียว ห้าม Copy) และ `tmp` (ใช้ชั่วคราว ประหยัดแรมสำหรับการคำนวณ Field ขนาดใหญ่). ภาพนี้ต้องสื่อเรื่อง Move Semantics และ Reference Counting
Prompt: "Technical C++ Memory Diagram: `autoPtr` vs `tmp`. **Left Panel (autoPtr):** A single Ptr Object holding a Key to a Data block (Heap). Arrow shows 'Exclusive Ownership'. Action 'Move': The Key is passed to another Ptr, and the original becomes Empty (Null). **Right Panel (tmp):** A Large Matrix Data block. Multiple `tmp` objects pointing to it without copying. A small 'Ref Counter' badge says 'Refs: 1'. Explain that this is for 'Large Field Operations' to avoid deep copying. STYLE: Modern Memory/Heap visualization, distinct colors (Red for exclusive, Blue for shared)."
-->
![[IMG_05_003.jpg]]

### 1. autoPtr — Exclusive Ownership

#### What? (Definition)
Smart pointer ที่มี exclusive ownership ของ resource — move-only, ไม่สามารถ copy ได้

#### Why? (Motivation/Benefits)
- **Clear ownership** — เจ้าของคนเดียวชัดเจน ไม่มีการ share
- **No accidental copies** — compile-time protection ป้องกัน deep copy
- **Efficient** — เพียง pointer transfer (8 bytes)
- **Predictable lifecycle** — ผู้ครอบครองคนเดียว

#### How? (Implementation)

```cpp
template<class T>
class autoPtr
{
    T* ptr_;
    
public:
    explicit autoPtr(T* p) : ptr_(p) {}
    ~autoPtr() { delete ptr_; }  // Automatic cleanup
    
    // Move only (no copy)
    autoPtr(autoPtr&& other) : ptr_(other.ptr_) {
        other.ptr_ = nullptr;
    }
    autoPtr(const autoPtr&) = delete;  // ❌ No copy
    
    T& operator*() { return *ptr_; }
    T* release() { T* t = ptr_; ptr_ = nullptr; return t; }
};
```

#### When to Use
- Mesh, Solver objects — things that shouldn't be copied
- Factory function return values
- Optional objects (can be empty/null)

**Example:**
```cpp
autoPtr<fvMesh> mesh(new fvMesh(...));
// mesh cannot be copied, only moved
```

---

### 2. tmp — Shared Ownership (Reference Counted)

#### What? (Definition)
Smart pointer ที่มี shared ownership ด้วย reference counting — copy ได้โดยไม่ copy data

#### Why? (Motivation/Benefits)
- **Efficient sharing** — หลายตัวชี้ข้อมูลเดียวกันได้
- **No deep copies** — ประหยัด memory สำหรับ large fields
- **Automatic cleanup** — delete เมื่อ reference count = 0
- **Expression templates** — ประหยัด compute time

#### How? (Implementation)

```cpp
template<class T>
class tmp
{
    T* ptr_;
    bool isTemporary_;
    
public:
    tmp(T* p) : ptr_(p), isTemporary_(true) {
        ptr_->ref();  // Increment count
    }
    
    ~tmp() {
        if (ptr_->unref()) delete ptr_;  // Delete if last
    }
    
    tmp(const tmp& t) : ptr_(t.ptr_) {
        ptr_->ref();  // Share, increment count
    }
};
```

#### When to Use
- Fields, expression results — things that can be shared
- Large matrix operations
- Temporary calculations in loops

**Example:**
```cpp
tmp<volScalarField> gradP = fvc::grad(p);
tmp<volScalarField> copy = gradP;  // Shared, no data copy!
```

---

## Reference Counting

### What? (Definition)
Mechanism สำหรับ track จำนวน references ที่ชี้ไปยัง object เดียวกัน

### Why? (Motivation/Benefits)
- **Shared ownership** — หลายส่วน share resource ได้อย่างปลอดภัย
- **Automatic deletion** — object ถูกทำลายเมื่อไม่มีใครใช้
- **Efficient** — ไม่ต้อง copy data จริง

### How? (Implementation)

```cpp
class refCount
{
    mutable int count_;
    
public:
    refCount() : count_(0) {}
    
    void ref() const { ++count_; }
    bool unref() const { return (--count_ == 0); }
    int count() const { return count_; }
};
```

**Lifecycle:**
1. Object created → count = 1
2. Copied/shared → count++
3. Reference destroyed → count--
4. count == 0 → delete object

---

## Quick Reference

| Pointer | Ownership | Copy | Move | Size (64-bit) | When to Use |
|---------|-----------|------|------|---------------|-------------|
| `autoPtr<T>` | Exclusive | ❌ | ✅ | 8 bytes | Mesh, Solver, large objects |
| `tmp<T>` | Shared | ✅ | ✅ | 16 bytes | Fields, temporaries |
| `T*` (raw) | None | ✅ | — | 8 bytes | Avoid unless necessary |

---

## Common Patterns

### Factory Function

#### What? (Definition)
Function ที่สร้างและส่งคืน object พร้อม transfer ownership

#### Why? (Motivation/Benefits)
- **Encapsulation** — ซ่อนการสร้าง object ที่ซับซ้อน
- **Polymorphism** — สร้าง derived types ผ่าน base interface
- **Clear ownership** — caller รับ responsibility ชัดเจน

#### How? (Implementation)

```cpp
autoPtr<dragModel> createDragModel(const dictionary& dict)
{
    return autoPtr<dragModel>(new SchillerNaumann(dict));
    // Ownership transferred to caller
}

// Usage
autoPtr<dragModel> drag = createDragModel(dict);
```

---

### Expression Templates

#### What? (Definition)
Technique สำหรับ optimize การคำนวณ expression โดยหลีกเลี่ยง intermediate copies

#### Why? (Motivation/Benefits)
- **Zero-copy** — แชร์ memory ระหว่าง intermediate results
- **Cache-friendly** — ลด memory bandwidth
- **Fast** — ประหยัดทั้ง memory และ compute time

#### How? (Implementation)

```cpp
// All tmp<> — no unnecessary copies
tmp<volScalarField> result = p + rho*gh;
// Sharing + ref counting = efficient
```

---

### Field Creation

#### What? (Definition)
Pattern สำหรับสร้าง fields ใน OpenFOAM cases

#### Why? (Motivation/Benefits)
- **IO integration** — อ่าน/เขียนจาก file อัตโนมัติ
- **Optional fields** — สร้างเฉพาะเมื่อต้องการ
- **Memory control** — manage lifecycle ชัดเจน

#### How? (Implementation)

```cpp
// In createFields.H
volScalarField p
(
    IOobject("p", runTime.timeName(), mesh, IOobject::MUST_READ),
    mesh
);

// Or with autoPtr for optional fields
autoPtr<volScalarField> pPtr;
if (readP)
{
    pPtr.reset(new volScalarField(...));
}
```

---

## Memory Layout

| Type | Size (64-bit) | Overhead | Notes |
|------|---------------|----------|-------|
| `T*` (raw) | 8 bytes | None | No automatic management |
| `autoPtr<T>` | 8 bytes | None | Move-only overhead |
| `tmp<T>` | 16 bytes | +8 (flag) | Reference counting |
| `refCount` in object | +4 bytes | Per object | Shared by all tmp<T> |

---

## Debugging Tips

### Memory Leaks

#### What? (Definition)
Memory ที่ถูก allocate แต่ไม่ถูก deallocate — accumulate จน crash

#### Why? (Motivation/Benefits)
- **CFD applications** — large meshes amplify leaks
- **Long simulations** — leaks จะชัดเจนในระยะยาว
- **Production reliability** — prevent crashes in critical runs

#### How? (Detection)

```bash
# Use valgrind
valgrind --leak-check=full myFoamApp

# Check output for:
# - "definitely lost": real leaks
# - "indirectly lost": chained leaks
# - "still reachable": typically OK (globals)
```

### Common Mistakes

| Mistake | Problem | Fix | Prevention |
|---------|---------|-----|-------------|
| Raw `new` without smart ptr | Leak | Use `autoPtr` or `tmp` | **Always** wrap allocations |
| Copy `autoPtr` | Compile error | Use `std::move()` | Remember: move-only |
| Access `.ref()` on const tmp | Crash | Check `valid()` first | Validate before access |
| Forget `release()` on transfer | Double delete | Call `release()` | Transfer = release |
| Return raw pointer from factory | Unclear ownership | Return `autoPtr<T>` | Factory = ownership transfer |
| Mixed raw/smart pointers | Double delete | Choose one paradigm | Consistency is key |
| Store `tmp` in container | Premature deletion | Use `autoPtr` or `refPtr` | Containers need stable ownership |

---

## 🧠 Concept Check

<details>
<summary><b>1. autoPtr กับ tmp ต่างกันอย่างไร?</b></summary>

- **autoPtr**: Exclusive ownership, move-only, ใช้กับ object ที่ไม่ควร copy (mesh, solver)
- **tmp**: Shared ownership ด้วย ref counting, ใช้กับ field และ temporaries ที่ต้อง share ได้

**Key distinction**: `autoPtr` = single owner, `tmp` = shared ownership
</details>

<details>
<summary><b>2. RAII ช่วยเรื่อง exception safety อย่างไร?</b></summary>

เมื่อ exception throw stack จะ unwind และ destructors ของ local objects ทุกตัวจะถูกเรียก — ทำให้ memory ถูกปล่อยอัตโนมัติแม้มี error

**Mechanism**: Stack unwinding → destructor calls → automatic cleanup
</details>

<details>
<summary><b>3. ทำไม tmp ใช้ reference counting?</b></summary>

เพื่อให้ expression templates เช่น `p + rho*gh` สามารถ share intermediate results ได้โดยไม่ต้อง copy ข้อมูลจริง — ประหยัดทั้ง memory และ compute time

**Benefit**: One data allocation, multiple efficient references
</details>

<details>
<summary><b>4. เมื่อไหร่ควรใช้ autoPtr vs tmp?</b></summary>

- **ใช้ autoPtr** เมื่อ:
  - Object มีเจ้าของคนเดียวชัดเจน
  - Object ขนาดใหญ่และไม่ควร copy
  - Factory function return values
  - Optional/lazy initialization

- **ใช้ tmp** เมื่อ:
  - Field calculations ที่ต้อง share
  - Expression template results
  - Large matrix operations
  - Temporary values in loops

**Decision rule**: Exclusive ownership → `autoPtr`; Shared access → `tmp`
</details>

---

## Key Takeaways

✅ **RAII Principle** — Resource management ผูกกับ object lifecycle; constructor acquires, destructor releases

✅ **Smart Pointer Selection** — `autoPtr` สำหรับ exclusive ownership (mesh, solver), `tmp` สำหรับ shared access (fields, calculations)

✅ **Reference Counting** — Mechanism ที่ให้หลายตัว share object ได้อย่างปลอดภัย; delete เมื่อ count = 0

✅ **Memory Safety** — Smart pointers prevent leaks, double deletion, dangling pointers; exception-safe โดย default

✅ **Performance** — Expression templates + `tmp` = zero-copy operations; ประหยัย memory และ compute time

✅ **Best Practices** — Avoid raw pointers; use `autoPtr` สำหรับ ownership transfer, `tmp` สำหรับ computed values; debug with valgrind

---

## 📖 เอกสารที่เกี่ยวข้อง

- **บทถัดไป:** [03_Smart_Pointers.md](03_Smart_Pointers.md) — Advanced smart pointer patterns and `refPtr`

---

**Next Steps:** 
1. Practice การเลือกใช้ smart pointers ใน exercises ท้ายบท
2. Debug memory leaks ใน sample code ด้วย valgrind
3. Apply RAII principles ใน custom solver development