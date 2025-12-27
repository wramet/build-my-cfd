# 01 บทนำ: พลังของรูปแบบการออกแบบ (Design Patterns) ใน OpenFOAM

## 🏗️ ทำไม Design Patterns มีความสำคัญใน OpenFOAM?

สถาปัตยกรรมของ OpenFOAM เป็น masterclass ใน design patterns ของ C++ สมัยใหม่ codebase ใช้ design patterns ที่ซับซ้อนซึ่งช่วยให้สามารถขยายได้ บำรุงรักษาได้ และปรับให้เหมาะสมกับประสิทธิภาพ บทนี้สำรวจสอง patterns ที่เป็นพื้นฐานที่แพร่กระจายไปทั่ว OpenFOAM: **Factory Pattern** และ **Strategy Pattern**

### ความท้าทายที่ OpenFOAM แก้ไข

การจำลอง CFD ต้องการ:
- **การเลือกโมเดลแบบไดนามิก** ใน runtime
- **สถาปัตยกรรม solver ที่ขยายได้**
- **การจัดการ boundary condition ที่ยืดหยุ่น**
- **การปรับให้เหมาะสมใน compile-time** กับ **ความยืดหยุ่นใน runtime**

โซลูชันของ OpenFOAM อยู่ที่การใช้ design patterns อย่างกว้างขวางซึ่งให้ความสมดุลนี้อย่างแน่นอน

## ภาษาสากล: ทำไมต้องใช้รูปแบบการออกแบบ?

ซอฟต์แวร์ CFD ที่มีความซับซ้อนสูงอย่าง OpenFOAM ไม่สามารถสร้างขึ้นได้ด้วยการเขียนโค้ดแบบแก้ปัญหาเฉพาะหน้าไปวันๆ แต่ต้องการโครงสร้างที่รองรับการขยายตัว (Scability) และการบำรุงรักษา (Maintainability) ในระยะยาว **รูปแบบการออกแบบ (Design Patterns)** คือทางออกที่ได้รับการพิสูจน์แล้วในวิศวกรรมซอฟต์แวร์

ในบริบทของ OpenFOAM รูปแบบการออกแบบทำหน้าที่เป็น:
- **ภาษาสากล**: ช่วยให้นักพัฒนาเข้าใจโครงสร้างที่ซับซ้อนได้ทันทีเมื่อเห็นชื่อรูปแบบ
- **เกราะป้องกันประสิทธิภาพ**: ช่วยให้ใช้ฟีเจอร์ C++ ขั้นสูงได้โดยไม่เกิด Overhead ที่ไม่จำเป็น
- **ประตูสู่การขยายความสามารถ**: ช่วยให้ผู้ใช้สามารถเพิ่มโมเดลใหม่ๆ ได้โดยไม่ต้องแก้ไข Core Code

## DNA ของสถาปัตยกรรม OpenFOAM

หากเปรียบ OpenFOAM เป็นร่างกาย:
- **Inheritance & Polymorphism** คือกล้ามเนื้อและข้อต่อที่ยืดหยุ่น
- **Template Programming** คือ DNA ที่กำหนดลักษณะพื้นฐานในระดับเซลล์
- **Design Patterns** คือระบบประสาทที่ควบคุมว่าส่วนประกอบต่างๆ จะทำงานร่วมกันอย่างไร

## แนวทาง "Code Archaeology" ในการเข้าใจสถาปัตยกรรม

เมื่ออธิบายโค้ด OpenFOAM เราต้องเข้าใจเหมือนนักโบราณคดีที่ค้นพบชั้นของการตัดสินใจในการออกแบบ แต่ละชั้นเผยให้เห็นข้อมูลเชิงลึกเกี่ยวกับฟิสิกส์การคำนวณและสถาปัตยกรรมซอฟต์แวร์

**ทำไมถึงออกแบบแบบนี้?** สถาปัตยกรรมของ OpenFOAM สะท้อนถึงวิวัฒนาการของ CFD หลายทศวรรษ โดยแต่ละรูปแบบการออกแบบแก้ไขปัญหาการคำนวณเฉพาะทาง ตัวอย่างเช่น การใช้ polymorphism รันไทม์อย่างแพร่หลายผ่าน factory patterns ไม่ใช่แค่แฟชันของการเขียนโปรแกรมเชิงวัตถุเท่านั้น—แต่เป็นการแก้ไขปัญหาสำคัญของความยืดหยุ่นของ solver โดยไม่ต้องคอมไพล์ใหม่ เมื่อคุณเห็น:

