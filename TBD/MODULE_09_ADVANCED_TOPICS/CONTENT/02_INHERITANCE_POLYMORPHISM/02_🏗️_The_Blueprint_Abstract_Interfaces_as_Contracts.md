## 🏗️ แบบแปลน: Abstract Interfaces เป็นสัญญา

### ทำไมต้องใช้ Pointers ไปยัง Base Classes?

ในการออกแบบซอฟต์แวร์เชิงวัตถุ อินเทอร์เฟซนามธรรมทำหน้าที่เป็นสัญญาที่กำหนดฟังก์ชันการทำงานที่จำเป็นต้องมีโดยไม่ต้องระบุวิธีการ implement รูปแบบการออกแบบนี้เป็นพื้นฐานสำคัญของความยืดหยุ่นและการบำรุงรักษาของ OpenFOAM

```cpp
// BLUEPRINT: Program กับ interfaces ไม่ใช่ implementations
class dragModel  // ข้อกำหนดของ socket นามธรรม
{
public:
    virtual tmp<surfaceScalarField> K() const = 0;  // Pure virtual = รูปแบบ plug ที่ต้องการ
};

// Client code ทำงานกับ drag model ใดๆ ก็ได้
void calculateMomentum(const dragModel& drag)  // ยอมรับ plug ที่เป็นไปตามข้อกำหนด
{
    surfaceScalarField K = drag.K();  // ใช้ socket interface
    // ... momentum calculation
};

// Concrete implementations ให้ฟิสิกส์จริง
class SchillerNaumann : public dragModel { /* implements K() */ };
class Ergun : public dragModel { /* different K() implementation */ };
```

**การเลือกการออกแบบ**: Solver รับ reference ของ `dragModel&` ไม่ใช่ `SchillerNaumann&` ที่เจาะจง ซึ่งช่วยให้:

1. **Algorithm Reuse**: momentum solver เดียวกันทำงานกับ drag laws ทั้งหมดได้
2. **Decoupled Development**: นักพัฒนา model ฟิสิกส์ไม่ต้องเข้าใจภายใน solver
3. **Runtime Flexibility**: เลือก model ได้ในช่วงตั้งค่า case

การเลือกสถาปัตยกรรมนี้ตาม **Dependency Inversion Principle** จากหลักการ SOLID: high-level modules ไม่ควรพึ่งพา low-level modules แต่ทั้งสองควรพึ่งพา abstractions ใน OpenFOAM solvers พึ่งพา abstract model interfaces ไม่ใช่ implementations ที่เจาะจง ทำให้สามารถเพิ่ม drag models ใหม่ได้โดยไม่ต้องแก้ไข solver code

**Interface Segregation**: Abstract interfaces ให้สัญญาที่เล็กที่สุดและเฉพาะเจาะจง แต่ละ physics model implement เฉพาะ methods ที่ต้องการ หลีกเลี่ยง "fat interface" problem ที่ classes ถูกบังคับให้ implement methods ที่ไม่ได้ใช้

### Virtual Function Table (vtable) - แผนภูมิการเชื่อมต่อที่ซ่อนอยู่

ทุก abstract base class ที่มี virtual functions จะมี vtable ที่มองไม่เห็นซึ่งทำให้เกิดพฤติกรรม polymorphic กลไกนี้เป็นกระดูกสันหลังของ runtime polymorphism ใน C++ และสำคัญต่อความยืดหยุ่นของ OpenFOAM

```cpp
// Conceptual vtable for dragModel hierarchy
struct dragModel_vtable {
    void (*destructor)(dragModel*);
    tmp<surfaceScalarField> (*K)(const dragModel*);
};

// Each object carries a vtable pointer
class dragModel {
    dragModel_vtable* __vptr;  // Hidden member added by compiler
public:
    virtual ~dragModel() = 0;
    virtual tmp<surfaceScalarField> K() const = 0;
};
```

**สถาปัตยกรรม vtable**:

- **สร้างโดย compiler** ต่อ class type ระหว่าง compilation
- **Array of function pointers** ไปยัง implementations จริง
- **vtable หนึ่งต่อ class** ใช้ร่วมกันโดย instances ทั้งหมด
- **Runtime cost**: pointer dereference พิเศษหนึ่งตัวต่อ virtual call (~5 CPU cycles)

**Memory Layout**:
```
+-------------------+     +---------------------+
| dragModel object  | --> | dragModel vtable    | --> | SchillerNaumann::K() |
+-------------------+     +---------------------+     +----------------------+
| __vptr            |     | destructor()        |     | SchillerNaumann::~() |
| other data        |     | K()                 |     +----------------------+
+-------------------+     +---------------------+
```

**Polymorphic Dispatch Process**:
1. เมื่อเรียก `drag.K()` compiler สร้าง code เพื่อ:
   - Load vtable pointer จาก object (`drag.__vptr`)
   - หาตำแหน่งใน vtable สำหรับ function pointer `K()`
   - กระโดดไปยัง implementation function จริง

**ปัจจัยด้านประสิทธิภาพ**:
- **Overhead**: ~5 CPU cycles ต่อ virtual call
- **Inline Inhibition**: Virtual calls ไม่สามารถ inlined ได้ใน compile time
- **Cache Impact**: Vtable pointers เล็กและ cache-friendly โดยทั่วไป
- **Trade-off**: ต้นทุนประสิทธิภาพเล็กน้อยแต่ได้ code reuse และ flexibility สูง

**Template vs. Virtual**: OpenFOAM มักใช้ templates สำหรับ code ที่ต้องการประสิทธิภาพสูง และ virtual functions สำหรับ configurability Templates ให้ compile-time polymorphism โดยไม่มี runtime overhead ในขณะที่ virtual functions ให้ runtime polymorphism ที่จำเป็นสำหรับ model selection ผ่าน input files

**ตัวอย่างใน OpenFOAM**: ระบบ turbulence modeling ใช้รูปแบบนี้อย่างกว้างขวาง:
```cpp
class turbulenceModel {
public:
    virtual const volScalarField& k() const = 0;
    virtual const volScalarField& epsilon() const = 0;
    virtual tmp<volSymmTensorField> R() const = 0;
};

// Runtime selection works through abstract interface
autoPtr<turbulenceModel> turbulence = turbulenceModel::New(mesh, phi, U);
const volScalarField& turbulentKE = turbulence().k();
```

สถาปัตยกรรมนี้ทำให้ OpenFOAM รองรับ turbulence models ได้หลายสิบรุ่นซึ่งสามารถเลือกได้ใน runtime ผ่าน dictionary entry `turbulenceModel` โดยไม่ต้อง recompile solver
