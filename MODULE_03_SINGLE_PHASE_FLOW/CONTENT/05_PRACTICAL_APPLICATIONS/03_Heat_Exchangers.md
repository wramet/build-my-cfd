# เครื่องแลกเปลี่ยนความร้อน (Heat Exchangers)

## 📖 บทนำ (Introduction)

เครื่องแลกเปลี่ยนความร้อน (Heat Exchangers) เป็นอุปกรณ์ที่สำคัญในหลายอุตสาหกรรม ใช้สำหรับถ่ายเทความร้อนระหว่างของไหลสองกระแสที่มีอุณหภูมิต่างกัน การจำลอง CFD ของเครื่องแลกเปลี่ยนความร้อนเป็นงานที่มีความซับซ้อนเนื่องจากเกี่ยวข้องกับ:

- **การไหลของของไหลสองกระแส** (hot fluid และ cold fluid)
- **การถ่ายเทความร้อนผ่านตัวนำ** (ผนังท่อหรือแผ่นกั้น)
- **ปฏิสัมพันธ์แบบ Conjugate Heat Transfer (CHT)** ระหว่างของไหลและของแข็ง

OpenFOAM มีความสามารถในการจำลองปรากฏการณ์เหล่านี้ได้อย่างมีประสิทธิภาพ

---

## 🔍 1. ตัวชี้วัดประสิทธิภาพ (Performance Metrics)

### 1.1 ประสิทธิภาพ (Effectiveness, ε)

ประสิทธิภาพของเครื่องแลกเปลี่ยนความร้อนเป็นอัตราส่วนระหว่างการถ่ายเทความร้อนจริงกับการถ่ายเทความร้อนสูงสุดที่เป็นไปได้:

$$\varepsilon = \frac{q_{actual}}{q_{max}}$$

โดยที่:
- $q_{actual}$ = อัตราการถ่ายเทความร้อนจริง [W]
- $q_{max}$ = อัตราการถ่ายเทความร้อนสูงสุดที่เป็นไปได้ [W]

**การถ่ายเทความร้อนสูงสุด** คำนวณได้จาก:

$$q_{max} = C_{min} (T_{h,in} - T_{c,in})$$

โดยที่:
- $C_{min}$ = อัตราการไหลของความร้อนต่ำสุด [W/K] = $\min(\dot{m}_h c_{p,h}, \dot{m}_c c_{p,c})$
- $T_{h,in}$ = อุณหภูมิของของไหลร้อนที่ทางเข้า [K]
- $T_{c,in}$ = อุณหภูมิของของไหลเย็นที่ทางเข้า [K]

> [!INFO] ประสิทธิภาพ $\varepsilon$ มีค่าระหว่าง 0 ถึง 1 โดยค่าที่ใกล้เคียง 1 แสดงถึงประสิทธิภาพสูง

### 1.2 จำนวนหน่วยถ่ายเทความร้อน (NTU - Number of Transfer Units)

NTU เป็นพารามิเตอร์ไร้มิติที่ใช้วัดขนาดของเครื่องแลกเปลี่ยนความร้อน:

$$NTU = \frac{U A}{C_{min}}$$

โดยที่:
- $U$ = สัมประสิทธิ์การถ่ายเทความร้อนโดยรวม [W/(m²·K)]
- $A$ = พื้นที่ผิวสำหรับถ่ายเทความร้อน [m²]
- $C_{min}$ = อัตราการไหลของความร้อนต่ำสุด [W/K]

**ความสัมพันธ์ระหว่าง NTU และประสิทธิภาพ** สำหรับเครื่องแลกเปลี่ยนแบบ counterflow:

$$\varepsilon = \frac{1 - \exp[-NTU(1 - C_r)]}{1 - C_r \exp[-NTU(1 - C_r)]}$$

โดย $C_r = C_{min}/C_{max}$ เป็นอัตราส่วนความจุของความร้อน

### 1.3 ความแตกต่างอุณหภูมิเฉลี่ยลอการิทึม (LMTD - Log Mean Temperature Difference)

วิธี LMTD ใช้สำหรับคำนวณขนาดของเครื่องแลกเปลี่ยนความร้อน:

$$Q = U A \Delta T_{LMTD}$$

โดยที่:

$$\Delta T_{LMTD} = \frac{\Delta T_1 - \Delta T_2}{\ln(\Delta T_1/\Delta T_2)}$$

- สำหรับ **parallel flow**:
  - $\Delta T_1 = T_{h,in} - T_{c,in}$
  - $\Delta T_2 = T_{h,out} - T_{c,out}$

