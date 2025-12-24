# ภาพรวมแรงยกในการไหลแบบหลายเฟส (Lift Forces in Multiphase Flow Overview)

## บทนำ (Introduction)

**แรงยก (Lift Forces)** เป็นกลไกพื้นฐานของการถ่ายโอนโมเมนตัมระหว่างเฟส (interfacial momentum transfer mechanisms) ในการไหลแบบหลายเฟส (multiphase flows) ซึ่งมีความสำคัญอย่างยิ่งต่อการทำนายการกระจายตัวของเฟสและพฤติกรรมการไหลในระบบทางวิศวกรรม

### คุณสมบัติหลักของแรงยก

แรงยกในการไหลแบบหลายเฟสมีลักษณะเฉพาะดังนี้:

- มี==ทิศทางตั้งฉาก==กับความเร็วสัมพัทธ์ระหว่างเฟส
- เกิดจากปรากฏการณ์ทางกายภาพที่หลากหลาย:
  - แรงเฉือน (shear) ในเฟสต่อเนื่อง
  - ความแตกต่างของความดัน (pressure gradients)
  - การหมุนของอนุภาค (particle rotation)
  - การมีอยู่ของผนังที่อยู่ใกล้เคียง
- มีความสำคัญอย่างยิ่งในการไหลแบบเฉือน (shear flows) และการไหลที่มีความหมุนวน (vorticity)

> [!INFO] ความสำคัญของแรงยก
> แรงยกเป็นปัจจัยสำคัญที่กำหนดการกระจายตัวของฟองอากาศในท่อ การเคลื่อนที่ของอนุภาคในเครื่องแยก และประสิทธิภาพการผสมในเครื่องปฏิกรณ์

---

## กลไกทางกายภาพ (Physical Mechanisms)

### 1. แรงยกที่เกิดจากแรงเฉือน (Shear-Induced Lift)

**Magnus Effect** เป็นกลไกพื้นฐานของแรงยก เมื่ออนุภาคเคลื่อนที่ในกระแสเฉือนจะเกิดการกระจายความดันที่ไม่สมมาตรรอบๆ อนุภาค

**กลไก:**
- ความแตกต่างของความเร็วที่ข้ามอนุภาค → การกระจายความดันไม่สมมาตร
- แรงสุทธิ → ตั้งฉากกับความเร็วสัมพัทธ์และทิศทางของแรงเฉือน

### 2. แรงยกที่เกิดจากการหมุน (Rotation-Induced Lift)

เมื่ออนุภาคหมุนสัมพัทธ์กับของไหลโดยรอบ จะก่อให้เกิดการไหลวน (circulation) ซึ่งสร้างแรงยกตามทฤษฎีบท Kutta-Joukowski:

$$F_L = \rho_f \Gamma U L$$

โดยที่:
- $\rho_f$ = ความหนาแน่นของของไหล
- $\Gamma$ = ความแรงของการไหลวน (circulation strength)
- $U$ = ความเร็วสัมพัทธ์
- $L$ = ความยาวลักษณะเฉพาะ

### 3. แรงยกที่เกิดจากผนัง (Wall-Induced Lift)

เมื่ออนุภาคเข้าใกล้ผนัง:
- สนามการไหลจะบิดเบี้ยวเนื่องจากการมีอยู่ของผนัง
- แรงยกโดยทั่วไปจะผลักอนุภาคให้ออกจากผนัง

### 4. แรงยกสำหรับอนุภาคที่เสียรูป (Deformation-Induced Lift)

สำหรับฟองอากาศและหยดน้ำ การเสียรูปมีผลอย่างมากต่อแรงยก โดยมีพารามิเตอร์สำคัญคือ **Eötvös number**:

$$Eo = \frac{g \Delta \rho d^2}{\sigma}$$

---

## สมการหลัก (Governing Equations)

### แรงยกแบบคลาสสิก (Classical Lift Force)

สำหรับอนุภาคที่เคลื่อนที่ในกระแสเฉือนแบบสม่ำเสมอ:

$$\mathbf{F}_L = C_L \rho_c V_p (\mathbf{u}_c - \mathbf{u}_p) \times (\nabla \times \mathbf{u}_c) \tag{1}$$

