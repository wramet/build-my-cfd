# Smart Pointers in OpenFOAM

Smart Pointers ใน OpenFOAM — ป้องกัน memory leaks อัตโนมัติ

## 🎯 Learning Objectives

**หลังจากอ่านบทนี้ คุณจะสามารถ:**
- อธิบาย **What** — Smart pointers คืออะไร และแตกต่างจาก raw pointers อย่างไร
- เข้าใจ **Why** — ทำไม OpenFOAM ต้องใช้ smart pointers และปัญหา memory leaks ที่เกิดขึ้นได้
- ใช้งาน **How** — เลือกและใช้ `autoPtr`, `tmp`, และ `PtrList` อย่างเหมาะสม
- หลีกเลี่ยง common pitfalls ในการใช้งาน smart pointers
- ประยุกต์ใช้ patterns ต่างๆ (lazy initialization, factory pattern) ในการเขียนโค้ด OpenFOAM

---

## Overview: What Are Smart Pointers?

> **💡 คิดแบบนี้:**
> Smart pointer = **กล่องเก็บของที่เก็บกวาดให้อัตโนมัติ**
>
> - Regular pointer: คุณต้อง `delete` เอง → **ลืม = memory leak**
> - Smart pointer: ทิ้งกล่อง ของข้างในถูก delete ให้ → **automatic cleanup**

### Why Do We Need Smart Pointers?

```cpp
// ❌ PROBLEM: Raw pointer - ลืม delete ได้ง่าย
volScalarField* field = new volScalarField(...);
// ... ทำงานไปเรื่อยๆ ...
// ลืม delete → memory leak!
// ใน CFD simulation ที่วนลูป millions of iterations → RAM เต็ม → crash

// ✅ SOLUTION: Smart pointer - auto delete
autoPtr<volScalarField> fieldPtr(new volScalarField(...));
// ... ทำงานไปเรื่อยๆ ...
// fieldPtr ถูกทำลาย → delete อัตโนมัติ ✅
```

**Why memory leaks ร้ายแรงใน CFD?**
- CFD meshes มี cells หลายล้าน → fields ใช้ memory เป็น GB
- Leak เล็กๆ ในแต่ละ time step × 100,000 steps = **หลาย GB หาย**
- Parallel runs → รวม memory leaks ของทุก processor → **cluster crash**

### Types of Smart Pointers

| Type | ลักษณะ | ใช้เมื่อ |
|------|-------|---------|
| `autoPtr` | **1 เจ้าของเท่านั้น** (unique ownership) | Factory pattern, class members |
| `tmp` | **หลายคนอ้างอิงได้** (reference counted) | Temporary calculations, fvc:: functions |
| `PtrList` | **List of pointers** | Collections of objects, polymorphism |

---

## 1. autoPtr — Unique Ownership

### What is autoPtr?

`autoPtr` เป็น smart pointer ที่มีเจ้าของ **คนเดียว** (unique ownership):
- Object มีเจ้าของเพียงคนเดียวเสมอ
- Transfer ownership ได้ (move semantics)
- เมื่อถูกทำลาย → delete object ให้อัตโนมัติ

### Why Use autoPtr?

```cpp
// ❌ WITHOUT autoPtr: ลืม delete
void createField()
{
    volScalarField* field = new volScalarField(...);
    // ลืม delete → memory leak
}

// ✅ WITH autoPtr: auto cleanup
void createField()
{
    autoPtr<volScalarField> fieldPtr(new volScalarField(...));
}  // fieldPtr destroyed → delete automatically ✅
```

### How to Use autoPtr

```cpp
// Create with new
autoPtr<volScalarField> fieldPtr(new volScalarField(...));
// ตอนนี้ fieldPtr เป็นเจ้าของ field

// Access value
volScalarField& field = fieldPtr();   // ใช้ () operator
volScalarField& field = *fieldPtr;    // หรือ * operator

// Check if valid (not null)
if (fieldPtr.valid())
{
    // ใช้ได้อย่างปลอดภัย
}

// Release ownership (คุณรับผิดชอบ delete เอง)
volScalarField* raw = fieldPtr.release();

// Reset with new pointer (old one deleted)
fieldPtr.reset(new volScalarField(...));

// Delete and set null
fieldPtr.clear();
```

#### Transfer Ownership

