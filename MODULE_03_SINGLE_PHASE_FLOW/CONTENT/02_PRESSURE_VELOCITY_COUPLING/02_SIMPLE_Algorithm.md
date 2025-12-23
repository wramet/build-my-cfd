# อัลกอริทึม SIMPLE (Semi-Implicit Method for Pressure-Linked Equations)

## 🎯 วัตถุประสงค์ (Purpose) 

**อัลกอริทึม SIMPLE** ถูกออกแบบมาเพื่อหาผลเฉลยของสนามความดันและความเร็วใน **สภาวะคงที่ (Steady-state)** พัฒนาโดย Patankar และ Spalding (1972) อัลกอริทึมนี้เป็นหัวใจสำคัญของ Solver เช่น `simpleFoam` ใน OpenFOAM

---

## 📐 1. ขั้นตอนการทำงานของ SIMPLE Algorithm

กระบวนการวนซ้ำ (Iterative Process) มีขั้นตอนดังนี้:

1. **ทำนายโมเมนตัม (Momentum Prediction)**:
   แก้สมการโมเมนตัมโดยใช้สนามความดันชั่วคราว ($p^*$) จากรอบก่อนหน้า เพื่อหาความเร็วชั่วคราว ($\\mathbf{u}^*$):
   $$a_P \\mathbf{u}^* = \\mathbf{H}(\\mathbf{u}^*) - \\nabla p^* \\tag{1.1}$$ 

2. **แก้สมการการแก้ไขความดัน (Pressure Correction)**:
   สร้างและแก้สมการ Poisson สำหรับ $p'$ (Pressure correction):
   $$\\nabla \\cdot \\left( \\frac{1}{a_P} \\nabla p' \\right) = \\nabla \\cdot \\mathbf{u}^* \\tag{1.2}$$ 

3. **แก้ไขความดันและความเร็ว (Field Update)**:
   อัปเดตสนามตัวแปรโดยใช้ $p'$:
   $$p = p^* + \\alpha_p p' \\tag{1.3}$$ 
   $$\\mathbf{u} = \\mathbf{u}^* - \\frac{1}{a_P} \\nabla p' \\tag{1.4}$$ 

4. **Under-Relaxation**:
   ใช้ค่า $\\alpha$ เพื่อหน่วงการเปลี่ยนแปลงของคำตอบ ป้องกันการลู่ออก (Divergence) 

5. **ตรวจสอบการลู่เข้า (Convergence Check)**:
   ตรวจสอบค่า Residuals หากต่ำกว่าเกณฑ์ (เช่น $10^{-6}$) ให้จบการทำงาน

---

## 🔧 2. การควบคุมความเสถียร (Under-Relaxation)

เนื่องจาก SIMPLE เป็นอัลกอริทึมแบบ Segregated การอัปเดตค่าที่เร็วเกินไปอาจทำให้ระบบไม่เสถียร OpenFOAM ใช้การปรับแต่งใน `fvSolution`:

```cpp
relaxationFactors
{
    fields
    {
        p               0.3;    // แรงดันต้องการการหน่วงที่สูง
    }
    equations
    {
        U               0.7;    // ความเร็ว
        "(k|epsilon|omega)" 0.7;
    }
}
```

**สูตรทางคณิตศาสตร์:**
$$\\phi^{new} = \\phi^{old} + \\alpha (\\phi^* - \\phi^{old})$$
โดยที่ $\\phi^*$ คือค่าที่คำนวณได้ใหม่ในรอบนั้น

---

## 💻 3. OpenFOAM Source Code ตัวอย่าง

ตัวอย่างโครงสร้างลูปใน `simpleFoam.C`:

```cpp
while (simple.loop())
{
    // 1. Momentum Predictor
    tmp<fvVectorMatrix> tUEqn
    (
        fvm::div(phi, U) + turbulence->divDevReff(U)
    );
    fvVectorMatrix& UEqn = tUEqn.ref();
    UEqn.relax();
    solve(UEqn == -fvc::grad(p));

    // 2. Pressure Correction
    volScalarField rAU(1.0/UEqn.A());
    surfaceScalarField phiHbyA("phiHbyA", fvc::flux(rAU*UEqn.H()));
    
    while (simple.correctNonOrthogonal())
    {
        fvScalarMatrix pEqn
        (
            fvm::laplacian(rAU, p) == fvc::div(phiHbyA)
        );
        pEqn.solve();
        if (simple.finalNonOrthogonalIter())
        {
            phi = phiHbyA - pEqn.flux();
        }
    }

    // 3. Velocity Correction
    U = HbyA - rAU*fvc::grad(p);
    U.correctBoundaryConditions();
}
```

---

## 📊 4. ข้อดีและข้อจำกัดของ SIMPLE

| ข้อดี (Advantages) | ข้อจำกัด (Limitations) |
|-------------------|----------------------|
| แข็งแกร่ง (Robust) สำหรับปัญหาคงตัว | ไม่เหมาะสำหรับปัญหาชั่วคร่าว (Transient) |
| ใช้หน่วยความจำน้อย | ต้องปรับแต่ง Relaxation Factors อย่างระมัดระวัง |
| ลู่เข้าสู่คำตอบสุดท้ายได้แน่นอน | อัตราการลู่เข้าช้ากว่าแบบ Coupled |

---
**หัวข้อถัดไป**: [อัลกอริทึม PISO และ PIMPLE สำหรับ Transient](./03_PISO_and_PIMPLE_Algorithms.md)
