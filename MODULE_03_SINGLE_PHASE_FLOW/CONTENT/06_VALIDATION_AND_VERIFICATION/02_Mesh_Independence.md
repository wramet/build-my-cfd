# Mesh Independence Study

การศึกษาความเป็นอิสระของ Mesh ตามมาตรฐาน ASME V&V 20

---

## Learning Objectives | วัตถุประสงค์การเรียนรู้

**หลังจบบทนี้ คุณจะสามารถ:**
- อธิบายแนวคิด mesh independence และความสำคัญต่อความน่าเชื่อถือของผลลัพธ์ CFD
- คำนวณ Grid Convergence Index (GCI) ด้วยวิธีสาม grid ตามมาตรฐาน ASME V&V 20
- ใช้ Richardson extrapolation เพื่อประมาณค่าที่แม่นยำ
- ตรวจสอบ asymptotic range เพื่อยืนยันความถูกต้องของการวิเคราะห์
- ประยุกต์ใช้ OpenFOAM tools สำหรับสร้างและเปรียบเทียบหลายระดับ mesh
- กำหนดขนาดเซลล์แรกให้เหมาะสมกับ1$y^+1target ใน turbulence modeling

**After completing this section, you will be able to:**
- Explain mesh independence concept and its importance for CFD result credibility
- Calculate Grid Convergence Index (GCI) using three-grid method per ASME V&V 20 standard
- Apply Richardson extrapolation to estimate accurate values
- Verify asymptotic range to confirm analysis validity
- Utilize OpenFOAM tools for generating and comparing multiple mesh levels
- Determine first cell height for target1$y^+1in turbulence modeling

---

## What is Mesh Independence? | Mesh Independence คืออะไร?

**Mesh Independence** หมายถึงสถานะที่ผลลัพธ์การจำลองไม่เปลี่ยนแปลงอย่างมีนัยสำคัญเมื่อมีการ refine mesh ต่อไป

**Mesh Independence** refers to the state where simulation results do not change significantly when further refining the mesh

### แนวคิดพื้นฐาน | Key Concepts

- **Discretization Error**: ความผิดพลาดจากการแบ่งโดเมนต่อเนื่องเป็นเซลล์จำกัด
- **Grid Convergence**: สถานะที่ผลลัพธ์ลู่เข้าสู่ค่าคงที่เมื่อลดขนาดเซลล์
- **Asymptotic Range**: ช่วงที่ error ลดลงตามสมการ1$O(h^p)1อย่างสม่ำเสมอ

### สัญลักษณ์หลัก | Main Symbols

| Symbol | หมายถึง | Meaning |
|--------|---------|--------|
|1$h1| ขนาด characteristic cell | Characteristic cell size |
|1$r1| Refinement ratio ($h_{coarse}/h_{fine}$) | Refinement ratio |
|1$p1| Observed order of accuracy | อันดับของความแม่นยำที่สังเกตได้ |
|1$f1| Quantity of interest | ปริมาณที่สนใจ |
|1$GCI1| Grid Convergence Index | ดัชนีการลู่เข้าของกริด |

---

## Why is it Critical? | ทำไมสำคัญ?

### ผลที่ตามมาของการไม่ตรวจสอบ Mesh Independence | Consequences of NOT Checking Mesh Independence

**หากไม่ตรวจสอบ mesh independence:**

1. **ผลลัพธ์ที่ไม่น่าเชื่อถือ**: ค่าที่รายงานอาจมี discretization error สูงกว่าที่คิด
2. **การตัดสินใจที่ผิดพลาด**: การออกแบบที่อ้างอิงผลลัพธ์ที่ไม่ลู่เข้าอาจล้มเหลว
3. **การประหยัดทรัพยากรฟุ้ยเปล่า**: Mesh ละเอียดเกินไปโดยไม่จำเป็น
4. **การปฏิเสธจากวารสาร**: บทความวิจัยที่ไม่มี mesh independence study มักถูกปฏิเสธ
5. **ความผิดพลาดที่ซ่อนอยู่**: บางครั้ง coarse mesh ให้ค่าดูเหมือน "ดี" เพราะ error cancel-out

**If mesh independence is NOT checked:**

1. **Unreliable Results**: Reported values may have higher discretization error than expected
2. **Wrong Decisions**: Designs based on unconverged results may fail
3. **Wasted Resources**: Excessively refined meshes without necessity
4. **Journal Rejection**: Papers without mesh independence study are often rejected
5. **Hidden Errors**: Sometimes coarse meshes give "good" values due to error cancelation

### มาตรฐานอุตสาหกรรม | Industry Standards

- **ASME V&V 20**: มาตรฐานสำหรับ verification & validation ใน CFD
- **ERCOFTAC**: Guidelines สำหรับ best practices
- **AIAA**: จำเป็นต้องมี GCI analysis สำหรับงานวิจัย

---

## How to Perform Mesh Independence Study | วิธีดำเนินการ

### ขั้นตอนโดยรวม | Overall Procedure

```
Create Meshes → Run Simulations → Extract QoI → Calculate GCI → Check Convergence → Report Results
```

---

## 1. Three-Grid Method | วิธีสาม Grid

ตามมาตรฐาน ASME V&V 20 ต้องการ Mesh อย่างน้อย 3 ระดับเพื่อคำนวณ observed order of accuracy ($p$)

According to ASME V&V 20 standard, at least 3 mesh levels are required to calculate observed order of accuracy ($p$)

### ข้อกำหนดเบื้องต้น | Requirements

