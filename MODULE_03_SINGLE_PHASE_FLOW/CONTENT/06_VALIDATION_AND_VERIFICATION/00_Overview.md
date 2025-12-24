# การทวนสอบและตรวจสอบความถูกต้อง (Validation and Verification - V&V)

## 🔍 ภาพรวม (Overview)

ในโลกของ Computational Fluid Dynamics (CFD) ความมั่นใจในผลลัพธ์ไม่ได้มาจากภาพกราฟิกที่สวยงาม แต่มาจากกระบวนการ **V&V** ที่เข้มงวด โมดูลนี้ครอบคลุมรากฐานทางวิทยาศาสตร์และเครื่องมือใน OpenFOAM เพื่อวัดปริมาณความไม่แน่นอนและสร้างความเชื่อถือได้ให้กับผลการจำลอง

---

## 🎯 วัตถุประสงค์การเรียนรู้ (Learning Objectives)

เมื่อจบโมดูลนี้ คุณจะสามารถ:

1. **แยกแยะ V&V**: เข้าใจความแตกต่างระหว่าง "Solving the equations right" (Verification) และ "Solving the right equations" (Validation)
2. **วิเคราะห์ความเป็นอิสระของ Mesh**: ดำเนินการศึกษาการลู่เข้าของกริดและคำนวณ GCI
3. **ใช้ตัวชี้วัดความคลาดเคลื่อน**: คำนวณ Error Norms ($L_1, L_2, L_\infty$) ใน OpenFOAM
4. **ตรวจสอบความถูกต้องจากการทดลอง**: เปรียบเทียบผล CFD กับข้อมูล Benchmark (เช่น Cavity flow, Channel flow)
5. **วิเคราะห์ความละเอียดผนัง**: ตรวจสอบความเหมาะสมของ $y^+$ สำหรับแบบจำลองความปั่นป่วน

---

## 📐 1. แนวคิดหลักของ V&V (Core Concepts)

### 1.1 Verification กับ Validation

| ประเภท | คำถามหลัก | เป้าหมาย |
|---------|-----------|-----------|
| **Verification** | เราแก้สมการถูกต้องหรือไม่? | ลดข้อผิดพลาดเชิงตัวเลข (Numerical Errors) |
| **Validation** | เราแก้สมการที่ถูกต้องหรือไม่? | ลดข้อผิดพลาดจากการสร้างแบบจำลอง (Modeling Errors) |

**Verification** ตอบคำถามว่า "*เรากำลังแก้สมการอย่างถูกต้องหรือไม่?*" โดยตรวจสอบให้แน่ใจว่าผลเฉลยเชิงตัวเลขถูกต้องตามหลักคณิตศาสตร์

**Validation** ตอบคำถามว่า "*เรากำลังแก้สมการที่ถูกต้องหรือไม่?*" โดยตรวจสอบให้แน่ใจว่าแบบจำลองแสดงถึงความเป็นจริงทางกายภาพได้อย่างแม่นยำ

### 1.2 แหล่งที่มาของความไม่แน่นอน (Sources of Uncertainty)

#### ข้อผิดพลาดเชิงตัวเลข (Numerical Errors)

$$\epsilon_{\text{numerical}} = |f_{\text{numerical}} - f_{\text{exact}}|$$

ประกอบด้วย:
- **Discretization Errors**: การประมาณค่าผลต่าจากการแปลงสมการเชิงอนุพันธ์เป็นรูปแบบ discrete
- **Round-off Errors**: ความแม่นยำที่จำกัดของเลขทศนิยม
- **Iteration Errors**: การหยุด Solver แบบวนซ้ำก่อนที่จะลู่เข้าอย่างสมบูรณ์

ใน OpenFOAM สมการโมเมนตัมของ Navier-Stokes ถูกแบ่งย่อยเป็น:

```cpp
// Finite volume discretization of momentum equation
// Construct the matrix for the momentum equation using finite volume method
// fvm: implicit discretization, fvc: explicit calculation
fvVectorMatrix UEqn
(
    fvm::ddt(rho, U)                // Time derivative term (implicit)
  + fvm::div(phi, U)                // Convection term (implicit)
    ==                                // Equals operator
    fvc::div(-p*I)                   // Pressure gradient term (explicit)
  + fvc::div(tau)                    // Viscous stress divergence (explicit)
);
```

