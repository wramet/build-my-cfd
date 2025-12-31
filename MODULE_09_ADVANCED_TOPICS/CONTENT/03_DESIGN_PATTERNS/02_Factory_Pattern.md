# Factory Pattern

ในบทนี้เราจะเรียนรู้เกี่ยวกับ Factory Pattern ซึ่งเป็นหนึ่งใน Design Pattern ที่สำคัญที่สุดใน OpenFOAM ใช้สำหรับสร้าง Object แบบ Dynamic ผ่าน Dictionary-driven Configuration

---

## Learning Objectives

หลังจากอ่านบทนี้ คุณจะสามารถ:
- เข้าใจหลักการของ Factory Pattern และปัญหาที่แก้ไข
- อธิบายการทำงานของ Run-Time Selection (RTS) System ใน OpenFOAM
- เขียน Code สร้าง Base Class ด้วย `declareRunTimeSelectionTable`
- ลงทะเบียน Derived Class ด้วย `addToRunTimeSelectionTable`
- ใช้งาน Factory Method ผ่าน `ClassName::New()`
- เปรียบเทียบความแตกต่างระหว่าง Hard-coded creation กับ Factory Pattern

---

## Prerequisites

ความรู้พื้นฐานที่ต้องมี:
- Basic C++ Syntax (classes, inheritance, virtual functions)
- พื้นฐานเกี่ยวกับ Polymorphism และ Abstract Base Classes
- ความเข้าใจ OpenFOAM Dictionary Format (`constant/` properties files)

---

## Overview

### What (คืออะไร?)

Factory Pattern เป็น **Creational Design Pattern** ที่ทำให้เราสามารถสร้าง Object ได้โดยไม่ต้องระบุ Concrete Class ที่แน่นอน แต่ใช้ **Identifier** เช่น ชื่อจาก Dictionary ในการระบุ Type ของ Object ที่ต้องการสร้าง

ใน OpenFOAM Factory Pattern ถูก Implement ผ่าน **Run-Time Selection (RTS) System** ซึ่งเป็นกลไกพื้นฐานที่ใช้ในการสร้าง:
- Turbulence Models (`kEpsilon`, `kOmegaSST`, `SpalartAllmaras`, etc.)
- Discretization Schemes (`Gauss`, `upwind`, `linear`, etc.)
- Boundary Conditions (`fixedValue`, `zeroGradient`, etc.)
- Function Objects
- และอื่นๆ อีกมากมาย

### Why (ทำไมต้องใช้?)

ปัญหาที่ Factory Pattern แก้ไข:

**1. Hard-coded Dependency Problem**
```cpp
// ❌ WITHOUT FACTORY: Code ที่ยากต่อการบำรุงรักษา
turbulenceModel* turb;
if (type == "kEpsilon")
    turb = new kEpsilon(mesh);
else if (type == "kOmegaSST")
    turb = new kOmegaSST(mesh);
else if (type == "SpalartAllmaras")
    turb = new SpalartAllmaras(mesh);
// ... 50+ models อีกเต็มไปหมด

// ทุกครั้งที่เพิ่ม Model ใหม่:
// ❌ ต้องแก้ User Code
// ❌ ต้อง Recompile Solver
// ❌ มีโอกาสเกิด Bug จากการแก้ if-else chain
```

**2. Open-Closed Principle Violation**
- โค้ดด้านบนละเมิดหลักการ "Open for Extension, Closed for Modification"
- การเพิ่ม Model ใหม่ต้องแก้ไขโค้ดเดิม (risky)

**3. Configuration Driven vs Code Driven**
- OpenFOAM เป็น Simulation Framework ที่ User ต้องการเปลี่ยน Model/Method ผ่าน Dictionary ง่ายๆ
- ไม่ต้อง Recompile Solver ทุกครั้งที่เปลี่ยน Model

### How (ใช้งานใน OpenFOAM อย่างไร?)

OpenFOAM ใช้ **Run-Time Selection Table** เพื่อเก็บ Mapping ระหว่าง:
- **Key** = ชื่อ Class (เช่น `"kEpsilon"`, `"kOmegaSST"`)
- **Value** = Pointer ไปยัง Constructor Function

