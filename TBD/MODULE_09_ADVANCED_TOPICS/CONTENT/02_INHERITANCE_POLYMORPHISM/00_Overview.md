# 🧬 การสืบทอด โพลิมอร์ฟิซึม และการเลือกขณะทำงานในโมเดล OpenFOAM

**กลุ่มเป้าหมาย**: โปรแกรมเมอร์ C++ ระดับกลางที่กำลังเปลี่ยนไปสู่ความคิดแบบสถาปัตยกรรมของ OpenFOAM
**โฟกัส**: เหตุผลทางสถาปัตยกรรม "ทำไม" เบื้องหลังลำดับชั้นการสืบทอดและโพลิมอร์ฟิซึมขณะทำงานในระบบหลายเฟส
**แนวคิดหลัก**: Virtual Dispatch, Abstract Base Classes, Factory Pattern, Run-Time Selection Tables (RTS)
**ข้อกำหนดเบื้องต้น**: การสืบทอด C++ พื้นฐาน, ความคุ้นเคยกับชนิดฟิลด์ OpenFOAM

## Abstract Base Classes: รากฐานของสถาปัตยกรรมโมเดล

สถาปัตยกรรมโมเดลของ OpenFOAM พึ่งพา abstract base classes เป็นอย่างมากที่กำหนดอินเทอร์เฟซมาตรฐาน พิจารณาลำดับชั้นของโมเดลเฟส:

```cpp
// Base class ที่ phase models ทั้งหมดสืบทอดมา
template<class Base>
class phaseModel
:
    public Base
{
    // Pure virtual function ที่ derived classes ทั้งหมดต้อง implement
    virtual tmp<volScalarField> rho() const = 0;
    
    // Interface สำหรับการคำนวณ phase fraction
    virtual const volScalarField& alpha() const = 0;
};
```

Abstract base class นี้สร้าง **สัญญา** ที่ phase models ทั้งหมดต้องเติมเต็ม คลาสที่สืบทอดเช่น `gasPhaseModel` หรือ `liquidPhaseModel` จะต้อง implement วิธี `rho()` และ `alpha()` เพื่อให้แน่ใจว่ามี **พฤติกรรมโพลิมอร์ฟิก** ซึ่งโค้ดที่เรียกใช้สามารถทำงานกับ phase model ใดๆ โดยไม่ต้องรู้ชนิดเฉพาะ

## Virtual Dispatch: การแก้ไขวิธีแบบไดนามิก

เมื่อ OpenFOAM เรียกใช้ virtual method บน base class pointer หรือ reference, กลไก **virtual function table (vtable)** จะทำให้แน่ใจว่า derived implementation ที่ถูกต้องถูกเรียกขณะทำงาน:

```cpp
phaseModel* phase = phaseSystem.phase("gas"); // ชี้ไปที่ gasPhaseModel
volScalarField density = phase->rho(); // Dispatches ไปที่ gasPhaseModel::rho()

phase = phaseSystem.phase("water"); // ตอนนี้ชี้ไปที่ liquidPhaseModel  
density = phase->rho(); // Dispatches ไปที่ liquidPhaseModel::rho()
```

กลไกนี้ช่วยให้ **polymorphic containers** ที่ phase models ที่แตกต่างกันสามารถจัดเก็บและเข้าถึงผ่านอินเทอร์เฟซเดียวกัน:

```cpp
List<phaseModel*> phases;
phases.append(new gasPhaseModel(...));
phases.append(new liquidPhaseModel(...));

// อินเทอร์เฟซสม่ำเสมอสำหรับเฟสทั้งหมด
forAll(phases, i)
{
    volScalarField phaseDensity = phases[i]->rho();
    phaseDensity.rename(phases[i]->name() + "Rho");
}
```

## Factory Pattern: การเลือกโมเดลขณะทำงาน

การ implement Factory Pattern ของ OpenFOAM อนุญาตให้เลือกโมเดลผ่าน dictionary entries โดยไม่ต้องคอมไพล์ใหม่ องค์ประกอบหลักประกอบด้วย:

### 1. Runtime Selection Tables (RTS)

```cpp
// ใน phaseModel.H
declareRunTimeSelectionTable
(
    phaseModel,
    phaseModel,
    dictionary,
    (
        const dictionary& dict,
        const phaseSystem& fluid,
        const word& phaseName
    ),
    (dict, fluid, phaseName)
);
```

### 2. Static Creator Methods ใน Derived Classes

```cpp
// ใน gasPhaseModel.C
addToRunTimeSelectionTable
(
    phaseModel,
    gasPhaseModel,
    dictionary
);
```

