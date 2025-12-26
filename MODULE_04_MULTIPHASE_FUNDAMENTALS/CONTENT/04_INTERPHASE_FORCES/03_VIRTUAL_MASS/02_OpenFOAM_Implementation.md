# การนำ Virtual Mass ไปใช้ใน OpenFOAM

## ภาพรวม

**Virtual Mass** ในการไหลแบบหลายเฟส (multiphase flows) หมายถึง แรงเฉื่อยเพิ่มเติมที่จำเป็นในการเร่งเฟสต่อเนื่องที่อยู่รอบๆ เมื่ออนุภาคเฟสที่กระจายตัว (dispersed phase particles) ถูกเร่ง

ส่วนนี้จะบันทึกการนำ Virtual Mass Models ไปใช้ใน OpenFOAM ภายใต้กรอบการทำงานแบบ **Eulerian-Eulerian multiphase**

---

## 1. สถาปัตยกรรมคลาส (Class Architecture)

### 1.1 คลาสพื้นฐาน VirtualMassModel

สถาปัตยกรรม Virtual Mass Model เป็นไปตามรูปแบบการออกแบบแบบ **Polymorphic** ของ OpenFOAM โดยมีคลาสพื้นฐานแบบ Pure virtual:

```cpp
// Base virtual mass model class
class virtualMassModel
{
public:
    // Calculate virtual mass coefficient
    virtual tmp<volScalarField> Cvm() const = 0;

    // Calculate virtual mass force
    virtual tmp<volVectorField> Fi() const = 0;

    // Virtual destructor
    virtual ~virtualMassModel() {}
};
```

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C:19`

**📖 Explanation:** คลาสพื้นฐาน `virtualMassModel` กำหนด interface สำหรับการคำนวณแรง virtual mass ในระบบ multiphase โดยใช้รูปแบบ polymorphic design pattern ที่ช่วยให้สามารถสลับรุ่นของ virtual mass model ที่แตกต่างกันได้ในขณะทำงาน (runtime)

**🔑 Key Concepts:**
- **Pure Virtual Methods:** `Cvm()` และ `Fi()` เป็นเมธอดแบบ pure virtual ที่ต้องถูก implement ใน derived classes
- **Runtime Selection:** ระบบ selection ของ OpenFOAM ช่วยให้เลือก model ผ่าน dictionary
- **Return Types:** ใช้ `tmp<volScalarField>` และ `tmp<volVectorField>` เพื่อการจัดการหน่วยความจำที่มีประสิทธิภาพ

**การออกแบบเชิง Polymorphic:**

การออกแบบนี้ช่วยให้สามารถเลือกรุ่น Virtual Mass ที่แตกต่างกันได้ในขณะทำงาน (runtime) ผ่านกลไกการเลือกขณะทำงานของ OpenFOAM

คลาสพื้นฐานกำหนดเมธอดแบบ Pure virtual สองเมธอด:

- **`Cvm()`**: ส่งคืนสนามสัมประสิทธิ์ Virtual Mass (ไม่มีหน่วย)
- **`Fi()`**: ส่งคืนสนามเวกเตอร์แรง Virtual Mass

### 1.2 โครงสร้างคลาสใน C++

```cpp
class virtualMassModel
{
public:
    // Calculate virtual mass coefficient
    virtual tmp<volScalarField> Cvm() const = 0;

    // Calculate virtual mass force
    virtual tmp<volVectorField> Fi() const = 0;
};
```

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C:19`

**📖 Explanation:** ส่วนประกอบหลักของคลาส virtualMassModel ที่กำหนด interface สำหรับการคำนวณค่าสัมประสิทธิ์และแรง virtual mass โดยใช้ template class `tmp` เพื่อ optimization ของการจัดการหน่วยความจำใน OpenFOAM

**🔑 Key Concepts:**
- **Template Management:** ใช้ `tmp<>` เพื่อลดการ copy ของ field objects
- **Const Correctness:** ใช้ `const`  qualifier เพื่อรับประกันว่าเมธอดไม่แก้ไขสถานะของ object
- **Field Types:** `volScalarField` และ `volVectorField` เป็น field types หลักใน OpenFOAM

