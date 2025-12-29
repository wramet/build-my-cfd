# Architecture and Design Patterns

สถาปัตยกรรมและรูปแบบการออกแบบ Utilities

> **ลิงก์ที่เกี่ยวข้อง**:
> - ดูภาพรวม Expert Utilities → [00_Overview.md](./00_Overview.md)
> - ดู Utility Categories → [01_Utility_Categories_and_Organization.md](./01_Utility_Categories_and_Organization.md)
> - ดูการสร้าง Custom Utilities → [05_Creating_Custom_Utilities.md](./05_Creating_Custom_Utilities.md)

---

## 📋 บทนำ (Introduction)

Utilities ใน OpenFOAM ทั้งหมด **ใช้โครงสร้างและรูปแบบเดียวกัน** (Common Patterns) ซึ่งทำให้:
- อ่านโค้ดคนอื่นเข้าใจง่าย
- เขียน utility ใหม่ได้รวดเร็ว
- ดูแลรักษาโค้ดง่าย

ในบทนี้คุณจะได้เรียนรู้:
- **โครงสร้างมาตรฐาน** ของ OpenFOAM utility
- **การใช้ argList** สำหรับ command line arguments
- **การอ่าน/เขียน Fields** (volScalarField, volVectorField)
- **Design Patterns** ที่ใช้บ่อย
- **ตัวอย่าง Utility แบบเต็ม**

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

| Include | หน้าที่ | สร้าง Object |
|:--------|:---------|:-------------|
| **setRootCase.H** | Parse command line, set case directory | `args` |
| **createTime.H** | Create Time object (manage time) | `runTime` |
| **createMesh.H** | Create Mesh object | `mesh` |
| **createFields.H** | (Optional) Create custom fields | Custom fields |

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

---

## 🔧 2. Command Line Arguments (argList)

### 2.1 เพิ่ม Options

```cpp
// หลัง #include "setRootCase.H"

// เพิ่ม option: -patch <name>
args.addOption("patch", "patchName", "Patch to process");

// เพิ่ม option: -overwrite (no value)
args.addOption("overwrite", "Overwrite existing files");

// เพิ่ม option: -time <t> (default: latestTime)
args.addOption("time", "0", "Time to process");

// Parse (อัตโนมัติจาก setRootCase.H)
```

### 2.2 อ่านค่า Arguments

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
```

### 2.3 ตัวอย่างการใช้งาน

```bash
# รัน utility
myUtility -patch inlet -overwrite -time 100

# Output:
# Processing patch: inlet
# Will overwrite existing files
# Processing time: 100
```

---

## 📦 3. Field Access (การอ่าน/เขียน Fields)

### 3.1 อ่าน Fields ที่มีอยู่แล้ว

```cpp
// อ่าน scalar field (เช่น p, T)
volScalarField p
(
    IOobject
    (
        "p",                    // ชื่อ field
        runTime.timeName(),     // Time folder (เช่น 0, 100, 200)
        mesh,                   // Mesh reference
        IOobject::MUST_READ     // ต้องอ่าน (error ถ้าไม่เจอ)
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
        IOobject::MUST_READ
    ),
    mesh
);

Info<< "Max p: " << max(p).value() << endl;
Info<< "Max |U|: " << max(mag(U)).value() << endl;
```

### 3.2 สร้าง Fields ใหม่

```cpp
// สร้าง scalar field ใหม่ (เริ่มจาก 0)
volScalarField myField
(
    IOobject
    (
        "myField",              // ชื่อ field
        runTime.timeName(),
        mesh,
        IOobject::NO_READ       // ไม่ต้องอ่าน (สร้างใหม่)
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
        IOobject::NO_READ
    ),
    mesh,
    dimensionedVector("zero", dimVelocity, Zero)
);
```

### 3.3 เขียน Fields ลงไฟล์

```cpp
// เขียน field ทันที
myField.write();

// หรือเขียนหลาย fields
pSquared.write();
myField.write();
myVector.write();

// Output:
// --> 0/pSquared, 0/myField, 0/myVector
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
        FatalError << "Must specify -patch option" << endl;
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
            IOobject::MUST_READ
        ),
        mesh
    );

    // 5. Get patch reference
    label patchID = mesh.boundaryMesh().findPatchID(patchName);

    if (patchID == -1)
    {
        FatalError << "Patch " << patchName << " not found" << endl;
    }

    // 6. Calculate average on patch
    const fvPatchScalarField& pp = p.boundaryField()[patchID];
    scalar avgP = gAverage(pp);

    // 7. Output result
    Info<< "\nAverage pressure on " << patchName << ": " << avgP << " Pa\n" << endl;

    Info<< "\nEnd\n" << endl;
    return 0;
}
```

### 4.2 วิธี Compile

```bash
# สร้าง folder สำหรับ utility
mkdir -p $FOAM_RUN/applications/utilities/myUtility
cd $FOAM_RUN/applications/utilities/myUtility

