# Verification - Introduction

บทนำ Verification

---

## Overview

> **Verification** = Are we solving the equations correctly?

<!-- IMAGE: IMG_08_001 -->
<!-- 
Purpose: เพื่อแยกแยะ "Verification" กับ "Validation" ให้ขาดจากกัน. ภาพนี้ต้องใช้แผนภาพ V-Model หรือ Parallel Paths ที่แสดงว่า: Verification คือการเช็คคณิตศาสตร์ (Math Check) ส่วน Validation คือการเช็คฟิสิกส์ (Reality Check)
Prompt: "Conceptual Diagram: Verification vs Validation. **Left Path (Verification):** 'Solving the equations right'. Flow: Code $\rightarrow$ Mathematics $\rightarrow$ Numerical Solution. Icon: Calculator/Checkmark. **Right Path (Validation):** 'Solving the right equations'. Flow: Real World $\rightarrow$ Physics Model $\rightarrow$ Simulation Result. Icon: Experiment/Balance Scale. **Comparison:** In the center, show Simulation Result being compared against MATH (Verification) vs EXPERIMENT (Validation). STYLE: Blueprint schematic, clear logical flow, contrasting colors."
-->
![IMG_08_001: Verification vs Validation](IMG_08_001.jpg)

---

## 1. Verification Types

| Type | Check |
|------|-------|
| **Code** | Implementation correct? |
| **Solution** | Solver converges? |
| **Calculation** | Results consistent? |

---

## 2. Method of Manufactured Solutions (MMS)

```cpp
// Create exact solution
volScalarField Texact
(
    mesh,
    dimensionedScalar("T", dimTemperature, 0)
);

forAll(Texact, cellI)
{
    scalar x = mesh.C()[cellI].x();
    Texact[cellI] = sin(x);  // Known solution
}

// Calculate source term for this solution
volScalarField source = fvc::laplacian(alpha, Texact);

// Solve with source
solve(fvm::laplacian(alpha, T) == source);

// Compare
scalar error = gSum(mag(T - Texact) * mesh.V()) / gSum(mesh.V());
```

---

## 3. Order of Accuracy

```bash
# Run with different mesh sizes
for n in 10 20 40 80; do
    blockMesh -dict system/blockMeshDict.$n
    solver
    # Record error
done

# Should see error ~ h^p (p = order of scheme)
```

<!-- IMAGE: IMG_08_002 -->
<!-- 
Purpose: เพื่อแสดงกราฟ "Grid Convergence" ซึ่งเป็นหลักฐานสำคัญที่สุดของ Verification. ภาพนี้ต้องโชว์กราฟ Log-Log ของ Error vs Grid Step ($h$). ความชันของเส้น (Slope) คือ Order of Accuracy.
Prompt: "Standard Grid Convergence Plot (Log-Log Scale). **X-axis:** Grid Spacing $h$ (Decreasing $\rightarrow$). **Y-axis:** Error Norm $E$ (Decreasing $\downarrow$). **Data Points:** 4-5 points showing error dropping as grid gets finer. **Reference Lines:** Dashed lines representing Slope = 1 (1st Order) and Slope = 2 (2nd Order). **Annotation:** Calculate 'Observed Order $p$' from the slope. Show 'Asymptotic Range' where the slope becomes constant. STYLE: Academic scientific plot, clean grid lines, LaTeX labels."
-->
![IMG_08_002: Grid Convergence Study](IMG_08_002.jpg)

---

## 4. Conservation Check

```cpp
// Mass conservation
scalar massIn = gSum(phi.boundaryField()[inlet]);
scalar massOut = gSum(phi.boundaryField()[outlet]);

if (mag(massIn + massOut) > SMALL)
{
    Warning << "Mass not conserved";
}
```

---

## Quick Reference

| Check | Method |
|-------|--------|
| Implementation | MMS |
| Convergence | Residuals |
| Order | Grid refinement |
| Conservation | Flux balance |

---

## Concept Check

<details>
<summary><b>1. MMS คืออะไร?</b></summary>

**Manufactured Solution** — create exact answer, verify solver finds it
</details>

<details>
<summary><b>2. Order of accuracy ตรวจอย่างไร?</b></summary>

**Grid refinement study** — error should decrease as h^p
</details>

<details>
<summary><b>3. Conservation check ทำอะไร?</b></summary>

**Verify fluxes balance** — in = out
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Architecture:** [03_OpenFOAM_Architecture.md](03_OpenFOAM_Architecture.md)
