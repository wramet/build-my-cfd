# FunctionObject Integration

การรวม FunctionObject เข้ากับ Solver

---

## Overview

> **Function Objects** = Post-processing hooks in solver loop

---

## 1. Basic Structure

```cpp
class myFunctionObject : public functionObject
{
public:
    TypeName("myFunctionObject");

    myFunctionObject(const word& name, const dictionary& dict);

    virtual bool execute() override;  // Called each step
    virtual bool write() override;    // Write output
    virtual bool read(const dictionary& dict) override;
};
```

---

## 2. Registration

```cpp
// In source file
defineTypeNameAndDebug(myFunctionObject, 0);

addToRunTimeSelectionTable
(
    functionObject,
    myFunctionObject,
    dictionary
);
```

---

## 3. controlDict Usage

```cpp
functions
{
    myFunc
    {
        type            myFunctionObject;
        libs            ("libmyFunctions.so");
        executeControl  timeStep;
        writeControl    writeTime;
    }
}
```

---

## 4. Accessing Fields

```cpp
bool myFunctionObject::execute()
{
    const volVectorField& U = mesh_.lookupObject<volVectorField>("U");
    scalar maxU = max(mag(U)).value();
    Info << "Max velocity: " << maxU << endl;
    return true;
}
```

---

## 5. Built-in Function Objects

| Type | Purpose |
|------|---------|
| `fieldAverage` | Time averaging |
| `probes` | Point sampling |
| `forces` | Force calculation |
| `yPlus` | y+ calculation |

---

## Quick Reference

| Method | When Called |
|--------|-------------|
| `execute()` | Each time step |
| `write()` | At write time |
| `read()` | On construction |

---

## 🧠 Concept Check

<details>
<summary><b>1. execute() vs write()?</b></summary>

- **execute()**: Every time step
- **write()**: At scheduled write times
</details>

<details>
<summary><b>2. ทำไมต้อง libs?</b></summary>

**Load library** ที่มี function object registered
</details>

<details>
<summary><b>3. Access mesh อย่างไร?</b></summary>

ผ่าน **mesh_ member** หรือ `obr()` (object registry)
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Patterns:** [05_Design_Patterns.md](05_Design_Patterns.md)