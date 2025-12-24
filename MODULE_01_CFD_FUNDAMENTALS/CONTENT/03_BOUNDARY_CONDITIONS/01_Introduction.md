# บทนำ Boundary Condition ใน OpenFOAM

## ความสำคัญของ Boundary Condition

**Boundary Condition** มีความสำคัญอย่างยิ่งในการจำลอง CFD เนื่องจากเป็นตัวกำหนดว่าของไหลมีปฏิสัมพันธ์กับขอบเขตโดเมนอย่างไร

> [!INFO] **Boundary Condition คืออะไร?**
> Boundary Condition เป็นองค์ประกอบพื้นฐานในการจำลองพลศาสตร์ของไหลเชิงคำนวณ (Computational Fluid Dynamics หรือ CFD) ซึ่งกำหนดว่าคุณสมบัติของไหลมีพฤติกรรมอย่างไรที่ขอบเขตทางกายภาพของโดเมนการคำนวณ

```mermaid
graph TD
    A["CFD Domain"] --> B["Inlet Boundary<br/>Fixed Velocity"]
    A --> C["Outlet Boundary<br/>Fixed Pressure"]
    A --> D["Wall Boundary<br/>No-slip Condition"]
    A --> E["Symmetry Boundary<br/>Zero Gradient"]
    A --> F["Periodic Boundary<br/>Cyclic Condition"]

    B --> B1["Velocity: u = U₀<br/>Pressure: ∂p/∂n = 0"]
    C --> C1["Pressure: p = P₀<br/>Velocity: ∂u/∂n = 0"]
    D --> D1["Velocity: u = 0<br/>Temperature: T = T_w"]
    E --> E1["Normal Gradient: ∂φ/∂n = 0<br/>Tangential: φ = constant"]
    F --> F1["Matching: φ_left = φ_right<br/>Gradient: ∂φ/∂n_left = -∂φ/∂n_right"]

    G["Mathematical Forms"] --> G1["Dirichlet: φ = φ₀<br/>Value specified"]
    G --> G2["Neumann: ∂φ/∂n = g<br/>Gradient specified"]
    G --> G3["Robin: aφ + b∂φ/∂n = c<br/>Mixed condition"]
    G --> G4["Cauchy: φ = φ₀<br/>and ∂φ/∂n = g<br/>Both specified"]

    style A fill:#e3f2fd,stroke:#1565c0,stroke-width:3px,color:#000
    style B fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px,color:#000
    style C fill:#ffccbc,stroke:#e65100,stroke-width:2px,color:#000
    style D fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000
    style E fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000
    style F fill:#e1bee7,stroke:#7b1fa2,stroke-width:2px,color:#000
    style G fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000
    style G1 fill:#e8f5e9,stroke:#2e7d32,stroke-width:1px,color:#000
    style G2 fill:#e8f5e9,stroke:#2e7d32,stroke-width:1px,color:#000
    style G3 fill:#e8f5e9,stroke:#2e7d32,stroke-width:1px,color:#000
    style G4 fill:#e8f5e9,stroke:#2e7d32,stroke-width:1px,color:#000
```
> **Figure 1:** ประเภทเงื่อนไขขอบเขตพื้นฐานในโดเมน CFD แสดงความเชื่อมโยงระหว่างรูปแบบทางกายภาพ (เช่น ทางเข้า ทางออก ผนัง) และรูปแบบทางคณิตศาสตร์ (Dirichlet, Neumann, Robin) เพื่อกำหนดพฤติกรรมการไหลที่ขอบเขต


- **การบังคับใช้ข้อจำกัดทางกายภาพ**: เช่น เงื่อนไขไม่ลื่น (no-slip conditions) ที่ผนังแข็ง
- **การระบุแรงขับเคลื่อน**: เช่น การไล่ระดับความดัน (pressure gradients)
- **การรับรองการอนุรักษ์มวล**: ผ่านเงื่อนไขทางเข้า/ออก (inlet/outlet conditions)
- **การสร้างผลเฉลยเอกลักษณ์**: ให้แผนการแยกส่วนเชิงตัวเลขสร้างผลลัพธ์ที่มีความหมายทางกายภาพ

---

## พื้นฐานทางคณิตศาสตร์

ในพลศาสตร์ของไหลเชิงคำนวณ (computational fluid dynamics) **Boundary Condition** เป็นตัวแทนของส่วนต่อประสานทางคณิตศาสตร์ระหว่างโดเมนการคำนวณ (computational domain) กับสภาพแวดล้อมภายนอก

