# บทนำสู่ Finite Volume Method ใน OpenFOAM

## แนวคิดพื้นฐานของ Finite Volume Method (FVM)

**Finite Volume Method (FVM)** เป็นเทคนิคการประมาณค่าแบบตัวเลข (numerical discretization technique) ที่ OpenFOAM ใช้ในการแปลงสมการเชิงอนุพันธ์ย่อย (Partial Differential Equations หรือ PDEs) ที่ควบคุมการไหลของของไหลให้เป็นระบบสมการพีชคณิตที่สามารถคำนวณหาคำตอบได้

### หลักการการอนุรักษ์

Finite Volume Method ทำงานบน**รูปแบบอินทิกรัลของสมการการอนุรักษ์ (conservation equations)** ซึ่งรับประกันว่าปริมาณทางกายภาพพื้นฐาน เช่น:

- **มวล (Mass)**
- **โมเมนตัม (Momentum)**
- **พลังงาน (Energy)**

จะถูกอนุรักษ์ไว้ในระดับดิสครีต

**ความแตกต่างจากวิธีอื่น**: วิธีอื่น ๆ ทำการประมาณค่าแบบดิสครีตสำหรับรูปแบบเชิงอนุพันธ์ (differential forms) แต่ FVM จะ:

1. **แบ่งโดเมนการคำนวณ**ออกเป็นชุดของปริมาตรควบคุม (control volumes หรือ cells) ที่ไม่ทับซ้อนกัน
2. **ประยุกต์ใช้กฎการอนุรักษ์โดยตรง**กับปริมาตรควบคุมแต่ละส่วน

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

    classDef process fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    classDef decision fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    classDef terminator fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
    classDef storage fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;
```
> **Figure 1:** แนวคิดพื้นฐานของวิธี Finite Volume แสดงการแบ่งโดเมนการคำนวณออกเป็นปริมาตรควบคุมแบบไม่ต่อเนื่อง โดยประยุกต์ใช้กฎการอนุรักษ์กับฟลักซ์สุทธิและพจน์แหล่งกำเนิด

### รูปแบบสมการทั่วไป

สำหรับสมการการอนุรักษ์ทั่วไปในรูปแบบ:
$$\frac{\partial \phi}{\partial t} + \nabla \cdot \mathbf{F}(\phi) = S(\phi)$$

**นิยามตัวแปร:**
- $\phi$: ปริมาณที่ถูกอนุรักษ์ (conserved quantity)
- $\mathbf{F}$: เวกเตอร์ฟลักซ์ (flux vector)
- $S$: เทอมแหล่งกำเนิด (source term)

FVM จะทำการประมาณค่าแบบดิสครีตสำหรับรูปแบบอินทิกรัลเหนือปริมาตรควบคุม $V$:
$$\int_V \frac{\partial \phi}{\partial t} \, \mathrm{d}V + \int_V \nabla \cdot \mathbf{F}(\phi) \, \mathrm{d}V = \int_V S(\phi) \, \mathrm{d}V$$

---

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
> **Figure 2:** ความเชื่อมโยงระหว่างปริมาตรควบคุมในเมชเชิงคำนวณ แสดงการแลกเปลี่ยนฟลักซ์ (มวล โมเมนตัม พลังงาน) ข้ามขอบเขตร่วมระหว่างเซลล์ที่อยู่ติดกัน

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

    %% Styling Definitions
    classDef process fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    classDef decision fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    classDef terminator fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
    classDef storage fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;

    class A,B,C,D process
    class E,F,G,H,I storage
    class J,K,L decision
```
> **Figure 3:** ขั้นตอนการทำงานที่ขนานกันระหว่างแนวทางเชิงวิเคราะห์แบบต่อเนื่องและแนวทางเชิงตัวเลขแบบไม่ต่อเนื่องใน CFD โดยเน้นการแปลงจากสมการเชิงอนุพันธ์ไปสู่ระบบสมการพีชคณิต

---

## กรอบการนำไปใช้งานใน OpenFOAM

### สถาปัตยกรรม C++ Template

การนำ FVM มาใช้ใน OpenFOAM สร้างขึ้นบน**ระบบ C++ template ที่ซับซ้อน**ซึ่งให้:

- **การดำเนินการฟิลด์ที่ไม่ขึ้นกับชนิดข้อมูล** (type-agnostic field operations)
- **รักษาประสิทธิภาพการคำนวณ**ไว้

### ไลบรารีหลัก

การดำเนินการ FVM หลักใน OpenFOAM จัดการโดยไลบรารี `finiteVolume` ซึ่งประกอบด้วย:

- **คลาสและฟังก์ชันสำหรับการคำนวณ**: Gradient, Divergence, Temporal Integration
- **คลาส `fvMesh`**: สำหรับเข้าถึงข้อมูลทางเรขาคณิต:
  - ปริมาตรเซลล์ (cell volumes)
  - พื้นที่หน้า (face areas)
  - ข้อมูลทางเรขาคณิตสำหรับการประมาณค่าแบบดิสครีต

### กระบวนการประมาณค่าแบบดิสครีต

