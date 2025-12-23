# ขั้นตอนการทำงานของการจำลอง CFD ใน OpenFOAM

การจำลอง OpenFOAM เป็นไปตามขั้นตอนการทำงานที่เป็นระบบสามขั้นตอน ซึ่งเปลี่ยนคำจำกัดความของปัญหาทางกายภาพให้เป็นผลเฉลยเชิงตัวเลขและข้อมูลเชิงลึกที่นำไปใช้ได้จริง


```mermaid
flowchart TD
    A["Physical Problem"] --> B["Pre-Processing"]
    B --> C["Solving"]
    C --> D["Post-Processing"]
    D --> E["Engineering Insights"]

    B --> B1["Geometry & Mesh"]
    B --> B2["Boundary Conditions"]
    B --> B3["Physical Properties"]
    B --> B4["Solver Parameters"]

    C --> C1["Discretization"]
    C --> C2["Numerical Solution"]
    C --> C3["Convergence Monitoring"]

    D --> D1["Visualization"]
    D --> D2["Data Extraction"]
    D --> D3["Validation"]

    style A fill:#e3f2fd,stroke:#1565c0,stroke-width:3px,color:#000
    style B fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000
    style C fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000
    style D fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000
    style E fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000
```

---

## 1. ขั้นตอน Pre-Processing

### การวางรากฐานทางคณิตศาสตร์และเรขาคณิต

ขั้นตอน Pre-processing เป็นการสร้างรากฐานสำหรับการจำลอง CFD ประกอบด้วยองค์ประกอบสี่ส่วนที่เชื่อมโยงกัน

#### **1.1 การสร้าง Geometry และ Mesh**

โดเมนการคำนวณถูกสร้างขึ้นโดยใช้ยูทิลิตี `blockMesh` ซึ่งแปลงคำจำกัดความทางเรขาคณิตให้เป็นโครงสร้าง Mesh แบบไม่ต่อเนื่อง


```mermaid
graph LR
    A["Physical Domain"] --> B["blockMesh Utility"]
    B --> C["Structured Mesh"]
    C --> D["Grid Cells"]
    D --> E["Discrete Geometry"]

    C --> F["Cell Centers"]
    C --> G["Cell Faces"]
    C --> H["Boundary Faces"]

    F --> I["Field Variables"]
    G --> J["Flux Calculations"]
    H --> K["Boundary Conditions"]

    I --> L["CFD Equations"]
    J --> L
    K --> L

    classDef process fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    classDef storage fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;

    class A,B,C,D,E,F,G,H,I,J,K,L process;
```


**ความสำคัญของ Mesh:**
- **แสดงถึง**: พื้นที่ทางกายภาพที่สมการควบคุมจะถูกแก้ไข
- **ผลกระทบ**: คุณภาพ Mesh ส่งผลโดยตรงต่อความแม่นยำของผลเฉลยและลักษณะการลู่เข้า

> [!INFO] **Block-based Meshing**
> OpenFOAM ใช้วิธี Block-based Method ซึ่งแบ่งรูปทรงเรขาคณิตที่ซับซ้อนออกเป็น Hexahedral Blocks ที่เรียบง่าย แต่ละ Block ถูกกำหนดโดย 8 Vertices และเต็มไปด้วยเซลล์ที่มีการไล่ระดับ

**OpenFOAM Code Implementation: blockMeshDict**
```cpp
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                             |
| \      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \    /   O peration     | Version:  v2012                                 |
|   \  /    A nd           | Web:      www.OpenFOAM.com                      |
|    \/     M anipulation  |                                             |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

convertToMeters 0.1; // Scale factor: converts all dimensions to meters

vertices
(
    (0 0 0)   // 0 - Lower-left-back corner
    (1 0 0)   // 1 - Lower-right-back corner
    (1 1 0)   // 2 - Upper-right-back corner
    (0 1 0)   // 3 - Upper-left-back corner
    (0 0 0.1) // 4 - Lower-left-front corner (z-direction thickness)
    (1 0 0.1) // 5 - Lower-right-front corner
    (1 1 0.1) // 6 - Upper-right-front corner
    (0 1 0.1) // 7 - Upper-left-front corner
);

blocks
(
    // hex (vertex ordering) (cells_x cells_y cells_z) grading ratios
    hex (0 1 2 3 4 5 6 7) (20 20 1) simpleGrading (1 1 1)
);

boundary
(
    movingWall
    {
        type wall;
        faces
        (
            (3 7 6 2)                // Top face (y = 1) - moving lid
        );
    }
    fixedWalls
    {
        type wall;
        faces
        (
            (0 4 7 3)                // Left wall (x = 0)
            (1 5 4 0)                // Bottom wall (y = 0)
            (2 6 5 1)                // Right wall (x = 1)
        );
    }
    frontAndBack
    {
        type empty;                  // Special boundary for 2D simulations
        faces
        (
            (0 1 2 3)                // Back face (z = 0)
            (4 5 6 7)                // Front face (z = 0.1)
        );
    }
);

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
```

