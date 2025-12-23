# การถ่ายเทความร้อนใน OpenFOAM: คู่มือการจำลองความร้อนเบื้องต้นถึงขั้นสูง

## 📋 ภาพรวม (Overview)

การถ่ายเทความร้อนเป็นหัวใจสำคัญของการประยุกต์ใช้งานทางวิศวกรรม ตั้งแต่การระบายความร้อนอิเล็กทรอนิกส์ไปจนถึงการออกแบบหม้อน้ำในโรงไฟฟ้า โมดูลนี้ครอบคลุมการนำสมการพลังงานไปใช้งานใน OpenFOAM เพื่อจำลองกลไกการนำ การพา และการแผ่รังสี

### รูปแบบการถ่ายเทความร้อน

การถ่ายเทความร้อนใน CFD ประกอบด้วย **สามรูปแบบหลัก**:

**การนำความร้อน (Conduction)** - การถ่ายเทพลังงานความร้อนผ่านการปฏิสัมพันธ์ของโมเลกุลโดยตรง:
$$\mathbf{q} = -k \nabla T$$

- $\mathbf{q}$ คือเวกเตอร์ฟลักซ์ความร้อน [W/m²]
- $k$ คือค่าสภาพนำความร้อน [W/(m·K)]
- $\nabla T$ คือความชันของอุณหภูมิ

**การพาความร้อน (Convection)** - การรวมกันของการนำความร้อนกับการเคลื่อนที่ของของไหล:
$$\mathbf{q} = h(T_s - T_\infty)$$

- $h$ คือสัมประสิทธิ์การถ่ายเทความร้อนแบบพาความร้อน [W/(m²·K)]
- $T_s$ คืออุณหภูมิพื้นผิว
- $T_\infty$ คืออุณหภูมิแวดล้อม

**การแผ่รังสีความร้อน (Radiation)** - การถ่ายเทพลังงานผ่านคลื่นแม่เหล็กไฟฟ้า:
$$q = \varepsilon \sigma (T^4_{hot} - T^4_{cold})$$

- $\varepsilon$ คือค่าการเปล่งรังสี (emissivity)
- $\sigma$ คือค่าคงที่ของสเตฟาน-โบลต์ซมันน์ ($5.67 × 10^{-8}$ W/(m²·K⁴))

---

## 🎯 วัตถุประสงค์การเรียนรู้ (Learning Objectives)

เมื่อจบโมดูลนี้ คุณจะสามารถ:

### 1. ตั้งค่าการจำลองการถ่ายเทความร้อน (Configure Heat Transfer Simulations)

ตั้งค่าการจำลองการถ่ายเทความร้อนที่สมบูรณ์โดยการทำความเข้าใจการนำสมการพลังงานพื้นฐานไปใช้ใน OpenFOAM:

$$\rho c_p \frac{\partial T}{\partial t} + \rho c_p \mathbf{u} \cdot \nabla T = \nabla \cdot (k \nabla T) + Q$$

โดยที่:
- $\rho$ คือ **ความหนาแน่นของของไหล** (fluid density) [kg/m³]
- $c_p$ คือ **ความจุความร้อนจำเพาะ** (specific heat capacity) [J/(kg·K)]
- $T$ คือ **สนามอุณหภูมิ** (temperature field) [K]
- $\mathbf{u}$ คือ **เวกเตอร์ความเร็ว** (velocity vector) [m/s]
- $k$ คือ **สภาพนำความร้อน** (thermal conductivity) [W/(m·K)]
- $Q$ คือ **แหล่งกำเนิดหรือแหล่งระบายความร้อน** (heat sources or sinks) [W/m³]