### 3. Factory Method ใน Base Class

```cpp
// ใน phaseModel.C
autoPtr<phaseModel> phaseModel::New
(
    const dictionary& dict,
    const phaseSystem& fluid,
    const word& phaseName
)
{
    const word modelType(dict.lookup("type"));
    
    typename dictionaryConstructorTable::iterator cstrIter =
        dictionaryConstructorTablePtr_->find(modelType);
        
    return cstrIter()(dict, fluid, phaseName);
}
```

สถาปัตยกรรมนี้ช่วยให้ **การเลือกโมเดลโดยใช้การกำหนดค่า** ซึ่งผู้ใช้ระบุชนิดโมเดลใน dictionary `fvSolution` หรือ `thermophysicalProperties`:

```
phases
{
    gas
    {
        type            gasPhase;    // เลือก gasPhaseModel
        equationOfState idealGas;
    }
    
    water
    {
        type            liquidPhase; // เลือก liquidPhaseModel
        equationOfState isothermal;
    }
}
```

## สถาปัตยกรรมระบบหลายเฟส: การประกอบของโมเดล

ระบบเฟสสาธิตให้เห็นว่า OpenFOAM ประกอบ model hierarchies หลายอย่างเข้าด้วยกันในกรอบการหลายเฟสที่สอดคล้องกัน:

```cpp
template<class Base>
class phaseSystem
:
    public Base
{
    // Composition: Container ของ phase model pointers
    HashPtrTable<phaseModel> phases_;
    
    // การเข้าถึงคุณสมบัติเฟสแบบโพลิมอร์ฟิก
    const phaseModel& phase(const word& phaseName) const;
    
    // Template method pattern: algorithms ใช้ phase interfaces
    virtual void correct() = 0;
};
```

**Template Method Pattern** ถูกใช้ที่โครงสร้างอัลกอริทึมพื้นฐานคงที่ใน base class, แต่การ implement เฉพาะแตกต่างกัน:

```cpp
// โครงสร้างอัลกอริทึมพื้นฐาน
void multiphaseSystem::correct()
{
    // ลำดับคงที่
    correctThermo();
    correctPhaseFractions();
    correctTurbulence();      // Virtual call ไปยัง derived implementation
    correctSpecies();
}

// Derived systems ให้การแก้ไข turbulence เฉพาะ
void reactingMultiphaseSystem::correctTurbulence()
{
    // การแก้ไข turbulence เฉพาะการไหลแบบปฏิกิริยา
    forAll(phases_, phaseI)
    {
        calculateReactiveEffects(phases_[phaseI]);
    }
}
```

## พิจารณาด้านประสิทธิภาพในสถาปัตยกรรมของ OpenFOAM

### กลยุทธ์การจัดการหน่วยความจำ

OpenFOAM ใช้ **reference-counted smart pointers** เพื่อจัดการวัตถุตลอดช่วงชีวิตอย่างมีประสิทธิภาพ:

```cpp
// tmp<T> ให้การจัดการหน่วยความจำอัตโนมัติ
tmp<volScalarField> phaseModel::rho() const
{
    // การส่งคืนค่าโดยค่ากระตุ้น move semantics ที่มีประสิทธิภาพ
    return tmp<volScalarField>::New(rhoField_);
}
```

### การเพิ่มประสิทธิภาพขณะคอมไพล์เทียบกับขณะทำงาน

แม้ว่า virtual dispatch จะให้ความยืดหยุ่น, OpenFOAM ใช้ **CRTP (Curiously Recurring Template Pattern)** เพื่อการเพิ่มประสิทธิภาพขณะคอมไพล์เมื่อทราบชนิดโมเดล:

```cpp
template<class DerivedType>
class phaseModelTemplate
{
    // CRTP ช่วยให้ polymorphism ขณะคอมไพล์
    const DerivedType& derived() const
    {
        return static_cast<const DerivedType&>(*this);
    }
    
    void efficientOperation()
    {
        // การเรียกโดยตรงไปยัง derived method โดยไม่มีค่าใช้จ่าย virtual
        derived().specificImplementation();
    }
};
```

### การแทรกและการเชี่ยวชาญเทมเพลต

เส้นทางสำคัญใน OpenFOAM ใช้ template specialization เพื่อกำจัดค่าใช้จ่าย virtual:

```cpp
// รุ่นเฉพาะสำหรับการรวมเฟสที่ทราบ
template<>
inline void phaseSystem<twoPhaseSystem>::solveContinuity()
{
    // เพิ่มประสิทธิภาพสำหรับสองเฟสพอดี
    alpha1_ = 1.0 - alpha2_; // การกำหนดค่าโดยตรงโดยไม่มี virtual call
    alpha2_ = 1.0 - alpha1_;
}
```