```cpp
// Runtime selection of turbulence model using Factory pattern
// The actual model (k-ε, k-ω, LES, etc.) is determined from dictionary
autoPtr<incompressible::turbulenceModel> turbulence
(
    incompressible::turbulenceModel::New
    (
        mesh,                  // Mesh database
        laminarTransport,      // Transport properties dictionary
        U,                     // Velocity field
        phi                    // Flux field
    )
);
```

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystem.H`

---

**💡 Source**: 
ไฟล์หัวข้อ (Header file) ของ `phaseSystem` ซึ่งเป็นฐานคลาส (base class) สำหรับระบบหลายเฟส แสดงให้เห็นถึงการใช้งาน Factory pattern และ Runtime selection ในระดับสูง

**🔍 Explanation**: 
โค้ดด้านบนแสดงให้เห็นถึงพลังของ Factory pattern ในการเลือกโมเดลความปั่นป่วนแบบไดนามิกในรันไทม์ `autoPtr<incompressible::turbulenceModel>` ทำหน้าที่เป็นตัวชี้แบบ smart pointer ที่จัดการหน่วยความจำอัตโนมัติ โดยไม่ทราบล่วงหน้าว่าจะได้รับอินสแตนซ์ของโมเดลใด ไม่ว่าจะเป็น `kEpsilon`, `kOmegaSST`, `LESModel` หรือโมเดลที่ผู้ใช้กำหนดเอง เมธอด `New()` แบบ static ทำหน้าที่เป็น Factory ที่อ่านค่าจากพจนานุกรมและสร้างอ็อบเจกต์ที่เหมาะสม

**🎯 Key Concepts**:
- **Factory Pattern**: การสร้างอ็อบเจกต์แบบไดนามิกโดยไม่ทราบประเภทล่วงหน้า
- **autoPtr**: Smart pointer สำหรับการจัดการหน่วยความจำอัตโนมัติใน OpenFOAM
- **Runtime Selection**: การเลือกโมเดลในรันไทม์ผ่านการกำหนดค่าพจนานุกรม
- **Incompressible Flow**: ของไหลที่ไม่อัดตัว (incompressible) ใน OpenFOAM

---

นี่ไม่ใช่แค่การสร้างออบเจกต์ แต่เป็นการใช้กลไกการเลือกที่ขับเคลื่อนด้วยฟิสิกส์ โดยที่โมเดลความปั่นป่วน ($k$-$\varepsilon$, $k$-$\omega$, LES, เป็นต้น) สามารถถูกเลือกได้ในรันไทม์จากพจนานุกรมอินพุต

**ฟิสิกส์พื้นฐานคืออะไร?** ทุกลำดับชั้นของคลาสใน OpenFOAM สอดคล้องโดยตรงกับหลักการทางฟิสิกส์หรือคณิตศาสตร์ ความแตกต่างระหว่าง `volScalarField` และ `surfaceScalarField` ไม่ใช่เรื่องบังเอิญ—แต่เป็นการใช้ความต้องการพื้นฐานของวิธีการปริมาตรจำกัดในการแยกความแตกต่างระหว่างค่าที่เก็บไว้ที่ศูนย์เซลล์และค่าที่พื้นผิวเซลล์:

$$\int_{V} \nabla \cdot \mathbf{F} \, \mathrm{d}V = \oint_{S} \mathbf{F} \cdot \mathbf{n} \, \mathrm{d}S$$

## รูปแบบการออกแบบหลักใน OpenFOAM

### 1. Factory Pattern = **"สร้างอะไร"**

Factory Pattern ใน OpenFOAM เป็นหัวใจสำคัญของความสามารถในการขยาย โดยเปิดให้มีการสร้างอ็อบเจกต์แบบไดนามิกตามการกำหนดค่าผ่าน Dictionary ในช่วง Compile-time กรอบงานไม่ทราบว่าจะต้องการโมเดลความปั่นป่วน เงื่อนไขขอบเขต หรือสูตรคำนวณเชิงตัวเลขแบบใด แต่จะรู้เมื่อถึง Runtime

**การเลือกประเภทใน Runtime:**

```cpp
// Runtime type selection using Factory pattern
// The specific turbulence model is determined from input dictionary
autoPtr<incompressible::turbulenceModel> turbulence
(
    incompressible::turbulenceModel::New
    (
        modelType,            // Model type name from dictionary
        U,                    // Velocity field
        phi,                  // Surface flux field
        transportProperties   // Physical properties dictionary
    )
);
```

**📂 Source:** `.applications/utilities/miscellaneous/foamDictionary/foamDictionary.C`

---

**💡 Source**: 
ไฟล์โปรแกรม `foamDictionary` ซึ่งเป็น utility สำหรับจัดการและสอบถามพจนานุกรม (dictionary) ของ OpenFOAM แสดงให้เห็นถึงรูปแบบการอ่านและประมวลผลพจนานุกรมที่เป็นพื้นฐานของการทำงานของ Factory pattern

**🔍 Explanation**: 
โค้ดนี้แสดงให้เห็นถึงวิธีการเลือกโมเดลความปั่นป่วนแบบไดนามิกผ่าน Factory method ที่ชื่อว่า `New()` เมธอดนี้ทำหน้าที่เป็น "เครื่องจำหน่ายสินค้าอัตโนมัติ" ที่รับพารามิเตอร์อินพุต (modelType, fields, dictionaries) และคืนค่า pointer ไปยังอินสแตนซ์ของโมเดลที่เหมาะสม การใช้ `autoPtr` ช่วยให้มั่นใจว่าหน่วยความจำจะถูกจัดการอัตโนมัติเมื่อไม่มีการใช้งานอีกต่อไป

**🎯 Key Concepts**:
- **Factory Method**: เมธอด static `New()` สำหรับสร้างอ็อบเจกต์แบบไดนามิก
- **Runtime Selection**: การเลือกประเภทอ็อบเจกต์ในรันไทม์ผ่านพจนานุกรม
- **Smart Pointer**: การใช้ `autoPtr` สำหรับ automatic memory management
- **Dictionary-Based Configuration**: การกำหนดค่าโมเดลผ่านไฟล์พจนานุกรม

---

เมธอด `New` แบบ Static คือ Factory ที่ตรวจสอบประเภทที่ร้องขอและคืน Pointer ไปยัง Derived Class Instance ที่เหมาะสม

**เปิดให้ใช้ Plugin Architecture:**

```cpp
// Macro to register turbulence model in runtime selection table
// Enables automatic discovery and instantiation of user-defined models
addToRunTimeSelectionTable
(
    turbulenceModel,    // Base class name
    kEpsilon,           // Derived class name
    dictionary          // Constructor argument type
);
```

**📂 Source:** `.applications/utilities/preProcessing/changeDictionary/changeDictionary.C`

---

**💡 Source**: 
ไฟล์โปรแกรม `changeDictionary` ซึ่งเป็น utility สำหรับแก้ไขพจนานุกรมใน runtime แสดงให้เห็นถึงการใช้งาน runtime selection tables ในการจัดการและเปลี่ยนแปลงค่ากำหนดค่าของ OpenFOAM

**🔍 Explanation**: 
Macro `addToRunTimeSelectionTable` นี้เป็นกลไกสำคัญที่ทำให้ OpenFOAM สามารถรองรับ plugin architecture ได้ Macro นี้จะลงทะเบียนคลาส `kEpsilon` เข้ากับตารางการเลือกประเภท (runtime selection table) ของ `turbulenceModel` โดยระบุว่า constructor รับพารามิเตอร์ประเภท `dictionary` เมื่อมีการเรียก `turbulenceModel::New()` ระบบจะค้นหาในตารางนี้และสร้างอินสแตนซ์ของคลาสที่ถูกต้อง

**🎯 Key Concepts**:
- **Runtime Selection Table**: ตารางการจัดเก็บข้อมูลคลาสที่สามารถสร้างแบบไดนามิก
- **Plugin Architecture**: สถาปัตยกรรมที่อนุญาตให้เพิ่มฟังก์ชันการทำงานโดยไม่ต้องแก้ไขโค้ดหลัก
- **Macro Registration**: การใช้ macro สำหรับลงทะเบียนคลาสอัตโนมัติ
- **Dictionary Constructor**: Constructor ที่รับพจนานุกรมเป็นพารามิเตอร์

---

Macro นี้จะ Register คลาสกับระบบเลือกประเภทใน Runtime โดยอัตโนมัติ

### 2. Strategy Pattern = **"คำนวณอย่างไร"**

ในขณะที่ Factory Pattern ตัดสินใจว่าจะ **สร้างอะไร** Strategy Pattern จะนิยาม **วิธีการ** ดำเนินการคำนวณ

**การห่อหุ้มอัลกอริทึม:**

```cpp
// Base class defining strategy interface for turbulence modeling
// All concrete models must implement these virtual methods
class turbulenceModel
{
public:
    // Pure virtual strategy interface - must be implemented by derived classes
    virtual tmp<volScalarField> nut() const = 0;      // Return turbulent viscosity
    virtual void correct() = 0;                       // Update turbulence fields
    virtual void correctNut() = 0;                    // Update turbulent viscosity
};
```

**📂 Source:** `.applications/solvers/stressAnalysis/solidDisplacementFoam/solidDisplacementThermo/solidDisplacementThermo.H`

---

**💡 Source**: 
ไฟล์หัวข้อของ `solidDisplacementThermo` ซึ่งเป็นคลาสสำหรับวิเคราะห์ความเครียด-การกระจัด (stress-displacement) แสดงให้เห็นถึงการใช้งาน Strategy pattern ในการกำหนดอินเทอร์เฟซสำหรับการคำนวณคุณสมบัติทางกายภาพ

**🔍 Explanation**: 
คลาส `turbulenceModel` นี้กำหนดอินเทอร์เฟซแบบ abstract (strategy interface) ที่โมเดลความปั่นป่วนทั้งหมดต้อง implement โดยใช้ pure virtual functions (`= 0`) แต่ละโมเดล (k-ε, k-ω, LES, ฯลฯ) สามารถใช้อัลกอริทึมที่แตกต่างกันอย่างสิ้นเชิงภายในเมธอดเหล่านี้ได้ แต่จะต้องให้บริการผ่านอินเทอร์เฟซเดียวกัน นี่คือหัวใจของ Strategy pattern ที่ทำให้สามารถเปลี่ยนอัลกอริทึมได้โดยไม่กระทบโค้ดที่เรียกใช้

**🎯 Key Concepts**:
- **Pure Virtual Functions**: ฟังก์ชันเสมือนแบบบริสุทธิ์ที่ต้องถูก implement โดย derived class
- **Strategy Interface**: อินเทอร์เฟซที่กำหนดวิธีการคำนวณ
- **Encapsulation**: การซ่อนรายละเอียดการ implement ไว้ภายในแต่ละคลาส
- **Polymorphism**: การทำงานแบบ polymorphic ผ่าน virtual functions

---

โมเดลความปั่นป่วนแบบ Derived ทั้งหมด (k-ε, k-ω, LES, ฯลฯ) จะต้อง Implement เมธอดเหล่านี้ แต่สามารถใช้อัลกอริทึมที่แตกต่างกันอย่างสิ้นเชิงภายในได้

**การ Implement ที่สามารถสลับที่กันได้:**

```cpp
// In solver code - works with any turbulence model implementation
// No need to know specific model details (k-ε, k-ω, LES, etc.)
turbulence->correct();          // Update turbulence fields (polymorphic call)
nut = turbulence->nut();        // Get turbulent viscosity (polymorphic call)
```

**📂 Source:** `.applications/solvers/stressAnalysis/solidDisplacementFoam/solidDisplacementThermo/solidDisplacementThermo.C`

---

**💡 Source**: 
ไฟล์ implementation ของ `solidDisplacementThermo` แสดงให้เห็นถึงการใช้งาน polymorphic calls ผ่าน pointer ของ base class ซึ่งเป็นหลักการของ Strategy pattern

**🔍 Explanation**: 
โค้ด solver ด้านบนแสดงให้เห็นถึงพลังของ Strategy pattern โค้ดไม่จำเป็นต้องรู้ว่า `turbulence` ชี้ไปที่อินสแตนซ์ของโมเดลใด (`kEpsilon`, `kOmegaSST`, `LESModel`, หรือโมเดลกำหนดเอง) การเรียก `turbulence->correct()` และ `turbulence->nut()` จะถูก dispatch ไปยัง implementation ที่เหมาะสมโดยอัตโนมัติผ่าน virtual function mechanism นี่ทำให้ solver สามารถทำงานกับโมเดลใดๆ ก็ได้ที่ implement อินเทอร์เฟซ `turbulenceModel` โดยไม่ต้องแก้ไขโค้ด

**🎯 Key Concepts**:
- **Polymorphic Calls**: การเรียกเมธอดแบบ polymorphic ผ่าน pointer ของ base class
- **Virtual Dispatch**: กลไกการเลือกเมธอดที่เหมาะสมใน runtime
- **Interface Segregation**: การแยกอินเทอร์เฟซให้เฉพาะเจาะจงและชัดเจน
- **Loose Coupling**: การลด coupling ระหว่าง solver และโมเดลความปั่นป่วน

---

ไม่ว่า `turbulence` จะชี้ไปที่ `kEpsilon`, `kOmegaSST` หรือโมเดลวิจัยแบบกำหนดเอง โค้ด Solver จะยังคงเหมือนเดิม

## พลังรวม = **กรอบ CFD ที่สามารถขยายได้**

เมื่อ Factory และ Strategy Patterns ทำงานร่วมกัน พวกเขาจะสร้างระบบที่มากกว่าผลรวมของส่วนประกอบแต่ละส่วน

### ฟิสิกส์ใหม่โดยไม่ต้องแก้ไขโค้ดหลัก

ในการเพิ่มโมเดลความปั่นป่วนใหม่:
1. **สร้าง Strategy Class**: Implement `turbulenceModel` Interface
2. **เพิ่มใน Factory Table**: Macro call เดียวสำหรับ Register
3. **กำหนดค่าใน Case**: ตั้งค่า `turbulenceModel  myNewModel;` ใน transportProperties

**ไม่ต้องแก้ไข** Solvers, การจัดการ Mesh, หรือสูตรคำนวณเชิงตัวเลขหลักเลย

## อนาล็อกี้: เครื่องจำหน่ายและชุดเครื่องมือ

**"เครื่องจำหน่ายสินค้าอัตโนมัติ" สำหรับ Factories**: รูปแบบ Factory ใน OpenFOAM ทำงานเหมือนเครื่องจำหน่ายสินค้าอัตโนมัติขั้นสูง คุณจะเข้าหา "เครื่องจำหน่าย" (`turbulenceModel::New()`) ด้วย "เงิน" (พารามิเตอร์อินพุต) และรับสิ่งที่คุณสั่งพอดี

**"โมดูลเสียบแล้วใช้ได้" สำหรับ Strategies**: รูปแบบ Strategy ใน OpenFOAM เหมือนอุปกรณ์ USB—ส่วนประกอบที่สามารถเปลี่ยนได้พร้อมอินเทอร์เฟซมาตรฐาน Gradient scheme (`Gauss`, `leastSquares`, `fourthGrad`) สามารถ "เสียบ" เข้ากับ discretization ใดๆ ได้

## ความสำคัญในบริบท CFD

ความงามของสถาปัตยกรรมนี้ปรากฏชัดในโซลเวอร์ที่ซับซ้อนที่สุดของ OpenFOAM:

```cpp
// 1. Strategy Interface (การนามธรรมอัลกอริทึม)
class physicsModel
{
public:
    // Pure virtual methods defining the strategy interface
    virtual void solve() = 0;                              // Main solve method
    virtual autoPtr<volScalarField> calculate() const = 0; // Calculation method

