# Python Plotting for CFD

การสร้างกราฟและ visualization ด้วย Python สำหรับ OpenFOAM

---

## 🎯 Learning Objectives

หลังจากอ่านบทนี้ คุณจะสามารถ:

1. **ใช้งาน** Matplotlib สำหรับ 2D plots ของ CFD data
2. **สร้าง** publication-quality figures สำหรับ journal papers
3. **plot** residuals, forces, และ probe data จาก OpenFOAM
4. **ใช้** Pandas ร่วมกับ Matplotlib สำหรับ data analysis
5. **customize** plots ด้วย styles, colors, และ annotations

---

## 📚 Prerequisites

- Python basics (variables, loops, functions)
- NumPy arrays
- OpenFOAM postProcessing output format

---

## 🏗️ 3W Framework

### What: Python Plotting คืออะไร?

**Matplotlib** เป็น Python library หลักสำหรับสร้างกราฟ:
- 2D line plots, scatter plots, contour plots
- Customizable สำหรับ publication
- Integrates with NumPy และ Pandas

**ใช้ร่วมกับ OpenFOAM:**
- Plot residuals จาก log files
- Visualize probe data
- Compare simulation vs experimental data
- Create parametric study plots

### Why: ทำไมต้องใช้ Python Plotting?

| Aspect | ParaView | Python/Matplotlib |
|--------|----------|-------------------|
| **3D visualization** | ✅ Excellent | ❌ Limited |
| **Publication figures** | ⚠️ Basic | ✅ Full control |
| **Automation** | ⚠️ Scripting needed | ✅ Native |
| **Data analysis** | ❌ | ✅ Pandas integration |
| **Batch processing** | ⚠️ | ✅ Easy |

### How: Basic Workflow

```python
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 1. Load data
data = np.loadtxt('postProcessing/probes/0/p')

# 2. Create plot
fig, ax = plt.subplots(figsize=(8, 6))
ax.plot(data[:, 0], data[:, 1], 'b-', linewidth=2)

# 3. Customize
ax.set_xlabel('Time [s]')
ax.set_ylabel('Pressure [Pa]')
ax.set_title('Pressure at Probe Point')
ax.grid(True)

# 4. Save
plt.savefig('pressure_probe.png', dpi=300, bbox_inches='tight')
```

---

## 📊 Common OpenFOAM Plots

### 1. Residuals Plot

```python
import re
import matplotlib.pyplot as plt

def parse_residuals(log_file):
    """Parse OpenFOAM log file for residuals."""
    residuals = {'Ux': [], 'Uy': [], 'Uz': [], 'p': [], 'k': [], 'omega': []}
    
    with open(log_file, 'r') as f:
        for line in f:
            # Match pattern: Solving for Ux, Initial residual = 0.001
            match = re.search(r'Solving for (\w+),.*Initial residual = ([\d.e+-]+)', line)
            if match:
                field, value = match.groups()
                if field in residuals:
                    residuals[field].append(float(value))
    
    return residuals

# Plot residuals
residuals = parse_residuals('log.simpleFoam')

fig, ax = plt.subplots(figsize=(10, 6))
for field, values in residuals.items():
    if values:
        ax.semilogy(values, label=field)

ax.set_xlabel('Iteration')
ax.set_ylabel('Residual')
ax.set_title('Convergence History')
ax.legend()
ax.grid(True, which='both')
plt.savefig('residuals.png', dpi=300)
```

### 2. Force Coefficients

