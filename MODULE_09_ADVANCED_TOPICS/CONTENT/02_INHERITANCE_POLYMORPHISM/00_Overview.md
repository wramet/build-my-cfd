# 02 การสืบทอดและพหุสัณฐาน (Inheritance & Polymorphism)

![[inheritance_polymorphism_overview.png]]
`A clean scientific illustration of "Polymorphism" in OpenFOAM. Show a standard "Base Interface" socket. Multiple different "Concrete Implementation" plugs (Turbulence, Drag, Heat Transfer) are shown nearby, indicating they all fit into the same socket. Use a minimalist palette with black lines and clear labels, scientific textbook diagram, clean vector line art, white background, high definition, flat design, educational infographic --ar 16:9`

## ภาพรวมของหัวข้อ

ในหัวข้อนี้ เราจะสำรวจหัวใจสำคัญของสถาปัตยกรรม OpenFOAM ที่ทำให้มันเป็นเครื่องมือ CFD ที่ยืดหยุ่นและขยายความสามารถได้มากที่สุด นั่นคือการใช้ **การสืบทอด (Inheritance)** และ **พหุสัณฐาน (Polymorphism)** เพื่อสร้างระบบแบบ Plug-and-Play สำหรับโมเดลทางฟิสิกส์

### แนวคิด "Plug-and-Play Physics Sockets"

จินตนาการการสร้างระบบสเตริโอที่คุณสามารถ **เปลี่ยนลำโพงแบบร้อน** (hot-swap) โดยไม่ต้องต่อสายใหม่ทั้งหมด ระบบการสืบทอดและพอลิมอร์ฟิซึมของ OpenFOAM ทำงานเหมือนกันทั้งหมด:

- **ซ็อกเก็ตมาตรฐาน** = คลาสแม่แบบนามธรรม (`phaseModel`, `dragModel`)
- **คอมโพเนนต์ที่เปลี่ยนได้แบบร้อน** = การใช้งานจริง (`purePhaseModel`, `SchillerNaumann`)
- **ขยายเสียง** = Solver ที่รู้จักเฉพาะอินเทอร์เฟซของซ็อกเก็ต
- **เพลย์ลิสต์ของผู้ใช้** = การกำหนดค่า Dictionary ที่เลือกคอมโพเนนต์ที่จะเสียบ

สถาปัตยกรรมของ OpenFOAM เปลี่ยนแปลงการพัฒนา CFD จาก "การเขียนโค้ดที่แก้สมการแบบ Hardcoded" เป็น "การกำหนดอินเทอร์เฟซมาตรฐานที่สามารถสลับเปลี่ยนโมเดลได้ตามความต้องการ" ผ่านกลไกที่เรียกว่า **Run-Time Selection (RTS)**

### พื้นฐานของ Abstract Base Classes

สถาปัตยกรรมโมเดลของ OpenFOAM พึ่งพา abstract base classes เป็นอย่างมากที่กำหนดอินเทอร์เฟซมาตรฐาน:

```cpp
// Base class that all phase models inherit from
template<class Base>
class phaseModel
:
    public Base
{
    // Pure virtual function - all derived classes must implement
    virtual tmp<volScalarField> rho() const = 0;

    // Interface for phase fraction calculation
    virtual const volScalarField& alpha() const = 0;
};
```

**📖 คำอธิบาย (Thai Explanation):**

**แหล่งที่มา (Source):** โครงสร้างแนวคิดพื้นฐานจาก `src/phaseSystemModels/phaseModel/phaseModel.H`

**คำอธิบาย:** Abstract base class (`phaseModel`) ทำหน้าที่เป็น "สัญญา" (contract) ที่กำหนดว่าโมเดลเฟสทุกตัวต้องมีฟังก์ชัน `rho()` และ `alpha()` ให้เรียกใช้งานได้ คีย์เวิร์ด `virtual` ทำให้เกิดพฤติกรรมพหุสัณฐาน และ `= 0` ระบุว่านี่เป็น "pure virtual function" ที่ derived class ต้อง implement ด้วยตนเอง

**แนวคิดสำคัญ (Key Concepts):**
- **Template Base Class**: การใช้เทมเพลต `<class Base>` ช่วยให้ `phaseModel` สืบทอดความสามารถจากคลาสฐานต่างๆ ได้อย่างยืดหยุ่น
- **Pure Virtual Functions**: ฟังก์ชันที่ไม่มีการนำไปใช้งานใน base class บังคับให้ derived classes สร้างการนำไปใช้งานเอง
- **Interface Segregation**: กำหนด API มาตรฐานที่ solver ใช้งานได้โดยไม่ต้องรู้ว่าเป็น phase model ชนิดใด

