# กลไกการถ่ายเทความร้อน: การนำ การพา และการแผ่รังสี

การจำลอง CFD ที่แม่นยำต้องระบุกลไกการถ่ายเทความร้อนให้สอดคล้องกับฟิสิกส์ของปัญหา

---

## 🧱 1. การนำความร้อน (Conduction)

การนำความร้อนเป็นการถ่ายเทพลังงานผ่านการปฏิสัมพันธ์ของโมเลกุลในวัสดุที่เป็นของแข็งหรือของไหลที่หยุดนิ่ง

### 1.1 กฎของฟูเรียร์ (Fourier's Law)

สมการควบคุมพื้นฐานสำหรับการถ่ายเทความร้อนในการไหลแบบเฟสเดียวคือสมการการอนุรักษ์พลังงาน:

$$\frac{\partial (\rho h)}{\partial t} + \nabla \cdot (\rho \mathbf{u} h) = \nabla \cdot (k \nabla T) + Q$$

**นิยามตัวแปร:**
- $\rho$ คือ ความหนาแน่น $[\text{kg/m}^3]$
- $h$ คือ เอนทาลปีจำเพาะ $[\text{J/kg}]$
- $\mathbf{u}$ คือ เวกเตอร์ความเร็ว $[\text{m/s}]$
- $k$ คือ สภาพนำความร้อน $[\text{W/(m·K)}]$
- $T$ คือ อุณหภูมิ $[\text{K}]$
- $Q$ คือ แหล่งกำเนิดความร้อน $[\text{W/m}^3]$

ในรูปของอุณหภูมิ สมการสามารถเขียนได้เป็น:

$$\rho c_p \frac{\partial T}{\partial t} + \rho c_p \mathbf{u} \cdot \nabla T = k \nabla^2 T + Q$$

โดยที่ $c_p$ คือ ความจุความร้อนจำเพาะที่ความดันคงที่ $[\text{J/(kg·K)}]$

### 1.2 การนำกฎของฟูเรียร์ไปใช้ใน OpenFOAM

กฎของฟูเรียร์ระบุว่าฟลักซ์ความร้อนเป็นสัดส่วนกับความชันของอุณหภูมิเชิงลบ:

$$\mathbf{q} = -k \nabla T$$

ใน OpenFOAM สิ่งนี้ถูกนำไปใช้ผ่านการแบ่งส่วนแบบ finite volume ของตัวดำเนินการ Laplacian

#### OpenFOAM Code Implementation

```cpp
// จาก fvScalarMatrix.H
template<>
tmp<fvScalarMatrix> laplacian
(
    const GeometricField<Type, fvPatchField, volMesh>&,
    GeometricField<Type, fvPatchField, volMesh>&
);

// การใช้งานใน solver การถ่ายเทความร้อน
fvScalarMatrix TEqn
(
    fvm::ddt(T) + fvm::div(phi, T)
  - fvm::laplacian(kappa/rho/cp, T)
 ==
    Q/(rho*cp)
);
```

### 1.3 แบบจำลองสภาพนำความร้อน

OpenFOAM รองรับแบบจำลองสภาพนำความร้อนที่หลากหลาย:

#### แบบจำลองที่รองรับ:

| แบบจำลอง | คำอธิบาย | กรณีการใช้งาน |
|-----------|-----------|--------------|
| **สภาพนำความร้อนคงที่** | ค่าสภาพนำความร้อนคงที่ | วัสดุโฮโมจีเนียส |
| **สภาพนำความร้อนขึ้นอยู่กับอุณหภูมิ** | ฟังก์ชัน $k(T)$ | วัสดุมีคุณสมบัติแปรผัน |
| **สภาพนำความร้อนประสิทธิผล** | สำหรับสื่อพรุน หรือวัสดุผสม | สื่อพรุน คอมโพสิต |

#### การนำไปใช้ใน OpenFOAM

