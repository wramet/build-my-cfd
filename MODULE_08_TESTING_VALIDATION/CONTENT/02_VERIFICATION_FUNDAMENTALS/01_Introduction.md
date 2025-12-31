# Verification - Introduction

บทนำ Verification

---

## Learning Objectives (จุดประสงค์การเรียนรู้)

After completing this module, you should be able to:

- **Differentiate** verification from validation using the "Are we solving the equations correctly?" framework
- **Identify** the three main types of verification checks: Code, Solution, and Calculation
- **Apply** Method of Manufactured Solutions (MMS) to verify code implementation
- **Perform** grid convergence studies to determine order of accuracy
- **Verify** conservation properties in OpenFOAM simulations

---

## Overview

### What is Verification? (Verification คืออะไร?)

**Verification** answers the question: **"Are we solving the equations correctly?"**

> **Verification = Mathematics Check** → Ensuring the numerical solution matches the mathematical model

Verification is the process of determining whether a computational simulation accurately represents the conceptual mathematical model. It focuses on:

- **Code correctness**: Implementation matches the mathematical formulation
- **Numerical accuracy**: Solutions converge to the correct values
- **Consistency**: Results are reproducible and mathematically sound

---

### Why is Verification Important? (ทำไม Verification จึงสำคัญ?)

| Reason | Impact |
|--------|--------|
| **Trust** | Build confidence in simulation results |
| **Debug** | Catch implementation errors early |
| **Quality** | Ensure reproducible, reliable results |
| **Documentation** | Provide evidence of correctness |

---

### How Do We Verify? (วิธีการ Verification)

**Three Main Approaches:**

1. **Code Verification** → Implementation correctness
   - Method of Manufactured Solutions (MMS)
   - Comparison with analytical solutions
   
2. **Solution Verification** → Numerical accuracy
   - Grid convergence studies
   - Order of accuracy analysis
   
3. **Calculation Verification** → Result consistency
   - Conservation checks
   - Flux balance verification

<!-- IMAGE: IMG_08_001 -->
<!-- 
Purpose: เพื่อแยกแยะ "Verification" กับ "Validation" ให้ขาดจากกัน. ภาพนี้ต้องใช้แผนภาพ V-Model หรือ Parallel Paths ที่แสดงว่า: Verification คือการเช็คคณิตศาสตร์ (Math Check) ส่วน Validation คือการเช็คฟิสิกส์ (Reality Check)
Prompt: "Conceptual Diagram: Verification vs Validation. **Left Path (Verification):** 'Solving the equations right'. Flow: Code $\rightarrow$ Mathematics $\rightarrow$ Numerical Solution. Icon: Calculator/Checkmark. **Right Path (Validation):** 'Solving the right equations'. Flow: Real World $\rightarrow$ Physics Model $\rightarrow$ Simulation Result. Icon: Experiment/Balance Scale. **Comparison:** In the center, show Simulation Result being compared against MATH (Verification) vs EXPERIMENT (Validation). STYLE: Blueprint schematic, clear logical flow, contrasting colors."
-->
![IMG_08_001: Verification vs Validation](IMG_08_001.jpg)

---

## 1. Verification Types (ประเภทของ Verification)

| Type | Question | Method |
|------|----------|--------|
| **Code** | Is the implementation correct? | MMS, Analytical Solutions |
| **Solution** | Does the solver converge? | Residuals, Grid Independence |
| **Calculation** | Are results consistent? | Conservation Checks, Flux Balance |

---

## 2. Method of Manufactured Solutions (MMS)

### Concept (แนวคิด)

Instead of solving a difficult problem with unknown solution:

1. **Choose** a simple, known solution (e.g., T = sin(x))
2. **Derive** the source term that produces this solution
3. **Run** the solver with this source term
4. **Compare** numerical result with the exact solution
5. **Quantify** error → verify implementation

> **Key Idea:** Work backwards from answer to question

### Application in OpenFOAM (การประยุกต์ใช้)

See detailed implementation with code examples in **[02_Method_of_Manufactured_Solutions.md](02_Method_of_Manufactured_Solutions.md)**

Basic structure:
- Manufacture analytical solution: `Texact = f(x,y,z,t)`
- Compute source term: `S = ∇·(α∇T) - ∂T/∂t`
- Run solver with source
- Measure error: `ε = ||T - Texact||`

---

## 3. Order of Accuracy (ลำดับความแม่นยำ)

### Grid Convergence Study (การศึกษาการลู่เข้าของเส้นตาข่าย)

**Purpose:** Verify that the solver achieves expected convergence rate

**Procedure:**

```bash
# Run with progressively refined meshes
for n in 10 20 40 80; do
    blockMesh -dict system/blockMeshDict.$n
    simpleFoam
    # Extract error metrics
done
```

**Expected Behavior:**
```
Error ∝ h^p
```
where:
- `h` = grid spacing (characteristic cell size)
- `p` = order of accuracy (1 = first order, 2 = second order)