---

## 2. รุ่น Constant Virtual Mass Model

คลาส `constantVirtualMass` นำ Virtual Mass Model ที่ง่ายที่สุดมาใช้ โดยมีสัมประสิทธิ์คงที่ที่ผู้ใช้กำหนด:

### 2.1 การนำไปใช้ใน C++

```cpp
class constantVirtualMass
:
    public virtualMassModel
{
private:
    // Constant virtual mass coefficient
    dimensionedScalar Cvm_;

public:
    // Constructor from dictionary and phase pair
    constantVirtualMass
    (
        const dictionary& dict,
        const phasePair& pair
    )
    :
        virtualMassModel(dict, pair),
        Cvm_("Cvm", dimless, dict)
    {}

    // Calculate virtual mass coefficient (returns constant value)
    virtual tmp<volScalarField> Cvm() const
    {
        return tmp<volScalarField>::New
        (
            "Cvm",
            volScalarField::New
            (
                "Cvm",
                pair_.mesh(),
                Cvm_
            )
        );
    }

    // Calculate virtual mass force per unit volume
    virtual tmp<volVectorField> Fi() const
    {
        // Get phase references
        const phaseModel& phase1 = pair_.phase1();
        const phaseModel& phase2 = pair_.phase2();

        // Get phase properties
        const volScalarField& alpha1 = phase1.alpha();
        const volScalarField& alpha2 = phase2.alpha();
        const volScalarField& rho1 = phase1.rho();
        const volVectorField& U1 = phase1.U();
        const volVectorField& U2 = phase2.U();

        // Virtual mass coefficient field
        const volScalarField Cvm = this->Cvm();

        // Material derivatives (acceleration terms)
        volVectorField DUDt1 = fvc::ddt(U1) + fvc::div(U1, U1);
        volVectorField DUDt2 = fvc::ddt(U2) + fvc::div(U2, U2);

        // Virtual mass force calculation
        return Cvm * rho1 * alpha1 * alpha2 * (DUDt2 - DUDt1);
    }
};
```

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C:87-105`

**📖 Explanation:** คลาส `constantVirtualMass` ใช้ค่าสัมประสิทธิ์คงที่ที่กำหนดใน dictionary และคำนวณแรง virtual mass จากความแตกต่างของ material derivative (acceleration) ระหว่างสองเฟส โดยใช้ finite volume calculus ของ OpenFOAM

**🔑 Key Concepts:**
- **Phase Pair Access:** `pair_.phase1()` และ `pair_.phase2()` ใช้เข้าถึง properties ของแต่ละเฟส
- **Material Derivative:** คำนวณด้วย `fvc::ddt(U) + fvc::div(U, U)` สำหรับ local และ convective acceleration
- **Field Operations:** ใช้ `fvc` (finite volume calculus) สำหรับ explicit operations
- **Density Reference:** ใช้ความหนาแน่นของ phase1 เป็น reference density ในการคำนวณ

### 2.2 สูตรทางคณิตศาสตร์

แรง Virtual Mass แบบคงที่คำนวณโดยใช้สูตรมาตรฐาน:

$$\mathbf{F}_{vm} = C_{vm} \rho_1 \alpha_1 \alpha_2 \left(\frac{D\mathbf{u}_2}{Dt} - \frac{D\mathbf{u}_1}{Dt}\right)$$

โดยที่:
- $C_{vm}$ คือ สัมประสิทธิ์ Virtual Mass (โดยทั่วไปคือ 0.5 สำหรับทรงกลม)
- $\rho_1$ คือ ความหนาแน่นของเฟสต่อเนื่อง
- $\alpha_1, \alpha_2$ คือ เศษส่วนปริมาตรของทั้งสองเฟส
- $\frac{D\mathbf{u}_i}{Dt}$ คือ อนุพันธ์เชิงมาเตอร์ (material derivative) ของความเร็วเฟส

อนุพันธ์เชิงมาเตอร์ คำนวณโดยใช้รูปแบบการพา (convective form):

$$\frac{D\mathbf{u}_i}{Dt} = \frac{\partial \mathbf{u}_i}{\partial t} + (\mathbf{u}_i \cdot \nabla)\mathbf{u}_i$$

---

## 3. รุ่น Shape-Dependent Virtual Mass Model

คลาส `shapeVirtualMass` ขยายการสร้างแบบจำลอง Virtual Mass เพื่อพิจารณาผลกระทบของรูปร่างอนุภาค:

### 3.1 การนำไปใช้ใน C++

```cpp
class shapeVirtualMass
:
    public virtualMassModel
{
private:
    // Particle shape specification
    word shapeType_;

    // Aspect ratio for non-spherical particles
    autoPtr<volScalarField> aspectRatio_;

public:
    // Calculate shape-dependent coefficient
    virtual tmp<volScalarField> Cvm() const
    {
        // Initialize with default spherical value
        tmp<volScalarField> tCvm = volScalarField::New("Cvm", pair_.mesh(), 0.5);
        volScalarField& Cvm = tCvm.ref();

        // Apply shape-dependent corrections
        if (shapeType_ == "ellipsoid")
        {
            const volScalarField& beta = aspectRatio_();

            // Cell-wise iteration for spatial variation
            forAll(Cvm, celli)
            {
                scalar beta_local = beta[celli];

                if (beta_local > 1.0) // Oblate spheroid
                {
                    // Disk-like particle formulation
                    Cvm[celli] = 2.0/(3.0*beta_local) /
                                (beta_local/(beta_local - sqrt(beta_local*beta_local - 1.0)));
                }
                else // Prolate spheroid
                {
                    // Rod-like particle formulation
                    Cvm[celli] = (log(2.0/beta_local) - 0.5) /
                                (log(2.0/beta_local) + 0.5);
                }
            }
        }

        return tCvm;
    }
};
```

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C:87-105`

