# Python Plotting for OpenFOAM

การสร้างกราฟและการวิเคราะห์ข้อมูลด้วย Python สำหรับ OpenFOAM

---

## Learning Objectives

หลังจากอ่านบทนี้ คุณจะสามารถ:

- ✅ **ติดตั้งและตั้งค่า** Python libraries ที่จำเป็นสำหรับ OpenFOAM visualization (matplotlib, seaborn, PyVista, fluidfoam)
- ✅ **โหลดและประมวลผลข้อมูล** OpenFOAM ทั้งจาก log files, probes และ time directories
- ✅ **เลือกใช้ library ที่เหมาะสม** ระหว่าง matplotlib, seaborn และ PyVista ตามประเภทของข้อมูลและวัตถุประสงค์
- ✅ **สร้างกราฟคุณภาพสูง** (publication-quality) สำหรับบทความวิจัยและรายงาน
- ✅ **จัดการหน่วยความจำ** เมื่อทำงานกับ large datasets อย่างมีประสิทธิภาพ

---

## Prerequisites

- พื้นฐานการใช้งาน OpenFOAM ([00_Overview.md](00_Overview.md))
- ความเข้าใจเกี่ยวกับ OpenFOAM directory structure และ output formats
- พื้นฐาน Python programming fundamentals
- แนะนำให้ศึกษา **ParaView visualization** ([01_ParaView_Visualization.md](01_ParaView_Visualization.md)) ก่อนเพื่อเข้าใจข้อมูล 3D

---

## 3W Framework

### What (อะไรคือ Python Plotting สำหรับ OpenFOAM?)

Python plotting คือการใช้ Python ecosystem เพื่อ:
- สร้าง **2D graphs**: time-series, profiles, comparisons
- สร้าง **3D visualizations**: isosurfaces, streamlines, volume rendering
- วิเคราะห์ **simulation data**: residuals, convergence, validation
- สร้าง **publication-quality figures**: พร้อมส่งวารสาร

### Why (ทำไมต้องใช้ Python?)

| เหตุผล | คำอธิบาย |
|---------|-----------|
| 🔄 **Reproducibility** | Script สามารถ reuse และ modify ได้ง่ายเมื่อข้อมูลเปลี่ยน |
| 📊 **Automation** | Batch processing หลาย test cases ได้อัตโนมัติ |
| 🎨 **Customization** | ปรับแต่งสไตล์กราฟได้ละเอียดกว่า ParaView |
| 🔬 **Integration** | วิเคราะห์ข้อมูลร่วมกับ experimental data ได้ |
| 💾 **Post-processing** | คำนวณ quantities ใหม่จาก CFD results ได้ |

### When (เมื่อไหร่ควรใช้ Python vs ParaView?)

```
┌─────────────────────────────────────────────────────────────────┐
│                    Decision Flowchart                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   มีข้อมูล 3D และต้องการ interactive exploration?           │
│          │                                                     │
│          ├─── YES ──→ ใช้ ParaView (01_ParaView_Visualization.md)│
│          │                                                     │
│          └─── NO ──→ ต้องการกราฟแบบใด?                      │
│                       │                                         │
│         ┌─────────────┼─────────────┐                          │
│         ▼             ▼             ▼                          │
│    Line plots   Contour plots  3D fields                       │
│    (time-series) (2D slices)   (volumes)                       │
│         │             │             │                          │
│         ▼             ▼             ▼                          │
│     matplotlib    matplotlib     PyVista                        │
│       / seaborn   / fluidfoam                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**ใช้ Python เมื่อ:**
- ต้องการ **line plots**: convergence history, probe data, validation
- ต้องการ **custom 2D contours**: พร้อม annotation และ formatting
- ต้องการ **batch processing**: หลาย cases หรือหลาย timesteps
- ต้องการ **integration**: กับ data analysis workflow อื่นๆ

**ใช้ ParaView เมื่อ:**
- ต้องการ **3D interactive visualization** ([01_ParaView_Visualization.md](01_ParaView_Visualization.md))
- ต้องการ **quick inspection** ของ flow fields
- ต้องการ **isosurfaces และ streamlines** แบบ real-time

### How (ใช้งานอย่างไร?)

```python
# Basic workflow pattern
1. Install required libraries (matplotlib, numpy, pandas, PyVista, fluidfoam)
2. Load OpenFOAM data (logs, probes, time directories)
3. Process/transform data if needed
4. Create appropriate visualization (line, contour, 3D)
5. Format for publication (labels, styles, resolution)
6. Export to file (PNG, PDF, SVG) or display interactively
```

---

## 1. Installation & Setup

### 1.1 Required Libraries

```bash
# Using pip (recommended for beginners)
pip install numpy matplotlib pandas seaborn pyvista fluidfoam

# Using conda (recommended for scientific computing)
conda install -c conda-forge numpy matplotlib pandas seaborn pyvista
pip install fluidfoam
```

### 1.2 Verify Installation

```python
import sys
print(f"Python version: {sys.version}")

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import pyvista as pv
import fluidfoam

print("✓ All libraries imported successfully!")
print(f"NumPy: {np.__version__}")
print(f"Matplotlib: {plt.matplotlib.__version__}")
print(f"PyVista: {pv.__version__}")
```

### 1.3 Setup for OpenFOAM

```python
# Set environment variables (if needed)
import os
os.environ['FOAM_RUN'] = '/path/to/OpenFOAM/cases'

