# 01 Testing Fundamentals (พื้นฐานการทดสอบ)

> [!INFO] Module Focus
> การสร้างความเชื่อถือได้ (Reliability) ให้กับซอฟต์แวร์ CFD ผ่านกระบวนการทดสอบซอฟต์แวร์ (Software Testing) และความเข้าใจในหลักการ Verfication และ Validation

## 🎯 วัตถุประสงค์การเรียนรู้ (Learning Objectives)
- เข้าใจความแตกต่างระหว่าง **Verification** (การตรวจสอบความถูกต้องของโค้ด) และ **Validation** (การตรวจสอบความสอดคล้องกับฟิสิกส์จริง)
- เชี่ยวชาญวิธีการ **MMS** (Method of Manufactured Solutions) สำหรับการทดสอบความถูกต้องของ solver
- เข้าใจหลักการ **Grid Convergence Study** และการคำนวณ **GCI** (Grid Convergence Index)
- สามารถออกแบบและดำเนินการทดสอบเชิงตัวเลข (Numerical Verification) สำหรับ OpenFOAM solvers
- เข้าใจแนวคิด **Order of Accuracy** และ **Consistency** ของระเบียบวิธีเชิงตัวเลข
- สามารถวิเคราะห์ **Error Norms** ($L_1, L_2, L_\infty$) และตีความผลลัพธ์การทดสอบ

## 📋 ข้อกำหนดเบื้องต้น (Prerequisites)
- ความเข้าใจในการใช้งาน OpenFOAM และโครงสร้างไฟล์ case
- พื้นฐานการเขียนโปรแกรม C++
- ความเข้าใจในระเบียบวิธีเชิงตัวเลข (Numerical Methods) สำหรับ CFD
- ความรู้เบื้องต้นเกี่ยวกับ partial differential equations (PDEs)
- ความเข้าใจเรื่อง discretization (Finite Volume Method)

---

## 📚 หัวข้อทางเทคนิค (Technical Topics)

### 01 [[01_Introduction_to_Verification|บทนำสู่การตรวจสอบความถูกต้อง]]
แนวคิดพื้นฐานของการทดสอบซอฟต์แวร์ CFD ความแตกต่างระหว่าง Verification และ Validation และบทบาทของการทดสอบในวงจรพัฒนาซอฟต์แวร์

### 02 [[02_Numerical_Verification_Methods|วิธีการตรวจสอบทางตัวเลข]]
เจาะลึก Method of Manufactured Solutions (MMS), Richardson Extrapolation, และ Grid Convergence Index (GCI) สำหรับการยืนยันความถูกต้องของ solver

### 03 [[03_OpenFOAM_Test_Architecture|สถาปัตยกรรมระบบทดสอบ OpenFOAM]]
สำรวจโครงสร้างไดเรกทอรี `applications/test` และวิธีการใช้งาน test framework ที่มีอยู่ใน OpenFOAM

---

## 🔬 แนวคิดหลัก (Core Concepts)

### Verification vs Validation

ในวงการ CFD มีการแยกแยะระหว่างสองแนวคิดสำคัญ:

**Verification** (ตรวจสอบความถูกต้องของโค้ด):
- ตอบคำถาม: *"Are we solving the equations right?"*
- เปรียบเทียบผลลัพธ์เชิงตัวเลขกับโซลูชันแม่นตำรา (analytical solutions)
- ตรวจสอบว่า discretization scheme ถูกต้องหรือไม่
- ไม่เกี่ยวข้องกับฟิสิกส์จริง แต่เกี่ยวกับความถูกต้องทางคณิตศาสตร์
- เป็นการทดสอบ **Code** และ **Calculation**

**Validation** (ตรวจสอบความสอดคล้องกับฟิสิกส์):
- ตอบคำถาม: *"Are we solving the right equations?"*
- เปรียบเทียบผลลัพธ์ CFD กับ experimental data
- ตรวจสอบว่าโมเดลทางฟิสิกส์ (turbulence models, multiphase models) แม่นยำพอ
- เกี่ยวข้องกับความสอดคล้องกับโลกแห่งความจริง
- เป็นการทดสอบ **Model** และ **Physics**

> **[!IMPORTANT] V-Model ใน CFD**
> แนวคิดนี้มักถูกแสดงด้วย **V-Model** ซึ่งแสดงความสัมพันธ์ระหว่างการพัฒนาและการทดสอบ แขนลงมาด้านซ้ายคือการพัฒนา (requirement → design → implementation) ส่วนแขนขึ้นด้านขวาคือการทดสอบ (unit testing → integration testing → system testing)

> [!TIP] เปรียบเทียบ: การสร้างสะพาน (Bridge Building Analogy)
> - **Verification**: เหมือนวิศวกรโครงสร้างที่คำนวณซ้ำแล้วซ้ำอีกว่า "เหล็กเบอร์นี้รับน้ำหนักได้ 10 ตันตามสูตรฟิสิกส์จริงหรือไม่?" (เช็คสูตรและการคำนวณ)
> - **Validation**: เหมือนการนำรถบรรทุกหนัก 10 ตันไปวิ่งบนสะพานจริงเพื่อดูว่า "สะพานถล่มไหม?" (เช็คกับความจริง)
> ถ้าคำนวณผิด (Verification fail) สะพานอาจถล่มตั้งแต่ในกระดาษ
> ถ้าคำนวณถูกแต่เลือกโมเดลเหล็กผิด (Validation fail) สะพานจริงก็อาจถล่มได้แม้คำนวณถูกเป๊ะ

### หลักการสำคัญของ Verification

**1. Consistency (ความสอดคล้อง):**
ระเบียบวิธีเชิงตัวเลขจะต้องลู่เสมอไปยังสมการเชิงอนุพันธ์เมื่อ $\Delta x, \Delta t \to 0$

**2. Stability (เสถียรภาพ):**
ความผิดพลาดไม่เติบโตแบบไม่มีขอบเขตเมื่อการจำลองดำเนินไป

**3. Convergence (การลู่เข้า):**
$$ \lim_{\Delta x \to 0} \| \phi_{numerical} - \phi_{exact} \| = 0 $$

---

## 📐 วิธีการตรวจสอบเชิงตัวเลข (Numerical Verification Methods)

### 1. Method of Manufactured Solutions (MMS)

MMS เป็นเทคนิคที่ทรงพลังสำหรับการทดสอบความถูกต้องของ solver:

**แนวคิดพื้นฐาน:**
1. เลือกฟังก์ชันโซลูชันที่ต้องการ $\tilde{\phi}(x,t)$
2. แทนฟังก์ชันนี้ลงในสมการของเรา เพื่อคำนวณ source term $S(x,t)$
3. ใช้ $S(x,t)$ นี้เป็น forcing term ในการจำลอง
4. เปรียบเทียบผลลัพธ์การจำลองกับ $\tilde{\phi}(x,t)$

**ตัวอย่างสำหรับสมการ Diffusion:**

สมการทั่วไป:
$$ \frac{\partial \phi}{\partial t} = \alpha \nabla^2 \phi + S $$

เลือกโซลูชันที่ต้องการ:
$$ \tilde{\phi}(x,y,t) = \sin(\pi x) \sin(\pi y) e^{-t} $$

คำนวณ source term:
$$ S(x,y,t) = \frac{\partial \tilde{\phi}}{\partial t} - \alpha \nabla^2 \tilde{\phi} $$

ดำเนินการ:
$$ \frac{\partial \tilde{\phi}}{\partial t} = -\sin(\pi x)\sin(\pi y)e^{-t} $$

