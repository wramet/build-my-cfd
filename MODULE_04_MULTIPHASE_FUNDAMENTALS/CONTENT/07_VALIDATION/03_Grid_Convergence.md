# Grid Convergence Study

การศึกษาการลู่เข้าของกริดสำหรับ Multiphase Flow

---

## Overview

> **เป้าหมาย:** ยืนยันว่าผลลัพธ์ **ไม่ขึ้นกับความละเอียดของ mesh** (Mesh Independent)

```mermaid
flowchart LR
    A[Coarse Mesh] --> B[Medium Mesh]
    B --> C[Fine Mesh]
    C --> D[Richardson Extrapolation]
    D --> E[GCI Calculation]
```

---

## 1. Systematic Mesh Refinement

### Three-Grid Method

| Mesh | Size | Cell Count |
|------|------|------------|
| Coarse | $h$ | $N$ |
| Medium | $h/2$ | $8N$ |
| Fine | $h/4$ | $64N$ |

**Refinement ratio:** $r = h_{coarse}/h_{fine} = 2$ (typical)

### OpenFOAM Commands

```bash
# สร้างและรัน mesh 3 ระดับ
# Coarse mesh
blockMesh
cp -r 0.org 0
interFoam > log.coarse

# Medium mesh (แก้ไข blockMeshDict: จำนวนเซลล์ × 2)
blockMesh
interFoam > log.medium

# Fine mesh (จำนวนเซลล์ × 4)
blockMesh
interFoam > log.fine
```

---

## 2. Richardson Extrapolation

### Observed Order of Accuracy

$$p = \frac{\ln\left(\frac{\phi_3 - \phi_2}{\phi_2 - \phi_1}\right)}{\ln(r)}$$

### Extrapolated Value

$$\phi_{exact} \approx \phi_1 + \frac{\phi_1 - \phi_2}{r^p - 1}$$

**Where:**
- $\phi_1$ = fine mesh result
- $\phi_2$ = medium mesh result
- $\phi_3$ = coarse mesh result
- $r$ = refinement ratio

---

## 3. Grid Convergence Index (GCI)

$$\text{GCI}_{fine} = F_s \frac{|\varepsilon_{12}|}{r^p - 1}$$

| Parameter | Value |
|-----------|-------|
| $F_s$ (3 grids) | 1.25 |
| $F_s$ (2 grids) | 3.0 |

**Relative error:**
$$\varepsilon_{12} = \frac{\phi_1 - \phi_2}{\phi_1}$$

### Acceptance Criteria

| Application | GCI Target |
|-------------|------------|
| Research | < 1% |
| Engineering | < 3% |
| Screening | < 5% |

### Asymptotic Range Check

$$\frac{\text{GCI}_{32}}{r^p \cdot \text{GCI}_{21}} \approx 1.0$$

ค่านี้ควรอยู่ในช่วง **0.8 - 1.2**

---

## 4. Error Norms

### L1 Norm (Average)
$$\varepsilon_{L1} = \frac{1}{N} \sum_{i=1}^{N} \left| \frac{\phi_i - \phi_{ref}}{\phi_{ref}} \right|$$

### L2 Norm (RMS)
$$\varepsilon_{L2} = \sqrt{\frac{1}{N} \sum_{i=1}^{N} \left( \frac{\phi_i - \phi_{ref}}{\phi_{ref}} \right)^2}$$

### L∞ Norm (Maximum)
$$\varepsilon_{max} = \max_{i} \left| \frac{\phi_i - \phi_{ref}}{\phi_{ref}} \right|$$

---

## 5. Multiphase-Specific Considerations

### Interface Resolution

| Model | Interface Cells |
|-------|-----------------|
| VOF | 2-3 cells |
| Level Set | 3-5 cells |

### Target GCI by Field

| Field | GCI Target |
|-------|------------|
| Phase fraction ($\alpha$) | < 3% |
| Velocity | < 5% |
| Pressure | < 2% |

### AMR for Interface

```cpp
// system/dynamicMeshDict
dynamicFvMesh   dynamicRefineFvMesh;

dynamicRefineFvMeshCoeffs
{
    refineInterval  1;
    field           alpha.water;
    lowerRefineLevel 0.01;
    upperRefineLevel 0.99;
    maxRefinement   4;
    maxCells        200000;
}
```

---

## 6. OpenFOAM Implementation

### Extract QoI with Function Objects

```cpp
// system/controlDict
functions
{
    gasHoldup
    {
        type            volRegion;
        operation       volAverage;
        fields          (alpha.gas);
        writeControl    writeTime;
    }

    pressureDrop
    {
        type            surfaceRegion;
        regionType      patch;
        name            inlet;
        operation       areaAverage;
        fields          (p);
    }
}
```

### Interpolate Between Meshes

```bash
# Interpolate from coarse to fine mesh
mapFields ../coarseCase -sourceTime latestTime -consistent
```

---

## 7. GCI Calculation Script

```python
# Python script for GCI calculation
import numpy as np

# Results from 3 mesh levels
phi = [0.152, 0.148, 0.141]  # fine, medium, coarse
r = 2.0  # refinement ratio

# Observed order
p = np.log((phi[2] - phi[1]) / (phi[1] - phi[0])) / np.log(r)

# Richardson extrapolation
phi_exact = phi[0] + (phi[0] - phi[1]) / (r**p - 1)

# GCI (fine mesh)
eps_12 = abs(phi[0] - phi[1]) / phi[0]
GCI_fine = 1.25 * eps_12 / (r**p - 1)

print(f"Observed order: {p:.2f}")
print(f"Extrapolated value: {phi_exact:.4f}")
print(f"GCI (fine): {GCI_fine*100:.2f}%")
```

---

## Quick Reference

| Step | Action |
|------|--------|
| 1 | สร้าง mesh 3 ระดับ (r = 2) |
| 2 | รัน simulation ทั้ง 3 |
| 3 | Extract QoI จาก postProcessing |
| 4 | คำนวณ $p$ (observed order) |
| 5 | คำนวณ $\phi_{exact}$ (Richardson) |
| 6 | คำนวณ GCI |
| 7 | ตรวจสอบ asymptotic range |

---

## Concept Check

<details>
<summary><b>1. ทำไมต้องใช้ mesh 3 ระดับ?</b></summary>

เพราะต้องการคำนวณ **observed order of accuracy** $p$ ซึ่งต้องใช้ผลลัพธ์ 3 จุดในการ fit logarithmic curve
</details>

<details>
<summary><b>2. GCI บอกอะไร?</b></summary>

GCI คือ **uncertainty estimate** ของผลลัพธ์เนื่องจากความละเอียดของ mesh — บอกว่าห่างจาก grid-independent solution เท่าไหร่ในรูปเปอร์เซ็นต์
</details>

<details>
<summary><b>3. ทำไม multiphase ต้องการ interface resolution พิเศษ?</b></summary>

เพราะ **interface** มี **sharp gradients** ของ phase fraction — ถ้า mesh หยาบเกินไป interface จะ **smeared** และทำนาย physics ผิด
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Validation Methodology:** [01_Validation_Methodology.md](01_Validation_Methodology.md)
- **Benchmark Problems:** [02_Benchmark_Problems.md](02_Benchmark_Problems.md)