# 07 โปรเจกต์ปฏิบัติ (Practical Project)

![[practical_project_overview.png]]
`A clean scientific illustration of a "Developer's Workshop". Show a computer screen with C++ code on one side and a 3D visualization of a non-Newtonian flow in a pipe on the other side. Surround the screen with icons for "Compilation", "Registration", and "Validation". Use a minimalist palette, scientific textbook diagram, clean vector line art, white background, high definition, flat design, educational infographic --ar 16:9`

## ภาพรวมของหัวข้อ

ยินดีต้อนรับสู่โปรเจกต์ปฏิบัติของโมดูลนี้ ซึ่งเป็นจุดสูงสุดของการเรียนรู้ที่จะนำความรู้ทั้งหมดที่ได้เรียนมา—ตั้งแต่ Template Programming, Inheritance, Design Patterns ไปจนถึง Memory Management—มาประยุกต์ใช้ในโปรเจกต์การพัฒนาโมเดลฟิสิกส์จริงใน OpenFOAM

เป้าหมายของโปรเจกต์นี้คือการสร้าง **โมเดลความหนืดแบบกำหนดเอง (Custom Viscosity Model)** ซึ่งจะช่วยให้คุณเห็นภาพรวมว่าสถาปัตยกรรมที่ซับซ้อนของ OpenFOAM ทำงานร่วมกันอย่างไรเพื่อสร้างระบบ CFD ที่ยืดหยุ่นและขยายความสามารถได้

## วัตถุประสงค์การเรียนรู้

เมื่อสำเร็จโครงการนี้ คุณจะสามารถ:

1. **สร้างโมเดลทางกายภาพแบบกำหนดเองที่สมบูรณ์** จากศูนย์
2. **เชี่ยวชาญระบบการเลือกแบบ runtime ของ OpenFOAM** (รูปแบบ factory)
3. **ประยุกต์ใช้การเขียนโปรแกรมเชิง template** สำหรับการดำเนินการฟิลด์แบบ generic
4. **ออกแบบลำดับชั้นคลาสที่เหมาะสม** ด้วยอินเทอร์เฟซเชิงเสมือน
5. **ผสานรวมโค้ดแบบกำหนดเอง** เข้ากับระบบการสร้างของ OpenFOAM
6. **ทดสอบและตรวจสอบความถูกต้อง** โมเดลของคุณในการจำลองจริง

## ขอบเขตโปรเจกต์

โปรเจกต์นี้จะสร้างโมเดล `powerLawViscosity` ที่ implement ความสัมพันธ์แบบ power-law สำหรับของไหลที่ไม่ใช่นิวตัน:

$$
\mu(\dot{\gamma}) = K \, \dot{\gamma}^{\,n-1}
$$

โดยที่:
- $\mu$ คือความหนืดแบบพลวัต (dynamic viscosity)
- $K$ คือดัชนีความสม่ำเสมอ (consistency index)
- $n$ คือดัชนี power-law (power-law index)
- $\dot{\gamma}$ คือขนาดของอัตราการเฉือน (shear rate magnitude)

### ความสำคัญของโมเดล Power-Law

โมเดลความหนืดแบบ power-law มีความสำคัญอย่างยิ่งเนื่องจาก:
- ขยายความสามารถของ OpenFOAM จากของไหลนิวตันไปสู่การจัดการพฤติกรรมที่ซับซ้อนของของไหลที่ไม่ใช่นิวตัน
- ใช้ในการประมวลผลพอลิเมอร์, การผลิตอาหาร, และการไหลของชีวะภาพ
- จับกลไกทางกายภาพของของไหลแบบตัดแรงเฉือน (pseudoplastic) และของไหลแบบเพิ่มแรงเฉือน (dilatant)
  - $n < 1$: พฤติกรรมการตัดแรงเฉือน (shear-thinning)
  - $n > 1$: พฤติกรรมการเพิ่มแรงเฉือน (shear-thickening)

## สิ่งที่จะได้เรียนรู้และลงมือทำ

ในโปรเจกต์นี้ คุณจะได้สัมผัสกับการสังเคราะห์แนวคิด (Synthesis of Concepts) ดังนี้:

### 1. Runtime Selection

การใช้มาโคร `addToRunTimeSelectionTable` เพื่อให้โมเดลของคุณถูกเลือกผ่าน Dictionary ได้:

```cpp
// Register the custom viscosity model in the runtime selection table
// This allows the model to be selected at runtime through dictionary
addToRunTimeSelectionTable
(
    viscosityModel,              // Base class name
    powerLawViscosity,           // Derived class name
    dictionary                   // Constructor argument type
);
```