# Or use fluidfoam to read OpenFOAM cases directly
import fluidfoam
print(f"fluidfoam version: {fluidfoam.__version__}")
```

### 1.4 Sample Data Structure

สำหรับทดสอบ code ในบทนี้ สามารถใช้ OpenFOAM tutorial cases:

```
tutorialCase/
├── 0/                    # Initial conditions
│   ├── p
│   └── U
├── constant/             # Mesh & properties
│   └── polyMesh/
├── system/               # Simulation settings
│   ├── controlDict
│   └── fvSchemes
└── postProcessing/       # Output data
    ├── probes/           # Time history at points
    │   └── 0/
    │       └── p         # Probe pressure data
    ├── sampleDict/       # Sampled along lines/planes
    │   └── 0/
    │       └── line_U.xy
    └── logs/             # Solver residuals
        └── pimpleFoam
```

**💡 Tip:** ใช้ `foamListTimes` เพื่อดู timesteps ที่มี:

```bash
cd tutorialCase
foamListTimes
```

---

## 2. Library Comparison Guide

### 2.1 When to Use Each Library

| Library | Strengths | Weaknesses | Best For |
|---------|-----------|------------|----------|
| **matplotlib** | Full control, publication quality, extensive documentation | Verbose for complex plots, limited 3D | Line plots, simple contours, customization-heavy figures |
| **seaborn** | Beautiful defaults, statistical plots, less code | Less flexible than matplotlib | Quick statistical analysis, heatmaps, distribution plots |
| **PyVista** | Easy 3D visualization, VTK backend, interactive | Requires 3D mesh data | 3D isosurfaces, volume rendering, streamlines |
| **fluidfoam** | Reads OpenFOAM directly, simple API | Limited to OpenFOAM, basic plotting | Loading OpenFOAM fields, mesh extraction |

### 2.2 Comparison Matrix

```
┌────────────────────┬──────────────┬──────────┬──────────┬─────────────┐
│ Feature            │ matplotlib   │ seaborn  │ PyVista  │ fluidfoam   │
├────────────────────┼──────────────┼──────────┼──────────┼─────────────┤
│ Line plots         │ ★★★★★        │ ★★★★     │ ★★       │ ★★★         │
│ 2D contours        │ ★★★★★        │ ★★★      │ ★★★★     │ ★★★         │
│ 3D visualization   │ ★★           │ ☆        │ ★★★★★    │ ★★ (read)   │
│ Statistical plots  │ ★★           │ ★★★★★    │ ★        │ ☆           │
│ OpenFOAM I/O       │ ★ (manual)   │ ☆        │ ★★★      │ ★★★★★       │
│ Publication quality│ ★★★★★        │ ★★★★     │ ★★★      │ ★★          │
│ Learning curve     │ Medium       │ Easy     │ Medium   │ Easy        │
└────────────────────┴──────────────┴──────────┴──────────┴─────────────┘
```

### 2.3 Decision Tree

```
Need to visualize OpenFOAM data?
         │
         ├─→ 3D volume/surface?
         │   └─→ YES: Use PyVista (Section 6)
         │
         ├─→ Statistical comparison?
         │   └─→ YES: Use seaborn (Section 5)
         │
         ├─→ Time-series/probes?
         │   └─→ YES: Use matplotlib (Section 3)
         │
         └─→ 2D contours?
             └─→ YES: Use matplotlib + fluidfoam (Section 4)
```

---

## 3. Basic Plotting with matplotlib

### 3.1 Time-Series Plots (Probes)

**Scenario:** Monitor pressure at a point over time

```python
import numpy as np
import matplotlib.pyplot as plt

# =====================================================
# STEP 1: Load probe data
# =====================================================
# OpenFOAM probe format: [time, value1, value2, ...]
probe_file = 'postProcessing/probes/0/p'

# Load data (skip header lines if any)
data = np.loadtxt(probe_file, skiprows=0)

# Extract time and pressure
time = data[:, 0]           # Column 0: time
pressure = data[:, 1]       # Column 1: pressure at first probe location

print(f"Data shape: {data.shape}")
print(f"Time range: {time[0]:.3f} - {time[-1]:.3f} s")

# =====================================================
# STEP 2: Create publication-quality plot
# =====================================================
fig, ax = plt.subplots(figsize=(10, 6))

# Plot with formatting
ax.plot(time, pressure, 
        color='#1f77b4',       # Professional blue
        linewidth=2,           # Thicker line for visibility
        label='Probe at (0.1, 0.05, 0.0)')

# Axis formatting
ax.set_xlabel('Time [s]', fontsize=14, fontweight='bold')
ax.set_ylabel('Pressure [Pa]', fontsize=14, fontweight='bold')
ax.set_title('Pressure Evolution at Probe Location', fontsize=16)

# Grid and legend
ax.grid(True, alpha=0.3, linestyle='--')
ax.legend(fontsize=12, loc='best')

# Set limits if needed
ax.set_xlim([0, max(time)])
ax.set_ylim([min(pressure)*0.95, max(pressure)*1.05])

# =====================================================
# STEP 3: Save in high resolution
# =====================================================
plt.tight_layout()  # Prevent label clipping
plt.savefig('pressure_evolution.png', 
            dpi=300,               # Publication resolution
            bbox_inches='tight')   # Remove whitespace

plt.savefig('pressure_evolution.pdf',
            dpi=300,
            bbox_inches='tight')

print("✓ Plots saved: pressure_evolution.png, pressure_evolution.pdf")
```

**Output:**
```
Data shape: (500, 2)
Time range: 0.000 - 1.000 s
✓ Plots saved: pressure_evolution.png, pressure_evolution.pdf
```

### 3.2 Multiple Probes on Same Plot

```python
import numpy as np
import matplotlib.pyplot as plt

# Load probe data (assume 3 probe locations)
probe_file = 'postProcessing/probes/0/p'
data = np.loadtxt(probe_file)

