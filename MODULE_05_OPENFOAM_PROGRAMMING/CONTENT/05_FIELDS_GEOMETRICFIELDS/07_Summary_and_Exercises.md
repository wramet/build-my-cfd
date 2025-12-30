# GeometricFields - Summary and Exercises

สรุปและแบบฝึกหัด GeometricFields — ฝึกทำเพื่อเข้าใจจริง

---

## 🎯 Learning Objectives | วัตถุประสงค์การเรียนรู้

**Learning Objectives:**
- Master GeometricField creation and initialization patterns for real solver development
- Develop proficiency in field operations (component access, mathematical operations, calculus)
- Understand boundary field manipulation for implementing boundary conditions
- Apply fvc:: calculus operators to solve practical CFD problems
- Build custom field writing capabilities for post-processing and debugging
- Establish complete understanding of the field-mesh-dimensions integration

**เป้าหมายการเรียนรู้:**
- เชี่ยวชาญการสร้างและเริ่มต้น GeometricField สำหรับการพัฒนา solver จริง
- เชี่ยวชาญการดำเนินการกับฟิลด์ (เข้าถึงส่วนประกอบ, การดำเนินการทางคณิตศาสตร์, แคลคูลัส)
- เข้าใจการจัดการ boundary field สำหรับสร้างเงื่อนไขขอบ
- ใช้ fvc:: calculus operators แก้ปัญหา CFD จริง
- เขียน custom field สำหรับ post-processing และ debugging
- สร้างความเข้าใจที่สมบูรณ์เกี่ยวกับการรวม field-mesh-dimensions

---

## 📋 Knowledge Prerequisites | ความรู้พื้นฐานที่ต้องมี

**Essential Background:**
- **Foundation Primitives** ([01_FOUNDATION_PRIMITIVES/02_Basic_Primitives.md](../../01_FOUNDATION_PRIMITIVES/02_Basic_Primitives.md:1)): Smart pointers, memory management
- **Dimensioned Types** ([02_DIMENSIONED_TYPES/01_Introduction.md](../../02_DIMENSIONED_TYPES/01_Introduction.md:1)): dimensionSet, dimensional consistency
- **Mesh Classes** ([04_MESH_CLASSES/05_fvMesh.md](../04_MESH_CLASSES/05_fvMesh.md:1)): volMesh, boundaryMesh structure
- **Field Hierarchy** ([03_Inheritance_Hierarchy.md](03_Inheritance_Hierarchy.md:1)): Field relationships

---

## 🔍 Section Overview | ภาพรวมหัวข้อ

```
GeometricFields Capstone
│
├── Summary Section (สรุปภาพรวม)
│   ├── Concept Integration Matrix
│   ├── Template Structure Reference
│   └── Common Pitfalls Summary
│
├── Exercise Suite (ชุดแบบฝึกหัด)
│   ├── Ex 1: Field Creation (การสร้างฟิลด์)
│   ├── Ex 2: Field Operations (การดำเนินการกับฟิลด์)
│   ├── Ex 3: Boundary Access (การเข้าถึงขอบ)
│   ├── Ex 4: Calculus Operations (การดำเนินการแคลคูลัส)
│   └── Ex 5: Custom Field Writing (การเขียนฟิลด์กำหนดเอง)
│
└── Integration Maps (แผนที่การเชื่อมโยง)
    ├── Concept Interconnections
    ├── Real-World Application Mapping
    └── Skill Progression Tracking
```

---

## Part 1: Comprehensive Summary | สรุปภาพรวม

### ทำมา Why This Summary Matters | ทำไมสรุปนี้สำคัญ

**CFD Consequences:**
- **Incomplete integration** → Bugs from mixing incompatible field types, dimension mismatches
- **Template confusion** → Compilation errors from wrong PatchField/GeoMesh combinations
- **Memory leaks** → Poor solver performance and crashes from incorrect field management
- **Wrong boundary access** → Solver crashes from const/non-const confusion
- **Missing calculus understanding** → Incorrect discretization and wrong physics

**OpenFOAM Reality:**
- Real solvers use GeometricField as primary data structure
- Every boundary condition is a PatchField specialization
- All fvc:: operations return temporary GeometricField objects
- Template errors are the #1 compilation issue for beginners

---

### 1.1 Concept Integration Matrix | แมตริกซ์การรวมแนวคิด

#### Core Concepts Hierarchy

```
GeometricField<Type, PatchField, GeoMesh>
│
├── Type (Data Type Layer)
│   ├── scalar: p, T, k, epsilon
│   ├── vector: U, grad(p)
│   ├── symmTensor: R (Reynolds stress)
│   ├── tensor: grad(U)
│   └── sphericalTensor: I (identity)
│
├── PatchField (Boundary Layer)
│   ├── fvPatchField: Cell-based BC (volFields)
│   ├── fvsPatchField: Face-based BC (surfaceFields)
│   └── Specialized BCs: fixedValue, zeroGradient, etc.
│
└── GeoMesh (Mesh Topology Layer)
    ├── volMesh: Cell-centered storage (finite volume)
    ├── surfaceMesh: Face-centered storage (fluxes)
    └── pointMesh: Point-centered storage (rare)
```

#### Dimensional Consistency Framework

| **Field** | **Dimension** | **Physical Meaning** |
|-----------|---------------|----------------------|
| `volScalarField p` | [M L⁻¹ T⁻²] | Pressure (Pa) |
| `volVectorField U` | [L T⁻¹] | Velocity (m/s) |
| `volScalarField T` | [Θ] | Temperature (K) |
| `surfaceScalarField phi` | [L³ T⁻¹] | Volume flux (m³/s) |
| `volScalarField rho` | [M L⁻³] | Density (kg/m³) |
| `volScalarField nu` | [L² T⁻¹] | Kinematic viscosity (m²/s) |

---

### 1.2 Template Structure Reference | โครงสร้างเทมเพลต

#### Complete Template Signature

```cpp
template<
    class Type,              // Data type: scalar, vector, tensor
    class PatchField,        // BC type: fvPatchField, fvsPatchField
    class GeoMesh            // Mesh type: volMesh, surfaceMesh
>
class GeometricField
: public DimensionedField<Type, GeoMesh>
, public LduBoundaryField<Type, PatchField, GeoMesh>
{
    // Inherits from:
    // 1. DimensionedField: Storage + dimensions + internal field
    // 2. LduBoundaryField: Boundary field handling + LDU matrix support
    
    // Core components:
    // - Internal field: Field<Type> (cell-centered)
    // - Boundary field: PtrList<PatchField<Type>> (per-patch)
    // - Mesh reference: const GeoMesh&
};
```

#### Common Specializations

```cpp
// Volume (cell-centered) scalar fields
using volScalarField = GeometricField<scalar, fvPatchField, volMesh>;

// Volume vector fields
using volVectorField = GeometricField<vector, fvPatchField, volMesh>;

// Surface (face-centered) scalar fields
using surfaceScalarField = GeometricField<scalar, fvsPatchField, surfaceMesh>;
```

#### Type Definition Flowchart

```
┌─────────────────────────────────────────────────────────────┐
│              Choose Field Specialization                     │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
         Cell-centered?                 Face-centered?
         (Finite Volume)                  (Fluxes)
              │                               │
              ▼                               ▼
    ┌─────────────────┐           ┌─────────────────┐
    │    volMesh      │           │  surfaceMesh    │
    └─────────────────┘           └─────────────────┘
              │                               │
      ┌───────┴───────┐               ┌───────┴───────┐
      │               │               │               │
   scalar?        vector?         scalar?       (rare)
      │               │               │
      ▼               ▼               ▼
┌──────────┐   ┌──────────┐   ┌──────────────┐
│volScalar │   │volVector │   │surfaceScalar │
│  Field   │   │  Field   │   │    Field     │
└──────────┘   └──────────┘   └──────────────┘
```

---

### 1.3 Field-Mesh Integration | การรวมฟิลด์กับเมช

#### Storage Architecture

```cpp
volScalarField p
(
    IOobject("p", runTime.timeName(), mesh, IOobject::MUST_READ),
    mesh
);

// Internal Architecture:
// ┌────────────────────────────────────────────────────────┐
// │  DimensionedField<scalar, volMesh>                     │
// │  ┌──────────────────────────────────────────────────┐  │
// │  │ dimensions: [M L⁻¹ T⁻²]                          │  │
// │  │ field_: List<scalar> (size = nCells)             │  │
// │  │   - cell 0: 101325.0                             │  │
// │  │   - cell 1: 101330.0                             │  │
// │  │   - ...                                          │  │
// │  └──────────────────────────────────────────────────┘  │
// │                                                         │
// │  LduBoundaryField<scalar, fvPatchField, volMesh>       │
// │  ┌──────────────────────────────────────────────────┐  │
// │  │ boundaryField_: PtrList<fvPatchField<scalar>>    │  │
// │  │   - [0]: inlet (fixedValueFvPatchField)          │  │
// │  │   - [1]: outlet (zeroGradientFvPatchField)       │  │
// │  │   - [2]: walls (noSlipFvPatchField)              │  │
// │  └──────────────────────────────────────────────────┘  │
// └────────────────────────────────────────────────────────┘
```

#### Memory Layout

