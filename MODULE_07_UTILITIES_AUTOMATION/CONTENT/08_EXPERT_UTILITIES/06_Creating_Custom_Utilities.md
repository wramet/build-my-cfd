# การสร้าง Custom Utilities (Creating Custom Utilities)

การพัฒนา **Custom Utilities** ใน OpenFOAM เป็นกระบวนการขยายขีดความสามารถของซอฟต์แวร์ CFD เพื่อตอบโจทย์งานวิจัยและวิศวกรรมเฉพาะทางที่ไม่สามารถทำได้ด้วยเครื่องมือมาตรฐาน บทนี้จะกล่าวถึงหลักการพัฒนา โครงสร้างโค้ด และตัวอย่างการประยุกต์ใช้งานจริง

---

## 1. รากฐานทางทฤษฎี (Theoretical Foundation)

### 1.1 สถาปัตยกรรมของ OpenFOAM Utilities

ยูทิลิตี้ใน OpenFOAM ทำงานบนสถาปัตยกรรม **Time-Database** ซึ่งเป็นระบบจัดการข้อมูลที่ขึ้นกับเวลา (Temporal Data Management) โดยมีสมการพื้นฐานในการเข้าถึงข้อมูล:

$$
\mathcal{D}(t) = \left\{ \mathbf{\Phi}(\mathbf{x}, t), \quad \forall \mathbf{x} \in \Omega \right\}
$$

เมื่อ:
- $\mathcal{D}(t)$ = ชุดข้อมูลทั้งหมดในเวลา $t$
- $\mathbf{\Phi}$ = เวกเตอร์ของสนามต่าง ๆ (เช่น $p$, $U$, $T$)
- $\mathbf{x}$ = ตำแหน่งในโดเมน $\Omega$

### 1.2 การประมวลผลแบบขนาน (Parallel Processing)

ในการรันแบบขนานด้วย MPI (Message Passing Interface) การคำนวณค่าทางสถิติต้องใช้ฟังก์ชันการรวมค่า (Reduction Operation):

$$
\Phi_{\text{global}} = \bigoplus_{i=1}^{N_{proc}} \Phi_{i}
$$

เมื่อ $\bigoplus$ แทน operation ประเภท `maxOp`, `sumOp`, `avgOp` เป็นต้น

> [!INFO] ความสำคัญของการทำ Parallel Reduction
> หากไม่ใช้ `reduce()` ค่าที่ได้จะเป็นค่า **Local** เท่านั้น ซึ่งจะไม่ถูกต้องในกรณีรันแบบขนาน

---

## 2. โครงสร้างพื้นฐานของ Utility (Basic Template)

ยูทิลิตี้ทุกตัวต้องทำตามโครงสร้างมาตรฐาน (**Canonical Template**) เพื่อให้สามารถทำงานร่วมกับระบบ Time database และ Mesh ของ OpenFOAM ได้อย่างสมบูรณ์

### 2.1 โครงสร้างไฟล์และไดเรกทอรี

```
myCustomUtility/
├── myCustomUtility.C          # ไฟล์โค้ดหลัก
└── Make/
    ├── files                  # ระบุไฟล์ต้นฉบับและตำแหน่ง output
    └── options                # ระบุ header และ library ที่ต้องใช้
```

### 2.2 Template Code แบบสมบูรณ์

