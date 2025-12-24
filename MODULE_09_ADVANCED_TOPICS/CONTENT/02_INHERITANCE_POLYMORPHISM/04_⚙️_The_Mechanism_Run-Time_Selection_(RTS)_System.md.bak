# ⚙️ กลไก: ระบบ Run-Time Selection (RTS)

## Factory Pattern พร้อมการกำหนดค่าแบบ Dictionary-Driven

ระบบ RTS (Run-Time Selection) ของ OpenFOAM เป็นหนึ่งในดีไซน์แพทเทิร์นที่ซับซ้อนที่สุดในวิศวกรรมซอฟต์แวร์ CFD ระบบนี้ช่วยให้สามารถทำงาน polymorphism ในขณะทำงานได้โดยไม่ต้องพึ่งพาประเภทที่ถูก hard-code โดยใช้รูปแบบ Factory ร่วมกับการกำหนดค่าแบบ dictionary-driven กลไกนี้อนุญาตให้ CFD solvers สามารถสร้างอินสแตนซ์ของโมเดลฟิสิกส์ รูปแบบเชิงตัวเลข และเงื่อนไขขอบเขตที่แตกต่างกันได้โดยพิจารณาจากไฟล์ข้อความอินพุตเพียงอย่างเดียว ซึ่งสร้างกรอบการจำลองที่มีความยืดหยุ่นและขยายได้สูง

หลักการหลักทำงานผ่านกระบวนการ 3 ขั้นตอน:

1. **Dictionary Specification**: ผู้ใช้ระบุประเภทของโมเดลใน dictionary ข้อความ (โดยทั่วไปอยู่ในไดเรกทอรี `constant/` หรือ `system/`)
2. **Factory Registration**: คลาสโมเดลที่เป็นรูปธรรม register ตัวเองโดยอัตโนมัติในระหว่างการเริ่มต้นแบบ static
3. **Runtime Dispatch**: วิธีการ factory สร้างอินสแตนซ์ของคลาสที่เหมาะสมตามรายการใน dictionary

พิจารณาการจำลองการไหลแบบ multiphase ที่คุณสมบัติของเฟสถูกกำหนดในรูปแบบ dictionary:

```cpp
// Dictionary entry in constant/phaseProperties
water
{
    type            pure;           // Maps to purePhaseModel class
    rho             1000;           // Constructor parameter
    mu              0.001;           // Dynamic viscosity
    sigma           0.072;          // Surface tension
}

// Runtime creation - NO hardcoded type names!
autoPtr<phaseModel> waterPhase = phaseModel::New(waterDict, mesh);
```

แนวทางนี้ขจัดการพึ่งพาในเวลา compile ระหว่าง solvers และโมเดลเฉพาะ โมเดลใหม่สามารถเพิ่มเป็นไลบรารีแยกต่างหากได้โดยไม่ต้องคอมไพล์ core solver ใหม่ ทำให้มีความสามารถในการขยายแบบ plugin ซึ่งเป็นสิ่งสำคัญสำหรับแอปพลิเคชัน CFD ที่เน้นการวิจัย

## Macro Magic: `declareRunTimeSelectionTable`

ระบบ RTS พึ่งพา preprocessor macros ที่ซับซ้อนในการสร้างโครงสร้างพื้นฐาน factory โดยอัตโนมัติ Macro `declareRunTimeSelectionTable` สร้างโครงสร้างข้อมูลสถิติและฟังก์ชันสมาชิกที่จำเป็นสำหรับการเลือกใน runtime:

```cpp
// In waveModel.H - declares factory infrastructure
declareRunTimeSelectionTable
(
    autoPtr,                // Return type: smart pointer for exclusive ownership
    waveModel,              // Base class name
    dictionary,             // Construction parameter type identifier
    (const dictionary& dict, const scalar g),  // Complete constructor signature
    (dict, g)               // Constructor argument names for invocation
);

// Macro expands to approximately 50+ lines of boilerplate code:
class waveModel {
public:
    // Type definition for factory function pointer
    typedef autoPtr<waveModel> (*dictionaryConstructorPtr)
        (const dictionary& dict, const scalar g);

    // Static factory table type
    typedef HashTable<dictionaryConstructorPtr, word> dictionaryConstructorTable;
    
    // Global registry pointer (initialized in .C file)
    static dictionaryConstructorTable* dictionaryConstructorTablePtr_;

    // Factory table management methods
    static const dictionaryConstructorTable& dictionaryConstructorTable();
    static bool dictionaryConstructorTablePtr;
    
    // Static New method for object creation
    static autoPtr<waveModel> New(const dictionary& dict, const scalar g);
};
```

