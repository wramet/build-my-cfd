# Smart Pointers in OpenFOAM

Smart Pointers ใน OpenFOAM — ป้องกัน memory leaks อัตโนมัติ

> **ทำไม Smart Pointers สำคัญ?**
> - **CFD ใช้ memory มหาศาล** — leak เล็กๆ × millions of iterations = crash
> - Manual memory management = bugs ที่หายาก
> - OpenFOAM patterns ต้องใช้ autoPtr/tmp ถูกต้อง

---

## Overview

> **💡 คิดแบบนี้:**
> Smart pointer = **กล่องเก็บของที่เก็บกวาดให้อัตโนมัติ**
>
> - Regular pointer: คุณต้อง `delete` เอง
> - Smart pointer: ทิ้งกล่อง ของข้างในถูก delete ให้

| Type | ลักษณะ | ใช้เมื่อ |
|------|-------|---------|
| `autoPtr` | **1 เจ้าของเท่านั้น** | Factory pattern, members |
| `tmp` | **หลายคนอ้างอิงได้** | Temporary calculations |
| `PtrList` | **List of pointers** | Collections of objects |

---

## 1. autoPtr — Unique Ownership

> **ทำไมใช้ autoPtr?**
> - Object มีเจ้าของ **คนเดียว**
> - Transfer ownership ได้ (move semantics)
> - Factory functions return `autoPtr`

### การสร้างและใช้งาน

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

// Reset with new pointer
fieldPtr.reset(new volScalarField(...));

// Delete and set null
fieldPtr.clear();
```

### Transfer Ownership

```cpp
// Move semantics: oldOwner หมดสิทธิ์
autoPtr<volScalarField> newOwner = std::move(oldOwner);

// After move, oldOwner is null!
if (!oldOwner.valid())
{
    Info << "oldOwner is now null" << endl;
}
```

### Factory Pattern (ใช้บ่อยมาก)

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

> **ทำไมใช้ tmp?**
> - `fvc::`, `fvm::` สร้าง **temporary fields** ขนาดใหญ่
> - Copy = ช้ามาก, `tmp` หลีกเลี่ยง copy
> - Reference counting = delete เมื่อไม่มีใครใช้

### การสร้างและใช้งาน

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

### Common Usage Pattern

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

### fvc:: Always Returns tmp

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

> **ทำไมใช้ PtrList?**
> - ต้องการ list ของ objects ที่แตกต่างกัน (polymorphism)
> - Object sizes vary → ใช้ pointers
> - Lazy allocation (set later)

### การสร้างและใช้งาน

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

### Polymorphism with PtrList

```cpp
// Base class pointer list
PtrList<boundaryCondition> bcs(nPatches);

// Can store different derived types
bcs.set(0, new fixedValueBC(...));
bcs.set(1, new zeroGradientBC(...));
// Each element is different type!
```

---

## 4. When to Use What

| Situation | Use | ทำไม |
|-----------|-----|------|
| Factory function return | `autoPtr` | Unique ownership to caller |
| fvc/fvm return | `tmp` | Temporary, may share |
| Class member (owned) | `autoPtr` | Clear ownership |
| Collection of objects | `PtrList` | Polymorphism |
| Avoid copy of const | `tmp` (ref mode) | Reference to existing |

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

## 6. Common Mistakes

### ❌ Double Delete

```cpp
// BAD: Don't use raw pointer after autoPtr takes it
volScalarField* raw = new volScalarField(...);
autoPtr<volScalarField> ptr(raw);
delete raw;  // ERROR: double delete! ptr จะ delete อีกครั้ง
```

### ❌ Dangling Reference

```cpp
// BAD: tmp destroyed before use
const volScalarField& bad = computeField()();  // tmp destroyed here!
// bad is now dangling reference!

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

## Quick Reference

| Method | Description | ตัวอย่าง |
|--------|-------------|---------|
| `.valid()` | Check if pointer is set | `if (ptr.valid())` |
| `.reset(ptr)` | Replace with new pointer | `ptr.reset(new T())` |
| `.clear()` | Delete and set null | `ptr.clear()` |
| `.release()` | Give up ownership | `T* raw = ptr.release()` |
| `()` or `*` | Dereference | `ptr()` or `*ptr` |
| `->` | Member access | `ptr->method()` |

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
1. `fvc::grad(p)` สร้าง **volVectorField ใหม่** (ใหญ่มาก)
2. Return by value = copy ทั้ง field (ช้า!)
3. `tmp` หลีกเลี่ยง copy ด้วย move semantics
4. Reference counting ทำให้ safe สำหรับ chained operations

```cpp
// Without tmp: 3 copies!
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
- **Containers:** [05_Containers.md](05_Containers.md)
- **Deep Dive:** [../03_CONTAINERS_MEMORY/00_Overview.md](../03_CONTAINERS_MEMORY/00_Overview.md)