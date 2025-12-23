# การอนุรักษ์พลังงานในระบบหลายเฟส (Energy Conservation Equations)

## 📐 สมการพลังงานเฉพาะเฟส (Phase-Specific Energy Equation)

> [!INFO] ภาพรวม
> ในระบบหลายเฟส แต่ละเฟส $k$ มีการอนุรักษ์พลังงานที่รวมถึงการพาความร้อน การนำความร้อน งานจากความดัน และการแลกเปลี่ยนพลังงานที่รอยต่อ สมการเหล่านี้เป็นรากฐานสำคัญในการจำลองปรากฏการณ์การถ่ายเทความร้อน การเปลี่ยนเฟส และปฏิกิริยาเคมีในระบบหลายเฟส

### สมการในรูปของเอนทัลปีจำเพาะ ($h_k$)

สำหรับเฟส $k$ ในระบบหลายเฟส:

$$\frac{\partial}{\partial t}(\alpha_k \rho_k h_k) + \nabla \cdot (\alpha_k \rho_k \mathbf{u}_k h_k) = \alpha_k \frac{\partial p}{\partial t} + \nabla \cdot (\alpha_k \kappa_k \nabla T_k) + \Phi_k + \dot{q}_k + \dot{m}_k h_{k,int} + \mathbf{M}_k \cdot \mathbf{u}_k \tag{3.1}$$

**นิยามตัวแปร**:

| สัญลักษณ์ | ความหมาย | หน่วย |
|----------|-----------|--------|
| $\alpha_k$ | สัดส่วนปริมาตรของเฟส $k$ | ไม่มีหน่วย |
| $\rho_k$ | ความหนาแน่นของเฟส $k$ | $\text{kg/m}^3$ |
| $h_k$ | เอนทัลปีจำเพาะของเฟส $k$ | $\text{J/kg}$ |
| $\mathbf{u}_k$ | ความเร็วของเฟส $k$ | $\text{m/s}$ |
| $p$ | ความดันร่วม (shared pressure) | $\text{Pa}$ |
| $\kappa_k$ | สภาพนำความร้อนของเฟส $k$ | $\text{W/(m·K)}$ |
| $T_k$ | อุณหภูมิของเฟส $k$ | $\text{K}$ |
| $\Phi_k$ | การกระจายความหนืด (Viscous Dissipation) | $\text{W/m}^3$ |
| $\dot{q}_k$ | อัตราการถ่ายเทความร้อนระหว่างเฟส | $\text{W/m}^3$ |
| $\dot{m}_k$ | อัตราการถ่ายเทมวล | $\text{kg/(m}^3\cdot\text{s)}$ |
| $h_{k,int}$ | เอนทัลปีที่พื้นผิวรอยต่อ | $\text{J/kg}$ |
| $\mathbf{M}_k$ | แรงที่รอยต่อ (Interfacial Force) | $\text{N/m}^3$ |

---

## 🔍 การวิเคราะห์แต่ละเทอมในสมการ

### 1. พจน์ชั่วขณะ (Temporal Term)

$$\frac{\partial}{\partial t}(\alpha_k \rho_k h_k)$$

แสดงถึงการสะสมของเอนทัลปีตามเวลา คำนึงถึงการมีอยู่ของเฟสผ่านสัดส่วนปริมาตร $\alpha_k$

### 2. พจน์การพา (Convective Term)

$$\nabla \cdot (\alpha_k \rho_k \mathbf{u}_k h_k)$$

การขนส่งเอนทัลปีโดยการเคลื่อนที่แบบกลุ่มของเฟส $k$ รวมสัดส่วนเฟสสำหรับการถ่วงน้ำหนักที่ถูกต้อง

### 3. งานจากความดัน (Pressure Work)

$$\alpha_k \frac{\partial p}{\partial t}$$

แสดงถึงงานที่ทำโดยการเปลี่ยนแปลงความดันตามเวลา สำคัญมากสำหรับระบบที่อัดตัวได้ (Compressible flows)

> [!TIP] หมายเหตุ
> สำหรับระบบที่อัดตัวไม่ได้ (incompressible flows) พจน์นี้มักจะถูกละเลย

### 4. การนำความร้อน (Heat Conduction)

$$\nabla \cdot (\alpha_k \kappa_k \nabla T_k)$$