- สำหรับ **counterflow** (มีประสิทธิภาพสูงกว่า):
  - $\Delta T_1 = T_{h,in} - T_{c,out}$
  - $\Delta T_2 = T_{h,out} - T_{c,in}$

---

## 🛠️ 2. กลยุทธ์การจำลองใน OpenFOAM (Simulation Strategies)

### 2.1 Multi-Region Approach (แนวทางหลายภูมิภาค)

แนวทางนี้ใช้ `chtMultiRegionFoam` (Conjugate Heat Transfer Multi-Region) เพื่อแก้สมการในแต่ละภูมิภาคแยกกัน:

#### โครงสร้างภูมิภาค (Region Structure):

```cpp
constant/
├── polyMesh/                    # Mesh ภูมิภาครวม (สำหรับ decomposePar)
├── regionProperties            # รายชื่อภูมิภาคทั้งหมด
├── hotFluid/                    # ภูมิภาคของไหลร้อน
│   ├── polyMesh/
│   ├── thermophysicalProperties
│   └── turbulenceProperties
├── coldFluid/                   # ภูมิภาคของไหลเย็น
│   ├── polyMesh/
│   ├── thermophysicalProperties
│   └── turbulenceProperties
└── solidWall/                   # ภูมิภาคของแข็ง (ผนังท่อ)
    ├── polyMesh/
    └── thermophysicalProperties
```

#### การกำหนดค่า thermophysicalProperties:

```cpp
// สำหรับภูมิภาคของไหล (Fluid Region)
thermoType
{
    type            heRhoThermo;
    mixture         pureMixture;  // สำหรับของไหลเฟสเดียว
    transport       constAnIso;  // การนำความร้อนคงที่
    thermo          hConst;      // ความร้อนจำเพาะคงที่
    equationOfState perfectGas; // หรือ incompressiblePerfectGas
    specie          specie;      // สำหรับของไหลเดี่ยว
    energy          sensibleEnthalpy;
}

mixture
{
    specie
    {
        molWeight       28.9;    // น้ำหนักโมเลกุล [g/mol] สำหรับอากาศ
    }
    thermodynamics
    {
        Cp              1005;    // ความร้อนจำเพาะ [J/(kg·K)]
        Hf              0;       // เอนทาลปีการก่อตัว [J/kg]
    }
    transport
    {
        mu              1.8e-5;  // ความหนืด [Pa·s]
        Pr              0.71;    // Prandtl number
        kappa           0.026;   // ความนำความร้อน [W/(m·K)]
    }
}

// สำหรับภูมิภาคของแข็ง (Solid Region)
thermoType
{
    type            heSolidThermo;
    mixture         pureMixture;
    transport       constIso;    // การนำความร้อนไอโซทรอปิก
    thermo          hConst;      // เอนทาลปีขึ้นกับอุณหภูมิ
    equationOfState rhoConst;    // ความหนาแน่นคงที่
    specie          specie;
    energy          sensibleEnthalpy;
}

mixture
{
    specie
    {
        molWeight       26.98;   // อลูมิเนียม
    }
    thermodynamics
    {
        Cp              903;     // [J/(kg·K)]
        Hf              0;
    }
    transport
    {
        kappa           237;     // [W/(m·K)] อลูมิเนียม
    }
    equationOfState
    {
        R               287;     // ค่าคงที่ของก๊าซเฉพาะ
        rho             2700;    // ความหนาแน่น [kg/m³]
    }
}
```

#### เงื่อนไขขอบเขตระหว่างภูมิภาค:

```cpp
// 0/T สำหรับแต่ละภูมิภาค
regions
{
    hotFluid_to_solidWall
    {
        type            compressible::turbulentTemperatureCoupledBaffleMixed;
        value           uniform 300;          // อุณหภูมิเริ่มต้น
        Tnbr            300;                   // อุณหภูมิของภูมิภาคข้างเคียง
        kappa           none;                  // จะถูกคำนวณจาก thermophysicalProperties
        K               none;                  // ค่าการนำความร้อนรวม
    }
}
```

### 2.2 แบบจำลองสื่อพรุน (Porous Media Simplification)

สำหรับเครื่องแลกเปลี่ยนที่มีท่อนับพัน การจำลองทุกท่อจะใช้ทรัพยากรการคำนวณมหาศาล แนวทาง **Homogenization** จะแทนที่กลุ่มท่อด้วย **โซนพรุน** ที่มีแรงต้านการไหลเทียบเท่า

