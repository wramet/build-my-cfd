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
// Template specialization for Laplacian operator
// from src/finiteVolume/fvMatrices/fvScalarMatrix/fvScalarMatrix.H
template<>
tmp<fvScalarMatrix> laplacian
(
    const GeometricField<Type, fvPatchField, volMesh>&,
    GeometricField<Type, fvPatchField, volMesh>&
);

// Heat transfer solver implementation using finite volume method
// Equation: dT/dt + div(phi,T) - laplacian(alpha,T) = Q/(rho*cp)
fvScalarMatrix TEqn
(
    fvm::ddt(T) + fvm::div(phi, T)
  - fvm::laplacian(kappa/rho/cp, T)
 ==
    Q/(rho*cp)
);
```

**แหล่งที่มา:** 📂 `src/finiteVolume/fvMatrices/fvScalarMatrix/fvScalarMatrix.H`

**คำอธิบาย:**
- `fvm::ddt(T)`: เทอมอนุพัทธ์เวลาของอุณหภูมิ (transient term)
- `fvm::div(phi, T)`: เทอมการพาความร้อน (convection term) โดย phi คืออัตราการไหลของมวล
- `fvm::laplacian(kappa/rho/cp, T)`: เทอมการนำความร้อน (conduction term) โดย kappa/rho/cp คือสัมประสิทธิ์การแพร่ความร้อน
- `Q/(rho*cp)`: เทอมแหล่งกำเนิดความร้อน (source term)

**แนวคิดสำคัญ:**
- การใช้ `fvm` (finite volume method) แทน `fvc` (finite volume calculus) เพื่อสร้างเมทริกซ์สำหรับการแก้สมการโดยนัย (implicit)
- การหารด้วย `rho*cp` เพื่อแปลงหน่วยให้อยู่ในรูปของอุณหภูมิ [K]
- ตัวแปร `kappa` คือสภาพนำความร้อน [W/(m·K)]

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
// Temperature-dependent thermal conductivity model
// Linear variation: k = k0 * [1 + beta*(T - T0)]
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

// Apply temperature-dependent model
// k0: reference conductivity at T0
// beta: temperature coefficient [1/K]
k = k0 * (1.0 + beta*(T - T0));
```

**แหล่งที่มา:** 📂 `src/thermophysicalModels/basic/thermoPhysics/` (Basic thermophysical models)

**คำอธิบาย:**
- `IOobject::READ_IF_PRESENT`: อ่านค่าจากไฟล์ถ้ามี หรือสร้างค่าเริ่มต้น
- `dimensionSet(1, 1, -3, -1, 0, 0, 0)`: หน่วย [kg·m/(s³·K)] = [W/(m·K)]
- การใช้โมเดลเชิงเส้นสำหรับการพึ่งพาอุณหภูมิ: $k(T) = k_0[1 + \beta(T-T_0)]$

**แนวคิดสำคัญ:**
- การใช้ `AUTO_WRITE` ให้เขียนฟิลด์ออกมาโดยอัตโนมัติเมื่อจบการคำนวณ
- สามารถใช้ฟังก์ชันที่ซับซ้อนกว่านี้ เช่น พหุนาม หรือฟังก์ชันชิ้นส่วน (piecewise function)
- สำหรับวัสดุที่มีสภาพนำความร้อนแปรผันอย่างมาก อาจต้องใช้การวนซ้ำ (iteration) เพื่อให้การแก้สมการลู่ัน

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
// Forced convection heat transfer coefficient calculation
// Using Dittus-Boelter correlation for turbulent flow in pipes
// Calculate dimensionless numbers
scalar Re = rho.value()*mag(U_wall)*L_char/mu.value();
scalar Pr = mu.value()*cp.value()/k.value();
scalar Nu = 0.023*pow(Re, 0.8)*pow(Pr, 0.4);  // Dittus-Boelter (heating)

// Calculate convection coefficient
// h = Nu * k / L
scalar h_conv = Nu*k.value()/L_char;

