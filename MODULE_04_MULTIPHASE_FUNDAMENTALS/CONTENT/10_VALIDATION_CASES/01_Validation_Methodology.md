# ระเบียบวิธีวิจัยสำหรับการตรวจสอบความถูกต้อง (Validation Methodology)

## 1. บทนำ (Introduction)

**การตรวจสอบความถูกต้อง (Validation)** คือกระบวนการที่เป็นระบบเพื่อให้แน่ใจว่าแบบจำลองทางคอมพิวเตอร์สามารถแทนปรากฏการณ์ทางฟิสิกส์ในโลกแห่งความเป็นจริงได้อย่างแม่นยำ สำหรับการไหลหลายเฟสแบบ Eulerian-Eulerian การตรวจสอบความถูกต้องช่วยสร้างความเชื่อมั่นในผลการพยากรณ์ของ CFD ผ่านการเปรียบเทียบอย่างเข้มงวดกับผลเฉลยเชิงวิเคราะห์ (Analytical solutions), ข้อมูลการทดลอง (Experimental data) และปัญหาเบนช์มาร์ก (Benchmark problems)

---

## 2. ลำดับชั้นของการตรวจสอบความถูกต้อง (Validation Hierarchy)

กระบวนการตรวจสอบความถูกต้องจะดำเนินการตามลำดับขั้นจากพื้นฐานไปสู่ระบบที่ซับซ้อน:

### 2.1 การตรวจสอบโค้ด (Code Verification - คณิตศาสตร์ถูกต้องหรือไม่?)
เพื่อให้แน่ใจว่าการเขียนโปรแกรมและอัลกอริทึมแก้สมการคณิตศาสตร์ได้อย่างถูกต้อง:

- **Method of Manufactured Solutions (MMS)**: การกำหนดผลเฉลยเชิงวิเคราะห์และคำนวณเทอมแหล่งกำเนิด (Source terms) เพื่อทดสอบ Solver
  - **Continuity**: $\frac{\partial \alpha_k}{\partial t} + \nabla \cdot (\alpha_k \mathbf{u}_k) = S_{\alpha_k}^{\text{manufactured}}$
  - **Momentum**: $\rho_k \alpha_k \frac{\partial \mathbf{u}_k}{\partial t} + \rho_k \alpha_k (\mathbf{u}_k \cdot \nabla)\mathbf{u}_k = -\alpha_k \nabla p + \mathbf{M}_k^{\text{manufactured}}$

- **Grid Convergence Studies**: ประเมินความแม่นยำของการ Discretization ผ่าน **Grid Convergence Index (GCI)**:
$$\text{GCI} = F_s \frac{|\epsilon_{12}|}{r^p - 1}$$
โดย $F_s$ คือปัจจัยความปลอดภัย (มักใช้ 1.25), $\epsilon_{12}$ คือ Error สัมพัทธ์ระหว่างเมช, $r$ คืออัตราส่วนการละเอียดของเมช และ $p$ คืออันดับความแม่นยำที่สังเกตได้ (Observed order of accuracy)

- **Conservation Checks**: ตรวจสอบการอนุรักษ์มวลและพลังงานในระดับ Global:
  - **Mass**: $\sum_{k} \frac{\partial}{\partial t} \int_V \rho_k \alpha_k \, \mathrm{d}V = 0$

**ตัวอย่างโค้ด OpenFOAM สำหรับตรวจสอบ Mass Balance:**
```cpp
forAll(phases, phasei)
{
    const volScalarField& alpha = phases[phasei];
    const volVectorField& U = phases[phasei].U();
    scalar massIn = fvc::domainIntegrate(alpha*U & mesh.Sf()).value();
    Info << "Phase " << phases[phasei].name() << " mass balance error: " << massIn << " kg/s" << endl;
}
```

---

### 2.2 การตรวจสอบความถูกต้องของโมเดล (Model Validation - ฟิสิกส์ถูกต้องหรือไม่?)
ประเมินว่าโมเดลทางคณิตศาสตร์แทนปรากฏการณ์ทางฟิสิกส์ได้ถูกต้องเพียงใด:

- **Fundamental Physics**: เปรียบเทียบความเร็วลอยตัวของฟองเดี่ยว (Single bubble rise velocity) กับสูตรสหสัมพันธ์:
$$v_t = \sqrt{\frac{4g d_b (\rho_l - \rho_g)}{3C_d \rho_l}}$$

