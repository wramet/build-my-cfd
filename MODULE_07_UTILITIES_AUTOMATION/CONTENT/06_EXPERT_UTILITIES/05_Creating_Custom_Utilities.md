# Creating Custom Utilities

การสร้าง Utility ของตัวเอง

---

## Learning Objectives

เมื่ออ่านจบบทนี้ คุณจะสามารถ:
- **อธิบาย** โครงสร้างพื้นฐานของ OpenFOAM utility และบทบาทของแต่ละไฟล์
- **สร้าง** custom utility ใหม่ตั้งแต่เริ่มต้นโดยใช้เทมเพลตมาตรฐาน
- **เขียน**โค้ด C++ ที่เข้าถึง mesh, fields, และข้อมูลกรณีของ OpenFOAM
- **รวบรวม (compile)** และ debug utility ด้วย `wmake`
- **แก้ไขปัญหา** ข้อผิดพลาดการรวมรวมที่พบบ่อย
- **ทดสอบ** utility กับกรณีตัวอย่างและตรวจสอบผลลัพธ์
- **ประยุกต์ใช้** utilities อย่างมีประสิทธิภาพสำหรับ automation และ post-processing

---

## 🎯 What: What is a Custom Utility?

**Custom utility** ใน OpenFOAM คือโปรแกรมแบบ standalone (ทำงานได้ด้วยตัวเอง) ที่คุณเขียนขึ้นเพื่อทำงาเฉพาะที่ไม่มีใน utilities มาตรฐาน มันเป็นเครื่องมืออเนกประสงค์ที่ช่วยให้คุณสามารถ:

- อ่านและประมวลผลข้อมูล OpenFOAM (mesh, fields, boundary conditions)
- ทำการคำนวณเฉพาะทาง (ตัวอย่าง: คำนวณค่า coefficients พิเศษ)
- สร้าง post-processing pipelines แบบอัตโนมัติ
- แปลงข้อมูลระหว่างรูปแบบต่าง ๆ
- สร้าง reports และ statistics อัตโนมัติ

### ความแตกต่างระหว่าง Utilities กับ Solvers

| แง่มุม | Utilities | Solvers |
|---------|-----------|---------|
| **วัตถุประสงค์** | Post-processing, data extraction, manipulation | แก้สมการกาภาค (PDEs) ตามเวลา |
| **โครงสร้าง** | อ่านข้อมูล → ประมวลผล → เขียนผลลัพธ์ | Time loop → แก้สมการ → บันทึก |
| **ตัวอย่าง** | `patchIntegrate`, `sample`, `foamListTimes` | `simpleFoam`, `interFoam` |
| **ความซับซ้อน** | ปานกลาง (ไม่มี time loop) | สูง (มี time stepping, solvers) |

### ตัวอย่าง Utilities ที่มีประโยชน์

1. **Validation utilities:** ตรวจสอบคุณภาพ mesh หรือ fields
2. **Data extraction:** ดึงข้อมูลบางส่วนออกมาวิเคราะห์
3. **Format conversion:** แปลงข้อมูลเป็น CSV, JSON, หรือรูปแบบอื่น
4. **Automation tools:** ทำงานซ้ำ ๆ อัตโนมัติ (batch post-processing)
5. **Custom calculations:** คำนวณปริมาณที่ไม่มีใน utilities มาตรฐาน

---

## 🤔 Why: Create Your Own Utilities?

### เหตุผลที่ควรสร้าง Custom Utilities

| เหตุผล | คำอธิบาย | ตัวอย่าง |
|---------|-----------|---------|
| **Automation** | ลดงานซ้ำที่ต้องทำ manual | สร้าง force report อัตโนมัติจากหลายกรณี |
| **Custom Analysis** | คำนวณปริมาณเฉพาะทาง | คำนวณ thermal efficiency factor ที่ซับซ้อน |
| **Workflow Integration** | เชื่อมโยงขั้นตอนการทำงาน | รวมข้อมูลจากหลาย source เป็น dashboard |
| **Debugging** | ตรวจสอบข้อมูลระหว่างคำนวณ | ตรวจสอบ field bounds หรือ conservation |
| **Reproducibility** | ทำให้การวิเคราะห์สามารถทำซ้ำได้ | Standardized post-processing pipeline |
| **Performance** | ทำงานที่เร็วกว่า manual | ประมวลผลข้อมูลจำนวนมากในเวลาสั้น |

