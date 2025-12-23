# **เลขไร้มิติในการพลศาสตร์ของไหลเชิงคำนวณ**

เลขไร้มิติเป็นพารามิเตอร์พื้นฐานในพลศาสตร์ของไหลที่บ่งบอกถึงความสำคัญสัมพัทธ์ของปรากฏการณ์ทางฟิสิกส์ที่แข่งขันกัน


```mermaid
graph LR
    subgraph "Inertial Forces"
        A["Convective<br/>Inertial Forces"]
        B["Pressure Gradient<br/>Forces"]
    end

    subgraph "Viscous Forces"
        C["Viscous Shear<br/>Forces"]
        D["Molecular<br/>Diffusion"]
    end

    subgraph "External Forces"
        E["Gravity<br/>Forces"]
        F["Buoyancy<br/>Forces"]
        G["Surface Tension<br/>Forces"]
    end

    subgraph "Dimensionless Numbers"
        H["Reynolds Number<br/>Re = ρUL/μ"]
        I["Froude Number<br/>Fr = U/√(gL)"]
        J["Weber Number<br/>We = ρU²L/σ"]
        K["Euler Number<br/>Eu = ΔP/ρU²"]
    end

    A --> H
    C --> H

    A --> I
    E --> I

    A --> J
    G --> J

    B --> K
    A --> K

    classDef process fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    classDef decision fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    classDef terminator fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
    classDef storage fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;

    class A,B inertial
    class C,D viscous
    class E,F,G external
    class I,J,K dimensionless

    classDef inertial fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    classDef viscous fill:#ffecb3,stroke:#ff8f00,stroke-width:2px,color:#000;
    classDef external fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;
    classDef dimensionless fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000;
```
> **Figure 1:** การหาที่มาของเลขไร้มิติที่สำคัญ (Re, Fr, We, Eu) จากอัตราส่วนของแรงพื้นฐานต่าง ๆ (แรงเฉื่อย, แรงหนืด, แรงโน้มถ่วง, แรงดัน และแรงตึงผิว)


## **ประโยชน์ของเลขไร้มิติ**

เลขเหล่านี้ช่วยให้วิศวกรและนักวิจัยสามารถ:
- **คาดการณ์ระบอบการไหล** (Flow Regimes)
- **ระบุกลไกการถ่ายโอนที่สำคัญ**
- **ตัดสินใจอย่างมีข้อมูลเกี่ยวกับแนวทางการสร้างแบบจำลองที่เหมาะสม**

## **บทบาทใน OpenFOAM**

ในบริบทของการจำลอง OpenFOAM เลขไร้มิติเป็นแนวทางใน:
- **การสร้าง Mesh** (Grid Generation)
- **การเลือก Solver** (Solver Selection)
- **การเลือกแบบจำลอง Turbulence** (Turbulence Model Selection)

พวกมันเป็นรากฐานสำหรับการวิเคราะห์ **Dynamic Similarity** เพื่อให้มั่นใจว่าแบบจำลองเชิงคำนวณแสดงถึงฟิสิกส์ของระบบในโลกแห่งความเป็นจริงได้อย่างแม่นยำ

---

## **Reynolds Number ($Re$)**

Reynolds number อาจกล่าวได้ว่าเป็นพารามิเตอร์ไร้มิติที่สำคัญที่สุดในกลศาสตร์ของไหล ซึ่งแสดงถึงอัตราส่วนของแรงเฉื่อยต่อแรงหนืดในการไหล:

$$Re = \frac{\rho U L}{\mu} = \frac{\text{Inertial Forces}}{\text{Viscous Forces}}$$

โดยที่:
- $\rho$ = ความหนาแน่นของของไหล [kg/m³]
- $U$ = ความเร็วจำเพาะ [m/s]
- $L$ = มาตราส่วนความยาวจำเพาะ [m]
- $\mu$ = ความหนืดพลวัต [Pa·s]

### **Flow Regime Classification**

Reynolds number กำหนดระบอบการไหลและมีความสำคัญอย่างยิ่งต่อการทำนายการเปลี่ยนผ่านระหว่างการไหลแบบ Laminar และ Turbulent:

| ค่า Reynolds Number | ระบอบการไหล | ลักษณะการไหล |
|---------------------|--------------|----------------|
| $Re < 2300$ | Laminar | การไหลเป็นชั้นๆ ไม่มีการปนเปื้อน |
| $2300 < Re < 4000$ | Transitional | การเปลี่ยนผ่านจาก Laminar เป็น Turbulent |
| $Re > 4000$ | Turbulent | การไหลมีการปนเปื้อนและกระเพื่อม |

