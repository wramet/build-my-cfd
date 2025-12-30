# Field Types - Exercises and Capstone Projects

แบบฝึกหัดและโปรเจกต์รวม Field Types

> [!TIP] ทำเนื้อหานี้สำคัญ?
> หัวข้อนี้เป็น **การเชื่อมโยงความรู้ทั้งหมด** เกี่ยวกับ Field Types เข้ากับโจทย์จริง การแก้โจทย์ต่อไปนี้จะช่วยให้คุณ:
> - นำ **volume fields, surface fields, point fields** ไปประยุกต์ใช้กับ solver ที่คุณกำลังพัฒนา
> - เขียน **custom boundary conditions** และ **function objects** ได้อย่างมั่นใจ
> - เชื่อมต่อ **code implementation** กับ **case files** อย่างถูกต้อง
> - เข้าใจ **data flow** จากไฟล์ case → memory → output
>
> **Prerequisites:** คุณควรอ่าน 00_Overview.md, 02-06 ก่อนทำแบบฝึกหัดนี้

---

## 🎯 Learning Objectives

เมื่อจบแบบฝึกหัดนี้ คุณจะสามารถ:
- ✅ สร้าง fields ใน C++ code และเชื่อมต่อกับ case files ได้อย่างถูกต้อง
- ✅ คำนวณ flux ผ่าน surface fields สำหรับ conservation equations
- ✅ เขียน custom boundary conditions ที่เข้าถึง patch data
- ✅ ใช้ point fields สำหรับ dynamic meshing problems
- ✅ แก้ไข solver code เพื่อเพิ่ม functionality ใหม่

**Difficulty:** Intermediate | **Estimated Time:** 2-3 hours

---

## 📋 Learning Path

```
Prerequisites
    ↓
┌─────────────────────────────────────────────────────────────┐
│ 00_Overview.md (Read all reference tables)                  │
│ 02_Volume_Fields.md → 03_Surface_Fields.md → 05_Point_Fields.md │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│ Exercise 1-5: Foundational Skills (30 min)                  │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│ Capstone Project: Integration Challenge (90 min)            │
└─────────────────────────────────────────────────────────────┘
```

---

## 📝 Exercise 1: Field Creation and Case Integration

> [!NOTE] **📂 OpenFOAM Context: From Solver Code to Case Files**
> **Scenario:** คุณกำลังพัฒนา solver ใหม่สำหรับคำนวณ **turbulent kinetic energy production** ($P_k = -\tau_{ij} \frac{\partial u_i}{\partial x_j}$) และต้องการเพิ่ม field ใหม่ชื่อ `kProduction`
>
> **Domain E (Coding):** สร้าง field ใน solver
> ```cpp
> // ใน createFields.H ของ solver ของคุณ
> volScalarField kProduction
> (
>     IOobject
>     (
>         "kProduction",
>         runTime.timeName(),
>         mesh,
>         IOobject::NO_READ,  // ไม่ต้องอ่านจากไฟล์ (คำนวณเอง)
>         IOobject::AUTO_WRITE // เขียนลงไฟล์ output อัตโนมัติ
>     ),
>     mesh,
>     dimensionedScalar("zero", dimless/dimTime, scalar(0))
> );
> ```
>
> **Domain A (Case Files):** หลังจากรัน solver ไฟล์ output จะถูกสร้าง:
> ```
> 0.5/kProduction  ← output field file
> ├── dimensions      [0 0 -1 0 0 0 0]  (1/s)
> ├── internalField   uniform 0;
> └── boundaryField  { ... }
> ```

### โจทย์:
1. สร้าง `volScalarField temperatureVariance` สำหรับเก็บค่า $T'^2 = (T - \bar{T})^2$
2. กำหนด dimensions และ initial conditions ที่เหมาะสม
3. ระบุว่า field นี้ควรใช้ `MUST_READ` หรือ `NO_READ` และทำไม?

### 💡 Answer Key:
<details>
<summary>คลิกเพื่อดูเฉลย</summary>

```cpp
volScalarField temperatureVariance
(
    IOobject
    (
        "temperatureVariance",
        runTime.timeName(),
        mesh,
        IOobject::MUST_READ,  // อ่านค่าเริ่มต้นจากไฟล์ case
        IOobject::AUTO_WRITE
    ),
    mesh
);
```