// Calculate wall heat flux [W/m²]
// q = h * (T_wall - T_bulk)
q_wall = h_conv * (T_wall - T_bulk);
```

**แหล่งที่มา:** 📂 `src/thermophysicalModels/specie/transport/` (Transport properties)

**คำอธิบาย:**
- `mag(U_wall)`: ขนาดของความเร็วที่ผนัง
- `L_char`: ความยาวลักษณะ (characteristic length) เช่น เส้นผ่านศูนย์กลางท่อ หรือความยาวแผ่น
- จำนวนไร้มิติทั้งหมดไม่มีหน่วย เป็นอัตราส่วนของแรงต่างๆ

**แนวคิดสำคัญ:**
- สมการ Dittus-Boelter ใช้ได้สำหรับ $Re \ge 10,000$, $0.6 \le Pr \le 160$, และ $L/D \ge 10$
- สำหรับการไหลแบบลามินาร์ ใช้ $Nu = 3.66$ (สำหรับท่อกลม) หรือ $Nu = 0.664 Re^{1/2} Pr^{1/3}$ (สำหรับแผ่นเรียบ)
- การพาความร้อนแบบบังคับต้องระบุเงื่อนไขขอบเขตที่เหมาะสม เช่น `externalWallHeatFluxTemperature`

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
// Boussinesq approximation for natural convection
// Buoyancy force term: f_b = rho * g * beta * (T - T_ref)
// Assumes density variation only affects buoyancy term
volVectorField gBoussinesq
(
    IOobject("gBoussinesq", runTime.timeName(), mesh),
    rho*beta*(T - T_ref)*g
);

// Momentum equation with buoyancy source term
// Solves: ddt(U) + div(phi,U) - laplacian(nu,U) = -grad(p) + gBoussinesq
fvVectorMatrix UEqn
(
    fvm::ddt(U) + fvm::div(phi, U)
  - fvm::laplacian(nu, U)
 ==
    gBoussinesq
);
```

**แหล่งที่มา:** 📂 `applications/solvers/heatTransfer/buoyantBoussinesqSimpleFoam/`

**คำอธิบาย:**
- การประมาณแบบ Boussinesq ถือว่าความหนาแน่นคงที่ ยกเว้นในเทอมแรงลอยตัว
- เหมาะสำหรับการเปลี่ยนแปลงอุณหภูมิเล็กน้อย ($\Delta T/T < 0.1$)
- ประหยัดเวลาคำนวณเมื่อเทียบกับแบบจำลอง compressible

**แนวคิดสำคัญ:**
- การใช้ Boussinesq approximation ลดความซับซ้อนของสมการโมเมนตัม
- ไม่เหมาะสำหรับการเปลี่ยนแปลงอุณหภูมิขนาดใหญ่ หรือการไหลที่ความเร็วสูง
- ต้องระบุ `beta` (สัมประสิทธิ์การขยายตัว) และ `T_ref` (อุณหภูมิอ้างอิง) ในไฟล์คุณสมบัติ
- สำหรับการเปลี่ยนแปลงอุณหภูมิขนาดใหญ่ ให้ใช้ `buoyantSimpleFoam` หรือ `buoyantPimpleFoam` แทน

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
// P-1 radiation model implementation
// Solves diffusion equation for incident radiation G
// Equation: laplacian(1/(3*a), G) = a*(4*sigma*T^4 - G)
// where a is absorption coefficient
fvScalarMatrix GEqn
(
    fvm::laplacian(1.0/(3.0*aRad + 0.0), G)
 ==
    aRad*4.0*physicoChemical::sigma*T4 - aRad*G
);

