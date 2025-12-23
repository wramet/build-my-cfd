# สมการปรากฏการณ์ระหว่างเฟส (Interfacial Phenomena Equations)

## ภาพรวม (Overview)

**ปรากฏการณ์ระหว่างเฟส (Interfacial Phenomena)** เป็นกลไกทางฟิสิกส์ที่เกิดขึ้นที่พื้นผิวรอยต่อระหว่างเฟสต่างๆ ในระบบการไหลแบบหลายเฟส ซึ่งมีความสำคัญอย่างยิ่งต่อการทำนายพฤติกรรมของการไหลและการถ่ายเท

> [!INFO] ความสำคัญของปรากฏการณ์ระหว่างเฟส
> ปรากฏการณ์เหล่านี้ควบคุม:
> - การเคลื่อนที่และรูปร่างของฟอง/หยด (bubble/drop dynamics)
> - การถ่ายเทมวลและความร้อนระหว่างเฟส
> - เสถียรภาพของพื้นผิวรอยต่อ (interface stability)
> - พฤติกรรมการเปียก (wetting behavior) และการแพร่กระจาย

---

## 1. ผลของแรงตึงผิว (Surface Tension Effects)

แรงตึงผิว ($\sigma$) สร้างความแตกต่างของความดันข้ามพื้นผิวรอยต่อที่โค้ง และกำหนดพฤติกรรมการเคลื่อนที่ของรอยต่อ

### 1.1 สมการ Young-Laplace

อธิบายความกระโดดของความดัน ($\Delta p$) ข้ามรอยต่อที่มีความโค้ง ($\kappa$):

$$\Delta p = \sigma \kappa \tag{4.1}$$

**ความโค้งเฉลี่ย ($\kappa$):**
$$\kappa = \nabla \cdot \mathbf{n} = \nabla \cdot \left( \frac{\nabla \alpha}{|\nabla \alpha|} \right) \tag{4.2}$$

**กรณีพิเศษ:**
- **ทรงกลม:** $\Delta p = \frac{2\sigma}{R}$
- **ทรงกระบอก:** $\Delta p = \frac{\sigma}{R}$

### 1.2 แบบจำลอง Continuum Surface Force (CSF)

ใน OpenFOAM, แรงตึงผิวจะถูกแปลงเป็นแรงต่อหน่วยปริมาตรเพื่อให้คำนวณร่วมกับสมการโมเมนตัมได้:

$$\mathbf{F}_{st} = \sigma \kappa \nabla \alpha \tag{4.3}$$

โดยที่:
- $\sigma$ = สัมประสิทธิ์แรงตึงผิว (surface tension coefficient) [N/m]
- $\kappa$ = ความโค้งของพื้นผิวรอยต่อ (interface curvature) [1/m]
- $\nabla \alpha$ = เกรเดียนต์ของสัดส่วนปริมาตร (volume fraction gradient)

> [!TIP] การคำนวณความโค้ง
> เทอม `delta` ถูกเพิ่มเข้าไปเพื่อป้องกันการหารด้วยศูนย์ในบริเวณที่มีเกรเดียนต์ต่ำ:
> ```cpp
> volVectorField n = fvc::grad(alpha);
> volVectorField nHat = n/(mag(n) + delta);
> volScalarField kappa = -fvc::div(nHat);
> ```

---

## 2. ผลของ Marangoni (Marangoni Effects)

เกิดจากความไม่สม่ำเสมอของแรงตึงผิวตามแนวพื้นผิวรอยต่อ ($\nabla_s \sigma$) ซึ่งขับเคลื่อนการไหลขนานกับรอยต่อ

### 2.1 สมการความเค้น Marangoni

$$\boldsymbol{\tau}_{Marangoni} = \nabla_s \sigma = \frac{\partial \sigma}{\partial T} \nabla_s T + \frac{\partial \sigma}{\partial C} \nabla_s C \tag{4.4}$$

โดยที่ $\nabla_s = (\mathbf{I} - \mathbf{n}\mathbf{n}) \cdot \nabla$ คือ Surface Gradient Operator

**กลไกทางกายภาพ:**
- **Thermocapillary (Marangoni Effect):** การไหลเนื่องจากความแตกต่างของอุณหภูมิ
- **Diffusocapillary Effect:** การไหลเนื่องจากความเข้มข้นของสารละลาย

### 2.2 จำนวน Marangoni (Ma)

$$\text{Ma} = \frac{|\partial \sigma/\partial T| \Delta T L}{\mu \alpha}$$

