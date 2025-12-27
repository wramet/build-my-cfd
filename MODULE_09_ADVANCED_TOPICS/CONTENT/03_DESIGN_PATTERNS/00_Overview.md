# 🏭🔀 Design Patterns ใน OpenFOAM: Factory & Strategy Patterns

## 📑 สารบัญ

- [ภาพรวม](#ภาพรวมoverview)
- [ความสำคัญของ Design Patterns ใน OpenFOAM](#ความสำคัญของ-design-patterns-ใน-openfoam)
- [Factory Pattern](#-factory-pattern-การสร้างออบเจกต์ใน-runtime)
- [Strategy Pattern](#-strategy-pattern-อัลกอริทึมที่แทนที่ได้)
- [ความสอดคล้องระหว่าง Factory และ Strategy](#ความสอดคล้องระหว่าง-factory-และ-strategy)
- [การนำไปประยุกต์ใช้](#การนำไปประยุกต์ใช้)
- [การวิเคราะห์ประสิทธิภาพ](#การวิเคราะห์ประสิทธิภาพ)
- [สรุป](#สรุป)

---

## ภาพรวม(Overview)

**บทบาท**: OpenFOAM Developer และผู้เชี่ยวชาญด้านสถาปัตยกรรม C++
**เป้าหมาย**: คำอธิบายเชิงลึกเกี่ยวกับ Design Patterns ที่ใช้ใน OpenFOAM ไม่ใช่เพียงแค่การใช้งาน syntax

สถาปัตยกรรมของ OpenFOAM เป็น masterclass ในการประยุกต์ใช้ Design Patterns ของ C++ สมัยใหม่ โดยเฉพาะ **Factory Pattern** และ **Strategy Pattern** ซึ่งทำให้ OpenFOAM มีความยืดหยุ่น สามารถขยายได้ และบำรุงรักษาได้ง่าย หนังสือนี้จะเจาะลึกทั้งสอง Patterns ที่เป็นรากฐานของ OpenFOAM

---

## ความสำคัญของ Design Patterns ใน OpenFOAM

### ปัญหาที่ OpenFOAM แก้ไข

การจำลอง CFD (Computational Fluid Dynamics) ต้องการ:

- ✅ **การเลือกโมเดลแบบไดนามิก** ใน runtime เช่น การเปลี่ยนโมเดลความปั่นป่วนโดยไม่ต้องคอมไพล์ใหม่
- ✅ **สถาปัตยกรรม solver ที่ขยายได้** สามารถเพิ่มโมเดลฟิสิกส์ใหม่โดยไม่ต้องแก้โค้ดหลัก
- ✅ **การจัดการ boundary condition ที่ยืดหยุ่น** สลับรูปแบบเชิงตัวเลขผ่านไฟล์พจนานุกรม
- ✅ **การปรับสมดุลระหว่างประสิทธิภาพใน compile-time** กับ **ความยืดหยุ่นใน runtime**

OpenFOAM แก้ไขความท้าทายเหล่านี้ด้วยการใช้ Design Patterns อย่างกว้างขวางซึ่งให้ความสมดุลที่เหมาะสมระหว่างความยืดหยุ่นและประสิทธิภาพ

### แนวคิดพื้นฐาน: Code Archaeology & Concept over Syntax

เมื่อศึกษาโค้ด OpenFOAM เราต้องมองเหมือนนักโบราณคดีที่ค้นพบชั้นของการตัดสินใจในการออกแบบ แต่ละชั้นเผยให้เห็นข้อมูลเชิงลึกเกี่ยวกับฟิสิกส์การคำนวณและสถาปัตยกรรมซอฟต์แวร์

> **"ทำไมถึงออกแบบแบบนี้?"**
> สถาปัตยกรรมของ OpenFOAM สะท้อนถึงวิวัฒนาการของ CFD หลายทศวรรษ โดยแต่ละ Pattern แก้ไขปัญหาการคำนวณเฉพาะทาง

---

## 🏭 Factory Pattern (การสร้างออบเจกต์ใน Runtime)

### Hook: เครื่องจำหน่าย CFD

จินตนาการเครื่องจำหน่ายสำหรับโมเดลฟิสิกส์ คุณแทรก dictionary (เหรียญ) ที่มี `type: "kEpsilon"` กดปุ่ม และออกมาเป็นโมเดลความปั่นป่วนที่สมบูรณ์ คุณไม่จำเป็นต้องรู้ว่ามันถูกประกอบขึ้นภายในอย่างไร การทำนายซ้อนที่สวยงามนี้แก้ไขความท้าทายพื้นฐานของ CFD:

> **จะสร้างออบเจกต์ที่ประเภทแน่นอนเป็นที่รู้จักเฉพาะใน runtime จากข้อมูลผู้ใช้ได้อย่างไร?**

### Blueprint: อินเทอร์เฟซนามธรรมและมาโคร

```cpp
// Abstract base class with pure virtual functions
class turbulenceModel
{
public:
    // Runtime type information
    TypeName("turbulenceModel");

    // Pure virtual interface - enforces implementation
    virtual tmp<volScalarField> k() const = 0;
    virtual tmp<volScalarField> epsilon() const = 0;
    virtual void correct() = 0;

    // Factory method (static) - main entry point
    static autoPtr<turbulenceModel> New
    (
        const volVectorField& U,
        const surfaceScalarField& phi,
        transportModel& transport,
        const word& propertiesName
    );

    virtual ~turbulenceModel() {}
};

// Runtime selection table declaration
declareRunTimeSelectionTable
(
    autoPtr,
    turbulenceModel,
    dictionary,
    (const volVectorField& U, const surfaceScalarField& phi,
     transportModel& transport, const word& propertiesName)
);
```

**📖 คำอธิบาย:**
- **Abstract Base Class**: `turbulenceModel` เป็นคลาสฐานนามธรรมที่กำหนด interface สำหรับโมเดลความปั่นป่วนทั้งหมด
- **Pure Virtual Functions**: ฟังก์ชัน `k()`, `epsilon()`, และ `correct()` เป็น pure virtual ที่บังคับให้ derived classes ต้อง implement
- **Factory Method**: ฟังก์ชัน `New()` เป็น static method ที่ทำหน้าที่สร้างออบเจกต์แบบไดนามิกตามประเภทที่ระบุใน dictionary
- **Runtime Selection Table**: มาโคร `declareRunTimeSelectionTable` ประกาศตาราง hash table สำหรับเก็บ function pointers ไปยัง constructors ของแต่ละโมเดล

**🔑 แนวคิดสำคัญ:**
1. **Runtime Type Information (RTTI)**: OpenFOAM ใช้ระบบ RTTI แบบ custom ผ่าน `TypeName` macro
2. **Static Factory Method**: ฟังก์ชัน `New()` เป็นจุดเดียวที่ใช้สร้างออบเจกต์ทุกประเภท
3. **Automatic Registration**: แต่ละโมเดลลงทะเบียนตัวเองกับตาราง selection โดยอัตโนมัติ

### กลไกภายใน: Runtime Selection

```cpp
// 1. Constructor table (static hash table)
typedef HashTable<autoPtr<turbulenceModel> (*)(...), word, string> constructorTable;

// 2. The New() selector implementation
autoPtr<turbulenceModel> turbulenceModel::New(...)
{
    const word modelType = dict.lookup("turbulenceModel");

    // Look up constructor in table
    typename constructorTable::iterator cstrIter =
        constructorTablePtr_->find(modelType);

    // Call constructor through function pointer
    return cstrIter()(U, phi, dict);
}
```

**📖 คำอธิบาย:**
- **Constructor Table**: `HashTable` เก็บ function pointers ที่ map จากชื่อโมเดล (string) ไปยัง constructor function
- **Dictionary Lookup**: อ่านประเภทโมเดลจาก dictionary file (เช่น `turbulenceModel kEpsilon;`)
- **Function Pointer Call**: ค้นหา constructor ที่เหมาะสมและเรียกผ่าน function pointer
- **autoPtr Return**: คืนค่าเป็น smart pointer ที่จัดการหน่วยความจำอัตโนมัติ

**🔑 แนวคิดสำคัญ:**
1. **Hash Table Lookup**: การค้นหาเป็น O(1) ทำให้การสร้างออบเจกต์รวดเร็ว
2. **Type Safety**: Compiler ตรวจสอบ signature ของ function pointers ใน compile-time
3. **Decoupling**: โค้ดที่เรียก `New()` ไม่ต้องรู้จัก concrete classes

### ความมหัศจรรย์: Static Initialization

```cpp
// The registrar object's constructor adds entry to global table
// This happens BEFORE main() executes (static initialization)
namespace
{
    class addkEpsilonConstructorToTable
    {
    public:
        addkEpsilonConstructorToTable()
        {
            turbulenceModel::dictionaryConstructorTable::insert
            (
                "kEpsilon",
                &kEpsilon::New
            );
        }
    };

    static addkEpsilonConstructorToTable registerkEpsilon;
}
```

**📖 คำอธิบาย:**
- **Static Initialization**: ตัวแปร `registerkEpsilon` ถูกสร้างก่อนที่ `main()` จะเริ่มทำงาน
- **Registrar Class**: Constructor ของ `addkEpsilonConstructorToTable` ลงทะเบียนโมเดลเข้ากับตาราง
- **Automatic Registration**: ไม่ต้องเขียนโค้ดลงทะเบียนแยก เกิดขึ้นอัตโนมัติ
- **Anonymous Namespace**: จำกัด scope ไม่ให้ชื่อคลาสซ้ำกับไฟล์อื่น

**🔑 แนวคิดสำคัญ:**
1. **Zero-Overhead Abstraction**: ไม่มีค่าใช้จ่าย runtime นอกเหนือจาก static initialization
2. **Plugin Architecture**: Libraries ใหม่สามารถลงทะเบียนโมเดลได้โดยไม่ต้องแก้โค้ดหลัก
3. **Linker Magic**: Linker รวม static objects จากทุก object file เข้าด้วยกัน

### ประโยชน์ของ Factory Pattern

| ประโยชน์ | คำอธิบาย |
|----------|-----------|
| **Dictionary-Driven** | ผู้ใช้เลือกโมเดลผ่านไฟล์ข้อความ |
| **Plugin Architecture** | โมเดลใหม่เป็น shared libraries |
| **Type Safety** | ตรวจสอบใน compile-time |
| **Memory Safety** | `autoPtr` จัดการหน่วยความจำอัตโนมัติ |

---

## 🔀 Strategy Pattern (อัลกอริทึมที่แทนที่ได้)

### Hook: ชุดเครื่องมืออัลกอริทึม CFD

จินตนาการชุดเครื่องมือที่แต่ละอันแก้ปัญหาเฉพาะทาง คุณไม่สนใจว่าประแจทำงานภายในอย่างไร—คุณแค่ต้องการขันสกรู

> **ใน OpenFOAM แบบจำลองแรงลาก, แบบจำลองความปั่นป่วน, และรูปแบบตัวเลขเป็นเครื่องมือ "สลับเปลี่ยนได้" ในชุดเครื่องมือ CFD ของคุณ**

### Blueprint: อินเทอร์เฟซอัลกอริทึม

```cpp
// Strategy Interface
class dragModel
{
public:
    TypeName("dragModel");

    // Pure virtual strategy method
    virtual tmp<surfaceScalarField> K
    (
        const phaseModel& phase1,
        const phaseModel& phase2
    ) const = 0;

    // Factory for runtime selection
    static autoPtr<dragModel> New
    (
        const dictionary& dict,
        const phaseModel& phase1,
        const phaseModel& phase2
    );
};

// Concrete Strategy: Schiller-Naumann Drag
class SchillerNaumann : public dragModel
{
private:
    dimensionedScalar C_;
    dimensionedScalar n_;

public:
    TypeName("SchillerNaumann");

    // Strategy implementation
    virtual tmp<surfaceScalarField> K
    (
        const phaseModel& phase1,
        const phaseModel& phase2
    ) const override
    {
        const volScalarField Re = mag(phase1.U() - phase2.U()) * phase1.d() / phase2.nu();
        const volScalarField Cd = 24.0/Re * (1.0 + 0.15*pow(Re, 0.687));
        return 0.75 * Cd * phase2.rho() * mag(phase1.U() - phase2.U()) / phase1.d();
    }
};
```

**📖 คำอธิบาย:**
- **Strategy Interface**: `dragModel` นิยาม interface สำหรับคำนวณสัมประสิทธิ์แรงลาก
- **Pure Virtual Method**: ฟังก์ชัน `K()` เป็น pure virtual ที่แต่ละโมเดลต้อง implement
- **Concrete Strategy**: `SchillerNaumann` เป็น implementation ที่คำนวณ drag coefficient ตามสมการ Schiller-Naumann
- **Factory Integration**: ฟังก์ชัน `New()` รวมกับ Factory Pattern สำหรับ runtime selection

**🔑 แนวคิดสำคัญ:**
1. **Algorithm Encapsulation**: แต่ละ strategy ห่อหุ้มอัลกอริทึมทางคณิตศาสตร์เฉพาะ
2. **Interchangeability**: สามารถสลับ strategy ใน runtime โดยไม่ต้องแก้โค้ดที่เรียกใช้
3. **Polymorphism**: โค้ดที่เรียกใช้ทำงานกับ interface ไม่ใช่ concrete implementation

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C`

### กลไกภายใน: Strategy + Factory Synergy

OpenFOAM ผสาน Strategy Pattern (การ abstract อัลกอริทึม) กับ Factory Pattern (การสร้างใน runtime):

```cpp
// 1. Dictionary ระบุอัลกอริทึม
dragModel
{
    type            SchillerNaumann;  // Strategy selection
    C               0.44;
    n               1.0;
}

// 2. Factory สร้าง concrete strategy
autoPtr<dragModel> drag = dragModel::New(dragDict, phase1, phase2);

// 3. ใช้อัลกอริทึมแบบ polymorphic
surfaceScalarField Kdrag = drag->K(phase1, phase2);
```

**📖 คำอธิบาย:**
- **Dictionary Configuration**: ไฟล์ `dict` ระบุประเภทของ strategy ผ่าน keyword `type`
- **Factory Creation**: ฟังก์ชัน `New()` สร้าง concrete strategy ตามประเภทที่ระบุ
- **Polymorphic Usage**: โค้ดที่เรียกใช้ไม่ต้องรู้ว่าเป็น strategy ใด เพียงเรียก `K()` ผ่าน pointer ของ base class
- **Runtime Flexibility**: สามารถเปลี่ยน strategy โดยแก้ไข dictionary โดยไม่ต้อง recompile

**🔑 แนวคิดสำคัญ:**
1. **Separation of Concerns**: การสร้าง (Factory) แยกจากการใช้งาน (Strategy)
2. **Open/Closed Principle**: เปิดสำหรับ extension (เพิ่ม strategy ใหม่) ปิดสำหรับ modification
3. **Configuration-Driven**: พฤติกรรมโปรแกรมขับเคลื่อนด้วยไฟล์ configuration ไม่ใช่ hard-coded

### กลไก: การ Encapsulation อัลกอริทึมคณิตศาสตร์

**Schiller-Naumann Drag**:
$$
C_D = \frac{24}{\mathrm{Re}} (1 + 0.15\mathrm{Re}^{0.687})
$$

**Ergun Drag** (สำหรับ packed beds):
$$
K = 150 \frac{(1-\alpha)^2 \mu}{\alpha d_p^2} + 1.75 \frac{(1-\alpha) \rho |\mathbf{U}|}{d_p}
$$

**Gibilaro Drag**:
$$
K = \frac{17.3}{\mathrm{Re}} + 0.336
$$

> Strategy Pattern ทำให้เป็นไปได้: การสลับเปลี่ยนระหว่างสูตรทางคณิตศาสตร์เหล่านี้ผ่านการกำหนดค่า dictionary โดยไม่ต้องเปลี่ยนโค้ด

---

## ความสอดคล้องระหว่าง Factory และ Strategy

ความเยี่ยมทางสถาปัตยกรรมที่แท้จริงของ OpenFOAM อยู่ที่การรวมรูปแบบ Factory และ Strategy เข้าด้วยกัน

### พลังของการผสมผสาน

```cpp
// 1. Strategy Interface (การนามธรรมอัลกอริทึม)
class physicsModel
{
public:
    virtual void solve() = 0;
    virtual autoPtr<volScalarField> calculate() const = 0;

    // 2. Factory Method (การสร้างในรันไทม์)
    static autoPtr<physicsModel> New(const dictionary& dict);
};

// การใช้งานในโซลเวอร์:
autoPtr<physicsModel> model = physicsModel::New(dict);  // Factory
model->solve();                                          // Strategy
```

**📖 คำอธิบาย:**
- **Dual Interface**: `physicsModel` ทำหน้าที่เป็นทั้ง Strategy interface และ Factory entry point
- **Factory Creates**: ฟังก์ชัน `New()` สร้าง concrete strategy ตาม dictionary
- **Strategy Executes**: ฟังก์ชัน `solve()` และ `calculate()` ทำงานแบบ polymorphic
- **Clean Separation**: การสร้างแยกจากการใช้งาน แต่รวมอยู่ใน interface เดียว

**🔑 แนวคิดสำคัญ:**
1. **Synergy**: Factory + Strategy = ความยืดหยุ่นสูงสุด
2. **Minimal Interface**: Interface เดียวทั้งการสร้างและการใช้งาน
3. **Runtime Composition**: สามารถประกอบโมเดลที่ซับซ้อนจาก strategies หลายตัว

### เฟรมเวิร์กคณิตศาสตร์

จากมุมมองทางคณิตศาสตร์ การผสาน Factory-Strategy ใช้การแมปที่ซับซ้อน:

กำหนด:
- $\mathcal{A}$ = ช่องว่างอัลกอริทึม (Strategy implementations ทั้งหมด)
- $\mathcal{I}$ = ช่องว่างอินเทอร์เฟซ (abstract base classes)
- $\mathcal{F}$ = ฟังก์ชันการแมป Factory
- $\mathcal{P}$ = ช่องว่างพารามิเตอร์ (dictionary configurations)

ระบบที่ผสานใช้ความสัมพันธ์:

$$
\mathcal{F}: \mathcal{P} \to \mathcal{A} \to \mathcal{I}
$$

โดยที่:
- **Strategy** กำหนด $\mathcal{A} \to \mathcal{I}$ (การแมปอัลกอริทึมไปยังอินเทอร์เฟซ)
- **Factory** กำหนด $\mathcal{P} \to \mathcal{A}$ (การแมปพารามิเตอร์ไปยังอัลกอริทึม)

### เมทริกซ์รูปแบบการออกแบบใน OpenFOAM

| รูปแบบ | ตัวอย่าง | วัตถุประสงค์ | การใช้งานใน OpenFOAM |
|---------|---------|---------|-------------------------|
| **Factory Method** | `turbulenceModel::New()` | การสร้างออบเจกต์ | `declareRunTimeSelectionTable` |
| **Strategy** | `dragModel::K()` | การห่อหุ้มอัลกอริทึม | ฟังก์ชันเสมือนแบบบริสุทธิ์ |
| **Template Method** | `phaseModel::correct()` | โครงร่างอัลกอริทึม | ฟังก์ชันเสมือนที่มีการใช้งานเริ่มต้น |
| **Abstract Factory** | `phaseSystem::New()` | การสร้างแฟมิลี | Factory ที่ซ้อนกัน |

---

## การนำไปประยุกต์ใช้

### ขั้นตอน: โมเดลทางกายภาพใหม่

#### ขั้นที่ 1: การวิเคราะห์ทางกายภาพ

สหสัมพันธ์จำนวน Nusselt $Nu = a \cdot Re^b \cdot Pr^c$ แทนสัมประสิทธิ์การถ่ายเทความร้อนไร้มิติ:

$$h = \frac{Nu \cdot k}{L} = \frac{a \cdot Re^b \cdot Pr^c \cdot k}{L}$$

#### ขั้นที่ 2-3: การออกแบบและ Implement

```cpp
class MyHeatTransfer : public heatTransferModel
{
    dimensionedScalar a_, b_, c_;

public:
    TypeName("myHeatTransfer");

    virtual tmp<volScalarField> h
    (
        const phaseModel& phase1,
        const phaseModel& phase2
    ) const override
    {
        const volScalarField U_rel = mag(phase1.U() - phase2.U());

        const volScalarField Re = max
        (
            U_rel * phase1.d() / max(phase2.nu(), dimensionedScalar("smallNu", dimless, 1e-12)),
            dimensionedScalar("smallRe", dimless, 1e-6)
        );

        const volScalarField Pr = max
        (
            phase2.Cp() * phase2.mu() / max(phase2.kappa(), dimensionedScalar("smallK", dimless, 1e-12)),
            dimensionedScalar("smallPr", dimless, 1e-6)
        );

        const volScalarField Nu = a_ * pow(Re, b_) * pow(Pr, c_);
        return Nu * phase2.kappa() / phase1.d();
    }
};
```

**📖 คำอธิบาย:**
- **Custom Heat Transfer Model**: สร้างโมเดลการถ่ายเทความร้อนที่คำนวณสัมประสิทธิ์ h จาก correlation
- **Nusselt Correlation**: ใช้สมการ $Nu = a \cdot Re^b \cdot Pr^c$ โดย a, b, c เป็นพารามิเตอร์ที่กำหนดได้
- **Safety Guards**: ฟังก์ชัน `max()` ป้องกันการหารด้วยศูนย์โดยใช้ค่าน้อยๆ (smallNu, smallK)
- **Field Operations**: การคำนวณทั้งหมดเป็น field operations แบบ vectorized ไม่ใช่ loop เหนือ elements

**🔑 แนวคิดสำคัญ:**
1. **Parameter Tuning**: a, b, c สามารถกำหนดใน dictionary เพื่อปรับ correlation
2. **Numerical Stability**: การใช้ `max()` กับค่าเล็กๆ ป้องกัน NaN และ Inf
3. **Dimensioned Calculations**: ทุกค่ามีหน่วยติดตัว ตรวจสอบโดยระบบ type system
4. **Polymorphic Integration**: โมเดลใหม่ทำงานกับ solver ที่มีอยู่โดยไม่ต้องแก้ไข

#### ขั้นที่ 4: การลงทะเบียน

```cpp
addToRunTimeSelectionTable
(
    heatTransferModel,
    MyHeatTransfer,
    dictionary
);
```

**📖 คำอธิบาย:**
- **Runtime Registration**: มาโครนี้ลงทะเบียน `MyHeatTransfer` กับตาราง selection ของ `heatTransferModel`
- **Automatic Discovery**: เมื่อ library ถูกโหลด โมเดลจะพร้อมใช้งานทันที
- **Dictionary Keyword**: คำว่า "dictionary" ระบุว่าโมเดลนี้ใช้ dictionary constructor

**🔑 แนวคิดสำคัญ:**
1. **Zero Boilerplate**: ไม่ต้องเขียนโค้ดลงทะเบียนเพิ่ม
2. **Compile-Time Safety**: Compiler ตรวจสอบว่า signature ตรงกับ base class
3. **Linker Integration**: Symbol จะถูก export เมื่อสร้าง shared library

#### ขั้นที่ 5-7: Build และการใช้งาน

**Make/files**:
```makefile
MyHeatTransfer.C
LIB = $(FOAM_USER_LIBBIN)/libMyHeatTransfer
```

**Make/options**:
```makefile
EXE_INC = \
    -I$(LIB_SRC)/finiteVolume/lnInclude \
    -I$(LIB_SRC)/thermophysicalModels/lnInclude

EXE_LIBS = \
    -lfiniteVolume \
    -lthermophysicalModels
```

**การใช้ใน case**:
```cpp
heatTransferModel
{
    type    myHeatTransfer;
    a       0.023;
    b       0.8;
    c       0.4;
}
```

**📖 คำอธิบาย:**
- **Make/files**: ระบุ source files และ library output destination
- **Make/options**: กำหนด include paths และ library dependencies
- **Case Configuration**: ไฟล์ dictionary ระบุ type และ parameters

**🔑 แนวคิดสำคัญ:**
1. **Modular Build**: โมเดลใหม่เป็น library แยก ไม่ใช่ส่วนหนึ่งของ solver
2. **Dynamic Loading**: OpenFOAM โหลด libraries ตาม `controlDict` ผ่าน `libs`
3. **Parameter Injection**: a, b, c ถูกอ่านจาก dictionary และส่งผ่าน constructor

### รายการตรวจสอบการ Debugging

#### ปัญหาการลงทะเบียน Factory

```cpp
// ❌ ผิด: TypeName ไม่ตรงกัน
TypeName("myHeatTransfer");  // lowercase m
// type    MyHeatTransfer;   // Capital M

// ✅ ถูก: ต้องตรงกันทั้งหม้าย
TypeName("myHeatTransfer");
// type    myHeatTransfer;
```

```cpp
// ❌ ผิด: ลงทะเบียนใน .H แทน .C
// MyHeatTransfer.H: addToRunTimeSelectionTable(...)

// ✅ ถูก: ต้องอยู่ใน .C
// MyHeatTransfer.C: addToRunTimeSelectionTable(...)
```

**📖 คำอธิบาย:**
- **Case Sensitivity**: `TypeName` ต้องตรงกับ `type` ใน dictionary ทุกประการ
- **Source File Location**: `addToRunTimeSelectionTable` ต้องอยู่ใน .C ไม่ใช่ .H
- **Duplicate Registration**: ห้ามลงทะเบียนชื่อเดียวกันสองครั้ง

**🔑 แนวคิดสำคัญ:**
1. **Name Consistency**: ตรวจสอบการสะกดชื่อทุกที่
2. **Linker Errors**: ถ้าลงทะเบียนใน .H จะเกิด multiple definition errors
3. **Runtime Debugging**: ใช้ `wmakeLibs` เพื่อดูว่า library โหลดสำเร็จหรือไม่

---

## การวิเคราะห์ประสิทธิภาพ

### โอเวอร์เฮดของ Virtual Function

| ตัวชี้วัด | ค่า |
|-----------|------|
| Field operations (เช่น `U + V`) | ~1000 ns |
| Virtual function call | ~2 ns |
| **โอเวอร์เฮด** | **~0.2% ต่อการเรียก** |

**การอธิบายทางคณิตศาสตร์**:

กำหนด:
- $t_{\text{field}}$ = เวลาการดำเนินการกับ field
- $t_{\text{virtual}}$ = เวลาการส่งผ่านแบบ virtual
- $n$ = จำนวนการดำเนินการต่อ time step

โอเวอร์เฮดสัมพัทธ์:
$$
\frac{T_{\text{virtual}} - T_{\text{static}}}{T_{\text{static}}} = \frac{t_{\text{virtual}}}{t_{\text{field}}} \approx 0.002 \ (0.2\%)
$$

> **สรุป**: โอเวอร์เฮดของ virtual function น้อยมากเมื่อเปรียบกับการดำเนินการกับ field ความยืดหยุ่นที่ได้รับมีค่ามากกว่าค่าใช้จ่ายด้านประสิทธิภาพ

### โอเวอร์เฮดของหน่วยความจำ

| ส่วนประกอบ | หน่วยความจำ |
|------------|--------------|
| แต่ละ strategy object | ~64 bytes |
| การจำลองทั่วไป (10-20 objects) | ~1-2 KB |
| Static tables (1000 types) | ~100 KB |
| **รวม** | **เล็กน้อยเมื่อเปรียบกับ field storage** |

### การปรับให้เหมาะสมประสิทธิภาพ Solver

| Solver Type | Complexity | Memory Usage | Best For |
|-------------|------------|--------------|----------|
| Diagonal | O(n) | Low | Diagonally dominant systems |
| PCG | O(n√n) | Medium | Symmetric positive definite |
| GAMG | O(n log n) | High | Large-scale problems |
| SmoothSolver | O(n²) | Low-Medium | Small-medium problems |

**ผลกระทบของ Preconditioner**:
- ไม่ใช้ preconditioning: 100-1000 iterations
- Diagonal preconditioning: 50-200 iterations
- ILU/GAMG: 10-50 iterations

### Bottlenecks ทั่วไป

```
Linear Solver Convergence:  ████░░░░░░ 40-60%
Matrix Assembly:            ██░░░░░░░░ 15-25%
Boundary Condition Updates: █░░░░░░░░░ 5-15%
File I/O:                   ░░░░░░░░░░ 5-10%
```

---

## สรุป

### Factory Pattern = **"สร้างอะไร"**

Factory Pattern เป็นหัวใจสำคัญของความสามารถในการขยาย โดยเปิดให้มีการสร้างอ็อบเจกต์แบบไดนามิกตามการกำหนดค่าผ่าน Dictionary

```cpp
autoPtr<incompressible::turbulenceModel> turbulence
(
    incompressible::turbulenceModel::New
    (
        modelType, U, phi, transportProperties
    )
);
```

**คุณสมบัติหลัก**:
- 📦 การสร้างโดยใช้ Dictionary
- 🔄 การเลือกประเภทใน Runtime
- 🔌 เปิดให้ใช้ Plugin Architecture
- 🛡️ การจัดการหน่วยความจำอัตโนมัติ

### Strategy Pattern = **"คำนวณอย่างไร"**

Strategy Pattern นิยาม **วิธีการ** ดำเนินการคำนวณ โดยห่อหุ้มตรรกะอัลกอริทึมไว้เบื้องหลัง Interface ที่สม่ำเสมอ

```cpp
// Solver ทำงานกับ Interface ไม่ใช่ Implementation
turbulence->correct();
nut = turbulence->nut();
```

**คุณสมบัติหลัก**:
- 🎯 การห่อหุ้มอัลกอริทึม
- 🔀 การ Implement ที่สามารถสลับที่กันได้
- 📐 การนามธรรมของโมเดลทางคณิตศาสตร์

### พลังรวม = **กรอบ CFD ที่สามารถขยายได้**

เมื่อ Factory และ Strategy Patterns ทำงานร่วมกัน:

- ✅ **ฟิสิกส์ใหม่โดยไม่ต้องแก้ไขโค้ดหลัก**
- ✅ **การ Integrate โมเดลวิจัยได้ง่าย**
- ✅ **การปรับแต่งเฉพาะอุตสาหกรรม**
- ✅ **สถาปัตยกรรมที่บำรุงรักษาและทดสอบง่าย**

### ปรัชญาดีไซน์แพตเทิร์นของ OpenFOAM

> **Factory & Strategy Patterns แปลง CFD จาก "ฟิสิกส์ที่ Hardcoded" ไปสู่ "วิทยาศาสตร์การคำนวณที่สามารถขยายได้"**

สถาปัตยกรรมนี้ทำให้ OpenFOAM พัฒนาอย่างต่อเนื่องกับงานวิจัยในขณะที่ยังคงความมั่นคงและประสิทธิภาพระดับอุตสาหกรรม

ความสวยงามอยู่ที่ว่า Patterns เหล่านี้สอดคล้องกับวิธีคิดแบบ CFD อย่างเป็นธรรมชาติ:
- **Factory Pattern** ≈ การกำหนดค่า Case ที่ไม่ขึ้นกับ Mesh
- **Strategy Pattern** ≈ การเลือกโมเดลทางคณิตศาสตร์
- **การรวมกัน** ≈ ความสามารถ Plug-and-play ของ Solver ฟิสิกส์

---

*เอกสารนี้ใช้หลักสูตร **Code Archaeology** และ **Concept over Syntax** ถาม "ทำไม" ก่อน "อย่างไร" เสมอ และใช้ analogies เพื่อเชื่อมโยงความซับซ้อนของ C++ กับสัญชาตญาณ CFD*

## 📚 เอกสารที่เกี่ยวข้อง (Related Documents)

*   **ถัดไป:** [01_Introduction.md](01_Introduction.md) - บทนำสู่ Design Patterns ใน OpenFOAM