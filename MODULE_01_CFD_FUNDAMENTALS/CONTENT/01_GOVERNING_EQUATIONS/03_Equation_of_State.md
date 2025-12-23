# สมการสถานะ (Equation of State - EOS)

**สมการสถานะ** เป็นความสัมพันธ์พื้นฐานในพลศาสตร์ของไหลที่เชื่อมโยงสมบัติทางอุณหพลศาสตร์ เช่น ความดัน ความหนาแน่น และอุณหภูมิ ซึ่งเป็นการปิดระบบสมการควบคุม (governing equations) ให้สมบูรณ์

ใน **OpenFOAM**, EOS มีความสำคัญอย่างยิ่งต่อการกำหนดพฤติกรรมทางกายภาพของของไหลในการจำลอง:

- **การไหลแบบอัดตัวได้** (Compressible Flow)
- **การไหลแบบอัดตัวไม่ได้** (Incompressible Flow)

---

## ภาพรวมความสำคัญของสมการสถานะ

สมการสถานะทำหน้าที่เชื่อมโยงตัวแปรทางอุณหพลศาสตร์สามตัวที่สำคัญที่สุดในพลศาสตร์ของไหล:

```mermaid
graph TD
    P["Pressure: p<br/>Pascal (Pa)"] --> E["Equation of State<br/>Relates P, ρ, T"]
    RHO["Density: ρ<br/>kg/m³"] --> E
    T["Temperature: T<br/>Kelvin (K)"] --> E
    E --> IDEAL["Ideal Gas Law<br/>p = ρRT"]
    IDEAL --> VARIABLES["Variables:<br/>R = Specific gas constant<br/>T = Absolute temperature<br/>ρ = Density<br/>p = Pressure"]
    E --> THERMO["Thermodynamic<br/>Consistency"]

    E --> COMP["Compressible Flow<br/>ρ varies with p, T"]
    E --> INCOMP["Incompressible Flow<br/>ρ = constant"]

    COMP --> SOLVER1["rhoSimpleFoam<br/>rhoPimpleFoam<br/>sonicFoam"]
    INCOMP --> SOLVER2["simpleFoam<br/>pimpleFoam<br/>icoFoam"]

    %% Styling Definitions
    classDef process fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    classDef decision fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    classDef terminator fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
    classDef storage fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;

    class P,RHO,T process
    class E decision
    class IDEAL,VARIABLES,SOLVER1,SOLVER2 storage
    class THERMO,COMP,INCOMP terminator
```

---

## กฎแก๊สอุดมคติ (Ideal Gas Law)

### รูปแบบสมการ

สำหรับการไหลแบบอัดตัวได้ กฎแก๊สอุดมคติให้ความสัมพันธ์ระหว่างความดัน ($p$) ความหนาแน่น ($\rho$) และอุณหภูมิ ($T$) ดังนี้:

$$p = \rho R T$$

**โดยที่:**
- $p$ คือ ความดันสัมบูรณ์ [Pa]
- $\rho$ คือ ความหนาแน่นของไหล [kg/m³]
- $R$ คือ ค่าคงที่แก๊สจำเพาะ [J/(kg·K)]
- $T$ คือ อุณหภูมิสัมบูรณ์ [K]

### ข้อสมมติพื้นฐาน

กฎแก๊สอุดมคติอาศัยข้อสมมติต่อไปนี้:

> [!INFO] ข้อสมมติของแก๊สอุดมคติ
> - ของไหลมีพฤติกรรมเป็นแก๊สอุดมคติ
> - ใช้ได้กับแก๊สส่วนใหญ่ที่อุณหภูมิและความดันปกติ
> - ปฏิสัมพันธ์ระดับโมเลกุลมีค่าน้อยมาก
> - ปริมาตรของโมเลกุลแก๊สเมื่อเทียบกับปริมาตรรวมเพิกเฉยได้

### ความสัมพันธ์กับค่าคงที่แก๊สสากล

ค่าคงที่แก๊สจำเพาะ ($R$) เกี่ยวข้องกับค่าคงที่แก๊สสากล ($R_{universal}$) ดังนี้:

$$R = \frac{R_{universal}}{M}$$

โดยที่:
- $R_{universal} = 8314$ J/(kmol·K)
- $M$ คือ มวลโมเลกุล [kg/kmol]

ตัวอย่าง:
- อากาศ ($M \approx 29$ kg/kmol): $R \approx 287$ J/(kg·K)
- ฮีเลียม ($M \approx 4$ kg/kmol): $R \approx 2077$ J/(kg·K)

### OpenFOAM Code Implementation

