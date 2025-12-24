# 6. ข้อผิดพลาดที่พบบ่อยและการ Debugging

ส่วนนี้ครอบคลุมข้อผิดพลาดที่พบบ่อยและเทคนิคการ debugging เมื่อทำงานกับระบบสถาปัตยกรรมความสามารถในการขยายของ OpenFOAM การเข้าใจปัญหาเหล่านี้จะช่วยให้คุณหลีกเลี่ยงและแก้ไขปัญหาได้อย่างรวดเร็วเมื่อพัฒนา functionObjects และ extensions แบบกำหนดเอง

## 6.1 ข้อผิดพลาดในการ Compile (Compilation Errors)

### Template Instantiation Errors

**Problem:** Template instantiation failure เมื่อ compile functionObjects

```cpp
// Error example:
// error: undefined reference to `Foam::myFunctionObject::New(...)`
```

**Solution:** ตรวจสอบให้แน่ใจว่าได้ include header files ที่จำเป็นและ template specializations ครบถ้วน

```cpp
// Include forward declarations for volume fields
// Include concrete field implementations
// Include base functionObject class
// Include dictionary class for parameter reading
#include "volFieldsFwd.H"      // Forward declarations
#include "volScalarField.H"    // Concrete implementations
#include "functionObject.H"
#include "dictionary.H"
```

📚 **คำอธิบายเชิงลึก:**

**แหล่งที่มา (Source):**
```
.applications/utilities/mesh/generation/foamyMesh/conformalVoronoiMesh/initialPointsMethod/initialPointsMethod/initialPointsMethod.C
```

**คำอธิบาย (Explanation):**
- `volFieldsFwd.H` มีการ forward declarations สำหรับ field types ที่ช่วยลด circular dependencies
- `volScalarField.H` มีการ implement จริงของ scalar field class
- Template instantiation ต้องการทั้ง declaration และ definition ให้ครบถ้วน

**แนวคิดสำคัญ (Key Concepts):**
1. **Forward Declaration**: ประกาศชื่อ class โดยไม่ต้อง include header เต็ม
2. **Template Instantiation**: กระบวนการสร้าง code จริงจาก template
3. **Circular Dependency**: เมื่อสอง files ต้องการ include กันและกัน

**Debugging Tip:** ใช้ `wmake -debug` เพื่อดูรายละเอียดการ expand macros และ template instantiation

### Linking Errors

**Problem:** Undefined reference to typeinfo หรือ vtable

```bash
# Error: undefined reference to 'typeinfo for Foam::myFunctionObject'
# หรือ: undefined reference to 'vtable for Foam::myFunctionObject'
```

**Solution:** Virtual functions ต้องถูกกำหนดอย่างถูกต้อง

```cpp
// Always provide virtual destructor to ensure proper cleanup
// Override pure virtual functions from base class
// Use default keyword for simple default implementations
class myFunctionObject : public functionObject
{
public:
    // Virtual destructor required for proper polymorphic behavior
    virtual ~myFunctionObject() {}  // Virtual destructor จำเป็น
    
    // Pure virtual function - must be implemented by derived classes
    virtual bool execute() = 0;
    
    // Pure virtual function for writing results
    virtual bool write() = 0;
};

// Alternative: Use default keyword for defaulted destructor
// This generates the default implementation automatically
virtual ~myFunctionObject() = default;
```

📚 **คำอธิบายเชิงลึก:**

**แหล่งที่มา (Source):**
```
.applications/utilities/mesh/generation/foamyMesh/conformalVoronoiMesh/initialPointsMethod/initialPointsMethod/initialPointsMethod.C
```

**คำอธิบาย (Explanation):**
- **typeinfo** ถูกสร้างโดย compiler สำหรับ polymorphic classes (classes ที่มี virtual functions)
- **vtable** (virtual table) เป็น table ของ function pointers ที่ใช้สำหรับ dynamic dispatch
- Undefined reference เกิดเมื่อ:
  - ลืม implement virtual functions
  - ลืม provide virtual destructor
  - Linker หา implementation ไม่เจอ

**แนวคิดสำคัญ (Key Concepts):**
1. **Vtable**: Table ของ function pointers สำหรับ runtime polymorphism
2. **RTTI (Run-Time Type Information)**: ข้อมูลประเภทของ object ที่ runtime
3. **Dynamic Dispatch**: การเลือก function ที่จะเรียกตามประเภทจริงของ object

**Common Mistake:** ลืม implement pure virtual functions ทั้งหมดใน derived class

## 6.2 ข้อผิดพลาดใน Runtime (Runtime Errors)

### 6.2.1 Dynamic Library Loading Issues

**Problem:** Library ไม่สามารถโหลดได้

```bash
# Error message:
--> FOAM FATAL ERROR:
    Unknown functionObject type myFilter
```

**Diagnostic Steps:**

1. **ตรวจสอบว่า library ถูก compile อย่างถูกต้อง**
```bash
# Verify library exists in user libbin directory
ls -la $FOAM_USER_LIBBIN/libmyFunctionObjects.so

# Check library dependencies and linked libraries
ldd $FOAM_USER_LIBBIN/libmyFunctionObjects.so
```

