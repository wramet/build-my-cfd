# Dynamic Library Loading

การโหลด Library แบบ Dynamic

---

## 🎯 Learning Objectives

หลังจากอ่านบทนี้ คุณจะสามารถ:

1. **อธิบาย** กลไกการโหลด library แบบ dynamic ใน OpenFOAM
2. **ใช้งาน** libs directive ใน controlDict และ dlLibraryTable ใน code
3. **สร้างและคอมไพล์** custom library ด้วย wmake พร้อม Make/files ที่ถูกต้อง
4. **วิเคราะห์** ลำดับเหตุการณ์เมื่อ library ถูกโหลดและจัดการปัญหาที่เกิดขึ้น
5. **เลือกใช้** วิธีการโหลด library ที่เหมาะสมกับ use case ที่แตกต่างกัน

---

## Overview

> Load libraries at runtime without recompiling solver - เพิ่มความยืดหยุ่นให้ simulation ผ่าน dynamic linking

Dynamic library loading เป็นกลไกที่ทำให้ OpenFOAM สามารถโหลด custom functionality ที่ compile เป็น shared library (.so) ได้ใน runtime โดยไม่ต้อง recompile solver ทั้งหมด นี่คือพื้นฐานของ extensibility ที่ทำให้ผู้ใช้สามารถ:
- เพิ่ม turbulence models ใหม่
- สร้าง boundary conditions แบบ custom
- เขียน function objects สำหรับ monitoring
- สร้าง custom transport models

**กลไกหลัก:**
1. **libs directive** ใน controlDict - โหลด library อัตโนมัติเมื่อ solver เริ่มทำงาน
2. **dlLibraryTable API** - โหลด library แบบ programmatic จากภายใน code
3. **RTS registration** - ลงทะเบียน classes ผ่าน static initializers

---

## 1. Loading Libraries via controlDict

วิธีที่พบบ่อยที่สุดในการโหลด libraries คือการระบุใน `system/controlDict`:

### 1.1 Basic Syntax

```cpp
// system/controlDict
libs
(
    "libmyTurbulenceModels.so"
    "libmyBoundaryConditions.so"
    "libmyFunctionObjects.so"
);
```

**ลำดับเหตุการณ์:**

```
Solver Start
    ↓
Read controlDict
    ↓
Process libs directive
    ↓
Load each library (.so)
    ↓
Execute static initializers
    ↓
Register classes to RTS tables
    ↓
Continue reading dictionaries
    ↓
Instantiate models/boundaries
```

### 1.2 Library Search Path

OpenFOAM จะค้นหา libraries ตามลำดับนี้:

```bash
# 1. พาธที่ระบุใน libs directive (absolute/relative)
libs ("/absolute/path/to/libcustom.so");

# 2. $FOAM_USER_LIBBIN (default: $HOME/OpenFOAM/woramet-*/platforms/linux64GccDPInt32Opt/lib)
ls $FOAM_USER_LIBBIN
# Output: libcustomTurbulence.so  libcustomBC.so  ...

# 3. $FOAM_LIBBIN (system-wide: /opt/openfoam/platforms/.../lib)
ls $FOAM_LIBBIN

# 4. $LD_LIBRARY_PATH (environment variable)
echo $LD_LIBRARY_PATH
```

### 1.3 Loading at Specific Times

```cpp
// system/controlDict

// Load immediately at startup (default)
libs
(
    "libmyLibrary.so"
);

// Load on demand - ไม่ support โดยตรง
// ต้องใช้ dlLibraryTable API แทน
```

**⚠️ Important:** libraries จะถูกโหลด **ก่อน** ที่ solver จะอ่าน dictionaries อื่นๆ ดังนั้น classes ใน library จะพร้อมใช้งานใน `0/`, `constant/`, `system/` files

---

## 2. Programmatic Loading with dlLibraryTable

สำหรับการโหลด libraries แบบ dynamic จากภายใน code หรือ conditional loading:

### 2.1 Basic Usage

```cpp
#include "dlLibraryTable.H"

// Load single library
bool success = dlLibraryTable::open("libmyAdvancedModels.so");

if (!success)
{
    WarningInFunction
        << "Failed to load libmyAdvancedModels.so" << endl;
}
```

### 2.2 Conditional Loading

