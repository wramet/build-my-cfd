# Python Plotting

การสร้างกราฟด้วย Python

---

## Overview

> **Python** = Powerful visualization และ analysis tool

---

## 1. Libraries

| Library | Use |
|---------|-----|
| matplotlib | Basic plotting |
| numpy | Data handling |
| pandas | Data analysis |
| seaborn | Statistical plots |
| PyVista | 3D visualization |

---

## 2. Basic Plot

```python
import numpy as np
import matplotlib.pyplot as plt

# Load OpenFOAM data
data = np.loadtxt('postProcessing/probes/0/p')

# Plot
plt.figure(figsize=(10, 6))
plt.plot(data[:,0], data[:,1], 'b-', label='Pressure')
plt.xlabel('Time [s]')
plt.ylabel('Pressure [Pa]')
plt.legend()
plt.savefig('pressure.png', dpi=300)
```

---

## 3. Profile Comparison

```python
# Load CFD and experimental
cfd = np.loadtxt('postProcessing/sample/0/line_U.xy')
exp = np.loadtxt('experimental.csv', delimiter=',')

plt.figure()
plt.plot(cfd[:,0], cfd[:,1], 'b-', label='CFD')
plt.plot(exp[:,0], exp[:,1], 'ro', label='Experiment')
plt.legend()
plt.savefig('validation.png')
```

---

## 4. Contour Plot

```python
from fluidfoam import readof

# Read field
T = readof.readscalar('case', '100', 'T')
mesh = readof.readmesh('case')

plt.tricontourf(mesh.x, mesh.y, T, levels=50)
plt.colorbar(label='Temperature [K]')
```

---

## 5. Residual Plot

```python
import pandas as pd

# Parse log file
residuals = pd.read_csv('logs/p_0', sep='\s+', header=None)
residuals.columns = ['time', 'residual']

plt.semilogy(residuals['time'], residuals['residual'])
plt.ylabel('Residual')
plt.xlabel('Iteration')
```

---

## Quick Reference

| Task | Code |
|------|------|
| Load data | `np.loadtxt()` |
| Line plot | `plt.plot()` |
| Contour | `plt.contourf()` |
| Save | `plt.savefig()` |

---

## Concept Check

<details>
<summary><b>1. fluidfoam ใช้ทำอะไร?</b></summary>

**Read OpenFOAM** fields directly into Python
</details>

<details>
<summary><b>2. semilogy ใช้เมื่อไหร่?</b></summary>

**Residuals** — log scale on y-axis
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **ParaView:** [01_ParaView_Visualization.md](01_ParaView_Visualization.md)