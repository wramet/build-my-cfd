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
    mu              0.001;          // Dynamic viscosity
    sigma           0.072;          // Surface tension
}

// Runtime creation - NO hardcoded type names!
// การสร้างออบเจกต์ในขณะทำงาน - ไม่มีชื่อประเภทที่ถูก hard-code
autoPtr<phaseModel> waterPhase = phaseModel::New(waterDict, mesh);
```

**📚 คำอธิบายโดยละเอียด (Thai Explanation)**

**แหล่งที่มา (Source):** แนวคิดนี้ถูกนำไปใช้ใน OpenFOAM solvers และ utilities หลายตัว โดยเฉพาะในไฟล์ `.applications/utilities/thermophysical/chemkinToFoam/chemkinReader/chemkinReader.C` ซึ่งใช้การกำหนดค่าแบบ dictionary-driven สำหรับการอ่านข้อมูลทางเคมี

**คำอธิบาย (Explanation):** โค้ดตัวอย่างแสดงให้เห็นถึงพลังของระบบ RTS ใน OpenFOAM ผู้ใช้สามารถระบุคุณสมบัติของเฟส (เช่น water) ในไฟล์ dictionary แบบข้อความ โดยระบุประเภทของโมเดล (`type pure`) และพารามิเตอร์ต่างๆ ที่จำเป็น ระบบจะสร้างออบเจกต์ `phaseModel` ที่เหมาะสม (ในกรณีนี้คือ `purePhaseModel`) โดยอัตโนมัติเมื่อโปรแกรมทำงาน โดยไม่ต้องแก้ไขหรือคอมไพล์โค้ด solver ใหม่

**แนวคิดสำคัญ (Key Concepts):**
- **Dictionary-Driven Configuration:** การกำหนดค่าผ่านไฟล์ข้อความที่อ่านง่าย
- **Runtime Polymorphism:** การสร้างออบเจกต์ตามประเภทที่ระบุใน runtime
- **Factory Pattern:** ดีไซน์แพทเทิร์นสำหรับสร้างออบเจกต์โดยไม่ระบุคลาสที่แน่นอน
- **Decoupling:** การแยก solver ออกจากโมเดลเฉพาะ ทำให้สามารถเพิ่มโมเดลใหม่ได้โดยไม่กระทบ solver

---

แนวทางนี้ขจัดการพึ่งพาในเวลา compile ระหว่าง solvers และโมเดลเฉพาะ โมเดลใหม่สามารถเพิ่มเป็นไลบรารีแยกต่างหากได้โดยไม่ต้องคอมไพล์ core solver ใหม่ ทำให้มีความสามารถในการขยายแบบ plugin ซึ่งเป็นสิ่งสำคัญสำหรับแอปพลิเคชัน CFD ที่เน้นการวิจัย

## Macro Magic: `declareRunTimeSelectionTable`

ระบบ RTS พึ่งพา preprocessor macros ที่ซับซ้อนในการสร้างโครงสร้างพื้นฐาน factory โดยอัตโนมัติ Macro `declareRunTimeSelectionTable` สร้างโครงสร้างข้อมูลสถิติและฟังก์ชันสมาชิกที่จำเป็นสำหรับการเลือกใน runtime:

```cpp
// In waveModel.H - declares factory infrastructure
// การประกาศโครงสร้างพื้นฐานของ factory
declareRunTimeSelectionTable
(
    autoPtr,                // Return type: smart pointer for exclusive ownership
    waveModel,              // Base class name
    dictionary,             // Construction parameter type identifier
    (const dictionary& dict, const scalar g),  // Complete constructor signature
    (dict, g)               // Constructor argument names for invocation
);

// Macro expands to approximately 50+ lines of boilerplate code:
// Macro นี้จะขยายไปเป็นโค้ดประมาณ 50+ บรรทัด
class waveModel {
public:
    // Type definition for factory function pointer
    // นิยามประเภทสำหรับ pointer ของฟังก์ชัน factory
    typedef autoPtr<waveModel> (*dictionaryConstructorPtr)
        (const dictionary& dict, const scalar g);

