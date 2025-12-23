# แนวคิดพื้นฐานของแรงยก (Fundamental Lift Concepts)

## 1. บทนำ (Introduction)

**แรงยก (Lift forces)** ในการไหลหลายเฟสคือแรงที่กระทำต่อเฟสกระจาย (อนุภาค, ฟองอากาศ, หยดของเหลว) ในทิศทาง **ตั้งฉาก (Perpendicular)** กับความเร็วสัมพัทธ์ระหว่างเฟส แรงนี้มีบทบาทสำคัญในการกำหนดการกระจายตัวของเฟสในแนวขวาง

---

## 2. กลไกทางกายภาพ (Physical Mechanisms)

สาเหตุหลักของแรงยกเกิดจากความไม่สมมาตรของสนามการไหลรอบๆ อนุภาค:

### 2.1 Shear-Induced Lift (Saffman Lift)
เกิดขึ้นเมื่ออนุภาคอยู่ในบริเวณที่มีความชันของความเร็ว (Velocity gradient) ความเร็วที่แตกต่างกันระหว่างสองด้านของอนุภาคทำให้เกิดความแตกต่างของความดัน (Bernoulli effect) และแรงเค้นหนืดที่ไม่สมมาตร ส่งผลให้เกิดแรงยกสุทธิ

### 2.2 Rotation-Induced Lift (Magnus Effect)
หากอนุภาคมีการหมุน (Rotation) ความเร็วที่ผิวของอนุภาคจะเสริมกับความเร็วของไหลในด้านหนึ่งและต้านในอีกด้านหนึ่ง สร้างการไหลวน (Circulation) และแรงยกตามทฤษฎีบท Kutta-Joukowski

### 2.3 Wall-Induced Lift
ใกล้ผนัง สนามการไหลจะบิดเบี้ยวเนื่องจากข้อจำกัดทางเรขาคณิต โดยทั่วไปจะสร้างแรงผลัก (Repulsion) ให้อนุภาคเคลื่อนที่ออกจากผนัง

---

## 3. การวิเคราะห์ทางคณิตศาสตร์ (Mathematical Derivation)

### 3.1 แรงยกแบบคลาสสิก (Classical Lift Force)
$$\mathbf{F}_L = C_L \rho_c V_p (\mathbf{u}_c - \mathbf{u}_p) \times (\nabla \times \mathbf{u}_c) \tag{1.1}$$ 

### 3.2 แรงยก Saffman (สำหรับ Reynolds ต่ำ)
$$\mathbf{F}_L = 1.615 \rho_c \nu_c^{1/2} d^2 (\mathbf{u}_c - \mathbf{u}_p) \left| \frac{\mathrm{d}u_c}{\mathrm{d}y} \right|^{1/2} \tag{1.2}$$ 

---

## 4. การวิเคราะห์แบบไร้มิติ (Dimensionless Analysis)

พารามิเตอร์ที่ใช้ระบุความสำคัญของแรงยก:

| พารามิเตอร์ | นิยาม | ความหมาย |
|-----------|-------|----------|
| **Particle Reynolds ($Re_p$)** | $\frac{\rho_c |\mathbf{u}_r| d}{\mu_c}$ | แรงเฉื่อยต่อแรงหนืดของอนุภาค |
| **Shear Reynolds ($Re_\gamma$)** | $\frac{\rho_c \gamma d^2}{\mu_c}$ | ความแรงของกระแสเฉือน |
| **Saffman Parameter ($S$)** | $\frac{Re_\gamma^{1/2}}{Re_p}$ | ระบุว่าแรงยกจากการเฉือนมีอิทธิพลมากเพียงใด |

---

## 5. การนำไปใช้ใน OpenFOAM

ใน OpenFOAM การคำนวณแรงยกมักใช้ความหมุนวน (Vorticity, $\boldsymbol{\omega} = \nabla \times \mathbf{u}_c$) เป็นตัวแทนของความไม่สมมาตร:

```cpp
// การคำนวณความหมุนวนใน OpenFOAM
volVectorField omega = fvc::curl(Uc);

// คำนวณแรงยกต่อหน่วยปริมาตร
volVectorField FLift = CL * rhoc * alphad * (Uc - Ud) ^ omega;
```

แรงนี้จะถูกรวมเข้าเป็นเทอมแหล่งกำเนิดในสมการโมเมนตัม เพื่อทำนายการเคลื่อนที่แนวขวางของเฟสกระจายได้อย่างแม่นยำ

```