```cpp
// NOTE: Synthesized by AI - Verify parameters
#include "fvCFD.H"
#include "IOobject.H"
#include "volFields.H"
#include "timeSelector.H"

using namespace Foam;

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

int main(int argc, char *argv[])
{
    // ========================================================================
    // PHASE 1: Initialization
    // ========================================================================

    // 1.1 ตรวจสอบและตั้งค่า root case directory
    #include "setRootCase.H"

    // 1.2 สร้างออบเจกต์เวลา (Time object)
    #include "createTime.H"

    // 1.3 สร้างออบเจกต์เมช (Mesh object)
    #include "createMesh.H"

    Info<< "\n==========================================\n"
        << "Starting Custom Utility Execution\n"
        << "Case: " << rootCase() << "\n"
        << "Mesh: " << mesh.nCells() << " cells\n"
        << "==========================================\n" << endl;

    // ========================================================================
    // PHASE 2: Time Loop Processing
    // ========================================================================

    // 2.1 กรองเวลาที่ต้องการประมวลผล
    instantList timeDirs = timeSelector::select
    (
        runTime.times(),
        args
    );

    // 2.2 ลูปหลักสำหรับแต่ละช่วงเวลา
    forAll(timeDirs, timeI)
    {
        runTime.setTime(timeDirs[timeI], timeI);

        Info<< "\n--- Processing Time: " << runTime.timeName()
            << " ---" << endl;

        // ====================================================================
        // PHASE 3: Field Loading & Processing
        // ====================================================================

        // 3.1 ตรวจสอบการมีอยู่ของฟิลด์ (Field Existence Check)
        if (!exists(runTime.timePath()/volVectorField::typeName/"U"))
        {
            WarningIn(args.executable())
                << "Velocity field U not found at time "
                << runTime.timeName() << nl
                << "Skipping this time directory..." << endl;
            continue;
        }

        // 3.2 โหลดฟิลด์ความเร็ว (Load Velocity Field)
        volVectorField U
        (
            IOobject
            (
                "U",
                runTime.timeName(),
                mesh,
                IOobject::MUST_READ,
                IOobject::AUTO_WRITE
            ),
            mesh
        );

        // 3.3 โหลดฟิลด์ความดัน (Load Pressure Field)
        volScalarField p
        (
            IOobject
            (
                "p",
                runTime.timeName(),
                mesh,
                IOobject::MUST_READ,
                IOobject::NO_WRITE
            ),
            mesh
        );

        // ====================================================================
        // PHASE 4: Mathematical Operations
        // ====================================================================

        // 4.1 คำนวณค่ามหัศจรรย์ของความเร็ว
        volScalarField magU = mag(U);

        // 4.2 คำนวณค่าสถิติ (Statistical Quantities)
        scalar maxU = max(magU).value();
        scalar minU = min(magU).value();
        scalar avgU = average(magU).value();

        // 4.3 Parallel Reduction (สำคัญมากสำหรับการรันแบบขนาน)
        reduce(maxU, maxOp<scalar>());
        reduce(minU, minOp<scalar>());
        reduce(avgU, sumOp<scalar>());
        avgU /= Pstream::nProcs();

        // 4.4 แสดงผลลัพธ์
        Info<< "Velocity Statistics:" << nl
            << "  Maximum: " << maxU << " m/s" << nl
            << "  Minimum: " << minU << " m/s" << nl
            << "  Average: " << avgU << " m/s" << endl;

        // ====================================================================
        // PHASE 5: Derived Field Computation
        // ====================================================================

        // 5.1 คำนวณ Vorticity (การหมุนของไหล)
        volVectorField vorticity
        (
            IOobject
            (
                "vorticity",
                runTime.timeName(),
                mesh,
                IOobject::NO_READ,
                IOobject::AUTO_WRITE
            ),
            fvc::curl(U)
        );

        // 5.2 คำนวณ Q-Criterion (สำหรับการระบุโครงสร้างพลวัต)
        volScalarField QCriterion
        (
            IOobject
            (
                "Q",
                runTime.timeName(),
                mesh,
                IOobject::NO_READ,
                IOobject::AUTO_WRITE
            ),
            0.5 * (sqr(tr(fvc::grad(U))) - tr(sqr(fvc::grad(U))))
        );

        // 5.3 เขียนฟิลด์ใหม่ลงไฟล์
        vorticity.write();
        QCriterion.write();
    }

    // ========================================================================
    // PHASE 6: Finalization
    // ========================================================================

    Info<< "\n==========================================\n"
        << "Execution Completed Successfully!\n"
        << "Total processed times: " << timeDirs.size() << "\n"
        << "==========================================\n" << endl;

    return 0;
}

// ************************************************************************* //
```

---

## 3. การคอมไพล์ด้วย wmake (Compilation Process)

ในการสร้าง Custom Utility คุณต้องเตรียมไฟล์คอนฟิกูเรชันในโฟลเดอร์ `Make/` ตามโครงสร้างที่กำหนด

### 3.1 ไฟล์ `Make/files`

ระบุชื่อไฟล์ต้นฉบับ (`.C`) และตำแหน่งไฟล์ไบนารีที่จะถูกสร้าง:

```make
# NOTE: Synthesized by AI - Verify parameters
# ระบุไฟล์ต้นฉบับทั้งหมด
myCustomUtility.C

# ระบุตำแหน่งที่จะติดตั้ง executable
EXE = $(FOAM_USER_APPBIN)/myCustomUtility

# ถ้าต้องการให้ utility อยู่ใน directory ปัจจุบัน:
# EXE = $(FOAM_RUN)/myCustomUtility
```