# สร้างไฟล์:
# - myUtility.C (code ด้านบน)
# - Make/files
# - Make/options

# Make/files:
myUtility.C

EXE = $(FOAM_USER_APPBIN)/myUtility

# Make/options:
EXE_INC = \
    -I$(LIB_SRC)/finiteVolume/lnInclude \
    -I$(LIB_SRC)/meshTools/lnInclude

EXE_LIBS = \
    -lfiniteVolume \
    -lmeshTools

# Compile
wmake
```

---

## 🎨 5. Common Design Patterns

### 5.1 Pattern 1: Time Loop (วนลูปตามเวลา)

```cpp
#include "fvCFD.H"

int main(int argc, char *argv[])
{
    #include "setRootCase.H"
    #include "createTime.H"
    #include "createMesh.H"

    // อ่าน field
    volScalarField T(IOobject("T", runTime.timeName(), mesh, IOobject::MUST_READ), mesh);

    // วนลูปตาม time steps
    while (runTime.loop())
    {
        Info<< "Time = " << runTime.timeName() << endl;

        runTime++;

        // อ่าน field ใหม่ (ถ้ามีการ update)
        T = volScalarField(IOobject("T", runTime.timeName(), mesh, IOobject::MUST_READ), mesh);

        // ประมวลผล...
        scalar avgT = average(T).value();
        Info<< "Average T: " << avgT << endl;
    }

    return 0;
}
```

### 5.2 Pattern 2: Loop ผ่าน Patches

```cpp
// วนลูปผ่านทุก patches
const fvPatchList& patches = mesh.boundary();

forAll(patches, patchi)
{
    const fvPatch& patch = patches[patchi];

    Info<< "Patch " << patch.name()
        << " has " << patch.size() << " faces" << endl;

    // เข้าถึง field values บน patch
    const fvPatchScalarField& pp = p.boundaryField()[patchi];
    scalar patchAvg = gAverage(pp);

    Info<< "  Average p: " << patchAvg << endl;
}
```

### 5.3 Pattern 3: Cell Iteration (วนลูปผ่าน cells)

```cpp
// วนลูปผ่านทุก cells
forAll(p, celli)
{
    scalar cellP = p[celli];  // ค่า pressure ที่ cell i
    vector cellU = U[celli];  // ค่า velocity ที่ cell i

    // ประมวลผล...
    p[celli] = cellP * 1.1;  // เพิ่มค่า p ขึ้น 10%
}

// หรือใช้ iterator (สำหรับ operations ซับซ้อน)
for (int celli = 0; celli < mesh.nCells(); celli++)
{
    // ...
}
```

### 5.4 Pattern 4: Conditional Execution

```cpp
// เช็คว่า field มีอยู่หรือไม่
if (exists(runTime.timePath() / "myField"))
{
    volScalarField myField(IOobject("myField", runTime.timeName(), mesh, IOobject::MUST_READ), mesh);
    Info<< "Found myField" << endl;
}
else
{
    Info<< "myField not found, using default" << endl;
    volScalarField myField(IOobject("myField", runTime.timeName(), mesh, IOobject::NO_READ), mesh, dimensionedScalar("zero", dimless, Zero));
}
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

// ปรับ scale
p *= 1.1;  // เพิ่ม 10%
p += 100;  // บวก 100

// Operations
volScalarField pSquared = sqr(p);      // p²
volScalarField pSqrt = sqrt(p);        // √p (ต้องไม่ติดลบ)
volScalarField magP = mag(p);          // |p|
```

### 6.2 Vector Fields (เช่น U)

```cpp
volVectorField U(...);

// Magnitude (ขนาด)
volScalarField magU = mag(U);  // |U| = sqrt(Ux² + Uy² + Uz²)

// ค่าสูงสุด/ต่ำสุด
scalar maxU = max(magU).value();

// Components
volScalarField Ux = U.component(0);  // U.x
volScalarField Uy = U.component(1);  // U.y
volScalarField Uz = U.component(2);  // U.z

// Vector operations
volVectorField Unew = U * 1.1;       // Scale
volVectorField V = U + vector(1, 0, 0);  // Add vector
```

### 6.3 Tensor Fields (เช่น Stress tensor)

```cpp
volSymmTensorField sigma(...);  // Symmetric tensor

// Components
volScalarField sigmaxx = sigma.component(0);  // xx
volScalarField sigmaxy = sigma.component(1);  // xy
volScalarField sigmaxz = sigma.component(2);  // xz

// Trace (sum of diagonal)
volScalarField tr = tr(sigma);
```

---

## 🛠️ 7. Debugging Tips

### 7.1 แสดงผลข้อมูล

```cpp
// แสดงผลลัพธ์
Info<< "Number of cells: " << mesh.nCells() << endl;
Info<< "Number of patches: " << mesh.boundary().size() << endl;
Info<< "Time range: " << runTime.startTime().value()
    << " to " << runTime.endTime().value() << endl;

