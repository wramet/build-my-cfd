# 08_🎓_LEARNING_PROGRESSION.md

## 🎓 ความคืบหน้าการเรียนรู้

### ระยะที่ 1: การจดจำรูปแบบ (สัปดาห์ที่ 1)

#### 1.1 การระบุการใช้งาน Factory

รูปแบบ Factory Method เป็นพื้นฐานของ polymorphism ขณะทำงานของ OpenFOAM มองหารูปแบบหลักเหล่านี้ใน codebase:

```cpp
// Factory creation pattern - พบได้ทั่วไปใน OpenFOAM
autoPtr<incompressible::turbulenceModel> turbulence
(
    incompressible::turbulenceModel::New
    (
        U,
        phi,
        laminarTransport
    )
);
```

**ตัวระบุหลักที่ต้องค้นหา:**
- การเรียก `ClassName::New()`
- การประกาศ `autoPtr<ClassName>`
- `declareRunTimeSelectionTable` ใน header files
- การใช้งาน `TypeName` macro

#### 1.2 การจดจำรูปแบบ Strategy

รูปแบบ Strategy ปรากฏเป็น pure virtual interfaces พร้อมด้วย concrete implementations:

```cpp
// Abstract strategy interface
class LESdelta
{
public:
    virtual tmp<volScalarField> delta() const = 0;
    virtual ~LESdelta() {}
};

// Concrete strategy implementations  
class vanDriestDelta : public LESdelta
{
    virtual tmp<volScalarField> delta() const override;
};
```

**สัญญาณการระบุ:**
- Pure virtual functions (`= 0`)
- คลาสลูกหลายคลาสจากคลาสแม่เดียวกัน
- การเลือกขณะทำงานผ่านชื่อ string
- `addToRunTimeSelectionTable` macros

#### 1.3 การติดตาม Dictionary Flow

ติดตามการไหลของข้อมูลจาก input files ไปยัง instantiated objects:

```
controlDict:
{
    simulationType  LESModel;
    LESModel        kEqn;         // ← String นี้ขับเคลื่อนการเลือก
    turbulence      on;
}
```

**เส้นทางการปฏิบัติ:**
1. แยกวิเคราะห์ dictionary file → `kEqn` string
2. ค้นหา registry → พบ `kEqn` constructor
3. การสร้างแบบไดนามิก → `autoPtr<kEqn>` object
4. ส่งคืน base class pointer → `LESdelta*` polymorphic interface

### ระยะที่ 2: การเข้าใจรูปแบบ (สัปดาห์ที่ 2)

#### 2.1 การวิเคราะห์ Runtime Selection Table

ความมหัศจรรย์เริ่มต้นด้วย `declareRunTimeSelectionTable` macro:

```cpp
// ใน header file ของคลาสแม่ ( LESdelta.H )
declareRunTimeSelectionTable
(
    LESdelta,               // ชื่อคลาสแม่
    LESdelta,               // ชื่อคลาสแม่ (ซ้ำ)
    dictionary,
    (
        const word& modelType,
        const dictionary& dict,
        const fvMesh& mesh
    ),
    (modelType, dict, mesh)
);
```

**macro นี้ขยายไปเป็น:**
```cpp
// ตัวแปรสมาชิกแบบ static - เก็บ registry
static HashTable<autoPtr<LESdelta>(*/*parameters*/)> dictionaryConstructorTablePtr_;
static const char* dictionaryConstructorTablePtr_[] = {"kEqn", "vanDriest", ...};

// Constructor table accessor
static HashTable<autoPtr<LESdelta>*(...)>& dictionaryConstructorTable();
```

#### 2.2 การขยาย Registration Table

แต่ละ derived class ลงทะเบียนตัวเอง:

```cpp
// ใน source file ของ derived class ( kEqn.H )
addToRunTimeSelectionTable
(
    LESdelta,
    kEqn,
    dictionary
);
```

