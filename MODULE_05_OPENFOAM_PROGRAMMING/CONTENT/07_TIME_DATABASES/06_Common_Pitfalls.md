# Common Pitfalls - Time & Databases

Learning Objectives
- Identify and prevent common runtime errors in time management and object registry operations
- Debug object lookup failures and registry issues
- Optimize time-stepping performance and avoid memory leaks
- Understand write control mechanisms and output pitfalls

---

## 1. Object Lookup Failures

### 1.1 Requesting Non-Existent Objects

**Problem:**
```
--> FOAM FATAL ERROR:
    request for object "T" that does not exist
```

**Prevention Strategy:**
```cpp
// ALWAYS check existence first
if (mesh.foundObject<volScalarField>("T"))
{
    const volScalarField& T = mesh.lookupObject<volScalarField>("T");
}
else
{
    Warning << "Field 'T' not found in registry!" << endl;
    // Handle gracefully or create field
}
```

**Key Insight:** `lookupObject<T>()` throws fatal error if object doesn't exist. Use `foundObject<T>()` as guard condition.

---

### 1.2 Wrong Registry Lookup

**Problem:**
```cpp
// WRONG - Looking in Time registry for fields
const volScalarField& T = runTime.lookupObject<volScalarField>("T");
// FATAL ERROR: Object not found
```

**Prevention Strategy:**
```cpp
// CORRECT - Fields register with mesh, not Time
const volScalarField& T = mesh.lookupObject<volScalarField>("T");

// Time registry contains: Time, runTime, global objects
// Mesh registry contains: fields, boundary conditions, mesh data
```

**Quick Reference:**
| Object Type | Registry |
|-------------|----------|
| volScalarField, volVectorField | `mesh.lookupObject` |
| Time, runTime | `runTime.lookupObject` |
| mesh-related objects | `mesh.lookupObject` |
| global universal objects | `runTime.lookupObject` |

---

## 2. Time Storage Issues

### 2.1 Old Time Not Stored

**Problem:**
```cpp
const volScalarField& T0 = T.oldTime();
// FATAL ERROR: oldTime() not previously stored
```

**Prevention Strategy:**
```cpp
// Option 1: Explicit storage (rarely needed)
T.storeOldTime();

// Option 2: Let fvMatrix handle it (preferred)
fvMatrix<scalar> TEqn(fvm::ddt(T) + ...);
// fvm::ddt automatically calls storeOldTime()

// Option 3: Check before accessing
if (T.nOldTimes() > 0)
{
    const volScalarField& T0 = T.oldTime();
}
```

**Key Insight:** Transient schemes require previous time step data. Always ensure old times exist before accessing.

---

### 2.2 Time Precision Mismatches

**Problem:**
```cpp
// Case setup expects precision 6
timePrecision  6;

// But code writes with default precision
// Results in: 0.001 vs 0.001000 (directory mismatch)
```

**Prevention Strategy:**
```cpp
// In controlDict
application     simpleFoam;
startFrom       latestTime;
timePrecision   6;  // Matches time step size

// In custom code
runTime.setTimeProperties(timePrecision, 6);
```

**Common Issue:** Time directories like `0.001` vs `0.001000` cause "cannot find file" errors.

---

## 3. Write Control Pitfalls

### 3.1 Missing write() Calls

**Problem:**
```cpp
while (runTime.loop())
{
    solve(UEqn == -fvc::grad(p));
    // No runTime.write() - NO OUTPUT!
}
```

**Prevention Strategy:**
```cpp
while (runTime.loop())
{
    solve(UEqn == -fvc::grad(p));
    runTime.write();  // REQUIRED for output
}

// Check write settings in controlDict
writeControl    timeStep;
writeInterval   100;
```

---

### 3.2 purgeWrite Misunderstandings

**Problem:**
```cpp
// controlDict
purgeWrite  2;  // Keeps only latest 2 time directories
// User expects: Keeps 0, 100, 200, 300...
// Reality: Only keeps 200, 300 (loses 0, 100)
```