```cpp
// ตัวอย่างสภาพนำความร้อนขึ้นอยู่กับอุณหภูมิ
volScalarField k
(
    IOobject
    (
        "k",
        runTime.timeName(),
        mesh,
        IOobject::READ_IF_PRESENT,
        IOobject::AUTO_WRITE
    ),
    mesh,
    dimensionedScalar("k", dimensionSet(1, 1, -3, -1, 0, 0, 0), 0.0)
);

// แบบจำลองขึ้นอยู่กับอุณหภูมิ
k = k0 * (1.0 + beta*(T - T0));
```

---

## 💨 2. การพาความร้อน (Convection)

เป็นการถ่ายเทความร้อนที่เกิดขึ้นเนื่องจากการเคลื่อนที่ของของไหล แบ่งเป็นสองประเภทหลัก:

### 2.1 การพาความร้อนแบบบังคับ (Forced Convection)

การพาความร้อนแบบบังคับเกิดขึ้นเมื่อการเคลื่อนที่ของของไหลถูกกระตุ้นโดยวิธีการภายนอก (ปั๊ม พัดลม ฯลฯ)

สัมประสิทธิ์การพาความร้อน $h_c$ เชื่อมโยงฟลักซ์ความร้อนที่ผนังกับความแตกต่างของอุณหภูมิ:

$$q_w = h_c (T_w - T_\infty)$$

#### จำนวนไร้มิติสำคัญ:

| จำนวนไร้มิติ | สูตร | ความหมาย |
|---------------|-------|------------|
| **จำนวนเรย์โนลด์ส** | $Re = \frac{\rho u L}{\mu}$ | อัตราส่วนแรงเฉื่อยต่อแรงเหนียว |
| **จำนวนแพรนเดิล** | $Pr = \frac{\mu c_p}{k}$ | อัตราส่วนการแพร่โมเมนตัมต่อการแพร่ความร้อน |
| **จำนวนนัสเซิลต์** | $Nu = \frac{h_c L}{k}$ | อัตราส่วนการพาความร้อนต่อการนำความร้อน |

#### ความสัมพันธ์จำนวนนัสเซิลต์:

- **Dittus-Boelter**: $Nu = 0.023 Re^{0.8} Pr^n$
  - $n = 0.4$ สำหรับการให้ความร้อน
  - $n = 0.3$ สำหรับการทำให้เย็น

- **Sieder-Tate**: $Nu = 0.027 Re^{0.8} Pr^{1/3} (\mu/\mu_w)^{0.14}$

#### OpenFOAM Implementation

```cpp
// ตัวอย่างการคำนวณฟลักซ์ความร้อนที่ผนังสำหรับการพาความร้อนแบบบังคับ
scalar Re = rho.value()*mag(U_wall)*L_char/mu.value();
scalar Pr = mu.value()*cp.value()/k.value();
scalar Nu = 0.023*pow(Re, 0.8)*pow(Pr, 0.4);  // Dittus-Boelter
scalar h_conv = Nu*k.value()/L_char;

q_wall = h_conv * (T_wall - T_bulk);
```

### 2.2 การพาความร้อนตามธรรมชาติ (Natural Convection)

การพาความร้อนตามธรรมชาติเกิดขึ้นเนื่องจากแรงลอยตัวที่เกิดจากการเปลี่ยนแปลงความหนาแน่น

แบบจำลองแรงลอยตัวใช้การประมาณแบบ Boussinesq:

$$\mathbf{f}_b = \rho \mathbf{g} \beta (T - T_\text{ref})$$

**นิยามตัวแปร:**
- $\mathbf{g}$ คือ เวกเตอร์ความเร่งเนื่องจากแรงโน้มถ่วง
- $\beta$ คือ สัมประสิทธิ์การขยายตัวทางความร้อน
- $T_\text{ref}$ คือ อุณหภูมิอ้างอิง

#### จำนวนเรย์ลี (Rayleigh Number)