> [!TIP] ตำแหน่งการติดตั้ง
> - `$FOAM_USER_APPBIN`: สำหรับ utilities ส่วนบุคคล (ติดตั้งใน `~/OpenFOAM/.../platforms/linux64GccDPInt32Opt/bin`)
> - `$FOAM_APPBIN`: สำหรับ utilities ระดับระบบ (ต้องมีสิทธิ์ admin)

### 3.2 ไฟล์ `Make/options`

ระบุตำแหน่ง Header และไลบรารีที่จำเป็น:

```make
# NOTE: Synthesized by AI - Verify parameters
# Include paths
EXE_INC = \
    -I$(LIB_SRC)/finiteVolume/lnInclude \
    -I$(LIB_SRC)/meshTools/lnInclude \
    -I$(LIB_SRC)/sampling/lnInclude \
    -I$(LIB_SRC)/transportModels \
    -I$(LIB_SRC)/turbulenceModels

# Library paths
EXE_LIBS = \
    -lfiniteVolume \
    -lmeshTools \
    -lsampling \
    -lincompressibleTransportModels \
    -lincompressibleTurbulenceModels
```

### 3.3 ขั้นตอนการคอมไพล์

```bash
# NOTE: Synthesized by AI - Verify parameters
# เข้าไปใน directory ของ utility
cd $WM_PROJECT_USER_DIR/applications/utilities/myCustomUtility

# รันคำสั่ง wmake
wmake

# ผลลัพธ์ที่คาดหวัง:
# wmake LnInclude src
# wmake MkInclude src
# wmake Ctoo myCustomUtility.C
# wmake ld
# /home/user/OpenFOAM/user-v2206/platforms/linux64GccDPInt32Opt/bin/myCustomUtility
```

> [!WARNING] ข้อผิดพลาดที่พบบ่อย
> หากเจอ error: `fvCFD.H: No such file or directory` ให้ตรวจสอบว่าได้ source สภาพแวดล้อม OpenFOAM แล้ว:
> ```bash
> source /opt/openfoam/etc/bashrc
> ```

---

## 4. ตัวอย่างการใช้งานจริง (Practical Examples)

### 4.1 Example 1: Field Statistics Utility

เครื่องมือสำหรับวิเคราะห์สถิติของฟิลด์ความเร็วและความดัน:

```cpp
// NOTE: Synthesized by AI - Verify parameters
// ภายในลูปเวลา

// 1. โหลดฟิลด์
volVectorField U(IOobject("U", runTime.timeName(), mesh, IOobject::MUST_READ), mesh);
volScalarField p(IOobject("p", runTime.timeName(), mesh, IOobject::MUST_READ), mesh);

// 2. คำนวณค่าสถิติพื้นฐาน
scalar maxU = max(mag(U)).value();
scalar minU = min(mag(U)).value();
scalar meanU = average(mag(U)).value();
scalar maxP = max(p).value();
scalar minP = min(p).value();

// 3. Parallel reduction
reduce(maxU, maxOp<scalar>());
reduce(minU, minOp<scalar>());
reduce(meanU, sumOp<scalar>());
reduce(maxP, maxOp<scalar>());
reduce(minP, minOp<scalar>());

meanU /= Pstream::nProcs();

// 4. แสดงผล
Info<< "Field Statistics at t = " << runTime.timeName() << ":" << nl
    << "  Velocity [m/s]:" << nl
    << "    Max: " << maxU << nl
    << "    Min: " << minU << nl
    << "    Mean: " << meanU << nl
    << "  Pressure [Pa]:" << nl
    << "    Max: " << maxP << nl
    << "    Min: " << minP << endl;
```

### 4.2 Example 2: Gradient & Divergence Computation

คำนวณปริมาณทางเวกเตอร์และเทนเซอร์ที่สำคัญในการวิเคราะห์การไหล:

```cpp
// NOTE: Synthesized by AI - Verify parameters
// คำนวณ Gradient ของความเร็ว
volTensorField gradU = fvc::grad(U);

// คำนวณ Symmetric Gradient (Rate-of-Strain Tensor)
volSymmTensorField D = symm(gradU);

// คำนวณ Skew-Symmetric Gradient (Vorticity Tensor)
volTensorField W = skew(gradU);

// คำนวณ Divergence ของความเร็ว (สำหรับตรวจสอบ Incompressibility)
volScalarField divU = fvc::div(U);

// คำนวณค่า Magnitude ของ Shear Rate
volScalarField magD = mag(D);

// คำนวณค่า Mean Kinetic Energy
volScalarField ke = 0.5 * magSqr(U);

// เขียนฟิลด์ลงไฟล์
gradU.write();
D.write();
divU.write();
ke.write();
```

### 4.3 Example 3: Force Calculation

คำนวณแรงที่กระทำต่อพื้นผิว (สำคัญสำหรับงาน Aerodynamics):

```cpp
// NOTE: Synthesized by AI - Verify parameters
// 1. ระบุ Patch ที่ต้องการคำนวณ
label wallPatchID = mesh.boundaryMesh().findPatchID("walls");

if (wallPatchID != -1)
{
    // 2. เข้าถึงข้อมูลบน Patch
    const fvPatchVectorField& pPatch = p.boundaryField()[wallPatchID];
    const fvPatchVectorField& UPatch = U.boundaryField()[wallPatchID];
    const vectorField& Sf = mesh.Sf().boundaryField()[wallPatchID];

    // 3. คำนวณแรงแต่ละส่วน
    vector pressureForce = vector::zero;
    vector viscousForce = vector::zero;

    // 4. ลูปผ่านทุก Face บน Patch
    forAll(pPatch, faceI)
    {
        // แรงเนื่องจากความดัน
        pressureForce += pPatch[faceI] * Sf[faceI];

        // แรงเนื่องจากความหนืด (Viscous Force)
        // ต้องการ Gradient ของความเร็วบน Patch
        tensorField gradUPatch = U.boundaryField()[wallPatchID].snGrad();
        viscousForce += mu * gradUPatch[faceI] * Sf[faceI].mag();
    }

    // 5. Parallel Reduction
    reduce(pressureForce, sumOp<vector>());
    reduce(viscousForce, sumOp<vector>());

    // 6. แสดงผล
    Info<< "Forces on 'walls' patch:" << nl
        << "  Pressure Force [N]: " << pressureForce << nl
        << "  Viscous Force [N]: " << viscousForce << nl
        << "  Total Force [N]: " << (pressureForce + viscousForce) << endl;
}
```

---

## 5. แผนผังการพัฒนา Utility

```mermaid
flowchart TD
    A[เริ่มต้น] --> B[วิเคราะห์ความต้องการ]
    B --> C[ออกแบบ Algorithm]
    C --> D[เขียนโค้ด C++]
    D --> E[สร้างไฟล์ Make/files]
    E --> F[สร้างไฟล์ Make/options]
    F --> G[รันคำสั่ง wmake]
    G --> H{คอมไพล์ผ่าน?}
    H -->|ไม่ผ่าน| I[แก้ไขข้อผิดพลาด]
    I --> D
    H -->|ผ่าน| J[ทดสอบการทำงาน]
    J --> K{ใช้งานได้?}
    K -->|ไม่| I
    K -->|ใช่| L[ยูทิลิตี้พร้อมใช้งาน]
    L --> M[บันทึกเอกสาร]
    M --> N[จบ]
```

---

## 6. หลักการทางคณิตศาสตร์สำหรับ Utilities

### 6.1 การคำนวณ Gradient

ใน OpenFOAM การคำนวณ Gradient ใช้ **Gauss Theorem**:

$$
\int_{\Omega} \nabla \phi \, dV = \oint_{\partial \Omega} \phi \, \mathbf{n} \, dS
$$

เมื่อ:
- $\phi$ = สนามสเกลาร์
- $\mathbf{n}$ = เวกเตอร์หน่วยตั้งฉากกับพื้นผิว
- $dS$ = องค์ประกอบพื้นที่ผิว

### 6.2 การคำนวณ Divergence

การคำนวณ Divergence ใช้หลักการเดียวกัน:

$$
\int_{\Omega} \nabla \cdot \mathbf{u} \, dV = \oint_{\partial \Omega} \mathbf{u} \cdot \mathbf{n} \, dS
$$

เมื่อ $\mathbf{u}$ = เวกเตอร์ความเร็ว

### 6.3 การคำนวณ Laplacian

Laplacian ใช้แนวคิด **Gauss Divergence Theorem**:

