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

> [!TIP] **Physical Analogy: The Fire Brigade (หน่วยดับเพลิงส่งน้ำ)**
>
> เปรียบเทียบ "ความร้อน" (Heat) เป็น "ถังน้ำ" ที่ต้องส่งจากจุด A ไป B:
>
> 1.  **Conduction (การนำ):** ยืนต่อแถวเรียงหนึ่งแล้วส่งถังน้ำต่อมือกันไปเรื่อยๆ
>     - ต้องสัมผัสกัน (Contact)
>     - ถ้าคนยืนห่างกัน (ฉนวน) ก็ส่งไม่ได้
>
> 2.  **Convection (การพา):** คนถือถังน้ำแล้ว **"วิ่ง"** ไปส่งที่ปลายทาง
>     - อาศัยการเคลื่อนที่ของตัวกลาง (Fluid flow) เข้ามาช่วยพาไป
>     - มีประสิทธิภาพสูงกว่าการส่งต่อมือมาก (ถ้าน้ำไหลเร็ว)
>
> 3.  **Radiation (การแผ่รังสี):** ใช้ "สายยางฉีดน้ำ" ข้ามไปเลย
>     - ไม่ต้องอาศัยคนยืนต่อแถว (ไม่ต้องมีตัวกลาง)
>     - ส่งข้ามสุญญากาศได้ (เหมือนแสงอาทิตย์มายังโลก)

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
    type            heRhoThermo;    // Enthalpy-based thermodynamics for compressible flows
    mixture         pureMixture;    // Single component fluid
    transport       sutherland;     // Viscosity model: Sutherland's law
    thermo          hConst;         // Constant specific heat capacity
    equationOfState perfectGas;     // Equation of state for ideal gas
    specie          specie;         // Species properties
    energy          sensibleEnthalpy; // Energy variable: sensible enthalpy
}

specie
{
    molWeight       28.96;           // kg/kmol (air)
}

thermo
{
    Cp              1005;            // J/(kg·K)
    Hf              0;               // Heat of formation
}