### **Characteristic Length ($L$)**

ความยาวจำเพาะ $L$ ขึ้นอยู่กับรูปทรงเรขาคณิต:
- **การไหลในท่อ**: Hydraulic Diameter
- **การไหลภายนอกเหนือแผ่นเรียบ**: ระยะห่างจากขอบนำ
- **การไหลรอบทรงกลม**: เส้นผ่านศูนย์กลางทรงกลม

### **Reynolds Number ในการจำลอง CFD**

Reynolds number ส่งผลโดยตรงต่อ:

#### **1. Turbulence Model Selection**
- $Re$ ต่ำ: แบบจำลอง Laminar
- $Re$ สูง: แนวทาง RANS, LES หรือ DNS

#### **2. Grid Resolution Requirements**
- $Re$ สูง: Mesh ที่ละเอียดขึ้นใกล้ผนังเพื่อจำลอง Boundary Layer
- $y^+ < 1$ สำหรับ Wall-resolved LES

#### **3. Time Step Constraints**
- ในการจำลองแบบ Transient: เงื่อนไข Courant-Friedrichs-Lewy (CFL)
- ได้รับผลกระทบจาก Reynolds number ผ่านมาตราส่วนความเร็วและความยาว

#### **4. Wall Treatment**
- การเลือกระหว่าง Wall Function และ Near-wall Resolution
- ขึ้นอยู่กับค่า $y^+$ ที่อิงตาม $Re$

### **OpenFOAM Code Implementation**

```cpp
// Example: Calculating Reynolds number in an OpenFOAM application
const dimensionedScalar Re
(
    "Re",
    dimensionSet(0, 0, 0, 0, 0, 0, 0),
    rho.value() * U.value() * L.value() / mu.value()
);

// In turbulence model selection (transportProperties dictionary)
simulationType   laminar;     // for Re < 2300
simulationType   RAS;         // for Re > 4000
simulationType   LES;         // for high Re with resolved turbulence
```

---

## **Froude Number ($Fr$)**

Froude number บ่งบอกถึงความสำคัญสัมพัทธ์ของแรงเฉื่อยต่อแรงโน้มถ่วง และมีความสำคัญอย่างยิ่งสำหรับการไหลที่มี Free Surface:

$$Fr = \frac{U}{\sqrt{gL}} = \sqrt{\frac{\text{Inertial Forces}}{\text{Gravitational Forces}}}$$

โดยที่:
- $U$ = ความเร็วจำเพาะ [m/s]
- $g$ = ความเร่งโน้มถ่วง [9.81 m/s²]
- $L$ = มาตราส่วนความยาวจำเพาะ [m]


```mermaid
graph LR
    A["Froude Number<br/>Fr = U/√(gL)"] --> B{"Flow Classification"}

    B -->|Fr < 1| C["Subcritical Flow<br/>(Tranquil)"]
    B -->|Fr = 1| D["Critical Flow<br/>(Fr = 1)"]
    B -->|Fr > 1| E["Supercritical Flow<br/>(Rapid)"]

    C --> F["Slow flow<br/>Large depth<br/>Disturbances travel upstream"]
    D --> G["Critical depth<br/>Fr = 1<br/>Maximum specific energy"]
    E --> H["Fast flow<br/>Shallow depth<br/>Disturbances cannot travel upstream"]

    I["Free Surface Effects"] --> J["Wave formation"]
    I --> K["Hydraulic jumps"]
    I --> L["Weir flow"]
    I --> M["Open channel flow"]

    style A fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
    style B fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000
    style C fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000
    style D fill:#fff3e0,stroke:#ef6c00,stroke-width:2px,color:#000
    style E fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000
    style I fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000
    classDef process fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
    classDef decision fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000
    classDef storage fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000
```
> **Figure 2:** การจำแนกการไหลตามเลขฟรูด ($Fr$) แสดงการเปลี่ยนผ่านจากระบอบการไหลแบบ Subcritical ไปสู่ Supercritical และปรากฏการณ์ทางกายภาพที่เกี่ยวข้อง (คลื่น, Hydraulic jumps)



### **Flow Classification by Froude Number**

