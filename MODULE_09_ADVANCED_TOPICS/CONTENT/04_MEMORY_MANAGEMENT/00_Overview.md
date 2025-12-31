# Memory Management - Overview

ภาพรวม Memory Management

---

## 🎯 Learning Objectives

**After completing this module, you will be able to:**

- **Understand** the memory management challenges in C++ and OpenFOAM
- **Identify** when to use each smart pointer type (`autoPtr`, `tmp`, `refPtr`, `PtrList`)
- **Apply** proper memory ownership patterns in OpenFOAM code
- **Debug** common memory-related errors (leaks, dangling references, double-free)
- **Optimize** memory usage and performance in your solvers

**เป้าหมายการเรียนรู้:**

- เข้าใจปัญหาการจัดการหน่วยความจำใน C++ และ OpenFOAM
- รู้จักใช้ smart pointer แต่ละประเภทได้อย่างเหมาะสม
- ใช้รูปแบบการเป็นเจ้าของหน่วยความจำที่ถูกต้อง
- แก้ไขข้อผิดพลาดเกี่ยวกับหน่วยความจำ
- ปรับปรุงประสิทธิภาพหน่วยความจำใน solver

---

## 📚 What: Memory Management in OpenFOAM

### The Problem

**Manual memory management in C++ is error-prone:**

```cpp
// ❌ Dangerous manual management
volScalarField* field = new volScalarField(...);
// What if exception occurs here?
delete field;  // Easy to forget!
```

**Common Issues:**
- **Memory leaks**: Allocated but never freed
- **Dangling pointers**: Accessing freed memory
- **Double-free**: Deleting same memory twice
- **Ownership confusion**: Who should delete what?

### The Solution

**OpenFOAM's Smart Pointer Hierarchy:**

| Pointer Type | Ownership Model | Reference Counting | Move-Only | Typical Use |
|--------------|-----------------|-------------------|-----------|-------------|
| `autoPtr<T>` | Unique | ❌ No | ✅ Yes | Factory returns |
| `tmp<T>` | Shared | ✅ Yes | ❌ No | Temporary objects |
| `refPtr<T>` | Optional | ✅ Yes | ❌ No | Reference wrapper |
| `PtrList<T>` | Collection | ❌ No | ✅ Yes | Dynamic arrays |

<!-- IMAGE: IMG_09_005 -->
![Smart Pointer Types](IMG_09_005.jpg)

---

## 💡 Why: Design Principles

### 1. **Automatic Cleanup**

```cpp
// ✅ Automatic when scope ends
{
    autoPtr<Model> model = Model::New(dict);
    model().compute();
}  // <- Automatic delete here
```

### 2. **Clear Ownership**

- **Unique ownership** (`autoPtr`): Only one owner, transfers via move
- **Shared ownership** (`tmp`): Multiple owners via reference counting
- **Collection ownership** (`PtrList`): Owns multiple objects

### 3. **Exception Safety**

```cpp
// ✅ Safe even if compute() throws
tmp<volScalarField> tField = fvc::grad(p);
volScalarField& field = tField();
field = someFunction();  // Might throw
// tmp destructor still runs!
```

### 4. **Performance**

- **Reference counting** avoids unnecessary copies
- **Move semantics** transfers ownership without copying
- **Expression templates** reduce temporary allocations

---

## 🔧 How: Using Smart Pointers

### Quick Decision Tree

```
Need to return from factory?
├─ Yes → autoPtr<T>
└─ No → Need to share with multiple users?
    ├─ Yes → tmp<T>
    └─ No → Need a collection?
        ├─ Yes → PtrList<T>
        └─ No → Might reference existing object?
            └─ Yes → refPtr<T>
```

### Basic Usage Patterns

#### 1. **autoPtr** - Factory Returns

```cpp
// Creating
autoPtr<Model> model = Model::New(dict);

// Accessing
model().compute();

// Transferring ownership
autoPtr<Model> other = std::move(model);
// model is now null!

// Checking
if (model.valid()) { /* ... */ }
```

#### 2. **tmp** - Temporary Objects

```cpp
// Creating
tmp<volScalarField> tField = fvc::grad(p);

// Using reference
volScalarField& field = tField();

// Return from functions
tmp<volScalarField> calculate()
{
    return tmp<volScalarField>(fvc::grad(p));
}
// Automatic cleanup when all refs destroyed
```

#### 3. **PtrList** - Collections

```cpp
// Creating
PtrList<volScalarField> fields(n);

// Setting
fields.set(0, new volScalarField(mesh));
fields.set(1, new volScalarField(mesh));

// Accessing
fields[0].setSize(100);

// Iterating
forAll(fields, i)
{
    fields[i].setSize(100);
}
```

