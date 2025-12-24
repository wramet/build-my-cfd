# การควบคุมและการจัดการการจำลอง (Simulation Control and Management)

การรันการจำลองที่ประสบความสำเร็จใน OpenFOAM ไม่ได้ขึ้นอยู่กับ Solver ที่เลือกเท่านั้น แต่ยังรวมถึงการตั้งค่าพารามิเตอร์เชิงตัวเลขและการตรวจสอบการลู่เข้าอย่างเป็นระบบ

---

## 🏗️ 1. โครงสร้าง Directory ของ Case

Case ของ OpenFOAM ต้องมีโครงสร้างที่เป็นมาตรฐานเพื่อให้ Solver เข้าถึงข้อมูลได้ถูกต้อง:

```bash
incompressibleCase/
├── 0/                       # Boundary & Initial Conditions
│   ├── U                   # Velocity [m/s]
│   ├── p                   # Pressure [m²/s²] (สำหรับ incompressible คือ p/rho)
│   └── (k, epsilon, omega)  # Turbulence quantities
├── constant/                # Physical & Mesh Data
│   ├── polyMesh/           # Mesh topology
│   ├── transportProperties # nu (kinematic viscosity)
│   └── turbulenceProperties # Turbulence model selection
└── system/                  # Numerical Control
    ├── controlDict         # Time/Output control
    ├── fvSchemes           # Discretization schemes
    └── fvSolution          # Solver settings & algorithms
```

> [!INFO] ความสำคัญของโครงสร้าง Directory
> โครงสร้างนี้เป็นมาตรฐานที่ OpenFOAM ใช้เพื่อระบุตำแหน่งของข้อมูลทั้งหมดที่จำเป็นสำหรับการจำลอง การจัดระเบียบที่ถูกต้องช่วยให้ Solver ทำงานได้อย่างมีประสิทธิภาพ

---

## ⚙️ 2. การควบคุมหลัก (`system/controlDict`)

ไฟล์ `controlDict` ทำหน้าที่กำหนดช่วงเวลาการคำนวณและความถี่ในการเขียนไฟล์ผลลัพธ์:

### 2.1 การตั้งค่าพื้นฐาน

```cpp
application     simpleFoam;          // Solver to be used
startFrom       startTime;           // Start from initial time
startTime       0;                   // Initial time value
stopAt          endTime;             // Stop at specified end time
endTime         1000;                // Final time value
deltaT          1;                   // Time step size

writeControl    timeStep;            // Write output based on time steps
writeInterval   100;                 // Write every 100 time steps
purgeWrite      3;                   // Keep only the 3 most recent results
runTimeModifiable true;              // Allow modification while running
```

**คำอธิบาย:**
- **📂 Source:** ไฟล์ `system/controlDict` ในทุกๆ OpenFOAM case
- **การอธิบาย:** ไฟล์ controlDict คือไฟล์หลักในการควบคุมการทำงานของ Solver กำหนดเวลาเริ่มต้น เวลาสิ้นสุด ขนาดของ Time step และความถี่ในการบันทึกผลลัพธ์
- **แนวคิดสำคัญ:** 
  - `application`: ระบุ Solver ที่จะใช้ (simpleFoam, pimpleFoam, etc.)
  - `deltaT`: ขนาด Time step ส่งผลต่อความเสถียรและความแม่นยำ
  - `purgeWrite`: ช่วยประหยัดพื้นที่ดิสก์โดยเก็บเฉพาะผลลัพธ์ล่าสุด
  - `runTimeModifiable`: อนุญาตให้แก้ไขค่าขณะรันโดยไม่ต้องหยุด Solver

### 2.2 การตั้งค่า Time Stepping สำหรับ Transient Flow

สำหรับการจำลองแบบ Transient การเลือก **Time step** ที่เหมาะสมเป็นสิ่งสำคัญ:

```cpp
application     pimpleFoam;          // Transient solver
startFrom       latestTime;          // Continue from last time
startTime       0;                   // Initial time
stopAt          endTime;             // Stop condition
endTime         10.0;                // Final simulation time

deltaT          0.001;               // Initial time step size
adjustTimeStep  yes;                 // Enable automatic time step adjustment
maxCo           1.0;                 // Maximum Courant number
maxDeltaT       0.01;                // Maximum time step allowed
```

