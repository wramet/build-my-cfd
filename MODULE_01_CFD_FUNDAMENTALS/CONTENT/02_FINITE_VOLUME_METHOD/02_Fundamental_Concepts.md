# แนวคิดพื้นฐานของ Finite Volume Method

## แนวทางการใช้ Control Volume

**Finite Volume Method** แบ่ง Computational Domain ออกเป็นชุดของ **Control Volume (Cells)** ที่ไม่ทับซ้อนกัน โดย:

- **Governing Equations** จะถูกอินทิเกรตเหนือ Control Volume แต่ละอัน
- รับประกันการอนุรักษ์มวล โมเมนตัม และพลังงานในระดับท้องถิ่น (local conservation)
- เป็นรากฐานทางคณิตศาสตร์ของ **Computational Framework ของ OpenFOAM**
- วิธีการที่เข้มงวดในการ Discretize **Partial Differential Equations** โดยยังคงรักษ์ Conservation Laws พื้นฐานทางฟิสิกส์ไว้

```mermaid
graph LR
    subgraph "Computational Domain"
        CV1["Control Volume 1"]
        CV2["Control Volume 2"]
        CV3["Control Volume 3"]
        CV4["Control Volume 4"]
        CV5["Control Volume 5"]
        CV6["Control Volume 6"]
    end

    subgraph "Fluxes Across Boundaries"
        F12["Flux 1→2"]
        F23["Flux 2→3"]
        F34["Flux 3→4"]
        F45["Flux 4→5"]
        F56["Flux 5→6"]
        F61["Flux 6→1"]
        F13["Flux 1→3"]
        F24["Flux 2→4"]
        F35["Flux 3→5"]
        F46["Flux 4→6"]
    end

    CV1 -- "Mass, Momentum, Energy" --> F12
    F12 --> CV2
    CV2 --> F23
    F23 --> CV3
    CV3 --> F34
    F34 --> CV4
    CV4 --> F45
    F45 --> CV5
    CV5 --> F56
    F56 --> CV6
    CV6 --> F61
    F61 --> CV1

    CV1 -.-> F13
    F13 -.-> CV3
    CV2 -.-> F24
    F24 -.-> CV4
    CV3 -.-> F35
    F35 -.-> CV5
    CV4 -.-> F46
    F46 -.-> CV6

    classDef cv fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    classDef flux fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    class CV1,CV2,CV3,CV4,CV5,CV6 cv;
    class F12,F23,F34,F45,F56,F61,F13,F24,F35,F46 flux;
```

## ความเข้าใจเชิงกายภาพ

### หลักการสมดุล

แนวทางการใช้ Control Volume สามารถเข้าใจได้ผ่านการเปรียบเทียบ:

**ลองจินตนาการ** การแบ่ง Fluid Domain ที่ต่อเนื่องออกเป็นกล่องเล็กๆ หรือ **Control Volume** ที่แยกจากกัน:

1. **สำหรับแต่ละกล่อง**: พิจารณา Fluxes (การไหล) ทั้งหมดที่ข้ามผ่านขอบเขต
2. **การสมดุล**: การเปลี่ยนแปลงสุทธิของปริมาณที่อนุรักษ์ = ปริมาณที่ไหลเข้า - ปริมาณที่ไหลออก + Sources/Sinks
3. **หลักการทางฟิสิกส์**: สิ่งที่เข้า + สิ่งที่ถูกสร้าง = สิ่งที่ออก + สิ่งที่ถูกทำลาย + การเปลี่ยนแปลงในระบบ

### จากมุมมองการคำนวณ

**Control Volume แต่ละอัน** จะกลายเป็น **Computational Cell** ที่เราเก็บและแก้สมการคณิตศาสตร์ โดยมีลักษณะสำคัญ:

- **Local Conservation**: การอนุรักษ์ที่แม่นยำในระดับ Cell แต่ละอัน
- **Flux Balance**: การคำนวณ Fluxes ที่ขอบเขทของ Cell
- **Source Terms**: การรวม Sources หรือ Sinks ภายใน Cell