#### 4. **refPtr** - Reference or Pointer

```cpp
// Hold reference
refPtr<volScalarField> rRef(field);

// Hold pointer
refPtr<volScalarField> rPtr(new volScalarField(mesh));

// Use uniformly
if (rRef.valid())
{
    rRef().setSize(100);
}
```

---

## 🗺️ Module Learning Roadmap

### Visual Progression

```
┌─────────────────────────────────────────────────────────────┐
│                    MEMORY MANAGEMENT MODULE                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐      ┌──────────────────┐            │
│  │ 01. Introduction │ ───► │ 02. Syntax       │            │
│ │    What & Why    │      │    How to Use    │            │
│  └──────────────────┘      └──────────────────┘            │
│           │                          │                      │
│           ▼                          ▼                      │
│  ┌──────────────────┐      ┌──────────────────┐            │
│  │ 03. Mechanics    │ ───► │ 04. Theory      │            │
│  │    How Works     │      │    Math Behind   │            │
│  └──────────────────┘      └──────────────────┘            │
│           │                          │                      │
│           └──────────┬───────────────┘                      │
│                      ▼                                      │
│            ┌──────────────────┐                             │
│            │ 05. Patterns     │ ───► ┌──────────────┐      │
│            │    Design        │       │ 06. Practice │      │
│            └──────────────────┘       │  Best Pract. │      │
│                      │                └──────────────┘      │
│                      ▼                       │              │
│            ┌──────────────────┐              ▼              │
│            │ 07. Errors       │ ◄──────── ┌──────────────┐ │
│            │    Debug         │            │ 08. Perf.    │ │
│            └──────────────────┘            │  Optimization│ │
│                                              └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### File Contents

| File | Topic | What You'll Learn | Prerequisites |
|------|-------|-------------------|---------------|
| **01_Introduction** | Basics & Concepts | What smart pointers are, why OpenFOAM needs them | None |
| **02_Syntax** | Usage Patterns | How to use each type in code | 01 |
| **03_Mechanics** | Internal Details | How reference counting, moves work | 01, 02 |
| **04_Theory** | Mathematical Foundation | Memory safety proofs, performance analysis | 01, 03 |
| **05_Patterns** | Design Integration | Combining smart pointers in solver design | 02, 03 |
| **06_Errors** | Debugging | Common issues and solutions | 02, 03 |
| **07_Performance** | Optimization | Cache behavior, memory tuning, profiling | 04, 05 |

### Recommended Learning Path

**Beginner Path** (Focus on usage):
1. 01_Introduction → 02_Syntax → 07_Errors

**Intermediate Path** (Focus on understanding):
1. 01_Introduction → 02_Syntax → 03_Mechanics → 05_Patterns → 06_Errors

**Advanced Path** (Focus on theory & optimization):
1. All files sequentially, with emphasis on 04_Theory and 07_Performance

---

## 🔗 Cross-Module Connections

**Related Concepts in Other Modules:**

- **Templates (Module 9-1)**: Smart pointers are template classes
- **Inheritance (Module 9-2)**: Runtime selection uses `autoPtr`
- **Factory Pattern (Module 9-3)**: Returns `autoPtr<T>` for polymorphic objects
- **Design Patterns (Module 9-3)**: Strategy pattern uses `tmp<T>`

**Prerequisite Knowledge:**

- C++ pointers and references
- Basic C++ templates
- RAII (Resource Acquisition Is Initialization)

---

## 📋 Quick Reference

### Decision Guide

| Need | Use | Example |
|------|-----|---------|
| **Factory return** | `autoPtr<T>` | `Model::New()` returns `autoPtr<Model>` |
| **Temporary object** | `tmp<T>` | `fvc::grad(p)` returns `tmp<volScalarField>` |
| **Pointer collection** | `PtrList<T>` | Boundary conditions list |
| **Reference wrapper** | `refPtr<T>` | Optional field reference |
| **Check validity** | `.valid()` | `if (ptr.valid())` |
| **Get raw pointer** | `.get()` / `.ptr()` | Transfer to legacy API |

### Common Operations

```cpp
// Create
autoPtr<T> ptr(new T(...));
tmp<T> tmpObj = T::New(...);
PtrList<T> list(n);

// Access
ptr().method();      // autoPtr
tmpObj().method();   // tmp
list[i].method();    // PtrList

// Transfer ownership
autoPtr<T> other = std::move(ptr);

// Check
if (ptr.valid()) { /* ... */ }

