# Simulation Control

การควบคุมการจำลองใน OpenFOAM

---

## Learning Objectives

หลังจากอ่านบทนี้ คุณควรจะสามารถ:

- **WHAT:** อธิบายหน้าที่และโครงสร้างของ `controlDict`, `fvSolution`, และ `fvSchemes`
- **WHY:** เข้าใจเหตุผลทางฟิสิกส์และเชิงตัวเลขที่อยู่เบื้องหลังการตั้งค่าแต่ละอย่าง
- **HOW:** เลือกและปรับแต่ง linear solvers, under-relaxation factors, และ discretization schemes อย่างเหมาะสม

> **ทำไมต้องเข้าใจ Simulation Control?**
> - **controlDict, fvSolution, fvSchemes** ควบคุมทุกอย่าง
> - ตั้งค่าผิด = **diverge** หรือ **ช้ามาก**
> - Best practices ช่วยประหยัดเวลาและทรัพยากร

---

## Overview Table

| File | Purpose | Key Parameters |
|------|---------|----------------|
| `system/controlDict` | Time control, output, function objects | `deltaT`, `writeInterval`, `adjustTimeStep` |
| `system/fvSolution` | Linear solvers, algorithms, relaxation | `solver`, `tolerance`, `nCorrectors` |
| `system/fvSchemes` | Discretization schemes | `gradSchemes`, `divSchemes`, `laplacianSchemes` |

---

## Part 1: controlDict - Time Control & Output

### WHAT: Basic Structure

ไฟล์ `system/controlDict` คือสมองที่ควบคุมการทำงานของ solver — บอกว่า **เริ่มเมื่อ, จบเมื่อ, เขียน output เมื่อไหร่, และรันยังไง**

```cpp
application     simpleFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         1000;
deltaT          1;

writeControl    timeStep;
writeInterval   100;
purgeWrite      3;              // Keep only 3 latest results
runTimeModifiable true;         // Allow runtime modification
```

### WHY: Understanding Time Stepping

#### **Steady-State vs Transient**

| Aspect | Steady-State | Transient |
|--------|--------------|-----------|
| `deltaT` | Pseudo time step (not physical) | Physical time step |
| `stopAt` | `endTime` (iterations) | `endTime` (seconds) |
| `adjustTimeStep` | `no` | Usually `yes` |

#### **CFL Condition (Courant-Friedrichs-Lewy)**

สำหรับ transient simulations, time step ต้องเคารพเงื่อนไข CFL:

$$Co = \frac{|u| \Delta t}{\Delta x} < 1$$

โดยที่:
- $|u|$ = ความเร็วสูงสุดใน domain
- $\Delta t$ = time step
- $\Delta x$ = cell size ที่เล็กที่สุด

**Physical Reasoning:** CFL < 1 รับประกันว่าข้อมูลจะไม่ "กระโดด" ข้าม cell มากกว่า 1 ชั้นต่อ time step หนึ่ง — นี่คือเงื่อนไขความเสถียรเชิงตัวเลข

### HOW: Time-Step Estimation Strategies

#### **Strategy 1: Conservative Starting**

```cpp
// สำหรับ simulation ใหม่ — เริ่มต้นปลอดภัย
deltaT          0.001;
adjustTimeStep  yes;
maxCo           0.5;            // Conservative: 0.5 < 1
maxDeltaT       0.01;
```

#### **Strategy 2: Mesh-Based Estimation**

คำนวณ `deltaT` เบื้องต้นจาก mesh:

```bash
# หา cell size ที่เล็กที่สุด
checkMesh | grep "bounding box"
# สมมติได้ 0.001 m

# สมมติ u_max ≈ 10 m/s
deltaT_max = 0.5 * 0.001 / 10 = 5e-5 s
```

```cpp
deltaT          5e-5;
adjustTimeStep  yes;
maxCo           0.8;
maxDeltaT       0.001;          // อนุญาตให้เพิ่มได้เรื่อยๆ
```

