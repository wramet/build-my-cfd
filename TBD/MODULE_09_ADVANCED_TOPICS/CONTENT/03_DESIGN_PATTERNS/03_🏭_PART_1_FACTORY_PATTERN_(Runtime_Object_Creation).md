## 🏭 ส่วนที่ 1: FACTORY PATTERN (การสร้างออบเจกต์ในขณะทำงาน)

### 1. "Hook": เครื่องจำหน่าย CFD

จินตนาการเครื่องจำหน่ายสำหรับโมเดลฟิสิกส์ คุณแทรก dictionary (เหรียญ) ที่มี `type: "kEpsilon"` กดปุ่ม และออกมาเป็นโมเดลความปั่นป่วนที่สมบูรณ์ คุณไม่จำเป็นต้องรู้ว่ามันถูกประกอบขึ้นภายในอย่างไร การทำนายซ้อนที่สวยงามนี้แก้ไขความท้าทายพื้นฐานของ CFD อย่างหนึ่ง: วิธีการสร้างออบเจกต์ที่ประเภทที่แน่นอนจะเป็นที่รู้จักเฉพาะในขณะทำงานจากข้อมูลที่ผู้ใช้ป้อน (dictionary files)?

ในการเขียนโปรแกรม C++ แบบดั้งเดิม คุณอาจใช้ if-else chains ที่ต้องการการคอมไพล์ใหม่สำหรับโมเดลใหม่:
```cpp
// Hardcoded approach - requires recompilation for new models
if (turbModelType == "kEpsilon") {
    return autoPtr<turbulenceModel>(new kEpsilonModel(...));
} else if (turbModelType == "kOmega") {
    return autoPtr<turbulenceModel>(new kOmegaModel(...));
} // Must modify this file for each new model
```

โซลูชันของ OpenFOAM ใช้ runtime selection tables ที่เปิดใช้งานสถาปัตยกรรมปลั๊กอินจริง ซึ่งหมายความว่าโมเดลฟิสิกส์ใหม่สามารถคอมไพล์แยกกันและค้นพบโดยอัตโนมัติในขณะทำงาน เหมือนกับการเพิ่มน้ำอัดลมใหม่ในเครื่องจำหน่ายโดยไม่ต้องออกแบบเครื่องทั้งหมดใหม่

Factory pattern มีความสำคัญเป็นพิเศษในการจำลอง CFD ที่ผู้ใช้มักจะทดลองกับโมเดลความปั่นป่วนที่แตกต่างกัน, เงื่อนไขขอบเขต, รูปแบบตัวเลข และโมเดลฟิสิกส์ โดยไม่มี pattern นี้ ผู้ใช้จะต้องคอมไพล์ solver ทั้งหมดใหม่เพียงเพื่อเปลี่ยนจากโมเดล $k-\epsilon$ เป็นโมเดล $k-\omega$

### 2. แบบแผน: อินเทอร์เฟซนามธรรมและมาโคร

การแยกอินเทอร์เฟซจากการใช้งานตามหลักการออกแบบเชิงวัตถุที่ให้ข้อดีหลายประการสำหรับการคำนวณทางวิทยาศาสตร์:

**Extensibility**: โมเดลความปั่นป่วนใหม่สามารถเพิ่มได้โดยไม่ต้องแก้ไขโค้ด solver หลัก นักวิจัย CFD สามารถพัฒนาโมเดลความปั่นป่วนแบบกำหนดเองเป็นไลบรารีแยกต่างหากและวางลงในการติดตั้ง OpenFOAM

**Maintainability**: การแยกความกังวลอย่างชัดเจนหมายความว่าตรรกะ solver ยังคงเป็นอิสระจากการใช้งานโมเดลเฉพาะ ซึ่งทำให้การ debug ง่ายขึ้นและอนุญาตให้พัฒนาส่วนประกอบโมเดลที่แตกต่างกันได้พร้อมกัน

**Testability**: อินเทอร์เฟซสามารถจำลองสำหรับการทดสอบหน่วย ทำให้สามารถทดสอบอัลกอริทึม solver อย่างครอบคลุมโดยไม่ต้องการโมเดลฟิสิกส์ที่ซับซ้อน