Macro จัดการกับหลายประเด็นโดยอัตโนมัติ:
- **Smart Pointer Types**: ใช้ `autoPtr` สำหรับ exclusive ownership และ `tmp` สำหรับการแชร์แบบ reference-counted
- **Hash Table Storage**: การค้นหา constructors โดยชื่อโมเดลอย่างมีประสิทธิภาพ O(1)
- **Template Flexibility**: ทำงานกับ return type และชุดค่าพารามิเตอร์ใดๆ
- **Thread Safety**: ให้การเข้าถึงข้อมูล static initialization อย่างปลอดภัย

## Static Registration: `addToRunTimeSelectionTable`

กลไกการลงทะเบียนใช้ประโยชน์จาก C++ static initialization เพื่อลงทะเบียนคลาสโมเดลโดยอัตโนมัติก่อนที่ `main()` จะเริ่มทำงาน วิธีการที่สง่างามนี้ช่วยให้มั่นใจได้ว่าโมเดลที่มีอยู่ทั้งหมดเป็นที่รู้จักของระบบโดยไม่ต้องการการลงทะเบียนด้วยตนเอง:

```cpp
// In purePhaseModel.C - registers at program startup
addToRunTimeSelectionTable
(
    phaseModel,           // Base class for registration
    purePhaseModel,       // Concrete class to register
    dictionary            // Parameter signature identifier
);

// Macro creates static registration object (simplified):
namespace {
    // Anonymous namespace ensures uniqueness
    phaseModel::dictionaryConstructorTable::entry_proxy
        addpurePhaseModelToRunTimeSelectionTable
        (
            "pure",                     // Dictionary type name for lookup
            purePhaseModel::New         // Static factory function pointer
        );
}

// Concrete class implements the New method:
autoPtr<phaseModel> purePhaseModel::New
(
    const dictionary& dict,
    const fvMesh& mesh
)
{
    // Actual object construction with parameter validation
    return autoPtr<phaseModel>(new purePhaseModel(dict, mesh));
}
```

**ข้อมูลเชิงเทคนิคที่สำคัญ**: การลงทะเบียนเกิดขึ้นในระหว่าง **ระยะเวลาการเริ่มต้นแบบ static** ของการทำงานโปรแกรม C++ ซึ่งเกิดขึ้น:
1. ก่อนที่ `main()` จะเริ่ม
2. ในลำดับที่ไม่ระบุทั่ว translation units
3. พร้อมรับประกันการเริ่มต้นของตัวแปร static local ใน C++11+

คลาส `entry_proxy` ช่วยให้มั่นใจได้ในการลงทะเบียนที่แข็งแกร่ง:
```cpp
template<class Type, class TypeTable>
class entry_proxy {
public:
    entry_proxy(const word& name, Type* ptr) {
        if (!TypeTable::tablePtr_) {
            TypeTable::tablePtr_ = new TypeTable;
        }
        TypeTable::tablePtr_->insert(name, ptr);
    }
};
```

## Factory Method Implementation

ฟังก์ชัน dispatcher ทำหน้าที่เป็นศูนย์กลางสำหรับการสร้างออบเจกต์ โดยแปลงตัวระบุสตริงเป็นอินสแตนซ์คลาสที่เป็นรูปธรรม:

```cpp
// phaseModel::New() - the core dispatcher method
autoPtr<phaseModel> phaseModel::New
(
    const dictionary& dict,
    const fvMesh& mesh
)
{
    // 1. Extract model type from dictionary with fallback
    const word modelType = dict.lookupOrDefault<word>("type", "pure");

    Info << "Selecting phaseModel: " << modelType << endl;

    // 2. Look up factory function in global registry
    dictionaryConstructorTable::iterator cstrIter =
        dictionaryConstructorTablePtr_->find(modelType);

    // 3. Handle missing models with comprehensive error reporting
    if (cstrIter == dictionaryConstructorTablePtr_->end()) {
        FatalErrorInFunction
            << "Unknown phaseModel type " << modelType << nl << nl
            << "Valid types are:" << nl
            << dictionaryConstructorTablePtr_->sortedToc() << nl << nl
            << "Dictionary contents:" << nl
            << dict << nl << nl
            << exit(FatalError);
    }

    // 4. Invoke factory function through function pointer
    autoPtr<phaseModel> phasePtr = cstrIter()(dict, mesh);
    
    Info << "Created phaseModel of type " << modelType 
         << " for phase " << phasePtr->name() << endl;
         
    return phasePtr;
}
```