---

Abstract base class นี้สร้าง **สัญญา** ที่ phase models ทั้งหมดต้องเติมเต็ม ซึ่งทำให้เกิด **พฤติกรรมโพลิมอร์ฟิก** ซึ่งโค้ดที่เรียกใช้สามารถทำงานกับ phase model ใดๆ โดยไม่ต้องรู้ชนิดเฉพาะ

## วัตถุประสงค์การเรียนรู้

เมื่อจบหัวข้อนี้ คุณจะสามารถ:

1. **เข้าใจอินเทอร์เฟซแบบนามธรรม (Abstract Interfaces)**: อธิบายว่าทำไม OpenFOAM จึงเน้นการออกแบบผ่าน Base Classes มากกว่าการระบุการนำไปใช้งานจริง (Implementation)

2. **วิเคราะห์ลำดับชั้นการสืบทอด**: เข้าใจโครงสร้างการสืบทอดของโมเดลซับซ้อน เช่น Phase Models และ Turbulence Models

3. **เชี่ยวชาญระบบ Run-Time Selection (RTS)**: เข้าใจกลไกเบื้องหลังที่ช่วยให้เลือกโมเดลผ่าน Dictionary โดยไม่ต้องคอมไพล์โค้ดใหม่

4. **ประเมินประสิทธิภาพของ Virtual Dispatch**: เข้าใจความสมดุล (Trade-off) ระหว่างความยืดหยุ่นของฟังก์ชันเสมือนและประสิทธิภาพการคำนวณ

5. **นำแนวคิดการประกอบโมเดล (Composition) ไปใช้**: เข้าใจวิธีการสร้างระบบ CFD ที่ซับซ้อนจากส่วนประกอบย่อยๆ ที่ทำงานร่วมกัน

## ข้อกำหนดเบื้องต้น (Prerequisites)

- **ความเข้าใจ C++ OOP**: พื้นฐานเรื่อง Classes, Inheritance และ Virtual Functions
- **01_TEMPLATE_PROGRAMMING**: ควรผ่านหัวข้อพื้นฐานเทมเพลต เนื่องจาก RTS มักใช้เทมเพลตร่วมด้วย
- **ความคุ้นเคยกับ Dictionary ใน OpenFOAM**: เข้าใจวิธีการกำหนดค่าใน `fvSolution` หรือ `thermophysicalProperties`

## Virtual Dispatch: การแก้ไขวิธีแบบไดนามิก

เมื่อ OpenFOAM เรียกใช้ virtual method บน base class pointer หรือ reference, กลไก **virtual function table (vtable)** จะทำให้แน่ใจว่า derived implementation ที่ถูกต้องถูกเรียกขณะทำงาน:

```cpp
// Base class pointer can point to any derived class
phaseModel* phase = phaseSystem.phase("gas"); // Points to gasPhaseModel
volScalarField density = phase->rho(); // Dispatches to gasPhaseModel::rho()

// Same pointer now points to different derived class
phase = phaseSystem.phase("water"); // Now points to liquidPhaseModel
density = phase->rho(); // Dispatches to liquidPhaseModel::rho()
```

**📖 คำอธิบาย (Thai Explanation):**

**แหล่งที่มา (Source):** แนวคิดพื้นฐานของ polymorphic dispatch ใน `src/phaseSystemModels/phaseModel/`

**คำอธิบาย:** กลไก vtable ของ C++ ทำให้ pointer ชนิด `phaseModel*` สามารถเรียกใช้ฟังก์ชัน `rho()` ที่ถูกต้องสำหรับแต่ละ derived class ได้โดยอัตโนมัติ โดยไม่ต้องมีการ `if-else` หรือ `switch-case` เพื่อตรวจสอบชนิดของ object ช่วยให้โค้ดกระชับและบำรุงรักษาง่าย

**แนวคิดสำคัญ (Key Concepts):**
- **Dynamic Dispatch**: การเลือกฟังก์ชันที่จะเรียกเกิดขึ้นขณะโปรแกรมทำงาน (runtime) ไม่ใช่ตอนคอมไพล์
- **vtable (Virtual Table)**: ตารางฟังก์ชันเสมือนที่คอมไพเลอร์สร้างให้แต่ละคลาสที่มี virtual functions
- **Base Class Interface**: การทำงานผ่าน interface ร่วมกันทำให้ solver ไม่ต้องรู้ว่าทำงานกับ derived class ใด

