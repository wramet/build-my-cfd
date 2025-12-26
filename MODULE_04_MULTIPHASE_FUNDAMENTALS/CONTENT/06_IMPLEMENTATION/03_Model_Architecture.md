# สถาปัตยกรรมโมเดลและรายละเอียดการนำไปใช้งาน (Model Architecture & Implementation)

## 1. บทนัด (Introduction)

OpenFOAM ใช้สถาปัตยกรรมที่ยืดหยุ่นและขยายได้สูง (Modular & Extensible) สำหรับการจัดการโมเดลหลายเฟส โดยเฉพาะใน `multiphaseEulerFoam` ซึ่งใช้ระบบ **Run-time Selection** ช่วยให้ผู้ใช้สามารถเลือกหรือเปลี่ยนโมเดลฟิสิกส์ต่างๆ ได้ผ่านไฟล์การตั้งค่าโดยไม่ต้องคอมไพล์โค้ดใหม่

---

## 2. หลักการออกแบบหลัก (Core Design Principles)

- **Runtime Selection**: โมเดลถูกเลือกแบบไดนามิกผ่านพจนานุกรม `phaseProperties` โดยใช้กลไก `TypeName` และ `New`
- **Polymorphism**: ใช้คลาสฐาน (Base class) กำหนดอินเตอร์เฟซมาตรฐาน (เช่น `dragModel`) และให้คลาสลูก (Derived class) นำไปใช้งานจริง (เช่น `SchillerNaumannDrag`)
- **Phase-pair Specificity**: โมเดลส่วนใหญ่ทำงานบนออบเจ็กต์ `phasePair` ซึ่งเก็บข้อมูลการปฏิสัมพันธ์ระหว่างคู่เฟสที่เฉพาะเจาะจง

---

## 3. ลำดับชั้นโมเดลการถ่ายโอนโมเมนตัมระหว่างเฟส (Interfacial Momentum Transfer Model Hierarchy)

### 3.1 โครงสร้างคลาส dragModel

ลำดับชั้นโมเดลการลากตัวใน OpenFOAM ให้กรอบการทำงานที่ยืดหยุ่นสำหรับการคำนวณการถ่ายเทโมเมนตัมระหว่างเฟสในการไหลแบบหลายเฟส

**คลาสฐาน `dragModel`** ทำหน้าที่เป็นอินเตอร์เฟซนามธรรม:
- ออกแบบให้ยืดหยุ่น สามารถเลือก correlations การลากตัวที่แตกต่างกันได้ในขณะทำงาน
- ใช้รูปแบบเมธอด factory สำหรับการสร้างโมเดลแบบไดนามิก

```cpp
// Base drag model interface
class dragModel
{
public:
    // Virtual destructor for proper cleanup
    virtual ~dragModel() {}

    // Calculate drag force between phases
    // Returns: volVectorField - drag force per unit volume [N/m³]
    virtual tmp<volVectorField> F
    (
        const phaseModel& phase1, // Dispersed phase
        const phaseModel& phase2  // Continuous phase
    ) const = 0;

    // Factory method for runtime model selection
    // Returns: autoPtr to constructed dragModel
    static autoPtr<dragModel> New
    (
        const dictionary& dict,    // Model sub-dictionary
        const phasePair& pair      // Phase pair key
    );
};
```