**นิยามตัวแปร:**
- $C_L$ = สัมประสิทธิ์แรงยก (lift coefficient)
- $\rho_c$ = ความหนาแน่นของเฟสต่อเนื่อง
- $V_p$ = ปริมาตรของอนุภาค
- $\mathbf{u}_c$ = ความเร็วของเฟสต่อเนื่อง
- $\mathbf{u}_p$ = ความเร็วของอนุภาค
- $\nabla \times \mathbf{u}_c$ = ความปั่นป่วน (vorticity)

### แรงยก Saffman (Saffman Lift Force)

สำหรับ Reynolds number ต่ำในกระแสเฉือนเชิงเส้น:

$$\mathbf{F}_L = C_S \rho_c \nu_c^{1/2} d^2 |\mathbf{u}_c - \mathbf{u}_p| \left(\frac{\partial u_c}{\partial y}\right)^{1/2} \mathbf{n}_L \tag{2}$$

โดยที่:
- $C_S = 6.46$ (ค่าคงที่ทางทฤษฎี)
- $\nu_c = \mu_c/\rho_c$ = ความหนืดจลน์
- $d$ = เส้นผ่านศูนย์กลางของอนุภาค
- $\mathbf{n}_L$ = เวกเตอร์หนึ่งหน่วยที่ตั้งฉากกับทั้งความเร็วสัมพัทธ์และทิศทางของการเฉือน

### แรงยกเฉลี่ยตามปริมาตร (Volume-Averaged Lift Force)

สำหรับระบบหลายเฟส:

$$\mathbf{F}_{L,kl} = C_L \rho_k \alpha_k (\mathbf{u}_l - \mathbf{u}_k) \times (\nabla \times \mathbf{u}_k) \tag{3}$$

**นิยามตัวแปร:**
- $\mathbf{F}_{L,kl}$ = แรงยกต่อหน่วยปริมาตรที่กระทำต่อเฟส $k$ เนื่องมาจากเฟส $l$
- $\alpha_k$ = เศษส่วนปริมาตรของเฟส $k$

---

## แบบจำลองที่สำคัญ (Key Models)

### โมเดลแรงยก Saffman-Mei (Saffman-Mei Lift Model)

เป็นการต่อยอดจากทฤษฎีแรงยก Saffman แบบดั้งเดิม เพื่อพิจารณาผลกระทบของ Reynolds number ที่มีค่าจำกัด:

$$C_L = \begin{cases}
\frac{2.255}{\sqrt{Re_p S}} \left(1 - 0.15 Re_p^{0.687}\right) & Re_p < 40 \\
\frac{1}{\sqrt{Re_p S}} \left(0.5 + 0.2 Re_p\right) & 40 \leq Re_p \leq 1000
\end{cases} \tag{4}$$

**การนิยามตัวแปร:**
- $Re_p = \frac{\rho_c d_p |\mathbf{u}_c - \mathbf{u}_p|}{\mu_c}$ = Particle Reynolds number
- $S = \frac{d_p}{|\mathbf{u}_c - \mathbf{u}_p|} \sqrt{\left|\frac{\partial \mathbf{u}_c}{\partial y}\right|^2 + \left|\frac{\partial \mathbf{u}_c}{\partial z}\right|^2}$ = Dimensionless shear rate parameter

### โมเดลแรงยก Tomiyama (Tomiyama Lift Model)

ถูกพัฒนาขึ้นโดยเฉพาะสำหรับ==ฟองอากาศที่เสียรูปได้==ในการไหลของของเหลว:

$$C_L = \begin{cases}
\min\left[0.288 \tanh(0.121 Re_p), f(Eo)\right] & Eo \leq 4 \\
f(Eo) & 4 < Eo \leq 10 \\
-0.27 & Eo > 10
\end{cases} \tag{5}$$

**ฟังก์ชันวิกฤต:**
$$f(Eo) = 0.00105 Eo^3 - 0.1159 Eo^2 + 0.426 Eo - 0.2303$$

**นิยามตัวแปร:**
- $Eo = \frac{(\rho_c - \rho_d) g d_p^2}{\sigma}$ = Eötvös number

