# การนำไปใช้ใน OpenFOAM (OpenFOAM Implementation)

## ภาพรวม (Overview)

OpenFOAM มีกรอบการทำงานที่ครอบคลุมสำหรับการจำลองแรงยกในการไหลแบบหลายเฟส โดยใช้สถาปัตยกรรมเชิงวัตถุ (object-oriented architecture) ที่รองรับการเลือกโมเดลขณะรันโปรแกรม (runtime selection)

---

## สถาปัตยกรรมคลาส (Class Architecture)

### คลาสพื้นฐานของโมเดลแรงยก (Lift Model Base Class)

```cpp
// Base lift model class
class liftModel
{
public:
    // Calculate lift force
    virtual tmp<volVectorField> Fi() const = 0;

    // Calculate lift coefficient
    virtual tmp<volScalarField> Cl() const = 0;

    // Virtual destructor
    virtual ~liftModel() {}
};
```

📂 **Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystem.C`

### คำอธิบาย (Explanation)

คลาสพื้นฐานของโมเดลแรงยก (lift model base class) กำหนดอินเทอร์เฟซสำหรับการคำนวณแรงยก (lift forces) ในการจำลองการไหลแบบหลายเฟส (multiphase flow simulations)

### แนวคิดสำคัญ (Key Concepts)

- เป็น **abstract base class** ที่บังคับโครงสร้างทั่วไปสำหรับทุกการนำโมเดลแรงยกไปใช้
- ใช้ฟังก์ชัน **pure virtual** `Fi()` และ `Cl()`
- แรงยก $\mathbf{F}_L$ จะกระทำตั้งฉากกับทิศทางความเร็วสัมพัทธ์ระหว่างเฟส
- มีความสำคัญอย่างยิ่งต่อการทำนายพฤติกรรมของเฟสที่กระจายตัวในการไหลแบบเฉือน

---

## ลำดับชั้นของคลาส (Lift Model Hierarchy)

```
liftModel (Abstract Interface)
├── dispersedLiftModel (สำหรับอนุภาคในเฟสกระจายตัว)
├── TomiyamaLift
├── SaffmanMeiLift
├── constantLiftCoefficient
├── noLift
└── wallDampedLift
```

### คุณสมบัติหลัก (Key Features)

| คุณสมบัติ | คำอธิบาย |
|-----------|----------|
| **การเลือกขณะทำงาน (Runtime Selection)** | แบบจำลองสามารถเลือกได้ผ่านการป้อนข้อมูลใน dictionary |
| **การรองรับการผสม (Blending Support)** | การผสมแบบอัตโนมัติระหว่างเฟสในระบบหลายเฟส |
| **แรงที่หน้าตัดและปริมาตร (Face and Volume Forces)** | รองรับทั้งรูปแบบแรงต่อปริมาตรและแรงต่อพื้นผิว |
| **การจัดการเงื่อนไขขอบเขต (Boundary Condition Handling)** | การจัดการที่เหมาะสมสำหรับขอบเขตฟลักซ์คงที่ (fixed flux boundaries) |

---

## การนำ Saffman-Mei ไปใช้ (Saffman-Mei Implementation)

### สมการแรงยกและตัวแปร

$$\mathbf{F}_L = \rho_c \alpha_d C_L \mathbf{U}_r \times \boldsymbol{\omega}$$

**ตัวแปร:**
- $\mathbf{F}_L$ = แรงยก (Lift force)
- $\rho_c$ = ความหนาแน่นของเฟสต่อเนื่อง (Continuous phase density)
- $\alpha_d$ = ส่วนประกอบปริมาตรของเฟสกระจายตัว (Dispersed phase volume fraction)
- $C_L$ = สัมประสิทธิ์แรงยก (Lift coefficient)
- $\mathbf{U}_r$ = ความเร็วสัมพัทธ์ (Relative velocity)
- $\boldsymbol{\omega}$ = ความปั่นป่วนของเฟสต่อเนื่อง (Vorticity of continuous phase)

### OpenFOAM Code Implementation

```cpp
class SaffmanMeiLift
:
    public liftModel
{
    // Calculate lift coefficient
    virtual tmp<volScalarField> Cl() const
    {
        // Get Reynolds number and Saffman parameter from the pair
        const volScalarField& Re = pair_.Re();
        const volScalarField& Sr = pair_.Sr(); // Saffman parameter

        // Create temporary scalar field for lift coefficient
        tmp<volScalarField> tCl
        (
            new volScalarField
            (
                IOobject
                (
                    "Cl",
                    pair_.mesh().time().timeName(),
                    pair_.mesh()
                ),
                pair_.mesh(),
                dimensionedScalar("Cl", dimless, 0)
            )
        );

        volScalarField& Cl = tCl.ref();

        // Calculate lift coefficient for each cell based on Reynolds number
        forAll(Cl, celli)
        {
            if (Re[celli] < 40)
            {
                // Low Reynolds number regime
                Cl[celli] = 2.255/sqrt(Re[celli]*Sr[celli])*
                           (1.0 - 0.15*pow(Re[celli], 0.687));
            }
            else if (Re[celli] <= 1000)
            {
                // Intermediate Reynolds number regime
                Cl[celli] = (0.5 + 0.2*Re[celli])/sqrt(Re[celli]*Sr[celli]);
            }
            else
            {
                // High Reynolds number regime - negligible lift
                Cl[celli] = 0;
            }
        }

        return tCl;
    }

    // Calculate lift force
    virtual tmp<volVectorField> Fi() const
    {
        // Access dispersed and continuous phase properties
        const phaseModel& dispersed = pair_.dispersed();
        const phaseModel& continuous = pair_.continuous();

        const volScalarField& alpha = dispersed.alpha();
        const volScalarField& rho = continuous.rho();
        const volVectorField& Uc = continuous.U();
        const volVectorField& Ud = dispersed.U();
        const volScalarField& Cl = this->Cl();

        // Relative velocity
        volVectorField Ur = Ud - Uc;

        // Vorticity of continuous phase
        volVectorField omega = fvc::curl(Uc);

        // Lift force calculation
        return rho*alpha*Cl*Ur*omega;
    }
};
```

📂 **Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/ThermalPhaseChangePhaseSystem/ThermalPhaseChangePhaseSystem.C`