**📁 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/interfacialModels/dragModels/dragModel/dragModel.H`

**คำอธิบาย:**
- **Base Class Pattern**: คลาส `dragModel` ทำหน้าที่เป็น abstract interface ที่กำหนดโครงสร้างพื้นฐานสำหรับโมเดลการลากตัวทั้งหมด
- **Factory Method**: เมธอด `New()` ใช้สำหรับสร้างออบเจ็กต์โมเดลแบบ runtime ผ่านกลไก `TypeName` ของ OpenFOAM
- **Virtual Function**: เมธอด `F()` เป็น pure virtual function ที่แต่ละโมเดลต้องนำไปใช้งานจริง

**แนวคิดสำคัญ:**
- **Runtime Selection**: ผู้ใช้สามารถระบุชนิดของโมเดลในไฟล์ `constant/phaseProperties` โดยไม่ต้องคอมไพล์โค้ดใหม่
- **Polymorphic Design**: โค้ดส่วนปัจจัยการแก้สมการ (solver) สามารถเรียกใช้งานโมเดลผ่าน interface ร่วมกัน
- **Phase Pair Dependency**: โมเดลทำงานบนคู่เฟส (phase pair) ซึ่งเก็บข้อมูลของสองเฟสที่โต้ตอบกัน

### 3.2 โมเดล Schiller-Naumann Drag

**คุณสมบัติ:**
- สืบทอดจากคลาส `dragModel`
- เหมาะสำหรับการไหลของฟองกระจาย (dispersed bubble flow)
- ใช้งานได้ดีกับจำนวน Reynolds ต่ำถึงปานกลาง

**สมการสัมประสิทธิ์การลากตัว:**
$$C_D = \begin{cases} 24(1 + 0.15 Re^{0.687}) / Re & \text{if } Re < 1000 \\ 0.44 & \text{if } Re \geq 1000 \end{cases}$$

**ตัวแปรในสมการ:**
- $C_D$ = สัมประสิทธิ์การลากตัว (drag coefficient)
- $Re$ = จำนวน Reynolds สัมพัทธ์ระหว่างเฟส
- $Re = \rho_p |\mathbf{u}_p - \mathbf{u}_c| d_p / \mu_c$
  - $\rho_p$ = ความหนาแน่นของอนุภาค
  - $\mathbf{u}_p, \mathbf{u}_c$ = เวกเตอร์ความเร็วของเฟสอนุภาคและเฟสต่อเนื่อง
  - $d_p$ = เส้นผ่านศูนย์กลางอนุภาค
  - $\mu_c$ = ความหนืดของเฟสต่อเนื่อง

```cpp
// Schiller-Naumann drag model implementation
class SchillerNaumannDrag
:
    public dragModel
{
private:
    // Reference to phase pair (dispersed/continuous)
    const phasePair& pair_;

public:
    // Constructor from dictionary
    SchillerNaumannDrag
    (
        const dictionary& dict, // Model parameters
        const phasePair& pair   // Phase pair reference
    );

    // Calculate drag force using Schiller-Naumann correlation
    // Formula: F = 0.75 * Cd * rho_c * alpha_d * |U_rel| * U_rel / d_p
    virtual tmp<volVectorField> F
    (
        const phaseModel& phase1,
        const phaseModel& phase2
    ) const;

    // Drag coefficient calculation
    // Cd = 24*(1 + 0.15*Re^0.687)/Re  for Re < 1000
    // Cd = 0.44                        for Re >= 1000
    virtual tmp<volScalarField> Cd
    (
        const volScalarField& Re // Reynolds number field
    ) const;
};
```

**📁 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/interfacialModels/dragModels/SchillerNaumann/SchillerNaumann.H`

**คำอธิบาย:**
- **Schiller-Naumann Correlation**: เป็นหนึ่งในโมเดลการลากตัวที่ได้รับความนิยมสูงสำหรับการไหลแบบ dispersed flow เช่น ฟองในของเหลว
- **Two Regime Formula**: สมการมีสองช่วง - ช่วง creeping flow (Re < 1000) ใช้ Stokes+ correction และช่วง turbulent (Re ≥ 1000) ใช้ค่าคงที่
- **Reynolds Calculation**: Re ถูกคำนวณจากความเร็วสัมพัทธ์ระหว่างเฟส ความหนาแน่น และความหนืด

**แนวคิดสำคัญ:**
- **Dispersed Phase Assumption**: โมเดลนี้อิงว่ามีเฟสหนึ่งเป็น dispersed (เช่น ฟอง) และอีกเฟสเป็น continuous
- **Intermediate Reynolds**: เหมาะสำหรับช่วง Reynolds ที่ไม่ต่ำมาก (Re > 0.1) แต่ยังไม่ถึง turbulent เต็มรูปแบบ
- **Standard Reference**: ถูกใช้เป็น reference model ในหลายการศึกษาเปรียบเทียบ

### 3.3 แรงระหว่างเฟสอื่นๆ

เทอม $\mathbf{M}_k$ ในสมการโมเมนตัมคือผลรวมของแรงต่างๆ ที่เกิดขึ้นที่อินเตอร์เฟซ:
$$\mathbf{M}_k = \sum_{l=1}^{N} (\mathbf{F}^{D}_{kl} + \mathbf{F}^{L}_{kl} + \mathbf{F}^{VM}_{kl} + \mathbf{F}^{TD}_{kl})$$

#### แรงยก (Lift Force)
$$\mathbf{F}^{L}_{kl} = C_L \rho_k \alpha_l (\mathbf{u}_l - \mathbf{u}_k) \times (\nabla \times \mathbf{u}_k)$$

