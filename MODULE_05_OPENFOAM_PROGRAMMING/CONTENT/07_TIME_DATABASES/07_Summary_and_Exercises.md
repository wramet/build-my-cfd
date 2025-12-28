# Time & Databases - Summary and Exercises

สรุปและแบบฝึกหัด

---

## Summary

### Time Methods

| Method | Description |
|--------|-------------|
| `value()` | Current time |
| `deltaT()` | Time step |
| `timeName()` | Time as string |
| `loop()` | Advance and check |
| `write()` | Write outputs |

### Registry Methods

| Method | Description |
|--------|-------------|
| `lookupObject<T>()` | Get by name |
| `foundObject<T>()` | Check exists |
| `store()` | Register object |

---

## Exercise 1: Time Loop

```cpp
#include "createTime.H"
#include "createMesh.H"

while (runTime.loop())
{
    Info << "Time = " << runTime.timeName() << endl;

    scalar t = runTime.value();
    scalar dt = runTime.deltaT().value();

    // ... solve equations

    runTime.write();
}
```

---

## Exercise 2: Object Lookup

```cpp
// Check and lookup
if (mesh.foundObject<volVectorField>("U"))
{
    const volVectorField& U = mesh.lookupObject<volVectorField>("U");
    Info << "Max velocity: " << max(mag(U)).value() << endl;
}
```

---

## Exercise 3: Write Control

```cpp
// system/controlDict
application     simpleFoam;
startTime       0;
endTime         1000;
deltaT          1;

writeControl    timeStep;
writeInterval   100;
```

### Write Options

| writeControl | Meaning |
|--------------|---------|
| `timeStep` | Every N steps |
| `runTime` | Every T seconds |
| `adjustableRunTime` | Adjusted |
| `clockTime` | Wall time |

---

## Exercise 4: Adaptive Time Step

```cpp
// system/controlDict
adjustTimeStep  yes;
maxCo           1.0;
maxDeltaT       0.01;
```

```cpp
// In solver
#include "CourantNo.H"
#include "setDeltaT.H"
```

---

## Exercise 5: Function Objects

```cpp
// system/controlDict
functions
{
    fieldAverage1
    {
        type            fieldAverage;
        writeControl    writeTime;
        fields
        (
            U { mean on; prime2Mean on; }
            p { mean on; }
        );
    }
}
```

---

## Quick Reference

| Task | Code |
|------|------|
| Current time | `runTime.value()` |
| Time step | `runTime.deltaT().value()` |
| Write now | `runTime.write()` |
| Lookup field | `mesh.lookupObject<T>("name")` |
| Check field | `mesh.foundObject<T>("name")` |

---

## Concept Check

<details>
<summary><b>1. loop() vs run() ต่างกันอย่างไร?</b></summary>

- **loop()**: increment time + check end
- **run()**: check end only (no increment)
</details>

<details>
<summary><b>2. writeControl timeStep vs runTime?</b></summary>

- **timeStep**: Write every N iterations
- **runTime**: Write every T seconds
</details>

<details>
<summary><b>3. Function objects ทำอะไร?</b></summary>

**Execute actions** at specified times (averaging, sampling, etc.)
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Object Registry:** [03_Object_Registry.md](03_Object_Registry.md)