# ภาพรวมการจำลอง CFD ครั้งแรก: Lid-Driven Cavity

> [!INFO] **ภาพรวมโมดูลนี้**
> โมดูลนี้จะแนะนำการจำลอง CFD แรกของคุณใน OpenFOAM โดยใช้ปัญหาคลาสสิก **Lid-Driven Cavity Flow** ซึ่งเป็นกรณีทดสอบมาตรฐานที่เทียบเคียงได้กับ "Hello World" ของ Computational Fluid Dynamics

---

## 1. ปัญหา Lid-Driven Cavity Flow

### 1.1 คำอธิบายทางกายภาพ

ลองจินตนาการถึงกล่องสี่เหลี่ยมที่บรรจุของไหลอยู่ **ฝาปิดด้านบนเคลื่อนที่ไปทางขวาด้วยความเร็วคงที่** โดยลากของไหลให้เคลื่อนที่ตามไปด้วย

การจัดวางที่ดูเรียบง่ายนี้สร้างรูปแบบการไหลที่ซับซ้อน ซึ่งทำหน้าที่เป็น **ปัญหาอ้างอิง (benchmark problems)** พื้นฐานที่สุดในพลศาสตร์ของไหลเชิงคำนวณ (Computational Fluid Dynamics หรือ CFD)

```mermaid
graph TD
    A["Cavity Geometry<br/>Square Box with Fluid"] --> B["Moving Lid<br/>Constant Velocity U<sub>lid</sub>"]
    B --> C["Primary Vortex<br/>Large Central Rotation"]
    C --> D["Secondary Vortices<br/>Corner Eddies"]
    D --> E["Boundary Layers<br/>Wall Shear Effects"]
    E --> F["Shear Layer<br/>Velocity Gradient"]

    style A fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
    style B fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000
    style C fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000
    style D fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000
    style E fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000
    style F fill:#fff3e0,stroke:#ef6c00,stroke-width:2px,color:#000
```

### 1.2 พารามิเตอร์และฟิสิกส์

| พารามิเตอร์ | ค่าที่กำหนด | คำอธิบาย |
|---|---|---|
| **Domain** | โพรงสี่เหลี่ยมจัตุรัส ($L \times L$) | ขอบเขตการจำลอง |
| **Top Wall** | เคลื่อนที่ ($U = 1$ m/s) | ฝาปิดที่เคลื่อนที่ |
| **Other Walls** | หยุดนิ่ง ($U = 0$) | ผนังด้านข้างและด้านล่าง |
| **Fluid** | อัดตัวไม่ได้ (Incompressible), แบบนิวตัน (Newtonian) | ชนิดของของไหล |
| **Flow** | ลามินาร์ (Laminar) ($Re = 10$) | ลักษณะการไหล |

#### ลักษณะฟิสิกส์ที่เกิดขึ้น:
- **การก่อตัวของ Primary และ Secondary Vortices**
- **การก่อตัวของ Boundary Layer**
- **พลวัตของ Shear Layer ที่รุนแรง**

---

## 2. รากฐานทางคณิตศาสตร์

### 2.1 สมการควบคุม

การเคลื่อนที่ของของไหลถูกควบคุมโดย **Incompressible Navier-Stokes equations**:

**สมการความต่อเนื่อง (การอนุรักษ์มวล):**
$$\nabla \cdot \mathbf{u} = 0$$

**สมการโมเมนตัม:**
$$\rho \left(\frac{\partial \mathbf{u}}{\partial t} + \mathbf{u} \cdot \nabla \mathbf{u}\right) = -\nabla p + \mu \nabla^2 \mathbf{u} + \mathbf{f}$$

ในรูปแบบ Component สำหรับการไหล 2 มิติ:

**แกน x:**
$$\rho \left(\frac{\partial u}{\partial t} + u \frac{\partial u}{\partial x} + v \frac{\partial u}{\partial y}\right) = -\frac{\partial p}{\partial x} + \mu \left(\frac{\partial^2 u}{\partial x^2} + \frac{\partial^2 u}{\partial y^2}\right)$$

**แกน y:**
$$\rho \left(\frac{\partial v}{\partial t} + u \frac{\partial v}{\partial x} + v \frac{\partial v}{\partial y}\right) = -\frac{\partial p}{\partial y} + \mu \left(\frac{\partial^2 v}{\partial x^2} + \frac{\partial^2 v}{\partial y^2}\right)$$

