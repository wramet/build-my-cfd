# Field Types - Summary and Exercises

สรุปและแบบฝึกหัด Field Types

> [!TIP] ทำไม Field Types สำคัญ?
> Field Types คือ **รากฐานของการจัดเก็บข้อมูลฟิสิกส์** ใน OpenFOAM ทุก solver ทำงานกับ fields (เช่น `p`, `U`, `T`) การเข้าใจว่า field แต่ละประเภทเก็บข้อมูลที่ไหน (cell center vs face center vs point) และเข้าถึงข้อมูลยังไง จะช่วยให้คุณ:
> - เขียน **custom boundary conditions** ได้อย่างถูกต้อง
> - สร้าง **function objects** สำหรับวิเคราะห์ข้อมูลได้
> - แก้ไข **solver code** หรือสร้าง solver ใหม่ได้อย่างมั่นใจ
> - Debug ปัญหาการ **interpolation** ระหว่าง cell/face ได้
>
> ในมุมมองของไฟล์ case: fields ถูกจัดเก็บในโฟลเดอร์ `0/` (เริ่มต้น) และ `time directories` (ผลลัพธ์) ส่วนการจัดการ fields ผ่านโค้ด C++ จะอยู่ใน `src/` ของ custom solvers หรือ library

---

## Summary

> [!NOTE] **📂 OpenFOAM Context: Field Storage in Case Files**
> ใน **มุมมองไฟล์ case** (Domain A):
> - Fields ทั้งหมดถูกจัดเก็บในไฟล์ข้อความภายใต้โฟลเดอร์ `0/` (สำหรับเวลา t=0) และโฟลเดอร์เวลาถัดๆไป (เช่น `0.1/`, `0.2/`, ...)
> - **volScalarField** → ไฟล์เช่น `0/p`, `0/T`, `0/k` (ค่าที่ cell centers)
> - **volVectorField** → ไฟล์เช่น `0/U` (ค่าที่ cell centers)
> - **surfaceScalarField** → ไฟล์เช่น `0/phi` (ค่าที่ face centers)
> - **pointVectorField** → ไฟล์เช่น `0/pointDisplacement` (ค่าที่ mesh vertices)
>
> ใน **มุมมองโค้ด C++** (Domain E):
> - การประกาศ fields อยู่ในไฟล์ solver `.C` เช่น `src/finiteVolume/cfd/tools/general/interFoam/interFoam.C`
> - Header files: `src/finiteVolume/fields/volFields/volFields.H`, `src/finiteVolume/fields/surfaceFields/surfaceFields.H`
> - การอ่าน/เขียน fields ผ่าน `IOobject` จะชี้ไปที่โฟลเดอร์ `constant/` หรือ time directories โดยอัตโนมัติ

### Field Type Hierarchy

| Type | Location | Example |
|------|----------|---------|
| `volScalarField` | Cell center | p, T, k |
| `volVectorField` | Cell center | U |
| `surfaceScalarField` | Face center | phi |
| `pointVectorField` | Mesh vertex | pointDisplacement |

### Template Structure

> [!NOTE] **📂 OpenFOAM Context: Template Instantiation in Source Code**
> ใน **Domain E: Coding/Customization**:
> - Template `GeometricField<Type, PatchField, GeoMesh>` ถูกใช้ใน **source code** ของ OpenFOAM
> - การสร้าง field types ต่างๆ เป็นการ **template instantiation**:
>   - `volScalarField` = `GeometricField<scalar, fvPatchField, volMesh>`
>   - `volVectorField` = `GeometricField<vector, fvPatchField, volMesh>`
>   - `surfaceScalarField` = `GeometricField<scalar, fvsPatchField, surfaceMesh>`
> - **File locations:** นิยามหลักอยู่ใน `src/OpenFOAM/fields/GeometricField/GeometricField.C`
> - **PatchField definitions:** `src/finiteVolume/fields/fvPatchFields/` (สำหรับ volume fields)
> - **Surface patchField:** `src/finiteVolume/fields/fvsPatchFields/` (สำหรับ surface fields)
>
> ใน **custom code** ของคุณ:
> - เมื่อเขียน solver ใหม่ หรือ function object คุณจะต้อง `#include` headers เหล่านี้จาก `src/finiteVolume/fields/...`
> - การเลือก `PatchField` และ `GeoMesh` ที่ถูกต้องจะกำหนดว่า field ของคุณ "อยู่ที่ไหน" และ "มี boundary condition แบบไหน"

