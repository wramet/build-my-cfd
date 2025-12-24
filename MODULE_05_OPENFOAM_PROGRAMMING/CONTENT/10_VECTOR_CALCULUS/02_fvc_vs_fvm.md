# fvc vs fvm: แตกต่างกันอย่างไร?

![[explicit_calculator_vs_implicit_architect.png]]
> **Academic Vision:** A split screen. On the left (fvc), a calculator producing a direct number. On the right (fvm), an architect drawing a complex blueprint (The Matrix) of a building that hasn't been built yet. Clean, high-contrast flat design.

ใน OpenFOAM การดำเนินการทางแคลคูลัสเวกเตอร์มีอยู่ในรูปแบบพื้นฐานสองรูปแบบ:

- **`fvc::` (Finite Volume Calculus)**: การดำเนินการ **ชัดแจ้ง (Explicit)** ที่คำนวณค่าโดยตรงจากข้อมูล field ใช้สำหรับ source terms, post-processing, และการคำนวณที่ต้องการค่าทันที
- **`fvm::` (Finite Volume Method)**: การดำเนินการ **โดยนัย (Implicit)** ที่สร้างค่าสัมประสิทธิ์เมทริกซ์สำหรับระบบเชิงเส้น ใช้สำหรับแก้สมการเชิงอนุพันธ์เพื่อหาค่า Unknown

---

## 📊 ภาพรวมการดำเนินการ Explicit กับ Implicit

```mermaid
flowchart TD
    subgraph fvc_Explicit["fvc:: Explicit Operations"]
        D1["Data Known<br/>(Field Values)"] --> C["fvc::Operation<br/>(Calculate Now)"]
        C --> R["Result: Field Value<br/>(Immediate Output)"]
    end

    subgraph fvm_Implicit["fvm:: Implicit Operations"]
        D2["Data Unknown<br/>(Future Values)"] --> M["fvm::Operation<br/>(Build Matrix)"]
        M --> Mat["Result: fvMatrix<br/>(A·x = b system)"]
        Mat --> S["Linear Solver<br/>(GAMG, PCG, etc.)"]
        S --> R2["Result: Future Value<br/>(After Solve)"]
    end

    style fvc_Explicit fill:#e3f2fd,stroke:#2196f3
    style fvm_Implicit fill:#fff3e0,stroke:#ff9800
```
> **Figure 1:** การเปรียบเทียบกระบวนการทำงานระหว่างการคำนวณแบบ Explicit (fvc::) ที่ให้ผลลัพธ์ทันที กับการคำนวณแบบ Implicit (fvm::) ที่สร้างระบบสมการเมทริกซ์เพื่อหาค่าในอนาคตความปลอดภัยทางฟิสิกส์ไม่ส่งผลกระทบต่อความเร็วในการจำลอง ผ่านการใช้พลังของ C++ Template Metaprogramming ในการตรวจสอบความสอดคล้องทางมิติทั้งหมดที่ขั้นตอนการคอมไพล์โปรแกรมเพียงครั้งเดียว

---

## 🎯 ตารางเปรียบเทียบความแตกต่าง

| หัวข้อเปรียบเทียบ | `fvc` (Explicit) | `fvm` (Implicit) |
|:---|:---|:---|
| **ผลลัพธ์ที่ได้** | ค่าตัวเลข (Fields) | เมทริกซ์ระบบสมการ (`fvMatrix`) |
| **ความหมาย** | "จงคำนวณค่านี้ให้ฉันเดี๋ยวนี้" | "จงสร้างสมการเพื่อหาค่านี้ให้ฉัน" |
| **การลู่เข้า (Stability)** | ขึ้นกับขนาดก้าวเวลา (เสถียรน้อยกว่า) | เสถียรกว่ามาก (รองรับก้าวเวลาใหญ่ได้) |
| **ตัวอย่างฟังก์ชัน** | `fvc::grad`, `fvc::div`, `fvc::flux`, `fvc::laplacian` | `fvm::ddt`, `fvm::div`, `fvm::laplacian` |
| **การใช้หน่วยความจำ** | น้อยกว่า | มากกว่า (เก็บเมทริกซ์) |
| **ประสิทธิภาพต่อการวนซ้ำ** | เร็วกว่า | ช้ากว่า (ต้อง solve) |
| **ข้อจำกัด Time Step** | CFL: $\Delta t \leq \frac{\Delta x^2}{2\Gamma}$ | เสถียรโดยไม่มีเงื่อนไข |

