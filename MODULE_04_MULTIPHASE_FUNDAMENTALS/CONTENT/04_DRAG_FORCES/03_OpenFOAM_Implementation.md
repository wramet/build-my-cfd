# รายละเอียดการนำไปใช้ใน OpenFOAM (OpenFOAM Implementation)

## 1. ลำดับชั้นของคลาส Drag Model (Class Hierarchy) 

OpenFOAM ออกแบบระบบจำลองแรงฉุดโดยใช้หลักการ Object-Oriented Programming ซึ่งช่วยให้ผู้ใช้สามารถสลับโมเดลได้ตามความเหมาะสมผ่านไฟล์การตั้งค่า

### โครงสร้างหลักใน C++
คลาสพื้นฐาน `dragModel` กำหนดฟังก์ชันเสมือน (Virtual functions) สำหรับโมเดลลูก:

```cpp
class dragModel
{
public:
    // คำนวณสัมประสิทธิ์แรงฉุด (Pure virtual)
    virtual tmp<volScalarField> Cd() const = 0;

    // คำนวณสัมประสิทธิ์การแลกเปลี่ยนโมเมนตัม
    virtual tmp<volScalarField> K() const;

    // คำนวณแรงฉุดรวม
    virtual tmp<volVectorField> F() const;
};
```

---

## 2. การคำนวณ Momentum Exchange Coefficient ($K$)

ค่า $K$ คือพารามิเตอร์ที่เชื่อมโยงความเร็วของทั้งสองเฟสเข้าด้วยกันในสมการโมเมนตัม

### สูตรที่ใช้ใน Source Code
$$K = \frac{3}{4} C_D \frac{\alpha_k \alpha_l \rho_l}{d_k} |\mathbf{u}_l - \mathbf{u}_k| \tag{3.1}$$

**การนำไปใช้ (Implementation):**
```cpp
tmp<volScalarField> dragModel::K() const
{
    const volScalarField& alpha1 = pair_.phase1().alpha();
    const volScalarField& alpha2 = pair_.phase2().alpha();
    const volScalarField& rho2 = pair_.phase2().rho();
    const volScalarField& d = pair_.dispersed().d();
    const volScalarField& Ur = pair_.Ur();

    return (3.0/4.0)*Cd()*alpha1*alpha2*rho2/(d)*Ur;
}
```

---

## 3. การจัดการความเร็วสัมพัทธ์และเลขเรย์โนลด์

OpenFOAM คำนวณความเร็วสัมพัทธ์ ($U_r$) และเลขเรย์โนลด์ของอนุภาค ($Re_p$) โดยอัตโนมัติในคลาส `PhasePair`:

- **Relative Velocity:** $|\mathbf{u}_r| = |\mathbf{u}_2 - \mathbf{u}_1|$
- **Reynolds Number:** $Re_p = \frac{\rho_1 |\mathbf{u}_r| d_1}{\mu_1}$

---

## 4. ข้อควรพิจารณาด้านเสถียรภาพ (Numerical Stability)

เนื่องจากเทอมแรงฉุดมักจะมีค่าสูงและ "แข็ง" (Stiff) OpenFOAM จึงมีกลยุทธ์ดังนี้:

### 4.1 การจัดการแบบ Implicit vs Explicit
- **Explicit Drag:** คำนวณจากค่าความเร็วใน Time step ก่อนหน้า ง่ายแต่ต้องการ Time step ที่เล็กมาก
- **Implicit Drag:** แก้สมการความเร็วพร้อมกัน เสถียรกว่ามาก แต่อาศัยการคำนวณที่ซับซ้อนขึ้น

### 4.2 การใช้ Under-Relaxation
เพื่อป้องกันการแกว่งกวัดของผลเฉลย (Oscillations):
$$\mathbf{K}_{new} = (1-\lambda)\mathbf{K}_{old} + \lambda \mathbf{K}_{calculated}$$
โดยทั่วไปใช้ค่า $\lambda \approx 0.3 - 0.7$ ในไฟล์ `fvSolution`

---

## 5. การตั้งค่าใน `constant/phaseProperties`

ผู้ใช้สามารถเลือกโมเดลได้ง่ายๆ ดังนี้:

```cpp
drag
(
    (air in water)
    {
        type            SchillerNaumann;
    }
    (oil in water)
    {
        type            IshiiZuber;
    }
);
```

การนำไปใช้ที่มีความยืดหยุ่นสูงนี้ช่วยให้ OpenFOAM สามารถจำลองระบบที่มีหลายเฟสและหลายคู่ปฏิสัมพันธ์ได้อย่างมีประสิทธิภาพ