2. **ตรวจสอบการลงทะเบียนใน source code**
```cpp
// Macro to register functionObject in runtime selection table
// This must be present in the .C file, not in .H file
addToRunTimeSelectionTable
(
    functionObject,              // Base class name
    myFunctionObject,            // Derived class name
    dictionary                   // Constructor dictionary type
);
```

3. **ตรวจสอบ controlDict**
```cpp
// In system/controlDict - functionObject configuration
functions
{
    myFilter
    {
        // Type name must match TypeName in code
        type            myFilter;           // ต้องตรงกับ TypeName
        
        // Library name to load
        libs            ("libmyFunctionObjects.so");  // ต้องถูกต้อง
    }
}
```

📚 **คำอธิบายเชิงลึก:**

**แหล่งที่มา (Source):**
```
.applications/utilities/mesh/generation/foamyMesh/conformalVoronoiMesh/initialPointsMethod/initialPointsMethod/initialPointsMethod.C
```

**คำอธิบาย (Explanation):**
- `addToRunTimeSelectionTable` macro สร้าง entry ใน static table ที่ใช้ lookup functionObjects
- Macro นี้ต้องอยู่ใน `.C` file เพื่อให้ถูก execute เพียงครั้งเดียว
- OpenFOAM ใช้ **Runtime Selection Tables** สำหรับ dynamic object creation

**แนวคิดสำคัญ (Key Concepts):**
1. **Runtime Selection**: การสร้าง objects โดยไม่รู้ประเภทล่วงหน้า
2. **Static Initialization**: Code ที่รันก่อน main() เพื่อสร้าง registration tables
3. **Dynamic Loading**: โหลด libraries ที่ runtime ผ่าน dlopen

**Solution with Error Checking:**

```cpp
// Enhanced constructor with robust error handling
// This demonstrates proper validation and error reporting
myFunctionObject::myFunctionObject
(
    const word& name,           // Name of this functionObject
    const Time& runTime,        // Time object reference
    const dictionary& dict      // Parameter dictionary
)
:
    // Initialize base class with name
    functionObject(name),
    
    // Store reference to mesh - lookup "region0" mesh
    mesh_(runTime.lookupObject<fvMesh>("region0")),
    
    // Initialize member variables with default values
    fieldName_(word::null),
    threshold_(0.0)
{
    // Verify mesh object exists with try-catch for safety
    const fvMesh* meshPtr = nullptr;
    try
    {
        // Attempt to lookup mesh from object registry
        meshPtr = &runTime.lookupObject<fvMesh>("region0");
    }
    catch (const Foam::error& e)
    {
        // Fatal error if mesh not found - stops simulation
        FatalErrorIn("myFunctionObject::myFunctionObject")
            << "Cannot find fvMesh object: " << e.what() << exit(FatalError);
    }

    // Read configuration with validation
    // Check if required parameter exists
    if (!dict.readIfPresent("fieldName", fieldName_))
    {
        // Fatal I/O error if required parameter missing
        FatalIOErrorIn
        (
            "myFunctionObject::myFunctionObject",
            dict
        ) << "Missing mandatory entry 'fieldName'" << exit(FatalIOError);
    }
}
```

📚 **คำอธิบายเชิงลึก:**

**แหล่งที่มา (Source):**
```
.applications/utilities/mesh/generation/foamyMesh/conformalVoronoiMesh/initialPointsMethod/initialPointsMethod/initialPointsMethod.C
```

**คำอธิบาย (Explanation):**
- Constructor initialization list ใช้ initialize members ก่อน constructor body execute
- `lookupObject<fvMesh>()` ค้นหา mesh จาก object registry ของ Time
- `FatalErrorIn` และ `FatalIOErrorIn` เป็น OpenFOAM error handling mechanisms

**แนวคิดสำคัญ (Key Concepts):**
1. **Constructor Initialization List**: วิธีที่ efficient ที่สุดในการ initialize members
2. **Exception Handling**: การจัดการ error ด้วย try-catch
3. **Object Registry**: ตัวจัดการ objects ใน OpenFOAM

### 6.2.2 Registration Debugging

**Problem:** FunctionObject ไม่ปรากฏใน registration table

**Debug Code:** เพิ่มโค้ดนี้ใน constructor เพื่อตรวจสอบ

```cpp
// Add to constructor for debugging registration
// This code lists all registered functionObjects
if (debug)
{
    // Print header for registration table dump
    Info << "FunctionObject registration table:" << nl;

    // Get pointer to the runtime selection table
    const Foam::dictionaryConstructorTable* tablePtr =
        &Foam::functionObject::dictionaryConstructorTablePtr_;

    // Check if table exists
    if (tablePtr)
    {
        // Print total number of registered functionObjects
        Info << "Total registered: " << tablePtr->size() << nl;

        // Iterate through all registered entries
        forAllConstIter(Foam::dictionaryConstructorTable, *tablePtr, iter)
        {
            // Print each registered functionObject name
            Info << "  Registered: " << iter.key() << nl;
        }
    }
    else
    {
        // Warning if table pointer is null
        Info << "Warning: Constructor table is null!" << nl;
    }
}
```