**📖 Explanation:** คลาส `shapeVirtualMass` คำนวณค่าสัมประสิทธิ์ virtual mass ที่ขึ้นกับรูปร่างอนุภาค โดยใช้สูตรทางทฤษฎีสำหรับ ellipsoidal particles ที่พิจารณาอัตราส่วนภาพ (aspect ratio) และแยกการคำนวณระหว่าง oblate (disk-like) และ prolate (rod-like) spheroids

**🔑 Key Concepts:**
- **Spatial Variation:** ใช้ `forAll` loop เพื่อคำนวณค่า Cvm แบบ cell-by-cell
- **AutoPtr Management:** ใช้ `autoPtr<volScalarField>` สำหรับ optional field ที่มีหรือไม่มีได้
- **Aspect Ratio Definition:** β > 1 สำหรับ oblate, β < 1 สำหรับ prolate
- **Theoretical Formulations:** ใช้สูตร analytical solutions สำหรับ potential flow รอบ ellipsoids

### 3.2 สูตรสำหรับอนุภาคทรงรี (Ellipsoidal Particle Formulations)

สำหรับอนุภาคทรงรี สัมประสิทธิ์ Virtual Mass จะขึ้นอยู่กับอัตราส่วนภาพ (aspect ratio) $\beta = a/b$ โดยที่ $a$ คือแกนหลักและ $b$ คือแกนรอง:

**Oblate Spheroid (รูปจาน, $\beta > 1$):**
$$C_{vm} = \frac{2}{3\beta\left[\beta - \sqrt{\beta^2 - 1}\right]}$$

**Prolate Spheroid (รูปแท่ง, $\beta < 1$):**
$$C_{vm} = \frac{\ln(2/\beta) - 0.5}{\ln(2/\beta) + 0.5}$$

---

## 4. การคำนวณใน Solver (Numerical Workflow)

ใน Solver เช่น `multiphaseEulerFoam`, แรงมวลเสมือนคำนวณจากความแตกต่างของอนุพันธ์รวม (Material Derivative) ของความเร็วทั้งสองเฟส:

### 4.1 การคำนวณอนุพันธ์รวม

$$\frac{D\mathbf{u}}{Dt} = \frac{\partial \mathbf{u}}{\partial t} + \mathbf{u} \cdot \nabla \mathbf{u}$$

ในโค้ด OpenFOAM:

```cpp
// Material derivative calculation using finite volume calculus
volVectorField DUDt1 = fvc::ddt(U1) + fvc::div(U1, U1);
volVectorField DUDt2 = fvc::ddt(U2) + fvc::div(U2, U2);
```

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C:87-105`

**📖 Explanation:** การคำนวณ material derivative ใน OpenFOAM ใช้ finite volume calculus (fvc) สำหรับ explicit operations โดยแยก local acceleration term (`fvc::ddt`) และ convective acceleration term (`fvc::div`) ตาม Eulerian specification ของ material derivative

**🔑 Key Concepts:**
- **Local Acceleration:** `fvc::ddt(U)` คำนวณ ∂U/∂t
- **Convective Acceleration:** `fvc::div(U, U)` คำนวณ (U·∇)U
- **Explicit Evaluation:** ใช้ `fvc` namespace สำหรับ explicit field operations
- **Vector Field:** ผลลัพธ์เป็น `volVectorField` ที่เก็บค่า acceleration ทุก cell

### 4.2 การรวมแรงเข้ากับสมการโมเมนตัม

$$\mathbf{F}_{vm} = C_{vm} \rho_1 \alpha_1 \alpha_2 (DUDt_2 - DUDt_1)$$

---

## 5. การรวมเข้ากับ Multiphase Solvers

### 5.1 การรวมสมการโมเมนตัม

แรง Virtual Mass ถูกรวมเข้ากับสมการโมเมนตัมของเฟสในฐานะเทอมการถ่ายโอนโมเมนตัมระหว่างเฟสเพิ่มเติม

สำหรับเฟส $i$ สมการโมเมนตัมจะเป็น:

$$\frac{\partial (\alpha_i \rho_i \mathbf{u}_i)}{\partial t} + \nabla \cdot (\alpha_i \rho_i \mathbf{u}_i \mathbf{u}_i) = -\alpha_i \nabla p_i + \nabla \cdot \boldsymbol{\tau}_i + \alpha_i \rho_i \mathbf{g} + \sum_{j \neq i} \mathbf{M}_{ij}$$

โดยที่ $\mathbf{M}_{ij}$ รวมถึงแรง Virtual Mass:

$$\mathbf{M}_{vm,ij} = C_{vm} \rho_i \alpha_i \alpha_j \left(\frac{D\mathbf{u}_j}{Dt} - \frac{D\mathbf{u}_i}{Dt}\right)$$

### 5.2 การเชื่อมโยงกับแรงฉุด (Drag Forces)

แรง Virtual Mass ทำงานร่วมกับแรงฉุด (drag forces) เพื่อให้การถ่ายโอนโมเมนตัมระหว่างเฟสที่สมบูรณ์:

$$\mathbf{M}_{ij} = \mathbf{F}_{drag,ij} + \mathbf{F}_{vm,ij} + \mathbf{F}_{lift,ij} + \mathbf{F}_{turbulent,dispersion,ij}$$

แนวทางที่ครอบคลุมนี้ช่วยให้มั่นใจได้ถึงการแสดงปรากฏการณ์ระหว่างเฟสที่สำคัญทั้งหมดในการไหลแบบหลายเฟสได้อย่างแม่นยำ

---

## 6. ข้อควรพิจารณาด้านเสถียรภาพ (Numerical Stability)

เนื่องจากเทอมความเร่ง ($\partial \mathbf{u}/\partial t$) มักจะ "แข็ง" (Stiff) และอาจนำไปสู่การแกว่งกวัด (Oscillations) OpenFOAM จึงใช้กลยุทธ์ดังนี้:

### 6.1 การจัดการแบบ Implicit (`fvm::Sp`)

เพื่อเพิ่มความเป็นแนวทแยง (Diagonal dominance) ของเมทริกซ์โมเมนตัม:

```cpp
// Add implicit virtual mass contribution to diagonal
U1Eqn += fvm::Sp(Cvm*rho1*alpha1*alpha2/dt, U1);
```

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C:87-105`