การ implement นี้ให้ข้อได้เปรียบหลายประการ:
- **Runtime Validation**: ข้อเสนอแนะทันทีสำหรับชื่อโมเดลที่ไม่ถูกต้อง
- **Helpful Error Messages**: แสดงรายการโมเดลที่มีอยู่ทั้งหมดเมื่อเกิดข้อผิดพลาด
- **Diagnostic Information**: รายงานการสร้างโมเดลที่สำเร็จสำหรับการแก้จุดบกพร่อง
- **Type Safety**: การตรวจสอบในเวลา compile ของ constructor signatures

## Memory Management: `autoPtr` และ `tmp`

กลยุทธ์การจัดการหน่วยความจำของ OpenFOAM ผสานรวมกับระบบ RTS ผ่านคลาส smart pointer:

```cpp
autoPtr<phaseModel> phase = phaseModel::New(dict, mesh);
// phase เป็นเจ้าของออบเจกต์แบบ exclusive จะลบเมื่อออกจาก scope
// Transfer semantics: move-only, ไม่อนุญาตให้คัดลอก

// Access the underlying object
phaseModel& phaseRef = phase();  // Dereference operator
phaseModel* phasePtr = phase.operator->();  // Arrow operator

// For temporary field results, use tmp<> with reference counting
tmp<volScalarField> trho = phase->rho();
// สามารถนำกลับมาใช้ใหม่ได้โดยไม่ต้องคัดลอกผ่านกลไก refCount

// Efficient reuse pattern
tmp<volScalarField> density = phase->rho();
tmp<volScalarField> viscosity = phase->mu();

// Field operations work directly with tmp<> objects
tmp<volVectorField> velocity = phase->U();
tmp<volScalarField> Reynolds = 
    (density * mag(velocity) * characteristicLength) / viscosity;
```

คลาส `autoPtr` ให้:
- **Exclusive Ownership**: ความหมายของความเป็นเจ้าของที่ชัดเจน ไม่มีค่าใช้จ่ายในการ reference counting
- **Move Semantics**: การถ่ายโอนความเป็นเจ้าของอย่างมีประสิทธิภาพระหว่าง function scopes
- **Automatic Cleanup**: รูปแบบ RAII ช่วยให้มั่นใจในการ deallocation หน่วยความจำ
- **Null Safety**: การสร้างเริ่มต้นสร้าง null pointer

คลาส `tmp` จัดการการเข้าถึงแบบแชร์:
- **Reference Counting**: ความหมายแบบ copy-on-write อัตโนมัติสำหรับข้อมูลฟิลด์
- **Expression Templates**: เปิดใช้งาน lazy evaluation ของการดำเนินการทางคณิตศาสตร์
- **Memory Efficiency**: หลีกเลี่ยงการคัดลอกอาร์เรย์ฟิลด์ขนาดใหญ่ที่ไม่จำเป็น

## Advanced RTS Features

ระบบ RTS ของ OpenFOAM รองรับรูปแบบที่ซับซ้อนสำหรับแอปพลิเคชัน CFD ที่ซับซ้อน:

### Multiple Construction Signatures
```cpp
// Model can support multiple factory tables simultaneously
declareRunTimeSelectionTable
(
    autoPtr,
    phaseModel,
    dictionary,
    (const dictionary& dict, const fvMesh& mesh),
    (dict, mesh)
);

declareRunTimeSelectionTable
(
    autoPtr,
    phaseModel,
    mesh,
    (const fvMesh& mesh),
    (mesh)
);
```

### Template-Based Specialization
```cpp
// Templates work seamlessly with RTS
template<class Type>
class transportModel {
public:
    declareRunTimeSelectionTable
    (
        autoPtr,
        transportModel,
        dictionary,
        (const dictionary& dict),
        (dict)
    );
    
    virtual tmp<GeometricField<Type, fvPatchField, volMesh>> 
        nu() const = 0;
};
```

### Dynamic Library Loading
```cpp
// Models can be loaded from shared libraries at runtime
libs ("libreactingPhaseSystem.so" "libMyCustomModels.so");

// RTS automatically discovers models in loaded libraries
addToRunTimeSelectionTable
(
    phaseModel,
    myCustomPhaseModel,
    dictionary
);
```

ระบบ RTS ที่ซับซ้อนนี้เป็นกระดูกสันหลังของความสามารถในการขยายของ OpenFOAM ทำให้นักวิจัยและวิศวกรสามารถเพิ่มโมเดลฟิสิกส์ใหม่ รูปแบบเชิงตัวเลข และเงื่อนไขขอบเขตได้โดยไม่ต้องแก้ไขโค้ด core solver ความสง่างามของระบบนี้อยู่ที่ความสามารถในการรักษาความปลอดภัยของประเภทและประสิทธิภาพในขณะที่ให้ความยืดหยุ่นสูงสุดสำหรับการกำหนดค่าการจำลอง CFD