📚 **คำอธิบายเชิงลึก:**

**แหล่งที่มา (Source):**
```
.applications/utilities/mesh/generation/foamyMesh/conformalVoronoiMesh/initialPointsMethod/initialPointsMethod/initialPointsMethod.C
```

**คำอธิบาย (Explanation):**
- `dictionaryConstructorTablePtr_` เป็น global pointer ไปยัง registration table
- `forAllConstIter` เป็น OpenFOAM macro สำหรับ iterate containers อย่างปลอดภัย
- Registration table เป็น `HashTable` ที่ map type names ไปยัง constructor pointers

**แนวคิดสำคัญ (Key Concepts):**
1. **Static Class Members**: Variables ที่ใช้ร่วมกันทุก instances
2. **Template Metaprogramming**: การใช้ templates สร้าง data structures
3. **Debug Macros**: Macros ที่ใช้สำหรับ debugging

**Enable Debug Mode:**
```bash
# Set environment variable to enable global debug output
export FOAM_DEBUG=1

# Or enable per-class debugging in controlDict
DebugSwitches
{
    myFunctionObject 1;    // Enable debug for this class only
}
```

### 6.2.3 Field Access Errors

**Problem:** Field ไม่พบใน mesh

```cpp
// Error:
--> FOAM FATAL ERROR:
    Cannot find object file U in objectRegistry
```

**Solution:** ตรวจสอบว่า field มีอยู่จริงก่อนเข้าถอง

```cpp
// Safe field access with validation
// Always check field existence before accessing
void myFunctionObject::processField()
{
    // Check if field exists first before accessing
    // This prevents fatal errors when field is missing
    if (!mesh_.foundObject<volScalarField>(fieldName_))
    {
        // Print warning if field not found
        WarningIn("myFunctionObject::processField()")
            << "Field " << fieldName_ << " not found in mesh"
            << "Available fields: " << mesh_.names() << endl;
        return;    // Exit gracefully instead of crashing
    }

    // Safe access after validation - now we know field exists
    const volScalarField& field =
        mesh_.lookupObject<volScalarField>(fieldName_);

    // Process field...
}
```

📚 **คำอธิบายเชิงลึก:**

**แหล่งที่มา (Source):**
```
.applications/utilities/mesh/generation/foamyMesh/conformalVoronoiMesh/initialPointsMethod/initialPointsMethod/initialPointsMethod.C
```

**คำอธิบาย (Explanation):**
- `foundObject<T>()` ตรวจสอบว่ามี object ใน registry โดยไม่ throw error
- `lookupObject<T>()` ค้นหาและ return reference ถึง object
- Object Registry เป็น central repository สำหรับทุก objects ใน simulation

**แนวคิดสำคัญ (Key Concepts):**
1. **Defensive Programming**: การเขียนโค้ดที่รองรับ error conditions
2. **Object Registry**: Central storage สำหรับ simulation objects
3. **Type Safety**: Compile-time type checking ผ่าน templates

**Debug Available Fields:**
```cpp
// List all available fields in mesh for debugging
const wordList& fieldNames = mesh_.names();
Info << "Available fields:" << nl;
forAll(fieldNames, i)
{
    Info << "  " << fieldNames[i] << nl;
}
```

## 6.3 ข้อผิดพลาดเกี่ยวกับ Memory

### Memory Leaks

**Problem:** Memory ใช้เพิ่มขึ้นเรื่อยๆ ระหว่าง simulation

**Common Causes:**

1. **ไม่ใช้ smart pointers อย่างถูกต้อง**
```cpp
// BAD: Raw pointer without deletion - memory leak!
// Memory allocated but never freed
volScalarField* field = new volScalarField(...);
// Oops, forgot delete!

// GOOD: Use autoPtr for automatic memory management
// autoPtr automatically deletes object when it goes out of scope
autoPtr<volScalarField> fieldPtr
(
    new volScalarField(...)
);
// Automatic cleanup when fieldPtr goes out of scope
```

2. **Static objects ไม่ถูก cleanup**
```cpp
// BAD: Static allocation in function - memory never freed
static volScalarField* staticField = new volScalarField(...);
// This memory is NEVER freed - leaks until program exits

// GOOD: Use class member with proper lifecycle
// Memory managed by class constructor/destructor
class myFunctionObject
{
    // Smart pointer member - automatically managed
    autoPtr<volScalarField> field_;
};
```

📚 **คำอธิบายเชิงลึก:**

**แหล่งที่มา (Source):**
```
.applications/utilities/mesh/generation/foamyMesh/conformalVoronoiMesh/initialPointsMethod/initialPointsMethod/initialPointsMethod.C
```

**คำอธิบาย (Explanation):**
- **Raw Pointers**: ต้องจัดการ memory เอง ด้วย `delete` - ง่ายที่จะลืม
- **autoPtr**: Smart pointer ที่เป็นเจ้าของ object อย่างเดียว (exclusive ownership)
- **Memory Leak**: Memory ที่จองไว้แต่ไม่ได้คืน - สะสมจนหมด resource