**Prevention Strategy:**
```cpp
// controlDict settings
purgeWrite  5;  // Keeps last 5 time directories

// For archiving important times:
writeControl    outputTime;
writeInterval   1;
purgeWrite      0;  // Never purge (manual cleanup)
```

**Key Insight:** `purgeWrite N` keeps only the N most recent time directories. Critical restart data (like `0/`) may be lost!

---

### 3.3 Excessive Write Frequency

**Problem:**
```cpp
// controlDict
writeControl    timeStep;
writeInterval   1;  // Writes EVERY time step
// Causes massive I/O overhead
```

**Prevention Strategy:**
```cpp
// Option 1: Write every N time steps
writeControl    timeStep;
writeInterval   100;

// Option 2: Write at specific times
writeControl    runTime;
writeInterval   0.1;  // Every 0.1 seconds

// Option 3: Adjustable time step + writeInterval
writeControl    adjustableRunTime;
writeInterval   0.05;
maxCo           1.0;
```

**Performance Impact:** Writing every time step can increase simulation time by 10-100x.

---

## 4. Registry Memory Leaks

### 4.1 Manual Store() Without Ownership Transfer

**Problem:**
```cpp
// WRONG - Creates memory leak
volScalarField* T = new volScalarField(...);
mesh.objectRegistry::store(T);

// Later in loop
volScalarField* T2 = new volScalarField(...);
mesh.objectRegistry::store(T2);  // Leak! Old T not deleted
```

**Prevention Strategy:**
```cpp
// Option 1: Use autoPtr (RECOMMENDED)
autoPtr<volScalarField> TPtr
(
    new volScalarField(...)
);
mesh.objectRegistry::store(TPtr.ptr());  // Transfers ownership

// Option 2: Use tmp (for temporary fields)
tmp<volScalarField> tT
(
    new volScalarField(...)
);
tT.ref().rename("T");

// Option 3: Check before storing
if (!mesh.foundObject<volScalarField>("T"))
{
    mesh.objectRegistry::store(new volScalarField(...));
}
```

**Key Insight:** Registry takes ownership. Always check existence or use smart pointers.

---

### 4.2 Circular Registry Dependencies

**Problem:**
```cpp
// Field A references Field B
volScalarField& A = mesh.lookupObject<volScalarField>("A");
const volScalarField& B = mesh.lookupObject<volScalarField>("B");

// Field B references Field A (in initialization)
// Causes circular dependency during destruction
```

**Prevention Strategy:**
```cpp
// Use references/pointers carefully
// Clear references before destruction:
A.clear();
B.clear();

// Or use weak references via name lookup:
if (mesh.foundObject<volScalarField>("A"))
{
    const volScalarField& A = mesh.lookupObject<volScalarField>("A");
    // Use A
    // Reference invalid after scope - safe
}
```

---

## 5. Time-Stepping Pitfalls

### 5.1 CFL Violation from Fixed Time Steps

**Problem:**
```cpp
// controlDict
deltaT      0.01;
maxCo       1.0;  // Ignored with fixed deltaT!
// Results in instability if velocity increases
```

**Prevention Strategy:**
```cpp
// Enable adaptive time stepping
adjustTimeStep  yes;
maxCo           1.0;
maxDeltaT       0.01;
minDeltaT       1e-4;

// Solver will automatically reduce deltaT if maxCo exceeded
```

**Key Insight:** `maxCo` only works with `adjustTimeStep yes`.

---

### 5.2 runTimeModifiable Performance Cost

**Problem:**
```cpp
// controlDict
runTimeModifiable yes;  // Re-reads dictionaries EVERY time step
// Causes 5-10% performance overhead
```

**Prevention Strategy:**
```cpp
// Production runs (no modifications needed)
runTimeModifiable no;  // Faster

// Development/debugging runs
runTimeModifiable yes;  // Allows dictionary updates
```

**Performance Impact:** ~5% overhead for re-parsing dictionaries every time step.

---

## 6. Directory and Path Issues

### 6.1 Time Directory Mismatches