| Level | เซลล์ | Cell Size | การใช้งาน | Use |
|-------|--------|-----------|-------------|-----|
| Coarse ($h_1$) | น้อยสุด | Largest ($h_1$) | ค่าเริ่มต้น | Initial estimate |
| Medium ($h_2$) | ปานกลาง | Medium ($h_2$) | ตรวจสอบ convergence | Convergence check |
| Fine ($h_3$) | มากสุด | Smallest ($h_3$) | ความแม่นยำสูงสุด | Best accuracy |

### Refinement Ratio

$$r = \frac{h_{coarse}}{h_{fine}} = \frac{h_1}{h_2} = \frac{h_2}{h_3}$$

**Requirement:**1$r > 1.31(ideal:1$r = \sqrt{2} \approx 1.414$)

**หมายเหตุ**:1$h1สามารถคำนวณจาก1$h = (1/N)^{1/d}1เมื่อ1$N1= จำนวนเซลล์,1$d1= มิติ (2 หรือ 3)

---

## 2. GCI Calculation | การคำนวณ GCI

### Step 1: Observed Order of Accuracy | อันดับของความแม่นยำที่สังเกตได้

$$p = \frac{\ln\left|\frac{f_3 - f_2}{f_2 - f_1}\right|}{\ln(r)}$$

เมื่อ1$f_1, f_2, f_31คือ quantity of interest บน coarse, medium, fine mesh

Where1$f_1, f_2, f_31are the quantity of interest on coarse, medium, fine meshes

### Step 2: Richardson Extrapolation | การประมาณค่า Richardson

$$f_{exact} \approx f_1 + \frac{f_1 - f_2}{r^p - 1}$$

สูตรนี้ให้ค่าประมาณที่แม่นยำกว่า fine mesh ($O(h^{p+1})$)

This formula provides an estimate more accurate than the fine mesh ($O(h^{p+1})$)

### Step 3: Grid Convergence Index | ดัชนีการลู่เข้าของกริด

$$GCI_{fine} = F_s \frac{|f_1 - f_2|/|f_1|}{r^p - 1} \times 100\%$$

เมื่อ1$F_s1คือ safety factor:
-1$F_s = 1.251สำหรับ 3 grids (recommended)
-1$F_s = 3.01สำหรับ 2 grids (conservative)

Where1$F_s1is the safety factor:
-1$F_s = 1.251for 3 grids (recommended)
-1$F_s = 3.01for 2 grids (conservative)

### Step 4: Asymptotic Range Check | การตรวจสอบ Asymptotic Range

ตรวจสอบว่าอยู่ใน asymptotic range:

Verify that results are in asymptotic range:

$$0.9 < \frac{GCI_{coarse}}{r^p \cdot GCI_{fine}} < 1.1$$

ถ้าไม่อยู่ในช่วงนี้ แสดงว่า mesh ยังไม่ละเอียดพอ หรือ solution ไม่ smooth

If not within this range, mesh is not refined enough or solution is not smooth

### ตัวอย่างการคำนวณ | Calculation Example

**Scenario**: Drag coefficient ของทรงกลม ($D = 11m,1$U_\infty = 101m/s)

| Mesh | Cells |1$h1(m) |1$C_d1|
|------|-------|---------|-------|
| Coarse | 50,000 | 0.020 | 1.245 |
| Medium | 100,000 | 0.015 | 1.198 |
| Fine | 200,000 | 0.010 | 1.187 |

**Step 1**:1$r = 0.020/0.015 = 1.333$

**Step 2**: Order of accuracy
$$p = \frac{\ln|1.187-1.198|/|1.198-1.245|}{\ln(1.333)} = \frac{\ln(0.234)}{\ln(1.333)} = 2.01$$

**Step 3**: Richardson extrapolation
$$C_{d,exact} \approx 1.245 + \frac{1.245-1.198}{1.333^{2.01}-1} = 1.181$$

**Step 4**: GCI
$$GCI_{fine} = 1.25 \times \frac{|1.245-1.198|/|1.245|}{1.333^{2.01}-1} \times 100\% = 2.98\%$$

**Step 5**: Asymptotic check (calculate1$GCI_{coarse}1similarly):
$$Ratio = 0.96 \checkmark$$

**ผลสรุป**:1$C_d = 1.187 \pm 2.98\%1(mesh uncertainty)

---

## 3. OpenFOAM Workflow | ขั้นตอนใน OpenFOAM

### Step 1: Create Multiple Meshes | สร้างหลายระดับ Mesh

#### วิธีที่ 1: แก้ไข blockMeshDict โดยตรง

```bash
# สร้าง directory สำหรับแต่ละระดับ
mkdir -p coarse medium fine

# Coarse mesh
cat > coarse/system/blockMeshDict << EOF
blocks
(
    hex (0 1 2 3 4 5 6 7) (50 50 1) simpleGrading (1 1 1)
);
EOF

# Medium mesh
cat > medium/system/blockMeshDict << EOF
blocks
(
    hex (0 1 2 3 4 5 6 7) (100 100 1) simpleGrading (1 1 1)
);
EOF

# Fine mesh
cat > fine/system/blockMeshDict << EOF
blocks
(
    hex (0 1 2 3 4 5 6 7) (200 200 1) simpleGrading (1 1 1)
);
EOF

# Generate meshes
blockMesh -case coarse
blockMesh -case medium
blockMesh -case fine
```

#### วิธีที่ 2: ใช้ Parameterization (แนะนำ)

