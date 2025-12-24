# 3.2.4 การกระจายตัวเนื่องจากความปั่นป่วน (Turbulent Dispersion)

> [!INFO] **ภาพรวา**
> **การกระจายตัวเนื่องจากความปั่นป่วน (Turbulent dispersion)** เป็นปรากฏการณ์ที่สำคัญในกระแสการไหลแบบหลายเฟส (multiphase flows) ซึ่งอธิบายถึงการกระจายตัวของอนุภาค (particles), ละออง (droplets) หรือฟอง (bubbles) อันเนื่องมาจากความผันผวนของความปั่นป่วน (turbulent fluctuations) ในเฟสต่อเนื่อง (continuous phase)

---

## ความสำคัญและขอบเขต (Importance and Scope)

ใน OpenFOAM โมเดลการกระจายตัวเนื่องจากความปั่นป่วนมีความจำเป็นอย่างยิ่งในการทำนายพฤติกรรมของกระแสการไหลที่มีเฟสกระจายตัว (dispersed phase flows) เช่น:

| การประยุกต์ใช้ | ความสำคัญของ Turbulent Dispersion |
|--------------|--------------------------------------|
| **กระแสที่มีอนุภาคเกาะอยู่** (Particle-laden flows) | ป้องกันการสะสมอนุภาคที่ไม่สมจริงในบริเวณที่มีความเร็วต่ำ |
| **ละออง** (Sprays) | ควบคุมวิถีของละอองและการพัฒนาของมุมกรวยละออง |
| **การไหลแบบมีฟอง** (Bubbly flows) | ทำนายการกระจายตัวของฟองในชั้นเฉือนความปั่นป่วนและการกระจายตัวของเศษส่วนปริมาตรแก๊สในท่อ |
| **เครื่องปฏิกรณ์เคมี** | การกระจายตัวของตัวเร่งปฏิกิริยาและประสิทธิภาพการผสม |
| **การเผาไหม้แบบพ่นฝอย** | ส่งผลต่อประสิทธิภาพการเผาไหม้และกระบวนการผสม |

---

## กลไกทางกายภาพ (Physical Mechanism)

### หลักการพื้นฐาน

**การกระจายตัวเนื่องจากความปั่นป่วน** เกิดจากการสัมพันธ์กันระหว่าง:

1. **ความผันผวนของความเร็วเนื่องจากความปั่นป่วน** (turbulent velocity fluctuations)
2. **การกระจายตัวของเศษส่วนปริมาตร** (volume fraction distribution) ของเฟสกระจายตัว

ปรากฏการณ์นี้เกิดขึ้นเนื่องจาก **กระแสหมุนวนเนื่องจากความปั่นป่วน (turbulent eddies)** ในเฟสต่อเนื่องทำให้เกิดการเบี่ยงเบนของอนุภาคกระจายตัวออกจากเส้นทางเฉลี่ย (mean trajectories) นำไปสู่การผสมและการกระจายตัวที่เพิ่มขึ้น

### การแยกส่วน Reynolds (Reynolds Decomposition)

ในสภาวะการไหลแบบปั่นป่วน ความเร็วสามารถแยกออกเป็นส่วนเฉลี่ยและส่วนผันผวนได้ดังนี้:

$$\mathbf{u}_c = \overline{\mathbf{u}}_c + \mathbf{u}'_c$$

โดยที่:
- $\overline{\mathbf{u}}_c$ คือ ความเร็วเฉลี่ย (mean velocity)
- $\mathbf{u}'_c$ คือ ความเร็วผันผวน (fluctuating velocity) โดยมีเงื่อนไข $\overline{\mathbf{u}'_c} = 0$

### การตอบสนองของอนุภาค: Stokes Number

พารามิเตอร์ไร้มิติหลักที่ควบคุมการตอบสนองของอนุภาคต่อความปั่นป่วนคือ **Stokes number**:

$$St = \frac{\tau_p}{\tau_t}$$

โดยที่:
- **เวลาตอบสนองของอนุภาค** (Particle response time): $\tau_p = \frac{\rho_p d_p^2}{18\mu_c}$
- **สเกลเวลาของความปั่นป่วน** (Turbulent time scale): $\tau_t = \frac{k}{\varepsilon}$

> [!TIP] **ความหมายของ Stokes Number**
> - **$St \ll 1$**: อนุภาคติดตามความผันผวนของความปั่นป่วนอย่างใกล้ชิด → การกระจายตัวถูกควบคุมโดยสภาวะปั่นป่วน
> - **$St \gg 1$**: อนุภาคไม่ไวต่อความผันผวนของความปั่นป่วน → การกระจายตัวถูกจำกัดโดยความเฉื่อย

