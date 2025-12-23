# การกำหนดสูตรทางคณิตศาสตร์ของ Boundary Conditions

## บทนำ

**Boundary Conditions** เป็นองค์ประกอบพื้นฐานในการจำลองพลศาสตร์ของไหลเชิงคำนวณ (Computational Fluid Dynamics หรือ CFD) ซึ่งกำหนดว่าคุณสมบัติของไหลมีพฤติกรรมอย่างไรที่ขอบเขตทางกายภาพของโดเมนการคำนวณ

ใน OpenFOAM, Boundary Condition ถูกนำมาใช้ผ่านคลาส Field เฉพาะทางที่สืบทอดมาจากคลาสพื้นฐาน `fvPatchField` ซึ่งเป็นโครงสร้างที่แข็งแกร่งสำหรับการจัดการสถานการณ์ทางกายภาพต่างๆ ที่พบในการประยุกต์ใช้ทางวิศวกรรม

### ความสำคัญของ Boundary Conditions

> [!INFO] **ความสำคัญของ Boundary Condition**
> Boundary Condition มีความสำคัญอย่างยิ่งในการจำลอง CFD เนื่องจากเป็นตัวกำหนดว่าของไหลมีปฏิสัมพันธ์กับขอบเขตโดเมนอย่างไร ซึ่งส่งผลต่อ:
> - **การบังคับใช้ข้อจำกัดทางกายภาพ**: เช่น เงื่อนไขไม่ลื่น (no-slip conditions) ที่ผนังแข็ง
> - **การระบุแรงขับเคลื่อน**: เช่น การไล่ระดับความดัน (pressure gradients)
> - **การรับรองการอนุรักษ์มวล**: ผ่านเงื่อนไขทางเข้า/ออก (inlet/outlet conditions)
> - **การสร้างผลเฉลยเอกลักษณ์**: ให้แผนการแยกส่วนเชิงตัวเลขสร้างผลลัพธ์ที่มีความหมายทางกายภาพ

### ปัญหาที่กำหนดไม่ดี (Ill-Posed Problems)

หากไม่มีการกำหนด Boundary Condition ที่เหมาะสม การกำหนดสูตรทางคณิตศาสตร์จะไม่สมบูรณ์ นำไปสู่ปัญหาที่กำหนดไม่ดี (ill-posed problems) ซึ่งไม่สามารถหาผลเฉลยที่เป็นเอกลักษณ์ได้

---

## พื้นฐานทางคณิตศาสตร์

### สมการควบคุมที่เกี่ยวข้อง

Boundary Condition เหล่านี้กำหนดข้อจำกัดที่จำเป็นในการแก้ระบบสมการเชิงอนุพันธ์ย่อยที่ควบคุมการไหลของของไหล:

**สมการหลัก:**
- **สมการความต่อเนื่อง** (Continuity Equation): $\nabla \cdot \mathbf{u} = 0$
- **สมการโมเมนตัม** (Momentum Equation): $\rho \frac{\partial \mathbf{u}}{\partial t} + \rho (\mathbf{u} \cdot \nabla) \mathbf{u} = -\nabla p + \mu \nabla^2 \mathbf{u} + \mathbf{f}$
- **สมการพลังงาน** (Energy Equation)

### การจำแนกประเภทสมการเชิงอนุพันธ์ย่อย

พื้นฐานทางคณิตศาสตร์ของ Boundary Condition มาจากการจำแนกประเภทของสมการเชิงอนุพันธ์ย่อย:

```mermaid
graph LR
    subgraph "Partial Differential Equations Classification"
        PDE["Partial Differential<br/>Equations"]

        PDE --> Elliptic["<b>Elliptic PDE</b><br/>Equilibrium Problems<br/>- Laplace equation<br/>- Poisson equation<br/>- Steady-state heat conduction<br/><br/><b>Boundary Conditions:</b><br/>• Dirichlet (Value specified)<br/>• Neumann (Derivative specified)<br/>• Mixed (Robin)"]

        PDE --> Parabolic["<b>Parabolic PDE</b><br/>Time-dependent Problems<br/>- Heat equation<br/>- Diffusion equation<br/>- Unsteady heat conduction<br/><br/><b>Boundary Conditions:</b><br/>• Initial condition +<br/>• Dirichlet/Neumann<br/>  on spatial boundaries"]

        PDE --> Hyperbolic["<b>Hyperbolic PDE</b><br/>Wave/Transport Problems<br/>- Wave equation<br/>- Euler equations<br/>- Advection equation<br/><br/><b>Boundary Conditions:</b><br/>• Initial condition +<br/>• Characteristic-based<br/>  boundary conditions"]
    end

    subgraph "CFD Applications"
        EllipticCFD["<b>Elliptic in CFD:</b><br/>• Pressure equation<br/>• Potential flow<br/>• Steady heat transfer"]

        ParabolicCFD["<b>Parabolic in CFD:</b><br/>• Unsteady diffusion<br/>• Transient heat transfer<br/>• Viscous flows"]

        HyperbolicCFD["<b>Hyperbolic in CFD:</b><br/>• Compressible flow<br/>• Wave propagation<br/>• Convective transport"]
    end

    Elliptic -.-> EllipticCFD
    Parabolic -.-> ParabolicCFD
    Hyperbolic -.-> HyperbolicCFD

    classDef pde fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    classDef cfd fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;
    class PDE pde;
    class Elliptic,Parabolic,Hyperbolic pde;
    class EllipticCFD,ParabolicCFD,HyperbolicCFD cfd;
```

### เงื่อนไข Well-Posedness (Hadamard)

สำหรับปัญหาที่จะมีผลเฉลยที่ถูกต้อง จะต้องเป็น **Well-Posed Problem** ตามเกณฑ์ของ Hadamard:

1. **มี Solution อยู่** (Existence)
2. **Solution มีความเฉพาะเจาะจง** (Uniqueness)
3. **Solution ขึ้นอยู่กับ Boundary Data อย่างต่อเนื่อง** (Stability)

| ประเภท PDE | ตัวอย่าง | ข้อกำหนด Boundary Conditions |
|-------------|------------|------------------------------|
| **Elliptic** | Steady-State Diffusion, Potential Flow | Dirichlet หรือ Neumann บน Boundary ทั้งหมด |
| **Parabolic** | Transient Diffusion, Boundary Layer | Initial Conditions + Boundary Conditions |
| **Hyperbolic** | Wave Propagation, Inviscid Flow | Characteristics-Based Boundary Conditions |

---

## 1. Dirichlet Boundary Conditions (Fixed Value)

### แนวคิดหลัก

**Dirichlet Boundary Conditions** กำหนดค่าที่แน่นอนของตัวแปร Field $\phi$ ที่พื้นผิวขอบเขต (Boundary Surface) $\partial \Omega$ ของโดเมนการคำนวณ (Computational Domain)

### สูตรทางคณิตศาสตร์

$$\phi|_{\partial \Omega} = \phi_0(\mathbf{x}, t)$$

**ตัวแปร:**
- $\phi$ = ตัวแปร Field ที่ต้องการกำหนดค่า
- $\partial \Omega$ = พื้นผิวขอบเขตของโดเมน
- $\phi_0$ = ฟังก์ชันค่าที่กำหนดไว้ล่วงหน้า
- $\mathbf{x}$ = ตำแหน่งในปริภูมิ
- $t$ = เวลา

### วัตถุประสงค์หลัก

- ใช้เมื่อทราบพฤติกรรมทางกายภาพที่ขอบเขตล่วงหน้า
- เหมาะสำหรับการกำหนดค่าที่วัดได้จริงหรือข้อกำหนดทางวิศวกรรม

### ตัวอย่างการประยุกต์ใช้

| กรณีศึกษา | สมการ | คำอธิบาย |
|-------------|---------|-----------|
| **Velocity Inlets** | $\mathbf{u} = \mathbf{u}_{\text{inlet}}(\mathbf{x}, t)$ | โปรไฟล์ความเร็วขาเข้าที่ทราบจากการทดลอง |
| **Temperature Boundaries** | $T = T_{\text{wall}}$ | อุณหภูมิผนังคงที่สำหรับพื้นผิว Isothermal |
| **Pressure Outlets** | $p = p_{\text{ambient}}$ | ความดันขาออกเท่ากับสภาวะแวดล้อม |

### การใช้งานใน OpenFOAM

