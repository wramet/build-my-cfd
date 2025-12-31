# Field Algebra - Summary and Exercises

สรุปและแบบฝึกหัด Field Algebra

> [!TIP] ทำไม Field Algebra สำคัญใน OpenFOAM?
> Field Algebra คือภาษาพื้นฐานที่ใช้สื่อสารกับ **Fields** (ค่าที่กระจายอยู่บน mesh) ใน OpenFOAM:
> - **ความสำคัญ:** ทุก solver ใช้ field algebra เพื่อคำนวณ gradient, divergence, laplacian สำหรับสมการกายภาพ
> - **ความเสถียร:** การเลือกใช้ `fvm` (implicit) กับ `fvc` (explicit) ส่งผลต่อความเสถียรของการคำนาณ
> - **Performance:** การใช้ expression templates ทำให้การคำนวณหลาย operation รวดเร็วขึ้น
> - **ขอบเขต:** ใช้ใน **การพัฒนา solver** (`src/finiteVolume/`) และ **function objects** สำหรับ post-processing
>
> **ตัวอย่างการประยุกต์ใช้:**
> - คำนวณค่า `y+` จาก field `U` และ `nut`
> - สร้าง source term แบบ dynamic สำหรับสมการพลังงาน
> - คำนวณ vortex identification criteria (Q-criterion, lambda-2)

---

## Learning Objectives

เมื่อจบบทนี้ คุณจะสามารถ:
- **เขียนสมการพีชคณิตบน fields** เพื่อคำนวณค่าต่างๆ แบบ automatic dimensional checking
- **เลือกใช้ `fvm` กับ `fvc`** อย่างเหมาะสมตามความต้องการด้านความเสถียรและความแม่นยำ
- **ประกอบสมการ transport equation** แบบครบถ้วนสำหรับ solver development
- **คำนวณค่าเชิงสถิติ** และส่งออกผลแบบ parallel-aware
- **สร้าง flux fields** และใช้งาน surface field operations อย่างถูกต้อง

---

## Summary

### Key Operations

> [!NOTE] **📂 OpenFOAM Context**
> **Domain:** การดำเนินการพีชคณิตบน fields
>
> **ไฟล์ที่เกี่ยวข้อง:**
> - `0/*` - ไฟล์ initial/boundary conditions (อ่าน/เขียน fields: `U`, `p`, `T`)
> - `constant/transportProperties` - ค่าทางกายภาพ (density, viscosity) ที่ใช้ในการคำนาณ
>
> **การใช้งานใน Code:**
> - **Solver Development:** ใช้ใน `src/finiteVolume/` สำหรับสร้างสมการ line-by-line
> - **Function Objects:** ใช้คำนวณค่าเชิงสถิติ (min, max, average) และส่งออกผล
> - **Boundary Conditions:** ใช้คำนวณ gradient values ที่ patch boundaries
>
> **Keywords สำคัญ:**
> - `fvc::`, `fvm::` - Finite volume calculus operators
> - `volScalarField`, `volVectorField` - Field types
> - `dimensionedScalar` - Constant with units

| Category | Examples |
|----------|----------|
| Arithmetic | `+`, `-`, `*`, `/` |
| Calculus (fvc) | `grad`, `div`, `laplacian`, `curl` |
| Matrix (fvm) | `ddt`, `div`, `laplacian`, `Sp` |
| Statistics | `max`, `min`, `average`, `sum` |

### fvm vs fvc