> **📖 คำอธิบายภาษาไทย**
>
> **แหล่งที่มา**: Finite Volume Discretization Framework
>
> **การอธิบาย**: โค้ดนี้แสดงการจัดทำเมตริกซ์สมการโมเมนตัมใน OpenFOAM โดยใช้วิธี Finite Volume Method (FVM)
> - `fvm::ddt(rho, U)` - เทอมอนุพันธ์เชิงเวลาของความหนาแน่นและความเร็ว (แบบ implicit)
> - `fvm::div(phi, U)` - เทอมการพาความร้อน/convective term (แบบ implicit)
> - `fvc::div(-p*I)` - เทอมความดัน/pressure gradient (แบบ explicit)
> - `fvc::div(tau)` - เทอมความเค้นเฉือน/viscous stress (แบบ explicit)
>
> **แนวคิดสำคัญ**:
> - **Implicit (fvm)**: ค่าที่ตำแหน่ง cell center ถูกคำนวณพร้อมกันในระบบสมการเชิงเส้น
> - **Explicit (fvc)**: ค่าที่คำนวณจาก time step ก่อนหน้า
> - การผสมผสานระหว่าง implicit และ explicit เป็นหัวใจของความเสถียรและประสิทธิภาพในการคำนวณ CFD

#### ข้อผิดพลาดในการสร้างแบบจำลอง (Modeling Errors)

$$\epsilon_{\text{model}} = |f_{\text{experimental}} - f_{\text{model}}|$$

ประกอบด้วย:
- **Turbulence Model Limitations**: การประมาณค่า Reynolds stress term ใน RANS models
- **Wall Function Errors**: การสร้างแบบจำลองใกล้ผนัง
- **Multiphase Model Errors**: การติดตามส่วนต่อประสานและแรงตึงผิว

#### ข้อผิดพลาดของข้อมูลนำเข้า (Input Uncertainties)

- ความคลาดเคลื่อนของ Boundary Conditions (เงื่อนไขขาเข้า, แรงดันขาออก)
- ความไม่แน่นอนของคุณสมบัติวัสดุ (ความหนืด, ความหนาแน่น, ค่าการนำความร้อน)
- ความไม่แน่นอนทางเรขาคณิต (ความคลาดเคลื่อนในการผลิต)

---

## ⚙️ 2. เครื่องมือและระเบียบวิธีใน OpenFOAM

### 2.1 Method of Manufactured Solutions (MMS)

เทคนิคการตรวจสอบความถูกต้องที่มีประสิทธิภาพในชุดทดสอบของ OpenFOAM:

**ขั้นตอนการทำงาน**:
1. กำหนดผลเฉลยเชิงวิเคราะห์ $u_{\text{man}}(\mathbf{x},t)$
2. คำนวณเทอมแหล่งกำเนิดเพื่อบังคับให้สมการผลิตผลเฉลยที่สร้างขึ้น
3. ศึกษาความลู่เข้าของ Mesh อย่างเป็นระบบ

**สมการที่ปรับปรุงแล้ว**:
$$\frac{\partial u_{\text{man}}}{\partial t} + \nabla \cdot (\mathbf{u} u_{\text{man}}) = \nabla \cdot (\Gamma \nabla u_{\text{man}}) + S_{\text{man}}$$

โดยที่เทอมแหล่งกำเนิดที่สร้างขึ้น:
$$S_{\text{man}} = \frac{\partial u_{\text{man}}}{\partial t} + \nabla \cdot (\mathbf{u} u_{\text{man}}) - \nabla \cdot (\Gamma \nabla u_{\text{man}})$$

### 2.2 Grid Convergence Index (GCI)

วิธีมาตรฐานในการรายงานความไม่แน่นอนเชิงตัวเลข:

**การคำนวณ**:
- **อันดับความแม่นยำที่สังเกตได้**:
  $$p = \frac{\ln|\epsilon_{32}/\epsilon_{21}|}{\ln(r)}$$
  โดยที่ $\epsilon_{32} = f_3 - f_2$ และ $\epsilon_{21} = f_2 - f_1$

- **GCI สำหรับ Mesh ละเอียด**:
  $$\text{GCI}_{\text{fine}} = \frac{1.25|\epsilon_{32}|}{r^p - 1}$$

**เกณฑ์ GCI Tolerance**:

| การใช้งาน | GCI Tolerance | คำอธิบาย |
|-------------|---------------|-----------|
| **Engineering Design Studies** | **GCI < 5%** | ความแม่นยำที่สมเหตุสมผลสำหรับการตัดสินใจออกแบบ |
| **Research Publications** | **GCI < 2%** | ความแม่นยำสูงสำหรับการเปรียบเทียบกับข้อมูลทดลอง |
| **High-Accuracy Validation** | **GCI < 1%** | ความแม่นยำสูงสุดสำหรับ Benchmark หรือพัฒนาโมเดลใหม่ |

### 2.3 Error Norms ใน OpenFOAM

ตัวชี้วัดเชิงปริมาณของความแม่นยำ:

**$L_1$ Norm (Average Absolute Error)**:
$$L_1 = \frac{1}{V} \int_{\Omega} | \phi - \phi_{\text{ref}} | \, \mathrm{d}V$$

**$L_2$ Norm (Root Mean Square Error)**:
$$L_2 = \sqrt{\frac{1}{V} \int_{\Omega} (\phi - \phi_{\text{ref}})^2 \, \mathrm{d}V}$$

**$L_\infty$ Norm (Maximum Absolute Error)**:
$$L_{\infty} = \max_{\Omega} | \phi - \phi_{\text{ref}} |$$

**การนำไปใช้ใน OpenFOAM**:

```cpp
// OpenFOAM implementation of error norms
// Calculate quantitative error metrics for validation studies
void calculateErrorNorms(
    const volScalarField& field,          // Field to validate
    const volScalarField& reference,      // Reference/analytical solution
    const fvMesh& mesh                    // Mesh containing volume data
)
{
    // Get cell volumes from mesh
    const scalarField& V = mesh.V();
    scalar totalVolume = sum(V);

    // Absolute error field - calculate magnitude of difference
    volScalarField error = mag(field - reference);

    // L1 norm - average absolute error over entire domain
    scalar L1 = sum(error * V) / totalVolume;

    // L2 norm - root mean square error
    volScalarField errorSqr = sqr(field - reference);
    scalar L2 = sqrt(sum(errorSqr * V) / totalVolume);

    // L∞ norm - maximum absolute error in domain
    scalar Linf = max(error).value();

    // Output all error norms to console/log
    Info << "Error norms:" << nl
         << "  L1  = " << L1 << nl
         << "  L2  = " << L2 << nl
         << "  L∞ = " << Linf << endl;
}
```

> **📖 คำอธิบายภาษาไทย**
>
> **แหล่งที่มา**: Field Error Analysis Utilities
>
> **การอธิบาย**: ฟังก์ชันนี้คำนวณตัวชี้วัดความคลาดเคลื่อน 3 ชนิดสำหรับการตรวจสอบความถูกต้อง:
> - **$L_1$ Norm**: ค่าเฉลี่ยของความคลาดเคลื่อนสัมบูรณ์ → ใช้ประเมินความแม่นยำโดยรวม
> - **$L_2$ Norm**: รากที่สองของค่าเฉลี่ยความคลาดเคลื่อนกำลังสอง → ให้น้ำหนักมากกับความคลาดเคลื่อนขนาดใหญ่
> - **$L_\infty$ Norm**: ค่าความคลาดเคลื่อนสูงสุด → สำคัญสำหรับจุดที่มีความละเอียดสูง
>
> **แนวคิดสำคัญ**:
> - **Weighted Integration**: การคูณด้วยปริมาตรเซลล์ (V) เพื่อถ่วงน้ำหนักตามขนาดเซลล์
> - **Mesh Independence**: ใช้ error norms เพื่อตรวจสอบว่า mesh ละเอียดพอหรือยัง
> - **Validation Metric**: เปรียบเทียบผล CFD กับ analytical solution หรือ experimental data