#### **Strategy 3: Adaptive Time Stepping**

```cpp
adjustTimeStep  yes;
maxCo           0.8;
maxDeltaT       0.1;

// สำหรับ compressible flows
maxCo           0.3;            // More restrictive
maxDi           10.0;           // Diffusion number
```

### HOW: Output Control Best Practices

```cpp
// Basic output
writeControl    timeStep;
writeInterval   100;

// Runtime output (monitor during run)
runTimeModifiable true;

// Save disk space
purgeWrite      3;              // เก็บเฉพาะ 3 ไฟล์ล่าสุด

// Additional outputs
writeFormat     ascii;
writePrecision  8;
```

**Output Frequency Guidelines:**

| Simulation Type | `writeInterval` |
|-----------------|-----------------|
| Steady-state debugging | 10-50 iterations |
| Steady-state production | 100-500 iterations |
| Transient (fast physics) | 0.001-0.01 s |
| Transient (slow physics) | 0.1-1.0 s |

---

## Part 2: fvSolution - Solvers & Algorithms

### WHAT: Linear Solvers

ทุก equation ใน CFD ถูกแปลงเป็น **linear system** $Ax=b$ — `fvSolution` บอกว่าใช้ solver ไหนแกะมัน

```cpp
solvers
{
    p
    {
        solver      GAMG;
        tolerance   1e-7;
        relTol      0.01;
        smoother    GaussSeidel;
    }
    
    U
    {
        solver      smoothSolver;
        smoother    GaussSeidel;
        tolerance   1e-8;
        relTol      0;
    }
    
    "(k|epsilon|omega)"
    {
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-6;
        relTol          0;
    }
}
```

### WHY: Solver Selection

#### **Pressure Equation: Why GAMG?**

Pressure Poisson equation เป็น **elliptic** — global effects propagate instantly

| Solver | Pros | Cons | Best For |
|--------|------|------|----------|
| **GAMG** | $O(N)$ — very fast for large meshes | Memory overhead | Large meshes (>100k cells), steady-state |
| PCG | Robust, simple | $O(N^{1.5})$ — slower | Small meshes, debugging |
| smoothSolver | Lightweight | Slow for large meshes | Very small cases |

**Physical Insight:** Multigrid (GAMG) ทำงานได้เร็วเพราะ:
- **Low-frequency errors** ถูกแก้บน coarse grids
- **High-frequency errors** ถูกแก้บน fine grids
- ทั้งสองเกิดพร้อมกัน — convergence รวดเร็ว

#### **Velocity Equation: Why smoothSolver?**

Momentum equation เป็น **convection-dominated** — non-symmetric, less elliptic

| Solver | Pros | Cons | Best For |
|--------|------|------|----------|
| **smoothSolver** | Fast, low memory | Not for very large meshes | General velocity, medium meshes |
| PBiCGStab | Robust for non-symmetric | Slower per iteration | Large meshes, bad quality |
| GAMG | Fast if working | Can diverge for non-symmetric | High-quality meshes only |

#### **Turbulence Equations: Why PBiCGStab?**

$k$, $\epsilon$, $\omega$ — สมการ scalar ที่มี source terms แรง และ convection-dominated

```cpp
// ทางเลือกอื่นหาก PBiCGStab ช้า
solver          GAMG;
tolerance       1e-6;
relTol          0;
```

### HOW: Tolerance Settings

#### **Absolute vs Relative Tolerance**

Solver หยุดเมื่อ **อย่างใดอย่างหนึ่ง** บรรลุ:

$$\|r\| < \text{tolerance} \quad \text{OR} \quad \frac{\|r\|}{\|r_0\|} < \text{relTol}$$

