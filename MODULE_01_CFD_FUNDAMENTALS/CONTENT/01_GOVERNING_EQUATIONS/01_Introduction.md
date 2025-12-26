# สมการควบคุมของพลศาสตร์ของไหล: รากฐานทางคณิตศาสต์สำหรับ CFD

## บทนำ

สมการควบคุมของพลศาสตร์ของไหลเป็น **รากฐานทางคณิตศาสต์** ของ Computational Fluid Dynamics (CFD) สมการเหล่านี้อธิบายถึง **การอนุรักษ์มวล, โมเมนตัม, และพลังงาน** ในการไหลของไหล และถูกแก้ปัญหาด้วยวิธีเชิงตัวเลขใน OpenFOAM

## พัฒนาการทางประวัติศาสตร์

รากฐานของพลศาสตร์ของไหลมาจาก **หลักการของกลศาสตร์ตัวกลางต่อเนื่อง** ซึ่งได้รับการพัฒนาอย่างเป็นระบบครั้งแรกโดย Claude-Louis Navier และ George Gabriel Stokes ในช่วงต้นศตวรรษที่ 19

```mermaid
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Theory["Continuum Mechanics<br/>Conservation Laws"]:::context
PDE["Navier-Stokes Equations<br/>Partial Differential Eqns"]:::implicit
FVM["Finite Volume Method<br/>Discretization"]:::explicit
Code["OpenFOAM<br/>Numerical Solution"]:::explicit

Theory --> PDE
PDE --> FVM
FVM --> Code
```
> **Figure 1:** แผนผังแนวคิดที่ไล่เรียงพัฒนาการของ CFD ตั้งแต่หลักการของกลศาสตร์ตัวกลางต่อเนื่องไปจนถึงการ Discretization แบบ Finite Volume และเทคนิคการจับคลื่นกระแทกในปัจจุบัน

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
flowchart TD
    subgraph Forces["Applied Forces on Fluid Element"]
        direction LR
        P["Pressure Forces<br/>-∇p"]:::implicit
        V["Viscous Forces<br/>∇⋅τ"]:::implicit
        B["Body Forces<br/>f"]:::implicit
    end
    
    Sum["Net Force<br/>ΣF = F_pressure + F_viscous + F_body"]:::explicit
    
    P --> Sum
    V --> Sum
    B --> Sum
    
    Sum -->|Newton's 2nd Law: F = ma| Acc["Acceleration<br/>ρ(∂u/∂t + (u⋅∇)u)"]:::volatile
    
    Acc --> Inertia["Inertial Terms<br/>Local + Convective Acceleration"]:::context

classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef volatile fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
```
> **Figure 2:** สมดุลของแรงในสมการ Navier-Stokes แสดงการแยกส่วนของแรงสุทธิออกเป็นแรงดัน แรงหนืด และแรงภายนอกที่เป็นตัวขับเคลื่อนการเคลื่อนที่ของของไหล

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
// Finite Volume discretization in OpenFOAM
// การทำให้เป็นส่วนย่อยด้วย Finite Volume ใน OpenFOAM
fvScalarMatrix TEqn
(
    fvm::ddt(rho, T)                   // Time derivative term
                                        // พจน์อนุพันธ์เทียบกับเวลา
  + fvm::div(phi, T)                   // Convective term (mass/heat transport)
                                        // พจน์การพาความร้อน/มวล
  - fvm::laplacian(k/rho, T)           // Diffusive term (thermal conduction)
                                        // พจน์การแพร่
 ==
    sources/rho                        // Source terms
                                        // พจน์แหล่งกำเนิด
);

TEqn.solve();                          // Solve the linear system
                                        // แก้ระบบสมการเชิงเส้น
```

> **📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystem.H`

> **คำอธิบาย:**
> - `fvm::ddt` - อนุพันธ์เชิงเวลาแบบ implicit (implicit time derivative) สำหรับการแก้ปัญหาแบบ transient
> - `fvm::div` - พจน์การพา (convective term) ที่ถูกทำให้เป็นเชิงเส้นด้วย fvm (finite volume method)
> - `fvm::laplacian` - พจน์การแพร่ (diffusive term) สำหรับการนำความร้อนหรือความหนืด
> - `solve()` - ฟังก์ชันการแก้ระบบสมการเชิงเส้นที่เกิดจากการ discretization
>
> **แนวคิดสำคัญ:**
> - **Finite Volume Method** แบ่งโดเมนเป็น control volumes และใช้ integral form ของสมการอนุรักษ์
> - **Implicit vs Explicit**: fvm (implicit) ใช้สำหรับเสถียรภาพที่ดีกว่าในขณะที่ fvc (explicit) ใช้สำหรับการคำนวณที่รวดเร็ว
> - **Matrix Assembly**: สมการถูกประกอบเป็นระบบเชิงเส้น $Ax=b$ และแก้ด้วย linear solvers

### คลาส Field แบบ Template-Based

OpenFOAM ใช้ **Templated field classes** เพื่อจัดการปริมาณทางกายภาพ:

```cpp
// Field declarations in OpenFOAM
// ตัวอย่างการประกาศ Field ใน OpenFOAM
volScalarField p(mesh);           // Pressure field [Pa]
                                    // Field ความดัน