### คำอธิบาย (Explanation)

การนำ Saffman-Mei lift model ไปใช้ใน OpenFOAM แบ่งเป็นสองส่วนหลัก: การคำนวณสัมประสิทธิ์แรงยก $C_L$ และการคำนวณเวกเตอร์แรงยก $\mathbf{F}_L$ โค้ดนี้แสดงการใช้งานจริงใน OpenFOAM โดยใช้ volScalarField และ volVectorField สำหรับการคำนวณบน mesh

### แนวคิดสำคัญ (Key Concepts)

- ใช้ **Reynolds number (Re)** และ **Saffman parameter (Sr)** ในการกำหนดช่วงของสมการ
- แรงยกคำนวณจาก **ผลคูณไขว้** ระหว่างความเร็วสัมพัทธ์และความหมุนวน
- การคำนวณทำ **cell-by-cell** เพื่อรองรับความแปรผันของสมบัติการไหลบน mesh

### สัมประสิทธิ์แรงยกตามช่วงเรย์โนลด์ส

โมเดลนี้ใช้ **Saffman parameter** $Sr = \frac{Re_s^2}{Re}$ โดยที่ $Re_s$ คือ shear Reynolds number

| ช่วงเรย์โนลด์ส | สมการสัมประสิทธิ์แรงยก $C_L$ | คำอธิบาย |
|---|---|---|
| $Re < 40$ | $C_L = \frac{2.255}{\sqrt{Re \cdot Sr}}(1 - 0.15 Re^{0.687})$ | แรงยกสูงสำหรับอนุภาคเล็ก |
| $40 \leq Re \leq 1000$ | $C_L = \frac{0.5 + 0.2Re}{\sqrt{Re \cdot Sr}}$ | ช่วงเรย์โนลด์สกลาง |
| $Re > 1000$ | $C_L = 0$ | แรงยกน้อยมาก |

