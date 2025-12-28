# Implementation Mechanisms

กลไกการ Implement Memory Management

---

## Overview

> Smart pointers ใช้ **RAII** และ **reference counting**

---

## 1. RAII Principle

```cpp
// Constructor acquires, destructor releases
class autoPtr
{
    T* ptr_;
public:
    autoPtr(T* p) : ptr_(p) {}      // Acquire
    ~autoPtr() { delete ptr_; }      // Release
};
```

---

## 2. Ownership Transfer

```cpp
// Move semantics
autoPtr(autoPtr&& other) noexcept
: ptr_(other.ptr_)
{
    other.ptr_ = nullptr;  // Source becomes null
}
```

---

## 3. Reference Counting

```cpp
// tmp uses ref count
tmp(const tmp& other)
{
    ptr_ = other.ptr_;
    ++refCount_;
}

~tmp()
{
    if (--refCount_ == 0)
        delete ptr_;
}
```

---

## 4. OpenFOAM tmp Features

```cpp
// Can hold reference (non-owning)
tmp(const T& ref) : ptr_(&ref), isRef_(true) {}

// Check ownership
bool isTmp() const { return !isRef_; }
```

---

## 5. PtrList Implementation

```cpp
template<class T>
class PtrList
{
    T** ptrs_;
    label size_;

public:
    ~PtrList()
    {
        forAll(*this, i)
        {
            delete ptrs_[i];
        }
    }
};
```

---

## Quick Reference

| Pattern | Mechanism |
|---------|-----------|
| autoPtr | Single owner, move |
| tmp | Reference counting |
| PtrList | Array of owned ptrs |

---

## 🧠 Concept Check

<details>
<summary><b>1. RAII คืออะไร?</b></summary>

**Resource Acquisition Is Initialization** — tie lifetime to scope
</details>

<details>
<summary><b>2. Move semantics ทำอะไร?</b></summary>

**Transfer ownership** without copy, nullptr source
</details>

<details>
<summary><b>3. tmp isRef ใช้เมื่อไหร่?</b></summary>

เมื่อ tmp **holds reference** to existing object (non-owning)
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Mechanics:** [03_Internal_Mechanics.md](03_Internal_Mechanics.md)