**📖 คำอธิบาย (Source/Explanation/Key Concepts):**

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/InterfaceCompositionPhaseChangePhaseSystem/InterfaceCompositionPhaseChangePhaseSystem.C:38-76`

**💡 คำอธิบาย:**
มาโคร `addToRunTimeSelectionTable` เป็นกลไกสำคัญของ OpenFOAM ที่ทำให้โมเดลที่กำหนดเองสามารถถูกเลือกและใช้งานได้ในขณะ runtime โดยไม่ต้องคอมไพล์โปรแกรมใหม่ การลงทะเบียนนี้จะสร้างตารางข้อมูลภายในที่เก็บข้อมูลเกี่ยวกับคลาสลูกค่า ชื่อคลาส และประเภทอาร์กิวเมนต์ที่ต้องการสำหรับการสร้างออบเจกต์

**🔑 Key Concepts:**
- **Runtime Selection Table**: ตารางข้อมูลภายในที่เชื่อมโยงชื่อโมเดล (เช่น "powerLaw") กับฟังก์ชันการสร้างออบเจกต์
- **Factory Pattern**: รูปแบบการออกแบบที่อนุญาตให้สร้างออบเจกต์โดยไม่ต้องระบุคลาสที่แน่นอนในโค้ด
- **Dictionary-based Configuration**: การกำหนดค่าผ่านไฟล์ dictionary ทำให้ผู้ใช้สามารถเปลี่ยนโมเดลได้โดยไม่ต้องแก้โค้ด

---

ซึ่งช่วยให้ผู้ใช้เลือกโมเดลผ่านไฟล์ `transportProperties`:

```cpp
// Select the viscosity model type in transportProperties dictionary
viscosityModel  powerLaw;

// Model-specific coefficients
powerLawCoeffs
{
    K       0.01;     // Consistency index [Pa.s^n]
    n       0.7;      // Power-law index (dimensionless)
    nuMin   1e-6;     // Minimum viscosity limit [m^2/s]
    nuMax   1e6;      // Maximum viscosity limit [m^2/s]
}
```

**📖 คำอธิบาย (Source/Explanation/Key Concepts):**

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/InterfaceCompositionPhaseChangePhaseSystem/InterfaceCompositionPhaseChangePhaseSystem.C:90-100`

**💡 คำอธิบาย:**
ไฟล์ `transportProperties` เป็นจุดเชื่อมต่อระหว่างผู้ใช้และระบบ runtime selection ของ OpenFOAM เมื่อ solver เริ่มทำงาน ระบบจะอ่านคีย์เวิร์ด `viscosityModel` และค้นหาใน runtime selection table เพื่อสร้างออบเจกต์ของคลาสที่เหมาะสม (ในที่นี้คือ `powerLawViscosity`)

**🔑 Key Concepts:**
- **Dictionary Lookup**: กระบวนการค้นหาชื่อโมเดลในตาราง runtime selection
- **Coefficient Dictionary**: การจัดเก็บพารามิเตอร์เฉพาะของโมเดลใน sub-dictionary
- **Parameter Validation**: การตรวจสอบค่าพารามิเตอร์ที่อ่านจากไฟล์ (เช่น ค่า K, n, nuMin, nuMax)

---

### 2. Template Programming

การจัดการฟิลด์อย่างมีประสิทธิภาพด้วย `tmp<volScalarField>` และ template operations:

```cpp
// Calculate viscosity using template-based field operations
// Returns a temporary field object for efficient memory management
tmp<volScalarField> calcNu() const
{
    // Create temporary scalar field with calculated viscosity values
    tmp<volScalarField> tnu
    (
        new volScalarField
        (
            IOobject("nu", mesh_.time().timeName(), mesh_),
            K_ * pow(max(shearRate, dimensionedScalar("small", dimless/dimTime, SMALL)), n_ - 1.0)
        )
    );
    return tnu;
}
```

