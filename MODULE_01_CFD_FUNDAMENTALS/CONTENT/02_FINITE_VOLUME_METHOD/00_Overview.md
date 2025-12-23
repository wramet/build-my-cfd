# ภาพรวม Finite Volume Method ใน OpenFOAM

## บทนำ

**Finite Volume Method (FVM)** เป็นเทคนิคการประมาณค่าแบบตัวเลข (numerical discretization technique) ที่ OpenFOAM ใช้ในการแปลงสมการเชิงอนุพันธ์ย่อย (Partial Differential Equations หรือ PDEs) ที่ควบคุมการไหลของของไหลให้เป็นระบบสมการพีชคณิตที่สามารถคำนวณหาคำตอบได้

เอกสารนี้ให้ภาพรวมแบบครอบคลุมของ Finite Volume Method ใน OpenFOAM ครอบคลุมตั้งแต่แนวคิดพื้นฐาน สมการควบคุม การทำให้เป็นดิสครีต การประกอบเมทริกซ์ การนำไปใช้ในโค้ด ไปจนถึงแนวปฏิบัติที่ดีที่สุด

---

## แนวคิดพื้นฐานของ Finite Volume Method

### หลักการอนุรักษ์

Finite Volume Method ทำงานบน**รูปแบบอินทิกรัลของสมการการอนุรักษ์ (conservation equations)** ซึ่งรับประกันว่าปริมาณทางกายภาพพื้นฐาน เช่น:

- **มวล (Mass)**
- **โมเมนตัม (Momentum)**
- **พลังงาน (Energy)**

จะถูกอนุรักษ์ไว้ในระดับดิสครีต

```mermaid
graph TD
    subgraph "Domain Division into Control Volumes"
        A["Computational Domain"] --> B["Discretization Process"]
        B --> C["Control Volume 1"]
        B --> D["Control Volume 2"]
        B --> E["Control Volume N"]

        subgraph "Single Control Volume Details"
            F["Cell Center<br/>P"]
            G["Face Centers<br/>E, W, N, S, T, B"]
            H["Cell Corners<br/>Vertices"]
            F -.-> G
            G -.-> H
        end

        subgraph "Flow Through Boundaries"
            I["Mass Flux<br/>ρu · A"]
            J["Momentum Flux<br/>ρu² · A"]
            K["Energy Flux<br/>ρh · A"]
            L["Source Terms<br/>S"]

            M["Net Flux = Outflow - Inflow"]
            I --> M
            J --> M
            K --> M
            L --> M
        end
    end

    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style C fill:#e8f5e9
    style D fill:#e8f5e9
    style E fill:#e8f5e9
    style F fill:#fff3e0
    style G fill:#fce4ec
    style H fill:#f1f8e9
    style I fill:#e0f2f1
    style J fill:#e0f2f1
    style K fill:#e0f2f1
    style L fill:#fff8e1
    style M fill:#ffebee
```

### แนวทางการใช้ Control Volume

**Finite Volume Method** แบ่ง Computational Domain ออกเป็นชุดของ **Control Volume (Cells)** ที่ไม่ทับซ้อนกัน โดย:

- **Governing Equations** จะถูกอินทิเกรตเหนือ Control Volume แต่ละอัน
- รับประกันการอนุรักษ์มวล โมเมนตัม และพลังงานในระดับท้องถิ่น (local conservation)
- เป็นรากฐานทางคณิตศาสตร์ของ **Computational Framework ของ OpenFOAM**
- วิธีการที่เข้มงวดในการ Discretize **Partial Differential Equations** โดยยังคงรักษ์ Conservation Laws พื้นฐานทางฟิสิกส์ไว้

---

## สมการควบคุม (Governing Equations)

### การอนุรักษ์มวล

**สมการความต่อเนื่อง** (continuity equation) แสดงหลักการอนุรักษ์มวลในระบบของไหล

```mermaid
graph TD
    subgraph Fluxes
        In["Mass Influx<br/>ρ u S"]
        Out["Mass Outflux<br/>-(ρ u S)_out"]
    end

    In --> Balance["Mass Balance<br/>Net Flux"]
    Out --> Balance

    Balance --> Accum["Accumulation<br/>∂ρ/∂t V"]

    Accum --> Eq["Continuity Equation<br/>∂ρ/∂t + ∇·(ρu) = 0"]

    style Fluxes fill:#e3f2fd,stroke:#1565c0
    style Balance fill:#fff9c4,stroke:#fbc02d
    style Accum fill:#e8f5e9,stroke:#2e7d32
```