กระบวนการใน OpenFOAM มีขั้นตอนพื้นฐานดังนี้:

#### 1. การแบ่ง Mesh (Mesh Decomposition)
โดเมนการคำนวณจะถูกแบ่งย่อยออกเป็น Finite Volume Cells ผ่าน `polyMesh`
- แต่ละเซลล์แสดงถึง Control Volume
- มีการประยุกต์ใช้กฎการอนุรักษ์

#### 2. การอินทิเกรตบนพื้นผิว (Surface Integration)
ทฤษฎีบท Divergence (Divergence Theorem) ถูกใช้เพื่อแปลง Volume Integrals ของ Divergences ให้เป็น Surface Integrals:
$$\int_V \nabla \cdot \mathbf{F} \, \mathrm{d}V = \oint_{\partial V} \mathbf{F} \cdot \mathbf{n} \, \mathrm{d}S$$

**นิยามตัวแปร:**
- $\mathbf{n}$: เวกเตอร์แนวฉากภายนอก (outward normal vector) ที่พื้นผิว

#### 3. การประเมิน Flux (Flux Evaluation)
Surface Fluxes จะถูกประเมินที่หน้าเซลล์ (cell faces) โดยใช้ Interpolation Schemes:

- **Linear Scheme**
- **Upwind Scheme**
- **Higher-order Schemes**

สร้างค่าที่จุดศูนย์กลางหน้า (face-centered values) จากค่าที่ไม่ทราบที่จุดศูนย์กลางเซลล์ (cell-centered unknowns)

#### 4. การประมาณค่าแบบดิสครีตเชิงเวลา (Temporal Discretization)
อนุพันธ์เทียบกับเวลา (Time derivatives) จะถูกประมาณค่าแบบดิสครีตโดยใช้ Schemes:

- **Euler Scheme** (อันดับหนึ่ง)
- **Backward Scheme** (อันดับสอง)
- **Crank-Nicolson Scheme** (อันดับสอง)

---

## โครงสร้าง Mesh และการทำให้เป็นดิสครีตเชิงพื้นที่

### แนวทางแบบ Cell-Centered

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

    classDef cell fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    classDef face fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    classDef point fill:#e8f5e9,stroke:#2e7d32,stroke-width:1px,color:#000;
    classDef vector fill:#fce4ec,stroke:#ad1457,stroke-width:1px,color:#000;
    classDef property fill:#f3e5f5,stroke:#7b1fa2,stroke-width:1px,color:#000;

    class P,N cell;
    class f face;
    class C_P,C_N,C_f point;
    class Sf,nf,Af vector;
    class V_P property;
```
> **Figure 4:** รายละเอียดทางเรขาคณิตของปริมาตรควบคุมแบบเน้นจุดศูนย์กลางเซลล์ แสดงความสัมพันธ์ระหว่างจุดศูนย์กลางเซลล์ ($P, N$), จุดศูนย์กลางหน้า ($f$) และเวกเตอร์พื้นผิว ($S_f$) ที่ใช้ใน OpenFOAM

ในแผนการนี้ **Flux** ของ mass, momentum และ energy จะถูกคำนวณและประเมินที่ Face ระหว่างเซลล์ที่อยู่ติดกัน เพื่อให้มั่นใจว่าสมการอนุรักษ์ในรูปปริพันธ์เป็นไปตามที่กำหนดไว้อย่างแม่นยำในแต่ละ Control Volume

**ข้อมูลทางเรขาคณิตที่จำเป็น**:
- ปริมาตรเซลล์ ($V_P$)
- พื้นที่ Face ($|\mathbf{S}_f|$)
- เวกเตอร์แนวฉากของ Face ($\mathbf{n}_f$)

แต่ละ Face มีเวกเตอร์พื้นที่ผิว $\mathbf{S}_f = \mathbf{n}_f A_f$ ที่ชี้จาก Owner Cell ไปยัง Neighbor Cell ข้อมูลทางเรขาคณิตนี้ช่วยให้สามารถคำนวณ:
- **Gradients**
- **Divergence Operations**
- **Flux Terms**

แนวทางแบบ Cell-Centered นำไปสู่ Sparse Linear System ที่สามารถแก้ไขได้อย่างมีประสิทธิภาพโดยใช้วิธี Iterative Methods

### องค์ประกอบทางเรขาคณิตที่สำคัญ

```mermaid
graph LR
    subgraph "Owner Cell P"
        P["<b>Cell Center P</b><br/><i>φ<sub>P</sub>, u<sub>P</sub>, p<sub>P</sub></i><br/>Control Volume"]
    end

    subgraph "Face f"
        f["<b>Face f</b><br/>Area: |S<sub>f</sub>|<br/>Normal: n<sub>f</sub>"]
    end

    subgraph "Neighbor Cell N"
        N["<b>Cell Center N</b><br/><i>φ<sub>N</sub>, u<sub>N</sub>, p<sub>N</sub></i><br/>Control Volume"]
    end

    subgraph "Geometric Vectors"
        Sf["<b>Surface Vector</b><br/>S<sub>f</sub> = n<sub>f</sub> × A<sub>f</sub>"]
        dPN["<b>Distance Vector</b><br/>d<sub>PN</sub> = r<sub>N</sub> - r<sub>P</sub>"]
        dPf["<b>Offset Vector</b><br/>d<sub>Pf</sub> = r<sub>f</sub> - r<sub>P</sub>"]
    end

    P -- "Owner → Face" --> f
    f -- "Face → Neighbor" --> N
    P -- "d<sub>PN</sub>" --> N
    P -- "S<sub>f</sub> (points outward)" --> f

    style P fill:#e3f2fd,stroke:#1565c0,stroke-width:3px,color:#000;
    style N fill:#e8f5e9,stroke:#2e7d32,stroke-width:3px,color:#000;
    style f fill:#fff9c4,stroke:#fbc02d,stroke-width:3px,color:#000;
    style Sf fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
    style dPN fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000;
    style dPf fill:#e0f2f1,stroke:#00695c,stroke-width:2px,color:#000;
