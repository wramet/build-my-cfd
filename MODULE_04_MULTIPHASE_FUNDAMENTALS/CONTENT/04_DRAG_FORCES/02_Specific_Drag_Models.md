# แบบจำลองแรงลากเฉพาะ (Specific Drag Models)

## บทนำ (Introduction)

**แบบจำลองแรงลาก (Drag models)** เป็นความสัมพันธ์เชิงประจักษ์ (empirical correlations) ที่ใช้คำนวณสัมประสิทธิ์แรงลาก $C_D$ เพื่อทำนายการแลกเปลี่ยนโมเมนตัมระหว่างเฟสในระบบ multiphase flow การเลือกแบบจำลองที่เหมาะสมขึ้นอยู่กับ:

- ชนิดของอนุภาค/ฟองอากาศ (particle/bubble type)
- เลขเรย์โนลด์ของอนุภาค ($Re_p$)
- ความเข้มข้นของเฟสกระจาย ($\alpha_d$)
- คุณสมบัติทางฟิสิกส์ของพื้นผิว (surface properties)

> [!INFO] หมายเหตุสำคัญ
> แบบจำลองแรงลากที่แตกต่างกันถูกพัฒนาขึ้นสำหรับระบอบการไหลที่เฉพาะเจาะจง การเลือกโมเดลที่ไม่เหมาะสมอาจนำไปสู่ความคลาดเคลื่อนในการทำนายที่มีนัยสำคัญ

---

## แบบจำลองสำหรับอนุภาคทรงกลม (Spherical Particle Models)

### Schiller-Naumann Model

**แบบจำลองแรงลากที่ใช้กันอย่างแพร่หลายที่สุดใน OpenFOAM** โดยเฉพาะอย่างยิ่งสำหรับอนุภาคทรงกลมในทั้ง laminar และ turbulent regimes

#### หลักการทำงาน
โมเดลนี้ให้การเปลี่ยนผ่านที่ราบรื่นระหว่างช่วง low และ high Reynolds number โดยการรวม **Stokes drag correction** เข้ากับค่า drag coefficient คงที่สำหรับ turbulent flows

#### สมการ Drag Coefficient
Drag coefficient $C_D$ ขึ้นอยู่กับ particle Reynolds number $Re_p$:

$$C_D = \begin{cases}
\frac{24}{Re_p}(1 + 0.15 Re_p^{0.687}) & Re_p < 1000 \\
0.44 & Re_p \geq 1000
\end{cases} \tag{1}$$

**ความหมายของตัวแปร:**
- $C_D$ = drag coefficient (ไม่มีหน่วย)
- $Re_p$ = particle Reynolds number (ไม่มีหน่วย)

#### การทำงานในแต่ละช่วง

**Low Reynolds Numbers ($Re_p < 1$)**:
- โมเดลจะลดรูปเป็น **Stokes drag law**: $C_D = 24/Re_p$
- เหมาะสำหรับ creeping flow

**Intermediate Reynolds Numbers**:
- เทอม **Schiller-Naumann correction**: $(1 + 0.15 Re_p^{0.687})$
- คำนึงถึงความเบี่ยงเบนจาก Stokes flow อันเนื่องมาจากผลของแรงเฉื่อย

**High Reynolds Numbers ($Re_p \geq 1000$)**:
- Drag coefficient เข้าใกล้ค่าคงที่ **0.44**
- ค่าทั่วไปสำหรับ turbulent flow รอบทรงกลม
- **Pressure drag** มีอิทธิพลหลัก

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
        // Access Reynolds number field from phase pair
        const volScalarField& Re = pair_.Re();

        // Create new drag coefficient field
        return volScalarField::New
        (
            "Cd",
            max
            (
                // Low to intermediate Re regime with correction
                24.0/Re*(1.0 + 0.15*pow(Re, 0.687)),
                // High Re regime - constant drag
                0.44
            )
        );
    }
};
```

📂 **Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C`

#### รายละเอียดการ Implement:

**Source Explanation:** โค้ดนี้แสดงการ implement แบบจำลอง Schiller-Naumann ใน OpenFOAM ซึ่งเป็นส่วนหนึ่งของระบบโอนย้ายโมเมนตัมระหว่างเฟสใน solver `multiphaseEulerFoam` คลาส `SchillerNaumann` สืบทอดจาก `dragModel` ฐานและแทนที่เมธอด `Cd()` สำหรับคำนวณสัมประสิทธิ์แรงลาก