การนำความร้อนภายในเฟสตามกฎของฟูเรียร์ (Fourier's Law) ซึ่งปรับสเกลตามการมีอยู่ของเฟส

### 5. การกระจายความหนืด (Viscous Dissipation)

$$\Phi_k = \boldsymbol{\tau}_k : \nabla \mathbf{u}_k$$

การแปลงพลังงานกลเป็นความร้อนผ่านแรงเสียดทานหนืดภายในเฟส

$$\boldsymbol{\tau}_k = \mu_k \left[ \nabla \mathbf{u}_k + (\nabla \mathbf{u}_k)^T \right] - \frac{2}{3} \mu_k (\nabla \cdot \mathbf{u}_k) \mathbf{I}$$

### 6. การถ่ายเทความร้อนระหว่างเฟส ($\dot{q}_k$)

$$\dot{q}_{kl} = h_{kl} A_{kl} (T_l - T_k)$$

โดยที่:
- $h_{kl}$ = สัมประสิทธิ์การถ่ายเทความร้อน (Heat transfer coefficient)
- $A_{kl}$ = ความหนาแน่นพื้นที่รอยต่อ (Interfacial area density)

> [!WARNING] ข้อควรระวัง
> ค่าสัมประสิทธิ์การถ่ายเทความร้อน $h_{kl}$ มักพึ่งพากับเลขเรย์โนลด์ส (Reynolds number) และเลขพรันด์ทล์ (Prandtl number)

### 7. การถ่ายเทมวลและเอนทัลปีรอยต่อ

$$\dot{m}_k h_{k,int}$$

พจน์นี้สำคัญมากสำหรับระบบที่มีการเปลี่ยนเฟส (phase change) เช่น การระเหยและการควบแน่น

### 8. งานจากแรงระหว่างเฟส

$$\mathbf{M}_k \cdot \mathbf{u}_k$$

งานที่เกิดจากแรงระหว่างเฟส (drag, lift, virtual mass, etc.)

---

## 🌡️ อุณหพลศาสตร์ของการเปลี่ยนเฟส (Phase Change Thermodynamics)

ระหว่างการเปลี่ยนเฟส (เช่น การระเหยหรือควบแน่น) สมดุลพลังงานต้องพิจารณาความร้อนแฝง (Latent Heat):

### สมการสมดุลพลังงานที่รอยต่อ

$$\dot{m}_{kl} L + \dot{q}_{kl} = 0 \tag{3.2}$$

โดยที่:
- $L = h_{vapor}^{sat} - h_{liquid}^{sat}$ = ความร้อนแฝงของการกลายเป็นไอ (Latent heat of vaporization)
- $\dot{m}_{kl}$ = อัตราการถ่ายเทมวลจากเฟส $k$ ไปยังเฟส $l$
- $\dot{q}_{kl}$ = อัตราการถ่ายเทความร้อนจากเฟส $k$ ไปยังเฟส $l$

### ผลของ Gibbs-Thomson

ความโค้งของพื้นผิวรอยต่อส่งผลต่ออุณหภูมิสมดุล:

$$T_{interface} = T_{sat} \left(1 - \frac{2\sigma v_l}{h_{lg}^{sat} r}\right)$$

โดยที่:
- $\sigma$ = สัมประสิทธิ์แรงตึงผิว
- $v_l$ = ปริมาตรจำเพาะของเฟสของเหลว
- $r$ = รัศมีความโค้งของพื้นผิว
- $h_{lg}^{sat}$ = ความร้อนแฝงที่ภาวะอิ่มตัว

> [!INFO] นัยสำคัญ
> ผล Gibbs-Thomson สำคัญมากสำหรับการเกิดฟอง (nucleation) และการเติบโตของผลึก (crystal growth)

---

## 💻 การนำไปใช้ใน OpenFOAM (C++ Implementation)

### การสร้างสมการพลังงานใน Solver

ใน Solver เช่น `reactingTwoPhaseEulerFoam`, `multiphaseEulerFoam`, สมการพลังงานถูกสร้างดังนี้:

```cpp
// Energy equation construction for phase k
fvScalarMatrix hEqn
(
    fvm::ddt(alpha, rho, h)
  + fvm::div(alphaRhoPhi, h)
 ==
    alpha*rho*(dpdt)                  // Pressure work
  + fvc::div(alpha*kappa*grad(T))     // Conduction
  + viscousDissipation                 // Viscous dissipation
  + interfacialHeatTransfer            // Heat transfer between phases
  + massTransfer*InterfaceEnthalpy     // Latent heat / phase change
  + interfacialMomentumTransfer & U    // Interfacial work
);
```

### การตั้งค่าเทอร์โมฟิสิกส์

OpenFOAM ต้องการไฟล์ `constant/thermophysicalProperties.phaseName` เพื่อกำหนดโมเดลพลังงาน

#### ประเภทของโมเดลเทอร์โมฟิสิกส์

| โมเดล | คำอธิบาย | การใช้งาน |
|--------|-----------|-----------|
| **hConstThermo** | เอนทัลปีคงที่ | ระบบที่อุณหภูมิไม่แตกต่างมาก |
| **janafThermo** | เอนทัลปีแปรผันตามอุณหภูมิ (JANAF tables) | แก๊สที่ความดันสูง/อุณหภูมิสูง |
| **hPolynomialThermo** | เอนทัลปีเป็นพหุนามของอุณหภูมิ | ของไหลทั่วไป |
| **icoPolynomial** | แบบจำลองพหุนามสำหรับของเหลว | ของเหลวที่ไม่อัดตัวได้ |

### ตัวอย่างการตั้งค่าในไฟล์ thermophysicalProperties

```cpp
// Example for liquid phase
thermoType
{
    type            heRhoThermo;
    mixture         multiComponentMixture;
    transport       const;
    thermo          hPolynomial;
    energy          sensibleEnthalpy;
    equationOfState perfectGas;  // or icoPolynomial for liquids
    specie          specie;
}

mixture
{
    specie
    {
        nMoles          1;
        molWeight       18.015;  // Water
    }

    thermodynamics
    {
        Hf              0;
        Cp              4181;    // J/kg.K for water
        Sf              0;
    }

    transport
    {
        mu              0.001;   // Pa.s
        Pr              7.0;     // Prandtl number
        kappa           0.6;     // W/m.K
    }
}
```

### การคำนวณคุณสมบัติของส่วนผสม

```cpp
// Mixture properties calculation
template<class ThermoType>
inline const typename ThermoType::thermoType&
multiphaseMixture<ThermoType>::cellThermoMixture
(
    const label celli
) const
{
    return mixtures_[celli].thermo();
}

// Effective thermal conductivity
k_eff = sum_k(alpha_k * k_k);
```

---

## 📊 ตารางสรุปกลไกการแลกเปลี่ยนพลังงาน

| กลไก | สมการปิด (Closure) | ความสำคัญ | การประยุกต์ใช้ |
|-----|-------------------|-----------|----------------|
| **Interphase Heat** | Nusselt Correlations (Ranz-Marshall) | สูง (ระบบที่มีความต่างอุณหภูมิ) | Heat exchangers, Boiling |
| **Latent Heat** | Clausius-Clapeyron, Hertz-Knudsen | สูงมาก (Boiling, Condensation) | Phase change phenomena |
| **Viscous Work** | Viscous Dissipation Model | ต่ำ (ยกเว้น High-speed/High-viscosity) | Polymer processing |
| **Pressure Work** | Isenthalpic/Isothermal assumptions | ปานกลาง (Compressible flows) | Gas dynamics |
| **Marangoni Effect** | Thermocapillary convection | ปานกลาง (Free surface flows) | Welding, Crystal growth |

### สหสัมพันธ์การถ่ายเทความร้อนระหว่างเฟส

**โมเดล Ranz-Marshall** (สำหรับฟอง/หยด):

$$Nu = 2 + 0.6 Re^{1/2} Pr^{1/3}$$

$$h_{kl} = \frac{Nu \cdot k_l}{d_p}$$

โดยที่:
- $Nu$ = เลขนุสเซลต์ (Nusselt number)
- $Re$ = เลขเรย์โนลด์ส (Reynolds number)
- $Pr$ = เลขพรันด์ทล์ (Prandtl number)
- $d_p$ = เส้นผ่านศูนย์กลางของฟอง/หยด

> [!TIP] เคล็ดลับ
> การเลือกสหสัมพันธ์การถ่ายเทความร้อนที่ถูกต้อง ($Nu$ correlation) มีผลอย่างยิ่งต่อความแม่นยำในการทำนายอุณหภูมิของแต่ละเฟสในระบบ

---

## 🔄 สมการพลังงานของส่วนผสม (Mixture Energy Equation)

### การอนุรักษ์พลังงานของส่วนผสม

สมการพลังงานของส่วนผสมให้สมดุลพลังงานโดยรวม:

$$\frac{\partial (\rho h)}{\partial t} + \nabla \cdot (\rho \mathbf{u} h) = \frac{\partial p}{\partial t} + \nabla \cdot (k_{eff} \nabla T) + \Phi \tag{3.3}$$

โดยที่:
- $\rho = \sum_k \alpha_k \rho_k$ = ความหนาแน่นของส่วนผสม
- $\mathbf{u} = \frac{1}{\rho} \sum_k \alpha_k \rho_k \mathbf{u}_k$ = ความเร็วของส่วนผสม
- $k_{eff} = \sum_k \alpha_k k_k$ = สภาพนำความร้อนประสิทธิผล
- $\Phi$ = การกระจายตัวเนื่องจากความหนืดรวม

### ความสัมพันธ์อุณหพลศาสตร์

สำหรับการคำนวณคุณสมบัติทางอุณหพลศาสตร์:

**ความหนาแน่นของส่วนผสม**:
$$\rho_{mix} = \sum_k \alpha_k \rho_k$$

**ความร้อนจำเพาะของส่วนผสม**:
$$c_{p,mix} = \frac{1}{\rho_{mix}} \sum_k \alpha_k \rho_k c_{p,k}$$

**สภาพนำความร้อนของส่วนผสม**:
$$k_{mix} = \sum_k \alpha_k k_k$$

---

## 🌊 ผลของ Marangoni ต่อการถ่ายเทความร้อน (Marangoni Effects on Heat Transfer)

### แนวคิดพื้นฐาน

**ผลของ Marangoni** เกิดจากการเปลี่ยนแปลงของแรงตึงผิวตามตำแหน่งอันเนื่องมาจากความแตกต่างของอุณหภูมิ ซึ่งขับเคลื่อนการไหลที่พื้นผิวรอยต่อ

### ความเค้น Marangoni

$$\boldsymbol{\tau}_{Marangoni} = \nabla_s \sigma = \frac{\partial \sigma}{\partial T} \nabla_s T$$

โดยที่:
- $\nabla_s$ = ตัวดำเนินการเกรเดียนต์บนพื้นผิว
- $\frac{\partial \sigma}{\partial T}$ = อนุพันธ์ของแรงตึงผิวเทียบกับอุณหภูมิ

### จำนวน Marangoni

$$\text{Ma} = \frac{|\partial \sigma/\partial T| \Delta T L}{\mu \alpha}$$

โดยที่:
- $\Delta T$ = ความแตกต่างของอุณหภูมิ
- $L$ = มาตราส่วนความยาว
- $\mu$ = ความหนืดพลวัต
- $\alpha$ = การแพร่ความร้อน

### การนำไปใช้ใน OpenFOAM

```cpp
// Marangoni force calculation
volVectorField gradT = fvc::grad(T);
volVectorField n = fvc::grad(alpha)/mag(fvc::grad(alpha));

// Surface tension gradient
volVectorField gradSigma = dSigma_dT * gradT;

// Tangential component (Marangoni stress)
volVectorField marangoniStress = gradSigma - n*(n & gradSigma);

// Volume force for CSF
volVectorField Fmarangoni = marangoniStress * mag(fvc::grad(alpha));
```

> [!WARNING] ความสำคัญ
> ผลของ Marangoni มักมีอิทธิพลมากในระบบที่มีความแตกต่างของอุณหภูมิสูง เช่น การเชื่อม (welding) และการเติบโตของผลึก (crystal growth)

---

## 📐 การวิเคราะห์แบบไร้มิติ (Dimensionless Analysis)

### เลขมิติสำคัญสำหรับการถ่ายเทความร้อน

| เลข | สมการ | ความหมายทางกายภาพ |
|-----|----------|---------------------|
| **Prandtl** | $Pr = \frac{\mu c_p}{k}$ | อัตราส่วนของการแพร่ตัวของโมเมนตัมต่อความร้อน |
| **Nusselt** | $Nu = \frac{h L}{k}$ | อัตราส่วนของการถ่ายเทความร้อนแบบนูมำนักต่อการนำ |
| **Peclet** | $Pe = Re \cdot Pr = \frac{u L}{\alpha}$ | อัตราส่วนของการพาความร้อนต่อการนำ |
| **Stanton** | $St = \frac{Nu}{Re \cdot Pr}$ | ประสิทธิภาพการถ่ายเทความร้อน |
| **Eckert** | $Ec = \frac{u^2}{c_p \Delta T}$ | อัตราส่วนของพลังงานจลน์ต่อเอนทัลปี |

### แผนที่ระบอบการไหลความร้อน (Thermal Flow Regime Map)

| ระบอบ | เงื่อนไข | ลักษณะ |
|--------|----------|--------|
| **Conduction dominant** | $Pe \ll 1$ | การนำความร้อนมีอิทธิพลเหนือกว่า |
| **Intermediate** | $Pe \sim 1$ | การพาและการนำสำคัญเท่ากัน |
| **Convection dominant** | $Pe \gg 1$ | การพาความร้อนมีอิทธิพลเหนือกว่า |

---

## 🔧 การประยุกต์ใช้ในกรณีศึกษา (Application Case Studies)

### 1. การเดือด (Boiling)

สมการสำหรับการถ่ายเทมวลในระบบการเดือด:

$$\dot{m}_{lv} = \frac{q''}{h_{lv}}$$

โดยที่ $q''$ = ฟลักซ์ความร้อนที่พื้นผิว

### 2. การควบแน่น (Condensation)

**แบบจำลอง Hertz-Knudsen**:

$$\dot{m}_{lv} = \frac{C_{evap}}{\sqrt{2\pi}} \left( \frac{p_{sat} - p_l}{\sqrt{R_g T_l}} \right) \alpha_l \alpha_v$$

### 3. การแลกเปลี่ยนความร้อนในเครื่องแลกเปลี่ยนความร้อน (Heat Exchangers)

$$Q = U A \Delta T_{lm}$$

โดยที่:
- $U$ = สัมประสิทธิ์การถ่ายเทความร้อนโดยรวม
- $\Delta T_{lm}$ = ความแตกต่างของอุณหภูมิเฉลี่ยแบบลอการิทึม (Log-mean temperature difference)

### 4. การเชื่อม (Welding)

การถ่ายเทความร้อนร่วมกับผลของ Marangoni:

$$\mathbf{q} = -k \nabla T + \mathbf{u} \rho h + \mathbf{F}_{Marangoni} \cdot \mathbf{u}$$

---

## 📚 สรุปและข้อเสนอแนะ (Summary and Recommendations)

### หลักการสำคัญ

1. **การเลือกโมเดลเทอร์โมฟิสิกส์ที่เหมาะสม** มีความสำคัญอย่างยิ่งต่อความแม่นยำของการจำลอง
2. **การปิดสมการ (Closure Relations)** สำหรับการถ่ายเทความร้อนระหว่างเฟสต้องได้รับความสำคัญเป็นพิเศษ
3. **ผลของการเปลี่ยนเฟส** (Phase Change Effects) ต้องถูกจำลองอย่างถูกต้องโดยใช้ความร้อนแฝง
4. **ผลของ Marangoni** สำคัญในระบบที่มีความแตกต่างของอุณหภูมิสูง

### แนวทางการนำไปใช้ใน OpenFOAM

```cpp
// General workflow for energy equation in multiphase
1. กำหนดโมเดลเทอร์โมฟิสิกส์สำหรับแต่ละเฟส
2. สร้างสมการพลังงานสำหรับแต่ละเฟส
3. คำนวณการแลกเปลี่ยนความร้อนระหว่างเฟส
4. จัดการผลของการเปลี่ยนเฟส (ถ้ามี)
5. แก้สมการด้วยรูปแบบเชิงตัวเลขที่เหมาะสม
6. ตรวจสอบการอนุรักษ์พลังงาน
```

### ข้อควรพิจารณาด้านเสถียรภาพ

| ประเด็น | เงื่อนไข | วิธีการจัดการ |
|----------|-----------|----------------|
| **CFL condition** | $\Delta t \leq \frac{\Delta x}{|u|_{max}}$ | ใช้ time stepping ที่เหมาะสม |
| **Boundedness** | $0 \leq h_k \leq h_{max}$ | ใช้รูปแบบที่รักษาค่าบวก |
| **Conservation** | $\sum E_{in} = \sum E_{out}$ | ตรวจสอบ balance ของพลังงาน |
| **Convergence** | $R_h < 10^{-6}$ | ใช้ under-relaxation ที่เหมาะสม |

---

## 🔗 การอ้างอิงเชิงลึก (Cross-References)

สมการการอนุรักษ์พลังงานเชื่อมโยงกับ:

- [[02_Mass_Conservation#การวิเคราะห์แต่ละเทอมในสมการ]]: ทบทวนแนวคิดพื้นฐานเรื่องการอนุรักษ์
- [[02_Foundation_and_Mathematical_Framework]]: ทฤษฎีบทการหาค่าเฉลี่ยของเฟส
- [[06_Interfacial_Phenomena_Equations]]: ผลของแรงตึงผิวและ Marangoni
- [[08_Closure_Relations]]: ความสัมพันธ์ปิดสำหรับคุณสมบัติทางอุณหพลศาสตร์
- [[10_Special_Cases]]: การประยุกต์ใช้ในกรณีพิเศษ
