# บันทึกบทเรียน: Testing & Validation — การสร้างความเชื่อมั่นใน CFD

**วันที่:** 28 ธันวาคม 2025

> **สิ่งที่จะได้เรียนรู้:**
> 1. Verification vs Validation — ความแตกต่างที่สำคัญ
> 2. Method of Manufactured Solutions (MMS)
> 3. Grid Convergence Index (GCI)
> 4. Validation Benchmarks
> 5. Testing & Debugging

---

## 1. ทำไม V&V สำคัญ?

> **"A CFD result without uncertainty quantification is just a pretty picture"**

### 1.1 The Fundamental Questions

| Question | Process | Target |
|----------|---------|--------|
| **"Am I solving the equations correctly?"** | Verification | Code, Numerics |
| **"Am I solving the right equations?"** | Validation | Physics, Model |

### 1.2 V&V Framework

```
┌─────────────────────────────────────────────────────────────┐
│                    V&V Framework                            │
├──────────────────────────┬──────────────────────────────────┤
│       VERIFICATION       │          VALIDATION              │
├──────────────────────────┼──────────────────────────────────┤
│ • Code หยิบสมการถูกไหม?   │ • สมการจำลอง physics ถูกไหม?      │
│ • Discretization ถูกไหม?  │ • Model assumptions ถูกไหม?      │
│                          │                                  │
│ Methods:                 │ Methods:                         │
│ • MMS                    │ • Comparison with experiments    │
│ • Grid Convergence       │ • Benchmark cases                │
│ • Conservation checks    │ • Sensitivity analysis           │
└──────────────────────────┴──────────────────────────────────┘
```

### 1.3 Real-World Impact

| Without V&V | With V&V |
|-------------|----------|
| "Cd = 0.35" | "Cd = 0.35 ± 0.02 (GCI 95%)" |
| Meaningless | Publishable, defensible |

---

## 2. Verification — Code & Solution

### 2.1 Types of Verification

| Type | Question | Method |
|------|----------|--------|
| **Code Verification** | ใส่สมการถูกไหม? | MMS, Analytical solutions |
| **Solution Verification** | ลู่เข้าหรือยัง? | Grid convergence, Residuals |
| **Calculation Verification** | คำนวณถูกไหม? | Conservation checks |

### 2.2 Quick Verification Checks

```bash
# 1. Check residuals
grep "Solving for" log.simpleFoam | tail -20

# 2. Check continuity
grep "continuity" log.simpleFoam

# 3. Conservation (mass flux)
postProcess -func 'inletMassFlowRate'
postProcess -func 'outletMassFlowRate'

# 4. Check mesh
checkMesh
```

---

## 3. Method of Manufactured Solutions (MMS)

> **"The gold standard for code verification"**

### 3.1 The Idea

```
=== Normal CFD ===
Known: สมการ + BCs
Unknown: Solution φ

=== MMS (Reverse) ===
Known: Solution φ_exact (ที่ "ผลิต" ขึ้นมา)
Calculate: Source term S ที่ทำให้สมการเป็นจริง
Verify: φ_numerical ≈ φ_exact ?
```

### 3.2 MMS Workflow

```
1. Choose φ_exact = φ₀ sin(πx/L) cos(πy/L)
       ↓
2. Substitute into equation: L[φ_exact] = S
       ↓
3. Add S as source term in solver
       ↓
4. Run simulation → get φ_numerical
       ↓
5. Compare: Error = φ_numerical - φ_exact
       ↓
6. Run on finer meshes → Check order of accuracy
```

### 3.3 Example: Diffusion Equation

**Equation:**
$$\nabla \cdot (D \nabla \phi) = 0$$

**Manufactured Solution:**
$$\phi_{exact} = \phi_0 \sin\left(\frac{\pi x}{L}\right) \cos\left(\frac{\pi y}{L}\right)$$

**Compute Source Term:**
$$S = -D \nabla^2 \phi_{exact} = \phi_0 D \frac{2\pi^2}{L^2} \sin\left(\frac{\pi x}{L}\right) \cos\left(\frac{\pi y}{L}\right)$$

**Modified Equation:**
$$\nabla \cdot (D \nabla \phi) + S = 0$$

### 3.4 OpenFOAM Implementation