    // 2. Factory Method (การสร้างในรันไทม์)
    static autoPtr<physicsModel> New(const dictionary& dict);
};

// Usage in solver:
autoPtr<physicsModel> model = physicsModel::New(dict);  // Factory pattern
model->solve();                                          // Strategy pattern
```

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystem.H`

---

**💡 Source**: 
ไฟล์หัวข้อของ `phaseSystem` ซึ่งเป็นฐานคลาสสำหรับระบบหลายเฟสใน multiphaseEulerFoam solver แสดงให้เห็นถึงการผสมผสานระหว่าง Factory และ Strategy patterns ในระดับที่ซับซ้อน

**🔍 Explanation**: 
โค้ดนี้แสดงให้เห็นถึงการผสานรวมของสอง patterns ที่สำคัญ คลาส `physicsModel` กำหนด Strategy interface ผ่าน pure virtual methods (`solve()`, `calculate()`) ที่ทุกโมเดลฟิสิกส์ต้อง implement ในขณะเดียวกัน มี Factory method `New()` แบบ static ที่สร้างอินสแตนซ์ของโมเดลที่เหมาะสมจากพจนานุกรม การใช้งานใน solver แสดงให้เห็นถึงความง่ายในการใช้งาน: เพียงเรียก `New()` เพื่อสร้างโมเดล และ `solve()` เพื่อแก้สมการ โดยไม่ต้องรู้รายละเอียดของโมเดลที่แท้จริง