**📖 Explanation:** การใช้ `fvm::Sp` (finite volume method - Source term with Positive diagonal) เพิ่ม contribution ของ virtual mass force ลงในเมทริกซ์สัมประสิทธิ์แบบ implicit ซึ่งช่วยเพิ่ม diagonal dominance และปรับปรุงความเสถียรของการแก้ระบบเชิงเส้น

**🔑 Key Concepts:**
- **Implicit Treatment:** ใช้ `fvm` namespace สำหรับ implicit discretization
- **Diagonal Enhancement:** `Sp` เพิ่มค่าบน diagonal ของเมทริกซ์
- **Time Step Scaling:** หารด้วย `dt` เพื่อ dimensional consistency
- **Stability Improvement:** Implicit treatment ลดข้อจำกัดของ time step

### 6.2 ข้อจำกัดของ Time Step (CFL Constraint)

แรงมวลเสมือนเพิ่มความเร็วเสียงประสิทธิผล (Effective sound speed) ในระบบ ซึ่งอาจต้องการ Time step ที่เล็กลง:

$$\Delta t \leq \frac{\Delta x}{|\mathbf{u}| + \sqrt{\frac{C_{vm} \rho_c}{\rho_d + C_{vm} \rho_c}}}$$

---

## 7. การจัดการแบบ Explicit เทียบกับ Implicit

### 7.1 Explicit Virtual Mass

$$\mathbf{F}_{VM}^{n+1} = \mathbf{F}_{VM}(\mathbf{u}^n, \mathbf{u}^n)$$

การจัดการ Explicit virtual mass จะประเมินแรง virtual mass โดยใช้ข้อมูลจากระดับเวลา (time level) ก่อนหน้า $t^n$ เท่านั้น

**ข้อดีของรูปแบบ Explicit:**

- **ความง่ายในการนำไปใช้ (Implementation Simplicity)**: รูปแบบ Explicit ต้องการเพียงตัวแปรในระดับเวลาปัจจุบัน ทำให้ง่ายต่อการนำไปใช้โดยไม่ต้องปรับเปลี่ยนโครงสร้างของระบบเชิงเส้น (linear system)

- **ประสิทธิภาพในการคำนวณ (Computational Efficiency)**: เนื่องจากไม่มีการเพิ่มเทอมที่เชื่อมโยง (coupling terms) เข้าไปในเมทริกซ์โมเมนตัม (momentum matrix) ต้นทุนการคำนวณต่อขั้นเวลา (time step) จึงค่อนข้างต่ำ

**ข้อจำกัดด้านเสถียรภาพ (Stability Limitations):** แนวทาง Explicit จะมีข้อจำกัดเรื่องขนาดของขั้นเวลาที่ถูกควบคุมโดยเงื่อนไข Courant-Friedrichs-Lewy (CFL):

$$\Delta t \leq \sqrt{\frac{C_{VM} \rho_1 \rho_2 \Delta x^2}{2(\rho_1 + \rho_2) \mu}}$$

### 7.2 Implicit Virtual Mass

$$\mathbf{F}_{VM}^{n+1} = \mathbf{F}_{VM}(\mathbf{u}^{n+1}, \mathbf{u}^{n+1})$$

การจัดการ Implicit virtual mass ใช้ความเร็วที่ไม่ทราบค่า ณ ระดับเวลาถัดไป $t^{n+1}$ ส่งผลให้เกิดรูปแบบที่เชื่อมโยงกันอย่างสมบูรณ์ (fully coupled formulation)

**ประโยชน์ของรูปแบบ Implicit:**

- **เสถียรภาพที่เพิ่มขึ้น (Enhanced Stability)**: แนวทาง Implicit จะขจัดข้อจำกัดเรื่องขนาดขั้นเวลาที่เกี่ยวข้องกับ virtual mass ทำให้สามารถใช้ขั้นเวลาที่ใหญ่ขึ้นมากในขณะที่ยังคงเสถียรภาพเชิงตัวเลข (numerical stability) ไว้ได้