จำนวนเรย์ลีเป็นตัวบ่งชี้การพาความร้อนตามธรรมชาติ:

$$Ra = \frac{g \beta \Delta T L^3}{\nu \alpha} = Gr \cdot Pr$$

โดยที่:
- $Gr = \frac{g \beta \Delta T L^3}{\nu^2}$ คือ จำนวนกราสชอฟ (Grashof number)
- $\nu = \mu/\rho$ คือ ความหนืดจลนศาสตร์ (kinematic viscosity)
- $\alpha = k/(\rho c_p)$ คือ การแพร่ความร้อน (thermal diffusivity)

#### การนำการประมาณแบบ Boussinesq ไปใช้

```cpp
// การนำการประมาณแบบ Boussinesq ไปใช้
volVectorField gBoussinesq
(
    IOobject("gBoussinesq", runTime.timeName(), mesh),
    rho*beta*(T - T_ref)*g
);

// ในสมการโมเมนตัม
fvVectorMatrix UEqn
(
    fvm::ddt(U) + fvm::div(phi, U)
  - fvm::laplacian(nu, U)
 ==
    gBoussinesq
);
```

---

## ☀️ 3. การแผ่รังสี (Radiation)

เป็นการถ่ายเทพลังงานผ่านคลื่นแม่เหล็กไฟฟ้า ซึ่งมีความสำคัญมากในปัญหาที่มีอุณหภูมิสูง

### 3.1 กฎของสเตฟาน-โบลต์ซมันน์ (Stefan-Boltzmann Law)

$$q_{rad} = \varepsilon \sigma (T^4_{hot} - T^4_{cold})$$

**นิยามตัวแปร:**
- $\varepsilon$ คือ Emissivity (ค่าการเปล่งรังสี)
- $\sigma$ คือค่าคงที่ของ Stefan-Boltzmann ($5.67 \times 10^{-8} \, \text{W/(m}^2\text{K}^4)$)

### 3.2 สมการการถ่ายโอนการแผ่รังสี (Radiative Transfer Equation - RTE)

สมการการถ่ายโอนการแผ่รังสี (RTE) ควบคุมการถ่ายโอนการแผ่รังสี:

$$\mathbf{s} \cdot \nabla I(\mathbf{x}, \mathbf{s}) = \kappa I_b - \beta I + \sigma_s \int_{4\pi} I(\mathbf{x}, \mathbf{s}') \Phi(\mathbf{s}, \mathbf{s}') \, \mathrm{d}\Omega'$$

**นิยามตัวแปร:**
- $I$ คือ ความเข้มของการแผ่รังสี (radiation intensity)
- $\mathbf{s}$ คือ เวกเตอร์ทิศทาง
- $\kappa$ คือ สัมประสิทธิ์การดูดกลืน (absorption coefficient)
- $\beta = \kappa + \sigma_s$ คือ สัมประสิทธิ์การดับสูญ (extinction coefficient)
- $\sigma_s$ คือ สัมประสิทธิ์การกระเจิง (scattering coefficient)
- $\Phi$ คือ ฟังก์ชันเฟสการกระเจิง (scattering phase function)

### 3.3 แบบจำลอง P-1 Radiation Model

แบบจำลอง P-1 เป็นแบบจำลองการแผ่รังสีที่ง่ายที่สุดใน OpenFOAM โดยใช้การกระจายอนุกรมฮาร์มอนิกทรงกลมอันดับหนึ่งของ RTE:

$$\nabla \cdot \frac{1}{3\kappa} \nabla G = \kappa (4\sigma T^4 - G)$$

โดยที่ $G$ คือ การแผ่รังสีที่ตกกระทบ (incident radiation) และ $\sigma$ คือ ค่าคงที่ของ Stefan-Boltzmann

#### OpenFOAM Implementation