```cpp
// Example: Load library based on user setting
const dictionary& dict = mesh_.solutionDict();
bool useAdvancedModel = dict.getOrDefault<bool>("useAdvancedModel", false);

if (useAdvancedModel)
{
    if (dlLibraryTable::open("libAdvancedModels.so"))
    {
        Info << "Loaded advanced models library" << endl;
    }
    else
    {
        FatalErrorInFunction
            << "Cannot run without advanced models library"
            << exit(FatalError);
    }
}
```

### 2.3 Loading from Custom Path

```cpp
// Load from absolute path
dlLibraryTable::open("/path/to/custom/lib/libmyLib.so");

// Load from environment variable
fileName libPath = getEnv("MY_CUSTOM_LIB_DIR")/"libmyLib.so";
dlLibraryTable::open(libPath);

// Load multiple libraries
List<fileName> libFiles;
libFiles.append("libFirst.so");
libFiles.append("libSecond.so");

forAll(libFiles, i)
{
    dlLibraryTable::open(libFiles[i]);
}
```

### 2.4 Error Handling

```cpp
// Comprehensive error handling
if (!dlLibraryTable::open("libRequired.so"))
{
    // Option 1: Fatal error
    FatalErrorIn("mySolver::mySolver()")
        << "Required library libRequired.so not found"
        << nl
        << "Searched in:" << nl
        << "  - Current directory" << nl
        << "  - " << Foam::getEnv("FOAM_USER_LIBBIN") << nl
        << "  - " << Foam::getEnv("FOAM_LIBBIN") << nl
        << exit(FatalError);
}

// Option 2: Graceful degradation
if (!dlLibraryTable::open("libOptional.so"))
{
    Info << "Warning: Optional library not loaded, using defaults" << endl;
    useDefaultModels_ = true;
}
```

---

## 3. Complete Library Compilation Process

### 3.1 Directory Structure

```bash
myCustomLibrary/
├── Make/
│   ├── files          # Required: source files + output library name
│   └── options        # Required: include paths, compiler flags
├── myTurbModel.H      # Header file
├── myTurbModel.C      # Source file
├── myBoundaryCondition.H
├── myBoundaryCondition.C
└── README.md
```

### 3.2 Make/files (Required)

```cpp
// myCustomLibrary/Make/files

// Source files to compile
myTurbModel.C
myBoundaryCondition.C

// Output library (REQUIRED)
LIB = $(FOAM_USER_LIBBIN)/libmyCustomLibrary
```

**รายละเอียด:**
- **LIB =** ระบุ output library name และ location
- **$(FOAM_USER_LIBBIN)** = environment variable ชี้ไปที่ user lib directory
- **libmyCustomLibrary** = output จะเป็น `libmyCustomLibrary.so`
- **บรรทัดว่าง** = required separator ระหว่าง source files และ LIB directive

### 3.3 Make/options (Optional but Recommended)

```cpp
// myCustomLibrary/Make/options

// Include paths
EXE_INC = \
    -I$(LIB_SRC)/finiteVolume/lnInclude \
    -I$(LIB_SRC)/meshTools/lnInclude \
    -I$(LIB_SRC)/turbulenceModels \
    -I./../commonInclude

// Library dependencies (libraries this one links to)
LIB_LIBS = \
    -lfiniteVolume \
    -lmeshTools
```

**รายละเอียด:**
- **EXE_INC** = include paths สำหรับ header files
- **LIB_LIBS** = libraries ที่จำเป็นต้อง link ด้วย (สำหรับ libraries ไม่ใช่ executables)

### 3.4 Example Source File with RTS Registration

```cpp
// myTurbModel.H
#ifndef myTurbModel_H
#define myTurbModel_H

#include "turbulentTransportModel.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{

class myTurbModel
:
    public turbulentTransportModel
{
    // Private members
    // ...

public:
    // Runtime type information
    TypeName("myTurbModel");

    // Constructors
    myTurbModel
    (
        const geometricOneField& alpha,
        const geometricOneField& rho,
        const volVectorField& U,
        const surfaceScalarField& phi,
        const word& propertiesName
    );

    // Destructor
    virtual ~myTurbModel() = default;

    // Member functions
    // ...
};

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

} // End namespace Foam

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

#endif

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
```