- ใช้โมเดลแรงยกของ Tomiyama หรือแบบอื่น
- $C_L$ = สัมประสิทธิ์แรงยก

#### แรงมวลเสมือน (Virtual Mass Force)
$$\mathbf{F}^{VM}_{kl} = C_{VM} \rho_k \alpha_l \left(\frac{D\mathbf{u}_l}{Dt} - \frac{D\mathbf{u}_k}{Dt}\right)$$

- คำนึงถึงผลกระทบของมวลเพิ่ม
- $C_{VM}$ = สัมประสิทธิ์มวลเสมือน (ค่าทั่วไป = 0.5)

#### การกระเจืองความปั่นป่วน (Turbulent Dispersion)
$$\mathbf{F}^{TD}_{kl} = C_{TD} \rho_k \frac{\mu_{t,k}}{\sigma_{t,k}} (\nabla \alpha_l - \nabla \alpha_k)$$

- ใช้โมเดลของ Burns หรือ Lopez de Bertodano
- $C_{TD}$ = สัมประสิทธิ์การกระเจืองความปั่นป่วน

```cpp
// Interfacial momentum transfer implementation
// Shows how multiple force models are combined in MomentumTransferPhaseSystem

// Template for adding mass transfer momentum contribution
template<class BasePhaseSystem>
void Foam::MomentumTransferPhaseSystem<BasePhaseSystem>::addDmdtUfs
(
    const phaseSystem::dmdtfTable& dmdtfs,  // Mass transfer rates
    phaseSystem::momentumTransferTable& eqns // Momentum equations
)
{
    // Iterate over all mass transfer pairs
    forAllConstIter(phaseSystem::dmdtfTable, dmdtfs, dmdtfIter)
    {
        const phaseInterface interface(*this, dmdtfIter.key());
        
        // Get mass transfer rate (positive = phase2->phase1)
        const volScalarField& dmdtf = *dmdtfIter();
        const volScalarField dmdtf21(posPart(dmdtf)); // Transfer to phase1
        const volScalarField dmdtf12(negPart(dmdtf)); // Transfer to phase2

        phaseModel& phase1 = this->phases()[interface.phase1().name()];
        phaseModel& phase2 = this->phases()[interface.phase2().name()];

        // Add momentum source for phase1 (gains mass + velocity)
        if (!phase1.stationary())
        {
            *eqns[phase1.name()] +=
                dmdtf21*phase2.U()      // Incoming momentum
              + fvm::Sp(dmdtf12, phase1.URef()); // Outgoing correction
        }

        // Add momentum source for phase2 (loses mass - velocity)
        if (!phase2.stationary())
        {
            *eqns[phase2.name()] -=
                dmdtf12*phase1.U()      // Incoming momentum
              + fvm::Sp(dmdtf21, phase2.URef()); // Outgoing correction
        }
    }
}
```