#### สมการ Darcy-Forchheimer:

$$\nabla p = -\left(\frac{\mu}{K} + \beta \rho |\mathbf{u}|\right) \mathbf{u}$$

โดยที่:
- $\nabla p$ = การไล่ระดับความดัน [Pa/m]
- $\mu$ = ความหนืดพลศาสตร์ [Pa·s]
- $K$ = ความซึมผ่านได้ (permeability) [m²]
- $\beta$ = สัมประสิทธิ์ Forchheimer [m⁻¹]
- $\rho$ = ความหนาแน่น [kg/m³]
- $\mathbf{u}$ = เวกเตอร์ความเร็ว [m/s]

> [!TIP] การใช้แบบจำลองพรุนช่วยลดจำนวนเซลล์ mesh ได้อย่างมาก แต่ต้องการการปรับเทียบ (calibration) กับข้อมูลการทดลอง

---

## 💻 3. OpenFOAM Implementation

### 3.1 การกำหนดค่าโซนพรุน (Porous Zone Configuration)

ใช้ `fvOptions` ใน `system/fvOptions` เพื่อจำลองเครื่องแลกเปลี่ยนความร้อนแบบพรุน:

```cpp
// system/fvOptions
porousHeatExchanger
{
    type            explicitPorositySource;
    active          true;
    selectionMode   cellZone;
    cellZone        heatExchangerZone;

    explicitPorositySourceCoeffs
    {
        type            DarcyForchheimer;

        DarcyForchheimerCoeffs
        {
            // ทิศทางที่ 1 (x) - ทิศทางการไหลหลัก
            d   (1e5 1e5 1e5);    // สัมประสิทธิ์ Darcy [1/m²]
            f   (10 10 10);       // สัมประสิทธิ์ Forchheimer [1/m]

            // d = μ/K, f = β√(ความยาวลักษณะ)
            // ค่าจะถูกปรับเทียบจากข้อมูลการทดลอง
        }
    }
}

heatSource
{
    type            scalarSemiImplicitSource;
    active          true;
    selectionMode   cellZone;
    cellZone        heatExchangerZone;

    scalarSemiImplicitSourceCoeffs
    {
        T
        {
            // แหล่งความร้อนแบบคงที่ [W/m³]
            Su      10000;

            // เทอม implicit (ถ้าต้องการให้ขึ้นกับ T)
            Sp      0;
        }
    }
}
```

### 3.2 การติดตามประสิทธิภาพ (Performance Tracking)

เพิ่ม function objects ใน `system/controlDict` เพื่อติดตามตัวชี้วัดประสิทธิภาพ:

```cpp
// system/controlDict
functions
{
    // คำนวณอุณหภูมิเฉลี่ยที่ inlet/outlet
    tempInlet
    {
        type            surfaceFieldValue;
        functionObjectLibs ("libfieldFunctionObjects.so");
        operation       weightedAverage;
        weightField     phi;
        region          region0;
        fields          (T);
        surfaces
        (
            inlet
            {
                type            patch;
                patches         (inlet);
            }
        );
        writeFields     false;
        writeLocation   false;
    }

    tempOutlet
    {
        type            surfaceFieldValue;
        functionObjectLibs ("libfieldFunctionObjects.so");
        operation       weightedAverage;
        weightField     phi;
        region          region0;
        fields          (T);
        surfaces
        (
            outlet
            {
                type            patch;
                patches         (outlet);
            }
        );
        writeFields     false;
        writeLocation   false;
    }

    // คำนวณความดันตกคร่อม
    pressureDrop
    {
        type            pressureDrop;
        functionObjectLibs ("libfieldFunctionObjects.so");
        region          region0;
        patches
        (
            inlet
            outlet
        );
        log             true;
    }

    // คำนวณอัตราการถ่ายเทความร้อน
    heatTransferRate
    {
        type            surfaceHeatTransferRate;
        functionObjectLibs ("libfieldFunctionObjects.so");
        region          region0;
        surfaceFormat   none;
        patches
        (
            "heatExchangerWalls"
        );
        log             true;
    }
}
```

### 3.3 การคำนวณประสิทธิภาพหลังการจำลอง (Post-Processing Effectiveness)

ใช้ `postProcess` หรือสคริปต์ Python เพื่อคำนวณประสิทธิภาพ:

```bash
# ดึงค่าอุณหภูมิเฉลี่ยจากผลลัพธ์
postProcess -func "surfaceFieldValue(name=inlet,operation=weightedAverage,weightField=phi,field=T)" -latestTime
postProcess -func "surfaceFieldValue(name=outlet,operation=weightedAverage,weightField=phi,field=T)" -latestTime
```

สมการคำนวณประสิทธิภาพ:

$$\varepsilon = \frac{\dot{m}_c c_{p,c} (T_{c,out} - T_{c,in})}{\dot{m}_h c_{p,h} (T_{h,in} - T_{c,in})}$$

สำหรับกรณีที่ $C_{min} = C_c$ (ของไหลเย็นมีความจุความร้อนน้อยกว่า)

---

## 📈 4. การตรวจสอบความถูกต้อง (Validation)

ผลการจำลองควรได้รับการตรวจสอบเทียบกับวิธีมาตรฐาน

### 4.1 วิธี LMTD (Log Mean Temperature Difference Method)

เปรียบเทียบอัตราการถ่ายเทความร้อนจาก CFD กับค่าทางทฤษฎี:

$$Q_{CFD} = \dot{m}_h c_{p,h} (T_{h,in} - T_{h,out})$$
$$Q_{theory} = U A \Delta T_{LMTD}$$

ตรวจสอบความคลาดเคลื่อน:

$$\text{Error} = \left| \frac{Q_{CFD} - Q_{theory}}{Q_{theory}} \right| \times 100\%$$

> [!WARNING] ความคลาดเคลื่อนที่ยอมรับได้โดยทั่วไปคือ < 10% สำหรับการจำลอง CFD ในอุตสาหกรรม

### 4.2 Energy Balance (สมดุลพลังงาน)

ตรวจสอบว่าการถ่ายเทความร้อนระหว่างสองกระแสสมดุลกัน:

$$\dot{Q}_{hot} = \dot{m}_h c_{p,h} (T_{h,in} - T_{h,out})$$
$$\dot{Q}_{cold} = \dot{m}_c c_{p,c} (T_{c,out} - T_{c,in})$$

**เกณฑ์การตรวจสอบ:**

$$\left| \frac{\dot{Q}_{hot} - \dot{Q}_{cold}}{\dot{Q}_{hot}} \right| < 0.05 \quad (\text{หรือ } 5\%)$$

### 4.3 การเปรียบเทียบกับสมการเชิงประจักษ์

เปรียบเทียบค่า Nusselt number จาก CFD:

$$Nu_{CFD} = \frac{h D}{k} = \frac{q'' D}{k (T_w - T_b)}$$

กับสมการเชิงประจักษ์สำหรับการไหลในท่อ:

| สมการ | ชื่อ | เงื่อนไข |
|---------|------|----------|
| Dittus-Boelter | $Nu = 0.023 Re^{0.8} Pr^{n}$ | $n=0.4$ (heating), $n=0.3$ (cooling) |
| Gnielinski | $Nu = \frac{(f/8)(Re-1000)Pr}{1+12.7\sqrt{f/8}(Pr^{2/3}-1)}$ | ความแม่นยำสูงกว่า |
| Sieder-Tate | $Nu = 0.027 Re^{0.8} Pr^{1/3} (\mu/\mu_w)^{0.14}$ | มีผลจากความหนืดที่ผนัง |

---

## 📚 5. กรณีศึกษา (Case Studies)

### 5.1 เครื่องแลกเปลี่ยนความร้อนแบบเปลือกและท่อ (Shell-and-Tube Heat Exchanger)

#### โครงสร้าง:

```
┌─────────────────────────────────────────┐
│         SHELL (ของไหลด้านนอก)          │
│  ←───────────────────────────────→       │
│    ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐        │
│    │Tube│ │Tube│ │Tube│ │Tube│ │Tube│       │
│    └───┘ └───┘ └───┘ └───┘ └───┘        │
│  ←───────────────────────────────→       │
│                                         │
│    แผ่นกั้น (Baffles) นำทางการไหล       │
└─────────────────────────────────────────┘
         ↑
    TUBE (ของไหลด้านใน)
    ←───────────→
```

#### พารามิเตอร์การจำลอง:

```cpp
// constant/turbulenceProperties (สำหรับ shell side)
simulationType RAS;
RAS
{
    RASModel        kEpsilon;
    turbulence      on;

    // ค่าคงที่มาตรฐาน
    kEpsilonCoeffs
    {
        Cmu             0.09;
        C1              1.44;
        C2              1.92;
        sigmaEps        1.11;
    }
}

// system/fvSchemes
ddtSchemes
{
    default         steadyState;
}
gradSchemes
{
    default         Gauss linear;
    grad(p)         Gauss linear;
    grad(U)         cellLimited Gauss linear 1;
}
divSchemes
{
    default         none;
    div(phi,U)      Gauss upwind;  // สำหรับความเสถียร
    div(phi,k)      Gauss upwind;
    div(phi,epsilon) Gauss upwind;
}
laplacianSchemes
{
    default         Gauss linear corrected;
}
```

