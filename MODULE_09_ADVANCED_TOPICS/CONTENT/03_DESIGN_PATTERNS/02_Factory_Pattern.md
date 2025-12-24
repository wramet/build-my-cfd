# 02 Factory Pattern: การสร้างออบเจกต์ขณะรันโปรแกรม (Runtime Object Creation)

**ปัญหา**: Solver ของ OpenFOAM ไม่ควรต้องรู้ล่วงหน้าว่าผู้ใช้จะเลือกใช้โมเดลความปั่นป่วน (Turbulence Model) ตัวไหน หรือเงื่อนไขขอบเขต (Boundary Condition) แบบใด

---

## 1. "Hook": เครื่องจำหน่าย CFD

จินตนาการเครื่องจำหน่ายสำหรับโมเดลฟิสิกส์ คุณแทรก dictionary (เหรียญ) ที่มี `type: "kEpsilon"` กดปุ่ม และออกมาเป็นโมเดลความปั่นป่วนที่สมบูรณ์ คุณไม่จำเป็นต้องรู้ว่ามันถูกประกอบขึ้นภายในอย่างไร การทำนายซ้อนที่สวยงามนี้แก้ไขความท้าทายพื้นฐานของ CFD อย่างหนึ่ง: **วิธีการสร้างออบเจกต์ที่ประเภทที่แน่นอนจะเป็นที่รู้จักเฉพาะในขณะทำงานจากข้อมูลที่ผู้ใช้ป้อน (dictionary files)**?

ในการเขียนโปรแกรม C++ แบบดั้งเดิม คุณอาจใช้ if-else chains ที่ต้องการการคอมไพล์ใหม่สำหรับโมเดลใหม่:

```cpp
// Hardcoded approach - requires recompilation for new models
// แนวทางการเขียนโค้ดแบบ hardcoded - ต้องคอมไพล์ใหม่สำหรับโมเดลใหม่
if (turbModelType == "kEpsilon") {
    return autoPtr<turbulenceModel>(new kEpsilonModel(...));
} else if (turbModelType == "kOmega") {
    return autoPtr<turbulenceModel>(new kOmegaModel(...));
} // Must modify this file for each new model
```

**คำอธิบาย:**
- **ที่มา (Source):** แนวคิดเบื้องต้นจาก C++ programming fundamentals
- **คำอธิบาย (Explanation):** โค้ดตัวอย่างนี้แสดงแนวทางแบบดั้งเดิมที่ไม่ยืดหยุ่น โดยใช้ if-else chains ในการตรวจสอบประเภทของโมเดลความปั่นป่วน ซึ่งทำให้ต้องคอมไพล์โค้ดใหม่ทุกครั้งที่เพิ่มโมเดลใหม่
- **แนวคิดสำคัญ (Key Concepts):**
  - Hardcoded type checking
  - Compilation coupling
  - If-else conditional chains
  - Pointer management with autoPtr

โซลูชันของ OpenFOAM ใช้ **runtime selection tables** ที่เปิดใช้งานสถาปัตยกรรมปลั๊กอินจริง ซึ่งหมายความว่าโมเดลฟิสิกส์ใหม่สามารถคอมไพล์แยกกันและค้นพบโดยอัตโนมัติในขณะทำงาน เหมือนกับการเพิ่มน้ำอัดลมใหม่ในเครื่องจำหน่ายโดยไม่ต้องออกแบบเครื่องทั้งหมดใหม่

Factory pattern มีความสำคัญเป็นพิเศษในการจำลอง CFD ที่ผู้ใช้มักจะทดลองกับโมเดลความปั่นป่วนที่แตกต่างกัน, เงื่อนไขขอบเขต, รูปแบบตัวเลข และโมเดลฟิสิกส์ โดยไม่มี pattern นี้ ผู้ใช้จะต้องคอมไพล์ solver ทั้งหมดใหม่เพียงเพื่อเปลี่ยนจากโมเดล $k-\epsilon$ เป็นโมเดล $k-\omega$

---

## 2. แบบแผน: อินเทอร์เฟซนามธรรมและมาโคร

การแยกอินเทอร์เฟซจากการใช้งานตามหลักการออกแบบเชิงวัตถุที่ให้ข้อดีหลายประการสำหรับการคำนวณทางวิทยาศาสตร์:

### ประโยชน์ของการแยก Interface

**Extensibility**: โมเดลความปั่นป่วนใหม่สามารถเพิ่มได้โดยไม่ต้องแก้ไขโค้ด solver หลัก นักวิจัย CFD สามารถพัฒนาโมเดลความปั่นป่วนแบบกำหนดเองเป็นไลบรารีแยกต่างหากและวางลงในการติดตั้ง OpenFOAM

**Maintainability**: การแยกความกังวลอย่างชัดเจนหมายความว่าตรรกะ solver ยังคงเป็นอิสระจากการใช้งานโมเดลเฉพาะ ซึ่งทำให้การ debug ง่ายขึ้นและอนุญาตให้พัฒนาส่วนประกอบโมเดลที่แตกต่างกันได้พร้อมกัน

