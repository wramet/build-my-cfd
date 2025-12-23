# การไหลภายในและเครือข่ายท่อ (Internal Flows and Piping)

## 📖 บทนำ (Introduction)

การไหลภายในเป็นพื้นฐานของระบบวิศวกรรมมากมาย เช่น ท่อส่งน้ำมัน ระบบระบายอากาศ (HVAC) และเครื่องปฏิกรณ์เคมี ความท้าทายหลักคือการคาดการณ์ความดันตกคร่อมและประสิทธิภาพการผสม

> [!INFO] ความสำคัญทางอุตสาหกรรม
> การไหลภายในมีบทบาทสำคัญในหลายอุตสาหกรรม รวมถึง:
> - **วิศวกรรมกระบวนการ**: ระบบท่อและเครื่องแลกเปลี่ยนความร้อน
> - **พลังงาน**: เครื่องปั๊มและกังหัน
> - **การแพทย์**: การไหลของเลือดในหลอดเลือด
> - **สิ่งแวดล้อม**: การระบายน้ำและการบำบัดน้ำเสีย

---

## 🔍 1. ฟิสิกส์ของการไหลในท่อ

### 1.1 ความดันตกคร่อม (Pressure Drop)

การสูญเสียพลังงานเนื่องจากแรงเสียดทานอธิบายด้วยสมการ **Darcy-Weisbach**:

$$\Delta p = f \frac{L}{D} \frac{\rho U^2}{2}$$

โดยที่:
- $\Delta p$ = ความดันตกคร่อม (Pa)
- $f$ = Friction factor ซึ่งขึ้นอยู่กับความหยาบผิวและ Reynolds number
- $L$ = ความยาวท่อ (m)
- $D$ = เส้นผ่านศูนย์กลางท่อ (m)
- $\rho$ = ความหนาแน่นของไหล (kg/m³)
- $U$ = ความเร็วเฉลี่ย (m/s)

ใน OpenFOAM เราวัดค่านี้ได้จาก:

$$\Delta p = p_{inlet} - p_{outlet}$$

#### การคำนวณ Friction Factor

**การไหลแบบ Laminar** ($\text{Re} < 2300$):
$$f = \frac{64}{\text{Re}}$$

**การไหลแบบ Turbulent**: ใช้สมการ **Colebrook-White**:

$$\frac{1}{\sqrt{f}} = -2 \log_{10}\left(\frac{\epsilon/D}{3.7} + \frac{2.51}{\text{Re}\sqrt{f}}\right)$$

โดย $\epsilon/D$ คือความหยาบสัมพัทธ์ (relative roughness)

### 1.2 Reynolds Number สำหรับการไหลในท่อ

$$\text{Re} = \frac{\rho U_{avg} D}{\mu}$$

โดยที่:
- $U_{avg}$ = ความเร็วเฉลี่ย
- $\mu$ = ความหนืดพลศาสตร์ (dynamic viscosity)

**การจำแนกระบอบการไหล**:
- $\text{Re} < 2300$: การไหลแบบ Laminar
- $2300 < \text{Re} < 4000$: การไหลแบบ Transitional
- $\text{Re} > 4000$: การไหลแบบ Turbulent

### 1.3 ลักษณะโปรไฟล์ความเร็ว (Velocity Profiles)

**การไหลแบบ Laminar**: โปรไฟล์แบบพาราโบลา (Hagen-Poiseuille flow)

$$u(r) = \frac{\Delta p}{4\mu L} (R^2 - r^2) = 2U_{avg}\left[1 - \left(\frac{r}{R}\right)^2\right]$$

**การไหลแบบ Turbulent**: โปรไฟล์ที่แบนลงตรงกลาง (Plug-like) พร้อมชั้นบางๆ ที่มีความหนืด (viscous sublayer) ซึ่งอธิบายด้วย **Law of the Wall**:

$$u^+ = \frac{1}{\kappa} \ln y^+ + C$$

โดยที่:
- $u^+ = u/u_{\tau}$ (ความเร็วไร้มิติ)
- $y^+ = y u_{\tau}/\nu$ (ระยะห่างไร้มิติจากผนัง)
- $\kappa \approx 0.41$ = von Kármán constant
- $C \approx 5.0$ = ค่าคงที่

