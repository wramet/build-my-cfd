# Rhie-Chow Interpolation

**ทำไมต้องเข้าใจ Rhie-Chow Interpolation?**

บน collocated grid — ที่ velocity และ pressure ถูกเก็บไว้ที่ตำแหน่งเดียวกัน (cell centers) — การคำนวณ pressure gradient ด้วย linear interpolation ทั่วไปทำให้เกิดปัญหา **checkerboard oscillation** ซึ่ง:

- Pressure field แกว่ง (100, 0, 100, 0, ...) แต่ gradient เป็นศูนย์
- Solver มองไม่เห็นความแตกต่างระหว่าง cells ที่อยู่ติดกัน
- ส่งผลให้การคำนวณ diverge หรือให้ผลลัพธ์ที่ไม่เป็นไปตามฟิสิกส์

**Rhie-Chow interpolation** แก้ปัญหานี้ด้วยการเพิ่ม correction term ที่ทำให้ pressure gradient "มองเห็น" cells ข้างๆ ได้อย่างถูกต้อง — และใน OpenFOAM ถูก apply โดยอัตโนมัติผ่าน `fvc::flux()`

---

## Learning Objectives

หลังจากอ่านบทนี้ คุณควรจะสามารถ:

- **อธิบาย** ปัญหา checkerboard pressure บน collocated grid และสาเหตุที่เกิดขึ้น
- **วิเคราะห์** สมการ Rhie-Chow interpolation และ correction term ที่ใช้แก้ปัญหา
- **ระบุ** การนำไปใช้ใน OpenFOAM ผ่าน `fvc::flux()` และ pEqn.H
- **แก้ไข** ปัญหาความลู่เข้าที่เกิดจาก mesh ที่ไม่ตั้งฉากด้วย non-orthogonal correctors
- **เปรียบเทียบ** ข้อดีข้อเสียระหว่าง staggered grid และ collocated grid พร้อม Rhie-Chow

---

## Core Content

### 1. The Checkerboard Problem

#### Why It Happens

การคำนวณ pressure gradient ที่ cell1$P1จาก cells1$W1และ1$E1ด้วย central difference:

$$\left(\frac{\partial p}{\partial x}\right)_P \approx \frac{p_E - p_W}{2\Delta x}$$

ถ้า pressure field เป็นแบบ checkerboard:1$p = 100, 0, 100, 0, ...$

- ที่ cell1$P=21(p=0): gradient ≈ (100 - 100)/2Δx = 0
- ที่ cell1$P=31(p=100): gradient ≈ (0 - 0)/2Δx = 0

**แม้ว่า pressure จะต่างกันมาก แต่ gradient ที่คำนวณได้เป็นศูนย์!**

#### Visualization: Checkerboard Pattern

```
Checkerboard Pressure บน Collocated Grid

    p = 100    0    100    0    100    0
         ↓     ↓     ↓     ↓     ↓     ↓
    ┌─────┬─────┬─────┬─────┬─────┬─────┐
    │ 100 │  0  │ 100 │  0  │ 100 │  0  │
    ├─────┼─────┼─────┼─────┼─────┼─────┤
    │  0  │ 100 │  0  │ 100 │  0  │ 100 │
    ├─────┼─────┼─────┼─────┼─────┼─────┤
    │ 100 │  0  │ 100 │  0  │ 100 │  0  │
    ├─────┼─────┼─────┼─────┼─────┼─────┤
    │  0  │ 100 │  0  │ 100 │  0  │ 100 │
    └─────┴─────┴─────┴─────┴─────┴─────┘

Pressure gradient ระหว่าง Cell Centers (เช่น 100 → 0)
ถูกคำนวณโดยเฉลี่ยจาก cell ข้างๆ ซึ่งทำให้ Solver "มองไม่เห็น" ความแตกต่าง
เพราะ (100-0)/2 และ (0-100)/2 อาจ cancel กันเมื่อถูก average

→ ส่งผลให้ pressure field แกว่ง (oscillate) และไม่ลู่เข้า
```

#### Consequences

| Effect | Description |
|--------|-------------|
| Pressure oscillation | Field สลับค่าระหว่าง cells แต่ gradient = 0 |
| Solver divergence | Iterations ไม่ลู่เข้าระหว่าง p-U coupling |
| Non-physical results | Velocity field ผิดพลาดเนื่องจาก pressure ผิด |

---

### 2. Rhie-Chow Interpolation Formula

#### Mathematical Formulation

Rhie-Chow interpolation คำนวณ face velocity1$\mathbf{u}_f1จาก cell-centered velocities โดยเพิ่ม correction term:

$$\mathbf{u}_f = \overline{\mathbf{u}}_f - D_f \left[(\nabla p)_f - \overline{(\nabla p)}_f\right]$$