**คำอธิบาย:**
- **📂 Source:** ไฟล์ `system/controlDict` สำหรับ Transient simulations
- **การอธิบาย:** การตั้งค่า Time stepping แบบ Adaptive ที่ปรับขนาด Time step อัตโนมัติตามค่า Courant number เพื่อรักษาความเสถียรของการคำนวณ
- **แนวคิดสำคัญ:**
  - `adjustTimeStep`: เปิดใช้งานการปรับ Time step อัตโนมัติ
  - `maxCo`: ค่า Courant number สูงสุดที่ยอมรับได้ (ควร ≤ 1)
  - ระบบจะลด `deltaT` อัตโนมัติหาก Co เกินค่าที่กำหนด

**เงื่อนไข CFL (Courant-Friedrichs-Lewy):**

สำหรับความเสถียรของการคำนวณ:
$$\text{CFL} = \frac{|\mathbf{u}| \Delta t}{\Delta x} < 1$$

โดยที่:
- $\mathbf{u}$ = ความเร็วของไหล (m/s)
- $\Delta t$ = ขนาด time step (s)
- $\Delta x$ = ขนาดเซลล์ mesh (m)

### 2.3 การตรวจสอบค่าระหว่างรัน (Runtime Monitoring)

```cpp
functions
{
    // Monitor equation residuals during simulation
    residuals
    {
        type            residuals;                         // Residual calculation
        functionObjectLibs ("libutilityFunctionObjects.so");
        fields          (p U k epsilon);                   // Variables to monitor
        writeControl    timeStep;
        writeInterval   1;
    }

    // Monitor forces acting on walls
    forces
    {
        type            forces;                            // Force calculation
        libs            (fieldFunctionObjects);
        patches         (walls);                           // Patches to calculate
        rho             rhoInf;                            // Density type
        rhoInf          1.225;                             // Reference density [kg/m³]
        writeControl    timeStep;
        writeInterval   1;
    }

    // Monitor Courant number field
    CourantNumber
    {
        type            CourantNumber;                     // Co field calculation
        libs            (fieldFunctionObjects);
        writeControl    timeStep;
        writeInterval   1;
    }
}
```

**คำอธิบาย:**
- **📂 Source:** ไฟล์ `system/controlDict` - ส่วน `functions`
- **การอธิบาย:** Function objects ช่วยตรวจสอบค่าต่างๆ ระหว่างการจำลองโดยไม่ต้องหยุด Solver สามารถวิเคราะห์ Residuals, Forces, และ Courant number ได้แบบ Real-time
- **แนวคิดสำคัญ:**
  - `type`: ประเภทของ function object (residuals, forces, CourantNumber)
  - `fields`: ตัวแปรที่ต้องการตรวจสอบ
  - `patches`: พื้นที่ผิวที่คำนวณแรง
  - `rhoInf`: ความหนาแน่นอ้างอิงสำหรับแรง

---

## 🔧 3. การตั้งค่าความละเอียดเชิงตัวเลข (`system/fvSolution`)

### 3.1 Linear Solvers

OpenFOAM แก้ระบบสมการ $Ax=b$ โดยใช้ Linear Solvers ที่แตกต่างกันตามประเภทของสมการ:

```cpp
solvers
{
    p
    {
        solver          GAMG;                              // Geometric-Algebraic Multi-Grid
        tolerance       1e-07;                             // Absolute tolerance
        relTol          0.01;                              // Relative tolerance
        smoother        GaussSeidel;                       // Smoother type
        nPreSweeps      0;                                 // Pre-smoothing iterations
        nPostSweeps     2;                                 // Post-smoothing iterations
        cacheAgglomerator true;                            // Cache agglomeration
    }

    pFinal
    {
        $p;                                               // Inherit from p
        relTol          0;                                 // Zero relative tolerance
    }

    U
    {
        solver          smoothSolver;                      // Smoothed solver
        smoother        GaussSeidel;                       // Smoother algorithm
        tolerance       1e-08;                             // Absolute tolerance
        relTol          0;                                 // Relative tolerance
    }

    "(k|epsilon|omega)"
    {
        solver          PBiCGStab;                         // Stabilized Bi-Conjugate Gradient
        preconditioner  DILU;                              // Diagonal Incomplete LU
        tolerance       1e-06;                             // Absolute tolerance
        relTol          0;                                 // Relative tolerance
    }
}
```