$$
\int_{\Omega} \nabla^2 \phi \, dV = \oint_{\partial \Omega} \nabla \phi \cdot \mathbf{n} \, dS
$$

ใน OpenFOAM ใช้ฟังก์ชัน `fvc::laplacian(phi)`

### 6.4 การคำนวณ Curl (Vorticity)

สำหรับคำนวณ Vorticity $\boldsymbol{\omega} = \nabla \times \mathbf{u}$:

$$
\boldsymbol{\omega} = \nabla \times \mathbf{u} = \begin{bmatrix}
\frac{\partial w}{\partial y} - \frac{\partial v}{\partial z} \\
\frac{\partial u}{\partial z} - \frac{\partial w}{\partial x} \\
\frac{\partial v}{\partial x} - \frac{\partial u}{\partial y}
\end{bmatrix}
$$

ใน OpenFOAM ใช้: `fvc::curl(U)`

---

## 7. การจัดการ Boundary Conditions

เมื่อสร้าง Custom Utilities การเข้าใจและจัดการ Boundary Conditions ถือเป็นสิ่งสำคัญ

### 7.1 การตรวจสอบ Boundary Types

```cpp
// NOTE: Synthesized by AI - Verify parameters
const fvBoundaryMesh& boundaries = mesh.boundary();

forAll(boundaries, patchI)
{
    const fvPatch& patch = boundaries[patchI];

    Info<< "Patch " << patchI << ": " << patch.name()
        << " (Type: " << patch.type() << ")" << nl
        << "  Faces: " << patch.size() << nl
        << "  Start Face: " << patch.start() << endl;
}
```

### 7.2 การเข้าถึงข้อมูลบน Patch

```cpp
// NOTE: Synthesized by AI - Verify parameters
// ระบุ Patch ที่ต้องการ
label patchID = mesh.boundaryMesh().findPatchID("inlet");

if (patchID != -1)
{
    // เข้าถึง Field บน Patch
    const fvPatchVectorField& Upatch = U.boundaryField()[patchID];

    // คำนวณค่าเฉลี่ยบน Patch
    vector avgU = vector::zero;
    forAll(Upatch, faceI)
    {
        avgU += Upatch[faceI];
    }
    avgU /= Upatch.size();

    Info<< "Average velocity at inlet: " << avgU << endl;
}
```

---

## 8. การเขียนข้อมูล Output

### 8.1 การเขียนไฟล์ CSV

```cpp
// NOTE: Synthesized by AI - Verify parameters
// สร้างไฟล์สำหรับเก็บข้อมูล
OFstream outputFile("velocityStatistics.csv");

// เขียน Header
outputFile << "Time,MaxU,MinU,AvgU" << endl;

// เขียนข้อมูลในแต่ละเวลา
outputFile << runTime.value() << ","
           << maxU << ","
           << minU << ","
           << avgU << endl;
```

### 8.2 การเขียนฟิลด์ใหม่

```cpp
// NOTE: Synthesized by AI - Verify parameters
// สร้างฟิลด์ใหม่
volScalarField myDerivedField
(
    IOobject
    (
        "derivedField",
        runTime.timeName(),
        mesh,
        IOobject::NO_READ,      // ไม่ต้องอ่านจากไฟล์
        IOobject::AUTO_WRITE    // เขียนอัตโนมัติ
    ),
    mesh,
    dimensionedScalar("zero", dimless, 0.0)
);

// คำนวณค่า
myDerivedField = mag(U) / mag(U.max());

// เขียนลงไฟล์
myDerivedField.write();
```

---

## 9. การจัดการ Memory (Memory Management)

> [!WARNING] หลีกเลี่ยง Memory Leaks
> ใน OpenFOAM การใช้ `tmp<T>` ช่วยลดภาระการจัดการหน่วยความจำ

```cpp
// NOTE: Synthesized by AI - Verify parameters
// วิธีที่ไม่แนะนำ (สร้างการ Copy)
volScalarField magU1 = mag(U);  // Copy ทั้ง field

// วิธีที่แนะนำ (ใช้ tmp)
tmp<volScalarField> tmagU = mag(U);
const volScalarField& magU2 = tmagU();  // ใช้ reference
// tmagU จะถูกทำลายอัตโนมัติเมื่อออกจาก scope
```

---

## 10. การดีบักและแก้ไขข้อผิดพลาด (Debugging)

### 10.1 การใช้ Info และ Warning

