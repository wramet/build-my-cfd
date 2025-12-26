# 01 Verification Fundamentals (พื้นฐานการตรวจสอบความถูกต้อง)

> [!INFO] Module Focus
> การสร้างความเชื่อถือได้ (Reliability) ให้กับผลลัพธ์ CFD ผ่านกระบวนการตรวจสอบเชิงตัวเลข (Numerical Verification) และความเข้าใจในโครงสร้างระบบทดสอบของ OpenFOAM

## 🎯 วัตถุประสงค์การเรียนรู้ (Learning Objectives)
- เข้าใจความแตกต่างระหว่าง **Verification** (Code Check) และ **Validation** (Physics Check)
- เชี่ยวชาญวิธีการ **MMS** (Method of Manufactured Solutions) และการศึกษา **Grid Convergence**
- เข้าใจโครงสร้างและสถาปัตยกรรมของชุดทดสอบใน OpenFOAM (`applications/test`)

## 📋 ข้อกำหนดเบื้องต้น (Prerequisites)
- พื้นฐานการใช้งาน OpenFOAM และโครงสร้างโฟลเดอร์ Case
- ความเข้าใจในการเขียนโปรแกรม C++ เบื้องต้น
- พื้นฐานระเบียบวิธีเชิงตัวเลข (Numerical Methods)

---

## 📘 บทนำ (Introduction)

### ความสำคัญของการตรวจสอบความถูกต้อง

ในการจำลองทางการคำนวณ (Computational Fluid Dynamics: CFD) ผลลัพธ์ที่ได้จากการแก้สมการเชิงอนุพันธ์ด้วยคอมพิวเตอร์จะต้องได้รับการตรวจสอบอย่างเป็นระบบเพื่อให้มั่นใจในความถูกต้องและความน่าเชื่อถือ กระบวนการนี้แบ่งออกเป็นสองส่วนหลัก:

1. **Verification (การตรวจสอบเชิงตัวเลข)**: ตรวจสอบว่าโค้ดแก้สมการถูกต้องตามระเบียบวิธีเชิงตัวเลขหรือไม่
2. **Validation (การตรวจสอบเชิงฟิสิกส์)**: ตรวจสอบว่าแบบจำลองทางคณิตศาสตร์ (Mathematical Model) สอดคล้องกับปรากฏการณ์ทางฟิสิกส์จริงหรือไม่

### Verification vs Validation

```mermaid
flowchart LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
A[Physical Reality]:::explicit -->|Compare| B{Validation}:::explicit
B --> C[Mathematical Model]:::implicit
C -->|Discretization| D[Numerical Model]:::implicit
D -->|Verification| E[Computer Code]:::implicit
E --> F[Simulation Results]:::explicit
```

**ตัวอย่างสมการเชิงอนุพันธ์ที่ใช้ในการตรวจสอบ:**

สมการขนส่ง (Transport Equation) แบบทั่วไป:

$$
\frac{\partial (\rho \phi)}{\partial t} + \nabla \cdot (\rho \mathbf{u} \phi) = \nabla \cdot (\Gamma \nabla \phi) + S_\phi
$$

โดยที่:
- $\phi$ = ปริมาณที่ถูกขนส่ง (Transported Variable)
- $\rho$ = ความหนาแน่น (Density)
- $\mathbf{u}$ = ความเร็ว (Velocity)
- $\Gamma$ = สัมประสิทธิ์การแพร่ (Diffusion Coefficient)
- $S_\phi$ = เทอมต้นกำเนิด (Source Term)

### แนวคิดพื้นฐานของการตรวจสอบ (Fundamental Concepts)

#### 1. Order of Accuracy (ลำดับความแม่นยำ)

ในการวิเคราะห์เชิงตัวเลข ความผิดพลาดจากการ Discretization สามารถเขียนในรูปแบบ:

$$
\epsilon = C h^p + \mathcal{O}(h^{p+1})
$$