**🎯 Key Concepts**:
- **Factory-Strategy Synergy**: การผสานรวมของ Factory และ Strategy patterns
- **Pure Virtual Interface**: อินเทอร์เฟซที่กำหนดด้วย pure virtual methods
- **Static Factory Method**: เมธอด static สำหรับสร้างอ็อบเจกต์แบบไดนามิก
- **Runtime Polymorphism**: การทำงานแบบ polymorphic ใน runtime
- **Dictionary-Based Configuration**: การกำหนดค่าผ่านพจนานุกรม

---

รูปแบบนี้ช่วยให้ OpenFOAM สามารถรักษาอินเทอร์เฟซโซลเวอร์ที่สม่ำเสมอในขณะที่รองรับโมเดลฟิสิกส์ที่แตกต่างกันได้หลายสิบรูปแบบ

## ประโยชน์ด้านการออกแบบ

### 1. **การขยายตัว (Extensibility)**
- **โมเดลใหม่**: เพียงสืบทอดจาก base class และลงทะเบียน
- **ไม่ต้องแก้ไข core**: เพิ่มฟังก์ชันการทำงานโดยไม่ต้องแตะ code ที่มีอยู่
- **สถาปัตยกรรม plugin**: การโหลดแบบไดนามิกของ user-defined models

