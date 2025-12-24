# Introduction to Time and Database Systems

> [!INFO] Overview
> This module explores the **Time** class and **objectRegistry** system — OpenFOAM's central data management infrastructure that coordinates temporal evolution and object storage throughout CFD simulations.

---

## 🌡️ Hook: The "Weather Station Network" Analogy

Imagine you are establishing a **national weather monitoring system**. You need to measure temperature across the entire country:

- **Individual weather stations** measure temperature at specific locations
- **Regional offices** aggregate data and manage local boundaries
- **National headquarters** coordinates everything and guarantees data consistency
- **Measurement units** (Celsius vs Fahrenheit) must be tracked to prevent errors

```mermaid
graph TD
    subgraph National_Level["National Headquarters (Time/runTime)"]
        T[Time Controller]
        T --> |broadcasts| DT[Time Signals]
    end

    subgraph Regional_Network["Regional Offices (objectRegistry)"]
        OR[Object Registry]
        OR --> |manages| REG1[Region 1 Data]
        OR --> |manages| REG2[Region 2 Data]
        OR --> |manages| REG3[Region 3 Data]
    end

    subgraph Local_Stations["Weather Stations (GeometricField)"]
        FS1[Field Station 1]
        FS2[Field Station 2]
        FS3[Field Station 3]
    end

    DT --> OR
    REG1 --> FS1
    REG2 --> FS2
    REG3 --> FS3

    FS1 --> |reports| OR
    FS2 --> |reports| OR
    FS3 --> |reports| OR
end
```
> **Figure 1:** อุปมาเปรียบเทียบระบบการจัดการข้อมูลของ OpenFOAM กับเครือข่ายสถานีตรวจอากาศระดับชาติ ซึ่งแสดงให้เห็นถึงการประสานงานระหว่างส่วนควบคุมกลาง สำนักงานภูมิภาค และสถานีตรวจวัดในพื้นที่

## 📊 Mapping to OpenFOAM Architecture

OpenFOAM's `GeometricField` is the **weather station network** for CFD data:

| Weather Station | OpenFOAM Field | Description |
|-----------------|----------------|-------------|
| Individual measurement point | `Field<Type>` | Raw data |
| Calibrated station | `DimensionedField` | With physical dimensions |
| Complete network | `GeometricField` | With boundary conditions |
| Temperature monitoring | `volScalarField` | Scalar values on mesh |
| Geographic map | `fvMesh` | Defines station locations |

**Real-world analogy**: Think of `GeometricField` as a **smart city infrastructure**:

- **Data pipes** (`Field`) transmit raw measurements
- **Unit converters** (`dimensionSet`) guarantee consistency
- **Zone managers** (`boundaryField`) handle local conditions
- **City map** (`fvMesh`) defines spatial layout

## 💻 Technical Implementation

The weather station analogy maps directly to OpenFOAM's field architecture:

```cpp
// Individual weather station = Field<Type>
Field<scalar> temperatureAtStation;

// Calibrated station with unit tracking = DimensionedField<scalar>
DimensionedField<scalar, volMesh> calibratedTemperature(
    "T",                                                                  // Field name
    dimensionSet(0, 0, 0, 1, 0, 0, 0),                                   // Temperature dimensions [K]
    temperatureValues                                                   // Field values
);

// Complete weather network = GeometricField
GeometricField<scalar, fvPatchField, volMesh> temperatureField(
    IOobject("T", runTime.timeName(), mesh, IOobject::MUST_READ),       // I/O object with time directory
    mesh                                                                // Mesh reference
);
```

> **📂 Source:** OpenFOAM implementation reference for field construction patterns can be found in:
> `.applications/solvers/multiphase/multiphaseEulerFoam/multiphaseCompressibleMomentumTransportModels/derivedFvPatchFields/alphatWallBoilingWallFunction/alphatWallBoilingWallFunctionFvPatchScalarField.C:70-94`

