# รายละเอียดการนำไปใช้ใน OpenFOAM (OpenFOAM Implementation)

## ภาพรวม (Overview)

OpenFOAM นำสถาปัตยกรรม drag model ที่ซับซ้อนมาใช้ ซึ่งเป็นรากฐานสำหรับการคำนวณการแลกเปลี่ยนโมเมนตัมของ Multiphase Flow ผ่านการออกแบบแบบ Object-Oriented ที่ช่วยให้ผู้ใช้สามารถสลับโมเดลได้ตามความเหมาะสม

---

## 1. ลำดับชั้นของคลาส Drag Model (Class Hierarchy)

OpenFOAM ออกแบบระบบจำลองแรงฉุดโดยใช้หลักการ Object-Oriented Programming ซึ่งช่วยให้ผู้ใช้สามารถสลับโมเดลได้ตามความเหมาะสมผ่านไฟล์การตั้งค่า

### หลักการสำคัญ
- คลาสพื้นฐาน `dragModel` กำหนดอินเทอร์เฟซพื้นฐาน
- การออกแบบแบบ Polymorphic ช่วยให้สามารถสลับระหว่าง Drag Correlation ที่แตกต่างกันได้อย่างราบรื่น
- รักษา Workflow การคำนวณที่สอดคล้องกัน

### โครงสร้างคลาสพื้นฐาน (Base Class Structure)

คลาสพื้นฐาน `dragModel` กำหนดฟังก์ชันเสมือน (Virtual functions) สำหรับโมเดลลูก:

```cpp
class dragModel
{
public:
    // คำนวณสัมประสิทธิ์แรงฉุด (Pure virtual)
    virtual tmp<volScalarField> Cd() const = 0;

    // คำนวณสัมประสิทธิ์การแลกเปลี่ยนโมเมนตัม
    virtual tmp<volScalarField> K() const;

    // คำนวณแรงฉุดรวม
    virtual tmp<volVectorField> F() const;
};
```

**คุณสมบัติที่สำคัญ:**
- ใช้ระบบ Smart Pointer `tmp` ของ OpenFOAM สำหรับการจัดการหน่วยความจำที่มีประสิทธิภาพ
- ฟังก์ชัน Pure virtual `Cd()` รับประกันว่าคลาสที่สืบทอดมาต้องนำการคำนวณ drag coefficient ที่เฉพาะเจาะจงมาใช้
- การนำไปใช้เริ่มต้นของ `K()` และ `F()` ให้สูตรมาตรฐานที่สามารถเขียนทับได้

### ลำดับชั้นของคลาส (Class Hierarchy Diagram)

```mermaid
flowchart TD
    A[dragModel<br/>Base Class] --> B[SchillerNaumann<br/>Standard Spherical Particles]
    A --> C[IshiiZuber<br/>Deformable Bubbles/Droplets]
    A --> D[MorsiAlexander<br/>Wide Re Range]
    A --> E[SyamlalOBrien<br/>Fluidized Beds]
    A --> F[Tomiyama<br/>Contaminated Bubbles]

    B --> B1[Virtual Cd&#40;&#41;]
    C --> C1[Virtual Cd&#40;&#41;]
    D --> D1[Virtual Cd&#40;&#41;]
    E --> E1[Virtual Cd&#40;&#41;]
    F --> F1[Virtual Cd&#40;&#41;]
```

---

## 2. การคำนวณ Momentum Exchange Coefficient ($K$)

ค่า $K$ คือพารามิเตอร์ที่เชื่อมโยงความเร็วของทั้งสองเฟสเข้าด้วยกันในสมการโมเมนตัม

### สูตรที่ใช้ใน Source Code

**Momentum exchange coefficient `K`** แสดงถึงพารามิเตอร์การเชื่อมโยงพื้นฐานระหว่างเฟสในระบบ Multiphase Flow

$$K = \frac{3}{4} C_D \frac{\alpha_k \alpha_l \rho_l}{d_k} |\mathbf{u}_r| \tag{2.1}$$

