# 🔧 คู่มือการนำไปใช้งานจริง

## การสร้างโมเดลเฟสแบบกำหนดเอง

การ implement โมเดลเฟสแบบกำหนดเองใน OpenFOAM จำเป็นต้องเข้าใจ Factory Pattern และสถาปัตยกรรม Virtual Interface คลาส `phaseModel` ทำหน้าที่เป็นฐานสำหรับการแสดงเฟสทั้งหมดในการจำลองหลายเฟส โดยให้ส่วนติดต่อมาตรฐานที่เปิดใช้งาน Runtime Polymorphism ผ่านระบบ Factory แบบ Dictionary-based

```cpp
// 1. สืบทอดจาก phaseModel
class myCustomPhaseModel : public phaseModel {
private:
    dimensionedScalar customProperty_;

public:
    // 2. Runtime type information (จำเป็น)
    TypeName("myCustomPhase");

    // 3. Constructor ที่ตรงกับ signature ของ factory (จำเป็น)
    myCustomPhaseModel(const dictionary& dict, const fvMesh& mesh);

    // 4. Implement pure virtual interface (จำเป็น)
    virtual tmp<volScalarField> rho() const override;
    virtual tmp<volScalarField> mu() const override;

    // 5. ไม่จำเป็น: Override template methods
    virtual void correct() override;
};
```

มาโคร `TypeName("myCustomPhase")` สร้างข้อมูลประเภท Runtime ที่ระบบ Factory ของ OpenFOAM ใช้สำหรับการสร้างวัตถุ ซึ่งเปิดใช้งานการสร้างโมเดลเฟสจากรายการ Dictionary โดยไม่ต้องมีความรู้เกี่ยวกับประเภทอย่างชัดเจนในขณะ Compile

Constructor ต้องปฏิบัติตาม signature ที่แน่นอนที่ Factory Pattern กำหนด `dictionaryConstructorTable` ของ OpenFOAM คาดหวัง Constructor ที่สามารถเรียกใช้ได้กับ Dictionary Reference และ Mesh Reference โดยอนุญาตให้มีการสร้างวัตถุที่มีพารามิเตอร์จาก Case Files

```cpp
// 6. Register ในไฟล์ .C (จำเป็น)
addToRunTimeSelectionTable(phaseModel, myCustomPhaseModel, dictionary);
```

มาโครการ Register นี้มีความสำคัญมาก - มันเพิ่มโมเดลเฟสแบบกำหนดเองเข้าไปใน Runtime Selection Table ของ OpenFOAM ซึ่งเปิดใช้งานการค้นพบและการสร้างตัวอย่างโดยอัตโนมัติผ่าน Factory Method `New` โดยไม่มีการ Register นี้ แม้จะ implement โมเดลเฟสอย่างถูกต้องก็ไม่สามารถสร้างตัวอย่างจาก Case Dictionaries ได้

## การสร้างโมเดลอินเตอร์เฟซแบบกำหนดเอง

Interfacial Models implement ฟิสิกส์ระหว่างเฟสต่างๆ เช่น Drag Forces, Heat Transfer หรือ Mass Transfer ส่วนติดต่อโมเดล Drag ใช้ Factory Pattern ที่คล้ายกัน แต่โดยทั่วไปทำงานระหว่าง Phase References สองตัว

```cpp
class myCustomDragModel : public dragModel {
public:
    TypeName("myCustomDrag");

    myCustomDragModel(const dictionary& dict, const phaseModel& phase1,
                      const phaseModel& phase2);

    virtual tmp<surfaceScalarField> K() const override;
};

// Registration สำหรับ factory พารามิเตอร์ 3 ตัว
addToRunTimeSelectionTable(dragModel, myCustomDragModel, dictionary);
```

เมธอด `K()` ส่งคืนสัมประสิทธิ์การแลกเปลี่ยนโมเมนตัมที่ปรากฏในเทอมการถ่ายโอนโมเมนตัมระหว่างอินเตอร์เฟซ $\mathbf{M}_{12} = K_{12}(\mathbf{u}_1 - \mathbf{u}_2$) ฟิลด์ที่ส่งคืนต้องเป็น `surfaceScalarField` เพื่อให้มั่นใจว่ามีการประเมินอย่างถูกต้องที่ศูนย์กลางของ Face ที่เกิดการคำนวณ Flux ระหว่างอินเตอร์เฟซ

Interfacial Models เข้าถึงคุณสมบัติของเฟสผ่าน Phase References ซึ่งเปิดใช้งานการ implement สหสัมพันธ์ที่ซับซ้อนที่ขึ้นอยู่กับความหนาแน่นของเฟส ความหนืด ปริมาตรส่วน และคุณสมบัติการขนส่งอื่นๆ

## การทดสอบการ Register ของ Factory

ระบบ Factory ของ OpenFOAM อาจไม่ชัดเจนในระหว่างการพัฒนา ซึ่งทำให้การตรวจสอบการ Register สำเร็จเป็นสิ่งจำเป็นสำหรับการ Debug เทมเพลต Utility ต่อไปนี้มีวิธีการที่เป็นระบบในการแสดงรายการโมเดลที่ Register ทั้งหมดของ Base Type ที่กำหนด

```cpp
// Utility สำหรับตรวจสอบการ Register
template<class BaseType>
void listRegisteredModels() {
    Info << "Registered " << BaseType::typeName << " models:" << nl;
    const auto& table = BaseType::dictionaryConstructorTable();
    forAllConstIter(typename BaseType::dictionaryConstructorTable, table, iter) {
        Info << "  " << iter.key() << nl;
    }
}
```

เทมเพลตนี้ใช้ Iteration Macros ของ OpenFOAM เพื่อข้ามผ่าน Dictionary Constructor Table ซึ่งเก็บการแม็ประหว่างชื่อโมเดล (Dictionary Keys) และฟังก์ชัน Factory `BaseType::typeName` ให้ชื่อของ Base Class ที่มนุษย์อ่านได้สำหรับการจัดรูปแบบผลลัพธ์ที่ชัดเจน

```cpp
// ใช้ในการพัฒนา
listRegisteredModels<phaseModel>();
listRegisteredModels<dragModel>();
```

เมื่อ implement โมเดลแบบกำหนดเอง ขั้นตอนการตรวจสอบนี้ควรดำเนินการทันทีหลังจากการ Compile เพื่อให้แน่ใจว่าการ Register สำเร็จ การไม่มีโมเดลแบบกำหนดเองจากผลลัพธ์นี้มักบ่งบอกว่ามีมาโคร `addToRunTimeSelectionTable` หายไปหรือมีปัญหาการ Compile ที่ขัดขวางการรวม Symbol

แนวทางการทดสอบนี้มีประโยชน์อย่างยิ่งเมื่อทำงานกับการจำลองหลายเฟสที่ซับซ้อนซึ่ง Interfacial Models หลายตัวต้องทำงานร่วมกันผ่านสถาปัตยกรรมระบบเฟสของ OpenFOAM