---

## ⚙️ กฎการเลือกใช้งาน

> [!TIP] กฎทองคำในการเลือกใช้ fvc หรือ fvm
>
> - หากตัวแปรนั้นคือ **คำตอบที่เรากำลังหา** $\rightarrow$ ใช้ **`fvm`** (เพื่อให้สมการเป็นแบบ Implicit)
> - หากตัวแปรนั้นคือ **ค่าคงที่หรือค่าที่รู้แล้ว** จากขั้นตอนก่อนหน้า $\rightarrow$ ใช้ **`fvc`** (เพื่อคำนวณเป็นสัมประสิทธิ์หรือเทอม Source)

### ตัวอย่างในโซลเวอร์

```cpp
// Calculate flux (phi) from current velocity (Explicit)
// คำนวณฟลักซ์จากความเร็วปัจจุบันแบบชัดแจ้ง
phi = fvc::flux(U);

// Build energy equation to find new T (Implicit)
// สร้างสมการพลังงานเพื่อหาค่า T ใหม่แบบโดยนัย
fvScalarMatrix TEqn(
    fvm::ddt(T)
  + fvm::div(phi, T)
 == fvm::laplacian(DT, T)
);
TEqn.solve();
```

**📖 คำอธิบาย (Thai Explanation):**

**Source/Explanation:**
- บรรทัดแรกใช้ `fvc::flux(U)` เพื่อคำนวณ face flux จาก velocity field ปัจจุบัน เนื่องจาก U เป็นค่าที่รู้แล้ว
- ส่วนที่สองสร้างสมการพลังงานโดยใช้ `fvm::ddt()`, `fvm::div()`, และ `fvm::laplacian()` เพื่อสร้างเมทริกซ์สมการที่จะหาค่า T ใหม่

**Key Concepts:**
- **Explicit Calculation**: การคำนวณที่ให้ผลลัพธ์ทันทีจากค่าที่รู้แล้ว
- **Implicit Formulation**: การสร้างระบบสมการเชิงเส้นเพื่อหาค่าที่ยังไม่รู้
- **fvMatrix**: เมทริกซ์ระบบสมการ A·x = b ที่ต้องถูกแก้ด้วย linear solver

**📂 Source:** .applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystem.C

---

## 🔬 รายละเอียดการดำเนินการแบบ Explicit (`fvc::`)

### แนวคิดพื้นฐาน

การดำเนินการ Explicit ประเมินค่าโดยใช้ข้อมูลจากการวนซ้ำปัจจุบันหรือ time step ปัจจุบัน ส่งผลให้เกิดค่าที่คำนวณได้ทันที

### ลักษณะเฉพาะ

- **ใช้ค่าสนามปัจจุบันโดยตรง**
- **สร้างพจน์ explicit (ย้ายไป RHS)**
- **ไม่มีการ coupling ระหว่างเซลล์ข้างเคียง**
- **ข้อจำกัดด้าน time step อาจเข้มงวด**
- **ใช้ทรัพยากรการคำนวณน้อยต่อการประเมิน**

### การดำเนินการ Explicit ทั่วไป

