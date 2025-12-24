# แนวคิดพื้นฐานของแรงยก (Fundamental Lift Concepts)

## 1. บทนำ (Introduction)

**แรงยก (Lift forces)** ในการไหลหลายเฟสคือแรงที่กระทำต่อเฟสกระจาย (อนุภาค, ฟองอากาศ, หยดของเหลว) ในทิศทาง **ตั้งฉาก (Perpendicular)** กับความเร็วสัมพัทธ์ระหว่างเฟส แรงนี้มีบทบาทสำคัญในการกำหนดการกระจายตัวของเฟสในแนวขวาง

### คุณสมบัติหลัก
- มีทิศทางตั้งฉากกับความเร็วสัมพัทธ์ระหว่างเฟส
- เกิดจากปรากฏการณ์ทางกายภาพที่หลากหลาย:
  - แรงเฉือน (shear) ในเฟสต่อเนื่อง
  - ความแตกต่างของความดัน (pressure gradients)
  - การหมุนของอนุภาค (particle rotation)
  - การมีอยู่ของผนังที่อยู่ใกล้เคียง

### สมการหลัก

$$\mathbf{F}_L = C_L \rho_c V_p (\mathbf{u}_c - \mathbf{u}_p) \times (\nabla \times \mathbf{u}_c) \tag{1.1}$$

โดยที่:
- $C_L$ = สัมประสิทธิ์แรงยก (lift coefficient) ซึ่งขึ้นอยู่กับสภาวะการไหล
- $\rho_c$ = ความหนาแน่นของเฟสต่อเนื่อง
- $V_p$ = ปริมาตรของอนุภาค
- $\mathbf{u}_c$ = ความเร็วของเฟสต่อเนื่อง
- $\mathbf{u}_p$ = ความเร็วของอนุภาค
- $\nabla \times \mathbf{u}_c$ = ความหมุนวน (vorticity)

---

## 2. กลไกทางกายภาพ (Physical Mechanisms)

### 2.1 Magnus Effect

กลไกพื้นฐานสำหรับแรงยกคือ **Magnus effect** ซึ่งวัตถุที่หมุนหรือเคลื่อนที่แบบไม่สมมาตรจะประสบกับแรงที่ตั้งฉากกับการเคลื่อนที่ ปรากฏการณ์นี้เกิดขึ้นจากการปฏิสัมพันธ์ระหว่างการเคลื่อนที่ของวัตถุและสนามการไหลของของไหลโดยรอบ ทำให้เกิดการกระจายความดันที่ไม่สมมาตรซึ่งสร้างแรงสุทธิที่ตั้งฉากกับทิศทางการเคลื่อนที่หลัก

### 2.2 Shear-Induced Lift (Saffman Lift)

เกิดขึ้นเมื่ออนุภาคอยู่ในบริเวณที่มีความชันของความเร็ว (Velocity gradient) ความเร็วที่แตกต่างกันระหว่างสองด้านของอนุภาคทำให้เกิดความแตกต่างของความดัน (Bernoulli effect) และแรงเค้นหนืดที่ไม่สมมาตร ส่งผลให้เกิดแรงยกสุทธิ

**กลไก:**
- ความแตกต่างของความเร็ว → การกระจายความดันไม่สมมาตร
- แรงสุทธิ → ตั้งฉากกับความเร็วสัมพัทธ์และทิศทางของแรงเฉือน

**คุณสมบัติ:**
- มีอิทธิพลที่จำนวน Reynolds ต่ำ (low Reynolds numbers)
- ผลกระทบจากความหนืด (viscous effects) มีความสำคัญ
- เกี่ยวข้องกับการกระจายตัวของความดันที่ไม่สมมาตร

### 2.3 Rotation-Induced Lift (Magnus Effect)