### Use Cases ที่พบบ่อย

- **Research:** คำนวณ dimensionless numbers พิเศษสำหรับ paper
- **Industry:** สร้าง automated reports สำหรับลูกค้า
- **Validation:** เปรียบเทียบ results กับ experimental data
- **Optimization:** สร้าง objective functions สำหรับ parametric studies
- **Data Export:** แปลง OpenFOAM data เป็นรูปแบบที่ tools อื่นรับได้

---

## 🛠️ How: Building Custom Utilities

### Phase 1: Planning Your Utility

ก่อนเริ่มเขียนโค้ด ให้ตอบคำถามเหล่านี้:

| คำถาม | ตัวอย่างคำตอบ |
|--------|-----------------|
| **Input** คืออะไร? | Case directory, time directories, specific fields |
| **Output** คืออะไร? | File (CSV/JSON), terminal output, new fields |
| **Processing** ต้องทำอะไร? | คำนวณ integral บน patch, สรุป statistics |
| **Dependencies** ต้องการอะไร? | finiteVolume, meshTools, specific function objects |

### Phase 2: Directory Structure

```
myUtility/
├── Make/
│   ├── files          # Source files and target executable
│   └── options        # Compiler flags and libraries
└── myUtility.C        # Main source code
```

**แต่ละไฟล์มีหน้าที่:**
- **Make/files:** ระบุ source files และชื่อ executable
- **Make/options:** ระบุ include paths และ libraries ที่ต้องใช้
- **myUtility.C:** โค้ดหลักของ utility

### Phase 3: Creating Make/files

```make
myUtility.C

EXE =1$(FOAM_USER_APPBIN)/myUtility
```

**อธิบาย:**
- บรรทัดแรก: ระบุ source file(s) ที่ต้องรวมรวม (หลายไฟล์ก็ได้)
- `EXE`: ระบุ path ของ executable ที่จะสร้าง
  - `$(FOAM_USER_APPBIN)`: เขียนใน user's bin directory (แนะนำ)
  - `$(FOAM_APPBIN)`: เขียนใน system-wide bin (ต้องการ sudo)

**ตัวอย่างหลาย source files:**
```make
myUtility.C
helperFunctions.C
dataProcessor.C

EXE =1$(FOAM_USER_APPBIN)/myUtility
```

### Phase 4: Creating Make/options

```make
EXE_INC = \
    -I$(LIB_SRC)/finiteVolume/lnInclude \
    -I$(LIB_SRC)/meshTools/lnInclude

EXE_LIBS = \
    -lfiniteVolume \
    -lmeshTools
```

**อธิบาย:**
- `EXE_INC`: Include paths (header files)
  - `$(LIB_SRC)/finiteVolume/lnInclude`: finiteVolume headers
  - เพิ่ม libraries อื่นตามที่ต้องการ
- `EXE_LIBS`: Libraries ที่ต้อง link
  - `-lfiniteVolume`: link finiteVolume library
  - libraries อื่น: `-lmeshTools`, `-lsampling`, `-lfileFormats`, etc.

**Libraries ที่ใช้บ่อย:**
```make
# Basic mesh and field access
-lfiniteVolume

# Advanced mesh operations
-lmeshTools

# Sampling and probing
-lsampling

# File I/O (CSV, JSON, etc.)
-lfileFormats

# Thermophysical models
-lfluidThermophysicalModels

# Turbulence models
-lturbulenceModels
```

### Phase 5: Writing Source Code

#### 5.1 Basic Template

