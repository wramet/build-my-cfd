# 🔀 ส่วนที่ 2: STRATEGY PATTERN (อัลกอริทึมที่แทนที่กันได้)

## 1. "Hook": ชุดเครื่องมืออัลกอริทึม CFD

**อนาล็อกี**: จินตนาการชุดเครื่องมือที่แต่ละอันแก้ปัญหาเฉพาะทาง คุณไม่สนใจว่าประแจทำงานภายในอย่างไร—คุณแค่ต้องการขันสกรู ใน OpenFOAM แบบจำลองแรงลาก, แบบจำลองความปั่นป่วน, และรูปแบบการ Discretization เป็นเครื่องมือ "สลับเปลี่ยนได้" ในชุดเครื่องมือ CFD ของคุณ

**ปัญหาที่แก้**: จะ encapsulate กลุ่มของอัลกอริทึมที่เกี่ยวข้องและทำให้สามารถสลับเปลี่ยนกันได้ใน runtime?

**บริบทฟิสิกส์**: กฎแรงลากที่แตกต่างกัน (Schiller-Naumann, Ergun, Gibilaro) มีความแตกต่างทางคณิตศาสตร์ แต่มี interface เดียวกัน (คำนวณสัมประสิทธิ์แรงลาก)

## 2. Blueprint: อินเทอร์เฟซอัลกอริทึม

**คำจำกัดความ Strategy Pattern**: กำหนด family ของอัลกอริทึม, encapsulate แต่ละอัน, และทำให้สามารถสลับเปลี่ยนกันได้

**การ Implement ใน OpenFOAM**: Abstract base class พร้อม pure virtual methods, concrete implementations สำหรับแต่ละอัลกอริทึม

```cpp
// Strategy Interface
class dragModel
{
public:
    TypeName("dragModel");

    // Pure virtual strategy method
    virtual tmp<surfaceScalarField> K
    (
        const phaseModel& phase1,
        const phaseModel& phase2
    ) const = 0;

    // Factory for runtime selection (combines Strategy with Factory!)
    static autoPtr<dragModel> New
    (
        const dictionary& dict,
        const phaseModel& phase1,
        const phaseModel& phase2
    );
};

// Concrete Strategy: Schiller-Naumann Drag
class SchillerNaumann
:
    public dragModel
{
private:
    dimensionedScalar C_;  // Algorithm parameters
    dimensionedScalar n_;

public:
    TypeName("SchillerNaumann");

    // Strategy implementation
    virtual tmp<surfaceScalarField> K
    (
        const phaseModel& phase1,
        const phaseModel& phase2
    ) const override
    {
        // Mathematical implementation
        const volScalarField Re = mag(phase1.U() - phase2.U()) * phase1.d() / phase2.nu();
        const volScalarField Cd = 24.0/Re * (1.0 + 0.15*pow(Re, 0.687));

        return 0.75 * Cd * phase2.rho() * mag(phase1.U() - phase2.U()) / phase1.d();
    }
};
```

## 3. กลไกภายใน: Strategy + Factory Synergy

**การผสมผสานที่มีพลัง**: OpenFOAM ผสมผสาน Strategy Pattern (การ abstract อัลกอริทึม) กับ Factory Pattern (การสร้างใน runtime)

**กลไกการลงทะเบียน** (เหมือนกับ Factory):
```cpp
// In SchillerNaumann.C
addToRunTimeSelectionTable(dragModel, SchillerNaumann, dictionary);
```

**ขั้นตอนการเลือกอัลกอริทึม**:
```cpp
// 1. Dictionary ระบุอัลกอริทึม
dragModel
{
    type            SchillerNaumann;  // Strategy selection
    C               0.44;             // Algorithm parameters
    n               1.0;
}

// 2. Factory สร้าง concrete strategy
autoPtr<dragModel> drag = dragModel::New(dragDict, phase1, phase2);

// 3. ใช้อัลกอริทึมแบบ polymorphic
surfaceScalarField Kdrag = drag->K(phase1, phase2);
```

## 4. กลไก: การ Encapsulation อัลกอริทึมคณิตศาสตร์

**แต่ละ strategy encapsulate แบบจำลองทางคณิตศาสตร์**:

**Schiller-Naumann Drag**:
$$
C_D = \frac{24}{\mathrm{Re}} (1 + 0.15\mathrm{Re}^{0.687})
$$

**Ergun Drag** (สำหรับ packed beds):
$$
K = 150 \frac{(1-\alpha)^2 \mu}{\alpha d_p^2} + 1.75 \frac{(1-\alpha) \rho |\mathbf{U}|}{d_p}
$$

**Gibilaro Drag**:
$$
K = \frac{17.3}{\mathrm{Re}} + 0.336
$$

**Strategy Pattern ทำให้เป็นไปได้**: การสลับเปลี่ยนระหว่างสูตรทางคณิตศาสตร์เหล่านี้ผ่านการกำหนดค่า dictionary โดยไม่ต้องเปลี่ยนโค้ด

## 5. "Why": Strategy Pattern สำหรับอัลกอริทึม CFD