**นิยามตัวแปร:**
- `$K$` = Momentum exchange coefficient
- `$C_d$` = Drag coefficient (จาก model ที่เฉพาะเจาะจง)
- `$\alpha_1$`, `$\alpha_2$` = Volume fractions ของเฟสที่ 1 และ 2
- `$\rho_2$` = Density ของเฟสที่ 2 (dispersed phase)
- `$d_1$` = Diameter ของอนุภาคในเฟสที่ 1
- `$|\mathbf{u}_r|$` = Relative velocity magnitude

### การนำไปใช้ใน OpenFOAM (Implementation)

```cpp
tmp<volScalarField> dragModel::K() const
{
    const volScalarField& alpha1 = pair_.phase1().alpha();
    const volScalarField& alpha2 = pair_.phase2().alpha();
    const volScalarField& rho2 = pair_.phase2().rho();
    const volScalarField& d = pair_.dispersed().d();
    const volScalarField& Ur = pair_.Ur();

    return (3.0/4.0)*Cd()*alpha1*alpha2*rho2/(d)*Ur;
}
```

**ปัจจัยที่รวมอยู่ในการคำนวณ:**
- **Volume fractions** (`alpha1`, `alpha2`) - การกระจายตัวของเฟส
- **Dispersed phase density** (`rho2`) - ผลกระทบจากความเฉื่อย
- **Particle diameter** (`d`) - ขนาดความยาวลักษณะเฉพาะ
- **Relative velocity magnitude** (`Ur`) - ผลกระทบแบบไดนามิก
- **Drag coefficient** (`Cd()`) - จากการนำไปใช้ของ model ที่เฉพาะเจาะจง

---

## 3. การจัดการความเร็วสัมพัทธ์และเลขเรย์โนลด์

OpenFOAM คำนวณความเร็วสัมพัทธ์ ($U_r$) และเลขเรย์โนลด์ของอนุภาค ($Re_p$) โดยอัตโนมัติในคลาส `PhasePair`:

### การคำนวณในคลาส PhasePair

**Relative velocity** แสดงถึงแรงขับเคลื่อนทางจลนศาสตร์เบื้องหลังการถ่ายโอนโมเมนตัมระหว่างเฟส

```cpp
tmp<volScalarField> PhasePair::Ur() const
{
    return mag(phase2().U() - phase1().U());
}

tmp<volScalarField> PhasePair::Re() const
{
    return phase1().rho()*Ur()*dispersed().d()/phase1().mu();
}
```

### สมการทางคณิตศาสตร์

**Relative Velocity:**
$$|\mathbf{u}_r| = |\mathbf{u}_2 - \mathbf{u}_1|$$

**Reynolds Number:**
$$Re = \frac{\rho_1 \cdot |\mathbf{u}_r| \cdot d_1}{\mu_1}$$

**นิยามตัวแปร:**
- `$|\mathbf{u}_r|$` = Relative velocity magnitude
- `$\mathbf{u}_1$`, `$\mathbf{u}_2$` = Velocity vectors ของเฟสที่ 1 และ 2
- `$Re$` = Reynolds number (ไม่มีหน่วย)
- `$\rho_1$` = Density ของเฟสที่ 1 (continuous phase)
- `$d_1$` = Characteristic diameter
- `$\mu_1$` = Dynamic viscosity ของเฟสที่ 1

**ประโยชน์ของระบบ:**
- **ตรวจจับระบอบการไหลโดยอัตโนมัติ** - ช่วยให้ Drag Correlation ที่เหมาะสมถูกนำไปใช้ตามเงื่อนไขการไหลในแต่ละตำแหน่ง
- **ความสอดคล้องกับสูตร drag model** - การใช้คุณสมบัติของ continuous phase ในการคำนวณ Reynolds number
- **การแสดงคุณสมบัติทางฟิสิกส์ที่แม่นยำ** - รับประกันการจำลอง interfacial physics ที่ถูกต้อง

---