**แนวคิดสำคัญ (Key Concepts):**
1. **RAII (Resource Acquisition Is Initialization)**: จอง resource ใน constructor, คืนใน destructor
2. **Smart Pointers**: Pointers ที่จัดการ memory อัตโนมัติ
3. **Ownership Semantics**: การกำหนดว่าใครเป็นเจ้าของ memory

**Memory Profiling:**
```bash
# Use valgrind for memory leak detection
# Runs simulation with detailed memory tracking
mpirun -np 4 valgrind --leak-check=full --show-leak-kinds=all \
    simpleFoam -parallel > valgrind.log 2>&1

# Check for memory usage during runtime
# Monitor memory consumption in real-time
watch -n 1 'ps aux | grep simpleFoam'
```

### Dangling Pointers

**Problem:** การเข้าถึง memory ที่ถูก deallocate แล้ว

```cpp
// DANGEROUS: Reference to temporary
// This reference becomes invalid after mesh update
const volScalarField& tempField =
    mesh_.lookupObject<volScalarField>("U");
// tempField may become dangling pointer after mesh update!
// Dereferencing it causes undefined behavior or crash
```

**Solution:** ใช้ `autoPtr` หรือ lookup ใหม่ทุกครั้ง

```cpp
// SAFE: Re-lookup each time to ensure validity
// Always look up fresh reference to avoid dangling pointers
bool execute()
{
    // Check field exists each time
    if (mesh_.foundObject<volScalarField>("U"))
    {
        // Get fresh reference - guaranteed valid
        const volScalarField& field =
            mesh_.lookupObject<volScalarField>("U");
        
        // Use field immediately - don't store reference long-term
    }
    return true;
}
```

📚 **คำอธิบายเชิงลึก:**

**แหล่งที่มา (Source):**
```
.applications/utilities/mesh/generation/foamyMesh/conformalVoronoiMesh/initialPointsMethod/initialPointsMethod/initialPointsMethod.C
```

**คำอธิบาย (Explanation):**
- **Dangling Pointer**: Pointer ที่ชี้ไปยัง memory ที่ถูก deallocate แล้ว
- **Undefined Behavior**: การ dereference dangling pointer สามารถทำให้โปรแกรม crash หรือทำงานผิด
- **Reference Lifetime**: References ใน C++ ไม่มี mechanism ตรวจสอบความถูกต้องอัตโนมัติ

**แนวคิดสำคัญ (Key Concepts):**
1. **Object Lifetime**: ระยะเวลาที่ object ถูกจอง memory อยู่
2. **Reference Validity**: ช่วงเวลาที่ reference สามารถใช้งานได้อย่างปลอดภัย
3. **Smart Pointers**: วิธีป้องกัน dangling pointers ด้วย automatic management

## 6.4 ข้อผิดพลาดเกี่ยวกับ Mesh Update

### Mesh Topology Changes

**Problem:** FunctionObject ทำงานผิดพลาดหลังจาก mesh topology เปลี่ยน

```cpp
// Error when using dynamic mesh (e.g., fvMotionSolver)
--> FOAM FATAL ERROR:
    Attempting to address invalid field pointer
```

**Solution:** Implement mesh update handlers

```cpp
// Handle mesh topology changes (e.g., refinement, adaptive meshing)
// This method is called when mesh topology changes
void myFunctionObject::updateMesh(const mapPolyMesh& mpm)
{
    Info << "Mesh topology changed, updating fields..." << endl;

    // Check if we have a valid field to update
    if (filteredField_.valid())
    {
        // Map field from old mesh to new mesh topology
        // mapPolyMesh contains information about how cells/points moved
        filteredField_().mapFields(mpm);
    }
}

// Handle mesh point motion (e.g., moving mesh, FSI)
// This method is called when mesh points move but topology stays same
void myFunctionObject::movePoints(const polyMesh& mesh)
{
    Info << "Mesh points moved" << endl;

    // Check if we have a valid field
    if (filteredField_.valid())
    {
        // Update geometric quantities (cell volumes, face areas, etc.)
        // Fields may need to be re-interpolated or recalculated
        filteredField_().movePoints();
    }
}
```

📚 **คำอธิบายเชิงลึก:**

**แหล่งที่มา (Source):**
```
.applications/utilities/mesh/generation/foamyMesh/conformalVoronoiMesh/initialPointsMethod/initialPointsMethod/initialPointsMethod.C
```

**คำอธิบาย (Explanation):**
- **mapPolyMesh**: Object ที่มีข้อมูลการ mapping ระหว่าง old mesh และ new mesh
- **updateMesh()**: Called เมื่อ mesh topology เปลี่ยน (add/remove cells, refinement)
- **movePoints()**: Called เมื่อ mesh points move แต่ topology เหมือนเดิม (deformation)

**แนวคิดสำคัญ (Key Concepts):**
1. **Mesh Topology**: โครงสร้างของ mesh (cells, faces, points)
2. **Mesh Motion**: การเคลื่อนที่ของ mesh points
3. **Field Mapping**: การ transfer field data ระหว่าง meshes