**Testability**: อินเทอร์เฟซสามารถจำลองสำหรับการทดสอบหน่วย ทำให้สามารถทดสอบอัลกอริทึม solver อย่างครอบคลุมโดยไม่ต้องการโมเดลฟิสิกส์ที่ซับซ้อน

### องค์ประกอบไวยากรณ์หลัก

องค์ประกอบไวยากรณ์หลักทำงานร่วมกันเพื่อสร้างสถาปัตยกรรมที่ยืดหยุ่นนี้:

```cpp
// 1. Abstract base class with pure virtual functions
// 1. คลาสพื้นฐานแบบนามธรรมที่มีฟังก์ชันเสมือนแบบบริสุทธิ์
class turbulenceModel
{
public:
    // Runtime type information - enables identification
    // ข้อมูลประเภทขณะทำงาน - ช่วยให้สามารถระบุประเภทได้
    TypeName("turbulenceModel");

    // Pure virtual interface - enforces implementation requirements
    // อินเทอร์เฟซเสมือนแบบบริสุทธิ์ - บังคับให้มีการใช้งาน
    virtual tmp<volScalarField> k() const = 0;
    virtual tmp<volScalarField> epsilon() const = 0;
    virtual void correct() = 0;

    // Factory method (static) - main entry point for object creation
    // เมธอด factory (แบบสแตติก) - จุดเริ่มต้นหลักในการสร้างออบเจกต์
    static autoPtr<turbulenceModel> New
    (
        const volVectorField& U,
        const surfaceScalarField& phi,
        transportModel& transport,
        const word& propertiesName
    );

    // Virtual destructor - ensures proper cleanup
    // ดีสตรักเตอร์เสมือน - รับประกันการทำความสะอาดที่เหมาะสม
    virtual ~turbulenceModel() {}
};

// 2. Runtime selection table declaration (header)
// 2. การประกาศตารางการเลือกขณะทำงาน (header file)
declareRunTimeSelectionTable
(
    autoPtr,                // Return type - smart pointer for memory management
                            // ประเภทการคืนค่า - smart pointer สำหรับจัดการหน่วยความจำ
    turbulenceModel,        // Base class name
                            // ชื่อคลาสพื้นฐาน
    dictionary,            // Constructor parameter types...
                            // ประเภทพารามิเตอร์คอนสตรักเตอร์...
    (const volVectorField& U, const surfaceScalarField& phi, transportModel& transport, const word& propertiesName)
);

// 3. Runtime selection table definition (source)
// 3. การนิยามตารางการเลือกขณะทำงาน (source file)
defineRunTimeSelectionTable(turbulenceModel, dictionary,
    (const volVectorField& U, const surfaceScalarField& phi, transportModel& transport, const word& propertiesName));
```

**คำอธิบาย:**
- **ที่มา (Source):** โครงสร้างพื้นฐานของ Factory Pattern ใน OpenFOAM จาก turbulence model architecture
- **คำอธิบาย (Explanation):** โค้ดตัวอย่างนี้แสดงองค์ประกอบหลักสามส่วนของระบบ Factory: (1) คลาสพื้นฐานแบบนามธรรมที่กำหนดอินเทอร์เฟซ, (2) มาโครสำหรับประกาศตารางการเลือกขณะทำงานในไฟล์ header, และ (3) การนิยามตารางในไฟล์ source
- **แนวคิดสำคัญ (Key Concepts):**
  - Abstract base class design
  - Pure virtual functions
  - Runtime type information (RTTI)
  - Smart pointer management (autoPtr)
  - Runtime selection tables
  - Factory method pattern

**ความสำคัญของ `tmp<volScalarField>`**: ประเภทการคืนค่านี้เป็นสิ่งสำคัญเป็นพิเศษในกลยุทธ์การจัดการหน่วยความจำของ OpenFOAM มันใช้การนับการอ้างอิงเพื่อจัดการหน่วยความจำฟิลด์โดยอัตโนมัติและหลีกเลี่ยงการคัดลอกที่ไม่จำเป็น ซึ่งเป็นสิ่งสำคัญสำหรับประสิทธิภาพในการจำลอง CFD ขนาดใหญ่

---

## 3. กลไกภายใน: `New()` Selector และมาโคร

ความมหัศจรรย์ของ factory pattern อยู่ในระบบมาโครที่ซับซ้อนของ OpenFOAM ที่ทำให้การลงทะเบียนออบเจกต์เป็นไปโดยอัตโนมัติ มาตรวจสอบแต่ละส่วนประกอบ:

### `TypeName` Macro

```cpp
// Expands to static member functions for type identification
// ขยายเป็นฟังก์ชันสมาชิกแบบสแตติกสำหรับระบุประเภท
#define TypeName(TypeNameString)                                    \
    static const ::Foam::word typeName;                            \
    static const ::Foam::word& type() { return typeName; }         \
    virtual const ::Foam::word& type() const { return typeName; }
```

**คำอธิบาย:**
- **ที่มา (Source):** OpenFOAM macro definitions จาก src/OpenFOAM/macros/macros.H
- **คำอธิบาย (Explanation):** มาโคร `TypeName` สร้างฟังก์ชันสมาชิกแบบสแตติกสามฟังก์ชันสำหรับการระบุประเภทขณะทำงาน: ตัวแปรสตริงแบบสแตติกสำหรับเก็บชื่อประเภท, getter แบบสแตติกสำหรับ factory, และ getter เสมือนสำหรับ polymorphic operations
- **แนวคิดสำคัญ (Key Concepts):**
  - Macro expansion
  - Static member variables
  - Runtime type identification
  - Virtual function overloading