```mermaid
graph LR
    A["Computational Domain Ω"] --> B["Boundary Surface ∂Ω"]
    B --> C["FixedValue Boundary"]
    C --> D["Field φ Assignment"]
    D --> E["φ = φ₀(x,t)"]

    F["Velocity Inlet"] --> G["u = u_inlet(x,t)"]
    H["Temperature Wall"] --> I["T = T_wall"]
    J["Pressure Outlet"] --> K["p = p_ambient"]

    C --> F
    C --> H
    C --> J

    L["OpenFOAM Implementation"] --> M["fixedValue"]
    M --> N["value uniform <constant>"]
    M --> O["timeVaryingValue <function>"]

    classDef process fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    classDef storage fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;

    class A,B,C,D,E,F,G,H,I,J,K process;
    class L,M,N,O storage;
```

#### OpenFOAM Code Implementation

```cpp
// Example in OpenFOAM dictionary format for velocity field
boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform (10 0 0);  // Fixed velocity vector in m/s
    }

    wallTemperature
    {
        type            fixedValue;
        value           uniform 300;       // Fixed temperature in Kelvin
    }
}
```

> [!TIP] **เงื่อนไขการใช้งาน**
> - ค่าคงที่: `value uniform <constant>`
> - ค่าที่เปลี่ยนตามเวลา: `value table ((0 1) (1 2))`

**ความหมายทางกายภาพ:**
การตีความทางกายภาพของ Dirichlet Condition คือ **ขอบเขตทำหน้าที่เป็นแหล่งกำเนิดหรือแหล่งรับ** ที่รักษาระดับตัวแปร Field ไว้ที่ค่าที่กำหนด โดยไม่คำนึงถึงผลลัพธ์ภายใน

**เงื่อนไขเหล่านี้มักใช้สำหรับ:**
- **ความเร็วขาเข้า (Inlet velocities)**: การกำหนดโปรไฟล์ความเร็วที่ทางเข้าของไหล
- **อุณหภูมิผนัง (Wall temperatures)**: การกำหนดการกระจายตัวของอุณหภูมิบนพื้นผิวที่ถูกทำให้ร้อน/เย็น
- **ค่าความเข้มข้น (Concentration values)**: การกำหนดความเข้มข้นของสปีชีส์ที่ขอบเขตการถ่ายโอนมวล

---

## 2. Neumann Boundary Conditions (Fixed Gradient)

### แนวคิดหลัก

**Neumann Boundary Conditions** กำหนดอนุพันธ์ปกติ (Normal Derivative) ของตัวแปร Field ที่ขอบเขต ซึ่งเป็นการกำหนด Flux ของปริมาณที่ผ่านพื้นผิวขอบเขต

### สูตรทางคณิตศาสตร์

$$\frac{\partial \phi}{\partial n}\bigg|_{\partial \Omega} = \mathbf{n} \cdot \nabla \phi = g_0(\mathbf{x}, t)$$

**ตัวแปร:**
- $\mathbf{n}$ = เวกเตอร์ Normal หน่วยที่ชี้ออกด้านนอก
- $g_0$ = Normal Gradient ที่กำหนดไว้
- $\nabla \phi$ = เกรเดียนต์ของ Field
- $\frac{\partial}{\partial n}$ = อนุพันธ์ในทิศทาง Normal ไปยังขอบเขต

### ความสำคัญ

- เหมาะสำหรับปัญหาการถ่ายเทความร้อน การขนส่งมวล และการวิเคราะห์ความเค้น
- เงื่อนไข Flux มักถูกกำหนดได้ง่ายกว่าค่าตัวแปร

### ตัวอย่างการประยุกต์ใช้

| กรณีศึกษา | สมการ | คำอธิบาย |
|-------------|---------|-----------|
| **Adiabatic Walls** | $\frac{\partial T}{\partial n} = 0$ | ขอบเขตหุ้มฉนวน ไม่มี Heat Flux |
| **Symmetry Planes** | $\frac{\partial \phi}{\partial n} = 0$ | สมมาตรแบบกระจกใน Flow Field |
| **Specified Heat Flux** | $-k \frac{\partial T}{\partial n} = q''_{\text{wall}}$ | Heat Flux ที่ทราบค่า |
| **Free-slip Walls** | $\frac{\partial u_t}{\partial n} = 0$ | การไหลตามผนังโดยไม่มีแรงต้านความหนืด |

### การใช้งานใน OpenFOAM

