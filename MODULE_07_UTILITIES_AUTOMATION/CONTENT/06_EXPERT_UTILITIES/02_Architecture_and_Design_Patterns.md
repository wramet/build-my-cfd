# Architecture and Design Patterns

สถาปัตยกรรมและรูปแบบการออกแบบ Utilities

> **ลิงก์ที่เกี่ยวข้อง**:
> - ดูภาพรวม Expert Utilities → [00_Overview.md](./00_Overview.md)
> - ดู Utility Categories → [01_Utility_Categories_and_Organization.md](./01_Utility_Categories_and_Organization.md)
> - ดูการสร้าง Custom Utilities → [05_Creating_Custom_Utilities.md](./05_Creating_Custom_Utilities.md)

---

## 🎯 Learning Objectives (วัตถุประสงค์การเรียนรู้)

เมื่อจบบทนี้ คุณจะสามารถ:

1. **เข้าใจโครงสร้างมาตรฐาน** ของ OpenFOAM utility และไลบรารีหลักที่ใช้
2. **ใช้งาน argList** สำหรับจัดการ command line arguments ได้อย่างมีประสิทธิภาพ
3. **อ่านและเขียน Fields** (volScalarField, volVectorField, volTensorField) ได้อย่างถูกต้อง
4. **ประยุกต์ใช้ Design Patterns** ทั่วไป (Time Loop, Patch Loop, Cell Iteration)
5. **สร้าง Utility แบบเต็ม** ที่สามารถ compile และใช้งานได้จริง

---

## 📋 บทนำ (Introduction)

### WHY: ทำไมต้องเข้าใจ Architecture?

Utilities ใน OpenFOAM ทั้งหมด **ใช้โครงสร้างและรูปแบบเดียวกัน** (Common Patterns) การเข้าใจ architecture นี้มีความสำคัญอย่างยิ่ง:

**ก่อนสร้าง Custom Utilities:**
- เข้าใจโครงสร้าง → อ่านโค้ดคนอื่นเข้าใจง่าย → สามารถเรียนรู้จาก utilities ที่มีอยู่
- รู้จัก Design Patterns → เขียน utility ใหม่ได้รวดเร็ว → ไม่ต้องคิดโครงสร้างใหม่ทุกครั้ง
- เข้าใจ Field I/O → ดูแลรักษาโค้ดง่าย → Debug ได้เร็ว

**ประโยชน์ของการทำความเข้าใจ:**
1. **ความสามารถในการอ่าน Source Code**: OpenFOAM มี utilities หลายร้อยตัว ถ้าเข้าใจ architecture สามารถเปิดอ่านและเรียนรู้ได้ทันที
2. **การพัฒนาที่รวดเร็ว**: ไม่ต้องเริ่มจากศูนย์ ใช้ patterns ที่มีอยู่เป็น template
3. **การ Debug ที่มีประสิทธิภาพ**: รู้ว่า objects ถูกสร้างเมื่อไหร่ และใช้งานอย่างไร
4. **การสื่อสาร**: สามารถอธิบายโค้ดให้ผู้อื่นเข้าใจด้วยภาษาทางการของ OpenFOAM

### WHAT: สิ่งที่จะเรียนรู้

ในบทนี้คุณจะได้เรียนรู้:
- **โครงสร้างมาตรฐาน** ของ OpenFOAM utility
- **การใช้ argList** สำหรับ command line arguments
- **การอ่าน/เขียน Fields** (volScalarField, volVectorField, volTensorField)
- **Design Patterns** ที่ใช้บ่อยใน OpenFOAM
- **ตัวอย่าง Utility แบบเต็ม** พร้อม compile instructions

### HOW: แนวทางการเรียนรู้

1. **เข้าใจ Skeleton**: เริ่มจากโครงสร้างพื้นฐาน (includes, main function)
2. **ลงมือปฏิบัติ**: ทำตามตัวอย่าง code และ compile จริง
3. **วิเคราะห์ Patterns**: สังเกตรูปแบบที่ซ้ำกันใน utilities ต่างๆ
4. **ขยายความ**: ลองแก้ไข และสร้าง utilities ของตัวเอง

> [!TIP] **ก่อนเริ่ม**
> บทนี้ต้องการพื้นฐาน **C++ ขั้นพื้นฐาน** (classes, pointers, references)
> ถ้ายังไม่คุ้นเคย แนะนำให้อ่านพื้นฐาน C++ ก่อน

---

## 🏗️ 1. Standard Structure (โครงสร้างมาตรฐาน)

### 1.1 Skeleton ของ Utility

ทุก OpenFOAM utility มีโครงสร้างเหมือนกัน:

```cpp
#include "fvCFD.H"

// ========================
// 1. Setup (เริ่มต้น)
// ========================
int main(int argc, char *argv[])
{
    // 1.1 ตั้งค่า Root Case
    #include "setRootCase.H"

    // 1.2 สร้าง Time object
    #include "createTime.H"

    // 1.3 สร้าง Mesh object
    #include "createMesh.H"

    // ========================
    // 2. Utility Logic (เนื้อหาหลัก)
    // ========================

    // 2.1 อ่าน fields
    // 2.2 ประมวลผล
    // 2.3 เขียน results

    // ========================
    // 3. Cleanup (จบ)
    // ========================
    Info<< "\nEnd\n" << endl;

    return 0;
}
```

### 1.2 Include Files หลัก

| Include | หน้าที่ | สร้าง Object | รายละเอียดเพิ่มเติม |
|:--------|:---------|:-------------|:-------------------|
| **setRootCase.H** | Parse command line, set case directory | `args` | อ่าน command line arguments และกำหนด case directory |
| **createTime.H** | Create Time object (manage time) | `runTime` | อ่าน controlDict, กำหนด startTime/endTime/deltaT |
| **createMesh.H** | Create Mesh object | `mesh` | อ่าน mesh จาก constant/polyMesh/ |
| **createFields.H** | (Optional) Create custom fields | Custom fields | สร้าง fields พิเศษที่ต้องใช้ |