#### ผลลัพธ์ที่คาดหวัง:

- **โปรไฟล์อุณหภูมิ**: การเปลี่ยนแปลงของอุณหภูมิตามความยาวเครื่องแลกเปลี่ยน
- **ความดันตกคร่อม**: $\Delta p$ บนทั้ง shell side และ tube side
- **สัมประสิทธิ์การถ่ายเทความร้อน**: $h$ คำนวณจาก gradient อุณหภูมิบริเวณผนัง

### 5.2 เครื่องแลกเปลี่ยนความร้อนแบบแผ่น (Plate Heat Exchanger)

#### คุณสมบัติเฉพาะ:

- **รอยหยัก (corrugations)**: กระตุ้นความปั่นป่วนที่ Reynolds number ต่ำ
- **พื้นที่กะทัดรัด**: ให้ค่า $h$ สูงในปริมาตรเล็ก
- **การไหลแบบ counterflow**: โดยปกติจะมีประสิทธิภาพสูงกว่า parallel flow

#### การตั้งค่า Mesh:

```cpp
// system/snappyHexMeshDict
castellatedMesh true;
snap            true;
addLayers       true;

geometry
{
    plateHeatExchanger.stl
    {
        type triSurfaceMesh;
        name plates;
    }
}

refinementSurfaces
{
    plates
    {
        level (4 4);  // ความละเอียดสูงบริเวณรอยหยัก
    }
}

addLayersCoeffs
{
    relativeSizes  true;
    layers
    {
        plates
        {
            nSurfaceLayers  5;  // Boundary layer layers
        }
    }
    expansionRatio 1.2;
    finalLayerThickness 0.3;
    minThickness 0.05;
}
```

---

## ⚠️ 6. ข้อควรพิจารณาและข้อจำกัด

### 6.1 การสะสมคราบ (Fouling)

การสะสมคราบตามกาลเวลาจะ:

- เพิ่ม **ความต้านทานความร้อน** (thermal resistance)
- เพิ่ม **แรงดันตกคร่อม**
- ลด **ประสิทธิภาพ** ของเครื่องแลกเปลี่ยนความร้อน

**Fouling factor:**

$$R_f = \frac{1}{U_{fouled}} - \frac{1}{U_{clean}}$$

ใน OpenFOAM สามารถจำลองเป็นชั้นความต้านทานความร้อนเพิ่มเติม:

```cpp
// 0/T (boundary condition)
wallWithFouling
{
    type            externalWallHeatFluxTemperature;
    mode            coefficient;
    Ta              constant 300;     // อุณหภูมิภายนอก
    h               uniform 500;      // สัมประสิทธิ์การถ่ายเทความร้อนรวม (รวม fouling)
    kappa           none;            // ใช้ค่าจาก thermophysicalProperties
    value           uniform 300;     // อุณหภูมิเริ่มต้น
}
```

### 6.2 ข้อจำกัดของแบบจำลอง

| แบบจำลอง | ข้อดี | ข้อเสีย | ความเหมาะสม |
|-----------|--------|---------|---------------|
| **Multi-Region CHT** | แม่นยำสูง รายละเอียดดี | ใช้เวลาคำนวณนาน | การออกแบบรายละเอียด การวิจัย |
| **Porous Media** | เร็ว ประหยัด | ต้อง calibration ไม่มีรายละเอียดโฟลว์ในท่อ | การวิเคราะห์ระบบขนาดใหญ่ |
| **Periodic Unit Cell** | สมดุลระหว่างความแม่นยำและเวลา | ไม่จับผลขอบ | การศึกษาการไหลในท่อแต่ละท่อ |

---

## ✅ 7. แนวทางปฏิบัติที่ดีที่สุด (Best Practices)

### 7.1 การเตรียมรูปทรงเรขาคณิต (Geometry Preparation)