```cpp
// การนำแบบจำลอง P-1 ไปใช้
fvScalarMatrix GEqn
(
    fvm::laplacian(1.0/(3.0*aRad + 0.0), G)
 ==
    aRad*4.0*physicoChemical::sigma*T4 - aRad*G
);

GEqn.relax();
GEqn.solve();
```

### 3.4 การแผ่รังสีแบบพื้นผิวต่อพื้นผิว (Surface-to-Surface Radiation)

สำหรับสื่อที่ไม่มีส่วนร่วม (non-participating media) การแผ่รังสีแบบพื้นผิวต่อพื้นผิวจะพิจารณาถึงปัจจัยการมองเห็น (view factors) ระหว่างพื้นผิว:

$$Q_{ij} = F_{ij} \epsilon_i A_i \sigma (T_i^4 - T_j^4)$$

โดยที่ $F_{ij}$ คือ ปัจจัยการมองเห็นระหว่างพื้นผิว $i$ และ $j$

#### OpenFOAM Implementation

```cpp
// การคำนวณปัจจัยการมองเห็น
scalarField Fij(nFaces, 0.0);
forAll(Fij, i)
{
    forAll(Fij, j)
    {
        vector ri = faceCentres[i];
        vector rj = faceCentres[j];
        vector di = faceAreas[i]/mag(faceAreas[i]);
        vector dj = faceAreas[j]/mag(faceAreas[j]);

        scalar cosTheta = max(di & (rj - ri)/mag(rj - ri), 0.0);
        scalar cosThetaJ = max(-dj & (ri - rj)/mag(ri - rj), 0.0);

        Fij[i] = cosTheta * cosThetaJ / (pi * pow(mag(rj - ri), 2));
    }
}
```

---

## 🚪 4. เงื่อนไขขอบเขต (Thermal Boundary Conditions)

| ประเภท | คำสั่งใน OpenFOAM | คำอธิบาย |
|-------|------------------|----------|
| **อุณหภูมิคงที่** | `fixedValue` | กำหนดอุณหภูมิผิวตรงๆ |
| **ฟลักซ์ความร้อนคงที่** | `fixedGradient` | กำหนดเกรเดียนต์อุณหภูมิ $\partial T/\partial n$ |
| **อะเดียแบติก (ฉนวน)** | `zeroGradient` | ไม่มีการไหลของความร้อนข้ามขอบเขต |
| **การพาความร้อน** | `externalWallHeatFluxTemperature` | ระบุ $h$ และอุณหภูมิแวดล้อม $T_a$ |

### 4.1 อุณหภูมิคงที่ (`fixedValue`)

```cpp
walls
{
    type            fixedValue;
    value           uniform 300;  // อุณหภูมิในหน่วยเคลวิน
}
```

**กรณีการใช้งาน:**
- ผนังที่ถูกควบคุมอุณหภูมิอย่างแม่นยำ
- เงื่อนไขขอบเขตอินพุทที่รู้อุณหภูมิ
- การทดสอบการตรวจสอบเชิงตัวเลข

### 4.2 ฟลักซ์ความร้อน (`fixedGradient`)

```cpp
walls
{
    type            fixedGradient;
    gradient        uniform 1000;  // ฟลักซ์ความร้อน [W/m^2]/k
}
```

**กรณีการใช้งาน:**
- การให้ความร้อนคงที่ที่ผนัง
- สมมติฐานความร้อนคงที่ที่ผิวขอบเขต
- การจำลองความร้อนแบบหนึ่งมิติ

### 4.3 การพาความร้อน (`externalWallHeatFluxTemperature`)

```cpp
walls
{
    type            externalWallHeatFluxTemperature;
    mode            coefficient;
    h               uniform 10;      // สัมประสิทธิ์การถ่ายเทความร้อน
    Ta              uniform 293;     // อุณหภูมิแวดล้อม
    thicknessLayers (0.001 0.002);    // ความหนาของชั้นผนัง
    kappaLayers     (0.5 0.1);        // สภาพนำความร้อนของชั้น
}
```

