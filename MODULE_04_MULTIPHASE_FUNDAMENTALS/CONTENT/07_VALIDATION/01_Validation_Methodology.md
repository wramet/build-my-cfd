# Validation Methodology

ระเบียบวิธีการตรวจสอบความถูกต้องสำหรับ Multiphase Flow

---

## Learning Objectives

เมื่ออ่านจบบทนี้ คุณจะสามารถ:
- อธิบายความแตกต่างระหว่าง code verification และ model validation
- ประยุกต์ใช้ validation workflow ที่เหมาะสมกับปัญหา multiphase flow
- วิเคราะห์ผลลัพธ์จาก verification และ validation tests
- ประเมินความเหมาะสมของ uncertainty quantification methods

---

## Prerequisites

ก่อนเริ่มบทนี้ คุณควรมีความรู้เกี่ยวกับ:
- **OpenFOAM Fundamentals:** การใช้งาน `blockMesh`, `snappyHexMesh`, และ solvers พื้นฐาน
- **Multiphase Flow:** ความเข้าใจเรื่อง VOF method หรือ Euler-Euler approach (ทบทวนจาก MODULE_04)
- **Numerical Methods:** แนวคิดเรื่อง discretization error, convergence, และ order of accuracy
- **Python Basics:** การใช้งาน Python สำหรับ data analysis (numpy, pandas, matplotlib)

> **หากยังไม่พร้อม:** แนะนำให้ทบทวน MODULE_04_MULTIPHASE_FUNDAMENTALS/CONTENT/02_VOF_METHOD และ 03_EULER_EULER_METHOD

---

## Validation Hierarchy

```
Code Verification → Solution Verification → Model Validation → Prediction
```

### Four Levels of Validation

| Level | Method | Purpose |
|-------|--------|---------|
| **Code Verification** | MMS, Unit tests | ตรวจสอบว่า code implement ถูกต้อง |
| **Solution Verification** | Grid study, GCI | ตรวจสอบ discretization error |
| **Model Validation** | Compare with exp | ตรวจสอบว่า physics ถูกต้อง |
| **Prediction** | Blind tests | ประเมิน predictive capability |

**Key Concept:** แต่ละระดับสร้างความมั่นใจ - code verification รับประกัน solver ถูกต้อง, solution verification รับประกัน numerical error ต่ำ, model validation รับประกัน physics ถูกต้อง

---

## 1. Code Verification Methodology

### 1.1 Method of Manufactured Solutions (MMS)

**WHAT (Definition):** เทคนิคที่สร้าง analytical solution ขึ้นมาเอง จากนั้นคำนวณ source term ที่ต้องเพิ่มเข้าไปในสมการ เพื่อตรวจสอบว่า solver ให้ผลลัพธ์ตรงกับ solution ที่กำหนด

**WHY (Importance):**
- ทดสอบความถูกต้องของ discretization scheme อย่างครอบคลุม
- วัด observed order of accuracy ได้จริง (ไม่ใช่ค่าท้ายทาย)
- ไม่ต้องการ analytical solution ที่ซับซ้อนจาก physics problems
- สามารถทดสอบทุกส่วนของ code รวมถึง boundary conditions

**HOW (Implementation):**

**Workflow:**
```
1. Define exact solution: α_exact(x,t) = sin(πx)cos(πt)
2. Compute source term: S_α = -∂α/∂t - ∇·(αU)
3. Add S_α to transport equation
4. Solve numerically
5. Compare: error = |α_computed - α_exact|
6. Verify order: error ~ h^p
```

**Target:** Observed order p ≈ theoretical order (1st or 2nd)

> **หมายเหตุ:** Implementation details และ code examples อยู่ใน `02_Benchmark_Cases.md` - MMS section

---

### 1.2 Grid Convergence Index (GCI)

**WHAT (Definition):** ดัชนีวัดความใกล้เคียงของ solution ที่มีต่อ asymptotic (mesh-independent) solution โดยใช้ค่าความแตกต่างระหว่าง meshes