```cpp
// สร้าง Manufactured Solution
volScalarField phiExact
(
    IOobject("phiExact", runTime.timeName(), mesh, ...),
    mesh,
    dimensionedScalar("zero", dimless, 0.0)
);

// คำนวณ phiExact ที่ทุก cell
const volVectorField& C = mesh.C();
forAll(C, celli)
{
    scalar x = C[celli].x();
    scalar y = C[celli].y();
    phiExact[celli] = phi0 * Foam::sin(pi * x / L) 
                          * Foam::cos(pi * y / L);
}

// คำนวณ Source Term
volScalarField sourceTerm = D * fvc::laplacian(phiExact);

// แก้สมการ
solve(fvm::laplacian(D, phi) == sourceTerm);

// คำนวณ Error
volScalarField error = phi - phiExact;
scalar L2norm = Foam::sqrt(sum(magSqr(error) * mesh.V()).value());

Info<< "L2 Error: " << L2norm << endl;
```

### 3.5 Verify Order of Accuracy

**Run on multiple meshes:**

| Mesh | Cells | Δx | L2 Error | Order |
|------|-------|-----|----------|-------|
| Coarse | 20² | 0.05 | 1.2e-3 | — |
| Medium | 40² | 0.025 | 3.0e-4 | 2.0 |
| Fine | 80² | 0.0125 | 7.5e-5 | 2.0 |

**Order of Accuracy:**
$$p = \frac{\log(E_1/E_2)}{\log(\Delta x_1/\Delta x_2)} = \frac{\log(1.2e-3/3.0e-4)}{\log(0.05/0.025)} = 2.0$$

**If p ≈ 2 (for 2nd order scheme) → Code verified! ✅**

---

## 4. Grid Convergence Index (GCI)

> **"มาตรฐานทองคำสำหรับ Mesh Independence Study"**

### 4.1 Why GCI?

**Problem:** ทุกคนทำ mesh study แต่รายงานไม่มีมาตรฐาน

**Solution:** GCI ให้วิธีมาตรฐานในการ:
1. ประมาณ order of accuracy จาก results
2. คำนวณ uncertainty ของ mesh
3. รายงานผลพร้อม error band

### 4.2 GCI Procedure

```
Step 1: Run 3 meshes (Coarse, Medium, Fine)
        h₃ > h₂ > h₁ (h = characteristic size)
        Refinement ratio r = h₂/h₁ ≈ 2

Step 2: Extract quantity of interest (Cd, Cl, etc.)
        f₁ (fine), f₂ (medium), f₃ (coarse)

Step 3: Calculate apparent order
        ε₂₁ = f₂ - f₁
        ε₃₂ = f₃ - f₂
        p = ln(|ε₃₂/ε₂₁|) / ln(r)

Step 4: Calculate GCI
        GCI = Fs × |ε₂₁/f₁| / (rᵖ - 1)
        
        Fs = 1.25 (for 3+ grids)
        Fs = 3.0  (for 2 grids, not recommended)
```

### 4.3 GCI Example

**Drag coefficient from 3 meshes:**

| Mesh | Cells | Cd |
|------|-------|-----|
| Fine | 2M | 0.345 |
| Medium | 1M | 0.352 |
| Coarse | 500k | 0.368 |

**Calculate:**
```
ε₂₁ = 0.352 - 0.345 = 0.007
ε₃₂ = 0.368 - 0.352 = 0.016

r = (2M/1M)^(1/3) = 1.26  (assuming similar mesh)

p = ln(|0.016/0.007|) / ln(1.26) = 3.5

GCI = 1.25 × |0.007/0.345| / (1.26^3.5 - 1) = 2.1%

Reported: Cd = 0.345 ± 0.007 (GCI 95% confidence)
```

### 4.4 Python GCI Calculator

```python
import numpy as np

def calculate_gci(f1, f2, f3, r=2.0, Fs=1.25):
    """
    Calculate Grid Convergence Index
    
    Parameters:
    f1: Fine mesh result
    f2: Medium mesh result  
    f3: Coarse mesh result
    r: Grid refinement ratio (h2/h1)
    Fs: Safety factor (1.25 for 3 grids)
    
    Returns:
    p: Apparent order of accuracy
    f_exact: Extrapolated exact value
    GCI: Grid Convergence Index (%)
    """
    eps21 = f2 - f1
    eps32 = f3 - f2
    
    # Check convergence type
    if eps21 * eps32 < 0:
        print("Warning: Oscillatory convergence!")
    
    # Apparent order
    p = np.log(abs(eps32 / eps21)) / np.log(r)
    
    # Richardson extrapolation
    f_exact = f1 + (f1 - f2) / (r**p - 1)
    
    # GCI
    GCI = (Fs * abs((f2 - f1) / f1)) / (r**p - 1) * 100
    
    return p, f_exact, GCI

# Example
p, f_exact, gci = calculate_gci(0.345, 0.352, 0.368, r=1.26)

print(f"Apparent Order: {p:.2f}")
print(f"Extrapolated Value: {f_exact:.4f}")
print(f"GCI: {gci:.2f}%")
```