```
Physical Domain Memory Layout:
┌───────────────────────────────────────────────────────┐
│  Cell-centered (volScalarField)                        │
│  ┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐         │
│  │ 0 │ 1 │ 2 │ 3 │ 4 │ 5 │ 6 │ 7 │ 8 │ 9 │...│         │
│  └───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘         │
│           ↑                                             │
│           Internal field (contiguous array)             │
└───────────────────────────────────────────────────────┘

Boundary Field Memory Layout:
┌───────────────────────────────────────────────────────┐
│  Patch 0 (inlet)      │ Patch 1 (outlet) │ ...        │
│  ┌───┬───┬───┬───┐    │ ┌───┬───┬───┬───┐             │
│  │ 0 │ 1 │ 2 │...│    │ │ 0 │ 1 │ 2 │...│             │
│  └───┴───┴───┴───┘    │ └───┴───┴───┴───┘             │
│  Face values          │  Face values                  │
└───────────────────────────────────────────────────────┘
```

---

### 1.4 Common Pitfalls Summary | สรุปปัญหาที่พบบ่อย

#### Top 5 Critical Pitfalls

| **#** | **Pitfall** | **Symptom** | **Solution** |
|-------|-------------|-------------|--------------|
| **1** | Wrong IOobject read option | Solver crash, missing field | Use MUST_READ for required fields, READ_IF_PRESENT for optional |
| **2** | Confusing boundaryField() vs boundaryFieldRef() | Compilation error: cannot assign | Use boundaryFieldRef() for modification, boundaryField() for read |
| **3** | Dimension mismatch in operations | Dimension error at runtime | Check dimensions with .dimensions() before operations |
| **4** | Not writing custom fields | Field missing in post-processing | Set IOobject::AUTO_WRITE and call .write() |
| **5** | Incorrect patch ID | Segfault or wrong BC | Always check findPatchID() != -1 before use |

#### Pitfall Prevention Checklist

```cpp
// ✅ Safe Field Creation Pattern
volScalarField T
(
    IOobject
    (
        "T",                                    // Unique name
        runTime.timeName(),                     // Current time
        mesh,                                   // Valid mesh
        IOobject::MUST_READ,                    // Clear read intent
        IOobject::AUTO_WRITE                    // Auto output
    ),
    mesh                                        // Mesh constructor
);

// ✅ Safe Boundary Access Pattern
label patchID = mesh.boundaryMesh().findPatchID("inlet");
if (patchID != -1)
{
    // Read (const access)
    const scalarField& patchT = T.boundaryField()[patchID];
    
    // Write (non-const access)
    T.boundaryFieldRef()[patchID] == 300.0;
}
else
{
    FatalErrorInFunction << "Patch 'inlet' not found" << abort(FatalError);
}

// ✅ Safe Dimension Check
if (p.dimensions() != dimPressure)
{
    WarningInFunction << "Field 'p' does not have pressure dimensions";
}

// ✅ Safe Field Writing
customField.write();
Info << "Wrote customField at time " << runTime.timeName() << endl;
```

---

## Part 2: Exercise Suite | ชุดแบบฝึกหัด

### ทำมา Why These Exercises Build Real Skills | ทำไมแบบฝึกหัดเหล่านี้สร้างทักษะจริง

**Real-World Mapping:**
- **Exercise 1** → Every solver creates fields (momentum, energy, turbulence)
- **Exercise 2** → All CFD codes need field algebra (Reynolds number, Courant number)
- **Exercise 3** → Boundary conditions are 50% of CFD setup difficulty
- **Exercise 4** → fvc:: operations are the core of finite volume discretization
- **Exercise 5** → Custom fields enable debugging and custom outputs

**Skill Progression:**
```
Basic Creation (Ex 1)
        ↓
Algebraic Operations (Ex 2)
        ↓
Boundary Manipulation (Ex 3)
        ↓
Calculus Operations (Ex 4)
        ↓
Custom Output (Ex 5)
        ↓
Ready for custom solver development
```

**OpenFOAM Developer Reality:**
- 90% of solver development is field manipulation
- Boundary condition bugs cause 60% of solver failures
- Every production solver uses custom output fields
- Debugging requires writing intermediate fields

---

### Exercise 1: Field Creation and Initialization

#### 🎯 Exercise Objectives | วัตถุประสงค์แบบฝึกหัด

**Learning Goals:**
- Create volScalarField and volVectorField from files
- Initialize fields with constant values
- Set correct IOobject options for different use cases
- Understand field registration in the object registry

**ทักษะที่ได้รับ:**
- สร้าง volScalarField และ volVectorField จากไฟล์
- เริ่มต้นฟิลด์ด้วยค่าคงที่
- ตั้งค่า IOobject options ที่เหมาะสม
- เข้าใจการลงทะเบียนฟิลด์ใน object registry

---

#### 📝 Task Specification | รายละเอียดงาน

**Scenario:** You are developing a custom solver for conjugate heat transfer. You need to:
1. Read temperature field from initial conditions
2. Create velocity field with zero initial velocity
3. Create a custom property field (thermal conductivity)

**Implementation:**

```cpp
// ===== PART A: Read existing field from file =====
volScalarField T
(
    IOobject
    (
        "T",                                    // Field name
        runTime.timeName(),                     // Time directory (e.g., "0")
        mesh,                                   // Mesh database
        IOobject::MUST_READ,                    // MUST exist in "0/" directory
        IOobject::AUTO_WRITE                    // Write automatically each timestep
    ),
    mesh                                        // Required constructor argument
);

// ===== PART B: Create field with initial value =====
volVectorField U
(
    IOobject
    (
        "U",                                    // Field name
        runTime.timeName(),
        mesh,
        IOobject::READ_IF_PRESENT,              // Optional: read if file exists
        IOobject::AUTO_WRITE
    ),
    mesh,
    dimensionedVector                          // Initial value specification
    (
        "U",                                    // Name
        dimVelocity,                            // Dimensions: [L T⁻¹]
        vector::zero                            // Value: (0, 0, 0)
    )
);

// ===== PART C: Create custom property field =====
volScalarField kappa
(
    IOobject
    (
        "kappa",                                // Thermal conductivity
        runTime.timeName(),
        mesh,
        IOobject::NO_READ,                      // Don't read from file
        IOobject::AUTO_WRITE
    ),
    mesh,
    dimensionedScalar("kappa", dimless, 0.6)   // dimensionless, initial value 0.6
);

// ===== PART D: Verify creation =====
Info << "Created fields:" << nl
     << "  T: " << T.size() << " cells, dimensions: " << T.dimensions() << nl
     << "  U: " << U.size() << " cells, dimensions: " << U.dimensions() << nl
     << "  kappa: " << kappa.size() << " cells, dimensions: " << kappa.dimensions() << nl
     << endl;
```

---

#### ✅ Expected Output and Validation | เกณฑ์การตรวจสอบ

**Console Output:**
```
Created fields:
  T: 1000 cells, dimensions: [0 0 0 1 0 0 0]
  U: 1000 cells, dimensions: [0 1 -1 0 0 0 0]
  kappa: 1000 cells, dimensions: [0 0 0 0 0 0 0]
```

**Validation Criteria:**
1. ✓ Field T reads from `0/T` file without errors
2. ✓ Field U initializes to (0, 0, 0) everywhere
3. ✓ Field kappa is created (no file read)
4. ✓ All fields report correct sizes matching mesh.nCells()
5. ✓ Dimensions match expected SI units

**Self-Check Commands:**
```bash
# After running solver, check output files
ls -la 0/T 0/U    # Should exist
ls -la 0/kappa    # Should NOT exist (NO_READ)
ls -la 1e-05/     # All fields should be present (AUTO_WRITE)
```

---

#### 🧩 Common Issues and Solutions | ปัญหาที่พบบ่อยและวิธีแก้

| **Error** | **Cause** | **Solution** |
|-----------|-----------|--------------|
| `cannot open file` | File `0/T` doesn't exist | Create initial file or use READ_IF_PRESENT |
| `dimension error` | Wrong dimensions in initialization | Check dimVelocity, dimless, etc. |
| `field already exists` | Duplicate field name | Ensure unique names across all fields |
| `wrong number of cells` | Field size mismatch | Field auto-sizes to mesh, should match |

---

### Exercise 2: Field Operations and Algebra

#### 🎯 Exercise Objectives | วัตถุประสงค์แบบฝึกหัด

**Learning Goals:**
- Perform magnitude calculations on vector fields
- Extract vector components
- Implement mathematical combinations of fields
- Apply dimension checking to field operations

**ทักษะที่ได้รับ:**
- คำนวณขนาดของฟิลด์เวกเตอร์
- แยกส่วนประกอบของเวกเตอร์
- ดำเนินการคณิตศาสตร์ระหว่างฟิลด์
- ตรวจสอบมิติของการดำเนินการ

---

#### 📝 Task Specification | รายละเอียดงาน

**Scenario:** In your heat transfer solver, you need to calculate:
1. Velocity magnitude for Courant number calculation
2. X-velocity component for visualization
3. Dynamic pressure field for force calculations

**Implementation:**