transport
{
    As              1.458e-06;       // Sutherland coefficient
    Ts              110.4;           // Sutherland temperature [K]
}
```

> **📖 คำอธิบาย (Explanation):**
> ไฟล์นี้กำหนดคุณสมบัติทางเทอร์โมฟิสิกส์ของของไหลที่ใช้ในการจำลอง
>
> **แหล่งที่มา (Source):** ไฟล์ `constant/thermophysicalProperties`
>
> **แนวคิดสำคัญ (Key Concepts):**
> - `heRhoThermo`: คำนวณสมบัติของของไหลจากความหนาแน่นและเอนทาลปี
> - `sutherland`: กฎของ Sutherland สำหรับการพึ่งพาความหนืดต่ออุณหภูมิ
> - `perfectGas`: สมการสถานะสำหรับก๊าซอุดมคติ

### 3. จัดการเงื่อนไขขอบเขตความร้อน (Apply Thermal Boundary Conditions)

นำไปใช้และกำหนดค่าเงื่อนไขขอบเขตความร้อนสำหรับสถานการณ์การถ่ายเทความร้อนต่างๆ

#### อุณหภูมิคงที่ (Fixed Temperature - Dirichlet)

```cpp
walls
{
    type            fixedValue;      // Fixed value boundary condition
    value           uniform 300;     // Temperature = 300 K
}
```

> **📖 คำอธิบาย (Explanation):**
> กำหนดอุณหภูมิคงที่ที่ผนัง ใช้สำหรับกรณีที่รู้ค่าอุณหภูมิพื้นผิว
>
> **แหล่งที่มา (Source):** ไฟล์ `0/T`
>
> **แนวคิดสำคัญ (Key Concepts):**
> - `fixedValue`: เงื่อนไขขอบเขตแบบ Dirichlet (กำหนดค่าโดยตรง)
> - `uniform`: ค่าเดียวกันทั่วทั้งผนัง

#### ฟลักซ์ความร้อนคงที่ (Fixed Heat Flux - Neumann)

```cpp
heatedWall
{
    type            fixedGradient;   // Fixed gradient boundary condition
    gradient        uniform 1000;    // Heat flux = 1000 W/m²
}
```

> **📖 คำอธิบาย (Explanation):**
> กำหนดอัตราการไหลของความร้อนผ่านผนัง ใช้สำหรับกรณีที่รู้ค่าฟลักซ์ความร้อน
>
> **แหล่งที่มา (Source):** ไฟล์ `0/T`
>
> **แนวคิดสำคัญ (Key Concepts):**
> - `fixedGradient`: เงื่อนไขขอบเขตแบบ Neumann (กำหนดความชัน)
> - ฟลักซ์ความร้อน $q = -k \nabla T$

#### การถ่ายเทความร้อนแบบพา (Convective Heat Transfer)

```cpp
externalWall
{
    type            externalWallHeatFluxTemperature; // Convective BC
    mode            coefficient;     // Use heat transfer coefficient
    h               uniform 25;      // W/m²K - heat transfer coefficient
    Ta              uniform 293;     // K - ambient temperature
    thicknessLayers (0.001 0.002);   // Wall layer thicknesses [m]
    kappaLayers     (0.5 0.1);       // Thermal conductivity of layers [W/mK]
}
```

> **📖 คำอธิบาย (Explanation):**
> จำลองการถ่ายเทความร้อนแบบพาระหว่างผนังและสภาพแวดล้อม รองรับผนังหลายชั้น
>
> **แหล่งที่มา (Source):** ไฟล์ `0/T`
>
> **แนวคิดสำคัญ (Key Concepts):**
> - `externalWallHeatFluxTemperature`: เงื่อนไขขอบเขตการถ่ายเทความร้อนแบบพา
> - สมการนิวตันสำหรับการอณู: $q = h(T_s - T_\infty)$

#### ผนังแบบอะเดียแบติก (Adiabatic Wall)

```cpp
adiabaticWalls
{
    type            zeroGradient;    // Zero gradient condition (adiabatic)
}
```

> **📖 คำอธิบาย (Explanation):**
> ผนังที่ไม่มีการถ่ายเทความร้อนผ่าน ใช้สำหรับผนังฉนวน
>
> **แหล่งที่มา (Source):** ไฟล์ `0/T`
>
> **แนวคิดสำคัญ (Key Concepts):**
> - `zeroGradient`: อนุพันธ์ปกติเป็นศูนย์ ($\partial T/\partial n = 0$)
> - ไม่มีฟลักซ์ความร้อนผ่านผนัง

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
// Energy/enthalpy equation solver implementation
// สมการเอนทาลปี/พลังงาน
fvScalarMatrix EEqn
(
    // Transient term: time derivative of enthalpy
    fvm::ddt(rho, he)
    // Convection term: enthalpy transport by fluid motion
  + fvm::div(phi, he)
    // Diffusion term: heat conduction (including turbulent effects)
  - fvm::laplacian(turbulence->alphaEff(), he)
 ==
    // Buoyancy source term: work done by gravity
    rho*(U&g)
    // Kinetic energy terms
  + fvc::ddt(rho, K) + fvc::div(phi, K)
    // Additional heat sources/sinks
  + sources(rho, he)
);

// Calculate enthalpy from total energy
he = (E - 0.5*magSqr(U)) - p/rho;
```

> **📖 คำอธิบาย (Explanation):**
> สมการพลังงาน/เอนทาลปีใน OpenFOAM ที่รวมเอาเอฟเฟกต์การถ่ายเทความร้อนและความปั่นป่วน
>
> **แหล่งที่มา (Source):** `.applications/solvers/heatTransfer/buoyantSimpleFoam/EEqn.H`
>
> **แนวคิดสำคัญ (Key Concepts):**
> - `fvm::ddt`: เทอมข้างเวลา (transient term)
> - `fvm::div`: เทอมการพา (convection term)
> - `fvm::laplacian`: เทอมการแพร่ (diffusion term)
> - `turbulence->alphaEff()`: การแพร่ความร้อนประสิทธิผลรวมความปั่นป่วน
> - `U&g`: เทอมแหล่งกำเนิดจากแรงโน้มถ่วง (buoyancy source)

---

## 🌡️ 2. แบบจำลองเทอร์โมฟิสิกส์ (Thermophysical Models)

ไฟล์ `constant/thermophysicalProperties` ควบคุมการคำนวณคุณสมบัติของของไหล:

### แบบจำลองแก๊สสมบูรณ์ (Perfect Gas Model)

