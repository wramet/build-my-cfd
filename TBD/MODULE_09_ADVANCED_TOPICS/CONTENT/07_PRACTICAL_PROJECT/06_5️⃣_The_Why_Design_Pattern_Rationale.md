## 5️⃣ "Why": หลักการออกแบบ Pattern

### 🏭 **Factory Pattern: สนามทดลองการเขียนโค้ดของผู้ใช้เทียบกับเสถียรภาพของคลังหลัก**

Factory Pattern ใน OpenFOAM แสดงถึงวิธีแก้ปัญหาที่สวยงามสำหรับความท้าทายพื้นฐานของวิศวกรรมซอฟต์แวร์ในเฟรมเวิร์ก CFD: การเปิดใช้งานความสามารถในการขยายตัวในขณะที่รักษาเสถียรภาพของคลังหลัก

**ปัญหาหลัก**: แอปพลิเคชันพลศาสตร์ของไหลเชิงคำนวณต้องการให้ผู้ใช้ implement แบบจำลองฟิสิกส์แบบกำหนดเอง (turbulence closures, thermophysical properties, reaction mechanisms, เป็นต้น) หากไม่มี architectural pattern ที่เหมาะสม สิ่งนี้จะต้องการ:

1. **การแก้ไขคลังหลักโดยตรง**: ผู้ใช้จำเป็นต้องแก้ไขไฟล์ซอร์ส OpenFOAM โดยตรง
2. **การคอมไพล์ใหม่ทั้งหมด**: การเพิ่มแบบจำลองแบบกำหนดเองหนึ่งรายการจำเป็นต้องสร้างคลัง OpenFOAM ทั้งหมดใหม่
3. **การทำลายความเข้ากันได้**: การเปลี่ยนแปลงอาจทำให้การจำลองหรือไฟล์ case ที่มีอยู่ใช้ไม่ได้
4. **ความสับสนของการควบคุมเวอร์ชัน**: การผสานการแก้ไขคลังหลักระหว่างการอัปเดต OpenFOAM จะกลายเป็นปัญหา

**การแก้ปัญหาของ Factory**: ตารางการเลือกขณะ runtime สร้าง **sandbox architecture** ที่แยกความรับผิดชอบออกจากกันอย่างชัดเจน:

#### ความรับผิดชอบของคลังหลัก
```cpp
// Abstract base class กำหนด interface
class turbulenceModel
{
public:
    // Factory method สำหรับการสร้างขณะ runtime
    static autoPtr<turbulenceModel> New
    (
        const volVectorField& U,
        const surfaceScalarField& phi,
        const word& modelType
    );
    
    // Pure virtual interface
    virtual tmp<volSymmTensorField> devReff() const = 0;
    virtual void correct() = 0;
};
```

#### การ implement โค้ดของผู้ใช้
```cpp
// ผู้ใช้ implement ฟิสิกส์เฉพาะ
class myCustomTurbulenceModel : public turbulenceModel
{
public:
    // Constructor พร้อมการลงทะเบียนประเภทขณะ runtime
    TypeName("myCustomTurbulence");
    
    myCustomTurbulenceModel
    (
        const volVectorField& U,
        const surfaceScalarField& phi
    );
    
    // การ implement ของ virtual interface
    virtual tmp<volSymmTensorField> devReff() const override;
    virtual void correct() override;
};

// Registration macro เชื่อมโยงชื่อกับ constructor
addToRunTimeSelectionTable
(
    turbulenceModel,
    myCustomTurbulenceModel,
    dictionary
);
```

### 📚 **การแยกความรับผิดชอบ**

สถาปัตยกรรมนี้สร้างสัญญาที่ชัดเจนระหว่างคอมโพเนนต์ต่างๆ:

| คอมโพเนนต์ | ความรับผิดชอบหลัก | ตำแหน่งทั่วไป | ประโยชน์หลัก |
|-----------|----------------------|------------------|--------------|
| **Base Class** | กำหนด abstract interface, ลายเซ็น factory method, โครงสร้างข้อมูลทั่วไป | คลังหลัก OpenFOAM (`$FOAM_SRC/`) | รับประกัน API ที่สอดคล้องกัน, ทำให้ polymorphism เป็นไปได้, จัดเตรียมโครงสร้างพื้นฐาน factory |
| **Concrete Class** | Implement ฟิสิกส์/คณิตศาสตร์เฉพาะ, การลงทะเบียนด้วยตนเอง, การแยกวิเคราะห์พารามิเตอร์ | คลังผู้ใช้ (`$FOAM_USER_APPBIN/`) | ห่อหุ้มรายละเอียดฟิสิกส์, คอมไพล์ใหม่ได้โดยอิสระ, ควบคุมเวอร์ชันได้ |
| **Factory System** | การค้นหาประเภทขณะ runtime, การแมป constructor, การจัดการวงจรชีวิตของออบเจกต์ | ระบบรีจิสทรี OpenFOAM (`src/OpenFOAM/db/runTimeSelection/`) | แยกการเลือกจากการ implement, จัดการการจัดการหน่วยความจำ, เปิดใช้งานการโหลดแบบไดนามิก |
| **Dictionary Files** | การเลือกแบบจำลอง, การกำหนดค่าพารามิเตอร์, การตั้งค่าเฉพาะ case | ไฟล์ case (`system/`, `constant/`) | อนุญาตการกำหนดค่าขณะ runtime, ช่วยในการศึกษาพารามิเตอร์, แยกฟิสิกส์จากการตั้งค่า case |