### แรงกระจายตัวเนื่องจากความปั่นป่วน (Turbulent Dispersion Force)

ใน **กรอบการทำงานแบบ Eulerian-Eulerian** แรงกระจายตัวเนื่องจากความปั่นป่วนส่งผลต่อการแลกเปลี่ยนโมเมนตัมระหว่างเฟสผ่านเทอมการถ่ายโอนระหว่างรอยต่อ (interfacial transfer terms)

$$\mathbf{F}_{TD} = -\overline{\alpha_d' \rho_d \mathbf{u}_d'}$$

ซึ่งแสดงถึงการถ่ายโอนโมเมนตัมสุทธิที่เกิดจากการปฏิสัมพันธ์ระหว่างความไม่สม่ำเสมอของความเข้มข้นและความผันผวนของความเร็ว

---

## ทฤษฎีและสูตรทางคณิตศาสตร์ (Mathematical Framework)

### สมการ Reynolds-Averaged สำหรับ Multiphase Flow

สำหรับ **Multiphase flow** ที่มีการผันผวนของความปั่นป่วน สมการโมเมนตัมมีรูปแบบดังนี้:

$$\frac{\partial}{\partial t}(\overline{\alpha_k \rho_k \mathbf{u}_k}) + \nabla \cdot (\overline{\alpha_k \rho_k \mathbf{u}_k \mathbf{u}_k}) = -\overline{\alpha_k \nabla p} + \nabla \cdot \overline{\boldsymbol{\tau}_k} + \overline{\mathbf{M}_k} - \nabla \cdot \overline{\alpha_k \rho_k \mathbf{u}'_k \mathbf{u}'_k}$$

เทอม **$-\nabla \cdot \overline{\alpha_k \rho_k \mathbf{u}'_k \mathbf{u}'_k}$** คือ **Turbulent stress** สำหรับเฟส $k$

### โมเดลการกระจายตัวเนื่องจากความปั่นป่วน (Turbulent Dispersion Models)

#### 1. โมเดล Gradient Diffusion (การแพร่แบบเกรเดียนต์)

แนวทางที่พบได้บ่อยที่สุดคือการจำลองการกระจายตัวของความปั่นป่วนเป็นกระบวนการแพร่แบบเกรเดียนต์:

$$\mathbf{F}_{TD,k} = -D_{TD,k} \nabla \alpha_k$$

โดยที่ $D_{TD,k}$ คือ **สัมประสิทธิ์การกระจายตัวของความปั่นป่วน** (turbulent dispersion coefficient) สำหรับเฟส $k$

##### โมเดลของ Burns et al. (2004)

$$D_{TD,k} = \frac{\mu_{t,c}}{\sigma_{TD}} \frac{\alpha_k \alpha_l}{\alpha_{max}}$$

**นิยามตัวแปร:**
- $\mu_{t,c}$ = ความหนืดของความปั่นป่วน (turbulent viscosity) ของเฟสต่อเนื่อง
- $\sigma_{TD}$ = จำนวน Schmidt สำหรับการกระจายตัว (โดยทั่วไปคือ 0.6-1.0)
- $\alpha_{max}$ = สัดส่วนการอัดแน่นสูงสุด (maximum packing fraction) (โดยทั่วไปคือ 0.6-0.8)

##### โมเดลของ Simonin

$$D_{TD,k} = C_{TD} \sqrt{k_c} l_c$$

**นิยามตัวแปร:**
- $k_c$ = พลังงานจลน์ของความปั่นป่วน (turbulent kinetic energy) ของเฟสต่อเนื่อง
- $l_c$ = มาตราส่วนความยาวของความปั่นป่วน (turbulent length scale)
- $C_{TD}$ = สัมประสิทธิ์เชิงประจักษ์ (โดยทั่วไปคือ 0.1-0.5)

#### 2. โมเดล Drift Velocity (ความเร็วลอยเลื่อน)

สูตรทางเลือกที่ใช้ความเร็วลอยเลื่อน (drift velocity):

$$\mathbf{F}_{TD,k} = C_{TD} \alpha_k \alpha_l \rho_c (\mathbf{v}_{drift} \cdot \nabla \alpha_l)$$

โดยที่ความเร็วลอยเลื่อนคือ:

$$\mathbf{v}_{drift} = -D_{t,c} \frac{\nabla \alpha_l}{\alpha_l}$$

และ $D_{t,c} = \mu_{t,c}/\rho_c$ คือ **ความสามารถในการแพร่ของความปั่นป่วน** (turbulent diffusivity)

#### 3. โมเดล Lopez de Bertodano (1998)

สูตรที่พบมากที่สุดใน OpenFOAM:

$$\mathbf{F}_{TD} = \sum_{k \neq q} C_{TD} \rho_k \alpha_k \frac{\mu_{t,k}}{\sigma_{TD}} \left(\nabla \alpha_q - \frac{\alpha_q}{1-\alpha_q} \nabla \alpha_q\right)$$

**นิยามตัวแปร:**
- $C_{TD}$ = สัมประสิทธิ์การกระจายตัวเนื่องจากความปั่นป่วน (โดยทั่วไปคือ 1.0)
- $\rho_k$ = ความหนาแน่นของเฟส $k$
- $\alpha_k$ = เศษส่วนปริมาตรของเฟส $k$
- $\mu_{t,k}$ = ความหนืดเนื่องจากความปั่นป่วน (turbulent viscosity) ของเฟส $k$
- $\sigma_{TD}$ = จำนวน Schmidt ของความปั่นป่วน (turbulent Schmidt number) (โดยทั่วไปคือ 0.9-1.0)

---

## การนำไปใช้ใน OpenFOAM (Implementation in OpenFOAM)

### สถาปัตยกรรมโค้ด (Code Architecture)

โมเดลการกระจายตัวเนื่องจากความปั่นป่วนใน OpenFOAM ปฏิบัติตามรูปแบบการออกแบบเชิงวัตถุแบบคลาสสิก โดยมีคลาสฐานแบบนามธรรมที่กำหนดอินเทอร์เฟซ

```cpp
// Base class for turbulent dispersion models
// คลาสฐานสำหรับโมเดลการกระจายตัวเนื่องจากความปั่นป่วน
template<class PhasePair>
class turbulentDispersionModel
{
protected:
    // Reference to the phase pair
    // อ้างอิงถึงคู่เฟส
    const PhasePair& pair_;

public:
    // Virtual destructor for proper cleanup
    // ตัวทำลายแบบเสมือนสำหรับการทำความสะอาดที่เหมาะสม
    virtual ~turbulentDispersionModel() {}

    // Calculate and return the turbulent dispersion force
    // คำนวณและส่งคืนแรงกระจายตัวเนื่องจากความปั่นป่วน
    virtual tmp<volVectorField> Fd() const = 0;

    // Read model parameters from dictionary
    // อ่านพารามิเตอร์โมเดลจากพจนานุกรม
    virtual bool read() = 0;
};
```

**📂 Source:** `src/transportModels/multiphase/derivedInterfacialModels/turbulentDispersionModel/turbulentDispersionModel.H`

**คำอธิบายเพิ่มเติม:**

โครงสร้างคลาสแบบนามธรรม (abstract class) นี้เป็นพื้นฐานของการออกแบบโมเดลการกระจายตัวเนื่องจากความปั่นป่วนใน OpenFOAM โดยมีหลักการสำคัญดังนี้:

- **Template Design:** การใช้ `template<class PhasePair>` ทำให้คลาสสามารถทำงานกับคู่เฟสใดก็ได้ ไม่ว่าจะเป็นของไหล-ของแข็ง ของไหล-ฟอง หรือคู่เฟสอื่นๆ

- **Protected Member:** ตัวแปร `pair_` ถูกประกาศเป็น protected เพื่อให้คลาสลูก (derived classes) สามารถเข้าถึงข้อมูลเกี่ยวกับคู่เฟสได้โดยตรง

- **Pure Virtual Functions:** ฟังก์ชัน `Fd()` และ `read()` เป็น pure virtual functions (= 0) ซึ่งบังคับให้ทุกคลาสลูกต้องมีการ implement ฟังก์ชันเหล่านี้

- **RTTI Support:** การใช้ virtual functions ช่วยให้ระบบ RTTI (Run-Time Type Identification) ของ OpenFOAM สามารถจัดการคลาสต่างๆ ได้อย่างถูกต้อง

### โมเดลที่มีให้ใช้งานใน OpenFOAM