$$ \frac{\partial^2 \tilde{\phi}}{\partial x^2} = -\pi^2\sin(\pi x)\sin(\pi y)e^{-t} $$

$$ \frac{\partial^2 \tilde{\phi}}{\partial y^2} = -\pi^2\sin(\pi x)\sin(\pi y)e^{-t} $$

$$ \nabla^2 \tilde{\phi} = -2\pi^2\sin(\pi x)\sin(\pi y)e^{-t} $$

จะได้:
$$ S(x,y,t) = -\sin(\pi x)\sin(\pi y)e^{-t} + 2\alpha\pi^2\sin(\pi x)\sin(\pi y)e^{-t} $$

$$ S(x,y,t) = \sin(\pi x)\sin(\pi y)e^{-t}(2\alpha\pi^2 - 1) $$

**ข้อดีของ MMS:**
- สามารถใช้กับ PDE ที่ซับซ้อนซึ่งไม่มี analytical solution
- สามารถทดสอบทุกส่วนของ solver (temporal, spatial, source terms)
- โซลูชันสามารถออกแบบให้มีความซับซ้อนตามต้องการ

**Error Norms สำหรับ MMS:**

$$ L_1 = \frac{1}{N} \sum_{i=1}^{N} |\phi_i - \tilde{\phi}_i| $$

$$ L_2 = \sqrt{\frac{1}{N} \sum_{i=1}^{N} (\phi_i - \tilde{\phi}_i)^2} $$

$$ L_\infty = \max_{i} |\phi_i - \tilde{\phi}_i| $$

### 2. Grid Convergence Study

การศึกษาความเข้าใจความละเอียดของ grid (mesh refinement) เป็นสิ่งจำเป็น:

**ขั้นตอนการดำเนินการ:**
1. สร้าง 3 เมชหรือมากกว่าที่มีความละเอียดแตกต่างกัน (coarse, medium, fine)
2. ดำเนินการจำลองและบันทึกค่าที่สนใจ (เช่น drag coefficient, velocity ที่จุดหนึ่ง)
3. คำนวณอัตราส่วนการลดขนาด $r = h_{coarse}/h_{fine}$
4. วิเคราะห์ความเข้าใจความละเอียด

**Order of Accuracy:**

สำหรับสามเมช (3-grid study):
$$ p = \frac{\ln\left(\frac{f_3 - f_2}{f_2 - f_1}\right)}{\ln(r)} $$

เมื่อ:
- $f_1$ = ค่าจาก fine mesh
- $f_2$ = ค่าจาก medium mesh
- $f_3$ = ค่าจาก coarse mesh
- $r$ = refinement ratio

**Grid Convergence Index (GCI):**

$$ GCI_{fine} = \frac{F_s |e|}{r^p - 1} $$

$$ e_{21} = \left| \frac{f_1 - f_2}{f_1} \right| $$

$$ GCI_{21} = \frac{1.25 e_{21}}{r^p - 1} $$

เมื่อ:
- $F_s$ = factor ความปลอดภัย (มักใช้ 1.25 สำหรับการใช้งานทั่วไป)
- $e$ = relative error ระหว่างเมช
- $r$ = refinement ratio
- $p$ = order of accuracy

**การตรวจสอบ Asymptotic Range:**

เพื่อให้มั่นใจว่าอยู่ใน asymptotic range:
$$ \frac{GCI_{32}}{r^p \times GCI_{21}} \approx 1 $$

ถ้าค่านี้อยู่ระหว่าง 0.9 ถึง 1.1 แสดงว่าอยู่ใน asymptotic range

### 3. Richardson Extrapolation

ใช้สำหรับประมาณค่าที่ไม่มีตัวตน (grid-independent solution):

$$ \phi_{ext} = \phi_{fine} + \frac{\phi_{fine} - \phi_{coarse}}{r^p - 1} $$

**Error Estimate:**

$$ \varepsilon_{ext} = \frac{|\phi_{fine} - \phi_{coarse}|}{r^p - 1} $$

**Uncertainty จาก Grid:**

$$ U_G = F_s \left| \frac{f_2 - f_1}{r^p - 1} \right| $$

---

## 🛠️ ตัวอย่างการนำไปใช้ใน OpenFOAM (Practical Implementation)

### ตัวอย่าง 1: การตั้งค่า MMS สำหรับ Scalar Transport Solver

```cpp
// NOTE: AI-generated code - Verify parameters
// File: createFields.H in test case

// Create temperature field with IOobject for proper I/O handling
volScalarField T
(
    IOobject
    (
        "T",                           // Field name
        runTime.timeName(),            // Time directory
        mesh,                          // Mesh reference
        IOobject::MUST_READ,           // Must read from file
        IOobject::AUTO_WRITE           // Auto-write on output
    ),
    mesh
);

// Manufactured solution field (exact analytical solution)
volScalarField T_exact
(
    IOobject
    (
        "T_exact",                     // Field name for exact solution
        runTime.timeName(),            // Time directory
        mesh,                          // Mesh reference
        IOobject::NO_READ,             // Don't read from file
        IOobject::AUTO_WRITE           // Auto-write for comparison
    ),
    mesh,
    dimensionedScalar("zero", dimTemperature, 0.0)  // Initialize to zero
);

// Source term field from MMS procedure
volScalarField sourceTerm
(
    IOobject
    (
        "sourceTerm",                  // Field name for source term
        runTime.timeName(),            // Time directory
        mesh,                          // Mesh reference
        IOobject::NO_READ,             // Don't read from file
        IOobject::AUTO_WRITE           // Auto-write for debugging
    ),
    mesh,
    dimensionedScalar("zero", dimTemperature/dimTime, 0.0)  // Initialize to zero
);

// Calculate manufactured solution and corresponding source term
const volVectorField& C = mesh.C();    // Get cell centers
scalarField& T_exact_cells = T_exact.primitiveFieldRef();
scalarField& source_cells = sourceTerm.primitiveFieldRef();

forAll(T_exact_cells, celli)
{
    scalar x = C[celli].x();           // Cell center x-coordinate
    scalar y = C[celli].y();           // Cell center y-coordinate
    scalar t = runTime.value();        // Current simulation time

    // Manufactured solution: T = sin(πx)sin(πy)e^(-t)
    T_exact_cells[celli] = sin(M_PI*x) * sin(M_PI*y) * exp(-t);

    // Source term derived from MMS: S = -T + 2*π²*T
    source_cells[celli] = -T_exact_cells[celli] + 
                          2.0*M_PI*M_PI*T_exact_cells[celli];
}
```

> **📂 Source:** OpenFOAM Field Initialization Pattern
> 
> **คำอธิบาย (Thai):**
> โค้ดนี้สาธิตวิธีการสร้าง field objects ใน OpenFOAM สำหรับการทดสอบ MMS:
> 
> **ส่วนประกอบหลัก:**
> 1. **volScalarField T** - Field อุณหภูมิหลักที่จะถูกแก้สมการ
> 2. **volScalarField T_exact** - Field สำหรับเก็บโซลูชันแม่นตำราที่ต้องการ
> 3. **volScalarField sourceTerm** - Source term ที่คำนวณจาก MMS procedure
> 
> **ขั้นตอนสำคัญ:**
> - ใช้ `IOobject` เพื่อกำหนดวิธีการอ่าน/เขียน field (MUST_READ, NO_READ, AUTO_WRITE)
> - ใช้ `dimensionedScalar` เพื่อกำหนด dimension ของ field (temperature, temperature/time)
> - ใช้ `mesh.C()` เพื่อเข้าถึง cell center coordinates
> - ใช้ `primitiveFieldRef()` เพื่อแก้ไขค่าใน cell โดยตรง
> - คำนวณ source term จากสมการ: $S = \frac{\partial \tilde{T}}{\partial t} - \alpha \nabla^2 \tilde{T}$
> 
> **แนวคิดสำคัญ:**
> - MMS ต้องการให้เราเลือกฟังก์ชันโซลูชันที่ต้องการก่อน แล้วคำนวณ source term ที่ทำให้ฟังก์ชันนั้นเป็น solution
> - Source term นี้จะถูกใส่เป็น forcing term ในสมการ transport