time = data[:, 0]
pressure_1 = data[:, 1]
pressure_2 = data[:, 2]
pressure_3 = data[:, 3]

fig, ax = plt.subplots(figsize=(12, 6))

# Plot all probes with different styles
ax.plot(time, pressure_1, 'b-', linewidth=2, label='Inlet')
ax.plot(time, pressure_2, 'r--', linewidth=2, label='Mid-section')
ax.plot(time, pressure_3, 'g:', linewidth=2, label='Outlet')

ax.set_xlabel('Time [s]', fontsize=14)
ax.set_ylabel('Pressure [Pa]', fontsize=14)
ax.set_title('Pressure at Multiple Locations', fontsize=16)
ax.grid(True, alpha=0.3)
ax.legend(fontsize=12)

plt.tight_layout()
plt.savefig('multiple_probes.png', dpi=300)
```

---

## 4. Contour Plots with fluidfoam

### 4.1 Installation

```bash
pip install fluidfoam
```

### 4.2 Reading OpenFOAM Fields

```python
from fluidfoam import readof
import numpy as np
import matplotlib.pyplot as plt

# =====================================================
# STEP 1: Read OpenFOAM mesh and field
# =====================================================
case_path = 'myCase'          # Path to OpenFOAM case
time_step = '500'             # Time directory to read

# Read mesh coordinates
mesh = readof.readmesh(case_path)
print(f"Mesh nodes: {len(mesh.x)}")
print(f"x range: [{mesh.x.min():.3f}, {mesh.x.max():.3f}]")
print(f"y range: [{mesh.y.min():.3f}, {mesh.y.max():.3f}]")

# Read scalar field (e.g., pressure, temperature)
T = readof.readscalar(case_path, time_step, 'T')
print(f"Field T range: [{T.min():.2f}, {T.max():.2f}]")

# Read vector field (e.g., velocity)
U = readof.readvector(case_path, time_step, 'U')
U_mag = np.sqrt(U[:, 0]**2 + U[:, 1]**2 + U[:, 2]**2)
print(f"Velocity magnitude: {U_mag.max():.3f} m/s")
```

### 4.3 2D Contour Plot

```python
import matplotlib.pyplot as plt
from fluidfoam import readof
import numpy as np

# Read data
mesh = readof.readmesh('myCase')
T = readof.readscalar('myCase', '500', 'T')

# =====================================================
# STEP 2: Create filled contour plot
# =====================================================
fig, ax = plt.subplots(figsize=(10, 8))

# Triangulated contour (unstructured mesh)
levels = np.linspace(T.min(), T.max(), 50)
contour = ax.tricontourf(mesh.x, mesh.y, T, 
                        levels=levels,
                        cmap='jet',          # Color scheme
                        extend='both')       # Extend colorbar

# Add contour lines
ax.tricontour(mesh.x, mesh.y, T, 
              levels=10,
              colors='black',
              linewidths=0.5,
              alpha=0.3)

# Colorbar
cbar = plt.colorbar(contour, ax=ax)
cbar.set_label('Temperature [K]', fontsize=14, fontweight='bold')

# Formatting
ax.set_xlabel('x [m]', fontsize=14)
ax.set_ylabel('y [m]', fontsize=14)
ax.set_title('Temperature Distribution at t=500s', fontsize=16)
ax.set_aspect('equal')  # Preserve aspect ratio
ax.grid(True, alpha=0.2)

plt.tight_layout()
plt.savefig('temperature_contour.png', dpi=300)
print("✓ Contour plot saved")
```

### 4.4 Velocity Magnitude Contour

```python
# Read velocity field
U = readof.readvector('myCase', '500', 'U')
U_mag = np.sqrt(U[:, 0]**2 + U[:, 1]**2 + U[:, 2]**2)

fig, ax = plt.subplots(figsize=(10, 8))

levels = np.linspace(0, U_mag.max(), 50)
contour = ax.tricontourf(mesh.x, mesh.y, U_mag,
                        levels=levels,
                        cmap='viridis')

cbar = plt.colorbar(contour, ax=ax)
cbar.set_label('Velocity Magnitude [m/s]', fontsize=14)

ax.set_xlabel('x [m]', fontsize=14)
ax.set_ylabel('y [m]', fontsize=14)
ax.set_title('Velocity Magnitude', fontsize=16)
ax.set_aspect('equal')

plt.tight_layout()
plt.savefig('velocity_contour.png', dpi=300)
```

---

## 5. Statistical Plots with seaborn

### 5.1 Validation: CFD vs Experimental Data

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# =====================================================
# STEP 1: Load CFD and experimental data
# =====================================================
# CFD output from sampleDict
cfd_data = np.loadtxt('postProcessing/sample/0/line_U.xy', 
                      skiprows=0)
cfd_x = cfd_data[:, 0]
cfd_u = cfd_data[:, 1]

# Experimental data (CSV format)
exp_data = pd.read_csv('experimental_velocity.csv')
exp_x = exp_data['x'].values
exp_u = exp_data['U'].values

# =====================================================
# STEP 2: Create comparison plot
# =====================================================
sns.set_style('whitegrid')      # Professional style
sns.set_context('paper',         # Publication settings
                font_scale=1.3)

fig, ax = plt.subplots(figsize=(10, 6))

# CFD: line plot
ax.plot(cfd_x, cfd_u, 
        'b-', linewidth=2.5, label='CFD (OpenFOAM)')

# Experimental: scatter with error bars
ax.errorbar(exp_x, exp_u, 
            yerr=exp_data['U_err'].values,
            fmt='ro', markersize=8,
            capsize=5, capthick=2,
            label='Experiment')

# Formatting
ax.set_xlabel('Position x [m]', fontsize=14, fontweight='bold')
ax.set_ylabel('Velocity U [m/s]', fontsize=14, fontweight='bold')
ax.set_title('CFD Validation: Velocity Profile Comparison', fontsize=16)

ax.legend(fontsize=12, loc='best')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('validation_comparison.png', dpi=300)
print("✓ Validation plot saved")
```