```cpp
// Move semantics: oldOwner หมดสิทธิ์
autoPtr<volScalarField> newOwner = std::move(oldOwner);

// After move, oldOwner is null!
if (!oldOwner.valid())
{
    Info << "oldOwner is now null" << endl;
}
```

#### Factory Pattern (ใช้บ่อยมาก)

```cpp
// Turbulence model factory
autoPtr<turbulenceModel> turbulence
(
    turbulenceModel::New(U, phi, transport)  // Returns autoPtr
);

// Access
turbulence->correct();
```

---

## 2. tmp — Reference Counted Temporary

### What is tmp?

`tmp` เป็น smart pointer ที่มี **reference counting**:
- หลายตัวแปรสามารถชี้ไป object เดียวกันได้
- นับจำนวนคนที่ใช้งาน (reference count)
- Reference count = 0 → delete object

### Why Use tmp?

```cpp
// ❌ PROBLEM: Copy = ช้ามาก!
tmp<volScalarField> computeBigField()
{
    // Field ขนาด 10 million cells ≈ 80 MB
    return volScalarField(...);  // Copy 80 MB! ช้ามาก
}

// ✅ SOLUTION: tmp = move, ไม่ copy
tmp<volScalarField> computeBigField()
{
    return tmp<volScalarField>(new volScalarField(...));  // Move 40 bytes
}
```

**Why tmp กับ fvc:: functions?**
1. `fvc::grad(p)` สร้าง **volVectorField ใหม่** (ใหญ่มาก ~80 MB)
2. Return by value = copy ทั้ง field (ช้า!)
3. `tmp` หลีกเลี่ยง copy ด้วย move semantics
4. Reference counting ทำให้ safe สำหรับ chained operations

```cpp
// Without tmp: 3 copies!
volVectorField a = fvc::grad(p);         // copy 80 MB
volVectorField b = fvc::div(phi, a);     // copy 80 MB
volScalarField c = fvc::laplacian(a, b); // copy 80 MB
// Total: 240 MB copied

// With tmp: 0 copies!
volScalarField c = fvc::laplacian(fvc::grad(p), fvc::div(phi, U));
// Total: 0 MB copied ✅
```

### How to Use tmp

```cpp
// Create temporary field
tmp<volScalarField> tResult(new volScalarField(...));

// Or wrap existing field (stores reference, no copy!)
tmp<volScalarField> tRef(T);  // T ต้อง const

// Access value
volScalarField& result = tResult();
const volScalarField& result = tResult();

// Check if owns memory vs reference
tResult.isTmp();  // true if owns memory (allocated by new)
```

#### Common Usage Pattern

```cpp
// Function returning tmp
tmp<volScalarField> computeField()
{
    tmp<volScalarField> tResult
    (
        new volScalarField
        (
            IOobject
            (
                "computed",
                mesh.time().timeName(),
                mesh
            ),
            mesh,
            dimensionedScalar("zero", dimless, 0)
        )
    );
    
    // Compute values...
    tResult.ref() = someComputation();
    
    return tResult;  // Move semantics, no copy
}

// Use result
tmp<volScalarField> tField = computeField();
volScalarField myField = tField();  // Copies or moves
```

#### fvc:: Always Returns tmp

```cpp
// fvc functions return tmp
tmp<volVectorField> tGradP = fvc::grad(p);

// Use immediately (common pattern)
volVectorField gradP = fvc::grad(p)();  // Note: ()() at end

// Or keep tmp alive
tmp<volVectorField> tGradP = fvc::grad(p);
forAll(gradP, cellI)
{
    vector g = tGradP()[cellI];  // Access
}
// tGradP destroyed here, memory freed
```

---

## 3. PtrList — List of Pointers

### What is PtrList?

`PtrList<T>` เป็น list ของ smart pointers:
- เก็บ pointers หลายตัวใน list เดียว
- Automatic cleanup เมื่อ list ถูกทำลาย
- Support lazy allocation (set later)

### Why Use PtrList?

```cpp
// ❌ PROBLEM: ต้อง allocate ทุกตัวพร้อมกัน
List<volScalarField> fields(3);
// Must construct all 3 now, even if not ready

// ✅ SOLUTION: PtrList - lazy allocation
PtrList<volScalarField> fields(3);
// Pointers start null, set later when ready
fields.set(0, new volScalarField(...));  // Set first
fields.set(1, new volScalarField(...));  // Set second
// field[2] still null
```

### How to Use PtrList