```mermaid
graph LR
    A["Boundary ∂Ω"] --> B["Normal Vector n"]
    B --> C["Gradient ∇φ"]
    C --> D["Normal Derivative ∂φ/∂n"]
    D --> E["Flux g₀(x,t)"]

    F["Control Volume"] --> A
    G["Field Variable φ"] --> C

    H["Adiabatic Wall"] --> I["∂T/∂n = 0"]
    J["Heat Flux"] --> K["-k∂T/∂n = q''ₙ"]
    L["Symmetry Plane"] --> M["∂φ/∂n = 0"]

    I --> D
    K --> D
    M --> D

    classDef process fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    classDef decision fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    classDef storage fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;

    class A,B,F,G process;
    class C,D,E decision;
    class H,J,L storage;
```

#### OpenFOAM Code Implementation

```cpp
boundaryField
{
    outlet
    {
        type            fixedGradient;
        gradient        uniform (0 0 0);   // Zero gradient (fully developed flow)
    }

    heatFluxWall
    {
        type            fixedGradient;
        gradient        uniform 1000;      // Heat flux in W/m²
    }
}
```

> [!INFO] **Zero Gradient Condition**
> เงื่อนไข `zeroGradient` มีความสำคัญอย่างยิ่งสำหรับ:
> - **ขอบเขตทางออก (Outlet boundaries)**: การสมมติว่าการไหลพัฒนาเต็มที่ (fully developed flow)
> - **ระนาบสมมาตร (Symmetry planes)**: ที่ไม่มี Flux ไหลผ่านขอบเขตสมมาตร
> - **ผนังฉนวนความร้อน (Adiabatic walls)**: ที่ไม่มีการถ่ายเทความร้อน (Heat Flux)

ความสำคัญทางกายภาพของ Neumann Condition คือ **การควบคุมอัตราการเปลี่ยนแปลงของตัวแปร Field** ในทิศทาง Normal ไปยังขอบเขต ซึ่งเป็นการจัดการ Flux ที่ไหลผ่านพื้นผิวขอบเขตได้อย่างมีประสิทธิภาพ

---

## 3. Mixed (Robin) Boundary Conditions

### แนวคิดหลัก

**Mixed Boundary Conditions** หรือที่เรียกว่า **Robin Boundary Conditions** แสดงถึงการรวมกันของ Dirichlet และ Neumann conditions โดยเชื่อมโยงค่า Field กับ Normal Derivative

### สูตรทางคณิตศาสตร์

$$a \phi + b \frac{\partial \phi}{\partial n} = c$$

**ตัวแปร:**
- $a$, $b$, $c$ = ค่าคงที่หรือฟังก์ชันของตำแหน่งและเวลา

### ลักษณะพิเศษ

- เมื่อ $b = 0$ → Pure Dirichlet Condition
- เมื่อ $a = 0$ → Pure Neumann Condition
- เมื่อ $a, b \neq 0$ → Mixed Condition

### ข้อดี

- ให้การแสดงปรากฏการณ์ Boundary ทางกายภาพที่สมจริงยิ่งขึ้น
- เหมาะสำหรับการถ่ายเทความร้อนแบบพาความร้อนและผลกระทบจากแรงเสียดทาน

### ตัวอย่างการประยุกต์ใช้

| กรณีศึกษา | สมการ | คำอธิบาย |
|-------------|---------|-----------|
| **Convective Heat Transfer** | $h(T_{\text{wall}} - T_{\infty}) = -k \frac{\partial T}{\partial n}$ | $h$ = Convective Heat Transfer Coefficient |
| **Wall Function Formulations** | $u_\tau^2 = \nu_t \frac{\partial u}{\partial n}$ | Wall Shear Stress เกี่ยวข้องกับ Velocity Gradient |
| **Porosity and Permeability** | $\alpha \phi + \beta \frac{\partial \phi}{\partial n} = \gamma$ | การไหลผ่านตัวกลางที่มีรูพรุน |
| **Radiation Boundary** | $\frac{\partial T}{\partial n} + \sigma \epsilon (T^4 - T_{\infty}^4) = 0$ | รวมผลกระทบ Conduction และ Radiation |

### การประยุกต์ใช้สำคัญ - Newton's Cooling Law

$$-k\frac{\partial T}{\partial n} = h(T_s - T_\infty)$$

