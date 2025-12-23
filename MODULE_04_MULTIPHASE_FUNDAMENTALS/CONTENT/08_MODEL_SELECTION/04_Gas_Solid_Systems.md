# ระบบก๊าซ-ของแข็ง (Gas-Solid Systems)

## 1. บทนำ (Introduction) 

ระบบก๊าซ-ของแข็งพบได้บ่อยในกระบวนการทางอุตสาหกรรม เช่น เตาเผาฟลูอิไดซ์เบด (Fluidized Beds) และการขนส่งผงทางท่อ พฤติกรรมหลักถูกกำหนดโดยการชนกันของอนุภาค (Particle collisions) และแรงต้านทานจากก๊าซ

---

## 2. การจำแนกตามความเข้มข้น (Regime Classification)

### 2.1 การไหลแบบเจือจาง (Dilute Flow, $\alpha_s < 0.1$)
อนุภาคอยู่ห่างกันมาก ปฏิสัมพันธ์ระหว่างอนุภาคน้อย
- **Drag:** Wen-Yu Model (ออกแบบมาสำหรับก๊าซ-ของแข็งเจือจาง)
- **Turbulence:** การเคลื่อนที่ของอนุภาคสามารถเพิ่มหรือลดความปั่นป่วนของก๊าซได้

### 2.2 การไหลแบบหนาแน่น (Dense Flow, $\alpha_s > 0.1$)
การชนกันของอนุภาคมีความสำคัญมาก ต้องใช้ **Kinetic Theory of Granular Flow (KTGF)** เพื่อคำนวณความเครียดของของแข็ง (Solid stress)
- **Drag:** Gidaspow Model (รวม Wen-Yu และ Ergun เข้าด้วยกัน)
- **Solid Pressure:** คำนวณจาก Granular Temperature ($\Theta$)

---

## 3. แบบจำลองที่แนะนำ (Recommended Models)

### 3.1 แรงฉุด Gidaspow Model
เป็นโมเดลที่เสถียรที่สุดสำหรับระบบที่ความเข้มข้นเปลี่ยนแปลงกว้าง:
- หาก $\alpha_g > 0.8$: ใช้ Wen-Yu
- หาก $\alpha_g \leq 0.8$: ใช้ Ergun Equation

### 3.2 ทฤษฎีจลน์ (KTGF)
ใช้ในการคำนวณความหนืดประสิทธิผลของอนุภาค:
$$ \mu_s = \mu_{s,coll} + \mu_{s,kin} + \mu_{s,fric} \tag{4.1} $$

---

## 4. การนำไปใช้ใน OpenFOAM

ตัวอย่างการตั้งค่าใน `phaseProperties` สำหรับระบบ Fluidized Bed:

```openfoam
solid
{
    type            solidPhase;
    kineticTheoryModel Gidaspow;
    
    kineticTheoryCoeffs
    {
        restitutionCoeff    0.9;
        frictionCoeff       0.05;
    }
}

phaseInteraction
{
    dragModel       Gidaspow;
}
```

### พารามิเตอร์วิกฤต:
ในระบบ Gas-Solid ค่า **Restitution Coefficient ($e$)** มีผลอย่างมากต่อความสูงของเตียง (Bed expansion) โดยทั่วไปมีค่าระหว่าง 0.8 - 0.95

```