**คำอธิบาย:**
- **📂 Source:** ไฟล์ `.applications/test/patchRegion/cavity_pinched/system/fvSolution`
- **การอธิบาย:** การตั้งค่า Linear solvers กำหนดวิธีการแก้ระบบสมการเชิงเส้นสำหรับแต่ละตัวแปร แต่ละ Solver มีความเหมาะสมกับประเภทสมการที่แตกต่างกัน
- **แนวคิดสำคัญ:**
  - `GAMG`: เหมาะสำหรับสมการ Elliptic (Pressure) เร็วและใช้หน่วยความจำปานกลาง
  - `PBiCGStab`: สำหรับสมการ Non-symmetric (Momentum, Turbulence)
  - `smoothSolver`: สำหรับกรณีที่มีเงื่อนไขไม่ดี ใช้หน่วยความจำน้อย
  - `tolerance`: ค่าความคลาดเคลื่อนสัมบูรณ์
  - `relTol`: ค่าความคลาดเคลื่อนสัมพัทธ์

**การเลือก Linear Solver ที่เหมาะสม:**

| Solver | ประเภทสมการ | ความเร็ว | หน่วยความจำ | การใช้งานที่เหมาะสม |
|--------|----------------|------------|----------------|---------------------|
| **GAMG** | Elliptic (Pressure) | เร็วมาก | ปานกลาง | Pressure equation |
| **PBiCGStab** | Non-symmetric | ปานกลาง | ต่ำ | Momentum, Turbulence |
| **PCG** | Symmetric | ปานกลาง | ต่ำ | Symmetric systems |
| **smoothSolver** | ทั่วไป | ช้ากว่า | ต่ำมาก | กรณีที่มีเงื่อนไขไม่ดี |

### 3.2 Under-Relaxation (สำหรับ SIMPLE)

เพื่อรักษาความเสถียรใน `simpleFoam` จำเป็นต้องใช้ **Relaxation factors**:

$$\phi^{n+1} = \phi^n + \alpha (\phi^{new} - \phi^n)$$

โดยที่ $\alpha$ คือ Under-Relaxation Factor (0 < $\alpha$ ≤ 1)

```cpp
relaxationFactors
{
    fields
    {
        p               0.3;    // Pressure: lower = more stable
    }
    equations
    {
        U               0.7;    // Velocity
        "(k|epsilon|omega)" 0.7; // Turbulence quantities
    }
}
```

**คำอธิบาย:**
- **📂 Source:** ไฟล์ `system/fvSolution` สำหรับ SIMPLE algorithm
- **การอธิบาย:** Under-relaxation ช่วยรักษาความเสถียรของการคำนวณโดยลดการเปลี่ยนแปลงของตัวแปรในแต่ละ Iteration ค่าที่ต่ำกว่า 1 จะทำให้การลู่เข้าช้าลงแต่เสถียรขึ้น
- **แนวคิดสำคัญ:**
  - `p`: ความดันมักต้องการค่าต่ำ (0.2-0.5) เพื่อความเสถียร
  - `U`: ความเร็วใช้ค่าปานกลาง (0.5-0.8)
  - สมการที่ซับซ้อนอาจต้องลดค่า relaxation factors

**ค่าแนะนำสำหรับ Under-Relaxation:**

| ตัวแปร | ช่วงค่า | ผลกระทบของค่าต่ำ | ผลกระทบของค่าสูง |
|---------|-----------|---------------------|---------------------|
| **ความดัน (p)** | 0.2 - 0.5 | เสถียรขึ้น, ช้าลง | ลู่เข้าเร็วขึ้น, อาจ diverge |
| **ความเร็ว (U)** | 0.5 - 0.8 | เสถียรขึ้น, ช้าลง | ลู่เข้าเร็วขึ้น, เสี่ยง oscillation |
| **Turbulence** | 0.5 - 0.8 | เสถียรขึ้น | ลู่เข้าเร็วขึ้น |

### 3.3 การตั้งค่า Algorithm

#### SIMPLE Algorithm (Steady-State)

```cpp
SIMPLE
{
    nNonOrthogonalCorrectors 0;                         // Non-orthogonal correction loops
    nCorrectors      2;                                 // Number of pressure-velocity corrections
    pRefCell         0;                                 // Reference cell for pressure
    pRefValue        0;                                 // Reference pressure value
}
```