**กรณีการใช้งาน:**
- การถ่ายเทความร้อนระหว่างภายนอกและภายใน
- ผนังแบบหลายชั้น
- การจำลองความร้อนระหว่างวัสดุ

### 4.4 Boundary Conditions การแผ่รังสี (`greyDiffusiveRadiation`)

```cpp
walls
{
    type            greyDiffusiveRadiation;
    emissivity      uniform 0.8;
    Tambient        uniform 300;
    qr              qr;              // สนามการแผ่รังสีที่ตกกระทบ
}
```

### 4.5 ผนังแบบอะเดียแบติก (`zeroGradient`)

```cpp
adiabaticWalls
{
    type            zeroGradient;
}
```

**กรณีการใช้งาน:**
- ผนังฉนวนความร้อน
- สมมาตรทางความร้อน
- การจำลองที่ไม่มีการสูญเสียความร้อน

---

## 🔧 5. การนำ Solver ของ OpenFOAM ไปใช้

### 5.1 Solver การถ่ายเทความร้อนแบบไม่สามารถอัดได้ (Incompressible Heat Transfer Solvers)

#### `buoyantSimpleFoam`

**ลักษณะ**: Solver แบบสภาวะคงที่ (steady-state) สำหรับการไหลแบบปั่นป่วนที่มีแรงลอยตัวและการถ่ายเทความร้อน

**ขั้นตอนการทำงาน**:
1. **สมการโมเมนตัม**: แก้สมการโมเมนตัมพร้อมการพาความร้อนและแรงลอยตัว
2. **สมการพลังงาน**: แก้สมการพลังงานสำหรับอุณหภูมิหรือเอนทาลปี
3. **Pressure-velocity coupling**: ใช้ขั้นตอน SIMPLE

#### โครงสร้างการทำงาน:

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

#### `buoyantBoussinesqSimpleFoam`

**ลักษณะ**: Solver การไหลแบบมีแรงลอยตัวโดยใช้การประมาณแบบ Boussinesq

**คุณสมบัติเฉพาะ**:
- ใช้การประมาณแบบ Boussinesq สำหรับการเปลี่ยนแปลงความหนาแน่น
- เหมาะสำหรับการเปลี่ยนแปลงอุณหภูมิเล็กน้อย
- ประหยัดค่าใช้จ่ายการคำนวณเมื่อเทียบกับ solver แบบอัดได้

#### การเปลี่ยนแปลงความหนาแน่นแบบ Boussinesq

```cpp
// การเปลี่ยนแปลงความหนาแน่นแบบ Boussinesq
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

#### `heatTransferFoam`

**ลักษณะ**: Solver เฉพาะสำหรับการถ่ายเทความร้อนโดยไม่คำนึงถึงการไหล

```cpp
// สมการอุณหภูมิ
fvScalarMatrix TEqn
(
    fvm::ddt(T)
  + fvm::div(phi, T)
  - fvm::laplacian(DT, T)
 ==
    Q/(rho*cp)
);

TEqn.relax();
TEqn.solve();
```

### 5.2 Solver การถ่ายเทความร้อนแบบอัดได้ (Compressible Heat Transfer Solvers)

#### `buoyantPimpleFoam`

**ลักษณะ**: Solver แบบชั่วขณะ (transient) สำหรับการไหลแบบอัดได้และปั่นป่วนพร้อมการถ่ายเทความร้อน

**ความสามารถ**:
- ความหนาแน่นแปรผันตามความดันและอุณหภูมิ
- ใช้ขั้นตอน PIMPLE (ความเป็นผลสืบเนื่องของ PISO และ SIMPLE)
- เหมาะสำหรับปัญหาที่มีการเปลี่ยนแปลงอุณหภูมิขนาดใหญ่

#### สมการพลังงานสำหรับการไหลแบบอัดได้

```cpp
// สมการพลังงานสำหรับการไหลแบบอัดได้
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

## ⚙️ 6. คุณสมบัติขั้นสูงสำหรับการถ่ายเทความร้อน

