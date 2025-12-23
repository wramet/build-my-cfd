# 🧩 สถาปัตยกรรมขั้นสูง: ความสามารถในการขยายใน OpenFOAM

สถาปัตยกรรมของ OpenFOAM ถูกออกแบบมาโดยพื้นฐานที่เน้นความสามารถในการขยาย (extensibility) โดยจัดเตรียมกรอบงานที่ครอบคลุมซึ่งอนุญาตให้นักวิจัย วิศวกร และนักพัฒนาสามารถขยายความสามารถผ่านกลไกหลายรูปแบบ สถาปัตยกรรมความสามารถในการขยายถูกสร้างขึ้นบนหลักการหลักหลายประการ:

## ปรัชญาการออกแบบที่ใช้ Template

ในแกนกลางของ OpenFOAM ใช้วิธีการ Template Metaprogramming ที่ซับซ้อนซึ่งเปิดใช้งาน polymorphism ระดับ compile-time และ type safety รูปแบบการออกแบบนี้ปรากฏอยู่ทั่วทั้ง codebase:

```cpp
// ตัวอย่างความสามารถในการขยายแบบ template ของ OpenFOAM
template<class Type>
class GeometricField
{
    // Field operations ที่ทำงานกับ scalar, vector, tensor fields
    template<class Type2>
    void operator=(const GeometricField<Type2>&);
};

// Solvers ที่เฉพาะเจาะจงสำหรับฟิสิกส์ที่แตกต่างกัน
template<class Type>
class GAMGSolver : public LduMatrix<Type, Type, Type>::solver
{
    // Generic solver implementation
};
```

แนวทางแบบ template นี้อนุญาตให้ผู้ใช้สามารถ:
- สร้างประเภท field ใหม่ (scalar, vector, tensor, complex)
- สร้าง solvers ที่เฉพาะเจาะจงสำหรับฟิสิกส์เฉพาะทาง
- พัฒนา boundary conditions แบบกำหนดเองพร้อม type safety
- ขยาย numerical schemes ในขณะที่ยังคงประสิทธิภาพ

## สถาปัตยกรรม Solver แบบโมดูลาร์

ความสามารถในการขยาย solver ของ OpenFOAM ปฏิบัติตามรูปแบบการย่อยสลายแบบลำดับชั้น ซึ่งปัญหาฟิสิกส์ที่ซับซ้อนจะถูกแบ่งออกเป็นส่วนประกอบที่ใช้ซ้ำได้:

### รูปแบบการย่อยสลายหลัก
```cpp
// โครงสร้าง solver ทั่วไปที่แสดงจุดที่สามารถขยายได้
solver
├── Mesh (fvMesh)
├── Physics Models
│   ├── Turbulence models (RASModel, LESModel)
│   ├── Thermophysical models (basicThermo, psiThermo)
│   ├── Multiphase models (phaseModel, phaseSystem)
│   └── Transport models (viscosityModel, diffusivityModel)
├── Numerical Methods
│   ├── Time integration (Euler, backward, CrankNicolson)
│   ├── Discretization schemes (fvSchemes)
│   └── Linear solvers (GAMG, PCG, smoothSolver)
└── Boundary Conditions
    ├── Fixed value, gradient, mixed
    ├── Custom derived conditions
    └── Coupled conditions (AMI, cyclic)
```

### กลไกการขยาย

#### 1. **Runtime Selection Tables**
OpenFOAM ใช้ runtime selection tables เพื่อเปิดใช้งานการเลือกโมเดลแบบไดนามิกโดยไม่ต้องคอมไพล์ใหม่:

```cpp
// Runtime selection macro implementation
#define addToRunTimeSelectionTable
(
    baseType,
    derivedType,
    typeName
)

// การใช้งานในนิยามโมเดล
addToRunTimeSelectionTable
(
    turbulenceModel,
    kEpsilon,
    dictionary
);
```

#### 2. **Abstract Base Classes**
กรอบงานจัดหา abstract base classes จำนวนมากซึ่งกำหนดอินเตอร์เฟซสำหรับการขยาย:

```cpp
// Abstract turbulence model interface
class turbulenceModel
{
public:
    // Virtual destructor สำหรับการสืบทอดที่เหมาะสม
    virtual ~turbulenceModel() {}
    
    // Pure virtual functions ที่ต้อง implement
    virtual tmp<volSymmTensorField> devReff() const = 0;
    virtual tmp<fvVectorMatrix> divDevReff(volVectorField& U) const = 0;
    
    // Runtime type information
    virtual const word& type() const = 0;
};
```