```cpp
// === Gradient Operations ===
// Pressure gradient (driving force in momentum equation)
// กราดิเอนต์ของความดัน - แรงขับเคลื่อนในสมการโมเมนตัม
volVectorField gradP = fvc::grad(p);

// Temperature gradient (for heat flux calculation)
// กราดิเอนต์ของอุณหภูมิ - สำหรับคำนวณความร้อน
volVectorField gradT = fvc::grad(T);

// === Divergence Operations ===
// Divergence of velocity field (continuity equation)
// ไดเวอร์เจนซ์ของสนามความเร็ว - สมการต่อเนื่อง
volScalarField divU = fvc::div(U);

// Divergence of flux (source term in momentum equation)
// ไดเวอร์เจนซ์ของฟลักซ์ - เทอมต้นทางในสมการโมเมนตัม
volScalarField divPhi = fvc::div(phi);

// === Laplacian Operations ===
// Thermal diffusion
// การแพร่ของความร้อน
volScalarField laplacianT = fvc::laplacian(DT, T);

// Viscous diffusion
// การแพร่ของความหนืด
volVectorField laplacianU = fvc::laplacian(nu, U);

// === Curl Operations ===
// Vorticity field
// สนามวอร์ติซิตี้ (การหมุนของไหล)
volVectorField vorticity = fvc::curl(U);

// === Flux Operations ===
// Face flux field
// สนามฟลักซ์ที่ผิวเซลล์
surfaceScalarField phi = fvc::flux(U);

// Mass flow rate
// อัตราการไหลของมวล
surfaceScalarField rhoPhi = fvc::flux(rho, U);

// === Surface Normal Gradients ===
// Normal gradient at faces
// กราดิเอนต์ตั้งฉากที่ผิวเซลล์
surfaceScalarField snGradT = fvc::snGrad(T);

// === Temporal Derivatives ===
// Time derivative using Euler scheme
// อนุพันธ์เวลาโดยใช้รูปแบบออยเลอร์
volScalarField ddtT = fvc::ddt(T);
```

**📖 คำอธิบาย (Thai Explanation):**

**Source/Explanation:**
- **Gradient Operations**: คำนวณอนุพันธ์เชิงพื้นที่ของสนามต่างๆ เช่น กราดิเอนต์ความดันใช้หาแรงขับเคลื่อน
- **Divergence Operations**: คำนวณการไหลออก (outflow) จากแต่ละเซลล์ ใช้ตรวจสอบการอนุรักษ์มวล
- **Laplacian Operations**: คำนวณเทอมการแพร่ (diffusion) เช่น ความร้อนและความหนืด
- **Curl Operations**: คำนวณการหมุนของไหล (vorticity) สำคัญในการวิเคราะห์กระแส
- **Flux Operations**: คำนวณอัตราการไหลผ่านผิวเซลล์ ใช้ในการคำนวณมวลและโมเมนตัม

**Key Concepts:**
- **Explicit Evaluation**: การคำนวณค่าทันทีจากข้อมูลปัจจุบัน
- **Field Interpolation**: การแปลงค่าจาก cell center ไปยัง face centers
- **Gauss Theorem**: ใช้ทฤษฎีบทของเกาส์ในการแปลงปริมาตรเป็นพื้นผิว
- **Immediate Results**: ผลลัพธ์พร้อมใช้งานทันทีโดยไม่ต้องแก้สมการ

**📂 Source:** .applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C

### ข้อดีและข้อเสีย

| ข้อดี | ข้อเสีย |
|:---|:---|
| • ง่ายต่อการ implement<br/>• ใช้หน่วยความจำน้อย<br/>• เร็วต่อการคำนวณแต่ละครั้ง | • ข้อจำกัดความเสถียรที่เข้มงวด<br/>• ต้องการ time step เล็กๆ<br/>• อาจมี numerical diffusion |

---

## 🏗️ รายละเอียดการดำเนินการแบบ Implicit (`fvm::`)

### แนวคิดพื้นฐาน

การดำเนินการ Implicit สร้างระบบสมการที่ coupled โดยค่าสนามที่ไม่รู้ปรากฏในทั้งด้านซ้ายมือ (สัมประสิทธิ์เมทริกซ์) และด้านขวามือ (พจน์ต้นทาง)

### ลักษณะเฉพาะ

- **สร้างพจน์ implicit (สัมประสิทธิ์เมทริกซ์)**
- **Coupling เซลล์ข้างเคียงผ่านพจน์ off-diagonal**
- **อนุญาต time step ที่ใหญ่ขึ้นสำหรับความเสถียร**
- **ต้องการการแก้ระบบสมการเชิงเส้น**
- **ใช้ทรัพยากรการคำนวณมากขึ้นต่อการวนซ้ำ**