**Log-Log Plot:**
- Slope = observed order of accuracy
- Asymptotic range → constant slope at fine grids

<!-- IMAGE: IMG_08_002 -->
<!-- 
Purpose: เพื่อแสดงกราฟ "Grid Convergence" ซึ่งเป็นหลักฐานสำคัญที่สุดของ Verification. ภาพนี้ต้องโชว์กราฟ Log-Log ของ Error vs Grid Step ($h$). ความชันของเส้น (Slope) คือ Order of Accuracy.
Prompt: "Standard Grid Convergence Plot (Log-Log Scale). **X-axis:** Grid Spacing $h$ (Decreasing $\rightarrow$). **Y-axis:** Error Norm $E$ (Decreasing $\downarrow$). **Data Points:** 4-5 points showing error dropping as grid gets finer. **Reference Lines:** Dashed lines representing Slope = 1 (1st Order) and Slope = 2 (2nd Order). **Annotation:** Calculate 'Observed Order $p$' from the slope. Show 'Asymptotic Range' where the slope becomes constant. STYLE: Academic scientific plot, clean grid lines, LaTeX labels."
-->
![IMG_08_002: Grid Convergence Study](IMG_08_002.jpg)

---

## 4. Conservation Check (การตรวจสอบการอนุรักษ์)

### Why Conservation Matters (ทำไมต้องตรวจสอบการอนุรักษ์)

Physical quantities (mass, momentum, energy) must satisfy:

$$\frac{d}{dt}\int_V \rho \, dV + \oint_{\partial V} \mathbf{\phi} \cdot d\mathbf{A} = 0$$

**In OpenFOAM:**

```cpp
// Mass conservation check
scalar massIn = gSum(phi.boundaryField()[inlet]);
scalar massOut = gSum(phi.boundaryField()[outlet]);
scalar massError = mag(massIn + massOut);

if (massError > tolerance)
{
    Warning << "Mass not conserved: error = " << massError << endl;
}

// Energy conservation check
scalar energyIn = gSum(phi.boundaryField()[inlet] * 
                       rho.boundaryField()[inlet] * 
                       h.boundaryField()[inlet]);
```

**Acceptance Criteria:**
- Steady-state: `|in - out| / max(|in|, |out|) < 1e-6`
- Transient: check integral form over control volume

---

## Quick Reference (สรุปอ้างอิง)

| Verification Aspect | Check Method | OpenFOAM Tool |
|---------------------|--------------|---------------|
| **Implementation** | MMS | Custom BCs, source terms |
| **Convergence** | Residuals | `solverInfo`, `logs` |
| **Order Accuracy** | Grid refinement | `blockMeshDict` variants |
| **Conservation** | Flux balance | `phi`, boundaryField sums |

---

## Concept Check (ทดสอบความเข้าใจ)

<details>
<summary><b>1. MMS คืออะไร?</b></summary>

**Method of Manufactured Solutions** — Choose exact solution, compute source term, verify solver finds it. Key advantage: works for ANY equation type.

</details>

<details>
<summary><b>2. Order of accuracy ตรวจอย่างไร?</b></summary>

**Grid refinement study** — Run same case on multiple grid sizes (h, h/2, h/4...), plot error vs h on log-log scale, slope = observed order. Should match theoretical order (e.g., 2 for upwind).

</details>

<details>
<summary><b>3. Conservation check ทำอะไร?</b></summary>

**Verify flux balance** — For steady state, sum of boundary fluxes should be zero (∑φ_in + ∑φ_out = 0). Checks if solver correctly enforces physical conservation laws.

</details>

<details>
<summary><b>4. Verification vs Validation ต่างกันอย่างไร?</b></summary>

**Verification** = "Are we solving the equations correctly?" (Math check)  
**Validation** = "Are we solving the right equations?" (Physics check)

Example:  
- Verification: Does my solver satisfy ∇·v = 0?  
- Validation: Does my turbulence model match real flow data?

</details>

---

## Key Takeaways (สรุปสิ่งสำคัญ)

- ✅ **Verification** ensures we're solving the equations correctly (mathematics, not physics)
- ✅ **MMS** is the gold standard for code verification — manufacture solution, verify solver finds it
- ✅ **Grid convergence studies** prove the solver achieves expected order of accuracy
- ✅ **Conservation checks** verify fundamental physical laws are satisfied
- ✅ **Always verify** before validating — a buggy solver cannot be validated against experiments

---

## Related Documents (เอกสารที่เกี่ยวข้อง)

- **Previous:** [00_Overview.md](00_Overview.md) — Verification framework and scope
- **Next:** [02a_Method_of_Manufactured_Solutions.md](02a_Method_of_Manufactured_Solutions.md) — Detailed MMS implementation
- **Related:** [02b_Code_Verification_Practices.md](02b_Code_Verification_Practices.md) — Systematic verification workflows
- **Validation:** [00_Overview.md](../03_VALIDATION_FUNDAMENTALS/00_Overview.md) — Physics verification methods