    // Static factory table type
    // ประเภทตาราง factory แบบสถิติ
    typedef HashTable<dictionaryConstructorPtr, word> dictionaryConstructorTable;

    // Global registry pointer (initialized in .C file)
    // Pointer สำหรับรีจิสทรีทั่วไป (เริ่มต้นในไฟล์ .C)
    static dictionaryConstructorTable* dictionaryConstructorTablePtr_;

    // Factory table management methods
    // วิธีการจัดการตาราง factory
    static const dictionaryConstructorTable& dictionaryConstructorTable();
    static bool dictionaryConstructorTablePtr;

    // Static New method for object creation
    // วิธีการ New แบบสถิติสำหรับสร้างออบเจกต์
    static autoPtr<waveModel> New(const dictionary& dict, const scalar g);
};
```

**📚 คำอธิบายโดยละเอียด (Thai Explanation)**

**แหล่งที่มา (Source):** รูปแบบนี้ถูกนำไปใช้อย่างแพร่หลายใน OpenFOAM โดยเฉพาะในไฟล์ตัวอย่างเช่น `.applications/test/syncTools/Test-syncTools.C` และ `.applications/test/globalIndex/Test-globalIndex.C`

**คำอธิบาย (Explanation):** Macro `declareRunTimeSelectionTable` เป็นหัวใจสำคัญของระบบ RTS ใน OpenFOAM มันทำหน้าที่สร้างโครงสร้างพื้นฐานที่จำเป็นสำหรับ factory pattern โดยอัตโนมัติ ซึ่งประกอบด้วย:

1. **Function Pointer Type:** นิยามประเภท pointer สำหรับฟังก์ชันที่สร้างออบเจกต์ (constructor)
2. **Hash Table:** ตารางแบบ Hash สำหรับเก็บฟังก์ชัน constructors ทั้งหมด โดยใช้ชื่อโมเดลเป็นคีย์
3. **Static Registry:** ตัวแปร static สำหรับเก็บตาราง constructors ที่ใช้ร่วมกันทั่วทั้งโปรแกรม
4. **Management Methods:** ฟังก์ชันสำหรับเข้าถึงและจัดการตาราง constructors

สิ่งที่น่าประทับใจคือ macro นี้แปลงเป็นโค้ด C++ ประมาณ 50+ บรรทัด ซึ่งประกอบด้วยโครงสร้างข้อมูล ฟังก์ชัน และตรรกะที่จำเป็นสำหรับการสร้างออบเจกต์ใน runtime

**แนวคิดสำคัญ (Key Concepts):**
- **Preprocessor Macros:** การใช้ macro เพื่อสร้างโค้ดซ้ำๆ อัตโนมัติ
- **Function Pointers:** การใช้ pointer ชี้ไปยังฟังก์ชันสำหรับการสร้างออบเจกต์
- **Hash Table:** โครงสร้างข้อมูลสำหรับเก็บและค้นหา constructors อย่างรวดเร็ว
- **Static Initialization:** การเริ่มต้นตัวแปร static ก่อนฟังก์ชัน main() ทำงาน

---

Macro จัดการกับหลายประเด็นโดยอัตโนมัติ:
- **Smart Pointer Types:** ใช้ `autoPtr` สำหรับ exclusive ownership และ `tmp` สำหรับการแชร์แบบ reference-counted
- **Hash Table Storage:** การค้นหา constructors โดยชื่อโมเดลอย่างมีประสิทธิภาพ O(1)
- **Template Flexibility:** ทำงานกับ return type และชุดค่าพารามิเตอร์ใดๆ
- **Thread Safety:** ให้การเข้าถึงข้อมูล static initialization อย่างปลอดภัย

## Static Registration: `addToRunTimeSelectionTable`

กลไกการลงทะเบียนใช้ประโยชน์จาก C++ static initialization เพื่อลงทะเบียนคลาสโมเดลโดยอัตโนมัติก่อนที่ `main()` จะเริ่มทำงาน วิธีการที่สง่างามนี้ช่วยให้มั่นใจได้ว่าโมเดลที่มีอยู่ทั้งหมดเป็นที่รู้จักของระบบโดยไม่ต้องการการลงทะเบียนด้วยตนเอง:

```cpp
// In purePhaseModel.C - registers at program startup
// ลงทะเบียนโมเดลเมื่อเริ่มต้นโปรแกรม
addToRunTimeSelectionTable
(
    phaseModel,           // Base class for registration
    purePhaseModel,       // Concrete class to register
    dictionary            // Parameter signature identifier
);