```python
import pandas as pd
import matplotlib.pyplot as plt

# Load force coefficients
df = pd.read_csv(
    'postProcessing/forceCoeffs/0/coefficient.dat',
    sep=r'\s+',
    skiprows=13,
    names=['Time', 'Cd', 'Cs', 'Cl', 'CmRoll', 'CmPitch', 'CmYaw',
           'Cd(f)', 'Cd(r)', 'Cs(f)', 'Cs(r)', 'Cl(f)', 'Cl(r)']
)

# Plot Cd and Cl
fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

axes[0].plot(df['Time'], df['Cd'], 'b-', linewidth=1.5)
axes[0].set_ylabel('Drag Coefficient (Cd)')
axes[0].grid(True)
axes[0].axhline(y=df['Cd'].iloc[-100:].mean(), color='r', linestyle='--', 
                label=f"Mean Cd = {df['Cd'].iloc[-100:].mean():.4f}")
axes[0].legend()

axes[1].plot(df['Time'], df['Cl'], 'g-', linewidth=1.5)
axes[1].set_xlabel('Time [s]')
axes[1].set_ylabel('Lift Coefficient (Cl)')
axes[1].grid(True)

plt.tight_layout()
plt.savefig('force_coefficients.png', dpi=300)
```

### 3. Velocity Profile Comparison

```python
import numpy as np
import matplotlib.pyplot as plt

# Experimental data
exp_y = np.array([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
exp_u = np.array([0, 0.4, 0.7, 0.85, 0.92, 0.96, 0.98, 0.99, 1.0, 1.0, 0])

# CFD data from sample line
cfd_data = np.loadtxt('postProcessing/sampleLine/1000/lineVelocity_U.xy')
cfd_y = cfd_data[:, 0]
cfd_u = cfd_data[:, 1]

# Normalize
cfd_y_norm = cfd_y / cfd_y.max()
cfd_u_norm = cfd_u / cfd_u.max()

# Plot comparison
fig, ax = plt.subplots(figsize=(6, 8))
ax.plot(exp_u, exp_y, 'ko', markersize=8, label='Experimental')
ax.plot(cfd_u_norm, cfd_y_norm, 'b-', linewidth=2, label='OpenFOAM (k-ω SST)')

ax.set_xlabel('u/U_max')
ax.set_ylabel('y/H')
ax.set_title('Velocity Profile - Channel Flow')
ax.legend()
ax.grid(True)
ax.set_xlim([0, 1.1])
ax.set_ylim([0, 1])

plt.savefig('velocity_profile.png', dpi=300, bbox_inches='tight')
```

---

## 🎨 Publication-Quality Figures

### Style Configuration

```python
import matplotlib.pyplot as plt

# Set global style
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 12,
    'axes.labelsize': 14,
    'axes.titlesize': 16,
    'legend.fontsize': 11,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'figure.figsize': (8, 6),
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'axes.grid': True,
    'grid.alpha': 0.3,
    'lines.linewidth': 2,
})
```

### Color Schemes

```python
# Colorblind-friendly palette
colors = {
    'blue': '#0077BB',
    'red': '#CC3311',
    'green': '#009988',
    'orange': '#EE7733',
    'purple': '#AA3377',
    'grey': '#BBBBBB'
}

# Usage
ax.plot(x, y1, color=colors['blue'], label='k-ε')
ax.plot(x, y2, color=colors['red'], label='k-ω SST')
```

---

## 🧠 Concept Check

<details>
<summary><b>1. semilogy กับ plot ต่างกันอย่างไร?</b></summary>

**semilogy:** Y-axis เป็น logarithmic scale — เหมาะสำหรับ residuals ที่ลดลงหลายลำดับขนาด

**plot:** Linear scale ทั้งสองแกน — สำหรับ data ทั่วไป
</details>

<details>
<summary><b>2. ทำไมต้องใช้ bbox_inches='tight' ใน savefig?</b></summary>

**ป้องกัน labels/titles ถูกตัด**: Matplotlib จะ crop figure ให้พอดีกับ content โดยไม่มี whitespace เกินและไม่ตัด labels ที่อยู่นอก figure bounds
</details>

---

## 📖 Related Documents

- [01_ParaView_Visualization.md](01_ParaView_Visualization.md) — 3D visualization
- [03_Blender_Rendering.md](03_Blender_Rendering.md) — Photorealistic rendering
- [04_Animation_Techniques.md](04_Animation_Techniques.md) — Creating animations