โดยที่:
- $\epsilon$ = ความผิดพลาด (Error)
- $h$ = ขนาด Grid Spacing
- $p$ = ลำดับความแม่นยำ (Order of Accuracy)
- $C$ = ค่าคงที่

#### 2. Grid Convergence Study (การศึกษาการลู่เข้าของเมช)

การศึกษาโดยใช้เมชหลายขนาดเพื่อยืนยันว่าผลลัพธ์ลู่เข้าสู่ค่าที่ไม่แปรเปลี่ยนเมื่อลดขนาดเมช:

$$
\phi_{h} \to \phi_{exact} \quad \text{as} \quad h \to 0
$$

ตัวอย่างโครงสร้างไฟล์ `fvSchemes` สำหรับการทดสอบ:

```cpp
// Finite volume schemes dictionary for numerical discretization
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      fvSchemes;
}

// Temporal discretization schemes
ddtSchemes
{
    default Euler; // First-order implicit Euler scheme
}

// Gradient calculation schemes
gradSchemes
{
    default Gauss linear; // Linear interpolation with Gauss theorem
}

// Divergence (convection) schemes
divSchemes
{
    default none;
    div(phi,U) Gauss limitedLinearV 1; // Limited linear scheme with van Leer limiter
    div(phi,k) Gauss limitedLinear 1;
    div(phi,epsilon) Gauss limitedLinear 1;
}

// Laplacian (diffusion) schemes
laplacianSchemes
{
    default Gauss linear corrected; // Corrected surface normal gradient
}
```

> **คำอธิบาย (Explanation):**
> ไฟล์ `fvSchemes` กำหนดระเบียบวิธีเชิงตัวเลขที่ใช้ในการ discretize สมการใน OpenFOAM:
> - **ddtSchemes**: กำหนดวิธีการแก้เชิงเวลา (Temporal discretization) - Euler แบบ First-order เหมาะสำหรับการทดสอบเบื้องต้น
> - **gradSchemes**: คำนวณ Gradient ของ Field ที่ cell face ด้วยวิธี Gauss linear
> - **divSchemes**: จัดการเทอม Convection ด้วย Limited Linear scheme เพื่อป้องกันการ oscillate
> - **laplacianSchemes**: แก้เทอม Diffusion พร้อม corrected surface normal gradient เพื่อความแม่นยำ
>
> **แหล่งที่มา (Source):** 📂 `applications/solvers/stressAnalysis/solidDisplacementFoam/` (Reference for scheme structure)

---

#### 3. Method of Manufactured Solutions (MMS)

เทคนิคสำคัญในการ Verification โดยการกำหนดคำตอบที่ต้องการล่วงหน้า แล้วคำนวณ Source Term ที่สอดคล้อง:

**ขั้นตอนการดำเนินการ:**

1. **กำหนด Solution ที่ต้องการ**: $\phi_{exact}(x, t)$
2. **แทนค่าในสมการ**: หา $S_\phi$ ที่ทำให้สมการเป็นจริง
3. **รัน Simulation**: ใช้ Source Term ที่คำนวณได้
4. **เปรียบเทียบ**: ตรวจสอบความผิดพลาด

ตัวอย่าง: สมการ Diffusion แบบ 1D

$$
\frac{\partial \phi}{\partial t} = \alpha \frac{\partial^2 \phi}{\partial x^2} + S(x,t)
$$

ถ้ากำหนด $\phi_{exact} = \sin(\pi x) \cdot \exp(-t)$ แล้ว:

$$
S(x,t) = -\sin(\pi x) e^{-t} + \alpha (-\pi^2 \sin(\pi x) e^{-t})
$$

---

## 🔧 เครื่องมือและวิธีการหลัก (Key Tools and Methods)

### 1. Richardson Extrapolation (การพิเศษของ Richardson)

ใช้ในการประมาณค่าที่แม่นยำจากผลลัพธ์ของเมชหลายขนาด:

$$
\phi_{exact} \approx \phi_2 + \frac{\phi_2 - \phi_1}{r^p - 1}
$$