| Term | Meaning | Physical Interpretation |
|------|---------|------------------------|
|1$\overline{\mathbf{u}}_f1| Linear interpolation of1$\mathbf{u}1จาก cell centers | Base velocity estimate |
|1$D_f1|1$\overline{(1/a_P)}_f1— interpolated inverse diagonal coefficient | Pressure-velocity coupling strength |
|1$(\nabla p)_f1| Compact gradient at face (direct differentiation) | "True" pressure gradient |
|1$\overline{(\nabla p)}_f1| Interpolated gradient from cell centers | Smoothed gradient |

#### Key Insight

**Correction term = 0** เมื่อ pressure field smooth (เพราะ1$(\nabla p)_f \approx \overline{(\nabla p)}_f$)

**Correction term ≠ 0** เมื่อ pressure field มี oscillation → แก้ไข face velocity เพื่อให้ "มองเห็น" pressure difference

---

### 3. OpenFOAM Implementation

#### In pEqn.H

Rhie-Chow ถูก apply โดยอัตโนมัติเมื่อคำนวณ face flux:

```cpp
// 1. Reciprocal of diagonal coefficient
volScalarField rAU(1.0/UEqn.A());

// 2. H-operator (momentum excluding pressure gradient)
volVectorField HbyA(constrainHbyA(rAU*UEqn.H(), U, p));

// 3. Face flux with Rhie-Chow (implicit correction)
surfaceScalarField phiHbyA
(
    fvc::flux(HbyA)               // Rhie-Chow applied here!
  + fvc::interpolate(rAU)*fvc::ddtCorr(U, phi)
);

// 4. Pressure equation (Poisson)
fvScalarMatrix pEqn
(
    fvm::laplacian(rAU, p) == fvc::div(phiHbyA)
);
```

#### Code Mapping: Theory → OpenFOAM

| Mathematical Symbol | OpenFOAM Code | Description |
|---------------------|---------------|-------------|
|1$a_P1| `UEqn.A()` | Diagonal coefficient of U matrix |
|1$\mathbf{H}(\mathbf{u})1| `UEqn.H()` | Momentum equation excluding pressure |
|1$1/a_P1| `rAU` | Reciprocal diagonal coefficient |
| Face flux1$\phi_f1| `fvc::flux(HbyA)` | Rhie-Chow interpolated flux |

#### How It Works

1. `UEqn.A()` ดึง diagonal coefficients จาก momentum matrix
2. `rAU*UEqn.H()` คำนวณ intermediate velocity
3. `fvc::flux()` apply **Rhie-Chow correction** อัตโนมัติเมื่อ interpolate จาก cell → face

---

### 4. Non-Orthogonal Correction

#### The Challenge

สำหรับ mesh ที่ไม่ตั้งฉาก (non-orthogonal meshes):

- Face normal1$\mathbf{n}_f1ไม่ตรงกับ line ระหว่าง cell centers
- Laplacian term1$\nabla \cdot (D_f \nabla p)1มี error จาก non-orthogonality
- ต้องการ iterative correction

#### OpenFOAM Solution

ใน `fvSolution`:

```cpp
PIMPLE
{
    nNonOrthogonalCorrectors 2;  // เพิ่มถ้า mesh quality แย่
}
```

ใน `pEqn.H` loop:

```cpp
for (int nonOrth = 0; nonOrth <= nNonOrthCorr; nonOrth++)
{
    fvScalarMatrix pEqn
    (
        fvm::laplacian(rAU, p) == fvc::div(phiHbyA)
    );
    
    pEqn.solve();
    
    // Update flux เฉพาะ iteration สุดท้าย
    if (nonOrth == nNonOrthCorr)
        phi = phiHbyA - pEqn.flux();
}
```

#### Guidelines

| Mesh Quality | nNonOrthCorr | Notes |
|--------------|--------------|-------|
| Excellent (< 30°) | 0 | Non-orthogonality ต่ำ |
| Good (30-50°) | 1 | Default สำหรับ meshes ส่วนใหญ่ |
| Fair (50-70°) | 2-3 | Meshes ที่ซับซ้อน |
| Poor (> 70°) | 3+ + improve mesh | ควร improve mesh ก่อน |

---

### 5. Troubleshooting Guide

#### Common Problems

| Problem | Symptom | Diagnosis | Solution |
|---------|---------|-----------|----------|
| Checkerboard | Oscillating p field, high residuals | Visualize pressure — สลับค่า checkerboard | Check mesh quality; verify Rhie-Chow active |
| Slow convergence | Residuals ลดช้ามาก | ตรวจ nNonOrthCorr settings | Increase nNonOrthogonalCorrectors |
| Divergence | Solver fails ระหว่าง iterations | Check mesh orthogonality | Improve mesh; increase correctors temporarily |
| Mass imbalance |1$\sum \phi_f \neq 01| ตรวจ flux correction | Ensure `phi = phiHbyA - pEqn.flux()` after loop |

#### Mesh Quality Check

```bash
checkMesh -allGeometry
```

| Metric | Target | Action |
|--------|--------|--------|
| Non-orthogonality angle | < 70° | Increase nNonOrthCorr if 50-70° |
| Skewness | < 2 | Improve mesh if > 2 |
| Aspect ratio | < 1000 | Improve mesh if extreme |

