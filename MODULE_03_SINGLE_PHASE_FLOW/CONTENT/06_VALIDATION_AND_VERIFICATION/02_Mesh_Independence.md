# Mesh Independence Study

การตรวจสอบความเป็นอิสระของ Mesh ตามมาตรฐาน ASME V&V 20

---

## Overview

**Mesh Independence** = ผลลัพธ์ไม่เปลี่ยนเมื่อ refine mesh อีกต่อไป

ใช้ **Grid Convergence Index (GCI)** เพื่อวัด discretization uncertainty อย่างเป็นระบบ

---

## 1. Three-Grid Method

ต้องการ Mesh อย่างน้อย 3 ระดับ:

| Level | Cell Size | Use |
|-------|-----------|-----|
| Coarse ($h_1$) | Largest | Initial estimate |
| Medium ($h_2$) | Medium | Convergence check |
| Fine ($h_3$) | Smallest | Best accuracy |

**Requirement:** Refinement ratio $r = h_{coarse}/h_{fine} > 1.3$

---

## 2. GCI Calculation

### Observed Order of Accuracy

$$p = \frac{\ln\left|\frac{f_3 - f_2}{f_2 - f_1}\right|}{\ln(r)}$$

- $f_1, f_2, f_3$ = quantity of interest on coarse, medium, fine

### Richardson Extrapolation

$$f_{exact} \approx f_1 + \frac{f_1 - f_2}{r^p - 1}$$

### Grid Convergence Index

$$GCI_{fine} = F_s \frac{|f_1 - f_2|/|f_1|}{r^p - 1} \times 100\%$$

- $F_s = 1.25$ (three grids)
- $F_s = 3.0$ (two grids)

### Asymptotic Range Check

$$0.9 < \frac{GCI_{coarse}}{r^p \cdot GCI_{fine}} < 1.1$$

---

## 3. OpenFOAM Workflow

### Step 1: Create Multiple Meshes

```bash
# system/blockMeshDict - change cells
sed 's/cells (100 100 1);/cells (50 50 1);/' system/blockMeshDict > coarse/system/blockMeshDict
blockMesh -case coarse
blockMesh -case medium
blockMesh -case fine
```

### Step 2: Extract Quantity of Interest

```cpp
// system/controlDict
functions
{
    forceCoeffs
    {
        type    forceCoeffs;
        libs    (fieldFunctionObjects);
        patches (object);
        rho     rhoInf;
        rhoInf  1.225;
        magUInf 10.0;
        lRef    1.0;
        Aref    1.0;
    }
}
```

### Step 3: Analyze with Python

```python
import numpy as np

def calculate_gci(f, h, Fs=1.25):
    f1, f2, f3 = f  # coarse, medium, fine
    r = h[0] / h[1]
    
    # Order of convergence
    p = np.log(abs((f3-f2)/(f2-f1))) / np.log(r)
    
    # Richardson extrapolation
    f_exact = f1 + (f1-f2)/(r**p - 1)
    
    # GCI
    GCI = Fs * abs(f1-f2)/abs(f1) / (r**p - 1) * 100
    
    return {'p': p, 'f_exact': f_exact, 'GCI': GCI}

# Example
f = [1.245, 1.198, 1.187]  # Cd values
h = [0.02, 0.015, 0.01]    # cell sizes
result = calculate_gci(f, h)
print(f"GCI = {result['GCI']:.2f}%")
```

---

## 4. $y^+$ Requirements

สำหรับ turbulence modeling:

| Type | $y^+$ | Wall Function |
|------|-------|---------------|
| Low-Re | < 1 | `nutLowReWallFunction` |
| Wall Functions | 30-300 | `nutkWallFunction` |
| Buffer (avoid!) | 1-30 | Inaccurate |

### Check $y^+$

```bash
postProcess -func yPlus
```

### Calculate First Cell Height

```python
def first_cell_height(y_plus_target, Re, U, L):
    Cf = 0.075 / (np.log10(Re) - 2)**2
    tau_w = 0.5 * Cf * 1.225 * U**2
    u_tau = np.sqrt(tau_w / 1.225)
    nu = U * L / Re
    return y_plus_target * nu / u_tau

# y+ = 1
y = first_cell_height(1, 1e6, 10, 1)
print(f"First cell: {y:.2e} m")
```

---

## 5. Acceptance Criteria

| Application | GCI Target | $y^+$ Check |
|-------------|------------|-------------|
| Preliminary | < 10% | Verify range |
| Design | < 5% | In target |
| Publication | < 2% | Perfect |

### Energy Balance Check

$$\left|\frac{Q_{in} - Q_{out}}{Q_{in}}\right| < 0.01$$

---

## Concept Check

<details>
<summary><b>1. ทำไมต้องใช้ 3 ระดับ mesh?</b></summary>

สองระดับให้ได้แค่ rate of change — สามระดับให้คำนวณ **observed order of accuracy ($p$)** ซึ่งบอกว่า solution กำลัง converge อย่างไร
</details>

<details>
<summary><b>2. GCI บอกอะไร?</b></summary>

GCI = uncertainty band จาก discretization — ถ้า GCI = 2% แปลว่าค่าจริงอยู่ในช่วง $\pm 2\%$ ของค่าที่คำนวณได้
</details>

<details>
<summary><b>3. ทำไม $y^+$ = 5-30 ไม่ดี?</b></summary>

Buffer layer เป็นบริเวณ transition ที่ทั้ง linear law ($u^+ = y^+$) และ log-law ไม่ valid — wall functions จะให้ผลผิดพลาด
</details>

---

## Related Documents

- **บทก่อนหน้า:** [01_V_and_V_Principles.md](01_V_and_V_Principles.md)
- **บทถัดไป:** [03_Experimental_Validation.md](03_Experimental_Validation.md)