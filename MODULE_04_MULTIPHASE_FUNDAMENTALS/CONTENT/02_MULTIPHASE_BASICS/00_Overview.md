# พื้นฐานการจำลองการไหลแบบหลายเฟสแบบออยเลอร์ (Eulerian Multiphase Flow Fundamentals)

การจำลองการไหลแบบหลายเฟสแบบออยเลอร์ (Eulerian multiphase flow modeling) เป็นแนวทางที่พิจารณาแต่ละเฟส (ของเหลว ก๊าซ ของแข็ง) เป็น **สสารต่อเนื่องที่แทรกซึมซึ่งกันและกัน (Interpenetrating Continua)** โดยแต่ละเฟสจะมีชุดสมการอนุรักษ์ (Conservation Equations) ของตนเอง และเชื่อมโยงกันผ่านปรากฏการณ์ที่รอยต่อ (Interfacial Phenomena)

---

## 1. แนวคิดพื้นฐาน (Fundamental Concepts)

### การนิยามเฟสและเศษส่วนปริมาตร (Volume Fraction - $\alpha$)

ในระบบหลายเฟส แต่ละเฟส $k$ จะถูกระบุด้วยสัดส่วนปริมาตร $\alpha_k$ ซึ่งแสดงถึงโอกาสหรือสัดส่วนของปริมาตรควบคุมที่เฟสนั้นครอบครองอยู่:

$$\sum_{k=1}^{n} \alpha_k = 1$$

โดยที่ $0 \leq \alpha_k \leq 1$ หาก $\alpha_k = 1$ หมายถึงจุดนั้นมีเพียงเฟส $k$ เท่านั้น (Pure phase)

### คุณสมบัติของสารผสม (Mixture Properties)

คุณสมบัติที่มีประสิทธิภาพ (Effective properties) ของสารผสมคำนวณโดยอิงจากสัดส่วนปริมาตร:

- **ความหนาแน่นรวม:** $\rho_{mix} = \sum \alpha_k \rho_k$
- **ความหนืดรวม:** $\mu_{mix} = \sum \alpha_k \mu_k$

---

## 2. สมการควบคุม (Governing Equations)

### 2.1 สมการความต่อเนื่อง (Continuity Equations)
สำหรับแต่ละเฟส $k$:
$$\frac{\partial (\alpha_k \rho_k)}{\partial t} + \nabla \cdot (\alpha_k \rho_k \mathbf{u}_k) = \sum_{l \neq k} \dot{m}_{lk}$$
โดยที่ $\dot{m}_{lk}$ คืออัตราการถ่ายเทมวลจากเฟส $l$ ไปยังเฟส $k$ (เช่น การระเหยหรือควบแน่น)

### 2.2 สมการโมเมนตัม (Momentum Equations)
$$\frac{\partial (\alpha_k \rho_k \mathbf{u}_k)}{\partial t} + \nabla \cdot (\alpha_k \rho_k \mathbf{u}_k \mathbf{u}_k) = -\alpha_k \nabla p + \nabla \cdot (\alpha_k \boldsymbol{\tau}_k) + \alpha_k \rho_k \mathbf{g} + \mathbf{M}_k$$
- **$p$:** ความดันร่วม (Shared pressure)
- **$oldsymbol{\tau}_k$:** เทนเซอร์ความเค้น (Stress tensor) รวมถึงความปั่นป่วน
- **$\\\mathbf{M}_k$:** แรงระหว่างเฟส (Interfacial forces) เช่น Drag, Lift, Virtual Mass

### 2.3 สมการพลังงาน (Energy Equation)
$$\frac{\partial (\alpha_k \rho_k h_k)}{\partial t} + \nabla \cdot (\alpha_k \rho_k \mathbf{u}_k h_k) = \alpha_k \frac{\partial p}{\partial t} + \nabla \cdot (\alpha_k \kappa_k \nabla T_k) + Q_k$$
- **$Q_k$:** การถ่ายเทความร้อนระหว่างเฟส $Q_{kl} = h_{kl} A_{kl} (T_l - T_k)$

---

## 3. แรงที่รอยต่อ (Interfacial Forces)

การถ่ายเทโมเมนตัม $\mathbf{M}_k$ ประกอบด้วยแรงสำคัญดังนี้:

| แรง (Force) | ความหมายทางฟิสิกส์ | สมการพื้นฐาน |
|---|---|---|
| **Drag** | แรงต้านเนื่องจากความเร็วสัมพัทธ์ | $\mathbf{F}_D = K_{kl}(\mathbf{u}_l - \mathbf{u}_k)$ |
| **Lift** | แรงยกเนื่องจากความเฉือนในของไหล | $\mathbf{F}_L = C_L \rho_c \alpha_k (\mathbf{u}_k - \mathbf{u}_c) \times (\nabla \times \mathbf{u}_c)$ |
| **Virtual Mass** | แรงเนื่องจากการเร่งของไหลรอบข้าง | $\mathbf{F}_{VM} = C_{VM} \rho_c \alpha_k (\frac{D\mathbf{u}_c}{Dt} - \frac{D\mathbf{u}_k}{Dt})$ |
| **Turbulent Dispersion** | การกระจายตัวเนื่องจากความปั่นป่วน | $\mathbf{F}_{TD} = -C_{TD} \rho_c k_{t,c} \nabla \alpha_k$ |

---

## 4. รูปแบบการไหล (Flow Regimes)

พฤติกรรมของการไหลแบบหลายเฟสขึ้นอยู่กับการกระจายตัวของแต่ละเฟส:

- **Dispersed Flow:** เฟสหนึ่งกระจายเป็นหยดหรือฟองในอีกเฟสที่เป็นเนื้อเดียว (เช่น Bubbly flow, Spray)
- **Separated Flow:** เฟสต่างๆ แยกกันชัดเจนด้วยรอยต่อขนาดใหญ่ (เช่น Stratified flow, Annular flow)
- **Transitional Flow:** รูปแบบผสมที่ซับซ้อน (เช่น Slug flow, Churn flow)

---

## 5. การนำไปใช้ใน OpenFOAM

ใน OpenFOAM การแก้สมการเหล่านี้ใช้ `multiphaseEulerFoam` โดยมีโครงสร้างหลักดังนี้:

- **`constant/phaseProperties`:** กำหนดโมเดลของแต่ละเฟสและแรงระหว่างเฟส
- **`alphaEqn.H`:** แก้สมการสัดส่วนเฟสโดยใช้ MULES scheme
- **`pEqn.H`:** แก้สมการความดันเพื่อรักษาเงื่อนไขความต่อเนื่อง (Continuity)

---

เนื้อหาในบทนี้เป็นพื้นฐานสำคัญก่อนที่จะเจาะลึกในรายละเอียดของแต่ละแรง (Module 04-07) และการตั้งค่า Solver ในระดับสูงต่อไป