ผ่าน 3 ขั้นตอนหลัก:
1. **Declaration** - Base Class ประกาศ RTSTable ด้วย `declareRunTimeSelectionTable`
2. **Registration** - Derived Class ลงทะเบียนตัวเองด้วย `addToRunTimeSelectionTable`
3. **Factory Method** - User เรียก `ClassName::New(dictionary)` เพื่อสร้าง Object

---

## Factory Pattern ใน OpenFOAM

### Visual Comparison

![IMG_09_004: Factory Pattern Comparison - Hard-coded vs Factory](IMG_09_004.jpg)

**ภาพประกอบ:**
- **Panel A (The Mess):** แสดงโค้ดแบบ Hard-coded if-else chain ที่ยาวและซับซ้อน
- **Panel B (Factory Pattern):** แสดง RTSTable ที่ทำหน้าที่เป็น Factory Hub ให้แต่ละ Model ลงทะเบียนตัวเองได้อย่างอิสระ โดยไม่กระทบกัน

---

## Implementation Walkthrough

### ขั้นตอนที่ 1: Base Class Declaration

Base Class (Abstract Class) จะเป็นเจ้าของ Factory Method และ RTSTable:

```cpp
// turbulenceModel.H
#ifndef turbulenceModel_H
#define turbulenceModel_H

#include "autoPtr.H"
#include "dictionary.H"
#include "runTimeSelectionTables.H"

namespace Foam
{

class turbulenceModel
{
protected:
    // Data members
    const volVectorField& U_;
    const surfaceScalarField& phi_;
    
public:
    // 1. DECLARE RUNTIME SELECTION TABLE
    // Macro นี้สร้าง:
    // - Static hash table สำหรับเก็บ Constructor pointers
    // - Typedefs สำหรับ Constructor signature
    declareRunTimeSelectionTable
    (
        autoPtr,              // Return type: smart pointer
        turbulenceModel,      // Base class name
        dictionary,           // Lookup key type
        (const dictionary& dict), // Constructor parameters
        (dict)                // Arguments to pass
    );

    // 2. VIRTUAL DESTRUCTOR (Important!)
    virtual ~turbulenceModel() {}
    
    // 3. PURE VIRTUAL METHODS (Interface)
    virtual void correct() = 0;
    virtual tmp<volSymmTensorField> R() const = 0;
    
    // 4. FACTORY METHOD (Static)
    // User เรียก method นี้เพื่อสร้าง Object
    static autoPtr<turbulenceModel> New
    (
        const dictionary& dict
    );
};

} // End namespace Foam

#endif
```

**คำอธิบาย `declareRunTimeSelectionTable`:**
- **autoPtr**: Smart pointer ที่จัดการ Memory Ownership (C++98 สมัย OpenFOAM พัฒนา)
- **dictionary**: Type ของ Key ที่ใช้ Lookup ใน RTSTable (สามารถเป็น `word`, `wordRe` ก็ได้)
- **(const dictionary& dict)**: Constructor parameter signature
- **(dict)**: Argument ที่จะ Pass ให้ Constructor

---

### ขั้นตอนที่ 2: Factory Method Implementation

Implement `New()` method ใน `.C` file:

```cpp
// turbulenceModel.C
#include "turbulenceModel.H"

// 2. FACTORY METHOD IMPLEMENTATION
Foam::autoPtr<Foam::turbulenceModel> 
Foam::turbulenceModel::New(const dictionary& dict)
{
    // 2.1 READ TYPE FROM DICTIONARY
    word modelName(dict.lookup("type"));
    
    Info<< "Selecting turbulence model: " << modelName << endl;
    
    // 2.2 LOOKUP IN RTSTABLE
    // dictionaryConstructorTable ถูกสร้างโดย Macro
    auto cstrIter = dictionaryConstructorTablePtr_->find(modelName);
    
    // 2.3 ERROR HANDLING
    if (cstrIter == dictionaryConstructorTablePtr_->end())
    {
        FatalErrorInFunction
            << "Unknown turbulence model " << modelName
            << nl << "Valid models:" << nl
            << dictionaryConstructorTablePtr_->sortedToc()
            << exit(FatalError);
    }
    
    // 2.4 CALL CONSTRUCTOR AND RETURN
    // cstrIter() returns autoPtr<turbulenceModel>
    return cstrIter()(dict);
}
```

