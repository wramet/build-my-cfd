# ParaView Visualization for CFD

---

## Learning Objectives

By the end of this tutorial, you will be able to:

- **Set up ParaView** to visualize OpenFOAM simulation results using the `case.foam` marker file
- **Apply common visualization filters** (Slice, Contour, Glyph, Streamline) to extract flow features
- **Navigate the ParaView interface** efficiently using keyboard shortcuts and the pipeline browser
- **Optimize performance** when handling large CFD datasets with millions of cells
- **Export publication-quality images** and animations for technical reports and presentations
- **Choose appropriate visualization techniques** based on your analysis objectives (qualitative inspection vs quantitative comparison)

---

## Prerequisites

| Requirement | Details |
|-------------|---------|
| **Software** | ParaView 5.9+ (recommended: 5.11+) |
| **Data** | Completed OpenFOAM simulation with time directories |
| **Hardware** | 8GB+ RAM for moderate cases; 16GB+ recommended for large datasets |
| **Knowledge** | Basic familiarity with OpenFOAM case structure |

---

## 3W Framework: ParaView in Context

### WHAT (ParaView = CFD Post-Processing Standard)

**ParaView** is an open-source, multi-platform data analysis and visualization application designed for rendering large scientific datasets. For OpenFOAM users, it serves as the **primary graphical interface** for:

- **Qualitative flow inspection**: Identifying recirculation zones, separation points, wake structures
- **Quantitative analysis**: Extracting profiles, surface integrals, point probes
- **Communication**: Creating publication-quality figures and presentation animations
- **Validation**: Comparing simulation results against experimental data or other solvers

### WHY (When to Use ParaView vs Other Tools)

| Scenario | Recommended Tool | Rationale |
|----------|------------------|-----------|
| **Quick field inspection** during simulation | ParaView | Real-time rendering, interactive exploration |
| **Publication-ready line plots** (XY data) | Python/Matplotlib (see §02) | Better control over typography, multiple datasets |
| **Photorealistic rendering** for marketing | Blender (see §03) | Advanced lighting, materials, compositing |
| **Automated batch processing** of 100+ cases | Python PyVista/Paraview.py | Scriptable, reproducible workflows |
| **Interactive presentations** to stakeholders | ParaView | Smooth camera animations, real-time filtering |
| **Time-series analysis** at specific probe locations | Python | Direct data manipulation, statistical analysis |

**Key Advantages of ParaView for CFD:**

- **Native OpenFOAM reader**: Built-in `case.foam` support handles polyhedral meshes, decomposed cases
- **Scalable architecture**: Client-server mode for remote HPC visualization
- **Rich filter ecosystem**: 100+ filters for derived quantities (vorticity, Q-criterion, wall y+)
- **Interactive**: Real-time camera manipulation, instant filter parameter updates
- **Batch-capable**: Python scripting for reproducible figures

### HOW (Implementation Strategy)

This section provides a **progressive learning path**:

1. **Setup** (§1): Launch ParaView with OpenFOAM data
2. **Interface Navigation** (§2): Understanding the workspace components
3. **Basic Visualization** (§3): Essential filters for everyday CFD analysis
4. **Advanced Techniques** (§4): Performance optimization and professional workflows
5. **Export & Animation** (§5): Deliverables for reports and presentations

> **Cross-Reference:** For automated plotting of XY data (e.g., convergence history, probe time series), see [02_Python_Plotting.md](02_Python_Plotting.md). For photorealistic rendering, see [03_Blender_Rendering.md](03_Blender_Rendering.md).

---

## 1. Launching ParaView with OpenFOAM Data

### 1.1 The `case.foam` Marker File

ParaView requires a **marker file** to recognize OpenFOAM case directories:

```bash
# Navigate to your OpenFOAM case directory
cd /path/to/your/case

# Create the marker file (empty file)
touch case.foam

# Launch ParaView
paraview case.foam
```

**Why `case.foam`?**

- Acts as a **pointer** to the case directory structure
- Signals ParaView to use the **built-in OpenFOAM reader**
- Allows browsing **all time directories** (0/, 0.1/, 0.2/, ...)
- Works for **both serial and reconstructed decomposed cases**

