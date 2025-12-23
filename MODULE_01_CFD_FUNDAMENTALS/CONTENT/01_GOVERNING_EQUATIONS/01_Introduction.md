# สมการควบคุมของพลศาสตร์ของไหล: รากฐานทางคณิตศาสต์สำหรับ CFD

## บทนำ

สมการควบคุมของพลศาสตร์ของไหลเป็น **รากฐานทางคณิตศาสตร์** ของ Computational Fluid Dynamics (CFD) สมการเหล่านี้อธิบายถึง **การอนุรักษ์มวล, โมเมนตัม, และพลังงาน** ในการไหลของไหล และถูกแก้ปัญหาด้วยวิธีเชิงตัวเลขใน OpenFOAM

## พัฒนาการทางประวัติศาสตร์

รากฐานของพลศาสตร์ของไหลมาจาก **หลักการของกลศาสตร์ตัวกลางต่อเนื่อง** ซึ่งได้รับการพัฒนาอย่างเป็นระบบครั้งแรกโดย Claude-Louis Navier และ George Gabriel Stokes ในช่วงต้นศตวรรษที่ 19

```mermaid
graph LR
    A["Continuum<br/>Mechanics"] --> B["Infinitesimal<br/>Control Volume"]
    B --> C["Field Variables"]
    C --> D["Velocity: u(x,t)"]
    C --> E["Pressure: p(x,t)"]
    C --> F["Temperature: T(x,t)"]
    B --> G["Fluid as Continuous<br/>Medium"]
    G --> H["Continuous<br/>Field Functions"]
    H --> I["Conservative Form<br/>in OpenFOAM"]
    I --> J["Finite Volume<br/>Discretization"]
    I --> K["Shock Wave<br/>Accuracy"]
    I --> L["Conservation<br/>Properties"]

    classDef process fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    classDef decision fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    classDef terminator fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
    classDef storage fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;

    class A,B,G process;
    class C,H,I,J decision;
    class D,E,F,K,L storage
```

### สมมติฐานพื้นฐาน

- **ของไหลถูกพิจารณาว่าเป็นตัวกลางต่อเนื่อง** แทนที่จะเป็นอนุภาคแยกส่วน
- **ตัวแปรสนามเป็นฟังก์ชันต่อเนื่อง**:
  - ความเร็ว: $\mathbf{u}(\mathbf{x},t)$
  - ความดัน: $p(\mathbf{x},t)$
  - อุณหภูมิ: $T(\mathbf{x},t)$

### Conservative Form ใน OpenFOAM

สมการควบคุมแสดงใน **Conservative form** เพื่อ:
- ให้การแสดงผลที่แม่นยำของคลื่นกระแทก (shock waves)
- รักษาคุณสมบัติการอนุรักษ์ในปริมาตรควบคุม
- **เข้ากันได้กับวิธี Finite Volume discretization** ของ OpenFOAM

---

## กฎการอนุรักษ์พื้นฐาน

### 1. การอนุรักษ์มวล (สมการความต่อเนื่อง)

หลักการนี้ระบุว่า **มวลไม่สามารถถูกสร้างหรือทำลายได้** ภายในปริมาตรควบคุม

> [!INFO] หลักการอนุรักษ์มวล
> มวลไม่สามารถถูกสร้างขึ้นหรือถูกทำลายได้ในระบบการไหลของของไหล เมื่อไม่มีแหล่งกำเนิดหรือแหล่งรับมวลอยู่

**สำหรับของไหลอัดตัวได้**:
$$\frac{\partial \rho}{\partial t} + \nabla \cdot (\rho \mathbf{u}) = 0 \tag{1}$$

โดยที่:
- $\rho$ = ความหนาแน่นของของไหล [kg/m³]
- $\mathbf{u}$ = เวกเตอร์ความเร็ว [m/s]
- $\nabla \cdot$ = Divergence operator

**สำหรับของไหลอัดตัวไม่ได้** ($\rho = \text{constant}$):
$$\nabla \cdot \mathbf{u} = 0 \tag{2}$$

