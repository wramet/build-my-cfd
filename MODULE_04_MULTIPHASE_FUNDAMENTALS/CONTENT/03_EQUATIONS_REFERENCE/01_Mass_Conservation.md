# สมการการอนุรักษ์มวล (Mass Conservation Equations)

## สมการความต่อเนื่องจำเพาะเฟส - การพิสูจน์ฉบับสมบูรณ์

**หลักการพื้นฐาน**: มวลไม่สามารถถูกสร้างขึ้นหรือทำลายได้ เพียงแต่ถูกถ่ายเทระหว่างเฟสหรือถูกขนส่งผ่านปริภูมิเท่านั้น ในแบบจำลอง Eulerian-Eulerian แต่ละเฟส $k$ จะมีสมการความต่อเนื่องของตนเอง

### รากฐานทางคณิตศาสตร์ (Mathematical Foundation)

**สมการหลัก**: สำหรับเฟส $k$ ในระบบหลายเฟส:

$$\frac{\partial}{\partial t}(\alpha_k \rho_k) + \nabla  \cdot (\alpha_k \rho_k \mathbf{u}_k) = \dot{m}_k \tag{1.1} $$

**นิยามตัวแปร**:
- **$\alpha_k$**: สัดส่วนปริมาตรของเฟส $k$ (volume fraction, ไม่มีหน่วย) โดยที่ $0 \leq \alpha_k \leq 1$
- **$\rho_k$**: ความหนาแน่นของเฟส $k$ ($\text{kg/m}^3$)
- **$\mathbf{u}_k$**: เวกเตอร์ความเร็วของเฟส $k$ ($\text{m/s}$)
- **$\dot{m}_k$**: อัตราการถ่ายเทมวลสุทธิเชิงปริมาตรไปยังเฟส $k$ ($\text{kg/(m}^3\cdot\text{s)}$)

---

## การพิสูจน์จากการวิเคราะห์ปริมาตรควบคุม (Control Volume Analysis)

### 1. การนิยามมวลในปริมาตรควบคุม
พิจารณาปริมาตรควบคุม $V$ ที่ตรึงอยู่กับที่ มวลของเฟส $k$ ภายในปริมาตรนี้คือ:
$$m_k(t) = \int_{V} \alpha_k \rho_k \, \mathrm{d}V$$ 

### 2. อัตราการเปลี่ยนแปลงมวลตามเวลา
$$\frac{\mathrm{d}m_k}{\mathrm{d}t} = \int_V \frac{\partial}{\partial t}(\alpha_k \rho_k) \, \mathrm{d}V$$ 

### 3. ฟลักซ์มวลผ่านขอบเขต (Mass Flux)
ฟลักซ์มวลสุทธิที่ไหลออกจากปริมาตรควบคุมผ่านพื้นผิว $A$:
$$\dot{m}_{flux} = \oint_A \alpha_k \rho_k \mathbf{u}_k \cdot \mathbf{n} \, \mathrm{d}A = \int_V \nabla \cdot (\alpha_k \rho_k \mathbf{u}_k) \, \mathrm{d}V \quad (\text{ใช้ Divergence Theorem})$$ 

### 4. แหล่งกำเนิดมวลจากการเปลี่ยนเฟส (Source Term)
มวลที่เพิ่มขึ้นหรือลดลงจากการถ่ายเทระหว่างเฟส:
$$\dot{m}_{source} = \int_V \dot{m}_k \, \mathrm{d}V$$ 

### 5. การรวมสมการอนุรักษ์
จากหลักการ: [อัตราการเปลี่ยนแปลงมวล] + [ฟลักซ์มวลสุทธิขาออก] = [แหล่งกำเนิดมวล]
$$\int_V \left[ \frac{\partial}{\partial t}(\alpha_k \rho_k) + \nabla \cdot (\alpha_k \rho_k \mathbf{u}_k) - \dot{m}_k \right] \mathrm{d}V = 0$$ 
เนื่องจาก $V$ เป็นปริมาตรใดๆ พจน์ในวงเล็บต้องเป็นศูนย์ นำไปสู่สมการที่ (1.1)