| โมเดล | คำอธิบาย | การใช้งาน |
|--------|-------------|-------------|
| **GradAlphaDispersionModel** | นำการกระจายตัวเนื่องจากความปั่นป่วนแบบอิงเกรเดียนต์โดยใช้เกรเดียนต์ของเศษส่วนปริมาตรมาใช้ | กระแสการไหลทั่วไป |
| **NoDispersion** | ปิดการใช้งานผลกระทบจากการกระจายตัวเนื่องจากความปั่นป่วน | ทดสอบและการตรวจสอบ |
| **ConstantDispersion** | ใช้สัมประสิทธิ์การกระจายตัวเนื่องจากความปั่นป่วนแบบคงที่ | การปรับแต่งง่ายๆ |

### การตั้งค่าใน OpenFOAM

ใน OpenFOAM แรงกระจายตัวเนื่องจากความปั่นป่วนถูกกำหนดใน `constant/phaseProperties`:

```cpp
// Turbulent dispersion model configuration
// การกำหนดค่าโมเดลการกระจายตัวเนื่องจากความปั่นป่วน
turbulentDispersion
(
    (air in water)
    {
        // Model type: Burns, NoDispersion, or ConstantDispersion
        // ประเภทโมเดล: Burns, NoDispersion หรือ ConstantDispersion
        type            Burns;
        
        // Turbulent Schmidt number (typically 0.6-1.0)
        // จำนวน Schmidt ของความปั่นป่วน (โดยทั่วไป 0.6-1.0)
        sigma           0.9;
        
        // Turbulent dispersion coefficient (typically 1.0)
        // สัมประสิทธิ์การกระจายตัวเนื่องจากความปั่นป่วน (โดยทั่วไป 1.0)
        Ctd             1.0;
    }
);
```

**📂 Source:** `tutorials/multiphase/multiphaseEulerFoam/bubbleColumn/constant/phaseProperties`

**คำอธิบายเพิ่มเติม:**

ไฟล์ `phaseProperties` เป็นจุดศูนย์รวมการกำหนดค่าทั้งหมดสำหรับโมเดล Eulerian-Eulerian multiphase flow ใน OpenFOAM:

- **Model Selection:** พารามิเตอร์ `type` ระบุโมเดลที่จะใช้ โดยโมเดล Burns เป็นที่นิยมสำหรับกรณีทั่วไป

- **Parameter Tuning:** `sigma` (Schmidt number) ควบคุมอัตราส่วนระหว่างความหนืดของความปั่นป่วนกับสัมประสิทธิ์การกระจายตัว ส่วน `Ctd` เป็นสัมประสิทธิ์ปรับค่าที่ใช้ในการปรับความเข้มของแรงกระจายตัว

- **Phase Pair Syntax:** ไวยากรณ์ `(air in water)` ระบุว่าเฟสกระจายตัว (air) อยู่ภายในเฟสต่อเนื่อง (water)

- **Multiple Phase Pairs:** สามารถกำหนดหลายคู่เฟสในรูปแบบลิสต์ถ้ามีมากกว่า 2 เฟสในระบบ

### การรวมเข้ากับระบบเฟส (Integration with Phase Systems)

ใน Solver `multiphaseEulerFoam` การกระจายตัวเนื่องจากความปั่นป่วนจะถูกรวมเข้าผ่าน:

1. **การถ่ายโอนโมเมนตัมระหว่างรอยต่อ (Interfacial Momentum Transfer)**
   - แรงจากการกระจายตัวเนื่องจากความปั่นป่วนมีส่วนช่วยในเทอมการถ่ายโอนโมเมนตัมระหว่างรอยต่อในสมการโมเมนตัมของแต่ละเฟส

2. **การเชื่อมโยงเศษส่วนปริมาตร (Volume Fraction Coupling)**
   - แรงขึ้นอยู่กับเกรเดียนต์ของเศษส่วนปริมาตร ทำให้เกิดการเชื่อมโยงที่แข็งแกร่งระหว่างเฟส

3. **การรวมเข้ากับโมเดลความปั่นป่วน (Turbulence Model Integration)**
   - ความหนืดเนื่องจากความปั่นป่วนจากโมเดลความปั่นป่วนของเฟสต่อเนื่องจะถูกนำมาใช้ในการคำนวณสัมประสิทธิ์การกระจายตัว