มาโครนี้สร้างฟังก์ชันที่จำเป็นสามฟังก์ชัน:

1. **ที่เก็บข้อมูลสตริงประเภทแบบสแตติก** - เก็บชื่อประเภทของคลาส
2. **Getter แบบสแตติกสำหรับข้อมูลประเภท** - ใช้โดย factory
3. **Getter แบบเสมือนสำหรับการตรวจสอบประเภทในขณะทำงาน** - ใช้โดยการดำเนินการแบบ polymorphic

### `addToRunTimeSelectionTable` Macro

```cpp
// What the macro actually does (simplified):
// สิ่งที่มาโครทำจริงๆ (แบบลดความซับซ้อน):
#define addToRunTimeSelectionTable(baseType, thisType, argNames)   \
    /* 1. Creates a constructor wrapper function */                \
    /* 1. สร้างฟังก์ชันครอบคอนสตรักเตอร์ */                          \
    ::Foam::autoPtr<baseType> thisType::New argNames               \
    {                                                              \
        return autoPtr<baseType>(new thisType argNames);           \
    }                                                              \
    /* 2. Creates a static registrar object */                     \
    /* 2. สร้างออบเจกต์ registrar แบบสแตติก */                        \
    namespace {                                                    \
        ::Foam::baseType::argNames##ConstructorTable::             \
        add##thisType##ConstructorToTable                          \
        add##thisType##argNames##ConstructorToTable##_;            \
    }
```

**คำอธิบาย:**
- **ที่มา (Source):** OpenFOAM runtime selection macros จาก src/OpenFOAM/db/runTimeSelectionTables/addToRunTimeSelectionTable.H
- **คำอธิบาย (Explanation):** มาโครนี้ทำงานสองส่วนหลัก: (1) สร้างฟังก์ชันครอบคอนสตรักเตอร์แบบสแตติกที่ตรงกับลายเซ็นที่ factory คาดหวัง และ (2) สร้างออบเจกต์ registrar แบบสแตติกที่เพิ่มคอนสตรักเตอร์เข้าไปในตารางการเลือกแบบโกลบอล
- **แนวคิดสำคัญ (Key Concepts):**
  - Macro metaprogramming
  - Constructor wrapping
  - Static initialization
  - Namespace scoping
  - Template-based registration

มาโครนี้ทำงานสองการดำเนินการที่สำคัญ:

1. สร้างฟังก์ชันครอบคอนสตรักเตอร์แบบสแตติกที่ตรงกับลายเซ็นที่ factory คาดหวัง
2. สร้างออบเจกต์ registrar แบบสแตติกที่เพิ่มคอนสตรักเตอร์ไปยังตารางการเลือกแบบโกลบอล

### ความมหัศจรรย์: Static Initialization

```cpp
// The registrar object's constructor adds the entry to the global table
// This happens BEFORE main() executes (static initialization)
// คอนสตรักเตอร์ของออบเจกต์ registrar เพิ่มรายการเข้าไปในตารางโกลบอล
// สิ่งนี้เกิดขึ้นก่อนที่ main() จะทำงาน (static initialization)

namespace
{
    // Anonymous namespace - limits scope to this file
    // Namespace ไม่มีชื่อ - จำกัดขอบเขตเฉพาะไฟล์นี้
    class addmyTurbulenceModelConstructorToTable
    {
    public:
        addmyTurbulenceModelConstructorToTable()
        {
            turbulenceModel::dictionaryConstructorTable::insert
            (
                "myTurbulence",           // Key - matches dictionary type
                                        // คีย์ - ตรงกับประเภทใน dictionary
                &myTurbulenceModel::New   // Function pointer to constructor
                                        // พอยน์เตอร์ฟังก์ชันไปยังคอนสตรักเตอร์
            );
        }
    };

    // Static object - constructor runs during program initialization
    // ออบเจกต์แบบสแตติก - คอนสตรักเตอร์ทำงานระหว่างการเริ่มต้นโปรแกรม
    static addmyTurbulenceModelConstructorToTable registermyTurbulenceModel;
}
```

**คำอธิบาย:**
- **ที่มา (Source):** Pattern ที่ใช้ใน OpenFOAM สำหรับการลงทะเบียนโมเดล เช่น dragModel, virtualMassModel ใน multiphaseEulerFoam
- **คำอธิบาย (Explanation):** โค้ดนี้แสดงกลไกการลงทะเบียนอัตโนมัติผ่าน static initialization ออบเจกต์ registrar ถูกสร้างขึ้นก่อนที่ main() จะเริ่มทำงาน และคอนสตรักเตอร์ของมันเพิ่มฟังก์ชันคอนสตรักเตอร์เข้าไปในตารางแบบโกลบอล
- **แนวคิดสำคัญ (Key Concepts):**
  - Anonymous namespace
  - Static object initialization
  - Function pointers
  - Constructor side effects
  - Hash table insertion