```cpp
#include "fvCFD.H"

int main(int argc, char *argv[])
{
    // 1. Initialize OpenFOAM environment
    #include "setRootCase.H"
    #include "createTime.H"
    #include "createMesh.H"

    // 2. Your processing code here
    Info << "Mesh statistics:" << endl;
    Info << "  Cells: " << mesh.nCells() << endl;
    Info << "  Faces: " << mesh.nFaces() << endl;
    Info << "  Points: " << mesh.nPoints() << endl;

    // 3. Exit successfully
    return 0;
}
```

**อธิบายแต่ละส่วน:**

1. **`#include "fvCFD.H"`**: Header หลักที่รวม headers พื้นฐานทั้งหมด
   - `fvMesh`, `Time`, `argList`, และอื่น ๆ

2. **`setRootCase.H`**: อ่าน command-line arguments
   - ตั้งค่า `rootCase` และ `caseDir`

3. **`createTime.H`**: สร้าง time object
   - ใช้อ่าน time directories และ controlDict

4. **`createMesh.H`**: สร้าง mesh object
   - อ่าน mesh จาก `constant/polyMesh`

#### 5.2 Complete Example: Patch Force Calculator

```cpp
#include "fvCFD.H"
#include "surfaceFields.H"

int main(int argc, char *argv[])
{
    #include "setRootCase.H"
    #include "createTime.H"
    #include "createMesh.H"

    // 1. Read pressure and velocity fields
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

    volVectorField U
    (
        IOobject
        (
            "U",
            runTime.timeName(),
            mesh,
            IOobject::MUST_READ,
            IOobject::NO_WRITE
        ),
        mesh
    );

    // 2. Calculate forces on all patches
    const volVectorField::Boundary& pBf = p.boundaryField();
    const volVectorField::Boundary& UBf = U.boundaryField();
    const surfaceVectorField::Boundary& SfBf = mesh.Sf().boundaryField();

    Info << "\nForces on patches:" << nl << endl;

    forAll(mesh.boundary(), patchi)
    {
        const fvPatch& patch = mesh.boundary()[patchi];
        
        // Skip empty and processor patches
        if (patch.size() == 0 || isA<processorFvPatch>(patch))
        {
            continue;
        }

        vector forceSum = vector::zero;
        scalar pressureForce = 0;
        scalar viscousForce = 0;

        // Sum forces over patch faces
        forAll(patch, facei)
        {
            // Pressure force: p * Sf
            vector fP = pBf[patchi][facei] * SfBf[patchi][facei];
            
            // Viscous force (simplified): mu * grad(U) * Sf
            // Note: Full viscous force requires stress tensor calculation
            vector fV = vector::zero;

            forceSum += fP + fV;
            pressureForce += mag(fP);
            viscousForce += mag(fV);
        }

        // Output results
        Info << patch.name() << ":" << nl
             << "  Force: " << forceSum << nl
             << "  Pressure force magnitude: " << pressureForce << nl
             << "  Viscous force magnitude: " << viscousForce << nl
             << endl;
    }

    Info << "\nEnd\n" << endl;

    return 0;
}
```

**อธิบาย:**
- อ่าน fields `p` และ `U` จากระยะเวลาปัจจุบัน
- คำนวณ forces บนทุก patches โดย integrate pressure × area
- ข้าม processor patches (สำหรับ parallel runs)
- Output forces และ magnitudes ไปที่ terminal

#### 5.3 Advanced Example: Time Series Exporter