**รูปแบบทั่วไป:**
$$\frac{\partial \rho}{\partial t} + \nabla \cdot (\rho \mathbf{u}) = 0$$

**สำหรับการไหลแบบอัดตัวไม่ได้** ($\rho = \text{constant}$):
$$\nabla \cdot \mathbf{u} = 0$$

### การอนุรักษ์โมเมนตัม

**สมการโมเมนตัม** (momentum equation) ซึ่งได้มาจากกฎข้อที่สองของนิวตัน ควบคุมการเคลื่อนที่ของอนุภาคของไหล

```mermaid
graph TD
    subgraph Forces["Forces Acting on Element"]
        P["Pressure Forces<br/>-∇p"]
        V["Viscous Forces<br/>∇·τ"]
        B["Body Forces<br/>ρg"]
    end

    P --> Net["Net Force<br/>ΣF"]
    V --> Net
    B --> Net

    Net -->|Newton's 2nd Law| Acc["Acceleration<br/>ρ Du/Dt"]

    Acc --> Inertia["Inertial Response<br/>Unsteady + Convective"]

    style Forces fill:#e3f2fd,stroke:#1565c0
    style Net fill:#fff9c4,stroke:#fbc02d
    style Acc fill:#e8f5e9,stroke:#2e7d32
```

**รูปแบบทั่วไป:**
$$\rho \frac{\partial \mathbf{u}}{\partial t} + \rho (\mathbf{u} \cdot \nabla) \mathbf{u} = -\nabla p + \mu \nabla^2 \mathbf{u} + \mathbf{f}$$

### การอนุรักษ์พลังงาน

**สมการพลังงาน** (energy equation) ควบคุมการถ่ายเทพลังงานความร้อน (thermal energy) ภายในระบบของไหล

สำหรับของไหลที่มีอุณหภูมิ $T$ สมการพลังงานในรูปของอุณหภูมิคือ:

$$\rho c_p \frac{\partial T}{\partial t} + \rho c_p \mathbf{u} \cdot \nabla T = k \nabla^2 T + Q$$

---

## การทำให้เป็นส่วนย่อยเชิงพื้นที่ (Spatial Discretization)

### โครงสร้าง Mesh

#### แนวทางแบบ Cell-Centered

OpenFOAM ใช้แผนการทำให้เป็นส่วนย่อยแบบ **Finite Volume** ที่เน้น **cell-centered** โดยที่ตัวแปรหลักทั้งหมด (velocity, pressure, temperature, ฯลฯ) จะถูกเก็บไว้ที่จุดศูนย์กลางทางเรขาคณิตของเซลล์คำนวณ

แนวทางนี้มีข้อดีหลายประการสำหรับการคำนวณ CFD:
- **คุณสมบัติการอนุรักษ์** (conservation properties)
- **การนำ Boundary Condition ที่ซับซ้อนไปใช้ได้อย่างตรงไปตรงมา**

```mermaid
graph LR
    subgraph CellCenteredFiniteVolume
        P["Cell P<br/>Owner Cell"]
        N["Cell N<br/>Neighbor Cell"]
        f["Face f<br/>Boundary Interface"]
        C_P["Center Point P<br/>(x_P, y_P, z_P)"]
        C_N["Center Point N<br/>(x_N, y_N, z_N)"]
        C_f["Face Center f<br/>(x_f, y_f, z_f)"]
        Sf["Surface Vector S_f<br/>S_f = n_f × A_f"]
        V_P["Cell Volume V_P<br/>Control Volume"]
        nf["Normal Vector n_f<br/>Unit Normal"]
        Af["Face Area A_f<br/>Surface Area"]

        P -- "Owner" --> f
        N -- "Neighbor" --> f
        P -- "Center" --> C_P
        N -- "Center" --> C_N
        f -- "Center" --> C_f
        f -- "Area Vector" --> Sf
        f -- "Normal" --> nf
        f -- "Area" --> Af
        P -- "Volume" --> V_P
    end

    style P fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    style N fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    style f fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    style C_P fill:#e8f5e9,stroke:#2e7d32,stroke-width:1px,color:#000;
    style C_N fill:#e8f5e9,stroke:#2e7d32,stroke-width:1px,color:#000;
    style C_f fill:#ffebee,stroke:#c62828,stroke-width:1px,color:#000;
    style Sf fill:#fce4ec,stroke:#ad1457,stroke-width:1px,color:#000;
    style V_P fill:#f3e5f5,stroke:#7b1fa2,stroke-width:1px,color:#000;
    style nf fill:#e0f2f1,stroke:#00796b,stroke-width:1px,color:#000;
    style Af fill:#e0f2f1,stroke:#00796b,stroke-width:1px,color:#000;
```