```python
# scripts/generate_meshes.py
import os
import json

mesh_configs = {
    'coarse': {'cells': (50, 50, 1)},
    'medium': {'cells': (100, 100, 1)},
    'fine':   {'cells': (200, 200, 1)}
}

base_dir = 'system'
template = """
blocks
(
    hex (0 1 2 3 4 5 6 7) ({0} {1} {2}) simpleGrading (1 1 1)
);
"""

for level, config in mesh_configs.items():
    os.makedirs(f'{level}/system', exist_ok=True)
    
    # Read base blockMeshDict
    with open(f'{base_dir}/blockMeshDict', 'r') as f:
        content = f.read()
    
    # Replace cells line
    cells_str = f"cells {config['cells']}"
    # ... (modify content)
    
    with open(f'{level}/system/blockMeshDict', 'w') as f:
        f.write(content)
```

### Step 2: Run Simulations | รันการจำลอง

```bash
# Run all cases (สามารถใช้ script ช่วยได้)
for level in coarse medium fine; do
    echo "Running1$level..."
    cd1$level
    simpleFoam > log.$level 2>&1
    cd ..
done

# หรือใช้ parallel
for level in coarse medium fine; do
    cd1$level
    decomposePar
    mpirun -np 4 simpleFoam -parallel
    reconstructPar
    cd ..
done
```

### Step 3: Extract Quantity of Interest | ดึงค่าที่สนใจ

#### สร้าง Function Object สำหรับวัด Cd

```cpp
// system/controlDict (เพิ่มในทุก case)
application     simpleFoam;

startFrom       startTime;

startTime       0;

stopAt          endTime;

endTime         1000;

deltaT          1;

functions
{
    // Drag coefficient
    forceCoeffsObj
    {
        type            forceCoeffs;
        libs            ("libforces.so");
        
        // Write frequency
        writeControl    timeStep;
        writeInterval   10;
        
        // Patches to integrate
        patches         ("obj");
        
        // Density for incompressible
        rho             rhoInf;
        rhoInf          1.225;
        
        // Reference velocity
        CofR            (0 0 0);
        magUInf         10.0;
        
        // Reference dimensions
        lRef            1.0;    // Length
        Aref            1.0;    // Area
        
        // Lift direction
        liftDir         (0 1 0);
        
        // Drag direction
        dragDir         (1 0 0);
        
        // Pitch axis
        pitchAxis       (0 0 1);
    }
    
    // Monitor convergence
    residuals
    {
        type            residuals;
        libs            ("libutilityFunctionObjects.so");
        
        fields          (p U);
        
        writeControl    none;
        writeInterval   0;
    }
}
```

#### ดึงค่าจาก log files

```bash
# ดู Cd ที่ converge
grep "Cd = " coarse/postProcessing/forceCoeffsObj/0/coefficient.dat | tail -1

# หรือ extract ค่าสุดท้าย
for level in coarse medium fine; do
    echo -n "$level: "
    tail -11$level/postProcessing/forceCoeffsObj/0/coefficient.dat | awk '{print1$2}'
done
```

### Step 4: Analyze with Python | วิเคราะห์ด้วย Python

```python
#!/usr/bin/env python3
"""
GCI Calculator for OpenFOAM Results
ตามมาตรฐาน ASME V&V 20
"""

import numpy as np
import pandas as pd
from pathlib import Path

def calculate_gci(f, h, Fs=1.25):
    """
    Calculate Grid Convergence Index using three-grid method
    
    Parameters:
    -----------
    f : array-like
        Quantity of interest [coarse, medium, fine]
    h : array-like
        Characteristic cell sizes [coarse, medium, fine]
    Fs : float
        Safety factor (1.25 for 3 grids, 3.0 for 2 grids)
    
    Returns:
    --------
    dict : GCI analysis results
    """
    f1, f2, f3 = f
    h1, h2, h3 = h
    
    # Refinement ratio (assume constant)
    r = h1 / h2
    r_check = h2 / h3
    
    if abs(r - r_check) > 0.1:
        print(f"Warning: r varies ({r:.3f} vs {r_check:.3f})")
    
    # Observed order of accuracy
    epsilon_21 = f2 - f1
    epsilon_32 = f3 - f2
    
    if abs(epsilon_21) < 1e-12 or abs(epsilon_32) < 1e-12:
        raise ValueError("Solutions too similar - cannot calculate p")
    
    p = np.log(abs(epsilon_32 / epsilon_21)) / np.log(r)
    
    # Richardson extrapolation
    f_exact = f1 + (f1 - f2) / (r**p - 1)
    
    # GCI for fine mesh
    GCI_fine = Fs * abs(epsilon_21) / abs(f1) / (r**p - 1) * 100
    
    # GCI for coarse mesh (for asymptotic check)
    GCI_coarse = Fs * abs(epsilon_32) / abs(f2) / (r**p - 1) * 100
    
    # Asymptotic range check
    asymptotic_ratio = GCI_coarse / (r**p * GCI_fine)
    
    return {
        'p': p,
        'f_exact': f_exact,
        'GCI_fine': GCI_fine,
        'GCI_coarse': GCI_coarse,
        'asymptotic_ratio': asymptotic_ratio,
        'in_asymptotic_range': 0.9 < asymptotic_ratio < 1.1,
        'r': r
    }

def extract_from_openfoam(case_dirs):
    """
    Extract quantity of interest from OpenFOAM cases
    
    Parameters:
    -----------
    case_dirs : list
        List of case directories [coarse, medium, fine]
    
    Returns:
    --------
    dict : Extracted values
    """
    results = {}
    
    for case in case_dirs:
        # Assuming forceCoeffs output
        coeff_file = Path(case) / "postProcessing/forceCoeffsObj/0/coefficient.dat"
        
        if coeff_file.exists():
            data = np.loadtxt(coeff_file)
            # Cd is usually column 1 (check your file!)
            Cd = data[-1, 1]  # Last timestep
            results[case] = Cd
        else:
            print(f"Warning: {coeff_file} not found")
    
    return results

def print_gci_report(result):
    """Print formatted GCI report"""
    print("\n" + "="*60)
    print("GRID CONVERGENCE INDEX (GCI) ANALYSIS")
    print("="*60)
    print(f"Refinement ratio (r):          {result['r']:.4f}")
    print(f"Order of accuracy (p):         {result['p']:.4f}")
    print(f"Richardson extrapolated value: {result['f_exact']:.6f}")
    print(f"\nGCI (fine mesh):               {result['GCI_fine']:.4f}%")
    print(f"GCI (coarse mesh):             {result['GCI_coarse']:.4f}%")
    print(f"Asymptotic ratio:              {result['asymptotic_ratio']:.4f}")
    print(f"In asymptotic range:           {result['in_asymptotic_range']}")
    
    if result['in_asymptotic_range']:
        print("\n✓ Mesh is in asymptotic range - GCI is valid")
    else:
        print("\n✗ WARNING: Not in asymptotic range - refine meshes further")
    print("="*60 + "\n")

# ============ Example Usage ============
if __name__ == "__main__":
    
    # Method 1: Manual input
    print("Example 1: Manual Cd values")
    f = [1.245, 1.198, 1.187]  # Cd on coarse, medium, fine
    h = [0.020, 0.015, 0.010]  # Characteristic cell sizes
    
    result = calculate_gci(f, h)
    print_gci_report(result)
    
    # Method 2: Extract from OpenFOAM cases
    # print("\nExample 2: Extract from OpenFOAM")
    # cases = ['coarse', 'medium', 'fine']
    # results = extract_from_openfoam(cases)
    # f_list = [results[c] for c in cases]
    # 
    # # Estimate h from cell count
    # cell_counts = [50000, 100000, 200000]
    # h_list = [(1/n)**(1/3) for n in cell_counts]
    # 
    # result = calculate_gci(f_list, h_list)
    # print_gci_report(result)
```