**Flow ของ Factory Method:**
1. อ่าน `"type"` จาก Dictionary (เช่น `kOmegaSST`)
2. ค้นหาใน RTSTable ว่ามี Class ชื่อนี้ลงทะเบียนไว้ไหม
3. ถ้าเจอ → เรียก Constructor และ Return `autoPtr`
4. ถ้าไม่เจอ → Throw FatalError พร้อมรายชื่อ Model ที่มีทั้งหมด

---

### ขั้นตอนที่ 3: Derived Class Registration

แต่ละ Derived Class ลงทะเบียนตัวเองกับ RTSTable:

```cpp
// kEpsilon.H
class kEpsilon
:
    public turbulenceModel
{
public:
    // 3.1 CONSTRUCTOR WITH MATCHING SIGNATURE
    kEpsilon(const dictionary& dict);
    
    // ... other methods
};
```

```cpp
// kEpsilon.C
#include "kEpsilon.H"

// 3.2 REGISTRATION MACRO
addToRunTimeSelectionTable
(
    turbulenceModel,  // Base class
    kEpsilon,         // Derived class
    dictionary        // Table type (must match declare)
);

// 3.3 CONSTRUCTOR IMPLEMENTATION
Foam::kEpsilon::kEpsilon(const dictionary& dict)
:
    turbulenceModel(dict)
{
    Info<< "Creating kEpsilon model" << endl;
}
```

**สิ่งที่ Macro ทำ:**
- สร้าง Static Constructor Pointer ชี้ไปที่ `kEpsilon::kEpsilon(const dictionary&)`
- เพิ่ม Pointer นี้เข้าไปใน RTSTable ของ Base Class
- Key = `"kEpsilon"` (ชื่อ Class)
- Value = Pointer to Constructor

---

### ขั้นตอนที่ 4: User Usage

User ใช้งานผ่าน Dictionary และ `New()` method:

```cpp
// constant/turbulenceProperties
simulationType  RASModel;

RASModel kEpsilon;    // User เปลี่ยนตรงนี้ได้อิสระ

kEpsilonCoeffs
{
    Cmu         0.09;
    C1          1.44;
    C2          1.92;
    sigmaEps    1.3;
}
```

```cpp
// createFields.H ใน Solver
autoPtr<turbulenceModel> turb
(
    turbulenceModel::New(turbulenceDict)
);

// ใน Time Loop
while (runTime.loop())
{
    turb->correct();  // Polymorphic call
    // ... solve equations
}
```

**ประโยชน์:**
- User เปลี่ยน `kEpsilon` → `kOmegaSST` ใน Dictionary
- **ไม่ต้อง Recompile Solver**
- RTSTable จะสร้าง Object ให้ถูกต้องอัตโนมัติ

---

## Real-World OpenFOAM Examples

### Example 1: Discretization Schemes

```cpp
// fvSchemes
gradSchemes
{
    default Gauss linear;
}

divSchemes
{
    div(phi,U) Gauss upwind;
}
```

**Behind the scenes:**
```cpp
// fvSchemes.C
autoPtr<gradScheme> GaussGradScheme::New(const fvMesh& mesh)
{
    // Returns "Gauss <scheme>" where <scheme> is linear/upwind/etc
}

// Linear Scheme ลงทะเบียน:
addToRunTimeSelectionTable(gradScheme, GaussGradScheme, mesh);
```

### Example 2: Boundary Conditions

```cpp
// 0/U
boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform (10 0 0);
    }
    
    outlet
    {
        type            zeroGradient;
    }
}
```

**Factory Creates:**
```cpp
// fvPatchField.C
autoPtr<fvPatchField<vector>> fvPatchField<vector>::New
(
    const fvPatch& p,
    const dictionary& dict
)
{
    word typeName = dict.lookup("type");
    // Returns fixedValueFvPatchField, zeroGradientFvPatchField, etc
}
```

### Example 3: Function Objects