### 6.1 วัสดุเปลี่ยนสถานะ (Phase Change Materials)

สำหรับการจำลองการเปลี่ยนสถานะ OpenFOAM มีวิธีการแบบเอนทาลปี-รูพรุน (enthalpy-porosity methods)

#### OpenFOAM Implementation

```cpp
// แบบจำลองเอนทาลปี-รูพรุนสำหรับการหลอมเหลว/แข็งตัว
volScalarField liquidFraction
(
    IOobject("liquidFraction", runTime.timeName(), mesh),
    mesh,
    dimensionedScalar("liquidFraction", dimless, 0)
);

forAll(liquidFraction, i)
{
    if (T[i] < Tsolidus)
    {
        liquidFraction[i] = 0;
    }
    else if (T[i] > Tliquidus)
    {
        liquidFraction[i] = 1;
    }
    else
    {
        liquidFraction[i] = (T[i] - Tsolidus)/(Tliquidus - Tsolidus);
    }
}
```

### 6.2 การถ่ายเทความร้อนในสื่อพรุน (Porous Media Heat Transfer)

สำหรับการถ่ายเทความร้อนในสื่อพรุน จะมีการเพิ่มพจน์แหล่งกำเนิดเพิ่มเติม

#### สมการพลังงานพร้อมปฏิสัมพันธ์กับเฟสของแข็ง

```cpp
// แหล่งกำเนิดโมเมนตัมสำหรับสื่อพรุน
DarcyForchheimerCoeffs darcyCoeffs(porousZone, D, F, U);

// สมการพลังงานพร้อมปฏิสัมพันธ์กับเฟสของแข็ง
fvScalarMatrix TEqn
(
    fvm::ddt(rho, T)
  + fvm::div(phi, T)
  - fvm::laplacian(kEff/rho/cp, T)
 ==
    solidPhaseSource
  + porositySource
);
```

### 6.3 การถ่ายเทความร้อนแบบสังยุค (Conjugate Heat Transfer - CHT)

สำหรับการเชื่อมต่อการถ่ายเทความร้อนระหว่างของแข็งและของไหล

#### การถ่ายเทความร้อนแบบหลายภูมิภาค (Multi-region heat transfer)

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
    kappaMethod     fluidThermo;  // หรือ solidThermo
}
```

---

## 📊 7. ข้อควรพิจารณาเชิงตัวเลข (Numerical Considerations)

### 7.1 ข้อจำกัดของ Time Step

สำหรับการจำลองการถ่ายเทความร้อนแบบชัดแจ้ง (explicit) time step จะถูกจำกัดโดย:

$$\Delta t \leq \frac{\Delta x^2}{2\alpha}$$

โดยที่ $\alpha = k/(\rho c_p)$ คือ การแพร่ความร้อน (thermal diffusivity)

#### OpenFOAM Implementation

```cpp
// การคำนวณ time step เพื่อความเสถียร
scalar deltaX = pow(mesh.V()[0], 1.0/3.0);
scalar alpha = kappa.value()/(rho.value()*cp.value());
scalar maxDeltaT = 0.5*sqr(deltaX)/alpha;