> [!TIP] **OpenFOAM Implementation**
> สมการพลังงานใน OpenFOAM ถูกแก้ในรูปของ **เอนทาลปี ($h$)** หรือ **พลังงานภายใน ($e$)**:
> $$\frac{\partial (\rho h)}{\partial t} + \nabla \cdot (\rho \mathbf{u} h) = \nabla \cdot (\alpha_{eff} \nabla h) + \frac{Dp}{Dt} + Q$$
> โดยที่ $\alpha_{eff}$ คือค่าการแพร่ความร้อนประสิทธิผล (Thermal Diffusivity) ที่รวมผลของความปั่นป่วน

### 2. กำหนดค่าคุณสมบัติทางเทอร์โมฟิสิกส์ (Configure Thermophysical Properties)

กำหนดค่าและเลือกแบบจำลองทางเทอร์โมฟิสิกส์ (thermophysical models) ที่เหมาะสมตามข้อกำหนดของการจำลอง

#### แบบจำลองที่รองรับใน OpenFOAM

| แบบจำลอง | คำอธิบาย | กรณีการใช้งาน |
|-----------|-----------|--------------|
| **สภาพนำความร้อนคงที่** (`const`) | ค่าสภาพนำความร้อนคงที่ | วัสดุโฮโมจีเนียส |
| **สภาพนำความร้อนขึ้นอยู่กับอุณหภูมิ** (`polynomial`) | ฟังก์ชัน $k(T)$ | วัสดุมีคุณสมบัติแปรผัน |
| **กฎของซัทเธอร์แลนด์** (`sutherland`) | การพึ่งพาอุณหภูมิแบบเลขชี้กำลัง | แก๊ส (อากาศ) |
| **สภาพนำความร้อนประสิทธิผล** | สำหรับสื่อพรุน หรือวัสดุผสม | สื่อพรุน คอมโพสิต |

#### โครงสร้าง `constant/thermophysicalProperties`

```cpp
thermoType
{
    type            heRhoThermo;
    mixture         pureMixture;
    transport       sutherland;      // หรือ const, polynomial
    thermo          hConst;          // หรือ janaf
    equationOfState perfectGas;
    specie          specie;
    energy          sensibleEnthalpy;
}

specie
{
    molWeight       28.96;           // kg/kmol (อากาศ)
}

thermo
{
    Cp              1005;            // J/(kg·K)
    Hf              0;               // ความร้อนของการก่อตัว
}

transport
{
    As              1.458e-06;       // Sutherland coefficient
    Ts              110.4;           // Sutherland temperature [K]
}
```

### 3. จัดการเงื่อนไขขอบเขตความร้อน (Apply Thermal Boundary Conditions)

นำไปใช้และกำหนดค่าเงื่อนไขขอบเขตความร้อนสำหรับสถานการณ์การถ่ายเทความร้อนต่างๆ

#### อุณหภูมิคงที่ (Fixed Temperature - Dirichlet)

```cpp
walls
{
    type            fixedValue;
    value           uniform 300;     // K
}
```

#### ฟลักซ์ความร้อนคงที่ (Fixed Heat Flux - Neumann)

```cpp
heatedWall
{
    type            fixedGradient;
    gradient        uniform 1000;    // W/m²
}
```

#### การถ่ายเทความร้อนแบบพา (Convective Heat Transfer)

```cpp
externalWall
{
    type            externalWallHeatFluxTemperature;
    mode            coefficient;
    h               uniform 25;      // W/m²K
    Ta              uniform 293;     // K
    thicknessLayers (0.001 0.002);   // ความหนาของชั้นผนัง
    kappaLayers     (0.5 0.1);       // สภาพนำความร้อนของชั้น
}
```

#### ผนังแบบอะเดียแบติก (Adiabatic Wall)

```cpp
adiabaticWalls
{
    type            zeroGradient;    // ∂T/∂n = 0
}
```

### 4. จำลองแรงลอยตัว (Simulate Buoyancy Effects)

ใช้การประมาณแบบ Boussinesq สำหรับการพาความร้อนตามธรรมชาติ:

$$\mathbf{f}_b = \rho \mathbf{g} \beta (T - T_{\text{ref}})$$

โดยที่:
- $\mathbf{g}$ คือ เวกเตอร์ความเร่งเนื่องจากแรงโน้มถ่วง (9.81 m/s²)
- $\beta$ คือ สัมประสิทธิ์การขยายตัวทางความร้อน (thermal expansion coefficient) [1/K]
- $T_{\text{ref}}$ คือ อุณหภูมิอ้างอิง [K]

> [!INFO] **การประมาณแบบ Boussinesq**
> การประมาณแบบนี้เหมาะสำหรับ:
> - ความแตกต่างอุณหภูมิเล็กน้อย ($\Delta T < 20$°C สำหรับอากาศ)
> - จำนวนเรย์ลี $10^4 < Ra < 10^7$
> - การไหลที่ไม่มีการอัดตัวที่สำคัญ

### 5. จำลองการถ่ายเทความร้อนแบบควบคู่ (CHT - Conjugate Heat Transfer)

เชื่อมโยงการไหลของของไหลกับการนำความร้อนในของแข็ง

### 6. คำนวณสัมประสิทธิ์การถ่ายเทความร้อน (Calculate Heat Transfer Coefficients)

คำนวณและวิเคราะห์ประสิทธิภาพการถ่ายเทความร้อนโดยใช้วิธีการต่างๆ

#### สัมประสิทธิ์การถ่ายเทความร้อนเฉพาะที่

$$h_{local} = -\frac{k \frac{\partial T}{\partial n}}{T_{wall} - T_{ref}}$$

#### จำนวนนัสเซิลต์ (Nusselt Number)

$$\mathrm{Nu} = \frac{hL}{k}$$

| สภาวะการไหล | ความสัมพันธ์ | เงื่อนไข |
|--------------|-------------------|----------|
| ลามินาร์ | $\mathrm{Nu} = 0.664 \mathrm{Re}^{1/2} \mathrm{Pr}^{1/3}$ | เหนือแผ่นเรียบ |
| ปั่นป่วน | $\mathrm{Nu} = 0.037 \mathrm{Re}^{0.8} \mathrm{Pr}^{1/3}$ | เหนือแผ่นเรียบ |
| การพาความร้อนตามธรรมชาติ | $\mathrm{Nu} = 0.59 \mathrm{Ra}^{1/4}$ | $10^4 < Ra < 10^9$ |

---

## 🔥 1. กลไกการถ่ายเทความร้อน (Heat Transfer Mechanisms)

OpenFOAM จัดการกลไกพื้นฐานสามรูปแบบดังนี้:

| กลไก | กฎทางกายภาพ | การนำไปใช้ใน OpenFOAM |
|------|------------|-----------------------|
| **การนำ (Conduction)** | กฎของฟูเรียร์: $\mathbf{q} = -k \nabla T$ | ตัวดำเนินการ `fvm::laplacian` |
| **การพา (Convection)** | การพาพลังงาน: $\nabla \cdot (\rho \mathbf{u} h)$ | ตัวดำเนินการ `fvm::div` ในสมการเอนทาลปี |
| **การแผ่รังสี (Radiation)** | $q \propto T^4$ | แบบจำลอง P-1 หรือ fvDOM |

### สมการพลังงานใน OpenFOAM

ใน OpenFOAM สมการพลังงานมักจะถูกแก้ในรูปของ **เอนทาลปี ($h$)** หรือ **พลังงานภายใน ($e$)**:

$$\frac{\partial (\rho h)}{\partial t} + \nabla \cdot (\rho \mathbf{u} h) = \nabla \cdot (\alpha_{eff} \nabla h) + \frac{Dp}{Dt} + Q$$

โดยที่:
- $\alpha_{eff}$ คือค่าการแพร่ความร้อนประสิทธิผล (Thermal Diffusivity) ที่รวมผลของความปั่นป่วน
- $\alpha_{eff} = \alpha + \alpha_t = \frac{k}{\rho c_p} + \frac{k_t}{\rho c_p}$