**คำอธิบาย:**
- **📂 Source:** ไฟล์ `system/fvSolution` สำหรับ steady-state solvers
- **การอธิบาย:** SIMPLE (Semi-Implicit Method for Pressure-Linked Equations) algorithm ใช้สำหรับการจำลอง Steady-state ด้วยการวนซ้ำเพื่อให้ Pressure และ Velocity ลู่เข้าสู่กันและกัน
- **แนวคิดสำคัญ:**
  - `nCorrectors`: จำนวนรอบการแก้ไข Pressure-velocity coupling
  - `pRefCell`: ระบุ Cell ที่ใช้อ้างอิงความดัน
  - `pRefValue`: ค่าความดันที่ Cell อ้างอิง (กำหนดระดับความดันสัมบูรณ์)

#### PIMPLE Algorithm (Transient ที่มี Time step ขนาดใหญ่)

```cpp
PIMPLE
{
    nCorrectors      2;                                 // Number of outer correctors
    nNonOrthogonalCorrectors 0;                         // Non-orthogonal iterations
    nAlphaCorr       1;                                 // Volume fraction corrections (multiphase)
    nAlphaSubCycles  2;                                 // Sub-cycles for VOF method

    // Convergence control criteria
    residualControl
    {
        p               1e-6;                           // Pressure residual tolerance
        U               1e-6;                           // Velocity residual tolerance
        "(k|epsilon)"   1e-5;                           // Turbulence residual tolerance
    }
}
```

**คำอธิบาย:**
- **📂 Source:** ไฟล์ `system/fvSolution` สำหรับ transient solvers
- **การอธิบาย:** PIMPLE คือการผสมกันของ PISO และ SIMPLE ให้ใช้งานได้ทั้ง Transient และ Steady-state พร้อมการควบคุมการลู่เข้าแบบยืดหยุ่น
- **แนวคิดสำคัญ:**
  - `nCorrectors`: จำนวนรอบการแก้ไขภายใน Time step เดียว
  - `residualControl`: กำหนดเกณฑ์การลู่เข้าสำหรับแต่ละตัวแปร
  - ช่วยให้ใช้ Time step ขนาดใหญ่ได้โดยยังคงความเสถียร

---

## 🔄 4. การตรวจสอบการลู่เข้า (Convergence Monitoring)

### 4.1 Residual Analysis

**Residual** คือตัววัดความไม่สมดุลของสมการเชิงตัวเลข:

$$\text{Residual} = \| \mathbf{A}\mathbf{x} - \mathbf{b} \|$$

โดยที่:
- $\mathbf{A}$ = Coefficient matrix
- $\mathbf{x}$ = Solution vector
- $\mathbf{b}$ = Right-hand side vector

**ประเภทของ Residual:**

1. **Initial Residual**: ค่าก่อนเริ่มแก้ในแต่ละ Iteration
   $$\text{Res}_0 = \| \mathbf{A}x_0 - \mathbf{b} \|$$

2. **Final Residual**: ค่าหลังจาก Solver ทำงานเสร็จในรอบนั้น
   $$\text{Res}_f = \| \mathbf{A}x_n - \mathbf{b} \|$$

3. **Normalized Residual**:
   $$\text{Res}_{norm} = \frac{\text{Res}_f}{\text{Res}_0}$$

**เกณฑ์แนะนำ:**

| ตัวแปร | Initial Residual | Final Residual | ความหมาย |
|---------|------------------|----------------|-------------|
| **ความดัน ($p$)** | - | $10^{-6}$ ถึง $10^{-7}$ | Pressure field ลู่เข้าแล้ว |
| **ความเร็ว ($U$)** | - | $10^{-7}$ ถึง $10^{-8}$ | Velocity field ลู่เข้าแล้ว |
| **Turbulence ($k, \varepsilon$)** | - | $10^{-5}$ ถึง $10^{-6}$ | Turbulence ลู่เข้าแล้ว |

**ตัวอย่าง Log Output:**

```bash
Time = 100

smoothSolver: Solving for Ux, Initial residual = 0.00123, Final residual = 3.45e-06, No Iterations 4
smoothSolver: Solving for Uy, Initial residual = 0.000987, Final residual = 2.76e-06, No Iterations 4
GAMG: Solving for p, Initial residual = 0.0456, Final residual = 1.23e-07, No Iterations 12
time step continuity errors : sum local = 2.34e-05, global = 1.23e-06, cumulative = 2.34e-06
SIMPLE iteration converged
```

**การวิเคราะห์:**
- Residual ลดลงจาก 0.00123 → 3.45e-06 (Ux)
- Residual ลดลงจาก 0.0456 → 1.23e-07 (p)
- Continuity error อยู่ในระดับที่ยอมรับได้