runTime.setDeltaT(min(runTime.deltaTValue(), maxDeltaT));
```

### 7.2 Under-Relaxation เพื่อความเสถียร

```cpp
// ปัจจัยการผ่อนคลาย (Under-relaxation factors) ใน fvSolution
relaxationFactors
{
    fields
    {
        p               0.3;
        U               0.7;
        T               0.8;
        h               0.8;
    }
    equations
    {
        U               0.8;
        T               0.9;
        h               0.9;
    }
}
```

### 7.3 การตั้งค่า Linear Solver

```cpp
// การตั้งค่า Solver สำหรับสมการอุณหภูมิ
T
{
    solver          GAMG;
    smoother        GaussSeidel;
    tolerance       1e-06;
    relTol          0;
    smoother        GaussSeidel;
    nPreSweeps      1;
    nPostSweeps     2;
}
```

---

## ✅ 8. การตรวจสอบความถูกต้องและแนวปฏิบัติที่ดีที่สุด (Validation and Best Practices)

### 8.1 กรณีศึกษาเพื่อการตรวจสอบ (Verification Cases)

| กรณีศึกษา | คำอธิบาย | จุดประสงค์ |
|------------|-----------|-----------|
| **การนำความร้อนแบบสภาวะคงที่** | การนำความร้อน 1 มิติในแผ่นเรียบ | การตรวจสอบผลเฉลยการวิเคราะห์ |
| **การนำความร้อนแบบชั่วขณะ** | การเปลี่ยนแปลงอุณหภูมิที่พื้นผิวอย่างฉับพลัน | การตรวจสอบการวิวัฒนาการเวลา |
| **การพาความร้อนตามธรรมชาติ** | การพาความร้อนแบบ Rayleigh-Bénard | การตรวจสอบแรงลอยตัวและการปั่นป่วน |
| **การพาความร้อนแบบบังคับ** | การไหลเหนือแผ่นเรียบที่ได้รับความร้อน | การตรวจสอบความสัมพันธ์การพาความร้อน |

### 8.2 แนวทางการสร้าง Mesh

#### การจำแนกชั้นขอบเขต (Boundary Layer Resolution)
- **$y^+ \approx 1$** สำหรับการจำลองการถ่ายเทความร้อนใกล้ผนัง
- **ชั้นขอบเขตความร้อน**: $\delta_T \sim \frac{L}{Re^{0.5} Pr^{1/3}}$
- **ความเป็นอิสระของ Mesh**: ดำเนินการศึกษาการปรับปรุงกริดอย่างเป็นระบบ

### 8.3 แนวทางการเลือก Solver

| การใช้งาน | Solver ที่แนะนำ | คุณสมบัติหลัก |
|---|---|---|
| การพาความร้อนตามธรรมชาติ | `buoyantBoussinesqSimpleFoam` | การประมาณแบบ Boussinesq |
| การถ่ายเทความร้อนแบบอัดได้ | `buoyantPimpleFoam` | ความหนาแน่นแปรผัน, ชั่วขณะ |
| การนำความร้อนอย่างง่าย | `laplacianFoam` | การนำความร้อนอย่างเดียว |
| การถ่ายเทความร้อนแบบสังยุค | `chtMultiRegionFoam` | การเชื่อมต่อหลายภูมิภาค |

---

## 🚀 9. การเพิ่มประสิทธิภาพประสิทธิภาพ (Performance Optimization)

### 9.1 การประมวลผลแบบขนาน (Parallel Computing)

การจำลองการถ่ายเทความร้อนได้รับประโยชน์จากการแบ่งโดเมน:

```bash
# แบ่งเคสสำหรับการประมวลผลแบบขนาน
decomposePar

# รันแบบขนาน
mpirun -np 8 buoyantSimpleFoam -parallel

# รวบรวมผลลัพธ์
reconstructPar
```

### 9.2 การเพิ่มประสิทธิภาพหน่วยความจำ (Memory Optimization)

- ใช้ object `tmp` สำหรับฟิลด์ชั่วคราว
- เพิ่มประสิทธิภาพการจัดเก็บสำหรับเทนเซอร์สมมาตร (symmetric tensors)
- ลดการถ่ายโอนฟิลด์ระหว่างภูมิภาคให้น้อยที่สุด

---

เอกสารนี้ครอบคลุมทั้งพื้นฐานทางทฤษฎีและรายละเอียดการนำไปใช้จริงสำหรับการวิเคราะห์ปัญหาทางความร้อนด้วย CFD อย่างมีประสิทธิภาพ

---
**หัวข้อถัดไป**: [[การไหลที่ขับเคลื่อนด้วยแรงลอยตัว]]