```mermaid
graph LR
    subgraph "Continuous Domain"
        A["Continuous Fluid<br/>Domain"] --> B["Mathematical<br/>Fields"]
        B --> C["Differential<br/>Equations"]
        C --> D["Analytical<br/>Solutions"]
    end

    subgraph "Discretized Domain"
        E["Control Volume<br/>Grid"] --> F["Computational<br/>Mesh"]
        F --> G["Cell-centered<br/>Values"]
        G --> H["Algebraic<br/>Equations"]
        H --> I["Numerical<br/>Solution"]
    end

    A -.->|Discretization| E
    D -.->|Transformation| H

    subgraph "Key Relationships"
        J["Flux Conservation<br/>at Cell Faces"]
        K["Local Mass<br/>Balance"]
        L["Numerical<br/>Integration"]
    end

    F --> J
    J --> K
    K --> L

    classDef process fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    classDef decision fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    classDef terminator fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
    classDef storage fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;

    class A,B,C,D process
    class E,F,G,H,I storage
    class J,K,L decision
```

---

## สมการควบคุม (Governing Equations)

### การอนุรักษ์มวล (Mass Conservation)

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

สำหรับปริมาตรควบคุม (control volume) $V$ ที่มีพื้นที่ผิว $S$ อัตราการสะสมมวลภายในปริมาตรจะเท่ากับอัตราการไหลสุทธิของมวล (net mass flux) ผ่านพื้นผิว

**รูปแบบทั่วไป:**
$$\frac{\partial \rho}{\partial t} + \nabla \cdot (\rho \mathbf{u}) = 0$$

โดยที่:
* $\rho$ = ความหนาแน่นของของไหล (fluid density)
* $\mathbf{u}$ = เวกเตอร์ความเร็ว (velocity vector)

**สำหรับการไหลแบบอัดตัวไม่ได้** ($\rho = \text{constant}$):
$$\nabla \cdot \mathbf{u} = 0$$

เงื่อนไข **divergence-free condition** นี้ทำให้มั่นใจได้ว่าอัตราการไหลเชิงปริมาตร (volumetric flow rate) ที่ไหลเข้าสู่ปริมาตรควบคุมขนาดเล็กมาก ๆ จะเท่ากับอัตราการไหลเชิงปริมาตรที่ไหลออก ซึ่งเป็นการรักษาสภาพการอนุรักษ์มวลตลอดทั่วทั้งโดเมน (domain)

### การอนุรักษ์โมเมนตัม (Momentum Conservation)

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

สมการนี้ปรับสมดุลระหว่างแรงเฉื่อย (inertial forces) กับแรงที่กระทำต่อปริมาตร (body forces) และแรงที่กระทำต่อพื้นผิว (surface forces) ที่กระทำต่อองค์ประกอบของไหล

**รูปแบบทั่วไป:**
$$\rho \frac{\partial \mathbf{u}}{\partial t} + \rho (\mathbf{u} \cdot \nabla) \mathbf{u} = -\nabla p + \mu \nabla^2 \mathbf{u} + \mathbf{f}$$

โดยที่:
* $p$ = ความดันสถิต (static pressure)
* $\mu$ = ความหนืดจลน์ (dynamic viscosity)
* $\mathbf{f}$ = แรงที่กระทำต่อปริมาตร (body forces) เช่น แรงโน้มถ่วง ($\rho \mathbf{g}$)

#### การวิเคราะห์แต่ละพจน์:

**ด้านซ้ายมือ (Local + Convective Acceleration):**
* $\rho \frac{\partial \mathbf{u}}{\partial t}$ = ความเร่งเฉพาะที่ (local acceleration)
* $\rho (\mathbf{u} \cdot \nabla) \mathbf{u}$ = ความเร่งแบบพา (convective acceleration)

**ด้านขวามือ (Surface + Body Forces):**
* $-\nabla p$ = แรงดัน (pressure forces)
* $\mu \nabla^2 \mathbf{u}$ = แรงหนืด (viscous forces)
* $\mathbf{f}$ = แรงภายนอก (external body forces)

ระบบสมการเชิงอนุพันธ์ย่อยแบบไม่เชิงเส้น (nonlinear system of partial differential equations) นี้เป็นรากฐานของการวิเคราะห์พลศาสตร์ของไหล (fluid dynamics analysis) ใน OpenFOAM

### การอนุรักษ์พลังงาน (Energy Conservation)

**สมการพลังงาน** (energy equation) ควบคุมการถ่ายเทพลังงานความร้อน (thermal energy) ภายในระบบของไหล

