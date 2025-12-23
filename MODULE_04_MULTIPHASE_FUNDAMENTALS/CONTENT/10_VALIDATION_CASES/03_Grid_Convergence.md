# การศึกษาการลู่เข้าของกริด (Grid Convergence Study)

## 1. บทนำ (Introduction)

การศึกษาการลู่เข้าของกริด (Grid Convergence Study) เป็นขั้นตอนสำคัญในกระบวนการ **Code Verification** เพื่อให้แน่ใจว่าผลเฉลยเชิงตัวเลข (Numerical Solution) ไม่ขึ้นอยู่กับความละเอียดของเมช (Mesh Independent) การศึกษาเชิงระบบนี้ช่วยให้เราสามารถประเมินความไม่แน่นอนเชิงตัวเลข (Numerical Uncertainty) และหาค่าที่ใกล้เคียงกับผลเฉลยที่แท้จริงได้แม่นยำยิ่งขึ้น

---

## 2. พื้นฐานทางทฤษฎี (Theoretical Foundation)

### 2.1 การละเอียดเมชอย่างเป็นระบบ (Systematic Mesh Refinement)
การศึกษาต้องรันบนเมชอย่างน้อย 3 ชุดที่มีความละเอียดต่างกันตามอัตราส่วนคงที่ $r$ (มักใช้ $r=2$):
- เมชหยาบ ($h_3$)
- เมชกลาง ($h_2$)
- เมชละเอียด ($h_1$)

### 2.2 Richardson Extrapolation
ใช้สำหรับประมาณค่าผลเฉลยในอุดมคติที่ขนาดเมชเป็นศูนย์ ($h \to 0$):
$$\phi_{exact} \approx \phi_1 + \frac{\phi_1 - \phi_2}{r^p - 1}$$ 

โดยที่ $p$ คืออันดับความแม่นยำที่สังเกตได้ (Observed order of accuracy):
$$p = \frac{\ln\left(\frac{\phi_3 - \phi_2}{\phi_2 - \phi_1}\right)}{\ln(r)}$$

---

## 3. ดัชนีการลู่เข้าของกริด (Grid Convergence Index - GCI)

ดัชนี GCI ตามวิธีของ Roache (1998) เป็นตัวชี้วัดความแปรปรวนเชิงตัวเลขในรูปแบบเปอร์เซ็นต์:
$$\text{GCI}_{12} = F_s \frac{|\epsilon_{12}|}{r^p - 1}$$ 

- $F_s$: ปัจจัยความปลอดภัย (Safety Factor) โดยทั่วไปใช้ 1.25 สำหรับการศึกษาด้วยเมช 3 ระดับ
- $\epsilon_{12}$: ความคลาดเคลื่อนสัมพัทธ์ระหว่างเมชละเอียดและเมชกลาง ($|\phi_1 - \phi_2| / \phi_1$)

---

## 4. การประเมินคุณภาพด้วย Error Norms

เราใช้ Norm รูปแบบต่างๆ เพื่อประเมินความแม่นยำทั่วทั้งโดเมน:

- **L2 Norm (Root Mean Square Error)**: ประเมินความแม่นยำโดยรวม
$$\epsilon_{L2} = \sqrt{\frac{1}{N} \sum_{i=1}^{N} \left( \frac{\phi_i - \phi_{exact,i}}{\phi_{ref}} \right)^2 }$$ 

- **Maximum Norm (L∞)**: ระบุจุดที่เกิดความคลาดเคลื่อนสูงที่สุด
$$\epsilon_{max} = \max_{i} \left| \frac{\phi_i - \phi_{exact,i}}{\phi_{ref}} \right|$$ 

---

## 5. การนำไปใช้งานใน OpenFOAM (C++ Implementation)

### 5.1 คลาสสำหรับคำนวณการลู่เข้า
```cpp
class gridConvergenceStudy {
public:
    void calculateConvergence() {
        scalar r = meshSizes[1] / meshSizes[0];
        // คำนวณอันดับความแม่นยำ p
        scalar p = log(mag(results[2] - results[1]) / mag(results[1] - results[0])) / log(r);
        // Richardson extrapolation
        scalar phi_exact = results[2] + (results[2] - results[1]) / (pow(r, p) - 1);
        // GCI สำหรับเมชละเอียด
        scalar GCI_fine = 1.25 * mag(results[2] - results[1]) / (pow(r, p) - 1) / mag(phi_exact);
        Info << "GCI on finest mesh: " << GCI_fine * 100 << "%" << endl;
    }
};
```

---

## 6. แนวทางปฏิบัติสำหรับการไหลหลายเฟส (Multiphase Specifics)

การศึกษาการลู่เข้าในระบบหลายเฟสมีความท้าทายเพิ่มเติมดังนี้:
1. **Interface Tracking**: ต้องละเอียดเมชเป็นพิเศษบริเวณอินเตอร์เฟซเพื่อจับรูปทรงของฟองหรือคลื่นให้ถูกต้อง
2. **Phase Fraction Convergence**: สนามสัดส่วนปริมาตร ($\alpha$) มักลู่เข้าช้ากว่าสนามความเร็ว ($U$) จึงต้องตรวจสอบ GCI แยกตามแต่ละเฟส
3. **Adaptive Mesh Refinement (AMR)**: ในกรณีที่ใช้อินเตอร์เฟซแบบเคลื่อนที่ ควรใช้เกณฑ์การละเอียดเมชที่อิงจาก Gradient ของ $\alpha$

### เกณฑ์การยอมรับ (Acceptance Criteria)
- **GCI < 3%** สำหรับตัวแปรหลัก (เช่น Gas Holdup, Terminal Velocity)
- **Mass Conservation Error < $10^{-10}$** สำหรับการตรวจสอบความถูกต้องของโค้ด

การทำ Grid Convergence Study อย่างเป็นระบบช่วยเปลี่ยนจากการจำลองที่ "ดูเหมือนจริง" ให้กลายเป็นการคำนวณทางวิศวกรรมที่ "เชื่อถือได้"

*อ้างอิง: Roache, P. J. (1998) และมาตรฐาน ASME V&V 20 สำหรับการตรวจสอบความถูกต้องใน CFD*