> [!TIP] ปรากฏการณ์ Wall Peeling
> คุณสมบัติที่น่าทึ่งที่สุดของโมเดล Tomiyama คือการทำนายค่าสัมประสิทธิ์แรงยกที่เป็น==ลบ==สำหรับ $Eo > 10$ ซึ่งอธิบายปรากฏการณ์ wall peeling ที่ฟองอากาศขนาดใหญ่จะเคลื่อนที่ออกจากผนังไปยังศูนย์กลางของช่องไหล

### โมเดลแรงยก Legendre-Magnaudet (Legendre-Magnaudet Lift Model)

เป็นกรอบการทำงานที่ครอบคลุมสำหรับการคำนวณแรงยกบนฟองอากาศในการไหลแบบหนืด โดยพิจารณาอัตราส่วนความหนืด:

$$C_L = C_L^{\text{inviscid}} + C_L^{\text{viscous}} \tag{6}$$

**ส่วน Inviscid:**
$$C_L^{\text{inviscid}} = \frac{6}{\pi^2} \frac{(2 + \lambda)^2 + \lambda}{(1 + \lambda)^3}$$

**ส่วน Viscous:**
$$C_L^{\text{viscous}} = \frac{16}{\pi} \frac{\lambda}{(1 + \lambda)^2} \frac{1}{\sqrt{Re_p}}$$

โดยที่ $\lambda = \mu_d/\mu_c$ = อัตราส่วนความหนืดระหว่างเฟสที่กระจายตัวและเฟสต่อเนื่อง

---

## พารามิเตอร์ไร้มิติ (Dimensionless Parameters)

### Particle Reynolds Number

$$Re_p = \frac{\rho_c |\mathbf{u}_c - \mathbf{u}_p| d}{\mu_c} \tag{7}$$

เป็นตัวบ่งชี้ความสำคัญสัมพัทธ์ของแรงเฉื่อยต่อแรงหนืดสำหรับอนุภาคที่เคลื่อนที่ผ่านเฟสต่อเนื่อง

### Shear Reynolds Number

$$Re_\gamma = \frac{\rho_c \gamma d^2}{\mu_c} \tag{8}$$

โดยที่ $\gamma = \frac{\partial u_c}{\partial y}$ = อัตราการเฉือน (shear rate)

เป็นตัววัดความแรงของกระแสเฉือนที่กระทำเทียบกับผลของความหนืด

### Saffman Parameter

$$S = \frac{Re_\gamma^{1/2}}{Re_p} \tag{9}$$

| เงื่อนไข | ค่า S | ผลลัพธ์ |
|-----------|--------|----------|
| **Valid Saffman Theory** | $S \gg 1$ | $Re_p \ll Re_\gamma^{1/2}$ |
| **Transition Region** | $S \sim 1$ | ต้องใช้โมเดลที่ซับซ้อนกว่า |
| **Invalid Saffman Theory** | $S \ll 1$ | อนุภาคมีอิทธิพลเหนือการเฉือน |

---

## การนำไปใช้ใน OpenFOAM (OpenFOAM Implementation)

### สถาปัตยกรรมหลัก (Core Architecture)

```
liftModel (Abstract Interface)
├── dispersedLiftModel (สำหรับอนุภาคในเฟสกระจายตัว)
├── TomiyamaLift
├── constantLiftCoefficient
├── noLift
└── wallDampedLift
```

### การตั้งค่าใน `constant/phaseProperties`

```openfoam
lift
(
    (air in water)
    {
        type            Tomiyama;
    }
);
```

### OpenFOAM Code Implementation

#### การคำนวณแรงยกแบบ Saffman-Mei

```cpp
// Saffman-Mei lift force calculation in OpenFOAM
// Source: .applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystem.C
class SaffmanMeiLift : public liftModel
{
    // Calculate lift coefficient based on particle Reynolds and Saffman parameter
    virtual tmp<volScalarField> Cl() const
    {
        const volScalarField& Re = pair_.Re();
        const volScalarField& Sr = pair_.Sr(); // Saffman parameter

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

        // Loop through all cells to calculate local lift coefficient
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
                // High Reynolds number regime - lift coefficient approaches zero
                Cl[celli] = 0;
            }
        }

        return tCl;
    }

    // Calculate lift force vector field
    virtual tmp<volVectorField> Fi() const
    {
        const phaseModel& dispersed = pair_.dispersed();
        const phaseModel& continuous = pair_.continuous();

        const volScalarField& alpha = dispersed.alpha();
        const volScalarField& rho = continuous.rho();
        const volVectorField& Uc = continuous.U();
        const volVectorField& Ud = dispersed.U();
        const volScalarField& Cl = this->Cl();

        // Relative velocity between phases
        volVectorField Ur = Ud - Uc;

        // Vorticity of continuous phase (curl of velocity field)
        volVectorField omega = fvc::curl(Uc);

        // Calculate lift force: F_L = rho * alpha * C_L * (U_r x omega)
        return rho*alpha*Cl*Ur*omega;
    }
};
```