```cpp
// ===== ASSUMPTION: Fields U and rho already exist =====
// volVectorField U(mesh, ...);    // Velocity field
// volScalarField rho(mesh, ...);  // Density field

// ===== PART A: Velocity Magnitude =====
volScalarField magU
(
    IOobject
    (
        "magU",                                // Output field name
        runTime.timeName(),
        mesh,
        IOobject::NO_READ,
        IOobject::AUTO_WRITE
    ),
    mag(U)                                    // mag(U) = sqrt(U·U)
);

// ===== PART B: Component Extraction =====
volScalarField Ux
(
    IOobject("Ux", runTime.timeName(), mesh, IOobject::NO_READ, IOobject::AUTO_WRITE),
    U.component(0)                            // 0=x, 1=y, 2=z
);

volScalarField Uy
(
    IOobject("Uy", runTime.timeName(), mesh, IOobject::NO_READ, IOobject::AUTO_WRITE),
    U.component(1)
);

// ===== PART C: Dynamic Pressure Calculation =====
// q_dynamic = 0.5 * rho * |U|²
volScalarField dynP
(
    IOobject("dynP", runTime.timeName(), mesh, IOobject::NO_READ, IOobject::AUTO_WRITE),
    0.5 * rho * magSqr(U)                     // magSqr(U) = U·U
);

// ===== PART D: Reynolds Number Field =====
// Re = (rho * |U| * L) / mu
// Assume characteristic length L = 0.1 m, dynamic viscosity mu = 1e-5
dimensionedScalar L("L", dimLength, 0.1);
dimensionedScalar mu("mu", dimensionSet(1, -1, -1, 0, 0, 0, 0), 1e-5);

volScalarField Re
(
    IOobject("Re", runTime.timeName(), mesh, IOobject::NO_READ, IOobject::AUTO_WRITE),
    (rho * magU * L) / mu
);

// ===== PART E: Print Statistics =====
Info << "Field statistics:" << nl
     << "  magU: min=" << min(magU).value() << ", max=" << max(magU).value() << nl
     << "  dynP: min=" << min(dynP).value() << ", max=" << max(dynP).value() << nl
     << "  Re:   min=" << min(Re).value() << ", max=" << max(Re).value() << nl
     << endl;
```

---

#### ✅ Expected Output and Validation | เกณฑ์การตรวจสอบ

**Console Output Example:**
```
Field statistics:
  magU: min=0.0, max=5.23
  dynP: min=0.0, max=13745.5
  Re:   min=0.0, max=523000
```

**Validation Criteria:**
1. ✓ `magU ≥ 0` everywhere (magnitude is non-negative)
2. ✓ `magSqr(U) == magU * magU` (mathematical consistency)
3. ✓ `Ux` and `Uy` are scalar fields with correct dimensions [L T⁻¹]
4. ✓ `dynP` has dimensions [M L⁻¹ T⁻²] (pressure units)
5. ✓ `Re` is dimensionless [0 0 0 0 0 0 0]

**Dimensional Analysis:**
```
magU:            [L T⁻¹]
magSqr(U):       [L² T⁻²]
rho:             [M L⁻³]
dynP = 0.5*rho*magSqr(U):
                 [M L⁻³] * [L² T⁻²] = [M L⁻¹ T⁻²] ✓ (pressure)

Re = (rho*magU*L)/mu:
     [M L⁻³][L T⁻¹][L] / [M L⁻¹ T⁻¹]
     = [M L⁻¹ T⁻¹] / [M L⁻¹ T⁻¹] = [1] ✓ (dimensionless)
```

---

#### 🔍 Concept Check | ทบทวนแนวคิด

<details>
<summary><b>Why use magSqr(U) instead of mag(U)*mag(U)?</b></summary>

**Mathematical equivalence:** `magSqr(U) = mag(U) * mag(U)`

**Performance difference:**
- `magSqr(U)`: Single calculation `U·U`
- `mag(U)*mag(U)`: Calculates `sqrt(U·U)`, then squares it = wasted sqrt operation

**Best practice:** Use `magSqr(U)` when you need squared magnitude (common in kinetic energy, dynamic pressure)
</details>

<details>
<summary><b>How to extract all 3 components efficiently?</b></summary>

```cpp
// Method 1: Individual component() calls (3 iterations)
volScalarField Ux(U.component(0));
volScalarField Uy(U.component(1));
volScalarField Uz(U.component(2));

// Method 2: Single iteration (more efficient)
volScalarField Ux(mesh, IOobject("Ux", ...), dimensionedScalar("Ux", dimVelocity, 0));
volScalarField Uy(mesh, IOobject("Uy", ...), dimensionedScalar("Uy", dimVelocity, 0));
volScalarField Uz(mesh, IOobject("Uz", ...), dimensionedScalar("Uz", dimVelocity, 0));

forAll(U, cellI)
{
    Ux[cellI] = U[cellI].x();
    Uy[cellI] = U[cellI].y();
    Uz[cellI] = U[cellI].z();
}
```
</details>

---

### Exercise 3: Boundary Field Access and Modification

#### 🎯 Exercise Objectives | วัตถุประสงค์แบบฝึกหัด

**Learning Goals:**
- Find patch IDs by name
- Access boundary field values (read-only)
- Modify boundary field values (read-write)
- Distinguish between boundaryField() and boundaryFieldRef()

**ทักษะที่ได้รับ:**
- ค้นหา patch ID จากชื่อ
- เข้าถึงค่า boundary field (อ่านอย่างเดียว)
- แก้ไขค่า boundary field (อ่านและเขียน)
- แยกความแตกต่างระหว่าง boundaryField() และ boundaryFieldRef()

---

#### 📝 Task Specification | รายละเอียดงาน

**Scenario:** Your conjugate heat transfer solver needs to:
1. Read inlet temperature from a table (time-varying)
2. Set wall temperature to a fixed value (isothermal wall)
3. Implement adiabatic (zero gradient) condition at outlet

**Implementation:**

```cpp
// ===== ASSUMPTION: Field T already exists =====
// volScalarField T(mesh, ...);

// ===== PART A: Find Patch IDs =====
label inletID  = mesh.boundaryMesh().findPatchID("inlet");
label outletID = mesh.boundaryMesh().findPatchID("outlet");
label wallID   = mesh.boundaryMesh().findPatchID("walls");

// Safety check: Ensure patches exist
if (inletID == -1 || outletID == -1 || wallID == -1)
{
    FatalErrorInFunction
        << "Missing required boundary patches:" << nl
        << "  inlet:  " << (inletID != -1 ? "found" : "MISSING") << nl
        << "  outlet: " << (outletID != -1 ? "found" : "MISSING") << nl
        << "  walls:  " << (wallID != -1 ? "found" : "MISSING") << nl
        << abort(FatalError);
}

// ===== PART B: Read Boundary Values (const access) =====
const scalarField& Tin = T.boundaryField()[inletID];

Info << "Inlet temperature:" << nl
     << "  min: " << min(Tin) << nl
     << "  max: " << max(Tin) << nl
     << "  avg: " << average(Tin) << nl
     << endl;

// ===== PART C: Modify Boundary Values (non-const access) =====
// Case C1: Fixed temperature at walls
T.boundaryFieldRef()[wallID] == 350.0;  // == operator for BC evaluation

// Case C2: Time-varying inlet temperature
scalar currentTime = runTime.value();
scalar T_inlet = 300.0 + 50.0 * sin(2.0 * 3.14159 * currentTime / 10.0);

// Option 1: Direct assignment (creates fixedValue)
T.boundaryFieldRef()[inletID] == T_inlet;

// Option 2: Loop over faces (for spatial variation)
scalarField& Tinlet = T.boundaryFieldRef()[inletID];
forAll(Tinlet, faceI)
{
    // Example: linear temperature profile across inlet
    const face& f = mesh.boundaryMesh()[inletID][faceI];
    point faceCenter = f.center(mesh.points());
    Tinlet[faceI] = 300.0 + 10.0 * faceCenter.x();  // Varies with x-coordinate
}

// ===== PART D: Zero Gradient at Outlet =====
// Zero gradient means: boundary value = adjacent cell value
// This is the DEFAULT if BC is set to zeroGradient
// Explicit enforcement (if needed):
T.boundaryFieldRef()[outletID] == T.boundaryField()[outletID].patchInternalField();

// ===== PART E: Print Boundary Summary =====
Info << "Boundary conditions applied:" << nl
     << "  inlet:  T = " << T_inlet << " K (time-varying)" << nl
     << "  outlet: zeroGradient (adiabatic)" << nl
     << "  walls:  T = 350.0 K (isothermal)" << nl
     << endl;
```

---

#### ✅ Expected Output and Validation | เกณฑ์การตรวจสอบ

**Console Output Example:**
```
Inlet temperature:
  min: 295.3
  max: 304.7
  avg: 300.0

Boundary conditions applied:
  inlet:  T = 312.4 K (time-varying)
  outlet: zeroGradient (adiabatic)
  walls:  T = 350.0 K (isothermal)
```

**Validation Criteria:**
1. ✓ All required patches found (no FatalError)
2. ✓ Inlet temperature varies with time (`T_inlet != constant`)
3. ✓ Wall temperature set to exactly 350.0 K
4. ✓ Outlet temperature equals adjacent cell values (zero gradient)
5. ✓ Temperature is physically reasonable (T > 0 K everywhere)

**ParaView Visualization Check:**
1. Open case in ParaView
2. Apply "Extract Block" filter to see boundaries
3. Color plot by "T"
4. Walls should show uniform 350.0 K
5. Inlet should show temperature variation
6. Outlet should show gradient perpendicular to boundary

---

#### 🚨 Critical Safety Rules | กฎความปลอดภัยสำคัญ

```cpp
// ❌ WRONG: Using boundaryField() for modification
T.boundaryField()[wallID] == 350.0;  // COMPILATION ERROR!
// Error: cannot assign to const reference

// ❌ WRONG: Using assignment operator for BC
T.boundaryFieldRef()[wallID] = 350.0;  // RUNTIME ERROR!
// Wrong: Overwrites entire BC object, loses patchField type

// ✅ CORRECT: Using boundaryFieldRef() with == operator
T.boundaryFieldRef()[wallID] == 350.0;  // Correct BC evaluation

// ✅ CORRECT: Loop with boundaryFieldRef()
scalarField& Twall = T.boundaryFieldRef()[wallID];
forAll(Twall, faceI)
{
    Twall[faceI] = 350.0;  // Direct assignment in loop is OK
}
```