ความยอดเยี่ยมของแนวทางนี้อยู่ใน **ลำดับการเริ่มต้นแบบสแตติกของ C++** คอนสตรักเตอร์ของออบเจกต์ registrar ทำงานโดยอัตโนมัติเมื่อโปรแกรมเริ่ม ก่อนที่ `main()` จะถูกเรียก ซึ่งหมายความว่าตารางการเลือกจะเต็มไปด้วยข้อมูลก่อนที่โค้ดผู้ใช้จะพยายามสร้างออบเจกต์

---

## 4. กลไก: จาก Dictionary ถึงออบเจกต์

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
> **Figure 1:** แผนผังแสดงกระบวนการทำงานของ Factory Pattern ใน OpenFOAM เริ่มต้นจากการอ่านค่าจาก Dictionary เพื่อค้นหาประเภทของโมเดลที่ต้องการในตารางการเลือก (Selection Table) หากพบประเภทที่ถูกต้อง ระบบจะเรียกคอนสตรักเตอร์ที่ลงทะเบียนไว้เพื่อสร้างออบเจกต์จริงผ่านการจัดสรรหน่วยความจำแบบไดนามิก และส่งคืนในรูปแบบ Smart Pointer (`autoPtr`) เพื่อความปลอดภัยในการจัดการหน่วยความจำ

### การแสดงทางคณิตศาสตร์

กลไกนี้ใช้ระบบการสร้างออบเจกต์แบบ type-safe ที่แข็งแกร่ง การแสดงทางคณิตศาสตร์ของการจับคู่ factory นี้สามารถแสดงเป็น:

**กำหนด:**
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

### รายละเอียดการใช้งานที่สำคัญ

ตารางการเลือกใช้ `HashTable` สำหรับการค้นหาที่มีประสิทธิภาพ:

```cpp
// Simplified implementation (actual OpenFOAM code is more complex)
// การใช้งานแบบลดความซับซ้อน (โค้ด OpenFOAM จริงซับซ้อนกว่านี้)
class ConstructorTable
:
    public HashTable<autoPtr<baseType> (*)(argNames)>
{
    // Inherits hash table functionality
    // สืบทอดฟังก์ชันการทำงานของ hash table
    // Key: type name (word)
    //     คีย์: ชื่อประเภท (word)
    // Value: function pointer to constructor
    //       ค่า: พอยน์เตอร์ฟังก์ชันไปยังคอนสตรักเตอร์
};
```

**คำอธิบาย:**
- **ที่มา (Source):** HashTable template class จาก src/OpenFOAM/containers/HashTables/HashTable/HashTable.H
- **คำอธิบาย (Explanation):** ตารางการเลือกขณะทำงานใช้ HashTable เพื่อจัดเก็บการจับคู่ระหว่างชื่อประเภท (key) และพอยน์เตอร์ฟังก์ชันคอนสตรักเตอร์ (value) ซึ่งให้เวลาค้นหา O(1)
- **แนวคิดสำคัญ (Key Concepts):**
  - Hash table data structure
  - Function pointer storage
  - Template inheritance
  - Key-value mapping
  - O(1) lookup complexity

การจัดการข้อผิดพลาดเป็นแบบครอบคลุม โดยให้ข้อเสนอแนะที่เป็นประโยชน์เมื่อไม่พบประเภท:

```cpp
// Error message generation (simplified)
// การสร้างข้อความแจ้งข้อผิดพลาด (แบบลดความซับซ้อน)
// Error message generation (simplified)
// การสร้างข้อความแจ้งข้อผิดพลาด (แบบลดความซับซ้อน)
if (!constructorTable.found(typeName))
{
    FatalErrorInFunction
        << "Unknown " << baseType::typeName << " type '" << typeName << "'" << nl << nl
        << "Valid " << baseType::typeName << " types are:" << nl << nl
        << constructorTable.sortedToc()  // Lists all available types
                                        // แสดงรายการประเภทที่มีอยู่ทั้งหมด
        << exit(FatalError);
}
```

**คำอธิบาย:**
- **ที่มา (Source):** Error handling pattern ใน OpenFOAM runtime selection mechanisms
- **คำอธิบาย (Explanation):** ตัวอย่างนี้แสดงการจัดการข้อผิดพลาดเมื่อไม่พบประเภทที่ร้องขอ โดยระบบจะแสดงรายการประเภทที่มีอยู่ทั้งหมดจากตารางการเลือก เพื่อช่วยให้ผู้ใช้ตรวจสอบและแก้ไขได้
- **แนวคิดสำคัญ (Key Concepts):**
  - Error handling
  - User feedback
  - Table of contents generation
  - Fatal error system
  - Diagnostic information

---

## 5. "Why": Factory Method Design Pattern

Factory Method Design Pattern เป็นหนึ่งใน Gang of Four design patterns ที่กำหนดอินเทอร์เฟซสำหรับการสร้างออบเจกต์ แต่ให้ subclasses ตัดสินใจว่าจะ instantiate คลาสใด การใช้งานของ OpenFOAM มีความซับซ้อนเป็นพิเศษเพราะมันแก้ไขความท้าทายหลายอย่างพร้อมกัน

### Factory Method แบบดั้งเดิม vs OpenFOAM

