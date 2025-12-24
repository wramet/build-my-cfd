## 💻 ตัวอย่างการใช้งาน vs. ข้อผิดพลาดที่พบบ่อย

### การใช้งานที่ถูกต้อง: การกำหนดค่าแบบ Dictionary-Driven

ในสถาปัตยกรรม multiphase solver ของ OpenFOAM ระบบการกำหนดค่าแบบ dictionary-driven ช่วยให้สามารถสร้าง solver ทั่วไปที่สามารถจัดการกับการกำหนดค่า phase ใดๆ ได้โดยไม่ต้องแก้ไขโค้ด แนวทางนี้สาธิตถึงพลังของ factory pattern ที่รวมกับ runtime polymorphism

phase properties dictionary (`constant/phaseProperties`) กำหนด phases ทั้งหมดและคุณสมบัติทาง thermophysical:

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

โค้ด solver ยังคงเป็นแบบทั่วไปโดยสมบูรณ์ สร้าง phases ที่กำหนดค่าโดยอัตโนมัติผ่านระบบ factory:

```cpp
phaseSystem fluid(mesh);  // สร้าง phases ที่กำหนดค่าโดยอัตโนมัติ
```

รูปแบบการออกแบบนี้ช่วยให้ solver binary ตัวเดียวกันสามารถจัดการกับชุดค่าผสมของ phases ใดๆ ก็ได้ โดยการเพิ่มประเภท phase ใหม่ผ่านการ registration แทนการแก้ไขโค้ด

### ข้อผิดพลาดที่ 1: Object Slicing

Object slicing เป็นข้อผิดพลาด C++ ที่สำคัญที่เกิดขึ้นเมื่ออ็อบเจกต์ของ derived class ถูกส่งผ่านค่าไปยังฟังก์ชันที่คาดหวังอ็อบเจกต์ของ base class สิ่งนี้จะตัดส่วน derived class ทิ้ง ทำให้เกิดพฤติกรรม polymorphic ที่ไม่ถูกต้อง

**ปัญหา**: การส่งผ่านค่าคัดลอกเฉพาะส่วน phaseModel เท่านั้น สูญเสียข้อมูลของ derived class:

```cpp
// ผิด: การส่งผ่านค่าทำให้ derived object ถูกตัดออก
void processPhase(phaseModel phase) {  // คัดลอกเฉพาะส่วน phaseModel เท่านั้น
    phase.correct();  // เรียก phaseModel::correct() เสมอ ไม่ใช่ implementation ของ derived class
}
```

**วิธีแก้ไข**: ส่งผ่าน reference เพื่อรักษา polymorphism:

```cpp
// ถูกต้อง: การส่งผ่าน reference รักษา polymorphism
void processPhase(const phaseModel& phase) {  // Reference ไปยังอ็อบเจกต์จริง
    phase.correct();  // เรียก implementation ของ derived class ผ่าน virtual dispatch
}
```

**Best Practice**: ใช้ smart pointers สำหรับทั้ง polymorphism และการจัดการ ownership:

```cpp
// ดีที่สุด: ใช้ smart pointers
void processPhase(autoPtr<phaseModel> phase) {
    phase->correct();  // รักษาความหมายของ ownership
}
```

### ข้อผิดพลาดที่ 2: การขาด Virtual Destructor

เมื่อใช้ base classes แบบ polymorphic virtual destructor จำเป็นเพื่อให้แน่ใจว่ามีการ cleanup ที่เหมาะสมเมื่อลบอ็อบเจกต์ derived ผ่าน base class pointers

**ปัญหา**: Memory leaks กับ derived classes:

```cpp
// ผิด: Memory leak กับ derived classes
class dragModel {
public:
    ~dragModel() {}  // Non-virtual destructor
};

class SchillerNaumann : public dragModel {
    volScalarField* customField_;  // จัดสรรใน constructor
public:
    ~SchillerNaumann() { delete customField_; }  // ไม่เคยถูกเรียกผ่าน base pointer
};

// การใช้งาน:
dragModel* model = new SchillerNaumann(dict);
delete model;  // เรียกเฉพาะ dragModel::~dragModel() เท่านั้น memory leak!
```

