# 05_Expected_Results.md

---

## Learning Objectives

After completing this section, you should be able to:
- **Understand** the physical flow patterns expected in lid-driven cavity flow at different Reynolds numbers
- **Validate** your OpenFOAM simulation results against the Ghia et al. (1982) benchmark data
- **Quantify** simulation accuracy using error metrics (L2 norm, maximum error)
- **Perform** grid convergence studies to verify mesh independence
- **Interpret** discrepancies and troubleshoot common validation issues

---

## Key Takeaways

- **Ghia et al. (1982)** is the standard benchmark for lid-driven cavity validation — always compare against this reference
- **Acceptable error ranges:** < 5% for coarse engineering meshes, < 1% for fine research-grade meshes
- **Primary vortex center** shifts toward the cavity center as Reynolds number increases
- **Secondary vortices** appear in corners at Re ≥ 400
- **Grid convergence** is essential: error should systematically decrease with mesh refinement
- **Validation methodology:** Visual checks → Quantitative comparison → Error metrics → Convergence study

---

# Expected Results & Validation

การตรวจสอบความถูกต้องของผลลัพธ์

---

## Overview

### WHAT: Validation Against Benchmark Data

Validation is the process of comparing your CFD simulation results against trusted reference data to verify accuracy. For lid-driven cavity flow, the **Ghia et al. (1982)** dataset is the universally accepted benchmark.

### WHY: Ensure Simulation Reliability

- **CFD without validation = unreliable results**
- Benchmark data confirms your numerical setup is correct
- Learn to **compare against references** from the start of your CFD practice
- Establish confidence before applying to new, unvalidated problems

### HOW: Through Systematic Comparison

1. **Visual inspection** of flow patterns (streamlines, vortex positions)
2. **Quantitative comparison** of velocity profiles along centerlines
3. **Error metrics** (L2 norm, maximum error)
4. **Grid convergence study** to verify mesh independence

---

## Prerequisites

