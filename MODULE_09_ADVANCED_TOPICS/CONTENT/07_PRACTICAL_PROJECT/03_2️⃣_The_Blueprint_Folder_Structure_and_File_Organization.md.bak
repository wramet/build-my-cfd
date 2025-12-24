## 2️⃣ แบบแปลน:โครงสร้างโฟลเดอร์และการจัดระเบียบไฟล์

### 📁 **โครงสร้างโปรเจกต์**

การจัดระเบียบโมเดลความหนืดแบบกำหนดเองใน OpenFOAM จะทำตามโครงสร้างที่กำหนดอย่างชัดเจนเพื่อให้แน่ใจว่าการคอมไพล์ การผสานรวมกับกลไกการเลือกขณะทำงาน และการบำรุงรักษาสามารถดำเนินการได้อย่างถูกต้อง โครงสร้างแบบลำดับชั้นจะแยกคำจำกัดความอินเทอร์เฟซจากการ implement ทำตามการตั้งชื่อมาตรฐานของ OpenFOAM และให้เส้นทางเอกสารที่ชัดเจน

```
customViscosityModel/
├── Make/
│   ├── files          # รายการไฟล์ต้นทางและเป้าหมายไลบรารี
│   └── options        # คอมไพล์ flags และ dependencies
├── powerLawViscosity/
│   ├── powerLawViscosity.H    # ไฟล์ส่วนหัวพรับคำประกาศคลาส
│   └── powerLawViscosity.C    # ไฟล์ implementation
└── README.md          # เอกสารและคำแนะนำการใช้งาน
```

โครงสร้างนี้ใช้ประโยชน์จากระบบสร้าง `wmake` ของ OpenFOAM โดยที่โฟลเดอร์ `Make/` จะมีไฟล์คอนฟิกกูเรชันการสร้างที่ระบุ dependencies ของการคอมไพล์ เส้นทาง include และเป้าหมาย output การ implement คลาสจะทำตามรูปแบบ header-implementation ทั่วไปของโปรเจกต์ C++ โดยไฟล์ส่วนหัวจะกำหนดอินเทอร์เฟซและไฟล์ต้นทางจะให้การ implement ที่เป็นรูปธรรม

### 📄 **คำอธิบายไฟล์**

#### **Make/files** - คอนฟิกกูเรชันระบบสร้าง

ไฟล์ `Make/files` ทำหน้าที่เป็น build descriptor หลักสำหรับระบบ `wmake` โดยจะระบุไฟล์ต้นทางที่จะคอมไพล์และตำแหน่งเป้าหมายของไลบรารี:

```
powerLawViscosity/powerLawViscosity.C

LIB = $(FOAM_USER_LIBBIN)/libcustomViscosityModels
```

การคอนฟิกกูเรชันนี้จะบอกระบบสร้างว่า:
1. คอมไพล์ไฟล์ต้นทางที่อยู่ `powerLawViscosity/powerLawViscosity.C`
2. ลิงก์เข้ากับไลบรารีแบบ shared ที่ชื่อ `libcustomViscosityModels`
3. ติดตั้งไลบรารีในไดเรกทอรีไลบรารีของผู้ใช้ที่ระบุโดย `$(FOAM_USER_LIBBIN)`

การตั้งชื่อไลบรารี (คำนำหน้า `lib` และส่วนขยายไลบรารีแบบ shared) จะทำตามสถาปัตยกรรมปลั๊กอินมาตรฐานของ OpenFOAM ซึ่งช่วยให้โมเดลความหนืดแบบกำหนดเองสามารถโหลดได้แบบไดนามิกขณะทำงานผ่านกลไกการเลือกขณะทำงาน

#### **Make/options** - Dependencies และ Includes

ไฟล์ `Make/options` จะกำหนดคอมไพล์ flags, include paths, และ library dependencies ที่จำเป็นสำหรับการสร้างโมเดลความหนืดแบบกำหนดเอง:

```
EXE_INC = \
    -I$(LIB_SRC)/finiteVolume/lnInclude \
    -I$(LIB_SRC)/transportModels/lnInclude \
    -I$(LIB_SRC)/thermophysicalModels/lnInclude

EXE_LIBS = \
    -lfiniteVolume \
    -ltransportModels \
    -lthermophysicalModels
```