**ทำไมต้อง Strategy Pattern ใน CFD?**:
1. **ความหลากหลายของอัลกอริทึม**: มีแบบจำลองทางคณิตศาสตร์ที่ถูกต้องหลายรูปแบบสำหรับฟิสิกส์เดียวกัน
2. **แบบจำลองเชิงประจักษ์**: แบบจำลองแรงลาก, การถ่ายเทความร้อน, ความปั่นป่วนมักเป็นสหสัมพันธ์เชิงประจักษ์
3. **ความยืดหยุ่นสำหรับการวิจัย**: สามารถเพิ่มแบบจำลองใหม่ได้โดยไม่ต้องแก้ไขโค้ด solver
4. **ความยืดหยุ่นในการตรวจสอบความถูกต้อง**: การเปรียบเทียบแบบจำลองต่างๆ บนปัญหาเดียวกันได้ง่าย

**ประโยชน์ด้านการออกแบบ**:
- **Encapsulation**: แต่ละอัลกอริทึมเป็นแบบสแตนด์อโลน
- **Interchangeability**: สามารถสลับแบบจำลองได้ใน runtime
- **Testability**: สามารถทดสอบแบบจำลองแต่ละอันแยกกันได้
- **Maintainability**: การเปลี่ยนแปลงอัลกอริทึมไม่กระทบโครงสร้าง solver

**พิจารณาด้านประสิทธิภาพ**: Virtual function overhead มีค่าเล็กน้อยเมื่อเทียบกับ field operations (โดยทั่วไป <0.1% ของ runtime)

## 6. ตัวอย่างการใช้งาน & ข้อผิดพลาด

### ✅ การใช้งานที่ถูกต้อง: การ Implement แบบจำลองแรงลากใหม่

```cpp
// 1. ศึกษาฟิสิกส์
// New drag correlation from journal paper:
// C_D = A/Re + B*Re^C

// 2. Implement เป็น strategy
class MyDragModel : public dragModel
{
    dimensionedScalar A_, B_, C_;

public:
    TypeName("myDrag");

    MyDragModel(const dictionary& dict, const phaseModel& p1, const phaseModel& p2)
    :
        dragModel(dict, p1, p2),
        A_(dict.lookup<dimensionedScalar>("A")),
        B_(dict.lookup<dimensionedScalar>("B")),
        C_(dict.lookup<dimensionedScalar>("C"))
    {}

    virtual tmp<surfaceScalarField> K(const phaseModel& p1, const phaseModel& p2) const override
    {
        const volScalarField Re = mag(p1.U() - p2.U()) * p1.d() / p2.nu();
        const volScalarField Cd = A_/Re + B_*pow(Re, C_);

        return 0.75 * Cd * p2.rho() * mag(p1.U() - p2.U()) / p1.d();
    }
};

// 3. Register
addToRunTimeSelectionTable(dragModel, MyDragModel, dictionary);

// 4. ใช้ใน case
dragModel
{
    type    myDrag;
    A       24.0;
    B       0.15;
    C       0.687;
}
```

### ❌ Anti-Patterns ของ Strategy Pattern

**Anti-Pattern 1: อัลกอริทึมเป็น Switch Statement**
```cpp
// WRONG: Hardcoded algorithm selection
surfaceScalarField calculateDrag(const word& modelType, ...)
{
    if (modelType == "SchillerNaumann")
        return calculateSchillerNaumann(...);
    else if (modelType == "Ergun")
        return calculateErgun(...);
    // Adding new models requires modifying this function
}

// RIGHT: Strategy pattern
autoPtr<dragModel> drag = dragModel::New(dict, phase1, phase2);
return drag->K(phase1, phase2);
```

**Anti-Pattern 2: การผสมผสานอัลกอริทึมกับข้อมูล**
```cpp
// WRONG: Algorithm parameters mixed with phase data
class phaseModel
{
    // ...
    scalar dragCoefficient_;  // Which drag model does this belong to?
    word dragModelType_;      // Mixing concerns
};

// RIGHT: Separate strategy object
class phaseModel
{
    autoPtr<dragModel> drag_;  // Strategy object
};
```

**Anti-Pattern 3: การ Copy-Paste การ Implement อัลกอริทึม**
```cpp
// WRONG: Duplicated code across solvers
void solver1::calculateDrag() { /* Schiller-Naumann implementation */ }
void solver2::calculateDrag() { /* Same implementation copied */ }
void solver3::calculateDrag() { /* Same implementation copied again */ }

// RIGHT: Single strategy implementation
class SchillerNaumann : public dragModel { /* One implementation */ };
// Used by all solvers via dragModel::New()
```

## 7. สรุป Strategy Pattern

**Strategy Pattern ใน OpenFOAM คือ**:
1. **ชุดเครื่องมือ** ของอัลกอริทึมที่สลับเปลี่ยนได้
2. **การ Encapsulation แบบจำลองทางคณิตศาสตร์**
3. **การเลือกอัลกอริทึมใน runtime**
4. **รวมกับ Factory Pattern** สำหรับการสร้าง

**จุดสำคัญ**:
- แต่ละอัลกอริทึมเป็น class แยกกันที่ implement common interface
- อัลกอริทึมถูกเลือกผ่านฟิลด์ `type` ใน dictionary
- Strategy + Factory ทำให้การสลับอัลกอริทึมใน runtime เป็นไปได้
- Virtual function overhead มีค่าเล็กน้อยสำหรับ field operations