เงื่อนไข **divergence-free condition** นี้ทำให้มั่นใจได้ว่าอัตราการไหลเชิงปริมาตร (volumetric flow rate) ที่ไหลเข้าสู่ปริมาตรควบคุมขนาดเล็กมาก ๆ จะเท่ากับอัตราการไหลเชิงปริมาตรที่ไหลออก

### 2. การอนุรักษ์โมเมนตัม (สมการ Navier-Stokes)

สมการนี้ได้มาจากการประยุกต์ใช้ **กฎข้อที่สองของนิวตัน** โดยสร้างสมดุลระหว่างแรงต่างๆ:

$$\rho \frac{\partial \mathbf{u}}{\partial t} + \rho (\mathbf{u} \cdot \nabla) \mathbf{u} = -\nabla p + \nabla \cdot \boldsymbol{\tau} + \mathbf{f} \tag{3}$$

โดยที่:
- $p$ = ความดัน [Pa]
- $\boldsymbol{\tau}$ = Viscous stress tensor [Pa]
- $\mathbf{f}$ = Body forces (เช่น แรงโน้มถ่วง) [N/m³]

**Viscous stress tensor สำหรับ Newtonian fluid**:
$$\boldsymbol{\tau} = \mu \left[ \nabla \mathbf{u} + (\nabla \mathbf{u})^T \right] - \frac{2}{3} \mu (\nabla \cdot \mathbf{u}) \mathbf{I} \tag{4}$$

โดยที่:
- $\mu$ = Dynamic viscosity [Pa·s]
- $\mathbf{I}$ = Identity tensor

```mermaid
graph TD
    subgraph Forces["Applied Forces"]
        P["Pressure Forces<br/>-∇p"]
        V["Viscous Forces<br/>∇⋅τ"]
        B["Body Forces<br/>f"]
    end

    P --> Sum["Net Force<br/>ΣF"]
    V --> Sum
    B --> Sum

    Sum -->|Newton's 2nd Law| Acc["Acceleration<br/>ρ Du/Dt"]

    Acc --> Inertia["Inertial Terms<br/>Local: ∂u/∂t<br/>Convective: (u⋅∇)u"]

    style Forces fill:#e3f2fd,stroke:#1565c0
    style Sum fill:#fff9c4,stroke:#fbc02d
    style Acc fill:#e8f5e9,stroke:#2e7d32
```

### 3. การอนุรักษ์พลังงาน

สมการนี้อิงตาม **กฎข้อที่หนึ่งของอุณหพลศาสตร์**:

$$\rho c_p \frac{\partial T}{\partial t} + \rho c_p (\mathbf{u} \cdot \nabla) T = k \nabla^2 T + \Phi + Q \tag{5}$$

โดยที่:
- $c_p$ = Specific heat capacity ที่ความดันคงที่ [J/(kg·K)]
- $k$ = Thermal conductivity [W/(m·K)]
- $\Phi$ = Viscous dissipation [W/m³]
- $Q$ = แหล่งกำเนิดหรือตัวรับความร้อน [W/m³]

**Viscous dissipation**:
$$\Phi = \boldsymbol{\tau} : \nabla \mathbf{u} \tag{6}$$

---

## สัญกรณ์เทนเซอร์และรูปแบบองค์ประกอบ

### Tensor Notation

สมการควบคุมสามารถแสดงได้อย่างกระชับโดยใช้ **Index notation** (Einstein summation convention):

**สมการความต่อเนื่อง**:
$$\frac{\partial \rho}{\partial t} + \frac{\partial}{\partial x_i} (\rho u_i) = 0 \tag{7}$$

**สมการโมเมนตัมในรูป Component**:
$$\rho \frac{\partial u_i}{\partial t} + \rho u_j \frac{\partial u_i}{\partial x_j} = -\frac{\partial p}{\partial x_i} + \frac{\partial \tau_{ij}}{\partial x_j} + f_i \tag{8}$$

โดยที่ $i,j = 1,2,3$ แทนสามมิติเชิงพื้นที่

---

## การนำไปใช้งานใน OpenFOAM

### การทำให้เป็นส่วนย่อยด้วย Finite Volume

OpenFOAM ใช้ **Finite Volume Method (FVM)** ในการจัดการสมการบน **polyhedral meshes**:

**Integral form ของสมการการอนุรักษ์**:
$$\int_V \frac{\partial \phi}{\partial t} \, \mathrm{d}V + \oint_S \phi \mathbf{u} \cdot \mathbf{n} \, \mathrm{d}S = \int_V S_\phi \, \mathrm{d}V \tag{9}$$

โดยที่:
- $\phi$ = ปริมาณที่ถูกขนส่ง (transported quantity)
- $V$ = Control volume [m³]
- $S$ = Control surface [m²]
- $\mathbf{n}$ = เวกเตอร์แนวฉากที่ชี้ออก (outward normal vector)

**การทำให้เป็นส่วนย่อยใน OpenFOAM**:
```cpp
// การทำให้เป็นส่วนย่อยด้วย Finite Volume ใน OpenFOAM
fvScalarMatrix TEqn
(
    fvm::ddt(rho, T)                   // พจน์อนุพันธ์เทียบกับเวลา
  + fvm::div(phi, T)                   // พจน์การพาความร้อน/มวล
  - fvm::laplacian(k/rho, T)           // พจน์การแพร่
 ==
    sources/rho                        // พจน์แหล่งกำเนิด
);

TEqn.solve();                          // แก้ระบบสมการเชิงเส้น
```

### คลาส Field แบบ Template-Based

OpenFOAM ใช้ **Templated field classes** เพื่อจัดการปริมาณทางกายภาพ:

```cpp
// ตัวอย่างการประกาศ Field ใน OpenFOAM
volScalarField p(mesh);           // Field ความดัน
volVectorField U(mesh);           // Field ความเร็ว
volScalarField T(mesh);           // Field อุณหภูมิ
surfaceScalarField phi(mesh);     // Field ฟลักซ์
```

**การหาอนุพันธ์อัตโนมัติ**:
```cpp
// ตัวอย่างการหาอนุพันธ์อัตโนมัติ
volVectorField gradP = fvc::grad(p);              // Gradient ความดัน
volScalarField divU = fvc::div(U);                // Divergence ความเร็ว
volTensorField gradU = fvc::grad(U);              // Tensor Gradient ความเร็ว
```

### Time Discretization Schemes

OpenFOAM รองรับ Time discretization ที่หลากหลาย:

| Scheme | ความแม่นยำ | ประเภท | ข้อดี | เหมาะสำหรับ |
|--------|------------|---------|--------|-------------|
| Euler | อันดับหนึ่ง | Explicit/Implicit | เสถียร, ง่าย | Transient problems ทั่วไป |
| Crank-Nicolson | อันดับสอง | Implicit | ความแม่นยำสูง | ปัญหาที่ต้องการความแม่นยำ |
| Backward | อันดับสอง | Implicit | เสถียรมาก | Stiff problems |

**การตั้งค่าใน OpenFOAM**:
```cpp
// การเลือก Time scheme
ddtSchemes
{
    default         Euler;               // อันดับหนึ่ง
    // default        CrankNicolson 0.9;  // อันดับสองแบบผสม
    // default        backward;            // อันดับสอง
}
```

---

## คุณสมบัติทางคณิตศาสตร์และกลยุทธ์การแก้ปัญหา

### ความไม่เป็นเชิงเส้น

**พจน์ Convective** $(\mathbf{u} \cdot \nabla)\mathbf{u}$ ทำให้เกิด **ความไม่เป็นเชิงเส้น** ซึ่งต้องใช้วิธีการแก้ปัญหาแบบวนซ้ำ:

```cpp
// การจัดการพจน์ไม่เป็นเชิงเส้น
fvVectorMatrix UEqn
(
    fvm::ddt(rho, U)
  + fvm::div(phi, U)
  + fvc::div((rho*phi), U) - fvm::Sp(fvc::div(phi*rho), U)  // Treat nonlinearity
);
```

### การเชื่อมโยงความดัน-ความเร็ว

สมการเหล่านี้มี **การเชื่อมโยงกันอย่างมาก** ผ่าน Pressure-velocity coupling โดย OpenFOAM ใช้อัลกอริทึม:

#### อัลกอริทึม SIMPLE (Semi-Implicit Method for Pressure-Linked Equations)