### 4.5 GCI Interpretation

| Observed Order | Expected | Interpretation |
|----------------|----------|----------------|
| p ≈ 2.0 | 2nd order | ✅ Scheme working correctly |
| p << expected | — | Mesh not in asymptotic range |
| p >> expected | — | Lucky cancellation? Check! |
| Oscillatory | — | Problem! Check BCs, scheme |

---

## 5. Validation — Physics & Models

### 5.1 Validation vs Verification

| Aspect | Verification | Validation |
|--------|--------------|------------|
| **Reference** | Analytical/MMS | Experiments |
| **Question** | Coding correct? | Physics correct? |
| **Error source** | Numerics | Modeling |

### 5.2 Standard Benchmarks

| Benchmark | Physics | Reference |
|-----------|---------|-----------|
| **Lid-driven cavity** | 2D laminar recirculation | Ghia et al. (1982) |
| **Backward-facing step** | Separation, reattachment | Driver & Seegmiller (1985) |
| **Turbulent channel** | Wall-bounded turbulence | Kim et al. (1987) DNS |
| **Ahmed body** | External aerodynamics | Ahmed et al. (1984) |
| **Pipe flow** | Developed profiles | Moody, Blasius |

### 5.3 Validation Metrics

**Quantitative:**

$$RMSE = \sqrt{\frac{1}{N} \sum_{i=1}^{N} (CFD_i - Exp_i)^2}$$

$$R^2 = 1 - \frac{\sum(CFD_i - Exp_i)^2}{\sum(Exp_i - \bar{Exp})^2}$$

| Metric | Good Value | Interpretation |
|--------|------------|----------------|
| RMSE | < 5% of range | Low overall error |
| R² | > 0.95 | Strong correlation |
| Max Error | < 10% | No outliers |

### 5.4 Validation Process

```
1. Select Benchmark
   ├── Published experimental data
   ├── Well-documented geometry
   └── Relevant to your physics
   
2. Setup Case
   ├── Match geometry exactly
   ├── Match flow conditions
   ├── Document all settings
   
3. Run Simulation
   ├── Verify convergence
   ├── Check mesh independence (GCI)
   └── Multiple turbulence models if needed
   
4. Extract Data
   ├── Same locations as experiment
   ├── Same quantities
   └── Proper averaging (if needed)
   
5. Compare & Report
   ├── Overlay plots
   ├── Compute metrics
   └── Document discrepancies
```

### 5.5 Example: Lid-Driven Cavity

```cpp
// Case setup
// - Square cavity, Re = 1000
// - Top lid moving at U = 1 m/s
// - Extract u-velocity along vertical centerline
// - Compare with Ghia et al. data
```

**Ghia et al. Reference Data (Re = 1000):**
| y/L | u/U |
|-----|-----|
| 0.0000 | 0.00000 |
| 0.0625 | -0.20581 |
| 0.5000 | -0.21090 |
| 0.9688 | 0.84123 |
| 1.0000 | 1.00000 |

---

## 6. Testing & Debugging

### 6.1 Check Hierarchy

```
Level 1: Does it run?
├── Compile without errors
├── Start without crash
└── Complete some iterations

Level 2: Does it converge?
├── Residuals decreasing
├── No oscillation
└── Reaches target tolerance

Level 3: Is it physically correct?
├── Conservation satisfied
├── Qualitative behavior OK
└── Matches expected trends

Level 4: Is it accurate?
├── Mesh independent (GCI)
├── Scheme appropriate
└── Matches validation data
```

### 6.2 Common Issues & Checks

