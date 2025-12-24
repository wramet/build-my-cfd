## 4️⃣ กลไก: การสืบทอดและฟังก์ชันเสมือน

### 🏗️ **การออกแบบลำดับชั้นคลาส**

ระบบ transport model ของ OpenFOAM ใช้ลำดับชั้นคลาสที่ซับซ้อนซึ่งให้ความยืดหยุ่นและสามารถขยายได้ ในพื้นฐานจะมี `viscosityModel` ซึ่งเป็น abstract base class ที่กำหนด interface ที่ viscosity models ทั้งหมดต้อง implement รูปแบบการสืบทอดนี้ช่วยให้ OpenFOAM สามารถจัดการ viscosity models ทั้งหมดอย่างสม่ำเสมอในขณะที่ยังคงให้การ implement แต่ละอันมีพฤติกรรมเฉพาะตัว

ลำดับชั้นจะใช้รูปแบบการออกแบบแบบ object-oriented แบบคลาสสิก:

```cpp
class viscosityModel
{
    // Abstract base class กับ pure virtual functions
    virtual ~viscosityModel() {}
    
    // Interface ที่ derived classes ทั้งหมดต้อง implement
    virtual tmp<volScalarField> nu() const = 0;
    virtual void correct() = 0;
    // ... ฟังก์ชันเสมือนอื่นๆ
};

class constantViscosity : public viscosityModel
{
    // Concrete implementation สำหรับค่าความหนืดคงที่
    virtual tmp<volScalarField> nu() const override;
    virtual void correct() override;
};

class powerLawViscosity : public viscosityModel  
{
    // โมเดล non-Newtonian แบบกำหนดเองของเรา
    virtual tmp<volScalarField> nu() const override;
    virtual void correct() override;
};
```

การออกแบบนี้ทำให้เกิด **polymorphism** - OpenFOAM สามารถเรียก `nu()` หรือ `correct()` บนออบเจ็กต์ viscosity model ใดๆ โดยไม่ต้องรู้ประเภทจริงของมัน กลไก runtime dispatch จะทำให้แน่ใจว่า implementation ที่เหมาะสมจะถูกเรียกตามประเภทออบเจ็กต์จริง

### 🔌 **สัญญา Interface เสมือน**

Abstract base class สร้าง **สัญญา** ผ่าน pure virtual functions ที่รับประกันพฤติกรรมที่สม่ำเสมอใน implementations ทั้งหมด:

```cpp
// Interface หลักที่ต้อง implement โดย derived classes
virtual bool read() = 0;
virtual tmp<volScalarField> nu() const = 0;
virtual tmp<scalarField> nu(const label patchi) const = 0;
virtual void correct() = 0;
```

**การแยกส่วนสัญญา:**

- `read()`: อนุญาตให้อ่านพารามิเตอร์โมเดลจาก input dictionaries ในระหว่าง runtime
- `nu()`: ส่งคืนฟิลด์ความหนืดเชิงจลน์สำหรับโดเมนการคำนวณทั้งหมด
- `nu(const label patchi)`: ส่งคืนค่าความหนืดโดยเฉพาะสำหรับ boundary patches
- `correct()`: อัปเดตสถานะโมเดล (สำคัญสำหรับโมเดล non-Newtonian ที่ความหนืดขึ้นกับสถานะการไหล)

ไวยากรณ์ `= 0` ทำให้เป็น **pure virtual functions** ซึ่งหมายความว่า:
1. Base class ไม่สามารถ instantiated โดยตรง
2. Derived classes ต้องให้ implementations
3. การบังคับใช้สัญญา interface ในระหว่าง compile-time

การออกแบบนี้ป้องกัน implementations ที่ไม่สมบูรณ์และทำให้แน่ใจว่า viscosity models ทั้งหมดให้ฟังก์ชันพื้นฐานที่ OpenFOAM's solver infrastructure คาดหวัง

### 🏭 **ความมหัศจรรย์ของ Factory Registration**

OpenFOAM ใช้ **factory pattern** ที่ซับซ้อนซึ่งช่วยให้สามารถเลือกโมเดลใน runtime ผ่าน dictionary keywords กลไกการจดทะเบียนที่สำคัญ:

```cpp
addToRunTimeSelectionTable
(
    viscosityModel,      // Base class สำหรับ factory
    powerLawViscosity,   // Concrete implementation ของเรา  
    dictionary           // Constructor signature type
);
```

**macro นี้จะขยายเพื่อสร้าง infrastructure ของ factory:**