**Key Concepts:**
- `tmp<volScalarField>` = กลยุทธ์การจัดการหน่วยความจำสำหรับ temporary fields
- `pair_.Re()` = เข้าถึง Reynolds number field จาก phase pair
- `volScalarField::New` = สร้าง field ใหม่พร้อมการจัดการหน่วยความจำอัตโนมัติ
- `max` function = ให้มั่นใจว่ามีการเปลี่ยนผ่านที่ราบรื่นระหว่างสอง regime
- `pow(Re, 0.687)` = คำนวณ exponent ของ Reynolds number อย่างมีประสิทธิภาพ

---

### Morsi-Alexander Model

**Morsi-Alexander model** เป็นหนึ่งใน drag correlations ที่ครอบคลุมมากที่สุด โดยแบ่งช่วงของ Reynolds number ออกเป็นห้า distinct regions

#### หลักการทำงาน
แนวทางแบบ **piecewise** ให้ความแม่นยำสูงในสภาวะการไหลที่หลากหลาย

#### สมการทั่วไป
$$C_D = \sum_{i=1}^{5} a_i Re_p^{b_i} \tag{2}$$

#### 5 ช่วงของ Reynolds Number

| ช่วง | ขอบเขต Reynolds number | ลักษณะการไหล | Coefficients |
|-------|--------------------------|----------------|---------------|
| 1 | $0 < Re_p \leq 0.1$ | Creeping flow | $(a_1, b_1)$ |
| 2 | $0.1 < Re_p \leq 1000$ | Laminar transition | $(a_2, b_2)$ |
| 3 | $1000 < Re_p \leq 5 \times 10^3$ | Early turbulent | $(a_3, b_3)$ |
| 4 | $5 \times 10^3 < Re_p \leq 10^4$ | Turbulent developing | $(a_4, b_4)$ |
| 5 | $10^4 < Re_p \leq 10^5$ | Fully turbulent | $(a_5, b_5)$ |

#### ข้อดีและข้อเสีย

**ข้อดี:**
- **ความแม่นยำสูง** ในทุกช่วง Reynolds number
- สามารถแสดงลักษณะของ drag ใน flow regimes ที่แตกต่างกันได้อย่างละเอียด
- เหมาะสำหรับ **creeping flow** ไปจนถึง **highly turbulent flows**

**ข้อเสีย:**
- **ความไม่ต่อเนื่อง** ที่ขอบเขตของแต่ละช่วงอาจก่อให้เกิดปัญหาทางตัวเลข
- ต้องการ **smoothing** ที่เหมาะสมในการ implement
- ซับซ้อนกว่าโมเดลอื่น

---

## แบบจำลองสำหรับฟองอากาศและหยดของเหลว (Bubbles & Droplets)

ในระบบ Gas-Liquid พื้นผิวรอยต่อสามารถเปลี่ยนรูปได้ (Deformable interfaces) แรงลากจึงขึ้นอยู่กับ **Eötvös Number ($Eo$)** ซึ่งแสดงอัตราส่วนของแรงลอยตัวต่อแรงตึงผิว

### Ishii-Zuber Model

**Ishii-Zuber model** ถูกพัฒนาขึ้นมาโดยเฉพาะสำหรับ multiphase flows ที่เกี่ยวข้องกับ **distorted bubbles** และ **droplets** ทำให้เหมาะอย่างยิ่งสำหรับระบบ gas-liquid

#### หลักการทำงาน
โมเดลนี้คำนึงถึงการเปลี่ยนผ่านระหว่าง **spherical bubbles** และ **distorted/slug flow regimes**

#### สมการ Drag Coefficient
$$C_D = \begin{cases}
\frac{24}{Re_p}(1 + 0.1 Re_p^{0.75}) & Re_p < 1000 \\
\frac{8}{3}\frac{Eo}{Eo + 4} & \text{Distorted regime}
\end{cases} \tag{3}$$

**ความหมายของตัวแปร:**
- $C_D$ = drag coefficient (ไม่มีหน่วย)
- $Re_p$ = particle Reynolds number (ไม่มีหน่วย)
- $Eo$ = Eötvös number (ไม่มีหน่วย)

#### Eötvös Number (Eo)
ใน distorted regime จะมีการใช้ **Eötvös number**:

$$Eo = \frac{g(\rho_c - \rho_d)d^2}{\sigma} \tag{4}$$

**ความหมายของตัวแปร:**
- $g$ = gravitational acceleration (m/s²)
- $\rho_c$ = density ของ continuous phase (kg/m³)
- $\rho_d$ = density ของ dispersed phase (kg/m³)
- $d$ = characteristic particle/bubble diameter (m)
- $\sigma$ = surface tension (N/m)

#### การทำงานของโมเดล