### 1.2 Initial Loading

1. **Open File**: `File > Open` → Select `case.foam`
2. **Apply**: Click the **green Apply button** in Properties panel
3. **Mesh Display**: The computational mesh appears (wireframe or surface)

> **Common Pitfall:** If no geometry appears after clicking Apply, check that:
> - Time directories contain `polyMesh/` folder with `points`, `faces`, `owner`
> - Case is **reconstructed** (use `reconstructPar` if running in parallel)
> - Memory is sufficient (check System Monitor for RAM usage)

---

## 2. Interface Overview

<!-- IMAGE: IMG_07_004 -->
<!-- 
Purpose: Interface annotation for beginners
Prompt: "Mockup of ParaView User Interface. **Central Viewport:** A stunning 3D visualization of aerodynamic flow around a car (Streamlines + Pressure Surface). **Sidebar (Left):** 'Pipeline Browser' showing loaded modules. **Panel (Bottom-Left):** 'Properties' with 'Apply' button highlighted green. **Toolbar (Top):** Icons for 'Slice', 'Clip', 'Glyph'. **Annotations:** Callout bubbles pointing to key areas: 1. Pipeline Browser 2. Properties Panel 3. 3D Viewport 4. Toolbar. STYLE: Clean UI mockup, high-resolution aesthetic, dark theme."
-->
![[IMG_07_004.jpg]]

### Key Interface Components

| Region | Function | Pro Tips |
|--------|----------|----------|
| **Pipeline Browser** (left) | Shows all filters and data objects | **Collapse** long pipelines; rename objects (right-click > Rename) |
| **Properties Panel** (bottom-left) | Configure filter parameters | **Ctrl+Space** to search parameters; changes require **Apply** |
| **3D Viewport** (center) | Interactive rendering | **Left-click drag**: Rotate; **Shift+left-click**: Pan; **Scroll**: Zoom |
| **Color Legend** (right) | Color scale bar | **Edit** > Rescale to Custom Range for consistent comparisons |
| **Toolbar** (top) | Quick access to common filters | **Customize** via Settings > Toolbars |

---

## 3. Essential Visualization Filters

### 3.1 Slice (Planar Cutting)

**Use Case:** Inspecting internal flow structures (boundary layers, wakes)

```
Filters > Common > Slice
```

**Configuration:**
- **Slice Type**: Plane (default)
- **Origin**: Center point of cutting plane
- **Normal**: Vector normal to plane (e.g., (1,0,0) for YZ-plane)

**Keyboard Shortcut:** None by default; add via Settings > Configure Shortcuts

**Example:**
```python
# Slice at mid-span of airfoil
Origin: (0, 0, 0.5)  # Adjust based on domain
Normal: (0, 0, 1)    # Z-normal slice
```

### 3.2 Contour (Iso-Surfaces)

**Use Case:** Visualizing surfaces of constant field value (pressure iso-surfaces, vorticity cores)

```
Filters > Common > Contour
```

**Configuration:**
- **Contour By**: Select field (e.g., `p`, `U`, `vorticity`)
- **Isosurfaces**: Add specific values or use range

**Example Application:**
```python
# Visualize pressure wake structure
Contour By: p (pressure)
Isosurfaces: 101325 Pa (ambient pressure)

# Visualize vortex cores (Q-criterion)
# First compute Q-criterion: Filters > Algebraic > Calculator
# Expression: -0.5*(Trace(Gradient^2))  # Simplified
```

### 3.3 Glyph (Vector Field)

**Use Case:** Showing velocity/direction at specific locations (avoid visual clutter)

```
Filters > Common > Glyph
```

**Configuration:**
- **Scale Mode**: Vector (magnitude-based) or Off (uniform size)
- **Glyph Mode**: Arrow/Arrow/Cone
- **Scaling**: Adjust scale factor (start with 0.001 for typical CFD)

**Performance Tip:** Use **Masking** to reduce glyph count:
```
Glyph > Masking > Enable Masking
Mask Points: Stride (iTh) = 10  # Show 1 in 10 vectors
```

### 3.4 Streamtracer (Flow Pathlines)