---

กลไกนี้ช่วยให้ **polymorphic containers** ที่ phase models ที่แตกต่างกันสามารถจัดเก็บและเข้าถึงผ่านอินเทอร์เฟซเดียวกัน:

```cpp
// Polymorphic container storing different phase model types
List<phaseModel*> phases;
phases.append(new gasPhaseModel(...));
phases.append(new liquidPhaseModel(...));

// Uniform interface for all phases
forAll(phases, i)
{
    volScalarField phaseDensity = phases[i]->rho();
    phaseDensity.rename(phases[i]->name() + "Rho");
}
```

**📖 คำอธิบาย (Thai Explanation):**

**แหล่งที่มา (Source):** รูปแบบการใช้งาน polymorphic containers ใน `src/phaseSystemModels/phaseSystem/`

**คำอธิบาย:** `List<phaseModel*>` เป็น container แบบโพลิมอร์ฟิกที่เก็บ pointers ไปยัง derived classes ต่างๆ ได้ เนื่องจาก derived classes ทั้งหมดสืบทอดจาก `phaseModel` การวนลูป `forAll` สามารถเรียกใช้ `rho()` บนทุก element ได้โดยไม่ต้องรู้ว่าเป็น gas หรือ liquid phase

**แนวคิดสำคัญ (Key Concepts):**
- **Polymorphic Container**: Container ที่เก็บ pointers/references ของ base class แต่จริงๆ ชี้ไปยัง derived classes
- **Uniform Interface**: ทุก derived class ตอบสนอง interface เดียวกัน ทำให้เขียนโค้ดทั่วไปได้
- **Open/Closed Principle**: เปิดสำหรับการขยาย (เพิ่ม derived class ใหม่) แต่ปิดสำหรับการแก้ไข (ไม่ต้องเปลี่ยน loop)

---

### Factory Pattern: การเลือกโมเดลขณะทำงาน

การ implement Factory Pattern ของ OpenFOAM อนุญาตให้เลือกโมเดลผ่าน dictionary entries โดยไม่ต้องคอมไพล์ใหม่:

```cpp
// In phaseModel.H - Declare run-time selection table
declareRunTimeSelectionTable
(
    phaseModel,
    phaseModel,
    dictionary,
    (
        const dictionary& dict,
        const phaseSystem& fluid,
        const word& phaseName
    ),
    (dict, fluid, phaseName)
);

// In gasPhaseModel.C - Register this model with the factory
addToRunTimeSelectionTable
(
    phaseModel,
    gasPhaseModel,
    dictionary
);

// In phaseModel.C - Factory method to create models from dictionary
autoPtr<phaseModel> phaseModel::New
(
    const dictionary& dict,
    const phaseSystem& fluid,
    const word& phaseName
)
{
    const word modelType(dict.lookup("type"));

    typename dictionaryConstructorTable::iterator cstrIter =
        dictionaryConstructorTablePtr_->find(modelType);

    return cstrIter()(dict, fluid, phaseName);
}
```

**📖 คำอธิบาย (Thai Explanation):**

**แหล่งที่มา (Source):** 📂 `.applications/utilities/mesh/generation/foamyMesh/conformalVoronoiMesh/initialPointsMethod/initialPointsMethod/initialPointsMethod.C`

**คำอธิบาย:** ระบบ Run-Time Selection ของ OpenFOAM ใช้ macro `declareRunTimeSelectionTable` เพื่อสร้าง "Selection Table" ที่เก็บ pointers ไปยัง constructor functions ของ derived classes ทั้งหมด เมื่อเรียก `phaseModel::New()` ระบบจะค้นหาชนิดโมเดลจาก dictionary แล้วเรียก constructor ที่เหมาะสมผ่าน function pointer

**แนวคิดสำคัญ (Key Concepts):**
- **Factory Method**: ฟังก์ชัน `New()` ที่สร้าง object โดยไม่ให้ผู้เรียกต้องรู้ concrete class
- **Run-Time Selection Table**: Hash table ที่ map ชื่อโมเดล (string) ไปยัง constructor pointer
- **Macro Magic**: Macros ของ OpenFOAM สร้าง boilerplate code สำหรับ registration และ lookup
- **Dictionary-Driven Configuration**: ผู้ใช้เปลี่ยนโมเดลโดยแก้ไข dictionary ไม่ต้องคอมไพล์ใหม่

---

สถาปัตยกรรมนี้ช่วยให้ **การเลือกโมเดลโดยใช้การกำหนดค่า** ซึ่งผู้ใช้ระบุชนิดโมเดลใน dictionary:

```
phases
{
    gas
    {
        type            gasPhase;    // Selects gasPhaseModel
        equationOfState idealGas;
    }

    water
    {
        type            liquidPhase; // Selects liquidPhaseModel
        equationOfState isothermal;
    }
}
```

**📖 คำอธิบาย (Thai Explanation):**

**แหล่งที่มา (Source):** ไฟล์การกำหนดค่าใน `tutorials/multiphase/multiphaseEulerFoam/`

**คำอธิบาย:** Dictionary นี้แสดงให้เห็นพลังของ Run-Time Selection ผู้ใช้เพียงระบุ `type gasPhase` หรือ `type liquidPhase` และระบบ RTS จะสร้าง object ชนิดที่ถูกต้องให้โดยอัตโนมัติ ไม่ต้องเปลี่ยนโค้ด solver หรือคอมไพล์ใหม่

**แนวคิดสำคัญ (Key Concepts):**
- **Declarative Configuration**: ผู้ใช้ประกาศว่าต้องการโมเดลใด ไม่ต้องกังวลเรื่องการสร้าง
- **Hot-Swappable Models**: สามารถเปลี่ยนโมเดลได้ทันทีโดยแก้ dictionary เท่านั้น
- **Type Safety**: ระบบ RTS ตรวจสอบว่าโมเดลที่ระบุมีอยู่จริง ถ้าไม่พบจะแสดง error

---

## รูปแบบการออกแบบ (Design Patterns)

### 1. Strategy Pattern: อัลกอริทึมที่สามารถสลับทดแทนกันได้

แต่ละ drag correlation (`SchillerNaumann`, `Ergun`, `WenYu` เป็นต้น) จะใช้งาน interface ทั่วไปเดียวกัน แต่ห่อหุ้ม physical correlations ที่แตกต่างกันไว้:

**กรอบงานคณิตศาสตร์**: drag models ทั้งหมดใช้งาน interface:
$$K_d = \text{drag\_model}.K(\alpha_c, \alpha_d, \mathbf{u}_c, \mathbf{u}_d, \rho_c, \rho_d, \mu_c, \mu_d, d_p)$$

โดยแต่ละโมเดลจะให้ correlation ของตนเอง:
- **Schiller-Naumann**: $K_d = \frac{3}{4}C_D\frac{\alpha_c\alpha_d\rho_c|\mathbf{u}_c - \mathbf{u}_d|}{d_p}$
- **Ergun**: $K_d = 150\frac{\alpha_d^2\mu_c(1-\alpha_c)}{\alpha_c^3d_p^2} + 1.75\frac{\alpha_c\alpha_d\rho_c|\mathbf{u}_c - \mathbf{u}_d|}{d_p}$

```cpp
// Strategy interface - all drag models implement this
class dragModel
{
public:
    // Common interface - all strategies provide this
    virtual tmp<volScalarField> K
    (
        const volScalarField& alpha1,
        const volScalarField& alpha2,
        const volVectorField& U1,
        const volVectorField& U2,
        const volScalarField& rho1,
        const volScalarField& rho2,
        const volScalarField& mu1,
        const volScalarField& mu2,
        const scalarDiameter& d
    ) const = 0;
};

// Concrete Strategy 1: Schiller-Naumann correlation
class SchillerNaumann
:
    public dragModel
{
    tmp<volScalarField> K(...) const
    {
        // Implements Schiller-Naumann correlation
        return 0.75 * Cd * alpha1 * alpha2 * rho1 * mag(U1 - U2) / d;
    }
};

// Concrete Strategy 2: Ergun correlation
class Ergun
:
    public dragModel
{
    tmp<volScalarField> K(...) const
    {
        // Implements Ergun correlation
        return 150.0 * sqr(alpha2) * mu1 * (1 - alpha1) / (sqr(alpha1) * sqr(d))
             + 1.75 * alpha1 * alpha2 * rho1 * mag(U1 - U2) / d;
    }
};
```

**📖 คำอธิบาย (Thai Explanation):**

**แหล่งที่มา (Source):** `src/phaseSystemModels/interfacialModels/dragModels/dragModel/dragModel.H`

**คำอธิบาย:** Strategy Pattern ใน drag models ทำให้ solver สามารถเปลี่ยน drag correlation ได้โดยไม่ต้องแก้โค้ด solver ทุก drag model ให้ interface เดียวกันคือฟังก์ชัน `K()` แต่ละ model คำนวณ drag coefficient ด้วยสูตรที่แตกต่างกัน