**ใช้งาน:**

```bash
python3 scripts/gci_calculator.py
```

**Output:**

```
============================================================
GRID CONVERGENCE INDEX (GCI) ANALYSIS
============================================================
Refinement ratio (r):          1.3333
Order of accuracy (p):         2.0100
Richardson extrapolated value: 1.180780

GCI (fine mesh):               2.9834%
GCI (coarse mesh):             4.3891%
Asymptotic ratio:              0.9602
In asymptotic range:           True

✓ Mesh is in asymptotic range - GCI is valid
============================================================
```

---

## 4.1$y^+1Requirements | ข้อกำหนด1$y^+$

สำหรับ turbulent flow simulations ความละเอียดของ mesh ใกล้ผนัง ($y^+$) มีผลต่อความแม่นยำของผลลัพธ์อย่างมาก

For turbulent flow simulations, near-wall mesh resolution ($y^+$) significantly affects result accuracy

### ความสำคัญของ1$y^+1| Why1$y^+1Matters

$y^+1คือ dimensionless distance จากผนัง:

$y^+1is the dimensionless distance from the wall:

$$y^+ = \frac{y \cdot u_\tau}{\nu} = \frac{y \cdot \sqrt{\tau_w/\rho}}{\nu}$$

### ข้อแนะนำตาม Turbulence Model | Recommendations by Turbulence Model

| Approach |1$y^+1Range | Wall Function | OpenFOAM Type | การใช้งาน | Use Case |
|----------|-------------|---------------|---------------|-------------|----------|
| **Low-Re Models** |1$y^+ < 11| Direct resolution | `nutLowReWallFunction` | ละเอียดมาก, แพง | High accuracy, research |
| **Wall Functions** |1$30 < y^+ < 3001| Log-law | `nutkWallFunction` | ประหยัด, พอถูง | Industrial, fast |
| **Enhanced Wall** |1$1 < y^+ < 51| Blended | `nutUSpaldingWallFunction` | ความแม่นยำสูง | Accurate but expensive |
| **Buffer Zone** |1$1 < y^+ < 301| ❌ AVOID | ❌ | ไม่ valid | Inaccurate region |

**⚠️ CRITICAL**: หลีกเลี่ยงช่วง1$1 < y^+ < 301(buffer layer) เพราะทั้ง linear law และ log-law ไม่ valid

**⚠️ CRITICAL**: Avoid1$1 < y^+ < 301(buffer layer) as neither linear nor log-law is valid

### ตรวจสอบ1$y^+1ใน OpenFOAM | Check1$y^+1in OpenFOAM

#### Step 1: รัน Simulation ให้ Converge

```bash
simpleFoam > log &
```

#### Step 2: คำนวณ1$y^+$

```bash
# คำนวณหลังจาก converge
postProcess -func yPlus -latestTime

# หรือเพิ่มใน controlDict
functions
{
    yPlus
    {
        type            yPlus;
        libs            ("libfieldFunctionObjects.so");
        writeControl    timeStep;
        writeInterval   100;
    }
}
```

#### Step 3: ตรวจสอบค่า

```bash
# ดูค่าเฉลี่ย
paraFoAM -builtin

# หรือ extract statistics
postProcess -func "mag(U)" -latestTime
foamCalc mag grad(U)
```