**Use Case:** Tracing fluid particle trajectories for flow visualization

```
Filters > Common > Stream Tracer
```

**Configuration:**
- **Seed Type**: Point Source / Line Source / High Resolution Line Source
- **Vector Field**: `U` (velocity)
- **Maximum Steps**: 1000 (default) for complex paths
- **Step Length**: Auto (default)

**Best Practices:**
- **Seed placement**: Position in upstream region
- **Number of seeds**: Start with 50-100; increase for finer detail
- **Integration Direction**: BOTH (forward + backward)

> **Common Pitfall:** Streamlines appear "broken" or too short
> - **Solution:** Increase **Maximum Steps** and **Step Length**
> - **Check:** Vector field `U` is selected (not `mag(U)`)

### Filter Selection Guide

| Analysis Goal | Recommended Filter | Color By |
|---------------|-------------------|----------|
| Boundary layer profile | Slice | `U` (velocity magnitude) |
| Separation/reattachment lines | Surface LIC | Wall shear stress |
| Vortex cores | Contour | Q-criterion / vorticity magnitude |
| Wake structure | Streamtracer + Slice | `p` (pressure) |
| Heat transfer | Contour (Iso-surfaces) | Temperature |

---

## 4. Advanced Workflows & Performance Optimization

### 4.1 Handling Large Datasets (Millions of Cells)

**Problem:** ParaView becomes slow/laggy with large meshes

**Solutions:**

| Strategy | Implementation | Speedup |
|----------|----------------|---------|
| **Reduce Mesh Resolution** | Filters > Mesh Reduction > Decimate | 5-10x |
| **Temporal Reduction** | Load only every Nth timestep | 2-5x |
| **Server-Side Rendering** | Use `pvserver` on HPC, client locally | Offloads compute |
| **Data Level of Detail** | Represent large cells as points | 3-5x |
| **Disable Auto-Update** | Settings > General > Auto Apply = Off | Prevents lags |

**Example: Decimating Large Mesh**
```
Filters > Mesh Reduction > Decimate
Reduction Factor: 0.9  # Keep 10% of triangles
```

### 4.2 Creating Derived Fields

**Calculator Filter:** Compute custom quantities

```
Filters > Algebraic > Calculator
```

**Common Expressions:**

| Quantity | Formula (Calculator) | Notes |
|----------|---------------------|-------|
| **Velocity Magnitude** | `mag(U)` | Built-in alternative |
| **Vorticity Magnitude** | `mag(vorticity)` | Requires vorticity computation first |
| **Wall Shear Stress** | `wallShearStress` | Pre-computed in OpenFOAM |
| **Q-Criterion** | `-0.5*(Trace(Gradient^2))` | Vortex identification |
| **Pressure Coefficient** | `(p - pInf) / (0.5 * rho * UInf^2)` | Normalize pressure |

### 4.3 Batch Processing with Python Shell

**ParaView Python Shell:** `View > Python Shell`

**Example: Export Multiple Timesteps**
```python
from paraview.simple import *

# Load case
case = OpenFOAMReader(FileName='case.foam')
case.MeshRegions = ['internalMesh', 'patch_inlet', 'patch_outlet']

# Create screenshot function
def export_timestep(timestep):
    case.TimestepValues = timestep
    Render()
    WriteImage(f'screenshot_{timestep}.png', resolution=(1920, 1080))

# Loop over timesteps
for t in case.TimestepValues:
    export_timestep(t)
```

> **Cross-Reference:** For advanced Python automation, see [02_Python_Plotting.md](02_Python_Plotting.md) §5

---

## 5. Exporting Images & Animations

### 5.1 Saving Screenshots (Static Images)

```
File > Save Screenshot
```

**Recommended Settings:**

| Parameter | Recommendation | Rationale |
|-----------|----------------|-----------|
| **Resolution** | 1920×1080 (Full HD) or 3840×2160 (4K) | Publication-ready |
| **Format** | PNG (lossless) or PDF (vector) | PNG for raster; PDF for line art |
| **Color Scale** | Include "Save Color Legend" option | For reproducibility |
| **View Size** | Use "Lock View Size" before capture | Consistent aspect ratio |