### 5.2 Heatmap for Parameter Study

```python
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

# Load parameter study results
df = pd.read_csv('parameter_study.csv')

# Create pivot table for heatmap
pivot_table = df.pivot('velocity_inlet', 'mesh_size', 'drag_coefficient')

# Plot heatmap
fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(pivot_table, 
            annot=True,           # Show values
            fmt='.3f',            # Number format
            cmap='RdYlGn_r',      # Color scheme (reversed)
            cbar_kws={'label': 'Drag Coefficient [-]'},
            ax=ax)

ax.set_xlabel('Mesh Size [cells]', fontsize=14)
ax.set_ylabel('Inlet Velocity [m/s]', fontsize=14)
ax.set_title('Drag Coefficient: Parameter Study', fontsize=16)

plt.tight_layout()
plt.savefig('parameter_heatmap.png', dpi=300)
```

### 5.3 Multiple Cases Comparison

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load results from multiple cases
cases = ['case_rough', 'case_smooth', 'case_optimized']
data_list = []

for case in cases:
    df = pd.read_csv(f'{case}/forces.dat', 
                     sep='\s+', 
                     names=['time', 'drag', 'lift'])
    df['case'] = case.replace('case_', '').title()
    data_list.append(df)

# Combine all data
all_data = pd.concat(data_list, ignore_index=True)

# Plot with seaborn
sns.set_style('whitegrid')
fig, ax = plt.subplots(figsize=(12, 6))

sns.lineplot(data=all_data, 
             x='time', 
             y='drag', 
             hue='case',
             style='case',
             linewidth=2.5,
             ax=ax)

ax.set_xlabel('Time [s]', fontsize=14)
ax.set_ylabel('Drag Force [N]', fontsize=14)
ax.set_title('Drag Force Comparison', fontsize=16)
ax.legend(title='Case', fontsize=11)

plt.tight_layout()
plt.savefig('multi_case_comparison.png', dpi=300)
```

---

## 6. 3D Visualization with PyVista

### 6.1 Installation

```bash
# Using pip
pip install pyvista[q]  # [q] includes Qt for interactive display

# Using conda
conda install -c conda-forge pyvista pyvistaqt
```

### 6.2 Reading OpenFOAM Data

```python
import pyvista as pv
import numpy as np

# =====================================================
# STEP 1: Read OpenFOAM case
# =====================================================
# PyVista can read OpenFOAM format directly
mesh = pv.OpenFOAMReader('myCase/myCase.foam')

# List available arrays
print("Available point arrays:", mesh.array_names)
print("Time steps:", mesh.time_values)

# Set time step
mesh.set_active_time_value(0.5)  # t = 0.5s

# Read mesh data
grid = mesh.read()
print(f"Grid points: {grid.n_points}")
print(f"Grid cells: {grid.n_cells}")
```

### 6.3 3D Isosurface

```python
import pyvista as pv

# Load mesh
reader = pv.OpenFOAMReader('myCase/myCase.foam')
reader.set_active_time_value(0.5)
mesh = reader.read()

# =====================================================
# STEP 2: Create isosurface
# =====================================================
# Extract isosurface at specific value
isosurf = mesh.contour(isosurfaces=[300], scalars='T')

# Plot
plotter = pv.Plotter(window_size=[1024, 768])
plotter.add_mesh(isosurf, 
                 color='cyan',
                 opacity=0.8,
                 show_edges=False,
                 label='T = 300K')

# Add outline
plotter.add_mesh(mesh.outline(), color='black')

# Add axes
plotter.add_axes()

# Set camera and background
plotter.camera_position = 'xy'
plotter.background_color = 'white'

plotter.add_legend()
plotter.show()
```

### 6.4 Volume Rendering

```python
# Volume rendering for scalar fields
plotter = pv.Plotter(window_size=[1024, 768])

# Add volume with opacity transfer function
plotter.add_volume(mesh, 
                  scalars='T',
                  cmap='jet',
                  opacity='linear',
                  show_scalar_bar=True,
                  scalar_bar_args={'title': 'Temperature [K]'})

plotter.camera_position = 'xy'
plotter.add_axes()
plotter.show()
```

### 6.5 Slice Planes

```python
# Create slice at specific location
slice_x = mesh.slice(normal='x', origin=(0.5, 0, 0))
slice_y = mesh.slice(normal='y', origin=(0, 0.5, 0))

plotter = pv.Plotter(window_size=[1024, 768])

plotter.add_mesh(slice_x, 
                 scalars='T',
                 cmap='jet',
                 show_scalar_bar=True,
                 label='x-slice')

plotter.add_mesh(slice_y,
                 scalars='T',
                 cmap='jet',
                 label='y-slice')

plotter.add_legend()
plotter.show()
```

---

## 7. Residual and Convergence Plots

### 7.1 Parsing Solver Log Files

```python
import pandas as pd
import matplotlib.pyplot as plt
import re