---

## การนำ Tomiyama Lift Model ไปใช้

### สมการและตัวแปรหลัก

Tomiyama lift model ถูกออกแบบมาโดยเฉพาะสำหรับ **ฟองแก๊สในของเหลว** และคำนึงถึงการเปลี่ยนแปลงจากแรงยกที่เป็นบวกไปเป็นแรงยกที่เป็นลบ

**Eötvös Number:**
$$Eo = \frac{\Delta \rho g d^2}{\sigma}$$

**ตัวแปร:**
- $Eo$ = Eötvös number (อัตราส่วนแรงลอยตัวต่อแรงตึงผิว)
- $\Delta \rho$ = ความแตกต่างความหนาแน่นระหว่างเฟส
- $g$ = ความเร่งเนื่องจากแรงโน้มถ่วง
- $d$ = เส้นผ่านศูนย์กลางของฟอง
- $\sigma$ = ความตึงผิว

### องค์ประกอบของสัมประสิทธิ์แรงยก

**ส่วนประกอบจากความหนืด (Viscous contribution):**
$$C_L^{viscous} = 0.288 \tanh(0.121 Re)$$

**ส่วนประกอบจาก Eötvös (Eötvös contribution):**
$$C_L^{Eo} = 0.00105Eo^3 - 0.1159Eo^2 + 0.426Eo - 0.2303$$

### OpenFOAM Implementation

```cpp
class TomiyamaLift
:
    public liftModel
{
    // Calculate lift coefficient for Tomiyama model
    virtual tmp<volScalarField> Cl() const
    {
        // Get Reynolds number and Eötvös number from the pair
        const volScalarField& Re = pair_.Re();
        const volScalarField& Eo = pair_.Eo();

        // Create temporary scalar field for lift coefficient
        tmp<volScalarField> tCl = volScalarField::New("Cl", pair_.mesh(), 0.0);
        volScalarField& Cl = tCl.ref();

        // Calculate lift coefficient for each cell based on Eötvös number
        forAll(Cl, celli)
        {
            scalar Re_local = Re[celli];
            scalar Eo_local = Eo[celli];

            // Viscous contribution using hyperbolic tangent
            scalar Cl_tanh = 0.288*tanh(0.121*Re_local);

            // Eötvös contribution - cubic polynomial
            scalar f_Eo = 0.00105*pow(Eo_local, 3)
                        - 0.1159*pow(Eo_local, 2)
                        + 0.426*Eo_local
                        - 0.2303;

            if (Eo_local <= 4)
            {
                // Small bubbles - positive lift (wall-attracting)
                Cl[celli] = min(Cl_tanh, f_Eo);
            }
            else if (Eo_local <= 10)
            {
                // Medium bubbles - transition regime
                Cl[celli] = f_Eo;
            }
            else
            {
                // Large bubbles - negative lift (wall-repelling)
                Cl[celli] = -0.27;
            }
        }

        return tCl;
    }
};
```