// Macro creates static registration object (simplified):
// Macro สร้างออบเจกต์ลงทะเบียนแบบ static (แบบย่อ)
namespace {
    // Anonymous namespace ensures uniqueness
    // Namespace ไม่มีชื่อช่วยให้มั่นใจว่าไม่ซ้ำกัน
    phaseModel::dictionaryConstructorTable::entry_proxy
        addpurePhaseModelToRunTimeSelectionTable
        (
            "pure",                     // Dictionary type name for lookup
            purePhaseModel::New         // Static factory function pointer
        );
}

// Concrete class implements the New method:
// คลาสที่เป็นรูปธรรม implement วิธีการ New
autoPtr<phaseModel> purePhaseModel::New
(
    const dictionary& dict,
    const fvMesh& mesh
)
{
    // Actual object construction with parameter validation
    // การสร้างออบเจกต์จริงพร้อมการตรวจสอบพารามิเตอร์
    return autoPtr<phaseModel>(new purePhaseModel(dict, mesh));
}
```

**📚 คำอธิบายโดยละเอียด (Thai Explanation)**

**แหล่งที่มา (Source):** กลไกนี้ถูกนำไปใช้อย่างแพร่หลายใน OpenFOAM โดยเฉพาะใน utilities เช่น `.applications/utilities/mesh/manipulation/polyDualMesh/meshDualiser.C`

**คำอธิบาย (Explanation):** Macro `addToRunTimeSelectionTable` เป็นกลไกที่ชาญฉลาดในการลงทะเบียนโมเดลใหม่เข้าสู่ระบบ RTS โดยอัตโนมัติ สิ่งที่น่าสนใจคือ:

1. **Anonymous Namespace:** การใช้ namespace ไม่มีชื่อช่วยป้องกันความขัดแย้งของชื่อตัวแปรระหว่างไฟล์ต่างๆ
2. **Static Initialization:** การลงทะเบียนเกิดขึ้นโดยอัตโนมัติก่อนที่ฟังก์ชัน `main()` จะเริ่มทำงาน
3. **entry_proxy Class:** คลาสตัวช่วยที่จัดการการเพิ่มโมเดลเข้าสู่ตาราง constructors
4. **Factory Function:** แต่ละคลาสต้อง implement ฟังก์ชัน `New` สำหรับสร้างออบเจกต์ของตัวเอง

เมื่อโปรแกรมถูกคอมไพล์ ทุกไฟล์ `.C` ที่ใช้ macro นี้จะสร้างออบเจกต์ลงทะเบียนแบบ static ซึ่งจะถูกเรียกก่อน `main()` ทำให้โมเดลทั้งหมดพร้อมใช้งานเมื่อโปรแกรมเริ่มทำงาน

**แนวคิดสำคัญ (Key Concepts):**
- **Static Initialization Order:** ลำดับการเริ่มต้นตัวแปร static ก่อน main()
- **Anonymous Namespace:** กลไกสำหรับป้องกันความขัดแย้งของชื่อ
- **Entry Proxy Pattern:** ดีไซน์แพทเทิร์นสำหรับลงทะเบียนคลาสอัตโนมัติ
- **Zero Registration Overhead:** ไม่ต้องลงทะเบียนด้วยตนเอง ทำให้ลดความผิดพลาด

---

**ข้อมูลเชิงเทคนิคที่สำคัญ**: การลงทะเบียนเกิดขึ้นในระหว่าง **ระยะเวลาการเริ่มต้นแบบ static** ของการทำงานโปรแกรม C++ ซึ่งเกิดขึ้น:
1. ก่อนที่ `main()` จะเริ่ม
2. ในลำดับที่ไม่ระบุทั่ว translation units
3. พร้อมรับประกันการเริ่มต้นของตัวแปร static local ใน C++11+

คลาส `entry_proxy` ช่วยให้มั่นใจได้ในการลงทะเบียนที่แข็งแกร่ง:
```cpp
template<class Type, class TypeTable>
class entry_proxy {
public:
    // Constructor registers the class with the factory table
    // Constructor ลงทะเบียนคลาสเข้ากับตาราง factory
    entry_proxy(const word& name, Type* ptr) {
        // Initialize table if not exists
        // เริ่มต้นตารางหากยังไม่มี
        if (!TypeTable::tablePtr_) {
            TypeTable::tablePtr_ = new TypeTable;
        }
        // Insert into hash table by name
        // เพิ่มเข้าในตาราง hash ตามชื่อ
        TypeTable::tablePtr_->insert(name, ptr);
    }
};
```

**📚 คำอธิบายโดยละเอียด (Thai Explanation)**

**แหล่งที่มา (Source):** คลาส `entry_proxy` และกลไกการลงทะเบียนถูกนำไปใช้ในหลายส่วนของ OpenFOAM โดยเฉพาะใน utilities ที่ต้องการการจัดการ mesh และ data structures ที่ซับซ้อน

**คำอธิบาย (Explanation):** คลาส `entry_proxy` เป็นคลาส template ขนาดเล็กแต่มีพลังมาก ทำหน้าที่เป็นตัวกลางในการลงทะเบียนคลาสใหม่เข้าสู่ระบบ RTS:

1. **Lazy Initialization:** ตรวจสอบและสร้างตารางถ้ายังไม่มีอยู่
2. **Hash Table Insertion:** เพิ่มฟังก์ชัน constructor เข้าสู่ตารางโดยใช้ชื่อเป็นคีย์
3. **Type Safety:** รับประกันว่าประเภทของคลาสถูกต้องผ่าน template parameters
4. **Automatic Registration:** การลงทะเบียนเกิดขึ้นโดยอัตโนมัติผ่าน constructor

สิ่งที่น่าสนใจคือคลาสนี้ทำงานผ่าน constructor ซึ่งถูกเรียกโดยอัตโนมัติเมื่อโปรแกรมเริ่มทำงาน ทำให้การลงทะเบียนโมเดลทุกตัวเกิดขึ้นโดยอัตโนมัติและโปร่งใสต่อผู้ใช้

**แนวคิดสำคัญ (Key Concepts):**
- **Lazy Initialization Pattern:** การสร้างออบเจกต์เมื่อจำเป็นต้องใช้จริง
- **Template Metaprogramming:** การใช้ template เพื่อสร้างโค้ดทั่วไปและปลอดภัย
- **RAII (Resource Acquisition Is Initialization):** การจัดการทรัพยากรผ่าน constructor/destructor
- **Hash Table Operations:** การดำเนินการพื้นฐานบนตาราง hash

---

## Factory Method Implementation

ฟังก์ชัน dispatcher ทำหน้าที่เป็นศูนย์กลางสำหรับการสร้างออบเจกต์ โดยแปลงตัวระบุสตริงเป็นอินสแตนซ์คลาสที่เป็นรูปธรรม:

```cpp
// phaseModel::New() - the core dispatcher method
// วิธีการหลักในการจัดการการสร้างออบเจกต์
autoPtr<phaseModel> phaseModel::New
(
    const dictionary& dict,
    const fvMesh& mesh
)
{
    // 1. Extract model type from dictionary with fallback
    // ดึงประเภทโมเดลจาก dictionary พร้อมค่าเริ่มต้น
    const word modelType = dict.lookupOrDefault<word>("type", "pure");

    Info << "Selecting phaseModel: " << modelType << endl;

    // 2. Look up factory function in global registry
    // ค้นหาฟังก์ชัน factory ในรีจิสทรีทั่วไป
    dictionaryConstructorTable::iterator cstrIter =
        dictionaryConstructorTablePtr_->find(modelType);

    // 3. Handle missing models with comprehensive error reporting
    // จัดการกรณีโมเดลไม่พร้อมพร้อมรายงานข้อผิดพลาดอย่างละเอียด
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
    // เรียกฟังก์ชัน factory ผ่าน function pointer
    autoPtr<phaseModel> phasePtr = cstrIter()(dict, mesh);

    Info << "Created phaseModel of type " << modelType
         << " for phase " << phasePtr->name() << endl;

    return phasePtr;
}
```

**📚 คำอธิบายโดยละเอียด (Thai Explanation)**

**แหล่งที่มา (Source):** รูปแบบฟังก์ชัน dispatcher นี้ถูกนำไปใช้อย่างแพร่หลายใน OpenFOAM โดยเฉพาะในไฟล์เช่น `.applications/utilities/thermophysical/chemkinToFoam/chemkinReader/chemkinReader.C` ซึ่งใช้สำหรับสร้าง readers ประเภทต่างๆ

**คำอธิบาย (Explanation):** ฟังก์ชัน `phaseModel::New()` เป็นหัวใจของระบบ RTS ทำหน้าที่เป็น dispatcher หรือตัวจัดการกลางในการสร้างออบเจกต์:

1. **Dictionary Lookup:** อ่านประเภทโมเดลจาก dictionary พร้อมค่าเริ่มต้น ("pure")
2. **Factory Table Search:** ค้นหาฟังก์ชัน constructor ที่เหมาะสมในตาราง hash
3. **Error Handling:** แสดงข้อผิดพลาดที่ครบถ้วนหากไม่พบโมเดล พร้อมรายชื่อโมเดลที่มี
4. **Object Creation:** เรียกฟังก์ชัน constructor ผ่าน function pointer และคืนค่าออบเจกต์

สิ่งที่ทำให้ฟังก์ชันนี้มีประสิทธิภาพคือการใช้ Hash Table สำหรับการค้นหาที่รวดเร็ว (O(1)) และการจัดการข้อผิดพลาดที่ครบถ้วน ซึ่งช่วยให้ผู้ใช้รู้ว่ามีโมเดลอะไรบ้างและทำอะไรผิดพลาด

**แนวคิดสำคัญ (Key Concepts):**
- **Dispatcher Pattern:** ดีไซน์แพทเทิร์นสำหรับจัดการการเรียกฟังก์ชันที่เหมาะสม
- **Hash Table Lookup:** การค้นหาที่รวดเร็วผ่านตาราง hash
- **Error Reporting:** การรายงานข้อผิดพลาดที่มีประโยชน์และเป็นมิตรกับผู้ใช้
- **Smart Pointer Return:** การคืนค่าผ่าน smart pointer เพื่อความปลอดภัยของหน่วยความจำ

---

การ implement นี้ให้ข้อได้เปรียบหลายประการ:
- **Runtime Validation:** ข้อเสนอแนะทันทีสำหรับชื่อโมเดลที่ไม่ถูกต้อง
- **Helpful Error Messages:** แสดงรายการโมเดลที่มีอยู่ทั้งหมดเมื่อเกิดข้อผิดพลาด
- **Diagnostic Information:** รายงานการสร้างโมเดลที่สำเร็จสำหรับการแก้จุดบกพร่อง
- **Type Safety:** การตรวจสอบในเวลา compile ของ constructor signatures

## Memory Management: `autoPtr` และ `tmp`

กลยุทธ์การจัดการหน่วยความจำของ OpenFOAM ผสานรวมกับระบบ RTS ผ่านคลาส smart pointer:

```cpp
// Create phase model using RTS - autoPtr manages exclusive ownership
// สร้างโมเดลเฟสโดยใช้ RTS - autoPtr จัดการ exclusive ownership
autoPtr<phaseModel> phase = phaseModel::New(dict, mesh);
// phase เป็นเจ้าของออบเจกต์แบบ exclusive จะลบเมื่อออกจาก scope
// Transfer semantics: move-only, ไม่อนุญาตให้คัดลอก