// Relax and solve the radiation equation
// Relaxation improves stability for coupled radiation-flow problems
GEqn.relax();
GEqn.solve();
```

**แหล่งที่มา:** 📂 `src/thermophysicalModels/radiationModels/radiationModel/P1/`

**คำอธิบาย:**
- `aRad`: สัมประสิทธิ์การดูดกลืน (absorption coefficient) [1/m]
- `G`: การแผ่รังสีที่ตกกระทบ (incident radiation) [W/m²]
- `T4`: $T^4$ ที่คำนวณไว้ล่วงหน้าเพื่อประสิทธิภาพ
- แบบจำลอง P-1 แปลง RTE ให้เป็นสมการแบบ diffusion ที่แก้ได้ง่าย

**แนวคิดสำคัญ:**
- P-1 model เหมาะสำหรับสื่อที่มีการดูดกลืนสูง (optically thick media)
- ไม่เหมาะสำหรับสื่อโปร่งแสง (transparent media) หรือการแผ่รังสีแบบ surface-to-surface
- การใช้ `relax()` ช่วยให้การแก้ปัญหาลู่ันเมื่อ radiation และ flow coupling แรงมาก
- ต้องระบุค่า `aRad` ในไฟล์คุณสมบัติ radiation

### 3.4 การแผ่รังสีแบบพื้นผิวต่อพื้นผิว (Surface-to-Surface Radiation)

สำหรับสื่อที่ไม่มีส่วนร่วม (non-participating media) การแผ่รังสีแบบพื้นผิวต่อพื้นผิวจะพิจารณาถึงปัจจัยการมองเห็น (view factors) ระหว่างพื้นผิว:

$$Q_{ij} = F_{ij} \epsilon_i A_i \sigma (T_i^4 - T_j^4)$$

โดยที่ $F_{ij}$ คือ ปัจจัยการมองเห็นระหว่างพื้นผิว $i$ และ $j$

#### OpenFOAM Implementation

```cpp
// View factor calculation for surface-to-surface radiation
// Computes geometric view factors between face pairs
// Assumes diffuse gray surfaces
scalarField Fij(nFaces, 0.0);
forAll(Fij, i)
{
    forAll(Fij, j)
    {
        vector ri = faceCentres[i];
        vector rj = faceCentres[j];
        vector di = faceAreas[i]/mag(faceAreas[i]);
        vector dj = faceAreas[j]/mag(faceAreas[j]);

        // Cosine of angle between normal and line of sight
        scalar cosTheta = max(di & (rj - ri)/mag(rj - ri), 0.0);
        scalar cosThetaJ = max(-dj & (ri - rj)/mag(ri - rj), 0.0);

        // View factor from i to j
        // Fij = cos(theta_i) * cos(theta_j) / (pi * r^2)
        Fij[i] = cosTheta * cosThetaJ / (pi * pow(mag(rj - ri), 2));
    }
}
```

**แหล่งที่มา:** 📂 `src/thermophysicalModels/radiationModels/radiationModel/viewFactor/`

**คำอธิบาย:**
- `faceCentres`: ตำแหน่งกลางหน้า (face centers)
- `faceAreas`: เวกเตอร์พื้นที่หน้า (face area vectors) ชี้ไปทางปกติ (normal)
- ใช้หลักการ cosines law สำหรับ diffuse surfaces
- `max(..., 0.0)` รับประกันว่า view factors ไม่ติดลบ

**แนวคิดสำคัญ:**
- การคำนวณ view factor แบบนี้มีความซับซ้อน O(N²) โดยที่ N จำนวนหน้าผนัง
- ในทางปฏิบัติใช้ ray tracing หรือ Monte Carlo methods สำหรับ geometries ที่ซับซ้อน
- สำหรับการคำนวณ view factor ที่มีประสิทธิภาพ ให้ใช้ `viewFactors` utility ใน OpenFOAM
- การแผ่รังสีแบบ surface-to-surface ไม่คำนึงถึงการดูดกลืนของสื่อระหว่างพื้นผิว

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
    value           uniform 300;  // Temperature in Kelvin
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
    gradient        uniform 1000;  // Heat flux [W/m^2]/k
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
    h               uniform 10;      // Heat transfer coefficient [W/(m²·K)]
    Ta              uniform 293;     // Ambient temperature [K]
    thicknessLayers (0.001 0.002);    // Wall layer thicknesses [m]
    kappaLayers     (0.5 0.1);        // Layer thermal conductivities [W/(m·K)]
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
    qr              qr;              // Incident radiation field
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
// Main iteration loop for steady-state solver
// SIMPLE algorithm: Semi-Implicit Method for Pressure-Linked Equations
while (simple.loop())
{
    // Momentum equation with convection and diffusion
    // Solves: div(phi,U) + divDevReff(U) = -grad(p)
    tmp<fvVectorMatrix> UEqn
    (
        fvm::div(phi, U)
      + turbulence->divDevReff(U)
    );

    // Relax momentum equation for stability
    UEqn.relax();
    // Solve momentum with pressure gradient as source
    solve(UEqn == -fvc::grad(p));

    // Energy equation for enthalpy h
    // Solves: div(phi,h) + divPhidp*h - laplacian(kappaEff,h) = sources
    fvScalarMatrix TEqn
    (
        fvm::div(phi, h)
      + fvm::SuSp(divPhidp, h)
      - fvm::laplacian(kappaEff, h)
     ==
        sources(h)
    );

    // Relax and solve energy equation
    TEqn.relax();
    TEqn.solve();
}
```