**วิธีการทำงาน:**

```cpp
#include "setRootCase.H"
// → อ่าน command line arguments
// → กำหนด case directory (ตำแหน่งโฟลเดอร์)
// → สร้าง object: argList args

#include "createTime.H"
// → อ่าน controlDict
// → กำหนด startTime, endTime, deltaT
// → สร้าง object: Time runTime

#include "createMesh.H"
// → อ่าน mesh จาก constant/polyMesh/
// → สร้าง object: fvMesh mesh
```

### 1.3 fvCFD.H - The Master Include

```cpp
#include "fvCFD.H"
```

**fvCFD.H** เป็น header file หลักที่รวม includes ที่จำเป็นสำหรับ finite volume CFD:

- **Mesh types**: `fvMesh`, `polyMesh`
- **Field types**: `volScalarField`, `volVectorField`, `volTensorField`
- **Boundary conditions**: `fvPatchField`, `fixedValueFvPatchField`
- **Time management**: `Time`
- **Mathematical operations**: `fvm`, `fvc` (finite volume method/volume calculus)

> [!NOTE] **ทำไมต้องใช้ fvCFD.H?**
> - รวมทุกอย่างที่ต้องการในที่เดียว
> - ลดความซับซ้อนของ includes
> - เป็นมาตรฐานใน OpenFOAM utilities

---

## 🔧 2. Command Line Arguments (argList)

### 2.1 argList Object

หลังจาก `#include "setRootCase.H"` จะมี object `argList args` ถูกสร้างขึ้น:

```cpp
argList args(argc, argv);  // สร้างโดย setRootCase.H
```

**ความสามารถ:**
- อ่าน command line arguments
- กำหนด case directory
- เพิ่ม custom options
- Validate arguments

### 2.2 เพิ่ม Options

```cpp
// หลัง #include "setRootCase.H"

// เพิ่ม option: -patch <name>
args.addOption("patch", "patchName", "Patch to process");

// เพิ่ม option: -overwrite (no value)
args.addOption("overwrite", "Overwrite existing files");

// เพิ่ม option: -time <t> (default: latestTime)
args.addOption("time", "0", "Time to process");

// เพิ่ม option: -field <name> (required)
args.addOption("field", "fieldName", "Field to process");

// Parse (อัตโนมัติจาก setRootCase.H)
```

### 2.3 อ่านค่า Arguments

```cpp
// อ่าน option (มี value)
if (args.found("patch"))
{
    word patchName = args.get<word>("patch");
    Info<< "Processing patch: " << patchName << endl;
}

// เช็ค option (ไม่มี value, flag เท่านั้น)
bool overwrite = args.found("overwrite");
if (overwrite)
{
    Info<< "Will overwrite existing files" << endl;
}

// อ่าน option มี default value
scalar timeValue = args.get<scalar>("time", runTime.timeName());
Info<< "Processing time: " << timeValue << endl;

// อ่าน option ที่จำเป็นต้องมี
if (!args.found("field"))
{
    FatalError << "Must specify -field option" << exit(FatalError);
}
word fieldName = args.get<word>("field");
```

### 2.4 ตัวอย่างการใช้งาน

```bash
# รัน utility
myUtility -patch inlet -overwrite -time 100 -field p

# Output:
# Processing patch: inlet
# Will overwrite existing files
# Processing time: 100
# Processing field: p
```

### 2.5 การระบุ Time Directory

```cpp
// เลือก time directory ที่ต้องการ
if (args.found("time"))
{
    scalar timeValue = args.get<scalar>("time");
    instantList timeDirs = Time::findTimes(args.rootPath());
    forAll(timeDirs, i)
    {
        if (timeDirs[i].value() == timeValue)
        {
            runTime.setTime(timeDirs[i], i);
            break;
        }
    }
}
```

---

## 📦 3. Field Access (การอ่าน/เขียน Fields)

### 3.1 IOobject - The Field Constructor

ทุก field ใน OpenFOAM ต้องมี **IOobject** ที่ระบุ:

```cpp
IOobject
(
    "fieldName",            // 1. ชื่อ field
    runTime.timeName(),     // 2. Time directory (เช่น 0, 100, 200)
    mesh,                   // 3. Mesh reference
    IOobject::MUST_READ     // 4. Read option
)
```

**Read Options:**
| Option | ความหมาย | ใช้เมื่อ |
|:-------|:-----------|:---------|
| `IOobject::MUST_READ` | ต้องอ่าน (error ถ้าไม่เจอ) | Field ที่จำเป็นต้องมี |
| `IOobject::READ_IF_PRESENT` | อ่านถ้ามี (ไม่ error ถ้าไม่เจอ) | Field ที่เป็น optional |
| `IOobject::NO_READ` | ไม่อ่าน (สร้างใหม่) | Field ใหม่ที่จะสร้าง |

**Write Options:**
| Option | ความหมาย | ใช้เมื่อ |
|:-------|:-----------|:---------|
| `IOobject::AUTO_WRITE` | เขียนอัตโนมัติเมื่อ runTime++ | Field ที่ต้องการบันทึกทุก time step |
| `IOobject::NO_WRITE` | ไม่เขียน | Field ชั่วคราว |

### 3.2 อ่าน Fields ที่มีอยู่แล้ว

```cpp
// อ่าน scalar field (เช่น p, T)
volScalarField p
(
    IOobject
    (
        "p",                    // ชื่อ field
        runTime.timeName(),     // Time folder (เช่น 0, 100, 200)
        mesh,                   // Mesh reference
        IOobject::MUST_READ,    // ต้องอ่าน (error ถ้าไม่เจอ)
        IOobject::NO_WRITE      // ไม่เขียน (เพราะไม่ได้แก้ไข)
    ),
    mesh
);

// อ่าน vector field (เช่น U)
volVectorField U
(
    IOobject
    (
        "U",
        runTime.timeName(),
        mesh,
        IOobject::MUST_READ,
        IOobject::AUTO_WRITE      // เขียนอัตโนมัติถ้าแก้ไข
    ),
    mesh
);

// แสดงผลข้อมูล
Info<< "Field 'p' loaded successfully" << endl;
Info<< "  Max p: " << max(p).value() << endl;
Info<< "  Min p: " << min(p).value() << endl;
Info<< "  Avg p: " << average(p).value() << endl;

Info<< "Field 'U' loaded successfully" << endl;
Info<< "  Max |U|: " << max(mag(U)).value() << endl;
```

