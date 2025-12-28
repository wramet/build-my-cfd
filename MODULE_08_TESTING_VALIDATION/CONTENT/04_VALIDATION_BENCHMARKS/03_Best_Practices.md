# Best Practices

แนวปฏิบัติที่ดีสำหรับ Validation

---

## Overview

> Follow best practices for **reliable, reproducible** validation

---

## 1. Documentation

| Document | Content |
|----------|---------|
| README | Case description |
| Validation report | Comparison results |
| Reference | Data sources |

---

## 2. Case Organization

```
validation/
├── README.md
├── case/
│   ├── Allrun
│   ├── Allclean
│   ├── system/
│   └── 0/
├── experimental/
│   └── data.csv
├── results/
│   └── comparison.png
└── report.md
```

---

## 3. Mesh Independence Study

```bash
#!/bin/bash
# meshStudy.sh

for level in coarse medium fine; do
    cp -r case case_$level
    cd case_$level
    blockMesh -dict system/blockMeshDict.$level
    simpleFoam
    postProcess -func 'probes'
    cd ..
done

python3 plotConvergence.py
```

---

## 4. Sensitivity Analysis

| Parameter | Range | Default |
|-----------|-------|---------|
| Mesh size | 10k-1M cells | 100k |
| Time step | 1e-6 to 1e-3 | 1e-4 |
| Relaxation | 0.3-0.9 | 0.7 |

---

## 5. Error Reporting

```python
# metrics.py
import numpy as np

def compute_metrics(sim, exp):
    return {
        'RMSE': np.sqrt(np.mean((sim - exp)**2)),
        'MAE': np.mean(np.abs(sim - exp)),
        'R2': 1 - np.sum((sim - exp)**2) / np.sum((exp - np.mean(exp))**2),
        'Max_Error': np.max(np.abs(sim - exp))
    }
```

---

## 6. Acceptance Criteria

| Metric | Threshold |
|--------|-----------|
| Velocity | < 5% error |
| Pressure | < 10% error |
| Temperature | < 2K difference |
| y+ | Within 1-5 range |

---

## 7. Version Control

```bash
# Track changes
git add .
git commit -m "Validation case: backward-facing step"

# Tag validated version
git tag -a v1.0 -m "Validated against NASA data"
```

---

## Quick Reference

| Practice | Why |
|----------|-----|
| Document everything | Reproducibility |
| Mesh study | Verify independence |
| Multiple metrics | Complete picture |
| Version control | Track changes |

---

## Concept Check

<details>
<summary><b>1. Mesh study ทำไม?</b></summary>

**Verify results don't change** with finer mesh
</details>

<details>
<summary><b>2. R² คืออะไร?</b></summary>

**Coefficient of determination** — 1.0 = perfect match
</details>

<details>
<summary><b>3. ทำไมต้อง document?</b></summary>

**Reproducibility** — others can repeat validation
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Physical Validation:** [01_Physical_Validation.md](01_Physical_Validation.md)