```cpp
thermoType
{
    type            hePsiThermo;     // Psi-based thermodynamics for compressible flows
    mixture         pureMixture;     // Single component mixture
    transport       sutherland;      // Temperature-dependent viscosity
    thermo          hConst;          // Constant specific heat
    equationOfState perfectGas;      // Ideal gas law: p = rho*R*T
    specie          specie;          // Species properties
    energy          sensibleEnthalpy; // Enthalpy as energy variable
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

> **📖 คำอธิบาย (Explanation):**
> การตั้งค่าคุณสมบัติทางเทอร์โมฟิสิกส์สำหรับก๊าซอุดมคติเช่นอากาศ
>
> **แหล่งที่มา (Source):** ไฟล์ `constant/thermophysicalProperties`
>
> **แนวคิดสำคัญ (Key Concepts):**
> - `hePsiThermo`: คำนวณคุณสมบัติจากค่า psi = 1/R*T (สำหรับก๊าศอัดได้)
> - `perfectGas`: ใช้กฎ PV = nRT
> - `sutherland`: ความหนืดตามกฎ Sutherland: $\mu = \mu_0 (T/T_0)^{3/2} (T_0+S)/(T+S)$

### แบบจำลองของเหลวอัดตัวไม่ได้ (Incompressible Liquid Model)

```cpp
thermoType
{
    type            heRhoThermo;     // Rho-based thermodynamics
    mixture         pureMixture;     // Single component
    transport       const;           // Constant viscosity
    thermo          hConst;          // Constant specific heat
    equationOfState rhoConst;        // Constant density
    specie          specie;          // Species properties
    energy          sensibleEnthalpy; // Sensible enthalpy
}

mixture
{
    specie
    {
        molWeight       18.01528;       // kg/kmol (water)
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
        mu              1.002e-3;       // Pa·s - dynamic viscosity
        Pr              7.0;            // Prandtl number
        kappa           0.606;          // W/(m·K) - thermal conductivity
    }
}
```

> **📖 คำอธิบาย (Explanation):**
> การตั้งค่าคุณสมบัติทางเทอร์โมฟิสิกส์สำหรับของเหลวอัดตัวไม่ได้เช่นน้ำ
>
> **แหล่งที่มา (Source):** ไฟล์ `constant/thermophysicalProperties`
>
> **แนวคิดสำคัญ (Key Concepts):**
> - `heRhoThermo`: ใช้ความหนาแน่นโดยตรงในการคำนวณ
> - `rhoConst`: ความหนาแน่นคงที่
> - `Pr`: จำนวน Prandtl = $\mu c_p / k$

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
// Boussinesq approximation for density variations
// Density depends linearly on temperature
rho = rhoRef*(1.0 - beta*(T - TRef));

// Momentum equation with buoyancy source term
// สมการโมเมนตัมพร้อมแรงลอยตัว
tmp<fvVectorMatrix> UEqn
(
    // Convection term
    fvm::div(phi, U)
    // Viscous stress term (deviatoric part)
  + turbulence->divDevReff(U)
 ==
    // Buoyancy force source term (Boussinesq approximation)
    rhoRef*(g - beta*(T - TRef)*g)
);
```

> **📖 คำอธิบาย (Explanation):**
> การใช้การประมาณแบบ Boussinesq เพื่อจำลองแรงลอยตัวในของไหลอัดตัวไม่ได้
>
> **แหล่งที่มา (Source):** `.applications/solvers/heatTransfer/buoyantBoussinesqSimpleFoam/UEqn.H`
>
> **แนวคิดสำคัญ (Key Concepts):**
> - `rhoRef`: ความหนาแน่นอ้างอิง (reference density)
> - `beta`: สัมประสิทธิ์การขยายตัวทางความร้อน (thermal expansion coefficient)
> - การประมาณแบบ Boussinesq ถือว่าความหนาแน่นแปรผันเฉพาะในเทอมแรงลอยตัวเท่านั้น
> - `divDevReff`: แรงเฉือนมุมฉากที่มีประสิทธิภาพรวมความปั่นป่วน

#### `buoyantSimpleFoam`

**ลักษณะ**: Solver แบบสภาวะคงที่ (steady-state) สำหรับการไหลแบบอัดได้ที่มีแรงลอยตัวและการถ่ายเทความร้อน

**ขั้นตอนการทำงาน**:
1. **สมการโมเมนตัม**: แก้สมการโมเมนตัมพร้อมการพาความร้อนและแรงลอยตัว
2. **สมการพลังงาน**: แก้สมการพลังงานสำหรับอุณหภูมิหรือเอนทาลปี
3. **Pressure-velocity coupling**: ใช้ขั้นตอน SIMPLE

**โครงสร้างการทำงาน**:
```cpp
// Main iteration loop for steady-state solver
// ลูปหลัก
while (simple.loop())
{
    // Momentum equation solver
    // สมการโมเมนตัม
    tmp<fvVectorMatrix> UEqn
    (
        fvm::div(phi, U)                    // Convection
      + turbulence->divDevReff(U)           // Viscous stress
    );

    UEqn.relax();                            // Under-relaxation
    solve(UEqn == -fvc::grad(p));           // Solve with pressure gradient

    // Energy equation solver
    // สมการพลังงาน
    fvScalarMatrix TEqn
    (
        fvm::div(phi, h)                     // Enthalpy convection
      + fvm::SuSp(divPhidp, h)               // Pressure work term
      - fvm::laplacian(kappaEff, h)          // Heat diffusion
     ==
        sources(h)                           // Heat sources/sinks
    );

    TEqn.relax();                            // Under-relaxation
    TEqn.solve();                            // Solve energy equation
}
```