### 3.3 สร้าง Fields ใหม่

```cpp
// สร้าง scalar field ใหม่ (เริ่มจาก 0)
volScalarField myField
(
    IOobject
    (
        "myField",              // ชื่อ field
        runTime.timeName(),
        mesh,
        IOobject::NO_READ,      // ไม่ต้องอ่าน (สร้างใหม่)
        IOobject::AUTO_WRITE    // เขียนอัตโนมัติ
    ),
    mesh,
    dimensionedScalar("zero", dimless, Zero)  // ค่าเริ่มต้น = 0
);

// สร้างจาก field ที่มีอยู่
volScalarField pSquared = sqr(p);  // p²

// สร้าง vector field ใหม่
volVectorField myVector
(
    IOobject
    (
        "myVector",
        runTime.timeName(),
        mesh,
        IOobject::NO_READ,
        IOobject::AUTO_WRITE
    ),
    mesh,
    dimensionedVector("zero", dimVelocity, Zero)
);

// สร้าง field ที่มี dimension
volScalarField Tkelvin
(
    IOobject
    (
        "Tkelvin",
        runTime.timeName(),
        mesh,
        IOobject::NO_READ,
        IOobject::AUTO_WRITE
    ),
    mesh,
    dimensionedScalar("T0", dimTemperature, 293.15)  // 293.15 K
);
```

### 3.4 เขียน Fields ลงไฟล์

```cpp
// เขียน field ทันที
myField.write();

// หรือเขียนหลาย fields
pSquared.write();
myField.write();
myVector.write();

// Output:
// --> 0/pSquared, 0/myField, 0/myVector

// เขียนเฉพาะถ้ามีการเปลี่ยนแปลง
if (args.found("overwrite"))
{
    myField.write();
}
```

### 3.5 การอ่าน Optional Fields

```cpp
// อ่าน field ที่อาจจะไม่มี
if (exists(runTime.timePath() / "T"))
{
    volScalarField T
    (
        IOobject
        (
            "T",
            runTime.timeName(),
            mesh,
            IOobject::MUST_READ,
            IOobject::NO_WRITE
        ),
        mesh
    );
    
    Info<< "Temperature field found" << endl;
    Info<< "  Max T: " << max(T).value() << endl;
}
else
{
    Info<< "Temperature field not found, skipping..." << endl;
}
```

---

## 🧮 4. ตัวอย่าง Utility แบบเต็ม

### 4.1 Utility: คำนวณค่าเฉลี่ยบน Patch

**วัตถุประสงค์**: คำนวณค่าเฉลี่ยของ pressure บน patch ที่ระบุ

```cpp
#include "fvCFD.H"

int main(int argc, char *argv[])
{
    // 1. Setup
    #include "setRootCase.H"
    #include "createTime.H"
    #include "createMesh.H"

    // 2. Add command line option
    args.addOption("patch", "patchName", "Patch to calculate average");

    // 3. Read option
    if (!args.found("patch"))
    {
        FatalError << "Must specify -patch option" << exit(FatalError);
    }

    word patchName = args.get<word>("patch");
    Info<< "Calculating average pressure on patch: " << patchName << endl;

    // 4. Read pressure field
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

    // 5. Get patch reference
    label patchID = mesh.boundaryMesh().findPatchID(patchName);

    if (patchID == -1)
    {
        FatalError << "Patch " << patchName << " not found" << exit(FatalError);
    }

    // 6. Calculate average on patch
    const fvPatchScalarField& pp = p.boundaryField()[patchID];
    scalar avgP = gAverage(pp);
    scalar maxP = gMax(pp);
    scalar minP = gMin(pp);

    // 7. Output result
    Info<< "\n=== Patch Statistics ===" << endl;
    Info<< "Patch: " << patchName << endl;
    Info<< "  Average pressure: " << avgP << " Pa" << endl;
    Info<< "  Max pressure: " << maxP << " Pa" << endl;
    Info<< "  Min pressure: " << minP << " Pa" << endl;
    Info<< "========================\n" << endl;

    Info<< "\nEnd\n" << endl;
    return 0;
}
```

### 4.2 วิธี Compile

```bash
# สร้าง folder สำหรับ utility
mkdir -p1$FOAM_RUN/applications/utilities/myUtility
cd1$FOAM_RUN/applications/utilities/myUtility

# สร้างไฟล์:
# - myUtility.C (code ด้านบน)
# - Make/files
# - Make/options

# Make/files:
myUtility.C

EXE =1$(FOAM_USER_APPBIN)/myUtility

# Make/options:
EXE_INC = \
    -I$(LIB_SRC)/finiteVolume/lnInclude \
    -I$(LIB_SRC)/meshTools/lnInclude

EXE_LIBS = \
    -lfiniteVolume \
    -lmeshTools

# Compile
wmake

# รัน
cd ~/OpenFOAM/caseName
myUtility -patch inlet
```

### 4.3 Utility: Time Loop Processing

**วัตถุประสงค์**: คำนวณ statistics ของ field ผ่านทุก time steps