**การดำเนินการ:** รันคำสั่งสร้าง Mesh
```bash
blockMesh
```

#### **1.2 การกำหนด Boundary Condition**

ไฟล์ Boundary Condition ในไดเรกทอรี `0/` จะกำหนดข้อจำกัดทางกายภาพที่ขอบเขตของโดเมน:

| Boundary Type | คำอธิบาย | การใช้งานทั่วไป |
|---------------|------------|------------------|
| Velocity Inlets | กำหนดความเร็วที่ช่องเข้า | Inlet flows, ducts |
| Pressure Outlets | กำหนดความดันที่ช่องออก | Exit conditions |
| Wall Conditions | กำหนดเงื่อนไขผนัง | No-slip, isothermal |
| Symmetry Planes | กำหนดเงื่อนไขสมมาตร | Symmetric domains |

**OpenFOAM Code Implementation: ฟิลด์ความเร็ว (0/U)**
```cpp
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                             |
| \      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \    /   O peration     | Version:  v2012                                 |
|   \  /    A nd           | Web:      www.OpenFOAM.com                      |
|    \/     M anipulation  |                                             |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       volVectorField;     // Volume vector field
    object      U;                  // Velocity field
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 1 -1 0 0 0 0];  // m/s (LT^(-1))

internalField   uniform (0 0 0);    // Initial velocity: fluid at rest

boundaryField
{
    movingWall
    {
        type            fixedValue;          // Dirichlet condition
        value           uniform (1 0 0);    // Lid velocity: U = 1 m/s in x-direction
    }

    fixedWalls
    {
        type            noSlip;             // No-slip condition (U = 0 at walls)
    }

    frontAndBack
    {
        type            empty;              // 2D simulation constraint
    }
}

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
```

**OpenFOAM Code Implementation: ฟิลด์ความดัน (0/p)**
```cpp
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                             |
| \      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \    /   O peration     | Version:  v2012                                 |
|   \  /    A nd           | Web:      www.OpenFOAM.com                      |
|    \/     M manupulation  |                                             |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;     // Volume scalar field
    object      p;                  // Pressure field
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 2 -2 0 0 0 0];  // m^2/s^2 (L^2 T^(-2)) - kinematic pressure

internalField   uniform 0;          // Initial gauge pressure

boundaryField
{
    movingWall
    {
        type            zeroGradient;       // Neumann condition: ∂p/∂n = 0
    }

    fixedWalls
    {
        type            zeroGradient;       // Walls don't prescribe pressure
    }

    frontAndBack
    {
        type            empty;              // 2D simulation constraint
    }
}

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
```

> [!TIP] **Kinematic Pressure**
> ใน OpenFOAM สำหรับการไหลแบบ Incompressible ความดันที่ใช้คือ ==Kinematic pressure== ($p/\rho$) ซึ่งมีหน่วย $\text{m}^2/\text{s}^2$ แทนที่จะเป็น Pa ($\text{kg}/(\text{m} \cdot \text{s}^2)$)

#### **1.3 การกำหนดค่าคุณสมบัติทางกายภาพ**

ไดเรกทอรี `constant/` ประกอบด้วยคุณสมบัติของวัสดุและคำจำกัดความของ Physical Model:

**OpenFOAM Code Implementation: transportProperties**
```cpp
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                             |
| \      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \    /   O peration     | Version:  v2012                                 |
|   \  /    A nd           | Web:      www.OpenFOAM.com                      |
|    \/     M anipulation  |                                             |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      transportProperties;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

transportModel  Newtonian;          // Newtonian fluid model

nu              [0 2 -1 0 0 0 0] 0.01;  // Kinematic viscosity ν = 0.01 m^2/s

// Reynolds number calculation:
// Re = UL/ν = (1 m/s × 0.1 m) / 0.01 m^2/s = 10
// This gives a low Reynolds number flow in the laminar regime

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
```

