# 06 ข้อผิดพลาดที่พบบ่อยและการดีบักใน Solver การไหลหลายเฟส (Common Errors and Debugging in Multiphase Solvers)

## การใช้งานที่ถูกต้อง: การกำหนดค่าผ่านพจนานุกรม (Dictionary-Driven Configuration)

ในสถาปัตยกรรมของ solver การไหลหลายเฟสใน OpenFOAM ระบบการกำหนดค่าผ่านพจนานุกรมช่วยให้สามารถสร้าง solver อเนกประสงค์ที่สามารถจัดการกับการกำหนดค่าเฟสใดๆ ได้โดยไม่ต้องแก้ไขโค้ด แนวทางนี้แสดงให้เห็นถึงพลังของรูปแบบ Factory (Factory patterns) ร่วมกับ Runtime Polymorphism

พจนานุกรมคุณสมบัติเฟส (`constant/phaseProperties`) กำหนดเฟสทั้งหมดและคุณสมบัติทางความร้อนฟิสิกส์ของเฟสเหล่านั้น:

```cpp
// constant/phaseProperties
phases (water air);

water {
    type            pure;
    rho             uniform 1000;
    mu              uniform 0.001;
}

air {
    type            pure;
    rho             uniform 1.225;
    mu              uniform 1.8e-5;
}
```

**📚 แหล่งที่มา:**
`constant/phaseProperties` - พจนานุกรมการกำหนดค่าขณะรันโปรแกรม (Runtime configuration dictionary) สำหรับการจำลองการไหลหลายเฟส

**💡 คำอธิบาย:**
ไฟล์พจนานุกรมนี้แสดงถึงแนวทางการกำหนดค่าของ OpenFOAM โดยที่คุณสมบัติของเฟสจะถูกกำหนดขณะรันโปรแกรมแทนที่จะเป็นเวลาคอมไพล์ คำหลัก `phases` จะแสดงรายการชื่อเฟสทั้งหมด ตามด้วยบล็อกของแต่ละเฟสที่ระบุคุณสมบัติการขนส่ง (ความหนาแน่น `rho` และความหนืด `mu`) รูปแบบนี้ช่วยให้ไบนารีของ solver ตัวเดียวกันสามารถจัดการกับการรวมกันของเฟสใดๆ ก็ได้

**🎯 แนวคิดสำคัญ:**
- Dictionary-driven configuration (การกำหนดค่าผ่านพจนานุกรม)
- Runtime polymorphism (พหุสัณฐานขณะรันโปรแกรม)
- Phase property specification (การระบุคุณสมบัติเฟส)
- Factory pattern preparation (การเตรียมรูปแบบโรงงาน)

โค้ดของ solver ยังคงเป็นแบบทั่วไป (generic) โดยจะสร้างเฟสที่กำหนดค่าไว้อัตโนมัติผ่านระบบ factory:

```cpp
// Generate interfacial models from dictionary configuration
this->generateInterfacialModels(dragModels_);
this->generateInterfacialModels(virtualMassModels_);
this->generateInterfacialModels(liftModels_);
```

**📚 แหล่งที่มา:**
`.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C:56-60`

**💡 คำอธิบาย:**
เมธอดเทมเพลต `generateInterfacialModels()` จะอ่านการนิยามอินเทอร์เฟซของเฟสจากพจนานุกรม และสร้างออบเจกต์โมเดลที่เหมาะสมโดยใช้ตารางการเลือกขณะรันโปรแกรม (Runtime selection table) สิ่งนี้แสดงให้เห็นถึงรูปแบบ factory ที่ประเภทโมเดลที่เป็นรูปธรรม (concrete model types) จะถูกสร้างขึ้นตามรายการในพจนานุกรมโดยไม่ต้องระบุชื่อคลาสตายตัวในโค้ด

**🎯 แนวคิดสำคัญ:**
- Template-based model generation (การสร้างโมเดลแบบใช้เทมเพลต)
- Runtime selection tables (ตารางการเลือกขณะรันโปรแกรม)
- Hash table storage for models (การจัดเก็บโมเดลในตารางแฮช)
- Automatic object instantiation (การสร้างอินสแตนซ์ออบเจกต์อัตโนมัติ)