ตัวแปร `EXE_INC` ระบุไดเรกทอรี include เพิ่มเติม:
- `-I$(LIB_SRC)/finiteVolume/lnInclude`: เข้าถึงคลาสและฟังก์ชัน finite volume method
- `-I$(LIB_SRC)/transportModels/lnInclude`: อินเทอร์เฟซ transport model พื้นฐาน
- `-I$(LIB_SRC)/thermophysicalModels/lnInclude`: การสนับสนุน thermophysical property model

ตัวแปร `EXE_LIBS` ระบุไลบรารีที่จะลิงก์ด้วย:
- `-lfiniteVolume`: ฟังก์ชันหลัก finite volume (fvc operations, mesh classes)
- `-ltransportModels`: อินเทอร์เฟซ viscosity model พื้นฐาน (viscosityModel class)
- `-lthermophysicalModels`: การคำนวณและความสัมพันธ์ของ thermophysical properties

dependencies เหล่านี้ช่วยให้มั่นใจว่าโมเดลความหนืดแบบกำหนดเองสามารถเข้าถึงโครงสร้างพื้นฐาน CFD ของ OpenFOAM ได้ในขณะที่ยังคงการแยกส่วนที่ชัดเจนผ่านสถาปัตยกรรมไลบรารีแบบโมดูลาร์

#### **powerLawViscosity.H** - คำประกาศคลาส

ไฟล์ส่วนหัวจะกำหนดอินเทอร์เฟซที่สมบูรณ์สำหรับโมเดลความหนืดแบบ power-law โดยทำตามลำดับชั้นของคลาสและรูปแบบการออกแบบของ OpenFOAM:

```cpp
#ifndef powerLawViscosity_H
#define powerLawViscosity_H

#include "viscosityModel.H"
#include "dimensionedScalar.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{
namespace viscosityModels
{

/*---------------------------------------------------------------------------*\
                       คำประกาศคลาส powerLawViscosity
\*---------------------------------------------------------------------------*/

class powerLawViscosity
:
    public viscosityModel
{
    // Private Data

        //- สัมประสิทธิ์ power-law
        dimensionedScalar K_;
        dimensionedScalar n_;
        dimensionedScalar nuMin_;
        dimensionedScalar nuMax_;

        //- ฟิลด์อัตราการเฉือน
        volScalarField shearRate_;


    // Private Member Functions

        //- คำนวณขนาดของอัตราการเฉือน
        tmp<volScalarField> calcShearRate() const;

        //- คำนวณความหนืดจากอัตราการเฉือน
        tmp<volScalarField> calcNu() const;


public:

    //- ข้อมูลประเภทขณะทำงาน
    TypeName("powerLaw");


    // Constructors

        //- สร้างจาก components
        powerLawViscosity
        (
            const fvMesh& mesh,
            const word& group = word::null
        );


    //- Destructor
    virtual ~powerLawViscosity() = default;


    // Member Functions

        //- อ่านพจนานุกรม viscosityProperties
        virtual bool read();

        //- ส่งคืนความหนืดแบบลามินาร์
        virtual tmp<volScalarField> nu() const;

        //- ส่งคืนความหนืดแบบลามินาร์สำหรับ patch
        virtual tmp<scalarField> nu(const label patchi) const;

        //- แก้ไขความหนืด (คำนวณอัตราการเฉือนใหม่)
        virtual void correct();


    // Member Operators

        //- ห้ามการกำหนดค่า bitwise แบบ default
        void operator=(const powerLawViscosity&) = delete;
};


// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

} // End namespace viscosityModels
} // End namespace Foam

#endif
```

**องค์ประกอบการออกแบบหลัก:**

1. **ลำดับชั้นการสืบทอด**: คลาสสืบทอดจาก `viscosityModel` ซึ่งสร้างอินเทอร์เฟซ polymorphic ที่ใช้โดยกรอบงาน transport model ของ OpenFOAM

2. **ระบบประเภทขณะทำงาน**: แมโค `TypeName("powerLaw")` จะลงทะเบียนคลาสกับกลไกการเลือกขณะทำงานของ OpenFOAM ซึ่งช่วยให้สร้างผ่านรายการพจนานุกรมได้