- **การปรับเปลี่ยนระบบเชิงเส้น (Linear System Modification)**: เทอม Implicit จะส่งผลต่อความเป็นแนวทแยงหลัก (diagonal dominance) ของเมทริกซ์สัมประสิทธิ์ (coefficient matrix) ซึ่งช่วยปรับปรุงการกำหนดเงื่อนไขของระบบเชิงเส้น (conditioning of the linear system)

### 7.3 รูปแบบกึ่ง Implicit (Semi-Implicit Formulation)

การประนีประนอมที่พบบ่อยระหว่างเสถียรภาพและประสิทธิภาพในการคำนวณคือรูปแบบกึ่ง Implicit:

$$\mathbf{F}_{VM}^{n+1} = C_{VM} \rho \alpha_1 \alpha_2 \left( \frac{D\mathbf{u}_2^n}{Dt} - \frac{D\mathbf{u}_1^{n+1}}{Dt} \right)$$

รูปแบบนี้จัดการแรง virtual mass แบบกึ่ง Implicit โดยรวมเอาอัตราเร่งของเฟส 1 ที่ $t^{n+1}$ ในขณะที่ใช้อัตราเร่งของเฟส 2 จากระดับเวลาก่อนหน้า $t^n$

**ข้อดีของรูปแบบกึ่ง Implicit:**

- **แนวทางที่สมดุล (Balanced Approach)**: รูปแบบกึ่ง Implicit รักษาลักษณะเสถียรภาพที่เหมาะสมในขณะที่ยังคงต้นทุนการคำนวณที่จัดการได้

- **การเชื่อมโยงบางส่วน (Partial Coupling)**: ต้องการเพียงเฟสเดียวที่ต้องจัดการแบบ Implicit ซึ่งช่วยลดความซับซ้อนของระบบเชิงเส้นเมื่อเทียบกับรูปแบบ Implicit เต็มรูปแบบ

### 7.4 การนำ Implicit Virtual Mass ไปใช้ใน OpenFOAM

ใน OpenFOAM การนำ Implicit virtual mass ไปใช้ปรากฏในสมการโมเมนตัมในรูปของส่วนประกอบเมทริกซ์แนวทแยง (diagonal matrix contributions):