> [!TIP] อัลกอริทึม SIMPLE
> อัลกอริทึม SIMPLE ใช้สำหรับการแก้สมการโมเมนตัมและความดันแบบ coupled ในการไหลแบบอัดตัวไม่ได้

**ขั้นตอนอัลกอริทึม SIMPLE**:
1. **Momentum Prediction**: แก้สมการโมเมนตัมโดยใช้ความดันจาก time step ก่อนหน้า
2. **Pressure Correction**: แก้สมการแก้ไขความดันเพื่อให้เกิดความต่อเนื่องของมวล
3. **Velocity Correction**: แก้ไขความเร็วโดยใช้ความดันที่ถูกแก้ไข
4. **Convergence Check**: ตรวจสอบการลู่เข้าและทำซ้ำถ้าจำเป็น

**การนำไปใช้ใน OpenFOAM**:
```cpp
// อัลกอริทึม SIMPLE
while (simple.correctNonOrthogonal())
{
    // สมการโมเมนตัม
    tmp<fvVectorMatrix> UEqn(fvm::ddt(U) + fvm::div(phi, U));
    UEqn().relax();

    // สมการความดัน
    adjustPhi(phi, U, p);

    // ลูปการเชื่อมโยงความดัน-ความเร็ว
    for (int corr = 0; corr < nCorr; corr++)
    {
        // แก้โมเมนตัม
        solve(UEqn() == -fvc::grad(p));

        // แก้ความดัน
        solve(fvm::laplacian(rAU, p) == fvc::div(phi));
    }
}
```

```mermaid
graph LR
    A["Start SIMPLE Algorithm"] --> B["Momentum Prediction<br/>Solve momentum equations<br/>using pressure from<br/>previous iteration"]

    B --> C["Pressure Correction<br/>Solve pressure correction<br/>equation to ensure<br/>mass continuity"]

    C --> D["Velocity Correction<br/>Update velocity field<br/>using corrected<br/>pressure"]

    D --> E{"Convergence<br/>Check"}

    E -->|Not converged| B
    E -->|Converged| F["End<br/>Solution<br/>Complete"]

    classDef process fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    classDef decision fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    classDef terminator fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;

    class A,B,C,D process;
    class E decision;
    class F terminator
```

### Boundary Conditions

การกำหนด **Boundary Conditions** ที่เหมาะสมเป็นสิ่งสำคัญ:

```cpp
// ตัวอย่าง Boundary Condition
dimensions      [0 2 -2 0 0 0 0];

internalField   uniform 0;

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform (10 0 0);    // ทางเข้าความเร็ว
    }

    outlet
    {
        type            zeroGradient;       // ทางออก
    }

    walls
    {
        type            noSlip;            // ผนังแบบ No-slip
    }

    symmetry
    {
        type            symmetry;          // ระนาบสมมาตร
    }
}
```

---

## การวิเคราะห์มิติและการทำให้ไร้มิติ

เพื่อความเข้าใจและการเปรียบเทียบที่ดีขึ้น สมการควบคุมมักจะถูกทำให้ไร้มิติโดยใช้ **Characteristic scales**:

### Characteristic Scales

- **มาตราส่วนความยาว (Length scale)**: $L$ [m]
- **มาตราส่วนความเร็ว (Velocity scale)**: $U_{\text{ref}}$ [m/s]
- **มาตราส่วนเวลา (Time scale)**: $t_{\text{ref}} = L/U_{\text{ref}}$ [s]
- **มาตราส่วนความดัน (Pressure scale)**: $p_{\text{ref}} = \rho U_{\text{ref}}^2$ [Pa]

### Reynolds Number

**Reynolds number แบบไร้มิติ**:
$$\text{Re} = \frac{\rho U_{\text{ref}} L}{\mu} \tag{10}$$

**สมการโมเมนตัมแบบไร้มิติ**:
$$\frac{\partial \mathbf{u}^*}{\partial t^*} + (\mathbf{u}^* \cdot \nabla^*) \mathbf{u}^* = -\nabla^* p^* + \frac{1}{\text{Re}} \nabla^{*2} \mathbf{u}^* + \mathbf{f}^* \tag{11}$$

โดยที่เครื่องหมายดอกจัน (*) แทนปริมาณไร้มิติ