| ค่า Froude Number | ระบอบการไหล   | ลักษณะการไหล                             |
| ----------------- | ------------- | ---------------------------------------- |
| $Fr < 1$          | Subcritical   | การไหลสงบ คลื่นสามารถแพร่ทวนน้ำได้       |
| $Fr = 1$          | Critical      | สภาวะวิกฤต Hydraulic Jump                |
| $Fr > 1$          | Supercritical | การไหลรวดเร็ว การรบกวนไม่สามารถทวนน้ำได้ |

Froude number มีความสำคัญอย่างยิ่งใน:
- **การไหลแบบ Free Surface**
- **วิศวกรรมไฮดรอลิก**
- **สถาปัตยกรรมเรือ**

### **Froude Number Applications**

ในการไหลแบบ Multiphase ที่เกี่ยวข้องกับ Gas-Liquid Interface, Froude number ส่งผลต่อ:

#### **1. Wave Phenomena**
- Surface Wave
- Capillary Wave
- Gravity Wave

#### **2. Interface Stability**
- Kelvin-Helmholtz instability
- Rayleigh-Taylor instability

#### **3. Gravity-Driven Flows**
- สถานการณ์เขื่อนแตก
- หิมะถล่ม
- Debris Flow

#### **4. Ship Hydrodynamics**
- แรงต้านของเรือ
- รูปแบบ Wake
- Vortex Shedding
- Wave Drag

#### **5. Open Channel Flow**
- Hydraulic Jump
- Flow Transition

### **OpenFOAM Implementation**

สำหรับการไหลแบบ Free Surface ใน OpenFOAM, Froude number เป็นแนวทางในการเลือก Solver:

```cpp
// interFoam solver for two-phase incompressible flow
// Suitable for Fr ~ 0.1 - 10 (subcritical to supercritical)
solver interFoam;

// MultiphaseEulerFoam for general multiphase flows
// Handles wide range of Fr including gravity-driven flows
solver multiphaseEulerFoam;

// Example: Setting gravitational acceleration in constant/g
dimensionedVector g
(
    "g",
    dimensionSet(0, 1, -2, 0, 0, 0, 0),
    vector(0, 0, -9.81)
);
```

---

## **Mach Number ($Ma$)**

Mach number แสดงถึงอัตราส่วนของความเร็วการไหลต่อความเร็วเสียงเฉพาะที่ และเป็นพื้นฐานสำหรับการวิเคราะห์การไหลแบบ Compressible:

$$Ma = \frac{U}{c} = \frac{\text{Flow Velocity}}{\text{Speed of Sound}}$$

โดยที่:
- $U$ = ความเร็วการไหล [m/s]
- $c$ = ความเร็วเสียงเฉพาะที่ [m/s]
- $c = \sqrt{\gamma R T}$ สำหรับ Ideal Gas
- $\gamma$ = อัตราส่วนความร้อนจำเพาะ (≈ 1.4 สำหรับอากาศ)
- $R$ = ค่าคงที่ของก๊าซจำเพาะ [J/(kg·K)]
- $T$ = อุณหภูมิสัมบูรณ์ [K]


```mermaid
graph LR
    A["Flow Velocity U"] --> B["Mach Number<br/>Ma = U/c"]
    B --> C{"Flow Regimes"}

    C -->|Ma < 0.3| D["Incompressible<br/>ρ ≈ constant"]
    C -->|0.3 < Ma < 0.8| E["Subsonic Compressible<br/>Density varies"]
    C -->|0.8 < Ma < 1.2| F["Transonic<br/>Shocks mixed"]
    C -->|Ma > 1.2| G["Supersonic<br/>Strong Shocks"]

    D --> H["Solvers:<br/>simpleFoam<br/>pimpleFoam"]
    E --> I["Solvers:<br/>rhoSimpleFoam<br/>rhoPimpleFoam"]
    F --> J["Solvers:<br/>sonicFoam<br/>rhoCentralFoam"]
    G --> J

    H --> K["No EOS needed<br/>or Incompressible"]
    I --> L["Equation of State<br/>p = ρRT"]
    J --> M["Shock Capturing<br/>Schemes"]

    style A fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
    style B fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000
    style C fill:#fff3e0,stroke:#ef6c00,stroke-width:2px,color:#000
    style D fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000
    style E fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000
    style F fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000
    style G fill:#fbe9e7,stroke:#bf360c,stroke-width:2px,color:#000
```
> **Figure 3:** การจำแนกระบอบการไหลแบบอัดตัวได้ตามเลขมัค ($Ma$) โดยรายละเอียดการเปลี่ยนผ่านจากการไหลแบบอัดตัวไม่ได้ไปสู่ความเร็วเหนือเสียง และข้อกำหนดของ Solver ใน OpenFOAM ที่เกี่ยวข้อง



