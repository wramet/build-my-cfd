# แบบจำลองการกระจายตัวเนื่องจากความปั่นป่วนเฉพาะ (Specific Models)

## 1. บทนำ (Introduction)

แบบจำลองการกระจายตัวเนื่องจากความปั่นป่วนทำหน้าที่กำหนดสัมประสิทธิ์การแพร่ ($D_{TD}$) เพื่อปิดเทอมแรงกระจายตัวในสมการโมเมนตัม โดยส่วนใหญ่จะอิงตามคุณสมบัติความปั่นป่วนของเฟสต่อเนื่อง (เช่น $\mu_{t,c}$, $k_c$, $\varepsilon_c$)

---

## 2. แบบจำลอง Burns et al. (นิยมใช้ที่สุด)

เป็นแบบจำลองที่ง่ายและเสถียรที่สุด อิงตามสมมติฐานการแพร่ตามเกรเดียนต์ (Gradient Diffusion Hypothesis):

$$\mathbf{F}_{td} = -C_{td} \rho_c \frac{\mu_{t,c}}{\sigma_{td}} \nabla \alpha_d \tag{2.1}$$

**พารามิเตอร์ที่สำคัญ:**
- $\mu_{t,c}$: ความหนืดความปั่นป่วนของเฟสต่อเนื่อง
- $\sigma_{td}$: Turbulent Schmidt Number (ค่าปกติ 0.9 - 1.0)
- $C_{td}$: สัมประสิทธิ์การกระจายตัว

---

## 3. แบบจำลอง Lopez de Bertodano

เน้นการพิจารณาสัดส่วนเฟสเฉพาะที่ โดยระบุว่าแรงกระจายตัวควรจะแรงที่สุดเมื่อเฟสกระจายตัวมีปริมาณน้อย:

$$D_{TD,k} = C_{TD} \frac{\mu_{t,c}}{\rho_c} \frac{\alpha_k \alpha_l}{\max(\alpha_k, \alpha_l)} \tag{2.2}$$

แบบจำลองนี้เหมาะสำหรับระบบ Gas-Liquid ที่มีการเปลี่ยนแปลง Void fraction อย่างมากในโดเมน

---

## 4. แบบจำลอง Simonin

อิงตามทฤษฎีจลนศาสตร์ (Kinetic Theory) โดยพิจารณามาตราส่วนความยาวความปั่นป่วน ($l_c$):

$$D_{TD,k} = C_{TD} \sqrt{k_c} l_c \tag{2.3}$$

โดยที่ $l_c = C_μ^{3/4} k_c^{3/2} / \epsilon_c$ เหมาะสำหรับระบบ **Fluidized Bed** หรือสารแขวนลอยที่มีความเข้มข้นสูง

---

## 5. การนำไปใช้ใน OpenFOAM (C++ Implementation)

ใน OpenFOAM, โมเดลเหล่านี้ถูกนำไปใช้ผ่านคลาส `turbulentDispersionModel`:

```cpp
// การคำนวณแรงใน Burns model (OpenFOAM Source Code)
virtual tmp<volVectorField> Fi() const
{
    const volScalarField& alpha = dispersed().alpha();
    const volScalarField& rho = continuous().rho();
    const volScalarField Dtd = this->D(); // สัมประสิทธิ์การกระจายตัว

    return -rho * Dtd * fvc::grad(alpha);
}
```

---

## 📊 ตารางสรุปการเลือกใช้งาน

| โมเดล | กลไกหลัก | การใช้งานที่เหมาะสม |
|-------|----------|-------------------|
| **Burns** | Gradient Diffusion | ทั่วไป, ระบบ Gas-Liquid |
| **Bertodano** | Asymmetric Alpha | ระบบที่มี Void fraction ผันผวนสูง |
| **Simonin** | Kinetic Theory | ระบบของแข็ง-ของเหลว, หนาแน่น |

การเลือกค่า **Turbulent Schmidt Number ($\sigma_{td}$)** ที่ถูกต้องมีผลอย่างมากต่อการทำนายโปรไฟล์ความเข้มข้นของอนุภาค หากตั้งค่าต่ำเกินไปอนุภาคจะฟุ้งกระจายมากเกินความจริง