## 4. การนำไปใช้ Drag Model ที่เฉพาะเจาะจง (Specific Drag Model Implementations)

### 4.1 Schiller-Naumann Model

**Schiller-Naumann drag model** เป็น drag correlation ที่ถูกใช้งานอย่างแพร่หลายที่สุดใน OpenFOAM โดยเฉพาะอย่างยิ่งสำหรับอนุภาคทรงกลมในทั้ง laminar และ turbulent regimes

#### สมการ Drag Coefficient

Drag coefficient $C_D$ ขึ้นอยู่กับ particle Reynolds number $Re_p$:

$$C_D = \begin{cases}
\frac{24}{Re_p}(1 + 0.15 Re_p^{0.687}) & Re_p < 1000 \\
0.44 & Re_p \geq 1000
\end{cases}$$

#### OpenFOAM Code Implementation

```cpp
// Schiller-Naumann drag model
template<class PhasePair>
class SchillerNaumann
:
    public dragModel
{
    virtual tmp<volScalarField> Cd() const
    {
        const volScalarField& Re = pair_.Re();

        return volScalarField::New
        (
            "Cd",
            max
            (
                24.0/Re*(1.0 + 0.15*pow(Re, 0.687)),
                0.44
            )
        );
    }
};
```

**รายละเอียดการ Implement:**
- `tmp<volScalarField>` = กลยุทธ์การจัดการหน่วยความจำสำหรับ temporary fields
- `pair_.Re()` = เข้าถึง Reynolds number field จาก phase pair
- `volScalarField::New` = สร้าง field ใหม่พร้อมการจัดการหน่วยความจำอัตโนมัติ
- `max` function = ให้มั่นใจว่ามีการเปลี่ยนผ่านที่ราบรื่นระหว่างสอง regime
- `pow(Re, 0.687)` = คำนวณ exponent ของ Reynolds number อย่างมีประสิทธิภาพ

### 4.2 Ishii-Zuber Model

**Ishii-Zuber model** ถูกพัฒนาขึ้นมาโดยเฉพาะสำหรับ multiphase flows ที่เกี่ยวข้องกับ **distorted bubbles** และ **droplets** ทำให้เหมาะอย่างยิ่งสำหรับระบบ gas-liquid

#### สมการ Drag Coefficient

$$C_D = \begin{cases}
\frac{24}{Re_p}(1 + 0.1 Re_p^{0.75}) & Re_p < 1000 \\
\frac{8}{3}\frac{Eo}{Eo + 4} & \text{Distorted regime}
\end{cases}$$

โดยที่ **Eötvös number** $Eo = \frac{g(\rho_c - \rho_d)d^2}{\sigma}$

**ความหมายของตัวแปร:**
- $g$ = gravitational acceleration (m/s²)
- $\rho_c$ = density ของ continuous phase (kg/m³)
- $\rho_d$ = density ของ dispersed phase (kg/m³)
- $d$ = characteristic particle/bubble diameter (m)
- $\sigma$ = surface tension (N/m)

### 4.3 Syamlal-O'Brien Model

**Syamlal-O'Brien model** ถูกพัฒนาขึ้นมาโดยเฉพาะสำหรับ **fluidized bed applications** ซึ่งการมีปฏิสัมพันธ์ระหว่างอนุภาคและผลกระทบของ dense phase มีอิทธิพลอย่างมาก

#### สมการหลัก

$$C_D = \frac{v_r^2}{v_s^2}$$

**ความหมายของตัวแปร:**
- $C_D$ = drag coefficient (ไม่มีหน่วย)
- $v_r$ = relative velocity ระหว่าง phases (m/s)
- $v_s$ = terminal settling velocity ของอนุภาคเดี่ยว (m/s)

### 4.4 Tomiyama Model

**Tomiyama model** ถูกพัฒนาขึ้นมาโดยเฉพาะสำหรับ **contaminated bubbles** ในระบบ gas-liquid

#### สมการ Drag Coefficient