#### การใช้งานใน OpenFOAM

```cpp
// สมการเอนทาลปี/พลังงาน
fvScalarMatrix EEqn
(
    fvm::ddt(rho, he)
  + fvm::div(phi, he)
  - fvm::laplacian(turbulence->alphaEff(), he)
 ==
    rho*(U&g)
  + fvc::ddt(rho, K) + fvc::div(phi, K)
  + sources(rho, he)
);

he = (E - 0.5*magSqr(U)) - p/rho;
```

---

## 🌡️ 2. แบบจำลองเทอร์โมฟิสิกส์ (Thermophysical Models)

ไฟล์ `constant/thermophysicalProperties` ควบคุมการคำนวณคุณสมบัติของของไหล:

### แบบจำลองแก๊สสมบูรณ์ (Perfect Gas Model)

```cpp
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

specie
{
    molWeight       28.96;           // kg/kmol
}

thermo
{
    Cp              1005;            // J/(kg·K)
    Hf              0;               // J/kg
}

transport
{
    As              1.458e-06;       // Sutherland coefficient
    Ts              110.4;           // Sutherland temperature [K]
}
```

### แบบจำลองของเหลวอัดตัวไม่ได้ (Incompressible Liquid Model)

```cpp
thermoType
{
    type            heRhoThermo;
    mixture         pureMixture;
    transport       const;
    thermo          hConst;
    equationOfState rhoConst;
    specie          specie;
    energy          sensibleEnthalpy;
}

mixture
{
    specie
    {
        molWeight       18.01528;       // kg/kmol (น้ำ)
    }
    equationOfState
    {
        rho             998.2;          // kg/m³
    }
    thermodynamics
    {
        Cp              4182;           // J/(kg·K)
        Hf              0;
    }
    transport
    {
        mu              1.002e-3;       // Pa·s
        Pr              7.0;
        kappa           0.606;          // W/(m·K)
    }
}
```

---

## 🚀 3. Solvers ที่สำคัญ (Important Solvers)

### Solver การถ่ายเทความร้อนแบบไม่สามารถอัดได้

#### `buoyantBoussinesqSimpleFoam`

**ลักษณะ**: Solver แบบสภาวะคงที่ (steady-state) สำหรับการไหลแบบอัดตัวไม่ได้ที่ขับเคลื่อนด้วยแรงลอยตัวเล็กน้อย

**คุณสมบัติเฉพาะ**:
- ใช้การประมาณแบบ Boussinesq สำหรับการเปลี่ยนแปลงความหนาแน่น
- เหมาะสำหรับการเปลี่ยนแปลงอุณหภูมิเล็กน้อย
- ประหยัดค่าใช้จ่ายการคำนวณเมื่อเทียบกับ solver แบบอัดได้

**การเปลี่ยนแปลงความหนาแน่นแบบ Boussinesq**:
```cpp
rho = rhoRef*(1.0 - beta*(T - TRef));

// สมการโมเมนตัมพร้อมแรงลอยตัว
tmp<fvVectorMatrix> UEqn
(
    fvm::div(phi, U)
  + turbulence->divDevReff(U)
 ==
    rhoRef*(g - beta*(T - TRef)*g)
);
```

#### `buoyantSimpleFoam`

**ลักษณะ**: Solver แบบสภาวะคงที่ (steady-state) สำหรับการไหลแบบอัดได้ที่มีแรงลอยตัวและการถ่ายเทความร้อน

**ขั้นตอนการทำงาน**:
1. **สมการโมเมนตัม**: แก้สมการโมเมนตัมพร้อมการพาความร้อนและแรงลอยตัว
2. **สมการพลังงาน**: แก้สมการพลังงานสำหรับอุณหภูมิหรือเอนทาลปี
3. **Pressure-velocity coupling**: ใช้ขั้นตอน SIMPLE

