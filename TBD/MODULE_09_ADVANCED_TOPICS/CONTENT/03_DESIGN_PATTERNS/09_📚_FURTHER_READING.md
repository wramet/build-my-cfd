# 📚 บทอ่านเพิ่มเติม

## อ้างอิงรูปแบบการออกแบบ (Design Pattern References)

### **Gamma, et al.** *Design Patterns: Elements of Reusable Object-Oriented Software*
ข้อความพื้นฐานเกี่ยวกับรูปแบบการออกแบบซอฟต์แวร์ ซึ่งเป็นที่รู้จักกันทั่วไปในนาม "หนังสือของกลุ่มสี่คน" (Gang of Four) ผลงานนี้กำหนดรูปแบบการออกแบบคลาสสิก 23 รูปแบบ รวมถึง **Factory Method**, **Abstract Factory**, **Strategy**, **Observer**, และ **Template Method** ซึ่งถูกนำมาใช้อย่างกว้างขวางในสถาปัตยกรรมของ OpenFOAM หนังสือเล่มนี้ให้:

- รายการเป็นระบบของรูปแบบการสร้าง (creational) โครงสร้าง (structural) และพฤติกรรม (behavioral)
- รายละเอียดการนำไปใช้และข้อดีข้อเสียของแต่ละรูปแบบ
- ตัวอย่างจากโลกจริงที่แสดงให้เห็นถึงความสามารถในการนำรูปแบบไปใช้
- แนวทางสำหรับการประกอบรูปแบบและการใช้งาน

ในบริบทของ OpenFOAM รูปแบบเหล่านี้ปรากฏใน:
- **ระบบการเลือกขณะรันไทม์ (Runtime Selection System)**: รูปแบบ Factory Method และ Abstract Factory สำหรับการสร้างอินสแตนซ์ของโมเดล
- **สถาปัตยกรรมของ Linear Solver**: รูปแบบ Strategy สำหรับอัลกอริทึมของ Solver ที่แตกต่างกัน
- **การประมวลผล Mesh**: รูปแบบ Template Method สำหรับเวิร์กโฟลว์การจัดการ Mesh ที่สอดคล้องกัน

### **Alexandrescu, A.** *Modern C++ Design: Generic Programming and Design Patterns Applied*
การจัดการขั้นสูงของ Template Metaprogramming และการออกแบบตามนโยบาย (Policy-Based Design) ซึ่งเกี่ยวข้องโดยตรงกับการใช้ C++ Templates อย่างกว้างขวางของ OpenFOAM หนังสือเล่มนี้ครอบคลุม:

- **Policy-Based Design**: การสร้างองค์ประกอบที่ยืดหยุ่นผ่านพารามิเตอร์ของ Template
- **Template Specialization**: การเพิ่มประสิทธิภาพการนำไปใช้สำหรับชนิดข้อมูลเฉพาะ
- **Type Traits**: การวิเคราะห์และจัดการประเภทข้อมูลในขณะ Compile
- **Typelists**: การจัดการกลุ่มของประเภทข้อมูลในขณะ Compile

การใช้งานใน OpenFOAM ได้แก่:
- **ประเภทของ Field (Field Types)**: `volScalarField`, `volVectorField` ผ่าน Template Specialization
- **คลาส GeometricField**: Policy-Based Design สำหรับพฤติกรรมของ Field ที่แตกต่างกัน
- **การวิเคราะห์มิติ (Dimensional Analysis)**: Template Metaprogramming สำหรับการตรวจสอบความสอดคล้องของหน่วย
- **พีชคณิตเชิงเส้น (Linear Algebra)**: การดำเนินการเมทริกซ์และเวกเตอร์แบบ Template-Based

### **Fowler, M.** *Patterns of Enterprise Application Architecture*
แม้จะมุ่งเน้นไปที่แอปพลิเคชันระดับองค์กร แต่รูปแบบสถาปัตยกรรมที่นำเสนอสามารถนำไปใช้กับ CFD Frameworks ขนาดใหญ่อย่าง OpenFOAM ได้โดยตรง:

- **รูปแบบแหล่งข้อมูล (Data Source Patterns)**: รูปแบบการเข้าถึงฐานข้อมูลที่คล้ายคลึงกับการจัดการข้อมูล Field และ Mesh ของ OpenFOAM
- **รูปแบบ Object-Relational**: การจับคู่ระหว่างอ็อบเจกต์และการจัดเก็บข้อมูล คล้ายกับความสัมพันธ์ Field-Mesh ของ OpenFOAM
- **รูปแบบตรรกะโดเมน (Domain Logic Patterns)**: รูปแบบการจัดระเบียบตรรกะธุรกิจที่สามารถนำไปใช้กับการนำโมเดลฟิสิกส์ไปใช้
- **รูปแบบการนำเสนอเว็บ (Web Presentation Patterns)**: หลักการแยกความกังวล (Separation of Concerns) ที่เกี่ยวข้องกับการแยก Solver/approach ของ OpenFOAM