| Variable | `tolerance` | `relTol` | Rationale |
|----------|-------------|----------|-----------|
| p | 1e-7 | 0.01 | Pressure gradient drives flow — need accuracy |
| U | 1e-8 | 0 | Velocity field — tight absolute |
| Turbulence | 1e-6 | 0 | Less critical than p, U |

**Best Practice:** 
- ตั้ง `relTol` = 0.01-0.1 เพื่อ speed up
- ตั้ง `tolerance` ตาม table ด้านบนเพื่อความแม่นยำ
- Debugging: ใช้ `relTol` = 0 เพื่อ guarantee convergence

---

### WHAT: Under-Relaxation

### WHY: Why SIMPLE Needs Relaxation

SIMPLE algorithm ใช้ segregated approach — แก้ p และ U แยกกัน — แต่ p-U coupling แข็งแรงมาก!

**Physical Reasoning:**

- **ไม่มี time derivative** → ไม่มี natural damping
- Pressure correction $\Delta p$ มากเกินไป → velocity เปลี่ยนแรงเกิน → diverge
- **Under-relaxation** = ลดการเปลี่ยนแปลงในแต่ละ iteration

$$\phi_{new} = \phi_{old} + \alpha (\phi_{calc} - \phi_{old})$$

### HOW: Relaxation Factor Selection

```cpp
relaxationFactors
{
    fields    { p 0.3; }
    equations { U 0.7; "(k|epsilon)" 0.7; }
}
```

| Variable | Range | Lower = | Higher = | When to Adjust |
|----------|-------|---------|----------|----------------|
| p | 0.2-0.5 | More stable | Faster | Diverging → lower; Too slow → raise |
| U | 0.5-0.8 | More stable | Faster | Same as p |
| Turbulence | 0.5-0.8 | More stable | Faster | Often keep at 0.8 |

**Practical Guide:**

```cpp
// Starting point (conservative)
fields    { p 0.2; }
equations { U 0.5; k 0.5; epsilon 0.5; }

// After 100 iterations, if stable
fields    { p 0.3; }
equations { U 0.7; k 0.8; epsilon 0.8; }

// Aggressive (good mesh, initialized)
fields    { p 0.5; }
equations { U 0.8; k 0.8; epsilon 0.8; }
```

---

### WHAT: Algorithm Settings

```cpp
SIMPLE
{
    nNonOrthogonalCorrectors 1;
    pRefCell    0;
    pRefValue   0;
    residualControl 
    {
        p   1e-5;
        U   1e-5;
        epsilon 1e-4;
    }
}

PIMPLE
{
    nOuterCorrectors 2;
    nCorrectors      2;
    nNonOrthogonalCorrectors 1;
    
    // Optional: residual control for transient
    residualControl
    {
        p   1e-4;
        U   1e-4;
    }
}
```

### WHY: Understanding Correctors

| Corrector | Purpose | When to Increase |
|-----------|---------|------------------|
| `nNonOrthogonalCorrectors` | Fix mesh non-orthogonality errors | Mesh has > 50° non-orthogonality |
| `nOuterCorrectors` (PIMPLE) | Outer iterations for p-U coupling | Tight coupling needed |
| `nCorrectors` (PIMPLE) | Pressure equation solves per time step | Default 2 is usually fine |

### HOW: Residual Control

```cpp
// Stop automatically when converged
SIMPLE
{
    residualControl
    {
        p       1e-5;
        U       1e-5;
        epsilon 1e-4;
    }
}
```

**Guidelines:**

| Variable | Steady-State | Transient |
|----------|--------------|-----------|
| p | 1e-5 - 1e-6 | 1e-4 - 1e-5 |
| U | 1e-5 - 1e-6 | 1e-4 - 1e-5 |
| k, ε | 1e-4 - 1e-5 | 1e-3 - 1e-4 |

---

## Part 3: fvSchemes - Discretization

### WHAT: Discretization Schemes

`fvSchemes` กำหนดวิธีแปลง derivatives เป็นพีชคณิต — มีผลต่อ **accuracy** และ **stability** โดยตรง