**แนวคิดสำคัญ (Key Concepts):**
- **Strategy Interface**: กำหนด signature ร่วมกันสำหรับทุก strategy
- **Concrete Strategies**: Derived classes ที่ implement algorithms เฉพาะ
- **Interchangeable Algorithms**: สามารถสลับ strategy ได้โดยไม่กระทบ client code
- **Encapsulation of Correlations**: Physical correlations ถูกห่อหุ้มใน classes แยกกัน

---

### 2. Template Method Pattern: การขยายแบบควบคุม

ฐาน `phaseModel` กำหนดโครงร่างของ correction algorithm:

```cpp
class phaseModel {
public:
    // Template Method - defines algorithm skeleton
    // Public non-virtual interface - controls algorithm flow
    virtual void correct() {
        preCorrect();           // Hook method - optional override
        correctThermo();        // Pure virtual - must implement
        correctTurbulence();    // Virtual - may override
        correctSpecies();       // Virtual - may override
        postCorrect();          // Hook method - optional override
        updateFields();         // Fixed final step - cannot override
    }

protected:
    // Hook methods with default implementations
    virtual void preCorrect() {}
    virtual void postCorrect() {}
    
    // Steps that derived classes must provide
    virtual void correctThermo() = 0;
    
    // Steps with default behavior that can be overridden
    virtual void correctTurbulence() {}
    virtual void correctSpecies() {}
    
private:
    // Final step that cannot be overridden
    void updateFields();
};
```

**📖 คำอธิบาย (Thai Explanation):**

**แหล่งที่มา (Source):** รูปแบบ Template Method พร้อม NVI (Non-Virtual Interface) ใน `src/thermophysicalModels/`

**คำอธิบาย:** Template Method Pattern กำหนดโครงร่างของ algorithm ใน base class (`correct()`) แต่ให้ derived classes กำหนด implementation ของขั้นตอนบางส่วน ในที่นี้ใช้ NVI pattern โดย `correct()` เป็น public non-virtual ที่เรียก virtual functions อื่นๆ ช่วยควบคุมลำดับการทำงานและให้จุด hooks สำหรับ extension

**แนวคิดสำคัญ (Key Concepts):**
- **Template Method**: ฟังก์ชันที่กำหนด algorithm steps แต่ไม่ implement ทุก step
- **Hook Methods**: Virtual functions ที่ derived classes สามารถ override เพื่อขยายพฤติกรรม
- **NVI (Non-Virtual Interface)**: Public เป็น non-virtual, private/protected เป็น virtual
- **Hollywood Principle**: "Don't call us, we'll call you" - base class เรียก derived class methods

---

**กรอบงานคณิตศาสตร์**: template method ทำให้มั่นใจได้ถึงลำดับการประเมินที่สอดคล้องกัน:
$$\text{Correct}() = \begin{cases}
\text{PreCorrect}() & \text{optional pre-processing} \\
\text{CorrectThermo}() & \text{mandatory thermodynamic update} \\
\text{CorrectTurbulence}() & \text{optional turbulence update} \\
\text{CorrectSpecies}() & \text{optional species transport} \\
\text{PostCorrect}() & \text{optional post-processing} \\
\text{UpdateFields}() & \text{mandatory field consolidation}
\end{cases}$$

### 3. Composite Pattern: ระบบลำดับชั้น

```cpp
// Composite class - manages collection of phases
class phaseSystem {
private:
    // Composition: Container of phase model pointers
    PtrList<phaseModel> phases_;
    PtrList<dragModel> dragModels_;

public:
    // Delegate to components
    virtual void correct() {
        forAll(phases_, phasei) {
            phases_[phasei].correct();
        }
    }

    // Aggregate properties from all phases
    virtual tmp<volScalarField> totalDensity() const {
        tmp<volScalarField> trho = phases_[0].rho()*phases_[0].alpha();
        for(label i = 1; i < phases_.size(); i++) {
            trho.ref() += phases_[i].rho()*phases_[i].alpha();
        }
        return trho;
    }
};
```

**📖 คำอธิบาย (Thai Explanation):**

**แหล่งที่มา (Source):** `src/phaseSystemModels/phaseSystem/phaseSystem.H`

**คำอธิบาย:** Composite Pattern ใช้ `phaseSystem` เป็น container ที่เก็บรวบรวม `phaseModel` หลายๆ ตัว และจัดการ lifecycle ของพวกมัน `PtrList<phaseModel>` เป็น container แบบ polymorphic ที่เก็บ pointers ไปยัง derived classes ต่างๆ ฟังก์ชัน `correct()` วนลูปเรียก `correct()` บนทุก phase ส่วน `totalDensity()` รวมค่า density จากทุก phase