**📁 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C`

**คำอธิบาย:**
- **Multi-Force Superposition**: แรงระหว่างเฟสทั้งหมดถูกรวมเข้าด้วยกันในเทอม $\mathbf{M}_k$ ซึ่งถูกเพิ่มลงในสมการโมเมนตัม
- **Mass-Momentum Coupling**: เมื่อมีการถ่ายโอนมวล โมเมนตัมก็ต้องถูกถ่ายโอนไปด้วย ฟังก์ชัน `addDmdtUfs` จัดการสิ่งนี้
- **Stationary Phase Handling**: เฟสที่เคลื่อนที่ไม่ได้ (เช่น solid wall) จะถูกข้ามไป

**แนวคิดสำคัญ:**
- **Force Balance**: โมเมนตัมระหว่างเฟสถูกถ่ายโอนผ่านกลไกหลายแบบพร้อมกัน
- **Action-Reaction**: แรงที่เฟส 1 กระทำต่อเฟส 2 เท่ากับแรงที่เฟส 2 กระทำต่อเฟส 1 ในทิศทางตรงข้าม
- **Numerical Stability**: การจัดการ mass transfer ต้องระมัดระวังเพื่อหลีกเลี่ยงปัญหาเชิงตัวเลข

---

## 4. การผสมผสานโมเดลความปั่นป่วน (Turbulence Modeling Integration)

กรอบการทำงานโมเดลความปั่นป่วนแบบหลายเฟสขยายแนวทางการจำลองความปั่นป่วนแบบเฟสเดียวเพื่อจัดการกับหลายเฟสที่โต้ตอบกัน

### 4.1 สถาปัตยกรรมหลัก

**คลาส `phaseCompressibleTurbulenceModel`:**
- สืบทอดจาก `compressible::turbulenceModel` ฐาน
- เพิ่มฟังก์ชันการทำงานเฉพาะเฟส ผ่านการอ้างอิงถึงโมเดลเฟสแต่ละตัว
- รักษาการ coupling ที่เหมาะสมระหว่างเฟส

### 4.2 คุณสมบัติที่สำคัญ

- แต่ละเฟสมีลักษณะความปั่นป่วนของตัวเอง
- ให้การเข้าถึงฟิลด์เฉพาะเฟส: ความหนาแน่น, ความเร็ว, สัดส่วนปริมาตร
- รักษาเสถียรภาพเชิงตัวเลข และความสอดคล้องทางฟิสิกส์ข้ามอินเตอร์เฟซเฟส

```cpp
// Multiphase turbulence model base class
class phaseCompressibleTurbulenceModel
:
    public compressible::turbulenceModel
{
protected:
    // Reference to phase model
    const phaseModel& phase_;
    
    // Reference to phase system
    const phaseSystem& phaseSystem_;

public:
    // Constructor with phase-specific fields
    phaseCompressibleTurbulenceModel
    (
        const volScalarField& rho,  // Phase density
        const volVectorField& U,   // Phase velocity
        const surfaceScalarField& phi, // Phase flux
        const phaseModel& phase    // Phase reference
    );

    // Calculate Reynolds stress tensor for this phase
    // Returns: -rho * mean(u' * u')
    virtual tmp<volSymmTensorField> R() const;

    // Calculate turbulent viscosity for this phase
    // Returns: mu_t = rho * Cmu * k^2 / epsilon
    virtual tmp<volScalarField> mut() const;

    // Correct turbulence quantities (solve k, epsilon equations)
    virtual void correct();
};
```

**📁 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseModel/PhaseCompressibleTurbulenceModel.H`

**คำอธิบาย:**
- **Phase-Specific Turbulence**: แต่ละเฟสมีโมเดลความปั่นป่วนของตัวเอง ซึ่งแตกต่างจาก single-phase flow
- **Reynolds Stress**: เทนเซอร์ความเค้น $\mathbf{R}_k$ แสดงถึงการถ่ายโอนโมเมนตัมจากความปั่นป่วน
- **Turbulent Viscosity**: ความหนืด $\mu_{t,k}$ ใช้ในการจำลองผลกระทบของความปั่นป่วนต่อการไหลเฉลี่ย

**แนวคิดสำคัญ:**
- **Multi-Regime Turbulence**: ความปั่นป่วนในแต่ละเฟสมีลักษณะแตกต่างกัน (เช่น turbulent bubbles vs laminar liquid)
- **Interface Effects**: อินเตอร์เฟซระหว่างเฟสสร้างความปั่นป่วนเพิ่มเติม
- **Numerical Coupling**: การแก้โมเดลความปั่นป่วนต้อง coupling กับสมการโมเมนตัม

### 4.3 เมธอดสำคัญสำหรับการคำนวณแบบหลายเฟส

#### การคำนวณความเค้น Reynolds (`R()`)

ส่งคืนเทนเซอร์ความเค้น Reynolds สำหรับเฟส ซึ่งคำนึงถึงการถ่ายเทโมเมนตัมแบบปั่นป่วน:

$$\mathbf{R}_k = -\rho_k \overline{\mathbf{u}'_k \mathbf{u}'_k}$$

**ตัวแปร:**
- $\mathbf{R}_k$ = เทนเซอร์ความเค้น Reynolds สำหรับเฟส $k$
- $\rho_k$ = ความหนาแน่นของเฟส $k$
- $\overline{\mathbf{u}'_k \mathbf{u}'_k}$ = การเฉลี่ยของผลคูณความเร็วความปั่นป่วน

#### ความหนืดความปั่นป่วน (`mut()`)

คำนวณความหนืดความปั่นป่วนสำหรับเฟส โดยทั่วไปจำลองโดยใช้โมเดลความหนืด eddy:

$$\mu_{t,k} = \rho_k C_\mu \frac{k_k^2}{\epsilon_k}$$

**ตัวแปร:**
- $\mu_{t,k}$ = ความหนืดความปั่นป่วนของเฟส $k$
- $C_\mu$ = ค่าคงที่จากโมเดลความปั่นป่วน
- $k_k$ = พลังงานจลน์ความปั่นป่วนของเฟส $k$
- $\epsilon_k$ = อัตราการสลายของพลังงานจลน์ความปั่นป่วนของเฟส $k$