def parse_openfoam_log(log_file):
    """
    Parse OpenFOAM solver log for residuals.
    
    Example log format:
    Time = 0.1
    ...
    DICPCG:  Solving for p, Initial residual = 0.001, Final residual = 1e-5, No Iterations 50
    DILUPBiCG:  Solving for Ux, Initial residual = 0.01, Final residual = 1e-6, No Iterations 5
    """
    
    data = {'time': [], 'p': [], 'Ux': [], 'Uy': [], 'Uz': []}
    
    with open(log_file, 'r') as f:
        for line in f:
            # Extract time
            time_match = re.search(r'Time = (\d+\.\d+)', line)
            if time_match:
                data['time'].append(float(time_match.group(1)))
            
            # Extract residuals
            p_match = re.search(r'Solving for p.*Initial residual = ([\d.e-]+)', line)
            if p_match:
                data['p'].append(float(p_match.group(1)))
            
            U_match = re.search(r'Solving for Ux.*Initial residual = ([\d.e-]+)', line)
            if U_match:
                data['Ux'].append(float(U_match.group(1)))
    
    return pd.DataFrame(data)

# Usage
df = parse_openfoam_log('log.pimpleFoam')
print(df.head())
```

### 7.2 Residual Plot

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(12, 6))

# Plot residuals on log scale
ax.semilogy(df['time'], df['p'], 'b-', linewidth=2, label='p')
ax.semilogy(df['time'], df['Ux'], 'r-', linewidth=2, label='Ux')
ax.semilogy(df['time'], df['Uy'], 'g-', linewidth=2, label='Uy')

# Formatting
ax.set_xlabel('Time [s]', fontsize=14)
ax.set_ylabel('Initial Residual [-]', fontsize=14)
ax.set_title('Solver Convergence History', fontsize=16)
ax.grid(True, alpha=0.3, which='both')
ax.legend(fontsize=12, loc='best')

# Add convergence threshold
ax.axhline(y=1e-5, color='k', linestyle='--', alpha=0.5, label='Target')
ax.text(df['time'].iloc[-1]*0.9, 1e-4, 'Target: 1e-5', fontsize=10)

plt.tight_layout()
plt.savefig('convergence_history.png', dpi=300)
```

### 7.3 Force Convergence

```python
# Parse force coefficients from log
import re
import matplotlib.pyplot as plt

# Example: extract Cd and Cl from log
time_vals = []
cd_vals = []
cl_vals = []

with open('log.simpleFoam', 'r') as f:
    for line in f:
        # Match force coefficients
        match = re.search(r'Cd\s*=\s*([\d.e-]+)\s*Cl\s*=\s*([\d.e-]+)', line)
        if match:
            # Find preceding time
            # (Simplified - in practice, track time separately)
            cd_vals.append(float(match.group(1)))
            cl_vals.append(float(match.group(2)))

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

ax1.plot(cd_vals, 'b-', linewidth=2)
ax1.set_ylabel('Drag Coefficient [-]', fontsize=12)
ax1.grid(True, alpha=0.3)
ax1.set_title('Force Coefficient Convergence', fontsize=14)

ax2.plot(cl_vals, 'r-', linewidth=2)
ax2.set_xlabel('Iteration', fontsize=12)
ax2.set_ylabel('Lift Coefficient [-]', fontsize=12)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('force_convergence.png', dpi=300)
```

---

## 8. Publication-Quality Plots

### 8.1 Style Guidelines

**มาตรฐานวารสารวิทยาศาสตร์:**

| Element | Guideline |
|---------|-----------|
| **Font size** | 10-12 pt for labels, 14-16 pt for titles |
| **Line width** | 1.5-2.5 pt for visibility |
| **Colors** | Use colorblind-safe palettes |
| **Resolution** | 300-600 DPI for raster, vector for printing |
| **Aspect ratio** | 4:3 or 16:9 depending on layout |
| **Units** | Always include units in axis labels |

### 8.2 Custom Style Template

```python
import matplotlib.pyplot as plt
import numpy as np

# =====================================================
# Publication style configuration
# =====================================================
def setup_publication_style():
    """Configure matplotlib for publication-quality plots."""
    
    # Figure settings
    plt.rcParams['figure.dpi'] = 100
    plt.rcParams['savefig.dpi'] = 300
    plt.rcParams['figure.figsize'] = [10, 6]
    
    # Font settings
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Times New Roman']
    plt.rcParams['font.size'] = 12
    plt.rcParams['axes.labelsize'] = 14
    plt.rcParams['axes.titlesize'] = 16
    
    # Line settings
    plt.rcParams['lines.linewidth'] = 2.0
    plt.rcParams['lines.markersize'] = 8
    
    # Legend settings
    plt.rcParams['legend.fontsize'] = 12
    plt.rcParams['legend.frameon'] = True
    
    # Grid settings
    plt.rcParams['grid.alpha'] = 0.3
    plt.rcParams['grid.linestyle'] = '--'
    
    # Axis settings
    plt.rcParams['axes.linewidth'] = 1.5
    plt.rcParams['xtick.major.width'] = 1.5
    plt.rcParams['ytick.major.width'] = 1.5

# Apply style
setup_publication_style()

# =====================================================
# Example: Publication-quality comparison plot
# =====================================================
fig, ax = plt.subplots(figsize=(10, 6))

# CFD data
cfd_x = np.linspace(0, 1, 100)
cfd_u = 1 - cfd_x**2

# Experimental data
exp_x = np.linspace(0, 1, 20)
exp_u = 1 - cfd_x**2 + np.random.normal(0, 0.05, 20)

# Plot
ax.plot(cfd_x, cfd_u, 'b-', linewidth=2.5, label='CFD')
ax.errorbar(exp_x, exp_u, yerr=0.05, fmt='ro', 
            markersize=6, capsize=4, label='Experiment')

# Formatting
ax.set_xlabel('Position y/h [-]', fontweight='bold')
ax.set_ylabel('Velocity U/U$_{center}$ [-]', fontweight='bold')
ax.set_title('Channel Flow Validation', fontsize=16, fontweight='bold')
ax.legend(loc='best', framealpha=0.9)
ax.grid(True, alpha=0.3)

ax.set_xlim([0, 1])
ax.set_ylim([0, 1.1])

# Save in multiple formats
plt.tight_layout()
plt.savefig('figure1.pdf', bbox_inches='tight')      # Vector for LaTeX
plt.savefig('figure1.png', dpi=300, bbox_inches='tight')  # Raster for presentations
print("✓ Publication plot saved")
```