volVectorField U(mesh);           // Velocity field [m/s]
                                    // Field ความเร็ว
volScalarField T(mesh);           // Temperature field [K]
                                    // Field อุณหภูมิ
surfaceScalarField phi(mesh);     // Flux field [m³/s]
                                    // Field ฟลักซ์
```

> **📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseModel/MovingPhaseModel/MovingPhaseModel.C`

> **คำอธิบาย:**
> - `volScalarField` - สเกลาร์ฟิลด์บนจุดศูนย์กลางของเซลล์ (cell-centered scalar field)
> - `volVectorField` - เวกเตอร์ฟิลด์บนจุดศูนย์กลางของเซลล์ (cell-centered vector field)
> - `surfaceScalarField` - สเกลาร์ฟิลด์บนพื้นผิวเซลล์ (face-centered scalar field) สำหรับฟลักซ์
>
> **แนวคิดสำคัญ:**
> - **Geometric Fields**: OpenFOAM แยกแยะระหว่าง volume fields (ภายในเซลล์) และ surface fields (บนผิวเซลล์)
> - **Mesh Association**: ทุกฟิลด์ต้องถูกผูกกับ mesh object ที่ถูกสร้างขึ้น
> - **Dimensional Consistency**: แต่ละฟิลด์มีหน่วยตามระบบ SI ที่ถูกตรวจสอบโดยระบบ

**การหาอนุพันธ์อัตโนมัติ**:
```cpp
// Automatic derivative calculations in OpenFOAM
// ตัวอย่างการหาอนุพันธ์อัตโนมัติ
volVectorField gradP = fvc::grad(p);              // Pressure gradient [Pa/m]
                                                        // Gradient ความดัน
volScalarField divU = fvc::div(U);                // Velocity divergence [1/s]
                                                        // Divergence ความเร็ว
volTensorField gradU = fvc::grad(U);              // Velocity gradient tensor [1/s]
                                                        // Tensor Gradient ความเร็ว
```

> **📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C`

> **คำอธิบาย:**
> - `fvc::grad` - คำนวณ gradient ของสเกลาร์หรือเวกเตอร์ฟิลด์ด้วย finite volume calculus
> - `fvc::div` - คำนวณ divergence ของเวกเตอร์ฟิลด์บนผิวเซลล์
> - `fvc::` (finite volume calculus) - คำนวณ explicit ที่ให้ค่าจากเวลาก่อนหน้า
>
> **แนวคิดสำคัญ:**
> - **Spatial Discretization**: อนุพันธ์เชิงพื้นที่ถูกประมาณโดยใช้ค่าบนผิวเซลล์
> - **Gauss Theorem**: การแปลง integral บนปริมาตรเป็น integral บนผิวเพื่อการคำนวณ
> - **Mesh Non-Orthogonality**: ความแม่นยำขึ้นกับคุณภาพของ mesh โดยเฉพาะมุมฉาก

### Time Discretization Schemes

OpenFOAM รองรับ Time discretization ที่หลากหลาย:

| Scheme | ความแม่นยำ | ประเภท | ข้อดี | เหมาะสำหรับ |
|--------|------------|---------|--------|-------------|
| Euler | อันดับหนึ่ง | Explicit/Implicit | เสถียร, ง่าย | Transient problems ทั่วไป |
| Crank-Nicolson | อันดับสอง | Implicit | ความแม่นยำสูง | ปัญหาที่ต้องการความแม่นยำ |
| Backward | อันดับสอง | Implicit | เสถียรมาก | Stiff problems |

**การตั้งค่าใน OpenFOAM**:
```cpp
// Time discretization scheme selection
// การเลือก Time scheme
ddtSchemes
{
    default         Euler;               // First-order scheme
                                        // อันดับหนึ่ง
    // default        CrankNicolson 0.9;  // Second-order blended scheme
                                        // อันดับสองแบบผสม
    // default        backward;            // Second-order scheme
                                        // อันดับสอง
}
```

> **📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystem.C`