---

## ข้อจำกัดของสัดส่วนปริมาตร (Volume Fraction Constraints)

**หลักการพื้นฐาน**: ผลรวมของสัดส่วนเฟสทั้งหมดจะต้องเท่ากับหนึ่ง ณ ทุกจุดในโดเมน เพื่อรับประกันว่าปริมาตรควบคุมถูกเติมเต็มอย่างสมบูรณ์

$$\sum_{k=1}^{N} \alpha_k = 1 \tag{1.2} $$

และสำหรับอัตราการถ่ายเทมวลสุทธิรวมทุกเฟสต้องเป็นศูนย์:
$$\sum_{k=1}^{N} \dot{m}_k = 0 \tag{1.3} $$

---

## การถ่ายเทมวลที่พื้นผิวรอยต่อ (Interfacial Mass Transfer)

เทอม $\dot{m}_k$ สามารถสร้างแบบจำลองได้หลายวิธี ขึ้นอยู่กับฟิสิกส์ของปัญหา:

### 1. โมเดลการระเหย/การควบแน่น (Phase Change Model)
$$\dot{m}_{lv} = h_m A_{lv}(\rho_{v,sat} - \rho_v)$$
โดยที่ $A_{lv}$ คือความหนาแน่นพื้นที่ผิวสัมผัส (Interfacial Area Density) และ $h_m$ คือสัมประสิทธิ์การถ่ายเทมวล

### 2. สมการ Hertz-Knudsen (Molecular Kinetic Theory)
นิยมใช้ในการจำลองการเปลี่ยนเฟสที่รวดเร็ว:
$$\dot{m}_{lv} = \frac{2}{2-\sigma} \sqrt{\frac{M}{2\pi R T}} \cdot \frac{p_{sat}(T) - p_v}{\sqrt{R T}}$$ 

---

## การนำไปใช้ใน OpenFOAM (OpenFOAM Implementation)

ใน Solver เช่น `multiphaseEulerFoam`, สมการความต่อเนื่องจะถูกแยกส่วน (discretized) ดังนี้:

```cpp
// Phase continuity equation construction
fvScalarMatrix alphaEqn
(
    fvm::ddt(alpha, rho) 
  + fvm::div(alphaRhoPhi, alpha)
 ==
    massTransferSource // เทอมแหล่งกำเนิดจากการเปลี่ยนเฟส
);

alphaEqn.solve();
```

### อัลกอริทึม MULES
OpenFOAM ใช้ **MULES (Multidimensional Universal Limiter with Explicit Solution)** เพื่อแก้สมการ $\alpha$ โดยรับประกันว่า:
1. **Boundedness:** $0 \leq \alpha \leq 1$ เสมอ
2. **Conservation:** มวลถูกอนุรักษ์อย่างเข้มงวด
3. **Sharpness:** รอยต่อเฟสไม่ฟุ้งกระจายจนเกินไป

---

## สรุปการวิเคราะห์เชิงตัวเลข (Numerical Considerations)

| พารามิเตอร์ | ข้อกำหนด | ผลกระทบ |
|------------|------------|----------|
| **CFL Number** | $\text{Co} < 1.0$ (แนะนำ 0.5 สำหรับ multiphase) | ความเสถียรของการคำนวณรอยต่อ |
| **Summation** | $\sum \alpha_k = 1$ | ความถูกต้องของสนามความดันและความต่อเนื่อง |
| **Mass Balance** | $\dot{m}_{12} = -\dot{m}_{21}$ | การอนุรักษ์มวลรวมของระบบ |

สมการความต่อเนื่องเป็นรากฐานที่สำคัญที่สุด หากสมการนี้ไม่ลู่เข้าหรือไม่อนุรักษ์มวล ผลลัพธ์ในสมการโมเมนตัมและพลังงานจะผิดพลาดตามไปด้วย