### คำนวณ First Cell Height | Calculate First Cell Height

กำหนดขนาดเซลล์แรกให้ได้1$y^+1ที่ต้องการ

Determine first cell height to achieve target1$y^+$

```python
#!/usr/bin/env python3
"""
First Cell Height Calculator for Target y+
"""

def calculate_first_cell_height(y_plus_target, Re, U_inf, L_ref):
    """
    Calculate first cell height for target y+
    
    Parameters:
    -----------
    y_plus_target : float
        Target y+ value (e.g., 1 for low-Re, 50 for wall functions)
    Re : float
        Reynolds number
    U_inf : float
        Freestream velocity (m/s)
    L_ref : float
        Reference length (m)
    
    Returns:
    --------
    float : First cell height (m)
    """
    rho = 1.225  # Air density (kg/m^3)
    
    # Skin friction coefficient (flat plate approximation)
    Cf = 0.075 / (np.log10(Re) - 2)**2
    
    # Wall shear stress
    tau_w = 0.5 * Cf * rho * U_inf**2
    
    # Friction velocity
    u_tau = np.sqrt(tau_w / rho)
    
    # Kinematic viscosity
    nu = U_inf * L_ref / Re
    
    # First cell height
    y = y_plus_target * nu / u_tau
    
    return y

def expansion_ratio_calculator(y_first, n_layers, boundary_layer_thickness):
    """
    Calculate expansion ratio for boundary layer mesh
    
    Parameters:
    -----------
    y_first : float
        First cell height
    n_layers : int
        Number of boundary layers
    boundary_layer_thickness : float
        Target boundary layer thickness
    
    Returns:
    --------
    float : Expansion ratio
    """
    # Geometric progression: y_total = y1 * (r^n - 1) / (r - 1)
    # Solve for r numerically or approximate
    r = 1.2  # Initial guess
    
    # Iterative solution
    for _ in range(100):
        y_total = y_first * (r**n_layers - 1) / (r - 1)
        if abs(y_total - boundary_layer_thickness) < 1e-6:
            break
        r += 0.01
    
    return min(r, 1.5)  # Cap at 1.5 for quality

# ============ Examples ============
if __name__ == "__main__":
    
    print("="*60)
    print("FIRST CELL HEIGHT CALCULATOR")
    print("="*60)
    
    # Example 1: Low-Re model (y+ = 1)
    print("\nExample 1: Low-Re Model (y+ = 1)")
    print("-" * 40)
    Re = 1e6
    U = 10.0
    L = 1.0
    
    y1 = calculate_first_cell_height(1, Re, U, L)
    print(f"Re = {Re:.0e}, U = {U} m/s, L = {L} m")
    print(f"First cell height (y+ = 1): {y1:.2e} m = {y1*1e6:.2f} μm")
    
    # Example 2: Wall function (y+ = 50)
    print("\nExample 2: Wall Function (y+ = 50)")
    print("-" * 40)
    y50 = calculate_first_cell_height(50, Re, U, L)
    print(f"First cell height (y+ = 50): {y50:.2e} m = {y50*1e3:.4f} mm")
    
    # Example 3: BlockMeshDict with firstCellHeight
    print("\nExample 3: blockMeshDict with firstCellHeight")
    print("-" * 40)
    print("""
boundary
(
    obj
    {
        type wall;
        faces
        (
            (3 7 6 2)
        );
    }
);

// For boundary layer specification:
castellatedMeshControls
{
    refinementBoxes
    {
        box1
        {
            type inside;
            level (2 2);  // Refinement level
        }
    }
    
    // For addLayers (snappyHexMesh)
    addLayers
    {
        obj
        {
            nSurfaceLayers 20;
            
            // Expansion ratio
            expansionRatio 1.2;
            
            // First layer thickness
            firstLayerThickness1${y50};  // Use calculated value
            
            // Final layer thickness
            finalLayerThickness 0.5;
            
            // Min thickness
            minThickness 0.01;
        }
    }
}
    """)
    
    # Example 4: Multiple conditions
    print("\nExample 4: First Cell Heights for Various Conditions")
    print("-" * 40)
    print(f"{'Re':<10} {'U (m/s)':<10} {'y+ = 1 (mm)':<15} {'y+ = 50 (mm)':<15}")
    print("-" * 50)
    
    for Re_test in [1e5, 1e6, 1e7]:
        for U_test in [5, 10, 20]:
            y1_mm = calculate_first_cell_height(1, Re_test, U_test, 1.0) * 1e3
            y50_mm = calculate_first_cell_height(50, Re_test, U_test, 1.0) * 1e3
            print(f"{Re_test:<10.0e} {U_test:<10.1f} {y1_mm:<15.4f} {y50_mm:<15.4f}")
    
    print("="*60)
```

### การตั้งค่าใน OpenFOAM | OpenFOAM Settings

#### ใน blockMeshDict (สำหรับ simple geometries)

```cpp
// คำนวณ grading เพื่อให้ได้ firstCellHeight
// ระยะทางรวม = sum(y_i) โดย y_i = y1 * r^(i-1)
// ใช้ simpleGrading หรือ edgeGrading

blocks
(
    hex (0 1 2 3 4 5 6 7) 
    (100 100 50) 
    simpleGrading (1 1 10)  // Grading toward wall
);
```

#### ใน snappyHexMeshDict (สำหรับ complex geometries)