**คำอธิบายโค้ด:**
- **📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystem.C`
- **การทำงาน:** คลาส `SaffmanMeiLift` คำนวณสัมประสิทธิ์แรงยก $C_L$ ตามโมเดล Saffman-Mei โดยแบ่งเป็น 3 ช่วงของ Reynolds number
- **แนวคิดสำคัญ:**
  - ใช้ `pair_.Re()` และ `pair_.Sr()` เพื่อรับค่า Reynolds number และ Saffman parameter
  - สร้าง `volScalarField` สำหรับเก็บค่าสัมประสิทธิ์แรงยกในแต่ละเซลล์
  - ใช้เงื่อนไข `if-else` เพื่อเลือกสมการที่เหมาะสมกับช่วง Reynolds number
  - ฟังก์ชัน `Fi()` คำนวณแรงยกเวกเตอร์โดยใช้ cross product ระหว่างความเร็วสัมพัทธ์และความหมุนวน
- **เทคนิค OpenFOAM:** ใช้ `fvc::curl()` ในการคำนวณความหมุนวน และ `volVectorField` สำหรับเก็บข้อมูลเวกเตอร์ในแต่ละเซลล์

---

#### การคำนวณแรงยกแบบ Tomiyama

```cpp
// Tomiyama lift model for deformable bubbles
// Source: .applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystem.C
class TomiyamaLift : public liftModel
{
    // Calculate Tomiyama lift coefficient based on Eötvös number
    virtual tmp<volScalarField> Cl() const
    {
        const volScalarField& Re = pair_.Re();
        const volScalarField& Eo = pair_.Eo();

        tmp<volScalarField> tCl = volScalarField::New("Cl", pair_.mesh(), 0.0);
        volScalarField& Cl = tCl.ref();

        // Loop through all cells to calculate local lift coefficient
        forAll(Cl, celli)
        {
            scalar Re_local = Re[celli];
            scalar Eo_local = Eo[celli];

            // Calculate tanh component for small bubbles
            scalar Cl_tanh = 0.288*tanh(0.121*Re_local);

            // Calculate cubic polynomial function of Eötvös number
            scalar f_Eo = 0.00105*pow(Eo_local, 3)
                        - 0.1159*pow(Eo_local, 2)
                        + 0.426*Eo_local
                        - 0.2303;

            if (Eo_local <= 4)
            {
                // Small spherical bubbles - use minimum of tanh and polynomial
                Cl[celli] = min(Cl_tanh, f_Eo);
            }
            else if (Eo_local <= 10)
            {
                // Transition regime - deformable bubbles
                Cl[celli] = f_Eo;
            }
            else
            {
                // Large bubbles - negative lift coefficient (wall peeling effect)
                Cl[celli] = -0.27;
            }
        }

        return tCl;
    }
};
```

**คำอธิบายโค้ด:**
- **📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystem.C`
- **การทำงาน:** โมเดล Tomiyama ออกแบบมาสำหรับฟองอากาศที่เสียรูปได้ โดยคำนึงถึงผลกระทบของ Eötvös number ($Eo$)
- **แนวคิดสำคัญ:**
  - ใช้ `pair_.Eo()` เพื่อรับค่า Eötvös number ซึ่งวัดระดับการเสียรูปของฟองอากาศ
  - สำหรับ $Eo \leq 4$: ฟองอากาศมีรูปร่างเกือบกลม ใช้ค่าน้อยสุดระหว่างฟังก์ชัน `tanh` และพหุนาม
  - สำหรับ $4 < Eo \leq 10$: ฟองอากาศเริ่มเสียรูป ใช้ฟังก์ชันพหุนามอย่างเดียว
  - สำหรับ $Eo > 10$: ฟองอากาศเสียรูปมาก มีสัมประสิทธิ์แรงยกเป็นลบ ($C_L = -0.27$) ซึ่งอธิบายปรากฏการณ์ wall peeling