$$C_D = \max\left[0.44, \min\left(\frac{24}{Re_p}(1 + 0.15 Re_p^{0.687}), \frac{72}{Re_p}\right)\right]$$

---

## 5. ข้อควรพิจารณาด้านเสถียรภาพ (Numerical Stability)

เนื่องจากเทอมแรงฉุดมักจะมีค่าสูงและ "แข็ง" (Stiff) OpenFOAM จึงมีกลยุทธ์ดังนี้:

### 5.1 การจัดการแบบ Implicit vs Explicit

#### **Explicit Drag:**
$$\mathbf{M}_k^{n+1} = \mathbf{K}_{kl}^n (\mathbf{u}_l^n - \mathbf{u}_k^n)$$

- **ข้อดี**: การนำไปใช้ที่ง่าย, ไม่มีการเชื่อมโยงระหว่างเฟสในแต่ละ time step
- **ข้อเสีย**: ข้อจำกัดของ time step (CFL condition)

#### **Implicit Drag:**
$$\mathbf{M}_k^{n+1} = \mathbf{K}_{kl}^{n+1} (\mathbf{u}_l^{n+1} - \mathbf{u}_k^{n+1})$$

- **ข้อดี**: เสถียรภาพสูงกว่า, time step ที่ใหญ่ขึ้น
- **ข้อเสีย**: การแก้ปัญหาระบบที่เชื่อมโยงกัน (coupled system solution)

### 5.2 การใช้ Under-Relaxation

เพื่อป้องกันการแกว่งกวัดของผลเฉลย (Oscillations):

$$\mathbf{K}_{new} = (1-\lambda)\mathbf{K}_{old} + \lambda \mathbf{K}_{calculated}$$

โดยทั่วไปใช้ค่า $\lambda \approx 0.3 - 0.7$ ในไฟล์ `fvSolution`

**แฟกเตอร์การผ่อนคลายทั่วไป (Typical relaxation factor)**: $\lambda = 0.3 - 0.7$

| ปัจจัย | ค่าแนะนำของ $\lambda$ | คำอธิบาย |
|---------|----------------------|-----------|
| **รูปแบบการไหล** | $0.5 - 0.7$ (สภาวะคงตัว) <br> $0.3 - 0.5$ (ไม่คงตัว) | ปัญหาสภาวะคงตัวใช้การผ่อนคลายที่น้อยกว่า |
| **ระดับการเชื่อมโยง** | $0.3 - 0.4$ (สูง) <br> $0.5 - 0.7$ (ต่ำ) | การไหลแบบหลายเฟสที่เชื่อมโยงกันอย่างมากต้องการการผ่อนคลายมากขึ้น |
| **คุณภาพ Mesh** | $0.4 - 0.6$ (คุณภาพต่ำ) <br> $0.5 - 0.7$ (คุณภามสูง) | Mesh ที่ละเอียดกว่าอาจยอมให้ใช้แฟกเตอร์การผ่อนคลายที่ใหญ่ขึ้น |

---

## 6. ผลกระทบของสารแขวนลอยความเข้มข้นสูง (Dense Suspension Effects)

### การตกตะกอนแบบถูกขัดขวาง (Hindered Settling)

ใน Solver `multiphaseEulerFoam` ของ OpenFOAM ผลกระทบของสารแขวนลอยความเข้มข้นสูงจะถูกรวมเข้าไว้ด้วยกันผ่านการปรับปรุงค่าสัมประสิทธิ์การแลกเปลี่ยนโมเมนตัม $\mathbf{K}_{kl}$ ระหว่างเฟส $k$ และ $l$:

$$\mathbf{K}_{kl}^{modified} = \mathbf{K}_{kl} \cdot f(\alpha_l)$$

### สมการ Richardson-Zaki

**ตัวประกอบการตกตะกอนแบบถูกขัดขวาง** $f(\alpha_c)$ จะปรับปรุงความเร็วตกตะกอนสุดท้าย:

$$v_t = v_{t,0} (1 - \alpha_d)^n$$