องค์ประกอบไวยากรณ์หลักทำงานร่วมกันเพื่อสร้างสถาปัตยกรรมที่ยืดหยุ่นนี้:

```cpp
// 1. Abstract base class with pure virtual functions
class turbulenceModel
{
public:
    // Runtime type information - enables identification
    TypeName("turbulenceModel");

    // Pure virtual interface - enforces implementation requirements
    virtual tmp<volScalarField> k() const = 0;
    virtual tmp<volScalarField> epsilon() const = 0;
    virtual void correct() = 0;

    // Factory method (static) - main entry point for object creation
    static autoPtr<turbulenceModel> New
    (
        const volVectorField& U,
        const surfaceScalarField& phi,
        transportModel& transport,
        const word& propertiesName
    );

    // Virtual destructor - ensures proper cleanup
    virtual ~turbulenceModel() {}
};

// 2. Runtime selection table declaration (header)
declareRunTimeSelectionTable
(
    autoPtr,                // Return type - smart pointer for memory management
    turbulenceModel,        // Base class name
    dictionary,            // Constructor parameter types...
    (const volVectorField& U, const surfaceScalarField& phi, transportModel& transport, const word& propertiesName)
);

// 3. Runtime selection table definition (source)
defineRunTimeSelectionTable(turbulenceModel, dictionary, 
    (const volVectorField& U, const surfaceScalarField& phi, transportModel& transport, const word& propertiesName));
```

ประเภทการคืนค่า `tmp<volScalarField>` เป็นสิ่งสำคัญเป็นพิเศษในกลยุทธ์การจัดการหน่วยความจำของ OpenFOAM มันใช้การนับการอ้างอิงเพื่อจัดการหน่วยความจำฟิลด์โดยอัตโนมัติและหลีกเลี่ยงการคัดลอกที่ไม่จำเป็น ซึ่งเป็นสิ่งสำคัญสำหรับประสิทธิภาพในการจำลอง CFD ขนาดใหญ่

### 3. กลไกภายใน: `New()` Selector และมาโคร

ความมหัศจรรย์ของ factory pattern อยู่ในระบบมาโครที่ซับซ้อนของ OpenFOAM ที่ทำให้การลงทะเบียนออบเจกต์เป็นไปโดยอัตโนมัติ มาตรวจสอบแต่ละส่วนประกอบ:

#### `TypeName` Macro
```cpp
// Expands to static member functions for type identification
#define TypeName(TypeNameString)                                    \
    static const ::Foam::word typeName;                            \
    static const ::Foam::word& type() { return typeName; }         \
    virtual const ::Foam::word& type() const { return typeName; }
```

มาโครนี้สร้างฟังก์ชันที่จำเป็นสามฟังก์ชัน:
1. ที่เก็บข้อมูลสตริงประเภทแบบสแตติก
2. getter แบบสแตติกสำหรับข้อมูลประเภท (ใช้โดย factory)
3. getter แบบเสมือนสำหรับการตรวจสอบประเภทในขณะทำงาน (ใช้โดยการดำเนินการแบบ polymorphic)

#### `addToRunTimeSelectionTable` Macro
```cpp
// What the macro actually does (simplified):
#define addToRunTimeSelectionTable(baseType, thisType, argNames)   \
    /* 1. Creates a constructor wrapper function */                \
    ::Foam::autoPtr<baseType> thisType::New argNames               \
    {                                                              \
        return autoPtr<baseType>(new thisType argNames);           \
    }                                                              \
    /* 2. Creates a static registrar object */                     \
    namespace {                                                    \
        ::Foam::baseType::argNames##ConstructorTable::             \
        add##thisType##ConstructorToTable                          \
        add##thisType##argNames##ConstructorToTable##_;            \
    }
```

มาโครนี้ทำงานสองการดำเนินการที่สำคัญ:
1. สร้างฟังก์ชันครอบคอนสตรักเตอร์แบบสแตติกที่ตรงกับลายเซ็นที่ factory คาดหวัง
2. สร้างออบเจกต์ registrar แบบสแตติกที่เพิ่มคอนสตรักเตอร์ไปยังตารางการเลือกแบบโกลบอล