---

#### 🧩 Common Issues and Solutions | ปัญหาที่พบบ่อย

| **Error** | **Cause** | **Solution** |
|-----------|-----------|--------------|
| `patchID == -1` | Patch name doesn't exist | Check `boundary` file in `constant/polyMesh` |
| `cannot assign to const` | Used `boundaryField()` instead of `boundaryFieldRef()` | Use `boundaryFieldRef()` for modification |
| `segmentation fault` | Accessed invalid patch ID | Always check `findPatchID() != -1` |
| `wrong BC type` | Assignment overwrites BC object | Use `==` operator for BC evaluation |

---

### Exercise 4: Calculus Operations with fvc::

#### 🎯 Exercise Objectives | วัตถุประสงค์แบบฝึกหัด

**Learning Goals:**
- Compute gradient of scalar fields (∇p, ∇T)
- Calculate divergence of vector fields (∇·U, ∇·φ)
- Apply Laplacian operator (∇²T, ∇²U)
- Understand finite volume discretization concepts

**ทักษะที่ได้รับ:**
- คำนวณ gradient ของฟิลด์สเกลาร์
- คำนวณ divergence ของฟิลด์เวกเตอร์
- ใช้ตัวดำเนินการ Laplacian
- เข้าใจแนวคิดการ discretization แบบ finite volume

---

#### 📝 Task Specification | รายละเอียดงาน

**Scenario:** You are implementing a simple diffusion solver. The governing equation is:
```
∂T/∂t = α ∇²T
```
Where α is thermal diffusivity. You need to compute the Laplacian of temperature.

**Implementation:**

```cpp
// ===== ASSUMPTION: Fields T and alpha already exist =====
// volScalarField T(mesh, ...);           // Temperature field
// volScalarField alpha(mesh, ...);       // Thermal diffusivity
// surfaceScalarField phi(mesh, ...);     // Flux field

// ===== PART A: Gradient Operation =====
// Compute ∇T (temperature gradient)
// Result: volVectorField (vector at cell centers)
volVectorField gradT
(
    IOobject("gradT", runTime.timeName(), mesh, IOobject::NO_READ, IOobject::AUTO_WRITE),
    fvc::grad(T)                           // ∇T = [∂T/∂x, ∂T/∂y, ∂T/∂z]
);

Info << "Temperature gradient magnitude:" << nl
     << "  min: " << min(mag(gradT)).value() << " K/m" << nl
     << "  max: " << max(mag(gradT)).value() << " K/m" << nl
     << endl;

// ===== PART B: Divergence Operation =====
// Compute ∇·U (velocity divergence, for continuity check)
// Result: volScalarField (scalar at cell centers)
volScalarField divU
(
    IOobject("divU", runTime.timeName(), mesh, IOobject::NO_READ, IOobject::AUTO_WRITE),
    fvc::div(phi)                          // ∇·φ (flux divergence)
);

Info << "Continuity error (∇·U):" << nl
     << "  min: " << min(divU).value() << " 1/s" << nl
     << "  max: " << max(divU).value() << " 1/s" << nl
     << "  avg: " << average(divU).value() << " 1/s" << nl
     << endl;

// ===== PART C: Laplacian Operation =====
// Compute ∇²T (Laplacian of temperature)
// Result: volScalarField (scalar at cell centers)
volScalarField lapT
(
    IOobject("lapT", runTime.timeName(), mesh, IOobject::NO_READ, IOobject::AUTO_WRITE),
    fvc::laplacian(alpha, T)               // ∇·(α∇T)
);

Info << "Temperature Laplacian (∇²T):" << nl
     << "  min: " << min(lapT).value() << " K/m²" << nl
     << "  max: " << max(lapT).value() << " K/m²" << nl
     << endl;

// ===== PART D: Curl Operation (Vorticity) =====
// Compute ω = ∇×U (vorticity)
// Result: volVectorField (vector at cell centers)
volVectorField vorticity
(
    IOobject("omega", runTime.timeName(), mesh, IOobject::NO_READ, IOobject::AUTO_WRITE),
    fvc::curl(U)                           // ∇×U
);

Info << "Vorticity magnitude:" << nl
     << "  min: " << min(mag(vorticity)).value() << " 1/s" << nl
     << "  max: " << max(mag(vorticity)).value() << " 1/s" << nl
     << endl;

// ===== PART E: Combined Operations (Example: Nusselt Number) =====
// Nu = -L * (∂T/∂n) / ΔT
// At wall: ∂T/∂n = n·∇T
label wallID = mesh.boundaryMesh().findPatchID("hotWall");
if (wallID != -1)
{
    // Get surface normal gradient at wall
    surfaceVectorField gradTf(fvc::interpolate(gradT));
    const surfaceVectorField& Sf = mesh.Sf();  // Face area vectors
    const surfaceScalarField& magSf = mesh.magSf();
    
    // Compute normal gradient
    surfaceScalarField dTdn(gradTf & Sf / magSf);
    
    // Get wall face values
    const scalarField& Twall = T.boundaryField()[wallID];
    const scalarField& dTdnWall = dTdn.boundaryField()[wallID];
    
    Info << "Wall heat transfer:" << nl
         << "  dT/dn: min=" << min(dTdnWall) << ", max=" << max(dTdnWall) << nl
         << endl;
}
```

---

#### ✅ Expected Output and Validation | เกณฑ์การตรวจสอบ

**Console Output Example:**
```
Temperature gradient magnitude:
  min: 0.0 K/m
  max: 1250.3 K/m

Continuity error (∇·U):
  min: -1.2e-05 1/s
  max: 1.5e-05 1/s
  avg: 2.3e-07 1/s

Temperature Laplacian (∇²T):
  min: -45.2 K/m²
  max: 52.8 K/m²

Vorticity magnitude:
  min: 0.0 1/s
  max: 125.4 1/s
```

**Validation Criteria:**
1. ✓ `gradT` is a volVectorField with dimensions [Θ L⁻¹]
2. ✓ `divU` should be ≈ 0 for incompressible flow (continuity)
3. ✓ `lapT` has dimensions [Θ L⁻²] (K/m²)
4. ✓ `vorticity` has dimensions [T⁻¹] (1/s)
5. ✓ All values are physically reasonable (no inf/nan)

**Physical Consistency Checks:**
```
✓ Gradient: ∇T points from cold → hot (opposite to heat flow)
✓ Divergence: ∇·U ≈ 0 for incompressible flow
✓ Laplacian: ∇²T < 0 in regions where T is maximum
✓ Vorticity: |ω| ≈ 0 in potential flow core
```

---

#### 🔍 Mathematical Background | พื้นฐานคณิตศาสตร์

**Finite Volume Discretization:**

| **Operator** | **Continuous** | **OpenFOAM** | **Discretized** |
|--------------|----------------|--------------|-----------------|
| Gradient | ∇T | `fvc::grad(T)` | Σ(Tf × Sf) / Vcell |
| Divergence | ∇·φ | `fvc::div(phi)` | Σ(φf · Sf) / Vcell |
| Laplacian | ∇²T | `fvc::laplacian(α,T)` | ∇·(α∇T) |
| Curl | ∇×U | `fvc::curl(U)` | ∇×U |

**Where:**
- `Tf`: Face temperature (interpolated from cells)
- `Sf`: Face area vector (normal × area)
- `Vcell`: Cell volume
- `φf`: Face flux

**Implementation Details:**
```cpp
// fvc::grad(T) implementation (simplified)
forAll(cells, cellI)
{
    vector gradT_cell = vector::zero;
    const cell& c = cells[cellI];
    
    forAll(c, faceI)
    {
        label faceI = c[faceI];
        scalar Tf = interpolate(T, faceI);  // Linear interpolation
        vector Sf = mesh.Sf()[faceI];        // Face area vector
        gradT_cell += Tf * Sf;               // Accumulate
    }
    gradT[cellI] = gradT_cell / mesh.V()[cellI];  // Divide by volume
}
```

---

#### 🧩 Common Issues and Solutions | ปัญหาที่พบบ่อย

| **Error** | **Cause** | **Solution** |
|-----------|-----------|--------------|
| `dimension error` | Field dimensions incompatible | Check `p.dimensions()` vs expected |
| `wrong field type` | Expected volScalarField but got volVectorField | Check operator return type |
| `NaN values` | Zero cell volumes or bad mesh | Check mesh quality with `checkMesh` |
| `wrong sign** | Confused about normal direction | `Sf` points OUT of owner cell |

---

### Exercise 5: Custom Field Creation and Output

#### 🎯 Exercise Objectives | วัตถุประสงค์แบบฝึกหัด

**Learning Goals:**
- Create custom fields for debugging and analysis
- Implement cell-by-cell field initialization
- Write custom fields to disk for post-processing
- Design output fields for specific engineering metrics

**ทักษะที่ได้รับ:**
- สร้าง custom fields สำหรับ debugging และวิเคราะห์
- กำหนดค่าเริ่มต้นฟิลด์ทีละเซลล์
- เขียนฟิลด์กำหนดเองลงดิสก์
- ออกแบบฟิลด์ output สำหรับเมตริกทางวิศวกรรม

---

#### 📝 Task Specification | รายละเอียดงาน

**Scenario:** You are debugging a turbulent flow solver. You need to output:
1. Cell ID field (for identifying problematic cells)
2. Courant number field (for stability analysis)
3. Y+ field (for turbulence model validation)
4. Custom vorticity magnitude field

**Implementation:**

```cpp
// ===== ASSUMPTION: Standard fields exist =====
// volVectorField U(mesh, ...);
// volScalarField rho(mesh, ...);
// volScalarField nu(mesh, ...);  // Kinematic viscosity
// surfaceScalarField phi(mesh, ...);