**Macro ขยายไปเป็น:**
```cpp
// Static constructor
namespace Foam
{
    LESdelta::adddictionaryConstructorToTable<kEqn> 
    addkEqnLESdeltaConstructorToLESdeltaTable_;
}

// Actual registration code
template<class Type>
class LESdelta::adddictionaryConstructorToTable
{
public:
    adddictionaryConstructorToTable(const word& lookup = Type::typeName)
    {
        LESdelta::dictionaryConstructorTablePtr_->set
        (
            lookup, 
            LESdelta::dictionaryConstructorTablePtr_
        );
    }
};
```

#### 2.3 กลไกการลงทะเบียนแบบ Static

การลงทะเบียนเกิดขึ้น **ก่อน `main()`** ผ่าน static initialization:

```cpp
// Execution order ระหว่าง linking
static LESdelta::addRunTimeSelectionTableConstructor<kEqn> 
    addkEqnConstructorToLESdeltaTable_;  // ← สร้างตอน compile time
                                       // ← ลงทะเบียนตอนเริ่มโปรแกรม
```

**ข้อดี:**
- การลงทะเบียนแบบ zero runtime overhead
- การตรวจสอบแบบ type-safe ที่ compile-time
- รองรับการขยายสถาปัตยกรรมแบบ plugin
- ไม่ต้องจัดการวัตถุด้วยตนเอง

### ระยะที่ 3: การประยุกต์ใช้รูปแบบ (สัปดาห์ที่ 3)

#### 3.1 การ implement แบบจำลองแบบกำหนดเองอย่างง่าย

สร้างแบบจำลองความปั่นป่วนแบบกำหนดเองอย่างง่าย:

```cpp
// myCustomModel.H
#ifndef myCustomModel_H
#define myCustomModel_H

#include "LESdelta.H"

namespace Foam
{
class myCustomModel
:
    public LESdelta
{
    // Private data
    const dimensionedScalar deltaCoeff_;

public:
    TypeName("myCustomModel");
    
    // Constructors
    myCustomModel
    (
        const word& modelType,
        const dictionary& dict,
        const fvMesh& mesh
    );
    
    // Destructor
    virtual ~myCustomModel() = default;
    
    // Member functions
    virtual tmp<volScalarField> delta() const;
};
}
#endif
```

```cpp
// myCustomModel.C
#include "myCustomModel.H"
#include "addToRunTimeSelectionTable.H"

namespace Foam
{
    defineTypeNameAndDebug(myCustomModel, 0);
    addToRunTimeSelectionTable(LESdelta, myCustomModel, dictionary);

    myCustomModel::myCustomModel
    (
        const word& modelType,
        const dictionary& dict,
        const fvMesh& mesh
    )
    :
        LESdelta(modelType, dict, mesh),
        deltaCoeff_(dimensionedScalar::lookupOrDefault("deltaCoeff", 0.1))
    {}

    tmp<volScalarField> myCustomModel::delta() const
    {
        return deltaCoeff_ * pow(mesh().V(), 1.0/3.0);
    }
}
```

#### 3.2 การแก้ไขปัญหาการลงทะเบียน

**ข้อผิดพลาดทั่วไปและวิธีแก้ไข:**

```bash
# ข้อผิดพลาด: Unknown LESdelta model myCustomModel
--> FOAM FATAL ERROR:
    Unknown LESdelta model myCustomModel
    
    Valid LESdelta models are:
    4 (kEqn, vanDriest, Prandtl, cubeRootVol)
```

**ขั้นตอนการแก้ไขปัญหา:**

1. **ตรวจสอบความสอดคล้องของ macro:**
```cpp
// ใน header file
declareRunTimeSelectionTable(LESdelta, LESdelta, dictionary, ...)

// ใน source file
addToRunTimeSelectionTable(LESdelta, myCustomModel, dictionary)  // ← ลำดับต้องตรงกัน
```

2. **ตรวจสอบ TypeName:**
```cpp
// ต้องตรงกันพอดี
TypeName("myCustomModel");           // ← ถูกต้อง
addToRunTimeSelectionTable(..., myCustomModel, ...);  // ← ใช้ชื่อคลาส
```

