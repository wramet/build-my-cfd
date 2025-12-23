# ภาพรวมของโปรแกรมแก้สมการ (Solver Overview)

## 1. บทนำ (Introduction)

`multiphaseEulerFoam` เป็น Solver ขั้นสูงใน OpenFOAM ที่ออกแบบมาสำหรับการจำลองการไหลหลายเฟสแบบ Transient โดยใช้แนวทาง **Eulerian-Eulerian** (หรือเรียกว่า Multi-fluid model) ซึ่งแต่ละเฟสจะถูกพิจารณาว่าเป็นตัวกลางที่แทรกซึมซึ่งกันและกัน (Interpenetrating continua) และมีชุดสมการอนุรักษ์ (Conservation equations) แยกจากกันอย่างเด็ดขาด ทำให้สามารถจำลองปรากฏการณ์ทางฟิสิกส์ที่ซับซ้อนได้อย่างแม่นยำและเข้มงวดทางคณิตศาสตร์

---

## 2. ความสามารถหลัก (Core Capabilities)

`multiphaseEulerFoam` มีความสามารถในการแก้สมการสำหรับปรากฏการณ์ต่างๆ ดังนี้:

- **รองรับหลายเฟส (Multiple Phases)**: จัดการจำนวนเฟสได้ไม่จำกัด โดยแต่ละเฟส $k$ มีสนามความเร็ว $\mathbf{u}_k$, ความหนาแน่น $\rho_k$, อุณหภูมิ $T_k$, และสัดส่วนปริมาตร $\alpha_k$ เป็นของตัวเอง
- **การถ่ายโอนโมเมนตัมระหว่างเฟส (Inter-phase Momentum Transfer)**: รวมกลไกการแลกเปลี่ยนแรงที่ครอบคลุม เช่น แรงลาก (Drag, $\mathbf{F}_{drag}$), แรงยก (Lift, $\mathbf{F}_{lift}$), และแรงมวลเสมือน (Virtual mass, $\mathbf{F}_{vm}$)
- **การถ่ายโอนความร้อนและมวล (Heat & Mass Transfer)**: จำลองการแลกเปลี่ยนพลังงานและมวลระหว่างเฟส รวมถึงปรากฏการณ์การเปลี่ยนเฟส (Phase change) ผ่านอัตราการถ่ายโอนมวล $\dot{m}_{lk}$
- **การจำลองความปั่นป่วน (Turbulence Modeling)**: บูรณาการโมเดลความปั่นป่วนแบบหลายเฟสที่คำนึงถึงผลกระทบของเฟสกระจาย (Dispersed phase) ต่อการขนส่งความปั่นป่วน

### ประเภทระบบที่รองรับ (Supported Systems)

| ประเภทระบบ | คำอธิบาย | ตัวอย่างการประยุกต์ใช้ |
|---|---|---|
| **Gas-Liquid** | เฟสที่มีความหนาแน่นต่างกันมาก | Bubble columns, Aeration tanks |
| **Liquid-Liquid** | ของเหลวที่ไม่ผสมกัน (Immiscible) | Oil-water separation |
| **Solid-Fluid** | อนุภาคของแข็งในของไหล | Fluidized beds, Slurry flows |

---

## 3. สมการควบคุม (Governing Equations)

Solver นี้ใช้สมการอนุรักษ์ที่ได้จากการหาค่าเฉลี่ยตามปริมาตร (Volume-averaging) โดยแต่ละเฟส $k$ จะมีสัดส่วนปริมาตร $\alpha_k$ ในปริมาตรควบคุม (Control volume) ซึ่งต้องเป็นไปตามเงื่อนไข:
$$\sum_{k=1}^{N} \alpha_k = 1$$

### 3.1 การอนุรักษ์มวล (Mass Conservation)
สำหรับแต่ละเฟส $k$:
$$\frac{\partial (\alpha_k \rho_k)}{\partial t} + \nabla \cdot (\alpha_k \rho_k \mathbf{u}_k) = \sum_{l=1}^{N} \dot{m}_{lk}$$

**ตัวแปรหลัก:**
- $\alpha_k$: สัดส่วนปริมาตรของเฟส $k$ ($0 \leq \alpha_k \leq 1$)
- $\rho_k$: ความหนาแน่นของเฟส $k$ (kg/m³)
- $\mathbf{u}_k$: เวกเตอร์ความเร็วของเฟส $k$ (m/s)
- $\dot{m}_{lk}$: อัตราการถ่ายโอนมวลจากเฟส $l$ ไปยังเฟส $k$ (kg/m³·s) โดยมีเงื่อนไข $\sum_k \sum_l \dot{m}_{lk} = 0$

### 3.2 การอนุรักษ์โมเมนตัม (Momentum Conservation)
$$\frac{\partial (\alpha_k \rho_k \mathbf{u}_k)}{\partial t} + \nabla \cdot (\alpha_k \rho_k \mathbf{u}_k \mathbf{u}_k) = -\alpha_k \nabla p + \nabla \cdot \boldsymbol{\tau}_k + \alpha_k \rho_k \mathbf{g} + \mathbf{M}_k$$