#### ความมหัศจรรย์: Static Initialization
```cpp
// The registrar object's constructor adds the entry to the global table
// This happens BEFORE main() executes (static initialization)

namespace
{
    // Anonymous namespace - limits scope to this file
    class addmyTurbulenceModelConstructorToTable
    {
    public:
        addmyTurbulenceModelConstructorToTable()
        {
            turbulenceModel::dictionaryConstructorTable::insert
            (
                "myTurbulence",           // Key - matches dictionary type
                &myTurbulenceModel::New   // Function pointer to constructor
            );
        }
    };

    // Static object - constructor runs during program initialization
    static addmyTurbulenceModelConstructorToTable registermyTurbulenceModel;
}
```

ความยอดเยี่ยมของแนวทางนี้อยู่ในลำดับการเริ่มต้นแบบสแตติกของ C++ คอนสตรักเตอร์ของออบเจกต์ registrar ทำงานโดยอัตโนมัติเมื่อโปรแกรมเริ่ม ก่อนที่ `main()` จะถูกเรียก ซึ่งหมายความว่าตารางการเลือกจะเต็มไปด้วยข้อมูลก่อนที่โค้ดผู้ใช้จะพยายามสร้างออบเจกต์

### 4. กลไก: จาก Dictionary ถึงออบเจกต์

กระบวนการสร้างออบเจกต์ที่สมบูรณ์ตามกระแสที่ซับซ้อนที่แปลงการกำหนดค่าของผู้ใช้เป็นออบเจกต์ที่ทำงานได้:

```mermaid
graph TD
    A[Dictionary File<br/>type: "kEpsilon"] --> B[Factory Call<br/>turbulenceModel::New()]
    B --> C[Parse Dictionary<br/>Read type keyword]
    C --> D[Lookup in Selection Table<br/>Hash table search]
    D --> E{Found?}
    E -->|Yes| F[Call Registered Constructor<br/>kEpsilon::New(U, phi, transport)]
    E -->|No| G[Fatal Error with Available Types<br/>Built from table entries]
    F --> H[Dynamic Memory Allocation<br/>new kEpsilonModel(...)]
    H --> I[Wrap in autoPtr<br/>Smart pointer management]
    I --> J[Return to Caller<br/>Ready for use]
```

กลไกนี้ใช้ระบบการสร้างออบเจกต์แบบ type-safe ที่แข็งแกร่ง การแสดงทางคณิตศาสตร์ของการจับคู่ factory นี้สามารถแสดงเป็น:

Let:
- $\mathcal{D}$ เป็นพื้นที่การกำหนดค่า dictionary
- $\mathcal{T}$ เป็นพื้นที่ตัวระบุประเภท
- $\mathcal{C}$ เป็นพื้นที่ฟังก์ชันคอนสตรักเตอร์
- $\mathcal{O}$ เป็นพื้นที่ออบเจกต์ที่สร้างขึ้น

factory ใช้การจับคู่แบบประกอบ:

$$
F: \mathcal{D} \times \mathcal{T} \xrightarrow{\text{lookup}} \mathcal{C} \xrightarrow{\text{call}} \mathcal{O}
$$

โดยที่:
- $F(d, t) = c_t(d)$ จับคู่ dictionary $d$ และประเภท $t$ กับคอนสตรักเตอร์ $c_t$
- $c_t$ เป็นฟังก์ชันคอนสตรักเตอร์ที่ลงทะเบียนสำหรับประเภท $t$
- $d \in \mathcal{D}$ มีพารามิเตอร์เฉพาะโมเดล
- การจับคู่กลางใช้ hash table สำหรับเวลาค้นหา $O(1)$

**รายละเอียดการใช้งานที่สำคัญ:**