**Traditional Factory Method**: การตัดสินใจว่าจะ instantiate คลาสใดทำโดย subclasses ผ่านการถ่ายทอด

**OpenFOAM's Innovation**: การตัดสินใจทำผ่านการกำหนดค่าในขณะทำงาน (dictionary files) ไม่ใช่การถ่ายทอดในเวลาคอมไพล์

### ประโยชน์ที่ไม่เหมือนใครในบริบท CFD

**1. Dictionary-Driven Configuration**: ผู้ใช้สามารถเลือกและกำหนดค่าโมเดลฟิสิกส์ผ่านไฟล์ข้อความที่ใช้งานง่ายโดยไม่ต้องแก้ไขโค้ด

```cpp
// constant/turbulenceProperties
// constant/turbulenceProperties
simulationType  RAS;
RAS
{
    RASModel        kEpsilon;  // User selects model here
                            // ผู้ใช้เลือกโมเดลที่นี่
    turbulence      on;
    printCoeffs     on;
}
```

**คำอธิบาย:**
- **ที่มา (Source):** OpenFOAM dictionary file format สำหรับ turbulence model configuration
- **คำอธิบาย (Explanation):** ตัวอย่างไฟล์ dictionary แสดงการเลือกโมเดลความปั่นป่วน kEpsilon ผ่านพารามิเตอร์ RASModel ซึ่งอนุญาตให้ผู้ใช้เปลี่ยนโมเดลโดยไม่ต้องคอมไพล์โค้ดใหม่
- **แนวคิดสำคัญ (Key Concepts):**
  - Dictionary-based configuration
  - Runtime model selection
  - Text-based parameter input
  - User-friendly interface

**2. Plugin Architecture**: โมเดลใหม่สามารถคอมไพล์เป็น shared libraries และโหลดแบบไดนามิก

```bash
# Compile new turbulence model as shared library
# คอมไพล์โมเดลความปั่นป่วนใหม่เป็น shared library
wmake libso

# Add to case without recompiling solver
# เพิ่มใน case โดยไม่ต้องคอมไพล์ solver ใหม่
libs ("libCustomTurbulenceModels.so");
```

**คำอธิบาย:**
- **ที่มา (Source):** OpenFOAM shared library compilation และ dynamic loading mechanism
- **คำอธิบาย (Explanation):** คำสั่ง wmake libso สร้าง shared library จากโค้ดโมเดลใหม่ ซึ่งสามารถโหลดแบบไดนามิกผ่านพารามิเตอร์ libs ในไฟล์ controlDict โดยไม่ต้องคอมไพล์ solver ใหม่
- **แนวคิดสำคัญ (Key Concepts):**
  - Shared library compilation
  - Dynamic loading
  - Plugin architecture
  - wmake build system

**3. Type Safety**: การตรวจสอบในเวลาคอมไพล์ทำให้มั่นใจว่าการใช้งานทั้งหมดตอบสนองอินเทอร์เฟซเดียวกัน

```cpp
// Compile-time error if virtual functions not implemented
// ข้อผิดพลาดในการคอมไพล์หากไม่ได้ใช้งานฟังก์ชันเสมือน
class myModel : public turbulenceModel
{
    // Compiler error: must implement k() and epsilon()
    // ข้อผิดพลาดของคอมไพล์เลอร์: ต้องใช้งาน k() และ epsilon()
    virtual tmp<volScalarField> k() const override;  // Missing implementation
                                                     // ยังไม่มีการใช้งาน
};
```

**คำอธิบาย:**
- **ที่มา (Source):** C++ pure virtual function enforcement mechanism
- **คำอธิบาย (Explanation):** ตัวอย่างแสดงการบังคับใช้อินเทอร์เฟซผ่าน pure virtual functions คอมไพล์เลอร์จะแจ้งข้อผิดพลาดหากคลาส derived ไม่ได้ใช้งานฟังก์ชันทั้งหมดที่กำหนดในคลาสพื้นฐาน
- **แนวคิดสำคัญ (Key Concepts):**
  - Compile-time type checking
  - Pure virtual functions
  - Interface enforcement
  - Override keyword

**4. Memory Safety**: `autoPtr` ทำให้การล้างข้อมูลเป็นไปโดยอัตโนมัติและป้องกันการรั่วไหลของหน่วยความจำ

```cpp
{
    // autoPtr manages memory automatically
    // autoPtr จัดการหน่วยความจำอัตโนมัติ
    autoPtr<turbulenceModel> model = turbulenceModel::New(...);
    // Model automatically deleted when autoPtr goes out of scope
    // โมเดลถูกลบโดยอัตโนมัติเมื่อ autoPtr ออกนอกขอบเขต
    // No need for manual delete
    // ไม่ต้องลบด้วยตนเอง
}
```

**คำอธิบาย:**
- **ที่มา (Source):** autoPtr smart pointer implementation ใน src/OpenFOAM/memory/autoPtr/autoPtr.H
- **คำอธิบาย (Explanation):** autoPtr เป็น smart pointer ที่จัดการหน่วยความจำอัตโนมัติ เมื่อออบเจกต์ autoPtr ออกนอกขอบเขต คอนสตรักเตอร์จะถูกเรียกโดยอัตโนมัติ ป้องกันการรั่วไหลของหน่วยความจำ
- **แนวคิดสำคัญ (Key Concepts):**
  - Smart pointer pattern
  - RAII (Resource Acquisition Is Initialization)
  - Automatic memory management
  - Scope-based cleanup