รูปแบบการออกแบบนี้ช่วยให้ไบนารีของ solver ตัวเดียวสามารถจัดการกับเฟสใดๆ ก็ได้ โดยสามารถเพิ่มประเภทเฟสใหม่ผ่านการลงทะเบียน (registration) แทนที่จะต้องแก้ไขโค้ด

---

## ข้อผิดพลาดที่ 1: การเฉือนออบเจกต์ (Object Slicing)

การเฉือนออบเจกต์ (Object slicing) เป็นข้อผิดพลาดร้ายแรงใน C++ ที่เกิดขึ้นเมื่อออบเจกต์ของคลาสที่สืบทอดมา (derived class) ถูกส่งผ่านแบบค่า (pass by value) ไปยังฟังก์ชันที่ต้องการออบเจกต์ของคลาสฐาน (base class) สิ่งนี้จะ "เฉือน" ส่วนที่เป็นของคลาสที่สืบทอดมาออกไป ทำให้พฤติกรรมพหุสัณฐาน (polymorphic behavior) ไม่ถูกต้อง

### ปัญหา

การส่งผ่านแบบค่าจะคัดลอกเฉพาะส่วนของ `phaseModel` ที่เป็นคลาสฐาน ทำให้สูญเสียข้อมูลของคลาสที่สืบทอดมา:

```cpp
// ❌ ไม่ถูกต้อง: การส่งผ่านแบบค่าทำให้เกิดการเฉือนออบเจกต์
void processPhase(phaseModel phase) {  // คัดลอกเฉพาะส่วนที่เป็น phaseModel
    phase.correct();  // เรียกใช้ phaseModel::correct() เสมอ ไม่เคยเรียกส่วนที่สืบทอดมา
}
```

**📚 แหล่งที่มา:**
หลักการพหุสัณฐานทั่วไปของ C++ - ใช้ได้กับโมเดลเฟสทั้งหมดของ OpenFOAM

**💡 คำอธิบาย:**
เมื่อออบเจกต์ของคลาสที่สืบทอดมาถูกส่งผ่านแบบค่าไปยังฟังก์ชันที่ต้องการคลาสฐาน C++ จะสร้างออบเจกต์คลาสฐานผ่าน "การเฉือนออบเจกต์" เฉพาะสมาชิกของคลาสฐานเท่านั้นที่จะถูกคัดลอก ข้อมูลของคลาสที่สืบทอดมาจะสูญหายไป และการเรียกใช้ฟังก์ชันเสมือน (virtual dispatch) จะเรียกใช้ฟังก์ชันของคลาสฐานแทน

**🎯 แนวคิดสำคัญ:**
- Object slicing mechanism (กลไกการเฉือนออบเจกต์)
- Value vs reference semantics (ความหมายแบบค่าเทียบกับแบบอ้างอิง)
- Virtual function dispatch (การส่งฟังก์ชันเสมือน)
- Memory layout differences (ความแตกต่างของการจัดวางหน่วยความจำ)

### วิธีแก้ไข

ส่งผ่านแบบอ้างอิง (pass by reference) เพื่อรักษาความเป็นพหุสัณฐาน:

```cpp
// ✅ ถูกต้อง: การส่งผ่านแบบอ้างอิงช่วยรักษาความเป็นพหุสัณฐาน
void processPhase(const phaseModel& phase) {  // อ้างอิงไปยังออบเจกต์จริง
    phase.correct();  // เรียกใช้การทำงานของคลาสที่สืบทอดมาผ่าน virtual dispatch
}
```

**📚 แหล่งที่มา:**
แนวทางปฏิบัติที่ดีที่สุดมาตรฐานของ C++ - ใช้ทั่วทั้งโค้ดเบสของ OpenFOAM