📂 **Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystem.C`

### คำอธิบาย (Explanation)

Tomiyama model ถูกออกแบบมาเพื่อจำลองพฤติกรรมของฟองแก๊สในของเหลว โดยคำนึงถึงการเปลี่ยนแปลงจากแรงยกเชิงบวก (ดึงดูดผนัง) ไปเป็นแรงยกเชิงลบ (ผลักผนัง) เมื่อขนาดฟองเพิ่มขึ้น ซึ่งสำคัญมากในการทำนายการกระจายตัวของฟองในช่องทาง

### แนวคิดสำคัญ (Key Concepts)

- ใช้ **Eötvös number (Eo)** เป็นตัวกำหนดขนาดฟองและพฤติกรรมแรงยก
- แรงยก **เปลี่ยนเครื่องหมาย** จากบวกเป็นลบเมื่อ $Eo > 10$
- ใช้ **ฟังก์ชัน tanh** สำหรับส่วนประกอบจากความหนืด
- สำคัญมากสำหรับการทำนาย **wall peeling** ของฟองขนาดใหญ่

### สัมประสิทธิ์แรงยกตามขนาดฟอง

| ขนาดฟอง (Eötvös number) | สมการสัมประสิทธิ์แรงยก $C_L$ | พฤติกรรม | คำอธิบาย |
|---|---|---|---|
| **ฟองขนาดเล็ก** ($Eo \leq 4$) | $C_L = \min(C_L^{viscous}, C_L^{Eo})$ | แรงยกบวก | ดึงดูดผนัง |
| **ฟองขนาดกลาง** ($4 < Eo \leq 10$) | $C_L = C_L^{Eo}$ | แรงยกผันแปร | ช่วงเปลี่ยนผ่าน |
| **ฟองขนาดใหญ่** ($Eo > 10$) | $C_L = -0.27$ | แรงยกติดลบ | ผลักผนัง (wall peeling) |

### ความสำคัญในการจำลองการไหล

**จุดสำคัญ:**
- การเปลี่ยนแปลงจากพฤติกรรม **wall-attracting** ไปเป็น **wall-repelling** ส่งผลอย่างมากต่อ:
  - การกระจายตัวของฟองในโดเมน
  - ปริมาตรความเข้มข้นของพื้นที่ผิว (interfacial area concentration)
  - การถ่ายเทมวลและมวลระหว่างเฟส

---

## การคำนวณใน Solver (Numerical Workflow)

ใน Solver อย่าง `multiphaseEulerFoam`, ขั้นตอนการคำนวณแรงยกมีดังนี้:

### การคำนวณความหมุนวน (Vorticity)

แรงยกอ้างอิงจากความไม่สมมาตรของสนามการไหล ซึ่งแทนด้วย Vorticity ($\boldsymbol{\omega}$):

```cpp
// Calculate vorticity field from velocity field
// Vorticity is the curl of velocity: ω = ∇ × u
volVectorField omega = fvc::curl(Uc);
```

📂 **Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystem.C`

### คำอธิบาย (Explanation)

การคำนวณความหมุนวน (vorticity) เป็นขั้นตอนสำคัญในการคำนวณแรงยก เนื่องจากแรงยกเกิดจากความไม่สมมาตรของสนามการไหล ซึ่งวัดด้วย curl ของสนามความเร็ว

### แนวคิดสำคัญ (Key Concepts)

- **Vorticity** ($\boldsymbol{\omega} = \nabla \times \mathbf{u}$) วัดการหมุนของฟลูอิด
- การคำนวณใช้ **finite volume calculus** (fvc::curl)
- เป็น **อนุพันธ์อันดับหนึ่ง** ของสนามความเร็ว แต่เนื่องจากเป็น curl จึงต้องการ **อนุพันธ์อันดับสอง** โดยนัย

### การรวมแรงเข้ากับสมการโมเมนตัม

แรงยกต่อหน่วยปริมาตรคำนวณจากสัมประสิทธิ์ $C_L$:

$$\mathbf{F}_L = C_L \rho_c \alpha_d (\mathbf{u}_c - \mathbf{u}_d) \times \boldsymbol{\omega}$$

---

## ข้อควรพิจารณาด้านเสถียรภาพ (Stability Considerations)

แรงยกอาจทำให้การคำนวณไม่เสถียรเนื่องจากใช้การคำนวณอนุพันธ์อันดับสอง (ผ่าน curl) OpenFOAM จึงมีเทคนิคควบคุมดังนี้:

### แหล่งที่มาหลักของความไม่เสถียรเชิงตัวเลข

แรงยกสามารถก่อให้เกิดความไม่เสถียรเชิงตัวเลขได้ผ่านกลไกพื้นฐานสามประการ:

#### 1. ความไวต่อการคำนวณความหมุนวน (Vorticity Calculation Sensitivity)
- การคำนวณความหมุนวน $\boldsymbol{\omega} = \nabla \times \mathbf{u}$ จำเป็นต้องใช้ค่าอนุพันธ์อันดับสองของสนามความเร็ว
- อนุพันธ์เชิงพื้นที่เหล่านี้มีความไวต่อคุณภาพของ Mesh และข้อผิดพลาดจากการประมาณค่าเชิงตัวเลข
- บน Mesh ที่หยาบ สนามความหมุนวนอาจแสดงสัญญาณรบกวนเชิงตัวเลขที่มีนัยสำคัญ

#### 2. การขยายสัญญาณของผลคูณไขว้ (Cross-Product Amplification)
- สูตรทางคณิตศาสตร์ของแรงยกเกี่ยวข้องกับผลคูณไขว้ $\mathbf{F}_L \propto \mathbf{u}_d \times \boldsymbol{\omega}$
- การดำเนินการแบบเวกเตอร์นี้สามารถขยายข้อผิดพลาดเชิงตัวเลขขนาดเล็กได้อย่างทวีคูณ

#### 3. การกระจายแรงแบบไม่สมมาตร (Anisotropic Force Distribution)
- แรงยกจะกระทำในทิศทางตั้งฉากกับทิศทางของความเร็วสัมพัทธ์เป็นหลัก
- ทำให้เกิดสนามแรงที่ไม่สมมาตรซึ่งอาจก่อให้เกิดการเคลื่อนที่ในแนวข้างที่ผิดปกติ

---

## เทคนิคการทำให้เรียบ (Regularization Techniques)

เพื่อบรรเทาความท้าทายด้านความเสถียรเหล่านี้ เทคนิคการทำให้เรียบหลายอย่างถูกนำมาใช้กันทั่วไปในการใช้งาน OpenFOAM

### Vorticity Field Smoothing

สนามความหมุนวนสามารถทำให้เรียบได้ผ่านการแพร่กระจายอย่างชัดเจน (explicit diffusion) เพื่อลดสัญญาณรบกวนความถี่สูง:

$$\boldsymbol{\omega}_{smoothed} = \boldsymbol{\omega} + \nu_{smooth} \nabla^2 \boldsymbol{\omega}$$

โดยที่:
- $\boldsymbol{\omega}_{smoothed}$ คือสนามความหมุนวนที่ทำให้เรียบแล้ว
- $\nu_{smooth}$ คือสัมประสิทธิ์การแพร่กระจายเทียม (artificial diffusion coefficient)

#### OpenFOAM Code Implementation

```cpp
// Vorticity smoothing implementation
// Add artificial diffusion to smooth high-frequency noise
volVectorField omegaSmoothed = omega + nuSmooth * fvc::laplacian(omega);
```

