# 05. Practical Usage & Case Studies

## Overview

การจำลองของไหลแบบ Non-Newtonian ใน OpenFOAM ต้องการการกำหนดค่าที่เหมาะสมของ ==transport properties==, ==boundary conditions==, และ ==solver settings== เพื่อให้ได้ผลลัพธ์ที่แม่นยำและเสถียร

---

## 1. Transport Properties Configuration

ไฟล์ `constant/transportProperties` เป็นหัวใจสำคัญของการจำลอง Non-Newtonian fluids ซึ่งกำหนดโมเดลความหนืดและพารามิเตอร์ที่เกี่ยวข้อง

### 1.1 Basic Structure

```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      transportProperties;
}

// Select viscosity transport model
transportModel  HerschelBulkley;  // Options: BirdCarreau, powerLaw, CrossPowerLaw

// Kinematic viscosity [m²/s] - base reference value
nu              [0 2 -1 0 0 0 0] 1e-06;
```

> **📂 Source:** Standard OpenFOAM transportProperties dictionary structure
> 
> **💡 Explanation:**
> - ไฟล์นี้เป็น dictionary file มาตรฐานของ OpenFOAM ที่ใช้กำหนดคุณสมบัติทางกายภาพของของไหล
> - `transportModel` ระบุชื่อของโมเดลความหนืดที่ต้องการใช้งาน
> - `nu` เป็นค่าความหนืดอ้างอิง (kinematic viscosity) ที่มีหน่วย [m²/s]
>
> **🔑 Key Concepts:**
> - **Dimension Set:** `[0 2 -1 0 0 0 0]` แทนหน่วย [L²/T] ในระบบหน่วยฐานของ OpenFOAM (Mass, Length, Time, Temperature, etc.)
> - **Dictionary Class:** รูปแบบไฟล์ข้อมูลที่ OpenFOAM ใช้เก็บการตั้งค่าพารามิเตอร์ต่างๆ
> - **Transport Model:** ชื่อ class ของโมเดลความหนืดที่ถูก implement ใน OpenFOAM

### 1.2 Model-Specific Coefficients

#### Herschel-Bulkley Model

```cpp
HerschelBulkleyCoeffs
{
    // Zero-shear viscosity limit [m²/s]
    nu0         [0 2 -1 0 0 0 0] 1e-02;
    
    // Yield stress parameter [Pa·s/m³ or m²/s²]
    tau0        [0 2 -2 0 0 0 0] 5.0;
    
    // Consistency index [m²/s^n]
    k           [0 2 -1 0 0 0 0] 0.1;
    
    // Flow behavior index (dimensionless)
    n           [0 0 0 0 0 0 0] 0.5;
}
```

**Mathematical Model:**

$$
\mu = \min\left(\nu_0, \frac{\tau_0}{\dot{\gamma}} + k\dot{\gamma}^{n-1}\right)
$$

โดยที่:
- $\tau_0$ คือความเค้นจุดยอด (Yield Stress)
- $k$ คือดัชนีความสม่ำเสมอ (Consistency Index)
- $n$ คือดัชนีพฤติกรรมการไหล (Flow Behavior Index)

> **📂 Source:** `src/transportModels/viscosityModels/viscosityModel/HerschelBulkley/`
> 
> **💡 Explanation:**
> - Herschel-Bulkley โมเดลเป็นโมเดลที่รวมคุณสมบัติ yield stress และ power-law behavior เข้าด้วยกัน
> - พารามิเตอร์ `nu0` ใช้จำกัดค่าความหนืดไม่ให้เกินค่าที่กำหนด
> - ค่า `tau0` เป็น yield stress parameter ที่กำหนดแรงเฉือนขั้นต่ำที่ต้องใช้ก่อนของไหลจะเริ่มไหล
>
> **🔑 Key Concepts:**
> - **Yield Stress Fluids:** ของไหลที่ต้องการความเค้นเฉือนขั้นต่ำก่อนเริ่มไหล (เช่น ซอสมะเขือเปียก, ยาสีฝุ่น)
> - **Shear-Thinning:** เมื่อ n < 1 ความหนืดจะลดลงเมื่ออัตราการเฉือนเพิ่มขึ้น
> - **Shear-Thickening:** เมื่อ n > 1 ความหนืดจะเพิ่มขึ้นเมื่ออัตราการเฉือนเพิ่มขึ้น
> - **Viscosity Clipping:** ฟังก์ชัน `min()` ใช้ป้องกันความหนืดไม่ให้เกินค่าสูงสุดที่กำหนด

#### Bird-Carreau Model

```cpp
BirdCarreauCoeffs
{
    // Zero-shear viscosity [m²/s]
    nu0         [0 2 -1 0 0 0 0] 1.0;
    
    // Infinite-shear viscosity [m²/s]
    nuInf       [0 2 -1 0 0 0 0] 0.0;
    
    // Time constant [s]
    k           [0 0 1 0 0 0 0] 0.1;
    
    // Power law index (dimensionless)
    n           [0 0 0 0 0 0 0] 0.5;
    
    // Yasuda parameter (dimensionless)
    a           [0 0 0 0 0 0 0] 2.0;
}
```

**Mathematical Model:**

$$
\mu = \mu_{\infty} + (\mu_0 - \mu_{\infty})\left[1 + (k\dot{\gamma})^a\right]^{\frac{n-1}{a}}
$$

