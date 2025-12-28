# Memory Management - Common Errors

ข้อผิดพลาดที่พบบ่อย

---

## 1. Dangling Reference

### Problem

```cpp
const volScalarField& bad = fvc::grad(p)().component(0);
// tmp destroyed, reference invalid!
```

### Solution

```cpp
// Keep tmp alive
tmp<volVectorField> gradP = fvc::grad(p);
volScalarField gradPx = gradP().component(0);
```

---

## 2. Memory Leak

### Problem

```cpp
Model* model = new Model(...);
// Forgot delete!
```

### Solution

```cpp
autoPtr<Model> model(new Model(...));
// Automatic deletion
```

---

## 3. Double Delete

### Problem

```cpp
ptr = list[0];  // Shallow copy
delete list[0];
delete ptr;     // Double delete!
```

### Solution

```cpp
// Use smart pointers
autoPtr<T> ptr = list.release(0);
```

---

## 4. Invalid autoPtr Access

### Problem

```cpp
autoPtr<T> ptr;
ptr();  // Error: null pointer
```

### Solution

```cpp
if (ptr.valid())
{
    ptr();
}
```

---

## 5. tmp Not Stored

### Problem

```cpp
fvc::grad(p);  // Result discarded immediately
```

### Solution

```cpp
tmp<volVectorField> gradP = fvc::grad(p);
```

---

## 6. Ownership Confusion

### Problem

```cpp
autoPtr<T> a = some;
autoPtr<T> b = a;  // Now a is null!
b();  // OK
a();  // Error!
```

### Solution

```cpp
// Be aware of move semantics
autoPtr<T> b = std::move(a);  // Explicit
```

---

## Quick Troubleshooting

| Error | Fix |
|-------|-----|
| Dangling ref | Keep tmp alive |
| Memory leak | Use smart pointers |
| Null access | Check `.valid()` |
| Double delete | Use autoPtr/tmp |

---

## Concept Check

<details>
<summary><b>1. tmp scope ทำไมสำคัญ?</b></summary>

เพราะ **memory freed** เมื่อ tmp หมด scope
</details>

<details>
<summary><b>2. autoPtr copy ทำอะไร?</b></summary>

**Move ownership** — source becomes null
</details>

<details>
<summary><b>3. .valid() ใช้ทำไม?</b></summary>

**Check if pointer is non-null** before access
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Syntax:** [02_Memory_Syntax_and_Design.md](02_Memory_Syntax_and_Design.md)