หากอนุภาคมีการหมุน (Rotation) ความเร็วที่ผิวของอนุภาคจะเสริมกับความเร็วของไหลในด้านหนึ่งและต้านในอีกด้านหนึ่ง สร้างการไหลวน (Circulation) และแรงยกตามทฤษฎีบท Kutta-Joukowski

**สมการ Kutta-Joukowski:**
$$F_L = \rho_f \Gamma U L$$

**นิยามตัวแปร:**
- $\rho_f$ = ความหนาแน่นของของไหล
- $\Gamma$ = ความแรงของการไหลวน (circulation strength)
- $U$ = ความเร็วสัมพัทธ์ (relative velocity)
- $L$ = ความยาวลักษณะเฉพาะ (characteristic length)

**คุณสมบัติ:**
- คล้ายกับ Magnus effect บนลูกบอลที่หมุน
- สำคัญสำหรับอนุภาคที่เสียรูป (deformable particles)
- เกี่ยวข้องกับอนุภาคที่มีการไหลวนภายใน

### 2.4 Wall-Induced Lift

ใกล้ผนัง สนามการไหลจะบิดเบี้ยวเนื่องจากข้อจำกัดทางเรขาคณิต โดยทั่วไปจะสร้างแรงผลัก (Repulsion) ให้อนุภาคเคลื่อนที่ออกจากผนัง

**ปัจจัยที่มีผล:**
- ผลกระทบของภาพเสมือนการไหลวน (Image vortex effects)
- ความแตกต่างของความดันที่เกิดจากผนัง (Wall-induced pressure gradients)
- อัตราการเฉือนที่เปลี่ยนแปลงไป (Modified shear rates)
- ปฏิสัมพันธ์ทางอุทกพลศาสตร์กับขอบเขตผนัง

---

## 3. Flow Asymmetry

สาเหตุพื้นฐานของแรงยกใน Multiphase flow มาจาก **Flow asymmetry** รอบอนุภาค

### การไหลแบบ Shear และ Gradient ความเร็ว

พิจารณาอนุภาคในการไหลแบบ Shear ที่มี Gradient ความเร็ว $\frac{\partial u}{\partial y} \neq 0$:

```
          Higher velocity
        -------------------  u(y + d/2)
              |
              |  Particle
              |
        -------------------  u(y - d/2)
          Lower velocity
```

### 3.1 Pressure Asymmetry

**กลไก:**
- ความแตกต่างของความเร็วส่งผลให้เกิดความดันหยุดนิ่ง (stagnation pressures) ที่แตกต่างกัน
- ตามสมการ Bernoulli:
  $$p + \frac{1}{2}\rho u^2 = \text{constant}$$

**ผลลัพธ์:**
- ความเร็วที่สูงกว่าด้านหนึ่งส่งผลให้ความดันสถิต (static pressure) ต่ำลง
- ความเร็วที่ต่ำกว่าอีกด้านหนึ่งส่งผลให้ความดันสถิตสูงขึ้น
- ความแตกต่างของความดันนี้ $\Delta p$ ที่ข้ามอนุภาคจะสร้างแรงสุทธิที่ตั้งฉากกับทิศทางการไหลหลัก

### 3.2 Viscous Asymmetry

**กลไก:**
- ความเค้นเฉือน (shear stresses) ที่กระทำต่อพื้นผิวอนุภาคไม่สมมาตร
- เนื่องจาก Gradient ความเร็ว

**สมการ:**
$$\tau = \mu \frac{\partial u}{\partial n}$$

**นิยามตัวแปร:**
- $\tau$ = ความเค้นเฉือนเฉพาะที่ (local shear stress)
- $\mu$ = ความหนืดไดนามิก (dynamic viscosity)
- $\frac{\partial u}{\partial n}$ = Gradient ความเร็วที่ตั้งฉากกับพื้ผิว

**ผลลัพธ์:** การแปรผันของความเค้นเฉือนนี้มีส่วนช่วยต่อแรงยกสุทธิ

---

## 4. การวิเคราะห์ทางคณิตศาสตร์ (Mathematical Derivation)

