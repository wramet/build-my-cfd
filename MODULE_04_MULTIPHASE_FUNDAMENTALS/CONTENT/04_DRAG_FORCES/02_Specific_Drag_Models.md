# แบบจำลองแรงฉุดเฉพาะ (Specific Drag Models)

## 1. บทนำ (Introduction)

**Drag models** คือความสัมพันธ์เชิงประจักษ์ (empirical correlations) ที่ใช้คำนวณสัมประสิทธิ์แรงฉุด $C_D$ เพื่อทำนายการแลกเปลี่ยนโมเมนตัมระหว่างเฟส การเลือกโมเดลที่ถูกต้องขึ้นอยู่กับชนิดของอนุภาค เลขเรย์โนลด์ ($Re_p$) และความเข้มข้นของเฟสกระจาย ($\alpha_d$)

---

## 2. แบบจำลองสำหรับอนุภาคทรงกลม (Spherical Particles)

### 2.1 Schiller-Naumann Model
เป็นโมเดลที่นิยมใช้มากที่สุดใน OpenFOAM ครอบคลุมทั้งระบอบการไหลแบบ Laminar และ Turbulent:

$$C_D = \begin{cases}
\frac{24}{Re_p}(1 + 0.15 Re_p^{0.687}) & Re_p < 1000 \\
0.44 & Re_p \geq 1000
\end{cases} \tag{2.1}$$

### 2.2 Morsi-Alexander Model
ใช้การประมาณค่าแบบแบ่งช่วง (Piecewise) 5 ช่วง เพื่อความแม่นยำสูงในช่วง $Re_p$ ที่กว้างมาก:
$$C_D = a_1 + \frac{a_2}{Re_p} + \frac{a_3}{Re_p^2} \tag{2.2}$$

---

## 3. แบบจำลองสำหรับฟองอากาศและหยดของเหลว (Bubbles & Droplets)

ในระบบ Gas-Liquid พื้นผิวรอยต่อสามารถเสียรูปได้ (Deformable) แรงฉุดจึงขึ้นอยู่กับ **Eötvös Number ($Eo$)**:

### 3.1 Ishii-Zuber Model
คำนึงถึงการเปลี่ยนผ่านจากฟองทรงกลมไปสู่ฟองที่บิดเบี้ยว (Distorted bubbles):
$$C_D = \frac{8}{3}\frac{Eo}{Eo + 4} \quad (\text{สำหรับระบอบที่บิดเบี้ยว}) \tag{2.3}$$

### 3.2 Grace Correlation
$$C_D = \max\[\frac{2}{\sqrt{Re_p}}, \min\[\frac{8}{3}\frac{Eo}{Eo + 4}, 0.44\]\] \tag{2.4}$$

---

## 4. แบบจำลองสำหรับอนุภาคความเข้มข้นสูง (Dense Suspensions)

เมื่อ $\alpha_d > 0.1$ การปฏิสัมพันธ์ระหว่างอนุภาค (Crowding effect) จะทำให้แรงฉุดเพิ่มขึ้น:

### 4.1 Syamlal-O'Brien Model
นิยมใช้ในระบบ **Fluidized Bed**:
$$C_D = \frac{v_r^2}{v_s^2} \tag{2.5}$$ 
โดยที่ $v_s$ คือ Terminal settling velocity ที่ปรับปรุงตามความเข้มข้น

### 4.2 Gidaspow Model
ผสมผสานระหว่าง Wen-Yu (สำหรับเจือจาง) และ Ergun (สำหรับหนาแน่น)

---

## 5. อนุภาคที่ไม่ใช่ทรงกลม (Non-Spherical Particles)

ใช้ **Shape Factor ($\phi$)** เพื่อปรับปรุงค่า $C_D$ ตามสมการของ **Haider-Levenspiel**:
$$C_D = \frac{24}{Re_p}(1 + a Re_p^b) + \frac{c}{1 + d/Re_p} \tag{2.6}$$

---

## 📊 ตารางสรุปการเลือกใช้งาน

| โมเดล | ระบบที่เหมาะสม | จุดเด่น |
|-------|--------------|---------|
| **Schiller-Naumann** | ทั่วไป (Spherical) | เสถียร, คำนวณเร็ว |
| **Ishii-Zuber** | Gas-Liquid | รองรับการเสียรูปของฟอง |
| **Syamlal-O'Brien** | Fluidized Bed | แม่นยำในระบบหนาแน่น |
| **Haider-Levenspiel** | ผง, เมล็ดพืช | รองรับรูปร่างไม่คงที่ |

การเลือกโมเดลควรพิจารณาจากปรากฏการณ์ทางฟิสิกส์ที่เป็นตัวกำหนดหลักในระบบนั้นๆ