3. **การวิเคราะห์มิติ**: สมาชิก `dimensionedScalar` ช่วยให้แน่ใจว่ามีความสอดคล้องทางมิติผ่านระบบหน่วยของ OpenFOAM:
   - `K_`: ดัชนีความสม่ำเสมอ [kg·m⁻¹·sⁿ⁻²]
   - `n_`: ดัชนี power-law [ไร้มิติ]
   - `nuMin_`, `nuMax_`: ขีดจำกัดความหนืด [m²·s⁻¹]

4. **การจัดการฟิลด์**: `volScalarField shearRate_` เก็บอัตราการเฉือนที่คำนวณไว้เพื่อการ visualisation และการ debug

5. **การปฏิบัติตามอินเทอร์เฟซ**: ฟังก์ชันเสมือน (`nu()`, `nu(patchi)`, `correct()`, `read()`) จะ implement อินเทอร์เฟซ `viscosityModel` พื้นฐาน

6. **การจัดการหน่วยความจำ**: ใช้ `tmp` smart pointers สำหรับการจัดการฟิลด์ที่มีประสิทธิภาพและการจัดการหน่วยความจำอัตโนมัติ

#### **powerLawViscosity.C** - Implementation

ไฟล์ implementation จะให้การ implement ที่เป็นรูปธรรมของโมเดลความหนืดแบบ power-law รวมถึงการคำนวณทางคณิตศาสตร์และการผสานรวมกับระบบจัดการฟิลด์ของ OpenFOAM:

```cpp
#include "powerLawViscosity.H"
#include "fvMesh.H"
#include "fvc.H"
#include "addToRunTimeSelectionTable.H"
#include "volFields.H"
#include "surfaceFields.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{
namespace viscosityModels
{

// * * * * * * * * * * * * * * * * ข้อมูลสถิติ * * * * * * * * * * * * * * * //

defineTypeNameAndDebug(powerLawViscosity, 0);

addToRunTimeSelectionTable
(
    viscosityModel,
    powerLawViscosity,
    dictionary
);


// * * * * * * * * * * * * * * * * Constructors * * * * * * * * * * * * * * //

powerLawViscosity::powerLawViscosity
(
    const fvMesh& mesh,
    const word& group
)
:
    viscosityModel(mesh, group),
    K_("K", dimViscosity, 1.0),
    n_("n", dimless, 1.0),
    nuMin_("nuMin", dimViscosity, 0.0),
    nuMax_("nuMax", dimViscosity, GREAT),
    shearRate_
    (
        IOobject
        (
            "shearRate",
            mesh.time().timeName(),
            mesh,
            IOobject::NO_READ,
            IOobject::AUTO_WRITE
        ),
        mesh,
        dimensionedScalar("shearRate", dimless/dimTime, 0.0)
    )
{
    read();
    correct();
}


// * * * * * * * * * * * * * * * * Member Functions * * * * * * * * * * * * * * //

bool powerLawViscosity::read()
{
    if (!viscosityModel::read())
    {
        return false;
    }

    const dictionary& coeffsDict = this->dict_.subDict("powerLawCoeffs");

    coeffsDict.lookup("K") >> K_;
    coeffsDict.lookup("n") >> n_;
    coeffsDict.lookup("nuMin") >> nuMin_;
    coeffsDict.lookup("nuMax") >> nuMax_;

    return true;
}


tmp<volScalarField> powerLawViscosity::calcShearRate() const
{
    // คำนวณขนาดอัตราการเฉือนจากความชันของความเร็ว
    // สำหรับการไหลแบบ incompressible: sqrt(2 * symm(gradU) && symm(gradU))
    const volVectorField& U = mesh_.lookupObject<volVectorField>("U");

    tmp<volTensorField> tgradU = fvc::grad(U);
    const volTensorField& gradU = tgradU();

    // เทนเซอร์อัตราการยืดตัว: symm(gradU) = 0.5*(gradU + gradU.T())
    tmp<volSymmTensorField> tS = symm(gradU);
    const volSymmTensorField& S = tS();

    // ขนาดอัตราการเฉือน: sqrt(2 * S && S)
    return sqrt(2.0) * mag(S);
}


tmp<volScalarField> powerLawViscosity::calcNu() const
{
    // โมเดล power-law: ν = K * (shearRate)^(n-1)
    // พร้อมค่าจำกัด nuMin และ nuMax

    tmp<volScalarField> tshearRate = calcShearRate();
    const volScalarField& shearRate = tshearRate();

    tmp<volScalarField> tnu
    (
        new volScalarField
        (
            IOobject
            (
                "nu",
                mesh_.time().timeName(),
                mesh_,
                IOobject::NO_READ,
                IOobject::AUTO_WRITE
            ),
            K_ * pow(max(shearRate, dimensionedScalar("small", dimless/dimTime, SMALL)), n_ - 1.0)
        )
    );

    volScalarField& nu = tnu.ref();

    // ใช้ขีดจำกัด
    nu = max(nu, nuMin_);
    nu = min(nu, nuMax_);

    return tnu;
}


tmp<volScalarField> powerLawViscosity::nu() const
{
    return calcNu();
}


tmp<scalarField> powerLawViscosity::nu(const label patchi) const
{
    // คำนวณความหนืดสำหรับ patch ที่ระบุ
    // (แบบย่อ: ส่งคืนค่าฟิลด์ภายในที่ faces ของ patch)
    return nu().boundaryField()[patchi].patchInternalField();
}


void powerLawViscosity::correct()
{
    // อัปเดตฟิลด์อัตราการเฉือน
    shearRate_ = calcShearRate();

    // เขียนฟิลด์อัตราการเฉือนสำหรับ visualisation
    shearRate_.write();
}

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

} // End namespace viscosityModels
} // End namespace Foam

// ************************************************************************* //
```