**รูปแบบทั่วไปของ $f(\alpha_l)$**:

| ความสัมพันธ์ | สูตร | คำอธิบาย |
|--------------|--------|-----------|
| **Einstein relation** | $f(\alpha_l) = (1 - \alpha_d)^{2.5}$ | สำหรับความเข้มข้นต่ำ |
| **Barnea-Mizrahi** | $f(\alpha_l) = (1 - \alpha_d)^{2.0} \exp\left(\frac{2.5\alpha_d}{1 - \alpha_d}\right)$ | สำหรับความเข้มข้นสูง |

### OpenFOAM Code Implementation

```cpp
// ในคลาสโมเดลการลาก (drag model class)
virtual tmp<volScalarField> K(const phasePairKey& key) const
{
    const phaseModel& phase1 = this->phase1_;
    const phaseModel& phase2 = this->phase2_;

    // ค่าสัมประสิทธิ์การลากพื้นฐาน (Base drag coefficient)
    const volScalarField K0 = this->K0(key);

    // ตัวประกอบการตกตะกอนแบบถูกขัดขวาง (Hindered settling factor)
    const volScalarField alphaD = phase2;
    const volScalarField fHindered =
        (scalar(1) - alphaD)*exp(2.5*alphaD/(scalar(1) - alphaD));

    // ค่าสัมประสิทธิ์การลากที่ปรับปรุงแล้ว (Modified drag coefficient)
    return K0*fHindered;
}
```

---

## 7. ผลกระทบจากความปั่นป่วน (Turbulent Effects)

### การกระจายตัวเนื่องจากความปั่นป่วน (Turbulent Dispersion)

แรงกระจายตัวเนื่องจากความปั่นป่วน $\mathbf{F}_{TD}$ แสดงถึงผลทางสถิติของความผันผวนของความเร็วที่ปั่นป่วนต่อการกระจายตัวของเฟส:

$$\mathbf{F}_{TD} = -C_{TD} \rho_c k_c \nabla \alpha_d$$

โดยที่:
- $C_{TD}$ คือสัมประสิทธิ์เชิงปรจักษ์ (โดยทั่วไปมีค่า 0.1 - 1.0)
- $k_c$ คือพลังงานจลน์จากความปั่นป่วน (turbulent kinetic energy)

#### OpenFOAM Code Implementation

```cpp
// การคำนวณแรงกระจายตัวเนื่องจากความปั่นป่วน
const volScalarField Ctd(this->Ctd_);
const volScalarField kc(this->kc_);

// แรงกระจายตัวเนื่องจากความปั่นป่วน
const volVectorField Ftd
(
    -Ctd*rhoc*kc*fvc::grad(alphad)
);
```

### แรงลากที่ปรับปรุงด้วยความปั่นป่วน (Turbulence-Modified Drag)

**ความเร็วสัมพัทธ์ประสิทธิผล** (Effective relative velocity) รวมความผันผวนของความปั่นป่วน:

$$|\mathbf{u}_{rel}|_{eff} = \sqrt{|\mathbf{u}_l - \mathbf{u}_k|^2 + 2k_c}$$

---

## 8. อนุภาคที่ไม่ใช่ทรงกลม (Non-Spherical Particles)

### ตัวประกอบรูปร่าง (Shape Factor)

สำหรับอนุภาคที่ไม่ใช่ทรงกลม ให้ใช้ **ตัวประกอบรูปร่าง** $\phi$:

$$\phi = \frac{\text{พื้นที่ผิวของทรงกลมที่มีปริมาตรเท่ากัน}}{\text{พื้นที่ผิวจริง}}$$

เส้นผ่านศูนย์กลางที่เทียบเท่าคือ:
$$d_{eff} = d_v \phi^{0.5}$$

### สัมประสิทธิ์แรงลากที่ปรับปรุงแล้ว (Modified Drag Coefficient)

**การประมาณค่า Haider-Levenspiel**:

$$C_D = \frac{24}{Re_p}(1 + a Re_p^b) + \frac{c}{1 + d/Re_p}$$