### ตัวอย่าง 2: การกำหนด Boundary Conditions สำหรับ MMS

```cpp
// NOTE: AI-generated code - Verify parameters
// File: 0/T

dimensions      [0 0 0 1 0 0 0];        // Temperature dimensions [K]

internalField   uniform 0;              // Initial field value

boundaryField
{
    // Dirichlet BC with codedFixedValue for exact solution enforcement
    inlet
    {
        type            codedFixedValue;
        value           uniform 0;
        code
        #{
            // Get current time from database
            const scalar t = this->db().time().value();
            // Get face centers for this patch
            const vectorField& C = this->patch().Cf();
            // Reference to field values being set
            scalarField& Tfield = *this;

            forAll(Tfield, facei)
            {
                scalar x = C[facei].x();     // Face center x-coordinate
                scalar y = C[facei].y();     // Face center y-coordinate
                // Manufactured solution: T = sin(πx)sin(πy)e^(-t)
                Tfield[facei] = sin(M_PI*x) * sin(M_PI*y) * exp(-t);
            }
        #};
    }

    outlet
    {
        type            codedFixedValue;
        value           uniform 0;
        code
        #{
            const scalar t = this->db().time().value();
            const vectorField& C = this->patch().Cf();
            scalarField& Tfield = *this;

            forAll(Tfield, facei)
            {
                scalar x = C[facei].x();
                scalar y = C[facei].y();
                Tfield[facei] = sin(M_PI*x) * sin(M_PI*y) * exp(-t);
            }
        #};
    }

    walls
    {
        type            codedFixedValue;
        value           uniform 0;
        code
        #{
            const scalar t = this->db().time().value();
            const vectorField& C = this->patch().Cf();
            scalarField& Tfield = *this;

            forAll(Tfield, facei)
            {
                scalar x = C[facei].x();
                scalar y = C[facei].y();
                Tfield[facei] = sin(M_PI*x) * sin(M_PI*y) * exp(-t);
            }
        #};
    }
}
```

> **📂 Source:** OpenFOAM Boundary Condition System
> 
> **คำอธิบาย (Thai):**
> โค้ดนี้แสดงการใช้ `codedFixedValue` boundary condition ใน OpenFOAM สำหรับ MMS:
> 
> **แนวคิดสำคัญ:**
> - **codedFixedValue** ช่วยให้เราสามารถกำหนดค่า BC ด้วย C++ code โดยตรง
> - เหมาะสำหรับ MMS เพราะสามารถใส่ analytical solution ที่ boundary ได้
> - ทำให้ไม่ต้องสร้าง BC file แยกสำหรับแต่ละ time step
> 
> **ส่วนประกอบ:**
> 1. **this->db().time().value()** - เข้าถึง simulation time
> 2. **this->patch().Cf()** - เข้าถึง face centers ของ patch
> 3. ***this** - Reference ไปยัง field values ที่จะถูก set
> 4. **forAll loop** - วนลูปผ่านทุก face ใน patch
> 
> **ข้อดี:**
> - ไม่ต้อง recompile solver
> - แก้ไขได้โดยตรงใน dictionary file
> - ยืดหยุ่นสูงมากสำหรับ verification
> 
> **หมายเหตุ:**
> - coded BC จะถูก compile ครั้งแรกที่รัน อาจใช้เวลานานขึ้นเล็กน้อย
> - สามารถ debug ได้โดยดูไฟล์ที่ถูก generate ใน `-codedBoundaryConditions/`

### ตัวอย่าง 3: fvSchemes สำหรับ Grid Convergence Study

```cpp
// NOTE: AI-generated code - Verify parameters
// File: system/fvSchemes

// Temporal discretization schemes
ddtSchemes
{
    default         Euler;          // First-order implicit for convergence study
}

// Gradient calculation schemes
gradSchemes
{
    default         Gauss linear;   // Second-order central differencing
}

// Divergence (convection) schemes
divSchemes
{
    default         none;
    div(phi,T)      Gauss upwind;   // First-order upwind for verification
    // div(phi,T)   Gauss linear;    // Uncomment for second-order test
}

// Laplacian (diffusion) schemes
laplacianSchemes
{
    default         Gauss linear corrected;  // Second-order with non-orthogonal correction
}

// Interpolation schemes (face to cell)
interpolationSchemes
{
    default         linear;         // Linear interpolation
}

// Surface normal gradient schemes
snGradSchemes
{
    default         corrected;      // Non-orthogonal correction applied
}
```

> **📂 Source:** OpenFOAM Discretization Schemes
> 
> **คำอธิบาย (Thai):**
> ไฟล์ `fvSchemes` ครอบคลุมการกำหนดระเบียบวิธีเชิงตัวเลขทั้งหมดใน OpenFOAM:
> 
> **หมวดหมู่ schemes:**
> 
> **1. ddtSchemes (Temporal Discretization):**
> - **Euler**: First-order implicit ($O(\Delta t)$)
> - **backward**: Second-order implicit ($O(\Delta t^2)$)
> - **CrankNicolson**: Second-order trapezoidal
> 
> **2. gradSchemes (Spatial Gradients):**
> - **Gauss linear**: Second-order central differencing
> - **Gauss upwind**: First-order upwind
> - **leastSquares**: Fourth-order (สำหรับ structured meshes)
> 
> **3. divSchemes (Convective Terms):**
> - **Gauss upwind**: First-order, stable, diffusive
> - **Gauss linear**: Second-order, less diffusive
> - **Gauss linearUpwind**: Second-order with upwind bias
> - **Gauss QUICK**: Third-order (Quadratic Upwind Interpolation)
> 
> **4. laplacianSchemes (Diffusive Terms):**
> - **Gauss linear**: Second-order basic
> - **Gauss linear corrected**: รวม non-orthogonal correction
> 
> **แนวทางสำหรับ Verification:**
> - เริ่มด้วย first-order schemes เพื่อ confirm basic correctness
> - หลังจากนั้นทดสอบ higher-order schemes
> - ตรวจสอบว่า observed order ตรงกับ theoretical order
> 
> **ข้อควรระวัง:**
> - High-order schemes อาจไม่ stable บน meshes ที่มีคุณภาพต่ำ
> - Non-orthogonal correction จำเป็นสำหรับ highly non-orthogonal meshes

### ตัวอย่าง 4: fvSolution สำหรับ Verification

```cpp
// NOTE: AI-generated code - Verify parameters
// File: system/fvSolution

// Linear solver settings for each variable
solvers
{
    T
    {
        solver          GAMG;              // Geometric-Algebraic Multi-Grid
        tolerance       1e-12;             // Tight absolute tolerance for verification
        relTol          0.0;               // Disable relative tolerance (use absolute only)
        smoother        GaussSeidel;       // Smoother for GAMG

        // For verification, use very strict tolerances
        // This ensures errors come from discretization, not linear solver
    }
}

// Settings for SIMPLE-like algorithms
SIMPLE
{
    nNonOrthogonalCorrectors 0;            // Non-orthogonal correction iterations
    consistent      yes;                   // Use consistent SIMPLE algorithm
}
```