**Pro Tip:** Save **Color Legend** separately for multi-figure layouts:
```
View > Color Legend > Show
# Adjust position, then File > Save Screenshot
```

### 5.2 Creating Animations

**Method 1: Built-in Animation (Quick)**

```
File > Save Animation
```

**Configuration:**
- **Frame Window**: All timesteps or custom range
- **Frame Rate**: 15-30 FPS (higher = smoother but larger files)
- **Resolution**: Same as screenshot settings
- **Format**: AVI / OGG (video) or PNG sequence

**Method 2: Python Script (Custom Camera Paths)**

```python
from paraview.simple import *

# Set up camera animation
scene = GetActiveView()
scene.CameraPosition = [10, 0, 0]
scene.CameraFocalPoint = [0, 0, 0]

# Rotate camera 360 degrees
for i in range(0, 360, 5):
    scene.CameraPosition = [10*cos(radians(i)), 10*sin(radians(i)), 0]
    Render()
    WriteImage(f'frame_{i:03d}.png')
```

> **Cross-Reference:** For professional video editing (transitions, annotations), see [04_Animation_Techniques.md](04_Animation_Techniques.md) §3

---

## Keyboard Shortcuts Quick Reference

| Action | Shortcut | Notes |
|--------|----------|-------|
| **Rotate Camera** | Left-click drag | Orbit around focal point |
| **Pan Camera** | Shift + Left-click drag | Move in plane |
| **Zoom** | Mouse wheel / Right-click drag | In/out |
| **Reset Camera** | `r` | Return to default view |
| **Apply Filter** | `Ctrl + Space` | Focus Properties panel |
| **Undo** | `Ctrl + Z` | Revert last action |
| **Redo** | `Ctrl + Shift + Z` | Restore undone action |
| **Toggle Pipeline** | `Ctrl + 1` | Show/hide browser |
| **Toggle Properties** | `Ctrl + 2` | Show/hide panel |
| **Color by** | `Ctrl + 3` | Quick color selector |
| **Save Screenshot** | `Ctrl + Shift + S` | Export current view |
| **Search Filters** | `Ctrl + Shift + F` | Find filter by name |

**Customize Shortcuts:**
```
Settings > Configure Shortcuts > Filter by: "Apply"
```

---

## Common Pitfalls & Troubleshooting

| Issue | Symptom | Solution |
|-------|---------|----------|
| **No geometry after loading** | Empty viewport | Check: (1) Case reconstructed? (2) `polyMesh/` exists (3) Click Apply |
| **Decomposed case unreadable** | Error loading time dirs | Run `reconstructPar` before opening in ParaView |
| **Streamlines disappear** | Only seed points visible | Increase "Maximum Steps" (default 1000 → 5000) |
| **Glyphs too dense** | Viewport black with arrows | Use "Masking" > Stride = 10 or more |
| **Memory exhausted** | ParaView crashes | Load only every 2-3 timesteps; use Decimate filter |
| **Color scale wrong** | Field values off by factor | Check "Rescale to Custom Range" in Color Map Editor |
| **Animation too fast/slow** | Playback speed issues | Adjust "Cache Size" in Settings > Animation |
| **Wrong boundary patches** | Patches missing | Ensure `boundary` file in `constant/polyMesh/` |

> **FAQ Appendix:** See [Appendix_Troubleshooting.md](../Appendix_Troubleshooting.md) for extended error resolution guide

---

## Key Takeaways

1. **`case.foam` is essential**: Create empty marker file to enable ParaView's OpenFOAM reader
2. **Apply every change**: Click green **Apply** button after modifying filter parameters
3. **Choose the right filter**: Slice for profiles, Contour for iso-surfaces, Glyph for vectors, Streamtracer for pathlines
4. **Optimize for large cases**: Use Decimate, timestep reduction, or server-side rendering
5. **Batch with Python**: Automate repetitive tasks (multiple timesteps, parameter sweeps)
6. **Export wisely**: PNG for raster figures, PDF for vector graphics, PNG sequence for animations
7. **Keyboard shortcuts save time**: Learn `r` (reset), `Ctrl+Space` (search), `Ctrl+Shift+S` (screenshot)