### 8.3 Colorblind-Safe Palettes

```python
import matplotlib.pyplot as plt
import numpy as np

# Colorblind-safe color palette (Wong, 2011)
colors = {
    'blue': '#0072B2',
    'orange': '#D55E00',
    'green': '#009E73',
    'red': '#CC79A7',
    'purple': '#949494',
    'brown': '#F0E442'
}

# Example usage
fig, ax = plt.subplots(figsize=(10, 6))

ax.plot(x1, y1, color=colors['blue'], linewidth=2, label='Case A')
ax.plot(x2, y2, color=colors['orange'], linewidth=2, label='Case B')
ax.plot(x3, y3, color=colors['green'], linewidth=2, label='Case C')

ax.legend()
ax.grid(True, alpha=0.3)
```

### 8.4 Multi-Panel Figures

```python
import matplotlib.pyplot as plt
import numpy as np

# Create figure with 2x2 subplots
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Panel (a): Velocity profile
ax = axes[0, 0]
ax.plot(y, u, 'b-', linewidth=2)
ax.set_xlabel('y [m]')
ax.set_ylabel('U [m/s]')
ax.set_title('(a) Velocity Profile')
ax.grid(True, alpha=0.3)

# Panel (b): Pressure contour
ax = axes[0, 1]
contour = ax.tricontourf(mesh_x, mesh_y, p, levels=20, cmap='jet')
plt.colorbar(contour, ax=ax, label='Pressure [Pa]')
ax.set_title('(b) Pressure Field')

# Panel (c): Residuals
ax = axes[1, 0]
ax.semilogy(time, residual, 'r-', linewidth=2)
ax.set_xlabel('Time [s]')
ax.set_ylabel('Residual')
ax.set_title('(c) Convergence')
ax.grid(True, alpha=0.3)

# Panel (d): Force coefficients
ax = axes[1, 1]
ax.plot(iterations, cd, 'b-', linewidth=2, label='$C_d$')
ax.plot(iterations, cl, 'r--', linewidth=2, label='$C_l$')
ax.set_xlabel('Iteration')
ax.set_ylabel('Coefficient')
ax.set_title('(d) Force Coefficients')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('multi_panel_figure.png', dpi=300)
```

---

## 9. Memory Management for Large Datasets

### 9.1 Problem: Large Mesh Data

```
Typical OpenFOAM case sizes:
- Small (< 1M cells):     100 MB - 1 GB
- Medium (1-10M cells):   1 GB - 10 GB
- Large (> 10M cells):    10 GB - 100 GB

⚠️  Loading entire mesh into RAM may cause memory errors!
```

### 9.2 Strategies

#### Strategy 1: Chunked Loading

```python
import numpy as np

def load_in_chunks(filename, chunk_size=100000):
    """
    Load large data file in chunks to avoid memory overflow.
    """
    chunks = []
    with open(filename, 'r') as f:
        chunk = []
        for i, line in enumerate(f):
            if i % chunk_size == 0 and chunk:
                chunks.append(np.array(chunk))
                chunk = []
            chunk.append([float(x) for x in line.split()])
        
        if chunk:
            chunks.append(np.array(chunk))
    
    return np.concatenate(chunks)

# Usage
data = load_in_chunks('large_data.txt', chunk_size=50000)
print(f"Loaded {len(data)} rows")
```

#### Strategy 2: Downsample Large Mesh

```python
from fluidfoam import readof
import numpy as np

def downsample_mesh(mesh, field, factor=10):
    """
    Downsample mesh for visualization.
    Reduces number of points by 'factor'.
    """
    # Keep every n-th point
    indices = np.arange(0, len(mesh.x), factor)
    
    mesh_downsampled = type('obj', (object,), {
        'x': mesh.x[indices],
        'y': mesh.y[indices],
        'z': mesh.z[indices]
    })
    
    field_downsampled = field[indices]
    
    return mesh_downsampled, field_downsampled

# Usage
mesh = readof.readmesh('largeCase')
T = readof.readscalar('largeCase', '500', 'T')

print(f"Original mesh: {len(mesh.x)} points")

mesh_ds, T_ds = downsample_mesh(mesh, T, factor=10)
print(f"Downsampled: {len(mesh_ds.x)} points (10% reduction)")
```

#### Strategy 3: Use PyVista's Decimation

```python
import pyvista as pv

# Load mesh
mesh = pv.OpenFOAMReader('largeCase.foam').read()

print(f"Original: {mesh.n_cells} cells")

# Decimate (reduce cell count)
decimated = mesh.decimate(target_reduction=0.9)  # Keep 10%
print(f"Decimated: {decimated.n_cells} cells")

# Save memory
decimated.save('decimated_mesh.vtk')
```

#### Strategy 4: Process Time Steps Sequentially