3. **การตรวจสอบ linking:**
```bash
# ตรวจสอบให้แน่ใจว่า object files ถูก link
nm libOpenFOAM.so | grep myCustomModel
nm libLESdelta.so | grep myCustomModel
```

#### 3.3 การทดสอบ Tutorial Case

สร้าง test case เพื่อตรวจสอบแบบจำลองแบบกำหนดเอง:

```cpp
// system/controlDict
application     simpleFoam;

FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      controlDict;
}

// การเลือกแบบจำลอง LESdelta
LESdelta        myCustomModel;

// พารามิเตอร์เฉพาะแบบจำลอง
myCustomModelCoeffs
{
    deltaCoeff    0.15;
}
```

**ขั้นตอนการตรวจสอบ:**

1. **การตรวจสอบการ compile:**
```bash
cd $WM_PROJECT_DIR
./Allwmake libso
wmake libso myCustomModel
```

2. **การทดสอบการทำงาน:**
```bash
cd tutorials/incompressible/simpleFoam/pitzDaily
simpleFoam 2>&1 | grep -i "myCustomModel"
```

3. **การตรวจสอบผลลัพธ์:**
```bash
# ตรวจสอบว่าใช้แบบจำลองแบบกำหนดเองหรือไม่
grep "Selecting LESdelta model" log.simpleFoam
# ผลลัพธ์ควรแสดง: "Selecting LESdelta model myCustomModel"
```

### ระยะที่ 4: การเชี่ยวชาญรูปแบบ (สัปดาห์ที่ 4)

#### 4.1 การออกแบบสถาปัตยกรรม Model Family

ออกแบบแบบจำลองแบบใหม่ที่มีหลาย strategy:

```cpp
// multiphysicsModel.H
class multiphysicsModel
:
    public regIOobject
{
    // Strategy pattern สำหรับ physics ต่างๆ
    autoPtr<momentumTransferModel> momentumTransfer_;
    autoPtr<heatTransferModel> heatTransfer_;
    autoPtr<massTransferModel> massTransfer_;

public:
    declareRunTimeSelectionTable
    (
        multiphysicsModel,
        multiphysicsModel,
        dictionary,
        (
            const word& name,
            const fvMesh& mesh,
            const dictionary& dict
        ),
        (name, mesh, dict)
    );
    
    // Factory method
    static autoPtr<multiphysicsModel> New
    (
        const fvMesh& mesh,
        const dictionary& dict
    );
};
```

**รูปแบบการลงทะเบียนหลาย strategy:**

```cpp
// ตระกูล momentumTransferModels
class momentumTransferModel
{
public:
    declareRunTimeSelectionTable
    (
        momentumTransferModel,
        momentumTransferModel, 
        dictionary,
        (const dictionary& dict),
        (dict)
    );
    
    static autoPtr<momentumTransferModel> New
    (
        const dictionary& dict
    );
};

// การ implement แบบจำเพาะ
class dragModel : public momentumTransferModel
{
    addToRunTimeSelectionTable
    (
        momentumTransferModel,
        dragModel,
        dictionary
    );
};

class liftModel : public momentumTransferModel  
{
    addToRunTimeSelectionTable
    (
        momentumTransferModel,
        liftModel,
        dictionary
    );
};
```

#### 4.2 การเพิ่มประสิทธิภาพสำหรับ Performance-Critical

**การเพิ่มประสิทธิภาพ Template Specialization:**

```cpp
// เพิ่มประสิทธิภาพ fast path สำหรับบางประเภทที่รู้จัก
template<>
autoPtr<multiphysicsModel> multiphysicsModel::New<momentumTransferModel>
(
    const fvMesh& mesh,
    const dictionary& dict
)
{
    const word modelType(dict.lookup("momentumTransferModel"));
    
    // Compile-time dispatch - หลีกเลี่ยง overhead ของ virtual function
    if (modelType == "dragModel")
    {
        return autoPtr<multiphysicsModel>
        (
            new specializedDragModel(mesh, dict)
        );
    }
    else if (modelType == "liftModel") 
    {
        return autoPtr<multiphysicsModel>
        (
            new specializedLiftModel(mesh, dict)
        );
    }
    
    // กลับไปใช้ registry ทั่วไป
    return New(mesh, dict);
}
```