## 6.5 ข้อผิดพลาดเกี่ยวกับ Parallel Execution

### Processor Boundary Issues

**Problem:** ข้อมูลไม่ถูก synchronize ข้าม processors

```cpp
// WRONG: Local operation only - gives wrong results in parallel
// This only calculates max on local processor, not globally
scalar localMax = max(filteredField.primitiveField());
Info << "Max value: " << localMax << endl;  // Wrong on parallel!
```

**Solution:** ใช้ global reduction operations

```cpp
// CORRECT: Parallel-aware operation
// Use gMax (global max) to reduce across all processors
scalar localMax = max(filteredField.primitiveField());
scalar globalMax = gMax(filteredField.primitiveField());  // Reduce across procs

// Similarly for sum - use gSum for global sum
scalar localSum = sum(filteredField.primitiveField() * mesh_.V());
scalar globalSum = gSum(filteredField.primitiveField() * mesh_.V());  // Parallel sum

// Now we have correct global values
Info << "Global max: " << globalMax << ", Global sum: " << globalSum << endl;
```

📚 **คำอธิบายเชิงลึก:**

**แหล่งที่มา (Source):**
```
.applications/utilities/mesh/generation/foamyMesh/conformalVoronoiMesh/initialPointsMethod/initialPointsMethod/initialPointsMethod.C
```

**คำอธิบาย (Explanation):**
- **Local Operations**: ทำงานเฉพาะบน processor นั้นๆ - ผิดสำหรับ global calculations
- **Global Reductions**: Operations ที่รวมข้อมูลจากทุก processors (gMax, gSum, gMin, etc.)
- **MPI Communication**: การส่งข้อมูลระหว่าง processors ผ่าน MPI calls

**แนวคิดสำคัญ (Key Concepts):**
1. **Domain Decomposition**: การแบ่ง mesh ไปยัง processors หลายๆ ตัว
2. **Ghost Cells**: Cells ที่ขอบที่ใช้แลกเปลี่ยนข้อมูลระหว่าง processors
3. **Reduction Operations**: Operations ที่รวบรวมข้อมูลจากทุก processors

### MPI Communication Errors

**Problem:** Deadlock หรือ segmentation fault ใน parallel runs

**Debugging:**
```bash
# Run with MPI debugging enabled
# This shows detailed MPI communication information
mpirun -np 4 --mca coll_tuned_use_dynamic_rules 1 \
    --mca btl_base_verbose 30 simpleFoam -parallel

# Check processor communication with debugger
# Opens separate terminal for each processor
mpirun -np 4 xterm -e gdb simpleFoam
```

**Best Practices:**
```cpp
// Always check if we should write/output
// Only master process should write to disk to avoid corruption
if (Pstream::master())
{
    // Only master writes to disk
    outputFile_().write(data);
}

// Use reduce for custom operations
// Example: custom reduction across all processors
scalar customValue = ...;
reduce(customValue, sumOp<scalar>());    // Sum across all processors
reduce(customValue, maxOp<scalar>());    // Find maximum across processors
```

📚 **คำอธิบายเชิงลึก:**

**แหล่งที่มา (Source):**
```
.applications/utilities/mesh/generation/foamyMesh/conformalVoronoiMesh/initialPointsMethod/initialPointsMethod/initialPointsMethod.C
```

**คำอธิบาย (Explanation):**
- **Pstream::master()**: Returns true ถ้าเป็น master process (rank 0)
- **reduce()**: Global reduction operation ที่รวมข้อมูลจากทุก processors
- **Deadlock**: เมื่อ processors รอกันและไม่สามารถดำเนินการต่อได้

**แนวคิดสำคัญ (Key Concepts):**
1. **MPI Rank**: หมายเลขประจำตัวของแต่ละ processor (0 to n-1)
2. **Collective Operations**: Operations ที่ต้องมีการ participation จากทุก processors
3. **Parallel I/O**: การเขียนข้อมูลใน parallel runs อย่างปลอดภัย

## 6.6 ข้อผิดพลาดในการกำหนดค่า (Configuration Errors)

### Dictionary Parsing Errors

**Problem:** Syntax ผิดใน controlDict

```cpp
// WRONG: Missing semicolon - causes parsing error
functions
{
    myFilter
    {
        type myFilter    // Missing semicolon! Parser will fail here
    }
}
```

**Solution:** ตรวจสอบ syntax อย่างละเอียด

```cpp
// CORRECT: Proper OpenFOAM dictionary syntax
// Note semicolons after each value
functions
{
    myFilter
    {
        // FunctionObject type name - must match registered TypeName
        type            myFilter;         // Note the semicolon
        
        // Library containing this functionObject
        libs            ("libmyFunctionObjects.so");
        
        // Field to process
        fieldName       U;
        
        // Threshold value for filtering
        threshold       5.0;

        // Execute control parameters
        executeControl  timeStep;
        executeInterval 10;

        // Write control parameters
        writeControl    timeStep;
        writeInterval   10;
    }
}
```

📚 **คำอธิบายเชิงลึก:**