- **Dimensions:** `[0 0 0 1 0 0 0]` (K²)
- **Initial value:** ในไฟล์ `0/temperatureVariance`:
  ```cpp
  internalField   uniform 0;  // เริ่มต้นที่ zero หาือไม่มีข้อมูล
  ```
- **MUST_READ vs NO_READ:** ใช้ `MUST_READ` ถ้าต้องการกำหนดค่าเริ่มต้นจาก case, ใช้ `NO_READ` ถ้าคำนวณจาก field อื่นทันที

</details>

---

## 📝 Exercise 2: Flux Computation for Conservation Equations

> [!NOTE] **📂 OpenFOAM Context: Mass Flux in Continuity Equation**
> **Scenario:** คุณกำลังพัฒนา **compressible solver** และต้องคำนวณ **mass flux** $\phi = \rho \mathbf{U} \cdot \mathbf{S}_f$ สำหรับ continuity equation: $\frac{\partial \rho}{\partial t} + \nabla \cdot (\rho \mathbf{U}) = 0$
>
> **Physical Meaning:**
> - $\phi$ = **mass flow rate** ผ่านแต่ละ face $[\text{kg}/\text{s}]$
> - $\sum \phi_f = 0$ สำหรับ **steady-state, incompressible flow** (conservation of mass)
>
> **Connection to Case Files:**
> - `0/phi` → ไฟล์ flux field (ถ้า solver ต้องการ initial guess)
> - `system/fvSchemes` → ระบุ interpolation scheme:
>   ```cpp
>   interpolationSchemes
>   {
>       default         linear;
>       interpolate(rho) linearUpwind grad(U);
>   }
>   ```

### โจทย์:
1. เขียน code สร้าง `surfaceScalarField massFlux` จาก `volScalarField rho` และ `volVectorField U`
2. คำนวณ **total mass flow rate** ผ่าน patch ชื่อ "inlet"
3. ตรวจสอบ mass balance: $\sum \phi_f \approx 0$ สำหรับ incompressible flow

### 💡 Answer Key:
<details>
<summary>คลิกเฉลยและคำอธิบาย</summary>

```cpp
// 1. Create mass flux
surfaceScalarField massFlux = fvc::interpolate(rho * U) & mesh.Sf();

// 2. Calculate total mass flow at inlet
label inletI = mesh.boundaryMesh().findPatchID("inlet");
scalar massFlowInlet = sum(massFlux.boundaryField()[inletI]);

Info << "Inlet mass flow rate: " << massFlowInlet << " kg/s" << endl;

// 3. Check mass balance (for incompressible)
scalar totalFlux = sum(massFlux);
Info << "Global mass balance: " << totalFlux << " (should be ~0)" << endl;
```

**Physical Interpretation:**
- `massFlux > 0` → flow **out of cell** (face normal points outward)
- `massFlux < 0` → flow **into cell**
- สำหรับ **steady-state incompressible**: $\sum_{\text{all faces}} \phi_f = 0$

</details>

---

## 📝 Exercise 3: Custom Boundary Condition Development

> [!NOTE] **📂 OpenFOAM Context: BC Code ↔ Case File Connection**
> **Scenario:** คุณต้องการสร้าง **time-varying velocity inlet** ที่ velocity ขึ้นกับ elevation (z-direction) เช่น atmospheric boundary layer: $u(z) = U_{ref} \left(\frac{z}{z_{ref}}\right)^\alpha$
>
> **Domain E (Coding):** สร้าง custom BC class
> ```cpp
> // ใน src/finiteVolume/fields/fvPatchFields/derived/myTimeVaryingInlet/
> class myTimeVaryingInletFvPatchVectorField
>     : public fixedValueFvPatchVectorField
> {
>     // Update coefficients จะถูกเรียกทุก time step
>     virtual void updateCoeffs();
> };
> ```
>
> **Domain A (Case Files):** ใช้ BC ใน `0/U`:
> ```cpp
> inlet
> {
>     type            myTimeVaryingInlet;
>     Uref            10.0;      // Reference velocity [m/s]
>     zref            10.0;      // Reference height [m]
>     alpha           0.14;      // Power law exponent
> }
> ```