โดยที่:
- $k$ = Thermal Conductivity
- $h$ = Convective Heat Transfer Coefficient
- $T_s$ = Surface Temperature
- $T_\infty$ = Ambient Fluid Temperature

**การจัดรูปแบบใหม่:**
$$hT + k\frac{\partial T}{\partial n} = hT_\infty$$

### การใช้งานใน OpenFOAM

```mermaid
graph LR
    A["Mixed Boundary Condition"] --> B["Field Value Contribution"]
    A --> C["Normal Gradient Contribution"]
    B --> D["a ϕ term"]
    C --> E["b ∂ϕ/∂n term"]
    D --> F["Dirichlet Component"]
    E --> G["Neumann Component"]
    A --> H["General Form:"]
    H --> I["aϕ + b∂ϕ/∂n = c"]
    F --> J["Prescribed Value"]
    G --> K["Prescribed Flux"]
    J --> L["Fixed Temperature"]
    K --> M["Fixed Heat Flux"]
    L --> N["Convection Boundary"]
    M --> N
    N --> O["Robin Condition"]
    O --> P["Combined BC"]

    style A fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
    style B fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000
    style C fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000
    style H fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000
    style N fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000
```

#### OpenFOAM Code Implementation

```cpp
boundaryField
{
    convectiveWall
    {
        type            mixed;
        refGradient     uniform 0;
        refValue        uniform 300;
        valueFraction   uniform 0.5;     // Weighting factor (0 = gradient, 1 = value)
    }
}
```

พารามิเตอร์ `valueFraction` ควบคุมการถ่วงน้ำหนัก:
- `valueFraction = 1`: Dirichlet Condition บริสุทธิ์
- `valueFraction = 0`: Neumann Condition บริสุทธิ์
- `0 < valueFraction < 1`: Mixed Condition

**Boundary Condition นี้มีประโยชน์อย่างยิ่งสำหรับ:**
- **การถ่ายเทความร้อนแบบ Conjugate (Conjugate heat transfer)**: ซึ่งทั้งอุณหภูมิและผลกระทบของ Heat Flux มีความสำคัญ
- **ขอบเขตการแผ่รังสี (Radiation boundaries)**: ซึ่งการถ่ายเทความร้อนแบบแผ่รังสีเชื่อมโยงกับการถ่ายเทความร้อนแบบพา
- **เงื่อนไขการลื่นบางส่วน (Partial slip conditions)**: ในพลศาสตร์ของก๊าซเจือจาง

---

## ขั้นตอนการ Discretization แบบ Finite Volume

### การแปลง Boundary Conditions สู่ระบบสมการเชิงเส้น

ใน Finite Volume Framework ของ OpenFOAM, Boundary Conditions ถูกนำไปใช้ผ่าน Class Hierarchy `fvPatchField`:

#### ฟังก์ชันหลัก

1. **`updateCoeffs()`**: อัปเดต Boundary Condition Coefficients
2. **`evaluate()`**: กำหนดค่า Boundary Face โดยตรง
3. **`valueInternalCoeffs()`**: การมีส่วนร่วมของ Internal Coefficient
4. **`valueBoundaryCoeffs()`**: การมีส่วนร่วมของ Boundary Coefficient

### ขั้นตอนการ Discretization สำหรับแต่ละประเภท

#### 1. Dirichlet Condition (Fixed Value)

**การแปลงสู่ Discretized System:**
```cpp
// Dirichlet Implementation
// กำหนด Diagonal Coefficient ให้มีค่ามาก + Source Term
// ผลลัพธ์: φ_boundary = φ_specified
```

กลไก:
- กำหนดค่าสัมประสิทธิ์ในเมทริกซ์ให้มีค่ามาก (large number)
- กำหนด source term เพื่อให้ได้ค่าที่ต้องการ

#### 2. Neumann Condition (Fixed Gradient)

**การแปลงสู่ Discretized System:**
```cpp
// Neumann Implementation
// รวม Gradient โดยตรงในการคำนวณ Flux
// ผลลัพธ์: Flux = -k * (φ_boundary - φ_internal)/Δn = specified_flux
```

กลไก:
- คำนวณ Flux ผ่าน Boundary Face โดยตรง
- ใช้ Gradient ที่กำหนดในการคำนวณ