// Access the underlying object
// เข้าถึงออบเจกต์ที่อยู่ภายใน
phaseModel& phaseRef = phase();  // Dereference operator
phaseModel* phasePtr = phase.operator->();  // Arrow operator

// For temporary field results, use tmp<> with reference counting
// สำหรับผลลัพธ์ฟิลด์ชั่วคราว ใช้ tmp<> พร้อม reference counting
tmp<volScalarField> trho = phase->rho();
// สามารถนำกลับมาใช้ใหม่ได้โดยไม่ต้องคัดลอกผ่านกลไก refCount

// Efficient reuse pattern
// รูปแบบการนำกลับมาใช้ใหม่ที่มีประสิทธิภาพ
tmp<volScalarField> density = phase->rho();
tmp<volScalarField> viscosity = phase->mu();

// Field operations work directly with tmp<> objects
// การดำเนินการฟิลด์ทำงานโดยตรงกับออบเจกต์ tmp<>
tmp<volVectorField> velocity = phase->U();
tmp<volScalarField> Reynolds =
    (density * mag(velocity) * characteristicLength) / viscosity;
```

**📚 คำอธิบายโดยละเอียด (Thai Explanation)**

**แหล่งที่มา (Source):** ระบบ smart pointer ของ OpenFOAM ถูกนำไปใช้ทั่วทั้ง codebase โดยเฉพาะใน utilities ที่ต้องการการจัดการหน่วยความจำที่มีประสิทธิภาพ เช่น ใน `.applications/utilities/mesh/manipulation/polyDualMesh/meshDualiser.C`

**คำอธิบาย (Explanation):** OpenFOAM ใช้สองประเภทหลักของ smart pointer:

**autoPtr (Exclusive Ownership):**
- เป็นเจ้าของออบเจกต์แบบ exclusive เพียงหนึ่งตัวเท่านั้น
- ไม่สามารถคัดลอกได้ สามารถโอนความเป็นเจ้าของได้ (move-only)
- ลบออบเจกต์อัตโนมัติเมื่อออกจาก scope (RAII)
- เหมาะสำหรับออบเจกต์ที่สร้างจาก RTS

**tmp (Shared/Temporary Access):**
- ใช้ reference counting สำหรับการแชร์ข้อมูล
- รองรับ copy-on-write semantics
- เหมาะสำหรับฟิลด์ขนาดใหญ่ที่ไม่ต้องการคัดลอก
- ทำงานร่วมกับ expression templates สำหรับประสิทธิภาพสูง

การใช้ smart pointers ทั้งสองประเภทนี้ทำให้ OpenFOAM มีการจัดการหน่วยความจำที่ปลอดภัยและมีประสิทธิภาพ โดยไม่ต้องใช้ garbage collection แบบ Java หรือ C#

**แนวคิดสำคัญ (Key Concepts):**
- **RAII (Resource Acquisition Is Initialization):** การจัดการทรัพยากรผ่าน lifecycle ของออบเจกต์
- **Move Semantics:** การโอนความเป็นเจ้าของแทนการคัดลอก
- **Reference Counting:** การติดตามจำนวนการอ้างอิงของออบเจกต์
- **Copy-on-Write:** การคัดลอกเมื่อมีการแก้ไขจริงเท่านั้น
- **Expression Templates:** เทคนิคการเพิ่มประสิทธิภาพการดำเนินการคณิตศาสตร์

---

คลาส `autoPtr` ให้:
- **Exclusive Ownership:** ความหมายของความเป็นเจ้าของที่ชัดเจน ไม่มีค่าใช้จ่ายในการ reference counting
- **Move Semantics:** การถ่ายโอนความเป็นเจ้าของอย่างมีประสิทธิภาพระหว่าง function scopes
- **Automatic Cleanup:** รูปแบบ RAII ช่วยให้มั่นใจในการ deallocation หน่วยความจำ
- **Null Safety:** การสร้างเริ่มต้นสร้าง null pointer

คลาส `tmp` จัดการการเข้าถึงแบบแชร์:
- **Reference Counting:** ความหมายแบบ copy-on-write อัตโนมัติสำหรับข้อมูลฟิลด์
- **Expression Templates:** เปิดใช้งาน lazy evaluation ของการดำเนินการทางคณิตศาสตร์
- **Memory Efficiency:** หลีกเลี่ยงการคัดลอกอาร์เรย์ฟิลด์ขนาดใหญ่ที่ไม่จำเป็น

## Advanced RTS Features

ระบบ RTS ของ OpenFOAM รองรับรูปแบบที่ซับซ้อนสำหรับแอปพลิเคชัน CFD ที่ซับซ้อน:

### Multiple Construction Signatures
```cpp
// Model can support multiple factory tables simultaneously
// โมเดลสามารถรองรับหลายตาราง factory พร้อมกันได้
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