```cpp
// Create list of 3 pointers (initially null)
PtrList<volScalarField> fields(3);

// Set each element
forAll(fields, i)
{
    fields.set
    (
        i,
        new volScalarField
        (
            IOobject("field" + name(i), ...),
            mesh
        )
    );
}

// Access
volScalarField& f = fields[i];

// Check if set (important for lazy allocation)
if (fields.set(i))
{
    // Element i is valid
}
```

#### Polymorphism with PtrList

```cpp
// Base class pointer list
PtrList<boundaryCondition> bcs(nPatches);

// Can store different derived types
bcs.set(0, new fixedValueBC(...));
bcs.set(1, new zeroGradientBC(...));
// Each element is different type!
```

---

## 4. Decision Guide: When to Use What

### Decision Flowchart

```
Need to manage object?
│
├─ Is it a collection of objects?
│  └─ Yes → Use PtrList
│
├─ Is it from fvc/fvm function?
│  └─ Yes → Use tmp
│
├─ Is it a factory return?
│  └─ Yes → Use autoPtr
│
├─ Is it a class member (owned)?
│  └─ Yes → Use autoPtr
│
└─ Need to avoid copy of const?
   └─ Yes → Use tmp (ref mode)
```

### Comparison Table

| Situation | Use | Why |
|-----------|-----|------|
| Factory function return | `autoPtr` | Unique ownership to caller |
| fvc/fvm return | `tmp` | Temporary, may share reference |
| Class member (owned) | `autoPtr` | Clear ownership, auto cleanup |
| Collection of objects | `PtrList` | Polymorphism, lazy allocation |
| Avoid copy of const | `tmp` (ref mode) | Reference to existing, no copy |

---

## 5. Common Patterns

### Lazy Initialization

```cpp
class MyClass
{
    mutable autoPtr<volScalarField> cachedFieldPtr_;
    
public:
    const volScalarField& getCached() const
    {
        if (!cachedFieldPtr_.valid())
        {
            // Create on first access
            cachedFieldPtr_.reset(new volScalarField(...));
        }
        return cachedFieldPtr_();
    }
};
```

### Optional Field

```cpp
autoPtr<volScalarField> optionalField;

if (needOptionalField)
{
    optionalField.reset(new volScalarField(...));
}

// Check before use
if (optionalField.valid())
{
    optionalField() = ...;
}
```

---

## 6. Common Pitfalls

### ❌ Double Delete

```cpp
// BAD: Don't use raw pointer after autoPtr takes it
volScalarField* raw = new volScalarField(...);
autoPtr<volScalarField> ptr(raw);
delete raw;  // ERROR: double delete! ptr จะ delete อีกครั้ง

// GOOD: ให้ autoPtr ดูแลทั้งหมด
autoPtr<volScalarField> ptr(new volScalarField(...));
// ptr จะ delete เอง
```

### ❌ Dangling Reference

```cpp
// BAD: tmp destroyed before use
const volScalarField& bad = computeField()();  // tmp destroyed here!
// bad is now dangling reference! ชี้ไปหา memory ที่ถูก delete แล้ว

// GOOD: Keep tmp alive
tmp<volScalarField> tField = computeField();
const volScalarField& good = tField();  // tmp lives while we use reference
```

### ❌ Using After Move

```cpp
autoPtr<volScalarField> a(new volScalarField(...));
autoPtr<volScalarField> b = std::move(a);

// BAD: a is now null
// a->someMethod();  // CRASH!

// GOOD: Check first
if (a.valid())
{
    a->someMethod();
}
```

---

## 📋 Quick Reference

| Method | Description | ตัวอย่าง |
|--------|-------------|---------|
| `.valid()` | Check if pointer is set | `if (ptr.valid())` |
| `.reset(ptr)` | Replace with new pointer (old deleted) | `ptr.reset(new T())` |
| `.clear()` | Delete and set null | `ptr.clear()` |
| `.release()` | Give up ownership (you handle delete) | `T* raw = ptr.release()` |
| `()` or `*` | Dereference | `ptr()` or `*ptr` |
| `->` | Member access | `ptr->method()` |
| `.isTmp()` | Check if tmp owns memory (tmp only) | `if (tPtr.isTmp())` |
| `.set(i, ptr)` | Set element i (PtrList only) | `list.set(i, new T())` |

---

## 🎓 Key Takeaways

### Summary Comparison