```cpp
// Integration of turbulent dispersion into momentum equation
// การผนวกแรงกระจายตัวเนื่องจากความปั่นป่วนเข้ากับสมการโมเมนตัม
template<class PhaseType>
void PhaseSystem<PhaseType>::solve()
{
    // Calculate interfacial momentum transfer
    // คำนวณการถ่ายโอนโมเมนตัมระหว่างรอยต่อ
    tmp<volVectorField> tFtd = turbulentDispersion_->Fd();
    const volVectorField& Ftd = tFtd();
    
    // Add to momentum equation for each phase
    // เพิ่มเข้ากับสมการโมเมนตัมสำหรับแต่ละเฟส
    forAll(phases_, phasei)
    {
        fvVectorMatrix& UEqn = UEqns_[phasei];
        UEqn += Ftd;
    }
}
```

**📂 Source:** `src/transportModels/multiphase/PhaseSystem/PhaseSystem.C`

**คำอธิบายเพิ่มเติม:**

การผนวกโมเดลการกระจายตัวเนื่องจากความปั่นป่วนเข้ากับระบบสมการโมเมนตัมมีขั้นตอนสำคัญดังนี้:

- **Force Calculation:** ฟังก์ชัน `Fd()` คำนวณแรงกระจายตัวเนื่องจากความปั่นป่วนโดยใช้สถานะปัจจุบันของเฟส (เศษส่วนปริมาตร, ความเร็ว, ความหนืดของความปั่นป่วน)

- **tmp<> Smart Pointer:** การใช้ `tmp<volVectorField>` เป็นกลไกจัดการหน่วยความจำอัตโนมัติของ OpenFOAM เพื่อป้องกันการรั่วซึมของหน่วยความจำ

- **ForAll Loop:** `forAll(phases_, phasei)` เป็นวิธีการวนซ้ำที่ปลอดภัยและมีประสิทธิภาพสำหรับการจัดการรายการเฟสทั้งหมด

- **UEqn Addition:** การเพิ่มแรงกระจายตัวเข้ากับสมการโมเมนตัมด้วยตัวดำเนินการ `+=` เป็นวิธีที่ตรงไปตรงมาและชัดเจน

### การเชื่อมโยงกับโมเดลความปั่นป่วน (Connection to Turbulence Modeling)

การจำลองการกระจายแบบปั่นป่วนในการไหลแบบหลายเฟสมีความสัมพันธ์โดยตรงกับ **โมเดลความปั่นป่วนพื้นฐาน** ที่เลือกใช้:

| โมเดลความปั่นป่วน | สูตรความหนืด $\mu_{t,c}$ | ความเหมาะสม |
|-------------------|-------------------------|---------------|
| **$k$-$\epsilon$** | $\rho_c C_\mu \frac{k_c^2}{\varepsilon_c}$ | การไหลเลข Reynolds สูง, ไกลผนัง |
| **$k$-$\omega$** | $\rho_c \frac{k_c}{\omega_c}$ | การไหลใกล้ผนัง, การไหลแยก |
| **LES** | $\rho_c (C_s \Delta)^2 \|\mathbf{S}\|$ | การจำลองรายละเอียดสูง |

```cpp
// Turbulent viscosity calculation for k-epsilon model
// การคำนวณความหนืดของความปั่นป่วนสำหรับโมเดล k-epsilon
tmp<volScalarField> kEpsilon::muEff() const
{
    // Calculate turbulent viscosity
    // คำนวณความหนืดของความปั่นป่วน
    return tmp<volScalarField>
    (
        new volScalarField
        (
            "muEff",
            // mu_t = rho * Cmu * k^2 / epsilon
            mu_ + rho_ * Cmu_ * sqr(k_) / epsilon_
        )
    );
}
```

**📂 Source:** `src/turbulenceModels/compressible/kEpsilon/kEpsilon.C`

**คำอธิบายเพิ่มเติม:**

ความสัมพันธ์ระหว่างโมเดลความปั่นป่วนและแรงกระจายตัวเนื่องจากความปั่นป่วนมีความสำคัญอย่างยิ่ง:

- **Turbulent Viscosity:** ความหนืดของความปั่นป่วน ($\mu_t$) ถูกคำนวณจากพลังงานจลน์ของความปั่นป่วน ($k$) และอัตราการสลาย ($\epsilon$)

- **Cmu Constant:** $C_\mu$ เป็นค่าคงที่ประจักษ์ที่มีค่าโดยทั่วไปคือ 0.09 สำหรับโมเดล $k$-$\epsilon$

- **Coupling Mechanism:** ความหนืดของความปั่นป่วนจากเฟสต่อเนื่องถูกส่งผ่านไปยังโมเดลการกระจายตัวเพื่อคำนวณสัมประสิทธิ์การกระจาย

