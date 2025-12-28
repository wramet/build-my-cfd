# Field Lifecycle

วงจรชีวิตของ Field — Creation → Usage → Destruction

> **ทำไมบทนี้สำคัญ?**
> - รู้วิธี **สร้าง field** จาก file/code
> - เข้าใจ **old time management** สำหรับ time derivatives
> - รู้วิธี **write field** ให้ถูก

---

## Overview

> **💡 Field Lifecycle = Create → Initialize → Use → (Store Old) → Write → Destroy**
>
> ทุกขั้นตอนมี methods เฉพาะ

---

## 1. Creation Methods

### From File

```cpp
volScalarField p
(
    IOobject
    (
        "p",                    // Name
        runTime.timeName(),     // Time directory
        mesh,                   // Registry
        IOobject::MUST_READ,    // Must exist
        IOobject::AUTO_WRITE    // Write at output times
    ),
    mesh
);
```

### With Initial Value

```cpp
volScalarField T
(
    IOobject("T", runTime.timeName(), mesh, IOobject::NO_READ),
    mesh,
    dimensionedScalar("T", dimTemperature, 300)
);
```

### From Expression

```cpp
volScalarField rhoU2 = rho * magSqr(U);
```

---

## 2. IOobject Options

### Read Options

| Option | Meaning |
|--------|---------|
| `MUST_READ` | File must exist |
| `READ_IF_PRESENT` | Read if exists |
| `NO_READ` | Don't read |

### Write Options

| Option | Meaning |
|--------|---------|
| `AUTO_WRITE` | Write at output times |
| `NO_WRITE` | Never write |

---

## 3. Field Registration

```cpp
// Field automatically registered with mesh (objectRegistry)
volScalarField T(..., mesh, ...);

// Lookup registered field
const volScalarField& T = mesh.lookupObject<volScalarField>("T");

// Check existence
if (mesh.foundObject<volScalarField>("T")) { ... }
```

---

## 4. Old Time Management

```cpp
// Access previous time step
const volScalarField& T0 = T.oldTime();

// Old-old time
const volScalarField& T00 = T.oldTime().oldTime();

// Store for time derivative
T.storeOldTime();
```

---

## 5. Previous Iteration

```cpp
// Store for SIMPLE/PIMPLE iterations
T.storePrevIter();

// Access
const volScalarField& Tprev = T.prevIter();

// Relaxation
T.relax();  // Uses prevIter
```

---

## 6. Boundary Conditions

```cpp
// Correct boundary after solve
T.correctBoundaryConditions();

// Access boundary
const fvPatchScalarField& Tpatch = T.boundaryField()[patchI];

// Modify boundary
T.boundaryFieldRef()[patchI] == fixedValue;
```

---

## 7. Writing

```cpp
// Write at scheduled times
runTime.write();

// Force write
T.write();

// Write specific time
T.writeObject(IOstreamOption(), true);
```

---

## Quick Reference

| Stage | Method |
|-------|--------|
| Create | Constructor with IOobject |
| Read | `MUST_READ` in IOobject |
| Initialize | dimensionedScalar in constructor |
| Store old time | `.storeOldTime()` |
| Correct BC | `.correctBoundaryConditions()` |
| Write | `.write()` or `AUTO_WRITE` |

---

## 🧠 Concept Check

<details>
<summary><b>1. MUST_READ vs READ_IF_PRESENT?</b></summary>

- **MUST_READ**: Error if file missing
- **READ_IF_PRESENT**: Use initial value if missing
</details>

<details>
<summary><b>2. oldTime() ใช้เมื่อไหร่?</b></summary>

เมื่อต้องการ **previous time step** สำหรับ `fvm::ddt`
</details>

<details>
<summary><b>3. correctBoundaryConditions() ทำอะไร?</b></summary>

**Update boundary values** ตาม BC type หลังจาก solve
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Pitfalls:** [06_Common_Pitfalls.md](06_Common_Pitfalls.md)