// แสดงค่า field
Info<< "p range: " << min(p).value() << " to " << max(p).value() << endl;
```

### 7.2 เช็ค Errors

```cpp
// เช็คว่า patch มีอยู่จริง
label patchID = mesh.boundaryMesh().findPatchID(patchName);
if (patchID == -1)
{
    FatalError << "Patch " << patchName << " not found" << endl;
}

// เช็คว่า field มีอยู่
if (!exists(runTime.timePath() / "myField"))
{
    Warning << "myField not found" << endl;
}
```

---

## 📋 Quick Reference

### 8.1 Includes ที่ใช้บ่อย

| Include | Object ที่สร้าง | ใช้ทำอะไร |
|:--------|:-----------------|:------------|
| **setRootCase.H** | `args` | Parse command line |
| **createTime.H** | `runTime` | Manage time |
| **createMesh.H** | `mesh` | Mesh access |
| **createFields.H** | (Custom) | Custom fields |

### 8.2 Field IOobject Options

| Option | ความหมาย |
|:-------|:-----------|
| `IOobject::MUST_READ` | ต้องอ่าน (error ถ้าไม่เจอ) |
| `IOobject::READ_IF_PRESENT` | อ่านถ้ามี (ไม่ error ถ้าไม่เจอ) |
| `IOobject::NO_READ` | ไม่อ่าน (สร้างใหม่) |
| `IOobject::AUTO_WRITE` | เขียนอัตโนมัติ |
| `IOobject::NO_WRITE` | ไม่เขียน |

### 8.3 Common Operations

| Operation | Code |
|:----------|:-----|
| **Max/Min/Avg** | `max(field).value()`, `min(field).value()`, `average(field).value()` |
| **Sum** | `sum(field).value()` |
| **Magnitude** | `mag(vectorField)` |
| **Squared** | `sqr(field)` |
| **Sqrt** | `sqrt(field)` |

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

### ระดับปานกลาง (Medium)
3. **อธิบาย**: แตกต่างระหว่าง `IOobject::MUST_READ` และ `IOobject::READ_IF_PRESENT` คืออะไร?
   <details>
   <summary>คำตอบ</summary>
   - **MUST_READ**: ต้องอ่าน field นั้น (FatalError ถ้าไม่เจอ)
   - **READ_IF_PRESENT**: อ่านถ้ามี (ไม่ error ถ้าไม่เจอ)
   </details>

4. **เขียนโค้ด**: จงเขียน code อ่าน field `T` และคำนวณค่าเฉลี่ย
   <details>
   <summary>คำตอบ</summary>
   ```cpp
   volScalarField T(IOobject("T", runTime.timeName(), mesh, IOobject::MUST_READ), mesh);
   scalar avgT = average(T).value();
   Info<< "Average T: " << avgT << endl;
   ```
   </details>

### ระดับสูง (Hard)
5. **Hands-on**: สร้าง utility ที่:
   - รับ option `-field <name>` (ชื่อ field ที่ต้องการ)
   - รับ option `-patch <name>` (ชื่อ patch)
   - คำนวณค่าเฉลี่ยของ field บน patch นั้น

6. **Project**: สร้าง utility ที่:
   - วนลูปผ่านทุก time steps
   - คำนวณค่า max/min ของ field `U`
   - เขียนผลลัพธ์ไปยังไฟล์ `Ustats.dat`

---

## 🧠 Concept Check

<details>
<summary><b>1. setRootCase.H ทำอะไร?</b></summary>

**Parse command line** และ **set case directory**

- อ่าน arguments จาก command line
- กำหนดตำแหน่ง case directory (folder ปัจจุบัน)
- สร้าง object: `argList args` สำหรับใช้ในโปรแกรม
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
        IOobject::MUST_READ     // ต้องมีไฟล์
    ),
    mesh
);
```

**สำคัญ**: ต้องระบุชื่อ field, time, และ mesh reference
</details>

<details>
<summary><b>3. Design Patterns ที่ใช้บ่อยมีอะไรบ้าง?</b></summary>

**4 Patterns หลัก**:
1. **Time Loop**: `while (runTime.loop()) { ... }` - วนลูปตาม time steps
2. **Patch Loop**: `forAll(patches, patchi)` - วนลูปผ่าน boundary patches
3. **Cell Iteration**: `forAll(p, celli)` - วนลูปผ่าน cells
4. **Conditional**: `if (exists(...))` - เช็คว่ามีไฟล์/field หรือไม่
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md) — ภาพรวม Expert Utilities
- **Utility Categories:** [01_Utility_Categories_and_Organization.md](01_Utility_Categories_and_Organization.md) — หมวดหมู่ Utilities
- **Essential Utilities:** [03_Essential_Utilities_for_Common_CFD_Tasks.md](03_Essential_Utilities_for_Common_CFD_Tasks.md) — Utilities ที่ใช้บ่อย
- **Custom Utilities:** [05_Creating_Custom_Utilities.md](05_Creating_Custom_Utilities.md) — สร้าง Utility เอง