**คุณสมบัติทางกายภาพหลัก:**
- **ความหนาแน่นของของไหล**: $\rho$ (kg/m³)
- **ความหนืด**: $\mu$ (Pa·s) และ $\nu$ (m²/s)
- **ค่าการนำความร้อน**: $k$ (W/m·K)
- **พารามิเตอร์ Turbulence Model**: k, ε, ω เป็นต้น

#### **1.4 พารามิเตอร์ควบคุม Solver**

ไดเรกทอรี `system/` เป็นที่เก็บไฟล์การกำหนดค่า Solver ที่ควบคุมด้านตัวเลข:

| พารามิเตอร์ | สัญลักษณ์ | หน่วย | ผลกระทบ |
|--------------|------------|--------|-----------|
| Time Step | $\Delta t$ | s | เสถียรภาพและความแม่นยำ |
| เกณฑ์การลู่เข้า | - | - | ความเร็วในการคำนวณ |
| Discretization Schemes | - | - | ความแม่นยำเชิงตัวเลข |
| Linear Solver Tolerance | - | - | ความแม่นยำของผลเฉลย |

**OpenFOAM Code Implementation: controlDict**
```cpp
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                             |
| \      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \    /   O peration     | Version:  v2012                                 |
|   \  /    A nd           | Web:      www.OpenFOAM.com                      |
|    \/     M anipulation  |                                             |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      controlDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

application     icoFoam;            // Solver name

startFrom       startTime;          // Start simulation from specified time
startTime       0;                  // Begin at t = 0
stopAt          endTime;            // Stop when reaching end time
endTime         0.5;                // Final simulation time (seconds)
deltaT          0.005;              // Time step size: Δt = 0.005 s

// Output control parameters
writeControl    timeStep;           // Write based on time step count
writeInterval   20;                 // Write every 20 time steps
purgeWrite      0;                  // Keep all time directories
runTimeModifiable true;             // Allow runtime modification

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
```

**OpenFOAM Code Implementation: fvSchemes**
```cpp
ddtSchemes
{
    default         Euler;          // First-order temporal discretization
}

gradSchemes
{
    default         Gauss linear;   // Linear gradient reconstruction
}

divSchemes
{
    default         none;
    div(phi,U)      Gauss linear;   // Convection scheme
}

laplacianSchemes
{
    default         Gauss linear corrected;  // Diffusion scheme with non-orthogonal correction
}
```

**OpenFOAM Code Implementation: fvSolution**
```cpp
solvers
{
    p
    {
        solver          GAMG;              // Geometric-Algebraic Multi-Grid
        tolerance       1e-06;
        relTol          0;
        smoother        GaussSeidel;
    }

    U
    {
        solver          smoothSolver;
        smoother        GaussSeidel;
        tolerance       1e-05;
        relTol          0;
    }
}

PISO
{
    nCorrectors      2;                 // Number of pressure correction loops
    nNonOrthogonalCorrectors 0;
    pRefCell        0;                  // Reference cell for pressure
    pRefValue       0;                  // Reference pressure value
}
```

---

## 2. ขั้นตอน Solving

### การดำเนินการแก้ไขเชิงตัวเลข

Solver เฉพาะทางจะใช้การ Discretization แบบ Finite Volume ของสมการ Navier-Stokes

#### **2.1 สมการควบคุม**

**สมการพื้นฐานของการไหลแบบ Incompressible:**

$$\rho \frac{\partial \mathbf{u}}{\partial t} + \rho (\mathbf{u} \cdot \nabla) \mathbf{u} = -\nabla p + \mu \nabla^2 \mathbf{u} + \mathbf{f} \tag{2.1}$$

$$\nabla \cdot \mathbf{u} = 0 \tag{2.2}$$

**การกำหนดตัวแปร:**
- $\mathbf{u}$ = Velocity vector (m/s)
- $p$ = Pressure (Pa)
- $\rho$ = Density (kg/m³)
- $\mu$ = Dynamic viscosity (Pa·s)
- $\mathbf{f}$ = Body force (N/m³)

ในรูปแบบ Component สำหรับการไหล 2 มิติ:

**แกน x:**
$$\rho \left(\frac{\partial u}{\partial t} + u \frac{\partial u}{\partial x} + v \frac{\partial u}{\partial y}\right) = -\frac{\partial p}{\partial x} + \mu \left(\frac{\partial^2 u}{\partial x^2} + \frac{\partial^2 u}{\partial y^2}\right) \tag{2.3}$$

**แกน y:**
$$\rho \left(\frac{\partial v}{\partial t} + u \frac{\partial v}{\partial x} + v \frac{\partial v}{\partial y}\right) = -\frac{\partial p}{\partial y} + \mu \left(\frac{\partial^2 v}{\partial x^2} + \frac{\partial^2 v}{\partial y^2}\right) \tag{2.4}$$

#### **2.2 การ Discretization ด้วย Finite Volume Method**

OpenFOAM ใช้ Finite Volume Method (FVM) สำหรับการ Discretization:

$$\int_{V_P} \frac{\partial \phi}{\partial t} \, \mathrm{d}V + \int_{V_P} \nabla \cdot \mathbf{F} \, \mathrm{d}V = \int_{V_P} S_\phi \, \mathrm{d}V \tag{2.5}$$

**การนิยามตัวแปร:**
- $\phi$ = ตัวแปรที่ต้องการแก้สมการ (field variable)
- $V_P$ = Volume ของเซลล์ P
- $\mathbf{F}$ = Flux vector
- $S_\phi$ = Source term

**OpenFOAM Code Implementation: การ Discretization ใน Solver**
```cpp
// ตัวอย่างการ Discretization ใน OpenFOAM
fvVectorMatrix UEqn
(
    fvm::ddt(rho, U)                    // Temporal term: ∂(ρU)/∂t
  + fvm::div(rhoPhi, U)                 // Convection: ∇·(ρUU)
  + fvm::SuSp(-fvc::div(rhoPhi), U)     // Explicit source treatment
 ==
    - fvc::grad(p)                      // Pressure gradient: -∇p
  + fvc::laplacian(mu, U)               // Viscous diffusion: μ∇²U
  + fvOptions(rho, U)                   // Additional source terms
);
```

#### **2.3 อัลกอริทึม PISO**

OpenFOAM ใช้ PISO Algorithm (Pressure Implicit with Splitting of Operators) สำหรับการจัดการ Pressure-Velocity Coupling:


```mermaid
graph TD
    A["Start Time Step"] --> B["Predict Velocity<br/>U* from previous time step"]
    B --> C["Solve Momentum Equation<br/>∇·(ρU*U*) = -∇p* + μ∇²U*"]
    C --> D["Pressure Correction<br/>p' = pnew - p*"]
    D --> E["Solve Pressure Equation<br/>∇²p' = ρ/Δt ∇·U*"]
    E --> F["Correct Velocity<br/>U = U* - Δt/ρ ∇p'"]
    F --> G["Update Pressure<br/>p = p* + p'"]
    G --> H{"PISO Corrections<br/>Complete?"}
    H -->|No| I["Additional Correction<br/>nCorrectors = 2"]
    I --> E
    H -->|Yes| J["Advance to Next Time Step"]
    J --> K{"Simulation End?"}
    K -->|No| A
    K -->|Yes| L["End Simulation"]

    classDef process fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    classDef decision fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    classDef terminator fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
    classDef storage fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;

    class A,L terminator;
    class B,C,D,F,G,I process;
    class E,J storage;
    class H,K decision;
```


**ขั้นตอนการทำงานของ PISO Algorithm:**
1. **Predict Velocity** - แก้สมการโมเมนตัมโดยใช้ความดันจาก time step ก่อนหน้า
2. **Pressure Correction** - แก้สมการความดันเพื่อให้เกิดความต่อเนื่อง
3. **Velocity Correction** - แก้ไขความเร็วตามความดันที่แก้ไขแล้ว
4. **Repeat** - ทำขั้นตอนที่ 2-3 จนกว่าจะลู่เข้า
5. **Advance Time** - ไปยัง time step ถัดไป

### การตรวจสอบการลู่เข้า

ความคืบหน้าของผลเฉลยจะถูกติดตามผ่านการตรวจสอบ Residual

