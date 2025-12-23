# รายละเอียดการนำไปใช้ใน OpenFOAM (OpenFOAM Implementation)

## 1. ลำดับชั้นของคลาส (Class Hierarchy) 

OpenFOAM จัดการแรงมวลเสมือนผ่านระบบคลาสที่มีความยืดหยุ่น โดยมีคลาสพื้นฐานคือ `virtualMassModel` ซึ่งช่วยให้เลือกโมเดลที่ต้องการได้ขณะรันโปรแกรม

### โครงสร้างคลาสใน C++
```cpp
class virtualMassModel
{
public:
    // คำนวณสัมประสิทธิ์มวลเสมือน (Cvm)
    virtual tmp<volScalarField> Cvm() const = 0;

    // คำนวณแรงมวลเสมือนต่อหน่วยปริมาตร (Fi)
    virtual tmp<volVectorField> Fi() const = 0;
};
```

---

## 2. การคำนวณใน Solver (Numerical Workflow)

ใน Solver เช่น `multiphaseEulerFoam`, แรงมวลเสมือนคำนวณจากความแตกต่างของอนุพันธ์รวม (Material Derivative) ของความเร็วทั้งสองเฟส:

### 2.1 การคำนวณอนุพันธ์รวม
$$\frac{D\mathbf{u}}{Dt} = \frac{\partial \mathbf{u}}{\partial t} + \mathbf{u} \cdot \nabla \mathbf{u}$$ 

ในโค้ด OpenFOAM:
```cpp
volVectorField DUDt1 = fvc::ddt(U1) + fvc::div(U1, U1);
volVectorField DUDt2 = fvc::ddt(U2) + fvc::div(U2, U2);
```

### 2.2 การรวมแรงเข้ากับสมการโมเมนตัม
$$\mathbf{F}_{vm} = C_{vm} \rho_1 \alpha_1 \alpha_2 (DUDt_2 - DUDt_1)$$

---

## 3. ข้อควรพิจารณาด้านเสถียรภาพ (Numerical Stability)

เนื่องจากเทอมความเร่ง ($\partial \mathbf{u}/\partial t$) มักจะ "แข็ง" (Stiff) และอาจนำไปสู่การแกว่งกวัด (Oscillations) OpenFOAM จึงใช้กลยุทธ์ดังนี้:

### 3.1 การจัดการแบบ Implicit (`fvm::Sp`)
เพื่อเพิ่มความเป็นแนวทแยง (Diagonal dominance) ของเมทริกซ์โมเมนตัม:
```cpp
U1Eqn += fvm::Sp(Cvm*rho1*alpha1*alpha2/dt, U1);
```

### 3.2 ข้อจำกัดของ Time Step (CFL Constraint)
แรงมวลเสมือนเพิ่มความเร็วเสียงประสิทธิผล (Effective sound speed) ในระบบ ซึ่งอาจต้องการ Time step ที่เล็กลง:
$$\Delta t \leq \frac{\Delta x}{|\mathbf{u}| + \sqrt{\frac{C_{vm} \rho_c}{\rho_d + C_{vm} \rho_c}}}$$ 

---

## 4. การตั้งค่าใน `phaseProperties`

ตัวอย่างการตั้งค่าโมเดลสัมประสิทธิ์คงที่:

```openfoam
virtualMass
(
    (air in water)
    {
        type            constantCoefficient;
        Cvm             0.5;
    }
);
```

การจัดการแรงมวลเสมือนอย่างถูกต้องเป็นกุญแจสำคัญสู่ความเสถียรเชิงตัวเลขในการจำลองระบบ Gas-Liquid ที่มีความเร่งสูง