> [!NOTE] **📂 OpenFOAM Context**
> **Domain:** Numerical Discretization Schemes
>
> **ไฟล์ที่เกี่ยวข้อง:**
> - `system/fvSchemes` - กำหนด discretization schemes สำหรับ `grad`, `div`, `laplacian`
> - `system/fvSolution` - กำหนด solver tolerances และ algorithms
>
> **การใช้งานใน Solver Code:**
> ```cpp
> // ใน solver createEquation():
> // fvm ใช้สำหรับ terms ที่ต้องการ implicit treatment
> // fvc ใช้สำหรับ terms ที่คำนวณแบบ explicit
>
> fvScalarMatrix TEqn
> (
>     fvm::ddt(T)              // Implicit: เสถียรกับ time step ใหญ่
>   + fvm::div(phi, T)         // Implicit: conservative
>   - fvm::laplacian(DT, T)    // Implicit: diffusion dominant
> ==
>     fvc::grad(p)             // Explicit: known from previous iteration
>   + fvc::Su(source, T)       // Explicit: source term
> );
> ```
>
> **Keywords ใน dictionary:**
> - `gradSchemes` - เลือก scheme สำหรับ gradient (Gauss, leastSquares)
> - `divSchemes` - เลือก scheme สำหรับ divergence (Gauss upwind, linear)
> - `laplacianSchemes` - เลือก scheme สำหรับ laplacian (Gauss linear corrected)

| Prefix | Type | Goes To | Usage Example |
|--------|------|---------|---------------|
| `fvm::` | Implicit | Matrix (LHS) | `fvm::ddt(T)`, `fvm::div(phi, T)` |
| `fvc::` | Explicit | Source (RHS) | `fvc::grad(p)`, `fvc::curl(U)` |

---

## Exercise 1: Basic Arithmetic

> [!NOTE] **📂 OpenFOAM Context**
> **Domain:** Field Computation และ Physics Properties
>
> **ไฟล์ที่เกี่ยวข้อง:**
> - `0/p`, `0/T`, `0/U` - ไฟล์ field conditions ที่ถูกอ่านเข้ามาเป็น `volScalarField`, `volVectorField`
> - `constant/transportProperties` - กำหนดค่า `rho` (density) และ `nu` (viscosity)
>
> **การใช้งานใน Code:**
> ```cpp
> // ใน solver::readFields()
> volScalarField p(IOobject("p", runTime.timeName(), mesh, ...), mesh);
> volScalarField T(IOobject("T", ...), mesh);
> volVectorField U(IOobject("U", ...), mesh);
>
> // อ่านค่า constant จาก transportProperties
> dimensionedScalar rho = transportProperties.lookup("rho");
>
> // คำนวณ dynamic pressure สำหรับ output
> volScalarField dynP = 0.5 * rho * magSqr(U);
> ```
>
> **ประยุกต์ใช้:**
> - **Post-processing:** คำนวณ dynamic pressure สำหรับ force coefficients
> - **Initial Conditions:** แปลงหน่วยอุณหภูมิ (Celsius → Kelvin)
> - **Boundary Conditions:** คำนวณค่าที่ boundary patches

**Difficulty:** ⭐ Beginner

**Task:** คำนวณ dynamic pressure และแปลงหน่วยอุณหภูมิ

```cpp
// Fields
volScalarField p(IOobject("p", runTime.timeName(), mesh, IOobject::MUST_READ, IOobject::AUTO_WRITE), mesh);
volScalarField T(IOobject("T", runTime.timeName(), mesh, IOobject::MUST_READ, IOobject::AUTO_WRITE), mesh);
volVectorField U(IOobject("U", runTime.timeName(), mesh, IOobject::MUST_READ, IOobject::AUTO_WRITE), mesh);
dimensionedScalar rho("rho", dimDensity, 1000);

// Arithmetic - Dimensional consistency maintained
volScalarField dynP = 0.5 * rho * magSqr(U);           // Dynamic pressure [kg/(m·s²)]
dimensionedScalar T_offset("T_offset", dimTemperature, 273.15);
volScalarField Ttotal = T + T_offset;                  // Convert °C to K
```

**Expected Output:**
- `dynP` - Dynamic pressure field
- `Ttotal` - Temperature in Kelvin

---

## Exercise 2: Calculus Operations