ตารางการเลือกใช้ `HashTable` สำหรับการค้นหาที่มีประสิทธิภาพ:
```cpp
// Simplified implementation (actual OpenFOAM code is more complex)
class ConstructorTable
:
    public HashTable<autoPtr<baseType> (*)(argNames)>
{
    // Inherits hash table functionality
    // Key: type name (word)
    // Value: function pointer to constructor
};
```

การจัดการข้อผิดพลาดเป็นแบบครอบคลุม โดยให้ข้อเสนอแนะที่เป็นประโยชน์เมื่อไม่พบประเภท:
```cpp
// Error message generation (simplified)
if (!constructorTable.found(typeName))
{
    FatalErrorInFunction
        << "Unknown " << baseType::typeName << " type '" << typeName << "'" << nl << nl
        << "Valid " << baseType::typeName << " types are:" << nl << nl
        << constructorTable.sortedToc()  // Lists all available types
        << exit(FatalError);
}
```

### 5. "Why": Factory Method Design Pattern

Factory Method Design Pattern เป็นหนึ่งใน Gang of Four design patterns ที่กำหนดอินเทอร์เฟซสำหรับการสร้างออบเจกต์ แต่ให้ subclasses ตัดสินใจว่าจะ instantiate คลาสใด การใช้งานของ OpenFOAM มีความซับซ้อนเป็นพิเศษเพราะมันแก้ไขความท้าทายหลายอย่างพร้อมกัน

**Traditional Factory Method**: การตัดสินใจว่าจะ instantiate คลาสใดทำโดย subclasses ผ่านการถ่ายทอด
**OpenFOAM's Innovation**: การตัดสินใจทำผ่านการกำหนดค่าในขณะทำงาน (dictionary files) ไม่ใช่การถ่ายทอดในเวลาคอมไพล์

แนวทางนี้ให้ประโยชน์ที่ไม่เหมือนใครในบริบท CFD:

1. **Dictionary-Driven Configuration**: ผู้ใช้สามารถเลือกและกำหนดค่าโมเดลฟิสิกส์ผ่านไฟล์ข้อความที่ใช้งานง่ายโดยไม่ต้องแก้ไขโค้ด:
```cpp
// constant/turbulenceProperties
simulationType  RAS;
RAS
{
    RASModel        kEpsilon;  // User selects model here
    turbulence      on;
    printCoeffs     on;
}
```

2. **Plugin Architecture**: โมเดลใหม่สามารถคอมไพล์เป็น shared libraries และโหลดแบบไดนามิก:
```bash
# Compile new turbulence model as shared library
wmake libso

# Add to case without recompiling solver
libs ("libCustomTurbulenceModels.so");
```

3. **Type Safety**: การตรวจสอบในเวลาคอมไพล์ทำให้มั่นใจว่าการใช้งานทั้งหมดตอบสนองอินเทอร์เฟซเดียวกัน:
```cpp
// Compile-time error if virtual functions not implemented
class myModel : public turbulenceModel
{
    // Compiler error: must implement k() and epsilon()
    virtual tmp<volScalarField> k() const override;  // Missing implementation
};
```

4. **Memory Safety**: `autoPtr` ทำให้การล้างข้อมูลเป็นไปโดยอัตโนมัติและป้องกันการรั่วไหลของหน่วยความจำ:
```cpp
{
    autoPtr<turbulenceModel> model = turbulenceModel::New(...);
    // Model automatically deleted when autoPtr goes out of scope
    // No need for manual delete
}
```

**Trade-offs and Considerations:**

factory pattern แนะนำความซับซ้อนและ overhead บางอย่าง:

**Runtime Overhead**: การเรียก virtual function และการค้นหา hash table เพิ่ม overhead ขั้นต่ำเมื่อเทียบกับ static dispatch ในการจำลอง CFD ที่ถูกครอบงำโดยการคำนวณตัวเลข  overhead นี้ไม่สำคัญ (<1% ของเวลาทำงานทั้งหมด)

**Complexity**: ระบบมาโครอาจสับสนสำหรับนักพัฒนาใหม่ อย่างไรก็ตาม รูปแบบมาตรฐานทำให้มันคาดเดาได้เมื่อเรียนรู้