```cpp
// system/snappyHexMeshDict
castellatedMeshControls
{
    locationInMesh (0.01 0 0.01);  // Point inside mesh
    
    // หลีกเลี่ยงรูหนอนจาก geometry
    nCellsBetweenLevels 3;
}

addLayersControls
{
    // เปิดใช้ boundary layer
    layers
    {
        "obj.*"
        {
            nSurfaceLayers 20;
        }
    }
    
    // การกระจายตัวของเซลล์
    relativeSizes true;  // หรือ false สำหรับ absolute thickness
    
    expansionRatio 1.2;  // 1.0 - 1.5 (สูงมากอาจทำให้ mesh quality แย่)
    
    finalLayerThickness 0.3;  // 30% ของ local cell size
    
    minThickness 0.01;  // Minimum thickness
    maxFaceThicknessRatio 0.5;
    
    // คุณภาพ mesh
    nGrow 1;
    featureAngle 90;
    nRelaxIter 5;
    nSmoothSurfaceNormals 1;
    nSmoothNormals 3;
    nSmoothThickness 10;
    minMedianAxisAngle 90;
    maxThicknessToMedialRatio 0.3;
}
```

---

## 5. Acceptance Criteria | เกณฑ์การยอมรับ

### มาตรฐาน GCI | GCI Standards

| ประเภท | Type | GCI Target | การใช้งาน | Application |
|--------|-----|------------|-------------|-------------|
| **ขั้นต้น** | Preliminary | < 10% | Screening, trend analysis | การคัดเลือก, ดูแนวโน้ม |
| **การออกแบบ** | Design | < 5% | Engineering decisions | การตัดสินใจทางวิศวกรรม |
| **การตีพิมพ์** | Publication | < 2% | Journal papers | บทความวิจัย |
| **วิจัยขั้นสูง** | High-end Research | < 1% | Benchmarking | การเปรียบเทียบมาตรฐาน |

### เกณฑ์1$y^+1|1$y^+1Criteria

| สถานการณ์ | Situation |1$y^+1Range | การยอมรับ | Acceptance |
|-----------|-----------|-------------|-------------|-------------|
| **Low-Re model** | Resolved turbulence |1$0.2 < y^+ < 11| Max1$y^+ < 11on 95% walls | 95% ของผนังมี1$y^+ < 11|
| **Wall functions** | High-Re model |1$30 < y^+ < 3001| Mean1$y^+ = 50 \pm 201| เฉลี่ย1$50 \pm 201|
| **Avoid** | Buffer zone |1$1 < y^+ < 301| ❌ Reject | ❌ ปฏิเสธ |

### Additional Checks | การตรวจสอบเพิ่มเติม

#### 1. Energy Balance Check (สำหรับ heat transfer)

$$\left|\frac{Q_{in} - Q_{out}}{Q_{in}}\right| < 0.01$$

```python
# ตรวจสอบพลังงาน conservation
def check_energy_balance(Q_in, Q_out, tolerance=0.01):
    imbalance = abs(Q_in - Q_out) / Q_in
    if imbalance < tolerance:
        print(f"✓ Energy balance OK: {imbalance*100:.3f}%")
        return True
    else:
        print(f"✗ Energy imbalance: {imbalance*100:.3f}% > {tolerance*100}%")
        return False
```

#### 2. Mass Balance Check

```bash
# ใช้ function object
functions
{
    flowRate
    {
        type            surfaceRegion;
        libs            ("libfieldFunctionObjects.so");
        
        operation       sum;
        regionType      patch;
        name            inlet;
        
        surfaceFormat   none;
        
        fields
        (
            phi
        );
    }
}
```

#### 3. Residual Convergence

```cpp
// ตรวจสอบว่า convergence จริง
residuals
{
    solver          smoothSolver;
    smoother        GaussSeidel;
    tolerance       1e-06;      // Final tolerance
    relTol          0;          // ไม่ใช้ relative tolerance
    
    // หรือใช้ convergence criteria
    convergence
    {
        type    scaled;
        tolerance   1e-6;
        residual    1e-7;
    }
}
```

---

## 6. Common Pitfalls | ข้อผิดพลาดทั่วไป

<details>
<summary><b>1. ใช้ mesh 2 ระดับเท่านั้น</b></summary>

**ปัญหา**: ไม่สามารถคำนวณ observed order ($p$) ได้ ต้องอนุมานจาก formal order

**วิธีแก้**: ใช้อย่างน้อย 3 ระดับตามมาตรฐาน ASME V&V 20

**Impact**: GCI จะมี safety factor สูงมาก ($F_s = 3.01vs1$1.25$)
</details>

<details>
<summary><b>2. Refinement ratio ไม่คงที่</b></summary>

**ปัญหา**:1$r_{12} \neq r_{23}1ทำให้สูตร GCI ไม่ valid

**วิธีแก้**: ใช้ refinement ratio คงที่ ($r = \sqrt{2}1แนะนำ)

**Check**:1$|r_{12} - r_{23}| < 0.1$
</details>

<details>
<summary><b>3. ไม่อยู่ใน asymptotic range</b></summary>

**ปัญหา**: อัตราส่วน1$GCI_{coarse}/(r^p \cdot GCI_{fine})1ไม่อยู่ใน [0.9, 1.1]

**สาเหตุ**: Mesh ยังไม่ละเอียดพอ หรือ solution ไม่ smooth

**วิธีแก้**: 
- Refine mesh ให้ละเอียดขึ้น
- ตรวจสอบ convergence criteria
- ตรวจสอบว่า quantity of interest smooth หรือไม่
</details>