**Low Reynolds Number Region:**
- ใช้ **modified Stokes correlation** พร้อม exponent 0.75
- แตกต่างจาก 0.687 ของ Schiller-Naumann
- สะท้อนถึง flow physics ที่แตกต่างกันในระบบ multiphase

**Distorted Regime:**
- **Eötvös number** แสดงถึงอัตราส่วนของ buoyancy forces ต่อ surface tension forces
- บ่งชี้ว่าเมื่อใดที่การเปลี่ยนรูปของฟองอากาศมีความสำคัญ
- เทอม $\frac{8}{3}\frac{Eo}{Eo + 4}$ ให้การเปลี่ยนผ่านที่ราบรื่น:
  - **Low $Eo$**: viscous-dominated drag
  - **High $Eo$**: deformation-dominated drag

---

### Grace Correlation

**ใช้สำหรับ**: ฟองอากาศในของเหลว (bubbles in liquids)

**สมการ drag coefficient**:
$$C_D = \max\left[\frac{2}{\sqrt{Re_p}}, \min\left(\frac{8}{3}\frac{Eo}{Eo + 4}, 0.44\right)\right] \tag{5}$$

**ตัวแปรในสมการ**:
- `$C_D$` = Drag coefficient
- `$Re_p$` = Reynolds number ของ particle
- `$Eo$` = Eötvös number

---

### Tomiyama Correlation

**ใช้สำหรับ**: ฟองอากาศที่มีการปนเปื้อน (contaminated bubbles)

**สมการ drag coefficient**:
$$C_D = \max\left[0.44, \min\left(\frac{24}{Re_p}(1 + 0.15 Re_p^{0.687}), \frac{72}{Re_p}\right)\right] \tag{6}$$

**ตัวแปรในสมการ**:
- `$C_D$` = Drag coefficient
- `$Re_p$` = Reynolds number ของ particle

---

## แบบจำลองสำหรับอนุภาคความเข้มข้นสูง (Dense Suspensions)

เมื่อ $\alpha_d > 0.1$ การปฏิสัมพันธ์ระหว่างอนุภาค (Crowding effect) จะทำให้แรงลากเพิ่มขึ้น ปรากฏการณ์นี้เรียกว่า **Hindered Settling**

### ปรากฎการณ์การตกตะกอนแบบถูกขัดขวาง (Hindered Settling)

เมื่อมีอนุภาคในความเข้มข้นสูง ความเร็วในการตกตะกอนของอนุภาคจะลดลงอย่างมีนัยสำคัญเมื่อเทียบกับพฤติกรรมของอนุภาคเดี่ยว

**กลไกทางฟิสิกส์:**

1. **การรบกวนของ Wake (Wake Interference)**
   - บริเวณ Wake ด้านหลังอนุภาคจะซ้อนทับและรบกวนซึ่งกันและกัน
   - การรบกวนนี้จะลดความแตกต่างของความดันระหว่างด้านหน้าและด้านหลังของอนุภาคแต่ละตัว
   - ผลลัพธ์: แรงลากลดลงอย่างมีประสิทธิภาพ

2. **การแทนที่ของโฟลว์ย้อนกลับ (Return Flow Displacement)**
   - ขณะที่อนุภาคตกตะกอนผ่านเฟสต่อเนื่อง อนุภาคจะแทนที่ของไหลที่ต้องไหลอ้อมอนุภาค
   - ในสารแขวนลอยที่มีความเข้มข้นสูง โฟลว์ย้อนกลับนี้จะถูกจำกัดด้วยการมีอยู่ของอนุภาคข้างเคียง
   - ผลกระทบ: ของไหลจะต้องเร่งความเร็วผ่านช่องว่างที่แคบลงระหว่างอนุภาค เกิดแรงต้านทานเพิ่มเติมต่อการตกตะกอน

3. **การเพิ่มขึ้นของความหนืดปรากฏ (Apparent Viscosity Enhancement)**
   - การมีอยู่ของอนุภาคที่กระจายตัวจะเพิ่มความหนืดประสิทธิผลของสารแขวนลอย
   - สมการความหนืดปรากฏ: $\mu_{app} = \mu_c \cdot \phi(\alpha_d)$
   - โดยที่ $\phi(\alpha_d)$ คือ ฟังก์ชันที่ขึ้นอยู่กับความเข้มข้นซึ่งมีค่ามากกว่าหนึ่งสำหรับ $\alpha_d > 0$

---

### ความสัมพันธ์แบบ Richardson-Zaki

**ความสัมพันธ์เชิงประจักษ์** ที่ใช้กันอย่างแพร่หลายที่สุดสำหรับการตกตะกอนแบบถูกขัดขวาง:

$$v_t = v_{t,0} \cdot (1 - \alpha_d)^n \tag{7}$$

**นิยามตัวแปร**:
- $v_t$ คือ ความเร็วในการตกตะกอนแบบถูกขัดขวาง
- $v_{t,0}$ คือ ความเร็วสุดท้ายของอนุภาคเดี่ยวในตัวกลางที่ไม่มีที่สิ้นสุด
- $\alpha_d$ คือ เศษส่วนปริมาตรของเฟสที่กระจายตัว
- $n$ คือ เลขชี้กำลัง Richardson-Zaki

#### ค่าเลขชี้กำลัง n ตาม Reynolds number

| ช่วง Reynolds number ($Re_p$) | เลขชี้กำลัง n | สภาวะโฟลว์ |
|-------------------------------|------------------|----------------|
| $Re_p < 0.2$ | $n = 4.65$ | Stokes regime |
| $0.2 < Re_p < 1.0$ | $n = 4.35 \cdot Re_p^{-0.03}$ | Intermediate regime |
| $1.0 < Re_p < 500$ | $n = 4.45 \cdot Re_p^{-0.1}$ | Transition regime |
| $Re_p > 500$ | $n = 2.39$ | Newton regime |

---

### Syamlal-O'Brien Model

**Syamlal-O'Brien model** ถูกพัฒนาขึ้นมาโดยเฉพาะสำหรับ **fluidized bed applications** ซึ่งการมีปฏิสัมพันธ์ระหว่างอนุภาคและผลกระทบของ dense phase มีอิทธิพลอย่างมาก

#### หลักการทำงานที่แตกต่าง
โมเดลนี้มีแนวทางที่แตกต่าง โดยการเชื่อมโยง drag coefficient กับอัตราส่วนของ relative velocity ต่อ terminal settling velocity

#### สมการหลัก
$$C_D = \frac{v_r^2}{v_s^2} \tag{8}$$

**ความหมายของตัวแปร:**
- $C_D$ = drag coefficient (ไม่มีหน่วย)
- $v_r$ = relative velocity ระหว่าง phases (m/s)
- $v_s$ = terminal settling velocity ของอนุภาคเดี่ยว (m/s)

#### Terminal Settling Velocity
$$v_s = 0.5 \left[ A - 0.06 Re_p + \sqrt{(0.06 Re_p)^2 + 0.12 Re_p (2B - A) + A^2} \right] \tag{9}$$

**ความหมายของตัวแปรเพิ่มเติม:**
- $A$ และ $B$ = ฟังก์ชันของ particle Reynolds number และ concentration
- $Re_p$ = particle Reynolds number (ไม่มีหน่วย)

#### ประโยชน์เด่น

**การจับผลกระทบของ Particle Concentration:**
- สูตรโดยธรรมชาติจับผลกระทบของ **particle concentration** ต่อ drag
- เหมาะอย่างยิ่งสำหรับ **dense particulate flows**
- **Traditional single-particle drag correlations** ไม่สามารถใช้งานได้

**การเปลี่ยนผ่านที่ราบรื่น:**
- เปลี่ยนผ่านระหว่าง **dilute** และ **dense phase regimes** ได้อย่างเป็นธรรมชาติ
- **ไม่จำเป็นต้องใช้ explicit regime switching logic**

---

### การนำไปใช้ใน OpenFOAM

ใน Solver `multiphaseEulerFoam` ของ OpenFOAM ผลกระทบของสารแขวนลอยความเข้มข้นสูงจะถูกรวมเข้าไว้ด้วยกันผ่านการปรับปรุงค่าสัมประสิทธิ์การแลกเปลี่ยนโมเมนตัม $\mathbf{K}_{kl}$ ระหว่างเฟส:

$$\mathbf{K}_{kl}^{modified} = \mathbf{K}_{kl} \cdot f(\alpha_l) \tag{10}$$

**นิยามตัวแปร**:
- $\mathbf{K}_{kl}^{modified}$ คือ ค่าสัมประสิทธิ์การแลกเปลี่ยนโมเมนตัมที่ปรับปรุงแล้ว
- $\mathbf{K}_{kl}$ คือ ค่าสัมประสิทธิ์การแลกเปลี่ยนโมเมนตัมพื้นฐาน
- $f(\alpha_l)$ คือ **ตัวประกอบการแก้ไขการตกตะกอนแบบถูกขัดขวาง**
- $\alpha_l$ คือ เศษส่วนปริมาตรของเฟสที่กระจายตัว

#### การแก้ไขความหนืดแบบ Einstein (Einstein Viscosity Correction)