### 4.1 แรงยกแบบคลาสสิก (Classical Lift Force)

$$\mathbf{F}_L = C_L \rho_c V_p (\mathbf{u}_c - \mathbf{u}_p) \times (\nabla \times \mathbf{u}_c) \tag{4.1}$$

สูตรแรงยกแบบคลาสสิกแสดงถึง **ปรากฏการณ์ Magnus effect** พื้นฐาน:
- อนุภาคจะได้รับแรงในแนวข้างตั้งฉากกับทั้งความเร็วสัมพัทธ์และความปั่นป่วนเฉพาะที่
- **ความสัมพันธ์แบบ cross-product** ทำให้มั่นใจได้ว่าแรงยกจะตั้งฉากกับระนาบที่เกิดจากเวกเตอร์ความเร็วสัมพัทธ์และเวกเตอร์ความปั่นป่วนเสมอ
- ส่งผลให้เกิดการเคลื่อนที่ของอนุภาคในแนวข้างสัมพันธ์กับทิศทางการไหล

### 4.2 แรงยก Saffman (สำหรับ Reynolds ต่ำ)

สำหรับ **Reynolds number ที่มีค่าน้อย** ในกระแสเฉือนเชิงเส้น (linear shear flow):

$$\mathbf{F}_L = 1.615 \rho_c \nu_c^{1/2} d^2 (\mathbf{u}_c - \mathbf{u}_p) \left| \frac{\partial u_c}{\partial y} \right|^{1/2} \tag{4.2}$$

**นิยามตัวแปร:**
- $\nu_c = \mu_c/\rho_c$ = **ความหนืดจลนศาสตร์** (kinematic viscosity)
- $d$ = **เส้นผ่านศูนย์กลางของอนุภาค** (particle diameter)
- $\frac{\partial u_c}{\partial y}$ = **อัตราการเฉือน** (shear rate)

แรงยก Saffman เกิดจากการวิเคราะห์ทางทฤษฎีของกระแสไหลที่ **Reynolds number ต่ำ** รอบทรงกลมในฟิลด์เฉือนเชิงเส้น:
- ค่าคงที่ $1.615$ ได้มาจาก **การจับคู่แบบ asymptotic** ของผลเฉลยภายในและภายนอก
- ใช้ได้เมื่อ **particle Reynolds number** มีค่าน้อยกว่ารากที่สองของ **shear Reynolds number** อย่างมาก
- การขึ้นกับ $\nu_c^{1/2}$ สะท้อนถึง **ลักษณะความหนืด** ของกลไกแรงยก
- แรงยกจะแปรผันตามรากที่สองของความหนืดจลนศาสตร์ ซึ่งบ่งชี้ถึงความสำคัญของ **การแพร่แบบหนืด** ในกระบวนการสร้างแรงยก

---

## 5. การวิเคราะห์แบบไร้มิติ (Dimensionless Analysis)

### 5.1 Particle Reynolds Number

กำหนด **particle Reynolds number** โดยอิงตามความเร็วในการเลื่อน (slip velocity):

$$Re_p = \frac{\rho_c |\mathbf{u}_c - \mathbf{u}_p| d}{\mu_c}$$

**Particle Reynolds number** เป็นตัวบ่งชี้:
- ความสำคัญสัมพันธ์ของ **แรงเฉื่อย** ต่อ **แรงหนืด** สำหรับอนุภาคที่เคลื่อนที่ผ่านเฟสต่อเนื่อง
- ใช้ความเร็วในการเลื่อน $|\mathbf{u}_c - \mathbf{u}_p|$ เป็น **มาตราความเร็วลักษณะเฉพาะ**
- แสดงถึงการเคลื่อนที่สัมพันธ์ระหว่างอนุภาคและของไหลที่อยู่รอบๆ

### 5.2 Shear Reynolds Number

กำหนด **shear Reynolds number**:

$$Re_\gamma = \frac{\rho_c \gamma d^2}{\mu_c}$$

โดยที่ $\gamma = \frac{\partial u_c}{\partial y}$ คือ **อัตราการเฉือน** (shear rate)

**Shear Reynolds number** เป็นตัววัด:
- ความแรงของกระแสเฉือนที่กระทำเทียบกับผลของความหนืด
- แตกต่างจาก particle Reynolds number ที่ขึ้นกับการเคลื่อนที่ของอนุภาค
- จะขึ้นอยู่กับความชันของความเร็วที่กำหนดและขนาดของอนุภาคเท่านั้น
- ทำให้เป็น **มาตรวัดความเข้มของการเฉือน** ของฟิลด์การไหล

### 5.3 Saffman Parameter

**Saffman parameter** คือ:

$$S = \frac{Re_\gamma^{1/2}}{Re_p}$$

#### เงื่อนไขการใช้งาน:

| เงื่อนไข | ค่า S | ผลลัพธ์ |
|-----------|--------|----------|
| **Valid Saffman Theory** | $S \gg 1$ | $Re_p \ll Re_\gamma^{1/2}$ |
| **Transition Region** | $S \sim 1$ | ต้องใช้โมเดลที่ซับซ้อนกว่า |
| **Invalid Saffman Theory** | $S \ll 1$ | อนุภาคมีอิทธิพลเหนือการเฉือน |

#### การตีความหมาย:

เมื่อ **$S \gg 1$**:
- กระแสเฉือนมีอิทธิพลเหนือการเคลื่อนที่สัมพัทธ์ของอนุภาค
- อนุภาคจะทำตัวเหมือนเป็น **passive tracer** ในฟิลด์เฉือนที่แรง
- ยืนยันสมมติฐานเบื้องหลังการวิเคราะห์ **asymptotic** ที่ Reynolds number ต่ำของ Saffman
- การรบกวนของอนุภาคต่อการไหลมีค่าน้อยเมื่อเทียบกับการเฉือนที่กำหนด

เมื่อ **$S \sim 1$ หรือน้อยกว่า**:
- การเคลื่อนที่ของอนุภาคจะมีค่าเทียบเคียงได้กับผลกระทบจากการเฉือน
- จะต้องใช้ **โมเดลแรงยกที่ซับซ้อนกว่า** ซึ่งคำนึงถึงผลกระทบของ Reynolds number ที่มีค่าจำกัด

---

## 6. ตารางสรุปพารามิเตอร์ (Summary Table)

| พารามิเตอร์ | นิยาม | ความหมาย |
|-----------|-------|----------|
| **Particle Reynolds ($Re_p$)** | $\frac{\rho_c |\mathbf{u}_r| d}{\mu_c}$ | แรงเฉื่อยต่อแรงหนืดของอนุภาค |
| **Shear Reynolds ($Re_\gamma$)** | $\frac{\rho_c \gamma d^2}{\mu_c}$ | ความแรงของกระแสเฉือน |
| **Saffman Parameter ($S$)** | $\frac{Re_\gamma^{1/2}}{Re_p}$ | ระบุว่าแรงยกจากการเฉือนมีอิทธิพลมากเพียงใด |

---

## 7. การนำไปใช้ใน OpenFOAM

ใน OpenFOAM การคำนวณแรงยกมักใช้ความหมุนวน (Vorticity, $\boldsymbol{\omega} = \nabla \times \mathbf{u}_c$) เป็นตัวแทนของความไม่สมมาตร

```cpp
// Calculate vorticity field from continuous phase velocity
// คำนวณสนามความหมุนวนจากความเร็วเฟสต่อเนื่อง
volVectorField omega = fvc::curl(Uc);

// Compute lift force per unit volume using classical formulation
// คำนวณแรงยกต่อหน่วยปริมาตรโดยใช้สูตรแบบคลาสสิก
// FLift = CL * rho_continuous * alpha_dispersed * (U_continuous - U_dispersed) × vorticity
volVectorField FLift = CL * rhoc * alphad * (Uc - Ud) ^ omega;
```