โดยที่สัมประสิทธิ์ $a, b, c, d$ ขึ้นอยู่กับรูปร่างของอนุภาค

| รูปร่างอนุภาค | $a$ | $b$ | $c$ | $d$ |
|----------------|------|------|------|------|
| **ทรงกระบอก (Cylinders)** | 0.0964 | 0.5565 | 0.6733 | 2.7184 |
| **แผ่นดิสก์ (Disks)** | 0.1115 | 0.6991 | 0.7166 | 2.0530 |
| **ทรงรี (Ellipsoids)** | *ขึ้นอยู่กับอัตราส่วนความยาว* | - | - | - |

---

## 9. พื้นผิวที่เปลี่ยนรูปได้ (Deformable Interfaces)

### การประมาณค่า Grace (Grace Correlation)

**สำหรับฟองในของเหลว**:

$$C_D = \max\left[\frac{2}{\sqrt{Re_p}}, \min\left(\frac{8}{3}\frac{Eo}{Eo + 4}, 0.44\right)\right]$$

### การประมาณค่า Tomiyama (Tomiyama Correlation)

**สำหรับฟองที่มีการปนเปื้อน**:

$$C_D = \max\left[0.44, \min\left(\frac{24}{Re_p}(1 + 0.15 Re_p^{0.687}), \frac{72}{Re_p}\right)\right]$$

---

## 10. การตั้งค่าใน `constant/phaseProperties`

ผู้ใช้สามารถเลือกโมเดลได้ง่ายๆ ดังนี้:

```cpp
drag
(
    (air in water)
    {
        type            SchillerNaumann;
    }
    (oil in water)
    {
        type            IshiiZuber;
    }
);
```

การนำไปใช้ที่มีความยืดหยุ่นสูงนี้ช่วยให้ OpenFOAM สามารถจำลองระบบที่มีหลายเฟสและหลายคู่ปฏิสัมพันธ์ได้อย่างมีประสิทธิภาพ

### การตั้งค่า Under-Relaxation ใน `system/fvSolution`

```cpp
relaxationFactors
{
    equations
    {
        U           0.7;      // การผ่อนคลายความเร็ว
        p           0.3;      // การผ่อนคลายความดัน
        k           0.6;      // การผ่อนคลายพลังงานความวุ่นวาย
        epsilon     0.5;      // การผ่อนคลายอัตราการสลายตัว
    }

    fields
    {
        "alpha.*"   0.4;      // การผ่อนคลายส่วนประกอบเฟส
    }
}
```

---

## 11. สรุปและข้อควรพิจารณา (Summary and Considerations)

### การเลือก Drag Model ที่เหมาะสม

| Drag Model | ชนิดของการไหลที่เหมาะสม | ข้อดี | ข้อจำกัด |
|-----------|-------------------|--------|-----------|
| **Schiller-Naumann** | อนุภาคทรงกลมทั่วไป | ใช้ง่าย, เสถียร | ไม่เหมาะกับอนุภาคที่เปลี่ยนรูป |
| **Ishii-Zuber** | การไหลมีฟอง, ฟองบิดเบี้ยว | รองรับพื้นผิวที่เปลี่ยนรูป | ซับซ้อนกว่า |
| **Morsi-Alexander** | ช่วง Reynolds number กว้าง | ความแม่นยำสูง | ซับซ้อน, ต้องการพารามิเตอร์มาก |
| **Syamlal-O'Brien** | เตียงของไหล, อนุภาคหนาแน่น | เหมาะกับสารแขวนลอยหนาแน่น | จำกัดสำหรับการไหลแบบอื่น |
| **Tomiyama** | ฟองที่มีการปนเปื้อน | คำนึงถึงผลของ surfactant | จำกัดสำหรับ gas-liquid systems |

### ข้อควรพิจารณาด้านเสถียรภาพ