### การคำนวณ Face Flux

#### นิพจน์ Flux ทั่วไป

ในกรอบ Finite Volume Terms การขนส่งทั้งหมดใน Governing Equations จะแสดงเป็น Fluxes ที่ผ่าน Cell Faces

$$\sum_f \mathbf{F}_f \cdot \mathbf{S}_f = 0$$

โดยที่:
- $\mathbf{F}_f$ แทน Flux Vector ที่ Face f
- $\mathbf{S}_f$ คือ Face Area Vector

#### 1. Convective Fluxes ($\nabla \cdot (\phi \mathbf{u})$)

**Term Convective สำหรับ Scalar Field $\phi$**:
$$\int_V \nabla \cdot (\phi \mathbf{u}) \, \mathrm{d}V = \sum_f \phi_f (\mathbf{u}_f \cdot \mathbf{S}_f) = \sum_f \phi_f \Phi_f$$

**Interpolation Schemes สำหรับ $\phi_f$**:

| Scheme | รูปแบบสมการ | ความแม่นยำ | ข้อดี | ข้อเสีย | กรณีที่เหมาะสม |
|--------|--------------|-------------|--------|--------|----------------|
| **CDS** (Central Differencing) | $\phi_f = 0.5(\phi_P + \phi_N)$ | Order 2 | High accuracy for smooth profiles | Unbounded oscillations in steep gradients | Laminar flow, fine meshes |
| **UDS** (Upwind) | $\phi_f = \phi_P$ if $\Phi_f > 0$ | Order 1 | Numerically stable, bounded | Significant numerical diffusion | High convection, coarse meshes |
| **QUICK** | $\phi_f = \frac{6}{8}\phi_P + \frac{3}{8}\phi_N - \frac{1}{8}\phi_{NN}$ | Order 3 | Excellent accuracy | Can be unstable for high convection | Structured grids, smooth flows |
| **MUSCL/TVD** | $\phi_f = \phi_U + \phi(r) \cdot \frac{1}{2}(\phi_D - \phi_U)$ | Order 2 | High accuracy with boundedness | Complex implementation | General CFD applications |

#### 2. Diffusive Fluxes ($\nabla \cdot (\Gamma \nabla \phi)$)

**Term Diffusive สำหรับ Scalar Field $\phi$ ที่มี Diffusion Coefficient $\Gamma$**:
$$\int_V \nabla \cdot (\Gamma \nabla \phi) \, \mathrm{d}V = \sum_f \Gamma_f (\nabla \phi)_f \cdot \mathbf{S}_f$$

**การประมาณค่า Gradient**:

สำหรับ Orthogonal Meshes ค่า Gradient ที่ Face จะถูกประมาณโดยใช้ Finite Differences ระหว่าง Adjacent Cell Centers:

$$(\nabla \phi)_f \cdot \mathbf{S}_f = |\mathbf{S}_f| \frac{\phi_N - \phi_P}{|\mathbf{d}_{PN}|}$$

---

## การทำให้เป็นดิสครีตเชิงเวลา (Temporal Discretization)

### Time Integration Schemes

| Scheme | รูปแบบสมการ | ความแม่นยำ | ความเสถียร | ข้อจำกัด | กรณีที่เหมาะสม |
|--------|--------------|-------------|------------|-----------|----------------|
| **Euler Explicit** | $\phi^{n+1} = \phi^n + \Delta t \cdot \mathcal{L}(\phi^n)$ | Order 1 | Conditionally stable | CFL < 1, small time steps | Explicit dynamics, small problems |
| **Euler Implicit** | $\phi^{n+1} = \phi^n + \Delta t \cdot \mathcal{L}(\phi^{n+1})$ | Order 1 | Unconditionally stable | Requires nonlinear solve | Steady-state, large time steps |
| **Crank-Nicolson** | $\phi^{n+1} = \phi^n + \frac{\Delta t}{2} [\mathcal{L}(\phi^n) + \mathcal{L}(\phi^{n+1})]$ | Order 2 | Good stability | Moderate complexity | Accurate transient flows |
| **BDF (Order 2)** | $\phi^{n+1} = \frac{4}{3}\phi^n - \frac{1}{3}\phi^{n-1} + \frac{2}{3}\Delta t \cdot \mathcal{L}(\phi^{n+1})$ | Order 2 | Good stability | Requires 2 previous steps | High accuracy transient |