> **คำอธิบายภาษาไทย (Thai Explanation):**
>
> **แหล่งที่มา (Source):**
> โค้ดตัวอย่างนี้แสดงลาย签名้นของการสร้างฟิลด์ใน OpenFOAM ซึ่งสามารถพบได้ในไฟล์การ implement boundary condition ของ multiphaseEulerFoam solver
>
> **คำอธิบาย (Explanation):**
> - `Field<scalar>`: เป็นคลาสพื้นฐานสำหรับเก็บข้อมูลสเกลาร์ในหน่วยความจำ ไม่มีข้อมูลเกี่ยวกับตำแหน่งเชิงเรขาคณิต หรือหน่วยของฟิสิกส์
> - `DimensionedField<scalar, volMesh>`: เพิ่มความสามารถในการติดตามหน่วยฟิสิกส์ (dimensionSet) ซึ่งช่วยป้องกันความผิดพลาดในการคำนวณที่เกี่ยวข้องกับหน่วย
> - `GeometricField<scalar, fvPatchField, volMesh>`: ฟิลด์สมบูรณ์ที่มีทั้งค่าขอบเขต (boundary conditions) และข้อมูลเชิงเรขาคณิตบน mesh
>
> **แนวคิดสำคัญ (Key Concepts):**
> - **IOobject**: ใช้ในการกำหนดวิธีการอ่าน/เขียนข้อมูล และเชื่อมโยงฟิลด์กับเวลาปัจจุบันของจำลอง
> - **runTime.timeName()**: สร้างชื่อไดเรกทอรีตามเวลา (เช่น "0", "0.01", "0.02") สำหรับการบันทึกผลลัพธ์
> - **mesh**: อ้างอิงถึงโครงสร้างเชิงเรขาคณิตที่ฟิลด์ถูกกำหนด
> - **Template parameters**: `<scalar, fvPatchField, volMesh>` ระบุประเภทข้อมูล ประเภท boundary field และประเภท mesh

## 🧮 Mathematical Foundation

The field network spans a discretized computational domain $\Omega$:

$$\mathbf{u}(\mathbf{x},t) = \sum_{i=1}^{N} \mathbf{u}_i(t) \phi_i(\mathbf{x})$$

**Mathematical variables:**
- $\mathbf{u}_i(t)$ = Weather station measurement at position $\mathbf{x}_i$
- $\phi_i(\mathbf{x})$ = Interpolation basis function (network communication)
- $N$ = Total number of measurement points

## 🏢 Boundary Conditions as Regional Offices

Just as weather regional offices manage geographic boundaries with different conditions:

```cpp
// Set inlet boundary condition - fixed temperature
temperatureField.boundaryField()[0] == fixedValueFvPatchField<scalar>(
    temperatureField.boundaryField()[0],    // Reference to boundary patch
    300.0                                    // Constant temperature (K)
);

// Set outlet boundary condition - zero gradient
temperatureField.boundaryField()[1] == zeroGradientFvPatchField<scalar>(
    temperatureField.boundaryField()[1]     // Zero gradient means no change
);
```

```mermaid
graph LR
    subgraph Boundary_Conditions["Regional Offices (Boundary Conditions)"]
        BC1[Inlet Region]
        BC2[Outlet Region]
        BC3[Wall Regions]
    end

    subgraph Field_Internal["Internal Domain"]
        IF[Internal Field Values]
    end

    BC1 --> |Fixed: 300K| IF
    BC2 --> |Zero Gradient| IF
    BC3 --> |Adiabatic| IF
end
```
> **Figure 2:** การจัดการเงื่อนไขขอบเขตเสมือนสำนักงานภูมิภาคที่ควบคุมพฤติกรรมของข้อมูลในแต่ละโซนของโดเมนการคำนวณ

> **📂 Source:** Boundary condition implementation patterns reference:
> `.applications/solvers/multiphase/multiphaseEulerFoam/multiphaseCompressibleMomentumTransportModels/derivedFvPatchFields/alphatWallBoilingWallFunction/alphatWallBoilingWallFunctionFvPatchScalarField.C:294-674`