```cpp
gradSchemes
{
    default         Gauss linear;
}

divSchemes
{
    default         none;
    div(phi,U)      Gauss upwind;           // 1st order
    div(phi,k)      Gauss upwind;
    div(phi,epsilon) Gauss upwind;
    div((nuEff*dev2(T(grad(U))))) Gauss linear;
}

laplacianSchemes
{
    default         Gauss linear corrected;
}

interpolationSchemes
{
    default         linear;
}

snGradSchemes
{
    default         corrected;
}
```

### WHY: Scheme Selection

#### **Gradient Schemes**

| Scheme | Accuracy | Stability | Best For |
|--------|----------|-----------|----------|
| `Gauss linear` | 2nd order | Good | Most cases |
| `Gauss linear corrected` | 2nd order + non-orthogonal correction | Good | Non-orthogonal meshes (>30°) |
| `leastSquares` | 2nd order | Very stable | Bad quality meshes |

**Physical Reasoning:** Gradients ใช้สำหรับ:
- Convection terms
- Diffusion terms
- Reconstruction

Non-orthogonal correction เพิ่ม accuracy สำหรับ meshes ที่ไม่ aligned

#### **Divergence Schemes — Critical!**

| Scheme | Order | Boundedness | Numerical Diffusion | When to Use |
|--------|-------|-------------|---------------------|-------------|
| **upwind** | 1st | ✓ Yes | High | Starting, stability |
| **linearUpwind** | 2nd | ✓ Yes | Medium | Production runs |
| **linearUpwindV** | 2nd | ✓ Yes | Medium | Vector-graded meshes |
| **QUICK** | 3rd | ✗ No | Low | Structured meshes only |
| **limitedLinearV 1** | 2nd | ✓ Yes | Low | High accuracy, unstructured |

**Physical Insight:**
- **Upwind:** ใช้ค่าจาก upstream cell — มี numerical diffusion สูง แต่ stable
- **Linear:** Interpolation — accurate แต่ oscillate ได้บน sharp gradients
- **Limited:** Blended — ได้ accuracy ของ linear แต่มี boundedness ของ upwind

#### **Laplacian Schemes**

| Scheme | Purpose |
|--------|---------|
| `Gauss linear` | Basic diffusion |
| `Gauss linear corrected` | Add non-orthogonal correction |

**Rule of Thumb:** เสมอใช้ `corrected` สำหรับ meshes ที่มี non-orthogonality > 30°

### HOW: Scheme Selection Strategy

#### **Phase 1: Stabilize (First 100 iterations)**

```cpp
divSchemes
{
    div(phi,U)      Gauss upwind;
    div(phi,k)      Gauss upwind;
    div(phi,epsilon) Gauss upwind;
}
```

#### **Phase 2: Accuracy (After stable)**

```cpp
divSchemes
{
    div(phi,U)      Gauss linearUpwind grad(U);
    div(phi,k)      Gauss linearUpwind grad(k);
    div(phi,epsilon) Gauss linearUpwind grad(epsilon);
}
```

#### **Phase 3: High Accuracy (Final runs)**

```cpp
divSchemes
{
    div(phi,U)      Gauss limitedLinearV 1;
    div(phi,k)      Gauss limitedLinearV 1;
    div(phi,epsilon) Gauss limitedLinearV 1;
}
```

---

## Part 4: Convergence Monitoring

### WHAT: Residuals & Convergence

**Residual** = ความผิดพลาดที่เหลืออยู่หลังจาก solver ทำงาน

$$r = b - Ax$$

### WHY: Multiple Convergence Criteria

เช็คเฉพาะ residual ไม่พอ! — ต้อง monitor **physical quantities** ด้วย

| Criterion | What It Shows |
|-----------|---------------|
| Residuals | Equation balance |
| Forces/coefficients | Physical convergence |
| Probes | Local behavior |
| Mass balance | Global conservation |

