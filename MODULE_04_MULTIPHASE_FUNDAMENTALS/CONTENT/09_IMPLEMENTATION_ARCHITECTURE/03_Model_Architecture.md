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
// โมเดลการลากตัวฐาน
class dragModel
{
public:
    // Virtual destructor
    virtual ~dragModel() {}

    // คำนวณแรงลากตัว
    virtual tmp<volVectorField> F
    (
        const phaseModel& phase1,
        const phaseModel& phase2
    ) const = 0;

    // เมธอด factory สำหรับการสร้างโมเดล
    static autoPtr<dragModel> New
    (
        const dictionary& dict,
        const phasePair& pair
    );
};
```

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
// โมเดลการลากตัว Schiller-Naumann
class SchillerNaumannDrag
:
    public dragModel
{
private:
    const phasePair& pair_;

public:
    // Constructor
    SchillerNaumannDrag
    (
        const dictionary& dict,
        const phasePair& pair
    );

    // คำนวณแรงลากตัว
    virtual tmp<volVectorField> F
    (
        const phaseModel& phase1,
        const phaseModel& phase2
    ) const;
};
```

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
// โมเดลความปั่นป่วนแบบหลายเฟส
class phaseCompressibleTurbulenceModel
:
    public compressible::turbulenceModel
{
protected:
    const phaseModel& phase_;
    const phaseSystem& phaseSystem_;

public:
    // Constructor
    phaseCompressibleTurbulenceModel
    (
        const volScalarField& rho,
        const volVectorField& U,
        const surfaceScalarField& phi,
        const phaseModel& phase
    );

    // คำนวณความเค้น Reynolds
    virtual tmp<volSymmTensorField> R() const;

    // คำนวณความหนืดความปั่นป่วน
    virtual tmp<volScalarField> mut() const;

    // ขั้นตอนการแก้ไข
    virtual void correct();
};
```

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
// alphaEqns.H - Phase fraction transport
forAll(phases, phasei)
{
    phaseModel& phase = phases[phasei];
    volScalarField& alpha = phase;

    // Phase fraction equation
    fvScalarMatrix alphaEqn
    (
        fvm::ddt(alpha, phase.rho())
      + fvm::div(alphaPhi, phase.rho())
    ==
        phase.massTransferSource()  // Interphase mass transfer
    );

    alphaEqn.relax();
    alphaEqn.solve();

    // Apply bounding
    alpha.maxMin(1.0, 0.0);
}

// Ensure phase fractions sum to unity
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

**การจับคู่โค้ดกับทฤษฎี:**
- `fvm::ddt(alpha, phase.rho())` → $\frac{\partial (\alpha_k \rho_k)}{\partial t}$ (อนุพันธ์เชิงเวลา)
- `fvm::div(alphaPhi, phase.rho())` → $\nabla \cdot (\alpha_k \rho_k \mathbf{u}_k)$ (พจน์นำพา)
- `phase.massTransferSource()` → $\sum_{l=1}^{N} \dot{m}_{lk}$ (การถ่ายโอนมวลระหว่างเฟส)

### 6.2 สมการโมเมนตัม (`UEqns.H`)

แก้สมการสำหรับแต่ละเฟสพร้อมเทอมการถ่ายโอนระหว่างเฟส:

```cpp
// UEqns.H - Momentum equation solution
PtrList<fvVectorMatrix> UEqns(phases.size());