### **Mach Number Flow Regimes**

| ค่า Mach Number | ระบอบการไหล | ผลกระทบของ Compressibility |
|-----------------|---------------|------------------------------|
| $Ma < 0.3$ | Incompressible | ความแปรผันของความหนาแน่นน้อยมาก |
| $0.3 < Ma < 0.8$ | Subsonic Compressible | มีผลกระทบของ compressibility เล็กน้อย |
| $Ma = 1$ | Sonic | สภาวะวิกฤต การไหลผ่านความเร็วเสียง |
| $0.8 < Ma < 1.2$ | Transonic | บริเวณ Subsonic/Supersonic ผสมกัน |
| $Ma > 1.2$ | Supersonic | การไหลเร็วกว่าเสียง Shock Wave ก่อตัว |
| $Ma > 5$ | Hypersonic | ผลกระทบจากอุณหภูมิสูงเพิ่มเติม |

### **Compressibility Effects in CFD**

ในการจำลอง CFD, ผลกระทบของการ Compressibility มีนัยสำคัญเมื่อ $Ma > 0.3$ ซึ่งต้องใช้:

#### **1. Coupled Solution**
- การแก้สมการ Momentum และ Energy แบบ Coupled
- ความแปรผันของความหนาแน่นส่งผลต่อ Pressure และ Velocity Field

#### **2. Equation of State**
- Ideal Gas ($p = \rho R T$)
- หรือแบบจำลองที่ซับซ้อนกว่า

#### **3. Shock Wave Handling**
- Scheme ที่มีความละเอียดสูง
- วิธี Shock-Capturing

#### **4. Boundary Conditions**
- Characteristic Boundary Condition
- สำหรับการไหลแบบ Supersonic

### **OpenFOAM Solver Selection**

OpenFOAM มี Solver เฉพาะทางสำหรับระบอบ Mach number ที่แตกต่างกัน:

```cpp
// Low Mach number (Ma < 0.3) - incompressible solvers
solver simpleFoam;        // Steady-state
solver pimpleFoam;        // Transient
solver icoFoam;          // Laminar transient

// Compressible flow solvers (Ma > 0.3)
solver rhoSimpleFoam;     // Steady compressible
solver rhoPimpleFoam;     // Transient compressible
solver sonicFoam;        // Transonic/supersonic flow

// High-speed flow with shock waves
solver reactingFoam;      // Combustion with compressibility

// Thermophysical properties for compressible flow
thermoType
{
    type            heRhoThermo;
    mixture         pureMixture;
    transport       sutherland;
    thermo          hConst;
    energy          sensibleEnthalpy;
    equationOfState perfectGas;
    specie          specie;
}
```

---

## **เลขไร้มิติที่สำคัญอื่นๆ**

ในขณะที่ Reynolds, Froude และ Mach number เป็นที่ใช้บ่อยที่สุดใน CFD แต่พารามิเตอร์ไร้มิติอื่นๆ อีกหลายตัวก็มีความสำคัญอย่างยิ่งสำหรับแอปพลิเคชันเฉพาะ:

### **Prandtl Number ($Pr$)**

$$Pr = \frac{c_p \mu}{k} = \frac{\text{Momentum Diffusivity}}{\text{Thermal Diffusivity}}$$

**ความสำคัญ:**
- จำเป็นสำหรับแอปพลิเคชันการถ่ายเทความร้อน
- $Pr \approx 0.7$ สำหรับก๊าซ
- $Pr \approx 7$ สำหรับน้ำ
- ส่งผลต่อความหนาของ Thermal Boundary Layer สัมพัทธ์กับ Velocity Boundary Layer