---

### 6. Comparison: Staggered vs Collocated Grids

#### Fundamental Differences

| Aspect | Staggered Grid | Collocated Grid + Rhie-Chow |
|--------|----------------|----------------------------|
| Variable storage | U at faces, p at centers | Both U and p at centers |
| Checkerboard | No (by design) | Requires Rhie-Chow correction |
| Code complexity | High (multiple data types) | Low (single data type) |
| Unstructured mesh | Difficult to implement | Natural fit |
| Accuracy | Same (2nd order) | Same (2nd order) |
| OpenFOAM use | Rare | Standard |

#### Why OpenFOAM Uses Collocated

1. **Flexibility:** Unstructured meshes ได้ง่าย
2. **Simplicity:** Single data structure สำหรับทุก fields
3. **Efficiency:** Rhie-Chow correction มี overhead น้อย
4. **Generality:** Support complex geometries ได้ดีกว่า

ดูรายละเอียดเพิ่มเติมเกี่ยวกับ discretization foundation ใน [01_Mathematical_Foundation.md](01_Mathematical_Foundation.md)

---

### 7. Concept Check

<details>
<summary><b>1. Staggered grid ทำไมไม่มีปัญหา Checkerboard?</b></summary>

บน staggered grid, velocity components ถูกเก็บไว้ที่ face centers และ pressure อยู่ที่ cell centers → pressure gradient ใช้ pressure จาก cells ทั้งสองข้างของ face โดยตรง (เช่น1$p_P - p_E$) ไม่มีการ "กระโดด" ข้าม cell → ไม่มีจุดบอดที่ gradient เป็นศูนย์เมื่อ pressure oscillate
</details>

<details>
<summary><b>2. ใน OpenFOAM, ฟังก์ชันใดใช้ Rhie-Chow correction?</b></summary>

`fvc::flux(HbyA)` — เมื่อคำนวณ face flux จาก cell-centered volume field, OpenFOAM ใช้ Rhie-Chow interpolation โดยอัตโนมัติเพื่อป้องกัน checkerboard ซึ่งรวม correction term1$-D_f[(\nabla p)_f - \overline{(\nabla p)}_f]1เข้าใน flux calculation
</details>

<details>
<summary><b>3. nNonOrthogonalCorrectors ช่วยอะไรใน pressure equation?</b></summary>

Non-orthogonal correctors แก้ไข error จาก mesh ที่ไม่ตั้งฉาก — เมื่อ face normal ไม่ตรงกับ line ระหว่าง cell centers, Laplacian term1$\nabla \cdot (D_f \nabla p)1มี error ซึ่ง iterative corrections ช่วยลด โดยแต่ละ iteration ปรับปรุง pressure solution และ flux เพื่อลด non-orthogonality effects
</details>

<details>
<summary><b>4. Correction term ใน Rhie-Chow เมื่อไหร่จะเป็นศูนย์?</b></summary>

Correction term1$-D_f[(\nabla p)_f - \overline{(\nabla p)}_f]1เป็นศูนย์เมื่อ pressure field smooth — เพราะ1$(\nabla p)_f1(gradient at face) และ1$\overline{(\nabla p)}_f1(interpolated gradient from cells) จะเท่ากันเมื่อ pressure เปลี่ยนแบบ linear ไม่มี oscillation → Rhie-Chow ไม่กระทบ smooth solutions
</details>

---

## Key Takeaways

- **Checkerboard problem:** Linear interpolation บน collocated grid ทำให้ pressure gradient "มองไม่เห็น" cells ข้างๆ → oscillation
- **Rhie-Chow solution:** Correction term1$-D_f[(\nabla p)_f - \overline{(\nabla p)}_f]1couples p กับ U อย่างถูกต้อง
- **OpenFOAM:** `fvc::flux(HbyA)` apply Rhie-Chow โดยอัตโนมัติ — ไม่ต้อง implement เอง
- **Non-orthogonal meshes:** Use `nNonOrthogonalCorrectors` เพื่อ iterative correction เมื่อ mesh quality ไม่ดี
- **Mesh quality:** Non-orthogonality < 70° และ skewness < 2 สำหรับ convergence ที่ดี
- **Collocated vs Staggered:** OpenFOAM ใช้ collocated + Rhie-Chow เพราะ flexibility และ simplicity สำหรับ unstructured meshes

---

## Related Documents

- **บทก่อนหน้า:** [03_PISO_and_PIMPLE_Algorithms.md](03_PISO_and_PIMPLE_Algorithms.md) — Rhie-Chow ใช้ภายใน PISO/PIMPLE loops
- **บทถัดไป:** [05_Algorithm_Comparison.md](05_Algorithm_Comparison.md) — เปรียบเทียบ solvers และ algorithms
- **Mathematical Foundation:** [01_Mathematical_Foundation.md](01_Mathematical_Foundation.md) — Discretization background