```cpp
GeometricField<Type, PatchField, GeoMesh>
// Type: scalar, vector, tensor
// PatchField: fvPatchField, fvsPatchField, pointPatchField
// GeoMesh: volMesh, surfaceMesh, pointMesh
```

---

## Exercise 1: Create Fields

> [!NOTE] **📂 OpenFOAM Context: Field Declaration in Solvers**
> ใน **Domain E: Coding/Customization**:
> - การสร้าง fields ด้วย `IOobject` เป็น **standard pattern** ในทุก OpenFOAM solvers
> - **Typical locations:** ไฟล์ solver เช่น `src/finiteVolume/cfd/tools/general/simpleFoam/simpleFoam.C`
> - **Keywords สำคัญใน IOobject:**
>   - `IOobject::MUST_READ` → ต้องมีไฟล์ field ใน `0/` (เช่น `0/p`, `0/U`)
>   - `IOobject::NO_READ` → สร้าง field ใหม่โดยไม่ต้องอ่านจากไฟล์ (มักใช้กับ intermediate fields)
>   - `runTime.timeName()` → ชี้ไปที่ time directory ปัจจุบัน (เช่น `0`, `0.1`, ...)
>
> **Example mapping:**
> - เมื่อ solver อ่าน `volScalarField p` ด้วย `MUST_READ` → จะมองหาไฟล์ `0/p` ใน case directory
> - เมื่อ solver สร้าง `volVectorField U` ใหม่ → จะสร้าง field ใน memory และเขียนลงไฟล์ output เมื่อถึงเวลา write
> - **Compilation:** ไฟล์ `.C` ของคุณต้องอยู่ในโครงสร้าง `Make/files` เพื่อ compile ให้เป็น executable

```cpp
// From file
volScalarField p
(
    IOobject("p", runTime.timeName(), mesh, IOobject::MUST_READ),
    mesh
);

// With initial value
volVectorField U
(
    IOobject("U", runTime.timeName(), mesh, IOobject::NO_READ),
    mesh,
    dimensionedVector("U", dimVelocity, vector::zero)
);
```

---

## Exercise 2: Field Arithmetic

> [!NOTE] **📂 OpenFOAM Context: Field Operations in Solver Equations**
> ใน **Domain E: Coding/Customization** (และ Domain A: Physics):
> - Field arithmetic ถูกใช้ใน **discretized equations** ของ solvers
> - **Typical locations:** ไฟล์ solver เช่น `src/finiteVolume/cfd/tools/general/simpleFoam/createFields.H` หรือใน main solver loop
>
> **Connection to Physics (Domain A):**
> - `rho * magSqr(U)` → คำนวณ **dynamic pressure** ($\frac{1}{2}\rho U^2$) สำหรับ drag/lift forces
> - `U.component(0)` → เข้าถึง **velocity component** (เช่น $u$, $v$, $w$) สำหรับ boundary conditions
> - `mag(U)` → คำนวณ **velocity magnitude** สำหรับ Courant number, Reynolds number
>
> **Connection to Function Objects:**
> - การคำนวณเหล่านี้มักถูกใช้ใน **function objects** สำหรับ runtime post-processing
> - **File:** `system/controlDict` → ระบุ `functions` ที่ใช้ field arithmetic
> - **Example function objects:** `forces`, `fieldMinMax`, `magSqr`

```cpp
// Scalar operations
volScalarField rhoU2 = rho * magSqr(U);

// Vector operations
volScalarField Ux = U.component(0);
volScalarField magU = mag(U);

// Mixed
volVectorField momentum = rho * U;
```

---

## Exercise 3: Surface Fields