```cpp
#include "fvCFD.H"
#include <fstream>

int main(int argc, char *argv[])
{
    #include "setRootCase.H"
    #include "createTime.H"
    #include "createMesh.H"

    // Add option
    args.addOption("field", "fieldName", "Field to process");
    
    if (!args.found("field"))
    {
        FatalError << "Must specify -field option" << exit(FatalError);
    }
    
    word fieldName = args.get<word>("field");
    
    // Create output file
    std::ofstream outFile(fieldName + "Stats.dat");
    outFile << "# Time Max Min Avg" << endl;
    
    // Get all time directories
    instantList timeDirs = Time::findTimes(args.rootPath());
    
    // Loop through all time directories
    forAll(timeDirs, i)
    {
        runTime.setTime(timeDirs[i], i);
        
        Info<< "Processing time: " << runTime.timeName() << endl;
        
        // Try to read field
        if (exists(runTime.timePath() / fieldName))
        {
            volScalarField field
            (
                IOobject
                (
                    fieldName,
                    runTime.timeName(),
                    mesh,
                    IOobject::MUST_READ,
                    IOobject::NO_WRITE
                ),
                mesh
            );
            
            scalar maxVal = max(field).value();
            scalar minVal = min(field).value();
            scalar avgVal = average(field).value();
            
            Info<< "  Max: " << maxVal << ", Min: " << minVal 
                << ", Avg: " << avgVal << endl;
                
            outFile << runTime.timeValue() << " " 
                    << maxVal << " " << minVal << " " << avgVal << endl;
        }
    }
    
    outFile.close();
    Info<< "\nResults written to " << fieldName + "Stats.dat" << endl;
    
    Info<< "\nEnd\n" << endl;
    return 0;
}
```

---

## 🎨 5. Common Design Patterns

### 5.1 Pattern 1: Time Loop (วนลูปตามเวลา)

**การใช้งาน**: ประมวลผล field ผ่านหลาย time steps

```cpp
#include "fvCFD.H"

int main(int argc, char *argv[])
{
    #include "setRootCase.H"
    #include "createTime.H"
    #include "createMesh.H"

    // อ่าน field
    volScalarField T
    (
        IOobject
        (
            "T",
            runTime.timeName(),
            mesh,
            IOobject::MUST_READ,
            IOobject::NO_WRITE
        ),
        mesh
    );

    // วนลูปตาม time steps
    while (runTime.loop())
    {
        Info<< "Time = " << runTime.timeName() << endl;

        runTime++;

        // อ่าน field ใหม่ (ถ้ามีการ update)
        T = volScalarField
        (
            IOobject
            (
                "T",
                runTime.timeName(),
                mesh,
                IOobject::MUST_READ,
                IOobject::NO_WRITE
            ),
            mesh
        );

        // ประมวลผล...
        scalar avgT = average(T).value();
        scalar maxT = max(T).value();
        
        Info<< "Average T: " << avgT << endl;
        Info<< "Max T: " << maxT << endl;
    }

    Info<< "\nEnd\n" << endl;
    return 0;
}
```

### 5.2 Pattern 2: Loop ผ่าน Patches

**การใช้งาน**: ประมวลผล field บน boundary patches

```cpp
// วนลูปผ่านทุก patches
const fvPatchList& patches = mesh.boundary();

Info<< "\n=== Patch Statistics ===" << endl;
forAll(patches, patchi)
{
    const fvPatch& patch = patches[patchi];

    Info<< "Patch " << patch.name()
        << " has " << patch.size() << " faces" << endl;

    // เข้าถึง field values บน patch
    const fvPatchScalarField& pp = p.boundaryField()[patchi];
    scalar patchAvg = gAverage(pp);
    scalar patchMax = gMax(pp);
    scalar patchMin = gMin(pp);

    Info<< "  Average p: " << patchAvg << endl;
    Info<< "  Max p: " << patchMax << endl;
    Info<< "  Min p: " << patchMin << endl;
}
Info<< "========================\n" << endl;
```

### 5.3 Pattern 3: Cell Iteration (วนลูปผ่าน cells)

**การใช้งาน**: ประมวลผลทุก cell แยกกัน

```cpp
// วนลูปผ่านทุก cells (แบบง่าย)
forAll(p, celli)
{
    scalar cellP = p[celli];  // ค่า pressure ที่ cell i
    vector cellU = U[celli];  // ค่า velocity ที่ cell i

    // ประมวลผล...
    if (cellP > 1e5)  // ถ้า pressure > 100 kPa
    {
        p[celli] = cellP * 1.1;  // เพิ่มค่า p ขึ้น 10%
    }
}

// หรือใช้ iterator (สำหรับ operations ซับซ้อน)
for (int celli = 0; celli < mesh.nCells(); celli++)
{
    // เข้าถึง cell center
    const vector& cellCenter = mesh.C()[celli];
    
    // เข้าถึง cell volume
    scalar cellVolume = mesh.V()[celli];
    
    // ประมวลผล...
    if (cellCenter.x() > 0.5)  // ถ้าอยู่ในบริเวณ x > 0.5
    {
        p[celli] *= 1.05;  // เพิ่ม pressure 5%
    }
}
```

### 5.4 Pattern 4: Conditional Execution

**การใช้งาน**: เช็คว่ามีไฟล์/field หรือไม่

```cpp
// เช็คว่า field มีอยู่หรือไม่
if (exists(runTime.timePath() / "myField"))
{
    volScalarField myField
    (
        IOobject
        (
            "myField",
            runTime.timeName(),
            mesh,
            IOobject::MUST_READ,
            IOobject::NO_WRITE
        ),
        mesh
    );
    Info<< "Found myField" << endl;
}
else
{
    Info<< "myField not found, using default" << endl;
    volScalarField myField
    (
        IOobject
        (
            "myField",
            runTime.timeName(),
            mesh,
            IOobject::NO_READ,
            IOobject::AUTO_WRITE
        ),
        mesh,
        dimensionedScalar("zero", dimless, Zero)
    );
}

// เช็คว่า patch มีอยู่หรือไม่
word patchName = "inlet";
label patchID = mesh.boundaryMesh().findPatchID(patchName);

if (patchID != -1)
{
    Info<< "Patch " << patchName << " found" << endl;
}
else
{
    Warning << "Patch " << patchName << " not found" << endl;
}
```