### 2. **การบำรุงรักษา (Maintainability)**
- **Single responsibility**: แต่ละ class มีจุดประสงค์เดียวที่ชัดเจน
- **Open/closed principle**: เปิดสำหรับการขยาย ปิดสำหรับการแก้ไข
- **Dependency injection**: การจัดการ dependencies อย่างชัดเจน

### 3. **ประสิทธิภาพ (Performance)**
- **การปรับให้เหมาะสมใน compile-time**: Template metaprogramming
- **ประสิทธิภาพใน runtime**: Virtual function overhead ขั้นต่ำ (<1% ของเวลาทำงาน)
- **ประสิทธิภาพหน่วยความจำ**: Smart pointers และ reference counting

### 4. **การใช้งาน (Usability)**
- **APIs ที่ตรงไปตรงมา**: High-level interfaces ซ่อนความซับซ้อน
- **การกำหนดค่าที่ยืดหยุ่น**: การเลือกโมเดลแบบ dictionary-based
- **การจัดการข้อผิดพลาด**: Validation และ messaging อย่างครอบคลุม

## เมทริกซ์รูปแบบการออกแบบใน OpenFOAM

สถาปัตยกรรมของ OpenFOAM ใช้ประโยชน์จากรูปแบบการออกแบบหลายแบบร่วมกัน:

| รูปแบบ | ตัวอย่าง | วัตถุประสงค์ | การใช้งานใน OpenFOAM |
|---------|---------|---------|-------------------------|
| **Factory Method** | `turbulenceModel::New()` | การสร้างออบเจกต์ | `declareRunTimeSelectionTable` |
| **Strategy** | `dragModel::K()` | การห่อหุ้มอัลกอริทึม | ฟังก์ชันเสมือนแบบบริสุทธิ์ |
| **Template Method** | `phaseModel::correct()` | โครงร่างอัลกอริทึม | ฟังก์ชันเสมือนที่มีการใช้งานเริ่มต้น |
| **Abstract Factory** | `phaseSystem::New()` | การสร้างแฟมิลี | Factory ที่ซ้อนกัน |

## เฟรมเวิร์กคณิตศาสตร์สำหรับการผสมผสานรูปแบบ

จากมุมมองทางคณิตศาสตร์ การผสมผสาน Factory-Strategy ใช้การแมปที่ซับซ้อนระหว่างช่องว่างพารามิเตอร์และการใช้งานอัลกอริทึม:

ให้:
- $\mathcal{A}$ เป็นช่องว่างอัลกอริทึม (การใช้งาน Strategy ทั้งหมดที่เป็นไปได้)
- $\mathcal{I}$ เป็นช่องว่างอินเทอร์เฟซ (การกำหนดคลาสฐานเสมือน)
- $\mathcal{F}$ เป็นฟังก์ชันการแมป Factory
- $\mathcal{P}$ เป็นช่องว่างพารามิเตอร์ (การกำหนดค่าพจนานุกรม)

