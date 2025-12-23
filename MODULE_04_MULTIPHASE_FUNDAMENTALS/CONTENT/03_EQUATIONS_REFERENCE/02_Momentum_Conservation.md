# การอนุรักษ์โมเมนตัมในระบบหลายเฟส (Momentum Conservation Equations)

## ทบทวนแนวคิดพื้นฐาน

จาก [[01_Mass_Conservation#อนุพันธ์เชิงปริภูมิ|สมการอนุรักษ์มวล]], เราได้เห็นแล้วว่าสำหรับเฟส $k$ ในระบบหลายเฟส สมการความต่อเนื่องมีรูปแบบ:

$$\frac{\partial}{\partial t}(\alpha_k \rho_k) + \nabla \cdot (\alpha_k \rho_k \mathbf{u}_k) = \dot{m}_k$$

สมการโมเมนตัมจะขยายแนวคิดนี้ไปยังการอนุรักษ์โมเมนตัม โดยมีเงื่อนไขขอบเขตและแรงระหว่างเฟสที่ซับซ้อนกว่ามาก

---

## 📐 สมการโมเมนตัมเฉพาะเฟส (Phase-Specific Momentum Equation)

### หลักการพื้นฐาน
**การอนุรักษ์โมเมนตัมสำหรับแต่ละเฟส** โดยคำนึงถึงแรงระหว่างเฟสและคุณสมบัติเฉพาะของแต่ละเฟส ในกรอบงานแบบ Eulerian-Eulerian แต่ละเฟส $k$ จะถูกควบคุมด้วยสมการโมเมนตัมของตนเอง

### สมการทั่วไป
สำหรับเฟส $k$ ในระบบหลายเฟส:

$$\frac{\partial}{\partial t}(\alpha_k \rho_k \mathbf{u}_k) + \nabla \cdot (\alpha_k \rho_k \mathbf{u}_k \mathbf{u}_k) = -\alpha_k \nabla p + \nabla \cdot (\alpha_k \boldsymbol{\tau}_k) + \alpha_k \rho_k \mathbf{g} + \mathbf{M}_k \tag{2.1}$$

**นิยามตัวแปร:**
- $\alpha_k$ = สัดส่วนปริมาตรของเฟส $k$ (volume fraction)
- $\rho_k$ = ความหนาแน่นของเฟส $k$ ($\text{kg/m}^3$)
- $\mathbf{u}_k$ = เวกเตอร์ความเร็วของเฟส $k$ ($\text{m/s}$)
- $p$ = ความดันร่วมระหว่างเฟส ($\text{Pa}$) - ในแบบจำลองส่วนใหญ่
- $\boldsymbol{\tau}_k$ = เทนเซอร์ความเค้น (stress tensor) ของเฟส $k$
- $\mathbf{g}$ = เวกเตอร์ความเร่งโน้มถ่วง ($\text{m/s}^2$)
- $\mathbf{M}_k$ = การถ่ายเทโมเมนตัมระหว่างเฟส (interfacial momentum transfer) ($\text{N/m}^3$)

> [!INFO] **ข้อสังเกตสำคัญเรื่องความดัน**
> สมการ (2.1) ใช้ความดันร่วม $p$ สำหรับทุกเฟส ซึ่งเป็นการสมมติที่ใช้กันทั่วไปในกรณีที่ความแตกต่างของความดันระหว่างเฟสเล็กนัย (เช่น แรงตึงผิวไม่สำคัญ) อย่างไรก็ตาม ในบางแบบจำลองอาจมีความดันที่แตกต่างกัน $p_k$ สำหรับแต่ละเฟส

---

## 🔍 การวิเคราะห์แต่ละเทอมในสมการ

### 1. ความเร่งตามเวลา (Temporal Acceleration)
$$\frac{\partial}{\partial t}(\alpha_k \rho_k \mathbf{u}_k)$$

**ความหมาย:** อัตราการเปลี่ยนแปลงโมเมนตัมเฉพาะที่ของเฟส $k$
- **ทางคณิตศาสตร์:** อนุพันธ์ย่อยของความหนาแน่นโมเมนตัม
- **ทางกายภาพ:** ความเร่งเฉพาะที่รวมถึงผลกระทบที่ไม่คงที่
- **ลักษณะหลายเฟส:** รวมการเปลี่ยนแปลงทั้งความเร็วและสัดส่วนปริมาตร

### 2. ความเร่งแบบพา (Convective Acceleration)
$$\nabla \cdot (\alpha_k \rho_k \mathbf{u}_k \mathbf{u}_k)$$

**ความหมาย:** ไดเวอร์เจนซ์ของเทนเซอร์ฟลักซ์โมเมนตัม
- **การวิเคราะห์เทนเซอร์:** $\mathbf{u}_k \mathbf{u}_k$ มีส่วนประกอบเป็น $(u_{k,i} u_{k,j})$
- **ทางกายภาพ:** ความเร่งเนื่องจากการเปลี่ยนแปลงความเร็วตามตำแหน่ง
- **การแปลความ:** ฟลักซ์โมเมนตัมเนื่องจากการเคลื่อนที่ของเฟส $k$ ผ่านขอบเขตของปริมาตรควบคุม

### 3. แรงดัน (Pressure Force)
$$-\alpha_k \nabla p$$

**ความหมาย:** เกรเดียนต์ของสนามสเกลาร์ความดัน
- **ลักษณะหลายเฟส:** เศษส่วนเฟสปรับเปลี่ยนแรงดัน
- **ทางกายภาพ:** แรงเนื่องจากความแตกต่างของความดัน
- **ข้อสมมติฐาน:** สนามความดันร่วม (mechanical equilibrium) ถูกใช้เป็นค่าเริ่มต้น

### 4. แรงหนืด (Viscous Force)
$$\nabla \cdot (\alpha_k \boldsymbol{\tau}_k)$$

**ความหมาย:** ไดเวอร์เจนซ์ของเทนเซอร์ความเค้น
- **ของไหลนิวตัน:** $\boldsymbol{\tau}_k = \mu_k \left( \nabla \mathbf{u}_k + \nabla \mathbf{u}_k^T \right) - \frac{2}{3}\mu_k (\nabla \cdot \mathbf{u}_k)\mathbf{I}$
- **ทางกายภาพ:** แรงหนืดภายในเฟส $k$ เท่านั้น
- **ลักษณะหลายเฟส:** ความเค้นกระทำเฉพาะในบริเวณของเฟส

### 5. แรงปริมาตร (Body Force)
$$\alpha_k \rho_k \mathbf{g}$$

**ความหมาย:** ความเร่งโน้มถ่วงคูณด้วยความหนาแน่น
- **ทางกายภาพ:** น้ำหนักของเฟส $k$ ต่อหน่วยปริมาตร
- **ลักษณะหลายเฟส:** ผลของแรงลอยตัว (buoyancy) ผ่านความแตกต่างของความหนาแน่น

### 6. การถ่ายเทโมเมนตัมระหว่างเฟส (Interfacial Momentum Transfer)
$$\mathbf{M}_k$$

**ความหมาย:** แรงทั้งหมดที่พื้นผิวระหว่างเฟส
- **การอนุรักษ์:** $\sum_{k=1}^{N} \mathbf{M}_k = \mathbf{0}$ (กฎข้อที่สามของนิวตัน)
- **ความซับซ้อน:** ขึ้นอยู่กับรูปทรงของพื้นผิวและสภาวะการไหล
- **ความสำคัญ:** เป็นเทอมที่เชื่อมโยงพลวัตของทุกเฟสเข้าด้วยกัน

---

## 📊 กรณีพิเศษและการทำให้ง่ายขึ้น

### การไหลแบบอัดตัวไม่ได้ (Incompressible Flow)
**เงื่อนไข:** $\rho_k = \text{คงที่}$

$$\alpha_k \rho_k \left[ \frac{\partial \mathbf{u}_k}{\partial t} + \mathbf{u}_k \cdot \nabla \mathbf{u}_k \right] = -\alpha_k \nabla p + \nabla \cdot (\alpha_k \boldsymbol{\tau}_k) + \alpha_k \rho_k \mathbf{g} + \mathbf{M}_k$$

### ไม่มีแรงระหว่างเฟส
**เงื่อนไข:** $\mathbf{M}_k = \mathbf{0}$

$$\frac{\partial}{\partial t}(\alpha_k \rho_k \mathbf{u}_k) + \nabla \cdot (\alpha_k \rho_k \mathbf{u}_k \mathbf{u}_k) = -\alpha_k \nabla p + \nabla \cdot (\alpha_k \boldsymbol{\tau}_k) + \alpha_k \rho_k \mathbf{g}$$

สิ่งนี้เกิดขึ้นเมื่อ:
- เฟสต่างๆ แยกกันโดยสมบูรณ์
- ไม่มีการถ่ายเทโมเมนตัมระหว่างเฟส
- กรณีศึกษาเชิงทฤษฎีบางอย่าง

---

## 🔄 การถ่ายเทโมเมนตัมระหว่างเฟส

### กรอบการทำงานทางคณิตศาสตร์
$$\mathbf{M}_k = \sum_{j \neq k} \mathbf{M}_{kj}$$

โดยที่ $\mathbf{M}_{kj}$ แสดงถึงการแลกเปลี่ยนโมเมนตัมจากเฟส $j$ ไปยังเฟส $k$

**หลักการอนุรักษ์:**
$$\sum_{k=1}^{N} \mathbf{M}_k = \mathbf{0}$$

**การพิสูจน์:** ตามกฎข้อที่สามของนิวตัน $\mathbf{M}_{kj} = -\mathbf{M}_{jk}$

> [!TIP] **การตีความ $\mathbf{M}_{kj} = -\mathbf{M}_{jk}$**
> แรงที่เฟส $j$ กระทำต่อเฟส $k$ มีขนาดเท่ากันแต่ทิศทางตรงข้ามกับแรงที่เฟส $k$ กระทำต่อเฟส $j$ นี่คือหลักการของแรงและปฏิกิริยา

---

## 💪 ประเภทของแรงระหว่างเฟส

เทอม $\mathbf{M}_k$ ประกอบด้วยแรงย่อยต่างๆ ดังนี้:

$$\mathbf{M}_k = \sum_{j \neq k} \left[ \mathbf{M}_{kj}^{drag} + \mathbf{M}_{kj}^{lift} + \mathbf{M}_{kj}^{vm} + \mathbf{M}_{kj}^{td} + \mathbf{M}_{kj}^{other} \right] \tag{2.2}$$

### 1. แรงฉุด (Drag Force)

#### กลไกทางกายภาพ
แรงต้านหนืดต่อการเคลื่อนที่สัมพัทธ์ระหว่างเฟส เกิดจากความเค้นเฉือนที่พื้นผิวและแรงฉุดเนื่องจากการแยกตัวของการไหล

#### รูปแบบทั่วไป
$$\mathbf{M}_{kj}^{drag} = K_{kj}(\mathbf{u}_j - \mathbf{u}_k)$$

#### สัมประสิทธิ์แรงฉุด $K_{kj}$

| สภาวะ | ช่วงเลขเรย์โนลด์ส | สัมประสิทธิ์ | สูตร |
|--------|-------------------|-------------|--------|
| **Stokes** | Re < 1 | $K_{kj}^{Stokes}$ | $\frac{18\mu_k \alpha_k \alpha_j}{d_p^2}$ |
| **Schiller-Naumann** | 1 < Re < 1000 | $K_{kj}^{SN}$ | $\frac{18\mu_k \alpha_k \alpha_j}{d_p^2} \cdot \frac{1}{24}C_D \text{Re}$ |
| **ค่า C_D** | - | - | $C_D = \frac{24}{\text{Re}}(1 + 0.15\text{Re}^{0.687})$ |

**นิยามเลขเรย์โนลด์ส:**
$$\text{Re} = \frac{\rho_k |\mathbf{u}_j - \mathbf{u}_k| d_p}{\mu_k}$$

#### การตีความทางกายภาพ
- **Re < 1**: แรงหนืดมีอิทธิพลเด่นชัด ความสัมพันธ์เป็นเชิงเส้น
- **1 < Re < 1000**: สภาวะเปลี่ยนผ่าน มีทั้งผลจากความหนืดและแรงเฉื่อย
- **Re > 1000**: แรงเฉื่อยมีอิทธิพลเด่นชัด ความสัมพันธ์เป็นกำลังสอง

### 2. แรงยก (Lift Force)

#### กลไกทางกายภาพ
แรงในแนวข้างกระทำต่ออนุภาค/ฟองอากาศ เนื่องจากการไล่ระดับความเร็วในเฟสต่อเนื่อง (Magnus effect และ Saffman lift)

#### รูปแบบทั่วไป
$$\mathbf{M}_{kj}^{lift} = C_L \rho_c \alpha_k \alpha_j (\mathbf{u}_j - \mathbf{u}_k) \times (\nabla \times \mathbf{u}_c)$$

โดยที่:
- $C_L$ = สัมประสิทธิ์แรงยก
- $\rho_c$ = ความหนาแน่นของเฟสต่อเนื่อง (continuous phase)
- $\mathbf{u}_c$ = ความเร็วของเฟสต่อเนื่อง

#### สัมประสิทธิ์แรงยก $C_L$

**Saffman Lift Coefficient (สำหรับ Re ต่ำ):**
$$C_L^{Saffman} = \frac{6.46}{\pi} d_p \sqrt{\frac{\nu_k}{|\mathbf{u}_{rel}|}}$$

**Mei Autlift Model (สำหรับ Re จำกัด):**
$$C_L = C_L^{Saffman} \cdot f(\text{Re}, \text{Re}_\gamma)$$

โดยที่:
- $\text{Re}_\gamma = \frac{d_p^2 |\nabla \times \mathbf{u}_k|}{\nu_k}$ = เลขเรย์โนลด์สของการเฉือน
- $\nu_k = \mu_k/\rho_k$ = ความหนืดจลนศาสตร์

#### การตีความทางกายภาพ
- **แรงยกบวก**: อนุภาคเคลื่อนที่เข้าหาบริเวณที่มีความเร็วสูงขึ้น
- **แรงยกเป็นลบ**: อนุภาคเคลื่อนที่เข้าหาบริเวณที่มีความเร็วต่ำลง
- **ขนาดขึ้นอยู่กับ**: การไล่ระดับความเร็ว, ความเร็วสัมพัทธ์, คุณสมบัติของของไหล

### 3. แรงมวลเสมือน (Virtual Mass Force)

#### กลไกทางกายภาพ
แรงเพิ่มเติมที่จำเป็นในการเร่งของไหลโดยรอบเมื่ออนุภาคเร่ง (ผลของมวลที่ถูกเพิ่มเข้ามา - added mass effect)

#### รูปแบบแบบสมมาตร
$$\mathbf{M}_{kj}^{vm} = C_{vm} \rho_c \alpha_k \alpha_j \left(\frac{\mathrm{D}\mathbf{u}_j}{\mathrm{D}t} - \frac{\mathrm{D}\mathbf{u}_k}{\mathrm{D}t}\right)$$

โดยที่ $C_{vm} = \frac{1}{2}$ สำหรับอนุภาคทรงกลม และ $\frac{\mathrm{D}\mathbf{u}}{\mathrm{D}t} = \frac{\partial \mathbf{u}}{\partial t} + \mathbf{u} \cdot \nabla \mathbf{u}$ คือ อนุพันธ์วัตถุ (material derivative)

#### การตีความทางกายภาพ
- **มวลเสมือนเป็นบวก**: อนุภาคที่กำลังเร่งจะพาของไหลโดยรอบไปด้วย
- **มวลเสมือนเป็นลบ**: อนุภาคที่กำลังหน่วงจะถ่ายโมเมนตัมกลับไปยังของไหล
- **ความสำคัญ:** มีความสำคัญสำหรับอัตราส่วนความหนาแน่นสูงและการเร่งอย่างรวดเร็ว

### 4. แรงอื่นๆ

| ประเภทแรง | กลไกทางกายภาพ | ความสำคัญ |
|------------|------------------|-------------|
| **Turbulent dispersion** | ความผันผวนของความเร็วแบบสุ่ม | สำคัญในการไหลที่มีความปั่นป่วนสูง |
| **Wall lubrication** | แรงผลักใกล้ผนัง | สำคัญในการไหลในท่อ |
| **Surface tension** | ผลกระทบจากความตึงผิว | สำคัญสำหรับพื้นผิวที่เปลี่ยนรูปได้ |

> [!INFO] **ดูรายละเอียดเพิ่มเติม**
> สำหรับรายละเอียดเพิ่มเติมเกี่ยวกับแรงตึงผิวและปรากฏการณ์ระหว่างเฟส โปรดดูที่ [[06_Interfacial_Phenomena_Equations]]

---

## 💻 การนำไปใช้ใน OpenFOAM (C++ Implementation)

### สมการโมเมนตัมใน OpenFOAM

ในไฟล์ `UEqn.H` ของ Solver `multiphaseEulerFoam`, สมการโมเมนตัมถูกสร้างดังนี้:

```cpp
// Momentum equation assembly for phase k
fvVectorMatrix UEqn
(
    fvm::ddt(alpha, rho, U) + fvm::div(alphaRhoPhi, U)
  - fvm::Sp(fvc::ddt(alpha, rho) + fvc::div(alphaRhoPhi), U)
  + turbulence->divDevReff(RhoEff)
 ==
    - alpha*fvc::grad(p)
    + alpha*rho*g
    + phase.Kd()*(U.otherPhase() - U) // Drag coupling
    + interfacialForces // Lift, virtual mass, etc.
);
```

**การแปลงความหมาย:**
- `fvm::ddt(alpha, rho, U)` แทน $\frac{\partial}{\partial t}(\alpha_k \rho_k \mathbf{u}_k)$
- `fvm::div(alphaRhoPhi, U)` แทน $\nabla \cdot (\alpha_k \rho_k \mathbf{u}_k \mathbf{u}_k)$
- `fvc::grad(p)` แทน $\nabla p$
- `turbulence->divDevReff(RhoEff)` แทน $\nabla \cdot (\alpha_k \boldsymbol{\tau}_k)$
- `alpha*rho*g` แทน $\alpha_k \rho_k \mathbf{g}$
- `phase.Kd()*(U.otherPhase() - U)` แทน $\mathbf{M}_{kj}^{drag}$
- `interfacialForces` แทนแรงระหว่างเฟสอื่นๆ

### การเชื่อมโยงความดัน-ความเร็ว

OpenFOAM ใช้เทคนิค **Partial Elimination Algorithm (PEA)** เพื่อจัดการกับเทอม Drag ที่มีความแข็ง (stiffness) สูง โดยการย้ายเทอมความเร็วของเฟสอื่นมาไว้ในด้าน implicit เพื่อเพิ่มความเสถียรในการคำนวณ

### การนำไปใช้ Interfacial Momentum Transfer

```cpp
// OpenFOAM interfacial momentum transfer implementation
template<class Phase1, class Phase2>
tmp<volVectorField> Phase1Phase2Model<Phase1, Phase2>::K() const
{
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
}
```

**การแปลงความหมาย:**
- `Kd * (phase2_.U() - phase1_.U())` แทน $\mathbf{M}_{kj}^{drag}$
- `Flift` แทน $\mathbf{M}_{kj}^{lift}$
- `Cvm * rho1_ * (DDt(phase2_.U()) - DDt(phase1_.U()))` แทน $\mathbf{M}_{kj}^{vm}$

---

## ⚙️ เทนเซอร์ความเค้น (Stress Tensor)

### สำหรับเฟส $k$ แบบนิวตัน

เทนเซอร์ความเค้นของโคชี (Cauchy stress tensor):
$$\boldsymbol{\sigma}_k = -p\mathbf{I} + \boldsymbol{\tau}_k$$

เทนเซอร์ความเค้นหนืด:
$$\boldsymbol{\tau}_k = \mu_k \left(\nabla \mathbf{u}_k + (\nabla \mathbf{u}_k)^T\right) + \lambda_k (\nabla \cdot \mathbf{u}_k)\mathbf{I}$$

**นิยามสัมประสิทธิ์:**
- $\mu_k$ = ความหนืดพลวัต (dynamic viscosity) ($\text{Pa·s}$)
- $\lambda_k$ = ความหนืดที่สอง (second viscosity) ($\text{Pa·s}$)
- **สำหรับก๊าซอะตอมเดี่ยว:** $\lambda_k = -\frac{2}{3}\mu_k$ (สมมติฐานของสโตกส์)

สำหรับของไหลที่อัดตัวไม่ได้ ($\nabla \cdot \mathbf{u}_k = 0$):
$$\boldsymbol{\tau}_k = \mu_k \left(\nabla \mathbf{u}_k + (\nabla \mathbf{u}_k)^T\right)$$

---

## 📊 ตารางสรุปพฤติกรรมทางฟิสิกส์

| แรง | กลไกหลัก | ความสำคัญ | การประยุกต์ใช้ |
|-----|----------|-----------|----------------|
| **Drag** | ความเร็วสัมพัทธ์ | สูงมาก (ทุกระบบ) | ทุกการจำลองหลายเฟส |
| **Lift** | การเฉือน (Shear) | สูง (การไหลในท่อ, ฟองอากาศ) | คอลัมน์ฟอง, การไหลในท่อ |
| **Virtual Mass** | การเร่งความเร็ว (Acceleration) | สูง (Unsteady flows, Gas-Liquid) | การเกิดฟอง, การสั่นไหว |
| **Turbulent Dispersion** | ความปั่นป่วน (Turbulence) | ปานกลาง (การผสมเฟส) | การไหลแบบปั่นป่วน |
| **Wall Lubrication** | แรงผลักจากผนัง | ปานกลาง (ใกล้ผนัง) | การไหลในท่อขนาดเล็ก |

---

## 🔗 หัวข้อที่เกี่ยวข้อง

- [[01_Mass_Conservation|สมการอนุรักษ์มวล]] - ทบทวนความต่อเนื่องก่อนศึกษาโมเมนตัม
- [[03_Energy_Conservation|สมการอนุรักษ์พลังงาน]] - ศึกษาถัดไปหลังจากโมเมนตัม
- [[06_Interfacial_Phenomena_Equations|ปรากฏการณ์ระหว่างเฟส]] - รายละเอียดเกี่ยวกับแรงตึงผิวและ Marangoni
- [[07_Turbulence_Modeling_Equations|แบบจำลองความปั่นป่วน]] - ผลกระทบของความปั่นป่วนต่อเทนเซอร์ความเค้น
- [[10_Special_Cases|กรณีพิเศษ]] - กรณีอัดตัวไม่ได้ แกรนูลาร์ และอื่นๆ

---

## 📝 สรุป

สมการอนุรักษ์โมเมนตัมสำหรับระบบหลายเฟสมีความซับซ้อนมากกว่าเฟสเดียวเนื่องจาก:

1. **เทอมการถ่ายเทโมเมนตัมระหว่างเฟส** ($\mathbf{M}_k$) เชื่อมโยงสมการของทุกเฟสเข้าด้วยกัน
2. **แรงระหว่างเฟสหลายประเภท** ต้องถูกจำลอง ขึ้นอยู่กับสภาวะการไหล
3. **เทนเซอร์ความเค้น** มีความซับซ้อนเนื่องจากการมีอยู่ของหลายเฟสในปริมาตรควบคุม
4. **การจัดการเชิงตัวเลข** ต้องการเทคนิคพิเศษเพื่อความเสถียร

การทำความเข้าใจสมการนี้อย่างถี่ถ้วนเป็นพื้นฐานสำคัญในการจำลองการไหลแบบหลายเฟสใน OpenFOAM อย่างมีประสิทธิภาพ