### โจทย์:
1. เขียนฟังก์ชัน `updateCoeffs()` สำหรับ BC ดังกล่าว
2. ใช้ `patch().Cf()` (face centers) เพื่อเข้าถึง elevation ของแต่ละ face
3. ตรวจสอบว่า BC ของคุณถูก compile และ load ได้อย่างถูกต้อง

### 💡 Answer Key:
<details>
<summary>คำอธิบายแนวทางการแก้</summary>

```cpp
void myTimeVaryingInletFvPatchVectorField::updateCoeffs()
{
    if (this->updated())
    {
        return;  // Skip if already updated
    }
    
    // Get face centers (z-coordinate is component 2)
    const vectorField& faceCenters = patch().Cf();
    scalarField z = faceCenters.component(2);
    
    // Calculate velocity profile: U(z) = Uref * (z/zref)^alpha
    scalarField Uprofile = Uref_ * pow(z / zref_, alpha_);
    
    // Update boundary values
    vectorField::operator=(vector(Uprofile, scalar(0), scalar(0)));
    
    fixedValueFvPatchVectorField::updateCoeffs();
}
```

**Testing:**
```bash
# Compile custom BC
wmake libso

# ใน case directory:
# 0/U → type myTimeVaryingInlet;
# รัน solver และตรวจสอบ velocity profile
paraFoam -builtin
```

</details>

---

## 📝 Exercise 4: Point Fields for Dynamic Meshing

> [!NOTE] **📂 OpenFOAM Context: Mesh Motion via Point Displacement**
> **Scenario:** คุณกำลังจำลอง **oscillating airfoil** ที่ pitch รอบ leading edge แบบ sinusoidal: $\theta(t) = \theta_0 \sin(2\pi f t)$
>
> **Domain D (Meshing):** การเคลื่อนที่ของ mesh
> - **Point displacement:** $\mathbf{d}_p = \mathbf{R}(\theta) \cdot (\mathbf{x}_p - \mathbf{x}_{LE}) - (\mathbf{x}_p - \mathbf{x}_{LE})$
> - **Mesh quality:** ต้องตรวจสอบว่าไม่มี cells ที่ skew หรือ non-orthogonal มากเกินไป
>
> **Domain A (Case Files):** ระบุ dynamic mesh settings
> ```cpp
> // constant/dynamicMeshDict
> dynamicFvMesh   dynamicMotionSolverFvMesh;
> motionSolverLibs ("libfvMotionSolvers.so");
> solver          displacementLaplacian;
>
> // 0/pointDisplacement
> airfoil
> {
>     type            oscillatingDisplacement;
>     amplitude       0.1;      // [rad]
>     frequency       1.0;      // [Hz]
>     axis            (0 0 1);  // Pitch axis
> }
> ```

### โจทย์:
1. สร้าง `pointVectorField pointD` สำหรับเก็บ displacement
2. เขียน loop คำนวณ displacement สำหรับแต่ละ vertex ตาม pitch motion
3. ตรวจสอบ mesh quality หลังจาก motion: `checkMesh -allGeometry -allTopology`

### 💡 Answer Key:
<details>
<summary>แนวทางการแก้</summary>

```cpp
// Create point mesh
const pointMesh& pMesh = pointMesh::New(mesh);

// Point displacement field
pointVectorField pointD
(
    IOobject
    (
        "pointDisplacement",
        runTime.timeName(),
        mesh,
        IOobject::MUST_READ,
        IOobject::AUTO_WRITE
    ),
    pMesh,
    dimensionedVector("zero", dimLength, vector::zero)
);

// Calculate pitch displacement (simplified)
const pointField& points = mesh.points();
vectorField displacement(points.size());

vector LE(0, 0, 0);  // Leading edge position
scalar theta = theta0_ * sin(2 * M_PI * f_ * runTime.value());

forAll(points, i)
{
    vector r0 = points[i] - LE;
    scalar x0 = r0.x();
    scalar y0 = r0.y();
    
    // Rotation matrix (2D)
    displacement[i] = vector(
        x0 * cos(theta) - y0 * sin(theta) - x0,
        x0 * sin(theta) + y0 * cos(theta) - y0,
        0
    );
}

pointD = displacement;
pointD.correctBoundaryConditions();
```