```mermaid
flowchart TD
    A[CAD Model] --> B[Simplify Geometry]
    B --> C[Create Fluid Domains]
    C --> D[Define Interfaces]
    D --> E[Generate Mesh]
    E --> F[Check Quality]
    F --> G[Run Simulation]
```
> **Figure 1:** ขั้นตอนมาตรฐานในการเตรียมรูปทรงเรขาคณิตสำหรับการจำลองเครื่องแลกเปลี่ยนความร้อน เริ่มต้นจากการจัดการโมเดล CAD การลดความซับซ้อนของรูปทรงที่ไม่มีผลต่อฟิสิกส์ การสร้างโดเมนของของไหล การกำหนดอินเทอร์เฟซระหว่างบริเวณที่แตกต่างกัน (เช่น ของไหลกับของแข็ง) การสร้างเมช และการตรวจสอบคุณภาพก่อนเริ่มการจำลองความปลอดภัยทางฟิสิกส์ไม่ส่งผลกระทบต่อความเร็วในการจำลอง ผ่านการใช้พลังของ C++ Template Metaprogramming ในการตรวจสอบความสอดคล้องทางมิติทั้งหมดที่ขั้นตอนการคอมไพล์โปรแกรมเพียงครั้งเดียว

**เคล็ดลับ:**

- ลดรายละเอียดขนาดเล็กที่ไม่สำคัญ (fillets < 1 mm)
- สร้าง **separate bodies** สำหรับแต่ละ region (hot fluid, cold fluid, solid)
- ตรวจสอบให้แน่ใจว่า **interfaces** ตรงกันระหว่าง regions

### 7.2 การสร้าง Mesh สำหรับ CHT

| พารามิเตอร์ | ค่าแนะนำ | เหตุผล |
|-------------|-----------|---------|
| **$y^+$** | ≈ 1 สำหรับ wall-resolved | การคำนวณ heat transfer ที่แม่นยำ |
| **Expansion ratio** | < 1.2 | ความเสถียรเชิงตัวเลข |
| **Non-orthogonality** | < 65° | ความแม่นยำของ gradient |
| **Layers บน interface** | 3-5 layers | การถ่ายเทความร้อนที่ถูกต้อง |

### 7.3 การเลือก Solver

| สถานการณ์ | Solver | เหตุผล |
|------------|--------|---------|
| **Steady-state CHT** | `chtMultiRegionFoam` | การแก้ปัญหา steady-state สำหรับหลายภูมิภาค |
| **Transient CHT** | `chtMultiRegionFoam` | การวิเคราะห์เชิงเวลา |
| **Porous media** | `porousSimpleFoam` | การไหลในตัวกลางพรุน |

### 7.4 การตรวจสอบการลู่เข้า (Convergence Monitoring)

```cpp
// system/fvSolution
SOLVERS
{
    p
    {
        solver          GAMG;
        tolerance       1e-06;
        relTol          0.01;
    }

    U
    {
        solver          smoothSolver;
        smoother        GaussSeidel;
        tolerance       1e-05;
        relTol          0.1;
    }

    T
    {
        solver          smoothSolver;
        smoother        GaussSeidel;
        tolerance       1e-06;
        relTol          0.01;
    }
}

SIMPLE
{
    nNonOrthogonalCorrectors 2;

    residualControl
    {
        p               1e-05;
        U               1e-05;
        T               1e-06;
        // possibly other fields
    }
}
```

**ตรวจสอบ:**

- **Residuals** ลดลง 3-4 ลำดับของขนาด
- **ปริมาณรวม** (integral quantities) เช่น อัตราการถ่ายเทความร้อนคงที่
- **Energy balance** ระหว่างสองกระแส

---

## 📖 สรุป (Summary)

เครื่องแลกเปลี่ยนความร้อนเป็นแอปพลิเคชันที่สำคัญของ CFD ใน OpenFOAM ซึ่งต้องการความเข้าใจใน:

1. **ทฤษฎีการถ่ายเทความร้อน** (Effectiveness, NTU, LMTD)
2. **Conjugate Heat Transfer (CHT)** สำหรับการจำลองร่วมกันของของไหลและของแข็ง
3. **แบบจำลองสื่อพรุน** เพื่อลดความซับซ้อนของการคำนวณ
4. **การตรวจสอบความถูกต้อง** กับวิธีทางทฤษฎีและการทดลอง

OpenFOAM มีเครื่องมือที่ครอบคลุม (`chtMultiRegionFoam`, `fvOptions`, function objects) สำหรับการจำลองเครื่องแลกเปลี่ยนความร้อนทั้งในมิติของการวิจัยและการออกแบบทางอุตสาหกรรม

---

**จบเนื้อหาโมดูลเครื่องแลกเปลี่ยนความร้อน**