// ===== PART A: Cell ID Field (for debugging) =====
volScalarField cellID
(
    IOobject
    (
        "cellID",                               // Field name
        runTime.timeName(),
        mesh,
        IOobject::NO_READ,                      // Never read from file
        IOobject::AUTO_WRITE                    // Always write
    ),
    mesh,
    dimensionedScalar("cellID", dimless, 0)    // Initialize to 0
);

// Assign cell ID to each cell
forAll(cellID, cellI)
{
    cellID[cellI] = scalar(cellI);             // Simple: cellID = cell index
}

Info << "Created cellID field with " << cellID.size() << " cells" << endl;

// ===== PART B: Courant Number Field =====
// Co = |U|Δt/Δx (dimensionless)
volScalarField Co
(
    IOobject("Co", runTime.timeName(), mesh, IOobject::NO_READ, IOobject::AUTO_WRITE),
    mesh,
    dimensionedScalar("Co", dimless, 0)
);

scalar deltaT = runTime.deltaTValue();          // Time step size

forAll(Co, cellI)
{
    scalar deltaX = pow(mesh.V()[cellI], 1.0/3.0);  // Approx cell size
    scalar magU_cell = mag(U[cellI]);
    
    if (deltaX > SMALL)
    {
        Co[cellI] = magU_cell * deltaT / deltaX;
    }
    else
    {
        Co[cellI] = 0.0;  // Avoid division by zero
    }
}

Info << "Courant number: min=" << min(Co).value()
     << ", max=" << max(Co).value()
     << ", avg=" << average(Co).value() << endl;

// ===== PART C: Y+ Field (wall distance) =====
// y+ = u*·y/ν, where u* = sqrt(τw/ρ)
volScalarField yPlus
(
    IOobject("yPlus", runTime.timeName(), mesh, IOobject::NO_READ, IOobject::AUTO_WRITE),
    mesh,
    dimensionedScalar("yPlus", dimless, 0)
);

// Get wall shear stress from turbulence model
// (Assuming wall functions are used)
const volScalarField::Boundary& wallShearStress =
    turbulence->wallShearStress();  // Returns τw at walls

const volScalarField::Boundary& nutBd = turbulence->nut()().boundaryField();
const volScalarField::Boundary& nuBd = nu.boundaryField();

forAll(yPlus.boundaryField(), patchI)
{
    const fvPatchScalarField& ypPatch = yPlus.boundaryFieldRef()[patchI];
    
    if (isA<wallFvPatch>(mesh.boundary()[patchI]))
    {
        const scalarField& tauw = wallShearStress[patchI];
        const scalarField& nutw = nutBd[patchI];
        const scalarField& nuw = nuBd[patchI];
        
        scalarField& yp = ypPatch;
        
        forAll(tauw, faceI)
        {
            scalar uStar = sqrt(mag(tauw[faceI]));  // Friction velocity
            scalar y = wallDist[patchI][faceI];     // Distance to wall
            yp[faceI] = uStar * y / (nuw[faceI] + nutw[faceI]);
        }
    }
}

Info << "Y+ range: min=" << min(yPlus).value()
     << ", max=" << max(yPlus).value() << endl;

// ===== PART D: Custom Vorticity Magnitude =====
// ω = ∇×U (already computed in Exercise 4)
volScalarField magVorticity
(
    IOobject("magVorticity", runTime.timeName(), mesh, IOobject::NO_READ, IOobject::AUTO_WRITE),
    mag(fvc::curl(U))                     // Magnitude of vorticity vector
);

Info << "Vorticity magnitude: min=" << min(magVorticity).value()
     << ", max=" << max(magVorticity).value() << endl;

// ===== PART E: Write All Custom Fields =====
cellID.write();
Co.write();
yPlus.write();
magVorticity.write();

Info << "Custom fields written at time " << runTime.timeName() << endl;
```

---

#### ✅ Expected Output and Validation | เกณฑ์การตรวจสอบ

**Console Output Example:**
```
Created cellID field with 5000 cells
Courant number: min=0.0, max=0.45, avg=0.12
Y+ range: min=0.5, max=125.3
Vorticity magnitude: min=0.0, max=185.2
Custom fields written at time 0.01
```

**Validation Criteria:**
1. ✓ `cellID` values range from 0 to nCells-1
2. ✓ `Co < 1.0` everywhere (CFL condition for stability)
3. ✓ `yPlus` at walls is in valid range (y+ > 0, typically 30 < y+ < 300 for wall functions)
4. ✓ `magVorticity ≥ 0` everywhere (magnitude is non-negative)
5. ✓ All fields appear in time directories (e.g., `0.01/`)

**ParaView Visualization Check:**
1. Open case in ParaView
2. Apply "CellID" field → Should show spatial distribution of cell IDs
3. Apply "Co" field → Check regions where Co > 0.5 (potential instability)
4. Apply "yPlus" field → Check wall y+ values for turbulence model validity
5. Apply "magVorticity" → Identify high-vorticity regions (shear layers, wakes)

---

#### 🔍 Real-World Application Use Cases | กรณีใช้งานจริง

**Use Case 1: Mesh Quality Analysis**
```cpp
volScalarField cellAspectRatio
(
    IOobject("aspectRatio", ...),
    mesh,
    dimensionedScalar("AR", dimless, 0)
);

forAll(cellAspectRatio, cellI)
{
    scalar maxEdge = maxEdgeLength(cellI);  // User-defined function
    scalar minEdge = minEdgeLength(cellI);
    cellAspectRatio[cellI] = maxEdge / (minEdge + SMALL);
}
// Visualize in ParaView to find skewed cells
```

**Use Case 2: Solver Performance Monitoring**
```cpp
volScalarField nIterations
(
    IOobject("nIters", ...),
    mesh,
    dimensionedScalar("nIters", dimless, 0)
);

// After pressure solver loop
nIterations = pEqn.nIterations();  // Assuming solver returns iterations
// Identify regions requiring more iterations
```

**Use Case 3: Heat Transfer Coefficient**
```cpp
volScalarField htc
(
    IOobject("heatTransferCoeff", ...),
    mesh,
    dimensionedScalar("h", dimensionSet(1, 0, -3, -1, 0), 0)
);

// h = q / (Twall - Tref)
label wallID = mesh.boundaryMesh().findPatchID("heatedWall");
scalarField& hWall = htc.boundaryFieldRef()[wallID];
const scalarField& Twall = T.boundaryField()[wallID];
scalar Tref = 300.0;  // Reference temperature

forAll(hWall, faceI)
{
    scalar q = heatFlux[faceI];  // From energy equation
    hWall[faceI] = q / (Twall[faceI] - Tref);
}
```

---

#### 🧩 Common Issues and Solutions | ปัญหาที่พบบ่อย

| **Error** | **Cause** | **Solution** |
|-----------|-----------|--------------|
| `field not written` | Missing `AUTO_WRITE` or `.write()` call | Set `IOobject::AUTO_WRITE` and call `.write()` |
| `wrong dimensions` | Incorrect `dimensionedScalar` specification | Check dimensionSet matches physical meaning |
| `division by zero` | Cell volume or distance is zero | Add `+ SMALL` to denominator |
| `inconsistent field size` | Field not initialized with mesh | Always pass mesh to constructor |

---

## Part 3: Integration Maps | แผนที่การเชื่อมโยง

### 3.1 Concept Interconnections | การเชื่อมโยงแนวคิด

#### GeometricField Dependencies

```
GeometricField Architecture
│
├── Foundation Primitives (Module 1)
│   ├── Smart Pointers (04_Smart_Pointers.md)
│   │   └── GeometricField uses autoPtr for temporary fields
│   ├── Basic Types (02_Basic_Primitives.md)
│   │   └── scalar, vector, tensor are core Type parameters
│   └── Containers (05_Containers.md)
│       └── Field<Type> = List<Type> with geometric awareness
│
├── Dimensioned Types (Module 2)
│   ├── dimensionSet (01_Introduction.md)
│   │   └── Enforces dimensional consistency in operations
│   ├── DimensionedField (03_Implementation_Mechanisms.md)
│   │   └── Base class: storage + dimensions + internal field
│   └── Template Metaprogramming (04_Template_Metaprogramming.md)
│       └── Compile-time dimension checking
│
├── Mesh Classes (Module 4)
│   ├── polyMesh (04_polyMesh.md)
│   │   └── Topological mesh structure
│   ├── fvMesh (05_fvMesh.md)
│   │   └── Finite volume mesh (stores boundary, cell centers)
│   └── Boundary Mesh
│       └── Patch definitions for boundaryField
│
└── Field Hierarchy (This Module)
    ├── Field<Type> (03_Inheritance_Hierarchy.md)
    │   └── Base: List<Type> + dimensions
    ├── DimensionedField
    │   └── Adds mesh + IOobject
    └── GeometricField
        └── Adds boundary conditions + calculus operations