#### 3. Mixed/Robin Condition

**การแปลงสู่ Discretized System:**
```cpp
// Robin Implementation
// เชื่อมโยงระหว่าง Value และ Gradient
// ผลลัพธ์: a*φ_boundary + b*(∂φ/∂n) = c
```

กลไก:
1. **ปรับ Boundary Face Coefficients** พิจารณาทั้งค่าและ Gradient
2. **ดัดแปลง Diagonal Coefficients** ให้สอดคล้องกับความสัมพันธ์เชิงเส้น
3. **ปรับ Source Terms** บังคับใช้ความสัมพันธ์ระหว่าง Field Value และ Normal Derivative

### การนำไปใช้งานใน OpenFOAM

**โครงสร้างคลาสพื้นฐาน:**

```cpp
template<class Type>
class fvPatchField
:
    public Field<Type>,
    public fvPatchField<Type>
{
public:
    // Virtual functions for boundary condition evaluation
    virtual void updateCoeffs() = 0;
    virtual void evaluate(const Pstream::commsTypes commsType) = 0;
    virtual tmp<Field<Type>> snGrad() const = 0;
};
```

---

## Wall Functions สำหรับ Turbulence

### แนวคิดหลัก

**Wall Function** เป็นตัวเชื่อมช่องว่างระหว่างทฤษฎี Turbulence ที่ถูกจำกัดด้วยผนังและข้อจำกัดของ Computational Mesh

### กฎ Logarithmic Law of the Wall

กฎ Logarithmic Law of the Wall สำหรับความเร็วคือ:

$$u^+ = \frac{1}{\kappa} \ln(y^+) + B$$

**ตัวแปร:**
- $u^+ = \frac{u}{u_\tau}$ คือความเร็วไร้มิติ
- $y^+ = \frac{y u_\tau}{\nu}$ คือระยะห่างจากผนังไร้มิติ
- $u_\tau = \sqrt{\frac{\tau_w}{\rho}}$ คือความเร็วเสียดทาน (friction velocity)
- $\kappa \approx 0.41$ คือค่าคงที่ von Kármán
- $B \approx 5.2$ คือค่าคงที่เชิงประจักษ์

### โครงสร้างชั้นขอบเขต (Boundary Layer Structure)

```mermaid
graph LR
    Wall["Wall Surface<br/>y+ < 1"]
    Viscous["Viscous Sublayer<br/>y+ < 5<br/>u+ = y+"]
    Buffer["Buffer Layer<br/>5 < y+ < 30<br/>Complex transition"]
    Log["Logarithmic Layer<br/>y+ > 30<br/>u+ = (1/k) ln(y+) + B"]
    Outer["Outer Layer<br/>Full turbulence<br/>u+ = u_tau"]

    Wall --> Viscous
    Viscous --> Buffer
    Buffer --> Log
    Log --> Outer

    style Wall fill:#ffebee,stroke:#c62828,stroke-width:3px
    style Viscous fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    style Buffer fill:#fff9c4,stroke:#fbc02d,stroke-width:2px
    style Log fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    style Outer fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
```

### การใช้งานใน OpenFOAM

#### Wall Function สำหรับ k-epsilon Model

```cpp
walls
{
    type            kqRWallFunction; // For turbulent kinetic energy k
    value           uniform 0.1;
}

walls
{
    type            epsilonWallFunction; // For turbulent dissipation epsilon
    value           uniform 0.01;
}
```

#### Wall Function สำหรับ k-omega Model

```cpp
walls
{
    type            omegaWallFunction; // For specific dissipation rate omega
    value           uniform 1000;
}
```

### Wall Function มาตรฐาน

**สำหรับ Turbulent Kinetic Energy:**
$$k_w = \frac{u_\tau^2}{\sqrt{C_\mu}}$$

- $k_w$ = Turbulent kinetic energy at wall
- $u_\tau$ = Friction velocity
- $C_\mu$ = Model constant (typically 0.09)

### ข้อกำหนด Mesh

**ค่า y+ ที่เหมาะสม:**
- **30-300** สำหรับ k-ε model
- **11-300** สำหรับ k-ω model
- **y+ < 1** สำหรับ Low Reynolds Number Models

---

## Boundary Conditions ขั้นสูง

### Time-Varying Boundary Conditions