### 2.4 การวิเคราะห์ความละเอียดผนัง (Wall Resolution Analysis)

**ระยะห่างไร้มิติจากผนัง $y^+$**:

$$y^+ = \frac{y u_{\tau}}{\nu} = \frac{y \sqrt{\tau_w/\rho}}{\nu}$$

โดยที่:
- $y$ = ระยะห่างตั้งฉากกับผนัง (wall-normal distance)
- $u_{\tau}$ = ความเร็วเสียดทาน (friction velocity)
- $\nu$ = ความหนืดจลนศาสตร์ (kinematic viscosity)
- $\tau_w$ = ความเค้นเฉือนที่ผนัง (wall shear stress)

**คำสั่งใน OpenFOAM**:

```bash
# คำนวณ yPlus สำหรับทุก patch ที่เป็นผนัง
# Calculate dimensionless wall distance for all wall patches
postProcess -func yPlus

# คำนวณความเค้นเฉือนที่ผนัง
# Calculate wall shear stress on wall boundaries
postProcess -func wallShearStress

# เขียนสนาม yPlus สำหรับการแสดงผลด้วยภาพ
# Write yPlus field for visualization in ParaView
yPlus
```

> **📖 คำอธิบายภาษาไทย**
>
> **แหล่งที่มา**: Post-Processing Utilities for Turbulence Modeling
>
> **การอธิบาย**: คำสั่ง postProcess ใช้คำนวณปริมาณที่สำคัญสำหรับ turbulence modeling:
> - **yPlus**: ระยะห่างไร้มิติ $y^+$ จากผนัง → บอกความละเอียดของ mesh ใกล้ผนัง
> - **wallShearStress**: ความเค้นเฉือน $\tau_w$ → ใช้คำนวณ $u_\tau$ และ $y^+$
>
> **แนวคิดสำคัญ**:
> - **Viscous Sublayer**: ถ้า $y^+ < 1$ → mesh ละเอียดพอสำหรับ low-Re models
> - **Wall Functions**: ถ้า $30 < y^+ < 300$ → เหมาะกับ high-Re models ที่ใช้ wall functions
> - **Mesh Quality**: ต้องตรวจสอบ $y^+$ ทุก patch เพื่อให้แน่ใจว่า mesh มีคุณภาพสม่ำเสมอ

**ข้อกำหนดของ Mesh ตาม Turbulence Model**:

| Model | ช่วง $y^+$ เป้าหมาย | ลักษณะ |
|-------|-------------------|-----------|
| **Low-Re $k$-$ε$** | $y^+ < 1$ | การแยก viscous sublayer โดยตรง |
| **Low-Re $k$-$ω$ SST** | $y^+ < 1$ | การผสมผสานระหว่าง $k$-$ω$ ใกล้ผนังและ $k$-$ε$ ในกระแสอิสระ |
| **Standard $k$-$ε$** | $30 < y^+ < 300$ | Wall functions ประมาณค่าฟิสิกส์ใกล้ผนัง |
| **Spalart-Allmaras** | $y^+ < 1$ | โมเดลสมการเดียวต้องการการแยกการกระจายความหนืวใกล้ผนัง |

**การประมาณความสูงเซลล์แรก**:

$$\Delta y = \frac{y^+_{\text{target}} \nu}{u_\tau}$$

ตัวอย่าง: อากาศที่ 20°C ($\nu = 1.5 \times 10^{-5}$ m²/s), $U_\infty = 10$ m/s, $y^+ = 1$ เป้าหมาย

$$u_\tau \approx 0.05 \times 10 = 0.5 \, \text{m/s}$$
$$\Delta y \approx \frac{1 \times 1.5 \times 10^{-5}}{0.5} = 3 \times 10^{-5} \, \text{m} = 30 \, \mu\text{m}$$

---

## 🧪 3. กรณีทดสอบมาตรฐาน (Benchmark Cases)

OpenFOAM มีกรณีทดสอบจำนวนมากในไดเรกทอรี `tutorials/`:

| กรณีทดสอบ | วัตถุประสงค์ | ฟิสิกส์ที่เกี่ยวข้อง |
|-------------|-------------|-------------------|
| **Lid-Driven Cavity** | Benchmark สำหรับ Solver การไหลแบบอัดตัวไม่ได้ | การไหลแบบลามินาร์ในช่องว่าง |
| **Backward-Facing Step** | การทดสอบการแยกตัวและการกลับมารวมกัน | กระแสน้ำวนและการแยกชั้นขอบ |
| **Turbulent Channel Flow** | การทวนสอบสำหรับแบบจำลองความปั่นป่วน | การไหลแบบปั่นป่วนในช่องทาง |
| **Dam Break** | การทวนสอบการไหลแบบหลายเฟส | การไหลแบบอิสระของพื้นผิว |

### 3.1 การทวนสอบด้วยผลเฉลยเชิงวิเคราะห์

#### การไหลแบบ Couette
สำหรับการไหลแบบลามินาร์แบบคงที่ระหว่างแผ่นขนาน:
$$u(y) = \frac{U}{h} y$$

โดยที่:
- $U$ = ความเร็วของแผ่นที่เคลื่อนที่
- $h$ = ความสูงของช่องว่าง

#### การไหลแบบ Poiseuille
สำหรับการไหลแบบขับเคลื่อนด้วยความดันในท่อ:
$$u(r) = \frac{\Delta p}{4\mu L} (R^2 - r^2)$$

โดยที่:
- $\Delta p$ = ความแตกต่างของความดัน
- $\mu$ = ความหนืวจลนศาสตร์ (dynamic viscosity)
- $L$ = ความยาวท่อ
- $R$ = รัศมีท่อ
- $r$ = พิกัดในแนวรัศมี

---

## 🏗️ 4. โครงสร้างกรณีทดสอบใน OpenFOAM

### 4.1 โครงสร้างไดเรกทอรี

```
testCase/
├── 0/              # เงื่อนไขเริ่มต้น (Initial conditions)
├── constant/       # Mesh และคุณสมบัติทางกายภาพ (Mesh and physical properties)
├── system/         # การควบคุม Solver (Solver control)
├── validation/     # ผลเฉลยอ้างอิง (Reference solutions)
└── Allrun         # สคริปต์การดำเนินการทดสอบ (Test execution script)
```

### 4.2 การตั้งค่า controlDict สำหรับ V&V

```cpp
// system/controlDict
// Solver and time control settings for validation studies
application     simpleFoam;              // Steady-state incompressible solver
startFrom       startTime;               // Start from latest time
startTime       0;                        // Initial time value
stopAt          endTime;                  // Stop condition type
endTime         1000;                     // Final time value
deltaT          1;                        // Time step size
adjustTimeStep  no;                       // Fixed time step

// Convergence criteria for residuals
// Lower values ensure higher accuracy for validation
residualControl
{
    p               1e-6;                 // Pressure residual tolerance
    U               1e-6;                 // Velocity residual tolerance
}
```

> **📖 คำอธิบายภาษาไทย**
>
> **แหล่งที่มา**: Solver Control Dictionary (system/controlDict)
>
> **การอธิบาย**: ไฟล์นี้ควบคุมการทำงานของ solver และเกณฑ์การลู่เข้า:
> - **residualControl**: กำหนดค่าความคลาดเคลื่อนที่ยอมรับได้ (tolerance)
>   - ถ้า residual < 1e-6 → ผลลัพธ์มีความแม่นยำสูง (เหมาะกับ validation)
>   - ถ้า residual = 1e-4 → ความแม่นยำปานกลาง (เหมาะกับ engineering design)
>
> **แนวคิดสำคัญ**:
> - **Convergence**: การลู่เข้าของ iterative solver สำคัญต่อความแม่นยำ
> - **Residual Monitoring**: ต้องตรวจสอบ residuals ของทุกตัวแปร (p, U, k, epsilon, etc.)
> - **Validation Requirement**: ใช้ tolerance ที่เข้มงวด (1e-6 หรือต่ำกว่า)

### 4.3 การทดสอบการถดถอย (Regression Testing)

