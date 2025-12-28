# Time & Databases - Common Pitfalls

ปัญหาที่พบบ่อย

---

## 1. Object Not Found

### Problem

```
--> FOAM FATAL ERROR:
    request for object "T" that does not exist
```

### Solution

```cpp
// Always check first
if (mesh.foundObject<volScalarField>("T"))
{
    const volScalarField& T = mesh.lookupObject<volScalarField>("T");
}
else
{
    Warning << "T not found!" << endl;
}
```

---

## 2. Wrong Registry

### Problem

Looking in wrong registry (Time vs mesh)

### Solution

```cpp
// Fields typically register with mesh
mesh.lookupObject<volScalarField>("T");

// Not runTime
// runTime.lookupObject<volScalarField>("T");  // Wrong!
```

---

## 3. Old Time Not Stored

### Problem

```cpp
const volScalarField& T0 = T.oldTime();
// Error if oldTime never stored
```

### Solution

```cpp
// Ensure old time stored (handled by fvm::ddt)
T.storeOldTime();
```

---

## 4. Write Not Called

### Problem

No output written

### Solution

```cpp
// Must call write in loop
while (runTime.loop())
{
    // ... solve
    runTime.write();  // Don't forget!
}
```

Or check `writeControl` in controlDict.

---

## 5. Wrong Time Step

### Problem

CFL violation or numerical instability

### Solution

```cpp
// Use adaptive time stepping
adjustTimeStep  yes;
maxCo           1.0;
maxDeltaT       0.01;
```

---

## 6. Directory Issues

### Problem

Can't find time directory

### Solution

```cpp
// Check time instance
Info << "Instance: " << T.instance() << endl;

// Ensure consistent paths
IOobject header(..., runTime.timeName(), mesh, ...);
```

---

## Quick Troubleshooting

| Problem | Check |
|---------|-------|
| Object not found | `foundObject()` first |
| Wrong value | Check registry (mesh vs time) |
| No output | `runTime.write()` in loop |
| Time mismatch | `timeName()` consistency |

---

## Concept Check

<details>
<summary><b>1. lookup ก่อน found ได้ไหม?</b></summary>

**ไม่ควร** — จะ error ถ้า object ไม่ exists
</details>

<details>
<summary><b>2. ทำไม oldTime() error?</b></summary>

เพราะ **ไม่เคย store** — ใช้ `storeOldTime()` หรือ `fvm::ddt`
</details>

<details>
<summary><b>3. fields register กับอะไร?</b></summary>

**mesh** (fvMesh) ไม่ใช่ runTime
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Object Registry:** [03_Object_Registry.md](03_Object_Registry.md)