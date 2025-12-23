# รายละเอียดการนำไปใช้ใน OpenFOAM (OpenFOAM Implementation)

## 1. ลำดับชั้นของคลาส (Lift Model Hierarchy) 

OpenFOAM จัดการแรงยกผ่านระบบคลาสที่มีความยืดหยุ่น โดยมีคลาสพื้นฐานคือ `liftModel` ซึ่งรองรับการเลือกใช้โมเดลต่างๆ ขณะรันโปรแกรม (Runtime Selection)

### โครงสร้างคลาสใน C++
```cpp
class liftModel
{
public:
    // คำนวณแรงยกต่อหน่วยปริมาตร
    virtual tmp<volVectorField> Fi() const = 0;

    // คำนวณสัมประสิทธิ์แรงยก
    virtual tmp<volScalarField> Cl() const = 0;
};
```

---

## 2. การคำนวณใน Solver (Numerical Workflow)

ใน Solver อย่าง `multiphaseEulerFoam`, ขั้นตอนการคำนวณแรงยกมีดังนี้:

### 2.1 การคำนวณความหมุนวน (Vorticity)
แรงยกอ้างอิงจากความไม่สมมาตรของสนามการไหล ซึ่งแทนด้วย Vorticity (\(\\boldsymbol{\\omega}\\)):
```cpp
volVectorField omega = fvc::curl(Uc);
```

### 2.2 การรวมแรงเข้ากับสมการโมเมนตัม
แรงยกต่อหน่วยปริมาตรคำนวณจากสัมประสิทธิ์ $C_L$:
$$\\mathbf{F}_L = C_L \\rho_c \\alpha_d (\\mathbf{u}_c - \\mathbf{u}_d) \\times \\boldsymbol{\\omega}$$

---

## 3. ข้อควรพิจารณาด้านเสถียรภาพ (Stability Considerations)

แรงยกอาจทำให้การคำนวณไม่เสถียรเนื่องจากใช้การคำนวณอนุพันธ์อันดับสอง (ผ่าน curl) OpenFOAM จึงมีเทคนิคควบคุมดังนี้:

### 3.1 Vorticity Smoothing
การทำให้สนาม Vorticity เรียบขึ้นเพื่อลดสัญญาณรบกวน (Noise):
$$\\boldsymbol{\\omega}_{smoothed} = \\boldsymbol{\\omega} + \\nu_{smooth} \\nabla^2 \\boldsymbol{\\omega}$$

### 3.2 Lift Coefficient Limiting
จำกัดค่า $C_L$ ไม่ให้สูงเกินไปจนทำให้ระบบระเบิด (Blow-up):
$$C_L^{limited} = \\min(\\|C_L\|, C_L^{max}) \\cdot \\text{sign}(C_L)$$
โดยทั่วไปค่า $C_L^{max}$ จะถูกตั้งไว้ที่ประมาณ 1.0

### 3.3 Under-Relaxation
ใช้การผ่อนคลายค่าแรงเพื่อให้ลู่เข้าได้ดีขึ้น:
$$\\mathbf{F}_L^{new} = (1-\\lambda_L)\\mathbf{F}_L^{old} + \\lambda_L \\mathbf{F}_L^{calculated}$$

---

## 4. การตั้งค่าใน `phaseProperties`

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

การนำไปใช้เหล่านี้ช่วยให้สามารถจำลองพฤติกรรมการเคลื่อนที่แนวขวางของเฟสกระจายได้อย่างแม่นยำ ภายใต้สภาวะการไหลที่ซับซ้อนในอุตสาหกรรม