### 4.2 รูปแบบการลู่เข้า

| รูปแบบ | ลักษณะ | การจัดการ |
|---------|---------|-------------|
| **ลดลงอย่างต่อเนื่อง** | Convergence ในอุดมคติ | ดำเนินการต่อ |
| **Convergence แบบแกว่ง** | Amplitude ลดลง | ยอมรับได้หากลดลง |
| **คงที่ (Plateau)** | ค่าต่ำสุดเฉพาะที่ | ปรับพารามิเตอร์ |
| **Divergence** | Residual เพิ่มขึ้น | ต้องแก้ไขทันที |

### 4.3 Physical Quantity Monitoring

นอกเหนือจาก Residual ควรติดตามปริมาณทางกายภาพผ่าน `functions` ใน `controlDict`:

```cpp
functions
{
    // Monitor force coefficients
    forceCoeffs
    {
        type            forceCoeffs;                       // Force coefficient calculation
        libs            (forces);
        patches         (airfoil);                         // Surface patches
        rho             rhoInf;                            // Density type
        rhoInf          1.225;                             // Reference density [kg/m³]
        CofR            (0.25 0 0);                        // Center of rotation
        liftDir         (0 1 0);                           // Lift direction
        dragDir         (1 0 0);                           // Drag direction
        pitchAxis       (0 0 1);                           // Pitch axis
        magUInf         10.0;                              // Freestream velocity [m/s]
        lRef            1.0;                               // Reference length [m]
        Aref            1.0;                               // Reference area [m²]
        writeControl    timeStep;
        writeInterval   1;
    }

    // Monitor mass flow rate
    massFlowRate
    {
        type            surfaceRegion;                      // Surface integration
        libs            (libfieldFunctionObjects.so);
        operation       sum;                               // Sum operation
        regionType      patch;                             // Patch region
        name            inlet;                             // Patch name
        surfaceField    phi;                               // Mass flux field
        writeControl    timeStep;
        writeInterval   1;
    }
}
```

**คำอธิบาย:**
- **📂 Source:** ไฟล์ `system/controlDict` - ส่วน `functions`
- **การอธิบาย:** Function objects สำหรับตรวจสอบปริมาณทางกายภาพเช่น สัมประสิทธิ์แรง (Lift/Drag) และอัตราการไหลของมวล เพื่อยืนยันความถูกต้องทางฟิสิกส์
- **แนวคิดสำคัญ:**
  - `CofR`: จุดศูนย์กลางการหมุนสำหรับการคำนวณ Moment
  - `liftDir`, `dragDir`: ทิศทางของแรงยกและแรงลาก
  - `magUInf`: ความเร็วกระแสอนันต์
  - `lRef`, `Aref`: ความยาวและพื้นที่อ้างอิงสำหรับการทำให้ไร้มิติ

**สูตรการคำนวณปริมาณทางกายภาพ:**

| ปริมาณ | สูตร | การใช้งาน |
|---------|-------|-------------|
| Drag coefficient | $C_D = \frac{F_D}{0.5\rho U^2 A}$ | แรงต้าน |
| Lift coefficient | $C_L = \frac{F_L}{0.5\rho U^2 A}$ | แรงยก |
| Mass flow rate | $\dot{m} = \rho \int \mathbf{u} \cdot \mathbf{n} \, dA$ | การไหลของมวล |
| Pressure drop | $\Delta p = p_{in} - p_{out}$ | การไหล |

### 4.4 เกณฑ์ Convergence ที่ครอบคลุม

**เกณฑ์การตรวจสอบ Convergence ที่ดี:**

1. ✅ **Residual ลดลง** ถึงค่าที่กำหนด (10⁻⁶ ถึง 10⁻⁸)
2. ✅ **ปริมาณทางกายภาพคงที่** (Drag, Lift ไม่เปลี่ยนแปลงมาก)
3. ✅ **สมดุลมวล** (mass balance < 1%)
4. ✅ **Continuity errors** ต่ำ (cumulative < 10⁻⁵)

---

## 🛠️ 5. แนวทางปฏิบัติที่ดีที่สุด (Best Practices)

### 5.1 กลยุทธ์การเริ่มต้น

1. **เริ่มต้นจากสิ่งง่ายๆ**: ใช้ Scheme อันดับหนึ่ง (เช่น `upwind`) ในช่วงแรกเพื่อให้การจำลองเสถียร แล้วจึงเปลี่ยนเป็นอันดับสอง (เช่น `linearUpwind`) เพื่อความแม่นยำ