**💡 คำอธิบาย:**
การส่งผ่านแบบอ้างอิง (`&`) จะหลีกเลี่ยงการคัดลอกและรักษาออบเจกต์ที่สมบูรณ์ไว้ รวมถึงส่วนของคลาสที่สืบทอดมาด้วย การเรียกใช้ฟังก์ชันเสมือนจะส่งไปยังการทำงานของคลาสที่สืบทอดมาได้อย่างถูกต้องผ่านกลไก vtable

**🎯 แนวคิดสำคัญ:**
- Reference semantics (ความหมายแบบอ้างอิง)
- Virtual dispatch tables (ตารางการส่งฟังก์ชันเสมือน)
- const correctness (ความถูกต้องของค่าคงที่)
- Interface-based programming (การโปรแกรมตามอินเทอร์เฟซ)

### แนวทางปฏิบัติที่ดีที่สุด (Best Practice)

ใช้สมาร์ทพอยน์เตอร์ (smart pointers) ทั้งสำหรับพหุสัณฐานและการจัดการความเป็นเจ้าของ:

```cpp
// ⭐ ดีที่สุด: ใช้สมาร์ทพอยน์เตอร์สำหรับการจัดการหน่วยความจำอัตโนมัติ
void processPhase(autoPtr<phaseModel> phase) {
    phase->correct();  // ความหมายความเป็นเจ้าของที่ชัดเจนพร้อมการล้างข้อมูลอัตโนมัติ
}
```

**📚 แหล่งที่มา:**
รูปแบบการจัดการหน่วยความจำของ OpenFOAM - สอดคล้องกับการใช้งาน `autoPtr<T>` ใน `src/OpenFOAM/memory/autoPtr.H`

**💡 คำอธิบาย:**
`autoPtr` ให้ความหมายความเป็นเจ้าของแบบผูกขาดพร้อมการทำลายอัตโนมัติ ตัวดำเนินการลูกศร (`->`) จะเข้าถึงออบเจกต์ในพอยน์เตอร์ในขณะที่ยังคงรักษาความชัดเจนของความเป็นเจ้าของ รูปแบบนี้รวมพหุสัณฐานเข้ากับหลักการ RAII (Resource Acquisition Is Initialization)

**🎯 แนวคิดสำคัญ:**
- RAII idiom (รูปแบบ RAII)
- Exclusive ownership (ความเป็นเจ้าของแบบผูกขาด)
- Automatic resource management (การจัดการทรัพยากรอัตโนมัติ)
- Exception safety (ความปลอดภัยจากข้อยกเว้น)

---

## ข้อผิดพลาดที่ 2: ขาด Destructor เสมือน (Missing Virtual Destructor)

เมื่อใช้คลาสฐานที่มีความเป็นพหุสัณฐาน จำเป็นต้องมี destructor เสมือนเพื่อให้แน่ใจว่ามีการล้างข้อมูลอย่างเหมาะสมเมื่อลบออบเจกต์ที่สืบทอดมาผ่านพอยน์เตอร์ของคลาสฐาน

### ปัญหา

หน่วยความจำรั่วไหลในคลาสที่สืบทอดมา:

```cpp
// ❌ ไม่ถูกต้อง: หน่วยความจำรั่วไหลในคลาสที่สืบทอดมา
class dragModel {
public:
    ~dragModel() {}  // Non-virtual destructor
};

class SchillerNaumann : public dragModel {
    volScalarField* customField_;  // จองหน่วยความจำใน constructor
public:
    ~SchillerNaumann() { delete customField_; }  // ไม่เคยถูกเรียกผ่านพอยน์เตอร์คลาสฐาน
};

// การใช้งาน:
dragModel* model = new SchillerNaumann(dict);
delete model;  // เรียกใช้เพียง dragModel::~dragModel() - หน่วยความจำรั่วไหล!
```

**📚 แหล่งที่มา:**
`.applications/solvers/multiphase/multiphaseEulerFoam/interfacialModels/dragModel/dragModel.H`