> [!NOTE] **📂 OpenFOAM Context: Flux Calculation in Finite Volume Method**
> ใน **Domain B: Numerics & Linear Algebra** (และ Domain E: Coding):
> - Surface fields คือ **หัวใจของ Finite Volume Method** เพราะ flux ผ่าน faces เป็นพื้นฐานของ conservation laws
> - **Typical locations:**
>   - Solvers: ไฟล์เช่น `src/finiteVolume/cfd/tools/general/simpleFoam/createPhi.H`
>   - FvSchemes: `system/fvSchemes` → ระบุ `interpolationScheme` สำหรับ cell-to-face interpolation
>
> **Keywords ใน case files:**
> - **`phi`** → **mass flux** field $[\text{kg}/\text{s}]$ หรือ **volume flux** $[\text{m}^3/\text{s}]$ ถูกสร้างในทุก incompressible solvers
> - **File locations:**
>   - `0/phi` → flux field file (สร้างอัตโนมัติโดย solver หรือ manually ในบาง solvers)
>   - `system/fvSchemes` → `interpolationSchemes` คุบควม `linear`, `upwind`, `linearUpwind` สำหรับ `fvc::interpolate()`
>
> **Connection to discretization (Domain B):**
> - `fvc::interpolate(rho * U)` → interpolate **cell-centered velocity** ไปยัง **face-centered values**
> - `& mesh.Sf()` → dot product กับ **face area vector** เพื่อคำนวณ flux
> - **Flux equation:** $\phi_f = \int_f \mathbf{U} \cdot d\mathbf{S}_f$

```cpp
// Mass flux
surfaceScalarField phi = fvc::interpolate(rho * U) & mesh.Sf();

// Face interpolation
surfaceScalarField Tf = fvc::interpolate(T);

// Volume flux
surfaceScalarField phiU = fvc::flux(U);
```

---

## Exercise 4: Boundary Access

> [!NOTE] **📂 OpenFOAM Context: Boundary Conditions in Case Files**
> ใน **Domain A: Physics & Fields** (และ Domain E: Coding):
> - การเข้าถึง boundary fields คือ **การเชื่อมต่อระหว่าง C++ code กับ boundary condition files** ใน `0/` directory
> - **Typical locations:**
>   - Boundary condition code: `src/finiteVolume/fields/fvPatchFields/derived/`
>   - Field files: `0/p`, `0/U`, `0/T` → มีส่วน `boundaryField` ที่ระบุ BC สำหรับแต่ละ patch
>
> **Keywords ใน case files:**
> - **Patch names** เช่น `"inlet"`, `"outlet"`, `"walls"` → ต้องตรงกับชื่อใน `constant/polyMesh/boundary`
> - **Boundary condition types**:
>   - `fixedValue` → กำหนดค่าคงที่ (เช่น velocity inlet)
>   - `zeroGradient` → gradient = 0 (เช่น pressure outlet)
>   - `fixedFluxPressure` → flux คงที่ (pressure BC)
>
> **Connection to Mesh (Domain D):**
> - `mesh.boundaryMesh().findPatchID("inlet")` → ค้นหา patch ID จากชื่อที่ระบุใน **`constant/polyMesh/boundary`** file
> - Boundary patches ถูกสร้างโดย **meshing tools** (`blockMesh`, `snappyHexMesh`) และถูกเก็บใน `constant/polyMesh/`
>
> **Practical use:**
> - การอ่าน/เขียน boundary values ผ่าน code มักใช้ใน **custom boundary conditions** หรือ **function objects** เช่น:
>   - `src/finiteVolume/fields/fvPatchFields/derived/timeVaryingMappedFixedValue/`
>   - `system/controlDict` → `functions` ที่ monitor boundary values

```cpp
// Find patch
label inletI = mesh.boundaryMesh().findPatchID("inlet");

// Read boundary
const vectorField& Uin = U.boundaryField()[inletI];

// Modify boundary
U.boundaryFieldRef()[inletI] == fixedValue;

// Surface normal gradient
scalarField snGradT = T.boundaryField()[inletI].snGrad();
```

---

## Exercise 5: Point Fields