> **📂 Source:** OpenFOAM Linear Solver Configuration
> 
> **คำอธิบาย (Thai):**
> ไฟล์ `fvSolution` กำหนดวิธีการแก้สมการเชิงเส้นและ algorithm settings:
> 
> **Linear Solvers:**
> 
> **1. GAMG (Geometric-Algebraic Multi-Grid):**
> - เหมาะสำหรับ large systems และ elliptic equations (เช่น pressure, diffusion)
> - ใช้ hierarchy of grids ในการ accelerate convergence
> - มักใช้เวลา $O(N)$ แทน $O(N^2)$
> 
> **2. smoothSolver:**
> - ใช้สำหรับ small to medium systems
> - Smoother options: GaussSeidel, DIC, DICGaussSeidel
> 
> **3. PCG (Preconditioned Conjugate Gradient):**
> - สำหรับ symmetric matrices
> - Preconditioners: DIC, GAMG
> 
> **Tolerance Settings สำหรับ Verification:**
> 
> **Absolute vs Relative Tolerance:**
> - **tolerance (absolute)**: พยายามลด residual ต่ำกว่าค่านี้
> - **relTol (relative)**: หยุดเมื่อ residual ลดลงถึง factor นี้จากค่าเริ่มต้น
> 
> **กฎสำคัญ:**
> - **Verification**: ใช้ `relTol = 0` เพื่อให้ linear solver ลู่เข้าสู่ absolute tolerance
> - **Production runs**: ใช้ `relTol = 0.01` ถึง `0.1` เพื่อประหยัดเวลา
> - **tolerance** ควรต่ำกว่า expected discretization error อย่างน้อย 1-2 orders
> 
> **ตัวอย่าง:**
> - ถ้าคาดว่า discretization error ~ 1e-4
> - ใช้ tolerance = 1e-6 ถึง 1e-8
> - ใช้ relTol = 0.0 สำหรับ verification

### ตัวอย่าง 5: การเขียน Script สำหรับ GCI Calculation

```python
# NOTE: AI-generated code - Verify parameters
# File: calculate_gci.py

import numpy as np
import pandas as pd

def calculate_gci(fine, medium, coarse, r=2.0, fs=1.25):
    """
    Calculate Grid Convergence Index (GCI)
    
    Parameters:
    -----------
    fine : float - Value from fine mesh
    medium : float - Value from medium mesh
    coarse : float - Value from coarse mesh
    r : float - Refinement ratio (default: 2.0)
    fs : float - Safety factor (default: 1.25)
    
    Returns:
    --------
    dict : GCI values and order of convergence
    """
    # Calculate order of convergence from three grids
    epsilon1 = abs(fine - medium)
    epsilon2 = abs(medium - coarse)
    
    # Prevent division by zero
    if epsilon1 < 1e-15 or epsilon2 < 1e-15:
        raise ValueError("Errors too small - check mesh refinement")
    
    # Order of convergence from Richardson extrapolation theory
    p = np.log(epsilon2 / epsilon1) / np.log(r)
    print(f"Order of convergence (p): {p:.3f}")
    
    # GCI for fine-medium pair
    gci_fine = (fs * epsilon1) / (r**p - 1)
    
    # GCI for medium-coarse pair
    gci_coarse = (fs * epsilon2) / (r**p - 1)
    
    # Check asymptotic range (should be close to 1)
    asymptotic_ratio = gci_coarse / (r**p * gci_fine)
    
    results = {
        'p': p,
        'GCI_fine': gci_fine,
        'GCI_coarse': gci_coarse,
        'asymptotic_ratio': asymptotic_ratio,
        'asymptotic_range': 0.9 < asymptotic_ratio < 1.1,
        'richardson_extrapolation': fine + (fine - medium) / (r**p - 1)
    }
    
    return results

def calculate_error_norms(numerical, exact):
    """
    Calculate error norms for MMS verification
    
    Parameters:
    -----------
    numerical : array - Values from simulation
    exact : array - Exact solution values
    
    Returns:
    --------
    dict : L1, L2, L_infinity norms
    """
    abs_error = np.abs(numerical - exact)
    
    # L1 norm: average absolute error
    l1_norm = np.mean(abs_error)
    
    # L2 norm: RMS error
    l2_norm = np.sqrt(np.mean(abs_error**2))
    
    # L_infinity norm: maximum absolute error
    linf_norm = np.max(abs_error)
    
    return {
        'L1': l1_norm,
        'L2': l2_norm,
        'L_inf': linf_norm
    }

# Example usage
if __name__ == "__main__":
    # Example: drag coefficient from three meshes
    cd_fine = 0.3245
    cd_medium = 0.3312
    cd_coarse = 0.3456
    
    results = calculate_gci(cd_fine, cd_medium, cd_coarse)
    
    print("\n=== Grid Convergence Study Results ===")
    print(f"Fine mesh value:   {cd_fine:.4f}")
    print(f"Medium mesh value: {cd_medium:.4f}")
    print(f"Coarse mesh value: {cd_coarse:.4f}")
    print(f"\nOrder of convergence (p): {results['p']:.3f}")
    print(f"GCI_fine (21):        {results['GCI_fine']:.4%}")
    print(f"GCI_coarse (32):      {results['GCI_coarse']:.4%}")
    print(f"Asymptotic ratio:     {results['asymptotic_ratio']:.3f}")
    print(f"Asymptotic range:     {results['asymptotic_range']}")
    print(f"Richardson extrapolation: {results['richardson_extrapolation']:.4f}")
    
    # Example: error norms calculation for MMS
    print("\n=== MMS Error Norms ===")
    numerical = np.array([0.98, 1.02, 0.99, 1.01])
    exact = np.array([1.0, 1.0, 1.0, 1.0])
    errors = calculate_error_norms(numerical, exact)
    print(f"L1 norm:    {errors['L1']:.6f}")
    print(f"L2 norm:    {errors['L2']:.6f}")
    print(f"L_inf norm: {errors['L_inf']:.6f}")
```

> **📂 Source:** Grid Convergence Methodology
> 
> **คำอธิบาย (Thai):**
> Python script นี้ครอบคลุมการคำนวณที่สำคัญสำหรับ verification ใน CFD:
> 
> **ส่วนที่ 1: calculate_gci()**
> 
> **Grid Convergence Index (GCI):**
> - เป็นมาตรฐาน industry standard สำหรับ reporting discretization error
> - ถูกเสนอโดย Roache (1998) และได้รับการยอมรับอย่างกว้างขวาง
> 
> **ขั้นตอนการคำนวณ:**
> 1. หาค่า error ระหว่าง meshes: $\epsilon_1 = |f_{fine} - f_{medium}|$, $\epsilon_2 = |f_{medium} - f_{coarse}|$
> 2. คำนวณ order of convergence: $p = \ln(\epsilon_2/\epsilon_1) / \ln(r)$
> 3. คำนวณ GCI: $GCI = F_s \epsilon / (r^p - 1)$
> 
> **Asymptotic Range Check:**
> - ตรวจสอบว่า meshes อยู่ใน asymptotic range ของ convergence
> - Ratio ควรอยู่ใกล้ 1.0 (ค่าที่ยอมรับ: 0.9 - 1.1)
> - ถ้าไม่อยู่ใน range นี้ อาจต้อง refine เพิ่ม
> 
> **ส่วนที่ 2: calculate_error_norms()**
> 
> **Error Norms:**
> - **L1**: Average absolute error (มีความ sensitive ต่อ outliers น้อยกว่า)
> - **L2**: RMS error (ใช้บ่อยที่สุดในวงการวิทยาศาสตร์)
> - **L∞**: Maximum error (สำคัญสำหรับ local error analysis)
> 
> **การตีความ:**
> - L2 < 1e-6: ยอดเยี่ยมสำหรับ double precision
> - L2 < 1e-4: ดีมากสำหรับ engineering applications
> - L∞: ช่วยระบุ locations ที่มี error สูงสุด
> 
> **Best Practices:**
> - ใช้อย่างน้อย 3 meshes สำหรับ GCI
> - Refinement ratio ควรคงที่ (เช่น 2)
> - ตรวจสอบ asymptotic range เสมอ
> - รายงานทั้ง GCI และ order of convergence