```
> **Figure 5:** ความสัมพันธ์ของเวกเตอร์ในการ Discretization แบบ Finite Volume โดยกำหนดเวกเตอร์ระยะทาง $\mathbf{d}_{PN}$ และเวกเตอร์พื้นที่หน้า $\mathbf{S}_f$ ซึ่งจำเป็นสำหรับการคำนวณเกรเดียนต์และฟลักซ์ระหว่างเซลล์เจ้าของ ($P$) และเซลล์ข้างเคียง ($N$)

**องค์ประกอบทางเรขาคณิตที่สำคัญ**:
- **P**: Owner Cell Center - เก็บ Field Variables ($\phi_P$, $\mathbf{u}_P$, $p_P$)
- **N**: Neighbor Cell Center - เก็บ Field Variables ($\phi_N$, $\mathbf{u}_N$, $p_N$)
- **f**: Face Centroid - ทำการคำนวณ Flux
- **d**: เวกเตอร์ระยะห่าง $\mathbf{d}_{PN} = \mathbf{r}_N - \mathbf{r}_P$ ระหว่าง Cell Centers
- **S**: เวกเตอร์พื้นที่ Face $\mathbf{S}_f = \mathbf{n}_f A_f$ ชี้จาก Owner ไปยัง Neighbor

กระบวนการ Discretization ต้องมี **Interpolation** ค่า Field จาก Cell Centers ไปยัง Face Centroids เพื่อประเมิน Convective และ Diffusive Fluxes

**ประเภท Mesh และการจัดการ**:

| ประเภท Mesh | ลักษณะ | การจัดการ |
|-------------|---------|-------------|
| **Orthogonal Meshes** | เส้นที่เชื่อมต่อ Cell Centers P และ N ขนานกับเวกเตอร์แนวฉากของ Face $\mathbf{n}_f$ | การคำนวณ Gradient ง่ายขึ้น |
| **Non-Orthogonal Meshes** | ทิศทางไม่ขนานกัน | ต้องมีการรวม **Correction Terms** เพิ่มเติมเพื่อรักษาความแม่นยำ |

OpenFOAM ใช้แผนการต่างๆ ตั้งแต่ Explicit Corrections แบบง่าย ไปจนถึง Non-Linear Correction Methods ที่ซับซ้อนยิ่งขึ้น

---

## Discretization Schemes ใน OpenFOAM

OpenFOAM ใช้ Discretization Schemes หลายแบบที่สามารถเลือกได้ผ่าน Dictionary `fvSchemes` ใน `system` Directory

### การคำนวณ Gradient (Gradient Calculation)

Gradient ของฟิลด์ $\phi$ ที่จุดศูนย์กลางเซลล์ (cell centers) คำนวณโดยใช้ทฤษฎีบทของ Gauss (Gauss's theorem):
$$\nabla \phi_P \approx \frac{1}{V_P} \sum_f \phi_f \mathbf{S}_f$$

**นิยามตัวแปร:**
- $V_P$: ปริมาตรเซลล์ (cell volume)
- $\phi_f$: ค่าที่ถูกประมาณค่าแบบ Interpolate ที่หน้า (interpolated face value)
- $\mathbf{S}_f = \mathbf{n}_f A_f$: เวกเตอร์พื้นที่ผิว (surface area vector)

**OpenFOAM Code Implementation:**
```cpp
// การคำนวณ gradient ใน OpenFOAM
volScalarField gradPhi = fvc::grad(phi);
// ใช้ Gauss theorem และ interpolation schemes
```

### การอินทิเกรตเชิงเวลา (Temporal Integration)

สำหรับปัญหาแบบ Unsteady, OpenFOAM มี Temporal Schemes ที่หลากหลาย:

#### Implicit Euler Scheme (อันดับหนึ่ง)
$$\frac{\partial \phi}{\partial t} \approx \frac{\phi^{n+1} - \phi^n}{\Delta t}$$

#### Backward Scheme (อันดับสอง)
$$\frac{\partial \phi}{\partial t} \approx \frac{3\phi^{n+1} - 4\phi^n + \phi^{n-1}}{2\Delta t}$$

**OpenFOAM Code Implementation:**
```cpp
// การกำหนด temporal scheme ใน fvSchemes
ddtSchemes
{
    default         backward;  // หรือ Euler
}
```

### Divergence Schemes

ตัวดำเนินการ Divergence สำหรับเทอม Convection สามารถประมาณค่าแบบดิสครีตได้โดยใช้ Schemes ที่หลากหลาย:

| Scheme | ลำดับความแม่นยำ | คุณสมบัติ |
|--------|-------------------|-------------|
| **Upwind** | อันดับหนึ่ง | เสถียรสูง แต่มี numerical diffusion |
| **Linear** | อันดับสอง | แม่นยำแต่อาจไม่เสถียร |
| **TVD Schemes** | อันดับสอง | สมดุลระหว่างความแม่นยำและเสถียรภาพ |
| **LimitedLinear** | อันดับสอง | มีตัวจำกัดการกระจาย |

**OpenFOAM Code Implementation:**
```cpp
// การกำหนด divergence scheme ใน fvSchemes
divSchemes
{
    div(phi,U)      Gauss upwind;      // สำหรับ convection
    div(phi,k)      Gauss limitedLinear 1;  // สำหรับ turbulent kinetic energy
}
```

### การประเมิน Face Flux

#### นิพจน์ Flux ทั่วไป

ในกรอบ Finite Volume Terms การขนส่งทั้งหมดใน Governing Equations จะแสดงเป็น Fluxes ที่ผ่าน Cell Faces

$$\sum_f \mathbf{F}_f \cdot \mathbf{S}_f = 0$$

โดยที่:
- $\mathbf{F}_f$ แทน Flux Vector ที่ Face f
- $\mathbf{S}_f$ คือ Face Area Vector

**ความท้าทาย**: Field Variables ถูกเก็บไว้ที่ Cell Centers แต่การคำนวณ Flux ต้องการค่าที่ Face Centroids ดังนั้นจึงต้องใช้ **Interpolation Schemes** เพื่อประมาณค่า Face จากค่า Cell Center โดยรอบ

ความแม่นยำและเสถียรภาพของการจำลอง CFD ขึ้นอยู่กับการเลือก **Interpolation Schemes** อย่างมาก

#### 1. Convective Fluxes ($\nabla \cdot (\phi \mathbf{u})$)

Convective Fluxes แสดงถึงการขนส่งปริมาณ Scalar เนื่องจากการเคลื่อนที่ของของไหล และเป็นพื้นฐานของ Conservation Equations ใน CFD

**Term Convective สำหรับ Scalar Field $\phi$**:
$$\int_V \nabla \cdot (\phi \mathbf{u}) \, \mathrm{d}V = \sum_f \phi_f (\mathbf{u}_f \cdot \mathbf{S}_f) = \sum_f \phi_f \Phi_f$$

โดยที่ $\Phi_f = \mathbf{u}_f \cdot \mathbf{S}_f$ คือ **Volumetric Flux** ผ่าน Face f ซึ่งแสดงถึงอัตราการไหลเชิงปริมาตรที่ผ่าน Face นั้น

**Interpolation Schemes สำหรับ $\phi_f$**:

| Scheme | รูปแบบสมการ | ความแม่นยำ | ข้อดี | ข้อเสีย | กรณีที่เหมาะสม |
|--------|--------------|-------------|--------|--------|----------------|
| **CDS** (Central Differencing) | $\phi_f = 0.5(\phi_P + \phi_N)$ | Order 2 | High accuracy for smooth profiles | Unbounded oscillations in steep gradients | Laminar flow, fine meshes |
| **UDS** (Upwind) | $\phi_f = \phi_P$ if $\Phi_f > 0$<br>$\phi_f = \phi_N$ if $\Phi_f < 0$ | Order 1 | Numerically stable, bounded | Significant numerical diffusion | High convection, coarse meshes |
| **QUICK** | $\phi_f = \frac{6}{8}\phi_P + \frac{3}{8}\phi_N - \frac{1}{8}\phi_{NN}$ | Order 3 | Excellent accuracy | Can be unstable for high convection | Structured grids, smooth flows |
| **MUSCL/TVD** | $\phi_f = \phi_U + \phi(r) \cdot \frac{1}{2}(\phi_D - \phi_U)$ | Order 2 | High accuracy with boundedness | Complex implementation | General CFD applications |

#### 2. Diffusive Fluxes ($\nabla \cdot (\Gamma \nabla \phi)$)

Diffusive Fluxes แสดงถึงการขนส่งเนื่องจาก Spatial Gradients และปรากฏใน Momentum, Energy และ Species Conservation Equations

**Term Diffusive สำหรับ Scalar Field $\phi$ ที่มี Diffusion Coefficient $\Gamma$**:
$$\int_V \nabla \cdot (\Gamma \nabla \phi) \, \mathrm{d}V = \sum_f \Gamma_f (\nabla \phi)_f \cdot \mathbf{S}_f$$

**การประมาณค่า Gradient**:

สำหรับ Orthogonal Meshes ค่า Gradient ที่ Face จะถูกประมาณโดยใช้ Finite Differences ระหว่าง Adjacent Cell Centers:

$$(\nabla \phi)_f \cdot \mathbf{S}_f = |\mathbf{S}_f| \frac{\phi_N - \phi_P}{|\mathbf{d}_{PN}|}$$

Diffusion Coefficient ที่ Face จะถูก Interpolate โดยใช้ **Harmonic Averaging**:

$$\Gamma_f = \frac{2\Gamma_P \Gamma_N}{\Gamma_P + \Gamma_N}$$

**Non-Orthogonal Correction**:
สำหรับ Non-Orthogonal Meshes OpenFOAM ใช้ Correction Schemes ที่แยก Gradient ออกเป็น Orthogonal และ Non-Orthogonal Components:

$$(\nabla \phi)_f \cdot \mathbf{S}_f = |\mathbf{S}_f| \frac{\phi_N - \phi_P}{|\mathbf{d}_{PN}|} + \underbrace{(\nabla \phi)_{correct} \cdot (\mathbf{S}_f - \mathbf{d}_{PN} \frac{|\mathbf{S}_f|}{|\mathbf{d}_{PN}|})}_{\text{Non-orthogonal correction}}$$

---

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
> **Figure 6:** คุณสมบัติการอนุรักษ์โดยธรรมชาติใน FVM ซึ่งฟลักซ์ที่ออกจากปริมาตรควบคุมหนึ่งจะเท่ากับฟลักซ์ที่เข้าสู่ปริมาตรควบคุมที่อยู่ติดกันพอดี ทำให้มั่นใจได้ถึงการอนุรักษ์ในระดับรวม

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

## การประกอบเมทริกซ์ (Matrix Assembly)

### จากสมการสู่เมทริกซ์

สำหรับแต่ละเซลล์ เราจะได้สมการที่เชื่อมโยง $\phi_P$ กับเซลล์เพื่อนบ้าน $\phi_N$:
$$a_P \phi_P + \sum_N a_N \phi_N = b$$

เมื่อเราเขียนสมการนี้สำหรับ *ทุก* เซลล์ เราจะได้ระบบสมการเชิงเส้นขนาดใหญ่:
$$[A][x] = [b]$$

*   **[A]**: Sparse matrix ที่ประกอบด้วยสัมประสิทธิ์ ($a_P, a_N$) ซึ่งได้มาจากรูปทรงเรขาคณิตและฟลักซ์ (fluxes)
*   **[x]**: Vector of unknowns (เช่น Pressure ที่ทุกเซลล์)
*   **[b]**: Source vector ที่ประกอบด้วยเทอมที่ชัดเจน (explicit terms) และค่า Boundary values

OpenFOAM solvers (PCG, PBiCG) จะแก้สมการเมทริกซ์นี้ด้วยวิธีวนซ้ำ (iteratively)

### กรอบการทำงาน Finite Volume Discretization

รากฐานของการประกอบเมทริกซ์ใน OpenFOAM อยู่บน **Finite Volume Discretization** ของสมการอนุรักษ์ (conservation equations)

พิจารณาสมการ Scalar Transport ทั่วไป:

$$\frac{\partial (\rho \phi)}{\partial t} + \nabla \cdot (\rho \mathbf{u} \phi) = \nabla \cdot (\Gamma \nabla \phi) + S_\phi$$

การอินทิเกรตเหนือ Control Volume $V$ และการประยุกต์ใช้ Divergence Theorem:

$$\int_V \frac{\partial (\rho \phi)}{\partial t} \, \mathrm{d}V + \int_{\partial V} (\rho \mathbf{u} \phi) \cdot \mathbf{n} \, \mathrm{d}S = \int_{\partial V} (\Gamma \nabla \phi) \cdot \mathbf{n} \, \mathrm{d}S + \int_V S_\phi \, \mathrm{d}V$$

รูปแบบอินทิกรัลนี้จะถูกประมาณค่าโดยใช้ Face values และข้อมูลทางเรขาคณิตเพื่อสร้างสมการ Discrete สำหรับแต่ละเซลล์ $P$:

$$a_P \phi_P + \sum_{f} a_f \phi_{N_f} = b_P$$

โดยที่ผลรวมเกิดขึ้นเหนือทุก Face ของเซลล์ และ $N_f$ แสดงถึงเซลล์เพื่อนบ้านที่อยู่ตรงข้าม Face $f$

### ความเบาบางและการจัดเก็บเมทริกซ์ (Matrix Sparsity and Storage)

Coefficient matrix `[A]` ใน OpenFOAM แสดงโครงสร้างที่เบาบางมาก (highly sparse structure)

### คุณสมบัติความเบาบาง
*   สำหรับ Mesh แบบ 3D Unstructured ทั่วไปที่มีเซลล์ Polyhedral
*   จำนวน Non-zero Entries ต่อแถวโดยเฉลี่ยประมาณ 12-20
*   แสดงถึงเซลล์เพื่อนบ้านโดยตรงของแต่ละเซลล์

### รูปแบบการจัดเก็บ

| รูปแบบการจัดเก็บ | คำอธิบาย | การใช้งาน |
|---|---|---|
| **Compressed Sparse Row (CSR)** | รูปแบบการจัดเก็บเริ่มต้นที่แถวถูกจัดเก็บต่อเนื่องกัน | ค่าเริ่มต้นทั่วไป |
| **Diagonal storage** | สำหรับอัลกอริทึม Solver ที่ต้องการการเข้าถึง Diagonal บ่อยครั้ง | การปรับปรุงประสิทธิภาพ |
| **Symmetric storage** | เมื่อ Discretization ส่งผลให้เกิด Symmetric Coefficient Matrices | ปัญหา Symmetric |

### การนำ Boundary Condition ไปใช้

Boundary Conditions จะปรับเปลี่ยนสัมประสิทธิ์เมทริกซ์และ Source Terms ผ่าน:

| ประเภท Boundary Condition | วิธีการใช้งาน | ผลกระทบ |
|---|---|---|
| **Dirichlet (Fixed Value)** | วิธี Penalty ขนาดใหญ่ หรือการปรับเปลี่ยนโดยตรง | แก้ไข Diagonal และ Source |
| **Neumann (Gradient)** | Zero-gradient หรือ Specified Gradient | ปรับเฉพาะ Source Terms |
| **Mixed (Robin)** | การรวมกันของข้อจำกัดด้านค่าและ Gradient | แก้ไขทั้ง Diagonal และ Source |
| **Calculated** | คำนวณจากตัวแปรอื่น ๆ ระหว่างการวนซ้ำ | Dependent ตามตัวแปรอื่น |

กรอบการทำงานของ Boundary Condition จะจัดการการปรับเปลี่ยนเมทริกซ์ที่เหมาะสมโดยอัตโนมัติ ในขณะที่ยังคงรักษาเสถียรภาพเชิงตัวเลขและคุณสมบัติการลู่เข้า (convergence properties)

---

## การนำ OpenFOAM ไปใช้งาน

### คลาสหลัก

#### **fvMesh**: คลาสเมชพื้นฐานใน OpenFOAM

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
> **Figure 7:** ลำดับชั้นการสืบทอดของคลาส `fvMesh` ใน OpenFOAM แสดงการสืบทอดจาก `polyMesh` (โทโพโลยี) และ `fvFields` (ข้อมูลฟิลด์) เพื่อรองรับเมชแบบปริมาตรจำกัดทั้งแบบคงที่และแบบเคลื่อนที่

`fvMesh` รักษาโครงสร้างเมชที่สมบูรณ์ รวมถึง:

- **ข้อมูลทางเรขาคณิต (Geometric Data)**: ปริมาตรเซลล์, พื้นที่หน้า, จุดศูนย์กลางหน้า และจุดศูนย์กลางเซลล์ ที่คำนวณจากโครงสร้างโพลีฮีดรอลพื้นฐาน

- **ข้อมูลการเชื่อมต่อ (Connectivity Information)**: การประชิดกันของหน้าและเซลล์, ความสัมพันธ์ระหว่างจุดกับหน้า และการแมปหน้าขอบเขต ที่ช่วยให้เข้าถึงเพื่อนบ้านได้อย่างมีประสิทธิภาพ

- **การรองรับการเปลี่ยนแปลงตามเวลา (Time-varying Support)**: จัดการการเคลื่อนที่ของเมชและการเปลี่ยนแปลงโทโพโลยีผ่านคลาสอนุพันธ์ `dynamicFvMesh` สำหรับการประยุกต์ใช้เมชเคลื่อนที่

- **การจัดการขอบเขต (Boundary Management)**: จัดเก็บแพตช์ของ Boundary Condition และข้อมูลการดิสครีตที่เกี่ยวข้อง ซึ่งช่วยให้สามารถประยุกต์ใช้ Boundary Condition ได้โดยอัตโนมัติในระหว่างการประกอบสมการ

คลาส `fvMesh` สืบทอดมาจากทั้ง `polyMesh` (โครงสร้างโทโพโลยี) และ `fvFields` (การจัดเก็บฟิลด์) ซึ่งให้ส่วนต่อประสานที่เป็นหนึ่งเดียวสำหรับการดำเนินการดิสครีตเชิงพื้นที่

#### **volScalarField / volVectorField**: คลาสฟิลด์แบบเทมเพลต

คลาสฟิลด์แบบเทมเพลตเหล่านี้แสดงถึงตัวแปรที่กำหนด ณ จุดศูนย์กลางเซลล์ (จุดควบคุมปริมาตรจำกัด)

**OpenFOAM Code Implementation:**

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

**คุณสมบัติหลักได้แก่**:

- **รูปแบบการจัดเก็บ (Storage Pattern)**: ค่าที่จัดเก็บ ณ จุดศูนย์กลางเซลล์ พร้อมการจัดการ Boundary Condition โดยอัตโนมัติผ่านคลาส boundary field เฉพาะทาง

- **การดำเนินการฟิลด์ (Field Operations)**: รองรับการดำเนินการทางคณิตศาสตร์ ($+, -, *, /$) ด้วยการคำนวณแบบฟิลด์ต่อฟิลด์โดยอัตโนมัติ โดยใช้ expression templates เพื่อประสิทธิภาพ

- **การรวม Boundary Condition (Boundary Condition Integration)**: จัดการ Dirichlet/Neumann conditions โดยอัตโนมัติผ่านประเภท boundary field ที่สืบทอมา (เช่น fixedValue, fixedGradient, mixed)

- **การรวมเชิงเวลา (Time Integration)**: จัดเตรียมการจัดเก็บ `oldTime()` และ `newTime()` สำหรับ schemes การดิสครีตเชิงเวลา รองรับ schemes การก้าวเวลาแบบหลายระดับ

- **ประสิทธิภาพหน่วยความจำ (Memory Efficiency)**: ใช้การจัดเก็บแบบนับอ้างอิง (reference-counted storage) (คลาส `tmp`) และการจัดการการพึ่งพาฟิลด์โดยอัตโนมัติ เพื่อลดการใช้หน่วยความจำและภาระการคำนวณ

#### **surfaceScalarField**: ฟิลด์บนหน้าเซลล์

`surfaceScalarField` แสดงถึงปริมาณที่กำหนดบนหน้าเซลล์ ซึ่งมีความสำคัญอย่างยิ่งสำหรับการคำนวณฟลักซ์และการประมาณค่า gradient

ฟิลด์ประเภทนี้มีความสำคัญสำหรับ:

- **การคำนวณฟลักซ์ (Flux Calculations)**: ฟลักซ์มวล $\phi = \rho \mathbf{U} \cdot \mathbf{S}_f$ (ขนาดความเร็วที่หน้าคูณด้วยเวกเตอร์พื้นที่หน้า) คำนวณที่หน้าเซลล์แต่ละหน้า

- **การคำนวณ Gradient (Gradient Computation)**: schemes การประมาณค่าในช่วงบนพื้นผิวใช้ค่าที่หน้าเพื่อคำนวณ cell-centered gradients โดยใช้ทฤษฎีบทของเกาส์: $$\nabla \psi = \frac{1}{V}\sum_f \psi_f \mathbf{S}_f$$

- **Schemes การดิสครีต (Discretization Schemes)**: schemes การประมาณค่าในช่วงที่แตกต่างกัน (linear, upwind, QUICK, TVD) กำหนดวิธีการประมาณค่าในช่วงจากเซลล์ไปยังหน้า เพื่อรักษาสมดุลระหว่างความแม่นยำและความเสถียร

- **การบังคับใช้การอนุรักษ์ (Conservation Enforcement)**: รับรองความต่อเนื่องของฟลักซ์ข้ามหน้าเซลล์ รักษาคุณสมบัติการอนุรักษ์โดยรวมผ่านการกำหนดเครื่องหมายฟลักซ์หน้าที่ระมัดระวัง

Surface fields จะถูกคำนวณโดยอัตโนมัติจาก volume fields ในระหว่างการประกอบสมการโดยใช้ interpolation schemes

#### **fvMatrix**: หัวใจสำคัญของระบบพีชคณิตเชิงเส้น

`fvMatrix` คือหัวใจสำคัญของระบบพีชคณิตเชิงเส้นของ OpenFOAM ซึ่งแสดงถึงรูปแบบการดิสครีตของสมการเชิงอนุพันธ์ย่อย (partial differential equations)

```mermaid
graph TD
    A["Volume Field<br/>(Cell Center)"] -->|Interpolation| B["Surface Field<br/>(Face Center)"]
    B -->|Flux Calculation| C["Cell Face Gradient<br/>Gauss Theorem"]
    C -->|Discretization| D["fvMatrix Structure<br/>Sparse Linear System"]

    D --> E["Diagonal Coefficients<br/>A_D"]
    D --> F["Off-Diagonal Coefficients<br/>A_O"]
    D --> G["Source Vector<br/>b"]

    E --> H["Linear Solver<br/>Ax = b"]
    F --> H
    G --> H

    I["Interpolation Schemes"] --> B
    I --> J["Linear"]
    I --> K["Upwind"]
    I --> L["QUICK"]
    I --> M["TVD"]

    N["Conservation<br/>Principle"] --> C
    O["Boundedness<br/>Constraints"] --> B

    classDef process fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    classDef decision fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    classDef terminator fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
    classDef storage fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;

    class A,B,C,H process;
    class D,E,F,G storage;
    class I,J,K,L,M decision;
    class N,O terminator;