**WHY (Importance):**
- ให้มาตรการที่เป็น quantitative สำหรับ mesh independence
- ช่วยกำหนดว่า mesh ละเอียดพอหรือไม่
- เป็นมาตรฐานที่ใช้กันอย่างแพร่หลายใน CFD community

**HOW (Application):**

**Quick Reference:**
1. Run 3+ meshes with refinement ratio r ≥ 1.3
2. Extract key quantity (e.g., terminal velocity, gas holdup)
3. Compute GCI between consecutive meshes
4. **Acceptance:** GCI < 5% → mesh-independent

> **หมายเหตุ:** Detailed GCI formulas, calculation procedures, and OpenFOAM implementation อยู่ใน `03_Grid_Convergence.md`

---

## 2. Solution Verification Methodology

### 2.1 Mesh Independence Study

**WHAT (Definition):** กระบวนการทดสอบว่า solution ไม่เปลี่ยนแปลงอย่างมีนัยสำคัญเมื่อละเอียด mesh เพิ่มขึ้น

**WHY (Importance):**
- รับประกันว่า results ไม่ใช่ artifact จาก mesh
- ลด numerical errors จาก discretization
- เป็นเงื่อนไขเบื้องต้นก่อนทำ model validation

**HOW (Implementation):**

**Systematic Approach:**
```
Coarse (N cells) → Medium (2N cells) → Fine (4N cells)
```

**Checklist:**
- [ ] Consistent refinement ratio (r = h2/h1 ≥ 1.3)
- [ ] Monitor key quantities: drag, velocity, phase fraction
- [ ] Compute GCI for each quantity
- [ ] Verify asymptotic range (GCI_fine/r^p ≈ GCI_medium)

**Decision Criteria:**
| Metric | Pass | Need Refinement |
|--------|------|-----------------|
| GCI | < 5% | ≥ 5% |
| Δf (fine-medium) | < 1% | ≥ 1% |
| p (observed) | ≈ theoretical | << theoretical |

---

### 2.2 Conservation Checks

**WHAT (Definition):** การตรวจสอบว่า solver conserve ค่าต่างๆ (mass, momentum) อย่างถูกต้อง

**WHY (Importance):**
- Conservation เป็นหลักมูลพื้นฐานของ CFD
- Violation บ่งชี้ว่ามีปัญหาใน solver หรือ setup
- เป็น quick check สำหรับความถูกต้องของ transient solutions

**HOW (Implementation):**

**Mass Balance Verification:**
```
Σ α_i = 1  (sum over all phases)
d/dt (∫ α dV) + ∮ αU·dA = 0
```

**OpenFOAM Implementation:**
```cpp
// system/controlDict
functions
{
    massBalance
    {
        type            volFieldValue;
        operation       sum;
        fields          (alpha.water alpha.air);
        // Check: sum = 1 ± tolerance
        writeFields     false;
    }
    
    alphaBounds
    {
        type            fieldMinMax;
        fields          (alpha.water);
        // Check: 0 ≤ α ≤ 1
        writeFields     false;
    }
}
```

**Acceptance Criteria:**
- Mass conservation error < 1e-6 (transient), < 1e-8 (steady)
- Phase fraction bounded: 0 ≤ α ≤ 1

---

## 3. Model Validation Methodology

### 3.1 Comparison with Experimental Data

**WHAT (Definition):** กระบวนการเปรียบเทียบ simulation results กับ experimental data เพื่อประเมินความถูกต้องของ physics models

**WHY (Importance):**
- ยืนยันว่า models แทน physics จริงได้อย่างแม่นยำ
- ระบุขอบเขตของความสามารถของแต่ละ model
- สร้างความมั่นใจในการใช้โมเดลทำนายปัญหาใหม่

**HOW (Implementation):**

**Validation Metrics:**

