# แบบจำลองแรงยกเฉพาะ (Specific Lift Models)

## 1. บทนำ (Introduction)

โมเดลแรงยกทำหน้าที่กำหนดค่าสัมประสิทธิ์แรงยก ($C_L$) ในสมการโมเมนตัม การเลือกโมเดลที่เหมาะสมขึ้นอยู่กับระบอบการไหล (เลขเรย์โนลด์) และความสามารถในการเสียรูปของอนุภาคหรือฟองอากาศ

---

## 2. โมเดลสำหรับอนุภาคแข็ง (Rigid Particles)

### 2.1 Saffman-Mei Model
พัฒนาขึ้นจากทฤษฎีของ Saffman โดยปรับปรุงให้ใช้ได้กับเลขเรย์โนลด์ที่สูงขึ้น ($Re_p < 1000$):

$$C_L = \begin{cases}
\frac{2.255}{\sqrt{Re_p S}} \left(1 - 0.15 Re_p^{0.687}\right) & Re_p < 40 \\
\frac{1}{\sqrt{Re_p S}} \left(0.5 + 0.2 Re_p\right) & 40 \leq Re_p \leq 1000
\end{cases} \tag{2.1}
$$

โดยที่ $S$ คือ Shear Rate Parameter

---

## 3. โมเดลสำหรับฟองอากาศ (Deformable Bubbles)

ในระบบ Gas-Liquid ฟองอากาศขนาดใหญ่จะเสียรูป ซึ่งส่งผลให้ทิศทางของแรงยกเปลี่ยนไป

### 3.1 Tomiyama Lift Model
เป็นโมเดลที่นิยมใช้ที่สุดสำหรับฟองอากาศ โดยพิจารณา **Eötvös Number ($Eo$)**:

$$C_L = \begin{cases}
\min\[0.288 \tanh(0.121 Re_p), f(Eo)\] & Eo \leq 4 \\
f(Eo) & 4 < Eo \leq 10 \\
-0.27 & Eo > 10
\end{cases} \tag{2.2}
$$

**ฟังก์ชันวิกฤต:** $f(Eo) = 0.00105 Eo^3 - 0.1159 Eo^2 + 0.426 Eo - 0.2303$

**พฤติกรรมทางกายภาพ:**
- **$Eo < 10$:** ฟองขนาดเล็ก แรงยกเป็นบวก (เคลื่อนที่เข้าหาผนัง)
- **$Eo > 10$:** ฟองขนาดใหญ่ แรงยกเป็นลบ (เคลื่อนที่เข้าสู่ศูนย์กลางท่อ)

---

## 4. ผลกระทบจากผนัง (Wall-Induced Lift)

เมื่ออนุภาคอยู่ใกล้ผนังแข็ง แรงยกจะถูกปรับปรุงเพื่อพิจารณาแรงผลักจากผนัง (Repulsion):

$$C_L^{wall} = C_L^{\infty} \cdot f\left(\frac{y_w}{d}\right) \tag{2.3}
$$

โดยที่ $f(y_w/d) = 1 - \exp(-\beta y_w/d)$ คือฟังก์ชันหน่วง (Damping function) เพื่อลดแรงยกเมื่อใกล้ผนัง

---

## 5. การนำไปใช้ใน OpenFOAM (C++ Implementation)

```cpp
// Tomiyama lift coefficient calculation in OpenFOAM
scalar f_Eo = 0.00105*pow(Eo, 3) - 0.1159*pow(Eo, 2) + 0.426*Eo - 0.2303;

if (Eo <= 4)
{
    Cl = min(0.288*tanh(0.121*Re), f_Eo);
}
else if (Eo <= 10)
{
    Cl = f_Eo;
}
else
{
    Cl = -0.27; // Negative lift for large bubbles
}
```

การเลือกโมเดลแรงยกที่ถูกต้องมีความสำคัญอย่างยิ่งในการทำนายรูปแบบการไหล เช่น การทำนายการรวมกลุ่มของฟองอากาศ (Bubble clustering) ในเครื่องปฏิกรณ์เคมี