> **📂 Source:** `src/transportModels/viscosityModels/viscosityModel/BirdCarreau/`
> 
> **💡 Explanation:**
> - Bird-Carreau โมเดลเหมาะสำหรับของไหลที่มีความหนืดเปลี่ยนแปลงอย่างต่อเนื่องตลอดช่วงความเร็วเฉือน
> - พารามิเตอร์ `a` (Yasuda parameter) ควบคุมความกว้างของช่วงการเปลี่ยนแปลง
> - โมเดลนี้มักใช้สำหรับการจำลองการไหลของเลือดและโพลีเมอร์หลายชนิด
>
> **🔑 Key Concepts:**
> - **Zero-Shear Viscosity:** ค่าความหนืดเมื่อของไหลอยู่ในสภาพนิ่ง (ขีดจำกัดเมื่อ shear rate → 0)
> - **Infinite-Shear Viscosity:** ค่าความหนืดเมื่ออัตราการเฉือนสูงมาก (ขีดจำกัดเมื่อ shear rate → ∞)
> - **Transition Region:** ช่วงที่ความหนืดเปลี่ยนจาก nu0 ไปเป็น nuInf
> - **Carreau-Yasuda Model:** สมการทั่วไปที่รวมพารามิเตอร์ a เพื่อความยืดหยุ่นในการเทียบกับข้อมูลทดลอง

#### Power Law Model

```cpp
powerLawCoeffs
{
    // Maximum viscosity limit [m²/s]
    nuMax       [0 2 -1 0 0 0 0] 1.0;
    
    // Minimum viscosity limit [m²/s]
    nuMin       [0 2 -1 0 0 0 0] 0.0;
    
    // Consistency index [m²/s^(2-n)]
    k           [0 2 -1 0 0 0 0] 0.1;
    
    // Power law index (dimensionless)
    n           [0 0 0 0 0 0 0] 0.5;
}
```

**Mathematical Model:**

$$
\mu = \min\left(\mu_{\max}, \max\left(\mu_{\min}, k\dot{\gamma}^{n-1}\right)\right)
$$

> **📂 Source:** `src/transportModels/viscosityModels/viscosityModel/powerLaw/`
> 
> **💡 Explanation:**
> - Power Law โมเดลเป็นโมเดลที่เรียบง่ายที่สุดสำหรับของไหล non-Newtonian
> - ใช้ฟังก์ชัน clipping ทั้งสองด้าน (max/min) เพื่อป้องกันค่าที่ไม่เป็นทางกายภาพ
> - เหมาะสำหรับการจำลองเบื้องต้นและการศึกษาเชิงทฤษฎี
>
> **🔑 Key Concepts:**
> - **Ostwald-de Waele Model:** ชื่อทางวิชาการของ Power Law model
> - **Clipping Strategy:** การจำกัดค่าความหนืดให้อยู่ในช่วงที่กำหนดเพื่อเสถียรภาพทางตัวเลข
> - **Power Law Region:** ช่วงที่สมการ power law ใช้ได้โดยไม่ต้อง clipping
> - **Limitations:** ไม่สามารถจำลอง yield stress หรือ plateau regions ได้

> [!TIP] Dimensional Consistency
> ตรวจสอบให้แน่ใจว่าหน่วยของพารามิเตอร์ทั้งหมดถูกต้อง โดยเฉพาะ:
> - $\tau_0$ มีหน่วย [Pa·s/m³] หรือ [0 2 -2 0 0 0 0] ใน OpenFOAM
> - $k$ ใน Power Law มีหน่วยที่ขึ้นกับค่า $n$

---

## 2. Boundary Conditions

### 2.1 Velocity Boundary Conditions

#### Standard Conditions (0/U)

```cpp
// Velocity field dimensions [m/s]
dimensions      [0 1 -1 0 0 0 0];

// Initial velocity field inside domain
internalField   uniform (0 0 0);

boundaryField
{
    // Inlet boundary - fixed velocity
    inlet
    {
        type            fixedValue;
        value           uniform (1 0 0);  // Flow in x-direction
    }

    // Wall boundaries - no-slip condition
    walls
    {
        type            noSlip;  // Alternative: partialSlip for wall slip
    }

    // Outlet boundary - zero gradient
    outlet
    {
        type            zeroGradient;
    }
}
```

> **📂 Source:** `etc/templates/pozFoam/cavity/0/U.org` (Reference template)
> 
> **💡 Explanation:**
> - `dimensions` กำหนดหน่วยของสนามความเร็ว [L/T]
> - `internalField` เป็นค่าเริ่มต้นของความเร็วภายในโดเมนที่เวลา t = 0
> - `boundaryField` กำหนดเงื่อนไขขอบเขตสำหรับแต่ละ patch ที่กำหนดไว้ใน mesh
>
> **🔑 Key Concepts:**
> - **Dirichlet BC (fixedValue):** กำหนดค่าโดยตรงที่ขอบเขต
> - **Neumann BC (zeroGradient):** กำหนดค่า gradient เป็นศูนย์ (อนุญาตให้ค่าเปลี่ยนไปตามการคำนวณภายใน)
> - **No-Slip Condition:** ความเร็วของของไหลที่ผนังเป็นศูนย์ (สภาพติดขอบ)
> - **Patch Naming:** ชื่อของ boundary ต้องตรงกับที่กำหนดใน `constant/polyMesh/boundary`

#### Wall Slip Conditions

สำหรับของไหลบางชนิด (เลือด, โพลีเมอร์) อาจเกิดการลื่นไถลที่ผนัง:

```cpp
walls
{
    type            partialSlip;
    value           uniform 0;
    slipFraction    0.1;    // 0 = no-slip, 1 = full-slip
}
```

**Mathematical Formulation:**