| Quantity | Definition | Target |
|----------|------------|--------|
| **RMSE** | $\sqrt{\frac{1}{N}\sum(y_{pred} - y_{exp})^2}$ | Minimize |
| **MAPE** | $\frac{100\%}{N}\sum|\frac{y_{pred} - y_{exp}}{y_{exp}}|$ | < 10-20% |
| **R²** | $1 - \frac{\sum(y_{exp} - y_{pred})^2}{\sum(y_{exp} - \bar{y})^2}$ | > 0.9 |

**Common Benchmark Systems:**
| System | Key Quantity | Validation Target |
|--------|--------------|-------------------|
| Single bubble | Terminal velocity $v_t$ | Theory: $v_t = \sqrt{4gd_b(\rho_l-\rho_g)/(3C_d\rho_l)}$ |
| Bubble column | Gas holdup profile | Experimental data |
| Pipe flow | Pressure drop | Darcy-Weisbach correlation |

**OpenFOAM Data Extraction:**
```cpp
// system/controlDict - probes at sensor locations
functions
{
    expProbes
    {
        type            probes;
        probeLocations  ((0.05 0 0) (0.1 0 0) (0.15 0 0));
        fields          (alpha.air U.air p);
        writeFields     false;
    }
    
    // Or use sets for line profiles
    centerlineProfile
    {
        type            sets;
        set             uniform;
        axis            xyz;
        start           (0 0 0);
        end             (0.5 0 0);
        fields          (alpha.air);
    }
}
```

**Python Analysis Example:**
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load experimental and simulation data
exp_data = pd.read_csv('experiment.csv')
sim_data = pd.read_csv('probeResults.csv')

# Calculate metrics
rmse = np.sqrt(np.mean((sim_data['alpha'] - exp_data['alpha'])**2))
mape = 100 * np.mean(np.abs((sim_data['alpha'] - exp_data['alpha']) / exp_data['alpha']))
r2 = 1 - np.sum((exp_data['alpha'] - sim_data['alpha'])**2) / np.sum((exp_data['alpha'] - exp_data['alpha'].mean())**2)

print(f"RMSE: {rmse:.4f}")
print(f"MAPE: {mape:.2f}%")
print(f"R²: {r2:.3f}")
```

---

### 3.2 Validation Decision Process

**WHAT (Definition):** ขั้นตอนการตัดสินใจว่า model ผ่าน validation หรือไม่ และถ้าไม่ผ่านควรแก้ไขอย่างไร

**WHY (Importance):**
- ให้ systematic approach ในการวินิจฉัยปัญหา
- ลดการเดาทิศทางการแก้ไข
- บันทึกการตัดสินใจสำหรับ future reference

**HOW (Implementation):**

**Step-by-Step:**
1. **Run simulation** with experimental conditions
2. **Extract data** at measurement locations
3. **Compute metrics** (RMSE, MAPE, R²)
4. **Assess agreement:**
   - MAPE < 10%: Excellent
   - MAPE 10-20%: Good
   - MAPE > 20%: Investigate model/parameters

**Discrepancy Investigation Flowchart:**
```
Large error → Check:
  1. Mesh independence (GCI < 5%?)
  2. Boundary conditions match experiment
  3. Turbulence model appropriateness
  4. Interfacial force models (drag, lift, wall lubrication)
  5. Time step sensitivity (CFL < 1)
  6. Parameter uncertainty