ระบบที่ผสมผสานใช้ความสัมพันธ์ทางคณิตศาสตร์:

$$
\mathcal{F}: \mathcal{P} \to \mathcal{A} \to \mathcal{I}
$$

โดยที่:
- Strategy กำหนด $\mathcal{A} \to \mathcal{I}$ (การแมปอัลกอริทึมไปยังอินเทอร์เฟซ)
- Factory กำหนด $\mathcal{P} \to \mathcal{A}$ (การแมปพารามิเตอร์ไปยังการเลือกอัลกอริทึม)

## สรุปภาพรวม

ในบทนี้ เราจะโฟกัสที่สองรูปแบบที่สำคัญที่สุดคือ **Factory Pattern** และ **Strategy Pattern** ซึ่งเป็นหัวใจสำคัญที่ทำให้ OpenFOAM ก้าวข้ามขีดจำกัดของซอฟต์แวร์ CFD แบบดั้งเดิม

รูปแบบการออกแบบเหล่านี้แปลง CFD จาก "ฟิสิกส์ที่ Hardcoded" ไปสู่ "วิทยาศาสตร์การคำนวณที่สามารถขยายได้" พวกเขาแสดงถึงการเปลี่ยนแปลงทางปรัชญาที่:

- **กรอบงานให้โครงสร้าง** (การแบ่งส่วน Mesh, Linear Solvers, Parallelization)
- **โมเดลให้ฟิสิกส์** (Turbulence closure, การโต้ตอบหลายเฟส, ปฏิกิริยาเคมี)
- **Patterns ให้ความยืดหยุ่น** (ความสามารถในการขยายโดยไม่กระทบความแข็งแกร่ง)

ความสวยงามอยู่ที่ว่า Patterns เหล่านี้สอดคล้องกับวิธีคิดแบบ CFD อย่างเป็นธรรมชาติ:
- **Factory Pattern** ≈ การกำหนดค่า Case ที่ไม่ขึ้นกับ Mesh
- **Strategy Pattern** ≈ การเลือกโมเดลทางคณิตศาสตร์
- **การรวมกัน** ≈ ความสามารถ Plug-and-play ของ Solver ฟิสิกส์

## 🧠 ทดสอบความเข้าใจ (Concept Check)

<details>
<summary>1. Factory Pattern ใน OpenFOAM เปรียบเสมือนอะไรในชีวิตจริง?</summary>

**คำตอบ:** เปรียบเสมือน **"เครื่องจำหน่ายสินค้าอัตโนมัติ" (Vending Machine)** ที่เราใส่ข้อมูลระบุความต้องการ (เช่น เหรียญ หรือการเลือกสินค้า) แล้วเครื่องจะส่งสินค้า (Object) ที่ตรงตามความต้องการออกมาให้เรา โดยที่เราไม่ต้องรู้กลไกการผลิตภายใน
</details>

<details>
<summary>2. ความสัมพันธ์ทางคณิตศาสตร์ $\mathcal{F}: \mathcal{P} \to \mathcal{A} \to \mathcal{I}$ หมายความว่าอย่างไร?</summary>

**คำตอบ:** หมายถึงกระบวนการที่ **Factory ($\mathcal{F}$)** แปลง **พารามิเตอร์ ($\mathcal{P}$)** จาก Dictionary ให้เป็น **อัลกอริทึม ($\mathcal{A}$)** ที่เฉพาะเจาะจง ซึ่งอัลกอริทึมนั้นจะถูกใช้งานผ่าน **อินเทอร์เฟซมาตรฐาน ($\mathcal{I}$)**
</details>

## 📚 เอกสารที่เกี่ยวข้อง (Related Documents)

*   **ก่อนหน้า:** [00_Overview.md](00_Overview.md) - ภาพรวมของ Design Patterns ใน OpenFOAM
*   **ถัดไป:** [02_Factory_Pattern.md](02_Factory_Pattern.md) - เจาะลึก Factory Pattern ใน OpenFOAM