**Debugging**: ข้อผิดพลาดที่จะถูกตรวจจับในเวลาคอมไพล์ในระบบ hardcoded ตอนนี้ปรากฏในขณะทำงาน OpenFOAM ลดผลกระทบนี้ด้วยข้อความผิดพลาดที่ครอบคลุมที่แสดงประเภทที่มีอยู่

**Compile-Time Dependencies**: factory pattern ลดการพึ่งพาในเวลาคอมไพล์เพราะ solver หลักไม่ต้องรู้เกี่ยวกับการใช้งานเฉพาะ ซึ่งปรับปรุงเวลา build สำหรับโค้ด CFD ขนาดใหญ่อย่างมาก

### 6. การใช้งาน & ตัวอย่างข้อผิดพลาด

#### ✅ การใช้งานที่ถูกต้อง: การเพิ่มโมเดลความปั่นป่วนใหม่

นี่คือตัวอย่างที่สมบูรณ์ของการใช้งานโมเดลความปั่นป่วนแบบกำหนดเอง:

```cpp
// myTurbulenceModel.H
class myTurbulenceModel
:
    public turbulenceModel
{
private:
    // Model-specific data members
    dimensionedScalar Cmu_;
    dimensionedScalar C1_;
    dimensionedScalar C2_;

public:
    TypeName("myTurbulence");  // MUST match dictionary type exactly

    // Constructor matching factory signature EXACTLY
    myTurbulenceModel
    (
        const volVectorField& U,
        const surfaceScalarField& phi,
        transportModel& transport,
        const word& propertiesName
    );

    // Implement required virtual functions
    virtual tmp<volScalarField> k() const override;
    virtual tmp<volScalarField> epsilon() const override;
    virtual void correct() override;

    // Destructor
    virtual ~myTurbulenceModel();
};
```

```cpp
// myTurbulenceModel.C
#include "myTurbulenceModel.H"

// Register in selection table - CRITICAL
addToRunTimeSelectionTable
(
    turbulenceModel,
    myTurbulenceModel,
    dictionary
);

myTurbulenceModel::myTurbulenceModel
(
    const volVectorField& U,
    const surfaceScalarField& phi,
    transportModel& transport,
    const word& propertiesName
)
:
    turbulenceModel(U, phi, transport, propertiesName),
    Cmu_("Cmu", dimless, 0.09),
    C1_("C1", dimless, 1.44),
    C2_("C2", dimless, 1.92)
{
    // Additional initialization
}

void myTurbulenceModel::correct()
{
    // Implementation of turbulence model equations
    // Transport equation for k:
    // ∂k/∂t + ∇·(Uk) = ∇·[(ν + νt/σk)∇k] + Pk - ε
    
    // Transport equation for ε:
    // ∂ε/∂t + ∇·(Uε) = ∇·[(ν + νt/σε)∇ε] + C1*ε/k*Pk - C2*ε²/k
    
    // Implementation details...
}

// Use in dictionary
// constant/turbulenceProperties
simulationType  RAS;
RAS
{
    RASModel        myTurbulence;  // Must match TypeName exactly
    turbulence      on;
    printCoeffs     on;
    
    // Model-specific coefficients
    Cmu             0.09;
    C1              1.44;
    C2              1.92;
}
```

#### ❌ ข้อผิดพลาดทั่วไปและการ Debugging

**Error 1: Missing `addToRunTimeSelectionTable`**
```cpp
// Error message:
--> FOAM FATAL ERROR:
Unknown turbulenceModel type 'myTurbulence'

Valid turbulenceModel types are:
kEpsilon
kOmegaSST
laminar
LESModel
SpalartAllmaras

// Root cause: Forgot to call addToRunTimeSelectionTable macro in .C file
// Solution: Add the macro immediately after including headers
addToRunTimeSelectionTable
(
    turbulenceModel,
    myTurbulenceModel,
    dictionary
);
```

**Error 2: TypeName Mismatch (Case Sensitivity)**
```cpp
// Dictionary file:
RASModel        MyTurbulence;  // Capital M

// Class definition:
TypeName("myTurbulence");  // lowercase m

// Error: Unknown turbulenceModel type 'MyTurbulence'
// Solution: Ensure exact case match
```