```mermaid
graph LR
    A["Control Volume<br/>Energy Balance"] --> B["<b>Energy In</b><br/>ρcₚ u·∇T"]
    B --> C["<b>Energy Storage</b><br/>ρcₚ ∂T/∂t"]
    A --> D["<b>Conduction</b><br/>k∇²T"]
    C --> E["<b>Temperature Field</b><br/>T(x,y,z,t)"]
    D --> E

    F["<b>Heat Transfer Mechanisms</b>"] --> G["<b>Convection</b><br/>Fluid movement"]
    F --> H["<b>Conduction</b><br/>Molecular diffusion"]
    F --> I["<b>Generation</b><br/>Source terms Q"]

    G --> J["<b>Transport Term</b><br/>ρcₚ u·∇T"]
    H --> K["<b>Diffusion Term</b><br/>k∇²T"]
    I --> L["<b>Source Term</b><br/>Q/(ρcₚ)"]

    J --> E
    K --> E
    L --> E

    style A fill:#e1f5fe
    style E fill:#f3e5f5
    style F fill:#fff3e0

    classDef process fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    classDef decision fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    classDef terminator fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
    classDef storage fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;
    classDef principle fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000;
    classDef arrows fill:none,stroke:none,color:none;

    class A,B,C,D,E,F,G,H,I,J,K,L process;
```

สำหรับของไหลที่มีอุณหภูมิ $T$ สมการพลังงานในรูปของอุณหภูมิคือ:

$$\rho c_p \frac{\partial T}{\partial t} + \rho c_p \mathbf{u} \cdot \nabla T = k \nabla^2 T + Q$$

โดยที่:
* $c_p$ = ความจุความร้อนจำเพาะที่ความดันคงที่ (specific heat capacity at constant pressure)
* $k$ = สภาพนำความร้อน (thermal conductivity)
* $Q$ = แหล่งกำเนิดความร้อน (heat sources) หรือตัวรับความร้อน (sinks) ภายในโดเมน (domain)

#### การวิเคราะห์แต่ละพจน์:

**ด้านซ้ายมือ (Temporal + Convective Energy Transport):**
* $\rho c_p \frac{\partial T}{\partial t}$ = การเปลี่ยนแปลงพลังงานความร้อนตามเวลา
* $\rho c_p \mathbf{u} \cdot \nabla T$ = การลำเลียงพลังงานความร้อนแบบพา