---

## การประกอบเมทริกซ์ (Matrix Assembly)

## จากสมการสู่เมทริกซ์

สำหรับแต่ละเซลล์ เราจะได้สมการที่เชื่อมโยง $\phi_P$ กับเซลล์เพื่อนบ้าน $\phi_N$:
$$a_P \phi_P + \sum_N a_N \phi_N = b$$

เมื่อเราเขียนสมการนี้สำหรับ *ทุก* เซลล์ เราจะได้ระบบสมการเชิงเส้นขนาดใหญ่:
$$[A][x] = [b]$$

*   **[A]**: Sparse matrix ที่ประกอบด้วยสัมประสิทธิ์ ($a_P, a_N$) ซึ่งได้มาจากรูปทรงเรขาคณิตและฟลักซ์ (fluxes)
*   **[x]**: Vector of unknowns (เช่น Pressure ที่ทุกเซลล์)
*   **[b]**: Source vector ที่ประกอบด้วยเทอมที่ชัดเจน (explicit terms) และค่า Boundary values

OpenFOAM solvers (PCG, PBiCG) จะแก้สมการเมทริกซ์นี้ด้วยวิธีวนซ้ำ (iteratively)

### ตัวอย่างสัมประสิทธิ์เมทริกซ์ (Matrix Coefficients Example)

สำหรับการแพร่กระจายแบบบริสุทธิ์ ($\nabla^2 \phi = 0$):
*   $a_N = -\frac{\Gamma A_f}{d_{PN}}$ (สัมประสิทธิ์เพื่อนบ้าน)
*   $a_P = -\sum a_N$ (สัมประสิทธิ์แนวทแยง)

```mermaid
graph LR
    A[Cell P] --> B[Cell N1]
    A --> C[Cell N2]
    A --> D[Cell N3]
    A --> E[Cell N4]
    F[Face 1] --> A
    F --> B
    G[Face 2] --> A
    G --> C
    H[Face 3] --> A
    H --> D
    I[Face 4] --> A
    I --> E
    J[a_P coefficient] --> A
    K[a_N1 coefficient] --> B
    L[a_N2 coefficient] --> C
    M[a_N3 coefficient] --> D
    N[a_N4 coefficient] --> E
    style A fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    style B fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;
    style C fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;
    style D fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;
    style E fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;
    style F fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    style G fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    style H fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    style I fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    style J fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
    style K fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
    style L fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
    style M fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
    style N fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
```

### โครงสร้าง Coefficient Matrix

การทำให้เป็นส่วนย่อยเชิงพื้นที่และเชิงเวลาของ Governing Equations ส่งผลให้เกิด Sparse Linear System:

$$\mathbf{A} \cdot \boldsymbol{\phi} = \mathbf{b}$$

โดยที่:
- $\mathbf{A}$ คือ Coefficient Matrix
- $\boldsymbol{\phi}$ คือ Solution Vector
- $\mathbf{b}$ คือ Source Vector

**คุณสมบัติที่สำคัญ**:
- **Diagonal Dominance**: $|A_{PP}| \geq \sum_{N} |A_{PN}|$ เพื่อความเสถียร
- **Sparsity Pattern**: แต่ละแถวมี Non-Zero Entries เฉพาะสำหรับเซลล์นั้นเองและเซลล์ข้างเคียงโดยตรง
- **Natural Sparsity**: เกิดจากการทำให้เป็นส่วนย่อยแบบ Finite Volume

---

## การนำ OpenFOAM ไปใช้งาน

## คลาสหลัก

### **fvMesh**: คลาสเมชพื้นฐานใน OpenFOAM

`fvMesh` คือคลาสเมชพื้นฐานใน OpenFOAM ที่จัดเก็บข้อมูลทางเรขาคณิตและโทโพโลยีทั้งหมดที่จำเป็นสำหรับการดิสครีตแบบปริมาตรจำกัด (finite volume discretization)