```cpp
#include "fvCFD.H"
#include "OFstream.H"

int main(int argc, char *argv[])
{
    #include "setRootCase.H"
    #include "createTime.H"
    #include "createMesh.H"

    // 1. Get patch name from arguments
    word patchName = "movingWall";  // Default
    if (argc > 2)
    {
        patchName = argv[2];
    }

    // 2. Open output file
    OFstream outputFile("patchData_" + patchName + ".csv");
    outputFile << "# Time,Area,AvgPressure,AvgVelocity,ForceX,ForceY,ForceZ" << nl;

    // 3. Loop over all time directories
    while (runTime.loop())
    {
        Info << "Time = " << runTime.timeName() << endl;

        // Read fields
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

        volVectorField U
        (
            IOobject
            (
                "U",
                runTime.timeName(),
                mesh,
                IOobject::MUST_READ,
                IOobject::NO_WRITE
            ),
            mesh
        );

        // Get patch
        label patchi = mesh.boundaryMesh().findPatchID(patchName);
        
        if (patchi == -1)
        {
            Warning << "Patch " << patchName << " not found" << endl;
            continue;
        }

        const fvPatch& patch = mesh.boundary()[patchi];
        const surfaceVectorField::Boundary& SfBf = mesh.Sf().boundaryField();

        // Calculate patch statistics
        scalar patchArea = 0;
        scalar avgP = 0;
        vector avgU = vector::zero;
        vector forceSum = vector::zero;

        forAll(patch, facei)
        {
            scalar faceArea = mag(SfBf[patchi][facei]);
            patchArea += faceArea;
            avgP += p.boundaryField()[patchi][facei] * faceArea;
            avgU += U.boundaryField()[patchi][facei] * faceArea;
            forceSum += p.boundaryField()[patchi][facei] * SfBf[patchi][facei];
        }

        // Normalize by area
        if (patchArea > SMALL)
        {
            avgP /= patchArea;
            avgU /= patchArea;
        }

        // Write to CSV
        outputFile << runTime.value() << ","
                   << patchArea << ","
                   << avgP << ","
                   << avgU.x() << "," << avgU.y() << "," << avgU.z() << ","
                   << forceSum.x() << "," << forceSum.y() << "," << forceSum.z()
                   << nl;
    }

    Info << "\nData exported to patchData_" << patchName << ".csv" << endl;

    return 0;
}
```

**คุณสมบัติ:**
- Loop ผ่านทุก time directories
- Export ข้อมูลไป CSV file
- รองรับ custom patch name ผ่าน command line
- คำนวณ statistics: area, average pressure/velocity, forces
- พร้อมใช้กับ plotting tools (Excel, Python, MATLAB)

### Phase 6: Compiling

```bash
wmake
```

**wmake process:**
1. อ่าน `Make/files` เพื่อระบุ sources
2. อ่าน `Make/options` สำหรับ includes/libraries
3. สร้าง dependency graph
4. Compile object files (`.o`)
5. Link เป็น executable
6. Install ไปยัง `$(FOAM_USER_APPBIN)`

**Output:**
```
Making dependency list for source file myUtility.C
SOURCE=myUtility.C ;  g++ -m64 -Dlinux64 -Wall -Wextra -Wno-unused-parameter -Wold-style-cast -Wnon-virtual-dtor -O3  -DNoRepository -ftemplate-depth-100 -I/usr/local/OpenFOAM/OpenFOAM-8/src/finiteVolume/lnInclude -I/usr/local/OpenFOAM/OpenFOAM-8/src/meshTools/lnInclude -IlnInclude -I. -I/usr/local/OpenFOAM/ThirdParty-8/platforms/linux64Gcc/gmp/6.1.2/include -I/usr/local/OpenFOAM/ThirdParty-8/platforms/linux64Gcc/mpfr/3.1.3/include -I/usr/local/OpenFOAM/ThirdParty-8/platforms/linux64Gcc/MPFR/3.1.3 -I/usr/local/OpenFOAM/OpenFOAM-8/src/OpenFOAM/lnInclude -I/usr/local/OpenFOAM/OpenFOAM-8/src/OSspecific/POSIX/lnInclude   -c myUtility.C -o Make/linux64GccDPInt32Opt/myUtility.o
g++ -m64 -Dlinux64 -Wall -Wextra -Wno-unused-parameter -Wold-style-cast -Wnon-virtual-dtor -O3  -DNoRepository -ftemplate-depth-100 -I/usr/local/OpenFOAM/OpenFOAM-8/src/finiteVolume/lnInclude -I/usr/local/OpenFOAM/OpenFOAM-8/src/meshTools/lnInclude -IlnInclude -I. -I/usr/local/OpenFOAM/ThirdParty-8/platforms/linux64Gcc/gmp/6.1.2/include -I/usr/local/OpenFOAM/ThirdParty-8/platforms/linux64Gcc/mpfr/3.1.3/include -I/usr/local/OpenFOAM/ThirdParty-8/platforms/linux64Gcc/MPFR/3.1.3 -I/usr/local/OpenFOAM/OpenFOAM-8/src/OpenFOAM/lnInclude -I/usr/local/OpenFOAM/OpenFOAM-8/src/OSspecific/POSIX/lnInclude   -Xlinker --add-needed -Xlinker --no-as-needed Make/linux64GccDPInt32Opt/myUtility.o -L/usr/local/OpenFOAM/OpenFOAM-8/platforms/linux64GccDPInt32Opt/lib \    -lfiniteVolume -lmeshTools -lOpenFOAM -ldl  -lm -o /home/user/OpenFOAM/user-8/platforms/linux64GccDPInt32Opt/bin/myUtility
```

