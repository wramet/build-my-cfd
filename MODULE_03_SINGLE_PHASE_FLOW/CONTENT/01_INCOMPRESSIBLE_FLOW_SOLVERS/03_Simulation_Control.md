# การควบคุมและการจัดการการจำลอง (Simulation Control and Management)

การรันการจำลองที่ประสบความสำเร็จใน OpenFOAM ไม่ได้ขึ้นอยู่กับ Solver ที่เลือกเท่านั้น แต่ยังรวมถึงการตั้งค่าพารามิเตอร์เชิงตัวเลขและการตรวจสอบการลู่เข้าอย่างเป็นระบบ

---

## 🏗️ 1. โครงสร้าง Directory ของ Case

Case ของ OpenFOAM ต้องมีโครงสร้างที่เป็นมาตรฐานเพื่อให้ Solver เข้าถึงข้อมูลได้ถูกต้อง:

```bash
incompressibleCase/
├── 0/                       # Boundary & Initial Conditions
│   ├── U                   # Velocity [m/s]
│   ├── p                   # Pressure [m²/s²] (สำหรับ incompressible คือ p/rho)
│   └── (k, epsilon, omega)  # Turbulence quantities
├── constant/                # Physical & Mesh Data
│   ├── polyMesh/           # Mesh topology
│   ├── transportProperties # nu (kinematic viscosity)
│   └── turbulenceProperties # Turbulence model selection
└── system/                  # Numerical Control
    ├── controlDict         # Time/Output control
    ├── fvSchemes           # Discretization schemes
    └── fvSolution          # Solver settings & algorithms
```

---

## ⚙️ 2. การควบคุมหลัก (`system/controlDict`)

ไฟล์ `controlDict` ทำหน้าที่กำหนดช่วงเวลาการคำนวณและความถี่ในการเขียนไฟล์ผลลัพธ์:

```cpp
application     simpleFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         1000;
deltaT          1;

writeControl    timeStep;
writeInterval   100;
purgeWrite      3;              // เก็บไฟล์ผลลัพธ์ล่าสุดไว้เพียง 3 ไฟล์
runTimeModifiable true;         // อนุญาตให้แก้ไขค่าในไฟล์ขณะรันอยู่ได้
```

---

## 🔧 3. การตั้งค่าความละเอียดเชิงตัวเลข (`system/fvSolution`)

### 3.1 Linear Solvers
OpenFOAM แก้ระบบสมการ $Ax=b$ โดยใช้ Linear Solvers ที่แตกต่างกันตามประเภทของสมการ:
- **p (Pressure)**: แนะนำใช้ **GAMG** (Geometric-Algebraic Multigrid) เพื่อการลู่เข้าที่รวดเร็ว
- **U (Velocity)**: แนะนำใช้ **PBiCGStab** หรือ **smoothSolver**

### 3.2 Under-Relaxation (สำหรับ SIMPLE)
เพื่อรักษาความเสถียรใน `simpleFoam` จำเป็นต้องใช้ relaxation factors:
```cpp
relaxationFactors
{
    fields
    {
        p               0.3;
    }
    equations
    {
        U               0.7;
        "(k|epsilon|omega)" 0.7;
    }
}
```

---

## 🔄 4. การตรวจสอบการลู่เข้า (Convergence Monitoring)

### 4.1 Residual Analysis
**Residual** คือตัววัดความไม่สมดุลของสมการเชิงตัวเลข $\| Ax - b \|$:
- **Initial Residual**: ค่าก่อนเริ่มแก้ในแต่ละ Iteration
- **Final Residual**: ค่าหลังจาก Solver ทำงานเสร็จในรอบนั้น

**เกณฑ์แนะนำ:**
- แรงดัน ($p$): $10^{-6}$ ถึง $10^{-7}$
- ความเร็ว ($U$): $10^{-7}$ ถึง $10^{-8}$

### 4.2 Physical Quantity Monitoring
นอกเหนือจาก Residual ควรติดตามปริมาณทางกายภาพผ่าน `functions` ใน `controlDict`:
```cpp
functions
{
    forces
    {
        type            forces;
        libs            (fieldFunctionObjects);
        patches         (walls);
        rho             rhoInf;
        rhoInf          1.225;
        writeControl    timeStep;
        writeInterval   1;
    }
}
```

---

## 🛠️ 5. แนวทางปฏิบัติที่ดีที่สุด (Best Practices)

1. **เริ่มต้นจากสิ่งง่ายๆ**: ใช้ Scheme อันดับหนึ่ง (เช่น `upwind`) ในช่วงแรกเพื่อให้การจำลองเสถียร แล้วจึงเปลี่ยนเป็นอันดับสอง (เช่น `linearUpwind`) เพื่อความแม่นยำ
2. **Check Mesh**: รัน `checkMesh` เสมอก่อนเริ่มจำลอง เพื่อตรวจสอบ **Non-orthogonality** (> 70° มักทำให้เกิดปัญหา)
3. **ตรวจสอบสมดุลมวล**: ตรวจสอบค่า `time step continuity errors` ในไฟล์ Log ค่ารวม (Cumulative) ควรมีค่าน้อยมาก

---
**จบเนื้อหาโมดูล Incompressible Flow Solvers**