#### 3. **Pointer Management System**
ระบบ pointer แบบ reference-counted ของ OpenFOAM เปิดใช้งานการจัดการหน่วยความจำอย่างปลอดภัยและการแชร์ออบเจกต์:

```cpp
// AutoPtr สำหรับความเป็นเจ้าของที่ไม่ซ้ำกัน
autoPtr<turbulenceModel> turbulence
(
    turbulenceModel::New
    (
        U, phi, transport, 
        turbulenceProperties
    )
);

// Tmp สำหรับออบเจกต์ชั่วคราว
tmp<surfaceScalarField> phiU = fvc::flux(U);
```

## ความสามารถในการขยาย Field และ Discretization

### ประเภท Field แบบกำหนดเอง
ผู้ใช้สามารถสร้างประเภท field ที่เฉพาะเจาะจงได้โดยการขยายคลาสที่มีอยู่:

```cpp
// ตัวอย่าง: Custom concentration field พร้อม reaction terms
class concentrationField : public volScalarField
{
private:
    // Reaction rate coefficients
    dimensionedScalar kReaction_;
    
public:
    // Constructor
    concentrationField
    (
        const IOobject& io,
        const fvMesh& mesh,
        const dimensionedScalar& kReaction
    );
    
    // Custom reaction source term
    tmp<fvScalarField> reactionSource();
};
```

### ส่วนขยาย Discretization Scheme
OpenFOAM อนุญาตให้ implement numerical schemes แบบกำหนดเอง:

```cpp
// Custom limited linear differencing scheme
class limitedLinearV : public surfaceInterpolationScheme<scalar>
{
private:
    // Limiter function
    tmp<surfaceScalarField> limiter
    (
        const GeometricField<scalar, fvPatchField, volMesh>& phi
    ) const;
    
public:
    // Interpolation function
    tmp<surfaceScalarField> interpolate
    (
        const GeometricField<scalar, fvPatchField, volMesh>&
    ) const;
};
```

## ความสามารถในการขยาย Physics Model

### ส่วนขยาย Multiphase Model
กรอบงาน multiphase แสดงให้เห็นถึงความสามารถในการขยายของ OpenFOAM ผ่านการสร้างองค์ประกอบ:

```cpp
// Custom interfacial momentum transfer model
class customLiftForce : public liftForceModel
{
public:
    // Constructor พร้อม model dictionary
    customLiftForce
    (
        const phaseInterface& interface,
        const dictionary& dict
    );
    
    // Lift force calculation
    virtual tmp<volVectorField> Fi() const;
    
    // Runtime type information
    TypeName("customLiftForce");
};
```

### โมเดลคุณสมบัติ Thermophysical
ผู้ใช้สามารถ implement property models แบบกำหนดเอง:

```cpp
// Custom equation of state
class customEOS : public equationOfState
{
private:
    dimensionedScalar a_;  // Attraction parameter
    dimensionedScalar b_;  // Co-volume parameter
    
public:
    // Pressure calculation
    virtual tmp<volScalarField> p
    (
        const volScalarField& rho,
        const volScalarField& T
    ) const;
    
    // Compressibility
    virtual tmp<volScalarField> psi
    (
        const volScalarField& rho,
        const volScalarField& T
    ) const;
};
```

## ความสามารถในการขยาย Utility และ Post-Processing

### กรอบงาน Utility แบบกำหนดเอง
Utilities ของ OpenFOAM ปฏิบัติตามรูปแบบมาตรฐานที่สามารถขยายได้:

```cpp
// Template สำหรับ utilities แบบกำหนดเอง
class customUtility
{
    const Time& runTime_;
    const fvMesh& mesh_;
    
public:
    // Constructor
    customUtility(const Time& runTime, const fvMesh& mesh);
    
    // Main execution method
    void execute();
    
    // Helper methods
    void readOptions();
    void processFields();
    void writeResults();
};

// Main function
int main(int argc, char *argv[])
{
    // Standard OpenFOAM initialization
    #include "setRootCase.H"
    #include "createTime.H"
    #include "createMesh.H"
    
    // Create and run utility
    customUtility utility(runTime, mesh);
    utility.execute();
    
    return 0;
}
```

### ความสามารถในการขยาย Function Object
Function objects ให้ความสามารถในการวิเคราะห์แบบ runtime-extensible:

```cpp
// Custom function object สำหรับ flow analysis
class flowAnalysis : public fvMeshFunctionObject
{
private:
    // Stored fields
    const volVectorField& U_;
    
    // Analysis parameters
    dimensionedScalar threshold_;
    
public:
    // Constructor
    flowAnalysis
    (
        const word& name,
        const Time& runTime,
        const dictionary& dict
    );
    
    // Execute method ที่ถูกเรียกในแต่ละ time step
    virtual void execute();
    
    // Write method สำหรับ output
    virtual void write();
    
    // Runtime type information
    TypeName("flowAnalysis");
};
```

## ความสามารถในการขยาย Build System

ระบบ build `wmake` ของ OpenFOAM รองรับส่วนขยายเฉพาะโปรเจกต์:

### โครงสร้างโปรเจกต์แบบกำหนดเอง
```
MyOpenFOAMProject/
├── Make/
│   ├── files          # รายการ source file
│   └── options        # Compilation flags
├── src/
│   ├── libraries/     # Custom libraries
│   └── utilities/     # Custom utilities
└── applications/
    ├── solvers/       # Custom solvers
    └── tutorials/     # Example cases
```

### การกำหนดค่า Make Files
```makefile
# ตัวอย่าง Make/options สำหรับโปรเจกต์แบบกำหนดเอง
EXE_INC = \
    -I$(LIB_SRC)/finiteVolume/lnInclude \
    -I$(LIB_SRC)/meshTools/lnInclude \
    -I$(LIB_SRC)/thermophysicalModels/basic/lnInclude \
    -I./lnInclude

EXE_LIBS = \
    -lfiniteVolume \
    -lmeshTools \
    -lbasicThermophysicalModels \
    -lmyCustomLib
```

## รูปแบบการขยายขั้นสูง

### Template Specialization
ผู้ใช้สามารถ specialize templates สำหรับฟิสิกส์เฉพาะทาง:

```cpp
// Specialization สำหรับ multiphase turbulence
template<>
class kEpsilon<multiphaseSystem> : public RASModel<multiphaseSystem>
{
private:
    // Phase-specific turbulence properties
    PtrList<volScalarField> k_;
    PtrList<volScalarField> epsilon_;
    
public:
    // Multiphase-aware turbulence calculation
    virtual void correct();
};
```

### Mixin Classes สำหรับ Cross-Cutting Concerns
```cpp
// Debug mixin สำหรับ logging แบบละเอียด
template<class BaseType>
class DebugMixin : public BaseType
{
protected:
    void debugLog(const word& message) const;
    void debugWriteField(const word& name, const GeometricField<...>& field) const;
};

// การใช้งาน
class debuggableSolver : public DebugMixin<solver>
{
public:
    virtual void solve() {
        debugLog("Starting solve step");
        BaseType::solve();
        debugLog("Solve step completed");
    }
};
```

## พิจารณาประสิทธิภาพในส่วนขยาย

เมื่อขยาย OpenFOAM พิจารณาประสิทธิภาพรวมถึง:

### การเพิ่มประสิทธิภาพหน่วยความจำ
```cpp
// การเข้าถึง field อย่างมีประสิทธิภาพพร้อม caching
class optimizedSolver
{
private:
    // Cached references เพื่อหลีกเลี่ยงการค้นหาซ้ำ
    const volScalarField& rho_;
    const surfaceScalarField& phi_;
    
    // Precomputed coefficients
    tmp<fvScalarMatrix> aMatrix_;
    
public:
    void solve() {
        // ใช้ cached references เพื่อประสิทธิภาพ
        fvScalarMatrix UEqn = fvm::ddt(rho_, U_) + ...;
    }
};
```

### การรองรับ Parallel Execution
ส่วนขยายต้องรักษาความเข้ากันได้แบบขนาน:

```cpp
// Parallel-aware custom operation
void parallelOperation()
{
    // Reduce operation ข้าม processors ทั้งหมด
    scalar globalSum = gSum(localField);
    
    // Synchronization point
    reduce(globalSum, sumOp<scalar>());
    
    // Parallel field writing
    if (Pstream::master()) {
        field.write();
    }
};
```

สถาปัตยกรรมความสามารถในการขยายนี้ทำให้ OpenFOAM เป็นแพลตฟอร์มที่ทรงพลังสำหรับการวิจัยและการประยุกต์ใช้พลศาสตร์ของไหลเชิงคำนวณ ทำให้ผู้ใช้สามารถขยายกรอบงานจาก boundary conditions ง่ายๆ ไปจนถึงการ implement solvers ทั้งหมดในขณะที่ยังคงคุณภาพโค้ด ประสิทธิภาพ และประสิทธิภาพแบบขนาน