📂 **Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystem.C`

### คำอธิบาย (Explanation)

การทำให้เรียบสนามความหมุนวนช่วยลดสัญญาณรบกวนเชิงตัวเลขที่เกิดจากการประมาณค่าอนุพันธ์บน mesh ที่หยาบ โดยการเพิ่มการแพร่กระจายเทียมเข้าไปในสนาม

### แนวคิดสำคัญ (Key Concepts)

- ใช้ **Laplacian operator** ($\nabla^2$) สำหรับการทำให้เรียบ
- สัมประสิทธิ์ $\nu_{smooth}$ ต้องถูกเลือกอย่างระมัดระวังเพื่อสมดุลระหว่างความเสถียรและความแม่นยำ
- ค่าทั่วไปอยู่ในช่วง $10^{-6}$ ถึง $10^{-4}$

สัมประสิทธิ์การทำให้เรียบควรได้รับการเลือกอย่างระมัดระวัง:
- ค่าทั่วไปอยู่ในช่วง $10^{-6}$ ถึง $10^{-4}$ ขึ้นอยู่กับความละเอียดของ Mesh และสภาวะการไหล
- ต้องมีค่ามากพอที่จะลดทอนสัญญาณรบกวนเชิงตัวเลข
- แต่ก็ต้องมีค่าน้อยพอที่จะรักษาโครงสร้างความหมุนวนที่มีความหมายทางกายภาพไว้ได้

### Lift Coefficient Limiting

เพื่อป้องกันขนาดแรงที่ผิดจริงซึ่งอาจทำให้การจำลองไม่เสถียร ค่าสัมประสิทธิ์แรงยกจะถูกจำกัดขอบเขตโดยใช้ฟังก์ชันการอิ่มตัว (saturation functions):

$$C_L^{limited} = \text{sign}(C_L) \min(|C_L|, C_L^{max})$$

ค่าสูงสุดทั่วไปสำหรับสัมประสิทธิ์แรงยกคือประมาณ:
$$|C_L|^{max} \approx 1.0$$

ค่านี้นับเป็นค่าสัมประสิทธิ์แรงยกสูงสุดตามทฤษฎีสำหรับอนุภาคทรงกลมในการไหลแบบไม่หนืด

#### OpenFOAM Code Implementation

```cpp
// Lift coefficient limiting
// Limit the magnitude of lift coefficient to prevent instability
scalar CLimited = sign(CL) * min(mag(CL), CLmax);
```

📂 **Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystem.C`

### คำอธิบาย (Explanation)

การจำกัดค่าสัมประสิทธิ์แรงยกช่วยป้องกันค่าที่ผิดปกติซึ่งอาจเกิดจากข้อผิดพลาดเชิงตัวเลข โดยการจำกัดค่าสัมบูรณ์ให้อยู่ในช่วงที่กายภาพสมเหตุสมผล

### แนวคิดสำคัญ (Key Concepts)

- ใช้ **saturation function** เพื่อจำกัดค่าสูงสุด
- ค่า $C_L^{max} \approx 1.0$ พิจารณาจากค่าทางทฤษฎี
- รักษา **เครื่องหมาย** ของสัมประสิทธิ์แรงยกเดิม

---

## การนำ Under-Relaxation มาใช้

Under-relaxation เป็นอีกชั้นหนึ่งของความเสถียรเชิงตัวเลข โดยการควบคุมอัตราที่แรงยกถูกนำเข้าสู่สมการโมเมนตัม

### สูตรการปรับค่าแรงยก

แรงยกที่ปรับค่าแล้วจะถูกคำนวณเป็นการรวมกันแบบถ่วงน้ำหนักของค่าก่อนหน้าและค่าปัจจุบัน:

$$\mathbf{F}_L^{new} = (1-\lambda_L)\mathbf{F}_L^{old} + \lambda_L \mathbf{F}_L^{calculated}$$

โดยที่:
- $\mathbf{F}_L^{new}$ คือแรงยกที่ปรับค่าแล้วสำหรับรอบปัจจุบัน
- $\mathbf{F}_L^{old}$ คือแรงยกจากรอบการวนซ้ำก่อนหน้า
- $\mathbf{F}_L^{calculated}$ คือแรงที่คำนวณใหม่ตามสภาวะการไหลปัจจุบัน
- $\lambda_L$ คือตัวประกอบการปรับค่าแรงยก (lift force relaxation factor)

### พารามิเตอร์การปรับค่าทั่วไป

ตัวประกอบการปรับค่า $\lambda_L$ โดยทั่วไปจะอยู่ในช่วง 0.3 ถึง 0.5 ขึ้นอยู่กับ:

| ปัจจัย | ค่า $\lambda_L$ ที่แนะนำ | คำอธิบาย |
|--------|---------------------|-----------|
| **คุณภาพของ Mesh** | 0.3 - 0.4 | Mesh ที่หยาบกว่าต้องการการปรับค่าที่เข้มข้นกว่า |
| **ระบอบการไหล** | 0.4 - 0.5 | การไหลที่มีความปั่นป่วนสูงอาจต้องการการปรับค่าที่รอบคอบกว่า |
| **ขนาด Time Step** | 0.2 - 0.4 | Time step ที่ใหญ่ขึ้นจำเป็นต้องใช้ตัวประกอบการปรับค่าที่เล็กลง |
| **ปริมาณเฟสที่กระจายตัว** | 0.3 - 0.5 | ปริมาตรเศษส่วนที่สูงขึ้นอาจต้องการ $\lambda_L$ ที่ลดลง |

#### OpenFOAM Code Implementation

```cpp
// Lift force under-relaxation
// Apply under-relaxation to improve numerical stability
scalar lambdaL = 0.4; // Typical relaxation factor
liftForce = (1.0 - lambdaL) * liftForce.oldTime() + lambdaL * liftForceCalculated;
```

📂 **Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystem.C`

### คำอธิบาย (Explanation)

Under-relaxation เป็นเทคนิคที่ใช้กันอย่างแพร่หลายใน CFD เพื่อปรับปรุงความเสถียรของการแก้สมการ โดยการผสมค่าจากรอบก่อนหน้าเข้ากับค่าใหม่ ช่วยลดการสั่นของคำตอบ

### แนวคิดสำคัญ (Key Concepts)

- ใช้ **weighted average** ระหว่างค่าเก่าและค่าใหม่
- ตัวประกอบ $\lambda_L$ ควบคุม **อัตราการอัปเดต**
- ค่า $\lambda_L$ ที่ต่ำกว่า = การบรรเทาที่แข็งแกร่งกว่า แต่การลู่เข้าช้ากว่า
- ต้องสมดุลระหว่าง **ความเสถียร** และ **อัตราการลู่เข้า**

---

## การตั้งค่าใน `phaseProperties`

### ตัวอย่างการตั้งค่าโมเดล Tomiyama

ตัวอย่างการตั้งค่าโมเดล Tomiyama พร้อมระบบหน่วงผนัง (Wall damping):

```openfoam
lift
(
    (air in water)
    {
        type            Tomiyama;
        aspectRatio     constant;
        E0              0.07;
    }
);
```

### ตัวอย่างการตั้งค่าโมเดล Saffman-Mei

```openfoam
lift
(
    (particles in water)
    {
        type            SaffmanMei;
        Cl              constant 0.5;
    }
);
```

### ตัวอย่างการตั้งค่าโมเดลสัมประสิทธิ์คงที่

```openfoam
lift
(
    (bubbles in liquid)
    {
        type            constantLiftCoefficient;
        Cl              0.5;
    }
);
```

---

## การประยุกต์ใช้งานใน Solver

### การใช้งานใน multiphaseEulerFoam

ใน `multiphaseEulerFoam` แรงยกจะถูกคำนวณและเพิ่มเข้าสมการโมเมนตัม:

```cpp
// Example usage in multiphaseEulerFoam
// Create dispersed lift model with runtime selection
liftModels::dispersedLiftModel dispersedLift(
    phasePairs,
    turbulence,
    mesh,
    dict.subDict("liftModels")
);

// Calculate lift force field
tmp<volVectorField> liftForce = dispersedLift.Flift();

// Add lift force contribution to momentum equation
momentumEqn += liftForce;
```

📂 **Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystem.C`

### คำอธิบาย (Explanation)

การนำแรงยกไปใช้ใน multiphaseEulerFoam solver เกี่ยวข้องกับการสร้าง dispersedLiftModel object ซึ่งรองรับการเลือกโมเดลขณะรัน และเพิ่มแรงที่คำนวณได้เข้าสมการโมเมนตัม