<details>
<summary><b>4. ใช้ผลลัพธ์ที่ยังไม่ converge</b></summary>

**ปัญหา**: ดึงค่าจาก iteration ที่ยังไม่ stabilize

**วิธีแก้**: 
- ตรวจสอบ residuals < 1e-6
- ตรวจสอบ quantity of interest เป็นฟังก์ชันของเวลา
- ใช้ค่าเฉลี่ยจาก 100 iterations สุดท้าย
</details>

<details>
<summary><b>5.1$y^+1อยู่ใน buffer zone</b></summary>

**ปัญหา**:1$1 < y^+ < 301ทั้ง wall functions และ resolved turbulence ให้ผลผิดพลาด

**วิธีแก้**: 
- สำหรับ wall functions: refine ให้1$y^+ > 30$
- สำหรับ low-Re: refine ให้1$y^+ < 1$

**Check**: `postProcess -func yPlus` หลังจาก converge
</details>

<details>
<summary><b>6. ตรวจสอบเฉพาะ global quantities</b></summary>

**ปัญหา**: Cd  converge แต่ local fields (pressure, velocity) ยังไม่

**วิธีแก้**: 
- ตรวจสอบ profiles ที่สำคัญ (boundary layer profiles)
- ตรวจสอบ local quantities (peak pressure, separation point)
- ใช้ field-wide error norms
</details>

<details>
<summary><b>7. Mesh quality เสียหายจากการ refine</b></summary>

**ปัญหา**: Non-orthogonality, skewness สูงขึ้นเมื่อ refine

**วิธีแก้**: 
- ตรวจสอบ `checkMesh` สำหรับทุกระดับ
- ใช้ grading ที่เหมาะสม (expansion ratio < 1.3)
- ปรับ refinement strategy
</details>

<details>
<summary><b>8. ไม่สามารถ reproduce ได้</b></summary>

**ปัญหา**: เปลี่ยน machine / solver version แล้วผลเปลี่ยน

**วิธีแก้**: 
- บันทึก OpenFOAM version, compiler options
- บันทึก solver settings, tolerance ทั้งหมด
- ใช้ version control สำหรับทุกอย่าง
</details>

---

## Key Takeaways | สรุปสำคัญ

### หลักการสำคัญ | Core Principles

1. **Mesh Independence คือหัวใจของ CFD credibility** - ไม่มีค่านี้ ผลลัพธ์ไม่น่าเชื่อถือ
2. **ASME V&V 20 เป็นมาตรฐานสากล** - ใช้ 3-grid method ด้วย GCI
3. **$y^+1สำคัญเท่ากับ global convergence** สำหรับ turbulent flow
4. **Asymptotic range check ไม่ต้องมีก็ได้แต่แนะนำ** - ยืนยันความ valid ของ GCI
5. **Mesh quality เท่ากับ convergence** - coarse mesh ที่ดี > fine mesh ที่เสียหาย
6. **บันทึกทุกอย่าง** - reproducibility คือหัวใจของวิทยาศาสตร์

### Workflow สรุป | Summary Workflow

```
1. Plan mesh levels (3+, r = 1.3-1.5)
   ↓
2. Generate meshes (check quality)
   ↓
3. Run simulations (to convergence)
   ↓
4. Extract quantities (monitor convergence)
   ↓
5. Calculate GCI (check asymptotic range)
   ↓
6. Verify y+ (post-process)
   ↓
7. Document (settings, results, uncertainties)
```

### Best Practices | แนวปฏิบัติที่ดี

- เริ่มต้นด้วย mesh ที่เหมาะสม (ไม่ละเอียด/หยาบเกินไป)
- ใช้ refinement ratio คงที่ ($r = \sqrt{2}$)
- ตรวจสอบทั้ง global quantities และ local profiles
- ตรวจสอบ mesh quality สำหรับทุกระดับ
- บันทึก OpenFOAM version, solver settings
- ให้ safety factor ถ้าไม่แน่ใจ
- เผยแพร่ทั้งผลลัพธ์ที่ดีและไม่ดี (transparency)

---

## Concept Check | ทดสอบความเข้าใจ

<details>
<summary><b>1. ทำไมต้องใช้ 3 ระดับ mesh? Why 3 mesh levels?</b></summary>

**คำตอบ**: 
- 2 ระดับให้แค่ rate of change → ไม่รู้ว่า solution converge ด้วยอันดับเท่าไร
- 3 ระดับให้คำนวณ **observed order of accuracy ($p$)** → บอกว่า solution กำลัง converge อย่างไร (p = 2 หมายถึง second-order)
- จาก1$p1คำนวณ GCI ได้ (safety factor = 1.25 vs 3.0)

**Answer**: 
- 2 levels → only rate of change, don't know convergence order
- 3 levels → calculate **observed order ($p$)** → tells how solution converges (p = 2 means second-order)
- From1$p$, can calculate GCI (safety factor = 1.25 vs 3.0)
</details>

<details>
<summary><b>2. GCI บอกอะไร? What does GCI tell us?</b></summary>

**คำตอบ**: 
- **GCI = uncertainty band** จาก discretization error
- GCI = 2% แปลว่า true value อยู่ในช่วง1$\pm 2\%1ของค่าที่คำนวณ (95% confidence)
- ค่า GCI ต่ำ = mesh independence ดี
- มาตรฐาน: < 2% (publication), < 5% (design)

**Answer**: 
- **GCI = uncertainty band** from discretization error
- GCI = 2% means true value is within1$\pm 2\%1of calculated value (95% confidence)
- Low GCI = good mesh independence
- Standards: < 2% (publication), < 5% (design)
</details>