> **คำอธิบายภาษาไทย (Thai Explanation):**
>
> **แหล่งที่มา (Source):**
> โค้ดนี้แสดงรูปแบบการตั้งค่า boundary condition ซึ่งเป็นรูปแบบมาตรฐานที่พบได้ในการ implement derived boundary conditions ใน OpenFOAM
>
> **คำอธิบาย (Explanation):**
> - **boundaryField()**: คืนค่ารายการของ boundary patches ทั้งหมดที่มีอยู่ในฟิลด์
> - **fixedValueFvPatchField**: boundary condition ที่กำหนดค่าคงที่ที่ขอบเขต (เช่น อุณหภูมินำเข้า)
> - **zeroGradientFvPatchField**: boundary condition ที่ไม่มีการเปลี่ยนแปลงของค่าในทิศทางปกติ (normal direction)
> - **Patch indexing**: [0], [1] คือ index ของ boundary patches ที่กำหนดใน mesh (เช็คได้จาก boundary file)
>
> **แนวคิดสำคัญ (Key Concepts):**
> - **Boundary Conditions (เงื่อนไขขอบเขต)**: คือการระบุพฤติกรรมของฟิลด์ที่ผิวขอบเขตของโดเมนการคำนวณ
> - **Patch Selection**: แต่ละ patch สามารถมี boundary condition ที่แตกต่างกันได้
> - **Virtual Constructor Pattern**: การใช้ `==` operator เป็นวิธีการ assign boundary condition แบบ polymorphic
> - **Runtime Selection**: boundary conditions ถูกสร้างจาก dictionary ใน time directory

## 🔗 Mesh Integration

The `fvMesh` provides the geometric framework:

```cpp
// Create mesh object from case directory
fvMesh mesh(
    IOobject(
        "region0",                    // Region name
        runTime.timeName(),           // Current time directory
        runTime,                      // Time object reference
        IOobject::MUST_READ           // Read from disk
    )
);
```

**This mesh defines:**
- **Station positions** (cell centers)
- **Communication paths** (face connections)
- **Regional boundaries** (patch definitions)

> **📂 Source:** Mesh construction pattern reference:
> `.applications/utilities/parallelProcessing/reconstructPar/fvFieldReconstructor.C:56-93`

> **คำอธิบายภาษาไทย (Thai Explanation):**
>
> **แหล่งที่มา (Source):**
> รูปแบบการสร้าง mesh object นี้พบได้ใน utilities ที่ทำงานกับ mesh ใน OpenFOAM
>
> **คำอธิบาย (Explanation):**
> - **IOobject**: เป็นคลาสที่ใช้จัดการการอ่าน/เขียนไฟล์ โดยระบุชื่อไฟล์, ตำแหน่ง, และวิธีการเข้าถึงข้อมูล
> - **MUST_READ**: flag ที่ระบุว่า mesh จะต้องถูกอ่านจาก disk (จาก polyMesh directory)
> - **region0**: ชื่อของ mesh region (สำหรับ multi-region cases)
> - **runTime.timeName()**: ชี้ไปยัง time directory ปัจจุบัน
>
> **แนวคิดสำคัญ (Key Concepts):**
> - **Mesh Structure**: mesh ประกอบด้วย cells, faces, points และ patches
> - **Time Coordination**: mesh object ถูกเชื่อมโยงกับ time database
> - **Automatic I/O**: IOobject จัดการการค้นหาและอ่านไฟล์ mesh อัตโนมัติ
> - **Multi-region Support**: สามารถมีหลาย mesh regions ใน case เดียว

## 🔄 Data Flow Architecture

The weather station analogy extends to data flow:

### Data Flow Stages:
1. **Measurement collection**: Field values at cell centers
2. **Regional processing**: Boundary condition calculations
3. **National coordination**: Global field operations and solver integration

