# ข้อควรระวังและการดีบัก (Common Pitfalls & Debugging)

![[unstable_equation_pitfall.png]]
`A tightrope walker representing the solver trying to balance on a thin wire labeled "fvc::laplacian" while being buffeted by wind (numerical instability). A sturdy bridge labeled "fvm::laplacian" is visible right next to them, representing stability, scientific textbook diagram, clean vector line art, white background, high definition, flat design, educational infographic --ar 16:9`

> [!TIP] 🎯 ความสำคัญของการเข้าใจ Pitfalls เหล่านี้
> การเข้าใจข้อผิดพลาดทั่วไปเหล่านี้จะ **ช่วยให้คุณประหยัดเวลาในการดีบัก** และ **พัฒนาโซลเวอร์ที่เสถียร** ข้อผิดพลาดเหล่านี้มักเกิดจากการเข้าใจผิดเกี่ยวกับ:
> - **Explicit (fvc) vs Implicit (fvm)**: ส่งผลต่อความเสถียรและขนาด Time step
> - **Dimensional Consistency**: OpenFOAM มีระบบตรวจสอบหน่วยอัตโนมัติ
> - **Mesh Quality**: คุณภาพเมชส่งผลต่อความแม่นยำของการคำนวณ Gradient/Div/Curl
> - **Type System**: การเลือกใช้ Scalar/Vector/Tensor ที่ถูกต้อง
>
> เครื่องมือเหล่านี้อยู่ใน **src/finiteVolume/** และถูกใช้ใน **ไฟล์โซลเวอร์ (.C files)** ซึ่งเป็นส่วนสำคัญของการพัฒนาโซลเวอร์และ boundary conditions

การใช้แคลคูลัสเวกเตอร์บนเมชมีรายละเอียดทางเทคนิคที่มักสร้างปัญหาให้กับนักพัฒนาโซลเวอร์ ส่วนนี้รวบรวมปัญหาที่พบบ่อย วิธีการแก้ไข และแนวทางปฏิบัติที่ดี

---

## 🔥 1. การสับสนระหว่าง `fvc` และ `fvm`

> [!NOTE] **📂 OpenFOAM Context**
> หัวข้อนี้เกี่ยวข้องกับ **Domain B: Numerics & Linear Algebra** และ **Domain E: Coding/Customization**
> - **ไฟล์โซลเวอร์**: `applications/solvers/` (เช่น `simpleFoam.C`, `myCustomSolver.C`)
> - **Keywords**: `fvc::` (Explicit), `fvm::` (Implicit), `fvScalarMatrix`, `solve()`
> - **ผลกระทบ**: การเลือกใช้ `fvc` แทน `fvm` จะทำให้โซลเวอร์ **ไม่เสถียร** และต้องใช้ time step ที่เล็กมาก
> - **ตำแหน่ง**: อยู่ในสมการหลักของโซลเวอร์ (main equation loop)
>
> ใน OpenFOAM คุณจะเห็นการใช้งานใน:
> - `src/finiteVolume/fvMesh/fvMesh.H` - Mesh ที่ใช้สำหรับการคำนวณ
> - `src/finiteVolume/fvm/fvm.H` - Implicit operators
> - `src/finiteVolume/fvc/fvc.H` - Explicit operators

### ปัญหาหลัก

> [!WARNING] ⚠️ ข้อผิดพลาดที่พบบ่อยที่สุด
> ใช้ `fvc::laplacian` ในสมการที่ควรเป็น `fvm::laplacian` สำหรับเทอมที่เป็นคำตอบที่ต้องการหา

### ผลกระทบ

**เมื่อใช้ `fvc::laplacian` ผิดที่:**
- โปรแกรมจะรันได้ แต่จะ **ไม่เสถียรอย่างยิ่ง**
- ต้องการก้าวเวลาที่เล็กมาก (CFL condition)
- เทอมการแพร่ถูกคำนวณแบบ Explicit
- อาจเกิดการระเบิดของโซลเวอร์ (Solver explosion)

### เงื่อนไขขอบเขตความเสถียร

สำหรับ Explicit Laplacian:
$$\Delta t \leq \frac{\Delta x^2}{2\Gamma}$$

โดยที่:
- $\Delta t$ = ขนาดขั้นเวลา
- $\Delta x$ = ขนาดเซลล์เม็ช
- $\Gamma$ = สัมประสิทธิ์การแพร่

### แนวทางปฏิบัติที่ถูกต้อง

```cpp
// ❌ ผิด: ใช้ fvc สำหรับสมการที่ต้องการแก้
// Using fvc for diffusion term creates explicit scheme - very unstable!
fvScalarMatrix TEqn
(
    fvm::ddt(T) + fvc::laplacian(DT, T) == source  // เสถียรมาก!
);

// ✅ ถูก: ใช้ fvm สำหรับ diffusion terms
// Implicit treatment of diffusion for unconditional stability
fvScalarMatrix TEqn
(
    fvm::ddt(T) + fvm::laplacian(DT, T) == source  // เสถียร
);

// ✅ ถูก: ใช้ fvc สำหรับ source terms หรือ post-processing
// Explicit evaluation is acceptable for known fields
volScalarField diffusionSource = fvc::laplacian(DT, T);  // ถูกต้อง
```

**Source:** 📂 `.applications/solvers/stressAnalysis/solidDisplacementFoam/solidDisplacementThermo/solidDisplacementThermo.C`

**คำอธิบาย (Thai):**
- **Source**: โค้ดตัวอย่างแสดงการใช้งาน `fvm::laplacian` ในไฟล์ `solidDisplacementThermo.C` ซึ่งเป็นส่วนประกอบของโซลเวอร์การวิเคราะห์ความเค้น (stress analysis solver)
- **Explanation**: การเลือกระหว่าง `fvc` (explicit) และ `fvm` (implicit) มีผลกระทบอย่างมากต่อความเสถียรของโซลเวอร์ เทอมการแพร่ (diffusion) ที่เป็นส่วนของ unknown variable ควรใช้ `fvm` เพื่อให้ได้ scheme แบบ implicit ซึ่งไม่มีข้อจำกัดด้านเวลา
- **Key Concepts**: 
  - **Explicit (fvc)**: คำนวณค่าจาก time step ก่อนหน้า มีเงื่อนไขความเสถียรที่เข้มงวด
  - **Implicit (fvm)**: คำนวณค่าจาก time step ปัจจุบัน ไร้ขีดจำกัดเวลาแต่ต้องแก้ระบบสมการ
  - **CFL Condition**: เงื่อนไขความเสถียรสำหรับ explicit schemes

### กฎพื้นฐาน

> [!TIP] 💡 กฎง่ายๆ
> - หากเทอมนั้นคือ **คำตอบที่คุณต้องการหา** (เช่น $T$, $p$, $U$) ให้ใช้ `fvm` เสมอ
> - หากเทอมนั้นคือ **ค่าที่ทราบแล้ว** หรือใช้เป็น source term ให้ใช้ `fvc`

---

## 📏 2. ความไม่สอดคล้องของมิติ (Dimension Mismatch)

> [!NOTE] **📂 OpenFOAM Context**
> หัวข้อนี้เกี่ยวข้องกับ **Domain A: Physics & Fields** และ **Domain E: Coding/Customization**
> - **ไฟล์**: `applications/solvers/` และ `src/finiteVolume/`
> - **Keywords**: `dimensionSet`, `dimensions()`, `dimPressure`, `dimDensity`, `dimAcceleration`
> - **Classes**: `dimensionedScalar`, `dimensionedVector`, `GeometricField`
> - **ตำแหน่ง**: ในฟังก์ชันการคำนวณ physics (เช่น คำนวณแรง ความเร่ง)
> - **Debugging**: ใช้ `Info << field.dimensions() << endl;` เพื่อตรวจสอบหน่วย
>
> ใน OpenFOAM คุณจะเห็นการใช้งานใน:
> - `src/OpenFOAM/dimensionSet/dimensionSet.H` - ระบบตรวจสอบหน่วย
> - `src/OpenFOAM/dimensionedTypes/` - ประเภทข้อมูลที่มีหน่วย
> - `src/finiteVolume/fields/GeometricFields/` - ฟิลด์ที่มีระบบตรวจสอบหน่ว

### ปัญหา

ลืมหารด้วยความหนาแน่น ($\rho$) เมื่อคำนวณความเร่งจากเกรเดียนต์ความดัน

### ตัวอย่างการแก้ไข

```cpp
// ❌ ผิด: ผลลัพธ์คือ [Force/Volume] ไม่ใช่ [Acceleration]
// fvc::grad(p) มีหน่วย [Pa/m] = [kg/(m²·s²)]
volVectorField acc = -fvc::grad(p);

// ✅ ถูก: ผลลัพธ์คือ [Acceleration] = [m/s²]
// p/rho มีหน่วย [m²/s²], gradient มีหน่วย [m/s²]
volVectorField acc = -fvc::grad(p/rho);

// ✅ ถูก: หรือใช้รูปแบบอื่นที่เทียบเท่า
// Alternative form with same dimensional correctness
volVectorField acc = -fvc::grad(p) / rho;
```

**Source:** 📂 `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystem.C`

**คำอธิบาย (Thai):**
- **Source**: ไฟล์ `phaseSystem.C` จากโซลเวอร์ multiphaseEulerFoam แสดงการจัดการ dimensional consistency ในระบบ multiphase
- **Explanation**: OpenFOAM มีระบบตรวจสอบหน่วย (dimension checking) ที่เข้มงวด การคำนวณความเร่งจาก gradient ของความดันต้องมีการหารด้วยความหนาแน่นเพื่อให้ได้หน่วยที่ถูกต้อง
- **Key Concepts**:
  - **Dimensioned Types**: OpenFOAM tracks dimensions through set {mass, length, time, temperature, ...}
  - **Pressure Gradient**: $\nabla p$ มีหน่วย $[M L^{-2} T^{-2}]$ (Force per volume)
  - **Acceleration**: มีหน่วย $[L T^{-2}]$ ต้อง divide pressure ด้วย density

### การตรวจสอบหน่วย

```cpp
// ตรวจสอบหน่วยของฟิลด์
// Debugging dimensions by printing to console
Info << "Gradient dimensions: " << fvc::grad(p).dimensions() << endl;
Info << "Acceleration dimensions: " << acc.dimensions() << endl;
```

### ตารางหน่วยที่ถูกต้อง

| การดำเนินการ | หน่วยของ input | หน่วยของ output | การใช้งาน |
|:---|:---|:---|:---|
| `fvc::grad(p)` | `[kPa/m]` | `[kPa/m]` | แรงต่อปริมาตร |
| `fvc::grad(p/rho)` | `[m²/s²]/m` | `[m/s²]` | ความเร่ง |
| `fvc::grad(T)` | `[K/m]` | `[K/m]` | Gradient อุณหภูมิ |
| `fvc::laplacian(DT, T)` | `[m²/s]·[K/m²]` | `[K/s]` | อัตราการเปลี่ยนแปลง |

---

## 🕸️ 3. ปัญหาคุณภาพเมช (Mesh Quality Issues)

> [!NOTE] **📂 OpenFOAM Context**
> หัวข้อนี้เกี่ยวข้องกับ **Domain D: Meshing** และ **Domain B: Numerics**
> - **ไฟล์ตรวจสอบ**: ใช้คำสั่ง `checkMesh` ใน terminal
> - **ไฟล์เมช**: `constant/polyMesh/points`, `constant/polyMesh/faces`
> - **ไฟล์ Scheme**: `system/fvSchemes` → `laplacianSchemes`, `gradSchemes`
> - **Keywords**: `non-orthogonality`, `skewness`, `aspectRatio`, `corrected`, `limited`
> - **การตรวจสอบ**: `checkMesh -allGeometry -allTopology`
> - **ผลกระทบ**: เมชที่ไม่ดีทำให้การคำนวณ gradient/laplacian มีค่า error สูง
>
> ใน OpenFOAM คุณจะเห็นการใช้งานใน:
> - `src/meshes/` - โครงสร้างข้อมูลเมช
> - `src/finiteVolume/fvMesh/fvMesh.H` - การเข้าถึงข้อมูลเมช
> - `src/finiteVolume/interpolation/` - การ interpolation บนเมช

### Non-orthogonality

**ปัญหา**: การคำนวณ Laplacian บนเมชที่มีความเบี้ยว (Skewness) สูง

**ผลลัพธ์**: ค่าที่หน้าเซลล์อาจผิดเพี้ยน ทำให้โซลเวอร์ Diverge

### การวินิจฉัยปัญหา

```cpp
// ตรวจสอบคุณภาพเมช
// Check mesh quality metrics
const polyMesh& mesh = ...;

scalar maxNonOrtho = 0.0;
scalar maxSkewness = 0.0;

forAll(mesh.faceAreas(), faceI)
{
    // ตรวจสอบ non-orthogonality
    // Calculate angle between face normal and cell-center vector
    scalar nonOrtho = ...;
    maxNonOrtho = max(maxNonOrtho, nonOrtho);

    // ตรวจสอบ skewness
    // Measure how skewed the face is relative to cell centers
    scalar skew = ...;
    maxSkewness = max(maxSkewness, skew);
}

Info << "Max non-orthogonality: " << maxNonOrtho << endl;
Info << "Max skewness: " << maxSkewness << endl;
```

**Source:** 📂 `.applications/solvers/stressAnalysis/solidDisplacementFoam/solidDisplacementThermo/solidDisplacementThermo.C`

**คำอธิบาย (Thai):**
- **Source**: ไฟล์ `solidDisplacementThermo.C` ใช้งานกับ mesh ผ่าน `fvMesh` class และตรวจสอบ mesh quality เพื่อความเสถียรของการคำนวณ
- **Explanation**: Mesh quality มีผลต่อความแม่นยำของการคำนวณ discretized operators Non-orthogonality สูงหมายถึง face ไม่ตั้งฉากกับเส้นเชื่อมระหว่าง cell centers ซึ่งทำให้เกิด error ในการคำนวณ gradient
- **Key Concepts**:
  - **Non-orthogonality**: มุมระหว่าง face normal และ cell-center vector
  - **Skewness**: ความไม่สมมาตรของ face position ที่ส่งผลต่อ interpolation accuracy
  - **Mesh quality limits**: Non-ortho < 70°, Skewness < 0.8 สำหรับความเสถียร

### วิธีแก้ไข: เลือก Scheme ที่เหมาะสม

เลือกใช้ Scheme ที่มีการแก้ค่าความไม่ตั้งฉากใน `system/fvSchemes`:

```cpp
// การเลือก Laplacian Scheme ที่เหมาะสมกับคุณภาพเมช
laplacianSchemes
{
    // แบบพื้นฐาน (เหมาะกับเมชคุณภามสูง)
    // Basic scheme - only for orthogonal meshes
    default         Gauss linear;

    // แก้ไข non-orthogonality (แนะนำ)
    // Adds correction term for non-orthogonal faces
    default         Gauss linear corrected;

    // แก้ไข non-orthogonality ที่รุนแรง
    // Limited correction for highly non-orthogonal meshes
    default         Gauss linear limited 0.5;

    // สำหรับ skewness สูง
    // Special handling for skewed faces
    default         Gauss linear skewCorrected;
}
```

### การเปรียบเทียบ Schemes

| Scheme | ความเสถียร | ความแม่นยำ | การใช้งาน |
|:---|:---|:---|:---|
| `Gauss linear` | ปานกลาง | ดี | เมชตั้งฉากดี |
| `Gauss linear corrected` | สูง | ดีมาก | เมสเบี้ยวเล็กน้อย |
| `Gauss linear limited` | สูงมาก | ปานกลาง | เมชเบี้ยวมาก |
| `Gauss leastSquares` | สูง | สูง | เมชไม่มีโครงสร้าง |

### การตรวจสอบ Mesh Quality

```bash
# ใช้ checkMesh เพื่อตรวจสอบคุณภาพเมช
checkMesh -allGeometry -allTopology

# ผลลัพธ์ที่ควรได้:
# - Max non-orthogonality < 70°
# - Max skewness < 0.8
# - Max aspect ratio < 1000
```

---

## 🔢 4. ข้อผิดพลาดเกี่ยวกับประเภทข้อมูล (Type Mismatches)

> [!NOTE] **📂 OpenFOAM Context**
> หัวข้อนี้เกี่ยวข้องกับ **Domain E: Coding/Customization**
> - **ไฟล์**: ซอร์สโค้ด C++ ของโซลเวอร์ (`applications/solvers/*.C`)
> - **Keywords**: `volScalarField`, `volVectorField`, `volTensorField`, `surfaceScalarField`
> - **Operators**: `fvc::div()`, `fvc::curl()`, `fvc::grad()`, `fvc::laplacian()`
> - **Compile Error**: ข้อผิดพลาดประเภทข้อมูลจะถูกจับตั้งแต่ compile-time
> - **Debugging**: อ่าน compiler error messages อย่างละเอียด
>
> ใน OpenFOAM คุณจะเห็นการใช้งานใน:
> - `src/finiteVolume/fields/volFields/` - Volume field types
> - `src/finiteVolume/fields/surfaceFields/` - Surface field types
> - `src/finiteVolume/fvc/fvcDtdt.C` - Divergence operators
> - `src/finiteVolume/fvc/fvcCurl.C` - Curl operators

### ข้อผิดพลาดที่พบบ่อย

| อาการ | สาเหตุ | วิธีแก้ |
|:---|:---|:---|
| `no match for fvc::div(volScalarField)` | Divergence ต้องใช้กับ Vector เท่านั้น | ตรวจสอบว่าพารามิเตอร์เป็น Vector หรือไม่ |
| `cannot convert fvMatrix to GeometricField` | พยายามเอาผลลัพธ์จาก `fvm` ไปเก็บในตัวแปรฟิลด์ | ใช้ `fvc` หากต้องการค่าตัวเลขทันที |
| `no match for fvc::curl(scalarField)` | Curl ทำงานได้เฉพาะกับฟิลด์เวกเตอร์ | ตรวจสอบประเภทฟิลด์ |

### การแก้ไขและตัวอย่างที่ถูกต้อง

```cpp
// ❌ ERROR: Divergence ของสเกลาร์ไม่ถูกต้อง
// Divergence requires vector/tensor field input
// volScalarField wrong = fvc::div(T);

// ✅ CORRECT: Divergence ของเวกเตอร์
// Correct: divergence of velocity vector field
volVectorField U(mesh);
volScalarField divU = fvc::div(U);

// ❌ ERROR: พยายามแปลง fvMatrix เป็น Field
// fvm returns matrix, not field - cannot directly assign
// volScalarField wrong = fvm::laplacian(DT, T);

// ✅ CORRECT: ใช้ fvc หากต้องการค่าทันที
// For immediate evaluation, use fvc (explicit)
volScalarField laplacianT = fvc::laplacian(DT, T);

// ✅ CORRECT: ใช้ fvm สำหรับการแก้สมการ
// fvm creates matrix for solving - must call solve()
fvScalarMatrix TEqn(fvm::laplacian(DT, T));
TEqn.solve();

// ❌ ERROR: Curl ของสเกลาร์
// Curl operator only defined for vector fields
// volVectorField wrong = fvc::curl(p);

// ✅ CORRECT: Curl ของเวกเตอร์
// Correct: curl of velocity gives vorticity
volVectorField vorticity = fvc::curl(U);
```

**Source:** 📂 `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/ThermalPhaseChangePhaseSystem/ThermalPhaseChangePhaseSystem.C`

**คำอธิบาย (Thai):**
- **Source**: ไฟล์ `ThermalPhaseChangePhaseSystem.C` แสดงการใช้งาน field operations ที่หลากหลายในระบบ multiphase ที่ซับซ้อน
- **Explanation**: OpenFOAM มี type system ที่เข้มงวด ตัวดำเนินการแต่ละตัวมีความต้องการเฉพาะเกี่ยวกับประเภทฟิลด์ (Scalar, Vector, Tensor) การผิดพลาดจะถูกจับได้ตั้งแต่ compile-time
- **Key Concepts**:
  - **Type Safety**: Compile-time checking prevents invalid operations
  - **Field Types**: `volScalarField`, `volVectorField`, `volTensorField`
  - **Operators**: Divergence reduces tensor rank by 1 (vector→scalar)
  - **fvm vs fvc Return Types**: `fvm` returns `fvMatrix`, `fvc` returns `GeometricField`

### การตรวจสอบประเภทขณะ compile-time

```cpp
// ตรวจสอบประเภทด้วย static_assert (C++11)
// Compile-time type checking for safety
static_assert(
    std::is_same<decltype(fvc::grad(p)), volVectorField>::value,
    "Gradient of scalar must be vector field"
);

// ใช้ decltype สำหรับการอนุมานประเภทอัตโนมัติ
// Type deduction for automatic variable typing
auto gradP = fvc::grad(p);  // gradP มีประเภท volVectorField
```

---

## 📊 5. สรุปตารางการวินิจฉัยปัญหา

> [!NOTE] **📂 OpenFOAM Context**
> หัวข้อนี้เกี่ยวข้องกับ **Domain B: Numerics & Linear Algebra** และ **Domain C: Simulation Control**
> - **ไฟล์**: `system/fvSchemes`, `system/fvSolution`, `system/controlDict`
> - **Keywords**: `residuals`, `tolerances`, `solvers`, `schemes`, `deltaT`, `maxCo`
> - **Log Files**: `log.simpleFoam`, `log.mySolver` - ตรวจสอบผลลัพธ์
> - **Debugging**: เพิ่ม `Info <<` statements ในโค้ดโซลเวอร์
> - **การตรวจสอบ**: ดู residual ใน log file ว่าลดลงหรือไม่
>
> ใน OpenFOAM คุณจะเห็นการใช้งานใน:
> - `src/ODE/ODESolvers/` - Solvers สำหรับ temporal discretization
> - `src/matrices/` - Linear solvers และ preconditioners
> - `src/OpenFOAM/db/IOobject/IOobject.C` - Logging output

### ตารางอาการและวิธีแก้

| 🚩 อาการ (Symptom) | 🔧 สาเหตุที่เป็นไปได้ | 💡 วิธีแก้ (Solution) |
|:---|:---|:---|
| **โซลเวอร์ระเบิด (Diverge) ทันที** | ใช้ `fvc` แทน `fvm` สำหรับเทอมหลัก | เปลี่ยนเทอมหลักจาก `fvc` เป็น `fvm` |
| **`Dimension mismatch`** | หน่วยของฟิลด์ไม่สอดคล้อง | หารด้วยตัวแปรที่เหมาะสม (เช่น $\rho$) |
| **Residual ไม่ลดลน** | เช็ค non-orthogonal correction ใน `fvSchemes` | เพิ่ม `corrected` หรือ `limited` ใน laplacianSchemes |
| **Compile Error: `no match`** | เช็คประเภทข้อมูล (Scalar/Vector/Tensor) | ตรวจสอบว่าใช้ operator ที่ถูกต้องกับประเภทฟิลด์ |
| **ผลลัพธ์ผิดปกติที่ขอบเขต** | เงื่อนไขขอบเขตไม่ถูกต้อง | ตรวจสอบ boundary conditions ใน `0/` directory |
| **CFL > 1 แต่โซลเวอร์เสถียร** | ใช้ explicit scheme ผิดที่ | เปลี่ยนเป็น implicit scheme สำหรับ convection/diffusion |
| **Time step ต้องเล็กมากๆ** | ใช้ explicit diffusion | เปลี่ยนจาก `fvc::laplacian` เป็น `fvm::laplacian` |
| **Mesh quality warning** | เมชมี skewness หรือ non-orthogonality สูง | ปรับปรุงเมชหรือเปลี่ยน scheme |

---

## 🧪 6. เครื่องมือการดีบัก

> [!NOTE] **📂 OpenFOAM Context**
> หัวข้อนี้เกี่ยวข้องกับ **Domain B: Numerics & Linear Algebra** และ **Domain E: Coding/Customization**
> - **ไฟล์**: ซอร์สโค้ดโซลเวอร์ (`applications/solvers/*.C`)
> - **Keywords**: `fvc::div()`, `fvc::grad()`, `Info`, `mesh.V()`, `sum()`, `max()`, `mag()`
> - **Classes**: `fvMesh`, `GeometricField`, `dimensionSet`
> - **Debugging Tools**: `Info <<`, `WarningIn`, `FatalErrorIn`
> - **Function Objects**: สามารถใช้ `system/controlDict` เพื่อเพิ่มการตรวจสอบ
>
> ใน OpenFOAM คุณจะเห็นการใช้งานใน:
> - `src/finiteVolume/fvMesh/fvMesh.H` - Mesh volume และ geometry
> - `src/OpenFOAM/global/constants/mathematical/mathematicalConstants.H` - ค่าคงที่ทางคณิตศาสตร์
> - `src/OpenFOAM/db/IOstreams/` - Input/output streams

### การตรวจสอบการอนุรักษ์ (Conservation Check)

```cpp
// ตรวจสอบสมดุลมวลสำหรับการไหลแบบอินคอมเพรสซิเบิล
// Continuity error check for incompressible flow
volScalarField continuityError = fvc::div(U);

scalar maxContinuityError = max(mag(continuityError));
scalar sumContinuityError = sum(continuityError * mesh.V());

Info << "Max continuity error: " << maxContinuityError << endl;
Info << "Sum continuity error: " << sumContinuityError << endl;

// ค่าควรอยู่ในช่วงความแม่นยำของเครื่อง (~1e-10)
// Should be near machine precision for incompressible flow
```

**Source:** 📂 `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystem.C`

**คำอธิบาย (Thai):**
- **Source**: ไฟล์ `phaseSystem.C` จาก multiphaseEulerFoam มีการตรวจสอบ mass conservation สำหรับ multiphase flows
- **Explanation**: การตรวจสอบ conservation laws เป็นเครื่องมือสำคัญในการ valid ผลลัพธ์ CFD สำหรับ incompressible flow divergence ของ velocity ควรเป็นศูนย์ (continuity equation)
- **Key Concepts**:
  - **Continuity Equation**: $\nabla \cdot \mathbf{U} = 0$ สำหรับ incompressible flow
  - **Conservation Check**: ตรวจสอบว่า solver คงรักษา conservation laws หรือไม่
  - **Machine Precision**: ค่า error ควรอยู่ในช่วง $10^{-10}$ ถึง $10^{-15}$

### การตรวจสอบ Boundaries

```cpp
// ตรวจสอบค่าขอบเขตหลังจากการคำนวณ gradient
// Debug boundary field values after gradient calculation
volVectorField gradP = fvc::grad(p);

forAll(gradP.boundaryField(), patchi)
{
    Info << "Patch " << mesh.boundaryMesh()[patchi].name() << ":" << endl;
    Info << "  Gradient: " << gradP.boundaryField()[patchi] << endl;
}
```

### การตรวจสอบสมดุลพลังงาน

```cpp
// สำหรับปัญหาการนำความร้อน
// Energy balance check for heat conduction
volScalarField heatGen = fvc::laplacian(kappa, T);  // [W/m³]
scalar totalHeatGen = sum(heatGen * mesh.V());

Info << "Total heat generation: " << totalHeatGen << " W" << endl;
```

---

## ✅ 7. แนวทางปฏิบัติที่ดี (Best Practices)

> [!NOTE] **📂 OpenFOAM Context**
> หัวข้อนี้เกี่ยวข้องกับ **Domain B: Numerics & Linear Algebra** และ **Domain C: Simulation Control**
> - **ไฟล์**: `system/fvSchemes`, `system/fvSolution`, `system/controlDict`
> - **Keywords**: `gradSchemes`, `divSchemes`, `laplacianSchemes`, `interpolationSchemes`, `snGradSchemes`
> - **Solver Settings**: `solvers` dictionary ใน `fvSolution`
> - **Time Control**: `deltaT`, `maxCo` ใน `controlDict`
> - **Best Practice**: เริ่มต้นด้วย scheme ที่เสถียรที่สุด แล้วค่อยปรับเพิ่มความแม่นยำ
>
> ใน OpenFOAM คุณจะเห็นการใช้งานใน:
> - `src/finiteVolume/fvSchemes/` - Implementation ของ numerical schemes
> - `src/finiteVolume/fvSolution/` - Solver parameters และ algorithms
> - `src/ODE/` - Temporal discretization schemes

### การเขียนสมการใหม่

> [!INFO] 📋 Checklist สำหรับการเขียนสมการ
> 1. ไล่ตรวจสอบทีละเทอมว่า:
>    - "ต้องการความเสถียร (Implicit)" หรือ "ต้องการค่าตัวเลข (Explicit)"
> 2. เลือก Namespace ให้ถูกตั้งแต่แรก (`fvm` vs `fvc`)
> 3. ตรวจสอบหน่วยของแต่ละเทอม
> 4. ตรวจสอบประเภทข้อมูล (Scalar vs Vector vs Tensor)
> 5. ทดสอบบนเมื่อคุณภาพสูงก่อน

### การเลือก Numerical Schemes

```cpp
// ใน system/fvSchemes
// Numerical scheme configuration

gradSchemes
{
    default         Gauss linear;           // ทั่วไป
    grad(p)         leastSquares;           // เมชไม่สม่ำเสมอ
}

divSchemes
{
    default         Gauss upwind;           // เสถียรสูง
    div(phi,U)      Gauss linearUpwindV grad(U);  // ดุจำนวน
    div(phi,T)      Gauss limitedLinear 1;  // สมดุล
}

laplacianSchemes
{
    default         Gauss linear corrected; // แก้ไข non-orthogonality
}
```

### การตรวจสอบก่อน Run

```bash
# 1. ตรวจสอบเมช
checkMesh

# 2. ตรวจสอบ initial conditions
foamListTimes

# 3. ทดสอบด้วย time step เล็กๆ ก่อน
# ใน controlDict: deltaT 1e-5;

# 4. เพิ่ม debugging output
# ใน solver: Info << "Variable: " << variable << endl;
```

---

## 🔄 8. การเปรียบเทียบ fvc vs fvm

> [!NOTE] **📂 OpenFOAM Context**
> หัวข้อนี้เกี่ยวข้องกับ **Domain B: Numerics & Linear Algebra** และ **Domain E: Coding/Customization**
> - **ไฟล์**: ซอร์สโค้ดโซลเวอร์ (`applications/solvers/*.C`)
> - **Namespaces**: `fvc::` (finite volume calculus), `fvm::` (finite volume method)
> - **Return Types**: `fvc` returns `GeometricField`, `fvm` returns `fvMatrix`
> - **Usage**: `fvm` สำหรับ implicit discretization (สร้าง matrix), `fvc` สำหรับ explicit evaluation
> - **Compilation**: `fvm` ต้องเรียก `.solve()` เพื่อแก้ระบบสมการ
>
> ใน OpenFOAM คุณจะเห็นการใช้งานใน:
> - `src/finiteVolume/fvm/` - Implicit discretization operators
> - `src/finiteVolume/fvc/` - Explicit calculus operators
> - `src/finiteVolume/fvMatrix/` - Matrix representation และ solvers

### สรุปความแตกต่าง

| ปัจจัย | `fvc::` (Explicit) | `fvm::` (Implicit) |
|:---|:---|:---|
| **ความเสถียร** | Time step จำกัด | เสถียรโดยไม่มีเงื่อนไข |
| **ความแม่นยำ** | อันดับสูงกว่าได้ | มักเป็นอันดับแรก/ที่สอง |
| **ต้นทุนการคำนวณ** | ต่ำต่อการวนซ้ำ | สูงกว่าต่อการวนซ้ำ |
| **หน่วยความจำ** | จัดเก็บน้อยกว่า | ต้องการจัดเก็บเมทริกซ์ |
| **การบรรจบกัน** | อาจต้องการการวนซ้ำหลายครั้ง | การวนซ้ำน้อยกว่าสำหรับ steady state |
| **Complexity** | ง่าย | ซับซ้อน |
| **ผลลัพธ์** | `GeometricField` | `fvMatrix` |

### แนวทาปการใช้งาน

```cpp
// ใช้ fvm:: สำหรับ:
// Use fvm for implicit discretization of main equation terms
fvm::ddt(T)           // Temporal derivatives - always implicit
fvm::div(phi, T)      // Convection terms - implicit for stability
fvm::laplacian(DT, T) // Diffusion terms - implicit required

// ใช้ fvc:: สำหรับ:
// Use fvc for explicit evaluation of known quantities
fvc::grad(p)          // Pressure gradients - explicit evaluation
fvc::div(U)           // Divergence checks - post-processing
fvc::curl(U)          // Vorticity calculations - derived quantity
fvc::interpolate(U)   // Face interpolations - geometric operation
```

**Source:** 📂 `.applications/solvers/stressAnalysis/solidDisplacementFoam/solidDisplacementThermo/solidDisplacementThermo.C`

**คำอธิบาย (Thai):**
- **Source**: ไฟล์ `solidDisplacementThermo.C` แสดงการใช้งานทั้ง `fvm` (ในการแก้สมการ) และ `fvc` (สำหรับการคำนวณค่าต่างๆ)
- **Explanation**: การเลือกระหว่าง explicit และ implicit discretization เป็นการ trade-off ระหว่างความเสถียร ความแม่นยำ และต้นทุนการคำนวณ Implicit schemes สร้างเมทริกซ์ที่ต้องแก้ แต่ไม่มีข้อจำกัดเวลา
- **Key Concepts**:
  - **Explicit (fvc)**: คำนวณโดยตรงจากค่าที่รู้ ไม่ต้องแก้เมทริกซ์
  - **Implicit (fvm)**: สร้างระบบสมการเชิงเส้น ต้องแก้ด้วย linear solver
  - **Matrix Assembly**: fvm operations build coefficient matrix
  - **CFL Condition**: Explicit schemes มีขีดจำกัดความเร็บ wave

---

## 🎯 9. การประยุกต์ใช้จริง: กรณีศึกษา

> [!NOTE] **📂 OpenFOAM Context**
> หัวข้อนี้เกี่ยวข้องกับ **Domain E: Coding/Customization** และ **Domain B: Numerics & Linear Algebra**
> - **ไฟล์**: Custom solver code (เช่น `myCustomSolver.C` ใน `applications/solvers/`)
> - **Workflow**: แก้ไข solver code → compile ใหม่ (`wmake`) → run simulation
> - **Keywords**: `fvScalarMatrix`, `solve()`, `fvm::`, `fvc::`, `mag()`, `dimensionedScalar`
> - **Debugging Process**: อ่าน compiler errors → แก้ code → recompile → check log files
> - **Validation**: เปรียบเทียบกับ analytical solution หรือ experimental data
>
> ใน OpenFOAM คุณจะเห็นการใช้งานใน:
> - `applications/solvers/heatTransfer/` - Heat transfer solvers
> - `applications/solvers/multiphase/` - Multiphase flow solvers
> - `src/finiteVolume/` - Core FV implementation

### กรณีที่ 1: สมการพลังงานที่ไม่เสถียร

**ปัญหา**: สมการพลังงานระเบิดทันทีที่ run

```cpp
// ❌ PROBLEMATIC
// Explicit treatment of both convection and diffusion - unstable!
fvScalarMatrix TEqn
(
    fvm::ddt(T) + fvc::div(phi, T) - fvc::laplacian(DT, T) == source
);
```

**การวินิจฉัย**:
- Convection: `fvc::div` (Explicit, conditionally stable)
- Diffusion: `fvc::laplacian` (Explicit, very restrictive time step)

**วิธีแก้ไข**:

```cpp
// ✅ CORRECT
// Fully implicit treatment for unconditional stability
fvScalarMatrix TEqn
(
    fvm::ddt(T) + fvm::div(phi, T) - fvm::laplacian(DT, T) == source
);
```

### กรณีที่ 2: การคำนวณ Vorticity ที่ผิดพลาด

**ปัญหา**: ต้องการคำนวณ vorticity magnitude

```cpp
// ❌ ERROR
// Type mismatch: curl returns vector, not scalar
volScalarField vorticity = fvc::curl(U);  // Type mismatch!

// ✅ CORRECT
// First calculate vorticity vector, then magnitude
volVectorField vorticityVec = fvc::curl(U);
volScalarField vorticityMag = mag(vorticityVec);
```

### กรณีที่ 3: การใช้งาน Gradient ที่ผิดหน่วย

**ปัญหา**: คำนวณแรงลอยตัวแต่ได้ผลลัพธ์ผิดปกติ

```cpp
// ❌ WRONG UNITS
// Dimensional inconsistency in buoyancy force calculation
volVectorField F_buoyancy = fvc::grad(p) * g;  // [Force/Volume] * [Acceleration]

// ✅ CORRECT
// Buoyancy force based on density difference
volVectorField F_buoyancy = (rho - rhoRef) * g;  // [Mass/Volume] * [Acceleration]
```

**Source:** 📂 `.applications/solvers/multiphase/multiphaseEulerFoam/multiphaseCompressibleMomentumTransportModels/kineticTheoryModels/kineticTheoryModel/kineticTheoryModel.C`

**คำอธิบาย (Thai):**
- **Source**: ไฟล์ `kineticTheoryModel.C` จาก multiphaseEulerFoam แสดงการคำนวณ forces และ phase interactions ที่ซับซ้อน
- **Explanation**: กรณีศึกษาเหล่านี้แสดงข้อผิดพลาดที่พบบ่อยในการพัฒนา solver OpenFOAM การเข้าใจ dimensional analysis และ type system เป็นสิ่งสำคัญ
- **Key Concepts**:
  - **Vorticity**: $\boldsymbol{\omega} = \nabla \times \mathbf{U}$ เป็น vector field
  - **Buoyancy Force**: $F_b = (\rho - \rho_{ref})\mathbf{g}$ ขึ้นกับความต่างความหนาแน่น
  - **Dimensional Consistency**: ทุก term ในสมการต้องมีหน่วยเดียวกัน

---

## 📚 10. สรุป

> [!NOTE] **📂 OpenFOAM Context - Integration Overview**
> หัวข้อนี้รวมทุก Domain ใน OpenFOAM:
> - **Domain A (Physics)**: การคำนวณ gradient/ลมดับ/curl ของฟิลด์ physics ใน `0/` directory
> - **Domain B (Numerics)**: การเลือก schemes ใน `system/fvSchemes` และ solvers ใน `system/fvSolution`
> - **Domain C (Control)**: การตั้งค่า time step และ write interval ใน `system/controlDict`
> - **Domain D (Meshing)**: คุณภาพเมชที่ส่งผลต่อความแม่นยำของ calculus operations
> - **Domain E (Coding)**: การเขียน custom solver/boundary condition ใน `src/` และ `applications/solvers/`
>
> **การนำไปใช้**: เมื่อคุณเขียน solver ใหม่ คุณจะใช้:
> - `fvm::` สำหรับ terms หลักในสมการ (implicit)
> - `fvc::` สำหรับ source terms และ post-processing (explicit)
> - ตรวจสอบ dimensions ด้วย `field.dimensions()`
> - ตรวจสอบ mesh quality ด้วย `checkMesh`
> - เลือก numerical schemes ที่เหมาะสมกับคุณภาพเมช

การใช้แคลคูลัสเวกเตอร์ใน OpenFOAM ต้องการความเข้าใจที่ลึกซึ้งเกี่ยวกับ:

1. **ความแตกต่างระหว่าง Explicit (`fvc::`) และ Implicit (`fvm::`)**
   - Explicit: สำหรับ source terms และ post-processing
   - Implicit: สำหรับ terms ที่เป็น unknowns ในสมการ

2. **ความสอดคล้องของมิติและประเภทข้อมูล**
   - ตรวจสอบหน่วยเสมอ
   - ตรวจสอบ Scalar vs Vector vs Tensor

3. **ผลกระทบของคุณภาพเมช**
   - Non-orthogonality ต้องการ corrected schemes
   - Skewness สูงต้องการ limited schemes

4. **การเลือก Numerical Schemes ที่เหมาะสม**
   - สมดุลระหว่างความแม่นยำและความเสถียร
   - ปรับให้เข้ากับคุณภาพเมช

> [!TIP] 🎯 จำไว้: เมื่อเขียน solver ใหม่ ให้เริ่มต้นด้วย schemes ที่เสถียรที่สุด แล้วค่อยๆ เพิ่มความแม่นยำหลังจากที่สมการทำงานได้อย่างถูกต้อง

---

**การหลีกเลี่ยงข้อผิดพลาดเหล่านี้จะช่วยประหยัดเวลาในการดีบักและทำให้ solver ของคุณทำงานได้อย่างเสถียรและถูกต้อง**

---

## 🧠 Concept Check

<details>
<summary><b>1. ทำไมการใช้ `fvc::laplacian` แทน `fvm::laplacian` ใน diffusion term ทำให้ solver ไม่เสถียร?</b></summary>

**`fvc::laplacian`** เป็น **explicit** → คำนวณจากค่า **time step ก่อนหน้า**

ปัญหา:
- ต้องปฏิบัติตาม **Von Neumann stability:** $\Delta t \leq \frac{\Delta x^2}{2\Gamma}$
- สำหรับ mesh ละเอียด (Δx เล็ก) → **time step ต้องเล็กมากๆ**
- ถ้า time step ใหญ่เกินไป → **solver diverge**

**Solution:** ใช้ `fvm::laplacian` ซึ่งเป็น unconditionally stable

</details>

<details>
<summary><b>2. ถ้า `fvc::grad(p)` มีหน่วย [Pa/m] ทำไมไม่สามารถใช้โดยตรงเป็น acceleration ได้?</b></summary>

**Dimensional analysis:**
- `fvc::grad(p)` มีหน่วย $[Pa/m] = [kg/(m^2 \cdot s^2)]$ = **Force per unit volume**
- **Acceleration** มีหน่วย $[m/s^2]$

**Solution:** ต้องหารด้วย density $\rho$:
```cpp
volVectorField acc = -fvc::grad(p) / rho;  // หน่วย: [m/s²]
```

</details>

<details>
<summary><b>3. เมื่อ `checkMesh` แสดง non-orthogonality > 70° ควรทำอย่างไร?</b></summary>

**Options:**
1. **ปรับปรุง mesh** — ใช้ `snappyHexMesh` settings ที่ดีกว่า หรือปรับ geometry
2. **เปลี่ยน scheme** ใน `system/fvSchemes`:
   ```cpp
   laplacianSchemes
   {
       default Gauss linear corrected;  // เพิ่ม correction
       // หรือ
       default Gauss linear limited 0.5;  // สำหรับ mesh แย่มาก
   }
   ```
3. **เพิ่ม nNonOrthogonalCorrectors** ใน `system/fvSolution`

</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md) — ภาพรวม Vector Calculus
- **บทก่อนหน้า:** [05_Curl_and_Laplacian.md](05_Curl_and_Laplacian.md) — Curl และ Laplacian
- **บทถัดไป:** [07_Summary_and_Exercises.md](07_Summary_and_Exercises.md) — สรุปและแบบฝึกหัด
- **fvc vs fvm:** [02_fvc_vs_fvm.md](02_fvc_vs_fvm.md) — เปรียบเทียบ Explicit และ Implicit