### ตัวอย่าง 6: การเขียน Function Object สำหรับ Error Calculation

```cpp
// NOTE: AI-generated code - Verify parameters
// File: system/fvOptions

// Load required function object libraries
libs
(
    "libutilityFunctionObjects.so"
    "libfieldFunctionObjects.so"
);

// Function object for error calculation
errors
{
    type    fieldMinMax;                 // Calculate field min/max values
    libs    ("libfieldFunctionObjects.so");
    
    fields  (T);                         // Fields to analyze
    
    // Calculate error between T and T_exact
    writeToFile     yes;                 // Write results to file
    log             yes;                 // Output to log
}
```

> **📂 Source:** OpenFOAM Function Objects Framework
> 
> **คำอธิบาย (Thai):**
> OpenFOAM Function Objects ช่วยให้สามารถคำนวณและรายงานผลลัพธ์ได้โดยอัตโนมัติ:
> 
> **Function Objects คืออะไร?**
> - คือ utilities ที่ทำงานระหว่าง simulation โดยไม่ต้องแก้ solver code
> - สามารถ calculate forces, fluxes, statistics, และอื่นๆ
> - ถูกกำหนดใน `system/controlDict` หรือ `system/fvOptions`
> 
> **Library Categories:**
> - **libutilityFunctionObjects.so**: General utilities (time, probes, sets)
> - **libfieldFunctionObjects.so**: Field operations (min/max, averages)
> - **libforces.so**: Force and moment calculations
> - **libsamplingFunctionObjects.so**: Data sampling
> 
> **ตัวอย่าง Function Objects สำหรับ Verification:**
> 
> **1. fieldMinMax:**
> ```cpp
// Track minimum and maximum values
minMaxT
{
    type    fieldMinMax;
    fields  (T U p);
}
```
> 
> **2. fieldAverage:**
> ```cpp
// Calculate time averages
avgT
{
    type            fieldAverage;
    fields
    (
        T
        {
            mean        on;
            prime2Mean  on;     // Variance
        }
    );
}
```
> 
> **3. probes:**
> ```cpp
// Sample at specific points
probeLocations
{
    type            probes;
    fields          (T U p);
    probeLocations
    (
        (0.05 0.05 0)
        (0.10 0.05 0)
    );
}
```
> 
> **สำหรับ MMS Verification:**
> - ใช้ probes หรือ samplePoints เพื่อเก็บค่าจากจุดที่สนใจ
> - ใช้ fieldMinMax เพื่อ track error bounds
> - ใช้ custom function objects สำหรับคำนวณ error norms
> 
> **ข้อดี:**
> - ไม่ต้อง recompile solver
> - ง่ายต่อการ share และ reuse
> - สามารถ enable/disable ได้โดยไม่กระทบ simulation

---

## 📊 การวิเคราะห์ผลลัพธ์ (Result Analysis)

### การตรวจสอบ Order of Accuracy

สำหรับการยืนยันความถูกต้องของ solver ควรตรวจสอบว่า:

**1. Observed Order of Accuracy สอดคล้องกับ Theoretical Order**

ระเบียบวิธีแบบ First-order:
$$ \|\phi_h - \phi_{exact}\| \approx C h^1 $$
- ค่าควรอยู่ใกล้ $p = 1.0 \pm 0.1$

ระเบียบวิธีแบบ Second-order:
$$ \|\phi_h - \phi_{exact}\| \approx C h^2 $$
- ค่าควรอยู่ใกล้ $p = 2.0 \pm 0.2$

**2. Error Norm Behavior:**

$$ \|\phi_{numerical} - \phi_{exact}\| \sim O(h^p) $$

เมื่อ $h$ คือ grid spacing และ $p$ คือ order of accuracy

ใน log-log plot:
$$ \ln(\|e\|) = \ln(C) + p \ln(h) $$

ความชัน (slope) ของกราฟคือ $p$

**3. Convergence Rate:**

สำหรับการ refine เมชด้วย factor $r$:
$$ \frac{\|e\|_{h}}{\|e\|_{h/r}} \approx r^p $$

### การตรวจสอบ Asymptotic Range

เพื่อให้มั่นใจว่าอยู่ใน asymptotic range of convergence:

$$ \frac{GCI_{coarse}}{r^p \times GCI_{fine}} \approx 1 $$

ถ้าค่านี้อยู่ระหว่าง 0.9 ถึง 1.1 แสดงว่า:
- อยู่ใน asymptotic range
- GCI calculation มีความน่าเชื่อถือ
- การ refine เพิ่มจะไม่เปลี่ยน order of convergence อย่างมีนัยสำคัญ

### การตีความ GCI

$$ GCI = \frac{F_s |\varepsilon|}{r^p - 1} $$

ความหมาย:
- GCI คือ estimate ของ error จากการ discretize ที่มีอยู่ใน fine mesh
- GCI 5% หมายถึง ผลลัพธ์อาจต่างจาก grid-independent solution ได้ถึง 5%

**Guidelines:**
- GCI < 1%: ความละเอียดของเมชดีมาก
- GCI 1-5%: ความละเอียดของเมชยอมรับได้สำหรับงานวิจัย
- GCI > 10%: ต้อง refine เมชเพิ่ม

### 💹 ตัวอย่างผลลัพธ์ (Example Results):
> - **Error Evolution**: L2 norm ลดลงแบบ exponential เมื่อรอบการคำนวณเพิ่มขึ้น
> - **Velocity Profile**: กราฟเปรียบเทียบระหว่าง `u` จาก OpenFOAM และ Analytical Solution ที่ลู่เข้าหากันอย่างสมบูรณ์
> - **GCI Table**: แสดงค่าความไม่แน่นอนจากเมช (Mesh Uncertainty) ที่ต่ำกว่า 1% ในระดับ Fine Mesh

---

## 🔍 แนวทางการปฏิบัติ (Best Practices)

### 1. การออกแบบ Test Cases

**หลักการสำคัญ:**

**1.1 เลือกโซลูชันที่มีความซับซ้อนเพียงพอ:**
- หลีกเลี่ยงฟังก์ชันที่ trivial เกินไป (เช่น constant หรือ linear)
- ใช้ฟังก์ชัน trigonometric, exponential, หรือ polynomial
- รวมถึงทุก term ในสมการ (convection, diffusion, source)

**1.2 รวมถึง Boundary Conditions ที่หลากหลาย:**
- **Dirichlet BC**: $\phi = \phi_0$ ที่ boundary
- **Neumann BC**: $\frac{\partial \phi}{\partial n} = q_0$ ที่ boundary
- **Robin BC**: $\alpha \phi + \beta \frac{\partial \phi}{\partial n} = \gamma$ ที่ boundary

**1.3 ตัวอย่าง Test Functions:**