```mermaid
graph LR
    subgraph "Low Pr Number (Pr < 1)"
        A["Gases<br/>(Pr ≈ 0.7)"]
        B["Thermal Boundary Layer<br/>THICKER<br/>than Velocity Layer"]
        C["Thermal Diffusivity<br/>HIGHER than Momentum"]
        A --> B --> C
    end

    subgraph "High Pr Number (Pr > 1)"
        D["Liquids<br/>(Pr ≈ 7)"]
        E["Thermal Boundary Layer<br/>THINNER<br/>than Velocity Layer"]
        F["Momentum Diffusivity<br/>HIGHER than Thermal"]
        D --> E --> F
    end

    G["Critical Applications"]
    H["Heat Exchangers"]
    I["Electronic Cooling"]
    J["Gas Turbines"]
    K["Chemical Reactors"]

    G --> H
    G --> I
    G --> J
    G --> K

    classDef process fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    classDef decision fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    classDef terminator fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
    classDef storage fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;

    class A,B,C,D,E,F process
    class G decision
    class H,I,J,K storage
```
> **Figure 4:** ผลกระทบของเลขพรานดท์ ($Pr$) ต่อฟิสิกส์ของชั้นขอบเขต โดยเปรียบเทียบความหนาสัมพัทธ์ของชั้นขอบเขตความร้อนและชั้นขอบเขตความเร็วสำหรับก๊าซ ($Pr$ ต่ำ) และของเหลว ($Pr$ สูง)



### **Schmidt Number ($Sc$)**

$$Sc = \frac{\mu}{\rho D} = \frac{\text{Momentum Diffusivity}}{\text{Mass Diffusivity}}$$

**ความสำคัญ:**
- มีความสำคัญอย่างยิ่งต่อ Mass Transfer และ Species Transport
- $Sc \approx 0.7$ สำหรับก๊าซในอากาศ
- ใช้ในการสร้างแบบจำลองการเผาไหม้และการกระจายมลพิษ

### **Weber Number ($We$)**

$$We = \frac{\rho U^2 L}{\sigma} = \frac{\text{Inertial Forces}}{\text{Surface Tension Forces}}$$

**ความสำคัญ:**
- สำคัญสำหรับการไหลแบบ Multiphase ที่มีแรงตึงผิว
- ควบคุมการแตกตัวของ Droplet, การก่อตัวของ Bubble และ Spray Dynamics
- $We > 12$ บ่งชี้ถึงการแตกตัวของ Droplet ใน Spray

### **Strouhal Number ($St$)**

$$St = \frac{f L}{U} = \frac{\text{Vortex Shedding Frequency} \times \text{Length}}{\text{Velocity}}$$

**ความสำคัญ:**
- บ่งบอกถึงความถี่ Vortex Shedding
- $St \approx 0.2$ สำหรับทรงกระบอกกลมในการไหลขวาง
- สำคัญสำหรับการวิเคราะห์การสั่นสะเทือนที่เกิดจากการไหล


```mermaid
graph LR
    A["Fluid Flow"] --> B["Cylinder"]
    B --> C["Vortex Formation"]
    C --> D["Alternating Vortices"]
    D --> E["Kármán Vortex Street"]

    F["Strouhal Number St = fL/U"] --> B
    G["St ≈ 0.2<br/>(Typical Value)"] --> F
    H["f: Vortex Shedding<br/>Frequency"] --> F
    I["L: Characteristic<br/>Length"] --> F
    J["U: Flow Velocity"] --> F

    K["Flow Parameters"] --> L["Reynolds Number"]
    L --> M["Flow Regime"]
    M --> C

    style A fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    style B fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    style C fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
    style D fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
    style E fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;
    style F fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    style G fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    style K fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;
    style L fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    style M fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
```
> **Figure 5:** กลไกการหลุดของ Vortex แบบ von Kármán จากทรงกระบอก ซึ่งอธิบายโดยเลขสเตราฮัล ($St$) ที่เชื่อมโยงความถี่ของการหลุดเข้ากับความเร็วการไหลและความยาวลักษณะเฉพาะ

---

## **เลขไร้มิติในการสร้างแบบจำลอง Turbulence**

Turbulence Model ใน OpenFOAM อิงตามพารามิเตอร์ไร้มิติโดยธรรมชาติ:

### **Wall Y-plus ($y^+$)**

$$y^+ = \frac{y u_\tau}{\nu} = \frac{\text{Distance from Wall} \times \text{Friction Velocity}}{\text{Kinematic Viscosity}}$$

**ความสำคัญ:**
- มีความสำคัญอย่างยิ่งต่อการจัดการใกล้ผนังใน RANS Model

| ค่า $y^+$ | บริเวณ | การจัดการ |
|-----------|--------|-------------|
| $y^+ < 5$ | Viscous Sublayer | จำลองได้ (Direct Simulation) |
| $5 < y^+ < 30$ | Buffer Layer | การเปลี่ยนผ่าน |
| $30 < y^+ < 300$ | Log Layer | Wall Function |

### **Turbulence Intensity ($I$)**