#### ขั้นตอนการแก้ไข (`correct()`)

อัปเดตปริมาณความปั่นป่วนในแต่ละช่วงเวลา:
- แก้สมการการถ่ายเท สำหรับพลังงานจลน์ความปั่นป่วน $k$
- แก้สมการการถ่ายเท สำหรับอัตราการสลาย $\epsilon$
- รวมผลของสัดส่วนปริมาตรเฟส และการโต้ตอบระหว่างเฟส

```cpp
// Solve turbulence transport equations for multiphase flow
void phaseCompressibleTurbulenceModel::correct()
{
    // Solve k-equation: TKE transport
    // ∂(ρk)/∂t + ∇·(ρU k) = ∇·[(μ+μt/σk)∇k] + Pk - ρε
    tmp<volScalarField> tKEqn
    (
        fvm::ddt(phase_.rho(), k_)
      + fvm::div(phase_.alphaPhi(), phase_.rho(), k_)
     ==
        fvm::laplacian(DkEff(), k_)
      + Pk()                          // Production term
      - fvm::Sp(phase_.rho()*epsilon_()/k_, k_)  // Dissipation
    );
    
    tKEqn().relax();
    tKEqn().solve();
    
    // Solve epsilon-equation: Dissipation rate transport
    // ∂(ρε)/∂t + ∇·(ρU ε) = ∇·[(μ+μt/σε)∇ε] + C1 Pk ε/k - C2 ρ ε²/k
    tmp<volScalarField> epsilonEqn
    (
        fvm::ddt(phase_.rho(), epsilon_)
      + fvm::div(phase_.alphaPhi(), phase_.rho(), epsilon_)
     ==
        fvm::laplacian(DEpsilonEff(), epsilon_)
      + C1_*Pk()*epsilon_()/k_        // Production
      - fvm::Sp(C2_*phase_.rho()*epsilon_()/k_, epsilon_)  // Destruction
    );
    
    epsilonEqn().relax();
    epsilonEqn().solve();
    
    // Update turbulent viscosity: μt = ρ Cμ k²/ε
    mut_ = phase_.rho()*Cmu_*sqr(k_)/epsilon_;
}
```