### 5.5 Pattern 5: Field Operations

**การใช้งาน**: ประมวลผล field ด้วย operations

```cpp
// Operation บน scalar fields
volScalarField p2 = sqr(p);      // p²
volScalarField sqrtP = sqrt(p);  // √p (ต้องไม่ติดลบ)
volScalarField magP = mag(p);    // |p|
volScalarField expP = exp(p);    // e^p
volScalarField logP = log(p);    // ln(p) (ต้อง > 0)

// Operation บน vector fields
volScalarField magU = mag(U);              // |U|
volVectorField U2 = U * 2.0;               // Scale
volVectorField Unew = U + vector(1, 0, 0); // Add vector

// Field arithmetic
volScalarField sum1 = p + T;         // p + T
volScalarField sum2 = p * 1.1;       // p * 1.1
volScalarField sum3 = p / 1000.0;    // p / 1000

// Component access
volScalarField Ux = U.component(0);  // U.x
volScalarField Uy = U.component(1);  // U.y
volScalarField Uz = U.component(2);  // U.z
```

---

## 📊 6. Working with Different Data Types

### 6.1 Scalar Fields (เช่น p, T)

```cpp
volScalarField p(...);

// ค่าสูงสุด/ต่ำสุด/เฉลี่ย
scalar maxP = max(p).value();
scalar minP = min(p).value();
scalar avgP = average(p).value();
scalar sumP = sum(p).value();

// ปรับ scale
p *= 1.1;  // เพิ่ม 10%
p += 100;  // บวก 100
p -= 50;   // ลบ 50
p /= 2.0;  // หาร 2

// Operations
volScalarField pSquared = sqr(p);      // p²
volScalarField pSqrt = sqrt(p);        // √p (ต้องไม่ติดลบ)
volScalarField magP = mag(p);          // |p|
volScalarField powP3 = pow(p, 3);      // p³
volScalarField expP = exp(p);          // e^p
volScalarField logP = log(p);          // ln(p)
volScalarField log10P = log10(p);      // log10(p)

// Trigonometric
volScalarField sinP = sin(p);
volScalarField cosP = cos(p);
volScalarField tanP = tan(p);

// Conditional
volScalarField pLimited = max(p, dimensionedScalar("min", dimPressure, 0));
volScalarField pClipped = min(max(p, dimensionedScalar("min", dimPressure, 0)), 
                              dimensionedScalar("max", dimPressure, 1e5));
```

### 6.2 Vector Fields (เช่น U)

```cpp
volVectorField U(...);

// Magnitude (ขนาด)
volScalarField magU = mag(U);  // |U| = sqrt(Ux² + Uy² + Uz²)

// ค่าสูงสุด/ต่ำสุด
scalar maxU = max(magU).value();
scalar minU = min(magU).value();
scalar avgU = average(magU).value();

// Components
volScalarField Ux = U.component(0);  // U.x
volScalarField Uy = U.component(1);  // U.y
volScalarField Uz = U.component(2);  // U.z

// หรือใช้ inline member functions
volScalarField Ux_alt = U.x();
volScalarField Uy_alt = U.y();
volScalarField Uz_alt = U.z();

// Vector operations
volVectorField Unew = U * 1.1;               // Scale
volVectorField V = U + vector(1, 0, 0);      // Add vector
volVectorField W = U - vector(0, 1, 0);      // Subtract vector

// Normalize
volVectorField Unorm = U / magU;  // Unit vector

// Vector products
volScalarField dotUV = U & V;     // Dot product
volVectorField crossUV = U ^ V;   // Cross product
```

### 6.3 Tensor Fields (เช่น Stress tensor)

```cpp
volSymmTensorField sigma(...);  // Symmetric tensor

// Components (6 components for symmetric tensor)
volScalarField sigmaxx = sigma.component(0);  // xx
volScalarField sigmaxy = sigma.component(1);  // xy
volScalarField sigmaxz = sigma.component(2);  // xz
volScalarField sigmayy = sigma.component(3);  // yy
volScalarField sigmayz = sigma.component(4);  // yz
volScalarField sigmazz = sigma.component(5);  // zz

// Invariants
volScalarField tr = tr(sigma);           // Trace (sum of diagonal)
volScalarField det = det(sigma);         // Determinant
volSymmTensorField inv = inv(sigma);     // Inverse

// Eigenvalues (symmetric tensor)
volScalarField lambdaMax = max(eigenValues(sigma));
volScalarField lambdaMin = min(eigenValues(sigma));

// Tensor operations
volSymmTensorField sigma2 = sqr(sigma);  // σ²
volScalarField magSigma = mag(sigma);    // |σ|
```

### 6.4 Surface Fields (บน faces)

```cpp
// Surface scalar field (บน faces)
surfaceScalarField phi
(
    IOobject
    (
        "phi",
        runTime.timeName(),
        mesh,
        IOobject::MUST_READ,
        IOobject::AUTO_WRITE
    ),
    mesh
);

// Surface vector field
surfaceVectorField faceCentres = mesh.Cf();
surfaceVectorField faceAreas = mesh.Sf();

// ค่าเฉลี่ยบน faces
scalar avgPhi = average(phi).value();
scalar maxPhi = max(phi).value();

// Interpolate จาก cell ไป face
surfaceScalarField pFace = fvc::interpolate(p);
```

---

## 🛠️ 7. Debugging Tips

### 7.1 แสดงผลข้อมูล