> [!NOTE] **📂 OpenFOAM Context**
> **Domain:** Spatial Discretization (Finite Volume Calculus)
>
> **ไฟล์ที่เกี่ยวข้อง:**
> - `system/fvSchemes` - กำหนด schemes สำหรับ `gradSchemes`, `divSchemes`, `laplacianSchemes`
> - `system/fvSolution` - กำหนด solver settings
>
> **ตัวอย่างใน fvSchemes:**
> ```cpp
> gradSchemes
> {
>     default         Gauss linear;
>     grad(p)         Gauss linear;  // ใช้กับ fvc::grad(p)
> }
>
> divSchemes
> {
>     default         none;
>     div(phi,U)      Gauss upwind;  // ใช้กับ fvc::div(phi, U)
> }
>
> laplacianSchemes
> {
>     default         Gauss linear corrected;
> }
> ```
>
> **การใช้งานใน Solver:**
> - **Pressure-velocity coupling:** `grad(p)` ใช้ใน momentum equation
> - **Continuity check:** `div(U)` ใช้ตรวจสอบ mass conservation
> - **Heat conduction:** `laplacian(alpha, T)` ใช้ใน energy equation
> - **Vorticity calculation:** `curl(U)` ใช้ใน turbulence visualization

**Difficulty:** ⭐⭐ Intermediate

**Task:** คำนวณ gradient, divergence, laplacian, และ curl

```cpp
// Gradient of pressure
volVectorField gradP = fvc::grad(p);

// Divergence of velocity field (continuity check)
volScalarField divU = fvc::div(phi);

// Laplacian of temperature (heat conduction)
dimensionedScalar alpha("alpha", dimArea/sqr(dimTime), 1e-5);
volScalarField lapT = fvc::laplacian(alpha, T);

// Curl of velocity (vorticity)
volVectorField omega = fvc::curl(U);
```

**Expected Output:**
- `gradP` - Pressure gradient vectors
- `divU` - Velocity divergence (should be ~0 for incompressible flow)
- `lapT` - Temperature laplacian
- `omega` - Vorticity field

---

## Exercise 3: Build Equation

> [!NOTE] **📂 OpenFOAM Context**
> **Domain:** Solver Equation Assembly
>
> **ไฟล์ที่เกี่ยวข้อง:**
> - `system/fvSchemes` - กำหนด schemes สำหรับแต่ละ term:
>   - `ddtSchemes` - Time discretization (Euler, backward, CrankNicolson)
>   - `divSchemes` - Convection term scheme
>   - `laplacianSchemes` - Diffusion term scheme
> - `system/fvSolution` - Solver tolerances และ algorithms
>
> **ตัวอย่างใน solver code (`*.C`):**
> ```cpp
> // ใน solver main loop (เช่น, simpleFoam, buoyantSimpleFoam)
> while (simple.loop())
> {
>     // Assemble temperature equation
>     fvScalarMatrix TEqn
>     (
>         fvm::ddt(T)                    // Temporal term
>       + fvm::div(phi, T)               // Convection (implicit)
>       - fvm::laplacian(alpha, T)       // Diffusion (implicit)
>     ==
>         fvc::Su(Sh, T)                 // Source (explicit)
>     );
>
>     TEqn.solve();                      // Solve linear system
> }
> ```
>
> **Keywords ใน dictionaries:**
> - `solvers` - กำหนด linear solver (GAMG, PCG) และ preconditioner
> - `tolerance`, `relTol` - ค่า convergence criteria
> - `nCorrectors` - จำนวน correction loops (PIMPLE, PISO)
>
> **ประยุกต์ใช้:**
> - **Custom solvers:** สร้าง transport equation สำหรับ scalar quantities
> - **Source terms:** เพิ่ม heat source, chemical reactions
> - **Coupling:** Couple multiple equations ผ่าน source terms

**Difficulty:** ⭐⭐⭐ Advanced