```cpp
// การขยายตัวของ macro แบบทำให้เข้าใจง่าย
namespace Foam
{
    typedef viscosityModel::adddictionaryConstructorToTable<powerLawViscosity>
        addpowerLawViscosityToviscosityModelTable;
    
    // ออบเจ็กต์การจดทะเบียนแบบ global ที่ execute ที่ startup
    addpowerLawViscosityToviscosityModelTable 
        addpowerLawViscosityToviscosityModelTable_;
}
```

**ความมหัศจรรย์เกิดขึ้นใน 3 ระยะ:**

1. **Compile-time**: macro สร้าง static constructor functions และสร้าง registration object
2. **Program startup**: static constructors execute, จดทะเบียนคลาสใน global lookup table ภายใต้ชื่อ "powerLaw"
3. **Runtime**: เมื่อ OpenFOAM พบ `viscosityModel powerLaw;` ใน dictionary มันจะ:
   - ค้นหา "powerLaw" ใน registration table
   - เรียก constructor ที่จดทะเบียนด้วย dictionary
   - ส่งคืน pointer ไปยังออบเจ็กต์ที่สร้างขึ้น

ระบบนี้ทำให้เกิด **extensible architecture** ที่สามารถเพิ่มโมเดลใหม่โดยไม่ต้องแก้ไข core OpenFOAM code เพียง compile โมเดลใหม่ของคุณกับ registration macro และมันจะพร้อมใช้งานสำหรับ solvers ทั้งหมด

### 🧬 **การใช้ Template ใน Field Operations**

ระบบ template ที่กว้างขวางของ OpenFOAM ให้ความปลอดภัยของประเภทและการปรับให้เหมาะสมด้านประสิทธิภาพสำหรับ field operations:

```cpp
tmp<volScalarField>          // ฟิลด์ความหนืดเชิงจลน์ (ฟิลด์สเกลาร์ 3 มิติ)
tmp<scalarField>             // ค่าสเกลาร์บน patches (อาร์เรย์ 1 มิติ)  
tmp<volTensorField>          // ฟิลด์เทนเซอร์ (เช่น เทนเซอร์ความเครียด)
tmp<volVectorField>          // ฟิลด์เวคเตอร์ (เช่น ฟิลด์ความเร็ว)
```

**การแยกส่วนลำดับชั้น template:**

- `Field<Type>`: template สำหรับอาร์เรย์ของออบเจ็กต์ทางเรขาคณิต
  - `scalarField`: อาร์เรย์ของค่าสเกลาร์
  - `vectorField`: อาร์เรย์ของเวคเตอร์ 3 มิติ  
  - `tensorField`: อาร์เรย์ของเทนเซอร์ 3×3

- `GeometricField<Type, PatchField, GeoMesh>`: template สำหรับฟิลด์ที่มี mesh topology
  - `volScalarField`: ฟิลด์สเกลาร์ที่กำหนดที่ cell centers
  - `volVectorField`: ฟิลด์เวคเตอร์ที่กำหนดที่ cell centers
  - `surfaceScalarField`: ฟิลด์สเกลาร์ที่กำหนดบน cell faces

**`tmp` smart pointer template ให้การจัดการหน่วยความจำอัตโนมัติ:**

```cpp
// การนับการอ้างอิงอัตโนมัติป้องกัน memory leaks
tmp<volScalarField> nuField = nu();  // สร้างฟิลด์ที่มี reference count = 1
volScalarField& fieldRef = nuField();  // การอ้างอิงโดยไม่มีความเป็นเจ้าของ
return nuField;  // Reference count ลดลง, หน่วยความจำถูกปลดปล่อยถ้า = 0
```

**ข้อดีของ template ใน OpenFOAM:**

1. **ความปลอดภัยของประเภท**: การตรวจสอบ compile-time ทำให้มั่นใจว่า field operations มีความสอดคล้องกันมิติ
2. **ประสิทธิภาพ**: Template specialization สร้างโค้ดที่ปรับให้เหมาะสมสำหรับแต่ละประเภทฟิลด์
3. **การนำกลับมาใช้ใหม่ของโค้ด**: อัลกอริทึมเดียวกันทำงานได้กับสเกลาร์, เวคเตอร์, และเทนเซอร์
4. **ประสิทธิภาพหน่วยความจำ**: Smart pointers ป้องกันการคัดลอกที่ไม่จำเป็นและจัดการการล้างข้อมูล

สถาปัตยกรรม template นี้ทำให้ OpenFOAM สามารถจัดการการจำลองหลายฟิสิกส์ที่ซับซ้อนในขณะที่ยังคงรักษาประสิทธิภาพการคำนวณที่สูงและป้องกันข้อผิดพลาดในการเขียนโปรแกรมทั่วไป
