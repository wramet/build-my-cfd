# พื้นฐาน Large Eddy Simulation (LES)

## 📋 1. บทนำสู่ LES

**Large Eddy Simulation (LES)** เป็นวิธีการที่อยู่ระหว่าง RANS (หาค่าเฉลี่ยทั้งหมด) และ DNS (แก้ปัญหาทุกสเกล)

### หลักการสำคัญ:
1. **Resolve**: แก้ปัญหาโครงสร้างความปั่นป่วนขนาดใหญ่ที่มีพลังงานสูงโดยตรง
2. **Model**: สร้างแบบจำลองเฉพาะความปั่นป่วนสเกลเล็ก (Subgrid-scale) ซึ่งมีลักษณะเป็น Isotropic มากกว่าและมีพฤติกรรมเป็นสากลมากกว่า

---

## 📐 2. การกรองเชิงพื้นที่ (Spatial Filtering)

ใน LES เราใช้ตัวกรอง (Filter) เพื่อแยกสเกลที่ต้องการแก้:
$$\bar{\phi}(\mathbf{x}, t) = \int_{\Omega} \phi(\mathbf{x}', t) G(\mathbf{x}, \mathbf{x}', \Delta) \mathrm{d}\mathbf{x}'$$ 

โดยที่ $\Delta$ คือความกว้างของตัวกรอง (Filter width) ซึ่งมักจะสัมพันธ์กับขนาดของ Mesh ($\Delta \approx \sqrt[3]{V_{cell}}$)

---

## 🔢 3. แบบจำลอง Subgrid-Scale (SGS Models)

เนื่องจากสเกลเล็กถูกตัดออก เราต้องการแบบจำลองมาทดแทนผลกระทบของมันผ่าน **SGS Stress Tensor ($\tau_{ij}^{SGS}$)**:

### 3.1 Smagorinsky Model (Static)
เป็นแบบจำลองที่ง่ายที่สุด อิงตามความหนืด Eddy:
$$\nu_{SGS} = (C_s \Delta)^2 |\bar{S}| \tag{3.1}$$ 
- $C_s$ มักมีค่าประมาณ 0.1 - 0.2

### 3.2 WALE (Wall-Adapted Local Eddy-viscosity)
ถูกออกแบบมาเพื่อให้ค่า $\nu_{SGS}$ ลู่เข้าสู่ศูนย์ที่ผนังโดยธรรมชาติ เหมาะสำหรับงานที่มีผนังซับซ้อน

---

## ⚙️ 4. ข้อกำหนดที่เข้มงวดของ LES

LES มีความต้องการทรัพยากรสูงกว่า RANS อย่างมาก:
- **Spatial Resolution**: Mesh ต้องละเอียดพอที่จะจับพลังงาน Turbulence ได้อย่างน้อย 80%
- **Temporal Resolution**: ค่า CFL ต้องต่ำกว่า 0.5 เสมอ ($Co < 0.5$)
- **Numerical Schemes**: ต้องใช้ Scheme อันดับสองที่ไม่มีความหน่วง (Non-dissipative) เช่น `Gauss linear`

---

## 💻 5. การตั้งค่าใน OpenFOAM (`constant/turbulenceProperties`)

```cpp
simulationType LES;
LES
{
    LESModel        Smagorinsky;
    turbulence      on;
    delta           cubeRootVol;
    SmagorinskyCoeffs
    {
        Cs          0.15;
    }
}
```

---
**จบเนื้อหาโมดูลการสร้างแบบจำลองความปั่นป่วน**

```