```
> **Figure 8:** การไหลของข้อมูลในกระบวนการประกอบ `fvMatrix` แสดงวิธีการประมาณค่าฟิลด์ปริมาตรจากจุดศูนย์กลางเซลล์ไปยังหน้าเซลล์ เพื่อสร้างระบบสมการเชิงเส้นแบบเบาบาง $[A][x] = [b]$ สำหรับตัวแก้สมการเชิงเส้น

เมทริกซ์นี้ใช้สมการ $\mathbf{A}\mathbf{x} = \mathbf{b}$ โดยที่:

- **เมทริกซ์ A (A-matrix)**: เมทริกซ์สัมประสิทธิ์ที่สร้างจากการดิสครีตแบบปริมาตรจำกัดของ derivative operators จัดเก็บในรูปแบบ sparse เพื่อประสิทธิภาพหน่วยความจำ

- **เวกเตอร์ x (x-vector)**: ค่าฟิลด์ที่ไม่ทราบค่า (เช่น ความดัน, องค์ประกอบความเร็ว) พร้อมการจัดเรียงอัตโนมัติตามการเชื่อมต่อของเมช

- **เวกเตอร์ b (b-vector)**: เทอมแหล่งกำเนิดที่มีส่วนร่วมแบบ explicit จาก Boundary Condition, source terms และองค์ประกอบการดิสครีตแบบ explicit

คลาส `fvMatrix` ให้การประกอบสมการที่ครอบคลุมผ่าน operator overloading:

**OpenFOAM Code Implementation:**

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

ระบบเมทริกซ์รองรับคุณสมบัติขั้นสูง ได้แก่:

- **การเชื่อมโยงเมทริกซ์ (Matrix coupling)**: การจัดการการพึ่งพาระหว่างสมการโดยอัตโนมัติผ่านการแยก operator แบบ explicit/implicit

- **สัมประสิทธิ์ Boundary Condition (Boundary condition coefficients)**: การรวม Boundary Condition โดยอัตโนมัติเข้าไปในสัมประสิทธิ์เมทริกซ์

- **การจัดการ Source Term (Source term management)**: การกำหนด Source Term ที่ยืดหยุ่นพร้อมการทำให้เป็นเชิงเส้นโดยอัตโนมัติ

- **ส่วนต่อประสาน Solver (Solver interface)**: การรวมเข้าโดยตรงกับ linear solvers ที่หลากหลาย (เช่น GAMG, PCG, PBiCG) และ preconditioners

### ตัวอย่างโค้ด: การแปลงสมการคณิตศาสตร์เป็นโค้ด

#### **สมการคณิตศาสตร์**:
$$\frac{\partial \rho \mathbf{U}}{\partial t} + \nabla \cdot (\phi \mathbf{U}) - \nabla \cdot (\mu \nabla \mathbf{U}) = -\nabla p$$

#### **การนิยามตัวแปร**:
- $\rho$ = ความหนาแน่นของของไหล (fluid density)
- $\mathbf{U}$ = เวกเตอร์ความเร็ว (velocity vector)
- $\mu$ = ความหนืดพลวัต (dynamic viscosity)
- $p$ = ความดัน (pressure)
- $\phi$ = เวกเตอร์ฟลักซ์มวล $\phi = \rho \mathbf{U}$ (mass flux vector)

นี่คือสมการการอนุรักษ์โมเมนตัมสำหรับการไหลแบบอัดตัวไม่ได้ (incompressible flow) ที่มีความหนาแน่น $\rho$, ความเร็ว $\mathbf{U}$, ความหนืดพลวัต $\mu$ และความดัน $p$ ที่เปลี่ยนแปลงได้

#### **OpenFOAM Code Implementation**:

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

## สรุป

**Finite Volume Method (FVM)** เป็นรากฐานที่แข็งแกร่งของ OpenFOAM สำหรับการแก้ปัญหา CFD ด้วยเหตุผลหลัก:

1. **การอนุรักษ์โดยธรรมชาติ**: รับประกันว่า Mass, Momentum และ Energy จะถูกอนุรักษ์ในระดับท้องถิ่นและโดยรวม

2. **ความยืดหยุ่นของ Mesh**: รองรับ Unstructured Meshes ที่ซับซ้อน รวมถึง Polyhedral Cells และ Non-orthogonal Geometries

3. **สถาปัตยกรรม C++ Template**: ให้การดำเนินการที่ Type-safe และมีประสิทธิภาพสูงบน Field Operations ที่หลากหลาย

4. **Discretization Schemes ที่หลากหลาย**: ให้ความสมดุลระหว่างความแม่นยำและความเสถียรสำหรับปัญหาที่หลากหลาย

5. **Sparse Matrix Systems**: การแก้ปัญหาที่มีประสิทธิภาพผ่าน Iterative Solvers และ Preconditioners

6. **การจัดการ Boundary Condition อัตโนมัติ**: การผนวก BCs เข้ากับ Matrix Systems โดยอัตโนมัติในขณะที่ยังคงคุณสมบัติการอนุรักษ์

> [!TIP] **คำแนะนำ**: เมื่อเริ่มต้นใช้งาน OpenFOAM ให้เริ่มต้นจากการใช้ Standard Schemes (Gauss linear สำหรับ gradient, Gauss upwind สำหรับ convection) และค่อยปรับแต่งเมื่อได้ความเข้าใจลักษณะของปัญหาที่กำลังแก้ไข

> [!INFO] **การเชื่อมโยง**: หัวข้อถัดไปจะกล่าวถึง [[02_Fundamental_Concepts]] ซึ่งจะอธิบายรายละเอียดเกี่ยวกับสมการควบคุม (Governing Equations) และการนำไปใช้ใน OpenFOAM