**Algorithm: การตรวจสอบการลู่เข้า**
```
เริ่มต้น Time Step
    สำหรับแต่ละสมการ:
        แก้สมการเชิงตัวเลข
        คำนวณ Residual
        ถ้า Residual < tolerance:
            การแก้ลู่เข้าแล้ว
        อื่น ๆ:
            ทำซ้ำ iteration
    จบการแก้สมการ
ตรวจสอบความเสถียรระดับโลการิทึม
```

**OpenFOAM Log Analysis:**
```
Time = 0.1
DILUPBiCG: Solving for Ux, initial residual = 0.0012, final residual = 1.2e-05, no iterations = 3
DILUPBiCG: Solving for Uy, initial residual = 0.0008, final residual = 8.1e-06, no iterations = 2
GAMG: Solving for p, initial residual = 0.05, final residual = 2.1e-04, no iterations = 12
```

> [!WARNING] **การตรวจสอบการลู่เข้า**
> ==Residuals== ควรลดลงต่ำกว่า $10^{-6}$ สำหรับสมการทั้งหมด หาก Residuals ไม่ลู่เข้า อาจต้อง:
> - ลด Time step size ($\Delta t$)
> - ตรวจสอบคุณภาพ Mesh
> - ปรับ Tolerance ของ Linear Solver

---

## 3. ขั้นตอน Post-Processing

### การแสดงผลและการวิเคราะห์

การทำงานร่วมกับ ParaView ช่วยให้สามารถแสดงผล Flow Fields ได้อย่างครอบคลุม

**ปริมาณที่น่าสนใจ:**
- **Velocity Vectors**: $\mathbf{u}$ (m/s)
- **Pressure Contours**: $p$ (Pa)
- **Vorticity**: $\omega = \nabla \times \mathbf{u}$ (1/s)
- **Wall Shear Stress**: $\tau_w$ (Pa)

**การเปิด ParaView:**
```bash
paraFoam -builtin
```

> [!TIP] **การใช้งาน ParaView**
- ใช้ ==Clip== สำหรับตัดระนาบ
- ใช้ ==Stream Tracer== สำหรับแสดง Streamlines
- ใช้ ==Contour== สำหรับแสดง Iso-surfaces
- ใช้ ==Calculator== สำหรับคำนวณปริมาณใหม่

### การดึงข้อมูลเชิงปริมาณ

ยูทิลิตี `sample` และ `probes` จะดึงข้อมูลเชิงตัวเลข

**OpenFOAM Code Implementation: probes function object**
```cpp
probes
{
    type            probes;
    fields          (p U k epsilon);
    probeLocations  ((0 0.1 0) (0.5 0.1 0));
    writeFields     true;
}
```

**OpenFOAM Code Implementation: sampling along a line**
```cpp
sets
(
    horizontalLine
    {
        type            uniform;
        axis            xy;           // 2D line in xy-plane
        start           (0 0.05 0.005);  // Starting point
        end             (0.1 0.05 0.005); // Ending point
        nPoints         100;          // Number of sampling points
    }
);
```

**Algorithm: การดึงข้อมูลตามแนวเส้น**
```
สร้างเส้นที่ต้องการวิเคราะห์
    กำหนดจุดเริ่มต้นและสิ้นสุด
    กำหนดจำนวนจุดตัดอ้างอิง
สำหรับแต่ละ Field ที่สนใจ:
    แทรกค่าจาก Mesh ไปยังเส้น
    บันทึกข้อมูลเป็นไฟล์ CSV
วิเคราะห์ Velocity Profiles และ Pressure Distributions
```

### การตรวจสอบความถูกต้องและการยืนยัน

Post-Processing รวมถึงการเปรียบเทียบกับข้อมูลอ้างอิง

**Grid Independence Study:**
```cpp
// การตรวจสอบความอิสระของ Mesh
สำหรับแต่ละขนาด Mesh:
    สร้าง Mesh (coarse, medium, fine)
    ทำการจำลอง
    วิเคราะห์ปริมาณสำคัญ (drag, pressure drop)
    ตรวจสอบการเปลี่ยนแปลง < 1%
```

**เกณฑ์ Grid Independence:**
$$\frac{|\phi_{\text{fine}} - \phi_{\text{coarse}}|}{|\phi_{\text{fine}}|} < 0.02 \tag{3.1}$$