```cpp
// Stage 1: Local measurements - access internal field values
scalarField& T = temperatureField.primitiveFieldRef();

// Stage 2: Regional boundary conditions - update patch values
forAll(temperatureField.boundaryField(), patchI)
{
    // Get reference to boundary patch
    fvPatchScalarField& patchT = temperatureField.boundaryFieldRef()[patchI];
    
    // Update boundary condition coefficients
    patchT.updateCoeffs();
}

// Stage 3: National coordination - global field operations
fvScalarMatrix TEqn(
    fvm::ddt(T) +           // Time derivative
    fvm::div(phi, T) -      // Convection term
    fvm::laplacian(DT, T) == source  // Diffusion term with source
);

// Solve the equation system
TEqn.solve();
```

```mermaid
flowchart TD
    subgraph Level_1["Level 1: Local Measurements"]
        A1[Cell Center Values]
    end

    subgraph Level_2["Level 2: Regional Processing"]
        B1[Boundary Condition Updates]
        B2[Patch-specific Calculations]
    end

    subgraph Level_3["Level 3: National Coordination"]
        C1[Field Operations]
        C2[Solver Integration]
        C3[Global Reductions]
    end

    A1 --> B1
    A1 --> B2
    B1 --> C1
    B2 --> C1
    C1 --> C2
    C1 --> C3
end
```
> **Figure 3:** สถาปัตยกรรมการไหลของข้อมูลสามระดับ ตั้งแต่การวัดค่าในพื้นที่ การประมวลผลระดับภูมิภาค ไปจนถึงการประสานงานระดับชาติผ่านตัวแก้ปัญหา

> **📂 Source:** Field solver integration pattern reference:
> `.applications/solvers/multiphase/multiphaseEulerFoam/multiphaseCompressibleMomentumTransportModels/derivedFvPatchFields/fixedMultiPhaseHeatFlux/fixedMultiPhaseHeatFluxFvPatchScalarField.H`

> **คำอธิบายภาษาไทย (Thai Explanation):**
>
> **แหล่งที่มา (Source):**
> รูปแบบการสร้างและแก้สมการ solver equations นี้เป็นมาตรฐานใน OpenFOAM solvers
>
> **คำอธิบาย (Explanation):**
> - **primitiveFieldRef()**: คืนค่า reference ถึงค่าฟิลด์ภายใน (internal field values)
> - **boundaryFieldRef()**: คืนค่า reference ถึง boundary field ที่สามารถแก้ไขได้
> - **updateCoeffs()**: อัปเดตค่าสัมประสิทธิ์ของ boundary condition สำหรับเวลาปัจจุบัน
> - **fvScalarMatrix**: matrix equation สำหรับ scalar field (ระบบ linear equations)
> - **fvm::ddt(), fvm::div(), fvm::laplacian()**: finite volume method discretization operators
>
> **แนวคิดสำคัญ (Key Concepts):**
> - **Three-stage Architecture**: การแยกส่วนประมวลผลออกเป็น local, regional, และ global ช่วยเพิ่มประสิทธิภาพ
> - **Implicit Discretization**: fvm (finite volume method) ใช้สำหรับ implicit terms ในสมการ
> - **Matrix Assembly**: operators ต่างๆ จะถูก assemble รวมกันเป็น system of linear equations
> - **Solver Integration**: matrix จะถูกส่งไปยัง linear solver เพื่อหาคำตอบ
> - **Boundary-Interior Coupling**: ข้อมูลระหว่าง internal field และ boundaries ถูก synchronize อัตโนมัติ

This hierarchical structure enables OpenFOAM to efficiently handle complex CFD calculations while maintaining data consistency and proper physical units throughout the computational domain.

---

## 🏗️ Core Components

At the programming level, we encounter the following key classes:

### **1. `Time` (the `runTime` variable)**

Manages information about the past, present, and future of the simulation:

```cpp
// Create Time object for simulation control
Time runTime
(
    "root",         // Case root directory path
    "caseName",     // Name of the case
    "system",       // System dictionary folder
    "constant"      // Constant dictionary folder
);
```

**Key responsibilities:**
- Temporal control: `startTime`, `endTime`, `deltaT`
- Time directory management: `timeName()`, `timePath()`
- Simulation loop control: `runTime.loop()`, `runTime.write()`

> **📂 Source:** Time class initialization reference:
> `.applications/utilities/preProcessing/setWaves/setWaves.C`

> **คำอธิบายภาษาไทย (Thai Explanation):**
>
> **แหล่งที่มา (Source):**
> การใช้ Time class เป็นมาตรฐานในทุก OpenFOAM application
>
> **คำอธิบาย (Explanation):**
> - **Time object**: เป็นตัวควบคุมหลักของ temporal evolution ใน simulation
> - **Root directory**: ตำแหน่งที่ตั้งของ case folder
> - **Case name**: ชื่อของ case ที่ใช้สร้าง time directories
> - **System/constant folders**: directories ที่เก็บ configuration และ mesh data
>
> **แนวคิดสำคัญ (Key Concepts):**
> - **Temporal Database**: Time class จัดการ time directories และ checkpointing
> - **Simulation Loop**: ควบคุมการวนซ้ำของ simulation time steps
> - **Time Stepping Control**: จัดการ deltaT, start time, end time
> - **Output Control**: กำหนดเวลาที่จะบันทึกผลลัพธ์ (writeInterval)

### **2. `objectRegistry`**

Acts as a "phone book" or "database" storing entries for all objects created in the run:

```cpp
// Get reference to object registry from mesh
const objectRegistry& db = mesh.db();

// Lookup objects by name from registry
const volScalarField& p = db.lookupObject<volScalarField>("p");

// Store object in registry
regIOobject::store(pressureField);
```

**Key operations:**
- Object registration: `regIOobject::store()`
- Object lookup: `objectRegistry::lookupObject()`
- Name-based access: Enables flexible data sharing

> **📂 Source:** Object registry usage pattern reference:
> `.applications/solvers/multiphase/multiphaseEulerFoam/multiphaseCompressibleMomentumTransportModels/derivedFvPatchFields/alphatWallBoilingWallFunction/alphatWallBoilingWallFunctionFvPatchScalarField.C:302-303`

> **คำอธิบายภาษาไทย (Thai Explanation):**
>
> **แหล่งที่มา (Source):**
> การใช้ objectRegistry พบได้ทั่วไปใน OpenFOAM boundary conditions และ function objects
>
> **คำอธิบาย (Explanation):**
> - **objectRegistry**: เป็น container แบบ centralized ที่เก็บ references ถึง objects ทั้งหมด
> - **mesh.db()**: mesh object เป็นส่วนหนึ่งของ registry hierarchy
> - **lookupObject<T>()**: template method สำหรับค้นหา objects ตามชื่อและประเภท
> - **Type Safety**: template parameter ช่วย verify ประเภทของ object ที่ค้นหา
>
> **แนวคิดสำคัญ (Key Concepts):**
> - **Centralized Storage**: objects ทั้งหมดถูกลงทะเบียนใน registry เดียว
> - **Name-based Lookup**: ใช้ชื่อ (string) ในการค้นหา objects
> - **Hierarchical Registry**: มีหลายระดับของ registry (mesh, runTime, etc.)
> - **Inter-object Communication**: objects ต่างๆ สามารถค้นหาและเข้าถึงกันได้ผ่าน registry
> - **Memory Management**: registry ช่วยจัดการ lifetime ของ objects

### **3. `regIOobject`**

Base class for objects requiring storage in the Registry and disk I/O capabilities:

```cpp
// Base class definition for registered I/O objects
class regIOobject : public IOobject
{
    // Pure virtual method for automatic file writing
    virtual bool writeData(Ostream&) const = 0;

    // Registry management methods
    bool checkOut();    // Remove from registry
    bool store();       // Register in registry
};
```