แรงนี้จะถูกรวมเข้าเป็นเทอมแหล่งกำเนิดในสมการโมเมนตัม เพื่อทำนายการเคลื่อนที่แนวขวางของเฟสกระจายได้อย่างแม่นยำ

```cpp
// Dimensionless parameters calculation for model selection
// คำนวณพารามิเตอร์ไร้มิติสำหรับการเลือกโมเดลที่เหมาะสม

// Calculate particle Reynolds number based on slip velocity
// คำนวณ Particle Reynolds number จากความเร็วสัมพัทธ์
scalar Re_p = rhoContinuous_ * slipVelocity * d_ / muContinuous_;

// Calculate shear Reynolds number based on shear rate
// คำนวณ Shear Reynolds number จากอัตราการเฉือน
scalar Re_gamma = rhoContinuous_ * shearRate * sqr(d_) / muContinuous_;

// Calculate Saffman parameter to determine appropriate lift model
// คำนวณพารามิเตอร์ Saffman เพื่อกำหนดโมเดลแรงยกที่เหมาะสม
scalar SaffmanParameter = sqrt(Re_gamma) / Re_p;

// Check validity of Saffman theory based on Saffman parameter
// ตรวจสอบความถูกต้องของทฤษฎี Saffman จากพารามิเตอร์
if (SaffmanParameter > 10.0) // S >> 1: Strong shear dominates
{
    // Use Saffman lift model for low Reynolds number shear flow
    // ใช้โมเดลแรงยก Saffman สำหรับการไหลแบบเฉือนที่ Reynolds number ต่ำ
}
else
{
    // Use more complex lift model for general flow conditions
    // ใช้โมเดลแรงยกที่ซับซ้อนกว่าสำหรับสภาวะการไหลทั่วไป
}
```

<details>
<summary>📖 คำอธิบายเพิ่มเติม (Thai Explanation)</summary>

**ที่มาทางทฤษฎี (Theoretical Background):**
โค้ดนี้แสดงการตรวจสอบเงื่อนไขการใช้งานทฤษฎี Saffman โดยใช้พารามิเตอร์ไร้มิติ การคำนวณเหล่านี้สำคัญในการกำหนดขอบเขตที่เหมาะสมของแต่ละโมเดลแรงยก

**แหล่งที่มา (Source):**
📂 `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C`

**แนวคิดสำคัญ (Key Concepts):**
- **Particle Reynolds Number**: วัดความสำคัญของแรงเฉื่อยเทียบกับแรงหนืดสำหรับอนุภาค
- **Shear Reynolds Number**: วัดความแรงของการเฉือนในสนามการไหล
- **Saffman Parameter**: ตัวบ่งชี้ว่าทฤษฎี Saffman ใช้ได้หรือไม่ (S >> 1)
- **Model Selection**: การเลือกโมเดลที่เหมาะสมขึ้นกับสภาวะการไหล

</details>

```cpp
// Classical lift force calculation using cross-product formulation
// คำนวณแรงยกแบบคลาสสิกโดยใช้สูตร cross-product
// F_lift = Cl * rho_continuous * V_particle * (U_continuous - U_particle) × vorticity
vectorClassicalLiftForce =
    Cl_ * rhoContinuous_ * particleVolume_ *
    (Ucontinuous_ - Uparticle_) ^ curl(Ucontinuous_);
```

<details>
<summary>📖 คำอธิบายเพิ่มเติม (Thai Explanation)</summary>

**ที่มาทางทฤษฎี (Theoretical Background):**
สมการนี้คือสูตรแรงยกแบบคลาสสิกที่อิงจาก Magnus effect โดยแรงยกจะเกิดขึ้นในทิศทางที่ตั้งฉากกับทั้งความเร็วสัมพัทธ์และความหมุนวนของการไหล