- **Model Hierarchy:** โครงสร้างแบบ Layered ทำให้สามารถเปลี่ยนโมเดลความปั่นป่วนโดยไม่กระทบต่อโมเดลการกระจายตัว

---

## พารามิเตอร์และการเลือกโมเดล (Parameters and Model Selection)

### สัมประสิทธิ์การกระจายตัวเนื่องจากความปั่นป่วน ($C_{TD}$)

| ค่า | คำอธิบาย | การใช้งานที่เหมาะสม |
|-----|-------------|-------------------|
| **0.1 - 0.5** | การกระจายตัวน้อย | กระแสการไหลที่มีความเฉพาะเจาะจงต่ำ |
| **1.0** | ค่าเริ่มต้นใน OpenFOAM | การใช้งานทั่วไป |
| **1.0 - 1.5** | การกระจายตัวมาก | การไหลแบบปั่นป่วนอย่างยิ่ง |

### จำนวน Schmidt ของความปั่นป่วน ($\sigma_{TD}$)

| ค่า | ความหมาย | ผลกระทบ |
|-----|------------|-----------|
| **0.7** | การแพร่ของโมเมนตัมสูงกว่า | การกระจายตัวน้อยลง |
| **0.9 - 1.0** | ค่าเริ่มต้น | สมดุลมาตรฐาน |
| **1.3** | การแพร่ของโมเมนตัมต่ำกว่า | การกระจายตัวมากขึ้น |

> [!WARNING] **ข้อควรระวัง**
> - ค่า $C_{TD}$ และ $\sigma_{TD}$ สูงอาจก่อให้เกิดความไม่เสถียรทางตัวเลข
> - ควรทำการทดลองกับค่าต่างๆ เพื่อหาค่าที่เหมาะสมกับแต่ละกรณี

---

## ข้อควรพิจารณาทางตัวเลข (Numerical Considerations)

### ความเสถียรเชิงตัวเลข (Numerical Stability)

เทอมการกระจายตัวเนื่องจากความปั่นป่วนสามารถก่อให้เกิดความแข็งแกร่งเชิงตัวเลข (numerical stiffness) ได้ โดยเฉพาะอย่างยิ่ง:

- **ใกล้ขอบเขตของเศษส่วนปริมาตร** ($\alpha \to 0$ หรือ $\alpha \to 1$)
- **ในบริเวณที่มีเกรเดียนต์ของเศษส่วนปริมาตรที่คมชัด**
- **เมื่อรวมเข้ากับแรงระหว่างรอยต่ออื่นๆ**

### เทคนิคการทำให้เป็นปกติ (Regularization Techniques)

#### 1. การจำกัดการไล่ระดับ (Gradient Limiting)

$$\nabla \alpha_{k,limited} = \min\left(|\nabla \alpha_k|, \nabla \alpha_{max}\right) \frac{\nabla \alpha_k}{|\nabla \alpha_k|}$$

#### 2. การผ่อนคลาย (Relaxation)

$$\mathbf{F}_{TD}^{new} = (1-\lambda_{TD})\mathbf{F}_{TD}^{old} + \lambda_{TD}\mathbf{F}_{TD}^{calculated}$$

โดยที่ $\lambda_{TD}$ คือตัวปรับการผ่อนคลาย (โดยทั่วไป 0.5-0.8)

```cpp
// Implementation of gradient limiting for numerical stability
// การนำไปใช้งานของการจำกัดเกรเดียนต์เพื่อความเสถียรทางตัวเลข
tmp<volVectorField> turbulentDispersionModel::limitGradient
(
    const volScalarField& alpha
) const
{
    // Calculate gradient
    // คำนวณเกรเดียนต์
    tmp<volVectorField> tgradAlpha = fvc::grad(alpha);
    const volVectorField& gradAlpha = tgradAlpha();
    
    // Calculate magnitude
    // คำนวณขนาด
    volScalarField magGradAlpha = mag(gradAlpha);
    
    // Apply limiting
    // ใช้การจำกัด
    volScalarField limiter = min(magGradAlpha, maxGrad_);
    
    // Return limited gradient
    // ส่งคืนเกรเดียนต์ที่ถูกจำกัดแล้ว
    return limiter * gradAlpha / (magGradAlpha + SMALL);
}
```

**📂 Source:** `src/transportModels/multiphase/derivedInterfacialModels/turbulentDispersionModels/gradAlphaDispersionModel/gradAlphaDispersionModel.C`

**คำอธิบายเพิ่มเติม:**