**การนิยามตัวแปร:**
- $\phi_{\text{fine}}$ = ค่าจาก Mesh ละเอียด
- $\phi_{\text{coarse}}$ = ค่าจาก Mesh หยาบ
- $\phi$ = ปริมาณที่สนใจ (ตำแหน่งจุดศูนย์กลางกระแสวน, ความเร็วสูงสุด)

**Validation Framework:**
- **Analytical Solutions**: กรณีที่มีผลเฉลยที่ทราบแน่นอน
- **Experimental Data**: ข้อมูลจากการทดลองในห้องปฏิบัติการ
- **Benchmark Cases**: กรณีมาตรฐานที่ได้รับการยอมรับ

> [!INFO] **Ghia et al. (1982) Benchmark**
> สำหรับ Lid-driven cavity problem ข้อมูลอ้างอิงจาก Ghia et al. (1982) ถือเป็นมาตรฐานสำหรับการตรวจสอบความถูกต้องของ CFD Solvers โดยเฉพาะสำหรับค่า Reynolds Number ต่างๆ

### การตรวจสอบคุณภาพ Mesh

**Mesh Quality Metrics:**

**Non-orthogonality Angle:**
$$\theta_{\text{max}} = \cos^{-1}\left(\frac{\mathbf{n} \cdot \mathbf{d}}{|\mathbf{n}||\mathbf{d}|}\right) \tag{3.2}$$

**การนิยามตัวแปร:**
- $\mathbf{n}$ = Normal vector ของ face
- $\mathbf{d}$ = Vector จาก cell center ของ owner ถึง neighbor

**Mesh Quality Guidelines:**
| เกณฑ์ | ค่าที่ดี | ค่าที่ยอมรับได้ | ค่าที่ไม่ดี |
|--------|------------|-------------------|---------------|
| Non-orthogonality | $\theta < 30^\circ$ | $30^\circ < \theta < 70^\circ$ | $\theta > 70^\circ$ |
| Aspect Ratio | $< 5$ | $5 - 20$ | $> 20$ |
| Skewness | $< 0.5$ | $0.5 - 0.8$ | $> 0.8$ |

---

## สรุปกรอบการทำงาน

กรอบการทำงานของ Workflow นี้เป็นรากฐานที่แข็งแกร่งสำหรับการวิเคราะห์ CFD ซึ่งช่วยให้สามารถสำรวจปัญหาพลศาสตร์ของไหลได้อย่างเป็นระบบ ตั้งแต่การไหลแบบ Laminar Flow อย่างง่าย ไปจนถึงปรากฏการณ์ Multiphase ที่ซับซ้อนพร้อมการถ่ายเทความร้อนและปฏิกิริยาเคมี


```mermaid
graph LR
    A["Pre-Processing"] --> B["Solving"]
    B --> C["Post-Processing"]
    C --> D["Validation"]
    D --> E["Engineering Decisions"]

    A --> A1["Mesh Generation"]
    A --> A2["Boundary Conditions"]
    A --> A3["Physical Properties"]

    B --> B1["FVM Discretization"]
    B --> B2["PISO Algorithm"]
    B --> B3["Convergence Check"]

    C --> C1["ParaView Visualization"]
    C --> C2["Data Extraction"]
    C --> C3["Quantitative Analysis"]

    D --> D1["Grid Independence"]
    D --> D2["Benchmark Comparison"]
    D --> D3["Experimental Validation"]

    style A fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000
    style B fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000
    style C fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000
    style D fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
    style E fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000
```


### หลักการสำคัญของ Workflow:

1. **Pre-Processing**: การสร้างรากฐานที่แม่นยำเป็นกุญแจสำคัญต่อความสำเร็จ
2. **Solving**: การเข้าใจ Discretization และ Algorithms ช่วยในการแก้ปัญหา
3. **Post-Processing**: การวิเคราะห์อย่างละเอียดเป็นสิ่งจำเป็นต่อการนำผลไปใช้
4. **Validation**: การตรวจสอบความถูกต้องเป็นสิ่งสำคัญต่อความน่าเชื่อถือ

> [!SUCCESS] **ความสำเร็จของการจำลอง CFD**
> การจำลอง CFD ที่ประสบความสำเร็จไม่ได้หมายความเพียงแค่ได้ผลลัพธ์ แต่คือ ==การได้ผลลัพธ์ที่ถูกต้อง== เชื่อถือได้ และ ==สามารถนำไปใช้ในการตัดสินใจทางวิศวกรรม== ได้อย่างมั่นใจ
