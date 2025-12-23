# สถาปัตยกรรมและการนำไปใช้งาน (Implementation Architecture)

## 1. บทนำ (Introduction)

`multiphaseEulerFoam` เป็น Solver การไหลหลายเฟสแบบออยเลอร์ (Eulerian) ที่ซับซ้อนที่สุดใน OpenFOAM ออกแบบมาเพื่อจำลองระบบที่มีเฟสของไหลกี่เฟสก็ได้ ($N$ phases) ที่ใช้สนามความดันร่วมกัน (Shared Pressure Field) ในขณะที่แต่ละเฟสยังคงรักษาคุณสมบัติทางกายภาพและเทอร์โมไดนามิกส์ที่แยกออกจากกันอย่างเด็ดขาด

Solver นี้เป็นตัวอย่างที่ยอดเยี่ยมของ **สถาปัตยกรรม C++ แบบ Template** ขั้นสูง ซึ่งรองรับการเลือกโมเดลฟิสิกส์ในขณะรันไทม์ (Run-time selectable physics models) เพื่อความยืดหยุ่นสูงสุดในการใช้งาน

---

## 2. รากฐานทางคณิตศาสตร์ (Mathematical Foundation)

Solver นี้ใช้แนวทาง **Eulerian-Eulerian** โดยแต่ละเฟส $k$ ถูกพิจารณาว่าเป็นคอนตินิวอัม (Continuum) ที่แทรกซึมกัน และมีชุดสมการอนุรักษ์ของตัวเอง:

### 2.1 สมการความต่อเนื่อง (Continuity Equation)
สำหรับแต่ละเฟส $k$:
$$\frac{\partial (\alpha_k \rho_k)}{\partial t} + \nabla \cdot (\alpha_k \rho_k \mathbf{u}_k) = \sum_{l \neq k} \dot{m}_{lk}$$ 

โดยที่:
- $\alpha_k$: สัดส่วนปริมาตรของเฟส (Volume fraction) โดยมีเงื่อนไข $\sum_k \alpha_k = 1$
- $\rho_k$: ความหนาแน่นของเฟส (Phase density)
- $\mathbf{u}_k$: เวกเตอร์ความเร็วของเฟส (Phase velocity vector)
- $\dot{m}_{lk}$: อัตราการถ่ายโอนมวลจากเฟส $l$ ไปยังเฟส $k$ (Mass transfer rate)

### 2.2 สมการโมเมนตัม (Momentum Equation)
สำหรับแต่ละเฟสที่เคลื่อนที่ $k$:
$$\frac{\partial (\alpha_k \rho_k \mathbf{u}_k)}{\partial t} + \nabla \cdot (\alpha_k \rho_k \mathbf{u}_k \mathbf{u}_k) = -\alpha_k \nabla p + \nabla \cdot (\alpha_k \boldsymbol{\tau}_k) + \alpha_k \rho_k \mathbf{g} + \sum_{l \neq k} \mathbf{M}_{lk} + \mathbf{F}_{\sigma,k}$$ 

โดยที่:
- $p$: สนามความดันร่วม (Shared pressure field)
- $\boldsymbol{\tau}_k$: เทนเซอร์ความเครียดของเฟส (Phase stress tensor): $\boldsymbol{\tau}_k = \mu_k (\nabla \mathbf{u}_k + \nabla \mathbf{u}_k^T) - \frac{2}{3}\mu_k (\nabla \cdot \mathbf{u}_k)\mathbf{I}$
- $\mathbf{M}_{lk}$: การถ่ายโอนโมเมนตัมระหว่างอินเตอร์เฟซ (Interfacial momentum transfer) จากเฟส $l$ ไปยังเฟส $k$
- $\mathbf{F}_{\sigma,k}$: แรงตึงผิว (Surface tension force)

### 2.3 สมการพลังงาน (Energy Equation)
$$\frac{\partial (\alpha_k \rho_k h_k)}{\partial t} + \nabla \cdot (\alpha_k \rho_k \mathbf{u}_k h_k) = \alpha_k \frac{\mathrm{d}p}{\mathrm{d}t} + \nabla \cdot (\alpha_k k_k \nabla T_k) + \sum_{l \neq k} Q_{lk} + \sum_{l \neq k} \dot{m}_{lk} h_{sat}$$ 