**💡 คำอธิบาย:**
การลบออบเจกต์ที่สืบทอดมาผ่านพอยน์เตอร์คลาสฐานโดยไม่มี destructor เสมือนจะทำให้เกิดพฤติกรรมที่ไม่ได้กำหนด (undefined behavior) การทำงานส่วนใหญ่จะเรียกเพียง destructor ของคลาสฐาน ทำให้ทรัพยากรของคลาสที่สืบทอดมารั่วไหล มาตรฐาน C++ ถือว่าสิ่งนี้เป็นพฤติกรรมที่ไม่ได้กำหนด

**🎯 แนวคิดสำคัญ:**
- Destructor dispatch (การส่ง destructor)
- Resource cleanup (การล้างทรัพยากร)
- Undefined behavior (พฤติกรรมที่ไม่ได้กำหนด)
- Memory leak patterns (รูปแบบหน่วยความจำรั่วไหล)

### วิธีแก้ไข

Destructor เสมือนช่วยให้แน่ใจว่ามีการล้างข้อมูลที่ถูกต้อง:

```cpp
// ✅ ถูกต้อง: Destructor เสมือนช่วยให้แน่ใจว่ามีการล้างข้อมูลที่ถูกต้อง
class dragModel {
public:
    virtual ~dragModel() = default;  // Virtual destructor
};
```

**📚 แหล่งที่มา:**
`.applications/solvers/multiphase/multiphaseEulerFoam/interfacialModels/dragModel/dragModel.H` (รูปแบบคลาสฐาน)

**💡 คำอธิบาย:**
การประกาศ `virtual` ช่วยให้แน่ใจว่า destructor ของคลาสที่สืบทอดมาจะถูกเรียกอย่างถูกต้องผ่านพอยน์เตอร์คลาสฐาน ไวยากรณ์ `= default` เป็นการขอให้คอมไพเลอร์สร้างการทำงานของ destructor ให้โดยที่ยังคงรักษาการส่งแบบเสมือนไว้

**🎯 แนวคิดสำคัญ:**
- Virtual destructor declaration (การประกาศ destructor เสมือน)
- Polymorphic deletion safety (ความปลอดภัยในการลบแบบพหุสัณฐาน)
- Compiler-generated defaults (ค่าเริ่มต้นที่คอมไพเลอร์สร้างให้)
- C++11 syntax (ไวยากรณ์ C++11)

**⚠️ ข้อควรจำ:** เมื่อคลาสฐานมีฟังก์ชันเสมือนใดๆ ให้ประกาศ destructor เสมือนเสมอเพื่อหลีกเลี่ยงพฤติกรรมที่ไม่ได้กำหนดและหน่วยความจำรั่วไหล

---

## ข้อผิดพลาดที่ 3: การข้ามระบบ Factory (Bypassing the Factory System)

การสร้างออบเจกต์โดยตรงจะเป็นการข้ามระบบการลงทะเบียน factory ที่ทรงพลังของ OpenFOAM ทำให้สูญเสียประโยชน์ของการขยายขีดความสามารถขณะรันโปรแกรมและการสร้างออบเจกต์ที่ขับเคลื่อนด้วยการกำหนดค่า

### ปัญหา

การสร้างประเภทแบบตายตัว (Hardcoded) ทำให้ต้องแก้ไขโค้ดเมื่อต้องการเพิ่มประเภทใหม่:

```cpp
// ❌ ไม่ถูกต้อง: การสร้างประเภทแบบตายตัว
autoPtr<phaseModel> phase(new purePhaseModel(dict, mesh));
// การเพิ่มประเภทเฟสใหม่ต้องแก้ไขโค้ดทั่วทั้งโค้ดเบส
```

**📚 แหล่งที่มา:**
Anti-pattern - ขัดแย้งกับรูปแบบ factory ใน `MomentumTransferPhaseSystem.C`

**💡 คำอธิบาย:**
การสร้างอินสแตนซ์โดยตรงจะกำหนดประเภทที่แน่นอนลงใน solver ซึ่งละเมิดหลักการ Open-Closed Principle (เปิดสำหรับการขยาย ปิดสำหรับการแก้ไข) ทุกประเภทเฟสใหม่จะต้องการการคอมไพล์โค้ดที่เกี่ยวข้องใหม่