forAll(phases, phasei)
{
    phaseModel& phase = phases[phasei];
    volVectorField& U = phase.U();

    // Momentum equation matrix
    fvVectorMatrix UEqn
    (
        fvm::ddt(alpha, phase.rho(), U)
      + fvm::div(alphaPhi, phase.rho(), U)
    ==
        // Pressure gradient term
        - alpha*fvc::grad(p)

        // Viscous stress term
      + fvc::div(alpha*phase.R())

        // Gravity term
      + alpha*rho*g

        // Interphase momentum transfer
      + phase.interfacialMomentumTransfer()
    );

    // Relax and solve
    UEqn.relax();
    UEqns.set(phasei, new fvVectorMatrix(UEqn));
}
```

**การจับคู่โค้ดกับทฤษฎี:**
- `fvm::ddt(alpha, phase.rho(), U)` → $\frac{\partial (\alpha_k \rho_k \mathbf{u}_k)}{\partial t}$
- `fvm::div(alphaPhi, phase.rho(), U)` → $\nabla \cdot (\alpha_k \rho_k \mathbf{u}_k \mathbf{u}_k)$
- `- alpha*fvc::grad(p)` → $-\alpha_k \nabla p$ (ไล่ระดับความดัน)
- `fvc::div(alpha*phase.R())` → $\nabla \cdot \boldsymbol{\tau}_k$ (ความเค้นเหนียว)
- `alpha*rho*g` → $\alpha_k \rho_k \mathbf{g}$ (แรงโน้มถ่วง)
- `phase.interfacialMomentumTransfer()` → $\mathbf{M}_k$ (การถ่ายโอนโมเมนตัมระหว่างเฟส)

### 6.3 สมการความดัน (`pEqn.H`)

ใช้รักษาความต่อเนื่องของมวลรวม โดยอิงจากอัลกอริทึม **PISO/PIMPLE**:

#### อัลกอริทึม PISO

1. **ขั้นตอนการพยากรณ์**: แก้สมการโมเมนตัมด้วยฟิลด์ความดันปัจจุบัน
2. **การแก้ไขความดัน**: แก้สมการ Poisson สำหรับความดัน:
   $$\nabla \cdot \left(\frac{1}{A_k} \nabla p\right) = \nabla \cdot \mathbf{H}_k$$
3. **การแก้ไขความเร็ว**: อัปเดตความเร็วโดยใช้ไล่ระดับความดัน:
   $$\mathbf{u}_k^{n+1} = \mathbf{u}_k^* - \frac{1}{A_k} \nabla p$$

```cpp
// pEqn.H - Pressure correction equation
for (int corr = 0; corr < nCorr; corr++)
{
    // Calculate pressure fluxes
    surfaceScalarField rUAf
    (
        "rUAf",
        interpolated(rAU)
    );

    // Phase fluxes
    PtrList<surfaceScalarField> phiPhis(phases.size());
    forAll(phases, phasei)
    {
        const phaseModel& phase = phases[phasei];
        const fvVectorMatrix& UEqn = UEqns[phasei];

        phiPhis.set
        (
            phasei,
            new surfaceScalarField
            (
                "phi" + phase.name(),
                fvc::interpolate(phase.U()) & mesh_.Sf()
            )
        );
    }

    // Pressure equation matrix
    fvScalarMatrix pEqn
    (
        fvm::laplacian(rUAf, p) ==
        fvc::div(phiHbyA)
    );

    // Solve pressure equation
    pEqn.solve();

    // Correct phase fluxes
    forAll(phases, phasei)
    {
        phiPhis[phasei] -= rUAf*fvc::snGrad(p)*mesh_.magSf();
    }
}
```

---

## 7. แนวทางการขยายโมเดล (Extensibility)

หากต้องการเพิ่มโมเดลแรง Drag ใหม่:

1. สร้างคลาสใหม่ที่สืบทอดจาก `dragModel`
2. นำฟังก์ชัน `F()`, `Cd()`, `K()` ไปใช้งานตามสูตรคณิตศาสตร์ที่ต้องการ
3. ลงทะเบียนโมเดลด้วยมาโคร `defineTypeName` และ `addToRunTimeSelectionTable`
4. เรียกใช้งานในไฟล์ `constant/phaseProperties` ของเคสที่ต้องการ

### ตัวอย่างการลงทะเบียนโมเดล

```cpp
// ในไฟล์ .C ของโมเดลใหม่
defineTypeNameAndDebug(customDragModel, 0);
addToRunTimeSelectionTable
(
    dragModel,
    customDragModel,
    dictionary
);
```

### การตั้งค่าใน phaseProperties

```foam
drag
{
    type        customDragModel;
    parameter1  value1;
    parameter2  value2;
}
```

สถาปัตยกรรมนี้ช่วยให้ OpenFOAM สามารถรองรับงานวิจัยและการใช้งานในอุตสาหกรรมที่ต้องการความละเอียดและความซับซ้อนของฟิสิกส์ในระดับสูงได้

---

*อ้างอิง: วิเคราะห์ตามซอร์สโค้ด OpenFOAM-10, dragModel.H และกลไก interfacialMomentumTransfer ของ multiphaseEulerFoam*