**แหล่งที่มา:** 📂 `applications/solvers/heatTransfer/buoyantSimpleFoam/`

**คำอธิบาย:**
- `simple.loop()`: วนซ้ำจนกว่าจะลู่ัน (convergence criteria ใน `fvSolution`)
- `divDevReff(U)`: การแพร่ของความเค้นที่มีประสิทธิภาพ (effective stress divergence)
- `kappaEff`: สภาพนำความร้อนที่มีประสิทธิภาพ (รวม turbulence)

**แนวคิดสำคัญ:**
- ใช้สำหรับการไหลแบบ steady-state ที่มีแรงลอยตัว
- ต้องการ under-relaxation factors ที่เหมาะสมเพื่อความเสถียร
- ใช้ enthalpy ($h$) แทน temperature ($T$) เพื่อรองรับ compressibility
- ใช้ `turbulence->divDevReff(U)`` สำหรับ Reynolds stress modeling

#### `buoyantBoussinesqSimpleFoam`

**ลักษณะ**: Solver การไหลแบบมีแรงลอยตัวโดยใช้การประมาณแบบ Boussinesq

**คุณสมบัติเฉพาะ**:
- ใช้การประมาณแบบ Boussinesq สำหรับการเปลี่ยนแปลงความหนาแน่น
- เหมาะสำหรับการเปลี่ยนแปลงอุณหภูมิเล็กน้อย
- ประหยัดค่าใช้จ่ายการคำนวณเมื่อเทียบกับ solver แบบอัดได้

#### การเปลี่ยนแปลงความหนาแน่นแบบ Boussinesq

```cpp
// Boussinesq approximation for density variations
// rho = rho_ref * [1 - beta*(T - T_ref)]
// Valid for small temperature variations (ΔT/T < 0.1)
rho = rhoRef*(1.0 - beta*(T - TRef));

// Momentum equation with buoyancy source term
// Boussinesq force: f_b = rho_ref * g * beta * (T - T_ref)
tmp<fvVectorMatrix> UEqn
(
    fvm::div(phi, U)
  + turbulence->divDevReff(U)
 ==
    rhoRef*(g - beta*(T - TRef)*g)
);
```

**แหล่งที่มา:** 📂 `applications/solvers/heatTransfer/buoyantBoussinesqSimpleFoam/`

**คำอธิบาย:**
- `rhoRef`: ความหนาแน่นอ้างอิงที่อุณหภูมิ `TRef`
- การคูณด้วย `g` ทั้งสองที่ให้แรงโน้มถ่วงลบด้วยแรงลอยตัว
- การลบ `rhoRef*beta*(T - TRef)*g` จาก `rhoRef*g` ให้แรงสุทธิ

**แนวคิดสำคัญ:**
- การประมาณแบบ Boussinesq ถือว่า density คงที่ในทุกเทอม ยกเว้น buoyancy
- เหมาะสำหรับปัญหา natural convection ที่ไม่รุนแรง
- ต้องไม่ใช้กับปัญหาที่มีความเร็วสูง หรือการบีบอัดมาก
- `beta` มักอยู่ในช่วง $10^{-3}$ ถึง $10^{-4}$ K⁻¹ สำหรับของเหลว

#### `heatTransferFoam`

**ลักษณะ**: Solver เฉพาะสำหรับการถ่ายเทความร้อนโดยไม่คำนึงถึงการไหล

```cpp
// Heat conduction equation (no fluid flow)
// Solves: dT/dt + div(phi,T) - laplacian(DT,T) = Q/(rho*cp)
// For pure conduction, phi = 0
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