<details>
<summary><b>3. ทำไม1$y^+1= 5-30 ไม่ดี? Why is y+ = 5-30 bad?</b></summary>

**คำตอบ**: 
- Buffer layer = transition zone ระหว่าง viscous sublayer ($y^+ < 5$) และ log-law region ($y^+ > 30$)
- ทั้ง linear law ($u^+ = y^+$) และ log-law ไม่ valid ในบริเวณนี้
- Wall functions จะให้ผลผิดพลาด และ resolved turbulence ก็ไม่ได้ประโยชน์
- **แนะนำ**:1$y^+ < 11(low-Re) หรือ1$y^+ = 30-3001(wall functions)

**Answer**: 
- Buffer layer = transition zone between viscous sublayer ($y^+ < 5$) and log-law region ($y^+ > 30$)
- Neither linear law ($u^+ = y^+$) nor log-law is valid here
- Wall functions give wrong results, resolved turbulence gives no benefit
- **Recommend**:1$y^+ < 11(low-Re) or1$y^+ = 30-3001(wall functions)
</details>

<details>
<summary><b>4. Asymptotic range check ล้มเหลว แก้ไขอย่างไร? Asymptotic check fails, what to do?</b></summary>

**คำตอบ**: 
- **ตรวจสอบ**: Refinement ratio คงที่หรือไม่? ($r_{12} \approx r_{23}$)
- **สาเหตุที่เป็นไปได้**:
  1. Mesh ยังไม่ละเอียดพอ → Refine เพิ่ม (เพิ่มระดับที่ 4)
  2. Solution ไม่ smooth → ตรวจสอบ turbulence transition, shocks
  3. Nonlinearity รุนแรง → ลด r ให้น้อยลง
  4. Error จาก iteration → ตรวจสอบ convergence criteria

**Answer**: 
- **Check**: Is refinement ratio constant? ($r_{12} \approx r_{23}$)
- **Possible causes**:
  1. Mesh not refined enough → Refine further (add 4th level)
  2. Solution not smooth → Check turbulence transition, shocks
  3. Strong nonlinearity → Reduce r
  4. Iteration error → Check convergence criteria
</details>

<details>
<summary><b>5. Richardson extrapolation มีประโยชน์อย่างไร? Benefits of Richardson extrapolation?</b></summary>

**คำตอบ**: 
- ให้ **estimate ของ exact solution** โดยไม่ต้อง refine mesh ต่อ
- Accuracy สูงกว่า fine mesh ($O(h^{p+1})1vs1$O(h^p)$)
- ใช้เปรียบเทียบกับ experimental data ได้ดีกว่า
- **ข้อจำกัด**: Valid ใน asymptotic range เท่านั้น

**Answer**: 
- Provides **estimate of exact solution** without further refinement
- More accurate than fine mesh ($O(h^{p+1})1vs1$O(h^p)$)
- Better for comparison with experimental data
- **Limitation**: Valid only in asymptotic range
</details>

<details>
<summary><b>6. ทรัพยากรจำกัด (GPU time) ทำอย่างไร? Limited resources, what to do?</b></summary>

**คำตอบ**: 
- เริ่มต้นด้วย 2 ระดับ (coarse, medium) → ประเมินแนวโน้ม
- ใช้ 2-grid GCI ($F_s = 3.0$) แต่ระบุว่าเป็น preliminary
- Refine เฉพาะบริเวณสำคัญ (adaptation)
- ใช้ wall functions แทน low-Re (ลดจำนวนเซลล์ 10x)
- **แต่ถ้าจะตีพิมพ์**: ต้อง 3 ระดับอย่างน้อย

**Answer**: 
- Start with 2 levels (coarse, medium) → Assess trend
- Use 2-grid GCI ($F_s = 3.0$) but label as preliminary
- Refine only critical regions (adaptation)
- Use wall functions instead of low-Re (10x fewer cells)
- **But for publication**: Minimum 3 levels required
</details>

---

## Related Documents | เอกสารที่เกี่ยวข้อง

### ลำดับบท | Module Sequence

- **บทก่อนหน้า**: [01_V_and_V_Principles.md](01_V_and_V_Principles.md) - หลักการ Verify & Validate, ประเภท Error
- **บทถัดไป**: [03_Experimental_Validation.md](03_Experimental_Validation.md) - การเปรียบเทียบกับข้อมูลทดลอง

### อ้างอิงเพิ่มเติม | Further References

- **ASME V&V 20 Standard**: Standard for Verification and Validation in Computational Fluid Dynamics
- **Roache (1998)**: "Verification of codes and calculations" - AIAA Journal
- **ERCOFTAC Guidelines**: Best Practices for Industrial CFD
- **OpenFOAM User Guide**: `postProcess -func yPlus`, forceCoeffs
- **BlockMesh Best Practices**: การสร้าง graded meshes ที่มี quality ดี

### Tools & Scripts | เครื่องมือและสคริปต์

- **GCI Calculator**: `scripts/gci_calculator.py` - Python script สำหรับคำนวณ GCI
- **First Cell Height**: `scripts/first_cell_calculator.py` - คำนวณขนาดเซลล์แรก
- **Mesh Quality Checker**: `checkMesh -allTopology -allGeometry`

---

**หมายเหตุ**: เนื้อหานี้เตรียมขึ้นตามมาตรฐาน ASME V&V 20 และ best practices จากวรรณกรรม CFD

**Note**: Content prepared according to ASME V&V 20 standard and CFD best practices literature