**Mesh Quality Check:**
```bash
checkMesh -allGeometry -allTopology -time 0.1
# ตรวจสอบ: Max non-orthogonality < 70°, Max skewness < 4
```

</details>

---

## 🚀 Capstone Project: Turbulent Channel Flow with Custom Post-Processing

> [!NOTE] **📂 OpenFOAM Context: Integration Across All Domains**
> **Project Overview:** พัฒนา **function object** สำหรับวิเคราะห์ turbulent channel flow โดยคำนวณ:
> 1. **Wall friction velocity:** $u_\tau = \sqrt{\tau_w / \rho}$
> 2. **Dimensionless wall distance:** $y^+ = \frac{y u_\tau}{\nu}$
> 3. **Velocity profile:** $u^+(y^+) = \frac{\bar{u}}{u_\tau}$
>
> **Domains Involved:**
> - **Domain A (Physics):** Turbulent boundary layer theory
> - **Domain D (Meshing):** Near-wall mesh resolution
> - **Domain E (Coding):** Custom function object implementation

### โจทย์:
1. **Part 1: Field Computation (30 min)**
   - สร้าง `volScalarField uTau` จาก wall shear stress: $\tau_w = \mu \frac{\partial u}{\partial y}|_{wall}$
   - ใช้ `T.boundaryField()[wallI].snGrad()` เพื่อคำนวณ gradient
   - คำนวณ `volScalarField yPlus` สำหรับทุก cell

2. **Part 2: Integration with Case Files (20 min)**
   - เขียน configuration ใน `system/controlDict` สำหรับ function object
   - ระบุ output directory สำหรับผลลัพธ์: `postProcessing/wallProfiles/`
   - เชื่อมต่อกับ field files: `0/U`, `0/nuSgs`

3. **Part 3: Validation and Verification (20 min)**
   - เปรียบเทียบ $u^+(y^+)$ กับ **law of the wall**: $u^+ = \frac{1}{\kappa} \ln y^+ + B$
   - ตรวจสอบว่า $y^+_{\text{first cell}} \approx 1$ สำหรับ low-Reynolds simulation
   - วิเคราะห์ mesh independence: ทดลองกับ $\Delta y$ ต่างกัน

### 💡 Starter Code:

```cpp
// ใน custom function object: calcWallProfile.C
const volScalarField::Boundary& wallGradU = U.boundaryField();

label wallI = mesh.boundaryMesh().findPatchID("walls");
scalarField tauW = mu.boundaryField()[wallI] * wallGradU[wallI].snGrad();

volScalarField uTau
(
    IOobject("uTau", runTime.timeName(), mesh),
    mesh,
    dimensionedScalar("zero", dimVelocity, scalar(0))
);

// Continue implementation...
```

### 📊 Expected Output:
```
postProcessing/wallProfiles/
├── 0.1/
│   ├── uTau       (scalarField at wall)
│   ├── yPlus      (volScalarField)
│   └── uPlus_vs_yPlus (data for plotting)
```

### 🎯 Success Criteria:
- ✅ Function object compile และ run ได้
- ✅ $y^+ < 1$ สำหรับ first cell near wall
- ✅ $u^+$ profile ตรงกับ law of the wall (within 10%)
- ✅ Code เชื่อมต่อกับ case files อย่างถูกต้อง

---

## 🧠 Concept Check

<details>
<summary><b>1. ทำไม flux field (surfaceScalarField) จำเป็นสำหรับ conservation equations?</b></summary>

เพราะ conservation laws (mass, momentum, energy) ถูกเขียนในรูป **divergence form**: $\nabla \cdot \mathbf{F}$ ซึ่งใน Finite Volume Method แปลงเป็น **sum of fluxes** ผ่าน faces: $\sum_f \mathbf{F}_f \cdot \mathbf{S}_f$

**Connection to physics:**
- Mass conservation: $\sum \phi_f = 0$ (incompressible)
- Momentum conservation: $\sum (\rho \mathbf{U} \mathbf{U})_f \cdot \mathbf{S}_f = \text{forces}$
</details>