**ความสัมพันธ์แบบ Einstein** ให้พื้นฐานทางทฤษฎีที่สำคัญสำหรับการเพิ่มขึ้นของความหนืดในสารแขวนลอยเจือจาง:

$$f(\alpha_l) = (1 - \alpha_d)^{2.5} \tag{11}$$

**ที่มาของเลขชี้กำลัง**: นิพจน์นี้สามารถหาได้จากสมการความหนืดแบบ Einstein สำหรับอนุภาคทรงกลมในของไหลแบบนิวตัน:

$$\mu_{app} = \mu_c (1 + 2.5\alpha_d + O(\alpha_d^2)) \tag{12}$$

---

#### ความสัมพันธ์แบบ Barnea-Mizrahi

**ความสัมพันธ์แบบ Barnea-Mizrahi** ให้คำอธิบายที่แม่นยำยิ่งขึ้นสำหรับความเข้มข้นของอนุภาคที่สูงขึ้น:

$$f(\alpha_l) = (1 - \alpha_d)^{2.0} \cdot \exp\left(\frac{2.5\alpha_d}{1 - \alpha_d}\right) \tag{13}$$

**ส่วนประกอบของสมการ:**

1. **พจน์พหุนาม** $(1 - \alpha_d)^{2.0}$:
   - คำนึงถึงความเร็วในการตกตะกอนที่ลดลง
   - อธิบายการลดลงของพื้นที่หลอกเลือด

2. **พจน์เอ็กซ์โพเนนเชียล**:
   - จับการเพิ่มขึ้นอย่างมากของแรงต้านทานเมื่อเข้าใกล้ขีดจำกัดการบรรจุสูงสุด

#### OpenFOAM Code Implementation

```cpp
// Drag model class implementation for hindered settling
virtual tmp<volScalarField> K(const phasePairKey& key) const
{
    // Access phase models from the phase pair
    const phaseModel& phase1 = this->phase1_;
    const phaseModel& phase2 = this->phase2_;

    // Calculate base drag coefficient
    const volScalarField K0 = this->K0(key);

    // Calculate hindered settling factor based on dispersed phase volume fraction
    const volScalarField alphaD = phase2;
    const volScalarField fHindered =
        (scalar(1) - alphaD) * exp(2.5*alphaD/(scalar(1) - alphaD));

    // Return modified drag coefficient accounting for particle crowding
    return K0 * fHindered;
}
```