**📖 คำอธิบาย (Source/Explanation/Key Concepts):**

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/InterfaceCompositionPhaseChangePhaseSystem/InterfaceCompositionPhaseChangePhaseSystem.C:84-88`

**💡 คำอธิบาย:**
ฟังก์ชัน `calcNu()` แสดงให้เห็นถึงพลังของ template programming และการจัดการหน่วยความจำใน OpenFOAM การใช้ `tmp<volScalarField>` ช่วยลดการคัดลอกหน่วยความจำโดยอัตโนมัติผ่าน reference counting สูตรคำนวณใช้ template operations เพื่อสร้าง expression tree ที่มีประสิทธิภาพ

**🔑 Key Concepts:**
- **tmp<T> Smart Pointer**: ตัวชี้อัจฉริยะที่จัดการวงจรชีวิตของออบเจกต์ชั่วคราวโดยอัตโนมัติ
- **Expression Templates**: เทคนิคการสร้าง expression tree เพื่อหลีกเลี่ยงการสร้างออบเจกต์ชั่วคราวที่ไม่จำเป็น
- **DimensionedScalar**: ประเภทข้อมูลที่มีการตรวจสอบมิติ (dimensional consistency checking) ในขณะคอมไพล์
- **Field Algebra**: การดำเนินการทางคณิตศาสตร์บนฟิลด์ทั้งช่องตาข่ายพร้อมกัน

---

### 3. Inheritance & Polymorphism

การสืบทอดจาก `viscosityModel` เพื่อสร้างอินเทอร์เฟซที่สอดคล้องกับระบบ:

```cpp
// Custom viscosity model class inheriting from base viscosityModel
class powerLawViscosity
:
    public viscosityModel
{
    // Pure virtual interface implementation
    // These methods MUST be implemented to conform to the interface
    virtual tmp<volScalarField> nu() const;      // Return viscosity field
    virtual void correct();                      // Update model calculations
    virtual bool read();                         // Re-read coefficients from dictionary
};
```

**📖 คำอธิบาย (Source/Explanation/Key Concepts):**

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/InterfaceCompositionPhaseChangePhaseSystem/InterfaceCompositionPhaseChangePhaseSystem.C:34-76`

**💡 คำอธิบาย:**
การสืบทอดจาก `viscosityModel` เป็นหัวใจสำคัญของการสร้างโมเดลฟิสิกส์ที่เข้ากันได้กับระบบ OpenFOAM คลาสฐาน `viscosityModel` กำหนด interface ที่เป็นนามธรรม (pure virtual functions) ซึ่งคลาสลูกทุกคลาสต้อง implement นี่คือหลักการของ polymorphism ที่ทำให้ solver สามารถทำงานกับโมเดลใดๆ ผ่าน interface ร่วมกันได้

**🔑 Key Concepts:**
- **Base Class Interface**: `viscosityModel` กำหนด contract ที่โมเดลทั้งหมดต้องปฏิบัติตาม
- **Virtual Functions**: ฟังก์ชันเสมือนช่วยให้มีการเรียกใช้ method ที่ถูกต้องตามประเภทจริงของออบเจกต์
- **Pure Virtual Methods**: `nu()`, `correct()`, และ `read()` ต้องถูก implement ในคลาสลูกทุกคลาส
- **Runtime Polymorphism**: ระบบสามารถเลือก method ที่เหมาะสมในขณะ runtime โดยไม่ต้องรู้คลาสที่แน่นอน

---

### 4. Factory Pattern

การทำความเข้าใจกลไกที่ `viscosityModel::New()` ใช้สร้างออบเจกต์ของคุณ:

```cpp
// Factory method declaration in base class
// Creates and returns a smart pointer to the appropriate viscosity model
static autoPtr<viscosityModel> New
(
    const volVectorField&,      // Velocity field reference
    const dictionary&           // Dictionary containing model configuration
);
```

**📖 คำอธิบาย (Source/Explanation/Key Concepts):**

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/InterfaceCompositionPhaseChangePhaseSystem/InterfaceCompositionPhaseChangePhaseSystem.C:79-88`

**💡 คำอธิบาย:**
ฟังก์ชัน `New()` เป็น factory method ที่จัดการกระบวนการสร้างออบเจกต์โมเดลความหนืดโดยอัตโนมัติ เมื่อเรียกใช้ ระบบจะ:
1. อ่านชื่อโมเดลจาก dictionary (เช่น "powerLaw")
2. ค้นหาใน runtime selection table
3. เรียก constructor ที่เหมาะสม
4. ส่งคืน smart pointer (`autoPtr`) ที่จัดการการลบออบเจกต์โดยอัตโนมัติ

**🔑 Key Concepts:**
- **Static Factory Method**: ฟังก์ชัน static ที่สร้างและส่งคืนออบเจกต์ที่เหมาะสม
- **autoPtr<T>**: ตัวชี้อัจฉริยะที่เป็นเจ้าของออบเจกต์และจัดการการลบโดยอัตโนมัติเมื่อไม่ใช้งาน
- **Encapsulation of Creation Logic**: ซ่อนความซับซ้อนของการสร้างออบเจกต์ไว้ใน factory method
- **Decoupling**: Client code (solver) ไม่ต้องรู้รายละเอียดของคลาสที่แน่นอน แต่ทำงานผ่าน interface ร่วมกัน

---

### 5. OpenFOAM Build System

การจัดการไฟล์ `Make/files` และ `Make/options` เพื่อคอมไพล์โปรเจกต์:

**Make/files:**
```makefile
# Source files to compile
powerLawViscosity/powerLawViscosity.C