| Issue | Check | Fix |
|-------|-------|-----|
| **Divergence** | Residuals exploding | Lower relaxation, check BC |
| **No convergence** | Residuals plateau | Increase iterations, check mesh |
| **Mass imbalance** | continuity error | Check BCs, mesh quality |
| **Wrong results** | Compare with theory | Check units, dimensions |

### 6.3 Debugging Tools

```bash
# Check mesh quality
checkMesh -allGeometry -allTopology

# Check boundary conditions
grep -r "type" 0/ | head -20

# Monitor residuals
pyFoamPlotRunner.py simpleFoam

# Check conservation
postProcess -func 'faceZoneFlow'
```

### 6.4 Unit Testing

```cpp
// Test individual functions
TEST(VectorTest, Magnitude)
{
    vector v(3, 4, 0);
    EXPECT_DOUBLE_EQ(mag(v), 5.0);
}

TEST(FieldTest, Average)
{
    scalarField f(100, 2.0);
    EXPECT_DOUBLE_EQ(average(f), 2.0);
}
```

---

## 7. Quick Reference

### 7.1 Verification Methods

| Method | Use Case |
|--------|----------|
| MMS | Code verification |
| GCI | Mesh independence |
| Conservation | Flux balance |
| Residuals | Convergence |

### 7.2 Validation Metrics

| Metric | Formula |
|--------|---------|
| RMSE | √(Σ(CFD-Exp)²/N) |
| R² | 1 - Σ(CFD-Exp)²/Σ(Exp-mean)² |
| RE | (CFD-Exp)/Exp × 100% |

### 7.3 Common Benchmarks

| Case | Solver | Physics |
|------|--------|---------|
| Cavity | icoFoam | Laminar |
| BackStep | simpleFoam | RANS |
| Channel | simpleFoam | Turbulence |
| Ahmed | simpleFoam | External aero |

---

## 8. 🧠 Advanced Concept Check

### Level 1: Fundamentals

<details>
<summary><b>Q1: Verification กับ Validation ต่างกันอย่างไร?</b></summary>

**คำตอบ:**

| Aspect | Verification | Validation |
|--------|--------------|------------|
| **Question** | Solving equations correctly? | Solving right equations? |
| **Reference** | Analytical, MMS | Experiments |
| **Focus** | Numerics, coding | Physics, modeling |
| **Outcome** | Code is bug-free | Model is appropriate |

**Analogy:**
- Verification: "I built the car according to blueprint"
- Validation: "The car actually drives well on roads"

</details>

<details>
<summary><b>Q2: ทำไม MMS ต้องเพิ่ม Source Term?</b></summary>

**คำตอบ:**

**เพราะ Manufactured Solution ไม่ได้เป็นคำตอบจริงของสมการเดิม!**

ตัวอย่าง:
- สมการ: ∇²φ = 0 (Laplace)
- ถ้าเลือก φ_exact = sin(x)cos(y)
- คำนวณ: ∇²(sin(x)cos(y)) = -2sin(x)cos(y) ≠ 0

ดังนั้นต้องเพิ่ม Source Term:
- สมการใหม่: ∇²φ + S = 0
- โดย S = 2sin(x)cos(y)

ตอนนี้ φ_exact = sin(x)cos(y) เป็นคำตอบจริง!

</details>

<details>
<summary><b>Q3: GCI Safety Factor Fs ทำหน้าที่อะไร?</b></summary>

**คำตอบ:**

**Fs = ค่าประกัน (Insurance Factor)**

Richardson Extrapolation สมมติว่า:
1. อยู่ใน asymptotic range
2. Order p คงที่
3. ไม่มี higher-order terms

แต่ในความจริงสมมติฐานอาจไม่จริง 100% → ต้องเผื่อ

| Grids | Fs | Reason |
|-------|-----|--------|
| 3+ | 1.25 | มีข้อมูลมากพอประมาณ p |
| 2 | 3.0 | ไม่รู้ p จริง → conservative |

</details>

### Level 2: Practical

<details>
<summary><b>Q4: ถ้า GCI ได้ p = 0.5 แทนที่จะเป็น 2.0 เกิดจากอะไร?</b></summary>

**คำตอบ:**

**สาเหตุที่เป็นไปได้:**

1. **ยังไม่อยู่ใน Asymptotic Range**
   - Mesh หยาบเกินไป
   - Error dominanted by other sources

2. **First-order dominates**
   - BC ไม่ถูกต้อง
   - Interface ไม่ smooth
   - Scheme reverts to 1st order

