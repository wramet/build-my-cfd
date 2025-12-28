# Practical Project - Common Errors

ข้อผิดพลาดที่พบบ่อย

---

## 1. Compilation Errors

### Missing Include

```
error: 'volScalarField' was not declared
```

```cpp
// Fix: Add include
#include "volFields.H"
```

### Missing Link

```
undefined reference to `Foam::turbulenceModel::New`
```

```bash
# Fix: Add to Make/options
EXE_LIBS = -lturbulenceModels
```

---

## 2. RTS Errors

### Type Not Found

```
Unknown model type "myModel"
```

Fix:
1. Check `addToRunTimeSelectionTable`
2. Verify library loaded
3. Check spelling

---

## 3. Runtime Errors

### Dimension Mismatch

```
Inconsistent dimensions for +
```

```cpp
// Fix: Verify dimensions
volScalarField result = rho * sqr(U);  // Check units
```

### Null Pointer

```
Segmentation fault
```

```cpp
// Fix: Check validity
if (ptr.valid()) { ptr(); }
```

---

## 4. Memory Errors

### Dangling Reference

```cpp
// Bad
const volScalarField& bad = fvc::grad(p)();

// Good
tmp<volVectorField> gradP = fvc::grad(p);
const volVectorField& good = gradP();
```

---

## 5. Debugging Tips

```bash
# Compile with debug
export WM_COMPILE_OPTION=Debug
wclean && wmake

# Run with gdb
gdb --args solver -case myCase
```

---

## Quick Troubleshooting

| Error | Fix |
|-------|-----|
| Not declared | Add #include |
| Undefined reference | Add library link |
| Unknown type | Check RTS, libs |
| Dimension | Check physics |
| Segfault | Check pointers |

---

## Concept Check

<details>
<summary><b>1. Undefined reference แก้อย่างไร?</b></summary>

**Link library** ใน Make/options: `-lLibName`
</details>

<details>
<summary><b>2. Dimension mismatch เกิดจากอะไร?</b></summary>

**Physics error** — กำลัง combine incompatible quantities
</details>

<details>
<summary><b>3. Debug build ดีอย่างไร?</b></summary>

**Better error messages** และ works with gdb
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Compilation:** [04_Compilation_process.md](04_Compilation_process.md)