> **📖 คำอธิบาย (Explanation):**
> โครงสร้างหลักของ solver สภาวะคงที่สำหรับการไหลแบบอัดได้พร้อมการถ่ายเทความร้อน
>
> **แหล่งที่มา (Source):** `.applications/solvers/heatTransfer/buoyantSimpleFoam/buoyantSimpleFoam.C`
>
> **แนวคิดสำคัญ (Key Concepts):**
> - `simple.loop()`: ลูปการวนซ้ำแบบ SIMPLE algorithm
> - `relax()`: การผ่อนคลาย (under-relaxation) เพื่อความเสถียร
> - `divPhidp`: เทอมงานของความดัน (pressure work)
> - `kappaEff`: การนำความร้อนประสิทธิผล

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
// Region coupling definition
regionCouplePolyPatch
{
    type            regionCouple;     // Coupled patch type
    neighbourRegion solidRegion;      // Name of neighbor region
    neighbourPatch solidToFluidPatch; // Name of neighbor patch
}

// Coupled boundary condition for heat transfer
// Coupled boundary condition
{
    type            compressible::turbulentTemperatureCoupledBaffleMixed;
    Tnbr            T;                // Neighbor temperature field
    kappaMethod     fluidThermo;      // Thermal conductivity method: fluidThermo or solidThermo
}
```

> **📖 คำอธิบาย (Explanation):**
> การตั้งค่าการเชื่อมต่อความร้อนระหว่างภูมิภาคของไหลและของแข็ง
>
> **แหล่งที่มา (Source):** ไฟล์ `constant/polyMesh/boundary` และ `0/T`
>
> **แนวคิดสำคัญ (Key Concepts):**
> - `regionCouple`: การเชื่อมต่อระหว่างภูมิภาค (region coupling)
> - `turbulentTemperatureCoupledBaffleMixed`: เงื่อนไขขอบเขตแบบผสมสำหรับการถ่ายเทความร้อนผ่านผนัง
> - `kappaMethod`: วิธีการคำนวณสภาพนำความร้อน (จากของไหลหรือของแข็ง)
> - `Tnbr`: อุณหภูมิของบริเวณข้างเคียง (neighbor temperature)

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

---

## 🧠 5. Concept Check (ทดสอบความเข้าใจ)

1. **ทำไมโลหะถึงรู้สึก "เย็น" กว่าไม้ ทั้งที่อุณหภูมิห้องเท่ากัน?**
   <details>
   <summary>เฉลย</summary>
   เพราะโลหะมีค่า **Thermal Conductivity ($k$)** สูงกว่าไม้มาก มันจึงสามารถ "ดึง" (Conduct) ความร้อนออกจากนิ้วมือของเราได้รวดเร็วกว่าไม้ เราจึงรู้สึกว่ามันเย็น (ความรู้สึกเย็นคืออัตราการสูญเสียความร้อน ไม่ใช่อุณหภูมิ)
   </details>

2. **Prandtl Number ($Pr$) บอกอะไรเรา?**
   <details>
   <summary>เฉลย</summary>
   $Pr$ คืออัตราส่วนระหว่าง **Momentum Diffusivity** ($\nu$) ต่อ **Thermal Diffusivity** ($\alpha$)
   - ถ้า $Pr \ll 1$ (เช่น โลหะเหลว): ความร้อนกระจายเร็วกว่าโมเมนตัมมาก (Thermal Boundary Layer หนา)
   - ถ้า $Pr \gg 1$ (เช่น น้ำมัน): โมเมนตัมกระจายเร็วกว่าความร้อน (Thermal Boundary Layer บางเฉียบ)
   </details>

3. **ทำไม Boussinesq Approximation ถึงใช้ไม่ได้กับความแตกต่างอุณหภูมิที่สูงมาก (เช่น ไฟไหม้)?**
   <details>
   <summary>เฉลย</summary>
   เพราะ Boussinesq สมมติว่าความหนาแน่นเปลี่ยนเฉพาะในเทอมแรงลอยตัว แต่ค่าอื่นๆ คงที่ ซึ่งใช้ได้เมื่อ $\Delta T$ น้อยๆ แต่ในกรณีไฟไหม้ หรือ $\Delta T$ สูง ความหนาแน่นเปลี่ยนแปลงมากจนกระทบต่อเทอม Inertia และ Continuity ด้วย ทำให้สมมติฐานนี้ไม่แม่นยำ ต้องใช้ Full Compressible Solver แทน
   </details>