> [!NOTE] **📂 OpenFOAM Context: Point Mesh and Dynamic Meshing**
> ใน **Domain D: Meshing** (และ Domain E: Coding):
> - Point fields ถูกใช้ใน **dynamic meshing**, **FEM (Finite Element Method)**, และ **mesh deformation** problems
> - **Typical locations:**
>   - Dynamic mesh solvers: `src/finiteVolume/cfd/tools/general/moveDynamicMesh/`
>   - FEM solvers: `src/finiteElement/`
>   - Point mesh code: `src/meshes/pointMesh/`
>
> **Keywords ใน case files:**
> - **`pointDisplacement`** → field สำหรับ **vertex displacement** ใน dynamic mesh cases
> - **File locations:**
>   - `0/pointDisplacement` → boundary condition สำหรับ mesh movement
>   - `constant/dynamicMeshDict` → ระบุ dynamic mesh solver (เช่น `linearElasticity`, `solidBodyMotion`)
>   - `system/controlDict` → `runTimeModifiable true` สำหรับ runtime mesh changes
>
> **Connection to Mesh (Domain D):**
> - `pointMesh::New(mesh)` → สร้าง **point mesh** จาก base mesh (`fvMesh`)
> - Point mesh เก็บข้อมูลที่ **mesh vertices** (ไม่ใช่ cell centers หรือ face centers)
> - ใช้ใน **mesh quality analysis**, **adaptive mesh refinement**, และ **moving boundaries**
>
> **Common applications:**
> - **Fluid-Structure Interaction (FSI):** คำนวณ displacement ของ solid boundaries
> - **Moving boundaries:** เช่น piston motion, valve movement
> - **Mesh morphing:** ปรับ mesh ตาม geometry changes

```cpp
// Create point mesh
const pointMesh& pMesh = pointMesh::New(mesh);

// Point displacement field
pointVectorField pointD
(
    IOobject("pointDisplacement", runTime.timeName(), mesh),
    pMesh,
    dimensionedVector("zero", dimLength, vector::zero)
);
```

---

## Quick Reference

> [!NOTE] **📂 OpenFOAM Context: Code Snippets in Practice**
> ใน **Domain E: Coding/Customization**:
> - ตารางนี้คือ **quick reference** สำหรับการเขียนโค้ด C++ ใน OpenFOAM
> - **Typical usage:**
>   - **Solver development:** ใช้ใน main solver loop หรือ createFields.H
>   - **Function objects:** ใช้ใน custom function objects สำหรับ runtime analysis
>   - **Boundary conditions:** ใช้ใน custom BC classes
>
> **Connection to case files:**
> - Cell value access (`T[cellI]`) → อ่านค่าจาก field ใน memory ที่โหลดจาก `0/T`
> - Boundary value access → เข้าถึงค่าจาก `boundaryField` ส่วนใน field files
> - Interpolation (`fvc::interpolate`) → ใช้ schemes จาก `system/fvSchemes`:
>   ```cpp
>   // ใน system/fvSchemes:
>   interpolationSchemes
>   {
>       default linear;
>   }
>   ```
> - Flux computation → สร้าง `phi` field ที่ใช้ใน continuity equation
>
> **Keywords ใน compilation:**
> - เมื่อใช้ snippets เหล่านี้ใน custom code ต้อง:
>   - `#include "fvCFD.H"` → สำหรับ field operations
>   - Link กับ `libfiniteVolume.so` ใน `Make/options`

| Need | Code |
|------|------|
| Cell value | `T[cellI]` |
| Boundary value | `T.boundaryField()[patchI][faceI]` |
| Interpolate to face | `fvc::interpolate(T)` |
| Compute flux | `fvc::interpolate(U) & mesh.Sf()` |
| Get component | `U.component(0)` |
| Magnitude | `mag(U)` |

---

## Concept Check

<details>
<summary><b>1. volScalarField vs surfaceScalarField ต่างกันอย่างไร?</b></summary>

- **volScalarField**: ค่าที่ **cell center**
- **surfaceScalarField**: ค่าที่ **face center**
</details>

<details>
<summary><b>2. ทำไมต้อง interpolate ก่อนคำนวณ flux?</b></summary>

เพราะ **velocity is cell-centered** แต่ **flux ต้องการค่าที่ face**
</details>

<details>
<summary><b>3. snGrad คืออะไร?</b></summary>

**Surface normal gradient** = gradient ในทิศตั้งฉากกับ boundary face
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Point Fields:** [05_Point_Fields.md](05_Point_Fields.md)