> **⚠️ Before Running Validation Scripts:**
> 
> **For Python validation script:**
> - Python 3.x installed
> - Required packages: `pip install numpy matplotlib`
> - Or use [Anaconda](https://www.anaconda.com/) / [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
>
> **For OpenFOAM sampling:**
> - Completed simulation with converged solution
> - Familiarity with `postProcess` functions (see [02_The_Workflow.md](02_The_Workflow.md))
> - Understanding of `controlDict` function objects

---

## Expected Flow Patterns

### WHAT: Flow Structures in Lid-Driven Cavity

The lid-driven cavity generates a primary recirculation vortex with possible secondary vortices in corners, depending on Reynolds number.

### WHY: Understanding Expected Physics

Knowing the expected flow patterns helps you:
- Identify incorrect simulations quickly
- Verify your mesh and solver settings are appropriate
- Develop physical intuition for recirculating flows

### HOW: Recognize Valid Flow Features

#### Primary Vortex

| Re | Center (x/L, y/L) | Stream Function ψ_max |
|----|-------------------|----------------------|
| 100 | (0.617, 0.734) | -0.1034 |
| 400 | (0.555, 0.606) | -0.1139 |
| 1000 | (0.531, 0.563) | -0.1179 |

*Reference: Ghia et al. (1982)*

> **💡 Stream Function (ψ) Explained:**
> - ψ = constant along streamlines
> - Difference in ψ between two streamlines = volumetric flow rate between them
> - In 2D incompressible flow: $u = \frac{\partial ψ}{\partial y}$, $v = -\frac{\partial ψ}{\partial x}$
> - **ψ_max** (negative value due to clockwise rotation) indicates vortex strength
> - Vortex center moves toward cavity center as Re increases

#### Secondary Vortices (Re ≥ 400)

As Reynolds number increases, corner vortices emerge due to flow separation:

| Re | Bottom-Right (BR) | Bottom-Left (BL) |
|----|-------------------|------------------|
| 400 | (0.89, 0.12) | (0.03, 0.04) |
| 1000 | (0.86, 0.11) | (0.08, 0.08) |

- **Bottom-Right** vortex appears first (Re ≥ 400)
- **Bottom-Left** vortex strengthens at higher Re
- **Top corners** may also show small vortices at Re ≥ 1000

---

## Reference Velocity Profiles

### WHAT: Ghia et al. Benchmark Data

The following tables provide the exact velocity values from Ghia et al. (1982) for direct comparison.

### WHY: Quantitative Validation Standard

These profiles are the most widely cited validation data for lid-driven cavity flow.

### HOW: Use for Direct Comparison

#### u-velocity at x = 0.5 (Vertical Centerline)

**Re = 100:**
```
y/L     u/U (Ghia)
0.0000  0.00000
0.0547  -0.03717
0.0625  -0.04192
0.0703  -0.04775
0.1016  -0.06434
0.1719  -0.10150
0.2813  -0.15662
0.4531  -0.21090
0.5000  -0.20581
0.6172  -0.13641
0.7344   0.00332
0.8516   0.23151
0.9531   0.68717
0.9609   0.73722
0.9688   0.78871
0.9766   0.84123
1.0000   1.00000
```

#### v-velocity at y = 0.5 (Horizontal Centerline)

**Re = 100:**
```
x/L     v/U (Ghia)
0.0000  0.00000
0.0625  0.09233
0.0703  0.10091
0.0781  0.10890
0.0938  0.12317
0.1563  0.16077
0.2266  0.17507
0.2344  0.17527
0.5000  0.05454
0.8047  -0.24533
0.8594  -0.22445
0.9063  -0.16914
0.9453  -0.10313
0.9531  -0.08864
0.9609  -0.07391
0.9688  -0.05906
1.0000  0.00000
```

> **📖 Reference:** Ghia, U., Ghia, K. N., & Shin, C. T. (1982). High-Re solutions for incompressible flow using the Navier-Stokes equations and a multigrid method. *Journal of Computational Physics*, 48(3), 387-411.

---

## Validation Methodology

### WHAT: Three-Stage Validation Process

Validation combines visual inspection, quantitative comparison, and error analysis to ensure simulation accuracy.

### WHY: Multi-Method Confidence

No single validation method is sufficient. Combining approaches provides:
- **Quick visual feedback** for obvious errors
- **Quantitative metrics** for objective assessment
- **Systematic verification** through grid convergence

### HOW: Perform Complete Validation

#### Stage 1: Visual Validation

**In ParaView, check:**
- ✓ Streamlines show clockwise primary rotation
- ✓ Primary vortex located near expected position (see table above)
- ✓ No spurious oscillations or unphysical features
- ✓ Symmetry (or lack thereof) matches expected Re behavior

**Red flags:**
- ✗ Counter-clockwise rotation (wrong boundary condition)
- ✗ Vortex at wall (insufficient resolution or wrong scheme)
- ✗ Multiple unexplained vortices (numerical instability)

#### Stage 2: Quantitative Comparison

**WHAT:** Extract velocity profiles along centerlines for direct comparison with Ghia data.

**WHY:** Provides numerical values for error calculation and objective validation.

**HOW:** Use OpenFOAM's built-in post-processing functions.

> **⚠️ Note:** We recommend using `controlDict` functions instead of the deprecated `sampleDict`. See [02_The_Workflow.md](02_The_Workflow.md#sampling-functions) for detailed explanation.

**Method: Define in controlDict**

```cpp
// system/controlDict
functions
{
    verticalCenterline
    {
        type            sets;
        setFormat       raw;
        fields          (U);
        sets
        (
            verticalCenterline
            {
                type    uniform;
                axis    y;
                start   (0.5 0 0.05);
                end     (0.5 1 0.05);
                nPoints 50;
            }
        );
        outputControl   timeStep;
        outputInterval  100;
    }
    
    horizontalCenterline
    {
        type            sets;
        setFormat       raw;
        fields          (U);
        sets
        (
            horizontalCenterline
            {
                type    uniform;
                axis    x;
                start   (0 0.5 0.05);
                end     (1 0.5 0.05);
                nPoints 50;
            }
        );
        outputControl   timeStep;
        outputInterval  100;
    }
}
```

**Run after simulation completes:**

```bash
# Extract data at final time
postProcess -func verticalCenterline -latestTime
postProcess -func horizontalCenterline -latestTime

# Output location: postProcessing/verticalCenterline/<finalTime>/verticalCenterline_U.raw
```

#### Stage 3: Automated Python Validation

**WHAT:** Python script for automated comparison and visualization.

**WHY:** Efficient way to compare profiles and calculate error metrics.

**HOW:** Use the script below (requires Python 3.x with numpy/matplotlib).

```python
#!/usr/bin/env python3
"""
Validation script for lid-driven cavity flow
Compares OpenFOAM results with Ghia et al. (1982) benchmark data
"""

import numpy as np
import matplotlib.pyplot as plt

# ===============================
# WHAT: Ghia et al. benchmark data for Re=100
# ===============================
ghia_y = [0, 0.0547, 0.0625, 0.0703, 0.1016, 0.1719, 
          0.2813, 0.4531, 0.5, 0.6172, 0.7344, 0.8516, 
          0.9531, 0.9609, 0.9688, 0.9766, 1.0]
ghia_u = [0, -0.03717, -0.04192, -0.04775, -0.06434, 
          -0.1015, -0.15662, -0.2109, -0.20581, -0.13641, 
          0.00332, 0.23151, 0.68717, 0.73722, 0.78871, 
          0.84123, 1.0]

# ===============================
# HOW: Load and process OpenFOAM data
# ===============================
# Load OpenFOAM data (adjust path as needed)
data = np.loadtxt('postProcessing/verticalCenterline/0.5/verticalCenterline_U.raw')
of_y = data[:, 1]      # y-coordinates
of_u = data[:, 3]      # Ux component (adjust column index if needed)

# ===============================
# VALIDATION: Plot comparison
# ===============================
plt.figure(figsize=(10, 8))

# Vertical centerline u-velocity
plt.subplot(2, 1, 1)
plt.plot(of_u, of_y, 'b-', linewidth=2, label='OpenFOAM')
plt.plot(ghia_u, ghia_y, 'ro', markersize=6, label='Ghia et al. (1982)')
plt.xlabel('u/U')
plt.ylabel('y/L')
plt.title('Vertical Centerline (x=0.5): u-velocity Comparison')
plt.legend()
plt.grid(True, alpha=0.3)

# Error plot
plt.subplot(2, 1, 2)
# Interpolate Ghia data to OpenFOAM points for error calculation
ghia_interp = np.interp(of_y, ghia_y, ghia_u)
error = np.abs(of_u - ghia_interp)
plt.plot(of_y, error, 'r-', linewidth=2)
plt.xlabel('y/L')
plt.ylabel('|u_CFD - u_ref|')
plt.title('Absolute Error Distribution')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('validation_comparison.png', dpi=150)
print("✓ Validation plot saved as validation_comparison.png")
plt.show()

# ===============================
# ERROR METRICS: Calculate L2 norm
# ===============================
l2_error = np.sqrt(np.mean((of_u - ghia_interp)**2))
max_error = np.max(error)
relative_l2 = l2_error / np.max(np.abs(ghia_u)) * 100

print(f"\n{'='*50}")
print("VALIDATION RESULTS")
print(f"{'='*50}")
print(f"L2 Error (absolute):     {l2_error:.6f}")
print(f"L2 Error (relative):     {relative_l2:.2f}%")
print(f"Maximum Error:           {max_error:.6f}")
print(f"{'='*50}")

# ===============================
# CONVERGENCE CHECK: Acceptable ranges
# ===============================
if relative_l2 < 1.0:
    print("✓ EXCELLENT: Research-grade accuracy (< 1%)")
elif relative_l2 < 5.0:
    print("✓ ACCEPTABLE: Engineering accuracy (< 5%)")
else:
    print("⚠ WARNING: Error exceeds acceptable range")
    print("  Consider: mesh refinement, longer convergence, or scheme adjustment")
print(f"{'='*50}\n")
```

**Usage:**

```bash
# Save script as validate_cavity.py
python3 validate_cavity.py
```

---

## Error Metrics and Acceptable Ranges

### WHAT: Quantifying Simulation Accuracy

Error metrics provide objective measures of how closely your simulation matches the benchmark.

### WHY: Objective Quality Assessment

- **Track improvement** during solver development
- **Compare different schemes** (upwind vs. linear vs. QUICK)
- **Verify mesh independence** through grid convergence
- **Document simulation quality** for reports/publications

### HOW: Calculate and Interpret Errors

#### L2 Norm Error (Root-Mean-Square Error)

$$E_{L2} = \sqrt{\frac{\sum_{i=1}^{N}(u_i^{CFD} - u_i^{ref})^2}{N}}$$

**Interpretation:**
- **< 1%**: Research-grade accuracy (fine mesh, high-order schemes)
- **1-5%**: Engineering accuracy (acceptable for most applications)
- **5-10%**: Coarse mesh or first-order schemes
- **> 10%**: Potential issues with setup/convergence

#### Maximum Error

$$E_{max} = \max_i |u_i^{CFD} - u_i^{ref}|$$

**Interpretation:**
- Identifies worst-case deviation
- Typically occurs near walls or vortex centers
- Should be < 5% of maximum velocity for well-resolved flows

#### Relative L2 Error

$$E_{rel} = \frac{E_{L2}}{\max(|u^{ref}|)} \times 100\%$$

Normalizes error by reference magnitude for percentage-based assessment.

---

## Grid Convergence Study

### WHAT: Verification of Mesh Independence

Grid convergence systematically refines the mesh to verify that errors decrease and solution approaches mesh-independent value.

### WHY: Ensure Results Are Mesh-Independent

- **Confirm discretization error** is acceptable
- **Verify mesh quality** is sufficient for physics captured
- **Determine optimal mesh** balancing accuracy and computational cost
- **Required for rigorous validation** in research publications

### HOW: Perform Convergence Study

#### Expected Error Reduction

| Grid | Cells | L2 Error (%) | Expected Use |
|------|-------|--------------|--------------|
| 10×10 | 100 | ~15% | Quick testing only |
| 20×20 | 400 | ~5% | Engineering accuracy |
| 40×40 | 1600 | ~2% | Good accuracy |
| 80×80 | 6400 | ~1% | Research-grade |

#### Procedure

1. **Run simulations** with at least 3 mesh densities (e.g., 20×20, 40×40, 80×80)
2. **Calculate error metrics** for each mesh against Ghia reference
3. **Plot error vs. mesh size** (log-log plot)
4. **Verify systematic decrease** in error with refinement
5. **Check convergence rate** (should approach theoretical order ~2 for second-order schemes)

#### Success Criteria

- ✓ Error decreases monotonically with mesh refinement
- ✓ Solution differences between finest two meshes < 1%
- ✓ L2 error on finest mesh < acceptable threshold for application

---

## Interpreting Discrepancies

### WHAT: When Results Don't Match

Even with correct setup, small discrepancies are expected. Understanding why is critical for proper interpretation.

### WHY: Sources of Deviation

Discrepancies arise from multiple sources; identifying the cause guides corrective action.

### HOW: Diagnose and Address Issues

#### Expected Discrepancies (Acceptable)

| Source | Magnitude | Action |
|--------|-----------|--------|
| **Truncation error** | < 2% for fine mesh | Acceptable; improve with mesh refinement |
| **Iteration convergence** | < 1% if residuals < 10⁻⁵ | Run longer if needed |
| **Numerical diffusion** | 1-5% with upwind schemes | Use higher-order schemes if critical |

#### Problematic Discrepancies (Require Action)

| Issue | Symptoms | Likely Cause | Solution |
|-------|----------|--------------|----------|
| **Vortex off-center** | Center position error > 5% | Not converged | Extend endTime; check residual targets |
| **Poor overall match** | L2 error > 10% | Mesh too coarse | Refine mesh (2× or more) |
| **Oscillations in profile** | Non-physical wiggles | Scheme unstable | Use upwind or limiters |
| **Wrong vortex direction** | Counter-clockwise rotation | BC error | Check lid velocity direction |
| **Symmetry errors** | Asymmetric at low Re | Insymmetric mesh/BCs | Verify blockMesh topology; check BCs |
| **Slow/non-convergence** | Residuals plateau | Time step too large | Reduce Courant number (< 1) |

#### Diagnostic Checklist

```
□ Residuals < 10⁻⁵ for all variables?
□ Final time sufficient for steady state (Re < 1000)?
□ Mesh quality: aspect ratio < 5, non-orthogonality < 70?
□ Boundary conditions: U=(1 0 0) on lid, (0 0 0) on walls?
□ Schemes: Gauss linear for spatial, Euler for temporal?
□ Solver: simpleFoam for steady, icoFoam/pimpleFoam for transient?
```

#### When to Accept vs. Iterate

- **Accept:** L2 error < 5%, physical flow patterns match, residuals converged
- **Iterate:** L2 error > 5%, unphysical features, clear symptoms from table above
- **Research-grade:** L2 error < 1%, verified with grid convergence ≥ 3 mesh levels

---

## Common Issues and Troubleshooting

### WHAT: Frequent Validation Problems

Below are common issues encountered when validating lid-driven cavity simulations.

### WHY: Learning from Typical Mistakes

Understanding these issues speeds up diagnosis and prevents repeated errors.

### HOW: Apply Solutions

| Issue | Possible Cause | Diagnosis | Solution |
|-------|----------------|-----------|----------|
| **Vortex off-center** | Not converged | Residuals still changing | Run longer endTime; tighten tolerance |
| **Poor validation** | Mesh too coarse | L2 error > 10% | Refine mesh (increase cells by 2-4×) |
| **Velocity oscillations** | Scheme instability | Wiggles in profile | Switch to upwind or add limiters |
| **Slow convergence** | Large time step | Courant > 1 | Reduce deltaT to achieve Co < 0.5 |
| **Wrong magnitude** | BC error | Max velocity ≠ 1 | Check lid BC: `U=(1 0 0)` not `fixedValue 1` |
| **No convergence** | Incompatible settings | Residuals plateau | Verify scheme/solver compatibility |
| **Asymmetric at Re=100** | Mesh/solver asymmetry | Profile not symmetric | Check blockMesh symmetry; solver tolerances |

---

## Concept Check

<details>
<summary><b>1. ทำไมต้อง validate กับ Ghia et al. (1982)?</b></summary>

เพราะเป็น benchmark reference ที่ได้รับการยอมรับในวงการ CFD — ใช้ high-resolution methods (multigrid with fine grid up to 257×257) และมี data ที่ละเอียด ทำให้เป็นมาตรฐานสากลสำหรับ lid-driven cavity validation
</details>

<details>
<summary><b>2. Grid convergence study ทำไปเพื่ออะไร?</b></summary>

เพื่อตรวจสอบว่า error มาจาก mesh resolution หรือ physics/setup ผิด — ถ้า error ลดลงเมื่อ mesh fine ขึ้นอย่างสม่ำเสมอ แสดงว่า approach ถูกต้องและ error เป็น truncation error ที่คาดหวังได้ แต่ถ้า error ไม่ลดลงหรือลดลงน้อยเกินไป อาจมีปัญหากับ scheme หรือ setup
</details>

<details>
<summary><b>3. L2 error < 5% ถือว่าดีไหม?</b></summary>

**ใช่** สำหรับ engineering applications ถือว่ายอมรับได้ (acceptable) — แต่สำหรับ research หรือ publication อาจต้องการ < 1% และต้องแสดง grid convergence อย่างเป็นทางการ ขึ้นกับความเข้มงวดของ application และ requirement ของงาน
</details>

<details>
<summary><b>4. ถ้าเจอ oscillation ใน velocity profile ควรทำอย่างไร?</b></summary>

Oscillation มักเกิดจาก instability ของ numerical schemes — วิธีแก้:
1. **เปลี่ยนเป็น upwind scheme** (เพิ่ม numerical diffusion แต่ stable)
2. **ใช้ limiters** (เช่น vanLeer, MUSCL) สำหรับ higher-order schemes
3. **ลด time step** เพื่อลด Courant number
4. **ตรวจสอบ mesh quality** — non-orthogonality สูงอาจก่อให้เกิด instability
</details>

<details>
<summary><b>5. Stream function ψ_max ทำไมเป็นค่าติดลบ?</b></summary>

เพราะ lid-driven cavity มีการหมุน **clockwise** — ใน convention ของ fluid mechanics:
- **Counter-clockwise rotation** → positive ψ
- **Clockwise rotation** → negative ψ
- **ค่า absolute** ของ ψ_max บอกความเข้มของการหมุน (vortex strength)
- Re สูงขึ้น → |ψ_max| เพิ่มขึ้น (การหมุนเข้มขึ้น)
</details>

---

## Related Documents

- **Previous:** [04_Step-by-Step_Tutorial.md](04_Step-by-Step_Tutorial.md) — Complete hands-on tutorial for running the simulation
- **Next:** [06_Exercises.md](06_Exercises.md) — Practice exercises to test your understanding
- **Reference:** [02_The_Workflow.md](02_The_Workflow.md) — Detailed sampling functions and post-processing setup
- **Overview:** [01_Introduction.md](01_Introduction.md) — Module introduction and prerequisites

---

## Further Reading

**Validation Methodology:**
- Oberkampf, W. L., & Trucano, T. G. (2002). Verification and validation in computational fluid dynamics. *Progress in Aerospace Sciences*, 38(3), 209-272.

**Lid-Driven Cavity Benchmarks:**
- Ghia, U., Ghia, K. N., & Shin, C. T. (1982). High-Re solutions for incompressible flow using the Navier-Stokes equations and a multigrid method. *Journal of Computational Physics*, 48(3), 387-411.

**Grid Convergence:**
- Roache, P. J. (1998). Verification of codes and calculations. *AIAA Journal*, 36(5), 696-702. (Grid Convergence Index - GCI method)