### Phase 7: Testing Your Utility

#### 7.1 Basic Test

```bash
# Navigate to a test case
cd ~/OpenFOAM/user-8/run/tutorials/incompressible/simpleFoam/pitzDaily

# Run your utility
myUtility

# Expected output:
# Mesh statistics:
#   Cells: 24382
#   Faces: 48674
#   Points: 24437
```

#### 7.2 Testing with Arguments

```bash
# If utility accepts patch name argument
myUtility inlet
```

#### 7.3 Validation Checklist

- [ ] Utility compiles without warnings
- [ ] Runs successfully on test case
- [ ] Produces expected output format
- [ ] Handles missing fields gracefully
- [ ] Works with parallel cases (decomposed domains)
- [ ] Performance acceptable (fast enough)

---

## 🔧 Troubleshooting Common Issues

### Issue 1: Compilation Errors

| Error | สาเหตุ | วิธีแก้ |
|-------|--------|---------|
| `error: 'fvCFD.H' file not found` | Header path ไม่ถูกต้อง | ตรวจสอบ `EXE_INC` in Make/options |
| `undefined reference to ' Foam::...'` | Library ไม่ได้ถูก link | เพิ่ม library ใน `EXE_LIBS` |
| `error: 'mesh' was not declared` | ลืม include createMesh.H | เพิ่ม `#include "createMesh.H"` |
| `fatal error: ... Permission denied` | ไม่มี permission เขียนใน system directory | ใช้ `$(FOAM_USER_APPBIN)` แทน `$(FOAM_APPBIN)` |

### Issue 2: Runtime Errors

| Error | สาเหตุ | วิธีแก้ |
|-------|--------|---------|
| `Cannot find file "file"` | Field หรือ file ไม่มี | ตรวจสอบว่า field มีอยู่จริงใน time directory |
| `patchID not found` | Patch name ผิด | ใช้ `boundary` utility เพื่อดู patch names ที่ถูกต้อง |
| `Attempt to read past EOF` | File corrupted หรือ incomplete | Re-run solver เพื่อสร้าง fields ใหม่ |
| `Segmentation fault` | Memory access error | ตรวจสอบ array bounds, null pointers |

### Issue 3: Wmake Issues

```bash
# Clean build artifacts
wclean

# Rebuild
wmake

# Force rebuild (ignore dependencies)
WM_NCOMPROCS=1 wmake -s
```

---

## 🧪 Testing Strategies

### Unit Testing Approach

```cpp
// Add assertions to verify results
#include "cassert.H"

// In your code:
scalar calculatedValue = /* ... */;
scalar expectedValue = /* ... */;

if (mag(calculatedValue - expectedValue) > SMALL)
{
    FatalError << "Test failed: expected " << expectedValue 
               << ", got " << calculatedValue << exit(FatalError);
}
```

### Validation Against Known Utilities

```bash
# Compare with standard utility
patchIntegrate p inlet > standard_output.txt
myUtility inlet > custom_output.txt

# Compare results
diff standard_output.txt custom_output.txt
```