โดยที่:
- $h_k$: เอนทาลปีจำเพาะของเฟส (Specific phase enthalpy)
- $k_k$: สัมประสิทธิ์การนำความร้อนของเฟส (Phase thermal conductivity)
- $Q_{lk}$: การถ่ายโอนความร้อนสัมผัส (Sensible heat transfer) จากเฟส $l$ ไปยังเฟส $k$
- $h_{sat}$: เอนทาลปีอิ่มตัว (Saturation enthalpy) สำหรับการเปลี่ยนเฟส

---

## 3. สถาปัตยกรรมหลัก (Core Architecture)

### 3.1 ลำดับชั้นของระบบเฟส (Phase System Hierarchy)
OpenFOAM ใช้การจัดการเฟสแบบลำดับชั้นเพื่อให้รองรับฟิสิกส์ที่หลากหลาย:

```cpp
#include "phaseSystem.H"                          // การจัดการเฟสหลัก
#include "phaseCompressibleMomentumTransportModel.H"  // ความปั่นป่วนเฉพาะเฟส
```

- **`phaseSystem.H`**: กำหนดโครงสร้างพื้นฐาน เช่น `momentumTransferTable`, `heatTransferTable` และ `specieTransferTable`
- **`phaseModel`**: คลาสที่เก็บข้อมูลสถานะของหนึ่งเฟส เช่น `U`, `alpha`, `rho`, `T`
- **`PtrListDictionary<phaseModel>`**: ใช้สำหรับเข้าถึงเฟสต่างๆ อย่างเป็นระบบ

### 3.2 รูปแบบการออกแบบแบบเทมเพลต (Template Design Patterns)
สถาปัตยกรรมนี้ใช้ C++ Templates อย่างกว้างขวางเพื่อความยืดหยุ่นในรันไทม์:
- **Phase Model Templates**: รองรับทั้ง `isochoric` (อัดตัวไม่ได้), `perfectGas`, และ `realGas` (อัดตัวได้)
- **Transfer System Templates**: 
  - `HeatTransferPhaseSystem`: การเชื่อมต่อความร้อนและ Latent heat
  - `MomentumTransferPhaseSystem`: จัดการ Drag, Lift, Virtual Mass, และ Turbulent Dispersion
  - `MassTransferPhaseSystem`: จัดการการระเหย (Evaporation) และการควบแน่น (Condensation)

---

## 4. อัลกอริทึมของ Solver (Solver Algorithm)

### 4.1 วงจรอัลกอริทึม PIMPLE
ใช้การเชื่อมต่อความดัน-ความเร็วแบบไฮบริด (Hybrid Pressure-Velocity Coupling) ซึ่งรวมเอาข้อดีของ SIMPLE (สำหรับ Steady-state) และ PISO (สำหรับ Transient) เข้าด้วยกัน:

```cpp
while (pimple.loop())  // วงจรแก้ไข PIMPLE
{
    if (!pimple.flow())
    {
        // แก้ไขคุณสมบัติทางความร้อนเท่านั้น
        if (pimple.thermophysics()) {
            fluid.solve(rAUs, rAUfs);
            fluid.correct();
            fluid.correctContinuityError();
            #include "YEqns.H"    // การขนส่งชนิด (Species transport)
            #include "EEqns.H"    // สมการพลังงาน
            #include "pEqnComps.H" // ความดันอัดตัวได้
        }
    }
    else
    {
        // การแก้ไขการไหลแบบเต็มที่มีการเชื่อมต่อโมเมนตัม
        if (faceMomentum) {
            #include "pUf/UEqns.H"  // โมเมนตัมแบบใบหน้า (Face-based)
            #include "pUf/pEqn.H"   // ความดันแบบใบหน้า
        } else {
            #include "pU/UEqns.H"   // โมเมนตัมแบบเซลล์ (Cell-based)
            #include "pU/pEqn.H"    // ความดันแบบเซลล์
        }
    }
}
```