**🎯 แนวคิดสำคัญ:**
- Tight coupling (การผูกมัดที่แน่นหนา)
- Compile-time dependencies (การขึ้นต่อกันเวลาคอมไพล์)
- Violation of Open-Closed Principle (การละเมิดหลักการ Open-Closed)
- Configuration vs hardcoding (การกำหนดค่าเทียบกับการระบุตายตัว)

### วิธีแก้ไข

ใช้เมธอด factory สำหรับการสร้างออบเจกต์ที่ขยายขีดความสามารถได้:

```cpp
// ✅ ถูกต้อง: ใช้เมธอด factory
autoPtr<phaseModel> phase = phaseModel::New(dict, mesh);
// เพิ่มประเภทเฟสใหม่ผ่านการลงทะเบียนเท่านั้น - ไม่ต้องแก้ไขโค้ด
```

**📚 แหล่งที่มา:**
`.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C:56-60`

**💡 คำอธิบาย:**
เมธอด factory แบบสถิต `New()` จะค้นหาชื่อประเภทในตารางการเลือกขณะรันโปรแกรม และเรียกใช้ constructor ที่เหมาะสมผ่านพอยน์เตอร์ฟังก์ชันที่ลงทะเบียนไว้ ประเภทใหม่จะถูกเพิ่มผ่านมาโครการลงทะเบียนเท่านั้นโดยไม่ต้องแก้ไขโค้ดเดิม

**🎯 แนวคิดสำคัญ:**
- Factory method pattern (รูปแบบเมธอดโรงงาน)
- Runtime type lookup (การค้นหาประเภทขณะรันโปรแกรม)
- Registration-based extension (การขยายตามการลงทะเบียน)
- Dictionary-driven instantiation (การสร้างอินสแตนซ์ผ่านพจนานุกรม)

### ประโยชน์ของรูปแบบ Factory

รูปแบบ Factory ช่วยให้:
- สามารถลงทะเบียนประเภทใหม่ขณะรันโปรแกรม
- สร้างออบเจกต์ที่ขับเคลื่อนด้วยพจนานุกรม
- สถาปัตยกรรมที่ขยายออกได้โดยไม่ต้องแก้ไขโค้ดหลัก

---

## ข้อผิดพลาดที่ 4: ลายเซ็น Constructor ไม่ถูกต้อง (Incorrect Constructor Signature)

รูปแบบ factory ต้องการให้คลาสที่สืบทอดมามีลายเซ็น constructor ที่ตรงกับคลาสฐานทุกประการ เพื่อให้สามารถสร้างออบเจกต์ผ่าน `addToRunTimeSelectionTable` ได้สำเร็จ

### ปัญหา

ลายเซ็น Constructor ไม่ตรงกับความต้องการของ factory:

```cpp
// ❌ ไม่ถูกต้อง: ไม่ตรงกับลายเซ็นของ factory
class badPhaseModel : public phaseModel {
public:
    badPhaseModel(const fvMesh& mesh) {}  // ขาดพารามิเตอร์พจนานุกรม
    // addToRunTimeSelectionTable จะล้มเหลวตอนคอมไพล์หรือรันโปรแกรม
};
```

**📚 แหล่งที่มา:**
รูปแบบข้อผิดพลาดที่พบบ่อย - ละเมิดข้อกำหนดลายเซ็นของ factory ในมาโครการลงทะเบียนของ OpenFOAM

**💡 คำอธิบาย:**
ตารางการเลือกขณะรันโปรแกรมจะเก็บพอยน์เตอร์ฟังก์ชัน constructor ที่มีลายเซ็นเฉพาะ ลายเซ็นที่ไม่ตรงกันจะไม่สามารถแปลงเป็นประเภทพอยน์เตอร์ฟังก์ชันที่คาดหวังได้ ทำให้เกิดความล้มเหลวในการคอมไพล์หรือการแครชขณะรันโปรแกรมเมื่อพยายามสร้างอินสแตนซ์