OpenFOAM รองรับ Time-Dependent Boundary Condition ที่ซับซ้อน:

#### การป้อนข้อมูลแบบตาราง (Tabular Data Input)

```cpp
boundaryField
{
    inlet
    {
        type            uniformFixedValue;
        uniformValue    table
        (
            (0     (1 0 0))    // Time = 0s, velocity = (1,0,0) m/s
            (10    (2 0 0))    // Time = 10s, velocity = (2,0,0) m/s
            (20    (1.5 0 0))  // Time = 20s, velocity = (1.5,0,0) m/s
        );
    }
}
```

#### ฟังก์ชันทางคณิตศาสตร์ (Mathematical Functions)

```cpp
boundaryField
{
    pulsatingInlet
    {
        type            codedFixedValue;
        value           uniform (0 0 0);
        code
        #{
            // Sinusoidal velocity variation
            scalar t = this->db().time().value();
            vectorField& field = *this;
            field = vector(1.0 + 0.5*sin(2*pi*0.1*t), 0, 0);
        #};
    }
}
```

### Coupled Boundary Conditions

สำหรับปัญหา Multiphysics ที่ต้องการการเชื่อมโยงระหว่าง Region ต่างๆ:

| Type | ความสามารถ | การประยุกต์ใช้ |
|------|-------------|-----------------|
| `turbulentTemperatureCoupledBaffleMixed` | การเชื่อมโยงความร้อนระหว่าง Region | Conjugate Heat Transfer |
| `thermalBaffle1DHeatTransfer` | การนำความร้อน 1 มิติผ่านผนัง | ผนังบางที่มีการนำความร้อน |
| `regionCoupledAMIFVPatchField` | Interface Conditions สำหรับ Non-Conformal Meshes | การเชื่อมต่อ Mesh ที่ไม่ตรงกัน |

### Cyclic (Periodic) Boundary Conditions

#### `cyclic` Boundary Condition

ใช้ **Periodic Boundary Conditions** โดยการสร้างการเชื่อมต่อเชิงทอพอโลยีระหว่าง Boundary Patch สองอัน

**การแปลงที่เป็นไปได้:**
- **การเลื่อน** (translation)
- **การหมุน** (rotation)
- **การสะท้อน** (reflection)

#### การนำไปใช้งานทางคณิตศาสตร์

สำหรับ Field $\phi$ ที่ใช้กับ Cyclic Boundary Conditions:
$$\phi_{\text{patch A}}(\mathbf{x}) = \phi_{\text{patch B}}(\mathbf{T}(\mathbf{x}))$$

โดยที่:
- $\mathbf{T}$ = การแปลงทางเรขาคณิตที่แมปพิกัดจาก Patch A ไปยัง Patch B
- $\phi$ = Field ที่ถูกบังคับใช้เงื่อนไข

ความต่อเนื่องของ Flux:
$$\mathbf{n}_A \cdot \nabla \phi_A = -\mathbf{n}_B \cdot \nabla \phi_B$$

#### OpenFOAM Code Implementation

```cpp
left
{
    type            cyclic;
    neighbourPatch  right;
}
```

### `inletOutlet` Boundary Condition

เป็นเงื่อนไขแบบไฮบริดที่ซับซ้อน ซึ่งจะเปลี่ยนพฤติกรรมโดยอัตโนมัติตามทิศทางการไหลเฉพาะที่

#### หลักการทางคณิตศาสตร์

Boundary Condition นี้ทำงานโดยพิจารณาจากเครื่องหมายของ **Local Mass Flux**:
$$\phi_f = \rho \mathbf{u} \cdot \mathbf{n}_f$$

ตรรกะการสลับ:
$$
\mathbf{u}_b = \begin{cases}
\mathbf{u}_{\text{fixed}} & \text{if } \phi_f > 0 \text{ (inflow)} \\
\mathbf{u}_{\text{zero-grad}} & \text{if } \phi_f \leq 0 \text{ (outflow)}
\end{cases}
$$

#### OpenFOAM Code Implementation

```cpp
outlet
{
    type            inletOutlet;
    inletValue      uniform (0 0 0);
    value           uniform (0 0 0);
}
```

---

## สรุปการเลือก Boundary Conditions

### ตารางการเลือกคู่ Boundary Condition