- **เทคนิค OpenFOAM:** ใช้ `volScalarField::New()` ในการสร้าง field ใหม่ และ `min()` function สำหรับเปรียบเทียบค่า
- **การประยุกต์ใช้:** โมเดลนี้เหมาะสำหรับการจำลองการไหลของฟองอากาศในเครื่องปฏิกรณ์และช่องไหลแนวตั้ง

---

#### การคำนวณแรงยกในสมการโมเมนตัม

```cpp
// Adding lift force to momentum equation
// Source: .applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystem.C
// Calculate lift force from dispersed phase model
tmp<volVectorField> liftForce = dispersedLift.Flift();

// Add lift force as source term to momentum equation
// This adds the cross product of relative velocity and vorticity
momentumEqn += liftForce;
```

**คำอธิบายโค้ด:**
- **📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystem.C`
- **การทำงาน:** เพิ่มแรงยกเป็นเทอม source ในสมการโมเมนตัม
- **แนวคิดสำคัญ:**
  - `dispersedLift.Flift()` คำนวณแรงยกต่อหน่วยปริมาตรจากโมเดลที่เลือก
  - แรงยกถูกเพิ่มเข้าไปในสมการโมเมนตัมโดยตรงผ่าน operator `+=`
  - การทำเช่นนี้ทำให้ solver คำนวณผลกระทบของแรงยกต่อการเคลื่อนที่ของเฟสกระจาย
- **เทคนิค OpenFOAM:** ใช้ `tmp<volVectorField>` สำหรับการจัดการหน่วยความจำอัตโนมัติ และ `momentumEqn` เป็น object ที่เก็บสมการโมเมนตัม
- **ข้อควรระวัง:** แรงยกเป็นเทอม source ที่สามารถก่อให้เกิดปัญหาความไม่เสถียรเชิงตัวเลขได้ ควรใช้ under-relaxation

---

## แรงยกที่เกิดจากผนัง (Wall-Induced Lift)

### แบบจำลองแรงยกที่แก้ไขโดยผนัง (Wall-Corrected Lift Model)

$$C_L^{wall} = C_L^{\infty} f\left(\frac{y_w}{d}\right) \tag{10}$$

**ฟังก์ชันการแก้ไขผนัง:**
$$f\left(\frac{y_w}{d}\right) = 1 - \exp\left(-\beta \frac{y_w}{d}\right)$$

โดยที่ $\beta \approx 1.5$ สำหรับสภาวะโฟลว์แบบหลายเฟสทั่วไป

### OpenFOAM Implementation สำหรับ Wall-Induced Lift

```cpp
// Wall-induced lift calculation with distance-based correction
// Source: .applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystem.C
// Loop through all boundary cells to calculate wall-induced lift
forAll(wallInducedLift, i)
{
    // Calculate distance to nearest wall
    scalar yw = wallDist[i];

    // Calculate dimensionless distance parameter
    scalar eta = yw/phase.d();

    if (eta > 0.1)
    {
        // Wall-corrected regime - use exponential damping function
        scalar fWall = 1.0 - exp(-beta_*eta);
        wallInducedLift[i] = liftCoeff[i] * fWall;
    }
    else
    {
        // Lubrication regime - very close to wall
        // Use lubrication theory approximation
        vector up = phase.U()[i];
        vector uw = wallVelocity[i];
        vector upw = up - uw;

        // Apply lubrication force correction
        wallInducedLift[i] = -Club_ * muContinuous[i] *
                           sqr(phase.d()[i])/yw * upw;
    }
}
```

**คำอธิบายโค้ด:**
- **📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystem.C`
- **การทำงาน:** คำนวณแรงยกที่ถูกแก้ไขโดยผนัง โดยพิจารณาระยะห่างจากผนัง
- **แนวคิดสำคัญ:**
  - คำนวณระยะห่างไร้มิติ $\eta = y_w/d$ โดย $y_w$ คือระยะห่างจากผนัง และ $d$ คือเส้นผ่านศูนย์กลางอนุภาค
  - สำหรับ $\eta > 0.1$: ใช้ฟังก์ชัน damping $f(\eta) = 1 - e^{-\beta\eta}$ เพื่อลดทอนแรงยกเมื่อใกล้ผนัง
  - สำหรับ $\eta \leq 0.1$: ใช้ทฤษฎี lubrication ซึ่งแรงขึ้นกับ $\mu U d^2 / y_w$