```cpp
// myTurbModel.C
#include "myTurbModel.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{

// * * * * * * * * * * * * * * Static Data Members * * * * * * * * * * * * * //

defineTypeNameAndDebug(myTurbModel, 0);

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

// Constructor implementation
myTurbModel::myTurbModel
(
    const geometricOneField& alpha,
    const geometricOneField& rho,
    const volVectorField& U,
    const surfaceScalarField& phi,
    const word& propertiesName
)
:
    turbulentTransportModel(alpha, rho, U, phi, propertiesName)
{
    Info << "Creating myTurbModel" << endl;
}

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

} // End namespace Foam

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
```

### 3.5 Compilation Steps

```bash
# 1. Navigate to library directory
cd myCustomLibrary/

# 2. Source OpenFOAM environment (if not already sourced)
source /opt/openfoam/etc/bashrc

# 3. Compile library
wmake libso

# Expected output:
# wmake libso 
# wmake LnInclude: linking .so lnInclude directory to /path/to/lnInclude
# wmake MkDir: /home/user/OpenFOAM/user-2306/platforms/linux64GccDPInt32Opt/lib
# wmake /home/user/OpenFOAM/user-2306/platforms/linux64GccDPInt32Opt/lib/libmyCustomLibrary.so
# /usr/bin/c++  -std=c++14  -Dlinux64 -DWM_DP -DWM_SP -O3  -DNoRepository -ftemplate-depth-200 ...
# libmyCustomLibrary.so
# 
# Finished: library linked to: /home/user/OpenFOAM/user-2306/platforms/linux64GccDPInt32Opt/lib/libmyCustomLibrary.so

# 4. Verify library was created
ls -lh $FOAM_USER_LIBBIN/libmyCustomLibrary.so
# Output: -rwxr-xr-x 1 user group 45K Dec 31 10:30 libmyCustomLibrary.so

# 5. Check symbols (optional)
nm -D $FOAM_USER_LIBBIN/libmyCustomLibrary.so | grep myTurbModel
```

### 3.6 Common Compilation Issues

```bash
# Issue 1: "error: turbulentTransportModel.H: No such file or directory"
# Solution: Add missing include path in Make/options
EXE_INC = -I$(LIB_SRC)/turbulenceModels

# Issue 2: "undefined reference to `Foam::..."
# Solution: Add missing library dependency in Make/options
LIB_LIBS = -lturbulenceModels -lfiniteVolume

# Issue 3: "Make/files not found"
# Solution: Ensure Make/files exists with proper format (not Make/file)

# Issue 4: Permission denied
# Solution: Check write permissions on $FOAM_USER_LIBBIN
chmod u+w $FOAM_USER_LIBBIN
```

---

## 4. What Happens on Load - Deep Dive

เมื่อ library ถูกโหลด มีหลายขั้นตอนที่เกิดขึ้นภายในระบบ:

### 4.1 Operating System Level

```
1. dlopen() system call
   ├─ OpenFOAM calls dlLibraryTable::open()
   ├─ Which calls POSIX dlopen("libmyLib.so", RTLD_LAZY|RTLD_GLOBAL)
   └─ OS locates .so file and loads into memory
       ↓
2. Memory Mapping
   ├─ Map library segments into process address space
   ├─ Resolve library dependencies (DT_NEEDED entries)
   └─ Allocate memory for code (.text) and data (.data/.bss)
       ↓
3. Dynamic Linking
   ├─ Process .dynamic section
   ├─ Resolve symbol references (external function calls)
   └─ Apply relocations
       ↓
4. Initialization (Critical for OpenFOAM)
   ├─ Call all constructors in .ctors section (global objects)
   ├─ Execute static initializers
   │   └─ THIS IS WHERE RTS REGISTRATION HAPPENS
   └─ Run on_load functions if present
```

### 4.2 OpenFOAM RTS Registration

```cpp
// Static initializer executed automatically on load
defineTypeNameAndDebug(myTurbModel, 0);

// Expands to (conceptually):
namespace Foam
{
    // Static object created when library loads
    template<>
    const word& myTurbModel::typeName = "myTurbModel";
    
    template<>
    int myTurbModel::debug = 0;
    