**ด้านขวามือ (Diffusion + Generation):**
* $k \nabla^2 T$ = การถ่ายเทความร้อนแบบนำ (conductive heat transfer) ตามกฎของฟูเรียร์ (Fourier's law)
* $Q$ = พจน์การเกิดความร้อนเชิงปริมาตร (volumetric heat generation)

**การใช้งานใน OpenFOAM:**
ใน OpenFOAM implementations สมการนี้อาจถูกแก้ในรูปของ:
* **เอนทาลปี** (enthalpy) $h$
* **พลังงานภายใน** (internal energy) $e$
* **อุณหภูมิสัมผัส** (sensible temperature)

ขึ้นอยู่กับ Thermophysical Model ที่ใช้

### การถ่ายเทชนิดสาร (Species Transport)

สำหรับการไหลแบบหลายองค์ประกอบ (multicomponent flows) ที่มีการถ่ายเทชนิดสารเคมี (chemical species transport) จะต้องแก้สมการอนุรักษ์สำหรับชนิดสาร $i$ แต่ละชนิด:

```mermaid
graph LR
    A[Control Volume] --> B[Species Transport In]
    A --> C[Species Transport Out]
    A --> D[Diffusion Flux J_i]
    A --> E[Chemical Production/Destruction omega_i]

    B --> F["ρ u Y_i (convective flux)"]
    C --> G["∂(ρY_i)/∂t (temporal change)"]
    D --> H["-∇·J_i (diffusion term)"]
    E --> I["ω_i (reaction source term)"]

    F --> J["Species Conservation Equation"]
    G --> J
    H --> J
    I --> J

    J --> K["∂(ρY_i)/∂t + ∇·(ρuY_i) = -∇·J_i + ω_i"]

    %% Styling Definitions
    classDef process fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    classDef decision fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    classDef terminator fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
    classDef storage fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;
    classDef arrow fill:none,stroke:#333,stroke-width:2px,color:#000;

    class A,J process;
    class B,C storage;
    class D,E decision;
    class F,G,H,I terminator;
```

$$\frac{\partial (\rho Y_i)}{\partial t} + \nabla \cdot (\rho \mathbf{u} Y_i) = -\nabla \cdot \mathbf{J}_i + \dot{\omega}_i$$

โดยที่:
* $Y_i$ = สัดส่วนมวล (mass fraction) ของชนิดสาร $i$
* $\mathbf{J}_i$ = เวกเตอร์ฟลักซ์การแพร่ (diffusive flux vector) สำหรับชนิดสาร $i$
* $\dot{\omega}_i$ = อัตราการผลิต/การทำลายสุทธิ (net rate of production/destruction) อันเนื่องมาจากปฏิกิริยาเคมี

#### กฎของฟิค (Fick's Law):

ฟลักซ์การแพร่ (diffusive flux) $\mathbf{J}_i$ โดยทั่วไปจะจำลองโดยใช้กฎของฟิคสำหรับการแพร่แบบไบนารี (binary diffusion):

$$\mathbf{J}_i = -\rho D_i \nabla Y_i$$

โดยที่:
* $D_i$ = สัมประสิทธิ์การแพร่ (diffusion coefficient) ของชนิดสาร $i$ ในสารผสม

#### เงื่อนไขการอนุรักษ์:
* สมการเหล่านี้รับรองการอนุรักษ์ชนิดสารแต่ละชนิด
* ยังคงรักษาการอนุรักษ์มวลโดยรวมผ่านสมการความต่อเนื่อง
* ผลรวมของสัดส่วนมวลของชนิดสารทั้งหมดจะต้องเป็นไปตาม $\sum_i Y_i = 1$ ณ ทุกจุดในโดเมน (domain)

### สมการสภาวะ (Equation of State)

**สมการสภาวะ** (equation of state) ให้ความสัมพันธ์ทางอุณหพลศาสตร์ระหว่างความดัน ความหนาแน่น และอุณหภูมิ ซึ่งเป็นการปิดระบบสมการควบคุม (governing equations)

```mermaid
graph LR
    P["Pressure (p)"] --> EOS["Equation of State"]
    T["Temperature (T)"] --> EOS
    R["Gas Constant (R)"] --> EOS
    Rho["Density (rho)"]
    EOS --> Rho

    subgraph "Thermodynamic Relationship"
        P2["p"]
        T2["T"]
        R2["R"]
        Rho2["rho"]
        P2 --- "*" R2
        R2 --- "*" T2
        P2 --- "=" Rho2
    end

    classDef process fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    classDef decision fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    classDef terminator fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
    classDef storage fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;
    class P,T,Rho,R,EOS process;
    class P2,T2,R2,Rho2 storage;
```

#### ก๊าซในอุดมคติ (Ideal Gas):

สำหรับก๊าซในอุดมคติ ความสัมพันธ์แสดงได้ดังนี้:

$$p = \rho R T$$

โดยที่:
* $R$ = ค่าคงที่ของก๊าซจำเพาะ (specific gas constant)

#### การใช้งานใน OpenFOAM:

ใน OpenFOAM สิ่งนี้ถูกนำไปใช้ผ่านคลาส Thermophysical Model เช่น:

| Model | Description | Use Case |
|-------|-------------|----------|
| `perfectGas` | ก๊าซในอุดมคติ | ก๊าซที่มีอุณหภูมิสูงและความดันต่ำ |
| `icoPolynomial` | พหุนามความหนาแน่นคงที่ | ของไหลอัดตัวไม่ได้ที่มีคุณสมบัติแปรผันตามอุณหภูมิ |
| `hPolynomial` | พหุนามเอนทาลปี | ของไหลที่มีความสัมพันธ์อุณหภูมิ-เอนทาลปีซับซ้อน |

#### ผลกระทบของการเลือกโมเดล:

การเลือกโมเดลสมการสภาวะ (equation of state model) ที่เหมาะสมส่งผลกระทบอย่างมากต่อ:

* **การเชื่อมโยงระหว่างสมการโมเมนตัมและพลังงาน**
* **การจำลองการไหลแบบอัดตัวได้** (compressible flow simulations)
* **บทบาทของการเปลี่ยนแปลงความหนาแน่นในพลศาสตร์ของการไหล**

**สำหรับการไหลแบบอัดตัวไม่ได้** (incompressible flows) ความหนาแน่นจะถือว่าคงที่ ทำให้ไม่จำเป็นต้องใช้ความสัมพันธ์ของสมการสภาวะที่ชัดเจน

---

## รูปแบบสมการทั่วไป (General Form)

สำหรับสมการการอนุรักษ์ทั่วไปในรูปแบบ:

$$\frac{\partial \phi}{\partial t} + \nabla \cdot \mathbf{F}(\phi) = S(\phi)$$

**นิยามตัวแปร:**
- $\phi$: ปริมาณที่ถูกอนุรักษ์ (conserved quantity)
- $\mathbf{F}$: เวกเตอร์ฟลักซ์ (flux vector)
- $S$: เทอมแหล่งกำเนิด (source term)

FVM จะทำการประมาณค่าแบบดิสครีตสำหรับรูปแบบอินทิกรัลเหนือปริมาตรควบคุม $V$:

$$\int_V \frac{\partial \phi}{\partial t} \, \mathrm{d}V + \int_V \nabla \cdot \mathbf{F}(\phi) \, \mathrm{d}V = \int_V S(\phi) \, \mathrm{d}V$$

## คุณสมบัติการอนุรักษ์และการจัดการข้อผิดพลาด

### คุณสมบัติการอนุรักษ์โดยธรรมชาติ

จุดแข็งของ Finite Volume Method อยู่ที่คุณสมบัติการอนุรักษ์โดยธรรมชาติ:

- **การไหลออก (outflow)** จากเซลล์หนึ่งจะกลายเป็น **การไหลเข้า (inflow)** สู่เซลล์ที่อยู่ติดกัน
- **รับประกันการอนุรักษ์โดยรวม (global conservation)** โดยไม่คำนึงถึงคุณภาพของ Mesh
- **สำคัญอย่างยิ่ง**สำหรับปัญหาที่เกี่ยวข้องกับ Shocks, Discontinuities

```mermaid
graph LR
    A["Control Volume i"] --> B["Flux F_i+1/2"]
    B --> C["Control Volume i+1"]
    C --> D["Flux F_i+3/2"]
    D --> E["Control Volume i+2"]

    A --> F["Flux F_i-1/2"]
    F --> G["Control Volume i-1"]
    G --> H["Flux F_i-3/2"]
    H --> I["Control Volume i-2"]

    style A fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    style C fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    style E fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    style G fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    style I fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;

    style B fill:#ffebee,stroke:#c62828,stroke-width:3px,color:#000;
    style D fill:#ffebee,stroke:#c62828,stroke-width:3px,color:#000;
    style F fill:#ffebee,stroke:#c62828,stroke-width:3px,color:#000;
    style H fill:#ffebee,stroke:#c62828,stroke-width:3px,color:#000;

    classDef cell fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    classDef flux fill:#ffebee,stroke:#c62828,stroke-width:3px,color:#000;
```

### กลไกการจัดการข้อผิดพลาดใน OpenFOAM

OpenFOAM ใช้กลไกการจัดการข้อผิดพลาด (error handling) และการควบคุมคุณภาพ (quality control) ที่ซับซ้อน:

#### 1. ความสอดคล้องของ Face Flux (Face Flux Consistency)
- **รับประกันว่า Face Fluxes จะถูกคำนวณเพียงครั้งเดียว**
- **นำไปใช้อย่างสอดคล้องกับเซลล์ที่อยู่ติดกันทั้งสองเซลล์**ในระหว่างการประกอบ Matrix

#### 2. การรวม Boundary Condition (Boundary Condition Integration)
- **การจัดการพิเศษสำหรับ Boundary Faces**
- **ทำให้มั่นใจว่า Boundary Conditions ถูกรวมเข้ากับสมการดิสครีตอย่างเหมาะสม**
- **ยังคงรักษาการอนุรักษ์ไว้**

#### 3. ความทนทานต่อคุณภาพ Mesh (Mesh Quality Robustness)
- **รองรับ Mesh ที่ไม่เป็น Orthogonal และ Skewed**
- **ผ่าน Correction Schemes และ Iterative Procedures**
- **ช่วยปรับปรุงความแม่นยำบนรูปทรงเรขาคณิตที่ซับซ้อน**

#### 4. ระบบ Sparse Matrix (Sparse Matrix Systems)
- **สมการที่ถูกประมาณค่าแบบดิสครีตจะถูกประกอบเข้าเป็น Sparse Matrix Systems**
- **สามารถหาคำตอบได้อย่างมีประสิทธิภาพโดยใช้วิธี Iterative Methods**
- **พร้อมกับ Preconditioners ที่เหมาะสม**

**OpenFOAM Code Implementation:**
```cpp
// การสร้างและแก้ไข sparse matrix system
fvScalarMatrix phiEqn
(
    fvm::ddt(phi)
  + fvm::div(phi, U)
  - fvm::laplacian(D, phi)
 ==
    Su
);

phiEqn.solve();  // การแก้ไขระบบสมการ
```

---

## การเชื่อมโยง Pressure-Velocity (Pressure-Velocity Coupling)

การเชื่อมโยงระหว่าง Pressure และ Velocity Fields เป็นสิ่งสำคัญของการจำลอง Incompressible Flow

| Algorithm | ลักษณะการทำงาน | รอบการทำซ้ำ | ข้อดี | ข้อเสีย |
|-----------|-----------------|---------------|--------|----------|
| **SIMPLE** | Sequential solution with under-relaxation | Multiple per time step | Robust, steady-state | Slow convergence |
| **PISO** | Multiple pressure corrections per time step | 2-3 corrections per step | Accurate for transient | Can be unstable |
| **PIMPLE** | Hybrid SIMPLE + PISO | Flexible | Good for both steady/transient | More complex |

### SIMPLE Algorithm Steps:
1. แก้สมการ Momentum ด้วย Pressure ที่คาดเดา $p^*$
2. แก้สมการ Pressure Correction
3. แก้ไข Pressure และ Velocity Fields
4. อัปเดต Turbulence และ Scalar Fields อื่นๆ
5. ตรวจสอบ Convergence (ทำซ้ำหากจำเป็น)

### PISO Algorithm Steps:
1. ทำนาย Velocity Field $\mathbf{u}^*$
2. แก้สมการ Pressure
3. แก้ไข Velocity Field
4. ทำซ้ำการแก้ไข Pressure-Velocity 2-3 ครั้ง
5. ก้าวไปสู่ Time Step ถัดไป

---

## ข้อดีและข้อจำกัดของ Finite Volume Method

### ข้อดี:

> [!INFO] **ข้อดีหลักของ FVM**
> - **การอนุรักษ์โดยธรรมชาติ**: รับประกันการอนุรักษ์ในระดับจากเซลล์
> - **ความยืดหยุ่นของ Mesh**: รองรับ Unstructured Meshes ที่ซับซ้อน
> - **การจัดการ Boundary Condition**: ใช้งานง่ายกับเรขาคณิตที่ซับซ้อน
> - **ประสิทธิภาพ**: Sparse Matrix Systems ที่สามารถแก้ไขได้อย่างมีประสิทธิภาพ
> - **ความแม่นยำ**: สามารถใช้ Higher-Order Schemes ได้

### ข้อจำกัด:

> [!WARNING] **ข้อจำกัดที่ต้องพิจารณา**
> - **ความซับซ้อนของ Discretization**: ต้องการ Interpolation Schemes ที่เหมาะสม
> - **Numerical Diffusion**: อาจเกิดจาก First-Order Schemes
> - **ความละเอียดของ Mesh**: ต้องการ Mesh ที่ละเอียดสำหรับ Gradient สูง
> - **เวลาคำนวณ**: การแก้ Implicit Systems อาจใช้เวลานาน

---

## สรุป

**Finite Volume Method** เป็นกรอบการทำงานที่มีประสิทธิภาพสำหรับการจำลอง CFD ซึ่ง:

1. **แบ่ง Domain** ออกเป็น Control Volumes ที่ไม่ทับซ้อนกัน
2. **อินทิเกรต** สมการควบคุมเหนือแต่ละ Control Volume
3. **ใช้ Divergence Theorem** แปลง Volume Integrals เป็น Surface Integrals
4. **ประมาณค่า Fluxes** ที่ Face Boundaries ด้วย Interpolation Schemes
5. **สร้าง Sparse Linear Systems** ที่สามารถแก้ไขได้อย่างมีประสิทธิภาพ

ใน OpenFOAM กรอบการทำงานนี้ถูกนำไปใช้ผ่าน Class `fvMatrix` ซึ่งให้การดำเนินการ Discretization ที่สม่ำเสมอและมีประสิทธิภาพสำหรับสมการ Conservation ทั้งหมด