**📚 คำอธิบายโดยละเอียด (Thai Explanation)**

**แหล่งที่มา (Source):** ความสามารถในการมีหลาย signatures ถูกนำไปใช้ใน utilities หลายตัวของ OpenFOAM โดยเฉพาะใน `.applications/utilities/thermophysical/chemkinToFoam/chemkinReader/chemkinReader.C`

**คำอธิบาย (Explanation):** ระบบ RTS ของ OpenFOAM รองรับการสร้างออบเจกต์ผ่านหลายวิธี โดยแต่ละวิธีมี signature ที่แตกต่างกัน:

1. **Dictionary-based:** สร้างจาก dictionary พร้อม mesh (สำหรับการตั้งค่าแบบละเอียด)
2. **Mesh-based:** สร้างจาก mesh เท่านั้น (สำหรับการใช้งานแบบง่าย)

ความยืดหยุ่นนี้ทำให้โมเดลสามารถสร้างได้หลายวิธีขึ้นอยู่กับบริบท ทำให้โค้ดมีความยืดหยุ่นและใช้งานได้หลากหลายยิ่งขึ้น

**แนวคิดสำคัญ (Key Concepts):**
- **Function Overloading:** การมีหลายฟังก์ชันด้วยชื่อเดียวกันแต่ signature ต่างกัน
- **Factory Table Multiplicity:** การมีหลายตาราง factory สำหรับวิธีการสร้างที่แตกต่างกัน
- **Context-Specific Construction:** การสร้างออบเจกต์ตามบริบทการใช้งาน