$$
\mathbf{u}_t = \beta \cdot \frac{\mathbf{t}}{\mu} \cdot \tau
$$

โดยที่:
- $\beta$ คือส่วนแบ่งการลื่นไถล (slip fraction)
- $\mathbf{t}$ คือทิศทางสัมผัส
- $\tau$ คือความเค้นเฉือนที่ผนัง

> **📂 Source:** `src/finiteVolume/fields/fvPatchFields/constraints/partialSlip/`
> 
> **💡 Explanation:**
> - `partialSlip` BC เหมาะสำหรับของไหลที่มีการลื่นไถลที่ผนัง (wall slip phenomenon)
> - `slipFraction` ค่า 0 หมายถึงไม่มีการลื่น (no-slip) และค่า 1 หมายถึงลื่นสมบูรณ์ (free-slip)
> - ใช้บ่อยในการจำลองการไหลของเลือดในหลอดเลือดขนาดเล็กและโพลีเมอร์
>
> **🔑 Key Concepts:**
> - **Navier Slip Condition:** แบบจำลองที่อนุญาตให้มีความเร็วจำลอง proportional กับความเค้นเฉือน
> - **Slip Length:** ระยะห่างสมมติที่ผนังซึ่งความเร็วเชิงเส้น extrapolate จะเป็นศูนย์
> - **Wall Depletion:** ปรากฏการณ์ที่อนุภาคขนาดใหญ่ถูกขับออกจากผนัง ทำให้เกิดการลื่น

### 2.2 Viscosity Field (0/nu)

```cpp
// Kinematic viscosity dimensions [m²/s]
dimensions      [0 2 -1 0 0 0 0];

// Initial viscosity field
internalField   uniform 1e-06;

boundaryField
{
    inlet
    {
        // Calculated from transport model
        type            calculated;
        value           uniform 1e-06;
    }

    walls
    {
        // Zero gradient - computed from velocity gradient
        type            zeroGradient;
    }

    outlet
    {
        type            zeroGradient;
    }
}
```

> **📂 Source:** Standard OpenFOAM viscosity field initialization
> 
> **💡 Explanation:**
> - `calculated` BC ใช้ที่ inlet เพื่อให้โมเดลความหนืดคำนวณค่าได้โดยอัตโนมัติ
> - `zeroGradient` ที่ผนังหมายความว่าความหนืดถูกคำนวณจาก gradient ของความเร็ว
> - ค่าความหนืดจะถูกอัปเดตในทุก time step ตามสมการโมเดลที่เลือก
>
> **🔑 Key Concepts:**
> - **Calculated BC:** Boundary condition ที่ค่าถูกคำนวณจาก solver หรือ model อื่น
> - **Coupled Fields:** ความหนืดและความเร็วมีความสัมพันธ์กันผ่าน strain rate
> - **Non-Linear Coupling:** ความหนืดขึ้นกับ strain rate ซึ่งขึ้นกับ gradient ของความเร็ว

> [!WARNING] Viscosity Clipping
> ในบริเวณ high-gradient (มุมแหลม, ขยายกะทันหัน) ความหนืดอาจลดต่ำเกินไป:
> - ใช้ `nuMin` และ `nuMax` ใน transportProperties
> - เพิ่ม mesh refinement ในบริเวณเหล่านั้น
> - ใช้ under-relaxation สำหรับ viscosity field

---

## 3. Solver Selection & Configuration

### 3.1 Recommended Solvers

| Solver | Flow Type | Application | Notes |
|--------|-----------|-------------|-------|
| **simpleFoam** | Steady-state, incompressible | General industrial flows | Fast convergence |
| **pimpleFoam** | Transient, incompressible | Complex time-dependent flows | Higher accuracy |
| **nonNewtonianIcoFoam** | Transient, laminar | Educational purposes | Specialized |
| **interFoam** | Multiphase | Injection molding, food processing | Supports non-Newtonian |

> **📂 Source:** `applications/solvers/incompressible/` directory structure
> 
> **💡 Explanation:**
> - **simpleFoam:** ใช้อัลกอริทึม SIMPLE (Semi-Implicit Method for Pressure-Linked Equations) สำหรับ steady-state
> - **pimpleFoam:** ผสม PISO และ SIMPLE สำหรับ transient flow ที่มีความเสถียรสูง
> - **nonNewtonianIcoFoam:** เขียนขึ้นเพื่อการศึกษา ใช้อัลกอริทึม PISO สำหรับ laminar flow
>
> **🔑 Key Concepts:**
> - **SIMPLE Algorithm:** ใช้ under-relaxation เพื่อให้ลู่เข้าใน steady-state
> - **PISO Algorithm:** แก้สมการ pressure-velocity coupling ใน transient ด้วย correctors หลายรอบ
> - **PIMPLE Algorithm:** ผสม SIMPLE และ PISO เพื่อความยืดหยุ่นใน large time step
> - **Laminar vs Turbulent:** nonNewtonianIcoFoam ออกแบบสำหรับ laminar flow เท่านั้น

### 3.2 fvSchemes Configuration

```cpp
ddtSchemes
{
    // First-order Euler scheme for transient term
    default         Euler;  // Alternative: backward for higher accuracy
}

gradSchemes
{
    // Central differencing for gradient calculation
    default         Gauss linear;
    grad(nu)        Gauss linear;  // Important for viscosity gradient
}

divSchemes
{
    default         none;
    // Upwind scheme for convection term stability
    div(phi,U)      Gauss upwind grad(U);
}

laplacianSchemes
{
    // Linear correction for non-orthogonal meshes
    default         Gauss linear corrected;
}
```