---

## 5. การ Discretize สมการโมเมนตัม

### 5.1 Face-based vs Cell-based Momentum
- **Face-based Momentum (`pUf`)**: ให้ความเสถียรสูงกว่าในกรณีที่เลข Courant สูง และมีการอนุรักษ์มวล (Mass conservation) ที่ดีกว่า
- **Cell-based Momentum (`pU`)**: เป็นแนวทางปริมาตรจำกัดแบบดั้งเดิม มีประสิทธิภาพในการคำนวณสูงกว่าและตั้งค่าเงื่อนไขขอบเขตได้ง่ายกว่า

### 5.2 การถ่ายโอนโมเมนตัมระหว่างอินเตอร์เฟซ (Interfacial Transfer)
- **Drag Force**: $\mathbf{M}_{drag,kl} = K_{drag,kl} (\mathbf{u}_l - \mathbf{u}_k)$
- **Lift Force**: $\mathbf{M}_{lift,kl} = C_{lift} \rho_k \alpha_k (\mathbf{u}_k - \mathbf{u}_l) \times (\nabla \times \mathbf{u}_k)$
- **Virtual Mass Force**: $\mathbf{M}_{vm,kl} = C_{vm} \rho_k \alpha_l \left(\frac{\mathrm{d}\mathbf{u}_k}{\mathrm{d}t} - \frac{\mathrm{d}\mathbf{u}_l}{\mathrm{d}t}\right)$
- **Turbulent Dispersion**: $\mathbf{M}_{td,kl} = C_{td} \rho_k \nabla \cdot (\mu_{t,k} \nabla \alpha_k)$

---

## 6. คุณสมบัติทางตัวเลขขั้นสูง (Advanced Numerical Features)

### 6.1 Partial Elimination Algorithm (PEA)
ใช้เพื่อเพิ่มความเสถียรในการคำนวณกรณีที่มีแรง Drag สูง (High density ratio) โดยการกำจัดเทอม Drag ออกจากสมการความดันผ่านการจัดการพีชคณิต ช่วยให้การลู่เข้า (Convergence) ดีขึ้นอย่างมาก

### 6.2 Local Time Stepping (LTS)
ใช้สำหรับการเร่งการคำนวณเข้าสู่สถานะคงที่ (Steady-state acceleration) โดยการก้าวเวลาที่แตกต่างกันในแต่ละพื้นที่ของเมช

---

## 7. การกำหนดค่าใช้งาน (Implementation Configuration)

### 7.1 ตัวอย่างไฟล์ `constant/phaseProperties`
```openfoam
phases (water air);

water
{
    phaseModel      incompressible;
    equationOfState isochoric;
    thermo          hConst;
    transport       const;
}

air
{
    phaseModel      compressible;
    equationOfState perfectGas;
    thermo          hConst;
    transport       const;
}

phaseSystem
{
    type            momentumTransferPhaseSystem;
    interfacialModels
    {
        drag
        {
            type        SchillerNaumann;
            blended     true;
        }
    }
}
```

### 7.2 ตัวอย่างไฟล์ `system/fvSolution`
```openfoam
PIMPLE
{
    nCorrectors     2;
    nAlphaCorr      1;
    faceMomentum    yes;
    partialElimination yes;
}
```

สถาปัตยกรรมของ `multiphaseEulerFoam` นี้ช่วยให้ผู้ใช้สามารถจำลองปรากฏการณ์ที่ซับซ้อน เช่น เครื่องปฏิกรณ์คอลัมน์ฟอง (Bubble column reactors) หรือการวิเคราะห์ความปลอดภัยในเครื่องปฏิกรณ์นิวเคลียร์ ได้อย่างมีประสิทธิภาพและแม่นยำ

*อ้างอิง: วิเคราะห์ตามซอร์สโค้ด OpenFOAM multiphaseEulerFoam, phaseSystem.H และ HeatTransferPhaseSystem.H*