---

### Template-Based Specialization
```cpp
// Templates work seamlessly with RTS
// Templates ทำงานร่วมกับ RTS ได้อย่างราบรื่น
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

**📚 คำอธิบายโดยละเอียด (Thai Explanation)**

**แหล่งที่มา (Source):** การใช้ template กับ RTS ถูกนำไปใช้อย่างแพร่หลายใน OpenFOAM โดยเฉพาะในไฟล์ต่างๆ ใน `src/OpenFOAM/fields/`

**คำอธิบาย (Explanation):** การรวม template กับ RTS ทำให้สามารถสร้างโมเดลที่ทำงานกับประเภทข้อมูลต่างๆ ได้:

1. **Type Generality:** โมเดลสามารถทำงานกับ scalar, vector, tensor หรือประเภทอื่นๆ
2. **Code Reuse:** เขียนโค้ดครั้งเดียว ใช้ได้กับหลายประเภท
3. **Type Safety:** การตรวจสอบประเภทในเวลา compile

สิ่งที่น่าประทับใจคือระบบ RTS สามารถจัดการกับ template classes ได้อย่างราบรื่น โดยไม่ต้องแก้ไข macro หรือโครงสร้างพื้นฐาน

**แนวคิดสำคัญ (Key Concepts):**
- **Template Metaprogramming:** การใช้ template เพื่อสร้างโค้ดทั่วไป
- **Type Erasure:** การซ่อนประเภทที่แน่นอนผ่าน interface
- **Compile-Time Polymorphism:** การทำ polymorphism ในเวลา compile

---

### Dynamic Library Loading
```cpp
// Models can be loaded from shared libraries at runtime
// โมเดลสามารถโหลดจาก shared libraries ใน runtime ได้
libs ("libreactingPhaseSystem.so" "libMyCustomModels.so");

