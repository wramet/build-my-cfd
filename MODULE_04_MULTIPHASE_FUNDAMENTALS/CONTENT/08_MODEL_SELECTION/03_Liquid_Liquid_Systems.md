# ระบบของเหลว-ของเหลว (Liquid-Liquid Systems)

## 1. บทนำ (Introduction)

ระบบของเหลว-ของเหลวมักพบในกระบวนการสกัด (Extraction) และการทำอิมัลชัน (Emulsions) ความท้าทายหลักคือการจัดการกับ **อัตราส่วนความหนืด (\lambda = \mu_d/\mu_c)** และความตึงผิวที่ต่ำกว่าระบบ Gas-Liquid

---

## 2. การจำแนกหยดของเหลว (Droplet Classification)

### 2.1 หยดขนาดเล็ก ($Eo < 0.5$)
หยดมีลักษณะเป็นทรงกลมแข็ง (Rigid sphere) เนื่องจากแรงตึงผิวมีอิทธิพลสูง
- **Drag:** Schiller-Naumann
- **Lift:** Legendre-Magnaudet (พิจารณาอัตราส่วนความหนืด $\lambda$)

### 2.2 หยดที่ผิดรูป ($Eo > 0.5$)
หยดเริ่มเสียรูปเป็นทรงรีหรือเกิดการสั่นของรูปร่าง
- **Drag:** Grace Model (ออกแบบมาสำหรับหยดของเหลวโดยเฉพาะ)
- **Turbulence:** Simonin Model (จัดการปฏิสัมพันธ์ระหว่างความปั่นป่วนและหยดน้ำ)

---

## 3. แบบจำลองที่แนะนำ (Recommended Models)

### 3.1 แรงยก Legendre-Magnaudet
ในระบบของเหลว-ของเหลว สัมประสิทธิ์แรงยกขึ้นอยู่กับความหนืดภายในหยด:
$$C_L^{\text{inviscid}} = \frac{6}{\pi^2} \frac{(2 + \lambda)^2 + \lambda}{(1 + \lambda)^3} \tag{3.1}$$ 

### 3.2 การรวมตัวและการแตกตัว (PBM)
หากความเข้มข้นหยดสูง ต้องใช้ **Film Drainage Model** สำหรับการรวมตัว และ **Weber Number Model** สำหรับการแตกตัว:
$$We = \frac{\rho_c u_{rel}^2 d}{\sigma} \tag{3.2}$$ 
การแตกตัวมักเกิดขึ้นเมื่อ $We > 12$

---

## 4. การนำไปใช้ใน OpenFOAM

ตัวอย่างการตั้งค่าใน `phaseProperties` สำหรับระบบสกัดน้ำมัน-น้ำ:

```openfoam
phaseInteraction
{
    dragModel       Grace;
    liftModel       LegendreMagnaudet;
    virtualMassModel constant;
    
    LegendreMagnaudetCoeffs
    {
        lambda      0.8; // อัตราส่วนความหนืด น้ำมัน/น้ำ
    }
}
```

### ข้อควรพิจารณา:
ระบบของเหลว-ของเหลวมักมีอัตราส่วนความหนาแน่นใกล้เคียงกัน ($\approx 1:1$) ส่งผลให้การเชื่อมโยงความดัน-ความเร็ว (Pressure-Velocity Coupling) มีความเสถียรกว่าระบบ Gas-Liquid แต่ต้องระวังเรื่องการทำนายขนาดหยดที่แม่นยำผ่าน PBM