```mermaid
flowchart TD
    A[การไหลในท่อ] --> B{Reynolds Number}
    B -->|Re < 2300| C[Laminar Flow]
    B -->|2300 < Re < 4000| D[Transitional Flow]
    B -->|Re > 4000| E[Turbulent Flow]

    C --> F[โปรไฟล์พาราโบลา]
    E --> G[โปรไฟล์ Plug-like]

    F --> H[f = 64/Re]
    G --> I[Colebrook-White Eq.]

    style C fill:#90EE90
    style E fill:#FFB6C1
```
> **Figure 1:** แผนผังการจำแนกระบอบการไหลในท่อ (Flow Regimes) ตามค่า Reynolds Number ซึ่งกำหนดลักษณะของโปรไฟล์ความเร็ว (Velocity Profile) และวิธีการคำนวณสัมประสิทธิ์ความเสียดทาน (Friction Factor) ที่แตกต่างกันระหว่างการไหลแบบ Laminar และ Turbulentความปลอดภัยทางฟิสิกส์ไม่ส่งผลกระทบต่อความเร็วในการจำลอง ผ่านการใช้พลังของ C++ Template Metaprogramming ในการตรวจสอบความสอดคล้องทางมิติทั้งหมดที่ขั้นตอนการคอมไพล์โปรแกรมเพียงครั้งเดียว

---

## 🛠️ 2. การสร้างแบบจำลองการผสม (Mixing Analysis)

ในระบบท่อที่มีการผสมสาร (เช่น Static Mixers) เราใช้ตัวชี้วัดเพื่อระบุประสิทธิภาพ

### 2.1 ดัชนีการผสม (Mixing Index, MI)

$$MI = 1 - \frac{\sigma}{\sigma_0}$$

โดยที่:
- $\sigma$ = ส่วนเบี่ยงเบนมาตรฐานของความเข้มข้นที่หน้าตัดใดๆ
- $\sigma_0$ = ส่วนเบี่ยงเบนมาตรฐานเริ่มต้น

**Coefficient of Variation** (สำหรับเครื่องผสมแบบสถิต):

$$CoV = \frac{\sigma_c}{\bar{c}}$$

โดยที่:
- $\sigma_c$ = ส่วนเบี่ยงเบนมาตรฐานของความเข้มข้น
- $\bar{c}$ = ค่าเฉลี่ยของความเข้มข้น
- $c$ = ความเข้มข้นของสารติดตาม (tracer concentration)

### 2.2 เวลากักตัว (Residence Time Distribution, RTD)

ใช้สเกลาร์พาสซีฟ (Passive scalar) เพื่อติดตามเวลาที่อนุภาคของไหลใช้ในระบบ:

$$\bar{t} = \frac{V}{\dot{V}}$$

**การกระจายเวลากักตัว (Residence Time Distribution)**:

$$E(t) = \frac{c(t)}{\int_0^\infty c(t) \, \mathrm{d}t}$$

**ประเภทของเครื่องปฏิกรณ์ตาม RTD**:

| ประเภทเครื่องปฏิกรณ์ | ลักษณะ RTD |
|------------------------|-------------|
| **Plug Flow Reactor (PFR)** ในอุดมคติ | RTD แบบ Dirac delta |
| **CSTR** ในอุดมคติ | RTD แบบ exponential |
| **เครื่องปฏิกรณ์ที่ไม่สมบูรณ์** | แสดงการกระจายตัวระหว่างกลาง |

---

## 💻 3. การนำไปใช้ใน OpenFOAM

### 3.1 การเลือก Solver ที่เหมาะสม

| Solver | ประเภท | ความเหมาะสม |
|--------|--------|--------------|
| **simpleFoam** | steady-state | การไหลแบบสม่ำเสมอ |
| **pimpleFoam** | transient | การไหลแบบไม่สม่ำเสมอ |
| **buoyantFoam** | CHT | การถ่ายเทความร้อนระหว่างของแข็ง-ของไหล |
| **chtMultiRegionFoam** | Multi-region | การจับคู่ของแข็ง-ของไหลหลายโซน |