1. **ความเสถียรเชิงตัวเลข (Numerical Stability)**:
   - เทอมแรงฉุดสามารถสร้างสมการที่แข็ง (stiff equations)
   - ต้องการการจัดการแบบอิมพลิซิต (implicit treatment)
   - การใช้ค่าเวลา (time step) ที่เล็กเกินไปอาจทำให้เกิดปัญหาการบิดเบือน (numerical diffusion)

2. **ขีดจำกัดของสัดส่วนเฟส (Phase Fraction Limits)**:
   - สัดส่วนเฟสที่ใกล้ศูนย์สามารถก่อให้เกิดปัญหาเชิงตัวเลขได้
   - การใช้ค่าความหนาแน่นขั้นต่ำ (minimum clipping) และการทำให้เรียบ (smoothing)
   - ค่าแนะนำ: $\alpha_{min} = 1 \times 10^{-6}$

3. **ความละเอียดของ Mesh (Mesh Resolution)**:
   - ต้องการความละเอียดที่เพียงพอเพื่อจับปรากฏการณ์ที่พื้นผิวสัมผัส
   - กฎทั่วไป: อย่างน้อย 10-20 cells ต่อเส้นผ่านศูนย์กลางอนุภาค
   - พิจารณา: การใช้ adaptive mesh refinement (AMR) สำหรับบริเวณที่มี gradient สูง

### ขั้นตอนการเลือกแบบจำลองแรงฉุด

```mermaid
flowchart TD
    A[เริ่มต้น: วิเคราะห์ปัญหา] --> B{ชนิดของอนุภาค?}
    B -->|ทรงกลม| C{Reynolds number?}
    B -->|ไม่สมมาตร| D[ใช้ Haider-Levenspiel]
    B -->|เปลี่ยนรูปได้| E{ระบบ?}

    C -->|Re &lt; 1000| F[Schiller-Naumann]
    C -->|Re &gt; 1000| F

    E -->|Gas-Liquid| G{ฟองสะอาดหรือปนเปื้อน?}
    E -->|เตียงของไหล| H[Syamlal-O'Brien]

    G -->|สะอาด| I[Grace/Ishii-Zuber]
    G -->|ปนเปื้อน| J[Tomiyama]

    F --> K{ความเข้มข้น?}
    K -->|สูง| L[เพิ่ม Hindered Settling]
    K -->|ต่ำ| M[ใช้โมเดลพื้นฐาน]

    D --> N[ตั้งค่า Shape Factor]
    H --> O[เพิ่ม Dense Suspension Effects]
    L --> O

    M --> P[ตั้งค่าใน phaseProperties]
    N --> P
    O --> P
    I --> P
    J --> P

    P --> Q[ตั้งค่า Under-Relaxation]
    Q --> R[ทดสอบและตรวจสอบ]
```

---

## 12. แหล่งอ้างอิงและการตรวจสอบความถูกต้อง (References and Validation)

### กรณีทดสอบมาตรฐาน (Benchmark Cases)

1. **การตกตะกอนของอนุภาคเดี่ยว**: เปรียบเทียบกับผลเฉลยเชิงวิเคราะห์ (analytical solutions)
2. **การทดลองเตียงของไหล**: ความเร็วขั้นต่ำของการไหล (minimum fluidization velocity)
3. **การวัดผลในคอลัมน์ฟอง**: ความสัมพันธ์ของความเร็วในการลอยขึ้น (rise velocity correlations)
4. **การไหลในท่อ**: การทำนายความดันตก (pressure drop predictions)

### เทคนิคการวัดที่ใช้เปรียบเทียบ

- Electrical Resistance Tomography (ERT)
- Particle Image Velocimetry (PIV)
- Laser Doppler Anemometry (LDA)

การทำความเข้าใจและการนำไปใช้ Drag Model ใน OpenFOAM เป็นสิ่งสำคัญ สำหรับการทำนายการไหลแบบ multiphase ที่แม่นยำ และเป็นรากฐานสำหรับการศึกษาปรากฏการณ์ระหว่างเฟสที่ซับซ้อนยิ่งขึ้น