| Flow Situation | Velocity BC | Pressure BC | Physical Justification | Best Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **ทางเข้า (ความเร็วที่ทราบ)** | `fixedValue` | `zeroGradient` | กำหนดโปรไฟล์ความเร็วขาเข้า, ความดันพัฒนาขึ้นเองตามธรรมชาติ | การไหลในท่อที่พัฒนาเต็มที่ |
| **ทางเข้า (ความดันที่ทราบ)** | `pressureInletVelocity` | `fixedValue` | การไหลที่ขับเคลื่อนด้วยความดัน, ความเร็วคำนวณจาก Pressure Gradient | การไหลแรงดัน, ระบบปั๊ม |
| **ทางออก (บรรยากาศ)** | `zeroGradient` | `fixedValue` | การระบายออกสู่สภาวะแวดล้อมอย่างอิสระ | ท่อนำออกสู่บรรยากาศ |
| **ผนัง (No-Slip)** | `noSlip` (หรือ `fixedValue` 0) | `zeroGradient` | เงื่อนไข No-Slip แบบหนืด, Pressure Gradient เกิดขึ้นเองตามธรรมชาติ | ผนังแข็งทุกประเภท |
| **ระนาบสมมาตร** | `symmetry` | `symmetry` | สมมาตรแบบสะท้อนรอบ Boundary | การจำลองครึ่งส่วนเพื่อประหยัดพื้นที่ |
| **ผนังเคลื่อนที่** | `movingWallVelocity` | `zeroGradient` | การเคลื่อนที่ของผนังที่กำหนดพร้อมผลกระทบจากความหนืด | แถบเคลื่อนที่, rotor |
| **การไหลอิสระ** | `freestreamVelocity` | `freestreamPressure` | Boundary Condition ระยะไกลสำหรับการไหลภายนอก | อากาศพลศาสตร์ภายนอก |
| **แบบ Cyclic/Periodic** | `cyclic` | `cyclic` | Boundary ของโดเมนแบบ Periodic สำหรับสมมาตร | ช่องทางซ้ำ, heat exchangers |

### หลักการสำคัญในการเลือก

1. **การเลือก Boundary Condition ที่เหมาะสม** สำคัญต่อความแม่นยำและความเสถียรของ CFD Simulations

2. **การจำแนกเป็น Dirichlet, Neumann, และ Robin** เป็นกรอบทางคณิตศาสตร์ที่รับประกัน Well-Posed Problems

3. **การประยุกต์ใช้ใน OpenFOAM** ต้องคำนึงถึง Physical Meaning และ Numerical Stability

4. **Boundary Conditions ขั้นสูง** ช่วยแก้ไขปัญหาที่ซับซ้อนใน Multiphysics และ Special Applications

---

## บทสรุป

**การเลือกและการนำ Boundary Condition ไปใช้อย่างเหมาะสม** เป็นพื้นฐานสำคัญสำหรับการจำลอง CFD ที่แม่นยำ เนื่องจากมีอิทธิพลอย่างมากต่อ:

- **Flow Physics** - ลักษณะการไหลที่เป็นจริง
- **Solution Stability** - ความเสถียรของการคำนวณ
- **Convergence** - การลู่เข้าสู่คำตอบ
- **Physical Accuracy** - ความถูกต้องทางกายภาพ

การเข้าใจและการนำ Boundary Conditions ไปใช้งานอย่างถูกต้องเป็นพื้นฐานสำคัญสำหรับการสร้าง CFD Simulations ที่แม่นยำและเชื่อถือได้ใน OpenFOAM

---

## อ้างอิงต่อเนื่อง

- [[00_Overview]] - ภาพรวมของ Boundary Conditions
- [[01_Introduction]] - บทนับ Boundary Condition ใน OpenFOAM
- [[02_Fundamental_Classification]] - การจำแนกพื้นฐาน
- [[03_Selection_Guide_Which_BC_to_Use]] - คู่มือการเลือก Boundary Condition
- [[05_Common_Boundary_Conditions_in_OpenFOAM]] - Boundary Condition ทั่วไปใน OpenFOAM
- [[06_Advanced_Boundary_Conditions]] - เงื่อนไขขอบเขตขั้นสูง
- [[07_Troubleshooting_Boundary_Conditions]] - การแก้ปัญหา Boundary Conditions
- [[08_Exercises]] - แบบฝึกหัด