### Performance Testing

```bash
# Time your utility
time myUtility

# Profile with valgrind (for deep optimization)
valgrind --tool=callgrind myUtility
```

---

## 📚 Code Examples Library

### Example 1: Simple Field Statistics

```cpp
#include "fvCFD.H"

int main(int argc, char *argv[])
{
    #include "setRootCase.H"
    #include "createTime.H"
    #include "createMesh.H"

    // Read field
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

    // Calculate statistics
    scalar TMin = gMin(T);
    scalar TMax = gMax(T);
    scalar TAvg = gAverage(T);

    Info << "Field T statistics:" << nl
         << "  Min: " << TMin << nl
         << "  Max: " << TMax << nl
         << "  Avg: " << TAvg << endl;

    return 0;
}
```

### Example 2: Mesh Quality Checker

```cpp
#include "fvCFD.H"
#include "meshTools.H"

int main(int argc, char *argv[])
{
    #include "setRootCase.H"
    #include "createTime.H"
    #include "createMesh.H"

    // Check non-orthogonality
    scalar maxNonOrtho = 0;
    scalar avgNonOrtho = 0;

    forAll(mesh.faceOwner(), facei)
    {
        vector nf = mesh.faceAreas()[facei];
        nf /= mag(nf);

        vector d = mesh.cellCentres()[mesh.faceOwner()[facei]] 
                 - mesh.faceCentres()[facei];

        scalar nonOrtho = mag(nf & (d/mag(d)));
        maxNonOrtho = max(maxNonOrtho, nonOrtho);
        avgNonOrtho += nonOrtho;
    }

    avgNonOrtho /= mesh.nFaces();

    Info << "Mesh quality:" << nl
         << "  Max non-orthogonality: " << maxNonOrtho << nl
         << "  Avg non-orthogonality: " << avgNonOrtho << endl;

    if (maxNonOrtho > 0.7)
    {
        Warning << "High non-orthogonality detected!" << endl;
    }

    return 0;
}
```

### Example 3: Multi-Field Exporter

```cpp
#include "fvCFD.H"
#include "OFstream.H"

int main(int argc, char *argv[])
{
    #include "setRootCase.H"
    #include "createTime.H"
    #include "createMesh.H"

    // Export cell center positions and multiple fields
    OFstream outputFile("cellData.csv");
    outputFile << "# X,Y,Z,p,Ux,Uy,Uz,T" << nl;

    // Read fields
    volScalarField p(IOobject("p", runTime.timeName(), mesh, IOobject::MUST_READ, IOobject::NO_WRITE), mesh);
    volVectorField U(IOobject("U", runTime.timeName(), mesh, IOobject::MUST_READ, IOobject::NO_WRITE), mesh);
    volScalarField T(IOobject("T", runTime.timeName(), mesh, IOobject::MUST_READ, IOobject::NO_WRITE), mesh);

    // Write data
    forAll(mesh.C(), celli)
    {
        outputFile << mesh.C()[celli].x() << ","
                   << mesh.C()[celli].y() << ","
                   << mesh.C()[celli].z() << ","
                   << p[celli] << ","
                   << U[celli].x() << "," << U[celli].y() << "," << U[celli].z() << ","
                   << T[celli] << nl;
    }

    Info << "Exported " << mesh.nCells() << " cells to cellData.csv" << endl;

    return 0;
}
```

---

## 🎓 Best Practices

### 1. Code Organization

```cpp
// Use separate files for complex utilities
// myUtility.C - main function
// helper.H - inline helper functions
// helper.C - helper function implementations
// calculations.H - calculation routines
```

### 2. Error Handling

```cpp
// Always check for errors
if (!fieldHeader.typeHeaderOk<volScalarField>(true))
{
    FatalError << "Cannot read field p at time " << runTime.timeName()
               << exit(FatalError);
}

// Use try-catch for critical sections
try
{
    // Critical code
}
catch (const std::exception& e)
{
    FatalError << "Error: " << e.what() << exit(FatalError);
}
```