### Trade-offs และข้อควรพิจารณา

factory pattern แนะนำความซับซ้อนและ overhead บางอย่าง:

| ข้อควรพิจารณา | คำอธิบาย |
|-----------------|------------|
| **Runtime Overhead** | การเรียก virtual function และการค้นหา hash table เพิ่ม overhead ขั้นต่ำเมื่อเทียบกับ static dispatch ในการจำลอง CFD ที่ถูกครอบงำโดยการคำนวณตัวเลข overhead นี้ไม่สำคัญ (<1% ของเวลาทำงานทั้งหมด) |
| **Complexity** | ระบบมาโครอาจสับสนสำหรับนักพัฒนาใหม่ อย่างไรก็ตาม รูปแบบมาตรฐานทำให้มันคาดเดาได้เมื่อเรียนรู้ |
| **Debugging** | ข้อผิดพลาดที่จะถูกตรวจจับในเวลาคอมไพล์ในระบบ hardcoded ตอนนี้ปรากฏในขณะทำงาน OpenFOAM ลดผลกระทบนี้ด้วยข้อความผิดพลาดที่ครอบคลุมที่แสดงประเภทที่มีอยู่ |
| **Compile-Time Dependencies** | factory pattern ลดการพึ่งพาในเวลาคอมไพล์เพราะ solver หลักไม่ต้องรู้เกี่ยวกับการใช้งานเฉพาะ ซึ่งปรับปรุงเวลา build สำหรับโค้ด CFD ขนาดใหญ่อย่างมาก |

---

## 6. การใช้งาน & ตัวอย่างข้อผิดพลาด

### ✅ การใช้งานที่ถูกต้อง: การเพิ่มโมเดลความปั่นป่วนใหม่

นี่คือตัวอย่างที่สมบูรณ์ของการใช้งานโมเดลความปั่นป่วนแบบกำหนดเอง:

```cpp
// myTurbulenceModel.H
// myTurbulenceModel.H
class myTurbulenceModel
:
    public turbulenceModel
{
private:
    // Model-specific data members
    // สมาชิกข้อมูลเฉพาะโมเดล
    dimensionedScalar Cmu_;
    dimensionedScalar C1_;
    dimensionedScalar C2_;

public:
    // TypeName MUST match dictionary type exactly
    // TypeName ต้องตรงกับประเภทใน dictionary ทุกประการ
    TypeName("myTurbulence");

    // Constructor matching factory signature EXACTLY
    // คอนสตรักเตอร์ต้องตรงกับลายเซ็นของ factory ทุกประการ
    myTurbulenceModel
    (
        const volVectorField& U,
        const surfaceScalarField& phi,
        transportModel& transport,
        const word& propertiesName
    );

    // Implement required virtual functions
    // ใช้งานฟังก์ชันเสมือนที่จำเป็น
    virtual tmp<volScalarField> k() const override;
    virtual tmp<volScalarField> epsilon() const override;
    virtual void correct() override;

    // Destructor
    // ดีสตรักเตอร์
    virtual ~myTurbulenceModel();
};
```

**คำอธิบาย:**
- **ที่มา (Source):** Custom turbulence model template structure จาก OpenFOAM documentation
- **คำอธิบาย (Explanation):** ไฟล์ header นี้กำหนดคลาสโมเดลความปั่นป่วนแบบกำหนดเองที่สืบทอดจาก turbulenceModel โดยมีสมาชิกข้อมูลเฉพาะโมเดล (Cmu_, C1_, C2_) และใช้งานฟังก์ชันเสมือนที่จำเป็น
- **แนวคิดสำคัญ (Key Concepts):**
  - Class inheritance
  - Dimensioned scalar types
  - Virtual function implementation
  - TypeName registration
  - Constructor signature matching

```cpp
// myTurbulenceModel.C
#include "myTurbulenceModel.H"

// Register in selection table - CRITICAL
// ลงทะเบียนในตารางการเลือก - สำคัญมาก
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
    // การเริ่มต้นเพิ่มเติม
}

void myTurbulenceModel::correct()
{
    // Implementation of turbulence model equations
    // การใช้งานสมการโมเดลความปั่นป่วน
    // Transport equation for k:
    // ∂k/∂t + ∇·(Uk) = ∇·[(ν + νt/σk)∇k] + Pk - ε

    // Transport equation for ε:
    // ∂ε/∂t + ∇·(Uε) = ∇·[(ν + νt/σε)∇ε] + C1*ε/k*Pk - C2*ε²/k

    // Implementation details...
    // รายละเอียดการใช้งาน...
}

// Use in dictionary
// constant/turbulenceProperties
simulationType  RAS;
RAS
{
    RASModel        myTurbulence;  // Must match TypeName exactly
                                    // ต้องตรงกับ TypeName ทุกประการ
    turbulence      on;
    printCoeffs     on;

    // Model-specific coefficients
    // สัมประสิทธิ์เฉพาะโมเดล
    Cmu             0.09;
    C1              1.44;
    C2              1.92;
}
```