3. **Discontinuities**
   - Shock waves
   - Contact surfaces
   - Reduce order automatically

4. **Implementation bug**
   - Scheme labeled 2nd order แต่ code ผิด

**วิธีแก้:**
- ใช้ mesh ละเอียดขึ้น
- ตรวจสอบ BCs
- ใช้ MMS verify code

</details>

<details>
<summary><b>Q5: เลือก Benchmark อย่างไรให้เหมาะกับงาน?</b></summary>

**คำตอบ:**

**Criteria:**

1. **Physics ใกล้เคียง**
   - Laminar vs Turbulent
   - Internal vs External
   - Compressible vs Incompressible

2. **ข้อมูลครบถ้วน**
   - Geometry published
   - BCs documented
   - Experimental data available

3. **Widely used**
   - ผู้อื่น validate แล้ว
   - Results comparable

| My Problem | Choose Benchmark |
|------------|------------------|
| Pipe flow | Poiseuille, turbulent channel |
| External aero | Ahmed body, NACA |
| Heat transfer | Natural convection cavity |
| Turbulence model | Backward step, channel |

</details>

<details>
<summary><b>Q6: R² = 0.8 แปลว่าอะไร ดีหรือไม่ดี?</b></summary>

**คำตอบ:**

**R² = Coefficient of Determination**

$$R^2 = 1 - \frac{\sum(CFD_i - Exp_i)^2}{\sum(Exp_i - \bar{Exp})^2}$$

| R² | Interpretation |
|----|----------------|
| 1.0 | Perfect match |
| 0.9-1.0 | Excellent |
| 0.8-0.9 | Good |
| 0.7-0.8 | Acceptable |
| < 0.7 | Poor |

**R² = 0.8:**
- 80% ของ variance ถูก explain
- 20% ยังมี discrepancy
- **For CFD: marginal to acceptable**

**Context matters:**
- Simple laminar: R² > 0.95 expected
- Complex turbulent: R² > 0.8 acceptable

</details>

### Level 3: Advanced

<details>
<summary><b>Q7: ทำไมต้องใช้ 3 meshes ใน GCI?</b></summary>

**คำตอบ:**

**Richardson Extrapolation:**
$$f = f_{exact} + Ch^p$$

**Unknowns:** f_exact, C, p (3 unknowns)
**Equations needed:** 3 (จาก 3 meshes)

| Meshes | Can determine |
|--------|---------------|
| 2 | f_exact (assume p) |
| 3 | f_exact + p (calculated) |
| 4+ | f_exact + p + verify |

**ถ้ามี 2 meshes:**
- ต้อง assume p (dangerous!)
- ใช้ Fs = 3.0 ชดเชย

**ถ้ามี 3+ meshes:**
- คำนวณ p จาก data
- ตรวจสอบว่า asymptotic
- ใช้ Fs = 1.25

</details>

<details>
<summary><b>Q8: Conservation Check ทำอย่างไร?</b></summary>

**คำตอบ:**

**Mass Conservation:**
$$\sum \dot{m}_{in} = \sum \dot{m}_{out}$$

```bash
# OpenFOAM
postProcess -func 'patchFlux(phi)'

# Or in log
grep "sum local" log.simpleFoam
```

**Expected:**
- Continuity error < 1e-6
- Mass imbalance < 0.1%

**Momentum Conservation:**
$$\sum F = \dot{m}_{out}U_{out} - \dot{m}_{in}U_{in}$$

**Energy Conservation:**
$$\sum Q = \dot{m}C_p(T_{out} - T_{in})$$

**If not conserved:**
- Check BCs
- Check mesh at boundaries
- Check solver convergence

</details>

<details>
<summary><b>Q9: MMS vs Analytical Solutions ต่างกันอย่างไร?</b></summary>

**คำตอบ:**

| Aspect | Analytical | MMS |
|--------|------------|-----|
| **Solution** | From physics | Invented |
| **Availability** | Limited, simple cases | Any case! |
| **Complexity** | Often simple geometry | Any geometry |
| **Tests** | Whole solver | Each term separately |

**Analytical Solution:**
- ต้องหาคำตอบ exact ซึ่งมีแค่บางกรณี
- เช่น: Poiseuille flow, Couette flow

**MMS:**
- "ผลิต" คำตอบขึ้นมาเอง
- ใช้ได้กับ complex geometry
- ทดสอบ code ได้ทุกส่วน