    // Runtime table registration (executed in static initializer)
    addNamedToRunTimeSelectionTable
    (
        turbulentTransportModel,
        myTurbModel,
        dictionary,
        myTurbModel
    );
}
```

**Timing Diagram:**

```
Time: 0ms     10ms     20ms     30ms     40ms     50ms
      |        |        |        |        |        |
Solver Start  ─┬─> Read controlDict
                       ─┬─> Process libs directive
                                ─┬─> dlopen("libmyLib.so")
                                         ├─> Load .so to memory (1-5ms)
                                         ├─> Resolve symbols (2-10ms)
                                         └─> Run static initializers (5-20ms)
                                              └─> Register to RTS tables
                                                       ─┬─> Continue reading dictionaries
                                                                ─┬─> Instantiate models
```

### 4.3 Symbol Visibility

```cpp
// Make/options - Control symbol visibility
EXE_INC = \
    -I$(LIB_SRC)/... \
    -fvisibility=default  // Export all symbols (default)
    // -fvisibility=hidden // Hide all by default, export marked symbols
```

**Default behavior:** All symbols are exported and available for:
- Dynamic loading by dlLibraryTable
- Linking by other libraries
- Runtime type information (RTTI)

### 4.4 Library Dependencies

```bash
# Check library dependencies
ldd $FOAM_USER_LIBBIN/libmyCustomLibrary.so

# Output example:
#   libmyCustomLibrary.so:
#       -lfiniteVolume => /path/to/libfiniteVolume.so
#       -lmeshTools => /path/to/libmeshTools.so
#       libstdc++.so.6 => /usr/lib/x86_64-linux-gnu/libstdc++.so.6
#       libgcc_s.so.1 => /usr/lib/x86_64-linux-gnu/libgcc_s.so.1
#       libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6
```

**Loading order matters:** If libA depends on libB, load libB first:

```cpp
// Correct order
dlLibraryTable::open("libBase.so");        // Load first
dlLibraryTable::open("libDerived.so");     // Depends on libBase

// Wrong order - will fail if derived references base symbols immediately
dlLibraryTable::open("libDerived.so");     // May fail
dlLibraryTable::open("libBase.so");
```

### 4.5 Multiple Loading Protection

```cpp
// OpenFOAM prevents duplicate loading
dlLibraryTable::open("libmyLib.so");  // First call - loads library
dlLibraryTable::open("libmyLib.so");  // Second call - returns true, no reload

// Implementation checks:
if (!isLibraryLoaded("libmyLib.so"))
{
    loadLibrary("libmyLib.so");
    markAsLoaded("libmyLib.so");
}
```

---

## 5. Loading Methods Comparison

| Aspect | controlDict (libs) | dlLibraryTable API |
|--------|-------------------|-------------------|
| **When to use** | Always-load libraries | Conditional/optional loading |
| **Configuration** | Case-specific | Hard-coded in solver |
| **Loading time** | Solver startup | When API called |
| **Error handling** | Warning, continue | Programmatic control |
| **Search path** | FOAM_LIBBIN, user paths | Must specify or search |
| **Best for** | Custom BCs, turbulence models | Optional features, plugins |

**Use cases:**

```cpp
// Scenario 1: Custom turbulence model (use controlDict)
// system/controlDict
// libs ("libmyKEpsilon.so");

// Scenario 2: Optional advanced model (use dlLibraryTable)
if (userRequestedAdvanced)
{
    dlLibraryTable::open("libAdvanced.so");
}

// Scenario 3: Third-party plugin (use controlDict for flexibility)
// system/controlDict
// libs ("libThirdPartyPlugin.so");
```

---

## 6. Practical Exercise

### Exercise: Create and Load a Custom Library

**Objective:** Create a custom library containing a simple boundary condition and load it in a case.

#### Step 1: Create Library Structure

```bash
# Create directory structure
mkdir -p $FOAM_RUN/customBC/
cd $FOAM_RUN/customBC/

# Create Make directory
mkdir Make

# Create source files
touch myFixedValueFvPatchField.H
touch myFixedValueFvPatchField.C
```

#### Step 2: Write Header File

```cpp
// myFixedValueFvPatchField.H
#ifndef myFixedValueFvPatchField_H
#define myFixedValueFvPatchField_H

#include "fixedValueFvPatchFields.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{