**การนิยามตัวแปร:**
- $\mathbf{u} = (u,v)$ = Velocity Vector (m/s)
- $p$ = Pressure (Pa)
- $\rho$ = Density (kg/m³)
- $\mu$ = Dynamic viscosity (Pa·s)
- $\mathbf{f}$ = Body forces (N/m³)

### 2.2 Reynolds Number

เลขเรย์โนลด์เป็นตัวบ่งชี้ลักษณะการไหลและถูกนิยามดังนี้:
$$Re = \frac{\rho U L}{\mu} = \frac{U L}{\nu}$$

**การนิยามตัวแปร:**
- $\rho$ = ความหนาแน่นของของไหล (kg/m³)
- $U$ = ความเร็วของฝาปิด (m/s)
- $L$ = ความยาวลักษณะเฉพาะของโพรง (m)
- $\mu$ = ความหนืดจลน์ (dynamic viscosity) (Pa·s)
- $\nu$ = ความหนืดคิเนมาติก (kinematic viscosity) (m²/s)

**สำหรับ $Re = 10$** การไหลยังคงเป็นแบบลามินาร์และคงที่ โดยก่อตัวเป็น **Primary Vortex** ที่มีลักษณะเฉพาะอยู่ตรงกลาง

### 2.3 รูปแบบ Finite Volume Method

OpenFOAM ใช้วิธี Finite Volume Method ในการ Discretization:

$$\int_{V_P} \frac{\partial \phi}{\partial t} \, \mathrm{d}V + \int_{V_P} \nabla \cdot \mathbf{F} \, \mathrm{d}V = \int_{V_P} S_\phi \, \mathrm{d}V$$

**การนิยามตัวแปร:**
- $\phi$ = ตัวแปรที่ต้องการแก้สมการ (field variable)
- $V_P$ = Volume ของเซลล์ P
- $\mathbf{F}$ = Flux vector
- $S_\phi$ = Source term

---

## 3. OpenFOAM Solver: icoFoam

### 3.1 คุณสมบัติหลักของ icoFoam

ใน OpenFOAM เราจะใช้ Solver ชื่อ `icoFoam` ซึ่งมีลักษณะเฉพาะดังนี้:

| คุณสมบัติ | รายละเอียด |
|---------|------------|
| **Algorithm** | ใช้ PISO algorithm (Pressure Implicit with Splitting of Operators) |
| **Flow Type** | สำหรับการไหลแบบชั่วคราว (transient) |
| **Compressibility** | รองรับการไหลแบบอัดตัวไม่ได้ (incompressible) |
| **Regime** | เหมาะสำหรับการไหลแบบราบเรียบ (laminar flow) |

### 3.2 อัลกอริทึม PISO

**PISO Algorithm** ใช้วิธีการแบบ predictor-corrector ในการจัดการกับการเชื่อมโยงระหว่างความดันและความเร็ว:

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

    class A,L terminator;
    class B,C,D,F,G,I process;
    class E,J storage;
    class H,K decision;
```

**ขั้นตอนการทำงาน:**
1. **Predict Velocity** - แก้สมการโมเมนตัมโดยใช้ความดันจาก time step ก่อนหน้า
2. **Pressure Correction** - แก้สมการความดันเพื่อให้เกิดความต่อเนื่อง
3. **Velocity Correction** - แก้ไขความเร็วตามความดันที่แก้ไขแล้ว
4. **Repeat** - ทำขั้นตอนที่ 2-3 จนกว่าจะลู่เข้า
5. **Advance Time** - ไปยัง time step ถัดไป

---

## 4. โครงสร้าง OpenFOAM Case

### 4.1 โครงสร้างไดเรกทอรี

```mermaid
graph TD
    A["lidDrivenCavity/<br/>Root Directory"] --> B["0/<br/>Initial Conditions"]
    A --> C["constant/<br/>Mesh Data"]
    A --> D["system/<br/>Control Settings"]
    A --> E["Allrun/<br/>Execution Script"]

    B --> B1["U<br/>Velocity Field<br/>Boundary Conditions"]
    B --> B2["p<br/>Pressure Field<br/>Boundary Conditions"]

    C --> C1["polyMesh/<br/>Mesh Geometry<br/>Points, Faces, Cells"]
    C --> C2["transportProperties<br/>Viscosity Model<br/>and Properties"]

    D --> D1["controlDict<br/>Time Stepping<br/>Solver Controls"]
    D --> D2["fvSchemes<br/>Discretization<br/>Schemes"]
    D --> D3["fvSolution<br/>Linear Solver<br/>Settings"]
    D --> D4["blockMeshDict<br/>Mesh Generation<br/>Parameters"]

    E --> E1["blockMesh<br/>Generate Initial Mesh"]
    E --> E2["icoFoam<br/>Run Incompressible<br/>Flow Solver"]
    E --> E3["paraFoam<br/>Post-processing<br/>and Visualization"]

    classDef storage fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;
    classDef process fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    classDef decision fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    classDef terminator fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;

    class A storage;
    class B,C,D,E process;
    class B1,B2,C1,C2,D1,D2,D3,D4,E1,E2,E3 terminator;