**📁 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/turbulenceModels/kEpsilon/kEpsilon.C`

**คำอธิบาย:**
- **Two-Equation Model**: ใช้โมเดล k-ε ซึ่งแก้สมการการถ่ายเทสองสมการสำหรับแต่ละเฟส
- **Source Terms**: พจน์การผลิต Pk และการสลาย ε คำนวณจาก gradient ความเร็ว
- **Phase Coupling**: สมการใช้ฟิลด์เฉพาะเฟส (α, ρ, U) ทำให้แต่ละเฟสมีความปั่นป่วนแยกกัน

**แนวคิดสำคัญ:**
- **TKE Balance**: พลังงานจลน์ความปั่นป่วนสมดุลระหว่างการผลิตและการสลาย
- **Eddy Viscosity**: การประมาณความหนืดจาก k และ ε ทำให้สามารถจำลองความเค้น Reynolds
- **Phase-Specific**: แต่ละเฟสมีค่า k และ ε ของตัวเอง ซึ่งอาจแตกต่างกันมาก

### 4.4 ขั้นตอนการทำงานของระบบ

```
START: Time loop
├── 1. Update phase fractions
├── 2. Solve momentum equations with drag forces
├── 3. Call turbulenceModel.correct() for each phase
│   ├── Update k-equation: ∂(ρk)/∂t + ∇·(ρU k) = ∇·[(μ+μt/σk)∇k] + Pk - ρε
│   └── Update ε-equation: ∂(ρε)/∂t + ∇·(ρU ε) = ∇·[(μ+μt/σε)∇ε] + C1 Pk ε/k - C2 ρ ε²/k
├── 4. Update turbulent viscosity μt
├── 5. Update Reynolds stress tensor R
└── 6. Check convergence
```

### 4.5 โมเดลความปั่นป่วนที่รองรับ

| โมเดล | ชื่อใน OpenFOAM | คุณสมบัติ |
|--------|-------------------|------------|
| k-ε Standard | `kEpsilon` | แบบดั้งเดิม, เหมาะกับการไหลที่พัฒนาเต็มที่ |
| k-ω Standard | `kOmega` | ดีกับชั้นขอบเขตและความดันแปรผันต่ำ |
| k-ω SST | `kOmegaSST` | ผสมผสาน k-ε และ k-ω, ความแม่นยำสูง |
| Spalart-Allmaras | `SpalartAllmaras` | โมเดลสมการเดียว, ประหยัดค่าใช้จ่าย |

---

## 5. โมเดลการถ่ายโอนความร้อนและมวล (Heat & Mass Transfer)

### 5.1 การถ่ายโอนความร้อน

$$Q_k = \sum_{l=1}^{N} h_{kl} A_{kl} (T_l - T_k)$$

โดยที่:
- $h_{kl}$ = สัมประสิทธิ์การถ่ายโอนความร้อนระหว่างเฟส (W/m²·K)
- $A_{kl}$ = ความหนาแน่นพื้นที่ผิวอินเตอร์เฟซ (1/m)
- $T_l, T_k$ = อุณหภูมิของเฟสที่เกี่ยวข้อง

### 5.2 การถ่ายโอนมวล

ควบคุมการเปลี่ยนเฟส โดยต้องเป็นไปตามเงื่อนไขการอนุรักษ์มวลรวม:

$$\sum_k \sum_l \dot{m}_{lk} = 0$$

โดยที่ $\dot{m}_{lk}$ = อัตราการถ่ายโอนมวลจากเฟส $l$ ไปยังเฟส $k$

**กลไกการถ่ายโอนมวลที่รองรับ:**
- การระเหย (Evaporation)
- การควบแน่น (Condensation)
- การเกิดโพรง (Cavitation)

---

## 6. รายละเอียดการนำสมการไปใช้งาน (Code Implementation)

### 6.1 สมการสัดส่วนเฟส (`alphaEqns.H`)

ใช้ติดตามการกระจายตัวของเฟส:

```cpp
// alphaEqns.H - Phase fraction transport equation
forAll(phases, phasei)
{
    phaseModel& phase = phases[phasei];
    volScalarField& alpha = phase;

    // Phase fraction transport equation:
    // ∂(α_k ρ_k)/∂t + ∇·(α_k ρ_k u_k) = Σ ṁ_lk
    fvScalarMatrix alphaEqn
    (
        // Temporal derivative: ∂(α_k ρ_k)/∂t
        fvm::ddt(alpha, phase.rho())
      
        // Convective term: ∇·(α_k ρ_k u_k)
      + fvm::div(alphaPhi, phase.rho())
    
        // Interphase mass transfer source: Σ ṁ_lk
     ==
        phase.massTransferSource()
    );

    // Under-relax for stability
    alphaEqn.relax();
    
    // Solve the equation
    alphaEqn.solve();

    // Bound phase fraction between 0 and 1
    alpha.maxMin(1.0, 0.0);
}

// Normalize to ensure: Σ α_k = 1
scalarField sumAlpha = phases[0];
for (label phasei = 1; phasei < phases.size(); phasei++)
{
    sumAlpha += phases[phasei];
}

forAll(phases, phasei)
{
    phases[phasei] /= sumAlpha;
}
```

**📁 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/alphaEqns.H`

**คำอธิบาย:**
- **Transport Equation**: สมการการนำพาคำนวณการเคลื่อนที่ของแต่ละเฟสผ่านโดเมน
- **Mass Transfer**: เทอม `massTransferSource()` เพิ่ม/ลด α เมื่อมีการเปลี่ยนเฟส
- **Bounding**: การจำกัด α ระหว่าง 0-1 สำคัญต่อเสถียรภาพเชิงตัวเลข
- **Normalization**: ผลรวมของทุกเฟสต้องเท่ากับ 1 เพื่อรักษาความสมดุลของปริมาตร

**แนวคิดสำคัญ:**
- **Conservation**: การเปลี่ยนแปลงของ α ในเฟสหนึ่งต้องสมดุลกับเฟสอื่น
- **Interface Tracking**: α ใกล้ 0.5 แสดงถึงอินเตอร์เฟซระหว่างเฟส
- **Numerical Stability**: การผ่อนคลาย (relaxation) และการจำกัดค่าช่วยป้องกันการหมุนเวียน

### 6.2 สมการโมเมนตัม (`UEqns.H`)

แก้สมการสำหรับแต่ละเฟสพร้อมเทอมการถ่ายโอนระหว่างเฟส:

```cpp
// UEqns.H - Momentum equation for each phase
PtrList<fvVectorMatrix> UEqns(phases.size());

forAll(phases, phasei)
{
    phaseModel& phase = phases[phasei];
    volVectorField& U = phase.U();

    // Momentum equation:
    // ∂(α_k ρ_k u_k)/∂t + ∇·(α_k ρ_k u_k u_k) = 
    //     -α_k ∇p + ∇·τ_k + α_k ρ_k g + M_k
    fvVectorMatrix UEqn
    (
        // Temporal derivative: ∂(α_k ρ_k u_k)/∂t
        fvm::ddt(alpha, phase.rho(), U)
      
        // Convection: ∇·(α_k ρ_k u_k u_k)
      + fvm::div(alphaPhi, phase.rho(), U)
    
        // Pressure gradient: -α_k ∇p
     ==
        - alpha*fvc::grad(p)

        // Viscous stress: ∇·τ_k (via Reynolds stress R)
      + fvc::div(alpha*phase.R())

        // Gravity: α_k ρ_k g
      + alpha*rho*g

        // Interphase momentum transfer: M_k = Σ(F_D + F_L + F_VM + F_TD)
      + phase.interfacialMomentumTransfer()
    );

    // Under-relax for numerical stability
    UEqn.relax();
    
    // Store for pressure correction
    UEqns.set(phasei, new fvVectorMatrix(UEqn));
}
```

**📁 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/UEqns.H`

**คำอธิบาย:**
- **Full Momentum Balance**: สมการรวมทุกแรงที่กระทำต่อเฟส: แรงดัน, ความเค้น, แรงโน้มถ่วง, และแรงระหว่างเฟส
- **Interfacial Transfer**: เทอม `interfacialMomentumTransfer()` รวม drag, lift, virtual mass, และ turbulent dispersion
- **Implicit Treatment**: พจน์ unsteady และ convection ถูก treat แบบ implicit (ด้วย `fvm`) เพื่อเสถียรภาพ
- **Explicit Terms**: พจน์ที่เหลี่ยมเฉียบ (เช่น แรงดัน) ถูก treat แบบ explicit (ด้วย `fvc`)

**แนวคิดสำคัญ:**
- **Phase Coupling**: สมการโมเมนตัมของแต่ละเฟส coupled กันผ่านแรงระหว่างเฟส
- **Segregated Approach**: แต่ละเฟสถูกแก้แยกกัน แล้วจึง coupling ผ่าน pressure correction
- **Pressure-Velocity Coupling**: ความดันเป็นตัวแปรร่วมกันที่ enforce ความต่อเนื่อง

### 6.3 สมการความดัน (`pEqn.H`)

ใช้รักษาความต่อเนื่องของมวลรวม โดยอิงจากอัลกอริทึม **PISO/PIMPLE**:

#### อัลกอริทึม PISO

1. **ขั้นตอนการพยากรณ์**: แก้สมการโมเมนตัมด้วยฟิลด์ความดันปัจจุบัน
2. **การแก้ไขความดัน**: แก้สมการ Poisson สำหรับความดัน:
   $$\nabla \cdot \left(\frac{1}{A_k} \nabla p\right) = \nabla \cdot \mathbf{H}_k$$
3. **การแก้ไขความเร็ว**: อัปเดตความเร็วโดยใช้ไล่ระดับความดัน:
   $$\mathbf{u}_k^{n+1} = \mathbf{u}_k^* - \frac{1}{A_k} \nabla p$$

```cpp
// pEqn.H - Pressure-velocity coupling with PISO/PIMPLE

// Non-orthogonal correction loop
for (int nonOrth = 0; nonOrth <= nNonOrthCorr; nonOrth++)
{
    // Pressure equation derived from continuity:
    // ∇·(Σ α_k ρ_k u_k) = 0
    // Discretized as: ∇·(H/A) - ∇·(1/A ∇p) = 0
    // => ∇·(1/A ∇p) = ∇·(H/A)
    
    fvScalarMatrix pEqn
    (
        fvm::laplacian(rUAf, p)
     ==
        fvc::div(phiHbyA)
    );

    // Add reference cell to prevent pressure drift
    pEqn.setReference(pRefCell, pRefValue);

    // Solve pressure equation
    pEqn.solve();

    // Correct phase fluxes with new pressure field
    // φ_k* = φ_k(H/A) - (1/A) ∇p·S_f
    forAll(phases, phasei)
    {
        phiPhis[phasei] -= rUAf*fvc::snGrad(p)*mesh_.magSf();
    }
}