```cpp
// system/controlDict
functions
{
    probes
    {
        type            probes;
        functionObjectLibs ("libsampling.so");
        // ...
    }
}
```

**Factory Mechanism:**
```cpp
// functionObjectList.C
autoPtr<functionObject> functionObject::New
(
    const word& type,
    const dictionary& dict
)
{
    // Returns appropriate function object (probes, sets, etc)
}
```

---

## Benefits of Factory Pattern

| ประโยชน์ | คำอธิบาย | OpenFOAM Context |
|-----------|-----------|------------------|
| **Decoupling** | User Code ไม่ต้องรู้จัก Concrete Class | Solver ไม่ต้อง include `kEpsilon.H` โดยตรง |
| **Extensibility** | เพิ่ม Model ใหม่ได้โดยไม่แก้ User Code | Plugin Model ใหม่ → Compile เฉพาะ Library |
| **Configuration** | Dictionary-driven สะดวกต่อ User | เปลี่ยน Model ผ่าน Text File |
| **Maintenance** | Central Creation Point | แก้ `New()` method ที่เดียว |
| **Open-Closed** | เปิดรับ Extension ปิดการแก้ไข | เพิ่ม Model ใหม่ = New Class + Register |
| **Type Safety** | Compiler Check ผ่าน RTSTable | ไม่มี Cast แบบ `void*` ที่อันตราย |

---

## Comparison: Before vs After Factory

### ❌ Before Factory (Hard-coded)

```cpp
// User must modify solver for new models
turbulenceModel* model;

if (dict.lookup("type") == word("kEpsilon"))
    model = new kEpsilon(mesh);
else if (dict.lookup("type") == word("kOmegaSST"))
    model = new kOmegaSST(mesh);
else if (dict.lookup("type") == word("SpalartAllmaras"))
    model = new SpalartAllmaras(mesh);
// ... repeat for 50+ models

model->correct();
```

**Problems:**
- ❌ ต้อง include ทุก Derived Class header
- ❌ ต้อง Recompile Solver เมื่อเพิ่ม Model
- ❌ Maintenance nightmare
- ❌ Error-prone

### ✅ After Factory (RTS System)

```cpp
// Clean, maintainable, extensible
autoPtr<turbulenceModel> model = turbulenceModel::New(dict);
model->correct();
```

**Benefits:**
- ✅ Solver ไม่รู้จัก Concrete Classes
- ✅ เพิ่ม Model ใหม่ → Compile Library เท่านั้น
- ✅ Easy to maintain
- ✅ Type-safe

---

## Under the Hood: How RTS Works

### What the Macros Actually Do

`declareRunTimeSelectionTable` expands to:

```cpp
// Simplified version (actual macro is more complex)
class turbulenceModel
{
    // Typedef for constructor pointer
    typedef autoPtr<turbulenceModel> (*dictionaryConstructorPtr)(const dictionary&);
    
    // Hash table type
    typedef HashTable<dictionaryConstructorPtr, word> dictionaryConstructorTable;
    
    // Static table (one per base class)
    static dictionaryConstructorTable* dictionaryConstructorTablePtr_;
    
    // Accessor
    static dictionaryConstructorTable& dictionaryConstructorTable();
};
```

`addToRunTimeSelectionTable` expands to:

```cpp
// Simplified version
namespace Foam
{
    // Define static constructor for kEpsilon
    autoPtr<turbulenceModel> kEpsilon_New(const dictionary& dict)
    {
        return autoPtr<turbulenceModel>(new kEpsilon(dict));
    }
    
    // Static registration at program startup
    static ::Foam::dictionaryConstructorTableEntry 
    addkEpsilonDictionaryConstructorToTurbulenceModelTable
    (
        "kEpsilon", 
        kEpsilon_New
    );
}
```

**Static Initialization Magic:**
- Global Static Object ถูกสร้าง **ก่อน `main()`**
- Constructor ของ Object นี้ลงทะเบียน Pointer กับ RTSTable
- เมื่อโปรแกรมเริ่มทำงาน RTSTable พร้อมใช้งาน

---

## Common Errors and Debugging

### Error 1: "Unknown type"