```cpp
// โมเดลทางอุณหพลศาสตร์สำหรับแก๊สอุดมคติ
thermoType
{
    type            hePsiThermo;
    mixture         pureMixture;
    transport       const;
    thermo          hConst;
    equationOfState perfectGas;    // สิ่งที่ Implement: p = ρRT
    specie          specie;
    energy          sensibleEnthalpy;
}

// การกำหนดค่าคงที่แก๊สจำเพาะ
specie
{
    molWeight       28.9;           // มวลโมเลกุล [g/mol] สำหรับอากาศ
}
```

> [!TIP] การเลือก Solver สำหรับแก๊สอุดมคติ
> สำหรับการไหลแบบอัดตัวได้ที่ใช้กฎแก๊สอุดมคติ ให้ใช้ Solver:
> - `rhoSimpleFoam` - สำหรับสภาวะคงตัว (Steady-state)
> - `rhoPimpleFoam` - สำหรับไม่คงที่ (Transient)
> - `sonicFoam` - สำหรับการไหล Transonic/Supersonic

---

## ของไหลที่อัดตัวไม่ได้ (Incompressible Fluid)

### รูปแบบสมการ

สำหรับของเหลว เช่น น้ำ ความหนาแน่นยังคงที่โดยพื้นฐาน:

$$\rho = \text{constant}$$

### เงื่อนไขที่ใช้ได้

> [!WARNING] เงื่อนไขการใช้แบบจำลอง Incompressible
> - การเปลี่ยนแปลงความดันมีค่าน้อยเมื่อเทียบกับ Bulk Modulus
> - การเปลี่ยนแปลงอุณหภูมิไม่ส่งผลกระทบต่อความหนาแน่นอย่างมีนัยสำคัญ
> - **เลข Mach โดยทั่วไปน้อยกว่า 0.3**

### ความสำคัญของเลข Mach

เลข Mach ($Ma$) เป็นตัวบ่งชี้ที่สำคัญว่าจะใช้สมการสถานะแบบใด:

$$Ma = \frac{U}{c} = \frac{\text{Flow Velocity}}{\text{Speed of Sound}}$$

| ค่า Mach Number | ระบอบการไหล | สมการสถานะที่เหมาะสม |
|-----------------|---------------|------------------------------|
| $Ma < 0.3$ | Incompressible | $\rho = \text{constant}$ |
| $0.3 < Ma < 0.8$ | Subsonic Compressible | $p = \rho R T$ |
| $Ma > 0.8$ | Transonic/Supersonic | $p = \rho R T$ + Shock Capturing |

### ประโยชน์ของการใช้แบบจำลอง Incompressible

- ✅ ช่วยลดความต้องการในการคำนวณลงอย่างมาก
- ✅ ยังคงความแม่นยำสำหรับการไหลของของเหลวที่ความเร็วต่ำ
- ✅ ไม่จำเป็นต้องแก้สมการพลังงานสำหรับการคำนวณความหนาแน่น

```mermaid
graph LR
    A[Start] --> B{Flow Type?}
    B -->|Compressible| C[Gas Properties]
    C --> D[Density ρ varies with p,T]
    D --> E[Ideal Gas Equation: ρ = p/RT]
    E --> F[Required for: <br/>Mach > 0.3<br/>Large pressure changes]

    B -->|Incompressible| G[Liquid Properties]
    G --> H[Density ρ = constant]
    H --> I[Ideal for: <br/>Mach < 0.3<br/>Small pressure changes]
    I --> J[Computational efficiency]

    F --> K[Applications: <br/>Aerodynamics<br/>High-speed flows]
    J --> L[Applications: <br/>Pipe flow<br/>Low-speed liquids]

    classDef process fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    classDef decision fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    class A,B,C,D,E,F,G,H,I,J,K,L process
```

### OpenFOAM Code Implementation

```cpp
// โมเดลทางอุณหพลศาสตร์สำหรับของไหลที่อัดตัวไม่ได้
thermoType
{
    type            hePsiThermo;
    mixture         pureMixture;
    transport       const;
    thermo          hConst;
    equationOfState incompressible;  // สิ่งที่ Implement: ρ = constant
    specie          specie;
    energy          sensibleEnthalpy;
}

// การกำหนดความหนาแน่น
specie
{
    molWeight       18.0;           // มวลโมเลกุล [g/mol] สำหรับน้ำ
    rho             1000;           // ความหนาแน่น [kg/m³]
}
```

---

## การนำไปใช้ใน OpenFOAM

### ไฟล์ `thermophysicalProperties`

**ไฟล์ `thermophysicalProperties`** เป็นที่ที่ EOS จะถูกระบุในแอปพลิเคชัน OpenFOAM ไฟล์นี้ปกติอยู่ในโฟลเดอร์ `constant/` ของ case ของคุณ