**แหล่งที่มา:** 📂 `applications/solvers/basic/laplacianFoam/`

**คำอธิบาย:**
- `DT`: การแพร่ความร้อน (thermal diffusivity) = $k/(\rho c_p)$
- สำหรับการนำอย่างเดียว ให้ตั้งค่า `phi = 0`
- เหมาะสำหรับ heat conduction ใน solids

**แนวคิดสำคัญ:**
- Solver นี้ใช้สำหรับปัญหา conduction เท่านั้น (ไม่มี fluid flow)
- ใช้แก้สมการ diffusion: $\partial T/\partial t = \alpha \nabla^2 T + Q/(\rho c_p)$
- สามารถใช้กับ transient หรือ steady-state (ตั้ง `ddtSchemes` เป็น `steadyState`)

### 5.2 Solver การถ่ายเทความร้อนแบบอัดได้ (Compressible Heat Transfer Solvers)

#### `buoyantPimpleFoam`

**ลักษณะ**: Solver แบบชั่วขณะ (transient) สำหรับการไหลแบบอัดได้และปั่นป่วนพร้อมการถ่ายเทความร้อน

**ความสามารถ**:
- ความหนาแน่นแปรผันตามความดันและอุณหภูมิ
- ใช้ขั้นตอน PIMPLE (ความเป็นผลสืบเนื่องของ PISO และ SIMPLE)
- เหมาะสำหรับปัญหาที่มีการเปลี่ยนแปลงอุณหภูมิขนาดใหญ่

#### สมการพลังงานสำหรับการไหลแบบอัดได้

```cpp
// Energy equation for compressible flow
// Solves for total energy E = he + 0.5*magSqr(U)
// Equation: ddt(rho,he) + div(phi,he) - laplacian(alphaEff,he) = sources
fvScalarMatrix EEqn
(
    fvm::ddt(rho, he)
  + fvm::div(phi, he)
  - fvm::laplacian(turbulence->alphaEff(), he)
 ==
    rho*(U&g)                     // Gravitational work
  + fvc::ddt(rho, K) + fvc::div(phi, K)  // Kinetic energy
  + sources(rho, he)             // Other sources
);

// Update enthalpy from total energy
// he = E - 0.5*magSqr(U) - p/rho
he = (E - 0.5*magSqr(U)) - p/rho;
```

**แหล่งที่มา:** 📂 `applications/solvers/heatTransfer/buoyantPimpleFoam/`

**คำอธิบาย:**
- `he`: sensible enthalpy [J/kg]
- `E`: total energy [J/kg]
- `K`: kinetic energy per unit mass = $0.5|\mathbf{U}|^2$
- `alphaEff`: effective thermal diffusivity (รวม turbulence)

**แนวคิดสำคัญ:**
- PIMPLE algorithm รวม PISO (สำหรับ transient) และ SIMPLE (สำหรับ under-relaxation)
- ใช้สำหรับการไหลที่มี compressibility effects สำคัญ
- ต้องระบุ thermophysical model ที่เหมาะสม (เช่n `perfectGas`, `rhoPolynomial`)
- สมการพลังงานรวม work จากความดันและแรงโน้มถ่วง

---

## ⚙️ 6. คุณสมบัติขั้นสูงสำหรับการถ่ายเทความร้อน

### 6.1 วัสดุเปลี่ยนสถานะ (Phase Change Materials)

สำหรับการจำลองการเปลี่ยนสถานะ OpenFOAM มีวิธีการแบบเอนทาลปี-รูพรุน (enthalpy-porosity methods)

#### OpenFOAM Implementation