### แนวคิดสำคัญ (Key Concepts)

- ใช้ **Runtime selection** ผ่าน dictionary
- แรงยกเพิ่มเป็น **source term** ในสมการโมเมนตัม
- รองรับ **multiple phase pairs** ในระบบหลายเฟส

### การใช้งานใน DPMFoam

สำหรับ Lagrangian particle tracking:

```cpp
// Enhanced particle force model including lift
// Calculate lift force on individual particles
vectorField F_lift = this->lift().particleLiftForce(
    particles,    // Particle properties
    Uc_,          // Continuous phase velocity
    rhoc_,        // Continuous phase density
    d_,           // Particle diameter
    nuc_          // Continuous phase viscosity
);
```

📂 **Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/populationBalanceModel/populationBalanceModel/populationBalanceModel.C`

### คำอธิบาย (Explanation)

ในแนวทาง Lagrangian แรงยกคำนวณสำหรับแต่ละอนุภาคโดยอิสระ โดยพิจารณาคุณสมบัติของอนุภาคและสภาพแวดล้อมโดยรอบ

### แนวคิดสำคัญ (Key Concepts)

- คำนวณแรง **particle-by-particle**
- พิจารณา **local flow conditions** รอบๆ อนุภาค
- เหมาะสำหรับ **dilute flows** ที่การโต้ตอบระหว่างอนุภาคน้อย

---

## การตรวจสอบความถูกต้อง (Validation)

การนำข้อความพิจารณาเชิงตัวเลขเหล่านี้มาใช้จำเป็นต้องมีการตรวจสอบความถูกต้องอย่างรอบคอบ:

### 1. การศึกษาความเป็นอิสระของกริด (Grid Independence Studies)
- ตรวจสอบว่าการทำให้เรียบไม่ส่งผลเสียต่อการลู่เข้าของผลเฉลยเมื่อ Mesh ละเอียดขึ้น
- เปรียบเทียบผลลัพธ์บน Mesh ที่มีความละเอียดแตกต่างกัน

### 2. การเปรียบเทียบกับ Benchmark (Benchmark Comparisons)
- ตรวจสอบความถูกต้องกับผลเฉลยเชิงวิเคราะห์
- เปรียบเทียบกับข้อมูลการทดลองสำหรับปัญหามาตรฐาน

### 3. การทดสอบความเสถียร (Stability Testing)
- ทดสอบพารามิเตอร์การปรับค่าและค่าจำกัดขอบเขตอย่างเป็นระบบในระบอบการไหลที่แตกต่างกัน
- ประเมินขีดจำกัดของความเสถียรสำหรับแต่ละวิธีการทำให้เรียบ

---

## สรุป

การนำแรงยกมาใช้ใน OpenFOAM ต้องการความเข้าใจทั้ง:

1. **สถาปัตยกรรมคลาส** - โครงสร้าง OOP ที่รองรับการเลือกโมเดลขณะรัน
2. **โมเดลทางฟิสิกส์** - Saffman-Mei, Tomiyama และโมเดลอื่นๆ
3. **ข้อควรพิจารณาเชิงตัวเลข** - Vorticity smoothing, coefficient limiting, under-relaxation
4. **การตั้งค่า** การใช้งาน - phaseProperties dictionary และ solver integration

การสร้างสมดุลที่เหมาะสมระหว่างความเสถียรเชิงตัวเลขและความแม่นยำทางกายภาพเป็นสิ่งจำเป็นสำหรับการจำลอง CFD ที่เชื่อถือได้ซึ่งรวมถึงแรงยก โดยเฉพาะอย่างยิ่งในการใช้งานของไหลหลายเฟสที่ปรากฏการณ์ระหว่างพื้นผิวมีบทบาทสำคัญในพลวัตโดยรวม