```cpp
// แสดงผลลัพธ์ของ mesh
Info<< "\n=== Mesh Information ===" << endl;
Info<< "Number of cells: " << mesh.nCells() << endl;
Info<< "Number of faces: " << mesh.nFaces() << endl;
Info<< "Number of internal faces: " << mesh.nInternalFaces() << endl;
Info<< "Number of patches: " << mesh.boundary().size() << endl;
Info<< "Number of points: " << mesh.nPoints() << endl;

// แสดงผลลัพธ์ของ time
Info<< "\n=== Time Information ===" << endl;
Info<< "Start time: " << runTime.startTime().value() << endl;
Info<< "End time: " << runTime.endTime().value() << endl;
Info<< "Delta t: " << runTime.deltaTValue() << endl;
Info<< "Current time: " << runTime.timeValue() << endl;

// แสดงค่า field
Info<< "\n=== Field Information ===" << endl;
Info<< "Field 'p':" << endl;
Info<< "  Min: " << min(p).value() << endl;
Info<< "  Max: " << max(p).value() << endl;
Info<< "  Average: " << average(p).value() << endl;
Info<< "  Sum: " << sum(p).value() << endl;
```

### 7.2 เช็ค Errors

```cpp
// เช็คว่า patch มีอยู่จริง
word patchName = "inlet";
label patchID = mesh.boundaryMesh().findPatchID(patchName);

if (patchID == -1)
{
    FatalErrorIn("main()")
        << "Patch " << patchName << " not found"
        << exit(FatalError);
}

// เช็คว่า field มีอยู่
word fieldName = "p";
if (!exists(runTime.timePath() / fieldName))
{
    WarningIn("main()")
        << "Field " << fieldName << " not found at time "
        << runTime.timeName() << endl
        << "Skipping..." << endl;
}

// เช็คว่า field มีค่าที่ไม่ถูกต้อง
scalar minP = min(p).value();
if (minP < 0)
{
    WarningIn("main()")
        << "Field " << p.name() << " has negative values: min = " << minP
        << endl;
}
```

### 7.3 Assertions

```cpp
// Assert ค่าที่คาดหวัง
if (mesh.nCells() == 0)
{
    FatalErrorIn("main()")
        << "Mesh has no cells!"
        << exit(FatalError);
}

// Assert ว่า field มีค่า
if (max(mag(p)).value() < 1e-10)
{
    WarningIn("main()")
        << "Field " << p.name() << " has very small values"
        << endl;
}

// Assert patch size
label patchID = mesh.boundaryMesh().findPatchID("inlet");
if (patchID != -1)
{
    label nFaces = mesh.boundaryMesh()[patchID].size();
    if (nFaces == 0)
    {
        WarningIn("main()")
            << "Patch 'inlet' has no faces"
            << endl;
    }
}
```

---

## 📋 Quick Reference

### 8.1 Includes ที่ใช้บ่อย

| Include | Object ที่สร้าง | ใช้ทำอะไร |
|:--------|:-----------------|:------------|
| **fvCFD.H** | - | Master include สำหรับ finite volume |
| **setRootCase.H** | `args` | Parse command line |
| **createTime.H** | `runTime` | Manage time |
| **createMesh.H** | `mesh` | Mesh access |
| **createFields.H** | (Custom) | Custom fields |

### 8.2 Field IOobject Options

| Option | ความหมาย | ใช้เมื่อ |
|:-------|:-----------|:---------|
| `IOobject::MUST_READ` | ต้องอ่าน (error ถ้าไม่เจอ) | Field ที่จำเป็นต้องมี |
| `IOobject::READ_IF_PRESENT` | อ่านถ้ามี (ไม่ error ถ้าไม่เจอ) | Field ที่เป็น optional |
| `IOobject::NO_READ` | ไม่อ่าน (สร้างใหม่) | Field ใหม่ที่จะสร้าง |
| `IOobject::AUTO_WRITE` | เขียนอัตโนมัติ | Field ที่ต้องการบันทึก |
| `IOobject::NO_WRITE` | ไม่เขียน | Field ชั่วคราว |

### 8.3 Common Operations

| Operation | Code | ความหมาย |
|:----------|:-----|:----------|
| **Max/Min/Avg** | `max(field).value()`, `min(field).value()`, `average(field).value()` | ค่าสูงสุด/ต่ำสุด/เฉลี่ย |
| **Sum** | `sum(field).value()` | ผลรวม |
| **Magnitude** | `mag(vectorField)` | ขนาดของเวกเตอร์ |
| **Squared** | `sqr(field)` | ยกกำลังสอง |
| **Sqrt** | `sqrt(field)` | รากที่สอง |
| **Power** | `pow(field, n)` | ยกกำลัง n |
| **Exp** | `exp(field)` | e^field |
| **Log** | `log(field)`, `log10(field)` | ln, log10 |

### 8.4 Useful Functions

```cpp
// Mesh info
mesh.nCells()              // จำนวน cells
mesh.nFaces()              // จำนวน faces
mesh.nPoints()             // จำนวน points
mesh.boundary().size()     // จำนวน patches

// Time info
runTime.timeValue()        // เวลาปัจจุบัน
runTime.timeName()         // ชื่อ time directory
runTime.deltaTValue()      // Delta t
runTime.startTime().value() // Start time
runTime.endTime().value()   // End time

// Patch info
mesh.boundaryMesh().findPatchID("name") // หา patch ID
mesh.boundaryMesh()[patchID].size()    // จำนวน faces บน patch
mesh.boundaryMesh()[patchID].name()    // ชื่อ patch

// Field info
field.name()               // ชื่อ field
field.size()               // จำนวน elements
field.dimensions()         // Dimensions

// File operations
exists(path)               // เช็คว่ามีไฟล์หรือไม่
```

---

## 📝 แบบฝึกหัด (Exercises)

### ระดับง่าย (Easy)
1. **True/False**: ทุก OpenFOAM utility ต้องมี `#include "fvCFD.H"`
   <details>
   <summary>คำตอบ</summary>
   ✅ จริง - fvCFD.H รวม includes พื้นฐานทุกอย่างสำหรับ finite volume
   </details>

2. **เลือกตอบ**: `createTime.H` สร้าง object อะไร?
   - a) `mesh`
   - b) `runTime`
   - c) `args`
   - d) `fields`
   <details>
   <summary>คำตอบ</summary>
   ✅ b) `runTime`
   </details>