```

---

## 4. Uncertainty Quantification

### 4.1 Sources of Uncertainty

**WHAT (Definition):** ปัจจัยต่างๆ ที่ทำให้ simulation results มีความไม่แน่นอน

**WHY (Importance):**
- ไม่มี simulation ที่ perfect 100%
- การทราบ source ของ uncertainty ช่วยในการตีความผลลัพธ์
- เป็นพื้นฐานสำหรับการปรับปรุง model

**HOW (Identification):**

| Type | Examples | Mitigation |
|------|----------|------------|
| **Input** | Inlet velocity, initial conditions | Sensitivity analysis |
| **Parameter** | $C_d$, $C_l$, bubble size | Calibration, UQ |
| **Model form** | Choice of drag model | Model comparison |
| **Experimental** | Measurement error | Error propagation |

---

### 4.2 Sensitivity Analysis

**WHAT (Definition):** การวิเคราะห์ว่า input parameters แต่ละตัวส่งผลต่อ output มากน้อยเพียงใด

**WHY (Importance):**
- ระบุ parameter ไหนสำคัญที่สุด (focus calibration)
- ลด effort ในการปรับจูน parameters ที่ไม่มีผล
- เข้าใจ interactions ระหว่าง parameters

**HOW (Implementation - Sobol Method):**

**Sobol Indices:**
- **S1 (first-order):** Direct effect of parameter
- **ST (total):** Total effect (including interactions)

**Complete Python Example:**
```python
#!/usr/bin/env python3
"""
Sobol Sensitivity Analysis for Multiphase Flow
Requires: SALib (pip install SALib)
"""

from SALib.sample import saltelli
from SALib.analyze import sobol
import numpy as np
import subprocess
import os
import json

# Define problem
problem = {
    'num_vars': 3,
    'names': ['Cd', 'Cl', 'db'],
    'bounds': [
        [0.4, 0.5],    # Drag coefficient
        [0.01, 0.1],   # Lift coefficient
        [0.001, 0.005] # Bubble diameter [m]
    ]
}

# Generate samples (N=1000 → 1000*(2*3+2) = 8000 evaluations)
print("Generating samples...")
N = 1000
samples = saltelli.sample(problem, N, calc_second_order=True)

# Run OpenFOAM for each sample
results = []
for i, params in enumerate(samples):
    print(f"Running case {i+1}/{len(samples)}")
    
    # Update parameters in constant/phaseProperties
    updatePhaseProperties(params)
    
    # Run simulation
    subprocess.run(['multiphaseEulerFoam'], stdout=subprocess.DEVNULL)
    
    # Extract quantity of interest (e.g., gas holdup)
    qoi = extractQuantity('gasHoldup')
    results.append(qoi)

# Convert to numpy array
results = np.array(results)

# Perform Sobol analysis
print("Analyzing results...")
Si = sobol.analyze(problem, results, calc_second_order=True, print_to_console=True)

# Save results
with open('sobol_results.json', 'w') as f:
    json.dump({k: v.tolist() for k, v in Si.items()}, f)

print("\nFirst-order (S1):", Si['S1'])
print("Total-order (ST):", Si['ST'])

# Identify important parameters
important = np.where(Si['ST'] > 0.1)[0]
print(f"\nImportant parameters (ST > 0.1): {[problem['names'][i] for i in important]}")
```

**Update Function Example:**
```python
def updatePhaseProperties(params):
    """Update phaseProperties with new parameters"""
    import re
    
    with open('constant/phaseProperties', 'r') as f:
        content = f.read()
    
    # Update drag coefficient
    content = re.sub(
        r'dragCoeffs\s*\{[^}]*Cd\s+([\d.]+)',
        f'dragCoeffs {{\n        Cd {params[0]:.4f}',
        content
    )
    
    with open('constant/phaseProperties', 'w') as f:
        f.write(content)
```

**Interpretation:**
- High S1 → Parameter dominates uncertainty
- High ST-S1 → Strong interaction effects
- Focus calibration on high-ST parameters

---

### 4.3 Monte Carlo UQ

**WHAT (Definition):** การสุ่ม parameters จาก distributions แล้ว propagate ผ่าน simulation เพื่อหา output distribution

**WHY (Importance):**
- ให้ uncertainty bounds ที่ realistic
- สามารถ capture nonlinear effects
- เหมาะสำหรับ complex interactions

**HOW (Implementation):**

**Complete Bash Script:**
```bash
#!/bin/bash
# Monte Carlo Uncertainty Quantification
# Usage: ./runMonteCarlo.sh