- **Simplified Systems**: ทดสอบกับระบบที่ควบคุมสภาวะได้ง่าย เช่น Bubble columns หรือการไหลในท่อ (Pipe flows) เพื่อวัดค่า Pressure drop ($\Delta P$) และสัดส่วนปริมาตรแก๊ส ($\alpha_g$)

- **Industrial Applications**: ทดสอบกับระบบจริง เช่น Fluidized beds เพื่อวัดอัตราการขยายตัวของชั้นอนุภาค (Bed expansion ratio) หรืออัตราการเกิดปฏิกิริยาเคมี

---

### 2.3 การประเมินความสามารถในการพยากรณ์ (Predictive Capability Assessment)
ประเมินประสิทธิภาพของแบบจำลองในสภาวะที่ไม่ได้ใช้ในการปรับแต่ง (Calibration) โมเดล:

- **Blind Predictions**: การทำนายผลโดยที่ผู้คำนวณไม่ทราบผลการทดลองล่วงหน้า เพื่อความโปร่งใสสูงสุด
- **Error Analysis**: การวิเคราะห์ความคลาดเคลื่อนทางสถิติ:
  - **RMSE**: $\sqrt{\frac{1}{N}\sum(y_i^{pred} - y_i^{exp})^2}$
  - **MAPE**: $\frac{100\%}{N}\sum\left|\frac{y_i^{pred} - y_i^{exp}}{y_i^{exp}}\right|$
  - **R²**: สัมประสิทธิ์การตัดสินใจ เพื่อดูความสัมพันธ์ระหว่างผลจำลองและผลทดลอง

---

## 3. การหาปริมาณความไม่แน่นอน (Uncertainty Quantification)

ใช้ประเมินความน่าเชื่อถือของแบบจำลองเมื่อปัจจัยนำเข้ามีความแปรปรวน:
- **Input Uncertainty**: การส่งผ่านความคลาดเคลื่อนจากข้อมูลดิบ ($\sigma_{output}^2 = \sum (\partial f / \partial x_i)^2 \sigma_{x_i}^2$)
- **Sensitivity Analysis**: ใช้ **Sobol Indices** เพื่อระบุว่าพารามิเตอร์ใดส่งผลต่อความแม่นยำมากที่สุด

**ตัวอย่างโครงสร้างโค้ด Monte Carlo Analysis:**
```cpp
class monteCarloAnalysis {
public:
    void runAnalysis() {
        for (int i = 0; i < nSamples; i++) {
            scalarField randomParams = generateRandomParameters();
            results[i] = runSingleSimulation(randomParams);
        }
        scalar meanResult = average(results);
        scalar confidenceInterval = 1.96 * stdDeviation(results) / sqrt(nSamples);
        Info << "95% CI: [" << meanResult - confidenceInterval << ", " << meanResult + confidenceInterval << "]" << endl;
    }
};
```

---

## 4. รายการตรวจสอบคุณภาพ (Quality Assurance Checklist)

เพื่อให้งานตรวจสอบความถูกต้องมีคุณภาพระดับมาตรฐาน:
1. **Mesh Quality**: Non-orthogonality < 70°, Skewness < 4, Aspect ratio < 1000
2. **Temporal Resolution**: เลข Courant (CFL) < 1.0 สำหรับอัลกอริทึม PISO
3. **Convergence**: ส่วนที่เหลือ (Residuals) ลดลงอย่างน้อย 6 อันดับ (Residual reduction < $10^{-6}$)
4. **Conservation**: ความไม่สมดุลของมวลและพลังงานรวมต้องน้อยกว่า 1%

ระเบียบวิธีวิจัยที่เข้มงวดนี้จะช่วยให้การใช้งาน `multiphaseEulerFoam` ใน OpenFOAM เป็นไปอย่างมีประสิทธิภาพและให้ผลลัพธ์ที่นำไปใช้งานต่อในทางวิศวกรรมได้อย่างปลอดภัย

*อ้างอิง: วิเคราะห์ตามมาตรฐาน ASME V&V 20 และระเบียบวิธีสากลสำหรับการตรวจสอบความถูกต้องของ CFD ในระบบหลายเฟส*