📂 **Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C`

#### รายละเอียดการ Implement:

**Source Explanation:** โค้ดนี้แสดงการ implement ของแบบจำลองแรงลากที่มีการแก้ไขสำหรับการตกตะกอนแบบถูกขัดขวาง (hindered settling) ในระบบ OpenFOAM ฟังก์ชัน `K()` คำนวณค่าสัมประสิทธิ์การแลกเปลี่ยนโมเมนตัมระหว่างเฟสโดยคำนึงถึงผลของความเข้มข้นของอนุภาค ซึ่งเป็นส่วนสำคัญของระบบ MomentumTransferPhaseSystem ที่จัดการการโอนย้ายโมเมนตัมระหว่างเฟสทั้งหมด

**Key Concepts:**
- `phasePairKey` = คีย์ที่ระบุคู่เฟสที่มีปฏิสัมพันธ์กัน
- `K0(key)` = ค่าสัมประสิทธิ์แรงลากพื้นฐานโดยไม่มีผลของความเข้มข้น
- `alphaD` = เศษส่วนปริมาตรของเฟสกระจาย (dispersed phase)
- `fHindered` = ตัวประกอบการแก้ไขแบบ Barnea-Mizrahi สำหรับผลของความเข้มข้นสูง
- `exp()` = ฟังก์ชันเลขชี้กำลังธรรมชาติสำหรับจับผลของการอุดตันของอนุภาค

---

## แบบจำลองสำหรับอนุภาคที่ไม่ใช่ทรงกลม (Non-Spherical Particles)

สำหรับอนุภาคที่ไม่ใช่ทรงกลม ให้ใช้ **ตัวประกอบรูปร่าง** $\phi$:

$$\phi = \frac{\text{พื้นที่ผิวของทรงกลมที่มีปริมาตรเท่ากัน}}{\text{พื้นที่ผิวจริง}} \tag{14}$$

**ความหมายของสมการ:**
- **Shape factor** ($\phi$): ปริมาณที่ไม่มีหน่วยวัดความเบี่ยงเบนจากทรงกลม ($0 \leq \phi \leq 1$)
- **$\phi = 1$**: ทรงกลมที่สมบูรณ์แบบ
- **เส้นผ่านศูนย์กลางประสิทธิผล**:
  $$d_{eff} = d_v \phi^{0.5} \tag{15}$$
  - $d_v$ เส้นผ่านศูนย์กลางเทียบเท่าปริมาตร (volume-equivalent diameter)
  - $d_{eff}$ เส้นผ่านศูนย์กลางที่พิจารณาทั้งปริมาตรและรูปร่าง

---

### สมการ Haider-Levenspiel

$$C_D = \frac{24}{Re_p}(1 + a Re_p^b) + \frac{c}{1 + d/Re_p} \tag{16}$$

**ความหมายของสมการ:**
- **$C_D$**: Drag coefficient ที่ปรับปรุงสำหรับอนุภาคที่ไม่ใช่ทรงกลม
- **$Re_p$**: จำนวน Reynolds ของอนุภาค (Particle Reynolds Number)
- **$a, b, c, d$**: สัมประสิทธิ์ที่ขึ้นอยู่กับรูปร่างอนุภาค

จำนวน Reynolds ของอนุภาค:
$$Re_p = \frac{\rho_f \mathbf{u} \cdot d_{eff}}{\mu_f} \tag{17}$$

**ความหมายของตัวแปร:**
- **$\rho_f$**: ความหนาแน่นของของไหล
- **$\mu_f$**: ความหนืดพลวัต (dynamic viscosity) ของของไหล
- **$\mathbf{u}$**: ความเร็วสัมพัทธ์ระหว่างอนุภาคกับของไหล
- **$d_{eff}$**: เส้นผ่านศูนย์กลางประสิทธิผล

#### สัมประสิทธิ์สำหรับรูปร่างต่างๆ

| รูปร่างอนุภาค | $a$ | $b$ | $c$ | $d$ |
|----------------|------|------|------|------|
| **ทรงกระบอก (Cylinders)** | 0.0964 | 0.5565 | 0.6733 | 2.7184 |
| **แผ่นดิสก์ (Disks)** | 0.1115 | 0.6991 | 0.7166 | 2.0530 |
| **ทรงรี (Ellipsoids)** | *ขึ้นอยู่กับอัตราส่วนความยาว* | - | - | - |

#### OpenFOAM Code Implementation

```cpp
// Haider-Levenspiel drag model for non-spherical particles
// Calculate particle Reynolds number using effective diameter
scalar Re_p = rhoc_ * mag(particle.Urel()) * dEff / muc_;

// Initialize coefficients based on particle shape
scalar a, b, c, d;
if (particle.shape() == "cylinder")
{
    a = 0.0964; b = 0.5565; c = 0.6733; d = 2.7184;
}
else if (particle.shape() == "disk")
{
    a = 0.1115; b = 0.6991; c = 0.7166; d = 2.0530;
}
else // ellipsoid or other shapes
{
    // Coefficients depend on aspect ratio
    a = 0.0800; b = 0.5000; c = 0.6500; d = 2.5000;
}

// Calculate drag coefficient using Haider-Levenspiel correlation
scalar CD = 24.0/Re_p*(1 + a*pow(Re_p, b)) + c/(1 + d/Re_p);
```

📂 **Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C`

#### รายละเอียดการ Implement:

**Source Explanation:** โค้ดนี้แสดงการ implement ของแบบจำลอง Haider-Levenspiel สำหรับคำนวณสัมประสิทธิ์แรงลากของอนุภาคที่ไม่ใช่ทรงกลมใน OpenFOAM การ implement นี้เป็นส่วนขยายของระบบ drag model ที่รองรับรูปร่างที่หลากหลายของอนุภาค โดยใช้สัมประสิทธิ์ที่แตกต่างกันตามประเภทของรูปร่าง

**Key Concepts:**
- `rhoc_` = ความหนาแน่นของ continuous phase
- `particle.Urel()` = ความเร็วสัมพัทธ์ของอนุภาค
- `dEff` = เส้นผ่านศูนย์กลางประสิทธิผลที่คำนึงถึงรูปร่าง
- `muc_` = ความหนืดของ continuous phase
- `pow()` = ฟังก์ชันยกกำลังสำหรับคำนวณเทอม Reynolds number
- การเลือกสัมประสิทธิ์แบบมีเงื่อนไข = ปรับ drag coefficient ตามรูปร่างอนุภาค

---

## ตารางเปรียบเทียบแบบจำลองแรงลาก (Drag Model Comparison)

