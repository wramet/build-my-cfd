# Field Algebra - Summary and Exercises

สรุปและแบบฝึกหัด Field Algebra

> [!TIP] ทำไม Field Algebra สำคัญใน OpenFOAM?
> Field Algebra คือภาษาพื้นฐานที่ใช้สื่อสารกับ **Fields** (ค่าที่กระจายอยู่บน mesh) ใน OpenFOAM:
> - **ความสำคัญ:** ทุก solver ใช้ field algebra เพื่อคำนวณ gradient, divergence, laplacian สำหรับสมการกายภาพ
> - **ความเสถียร:** การเลือกใช้ `fvm` (implicit) กับ `fvc` (explicit) ส่งผลต่อความเสถียรของการคำนวณ
> - **Performance:** การใช้ expression templates ทำให้การคำนวณหลาย operation รวดเร็วขึ้น
> - **ขอบเขต:** ใช้ใน **การพัฒนา solver** (`src/finiteVolume/`) และ **function objects** สำหรับ post-processing
>
> **ตัวอย่างการประยุกต์ใช้:**
> - คำนวณค่า `y+` จาก field `U` และ `nut`
> - สร้าง source term แบบ dynamic สำหรับสมการพลังงาน
> - คำนวณ vortex identification criteria (Q-criterion, lambda-2)

---

## Summary

### Key Operations

> [!NOTE] **📂 OpenFOAM Context**
> **Domain:** การดำเนินการพีชคณิตบน fields
>
> **ไฟล์ที่เกี่ยวข้อง:**
> - `0/*` - ไฟล์ initial/boundary conditions (อ่าน/เขียน fields: `U`, `p`, `T`)
> - `constant/transportProperties` - ค่าทางกายภาพ (density, viscosity) ที่ใช้ในการคำนวณ
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

| Prefix | Type | Goes To |
|--------|------|---------|
| `fvm::` | Implicit | Matrix (LHS) |
| `fvc::` | Explicit | Source (RHS) |

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

```cpp
// Fields
volScalarField p, T;
volVectorField U;
dimensionedScalar rho("rho", dimDensity, 1000);

// Arithmetic
volScalarField dynP = 0.5 * rho * magSqr(U);
volScalarField Ttotal = T + 273.15;
```

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

```cpp
// Gradient
volVectorField gradP = fvc::grad(p);

// Divergence
volScalarField divU = fvc::div(phi);

// Laplacian
volScalarField lapT = fvc::laplacian(alpha, T);

// Curl
volVectorField omega = fvc::curl(U);
```

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

```cpp
fvScalarMatrix TEqn
(
    fvm::ddt(T)                    // Time derivative
  + fvm::div(phi, T)               // Convection
 ==
    fvm::laplacian(alpha, T)       // Diffusion
  + fvc::Su(Sh, T)                 // Source (explicit)
);

TEqn.solve();
```

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

```cpp
// Mass flux
surfaceScalarField phi = fvc::interpolate(rho * U) & mesh.Sf();

// Convective flux
volScalarField convT = fvc::div(phi, T);
```

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

```cpp
scalar maxT = max(T).value();
scalar minT = min(T).value();
scalar avgT = average(T).value();
scalar sumT = gSum(T * mesh.V());  // Volume-weighted sum
```

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

| Operation | Code |
|-----------|------|
| Gradient | `fvc::grad(p)` |
| Divergence | `fvc::div(U)` |
| Laplacian | `fvc::laplacian(k, T)` |
| Curl | `fvc::curl(U)` |
| Interpolate | `fvc::interpolate(T)` |
| Flux | `linearInterpolate(U) & mesh.Sf()` |

---

## 🧠 Concept Check

<details>
<summary><b>1. fvm::div vs fvc::div ต่างกันอย่างไร?</b></summary>

- **fvm::div**: Implicit → matrix coefficients
- **fvc::div**: Explicit → evaluated immediately
</details>

<details>
<summary><b>2. ทำไมใช้ Sp vs Su?</b></summary>

- **Sp**: Implicit source (stabilizing)
- **Su**: Explicit source (may destabilize)
</details>

<details>
<summary><b>3. gSum vs sum ต่างกันอย่างไร?</b></summary>

- **sum**: Local processor sum
- **gSum**: Global sum (parallel)
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Dimensional Checking:** [04_Dimensional_Checking.md](04_Dimensional_Checking.md)