**Task:** ประกอบสมการ energy equation แบบครบถ้วน

```cpp
// Create a heat source term
volScalarField Sh(IOobject("Sh", runTime.timeName(), mesh, IOobject::MUST_READ, IOobject::AUTO_WRITE), mesh);

// Assemble temperature equation
fvScalarMatrix TEqn
(
    fvm::ddt(T)                    // Time derivative: ∂T/∂t
  + fvm::div(phi, T)               // Convection: ∇·(φT)
 ==
    fvm::laplacian(alpha, T)       // Diffusion: ∇·(α∇T)
  + fvc::Su(Sh, T)                 // Explicit source: Sh/rho/Cp
);

// Solve the equation
TEqn.solve();

// Report convergence
Info<< "T equation solver performance: " << TEqn.performance() << endl;
```

**Expected Output:**
- Solved temperature field `T`
- Solver performance statistics

---

## Exercise 4: Flux Calculation

> [!NOTE] **📂 OpenFOAM Context**
> **Domain:** Surface Fields และ Convective Terms
>
> **ไฟล์ที่เกี่ยวข้อง:**
> - `createPhi.H` - ไฟล์ standard ใน solver สำหรับสร้าง `phi` field
> - `0/phi` - Flux field (บาง solvers มีไฟล์นี้)
>
> **การใช้งานใน Solver:**
> ```cpp
> // มาตรฐานในทุก incompressible solver:
> // 1) สร้าง flux field
> surfaceScalarField phi
> (
>     IOobject("phi", runTime.timeName(), mesh, ...),
>     fvc::interpolate(U) & mesh.Sf()  // Interpolate U แล้ว dot product กับ face area
> );
>
> // 2) ใช้ใน convection terms
> fvm::div(phi, T)   // Transport of T ด้วย flux phi
> fvm::div(phi, U)   // Convection of velocity
> ```
>
> **Keywords สำคัญ:**
> - `&` - Dot product operator สำหรับ vectors
> - `mesh.Sf()` - Face area vectors (surface field)
> - `fvc::interpolate()` - Interpolate จาก cell centers ไปยัง face centers
>
> **ประยุกต์ใช้:**
> - **Conservation check:** คำนวณ `fvc::div(phi)` ตรวจสอบ mass conservation
> - **Boundary conditions:** กำหนด flux values ที่ inlets/outlets
> - **Post-processing:** คำนวณ mass flow rate ผ่าน surfaces

**Difficulty:** ⭐⭐ Intermediate

**Task:** สร้าง mass flux และคำนวณ convective transport

```cpp
// Mass flux calculation
surfaceScalarField phi
(
    IOobject("phi", runTime.timeName(), mesh, IOobject::NO_READ, IOobject::AUTO_WRITE),
    fvc::interpolate(rho * U) & mesh.Sf()
);

// Convective flux of temperature
volScalarField convT = fvc::div(phi, T);

// Mass conservation check
volScalarField massCont = fvc::div(phi);
scalar maxMassImbalance = max(mag(massCont)).value();
Info<< "Max mass imbalance: " << maxMassImbalance << endl;
```

**Expected Output:**
- `phi` - Mass flux field at faces
- `convT` - Convective temperature flux
- Mass imbalance indicator

---

## Exercise 5: Statistics