3. **เลือกตอบ**: `IOobject::MUST_READ` ทำอะไร?
   - a) สร้าง field ใหม่
   - b) อ่านถ้ามี
   - c) ต้องอ่าน (error ถ้าไม่เจอ)
   - d) เขียนอัตโนมัติ
   <details>
   <summary>คำตอบ</summary>
   ✅ c) ต้องอ่าน (error ถ้าไม่เจอ)
   </details>

### ระดับปานกลาง (Medium)
4. **อธิบาย**: แตกต่างระหว่าง `IOobject::MUST_READ` และ `IOobject::READ_IF_PRESENT` คืออะไร?
   <details>
   <summary>คำตอบ</summary>
   - **MUST_READ**: ต้องอ่าน field นั้น (FatalError ถ้าไม่เจอ) ใช้เมื่อ field จำเป็นต้องมี
   - **READ_IF_PRESENT**: อ่านถ้ามี (ไม่ error ถ้าไม่เจอ) ใช้เมื่อ field เป็น optional
   </details>

5. **อธิบาย**: argList ทำหน้าที่อะไร?
   <details>
   <summary>คำตอบ</summary>
   **argList** ทำหน้าที่:
   - อ่าน command line arguments
   - กำหนด case directory
   - เพิ่ม custom options
   - Validate arguments
   </details>

6. **เขียนโค้ด**: จงเขียน code อ่าน field `T` และคำนวณค่าเฉลี่ย
   <details>
   <summary>คำตอบ</summary>
   ```cpp
   volScalarField T
   (
       IOobject
       (
           "T",
           runTime.timeName(),
           mesh,
           IOobject::MUST_READ,
           IOobject::NO_WRITE
       ),
       mesh
   );
   scalar avgT = average(T).value();
   Info<< "Average T: " << avgT << endl;
   ```
   </details>

7. **เขียนโค้ด**: จงเขียน code เพิ่ม option `-field <name>` และอ่านค่า
   <details>
   <summary>คำตอบ</summary>
   ```cpp
   args.addOption("field", "fieldName", "Field to process");
   
   if (!args.found("field"))
   {
       FatalError << "Must specify -field option" << exit(FatalError);
   }
   
   word fieldName = args.get<word>("field");
   Info<< "Processing field: " << fieldName << endl;
   ```
   </details>

### ระดับสูง (Hard)
8. **Hands-on**: สร้าง utility ที่:
   - รับ option `-field <name>` (ชื่อ field ที่ต้องการ)
   - รับ option `-patch <name>` (ชื่อ patch)
   - คำนวณค่าเฉลี่ย, สูงสุด, ต่ำสุด ของ field บน patch นั้น
   - แสดงผลอย่างเป็นระเบียบ

   <details>
   <summary>คำใบ้</summary>
   ใช้ `mesh.boundaryMesh().findPatchID()` และ `field.boundaryField()[patchID]`
   </details>

9. **Project**: สร้าง utility ที่:
   - วนลูปผ่านทุก time steps
   - คำนวณค่า max/min/avg ของ field `U`
   - เขียนผลลัพธ์ไปยังไฟล์ `Ustats.dat` พร้อม time column
   - ใช้ `std::ofstream` สำหรับเขียนไฟล์

   <details>
   <summary>คำใบ้</summary>
   ใช้ `Time::findTimes()` และ `runTime.setTime()`
   </details>

10. **Advanced**: สร้าง utility ที่:
    - รับ option `-time1 <t1>` และ `-time2 <t2>`
    - อ่าน field ที่สอง time steps
    - คำนวณค่าความต่าง (difference) ระหว่างสอง time steps
    - เขียน field ความต่างลงไฟล์ใหม่

    <details>
    <summary>คำใบ้</summary>
    ใช้ `runTime.setTime()` เปลี่ยน time และคำนวณ `field2 - field1`
    </details>

---

## 🧠 Concept Check

<details>
<summary><b>1. setRootCase.H ทำอะไร?</b></summary>

**Parse command line** และ **set case directory**

- อ่าน arguments จาก command line
- กำหนดตำแหน่ง case directory (folder ปัจจุบัน)
- สร้าง object: `argList args` สำหรับใช้ในโปรแกรม

**ทำไมสำคัญ?**
- เป็นจุดเริ่มต้นของทุก OpenFOAM utility
- อนุญาตให้ใช้ command line options
- กำหนด working directory สำหรับอ่านไฟล์
</details>

<details>
<summary><b>2. อ่าน scalar field ทำอย่างไร?</b></summary>

```cpp
volScalarField p
(
    IOobject
    (
        "p",                    // ชื่อ field
        runTime.timeName(),     // Time folder (เช่น 0, 100)
        mesh,                   // Mesh reference
        IOobject::MUST_READ,    // ต้องมีไฟล์
        IOobject::AUTO_WRITE    // เขียนอัตโนมัติถ้าแก้ไข
    ),
    mesh
);
```

**สำคัญ**: ต้องระบุชื่อ field, time, และ mesh reference

**ทำไมต้องใช้ IOobject?**
- ระบุตำแหน่งและวิธีการอ่าน/เขียนไฟล์
- กำหนดว่า field ถูกเขียนอัตโนมัติหรือไม่
- ระบุว่า field จำเป็นต้องมีหรือไม่
</details>

<details>
<summary><b>3. Design Patterns ที่ใช้บ่อยมีอะไรบ้าง?</b></summary>

**5 Patterns หลัก**:
1. **Time Loop**: `while (runTime.loop()) { ... }` - วนลูปตาม time steps
2. **Patch Loop**: `forAll(patches, patchi)` - วนลูปผ่าน boundary patches
3. **Cell Iteration**: `forAll(p, celli)` - วนลูปผ่าน cells
4. **Conditional**: `if (exists(...))` - เช็คว่ามีไฟล์/field หรือไม่
5. **Field Operations**: `volScalarField p2 = sqr(p)` - ประมวลผล field