### 3.2 การตั้งค่า Boundary Conditions

#### ความเร็ว (Velocity)

```cpp
dimensions      [0 1 -1 0 0 0 0];
internalField   uniform (0 0 0);
boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform (1.0 0 0);
    }
    outlet
    {
        type            zeroGradient;
    }
    walls
    {
        type            noSlip;
    }
}
```

#### ความดัน (Pressure)

```cpp
dimensions      [0 2 -2 0 0 0 0];
internalField   uniform 0;
boundaryField
{
    inlet
    {
        type            zeroGradient;
    }
    outlet
    {
        type            fixedValue;
        value           uniform 0;
    }
    walls
    {
        type            zeroGradient;
    }
}
```

### 3.3 การคำนวณความดันตกคร่อม

ตัวอย่างการใช้ `surfaceFieldValue` เพื่อหาค่าความดันเฉลี่ยที่ทางเข้าและทางออก:

```cpp
functions
{
    pInlet
    {
        type            surfaceFieldValue;
        libs            (fieldFunctionObjects);
        operation       weightedAverage;
        weightField     phi;
        region          region0;
        surfaceFormat   none;
        fields          (p);
        patches         (inlet);
    }

    pOutlet
    {
        type            surfaceFieldValue;
        libs            (fieldFunctionObjects);
        operation       weightedAverage;
        weightField     phi;
        region          region0;
        surfaceFormat   none;
        fields          (p);
        patches         (outlet);
    }

    pressureDrop
    {
        type            coded;
        libs            (libutilityFunctionObjects.so);
        code
        #{
            const scalar pIn = pInlet->getValue();
            const scalar pOut = pOutlet->getValue();
            const scalar deltaP = pIn - pOut;

            Info << "Pressure drop: " << deltaP << " Pa" << endl;
        #};
    }
}
```

### 3.4 การติดตามแรง (Forces)

```cpp
functions
{
    forces
    {
        type            forces;
        functionObjectLibs ("libforces.so");
        patches         (walls);
        rho             rhoInf;
        log             true;

        rhoInf          1.225;
        CofR            (0 0 0);

        writeControl    timeStep;
        writeInterval   1;
    }
}
```

### 3.5 การคำนวณ Wall Shear Stress

```cpp
wallShearStress
{
    type            wallShearStress;
    libs            ("libfieldFunctionObjects.so");
    writeFields     true;
}
```

---

## 📋 4. ข้อควรระวังในการจำลองการไหลภายใน

### 4.1 Entry Length

ตรวจสอบว่าความยาวท่อเพียงพอให้การไหลพัฒนาเต็มที่ (Fully developed) หรือไม่

**ความยาวขาเข้า (Entry length)** $L_e$:

- **การไหลแบบ Laminar**: $L_{e,\text{lam}} \approx 0.06 D \text{Re}$
- **การไหลแบบ Turbulent**: $L_{e,\text{turb}} \approx 4.4 D \text{Re}^{1/6}$

> [!WARNING] ข้อควรระวัง
> หากความยาวท่อไม่เพียงพอ ต้องระบุโปรไฟล์ที่พัฒนาเต็มที่ที่ทางเข้า หรือใช้ periodic boundaries

ใน OpenFOAM โปรไฟล์ที่พัฒนาเต็มที่สามารถสร้างขึ้นด้วย `boundaryFoam` หรือตั้งค่าผ่าน `fixedValue` ด้วยฟังก์ชัน `codedFixedValue`

### 4.2 Mesh Quality

บริเวณข้อต่อ (Elbows) มักเกิดการแยกตัวของการไหล (Separation) ต้องการ Mesh ที่ละเอียดเป็นพิเศษ

**เกณฑ์คุณภาพ Mesh ที่แนะนำ**:

| เกณฑ์ | ค่าที่แนะนำ |
|----------|----------------|
| **ความเป็นฉาก (Orthogonality)** | มุมความเป็นฉาก > 60° |
| **อัตราส่วนภาพ (Aspect ratio)** | < 1000 |
| **ความเบ้ (Skewness)** | < 0.85 |
| **อัตราการขยาย (Expansion ratio)** | < 2 |