### การดำเนินการ Implicit ทั่วไป

```cpp
// === Temporal Integration ===
// Forward Euler (implicit)
// อินทิเกรชันเวลาแบบออยเลอร์แบบโดยนัย
fvScalarMatrix TEqn(fvm::ddt(T));

// Backward scheme (second-order)
// รูปแบบแบ็ควอร์ด อันดับสอง
fvScalarMatrix TEqn(fvm::ddt(T, backward));

// === Diffusion Terms ===
// Thermal diffusion
// การแพร่ของความร้อน
fvScalarMatrix TEqn(fvm::laplacian(DT, T));

// Viscous diffusion
// การแพร่ของความหนืด
fvVectorMatrix UEqn(fvm::laplacian(nu, U));

// === Convective Terms ===
// Upwind convection
// การพาแบบอัปวินด์
fvVectorMatrix UEqn(fvm::div(phi, U));

// === Combined Terms ===
// Energy equation
// สมการพลังงาน
fvScalarMatrix TEqn
(
    fvm::ddt(T)
  + fvm::div(phi, T)
  - fvm::laplacian(DT, T)
);

// Momentum equation
// สมการโมเมนตัม
fvVectorMatrix UEqn
(
    fvm::ddt(U)
  + fvm::div(phi, U)
  - fvm::laplacian(nu, U)
 ==
  -fvc::grad(p)
);
```

**📖 คำอธิบาย (Thai Explanation):**

**Source/Explanation:**
- **Temporal Integration**: `fvm::ddt()` สร้างเมทริกซ์สำหรับอนุพันธ์เวลาแบบโดยนัย ทำให้สามารถใช้ time step ที่ใหญ่ขึ้น
- **Diffusion Terms**: `fvm::laplacian()` สร้างเมทริกซ์การแพร่แบบโดยนัย สำคัญมากสำหรับความเสถียร
- **Convective Terms**: `fvm::div()` สร้างเมทริกซ์การพาแบบโดยนัย สร้าง coupling ระหว่างเซลล์ข้างเคียง
- **Mixed Treatment**: สมการโมเมนตัมใช้ `fvm` สำหรับเทอมที่ต้องการคำตอบ (U) แต่ใช้ `fvc::grad(p)` เพราะความดันเป็นค่าที่รู้

**Key Concepts:**
- **Matrix Assembly**: การประกอบเมทริกซ์ระบบสมการ A·x = b
- **Cell Coupling**: การเชื่อมโยงระหว่างเซลล์ข้างเคียงผ่าน off-diagonal coefficients
- **Linear Solvers**: การแก้ระบบสมการโดยใช้ GAMG, PCG, หรือ BiCGStab
- **Unconditional Stability**: ความเสถียรโดยไม่มีเงื่อนไขจำกัด time step
- **fvMatrix Type**: ประเภทข้อมูลเมทริกซ์ใน OpenFOAM (fvScalarMatrix, fvVectorMatrix)

**📂 Source:** .applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C

### ข้อดีและข้อเสีย

| ข้อดี | ข้อเสีย |
|:---|:---|
| • เสถียรกว่ามาก<br/>• รองรับ time step ใหญ่ได้<br/>• เหมาะกับ stiff problems | • ซับซ้อนกว่าในการ implement<br/>• ใช้หน่วยความจำมากขึ้น<br/>• ช้ากว่าต่อการวนซ้ำ |

---

## 📐 รากฐานทางคณิตศาสตร์

### Finite Volume Discretization

การดำเนินการทั้งสองแบบใช้หลักการเดียวกันจากทฤษฎีบทของ Gauss:

#### Gradient Operator

$$\nabla \phi = \frac{1}{V} \sum_{faces} \phi_f \mathbf{S}_f$$

โดยที่:
- $V$ คือปริมาตรของ cell
- $\phi_f$ คือค่าที่ face (interpolated)
- $\mathbf{S}_f$ คือเวกเตอร์พื้นที่ของ face