$$I = \frac{u'}{U_{avg}} = \frac{\text{RMS of velocity fluctuations}}{\text{Mean velocity}}$$

**ความสำคัญ:**
- ใช้สำหรับการเริ่มต้น Turbulence Model
- $I \approx 0.16 Re^{-1/8}$ สำหรับการไหลในท่อ
- ค่าทั่วไป:
  - การไหลสงบ: $I < 1\%$
  - การไหลปานกลาง: $I = 1-5\%$
  - การไหลอย่างรุนแรง: $I > 5\%$

### **Summary Table: Dimensionless Numbers in OpenFOAM**

| พารามิเตอร์ | สูตร | การใช้งานหลัก | Solver ที่เกี่ยวข้อง |
|--------------|-------|------------------|---------------------|
| Reynolds ($Re$) | $\frac{\rho U L}{\mu}$ | การทำนายระบอบการไหล | simpleFoam, pimpleFoam, icoFoam |
| Froude ($Fr$) | $\frac{U}{\sqrt{gL}}$ | การไหลแบบ Free Surface | interFoam, multiphaseEulerFoam |
| Mach ($Ma$) | $\frac{U}{c}$ | การไหลแบบ Compressible | sonicFoam, rhoSimpleFoam |
| Prandtl ($Pr$) | $\frac{c_p \mu}{k}$ | การถ่ายเทความร้อน | buoyantFoam, reactingFoam |
| Schmidt ($Sc$) | $\frac{\mu}{\rho D}$ | Mass Transfer | reactingFoam, scalarTransportFoam |
| Weber ($We$) | $\frac{\rho U^2 L}{\sigma}$ | Surface Tension Effects | interFoam, multiphaseEulerFoam |
| Strouhal ($St$) | $\frac{f L}{U}$ | Vortex Shedding | pimpleFoam (transient) |

---

## **ขั้นตอนการประยุกต์ใช้เลขไร้มิติใน OpenFOAM**

เพื่อใช้ประโยชน์จากเลขไร้มิติอย่างเต็มที่ในการจำลอง OpenFOAM ให้ทำตามขั้นตอนเหล่านี้:

### **1. Pre-Simulation Analysis**

```cpp
// คำนวณเลขไร้มิติจากเงื่อนไขการทำงาน
scalar Re = rho * U * L / mu;
scalar Ma = U / sqrt(gamma * R * T);
scalar Fr = U / sqrt(g * L);
```

### **2. Solver Selection**

> [!INFO] **การเลือก Solver ที่เหมาะสม**
> - ถ้า $Re < 2300$: ใช้ `icoFoam` หรือ `simpleFoam` แบบ laminar
> - ถ้า $Re > 4000$: ใช้ `simpleFoam` หรือ `pimpleFoam` พร้อม turbulence model
> - ถ้า $Ma > 0.3$: ใช้ compressible solvers เช่น `rhoSimpleFoam`
> - ถ้ามี free surface: ใช้ `interFoam`

### **3. Mesh Design Considerations**

```cpp
// สำหรับ high Re flows: ตรวจสอบ y+ values
// ใช้ utility: yPlusRAS หรือ yPlusLES
yPlus < 5   // สำหรับ wall-resolved LES/DNS
30 < yPlus < 300  // สำหรับ wall functions
```

### **4. Boundary Condition Setup**

```cpp
// ใช้ turbulence intensity สำหรับ inlet boundaries
// ใน 0/k
turbulence   kepsilon;  // หรือ kOmegaSST

k             uniform <I*U^2*3/2>;
epsilon       uniform <C_mu^0.75*k^1.5/l>;
```

### **5. Convergence Criteria**

```cpp
// ใช้ knowledge ของ flow regime สำหรับการตั้งค่า tolerance
solvers
{
    p
    {
        solver          GAMG;
        tolerance       1e-06;  // สำหรับ steady flows
        relTol          0.1;
    }
}
```

---

**บทสรุป**: เลขไร้มิติเป็นเครื่องมือพื้นฐานในการวิเคราะห์และสร้างแบบจำลอง CFD ใน OpenFOAM พวกเขาให้ความเข้าใจเชิงลึกเกี่ยวกับฟิสิกส์ที่ควบคุมการไหล ช่วยในการเลือก Solver และ Turbulence Model ที่เหมาะสม และแนะนำความต้องการของ Mesh และ Boundary Condition การเข้าใจและนำไปใช้เลขไร้มิติเหล่านี้อย่างถูกต้องเป็นกุญแจสำคัญสู่การจำลอง CFD ที่แม่นยำและเชื่อถือได้