โดยที่:
- $\phi_1, \phi_2$ = ผลลัพธ์จากเมชขนาดต่างกัน
- $r$ = อัตราส่วนของขนาดเมช (Grid Refinement Ratio)
- $p$ = ลำดับความแม่นยำที่คาดหวัง

### 2. Grid Convergence Index (GCI)

ดัชนีมาตรฐานสำหรับรายงานความไม่แน่นอนจากเมช:

$$
GCI = \frac{F_s |e|}{r^p - 1}
$$

โดยที่:
- $F_s$ = ปัจจัยความปลอดภัย (Safety Factor, มักใช้ 1.25 สำหรับชุดเมช 3 ขนาด)
- $e$ = ความผิดพลาดสัมพัทธ์ระหว่างเมช

> **[MISSING DATA]**: Insert specific simulation results/graphs for this section.

### 3. โครงสร้างการทดสอบใน OpenFOAM

ไดเรกทอรี `applications/test` ใน OpenFOAM มีโครงสร้างสำคัญ:

```
$WM_PROJECT_DIR/applications/test/
├── Mathematics/          // ทดสอบฟังก์ชันคณิตศาสตร์
├── matrices/             // ทดสอบ Linear Solvers
├── field/                // ทดสอบ Field Operations
└── ...
```

ตัวอย่างการสร้าง Unit Test แบบง่าย:

```cpp
// Basic verification test for gradient calculations
#include "fvCFD.H"

int main(int argc, char *argv[])
{
    // Initialize OpenFOAM environment
    #include "setRootCaseLists.H"
    #include "createTime.H"
    #include "createMesh.H"

    // Create test field - scalar field on mesh cells
    volScalarField phi
    (
        IOobject
        (
            "phi",                      // Field name
            runTime.timeName(),         // Time directory
            mesh,                       // Mesh reference
            IOobject::MUST_READ,        // Must read from file
            IOobject::AUTO_WRITE        // Auto-write on output
        ),
        mesh
    );

    // Test gradient calculation using finite volume calculus
    volVectorField gradPhi(fvc::grad(phi));

    // Verify error magnitude (dot product with x-direction unit vector)
    scalar error = mag(gradPhi & vector(1, 0, 0)).average();
    Info<< "Gradient Error: " << error << endl;

    return 0;
}
```

> **คำอธิบาย (Explanation):**
> โค้ดนี้แสดงตัวอย่างการสร้าง Unit Test สำหรับตรวจสอบการคำนวณ Gradient ใน OpenFOAM:
> - **Header Inclusions**: `fvCFD.H` รวม core finite volume tools ที่จำเป็น
> - **Initialization**: สาม standard include files สร้าง case, time, และ mesh objects
> - **Field Creation**: `volScalarField phi` สร้าง scalar field บน cell centers พร้อมอ่านจากไฟล์
> - **Gradient Test**: `fvc::grad()` คำนวณ gradient ด้วย finite volume calculus
> - **Error Calculation**: คำนวณความผิดพลาดโดย project gradient ไปทาง x-direction
>
> **แนวคิดสำคัญ (Key Concepts):**
> - **volScalarField**: Field ค่าเชิงเส้นกำกับ (scalar) บน cell centers
> - **fvc::grad**: Finite Volume Calculus - คำนวณ gradient จาก cell center values
> - **mag()**: ฟังก์ชันคำนวณ magnitude ของ vector/tensor
>
> **แหล่งที่มา (Source):** 📂 `applications/solvers/stressAnalysis/solidDisplacementFoam/solidDisplacementThermo/solidDisplacementThermo.C` (Reference pattern for field operations)

---

## 📊 แนวทางการประยุกต์ใช้ (Application Guidelines)

### ขั้นตอนการ Verification สำหรับ OpenFOAM Case

1. **Grid Independence Study**
   - สร้างเมช 3 ขนาด (Coarse, Medium, Fine)
   - Refinement Ratio: $r \geq 1.3$
   - วิเคราะห์ตัวแปรสำคัญ (เช่น Drag Coefficient, Nusselt Number)