// Correct phase velocities
forAll(phases, phasei)
{
    // u_k^(n+1) = u_k* - (1/A) ∇p
    phases[phasei].U() = UHbyA[phasei] - rAU[phasei]*fvc::grad(p);
}

// Continuity check: Σ ∇·(α_k φ_k) should be small
#include "continuityErrs.H"
```

**📁 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/pEqn.H`

**คำอธิบาย:**
- **Poisson Equation**: สมการความดันเป็นสมการ Poisson ที่ derived จากสมการความต่อเนื่อง
- **Flux Correction**: การแก้ไข flux ด้วย gradient ของความดันทำให้ความเร็ว satisfy continuity
- **Multiple Correctors**: PISO/PIMPLE ใช้หลาย correction เพื่อความแม่นยำและเสถียรภาพ
- **Reference Pressure**: ความดันต้องถูก fix ที่เซลล์หนึ่งเพื่อป้องกัน singular matrix

**แนวคิดสำคัญ:**
- **Mass Conservation**: การแก้สมการความดัน enforce ให้ total mass conserved
- **Segregated Solver**: ความเร็วและความดันถูกแก้แยกกันแล้ว coupled ผ่าน iterative correction
- **Multiphase Extension**: สมการความดันรวม contribution จากทุกเฟส

---

## 7. แนวทางการขยายโมเดล (Extensibility)

หากต้องการเพิ่มโมเดลแรง Drag ใหม่:

1. สร้างคลาสใหม่ที่สืบทอดจาก `dragModel`
2. นำฟังก์ชัน `F()`, `Cd()`, `K()` ไปใช้งานตามสูตรคณิตศาสตร์ที่ต้องการ
3. ลงทะเบียนโมเดลด้วยมาโคร `defineTypeName` และ `addToRunTimeSelectionTable`
4. เรียกใช้งานในไฟล์ `constant/phaseProperties` ของเคสที่ต้องการ

### ตัวอย่างการลงทะเบียนโมเดล

```cpp
// In customDragModel.C - Register new drag model

// Define type name for runtime selection
defineTypeNameAndDebug(customDragModel, 0);

// Add to runtime selection table
addToRunTimeSelectionTable
(
    dragModel,                    // Base class
    customDragModel,             // Derived class
    dictionary                   // Constructor argument type
);
```

**📁 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/interfacialModels/dragModels/customDragModel/customDragModel.C`

**คำอธิบาย:**
- **Runtime Selection Macros**: OpenFOAM ใช้ macros ในการลงทะเบียนคลาสลงในระบบ selection
- **Dictionary Constructor**: โมเดลต้องมี constructor ที่รับ `dictionary` เพื่ออ่านพารามิเตอร์
- **Automatic Discovery**: เมื่อถูก compile, โมเดลจะถูกเพิ่มลงใน runtime tables โดยอัตโนมัติ

**แนวคิดสำคัญ:**
- **Plug-in Architecture**: ผู้ใช้สามารถเพิ่มโมเดลใหม่โดยไม่ต้องแก้ไขโค้ดหลักของ solver
- **Template Pattern**: OpenFOAM กำหนด interface และผู้ใช้ implement logic เฉพาะ
- **Research Flexibility**: เหมาะสำหรับงานวิจัยที่ต้องการทดลองโมเดลฟิสิกส์ใหม่ๆ

### การตั้งค่าใน phaseProperties

```foam
// In constant/phaseProperties

drag
{
    type        customDragModel;
    parameter1  value1;
    parameter2  value2;
}
```

**คำอธิบาย:**
- **Type Keyword**: ระบุชื่อโมเดลที่จะใช้ ซึ่งตรงกับ `TypeName` ในโค้ด
- **Custom Parameters**: โมเดลสามารถอ่านพารามิเตอร์เพิ่มเติมจาก dictionary
- **Multiple Phase Pairs**: สามารถระบุโมเดลที่แตกต่างกันสำหรับแต่ละคู่เฟส

สถาปัตยกรรมนี้ช่วยให้ OpenFOAM สามารถรองรับงานวิจัยและการใช้งานในอุตสาหกรรมที่ต้องการความละเอียดและความซับซ้อนของฟิสิกส์ในระดับสูงได้

---

*อ้างอิง: วิเคราะห์ตามซอร์สโค้ด OpenFOAM-10, dragModel.H และกลไก interfacialMomentumTransfer ของ multiphaseEulerFoam*