OpenFOAM ใช้การทดสอบการถดถอยเพื่อตรวจจับการเปลี่ยนแปลงโค้ด:

```cpp
// Sample regression test structure
// Automated testing framework to detect code changes
Foam::Info << "Running regression test for " << solverName << nl;

// Compare current solution with reference solution
// Calculate maximum absolute difference across domain
scalar error = max(mag(phi - phiRef));

// Check if error exceeds tolerance threshold
if (error > tolerance)
{
    FatalErrorIn("regressionTest")
        << "Regression test failed. Error: " << error
        << " exceeds tolerance: " << tolerance
        << abort(FatalError);
}
```

> **📖 คำอธิบายภาษาไทย**
>
> **แหล่งที่มา**: Test Framework Utilities
>
> **การอธิบาย**: การทดสอบการถดถอย (regression testing) ใช้ตรวจจับการเปลี่ยนแปลงที่ไม่คาดคิด:
> - **Reference Solution (phiRef)**: ผลลัพธ์ที่ได้รับการตรวจสอบแล้ว ใช้เป็นเกณฑ์
> - **Current Solution (phi)**: ผลลัพธ์จากการรันโค้ดปัจจุบัน
> - **Tolerance Check**: ถ้า error > tolerance → อาจมี bug หรือการเปลี่ยนแปลงโค้ดที่ไม่ถูกต้อง
>
> **แนวคิดสำคัญ**:
> - **Automated Testing**: ใช้ใน CI/CD pipeline เพื่อตรวจสอบความถูกต้องของโค้ด
> - **Version Control**: เก็บ reference solutions ใน repository พร้อมกับโค้ด
> - **Verification Tool**: ช่วยตรวจสอบว่าการอัปเดตโค้ดไม่ทำให้ผลลัพธ์เปลี่ยนแปลง

---

## ⚠️ 5. ความท้าทายและข้อจำกัด

### 5.1 Verification Challenges

- **Discretization errors**: อาจบดบังข้อผิดพลาดในการนำไปใช้
- **Boundary condition implementation**: มักเป็นแหล่งที่มาของข้อผิดพลาดที่ละเอียดอ่อน
- **Parallel implementation**: ปัญหาความสอดคล้องกันระหว่าง serial และ parallel

### 5.2 Validation Limitations

- **Experimental uncertainty**: ข้อผิดพลาดในการวัดและผลกระทบจากสิ่งอำนวยความสะดวก
- **Scale effects**: ความแตกต่างของสเกลในห้องปฏิบัติการกับสเกลการใช้งาน
- **Model form uncertainty**: ข้อจำกัดของแบบจำลองทางฟิสิกส์

---

## ✅ 6. แนวทางปฏิบัติที่ดีที่สุด (Best Practices)

1. **Start Simple**: ตรวจสอบด้วย analytical solutions ก่อนกรณีที่ซับซ้อน
2. **Systematic Approach**: ใช้ระเบียบวิธีทดสอบที่เป็นระบบ
3. **Documentation**: เก็บบันทึกรายละเอียดของกิจกรรม V&V ทั้งหมด
4. **Continuous Process**: ผสานรวม V&V ตลอดวงจรการพัฒนา
5. **Peer Review**: ให้ผลลัพธ์ได้รับการตรวจสอบโดยอิสระเมื่อเป็นไปได้

---

## ⏱️ ระยะเวลาเรียนโดยประมาณ

- **ส่วนทฤษฎี (V&V Principles)**: 2-3 ชั่วโมง
- **ส่วนฝึกปฏิบัติ (Mesh Study & Case Setup)**: 2-3 ชั่วโมง
- **รวม**: 4-6 ชั่วโมง

---

## 📖 Key Takeaway

> **ใน CFD ความมั่นใจไม่ได้มาจากการได้ผลลัพธ์ที่สมบูรณ์แบบ แต่มาจากการวัดปริมาณความไม่แน่นอนและการตรวจสอบความถูกต้องอย่างเป็นระบบ**

---

**หัวข้อถัดไป**: [หลักการ V&V อย่างละเอียด](./01_V_and_V_Principles.md)