<details>
<summary><b>2. แบบไหนของ field ควรใช้ MUST_READ vs NO_READ?</b></summary>

| Field Type | IOobject::MUST_READ | IOobject::NO_READ |
|------------|---------------------|-------------------|
| **Primary physics fields** (`p`, `U`, `T`) | ✅ อ่าน initial/boundary conditions จาก `0/` | ❌ |
| **Derived/calculated fields** (`kProduction`, `uTau`) | ❌ (optional) | ✅ คำนวณจาก fields อื่น |
| **Output-only fields** (`residuals`, `yPlus`) | ❌ | ✅ |

**Decision tree:**
1. Field นี้ต้องการ **user-specified initial values** ใน case? → `MUST_READ`
2. Field นี้คำนวณ **จาก fields อื่นทันที**? → `NO_READ`
3. Field นี้เป็น **intermediate field** สำหรับ solver? → `NO_READ, AUTO_WRITE`
</details>

<details>
<summary><b>3. ทำไม point fields จำเป็นสำหรับ dynamic meshing?</b></summary>

เพราะ **mesh deformation** ต้องการ displacement ของ **vertices** (ไม่ใช่ cell centers)

**Key differences:**
- **Volume fields:** ค่าที่ cell centers → ใช้สำหรับ physics equations (Navier-Stokes)
- **Point fields:** ค่าที่ mesh vertices → ใช้สำหรับ mesh motion, FEM

**Connection to case files:**
- `0/pointDisplacement` → ระบุ displacement BC สำหรับ patches
- `constant/dynamicMeshDict` → ระบุ motion solver (e.g., `displacementLaplacian`)
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md) - ดูตาราง reference ทั้งหมด
- **Volume Fields:** [02_Volume_Fields.md](02_Volume_Fields.md) - cell-centered storage
- **Surface Fields:** [03_Surface_Fields.md](03_Surface_Fields.md) - flux computation
- **Point Fields:** [05_Point_Fields.md](05_Point_Fields.md) - dynamic meshing

---

## 🎓 Key Takeaways

### ✅ สิ่งที่คุณควรได้เรียนรู้:

1. **Field Creation Pattern:**
   ```cpp
   IOobject(name, timeName, mesh, READ/WRITE flags) → mesh → dimensions/initialValue
   ```

2. **Flux Computation:**
   ```cpp
   phi = fvc::interpolate(rho * U) & mesh.Sf();  // Mass flux [kg/s]
   ```

3. **Boundary Access:**
   ```cpp
   mesh.boundaryMesh().findPatchID("name") → patchI
   field.boundaryField()[patchI] → boundary values
   ```

4. **Code ↔ Case Connection:**
   - C++ fields ↔ `0/` directory files
   - Interpolation schemes ↔ `system/fvSchemes`
   - BC types ↔ `src/finiteVolume/fields/fvPatchFields/`

### 🔍 Common Pitfalls to Avoid:
- ❌ ลืมระบุ `dimensionSet` → จะได้ **dimension inconsistency** errors
- ❌ ใช้ `fvc::interpolate` ผิด scheme → ได้ **numerical diffusion**
- ❌ ไม่เชื่อมต่อ BC code กับ case files → **runtime error**
- ❌ คำนวณ flux โดยไม่คำนึงถึง **face normal direction**

---

## 📚 Additional Resources

### OpenFOAM Source Code:
- **Field definitions:** `src/finiteVolume/fields/volFields/volFields.H`
- **Surface fields:** `src/finiteVolume/fields/surfaceFields/surfaceFields.H`
- **Point mesh:** `src/meshes/pointMesh/pointMesh.H`
- **Boundary conditions:** `src/finiteVolume/fields/fvPatchFields/`

### Case File Locations:
- **Field files:** `0/p`, `0/U`, `0/phi`
- **Schemes:** `system/fvSchemes`, `system/fvSolution`
- **Mesh:** `constant/polyMesh/boundary`

### Next Steps:
1. ลองแก้โจทย์ Capstone Project ใน solver จริง (e.g., `pimpleFoam`)
2. ดูตัวอย่าง function objects ใน `src/OpenFOAM/db/functionObjects/`
3. ศึกษา custom BC ใน `tutorials/` เช่น `boundaryConditions/`