```cpp
// Enthalpy-porosity method for melting/solidification
// Calculates liquid fraction based on temperature
// Liquid fraction: gamma = 0 (solid), 1 (liquid), 0-1 (mushy zone)
volScalarField liquidFraction
(
    IOobject("liquidFraction", runTime.timeName(), mesh),
    mesh,
    dimensionedScalar("liquidFraction", dimless, 0)
);

// Calculate liquid fraction based on temperature
// Tsolidus: solidus temperature (start of melting)
// Tliquidus: liquidus temperature (end of melting)
forAll(liquidFraction, i)
{
    if (T[i] < Tsolidus)
    {
        liquidFraction[i] = 0;    // Fully solid
    }
    else if (T[i] > Tliquidus)
    {
        liquidFraction[i] = 1;    // Fully liquid
    }
    else
    {
        // Mushy zone (partial melting)
        liquidFraction[i] = (T[i] - Tsolidus)/(Tliquidus - Tsolidus);
    }
}
```

**แหล่งที่มา:** 📂 `applications/solvers/heatTransfer/buoyantSimpleFoam/` (Modified for phase change)

**คำอธิบาย:**
- `Tsolidus`: อุณหภูมิเริ่มละลาย (solidus temperature)
- `Tliquidus`: อุณหภูมิละลายหมด (liquidus temperature)
- ช่วง `Tsolidus` ถึง `Tliquidus` เรียกว่า mushy zone

**แนวคิดสำคัญ:**
- วิธีการ enthalpy-porosity ใช้ porous media approach สำหรับ phase change
- ใน mushy zone ให้ใส่ source term ในสมการโมเมนตัมเพื่อจำลองความต้านทาน
- latent heat จะถูกรวมในค่าความจุความร้อนจำเพาะอย่างมีประสิทธิภาพ (effective heat capacity)
- สามารถใช้ `chtMultiRegionFoam` สำหรับปัญหา melting/solidification ที่ซับซ้อน

### 6.2 การถ่ายเทความร้อนในสื่อพรุน (Porous Media Heat Transfer)

สำหรับการถ่ายเทความร้อนในสื่อพรุน จะมีการเพิ่มพจน์แหล่งกำเนิดเพิ่มเติม

#### สมการพลังงานพร้อมปฏิสัมพันธ์กับเฟสของแข็ง

```cpp
// Darcy-Forchheimer coefficients for porous media
// Momentum source: S = - (mu/D + rho*F*|U|)*U
// D: Darcy coefficient (viscous resistance)
// F: Forchheimer coefficient (inertial resistance)
DarcyForchheimerCoeffs darcyCoeffs(porousZone, D, F, U);

// Energy equation with solid-fluid interaction
// Additional source terms for:
// - Solid phase heat transfer
// - Porosity effects on thermal conductivity
fvScalarMatrix TEqn
(
    fvm::ddt(rho, T)
  + fvm::div(phi, T)
  - fvm::laplacian(kEff/rho/cp, T)  // Effective conductivity
 ==
    solidPhaseSource      // Solid-fluid heat transfer
  + porositySource        // Porosity effects
);
```

**แหล่งที่มา:** 📂 `src/finiteVolume/cfdTools/general/porousMedia/`

**คำอธิบาย:**
- `kEff`: สภาพนำความร้อนที่มีประสิทธิภาพ (effective thermal conductivity)
- `solidPhaseSource`: แหล่งกำเนิดจากการแลกเปลี่ยนความร้อนระหว่าง solid-fluid
- `porositySource`: แหล่งกำเนิดจากโครงสร้างพรุน

**แนวคิดสำคัญ:**
- ใช้ Darcy-Forchheimer model สำหรับ resistance ของ porous media
- สภาพนำความร้อนที่มีประสิทธิภาพขึ้นอยู่กับ porosity และ สภาพนำความร้อนของ solid-fluid
- สำหรับ packed beds ใช้ correlations เช่น Zehner-Schlunder หรือ Kunii-Smith
- ต้องระบุ `porosity`, `D`, และ `F` ในไฟล์ `constant/porousZones`

### 6.3 การถ่ายเทความร้อนแบบสังยุค (Conjugate Heat Transfer - CHT)

สำหรับการเชื่อมต่อการถ่ายเทความร้อนระหว่างของแข็งและของไหล

#### การถ่ายเทความร้อนแบบหลายภูมิภาค (Multi-region heat transfer)