#### Divergence Operator

$$\nabla \cdot \mathbf{\phi} = \frac{1}{V} \sum_{faces} \mathbf{\phi}_f \cdot \mathbf{S}_f$$

#### Laplacian Operator

$$\nabla \cdot (\Gamma \nabla \psi) = \frac{1}{V} \sum_{faces} \Gamma_f (\nabla \psi)_f \cdot \mathbf{S}_f$$

โดยที่:
- $\Gamma$ คือสัมประสิทธิ์การ diffused
- $(\nabla \psi)_f$ คือ gradient ที่ face

---

## 🔄 รูปแบบผสมและการผ่อนคลาย

ในทางปฏิบัติ มักใช้การผสมผสานระหว่าง explicit และ implicit

### การรักษาพาความร้อนแบบกึ่ง-implicit

```cpp
// Semi-implicit convection treatment
// การรักษาการพาแบบกึ่ง-โดยนัย
fvScalarMatrix TEqn
(
    fvm::ddt(T)
  + fvm::div(phi, T)           // Implicit part (ส่วนโดยนัย)
  - fvc::div(phi_implicit, T)  // Explicit correction (ส่วนชัดแจ้ง)
);
```

**📖 คำอธิบาย (Thai Explanation):**

**Source/Explanation:**
- ใช้ `fvm::div()` เพื่อสร้างเมทริกซ์ส่วนหลักที่เสถียร
- ใช้ `fvc::div()` เพื่อเพิ่มการแก้ไขแบบ explicit เพื่อเพิ่มความแม่นยำ
- เทคนิคนี้ใช้ในสถานการณ์ที่ต้องการทั้งความเสถียรและความแม่นยำ

**Key Concepts:**
- **Semi-Implicit Scheme**: รูปแบบกึ่งโดยนัยที่รวมข้อดีของทั้งสองแนวทาง
- **Under-Relaxation**: การผ่อนคลายเพื่อเพิ่มความเสถียรของการวนซ้ำ
- **Numerical Stability vs Accuracy**: การแลกเปลี่ยนระหว่างความเสถียรและความแม่นยำ

**📂 Source:** .applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C

### การผ่อนคลายสำหรับความเสถียร

```cpp
// Under-relaxation for stability
// การผ่อนคลายเพื่อความเสถียร
TEqn.relax(relaxationFactor);
TEqn.solve();
```

**📖 คำอธิบาย (Thai Explanation):**

**Source/Explanation:**
- `relax()` ผ่อนคลายเมทริกซ์เพื่อป้องกันการสั่นของการแก้ปัญหา
- `relaxationFactor` ค่าระหว่าง 0 ถึง 1 ยิ่งต่ำยิ่งเสถียรแต่ช้ากว่า

**Key Concepts:**
- **Relaxation Factor**: ค่าปัจจัยการผ่อนคลาย ค่ามาตรฐานคือ 0.7-0.9
- **Convergence Control**: การควบคุมการลู่เข้าของการวนซ้ำ
- **Stability Enhancement**: การเพิ่มความเสถียรในการแก้ปัญหา

**📂 Source:** .applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C

---

## 🌊 การประยุกต์ใช้อัลกอริทึม PISO

อัลกอริทึม PISO (Pressure-Implicit with Splitting of Operators) แสดงให้เห็นการใช้งานร่วมกันของ fvc และ fvm อย่างชัดเจน

```mermaid
flowchart LR
    A["Momentum Prediction<br/>(Implicit: fvm::div, fvm::laplacian)"] --> B["Flux Calculation<br/>(Explicit: fvc::interpolate)"]
    B --> C["Pressure Equation<br/>(Implicit: fvm::laplacian)"]
    C --> D["Velocity Correction<br/>(Explicit: fvc::grad)"]
    D --> E{Converged?}
    E -->|No| C
    E -->|Yes| F["Next Time Step"]
```
> **Figure 2:** ขั้นตอนการทำงานของอัลกอริทึม PISO ซึ่งแสดงให้เห็นถึงการใช้งานร่วมกันอย่างมีประสิทธิภาพระหว่างตัวดำเนินการแบบ Explicit และ Implicit ในการแก้ปัญหาความดันและความเร็วความปลอดภัยทางฟิสิกส์ไม่ส่งผลกระทบต่อความเร็วในการจำลอง ผ่านการใช้พลังของ C++ Template Metaprogramming ในการตรวจสอบความสอดคล้องทางมิติทั้งหมดที่ขั้นตอนการคอมไพล์โปรแกรมเพียงครั้งเดียว