**ทำสิ่งเหล่านี้ได้อย่างไร?**
- **Time Loop**: ใช้ `runTime.loop()` หรือ `Time::findTimes()` 
- **Patch Loop**: ใช้ `forAll(patches, patchi)` หรือ `mesh.boundary()`
- **Cell Iteration**: ใช้ `forAll(field, celli)` หรือ `mesh.nCells()`
- **Conditional**: ใช้ `exists()` หรือ `args.found()`
- **Field Operations**: ใช้ functions ที่มีใน OpenFOAM (sqr, sqrt, mag, etc.)
</details>

<details>
<summary><b>4. ทำไมต้องเข้าใจ Architecture ก่อนสร้าง Custom Utilities?</b></summary>

**เหตุผลหลัก**:
1. **อ่านโค้ดคนอื่นได้**: เข้าใจ utilities ที่มีอยู่แล้ว สามารถเรียนรู้จากมัน
2. **พัฒนาได้เร็ว**: ไม่ต้องคิดโครงสร้างใหม่ ใช้ patterns ที่มีอยู่
3. **Debug ง่าย**: รู้ว่า objects ถูกสร้างเมื่อไหร่ และใช้งานอย่างไร
4. **สื่อสารได้**: มีภาษาทางการร่วมกับผู้อื่นใน OpenFOAM community

**ตัวอย่าง**:
- ถ้ารู้ว่าทุก utility มี `setRootCase.H`, `createTime.H`, `createMesh.H` → สามารถเริ่มเขียนได้ทันที
- ถ้ารู้ว่า fields ใช้ IOobject → สามารถอ่าน/เขียน fields ได้อย่างถูกต้อง
- ถ้ารู้ Design Patterns → สามารถเลือกใช้ pattern ที่เหมาะสมกับงาน
</details>

<details>
<summary><b>5. argList ใช้ทำอะไรได้บ้าง?</b></summary>

**ความสามารถของ argList**:

1. **Parse command line**:
   ```cpp
   args.found("option")      // เช็คว่ามี option หรือไม่
   args.get<type>("option")  // อ่านค่า option
   ```

2. **Add custom options**:
   ```cpp
   args.addOption("name", "default", "description")
   ```

3. **Access case directory**:
   ```cpp
   args.rootPath()      // Root path
   args.caseName()      // Case name
   args.path()          // Full path
   ```

4. **Validate arguments**:
   ```cpp
   if (!args.found("required"))
   {
       FatalError << "Must specify -required" << exit(FatalError);
   }
   ```

**ทำไมสำคัญ?**
- ทำให้ utilities มีความยืดหยุ่น
- ผู้ใช้สามารถระบุ options ได้
- เป็นมาตรฐานใน OpenFOAM
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

### บทนี้เกี่ยวข้องกับ:
- **ภาพรวม:** [00_Overview.md](./00_Overview.md) — ภาพรวม Expert Utilities
- **Utility Categories:** [01_Utility_Categories_and_Organization.md](./01_Utility_Categories_and_Organization.md) — หมวดหมู่ Utilities
- **Essential Utilities:** [03_Essential_Utilities_for_Common_CFD_Tasks.md](./03_Essential_Utilities_for_Common_CFD_Tasks.md) — Utilities ที่ใช้บ่อย
- **Custom Utilities:** [05_Creating_Custom_Utilities.md](./05_Creating_Custom_Utilities.md) — สร้าง Utility เอง

### บทถัดไป:
- เรียนรู้ **Essential Utilities** ที่ใช้บ่อยในงาน CFD → [03_Essential_Utilities_for_Common_CFD_Tasks.md](./03_Essential_Utilities_for_Common_CFD_Tasks.md)
- เรียนรู้การ**สร้าง Custom Utilities** ตั้งแต่เริ่มต้น → [05_Creating_Custom_Utilities.md](./05_Creating_Custom_Utilities.md)

---

## 🎯 Key Takeaways (สรุปสิ่งสำคัญ)

### สิ่งที่ควรจำ:

1. **โครงสร้างมาตรฐาน**: ทุก OpenFOAM utility ใช้ skeleton เดียวกัน (fvCFD.H, setRootCase.H, createTime.H, createMesh.H)

2. **IOobject คือกุญแจ**: การอ่าน/เขียน fields ทุกครั้งต้องใช้ IOobject เพื่อระบุชื่อ, time, mesh, และ read/write options

3. **argList สำหรับ CLI**: ใช้ `args.addOption()` เพิ่ม options และ `args.found()/get()` อ่านค่า

4. **Design Patterns ที่ใช้บ่อย**:
   - Time Loop (`while (runTime.loop())`)
   - Patch Loop (`forAll(patches, patchi)`)
   - Cell Iteration (`forAll(field, celli)`)
   - Conditional (`if (exists(...))`)

5. **Field Operations**: OpenFOAM มี functions มากมายสำหรับ operations (sqr, sqrt, mag, max, min, average, etc.)

6. **Debugging**: ใช้ `Info<<`, `Warning`, และ `FatalError` พร้อมข้อความชัดเจน

### เชื่อมโยงกับบทอื่น:
- **บทที่ 1 (Categories)**: รู้จักหมวดหมู่ utilities → สามารถเลือกใช้ utility ที่เหมาะสม
- **บทที่ 3 (Essential Utilities)**: ใช้ความรู้เรื่อง architecture → อ่านและเข้าใจ utilities ที่มีอยู่
- **บทที่ 5 (Custom Utilities)**: ใช้ patterns ที่เรียน → สร้าง utilities ของตัวเองได้อย่างมีประสิทธิภาพ

---

> **พร้อมที่จะไปต่อ!** 
> ตอนนี้คุณเข้าใจโครงสร้างและ design patterns ของ OpenFOAM utilities แล้ว ไปดู **Essential Utilities** ที่ใช้บ่อยในงาน CFD ได้เลย → [03_Essential_Utilities_for_Common_CFD_Tasks.md](./03_Essential_Utilities_for_Common_CFD_Tasks.md)