## ทรัพยากรเฉพาะของ OpenFOAM

### **ซอร์สโค้ด OpenFOAM** `src/OpenFOAM/db/runTimeSelection/`
หัวใจของกลไกการขยายความสามารถของ OpenFOAM ซึ่งนำไปใช้ระบบการเลือกขณะรันไทม์ องค์ประกอบสำคัญได้แก่:

```cpp
// Runtime selection macros
#define addToRunTimeSelectionTable\
(\
    baseType,\
    thisType,\
    argNames\
)

// Usage example in turbulence models
addToRunTimeSelectionTable
(
    incompressible::turbulenceModel,
    kOmegaSST,
    dictionary
);
```

**คลาสสำคัญ:**
- **`runTimeSelectionTable`**: คลาส Template ที่จัดการการลงทะเบียนโมเดล
- **`autoPtr<T>`**: Smart Pointer สำหรับการจัดการหน่วยความจำอัตโนมัติ
- **`dictionary`**: โครงสร้างข้อมูลการกำหนดค่าสำหรับพารามิเตอร์ของโมเดล
- **`wordList`**: รายการสตริงสำหรับการเลือกโมเดล

**ข้อดีทางสถาปัตยกรรม:**
- **สถาปัตยกรรมปลั๊กอิน (Plugin Architecture)**: สามารถเพิ่มโมเดลใหม่ได้โดยไม่ต้องแก้ไข Core Solvers
- **ความปลอดภัยของประเภท (Type Safety)**: การตรวจสอบอินเตอร์เฟซของโมเดลในขณะ Compile
- **การจัดการหน่วยความจำ**: การทำความสะอาดอัตโนมัติผ่านรูปแบบ RAII
- **ขับเคลื่อนโดยการกำหนดค่า (Configuration-Driven)**: การเลือกโมเดลผ่าน Dictionaries ที่ใช้ข้อความ

### **คู่มือโปรแกรมเมอร์ OpenFOAM (OpenFOAM Programmer's Guide)**
เอกสารอย่างเป็นทางการที่ให้ความครอบคลุมเกี่ยวกับกลไกการเลือกขณะรันไทม์:

**แนวทางการนำไปใช้:**
```cpp
// Base class with virtual constructor
class myBaseClass
{
public:
    // Runtime selector
    static autoPtr<myBaseClass> New(const word& type, const dictionary& dict);
    
    // Pure virtual interface
    virtual void solve() = 0;
    
    virtual ~myBaseClass() = default;
};

// Derived class implementation
class myDerivedClass : public myBaseClass
{
    TypeName("myDerivedModel");
    
    virtual void solve() override
    {
        // Implementation details
    }
};
```

**แนวทางปฏิบัติที่ดีที่สุด:**
- การใช้แบบแผนการตั้งชื่อที่สอดคล้องกันสำหรับประเภทของโมเดล
- การจัดการข้อผิดพลาดที่เหมาะสมสำหรับการเลือกโมเดลที่ไม่ถูกต้อง
- การจัดทำเอกสารพารามิเตอร์ของโมเดลและค่าเริ่มต้น
- การตรวจสอบความถูกต้องของพารามิเตอร์อินพุตในระหว่างการสร้าง

### **ซอร์สโค้ด `multiphaseEulerFoam`**
การนำไปใช้ในโลกจริงที่แสดงให้เห็นถึงการใช้รูปแบบอย่างครบถ้วนในการจำลองการไหลแบบหลายเฟส (multiphase flow):

**รูปแบบการนำไปใช้ที่สำคัญ:**

```cpp
// Factory pattern for phase models
template<class Type>
class phaseModel
{
public:
    // Runtime constructor
    static autoPtr<phaseModel> New
    (
        const dictionary& phaseDict,
        const volScalarField& alpha,
        const volVectorField& U
    );
    
    // Strategy pattern for phase properties
    virtual tmp<volScalarField> rho() const = 0;
    virtual tmp<volScalarField> mu() const = 0;
};

// Template Method pattern for solution algorithm
class multiphaseSystem
{
    void solve()
    {
        // Template method defining solution steps
        preSolve();
        solveMomentum();
        solveContinuity();
        correct();
        postSolve();
    }
    
protected:
    virtual void preSolve() {}
    virtual void correct() {}
};
```

