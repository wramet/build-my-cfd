# Validation Coding

การเขียนโค้ดสำหรับ Validation

---

## Overview

> **Validation** = Verify simulation matches physical reality

---

## 1. Validation Types

| Type | Compare Against |
|------|-----------------|
| **Experimental** | Lab data |
| **Analytical** | Exact solutions |
| **Benchmark** | Standard cases |
| **Code-to-code** | Other solvers |

---

## 2. Post-Processing Function

```cpp
// In controlDict
functions
{
    fieldAverage1
    {
        type            fieldAverage;
        writeControl    writeTime;
        fields
        (
            U { mean on; prime2Mean on; }
            p { mean on; }
        );
    }
}
```

---

## 3. Sampling

```cpp
// Sample along line
functions
{
    sample1
    {
        type    sets;
        writeControl    writeTime;
        setFormat   raw;
        interpolationScheme cellPoint;
        fields  (U p);
        sets
        (
            centerLine
            {
                type    uniform;
                axis    x;
                start   (0 0.5 0.5);
                end     (1 0.5 0.5);
                nPoints 100;
            }
        );
    }
}
```

---

## 4. Compare with Data

```python
#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt

# Load simulation
sim = np.loadtxt('postProcessing/sample1/0/centerLine_U.xy')

# Load experimental
exp = np.loadtxt('experimental_data.csv', delimiter=',')

# Compare
plt.plot(sim[:,0], sim[:,1], label='Simulation')
plt.plot(exp[:,0], exp[:,1], 'o', label='Experiment')
plt.legend()
plt.savefig('validation.png')
```

---

## 5. Error Metrics

```python
# Relative error
rel_error = np.abs(sim - exp) / exp * 100

# RMSE
rmse = np.sqrt(np.mean((sim - exp)**2))

# L2 norm
l2_norm = np.sqrt(np.sum((sim - exp)**2))
```

---

## 6. Pass/Fail Criteria

```bash
# Check error within tolerance
if [ $(echo "$error < 5.0" | bc) -eq 1 ]; then
    echo "PASSED: Error < 5%"
else
    echo "FAILED: Error = $error%"
    exit 1
fi
```

---

## Quick Reference

| Task | Tool |
|------|------|
| Time average | `fieldAverage` |
| Line sample | `sets` |
| Probe points | `probes` |
| Surface data | `surfaces` |

---

## Concept Check

<details>
<summary><b>1. Validation vs Verification?</b></summary>

- **Validation**: Matches physics?
- **Verification**: Code correct?
</details>

<details>
<summary><b>2. RMSE คืออะไร?</b></summary>

**Root Mean Square Error** — aggregate measure of difference
</details>

<details>
<summary><b>3. ทำไมต้อง tolerance?</b></summary>

**Numerical simulations ไม่ exact** — ต้องยอมรับ error ระดับหนึ่ง
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Automation:** [03_Automation_Scripts.md](03_Automation_Scripts.md)