**แหล่งที่มา (Source):**
```
.applications/utilities/mesh/generation/foamyMesh/conformalVoronoiMesh/initialPointsMethod/initialPointsMethod/initialPointsMethod.C
```

**คำอธิบาย (Explanation):**
- OpenFOAM dictionaries ใช้ semicolons เพื่อ terminate entries
- Parentheses ใช้สำหรับ lists และ strings ที่มี spaces
- Indentation ใช้เพื่อ readability แต่ไม่ใช่ syntax requirement

**แนวคิดสำคัญ (Key Concepts):**
1. **Dictionary Syntax**: รูปแบบ grammar ของ OpenFOAM dictionaries
2. **Keyword-Value Pairs**: โครงสร้างพื้นฐานของ dictionary entries
3. **Parsing**: กระบวนการแปลง text เป็น data structures

**Validation in Code:**
```cpp
// Override read method to validate configuration
// This is called when functionObject is created or re-read
bool myFunctionObject::read(const dictionary& dict)
{
    // Validate required entries exist
    // Fatal error if required parameter missing
    if (!dict.found("fieldName"))
    {
        FatalIOErrorIn("myFunctionObject::read", dict)
            << "Required entry 'fieldName' not found" << exit(FatalIOError);
    }

    // Read parameters with validation
    // readIfPresent returns false if entry doesn't exist
    dict.readIfPresent("fieldName", fieldName_);
    
    // getOrDefault provides default value if entry missing
    threshold_ = dict.getOrDefault<scalar>("threshold", 0.0);

    // Print configuration for user confirmation
    Info << "Configuration:" << nl
         << "  fieldName: " << fieldName_ << nl
         << "  threshold: " << threshold_ << endl;

    return true;    // Return true if read successful
}
```

📚 **คำอธิบายเชิงลึก:**

**แหล่งที่มา (Source):**
```
.applications/utilities/mesh/generation/foamyMesh/conformalVoronoiMesh/initialPointsMethod/initialPointsMethod/initialPointsMethod.C
```

**คำอธิบาย (Explanation):**
- `found()` method checks ว่ามี entry ใน dictionary หรือไม่
- `readIfPresent()` อ่านค่าถ้ามี, ไม่ error ถ้าไม่มี
- `getOrDefault<T>()` อ่านค่าและใช้ค่า default ถ้าไม่มี

**แนวคิดสำคัญ (Key Concepts):**
1. **Input Validation**: การตรวจสอบความถูกต้องของ input parameters
2. **Default Values**: ค่าที่ใช้เมื่อ user ไม่ระบุ
3. **Error Messages**: ข้อความ error ที่ชัดเจนช่วย debugging

## 6.7 Debugging Tools และ Techniques

### Enable Debug Output

**1. Function-level debugging:**
```cpp
// In class definition - define debug switch
// First parameter: type name, second: initial debug level (0=off)
defineTypeNameAndDebug(myFunctionObject, 0);

// In controlDict - enable debug for specific class
DebugSwitches
{
    myFunctionObject 1;  // 0=off, 1=on, 2=verbose
}
```

**2. Conditional debug output:**
```cpp
// Only print debug info if debug flag is enabled
if (debug)
{
    // Print detailed debugging information
    Info << "DEBUG: Field name = " << fieldName_ << nl
         << "DEBUG: Threshold = " << threshold_ << nl
         << "DEBUG: Field size = " << field.size() << endl;
}
```

📚 **คำอธิบายเชิงลึก:**

**แหล่งที่มา (Source):**
```
.applications/utilities/mesh/generation/foamyMesh/conformalVoronoiMesh/initialPointsMethod/initialPointsMethod/initialPointsMethod.C
```

**คำอธิบาย (Explanation):**
- `defineTypeNameAndDebug` macro สร้าง:
  - TypeName สำหรับ runtime selection
  - debug variable สำหรับ conditional output
- `debug` เป็น static int ที่สามารถเปลี่ยนได้ที่ runtime

**แนวคิดสำคัญ (Key Concepts):**
1. **Conditional Compilation**: Code ที่ทำงานเฉพาะเมื่อ condition เป็นจริง
2. **Debug Switches**: Variables ที่ควบคุม debug output
3. **Runtime Configuration**: การเปลี่ยน behavior โดยไม่ต้อง recompile

### Performance Profiling

**1. CPU Time Profiling:**
```cpp
// Add timing instrumentation to measure performance
class myFunctionObject
{
    // Accumulated CPU time
    scalar cpuTime_;
    
    // Number of times execute was called
    label callCount_;

    bool execute()
    {
        // Record start time
        clock_t start = clock();

        // ... perform computation ...

        // Accumulate elapsed time
        cpuTime_ += (clock() - start) / CLOCKS_PER_SEC;
        callCount_++;

        return true;
    }

    ~myFunctionObject()
    {
        // Print performance statistics on destruction
        Info << "Performance stats:" << nl
             << "  Total CPU time: " << cpuTime_ << " s" << nl
             << "  Number of calls: " << callCount_ << nl
             << "  Average time per call: "
             << (cpuTime_ / callCount_) << " s" << endl;
    }
};
```