# Output library path and name
LIB = $(FOAM_USER_LIBBIN)/libcustomViscosityModels
```

**📖 คำอธิบาย (Source/Explanation/Key Concepts):**

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/InterfaceCompositionPhaseChangePhaseSystem/InterfaceCompositionPhaseChangePhaseSystem.C:26-30`

**💡 คำอธิบาย:**
ไฟล์ `Make/files` ระบุ source files ที่ต้องคอมไพล์และตำแหน่งที่จะเก็บ library ที่สร้างขึ้น ในที่นี้เราคอมไพล์ไฟล์ `powerLawViscosity.C` และสร้าง library ชื่อ `libcustomViscosityModels` ในโฟลเดอร์ user libraries ของ OpenFOAM

**🔑 Key Concepts:**
- **Source File Specification**: ระบุไฟล์ .C ที่ต้องคอมไพล์ (สามารถระบุหลายไฟล์)
- **Library Target**: `LIB` ระบุชื่อและตำแหน่งของ library ที่สร้างขึ้น
- **FOAM_USER_LIBBIN**: Environment variable ที่ชี้ไปยังโฟลเดอร์เก็บ libraries ของผู้ใช้
- **Library Naming Convention**: ชื่อ library ควรขึ้นต้นด้วย "lib" และลงท้ายด้วยชื่อที่สื่อความหมาย

---

**Make/options:**
```makefile
# Include directories for compilation
EXE_INC = \
    -I$(LIB_SRC)/finiteVolume/lnInclude \
    -I$(LIB_SRC)/transportModels/lnInclude

# Libraries to link against
EXE_LIBS = \
    -lfiniteVolume \
    -ltransportModels
```