| แบบจำลอง | ชนิดของการไหลที่เหมาะสม | ข้อดี | ข้อจำกัด |
|-----------|-------------------|--------|-----------|
| **Schiller-Naumann** | อนุภาคทรงกลมทั่วไป | ใช้ง่าย, เสถียร, การเปลี่ยนผ่านราบรื่น | ไม่เหมาะกับอนุภาคที่เปลี่ยนรูป |
| **Ishii-Zuber** | การไหลมีฟอง, ฟองบิดเบี้ยว | รองรับพื้นผิวที่เปลี่ยนรูป, ความแม่นยำสูง | ซับซ้อนกว่า, ต้องการค่า surface tension |
| **Morsi-Alexander** | ช่วง Reynolds number กว้าง | ความแม่นยำสูงในทุกช่วง | ซับซ้อน, อาจมีความไม่ต่อเนื่องทางตัวเลข |
| **Syamlal-O'Brien** | เตียงของไหล, อนุภาคหนาแน่น | เหมาะกับสารแขวนลอยหนาแน่น, การตรวจสอบความถูกต้องครอบคลุม | จำกัดสำหรับการไหลแบบอื่น |
| **Haider-Levenspiel** | อนุภาคที่ไม่ใช่ทรงกลม | รองรับรูปร่างที่หลากหลาย | ต้องการข้อมูล shape factor |
| **Grace** | ฟองอากาศในของเหลว | จับผลของการเปลี่ยนรูปได้ดี | จำกัดสำหรับระบบ gas-liquid |
| **Tomiyama** | ฟองอากาศที่มีการปนเปื้อน | เหมาะสำหรับฟองที่มี surfactant | จำกัดสำหรับฟองที่มีการปนเปื้อน |

---

## แนวทางการเลือกแบบจำลอง (Model Selection Guidelines)

### เลือก Schiller-Naumann เมื่อ:

- **อนุภาคเป็นทรงกลม** (Spherical particles)
- **Reynolds number ปานกลาง** (Moderate $Re_p$)
- **การไหลแบบ multiphase ทั่วไป** (General multiphase flow)
- **ระบบการเผาไหม้แบบละออง** (Spray combustion systems)
- **เจ็ตที่มีอนุภาค** (Particle-laden jets)
- **การขนส่งตะกอน** (Sediment transport)
- **ตัวแยกแบบไซโคลน** (Cyclone separators)

> [!TIP] ข้อได้เปรียบเชิงตัวเลข
> - การเปลี่ยนผ่านที่ราบรื่นระหว่างช่วงต่างๆ โดยไม่มีความไม่ต่อเนื่องเชิงตัวเลข
> - ประสิทธิภาพเชิงคำนวณ (computationally efficient)
> - ความเสถียร (robust) สำหรับการประยุกต์ใช้งานทางวิศวกรรมส่วนใหญ่

---

### เลือก Ishii-Zuber เมื่อ:

- **การไหลแบบมีฟองหรือแบบลูกทุ่ง** (Bubbly or slug flow)
- **พื้นผิวที่เปลี่ยนรูป** (Deformable interfaces)
- **Eötvös number สูง** ($Eo > 1$)
- **เครื่องปฏิกรณ์แบบ Bubble column** (Bubble column reactors)
- **ตัวแยกแก๊ส-ของเหลว** (Gas-liquid separators)
- **การไหลขณะเดือด** (Boiling flows)
- **การไหลแบบ Slug** (Slug flow)

> [!INFO] ฟิสิกส์ของอินเทอร์เฟซ
> ความสัมพันธ์นี้จับการเปลี่ยนผ่านจากฟองอากาศทรงกลมที่ถูกควบคุมโดยแรงหนืด ไปสู่ฟองอากาศที่เสียรูปซึ่งถูกควบคุมโดยแรงเฉื่อย และสุดท้ายคือฟองอากาศรูปหมวกที่ถูกควบคุมโดยแรงตึงผิว

---

### เลือก Syamlal-O'Brien เมื่อ:

- **เตียงของไหล** (Fluidized beds)
- **สารแขวนลอยอนุภาคหนาแน่น** (Dense particulate suspensions)
- **การไหลแบบเม็ด** (Granular flow) มีนัยสำคัญ
- **เตาเผาแบบ Circulating Fluidized Bed** (Circulating fluidized bed combustors)
- **การลำเลียงด้วยลม** (Pneumatic conveying)
- **เครื่องปฏิกรณ์แบบ Fluidized bed** (Fluidized bed reactors)

> [!TIP] การจับคู่หลายเฟส (Multiphase Coupling)
> ความสัมพันธ์นี้แสดงถึงแรงฉุดที่เพิ่มขึ้นเนื่องจากผลของความหนาแน่นของอนุภาค (particle crowding effects)

---

## การวิเคราะห์พารามิเตอร์ไร้มิติ (Dimensionless Parameter Analysis)

### 1. Particle Reynolds Number ($Re_p$)