## เทคนิคโพลิมอร์ฟิซึมขั้นสูง

### การสืบทอดหลายครั้งในการประกอบโมเดล

โมเดลที่ซับซ้อนเช่น `thermoPhaseModel` สืบทอดจาก base classes หลายตัว:

```cpp
class thermoPhaseModel
:
    public phaseModel,
    public fluidThermo,
    public turbulenceModel
{
    // การสืบทอดแบบ virtual แก้ไขปัญหา diamond
public:
    virtual tmp<volScalarField> kappa() const = 0;  // ความนำความร้อน
    virtual tmp<volScalarField> alpha() const = 0;  // ค่าสภาพการแพร่
};
```

### ประเภทการส่งคืนแบบ Covariant

OpenFOAM ใช้ประโยชน์จาก covariant return types สำหรับการโคลนแบบปลอดภัยชนิด:

```cpp
class phaseModel
{
public:
    virtual autoPtr<phaseModel> clone() const = 0;
};

class gasPhaseModel
:
    public phaseModel
{
public:
    // Covariant return: ส่งคืน gasPhaseModel pointer
    virtual autoPtr<gasPhaseModel> clone() const override
    {
        return autoPtr<gasPhaseModel>::New(*this);
    }
};
```

## การจัดการข้อผิดพลาดและความแข็งแกร่ง

### การดาวน์แคสต์แบบปลอดภัยด้วย `dynamic_cast`

OpenFOAM ใช้ `dynamic_cast` สำหรับการดาวน์แคสต์แบบปลอดภัยเมื่อต้องการฟังก์ชันการทำงานเฉพาะ:

```cpp
void phaseSystem::solveReactingPhases()
{
    forAll(phases_, i)
    {
        // การดาวน์แคสต์แบบปลอดภัยไปยัง reactive phase
        const reactivePhaseModel* reactivePhase = 
            dynamic_cast<const reactivePhaseModel*>(&phases_[i]);
            
        if (reactivePhase)
        {
            reactivePhase->solveReactions();
        }
    }
}
```

### การป้องกันพอยน์เตอร์ว่าง

Factory methods รวมการจัดการข้อผิดพลาดที่แข็งแกร่ง:

```cpp
autoPtr<phaseModel> phaseModel::New
(
    const dictionary& dict,
    const phaseSystem& fluid,
    const word& phaseName
)
{
    const word modelType(dict.lookup("type"));
    
    typename dictionaryConstructorTable::iterator cstrIter =
        dictionaryConstructorTablePtr_->find(modelType);
        
    if (cstrIter == dictionaryConstructorTablePtr_->end())
    {
        FatalIOErrorInFunction(dict)
            << "Unknown phaseModel type " << modelType << endl
            << "Valid phaseModel types:" << nl
            << dictionaryConstructorTablePtr_->sortedToc()
            << exit(FatalIOError);
    }
    
    return cstrIter()(dict, fluid, phaseName);
}
```

## สรุปรูปแบบการออกแบบ

| รูปแบบ | วัตถุประสงค์ | ตัวอย่าง OpenFOAM |
|---------|---------|------------------|
| **Abstract Factory** | สร้างกลุ่มของวัตถุที่เกี่ยวข้อง | `phaseModel::New()` |
| **Template Method** | โครงร่างอัลกอริทึมพร้อมขั้นตอนตัวแปร | `phaseSystem::correct()` |
| **Strategy** | ห่อหุ้มอัลกอริทึมสำหรับการแลกเปลี่ยน | `turbulenceModel` hierarchy |
| **Observer** | แจ้งวัตถุที่พึ่งพาการเปลี่ยนแปลงสถานะ | `phaseSystem::correctThermo()` |
| **Composite** | จัดการกลุ่มวัตถุเป็นวัตถุเดียว | `phaseSystem` ที่มี `phaseModel` หลายตัว |

แนวทางสถาปัตยกรรมนี้ช่วยให้ OpenFOAM สามารถให้ **กรอบการทำงานที่ขยายได้ บำรุงรักษาได้** ซึ่งโมเดลใหม่สามารถเพิ่มโดยไม่ต้องแก้ไขโค้ดที่มีอยู่, ในขณะเดียวกันรักษา **ประสิทธิภาพสูง** ผ่านการเพิ่มประสิทธิภาพอย่างระมัดระวังของเส้นทางสำคัญ