**การสร้าง Boundary Layer Mesh**:

- สำหรับ wall-resolved: $y^+ \approx 1$
- สำหรับ wall functions: $30 < y^+ < 300$

```cpp
// snappyHexMeshDict
addLayers
{
    walls
    {
        nSurfaceLayers 10;

        expansionRatio 1.2;
        finalLayerThickness 0.001;
        minThickness 1e-5;
    }
}
```

เพื่อจับภาพกระแสวนทุติยภูมิ (Dean vortices) ที่เกิดในท่อโค้ง

---

## 🏭 5. การประยุกต์ใช้ในอุตสาหกรรม

### 5.1 เครื่องผสมแบบสถิต (Static Mixers)

เครื่องผสมแบบสถิต (Kenics, helical) อาศัยองค์ประกอบทางเรขาคณิตในการแบ่งและรวมกระแส ทำให้เกิดการผสมโดยการไหลแบบสุ่ม (chaotic advection)

**คุณสมบัติ**:
- แรงดันตกคร่อมสูงกว่าท่อเปล่า
- ไม่มีชิ้นส่วนที่เคลื่อนไหว
- ประสิทธิภาพวัดด้วย Coefficient of Variation

**การตั้งค่าใน OpenFOAM**:
- Solver: `scalarTransportFoam` หรือเพิ่ม passive scalar ใน `simpleFoam`
- กำหนดค่าการแพร่ (diffusivity) ใน `transportProperties`
- Mesh: `snappyHexMesh` โดยปรับความละเอียดที่ใบพัด (mixer blades)

```mermaid
flowchart LR
    A[การไหลเข้า] --> B[Inlet]
    B --> C[Static Mixer Elements]
    C --> D[การแบ่งและรวมกระแส]
    D --> E[การผสมแบบ Chaotic]
    E --> F[Outlet]
    F --> G[การไหลออก]

    C --> H[Dean Vortices]
    C --> I[Flow Division]
    C --> J[Flow Recombination]

    style C fill:#FFE4B5
    style E fill:#90EE90
```
> **Figure 2:** กระบวนการทำงานของเครื่องผสมแบบสถิต (Static Mixer) ซึ่งอาศัยโครงสร้างภายในในการสร้างกระแสวน (Dean Vortices) และการแบ่งส่วนกระแสการไหลเพื่อเหนี่ยวนำให้เกิดการผสมที่มีประสิทธิภาพสูงผ่านกลไกการพาแบบโกลาหล (Chaotic Advection)ความปลอดภัยทางฟิสิกส์ไม่ส่งผลกระทบต่อความเร็วในการจำลอง ผ่านการใช้พลังของ C++ Template Metaprogramming ในการตรวจสอบความสอดคล้องทางมิติทั้งหมดที่ขั้นตอนการคอมไพล์โปรแกรมเพียงครั้งเดียว

### 5.2 เครื่องแลกเปลี่ยนความร้อน (Heat Exchangers)

#### เครื่องแลกเปลี่ยนความร้อนแบบเปลือกและท่อ (Shell-and-Tube)

**การประเมินประสิทธิภาพ**:
- วิธี **Log Mean Temperature Difference (LMTD)**
- วิธี **Number of Transfer Units (NTU)**

**การจำลองใน OpenFOAM**:
- จำลองหน่วยเซลล์ซ้ำ (representative periodic unit cell)
- ใช้ `chtMultiRegionFoam` สำหรับ conjugate heat transfer
- สำหรับเปลือกด้านนอกที่เป็นพรุน ใช้ `fvOptions` พร้อมสัมประสิทธิ์ Darcy-Forchheimer

```cpp
// constant/fvOptions - การจำลองโซนพรุน (Porous Zone)
porosity
{
    type            explicitPorositySource;
    active          true;
    selectionMode   cellZone;
    cellZone        radiator;

    explicitPorositySourceCoeffs
    {
        type            DarcyForchheimer;
        DarcyForchheimerCoeffs
        {
            d   (1e5 1e5 1e5);   // สัมประสิทธิ์ Darcy
            f   (10 10 10);      // สัมประสิทธิ์ Forchheimer
        }
    }
}
```