```

#### Knowledge Flow for Solver Development

```
Step 1: Foundation → Understand memory management
Step 2: Dimensions → Ensure dimensional consistency
Step 3: Mesh → Know where data lives (cells vs faces)
Step 4: Fields → Store and manipulate physical quantities
Step 5: Discretization → Apply fvc:: operators (This module)
Step 6: Solvers → Build complete PDE solvers
```

---

### 3.2 Real-World Application Mapping | การจับคู่แอปพลิเคชันจริง

#### Exercise → OpenFOAM Solver Mapping

| **Exercise** | **Real Solver** | **Application** |
|--------------|-----------------|-----------------|
| **Ex 1: Field Creation** | `createFields.H` in all solvers | Initialize rho, U, p, T, k, epsilon |
| **Ex 2: Field Operations** | `CourantNo.H` | Time step control in transient solvers |
| **Ex 3: Boundary Access** | `setInitialDeltaT.H` | Modify BCs for time-varying conditions |
| **Ex 4: Calculus Operations** | `UEqn.H`, `TEqn.H` | Discretize momentum, energy equations |
| **Ex 5: Custom Fields** | `createCustomFields.H` | Output y+, htc, vorticity for analysis |

#### Specific Solver Examples

**Example 1: SimpleFoam (Steady Turbulent Flow)**
```cpp
// From simpleFoam/createFields.H
volScalarField p
(
    IOobject("p", runTime.timeName(), mesh, IOobject::MUST_READ, IOobject::AUTO_WRITE),
    mesh
);

volVectorField U
(
    IOobject("U", runTime.timeName(), mesh, IOobject::MUST_READ, IOobject::AUTO_WRITE),
    mesh
);

// Ex 2: Field operations
#include "calculatePhi.H"  // phi = linearInterpolate(rho*U) & mesh.Sf

// Ex 4: Calculus operations
tmp<fvVectorMatrix> tUEqn(fvm::div(phi, U) - fvm::laplacian(nu, U));
```

**Example 2: BuoyantSimpleFoam (Heat Transfer)**
```cpp
// Ex 1: Temperature field
volScalarField T
(
    IOobject("T", runTime.timeName(), mesh, IOobject::MUST_READ, IOobject::AUTO_WRITE),
    mesh
);

// Ex 3: Boundary modification (time-varying)
label hotWallID = mesh.boundaryMesh().findPatchID("hotWall");
T.boundaryFieldRef()[hotWallID] == T_hot + 10.0 * sin(runTime.value());

// Ex 4: Energy equation Laplacian
solve(fvm::div(phi, T) - fvm::laplacian(alpha, T));
```

**Example 3: Custom Solver (Species Transport)**
```cpp
// Ex 5: Custom field for species mass fraction
volScalarField Y
(
    IOobject("Y", runTime.timeName(), mesh, IOobject::MUST_READ, IOobject::AUTO_WRITE),
    mesh
);

// Ex 2: Field operations (diffusion coefficient)
volScalarField D("D", D0 * (1.0 + Y));  // Concentration-dependent diffusion

// Ex 4: Species transport equation
solve(fvm::div(phi, Y) - fvm::laplacian(D, Y));
```

---

### 3.3 Skill Progression Tracking | การติดตามความก้าวหน้า

#### Competency Levels

```
Level 1: Beginner (Foundation)
├── Can create basic volScalarField, volVectorField
├── Understands IOobject parameters
└── Can read/write fields to disk

Level 2: Intermediate (Operations)
├── Can perform field algebra (mag, component, etc.)
├── Can access and modify boundary fields
├── Understands fvc:: basic operations (grad, div, laplacian)
└── Can create simple custom output fields

Level 3: Advanced (Solver Development)
├── Can implement complete PDE solvers
├── Can create custom boundary conditions
├── Understands fvm:: vs fvc:: operations
├── Can optimize field operations for performance
└── Can debug complex field interactions

Level 4: Expert (Production Solvers)
├── Can design new solver architectures
├── Can implement advanced turbulence models
├── Can optimize parallel field operations
├── Can develop custom discretization schemes
└── Can mentor others in field usage
```

#### Self-Assessment Checklist

**After completing this module, you should be able to:**

- [ ] Create volScalarField and volVectorField from files or with initial values
- [ ] Correctly set IOobject read/write options
- [ ] Compute magnitude, components, and field combinations
- [ ] Check field dimensions before operations
- [ ] Find patch IDs by name and validate they exist
- [ ] Read boundary values using boundaryField()
- [ ] Modify boundary values using boundaryFieldRef()
- [ ] Compute gradient (∇), divergence (∇·), and Laplacian (∇²)
- [ ] Understand finite volume discretization concepts
- [ ] Create custom output fields for debugging
- [ ] Calculate derived quantities (Courant number, y+, vorticity)
- [ ] Write custom fields to disk for ParaView visualization
- [ ] Debug common field-related errors
- [ ] Map field operations to solver development tasks

**If you checked ALL boxes:** You are ready for custom solver development!

**If you missed ANY boxes:** Review the relevant exercise and try the variations.

---

## Part 4: Quick Reference | คู่มืออ้างอิงรวดเร็ว

### 4.1 Field Type Reference | อ้างอิงประเภทฟิลด์

#### Common Field Specializations

| **Type** | **Storage** | **Location** | **Common Use Cases** | **Example** |
|----------|-------------|--------------|----------------------|-------------|
| `volScalarField` | Cell | Cell centers | Pressure, temperature, turbulence | `p`, `T`, `k`, `epsilon` |
| `volVectorField` | Cell | Cell centers | Velocity, gradients | `U`, `grad(T)` |
| `volTensorField` | Cell | Cell centers | Velocity gradients | `grad(U)` |
| `surfaceScalarField` | Face | Face centers | Volume flux, mass flux | `phi`, `massFlux` |
| `surfaceVectorField` | Face | Face centers | Face-centered vectors | `Uf` |
| `pointScalarField` | Point | Mesh points | Point data (rare) | Mesh motion |

#### Dimensional Constants

```cpp
// Common OpenFOAM dimensions
dimensionSet(0, 0, 0, 1, 0, 0, 0)  // Temperature [Θ]
dimensionSet(1, -1, -2, 0, 0, 0, 0) // Pressure [M L⁻¹ T⁻²]
dimensionSet(0, 1, -1, 0, 0, 0, 0)  // Velocity [L T⁻¹]
dimensionSet(0, 2, -1, 0, 0, 0, 0)  // Kinematic viscosity [L² T⁻¹]
dimensionSet(1, -3, 0, 0, 0, 0, 0)  // Density [M L⁻³]

// Named constants
dimPressure     // [M L⁻¹ T⁻²]
dimVelocity     // [L T⁻¹]
dimDensity      // [M L⁻³]
dimLength       // [L]
dimTime         // [T]
dimTemperature  // [Θ]
dimless         // [0 0 0 0 0 0 0]
```

---

### 4.2 Operation Reference | อ้างอิงการดำเนินการ

#### Field Operations

| **Category** | **Operation** | **Code** | **Return Type** |
|--------------|---------------|----------|-----------------|
| **Magnitude** | Vector magnitude | `mag(U)` | `volScalarField` |
| **Magnitude Squared** | Squared magnitude | `magSqr(U)` | `volScalarField` |
| **Component** | X-component | `U.component(0)` | `volScalarField` |
| **Component** | Y-component | `U.component(1)` | `volScalarField` |
| **Component** | Z-component | `U.component(2)` | `volScalarField` |
| **Sum** | Field addition | `p1 + p2` | `volScalarField` |
| **Product** | Scalar × Field | `0.5 * rho * U` | `volVectorField` |
| **Division** | Field / Scalar | `U / magU` | `volVectorField` |

#### Calculus Operations

| **Operator** | **Mathematical** | **OpenFOAM** | **Input** | **Output** |
|--------------|------------------|--------------|-----------|------------|
| Gradient | ∇T | `fvc::grad(T)` | `volScalarField` | `volVectorField` |
| Gradient | ∇U | `fvc::grad(U)` | `volVectorField` | `volTensorField` |
| Divergence | ∇·φ | `fvc::div(phi)` | `surfaceScalarField` | `volScalarField` |
| Divergence | ∇·U | `fvc::div(U)` | `volVectorField` | `volScalarField` |
| Laplacian | ∇²T | `fvc::laplacian(alpha, T)` | `scalar, volScalarField` | `volScalarField` |
| Curl | ∇×U | `fvc::curl(U)` | `volVectorField` | `volVectorField` |
| Interpolate | T at faces | `fvc::interpolate(T)` | `volScalarField` | `surfaceScalarField` |

---

### 4.3 IOobject Options | ตัวเลือก IOobject

#### Read Options

```cpp
IOobject::MUST_READ        // File MUST exist, fatal error if missing
IOobject::READ_IF_PRESENT  // Read if exists, otherwise use default value
IOobject::NO_READ          // Never read, always use default value
```

#### Write Options

```cpp
IOobject::AUTO_WRITE       // Automatically write at each time step
IOobject::NO_WRITE         // Never write (debug fields, intermediates)
```

#### Constructor Pattern

```cpp
IOobject
(
    "fieldName",           // 1. Field name (unique)
    runTime.timeName(),    // 2. Time directory (e.g., "0", "1e-05")
    mesh,                  // 3. Object registry (database)
    IOobject::MUST_READ,   // 4. Read option
    IOobject::AUTO_WRITE   // 5. Write option
)
```

---

### 4.4 Boundary Field Access | การเข้าถึง Boundary Field

#### Access Patterns

```cpp
// Find patch by name
label patchID = mesh.boundaryMesh().findPatchID("patchName");
if (patchID == -1) FatalErrorInFunction << "Patch not found" << abort(FatalError);

// Read-only access (const)
const scalarField& patchValues = field.boundaryField()[patchID];

// Read-write access (non-const)
scalarField& patchValues = field.boundaryFieldRef()[patchID];

// Direct BC assignment (recommended)
field.boundaryFieldRef()[patchID] == newValue;