```cpp
// ใน fvSchemes - เริ่มต้นด้วย first-order
divSchemes
{
    div(phi,U)    Gauss upwind;                          // First-order upwind
    div(phi,k)    Gauss upwind;
    div(phi,epsilon) Gauss upwind;
}

// หลังจากลู่เข้าแล้ว เปลี่ยนเป็น second-order
divSchemes
{
    div(phi,U)    Gauss linearUpwindV grad(U);           // Second-order linear upwind
    div(phi,k)    Gauss linearUpwindV grad(k);
    div(phi,epsilon) Gauss linearUpwindV grad(epsilon);
}
```

**คำอธิบาย:**
- **📂 Source:** ไฟล์ `system/fvSchemes` สำหรับ discretization schemes
- **การอธิบาย:** การเริ่มต้นด้วย First-order schemes ช่วยให้การจำลองเสถียรขึ้น แม้จะมี Numerical diffusion สูงกว่า หลังจากที่การจำลองลู่เข้าแล้วจึงเปลี่ยนเป็น Second-order schemes เพื่อความแม่นยำ
- **แนวคิดสำคัญ:**
  - `upwind`: First-order scheme เสถียรแต่มี Numerical diffusion
  - `linearUpwindV`: Second-order scheme แม่นยำกว่าแต่อาจไม่เสถียรเมื่อเริ่มต้น
  - การเปลี่ยน schemes ต้องระวัง Convergence

### 5.2 การตรวจสอบคุณภาพ Mesh

```bash
# รัน checkMesh เสมอก่อนเริ่มจำลอง
checkMesh -allGeometry -allTopology
```

**เกณฑ์คุณภาพ Mesh:**

| พารามิเตอร์ | ค่าที่ยอมรับได้ | ผลกระทบหากเกิน |
|--------------|-----------------|-------------------|
| **Aspect Ratio** | < 1000 | การลู่เข้าช้า |
| **Non-orthogonality** | < 70° | ความเสถียรลดลง |
| **Skewness** | < 0.5 | ความแม่นยำลดลง |
| **Expansion Ratio** | < 5 | Convergence แย่ลง |

> [!WARNING] คำเตือนเรื่อง Mesh Quality
> หากค่า **Non-orthogonality** > 70° จำเป็นต้องเพิ่ม `nNonOrthogonalCorrectors` ใน `fvSolution`

### 5.3 การตรวจสอบสมดุลมวล

ตรวจสอบค่า `time step continuity errors` ในไฟล์ Log:

```bash
# ค่าที่ดีควรเป็น:
time step continuity errors : sum local = 2.34e-05, global = 1.23e-06, cumulative = 2.34e-06

# cumulative ควรมีค่าน้อยมาก (< 1e-4)
```

### 5.4 การปรับปรุงความเสถียร

**หากเกิด Divergence:**

1. **ลด Under-relaxation factors**
   ```cpp
   relaxationFactors
   {
       fields { p 0.2; }      // ลดจาก 0.3
       equations { U 0.5; }   // ลดจาก 0.7
   }
   ```

2. **เปลี่ยนเป็น First-order schemes**
   ```cpp
   divSchemes
   {
       div(phi,U)    Gauss upwind;  // จาก linearUpwind
   }
   ```

3. **ตรวจสอบ Boundary Conditions**
   - ตรวจสอบความสอดคล้องของ Inlet/Outlet
   - ตรวจสอบการกำหนด Pressure Reference
   - ตรวจสอบความเข้ากันได้ของ Wall Functions

### 5.5 การเพิ่มประสิทธิภาพการคำนวณ

**การใช้งานแบบขนาน (Parallel Processing):**

```bash
# 1. แบ่ง case ออกเป็นส่วนๆ
decomposePar

# 2. รันแบบขนาน
mpirun -np 4 simpleFoam -parallel

# 3. รวมผลลัพธ์
reconstructPar
```

**การปรับแต่ง GAMG Solver:**

```cpp
p
{
    solver          GAMG;                               // Geometric-Algebraic Multi-Grid
    tolerance       1e-07;                              // Absolute tolerance
    relTol          0.01;                               // Relative tolerance
    smoother        GaussSeidel;                        // Smoother algorithm
    nPreSweeps      0;                                  // Pre-smoothing iterations
    nPostSweeps     2;                                  // Post-smoothing iterations
    cacheAgglomerator true;                              // Cache agglomeration for speed
    nCellsInCoarsestLevel 50;                            // Coarsest level cell count
}
```