> [!NOTE] **📂 OpenFOAM Context**
> **Domain:** Runtime Statistics และ Function Objects
>
> **ไฟล์ที่เกี่ยวข้อง:**
> - `system/controlDict` - ใช้กำหนด function objects สำหรับ statistics
> - `log.*` - Log files ที่เก็บค่า statistics ระหว่าง simulation
>
> **ตัวอย่างใน controlDict:**
> ```cpp
> functions
> {
>     // คำนวณ statistics ของ temperature field
>     TStats
>     {
>         type            sets;
>         functionObjectLibs ("libsampling.so");
>         ...
>     }
>
>     // หรือใช้ built-in function objects
>     fieldMinMax
>     {
>         type            fieldMinMax;
>         fields          (p U T);
>     }
> }
> ```
>
> **การใช้งานใน Custom Code:**
> ```cpp
> // ใน solver หรือ custom function object:
> Info<< "T min/max: " << min(T) << " / " << max(T) << endl;
> Info<< "Average T: " << average(T) << endl;
>
> // Volume-weighted integral (สำคัญสำหรับ parallel runs)
> scalar totalMass = gSum(rho * mesh.V());
> ```
>
> **Keywords สำคัญ:**
> - `gSum`, `gMax`, `gMin` - Global operations (parallel-aware)
> - `sum`, `max`, `min` - Local processor operations
> - `average()` - Domain-averaged values
> - `mesh.V()` - Cell volumes
>
> **ประยุกต์ใช้:**
> - **Convergence monitoring:** Track min/max values ของ fields
> - **Mass balance:** คำนวณ total mass ด้วย `gSum(rho * mesh.V())`
> - **Data export:** ส่งข้อมูล statistics ไปยัง log files

**Difficulty:** ⭐⭐⭐ Advanced

**Task:** คำนวณค่าเชิงสถิติแบบ parallel-aware

```cpp
// Local statistics (per processor)
scalar maxT_local = max(T).value();
scalar minT_local = min(T).value();

// Global statistics (across all processors)
scalar maxT_global = gMax(T);
scalar minT_global = gMin(T);
scalar avgT = average(T).value();

// Volume-weighted integrals (parallel-aware)
scalar totalMass = gSum(rho * mesh.V());
scalar totalInternalEnergy = gSum(rho * T * mesh.V());

// Output results
Info<< "Temperature statistics:" << nl
    << "  min (global): " << minT_global << " K" << nl
    << "  max (global): " << maxT_global << " K" << nl
    << "  average: " << avgT << " K" << nl
    << "Total mass: " << totalMass << " kg" << endl;
```

**Expected Output:**
- Min/max/average temperature values
- Total mass and internal energy

---

## Quick Reference

> [!NOTE] **📂 OpenFOAM Context**
> **Domain:** Common Field Operations ใน Solver Development
>
> **ตำแหน่งใช้งาน:**
> - **Solver code:** `applications/solvers/solversName/*.C`
> - **Function objects:** `src/functionObjects/`
> - **Boundary conditions:** `src/finiteVolume/fields/fvPatchFields/`
>
> **Mapping ไปยัง fvSchemes:**
> ```cpp
> // Operation          →  fvSchemes keyword
> fvc::grad(field)    →  gradSchemes { default Gauss linear; }
> fvc::div(phi, field) →  divSchemes { div(phi,field) Gauss upwind; }
> fvc::laplacian(k, T) →  laplacianSchemes { default Gauss linear corrected; }
> ```
>
> **ตัวอย่างการใช้งานจริง:**
> - **Pressure gradient force:** `fvc::grad(p)` ใน momentum equation
> - **Vorticity:** `fvc::curl(U)` สำหรับ turbulence visualization
> - **Heat flux:** `fvc::interpolate(k) * fvc::grad(T)` สำหรับ wall heat flux

| Operation | Code | Usage |
|-----------|------|-------|
| Gradient | `fvc::grad(p)` | Pressure force, wall gradients |
| Divergence | `fvc::div(phi, U)` | Continuity, convection |
| Laplacian | `fvc::laplacian(k, T)` | Diffusion, heat conduction |
| Curl | `fvc::curl(U)` | Vorticity, turbulence |
| Interpolate | `fvc::interpolate(T)` | Cell-to-face values |
| Flux | `linearInterpolate(U) & mesh.Sf()` | Mass flow rate |
| Statistics | `gSum(T * mesh.V())` | Global integrals |

---

## 🧠 Concept Check