**แหล่งที่มา (Source):**
📂 `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C`

**แนวคิดสำคัญ (Key Concepts):**
- **Cross-product Operation**: รับประกันว่าแรงยกจะตั้งฉากกับระนาบของความเร็วสัมพัทธ์และความหมุนวน
- **Vorticity**: ความหมุนวนของการไหลแทนความไม่สมมาตรของสนามการไหล
- **Lift Coefficient (Cl)**: ค่าสัมประสิทธิ์แรงยกที่ขึ้นกับสภาวะการไหลและรูปทรงอนุภาค

</details>

```cpp
// Saffman lift force calculation for low Reynolds number shear flow
// คำนวณแรงยก Saffman สำหรับการไหลแบบเฉือนที่ Reynolds number ต่ำ
// F_Saffman = 6.46 * rho * sqrt(nu) * d² * |U_slip| * sqrt(shear_rate) * direction

// Calculate slip velocity magnitude
// คำนวณขนาดของความเร็วสัมพัทธ์
scalar slipVelocity = mag(Ucontinuous_ - Uparticle_);

// Calculate shear rate magnitude
// คำนวณขนาดของอัตราการเฉือน
scalar shearRate = mag(dUcdy_);

// Compute Saffman lift force with proper directional vector
// คำนวณแรงยก Saffman พร้อมเวกเตอร์ทิศทางที่ถูกต้อง
// The constant 6.46 = 2 * 1.615 * 2 for spherical particles
// ค่าคงที่ 6.46 ได้มาจาก 2 * 1.615 * 2 สำหรับอนุภาคทรงกลม
vectorSaffmanLiftForce =
    6.46 * rhoContinuous_ * sqrt(nuContinuous_) *
    sqr(diameter_) * slipVelocity * sqrt(shearRate) * nL_;
```

<details>
<summary>📖 คำอธิบายเพิ่มเติม (Thai Explanation)</summary>

**ที่มาทางทฤษฎี (Theoretical Background):**
สมการ Saffman ได้มาจากการวิเคราะห์เชิงทฤษฎีสำหรับทรงกลมในกระแสเฉือนเชิงเส้นที่ Reynolds number ต่ำ ค่าคงที่ 6.46 ได้มาจากการแก้สมการ Navier-Stokes แบบ asymptotic

**แหล่งที่มา (Source):**
📂 `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C`

**แนวคิดสำคัญ (Key Concepts):**
- **Asymptotic Matching**: การเชื่อมผลเฉลยภายในและภายนอกแบบ asymptotic
- **Viscous Effects**: แรงยกแปรผันตามรากที่สองของความหนืด (sqrt(ν))
- **Shear Rate Dependence**: แรงยกแปรผันตามรากที่สองของอัตราการเฉือน
- **Valid Range**: ใช้ได้เมื่อ Re_p << sqrt(Re_γ) หรือ S >> 1

</details>

---

## 8. ความสำคัญในการประยุกต์ใช้งาน

การสร้างแบบจำลองแรงยกที่แม่นยำเป็น **สิ่งจำเป็น** สำหรับ:

### กระบวนการทางอุตสาหกรรม
- **กระบวนการแยก (separation processes)**
- **กระบวนการผสม (mixing processes)**
- **ปรากฏการณ์การถ่ายโอน (transport phenomena)**

### การทำนายที่น่าเชื่อถือ
- การได้ผลการทำนายที่ถูกต้องในการจำลองการไหลแบบหลายเฟส
- โดยเฉพาะในการใช้งานทางวิศวกรรมที่ต้องการความแม่นยำสูง

**ข้อสรุป:** การทำความเข้าใจและการนำแบบจำลองแรงยกเหล่านี้ไปใช้อย่างถูกต้องเป็น **สิ่งสำคัญอย่างยิ่ง** ในการได้ผลการทำนายที่น่าเชื่อถือในการจำลองการไหลแบบหลายเฟส