**คำอธิบาย:**
- **📂 Source:** ไฟล์ `system/fvSolution` สำหรับ GAMG solver optimization
- **การอธิบาย:** การปรับแต่ง GAMG solver สามารถเพิ่มประสิทธิภาพการคำนวณอย่างมาก โดยเฉพาะสำหรับปัญหาขนาดใหญ่ที่มีจำนวนเซลล์มาก
- **แนวคิดสำคัญ:**
  - `cacheAgglomerator`: เก็บข้อมูล agglomeration ไว้ใน cache เพื่อเร่งการคำนวณ
  - `nCellsInCoarsestLevel`: จำนวนเซลล์ในระดับหยาบที่สุด มีผลต่อประสิทธิภาพ
  - ค่าที่เหมาะสมขึ้นกับปัญหาและ Hardware

---

## 📋 6. สรุป Workflow การจำลอง

```mermaid
flowchart TD
    A[เริ่มต้น] --> B[ตรวจสอบ Mesh Quality]
    B --> C{คุณภาพดี?}
    C -->|ไม่| D[ปรับปรุง Mesh]
    D --> B
    C -->|ใช่| E[ตั้งค่า Initial Conditions]
    E --> F[ตั้งค่า Boundary Conditions]
    F --> G[ตั้งค่า controlDict]
    G --> H[ตั้งค่า fvSchemes]
    H --> I[ตั้งค่า fvSolution]
    I --> J[เริ่มต้นรัน Solver]
    J --> K[ตรวจสอบ Residuals]
    K --> L{ลู่เข้า?}
    L -->|ไม่| M[ปรับพารามิเตอร์]
    M --> K
    L -->|ใช่| N[ตรวจสอบ Physical Quantities]
    N --> O{คงที่?}
    O -->|ไม่| M
    O -->|ใช่| P[การจำลองสำเร็จ]
    P --> Q[วิเคราะห์ผลลัพธ์]
```

> **Figure 1:** แผนผังลำดับขั้นตอนการจำลองพลศาสตร์ของไหลเชิงคำนวณ (CFD Simulation Workflow) ใน OpenFOAM ตั้งแต่การตรวจสอบคุณภาพของเมช การตั้งค่าเงื่อนไขต่างๆ ไปจนถึงกระบวนการวนซ้ำเพื่อตรวจสอบความลู่เข้าของทั้งค่า Residual และปริมาณทางกายภาพ เพื่อให้มั่นใจในความถูกต้องและความเสถียรของผลลัพธ์

---

## 🎯 7. สรุปหลักการสำคัญ

### ขั้นตอนการจัดการการจำลองที่มีประสิทธิภาพ:

1. **🏗️ เตรียมโครงสร้าง Case** ให้ถูกต้องตามมาตรฐาน OpenFOAM
2. **⚙️ ตั้งค่า controlDict** สำหรับการควบคุมเวลาและ output
3. **🔧 ตั้งค่า fvSolution** ด้วย Linear solvers และ Algorithm ที่เหมาะสม
4. **🏃 รันการจำลอง** พร้อมตรวจสอบ Convergence อย่างใกล้ชิด
5. **🛠️ แก้ไขปัญหา** ด้วยกลยุทธ์ที่เหมาะสมหากเกิด Divergence
6. **✅ ตรวจสอบผลลัพธ์** ด้วยหลายเกณฑ์ (Residuals + Physical quantities)

### คำแนะนำเชิงปฏิบัติ:

- ✅ เริ่มต้นด้วย **Low-order schemes** เพื่อความเสถียร
- ✅ ใช้ **Under-relaxation** สำหรับปัญหาที่ซับซ้อน
- ✅ ตรวจสอบ **Mesh quality** ก่อนรันเสมอ
- ✅ Monitor **Multiple convergence criteria** ไม่ใช่เพียง Residuals
- ✅ **Document** การเปลี่ยนแปลงและผลลัพธ์
- ✅ ใช้ **Parallel processing** สำหรับ Case ขนาดใหญ่
- ✅ เปิดใช้ **Run-time modifiable** สำหรับการปรับแต่งขณะรัน

---

**จบเนื้อหาโมดูล Incompressible Flow Solvers**