<details>
<summary><b>1. fvm::div vs fvc::div ต่างกันอย่างไร?</b></summary>

- **fvm::div**: Implicit → matrix coefficients (LHS of equation)
- **fvc::div**: Explicit → evaluated immediately (RHS of equation)
- **Use fvm** for terms requiring stability (convection, diffusion)
- **Use fvc** for terms calculated from previous iteration (gradients, sources)
</details>

<details>
<summary><b>2. ทำไมใช้ Sp vs Su?</b></summary>

- **fvm::Sp(source, field)**: Implicit source → adds to matrix diagonal → stabilizing
- **fvc::Su(source, field)**: Explicit source → RHS only → may destabilize
- **Guideline**: Use `Sp` for source terms linear in the field variable
</details>

<details>
<summary><b>3. gSum vs sum ต่างกันอย่างไร?</b></summary>

- **sum**: Local processor sum only (works on single processor)
- **gSum**: Global sum across all processors (parallel-aware)
- **Always use gSum** for domain integrals in parallel simulations
</details>

<details>
<summary><b>4. ทำไมต้องใช้ dimensionedScalar แทน double?</b></summary>

- **Type safety**: OpenFOAM checks dimensional consistency at compile-time
- **Prevents errors**: Cannot accidentally add pressure to velocity
- **Documentation**: Units are explicit in the code
- **Example**: `dimensionedScalar rho("rho", dimDensity, 1000);`
</details>

<details>
<summary><b>5. surfaceScalarField vs volScalarField ต่างกันอย่างไร?</b></summary>

- **volScalarField**: Values defined at cell centers (interior of domain)
- **surfaceScalarField**: Values defined at cell faces (boundaries between cells)
- **Flux fields**: Always use `surfaceScalarField` (e.g., `phi`)
- **Use interpolate**: Convert between volume and surface fields
</details>

---

## Key Takeaways

> [!NOTE] **📚 Module 09: Field Algebra - Key Concepts**
>
> **1. Field Operations:**
> - **Arithmetic**: `+`, `-`, `*`, `/` work field-wise with dimensional checking
> - **Calculus**: `fvc::` for explicit, `fvm::` for implicit operations
> - **Statistics**: `gSum`, `gMax`, `average()` for domain-wide values
>
> **2. fvm vs fvc:**
> - **fvm** (implicit) → matrix coefficients → stable for large timesteps
> - **fvc** (explicit) → immediate evaluation → for known values
> - **Rule of thumb**: Use fvm for transport terms, fvc for gradients and sources
>
> **3. Solver Development:**
> - Equation assembly: `fvScalarMatrix TEqn(...)` then `TEqn.solve()`
> - Source terms: `fvm::Sp` (implicit) vs `fvc::Su` (explicit)
> - Performance: Expression templates eliminate temporary fields
>
> **4. Practical Skills:**
> - Read fields from `0/` directory with `IOobject`
> - Create flux fields: `phi = fvc::interpolate(rho*U) & mesh.Sf()`
> - Calculate statistics: `Info<< "Average T: " << average(T) << endl;`
>
> **5. Common Pitfalls:**
> - **Dimensional mismatch**: Cannot add pressure to temperature → use `dimensionedScalar` offsets
> - **Parallel unaware**: Use `gSum` instead of `sum` for domain integrals
> - **Memory overhead**: Expression templates help, but complex chains create temps
> - **Surface vs Volume**: Use `surfaceScalarField` for fluxes, `volScalarField` for cell values

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Operator Overloading:** [03_Operator_Overloading.md](03_Operator_Overloading.md)
- **Dimensional Checking:** [04_Dimensional_Checking.md](04_Dimensional_Checking.md)
- **Expression Templates:** [05_Expression_Templates.md](05_Expression_Templates.md)
- **Common Pitfalls:** [06_Common_Pitfalls.md](06_Common_Pitfalls.md)