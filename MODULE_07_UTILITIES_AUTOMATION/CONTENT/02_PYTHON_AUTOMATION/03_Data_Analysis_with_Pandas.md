# Data Analysis with Pandas

การวิเคราะห์ข้อมูลด้วย Pandas

---

## Overview

> **Pandas** = Python data analysis library

---

## 1. Load OpenFOAM Data

```python
import pandas as pd
import numpy as np

# Load probe data
df = pd.read_csv('postProcessing/probes/0/p', 
                 sep='\s+', skiprows=1, 
                 names=['time', 'p1', 'p2', 'p3'])
```

---

## 2. Basic Operations

```python
# Statistics
print(df.describe())

# Filter
high_p = df[df['p1'] > 1000]

# Time average
p_mean = df['p1'].mean()
```

---

## 3. foamLog Data

```python
# Parse residuals
residuals = pd.read_csv('logs/p_0', sep='\s+', 
                        header=None, names=['iter', 'res'])

# Plot convergence
residuals.plot(x='iter', y='res', logy=True)
```

---

## 4. Multiple Cases

```python
cases = ['Re_100', 'Re_500', 'Re_1000']
results = {}

for case in cases:
    results[case] = pd.read_csv(f'{case}/results.csv')

# Compare
df_all = pd.concat(results, axis=1)
```

---

## 5. Export

```python
# To CSV
df.to_csv('results.csv', index=False)

# To LaTeX
print(df.to_latex())
```

---

## Quick Reference

| Task | Code |
|------|------|
| Load | `pd.read_csv()` |
| Stats | `df.describe()` |
| Filter | `df[condition]` |
| Plot | `df.plot()` |

---

## Concept Check

<details>
<summary><b>1. Pandas ดีกว่า numpy อย่างไร?</b></summary>

**Named columns**, easier data manipulation
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