**Best Practice:**
- ถ้ามี Analytical → ใช้ก่อน (ง่ายกว่า)
- ถ้าไม่มี → ใช้ MMS

</details>

---

## 9. ⚡ Hands-on Challenges

### Challenge 1: GCI Study (⭐⭐⭐)

**วัตถุประสงค์:** ทำ mesh independence study ด้วย GCI

**Tasks:**
1. เลือก case (เช่น backward step)
2. สร้าง 3 meshes (coarse, medium, fine)
3. Run และ extract Cd
4. คำนวณ GCI ด้วย Python
5. รายงาน: Cd = X ± Y (GCI 95%)

---

### Challenge 2: Lid-Driven Cavity Validation (⭐⭐⭐)

**วัตถุประสงค์:** Validate กับ Ghia et al.

```bash
cp -r $FOAM_TUTORIALS/incompressible/icoFoam/cavity .
```

**Tasks:**
1. Run at Re = 1000
2. Extract u-velocity along vertical centerline
3. Plot vs Ghia data
4. Compute RMSE, R²

---

### Challenge 3: MMS Code Verification (⭐⭐⭐⭐⭐)

**วัตถุประสงค์:** Verify laplacianFoam ด้วย MMS

**Tasks:**
1. สร้าง manufactured solution: φ = sin(πx)sin(πy)
2. คำนวณ source term
3. Implement ใน fvOptions
4. Run on 3 meshes
5. Plot log(error) vs log(h)
6. Verify order ≈ 2

---

## 10. ❌ Common Mistakes

### Mistake 1: Skip Mesh Independence

```
❌ Run once และเชื่อผลลัพธ์
"Cd = 0.35" (mesh-dependent!)

✅ GCI study
"Cd = 0.35 ± 0.02" (quantified uncertainty)
```

---

### Mistake 2: Claim "Validated" Without Data

```
❌ "Model is validated"
แต่ไม่มี comparison กับ experiments

✅ "Model validated against Ghia et al. (1982)
   RMSE = 2.3%, R² = 0.97"
```

---

### Mistake 3: Wrong GCI Refinement Ratio

```
❌ Using non-uniform refinement
   Mesh1: 100 cells
   Mesh2: 150 cells  (r = 1.5)
   Mesh3: 300 cells  (r = 2.0)
   
   Different r → GCI formula breaks!

✅ Uniform refinement ratio
   Mesh1: 100 cells
   Mesh2: 200 cells  (r = 2)
   Mesh3: 400 cells  (r = 2)
```

---

### Mistake 4: Compare Wrong Quantities

```
❌ Experiment measures velocity at outlet
   CFD extracts velocity at different location

✅ Match exact locations, conditions
```

---

## 11. 🔗 เชื่อมโยงกับ Repository

| หัวข้อ | ไฟล์ใน Repository |
|--------|-------------------|
| **Testing Fundamentals** | `MODULE_08/01_TESTING_FUNDAMENTALS/` |
| **Verification** | `MODULE_08/02_VERIFICATION_FUNDAMENTALS/` |
| **MMS & GCI** | `MODULE_08/02_VERIFICATION_FUNDAMENTALS/02_Numerical_Methods.md` |
| **Test Framework** | `MODULE_08/03_TEST_FRAMEWORK_CODING/` |
| **Benchmarks** | `MODULE_08/04_VALIDATION_BENCHMARKS/` |
| **QA & Profiling** | `MODULE_08/05_QA_AUTOMATION_PROFILING/` |

---

## 12. สรุป: V&V Principles

### หลักการ 5 ข้อ

1. **Always Quantify Uncertainty**
   - ไม่มี error bar = ไม่มีความหมาย
   - ใช้ GCI สำหรับ mesh uncertainty

2. **Verify Before Validate**
   - ตรวจสอบ code ก่อน (MMS)
   - แล้วค่อย compare กับ experiments

3. **Use Standard Benchmarks**
   - ใช้ cases ที่คนอื่นใช้
   - Reproducible, comparable

4. **Document Everything**
   - Mesh, schemes, BCs, settings
   - ให้คนอื่น reproduce ได้

5. **Be Honest About Discrepancies**
   - ไม่มี model ที่ perfect
   - Report limitations clearly

---

*"CFD without V&V is just computational graphics"*