**คำอธิบาย:**
- **ที่มา (Source):** Runtime selection table registration pattern ใน OpenFOAM turbulence models
- **คำอธิบาย (Explanation):** ไฟล์ implementation นี้แสดงการลงทะเบียนโมเดลในตารางการเลือกขณะทำงานด้วยมาโคร addToRunTimeSelectionTable การเริ่มต้นคอนสตรักเตอร์ และการใช้งานเมธอด correct() สำหรับแก้สมการความปั่นป่วน
- **แนวคิดสำคัญ (Key Concepts):**
  - addToRunTimeSelectionTable macro
  - Constructor initialization list
  - DimensionedScalar initialization
  - Transport equation implementation
  - Dictionary configuration matching

### ❌ ข้อผิดพลาดทั่วไปและการ Debugging

**Error 1: Missing `addToRunTimeSelectionTable`**

```cpp
// Error message:
// ข้อความแจ้งข้อผิดพลาด:
--> FOAM FATAL ERROR:
Unknown turbulenceModel type 'myTurbulence'

Valid turbulenceModel types are:
kEpsilon
kOmegaSST
laminar
LESModel
SpalartAllmaras

// Root cause: Forgot to call addToRunTimeSelectionTable macro in .C file
// สาเหตุ: ลืมเรียกมาโคร addToRunTimeSelectionTable ในไฟล์ .C
// Solution: Add the macro immediately after including headers
// วิธีแก้: เพิ่มมาโครทันทีหลังจาก include headers
addToRunTimeSelectionTable
(
    turbulenceModel,
    myTurbulenceModel,
    dictionary
);
```

**คำอธิบาย:**
- **ที่มา (Source):** Common runtime selection error pattern ใน OpenFOAM
- **คำอธิบาย (Explanation):** ข้อผิดพลาดนี้เกิดขึ้นเมื่อไม่ได้เรียกมาโคร addToRunTimeSelectionTable ในไฟล์ .C ทำให้โมเดลไม่ได้ลงทะเบียนในตารางการเลือก วิธีแก้คือเพิ่มมาโครทันทีหลังจาก include headers
- **แนวคิดสำคัญ (Key Concepts):**
  - Runtime table registration
  - Macro placement
  - Error message interpretation
  - Type discovery mechanism

**Error 2: TypeName Mismatch (Case Sensitivity)**

```cpp
// Dictionary file:
// ไฟล์ dictionary:
RASModel        MyTurbulence;  // Capital M

// Class definition:
// การนิยามคลาส:
TypeName("myTurbulence");  // lowercase m

// Error: Unknown turbulenceModel type 'MyTurbulence'
// ข้อผิดพลาด: ไม่พบประเภท turbulenceModel 'MyTurbulence'
// Solution: Ensure exact case match
// วิธีแก้: ต้องแน่ใจว่าตรงกันทั้งตัวพิมพ์ใหญ่-เล็ก
```

**คำอธิบาย:**
- **ที่มา (Source):** String matching case sensitivity ใน OpenFOAM runtime selection
- **คำอธิบาย (Explanation):** ข้อผิดพลาดเกิดจากการไม่ตรงกันของชื่อประเภทระหว่างไฟล์ dictionary (MyTurbulence) และการนิยามคลาส (myTurbulence) โดย TypeName ตรงกับตัวพิมพ์เล็ก-ใหญ่ทุกประการ
- **แนวคิดสำคัญ (Key Concepts):**
  - Case-sensitive string matching
  - TypeName consistency
  - Dictionary configuration
  - Type registration keys

**Error 3: Wrong Constructor Signature**

```cpp
// WRONG: Missing const reference or wrong parameter order
// ผิด: ขาด const reference หรือลำดับพารามิเตอร์ผิด
myTurbulenceModel(volVectorField& U, surfaceScalarField& phi, ...) {}
myTurbulenceModel(const surfaceScalarField& phi, const volVectorField& U, ...) {}

// RIGHT: Must match factory declaration EXACTLY
// ถูกต้อง: ต้องตรงกับการประกาศของ factory ทุกประการ
myTurbulenceModel
(
    const volVectorField& U,
    const surfaceScalarField& phi,
    transportModel& transport,
    const word& propertiesName
);
```

**คำอธิบาย:**
- **ที่มา (Source):** Constructor signature requirements ใน OpenFOAM runtime selection
- **คำอธิบาย (Explanation):** ลายเซ็นคอนสตรักเตอร์ต้องตรงกับการประกาศของ factory ทุกประการ ทั้งประเภทพารามิเตอร์ คุณสมบัติ const/reference และลำดับของพารามิเตอร์
- **แนวคิดสำคัญ (Key Concepts):**
  - Function signature matching
  - Const correctness
  - Reference semantics
  - Parameter ordering

**Error 4: Linker Errors**

