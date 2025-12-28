# Smart Pointers in OpenFOAM

Smart Pointers ใน OpenFOAM

---

## Overview

> Smart pointers = Automatic memory management for OpenFOAM objects

| Type | Purpose |
|------|---------|
| `autoPtr` | Unique ownership |
| `tmp` | Temporary with reference counting |
| `PtrList` | List of pointers |

---

## 1. autoPtr

### Unique Ownership

```cpp
// Create with new
autoPtr<volScalarField> fieldPtr(new volScalarField(...));

// Access
volScalarField& field = fieldPtr();
volScalarField& field = *fieldPtr;

// Check validity
if (fieldPtr.valid()) { ... }

// Release ownership
volScalarField* raw = fieldPtr.release();

// Reset
fieldPtr.reset(new volScalarField(...));
fieldPtr.clear();  // Delete and set null
```

### Transfer Ownership

```cpp
// Move semantics
autoPtr<volScalarField> newOwner = std::move(oldOwner);

// After move, oldOwner is null
```

---

## 2. tmp

### Reference Counted Temporary

```cpp
// Create temporary
tmp<volScalarField> tResult(new volScalarField(...));

// Or from existing (const reference)
tmp<volScalarField> tRef(T);  // Stores reference, no copy

// Access
volScalarField& result = tResult();
const volScalarField& result = tResult();

// Check if reference or pointer
tResult.isTmp();  // true if owns memory
```

### Common Usage

```cpp
// Function returning tmp
tmp<volScalarField> computeField()
{
    tmp<volScalarField> tResult
    (
        new volScalarField
        (
            IOobject(...),
            mesh,
            dimensionedScalar(...)
        )
    );
    return tResult;
}

// Use result
tmp<volScalarField> tField = computeField();
volScalarField myField = tField();  // Copies or moves
```

---

## 3. PtrList

### List of Pointers

```cpp
// Create list of 3 pointers
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

// Check if set
if (fields.set(i)) { ... }
```

---

## 4. When to Use What

| Situation | Use |
|-----------|-----|
| Factory function return | `autoPtr` |
| Temporary calculation | `tmp` |
| May be reference | `tmp` |
| Collection of objects | `PtrList` |
| Single owned object | `autoPtr` |

---

## 5. Common Patterns

### Factory Pattern

```cpp
autoPtr<turbulenceModel> turbulence
(
    turbulenceModel::New(U, phi, transport)
);
```

### Return Temporary

```cpp
tmp<volVectorField> gradP()
{
    return fvc::grad(p);  // Returns tmp
}
```

### Lazy Initialization

```cpp
mutable autoPtr<volScalarField> cachedFieldPtr_;

const volScalarField& getCached()
{
    if (!cachedFieldPtr_.valid())
    {
        cachedFieldPtr_.reset(new volScalarField(...));
    }
    return cachedFieldPtr_();
}
```

---

## 6. Common Mistakes

### Double Delete

```cpp
// BAD: Don't use raw pointer after autoPtr takes it
volScalarField* raw = new volScalarField(...);
autoPtr<volScalarField> ptr(raw);
delete raw;  // ERROR: double delete!
```

### Dangling Reference

```cpp
// BAD: tmp destroyed before use
const volScalarField& bad = computeField()();  // tmp destroyed!

// GOOD: Keep tmp alive
tmp<volScalarField> tField = computeField();
const volScalarField& good = tField();
```

---

## Quick Reference

| Method | Description |
|--------|-------------|
| `.valid()` | Check if pointer is set |
| `.reset(ptr)` | Replace with new pointer |
| `.clear()` | Delete and set null |
| `.release()` | Give up ownership |
| `()` or `*` | Dereference |
| `->` | Member access |

---

## Concept Check

<details>
<summary><b>1. autoPtr vs tmp ต่างกันอย่างไร?</b></summary>

- **autoPtr**: Unique ownership, move only
- **tmp**: Reference counted, can share
</details>

<details>
<summary><b>2. ทำไม tmp ใช้กับ fvc:: functions?</b></summary>

เพราะ fvc:: **สร้าง temporary field** → ใช้ tmp เพื่อ avoid copies
</details>

<details>
<summary><b>3. PtrList กับ List<autoPtr> ต่างกันอย่างไร?</b></summary>

**PtrList** มี `.set()` method และ lazy allocation, List<autoPtr> ไม่มี
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Containers:** [05_Containers.md](05_Containers.md)