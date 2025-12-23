# การหาปริมาณความไม่แน่นอน (Uncertainty Quantification - UQ)

## 1. บทนำ (Introduction)

การหาปริมาณความไม่แน่นอน (Uncertainty Quantification - UQ) ใน CFD คือกระบวนการวิเคราะห์เชิงระบบว่าความแปรปรวนของพารามิเตอร์ขาเข้า (Input Parameters) ส่งผลต่อผลลัพธ์ของการจำลองอย่างไร กระบวนการนี้มีความสำคัญอย่างยิ่งต่อการตัดสินใจทางวิศวกรรมและการประเมินความเสี่ยงเพื่อให้ได้ผลการพยากรณ์ที่เชื่อถือได้ (Reliable Predictions)

---

## 2. การวิเคราะห์ความไวของพารามิเตอร์ (Sensitivity Analysis)

### 2.1 ดัชนี Sobol (Sobol Indices)
ใช้เพื่อระบุว่าพารามิเตอร์ตัวใดมีอิทธิพลต่อความไม่แน่นอนของผลลัพธ์มากที่สุด โดยการแยกความแปรปรวนรวม (Total Variance):
$$\text{Var}(Y) = \sum_{i} V_i + \sum_{i<j} V_{ij} + \cdots + V_{12...k}$$

**ดัชนีที่สำคัญ:**
- **First-order Index ($S_i$)**: $V_i / \text{Var}(Y)$ แสดงถึงผลกระทบหลักของพารามิเตอร์ตัวเดียว
- **Total Index ($S_{Ti}$)**: รวมผลกระทบจากปฏิสัมพันธ์ (Interactions) ทั้งหมดของพารามิเตอร์นั้นกับตัวอื่น

**ตัวอย่างโค้ดสำหรับการวิเคราะห์ Sobol:**
```cpp
class sobolAnalysis {
public:
    void calculateSobolIndices() {
        // สร้างลำดับ Sobol และรันการจำลอง
        scalarField YA = runSimulations(samplesA);
        scalarField YB = runSimulations(samplesB);
        // คำนวณดัชนี Sobol ลำดับแรกและดัชนีรวม
        scalarField firstOrder = calculateFirstOrderIndex(YA, YB, YC);
        scalarField total = calculateTotalIndex(YA, YB, YC);
        Info << "Sensitivity: First-order = " << firstOrder << ", Total = " << total << endl;
    }
};
```

---

## 3. ระเบียบวิธีวิจัยสำหรับการแพร่กระจายความไม่แน่นอน

### 3.1 การวิเคราะห์ Monte Carlo (Monte Carlo Analysis)
เป็นวิธีที่ตรงไปตรงมาที่สุดในการสุ่มพารามิเตอร์ โดยความคลาดเคลื่อนจะลดลงตามสัดส่วน $1/\sqrt{N}$ ($N$ คือจำนวนตัวอย่าง)

**เทคนิคการเพิ่มความเร็ว:**
| เทคนิค | ประสิทธิภาพ | กรณีที่เหมาะสม |
|----------|-------------|------------------|
| **Latin Hypercube** | ดี | กรณีทั่วไป |
| **Importance Sampling** | ดีมาก | จุดที่มีความน่าจะเป็นสูง |
| **Quasi-Monte Carlo** | ดีมาก | ฟังก์ชันที่เรียบ (Smooth) |

### 3.2 Polynomial Chaos Expansion (PCE)
เป็นทางเลือกที่มีประสิทธิภาพสูงกว่า Monte Carlo โดยการใช้พหุนามตั้งฉาก (Orthogonal Polynomials) เพื่อประมาณพื้นผิวตอบสนอง (Response Surface):
$$Y(\mathbf{p}) = \sum_{\boldsymbol{\alpha} \in \mathcal{A}} c_{\boldsymbol{\alpha}} \Psi_{\boldsymbol{\alpha}}(\mathbf{p})$$

---

## 4. แหล่งที่มาของความไม่แน่นอน (Sources of Uncertainty)

1. **Model Form Uncertainty**: ความคลาดเคลื่อนจากการลดรูปฟิสิกส์ (เช่น โมเดล Drag, Turbulence)
2. **Numerical Uncertainty**: ความคลาดเคลื่อนจากการ Discretization ในระดับปริภูมิและเวลา
3. **Input Parameter Uncertainty**: ความแปรปรวนของคุณสมบัติทางกายภาพ (Density, Viscosity, Surface Tension)

---

## 5. เมตริกและเกณฑ์การยอมรับ (Acceptance Criteria)

- **NRMSE (Normalized Root Mean Square Error)**:
$$\text{NRMSE} = \frac{\sqrt{\frac{1}{N}\sum(y_i^{num} - y_i^{exp})^2}}{y_{max}^{exp} - y_{min}^{exp}}$$
- **Acceptance Rule**: การจำลองจะถือว่าผ่านการยืนยันหากค่า Error ($E$) อยู่ภายในช่วงความไม่แน่นอนของการยืนยัน ($U_{val}$):
$$|E| < U_{val}$$

---

## 6. ประสิทธิภาพเชิงคำนวณ (Computational Efficiency)

ในการทำ UQ ประสิทธิภาพการคำนวณเป็นเรื่องสำคัญเนื่องจากต้องรันหลายเคส:
$$\text{efficiency} = \frac{\text{error}}{\text{wall time}}$$

การใช้โมเดลตัวแทน (Surrogate Models) หรือการประมวลผลแบบขนาน (Parallel Computing) จะช่วยลดระยะเวลาในการวิเคราะห์ UQ ได้อย่างมาก

*อ้างอิง: มาตรฐาน ASME V&V 20 (2009) สำหรับการตรวจสอบความถูกต้องใน CFD และพลศาสตร์ความร้อน*