เทคนิคการจำกัดเกรเดียนต์มีความสำคัญอย่างยิ่งสำหรับความเสถียรของการคำนวณ:

- **Gradient Calculation:** `fvc::grad(alpha)` ใช้ finite volume method ในการคำนวณเกรเดียนต์ของเศษส่วนปริมาตร

- **Magnitude Computation:** ฟังก์ชัน `mag()` คำนวณขนาดของเวกเตอร์เกรเดียนต์

- **MIN Operation:** การใช้ `min()` กับ `maxGrad_` ช่วยป้องกันไม่ให้เกรเดียนต์มีค่าเกินกว่าที่กำหนด

- **SMALL Constant:** การเพิ่มค่าคงที่ `SMALL` ในตัวหารเป็นเทคนิคมาตรฐานในการป้องกันการหารด้วยศูนย์

- **Vector Normalization:** การหารด้วย `magGradAlpha + SMALL` ทำให้ได้เวกเตอร์หน่วย (unit vector) ในทิศทางเดิม

### ข้อกำหนดของเมช (Mesh Requirements)

การทำนายการกระจายตัวเนื่องจากความปั่นป่วนอย่างแม่นยำต้องการ:

- **ความละเอียดของเมชเพียงพอที่จะจับเกรเดียนต์ของเศษส่วนปริมาตรได้**
- **การจัดการใกล้ผนังที่เหมาะสมสำหรับการไหลแบบปั่นป่วนที่ติดกับผนัง**
- **สกีมการประมาณค่าแบบอนุรักษ์** (conservative interpolation schemes) สำหรับการขนส่งเศษส่วนปริมาตร

---

## ข้อจำกัดและความท้าทาย (Limitations and Challenges)

### ข้อสมมติฐานในการจำลอง (Modeling Assumptions)

1. **การแพร่ตามเกรเดียนต์ (Gradient Diffusion)**
   - สมมติว่าฟลักซ์เนื่องจากความปั่นป่วนสามารถจำลองได้โดยใช้การแพร่ตามเกรเดียนต์
   - **ข้อจำกัด:** อาจไม่แม่นยำสำหรับกรณีที่ซับซ้อน

2. **ความปั่นป่วนแบบไอโซโทรปิก (Isotropic Turbulence)**
   - โมเดลส่วนใหญ่สมมติว่าการกระจายตัวเนื่องจากความปั่นป่วนเป็นแบบไอโซโทรปิก

3. **สมดุลเฉพาะที่ (Local Equilibrium)**
   - สันนิษฐานว่าเฟสกระจายตัวปรับตัวเข้ากับความผันผวนเนื่องจากความปั่นป่วนได้อย่างทันทีทันใด

### ข้อจำกัดทางกายภาพ (Physical Limitations)

1. **สารแขวนลอยหนาแน่น (Dense Suspensions)**
   - โมเดลอาจล้มเหลวที่เศษส่วนปริมาตรสูง

2. **อนุภาคขนาดใหญ่ (Large Particles)**
   - ผลของความเฉื่อยของอนุภาคไม่ได้ถูกจับได้อย่างสมบูรณ์

3. **ความปั่นป่วนแบบแอนไอโซโทรปิก (Anisotropic Turbulence)**
   - การจัดการการกระจายตัวที่ขึ้นกับทิศทางมีจำกัด

---

## หัวข้อขั้นสูง (Advanced Topics)

### การกระจายแบบ Anisotropic Turbulent

สำหรับความปั่นป่วนแบบ anisotropic สัมประสิทธิ์การกระจายจะกลายเป็นเทนเซอร์:

$$\mathbf{D}_{TD} = \begin{bmatrix}
D_{xx} & 0 & 0 \\
0 & D_{yy} & 0 \\
0 & 0 & D_{zz}
\end{bmatrix}$$

ซึ่งสามารถจำลองได้โดยใช้เทนเซอร์ความเค้น Reynolds:

$$\mathbf{D}_{TD} = C_{TD} \frac{\mathbf{R}}{\epsilon}$$

### การกระจายแบบ Non-Fickian

ในบางกรณี สมมติฐานการแพร่แบบ Fickian ไม่เป็นจริง:

$$\mathbf{F}_{TD} = -\mathbf{D}_{TD} \cdot \nabla \alpha - \mathbf{J}_{non-Fickian}$$