NUM_SAMPLES=100
RESULTS_FILE="mc_results.txt"

# Clear previous results
> $RESULTS_FILE

echo "Starting Monte Carlo with $NUM_SAMPLES samples..."

for i in $(seq 1 $NUM_SAMPLES); do
    echo "Running sample $i/$NUM_SAMPLES"
    
    # Sample random parameters from uniform distributions
    Cd=$(python -c "import random; print(f'{random.uniform(0.4, 0.5):.4f}')")
    Cl=$(python -c "import random; print(f'{random.uniform(0.01, 0.1):.4f}')")
    db=$(python -c "import random; print(f'{random.uniform(0.001, 0.005):.6f}')")
    
    # Backup original files
    cp constant/phaseProperties constant/phaseProperties.bak
    
    # Update parameters (using sed or python script)
    ./update_parameters.py $Cd $Cl $db
    
    # Run OpenFOAM
    multiphaseEulerFoam > log.mc_$i 2>&1
    
    # Extract quantity of interest
    QOI=$(postProcess -func "volFieldValue(sum,alpha.air)" -latestTime | grep "sum(alpha.air)" | awk '{print $3}')
    
    # Store results
    echo "$i,$Cd,$Cl,$db,$QOI" >> $RESULTS_FILE
    
    # Restore original files
    mv constant/phaseProperties.bak constant/phaseProperties
    
    # Clean up
    cleanCase
done

echo "Monte Carlo complete. Analyzing results..."
python analyze_mc.py $RESULTS_FILE
```

**Analysis Script (analyze_mc.py):**
```python
#!/usr/bin/env python3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys

# Load results
data = pd.read_csv(sys.argv[1], names=['run', 'Cd', 'Cl', 'db', 'gasHoldup'])

# Calculate statistics
mean = data['gasHoldup'].mean()
std = data['gasHoldup'].std()
ci_95 = 1.96 * std

print(f"Gas Holdup: {mean:.4f} ± {std:.4f}")
print(f"95% Confidence Interval: [{mean-ci_95:.4f}, {mean+ci_95:.4f}]")

# Plot histogram
plt.figure(figsize=(10, 6))
plt.hist(data['gasHoldup'], bins=30, density=True, alpha=0.7, edgecolor='black')
plt.xlabel('Gas Holdup')
plt.ylabel('Probability Density')
plt.title(f'Monte Carlo Results (N={len(data)})')
plt.axvline(mean, color='r', linestyle='--', label=f'Mean: {mean:.4f}')
plt.axvline(mean-ci_95, color='g', linestyle=':', label='95% CI')
plt.axvline(mean+ci_95, color='g', linestyle=':')
plt.legend()
plt.savefig('mc_distribution.png')
print("Saved plot to mc_distribution.png")

# Check for normality
from scipy import stats
_, p_normal = stats.normaltest(data['gasHoldup'])
print(f"Normality test p-value: {p_normal:.4f}")
if p_normal < 0.05:
    print("Warning: Distribution is NOT normal (consider non-parametric analysis)")
```

**Output Analysis:**
- Mean ± std: Expected value and uncertainty
- PDF: Distribution shape (normal, skewed?)
- Confidence intervals: 95% CI = mean ± 2σ

---

## Complete Validation Workflow

### Phase 1: Preparation
```
1. Define validation objectives
   - What quantities to predict?
   - What accuracy level required?

2. Select experimental benchmark
   - High-quality data available?
   - Geometry matches your application?

3. Identify key quantities of interest
   - Gas holdup, velocity profiles, pressure drop
```

### Phase 2: Code Verification
```bash
# Run MMS test cases
./runMMS.sh

# Check order of accuracy
python checkMMS.py > mms_results.txt

# Target: p ≈ theoretical order (1 or 2)
```

### Phase 3: Solution Verification
```bash
# Mesh independence study
for mesh in coarse medium fine; do
    cp system/blockMeshDict_$mesh system/blockMeshDict
    blockMesh
    multiphaseEulerFoam > log.$mesh
