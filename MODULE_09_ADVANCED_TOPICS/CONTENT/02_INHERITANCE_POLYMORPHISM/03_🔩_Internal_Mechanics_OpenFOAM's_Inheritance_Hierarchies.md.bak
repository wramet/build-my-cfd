## 🔩 กลไกภายใน: ลำดับชั้นการสืบทอดของ OpenFOAM

### แบบแผนระบบหลายเฟส

สถาปัตยกรรมของ multiphase solver ใน OpenFOAM แสดงให้เห็นถึงการใช้งานลำดับชั้นการสืบทอดที่ซับซ้อนในการจำลองระบบทางกายภาพที่ซับซ้อน ลำดับชั้นหลักใน `multiphaseEulerFoam` ถูกสร้างขึ้นรอบๆ `phaseModel` abstract base class ซึ่งเป็นตัวอย่างที่ชัดเจนของหลักการออกแบบเชิงวัตถุสำหรับแอปพลิเคชัน CFD

คลาส `phaseModel` ทำหน้าที่เป็นพื้นฐานในการแสดงถึงเฟสแต่ละเฟสในการไหลแบบหลายเฟส:

```cpp
// Core hierarchy from multiphaseEulerFoam
class phaseModel                        // Abstract: "IS-A field with phase properties"
    : public volScalarField             // IS-A: Phase fraction field
    , public dictionary                 // IS-A: Configuration container
{
protected:                              // Protected constructor enforces factory pattern
    phaseModel(const dictionary& dict, const fvMesh& mesh);

public:
    // Pure virtual interface - derived MUST implement
    virtual tmp<volScalarField> rho() const = 0;
    virtual tmp<volScalarField> mu() const = 0;
    virtual tmp<volScalarField> Cp() const = 0;

    // Template Method pattern - algorithm skeleton
    virtual void correct();             // Can be overridden
};
```

การออกแบบนี้แสดงให้เห็นถึงหลักการ **"is-a relationship"** - phase model **คือ** ทั้ง volumetric scalar field (แทน phase fraction) และ dictionary (บรรจุพารามิเตอร์การกำหนดค่า) Constructor แบบ protected บังคับให้ใช้ **factory pattern** ทำให้มั่นใจได้ว่า phase models ถูกสร้างขึ้นผ่านกลไกที่ควบคุมแทนการสร้างแบบตรง

Interface แบบ pure virtual บังคับให้คลาสที่สืบทอดต้อง implement คุณสมบัติทาง thermophysical ที่จำเป็น:
- `$\rho$` - ความหนาแน่น
- `$\mu$` - ความหนืดแบบพลศาสตร์  
- `$C_p$` - ความจุความร้อนจำเพาะ

เมธอด `correct()` ตาม **Template Method pattern** โดยให้โครงสร้างอัลกอริทึมเริ่มต้นที่คลาสที่สืบทอดสามารถปรับแต่งได้ขณะที่ยังคงพฤติกรรมที่สม่ำเสมอในลำดับชั้น

การ implement แบบ concrete เชี่ยวชาญสำหรับประเภทต่างๆ ของเฟส:

```cpp
class purePhaseModel : public phaseModel { 
    // Uniform properties across the entire phase field
    // Properties are constants or simple functions of temperature/pressure
};

class mixturePhaseModel : public phaseModel { 
    // Species-weighted properties calculated from mixture composition
    // Properties vary based on local species concentrations
};
```

### การสืบทอดหลายครั้ง: การแก้ปัญหา "Diamond Problem"

OpenFOAM ใช้ **non-virtual multiple inheritance** อย่างมีกลยุทธ์ในการรวมความสามารถที่ไม่ทับซ้อนกันโดยไม่มีความกำกวม แนวทางนี้เห็นได้ชัดเจนในลำดับชั้นประเภทฟิลด์:

```cpp
class GeometricField
    : public DimensionedField    // Mathematical field operations
    , public refCount            // Memory management (RAII)
{
    // No ambiguity: DimensionedField and refCount have no common ancestors
    // Each base provides distinct capability set
};
```

**Architecture Insight**: การออกแบบของ OpenFOAM แยกความกังวลออกจากกันอย่างระมัดระวังเพื่อให้การสืบทอดหลายครั้งรวมฟังก์ชันการทำงานที่เสริมกันแทนที่จะสร้างความขัดแย้ง คลาสพื้นฐานแต่ละคลาสแสดงถึงแง่มุมอิสระ:

- **DimensionedField**: ให้การดำเนินการทางคณิตศาสตร์ รูปแบบการกระจาย และ calculus ของฟิลด์
- **refCount**: Implement reference-counted memory management ตามหลักการ RAII

ลำดับชั้นการสืบทอดดำเนินต่อขึ้นไป:

```cpp
// phaseModel inherits from volScalarField which inherits from GeometricField
// Result: phaseModel gets mathematical operations + memory management + I/O
```

นี่สร้าง **capability composition** ที่:
- `phaseModel` ได้รับการดำเนินการทางคณิตศาสตร์ของฟิลด์จาก `volScalarField`
- `phaseModel` ได้รับการจัดเก็บการกำหนดค่าจาก `dictionary`
- `volScalarField` ได้รับความสามารถในการกระจายจาก `GeometricField`
- `GeometricField` ได้รับการจัดการหน่วยความจำจาก `refCount`

**Key Insight**: นี่คือ **implementation inheritance** (นำกลับมาใช้ใหม่) ไม่ใช่ **interface inheritance** (polymorphism) พฤติกรรมแบบ polymorphic มาจาก virtual functions ของ `phaseModel` ไม่ใช่จาก `volScalarField` การสืบทอดหลายครั้งให้การนำกลับมาใช้ใหม่ของ implementation ขณะที่ยังคงรักษา polymorphic interfaces ที่สะอาดผ่านกลไก virtual function

การออกแบบนี้อนุญาตให้ OpenFOAM สามารถ:
1. **นำโค้ดกลับมาใช้ใหม่**: กำจัดการซ้ำซ้อนของการดำเนินการฟิลด์และการจัดการหน่วยความจำ
2. **รักษาความปลอดภัยของประเภท**: การตรวจสอบเวลา compile ของการดำเนินการฟิลด์
3. **เปิดใช้งาน Polymorphism**: ประเภทเฟสต่างๆ สามารถถูกจัดการอย่างสม่ำเสมอผ่าน pointers ของคลาสพื้นฐาน
4. **รักษาประสิทธิภาพ**: การเรียก virtual function ถูกจำกัดไว้เฉพาะการคำนวณคุณสมบัติ thermophysical ไม่ใช่การดำเนินการฟิลด์พื้นฐาน

สถาปัตยกรรมผลลัพธ์รองรับการจำลองแบบหลายเฟสที่ซับซ้อนขณะที่ยังคงการแยกความกังวลที่สะอาดและการใช้หน่วยความจำที่มีประสิทธิภาพผ่านกลไก `tmp` และ `autoPtr` แบบ reference-counted ของ OpenFOAM