**แนวคิดสำคัญ (Key Concepts):**
- **Composite Object**: Object ที่เก็บ collection ของ objects อื่นๆ
- **Composition over Inheritance**: ใช้การรวม objects แทนการสืบทอกลึกๆ
- **Delegation**: Composite ฝากงานให้ components ทำจริง
- **Aggregation**: คำนวณค่ารวมจาก components (เช่น total density)

---

**กรอบงานคณิตศาสตร์**: คุณสมบัติของระบบเป็น composites:
$$\rho_{\text{total}} = \sum_{i=1}^{N} \alpha_i \rho_i$$

$$\mathbf{U}_{\text{mixture}} = \frac{\sum_{i=1}^{N} \alpha_i \rho_i \mathbf{U}_i}{\sum_{i=1}^{N} \alpha_i \rho_i}$$

## สถาปัตยกรรมระบบหลายเฟส: การประกอบของโมเดล

ระบบเฟสสาธิตให้เห็นว่า OpenFOAM ประกอบ model hierarchies หลายอย่างเข้าด้วยกันในกรอบการหลายเฟสที่สอดคล้องกัน:

```cpp
template<class Base>
class phaseSystem
:
    public Base
{
    // Composition: Container of phase model pointers
    HashPtrTable<phaseModel> phases_;

    // Polymorphic access to phase properties
    const phaseModel& phase(const word& phaseName) const;

    // Template method pattern: algorithms use phase interfaces
    virtual void correct() = 0;
};
```

**📖 คำอธิบาย (Thai Explanation):**

**แหล่งที่มา (Source):** `src/phaseSystemModels/phaseSystem/phaseSystem.H`

**คำอธิบาย:** `phaseSystem` เป็น template class ที่สืบทอดจาก `Base` และใช้ composition โดยเก็บ `HashPtrTable<phaseModel>` ที่ map ชื่อ phase ไปยัง phase model object ฟังก์ชัน `phase()` คืน reference ถึง phase model ใดๆ แบบ polymorphic

**แนวคิดสำคัญ (Key Concepts):**
- **Template Inheritance**: สืบทอกจาก base class แบบ parameterized
- **HashPtrTable**: Hash table ที่เก็บ smart pointers สำหรับ lookup รวดเร็ว
- **Polymorphic Access**: เข้าถึง derived objects ผ่าน base class reference
- **Mixed Composition**: ใช้ทั้ง inheritance (จาก Base) และ composition (phases_)

---

**Template Method Pattern** ถูกใช้ที่โครงสร้างอัลกอริทึมพื้นฐานคงที่ใน base class, แต่การ implement เฉพาะแตกต่างกัน:

```cpp
// Base algorithm structure
void multiphaseSystem::correct()
{
    // Fixed sequence
    correctThermo();
    correctPhaseFractions();
    correctTurbulence();      // Virtual call to derived implementation
    correctSpecies();
}

// Derived systems provide specific corrections
void reactingMultiphaseSystem::correctTurbulence()
{
    // Turbulence corrections specific to reacting flows
    forAll(phases_, phaseI)
    {
        calculateReactiveEffects(phases_[phaseI]);
    }
}
```

**📖 คำอธิบาย (Thai Explanation):**

**แหล่งที่มา (Source):** `src/phaseSystemModels/reactingMultiphaseSystem/reactingMultiphaseSystem.C`

**คำอธิบาย:** `multiphaseSystem::correct()` คือ template method ที่กำหนดลำดับการทำงานคงที่ แต่เรียก `correctTurbulence()` ซึ่งเป็น virtual function `reactingMultiphaseSystem` override `correctTurbulence()` เพื่อใส่ logic เฉพาะสำหรับ reacting flows

**แนวคิดสำคัญ (Key Concepts):**
- **Algorithm Skeleton**: Base class กำหนดขั้นตอนหลัก
- **Variable Steps**: Steps บางส่วนเป็น virtual สำหรับ customization
- **Invariant Sequence**: ลำดับการทำงานหลักคงที่ใน base class
- **Extension Points**: Virtual functions เป็นจุดที่ derived classes ขยายพฤติกรรม

---

## พิจารณาด้านประสิทธิภาพ

### กลยุทธ์การจัดการหน่วยความจำ