// RTS automatically discovers models in loaded libraries
// RTS ค้นหาโมเดลใน libraries ที่โหลดโดยอัตโนมัติ
addToRunTimeSelectionTable
(
    phaseModel,
    myCustomPhaseModel,
    dictionary
);
```

**📚 คำอธิบายโดยละเอียด (Thai Explanation)**

**แหล่งที่มา (Source):** ความสามารถในการโหลด dynamic libraries ถูกนำไปใช้ใน solvers และ utilities หลายตัวของ OpenFOAM โดยเฉพาะในกรณีที่ต้องการรองรับ custom physics

**คำอธิบาย (Explanation):** ความสามารถในการโหลด libraries แบบ dynamic เป็นหนึ่งในคุณสมบัติที่ทรงพลังที่สุดของ OpenFOAM:

1. **Plugin Architecture:** เพิ่มโมเดลใหม่โดยไม่ต้องคอมไพล์ solver ใหม่
2. **Runtime Discovery:** RTS ค้นหาโมเดลใน libraries ที่โหลดโดยอัตโนมัติ
3. **Research Flexibility:** นักวิจัยสามารถทดสอบโมเดลใหม่โดยไม่กระทบ core code

การทำงาน:
- เมื่อ library ถูกโหลด (ผ่านคำสั่ง `libs` ใน dictionary)
- Static initialization objects ใน library ทำงาน
- โมเดลใหม่ถูกลงทะเบียนใน RTS tables
- โมเดลพร้อมใช้งานทันทีโดยไม่ต้องเริ่มโปรแกรมใหม่

**แนวคิดสำคัญ (Key Concepts):**
- **Dynamic Loading:** การโหลด libraries ใน runtime
- **Plugin Architecture:** สถาปัตยกรรมแบบ plugin สำหรับการขยาย
- **Static Initialization:** การเริ่มต้นอัตโนมัติเมื่อ library ถูกโหลด
- **Shared Libraries:** การใช้ libraries แบบ shared (.so files)

---

ระบบ RTS ที่ซับซ้อนนี้เป็นกระดูกสันหลังของความสามารถในการขยายของ OpenFOAM ทำให้นักวิจัยและวิศวกรสามารถเพิ่มโมเดลฟิสิกส์ใหม่ รูปแบบเชิงตัวเลข และเงื่อนไขขอบเขตได้โดยไม่ต้องแก้ไขโค้ด core solver ความสง่างามของระบบนี้อยู่ที่ความสามารถในการรักษาความปลอดภัยของประเภทและประสิทธิภาพในขณะที่ให้ความยืดหยุ่นสูงสุดสำหรับการกำหนดค่าการจำลอง CFD