- **เทคนิค OpenFOAM:** ใช้ `wallDist` field สำหรับระยะห่างจากผนัง และ `forAll` loop สำหรับการคำนวณในแต่ละเซลล์
- **การประยุกต์ใช้:** โมเดลนี้สำคัญสำหรับการจำลองการไหลในท่อและช่องทางที่มีผนัง

---

## แรงยกอนุภาคที่เปลี่ยนรูปได้ (Deformable Particle Lift)

### ผลกระทบจากรูปร่าง (Shape Effects)

**Aspect Ratio:**
$$\mathcal{AR} = \frac{d_{major}}{d_{minor}}$$

**พารามิเตอร์การเปลี่ยนรูป:**
$$\epsilon = \frac{d_{major} - d_{minor}}{d_{major} + d_{minor}}$$

### แบบจำลองเชิงเส้น (Linear Model)

สำหรับการเปลี่ยนรูปปานกลาง:

$$C_L = C_{L,0} (1 + \beta_d \epsilon) \tag{11}$$

### แบบจำลองที่ไม่ใช่เชิงเส้น (Nonlinear Model)

สำหรับความแม่นยำสูงในช่วงการเปลี่ยนรูปทั้งหมด:

$$C_L = C_{L,0} \left[1 + \beta_1 \epsilon + \beta_2 \epsilon^2 + \beta_3 \epsilon^3 + \mathcal{O}(\epsilon^4)\right] \tag{12}$$

---

## ข้อควรพิจารณาเชิงตัวเลข (Numerical Considerations)

### ความเสถียรเชิงตัวเลข (Numerical Stability)

การนำแรงยกในของไหลหลายเฟสมาใช้งานนั้นมีปัญหาเชิงตัวเลขหลายประการ:

#### 1. ความไวต่อการคำนวณความหมุนวน

การคำนวณความหมุนวน $\boldsymbol{\omega} = \nabla \times \mathbf{u}$ จำเป็นต้องใช้ค่าอนุพันธ์อันดับสองของสนามความเร็ว

#### 2. เทคนิคการทำให้เรียบ (Regularization Techniques)

**การทำให้สนามความหมุนวนเรียบ:**
$$\boldsymbol{\omega}_{smoothed} = \boldsymbol{\omega} + \nu_{smooth} \nabla^2 \boldsymbol{\omega}$$

```cpp
// Vorticity smoothing implementation
// Source: .applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystem.C
// Smooth vorticity field using Laplacian operator
volVectorField omegaSmoothed = omega + nuSmooth * fvc::laplacian(omega);
```

**คำอธิบายโค้ด:**
- **📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystem.C`
- **การทำงาน:** ทำให้สนามความหมุนวนเรียบขึ้นโดยใช้ diffusion filtering
- **แนวคิดสำคัญ:**
  - เพิ่มเทอม Laplacian $\nabla^2 \boldsymbol{\omega}$ เข้ากับสนามความหมุนวนเดิม
  - พารามิเตอร์ $\nu_{smooth}$ คือค่าสัมประสิทธิ์การทำให้เรียบ (smoothing coefficient)
  - การทำเช่นนี้ช่วยลดความผันผวนของสนามความหมุนวนที่เกิดจากความละเอียดของ mesh
- **เทคนิค OpenFOAM:** ใช้ `fvc::laplacian()` ในการคำนวณ Laplacian operator
- **ข้อควรระวัง:** ค่า $\nu_{smooth}$ ที่สูงเกินไปอาจทำให้สูญเสียข้อมูลทางกายภาพของการไหล

---

**การจำกัดค่าสัมประสิทธิ์แรงยก:**
$$C_L^{limited} = \text{sign}(C_L) \min(|C_L|, C_L^{max})$$

```cpp
// Lift coefficient limiting to prevent numerical instability
// Source: .applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystem.C
// Limit lift coefficient to maximum absolute value
scalar CLimited = sign(CL) * min(mag(CL), CLmax);
```

**คำอธิบายโค้ด:**
- **📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystem.C`
- **การทำงาน:** จำกัดค่าสัมประสิทธิ์แรงยกไม่ให้เกินค่าสูงสุดที่กำหนด
- **แนวคิดสำคัญ:**
  - ใช้ฟังก์ชัน `min()` เพื่อให้แน่ใจว่า $|C_L| \leq C_L^{max}$
  - ใช้ `sign()` เพื่อรักษาเครื่องหมายของสัมประสิทธิ์แรงยก
  - ค่า $C_L^{max}$ ทั่วไปอยู่ที่ประมาณ 0.5-1.0 สำหรับการประยุกต์ใช้งานส่วนใหญ่