ระบุอัตราส่วนระหว่างแรงขับเคลื่อนเทอร์โมคาปิลลารีต่อการกระจายพลังงานหนืด

> [!WARNING] ความสำคัญในการจำลอง
> ปรากฏการณ์ Marangoni มีความสำคัญอย่างยิ่งใน:
> - การเชื่อม (Welding) และการหลอม (Melting)
> - Microfluidics และ Lab-on-a-chip
> - การเคลือบผิว (Coating processes)

---

## 3. มุมสัมผัสและการเปียก (Contact Angle and Wetting)

กำหนดพฤติกรรมที่รอยต่อระหว่างสามเฟส (Solid-Liquid-Gas) มาบรรจบกัน

### 3.1 สมการ Young (สมดุลสถิต)

$$\cos \theta_e = \frac{\sigma_{sg} - \sigma_{sl}}{\sigma_{lg}} \tag{4.5}$$

**คำนิยาม:**
- $\theta_e$ = มุมสัมผัสสมดุล (equilibrium contact angle)
- $\sigma_{sg}$ = แรงตึงผิวระหว่างของแข็ง-ก๊าซ
- $\sigma_{sl}$ = แรงตึงผิวระหว่างของแข็ง-ของเหลว
- $\sigma_{lg}$ = แรงตึงผิวระหว่างของเหลว-ก๊าซ

### 3.2 มุมสัมผัสดินามิกส์ (Dynamic Contact Angle)

เมื่อเส้นสัมผัสเคลื่อนที่ด้วยความเร็ว $U$, มุมสัมผัสจะเปลี่ยนไปตามกฎ Hoffman-Voinov-Tanner:

$$\theta_d^3 = \theta_e^3 + 9 \text{Ca} \ln\left(\frac{L}{L_{micro}}\right) \tag{4.6}$$

โดยที่ $\text{Ca} = \mu U / \sigma$ คือ Capillary Number

### 3.3 การนำไปใช้ใน OpenFOAM

#### การตั้งค่ามุมสัมผัสใน `0/alpha`

```cpp
wall
{
    type            constantAlphaContactAngle;
    theta0          60; // มุมสัมผัสสมดุล (องศา)
    limit           gradient;
    value           uniform 0;
}
```

#### การคำนวณความโค้งใน Solver

```cpp
// Interface normal
volVectorField n = fvc::grad(alpha);
volVectorField nHat = n/(mag(n) + deltaN);

// Curvature
volScalarField kappa = -fvc::div(nHat);

// Surface tension force
volVectorField Fst = sigma * kappa * nHat;
```

> [!TIP] เงื่อนไขขอบเขต
> - สำหรับ **hydrophilic surface** ($\theta < 90°$): ของเหลวกระจายตัวบนผิว
> - สำหรับ **hydrophobic surface** ($\theta > 90°$): ของเหลวย่อขึ้นเป็นหยด

---

## 4. การขนส่งพื้นที่ผิวระหว่างเฟส (Interfacial Area Transport)

พื้นที่ผิวระหว่างเฟสต่อหน่วยหนึ่งปริมาตร $A_{int}$ เป็นพารามิเตอร์สำคัญในการไหลแบบหลายเฟส

### 4.1 สมการการขนส่งพื้นที่ผิว

$$\frac{\partial (\rho A_{int})}{\partial t} + \nabla \cdot (\rho \mathbf{u} A_{int}) = \frac{\partial}{\partial x_i} \left( D_{A_{int}} \frac{\partial A_{int}}{\partial x_i} \right) + S_{A_{int}} \tag{4.7}$$

โดยที่ $S_{A_{int}}$ รวมเทอมการแตกตัว (breakup) และการรวมตัว (coalescence) ของฟอง/หยด

### 4.2 กลไกการแตกตัวและรวมตัว

**การแตกตัวของฟอง (Bubble Breakup):**
$$S_{breakup} = -k_{br} \alpha_d$$

**การรวมตัวของฟอง (Bubble Coalescence):**
$$S_{coal} = k_{coal} \alpha_d^2$$

โดยที่:
- $k_{br}$ = อัตราการแตกตัว (breakup rate)
- $k_{coal}$ = อัตราการรวมตัว (coalescence rate)
- $\alpha_d$ = สัดส่วนปริมาตรของเฟสกระจาย (dispersed phase fraction)

---

## 5. แรงระหว่างเฟส (Interfacial Forces)

### 5.1 ภาพรวมของแรงระหว่างเฟส

แรงทั้งหมดที่กระทำที่พื้นผิวรอยต่อระหว่างเฟส $i$ และ $j$:

$$\mathbf{F}_{int} = \mathbf{F}_{drag} + \mathbf{F}_{lift} + \mathbf{F}_{vm} + \mathbf{F}_{wall} + \mathbf{F}_{turb}$$

### 5.2 แรงลาก (Drag Force)

แรงต้านทานการเคลื่อนที่สัมพัทธ์ระหว่างเฟส:

$$\mathbf{F}_{drag} = \frac{3}{4} C_D \frac{\alpha_c \alpha_d \rho_c}{d_p} |\mathbf{u}_d - \mathbf{u}_c| (\mathbf{u}_c - \mathbf{u}_d) \tag{4.8}$$

**สัมประสิทธิ์แรงลาก ($C_D$):**

| ระบอบการไหล | เงื่อนไข | สัมประสิทธิ์ |
|--------------|-----------|------------------|
| **Stokes** | Re < 1 | $C_D = \frac{24}{Re}$ |
| **Intermediate** | 1 < Re < 1000 | $C_D = \frac{24}{Re}(1 + 0.15 Re^{0.687})$ |
| **Newton** | Re > 1000 | $C_D = 0.44$ |

### 5.3 แรงยก (Lift Force)

แรงในแนวข้างกระทำต่ออนุภาค/ฟองอากาศ เนื่องจากการไล่ระดับความเร็วในเฟสต่อเนื่อง:

$$\mathbf{F}_{lift} = C_L \alpha_d \rho_c (\mathbf{u}_d - \mathbf{u}_c) \times (\nabla \times \mathbf{u}_c) \tag{4.9}$$

โดยที่ $C_L$ คือสัมประสิทธิ์แรงยก (lift coefficient)

### 5.4 แรงมวลเสมือน (Virtual Mass Force)

แรงเพิ่มเติมที่จำเป็นในการเร่งของไหลโดยรอบเมื่ออนุภาคเร่ง:

$$\mathbf{F}_{vm} = C_{vm} \alpha_d \rho_c \left( \frac{D\mathbf{u}_c}{Dt} - \frac{D\mathbf{u}_d}{Dt} \right) \tag{4.10}$$

โดยที่ $C_{vm} = 0.5$ สำหรับอนุภาคทรงกลม

### 5.5 การนำไปใช้ใน OpenFOAM

```cpp
// Interfacial momentum transfer in multiphaseEulerFoam

// Drag force
volScalarField Kd = dragModel_->K();

// Lift force
volVectorField Flift = liftModel_->F();

// Virtual mass
volScalarField Cvm = virtualMassModel_->Cvm();

// Total interfacial momentum transfer
return Kd * (phase2_.U() - phase1_.U())
     + Flift
     + Cvm * rho1_ * (DDt(phase2_.U()) - DDt(phase1_.U()));
```

---

## 6. การถ่ายเทมวลและความร้อนระหว่างเฟส

### 6.1 การถ่ายเทมวล

อัตราการถ่ายเทมวลระหว่างเฟส $l$ และ $k$:

$$\dot{m}_{lk} = h_m A_{lk} (\rho_{k,sat} - \rho_k) \tag{4.11}$$

**โมเดล Hertz-Knudsen:**
$$\dot{m}_{lv} = \frac{2}{2-\sigma} \sqrt{\frac{M}{2\pi R T}} \cdot \frac{p_{sat}(T) - p_v}{\sqrt{R T}}$$

### 6.2 การถ่ายเทความร้อน

$$\dot{q}_{lk} = h_{heat} A_{lk} (T_l - T_k) \tag{4.12}$$

**สหสัมพันธ์ Nusselt:**
$$Nu = \frac{h_{heat} d_p}{k} = 2 + 0.6 Re^{1/2} Pr^{1/3}$$

---

## 7. เงื่อนไขกระโดดที่พื้นผิวรอยต่อ (Interface Jump Conditions)

ที่พื้นผิวรอยต่อระหว่างเฟส $i$ และ $j$:

### 7.1 การดุลมวล

$$\dot{m}_{ij}(\mathbf{u}_j - \mathbf{u}_i) \cdot \mathbf{n}_{ij} = 0 \tag{4.13}$$

### 7.2 การดุลโมเมนตัม

$$\dot{m}_{ij}(\mathbf{u}_j - \mathbf{u}_i) + \langle p_i - p_j \rangle \mathbf{n}_{ij} + \langle \boldsymbol{\tau}_i - \boldsymbol{\tau}_j \rangle \cdot \mathbf{n}_{ij} = \sigma \kappa \mathbf{n}_{ij} \tag{4.14}$$

