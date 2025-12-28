# Memory Management Fundamentals

พื้นฐานการจัดการหน่วยความจำใน OpenFOAM — RAII และ Smart Pointers

> **ทำไมบทนี้สำคัญที่สุด?**
> - **CFD ใช้ memory มหาศาล** — leak เล็กๆ = crash
> - เข้าใจ `autoPtr` vs `tmp` = เขียน code ที่ปลอดภัย
> - RAII principle = ไม่ต้อง `delete` เอง

---

## RAII Principle

**Resource Acquisition Is Initialization** — ทรัพยากรถูกจัดการอัตโนมัติตาม object lifetime

```cpp
{
    autoPtr<volScalarField> p(new volScalarField(...));
    // Memory allocated
    
    solve(*p);
    // Memory in use
    
} // Memory freed automatically (destructor)
```

**ข้อดี:**
- ไม่ต้อง `delete` ด้วยตนเอง
- Exception-safe (cleanup แม้มี error)
- ไม่มี memory leaks

---

## Smart Pointers

### 1. autoPtr — Exclusive Ownership

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

**Use for:** Mesh, Solver objects — things that shouldn't be copied

```cpp
autoPtr<fvMesh> mesh(new fvMesh(...));
// mesh cannot be copied, only moved
```

---

### 2. tmp — Shared Ownership (Reference Counted)

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

**Use for:** Fields, expression results — things that can be shared

```cpp
tmp<volScalarField> gradP = fvc::grad(p);
tmp<volScalarField> copy = gradP;  // Shared, no data copy!
```

---

## Reference Counting

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

| Pointer | Ownership | Copy | When to Use |
|---------|-----------|------|-------------|
| `autoPtr<T>` | Exclusive | ❌ Move only | Mesh, Solver, large objects |
| `tmp<T>` | Shared | ✅ Ref count | Fields, temporaries |
| `T*` (raw) | None | — | Avoid unless necessary |

---

## Common Patterns

### Factory Function

```cpp
autoPtr<dragModel> createDragModel(const dictionary& dict)
{
    return autoPtr<dragModel>(new SchillerNaumann(dict));
    // Ownership transferred to caller
}

// Usage
autoPtr<dragModel> drag = createDragModel(dict);
```

### Expression Templates

```cpp
// All tmp<> — no unnecessary copies
tmp<volScalarField> result = p + rho*gh;
// Sharing + ref counting = efficient
```

### Field Creation

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

| Type | Size (64-bit) | Overhead |
|------|---------------|----------|
| `T*` (raw) | 8 bytes | None |
| `autoPtr<T>` | 8 bytes | None |
| `tmp<T>` | 16 bytes | +8 (flag) |
| `refCount` in object | +4 bytes | Per object |

---

## Debugging Tips

### Memory Leaks

```bash
# Use valgrind
valgrind --leak-check=full myFoamApp
```

### Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Raw `new` without smart ptr | Leak | Use `autoPtr` or `tmp` |
| Copy `autoPtr` | Compile error | Use `std::move()` |
| Access `.ref()` on const tmp | Crash | Check `valid()` first |
| Forget `release()` on transfer | Double delete | Call `release()` |

---

## 🧠 Concept Check

<details>
<summary><b>1. autoPtr กับ tmp ต่างกันอย่างไร?</b></summary>

- **autoPtr**: Exclusive ownership, move-only, ใช้กับ object ที่ไม่ควร copy (mesh, solver)
- **tmp**: Shared ownership ด้วย ref counting, ใช้กับ field และ temporaries ที่ต้อง share ได้
</details>

<details>
<summary><b>2. RAII ช่วยเรื่อง exception safety อย่างไร?</b></summary>

เมื่อ exception throw stack จะ unwind และ destructors ของ local objects ทุกตัวจะถูกเรียก — ทำให้ memory ถูกปล่อยอัตโนมัติแม้มี error
</details>

<details>
<summary><b>3. ทำไม tmp ใช้ reference counting?</b></summary>

เพื่อให้ expression templates เช่น `p + rho*gh` สามารถ share intermediate results ได้โดยไม่ต้อง copy ข้อมูลจริง — ประหยัดทั้ง memory และ compute time
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [01_Container_Types.md](01_Container_Types.md)
- **บทถัดไป:** [03_Smart_Pointers.md](03_Smart_Pointers.md)