**รายละเอียดการ implement:**

1. **การลงทะเบียนขณะทำงาน**: 
   ```cpp
   addToRunTimeSelectionTable
   (
       viscosityModel,
       powerLawViscosity,
       dictionary
   );
   ```
   แมโคนี้จะลงทะเบียนคลาสกับระบบ factory ซึ่งช่วยให้สร้างจากรายการพจนานุกรมเช่น:
   ```
   transportModel  Newtonian;
   viscosity       powerLaw;
   powerLawCoeffs
   {
       K       0.01;
       n       0.7;
       nuMin   1e-6;
       nuMax   1e6;
   }
   ```

2. **การ implement ทางคณิตศาสตร์**:
   - **การคำนวณอัตราการเฉือน**: 
     $$\dot{\gamma} = \sqrt{2 \cdot \mathbf{S} : \mathbf{S}}$$
     โดยที่ $\mathbf{S} = \frac{1}{2}(\nabla\mathbf{u} + \nabla\mathbf{u}^T)$ เป็นเทนเซอร์อัตราการยืดตัว
   
   - **ความหนืดแบบ Power-Law**:
     $$\nu = K \cdot \dot{\gamma}^{n-1}$$
     โดยที่ $\nu_{\text{min}} \leq \nu \leq \nu_{\text{max}}$

3. **การจัดการฟิลด์**: 
   - ใช้ `tmp` smart pointers สำหรับการจัดการหน่วยความจำที่มีประสิทธิภาพ
   - การลงทะเบียนฟิลด์อัตโนมัติกับฐานข้อมูล mesh
   - การจัดการ I/O ที่เหมาะสมสำหรับ visualisation และความสามารถในการเริ่มต้นใหม่

4. **เสถียรภาพเชิงตัวเลข**: 
   - `max(shearRate, SMALL)` ป้องกันการหารด้วยศูนย์
   - ขีดจำกัดความหนืดป้องกันความไม่เสถียรเชิงตัวเลข
   - การบังคับใช้ความสอดคล้องทางมิติตลอดเวลา

5. **จุดการผสานรวม**:
   - Constructor เรียก `read()` และ `correct()` สำหรับการเริ่มต้น
   - เมธอด `correct()` ถูกเรียกทุก time step เพื่ออัปเดตความหนืด
   - การเข้าถึงฟิลด์ขอบเขตมีให้สำหรับการ coupling กับโมเดลอื่น

การ implement นี้สาธิตหลักการของ OpenFOAM: polymorphism เชิงวัตถุ, การผสานรวมการวิเคราะห์มิติ, การจัดการฟิลด์ที่มีประสิทธิภาพ และการผสานรวมที่ราบรื่นกับกรอบงาน solver CFD