**โครงสร้างการทำงาน**:
```cpp
// ลูปหลัก
while (simple.loop())
{
    // สมการโมเมนตัม
    tmp<fvVectorMatrix> UEqn
    (
        fvm::div(phi, U)
      + turbulence->divDevReff(U)
    );

    UEqn.relax();
    solve(UEqn == -fvc::grad(p));

    // สมการพลังงาน
    fvScalarMatrix TEqn
    (
        fvm::div(phi, h)
      + fvm::SuSp(divPhidp, h)
      - fvm::laplacian(kappaEff, h)
     ==
        sources(h)
    );

    TEqn.relax();
    TEqn.solve();
}
```

### Solver การถ่ายเทความร้อนแบบอัดได้

#### `buoyantPimpleFoam`

**ลักษณะ**: Solver แบบชั่วขณะ (transient) สำหรับการไหลแบบอัดได้และปั่นป่วนพร้อมการถ่ายเทความร้อน

**ความสามารถ**:
- ความหนาแน่นแปรผันตามความดันและอุณหภูมิ
- ใช้ขั้นตอน PIMPLE (ความเป็นผลสืบเนื่องของ PISO และ SIMPLE)
- เหมาะสำหรับปัญหาที่มีการเปลี่ยนแปลงอุณหภูมิขนาดใหญ่

### การถ่ายเทความร้อนแบบควบคู่ (Conjugate Heat Transfer)

#### `chtMultiRegionFoam`

**ลักษณะ**: Solver สำหรับปัญหาที่ต้องแก้ความร้อนในของไหลและของแข็งพร้อมกัน

**การถ่ายเทความร้อนแบบหลายภูมิภาค (Multi-region heat transfer)**:
```cpp
regionCouplePolyPatch
{
    type            regionCouple;
    neighbourRegion solidRegion;
    neighbourPatch solidToFluidPatch;
}

// Coupled boundary condition
{
    type            compressible::turbulentTemperatureCoupledBaffleMixed;
    Tnbr            T;
    kappaMethod     fluidThermo;      // หรือ solidThermo
}
```

### การเลือก Solver ที่เหมาะสม

| การใช้งาน | Solver ที่แนะนำ | คุณสมบัติหลัก |
|---|---|---|
| การพาความร้อนตามธรรมชาติ | `buoyantBoussinesqSimpleFoam` | การประมาณแบบ Boussinesq |
| การถ่ายเทความร้อนแบบอัดได้ | `buoyantPimpleFoam` | ความหนาแน่นแปรผัน, ชั่วขณะ |
| การนำความร้อนอย่างง่าย | `laplacianFoam` | การนำความร้อนอย่างเดียว |
| การถ่ายเทความร้อนแบบสังยุค | `chtMultiRegionFoam` | การเชื่อมต่อหลายภูมิภาค |

---

## 🔢 4. จำนวนไร้มิติที่สำคัญ (Important Dimensionless Numbers)

### จำนวนเรย์ลี (Rayleigh Number)

จำนวนเรย์ลีเป็นตัวบ่งชี้การพาความร้อนตามธรรมชาติ:

$$Ra = \frac{g \beta \Delta T L^3}{\nu \alpha} = Gr \cdot Pr$$

โดยที่:
- $Gr = \frac{g \beta \Delta T L^3}{\nu^2}$ คือ จำนวนกราสชอฟ (Grashof number)
- $\nu = \mu/\rho$ คือ ความหนืดจลนศาสตร์ (kinematic viscosity)
- $\alpha = k/(\rho c_p)$ คือ การแพร่ความร้อน (thermal diffusivity)

**การจำแนกระบอบการไหล**:

| ช่วง Rayleigh | ระบอบการไหล | ลักษณะการถ่ายเทความร้อน |
|:--------------:|:----------------|:------------------------|
| $Ra < 10^3$ | **การนำความร้อนเป็นหลัก** | Conduction dominates |
| $10^3 < Ra < 10^9$ | **การพาความร้อนแบบแลมินาร์** | Laminar natural convection |
| $Ra > 10^9$ | **การพาความร้อนแบบปั่นป่วน** | Turbulent natural convection |

### จำนวนปรานท์ (Prandtl Number)

จำนวนปรานท์เป็นคุณสมบัติของของไหลไร้มิติที่แสดงอัตราส่วนของความแพร่พลศาสตร์ต่อความแพร่ความร้อน:

$$Pr = \frac{\nu}{\alpha} = \frac{\mu c_p}{k}$$

**ค่า Prandtl ทั่วไป**:

| ของไหล | Prandtl Number | คุณสมบัติ |
|:--------:|:-------------:|:------------------------|
| **โลหะเหลว (Liquid metals)** | $Pr ≈ 0.01$ | ตัวนำความร้อนที่ดีเยี่ยม |
| **ก๊าซ (Gases)** | $Pr ≈ 0.7$ | อากาศ: 0.71 |
| **น้ำ (Water)** | $Pr ≈ 7$ | ที่ 20°C |
| **น้ำมัน (Oils)** | $Pr ≈ 100$ | ตัวนำความร้อนที่ไม่ดี |

---

## ⏱️ ระยะเวลาเรียนโดยประมาณ (Estimated Study Time)

| ส่วน | เวลาที่ใช้ |
|-----|-----------|
| **ภาคทฤษฎี** | 2-3 ชั่วโมง (พื้นฐานสมการและการระบุคุณสมบัติ) |
| **ภาคปฏิบัติ** | 2-3 ชั่วโมง (Case Setup: Cavity natural convection, CHT pipe) |
| **รวม** | **4-6 ชั่วโมง** |

---

## 🔗 การเชื่อมโยงกับไฟล์อื่นๆ (Connections to Other Files)

### ต่อยอดจาก: 03_TURBULENCE_MODELING.md

โมดูลการถ่ายเทความร้อนขยายแนวคิดการไหลแบบปั่นป่วนเพื่อรวมการขนส่งความร้อน:

#### ความต่อเนื่องของแนวคิดการขนส่งแบบปั่นป่วน

- **ความหนืดแบบปั่นป่วน** → **การแพร่ความร้อนแบบปั่นป่วน**

#### ตัวเลขพรานด์ทล์แบบปั่นป่วน

$$\mathrm{Pr}_t = \frac{\nu_t}{\alpha_t}$$

#### สมการเรย์โนลด์ส

$$\frac{Nu}{Re \cdot Pr} = \frac{C_f}{2}$$

### นำไปสู่: 05_PRACTICAL_APPLICATIONS.md

แนวคิดพื้นฐานการถ่ายเทความร้อนช่วยให้สามารถใช้งานในอุตสาหกรรมที่ซับซ้อนได้:

#### การประยุกต์ใช้ทางวิศวกรรม

| อุปกรณ์ | ปัญหาความร้อนหลัก | วิธีการแก้ไขใน OpenFOAM |
|----------|-------------------|--------------------------|
| **เครื่องปฏิกรณ์เคมี** | ปฏิกิริยาคายความร้อน/ดูดความร้อน | reactingFoam พร้อมการกำจัดความร้อน |
| **ระบบระบายความร้อน** | การจัดการความร้อนของส่วนประกอบ | การควบคู่ความร้อนของของแข็ง-ของไหล |
| **ตัวเก็บเกี่ยวพลังงานแสงอาทิตย์** | ปัญหาการคบคู่การแผ่รังสี-การพา-การนำ | การจำลองหลายโหมดการถ่ายเทความร้อน |

---

**หัวข้อถัดไป**: [พื้นฐานสมการพลังงาน](./01_Energy_Equation_Fundamentals.md)