```

**คำอธิบายไดเรกทอรี:**

| ไดเรกทอรี | วัตถุประสงค์ | เนื้อหา |
|-----------|-------------|----------|
| `0/` | เงื่อนไขเริ่มต้น | ค่าฟิลด์เริ่มต้น (ความเร็ว, ความดัน) ที่เวลา $t=0$ |
| `constant/` | คุณสมบัติคงที่ | Mesh ใน `polyMesh/` และคุณสมบัติทางกายภาพ |
| `system/` | การควบคุม Solver | Dictionaries ที่ควบคุมกระบวนการแก้ปัญหาเชิงตัวเลข |

### 4.2 เงื่อนไขขอบเขต (Boundary Conditions)

| ผนัง | เงื่อนไขความเร็ว | ค่า (m/s) |
|---|---|---|
| **Top Wall (Lid)** | $\mathbf{u} = (U_{lid}, 0)$ | $(1, 0)$ |
| **Bottom Wall** | $\mathbf{u} = (0, 0)$ | $(0, 0)$ |
| **Left Wall** | $\mathbf{u} = (0, 0)$ | $(0, 0)$ |
| **Right Wall** | $\mathbf{u} = (0, 0)$ | $(0, 0)$ |

---

## 5. OpenFOAM Code Implementation

### 5.1 การตั้งค่า fvSchemes

**OpenFOAM Code Implementation:**
```cpp
ddtSchemes
{
    default         Euler;
}

gradSchemes
{
    default         Gauss linear;
    grad(p)         Gauss linear;
}

divSchemes
{
    default         none;
    div(phi,U)      Gauss upwind;
}