```cpp
// NOTE: Synthesized by AI - Verify parameters
// การแสดงข้อมูล (Info level)
Info<< "Processing field: " << fieldName << endl;

// การแจ้งเตือน (Warning level)
WarningInFunction
    << "Field " << fieldName << " not found. Using default value." << endl;

// การแจ้งข้อผิดพลาดร้ายแรง (Fatal Error)
if (someCondition)
{
    FatalErrorInFunction
        << "Critical error: Cannot proceed without required field."
        << exit(FatalError);
}
```

### 10.2 การตรวจสอบ Field Existence

```cpp
// NOTE: Synthesized by AI - Verify parameters
// วิธีที่ 1: ตรวจสอบด้วย IOobject
IOobject fieldHeader
(
    "U",
    runTime.timeName(),
    mesh,
    IOobject::MUST_READ
);

if (fieldHeader.typeHeaderOk<volVectorField>(true))
{
    Info<< "Field U exists and can be read." << endl;
}
else
{
    Info<< "Field U not found." << endl;
}

// วิธีที่ 2: ตรวจสอบด้วย exists()
if (exists(runTime.timePath()/volVectorField::typeName/"U"))
{
    Info<< "Field U file exists." << endl;
}
```

---

## 11. ตัวอย่าง Utility แบบสมบูรณ์

### 11.1 Turbulence Kinetic Energy Analyzer

```cpp
// NOTE: Synthesized by AI - Verify parameters
// myTKEAnalyzer.C
#include "fvCFD.H"
#include "singlePhaseTransportModel.H"
#include "turbulentTransportModel.H"

using namespace Foam;

int main(int argc, char *argv[])
{
    #include "setRootCase.H"
    #include "createTime.H"
    #include "createMesh.H"

    // Create turbulence model
    autoPtr<incompressible::turbulenceModel> turbulence
    (
        incompressible::turbulenceModel::New(U, phi, laminarTransport)
    );

    instantList timeDirs = timeSelector::select(runTime.times(), args);

    forAll(timeDirs, timeI)
    {
        runTime.setTime(timeDirs[timeI], timeI);
        Info<< "Time: " << runTime.timeName() << endl;

        volVectorField U
        (
            IOobject("U", runTime.timeName(), mesh, IOobject::MUST_READ),
            mesh
        );

        // Calculate TKE from velocity fluctuations
        volScalarField k
        (
            IOobject
            (
                "k",
                runTime.timeName(),
                mesh,
                IOobject::NO_READ,
                IOobject::AUTO_WRITE
            ),
            0.5 * magSqr(U)
        );

        // Calculate TKE production
        volTensorField gradU = fvc::grad(U);
        volSymmTensorField S = symm(gradU);
        volScalarField P
        (
            IOobject
            (
                "kProduction",
                runTime.timeName(),
                mesh,
                IOobject::NO_READ,
                IOobject::AUTO_WRITE
            ),
            turbulence->nuEff() * 2.0 * magSqr(S)
        );

        k.write();
        P.write();

        scalar maxk = max(k).value();
        scalar maxP = max(P).value();

        reduce(maxk, maxOp<scalar>());
        reduce(maxP, maxOp<scalar>());

        Info<< "  Max TKE: " << maxk << " m²/s²" << nl
            << "  Max Production: " << maxP << " m²/s³" << endl;
    }

    Info<< "End\n" << endl;
    return 0;
}
```

---

## 12. การทดสอบและ Validation

### 12.1 การสร้าง Test Case

> [!TIP] แนวทางการทดสอบ
> ให้สร้าง Test Case ง่าย ๆ ที่มีคำตอบแน่นอน เช่น Channel Flow หรือ Cavity Flow

```cpp
// NOTE: Synthesized by AI - Verify parameters
// การตรวจสอบความถูกต้องของ Gradient
// ถ้า phi = x + y + z แล้ว grad(phi) ควรเท่ากับ (1, 1, 1)

volScalarField phi
(
    IOobject
    (
        "phi",
        runTime.timeName(),
        mesh,
        IOobject::NO_READ,
        IOobject::NO_WRITE
    ),
    mesh,
    dimensionedScalar("phi", dimless, 0.0)
);

const vectorField& C = mesh.C();
forAll(phi, cellI)
{
    phi[cellI] = C[cellI].x() + C[cellI].y() + C[cellI].z();
}

volVectorField gradPhi = fvc::grad(phi);

Info<< "Max deviation from expected gradient (1,1,1): "
    << max(mag(gradPhi - vector(1, 1, 1))).value() << endl;
```