### HOW: Function Objects

```cpp
functions
{
    // 1. Residual monitoring
    residuals
    {
        type            residuals;
        fields          (p U k epsilon);
        writeResidualFields on;
    }
    
    // 2. Force monitoring (aerodynamics)
    forces
    {
        type            forces;
        libs            ("libforces.so");
        writeControl    timeStep;
        writeInterval   1;
        patches         (airfoil);
        rho             rhoInf;
        rhoInf          1.225;
        CofR            (0 0 0);     // Center of rotation
        pitchAxis       (0 1 0);     // Pitch axis
    }
    
    // 3. Force coefficients
    forceCoeffs
    {
        type            forceCoeffs;
        libs            ("libforces.so");
        patches         (airfoil);
        rhoInf          1.225;
        CofR            (0 0 0);
        liftDir         (0 1 0);
        dragDir         (1 0 0);
        pitchAxis       (0 0 1);
        magUInf         50.0;
        lRef            1.0;         // Reference length
        Aref            1.0;         // Reference area
    }
    
    // 4. Probe sampling
    probeLocations
    {
        type            probes;
        libs            ("libsampling.so");
        writeControl    timeStep;
        writeInterval   10;
        probeLocations
        (
            (0.1 0 0)
            (0.2 0 0)
            (0.5 0 0)
        );
        fields          (p U k epsilon);
    }
    
    // 5. Surface sampling
    surfaceSampling
    {
        type            surfaces;
        libs            ("libsampling.so");
        writeControl    timeStep;
        writeInterval   100;
        surfaceFormat   vtk;
        fields          (p U);
        surfaces
        {
            midPlane
            {
                type            cuttingPlane;
                plane           pointAndNormalDict;
                pointAndNormalDict
                {
                    point   (0 0 0);
                    normal  (0 0 1);
                }
                interpolate true;
            }
        }
    }
}
```

---

## Part 5: Troubleshooting Guide

### Diagnostic Table

| Symptom | Likely Cause | Solution | File to Edit |
|---------|--------------|----------|--------------|
| **Immediate divergence** (first 10 iters) | Severe mesh problem | Run `checkMesh`, fix geometry | N/A (remesh) |
| **Pressure spikes** | Wrong BC, bad mesh | Check p BCs, especially outlets | `0/p` |
| **Residuals plateau** | Poor initialization | Map from similar case, use potentialFoam | `0/` |
| **Slow convergence** | Relaxation too low | Increase relaxation factors gradually | `system/fvSolution` |
| **Oscillating residuals** | Relaxation too high | Decrease relaxation, switch to upwind | `system/fvSolution`, `system/fvSchemes` |
| **Continuity errors high** | Non-orthogonal mesh | Increase `nNonOrthogonalCorrectors` | `system/fvSolution` |
| **Turbulence blows up** | Negative k, ε | Use bounded schemes, check turbulence BCs | `system/fvSchemes`, `0/*` |
| **NaN in fields** | Division by zero, negative sqrt | Check initial conditions, add limiters | `0/*`, `system/fvSchemes` |

### Specific Error Messages

#### **Error: "Maximum number of iterations exceeded"**

```cpp
// In fvSolution
solvers
{
    p
    {
        solver          GAMG;
        tolerance       1e-7;     // Relax this
        relTol          0.05;     // Or add this
        maxIter         1000;     // Increase if needed
    }
}
```

#### **Error: "Negative temperature T"**

```cpp
// In fvSchemes — use bounded scheme
divSchemes
{
    div(phi,T)   Gauss limitedLinearV 1;
}

// Or add in thermophysicalProperties
// TMin          200;  // Prevent negative
```

#### **Error: "Continuity error cannot be satisfied"**

```cpp
// In fvSolution
SIMPLE
{
    nNonOrthogonalCorrectors 3;  // Increase from 1
}
```

### Mesh Quality Check