```mermaid
graph LR
    subgraph "Base Classes"
        A["polyMesh<br/>Polygonal mesh topology<br/>Geometric structure"]
        B["fvFields<br/>Field management<br/>Boundary conditions"]
    end

    C["fvMesh<br/>Finite volume mesh<br/>Complete mesh structure"]
    D["dynamicFvMesh<br/>Time-varying mesh<br/>Moving/deforming meshes"]

    A --> C
    B --> C
    C --> D

    %% Styling Definitions
    classDef base fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;
    classDef core fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    classDef derived fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;

    class A,B base;
    class C core;
    class D derived;
```

### **volScalarField / volVectorField**: คลาสฟิลด์แบบเทมเพลต

คลาสฟิลด์แบบเทมเพลตเหล่านี้แสดงถึงตัวแปรที่กำหนด ณ จุดศูนย์กลางเซลล์ (จุดควบคุมปริมาตรจำกัด)

**OpenFOAM Code Implementation**:

```cpp
volScalarField p
(
    IOobject
    (
        "p",
        runTime.timeName(),
        mesh,
        IOobject::MUST_READ,
        IOobject::AUTO_WRITE
    ),
    mesh
);
```

### **fvMatrix**: หัวใจสำคัญของระบบพีชคณิตเชิงเส้น

`fvMatrix` คือหัวใจสำคัญของระบบพีชคณิตเชิงเส้นของ OpenFOAM ซึ่งแสดงถึงรูปแบบการดิสครีตของสมการเชิงอนุพันธ์ย่อย (partial differential equations)

**OpenFOAM Code Implementation**:

```cpp
fvScalarMatrix TEqn
(
    fvm::ddt(rho, T)           // อนุพันธ์เชิงเวลาแบบ Implicit
  + fvm::div(phi, T)           // การพาความร้อนแบบ Implicit
  - fvm::laplacian(k, T)       // การแพร่แบบ Implicit
 ==
    fvc::div(q)                // เทอมแหล่งกำเนิดแบบ Explicit
);
```

## ตัวอย่างโค้ด: การแปลงสมการคณิตศาสตร์เป็นโค้ด

### **สมการคณิตศาสตร์**:
$$\frac{\partial \rho \mathbf{U}}{\partial t} + \nabla \cdot (\phi \mathbf{U}) - \nabla \cdot (\mu \nabla \mathbf{U}) = -\nabla p$$

### **OpenFOAM Code Implementation**:

```cpp
fvVectorMatrix UEqn
(
    fvm::ddt(rho, U)                    // อนุพันธ์เชิงเวลาแบบ Implicit
  + fvm::div(phi, U)                    // เทอมการพาแบบ Implicit
  - fvm::laplacian(mu, U)               // เทอมการแพร่แบบ Implicit
 ==
    -fvc::grad(p)                       // เทอมความดันแบบ Explicit
);

UEqn.relax();                          // Relaxation สำหรับความเสถียร
solve(UEqn == -fvc::grad(p));          // แก้ระบบสมการ
```

---

## Pressure-Velocity Coupling

การเชื่อมโยงระหว่าง Pressure และ Velocity Fields เป็นสิ่งสำคัญของการจำลอง Incompressible Flow

| Algorithm | ลักษณะการทำงาน | รอบการทำซ้ำ | ข้อดี | ข้อเสีย |
|-----------|-----------------|---------------|--------|----------|
| **SIMPLE** | Sequential solution with under-relaxation | Multiple per time step | Robust, steady-state | Slow convergence |
| **PISO** | Multiple pressure corrections per time step | 2-3 corrections per step | Accurate for transient | Can be unstable |
| **PIMPLE** | Hybrid SIMPLE + PISO | Flexible | Good for both steady/transient | More complex |