class myFixedValueFvPatchField
:
    public fixedValueFvPatchField<scalar>
{
    // Private data

public:
    // Runtime type information
    TypeName("myFixedValue");

    // Constructors
    myFixedValueFvPatchField
    (
        const fvPatch&,
        const DimensionedField<scalar, volMesh>&
    );

    myFixedValueFvPatchField
    (
        const fvPatch&,
        const DimensionedField<scalar, volMesh>&,
        const dictionary&
    );

    // Member functions
    virtual void write(Ostream&) const;
};

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

} // End namespace Foam

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

#endif
```

#### Step 3: Write Source File

```cpp
// myFixedValueFvPatchField.C
#include "myFixedValueFvPatchField.H"
#include "addToRunTimeSelectionTable.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{

// * * * * * * * * * * * * * * Static Data Members * * * * * * * * * * * * * //

defineTypeNameAndDebug(myFixedValueFvPatchField, 0);
addToRunTimeSelectionTable
(
    fvPatchField<scalar>,
    myFixedValueFvPatchField,
    dictionary
);

// * * * * * * * * * * * * * * * * * Constructors  * * * * * * * * * * * * * //

myFixedValueFvPatchField::myFixedValueFvPatchField
(
    const fvPatch& p,
    const DimensionedField<scalar, volMesh>& iF
)
:
    fixedValueFvPatchField<scalar>(p, iF)
{
    Info << "Creating myFixedValue patch (default)" << endl;
}

myFixedValueFvPatchField::myFixedValueFvPatchField
(
    const fvPatch& p,
    const DimensionedField<scalar, volMesh>& iF,
    const dictionary& dict
)
:
    fixedValueFvPatchField<scalar>(p, iF, dict)
{
    Info << "Creating myFixedValue patch from dictionary" << endl;
    Info << "Patch: " << patch().name() << endl;
    Info << "Value: " << *this << endl;
}

// * * * * * * * * * * * * * * * Member Functions  * * * * * * * * * * * * * //

void myFixedValueFvPatchField::write(Ostream& os) const
{
    fixedValueFvPatchField<scalar>::write(os);
    os.writeKeyword("description")
        << "Custom fixedValue boundary condition"
        << token::END_STATEMENT << nl;
}

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

} // End namespace Foam

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
```

#### Step 4: Create Make/files

```bash
cat > Make/files << 'EOF'
myFixedValueFvPatchField.C

LIB = $(FOAM_USER_LIBBIN)/libCustomBC
EOF
```

#### Step 5: Create Make/options

```bash
cat > Make/options << 'EOF'
EXE_INC = \
    -I$(LIB_SRC)/finiteVolume/lnInclude

LIB_LIBS = \
    -lfiniteVolume
EOF
```

#### Step 6: Compile Library

```bash
cd $FOAM_RUN/customBC/
wmake libso

# Expected output:
# wmake libso
# wmake LnInclude: linking lnInclude directory to ...
# libCustomBC.so
# Finished: library linked to: $FOAM_USER_LIBBIN/libCustomBC.so

# Verify compilation
ls -lh $FOAM_USER_LIBBIN/libCustomBC.so
nm -D $FOAM_USER_LIBBIN/libCustomBC.so | grep myFixedValue
```

#### Step 7: Create Test Case

```bash
# Copy tutorial case
cp -r $FOAM_TUTORIALS/incompressible/simpleFoam/airFoil2D $FOAM_RUN/testCustomBC/
cd $FOAM_RUN/testCustomBC/

# Modify 0/U to use custom BC
cat > 0/U << 'EOF'
dimensions      [0 1 -1 0 0 0 0];

internalField   uniform (0 0 0);

boundaryField
{
    inlet
    {
        type            myFixedValue;
        value           uniform (10 0 0);
    }
    
    outlet
    {
        type            zeroGradient;
    }
    
    "(wall|airFoil).*"
    {
        type            noSlip;
    }
    
    "#includeEtc"
    {
        type            empty;
    }
}
EOF
```

#### Step 8: Load Library in Case

```bash
# Modify system/controlDict
cat >> system/controlDict << 'EOF'

libs
(
    "libCustomBC.so"
);
EOF
```

#### Step 9: Run and Verify

```bash
# Run solver
simpleFoam

