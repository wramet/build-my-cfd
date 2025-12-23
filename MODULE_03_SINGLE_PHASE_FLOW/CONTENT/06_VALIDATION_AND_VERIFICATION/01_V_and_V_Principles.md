# หลักการการตรวจสอบและยืนยันความถูกต้อง (V&V Principles)

## 📐 1. การตรวจสอบความถูกต้อง (Verification)

**Verification** เป็นกระบวนการตรวจสอบความแม่นยำทางคณิตศาสตร์: **"Are we solving the equations right?"**

### 1.1 การวิเคราะห์ข้อผิดพลาดเชิงตัวเลข
ข้อผิดพลาดรวมเกิดจากสามส่วนหลัก:
$$\varepsilon_{\text{total}} = \varepsilon_{\text{discretization}} + \varepsilon_{\text{iteration}} + \varepsilon_{\text{round-off}}$$

- **Discretization Error**: เกิดจากการแทนที่อนุพันธ์ด้วยพีชคณิต ($O(\Delta x^n)$)
- **Iteration Error**: เกิดจากการหยุด Solver ก่อนลู่เข้าอย่างสมบูรณ์
- **Round-off Error**: ข้อผิดพลาดจากการคำนวณเลขทศนิยมที่จำกัด

---

## 📊 2. การทวนสอบ (Validation)

**Validation** เป็นกระบวนการตรวจสอบความแม่นยำทางกายภาพ: **"Are we solving the right equations?"**

### 2.1 เมตริกการทวนสอบทางสถิติ (Statistical Metrics)
ใช้ในการวัดปริมาณความสอดคล้องระหว่าง CFD ($y_i^{CFD}$) และการทดลอง ($y_i^{exp}$):

**Root Mean Square Error (RMSE):**
$$\text{RMSE} = \sqrt{\frac{1}{N} \sum_{i=1}^{N} (y_i^{\text{CFD}} - y_i^{\text{exp}})^2}$$

**Coefficient of Determination ($R^2$):**
ใช้วัดความสัมพันธ์เชิงเส้นระหว่างสองชุดข้อมูล หาก $R^2 > 0.95$ ถือว่ามีความสอดคล้องกันสูงมาก

---

## 🏗️ 3. ลำดับชั้นการตรวจสอบ (Verification Hierarchy)

1. **Unit Testing**: ทดสอบคลาสและฟังก์ชันย่อยใน OpenFOAM
2. **Code Verification (MMS)**: ตรวจสอบว่า Solver ทำงานได้ตามอันดับความแม่นยำทางทฤษฎี
3. **Solution Verification**: ตรวจสอบความเป็นอิสระของ Mesh สำหรับงานแต่ละชิ้น

---

## ✅ 4. แนวทางปฏิบัติที่ดีที่สุด (Best Practices)

- **Start Simple**: ตรวจสอบความถูกต้องกับผลเฉลยเชิงวิเคราะห์ (Analytical solutions) สำหรับเคสที่ง่ายก่อน
- **Systematic Refinement**: การปรับปรุง Mesh ต้องทำอย่างเป็นระบบ (สม่ำเสมอทุกทิศทาง)
- **Blind Validation**: หลีกเลี่ยงการปรับแต่งพารามิเตอร์แบบ "Trial and error" เพื่อให้ตรงกับผลทดลองเพียงอย่างเดียว

---
**หัวข้อถัดไป**: [ความเป็นอิสระของ Mesh และการวิเคราะห์ GCI](./02_Mesh_Independence.md)
