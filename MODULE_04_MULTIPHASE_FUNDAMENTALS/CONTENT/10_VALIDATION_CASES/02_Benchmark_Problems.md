# ปัญหาเบนช์มาร์กสำหรับการตรวจสอบความถูกต้อง (Benchmark Problems)

## 1. บทนำ (Introduction)

ปัญหาเบนช์มาร์ก (Benchmark Problems) คือกรณีทดสอบมาตรฐานที่ใช้สำหรับประเมินความแม่นยำและความน่าเชื่อถือของ Solver ในการไหลหลายเฟส โดยจะเริ่มตั้งแต่ระดับ **ฟิสิกส์พื้นฐาน** ไปจนถึง **ระบบที่ซับซ้อนในอุตสาหกรรม** เพื่อเป็นกรอบการตรวจสอบความถูกต้องอย่างเป็นระบบสำหรับ `multiphaseEulerFoam`

---

## 2. การลอยตัวของฟองเดี่ยว (Single Bubble Rising)

เบนช์มาร์กนี้ใช้ทดสอบโมเดลแรงตึงผิว (Surface Tension), แรง Drag และแรง Lift ในระบบแก๊ส-ของเหลว

### 2.1 พารามิเตอร์ไร้มิติที่สำคัญ
พลศาสตร์ของฟองถูกควบคุมโดยพารามิเตอร์หลัก 3 ตัว:
- **Eötvös Number (Eo)**: อัตราส่วนระหว่างแรงลอยตัวต่อแรงตึงผิว
  $$Eo = \frac{g(\rho_l - \rho_g)d_b^2}{\sigma}$$
- **Bubble Reynolds Number (Re_b)**: อัตราส่วนระหว่างแรงเฉื่อยต่อแรงหนืด
  $$Re_b = \frac{\rho_l u_t d_b}{\mu_l}$$
- **Morton Number (Mo)**: ระบุคุณสมบัติของของไหลโดยไม่ขึ้นกับขนาดฟอง
  $$Mo = \frac{g\mu_l^4(\rho_l - \rho_g)}{\rho_l^2 \sigma^3}$$

### 2.2 การนำไปใช้งานใน OpenFOAM
```cpp
// กำหนดค่าเริ่มต้นฟองทรงกลม (Spherical Bubble)
const Vector<double> bubbleCenter(0.05, 0.05, 0.05);
const scalar bubbleRadius = 0.005; // 5 mm
forAll(alphaGas, celli) {
    const Vector<double>& cellCenter = mesh.C()[celli];
    scalar r = mag(cellCenter - bubbleCenter);
    // Smooth initialization โดยใช้ tanh
    alphaGas[celli] = 0.5 * (1 - tanh((r - bubbleRadius) / (0.5 * pow(mesh.V()[celli], 1.0/3.0))));
}
```

---

## 3. การไหลแบบแยกชั้น (Stratified Two-Phase Flow)

ใช้ทดสอบความสามารถในการจับภาพการแยกเฟสที่ขับเคลื่อนโดยแรงโน้มถ่วงและการแลกเปลี่ยนโมเมนตัมที่อินเตอร์เฟซในท่อแนวนอน

### 3.1 พารามิเตอร์ที่สำคัญ
- **Froude Number (Fr)**: $Fr = U_g / \sqrt{gD}$
- **Lockhart-Martinelli Parameter (X)**: อัตราส่วนการไล่ระดับความดันของแต่ละเฟส
  $$X = \sqrt{\frac{(dP/dx)_l}{(dP/dx)_g}}$$

### 3.2 โมเดลที่ใช้ตรวจสอบ
- **Taitel-Dukler Model**: ใช้พยากรณ์ความสูงของของเหลวสมดุล ($h_l/D$)
- **Pressure Drop**: พยากรณ์โดยใช้ Gas phase multiplier ($\Phi_g$)

---

## 4. การจำลองเตียงไหลฟลูอิดไดซ์ (Fluidized Bed)

เบนช์มาร์กที่ซับซ้อนสำหรับระบบแก๊ส-ของแข็ง ทดสอบแรง Drag และปฏิสัมพันธ์ระหว่างอนุภาค

### 4.1 ฟิสิกส์พื้นฐาน
- **Ergun Equation**: สำหรับการลดลงของความดันใน Fixed bed ก่อนการลอยตัว
  $$\frac{\Delta P}{L} = \frac{150(1-\alpha_{mf})^2\mu_g U_{mf}}{\alpha_{mf}^3 d_p^2} + \frac{1.75(1-\alpha_{mf})\rho_g U_{mf}^2}{\alpha_{mf}^3 d_p}$$
- **Minimum Fluidization ($U_{mf}$)**: จุดที่แรง Drag ขึ้นสมดุลกับน้ำหนักสุทธิของอนุภาค
  $$\Delta P = (\rho_s - \rho_g)(1-\alpha_{mf})gL$$

### 4.2 การวัดประสิทธิภาพ (Validation Metrics)
```cpp
void calculateFluidizationMetrics() {
    scalar expansionRatio = calculateBedHeight(alpha_solid) / initialBedHeight;
    scalar deltaP = inletPressure - outletPressure;
    // เปรียบเทียบกับค่าตามทฤษฎี
    scalar theoreticalDeltaP = (rho_solid - rho_gas) * (1 - alpha_mf) * 9.81 * finalBedHeight;
    Info << "Pressure drop error: " << mag(deltaP - theoreticalDeltaP)/theoreticalDeltaP * 100 << "%" << endl;
}
```

---

## 5. ความไม่เสถียรแบบ Rayleigh-Taylor (Rayleigh-Taylor Instability)

ใช้ทดสอบการผสมกันของของไหลต่างความหนาแน่นภายใต้แรงโน้มถ่วง (ของหนักอยู่บนของเบา)
- **Atwood Number (A)**: $A = (\rho_2 - \rho_1)/(\rho_2 + \rho_1)$
- **Linear Growth Rate ($\omega$)**: $\omega = \sqrt{A g k - \sigma k^3/\rho_m}$

---

## 6. เกณฑ์การยอมรับ (Acceptance Criteria)

| ระดับ (Level) | ตัวชี้วัด (Metric) | เกณฑ์การยอมรับ |
|-------|------|---------------------|
| **Code Verification** | Mass/Energy Balance | $< 10^{-10}$ |
| **Solution Verification** | GCI (Global) | $< 5\%$ |
| **Model Validation** | NRMSE (Engineering) | $< 15\%$ |
| **Model Validation** | R² (Sim vs Exp) | $> 0.8$ |

การตรวจสอบผ่านปัญหาเบนช์มาร์กเหล่านี้ช่วยสร้างความมั่นใจว่า Solver และ Closure models ที่เลือกใช้นั้นทำงานได้อย่างถูกต้องและเชื่อถือได้สำหรับการออกแบบทางวิศวกรรม

*อ้างอิง: วิเคราะห์ตามผลการทดลองของ Grace et al. (1976) และทฤษฎี Taitel-Dukler สำหรับการไหลหลายเฟส*