**ตัวแปรหลัก:**
- $p$: สนามความดันร่วม (Shared pressure field)
- $\boldsymbol{\tau}_k$: เทนเซอร์ความเครียดหนืด (Viscous stress tensor): $\boldsymbol{\tau}_k = \mu_k (\nabla \mathbf{u}_k + \nabla \mathbf{u}_k^T) - \frac{2}{3}\mu_k (\nabla \cdot \mathbf{u}_k)\mathbf{I}$
- $\mathbf{g}$ เวกเตอร์ความเร่งจากแรงโน้มถ่วง (m/s²)
- $\mathbf{M}_k$ เทอมการถ่ายโอนโมเมนตัมระหว่างเฟสโดยรวม (N/m³):
$$\mathbf{M}_k = \sum_{l=1}^{N} K_{kl}(\mathbf{u}_l - \mathbf{u}_k) + \sum_{l=1}^{N} \mathbf{L}_{kl} + \sum_{l=1}^{N} \mathbf{V}_{vm,kl}$$
โดยที่ $K_{kl}$ คือสัมประสิทธิ์แรง Drag, $\mathbf{L}_{kl}$ คือแรง Lift และ $\mathbf{V}_{vm,kl}$ คือแรง Virtual Mass

### 3.3 การอนุรักษ์พลังงาน (Energy Conservation)
$$\frac{\partial (\alpha_k \rho_k E_k)}{\partial t} + \nabla \cdot (\alpha_k \rho_k H_k \mathbf{u}_k) = \nabla \cdot (k_k \nabla T_k) + Q_k$$

**ตัวแปรหลัก:**
- $E_k, H_k$: พลังงานรวมและเอนทาลปีรวมต่อหน่วยมวล (J/kg)
- $k_k$: ความนำความร้อน (W/m·K)
- $Q_k$: การถ่ายโอนความร้อนระหว่างเฟส ($\sum Q_k = 0$)

---

## 4. การนำไปใช้งานเชิงตัวเลข (Numerical Implementation)

`multiphaseEulerFoam` ใช้อัลกอริทึม **PIMPLE** (ผสมผสานระหว่าง PISO และ SIMPLE) เพื่อจัดการความเชื่อมโยงระหว่างความดันและความเร็ว (Pressure-velocity coupling)

### 4.1 ขั้นตอนของอัลกอริทึม PIMPLE
1. **Prediction**: ทำนายความเร็ว $\mathbf{u}_k^{*}$ และสัดส่วนปริมาตร $\alpha_k^{*}$
2. **Momentum Solve**: แก้สมการโมเมนตัมของแต่ละเฟส โดยพิจารณาเทอม Inter-phase coupling แบบ Implicit
3. **Pressure Correction**: สร้างและแก้สมการความดันร่วม (Shared pressure equation) และแก้ไขความเร็วให้สอดคล้องกับกฎการอนุรักษ์มวล
4. **Volume Fraction Correction**: แก้ไข $\alpha_k$ เพื่อให้ $\sum \alpha_k = 1$
5. **Energy & Other Equations**: แก้สมการพลังงาน ความปั่นป่วน และสมการการขนส่งอื่นๆ
6. **Iteration**: ทำซ้ำลูป PISO/SIMPLE จนกว่าจะลู่เข้า (Convergence)

### 4.2 โครงสร้างโค้ดใน OpenFOAM (C++ Implementation)
```cpp
while (pimple.loop())
{
    // 1. Momentum predictor (optional)
    if (pimple.momentumPredictor())
    {
        forAll(phases, phasei) { phases[phasei].UEqn().relax(); }
    }

    // 2. Momentum coupling & solve
    forAll(phases, phasei) { phases[phasei].UEqn().solve(); }

    // 3. Pressure equation
    {
        fvScalarMatrix pEqn(fvm::laplacian(rAUf, p) == fvc::div(phiHbyA));
        pEqn.solve();
    }

    // 4. Volume fraction & Energy correction
    forAll(phases, phasei)
    {
        phases[phasei].alphaCorrect();
        if (solveEnergy) phases[phasei].TEqn().solve();
    }
}
```

---

## 5. การประยุกต์ใช้งานและข้อดี (Applications & Advantages)

### ความเหมาะสมในการใช้งาน
- **Dense Dispersed Phases**: เหมาะสำหรับระบบที่มีเฟสกระจายตัวหนาแน่น ($\alpha_d > 10\%$) ซึ่งวิธี Lagrangian จะใช้ทรัพยากรสูงเกินไป
- **Large Scale Simulations**: มีประสิทธิภาพสูงในการจำลองระบบขนาดใหญ่ เช่น อุตสาหกรรมเคมีและนิวเคลียร์

### ข้อดีเมื่อเทียบกับแนวทาง Lagrangian
1. **Computational Efficiency**: ประสิทธิภาพสูงกว่าเมื่อมีจำนวนอนุภาค/ฟองอากาศมหาศาล
2. **Natural Coupling**: การเชื่อมต่อระหว่างเฟสถูกฝังอยู่ในโครงสร้างสมการอย่างเป็นระบบ
3. **Scalability**: รองรับการคำนวณแบบขนาน (Parallel computing) ได้ดีเยี่ยม

*อ้างอิง: การวิเคราะห์ตามซอร์สโค้ด OpenFOAM multiphaseEulerFoam และเอกสารประกอบเชิงทฤษฎี*