### Step-by-Step PISO Algorithm

#### 1. Momentum Prediction (Implicit)

```cpp
// Momentum prediction (implicit)
// การทำนายโมเมนตัมแบบโดยนัย
fvVectorMatrix UEqn
(
    fvm::ddt(U)
  + fvm::div(phi, U)
  - fvm::laplacian(nu, U)
);
UEqn.solve();
```

**📖 คำอธิบาย (Thai Explanation):**

**Source/Explanation:**
- ใช้ `fvm` ทั้งหมดเพื่อสร้างเมทริกซ์โมเมนตัมแบบโดยนัย
- เมทริกซ์นี้จะถูกแก้เพื่อหาค่า U ใหม่
- ความเสถียรสูงเนื่องจากเป็นการรักษาแบบโดยนัย

**Key Concepts:**
- **Momentum Matrix**: เมทริกซ์สมการโมเมนตัม A·U = b
- **Implicit Discretization**: การกระจายตัวแบบโดยนัยของเทอมต่างๆ
- **Matrix Coefficients**: สัมประสิทธิ์เมทริกซ์ที่เชื่อมโยงเซลล์ข้างเคียง

**📂 Source:** .applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C

#### 2. Pressure-Velocity Coupling (Explicit)

```cpp
// Pressure-velocity coupling (explicit)
// การเชื่อมโยงความดันและความเร็วแบบชัดแจ้ง
volScalarField rUA = 1.0/UEqn.A();
surfaceScalarField rUAf = fvc::interpolate(rUA);
surfaceScalarField phiHbyA = (UEqn.H() & UEqn.flux()) / UEqn.A();
```

**📖 คำอธิบาย (Thai Explanation):**

**Source/Explanation:**
- `UEqn.A()` ดึง diagonal coefficients จากเมทริกซ์
- `UEqn.H()` ดึง source terms จากเมทริกซ์
- `fvc::interpolate()` แปลงค่าจาก cell center ไปยัง face centers

**Key Concepts:**
- **Matrix Diagonal**: ค่า diagonal ของเมทริกซ์ (A)
- **Source Terms**: เทอมต้นทางจากเมทริกซ์ (H)
- **Interpolation**: การแปลงค่าจากจุดกลางเซลล์ไปยังผิวเซลล์
- **Rhie-Chow Interpolation**: เทคนิคการแปลงเพื่อป้องกัน pressure-velocity decoupling

**📂 Source:** .applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C

#### 3. Pressure Equation (Implicit)

```cpp
// Pressure equation (implicit)
// สมการความดันแบบโดยนัย
fvScalarMatrix pEqn
(
    fvm::laplacian(rUAf, p) == fvc::div(phiHbyA)
);
pEqn.solve();
```

**📖 คำอธิบาย (Thai Explanation):**

**Source/Explanation:**
- `fvm::laplacian()` สร้างเมทริกซ์ความดันแบบโดยนัย
- `fvc::div()` คำนวณเทอมต้นทางจากฟลักซ์ที่ทำนายไว้
- สมการนี้จะถูกแก้เพื่อหาค่าความดันใหม่

**Key Concepts:**
- **Pressure Poisson Equation**: สมการ Poisson สำหรับความดัน
- **Mass Conservation**: การอนุรักษ์มวลผ่านสมการความดัน
- **Pressure Correction**: การแก้ไขความดันเพื่อให้สอดคล้องกับความต่อเนื่อง

**📂 Source:** .applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C

#### 4. Velocity Correction (Explicit)