### ปัญหาที่กำหนดไม่ดี (Ill-posed Problems)

หากไม่มีการกำหนด Boundary Condition ที่เหมาะสม การกำหนดสูตรทางคณิตศาสตร์จะไม่สมบูรณ์ นำไปสู่ปัญหาที่กำหนดไม่ดี (ill-posed problems) ซึ่งไม่สามารถหาผลเฉลยที่เป็นเอกลักษณ์ได้

> [!WARNING] **ข้อควรระวัง**
> การกำหนด Boundary Condition มากเกินไป (over-specification) หรือน้อยเกินไป (under-specification) สามารถนำไปสู่ปัญหาความไม่เสถียรเชิงตัวเลข (numerical instability) หรือไม่สามารถหาคำตอบที่ถูกต้องได้

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
> **Figure 2:** การจำแนกประเภทของสมการเชิงอนุพันธ์ย่อย (PDE) และการประยุกต์ใช้ใน CFD โดยแบ่งตามลักษณะทางคณิตศาสตร์ (Elliptic, Parabolic, Hyperbolic) ซึ่งเป็นตัวกำหนดความต้องการเงื่อนไขขอบเขตที่แตกต่างกัน


- **ตัวอย่าง**: สมการ Euler (Euler equations)
- **ทฤษฎีลักษณะเฉพาะ**: กำหนดว่า Boundary Condition ต้องถูกระบุที่ขอบเขตทางเข้า (inflow boundaries)
- **การแพร่กระจาย**: อนุญาตให้ข้อมูลแพร่กระจายออกไปที่ขอบเขตทางออก (outflow boundaries)

#### ระบบพาราโบลิก (Parabolic Systems)

- **ตัวอย่าง**: สมการ Navier-Stokes (Navier-Stokes equations)
- **ข้อกำหนด**: Boundary Condition ต้องถูกระบุบนขอบเขตทั้งหมดของโดเมนการคำนวณ
- **ผลกระทบ**: การเลือกและการนำ Boundary Condition ที่เหมาะสมไปใช้งานมีอิทธิพลพื้นฐานต่อความสมจริงทางกายภาพและความเสถียรเชิงตัวเลข

---

## ประเภทของ Boundary Conditions

### **Dirichlet (Fixed Value)**

**การนิยามทางคณิตศาสต์:**
$$\phi = \phi_0 \quad \text{บน Boundary} \quad \Gamma_D$$

โดยที่:
- $\phi$ = Field Variable ที่ต้องการกำหนดค่า
- $\phi_0$ = ค่าคงที่หรือฟังก์ชันที่ทราบ
- $\Gamma_D$ = Boundary ที่ใช้ Dirichlet Condition

**ความหมายทางกายภาพ:**
- **เหมาะสำหรับ:** ค่า Field ที่วัดหรือควบคุมได้โดยตรงที่พื้นผิว Boundary
- **ตัวอย่าง:** Velocity Profile ที่ Inlet, อุณหภูมิคงที่บนพื้นผิวร้อน, ค่า Pressure ที่ Outlet

**การนำไปใช้ใน OpenFOAM:**
```cpp
// Dirichlet Condition usage in OpenFOAM
fixedValue;           // Set constant value
timeVaryingFixedValue; // Time-dependent value
uniformFixedValue;    // Mathematical expression
```

> **📂 Source:** `.applications/utilities/parallelProcessing/reconstructPar/fvFieldReconstructorReconstructFields.C`

> **คำอธิบาย (Thai Explanation):**
> **Dirichlet Boundary Condition** หรือ Fixed Value Condition เป็นเงื่อนไขขอบเขตแบบกำหนดค่าโดยตรงที่พื้นผิวขอบเขต ใน OpenFOAM ใช้คลาส `fixedValueFvPatchField` เป็นฐานคลาสสำหรับเงื่อนไขประเภทนี้
> 
> **แนวคิดสำคัญ (Key Concepts):**
> - **การกำหนดค่าโดยตรง**: ค่าของตัวแปร (เช่น ความเร็ว ความดัน อุณหภูมิ) ถูกระบุเป็นค่าคงที่หรือฟังก์ชันที่ขอบเขต
> - **การใช้งาน**: เหมาะสำหรับ inlet conditions ที่ทราบค่าความเร็ว หรือผนังที่มีอุณหภูมิคงที่
> - **timeVaryingFixedValue**: ใช้เมื่อค่าที่ขอบเขตเปลี่ยนแปลงตามเวลา เช่น ความเร็จ inlet แปรผันตามเวลา
> - **uniformFixedValue**: ใช้นิพจน์ทางคณิตศาสตร์เพื่อกำหนดค่าที่ซับซ้อน เช่น ฟังก์ชันของตำแหน่งหรือเวลา