---

## 13. เอกสารและ Commenting

> [!TIP] หลักการเขียน Comment ที่ดี
> 1. อธิบายว่าทำไม (Why) ไม่ใช่ว่าทำอะไร (What)
> 2. ใช้ Comment เพื่ออธิบาย Algorithm ที่ซับซ้อน
> 3. ระบุ References ถ้าใช้สมการจากเอกสารวิชาการ

```cpp
// NOTE: Synthesized by AI - Verify parameters
// Example of well-commented code

// Calculate Q-criterion for vortex identification
// Reference: Hunt, J.C.R. et al. (1988)
// "Eddies, streams, and convergence zones in turbulent flows"
// Q = 0.5 * (||Ω||² - ||S||²)
// where Ω = vorticity tensor, S = strain rate tensor

volTensorField gradU = fvc::grad(U);
volSymmTensorField S = symm(gradU);  // Strain rate tensor
volTensorField Omega = skew(gradU);  // Vorticity tensor

// Q = 0.5 * (tr(Ω²) - tr(S²))
volScalarField Q
(
    IOobject
    (
        "Q",
        runTime.timeName(),
        mesh,
        IOobject::NO_READ,
        IOobject::AUTO_WRITE
    ),
    0.5 * (tr(Omega & Omega) - tr(S & S))
);
```

---

## 14. สรุป Best Practices

> [!SUCCESS] Checklist สำหรับการพัฒนา Utilities ที่ดี

### 14.1 โครงสร้างโค้ด
1. ✅ ใช้ Template มาตรฐาน (`setRootCase.H`, `createTime.H`, `createMesh.H`)
2. ✅ แยก Logic ออกเป็นฟังก์ชันย่อยที่ชัดเจน
3. ✅ ใช้ `const` reference เมื่อไม่ต้องการแก้ไขข้อมูล
4. ✅ ใช้ `tmp<T>` สำหรับ field ชั่วคราว

### 14.2 Parallel Support
5. ✅ ใช้ `reduce()` สำหรับทุก global reduction operations
6. ✅ ตรวจสอบ `Pstream::nProcs()` ก่อนทำ operation
7. ✅ หลีกเลี่ยงการใช้ I/O ภายใน loop ขนาน

### 14.3 Error Handling
8. ✅ ตรวจสอบการมีอยู่ของฟิลด์ก่อนอ่าน (`exists()`)
9. ✅ ใช้ `try-catch` สำหรับ operations ที่อาจล้มเหลว
10. ✅ ให้ข้อความ Error ที่ชัดเจนและเป็นประโยชน์

### 14.4 Performance
11. ✅ ลดการสร้าง field ชั่วคราวที่ไม่จำเป็น
12. ✅ ใช้ reference (`&`) แทนการ copy
13. ✅ ระมัดระวังการใช้ memory สำหรับ large meshes

### 14.5 Documentation
14. ✅ Comment อธิบาย Algorithm ที่ซับซ้อน
15. ✅ ระบุ References ถ้าใช้สมการจากเอกสารวิชาการ
16. ✅ สร้าง README อธิบายการใช้งาน

---

## 15. แหล่งอ้างอิงและการศึกษาเพิ่มเติม

1. **OpenFOAM Programmer's Guide**: https://www.openfoam.com/documentation/programmers-guide/
2. **OpenFOAM Source Code**: `$FOAM_SRC/applications/utilities/`
3. **CFD Online Wiki**: https://wiki.openfoam.com/

---

## 📋 สรุป (Summary)

ในบทนี้เราได้เรียนรู้:

- ✅ **โครงสร้างพื้นฐาน** ของ Custom Utilities
- ✅ **การคอมไพล์** ด้วย `wmake`
- ✅ **การประมวลผลฟิลด์** และการคำนวณปริมาณต่าง ๆ
- ✅ **Parallel Reduction** สำหรับการรันแบบขนาน
- ✅ **การจัดการ Boundary Conditions**
- ✅ **การเขียน Output** และการ Debug
- ✅ **Best Practices** สำหรับการพัฒนา Utilities ที่มีประสิทธิภาพ

---

**หัวข้อถัดไป**: [[07_Integration_with_Solver_Workflows]] เพื่อดูวิธีการรวม Custom Utility เข้ากับไปป์ไลน์การทำงานจริงและ Solver Workflows