### 7.3 การดุลพลังงาน

$$\dot{m}_{ij}(h_j - h_i) + \langle k_i \nabla T_i - k_j \nabla T_j \rangle \cdot \mathbf{n}_{ij} = 0 \tag{4.15}$$

---

## 8. ตัวเลขแบบไร้มิติสำคัญ (Key Dimensionless Numbers)

| ชื่อ | สมการ | ความหมาย |
|------|---------|------------|
| **เลขเวเบอร์ (Weber Number)** | $We = \frac{\rho U^2 L}{\sigma}$ | อัตราส่วนระหว่างแรงเฉื่อยและแรงตึงผิว |
| **เลขแคปิลลารี (Capillary Number)** | $Ca = \frac{\mu U}{\sigma}$ | อัตราส่วนระหว่างแรงหนืดและแรงตึงผิว |
| **เลขอีออตวอส (Eötvös Number)** | $Eo = \frac{(\rho_l - \rho_g) g d^2}{\sigma}$ | อัตราส่วนระหว่างแรงโน้มถ่วงและแรงตึงผิว |
| **เลขมอร์ตัน (Morton Number)** | $Mo = \frac{g \mu_l^4 (\rho_l - \rho_g)}{\rho_l^2 \sigma^3}$ | ค่าคงที่ของของไหลและอนุภาค |
| **จำนวน Marangoni (Marangoni Number)** | $Ma = \frac{|\partial \sigma/\partial T| \Delta T L}{\mu \alpha}$ | อัตราส่วนระหว่างแรง Marangoni และการกระจายพลังงานหนืด |

---

## 9. แอปพลิเคชันและกรณีศึกษา

### 9.1 Microfluidics

การใช้ประโยชน์จากปรากฏการณ์ Marangoni ใน:
- การควบคุมหยด (droplet manipulation)
- Lab-on-a-chip devices
- การผสมในมิติเล็ก (micro-mixing)

### 9.2 การเชื่อมและการหลอม (Welding and Melting)

ความสำคัญของแรงตึงผิวและ Marangoni convection:
- การกำหนดรูปร่างของรอยเชื่อม (weld pool shape)
- การแพร่กระจายของความร้อน
- คุณภาพของการเชื่อม

### 9.3 การไหลในช่องเล็ก (Microchannel Flow)

- การเคลื่อนที่ของฟองในไมโครแชนแนล
- ผลกระทบของมุมสัมผัส
- การเกิด slugs และ plugs

---

## 💻 การนำไปใช้ใน OpenFOAM

### การตั้งค่า Surface Tension ใน `constant/transportProperties`

```cpp
// Surface tension coefficient
sigma   sigma [0 2 -2 0 0 0 0] 0.07;

// Contact angle
theta0  theta0 [0 0 0 0 0 0 0] 60;

// Interface smoothing parameters
deltaN  deltaN [0 0 1 0 0 0 0] 1e-6;
```

### การคำนวณใน Solver

```cpp
// Interface properties
volScalarField sigma = fluid.sigma();
volScalarField kappa = fluid.kappa();

// Surface tension force
volVectorField Fst = sigma * kappa * fvc::grad(alpha);

// Add to momentum equation
UEqn += Fst;
```

### เงื่อนไขขอบเขตสำหรับ Contact Angle

```cpp
wall
{
    type            dynamicAlphaContactAngle;
    theta0          60;        // Static contact angle
    uTheta          0.5;       // Dynamic contact angle parameter
    limit           gradient;
    value           uniform 0;
}
```

---

## 📚 บทสรุป (Summary)

การทำความเข้าใจสมการปรากฏการณ์ระหว่างเฟสมีความสำคัญอย่างยิ่งต่อ:

1. **การจำลองการไหลแบบหลายเฟส** ให้แม่นยำ
2. **การทำนายพฤติกรรมของฟองและหยด** (bubble and drop dynamics)
3. **การออกแบบระบบ Microfluidics** และอุปกรณ์การไหล
4. **การปรับปรุงกระบวนการทางอุตสาหกรรม** (process optimization)

---

## 🔗 อ้างอิงเพิ่มเติม

- [[01_Table_of_Contents|สารบัญ]]
- [[02_Foundation_and_Mathematical_Framework|พื้นฐานและกรอบการทำงาน]]
- [[03_Mass_Conservation_Equations|สมการอนุรักษ์มวล]]
- [[04_Momentum_Conservation_Equations|สมการอนุรักษ์โมเมนตัม]]
- [[05_Energy_Conservation_Equations|สมการอนุรักษ์พลังงาน]]