**Error 3: Wrong Constructor Signature**
```cpp
// WRONG: Missing const reference or wrong parameter order
myTurbulenceModel(volVectorField& U, surfaceScalarField& phi, ...) {}
myTurbulenceModel(const surfaceScalarField& phi, const volVectorField& U, ...) {}

// RIGHT: Must match factory declaration EXACTLY
myTurbulenceModel
(
    const volVectorField& U,
    const surfaceScalarField& phi,
    transportModel& transport,
    const word& propertiesName
);
```

**Error 4: Linker Errors**
```cpp
// Error:
undefined reference to `myTurbulenceModel::typeName'
undefined reference to `myTurbulenceModel::New(...)'

// Causes and solutions:
// 1. TypeName macro missing from .H file
// 2. addToRunTimeSelectionTable missing from .C file  
// 3. .C file not included in Make/files
// 4. Library not properly linked
```

**Error 5: Template Instantiation Issues**
```cpp
// Common with templated factory patterns
Error: explicit instantiation of 'myModel<volScalarField>' but no definition available

// Solution: Ensure template definitions are in .C files, not just .H files
template<class Type>
myModel<Type>::myModel(...)
{
    // Implementation must be visible at link time
}
```

### 7. สรุป Factory Pattern

Factory Pattern ใน OpenFOAM แสดงถึงการใช้งานที่ซับซ้อนของการสร้างออบเจกต์ที่เปิดใช้งานความยืดหยุ่นที่จำเป็นสำหรับการจำลองพลศาสตร์ของไหลเชิงคำนวณ มันแปลงสิ่งที่จะเป็นการตัดสินใจ hardcoded ในเวลาคอมไพล์เป็นการเลือกแบบกำหนดค่าผู้ใช้ในขณะทำงาน

**Factory Pattern ให้:**

1. **เครื่องจำหน่ายสำหรับโมเดลฟิสิกส์** - ผู้ใช้เลือกโมเดลผ่านการกำหนดค่า dictionary ที่เรียบง่าย
2. **การสร้างออบเจกต์โดยใช้ dictionary** - เปิดใช้งานการสร้างต้นแบบอย่างรวดเร็วโดยไม่ต้องคอมไพล์โค้ดใหม่  
3. **ระบบการลงทะเบียนแบบใช้มาโคร** - การจัดการการลงทะเบียนคอนสตรักเตอร์โดยอัตโนมัติ
4. **สถาปัตยกรรมพร้อมใช้งานปลั๊กอิน** - Shared libraries สามารถโหลดแบบไดนามิก
5. **การออกแบบที่ปลอดภัยต่อหน่วยความจำ** - Smart pointers ป้องกันการรั่วไหลของหน่วยความจำ

**ข้อกำหนดการใช้งานที่สำคัญ:**

- **ใช้ `TypeName("identifier")` ในการประกาศคลาส** - สร้างข้อมูลประเภทในขณะทำงาน
- **ใช้ `addToRunTimeSelectionTable` ในไฟล์ .C** - ลงทะเบียนคอนสตรักเตอร์กับ factory
- **ลายเซ็นคอนสตรักเตอร์ต้องตรงกันทั้งหมด** - ประเภทพารามิเตอร์และลำดับสำคัญมาก
- **`type` ของ dictionary ต้องตรงกับ `TypeName` ทั้งหมด** - การจับคู่สตริงตามตัวพิมพ์เล็ก-ใหญ่
- **การลงทะเบียนเกิดผ่าน static initialization** - อัตโนมัติก่อนการดำเนินการ `main()`

รูปแบบนี้เปิดให้ชุมชนการคำนวณทางวิทยาศาสตร์สามารถขยาย OpenFOAM โดยไม่ต้องแก้ไขโค้ดหลัก ส่งเสริมระบบนิเวศที่มีชีวิตของโมเดลฟิสิกส์แบบกำหนดเอง, รูปแบบตัวเลข และเครื่องมือจำลองที่สามารถแบ่งปันและปรับใช้งานได้ง่าย