```cpp
// Velocity correction (explicit)
// การแก้ไขความเร็วแบบชัดแจ้ง
U -= rUA * fvc::grad(p);
```

**📖 คำอธิบาย (Thai Explanation):**

**Source/Explanation:**
- `fvc::grad(p)` คำนวณกราดิเอนต์ของความดัน
- ความเร็วถูกแก้ไขโดยลบกราดิเอนต์ความดัน
- เป็นการแก้ไขแบบ explicit จากความดันที่หาได้

**Key Concepts:**
- **Velocity Update**: การอัปเดตความเร็วจากความดัน
- **Pressure Gradient Force**: แรงจากกราดิเอนต์ความดัน
- **Mass Conservation Enforcement**: การบังคับให้สอดคล้องกับการอนุรักษ์มวล

**📂 Source:** .applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C

---

## 📋 ตารางเปรียบเทียบเชิงลึก

| ปัจจัย | Explicit (`fvc::`) | Implicit (`fvm::`) |
|:---|:---|:---|
| **ความเสถียร** | Time step จำกัด | เสถียรโดยไม่มีเงื่อนไข |
| **ความแม่นยำ** | อันดับสูงกว่าได้ | มักเป็นอันดับแรก/ที่สอง |
| **ต้นทุนการคำนวณ** | ต่ำต่อการวนซ้ำ | สูงกว่าต่อการวนซ้ำ |
| **หน่วยความจำ** | จัดเก็บน้อยกว่า | ต้องการจัดเก็บเมทริกซ์ |
| **การบรรจบกัน** | อาจต้องการการวนซ้ำหลายครั้ง | การวนซ้ำน้อยกว่าสำหรับ steady state |
| **Complexity** | ง่าย | ซับซ้อน |
| **การใช้งานทั่วไป** | Post-processing, Source terms | Diffusion, Pressure-velocity coupling |

---

## 💡 แนวทางปฏิบัติที่ดี

> [!INFO] Best Practices ในการเลือกใช้ fvc และ fvm
>
> - **ใช้ `fvm::`** สำหรับการแพร่, coupling ความดัน-ความเร็ว, และพจน์ต้นทางแบบ stiff
> - **ใช้ `fvc::`** สำหรับการพาความร้อนเมื่อใช้รูปแบบ explicit หรือการประมาณค่าเชิงอันดับสูง
> - **รวมทั้งสอง** เพื่อสมดุลที่เหมาะสมที่สุด: การรักษาพจน์ stiff แบบ implicit, แบบ explicit สำหรับพจน์ที่ไม่ stiff
> - **พิจารณา trade-offs** ระหว่างการแพร่เชิงตัวเลขและต้นทุนการคำนวณ
> - **ทดสอบความไวต่อ time step** เมื่อใช้การดำเนินการ explicit

---

## 🧪 การประยุกต์ใช้ใน Solver จริง

### สมการโมเมนตัม

```cpp
// Momentum equation with mixed explicit/implicit
// สมการโมเมนตัมที่มีทั้งชัดแจ้งและโดยนัย
fvVectorMatrix UEqn
(
    fvm::ddt(rho, U)              // Implicit time derivative (อนุพันธ์เวลาโดยนัย)
  + fvm::div(rhoPhi, U)           // Implicit convection (การพาโดยนัย)
 ==
  - fvc::grad(p)                  // Explicit pressure gradient (กราดิเอนต์ความดันชัดแจ้ง)
  + fvc::div(tau)                 // Explicit viscous stress (เครียงดันหนืดชัดแจ้ง)
  + fvOptions(rho, U)             // Source terms (เทอมต้นทาง)
);

UEqn.relax();
UEqn.solve();
```

**📖 คำอธิบาย (Thai Explanation):**

**Source/Explanation:**
- เลือกใช้ `fvm` สำหรับเทอมที่เกี่ยวกับ U (ตัวแปรที่หา) เพื่อความเสถียร
- ใช้ `fvc` สำหรับความดันและเครียงดันเพราะเป็นค่าที่รู้หรือคำนวณแยก
- `fvOptions` ใช้เพิ่มเทอมต้นทางเช่นแรงโน้มถ่วงหรือแหล่งกำเนิด