2. **Temporal Convergence Study**
   - ทดสอบ Time Step หลายขนาด
   - ตรวจสอบสถานะคงตัว (Steady State)

3. **Code Verification**
   - ใช้ MMS กับ Test Cases ที่รู้คำตอบ
   - ตรวจสอบ Order of Accuracy

ตัวอย่างการตั้งค่าใน `controlDict`:

```cpp
// Simulation control dictionary for verification studies
application     simpleFoam;        // Steady-state incompressible solver

startFrom       latestTime;        // Start from latest results

startTime       0;                 // Initial time value

stopAt          endTime;           // Stop at specified end time

endTime         1000;              // Final time value

deltaT          1;                 // Time step size

writeControl    timeStep;          // Write output based on time steps

writeInterval   100;               // Write every 100 time steps

// Function objects for convergence monitoring
functions
{
    convergence
    {
        type            convergence; // Convergence checking function
        libs            ("libutilityFunctionObjects.so");
        fields          (U p);      // Monitor velocity and pressure
        tolerance       1e-6;       // Convergence tolerance
    }
}
```

> **คำอธิบาย (Explanation):**
> ไฟล์ `controlDict` คือจุดควบคุมหลักของ simulation ใน OpenFOAM:
> - **application**: ระบุ solver ที่จะใช้ (simpleFoam สำหรับ steady-state incompressible flow)
> - **Time Control**: กำหนดช่วงเวลาของการจำลอง (startTime ถึง endTime)
> - **writeControl/writeInterval**: ควบคุมความถี่ในการบันทึกผลลัพธ์
> - **functions**: สร้าง function objects สำหรับ monitoring ความลู่เข้าแบบ real-time
>
> **แนวคิดสำคัญ (Key Concepts):**
> - **Function Objects**: กลไกของ OpenFOAM สำหรับ compute derived quantities ระหว่าง simulation
> - **Convergence Monitoring**: ตรวจสอบการลู่เข้าของ solution ผ่าน tolerance threshold
> - **Steady-State Simulation**: ไม่มีการเปลี่ยนแปลงตามเวลา - ใช้ large time steps
>
> **แหล่งที่มา (Source):** 📂 `applications/solvers/stressAnalysis/solidDisplacementFoam/` (Reference for control dictionary structure)

---

## 🚀 บทสรุป (Summary)

การตรวจสอบความถูกต้อง (Verification) เป็นกระบวนการสำคัญที่ช่วยให้เรามั่นใจในความน่าเชื่อถือของผลลัพธ์ CFD โดยเฉพาะอย่างยิ่งเมื่อใช้ OpenFOAM ซึ่งเป็นโค้ดแบบ Open Source ที่ผู้ใช้สามารถปรับเปลี่ยนและเพิ่มฟังก์ชันการทำงานได้ การเข้าใจหลักการ Verification จึงเป็นสิ่งจำเป็น

**หัวข้อถัดไปที่ควรศึกษา:**
- Method of Manufactured Solutions อย่างละเอียด
- Grid Convergence Index (GCI) และการประยุกต์ใช้
- สถาปัตยกรรมระบบทดสอบของ OpenFOAM

---

## 📚 หัวข้อทางเทคนิค (Technical Topics)

### 01 [[01_Introduction|บทนำสู่การตรวจสอบความถูกต้อง]]
ปรัชญาการทดสอบแบบหลายชั้น (Multi-layered testing) และความแตกต่างระหว่างการตรวจสอบโค้ดและการตรวจสอบฟิสิกส์

### 02 [[02_Numerical_Methods|วิธีการตรวจสอบทางตัวเลข]]
เจาะลึก MMS, Richardson Extrapolation และดัชนี GCI เพื่อยืนยันลำดับความแม่นยำ (Order of Accuracy)

### 03 [[03_OpenFOAM_Architecture|สถาปัตยกรรมระบบทดสอบ OpenFOAM]]
สำรวจไดเรกทอรี `applications/test` และโครงสร้างโค้ดสำหรับการทดสอบฟังก์ชันพื้นฐานใน OpenFOAM