```mermaid
graph TD
    subgraph "SIMPLE (Steady-State)"
        S_Start["Start Iteration"] --> S_Mom["Momentum Predictor"]
        S_Mom --> S_Pres["Pressure Equation"]
        S_Pres --> S_Corr["Correct U & p"]
        S_Corr --> S_Turb["Turbulence/Energy"]
        S_Turb --> S_Conv{"Converged?"}
        S_Conv -- No --> S_Start
        S_Conv -- Yes --> S_End["End Simulation"]
    end

    subgraph "PISO (Transient)"
        P_Start["Start Time Step"] --> P_Mom["Momentum Predictor"]
        P_Mom --> P_Loop["PISO Loop (2-3 times)"]
        P_Loop --> P_Pres["Pressure Equation"]
        P_Pres --> P_Corr["Correct U & p"]
        P_Corr --> P_Loop
        P_Corr -- "Loop Done" --> P_Turb["Turbulence/Energy"]
        P_Turb --> P_End["Next Time Step"]
    end

    subgraph "PIMPLE (Hybrid Transient)"
        Pi_Start["Start Time Step"] --> Pi_Outer["Outer Loop (SIMPLE)"]
        Pi_Outer --> Pi_Mom["Momentum Predictor"]
        Pi_Mom --> Pi_Inner["Inner Loop (PISO)"]
        Pi_Inner --> Pi_Pres["Pressure Equation"]
        Pi_Pres --> Pi_Corr["Correct U & p"]
        Pi_Corr --> Pi_Inner
        Pi_Corr -- "Inner Done" --> Pi_Turb["Turbulence/Energy"]
        Pi_Turb --> Pi_Conv{"Converged?"}
        Pi_Conv -- No --> Pi_Outer
        Pi_Conv -- Yes --> Pi_End["Next Time Step"]
    end

    classDef simple fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
    classDef piso fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px;
    classDef pimple fill:#fff3e0,stroke:#ef6c00,stroke-width:2px;

    class S_Start,S_Mom,S_Pres,S_Corr,S_Turb,S_Conv,S_End simple;
    class P_Start,P_Mom,P_Loop,P_Pres,P_Corr,P_Turb,P_End piso;
    class Pi_Start,Pi_Outer,Pi_Mom,Pi_Inner,Pi_Pres,Pi_Corr,Pi_Turb,Pi_Conv,Pi_End pimple;
```

---

## แนวปฏิบัติที่ดีที่สุด (Best Practices)

### คุณภาพของ Mesh (Mesh Quality)

คุณภาพของ Mesh เป็นปัจจัยสำคัญที่ส่งผลต่อความแม่นยำและความเสถียรของการจำลอง CFD

#### พารามิเตอร์คุณภาพหลัก

**Non-orthogonality**
การวัดมุมระหว่าง Face normal vector และเส้นเชื่อมต่อจุดศูนย์กลางของ Cell ที่อยู่ติดกัน พารามิเตอร์นี้ส่งผลโดยตรงต่อความแม่นยำของการคำนวณ Gradient

- **ค่าที่แนะนำ**: < 50°
- **ขีดจำกัดวิกฤต**: > 70° อาจเกิด Numerical diffusion ที่สำคัญ
- **การควบคุม**: `nonOrthogonalCorrectors` ใน `fvSolution` dictionary

```mermaid
graph LR
    subgraph "Cell Geometry Relationship"
        C1["Cell 1<br/>Center P"] -->|"Connecting<br/>Line d"| C2["Cell 2<br/>Center N"]
        F["Shared Face<br/>Surface f"] -->|"Face Normal<br/>Vector n"| C1
        F -->|"Face Normal<br/>Vector n"| C2
    end

    subgraph "Non-orthogonality Analysis"
        A["Angle between<br/>face normal n<br/>and line d"] --> B["Non-orthogonal<br/>Angle θ"]
        B --> C["θ < 50°: Good<br/>θ > 70°: Critical"]
    end

    subgraph "Impact on Calculations"
        D["Gauss Theorem<br/>Gradient Computation"] --> E["Accuracy<br/>Reduction"]
        B --> E
    end
```

**Skewness**
การวัดปริมาณการเบี่ยงเบนของจุด Face-cell intersection จาก Geometric face center

- **ค่าที่แนะนำ**: < 0.5
- **ขีดจำกัดวิกฤต**: > 0.6 สามารถลดความแม่นยำได้อย่างรุนแรง
- **ผลกระทบ**: นำข้อผิดพลาด Interpolation เข้ามาในการคำนวณ Face value
- **เครื่องมือวินิจฉัย**: `checkMesh` utility

### การเลือก Numerical Scheme (Numerical Scheme Selection)

#### **Temporal Discretization Schemes**

| Scheme | ลำดับความแม่นยำ | คำอธิบาย | กรณีที่เหมาะสม |
|--------|-----------------|-----------|---------------|
| Euler | First-order explicit | เรียบง่าย คำนวณเร็ว | การทดสอบเบื้องต้น |
| Backward | Second-order implicit | สมดุลระหว่างความเร็วและความแม่นยำ | การจำลอง Transient ทั่วไป |
| CrankNicolson | Second-order | ความแม่นยำยอดเยี่ยม | การจำลองที่ต้องการความแม่นยำสูง |