📚 **คำอธิบายเชิงลึก:**

**แหล่งที่มา (Source):**
```
.applications/utilities/mesh/generation/foamyMesh/conformalVoronoiMesh/initialPointsMethod/initialPointsMethod/initialPointsMethod.C
```

**คำอธิบาย (Explanation):**
- `clock()` returns processor time ที่ใช้โดยโปรแกรม
- `CLOCKS_PER_SEC` แปลง clock ticks เป็น seconds
- Destructor เป็นที่ที่ดีสำหรับ print summary statistics

**แนวคิดสำคัญ (Key Concepts):**
1. **CPU Time**: เวลา processor ที่ใช้ (wall time อาจต่างจาก CPU time)
2. **Performance Metrics**: ตัวชี้วัดประสิทธิภาพของโค้ด
3. **Statistical Analysis**: การวิเคราะห์ข้อมูล performance

**2. Using Linux perf:**
```bash
# Profile CPU usage with call graph
perf record -g simpleFoam
perf report

# Profile memory allocations specifically
perf record -e malloc,simpleFoam
perf report
```

### Log File Analysis

**Structured logging:**
```cpp
// Create dedicated log file for functionObject
OFstream logFile
(
    mesh_.time().globalPath()/"myFunctionObject.log"
);

// Define structured logging format
logFile << "# Time  Operation  Status  Details" << nl;

// Helper function for structured logging
void logOperation(const word& operation, const word& status, const word& details)
{
    // Write timestamped log entry
    logFile << mesh_.time().timeName() << tab
            << operation << tab
            << status << tab
            << details << nl;
    
    // Flush immediately to ensure data is written
    logFile.flush();
}
```

📚 **คำอธิบายเชิงลึก:**

**แหล่งที่มา (Source):**
```
.applications/utilities/mesh/generation/foamyMesh/conformalVoronoiMesh/initialPointsMethod/initialPointsMethod/initialPointsMethod.C
```

**คำอธิบาย (Explanation):**
- `OFstream` เป็น OpenFOAM output stream class
- `globalPath()` returns full path ไปยัง case directory
- `flush()` บังคับให้เขียนข้อมูลทันที (สำคัญสำหรับ debugging)

**แนวคิดสำคัญ (Key Concepts):**
1. **Structured Logging**: การบันทึกข้อมูลแบบมีรูปแบบ
2. **Timestamping**: การบันทึกเวลาของ events
3. **Data Persistence**: การเก็บข้อมูลไว้วิเคราะห์ภายหลัง

## 6.8 Best Practices สำหรับ Error Prevention

### 1. Defensive Programming

```cpp
// Robust functionObject with comprehensive error handling
class robustFunctionObject : public functionObject
{
    bool execute() override
    {
        try
        {
            // Validate preconditions before proceeding
            if (!validatePreconditions())
            {
                return false;
            }

            // Perform main computation
            performComputation();

            // Validate results after computation
            if (!validateResults())
            {
                WarningIn("robustFunctionObject::execute")
                    << "Result validation failed" << endl;
                return false;
            }

            return true;
        }
        catch (const std::exception& e)
        {
            // Catch any exceptions and log them
            ErrorIn("robustFunctionObject::execute")
                << "Exception caught: " << e.what() << endl;
            return false;
        }
    }

private:
    // Check if all required conditions are met
    bool validatePreconditions()
    {
        return mesh_.foundObject<volScalarField>(fieldName_);
    }

    // Verify results are reasonable
    bool validateResults()
    {
        // Check for NaN, inf, or extremely large values
        const volScalarField& result = filteredField_();

        // gMax finds global maximum across all processors
        // mag returns magnitude
        if (gMax(mag(result.primitiveField())) > GREAT)
        {
            return false;
        }

        return true;
    }
};
```

📚 **คำอธิบายเชิงลึก:**

**แหล่งที่มา (Source):**
```
.applications/utilities/mesh/generation/foamyMesh/conformalVoronoiMesh/initialPointsMethod/initialPointsMethod/initialPointsMethod.C
```

**คำอธิบาย (Explanation):**
- **Defensive Programming**: เขียนโค้ดที่คาดการณ์และจัดการ error conditions
- **Precondition Validation**: ตรวจสอบว่า input ถูกต้องก่อนประมวลผล
- **Postcondition Validation**: ตรวจสอบว่า output มีความสมเหตุสมผล
- **Exception Handling**: จัดการ unexpected errors อย่างสง่างาม

**แนวคิดสำคัญ (Key Concepts):**
1. **Fail-Safe Design**: ออกแบบให้ fail อย่างปลอดภัยเมื่อเกิด error
2. **Validation Layers**: หลายชั้นของการตรวจสอบ
3. **Error Recovery**: การกลับสู่สถานะที่ปลอดภัย

### 2. Unit Testing Framework