```cpp
// ไฟล์: constant/thermophysicalProperties

/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  10                                    |
|   \\  /    A nd           | Web:      www.OpenFOAM.org                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "constant";
    object      thermophysicalProperties;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

thermoType
{
    type            hePsiThermo;
    mixture         pureMixture;
    transport       sutherland;
    thermo          hConst;
    equationOfState perfectGas;
    specie          specie;
    energy          sensibleEnthalpy;
}

mixture
{
    specie
    {
        molWeight       28.9;
    }
    thermodynamics
    {
        Cp              1007;          // ความจุความร้อนจำเพาะ [J/kg·K]
        Hf              0;             // เอนทาลปีของการก่อตัว [J/kg]
    }
    transport
    {
        mu              1.8e-05;       // ความหนืดจลน์ [Pa·s]
        Pr              0.7;           // เลข Prandtl
    }
}

// ************************************************************************* //
```

### ผลกระทบต่อสมการควบคุม

การเลือกสมการสถานะส่งผลโดยตรงต่อ:

#### 1. สมการความต่อเนื่อง (Continuity Equation)

**สำหรับการไหลแบบอัดตัวได้:**
$$\frac{\partial \rho}{\partial t} + \nabla \cdot (\rho \mathbf{u}) = 0$$

**สำหรับการไหลแบบอัดตัวไม่ได้:**
$$\nabla \cdot \mathbf{u} = 0$$

#### 2. การเชื่อมโยงระหว่างสมการโมเมนตัมและสมการพลังงาน

ในการไหลแบบอัดตัวได้:
- ความหนาแน่น $\rho$ เปลี่ยนแปลงตามความดันและอุณหภูมิ
- สมการโมเมนตัมและพลังงาน **จะต้องถูกแก้แบบ coupled**
- ต้องใช้ Equation of State ในการคำนวณความหนาแน่นในแต่ละ time step

ในการไหลแบบอัดตัวไม่ได้:
- ความหนาแน่น $\rho$ เป็นค่าคงที่
- สมการโมเมนตัมและพลังงาน **สามารถถูกแก้แยกกันได้**
- ลดความซับซ้อนของการคำนวณ

---

## ตารางเปรียบเทียบประเภทของไหล

| ประเภทของไหล | สมการสถานะ | OpenFOAM Model | ข้อดี | ข้อเสีย | การใช้งาน |
|-------------|-------------|----------------|---------|---------|-------------|
| อัดตัวได้ | $p = \rho R T$ | `perfectGas` | แม่นยำสูง, สามารถจำลองการไหลความเร็วสูง, คลื่นกระแทก | คำนวณซับซ้อน, ใช้เวลานาน, ต้องแก้สมการ coupled | การไหลความเร็วสูง, แก๊ส, อากาศพลศาสตร์, การเผาไหม้ |
| อัดตัวไม่ได้ | $\rho = \text{const}$ | `incompressible` | คำนวณเร็ว, เสถียร, ใช้หน่วยความจำน้อย | ความแม่นยำจำกัดสำหรับความเร็วสูง, ไม่สามารถจำลองคลื่นกระแทก | ของเหลว, การไหลความเร็วต่ำ, ระบบท่อ, การไหลในช่อง |

---

## สรุปความสำคัญ

สมการสถานะเป็นส่วนสำคัญที่เชื่อมโยงสมการควบคุมทั้งหมดให้เป็นระบบที่สมบูรณ์:

1. **การเลือก EOS ที่เหมาะสม** ขึ้นอยู่กับชนิดของของไหลและเงื่อนไขการไหล (โดยเฉพาะ Mach number)

2. **ผลกระทบต่อ Solver** - EOS กำหนดว่าจะต้องใช้ Solver แบบใด (incompressible vs. compressible)

3. **ความซับซ้อนในการคำนวณ** - การไหลแบบอัดตัวได้ต้องการ computational resources มากกว่า

4. **ความแม่นยำ** - การเลือก EOS ที่ผิดอาจทำให้ผลลัพธ์มีความคลาดเคลื่อนอย่างมีนัยสำคัญ

---

## แหล่งอ้างอิงเพิ่มเติม

- [[00_Overview]] - ภาพรวมสมการควบคุม
- [[02_Conservation_Laws]] - กฎการอนุรักษ์มวล โมเมนตัม และพลังงาน
- [[04_Dimensionless_Numbers]] - เลขไร้มิติที่เกี่ยวข้องกับการเลือก EOS
- [[05_OpenFOAM_Implementation]] - การนำไปใช้ใน OpenFOAM อย่างละเอียด