OpenFOAM ใช้ **reference-counted smart pointers** เพื่อจัดการวัตถุตลอดช่วงชีวิตอย่างมีประสิทธิภาพ:

```cpp
// tmp<T> provides automatic memory management
tmp<volScalarField> phaseModel::rho() const
{
    // Efficient return by value with move semantics
    return tmp<volScalarField>::New(rhoField_);
}
```

**📖 คำอธิบาย (Thai Explanation):**

**แหล่งที่มา (Source):** `src/OpenFOAM/fields/tmp/tmp.H`

**คำอธิบาย:** `tmp<T>` เป็น smart pointer แบบ reference-counted ของ OpenFOAM เมื่อ `rho()` คืนค่า `tmp<volScalarField>` จะไม่ copy field ทั้งหมด แต่จะใช้ move semantics เพื่อโอน ownership ของข้อมูล ตัวนับ reference จะติดตามว่ามีผู้ใช้งาน field นี้กี่คน เมื่อไม่มีใครใช้แล้วจะ deallocate อัตโนมัติ

**แนวคิดสำคัญ (Key Concepts):**
- **Reference Counting**: นับจำนวน pointers ที่ชี้ไปยัง object เดียวกัน
- **Move Semantics**: โอน ownership แทนการ copy ข้อมูล ประหยัดหน่วยความจำ
- **Automatic Cleanup**: Object ถูกทำลายเมื่อ reference count เป็นศูนย์
- **tmp< T >**: Smart pointer เฉพาะของ OpenFOAM สำหรับ field objects

---

### การเพิ่มประสิทธิภาพขณะคอมไพล์เทียบกับขณะทำงาน

แม้ว่า virtual dispatch จะให้ความยืดหยุ่น, OpenFOAM ใช้ **CRTP (Curiously Recurring Template Pattern)** เพื่อการเพิ่มประสิทธิภาพขณะคอมไพล์เมื่อทราบชนิดโมเดล:

```cpp
template<class DerivedType>
class phaseModelTemplate
{
    // CRTP enables compile-time polymorphism
    const DerivedType& derived() const
    {
        return static_cast<const DerivedType&>(*this);
    }

    void efficientOperation()
    {
        // Direct call to derived method without virtual overhead
        derived().specificImplementation();
    }
};
```

**📖 คำอธิบาย (Thai Explanation):**

**แหล่งที่มา (Source):** รูปแบบ CRTP ใน `src/OpenFOAM/`

**คำอธิบาย:** CRTP คือเทคนิคที่ derived class ส่งตัวเองเป็น template parameter ของ base class: `class Derived : public Base<Derived>` ทำให้ base class รู้ชนิดของ derived class และสามารถ `static_cast` ไปยังชนิดที่ถูกต้อง ช่วยให้เรียกฟังก์ชันโดยตรงโดยไม่ผ่าน vtable ให้ความเร็วเท่ากับ non-virtual calls

**แนวคิดสำคัญ (Key Concepts):**
- **CRTP (Curiously Recurring Template Pattern)**: Derived class ส่งตัวเองเป็น template argument
- **Compile-Time Polymorphism**: การ resolve function calls เกิดขณะคอมไพล์ ไม่ใช่ runtime
- **Static Downcasting**: Base class cast ไปยัง derived type อย่างปลอดภัย
- **Zero-Overhead Abstraction**: ความยืดหยุ่นของ OOP โดยไม่มีค่าใช้จ่าย runtime

---

### ประสิทธิภาพของ Virtual Dispatch

แนวทางแบบพอลิมอร์ฟิกมีค่าใช้จ่ายด้านประสิทธิภาพเพียงเล็กน้อยเนื่องจาก:

1. **การเรียกฟังก์ชันเสมือน**: แก้ไขใน runtime แต่คำนวณได้ถูกเมื่อเทียบกับการดำเนินการ CFD
2. **การสร้างแม่แบบ**: การคำนวณที่หนักส่วนใหญ่ใช้แม่แบบสำหรับการปรับให้เหมาะสม
3. **ประสิทธิภาพแคช**: รูปแบบการเข้าถึงหน่วยความจำที่คล้ายกันในการใช้งานที่แตกต่างกัน

ความยืดหยุ่นที่ได้รับมีค่ามากกว่าค่าใช้จ่ายในระดับไมโครวินาทีของการจัดส่งฟังก์ชันเสมือนในการจำลองที่โดยทั่วไปทำงานเป็นชั่วโมงหรือวัน

## เนื้อหาในบทนี้