> **📂 Source:** Reference: `.applications/test/fieldMapping/pipe1D/system/fvSchemes`
> 
> **💡 Explanation:**
> - `ddtSchemes` คือการ discretize พจน์ temporal derivative (∂/∂t)
> - `gradSchemes` คำนวณ gradient ด้วย Gauss theorem และ interpolation
> - `divSchemes` ใช้ upwind เพื่อเสถียรภาพเนื่องจาก convection-dominated flows
> - `laplacianSchemes` ใช้ `corrected` เพื่อรองรับ non-orthogonal meshes
>
> **🔑 Key Concepts:**
> - **Temporal Discretization:** Euler (first-order) vs backward (second-order)
> - **Spatial Discretization:** Gauss integration กับ interpolation schemes ต่างๆ
> - **Upwind Scheme:** ใช้ค่าจาก upstream direction ป้องกัน oscillations
> - **Non-Orthogonal Correction:** ปรับปรุงค่าบน meshes ที่ไม่ orthogonal
> - **Numerical Diffusion:** Upwind schemes เพิ่ม numerical diffusion แต่เสถียรกว่า central differencing

### 3.3 fvSolution Configuration

```cpp
solvers
{
    p
    {
        // Geometric-Algebraic Multi-Grid solver for pressure
        solver          GAMG;
        tolerance       1e-06;
        relTol          0.01;
    }

    pFinal
    {
        // Tighter tolerance for final corrector
        solver          GAMG;
        tolerance       1e-06;
        relTol          0;
    }

    U
    {
        // Iterative solver for velocity
        solver          smoothSolver;
        smoother        GaussSeidel;
        tolerance       1e-05;
        relTol          0.1;
    }
}

PIMPLE
{
    // Number of pressure correctors
    nCorrectors      2;
    // Correctors for non-orthogonal meshes
    nNonOrthogonalCorrectors  1;
}
```

> **📂 Source:** Reference: `.applications/test/fieldMapping/pipe1D/system/fvSolution`
> 
> **💡 Explanation:**
> - **GAMG (Geometric-Algebraic Multi-Grid):** ใช้สำหรับสมการ pressure เพราะมีประสิทธิภาพสูงสำหรับ large systems
> - **smoothSolver:** ใช้สำหรับ velocity ด้วย Gauss-Seidel smoothing
> - **nCorrectors:** จำนวนรอบการแก้ไข pressure-velocity coupling
> - **pFinal:** ใช้ tolerance ที่เข้มงวดกว่าในรอบสุดท้าย
>
> **🔑 Key Concepts:**
> - **Linear Solvers:** เลือก solver ที่เหมาะกับลักษณะของสมการ (symmetric, asymmetric)
> - **Absolute vs Relative Tolerance:** `tolerance` คือค่าสัมบูรณ์ `relTol` คือค่าสัมพัทธ์
> - **Multi-Grid Methods:** ลดการลู่เข้าโดยใช้ coarse grid correction
> - **PIMPLE Parameters:** ควบคุมความถี่ในการแก้ pressure-velocity coupling
> - **Non-Orthogonal Correctors:** จำเป็นสำหรับ meshes ที่มีความ non-orthogonality สูง

> [!INFO] Relaxation Factors
> สำหรับการจำลอง Non-Newtonian:
> ```cpp
> relaxationFactors
> {
>     fields
>     {
>         p               0.3;
>         U               0.7;
>         nu              0.5;  // Critical for stability
>     }
> }
> ```
> 
> **💡 Explanation:**
> - `p` (pressure) ใช้ค่าต่ำเพื่อความเสถียรของ coupling
> - `U` (velocity) ใช้ค่าปานกลางเพื่อสมดุลระหว่างความเร็วและเสถียรภาพ
> - `nu` (viscosity) ใช้ค่า 0.5 เพื่อลด coupling ที่รุนแรงระหว่างความหนืดและความเร็ว

---

## 4. Complete Workflow

```mermaid
flowchart TD
    A[Pre-processing] --> B[Mesh Generation]
    B --> C[Set Initial Conditions]
    C --> D[Configure transportProperties]
    D --> E[Set Boundary Conditions]
    E --> F[Configure fvSchemes/fvSolution]
    F --> G{Run Simulation}
    G --> H{Monitor Convergence}
    H -- No --> I[Adjust Relaxation/nuMax]
    I --> G
    H -- Yes --> J[Post-processing]

    style D fill:#ffc,stroke:#333
    style I fill:#f99,stroke:#333
    style J fill:#cfc,stroke:#333
```
> **Figure 1:** แผนผังลำดับขั้นตอนการจำลองของไหลที่ไม่ใช่แบบนิวตัน (Complete Workflow) ตั้งแต่การเตรียมเมช การตั้งค่าพารามิเตอร์ของแบบจำลองความหนืด ไปจนถึงกระบวนการวิเคราะห์ผลและการตรวจสอบความลู่เข้า

> **📂 Source:** Standard OpenFOAM CFD workflow methodology
> 
> **💡 Explanation:**
> - **Pre-processing:** ขั้นตอนเตรียมความพร้อม包括 mesh generation และ parameter setup
> - **transportProperties Configuration:** ขั้นตอนสำคัญที่สุดสำหรับ non-Newtonian flows
> - **Convergence Monitoring:** ต้องติดตามทั้ง residuals และ viscosity field
> - **Iterative Adjustment:** การจำลอง non-Newtonian มักต้องมีการปรับพารามิเตอร์หลายครั้ง
>
> **🔑 Key Concepts:**
> - **Pre-processing Phase:** Mesh generation, boundary definition, initial conditions
> - **Configuration Phase:** การตั้งค่า transport model, numerical schemes, solver parameters
> - **Solution Phase:** การคำนวณและการติดตาม convergence
> - **Post-processing Phase:** การวิเคราะห์ผลลัพธ์และ validation
> - **Iterative Process:** การจำลองที่ซับซ้อนมักต้องกลับไปปรับค่าหลายรอบ