```python
from fluidfoam import readof
import matplotlib.pyplot as plt

def process_time_series(case_path, time_steps):
    """
    Process multiple timesteps without loading all at once.
    """
    for i, time in enumerate(time_steps):
        # Load single timestep
        T = readof.readscalar(case_path, str(time), 'T')
        
        # Process and save immediately
        fig, ax = plt.subplots()
        ax.tricontourf(mesh.x, mesh.y, T, levels=20, cmap='jet')
        ax.set_title(f'Time = {time} s')
        
        plt.savefig(f'contour_t{time}.png', dpi=150)
        plt.close()  # Free memory
        
        if (i+1) % 10 == 0:
            print(f"Processed {i+1}/{len(time_steps)} timesteps")

# Usage
time_steps = [0, 0.1, 0.2, 0.3, 0.4, 0.5]
process_time_series('myCase', time_steps)
```

### 9.3 Memory Profiling

```python
import sys
import numpy as np

def get_memory_usage(var):
    """Get memory usage of variable in MB."""
    return sys.getsizeof(var) / 1024**2

# Profile data loading
mesh = readof.readmesh('myCase')
T = readof.readscalar('myCase', '500', 'T')

print(f"Mesh: {get_memory_usage(mesh):.2f} MB")
print(f"Field T: {get_memory_usage(T):.2f} MB")
print(f"Total: {get_memory_usage(mesh) + get_memory_usage(T):.2f} MB")
```

---

## 10. Cross-Tool Integration

### 10.1 ParaView → Python Workflow

```
ParaView (quick inspection) 
    ↓
Export data to CSV/VTK
    ↓
Python (custom analysis/plotting)
    ↓
Publication-quality figures
```

**Export from ParaView:**
```
File → Export Scene → .png (quick view)
File → Save Data → .csv (line probes)
File → Save Data → .vtk (mesh slices)
```

**Import to Python:**
```python
import pandas as pd
import pyvista as pv

# Load CSV from ParaView probe
df = pd.read_csv('paraview_probe.csv')

# Load VTK slice
mesh = pv.read('paraview_slice.vtk')
```

### 10.2 Python → Blender Workflow

สำหรับ advanced animation:

1. **Python:** Export data to VTK format
   ```python
   import pyvista as pv
   mesh = pv.read('case.foam')
   mesh.save('animation_data.vtk')
   ```

2. **Blender:** Import และ render ([04_Animation_Techniques.md](04_Animation_Techniques.md))

---

## 11. Troubleshooting

### 11.1 Common Issues

| Problem | Solution |
|---------|----------|
| **ImportError: No module named 'fluidfoam'** | `pip install fluidfoam` |
| **MemoryError when loading mesh** | Use downsampling (Section 9.2) |
| **Empty plot** | Check data ranges: `print(data.min(), data.max())` |
| **Chinese characters in labels** | Add: `plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']` |
| **Slow rendering** | Reduce resolution: `plt.savefig(..., dpi=150)` |
| **fluidfoam can't find case** | Use absolute path or run from case directory |

### 11.2 Debug Checklist

```python
# Debug script
import numpy as np
import matplotlib.pyplot as plt

print("=== DEBUG INFO ===")
print(f"Working directory: {os.getcwd()}")
print(f"Files in directory: {os.listdir('.')}")

# Check if data file exists
if os.path.exists('data.txt'):
    print("✓ Data file found")
    data = np.loadtxt('data.txt')
    print(f"Data shape: {data.shape}")
    print(f"Data range: [{data.min():.3f}, {data.max():.3f}]")
else:
    print("✗ Data file NOT found")

# Test matplotlib
plt.figure()
plt.plot([1, 2, 3], [1, 4, 9])
plt.savefig('test_plot.png')
print("✓ Matplotlib working (test_plot.png created)")
```

---

## Quick Reference

### Data Loading

| Method | Use Case | Code |
|--------|----------|------|
| `np.loadtxt()` | Simple text files | `data = np.loadtxt('file.txt')` |
| `pd.read_csv()` | CSV with headers | `df = pd.read_csv('file.csv')` |
| `fluidfoam.readscalar()` | OpenFOAM scalar | `T = readof.readscalar('case', '500', 'T')` |
| `fluidfoam.readvector()` | OpenFOAM vector | `U = readof.readvector('case', '500', 'U')` |
| `fluidfoam.readmesh()` | OpenFOAM mesh | `mesh = readof.readmesh('case')` |
| `pv.OpenFOAMReader()` | 3D visualization | `mesh = pv.OpenFOAMReader('case.foam')` |

### Plot Types

| Plot Type | Library | Code |
|-----------|---------|------|
| Line plot | matplotlib | `plt.plot(x, y)` |
| Scatter | matplotlib | `plt.scatter(x, y)` |
| Contour (2D) | matplotlib | `plt.tricontourf(x, y, z)` |
| Heatmap | seaborn | `sns.heatmap(data)` |
| Isosurface (3D) | PyVista | `mesh.contour()` |
| Volume render | PyVista | `plotter.add_volume()` |

### Publication Settings

```python
# High resolution
plt.savefig('figure.png', dpi=300, bbox_inches='tight')

# Vector format (best for LaTeX)
plt.savefig('figure.pdf', bbox_inches='tight')

# Custom size
plt.figure(figsize=(10, 6))  # Width, height in inches
```

---

## 🧠 Concept Check

<details>
<summary><b>1. เมื่อไหร่ควรใช้ matplotlib vs PyVista?</b></summary>

- **matplotlib:** 2D plots, line graphs, contours, publication-quality figures
- **PyVista:** 3D visualization, isosurfaces, volume rendering

📖 See comparison table in **Section 2.1**
</details>

<details>
<summary><b>2. fluidfoam ใช้ทำอะไร?</b></summary>

**Read OpenFOAM fields directly** เข้า Python:
- `readscalar()` → pressure, temperature
- `readvector()` → velocity, forces
- `readmesh()` → mesh coordinates

📖 Examples in **Section 4**
</details>