---

### **Neumann (Fixed Gradient)**

**การนิยามทางคณิตศาสต์:**
$$\frac{\partial \phi}{\partial n} = g_0 \quad \text{บน Boundary} \quad \Gamma_N$$

โดยที่:
- $n$ = ทิศทาง Normal ที่พุ่งออกจาก Boundary
- $g_0$ = ค่า Gradient ที่ระบุ
- $\Gamma_N$ = Boundary ที่ใช้ Neumann Condition

**ความหมายทางกายภาพ:**
- **เหมาะสำหรับ:** Flux ของปริมาณที่ข้าม Boundary เป็นที่ทราบ
- **ตัวอย่าง:** ผนัง Adiabatic ในปัญหา Heat Transfer, ระนาบ Symmetry

**กรณีพิเศษ - ผนัง Adiabatic:**
$$\frac{\partial T}{\partial n} = 0$$
บ่งชี้ว่าไม่มี Heat Flux ผ่าน Boundary

**การนำไปใช้ใน OpenFOAM:**
```cpp
// Neumann Condition usage in OpenFOAM
fixedGradient;        // Set constant gradient value
zeroGradient;         // Zero gradient (special case)
```

> **📂 Source:** `.applications/utilities/parallelProcessing/reconstructPar/fvFieldReconstructorReconstructFields.C`

> **คำอธิบาย (Thai Explanation):**
> **Neumann Boundary Condition** หรือ Fixed Gradient Condition เป็นเงื่อนไขขอบเขตที่กำหนดค่าอนุพันธ์เชิงทิศทาง (gradient) ของตัวแปรในแนวปกติของพื้นผิวขอบเขต ใน OpenFOAM ใช้คลาส `fixedGradientFvPatchField` สำหรับเงื่อนไขประเภทนี้
> 
> **แนวคิดสำคัญ (Key Concepts):**
> - **การกำหนด Gradient**: ค่าอนุพันธ์เชิงทิศทาง ∂φ/∂n ถูกระบุแทนค่าของตัวแปรโดยตรง
> - **ผนัง Adiabatic**: zeroGradient แทนการไม่มีการถ่ายเทความร้อนผ่านผนัง
> - **Symmetry Plane**: ใช้ zeroGradient เพื่อให้แน่ใจว่าไม่มี flux ผ่านระนาบสมมาตร
> - **Outlet Boundaries**: มักใช้ zeroGradient สำหรับความเร็วที่ outlet สมมติว่าการไหลเต็มพัฒนาแล้ว

---

### **Robin (Mixed)**

**การนิยามทางคณิตศาสต์:**
$$a\phi + b\frac{\partial \phi}{\partial n} = c \quad \text{บน Boundary} \quad \Gamma_R$$

โดยที่:
- $a, b, c$ = ค่าคงที่หรือฟังก์ชันที่ระบุ
- $\Gamma_R$ = Boundary ที่ใช้ Robin Condition

**การประยุกต์ใช้สำคัญ - Newton's Cooling Law:**
$$-k\frac{\partial T}{\partial n} = h(T_s - T_\infty)$$

โดยที่:
- $k$ = Thermal Conductivity
- $h$ = Convective Heat Transfer Coefficient
- $T_s$ = Surface Temperature
- $T_\infty$ = Ambient Fluid Temperature

**การจัดรูปแบบใหม่:**
$$hT + k\frac{\partial T}{\partial n} = hT_\infty$$

**การนำไปใช้ใน OpenFOAM:**
```cpp
// Robin Condition usage in OpenFOAM
mixed;                         // General usage
convectiveHeatTransfer;        // Convective heat transfer
```

> **📂 Source:** `.applications/utilities/parallelProcessing/reconstructPar/fvFieldReconstructorReconstructFields.C`