```cpp
// Implicit virtual mass contribution to momentum equation
fvVectorMatrix U1Eqn
(
    fvm::ddt(alpha1, rho1, U1)
  + fvm::div(alphaPhi1, rho1, U1)
 ==
    // Other terms...
  + fvm::Sp(Cvm*rho1*alpha1*alpha2/dt, U1)  // Implicit virtual mass
  - Cvm*rho1*alpha1*alpha2*(DUDt2/dt)      // Explicit part
);
```

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C:87-105`

**📖 Explanation:** การ implement implicit virtual mass ใน OpenFOAM ใช้ `fvm::Sp` เพื่อเพิ่ม contribution ลงใน diagonal ของเมทริกซ์ และลบส่วน explicit ที่มาจาก acceleration ของเฟสอื่น ซึ่งสร้างรูปแบบ semi-implicit treatment ที่สมดุลระหว่างเสถียรภาพและประสิทธิภาพ

**🔑 Key Concepts:**
- **Matrix Construction:** `fvVectorMatrix` เป็น container สำหรับสมการโมเมนตัม
- **Implicit Diagonal:** `fvm::Sp` เพิ่มค่าลง diagonal แบบ implicit
- **Explicit Source:** ส่วนที่เป็น negative คือ explicit source term
- **Time Scaling:** การหารด้วย `dt` ช่วยให้ dimensional consistency
- **Semi-Implicit Balance:** ผสมผสาน implicit/explicit treatment

**รายละเอียดการนำไปใช้ (Implementation Details)**

1. **เทอมแนวทแยง (`fvm::Sp`)**: ฟังก์ชัน `fvm::Sp` จะเพิ่มค่าสัมประสิทธิ์ virtual mass เข้าไปที่แนวทแยงของเมทริกซ์โมเมนตัม:
   $$\mathbf{A}_{ii} \leftarrow \mathbf{A}_{ii} + \frac{C_{VM} \rho_1 \alpha_1 \alpha_2}{\Delta t}$$

2. **เทอมแหล่งกำเนิด (Source Term)**: ส่วน Explicit แสดงถึงส่วนประกอบจากอัตราเร่งของเฟสอื่น ซึ่งประเมินโดยใช้ค่าที่ทราบจากระดับเวลาก่อนหน้า

3. **การปรับสเกลขั้นเวลา (Time Step Scaling)**: การหารด้วย `dt` ช่วยให้มั่นใจได้ถึงความสอดคล้องของมิติ (dimensional consistency) และความแม่นยำของการอินทิเกรตเวลา

4. **การจัดการแบบสมมาตร (Symmetric Treatment)**: ทั้งสองเฟสได้รับการจัดการแบบสมมาตรในสมการโมเมนตัมที่เกี่ยวข้อง เพื่อให้มั่นใจในการอนุรักษ์โมเมนตัม (conservation of momentum)

---

## 8. การตั้งค่าใน `phaseProperties`

ตัวอย่างการตั้งค่าโมเดลสัมประสิทธิ์คงที่:

```openfoam
virtualMass
(
    (air in water)
    {
        type            constantCoefficient;
        Cvm             0.5;
    }
);
```

### 8.1 การกำหนดค่า Dictionary

Virtual Mass Models มักจะถูกระบุใน dictionary `phaseProperties`:

```foam
phaseProperties
{
    phase1
    {
        type            gas;
    }

    phase2
    {
        type            liquid;
    }

    // Virtual mass model configuration
    virtualMassModel
    {
        type            constant;
        Cvm             0.5;
    }
}
```

สำหรับรุ่นที่ขึ้นกับรูปร่าง:

```foam
virtualMassModel
{
    type            shape;
    shapeType       ellipsoid;
    aspectRatio
    {
        type            uniform;
        value           2.0;  // aspect ratio
    }
}
```

### 8.2 แนวทางการเลือกรุ่น

| รุ่น | เหมาะสำหรับ | ค่า $C_{vm}$ ทั่วไป | ภาระการคำนวณ |
|------|---------------|-------------------|----------------|
| **Constant** | ฟองอากาศ, อนุภาคทรงกลม | 0.5 (ทรงกลม), 0.3-0.7 (อื่นๆ) | ต่ำสุด |
| **Shape-Dependent** | อนุภาคทรงรี, จาน, แท่ง | คำนวณตามรูปร่าง | สูง |

**แนวทางการเลือกรุ่น:**

- **รุ่น Constant:**
  - เหมาะสำหรับฟองอากาศหรืออนุภาคทรงกลม
  - ตัวเลือกเริ่มต้นเมื่อไม่ทราบการกระจายตัวของรูปร่างอนุภาค

- **รุ่น Shape-Dependent:**
  - จำเป็นสำหรับอนุภาคที่ไม่ใช่ทรงกลม (ทรงรี, จาน, แท่ง)
  - สำคัญในการไหลแบบฟองอากาศที่มีฟองอากาศที่เสียรูป
  - จำเป็นสำหรับการไหลแบบกระจายตัวที่มีการเปลี่ยนแปลงอัตราส่วนภาพอย่างมีนัยสำคัญ

---

## 9. ข้อควรพิจารณาด้านประสิทธิภาพ

### 9.1 ประสิทธิภาพการคำนวณ

#### รุ่น Constant
- **การจัดสรรสนามเดียวสำหรับสัมประสิทธิ์**
- **การดำเนินการทางคณิตศาสตร์โดยตรงสำหรับการคำนวณแรง**
- **การนำไปใช้ที่มีประสิทธิภาพด้วยการดำเนินการสนามของ OpenFOAM**

#### รุ่น Shape-Dependent
- **การคำนวณแบบสนามสำหรับอัตราส่วนภาพที่แปรผันตามตำแหน่ง**
- **การคำนวณสัมประสิทธิ์แบบเซลล์ต่อเซลล์แบบวนซ้ำ**
- **ความต้องการหน่วยความจำที่เพิ่มขึ้นสำหรับสนามอัตราส่วนภาพ**

### 9.2 ความเสถียรเชิงตัวเลข

ผลกระทบของ Virtual Mass สามารถปรับปรุงความเสถียรเชิงตัวเลขได้โดย:
- **การเพิ่มการเชื่อมโยงระหว่างเฟส**
- **การลดความเร่งสัมพัทธ์ระหว่างเฟส**
- **การหน่วงการสั่นความถี่สูงในความเร็วเฟส**

อย่างไรก็ตาม สัมประสิทธิ์ Virtual Mass ที่สูงเกินไปอาจนำไปสู่:
- **สมการโมเมนตัมที่แข็ง (stiff)** ซึ่งต้องการขั้นเวลาที่เล็กกว่า
- **การเชื่อมโยงที่มากเกินไป** ซึ่งอาจยับยั้งการลื่นไถลของเฟสทางกายภาพ
- **การแพร่กระจายเชิงตัวเลข** ของพลวัตของอินเทอร์เฟซ

---

## 10. การตรวจสอบและการประยุกต์ใช้

### 10.1 กรณีตรวจสอบ (Validation Cases)

| กรณี | วัตถุประสงค์ | การตรวจสอบ |
|-------|---------------|-------------|
| **ทรงกลมที่กำลังเร่งในของเหลวที่อยู่นิ่ง** | ทดสอบพื้นฐาน | เปรียบเทียบกับผลเฉลยเชิงวิเคราะห์ |
| **พลวัตของคอลัมน์ฟองอากาศ** | การใช้งานจริง | ตรวจสอบกับความเร็วการลอยขึ้นของฟองอากาศจากการทดลอง |
| **การไหลที่มีอนุภาค** | ความเสถียร | ตรวจสอบผลกระทบของการเชื่อมโยงโมเมนตัม |

### 10.2 การประยุกต์ใช้ในอุตสาหกรรม

#### **เครื่องปฏิกรณ์แบบคอลัมน์ฟองอากาศ**
- การทำนายการเร่งความเร็วและการลอยขึ้นของฟองอากาศได้อย่างแม่นยำ
- สำคัญสำหรับการออกแบบเครื่องปฏิกรณ์ที่มีประสิทธิภาพสูง

#### **เตียงฟลูอิไดซ์ (Fluidized beds)**
- การแสดงผลกระทบการเร่งความเร็วของอนุภาคในสารแขวนลอยหนาแน่น
- ช่วยให้การพยากรณ์พฤติกรรมของเตียงฟลูอิไดซ์มีความแม่นยำมากขึ้น

#### **การประยุกต์ใช้ในอวกาศ**
- การสร้างแบบจำลองการเร่งความเร็วของหยดเชื้อเพลิงเหลวในกระแสแก๊ส
- สำคัญสำหรับการออกแบบระบบขับเคลื่อนจรวด

#### **การแปรรูปทางเคมี**
- การทำนายพลวัตของเฟสที่กระจายตัวในภาชนะผสม
- ปรับปรุงประสิทธิภาพของกระบวนการผสม

---

> [!TIP] การจัดการแรงมวลเสมือนอย่างถูกต้องเป็นกุญแจสำคัญสู่ความเสถียรเชิงตัวเลขในการจำลองระบบ Gas-Liquid ที่มีความเร่งสูง

> [!INFO] **Virtual Mass Models ใน OpenFOAM** นำเสนอโครงสร้างที่ครอบคลุมสำหรับการพิจารณาผลกระทบของมวลที่เพิ่มขึ้นในการไหลแบบหลายเฟส ทำให้สามารถจำลองระบบที่การเร่งความเร็วของเฟสและการเคลื่อนที่สัมพัทธ์มีความสำคัญได้อย่างแม่นยำ