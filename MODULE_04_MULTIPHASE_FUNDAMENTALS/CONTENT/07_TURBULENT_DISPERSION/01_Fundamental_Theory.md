# ทฤษฎีพื้นฐานการกระจายตัวเนื่องจากความปั่นป่วน (Fundamental Theory)

## 1. บทนำ (Introduction)

ในการไหลหลายเฟสแบบปั่นป่วน อนุภาคจะได้รับอิทธิพลจากกระแสหมุนวน (Eddies) หลายขนาด ซึ่งทำให้เกิดการเคลื่อนที่แบบสุ่มและการแพร่กระจายของเฟสในเชิงสถิติ

---

## 2. สมการโมเมนตัมเฉลี่ย (Reynolds-Averaged Equations)

เมื่อพิจารณาความผันผวนเนื่องจากความปั่นป่วนในระบบหลายเฟส สมการโมเมนตัมของเฟส $k$ คือ:

$$\frac{\partial}{\partial t}(\overline{\alpha_k \rho_k \mathbf{u}_k}) + \nabla \cdot (\overline{\alpha_k \rho_k \mathbf{u}_k \mathbf{u}_k}) = -\overline{\alpha_k \nabla p} + \nabla \cdot \overline{\boldsymbol{\tau}_k} + \overline{\mathbf{M}_k} - \nabla \cdot \overline{\alpha_k \rho_k \mathbf{u}'_k \mathbf{u}'_k} \tag{1.1}$$

เทอมสุดท้าย $\overline{\alpha_k \rho_k \mathbf{u}'_k \mathbf{u}'_k}$ คือ **Turbulent Stress** ซึ่งต้องอาศัยแบบจำลองการปิด (Closure) เช่น Boussinesq Approximation

---

## 3. การอนุมานแรงกระจายตัว (Force Derivation)

แรงกระจายตัวเนื่องจากความปั่นป่วนเกิดขึ้นจากสหสัมพันธ์ (Correlation) ระหว่างความผันผวนของความเร็วและความไม่สม่ำเสมอของความเข้มข้น:

$$\mathbf{F}_{TD} = -\overline{\alpha_d' \rho_d \mathbf{u}_d'} \tag{1.2}$$

โดยที่ $\alpha_d'$ คือความผันผวนของสัดส่วนปริมาตร และ $\mathbf{u}_d'$ คือความผันผวนของความเร็วเฟสกระจาย

---

## 4. สมมติฐานการแพร่ตามเกรเดียนต์ (Gradient Diffusion Hypothesis)

แบบจำลองส่วนใหญ่ตั้งสมมติฐานว่าฟลักซ์ความปั่นป่วนเป็นสัดส่วนกับเกรเดียนต์ของความเข้มข้น:

$$\mathbf{F}_{td} = -D_{TD} \nabla \alpha_d \tag{1.3}$$

โดยที่ $D_{TD}$ คือสัมประสิทธิ์การกระจายตัว ซึ่งสัมพันธ์กับความหนืดความปั่นป่วน ($\nu_t$):
$$D_{TD} = \frac{\nu_t}{\sigma_{TD}}$$
- **$\\sigma_{TD}$ (Turbulent Schmidt Number):** อัตราส่วนระหว่างการแพร่โมเมนตัมและการแพร่มวล (ค่าปกติ $\\approx 0.9$)

---

## 5. การตอบสนองของอนุภาค (Particle Response)

ประสิทธิภาพการกระจายตัวขึ้นอยู่กับ ** Stokes Number ($St$)**:
$$St = \frac{\tau_p}{\tau_t} \tag{1.4}$$
- **$St \ll 1$:** อนุภาคเคลื่อนที่ตามความผันผวนได้สมบูรณ์ (การกระจายตัวสูงสุด)
- **$St \gg 1$:** อนุภาคมีความเฉื่อยสูงเกินกว่าจะตอบสนองต่อกระแสหมุนวน (การกระจายตัวต่ำ)

การเข้าใจทฤษฎีนี้ช่วยให้สามารถปรับแต่งค่า **Turbulent Schmidt Number** ใน OpenFOAM ให้เหมาะสมกับขนาดอนุภาคและสภาวะการไหลจริงได้