```cpp
// Region coupling for conjugate heat transfer
// Couples thermal conditions between solid and fluid regions
regionCouplePolyPatch
{
    type            regionCouple;
    neighbourRegion solidRegion;        // Adjacent region name
    neighbourPatch solidToFluidPatch;   // Corresponding patch name
}

// Coupled boundary condition for heat transfer
// Ensures continuity of temperature and heat flux at interface
{
    type            compressible::turbulentTemperatureCoupledBaffleMixed;
    Tnbr            T;                   // Neighbor region temperature
    kappaMethod     fluidThermo;         // or solidThermo
}
```

**แหล่งที่มา:** 📂 `src/finiteVolume/fields/fvPatchFields/derived/`

**คำอธิบาย:**
- `regionCouple`: patch type สำหรับเชื่อมต่อระหว่าง regions
- `turbulentTemperatureCoupledBaffleMixed`: BC ที่รับประกันความต่อเนื่องของ T และ q
- `kappaMethod`: วิธีการคำนวณสภาพนำความร้อนที่ interface

**แนวคิดสำคัญ:**
- CHT ใช้สำหรับปัญหาที่มีทั้ง solid conduction และ fluid convection
- ใช้ `chtMultiRegionFoam` solver สำหรับปัญหา CHT
- ต้องสร้าง multiple regions ใน `constant/polyMesh` และระบุ coupling
- ที่ interface อุณหภูมิและฟลักซ์ความร้อนต้องต่อเนื่อง
- ใช้ `AMI` (Arbitrary Mesh Interface) สำหรับ non-conformal meshes

---

## 📊 7. ข้อควรพิจารณาเชิงตัวเลข (Numerical Considerations)

### 7.1 ข้อจำกัดของ Time Step

สำหรับการจำลองการถ่ายเทความร้อนแบบชัดแจ้ง (explicit) time step จะถูกจำกัดโดย:

$$\Delta t \leq \frac{\Delta x^2}{2\alpha}$$

โดยที่ $\alpha = k/(\rho c_p)$ คือ การแพร่ความร้อน (thermal diffusivity)

#### OpenFOAM Implementation

```cpp
// Calculate maximum stable time step for explicit heat transfer
// Based on Fourier number: Fo = alpha*dt/dx^2 <= 0.5
// For stability: dt <= dx^2/(2*alpha)
scalar deltaX = pow(mesh.V()[0], 1.0/3.0);  // Characteristic cell size
scalar alpha = kappa.value()/(rho.value()*cp.value());
scalar maxDeltaT = 0.5*sqr(deltaX)/alpha;    // Stability limit

// Set time step to minimum of current and maximum
runTime.setDeltaT(min(runTime.deltaTValue(), maxDeltaT));
```

**แหล่งที่มา:** 📂 `src/ODE/ODESolvers/` (Time stepping utilities)

**คำอธิบาย:**
- `deltaX`: ขนาดเซลล์ลักษณะ (characteristic cell size)
- `alpha`: การแพร่ความร้อน (thermal diffusivity) [m²/s]
- สมการ stability: $\Delta t \leq \Delta x^2 / (2\alpha)$

**แนวคิดสำคัญ:**
- ข้อจำกัด time step นี้ใช้สำหรับ explicit schemes
- สำหรับ implicit schemes ใช้ time step ที่ใหญ่กว่าได้
- ตัวแปร Courant number ยังสำคัญสำหรับ convection-dominated flows
- ในทางปฏิบัติ ใช้ `maxCo` (maximum Courant number) และ `maxDeltaT` ใน `controlDict`

### 7.2 Under-Relaxation เพื่อความเสถียร

```cpp
// Under-relaxation factors in fvSolution dictionary
// Helps convergence for steady-state problems
relaxationFactors
{
    fields
    {
        p               0.3;    // Pressure (low for stability)
        U               0.7;    // Velocity
        T               0.8;    // Temperature
        h               0.8;    // Enthalpy
    }
    equations
    {
        U               0.8;    // Momentum equation
        T               0.9;    // Energy equation
        h               0.9;    // Enthalpy equation
    }
}
```

**แหล่งที่มา:** 📂 `src/finiteVolume/fvSolution/`

