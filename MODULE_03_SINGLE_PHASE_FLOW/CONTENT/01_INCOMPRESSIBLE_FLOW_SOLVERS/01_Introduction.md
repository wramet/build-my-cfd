# บทนำสู่ Incompressible Flow Solvers

## 🎯 ภาพรวม (Overview)

Incompressible flow solvers เป็นรากฐานสำคัญของการจำลองพลศาสตร์ของไหลเชิงคำนวณ (CFD) สำหรับสถานการณ์ที่ความหนาแน่นของของไหลคงที่ตลอดเวลาและพื้นที่ (\(\rho = \text{constant}\)) โมดูลนี้จะนำเสนอสมมติฐานทางกายภาพ สมการควบคุม และความท้าทายหลักในการแก้ปัญหาทางคณิตศาสตร์ใน OpenFOAM

---

## 🌊 1. สมมติฐานการไหลแบบอัดตัวไม่ได้ (Incompressibility Assumption)

**Incompressible flow** คือการไหลที่ความหนาแน่นของอนุภาคของไหลไม่เปลี่ยนแปลงตามการเคลื่อนที่:
\n$$\frac{D\rho}{Dt} = 0 \quad \Rightarrow \quad \rho = \text{constant}$$ 

### 1.1 เงื่อนไขที่ใช้ได้ (Validity Conditions)
สมมติฐานนี้เป็นจริงเมื่อ **Mach number** (\(Ma\)) มีค่าต่ำ:

$$Ma = \frac{|\mathbf{u}|}{c} < 0.3$$ 

โดยที่ \(c\) คือความเร็วเสียงในตัวกลาง

### 1.2 ข้อจำกัดทางกายภาพ (Physical Limitations)
สมมติฐานนี้จะ **ไม่สามารถใช้ได้** ในกรณีต่อไปนี้:
- **High-speed flows**: เมื่อ \(Ma > 0.3\) (ผลกระทบจากการอัดตัวมีนัยสำคัญ)
- **Acoustics**: ไม่สามารถจับคลื่นเสียงได้เนื่องจากความเร็วเสียงถือเป็นอนันต์ (\(c \to \infty\))
- **Significant Heating**: เมื่อมีการถ่ายเทความร้อนที่ทำให้ความหนาแน่นเปลี่ยนแปลงอย่างมาก (ต้องใช้ Solver ที่รองรับ Boussinesq approximation หรือ Compressible solver)

---

## 📐 2. สมการควบคุม (Governing Equations)

ภายใต้สมมติฐาน Incompressibility สมการ Navier-Stokes จะถูกปรับปรุงดังนี้:

### 2.1 สมการความต่อเนื่อง (Continuity Equation)
การอนุรักษ์มวลจะลดรูปเหลือเงื่อนไข Divergence-free ของสนามความเร็ว:

$$\nabla \cdot \mathbf{u} = 0$$ 

สมการนี้หมายความว่าอัตราการไหลเข้าสู่ปริมาตรควบคุมใดๆ จะต้องเท่ากับอัตราการไหลออกเสมอ

### 2.2 สมการโมเมนตัม (Momentum Equation)
สำหรับการไหลของของไหล Newtonian ที่มีความหนาแน่นและความหนืดคงที่:

$$\rho \left( \frac{\partial \mathbf{u}}{\partial t} + (\mathbf{u} \cdot \nabla) \mathbf{u} \right) = -\nabla p + \mu \nabla^2 \mathbf{u} + \mathbf{f}$$ 

**นิยามตัวแปร:**
- \(\mathbf{u}\): Velocity vector [m/s]
- \(p\): Static pressure [Pa]
- \(\rho\): Density [kg/m^3]
- \(\mu\): Dynamic viscosity [Pa \cdot s]
- \(\mathbf{f}\): External forces (เช่น แรงโน้มถ่วง) [N/m^3]

### 2.3 การวิเคราะห์ไร้มิติ (Dimensionless Analysis)
พารามิเตอร์ที่กำหนดพฤติกรรมการไหลคือ **Reynolds Number (\(Re\))**:

$$Re = \frac{\text{Inertial Forces}}{\text{Viscous Forces}} = \frac{\rho U L}{\mu} = \frac{U L}{\nu}$$ 

โดยที่ \(\nu = \mu/\rho\) คือ ความหนืดจลนศาสตร์ (Kinematic viscosity) [m^2/s]

---

## 🔗 3. ความท้าทาย: Pressure-Velocity Coupling

ในระบบ Incompressible, **ความดัน (\(p\))** ไม่ได้มีความสัมพันธ์โดยตรงกับความหนาแน่นผ่านสมการสถานะ (Equation of State) แต่ทำหน้าที่เป็นตัวแปรเพื่อบังคับให้สนามความเร็วเป็นไปตามสมการความต่อเนื่อง (\(\nabla \cdot \mathbf{u} = 0\)) 

**ความยากทางคณิตศาสตร์:**
1. ไม่มีสมการวิวัฒนาการ (Evolution equation) สำหรับความดันโดยเฉพาะ
2. ความดันปรากฏเฉพาะในรูปของ Gradient (\(-\nabla p\)) ในสมการโมเมนตัม
3. การเปลี่ยนแปลงความดันส่งผลต่อความเร็วทันทีทั่วทั้งโดเมน (\(c \to \infty\))

**OpenFOAM Implementation:**
OpenFOAM แก้ปัญหานี้โดยการสร้างสมการความดัน (Pressure Poisson Equation) จากการรวมสมการโมเมนตัมและสมการความต่อเนื่องเข้าด้วยกัน

---

## 📊 4. การเลือก Solver ตามระบอบการไหล

| สภาพการไหล | Solver แนะนำ | อัลกอริทึม |
|------------|--------------|-----------|
| Steady-state, Laminar/Turbulent | `simpleFoam` | SIMPLE |
| Transient, Laminar | `icoFoam` | PISO |
| Transient, Turbulent, Small \(\Delta t\) | `pisoFoam` | PISO |
| Transient, Turbulent, Large \(\Delta t\) | `pimpleFoam` | PIMPLE |

---

## ✅ แนวทางปฏิบัติที่ดีที่สุด (Best Practices)

1. **ตรวจสอบ Mach Number**: มั่นใจว่า \(Ma < 0.3\) ก่อนใช้ Incompressible solvers
2. **Mesh Quality**: คุณภาพของ Mesh (โดยเฉพาะ Orthogonality) ส่งผลอย่างมากต่อการคำนวณ Pressure Gradient
3. **Boundary Conditions**: ตรวจสอบความสอดคล้องของ BC ระหว่าง \(U\) และ \(p\) (เช่น `fixedValue` สำหรับ \(U\) มักใช้คู่กับ `zeroGradient` สำหรับ \(p\))

---
**Next Topic**: [Standard Solvers in OpenFOAM](./02_Standard_Solvers.md)