```cpp
// Error:
// ข้อผิดพลาด:
undefined reference to `myTurbulenceModel::typeName'
undefined reference to `myTurbulenceModel::New(...)'

// Causes and solutions:
// สาเหตุและวิธีแก้:
// 1. TypeName macro missing from .H file
//    ไม่มีมาโคร TypeName ในไฟล์ .H
// 2. addToRunTimeSelectionTable missing from .C file
//    ไม่มี addToRunTimeSelectionTable ในไฟล์ .C
// 3. .C file not included in Make/files
//    ไฟล์ .C ไม่ได้รวมอยู่ใน Make/files
// 4. Library not properly linked
//    ไลบรารีไม่ได้ลิงก์อย่างถูกต้อง
```

**คำอธิบาย:**
- **ที่มา (Source):** Common linking errors ใน OpenFOAM custom model development
- **คำอธิบาย (Explanation):** ข้อผิดพลาด linker นี้เกิดจากหลายสาเหตุ ได้แก่ การขาดมาโคร TypeName การขาดการลงทะเบียนในตาราง ไฟล์ .C ไม่ได้รวมใน Make/files หรือไลบรารีไม่ได้ลิงก์
- **แนวคิดสำคัญ (Key Concepts):**
  - Linker error diagnosis
  - Macro dependencies
  - Build system configuration
  - Library linking

**Error 5: Template Instantiation Issues**

```cpp
// Common with templated factory patterns
// เกิดขึ้นบ่อยกับรูปแบบ factory แบบเทมเพลต
Error: explicit instantiation of 'myModel<volScalarField>' but no definition available

// Solution: Ensure template definitions are in .C files, not just .H files
// วิธีแก้: ต้องแน่ใจว่าการนิยามเทมเพลตอยู่ในไฟล์ .C ไม่ใช่เฉพาะไฟล์ .H
template<class Type>
myModel<Type>::myModel(...)
{
    // Implementation must be visible at link time
    // การใช้งานต้องมองเห็นได้ในเวลาลิงก์
}
```

**คำอธิบาย:**
- **ที่มา (Source):** Template instantiation requirements ใน OpenFOAM generic programming
- **คำอธิบาย (Explanation):** ข้อผิดพลาดนี้เกิดขึ้นเมื่อมีการ instantiation เทมเพลตอย่างชัดเจน แต่ไม่มีการนิยาม วิธีแก้คือต้องแน่ใจว่าการนิยามเทมเพลตมีอยู่ในไฟล์ .C เพื่อให้มองเห็นได้ในเวลาลิงก์
- **แนวคิดสำคัญ (Key Concepts):**
  - Template instantiation
  - Link-time visibility
  - Explicit template declaration
  - Template definition placement

---

## 7. สรุป Factory Pattern

Factory Pattern ใน OpenFOAM แสดงถึงการใช้งานที่ซับซ้อนของการสร้างออบเจกต์ที่เปิดใช้งานความยืดหยุ่นที่จำเป็นสำหรับการจำลองพลศาสตร์ของไหลเชิงคำนวณ มันแปลงสิ่งที่จะเป็นการตัดสินใจ hardcoded ในเวลาคอมไพล์เป็นการเลือกแบบกำหนดค่าผู้ใช้ในขณะทำงาน

### Factory Pattern ให้:

1. **เครื่องจำหน่ายสำหรับโมเดลฟิสิกส์** - ผู้ใช้เลือกโมเดลผ่านการกำหนดค่า dictionary ที่เรียบง่าย
2. **การสร้างออบเจกต์โดยใช้ dictionary** - เปิดใช้งานการสร้างต้นแบบอย่างรวดเร็วโดยไม่ต้องคอมไพล์โค้ดใหม่
3. **ระบบการลงทะเบียนแบบใช้มาโคร** - การจัดการการลงทะเบียนคอนสตรักเตอร์โดยอัตโนมัติ
4. **สถาปัตยกรรมพร้อมใช้งานปลั๊กอิน** - Shared libraries สามารถโหลดแบบไดนามิก
5. **การออกแบบที่ปลอดภัยต่อหน่วยความจำ** - Smart pointers ป้องกันการรั่วไหลของหน่วยความจำ

### ข้อกำหนดการใช้งานที่สำคัญ:

- **ใช้ `TypeName("identifier")` ในการประกาศคลาส** - สร้างข้อมูลประเภทในขณะทำงาน
- **ใช้ `addToRunTimeSelectionTable` ในไฟล์ .C** - ลงทะเบียนคอนสตรักเตอร์กับ factory
- **ลายเซ็นคอนสตรักเตอร์ต้องตรงกันทั้งหมด** - ประเภทพารามิเตอร์และลำดับสำคัญมาก
- **`type` ของ dictionary ต้องตรงกับ `TypeName` ทั้งหมด** - การจับคู่สตริงตามตัวพิมพ์เล็ก-ใหญ่
- **การลงทะเบียนเกิดผ่าน static initialization** - อัตโนมัติก่อนการดำเนินการ `main()`

รูปแบบนี้เปิดให้ชุมชนการคำนวณทางวิทยาศาสตร์สามารถขยาย OpenFOAM โดยไม่ต้องแก้ไขโค้ดหลัก ส่งเสริมระบบนิเวศที่มีชีวิตของโมเดลฟิสิกส์แบบกำหนดเอง, รูปแบบตัวเลข และเครื่องมือจำลองที่สามารถแบ่งปันและปรับใช้งานได้ง่าย