### 4.1 Pre-processing Checklist

- [ ] Verify mesh quality (aspect ratio, skewness)
- [ ] Set appropriate boundary layer resolution
- [ ] Validate model parameters (literature/experiment)
- [ ] Check dimensional consistency in transportProperties
- [ ] Configure appropriate time step (CFL condition)

> **📂 Source:** OpenFOAM mesh quality and best practice guidelines
> 
> **💡 Explanation:**
> - **Mesh Quality:** ตรวจสอบ aspect ratio (< 1000), skewness (< 0.85), non-orthogonality (< 70°)
> - **Boundary Layer:** ต้องการ mesh ละเอียดพอใกล้ผนังสำหรับ high gradient regions
> - **Parameter Validation:** ใช้ค่าจาก literature หรือทดลองเพื่อความถูกต้องทางกายภาพ
> - **Dimensional Check:** OpenFOAM จะตรวจสอบ consistency แต่ควรตรวจอีกครั้งด้วยตนเอง
> - **CFL Condition:** Courant number ควร < 1 สำหรับ explicit schemes
>
> **🔑 Key Concepts:**
> - **Mesh Quality Metrics:** aspect ratio, skewness, orthogonality, concavity
> - **y+ Value:** ระยะห่างของ cell แรกจากผนังเทียบกับ viscous length scale
> - **Dimensional Homogeneity:** ทุกพจน์ในสมการต้องมีหน่วยเหมือนกัน
> - **CFL (Courant-Friedrichs-Lewy):** เกณฑ์เสถียรภาพสำหรับ temporal discretization
> - **Grid Independence:** ผลลัพธ์ไม่ควรขึ้นกับขนาด mesh

### 4.2 Best Practice Workflow

```mermaid
flowchart LR
    A[Start] --> B[Run with Newtonian]
    B --> C[Check Velocity Field]
    C --> D[Switch to Non-Newtonian]
    D --> E[Monitor Viscosity Field]
    E --> F{Converged?}
    F -- No --> G[Adjust Parameters]
    G --> E
    F -- Yes --> H[Validate Results]

    style B fill:#e8f5e9,stroke:#2e7d32
    style D fill:#fff9c4,stroke:#fbc02d
    style H fill:#c8e6c9,stroke:#2e7d32
```
> **Figure 2:** แผนผังแสดงแนวทางปฏิบัติที่เป็นเลิศ (Best Practice) โดยใช้ลำดับการคำนวณจากแบบจำลองนิวตันไปสู่แบบจำลองที่ไม่ใช่แบบนิวตัน เพื่อรักษาเสถียรภาพทางตัวเลขและลดความซับซ้อนในการตั้งค่าเบื้องต้น

> **📂 Source:** Recommended progressive modeling approach for non-Newtonian CFD
> 
> **💡 Explanation:**
> - **Newtonian Baseline:** เริ่มจาก simple case เพื่อ validate mesh และ boundary conditions
> - **Gradual Complexity:** เพิ่มความซับซ้อนทีละน้อยเพื่อให้ติดตามปัญหาได้ง่าย
> - **Viscosity Monitoring:** สำคัญมากเพราะ non-Newtonian fluids มีความหนืดเปลี่ยนแบบ non-linear
> - **Iterative Tuning:** การปรับ parameters เป็นกระบวนการปกติ
>
> **🔑 Key Concepts:**
> - **Bottom-Up Approach:** เริ่มจาก simple model แล้วค่อยเพิ่มความซับซ้อน
> - **Validation Hierarchy:** ตรวจสอบทีละระดับตั้งแต่ mesh → BCs → transport model
> - **Parameter Sensitivity:** ผลกระทบของการเปลี่ยนค่า parameters ต่อ convergence
> - **Robustness First:** ตั้งค่าให้เสถียรก่อน ค่อยปรับให้แม่นยำภายหลัง
> - **Debugging Strategy:** แยกแยะปัญหาจาก mesh, numerical schemes, หรือ physical model

---

## 5. Practical Case Studies

### 5.1 Blood Flow in Artery

**Model:** Bird-Carreau

```cpp
transportModel  BirdCarreau;

BirdCarreauCoeffs
{
    // Blood viscosity at rest [m²/s]
    nu0         0.056;
    
    // Blood viscosity at high shear [m²/s]
    nuInf       0.0035;
    
    // Time constant [s]
    k           3.313;
    
    // Power law index (shear-thinning)
    n           0.3568;
    
    // Yasuda parameter
    a           2.0;
}
```

**Key Considerations:**
- ใช้ `pulsatileVelocity` inlet boundary condition
- เพิ่ม mesh refinement ใกล้ผนังหลอดเลือด
- วิเคราะห์ wall shear stress สำหรับการแพทย์