> **คำอธิบาย (Thai Explanation):**
> **Robin Boundary Condition** หรือ Mixed Condition เป็นเงื่อนไขขอบเขตแบบผสมผสานระหว่าง Dirichlet และ Neumann โดยระบุค่าตัวแปรและ gradient พร้อมกัน ใน OpenFOAM ใช้คลาส `mixedFvPatchField` สำหรับเงื่อนไขประเภทนี้
> 
> **แนวคิดสำคัญ (Key Concepts):**
> - **สมการผสม**: aφ + b(∂φ/∂n) = c เป็นการรวมค่าและ gradient ในสมการเดียว
> - **Newton's Cooling Law**: ใช้สำหรับการถ่ายเทความร้อนโดย convection ระหว่างผนังและของไหลโดยรอบ
> - **พารามิเตอร์**: ค่าสัมประสิทธิ์การถ่ายเทความร้อน h และความนำความร้อน k ถูกใช้ในการคำนวณ
> - **convectiveHeatTransfer**: เงื่อนไขเฉพาะสำหรับปัญหาการถ่ายเทความร้อนแบบ convection

---

## สมการควบคุมที่เกี่ยวข้อง

Boundary Condition เหล่านี้กำหนดข้อจำกัดที่จำเป็นในการแก้ระบบสมการเชิงอนุพันธ์ย่อยที่ควบคุมการไหลของของไหล:

### สมการหลัก

**สมการความต่อเนื่อง (Continuity Equation):**
$$\nabla \cdot \mathbf{u} = 0$$

**สมการโมเมนตัม (Momentum Equation):**
$$\rho \frac{\partial \mathbf{u}}{\partial t} + \rho (\mathbf{u} \cdot \nabla) \mathbf{u} = -\nabla p + \mu \nabla^2 \mathbf{u} + \mathbf{f}$$

โดยที่:
- $\mathbf{u}$ = **Velocity Vector** (เวกเตอร์ความเร็ว)
- $p$ = **Pressure** (ความดัน)
- $\rho$ = **Density** (ความหนาแน่น)
- $\mu$ = **Dynamic Viscosity** (ความหนืดพลศาสตร์)
- $\mathbf{f}$ = **Body Forces** (แรงภายนอก)

### ความสอดคล้องทางคณิตศาสตร์

การทำงานร่วมกันระหว่าง Boundary Condition ประเภทต่างๆ ต้องได้รับการปรับสมดุลอย่างระมัดระวัง เพื่อรักษาความสอดคล้องทางคณิตศาสตร์ในขณะที่ยังคงแสดงถึงปรากฏการณ์ทางกายภาพที่กำลังศึกษา

---

## การนำไปใช้งานใน OpenFOAM

### ฟีเจอร์หลัก

- **ความยืดหยุ่น**: ช่วยให้สามารถระบุค่า Boundary ได้อย่างยืดหยุ่นผ่านเฟรมเวิร์กพีชคณิตฟิลด์ (field algebra framework)
- **สถาปัตยกรรมโมดูลาร์**: ช่วยให้ผู้ใช้สามารถรวม Boundary Condition ประเภทต่างๆ เข้าด้วยกัน
- **การขยายได้**: ขยายเฟรมเวิร์กที่มีอยู่ผ่านการนำไปใช้งานแบบกำหนดเอง (custom implementations)

### โครงสร้างคลาสใน OpenFOAM

ลำดับชั้นคลาส `fvPatchField` เป็นรากฐานสำหรับการนำ Boundary Condition ประเภทต่างๆ ไปใช้งาน:

```cpp
// Basic boundary condition structure in OpenFOAM
class fvPatchField
{
    // Base class for all boundary conditions
};

// Types inherited from fvPatchField
class fixedValueFvPatchField;      // Dirichlet conditions
class fixedGradientFvPatchField;   // Neumann conditions
class mixedFvPatchField;           // Mixed conditions
```

> **📂 Source:** `.applications/utilities/parallelProcessing/reconstructPar/fvFieldReconstructorReconstructFields.C`

> **คำอธิบาย (Thai Explanation):**
> **คลาส fvPatchField** เป็นคลาสพื้นฐาน (base class) สำหรับ boundary conditions ทั้งหมดใน OpenFOAM ทำหน้าที่เป็น interface ระหว่าง mesh patches และ field data
> 
> **แนวคิดสำคัญ (Key Concepts):**
> - **Inheritance Hierarchy**: คลาสทั้งหมดสืบทอดจาก `fvPatchField` ซึ่งให้ฟังก์ชันพื้นฐานสำหรับการจัดการข้อมูลที่ patch
> - **Polymorphism**: ช่วยให้สามารถใช้ pointer ของคลาสฐานเพื่อเข้าถึงคลาสลูกได้อย่างยืดหยุ่น
> - **Template-based**: ใช้ template parameters เพื่อรองรับชนิดข้อมูลต่าง ๆ (scalar, vector, tensor)
> - **Virtual Functions**: ใช้ฟังก์ชันเสมือนสำหรับการคำนวณค่าที่ patch และการ update coefficients

