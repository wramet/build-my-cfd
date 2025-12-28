# Time & Databases - Introduction

บทนำ Time และ Object Registry

---

## Overview

> **Time** = Heart of OpenFOAM simulation control

---

## 1. Time Class Responsibilities

| Role | Description |
|------|-------------|
| Loop control | Start, end, deltaT |
| I/O scheduling | When to write |
| Object registry | Field storage |
| Directory management | Time folders |

---

## 2. Basic Time Loop

```cpp
#include "createTime.H"
#include "createMesh.H"

while (runTime.loop())
{
    Info << "Time = " << runTime.timeName() << endl;

    // Solve equations
    ...

    runTime.write();
}

Info << "End" << endl;
```

---

## 3. controlDict Settings

```cpp
// system/controlDict
application     simpleFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         1000;
deltaT          1;

writeControl    timeStep;
writeInterval   100;

purgeWrite      0;
writeFormat     ascii;
writePrecision  6;
```

---

## 4. Key Methods

### Time Control

```cpp
scalar t = runTime.value();
scalar dt = runTime.deltaT().value();
word tName = runTime.timeName();
bool continue = runTime.loop();
```

### I/O Control

```cpp
runTime.write();           // Write if scheduled
runTime.writeNow();        // Force write
runTime.writeAndEnd();     // Write and stop
```

---

## 5. Object Registry

```cpp
// Fields register with mesh
volScalarField T(..., mesh, ...);

// Lookup later
const volScalarField& T = mesh.lookupObject<volScalarField>("T");
```

---

## Quick Reference

| Need | Use |
|------|-----|
| Current time | `runTime.value()` |
| Time step | `runTime.deltaT()` |
| Time name | `runTime.timeName()` |
| Continue loop | `runTime.loop()` |
| Write output | `runTime.write()` |

---

## 🧠 Concept Check

<details>
<summary><b>1. loop() ทำอะไร?</b></summary>

**Increment time** และ return true ถ้ายังไม่ถึง endTime
</details>

<details>
<summary><b>2. timeName() vs value()?</b></summary>

- **timeName()**: String (for directories)
- **value()**: Scalar (for calculations)
</details>

<details>
<summary><b>3. writeControl ทำอะไร?</b></summary>

**กำหนดเมื่อไหร่จะ write** output files
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Time Architecture:** [02_Time_Architecture.md](02_Time_Architecture.md)