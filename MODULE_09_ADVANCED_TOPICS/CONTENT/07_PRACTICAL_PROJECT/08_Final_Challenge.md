# Final Challenge

โจทย์ท้าทายสุดท้าย

---

## Challenge: Create Complete Model

### Goal

สร้าง turbulence model ที่ทำงานได้จริง

---

## Step 1: File Structure

```
myTurbulenceModel/
├── Make/
│   ├── files
│   └── options
├── myTurbulenceModel.H
├── myTurbulenceModel.C
└── myTurbulenceModelI.H
```

---

## Step 2: Header (.H)

```cpp
class myTurbulenceModel : public eddyViscosity<RASModel>
{
    volScalarField k_;
    dimensionedScalar Cmu_;

public:
    TypeName("myTurbulenceModel");

    myTurbulenceModel(...);

    virtual tmp<volScalarField> k() const;
    virtual void correct();
};
```

---

## Step 3: Source (.C)

```cpp
defineTypeNameAndDebug(myTurbulenceModel, 0);

addToRunTimeSelectionTable
(
    RASModel, myTurbulenceModel, dictionary
);

void myTurbulenceModel::correct()
{
    // Implementation
}
```

---

## Step 4: Test

```cpp
// constant/turbulenceProperties
simulationType RAS;
RAS
{
    model myTurbulenceModel;
    turbulence on;
}
```

---

## Checklist

- [ ] Header with declaration
- [ ] Source with implementation
- [ ] RTS registration
- [ ] Make system
- [ ] Test case
- [ ] Documentation

---

## 🧠 Concept Check

<details>
<summary><b>1. Minimum requirements คืออะไร?</b></summary>

**Header + Source + Make + RTS registration**
</details>

<details>
<summary><b>2. ทดสอบอย่างไร?</b></summary>

**Run solver** กับ dictionary ที่เลือก model
</details>

<details>
<summary><b>3. Debug อย่างไร?</b></summary>

**Debug build** + gdb หรือ Info statements
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Errors:** [07_Common_Errors_and_Debugging.md](07_Common_Errors_and_Debugging.md)