**🎯 แนวคิดสำคัญ:**
- Function pointer types (ประเภทพอยน์เตอร์ฟังก์ชัน)
- Signature matching (การจับคู่ลายเซ็น)
- Type safety in factories (ความปลอดภัยของประเภทในโรงงาน)
- Constructor forwarding (การส่งต่อ constructor)

### วิธีแก้ไข

ทำให้ตรงกับลายเซ็นของ factory คลาสฐานทุกประการ:

```cpp
// ✅ ถูกต้อง: ตรงกับลายเซ็นของ factory คลาสฐานทุกประการ
class goodPhaseModel : public phaseModel {
public:
    goodPhaseModel(const dictionary& dict, const fvMesh& mesh)
    : phaseModel(dict, mesh) {}  // การส่งต่อ constructor คลาสฐานที่เหมาะสม
};
```

**📚 แหล่งที่มา:**
รูปแบบลายเซ็น constructor จากการสร้างโมเดลเฟส

**💡 คำอธิบาย:**
Constructor ของคลาสที่สืบทอดมาต้องรับพารามิเตอร์ที่ตรงตามที่ตาราง factory คาดหวัง และส่งต่อไปยัง constructor ของคลาสฐานผ่าน initialization list สิ่งนี้ช่วยให้แน่ใจว่ามีการเริ่มต้นออบเจกต์ที่เหมาะสมและความเข้ากันได้กับกลไกการเลือกขณะรันโปรแกรม

**🎯 แนวคิดสำคัญ:**
- Constructor delegation (การมอบหมาย constructor)
- Initialization lists (รายการการเริ่มต้น)
- Parameter forwarding (การส่งต่อพารามิเตอร์)
- Base class initialization (การเริ่มต้นคลาสฐาน)

ตารางการเลือกขณะรันโปรแกรมของ OpenFOAM ต้องการการจับคู่ลายเซ็นที่แน่นอน:
- พารามิเตอร์ `const dictionary& dict` สำหรับการกำหนดค่า
- พารามิเตอร์ `const fvMesh& mesh` สำหรับการอ้างอิงเมช
- การส่งต่อ constructor คลาสฐานที่เหมาะสม

สิ่งนี้ช่วยให้แน่ใจว่า factory สามารถสร้างออบเจกต์ได้อย่างสม่ำเสมอผ่านอินเทอร์เฟซ `New(dict, mesh)` ที่ใช้ทั่วทั้งสถาปัตยกรรม solver การไหลหลายเฟสของ OpenFOAM

---

## ข้อผิดพลาดที่ 5: ขาดข้อมูลประเภทขณะรันโปรแกรม (Missing Runtime Type Information)

OpenFOAM ใช้มาโคร `TypeName()` เพื่อระบุประเภทของคลาสขณะรันโปรแกรม การขาดมาโครนี้จะป้องกันไม่ให้ระบบ RTS ค้นหาและสร้างออบเจกต์ได้

### ปัญหา

```cpp
// ❌ ไม่ถูกต้อง: ขาดมาโคร TypeName
class myCustomPhase : public phaseModel {
    // ไม่มีการประกาศ TypeName()
    // ระบบ factory ไม่สามารถระบุประเภทนี้ได้
};
```

**📚 แหล่งที่มา:**
ระบบ OpenFOAM RTTI - นิยามไว้ใน `src/OpenFOAM/db/RunTimeSelections/typeInfo.H`

**💡 คำอธิบาย:**
มาโคร `TypeName()` ประกาศข้อมูลชื่อประเภทแบบสถิตที่ตารางการเลือกขณะรันโปรแกรมใช้สำหรับการค้นหาในพจนานุกรม หากไม่มีมาโครนี้ factory จะไม่สามารถเชื่อมโยงชื่อประเภทในพจนานุกรมกับคลาสที่เป็นรูปธรรมในระหว่างการสร้างอินสแตนซ์ได้

**🎯 แนวคิดสำคัญ:**
- Runtime type identification (การระบุประเภทขณะรันโปรแกรม)
- String-based type lookup (การค้นหาประเภทตามสตริง)
- Static type name storage (การจัดเก็บชื่อประเภทแบบสถิต)
- Factory registration keys (คีย์การลงทะเบียนโรงงาน)