### 5.3 ปั๊มและกังหัน (Pumps and Turbines)

#### ปั๊มแบบแรงเหวี่ยงหนีศูนย์กลาง (Centrifugal Pumps)

**การจำลองใน OpenFOAM**:
- **MRF**: `SRFSimpleFoam` สำหรับ steady-state
- **Sliding mesh**: `pimpleDyMFoam` สำหรับ transient
- สร้าง Mesh สำหรับใบพัดและปลอกหอยแยกกัน
- เชื่อมต่อด้วย `AMI` (Arbitrary Mesh Interface)

**Boundary Conditions**:
- ทางเข้า: `flowRateInletVelocity` หรือ `pressureInletOutlet`
- ทางออก: `pressureInletOutlet`
- ติดตามแรงบิดบนเพลาใบพัดผ่าน object ฟังก์ชัน `forces`

---

## 📊 6. ตัวชี้วัดที่สำคัญ (Important Metrics)

### 6.1 ความดันตกคร่อม (Pressure Drop)

**ค่าสัมประสิทธิ์ความดันตก (Loss Coefficient)**:

$$K = \frac{\Delta p}{\frac{1}{2}\rho U^2}$$

ค่าสำหรับอุปกรณ์ต่างๆ:

| ชนิดของอุปกรณ์ | Loss Coefficient (K) |
|-------------------|----------------------|
| ข้อต่อโค้งเรียบ 90° | 0.2–0.3 |
| ข้อต่อหักศอกแบบคม | 1.1 |
| ข้อต่อสามทาง (tee-junction) | 1.8 |

### 6.2 สัมประสิทธิ์การถ่ายเทความร้อน (Heat Transfer Coefficient)

**Nusselt number** สำหรับการไหลแบบปั่นป่วนในท่อเรียบ:

**สมการ Dittus-Boelter**:
$$\text{Nu} = 0.023 \text{Re}^{0.8} \text{Pr}^n$$

โดยที่:
- $\text{Pr} = c_p \mu / k$ = Prandtl number
- $n = 0.4$ สำหรับการให้ความร้อน
- $\text{Nu} = h D/k$ = Nusselt number

### 6.3 ประสิทธิภาพการผสม (Mixing Efficiency)

$$\eta_m = 1 - \frac{CoV}{CoV_0}$$

**ตัวชี้วัดอื่นๆ**:
- **Power number**: $N_p = P/(\rho N^3 D^5)$
- **Flow number**: $N_q = Q/(N D^3)$

โดย $N$ = ความเร็วรอนของใบพัด, $D$ = เส้นผ่านศูนย์กลางใบพัด

---

## ✅ 7. การตรวจสอบความถูกต้อง (Validation)

### 7.1 การเปรียบเทียบกับสมการเชิงประจักษ์

**สำหรับการไหลแบบ Laminar ในท่อ**:
- ความดันตกคร่อม: $\Delta p = f \frac{L}{D} \frac{\rho U^2}{2}$ โดยที่ $f = 64/\text{Re}$
- โปรไฟล์ความเร็ว: $u(r) = 2U\left[1 - \left(\frac{r}{R}\right)^2\right]$

### 7.2 การตรวจสอบการอนุรักษ์

$$\sum \dot{m}_{in} = \sum \dot{m}_{out}$$

---

## 📝 สรุป (Summary)

การจำลองการไหลภายในใน OpenFOAM ต้องการความเข้าใจใน:

1. **ฟิสิกส์การไหลในท่อ**: Reynolds number, โปรไฟล์ความเร็ว, ความดันตกคร่อม
2. **การเลือก Solver ที่เหมาะสม**: simpleFoam, pimpleFoam, buoyantFoam
3. **การตั้งค่า Boundary Conditions**: ความเร็ว, ความดัน, อุณหภูมิ
4. **Mesh Quality**: ความละเอียดบริเวณผนัง, ความเป็นฉาก
5. **การประมวลผลภายหลัง**: ความดันตกคร่อม, การผสม, การถ่ายเทความร้อน

---

**หัวข้อถัดไป**: [[เครื่องแลกเปลี่ยนความร้อน|./03_Heat_Exchangers.md]]
