# Inheritance and Virtual Functions

Inheritance และ Virtual Functions ใน Project

---

## Overview

> Leverage OpenFOAM's **class hierarchy** for model development

---

## 1. Base Class Selection

| Need | Base Class |
|------|------------|
| Turbulence | `turbulenceModel` |
| Transport | `basicThermo` |
| BC | `fvPatchField` |
| Function object | `functionObject` |

---

## 2. Implementation Pattern

```cpp
class myModel : public turbulenceModel
{
    // Private data
    volScalarField k_;

public:
    // RTS
    TypeName("myModel");

    // Constructor
    myModel(const volVectorField& U, const surfaceScalarField& phi);

    // Virtual functions
    virtual tmp<volScalarField> k() const override;
    virtual void correct() override;
};
```

---

## 3. Override Virtual Functions

```cpp
tmp<volScalarField> myModel::k() const
{
    return k_;
}

void myModel::correct()
{
    // Solve equations
    solve(kEqn == Pk - epsilon);
}
```

---

## 4. Call Base Class

```cpp
void myModel::correct()
{
    // Call base implementation first
    turbulenceModel::correct();

    // Then do model-specific work
    solveEquations();
}
```

---

## 5. Virtual Destructor

```cpp
class myModel
{
public:
    virtual ~myModel() = default;  // Essential!
};
```

---

## Quick Reference

| Keyword | Use |
|---------|-----|
| `virtual` | Allow override |
| `override` | Verify override |
| `= 0` | Pure virtual |
| `= default` | Default implementation |

---

## Concept Check

<details>
<summary><b>1. override keyword ทำอะไร?</b></summary>

**Compiler check** ว่า actually overrides base method
</details>

<details>
<summary><b>2. ทำไมต้อง virtual destructor?</b></summary>

**Proper cleanup** เมื่อ delete via base pointer
</details>

<details>
<summary><b>3. Pure virtual คืออะไร?</b></summary>

`= 0` — derived class **ต้อง** implement
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Design Patterns:** [06_Design_Pattern_Rationale.md](06_Design_Pattern_Rationale.md)