**การเพิ่มประสิทธิภาพ Memory Pool:**

```cpp
class memoryPoolManager
{
    static memoryPoolManager& instance()
    {
        static memoryPoolManager singleton;
        return singleton;
    }
    
    // Object pool
    List<multiphysicsModel*> modelPool_;
    label poolSize_;
    
public:
    multiphysicsModel* acquire()
    {
        if (poolSize_ > 0)
        {
            return modelPool_[--poolSize_];
        }
        return new multiphysicsModel();
    }
    
    void release(multiphysicsModel* model)
    {
        if (poolSize_ < modelPool_.size())
        {
            modelPool_[poolSize_++] = model;
        }
        else
        {
            delete model;
        }
    }
};
```

#### 4.3 เอกสารสำหรับนักพัฒนา

**เทมเพลตการจัดทำเอกสารรูปแบบ:**

```markdown
# เอกสารรูปแบบการออกแบบ [ModelName]

## ภาพรวมรูปแบบ
- **ประเภทรูปแบบ**: Strategy + Factory
- **สถานการณ์ที่เหมาะสม**: การสร้างแบบจำลอง coupled multiphysics
- **ลักษณะประสิทธิภาพ**: $O(n)$ time complexity, $O(1)$ space complexity

## แผนภาพสถาปัตยกรรม
```
[Dictionary Input] → [Runtime Selection] → [Strategy Objects]
     ↓                        ↓                        ↓
  การแยกวิเคราะห์ไฟล์ ← การระบุประเภท ← Constructor Table → [concreteStrategyA]
                                                                        [concreteStrategyB] 
                                                                        [concreteStrategyC]
```

## ตัวอย่างการใช้งาน
```cpp
// สร้างแบบจำลอง multiphysics
autoPtr<multiphysicsModel> model = multiphysicsModel::New(mesh, dict);

// กำหนดค่า strategy
model->setMomentumStrategy("dragModel");
model->setHeatStrategy("conjugateHeatModel");  

// การแก้ปัญหาขณะทำงาน
while (runTime.loop())
{
    model->solve();
}
```

## การทดสอบประสิทธิภาพ
| ขนาดแบบจำลอง | Virtual function call(ns) | Template specialization(ns) | อัตราเร่ง |
|----------------|--------------------------|-----------------------------|-------------|
| 1K cells       | 125                      | 89                          | 1.40×       |
| 100K cells     | 12500                    | 8900                        | 1.40×       |
| 1M cells       | 125000                   | 89000                       | 1.40×       |

## แนวทางการขยาย
1. สืบทอด `multiphysicsModel` base class
2. implement `declareRunTimeSelectionTable` macro
3. เพิ่ม `addToRunTimeSelectionTable` registration
4. แทนที่ core virtual functions
5. เพิ่ม source files ใน `Make/files`
```

**รายการตรวจสอบ Best Practices:**

- [ ] ใช้ `autoPtr` จัดการ object lifecycle
- [ ] implement virtual functions ที่จำเป็นทั้งหมดอย่างถูกต้อง  
- [ ] เพิ่ม `TypeInfo` และ `TypeName` macros ที่เหมาะสม
- [ ] implement `write()` method สำหรับ data serialization
- [ ] จัดเตรียมเอกสารและตัวอย่างที่สมบูรณ์
- [ ] รวม unit test coverage
- [ ] พิจารณา thread safety
- [ ] ปรับให้เหมาะสมกับประสิทธิภาพ critical path

ผ่านการเรียนรู้และฝึกปฏิบัติอย่างเป็นระบบในสี่ระยะนี้ คุณจะเชี่ยวชาญรูปแบบการออกแบบหลักของ OpenFOAM และสามารถขยายและปรับแต่ง CFD framework อันทรงพลังนี้ได้อย่างมีประสิทธิภาพ