| ค่า | การแนะนำ | โมเดลที่เหมาะสม |
|------|-------------|---------------|
| $Re_p < 1$ | การไหลแบบคลาน | Schiller-Naumann หรือ Stokes law |
| $1 < Re_p < 100$ | ช่วงกลาง | Schiller-Naumann พร้อมการแก้ไขอินเทอร์เฟซ |
| $Re_p > 1000$ | การไหลความเร็วสูง | Ishii-Zuber สำหรับอินเทอร์เฟซที่เสียรูปได้ |

---

### 2. Eötvös Number ($Eo$)

| ค่า | ผลของแรงตึงผิว | โมเดลที่เหมาะสม |
|------|-------------------|---------------|
| $Eo < 1$ | แรงตึงผิวมีอิทธิพลเหนือกว่า | Schiller-Naumann |
| $1 < Eo < 40$ | การเสียรูปปานกลาง | Ishii-Zuber |
| $Eo > 40$ | การเสียรูปอย่างมีนัยสำคัญ | Ishii-Zuber, Grace |

---

### 3. Void Fraction ($\alpha_d$)

| ค่า | ความเข้มข้นของอนุภาค | โมเดลที่เหมาะสม |
|------|---------------------|---------------|
| $\alpha_d < 0.1$ | การแขวนลอยเจือจาง | Schiller-Naumann |
| $0.1 < \alpha_d < 0.4$ | ความเข้มข้นปานกลาง | Ishii-Zuber, Richardson-Zaki correction |
| $\alpha_d > 0.4$ | การแขวนลอยหนาแน่น | Syamlal-O'Brien, Barnea-Mizrahi |

---

## ข้อควรพิจารณาเชิงคำนวณ (Computational Considerations)

| ปัจจัย | โมเดลที่ดีที่สุด | เหตุผล |
|---------|------------------|---------|
| **การลู่เข้า (Convergence)** | Schiller-Naumann | ความเสถียรเชิงตัวเลขที่ดีที่สุด |
| **ความแม่นยำ (Accuracy)** | Ishii-Zuber | ความแม่นยำของฟิสิกส์อินเทอร์เฟซที่ดีที่สุด |
| **การตรวจสอบความถูกต้อง (Validation)** | Syamlal-O'Brien | การตรวจสอบความถูกต้องเชิงประจักษ์ที่ครอบคลุมที่สุดสำหรับระบบหนาแน่น |
| **เฉพาะเจาะจงกับการประยุกต์ใช้งาน (Application-specific)** | ขึ้นอยู่กับกรณี | เลือกตามปรากฏการณ์ทางกายฟิสิกส์ที่มีอิทธิพลเหนือกว่า |

---

## สรุป (Summary)

**แบบจำลองแรงลากที่หลากหลาย** ถูกพัฒนาขึ้นเพื่อจัดการกับระบอบการไหลและเงื่อนไขทางฟิสิกส์ที่แตกต่างกัน:

1. **Schiller-Naumann**: มาตรฐานสากลสำหรับอนุภาคทรงกลม ครอบคลุมช่วง Reynolds number ที่กว้าง
2. **Ishii-Zuber**: เหมาะสำหรับฟองอากาศและหยดที่เปลี่ยนรูป คำนึงถึงผลของ surface tension
3. **Syamlal-O'Brien**: ออกแบบมาสำหรับระบบหนาแน่น เช่น fluidized beds
4. **Morsi-Alexander**: ให้ความแม่นยำสูงผ่านการแบ่งช่วงหลายช่วง
5. **Haider-Levenspiel**: ขยายผลไปยังอนุภาคที่ไม่ใช่ทรงกลมผ่าน shape factors
6. **Grace และ Tomiyama**: เฉพาะทางสำหรับฟองอากาศในระบบ gas-liquid

**การเลือกแบบจำลองที่เหมาะสม** ต้องพิจารณา:
- ลักษณะทางฟิสิกส์ของเฟส (physical phase characteristics)
- ความเข้มข้นของอนุภาค (particle concentration)
- ความเร็วและความหนืดของการไหล (flow velocity and viscosity)
- คุณสมบัติของพื้นผิว (surface properties)

> [!WARNING] คำเตือนสำคัญ
> การเลือกควรได้รับการตรวจสอบความถูกต้องเสมอเมื่อเทียบกับข้อมูลจากการทดลองหรือผลเฉลยเชิงวิเคราะห์เมื่อมีอยู่ โดยเข้าใจว่าความสัมพันธ์แรงลากเป็นแหล่งความไม่แน่นอนที่ใหญ่ที่สุดในการทำนายการไหลแบบหลายเฟสแบบ Eulerian