done

# Calculate GCI
python calculateGCI.py

# Target: GCI < 5%
```

### Phase 4: Model Validation
```bash
# Run with experimental conditions
cp experimentalSetup/* .
multiphaseEulerFoam

# Extract at measurement points
postProcess -func probes -latestTime

# Compare with experiment
python compareWithExperiment.py

# Target: MAPE < 20%
```

### Phase 5: Uncertainty Quantification
```bash
# Sensitivity analysis (if validation passes with ~10-20% error)
python sobolAnalysis.py

# Monte Carlo (for uncertainty quantification)
./runMonteCarlo.sh
```

---

## Quick Checklist

| Step | Check | Target |
|------|-------|--------|
| ✅ **MMS** | Order of accuracy | p ≈ expected (1 or 2) |
| ✅ **GCI** | Mesh independence | GCI < 5% |
| ✅ **Conservation** | Mass balance | Error < 1e-6 |
| ✅ **Bounds** | Phase fraction | 0 ≤ α ≤ 1 |
| ✅ **RMSE/MAPE** | Compare exp | MAPE < 10-20% |
| ✅ **Sensitivity** | Sobol indices | Identify key params |
| ✅ **Repeatability** | Run twice | Same results |

---

## Key Takeaways

- **Validation Hierarchy:** Code → Solution → Model → Prediction - แต่ละขั้นสร้างความมั่นใจ
  - Code verification: รับประกัน solver ถูกต้อง
  - Solution verification: รับประกัน numerical error ต่ำ
  - Model validation: รับประกัน physics ถูกต้อง
  - Prediction: รับประกันเชื่อถือได้สำหรับใช้งานจริง

- **MMS สำหรับ Code Verification:** ทดสอบว่า solver แก้สมการถูกต้อง (p ≈ theoretical)
  - สร้าง analytical solution ขึ้นมาเอง
  - คำนวณ source term
  - ตรวจสอบว่า solver ให้ผลตรงกัน

- **GCI สำหรับ Mesh Independence:** GCI < 5% → solution ไม่ sensitive กับ mesh
  - ใช้ 3+ meshes
  - Refinement ratio r ≥ 1.3
  - ดูรายละเอียดสูตรใน `03_Grid_Convergence.md`

- **Model Validation:** เปรียบเทียบกับ experiment ใช้ RMSE/MAPE/R² วัดความคลาดเคลื่อน
  - RMSE: Root mean square error
  - MAPE: Mean absolute percentage error (target < 10-20%)
  - R²: Coefficient of determination (target > 0.9)

- **Uncertainty Quantification:** ใช้ sensitivity analysis หา parameter สำคัญ - ลด effort ในการปรับจูน
  - Sobol indices: S1 (first-order), ST (total-order)
  - Monte Carlo: propagate parameter uncertainty → output distribution
  - Focus calibration บน parameters ที่มี ST สูง

---

## Concept Check

<details>
<summary><b>1. Code verification กับ model validation ต่างกันอย่างไร?</b></summary>

**Code Verification:**
- ตรวจสอบว่า code แก้สมการคณิตศาสตร์ถูกต้อง
- เปรียบเทียบกับ analytical solution หรือ MMS
- วัด order of accuracy (p ≈ theoretical)

**Model Validation:**
- ตรวจสอบว่าสมการคณิตศาสตร์แทน physics จริงได้ดี
- เปรียบเทียบกับ experiment
- วัด error metrics (RMSE, MAPE, R²)

**ตัวอย่าง:** MMS ยืนยันว่า solver คำนวณ transport equation ถูกต้อง (code verification), แต่ต้องเปรียบเทียบกับ data จาก bubble column experiment จึงจะรู้ว่า drag model ใช้ได้จริง (model validation)
</details>

<details>
<summary><b>2. GCI ใช้ทำอะไร และเกณฑ์คืออะไร?</b></summary>

**Purpose:** วัดว่า solution ใกล้ mesh-independent แค่ไหน (คือ error จาก discretization)

**เกณฑ์:**
- GCI < 5%: Mesh-independent ✓
- GCI 5-10%: อาจต้อง refine เพิ่ม
- GCI > 10%: Mesh ไม่ละเอียดพอ

**วิธีใช้:**
1. Run 3+ meshes (r ≥ 1.3)
2. Compute GCI ระหว่าง meshes
3. ถ้า GCI_fine < 5% → พอใช้

**หมายเหตุ:** สูตรคำนวณ GCI อยู่ใน `03_Grid_Convergence.md`
</details>

<details>
<summary><b>3. Sobol indices บอกอะไร และใช้ประโยชน์ได้อย่างไร?</b></summary>

**Meaning:**
- **S1 (first-order):** Effect โดยตรงของ parameter ต่อ output (ไม่รวม interactions)
- **ST (total-order):** Effect รวมทุกอย่าง (รวม interactions กับ parameters อื่น)

**Usage:**
- ถ้า S1(Cd) = 0.7 → drag coefficient อธิบาย 70% ของ output variance โดยตรง
- ถ้า ST(Cd) = 0.8 → Cd มีผลรวม 80% (รวม interactions)
- ST-S1 = 0.1 → Interactions กับ params อื่นมีผล 10%

**Application:**
- Prioritize calibration กับ parameters ที่มี ST สูง
- ลด effort สำหรับ parameters ที่ ST ≈ 0 (ไม่มีผล)
- ถ้า ST-S1 สูง → parameters มี interaction กันมาก
</details>

<details>
<summary><b>4. เมื่อ validation ให้ MAPE = 25% ควณทำอย่างไร?</b></summary>

**Investigation checklist:**
1. ✓ Check GCI < 5% (mesh-independent หรือยัง)
2. ✓ Verify boundary conditions match experiment
3. ✓ Check turbulence model (k-ε vs LES)
4. ✓ Review interfacial force models (drag, lift, wall lubrication)
5. ✓ Verify time step (CFL < 1)
6. ✓ Consider parameter uncertainty (run UQ)

**หลังการแก้ไข:**
- ถ้า MAPE ยัง > 20% → อาจต้อง reconsider model assumptions
- อาจเปลี่ยน drag model หรือเพิ่ม sub-models (bubble-induced turbulence)
- ถ้าไม่แน่ใจ → รัน sensitivity analysis เพื่อดูว่า params ไหนสำคัญ
</details>

<details>
<summary><b>5. Monte Carlo และ Sobol analysis แตกต่างกันอย่างไร?</b></summary>

**Sobol Analysis:**
- **Purpose:** หาว่า parameter ไหนสำคัญที่สุด
- **Method:** Variance decomposition
- **Output:** Sensitivity indices (S1, ST)
- **Use:** Focus calibration effort

**Monte Carlo UQ:**
- **Purpose:** หา output distribution เมื่อ parameters ไม่แน่นอน
- **Method:** Random sampling + propagation
- **Output:** Mean ± std, PDF, confidence intervals
- **Use:** รายงานความไม่แน่นอนใน results

**Workflow ทั่วไป:**
1. Run Sobol → รู้ว่า params ไหนสำคัญ
2. Calibrate params สำคัญ
3. Run Monte Carlo → หา uncertainty bounds
</details>

---

## Related Documents

- **Previous:** [00_Overview.md](00_Overview.md) - Validation concepts introduction
- **Next:** [02_Benchmark_Cases.md](02_Benchmark_Cases.md) - MMS implementation และ experimental benchmarks
- **Reference:** [03_Grid_Convergence.md](03_Grid_Convergence.md) - Detailed GCI calculation procedures
- **Application:** [04_Validation_Examples.md](04_Validation_Examples.md) - Real-world case studies