laplacianSchemes
{
    default         Gauss linear corrected;
}
```

### 5.2 การตั้งค่า fvSolution

**OpenFOAM Code Implementation:**
```cpp
solvers
{
    p
    {
        solver          GAMG;
        tolerance       1e-06;
        relTol          0.05;
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
    nCorrectors      2;
    nNonOrthogonalCorrectors 0;
    pRefCell        0;
    pRefValue       0;
}
```

### 5.3 ไฟล์การตั้งค่าหลัก

**0/U (ฟิลด์ความเร็ว):**
```cpp
dimensions      [0 1 -1 0 0 0 0];
internalField   uniform 0;
boundaryField
{
    movingWall
    {
        type            fixedValue;
        value           uniform (1 0 0);
    }
    fixedWalls
    {
        type            fixedValue;
        value           uniform (0 0 0);
    }
    frontAndBack
    {
        type            empty;
    }
}
```

**0/p (ฟิลด์ความดัน):**
```cpp
dimensions      [0 2 -2 0 0 0 0];
internalField   uniform 0;
boundaryField
{
    movingWall
    {
        type            zeroGradient;
    }
    fixedWalls
    {
        type            zeroGradient;
    }
    frontAndBack
    {
        type            empty;
    }
}
```

**constant/transportProperties:**
```cpp
transportModel  Newtonian;
nu              [0 2 -1 0 0 0 0] 0.01;
```

**system/controlDict:**
```cpp
application     icoFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         0.5;
deltaT          0.005;
writeControl    timeStep;
writeInterval   20;
```

---

## 6. ขั้นตอนการทำงานของการจำลอง CFD

การจำลอง OpenFOAM เป็นไปตามขั้นตอนการทำงานที่เป็นระบบสามขั้นตอน

### 6.1 ขั้นตอน Pre-Processing

#### การสร้าง Geometry และ Mesh

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
- **ผลกระทบ**: คุณภาพ Mesh ส่งผลโดยตรงต่อความแม่นยำของผลเฉลย

#### การกำหนด Boundary Condition

| Boundary Type | คำอธิบาย | การใช้งานทั่วไป |
|---------------|------------|------------------|
| Velocity Inlets | กำหนดความเร็วที่ช่องเข้า | Inlet flows, ducts |
| Pressure Outlets | กำหนดความดันที่ช่องออก | Exit conditions |
| Wall Conditions | กำหนดเงื่อนไขผนัง | No-slip, isothermal |
| Symmetry Planes | กำหนดเงื่อนไขสมมาตร | Symmetric domains |

#### การกำหนดค่าคุณสมบัติทางกายภาพ

- **ความหนาแน่นของของไหล**: $\rho$ (kg/m³)
- **ความหนืด**: $\mu$ (Pa·s)
- **ค่าการนำความร้อน**: $k$ (W/m·K)
- **พารามิเตอร์ Turbulence Model**: k, ε, ω เป็นต้น

### 6.2 ขั้นตอน Solving

Solver เฉพาะทางจะใช้การ Discretization แบบ Finite Volume ของสมการ Navier-Stokes

**สมการพื้นฐาน:**
$$\rho \frac{\partial \mathbf{u}}{\partial t} + \rho (\mathbf{u} \cdot \nabla) \mathbf{u} = -\nabla p + \mu \nabla^2 \mathbf{u} + \mathbf{f}$$

$$\nabla \cdot \mathbf{u} = 0$$

### 6.3 ขั้นตอน Post-Processing

#### การแสดงผลและการวิเคราะห์

การทำงานร่วมกับ ParaView ช่วยให้สามารถแสดงผล Flow Fields ได้อย่างครอบคลุม

**ปริมาณที่น่าสนใจ:**
- **Velocity Vectors**: $\mathbf{u}$ (m/s)
- **Pressure Contours**: $p$ (Pa)
- **Vorticity**: $\omega = \nabla \times \mathbf{u}$ (1/s)
- **Wall Shear Stress**: $\tau_w$ (Pa)

#### การดึงข้อมูลเชิงปริมาณ

ยูทิลิตี `sample` และ `probes` จะดึงข้อมูลเชิงตัวเลข

**OpenFOAM Code Implementation:**
```cpp
probes
{
    type            probes;
    fields          (p U k epsilon);
    probeLocations  ((0 0.1 0) (0.5 0.1 0));
    writeFields     true;
}
```

---

## 7. ผลลัพธ์ที่คาดหวัง

### 7.1 โครงสร้างกระแสวนหลัก

สำหรับ $Re = 10$ การจำลองจะแสดง:

| ลักษณะ | รายละเอียด |
|--------|-------------|
| **Primary Vortex** | กระแสวนขนาดใหญ่ตรงกลางโพรง |
| **ศูนย์กลางกระแสวน** | อยู่เยื้องศูนย์เล็กน้อยที่ $(x/L, y/L) \approx (0.5, 0.4)$ |
| **ทิศทางการไหล** | การไหลเวียนตามเข็มนาฬิกา |
| **ค่าความเร็ว** | สูงสุดบริเวณฝาปิดเคลื่อนที่ ($U = 1$ m/s) |

### 7.2 รูปแบบการไหลเวียนหลัก

| บริเวณ | ทิศทางการไหล | ความเร็วโดยประมาณ |
|---------|---------------|-------------------|
| **บริเวณด้านบน** | ไปทางขวาในแนวนอน | $U = 1$ m/s |
| **ผนังด้านขวา** | ไหลลงตามขอบแนวตั้ง | $0.6-0.7$ m/s |
| **บริเวณด้านล่าง** | ไปทางซ้ายตามผนัง | $0.2-0.3$ m/s |
| **ผนังด้านซ้าย** | ไหลขึ้นตามขอบแนวตั้ง | ความเร็วขึ้นปานกลาง |

### 7.3 จุดตรวจสอบเชิงปริมาณ

ตรวจสอบความถูกต้องของการจำลองด้วยค่าเหล่านี้:

- **Stream Function สูงสุด**: $\psi_{\max} \approx -0.1$ (เครื่องหมายลบ = การหมุนตามเข็มนาฬิกา)
- **ศูนย์กลางกระแสวนหลัก**: $(x, y) = (0.5L, 0.4L)$
- **ขนาดความเร็ว**: $|\mathbf{u}|_{\max} \approx 1.0$ ตามแนว Lid
- **Wall Shear Stress**: มีค่าไม่เป็นศูนย์ตามผนังทั้งหมด

---

## 8. เกณฑ์คุณภาพ Mesh

### 8.1 Non-orthogonality Angle

**Non-orthogonality Angle:**
$$\theta_{\text{max}} = \cos^{-1}\left(\frac{\mathbf{n} \cdot \mathbf{d}}{|\mathbf{n}||\mathbf{d}|}\right)$$

**การนิยามตัวแปร:**
- $\mathbf{n}$ = Normal vector ของ face
- $\mathbf{d}$ = Vector จาก cell center ของ owner ถึง neighbor

```mermaid
graph LR
    A["Cell P<br/>Center Point"] --> B["Face<br/>Normal Vector n"]
    B --> C["Non-orthogonality<br/>Angle θ"]
    C --> D["Cell Q<br/>Center Point"]
    A --> E["Vector d<br/>Owner to Neighbor"]
    E --> D
    B --> F["Face<br/>Plane"]
    D --> F
    C --> G["Quality Check:<br/>θ < 70° = Good<br/>θ > 70° = Poor"]

    %% Styling Definitions
    classDef process fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    classDef decision fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    classDef terminator fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
    classDef storage fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;
    class A,E process;
    class B,F storage;
    class C decision;
    class D terminator;
```

### 8.2 การวัดประสิทธิภาพการประมวลผลแบบขนาน

**Speedup และ Efficiency:**
- Speedup: $S = \frac{T_1}{T_p}$
- Efficiency: $E = \frac{S}{p} \times 100\%$

**การนิยามตัวแปร:**
- $T_1$ = เวลาที่ใช้กับ 1 processor
- $T_p$ = เวลาที่ใช้กับ p processors
- $p$ = จำนวน processors

---

## 9. แนวทางการเรียนรู้

### 9.1 โครงสร้างการเรียนรู้

```mermaid
graph TD
    A["Foundation Module"] --> B["CFD Fundamentals"]
    A --> C["OpenFOAM Basics"]
    B --> D["Single Phase Flow"]
    C --> D
    D --> E["Lid-Driven Cavity<br/>(This Module)"]
    E --> F["Multiphase Fundamentals"]
    D --> G["OpenFOAM Programming"]
    F --> H["Advanced Topics"]
    G --> I["Utilities & Automation"]
    H --> J["Testing & Validation"]
    I --> J

    classDef process fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;

    class A,B,C,D,E,F,G,H,I,J process;
```

### 9.2 ทักษะที่จะได้รับ

เมื่อจบโมดูลนี้ คุณจะมีความเข้าใจอย่างสมบูรณ์เกี่ยวกับ:

**ทักษะที่จะได้รับ:**
- OpenFOAM workflow แบบครบถ้วน
- การจัดการกับปัญหา CFD ที่ซับซ้อนมากขึ้น
- การประยุกต์ใช้แนวคิดที่ได้จากกรณีฐานนี้
- การจำลอง CFD ในระดับมืออาชีพ

**กรณี lid-driven cavity ทำหน้าที่เป็นรากฐานที่ยอดเยี่ยมสำหรับการทำความเข้าใจ:**
- ผลกระทบของคุณภาพ Mesh
- การนำ Boundary Condition ไปใช้อย่างถูกต้อง
- ความสำคัญของการแยกส่วนเชิงตัวเลข (numerical discretization) ที่เหมาะสม

---

## สรุป

**ปัญหา Lid-Driven Cavity** เป็นกรณีทดสอบที่ยอดเยี่ยมสำหรับ CFD Solvers และการประเมินคุณภาพ Mesh เนื่องจากเป็นปัญหามาตรฐานสำหรับ Benchmark ในเอกสารทางวิชาการ

การศึกษาโมดูลนี้จะให้คุณได้เรียนรู้:
- การตั้งค่า OpenFOAM case อย่างถูกต้อง
- การใช้งาน Solver icoFoam สำหรับปัญหา Incompressible Laminar Flow
- การวิเคราะห์ผลลัพธ์และการตรวจสอบความถูกต้อง
- การประยุกต์ใช้แนวคิดกับปัญหา CFD ที่ซับซ้อนมากขึ้น