> **📂 Source:** Biomedical flow modeling literature (Carreau et al., 1979)
> 
> **💡 Explanation:**
> - **Blood Rheology:** เลือดเป็น shear-thinning fluid ที่มีความหนืดสูงเมื่อนิ่งและลดลงเมื่อ shear rate เพิ่ม
> - **Fähraeus-Lindqvist Effect:** ความหนืดลดลงในหลอดเลือดขนาดเล็ก
> - **Pulsatile Flow:** การไหลแบบถี่เนื่องจากการเต้นของหัวใจ
>
> **🔑 Key Concepts:**
> - **Hemodynamics:** การศึกษาการไหลของเลือดและความสัมพันธ์กับระบบไหลเวียน
> - **Wall Shear Stress (WSS):** ความเค้นเฉือนที่ผนังหลอดเลือด สำคัญต่อความเสียหายของเยื่อบุ
> - **Oscillatory Shear Index (OSI):** ดัชนีวัดการเปลี่ยนทิศทางของ WSS
> - **Yield Stress Behavior:** เลือดมีคุณสมบัติเป็น yield stress fluid ในบางสภาพ

### 5.2 Polymer Extrusion

**Model:** Power Law

```cpp
transportModel  powerLaw;

powerLawCoeffs
{
    // Maximum viscosity limit [m²/s]
    nuMax       1000;
    
    // Minimum viscosity limit [m²/s]
    nuMin       0.1;
    
    // Consistency index [m²/s^(2-n)]
    k           5000;
    
    // Power law index (shear-thinning)
    n           0.4;
}
```

**Key Considerations:**
- ใช้ `inletOutlet` สำหรับ outlet
- ตรวจสอบ die swell ที่ outlet
- วิเคราะห์ pressure drop ผ่าน die

> **📂 Source:** Polymer processing literature (Bird et al., 1987)
> 
> **💡 Explanation:**
> - **Polymer Rheology:** โพลีเมอร์ส่วนใหญ่เป็น shear-thinning fluids
> - **Die Swell:** ปรากฏการณ์ที่ jet ขยายตัวหลังออกจาก die เนื่องจาก elastic recovery
> - **Pressure Drop:** สำคัญในการออกแบบ extrusion dies
>
> **🔑 Key Concepts:**
> - **Viscoelasticity:** โพลีเมอร์มีทั้ง viscous และ elastic behavior
> - **Shear-Thinning Index (n):** ค่า n < 1 บ่งบอกความสามารถในการลดความหนืด
> - **Entrance Effects:** การพัฒนา flow จาก entrance ไปจนถึง fully developed
> - **Melt Flow Index:** ค่าที่ใช้ในอุตสาหกรรมวัดความง่ายในการไหล
> - **Processing Window:** ช่วงของ temperature และ shear rate ที่เหมาะสม

### 5.3 Food Processing (Tomato Sauce)

**Model:** Herschel-Bulkley

```cpp
transportModel  HerschelBulkley;

HerschelBulkleyCoeffs
{
    // Zero-shear viscosity limit [m²/s]
    nu0         1000;
    
    // Yield stress [Pa·s/m³]
    tau0        50;
    
    // Consistency index [m²/s^n]
    k           10;
    
    // Flow behavior index
    n           0.5;
}
```

**Key Considerations:**
- ระบุ yielded/unyielded zones
- ใช้ `partialSlip` ที่ผนัง
- วิเคราะห์ mixing efficiency

> **📂 Source:** Food rheology literature (Steffe, 1996)
> 
> **💡 Explanation:**
> - **Yield Stress Foods:** ซอสมะเขือเปียก, มะขาม, ช็อกโกแลตหลอม มี yield stress
> - **Yielded vs Unyielded:** บริเวณที่ stress < yield stress จะเคลื่อนที่เป็น solid plug
> - **Wall Slip:** ปรากฏการณ์การลื่นของ particles ตามผนัง
>
> **🔑 Key Concepts:**
> - **Plug Flow:** บริเวณที่ของไหลเคลื่อนที่เป็น chunk เดียว (solid-like)
> - **Yield Surface:** พื้นที่แบ่งระหว่าง yielded และ unyielded zones
> - **Apparent Viscosity:** ความหนืดที่คำนวณจาก stress/shear rate ratio
> - **Thixotropy:** ความสามารถในการลดความหนืดตามเวลา (time-dependent)
> - **Rheometry:** การวัดคุณสมบัติทาง rheological ของ foods

---

## 6. Troubleshooting Guide

### 6.1 Common Issues

| Issue | Symptom | Solution |
|-------|---------|----------|
| **Divergence** | Residuals explode | Reduce time step, increase relaxation |
| **Unphysical viscosity** | Viscosity → 0 or ∞ | Add nuMin/nuMax clipping |
| **Slow convergence** | Residuals plateau | Improve mesh quality, adjust schemes |
| **Oscillations** | Fields wobble | Increase under-relaxation |

> **📂 Source:** OpenFOAM debugging and stability best practices
> 
> **💡 Explanation:**
> - **Divergence:** เกิดจาก time step ใหญ่เกินไป หรือ coupling ระหว่าง fields รุนแรงเกินไป
> - **Unphysical Viscosity:** ความหนืดที่คำนวณได้มีค่าผิดพลาดเนื่องจาก numerical errors
> - **Slow Convergence:** มักเกิดจาก mesh quality ไม่ดี หรือ schemes ไม่เหมาะสม
> - **Oscillations:** การสั่นของ fields เกิดจาก under-relaxation ต่ำเกินไป
>
> **🔑 Key Concepts:**
> - **Numerical Stability:** ความสามารถของ algorithm ในการลู่เข้าโดยไม่ explode
> - **CFL Condition:** เกณฑ์ความเสถียรสำหรับ explicit schemes
> - **Residual Monitoring:** การติดตามค่าความคลาดเคลื่อนของสมการ
> - **Relaxation Factors:** ค่าที่ลดการเปลี่ยนแปลงของ fields เพื่อเสถียรภาพ
> - **Mesh Independence:** ผลลัพธ์ไม่ควรขึ้นกับ mesh resolution