**จุดเด่นทางสถาปัตยกรรม:**
- **โครงสร้างโมเดลแบบลำดับชั้น (Hierarchical Model Structure)**: คลาสฐานพร้อมการนำไปใช้เฉพาะทาง
- **การสื่อสารระหว่างโมเดล (Inter-model Communication)**: อินเตอร์เฟซที่สอดคล้องกันสำหรับการโต้ตอบของโมเดล
- **การผสานรวมวิธีการเชิงตัวเลข (Numerical Methods Integration)**: การผสานรวมที่ราบรื่นกับ Linear Solvers และ Discretization Schemes
- **การสนับสนุนการประมวลผลแบบขนาน (Parallel Computing Support)**: การสร้างการสลายตัวและการสื่อสารแบบขนานในตัว

## CFD และวิธีการเชิงตัวเลข

### **Ferziger & Perić** *Computational Methods for Fluid Dynamics*
การจัดการอย่างครบถ้วนของวิธีการเชิงตัวเลขสำหรับการจำลองการไหลของของไหล ซึ่งให้พื้นฐานทางทฤษฎีสำหรับการนำไปใช้ของ OpenFOAM:

**พื้นฐานอัลกอริทึม:**
- **วิธีการปริมาตรจำกัด (Finite Volume Method)**: หลักการอนุรักษ์และเทคนิคการ Discretization
- **การเชื่อมโยงความดัน-ความเร็ว (Pressure-Velocity Coupling)**: อัลกอริทึม SIMPLE, SIMPLEC และ PISO
- **Linear Solvers**: วิธีการวนซ้ำและเกณฑ์การลู่เข้า
- **การสร้างแบบจำลองความปั่นป่วน (Turbulence Modeling)**: แนวทาง RANS, LES และ DES

**กรอบทางคณิตศาสตร์:**
$$\frac{\partial (\rho \phi)}{\partial t} + \nabla \cdot (\rho \mathbf{u} \phi) = \nabla \cdot (\Gamma \nabla \phi) + S_\phi$$

โดยที่ $\phi$ แทนปริมาณใดๆ ที่ถูกขนส่ง, $\Gamma$ คือสัมประสิทธิ์การแพร่ และ $S_\phi$ แทนเทอมต้นทาง

**เทคนิคการ Discretization:**
```cpp
// Gauss divergence theorem implementation
template<class Type>
tmp<GeometricField<Type, fvsPatchField, surfaceMesh>>
div
(
    const GeometricField<Type, fvPatchField, volMesh>& vf
)
{
    return surfaceIntegrate
    (
        mesh().Sf() & vf.interpolate()
    );
}
```

### **Versteeg & Malalasekera** *An Introduction to Computational Fluid Dynamics*
แนวทางปฏิบัติสำหรับการนำ CFD ไปใช้ ซึ่งเชื่อมโยงทฤษฎีกับการประยุกต์ใช้:

**การนำ Solver ไปใช้:**
```cpp
// Pressure-velocity coupling (SIMPLE algorithm)
while (pimple.correctNonOrthogonal())
{
    // Momentum predictor
    tmp<fvVectorMatrix> UEqn
    (
        fvm::div(rhoPhi, U)
      + fvm::Sp(phase.pressureWorkCoeff(), U)
     ==
        phase.momentumSource()
    );
    
    // Pressure equation
    fvScalarMatrix pEqn
    (
        fvm::laplacian(phase.rho()*rAUf(), p) == fvc::ddt(phase.rho())
    );
    
    pEqn.solve();
}
```

**การนำเงื่อนไขขอบเขตไปใช้:**
```cpp
// Fixed value boundary condition
template<class Type>
class fixedValueFvPatchField : public fvPatchField<Type>
{
public:
    // Update coefficients for matrix assembly
    virtual void updateCoeffs()
    {
        if (this->updated())
        {
            return;
        }
        
        fvPatchField<Type>::operator=(this->patchInternalField());
        fvPatchField<Type>::updateCoeffs();
    }
};
```

**หัวข้อการนำไปใช้ที่สำคัญ:**
- **การสร้าง Mesh และคุณภาพ**: การพิจารณาด้านโทโพโลยีและความตั้งฉากของ Grid
- **Discretization Schemes**: Schemes แบบ Upwind, Central Differencing และลำดับที่สูงขึ้น
- **การเร่งความเร็วการลู่เข้า (Convergence Acceleration)**: วิธีการ Multigrid และเทคนิคการ Preconditioning
- **การประมวลผลแบบขนาน (Parallel Processing)**: กลยุทธ์การสลายตัวโดเมนและการสมดุลภาระงาน

ทรัพยากรเหล่านี้ให้พื้นฐานทางทฤษฎีและการปฏิบัติสำหรับการเข้าใจสถาปัตยกรรมที่ซับซ้อนของ OpenFOAM และวิธีการนำ CFD ไปใช้ ทำให้นักพัฒนาสามารถขยายและปรับแต่ง Framework ได้อย่างมีประสิทธิภาพ