---

## Practice Exercises

### Exercise 1: Basic Slice Visualization

**Scenario:** Analyze velocity profile in a channel flow

1. Load `tutorials/heatTransfer/chtMultiRegionFoam/heatExchanger/` case
2. Create `case.foam` marker file
3. Apply **Slice** filter at mid-channel (z-normal plane)
4. Color by velocity magnitude `U`
5. Save screenshot at 1920×1080 resolution

**Learning Goal:** Familiarize with slice workflow

### Exercise 2: Streamline Visualization

**Scenario:** Identify recirculation zones in backward-facing step flow

1. Load `tutorials/incompressible/simpleFoam/airFoil2D/` case
2. Run simulation (`simpleFoam`)
3. Create **Stream Tracer** with:
   - Seed: Line source upstream of step
   - 100 streamlines
   - Integration: BOTH
4. Adjust color by velocity magnitude
5. Identify separation and reattachment points

**Learning Goal:** Understand streamline seeding and flow topology

### Exercise 3: Comparative Analysis

**Scenario:** Compare pressure distribution between two turbulence models

1. Run two cases: `kOmegaSST` and `kEpsilon`
2. Load both in ParaView simultaneously (two separate readers)
3. Create **Contour** filter for `p = 101325 Pa` (ambient pressure)
4. Export screenshots with **identical** camera position and color scale
5. Create Python script to automate (see §4.3)

**Learning Goal:** Reproducible comparative visualization

---

## Related Documentation

| Topic | File | Section |
|-------|------|---------|
| **Python Plotting** (XY data, automation) | [02_Python_Plotting.md](02_Python_Plotting.md) | §5 (ParaView Python scripting) |
| **Blender Rendering** (photorealistic output) | [03_Blender_Rendering.md](03_Blender_Rendering.md) | §2 (Importing from ParaView) |
| **Animation Production** (video editing) | [04_Animation_Techniques.md](04_Animation_Techniques.md) | §3 (Camera path scripting) |
| **Troubleshooting FAQ** | [../Appendix_Troubleshooting.md](../Appendix_Troubleshooting.md) | Visualization section |

---

## 🧠 Concept Check

<details>
<summary><b>1. case.foam ใช้ทำไม?</b></summary>

**Marker file** ที่บอก ParaView ว่า directory นี้เป็น OpenFOAM case ที่สามารถอ่านได้โดย built-in OpenFOAM reader ช่วยให้สามารถเรียกดูข้อมูลจากทุก time directory (0/, 0.1/, 0.2/, ...) ได้อย่างอัตโนมัติ
</details>

<details>
<summary><b>2. เมื่อไหร่ควรใช้ Slice vs Contour?</b></summary>

- **Slice:** ตัดข้อมูลด้วยระนาบ (plane) แสดงค่า field บนพื้นผิวนั้น เหมาะสำหรับดู profile ภายในโดเมน (boundary layer, wake)  
- **Contour:** แสดงพื้นผิวที่มีค่า field คงที่ (iso-surface) เหมาะสำหรับดูโครงสร้างการไหลแบบ 3D (vortex cores, pressure waves)
</details>

<details>
<summary><b>3. ParaView ช้ามากกับข้อมูลขนาดใหญ่ ทำอย่างไร?</b></summary>

ใช้ **Decimate filter** ลด resolution, โหลดเฉพาะทุก 2-3 timesteps, หรือใช้ `pvserver` บน HPC แล้ว remote render จากเครื่อง local ดู §4.1 สำหรับเทคนิคเพิ่มเติม
</details>

---

## Glossary

| Term | Definition |
|------|------------|
| **case.foam** | Empty marker file that signals ParaView to use the OpenFOAM reader |
| **Pipeline** | Sequence of filters applied to data (visualized in Pipeline Browser) |
| **Iso-surface** | 3D surface where a scalar field has constant value (created with Contour filter) |
| **Decimation** | Mesh reduction technique to decrease polygon count for performance |
| **Glyph** | Geometric representation (arrow/cone) placed at points to show vector direction |
| **Streamtracer** | Numerical integration of particle paths through a vector field |