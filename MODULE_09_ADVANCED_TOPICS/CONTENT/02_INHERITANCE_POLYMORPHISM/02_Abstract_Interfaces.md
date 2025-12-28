# Abstract Interfaces

Abstract Interfaces ใน OpenFOAM

---

## Overview

> **Abstract Interface** = Pure virtual functions defining contract

---

## 1. What is Abstract Class?

```cpp
class turbulenceModel
{
public:
    // Pure virtual = abstract
    virtual tmp<volScalarField> k() const = 0;
    virtual tmp<volScalarField> epsilon() const = 0;
    virtual void correct() = 0;

    // Can have concrete methods too
    virtual tmp<volScalarField> nuEff() const;
};
```

---

## 2. Why Interfaces?

| Benefit | Description |
|---------|-------------|
| **Contract** | Forces derived to implement |
| **Flexibility** | User code works with any derived |
| **Extensibility** | Add new implementations easily |
| **Testing** | Mock implementations |

---

## 3. OpenFOAM Interfaces

### turbulenceModel

```cpp
// All turbulence models must provide:
virtual tmp<volScalarField> k() const = 0;
virtual tmp<volScalarField> epsilon() const = 0;
virtual tmp<volScalarField> nut() const = 0;
virtual tmp<volSymmTensorField> R() const = 0;
```

### fvPatchField

```cpp
// All BC types must provide:
virtual tmp<Field<Type>> valueInternalCoeffs() const = 0;
virtual tmp<Field<Type>> valueBoundaryCoeffs() const = 0;
```

---

## 4. Implementing Interface

```cpp
class kEpsilon : public RASModel
{
    volScalarField k_;
    volScalarField epsilon_;

public:
    // Implement required methods
    virtual tmp<volScalarField> k() const
    {
        return k_;
    }

    virtual tmp<volScalarField> epsilon() const
    {
        return epsilon_;
    }

    virtual void correct()
    {
        // Solve k and epsilon equations
    }
};
```

---

## 5. Using Polymorphically

```cpp
// Work with base class pointer
autoPtr<turbulenceModel> turb = turbulenceModel::New(dict);

// Call interface methods
tmp<volScalarField> k = turb->k();
turb->correct();
```

---

## Quick Reference

| Concept | Syntax |
|---------|--------|
| Pure virtual | `virtual T f() = 0;` |
| Override | `virtual T f() override;` |
| Virtual destructor | `virtual ~Base() = default;` |

---

## Concept Check

<details>
<summary><b>1. = 0 หมายความว่าอะไร?</b></summary>

**Pure virtual** — derived class ต้อง implement
</details>

<details>
<summary><b>2. ทำไมต้อง virtual destructor?</b></summary>

**Proper cleanup** เมื่อ delete ผ่าน base pointer
</details>

<details>
<summary><b>3. abstract class instantiate ได้ไหม?</b></summary>

**ไม่ได้** — ต้องใช้ derived class
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Hierarchies:** [03_Inheritance_Hierarchies.md](03_Inheritance_Hierarchies.md)