**Key Concepts:**
- **Implicit-Explicit Split**: การแยกส่วนโดยนัยและชัดแจ้งของสมการ
- **Coupled Variables**: ตัวแปรที่เชื่อมโยงกันในสมการ
- **Source Terms**: เทอมต้นทางเช่นแรงภายนอกหรือแหล่งกำเนิด
- **Under-Relaxation**: การผ่อนคลายเพื่อความเสถียร

**📂 Source:** .applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C

### สมการพลังงาน

```cpp
// Energy equation
// สมการพลังงาน
fvScalarMatrix TEqn
(
    fvm::ddt(rho, T)              // Implicit time (เวลาโดยนัย)
  + fvm::div(rhoPhi, T)           // Implicit convection (การพาโดยนัย)
 ==
  fvm::laplacian(alpha, T)        // Implicit diffusion (การแพร่โดยนัย)
  + fvc::div(q)                   // Explicit heat flux (ฟลักซ์ความร้อนชัดแจ้ง)
  + fvOptions(rho, T)             // Source terms (เทอมต้นทาง)
);

TEqn.relax();
TEqn.solve();
```

**📖 คำอธิบาย (Thai Explanation):**

**Source/Explanation:**
- ใช้ `fvm` สำหรับเทอมหลักทั้งหมดที่เกี่ยวกับ T เพื่อความเสถียร
- ใช้ `fvc` สำหรับฟลักซ์ความร้อน q ที่คำนวณจากสมการอื่น
- `fvOptions` ใช้เพิ่มเทอมต้นทางเช่นแหล่งความร้อน

**Key Concepts:**
- **Energy Conservation**: การอนุรักษ์พลังงานในระบบ
- **Heat Transfer**: การถ่ายเทความร้อนผ่านการพาและการแพร่
- **Thermal Diffusivity**: สัมประสิทธิ์การแพร่ความร้อน
- **Coupled Physics**: ฟิสิกส์ที่เชื่อมโยงกันระหว่างความเร็วและอุณหภูมิ

**📂 Source:** .applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C

---

## 🔍 ข้อจำกัดความเสถียร

### Explicit Stability Limits

สำหรับการดำเนินการ explicit จำกัดโดยเงื่อนไข:

#### Convection (CFL Condition)

$$\Delta t \leq \frac{\Delta x}{|\mathbf{u}|_{\max}}$$

#### Diffusion (Von Neumann Stability)

$$\Delta t \leq \frac{\Delta x^2}{2\Gamma}$$

โดยที่:
- $\Delta x$ คือขนาดของเซลล์เมช
- $|\mathbf{u}|_{\max}$ คือความเร็วสูงสุด
- $\Gamma$ คือสัมประสิทธิ์การ diffused

### Implicit Advantages

การดำเนินการ implicit ส่วนใหญ่ไม่มีข้อจำกัดเหล่านี้ ทำให้สามารถใช้ time step ที่ใหญ่กว่าได้

---

## 🎓 สรุป

การเลือกระหว่าง `fvc::` และ `fvm::` เป็นการตัดสินใจที่สำคัญในการพัฒนา OpenFOAM solver:

- **`fvc::`** เหมาะสำหรับการคำนวณที่ต้องการผลลัพธ์ทันที แต่มาพร้อมกับข้อจำกัดความเสถียร
- **`fvm::`** ให้ความเสถียรที่ดีกว่าและรองรับ time step ที่ใหญ่ขึ้น แต่ต้องการทรัพยากรการคำนวณที่มากกว่า
- **การผสมผสาน** ทั้งสองแบบให้ผลลัพธ์ที่ดีที่สุดในการจำลอง CFD ที่ซับซ้อน

การเข้าใจความแตกต่างนี้เป็นพื้นฐานสำคัญในการพัฒนา solver ที่มีประสิทธิภาพและเสถียรสำหรับปัญหา CFD ที่หลากหลาย