// Release
T* raw = ptr.release();  // Now you're responsible!
```

---

## 🧠 Concept Check

<details>
<summary><b>1. What's the difference between autoPtr and tmp?</b></summary>

**Answer:**
- **autoPtr**: Unique ownership, move-only, no reference counting
- **tmp**: Shared ownership via reference counting, can be copied

**คำตอบ:**
- **autoPtr**: เจ้าของคนเดียว ย้ายได้อย่างเดียว ไม่มี reference counting
- **tmp**: ใช้ร่วมกันได้ มี reference counting ก็อปปี้ได้
</details>

<details>
<summary><b>2. ทำไม OpenFOAM ต้องใช้ smart pointers?</b></summary>

**คำตอบ:**
- **Automatic cleanup** — ป้องกัน memory leaks โดยอัตโนมัติ
- **Clear ownership** — ชัดเจนว่าใครเป็นเจ้าของหน่วยความจำ
- **Exception safety** — ลบอัตโนมัติแม้เกิด exception
- **Performance** — ลดการ copy ด้วย move semantics
</details>

<details>
<summary><b>3. When does tmp clean up its object?</b></summary>

**Answer:**
When **all references to the tmp object are destroyed** (reference count reaches zero)

**คำตอบ:**
เมื่อ **reference ทั้งหมดถูกทำลาย** (reference count เป็น 0)
</details>

<details>
<summary><b>4. Which smart pointer should you use for a factory method?</b></summary>

**Answer:**
`autoPtr<T>` — because factory methods create new objects and transfer ownership uniquely

**คำตอบ:**
`autoPtr<T>` — เพราะ factory สร้าง object ใหม่และโอนความเป็นเจ้าของ
</details>

---

## 🔑 Key Takeaways

### Core Concepts

1. **Smart pointers automate memory management** in OpenFOAM
2. **Choose the right type** based on ownership needs:
   - `autoPtr` for unique ownership (factory returns)
   - `tmp` for shared temporary objects
   - `PtrList` for collections
   - `refPtr` for optional references
3. **Reference counting** in `tmp` enables safe sharing without manual tracking
4. **Move semantics** transfers ownership efficiently without copying

### Best Practices

✅ **DO:**
- Use `autoPtr` for factory returns
- Use `tmp` for intermediate calculations
- Check `.valid()` before dereferencing
- Use `std::move()` to transfer ownership
- Follow the **Rule of Zero** (let smart pointers manage memory)

❌ **DON'T:**
- Mix raw pointers and smart pointers
- Use `new`/`delete` manually in OpenFOAM code
- Copy `autoPtr` (it's move-only)
- Forget to check validity before use
- Create circular references with `tmp`

### Performance Notes

- **`tmp` overhead**: Reference counting adds atomic operations
- **`autoPtr` efficiency**: Zero overhead when optimized
- **Cache locality**: Smart pointers improve data locality vs. scattered allocations
- **Move semantics**: Essential for performance in expression templates

### Next Steps

**Recommended reading order:**
1. Start with **01_Introduction** for fundamentals
2. Practice with **02_Syntax** examples
3. Understand internals in **03_Mechanics**
4. Learn design patterns in **05_Patterns**
5. Master debugging in **06_Errors**
6. Optimize with **07_Performance**

**สรุปสำคัญ:**
1. Smart pointers จัดการหน่วยความจำอัตโนมัติ
2. เลือกประเภทตามความต้องการความเป็นเจ้าของ
3. Reference counting ทำให้ปลอดภัย
4. Move semantics ถ่ายโอนความเป็นเจ้าของอย่างมีประสิทธิภาพ

---

## 📖 เอกสารที่เกี่ยวข้อง / Related Documents

**ใน Module นี้ (This Module):**
- **Introduction:** [01_Introduction.md](01_Introduction.md) - พื้นฐานและแนวคิด
- **Syntax & Design:** [02_Memory_Syntax_and_Design.md](02_Memory_Syntax_and_Design.md) - วิธีใช้งาน
- **Internal Mechanics:** [03_Internal_Mechanics.md](03_Internal_Mechanics.md) - กลไกภายใน
- **Performance:** [08_Performance_Optimization.md](08_Performance_Optimization.md) - การปรับปรุง performance

**โมดูลที่เกี่ยวข้อง (Related Modules):**
- **Module 9-1 (Templates):** Smart pointers เป็น template classes
- **Module 9-2 (Inheritance):** Runtime selection ใช้ `autoPtr`
- **Module 9-3 (Design Patterns):** Factory pattern คืนค่า `autoPtr<T>`

**แหล่งอ้างอิงเพิ่มเติม:**
- OpenFOAM Source Code: `src/OpenFOAM/memory/*.h`
- C++ Smart Pointers: `std::unique_ptr`, `std::shared_ptr` (C++11)