> **คำอธิบาย:**
> - `Euler` - วิธีอันดับหนึ่งที่ใช้ค่าที่ time step ก่อนหน้า เสถียรแต่ความแม่นยำต่ำ
> - `CrankNicolson` - วิธีอันดับสองที่ใช้ค่าถ่วงน้ำหนักระหว่าง time steps ให้ความแม่นยำสูง
> - `backward` - วิธีอันดับสองที่เสถียรสำหรับปัญหา stiff
>
> **แนวคิดสำคัญ:**
> - **Temporal Accuracy**: อันดับของความแม่นยำสัมพันธ์กับความละเอียดเชิงเวลา
> - **CFL Condition**: ข้อจำกัดของขนาด time step สำหรับ explicit schemes
> - **Implicit vs Explicit**: Implicit schemes เสถียรกว่าแต่ต้องการแก้ระบบสมการ

---

## คุณสมบัติทางคณิตศาสตร์และกลยุทธ์การแก้ปัญหา

### ความไม่เป็นเชิงเส้น

**พจน์ Convective** $(\mathbf{u} \cdot \nabla)\mathbf{u}$ ทำให้เกิด **ความไม่เป็นเชิงเส้น** ซึ่งต้องใช้วิธีการแก้ปัญหาแบบวนซ้ำ:

```cpp
// Nonlinear term treatment in momentum equation
// การจัดการพจน์ไม่เป็นเชิงเส้น
fvVectorMatrix UEqn
(
    fvm::ddt(rho, U)                              // Time derivative
                                                    // อนุพันธ์เทียบกับเวลา
  + fvm::div(phi, U)                              // Linearized convective term
                                                    // พจน์การพาที่ทำให้เป็นเชิงเส้น
  + fvc::div((rho*phi), U)                         // Explicit convective term
                                                    // พจน์การพาแบบ explicit
  - fvm::Sp(fvc::div(phi*rho), U)                 // Source term linearization
                                                    // การทำให้เป็นเชิงเส้นของพจน์แหล่งกำเนิด
);
```

> **📂 Source:** `.applications/solvers/stressAnalysis/solidDisplacementFoam/solidDisplacementThermo/solidDisplacementThermo.C`

> **คำอธิบาย:**
> - `fvm::div` - ประมาณค่าพจน์การพาแบบ implicit เพื่อความเสถียร
> - `fvc::div` - คำนวณพจน์การพาแบบ explicit จาก time step ก่อนหน้า
> - `fvm::Sp` - ประมาณค่าพจน์แหล่งกำเนิดเป็นเชิงเส้น $S \approx S^* + (\partial S/\partial \phi)(\phi - \phi^*)$
>
> **แนวคิดสำคัญ:**
> - **Linearization**: การทำให้เป็นเชิงเส้นของสมการที่ไม่เป็นเชิงเส้นด้วยการใช้ค่าจาก iteration ก่อนหน้า
> - **Under-Relaxation**: การใช้ factor ในการปรับค่าใหม่เพื่อความเสถียรของการวนซ้ำ
> - **Picard Iteration**: วิธีการแก้ปัญหาแบบวนซ้ำสำหรับสมการไม่เป็นเชิงเส้น

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
// SIMPLE algorithm implementation
// อัลกอริทึม SIMPLE
while (simple.correctNonOrthogonal())
{
    // Momentum equation
    // สมการโมเมนตัม
    tmp<fvVectorMatrix> UEqn(fvm::ddt(U) + fvm::div(phi, U));
    UEqn().relax();                              // Under-relaxation for stability
                                                // การประณีตค่าเพื่อความเสถียร

    // Pressure equation
    // สมการความดัน
    adjustPhi(phi, U, p);                       // Adjust fluxes for continuity
                                                // ปรับฟลักซ์เพื่อความต่อเนื่องของมวล

    // Pressure-velocity coupling loop
    // ลูปการเชื่อมโยงความดัน-ความเร็ว
    for (int corr = 0; corr < nCorr; corr++)
    {
        // Solve momentum equation
        // แก้โมเมนตัม
        solve(UEqn() == -fvc::grad(p));         // Momentum predictor
                                                // ตัวพยากรณ์โมเมนตัม

        // Solve pressure correction equation
        // แก้ความดัน
        solve(fvm::laplacian(rAU, p) == fvc::div(phi));  // Pressure correction
                                                        // การแก้ไขความดัน
    }
}
```

> **📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C`