**📖 คำอธิบาย (Source/Explanation/Key Concepts):**

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/InterfaceCompositionPhaseChangePhaseSystem/InterfaceCompositionPhaseChangePhaseSystem.C:26-30`

**💡 คำอธิบาย:**
ไฟล์ `Make/options` ระบุการตั้งค่าคอมไพล์เลอร์ รวมถึง include paths สำหรับ header files และ libraries ที่ต้อง link ในที่นี้เราต้องการ:
- `finiteVolume`: สำหรับคลาสฟิลด์และ finite volume method
- `transportModels`: สำหรับคลาสฐาน `viscosityModel`

**🔑 Key Concepts:**
- **Include Paths (`EXE_INC`)**: ระบุตำแหน่ง header files ด้วย flag `-I`
- **Library Dependencies (`EXE_LIBS`)**: ระบุ libraries ที่ต้อง link ด้วย flag `-l`
- **lnInclude Directory**: โฟลเดอร์พิเศษของ OpenFOAM ที่รวบรวม header files ทั้งหมดไว้ที่เดียว
- **Dependency Management**: ต้องระบุ libraries ที่โค้ดของเราใช้งาน

---

## ความท้าทายทางเทคนิค

คุณจะต้องเผชิญกับความท้าทายดังนี้:

1. **การนำทางลำดับชั้นการสืบทอดที่ซับซ้อน** ของ OpenFOAM
2. **Implement การดำเนินการฟิลด์แบบ template** ที่รักษาความปลอดภัยของประเภทข้อมูลขณะเดียวกันให้ประสิทธิภาพการคำนวณ
3. **สร้างกลไกการเลือกแบบ runtime** ที่อนุญาตให้ผู้ใช้เลือกโมเดลผ่านรายการ dictionary โดยไม่ต้องคอมไพล์ใหม่
4. **การคำนวณอัตราการเฉือน**:
   $$\dot{\gamma} = \sqrt{2 \cdot \mathbf{S} : \mathbf{S}}$$
   โดยที่ $\mathbf{S} = \frac{1}{2}(\nabla\mathbf{u} + \nabla\mathbf{u}^T)$ เป็นเทนเซอร์อัตราการยืดตัว

## จุดการผสานรวม

โมเดลสุดท้ายจะเชื่อมต่อโดยตรงเข้ากับกรอบการทำงานโมเดลการขนส่งที่มีอยู่ของ OpenFOAM ทำให้สามารถใช้งานได้ทันทีใน solvers มาตรฐาน เช่น:

- `simpleFoam` - สำหรับ steady-state incompressible flows
- `pimpleFoam` - สำหรับ transient incompressible flows
- Solvers หลายเฟสที่เฉพาะทาง

โดยไม่ต้องแก้ไขโค้ด solver หลัก

## ข้อกำหนดเบื้องต้น (Prerequisites)

- **ความเข้าใจในหัวข้อ 01 ถึง 06**: โปรเจกต์นี้ต้องการความรู้พื้นฐานจากทุกบทก่อนหน้า
- **ทักษะการใช้ Terminal**: การคอมไพล์โค้ดด้วย `wmake`
- **ความรู้พื้นฐานด้านฟิสิกส์ของไหล**: ความเข้าใจเรื่องความหนืด (Viscosity) และอัตราการเสียรูป (Strain Rate)

## เนื้อหาในบทนี้

1. **01_Project_Overview.md**: รายละเอียดและเป้าหมายของโปรเจกต์
2. **02_Model_Development_Rationale.md**: เหตุผลเบื้องหลังการสร้างโมเดลแบบกำหนดเอง (The Hook)
3. **03_Folder_and_File_Organization.md**: การจัดระเบียบโครงสร้างโฟลเดอร์และไฟล์ (The Blueprint)
4. **04_Compilation_Process.md**: เจาะลึกกลไกการคอมไพล์และ Build System (Internal Mechanics)
5. **05_Inheritance_and_Virtual_Functions.md**: การประยุกต์ใช้การสืบทอดในโมเดลจริง (The Mechanism)
6. **06_Design_Pattern_Rationale.md**: เหตุผลทางสถาปัตยกรรมเบื้องหลังการออกแบบ (The Why)
7. **07_Common_Errors_and_Debugging.md**: เวิร์กโฟลว์การใช้งานและการแก้ไขข้อผิดพลาด
8. **08_Final_Challenge.md**: บทสรุปและการท้าทายเพื่อต่อยอดโมเดลของคุณ

## ปรัชญาหลัก: "Learning by Doing"

โปรเจกต์นี้ไม่ได้เป็นเพียงการเขียนโค้ดตามคำสั่ง แต่เป็นการฝึกฝนให้คุณเป็น **OpenFOAM Developer**:

- **Synthesis over Analysis**: เน้นการนำองค์ประกอบย่อยๆ มารวมกันเป็นระบบที่ใช้งานได้จริง
- **Professional Standards**: ทำตามมาตรฐานการเขียนโค้ดและโครงสร้างของ OpenFOAM
- **Scalable Thinking**: คิดถึงการออกแบบโมเดลที่สามารถขยายไปใช้ในกรณีอื่นๆ ได้ในอนาคต

## สถาปัตยกรรมเชิงแนวคิด

```
┌─────────────────────────────────────────────────────────┐
│                 Solver (e.g., simpleFoam)                 │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────┐
        │   Factory Method        │
        │ viscosityModel::New()   │
        └─────────┬───────────────┘
                  │
        ┌─────────┴───────────────┐
        │   Runtime Selection     │
        │   (Dictionary lookup)   │
        └─────────┬───────────────┘
                  │
        ┌─────────┴───────────────┐
        │  powerLawViscosity      │
        │  (Your Custom Model)    │
        └─────────────────────────┘
                  │
        ┌─────────┴───────────────┐
        │  Template Operations   │
        │  - tmp<volScalarField> │
        │  - Field algebra       │
        │  - Dimension checking  │
        └─────────────────────────┘
```

## ความสำเร็จที่คาดหวัง

หลังจากเสร็จสิ้นโปรเจกต์นี้ คุณจะ:

1. **มีโมเดลความหนืดแบบ custom ที่ใช้งานได้จริง** ซึ่งสามารถนำไปใช้กับ case จริงได้ทันที
2. **เข้าใจสถาปัตยกรรมภายในของ OpenFOAM** ในระดับลึก
3. **สามารถสร้างโมเดลฟิสิกส์แบบกำหนดเองเพิ่มเติม** ได้ด้วยตัวเอง
4. **พร้อมที่จะมีส่วนร่วมกับชุมชน OpenFOAM** ด้วยโมเดลที่คุณพัฒนาขึ้น

---

**คำแนะนำ**: เริ่มต้นโปรเจกต์นี้ด้วยใจเปิจ พร้อมที่จะทดลองและเรียนรู้จากข้อผิดพลาด ทักษะที่คุณจะได้รับจากโปรเจกต์นี้จะมีคุณค่าอย่างยิ่งสำหรับการพัฒนา CFD ในระดับมืออาชีพ