### 3. Memory Management

```cpp
// Use smart pointers where appropriate
autoPtr<volScalarField> customFieldPtr;

// Let OpenFOAM manage memory
// Avoid manual new/delete
```

### 4. Documentation

```cpp
// Always add comments
// Calculate pressure force on patch
// F_p = ∫_patch p * dS
vector pressureForce = sum(p * patch.Sf());

// Document complex formulas
// Wall y+ calculation:
// y+ = rho * u_tau * y / mu
// where u_tau = sqrt(tau_w / rho)
scalar yPlus = /* ... */;
```

---

## 🚀 Advanced Topics

### Function Objects vs Utilities

**เมื่อไหร่ควรใช้อะไร:**

| ใช้ Function Objects เมื่อ | ใช้ Utilities เมื่อ |
|-------------------------|---------------------|
| ต้องการคำนวณระหว่าง simulation | ต้องการ post-processing หลังจบ |
| ต้องการ output ทุก time step | ต้องการ batch process |
| ต้องการ integration กับ solver | ต้องการ flexibility สูง |
| ต้องการใช้ controlDict | ต้องการ command-line tool |

### Parallel Execution

```bash
# For utilities that work on decomposed cases
mpirun -np 4 myUtility -parallel

# In code, check for parallel run
if (Pstream::parRun())
{
    Info << "Running in parallel with " << Pstream::nProcs() << " processes" << endl;
}
```

### Integration with Python

```cpp
// Use Python script to call utility
// system("python analysis.py");

// Or output JSON for Python processing
// OFstream jsonFile("output.json");
// jsonFile << "{\n";
// jsonFile << "  \"force\": [" << force.x() << ", " << force.y() << ", " << force.z() << "]\n";
// jsonFile << "}\n";
```

---

## ✅ Key Takeaways

### Core Concepts

- **Utilities** vs Solvers: Utilities ทำ post-processing และ data extraction, solvers แก้ PDEs
- **Directory structure:** `Make/files`, `Make/options`, และ source code เป็นส่วนสำคัญ
- **Compilation:** ใช้ `wmake` ซึ่งอ่าน configuration จาก `Make/` directory

### Practical Skills

- **สร้าง utility** จาก template: สร้าง directory, Make files, และ source code
- **เขียนโค้ด** ที่อ่าน mesh และ fields: ใช้ `fvCFD.H` และ standard includes
- **Compile** utilities: `wmake` ใน utility directory
- **Debug** compilation errors: ตรวจสอบ includes, libraries, syntax
- **Test** utilities: ใช้ test cases และ validation strategies

### Quality Checklist

- [ ] ใช้ proper directory structure
- [ ] Make/files มี source files และ EXE target
- [ ] Make/options มี correct includes และ libraries
- [ ] Source code มี error handling
- [ ] Utility compiles ไม่มี warnings
- [ ] Test กับ known cases
- [ ] Document การใช้งานและข้อจำกัด

### Next Steps

- **ฝึกเพิ่ม:** สร้าง utilities สำหรับ workflows ของคุณเอง
- **Learn from examples:** ตรวจสอบ source code ของ utilities มาตรฐานใน `$FOAM_UTILITIES`
- **Advanced features:** สำรวจ function objects, parallel processing, และ Python integration
- **Contribute:** พิจารณา contribute utilities ที่มีประโยชน์กลับไปที่ community

---

## 📖 Related Documentation

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **ตัวอย่าง Utilities:** [03_Essential_Utilities_for_Common_CFD_Tasks.md](03_Essential_Utilities_for_Common_CFD_Tasks.md)
- **Design Patterns:** [02_Architecture_and_Design_Patterns.md](02_Architecture_and_Design_Patterns.md)
- **Testing:** [05_Testing_and_QA.md](../05_PROFESSIONAL_PRACTICE/05_Testing_and_QA.md)

---

## 🧠 Concept Check

<details>
<summary><b>1. ข้อใดคือความแตกต่างหลักระหว่าง utilities กับ solvers?</b></summary>