**คำอธิบาย:**
- Under-relaxation ช่วยให้การแก้ปัญหาลู่ันโดยลดการเปลี่ยนแปลงในแต่ละ iteration
- ค่าต่ำกว่า = มากกว่าความเสถียร แต่ช้ากว่าการลู่ัน
- ค่าที่แนะนำขึ้นอยู่กับปัญหาและ scheme

**แนวคิดสำคัญ:**
- สำหรับ coupled problems (เช่น buoyancy-driven flow) ให้ใช้ค่าต่ำกว่า
- สำหรับ transient ปัญหาสามารถใช้ค่าสูงกว่า (หรือ 1.0)
- ใช้ `residuals` control ใน `fvSolution` เพื่อตรวจสอบการลู่ัน

### 7.3 การตั้งค่า Linear Solver

```cpp
// Linear solver settings for temperature equation
// Uses Geometric-Algebraic Multi-Grid (GAMG) for efficiency
T
{
    solver          GAMG;              // Geometric-Algebraic Multi-Grid
    smoother        GaussSeidel;       // Smoother for GAMG
    tolerance       1e-06;             // Absolute tolerance
    relTol          0;                 // Relative tolerance (0 = absolute only)
    nPreSweeps      1;                 // Number of pre-smoothing sweeps
    nPostSweeps     2;                 // Number of post-smoothing sweeps
    nFinestSweeps   2;                 // Sweeps on finest grid level
}
```

**แหล่งที่มา:** 📂 `src/OpenFOAM/matrices/lduMatrix/solvers/`

**คำอธิบาย:**
- `GAMG`: solver ที่มีประสิทธิภาพสำหรับ large-scale problems
- `GaussSeidel`: smoother สำหรับการลดความผิดพลาดในแต่ละระดับ grid
- `tolerance`: ความคลาดเคลื่อนสัมบูรณ์ (absolute tolerance)
- `relTol`: ความคลาดเคลื่อนสัมพัทธ์ (0 = ใช้ absolute tolerance เท่านั้น)

**แนวคิดสำคัญ:**
- สำหรับ small problems ใช้ `PBiCGStab` หรือ `smoothSolver` แทน GAMG
- สำหรับ highly convection-dominated flows ใช้สูงกว่า tolerance
- ใช้ `nCellsInCoarsestLevel` ใน GAMG settings สำหรับปรับปรุงประสิทธิภาพ
- ตั้งค่า solver ใน `system/fvSolution`

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
# Decompose case for parallel processing
# Uses method specified in system/decomposeParDict
decomposePar

# Run in parallel using MPI
# -np: number of processors
mpirun -np 8 buoyantSimpleFoam -parallel

# Reconstruct results from parallel runs
reconstructPar
```

**แหล่งที่มา:** 📂 `applications/utilities/parallelProcessing/decomposePar/`

**คำอธิบาย:**
- `decomposePar`: แบ่ง domain เป็น subdomains สำหรับ parallel processing
- `mpirun`: คำสั่งรัน parallel ด้วย MPI
- `reconstructPar`: รวบรวมผลลัพธ์จาก processors

**แนวคิดสำคัญ:**
- ใช้ `scotch` หรือ `metis` method สำหรับ decomposition ที่มีประสิทธิภาพ
- ตั้งค่า `numberOfSubdomains` ใน `decomposeParDict`
- สำหรับ large cases ใช้ `debug` switch สำหรับ load balancing
- Parallel scaling efficiency ขึ้นอยู่กับ mesh size และ solver

### 9.2 การเพิ่มประสิทธิภาพหน่วยความจำ (Memory Optimization)

- ใช้ object `tmp` สำหรับฟิลด์ชั่วคราว
- เพิ่มประสิทธิภาพการจัดเก็บสำหรับเทนเซอร์สมมาตร (symmetric tensors)
- ลดการถ่ายโอนฟิลด์ระหว่างภูมิภาคให้น้อยที่สุด

---

เอกสารนี้ครอบคลุมทั้งพื้นฐานทางทฤษฎีและรายละเอียดการนำไปใช้จริงสำหรับการวิเคราะห์ปัญหาทางความร้อนด้วย CFD อย่างมีประสิทธิภาพ

---
**หัวข้อถัดไป**: [[การไหลที่ขับเคลื่อนด้วยแรงลอยตัว]]