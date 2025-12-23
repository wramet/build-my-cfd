# Standard Incompressible Flow Solvers ใน OpenFOAM

โมดูลนี้ลงรายละเอียดเกี่ยวกับ Solver มาตรฐานที่ใช้สำหรับจำลองการไหลแบบอัดตัวไม่ได้ (incompressible flow) ใน OpenFOAM โดยเน้นที่ความแตกต่างของอัลกอริทึมและการนำไปใช้งานจริง

---

## 🚀 1. ภาพรวมของ Core Solvers

| Solver | ชนิดการไหล (Flow Type) | Algorithm | คุณสมบัติเด่น |
|--------|-----------------------|-----------|--------------|
| **icoFoam** | Transient Laminar | PISO | เรียบง่าย, สำหรับ Re ต่ำ, ไม่รองรับ Turbulence |
| **simpleFoam** | Steady-state Turbulent | SIMPLE | สำหรับปัญหาคงตัว, มีระบบ Under-relaxation |
| **pimpleFoam** | Transient Turbulent | PIMPLE | เสถียรสูง, รองรับ Time-step ขนาดใหญ่ ($Co > 1$) |
| **nonNewtonianIcoFoam** | Transient Non-Newtonian | PISO | ความหนืดแปรผันตามอัตราการเฉือน (Shear rate) |
| **SRFSimpleFoam** | Steady Rotating Frame | SIMPLE | สำหรับเครื่องจักรกลหมุน (Single Rotating Reference Frame) |

---

## ❄️ 2. icoFoam: Transient Laminar Flow

`icoFoam` เป็น Solver ที่ง่ายที่สุดใน OpenFOAM ใช้สำหรับจำลองการไหลแบบ Laminar ที่ขึ้นกับเวลา โดยไม่มีการรวมผลของ Turbulence

### 2.1 PISO Algorithm (Pressure-Implicit with Splitting of Operators)
ใช้วิธีการแก้ปัญหาแบบ Predictor-Corrector:
1. **Predictor Step**: แก้สมการโมเมนตัมหาความเร็วคาดการณ์ ($\\mathbf{u}^*$) โดยใช้ความดันเก่า
2. **Corrector Loop**: แก้สมการความดัน (Pressure Equation) และอัปเดตความเร็วเพื่อให้เป็นไปตามเงื่อนไข Divergence-free ($\\nabla \\cdot \\mathbf{u} = 0$)

### 2.2 OpenFOAM Implementation Code
```cpp
while (runTime.loop())
{
    // Momentum predictor
    fvVectorMatrix UEqn
    (
        fvm::ddt(U) + fvm::div(phi, U) - fvm::laplacian(nu, U)
    );
    solve(UEqn == -fvc::grad(p));

    // PISO corrector loop
    for (int corr=0; corr<nCorr; corr++)
    {
        volScalarField rAU = 1.0/UEqn.A();
        fvScalarMatrix pEqn
        (
            fvm::laplacian(rAU, p) == fvc::div(phi)
        );
        pEqn.solve();
        
        // Velocity correction
        U -= rAU*fvc::grad(p);
        U.correctBoundaryConditions();
    }
}
```

---

## 🌪️ 3. simpleFoam: Steady-State Turbulent Flow

`simpleFoam` ใช้สำหรับหาผลเฉลยที่สภาวะคงตัว (Steady-state) โดยรวมผลของความปั่นป่วน (Turbulence) ผ่านแบบจำลอง RANS

### 3.1 SIMPLE Algorithm (Semi-Implicit Method for Pressure-Linked Equations)
ลักษณะสำคัญคือการใช้ **Under-Relaxation** เพื่อลดการแกว่งของคำตอบและเพิ่มเสถียรภาพ:
$$\\phi^{n+1} = \\phi^n + \\alpha (\\phi^{new} - \\phi^n)$$
โดย $\\alpha$ คือ relaxation factor (โดยทั่วไป $\\alpha_p=0.3, \\alpha_U=0.7$)

### 3.2 OpenFOAM Implementation Code
```cpp
while (simple.loop())
{
    // Momentum equation with under-relaxation
    tmp<fvVectorMatrix> UEqn
    (
        fvm::div(phi, U) + turbulence->divDevReff(U)
    );
    UEqn().relax();
    solve(UEqn() == -fvc::grad(p));

    // Pressure correction
    pEqn = fvm::laplacian(UEqn().A(), p) == fvc::div(UEqn().flux());
    pEqn.solve();

    // Velocity correction
    U -= UEqn().H()/UEqn().A()*fvc::grad(p);
    U.correctBoundaryConditions();
}
```

---

## 🔄 4. pimpleFoam: Robust Transient Turbulent Flow

`pimpleFoam` รวมข้อดีของ PISO (Temporal Accuracy) และ SIMPLE (Stability) เข้าด้วยกัน ทำให้สามารถใช้ Time-step ขนาดใหญ่ได้โดยไม่สูญเสียความเสถียร

### 4.1 PIMPLE Algorithm Characteristics
- **Outer Correctors**: อนุญาตให้ทำซ้ำขั้นตอนทั้งหมดภายในหนึ่ง Time-step (คล้าย SIMPLE loops ในหนึ่งก้าวเวลา)
- **Stability**: ใช้ Under-relaxation ภายใน Time-step ได้ ทำให้รันที่ค่า Courant Number ($Co$) สูงกว่า 1 ได้อย่างปลอดภัย

### 4.2 Configuration (`system/fvSolution`)
```cpp
PIMPLE
{
    nOuterCorrectors 2;    // จำนวนรอบ SIMPLE ภายในหนึ่ง Time-step
    nCorrectors      2;    // จำนวนรอบ PISO
    nNonOrthogonalCorrectors 0;
}
```

---

## 📋 5. แนวทางการเลือก Solver (Solver Selection Guide)

| สถานการณ์ | Solver แนะนำ | เหตุผล |
|-----------|-------------|---------|
| **Low Re, Transient** | `icoFoam` | เรียบง่ายและแม่นยำสำหรับ Laminar |
| **Steady Aerodynamics** | `simpleFoam` | ประสิทธิภาพสูงสุดสำหรับสภาวะคงที่ |
| **Large Time-step Transient** | `pimpleFoam` | รันได้เร็วและเสถียรที่ Co > 1 |
| **Rotating Pump/Fan** | `SRFSimpleFoam` | รองรับพจน์แรงเหวี่ยงหนีศูนย์กลางและ Coriolis |

---
**Next Topic**: [Simulation Control and Management](./03_Simulation_Control.md)