```cpp
// Simple unit testing framework for functionObjects
class myFunctionObjectTest
{
public:
    // Run all test cases
    static void runAllTests()
    {
        testConstructor();
        testExecution();
        testErrorHandling();
        testMeshUpdate();
        Info << "All tests passed!" << endl;
    }

private:
    // Test constructor with various inputs
    static void testConstructor()
    {
        Info << "Testing constructor..." << endl;

        // Test normal construction with valid parameters
        dictionary validDict;
        validDict.add("fieldName", "U");
        validDict.add("threshold", 5.0);

        // Test with invalid parameters - should fail
        try
        {
            dictionary invalidDict;
            // Missing required parameters
            autoPtr<myFunctionObject> obj =
                myFunctionObject::New("test", runTime, invalidDict);
            
            // If we reach here, test failed - should have thrown error
            FatalErrorIn("myFunctionObjectTest::testConstructor")
                << "Should have thrown error for missing parameters"
                << exit(FatalError);
        }
        catch (const Foam::error&)
        {
            // Correctly caught expected error - test passed
            Info << "  ✓ Correctly rejected invalid parameters" << endl;
        }
    }
};
```

📚 **คำอธิบายเชิงลึก:**

**แหล่งที่มา (Source):**
```
.applications/utilities/mesh/generation/foamyMesh/conformalVoronoiMesh/initialPointsMethod/initialPointsMethod/initialPointsMethod.C
```

**คำอธิบาย (Explanation):**
- **Unit Testing**: การทดสอบแต่ละส่วนของโค้ดแยกจากกัน
- **Test Cases**: Scenarios ที่ต่างกันเพื่อทดสอบ functionality
- **Expected Failures**: Tests ที่คาดว่าจะ fail เมื่อ input ไม่ถูกต้อง

**แนวคิดสำคัญ (Key Concepts):**
1. **Test-Driven Development (TDD)**: เขียน tests ก่อนโค้ด
2. **Regression Testing**: ทดสอบว่า changes ไม่ได้ทำลาย functionality ที่มีอยู่
3. **Code Coverage**: วัดว่าโค้ดถูก test ครอบคลุมแค่ไหน

### 3. Documentation and Comments

```cpp
// Well-documented functionObject class
class wellDocumentedFunctionObject : public functionObject
{
    /*!
     * \brief Filter a scalar field based on threshold value
     *
     * This functionObject filters a volScalarField by keeping only
     * values above the specified threshold. All values below threshold
     * are set to zero.
     *
     * \param fieldName Name of the input field to filter
     * \param threshold Minimum value to keep in output field
     * \return True if filtering successful, false otherwise
     *
     * \warning Requires field to exist in mesh before calling
     * \warning Modifies field in-place - original values are lost
     *
     * \author Your Name
     * \date Year
     *
     * Example usage in controlDict:
     * \code
     * myFilter
     * {
     *     type thresholdFilter;
     *     fieldName U;
     *     threshold 5.0;
     * }
     * \endcode
     */
    bool execute() override;
};
```

📚 **คำอธิบายเชิงลึก:**

**แหล่งที่มา (Source):**
```
.applications/utilities/mesh/generation/foamyMesh/conformalVoronoiMesh/initialPointsMethod/initialPointsMethod/initialPointsMethod.C
```

**คำอธิบาย (Explanation):**
- **Doxygen Comments**: Special comment format สำหรับ generate documentation
- `\brief`: Short description ของ function/class
- `\param`: Document แต่ละ parameter
- `\return`: Document return value
- `\warning`: Important warnings สำหรับ users
- `\code` ... `\endcode`: Code examples

**แนวคิดสำคัญ (Key Concepts):**
1. **Self-Documenting Code**: โค้ดที่อธิบายตัวเองชัดเจน
2. **API Documentation**: Documents สำหรับ users ของ library/code
3. **Doxygen**: Tool สำหรับ generate documentation จาก comments

## 6.9 Troubleshooting Checklist

เมื่อเจอปัญหา ให้ตรวจสอบตามลำดับนี้:

**Phase 1: Compilation**
- [ ] Header files included ครบถ้วน
- [ ] Template specializations ถูกต้อง
- [ ] Virtual functions implemented ทั้งหมด
- [ ] `wmake` สำเร็จโดยไม่มี warnings

**Phase 2: Library Loading**
- [ ] Library file exists ใน `$FOAM_USER_LIBBIN`
- [ ] `addToRunTimeSelectionTable` macro present
- [ ] `libs("libXXX.so")` specified in controlDict
- [ ] `TypeName` matches `type` entry

**Phase 3: Runtime**
- [ ] Required fields exist ใน mesh
- [ ] Dictionary entries valid และ complete
- [ ] Mesh topology handled ถ้า dynamic mesh
- [ ] Parallel communication ถูกต้อง

**Phase 4: Output**
- [ ] Results written ถูกต้อง
- [ ] No memory leaks
- [ ] Performance acceptable

การเข้าใจข้อผิดพลาดทั่วไปเหล่านี้และเทคนิคการ debugging จะช่วยให้คุณพัฒนา OpenFOAM extensions ที่เสถียรและมีประสิทธิภาพ การใช้ best practices เหล่านี้จะลดเวลา debugging และเพิ่มความน่าเชื่อถือของโค้ดของคุณอย่างมาก