```bash
checkMesh -allGeometry -allTopology
```

| Metric | Good | Warning | Critical | Action |
|--------|------|---------|----------|--------|
| Non-orthogonality | < 50° | 50-70° | > 70° | Add correctors, improve mesh |
| Skewness | < 0.5 | 0.5-0.8 | > 0.8 | Remesh |
| Aspect ratio | < 100 | 100-500 | > 500 | Refine |
| Face-weight | > 0.05 | 0.01-0.05 | < 0.01 | Remesh |

---

## Part 6: Best Practices Summary

### Startup Checklist

1. **Mesh quality:** `checkMesh -allGeometry -allTopology`
2. **Conservative start:** Upwind schemes, low relaxation
3. **Monitor early:** Set up function objects before first run
4. **Save disk:** `purgeWrite 3` for debugging
5. **Runtime control:** `runTimeModifiable yes`

### Parameter Tuning Order

```
1. Check mesh (no point tuning bad mesh)
   ↓
2. Start with upwind, conservative relaxation
   ↓
3. Monitor residuals + physical quantities
   ↓
4. Once stable: increase relaxation
   ↓
5. Switch to 2nd order schemes
   ↓
6. Fine-tune for accuracy
```

### Common Pitfalls to Avoid

| Mistake | Why It's Bad | Correct Approach |
|---------|--------------|------------------|
| Starting with high-order schemes | Unstable, diverges | Start with upwind, switch later |
| Ignoring mass balance | Looks converged but wrong | Monitor `continuityErrors` |
| Over-relaxation on bad mesh | Diverges | Improve mesh first |
| `relTol` = 1 (too loose) | Never converges properly | Keep 0.01-0.1 |
| No physical monitoring | Can have wrong answer | Always monitor forces, probes |

---

## Concept Check

<details>
<summary><b>1. ทำไม SIMPLE ต้องใช้ under-relaxation แต่ PIMPLE ไม่จำเป็น?</b></summary>

**SIMPLE:** Steady-state, ไม่มี time derivative → ไม่มี natural damping → pressure correction สามารถทำให้ velocity เปลี่ยนแรงเกินไป → ต้องใช้ relaxation เพื่อลด update ในแต่ละ iteration

**PIMPLE:** มี time step ($\Delta t$) ที่เอง → time derivative ทำหน้าที่เป็น damping → pressure correction มีผลน้อยกว่า → ไม่จำเป็นต้องใช้ relaxation (แต่ใช้ได้ถ้าต้องการความเสถียร)
</details>

<details>
<summary><b>2. `tolerance` vs `relTol` ต่างกันอย่างไร? อย่างใดตั้งเป็น 0?</b></summary>

**tolerance** = Absolute residual target (e.g., 1e-7)  
**relTol** = Relative reduction from initial residual (e.g., 0.01 = 1% ของค่าเริ่มต้น)

Solver หยุดเมื่อ **อย่างใดอย่างหนึ่ง** บรรลุ

**Best Practice:**
- ตั้ง `tolerance` ตามความแม่นยำที่ต้องการ (p: 1e-7, U: 1e-8)
- ตั้ง `relTol` = 0.01-0.1 เพื่อ speed up หาก initial residual สูง
- Debugging: `relTol` = 0 เพื่อ guarantee absolute convergence
</details>

<details>
<summary><b>3. ทำไม GAMG เร็วกว่า PCG สำหรับ pressure equation?</b></summary>

**Pressure Poisson equation** เป็น elliptic — global effects propagate instantly → มี **low-frequency errors** (slow-converging global modes)

**PCG:** Single-grid — ลด error ทุก frequency ด้วยความเร็วใกล้เคียงกัน → iterations มาก

**GAMG:** Multigrid — แก้ low-frequency errors บน coarse grids (where they look high-frequency) → ลด global errors ได้เร็วมาก → $O(N)$ vs $O(N^{1.5})$