```mermaid
graph TD
    A["fvPatchField<br/>Base class for all<br/>boundary conditions"]
    B["fixedValueFvPatchField<br/>Dirichlet conditions<br/>(specified value)"]
    C["fixedGradientFvPatchField<br/>Neumann conditions<br/>(specified gradient)"]
    D["mixedFvPatchField<br/>Mixed/Robin conditions<br/>(value+gradient mix)"]
    E["calculatedFvPatchField<br/>Calculated from<br/>other fields"]
    F["timeVaryingMappedFvPatchField<br/>Time-varying boundary<br/>conditions"]
    G["cyclicFvPatchField<br/>Periodic boundary<br/>conditions"]
    H["wallFvPatchField<br/>Wall boundary<br/>conditions"]
    I["inletOutletFvPatchField<br/>Inlet/outlet switching<br/>based on flow direction"]

    A --> B
    A --> C
    A --> D
    A --> E
    A --> F
    A --> G
    A --> H
    A --> I

    B --> B1["fixedValue<br/>Constant value<br/>(T = 300K)"]
    C --> C1["fixedGradient<br/>Constant gradient<br/>(∂T/∂n = 100 K/m)"]
    D --> D1["mixed<br/>Linear combination<br/>(αT + β∂T/∂n = γ)"]
    G --> G1["cyclic<br/>Periodic mapping<br/>(P₁ = P₂)"]
    H --> H1["noSlip<br/>Zero velocity<br/>(u = 0)"]
    H --> H2["fixedFluxPressure<br/>Pressure gradient<br/>(∂p/∂n = 0)"]

    classDef base fill:#e3f2fd,stroke:#1565c0,stroke-width:3px,color:#000;
    classDef primary fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    classDef secondary fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;
    classDef tertiary fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;

    class A base;
    class B,C,D,E,F,G,H,I primary;
    class B1,C1,D1,G1,H1,H2 secondary;
```
> **Figure 3:** ลำดับชั้นของคลาสสำหรับเงื่อนไขขอบเขตใน OpenFOAM แสดงการสืบทอดจากคลาสฐาน `fvPatchField` ไปยังคลาสเฉพาะทางประเภทต่าง ๆ เพื่อรองรับความต้องการทางคณิตศาสตร์และกายภาพที่หลากหลาย


| ประเภท | คลาส | การใช้งาน | ตัวอย่าง |
|--------|-------|-------------|-----------|
| **Dirichlet** | `fixedValueFvPatchField` | กำหนดค่าคงที่ | อุณหภูมิผนัง, ความเร็วทางเข้า |
| **Neumann** | `fixedGradientFvPatchField` | กำหนดค่ากราดิเอนต์ | การถ่ายเทความร้อน, แรงเฉือน |
| **Mixed** | `mixedFvPatchField` | ผสมระหว่างค่าและกราดิเอนต์ | เงื่อนไขผนังขั้นสูง |
| **Wall Functions** | หลายคลาส | จำลองชั้นขอบเขต | ความปั่นป่วนใกล้ผนัง |

### การนำไปใช้งานจริง

#### ตัวอย่าง Velocity Inlet

```cpp
// 0/U file - Velocity field boundary conditions
dimensions      [0 1 -1 0 0 0 0];  // Velocity dimensions: [L/T]
internalField   uniform 0;        // Initial internal field value

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform (10 0 0);  // Uniform inlet velocity of 10 m/s in x-direction
    }

    outlet
    {
        type            zeroGradient;      // Zero gradient at outlet
    }

    walls
    {
        type            noSlip;            // No-slip condition at walls
    }
}
```

> **📂 Source:** `.applications/utilities/parallelProcessing/reconstructPar/fvFieldReconstructorReconstructFields.C`

> **คำอธิบาย (Thai Explanation):**
> **ไฟล์ 0/U** ใช้กำหนด boundary conditions สำหรับสนามความเร็วใน OpenFOAM ซึ่งเป็นส่วนสำคัญของการตั้งค่าเริ่มต้นของการจำลอง
> 
> **แนวคิดสำคัญ (Key Concepts):**
> - **dimensions**: ระบุหน่วยของค่าความเร็วเป็น [L T^-1] หรือ [m/s]
> - **internalField**: ค่าเริ่มต้นของความเร็วในโดเมนภายใน
> - **fixedValue**: กำหนดค่าคงที่ที่ inlet ในที่นี้คือ (10 0 0) m/s
> - **zeroGradient**: ใช้ที่ outlet สมมติว่าการไหลเต็มพัฒนา (fully developed)
> - **noSlip**: เงื่อนไขไม่ลื่นที่ผนัง ความเร็วเป็นศูนย์