| Feature | `autoPtr` | `tmp` | `PtrList` |
|---------|-----------|-------|-----------|
| **Ownership** | Unique (1 owner) | Shared (reference counted) | List of owners |
| **Copy** | ❌ Move only | ✅ Copy shares reference | ❌ Move only |
| **Primary Use** | Factory, members | Temporary calculations | Collections |
| **Destructor** | Deletes object | Deletes when ref count = 0 | Deletes all elements |
| **Typical Example** | `turbulenceModel::New()` | `fvc::grad(p)` | List of boundary conditions |
| **Null Check** | `.valid()` | `.valid()` or `.isTmp()` | `.set(i)` |
| **Key Benefit** | Clear ownership | Avoid large copies | Lazy allocation |

### Core Concepts

1. **What** — Smart pointers automate memory management, preventing leaks
2. **Why** — CFD uses massive memory; leaks cause crashes in long simulations
3. **How** — Choose the right type: `autoPtr` (unique), `tmp` (shared), `PtrList` (collections)

### Best Practices

✅ **DO:**
- Use `autoPtr` for factory returns and class members
- Use `tmp` for fvc/fvm operations to avoid copies
- Use `PtrList` for collections with lazy allocation
- Always check `.valid()` before using smart pointers
- Keep `tmp` alive when holding references

❌ **DON'T:**
- Don't manually delete objects owned by smart pointers
- Don't hold references to destroyed `tmp` objects
- Don't use smart pointers after `std::move`
- Don't forget to check validity before access

---

## 🧠 Concept Check

<details>
<summary><b>1. autoPtr vs tmp ต่างกันอย่างไร?</b></summary>

| | autoPtr | tmp |
|-|---------|-----|
| Ownership | **Unique** (1 เจ้าของ) | **Shared** (reference counted) |
| Copy | ❌ ไม่ได้ (move only) | ✅ ได้ (shares reference) |
| ใช้กับ | Factory, members | Temporary calculations |
| ตัวอย่าง | `turbulenceModel::New()` | `fvc::grad(p)` |
</details>

<details>
<summary><b>2. ทำไม tmp ใช้กับ fvc:: functions?</b></summary>

**เหตุผล:**
1. `fvc::grad(p)` สร้าง **volVectorField ใหม่** (ใหญ่มาก ~80 MB)
2. Return by value = copy ทั้ง field (ช้า!)
3. `tmp` หลีกเลี่ยง copy ด้วย move semantics
4. Reference counting ทำให้ safe สำหรับ chained operations

```cpp
// Without tmp: 3 copies = 240 MB!
volVectorField a = fvc::grad(p);         // copy
volVectorField b = fvc::div(phi, a);     // copy
volScalarField c = fvc::laplacian(a, b); // copy

// With tmp: 0 copies!
volScalarField c = fvc::laplacian(fvc::grad(p), fvc::div(phi, U));
```
</details>

<details>
<summary><b>3. PtrList กับ List&lt;autoPtr&gt; ต่างกันอย่างไร?</b></summary>

| | PtrList | List&lt;autoPtr&gt; |
|-|---------|-------------------|
| `.set(i, ptr)` | ✅ มี | ❌ ไม่มี |
| Lazy allocation | ✅ ได้ | ❌ ต้อง initialize ทุกตัว |
| Check if set | `set(i)` returns bool | ต้อง `valid()` เอง |

**แนะนำ:** ใช้ `PtrList` สำหรับ collections
</details>

<details>
<summary><b>4. Dangling reference คืออะไร? ป้องกันอย่างไร?</b></summary>

**Dangling reference:** Reference ที่ชี้ไปหา memory ที่ถูก delete แล้ว

```cpp
// BAD: tmp ถูกทำลายทันที
const volScalarField& bad = computeField()();  // tmp destroyed!
// bad ชี้ไปหา memory ที่ไม่มีแล้ว

// GOOD: เก็บ tmp ไว้
tmp<volScalarField> tField = computeField();  // tmp lives
const volScalarField& good = tField();        // safe
// ใช้ good ได้จนกว่า tField ถูกทำลาย
```
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Basic Primitives:** [02_Basic_Primitives.md](02_Basic_Primitives.md)
- **Containers:** [05_Containers.md](05_Containers.md)
- **Deep Dive:** [../02_DIMENSIONED_TYPES/00_Overview.md](../02_DIMENSIONED_TYPES/00_Overview.md)