<details>
<summary><b>3. semilogy ใช้เมื่อไหร่?</b></summary>

**Residuals and convergence** — log scale on y-axis เพื่อแสดงค่าที่ลดลงหลาย order of magnitude

📖 Example in **Section 7.2**
</details>

<details>
<summary><b>4. ทำอย่างไรเมื่อข้อมูล mesh ใหญ่เกินไป?</b></summary>

**3 strategies:**
1. Chunked loading (Section 9.2, Strategy 1)
2. Downsampling (Section 9.2, Strategy 2)
3. Process timesteps sequentially (Section 9.2, Strategy 4)

📖 Full guide in **Section 9**
</details>

<details>
<summary><b>5. seaborn ดีกว่า matplotlib ตรงไหน?</b></summary>

- **Beautiful default styles** → Less code for good plots
- **Statistical functions** → Heatmaps, distributions, regression
- **Easier multi-comparison** → Less boilerplate

📖 Examples in **Section 5**
</details>

---

## 📚 Key Takeaways

### ✅ Best Practices

1. **Choose the right tool:**
   - Line plots: matplotlib
   - Statistics: seaborn
   - 3D fields: PyVista
   - OpenFOAM I/O: fluidfoam

2. **Publication quality:**
   - Use 300+ DPI resolution
   - Always include units in labels
   - Use colorblind-safe palettes
   - Export both PNG (presentations) and PDF (LaTeX)

3. **Memory management:**
   - Downsample large meshes
   - Process timesteps sequentially
   - Use chunked loading for big files

4. **Workflow:**
   - ParaView → quick inspection ([01_ParaView_Visualization.md](01_ParaView_Visualization.md))
   - Python → custom analysis and plotting
   - Blender → advanced animation ([04_Animation_Techniques.md](04_Animation_Techniques.md))

### 🎯 Decision Framework

```
Data type?
├─ 3D volume → PyVista
├─ 2D field → matplotlib + fluidfoam
├─ Time series → matplotlib
├─ Statistics → seaborn
└─ Validation → matplotlib (comparison plots)
```

---

## 🎯 Practice Exercises

### Exercise 1: Basic Line Plot (⭐ Easy)

**Task:** Plot pressure vs time from probe data

```python
# Load data from postProcessing/probes/0/p
# Create line plot with proper labels
# Save as pressure_probe.png
```

**Solution:** See Section 3.1

---

### Exercise 2: Contour Plot (⭐⭐ Medium)

**Task:** Create temperature contour plot

```python
# Read mesh and T field using fluidfoam
# Create tricontourf plot
# Add colorbar with units
# Save as temperature_contour.png
```

**Solution:** See Section 4.3

---

### Exercise 3: Validation Plot (⭐⭐ Medium)

**Task:** Compare CFD vs experimental data

```python
# Load CFD data from sampleDict output
# Load experimental data from CSV
# Create comparison plot with error bars
# Use seaborn for styling
```

**Solution:** See Section 5.1

---

### Exercise 4: 3D Isosurface (⭐⭐⭐ Hard)

**Task:** Visualize 3D isosurface with PyVista

```python
# Load OpenFOAM case
# Extract isosurface at T = 300K
# Add volume rendering
# Save interactive screenshot
```

**Solution:** See Section 6.3

---

### Exercise 5: Multi-Panel Figure (⭐⭐⭐ Hard)

**Task:** Create 2x2 publication-quality figure

```python
# Panel (a): Velocity profile
# Panel (b): Pressure contour
# Panel (c): Residual history
# Panel (d): Force coefficients
# Apply publication style (Section 8.2)
```

**Solution:** See Section 8.4

---

## 📖 Related Documentation

### Within This Module

- **Overview:** [00_Overview.md](00_Overview.md) — Module introduction
- **ParaView:** [01_ParaView_Visualization.md](01_ParaView_Visualization.md) — 3D interactive visualization
- **Animation:** [04_Animation_Techniques.md](04_Animation_Techniques.md) — Advanced Blender rendering

### Cross-Module References

- **OpenFOAM Basics:** Module 02 — Simulation setup
- **Post-Processing:** Module 05 — Data extraction methods
- **Advanced Visualization:** Module 06 — Coupled physics visualization

### External Resources

- **Matplotlib:** https://matplotlib.org/stable/gallery/
- **PyVista:** https://docs.pyvista.org/
- **fluidfoam:** https://fluidfoam.readthedocs.io/
- **Seaborn:** https://seaborn.pydata.org/examples/

---

## 📋 Appendix: Keyboard Shortcuts

### Python REPL

| Shortcut | Action |
|----------|--------|
| `↑` / `↓` | Navigate command history |
| `Tab` | Auto-complete |
| `Ctrl+C` | Interrupt execution |
| `Ctrl+D` | Exit |

### Jupyter Notebook

| Shortcut | Action |
|----------|--------|
| `Shift+Enter` | Run cell and advance |
| `Ctrl+Enter` | Run cell in-place |
| `Tab` | Indent / auto-complete |
| `Shift+Tab` | Show function docstring |
| `DD` | Delete cell |
| `A` / `B` | Insert cell above/below |

### Matplotlib Interactive Mode

| Shortcut | Action |
|----------|--------|
| `Home` / `End` | Reset / forward view |
| `Left` / `Right` | Back / forward |
| `Pan` | Drag to pan |
| `Zoom` | Right-click drag to zoom |
| `s` | Save figure |
| `f` | Toggle fullscreen |
| `g` | Toggle grid |

---

**Last Updated:** 2025-12-31

**Contributors:** OpenFOAM Documentation Team

**Version:** 1.0 — Refactored for Pedagogical Coherence