#### ตัวอย่าง Pressure Outlet

```cpp
// 0/p file - Pressure field boundary conditions
dimensions      [1 -1 -2 0 0 0 0];  // Pressure dimensions: [M/LT²]
internalField   uniform 0;         // Initial internal field value

boundaryField
{
    inlet
    {
        type            zeroGradient;      // Zero gradient at inlet
    }

    outlet
    {
        type            fixedValue;
        value           uniform 0;         // Gauge pressure (relative to atmospheric)
    }

    walls
    {
        type            zeroGradient;      // Zero gradient at walls
    }
}
```

> **📂 Source:** `.applications/utilities/parallelProcessing/reconstructPar/fvFieldReconstructorReconstructFields.C`

> **คำอธิบาย (Thai Explanation):**
> **ไฟล์ 0/p** ใช้กำหนด boundary conditions สำหรับสนามความดันใน OpenFOAM ซึ่งมักใช้ความดันเกจ (gauge pressure) เป็นค่าอ้างอิง
> 
> **แนวคิดสำคัญ (Key Concepts):**
> - **dimensions**: ระบุหน่วยของความดันเป็น [M L^-1 T^-2] หรือ [Pa]
> - **Gauge Pressure**: ค่าความดันที่อ้างอิงกับความดันบรรยากาศ (0 = atmospheric pressure)
> - **zeroGradient at inlet**: ความดันไม่มีการเปลี่ยนแปลงในแนวปกติที่ inlet
> - **fixedValue at outlet**: กำหนดความดันคงที่ที่ outlet ซึ่งเป็นเงื่อนไขขอบเขตทั่วไป
> - **P-U Coupling**: ความสัมพันธ์ระหว่างความดันและความเร็วผ่านสมการ continuity

---

## ข้อควรพิจารณาขั้นสูง

### Well-Posedness (Hadamard)

เพื่อให้มั่นใจว่าปัญหามีคำตอบที่ถูกต้อง จำเป็นต้องตรวจสอบ:

1. **มี Solution อยู่**
2. **Solution มีความเฉพาะเจาะจง (Unique)**
3. **Solution ขึ้นอยู่กับ Boundary Data อย่างต่อเนื่อง**

### การจำแนกตามประเภท PDE

| ประเภท PDE | ตัวอย่าง | ข้อกำหนด Boundary Conditions |
|-------------|------------|------------------------------|
| **Elliptic** | Steady-State Diffusion, Potential Flow | Dirichlet หรือ Neumann บน Boundary ทั้งหมด |
| **Parabolic** | Transient Diffusion, Boundary Layer | Initial Conditions + Boundary Conditions |
| **Hyperbolic** | Wave Propagation, Inviscid Flow | Characteristics-Based Boundary Conditions |

---

## บทสรุป

การเข้าใจและการนำ Boundary Conditions ไปใช้งานอย่างถูกต้องเป็นพื้นฐานสำคัญสำหรับการสร้าง CFD Simulations ที่แม่นยำและเชื่อถือได้ใน OpenFOAM

**หลักการสำคัญ:**

1. **การเลือก Boundary Condition ที่เหมาะสม** สำคัญต่อความแม่นยำและความเสถียรของ CFD Simulations

2. **การจำแนกเป็น Dirichlet, Neumann, และ Robin** เป็นกรอบทางคณิตศาสตร์ที่รับประกัน Well-Posed Problems

3. **การประยุกต์ใช้ใน OpenFOAM** ต้องคำนึงถึง Physical Meaning และ Numerical Stability

4. **Boundary Conditions ขั้นสูง** ช่วยแก้ไขปัญหาที่ซับซ้อนใน Multiphysics และ Special Applications

---

> [!TIP] **การเรียนรู้เพิ่มเติม**
> - ดูรายละเอียดเพิ่มเติมเกี่ยวกับ [[02_Fundamental_Classification]]
> - เรียนรู้วิธีการเลือก Boundary Condition ที่เหมาะสมใน [[03_Selection_Guide_Which_BC_to_Use]]
> - ศึกษา [[04_Mathematical_Formulation]] สำหรับความเข้าใจเชิงลึก