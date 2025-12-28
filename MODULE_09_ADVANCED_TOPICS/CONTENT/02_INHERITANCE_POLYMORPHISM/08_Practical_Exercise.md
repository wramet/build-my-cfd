# Practical Exercise - Inheritance

แบบฝึกหัด Inheritance และ Polymorphism

---

## Exercise 1: Simple Inheritance

### Task

สร้าง class hierarchy สำหรับ source term

```cpp
// Base class
class sourceModel
{
public:
    virtual ~sourceModel() = default;
    virtual tmp<volScalarField> Su() const = 0;
    virtual tmp<volScalarField> Sp() const = 0;
};

// Constant source
class constantSource : public sourceModel
{
    dimensionedScalar value_;
public:
    constantSource(const dimensionedScalar& val) : value_(val) {}

    virtual tmp<volScalarField> Su() const
    {
        return tmp<volScalarField>(new volScalarField(..., value_));
    }
};
```

---

## Exercise 2: Run-Time Selection

### Task

เพิ่ม RTS ให้ sourceModel

```cpp
class sourceModel
{
public:
    TypeName("sourceModel");

    declareRunTimeSelectionTable
    (
        autoPtr, sourceModel, dictionary,
        (const dictionary& dict, const fvMesh& mesh),
        (dict, mesh)
    );

    static autoPtr<sourceModel> New(const dictionary& dict, const fvMesh& mesh);
};

// In .C file
defineTypeNameAndDebug(sourceModel, 0);
defineRunTimeSelectionTable(sourceModel, dictionary);

addToRunTimeSelectionTable(sourceModel, constantSource, dictionary);
```

---

## Exercise 3: Using Polymorphism

```cpp
// Create from dictionary
autoPtr<sourceModel> source = sourceModel::New(dict, mesh);

// Use polymorphically
fvScalarMatrix TEqn
(
    fvm::ddt(T)
  + fvm::div(phi, T)
  ==
    fvm::laplacian(alpha, T)
  + source->Su()
  + fvm::Sp(source->Sp()/T, T)
);
```

---

## Exercise 4: Dictionary Setup

```cpp
// constant/transportProperties
source
{
    type        constantSource;
    value       100;
}
```

---

## Quick Reference

| Task | Code |
|------|------|
| Declare virtual | `virtual Type func() = 0;` |
| Register type | `TypeName("name");` |
| Add to RTS | `addToRunTimeSelectionTable(...)` |
| Factory create | `Model::New(dict)` |

---

## 🧠 Concept Check

<details>
<summary><b>1. Pure virtual vs virtual?</b></summary>

- **Pure**: Must override (`= 0`)
- **Virtual**: Can override
</details>

<details>
<summary><b>2. autoPtr ใช้ทำไม?</b></summary>

**Ownership** — ensures proper deletion
</details>

<details>
<summary><b>3. dictionary type field ทำอะไร?</b></summary>

**Select concrete class** at runtime
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **RTS:** [04_Run_Time_Selection_System.md](04_Run_Time_Selection_System.md)