**วิธีแก้ไข**: Virtual destructor ช่วยให้แน่ใจในการ cleanup ที่เหมาะสม:

```cpp
// ถูกต้อง: Virtual destructor ช่วยให้แน่ใจในการ cleanup ที่เหมาะสม
class dragModel {
public:
    virtual ~dragModel() = default;  // Virtual destructor
};
```

### ข้อผิดพลาดที่ 3: การ Bypass ระบบ Factory

การสร้างอ็อบเจกต์โดยตรง bypass ระบบ factory registration ที่ทรงพลังของ OpenFOAM สูญเสียประโยชน์ของ runtime extensibility และการสร้างอ็อบเจกต์ที่ขับเคลื่อนโดย configuration

**ปัญหา**: การสร้างประเภทแบบ hardcoded ต้องการการแก้ไขโค้ดสำหรับประเภทใหม่:

```cpp
// ผิด: การสร้างประเภทแบบ hardcoded
autoPtr<phaseModel> phase(new purePhaseModel(dict, mesh));
// การเพิ่มประเภท phase ใหม่ต้องการการเปลี่ยนแปลงโค้ดทั่วทั้ง codebase
```

**วิธีแก้ไข**: ใช้ factory method สำหรับการสร้างอ็อบเจกต์ที่สามารถขยายได้:

```cpp
// ถูกต้อง: ใช้ factory method
autoPtr<phaseModel> phase = phaseModel::New(dict, mesh);
// ประเภท phase ใหม่ถูกเพิ่มผ่านการ registration เท่านั้น ไม่ต้องการการเปลี่ยนแปลงโค้ด
```

factory pattern ช่วยให้สามารถ:
- ทำ registration ประเภทใหม่ได้ที่ runtime
- การสร้างอ็อบเจกต์ที่ขับเคลื่อนโดย dictionary
- สถาปัตยกรรมที่สามารถขยายได้โดยไม่ต้องแก้ไข core code

### ข้อผิดพลาดที่ 4: Constructor Signature ที่ไม่ถูกต้อง

Factory patterns ต้องการให้ derived classes ตรงกับ constructor signature ของ base class อย่างแม่นยำสำหรับการสร้างอ็อบเจกต์ที่สำเร็จผ่าน `addToRunTimeSelectionTable`

**ปัญหา**: Constructor signature ไม่ตรงกับความต้องการของ factory:

```cpp
// ผิด: ไม่ตรงกับ factory signature
class badPhaseModel : public phaseModel {
public:
    badPhaseModel(const fvMesh& mesh) {}  // ขาดพารามิเตอร์ dictionary
    // addToRunTimeSelectionTable จะล้มเหลวที่การคอมไพล์หรือ runtime
};
```

**วิธีแก้ไข**: ตรงกับ base factory signature อย่างแม่นยำ:

```cpp
// ถูกต้อง: ตรงกับ base factory signature อย่างแม่นยำ
class goodPhaseModel : public phaseModel {
public:
    goodPhaseModel(const dictionary& dict, const fvMesh& mesh)
    : phaseModel(dict, mesh) {}  // การฝาก constructor ที่เหมาะสม
};
```

runtime selection tables ของ OpenFOAM ต้องการการจับคู่ signature อย่างแม่นยำ:
- `const dictionary& dict` parameter สำหรับการกำหนดค่า
- `const fvMesh& mesh` parameter สำหรับ reference ของ mesh
- การฝาก constructor ของ base class ที่เหมาะสม

สิ่งนี้ช่วยให้แน่ใจว่า factory สามารถสร้างอ็อบเจกต์ได้อย่างสม่ำเสมอผ่านอินเตอร์เฟซ `New(dict, mesh)` ที่ใช้ทั่วทั้งสถาปัตยกรรม multiphase solver ของ OpenFOAM