**Utilities:** ใช้สำหรับ post-processing, data extraction, และ manipulation โดยไม่มี time loop
**Solvers:** ใช้สำหรับแก้ PDEs ตามเวลาด้วย time stepping และ numerical schemes

Utilities อ่านข้อมูล → ประมวลผล → เขียนผลลัพธ์
Solvers วน loop เวลา → แก้สมการ → บันทึก results
</details>

<details>
<summary><b>2. ไฟล์ใดใน directory structure ของ utility ที่ระบุ source files และ executable target?</b></summary>

**Make/files**

มีหน้าที่ระบุ:
- Source files (`.C`, `.H`) ที่ต้องรวมรวม
- Target executable ผ่าน `EXE =1$(FOAM_USER_APPBIN)/utilityName`

ตัวอย่าง:
```make
myUtility.C
helper.C

EXE =1$(FOAM_USER_APPBIN)/myUtility
```
</details>

<details>
<summary><b>3. จงอธิบายการทำงานของ wmake ใน 3 ขั้นตอนหลัก</b></summary>

1. **Read configuration:** wmake อ่าน `Make/files` (sources, target) และ `Make/options` (includes, libraries)
2. **Compile:** สร้าง object files (`.o`) จาก source files โดยใช้ compiler flags ที่ระบุ
3. **Link:** Link object files กับ libraries ที่ระบุ และสร้าง executable ใน target directory

ผลลัพธ์: executable ถูกสร้างใน `$FOAM_USER_APPBIN/` (หรือ `$FOAM_APPBIN/`)
</details>

<details>
<summary><b>4. จงเขียน template code ขั้นต่ำสำหรับ utility ที่อ่าน field ชื่อ 'T' และแสดงค่า min, max, average</b></summary>

```cpp
#include "fvCFD.H"

int main(int argc, char *argv[])
{
    #include "setRootCase.H"
    #include "createTime.H"
    #include "createMesh.H"

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

    scalar TMin = gMin(T);
    scalar TMax = gMax(T);
    scalar TAvg = gAverage(T);

    Info << "T: Min=" << TMin << ", Max=" << TMax << ", Avg=" << TAvg << endl;

    return 0;
}
```
</details>

<details>
<summary><b>5. ขั้นตอนการ debug compilation error 'undefined reference to Foam::fvMesh::fvMesh(...)?</b></summary>

**ขั้นตอนแก้ไข:**

1. **ระบุ library:** ฟังก์ชัน `fvMesh` อยู่ใน library `finiteVolume`
2. **แก้ Make/options:** เพิ่ม library ใน `EXE_LIBS`:
   ```make
   EXE_LIBS = \
       -lfiniteVolume
   ```
3. **Clean และ rebuild:**
   ```bash
   wclean
   wmake
   ```
4. **Verify:** ตรวจสอบว่า error หายไปและ utility รวมรวมสำเร็จ
</details>

<details>
<summary><b>6. ยุทธศาสตร์ 3 ขั้นตอนในการทดสอบ utility ที่เพิ่งสร้าง?</b></summary>

1. **Compilation test:**
   - รัน `wmake` และตรวจสอบว่าไม่มี warnings
   - ตรวจสอบว่า executable ถูกสร้างใน `$FOAM_USER_APPBIN`

2. **Basic runtime test:**
   - รัน utility บน test case ง่าย ๆ (เช่น pitzDaily)
   - ตรวจสอบว่าไม่มี runtime errors
   - ตรวจสอบ output format

3. **Validation test:**
   - เปรียบเทียบ results กับ standard utilities หรือ known values
   - ทดสอบกับ different cases (mesh sizes, boundary conditions)
   - ตรวจสอบ parallel execution (ถ้า relevant)
</details>

---

**เอกสารนี้เป็นส่วนหนึ่งของ Expert Utilities Module**

[← กลับไปหน้ารวม](00_Overview.md) | [Utility Categories →](01_Utility_Categories_and_Organization.md)