สำหรับ 2D diffusion:
$$ \tilde{\phi}(x,y) = A \sin(k_x x) \sin(k_y y) + B \cos(k_x x) \cos(k_y y) $$

สำหรับ convection-diffusion:
$$ \tilde{\phi}(x,y) = \exp(-a(x^2 + y^2)) \sin(\omega t) $$

### 2. การจัดการ Numerical Tolerances

```cpp
// NOTE: AI-generated code - Verify parameters
// Example: tolerance settings for convergence

// File: system/fvSolution

solvers
{
    p
    {
        solver          GAMG;
        tolerance       1e-12;             // Very tight for verification
        relTol          0.0;               // Use absolute tolerance only
        smoother        GaussSeidel;
    }

    U
    {
        solver          smoothSolver;
        smoother        GaussSeidel;
        tolerance       1e-12;
        relTol          0.0;
        nSweeps         2;
    }

    T
    {
        solver          GAMG;
        tolerance       1e-12;
        relTol          0.0;
        smoother        GaussSeidel;
    }
}

// For transient solvers
PIMPLE
{
    nCorrectors     2;                     // Pressure correctors
    nNonOrthogonalCorrectors 1;            // Non-orthogonal correction loops
    nAlphaCorr      1;                     // Volume fraction correctors
    nAlphaSubCycles 1;                     // Sub-cycles for volume fraction

    // Use strict tolerances
    pRefCell        0;                     // Reference cell for pressure
    pRefValue       0;                     // Reference pressure value
}

// For MMS, use very strict absolute tolerances
// This ensures errors come from discretization, not linear solver
```

**กฎการตั้งค่า Tolerance:**
- สำหรับ verification: ใช้ tolerance 1-2 หลักมากกว่า expected error
- สำหรับ MMS: ใช้ `relTol = 0` เพื่อให้ linear solver ลู่เข้าสู่ tolerance สัมบูรณ์
- สำหรับ production runs: ใช้ `relTol = 0.01` ถึง `0.1`

### 3. การตรวจสอบ Mesh Quality

สำหรับการศึกษาความเข้าใจความละเอียดของเมช ต้องแน่ใจว่า:

**3.1 Mesh Quality คงที่ระหว่างการ Refine:**
- **Non-orthogonality**: คล้ายกันระหว่างเมชทั้งหมด (±5°)
- **Aspect ratio**: อยู่ในช่วงที่ยอมรับได้ (< 1000)
- **Skewness**: ไม่แตกต่างกันมาก (< 0.8)
- **Cell size uniformity**: ลดขนาดด้วย factor คงที่ทั่วทั้ง domain

**3.2 Systematic Refinement:**
- ลด cell size ด้วย factor คงที่ (เช่น 2)
- Refine ทั่วทั้ง domain ไม่ใช่แค่ local refinement
- รักษา topology ของเมชให้คล้ายกัน

**3.3 ตรวจสอดับ Mesh Quality:**

```bash
# NOTE: AI-generated commands - Verify usage
# Check mesh quality metrics
checkMesh -allGeometry -allTopology

# List available time directories
foamListTimes

# Visualize mesh in ParaView
paraFoam -builtin
```

### 4. การบันทึกและรายงานผล

```bash
# NOTE: AI-generated script - Verify usage
# Example: script for logging test results

#!/bin/bash
# File: run_verification.sh

# Create directory for results
RESULTS_DIR="verification_results"
mkdir -p $RESULTS_DIR

# Run on different meshes
for mesh in coarse medium fine; do
    echo "Running simulation on $mesh mesh..."

    # Copy mesh
    cp -r constant/polyMesh/$mesh/* constant/polyMesh/

    # Run solver
    solverName > log.$mesh 2>&1

    # Calculate error norms
    python3 calculate_error.py --mesh $mesh

    # Store results
    mv postProcessing/* $RESULTS_DIR/$mesh/
done

# Generate convergence report
python3 generate_report.py --results $RESULTS_DIR

echo "Verification complete. Results in $RESULTS_DIR"
```

**รายงานควรประกอบด้วย:**
1. ข้อมูลเมช (cell count, quality metrics)
2. การตั้งค่า numerics (schemes, tolerances)
3. Error norms สำหรับแต่ละเมช
4. Order of accuracy
5. GCI values
6. Asymptotic range check

### 5. การจัดการ Test Suites

```bash
# NOTE: AI-generated structure - Verify
# Test suite directory structure

test_suite/
├── test_cases/
│   ├── case1_mms_diffusion/
│   │   ├── coarse/
│   │   ├── medium/
│   │   └── fine/
│   └── case2_grid_convergence/
├── scripts/
│   ├── run_all_tests.sh
│   ├── calculate_gci.py
│   └── generate_report.py
└── results/
    └── timestamp/
```

---

## 🧪 การทดสอบใน OpenFOAM Framework

### โครงสร้างไดเรกทอรี Test

```
$FOAM applications/test/
├── mathematics/              # Test mathematical functions
│   └── graphs/
├── matrices/                 # Test linear algebra operations
│   ├── LU decomposition/
│   └── ICCG solver/
├── meshes/                   # Test mesh generation & manipulation
│   ├── polyMesh/
│   └── primitiveMesh/
├── fields/                   # Test field operations
│   ├── volFields/
│   └── surfaceFields/
└── discretisation/           # Test discretization schemes
    ├── fvm/
    └── fvc/
```

### การเขียน Unit Test ใน OpenFOAM

```cpp
// NOTE: AI-generated code - Verify test framework
// Example: testMatrices.C

#include "testSuite.H"
#include "SquareMatrix.H"
#include "SymmetricSquareMatrix.H"

using namespace Foam;

// Test matrix inversion functionality
void testMatrixInversion()
{
    // Create test matrix
    SquareMatrix<scalar> A(3, Zero);
    A[0][0] = 4; A[0][1] = 2; A[0][2] = 1;
    A[1][0] = 2; A[1][1] = 5; A[1][2] = 3;
    A[2][0] = 1; A[2][1] = 3; A[2][2] = 6;

    // Calculate inverse
    SquareMatrix<scalar> A_inv(A);
    A_inv.inv();

    // Verify that A * A_inv = I (identity matrix)
    SquareMatrix<scalar> I(A * A_inv);

    for (label i = 0; i < 3; ++i)
    {
        for (label j = 0; j < 3; ++j)
        {
            scalar expected = (i == j) ? 1.0 : 0.0;
            testAssert
            (
                mag(I[i][j] - expected) < SMALL,
                "Matrix inversion failed"
            );
        }
    }

    Info << "Matrix inversion test passed" << endl;
}

// Test matrix determinant calculation
void testMatrixDeterminant()
{
    SquareMatrix<scalar> A(3, Zero);
    A[0][0] = 1; A[0][1] = 2; A[0][2] = 3;
    A[1][0] = 4; A[1][1] = 5; A[1][2] = 6;
    A[2][0] = 7; A[2][1] = 8; A[2][2] = 9;

    scalar det = A.det();

    // Determinant of this matrix should be 0 (singular matrix)
    testAssert
    (
        mag(det) < SMALL,
        "Determinant calculation failed"
    );

    Info << "Matrix determinant test passed" << endl;
}

// Main test suite
int main(int argc, char* argv[])
{
    testSuite suite("MatrixTests");

    suite.addTest(testMatrixInversion);
    suite.addTest(testMatrixDeterminant);

    suite.run();

    return 0;
}
```