โดยเงื่อนไขที่สมมติฐาน Fickian ล้มเหลว ได้แก่:
1. กระแสน้ำวนความปั่นป่วนมีขนาดใหญ่เมื่อเทียบกับมาตราส่วนลักษณะเฉพาะที่สนใจ
2. โครงสร้างที่สอดคล้องกันเป็นตัวควบคุมการขนส่ง
3. เฉื่อยของอนุภาคจำกัด สร้างผลของความไม่สมดุล

### การผูกกันสองทิศทางกับความปั่นป่วน (Two-way Coupling)

อนุภาคสามารถแก้ไขความปั่นป่วนได้ ซึ่งมีนัยสำคัญเมื่อ:
- ปริมาตรอนุภาค > $10^{-3}$
- เวลาตอบสนองของอนุภาค ≈ มาตราส่วนเวลาความปั่นป่วน

#### 1. การลดทอนความปั่นป่วน (Turbulence Attenuation)

$$\epsilon_{mod} = \epsilon (1 + f_{att} \alpha_p)$$

#### 2. การเสริมความปั่นป่วน (Turbulence Enhancement)

$$S_{enh} = f_{enh} \alpha_p \frac{1}{2} C_D \rho_f |\mathbf{u}_f - \mathbf{u}_p|^2$$

---

## การทดสอบและการตรวจสอบความถูกต้อง (Validation Cases)

### กรณีทดสอบหลัก

| กรณีทดสอบ | วัตถุประสงค์ | ตัวชี้วัด |
|--------------|-------------|-----------|
| **การไหลแบบปั่นป่วนในท่อ** | กรณีทดสอบความถูกต้องพื้นฐาน | โปรไฟล์ความเข้มของอนุภาค, อัตราการตกตะกอน |
| **การผสมเจ็ท** | การประเมินการกระจายและการดูดซึม | อัตราการกระจายตัวของเจ็ท, การลดลงของความเร็ว |
| **ความปั่นป่วนเอกพันธ์และเท่ากัน (HIT)** | การศึกษาปฏิสัมพันธ์อนุภาค-ความปั่นป่วน | การเคลื่อนที่กำลังสองเฉลี่ย, ฟังก์ชันการแจกแจง |

---

## แหล่งอ้างอิงและการอ่านเพิ่มเติม (References)

### บทความที่เกี่ยวข้อง
- **[[01_Introduction]]** - บทนำสู่การกระจายตัวเนื่องจากความปั่นป่วน
- **[[02_Physical_Mechanisms]]** - กลไกทางกายภาพอย่างละเอียด
- **[[03_Fundamental_Theory]]** - ทฤษฎีพื้นฐานและสูตรทางคณิตศาสตร์
- **[[04_Turbulent_Dispersion_Models]]** - โมเดลการกระจายตัวทั้งหมด
- **[[05_Specific_Model_Formulations]]** - การกำหนดรูปแบบโมเดลเฉพาะ
- **[[06_Connection_to_Turbulence_Modeling]]** - การเชื่อมต่อกับโมเดลความปั่นป่วน
- **[[07_OpenFOAM_Implementation]]** - การนำไปใช้ใน OpenFOAM
- **[[08_Physical_Interpretation_and_Applications]]** - การตีความทางกายภาพและการประยุกต์ใช้
- **[[09_Validation_Cases]]** - กรณีทดสอบความถูกต้อง
- **[[10_Numerical_Considerations]]** - ข้อควรพิจารณาทางตัวเลข
- **[[11_Advanced_Topics]]** - หัวข้อขั้นสูง
- **[[12_Summary]]** - สรุปทั้งหมด

### เอกสารอ้างอิงหลัก
- Burns, A. D., et al. (2004). "A Favre-averaged two-fluid model for wall-bounded particle-laden turbulent flows"
- Lopez de Bertodano, M. (1998). "Turbulent bubbly two-phase flow in a triangular duct"
- Simonin, O. (1991). "Prediction of the dispersed phase turbulence in particle-laden jets"

---

> [!TIP] **เคล็ดลับสำหรับการใช้งาน**
> - เริ่มต้นด้วยค่าพารามิเตอร์เริ่มต้น ($C_{TD} = 1.0$, $\sigma_{TD} = 0.9$)
> - ปรับค่าพารามิเตอร์อย่างระมัดระวังตามผลลัพธ์การจำลอง
> - ตรวจสอบความลู่เข้าและความเสถียรของการคำนวณอย่างใกล้ชิด
> - ทดลองกับโมเดลที่แตกต่างกันเพื่อเปรียบเทียบผลลัพธ์