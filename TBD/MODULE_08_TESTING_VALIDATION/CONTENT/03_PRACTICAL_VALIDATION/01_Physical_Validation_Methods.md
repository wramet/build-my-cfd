# 01 วิธีการตรวจสอบความถูกต้องทางกายภาพ (Physical Validation Methods)

การตรวจสอบความถูกต้องทางกายภาพ (Physical Validation) คือกระบวนการยืนยันว่าแบบจำลอง CFD ของเราให้ผลลัพธ์ที่ตรงกับความเป็นจริงทางฟิสิกส์

## 1.1 การเปรียบเทียบกับผลเฉลยเชิงวิเคราะห์ (Analytical Solutions)

สำหรับปัญหาพื้นฐานที่มีสูตรคณิตศาสตร์รองรับ เราสามารถใช้สูตรเหล่านั้นเป็นบรรทัดฐาน (Benchmark)

![[poiseuille_flow_validation.png]]
`A comparison diagram for Poiseuille Flow in a pipe. The left side shows the analytical parabolic velocity profile with the LaTeX formula embedded. The right side shows a discretized CFD domain with cell-centered velocity vectors forming the same parabola. A 'Delta' symbol indicates the small error between them. Scientific textbook diagram, clean vector line art, white background, high definition, flat design, educational infographic --ar 16:9`

### ตัวอย่างที่ 1: การนำความร้อน 1 มิติ (1D Heat Conduction)
$$\frac{d^2T}{dx^2} = 0, \quad T(0) = T_0, \quad T(L) = T_L$$
ผลเฉลยเชิงวิเคราะห์คือเส้นตรง:
$$T(x) = T_0 + (T_L - T_0)\frac{x}{L}$$

### ตัวอย่างที่ 2: การไหลแบบพอยซีล (Poiseuille Flow)
การไหลในท่อที่มีความดันขับเคลื่อน:
$$u(r) = u_{max}\left(1 - \frac{r^2}{R^2}\right)$$
โดยที่ $u_{max}$ คำนวณได้จากความดันและค่าความหนืด ($\mu$)

---

## 1.2 การตรวจสอบด้วยข้อมูลการทดลอง (Experimental Validation)

เมื่อปัญหาซับซ้อนเกินกว่าจะมีสูตรเชิงวิเคราะห์ เราต้องใช้ข้อมูลจากการทดลองในห้องปฏิบัติการ

![[piv_vs_cfd_validation.png]]
`A dual-panel diagram showing Flow Validation. Panel A: 'Experimental (PIV)' shows a vector field with some measurement noise and error bars. Panel B: 'Numerical (CFD)' shows a smooth vector field from OpenFOAM. A cross-plot graph below compares velocity along a line, showing the CFD line passing through the experimental error bars. Scientific textbook diagram, clean vector line art, white background, high definition, flat design, educational infographic --ar 16:9`

### ข้อควรพิจารณาสำคัญ:
-   **Reynolds Number Matching**: ต้องแน่ใจว่าการจำลองมีค่า $Re$ ตรงกับการทดลอง
-   **Boundary Conditions**: พยายามจำลองเงื่อนไขขอบเขตให้เหมือนกับการตั้งค่าการทดลองมากที่สุด (เช่น Turbulence Intensity ที่ทางเข้า)
-   **Measurement Uncertainty**: ต้องตระหนักว่าข้อมูลการทดลองก็มีความคลาดเคลื่อน (Error Bar) ดังนั้นผลลัพธ์ CFD ไม่จำเป็นต้องตรงเป๊ะ 100% แต่ควรอยู่ในช่วงความเชื่อมั่น

### ตัวอย่างเทคนิคการตรวจสอบ:
-   **PIV Comparison**: การเปรียบเทียบสนามความเร็ว (Velocity Field) จาก Particle Image Velocimetry กับผลลัพธ์จาก OpenFOAM
-   **Point-wise comparison**: การเปรียบเทียบค่าความดันหรืออุณหภูมิที่ตำแหน่งเฉพาะ (Probes)

---

## 1.3 การศึกษาความเป็นอิสระของเมช (Mesh Independence Study)

ความถูกต้องทางกายภาพจะไม่สมบูรณ์หากผลลัพธ์ยังเปลี่ยนไปตามความละเอียดของเมช

```mermaid
flowchart TD
    A[Generate Coarse Mesh M1] --> B[Run Simulation S1]
    B --> C[Refine Mesh to M2]
    C --> D[Run Simulation S2]
    D --> E{Check Key Metric change 
    |S2 - S1| < Tolerance?}
    E -- No --> C
    E -- Yes --> F[Mesh Independent Solution]
```

### เวิร์กโฟลว์การทำ Mesh Independence:
1.  **Generate Coarse Mesh**: เริ่มจากเมชอย่างง่าย
2.  **Refine Mesh**: เพิ่มความละเอียดเป็น 2 เท่า (หรือตามอัตราส่วนที่เหมาะสม)
3.  **Compare Key Metrics**: เปรียบเทียบตัวแปรสำคัญ (เช่น แรงลาก, อุณหภูมิสูงสุด)
4.  **Convergence**: หากผลลัพธ์ระหว่างเมชละเอียดและเมชก่อนหน้าต่างกันน้อยกว่าเกณฑ์ที่กำหนด (เช่น < 1%) ถือว่าเมชนั้นมีความเป็นอิสระ

การทำกระบวนการนี้จะช่วยสร้างความมั่นใจว่า "ฟิสิกส์" ที่เราเห็น ไม่ได้เป็นผลมาจาก "ความหยาบของเมช"