> **📂 Source:** OpenFOAM Unit Testing Framework
> 
> **คำอธิบาย (Thai):**
> โค้ดนี้แสดงโครงสร้างการเขียน unit tests ใน OpenFOAM:
> 
> **ส่วนประกอบหลัก:**
> 
> **1. testSuite:**
> - Framework สำหรับ organizing และ running tests
> - คล้ายกับ Google Test หรือ Catch2 ใน C++
> - ให้ assertion macros เช่น `testAssert()`
> 
> **2. Test Functions:**
> - แต่ละ function ทดสอบ functionality เฉพาะ
> - ควรมีชื่อที่ชัดเจน (เช่น `testMatrixInversion`)
> - ใช้ `testAssert()` เพื่อตรวจสอบผลลัพธ์
> 
> **3. Matrix Operations:**
> - **SquareMatrix**: Matrix จตุรัสสำหรับ linear systems
> - **inv()**: คำนวณ inverse matrix
> - **det()**: คำนวณ determinant
> 
> **แนวทางการเขียน Tests:**
> 1. **Setup**: สร้าง objects ที่ต้องการทดสอบ
> 2. **Execute**: เรียก methods ที่ต้องการทดสอบ
> 3. **Verify**: ตรวจสอบผลลัพธ์ด้วย assertions
> 4. **Report**: บันทึกผลลัพธ์การทดสอบ
> 
> **ตัวอย่าง Test Cases:**
> - Matrix operations (inversion, determinant, multiplication)
> - Field operations (interpolation, differentiation)
> - Discretization schemes (fvm::div, fvc::grad)
> - Linear solvers (GAMG, PCG)
> 
> **ข้อดีของ Unit Testing:**
> - ตรวจจับ bugs ใน early stage
> - ทำให้มั่นใจว่า code changes ไม่ break functionality ที่มีอยู่
> - Documentation ที่ดีของ code behavior

### การใช้ Test Framework ของ OpenFOAM

OpenFOAM มี test suite ที่สามารถใช้สำหรับ verification:

**การ compile และ run tests:**

```bash
# NOTE: AI-generated commands - Verify
# Compile test
wmake $FOAM applications/test/matrices

# Run test
$FOAM_USER_APPBIN/testMatrices

# Run all tests
$FOAM/applications/test/AllRun
```

---

## 📖 บรรณานุกรม (References)

### หนังสือและบทความหลัก

1. **Roache, P. J.** (1998). *Verification of Codes and Calculations*. AIAA Journal.
   - คลาสสิกของวิชา นิยาม GCI และแนวทางการทำ grid convergence study
   - นิยาม V&V อย่างเป็นทางการ

2. **Oberkampf, W. L., & Trucano, T. G.** (2002). *Verification and Validation in Computational Fluid Dynamics*. Progress in Aerospace Sciences.
   - ภาพรวมของ V&V ใน CFD
   - แนวทางการออกแบบ validation experiments

3. **Salari, K., & Knupp, P.** (2000). *Code Verification by the Method of Manufactured Solutions*. Sandia National Labs.
   - คู่มือการใช้ MMS อย่างละเอียด
   - ตัวอย่าง test cases หลากหลาย

4. **Celik, I. B., et al.** (2008). *Procedure for Estimation and Reporting of Uncertainty Due to Discretization in CFD Applications*. ASME Journal of Fluids Engineering.
   - มาตรฐานการคำนวณ GCI
   - แนวทางการรายงานผล

### ทรัพยากร OpenFOAM

5. **OpenFOAM Programmer's Guide**
   - ส่วนที่เกี่ยวกับ testing และ debugging
   - การใช้ test framework

6. **OpenFOAM Wiki - Validation and Verification**
   - Test cases มาตรฐาน
   - ข้อมูล benchmark

### แหล่งข้อมูลออนไลน์

7. **NASA CFD Verification and Validation Website**
   - แหล่งรวม test cases
   - มาตรฐานการทำ V&V

8. **ERCOFTAC Special Interest Group on Verification and Validation**
   - Best practices และ guidelines
   - Workshop proceedings

---

## 🎓 แบบฝึกหัด (Exercises)

### Exercise 1: MMS สำหรับ 1D Heat Equation

**Mission:** สร้าง test case สำหรับ 1D unsteady heat equation:
$$ \frac{\partial T}{\partial t} = \alpha \frac{\partial^2 T}{\partial x^2} $$

**ขั้นตอนที่ 1: เลือก Manufactured Solution**
$$ \tilde{T}(x,t) = \sin(\pi x) e^{-t} $$

**ขั้นตอนที่ 2: คำนวณ Source Term**

1. First derivative:
   $$ \frac{\partial \tilde{T}}{\partial x} = \pi \cos(\pi x) e^{-t} $$

2. Second derivative:
   $$ \frac{\partial^2 \tilde{T}}{\partial x^2} = -\pi^2 \sin(\pi x) e^{-t} $$

3. Time derivative:
   $$ \frac{\partial \tilde{T}}{\partial t} = -\sin(\pi x) e^{-t} $$

4. Source term:
   $$ S(x,t) = \frac{\partial \tilde{T}}{\partial t} - \alpha \frac{\partial^2 \tilde{T}}{\partial x^2} $$
   $$ S(x,t) = -\sin(\pi x) e^{-t} + \alpha \pi^2 \sin(\pi x) e^{-t} $$
   $$ S(x,t) = \sin(\pi x) e^{-t} (\alpha \pi^2 - 1) $$

**Tasks:**
1. สร้าง OpenFOAM case พร้อม boundary conditions
2. รันบน 3 meshes (10, 20, 40 cells)
3. คำนวณ order of accuracy จาก L2 norm
4. เปรียบเทียบกับ theoretical order

> **[ตัวอย่างโซลูชัน]**:
> - $p = 1.98$ (ใกล้เคียงทฤษฎีคือ $2.0$)
> - Grid Independence บรรลุผลที่เมชระดับ 200,000 เซลล์

### Exercise 2: Grid Convergence สำหรับ Backward Facing Step

**Mission:** ทำ grid convergence study สำหรับ flow ผ่าน backward facing step

**Parameters:**
- Reynolds number: Re = 100 (laminar)
- Expansion ratio: 1:2
- Domain length: 30H

**Tasks:**
1. สร้าง 3 meshes ที่มี refinement factor = 2
2. รัน simulation ด้วย `simpleFoam` (steady-state) หรือ `pisoFoam` (transient)
3. ตรวจสอบ reattachment length ($x_r$)
4. คำนวณ GCI สำหรับ $x_r$
5. เปรียบเทียบกับ experimental data หรือ benchmark

**Reference Data:**
- Armaly et al. (1983): $x_r/H \approx 6.0$ สำหรับ Re = 100

> **[Benchmark Data]**: Re=5100, Step height H, Reattached length $L = 6.1H$ (±0.2)

### Exercise 3: MMS สำหรับ 2D Convection-Diffusion

**Mission:** สร้าง test case สำหรับ steady 2D convection-diffusion:
$$ \mathbf{u} \cdot \nabla \phi = \alpha \nabla^2 \phi + S $$

**Parameters:**
- $\mathbf{u} = (u_0, v_0) = (1.0, 0.5)$
- $\alpha = 0.1$

**Manufactured Solution:**
$$ \tilde{\phi}(x,y) = \sin(\pi x) \sin(\pi y) $$

**Tasks:**
1. คำนวณ source term $S(x,y)$
2. ตั้งค่า OpenFOAM case ด้วย `scalarTransportFoam`
3. ทดสอบทั้ง upwind และ linear schemes
4. เปรียบเทียบ order of accuracy