#### **Spatial Discretization for Convective Terms**

| Scheme | คุณสมบัติ | ข้อดี | ข้อเสีย |
|--------|------------|---------|---------|
| Gauss linear | Central differencing | Second-order accurate | ไม่เสถียรสำหรับ Reynolds สูง |
| Gauss upwind | First-order upwind | Stability สูงมาก | Numerical diffusion สูง |
| Gauss limitedLinear | Limited linear | สมดุลระหว่าง accuracy และ stability | Complex implementation |
| Gauss vanLeer | Van Leer limiter | สมดุลดี | Computational cost สูง |

**OpenFOAM Code Implementation:**
```cpp
// ใน fvSchemes dictionary
divSchemes
{
    div(phi,U)      Gauss limitedLinearV 1;
    div(phi,k)      Gauss limitedLinear 1;
    div(phi,epsilon) Gauss upwind;
}
```

### การตรวจสอบการลู่เข้า (Convergence Monitoring)

#### **Residuals**

แสดงถึงการวัดว่า Solution ปัจจุบันเป็นไปตาม Discretized governing equations ได้ดีเพียงใด

$$r = |A\phi - b|$$

- **การลดลงที่ต้องการ**: 3-6 ระดับขนาด (orders of magnitude)
- **การตรวจสอบ**: `residuals` subdictionary ใน `functions` ของ `controlDict`
- **เกณฑ์การลู่เข้า**: < 1e-5 สำหรับ Solvers ส่วนใหญ่

#### **Under-relaxation**

เทคนิค Stabilization ที่ช่วยชะลออัตราการเปลี่ยนแปลงเพื่อป้องกัน Numerical oscillations และ Divergence

$$\phi^{new} = \phi^{old} + \alpha (\phi^{calc} - \phi^{old})$$

**การตั้งค่าใน `fvSolution`:**
```cpp
relaxationFactors
{
    fields
    {
        p               0.3;
        U               0.5;
    }
    equations
    {
        k               0.7;
        epsilon         0.7;
    }
}
```

---

## สรุป

Finite Volume Method ใน OpenFOAM เป็นกรอบการทำงานที่ทรงพลังสำหรับการจำลอง CFD ซึ่งมีจุดแข็งหลัก ๆ ดังนี้:

1. **การอนุรักษ์โดยธรรมชาติ**: รับประกันการอนุรักษ์มวล โมเมนตัม และพลังงานในระดับดิสครีต

2. **ความยืดหยุ่น**: รองรับ Unstructured Meshes ที่ซับซ้อนและ Boundary Conditions ที่หลากหลาย

3. **สถาปัตยกรรมแบบเทมเพลต**: ช่วยให้สามารถนำโค้ดกลับมาใช้ใหม่ได้กับปริมาณทางฟิสิกส์ที่แตกต่างกัน

4. **ระบบเมทริกซ์เบาบาง**: ช่วยให้สามารถแก้ปัญหาขนาดใหญ่ได้อย่างมีประสิทธิภาพ

5. **การจัดการข้อผิดพลาดที่แข็งแกร่ง**: รองรับ Mesh Quality ที่หลากหลายและมี Correction Schemes สำหรับ Non-orthogonal Meshes

การเข้าใจหลักการเหล่านี้เป็นสิ่งสำคัญสำหรับการใช้งาน OpenFOAM อย่างมีประสิทธิภาพและการพัฒนา Solvers แบบ Custom

---

> [!TIP] **เอกสารที่เกี่ยวข้อง**
> - [[01_Introduction]] - บทนำสู่ Finite Volume Method
> - [[02_Fundamental_Concepts]] - แนวคิดพื้นฐาน
> - [[03_Spatial_Discretization]] - การทำให้เป็นดิสครีตเชิงพื้นที่
> - [[04_Temporal_Discretization]] - การทำให้เป็นดิสครีตเชิงเวลา
> - [[05_Matrix_Assembly]] - การประกอบเมทริกซ์
> - [[06_OpenFOAM_Implementation]] - การนำไปใช้ใน OpenFOAM
> - [[07_Best_Practices]] - แนวปฏิบัติที่ดีที่สุด
> - [[08_Exercises]] - แบบฝึกหัด