# Expected output:
# /*---------------------------------------------------------------------------*\
# | =========                 |                                                 |
# | \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
# |  \\    /   O peration     | Version:  v2306                                 |
# |   \\  /    A nd           | Web:      www.openfoam.com                      |
# |    \\/     M anipulation  |                                                 |
# \*---------------------------------------------------------------------------*/
# Build  : _some_hash_
# Arch   : "linux64GccDPInt32Opt"
# Exec   : simpleFoam
# Date   : Dec 31 2025
# Time   : 10:30:45
# Host   : hostname
# PID    : 12345
# 
# // * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
# Creating myFixedValue patch from dictionary
# Patch: inlet
# Value: uniform(10 0 0)
# ...
```

#### Step 10: Verification Checklist

```bash
# 1. Check library loaded
grep "libCustomBC" log.simpleFoam

# 2. Check BC created
grep "Creating myFixedValue" log.simpleFoam

# 3. Check simulation ran successfully
grep "End" log.simpleFoam

# 4. Verify output times exist
ls -1 processor* 2>/dev/null || ls -1 0.* 2>/dev/null

# 5. Check boundary values in final time
paraFoam -builtin
# Visually inspect inlet boundary condition
```

**Success criteria:**
- ✓ Library compiles without errors
- ✓ Library loads on solver startup (check log)
- ✓ Custom BC initializes (see Info message)
- ✓ Simulation completes successfully
- ✓ Boundary condition values are applied correctly

---

## 📚 Quick Reference

### Loading Libraries

| Task | Command/Syntax |
|------|----------------|
| Load in controlDict | `libs ("libmyLib.so");` |
| Load programmatically | `dlLibraryTable::open("libmyLib.so");` |
| Load with path | `dlLibraryTable::open("/path/to/lib.so");` |
| Check library loaded | `ldd libmyLib.so` |
| List symbols | `nm -D libmyLib.so \| grep typeName` |

### Compilation

| Task | Command |
|------|---------|
| Compile library | `wmake libso` |
| Clean library | `wclean` |
| Rebuild | `wclean && wmake libso` |
| Check include paths | `echo $WM_PROJECT_USER_DIR` |

### Library Locations

| Variable | Path |
|----------|------|
| `$FOAM_USER_LIBBIN` | `$HOME/OpenFOAM/<user>-<version>/platforms/<arch>/lib` |
| `$FOAM_LIBBIN` | `$WM_PROJECT_INST_DIR/<version>/platforms/<arch>/lib` |

### Make Files Template

```cpp
// Make/files (REQUIRED)
sourceFile1.C
sourceFile2.C
LIB = $(FOAM_USER_LIBBIN)/libMyLibrary

// Make/options (OPTIONAL)
EXE_INC = -I$(LIB_SRC)/finiteVolume/lnInclude
LIB_LIBS = -lfiniteVolume
```

---

## 🔑 Key Takeaways

1. **Dynamic library loading** ทำให้เราสามารถ extend OpenFOAM โดยไม่ต้อง recompile solver ทั้งหมด
2. **libs directive** ใน controlDict เป็นวิธีหลักในการโหลด libraries ที่ run-time
3. **RTS registration** เกิดขึ้นใน static initializers ซึ่ง execute อัตโนมัติเมื่อ library ถูกโหลด
4. **Make/files** ต้องระบุ source files และ `LIB =` directive อย่างน้อย 1 บรรทัดว่าง
5. **Compilation process** ใช้ `wmake libso` ซึ่งสร้าง .so file ใน $FOAM_USER_LIBBIN
6. **Loading order** matters: dependencies ต้องถูกโหลดก่อน libraries ที่ dependent
7. **dlLibraryTable API** ให้การ control ที่ดีกว่าสำหรับ conditional loading และ error handling
8. **Symbol visibility** ควบคุมได้ผ่าน compiler flags (-fvisibility)

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Runtime Selection:** [02_Runtime_Selection_Tables.md](02_Runtime_Selection_Tables.md)
- **Factory Pattern:** [03_Design_Patterns.md](../03_DESIGN_PATTERNS/03_Design_Patterns.md)
- **Code Organization:** [05_Professional_Practice/01_Project_Organization.md](../../MODULE_07_UTILITIES_AUTOMATION/CONTENT/05_PROFESSIONAL_PRACTICE/01_Project_Organization.md)