### 6.2 Expert Tips

#### Tip 1: Start Simple

```mermaid
flowchart LR
    A[Newtonian Model] --> B[Validate Mesh & BCs]
    B --> C[Switch to Power Law]
    C --> D[Validate Results]
    D --> E[Apply Complex Model]
```
> **Figure 3:** แผนภูมิแสดงกลยุทธ์การเพิ่มระดับความซับซ้อนของแบบจำลองความหนืด (Progressive Modeling Strategy) เพื่อการตรวจสอบความถูกต้องของระบบอย่างเป็นลำดับ

> **📂 Source:** Recommended CFD pedagogical approach
> 
> **💡 Explanation:**
> - **Foundation First:** ต้องมั่นใจว่าพื้นฐาน (mesh, BCs) ถูกต้องก่อนเพิ่มความซับซ้อน
> - **Incremental Complexity:** เพิ่ม physical models ทีละน้อยเพื่อให้ติดตามปัญหาได้
> - **Validation at Each Step:** ตรวจสอบผลลัพธ์ก่อน move ต่อ
>
> **🔑 Key Concepts:**
> - **Modular Validation:** แยก validation ของแต่ละ component
> - **Isolation of Variables:** เปลี่ยนแค่ parameter เดียวต่อครั้ง
> - **Physical Consistency:** ผลลัพธ์ต้องสอดคล้องกับ physics
> - **Computational Efficiency:** ลดเวลา debugging โดยเริ่มจาก simple case
> - **Building Intuition:** เข้าใจพฤติกรรมของ models แบบ gradual

#### Tip 2: Monitor Strain Rate

ใน ParaView, สร้างฟิลด์ strain rate จาก `grad(U)`:

```python
# Python Calculator in ParaView
strainRate = sqrt(2*mag(symm(Gradient(U))))
```

ตรวจสอบว่า:
- ไม่มีค่าสูงผิดปกติในบริเวณมุม
- ช่วงของค่าเหมาะสมกับโมเดล

> **📂 Source:** OpenFOAM post-processing best practices
> 
> **💡 Explanation:**
> - **Strain Rate Tensor:** สมมาตรส่วนของ velocity gradient tensor
> - **Magnitude:** ใช้ค่า scalar เพื่อการ visualise ง่าย
> - **Hot Spots:** บริเวณที่มี strain rate สูงผิดปกติอาจเป็นปัญหา mesh
>
> **🔑 Key Concepts:**
> - **Strain Rate Tensor:** $\dot{\gamma}_{ij} = \frac{1}{2}(\frac{\partial u_i}{\partial x_j} + \frac{\partial u_j}{\partial x_i})$
> - **Shear Rate Magnitude:** $\dot{\gamma} = \sqrt{2\mathbf{D}:\mathbf{D}}$ โดย $\mathbf{D}$ คือ rate-of-strain tensor
> - **Visualization Techniques:** ใช้ color maps และ iso-surfaces
> - **Model Applicability:** แต่ละโมเดลมีช่วง shear rate ที่เหมาะสม
> - **Numerical Artifacts:** ค่าสูงผิดปกติอาจเป็นผลจาก poor mesh quality

#### Tip 3: Validate with Analytical Solutions

สำหรับ **Poiseuille Flow in Pipe**:

$$
v_z(r) = \frac{n}{n+1}\left(\frac{\Delta p}{L} \frac{1}{2k}\right)^{1/n} \left(R^{(n+1)/n} - r^{(n+1)/n}\right)
$$

เปรียบเทียบกับผลการจำลอง

> **📂 Source:** Classical fluid mechanics analytical solutions (Bird et al.)
> 
> **💡 Explanation:**
> - **Poiseuille Flow:** การไหลในท่อกลมที่ fully developed
> - **Analytical Solution:** มี solution แน่นอนสำหรับ power law fluids
> - **Validation Method:** เปรียบเทียบ velocity profile จาก CFD กับ analytical
>
> **🔑 Key Concepts:**
> - **Analytical Solutions:** ทางการแก้ปัญหาที่ได้จากสมการโดยตรง
> - **Benchmark Cases:** กรณีศึกษามาตรฐานสำหรับ validation
> - **Error Metrics:** ใช้ RMS error, maximum deviation
> - **Grid Convergence:** ตรวจสอบว่า mesh ละเอียดพอ
> - **Code Verification:** ตรวจสอบว่า solver ทำงานถูกต้อง

---

## 7. Advanced Techniques

### 7.1 Viscosity Regularization

สำหรับ Herschel-Bulkley, ใช้ Papanastasiou regularization:

$$
\mu_{\text{eff}} = \mu_0 + \left(1 - e^{-m\dot{\gamma}}\right)\frac{\tau_0}{\dot{\gamma}} + k\dot{\gamma}^{n-1}
$$

โดยที่ $m$ เป็น regularization parameter (100-1000)

> **📂 Source:** Papanastasiou (1987) regularization of yield stress fluids
> 
> **💡 Explanation:**
> - **Singularity Problem:** สมการ Herschel-Bulkley มี singularity ที่ $\dot{\gamma} \rightarrow 0$
> - **Regularization:** แทนที่ singularity ด้วย exponential function ที่ smooth
> - **Parameter m:** ควบคุมความเร็วในการ transition จาก yield behavior
>
> **🔑 Key Concepts:**
> - **Yield Stress Singularity:** ปัญหาที่ความหนืด → ∞ เมื่อ shear rate → 0
> - **Regularization Methods:** ใช้ฟังก์ชัน smooth แทนที่ฟังก์ชันเดิม
> - **Papanastasiou Regularization:** ใช้ exponential function ในการปรับปรุง
> - **Numerical Stability:** regularization เพิ่มความเสถียรในการคำนวณ
> - **Physical Accuracy:** ต้อง balance ระหว่างความเสถียรและความแม่นยำ

