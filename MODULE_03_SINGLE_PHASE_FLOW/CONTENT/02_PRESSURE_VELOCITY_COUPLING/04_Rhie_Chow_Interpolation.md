# Rhie-Chow Interpolation

การป้องกัน Checkerboard Pressure บน Collocated Grid

---

## Overview

**ปัญหา:** บน collocated grid การใช้ linear interpolation ทำให้ pressure gradient "มองไม่เห็น" cell ที่อยู่ติดกัน → **Checkerboard oscillation**

**Rhie-Chow** เพิ่ม correction term เพื่อ couple p กับ U อย่างถูกต้อง — **ถูกใช้โดยอัตโนมัติ** ใน OpenFOAM ผ่าน `fvc::flux()`

---

## 1. The Checkerboard Problem

### Why It Happens

การคำนวณ $\nabla p$ ที่ cell $P$ จาก cells $W$ และ $E$:

$$\left(\frac{\partial p}{\partial x}\right)_P \approx \frac{p_E - p_W}{2\Delta x}$$

ถ้า $p = 10, 0, 10, 0, ...$ → gradient = 0 (ผิด!)

### Visualization: Checkerboard Pattern

```
ตัวอย่าง Checkerboard Pressure บน Collocated Grid

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

Gradient ระหว่าง Cell ที่อยู่ติดกัน (เช่น 100 → 0 หรือ 0 → 100)
จะถูกคำนวณโดยเฉลี่ยจาก cell ข้างๆ ซึ่งอาจทำให้ Solver "มองไม่เห็น" ความแตกต่าง

→ ส่งผลให้ pressure field แกว่ง (oscillate) และไม่ลู่เข้า
```

### Consequence

- Pressure field oscillates
- Solver diverges
- Non-physical results

---

## 2. Rhie-Chow Formula

$$\mathbf{u}_f = \overline{\mathbf{u}}_f - D_f \left[(\nabla p)_f - \overline{(\nabla p)}_f\right]$$

| Term | Meaning |
|------|---------|
| $\overline{\mathbf{u}}_f$ | Linear interpolation of $\mathbf{u}$ |
| $D_f$ | $\overline{(1/a_P)}_f$ |
| $(\nabla p)_f$ | Gradient at face (compact) |
| $\overline{(\nabla p)}_f$ | Interpolated gradient from cells |

**Key Insight:** Correction term = 0 เมื่อ pressure field smooth

---

## 3. OpenFOAM Implementation

### In pEqn.H

```cpp
// 1. Reciprocal of diagonal coefficient
volScalarField rAU(1.0/UEqn.A());

// 2. H-operator (momentum excluding pressure)
volVectorField HbyA(constrainHbyA(rAU*UEqn.H(), U, p));

// 3. Face flux with Rhie-Chow (implicit)
surfaceScalarField phiHbyA
(
    fvc::flux(HbyA)               // Rhie-Chow applied here
  + fvc::interpolate(rAU)*fvc::ddtCorr(U, phi)
);

// 4. Pressure equation
fvScalarMatrix pEqn
(
    fvm::laplacian(rAU, p) == fvc::div(phiHbyA)
);
```

### Code Mapping

| Theory | OpenFOAM |
|--------|----------|
| $a_P$ | `UEqn.A()` |
| $\mathbf{H}(\mathbf{u})$ | `UEqn.H()` |
| $1/a_P$ | `rAU` |
| Face flux | `fvc::flux(HbyA)` |

---

## 4. Non-Orthogonal Correction

สำหรับ mesh ที่ไม่ตั้งฉาก:

```cpp
// fvSolution
PIMPLE
{
    nNonOrthogonalCorrectors 2;  // เพิ่มถ้า mesh แย่
}
```

```cpp
// pEqn.H loop
for (int nonOrth = 0; nonOrth <= nNonOrthCorr; nonOrth++)
{
    fvScalarMatrix pEqn(fvm::laplacian(rAU, p) == fvc::div(phiHbyA));
    pEqn.solve();
    
    if (nonOrth == nNonOrthCorr)
        phi = phiHbyA - pEqn.flux();
}
```

---

## 5. Troubleshooting

| Problem | Symptom | Solution |
|---------|---------|----------|
| Checkerboard | Oscillating p field | Check mesh quality |
| Slow convergence | High residuals | Increase nNonOrthCorr |
| Divergence | Solver fails | Improve mesh orthogonality |

### Mesh Quality Check

```bash
checkMesh -allGeometry
```

| Metric | Target |
|--------|--------|
| Non-orthogonality | < 70° |
| Skewness | < 2 |

---

## 6. Comparison: Staggered vs Collocated

| Aspect | Staggered | Collocated + Rhie-Chow |
|--------|-----------|------------------------|
| Checkerboard | No (by design) | Requires correction |
| Code complexity | High | Low |
| Unstructured mesh | Difficult | Easy |
| Accuracy | Same | Same |

---

## Concept Check

<details>
<summary><b>1. Staggered grid ทำไมไม่มีปัญหา Checkerboard?</b></summary>

เพราะ velocity อยู่ที่ face และ pressure อยู่ที่ cell center → pressure gradient ใช้ cells ทั้งสองข้างของ face โดยตรง ไม่มี "จุดบอด"
</details>

<details>
<summary><b>2. ใน OpenFOAM, ฟังก์ชันใดใช้ Rhie-Chow?</b></summary>

`fvc::flux(HbyA)` — Rhie-Chow correction ถูก apply โดยอัตโนมัติเมื่อคำนวณ face flux จาก volume field
</details>

<details>
<summary><b>3. nNonOrthogonalCorrectors ช่วยอะไร?</b></summary>

แก้ไข error จาก mesh ที่ไม่ตั้งฉาก — Laplacian ต้องการ iterative correction เมื่อ face normal ไม่ตรงกับ line ระหว่าง cell centers
</details>

---

## Related Documents

- **บทก่อนหน้า:** [03_PISO_and_PIMPLE_Algorithms.md](03_PISO_and_PIMPLE_Algorithms.md)
- **บทถัดไป:** [05_Algorithm_Comparison.md](05_Algorithm_Comparison.md)