**Examples:** `fvMesh`, `volScalarField`, `volVectorField`

> **📂 Source:** regIOobject implementation reference:
> `.applications/utilities/parallelProcessing/reconstructPar/fvFieldReconstructor.C`

> **คำอธิบายภาษาไทย (Thai Explanation):**
>
> **แหล่งที่มา (Source):**
> regIOobject เป็น base class สำคัญที่ใช้กันทั่วไปใน OpenFOAM
>
> **คำอธิบาย (Explanation):**
> - **regIOobject**: คือ "Registered I/O Object" - รวมความสามารถ registry และ I/O
> - **Inherits from IOobject**: ได้ความสามารถในการอ่าน/เขียนไฟล์มาจาก IOobject
> - **writeData()**: pure virtual method ที่ derived classes ต้อง implement
> - **checkOut()**: ลบ object ออกจาก registry (เมื่อไม่ใช้งานแล้ว)
> - **store()**: ลงทะเบียน object ใน registry (เมื่อสร้างใหม่)
>
> **แนวคิดสำคัญ (Key Concepts):**
> - **Automatic Registration**: objects ถูกลงทะเบียนอัตโนมัติเมื่อสร้าง
> - **Automatic I/O**: สามารถเขียน/อ่านไฟล์อัตโนมัติผ่าน time database
> - **Polymorphic Base**: หลายประเภทของ objects สืบทอดจากคลาสนี้
> - **Lifetime Management**: registry จัดการ memory ผ่าน reference counting
> - **Time Coordination**: objects ถูกเขียนเมื่อ runTime.write() ถูกเรียก

These systems give OpenFOAM extremely high flexibility, as each code component can work together through "deposit and retrieve" data access from the central Registry.

---

## 📋 Module Structure

This module covers the following interconnected systems:

### **Topics Covered:**

1. **Time Management** (`Time` class)
   - Temporal discretization control
   - Time step management
   - Time directory handling

2. **Object Registry** (`objectRegistry`)
   - Centralized object storage
   - Name-based lookup system
   - Inter-object communication

3. **Registered I/O** (`regIOobject`)
   - Automatic file reading/writing
   - Object registration protocol
   - Database consistency

4. **Field Integration**
   - How fields interact with time systems
   - Automatic time directory management
   - Solver integration patterns

### **Learning Outcomes:**

After completing this module, you will understand:

> [!CHECK] Learning Objectives
> - ✅ How OpenFOAM manages temporal evolution through the `Time` class
> - ✅ How the `objectRegistry` provides centralized data management
> - ✅ How `regIOobject` enables automatic I/O and object registration
> - ✅ How these systems integrate with `GeometricField` for CFD simulations
> - ✅ How to write code that properly interacts with time and database systems

### **Prerequisites:**

> [!WARNING] Required Knowledge
> - C++ templates and inheritance
> - Basic finite volume method concepts
> - OpenFOAM field types (`volScalarField`, `volVectorField`)
> - Familiarity with OpenFOAM case structure

---

## 🎯 Why This Matters

Understanding Time and Database systems is crucial because:

1. **Every OpenFOAM simulation** uses these systems implicitly
2. **Custom boundary conditions** require proper registry interaction
3. **Function objects** depend on object lookup mechanisms
4. **Parallel computations** rely on coordinated time management
5. **Data output** is controlled through time and registry systems

The weather station analogy provides an intuitive mental model for these sophisticated software engineering concepts that underpin all of OpenFOAM's functionality.

---

## 📚 Further Reading

- [[02_Time_Class_Detailed]] - Deep dive into `Time` class functionality
- [[03_Object_Registry_Mechanisms]] - Registry implementation details
- [[04_Field_Database_Integration]] - How fields use database systems
- [[05_Advanced_Time_Control]] - Adaptive time stepping and sub-cycling