// Loop over faces
forAll(patchValues, faceI)
{
    patchValues[faceI] = customCalculation(faceI);
}
```

#### Common Boundary Conditions

| **BC Name** | **Type** | **Behavior** |
|-------------|----------|--------------|
| `fixedValue` | Dirichlet | Fixed value at boundary |
| `zeroGradient` | Neumann | Zero gradient (∂φ/∂n = 0) |
| `fixedGradient` | Neumann | Fixed gradient |
| `mixed` | Robin | Mixed (αφ + β∂φ/∂n = γ) |
| `calculated` | Computed | Value from expression |
| `empty` | None | 2D or symmetry boundaries |

---

### 4.5 Common Macros and Loops | มาโครและลูปทั่วไป

#### OpenFOAM Macros

```cpp
// Iterate over all cells/elements
forAll(field, i)
{
    field[i] = ...;  // i = 0 to field.size()-1
}

// Iterate over all cells (explicit type)
forAll(volScalarField, cellI)
{
    T[cellI] = ...;
}

// Iterate over boundary faces
forAll(patchField, faceI)
{
    patchField[faceI] = ...;
}

// Reverse iteration
forAllReverse(field, i)
{
    // i = field.size()-1 down to 0
}

// Iterate over internal cells
for (label cellI = 0; cellI < mesh.nInternalCells(); cellI++)
{
    // Only internal cells (not boundary cells)
}
```

#### Mesh Iteration

```cpp
// Cell iteration
forAll(mesh.cells(), cellI)
{
    const cell& c = mesh.cells()[cellI];
    label nFaces = c.nFaces();  // Number of faces in this cell
}

// Face iteration
forAll(mesh.faces(), faceI)
{
    const face& f = mesh.faces()[faceI];
    label nPoints = f.nPoints();  // Number of points in this face
}

// Patch iteration
forAll(mesh.boundaryMesh(), patchI)
{
    const polyPatch& patch = mesh.boundaryMesh()[patchI];
    word patchName = patch.name();
    label nFaces = patch.size();
}
```

---

## Part 5: Concept Check | ทบทวนแนวคิด

### 🧠 Concept Review Questions | คำถามทบทวนแนวคิด

<details>
<summary><b>1. What are the 5 IOobject constructor arguments and their purposes?</b></summary>

**Answer:**
1. **name**: Field identifier (e.g., "T", "U", "p")
2. **instance**: Time directory (e.g., `runTime.timeName()` = "0", "1e-05")
3. **registry**: Object database (typically `mesh` for fields)
4. **readOption**: MUST_READ, READ_IF_PRESENT, or NO_READ
5. **writeOption**: AUTO_WRITE or NO_WRITE

**Physical Meaning:**
- IOobject connects field data to disk files and mesh database
- Read/write control determines persistence and I/O behavior
- Registry enables field lookup by name in solvers
</details>

<details>
<summary><b>2. What is the difference between boundaryField() and boundaryFieldRef()?</b></summary>

**Answer:**
- **boundaryField()**: Returns `const` reference (read-only access)
  - Use for reading boundary values
  - Cannot modify BC through this accessor
  
- **boundaryFieldRef()**: Returns non-const reference (read-write access)
  - Use for modifying boundary values
  - Allows BC manipulation and assignment

**Example:**
```cpp
// Read (const)
const scalarField& Tin = T.boundaryField()[inletID];

// Write (non-const)
T.boundaryFieldRef()[inletID] == 300.0;
```

**Why it matters:**
- Prevents accidental modification of BCs when reading
- Compiler enforces const-correctness
- Catches bugs at compile-time, not runtime
</details>

<details>
<summary><b>3. How does the forAll macro differ from a standard for loop?</b></summary>

**Answer:**
```cpp
// Standard C++ for loop
for (label i = 0; i < field.size(); i++)
{
    field[i] = ...;
}

// OpenFOAM forAll macro
forAll(field, i)
{
    field[i] = ...;
}

// They are IDENTICAL after preprocessing
// forAll(field, i) expands to:
// for (Foam::label i=0; i < (field).size(); i++)
```

**Benefits:**
- More concise syntax (less boilerplate)
- Explicitly shows iteration over field elements
- OpenFOAM coding standard convention

**Related macros:**
- `forAllReverse(field, i)`: Iterate backwards
- `forAll(mesh.C(), cellI)`: Iterate over cell centers
</details>

<details>
<summary><b>4. Why must we use `==` operator when setting boundary conditions?</b></summary>

**Answer:**
The `==` operator in OpenFOAM boundary fields **does not mean equality comparison**. Instead, it **triggers boundary condition evaluation**.

```cpp
// ❌ WRONG: Assignment operator
T.boundaryFieldRef()[wallID] = 350.0;  // Overwrites BC object!

// ✅ CORRECT: Equality operator (BC evaluation)
T.boundaryFieldRef()[wallID] == 350.0;  // Evaluates BC
```

**Technical Details:**
- `operator=` would replace the entire fvPatchField object
- `operator==` calls `patchField::operator==(const scalar&)` which evaluates the BC
- This allows BCs to maintain their type (fixedValue, zeroGradient, etc.)

**Physical Meaning:**
- `==` means "evaluate this expression to get boundary values"
- BC is re-evaluated at every time step or when explicitly called
</details>

<details>
<summary><b>5. What is the finite volume discretization of ∇T (gradient)?</b></summary>

**Answer:**
In the finite volume method, the gradient at cell centers is computed using Gauss's theorem:

```
∫V ∇T dV = ∮S T n dS

∇T = (1/V) ∑(Tf × Sf)
```

**Where:**
- `Tf`: Temperature at face centers (interpolated from adjacent cells)
- `Sf`: Face area vector (magnitude = face area, direction = face normal)
- `V`: Cell volume

**Implementation in OpenFOAM:**
```cpp
volVectorField gradT = fvc::grad(T);
// Internally:
// 1. Interpolate T from cells to faces (linear interpolation)
// 2. Compute Tf × Sf for each face
// 3. Sum contributions for each cell
// 4. Divide by cell volume
```

**Discretization Schemes:**
- `Gauss linear`: Linear interpolation (most common)
- `Gauss upwind`: Upwind-biased (stable but diffusive)
- `leastSquares`: Cell-based gradient (second-order accurate)

**Why it matters:**
- Gradient accuracy affects solution quality
- Choice of scheme affects stability and convergence
- Non-orthogonal meshes require special treatment (corrected schemes)
</details>

<details>
<summary><b>6. How do we ensure dimensional consistency when creating fields?</b></summary>

**Answer:**
OpenFOAM enforces dimensional consistency at **compile time** using template metaprogramming.

**Key Principles:**
1. **Specify dimensions at creation**
   ```cpp
   volScalarField p
   (
       IOobject("p", ...),
       mesh,
       dimensionedScalar("p", dimPressure, 101325)  // [M L⁻¹ T⁻²]
   );
   ```

2. **Operations check dimensions**
   ```cpp
   volScalarField velocity = ...;        // [L T⁻¹]
   volScalarField length = ...;          // [L]
   volScalarField time = length / velocity;  // [L] / [L T⁻¹] = [T] ✓
   
   volScalarField pressure = velocity;   // COMPILATION ERROR!
   // Cannot assign [L T⁻¹] to [M L⁻¹ T⁻²]
   ```

3. **Use named dimension constants**
   ```cpp
   dimensionSet dimPressure(1, -1, -2, 0, 0, 0, 0);  // [M L⁻¹ T⁻²]
   // Or use predefined:
   dimensionedScalar p0("p0", dimPressure, 101325);
   ```

**7 Base Dimensions:**
- [0]: Mass (M)
- [1]: Length (L)
- [2]: Time (T)
- [3]: Temperature (Θ)
- [4]: Current (I)
- [5]: Luminous intensity (J)
- [6]: Amount of substance (N)

**Common Mistakes:**
```cpp
// ❌ WRONG: No dimensions specified
volScalarField T(IOobject("T", ...), mesh, 300.0);  // Error!