**สรุป:** GAMG ใช้ multigrid hierarchy ทำให้แก้ global modes ได้เร็วกว่า PCG มากสำหรับ large meshes
</details>

<details>
<summary><b>4. แก้ปัญหา residuals plateau ที่ 1e-4 ได้อย่างไร?</b></summary>

**Plateau** อาจเป็น:
1. **Local recirculation** — residuals สูงใน small region แต่ global ดี
2. **Poor initialization** — solution ไกลเกินไปจาก converged state
3. **Relaxation too low** — update ช้าเกินไป

**Solutions:**
1. **Check physical convergence:** Monitor forces, coefficients — ถ้า converge แล้ว residuals ยังสูง → เป็น local issue เท่านั้น
2. **Reinitialize:** `mapFields` from similar case หรือใช้ `potentialFoam` เริ่มต้น
3. **Increase relaxation:** ค่อยๆ เพิ่มจาก 0.3 → 0.5 → 0.7 สำหรับ p
4. **Switch schemes:** ลอง `limitedLinearV` แทน `upwind`
5. **Check mesh:** `checkMesh` — อาจมี bad cells ที่กำลังบ่มเพาะ residuals
</details>

<details>
<summary><b>5. เลือก discretization scheme สำหรับ steady-state RANS อย่างไร?</b></summary>

**Phase 1 — Stabilization (0-200 iterations):**
```cpp
divSchemes
{
    div(phi,U)      Gauss upwind;
    div(phi,k)      Gauss upwind;
    div(phi,epsilon) Gauss upwind;
}
```
High numerical diffusion → stable → get rough solution

**Phase 2 — Transition (200-500 iterations):**
```cpp
divSchemes
{
    div(phi,U)      Gauss linearUpwind grad(U);
    div(phi,k)      Gauss linearUpwind grad(k);
    div(phi,epsilon) Gauss linearUpwind grad(epsilon);
}
```
2nd order → better accuracy → maintain stability

**Phase 3 — Production (500+ iterations):**
```cpp
divSchemes
{
    div(phi,U)      Gauss limitedLinearV 1;
    div(phi,k)      Gauss limitedLinearV 1;
    div(phi,epsilon) Gauss limitedLinearV 1;
}
```
High accuracy, bounded → best results

**Key:** Never start with high-order schemes on initialized zero field!
</details>

---

## Key Takeaways

### What to Remember

1. **controlDict** = Time & output control
   - **CFL < 1** for transient stability
   - `adjustTimeStep yes` + `maxCo 0.8` = adaptive time stepping
   - `purgeWrite 3` = save disk space

2. **fvSolution** = Solvers & algorithms
   - **GAMG** for pressure (fast, elliptic)
   - **PBiCGStab** for turbulence (robust, non-symmetric)
   - **Relaxation** = SIMPLE's safety net (p: 0.3, U: 0.7)
   - `nNonOrthogonalCorrectors` fixes mesh errors

3. **fvSchemes** = Discretization
   - **Upwind** = stable but diffusive (start here)
   - **limitedLinearV** = accurate + bounded (end here)
   - **Never** start with high-order on bad initialization

4. **Convergence** = multiple criteria
   - Residuals ↓ AND forces stabilize AND mass balance OK
   - Monitor with function objects (`forces`, `probes`)

5. **Troubleshooting flow**
   - Divergence → lower relaxation, use upwind
   - Plateau → check initialization, increase relaxation
   - Slow → improve mesh, switch to GAMG

---

## Related Documents

- **บทก่อนหน้า:** [02_Standard_Solvers.md](02_Standard_Solvers.md) — เรียนรู้ solvers และ algorithms
- **บทถัดไป:** [../02_PRESSURE_VELOCITY_COUPLING/00_Overview.md](../02_PRESSURE_VELOCITY_COUPLING/00_Overview.md) — เจาะลึก SIMPLE/PISO/PIMPLE