### 7.2 Adaptive Time Stepping

```cpp
// Enable automatic time step adjustment
adjustTimeStep  yes;

// Maximum Courant number for stability
maxCo           0.5;

// Maximum time step allowed [s]
maxDeltaT       1.0;
```

> **📂 Source:** OpenFOAM time control documentation
> 
> **💡 Explanation:**
> - **Adaptive Time Stepping:** solver ปรับ time step อัตโนมัติตาม local CFL
> - **Courant Number:** ใช้เป็นเกณฑ์ในการปรับ time step
> - **Efficiency vs Accuracy:** balance ระหว่าง computational cost และ accuracy
>
> **🔑 Key Concepts:**
> - **CFL (Courant-Friedrichs-Lewy) Number:** $Co = \frac{u \Delta t}{\Delta x}$
> - **Local CFL:** คำนวณจาก cell แต่ละ cell ไม่ใช่ค่าเฉลี่ย
> - **Stability Criterion:** explicit schemes ต้องการ Co < 1
> - **Adaptive Algorithms:** ปรับ Δt เพื่อ maintain Co ในช่วงที่กำหนด
> - **Computational Efficiency:** ลดจำนวน time steps โดยรักษา stability

### 7.3 Parallel Computing

```bash
# Decompose case for parallel processing
decomposePar

# Run in parallel using 4 processors
mpirun -np 4 nonNewtonianIcoFoam -parallel

# Reconstruct parallel results
reconstructPar
```

> **📂 Source:** OpenFOAM parallel computing methodology
> 
> **💡 Explanation:**
> - **Domain Decomposition:** แบ่ง mesh เป็น subdomains สำหรับ parallel processing
> - **MPI (Message Passing Interface):** library สำหรับ parallel computation
> - **Load Balancing:** แบ่ง workload ระหว่าง processors อย่างสมดุล
>
> **🔑 Key Concepts:**
> - **Decomposition Methods:** scotch, simple, hierarchical, manual
> - **Processor Count:** ปรับสัดส่วนตาม mesh size และ hardware
> - **Communication Overhead:** ค่าใช้จ่ายในการส่งข้อมูลระหว่าง processors
> - **Speedup & Efficiency:** วัดประสิทธิภาพของ parallelization
> - **Scalability:** ความสามารถในการขยายไปยัง processors จำนวนมาก

---

## 8. Summary Checklist

> [!CHECKLIST] Pre-Simulation
> - [ ] Mesh quality verified
> - [ ] Model parameters validated
> - [ ] Boundary conditions set correctly
> - [ ] Dimensional consistency checked
> - [ ] Solver settings configured

> **📂 Source:** OpenFOAM pre-processing best practices
> 
> **💡 Explanation:**
> - **Mesh Quality:** ตรวจสอบ aspect ratio, skewness, non-orthogonality
> - **Parameter Validation:** ใช้ค่าจาก literature หรือ experiments
> - **Boundary Conditions:** ตรวจสอบว่า BCs สอดคล้องกับ physics
> - **Dimensional Consistency:** ตรวจสอบหน่วยของทุก parameters
> - **Solver Configuration:** ตั้งค่า schemes, solvers, relaxation factors

> [!CHECKLIST] During Simulation
> - [ ] Monitor residuals
> - [ ] Check viscosity field bounds
> - [ ] Verify mass conservation
> - [ ] Track convergence rate

> **📂 Source:** OpenFOAM runtime monitoring guidelines
> 
> **💡 Explanation:**
> - **Residual Monitoring:** ติดตามค่าความคลาดเคลื่อนของสมการทุก time step
> - **Viscosity Bounds:** ตรวจสอบว่าความหนืดอยู่ในช่วงที่กำหนด
> - **Mass Conservation:** ตรวจสอบว่า mass balance ถูกต้อง
> - **Convergence Rate:** ติดตามความเร็วในการลู่เข้าของ solution

> [!CHECKLIST] Post-Simulation
> - [ ] Validate with experimental data
> - [ ] Check mesh independence
> - [ ] Analyze key parameters (WSS, pressure drop)
> - [ ] Document results and settings

> **📂 Source:** OpenFOAM post-processing and validation procedures
> 
> **💡 Explanation:**
> - **Experimental Validation:** เปรียบเทียบผลกับข้อมูลทดลอง
> - **Mesh Independence:** ตรวจสอบว่าผลไม่ขึ้นกับ mesh resolution
> - **Parameter Analysis:** วิเคราะห์ค่าที่สำคัญ (WSS, pressure drop, velocity profiles)
> - **Documentation:** บันทึก settings และผลลัพธ์อย่างละเอียด

---

## 9. Further Reading

- [[00_Overview]] - ภาพรวม Non-Newtonian Fluids
- [[02_2._Blueprint_The_Viscosity-Model_Hierarchy]] - สถาปัตยกรรมโมเดล
- [[05_5._Code_Analysis_of_Three_Key_Models]] - วิเคราะห์โค้ดโมเดลหลัก
- OpenFOAM User Guide - Chapter 6: Physical Models
- OpenFOAM Wiki - nonNewtonianIcoFoam Tutorial