**Problem:**
```
Cannot find file "0.001/T"
but directory "0.001000/T" exists
```

**Prevention Strategy:**
```cpp
// Check time instance
Info << "Field instance: " << T.instance() << endl;
Info << "runTime.timeName(): " << runTime.timeName() << endl;

// Ensure consistent IOobject construction
IOobject header
(
    "T",
    runTime.timeName(),  // Use runTime for consistency
    mesh,
    IOobject::MUST_READ,
    IOobject::AUTO_WRITE
);

// Verify directory exists
fileName timePath = runTime.path()/runTime.timeName();
if (!isDir(timePath))
{
    FatalError << "Time directory not found: " << timePath
               << exit(FatalError);
}
```

---

## Quick Troubleshooting Guide

| Symptom | Likely Cause | Quick Fix |
|---------|-------------|-----------|
| `request for object` | Object doesn't exist | Use `foundObject()` first |
| `oldTime() not stored` | Missing time storage | Check `nOldTimes()` > 0 |
| No output files | Missing `write()` call | Add `runTime.write()` in loop |
| Directory not found | Time precision mismatch | Check `timePrecision` setting |
| Slow simulation | Excessive I/O | Increase `writeInterval` |
| Instability | Fixed deltaT too large | Enable `adjustTimeStep` |
| Memory growth | Registry leaks | Use `autoPtr` or check `foundObject()` |
| Wrong values | Wrong registry | Mesh vs Time registry confusion |

---

## Prevention Checklist

**Before Runtime:**
- [ ] Verify all fields exist in correct registry
- [ ] Check `timePrecision` matches time step size
- [ ] Confirm `writeControl` and `writeInterval` settings
- [ ] Set appropriate `purgeWrite` value (or 0 to keep all)

**During Development:**
- [ ] Always use `foundObject()` before `lookupObject()`
- [ ] Use `autoPtr` for manual registry storage
- [ ] Check `nOldTimes()` before accessing `oldTime()`
- [ ] Enable `adjustTimeStep` for robustness

**Performance Tuning:**
- [ ] Set `runTimeModifiable no` for production
- [ ] Increase `writeInterval` for long simulations
- [ ] Monitor memory usage for registry leaks
- [ ] Profile I/O time vs computation time

---

## Key Takeaways

1. **Defensive Lookup:** Always check object existence with `foundObject()` before `lookupObject()`
2. **Registry Awareness:** Fields live in `mesh` registry, not `runTime` registry
3. **Time Storage Management:** Verify `nOldTimes() > 0` before accessing `oldTime()`
4. **Write Control:** Understand `purgeWrite` behavior to avoid losing critical data
5. **Memory Safety:** Use `autoPtr` for manual registry storage to prevent leaks
6. **Performance:** Disable `runTimeModifiable` and reduce write frequency for production runs

---

## Exercises

**Exercise 1: Defensive Lookup**
```cpp
// TODO: Make this code crash-proof
const volScalarField& T = mesh.lookupObject<volScalarField>("T");
const volScalarField& p = mesh.lookupObject<volScalarField>("p");
```

**Exercise 2: Debug Time Storage**
```cpp
// TODO: Add safety checks before accessing old time
const volScalarField& T0 = T.oldTime();
const volScalarField& T00 = T.oldTime().oldTime();
```

**Exercise 3: Optimize Write Settings**
```cpp
// Current: Writes every time step, slow simulation
// TODO: Suggest better controlDict settings
writeControl    timeStep;
writeInterval   1;
```

**Exercise 4: Fix Memory Leak**
```cpp
// TODO: Fix potential registry leak
volScalarField* T = new volScalarField(...);
mesh.objectRegistry::store(T);
```

---

## Related Documentation

- **Overview:** [00_Overview.md](00_Overview.md)
- **Object Registry:** [03_Object_Registry.md](03_Object_Registry.md)
- **Functional Logic:** [04_Functional_Logic.md](04_Functional_Logic.md)
- **Design Patterns:** [05_Design_Patterns.md](05_Design_Patterns.md)