```
--> FOAM FATAL ERROR:
Unknown turbulence model Laminar
Valid models:
2(kEpsilon kOmegaSST)
```

**Cause:**
- Typo in Dictionary (เช่น `laminar` vs `Laminar`)
- Library ไม่ถูก Link

**Solution:**
```cpp
// Check spelling in dictionary
turbulenceModel Laminar;  // Capital L

// Or add library link in controlDict
libs ("libmyTurbulenceModels.so");
```

### Error 2: Linker Error (Undefined Symbol)

```
undefined reference to `Foam::turbulenceModel::New(Foam::dictionary const&)'
```

**Cause:**
- ลืม Compile Base Class `.C` file

**Solution:**
```bash
# Make/files
turbulenceModel.C  // Add this!

kEpsilon.C
kOmegaSST.C
```

### Error 3: Registration Not Working

**Symptom:**
- Model ไม่อยู่ใน Valid Models list

**Cause:**
- Macro mismatch ระหว่าง `declare` และ `addToRunTime`

**Solution:**
```cpp
// Base class
declareRunTimeSelectionTable
(
    autoPtr,              // Must match
    turbulenceModel,
    dictionary,           // Must match
    (const dictionary&),  // Must match
    (dict)
);

// Derived class
addToRunTimeSelectionTable
(
    turbulenceModel,  // Must match
    kEpsilon,
    dictionary        // Must match
);
```

---

## Quick Reference

### Essential Macros

| Macro | Purpose | Location |
|-------|---------|----------|
| `declareRunTimeSelectionTable` | ประกาศ RTSTable ใน Base Class | `.H` file |
| `addToRunTimeSelectionTable` | ลงทะเบียน Derived Class | `.C` file |
| `defineTemplateRunTimeSelectionTable` | Template version | `.H` file |

### Common Factory Methods

| Class | Factory Method | Example Types |
|-------|---------------|---------------|
| `turbulenceModel` | `New(dictionary)` | `kEpsilon`, `kOmegaSST` |
| `fvPatchField` | `New(patch, dict)` | `fixedValue`, `zeroGradient` |
| `gradScheme` | `New(mesh)` | `Gauss linear`, `leastSquares` |
| `functionObject` | `New(type, dict)` | `probes`, `sets` |

### RTSTable Types

| Table Type | Lookup Key | Example |
|------------|------------|---------|
| `dictionary` | `word` from dict | `turbulenceModel` |
| `mesh` | `word` from mesh | `fvSchemes` |
| `word` | Direct `word` | Some utility classes |

---

## Key Takeaways

✅ **Factory Pattern** ใน OpenFOAM ถูก Implement ผ่าน **Run-Time Selection System**

✅ **3 Components:**
1. `declareRunTimeSelectionTable` - Base Class ประกาศ Table
2. `addToRunTimeSelectionTable` - Derived Class ลงทะเบียน
3. `ClassName::New()` - Factory Method ที่ User เรียกใช้

✅ **Benefits:** Decoupling, Extensibility, Configuration-driven, Open-Closed Principle

✅ **Real-world Usage:** ใช้ทั่วทั้ง OpenFOAM (Turbulence, Schemes, BCs, Function Objects)

✅ **Memory Management:** `autoPtr` จัดการ Ownership Transfer จาก Factory ไปยัง Caller

✅ **Static Registration:** Macro สร้าง Global Object ที่ลงทะเบียนตัวเองก่อน `main()`

---

## 🧠 Concept Check

<details>
<summary><b>1. Factory Pattern ดีกว่า if-else chain อย่างไร?</b></summary>

**คำตอบ:**
- ✅ **Open-Closed Principle** - เพิ่ม Model ใหม่โดยไม่ต้องแก้ User Code
- ✅ **Decoupling** - Solver ไม่ต้องรู้จัก Concrete Classes
- ✅ **Maintainability** - ลด Code duplication และ Complexity
- ✅ **No Recompilation** - เปลี่ยน Model ผ่าน Dictionary ได้เลย
</details>

<details>
<summary><b>2. ทำไม return type เป็น autoPtr แทน raw pointer?</b></summary>

**คำตอบ:**
- ✅ **Ownership Transfer** - Factory สร้าง Object แล้วโอนความรับผิดชอบให้ Caller
- ✅ **Automatic Cleanup** - `autoPtr` ลบ Object เมื่อออกจาก Scope
- ✅ **Exception Safe** - ป้องกัน Memory Leak ถ้าเกิด Exception
- ✅ **Explicit Ownership** - Code Reader รู้ทันทีว่าใครเป็นเจ้าของ Memory
</details>

<details>
<summary><b>3. Registration เกิดขึ้นเมื่อไหร่?</b></summary>

**คำตอบ:**
- ✅ **Static Initialization** - ก่อน `main()` เริ่มทำงาน (program startup)
- ✅ **Global Object** - Macro สร้าง Static Object ที่ลงทะเบียนตัวเอง
- ✅ **Link Time** - Library ที่ถูก Link มาด้วยจะลงทะเบียน Models ทั้งหมด
</details>

<details>
<summary><b>4. ถ้า Dictionary ระบุ Type ที่ไม่มีใน RTSTable จะเกิดอะไรขึ้น?</b></summary>

**คำตอบ:**
- ✅ `New()` method จะค้นหาใน RTSTable และ **ไม่เจอ**
- ✅ Throw `FatalError` พร้อมรายชื่อ Models ที่มีทั้งหมด
- ✅ Program จะ Abort พร้อม Error Message ที่ชัดเจน
- ✅ User สามารถดูว่ามี Models อะไรให้ใช้ได้บ้าง
</details>

<details>
<summary><b>5. สามารถมี Factory หลายประเภทใน Class เดียวกันได้ไหม?</b></summary>

**คำตอบ:**
- ✅ **ได้!** เช่น `gradScheme` มี:
  - `declareRunTimeSelectionTable` สำหรับ `mesh` constructor
  - `declareRunTimeSelectionTable` สำหรับ `mesh::interpolation` constructor
- ✅ แต่ละ Table ต้องมีชื่อ Type ที่ต่างกัน
- ✅ Macro จะ Generate Methods แยกกัน (เช่น `New(mesh)`, `New(mesh, interp)`)
</details>

<details>
<summary><b>6. Template Classes ใช้ Factory Pattern ได้ไหม?</b></summary>

**คำตอบ:**
- ✅ **ได้!** ใช้ `defineTemplateRunTimeSelectionTable` และ `defineNamedTemplateRunTimeSelectionTable`
- ✅ Example: `fvPatchField<Type>` เป็น Template Class ที่ใช้ RTS
- ✅ Macro Template จะ Generate RTSTable สำหรับแต่ละ Type instantiation
</details>

---

## 📖 Related Documents

### Design Pattern Series
- **ภาพรวม:** [00_Overview.md](00_Overview.md) - ภาพรวม Design Patterns ใน OpenFOAM
- **Fundamentals:** [01_Introduction.md](01_Introduction.md) - แนะนำ Pattern Fundamentals
- **Strategy Pattern:** [03_Strategy_Pattern.md](03_Strategy_Pattern.md) - การเลือก Algorithm แบบ Dynamic
- **Pattern Synergy:** [04_Pattern_Synergy.md](04_Pattern_Synergy.md) - การใช้ Factory + Strategy ร่วมกัน
- **Performance:** [05_Performance_Analysis.md](05_Performance_Analysis.md) - ผลกระทบต่อ Performance

### Related OpenFOAM Concepts
- **Polymorphism:** [02_Inheritance_Polymorphism.md](../02_INHERITANCE_POLYMORPHISM/00_Overview.md) - พื้นฐาน Polymorphism
- **Template Programming:** [01_Template_Programming.md](../01_TEMPLATE_PROGRAMMING/00_Overview.md) - Template Fundamentals

### Practice & Implementation
- **Practical Exercise:** [06_Practical_Exercise.md](06_Practical_Exercise.md) - ฝึกสร้าง Custom Model ด้วย Factory Pattern

---

**Next:** [03_Strategy_Pattern.md](03_Strategy_Pattern.md) - เรียนรู้วิธีการเปลี่ยน Algorithm แบบ Runtime ด้วย Strategy Pattern