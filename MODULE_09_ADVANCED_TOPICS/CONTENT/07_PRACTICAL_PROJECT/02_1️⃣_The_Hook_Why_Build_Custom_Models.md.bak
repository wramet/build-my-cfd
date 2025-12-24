## 1️⃣ "Hook": ทำไมต้องสร้างแบบจำลองแบบกำหนดเอง?

### 🧠 **แบบจำลองทางความคิด: การสร้างชิ้นส่วนเครื่องยนต์แบบกำหนดเอง**

จินตนาการว่าคุณกำลังออกแบบเครื่องยนต์ประสิทธิภาพสูง OpenFOAM มอบ **ส่วนตัวเครื่องยนต์** (core framework), **ลูกสูบมาตรฐาน** (built-in models), และ **คู่มือการประกอบ** (APIs) ตอนนี้คุณต้องการ **เทอร์โบชาร์จแบบกำหนดเอง** (specialized physics) ที่ต้อง:

1. **เชื่อมต่อกับที่วางแบบมาตรฐาน** (สืบทอดจาก interface ฐาน)
2. **ใช้ท่อน้ำมันเชื้อเพลิงมาตรฐาน** (ทำงานกับ fields ของ OpenFOAM)
3. **เลือกผ่านควบคุมบนแผงควบคุม** (การเลือก dictionary ขณะรันไทม์)
4. **ทำตามข้อกำหนดโรงงาน** (คอมไพล์กับระบบ build ของ OpenFOAM)

โปรเจกต์นี้สอนคุณในการสร้างเทอร์โบชาร์จนั้น—แบบจำลองความหนืดแบบกำหนดเองที่บูรณาการเข้ากับสถาปัตยกรรมของ OpenFOAM อย่างราบรื่น

### 🔧 **ปัญหาการขยายตัวที่ OpenFOAM แก้ไข**

OpenFOAM ต้องรองรับ:
- **การเลือกแบบจำลองขณะรันไทม์** ผ่านไฟล์ dictionary (ไม่ต้องคอมไพล์ใหม่)
- **การสนับสนุนจากผู้ใช้** โดยไม่ต้องแก้ไขโค้ดหลัก
- **ความเข้ากันได้แบบย้อนหลัง** กับไฟล์ case ที่มีอยู่
- **ประสิทธิภาพ** ผ่านการปรับแต่งขณะคอมไพล์

**วิธีแก้ไข**: **รูปแบบ factory** กับตารางการเลือกขณะรันไทม์ การดำเนินการ field แบบ template-based และลำดับชั้นการสืบทอดที่ชัดเจน

### 🏗️ **กรอบงานสถาปัตยกรรมของ OpenFOAM**

ในแกนกลาง OpenFOAM แก้ปัญหาการขยายตัวผ่านรูปแบบการออกแบบหลายอย่าง:

#### ตารางการเลือกขณะรันไทม์
กลไก **RTS (Runtime Selection)** ทำให้สามารถโหลดแบบจำลองแบบไดนามิกได้โดยไม่ต้องคอมไพล์ใหม่ พิจารณา dictionary entry ทั่วไปนี้:

```
viscosityModel  myCustomViscosity;

myCustomViscosityCoeffs
{
    viscosityCoeff  0.001;
    temperatureCoeff  0.002;
    referenceTemp  293.15;
}
```

เบื้องหลัง OpenFOAM รักษา **ตารางการเลือกขณะรันไทม์** ที่แต่ละแบบจำลองที่ลงทะเบียนกำหนด:

```cpp
addToRunTimeSelectionTable
(
    viscosityModel,
    myCustomViscosity,
    dictionary
);
```

การเรียก macro นี้ลงทะเบียน `myCustomViscosity` ในตารางส่วนกลางที่ `viscosityModel::New()` สามารถค้นหาได้ขณะรันไทม์

#### การดำเนินการ Field แบบ Template-Based
ประเภท field ของ OpenFOAM ใช้ template อย่างหนักเพื่อประสิทธิภาพขณะรักษาความยืดหยุ่น:

```cpp
// Generic field operations
template<class Type>
void myCustomViscosity::correct()
{
    // Access to current fields
    const volScalarField& T = mesh_.lookupObject<volScalarField>("T");
    const volScalarField& p = mesh_.lookupObject<volScalarField>("p");
    
    // Calculate viscosity with generic field operations
    forAll(mu_, cellI)
    {
        mu_[cellI] = viscosityCoeff_ * exp(temperatureCoeff_ * (T[cellI] - referenceTemp_));
    }
}
```

#### ลำดับชั้นการสืบทอด
ลำดับชั้นคลาสที่ชัดเจนช่วยให้การบูรณาการถูกต้อง:

```cpp
// Base class
class viscosityModel
{
public:
    // Runtime selection interface
    static autoPtr<viscosityModel> New(const volVectorField&, const dictionary&);
    
    // Pure virtual interface
    virtual tmp<volScalarField> mu() const = 0;
    virtual void correct() = 0;
    virtual ~viscosityModel() = default;
};

// Our custom implementation
class myCustomViscosity
:
    public viscosityModel
{
    // Implementation details
    // Overrides of virtual methods
    // Custom member variables
};
```

### 🎯 **การประยุกต์ใช้ในจริง**

แบบจำลองแบบกำหนดเองจำเป็นเมื่อ:

1. **ฟิสิกส์เฉพาะทาง**: ของไหล Non-Newtonian วัสดุพิเศษ หรือปฏิสัมพันธ์หลายเฟสที่ไม่ครอบคลุมโดยแบบจำลองมาตรฐาน
2. **ความต้องการด้านการวิจัย**: การนำแบบจำลองทฤษฎีใหม่หรือสหสัมพันธ์ทดลองมาใช้
3. **การปรับแต่งประสิทธิภาพ**: การปรับแต่งเฉพาะโดเมนสำหรับการคำนวณซ้ำๆ
4. **การบูรณาการระบบเดิม**: การนำแบบจำลอง proprietary ที่มีอยู่เข้าสู่เวิร์กโฟลว์ของ OpenFOAM

### 📊 **ประโยชน์การบูรณาการ**

เมื่อสร้างอย่างถูกต้อง แบบจำลองแบบกำหนดเองจะได้รับ:

- **ประสิทธิภาพเนทีฟ**: การปรับแต่งขณะคอมไพล์เท่ากับแบบจำลองในตัว
- **การใช้งานโปร่งใส**: ไวยากรณ์ dictionary เดียวกันและประสบการณ์ผู้ใช้เดิม
- **API สอดคล้อง**: การเข้าถึงการดำเนินการ field และอรรถประโยชน์ mesh ทั้งหมดของ OpenFOAM
- **ความสามารถขนาน**: การขนาน MPI อัตโนมัติผ่านคลาส field ของ OpenFOAM
- **การบูรณาการหลังประมวลผล**: ทำงานร่วมกับ paraFoam, sample และอรรถประโยชน์อื่นๆ อย่างราบรื่น

### 🔄 **ขั้นตอนการพัฒนา**

กระบวนการพัฒนาแบบจำลองแบบกำหนดเองโดยทั่วไปจะเป็น:

1. **ขั้นตอนการออกแบบ**: กำหนดความต้องการด้านฟิสิกส์และการกำหนดสูตรคณิตศาสตร์
2. **การสร้าง**: สร้างคลาสที่สืบทอดจากคลาสฐานที่เหมาะสม
3. **การลงทะเบียน**: เพิ่ม macro การเลือกขณะรันไทม์
4. **การคอมไพล์**: บูรณาการกับระบบ build ของ OpenFOAM (`wmake`)
5. **การทดสอบ**: ตรวจสอบกับวิธีแก้วิเคราะห์หรือข้อมูลทดลอง
6. **การจัดทำเอกสาร**: สร้างเอกสารผู้ใช้และ case ตัวอย่าง

แนวทางเชิงระบบนี้ช่วยให้แน่ใจว่าแบบจำลองแบบกำหนดเองบูรณาการอย่างราบรื่นขณะรักษามาตรฐานคุณภาพและประสิทธิภาพที่คาดหวังในเวิร์กโฟลว์ CFD ระดับมืออาชีพ