- **เทคนิค OpenFOAM:** ใช้ `sign()` และ `mag()` functions สำหรับการจัดการสเกลาร์
- **ข้อควรระวัง:** การจำกัดค่ามากเกินไปอาจทำให้สูญเสียความแม่นยำทางกายภาพ

---

#### 3. การนำ Under-Relaxation มาใช้

แรงยกที่ปรับค่าแล้ว:

$$\mathbf{F}_L^{new} = (1-\lambda_L)\mathbf{F}_L^{old} + \lambda_L \mathbf{F}_L^{calculated} \tag{13}$$

```cpp
// Lift force under-relaxation for stability
// Source: .applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystem.C
// Set relaxation factor (typical value: 0.3-0.5)
scalar lambdaL = 0.4;

// Apply under-relaxation to lift force
// New value = weighted average of old and calculated values
liftForce = (1.0 - lambdaL) * liftForce.oldTime() + lambdaL * liftForceCalculated;
```

**คำอธิบายโค้ด:**
- **📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystem.C`
- **การทำงาน:** ใช้เทคนิค under-relaxation เพื่อปรับปรุงความเสถียรของการคำนวณ
- **แนวคิดสำคัญ:**
  - พารามิเตอร์ $\lambda_L$ คีสัมประสิทธิ์การปรับค่า (relaxation factor) โดยมีค่าระหว่าง 0 ถึง 1
  - ค่าที่แนะนำ: $\lambda_L = 0.3-0.5$ สำหรับการประยุกต์ใช้งานส่วนใหญ่
  - ค่า $\lambda_L$ ที่ต่ำกว่าทำให้การคำนานมีความเสถียรมากขึ้น แต่การลู่เข้าจะช้าลง
  - ใช้ `oldTime()` เพื่อเข้าถึงค่าจาก time step ก่อนหน้า
- **เทคนิค OpenFOAM:** ใช้การคูณ scalar กับ field และการบวก field โดยตรง
- **ข้อควรระวัง:** ค่า $\lambda_L$ ที่สูงเกินไปอาจก่อให้เกิด oscillation และความไม่เสถียร

---

## แนวทางการเลือกแบบจำลอง (Model Selection Guidelines)

### การไหลที่จำนวน Reynolds ต่ำ ($Re_p < 1$)

- **ใช้แบบจำลอง:** Saffman-Mei lift
- **ผลกระทบ:** ผลกระทบจากความหนืดมีอิทธิพลหลัก
- **เหมาะสำหรับ:** อนุภาคขนาดเล็กในของไหลหนืด

### การไหลที่จำนวน Reynolds ปานกลาง ($1 < Re_p < 100$)

| สถานการณ์ | แบบจำลองที่แนะนำ |
|------------|---------------------|
| **อนุภาคที่เสียรูป** | ใช้แบบจำลอง Tomiyama |
| **อนุภาคแข็ง (rigid particles)** | ใช้สัมประสิทธิ์คงที่ |

### การไหลที่จำนวน Reynolds สูง ($Re_p > 100$)

- **แนวทาง:** พิจารณาผลกระทบจากความปั่นป่วน
- **อาจต้องใช้:** แบบจำลองการเสียรูปขั้นสูง

### การไหลที่มีผนังล้อมรอบ (Wall-Bounded Flows)

> [!WARNING] การใช้งานโมเดลใกล้ผนัง
> **ใช้แบบจำลองที่หน่วงด้วยผนังเสมอ** (Always use wall-damped models) มีความสำคัญอย่างยิ่งต่อการทำนายค่าที่แม่นยำใกล้ผนัง

---

## การประยุกต์ใช้งานทางวิศวกรรม (Engineering Applications)

### การไหลแบบมีฟองอากาศ (Bubbly Flows)

| การประยุกต์ใช้ | บทบาทของแรงยก |
|----------------|----------------|
| การเคลื่อนที่ของฟองอากาศในช่องแนวตั้ง | ควบคุมการกระจายตัวของฟองในหม้อน้ำ |
| การกระจายตัวของฟองอากาศในเครื่องปฏิกรณ์ | ส่งผลต่อประสิทธิภาพการผสมและปฏิกิริยา |
| อุปกรณ์แยกเฟส | ช่วยในการแยกเฟสด้วยแรงลิฟต์ |

### การไหลที่มีอนุภาค (Particle-Laden Flows)

| การประยุกต์ใช้ | บทบาทของแรงยก |
|----------------|----------------|
| การขนส่งตะกอน (Sediment transport) | ส่งผลต่อการตกตะกอนและการถูกพัดพา |
| การแยกอนุภาคในเครื่องผสม | สร้างการกระจายตัวที่ไม่สม่ำเสมอ |
| ระบบขนส่งด้วยของเหลว | ส่งผลต่อการยกตัวของอนุภาค |

### ระบบเตียงฟลูอิไดซ์ (Fluidized Bed Systems)

แรงยกขับเคลื่อนการเคลื่อนที่ของอนุภาคในแนวข้าง ทำให้เกิดรูปแบบการไหลเวียนที่ช่วยเพิ่มการผสม:

- **การไหลเวียนแบบกัลฟ์สตรีม:** รูปแบบการไหลเวียนขนาดใหญ่
- **การผสมในรอยตามของฟองอากาศ:** อนุภาคที่ถูกพาไปในรอยตาม
- **การกระจายตัวในแนวข้าง:** การกระจายตัวของอนุภาค

---

## สรุป (Summary)

แรงยกในการไหลแบบหลายเฟสเป็นปรากฏการณ์ที่ซับซ้อนซึ่งมีความสำคัญอย่างยิ่งต่อการทำนายการกระจายตัวของเฟสในระบบทางวิศวกรรม

### จุดสำคัญที่ต้องจำ:

1. **กลไกทางฟิสิกส์:** แรงยกเกิดจากการไหลแบบเฉือน การหมุนของอนุภาค ผลกระทบจากผนัง และการเสียรูป
2. **การเลือกแบบจำลอง:** ขึ้นอยู่กับ Reynolds number คุณสมบัติของอนุภาค และสภาวะการไหล
3. **การนำไปใช้ใน OpenFOAM:** มีกรอบการทำงานแบบโมดูลาร์ที่รองรับหลายแบบจำลอง
4. **ความเสถียรเชิงตัวเลข:** ต้องใช้เทคนิคการทำให้เรียบและการปรับค่าเพื่อความเสถียร

การเลือกแบบจำลองแรงยกที่เหมาะสม รวมกับการพิจารณาด้านความเสถียรเชิงตัวเลข จะช่วยให้การทำนายการไหลแบบหลายเฟสมีความแม่นยำและเชื่อถือได้

---

## แหล่งอ้างอิงเพิ่มเติม (Further Reading)

สำหรับข้อมูลเพิ่มเติมเกี่ยวกับหัวข้อเฉพาะทาง โปรดดู:

- [[01_Introduction]] - รายละเอียดเกี่ยวกับแนวคิดพื้นฐานและประวัติ
- [[02_Physical_Mechanisms]] - กลไกทางกายภาพที่ละเอียด
- [[03_Fundamental_Lift_Force_Derivation]] - การหาแรงยกพื้นฐาน
- [[04_Specific_Lift_Models]] - โมเดลแรงยกเฉพาะทาง
- [[08_OpenFOAM_Implementation]] - รายละเอียดการนำไปใช้ใน OpenFOAM
- [[09_Numerical_Considerations]] - ข้อควรพิจารณาเชิงตัวเลข
- [[10_Applications_and_Examples]] - ตัวอย่างการประยุกต์ใช้งาน