### วิธีแก้ไข

```cpp
// ✅ ถูกต้อง: ประกาศ TypeName ในคลาส
class myCustomPhase : public phaseModel {
public:
    TypeName("myCustomPhase");  // จำเป็นสำหรับ RTS
    // ... การทำงานส่วนที่เหลือ
};
```

**📚 แหล่งที่มา:**
รูปแบบมาตรฐานในคลาสโมเดล OpenFOAM ทั้งหมด (เช่น drag models, phase models)

**💡 คำอธิบาย:**
มาโคร `TypeName("myCustomPhase")` จะขยายตัวเพื่อประกาศ `typeName` แบบสถิตและเมธอดข้อมูลประเภทขณะรันโปรแกรม พารามิเตอร์สตริงต้องตรงกับชื่อประเภทที่ใช้ในพจนานุกรมสำหรับการสร้างอินสแตนซ์

**🎯 แนวคิดสำคัญ:**
- Macro expansion (การขยายมาโคร)
- Static member declaration (การประกาศสมาชิกสถิต)
- Type name string literal (สตริงลิเทอรัลชื่อประเภท)
- Dictionary-to-class mapping (การจับคู่พจนานุกรมกับคลาส)

---

## ข้อผิดพลาดที่ 6: ลืมลงทะเบียนกับตารางการเลือกขณะรันโปรแกรม (Forgetting to Register with Run-Time Selection Table)

หลังจากสร้างคลาสใหม่แล้ว จะต้องลงทะเบียนกับระบบ factory ผ่านมาโคร `addToRunTimeSelectionTable` การขาดการลงทะเบียนนี้จะป้องกันไม่ให้คลาสถูกสร้างอินสแตนซ์ผ่านพจนานุกรม

### ปัญหา

```cpp
// คลาสถูกสร้างอย่างถูกต้องแต่ไม่ได้ลงทะเบียน
class myCustomPhase : public phaseModel {
public:
    TypeName("myCustomPhase");
    myCustomPhase(const dictionary& dict, const fvMesh& mesh);
    // ... ขาดการลงทะเบียนในไฟล์ .C
};

// ในไฟล์ .C ขาด:
// addToRunTimeSelectionTable(phaseModel, myCustomPhase, dictionary);
```

**📚 แหล่งที่มา:**
ข้อผิดพลาดการลงทะเบียนที่พบบ่อย - ละเมิดรูปแบบการขยายของ OpenFOAM

**💡 คำอธิบาย:**
การนิยามคลาสเพียงอย่างเดียวไม่ได้เป็นการเพิ่มคลาสเข้าไปในตารางการเลือกขณะรันโปรแกรม มาโครการลงทะเบียนจะสร้างรายการในตารางสถิตที่จับคู่ชื่อประเภทกับพอยน์เตอร์ฟังก์ชัน constructor หากไม่มีการลงทะเบียน factory จะไม่สามารถหาคลาสได้ในระหว่างการเรียกใช้ `New()`

**🎯 แนวคิดสำคัญ:**
- Static initialization (การเริ่มต้นแบบสถิต)
- Constructor function pointers (พอยน์เตอร์ฟังก์ชัน constructor)
- Table entry creation (การสร้างรายการในตาราง)
- Linkage requirements (ข้อกำหนดการเชื่อมโยง)

### วิธีแก้ไข

```cpp
// ในไฟล์ .C ต้องมีการลงทะเบียน:
addToRunTimeSelectionTable
(
    phaseModel,
    myCustomPhase,
    dictionary
);
```

**📚 แหล่งที่มา:**
`.applications/solvers/multiphase/multiphaseEulerFoam/interfacialModels/dragModel/dragModels/SchillerNaumann/SchillerNaumann.C` (ตัวอย่างการลงทะเบียน)

**💡 คำอธิบาย:**
มาโครนี้จะขยายตัวเป็นโค้ดที่สร้างออบเจกต์สถิตซึ่ง constructor ของมันจะเพิ่มคลาสเข้าไปในตารางการเลือกขณะรันโปรแกรมก่อนที่ `main()` จะทำงาน พารามิเตอร์ทั้งสามระบุคลาสฐาน, คลาสที่สืบทอดมา และประเภทตาราง constructor