### 🔄 **สถาปัตยกรรมปลั๊กอินของ OpenFOAM**

การ implement Factory Pattern นี้เปิดใช้งาน **plugin-like extensibility** ของ OpenFOAM ผ่านกลไกการเลือกขณะ runtime ที่ซับซ้อน:

#### ขั้นที่ 1: การคอมไพล์แยกกัน
แบบจำลองแบบกำหนดเองถูกคอมไพล์เป็นคลังอิสระ:
```bash
# ผู้ใช้คอมไพล์แบบจำลองแบบกำหนดเองแยกกัน
wmake libso
```

#### ขั้นที่ 2: การโหลดขณะ runtime
คลังถูกโหลดแบบไดนามิกเมื่อจำเป็น:
```cpp
// OpenFOAM's runtime loader
externalLibs libs
{
    libmyCustomModels.so;
}
```

#### ขั้นที่ 3: การเลือก Dictionary
แบบจำลองถูกเลือกผ่านการกำหนดค่า case:
```cpp
// In case file: system/controlDict or constant/turbulenceProperties
simulationType  RAS;
RAS
{
    RASModel        myCustomTurbulence;
    turbulence      on;
    // พารามิเตอร์แบบจำลองแบบกำหนดเอง
    Cmu             0.09;
    kappa           0.41;
    // พารามิเตอร์แบบกำหนดเองเพิ่มเติม
    customParameter 1.23;
}
```

#### ขั้นที่ 4: การสร้างอินสแตนซ์และการดำเนินการ
ระบบ factory จัดการการสร้างออบเจกต์:
```cpp
// การสร้างขณะ runtime ตามรายการ dictionary
autoPtr<turbulenceModel> turbulence
(
    turbulenceModel::New
    (
        U,
        phi,
        laminarTransport
    )
);

// การใช้แบบ polymorphic
turbulence->correct();
Reff = turbulence->devReff();
```

### 🎯 **ประโยชน์ของสถาปัตยกรรม**

รูปแบบการออกแบบนี้ให้ประโยชน์ที่สำคัญหลายประการ:

#### **ความยืดหยุ่นในการพัฒนา**
- **ไม่มีการแก้ไขคลังหลัก**: ผู้ใช้ไม่ต้องยุ่งกับซอร์สโค้ด OpenFOAM
- **การทดสอบแยกกัน**: แบบจำลองแบบกำหนดเองสามารถพัฒนาและทดสอบแยกจากกันได้
- **การพัฒนาแบบเพิ่มหน่วย**: แบบจำลองใหม่สามารถเพิ่มโดยไม่กระทบฟังก์ชันการทำงานที่มีอยู่

#### **ประสิทธิภาพการดำเนินงาน**
- **การคอมไพล์แบบเลือก**: เฉพาะคอมโพเนนต์ที่เปลี่ยนแปลงเท่านั้นที่ต้องคอมไพล์ใหม่
- **ประสิทธิภาพหน่วยความจำ**: แบบจำลองถูกโหลดเฉพาะเมื่อจำเป็น
- **ประสิทธิภาพ**: ค่าใช้จ่ายของ polymorphism ขณะ runtime เล็กน้อยเมื่อเทียบกับความยืดหยุ่นในการพัฒนา

#### **การบำรุงรักษา**
- **ความเข้ากันได้ของเวอร์ชัน**: แบบจำลองแบบกำหนดเองอยู่รอดการอัปเดต OpenFOAM
- **Interfaces ที่ชัดเจน**: สัญญาที่กำหนดไว้ดีระหว่างคอมโพเนนต์
- **สถาปัตยกรรมแบบโมดูล**: แต่ละคอมโพเนนต์มีความรับผิดชอบเดียว

#### **ความสามารถในการขยายตัว**
- **แบบจำลองแบบลำดับชั้น**: แบบจำลองใหม่สามารถสืบทอดจากแบบจำลองที่มีอยู่ได้
- **การผสานระหว่างโดเมน**: รูปแบบเดียวกันทำงานสำหรับฟิสิกส์, ตัวเลข, meshing, utilities
- **การผสานรวมของบุคคลที่สาม**: ผู้ขายเชิงพาณิชย์สามารถจัดจำหน่ายแบบจำลองกรรมสิทธิ์เป็นปลั๊กอิน

สถาปัตยกรรมที่ใช้ factory เป็นพื้นฐานของความสำเร็จของ OpenFOAM ทั้งในฐานะแพลตฟอร์มการวิจัยและเครื่องมือ CFD สำหรับการผลิต ทำให้สามารถพัฒนาได้ในขณะที่รักษาความเข้ากันได้แบบย้อนหลังและความสามารถในการขยายตัว