1. **01_🎣_The_Hook_Plug-and-Play_Physics_Sockets.md**: บทนำสู่แนวคิด "Plug-and-Play Physics Sockets" และความสำคัญของ Polymorphism

2. **02_🏗️_The_Blueprint_Abstract_Interfaces_as_Contracts.md**: การออกแบบ Base Classes ในฐานะ "สัญญา" (Contracts) ระหว่าง Solver และโมเดล พร้อม Virtual Function Table (vtable) ที่ทำให้เกิดพฤติกรรม polymorphic

3. **03_🔩_Internal_Mechanics_OpenFOAM's_Inheritance_Hierarchies.md**: เจาะลึกลำดับชั้นการสืบทอดของ OpenFOAM ตั้งแต่ระดับพื้นฐานจนถึงโมเดลซับซ้อน รวมถึงการสืบทอดหลายครั้งและการแก้ปัญหา "Diamond Problem"

4. **04_⚙️_The_Mechanism_Run-Time_Selection_(RTS)_System.md**: กลไกภายในของ RTS การทำงานของ Selection Tables และ Macro Magic ของ `declareRunTimeSelectionTable` และ `addToRunTimeSelectionTable`

5. **05_🎭_The_Why_Design_Patterns_in_Physics_Modeling.md**: รูปแบบการออกแบบ เช่น Factory, Strategy, Template Method และ Composite ในบริบทของฟิสิกส์

6. **06_💻_Usage_Examples_vs._Common_Errors.md**: วิธีการแก้ไขข้อผิดพลาดที่พบบ่อยในการพัฒนาและใช้งานโมเดลแบบ Polymorphic เช่น Object Slicing, การขาด Virtual Destructor, และการ Bypass ระบบ Factory

7. **07_📊_Performance_Considerations.md**: การวิเคราะห์ผลกระทบด้านประสิทธิภาพและเทคนิคการเพิ่มประสิทธิภาพ รวมถึงเค้าโครงหน่วยควาจำแบบติดต่อกัน, Structure of Arrays กับ Array of Structures, และ Expression Templates

8. **08_🔧_Practical_Implementation_Guide.md**: แบบฝึกหัดปฏิบัติการ: การเพิ่ม Custom Model เข้าสู่ระบบ Runtime Selection พร้อม Template สำหรับตรวจสอบการ Register ของ Factory

9. **09_📚_Summary_The_OpenFOAM_Polymorphism_Philosophy.md**: สรุปปรัชญา Polymorphism ของ OpenFOAM และการเปลี่ยนแปลง CFD Practice จาก hardcoded physics ไปสู่ configurable science

10. **10_🔍_Further_Exploration.md**: ไฟล์ต้นฉบับหลักที่ควรศึกษา การอ้างอิงรูปแบบการออกแบบ และเครื่องมือวิเคราะห์ประสิทธิภาพ

## การสำรวจเพิ่มเติมและแหล่งข้อมูล

### ไฟล์ต้นฉบับที่ควรศึกษา

- `src/phaseSystemModels/phaseModel/phaseModel.H`: ลำดับชั้นโมเดลเฟสหลัก

- `src/phaseSystemModels/interfacialModels/dragModels/dragModel/dragModel.H`: รูปแบบการออกแบบ Strategy

- `src/OpenFOAM/db/runTimeSelection/runTimeSelectionTables.H`: นิยามมาโคร RTS

- `src/finiteVolume/fields/fvPatchFields/basic/calculated/calculatedFvPatchField.H`: พหุสัณฐานฟิลด์

### การอ้างอิงรูปแบบการออกแบบ

- **รูปแบบ Strategy**: ลำดับชั้น `dragModel`
- **รูปแบบ Template Method**: `phaseModel::correct()` ด้วยรูปแบบ NVI
- **รูปแบบ Factory Method**: วิธี `New()` ทั้งหมดพร้อมตาราง RTS
- **รูปแบบ Composite**: `phaseSystem` ที่จัดการ `PtrList<phaseModel>`

### เครื่องมือวิเคราะห์ประสิทธิภาพ

```bash
# Analyze virtual call overhead
valgrind --tool=callgrind ./multiphaseEulerFoam
kcachegrind callgrind.out.*

# Measure model construction time from factory
export FOAM_VERBOSE=1  # Display model selection time
```

---

*ความรู้สำคัญ: **OpenFOAM ใช้พหุสัณฐานไม่ใช่เพียงในฐานะเทคนิคการเขียนโปรแกรม แต่เป็นปรัชญาการสร้างแบบจำลองฟิสิกส์***