---

## กรณีพิเศษและการลดรูป

### การไหลที่อัดตัวไม่ได้ (Incompressible Flow)

สำหรับ **incompressible flows** ($\rho = \text{constant}$) สมการจะลดรูปเป็น:

$$\nabla \cdot \mathbf{u} = 0 \tag{12}$$
$$\rho \left( \frac{\partial \mathbf{u}}{\partial t} + (\mathbf{u} \cdot \nabla) \mathbf{u} \right) = -\nabla p + \mu \nabla^2 \mathbf{u} + \mathbf{f} \tag{13}$$

### Laminar vs Turbulent Flow

| ลักษณะ | Laminar Flow | Turbulent Flow |
|---------|--------------|---------------|
| การเคลื่อนที่ | แบบชั้นๆ สมมาตร | ไม่สมมาตร มีปั่นป่วน |
| การผสม | การแพร่โมเลกุล | การพาอย่างมาก |
| สมการ | Navier-Stokes ตรงๆ | RANS/LES/DES |
| ความซับซ้อน | น้อย | สูงมาก |

**Reynolds Decomposition สำหรับ Turbulent Flow**:
$$\mathbf{u} = \overline{\mathbf{u}} + \mathbf{u}' \tag{14}$$
$$p = \overline{p} + p' \tag{15}$$

**RANS Equations**:
$$\rho \left( \frac{\partial \overline{\mathbf{u}}}{\partial t} + (\overline{\mathbf{u}} \cdot \nabla) \overline{\mathbf{u}} \right) = -\nabla \overline{p} + \mu \nabla^2 \overline{\mathbf{u}} - \nabla \cdot (\rho \overline{\mathbf{u}' \mathbf{u}'}) + \mathbf{f} \tag{16}$$

```mermaid
graph TD
    subgraph "Laminar Flow Characteristics"
        A["Smooth Streamlines"] --> B["Parallel Flow Layers"]
        B --> C["Predictable Motion"]
        C --> D["Low Reynolds Number"]
        D --> E["Direct NS Solution"]
    end

    subgraph "Turbulent Flow Characteristics"
        F["Chaotic Eddies"] --> G["Random Fluctuations"]
        G --> H["Mixing Enhancement"]
        H --> I["High Reynolds Number"]
        I --> J["RANS/LES Models"]
    end

    subgraph "Mathematical Treatment"
        K["Navier-Stokes"] --> L["Direct Solution"]
        M["Reynolds Decomposition"] --> N["RANS Equations"]
        N --> O["Turbulence Models"]
    end

    A --> K
    F --> M

    classDef process fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    classDef decision fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    classDef terminator fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
    classDef storage fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;

    class A,B,C,D,E,F,G,H,I,J process;
    class K,L,M,N,O storage
```

---

## บทสรุป

ความแม่นยำทางคณิตศาสตร์และการนำไปใช้งานที่ครอบคลุมใน OpenFOAM ช่วยให้สามารถจำลองการไหลของของไหลที่ซับซ้อนได้อย่างแม่นยำในงานวิศวกรรมและวิทยาศาสตร์ ตั้งแต่ **การไหลแบบ Laminar ในท่อ** ไปจนถึง **การเผาไหม้แบบ Turbulent และระบบ Multiphase**

### จุดสำคัญที่ควรจำ

- **Conservative Form** สำคัญต่อการรักษาคุณสมบัติการอนุรักษ์ใน FVM
- **Pressure-Velocity Coupling** เป็นความท้าทายหลักในการแก้สมการ Navier-Stokes
- **Reynolds Number** คือปัจจัยสำคัญในการกำหนดระบอบการไหลและการเลือก Turbulence Model
- **OpenFOAM** ให้เครื่องมือที่ยืดหยุ่นและทรงพลังในการแก้สมการควบคุมเหล่านี้

> [!SUCCESS] การเรียนรู้ต่อ
- ศึกษาเพิ่มเติมเกี่ยวกับ [[02_Conservation_Laws]]
- ดูตัวอย่างการใช้งานใน [[05_OpenFOAM_Implementation]]
- ฝึกปัญหาใน [[09_Exercises]]
