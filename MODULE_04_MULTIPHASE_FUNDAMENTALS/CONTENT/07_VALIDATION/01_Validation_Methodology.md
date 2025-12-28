# Validation Methodology

ระเบียบวิธีการตรวจสอบความถูกต้องสำหรับ Multiphase Flow

---

## Validation Hierarchy

```
Code Verification → Solution Verification → Model Validation → Prediction
```

| Level | Method | Purpose |
|-------|--------|---------|
| **Code Verification** | MMS, Unit tests | ตรวจสอบว่า code implement ถูกต้อง |
| **Solution Verification** | Grid study, GCI | ตรวจสอบ discretization error |
| **Model Validation** | Compare with exp | ตรวจสอบว่า physics ถูกต้อง |
| **Prediction** | Blind tests | ประเมิน predictive capability |

---

## 1. Code Verification

### Method of Manufactured Solutions (MMS)

สร้าง analytical solution → คำนวณ source term → ตรวจสอบว่า solver ให้ผลตรงกัน

```cpp
// Define exact solution
volScalarField alphaExact = 0.5*(1 + tanh(...));

// Calculate manufactured source
Salpha = -(fvc::ddt(alphaExact) + fvc::div(alphaExact*U));

// Add source to equation and solve
// Error = |alpha_computed - alphaExact|
```

### Grid Convergence Index (GCI)

$$\text{GCI} = 1.25 \cdot \frac{|f_2 - f_1|}{r^p - 1}$$

| Symbol | Meaning |
|--------|---------|
| $f_1, f_2$ | Solution on fine/coarse mesh |
| $r$ | Refinement ratio (e.g., 2) |
| $p$ | Observed order of accuracy |

```cpp
scalar p = log(epsilon32/epsilon21) / log(r);
scalar GCI = 1.25 * fabs(f2 - f1) / (pow(r, p) - 1);
```

**Target:** GCI < 5% for mesh-independent solution

---

## 2. Solution Verification

### Mesh Independence Study

```cpp
// system/blockMeshDict
// Mesh 1 (coarse): hex (0 1 2 3 4 5 6 7) (20 20 20)
// Mesh 2 (medium): hex (0 1 2 3 4 5 6 7) (40 40 40)
// Mesh 3 (fine):   hex (0 1 2 3 4 5 6 7) (80 80 80)
```

### Conservation Checks

```cpp
// system/controlDict
functions
{
    massBalance
    {
        type            volFieldValue;
        operation       sum;
        fields          (alpha.water);
    }
    
    alphaCheck
    {
        type            fieldMinMax;
        fields          (alpha.water alpha.air);
        // Check: 0 ≤ α ≤ 1
    }
}
```

---

## 3. Model Validation

### Compare with Experiments

| System | Quantity | Correlation/Data |
|--------|----------|------------------|
| Single bubble | Terminal velocity | $v_t = \sqrt{4gd_b(\rho_l-\rho_g)/(3C_d\rho_l)}$ |
| Bubble column | Gas holdup | Experimental profiles |
| Pipe flow | Pressure drop | Darcy-Weisbach |

### OpenFOAM Setup

```cpp
// system/controlDict - probes at sensor locations
functions
{
    expProbes
    {
        type            probes;
        probeLocations  ((0.05 0 0) (0.1 0 0) (0.15 0 0));
        fields          (alpha.air U.air p);
    }
}
```

### Error Metrics

$$\text{RMSE} = \sqrt{\frac{1}{N}\sum(y_{pred} - y_{exp})^2}$$

$$\text{MAPE} = \frac{100\%}{N}\sum\left|\frac{y_{pred} - y_{exp}}{y_{exp}}\right|$$

$$R^2 = 1 - \frac{\sum(y_{exp} - y_{pred})^2}{\sum(y_{exp} - \bar{y})^2}$$

---

## 4. Uncertainty Quantification

### Sources of Uncertainty

| Type | Examples |
|------|----------|
| Input | Inlet velocity, initial conditions |
| Parameter | Drag coefficient $C_d$, lift $C_l$ |
| Model form | Choice of drag model |
| Experimental | Measurement error |

### Sensitivity Analysis (Sobol Indices)

```python
# Python with SALib
from SALib.sample import saltelli
from SALib.analyze import sobol

problem = {
    'names': ['Cd', 'Cl', 'db'],
    'bounds': [[0.4, 0.5], [0.01, 0.1], [0.001, 0.005]]
}

samples = saltelli.sample(problem, 1000)
# Run OpenFOAM for each sample
Si = sobol.analyze(problem, results)
print("S1:", Si['S1'])  # First-order indices
```

### Monte Carlo

```bash
#!/bin/bash
for i in {1..100}; do
    # Sample random parameters
    Cd=$(python -c "import random; print(random.uniform(0.4, 0.5))")
    
    # Update phaseProperties
    sed -i "s/CdValue/$Cd/" constant/phaseProperties
    
    # Run
    multiphaseEulerFoam > log.$i
done

# Analyze statistics
python analyze_uncertainty.py
```

---

## Validation Workflow

```bash
# 1. Code verification (MMS)
./runMMS.sh
checkMMS > mms_results.txt

# 2. Mesh study
for mesh in coarse medium fine; do
    blockMesh -dict meshes/$mesh
    multiphaseEulerFoam
done
python calculateGCI.py

# 3. Compare with experiment
postProcess -func probes -latestTime
python compareWithExperiment.py

# 4. Uncertainty quantification
python sobolAnalysis.py
```

---

## Quick Checklist

| Step | Check | Target |
|------|-------|--------|
| ✅ MMS error | Order of accuracy | p ≈ expected (1 or 2) |
| ✅ GCI | Mesh independence | GCI < 5% |
| ✅ Conservation | Mass balance | Error < 1e-6 |
| ✅ α bounds | 0 ≤ α ≤ 1 | No violations |
| ✅ RMSE/MAPE | Compare exp | MAPE < 10-20% |
| ✅ Sensitivity | Sobol indices | Identify key params |

---

## Concept Check

<details>
<summary><b>1. Code verification กับ model validation ต่างกันอย่างไร?</b></summary>

- **Code verification**: ตรวจสอบว่า code แก้สมการคณิตศาสตร์ถูกต้อง (เปรียบเทียบกับ analytical solution)
- **Model validation**: ตรวจสอบว่าสมการคณิตศาสตร์แทน physics จริงได้ดี (เปรียบเทียบกับ experiment)
</details>

<details>
<summary><b>2. GCI ใช้ทำอะไร?</b></summary>

วัดว่า solution ใกล้ mesh-independent แค่ไหน — ถ้า GCI < 5% แสดงว่า mesh ละเอียดพอแล้ว
</details>

<details>
<summary><b>3. Sobol indices บอกอะไร?</b></summary>

บอกว่า parameter ไหน (Cd, Cl, db) ส่งผลต่อ output มากที่สุด — ช่วย prioritize การปรับจูน model
</details>

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [00_Overview.md](00_Overview.md)
- **บทถัดไป:** [02_Benchmark_Cases.md](02_Benchmark_Cases.md)