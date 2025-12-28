# Architecture - Practical Exercise

แบบฝึกหัด Architecture

---

## Exercise 1: Create RTS Model

### Task

สร้าง model ที่ใช้ Run-Time Selection

```cpp
// myModel.H
class myModel : public baseModel
{
public:
    TypeName("myModel");

    myModel(const dictionary& dict);

    virtual void compute() override;
};

// myModel.C
defineTypeNameAndDebug(myModel, 0);

addToRunTimeSelectionTable
(
    baseModel,
    myModel,
    dictionary
);

myModel::myModel(const dictionary& dict)
: baseModel(dict)
{}
```

---

## Exercise 2: Create Function Object

```cpp
class myFunctionObject : public functionObject
{
public:
    TypeName("myFunctionObject");

    myFunctionObject(const word& name, const dictionary& dict);

    virtual bool execute() override;
    virtual bool write() override;
};

// Register
addToRunTimeSelectionTable(functionObject, myFunctionObject, dictionary);
```

---

## Exercise 3: Load Dynamic Library

```cpp
// system/controlDict
libs ("libmyModels.so");

// Or in code
dlLibraryTable::open("libmyModels.so");
```

---

## Exercise 4: Use in Solver

```cpp
// Create model from dict
autoPtr<baseModel> model = baseModel::New(dict);

// Use
model->compute();
```

---

## Quick Reference

| Step | Code |
|------|------|
| Declare type | `TypeName("name")` |
| Register | `addToRunTimeSelectionTable` |
| Create | `Model::New(dict)` |
| Load lib | `libs (...)` |

---

## Concept Check

<details>
<summary><b>1. RTS ต้องทำอะไรบ้าง?</b></summary>

1. `TypeName`
2. `addToRunTimeSelectionTable`
3. Implement constructor
</details>

<details>
<summary><b>2. Function object ต้อง implement อะไร?</b></summary>

`execute()` และ `write()` methods
</details>

<details>
<summary><b>3. Load library อย่างไร?</b></summary>

`libs (...)` in controlDict หรือ `dlLibraryTable::open()`
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **RTS:** [02_Runtime_Selection_Tables.md](02_Runtime_Selection_Tables.md)