> **คำอธิบาย:**
> - `correctNonOrthogonal()` - วนซ้ำเพื่อจัดการ mesh ที่ไม่ใช่ orthoghonal และปรับปรุงความแม่นยำ
> - `relax()` - ใช้ under-relaxation factor เพื่อป้องกันการ oscillate ในการแก้ปัญหา
> - `adjustPhi()` - ปรับ flux บนผิวเซลล์ให้สอดคล้องกับสมการความต่อเนื่อง
> - `solve()` - แก้ระบบสมการเชิงเส้นสำหรับความดัน
>
> **แนวคิดสำคัญ:**
> - **Segregated Solution**: แก้สมการแยกกันและวนซ้ำจนถึงการลู่เข้า
> - **Pressure Correction**: แก้ไขความดันให้สอดคล้องกับสมการความต่อเนื่องของมวล
> - **Under-Relaxation**: ใช้ค่าน้อยกว่า 1 (0.3-0.7) สำหรับโมเมนตัมและความดันเพื่อความเสถียร

```mermaid
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Start(("Start")):::context
Pred["Momentum Predictor<br/>Solve U (guessed p)"]:::explicit
Corr["Pressure Corrector<br/>Solve pEqn (Mass Cont.)"]:::explicit
Update["Update Fields<br/>Correct U & Fluxes"]:::explicit
Check{"Converged?"}:::implicit
End(("End")):::context

Start --> Pred
Pred --> Corr
Corr --> Update
Update --> Check
Check -- No --> Pred
Check -- Yes --> End
```
> **Figure 3:** แผนผังลำดับขั้นตอนของอัลกอริทึม SIMPLE สำหรับการเชื่อมโยงความดันและความเร็วในสภาวะคงตัว แสดงวงรอบการแก้ไขแบบวนซ้ำที่จำเป็นสำหรับ Solver ของการไหลแบบอัดตัวไม่ได้

### Boundary Conditions

การกำหนด **Boundary Conditions** ที่เหมาะสมเป็นสิ่งสำคัญ:

```cpp
// Boundary condition specification
// ตัวอย่าง Boundary Condition
dimensions      [0 2 -2 0 0 0 0];               // Pressure dimensions [kg/(m·s²)]
                                                    // มิติของความดัน

internalField   uniform 0;                       // Initial field value
                                                    // ค่าเริ่มต้นของฟิลด์

boundaryField
{
    inlet
    {
        type            fixedValue;              // Fixed value boundary
                                                    // ค่าคงที่
        value           uniform (10 0 0);        // Inlet velocity [m/s]
                                                    // ทางเข้าความเร็ว
    }

    outlet
    {
        type            zeroGradient;            // Zero gradient (Neumann)
                                                    // ทางออก
    }

    walls
    {
        type            noSlip;                  // No-slip condition
                                                    // ผนังแบบ No-slip
    }

    symmetry
    {
        type            symmetry;                // Symmetry plane
                                                    // ระนาบสมมาตร
    }
}
```

> **📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C`

> **คำอธิบาย:**
> - `fixedValue` - กำหนดค่าคงที่บนผิว (Dirichlet boundary condition)
> - `zeroGradient` - อนุพันธ์เทียบกับปกติเป็นศูนย์ (Neumann boundary condition)
> - `noSlip` - ความเร็วเป็นศูนย์บนผิว (no-slip condition)
> - `symmetry` - เงื่อนไขสมมาตรที่สะท้อนค่าข้ามเคียง
>
> **แนวคิดสำคัญ:**
> - **Well-Posed Problem**: ต้องมี boundary conditions เพียงพอและสอดคล้องกัน
> - **Dirichlet vs Neumann**: Dirichlet กำหนดค่าโดยตรง Neumann กำหนดอนุพันธ์
> - **Physical Consistency**: boundary conditions ต้องสอดคล้องกับฟิสิกส์ของปัญหา

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
graph TB
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
subgraph Laminar["Laminar Flow"]
    L_Char["Re < Re_crit<br/>Orderly Streamlined"]:::implicit
    L_Math["Direct Navier-Stokes<br/>No Modeling Required"]:::implicit
    L_Char --> L_Math
end

subgraph Turbulent["Turbulent Flow"]
    T_Char["Re > Re_crit<br/>Chaotic Mixing"]:::explicit
    T_Math["RANS / LES<br/>Turbulence Modeling Required"]:::explicit
    T_Char --> T_Math
end
```
> **Figure 4:** ความแตกต่างระหว่างการไหลแบบราบเรียบ (Laminar) และแบบปั่นป่วน (Turbulent) โดยเปรียบเทียบพฤติกรรมของเส้นกระแสและแนวทางทางคณิตศาสตร์ที่เกี่ยวข้อง (ผลเฉลยโดยตรง เทียบกับการสลายตัวแบบเรย์โนลด์) ที่ใช้ในการจำลอง

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