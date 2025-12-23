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
fvVectorMatrix UEqn
(
    fvm::ddt(rho, U)
  + fvm::div(phi, U)
  ==
    fvc::div(-p*I)
  + fvc::div(tau)
);
```

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
void calculateErrorNorms(
    const volScalarField& field,
    const volScalarField& reference,
    const fvMesh& mesh
)
{
    const scalarField& V = mesh.V();
    scalar totalVolume = sum(V);

    // Absolute error field
    volScalarField error = mag(field - reference);

    // L1 norm
    scalar L1 = sum(error * V) / totalVolume;

    // L2 norm
    volScalarField errorSqr = sqr(field - reference);
    scalar L2 = sqrt(sum(errorSqr * V) / totalVolume);

    // L∞ norm
    scalar Linf = max(error).value();

    Info << "Error norms:" << nl
         << "  L1  = " << L1 << nl
         << "  L2  = " << L2 << nl
         << "  L∞ = " << Linf << endl;
}
```

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
postProcess -func yPlus

# คำนวณความเค้นเฉือนที่ผนัง
postProcess -func wallShearStress

# เขียนสนาม yPlus สำหรับการแสดงผลด้วยภาพ
yPlus
```

**ข้อกำหนดของ Mesh ตาม Turbulence Model**:

| Model | ช่วง $y^+$ เป้าหมาย | ลักษณะ |
|-------|-------------------|-----------|
| **Low-Re $k$-$ε$** | $y^+ < 1$ | การแยก viscous sublayer โดยตรง |
| **Low-Re $k$-$ω$ SST** | $y^+ < 1$ | การผสมผสานระหว่าง $k$-$ω$ ใกล้ผนังและ $k$-$ε$ ในกระแสอิสระ |
| **Standard $k$-$ε$** | $30 < y^+ < 300$ | Wall functions ประมาณค่าฟิสิกส์ใกล้ผนัง |
| **Spalart-Allmaras** | $y^+ < 1$ | โมเดลสมการเดียวต้องการการแยกการกระจายความหนืดใกล้ผนัง |

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
- $\mu$ = ความหนืดจลนศาสตร์ (dynamic viscosity)
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
application     simpleFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         1000;
deltaT          1;
adjustTimeStep  no;

// เกณฑ์การลู่เข้า (Convergence criteria)
residualControl
{
    p               1e-6;
    U               1e-6;
}
```

### 4.3 การทดสอบการถดถอย (Regression Testing)

OpenFOAM ใช้การทดสอบการถดถอยเพื่อตรวจจับการเปลี่ยนแปลงโค้ด:

```cpp
// โครงสร้างการทดสอบการถดถอยตัวอย่าง
Foam::Info << "Running regression test for " << solverName << nl;

// เปรียบเทียบกับผลเฉลยอ้างอิง
scalar error = max(mag(phi - phiRef));
if (error > tolerance)
{
    FatalErrorIn("regressionTest")
        << "Regression test failed. Error: " << error
        << " exceeds tolerance: " << tolerance
        << abort(FatalError);
}
```

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