**คำใบ้:**
$$ S = u_0 \frac{\partial \tilde{\phi}}{\partial x} + v_0 \frac{\partial \tilde{\phi}}{\partial y} - \alpha \nabla^2 \tilde{\phi} $$

> **[สรุปผล]**: Solver ผ่านการทดสอบ Verification ด้วย Order of Accuracy 2.0 บนเมชทุกระดับ

### Exercise 4: Verification ของ Navier-Stokes Solver

**Mission:** ยืนยันความถูกต้องของ 2D incompressible Navier-Stokes solver ด้วย MMS

**สมการ:**
$$ \nabla \cdot \mathbf{u} = 0 $$
$$ \frac{\partial \mathbf{u}}{\partial t} + \mathbf{u} \cdot \nabla \mathbf{u} = -\nabla p + \nu \nabla^2 \mathbf{u} + \mathbf{S}_u $$

**Manufactured Solutions:**
$$ \tilde{u}(x,y,t) = \sin(\pi x) \cos(\pi y) e^{-t} $$
$$ \tilde{v}(x,y,t) = -\cos(\pi x) \sin(\pi y) e^{-t} $$
$$ \tilde{p}(x,y) = \sin(\pi x) \sin(\pi y) e^{-t} $$

**Tasks:**
1. ตรวจสอบว่า $\nabla \cdot \tilde{\mathbf{u}} = 0$ (continuity)
2. คำนวณ source terms $\mathbf{S}_u$
3. ตั้งค่า test case ด้วย `icoFoam`
4. ทดสอบทั้ง velocity และ pressure fields

> **[ผลลัพธ์]**: Source terms ที่คำนวณได้ทำให้ Scalar field ลู่เข้าหา Manufactured Solution โดยมี Max Error $1.2 \times 10^{-7}$

---

## 🚀 เส้นทางการเรียนรู้ต่อ (Next Steps)

หลังจากเข้าใจหลักการการทดสอบ ควรศึกษาต่อไปยัง:

### 1. [[02_TECHNICAL_IMPLEMENTATION/00_Overview|Test Framework Development]]
- การเขียน automated test suites
- การใช้ C++ test frameworks ใน OpenFOAM
- การ implement MMS อัตโนมัติ

### 2. [[03_PRACTICAL_VALIDATION/00_Overview|Validation Benchmarks]]
- การเปรียบเทียบกับ experimental data
- มาตรฐานที่ยอมรับในวงการ CFD
- ERCOFTAC classic test cases
- NASA turbulence modeling resources

### 3. [[04_ADVANCED_TOPICS/00_Overview|QA, Automation & Profiling]]
- Regression testing
- Performance optimization
- Continuous integration สำหรับ CFD
- Automated reporting

### 4. ทรัพยากรเพิ่มเติม

**Online Courses:**
- NASA V&V Course
- Stanford CFD Verification

**Software:**
- EFD (Verification Database)
- OpenFOAM validation cases

**Communities:**
- OpenFOAM Verification & Validation Working Group
- AIAA V&V Committee

---

## 📝 สรุป (Summary)

### จุดสำคัญที่ต้องจำ

1. **Verification ≠ Validation**
   - Verification: ถูกต้องหรือไม่? (คณิตศาสตร์)
   - Validation: เหมาะสมหรือไม่? (ฟิสิกส์)

2. **MMS เป็นเครื่องมือทรงพลัง**
   - ใช้ได้กับ PDE ที่ซับซ้อน
   - ทดสอบทุกส่วนของ solver
   - ต้องคำนวณ source terms อย่างระมัดระวัง

3. **Grid Convergence จำเป็น**
   - ใช้อย่างน้อย 3 เมช
   - ตรวจสอบ asymptotic range
   - รายงาน GCI values

4. **Tolerance สำคัญมาก**
   - Verification: ใช้ strict tolerances
   - Validation: ใช้ tolerances ตามปกติ

5. **บันทึกทุกอย่าง**
   - การตั้งค่าทั้งหมด
   - Mesh quality metrics
   - Error norms และ convergence rates

### Checklists สำหรับ Verification

**Pre-Test:**
- [ ] เลือก manufactured solution ที่เหมาะสม
- [ ] คำนวณ source terms ถูกต้อง
- [ ] ตั้งค่า boundary conditions
- [ ] ตรวจสอบ mesh quality

**During Test:**
- [ ] ใช้ strict solver tolerances
- [ ] รันบนหลายเมช
- [ ] บันทึกทุก settings
- [ ] เก็บข้อมูล error norms

**Post-Test:**
- [ ] คำนวณ order of accuracy
- [ ] ตรวจสอบ asymptotic range
- [ ] คำนวณ GCI
- [ ] เปรียบเทียบกับ theoretical order
- [ ] เขียนรายงานอย่างสมบูรณ์

---

> **[!TIP] เครื่องมือช่วย**
> - `checkMesh`: ตรวจสอบคุณภาพเมช
> - `foamListTimes`: ดู time directories
> - `sample`: สกัดข้อมูลตามจุดที่ต้องการ
> - `paraFoam`: visualize ผลลัพธ์

---

**Document Version:** 1.0
**Last Updated:** 2025
**Maintained by:** OpenFOAM Thai Documentation Project

---

## 🧠 ตรวจสอบความเข้าใจ (Concept Check)

1. **ถาม:** ถ้าเราทำ MMS (Method of Manufactured Solutions) แล้วพบว่า Order of Accuracy ได้ค่า $p=1.0$ ทั้งที่ใช้ Discretization Schemes แบบ Second-order ปัญหาน่าจะเกิดจากอะไร?
   <details>
   <summary>เฉลย</summary>
   <b>ตอบ:</b> เป็นไปได้หลายสาเหตุ เช่น (1) โค้ดมี Bug ในส่วน implementation ของ scheme, (2) Boundary condition เป็น First-order และส่งผลกระทบเข้ามาข้างใน (Boundary pollution), หรือ (3) Mesh ที่ใช้ยังไม่ละเอียดพอที่จะเข้าไปอยู่ใน Asymptotic Range หรือ Discontinuity ใน Solution ที่เลือก
   </details>

2. **ถาม:** ทำไม Richardson Extrapolation ถึงใช้ไม่ได้ถ้าเราไม่ได้อยู่ใน Asymptotic Range?
   <details>
   <summary>เฉลย</summary>
   <b>ตอบ:</b> เพราะสมการของ Richardson Extrapolation สมมติว่าเทอม Error หลักมาจากเทอมแรกของ Taylor Series expansion ($Ch^p$) เท่านั้น หากไม่อยู่ใน Asymptotic Range เทอม Higher-order ($h^{p+1}, ...$) ยังมีผลกระทบสูงมาก ทำให้การประมาณค่าผิดพลาด
   </details>

3. **ถาม:** ในการทำ Grid Convergence Study ทำไมเราควรใช้ Refinement Ratio ที่เป็นเลขจำนวนเต็ม (เช่น 2) มากกว่าเลขทศนิยม (เช่น 1.5)?
   <details>
   <summary>เฉลย</summary>
   <b>ตอบ:</b> การใช้ Ratio 2 ทำให้ Cell Center ของ Grid หยาบ มักจะทับกับ Grid ละเอียดพอดี (ถ้าเป็น Structured Grid) ทำให้การเปรียบเทียบค่า (Sampling) แม่นยำที่สุดโดยไม่ต้องมีการ Interpolation ซึ่งอาจเพิ่ม Error โดยไม่จำเป็น แต่ถ้าเป็น Unstructured Grid ข้อนี้อาจไม่สำคัญเท่า
   </details>