// ✅ CORRECT: Specify dimensions
volScalarField T
(
    IOobject("T", ...),
    mesh,
    dimensionedScalar("T", dimTemperature, 300.0)
);
```
</details>

---

## 🔑 Key Takeaways | สรุปสิ่งสำคัญ

### Core Concepts | แนวคิดหลัก

1. **GeometricField = DimensionedField + Boundary Conditions**
   - Stores internal field values (cell-centered)
   - Stores boundary field values (patch-wise)
   - Enforces dimensional consistency
   - Enables finite volume operations (fvc::)

2. **Template Structure Defines Behavior**
   - `Type`: scalar, vector, tensor (data type)
   - `PatchField`: fvPatchField, fvsPatchField (BC handling)
   - `GeoMesh`: volMesh, surfaceMesh (topology)

3. **IOobject Controls I/O Behavior**
   - `MUST_READ`: File must exist (essential fields)
   - `READ_IF_PRESENT`: Optional fields with defaults
   - `AUTO_WRITE`: Output at every time step
   - `NO_WRITE`: Debug fields, intermediate calculations

4. **Boundary Access Must Be Const-Correct**
   - `boundaryField()`: Read-only (const)
   - `boundaryFieldRef()`: Read-write (non-const)
   - Always check `findPatchID() != -1`

5. **fvc:: Operations Implement Finite Volume Method**
   - `fvc::grad(T)`: Gauss theorem over cell faces
   - `fvc::div(phi)`: Flux balance
   - `fvc::laplacian(alpha, T)`: Diffusion operator
   - Return temporary fields for efficient chaining

6. **Custom Fields Enable Debugging**
   - Create meaningful output fields for ParaView
   - Calculate derived quantities (Co, y+, vorticity)
   - Use `NO_READ` + `AUTO_WRITE` for diagnostic fields
   - Always call `.write()` to output to disk

### Practical Guidelines | แนวทางปฏิบัติ

**DO ✅:**
- Always specify dimensions using `dimensionedScalar`
- Use `==` operator for boundary condition evaluation
- Check patch ID existence before accessing boundaries
- Validate field dimensions before operations
- Write custom fields for debugging solver issues
- Use `forAll` macro for idiomatic OpenFOAM code

**DON'T ❌:**
- Don't use `boundaryField()` for modification (use `boundaryFieldRef()`)
- Don't use `=` for BC assignment (use `==`)
- Don't forget to call `.write()` for custom output fields
- Don't assume patches exist (always check `findPatchID()`)
- Don't ignore dimension errors (they catch real bugs!)
- Don't create fields without proper IOobject configuration

---

## 📖 Related Documentation | เอกสารที่เกี่ยวข้อง

### Within This Module | ในโมดูลนี้

- **Overview:** [00_Overview.md](00_Overview.md:1) - Module roadmap and prerequisites
- **Design Philosophy:** [02_Design_Philosophy.md](02_Design_Philosophy.md:1) - Why fields are designed this way
- **Inheritance Hierarchy:** [03_Inheritance_Hierarchy.md](03_Inheritance_Hierarchy.md:1) - Class relationships
- **Field Lifecycle:** [04_Field_Lifecycle.md](04_Field_Lifecycle.md:1) - Creation, destruction, registration
- **Mathematical Type Theory:** [05_Mathematical_Type_Theory.md](05_Mathematical_Type_Theory.md:1) - Dimensional analysis
- **Common Pitfalls:** [06_Common_Pitfalls.md](06_Common_Pitfalls.md:1) - Error prevention

### Prerequisite Modules | โมดูลพื้นฐาน

- **Smart Pointers:** [01_FOUNDATION_PRIMITIVES/04_Smart_Pointers.md](../../01_FOUNDATION_PRIMITIVES/04_Smart_Pointers.md:1)
- **Basic Types:** [01_FOUNDATION_PRIMITIVES/02_Basic_Primitives.md](../../01_FOUNDATION_PRIMITIVES/02_Basic_Primitives.md:1)
- **Dimensioned Types:** [02_DIMENSIONED_TYPES/01_Introduction.md](../../02_DIMENSIONED_TYPES/01_Introduction.md:1)
- **fvMesh:** [04_MESH_CLASSES/05_fvMesh.md](../04_MESH_CLASSES/05_fvMesh.md:1)

### Advanced Topics | หัวข้อขั้นสูง

- **fvm:: Operations:** Finite volume **implicit** operators (for matrix assembly)
- **Custom Boundary Conditions:** Creating specialized PatchField classes
- **Parallel Fields:** Decomposed fields and MPI communication
- **Field Interpolation:** Cell-to-face, face-to-cell, point interpolation

---

## 🎓 Next Steps | ขั้นตอนถัดไป

### Recommended Learning Path | เส้นทางการเรียนรู้ที่แนะนำ

**After completing this module:**

1. **Practice with Real Solvers**
   - Read `createFields.H` in standard solvers (`simpleFoam`, `pimpleFoam`)
   - Trace field operations in solver equations (e.g., `UEqn.H`)
   - Modify boundary conditions in existing cases

2. **Build a Custom Solver**
   - Start with `scalarTransportFoam` template
   - Add custom output fields (Courant number, vorticity)
   - Implement time-varying boundary conditions
   - Debug using ParaView visualization

3. **Explore Advanced Topics**
   - **fvm:: operators**: Implicit discretization for matrix assembly
   - **Custom boundary conditions**: Inherit from `fvPatchField<Type>`
   - **Field manipulation**: Advanced algebraic operations
   - **Performance optimization**: Minimize temporary field creation

4. **Production Development**
   - Code review: Check for dimension consistency
   - Unit testing: Validate field operations
   - Documentation: Document custom fields and BCs
   - Version control: Track solver evolution

### Assessment | การประเมินผล

**Self-Assessment Questions:**
- Can you create a volScalarField from scratch without looking at examples?
- Do you understand when to use `MUST_READ` vs `READ_IF_PRESENT`?
- Can you explain why boundary conditions use `==` instead of `=`?
- Are you comfortable with fvc:: grad, div, and laplacian operations?
- Can you create custom output fields for debugging?

**If YES:** You are ready for custom solver development!

**If NO:** Revisit the relevant exercises and try the variations.

---

## 📚 Exercise Variations and Extensions | แบบฝึกหัดเพิ่มเติมและการขยาย

### Extended Exercise 1: Time-Varying Fields

**Task:** Create a field that varies sinusoidally in time and space.

```cpp
volScalarField waveField
(
    IOobject("wave", ...),
    mesh,
    dimensionedScalar("wave", dimless, 0)
);

const volVectorField& C = mesh.C();  // Cell centers
scalar t = runTime.value();

forAll(waveField, cellI)
{
    scalar x = C[cellI].x();
    scalar y = C[cellI].y();
    waveField[cellI] = sin(2.0 * 3.14159 * (x + t));
}
```

**Challenge:** Extend to 3D wave with frequency and wavelength parameters.

---

### Extended Exercise 2: Adaptive Boundary Conditions

**Task:** Implement a feedback-controlled boundary condition.

```cpp
label inletID = mesh.boundaryMesh().findPatchID("inlet");
scalar targetVelocity = 10.0;

// Measure outlet velocity
label outletID = mesh.boundaryMesh().findPatchID("outlet");
const scalarField& Uout = U.boundaryField()[outletID];
scalar avgUout = average(Uout);

// Adjust inlet to maintain target
scalar inletVelocity = targetVelocity + (targetVelocity - avgUout);
U.boundaryFieldRef()[inletID] == inletVelocity;

Info << "Feedback: inlet U = " << inletVelocity << " (target = " << targetVelocity << ")" << endl;
```

**Challenge:** Implement PID controller instead of proportional control.

---

### Extended Exercise 3: Field Interpolation

**Task:** Interpolate fields between different mesh regions.

```cpp
// Map from fine mesh to coarse mesh
volScalarField fineField(fineMesh, ...);
volScalarField coarseField(coarseMesh, ...);

// For each coarse cell, find average of overlapping fine cells
forAll(coarseField, coarseI)
{
    vector coarseC = coarseMesh.C()[coarseI];
    scalar sumValue = 0.0;
    label nValues = 0;
    
    forAll(fineField, fineI)
    {
        vector fineC = fineMesh.C()[fineI];
        scalar dist = mag(coarseC - fineC);
        
        if (dist < searchRadius)
        {
            sumValue += fineField[fineI];
            nValues++;
        }
    }
    
    coarseField[coarseI] = sumValue / max(nValues, 1);
}
```

**Challenge:** Implement inverse-distance weighting instead of averaging.

---

### Extended Exercise 4: Field Derivatives

**Task:** Compute second derivatives and mixed derivatives.

```cpp
// First derivatives
volVectorField gradT = fvc::grad(T);
volTensorField gradU = fvc::grad(U);

// Second derivatives (Laplacian)
volScalarField lapT = fvc::laplacian(T);
volVectorField lapU = fvc::laplacian(U);

// Mixed derivatives: ∂²T/∂x∂y
volScalarField d2Tdxdy
(
    IOobject("d2Tdxdy", ...),
    fvc::grad(gradT).component(1)  // y-component of ∇(∇T)
);
```

**Challenge:** Compute all components of the Hessian matrix (∇∇T).

---

## 🏆 Module Completion Checklist | รายการตรวจสอบการสำเร็จโมดูล

Use this checklist to verify your understanding before proceeding to advanced topics.

### Basic Competency | ความสามารถพื้นฐาน

- [ ] Can create volScalarField and volVectorField from files
- [ ] Understands IOobject constructor parameters
- [ ] Can compute field magnitude and components
- [ ] Can access boundary field values
- [ ] Can compute gradient, divergence, and Laplacian
- [ ] Can write custom fields to disk

### Intermediate Competency | ความสามารถระดับกลาง

- [ ] Can initialize fields with dimensioned values
- [ ] Can modify boundary conditions correctly
- [ ] Understands const-correctness in boundary access
- [ ] Can chain fvc:: operations (e.g., `mag(fvc::grad(T))`)
- [ ] Can create dimensionally consistent expressions
- [ ] Can debug common field-related errors

### Advanced Competency | ความสามารถขั้นสูง

- [ ] Can implement time-varying boundary conditions
- [ ] Can compute derived quantities (Co, y+, vorticity)
- [ ] Understands finite volume discretization schemes
- [ ] Can optimize field operations for performance
- [ ] Can design custom output fields for analysis
- [ ] Can map field operations to solver development

### Expert Competency | ความสามารถระดับผู้เชี่ยวชาญ

- [ ] Can create custom boundary condition classes
- [ ] Can implement parallel field operations
- [ ] Can design new field algebra operations
- [ ] Can mentor others in field usage
- [ ] Can contribute to OpenFOAM field classes
- [ ] Can optimize solver performance through field management

**Total Checkpoints: 24**
**Target: Complete at least 16 checkpoints before moving to advanced topics.**

---

**End of Module 05 - GeometricFields: Summary and Exercises**

Next Module: **06_Turbulence_Modeling** (if available) or **Advanced Topics in Custom Solver Development**