**🎯 แนวคิดสำคัญ:**
- Static table population (การเติมข้อมูลตารางสถิต)
- Macro code generation (การสร้างโค้ดผ่านมาโคร)
- Constructor table specification (การระบุตาราง constructor)
- Pre-main initialization (การเริ่มต้นก่อน main)

---

## เทคนิคการดีบัก: การตรวจสอบการลงทะเบียน Factory (Checking Factory Registration)

เมื่อประสบปัญหาเกี่ยวกับการเลือกขณะรันโปรแกรม ให้ใช้ยูทิลิตี้ต่อไปนี้เพื่อตรวจสอบว่าโมเดลใดบ้างที่ได้รับการลงทะเบียน:

```cpp
// Utility to check registration status
template<class BaseType>
void listRegisteredModels() {
    Info << "Registered " << BaseType::typeName << " models:" << nl;
    const auto& table = BaseType::dictionaryConstructorTable();
    forAllConstIter(typename BaseType::dictionaryConstructorTable, table, iter) {
        Info << "  " << iter.key() << nl;
    }
}

// ใช้ในระหว่างการพัฒนา:
listRegisteredModels<phaseModel>();
listRegisteredModels<dragModel>();
```

**📚 แหล่งที่มา:**
รูปแบบยูทิลิตี้ดีบักสำหรับตารางการเลือกขณะรันโปรแกรมของ OpenFOAM

**💡 คำอธิบาย:**
ฟังก์ชันเทมเพลตนี้จะเข้าถึงสมาชิก `dictionaryConstructorTable()` แบบสถิตของคลาสฐาน โดยจะวนลูปผ่านรายการที่ลงทะเบียนไว้ทั้งหมดและพิมพ์คีย์ชื่อประเภทออกมา มีประโยชน์สำหรับการตรวจสอบความสำเร็จของการลงทะเบียนและวินิจฉัยปัญหาของ factory

**🎯 แนวคิดสำคัญ:**
- Template utility functions (ฟังก์ชันยูทิลิตี้เทมเพลต)
- Hash table iteration (การวนลูปตารางแฮช)
- Static member access (การเข้าถึงสมาชิกสถิต)
- Runtime type introspection (การตรวจสอบประเภทขณะรันโปรแกรม)

เมื่อสร้างโมเดลที่กำหนดเอง ให้ทำการตรวจสอบนี้ทันทีหลังจากการคอมไพล์เพื่อยืนยันการลงทะเบียนที่สำเร็จ

---

## สรุปแนวทางปฏิบัติที่ดีที่สุด

1. **ใช้การอ้างอิงหรือพอยน์เตอร์เสมอ** สำหรับการส่งผ่านออบเจกต์พหุสัณฐานเพื่อหลีกเลี่ยงการเฉือนออบเจกต์

2. **ประกาศ Destructor เสมือน** ในทุกคลาสฐานที่มีฟังก์ชันเสมือน

3. **ใช้เมธอด Factory** (`New()`) แทนการสร้างออบเจกต์โดยตรง

4. **ตรวจสอบลายเซ็น Constructor** ว่าตรงตามความต้องการของตาราง factory ทุกประการ

5. **ใช้มาโคร TypeName** สำหรับข้อมูลประเภทขณะรันโปรแกรม

6. **ลงทะเบียนด้วย addToRunTimeSelectionTable** ในไฟล์ .C สำหรับคลาสที่สืบทอดมาทั้งหมด

7. **ตรวจสอบการลงทะเบียน** หลังจากการคอมไพล์เพื่อยืนยันว่าโมเดลถูกเพิ่มเข้าไปในตารางการเลือกขณะรันโปรแกรมแล้ว

8. **ใช้สมาร์ทพอยน์เตอร์** (`autoPtr`, `tmp`) เพื่อการจัดการหน่วยความจำที่ปลอดภัย
