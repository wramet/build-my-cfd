# Architecture - Common Errors

ข้อผิดพลาดที่พบบ่อย

---

## 1. RTS Type Not Found

### Problem

```
Unknown turbulenceModel type "myModel"
```

### Solution

1. Check spelling in dictionary
2. Ensure `addToRunTimeSelectionTable` in .C file
3. Link library with `-l` flag

---

## 2. Missing Library

### Problem

```
error while loading shared libraries: libmyLib.so
```

### Solution

```bash
# Add to Make/options
EXE_LIBS = -L$(FOAM_USER_LIBBIN) -lmyLib

# Or set LD_LIBRARY_PATH
export LD_LIBRARY_PATH=$FOAM_USER_LIBBIN:$LD_LIBRARY_PATH
```

---

## 3. Static Initialization Order

### Problem

RTS table not ready when registering

### Solution

```cpp
// Don't use static objects that depend on global tables
// Use function-local statics instead
```

---

## 4. Function Object Not Called

### Problem

Function object registered but never executes

### Solution

```cpp
// Check controlDict
functions
{
    myFunc
    {
        type            myFunctionObject;
        executeControl  timeStep;  // Required!
    }
}
```

---

## 5. Compile Error in RTS

### Problem

```
error: macro "addToRunTimeSelectionTable" requires 4 arguments
```

### Solution

```cpp
addToRunTimeSelectionTable
(
    baseClass,
    derivedClass,
    constructorName  // e.g., dictionary
);
```

---

## Quick Troubleshooting

| Error | Fix |
|-------|-----|
| Unknown type | Check RTS registration |
| Missing library | Link with -l |
| Not called | Check controlDict |
| Macro error | Check arguments |

---

## Concept Check

<details>
<summary><b>1. RTS type not found แก้อย่างไร?</b></summary>

1. Check spelling
2. Verify `addToRunTimeSelectionTable`
3. Link library
</details>

<details>
<summary><b>2. Library loading ต้องทำอะไร?</b></summary>

**Link** with Make/options หรือ set **LD_LIBRARY_PATH**
</details>

<details>
<summary><b>3. Function object ไม่ทำงานเพราะอะไร?</b></summary>

ไม่มี **executeControl** หรือ **type** ผิด
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **RTS:** [02_Runtime_Selection_Tables.md](02_Runtime_Selection_Tables.md)